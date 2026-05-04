"""
runtime.py

Defines the runtime control-flow mechanisms for the Pulse programming language.

This module provides internal constructs used by the interpreter to manage
non-linear execution flow during program runtime. Unlike syntax or semantic
errors, these constructs are not failures but signals that alter the normal
sequential execution of statements.

The runtime uses specialized exception-based control signals to handle
language features such as loop interruption and function returns. These
signals allow the interpreter to unwind execution contexts safely and
efficiently without relying on complex state flags or manual checks.

These runtime signals are intended strictly for internal interpreter use
and must be handled appropriately within control-flow constructs such as
loops and function execution blocks.
"""

from __future__ import annotations
from typing import Any, Optional, TYPE_CHECKING
from src.error import PulseRuntimeError
if TYPE_CHECKING:
    from src.interpreter import Interpreter

# Control-flow signals
class BreakException(Exception):
    def __init__(self) -> None:
        super().__init__("break")

class ContinueException(Exception):
    def __init__(self) -> None:
        super().__init__("continue")

class ReturnException(Exception):
    def __init__(self, value: Any = None) -> None:
        super().__init__("return")
        self.value = value

# User-visible exception hierarchy
class PulseException(Exception):
    def __init__(self, message: str = "") -> None:
        super().__init__(message)
        self.message = message
    
    def __str__(self) -> str:
        return self.message

class PulseRuntimeException(PulseException):
    def __init__(self, error: PulseRuntimeError) -> None:
        super().__init__(str(error))
        self.error = error
    
    @classmethod
    def from_message(cls, message: str) -> "PulseRuntimeException":
        return cls(PulseRuntimeError(message))
    
    def __str__(self) -> str:
        return str(self.error)

class PulseValueError(PulseRuntimeException):
    def __init__(self, error_or_message: "PulseRuntimeError | str") -> None:
        if isinstance(error_or_message, str):
            error_or_message = PulseRuntimeError(error_or_message)
        super().__init__(error_or_message)

class PulseTypeError(PulseRuntimeException):
    def __init__(self, error_or_message: "PulseRuntimeError | str") -> None:
        if isinstance(error_or_message, str):
            error_or_message = PulseRuntimeError(error_or_message)
        super().__init__(error_or_message)

class PulseIndexError(PulseRuntimeException):
    def __init__(self, error_or_message: "PulseRuntimeError | str") -> None:
        if isinstance(error_or_message, str):
            error_or_message = PulseRuntimeError(error_or_message)
        super().__init__(error_or_message)

class PulseKeyError(PulseRuntimeException):
    def __init__(self, error_or_message: "PulseRuntimeError | str") -> None:
        if isinstance(error_or_message, str):
            error_or_message = PulseRuntimeError(error_or_message)
        super().__init__(error_or_message)

class PulseAttributeError(PulseRuntimeException):
    def __init__(self, error_or_message: "PulseRuntimeError | str") -> None:
        if isinstance(error_or_message, str):
            error_or_message = PulseRuntimeError(error_or_message)
        super().__init__(error_or_message)

class PulseZeroDivisionError(PulseRuntimeException):
    def __init__(self, error_or_message: "PulseRuntimeError | str") -> None:
        if isinstance(error_or_message, str):
            error_or_message = PulseRuntimeError(error_or_message)
        super().__init__(error_or_message)

class PulseNameError(PulseRuntimeException):
    def __init__(self, error_or_message: "PulseRuntimeError | str") -> None:
        if isinstance(error_or_message, str):
            error_or_message = PulseRuntimeError(error_or_message)
        super().__init__(error_or_message)

class PulseNotImplementedError(PulseRuntimeException):
    def __init__(self, error_or_message: "PulseRuntimeError | str") -> None:
        if isinstance(error_or_message, str):
            error_or_message = PulseRuntimeError(error_or_message)
        super().__init__(error_or_message)

# Class system
class PulseClass:
    def __init__(self, name: str, methods: dict, class_vars: dict, bases: Optional[list["PulseClass"]] = None):
        self.name = name
        self.methods = methods
        self.class_vars = class_vars
        self.bases = bases or []
    
    def call(self, interpreter: "Interpreter", arguments: list, kwargs: dict) -> PulseInstance:
        instance = PulseInstance(self)
        
        init = self.find_method("__init__")
        if init is not None:
            init.bind(instance).call(interpreter, arguments, kwargs)
        
        return instance
    
    def find_method(self, name: str) -> Optional[Any]:
        if name in self.methods:
            return self.methods[name]
        
        for base in self.bases:
            method = base.find_method(name)
            if method is not None:
                return method
        
        return None
    
    def get(self, name: str) -> Any:
        if name in self.class_vars:
            return self.class_vars[name]
        
        method = self.find_method(name)
        if method is not None:
            if method.declaration.is_static:
                return method
            return method
        
        raise PulseAttributeError(f"Undefined class member '{name}'")
    
    def type_name(self) -> str:
        return f"class<{self.name}>"
    
    def __repr__(self) -> str:
        return f"<class {self.name}>"

class PulseInstance:
    def __init__(self, klass: PulseClass) -> None:
        self.klass = klass
        self.fields = {}
    
    def get(self, name: str) -> Any:
        if name in self.fields:
            return self.fields[name]
        
        if name in self.klass.class_vars:
            return self.klass.class_vars[name]
        
        method = self.klass.find_method(name)
        if method is not None:
            if method.declaration.is_static:
                return method
            return method.bind(self)
        
        raise PulseAttributeError(f"Undefined property '{name}'")
    
    def set(self, name: str, value: Any) -> None:
        self.fields[name] = value
    
    def type_name(self) -> str:
        return f"instance<{self.klass.name}>"
    
    def __repr__(self) -> str:
        return f"<instance of {self.klass.name}>"