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
    
