"""
function.py
"""

from src.environment import Environment
from src.error import ReturnException, PulseRuntimeError

class PulseFunction:
    def __init__(self, declaration, closure):
        self.declaration = declaration
        self.closure = closure
    
    def arity(self):
        return len(self.declaration.params)
    
    def call(self, interpreter, arguments):
        if len(arguments) != self.arity():
            raise PulseRuntimeError(f"Expected {self.arity()} arguments but got {len(arguments)}")
        
        # Create a new environment for the function
        environment = Environment(enclosing=self.closure)
        
        # Bind parameters
        for param, arg in zip(self.declaration.params, arguments):
            environment.define(param.lexeme, arg)
        
        previous = interpreter.environment
        interpreter.environment = environment
        
        try:
            for stmt in self.declaration.body:
                interpreter.execute(stmt)
        except ReturnException as e:
            return e.value
        finally:
            interpreter.environment = previous
        
        return None
    
    def __repr__(self):
        return "<function>"

class PulseNativeFunction:
    def __init__(self, name, func):
        self.name = name
        self.func = func
    
    def arity(self):
        return 0
    
    def call(self, interpreter, arguments):
        return self.func(*arguments)
    
    def __repr__(self):
        return f"<native fn {self.name}>"