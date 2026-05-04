"""
os_module.py

Pulse standard library module for operating system interactions.
Provides functions for directory management, file operations, path manipulation,
environment variables, and basic system information.
"""

from __future__ import annotations
import os
import shutil
from src.values import PulseModule, PulseString, PulseNull, PulseBoolean, PulseList, PulseNumber, PulseDict
from src.function import PulseNativeFunction
import sys

def make(interp) -> PulseModule:
    """Build and return the Pulse 'os' module."""
    
    def _check_str(val, name: str) -> str:
        """Raise if val is not a PulseString, then return its raw Python string value."""
        if not isinstance(val, PulseString):
            interp._raise(f"{name} must be a string, got '{val.type_name()}'")
        return val.value
    
    # Current Directory
    def _getcwd() -> PulseString:
        """Return the current working directory."""
        return PulseString(os.getcwd())
    
    def _chdir(path) -> PulseNull:
        """Change the current working directory."""
        p = _check_str(path, "chdir() 'path'")
        try:
            os.chdir(p)
        except FileNotFoundError:
            interp._raise(f"chdir() directory not found: '{p}'")
        except OSError as e:
            interp._raise(f"chdir() failed: {e}")
        return PulseNull()
    
    # Directory Operations
    def _listdir(path=None) -> PulseList:
        """List contents of a directory. Defaults to current directory."""
        p = _check_str(path, "listdir() 'path'") if path is not None else "."
        try:
            entries = os.listdir(p)
            return PulseList([PulseString(e) for e in sorted(entries)])
        except FileNotFoundError:
            interp._raise(f"listdir() directory not found: '{p}'")
        except OSError as e:
            interp._raise(f"listdir() failed: {e}")
    
    def _mkdir(path, exist_ok=None) -> PulseNull:
        """Create a directory."""
        p = _check_str(path, "mkdir() 'path'")
        ok = exist_ok.value if exist_ok is not None and isinstance(exist_ok, PulseBoolean) else False
        try:
            os.mkdir(p)
        except FileNotFoundError:
            if not ok:
                interp._raise(f"mkdir() directory already exists: '{p}'")
        except OSError as e:
            interp._raise(f"mkdir() failed: {e}")
        return PulseNull()
    
    def _makedirs(path, exist_ok=None) -> PulseNull:
        """Create a directory and all intermediate directories."""
        p = _check_str(path, "makedirs() 'path'")
        ok = exist_ok.value if exist_ok is not None and isinstance(exist_ok, PulseBoolean) else False
        try:
            os.makedirs(p, exist_ok=ok)
        except FileNotFoundError:
            if not ok:
                interp._raise(f"makedirs() directory already exists: '{p}'")
        except OSError as e:
            interp._raise(f"makedirs() failed: {e}")
        return PulseNull()
    
    def _rmdir(path) -> PulseNull:
        """Remove an empty directory."""
        p = _check_str(path, "rmdir() 'path'")
        try:
            os.rmdir(p)
        except FileNotFoundError:
            interp._raise(f"rmdir() directory not found: '{p}'")
        except OSError as e:
            interp._raise(f"rmdir() failed: {e}")
        return PulseNull()
    
    def _removedirs(path) -> PulseNull:
        """Remove directory and all empty parents."""
        p = _check_str(path, "removedirs() 'path'")
        try:
            os.removedirs(p)
        except FileNotFoundError:
            interp._raise(f"removedirs() directory not found: '{p}'")
        except OSError as e:
            interp._raise(f"removedirs() failed: {e}")
        return PulseNull()
    
    def _rmtree(path) -> PulseNull:
        """Remove a directory and all its contents recursively."""
        p = _check_str(path, "rmtree() 'path'")
        try:
            shutil.rmtree(p)
        except FileNotFoundError:
            interp._raise(f"removedirs() failed: {e}")
        except OSError as e:
            interp._raise(f"rmtree() failed: {e}")
        return PulseNull()
    
    # File Operations
    def _remove(path) -> PulseNull:
        """Delete a file."""
        p = _check_str(path, "remove() 'path'")
        try:
            os.remove(p)
        except FileNotFoundError:
            interp._raise(f"remove() file not found: '{p}'")
        except OSError as e:
            interp._raise(f"remove() failed: {e}")
        return PulseNull()
    
    def _rename(src, dst) -> PulseNull:
        """Rename or move a file or directory."""
        s = _check_str(src, "rename() 'src'")
        d = _check_str(dst, "rename() 'dst'")
        try:
            os.rename(s, d)
        except FileNotFoundError:
            interp._raise(f"rename() source not found: '{s}'")
        except OSError as e:
            interp._raise(f"rename() failed: {e}")
        return PulseNull()
    
    def _copy(src, dst) -> PulseNull:
        """Copy a file to a destination."""
        s = _check_str(src, "copy() 'src'")
        d = _check_str(dst, "copy() 'dst'")
        try:
            shutil.copy2(s, d)
        except FileNotFoundError:
            interp._raise(f"copy() source not found: '{s}'")
        except OSError as e:
            interp._raise(f"copy() failed: {e}")
        return PulseNull()
    
    # Path Checks
    def _exists(path) -> PulseBoolean:
        """Return True if path exists (file or directory)."""
        p = _check_str(path, "exists() 'path'")
        return PulseBoolean(os.path.exists(p))
    
    def _is_file(path) -> PulseBoolean:
        """Return True if path is a file."""
        p = _check_str(path, "is_file() 'path'")
        return PulseBoolean(os.path.isfile(p))
    
    def _is_dir(path) -> PulseBoolean:
        """Return True if path is a directory."""
        p = _check_str(path, "is_dir() 'path'")
        return PulseBoolean(os.path.isdir(p))
    
    def _is_abs(path) -> PulseBoolean:
        """Return True if path is absolute."""
        p = _check_str(path, "is_abs() 'path'")
        return PulseBoolean(os.path.isabs(p))
    
    # Path Manipulation
    def _join(*parts) -> PulseString:
        """Join path components."""
        str_paths = [_check_str(p, "join() argument") for p in parts]
        return PulseString(os.path.join(*str_paths))
    
    def _basename(path) -> PulseString:
        """Return the base name of a path."""
        p = _check_str(path, "basename() 'path'")
        return PulseString(os.path.basename(p))
    
    def _dirname(path) -> PulseString:
        """Return the directory component of a path."""
        p = _check_str(path, "dirname() 'path'")
        return PulseString(os.path.dirname(p))
    
    def _abspath(path) -> PulseString:
        """Return the absolute path."""
        p = _check_str(path, "abspath() 'path'")
        return PulseString(os.path.abspath(p))
    
    def _splitext(path) -> PulseList:
        """Split path into (root, ext) - returns a list of two strings."""
        p = _check_str(path, "splitext() 'path'")
        root, ext = os.path.splitext(p)
        return PulseList([PulseString(root), PulseString(ext)])
    
    def _split(path) -> PulseList:
        """Split path into (head, tail) - returns a list of two strings."""
        p = _check_str(path, "split() 'path'")
        head, tail = os.path.split(p)
        return PulseList([PulseString(head), PulseString(tail)])
    
    # File Info
    def _getsize(path) -> PulseNumber:
        """Return the size of a file in bytes."""
        p = _check_str(path, "getsize() 'path'")
        try:
            return PulseNumber(os.path.getsize(p))
        except FileNotFoundError:
            interp._raise(f"getsize() file not found: '{p}'")
        except OSError as e:
            interp._raise(f"getsize() failed: {e}")
    
    def _stat(path) -> PulseDict:
        """Return file start info as a dict."""
        p = _check_str(path, "stat() 'path'")
        try:
            s = os.stat(p)
            return PulseDict({
                PulseString("size"):  PulseNumber(s.st_size),
                PulseString("mtime"): PulseNumber(s.st_mtime),
                PulseString("ctime"): PulseNumber(s.st_ctime),
                PulseString("mode"):  PulseNumber(s.st_mode),
            })
        except FileNotFoundError:
            interp._raise(f"stat() path not found: '{p}'")
        except OSError as e:
            interp._raise(f"stat() failed: {e}")
    
    # Environment Variables
    def _getenv(key, default=None) -> PulseString | PulseNull:
        """Get an environment variable."""
        k = _check_str(key, "getenv() 'key'")
        val = os.environ.get(k)
        if val is None:
            return default if default is not None else PulseNull()
        return PulseString(val)
    
    def _setenv(key, value) -> PulseNull:
        """Set an environment variable."""
        k = _check_str(key, "setenv() 'key'")
        v = _check_str(value, "setenv() 'value'")
        os.environ[k] = v
        return PulseNull()
    
    def _env_vars() -> PulseDict:
        """Return all environment variables as a dict."""
        return PulseDict({
            PulseString(k): PulseString(v)
            for k, v in os.environ.items()
        })
    
    # System Info
    def _platform() -> PulseString:
        """Return th OS platform string."""
        return PulseString(sys.platform)
    
    def _sep() -> PulseString:
        """Return the OS path separator."""
        return PulseString(os.sep)
    
    
    return PulseModule("os", {
        "getcwd": PulseNativeFunction("getcwd", _getcwd),
        "chdir": PulseNativeFunction("chdir", _chdir),
        "listdir": PulseNativeFunction("listdir", _listdir),
        "mkdir": PulseNativeFunction("mkdir", _mkdir),
        "makedirs": PulseNativeFunction("makedirs", _makedirs),
        "rmdir": PulseNativeFunction("rmdir", _rmdir),
        "removedirs": PulseNativeFunction("removedirs", _removedirs),
        "rmtree": PulseNativeFunction("rmtree", _rmtree),
        "remove": PulseNativeFunction("remove", _remove),
        "rename": PulseNativeFunction("rename", _rename),
        "copy": PulseNativeFunction("copy", _copy),
        "exists": PulseNativeFunction("exists", _exists),
        "is_file": PulseNativeFunction("is_file", _is_file),
        "is_dir": PulseNativeFunction("is_dir", _is_dir),
        "is_abs": PulseNativeFunction("is_abs", _is_abs),
        "join": PulseNativeFunction("join", _join),
        "basename": PulseNativeFunction("basename", _basename),
        "dirname": PulseNativeFunction("dirname", _dirname),
        "abspath": PulseNativeFunction("abspath", _abspath),
        "splitext": PulseNativeFunction("splitext", _splitext),
        "split": PulseNativeFunction("split", _split),
        "getsize": PulseNativeFunction("getsize", _getsize),
        "stat": PulseNativeFunction("stat", _stat),
        "getenv": PulseNativeFunction("getenv", _getenv),
        "setenv": PulseNativeFunction("setenv", _setenv),
        "env_vars": PulseNativeFunction("env_vars", _env_vars),
        "platform": PulseNativeFunction("platform", _platform),
        "sep": PulseNativeFunction("sep", _sep),
    })