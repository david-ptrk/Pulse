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

import sys

# ANSI color codes
class _C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    MAGENTA = "\033[95m"
    WHITE = "\033[97m"

# Helpers
def _gutter(line_no: int, width: int) -> str:
    return f"{_C.DIM}{str(line_no).rjust(width)} |{_C.RESET}"

def _empty_gutter(width: int) -> str:
    return f"{_C.DIM}{' ' * width} |{_C.RESET}"

def _format_block(stage: str, stage_color: str, message: str, filename: str = "<pulse>", line: int = None, column: int = None, token_length: int = 1, context: str = None, hint: str = None) -> str:
    lines = []
    
    lines.append(
        f"{stage_color}{_C.BOLD}[{stage}]{_C.RESET} "
        f"{_C.WHITE}{_C.BOLD}{message}{_C.RESET}"
    )
    
    if line is not None:
        col_part = f":{column}" if column is not None else ""
        lines.append(
            f" {_C.CYAN}-->{_C.RESET} "
            f"{_C.DIM}{filename}:{line}{col_part}{_C.RESET}"
        )
    else:
        lines.append(
            f" {_C.CYAN}-->{_C.RESET} "
            f"{_C.DIM}{filename}{_C.RESET}"
        )
    
    if context is not None and line is not None:
        width = len(str(line)) + 1
        empty = _empty_gutter(width)
        filled = _gutter(line, width)
        
        lines.append(f" {empty}")
        lines.append(f" {filled} {context}")
        
        if column is not None:
            caret_offset = column - 1
            carets = stage_color + "^" * max(token_length, 1) + _C.RESET
            lines.append(f" {empty} {' ' * caret_offset}{carets}")
        
        lines.append(f" {empty}")
    
    if hint:
        lines.append(
            f"  {_C.GREEN}{_C.BOLD}hint:{_C.RESET} {_C.GREEN}{hint}{_C.RESET}"
        )
    
    return "\n".join(lines)

# Base error
class PulseError(Exception):
    STAGE = "Error"
    STAGE_COLOR = _C.RED
    
    def __init__(self, message: str, line: int = None, column: int = None, context: str = None, filename: str = "<pulse>", token_length: int = 1, hint: str = None):
        super().__init__(message)
        self.message = message
        self.line = line
        self.column = column
        self.context = context
        self.filename = filename
        self.token_length = token_length
        self.hint = hint
    
    def __str__(self) -> str:
        return _format_block(
            stage=self.STAGE,
            stage_color=self.STAGE_COLOR,
            message=self.message,
            filename=self.filename,
            line=self.line,
            column=self.column,
            token_length=self.token_length,
            context=self.context,
            hint=self.hint
        )

# Lexical error
class PulseLexError(PulseError):
    STAGE = "Lexical Error"
    STAGE_COLOR = _C.MAGENTA

# Syntax / Parse error
class PulseSyntaxError(PulseError):
    STAGE = "Syntax Error"
    STAGE_COLOR = _C.RED

# Semantic error
class PulseSemanticError(PulseError):
    STAGE = "Semantic Error"
    STAGE_COLOR = _C.YELLOW
    
    def __init__(self, message, token=None, context_source=None, filename="<pulse>", hint=None, **kwargs):
        line = getattr(token, "line", None) if token else kwargs.get("line")
        column = getattr(token, "column", None) if token else kwargs.get("column")
        length = getattr(token, "length", 1) if token else 1
        
        context = None
        if context_source and line is not None:
            src_lines = context_source.splitlines()
            if 0 < line <= len(src_lines):
                context = src_lines[line - 1]
        
        super().__init__(
            message=message,
            line=line,
            column=column,
            context=context,
            filename=filename,
            token_length=length,
            hint=hint
        )

# Runtime error
class PulseRuntimeError(PulseError):
    STAGE = "Runtime Error"
    STAGE_COLOR = _C.RED
    
    _current_stack = []
    
    @classmethod
    def push_stack(cls, func_name: str, line_number: int):
        cls._current_stack.append((func_name, line_number))
    
    @classmethod
    def pop_stack(cls):
        if cls._current_stack:
            cls._current_stack.pop()
    
    @classmethod
    def clear_stack(cls):
        cls._current_stack.clear()
    
    def __init__(self, message, token=None, context_source=None, filename="<pulse>", hint=None):
        line = getattr(token, "line", None) if token else None
        column = getattr(token, "column", None) if token else None
        length = getattr(token, "length", 1) if token else 1
        
        context = None
        if context_source and line is not None:
            src_lines = context_source.splitlines()
            if 0 < line <= len(src_lines):
                context = src_lines[line - 1]
        
        super().__init__(
            message=message,
            line=line,
            column=column,
            context=context,
            filename=filename,
            token_length=length,
            hint=hint
        )
        self.stack = list(PulseRuntimeError._current_stack)
    
    def __str__(self) -> str:
        base = super().__str__()
        if not self.stack:
            return base
        
        trace_lines = [f"\n  {_C.YELLOW}{_C.BOLD}Traceback:{_C.RESET}"]
        for func_name, ln in self.stack:
            trace_lines.append(
                f"    {_C.DIM}at{_C.RESET} "
                f"{_C.CYAN}{func_name}{_C.RESET}"
                f"{_C.DIM}  (line {ln}){_C.RESET}"
            )
        return base + "\n".join(trace_lines)

# Top-level reporter
def report_error(error: PulseError, filename: str = None) -> None:
    if filename and hasattr(error, "filename"):
        error.filename = filename
    print(str(error), file=sys.stderr)

# Example usage
if __name__ == "__main__":
    # syntax error example
    line_content = "    print(x + )"
    err1 = PulseSyntaxError("Unexpected token ')'", line=3, column=15, context=line_content)
    report_error(err1)
    
    # Runtime error example with stack trace
    PulseRuntimeError.push_stack("main", 10)
    PulseRuntimeError.push_stack("add_numbers", 5)
    PulseRuntimeError.push_stack("divide", 2)
    
    line_content_rt = "    result = a / b"
    err2 = PulseRuntimeError("Division by zero", line=12, column=14, context=line_content_rt)
    report_error(err2)
    
    PulseRuntimeError.pop_stack()
    PulseRuntimeError.pop_stack()
    PulseRuntimeError.pop_stack()