import pytest
from src.lexer import Lexer
from src.parser import Parser
from src.interpreter import Interpreter
from src.environment import Environment
from src.resolver import Resolver
from src.runtime import (PulseRuntimeException, PulseInstance )
from src.error import PulseRuntimeError, PulseSemanticError, PulseSyntaxError
from src.values import (
    PulseNumber, PulseString, PulseBoolean,
    PulseNull, PulseList, PulseDict, PulseRange,
    PulseTensor
)
import re
import numpy as np

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

def raises_semantic(source: str, fragment: str | None = None):
    with pytest.raises(PulseSemanticError) as exc_info:
        run(source)
    if fragment:
        clean = strip_ansi(str(exc_info.value)).lower()
        assert fragment.lower() in clean, (
            f"Expected '{fragment}' in error message, got:\n{str(exc_info.value)}"
        )
    return exc_info

def raises_syntax(source: str, fragment: str | None = None):
    with pytest.raises(PulseSyntaxError) as exc_info:
        run(source)
    if fragment:
        clean = strip_ansi(str(exc_info.value)).lower()
        assert fragment.lower() in clean, (
            f"Expected '{fragment}' in error message, got:\n{str(exc_info.value)}"
        )
    return exc_info

def tensor_result(source: str) -> np.ndarray:
    result = run(source)
    assert isinstance(result, PulseTensor), (
        f"Expected PulseTensor, got {type(result).__name__}"
    )
    return result.array

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
class TestDict:
    def test_literal_and_access(self):
        result = run('{"a": 1, "b": 2}["a"]')
        assert result.value == 1
    
    def test_assignment(self):
        result = run("""
d = {"x": 10}
d["x"] = 99
d["x"]
""")
        assert result.value == 99
    
    def test_new_key(self):
        result = run("""
d = {}
d["key"] = "val"
d["key"]
""")
        assert result.value == "val"
    
    def test_has_true(self):
        assert run('{"a": 1}.has("a")').value is True
    
    def test_has_false(self):
        assert run('{"a": 1}.has("z")').value is False
    
    def test_missing_key_errors(self):
        raises_runtime('{"a": 1}["z"]', "not found")
    
    def test_keys(self):
        result = run('{"a": 1, "b": 2}.keys()')
        assert isinstance(result, PulseList)
        assert len(result.elements) == 2
    
    def test_values(self):
        result = run('{"a": 1, "b": 2}.values()')
        assert isinstance(result, PulseList)
    
    def test_items(self):
        result = run('{"a": 1}.items()')
        assert isinstance(result, PulseList)
        assert isinstance(result.elements[0], PulseList)
    
    def test_remove(self):
        result = run("""
d = {"a": 1, "b": 2}
d.remove("a")
d.has("a")
""")
        assert result.value is False
    
    def test_remove_missing_key_errors(self):
        raises_runtime('{"a": 1}.remove("z")', "not found")
    
    def test_length(self):
        assert run('{"a": 1, "b": 2}.length()').value == 2
    
    def test_for_loop_iterates_keys(self):
        result = run("""
d = {"x": 1, "y": 2}
keys = []
for k in d:
    keys.append(k)
keys.length()
""")
        assert result.value == 2

# ----------------------------------------
# 7. Control flow
# ----------------------------------------
class TestControlFlow:
    def test_if_true_branch(self):
        assert run("""
x = 0
if true:
    x = 1
x
""").value == 1
    
    def test_if_false_branch(self):
        assert run("""
x = 0
if false:
    x = 1
else:
    x = 2
x
""").value == 2
    
    def test_elif_chain(self):
        assert run("""
x = 2
if x == 1:
    x = 10
elif x == 2:
    x = 20
elif x == 3:
    x = 30
else:
    x = 0
x
""").value == 20
    
    def test_while_loop(self):
        assert run("""
i = 0
while i < 5:
    i = i + 1
i
""").value == 5
    
    def test_while_break(self):
        assert run("""
i = 0
while true:
    if i == 3:
        break
    i = i + 1
i
""").value == 3
    
    def test_while_continue(self):
        result = run("""
evens = []
i = 0
while i < 6:
    i = i + 1
    if i % 2 != 0:
        continue
    evens.append(i)
evens.length()
""")
        assert result.value == 3
    
    def test_for_loop_over_list(self):
        assert run("""
total = 0
for x in [1, 2, 3, 4]:
    total = total + x
total
""").value == 10
    
    def test_for_loop_over_string(self):
        result = run("""
chars = []
for c in "abc":
    chars.append(c)
chars.length()
""")
        assert result.value == 3
    
    def test_for_loop_over_range(self):
        assert run("""
total = 0
for i in range(5):
    total = total + i
total
""").value == 10
    
    def test_for_loop_break(self):
        assert run("""
found = 0
for x in [1, 2, 3, 4, 5]:
    if x == 3:
        found = x
        break
found
""").value == 3
    
    def test_for_loop_continue(self):
        result = run("""
result = []
for x in [1, 2, 3, 4, 5]:
    if x == 3:
        continue
    result.append(x)
result.length()
""")
        assert result.value == 4
    
    def test_nested_loop_break_only_inner(self):
        result = run("""
count = 0
for i in range(3):
    for j in range(3):
        if j == 1:
            break
        count = count + 1
count
""")
        assert result.value == 3
    
    def test_return_exits_nested_loop(self):
        result = run("""
def find():
    for i in range(5):
        for j in range(5):
            if i == 2 and j == 2:
                return i * 10 + j
    return -1

find()
""")
        assert result.value == 22

