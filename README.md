# FileConnect (fc) 🔗

FileConnect (fc) is a developer utility that links Python files to **all programming languages and static formats** (C, C++, Rust, Go, C#, Java, JS, TS, HTML, CSS, SQL, JSON, CSV, YAML, etc.) except Git.

This workspace has been cleaned of temporary demo files. Instead, it provides native FileConnect libraries and entry points showing how to **import `fc`** directly inside each programming language environment:

---

## 🎨 Importing `fc` in Programming Languages

The workspace provides the following native bindings and integration files:

1. **Python**:
   - Package: [fc/](file:///home/ip-ascii/fc/fc/)
   - Import syntax: `import fc`
2. **JavaScript / Node.js**:
   - Library: [fc.js](file:///home/ip-ascii/fc/fc.js)
   - Entry point: [main.js](file:///home/ip-ascii/fc/main.js)
   - Import syntax: `const fc = require('./fc');`
3. **Rust**:
   - Module: [fc.rs](file:///home/ip-ascii/fc/fc.rs)
   - Entry point: [main.rs](file:///home/ip-ascii/fc/main.rs)
   - Import syntax: `mod fc;`
4. **C / C++**:
   - Header: [fc.h](file:///home/ip-ascii/fc/fc.h)
   - Implementation: [fc.c](file:///home/ip-ascii/fc/fc.c)
   - Entry point: [main.c](file:///home/ip-ascii/fc/main.c)
   - Import syntax: `#include "fc.h"`
5. **Java**:
   - Helper class: [fc.java](file:///home/ip-ascii/fc/fc.java)
   - Entry point: [Main.java](file:///home/ip-ascii/fc/Main.java)
   - Import syntax: `// fc class compiles in the classpath`
6. **C#**:
   - Helper class: [fc.cs](file:///home/ip-ascii/fc/fc.cs)
   - Entry point: [main.cs](file:///home/ip-ascii/fc/main.cs)
   - Import syntax: `// fc class compiles in the build target`
7. **JSON**:
   - Settings entry: [main.json](file:///home/ip-ascii/fc/main.json)
   - Declaration: `"import": "fc"`

---

## 🎨 VS Code Extension Features

- **Interactive Sidebar / View**: Visualizes file connections as a glowing force-directed graph. Node colors match their file extension type (e.g. C, Rust, JS, CSS, HTML).
- **CodeLens Commands**: Banners render above strings containing file paths, allowing you to click `🔗 Open <filename>` directly.
- **Document Links**: Turns text file path strings inside quotes into standard Ctrl+Clickable links to open the file.

### How to Run in Development Mode
1. Open the `/home/ip-ascii/fc` directory in VS Code.
2. Press **`F5`** (or go to **Run > Start Debugging**). A new **[Extension Development Host]** window will open.
3. Open any workspace folder containing Python scripts in the new window.
4. Click the **FileConnect** icon in the left activity bar to see the live graph, or command-click paths directly in your editor.

---

## Python API: `fc.link($PATH)`

In your Python code, you can import `fc` and link files dynamically:
```python
import fc

# Programmatically link any file type by path
demo_c = fc.link("main.c")
demo_rs = fc.link("main.rs")
demo_html = fc.link("demo.html")

# Call compiled functions directly!
# print(demo_c.add(10, 20))
```
