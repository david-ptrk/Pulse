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

# ----------------------------------------
# 2. Equality & comparisons across all types
# ----------------------------------------
class TestEquality:
    def test_null_equals_null(self):
        assert run("null == null").value is True
    
    def test_null_not_equal_to_zero(self):
        assert run("null == 0").value is False
    
    def test_bool_equality(self):
        assert run("true == true").value is True
        assert run("true == false").value is False
    
    def test_number_equality(self):
        assert run("1 == 1").value is True
        assert run("1 == 2").value is False
    
    def test_string_equality(self):
        assert run('"abc" == "abc"').value is True
        assert run('"abc" == "xyz"').value is False
    
    def test_list_equality_by_value(self):
        assert run("[1, 2, 3] == [1, 2, 3]").value is True
        assert run("[1, 2] == [1, 2, 3]").value is False
    
    def test_not_equal_operator(self):
        assert run("1 != 2").value is True
        assert run('"a" != "a"').value is False
    
    def test_comparison_operators(self):
        assert run("3 > 2").value is True
        assert run("2 >= 2").value is True
        assert run("1 < 2").value is True
        assert run("2 <= 1").value is False
    
    def test_different_types_not_equal(self):
        assert run('1 == "1"').value is False

# ----------------------------------------
# 3. Short-circuit evaluation
# ----------------------------------------
class TestShortCircuit:
    def test_or_short_circuits_on_true(self):
        result = run("true or (1 / 0)")
        assert result.value is True
    
    def test_and_short_circuits_on_false(self):
        result = run("false and (1 / 0)")
        assert result.value is False
    
    def test_or_returns_first_truthy(self):
        result = run("0 or 42")
        assert result.value == 42
    
    def test_and_returns_last_truthy(self):
        result = run("1 and 2")
        assert result.value == 2
    
    def test_or_returns_last_value_when_all_false(self):
        result = run("false or 0 or null")
        assert isinstance(result, PulseNull)
    
    def test_not_operator(self):
        assert run("not true").value is False
        assert run("not false").value is True
        assert run("not null").value is True
        assert run("not 0").value is True

# ----------------------------------------
# 4. String methods
# ----------------------------------------
class TestStringMethods:
    def test_upper(self):
        assert run('"hello".upper()').value == "HELLO"
    
    def test_lower(self):
        assert run('"WORLD".lower()').value == "world"
    
    def test_trim(self):
        assert run('"  hi  ".trim()').value == "hi"
    
    def test_split_default(self):
        result = run('"a b c".split()')
        assert isinstance(result, PulseList)
        assert len(result.elements) == 3
    
    def test_split_with_separator(self):
        result = run('"a,b,c".split(",")')
        assert [e.value for e in result.elements] == ["a", "b", "c"]
    
    def test_replace(self):
        assert run('"hello world".replace("world", "pulse")').value == "hello pulse"
    
    def test_starts_with(self):
        assert run('"hello".starts_with("he")').value is True
        assert run('"hello".starts_with("lo")').value is False
    
    def test_ends_with(self):
        assert run('"hello".ends_with("lo")').value is True
    
    def test_contains(self):
        assert run('"hello world".contains("world")').value is True
        assert run('"hello".contains("xyz")').value is False
    
    def test_length(self):
        assert run('"hello".length()').value == 5
    
    def test_join(self):
        result = run('", ".join(["a", "b", "c"])')
        assert result.value == "a, b, c"
    
    def test_string_index(self):
        result = run('"hello"[1]')
        assert result.value == "e"
    
    def test_string_negative_index(self):
        result = run('"hello"[-1]')
        assert result.value == "o"
    
    def test_string_index_out_of_bounds(self):
        raises_runtime('"hi"[10]', "out of range")
    
    def test_string_immutable(self):
        raises_runtime('"hello"[0] = "x"', "immutable")
    
    def test_method_chaining(self):
        result = run('"  Hello World  ".trim().lower()')
        assert result.value == "hello world"

# ----------------------------------------
# 5. List operations & mutation
# ----------------------------------------
class TestList:
    def test_literal(self):
        result = run("[1, 2, 3]")
        assert isinstance(result, PulseList)
        assert len(result.elements) == 3
    
    def test_index_access(self):
        assert run("[10, 20, 30][1]").value == 20
    
    def test_negative_index(self):
        assert run("[10, 20, 30][-1]").value == 30
    
    def test_index_out_of_bounds(self):
        raises_runtime("[1, 2][5]", "out of range")
    
    def test_index_assignment(self):
        result = run("""
x = [1, 2, 3]
x[0] = 99
x[0]
""")
        assert result.value == 99
    
    def test_append_mutates(self):
        result = run("""
x = [1, 2]
x.append(3)
x.length()
""")
        assert result.value == 3
    
    def test_pop_last(self):
        result = run("""
x = [1, 2, 3]
x.pop()
""")
        assert result.value == 3
    
    def test_pop_by_index(self):
        result = run("""
x = [10, 20, 30]
x.pop(1)
""")
        assert result.value == 20
    
    def test_pop_empty_list_errors(self):
        raises_runtime("""
x = []
x.pop()
""", "empty")
    
    def test_slice(self):
        result = run("[1, 2, 3, 4, 5].slice(1, 3)")
        assert [e.value for e in result.elements] == [2, 3]
    
    def test_contains_true(self):
        assert run("[1, 2, 3].contains(2)").value is True
    
    def test_contains_false(self):
        assert run("[1, 2, 3].contains(9)").value is False
    
    def test_reverse_mutates(self):
        result = run("""
x = [1, 2, 3]
x.reverse()
x[0]
""")
        assert result.value == 3
    
    def test_clear(self):
        result = run("""
x = [1, 2, 3]
x.clear()
x.length()
""")
        assert result.value == 0
    
    def test_list_mutation_via_reference(self):
        result = run("""
a = [1, 2, 3]
b = a
b.append(4)
a.length()
""")
        assert result.value == 4
    
    def test_nested_list(self):
        assert run("[[1, 2], [3, 4]][1][0]").value == 3

# ----------------------------------------
# 6. Dict operations
# ----------------------------------------