# ----------------------------------------
# 8. Functions
# ----------------------------------------
class TestFunctions:
    def test_basic_call(self):
        assert run("""
def add(a, b):
    return a + b
add(3, 4)
""").value == 7
    
    def test_return_null_implicitly(self):
        result = run("""
def nothing():
    pass
nothing()
""")
        assert isinstance(result, PulseNull)
    
    def test_recursive__fibonacci(self):
        result = run("""
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)
fib(10)
""")
        assert result.value == 55
    
    def test_closure_captures_enclosing_variable(self):
        result = run("""
def make_adder(n):
    def add(x):
        return x + n
    return add

add5 = make_adder(5)
add5(3)
""")
        assert result.value == 8
    
    def test_closure_cell_is_shared(self):
        result = run("""
def make_counter():
    count = 0
    def inc():
        count = count + 1
        return count
    return inc

c = make_counter()
c()
c()
c()
""")
        assert result.value == 3
    
    def test_keyword_arguments(self):
        result = run("""
def greet(name, greeting):
    return greeting + " " + name

greet(name="Pulse", greeting="Hello")
""")
        assert result.value == "Hello Pulse"
    
    def test_positional_and_keyword_mixed(self):
        result = run("""
def f(a, b, c):
    return a + b + c
f(1, 2, c=3)
""")
        assert result.value == 6
    
    def test_higher_order_function(self):
        result = run("""
def apply(func, value):
    return func(value)

def double(x):
    return x * 2

apply(double, 5)
""")
        assert result.value == 10
    
    def test_function_as_return_value(self):
        result = run("""
def multiplier(n):
    def mul(x):
        return x * n
    return mul

triple = multiplier(3)
triple(7)
""")
        assert result.value == 21
    
    def test_variadic_via_list(self):
        result = run("""
def sum_all(nums):
    total = 0
    for n in nums:
        total = total + n
    return total
sum_all([1, 2, 3, 4, 5])
""")
        assert result.value == 15
    
    def test_mutual_recursion(self):
        result = run("""
def is_even(n):
    if n == 0:
        return true
    return is_odd(n - 1)

def is_odd(n):
    if n == 0:
        return false
    return is_even(n - 1)

is_even(10)
""")
        assert result.value is True

# ----------------------------------------
# 9. Classes
# ----------------------------------------
class TestClasses:
    def test_basic_instantiation(self):
        result = run("""
class Dog:
    def __init__(self, name):
        self.name = name

d = Dog("Rex")
d.name
""")
        assert result.value == "Rex"
    
    def test_method_call(self):
        result = run("""
class Counter:
    def __init__(self):
        self.count = 0
    def increment(self):
        self.count = self.count + 1
    def get(self):
        return self.count

c = Counter()
c.increment()
c.increment()
c.increment()
c.get()
""")
        assert result.value == 3
    
    
    def test_class_without_init(self):
        result = run("""
class Empty:
    pass

e = Empty()
e
""")
        assert isinstance(result, PulseInstance)
    
    def test_class_variable(self):
        result = run("""
class Config:
    version = 42

Config.version
""")
        assert result.value == 42
    
    def test_instance_field_shadows_class_var(self):
        result = run("""
class C:
    x = 10
    def set(self, v):
        self.x = v
    def get(self):
        return self.x

obj = C()
obj.set(99)
obj.get()
""")
        assert result.value == 99
    
    def test_static_method(self):
        result = run("""
class Math:
    static def square(n):
        return n * n

Math.square(7)
""")
        assert result.value == 49
    
    def test_single_inheritance(self):
        result = run("""
class Animal:
    def speak(self):
        return "..."

class Dog(Animal):
    def speak(self):
        return "Woof"

d = Dog()
d.speak()
""")
        assert result.value == "Woof"
    
    def test_inheritance_method_fallback(self):
        result = run("""
class Animal:
    def breathe(self):
        return "inhale"

class Dog(Animal):
    def speak(self):
        return "Woof"

d = Dog()
d.breathe()
""")
        assert result.value == "inhale"
    
    def test_super_init_manual(self):
        result = run("""
class Vehicle:
    def __init__(self, speed):
        self.speed = speed

class Car(Vehicle):
    def __init__(self, speed, brand):
        Vehicle.__init__(self, speed)
        self.brand = brand
    def info(self):
        return self.brand

c = Car(100, "Tesla")
c.info()
""")
        assert result.value == "Tesla"
    
    def test_undefined_property_errors(self):
        raises_runtime("""
class A:
    pass
a = A()
a.foo
""", "undefined")
    
    def test_instance_method_not_accessible_on_class(self):
        raises_runtime("""
class A:
    def greet(self):
        return "hi"
A.greet()
""", "non-static")
    
    def test_chained_method_calls(self):
        result = run("""
class Builder:
    def __init__(self):
        self.parts = []
    def add(self, part):
        self.parts.append(part)
        return self
    def build(self):
        return self.parts.length()

Builder().add("a").add("b").add("c").build()
""")
        assert result.value == 3
    
    def test_mro_depth_two(self):
        result = run("""
class C:
    def hello(self):
        return "C"

class B(C):
    pass

class A(B):
    pass

A().hello()
""")
        assert result.value == "C"

