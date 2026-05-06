"""
stdlib/__init__.py

Registry of Pulse built-in standard library modules.
Each entry is a factor: (interpreter) -> PulseModule
"""

from src.stdlib import (
    math_module, io_module, model_module, preprocess_module, time_module, random_module,
    os_module, learn_module, metrics_module,
)

STDLIB_MODULES = {
    "math": math_module.make,
    "io": io_module.make,
    "models": model_module.make,
    "preprocess": preprocess_module.make,
    "time": time_module.make,
    "random": random_module.make,
    "os": os_module.make,
    "learn": learn_module.make,
    "metrics": metrics_module.make,
}