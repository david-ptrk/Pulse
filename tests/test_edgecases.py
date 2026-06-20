import pytest
import io
import sys
from src.lexer import Lexer
from src.parser import Parser
from src.interpreter import Interpreter
from src.resolver import Resolver
from src.environment import Environment
from src.error import PulseSemanticError
from src.runtime import PulseRuntimeException, PulseZeroDivisionError, PulseTypeError

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

def raises_pulse_error(source):
    with pytest.raises((PulseRuntimeException, PulseSemanticError)):
        run_pulse(source)

class TestArithmeticEdgeCases:
    def test_division_by_zero(self):
        with pytest.raises(PulseRuntimeException):
            run_pulse("print(1 / 0)")
    
    def test_floor_division_by_zero(self):
        with pytest.raises(PulseRuntimeException):
            run_pulse("print(1 // 0)")
    
    def test_modulo_by_zero(self):
        with pytest.raises(PulseRuntimeException):
            run_pulse("print(1 % 0)")
    
    def test_negative_modulo(self):
        assert run_pulse("print(-7 % 3)") == "2"
    
    def test_float_division_precision(self):
        assert run_pulse("print(0.1 + 0.2 == 0.3)") == "False"
    
    def test_integer_exponentiation(self):
        assert run_pulse("print(2 ** 10)") == "1024"
    
    def test_negative_exponentiation(self):
        assert run_pulse("print(2 ** -1)") == "0.5"
    
    def test_zero_exponentiation(self):
        assert run_pulse("print(0 ** 0)") == "1"
    
    def test_large_integer(self):
        assert run_pulse("print(10 ** 18)") == "1000000000000000000"
    
    def test_unary_minus(self):
        assert run_pulse("print(-(-5))") == "5"
    
    def test_chained_arithmetic(self):
        assert run_pulse("print(2 + 3 * 4 - 1)") == "13"
    
    def test_floor_division_negative(self):
        assert run_pulse("print(-7 // 2)") == "-4"

class TestStringEdgeCases:
    def test_empty_string(self):
        assert run_pulse('print("")') == ""
    
    def test_string_multiplication(self):
        with pytest.raises(PulseRuntimeException):
            run_pulse("print('ab' * 3)")
    
    def test_string_multiplication_zero(self):
        with pytest.raises(PulseRuntimeException):
            run_pulse("print('ab' * 0)")
    
    def test_string_with_newline_escape(self):
        assert run_pulse(r'print("a\nb")') == "a\nb"
    
    def test_fstring_expression(self):
        assert run_pulse('x = 5\nprint(f"val={x*2}")') == "val=10"
    
    def test_fstring_nested_expression(self):
        assert run_pulse('print(f"res={1+2+3}")') == "res=6"
    
    def test_string_equality(self):
        assert run_pulse('print("abc" == "abc")') == "True"
    
    def test_string_inequality(self):
        assert run_pulse('print("abc" != "xyz")') == "True"
    
    def test_string_comparison(self):
        with pytest.raises(PulseRuntimeException):
            run_pulse("print('a' < 'b')")
    
    def test_multiline_string(self):
        assert run_pulse('print("""hello\nworld""")') == "hello\nworld"

class TestScopingEdgeCases:
    def test_variable_use_before_assignment_raises(self):
        with pytest.raises(PulseRuntimeException):
            run_pulse("print(x)\nx = 1")
    
    def test_inner_scope_does_not_leak(self):
        source = "if True:\n    y = 10\nprint(y)"
        with pytest.raises(PulseRuntimeException):
            run_pulse(source)
    
    def test_function_scope_isolation(self):
        source = "def f():\n    z = 99\nf()\nprint(z)"
        with pytest.raises((PulseRuntimeException, PulseSemanticError, Exception)):
            run_pulse(source)
    
    def test_closure_captures_outer_variable(self):
        source = (
            "x = 10\n"
            "def f():\n"
            "    print(x)\n"
            "f()\n"
        )
        assert run_pulse(source) == "10"
    
    def test_nested_function_closure(self):
        source = (
            "def outer():\n"
            "    n = 5\n"
            "    def inner():\n"
            "        print(n)\n"
            "    inner()\n"
            "outer()\n"
        )
        assert run_pulse(source) == "5"
    
    def test_shadowing_in_function(self):
        source = (
            "x = 1\n"
            "def f():\n"
            "    x = 2\n"
            "    print(x)\n"
            "f()\n"
            "print(x)\n"
        )
        assert run_pulse(source) == "2\n1"

