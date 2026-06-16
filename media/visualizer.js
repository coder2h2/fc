const vscode = acquireVsCodeApi();

const canvas = document.getElementById('graph-canvas');
const ctx = canvas.getContext('2d');
const activeFileBadge = document.getElementById('active-file-badge');
const detailsPanel = document.getElementById('details-panel');

let nodes = [];
let links = [];
let selectedNode = null;
let hoveredNode = null;

const kRepulsion = 4000;
const kAttraction = 0.04;
const restLength = 120;
const gravity = 0.015;
const damping = 0.82;

let scale = 1.0;
let panX = 0;
let panY = 0;
let isPanning = false;
let startPanX = 0;
let startPanY = 0;
let isDraggingNode = false;
let draggedNode = null;
let mouseX = 0;
let mouseY = 0;

vscode.postMessage({ type: 'ready' });

function resizeCanvas() {
    const rect = canvas.parentElement.getBoundingClientRect();
    canvas.width = rect.width * window.devicePixelRatio;
    canvas.height = rect.height * window.devicePixelRatio;
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    if (panX === 0 && panY === 0 && nodes.length > 0) {
        resetView();
    }
}
window.addEventListener('resize', resizeCanvas);
setTimeout(resizeCanvas, 100);

function resetView() {
    scale = 1.0;
    const rect = canvas.getBoundingClientRect();
    panX = rect.width / 2;
    panY = rect.height / 2;
    
    const centerNode = nodes.find(n => n.isCenter);
    if (centerNode) {
        centerNode.x = 0;
        centerNode.y = 0;
        centerNode.vx = 0;
        centerNode.vy = 0;
        
        const nonCenter = nodes.filter(n => !n.isCenter);
        nonCenter.forEach((node, i) => {
            const angle = (i / nonCenter.length) * Math.PI * 2;
            node.x = Math.cos(angle) * restLength;
            node.y = Math.sin(angle) * restLength;
            node.vx = 0;
            node.vy = 0;
        });
    }
}

function getFileTypeColor(type) {
    const colors = {
        py: '#387eb8',
        html: '#e34c26',
        css: '#264de4',
        sql: '#c084fc',
        json: '#eab308',
        yaml: '#10b981',
        yml: '#10b981',
        csv: '#22c55e',
        txt: '#64748b',
        // Native languages
        c: '#555555',
        cpp: '#00599c',
        cc: '#00599c',
        rs: '#dea584',
        go: '#00add8',
        cs: '#178600',
        java: '#b07219',
        js: '#f1e05a',
        ts: '#3178c6',
        sh: '#89e051',
        bash: '#89e051',
        rb: '#701516',
        php: '#4f5d95',
        swift: '#f05138',
        kt: '#a97bff',
        hs: '#5e5086',
        // New formats added
        cob: '#003366',
        cbl: '#003366',
        f: '#4d4dff',
        for: '#4d4dff',
        f90: '#4d4dff',
        lisp: '#3fb68f',
        lsp: '#3fb68f',
        cl: '#3fb68f',
        asm: '#6e4a75',
        s: '#6e4a75',
        r: '#198ce7',
        R: '#198ce7',
        m: '#e16711',
        jl: '#a270ba',
        dart: '#00b4ab'
    };
    return colors[type] || '#14b8a6';
}

