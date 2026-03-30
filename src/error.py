"""
error.py

Handles error reporting for the Pulse programming language.

This module provides mechanisms to detect, format, and display errors
encountered during different stages of the language pipeline, including
lexing, parsing, and interpretation. Errors are reported with useful
context, such as line numbers and source code snippets, to help the
developer or user identify and fix issues quickly.

Key functionalities include:

- Lexical and syntax error reporting with line context.
- Runtime error messages (if integrated with the interpreter).
- Utilities to consistently format and print errors for debugging or user feedback.

By centralizing error handling, this module ensures that Pulse programs
provide clear and informative diagnostics, which is essential for
both language development and user experience.
"""

class PulseError(Exception):
    RED = "\033[91m"
    CYAN = "\033[96m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"

    def __init__(self, message, line=None, column=None, context=None):
        super().__init__(message)
        self.message = message
        self.line = line
        self.column = column
        self.context = context
    
    def __str__(self):
        loc = f"{self.CYAN}Line {self.line}, Col {self.column}{self.RESET}" if self.line is not None else ""
        ctx = ""
        if self.context and self.column is not None:
            pointer_line = " " * (self.column - 1) + f"{self.RED}^{self.RESET}"
            ctx = f"\n{self.context}\n{pointer_line}"
        elif self.context:
            ctx = f"\n{self.context}"
        return f"{self.RED}[PulseError]{self.RESET} {loc} - {self.message}{ctx}"

class PulseLexError(PulseError):
    pass

class PulseSyntaxError(PulseError):
    pass

class PulseRuntimeError(PulseError):
    _current_stack = []
    
    @classmethod
    def push_stack(cls, func_name, line_number):
        cls._current_stack.append((func_name, line_number))
    
    @classmethod
    def pop_stack(cls):
        if cls._current_stack:
            cls._current_stack.pop()
    
    @classmethod
    def clear_stack(cls):
        cls._current_stack.clear()
    
    def __init__(self, message, token=None, context_source=None):
        line = getattr(token, "line", None) if token else None
        column = getattr(token, "column", None) if token else None
        
        context = None
        if context_source and line is not None:
            lines = context_source.splitlines()
            if 0 < line <= len(lines):
                context = lines[line - 1]
        
        super().__init__(message, line=line, column=column, context=context)
        self.stack = list(PulseRuntimeError._current_stack)
    
    def __str__(self):
        base = super().__str__()
        if self.stack:
            stack_trace = "\n".join(
                f"{self.YELLOW}  at {func} (Line {ln}){self.RESET}" for func, ln in self.stack
            )
            return f"{base}\nStack trace:\n{stack_trace}"
        return base

class PulseSemanticError(PulseError):
    def __init__(self, message, token=None, context_source=None):
        line = getattr(token, "line", None) if token else None
        column = getattr(token, "column", None) if token else None
        
        context = None
        if context_source and line is not None:
            lines = context_source.splitlines()
            if 0 < line <= len(lines):
                context = lines[line - 1]
        
        super().__init__(message, line=line, column=column, context=context)

# Utility function to report errors
def report_error(error):
    print(error)

# Example usage
if __name__ == "__main__":
    # syntax error example
    line_content = "    print(x + )"
    err1 = SyntaxError("Unexpected token ')'", line=3, column=15, context=line_content)
    report_error(err1)
    
    # Runtime error example with stack trace
    RuntimeError.push_stack("main", 10)
    RuntimeError.push_stack("add_numbers", 5)
    RuntimeError.push_stack("divide", 2)
    
    line_content_rt = "    result = a / b"
    err2 = RuntimeError("Division by zero", line=12, column=14, context=line_content_rt)
    report_error(err2)
    
    RuntimeError.pop_stack()
    RuntimeError.pop_stack()
    RuntimeError.pop_stack()