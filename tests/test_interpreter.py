import pytest
import io
import sys
from src.lexer import Lexer
from src.parser import Parser
from src.interpreter import Interpreter
from src.resolver import Resolver
from src.environment import Environment

def run_pulse(source):
    output = io.StringIO()
    sys.stdout = output
    try:
        env = Environment()
        interpreter = Interpreter(env)
        tokens = Lexer(source).scan_tokens()
        statements = Parser(tokens, source).parse()
        Resolver(interpreter).resolve(statements)
        interpreter.interpret(statements, source)
    finally:
        sys.stdout = sys.__stdout__
    return output.getvalue().strip()

def test_print_number():
    assert run_pulse("print(42)") == "42"

def test_addition():
    assert run_pulse("print(2 + 3)") == "5"

def test_subtraction():
    assert run_pulse("print(10 - 4)") == "6"

def test_multiplication():
    assert run_pulse("print(3 * 4)") == "12"

def test_division():
    assert run_pulse("print(10 / 2)") == "5"

def test_modulus():
    assert run_pulse("print(10 % 3)") == "1"

def test_variable_assignment():
    assert run_pulse("x = 5\nprint(x)") == "5"

def test_variable_reassignment():
    assert run_pulse("x = 5\nx = 10\nprint(x)") == "10"

def test_print_string():
    assert run_pulse('print("hello")') == "hello"

def test_string_concatenation():
    result = run_pulse('print("hello" + " " + "world")')
    assert result == "hello world"

def test_true():
    assert run_pulse("print(true)") == "true"

def test_false():
    assert run_pulse("print(false)") == "false"

def test_if_true():
    source = "if true:\n    print(1)\n"
    assert run_pulse(source) == "1"

def test_if_false_else():
    source = "if false:\n    print(1)\nelse:\n    print(2)\n"
    assert run_pulse(source) == "2"