# ----------------------------------------
# 10. Try / except / else / finally
# ----------------------------------------
class TestTryExcept:
    def test_try_no_execution_runs_else(self):
        result = run("""
log = []
try:
    log.append("try")
except Exception:
    log.append("except")
else:
    log.append("else")
finally:
    log.append("finally")
log.length()
""")
        assert result.value == 3
    
    def test_try_with_exception_skips_else(self):
        result = run("""
log = []
try:
    log.append("try")
    x = 1 / 0
    log.append("after_error")
except Exception:
    log.append("except")
else:
    log.append("else")
finally:
    log.append("finally")
log
""")
        values = [e.value for e in result.elements]
        assert values == ["try", "except", "finally"]
    
    def test_finally_always_runs_on_success(self):
        result = run("""
ran = false
try:
    x = 1 + 1
finally:
    ran = true
ran
""")
        assert result.value is True
    
    def test_finally_always_runs_on_error(self):
        result = run("""
ran = false
try:
    try:
        x = 1 / 0
    finally:
        ran = true
except Exception:
    pass
ran
""")
        assert result.value is True
    
    def test_except_catches_by_type(self):
        result = run("""
caught = false
try:
    x = 1 / 0
except Exception:
    caught = true
caught
""")
        assert result.value is True
    
    def test_bare_except_catches_all(self):
        result = run("""
caught = false
try:
    x = 1 / 0
except:
    caught = true
caught
""")
        assert result.value is True
    
    def test_uncaught_exception_propagates(self):
        raises_runtime("""
try:
    x = 1 / 0
except ValueError:
    pass
""")
    
    def test_exception_variable_binding(self):
        result = run("""
msg = ""
try:
    x = 1 / 0
except Exception as e:
    msg = "caught"
msg
""")
        assert result.value == "caught"
    
    def test_nested_try_inner_caught(self):
        result = run("""
log = []
try:
    try:
        x = 1 / 0
    except Exception:
        log.append("inner")
    log.append("after_inner")
except Exception:
    log.append("outer")
log.length()
""")
        assert result.value == 2
    
    def test_return_inside_try_still_runs_finally(self):
        result = run("""
log = []
def f():
    try:
        log.append("try")
        return 42
    finally:
        log.append("finally")

val = f()
log.length()
""")
        assert result.value == 2
    
    def test_break_inside_try_runs_finally(self):
        result = run("""
log = []
for i in range(3):
    try:
        if i == 1:
            break
    finally:
        log.append(i)
log.length()
""")
        assert result.value == 2

