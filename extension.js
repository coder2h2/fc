const vscode = require('vscode');
const path = require('path');

// Supported language extensions
const SUPPORTED_EXTENSIONS = [
    'json', 'csv', 'sql', 'html', 'css', 'txt', 'yaml', 'yml', 
    'rs', 'go', 'c', 'cpp', 'cc', 'cs', 'java', 'js', 'ts', 
    'sh', 'bash', 'py', 'rb', 'php', 'swift', 'kt', 'hs'
];

let activeWebviewView = null;
let activeWebviewPanel = null;
let currentLinksData = null;

async function fileExists(uri) {
    try {
        await vscode.workspace.fs.stat(uri);
        return true;
    } catch {
        return false;
    }
}

async function resolvePath(documentUri, pathStr) {
    try {
        const docDir = path.dirname(documentUri.fsPath);
        const relPath = path.resolve(docDir, pathStr);
        const relUri = vscode.Uri.file(relPath);
        if (await fileExists(relUri)) {
            return relUri;
        }

        if (vscode.workspace.workspaceFolders) {
            for (const folder of vscode.workspace.workspaceFolders) {
                const absPath = path.resolve(folder.uri.fsPath, pathStr);
                const absUri = vscode.Uri.file(absPath);
                if (await fileExists(absUri)) {
                    return absUri;
                }
            }
        }

        const fileBase = path.basename(pathStr);
        if (fileBase.length > 3) {
            const results = await vscode.workspace.findFiles(`**/${fileBase}`);
            if (results.length > 0) {
                return results[0];
            }
        }
    } catch (e) {
        console.error('Error resolving path:', e);
    }
    return null;
}

async function scanForLinks(document) {
    if (!document || document.languageId !== 'python') {
        return null;
    }

    const activeUri = document.uri;
    const activeFileName = path.basename(activeUri.fsPath);
    const activeBaseName = path.basename(activeUri.fsPath, '.py');
    const linksMap = new Map();

    function addLink(name, uri, relation, type) {
        const uriStr = uri.toString();
        if (uriStr === activeUri.toString()) return;

        if (!linksMap.has(uriStr)) {
            linksMap.set(uriStr, {
                name,
                path: uri.fsPath,
                uri: uriStr,
                relation,
                type: type || path.extname(uri.fsPath).replace('.', '').toLowerCase()
            });
        } else if (relation === 'reference' && linksMap.get(uriStr).relation === 'same-name') {
            linksMap.get(uriStr).relation = 'referenced-same-name';
        }
    }

    // 1. Same-name files for all supported types
    try {
        for (const ext of SUPPORTED_EXTENSIONS) {
            if (ext === 'py') continue;
            const sameNameFiles = await vscode.workspace.findFiles(`**/${activeBaseName}.${ext}`);
            for (const fileUri of sameNameFiles) {
                addLink(path.basename(fileUri.fsPath), fileUri, 'same-name');
            }
        }
    } catch (err) {
        console.error('Error scanning for same-name files:', err);
    }

    // 2. Scan string literals for references to all supported extensions
    const text = document.getText();
    const stringRegex = /(['"`])(.*?)\1/g;
    let match;

    const extPattern = new RegExp(`\\.(${SUPPORTED_EXTENSIONS.join('|')})$`, 'i');

    while ((match = stringRegex.exec(text)) !== null) {
        const value = match[2].trim();
        if (value && extPattern.test(value) && !/^[0-9\.]+$/.test(value)) {
            const resolvedUri = await resolvePath(activeUri, value);
            if (resolvedUri) {
                addLink(path.basename(resolvedUri.fsPath), resolvedUri, 'reference');
            }
        }
    }

    // 3. Scan import modules
    const importRegex = /^\s*(?:import\s+([a-zA-Z0-9_\.,\s]+)|from\s+([a-zA-Z0-9_]+(?:\.[a-zA-Z0-9_]+)*)\s+import)/gm;
    while ((match = importRegex.exec(text)) !== null) {
        let moduleName = '';
        if (match[1]) {
            moduleName = match[1].split(',')[0].trim();
        } else if (match[2]) {
            moduleName = match[2].trim();
        }

        if (moduleName) {
            const parts = moduleName.split('.');
            const modulePathStr = parts.join('/');
            
            // Check for both .py files and other language modules (like .rs, .go, .c, etc.)
            for (const ext of ['py', 'rs', 'go', 'c', 'cpp', 'cc', 'cs', 'java', 'js', 'ts']) {
                const langUri = await resolvePath(activeUri, `${modulePathStr}.${ext}`);
                if (langUri) {
                    addLink(path.basename(langUri.fsPath), langUri, 'import', ext);
                    break;
                }
            }
        }
    }

    return {
        activeFile: {
            name: activeFileName,
            path: activeUri.fsPath,
            uri: activeUri.toString()
        },
        links: Array.from(linksMap.values())
    };
}

function updateWebviews(data) {
    currentLinksData = data;
    if (activeWebviewView) {
        activeWebviewView.webview.postMessage({ type: 'update', data });
    }
    if (activeWebviewPanel) {
        activeWebviewPanel.webview.postMessage({ type: 'update', data });
    }
}

async function handleActiveEditorChange(editor) {
    if (editor && editor.document.languageId === 'python') {
        const data = await scanForLinks(editor.document);
        updateWebviews(data);
    } else {
        updateWebviews(null);
    }
}

class FileConnectSidebarProvider {
    constructor(extensionUri) {
        this._extensionUri = extensionUri;
    }

    resolveWebviewView(webviewView, context, token) {
        activeWebviewView = webviewView;

        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this._extensionUri]
        };

        webviewView.webview.html = getWebviewContent(webviewView.webview, this._extensionUri);

        webviewView.webview.onDidReceiveMessage(async (message) => {
            switch (message.type) {
                case 'ready':
                    if (currentLinksData) {
                        webviewView.webview.postMessage({ type: 'update', data: currentLinksData });
                    } else if (vscode.window.activeTextEditor) {
                        handleActiveEditorChange(vscode.window.activeTextEditor);
                    }
                    break;
                case 'openFile':
                    const uri = vscode.Uri.parse(message.uri);
                    const doc = await vscode.workspace.openTextDocument(uri);
                    await vscode.window.showTextDocument(doc);
                    break;
            }
        });

        webviewView.onDidDispose(() => {
            activeWebviewView = null;
        });
    }
}

