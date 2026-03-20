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

from src.error import PulseRuntimeError

class Environment:
    def __init__(self, enclosing=None):
        self.values = {}
        self.enclosing = enclosing
    
    def define(self, name, value):
        self.values[name] = value
    
    def get(self, name):
        if name in self.values:
            return self.values[name]
        
        if self.enclosing:
            return self.enclosing.get(name)
        
        raise PulseRuntimeError(f"Undefined variable '{name}'")
    
    def assign(self, name, value):
        if name in self.values:
            self.values[name] = value
            return
        
        if self.enclosing:
            self.enclosing.assign(name, value)
            return
        
        self.define(name, value)
        return