# -*- coding: utf-8 -*-

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FileConnect Graph: {active_name}</title>
    <style>
        :root {
            --bg-gradient-start: #0b0f19;
            --bg-gradient-end: #141c2f;
            --card-bg: rgba(22, 31, 51, 0.6);
            --card-border: rgba(255, 255, 255, 0.08);
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --accent-color: #3b82f6;
            --accent-glow: rgba(59, 130, 246, 0.4);
            
            --color-py: #387eb8;
            --color-html: #e34c26;
            --color-css: #264de4;
            --color-sql: #c084fc;
            --color-json: #eab308;
            --color-yaml: #10b981;
            --color-txt: #64748b;
            --color-native: #00599c;
            --color-script: #f1e05a;
            --color-other: #14b8a6;
        }

        body {
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, var(--bg-gradient-start), var(--bg-gradient-end));
            color: var(--text-primary);
            overflow: hidden;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }

        .container {
            display: flex;
            flex-direction: column;
            height: 100vh;
            padding: 16px;
            box-sizing: border-box;
            gap: 12px;
        }

        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 18px;
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            backdrop-filter: blur(12px);
            border-radius: 12px;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2);
        }

        .title {
            font-weight: 600;
            font-size: 1.1rem;
            letter-spacing: 0.5px;
            background: linear-gradient(90deg, #60a5fa, #a78bfa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .badge {
            font-size: 0.8rem;
            padding: 5px 10px;
            border-radius: 6px;
            background: rgba(59, 130, 246, 0.15);
            border: 1px solid rgba(59, 130, 246, 0.3);
            color: #93c5fd;
            max-width: 60%;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .canvas-container {
            position: relative;
            flex: 1;
            background: rgba(15, 23, 42, 0.4);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            overflow: hidden;
        }

        #graph-canvas {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            display: block;
            cursor: grab;
        }

        #graph-canvas:active {
            cursor: grabbing;
        }

        .controls {
            position: absolute;
            top: 12px;
            right: 12px;
            display: flex;
            flex-direction: column;
            gap: 6px;
            z-index: 10;
        }

        .controls button {
            width: 36px;
            height: 36px;
            border-radius: 8px;
            border: 1px solid var(--card-border);
            background: rgba(30, 41, 59, 0.7);
            color: var(--text-primary);
            font-size: 1.2rem;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            backdrop-filter: blur(8px);
            transition: all 0.2s ease;
        }

        .controls button:hover {
            background: rgba(59, 130, 246, 0.2);
            border-color: rgba(59, 130, 246, 0.4);
            color: #60a5fa;
            transform: scale(1.05);
        }

        .details-panel {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            backdrop-filter: blur(12px);
            border-radius: 12px;
            padding: 14px 18px;
            min-height: 80px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2);
        }

        .details-placeholder {
            color: var(--text-secondary);
            font-size: 0.9rem;
            text-align: center;
            font-style: italic;
        }

        .details-content {
            display: flex;
            flex-direction: column;
            gap: 6px;
        }

        .details-file-header {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .details-name {
            font-weight: 600;
            font-size: 1.05rem;
        }

        .details-relation {
            font-size: 0.75rem;
            padding: 3px 8px;
            border-radius: 4px;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .details-relation.same-name {
            background: rgba(167, 139, 250, 0.15);
            color: #c084fc;
            border: 1px solid rgba(167, 139, 250, 0.3);
        }

        .details-relation.reference {
            background: rgba(16, 185, 129, 0.15);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }

        .details-relation.import {
            background: rgba(59, 130, 246, 0.15);
            color: #60a5fa;
            border: 1px solid rgba(59, 130, 246, 0.3);
        }

        .details-relation.active-file {
            background: rgba(234, 179, 8, 0.15);
            color: #fde047;
            border: 1px solid rgba(234, 179, 8, 0.3);
        }

        .details-path {
            font-size: 0.8rem;
            color: var(--text-secondary);
            word-break: break-all;
        }

        .details-action-tip {
            font-size: 0.75rem;
            color: #60a5fa;
            margin-top: 4px;
            font-weight: 500;
        }

        .legend {
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
            justify-content: center;
            padding: 6px;
        }

        .legend-item {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.8rem;
            color: var(--text-secondary);
        }

        .color-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            display: inline-block;
        }

        .color-dot.py { background-color: var(--color-py); }
        .color-dot.html { background-color: var(--color-html); }
        .color-dot.css { background-color: var(--color-css); }
        .color-dot.sql { background-color: var(--color-sql); }
        .color-dot.config { background-color: var(--color-json); }
        .color-dot.native { background-color: var(--color-native); }
        .color-dot.script { background-color: var(--color-script); }
        .color-dot.other { background-color: var(--color-other); }

        #toast {
            position: absolute;
            top: 20px;
            left: 50%;
            transform: translateX(-50%) translateY(-100px);
            background: rgba(15, 23, 42, 0.9);
            border: 1px solid rgba(96, 165, 250, 0.4);
            padding: 10px 20px;
            border-radius: 8px;
            font-size: 0.85rem;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
            transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            z-index: 1000;
            color: #93c5fd;
            pointer-events: none;
        }

        #toast.show {
            transform: translateX(-50%) translateY(0);
        }
    </style>
