import pytest
from src.error import PulseError, PulseRuntimeError, PulseSyntaxError
from src.environment import Environment
from pulse import run
from src.runtime import PulseException

def run_and_capture(source: str, env: Environment = None):
    captured = []
    
    def output(text, end="\n"):
        captured.append(text)
    
    run(source, output=output, env=env)
    return captured

def run_program(source: str, env: Environment = None):
    if env is None:
        env = Environment()
    run (source, env=env)
    return env

class TestBasicProgram:
    def test_hello_world(self):
        output = run_and_capture('print("Hello, world!")\n')
        assert output == ["Hello, world!"]
    
    def test_arithmetic_output(self):
        output = run_and_capture("print(2 + 3 * 4)\n")
        assert output == ["14"]
    
    def test_variable_assignment_and_print(self):
        source = (
            "age = 21\n"
            "print(age)\n"
        )
        output = run_and_capture(source)
        assert output == ["21"]
    
    def test_fstring_output(self):
        source = (
            'name = "Pulse"\n'
            'print(f"Hello, {name}!")\n'
        )
        output = run_and_capture(source)
        assert output == ["Hello, Pulse!"]
    
    def test_multiple_prints_preserve_order(self):
        source = (
            'print("first")\n'
            'print("second")\n'
            'print("third")\n'
        )
        output = run_and_capture(source)
        assert output == ["first", "second", "third"]

class TestControlFlowPrograms:
    def test_if_else_branch_taken(self):
        source = (
            "age = 12\n"
            "if age >= 18:\n"
            '    print("adult")\n'
            "else:\n"
            '    print("young")\n'
        )
        output = run_and_capture(source)
        assert output == ["young"]
    
    def test_while_loop_accumulates(self):
        source = (
            "total = 0\n"
            "i = 1\n"
            "while i <= 5:\n"
            "    total += i\n"
            "    i += 1\n"
            "print(total)\n"
        )
        output = run_and_capture(source)
        assert output == ["15"]
    
    def test_for_loop_over_list(self):
        source = (
            "for item in [1, 2, 3]:\n"
            "    print(item)\n"
        )
        output = run_and_capture(source)
        assert output == ["1", "2", "3"]
    
    def test_break_stops_loop(self):
        source = (
            "for i in [1, 2, 3, 4, 5]:\n"
            "    if i == 3:\n"
            "        break\n"
            "    print(i)\n"
        )
        output = run_and_capture(source)
        assert output == ["1", "2"]
    
    def test_continue_skips_iterations(self):
        source = (
            "for i in [1, 2, 3, 4]:\n"
            "    if i % 2 == 0:\n"
            "        continue\n"
            "    print(i)\n"
        )
        output = run_and_capture(source)
        assert output == ["1", "3"]

class TestFunctionPrograms:
    def test_function_return_value(self):
        source = (
            "def add(a, b):\n"
            "    return a + b\n"
            "\n"
            "print(add(2, 3))\n"
        )
        output = run_and_capture(source)
        assert output == ["5"]
    
    def test_function_with_default_argument(self):
        source = (
            'def greet(name, msg="hello"):\n'
            '    print(f"{msg}, {name}!")\n'
            "\n"
            'greet("World")\n'
        )
        output = run_and_capture(source)
        assert output == ["hello, World!"]
    
    def test_recursive_function(self):
        source = (
            "def factorial(n):\n"
            "    if n <= 1:\n"
            "        return 1\n"
            "    return n * factorial(n - 1)\n"
            "\n"
            "print(factorial(5))\n"
        )
        output = run_and_capture(source)
        assert output == ["120"]
    
    def test_varargs_function(self):
        source = (
            "def sum_all(*args):\n"
            "    total = 0\n"
            "    for n in args:\n"
            "        total += n\n"
            "    return total\n"
            "\n"
            "print(sum_all(1, 2, 3, 4))\n"
        )
        output = run_and_capture(source)
        assert output == ["10"]
    
    def test_lambda_usage(self):
        source = (
            "double = lambda x: x * 2\n"
            "print(double(21))\n"
        )
        output = run_and_capture(source)
        assert output == ["42"]
    
    def test_closure_captures_outer_variable(self):
        source = (
            "def make_counter():\n"
            "    count = 0\n"
            "    def increment():\n"
            "        count += 1\n"
            "        return count\n"
            "    return increment\n"
            "\n"
            "counter = make_counter()\n"
            "print(counter())\n"
            "print(counter())\n"
        )
        output = run_and_capture(source)
        assert output == ["1", "2"]

