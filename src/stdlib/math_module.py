import math
from src.values import PulseModule, PulseNumber, PulseNull
from src.function import PulseNativeFunction

def make(interp) -> PulseModule:
    def _sqrt(x):
        return PulseNumber(math.sqrt(x.value))
    
    def _floor(x):
        return PulseNumber(math.floor(x.value))
    
    def _ceil(x):
        return PulseNumber(math.ceil(x.value))
    
    def _abs(x):
        return PulseNumber(abs(x.value))
    
    def _pow(base, exp):
        return PulseNumber(math.pow(base.value, exp.value))
    
    def _log(x, base=None):
        if base is None:
            return PulseNumber(math.log(x.value))
        return PulseNumber(math.log(x.value, base.value))
    
    def _sin(x):
        return PulseNumber(math.sin(x.value))
    
    def _cos(x):
        return PulseNumber(math.cos(x.value))
    
    def _tan(x):
        return PulseNumber(math.tan(x.value))
    
    return PulseModule("math", {
        "sqrt":  PulseNativeFunction("sqrt",  _sqrt),
        "floor": PulseNativeFunction("floor", _floor),
        "ceil":  PulseNativeFunction("ceil",  _ceil),
        "abs":   PulseNativeFunction("abs",   _abs),
        "pow":   PulseNativeFunction("pow",   _pow),
        "log":   PulseNativeFunction("log",   _log),
        "sin":   PulseNativeFunction("sin",   _sin),
        "cos":   PulseNativeFunction("cos",   _cos),
        "tan":   PulseNativeFunction("tan",   _tan),
        "pi":    PulseNumber(math.pi),
        "e":     PulseNumber(math.e),
        "inf":   PulseNumber(math.inf),
    })