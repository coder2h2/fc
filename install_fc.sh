#!/bin/bash

# install_fc.sh - Installer script for FileConnect (fc)
# Copies native language bindings to a target project directory.

set -e

# Default source dir is the location of this script
SRC_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [ -z "$1" ]; then
    echo "Usage: $0 <target_project_directory>"
    exit 1
fi

TARGET_DIR="$1"
mkdir -p "$TARGET_DIR"

echo "=== Installing FileConnect (fc) into $TARGET_DIR ==="

# 1. Helper function to copy files safely
copy_lib() {
    local src="$1"
    local dest_dir="$2"
    if [ -f "$src" ] || [ -d "$src" ]; then
        mkdir -p "$dest_dir"
        cp -R "$src" "$dest_dir/"
        echo "✓ Copied $(basename "$src") to $dest_dir"
    else
        echo "✗ Source not found: $src"
    fi
}

# 2. Python package setup
copy_lib "$SRC_DIR/fc" "$TARGET_DIR"

# 3. JavaScript / Node.js
copy_lib "$SRC_DIR/fc.js" "$TARGET_DIR/libs/js"

# 4. Rust
copy_lib "$SRC_DIR/fc.rs" "$TARGET_DIR/libs/rust"

# 5. C / C++
copy_lib "$SRC_DIR/fc.h" "$TARGET_DIR/libs/cpp"
copy_lib "$SRC_DIR/fc.c" "$TARGET_DIR/libs/cpp"

# 6. Java
copy_lib "$SRC_DIR/fc.java" "$TARGET_DIR/libs/java"

# 7. C#
copy_lib "$SRC_DIR/fc.cs" "$TARGET_DIR/libs/csharp"

echo "==============================================="
echo "FileConnect files copied successfully!"
echo "NOTE: Some languages require additional package registration."