function getWebviewContent(webview, extensionUri) {
    const visualizerJsUri = webview.asWebviewUri(vscode.Uri.joinPath(extensionUri, 'media', 'visualizer.js'));
    const visualizerCssUri = webview.asWebviewUri(vscode.Uri.joinPath(extensionUri, 'media', 'visualizer.css'));

    return `
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>FileConnect Visualizer</title>
            <link rel="stylesheet" href="${visualizerCssUri}">
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <span class="title">FileConnect Graph</span>
                    <span id="active-file-badge" class="badge">No active file</span>
                </div>
                <div class="canvas-container">
                    <canvas id="graph-canvas"></canvas>
                    <div class="controls">
                        <button id="zoom-in" title="Zoom In">+</button>
                        <button id="zoom-out" title="Zoom Out">-</button>
                        <button id="reset-view" title="Reset View">⟲</button>
                    </div>
                </div>
                <div class="details-panel" id="details-panel">
                    <div class="details-placeholder">Click a node to view file details</div>
                </div>
                <div class="legend">
                    <div class="legend-item"><span class="color-dot py"></span> Python</div>
                    <div class="legend-item"><span class="color-dot html"></span> HTML</div>
                    <div class="legend-item"><span class="color-dot css"></span> CSS</div>
                    <div class="legend-item"><span class="color-dot sql"></span> SQL</div>
                    <div class="legend-item"><span class="color-dot config"></span> Config</div>
                    <div class="legend-item"><span class="color-dot other"></span> Native/Other</div>
                </div>
            </div>
            <script src="${visualizerJsUri}"></script>
        </body>
        </html>
    `;
}

