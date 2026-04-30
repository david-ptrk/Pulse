"""
src/native.py
Unified ctypes bindings for all Pulse native (C) extensions
"""

import ctypes
import os
import sys
import math

# Helpers
def _load_lib(name: str) -> ctypes.CDLL:
    lib_name = f"{name}.dll" if sys.platform == "win32" else f"{name}.so"
    lib_path = os.path.join(os.path.dirname(__file__), "..", "bin", lib_name)
    try:
        return ctypes.CDLL(os.path.abspath(lib_path))
    except OSError as e:
        raise RuntimeError(f"[native] Failed to load {lib_name}: {e}")

# Libraries
_loader = _load_lib("pulse_loader")
_math = _load_lib("pulse_math")

# pulse_loader bindings
_loader.pulse_find_module.restype = ctypes.c_int
_loader.pulse_find_module.argtypes = [
    ctypes.c_char_p,
    ctypes.POINTER(ctypes.c_char_p),
    ctypes.c_char_p,
    ctypes.c_size_t,
]

_loader.pulse_read_file.restype = ctypes.c_void_p
_loader.pulse_read_file.argtypes = [
    ctypes.c_char_p,
    ctypes.POINTER(ctypes.c_size_t),
]

_loader.pulse_free_buffer.restype = None
_loader.pulse_free_buffer.argtypes = [ctypes.c_void_p]

# pulse_math bindings
_math.pulse_math_last_error.restype = ctypes.c_char_p
_math.pulse_math_last_error.argtypes = []

for _fn in ("pulse_sqrt", "pulse_floor", "pulse_ceil",
            "pulse_log2", "pulse_log10", "pulse_exp",
            "pulse_sin",  "pulse_cos",   "pulse_tan",
            "pulse_abs"):
    _f = getattr(_math, _fn)
    _f.restype = ctypes.c_double
    _f.argtypes = [ctypes.c_double]

_math.pulse_log.restype = ctypes.c_double
_math.pulse_log.argtypes = [ctypes.c_double, ctypes.c_int, ctypes.c_double]

_math.pulse_pow.restype = ctypes.c_double
_math.pulse_pow.argtypes = [ctypes.c_double, ctypes.c_double]

# Loader API
def find_module(name: str, search_dirs: list[str]) -> str | None:
    dirs_enc = [d.encode() for d in search_dirs] + [None]
    dirs_arr = (ctypes.c_char_p * len(dirs_enc))(*dirs_enc)
    
    out_path = ctypes.create_string_buffer(1024)
    found = _loader.pulse_find_module(name.encode(), dirs_arr, out_path, ctypes.c_size_t(1024))
    return out_path.value.decode() if found else None

def read_file(path: str) -> str | None:
    out_len = ctypes.c_size_t(0)
    raw = _loader.pulse_read_file(path.encode(), ctypes.byref(out_len))
    if not raw:
        return None
    
    try:
        buf = (ctypes.c_char * out_len.value).from_address(raw)
        result = bytes(buf).decode("utf-8")
    finally:
        _loader.pulse_free_buffer(ctypes.c_void_p(raw))
    
    return result

# Math API
def _check_math_error(interp_raise) -> None:
    err = _math.pulse_math_last_error()
    if err:
        interp_raise(err.decode())

def make_c_math_functions(interp_raise: callable) -> dict:
    def _wrap1(c_fn):
        def call(x: float) -> float:
            result = c_fn(x)
            _check_math_error(interp_raise)
            return result
        return call
    
    def _log(x: float, base: float | None = None) -> float:
        result = _math.pulse_log(x, 1 if base is not None else 0, base or 0.0)
        _check_math_error(interp_raise)
        return result
    
    def _pow(b: float, e: float) -> float:
        result = _math.pulse_pow(b, e)
        _check_math_error(interp_raise)
        return result
    
    return {
        "sqrt": _wrap1(_math.pulse_sqrt),
        "floor": _wrap1(_math.pulse_floor),
        "ceil": _wrap1(_math.pulse_ceil),
        "log2": _wrap1(_math.pulse_log2),
        "log10": _wrap1(_math.pulse_log10),
        "exp": _wrap1(_math.pulse_exp),
        "sin": _wrap1(_math.pulse_sin),
        "cos": _wrap1(_math.pulse_cos),
        "tan": _wrap1(_math.pulse_tan),
        "abs": _wrap1(_math.pulse_abs),
        "log": _log,
        "pow": _pow,
    }