class TestFunctionEdgeCases:
    def test_function_no_return_gives_null(self):
        source = "def f():\n    pass\nprint(f())"
        assert run_pulse(source) in ("null", "None", "")
    
    def test_function_returns_none_explicitly(self):
        source = "def f():\n    return\nprint(f())"
        assert run_pulse(source) in ("null", "None", "")
    
    def test_recursive_factorial(self):
        source = (
            "def fact(n):\n"
            "    if n <= 1:\n"
            "        return 1\n"
            "    return n * fact(n - 1)\n"
            "print(fact(6))\n"
        )
        assert run_pulse(source) == "720"
    
    def test_default_argument(self):
        source = (
            "def greet(name, msg=\"hi\"):\n"
            "    print(msg + \" \" + name)\n"
            "greet(\"Bob\")\n"
        )
        assert run_pulse(source) == "hi Bob"
    
    def test_default_overridden(self):
        source = (
            "def greet(name, msg=\"hi\"):\n"
            "    print(msg + \" \" + name)\n"
            "greet(\"Bob\", \"hello\")\n"
        )
        assert run_pulse(source) == "hello Bob"
    
    def test_varargs(self):
        source = (
            "def f(*args):\n"
            "    print(len(args))\n"
            "f(1, 2, 3)\n"
        )
        assert run_pulse(source) == "3"
    
    def test_lambda_immediately_called(self):
        assert run_pulse("print((lambda x: x * 2)(5))") == "10"
    
    def test_lambda_as_argument(self):
        source = (
            "def apply(f, x):\n"
            "    return f(x)\n"
            "print(apply(lambda x: x + 1, 9))\n"
        )
        assert run_pulse(source) == "10"
    
    def test_return_outside_function_raises(self):
        with pytest.raises(PulseSemanticError):
            run_pulse("return 1")
    
    def test_mutual_recursion(self):
        source = (
            "def is_even(n):\n"
            "    if n == 0:\n"
            "        return True\n"
            "    return is_odd(n - 1)\n"
            "def is_odd(n):\n"
            "    if n == 0:\n"
            "        return False\n"
            "    return is_even(n - 1)\n"
            "print(is_even(4))\n"
            "print(is_odd(3))\n"
        )
        assert run_pulse(source) == "True\nTrue"
    
    def test_keyword_argument(self):
        source = (
            "def f(a, b):\n"
            "    print(a - b)\n"
            "f(b=3, a=10)\n"
        )
        assert run_pulse(source) == "7"

class TestControlFlowEdgeCases:
    def test_break_exits_loop(self):
        source = (
            "for i in range(10):\n"
            "    if i == 3:\n"
            "        break\n"
            "    print(i)\n"
        )
        assert run_pulse(source) == "0\n1\n2"
    
    def test_continue_skips_iteration(self):
        source = (
            "for i in range(5):\n"
            "    if i == 2:\n"
            "        continue\n"
            "    print(i)\n"
        )
        assert run_pulse(source) == "0\n1\n3\n4"
    
    def test_break_outside_loop_raises(self):
        with pytest.raises(PulseSemanticError):
            run_pulse("break")
    
    def test_continue_outside_loop_raises(self):
        with pytest.raises(PulseSemanticError):
            run_pulse("continue")
    
    def test_while_never_executes(self):
        assert run_pulse("while False:\n    print(1)") == ""
    
    def test_nested_loop_break(self):
        source = (
            "for i in range(3):\n"
            "    for j in range(3):\n"
            "        if j == 1:\n"
            "            break\n"
            "    print(i)\n"
        )
        assert run_pulse(source) == "0\n1\n2"
    
    def test_for_empty_iterable(self):
        assert run_pulse("for x in []:\n    print(x)") == ""
    
    def test_ternary_true(self):
        assert run_pulse('print("yes" if True else "no")') == "yes"
    
    def test_ternary_false(self):
        assert run_pulse('print("yes" if False else "no")') == "no"
    
    def test_chained_comparison(self):
        assert run_pulse("print(1 < 2 < 3)") == "True"
    
    def test_chained_comparison_false(self):
        assert run_pulse("print(1 < 2 > 3)") == "False"
    
    def test_elif_chain(self):
        source = (
            "x = 2\n"
            "if x == 1:\n"
            "    print('one')\n"
            "elif x == 2:\n"
            "    print('two')\n"
            "elif x == 3:\n"
            "    print('three')\n"
            "else:\n"
            "    print('other')\n"
        )
        assert run_pulse(source) == "two"