function mergeGraphData(newData) {
    if (!newData) {
        nodes = [];
        links = [];
        selectedNode = null;
        hoveredNode = null;
        activeFileBadge.textContent = 'No active file';
        activeFileBadge.title = '';
        showPlaceholder();
        return;
    }

    activeFileBadge.textContent = newData.activeFile.name;
    activeFileBadge.title = newData.activeFile.path;

    const oldNodesMap = new Map(nodes.map(n => [n.id, n]));
    const newNodes = [];
    const newLinks = [];

    const centerId = newData.activeFile.uri;
    let centerNode = oldNodesMap.get(centerId);
    if (!centerNode) {
        centerNode = {
            id: centerId,
            label: newData.activeFile.name,
            path: newData.activeFile.path,
            type: 'py',
            isCenter: true,
            x: 0,
            y: 0,
            vx: 0,
            vy: 0,
            r: 25,
            relation: 'active-file'
        };
    } else {
        centerNode.isCenter = true;
        centerNode.r = 25;
    }
    newNodes.push(centerNode);

    newData.links.forEach((link, i) => {
        const linkId = link.uri;
        let node = oldNodesMap.get(linkId);
        
        if (!node) {
            const angle = Math.random() * Math.PI * 2;
            const dist = restLength + (Math.random() * 40 - 20);
            node = {
                id: linkId,
                label: link.name,
                path: link.path,
                type: link.type,
                isCenter: false,
                x: centerNode.x + Math.cos(angle) * dist,
                y: centerNode.y + Math.sin(angle) * dist,
                vx: 0,
                vy: 0,
                r: 16,
                relation: link.relation
            };
        } else {
            node.isCenter = false;
            node.r = 16;
            node.relation = link.relation;
        }
        newNodes.push(node);

        newLinks.push({
            source: centerId,
            target: linkId,
            progress: Math.random()
        });
    });

    nodes = newNodes;
    links = newLinks;

    if (selectedNode && !nodes.some(n => n.id === selectedNode.id)) {
        selectedNode = null;
        showPlaceholder();
    } else if (selectedNode) {
        selectedNode = nodes.find(n => n.id === selectedNode.id);
        updateDetailsPanel(selectedNode);
    }

    if (panX === 0 && panY === 0) {
        resetView();
    }
}

window.addEventListener('message', event => {
    const message = event.data;
    switch (message.type) {
        case 'update':
            mergeGraphData(message.data);
            break;
    }
});

function showPlaceholder() {
    detailsPanel.innerHTML = '<div class="details-placeholder">Click a node to view file details</div>';
}

function updateDetailsPanel(node) {
    const relationText = node.relation.replace('-', ' ');
    detailsPanel.innerHTML = `
        <div class="details-content">
            <div class="details-file-header">
                <span class="details-name">${node.label}</span>
                <span class="details-relation ${node.relation}">${relationText}</span>
            </div>
            <div class="details-path" title="${node.path}">${node.path}</div>
            <div class="details-action-tip">💡 Double-click node to open file</div>
        </div>
    `;
}

function getWorldCoords(screenX, screenY) {
    const rect = canvas.getBoundingClientRect();
    const x = (screenX - rect.left - panX) / scale;
    const y = (screenY - rect.top - panY) / scale;
    return { x, y };
}

function getNodeAt(worldX, worldY) {
    for (let i = nodes.length - 1; i >= 0; i--) {
        const node = nodes[i];
        const dx = node.x - worldX;
        const dy = node.y - worldY;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist <= node.r + 4) {
            return node;
        }
    }
    return null;
}

canvas.addEventListener('mousedown', e => {
    const world = getWorldCoords(e.clientX, e.clientY);
    const clickedNode = getNodeAt(world.x, world.y);

    if (clickedNode) {
        if (e.detail === 2) {
            vscode.postMessage({ type: 'openFile', uri: clickedNode.id });
        } else {
            isDraggingNode = true;
            draggedNode = clickedNode;
            selectedNode = clickedNode;
            updateDetailsPanel(clickedNode);
        }
    } else {
        isPanning = true;
        startPanX = e.clientX - panX;
        startPanY = e.clientY - panY;
    }
});

canvas.addEventListener('mousemove', e => {
    mouseX = e.clientX;
    mouseY = e.clientY;
    const world = getWorldCoords(e.clientX, e.clientY);

    if (isDraggingNode && draggedNode) {
        draggedNode.x = world.x;
        draggedNode.y = world.y;
        draggedNode.vx = 0;
        draggedNode.vy = 0;
    } else if (isPanning) {
        panX = e.clientX - startPanX;
        panY = e.clientY - startPanY;
    } else {
        hoveredNode = getNodeAt(world.x, world.y);
    }
});

window.addEventListener('mouseup', () => {
    isDraggingNode = false;
    draggedNode = null;
    isPanning = false;
});

canvas.addEventListener('wheel', e => {
    e.preventDefault();
    const zoomFactor = 1.1;
    const mouseWorldBefore = getWorldCoords(e.clientX, e.clientY);
    
    if (e.deltaY < 0) {
        scale = Math.min(scale * zoomFactor, 3.0);
    } else {
        scale = Math.max(scale / zoomFactor, 0.4);
    }
    
    const rect = canvas.getBoundingClientRect();
    panX = (e.clientX - rect.left) - mouseWorldBefore.x * scale;
    panY = (e.clientY - rect.top) - mouseWorldBefore.y * scale;
});

