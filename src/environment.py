"""
environment.py

Implements the environment management system for the Pulse programming language.

The environment is responsible for storing and managing variable bindings
during program execution. It maintains mappings between identifiers and
their corresponding values, while also handling lexical scoping rules.

This module provides the foundational structure required to support
nested scopes, variable resolution, and scope chaining, which are essential
for correct execution of blocks, functions, and other scoped constructs.

The environment ensures that variables are resolved in the correct scope
by searching through enclosing environments when necessary, and allows
new scopes to be created and discarded as execution enters and exits
blocks.

This module primarily provides:
- The Environment class, which stores variable bindings in a scoped manner.
- Methods for defining, retrieving, and updating variables.
- Support for nested environments to model lexical scope.
- Error handling for undefined variables and invalid assignments.

The environment system will be used by the interpreter to manage state
during execution of a Pulse program.
"""

from typing import Any, Union
from src.tokens import Token
from src.error import PulseRuntimeError

_NameArg = Union[str, Token]
def _key(name) -> str:
    return name.lexeme if isinstance(name, Token) else name

class Environment:
    def __init__(self, enclosing=None):
        self.values = {}
        self.enclosing = enclosing
    
    def define(self, name, value):
        key = _key(name)
        
        if key in self.values:
            raise PulseRuntimeError(f"Variable '{key}' already defined.")
        self.values[key] = value
    
    def define_many(self, funcs):
        for name, value in funcs:
            self.define(name, value)
    
    def get(self, name):
        key = _key(name)
        
        if key in self.values:
            return self.values[key]
        
        if self.enclosing is not None:
            return self.enclosing.get(name)
        
        raise PulseRuntimeError(f"Undefined variable '{key}'")
    
    def assign(self, name, value):
        key = _key(name)
        
        if key in self.values:
            self.values[key] = value
            return
        
        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return
        
        raise PulseRuntimeError(f"Undefined variable '{key}'")
    
    def ancestor(self, distance):
        env = self
        for _ in range(distance):
            if env.enclosing is None:
                raise RuntimeError("Invalid scope distance: walked past global environment")
            env = env.enclosing
        return env
    
    def get_at(self, distance, name):
        key = name.lexeme if hasattr(name, "lexeme") else name
        return self.ancestor(distance).values[_key(name)]
    
    def assign_at(self, distance, name, value):
        key = name.lexeme if hasattr(name, "lexeme") else name
        self.ancestor(distance).values[_key(name)] = value