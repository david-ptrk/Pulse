import math
import pytest
from src.lexer import Lexer
from src.parser import Parser
from src.interpreter import Interpreter
from src.environment import Environment
from src.resolver import Resolver
from src.runtime import PulseRuntimeException
from src.error import PulseRuntimeError
from src.values import PulseNumber, PulseModule
import re

def run(source: str):
    tokens = Lexer(source).scan_tokens()
    ast = Parser(tokens, source).parse()
    interp = Interpreter(Environment())
    resolver = Resolver(interp)
    resolver.resolve(ast)
    PulseRuntimeError.clear_stack()
    return interp.interpret(ast, source)

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
# 1. Math constants
# ----------------------------------------
class TestMathConstants:
    def test_pi_constant(self):
        result = run("""
import math
math.pi
""")
        assert isinstance(result, PulseNumber)
        assert result.value == math.pi
    
    def test_e_constant(self):
        result = run("""
import math
math.e
""")
        assert isinstance(result, PulseNumber)
        assert result.value == math.e
    
    def test_tau_constant(self):
        result = run("""
import math
math.tau
""")
        assert isinstance(result, PulseNumber)
        assert result.value == math.tau
    
    def test_inf_constant(self):
        result = run("""
import math
math.inf
""")
        assert isinstance(result, PulseNumber)
        assert result.value == math.inf

# ----------------------------------------
# 2. Basic math functions
# ----------------------------------------
class TestMathFunctions:
    def test_sqrt(self):
        result = run("""
import math
math.sqrt(25)
""")
        assert isinstance(result, PulseNumber)
        assert result.value == 5
    
    def test_floor(self):
        result = run("""
import math
math.floor(3.9)
""")
        assert result.value == 3
    
    def test_ceil(self):
        result = run("""
import math
math.ceil(3.1)
""")
        assert result.value == 4
    
    def test_abs_positive(self):
        result = run("""
import math
math.abs(10)
""")
        assert result.value == 10
    
    def test_abs_negative(self):
        result = run("""
import math
math.abs(-10)
""")
        assert result.value == 10
    
    def test_pow(self):
        result = run("""
import math
math.pow(2, 5)
""")
        assert result.value == 32
    
    def test_exp(self):
        result = run("""
import math
math.exp(1)
""")
        assert pytest.approx(result.value) == math.e

# ----------------------------------------
# 3. Logarithmic functions
# ----------------------------------------
class TestLogFunctions:
    def test_log_default_base(self):
        result = run("""
import math
math.log(math.e)
""")
        assert pytest.approx(result.value) == 1
    
    def test_log_custome_base(self):
        result = run("""
import math
math.log(8, 2)
""")
        assert pytest.approx(result.value) == 3
    
    def test_log2(self):
        result = run("""
import math
math.log2(16)
""")
        assert result.value == 4
    
    def test_log10(self):
        result = run("""
import math
math.log10(1000)
""")
        assert result.value == 3

# ----------------------------------------
# 4. Trigonometric functions
# ----------------------------------------
class TestTrigFunctions:
    def test_sin(self):
        result = run("""
import math
math.sin(0)
""")
        assert pytest.approx(result.value) == 0
    
    def test_cos(self):
        result = run("""
import math
math.cos(0)
""")
        assert pytest.approx(result.value) == 1
    
    def test_tan(self):
        result = run("""
import math
math.tan(0)
""")
        assert pytest.approx(result.value) == 0

# ----------------------------------------
# 5. Runtime type checking
# ----------------------------------------
class TestMatchTypeErrors:
    def test_sqrt_non_number(self):
        raises_runtime("""
import math
math.sqrt("hello")
""", "must be a number")
    
    def test_floor_non_number(self):
        raises_runtime("""
import math
math.floor("hello")
""", "must be a number")
    
    def test_log_non_number(self):
        raises_runtime("""
import math
math.log("hello")
""", "must be a number")
    
    def test_log_invalid_base(self):
        raises_runtime("""
import math
math.log(10, "hello")
""", "base must be a number")
    
    def test_pow_invalid_base(self):
        raises_runtime("""
import math
math.pow("a", 2)
""", "base must be a number")
    
    def test_pow_invalid_exponent(self):
        raises_runtime("""
import math
math.pow(2, "a")
""", "exponent must be a number")
    
    def test_sin_non_number(self):
        raises_runtime("""
import math
math.sin("hello")
""", "must be a number")
    
    def test_abs_non_number(self):
        raises_runtime("""
import math
math.abs("hello")
""", "must be a number")

# ----------------------------------------
# 6. Module behavior
# ----------------------------------------
class TestMathModule:
    def test_math_module_exists(self):
        result = run("""
import math
math
""")
        assert isinstance(result, PulseModule)
    
    def test_nested_math_expression(self):
        result = run("""
import math
math.sqrt(math.pow(3, 2) + math.pow(4, 2))
""")
        assert pytest.approx(result.value) == 5
    
    def test_math_expression_with_constants(self):
        result = run("""
import math
math.sin(math.pi / 2)
""")
        assert pytest.approx(result.value) == 1