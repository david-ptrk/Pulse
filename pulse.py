import sys

from src.lexer import Lexer
from src.parser import Parser
from src.interpreter import Interpreter
from src.resolver import Resolver
from src.lexer import TokenType

# Global error flags
had_error = False
had_runtime_error = False

interpreter = Interpreter()

def run_file(path):
    global had_error, had_runtime_error

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

def run(source):
    global had_error, had_runtime_error, interpreter

    # 1. Lex
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()

    # 2. Parse
    parser = Parser(tokens)
    statements = parser.parse()

    if had_error:
        return
    
    # 3. Resolve (static analysis)
    resolver = Resolver(interpreter)
    resolver.resolve(statements)

    if had_error:
        return
    
    # 4. Interpret
    interpreter.interpret(statements)

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