"""
pybridge_module.py

Pulse standard library module providing integration with Python backend
functions for advanced computations that aren't (yet) implemented natively
in Pulse -- e.g. numpy/scipy routines, or a user's own Python helper code.

Two entry points:
    pybridge.import_module(name)  - import an installed Python module
                                    (e.g. "statistics", "numpy") and expose
                                    its public functions/values to Pulse.
    pybridge.load_file(path)      - execute a user-supplied .py file and
                                    expose its top-level functions/values
                                    to Pulse, the same way import works for
                                    .pul files elsewhere in the language.
"""

from __future__ import annotations
import importlib
import types
from src.values import (
    PulseValue, PulseModule, PulseNumber, PulseString, PulseBoolean, PulseNull, PulseList,
    PulseDict, PulseTensor,
)
from src.function import PulseNativeFunction

try:
    import numpy as np
except ImportError:
    np = None

def _to_python(interp, value: PulseValue):
    """Convert a Pulse value into the equivalent native Python value."""
    if isinstance(value, PulseNull):
        return None
    if isinstance(value, PulseBoolean):
        return value.value
    if isinstance(value, PulseNumber):
        return value.value
    if isinstance(value, PulseString):
        return value.value
    if isinstance(value, PulseList):
        return [_to_python(interp, e) for e in value.elements]
    if isinstance(value, PulseDict):
        return {_to_python(interp, k): _to_python(interp, v) for k, v in value.entries.items()}
    if isinstance(value, PulseTensor):
        return value.array
    interp._raise(f"Cannot pass a value of type '{value.type_name()}' to a Python function")

def _to_pulse(interp, value) -> PulseValue:
    """Convert a native Python value (typically a Python function's return value) into the corresponding Pulse value."""
    if value is None:
        return PulseNull()
    if isinstance(value, bool):
        return PulseBoolean(value)
    if isinstance(value, (int, float)):
        return PulseNumber(value)
    if isinstance(value, str):
        return PulseString(value)
    if isinstance(value, (list, tuple)):
        return PulseList([_to_pulse(interp, e) for e in value])
    if isinstance(value, dict):
        return PulseDict({_to_pulse(interp, k): _to_pulse(interp, v) for k, v in value.items()})
    if np is not None and isinstance(value, np.ndarray):
        try:
            return PulseTensor(value)
        except TypeError as e:
            interp._raise(str(e))
    if callable(value):
        return _wrap_callable(interp, getattr(value, "__name__", "py_function"), value)
    interp._raise(
        f"Cannot convert Python value of type '{type(value).__name__}' into Pulse "
        f"(supported: None, bool, int, float, str, list, dict, numpy array, callables)"
    )

def _wrap_callable(interp, name: str, py_func) -> PulseNativeFunction:
    """Wrap a raw Python callable so it can be called with normal Pulse call syntax, converting arguments and the return value at the boundary."""
    def bridged(*pulse_args, **pulse_kwargs):
        py_args = [_to_python(interp, a) for a in pulse_args]
        py_kwargs = {k: _to_python(interp, v) for k, v in pulse_kwargs.items()}
        try:
            result = py_func(*py_args, **py_kwargs)
        except Exception as e:
            interp._raise(f"Python function '{name}' raised {type(e).__name__}: {e}")
        return _to_pulse(interp, result)
    return PulseNativeFunction(name, bridged)

def _wrap_namespace(interp, name: str, namespace: dict) -> PulseModule:
    """Wrap a dict of Python names -> values (a module's __dict__, or the globals produced by exec()'ing a .py file) into a PulseModule."""
    members = {}
    for key, val in namespace.items():
        if key.startswith("_"):
            continue
        if isinstance(val, type):
            continue # skip classes for now; only plain functions/values are bridged
        if isinstance(val, types.ModuleType):
            continue # skip re-exported submodules
        if callable(val):
            members[key] = _wrap_callable(interp, key, val)
        else:
            try:
                members[key] = _to_pulse(interp, val)
            except Exception:
                continue  # skip module-level values we can't represent in Pulse
    return PulseModule(name, members)

def make(interp) -> PulseModule:
    """Build and return the Pulse 'pybridge' module."""
    
    def _import_module(name: PulseString) -> PulseModule:
        """Import an installed Python module by name and expose its public functions/values to Pulse. Example: pybridge.import_module("statistics")"""
        if not isinstance(name, PulseString):
            interp._raise(f"import_module() argument must be a string, got {name.type_name()}")
        try:
            py_module = importlib.import_module(name.value)
        except ImportError as e:
            interp._raise(f"Could not import Python module '{name.value}': {e}")
        return _wrap_namespace(interp, name.value, vars(py_module))
    
    def _load_file(path: PulseString) -> PulseModule:
        """Execute a user-supplied .py file and expose its top-level functions/values to Pulse. Example: pybridge.load_file("helpers.py")"""
        if not isinstance(path, PulseString):
            interp._raise(f"load_file() argument must be a string, got {path.type_name()}")
        namespace: dict = {"__name__": f"pybridge_module_{abs(hash(path.value))}"}
        try:
            with open(path.value, "r", encoding="utf-8") as f:
                source = f.read()
            exec(compile(source, path.value, "exec"), namespace)
        except FileNotFoundError:
            interp._raise(f"Python file not found: '{path.value}'")
        except Exception as e:
            interp._raise(f"Error executing Python file '{path.value}': {type(e).__name__}: {e}")
        return _wrap_namespace(interp, path.value, namespace)
    
    return PulseModule("pybridge", {
        "import_module": PulseNativeFunction("import_module", _import_module),
        "load_file": PulseNativeFunction("load_file", _load_file),
    })
