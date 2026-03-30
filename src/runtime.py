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

class BreakException(Exception):
    pass

class ContinueException(Exception):
    pass

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value