class FileConnectLinkProvider {
    async provideDocumentLinks(document, token) {
        if (document.languageId !== 'python') return [];
        const links = [];
        const text = document.getText();
        const stringRegex = /(['"`])(.*?)\1/g;
        let match;
        const extPattern = new RegExp(`\\.(${SUPPORTED_EXTENSIONS.join('|')})$`, 'i');
        
        while ((match = stringRegex.exec(text)) !== null) {
            const value = match[2].trim();
            if (value && extPattern.test(value) && !/^[0-9\.]+$/.test(value)) {
                const resolvedUri = await resolvePath(document.uri, value);
                if (resolvedUri) {
                    const startPos = document.positionAt(match.index + 1);
                    const endPos = document.positionAt(match.index + 1 + value.length);
                    const range = new vscode.Range(startPos, endPos);
                    const docLink = new vscode.DocumentLink(range, resolvedUri);
                    docLink.tooltip = `FileConnect: Open ${value}`;
                    links.push(docLink);
                }
            }
        }
        return links;
    }
}

class FileConnectCodeLensProvider {
    async provideCodeLenses(document, token) {
        if (!vscode.workspace.getConfiguration('fileconnect').get('showCodeLens', true)) {
            return [];
        }
        const lenses = [];
        const text = document.getText();
        const stringRegex = /(['"`])(.*?)\1/g;
        let match;
        const seenLines = new Set();
        const extPattern = new RegExp(`\\.(${SUPPORTED_EXTENSIONS.join('|')})$`, 'i');
        
        while ((match = stringRegex.exec(text)) !== null) {
            const value = match[2].trim();
            if (value && extPattern.test(value) && !/^[0-9\.]+$/.test(value)) {
                const resolvedUri = await resolvePath(document.uri, value);
                if (resolvedUri) {
                    const startPos = document.positionAt(match.index);
                    const line = startPos.line;
                    if (!seenLines.has(line)) {
                        seenLines.add(line);
                        const range = new vscode.Range(line, 0, line, 0);
                        const fileName = path.basename(resolvedUri.fsPath);
                        lenses.push(new vscode.CodeLens(range, {
                            title: `🔗 Open ${fileName}`,
                            command: 'fileconnect.openFile',
                            arguments: [resolvedUri]
                        }));
                    }
                }
            }
        }
        return lenses;
    }
}

function activate(context) {
    console.log('FileConnect (fc) extension is now active!');

    const sidebarProvider = new FileConnectSidebarProvider(context.extensionUri);
    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider('fileconnect.visualizerView', sidebarProvider)
    );

    context.subscriptions.push(
        vscode.languages.registerDocumentLinkProvider(
            { language: 'python', scheme: 'file' },
            new FileConnectLinkProvider()
        )
    );

    context.subscriptions.push(
        vscode.languages.registerCodeLensProvider(
            { language: 'python', scheme: 'file' },
            new FileConnectCodeLensProvider()
        )
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('fileconnect.openFile', async (uri) => {
            const doc = await vscode.workspace.openTextDocument(uri);
            await vscode.window.showTextDocument(doc);
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('fileconnect.showVisualizer', async () => {
            if (activeWebviewPanel) {
                activeWebviewPanel.reveal(vscode.ViewColumn.Two);
                return;
            }

            activeWebviewPanel = vscode.window.createWebviewPanel(
                'fileconnectVisualizerPanel',
                'FileConnect Graph',
                vscode.ViewColumn.Two,
                {
                    enableScripts: true,
                    localResourceRoots: [context.extensionUri],
                    retainContextWhenHidden: true
                }
            );

            activeWebviewPanel.webview.html = getWebviewContent(activeWebviewPanel.webview, context.extensionUri);

            activeWebviewPanel.webview.onDidReceiveMessage(async (message) => {
                switch (message.type) {
                    case 'ready':
                        if (currentLinksData) {
                            activeWebviewPanel.webview.postMessage({ type: 'update', data: currentLinksData });
                        } else if (vscode.window.activeTextEditor) {
                            handleActiveEditorChange(vscode.window.activeTextEditor);
                        }
                        break;
                    case 'openFile':
                        const uri = vscode.Uri.parse(message.uri);
                        const doc = await vscode.workspace.openTextDocument(uri);
                        await vscode.window.showTextDocument(doc);
                        break;
                }
            });

            activeWebviewPanel.onDidDispose(() => {
                activeWebviewPanel = null;
            });
        })
    );

    context.subscriptions.push(
        vscode.window.onDidChangeActiveTextEditor(handleActiveEditorChange)
    );

    context.subscriptions.push(
        vscode.workspace.onDidSaveTextDocument(async (document) => {
            if (vscode.window.activeTextEditor && document === vscode.window.activeTextEditor.document) {
                handleActiveEditorChange(vscode.window.activeTextEditor);
            }
        })
    );

    if (vscode.window.activeTextEditor) {
        handleActiveEditorChange(vscode.window.activeTextEditor);
    }
}

function deactivate() {
    activeWebviewView = null;
    activeWebviewPanel = null;
}

module.exports = {
    activate,
    deactivate
};
