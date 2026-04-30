# native.py
import ctypes
import os
import sys

_lib_name = "pulse_loader.dll" if sys.platform == "win32" else "pulse_loader.so"
_lib_path = os.path.join(os.path.dirname(__file__), "..", "bin", _lib_name)

try:
    _lib = ctypes.CDLL(os.path.abspath(_lib_path))
except OSError as e:
    raise RuntimeError(f"[pulse_loader] Failed to load shared library: {e}")

_lib.pulse_find_module.restype = ctypes.c_int
_lib.pulse_find_module.argtypes = [
    ctypes.c_char_p,
    ctypes.POINTER(ctypes.c_char_p),
    ctypes.c_char_p,
    ctypes.c_size_t,
]

_lib.pulse_read_file.restype = ctypes.c_void_p
_lib.pulse_read_file.argtypes = [
    ctypes.c_char_p,
    ctypes.POINTER(ctypes.c_size_t),
]

_lib.pulse_free_buffer.restype = None
_lib.pulse_free_buffer.argtypes = [ctypes.c_void_p]


def find_module(name: str, search_dirs: list[str]) -> str | None:
    dirs_enc = [d.encode() for d in search_dirs] + [None]
    dirs_arr = (ctypes.c_char_p * len(dirs_enc))(*dirs_enc)
    
    out_path = ctypes.create_string_buffer(1024)
    found = _lib.pulse_find_module(name.encode(), dirs_arr, out_path, ctypes.c_size_t(1024))
    return out_path.value.decode() if found else None

def read_file(path: str) -> str | None:
    out_len = ctypes.c_size_t(0)
    raw = _lib.pulse_read_file(path.encode(), ctypes.byref(out_len))
    if not raw:
        return None
    
    try:
        buf = (ctypes.c_char * out_len.value).from_address(raw)
        result = bytes(buf).decode("utf-8")
    finally:
        _lib.pulse_free_buffer(ctypes.c_void_p(raw))
    
    return result