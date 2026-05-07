"""
pulse.py

Entry point for the Pulse programming language.
"""

import sys
sys.setrecursionlimit(50000)

from src.tokens import TokenType
from src.lexer import Lexer
from src.parser import Parser
from src.interpreter import Interpreter
from src.resolver import Resolver
from src.environment import Environment
from src.error import PulseError, report_error
from src.runtime import PulseRuntimeException
from src.values import PulseNull
import argparse
from time import perf_counter

# Global runtime environment
global_env = Environment()
interpreter = Interpreter(global_env)

# Core pipeline
def run(source: str) -> any:
    # 1. Lexing
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    
    # 2. Parsing
    parser = Parser(tokens, source)
    statements = parser.parse()
    
    # 3. Resolving (static analysis)
    resolver = Resolver(interpreter)
    resolver.resolve(statements)
    
    # 4. Interpretation
    return interpreter.interpret(statements, source)

def run_with_time(source: str) -> any:
    total_start = perf_counter()
    
    start = perf_counter()
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    lex_time = perf_counter() - start
    
    start = perf_counter()
    parser = Parser(tokens, source)
    statements = parser.parse()
    parse_time = perf_counter() - start
    
    start = perf_counter()
    resolver = Resolver(interpreter)
    resolver.resolve(statements)
    resolve_time = perf_counter() - start
    
    start = perf_counter()
    result = interpreter.interpret(statements, source)
    interpret_time = perf_counter() - start
    
    total_time = perf_counter() - total_start
    
    print("\n=== Pipeline Timing ===")
    print(f"Lexing:        {lex_time:.6f}s")
    print(f"Parsing:       {parse_time:.6f}s")
    print(f"Resolving:     {resolve_time:.6f}s")
    print(f"Interpret:     {interpret_time:.6f}s")
    print(f"Total:         {total_time:.6f}s")
    
    return result

# File Execution
def run_file(path: str, show_time: bool) -> None:
    try:
        with open(path, "r", encoding="utf-8") as f:
            source = f.read()
    except FileNotFoundError:
        print(f"pulse: cannot open file '{path}': no such file", file=sys.stderr)
        sys.exit(1)
    
    try:
        if show_time:
            run_with_time(source)
        else:
            run(source)
    except PulseRuntimeException as e:
        report_error(e.error)
        sys.exit(1)
    except PulseError as e:
        report_error(e)
        sys.exit(1)

# REPL
_REPL_VERSION = "0.1"
_INDENT_KEYWORDS = (
    "if", "else", "elif", "for", "while", "def", "class", "try",
    "except", "finally", "match", "case",
)

def _is_incomplete(source: str) -> bool:
    stripped = source.strip()
    if not stripped:
        return False
    if stripped.count("(") > stripped.count(")"):
        return True
    if stripped.count("[") > stripped.count("]"):
        return True
    if stripped.count("{") > stripped.count("}"):
        return True
    if stripped.endswith(":"):
        return True
    return False

def _enable_history() -> None:
    try:
        import readline
        readline.parse_and_bind("tab: complete")
    except ImportError:
        pass

def run_prompt() -> None:
    _enable_history()
    
    print(f"Pulse {_REPL_VERSION} - interactive mode")
    print(f"Python {sys.version.split()[0]} on {sys.platform}")
    print('Type "exit" or press Ctrl+Z to quit.\n')
    
    buffer = []
    indent_level = 0
    
    while True:
        prompt = ("... " + "    " * indent_level) if buffer else ">>> "
        
        try:
            line = input(prompt)
        except EOFError:
            print()
            break
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt")
            buffer = []
            indent_level = 0
            continue
        
        if not buffer and line.strip() in ("exit", "exit()", "quit", "quit()"):
            print("Goodbye.")
            break
        
        if line.strip() == "":
            if buffer:
                source = "\n".join(buffer)
                buffer = []
                indent_level = 0
                _repl_run(source)
            continue
        
        indented_line = "    " * indent_level + line.strip()
        buffer.append(indented_line)
        
        stripped = line.strip()
        if stripped.endswith(":"):
            indent_level += 1
        elif stripped in ("pass", "break", "continue") or stripped.startswith("return"):
            indent_level = max(0, indent_level - 1)
        
        source = "\n".join(buffer)
        
        if not _is_incomplete(source) and not _is_in_block(buffer):
            buffer = []
            indent_level = 0
            _repl_run(source)

def _is_in_block(buffer: list[str]) -> bool:
    for line in reversed(buffer):
        if line.strip():
            return line.startswith(" ") or line.startswith("\t")
        return False

def _repl_run(source: str) -> None:
    try:
        result = run(source)
        if result is not None and not isinstance(result, PulseNull):
            print(repr(result))
    except PulseRuntimeException as e:
        report_error(e.error)
    except PulseError as e:
        report_error(e)
    except Exception as e:
        print(f"[Internal Error] {e}")

def main() -> int:
    parser = argparse.ArgumentParser(prog="pulse", description="Pulse Programming Language")
    
    parser.add_argument("file", nargs="?", help="Pulse source file (.pul)")
    parser.add_argument("--time", action="store_true", help="Show pipeline timing information")
    args = parser.parse_args()
    
    # REPL mode
    if args.file is None:
        run_prompt()
        return 0
    
    # Validate extension
    if not args.file.lower().endswith(".pul"):
        report_error(PulseError(f'Unsupported file type: "{args.file}". Expected a .pul file.'))
        return 1
    
    run_file(args.file, args.time)
    return 0

# Entry point
if __name__ == "__main__":
    sys.exit(main())