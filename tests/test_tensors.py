import pytest
import numpy as np
from src.lexer import Lexer
from src.parser import Parser
from src.interpreter import Interpreter
from src.environment import Environment
from src.resolver import Resolver
from src.runtime import PulseRuntimeException
from src.error import PulseRuntimeError
from src.values import PulseNumber, PulseString, PulseBoolean, PulseList, PulseTensor
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
# 1. Tensor Creation
# ----------------------------------------
class TestTensorCreation:
    def test_1d_tensor(self):
        result = run("@[1, 2, 3]")
        assert isinstance(result, PulseTensor)
        assert np.array_equal(result.array, np.array([1.0, 2.0, 3.0]))
    
    def test_2d_tensor(self):
        result = run("@[[1, 2], [3, 4]]")
        assert isinstance(result, PulseTensor)
        assert np.array_equal(result.array, np.array([[1.0, 2.0], [3.0, 4.0]]))

    def test_3d_tensor(self):
        result = run("@[[[1, 2], [3, 4]], [[5, 6], [7, 8]]]")
        assert isinstance(result, PulseTensor)
        assert result.array.shape == (2, 2, 2)

    def test_float_values(self):
        result = run("@[1.5, 2.5, 3.5]")
        assert isinstance(result, PulseTensor)
        assert np.allclose(result.array, [1.5, 2.5, 3.5])

    def test_single_element(self):
        result = run("@[42]")
        assert isinstance(result, PulseTensor)
        assert result.array[0] == 42.0

    def test_type_name(self):
        result = run("@[1, 2, 3]")
        assert result.type_name() == "tensor"

# ----------------------------------------
# 2. Tensor repr
# ----------------------------------------
class TestTensorRepr:
    def test_1d_repr(self):
        result = run("@[1, 2, 3]")
        assert repr(result) == "@[1.0, 2.0, 3.0]"

    def test_2d_repr(self):
        result = run("@[[1, 2], [3, 4]]")
        assert repr(result) == "@[[1.0, 2.0], [3.0, 4.0]]"

    def test_scalar_repr(self):
        # dot product of 1D tensors → scalar, no @ prefix
        result = run("@[1, 2] @ @[3, 4]")
        assert repr(result) == "11.0"

# ----------------------------------------
# 3. Tensor Properties
# ----------------------------------------
class TestTensorProperties:
    def test_shape_1d(self):
        result = run("@[1, 2, 3].shape")
        assert isinstance(result, PulseList)
        assert [e.value for e in result.elements] == [3]

    def test_shape_2d(self):
        result = run("@[[1, 2], [3, 4]].shape")
        assert isinstance(result, PulseList)
        assert [e.value for e in result.elements] == [2, 2]

    def test_ndim_1d(self):
        result = run("@[1, 2, 3].ndim")
        assert isinstance(result, PulseNumber)
        assert result.value == 1

    def test_ndim_2d(self):
        result = run("@[[1, 2], [3, 4]].ndim")
        assert isinstance(result, PulseNumber)
        assert result.value == 2

    def test_size(self):
        result = run("@[[1, 2], [3, 4]].size")
        assert isinstance(result, PulseNumber)
        assert result.value == 4

    def test_dtype(self):
        result = run("@[1, 2, 3].dtype")
        assert isinstance(result, PulseString)
        assert "float" in result.value

    def test_transpose(self):
        result = run("@[[1, 2], [3, 4]].T")
        assert isinstance(result, PulseTensor)
        assert np.array_equal(result.array, np.array([[1.0, 3.0], [2.0, 4.0]]))

    def test_unknown_property(self):
        raises_runtime("@[1, 2].unknown", "no property")

# ----------------------------------------
# 4. Element-wise Operations
# ----------------------------------------
class TestTensorElementwise:
    def test_add(self):
        result = run("@[1, 2, 3] + @[4, 5, 6]")
        assert isinstance(result, PulseTensor)
        assert np.array_equal(result.array, [5.0, 7.0, 9.0])

    def test_subtract(self):
        result = run("@[4, 5, 6] - @[1, 2, 3]")
        assert isinstance(result, PulseTensor)
        assert np.array_equal(result.array, [3.0, 3.0, 3.0])

    def test_multiply(self):
        result = run("@[2, 3, 4] * @[2, 2, 2]")
        assert isinstance(result, PulseTensor)
        assert np.array_equal(result.array, [4.0, 6.0, 8.0])

    def test_divide(self):
        result = run("@[4.0, 6.0, 8.0] / @[2.0, 2.0, 2.0]")
        assert isinstance(result, PulseTensor)
        assert np.allclose(result.array, [2.0, 3.0, 4.0])

    def test_2d_add(self):
        result = run("@[[1, 2], [3, 4]] + @[[5, 6], [7, 8]]")
        assert isinstance(result, PulseTensor)
        assert np.array_equal(result.array, [[6.0, 8.0], [10.0, 12.0]])

    def test_2d_multiply(self):
        result = run("@[[1, 2], [3, 4]] * @[[2, 2], [2, 2]]")
        assert isinstance(result, PulseTensor)
        assert np.array_equal(result.array, [[2.0, 4.0], [6.0, 8.0]])

