# io_module.py
from __future__ import annotations
from src.values import PulseModule, PulseString, PulseNull, PulseBoolean, PulseList
from src.function import PulseNativeFunction
import os

def make(interp) -> PulseModule:
    def _read_file(path: PulseString) -> PulseString:
        if not isinstance(path, PulseString):
            interp._raise(f"read_file() argument must be a string, got {path.type_name()}")
        try:
            with open(path.value, "r", encoding="utf-8") as f:
                return PulseString(f.read())
        except FileNotFoundError:
            interp._raise(f"File not found: '{path.value}'")
        except OSError as e:
            interp._raise(f"Could not read file '{path.value}': {e}")
    
    def _write_file(path: PulseString, content: PulseString) -> PulseNull:
        if not isinstance(path, PulseString):
            interp._raise(f"write_file() path must be a string, got {path.type_name()}")
        if not isinstance(content, PulseString):
            interp._raise(f"write_file() content must be a string, got {content.type_name()}")
        try:
            with open(path.value, "w", encoding="utf-8") as f:
                f.write(content.value)
            return PulseNull()
        except OSError as e:
            interp._raise(f"Could not write file '{path.value}': {e}")
    
    def _append_file(path: PulseString, content: PulseString) -> PulseNull:
        if not isinstance(path, PulseString):
            interp._raise(f"append_file() path must be a string, got {path.type_name()}")
        if not isinstance(content, PulseString):
            interp._raise(f"append_file() content must be a string, got {content.type_name()}")
        try:
            with open(path.value, "a", encoding="utf-8") as f:
                f.write(content.value)
            return PulseNull()
        except OSError as e:
            interp._raise(f"Could not append to file '{path.value}': {e}")
    
    def _file_exists(path: PulseString) -> PulseBoolean:
        if not isinstance(path, PulseString):
            interp._raise(f"file_exists() argument must be a string, got {path.type_name()}")
        return PulseBoolean(os.path.isfile(path.value))
    
    def _read_lines(path: PulseString) -> PulseList:
        if not isinstance(path, PulseString):
            interp._raise(f"read_lines() argument must be a string, got {path.type_name()}")
        try:
            with open(path.value, "r", encoding="utf-8") as f:
                return PulseList([PulseString(line.rstrip("\n")) for line in f])
        except FileNotFoundError:
            interp._raise(f"File not found: '{path.value}'")
        except OSError as e:
            interp._raise(f"Could not read file '{path.value}': {e}")
    
    return PulseModule("io", {
        "read_file":   PulseNativeFunction("read_file",   _read_file),
        "write_file":  PulseNativeFunction("write_file",  _write_file),
        "append_file": PulseNativeFunction("append_file", _append_file),
        "file_exists": PulseNativeFunction("file_exists", _file_exists),
        "read_lines":  PulseNativeFunction("read_lines",  _read_lines),
    })