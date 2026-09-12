import textwrap
import pytest
from src.values import PulseNumber, PulseString, PulseBoolean, PulseNull, PulseList, PulseDict
from src.runtime import PulseException
from src.environment import Environment
from pulse import run
from src.stdlib import pybridge_module as pb

class FakeInterp:
    def _raise(self, message):
        raise RuntimeError(message)

def run_and_capture(source: str, env: Environment = None):
    captured = []
    
    def output(text, end="\n"):
        captured.append(text)
    
    run(source, output=output, env=env)
    return captured

class TestToPython:
    def setup_method(self):
        self.interp = FakeInterp()
    
    def test_null(self):
        assert pb._to_python(self.interp, PulseNull()) is None
    
    def test_boolean(self):
        assert pb._to_python(self.interp, PulseBoolean(True)) is True
        assert pb._to_python(self.interp, PulseBoolean(False)) is False
    
    def test_number_int(self):
        assert pb._to_python(self.interp, PulseNumber(42)) == 42
    
    def test_number_float(self):
        assert pb._to_python(self.interp, PulseNumber(3.5)) == 3.5
    
    def test_string(self):
        assert pb._to_python(self.interp, PulseString("hi")) == "hi"
    
    def test_list(self):
        pulse_list = PulseList([PulseNumber(1), PulseNumber(2), PulseString("x")])
        assert pb._to_python(self.interp, pulse_list) == [1, 2, "x"]
    
    def test_nested_list(self):
        inner = PulseList([PulseNumber(1), PulseNumber(2)])
        outer = PulseList([inner, PulseNumber(3)])
        assert pb._to_python(self.interp, outer) == [[1, 2], 3]
    
    def test_dict(self):
        pulse_dict = PulseDict({PulseString("a"): PulseNumber(1)})
        assert pb._to_python(self.interp, pulse_dict) == {"a": 1}
    
    def test_unsupported_type_raises(self):
        class Unsupported:
            def type_name(self):
                return "weird"
        with pytest.raises(RuntimeError):
            pb._to_python(self.interp, Unsupported())

class TestToPulse:
    def setup_method(self):
        self.interp = FakeInterp()
    
    def test_none(self):
        result = pb._to_pulse(self.interp, None)
        assert isinstance(result, PulseNull)
    
    def test_bool(self):
        result = pb._to_pulse(self.interp, True)
        assert isinstance(result, PulseBoolean)
        assert result.value is True
    
    def test_int(self):
        result = pb._to_pulse(self.interp, 7)
        assert isinstance(result, PulseNumber)
        assert result.value == 7
    
    def test_float(self):
        result = pb._to_pulse(self.interp, 3.14)
        assert isinstance(result, PulseNumber)
        assert result.value == 3.14
    
    def test_bool_not_mistaken_for_int(self):
        # bool is a subclass of int in Python; must check bool first.
        result = pb._to_pulse(self.interp, False)
        assert isinstance(result, PulseBoolean)
    
    def test_string(self):
        result = pb._to_pulse(self.interp, "hello")
        assert isinstance(result, PulseString)
        assert result.value == "hello"
    
    def test_list(self):
        result = pb._to_pulse(self.interp, [1, 2, 3])
        assert isinstance(result, PulseList)
        assert [e.value for e in result.elements] == [1, 2, 3]
    
    def test_tuple_becomes_list(self):
        result = pb._to_pulse(self.interp, (1, 2))
        assert isinstance(result, PulseList)
    
    def test_dict(self):
        result = pb._to_pulse(self.interp, {"a": 1})
        assert isinstance(result, PulseDict)
        raw = {k.value: v.value for k, v in result.entries.items()}
        assert raw == {"a": 1}
    
    def test_callable_gets_wrapped(self):
        result = pb._to_pulse(self.interp, lambda x: x)
        assert hasattr(result, "call")
    
    def test_unsupported_object_raises(self):
        class Unsupported:
            pass
        with pytest.raises(RuntimeError):
            pb._to_pulse(self.interp, Unsupported())

class TestWrapCallable:
    def setup_method(self):
        self.interp = FakeInterp()
    
    def test_wrapped_function_roundtrips_values(self):
        def double(x):
            return x * 2
        bridged = pb._wrap_callable(self.interp, "double", double)
        result = bridged.call(self.interp, [PulseNumber(21)], {})
        assert isinstance(result, PulseNumber)
        assert result.value == 42
    
    def test_wrapped_function_propagates_python_exception_as_raise(self):
        def boom():
            raise ValueError("bad")
        bridged = pb._wrap_callable(self.interp, "boom", boom)
        with pytest.raises(RuntimeError):
            bridged.call(self.interp, [], {})
    
    def test_wrapped_function_supports_kwargs(self):
        def greet(name, greeting="hello"):
            return f"{greeting}, {name}!"
        bridged = pb._wrap_callable(self.interp, "greet", greet)
        result = bridged.call(
            self.interp, [PulseString("World")], {"greeting": PulseString("hi")}
        )
        assert isinstance(result, PulseString)
        assert result.value == "hi, World!"

class TestImportModuleIntegration:
    def test_import_statistics_and_call_mean(self):
        source = (
            'stats = pybridge.import_module("statistics")\n'
            "print(stats.mean([1, 2, 3, 4]))\n"
        )
        source = "import pybridge\n" + source
        output = run_and_capture(source)
        assert output == ["2.5"]
    
    def test_import_math_module_constant(self):
        source = (
            "import pybridge\n"
            'pymath = pybridge.import_module("math")\n'
            "print(pymath.sqrt(16))\n"
        )
        output = run_and_capture(source)
        assert output == ["4.0"]
    
    def test_import_nonexistent_module_raises_pulse_error(self):
        source = (
            "import pybridge\n"
            'pybridge.import_module("this_module_does_not_exist_12345")\n'
        )
        with pytest.raises(PulseException):
            run_and_capture(source)

class TestLoadFileIntegration:
    def test_load_file_and_call_function(self, tmp_path):
        helper_file = tmp_path / "helpers.py"
        helper_file.write_text(
            textwrap.dedent(
                """
                def add(a, b):
                    return a + b
                def shout(text):
                    return text.upper()
                """
            )
        )
        source = (
            "import pybridge\n"
            f'helpers = pybridge.load_file("{helper_file.as_posix()}")\n'
            "print(helpers.add(2, 3))\n"
            'print(helpers.shout("hi"))\n'
        )
        output = run_and_capture(source)
        assert output == ["5", "HI"]
    
    def test_load_file_missing_path_raises_pulse_error(self):
        source = (
            "import pybridge\n"
            'pybridge.load_file("does_not_exist_12345.py")\n'
        )
        with pytest.raises(PulseException):
            run_and_capture(source)
    
    def test_load_file_with_syntax_error_raises_pulse_error(self, tmp_path):
        bad_file = tmp_path / "broken.py"
        bad_file.write_text("def broken(:\n    pass\n")
        source = (
            "import pybridge\n"
            f'pybridge.load_file("{bad_file.as_posix()}")\n'
        )
        with pytest.raises(PulseException):
            run_and_capture(source)
    
    def test_load_file_function_raising_python_exception_surfaces_as_pulse_error(self, tmp_path):
        helper_file = tmp_path / "faulty.py"
        helper_file.write_text(
            textwrap.dedent(
                """
                def divide(a, b):
                    return a / b
                """
            )
        )
        source = (
            "import pybridge\n"
            f'helpers = pybridge.load_file("{helper_file.as_posix()}")\n'
            "helpers.divide(1, 0)\n"
        )
        with pytest.raises(PulseException):
            run_and_capture(source)
