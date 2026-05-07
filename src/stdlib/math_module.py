"""
math_module.py

Pulse standard library module for mathematical operations.
Functions are backed by C via native bindings for performance.
Constants are cached at import time.
"""

import math
from src.values import PulseModule, PulseNumber
from src.function import BuiltinFunction
from typing import Any
from src.native import make_c_math_functions

_PI = PulseNumber(math.pi)
_E = PulseNumber(math.e)
_INF = PulseNumber(math.inf)
_TAU = PulseNumber(math.tau)

_cached_module: PulseModule | None = None

def make(interp) -> PulseModule:
    """Built and return the Pulse 'math' module. Result is cached after first call."""
    
    global _cached_module
    if _cached_module is not None:
        return _cached_module
    
    _PN = PulseNumber
    _raise = interp._raise
    
    c_fns = make_c_math_functions(_raise)
    
    def _wrap(name: str):
        """Wrap a single-argument C math function with Pulse type checking."""
        c_fn = c_fns[name]
        def call(x):
            if not isinstance(x, _PN):
                _raise(f"{name}() argument must be a number, got {x.type_name()}")
            return _PN(c_fn(x.value))   # unwrap → C → rewrap
        return call
    
    def _log(x, base=None):
        """Return log(x) or log(x, base). Base defaults to e."""
        if not isinstance(x, _PN):
            _raise(f"log() argument must be a number, got {x.type_name()}")
        if base is not None and not isinstance(base, _PN):
            _raise(f"log() base must be a number, got {base.type_name()}")
        return _PN(c_fns["log"](x.value, base.value if base else None))
    
    def _pow(b, e):
        """Return b raised to the power e."""
        if not isinstance(b, _PN):
            _raise(f"pow() base must be a number, got {b.type_name()}")
        if not isinstance(e, _PN):
            _raise(f"pow() exponent must be a number, got {e.type_name()}")
        return _PN(c_fns["pow"](b.value, e.value))
    
    _cached_module = PulseModule("math", {
        "sqrt":  BuiltinFunction("sqrt",  _wrap("sqrt")),
        "floor": BuiltinFunction("floor", _wrap("floor")),
        "ceil":  BuiltinFunction("ceil",  _wrap("ceil")),
        "log":   BuiltinFunction("log",   _log),
        "log2":  BuiltinFunction("log2",  _wrap("log2")),
        "log10": BuiltinFunction("log10", _wrap("log10")),
        "exp":   BuiltinFunction("exp",   _wrap("exp")),
        "sin":   BuiltinFunction("sin",   _wrap("sin")),
        "cos":   BuiltinFunction("cos",   _wrap("cos")),
        "tan":   BuiltinFunction("tan",   _wrap("tan")),
        "abs":   BuiltinFunction("abs",   _wrap("abs")),
        "pow":   BuiltinFunction("pow",   _pow),
        "pi":    _PI,
        "e":     _E,
        "inf":   _INF,
        "tau":   _TAU,
    })
    return _cached_module