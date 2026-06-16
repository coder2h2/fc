# FileConnect (fc) 🔗

FileConnect (fc) is a developer utility that links Python files to **all programming languages and static formats** (C, C++, Rust, Go, C#, Java, JS, TS, HTML, CSS, SQL, JSON, CSV, YAML, etc.) except Git.

This workspace has been cleaned of temporary demo files. Instead, it provides native FileConnect libraries and entry points showing how to **import `fc`** directly inside each programming language environment:

---

## 📦 Installation & Setup

### 1. Global Installation (Python Importer)
To install the core FileConnect import engine globally in your active Python environment:
```bash
pip install -e .
```

### 2. Copying Libraries to a Target Project Workspace
To copy the native library bindings (`fc.js`, `fc.rs`, `fc.java`, etc.) directly into a target project workspace, use the provided installation script:
```bash
./install_fc.sh <target_project_directory>
```
This will set up the respective wrappers under:
* `your_project/fc/` (Python Package)
* `your_project/libs/js/fc.js` (JavaScript/Node/TS)
* `your_project/libs/rust/fc.rs` (Rust)
* `your_project/libs/cpp/fc.h` & `fc.c` (C/C++)
* `your_project/libs/java/fc.java` (Java)
* `your_project/libs/csharp/fc.cs` (C#)

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

## 🚀 Python API & Usage Examples

### 1. Basic Linking
Import `fc` and programmatically link any file type directly into your Python namespace:

```python
import fc

# Link files dynamically (compiles native code behind the scenes)
demo_c = fc.link("main.c")
demo_rs = fc.link("main.rs")
config = fc.link("settings.json")
styles = fc.link("theme.css")

# 1. Call native compiled functions directly in memory
result = demo_c.add_numbers(10, 20)

# 2. Access parsed JSON/YAML data directly as attributes
db_host = config.database["host"]

# 3. Access parsed CSS selectors as attributes
container_styles = styles.container
print(container_styles["display"])  # e.g., "flex"
```

### 2. Multi-Language Pipeline (Signaling Any-to-Any)
Use Python to coordinate execution across multiple programming languages natively:

```python
import fc

# Load different language modules
data_fetcher = fc.link("fetch_data.js")  # JavaScript script runner
c_processor = fc.link("process.c")        # C native compiled library
rust_writer = fc.link("write_log.rs")     # Rust native compiled library

# Step 1: Run JavaScript runner to retrieve API data
json_data = data_fetcher.run()

# Step 2: Pass output to a C function to parse/compute in memory
computed_value = c_processor.compute_metrics(json_data)

# Step 3: Trigger a Rust library function to save the final log
success = rust_writer.log_result(computed_value)
```
