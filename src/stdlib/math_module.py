import math
from src.values import PulseModule, PulseNumber
from src.function import PulseNativeFunction
from typing import Any

_PI = PulseNumber(math.pi)
_E = PulseNumber(math.e)
_INF = PulseNumber(math.inf)
_TAU = PulseNumber(math.tau)

_cached_module: PulseModule | None = None

def make(interp) -> PulseModule:
    global _cached_module
    if _cached_module is not None:
        return _cached_module
    
    _PN = PulseNumber
    _raise = interp._raise
    
    def _check(name: str, x: Any) -> float:
        if not isinstance(x, _PN):
            _raise(f"{name}() argument must be a number, got {x.type_name()}")
        return x.value
    
    def _sqrt(x: Any) -> PulseNumber:
        v = _check("sqrt", x)
        if v < 0:
            _raise("sqrt() argument must be non-negative")
        return _PN(math.sqrt(v))
    
    def _floor(x: Any) -> PulseNumber:
        return _PN(math.floor(_check("floor", x)))
    
    def _ceil(x: Any) -> PulseNumber:
        return _PN(math.ceil(_check("ceil", x)))
    
    def _log(x: Any, base: Any = None) -> PulseNumber:
        v = _check("log", x)
        if base is None:
            return _PN(math.log(v))
        if not isinstance(base, _PN):
            _raise(f"log() base must be a number, got {base.type_name()}")
        return _PN(math.log(v, base.value))
    
    def _sin(x: Any) -> PulseNumber:
        return _PN(math.sin(_check("sin", x)))
    
    def _cos(x: Any) -> PulseNumber:
        return _PN(math.cos(_check("cos", x)))
    
    def _tan(x: Any) -> PulseNumber:
        return _PN(math.tan(_check("tan", x)))
    
    def _log2(x: Any) -> PulseNumber:
        return _PN(math.log2(_check("log2", x)))
    
    def _log10(x: Any) -> PulseNumber:
        return _PN(math.log10(_check("log10", x)))
    
    def _exp(x: Any) -> PulseNumber:
        return _PN(math.exp(_check("exp", x)))
    
    _cached_module = PulseModule("math", {
        "sqrt":  PulseNativeFunction("sqrt",  _sqrt),
        "floor": PulseNativeFunction("floor", _floor),
        "ceil":  PulseNativeFunction("ceil",  _ceil),
        "log":   PulseNativeFunction("log",   _log),
        "log2":  PulseNativeFunction("log2",  _log2),
        "log10": PulseNativeFunction("log10", _log10),
        "exp":   PulseNativeFunction("exp",   _exp),
        "sin":   PulseNativeFunction("sin",   _sin),
        "cos":   PulseNativeFunction("cos",   _cos),
        "tan":   PulseNativeFunction("tan",   _tan),
        "pi":    _PI,
        "e":     _E,
        "inf":   _INF,
        "tau":   _TAU,
    })
    return _cached_module