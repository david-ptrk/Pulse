"""
os_module.py
"""

from __future__ import annotations
import os
import shutil
from src.values import PulseModule, PulseString, PulseNull, PulseBoolean, PulseList, PulseNumber, PulseDict
from src.function import PulseNativeFunction

def make(interp) -> PulseModule:
    def _check_str(val, name: str) -> str:
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
        pass