# ----------------------------------------
# 5. Matrix Multiplication
# ----------------------------------------
class TestTensorMatmul:
    def test_dot_product_1d(self):
        # 1D @ 1D → scalar
        result = run("@[1, 2] @ @[3, 4]")
        assert isinstance(result, PulseTensor)
        assert result.array.tolist() == 11.0

    def test_matmul_2d(self):
        # 2D @ 2D → 2D
        result = run("@[[1, 2], [3, 4]] @ @[[5, 6], [7, 8]]")
        assert isinstance(result, PulseTensor)
        assert np.array_equal(result.array, [[19.0, 22.0], [43.0, 50.0]])

    def test_matmul_stored(self):
        result = run("""
X = @[[1, 0], [0, 1]]
Y = @[[5, 6], [7, 8]]
X @ Y
""")
        assert isinstance(result, PulseTensor)
        assert np.array_equal(result.array, [[5.0, 6.0], [7.0, 8.0]])

# ----------------------------------------
# 6. Equality
# ----------------------------------------
class TestTensorEquality:
    def test_equal_tensors(self):
        result = run("@[1, 2, 3] == @[1, 2, 3]")
        assert isinstance(result, PulseBoolean)
        assert result.value is True

    def test_not_equal_tensors(self):
        result = run("@[1, 2, 3] != @[1, 2, 4]")
        assert isinstance(result, PulseBoolean)
        assert result.value is True

    def test_different_shapes_not_equal(self):
        result = run("@[1, 2] != @[1, 2, 3]")
        assert isinstance(result, PulseBoolean)
        assert result.value is True

# ----------------------------------------
# 7. Variable Assignment
# ----------------------------------------
class TestTensorVariables:
    def test_assign_and_use(self):
        result = run("""
X = @[1, 2, 3]
Y = @[4, 5, 6]
X + Y
""")
        assert isinstance(result, PulseTensor)
        assert np.array_equal(result.array, [5.0, 7.0, 9.0])

    def test_chain_ops(self):
        result = run("""
A = @[1, 2, 3]
B = @[1, 1, 1]
C = A + B
C * @[2, 2, 2]
""")
        assert isinstance(result, PulseTensor)
        assert np.array_equal(result.array, [4.0, 6.0, 8.0])

# ----------------------------------------
# 8. Error Cases
# ----------------------------------------
class TestTensorErrors:
    def test_shape_mismatch_add(self):
        raises_runtime("@[1, 2] + @[1, 2, 3]", "tensor operation failed")

    # def test_tensor_plus_number(self):
    #     raises_runtime("@[1, 2] + 5", "both operands must be tensors")

    # def test_number_plus_tensor(self):
    #     raises_runtime("5 + @[1, 2]", "both operands must be tensors")

    def test_tensor_plus_string(self):
        raises_runtime('@[1, 2] + "hello"', "both operands must be tensors")

# ----------------------------------------
# 9. Scalar-Tensor Operations
# ----------------------------------------
class TestScalarTensorOps:
    def test_tensor_plus_scalar(self):
        result = run("@[1, 2, 3] + 10")
        assert isinstance(result, PulseTensor)
        assert np.array_equal(result.array, [11.0, 12.0, 13.0])

    def test_tensor_minus_scalar(self):
        result = run("@[4, 5, 6] - 1")
        assert isinstance(result, PulseTensor)
        assert np.array_equal(result.array, [3.0, 4.0, 5.0])

    def test_tensor_multiply_scalar(self):
        result = run("@[1, 2, 3] * 2")
        assert isinstance(result, PulseTensor)
        assert np.array_equal(result.array, [2.0, 4.0, 6.0])

    def test_scalar_multiply_tensor(self):
        result = run("2 * @[1, 2, 3]")
        assert isinstance(result, PulseTensor)
        assert np.array_equal(result.array, [2.0, 4.0, 6.0])

    def test_tensor_divide_scalar(self):
        result = run("@[2, 4, 6] / 2")
        assert isinstance(result, PulseTensor)
        assert np.allclose(result.array, [1.0, 2.0, 3.0])

    def test_scalar_divide_by_zero(self):
        raises_runtime("@[1, 2, 3] / 0", "division by zero")

# ----------------------------------------
# 10. Tensor Methods
# ----------------------------------------
class TestTensorMethods:
    def test_sum(self):
        result = run("@[[1, 2], [3, 4]].sum()")
        assert isinstance(result, PulseNumber)
        assert result.value == 10.0

    def test_mean(self):
        result = run("@[[1, 2], [3, 4]].mean()")
        assert isinstance(result, PulseNumber)
        assert result.value == 2.5

    def test_max(self):
        result = run("@[[1, 2], [3, 4]].max()")
        assert isinstance(result, PulseNumber)
        assert result.value == 4.0

    def test_min(self):
        result = run("@[[1, 2], [3, 4]].min()")
        assert isinstance(result, PulseNumber)
        assert result.value == 1.0

    def test_flatten(self):
        result = run("@[[1, 2], [3, 4]].flatten()")
        assert isinstance(result, PulseTensor)
        assert np.array_equal(result.array, [1.0, 2.0, 3.0, 4.0])

    def test_reshape_to_flat(self):
        result = run("@[[1, 2], [3, 4]].reshape(4)")
        assert isinstance(result, PulseTensor)
        assert np.array_equal(result.array, [1.0, 2.0, 3.0, 4.0])

    def test_reshape_to_2d(self):
        result = run("@[1, 2, 3, 4].reshape(2, 2)")
        assert isinstance(result, PulseTensor)
        assert np.array_equal(result.array, [[1.0, 2.0], [3.0, 4.0]])

    def test_reshape_invalid(self):
        raises_runtime("@[1, 2, 3].reshape(2, 2)", "reshape failed")