# ----------------------------------------
# 11. Error diagnostics
# ----------------------------------------
class TestErrorDiagnostics:
    def test_runtime_exception_wraps_runtime_error(self):
        with pytest.raises(PulseRuntimeException) as exc_info:
            run("1 / 0")
        assert isinstance(exc_info.value.error, PulseRuntimeError)
    
    def test_error_has_message(self):
        with pytest.raises(PulseRuntimeException) as exc_info:
            run("1 / 0")
        assert exc_info.value.error.message != ""
    
    def test_error_str_contains_stage_label(self):
        with pytest.raises(PulseRuntimeException) as exc_info:
            run("1 / 0")
        assert "[Runtime Error]" in str(exc_info.value)
    
    def test_stack_populated_on_nested_call(self):
        PulseRuntimeError.clear_stack()
        with pytest.raises(PulseRuntimeException) as exc_info:
            run("""
def bad():
    return 1 / 0
bad()
""")
        error = exc_info.value.error
        assert isinstance(error, PulseRuntimeError)
        assert len(error.stack) >= 1
    
    def test_calling_non_callable_errors(self):
        raises_runtime("42()", "non-callable")
    
    def test_accessing_member_of_null_errors(self):
        raises_runtime("""
x = null
x.foo
""", "null")
    
    def test_undefined_variable_errors(self):
        raises_runtime("fooBarBaz", "undefined")
    
    def test_index_non_indexable_errors(self):
        raises_runtime("true[0]", "indexing")
    
    def test_wrong_type_for_builtin(self):
        raises_runtime('abs("hello")', "number")
    
    def test_sqrt_negative_errors(self):
        raises_runtime("""
from math import sqrt
sqrt(-1)
""", "non-negative")

# ----------------------------------------
# 12. F-strings
# ----------------------------------------
class TestFStrings:
    def test_basic_interpolation(self):
        result = run("""
name = "Pulse"
f"Hello, {name}!"
""")
        assert "Pulse" in result.value
    
    def test_expression_interpolation(self):
        result = run('f"Result: {2 + 3}"')
        assert "5" in result.value
    
    def test_nested_call_in_fstring(self):
        result = run('f"len: {len([1, 2, 3])}"')
        assert "3" in result.value
    
    def test_multiple_interpolations(self):
        result = run("""
a = 1
b = 2
f"{a} + {b} = {a + b}"
""")
        assert "1" in result.value
        assert "3" in result.value
    
    def test_fstring_with_dict_access(self):
        result = run("""
d = {"key": "value"}
f"got {d["key"]}"
""")
        assert "value" in result.value

# ----------------------------------------
# 13. Built-in functions
# ----------------------------------------
class TestBuiltins:
    def test_len_list(self):
        assert run("len([1, 2, 3])").value == 3
    
    def test_len_string(self):
        assert run('len("hello")').value == 5
    
    def test_len_dict(self):
        assert run('len({"a": 1, "b": 2})').value == 2
    
    def test_range_one_arg(self):
        result = run("range(5)")
        assert isinstance(result, PulseRange)
    
    def test_range_two_args(self):
        result = run("""
total = 0
for i in range(2, 6):
    total = total + i
total
""")
        assert result.value == 14
    
    def test_range_step_zero_errors(self):
        raises_runtime("range(0, 10, 0)", "step")
    
    def test_abs_positive(self):
        assert run("abs(5)").value == 5
    
    def test_abs_negative(self):
        assert run("abs(-7)").value == 7
    
    def test_pow(self):
        assert run("pow(2, 10)").value == 1024
    
    def test_sqrt(self):
        assert run("""
from math import sqrt
sqrt(16)
""").value == 4.0
    
    def test_round(self):
        assert run("round(3.7)").value == 4
    
    def test_round_digits(self):
        assert run("round(3.14159, 2)").value == 3.14
    
    def test_floor(self):
        assert run("""
from math import floor
floor(3.9)
""").value == 3
    
    def test_ceil(self):
        assert run("""
from math import ceil
ceil(3.1)
""").value == 4
    
    def test_min(self):
        assert run("min(3, 1, 4, 1, 5)").value == 1
    
    def test_max(self):
        assert run("max(3, 1, 4, 1, 5)").value == 5
    
    def test_int_from_string(self):
        assert run('int("42")').value == 42
    
    def test_int_bad_string_errors(self):
        raises_runtime('int("abc")', "convert")
    
    def test_float_from_string(self):
        assert run('float("3.14")').value == pytest.approx(3.14)
    
    def test_str_of_number(self):
        result = run("str(42)")
        assert isinstance(result, PulseString)
    
    def test_type_of_number(self):
        result = run("type(42)")
        assert isinstance(result, PulseString)
        assert "number" in result.value.lower()
    
    def test_type_of_string(self):
        result = run('type("hi")')
        assert "string" in result.value.lower()
    
    def test_type_of_list(self):
        result = run("type([1, 2])")
        assert "list" in result.value.lower()