document.getElementById('zoom-in').addEventListener('click', () => {
    const rect = canvas.getBoundingClientRect();
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;
    const worldCenter = getWorldCoords(centerX + rect.left, centerY + rect.top);
    scale = Math.min(scale * 1.25, 3.0);
    panX = centerX - worldCenter.x * scale;
    panY = centerY - worldCenter.y * scale;
});

document.getElementById('zoom-out').addEventListener('click', () => {
    const rect = canvas.getBoundingClientRect();
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;
    const worldCenter = getWorldCoords(centerX + rect.left, centerY + rect.top);
    scale = Math.max(scale / 1.25, 0.4);
    panX = centerX - worldCenter.x * scale;
    panY = centerY - worldCenter.y * scale;
});

document.getElementById('reset-view').addEventListener('click', resetView);

function updatePhysics() {
    const numNodes = nodes.length;
    for (let i = 0; i < numNodes; i++) {
        for (let j = i + 1; j < numNodes; j++) {
            const n1 = nodes[i];
            const n2 = nodes[j];
            const dx = n2.x - n1.x;
            const dy = n2.y - n1.y;
            const dist = Math.sqrt(dx * dx + dy * dy) || 1;

            if (dist < 400) {
                const force = kRepulsion / (dist * dist);
                const fx = (dx / dist) * force;
                const fy = (dy / dist) * force;

                if (n1 !== draggedNode && !n1.isCenter) {
                    n1.vx -= fx;
                    n1.vy -= fy;
                }
                if (n2 !== draggedNode && !n2.isCenter) {
                    n2.vx += fx;
                    n2.vy += fy;
                }
            }
        }
    }

    for (const link of links) {
        const source = nodes.find(n => n.id === link.source);
        const target = nodes.find(n => n.id === link.target);
        if (!source || !target) continue;

        const dx = target.x - source.x;
        const dy = target.y - source.y;
        const dist = Math.sqrt(dx * dx + dy * dy) || 1;
        const displacement = dist - restLength;
        const force = displacement * kAttraction;
        const fx = (dx / dist) * force;
        const fy = (dy / dist) * force;

        if (source !== draggedNode && !source.isCenter) {
            source.vx += fx;
            source.vy += fy;
        }
        if (target !== draggedNode && !target.isCenter) {
            target.vx -= fx;
            target.vy -= fy;
        }
    }

    for (const node of nodes) {
        if (node.isCenter) {
            if (node !== draggedNode) {
                node.x += (0 - node.x) * 0.1;
                node.y += (0 - node.y) * 0.1;
            }
            continue;
        }
        const dx = 0 - node.x;
        const dy = 0 - node.y;
        node.vx += dx * gravity;
        node.vy += dy * gravity;
    }

    for (const node of nodes) {
        if (node === draggedNode) continue;
        node.x += node.vx;
        node.y += node.vy;
        node.vx *= damping;
        node.vy *= damping;
    }
}

function drawGrid(rect) {
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.02)';
    ctx.lineWidth = 1;
    const gridSize = 40;
    const startX = -panX / scale;
    const startY = -panY / scale;
    const endX = (rect.width - panX) / scale;
    const endY = (rect.height - panY) / scale;
    const firstLineX = Math.floor(startX / gridSize) * gridSize;
    const firstLineY = Math.floor(startY / gridSize) * gridSize;

    for (let x = firstLineX; x < endX; x += gridSize) {
        ctx.beginPath(); ctx.moveTo(x, startY); ctx.lineTo(x, endY); ctx.stroke();
    }
    for (let y = firstLineY; y < endY; y += gridSize) {
        ctx.beginPath(); ctx.moveTo(startX, y); ctx.lineTo(endX, y); ctx.stroke();
    }
}