class TestExceptionEdgeCases:
    def test_catch_division_by_zero(self):
        source = (
            "try:\n"
            "    x = 1 / 0\n"
            "except Exception as e:\n"
            "    print(e)\n"
        )
        assert run_pulse(source) == "Division by zero"
    
    def test_finally_always_runs(self):
        source = (
            "try:\n"
            "    x = 1 / 0\n"
            "except Exception:\n"
            "    pass\n"
            "finally:\n"
            "    print('done')\n"
        )
        assert run_pulse(source) == "done"
    
    def test_finally_runs_on_success(self):
        source = (
            "try:\n"
            "    x = 1\n"
            "finally:\n"
            "    print('done')\n"
        )
        assert run_pulse(source) == "done"
    
    def test_else_runs_on_no_exception(self):
        source = (
            "try:\n"
            "    x = 1\n"
            "except Exception:\n"
            "    print('error')\n"
            "else:\n"
            "    print('ok')\n"
        )
        assert run_pulse(source) == "ok"
    
    def test_else_does_not_run_on_exception(self):
        source = (
            "try:\n"
            "    x = 1 / 0\n"
            "except Exception:\n"
            "    print('error')\n"
            "else:\n"
            "    print('ok')\n"
        )
        assert run_pulse(source) == "error"
    
    def test_nested_try_except(self):
        source = (
            "try:\n"
            "    try:\n"
            "        x = 1 / 0\n"
            "    except Exception:\n"
            "        print('inner')\n"
            "except Exception:\n"
            "    print('outer')\n"
        )
        assert run_pulse(source) == "inner"
    
    def test_raise_and_catch(self):
        source = (
            "try:\n"
            "    raise ValueError('oops')\n"
            "except Exception as e:\n"
            "    print(e)\n"
        )
        assert run_pulse(source) == "oops"
    
    def test_unhandled_exception_propagates(self):
        with pytest.raises(PulseRuntimeException):
            run_pulse("x = 1 / 0")
    
    def test_bare_except(self):
        source = (
            "try:\n"
            "    x = 1 / 0\n"
            "except:\n"
            "    print('caught')\n"
        )
        assert run_pulse(source) == "caught"

class TestListEdgeCases:
    def test_empty_list(self):
        assert run_pulse("x = []\nprint(len(x))") == "0"
    
    def test_nested_list_access(self):
        assert run_pulse("x = [[1, 2], [3, 4]]\nprint(x[1][0])") == "3"
    
    def test_negative_index(self):
        assert run_pulse("x = [1, 2, 3]\nprint(x[-1])") == "3"
    
    def test_index_out_of_bounds(self):
        with pytest.raises(PulseRuntimeException):
            run_pulse("x = [1, 2]\nprint(x[5])")
    
    def test_list_concatenation(self):
        assert run_pulse("print([1, 2] + [3, 4])") == "[1, 2, 3, 4]"
    
    def test_list_comprehension(self):
        assert run_pulse("print([x * 2 for x in range(4)])") == "[0, 2, 4, 6]"
    
    def test_list_comprehension_with_condition(self):
        assert run_pulse("print([x for x in range(6) if x % 2 == 0])") == "[0, 2, 4]"
    
    def test_list_slice(self):
        assert run_pulse("x = [1,2,3,4,5]\nprint(x[1:3])") == "[2, 3]"
    
    def test_list_mutation(self):
        source = "x = [1, 2, 3]\nx[1] = 99\nprint(x[1])"
        assert run_pulse(source) == "99"

class TestDictEdgeCases:
    def test_empty_dict(self):
        assert run_pulse("d = {}\nprint(len(d))") == "0"
    
    def test_dict_access(self):
        assert run_pulse('d = {"a": 1}\nprint(d["a"])') == "1"
    
    def test_dict_missing_key_raises(self):
        with pytest.raises(PulseRuntimeException):
            run_pulse('d = {}\nprint(d["x"])')
    
    def test_dict_update(self):
        assert run_pulse('d = {"a": 1}\nd["a"] = 2\nprint(d["a"])') == "2"
    
    def test_dict_nested(self):
        assert run_pulse('d = {"a": {"b": 42}}\nprint(d["a"]["b"])') == "42"
    
    def test_dict_keys_values(self):
        source = 'd = {"x": 1}\nprint(len(d.keys()))'
        assert run_pulse(source) == "1"

