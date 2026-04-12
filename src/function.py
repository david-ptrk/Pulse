"""
function.py

Defines callable function objects for the Pulse programming language runtime.

PulseFunction wraps user-defined functions and methods declared in Pulse source
code, managing parameter binding, closure environments, and return value handling.

PulseNativeFunction wraps Python-level built-in functions exposed to the Pulse
runtime, allowing the interpreter to call them uniformly alongside user-defined
functions.
"""

from src.environment import Environment
from src.error import PulseRuntimeError
import src.runtime as runtime

class PulseFunction:
    def __init__(self, declaration, closure):
        self.declaration = declaration
        self.closure = closure
        self.is_bound = False
        self.bound_instance = None
    
    def arity(self) -> int:
        return len(self.declaration.params)
    
    def call(self, interpreter, arguments, keyword_arguments=None):
        if keyword_arguments is None:
            keyword_arguments = {}
        
        params = self.declaration.params
        callable_params = [p for p in params if p.lexeme != "self"]

        if len(arguments) > len(callable_params):
            raise runtime.PulseRuntimeException(
                PulseRuntimeError(f"Expected {len(callable_params)} arguments but got {len(arguments)}")
            )
        
        bound = {}
        for i, param in enumerate(callable_params):
            if i < len(arguments):
                bound[param.lexeme] = arguments[i]
        
        params_names = {p.lexeme for p in callable_params}
        for key, value in keyword_arguments.items():
            if key not in params_names:
                raise runtime.PulseRuntimeException(
                    PulseRuntimeError(f"Unexpected keyword argument '{key}'")
                )
            
            if key in bound:
                raise runtime.PulseRuntimeException(
                    PulseRuntimeError(f"Multiple values for argument '{key}'")
                )
            
            bound[key] = value
        
        for param in callable_params:
            if param.lexeme not in bound:
                raise runtime.PulseRuntimeException(
                    PulseRuntimeError(f"Missing required argument '{param.lexeme}'")
                )
        
        # Create a new environment for the function
        environment = Environment(enclosing=self.closure)
        
        if self.bound_instance is not None:
            environment.define("self", self.bound_instance)
        
        # Bind parameters
        for name, value in bound.items():
            environment.define(name, value)
        
        previous = interpreter.environment
        interpreter.environment = environment
        
        try:
            for stmt in self.declaration.body.statements:
                interpreter.execute(stmt)
        except runtime.ReturnException as e:
            if self.declaration.is_method and self.declaration.name.lexeme == "init":
                return self.closure.get("self")
            return e.value
        finally:
            interpreter.environment = previous
        
        return None
    
    def bind(self, instance):
        bound = PulseFunction(self.declaration, self.closure)
        bound.is_bound = True
        bound.bound_instance = instance
        return bound
    
    def __repr__(self):
        return f"<function {self.declaration.name.lexeme}>"

class PulseNativeFunction:
    def __init__(self, name, func):
        self.name = name
        self.func = func
    
    def arity(self):
        return 0
    
    def call(self, interpreter, arguments, keyword_arguments=None):
        if keyword_arguments is None:
            keyword_arguments = {}
        return self.func(*arguments, **keyword_arguments)
    
    def __repr__(self):
        return f"<native fn {self.name}>"