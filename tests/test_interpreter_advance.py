import pytest
from src.lexer import Lexer
from src.parser import Parser
from src.interpreter import Interpreter
from src.environment import Environment
from src.resolver import Resolver
from src.runtime import (
    PulseRuntimeException,
    PulseException,
    PulseClass,
    PulseInstance
)
from src.error import PulseRuntimeError
from src.values import (
    PulseNumber,
    PulseString,
    PulseBoolean,
    PulseNull,
    PulseList,
    PulseDict
)
import re

def run(source: str):
    tokens = Lexer(source).scan_tokens()
    ast = Parser(tokens, source).parse()
    interp = Interpreter(Environment())
    resolver = Resolver(interp)
    resolver.resolve(ast)
    PulseRuntimeError.clear_stack()
    return interp.interpret(ast, source)

def run_expr(source: str):
    return run(source)

def strip_ansi(text: str):
    return re.sub(r'\x1b\[[0-9;]*m', '', text)

def raises_runtime(source: str, fragment: str | None = None):
    with pytest.raises(PulseRuntimeException) as exc_info:
        run(source)
    if fragment:
        clean = strip_ansi(str(exc_info.value)).lower()
        assert fragment.lower() in clean, (
            f"Expected '{fragment}' in error message, got:\n{str(exc_info.value)}"
        )
    return exc_info

# ----------------------------------------
# 1. Arithmetic & operator precedence
# ----------------------------------------
class TestArithmetic:
    def test_precedence_mul_before_add(self):
        result = run("2 + 3 * 4")
        assert isinstance(result, PulseNumber)
        assert result.value == 14
    
    def test_precedence_parens_override(self):
        result = run("(2 + 3) * 4")
        assert result.value == 20
    
    def test_integer_division(self):
        result = run("7 // 2")
        assert result.value == 3
        assert isinstance(result.value, int)
    
    def test_modulo(self):
        assert run("10 % 3").value == 1
    
    def test_unary_minus(self):
        assert run("-(-5)").value == 5
    
    def test_unary_minus_on_expression(self):
        assert run("-(2 + 3)").value == -5
    
    def test_chained_arithmetic(self):
        assert run("100 - 50 - 25").value == 25
    
    def test_float_division(self):
        result = run("7 / 2")
        assert result.value == 3.5
    
    def test_division_by_zero(self):
        raises_runtime("1 / 0", "division by zero")
    
    def test_modulo_by_zero(self):
        raises_runtime("5 % 0", "modulo by zero")
    
    def test_integer_division_by_zero(self):
        raises_runtime("5 // 0", "division by zero")
    
    def test_unary_minus_on_non_number(self):
        raises_runtime('-"hello"', "number")
    
    def test_adding_number_to_string_errors(self):
        raises_runtime('1 + "a"')
    
    def test_string_concatenation(self):
        result = run('"hello" + " " + "world"')
        assert isinstance(result, PulseString)
        assert result.value == "hello world"