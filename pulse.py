"""
pulse.py

Entry point for the Pulse programming language.
"""

import sys
sys.setrecursionlimit(50000)

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
from pulse_info import _show_info

# Core pipeline
def run(source: str, output=None, env: Environment = None, interpreter: Interpreter = None) -> any:
    if interpreter is None:
        if env is None:
            env = Environment()
        interpreter = Interpreter(env, output=output)
    
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

def run_with_time(source: str, env: Environment = None) -> any:
    if env is None:
        env = Environment()
    
    total_start = perf_counter()
    
    start = perf_counter()
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    lex_time = perf_counter() - start
    
    start = perf_counter()
    parser = Parser(tokens, source)
    statements = parser.parse()
    parse_time = perf_counter() - start
    
    interpreter = Interpreter(env)
    
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
    print(f"Interpreting:  {interpret_time:.6f}s")
    print(f"Total:         {total_time:.6f}s")
    
    return result

# File Execution
def run_file(path: str, show_time: bool, log_path: str = None) -> None:
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
        report_error(e.error, log_path=log_path)
        sys.exit(1)
    except PulseError as e:
        report_error(e, log_path=log_path)
        sys.exit(1)

# REPL
_REPL_VERSION = "0.1"

def _enable_history() -> None:
    try:
        import readline
        readline.parse_and_bind("tab: complete")
    except ImportError:
        pass

def _setup_tab_indent() -> None:
    """Configure Tab key to insert 4 spaces instead of triggering completion."""
    try:
        import readline
        readline.parse_and_bind('tab: self-insert')
        readline.set_completer(None)
    except ImportError:
        pass

def _expand_tabs(line: str, tabsize: int = 4) -> str:
    """Expand leading tabs to spaces; leave in-string tabs untouched."""
    return line.expandtabs(tabsize)

def _opens_block(line: str) -> bool:
    """True if this line is a block header that expects an indented body."""
    stripped = line.strip()
    if stripped.endswith(":"):
        return True
    if stripped.startswith("@"):
        return True
    if stripped.endswith("\\"):
        return True
    return False

def run_prompt() -> None:
    _enable_history()
    _setup_tab_indent()
    
    print(f"Pulse {_REPL_VERSION} - interactive mode")
    print(f"Python {sys.version.split()[0]} on {sys.platform}")
    print('Type "exit" or press Ctrl+Z to quit.\n')
    
    env = Environment()
    interpreter = Interpreter(env)
    buffer: list[str] = []
    
    while True:
        prompt = "... " if buffer else ">>> "
        
        try:
            line = input(prompt)
        except EOFError:
            if buffer:
                source = "\n".join(buffer)
                buffer = []
                _repl_run(source, interpreter)
            print()
            break
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt")
            buffer = []
            continue
        
        if not buffer and line.strip() in ("exit", "exit()", "quit", "quit()"):
            print("Goodbye.")
            break
        
        if line.strip() == "":
            if buffer:
                source = "\n".join(buffer)
                buffer = []
                _repl_run(source, interpreter)
            continue
        
        buffer.append(_expand_tabs(line))
        
        if len(buffer) == 1 and not _opens_block(buffer[0]):
            source = buffer[0]
            buffer = []
            _repl_run(source, interpreter)

def _repl_run(source: str, interpreter: Interpreter) -> None:
    try:
        result = run(source, interpreter=interpreter)
        if result is not None and not isinstance(result, PulseNull):
            print(repr(result))
    except PulseRuntimeException as e:
        report_error(e.error)
    except PulseError as e:
        report_error(e)
    except Exception as e:
        print(f"[Internal Error] {e}")

def main() -> int:
    parser = argparse.ArgumentParser(prog="pulse", description="Pulse Programming Language", add_help=True)
    
    parser.add_argument("file", nargs="?", help="Pulse source file (.pul)")
    parser.add_argument("--time", action="store_true", help="Show pipeline timing")
    parser.add_argument("--info", action="store_true", help="Show language reference")
    parser.add_argument("--log", action="store_true", help="Log errors as JSON Lines to <file>.log next to the source file")
    args = parser.parse_args()
    
    if args.info:
        _show_info()
        return 0
    
    # REPL mode
    if args.file is None:
        run_prompt()
        return 0
    
    # Validate extension
    if not args.file.lower().endswith(".pul"):
        report_error(PulseError(f'Unsupported file type: "{args.file}". Expected a .pul file.'))
        return 1
    
    log_path = f"{args.file}.log" if args.log else None
    run_file(args.file, args.time, log_path)
    return 0

# Entry point
if __name__ == "__main__":
    sys.exit(main())