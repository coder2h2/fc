# -*- coding: utf-8 -*-
"""
FileConnect (fc)
A Python library that links Python files to all file types (HTML, CSS, SQL, 
JSON, CSV, YAML, Rust, Go, C, C++, C#, Java, JS, TS, Python, PHP, Ruby, 
Swift, Kotlin, Haskell, Shell), allowing them to be imported directly 
as Python modules.
"""

import os
import re
import sys
import json
import csv
import inspect
import tempfile
import webbrowser
import subprocess
import shutil
import ctypes
import types
import importlib.abc
import importlib.machinery
from .visualizer_template import HTML_TEMPLATE

# --- Native Library Wrapper Modules ---

class NativeModule(types.ModuleType):
    """Dynamic module wrapper for compiled C/C++/Rust/Go shared libraries using ctypes."""
    def __init__(self, name, lib_path):
        super().__init__(name)
        self.__file__ = lib_path
        self.lib_path = lib_path
        self.lib = ctypes.CDLL(lib_path)

    def __getattr__(self, name):
        try:
            return getattr(self.lib, name)
        except AttributeError:
            return super().__getattribute__(name)

class DotNetModule(types.ModuleType):
    """Dynamic module wrapper for compiled C# assemblies, exposing execution runner."""
    def __init__(self, name, exe_path):
        super().__init__(name)
        self.__file__ = exe_path
        self.exe_path = exe_path

    def run(self, *args):
        """Execute the compiled C# assembly with arguments and return stdout."""
        cmd = [self.exe_path] if self.exe_path.endswith('.exe') else ['mono', self.exe_path]
        if not shutil.which(cmd[0]):
            cmd = ['dotnet', self.exe_path]
        
        proc = subprocess.run(cmd + list(args), capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError(f"C# execution failed: {proc.stderr}")
        return proc.stdout

class RunnerModule(types.ModuleType):
    """Dynamic module wrapper for compiled or interpreted runner scripts."""
    def __init__(self, name, filepath, run_cmd_loader):
        super().__init__(name)
        self.__file__ = filepath
        self.filepath = filepath
        self.run_cmd_loader = run_cmd_loader

    def run(self, *args):
        """Execute the script/compiled program with arguments and return stdout."""
        cmd = self.run_cmd_loader()
        proc = subprocess.run(cmd + list(args), capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError(f"Execution failed for {self.filepath}:\n{proc.stderr}")
        return proc.stdout

# --- Compile helper functions ---

def compile_native(src_path, ext):
    """Compile C, C++, Rust, Go, Fortran, or Assembly source files into a shared library (.so) with caching."""
    src_mtime = os.path.getmtime(src_path)
    cache_dir = os.path.join(os.path.dirname(src_path), '.fc_cache')
    os.makedirs(cache_dir, exist_ok=True)
    
    out_name = os.path.splitext(os.path.basename(src_path))[0] + '.so'
    out_path = os.path.abspath(os.path.join(cache_dir, out_name))

    if os.path.exists(out_path):
        if os.path.getmtime(out_path) > src_mtime:
            return out_path

    if ext == '.c':
        if not shutil.which('gcc') and not shutil.which('clang'):
            raise ImportError("Compiler 'gcc' or 'clang' is required to import C files.")
        cc = 'gcc' if shutil.which('gcc') else 'clang'
        cmd = [cc, '-shared', '-fPIC', '-o', out_path, src_path]
        
    elif ext in ['.cpp', '.cc']:
        if not shutil.which('g++') and not shutil.which('clang++'):
            raise ImportError("Compiler 'g++' or 'clang++' is required to import C++ files.")
        cxx = 'g++' if shutil.which('g++') else 'clang++'
        cmd = [cxx, '-shared', '-fPIC', '-o', out_path, src_path]

    elif ext == '.rs':
        if not shutil.which('rustc'):
            raise ImportError("Compiler 'rustc' is required to import Rust files.")
        cmd = ['rustc', '--crate-type', 'cdylib', '-o', out_path, src_path]

    elif ext == '.go':
        if not shutil.which('go'):
            raise ImportError("Compiler 'go' is required to import Go files.")
        cmd = ['go', 'build', '-buildmode', 'c-shared', '-o', out_path, src_path]

    elif ext in ['.f', '.for', '.f90']:
        if not shutil.which('gfortran'):
            raise ImportError("Compiler 'gfortran' is required to import Fortran files.")
        cmd = ['gfortran', '-shared', '-fPIC', '-o', out_path, src_path]

    elif ext in ['.s', '.asm']:
        if not shutil.which('gcc') and not shutil.which('clang'):
            raise ImportError("Compiler 'gcc' or 'clang' is required to compile Assembly files.")
        cc = 'gcc' if shutil.which('gcc') else 'clang'
        cmd = [cc, '-shared', '-fPIC', '-o', out_path, src_path]
    else:
        raise ValueError(f"Unsupported compilation extension: {ext}")

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise ImportError(f"Compilation failed for {src_path}:\n{proc.stderr}")
        
    return out_path

def compile_csharp(src_path):
    """Compile C# source files into an executable assembly with caching."""
    src_mtime = os.path.getmtime(src_path)
    cache_dir = os.path.join(os.path.dirname(src_path), '.fc_cache')
    os.makedirs(cache_dir, exist_ok=True)
    
    out_name = os.path.splitext(os.path.basename(src_path))[0] + '.exe'
    out_path = os.path.abspath(os.path.join(cache_dir, out_name))

    if os.path.exists(out_path):
        if os.path.getmtime(out_path) > src_mtime:
            return out_path

    if shutil.which('mcs'):
        cmd = ['mcs', f'-out:{out_path}', src_path]
    elif shutil.which('csc'):
        cmd = ['csc', f'-out:{out_path}', src_path]
    elif shutil.which('dotnet'):
        cmd = ['dotnet', 'csc', f'-out:{out_path}', src_path]
    else:
        raise ImportError("C# compiler 'mcs' or 'csc' or 'dotnet' is required to import C# files.")

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise ImportError(f"C# compilation failed for {src_path}:\n{proc.stderr}")
        
    return out_path

def compile_java(path):
    src_mtime = os.path.getmtime(path)
    cache_dir = os.path.join(os.path.dirname(path), '.fc_cache')
    os.makedirs(cache_dir, exist_ok=True)
    class_name = os.path.splitext(os.path.basename(path))[0]
    
    if not shutil.which('javac'):
        return None
        
    class_path = os.path.join(cache_dir, class_name + '.class')
    if not os.path.exists(class_path) or os.path.getmtime(class_path) < src_mtime:
        proc = subprocess.run(['javac', '-d', cache_dir, path], capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError(f"Java compilation failed:\n{proc.stderr}")
            
    return lambda: ['java', '-cp', cache_dir, class_name]

def compile_kotlin(path):
    src_mtime = os.path.getmtime(path)
    cache_dir = os.path.join(os.path.dirname(path), '.fc_cache')
    os.makedirs(cache_dir, exist_ok=True)
    jar_name = os.path.splitext(os.path.basename(path))[0] + '.jar'
    jar_path = os.path.join(cache_dir, jar_name)
    
    if not shutil.which('kotlinc'):
        return None
        
    if not os.path.exists(jar_path) or os.path.getmtime(jar_path) < src_mtime:
        proc = subprocess.run(['kotlinc', path, '-include-runtime', '-d', jar_path], capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError(f"Kotlin compilation failed:\n{proc.stderr}")
            
    return lambda: ['java', '-jar', jar_path]

def compile_haskell(path):
    src_mtime = os.path.getmtime(path)
    cache_dir = os.path.join(os.path.dirname(path), '.fc_cache')
    os.makedirs(cache_dir, exist_ok=True)
    bin_name = os.path.splitext(os.path.basename(path))[0] + '_hs'
    bin_path = os.path.join(cache_dir, bin_name)
    
    if not shutil.which('ghc'):
        return None
        
    if not os.path.exists(bin_path) or os.path.getmtime(bin_path) < src_mtime:
        proc = subprocess.run(['ghc', '-outputdir', cache_dir, '-o', bin_path, path], capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError(f"Haskell compilation failed:\n{proc.stderr}")
            
    return lambda: [bin_path]

def compile_swift(path):
    src_mtime = os.path.getmtime(path)
    cache_dir = os.path.join(os.path.dirname(path), '.fc_cache')
    os.makedirs(cache_dir, exist_ok=True)
    bin_name = os.path.splitext(os.path.basename(path))[0] + '_swift'
    bin_path = os.path.join(cache_dir, bin_name)
    
    if not shutil.which('swiftc'):
        return None
        
    if not os.path.exists(bin_path) or os.path.getmtime(bin_path) < src_mtime:
        proc = subprocess.run(['swiftc', '-o', bin_path, path], capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError(f"Swift compilation failed:\n{proc.stderr}")
            
    return lambda: [bin_path]

def compile_cobol(path):
    src_mtime = os.path.getmtime(path)
    cache_dir = os.path.join(os.path.dirname(path), '.fc_cache')
    os.makedirs(cache_dir, exist_ok=True)
    bin_name = os.path.splitext(os.path.basename(path))[0] + '_cob'
    bin_path = os.path.join(cache_dir, bin_name)
    
    if not shutil.which('cobc'):
        return None
        
    if not os.path.exists(bin_path) or os.path.getmtime(bin_path) < src_mtime:
        proc = subprocess.run(['cobc', '-x', '-o', bin_path, path], capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError(f"COBOL compilation failed:\n{proc.stderr}")
            
    return lambda: [bin_path]

# --- FileConnect Import Hooks ---

class FileConnectLoader(importlib.abc.Loader):
    def __init__(self, filepath, ext):
        self.filepath = filepath
        self.ext = ext

    def exec_module(self, module):
        module.__file__ = self.filepath
        module.filepath = self.filepath
        module.extension = self.ext

        # 1. Native libraries (compiled C/C++/Rust/Go/Fortran/Assembly)
        if self.ext in ['.c', '.cpp', '.cc', '.rs', '.go', '.f', '.for', '.f90', '.s', '.asm']:
            try:
                so_path = compile_native(self.filepath, self.ext)
                module.__class__ = NativeModule
                NativeModule.__init__(module, module.__name__, so_path)
            except Exception as e:
                module.error = e
                raise ImportError(f"Could not load native module: {e}") from e
            return

        # 2. C# compilation
        if self.ext == '.cs':
            try:
                exe_path = compile_csharp(self.filepath)
                module.__class__ = DotNetModule
                DotNetModule.__init__(module, module.__name__, exe_path)
            except Exception as e:
                module.error = e
                raise ImportError(f"Could not load C# module: {e}") from e
            return

        # 3. Interactively run formats (interpreted scripts or compiled runners)
        runners = {
            '.js': lambda path: ['node', path] if shutil.which('node') else None,
            '.ts': lambda path: (['deno', 'run', path] if shutil.which('deno') 
                                 else (['ts-node', path] if shutil.which('ts-node') else None)),
            '.sh': lambda path: ['bash', path],
            '.bash': lambda path: ['bash', path],
            '.py': lambda path: [sys.executable, path],
            '.rb': lambda path: ['ruby', path] if shutil.which('ruby') else None,
            '.php': lambda path: ['php', path] if shutil.which('php') else None,
            
            # Compiled runners
            '.java': lambda path: compile_java(path),
            '.kt': lambda path: compile_kotlin(path),
            '.hs': lambda path: compile_haskell(path),
            '.swift': lambda path: compile_swift(path),
            '.cob': lambda path: compile_cobol(path),
            '.cbl': lambda path: compile_cobol(path),
            
            # Interpreted runners
            '.lisp': lambda path: ['sbcl', '--script', path] if shutil.which('sbcl') else (['clisp', path] if shutil.which('clisp') else None),
            '.lsp': lambda path: ['sbcl', '--script', path] if shutil.which('sbcl') else (['clisp', path] if shutil.which('clisp') else None),
            '.cl': lambda path: ['sbcl', '--script', path] if shutil.which('sbcl') else (['clisp', path] if shutil.which('clisp') else None),
            '.r': lambda path: ['Rscript', path] if shutil.which('Rscript') else None,
            '.R': lambda path: ['Rscript', path] if shutil.which('Rscript') else None,
            '.m': lambda path: ['octave', '-q', path] if shutil.which('octave') else (['matlab', '-batch', f"run('{path}')"] if shutil.which('matlab') else None),
            '.jl': lambda path: ['julia', path] if shutil.which('julia') else None,
            '.dart': lambda path: ['dart', 'run', path] if shutil.which('dart') else (['dart', path] if shutil.which('dart') else None),
        }

        if self.ext in runners:
            try:
                cmd_builder = runners[self.ext]
                cmd = cmd_builder(self.filepath)
                if cmd is None:
                    runner_names = {'.js': 'Node.js', '.ts': 'Deno or ts-node', '.rb': 'Ruby', '.php': 'PHP', 
                                    '.java': 'Java SDK (javac)', '.kt': 'Kotlin compiler (kotlinc)', 
                                    '.hs': 'GHC (Haskell)', '.swift': 'Swift compiler'}
                    name_req = runner_names.get(self.ext, 'runner')
                    raise ImportError(f"Required interpreter/compiler '{name_req}' is missing on the system.")
                
                run_cmd_loader = cmd if callable(cmd) else (lambda: cmd)

                module.__class__ = RunnerModule
                RunnerModule.__init__(module, module.__name__, self.filepath, run_cmd_loader)
            except Exception as e:
                module.error = e
                raise ImportError(f"Could not load runner module: {e}") from e
            return

        # 4. Standard text/config formats
        try:
            with open(self.filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            module.error = e
            return

        if self.ext == '.json':
            try:
                data = json.loads(content)
                module.data = data
                if isinstance(data, dict):
                    module.__dict__.update(data)
            except Exception as e:
                module.error = e

        elif self.ext == '.csv':
            try:
                reader = csv.DictReader(content.splitlines())
                rows = list(reader)
                module.rows = rows
                module.headers = reader.fieldnames
                module.data = rows
            except Exception as e:
                module.error = e

        elif self.ext == '.sql':
            module.text = content
            module.query = content
            def execute(connection, **params):
                cursor = connection.cursor()
                cursor.execute(content, params)
                return cursor
            module.execute = execute

        elif self.ext == '.html':
            module.text = content
            module.content = content
            def render(**context):
                result = content
                for k, v in context.items():
                    result = result.replace(f"{{{{{k}}}}}", str(v))
                return result
            module.render = render

        elif self.ext == '.css':
            module.text = content
            module.content = content
            module.lines = content.splitlines()
            rules = {}
            try:
                # Remove comments
                css_clean = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
                blocks = re.findall(r'([^{]+)\{([^}]+)\}', css_clean)
                for selector, body in blocks:
                    selector = selector.strip()
                    if not selector: continue
                    props = {}
                    for line in body.split(';'):
                        if ':' in line:
                            k, v = line.split(':', 1)
                            props[k.strip()] = v.strip()
                    if props:
                        rules[selector] = props
                module.rules = rules
                module.data = rules
                # Expose selectors with valid python identifier names as attributes
                for sel, props in rules.items():
                    attr_name = re.sub(r'[^a-zA-Z0-9_]', '_', sel).strip('_')
                    if attr_name and not attr_name[0].isdigit():
                        setattr(module, attr_name, props)
            except Exception as e:
                module.error = e

        elif self.ext in ['.yaml', '.yml']:
            module.text = content
            try:
                import yaml
                data = yaml.safe_load(content)
                module.data = data
                if isinstance(data, dict):
                    module.__dict__.update(data)
            except ImportError:
                data = {}
                for line in content.splitlines():
                    if ':' in line and not line.strip().startswith('#'):
                        parts = line.split(':', 1)
                        k = parts[0].strip()
                        v = parts[1].strip().strip('"').strip("'")
                        data[k] = v
                module.data = data
                module.__dict__.update(data)
        else:
            module.text = content
            module.content = content
            module.lines = content.splitlines()

class FileConnectFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        name = fullname.split('.')[-1]

        suffixes = {
            '_json': '.json',
            '_csv': '.csv',
            '_sql': '.sql',
            '_html': '.html',
            '_css': '.css',
            '_txt': '.txt',
            '_yaml': '.yaml',
            '_yml': '.yml',
            '_rs': '.rs',
            '_go': '.go',
            '_c': '.c',
            '_cpp': '.cpp',
            '_cs': '.cs',
            '_java': '.java',
            '_js': '.js',
            '_ts': '.ts',
            '_sh': '.sh',
            '_bash': '.bash',
            '_rb': '.rb',
            '_php': '.php',
            '_swift': '.swift',
            '_kt': '.kt',
            '_hs': '.hs',
            '_cob': '.cob',
            '_cbl': '.cbl',
            '_f': '.f',
            '_for': '.for',
            '_f90': '.f90',
            '_lisp': '.lisp',
            '_lsp': '.lsp',
            '_cl': '.cl',
            '_asm': '.asm',
            '_s': '.s',
            '_r': '.r',
            '_R': '.R',
            '_m': '.m',
            '_jl': '.jl',
            '_dart': '.dart'
        }

        target_ext = None
        base_name = name
        for suffix, ext in suffixes.items():
            if name.endswith(suffix):
                target_ext = ext
                base_name = name[:-len(suffix)]
                break

        search_dirs = path if path else sys.path
        if not path:
            search_dirs = [os.getcwd()] + [
                p for p in sys.path 
                if p and not any(x in p for x in ['/usr/lib', '/usr/local/lib', '/lib/', 'site-packages', 'dist-packages', '.zip'])
            ]

        for directory in search_dirs:
            if not directory or not os.path.isdir(directory):
                continue

            candidates = []
            if target_ext:
                candidates.append((base_name + target_ext, target_ext))
                candidates.append((name + target_ext, target_ext))
            else:
                extensions = ['.json', '.csv', '.sql', '.html', '.css', '.txt', 
                              '.yaml', '.yml', '.rs', '.go', '.c', '.cpp', '.cs',
                              '.java', '.js', '.ts', '.sh', '.bash', '.py', '.rb',
                              '.php', '.swift', '.kt', '.hs', '.cob', '.cbl', 
                              '.f', '.for', '.f90', '.lisp', '.lsp', '.cl', 
                              '.asm', '.s', '.r', '.R', '.m', '.jl', '.dart']
                for ext in extensions:
                    candidates.append((name + ext, ext))

            for filename, ext in candidates:
                filepath = os.path.join(directory, filename)
                if os.path.exists(filepath) and os.path.isfile(filepath):
                    loader = FileConnectLoader(filepath, ext)
                    return importlib.machinery.ModuleSpec(fullname, loader, origin=filepath)

        return None

sys.meta_path.insert(0, FileConnectFinder())

# --- Programmatic Visualizer Scan Engine ---

def scan_file(file_path):
    if not file_path or not os.path.exists(file_path):
        return None

    file_dir = os.path.dirname(file_path)
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    links = []

    def add_link(name, path_str, relation, type_str=None):
        if path_str == os.path.abspath(file_path):
            return
        ext = type_str or os.path.splitext(path_str)[1].replace('.', '').lower()
        links.append({
            'name': name,
            'path': path_str,
            'relation': relation,
            'type': ext
        })

    try:
        for item in os.listdir(file_dir):
            item_path = os.path.join(file_dir, item)
            if os.path.isfile(item_path):
                f_base, f_ext = os.path.splitext(item)
                if f_base == base_name and f_ext.lower() != '.py':
                    add_link(item, os.path.abspath(item_path), 'same-name')
    except Exception:
        pass

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception:
        content = ""

    if content:
        strings = re.findall(r"(['\"`])(.*?)\1", content)
        for _, val in strings:
            val = val.strip()
            if re.search(r"\.[a-zA-Z0-9]{2,5}$", val) and not re.match(r"^[0-9\.]+$", val):
                resolved = resolve_path(file_path, val)
                if resolved:
                    add_link(os.path.basename(resolved), resolved, 'reference')

    dedup = {}
    for link in links:
        p = link['path']
        if p not in dedup:
            dedup[p] = link

    return {
        'activeFile': {
            'name': os.path.basename(file_path),
            'path': os.path.abspath(file_path)
        },
        'links': list(dedup.values())
    }

def resolve_path(current_file, path_str):
    cur_dir = os.path.dirname(current_file)
    rel_path = os.path.abspath(os.path.join(cur_dir, path_str))
    if os.path.exists(rel_path) and os.path.isfile(rel_path):
        return rel_path
    cwd_path = os.path.abspath(os.path.join(os.getcwd(), path_str))
    if os.path.exists(cwd_path) and os.path.isfile(cwd_path):
        return cwd_path
    return None

def visualize(file_path=None):
    target_file = file_path
    if not target_file:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        for frame_info in inspect.stack():
            filename = frame_info.filename
            if filename and os.path.isabs(filename):
                file_dir = os.path.dirname(os.path.abspath(filename))
                if file_dir != current_dir and "importlib" not in filename and "<" not in filename:
                    target_file = os.path.abspath(filename)
                    break

    if not target_file or not os.path.exists(target_file):
        print("[FileConnect] Error: Could not determine python target script.", file=sys.stderr)
        return

    data = scan_file(target_file)
    if not data:
        return

    data_json = json.dumps(data)
    html_content = HTML_TEMPLATE.replace('{active_name}', data['activeFile']['name']).replace('{graph_data_json}', data_json)

    try:
        target_dir = os.path.dirname(os.path.abspath(target_file))
        temp_dir = os.path.join(target_dir, '.fc_temp')
        os.makedirs(temp_dir, exist_ok=True)
        safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', data['activeFile']['name'])
        temp_path = os.path.join(temp_dir, f"{safe_name}_fc_graph.html")
        
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        webbrowser.open('file://' + os.path.abspath(temp_path))
    except Exception as e:
        print(f"[FileConnect] Error generating visualizer: {e}", file=sys.stderr)

def link(filepath):
    """Programmatically compile and link any file type, returning its loaded Python module namespace."""
    resolved = None
    
    # 1. Resolve absolute or relative to CWD
    if os.path.exists(filepath) and os.path.isfile(filepath):
        resolved = os.path.abspath(filepath)
    else:
        # 2. Check relative to calling script
        caller_file = None
        current_dir = os.path.dirname(os.path.abspath(__file__))
        for frame_info in inspect.stack():
            filename = frame_info.filename
            if filename and os.path.isabs(filename):
                file_dir = os.path.dirname(os.path.abspath(filename))
                if file_dir != current_dir and "importlib" not in filename and "<" not in filename:
                    caller_file = os.path.abspath(filename)
                    break
        
        if caller_file:
            caller_dir = os.path.dirname(os.path.abspath(caller_file))
            rel_path = os.path.abspath(os.path.join(caller_dir, filepath))
            if os.path.exists(rel_path) and os.path.isfile(rel_path):
                resolved = rel_path

    if not resolved:
        # 3. Fallback to global path resolving
        cwd = os.getcwd()
        resolved = resolve_path(os.path.abspath(os.path.join(cwd, 'dummy.py')), filepath)

    if not resolved or not os.path.exists(resolved):
        raise FileNotFoundError(f"FileConnect could not locate file path: {filepath}")

    ext = os.path.splitext(resolved)[1].lower()
    
    base_name = os.path.splitext(os.path.basename(resolved))[0]
    module_name = f"fc_link_{base_name}_{abs(hash(resolved))}"
    
    module = types.ModuleType(module_name)
    loader = FileConnectLoader(resolved, ext)
    loader.exec_module(module)
    
    sys.modules[module_name] = module
    return module