</head>
<body>
    <div id="toast">File path copied to clipboard!</div>
    <div class="container">
        <div class="header">
            <span class="title">FileConnect (fc) Graph</span>
            <span id="active-file-badge" class="badge">Checking...</span>
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
            <div class="legend-item"><span class="color-dot html"></span> HTML/CSS</div>
            <div class="legend-item"><span class="color-dot sql"></span> SQL</div>
            <div class="legend-item"><span class="color-dot config"></span> Config</div>
            <div class="legend-item"><span class="color-dot native"></span> Native (C/C++/Rust/Go/Fortran/Asm)</div>
            <div class="legend-item"><span class="color-dot script"></span> Scripts (JS/TS/Ruby/PHP/Dart/Lisp/R)</div>
            <div class="legend-item"><span class="color-dot other"></span> Other</div>
        </div>
    </div>

    <script>
        // Data injected dynamically from Python
        const graphData = {graph_data_json};

        // DOM elements
        const canvas = document.getElementById('graph-canvas');
        const ctx = canvas.getContext('2d');
        const activeFileBadge = document.getElementById('active-file-badge');
        const detailsPanel = document.getElementById('details-panel');
        const toast = document.getElementById('toast');

        // State variables
        let nodes = [];
        let links = [];
        let selectedNode = null;
        let hoveredNode = null;

        // View scale/pan
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

        // Physics variables
        const kRepulsion = 4000;
        const kAttraction = 0.04;
        const restLength = 130;
        const gravity = 0.015;
        const damping = 0.82;

        function showToast(text) {
            toast.textContent = text;
            toast.classList.add('show');
            setTimeout(() => toast.classList.remove('show'), 2000);
        }

        function getFileTypeColor(type) {
            const colors = {
                // Languages requested
                py: '#387eb8',
                html: '#e34c26',
                css: '#264de4',
                sql: '#c084fc',
                json: '#eab308',
                yaml: '#10b981',
                yml: '#10b981',
                csv: '#22c55e',
                txt: '#64748b',
                // C / C++ / Rust / Go / C# / Java
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

        function setupGraph() {
            if (!graphData) return;
            
            activeFileBadge.textContent = graphData.activeFile.name;
            activeFileBadge.title = graphData.activeFile.path;

            // Center node
            const centerNode = {
                id: graphData.activeFile.path,
                label: graphData.activeFile.name,
                path: graphData.activeFile.path,
                type: 'py',
                isCenter: true,
                x: 0,
                y: 0,
                vx: 0,
                vy: 0,
                r: 26,
                relation: 'active-file'
            };
            nodes.push(centerNode);

            // Leaf nodes
            graphData.links.forEach((link, i) => {
                const angle = (i / graphData.links.length) * Math.PI * 2;
                const dist = restLength + (Math.random() * 40 - 20);
                nodes.push({
                    id: link.path,
                    label: link.name,
                    path: link.path,
                    type: link.type,
                    isCenter: false,
                    x: Math.cos(angle) * dist,
                    y: Math.sin(angle) * dist,
                    vx: 0,
                    vy: 0,
                    r: 17,
                    relation: link.relation
                });

                links.push({
                    source: centerNode.id,
                    target: link.path,
                    progress: Math.random()
                });
            });

            resetView();
        }

        function resetView() {
            scale = 1.0;
            const rect = canvas.getBoundingClientRect();
            panX = rect.width / 2;
            panY = rect.height / 2;
        }

        function resizeCanvas() {
            const rect = canvas.parentElement.getBoundingClientRect();
            canvas.width = rect.width * window.devicePixelRatio;
            canvas.height = rect.height * window.devicePixelRatio;
            canvas.style.width = '100%';
            canvas.style.height = '100%';
            ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
            if (panX === 0 && panY === 0) resetView();
        }

        window.addEventListener('resize', resizeCanvas);

        function getWorldCoords(screenX, screenY) {
            const rect = canvas.getBoundingClientRect();
            return {
                x: (screenX - rect.left - panX) / scale,
                y: (screenY - rect.top - panY) / scale
            };
        }

        function getNodeAt(worldX, worldY) {
            for (let i = nodes.length - 1; i >= 0; i--) {
                const n = nodes[i];
                const dist = Math.hypot(n.x - worldX, n.y - worldY);
                if (dist <= n.r + 4) return n;
            }
            return null;
        }

        canvas.addEventListener('mousedown', e => {
            const world = getWorldCoords(e.clientX, e.clientY);
            const clicked = getNodeAt(world.x, world.y);

            if (clicked) {
                if (e.detail === 2) {
                    navigator.clipboard.writeText(clicked.path).then(() => {
                        showToast(`Copied: ${clicked.label}`);
                    }).catch(() => {
                        showToast(`Path: ${clicked.path}`);
                    });
                } else {
                    isDraggingNode = true;
                    draggedNode = clicked;
                    selectedNode = clicked;
                    updateDetails(clicked);
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
            const zoom = 1.1;
            const worldBefore = getWorldCoords(e.clientX, e.clientY);
            if (e.deltaY < 0) {
                scale = Math.min(scale * zoom, 3.0);
            } else {
                scale = Math.max(scale / zoom, 0.4);
            }
            const rect = canvas.getBoundingClientRect();
            panX = (e.clientX - rect.left) - worldBefore.x * scale;
            panY = (e.clientY - rect.top) - worldBefore.y * scale;
        });

        document.getElementById('zoom-in').addEventListener('click', () => {
            const rect = canvas.getBoundingClientRect();
            const wCenter = getWorldCoords(rect.width/2 + rect.left, rect.height/2 + rect.top);
            scale = Math.min(scale * 1.25, 3.0);
            panX = rect.width/2 - wCenter.x * scale;
            panY = rect.height/2 - wCenter.y * scale;
        });

        document.getElementById('zoom-out').addEventListener('click', () => {
            const rect = canvas.getBoundingClientRect();
            const wCenter = getWorldCoords(rect.width/2 + rect.left, rect.height/2 + rect.top);
            scale = Math.max(scale / 1.25, 0.4);
            panX = rect.width/2 - wCenter.x * scale;
            panY = rect.height/2 - wCenter.y * scale;
        });

        document.getElementById('reset-view').addEventListener('click', resetView);

        function updateDetails(node) {
            const relText = node.relation.replace('-', ' ');
            detailsPanel.innerHTML = `
                <div class="details-content">
                    <div class="details-file-header">
                        <span class="details-name">${node.label}</span>
                        <span class="details-relation ${node.relation}">${relText}</span>
                    </div>
                    <div class="details-path">${node.path}</div>
                    <div class="details-action-tip">💡 Double-click node to copy path to clipboard</div>
                </div>
            `;
        }

        function updatePhysics() {
            const num = nodes.length;
            for (let i = 0; i < num; i++) {
                for (let j = i + 1; j < num; j++) {
                    const n1 = nodes[i];
                    const n2 = nodes[j];
                    const dx = n2.x - n1.x;
                    const dy = n2.y - n1.y;
                    const dist = Math.hypot(dx, dy) || 1;
                    if (dist < 400) {
                        const force = kRepulsion / (dist * dist);
                        const fx = (dx / dist) * force;
                        const fy = (dy / dist) * force;
                        if (n1 !== draggedNode && !n1.isCenter) { n1.vx -= fx; n1.vy -= fy; }
                        if (n2 !== draggedNode && !n2.isCenter) { n2.vx += fx; n2.vy += fy; }
                    }
                }
            }

            links.forEach(l => {
                const s = nodes.find(n => n.id === l.source);
                const t = nodes.find(n => n.id === l.target);
                if (!s || !t) return;
                const dx = t.x - s.x;
                const dy = t.y - s.y;
                const dist = Math.hypot(dx, dy) || 1;
                const force = (dist - restLength) * kAttraction;
                const fx = (dx / dist) * force;
                const fy = (dy / dist) * force;
                if (s !== draggedNode && !s.isCenter) { s.vx += fx; s.vy += fy; }
                if (t !== draggedNode && !t.isCenter) { t.vx -= fx; t.vy -= fy; }
            });

            nodes.forEach(n => {
                if (n.isCenter) {
                    if (n !== draggedNode) {
                        n.x += (0 - n.x) * 0.1;
                        n.y += (0 - n.y) * 0.1;
                    }
                } else {
                    n.vx += (0 - n.x) * gravity;
                    n.vy += (0 - n.y) * gravity;
                    if (n !== draggedNode) {
                        n.x += n.vx;
                        n.y += n.vy;
                        n.vx *= damping;
                        n.vy *= damping;
                    }
                }
            });
        }

        function drawGrid(rect) {
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.02)';
            ctx.lineWidth = 1;
            const size = 40;
            const startX = -panX / scale;
            const startY = -panY / scale;
            const endX = (rect.width - panX) / scale;
            const endY = (rect.height - panY) / scale;
            const firstX = Math.floor(startX / size) * size;
            const firstY = Math.floor(startY / size) * size;

            for (let x = firstX; x < endX; x += size) {
                ctx.beginPath(); ctx.moveTo(x, startY); ctx.lineTo(x, endY); ctx.stroke();
            }
            for (let y = firstY; y < endY; y += size) {
                ctx.beginPath(); ctx.moveTo(startX, y); ctx.lineTo(endX, y); ctx.stroke();
            }
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

        function drawGraph() {
            const rect = canvas.getBoundingClientRect();
            ctx.clearRect(0, 0, rect.width, rect.height);

            ctx.save();
            ctx.translate(panX, panY);
            ctx.scale(scale, scale);

            drawGrid(rect);

            links.forEach(l => {
                const s = nodes.find(n => n.id === l.source);
                const t = nodes.find(n => n.id === l.target);
                if (!s || !t) return;
                const active = selectedNode && (selectedNode.id === s.id || selectedNode.id === t.id);
                const hover = hoveredNode && (hoveredNode.id === s.id || hoveredNode.id === t.id);

                ctx.beginPath();
                ctx.moveTo(s.x, s.y);
                ctx.lineTo(t.x, t.y);
                ctx.strokeStyle = active || hover ? 'rgba(96, 165, 250, 0.45)' : 'rgba(255, 255, 255, 0.08)';
                ctx.lineWidth = active || hover ? 2.5 : 1.5;
                ctx.stroke();

                l.progress = (l.progress + 0.004) % 1.0;
                const px = s.x + (t.x - s.x) * l.progress;
                const py = s.y + (t.y - s.y) * l.progress;
                ctx.beginPath();
                ctx.arc(px, py, 2.5, 0, Math.PI * 2);
                ctx.fillStyle = active || hover ? '#93c5fd' : 'rgba(255, 255, 255, 0.4)';
                ctx.fill();
            });

            nodes.forEach(n => {
                const color = getFileTypeColor(n.type);
                const hover = hoveredNode && hoveredNode.id === n.id;
                const active = selectedNode && selectedNode.id === n.id;

                ctx.beginPath();
                ctx.arc(n.x, n.y, n.r + 6, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(${hexToRgb(color)}, ${hover || active ? '0.22' : '0.06'})`;
                ctx.fill();

                ctx.beginPath();
                ctx.arc(n.x, n.y, n.r);
                const grad = ctx.createRadialGradient(n.x - n.r*0.2, n.y - n.r*0.2, 2, n.x, n.y, n.r);
                grad.addColorStop(0, adjustColorBrightness(color, 40));
                grad.addColorStop(1, color);
                ctx.fillStyle = grad;
                ctx.fill();

                ctx.beginPath();
                ctx.arc(n.x, n.y, n.r);
                ctx.strokeStyle = active ? '#ffffff' : (hover ? 'rgba(255,255,255,0.8)' : 'rgba(0,0,0,0.25)');
                ctx.lineWidth = active ? 2.5 : 2.0;
                ctx.stroke();

                if (n.isCenter) {
                    ctx.beginPath();
                    ctx.arc(n.x, n.y, n.r - 4, 0, Math.PI * 2);
                    ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
                    ctx.stroke();
                }

                ctx.fillStyle = '#ffffff';
                ctx.font = `600 ${n.isCenter ? 10 : 8}px sans-serif`;
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(n.type.toUpperCase(), n.x, n.y);

                if (scale > 0.5 || hover || active) {
                    ctx.fillStyle = hover || active ? '#ffffff' : 'var(--text-secondary)';
                    ctx.font = `${hover || active ? '600' : 'normal'} 10px sans-serif`;
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'top';
                    ctx.fillText(n.label, n.x, n.y + n.r + 6);
                }
            });

            ctx.restore();
        }

        function animate() {
            updatePhysics();
            drawGraph();
            requestAnimationFrame(animate);
        }

        // Run
        setupGraph();
        setTimeout(resizeCanvas, 50);
        animate();
    </script>
</body>
</html>
"""
