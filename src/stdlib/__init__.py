"""
stdlib/__init__.py

Registry of Pulse built-in standard library modules.
Each entry is a factor: (interpreter) -> PulseModule
"""

from src.stdlib import math_module, io_module

STDLIB_MODULES = {
    "math": math_module.make,
    "io": io_module.make,
}