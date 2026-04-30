# time_module.py
from __future__ import annotations
from src.values import PulseModule, PulseNumber, PulseString
from src.function import PulseNativeFunction
import time

def make(interp) -> PulseModule:
    def _now() -> PulseNumber:
        return PulseNumber(time.time())
    
    def _clock() -> PulseNumber:
        return PulseNumber(time.perf_counter())
    
    def _sleep(seconds) -> None:
        time.sleep(seconds.value)
    
    return PulseModule("time", {
        "now": PulseNativeFunction("now", _now),
        "clock": PulseNativeFunction("clock", _clock),
        "sleep": PulseNativeFunction("sleep", _sleep),
    })