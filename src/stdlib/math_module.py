import math
from src.values import PulseModule, PulseNumber
from src.function import PulseNativeFunction
from typing import Any

def make(interp) -> PulseModule:
    def _sqrt(x: Any) -> PulseNumber:
        if not isinstance(x, PulseNumber):
            interp._raise(f"sqrt() argument must be a number, got {x.type_name()}")
        if x.value < 0:
            interp._raise("sqrt() argument must be non-negative")
        return PulseNumber(math.sqrt(x.value))
    
    def _floor(x: Any) -> PulseNumber:
        if not isinstance(x, PulseNumber):
            interp._raise(f"floor() argument must be a number, got {x.type_name()}")
        return PulseNumber(math.floor(x.value))
    
    def _ceil(x: Any) -> PulseNumber:
        if not isinstance(x, PulseNumber):
            interp._raise(f"ceil() argument must be a number, got {x.type_name()}")
        return PulseNumber(math.ceil(x.value))
    
    def _log(x: Any, base: Any = None) -> PulseNumber:
        if not isinstance(x, PulseNumber):
            interp._raise(f"log() argument must be a number, got {x.type_name()}")
        if base is None:
            return PulseNumber(math.log(x.value))
        if not isinstance(base, PulseNumber):
            interp._raise(f"log() base must be a number, got {base.type_name()}")
        return PulseNumber(math.log(x.value, base.value))
    
    def _sin(x: Any) -> PulseNumber:
        if not isinstance(x, PulseNumber):
            interp._raise(f"sin() argument must be a number, got {x.type_name()}")
        return PulseNumber(math.sin(x.value))
    
    def _cos(x: Any) -> PulseNumber:
        if not isinstance(x, PulseNumber):
            interp._raise(f"cos() argument must be a number, got {x.type_name()}")
        return PulseNumber(math.cos(x.value))
    
    def _tan(x: Any) -> PulseNumber:
        if not isinstance(x, PulseNumber):
            interp._raise(f"tan() argument must be a number, got {x.type_name()}")
        return PulseNumber(math.tan(x.value))
    
    def _log2(x: Any) -> PulseNumber:
        if not isinstance(x, PulseNumber):
            interp._raise(f"log2() argument must be a number, got {x.type_name()}")
        return PulseNumber(math.log2(x.value))
    
    def _log10(x: Any) -> PulseNumber:
        if not isinstance(x, PulseNumber):
            interp._raise(f"log10() argument must be a number, got {x.type_name()}")
        return PulseNumber(math.log10(x.value))
    
    def _exp(x: Any) -> PulseNumber:
        if not isinstance(x, PulseNumber):
            interp._raise(f"exp() argument must be a number, got {x.type_name()}")
        return PulseNumber(math.exp(x.value))
    
    return PulseModule("math", {
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
        "pi":    PulseNumber(math.pi),
        "e":     PulseNumber(math.e),
        "inf":   PulseNumber(math.inf),
        "tau":   PulseNumber(math.tau),
    })