class TestClassPrograms:
    def test_class_instantiation_and_method_call(self):
        source = (
            "class Animal:\n"
            "    def __init__(self, name):\n"
            "        self.name = name\n"
            "    def speak(self):\n"
            '        print(f"{self.name} speaks")\n'
            "\n"
            'a = Animal("Rex")\n'
            "a.speak()\n"
        )
        output = run_and_capture(source)
        assert output == ["Rex speaks"]
    
    def test_class_inheritance_overrides_method(self):
        source = (
            "class Animal:\n"
            "    def __init__(self, name):\n"
            "        self.name = name\n"
            "    def speak(self):\n"
            '        print(f"{self.name} makes a sound")\n'
            "\n"
            "class Dog(Animal):\n"
            "    def speak(self):\n"
            '        print(f"{self.name} barks")\n'
            "\n"
            'd = Dog("Fido")\n'
            "d.speak()\n"
        )
        output = run_and_capture(source)
        assert output == ["Fido barks"]

class TestDataStructurePrograms:
    def test_list_mutation_methods(self):
        source = (
            "nums = [3, 1, 4, 1, 5]\n"
            "nums.append(9)\n"
            "nums.sort()\n"
            "print(nums)\n"
        )
        output = run_and_capture(source)
        assert output == ["[1, 1, 3, 4, 5, 9]"]
    
    def test_dict_access_and_methods(self):
        source = (
            'd = {"a": 1, "b": 2}\n'
            'print(d["a"])\n'
            'print(d.has("c"))\n'
        )
        output = run_and_capture(source)
        assert output == ["1", "False"]
    
    def test_list_comprehension(self):
        source = (
            "squares = [x * x for x in [1, 2, 3, 4]]\n"
            "print(squares)\n"
        )
        output = run_and_capture(source)
        assert output == ["[1, 4, 9, 16]"]
    
    def test_string_methods(self):
        source = (
            '"  Hello World  ".trim().lower()\n'
            's = "  Hello World  ".trim().lower()\n'
            "print(s)\n"
        )
        output = run_and_capture(source)
        assert output == ["hello world"]

class TestErrorPrograms:
    def test_undefined_variable_raises_runtime_error(self):
        with pytest.raises(PulseException):
            run_and_capture("print(does_not_exist)\n")
    
    def test_syntax_error_on_malformed_program(self):
        with pytest.raises(PulseSyntaxError):
            run_and_capture("if x\n    print(1)\n")
    
    def test_division_by_zero_raises(self):
        with pytest.raises(PulseException):
            run_and_capture("print(1 / 0)\n")
    
    def test_calling_non_function_raises(self):
        with pytest.raises(PulseException):
            run_and_capture("x = 5\nx()\n")
    
    def test_try_except_recovers_from_runtime_error(self):
        source = (
            "try:\n"
            "    x = 1 / 0\n"
            "except:\n"
            '    print("caught")\n'
        )
        output = run_and_capture(source)
        assert output == ["caught"]
    
    def test_raise_and_catch_custom_message(self):
        source = (
            "try:\n"
            '    raise ValueError("bad input")\n'
            "except ValueError as e:\n"
            "    print(e)\n"
        )
        output = run_and_capture(source)
        assert len(output) == 1
        assert "bad input" in output[0]

class TestSequentialExecution:
    def test_state_persists_across_multiple_run_calls_with_shared_env(self):
        env = run_program("age = 12\n")
        output = run_and_capture("age = age + 1\nprint(age)\n", env=env)
        assert output == ["13"]
    
    def test_function_defined_in_one_run_usable_in_next(self):
        env = run_program(
            "def square(x):\n"
            "    return x * x\n"
        )
        output = run_and_capture("print(square(6))\n", env=env)
        assert output == ["36"]

class TestTensorPrograms:
    def test_tensor_literal_and_shape(self):
        source = (
            "t = @[[1, 2, 3], [4, 5, 6]]\n"
            "print(t.shape)\n"
        )
        output = run_and_capture(source)
        assert len(output) == 1
    
    def test_tensor_addition(self):
        source = (
            "a = @[[1, 2], [3, 4]]\n"
            "b = @[[1, 1], [1, 1]]\n"
            "print(a + b)\n"
        )
        output = run_and_capture(source)
        assert len(output) == 1