# ----------------------------------------
# 14. Edge cases & regression guards
# ----------------------------------------
class TestEdgeCases:
    def test_empty_program(self):
        result = run("")
        assert result is None
    
    def test_multiple_assignments_same_name(self):
        assert run("""
x = 1
x = 2
x = 3
x
""").value == 3
    
    def test_truthiness_of_empty_list(self):
        assert run("not []").value is True
    
    def test_truthiness_of_non_empty_list(self):
        assert run("not [1]").value is False
    
    def test_truthiness_of_zero(self):
        assert run("not 0").value is True
    
    def test_truthiness_of_empty_string(self):
        assert run('not ""').value is True
    
    def test_deep_nesting_does_not_crash(self):
        result = run("((((((1 + 1))))))")
        assert result.value == 2
    
    def test_function_redefinition(self):
        raises_semantic("""
def f():
    return 1
def f():
    return 2
f()
""")
    
    def test_variable_scope_does_not_leak_from_block(self):
        raises_runtime("""
if true:
    secret = 42
secret
""")
    
    def test_variable_scope_uses_outer(self):
        result = run("""
secret = None
if true:
    secret = 42
secret
""")
        result.value == 42
    
    def test_for_loop_variable_inaccessible_after(self):
        raises_runtime("""
for i in range(3):
    pass
i
""")
    
    def test_large_recursion_without_crash(self):
        result = run("""
def count(n):
    if n == 0:
        return 0
    return 1 + count(n - 1)
count(200)
""")
        assert result.value == 200
    
    def test_passing_function_modifies_external_list(self):
        result = run("""
def fill(lst):
    lst.append(99)

items = []
fill(items)
items[0]
""")
        assert result.value == 99
    
    def test_null_equality_is_symmetric(self):
        assert run("null == null").value is True
        assert run("null != null").value is False
    
    def test_boolean_not_equal_to_number(self):
        assert run("true == 1").value is False

# ----------------------------------------
# 15. Tensor - construction & basic properties
# ----------------------------------------
class TestTensorConstruction:
    def test_1d_tensor_shape(self):
        result = run("@[1, 2, 3].shape")
        assert isinstance(result, PulseList)
        assert result.elements[0].value == 3
    
    def test_2d_tensor_shape(self):
        result = run("@[[1, 2], [3, 4]].shape")
        dims = [e.value for e in result.elements]
        assert dims == [2, 2]
    
    def test_tensor_ndim_1d(self):
        assert run("@[1, 2, 3].ndim").value == 1
    
    def test_tensor_ndim_2d(self):
        assert run("@[[1, 2], [3, 4]].ndim").value == 2
    
    def test_tensor_size(self):
        assert run("@[[1, 2], [3, 4]].size").value == 4
    
    def test_tensor_dtype(self):
        result = run("@[1.0, 2.0].dtype")
        assert isinstance(result, PulseString)
        assert "float" in result.value
    
    def test_tensor_type_name(self):
        result = run("type(@[1, 2])")
        assert "tensor" in result.value.lower()

# ----------------------------------------
# 16. Tensor - arithmetic (tensor OP tensor)
# ----------------------------------------
class TestTensorArithmetic:
    def test_tensor_add(self):
        arr = tensor_result("@[1, 2, 3] + @[4, 5, 6]")
        np.testing.assert_array_equal(arr, [5.0, 7.0, 9.0])
    
    def test_tensor_subtract(self):
        arr = tensor_result("@[5, 5, 5] - @[1, 2, 3]")
        np.testing.assert_array_equal(arr, [4.0, 3.0, 2.0])
    
    def test_tensor_elementwise_multiply(self):
        arr = tensor_result("@[1, 2, 3] * @[2, 2, 2]")
        np.testing.assert_array_equal(arr, [2.0, 4.0, 6.0])
    
    def test_tensor_elementwise_divide(self):
        arr = tensor_result("@[4, 6, 8] / @[2, 2, 2]")
        np.testing.assert_array_equal(arr, [2.0, 3.0, 4.0])
    
    def test_tensor_matmul(self):
        arr = tensor_result("@[[1, 2], [3, 4]] @ @[[1, 0], [0, 1]]")
        np.testing.assert_array_equal(arr,[[1.0, 2.0], [3.0, 4.0]])
    
    def test_tensor_matmul_dot_product(self):
        result = run("@[1, 2, 3] @ @[4, 5, 6]")
        assert isinstance(result, (PulseTensor, PulseNumber))
        val = float(result.array) if isinstance(result, PulseTensor) else result.value
        assert val == pytest.approx(32.0)
    
    def test_tensor_equality_true(self):
        result = run("@[1, 2, 3] == @[1, 2, 3]")
        assert isinstance(result, PulseBoolean)
        assert result.value is True
    
    def test_tensor_equality_false(self):
        result = run("@[1, 2, 3] == @[1, 2, 4]")
        assert result.value is False
    
    def test_tensor_not_equal(self):
        result = run("@[1, 2] != @[1, 2]")
        assert result.value is False
    
    def test_tensor_shape_mismatch_add_errors(self):
        raises_runtime("@[1, 2] + @[1, 2, 3]", "tensor operation failed")
    
    def test_tensor_wrong_type_errors(self):
        raises_runtime("@[1, 2] + 'hello'")

