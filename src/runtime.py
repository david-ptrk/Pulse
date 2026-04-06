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

from src.error import PulseRuntimeError

class PulseException(Exception):
    def __init__(self, message=""):
        super().__init__(message)
        self.message = message
    
    def __str__(self):
        return self.message

class PulseRuntimeException(PulseException):
    def __init__(self, error: PulseRuntimeError):
        super().__init__(str(error))
        self.error = error

class PulseValueError(PulseRuntimeException):
    pass

class PulseTypeError(PulseRuntimeException):
    pass

class BreakException(Exception):
    def __init__(self):
        super().__init__("break")

class ContinueException(Exception):
    def __init__(self):
        super().__init__("continue")

class ReturnException(Exception):
    def __init__(self, value=None, token=None):
        super().__init__(value)
        self.value = value
        self.token = token

class PulseClass:
    def __init__(self, name, fields):
        self.name = name
        self.fields = fields
    
    def get(self, name):
        if name in self.fields:
            return self.fields[name]
        raise PulseRuntimeException(
            PulseRuntimeError(f"Undefined property '{name}'")
        )
    
    def __repr__(self):
        return f"<class {self.name}>"