# Pulse Example Programs

This document lists example programs written in Pulse pseudo-code.  
These examples demonstrate the core syntax, language constructs, and AI-specific operations of Pulse.  
Each file is self-contained and includes a one-line description of expected behavior.

## Examples

| File                       | Description                                           |
| -------------------------- | ----------------------------------------------------- |
| 01_variables.pul           | Variable assignment and basic arithmetic              |
| 02_arithmetic.pul          | Demonstrates arithmetic operations (+, -, \*, /)      |
| 03_print.pul               | Console output using print()                          |
| 04_functions.pul           | Defining and calling simple functions                 |
| 05_if_else.pul             | Basic if/else conditional statements                  |
| 06_if_elif_else.pul        | Multi-branch if/elif/else statements                  |
| 07_while_loop.pul          | while loop demonstration                              |
| 08_for_loop.pul            | for loop demonstration                                |
| 09_tensor_creation.pul     | Creating tensors and initializing values              |
| 10_tensor_operations.pul   | Basic tensor operations (add, multiply, element-wise) |
| 11_dot_product.pul         | Dot product between tensors example                   |
| 12_matrix_creation.pul     | Creating matrices via matrix() wrapper                |
| 13_matrix_mul.pul          | Basic matrix multiplication and operations            |
| 14_simple_model_train.pul  | Defining a simple class and training method           |
| 15_model_predict.pul       | Using class methods to make predictions               |
| 16_nested_if.pul           | Nested if statements example                          |
| 17_chained_operations.pul  | Chained arithmetic and tensor operations              |
| 18_tensor_indexing.pul     | Indexing into tensors and accessing elements          |
| 19_tensor_slice.pul        | Slicing tensors for subarrays                         |
| 20_tensor_reshape.pul      | Reshaping tensors to different dimensions             |
| 21_model_eval.pul          | Evaluating models and running predictions             |
| 22_break_continue_pass.pul | Loop control: break, continue, and pass statements    |
| 23_recursion.pul           | Recursive function examples                           |
| 24_class_basic.pul         | Defining basic classes with attributes and methods    |
| 25_class_inheritance.pul   | Class inheritance and method overriding               |
| 26_console_io.pul          | Console input and output demonstration                |
| 27_file_io.pul             | File reading and writing example                      |
| 28_exception_handling.pul  | Handling exceptions using try/except blocks           |

## Usage

To run an example, execute the Pulse interpreter with the file:

```bash
$ pulse examples/01_variables.pul
```

## Notes

- All examples follow Pythonic syntax for readability.
- Tensor and matrix operations demonstrate AI-specific language constructs.
- Some examples include expected output in comments at the top of the file.