# ----------------------------------------
# 17. Tensor - scalar operations (commutativity)
# ----------------------------------------
class TestTensorScalarOps:
    def test_tensor_add_scalar(self):
        arr = tensor_result("@[1, 2, 3] + 10")
        np.testing.assert_array_equal(arr, [11.0, 12.0, 13.0])
    
    def test_scalar_add_tensor_commutative(self):
        arr = tensor_result("10 + @[1, 2, 3]")
        np.testing.assert_array_equal(arr, [11.0, 12.0, 13.0])
    
    def test_tensor_multiply_scalar(self):
        arr = tensor_result("@[1, 2, 3] * 3")
        np.testing.assert_array_equal(arr, [3.0, 6.0, 9.0])
    
    def test_scalar_multiply_tensor_commutative(self):
        arr = tensor_result("3 * @[1, 2, 3]")
        np.testing.assert_array_equal(arr, [3.0, 6.0, 9.0])
    
    def test_tensor_subtract_scalar(self):
        arr = tensor_result("@[5, 6, 7] - 2")
        np.testing.assert_array_equal(arr, [3.0, 4.0, 5.0])
    
    def test_tensor_divide_scalar(self):
        arr = tensor_result("@[4, 6, 8] / 2")
        np.testing.assert_array_equal(arr, [2.0, 3.0, 4.0])
    
    def test_tensor_divide_scalar_zero_errors(self):
        raises_runtime("@[1, 2, 3] / 0", "division by zero")
    
    def test_tensor_unsupported_op_with_scalar_errors(self):
        raises_runtime("@[1, 2] % 2", "does not support operator")

# ----------------------------------------
# 18. Tensor - indexing
# ----------------------------------------
class TestTensorIndexing:
    def test_1d_index_returns_number(self):
        result = run("@[10, 20, 30][1]")
        assert isinstance(result, PulseNumber)
        assert result.value == pytest.approx(20.0)
    
    def test_2d_index_returns_tensor_row(self):
        result = run("@[[1, 2], [3, 4]][0]")
        assert isinstance(result, PulseTensor)
        np.testing.assert_array_equal(result.array, [1.0, 2.0])
    
    def test_tensor_index_out_of_bounds_errors(self):
        raises_runtime("@[1, 2, 3][10]")

# ----------------------------------------
# 19. Tensor - properties and methods
# ----------------------------------------
class TestTensorMethods:
    def test_transpose(self):
        result = run("@[[1, 2], [3, 4]].T")
        assert isinstance(result, PulseTensor)
        np.testing.assert_array_equal(result.array, [[1.0, 3.0], [2.0, 4.0]])
    
    def test_flatten(self):
        result = run("@[[1, 2], [3, 4]].flatten()")
        assert isinstance(result, PulseTensor)
        np.testing.assert_array_equal(result.array, [1.0, 2.0, 3.0, 4.0])
    
    def test_reshape(self):
        result = run("@[1, 2, 3, 4].reshape(2, 2)")
        assert isinstance(result, PulseTensor)
        assert result.array.shape == (2, 2)
    
    def test_reshape_invalid_errors(self):
        raises_runtime("@[1, 2, 3].reshape(2, 2)", "reshape failed")
    
    def test_sum(self):
        result = run("@[1, 2, 3, 4].sum()")
        assert isinstance(result, PulseNumber)
        assert result.value == pytest.approx(10.0)
    
    def test_mean(self):
        result = run("@[1, 2, 3, 4].mean()")
        assert result.value == pytest.approx(2.5)
    
    def test_max(self):
        result = run("@[3, 1, 4, 1, 5, 9].max()")
        assert result.value == pytest.approx(9.0)
    
    def test_min(self):
        result = run("@[3, 1, 4, 1, 5, 9].min()")
        assert result.value == pytest.approx(1.0)
    
    def test_undefined_property_errors(self):
        raises_runtime("@[1, 2].foo", "no property")
    
    def test_2d_sum(self):
        result = run("@[[1, 2], [3, 4]].sum()")
        assert result.value == pytest.approx(10.0)
    
    def test_2d_mean(self):
        result = run("@[[1, 2], [3, 4]].mean()")
        assert result.value == pytest.approx(2.5)
    
    def test_chained_tensor_ops(self):
        result = run("@[1, 2, 3, 4].reshape(2, 2).sum()")
        assert result.value == pytest.approx(10.0)

