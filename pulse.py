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

# Global runtime environment
global_env = Environment()
interpreter = Interpreter(global_env)

# Core pipeline
def run(source: str) -> None:
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
    interpreter.interpret(statements, source)

# File Execution
def run_file(path: str) -> None:
    try:
        with open(path, "r", encoding="utf-8") as f:
            source = f.read()
    except FileNotFoundError:
        print(f"pulse: cannot open file '{path}': no such file", file=sys.stderr)
        sys.exit(1)
    
    try:
        run(source)
    except PulseRuntimeException as e:
        report_error(e.error)
        sys.exit(1)
    except PulseError as e:
        report_error(e)
        sys.exit(1)

# REPL
def run_prompt() -> None:
    while True:
        try:
            line = input("pulse> ")
        except EOFError:
            print()
            break
        
        try:
            run(line)
        except PulseError as e:
            print(e)

# Entry point
if __name__ == "__main__":
    if len(sys.argv) > 1:
        path = sys.argv[1]
        
        if not path.endswith(".pul"):
            report_error(
                PulseError(f'"{path}" is not a .pul file. Pulse only reads .pul, behave.')
            )
            sys.exit(1)
        
        run_file(path)
    else:
        run_prompt()