function drawGraph() {
    const rect = canvas.getBoundingClientRect();
    ctx.clearRect(0, 0, rect.width, rect.height);

    ctx.save();
    ctx.translate(panX, panY);
    ctx.scale(scale, scale);

    drawGrid(rect);

    links.forEach(link => {
        const source = nodes.find(n => n.id === link.source);
        const target = nodes.find(n => n.id === link.target);
        if (!source || !target) return;

        const isSelected = selectedNode && (selectedNode.id === source.id || selectedNode.id === target.id);
        const isHovered = hoveredNode && (hoveredNode.id === source.id || hoveredNode.id === target.id);
        
        ctx.beginPath();
        ctx.moveTo(source.x, source.y);
        ctx.lineTo(target.x, target.y);
        ctx.strokeStyle = isHovered || isSelected ? 'rgba(96, 165, 250, 0.45)' : 'rgba(255, 255, 255, 0.08)';
        ctx.lineWidth = isHovered || isSelected ? 2.5 : 1.5;
        ctx.stroke();

        link.progress = (link.progress + 0.004) % 1.0;
        const px = source.x + (target.x - source.x) * link.progress;
        const py = source.y + (target.y - source.y) * link.progress;

        ctx.beginPath();
        ctx.arc(px, py, 2.5, 0, Math.PI * 2);
        ctx.fillStyle = isSelected || isHovered ? '#93c5fd' : 'rgba(255, 255, 255, 0.4)';
        ctx.fill();
    });

    nodes.forEach(node => {
        const color = getFileTypeColor(node.type);
        const isHovered = hoveredNode && hoveredNode.id === node.id;
        const isSelected = selectedNode && selectedNode.id === node.id;

        ctx.beginPath();
        ctx.arc(node.x, node.y, node.r + 6, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${hexToRgb(color)}, ${isHovered || isSelected ? '0.22' : '0.06'})`;
        ctx.fill();

        ctx.beginPath();
        ctx.arc(node.x, node.y, node.r, 0, Math.PI * 2);
        const gradient = ctx.createRadialGradient(node.x - node.r*0.2, node.y - node.r*0.2, 2, node.x, node.y, node.r);
        gradient.addColorStop(0, adjustColorBrightness(color, 40));
        gradient.addColorStop(1, color);
        ctx.fillStyle = gradient;
        ctx.fill();

        ctx.beginPath();
        ctx.arc(node.x, node.y, node.r, 0, Math.PI * 2);
        ctx.strokeStyle = isSelected ? '#ffffff' : (isHovered ? 'rgba(255, 255, 255, 0.8)' : 'rgba(0, 0, 0, 0.25)');
        ctx.lineWidth = isSelected ? 2.5 : 2.0;
        ctx.stroke();

        if (node.isCenter) {
            ctx.beginPath();
            ctx.arc(node.x, node.y, node.r - 4, 0, Math.PI * 2);
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
            ctx.stroke();
        }

        ctx.fillStyle = '#ffffff';
        ctx.font = `600 ${node.isCenter ? 10 : 8}px sans-serif`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(node.type.toUpperCase(), node.x, node.y);

        if (scale > 0.5 || isHovered || isSelected) {
            ctx.fillStyle = isHovered || isSelected ? '#ffffff' : 'var(--text-secondary)';
            ctx.font = `${isHovered || isSelected ? '600' : 'normal'} 10px sans-serif`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'top';
            ctx.fillText(node.label, node.x, node.y + node.r + 6);
        }
    });

    ctx.restore();
}

function hexToRgb(hex) {
    const shorthandRegex = /^#?([a-f\d])([a-f\d])([a-f\d])$/i;
    const fullHex = hex.replace(shorthandRegex, (m, r, g, b) => r + r + g + g + b + b);
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(fullHex);
    return result ? `${parseInt(result[1], 16)}, ${parseInt(result[2], 16)}, ${parseInt(result[3], 16)}` : '255,255,255';
}

function adjustColorBrightness(hex, percent) {
    let R = parseInt(hex.substring(1, 3), 16);
    let G = parseInt(hex.substring(3, 5), 16);
    let B = parseInt(hex.substring(5, 7), 16);
    R = Math.min(255, parseInt((R * (100 + percent)) / 100));
    G = Math.min(255, parseInt((G * (100 + percent)) / 100));
    B = Math.min(255, parseInt((B * (100 + percent)) / 100));
    return `#${R.toString(16).padStart(2,'0')}${G.toString(16).padStart(2,'0')}${B.toString(16).padStart(2,'0')}`;
}

function animate() {
    updatePhysics();
    drawGraph();
    requestAnimationFrame(animate);
}

animate();
