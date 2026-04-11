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
    def __init__(self, name, methods, class_vars, bases=None):
        self.name = name
        self.methods = methods
        self.class_vars = class_vars
        self.bases = bases or []
    
    def call(self, interpreter, arguments, kwargs):
        instance = PulseInstance(self)
        
        init = self.find_method("__init__")
        if init:
            init.bind(instance).call(interpreter, arguments, kwargs)
        
        return instance
    
    def find_method(self, name):
        if name in self.methods:
            return self.methods[name]
        
        for base in self.bases:
            method = base.find_method(name)
            if method:
                return method
        
        return None
    
    def get(self, name):
        if name in self.class_vars:
            return self.class_vars[name]
        
        method = self.find_method(name)
        if method:
            return method
        
        raise PulseRuntimeException(
            PulseRuntimeError(f"Undefined class member '{name}'")
        )
    
    def __repr__(self):
        return f"<class {self.name}>"

class PulseInstance:
    def __init__(self, klass):
        self.klass = klass
        self.fields = {}
    
    def get(self, name):
        if name in self.fields:
            return self.fields[name]
        
        if name in self.klass.class_vars:
            return self.klass.class_vars[name]
        
        method = self.klass.find_method(name)
        if method:
            return method.bind(self)
        
        raise PulseRuntimeException(
            PulseRuntimeError(f"Undefined property '{name}'")
        )
    
    def set(self, name, value):
        self.fields[name] = value
    
    def __repr__(self):
        return f"<instance of {self.klass.name}"