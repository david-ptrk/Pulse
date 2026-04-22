from src.values import PulseModule, PulseString, PulseNull
from src.function import PulseNativeFunction

def make(interp) -> PulseModule:
    def _print(*args):
        print(" ".join(repr(a) for a in args))
        return PulseNull()
    
    def _input(prompt=None):
        p = prompt.value if prompt else ""
        return PulseString(input(p))
    
    return PulseModule("io", {
        "print": PulseNativeFunction("print", _print),
        "input": PulseNativeFunction("input", _input),
    })