# ----------------------------------------
# 20. Tensor - in Pulse program
# ----------------------------------------
class TestTensorInProgram:
    def test_tensor_in_variable(self):
        arr = tensor_result("""
t = @[1, 2, 3]
t
""")
        np.testing.assert_array_equal(arr, [1.0, 2.0, 3.0])
    
    def test_tensor_passed_to_function(self):
        result = run("""
def scale(t, factor):
    return t * factor

scale(@[1, 2, 3], 5)
""")
        assert isinstance(result, PulseTensor)
        np.testing.assert_array_equal(result.array, [5.0, 10.0, 15.0])
    
    def test_tensor_returned_from_function(self):
        result = run("""
def make_tensor():
    return @[10, 20, 30]

make_tensor()
""")
        assert isinstance(result, PulseTensor)
    
    def test_tensor_stored_in_list(self):
        result = run("""
tensors = [@[1, 2], @[3, 4]]
tensors[0]
""")
        assert isinstance(result, PulseTensor)
        np.testing.assert_array_equal(result.array, [1.0, 2.0])
    
    def test_tensor_in_loop_accumulation(self):
        result = run("""
t = @[0, 0, 0]
for i in range(3):
    t = t + @[1, 1, 1]
t.sum()
""")
        assert result.value == pytest.approx(9.0)
    
    def test_matrix_multiply_chain(self):
        result = run("""
a = @[[1, 0], [0, 1]]
b = @[[2, 3], [4, 5]]
c = a @ b
c.sum()
""")
        assert result.value == pytest.approx(14.0)

# ----------------------------------------
# 21. Multi-index and slicing
# ----------------------------------------
class TestMultiIndexAndSlice:
    def test_list_slice(self):
        result = run("[10, 20, 30, 40, 50][1:3]")
        assert isinstance(result, PulseList)
        values = [e.value for e in result.elements]
        assert values == [20.0, 30.0]
    
    def test_list_slice_from_start(self):
        result = run("[1, 2, 3, 4][:2]")
        values = [e.value for e in result.elements]
        assert values == [1.0, 2.0]
    
    def test_list_slice_to_end(self):
        result = run("[1, 2, 3, 4][2:]")
        values = [e.value for e in result.elements]
        assert values == [3.0, 4.0]
    
    def test_list_full_slice(self):
        result = run("[1, 2, 3][:]")
        assert len(result.elements) == 3
    
    def test_string_slice(self):
        result = run('"hello"[1:4]')
        assert isinstance(result, PulseString)
        assert result.value == "ell"
    
    def test_string_slice_from_start(self):
        assert run('"pulse"[:3]').value == "pul"
    
    def test_string_slice_to_end(self):
        assert run('"pulse"[2:]').value == "lse"
    
    def test_tensor_slice_1d(self):
        result = run("@[10, 20, 30, 40, 50][1:3]")
        assert isinstance(result, PulseTensor)
        np.testing.assert_array_equal(result.array, [20.0, 30.0])
    
    def test_tensor_2d_row_slice(self):
        result = run("@[[1,2],[3,4],[5,6]][1:3]")
        assert isinstance(result, PulseTensor)
        assert result.array.shape == (2, 2)
    
    def test_tensor_multi_index_element(self):
        result = run("@[[1, 2], [3, 4]][1, 0]")
        assert isinstance(result, PulseNumber)
        assert result.value == pytest.approx(3.0)
    
    def test_tensor_multi_index_element_row1_col1(self):
        result = run("@[[10, 20], [30, 40]][1, 1]")
        assert result.value == pytest.approx(40.0)
    
    def test_list_multi_index_not_slice_errors(self):
        raises_runtime("[[1,2],[3,4]][0, 1]")
    
    def test_slice_standalone_errors(self):
        raises_syntax("1:3")

# ----------------------------------------
# 22. Pipe operator
# ----------------------------------------
class TestPipeOperator:
    def test_pipe_single_function(self):
        result = run("""
def double(x):
    return x * 2

5 |> double
""")
        assert result.value == 10
    
    def test_pipe_chained(self):
        result = run("""
def double(x):
    return x * 2

def inc(x):
    return x + 1

3 |> double |> inc
""")
        assert result.value == 7
    
    def test_pipe_with_builtin(self):
        result = run("""
[1, 2, 3] |> len
""")
        assert result.value == 3
    
    def test_pipe_passes_tensor(self):
        result = run("""
def total(t):
    return t.sum()

@[1, 2, 3, 4] |> total
""")
        assert result.value == pytest.approx(10.0)
    
    def test_pipe_non_callable_right_errors(self):
        raises_runtime("5 |> 42", "callable")
    
    def test_pipe_preserves_type(self):
        result = run("""
def identity(x):
    return x

"hello" |> identity
""")
        assert isinstance(result, PulseString)
        assert result.value == "hello"
    
    def test_pipe_with_string_method_wrapper(self):
        result = run("""
def shout(s):
    return s.upper()

"hello" |> shout
""")
        assert result.value == "HELLO"

