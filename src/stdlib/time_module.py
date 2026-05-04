"""
time_module.py

Pulse standard library module for time and timing utilities.
Provides functions for getting the current time, measuring elapsed time, and pausing execution.
"""

from __future__ import annotations
from src.values import PulseModule, PulseNumber, PulseString
from src.function import PulseNativeFunction
import time

def make(interp) -> PulseModule:
    """Build and return the Pulse 'time' module."""
    
    def _now() -> PulseNumber:
        """Return the currect UNIX timestamp in seconds since the epoch."""
        return PulseNumber(time.time())
    
    def _clock() -> PulseNumber:
        """Return a high-resolution performance counter for timing code execution."""
        return PulseNumber(time.perf_counter())
    
    def _sleep(seconds) -> None:
        """Pause execution for the given number of seconds."""
        time.sleep(seconds.value)
    
    return PulseModule("time", {
        "now": PulseNativeFunction("now", _now),
        "clock": PulseNativeFunction("clock", _clock),
        "sleep": PulseNativeFunction("sleep", _sleep),
    })