class TestLogicalEdgeCases:
    def test_short_circuit_and(self):
        source = (
            "x = False and (1/0)\n"
            "print(x)\n"
        )
        assert run_pulse(source) == "False"
    
    def test_short_circuit_or(self):
        source = (
            "x = True or (1/0)\n"
            "print(x)\n"
        )
        assert run_pulse(source) == "True"
    
    def test_not_true(self):
        assert run_pulse("print(not True)") == "False"
    
    def test_not_false(self):
        assert run_pulse("print(not False)") == "True"
    
    def test_truthy_number(self):
        assert run_pulse("print(bool(1))") == "True"
    
    def test_falsy_zero(self):
        assert run_pulse("print(bool(0))") == "False"
    
    def test_falsy_empty_string(self):
        assert run_pulse('print(bool(""))') == "False"
    
    def test_falsy_empty_list(self):
        assert run_pulse("print(bool([]))") == "False"

class TestTypeConversionEdgeCases:
    def test_int_to_string(self):
        assert run_pulse('print(str(42))') == "42"
    
    def test_string_to_int(self):
        assert run_pulse('print(int("42"))') == "42"
    
    def test_string_to_int_invalid(self):
        with pytest.raises(PulseRuntimeException):
            run_pulse('print(int("abc"))')
    
    def test_float_to_int(self):
        assert run_pulse("print(int(3.9))") == "3"
    
    def test_int_to_float(self):
        assert run_pulse("print(float(3))") == "3.0"
    
    def test_bool_to_int(self):
        assert run_pulse("print(int(True))") == "1"

class TestPipeOperatorEdgeCases:
    def test_simple_pipe(self):
        source = (
            "def double(x):\n"
            "    return x * 2\n"
            "print(5 |> double)\n"
        )
        assert run_pulse(source) == "10"
    
    def test_chained_pipe(self):
        source = (
            "def inc(x):\n"
            "    return x + 1\n"
            "def double(x):\n"
            "    return x * 2\n"
            "print(3 |> inc |> double)\n"
        )
        assert run_pulse(source) == "8"

class TestClassEdgeCases:
    def test_basic_class_instantiation(self):
        source = (
            "class Dog:\n"
            "    def __init__(self, name):\n"
            "        self.name = name\n"
            "    def speak(self):\n"
            "        print(self.name)\n"
            "d = Dog('Rex')\n"
            "d.speak()\n"
        )
        assert run_pulse(source) == "Rex"
    
    def test_class_inheritance(self):
        source = (
            "class Animal:\n"
            "    def speak(self):\n"
            "        print('...')\n"
            "class Dog(Animal):\n"
            "    def speak(self):\n"
            "        print('woof')\n"
            "Dog().speak()\n"
        )
        assert run_pulse(source) == "woof"
    
    def test_class_inherits_method(self):
        source = (
            "class A:\n"
            "    def hello(self):\n"
            "        print('hello')\n"
            "class B(A):\n"
            "    pass\n"
            "B().hello()\n"
        )
        assert run_pulse(source) == "hello"
    
    def test_class_var(self):
        source = (
            "class C:\n"
            "    count = 0\n"
            "print(C.count)\n"
        )
        assert run_pulse(source) == "0"
    
    def test_undefined_property_raises(self):
        source = (
            "class A:\n"
            "    pass\n"
            "a = A()\n"
            "print(a.x)\n"
        )
        with pytest.raises(PulseRuntimeException):
            run_pulse(source)

class TestMatchEdgeCases:
    def test_match_literal(self):
        source = (
            "x = 2\n"
            "match x:\n"
            "    case 1:\n"
            "        print('one')\n"
            "    case 2:\n"
            "        print('two')\n"
            "    case _:\n"
            "        print('other')\n"
        )
        assert run_pulse(source) == "two"
    
    def test_match_wildcard(self):
        source = (
            "x = 99\n"
            "match x:\n"
            "    case 1:\n"
            "        print('one')\n"
            "    case _:\n"
            "        print('other')\n"
        )
        assert run_pulse(source) == "other"
    
    def test_match_or_pattern(self):
        source = (
            "x = 3\n"
            "match x:\n"
            "    case 1 | 2 | 3:\n"
            "        print('low')\n"
            "    case _:\n"
            "        print('high')\n"
        )
        assert run_pulse(source) == "low"
    
    def test_match_guard(self):
        source = (
            "x = 15\n"
            "match x:\n"
            "    case n if n > 10:\n"
            "        print('big')\n"
            "    case _:\n"
            "        print('small')\n"
        )
        assert run_pulse(source) == "big"