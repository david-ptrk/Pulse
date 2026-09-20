"""
stdlib/__init__.py

Registry of Pulse built-in standard library modules.
Each entry is a factor: (interpreter) -> PulseModule
"""

from importlib import import_module

def _module_factory(module_name: str):
    def make(interpreter):
        module = import_module(f"src.stdlib.{module_name}")
        return module.make(interpreter)
    return make

STDLIB_MODULES = {
    "math": _module_factory("math_module"),
    "io": _module_factory("io_module"),
    "models": _module_factory("model_module"),
    "preprocess": _module_factory("preprocess_module"),
    "time": _module_factory("time_module"),
    "random": _module_factory("random_module"),
    "os": _module_factory("os_module"),
    "learn": _module_factory("learn_module"),
    "metrics": _module_factory("metrics_module"),
    "datasets": _module_factory("datasets_module"),
    "pybridge": _module_factory("pybridge_module"),
}