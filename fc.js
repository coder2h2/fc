// fc.js
// JavaScript native implementation of FileConnect (fc) loading logic

const fs = require('fs');
const path = require('path');
const child_process = require('child_process');

const fc = {
    link: function(filepath) {
        if (!fs.existsSync(filepath)) {
            throw new Error(`FileConnect: File not found: ${filepath}`);
        }
        
        const ext = path.extname(filepath).toLowerCase();
        
        // 1. JSON loading
        if (ext === '.json') {
            return JSON.parse(fs.readFileSync(filepath, 'utf8'));
        }
        
        // 2. Static text formats (HTML, CSS, SQL, TXT)
        if (['.html', '.css', '.sql', '.txt', '.yaml', '.yml'].includes(ext)) {
            return {
                text: fs.readFileSync(filepath, 'utf8'),
                filepath: path.resolve(filepath),
                extension: ext
            };
        }
        
        // 3. Executable runners (Python, Shell, node)
        return {
            filepath: path.resolve(filepath),
            extension: ext,
            run: function(...args) {
                let cmd = [];
                if (ext === '.py') cmd = ['python3', filepath];
                else if (['.sh', '.bash'].includes(ext)) cmd = ['bash', filepath];
                else if (ext === '.js') cmd = ['node', filepath];
                else cmd = [filepath];
                
                const result = child_process.spawnSync(cmd[0], cmd.slice(1).concat(args), { encoding: 'utf8' });
                if (result.status !== 0) {
                    throw new Error(`Execution failed: ${result.stderr}`);
                }
                return result.stdout;
            }
        };
    }
};

module.exports = fc;