# ----------------------------------------
# 23. Destructuring / unpack expressions
# ----------------------------------------
class TestUnpack:
    def test_basic_unpack(self):
        result = run("""
a, b = [1, 2]
a + b
""")
        assert result.value == 3
    
    def test_unpack_three_values(self):
        result = run("""
x, y, z = [10, 20, 30]
x + y + z
""")
        assert result.value == 60
    
    def test_unpack_strings(self):
        result = run("""
a, b = ["hello", "world"]
b
""")
        assert result.value == "world"
    
    def test_unpack_order_preserved(self):
        result = run("""
first, second, third = [3, 1, 2]
first
""")
        assert result.value == 3
    
    def test_unpack_into_loop(self):
        result = run("""
pairs = [[1, 2], [3, 4], [5, 6]]
total = 0
for pair in pairs:
    a, b = pair
    total = total + a + b
total
""")
        assert result.value == 21
    
    def test_unpack_from_function_return(self):
        result = run("""
def coords():
    return [10, 20]

x, y = coords()
x * y
""")
        assert result.value == 200
    
    def test_unpack_count_mismatch_too_many_vars_errors(self):
        raises_runtime("""
a, b, c = [1, 2]
""", "unpack")
    
    def test_unpack_count_mismatch_too_few_vars_errors(self):
        raises_runtime("""
a, b = [1, 2, 3]
""", "unpack")
    
    def test_unpack_non_list_errors(self):
        raises_runtime("""
a, b = "hello"
""", "unpack")
    
    def test_unpack_tensor_1d(self):
        result = run("""
a, b, c = @[1, 2, 3]
a
""")
        assert isinstance(result, PulseNumber)
        assert result.value == pytest.approx(1.0)
    
    def test_unpack_tensor_rows(self):
        result = run("""
row1, row2 = @[[1, 2], [3, 4]]
row1
""")
        assert isinstance(result, PulseTensor)
        np.testing.assert_array_equal(result.array, [1.0, 2.0])
    
    def test_unpack_variables_are_independent(self):
        result = run("""
a, b = [1, 2]
a = 99
b
""")
        assert result.value == 2

# ----------------------------------------
# 24. Import system errors
# ----------------------------------------
class TestImportErrors:
    def test_import_nonexistent_module_errors(self):
        raises_runtime("import totally_fake_module_xyz", "not found")
    
    def test_import_non_existent_member_errors(self):
        raises_runtime(
            "from math import something_fake",
            "no member"
        )

# ----------------------------------------
# 25. Unbound method call guard
# ----------------------------------------
class TestUnboundMethodGuard:
    def test_calling_instance_method_on_class_without_self_errors(self):
        raises_runtime("""
class Greeter:
    def greet(self):
        return "hello"

Greeter.greet()
""", "self")
    
    def test_calling_static_method_on_class_works(self):
        result = run("""
class Math:
    static def square(n):
        return n * n

Math.square(6)
""")
        assert result.value == 36
    
    def test_calling_instance_method_through_instance_works(self):
        result = run("""
class Counter:
    def __init__(self):
        self.n = 0
    def inc(self):
        self.n = self.n + 1
        return self.n

c = Counter()
c.inc()
c.inc()
""")
        assert result.value == 2

# ----------------------------------------
# 26. Tensor + control flow
# ----------------------------------------
class TestTensorIntegration:
    def test_tensor_in_if_condition_errors_gracefully(self):
        # We just check it doesn't raise a Python-level crash
        try:
            run("""
t = @[1]
if t:
    x = 1
""")
        except PulseRuntimeException:
            pass
    
    def test_tensor_equality_in_if(self):
        result = run("""
a = @[1, 2, 3]
b = @[1, 2, 3]
x = None
if a == b:
    x = "equal"
else:
    x = "not equal"
x
""")
        assert result.value == "equal"
    
    def test_tensor_function_pipeline(self):
        result = run("""
def normalise(t):
    total = t.sum()
    return t * (1 / total)

def check_sum(t):
    return t.sum()

@[1, 1, 1, 1] |> normalise |> check_sum
""")
        assert result.value == pytest.approx(1.0)
    
    def test_tensor_stored_in_dict(self):
        result = run("""
d = {"weights": @[0.1, 0.2, 0.3]}
d["weights"].sum()
""")
        assert result.value == pytest.approx(0.6)
    
    def test_tensor_shape_used_in_arithmetic(self):
        result = run("""
t = @[[1, 2, 3], [4, 5, 6]]
rows = t.shape[0]
cols = t.shape[1]
rows * cols
""")
        assert result.value == 6
    
    def test_unpack_then_matmul(self):
        result = run("""
a, b = [@[[1, 0], [0, 1]], @[[2, 3], [4, 5]]]
(a @ b).sum()
""")
        assert result.value == pytest.approx(14.0)
