"""
pulse.py

Entry point for the Pulse programming language.
"""

import sys
from src.tokens import TokenType
from src.lexer import Lexer
from src.parser import Parser
from src.interpreter import Interpreter
from src.resolver import Resolver
from src.environment import Environment
from src.error import PulseRuntimeError, report_error

# Global error flags
had_error = False
had_runtime_error = False

global_env = Environment()
interpreter = Interpreter(global_env)

# Run file / REPL
def run_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        source = f.read()
    run(source)
    
    if had_error:
        sys.exit(65)
    if had_runtime_error:
        sys.exit(70)

def run_prompt():
    global had_error
    while True:
        try:
            line = input("pulse> ")
        except EOFError:
            break
        
        run(line)
        had_error = False

# Core pipeline
def run(source):
    global had_error, had_runtime_error
    
    had_error = False
    had_runtime_error = False
    
    try:
        # 1. Lexing
        lexer = Lexer(source)
        tokens = lexer.scan_tokens()
        
        if had_error: return
        
        # 2. Parsing
        parser = Parser(tokens, source)
        statements = parser.parse()
        
        if had_error: return
        
        # 3. Resolving (static analysis)
        resolver = Resolver(interpreter)
        
        try:
            resolver.resolve(statements)
        except Exception as e:
            report_error(e)
            had_error = True
            return
        
        if had_error: return
        
        # 4. Interpretation
        interpreter.interpret(statements, source)
    except PulseRuntimeError as e:
        report_error(e)

# Error handling
def error(line, message):
    report(line, "", message)

def token_error(token, message):
    if token.type == TokenType.EOF:
        report(token.line, " at end", message)
    else:
        report(token.line, f" at '{token.lexeme}'", message)

def runtime_error(err):
    global had_runtime_error
    print(f"{err}\n[line {err.token.line}]")
    had_runtime_error = True

def report(line, where, message):
    global had_error
    print(f"[line {line}] Error{where}: {message}")
    had_error = True

# Entry point
if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_file(sys.argv[1])
    else:
        run_prompt()