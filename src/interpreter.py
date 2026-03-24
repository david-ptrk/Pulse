"""
interpreter.py

Implements the interpreter for the Pulse programming language.

The interpreter is responsible for executing programs represented as
Abstract Syntax Trees (AST) produced by the parser. It performs a
tree-walk evaluation, traversing each node of the AST and computing
its corresponding runtime behavior.

This module bridges the gap between static program structure and
dynamic execution. It evaluates expressions, executes statements,
and manages program state through the environment system, which
provides support for lexical scoping, variable storage, and scope
resolution.

The interpreter handles core language features including:
- Evaluation of expressions (literals, variables, binary/unary operations)
- Execution of statements (declarations, assignments, blocks)
- Control flow constructs (conditionals, loops)
- Function definitions and function calls with proper scoping
- Return handling and function execution context
- Class and object behavior (if supported), including instantiation and method calls

The interpreter maintains execution state such as the current environment,
call contexts, and runtime values, ensuring correct scoping and isolation
between different program constructs.

This module primarily provides:
- The Interpreter class, which traverses AST nodes and evaluates them
    using a visitor-based approach
- Runtime evaluation methods corresponding to each AST node type
- Integration with the environment system for variable and scope management
- Mechanisms for handling runtime errors during program execution

The interpreter executes Pulse programs by walking the AST and
producing results or side effects in accordance with the language's
semantics.
"""

from src.expressions import ExprVisitor
from src.statements import StmtVisitor
from src.environment import Environment
from src.error import ReturnException, PulseRuntimeError
from src.function import PulseFunction, PulseNativeFunction
from src.tokens import Token
import math

class Interpreter(ExprVisitor, StmtVisitor):
    def __init__(self, global_environment):
        self.environment = global_environment
        
        # Native Functions
        self.environment.define_many([
            ("print", PulseNativeFunction("print", self.native_print)),
            ("input", PulseNativeFunction("input", self.native_input)),
            ("str", PulseNativeFunction("str", self.native_str)),
            ("int", PulseNativeFunction("int", self.native_int)),
            ("float", PulseNativeFunction("float", self.native_float)),
            ("type", PulseNativeFunction("type", self.native_type)),
            ("abs", PulseNativeFunction("abs", self.native_abs)),
            ("pow", PulseNativeFunction("pow", self.native_pow)),
            ("sqrt", PulseNativeFunction("sqrt", self.native_sqrt)),
            ("min", PulseNativeFunction("min", self.native_min)),
            ("max", PulseNativeFunction("max", self.native_max)),
            ("len", PulseNativeFunction("len", self.native_len)),
        ])
    
    def interpret(self, statements, source):
        """
        Entry point to execute a full AST program.
        'program' is a list of statements or a root node.
        """
        self.source = source

        result = None
        for stmt in statements:
            result = self.execute(stmt)
        return result
    
    def execute(self, stmt):
        return stmt.accept(self)
    
    def evaluate(self, expr):
        return expr.accept(self)
    
    def runtime_error(self, token: Token, message: str):
        raise PulseRuntimeError(message, token=token, context_source=self.source)
    
    # Native Functions
    def native_print(self, *args):
        output = " ".join(str(arg) for arg in args)
        print(output)
        return None
    
    def native_input(self, prompt=""):
        return input(prompt)
    
    def native_str(self, x):
        return str(x)
    
    def native_int(self, x):
        try:
            return int(x)
        except:
            raise PulseRuntimeError("Invalid conversion to int")
    
    def native_float(self, x):
        try:
            return float(x)
        except:
            raise PulseRuntimeError("Invalid conversion to float")
    
    def native_type(self, obj):
        if isinstance(obj, int):
            return "int"
        if isinstance(obj, float):
            return "float"
        if isinstance(obj, str):
            return "string"
        if obj is None:
            return "null"
        return "object"
    
    def native_abs(self, x):
        return abs(x)
    
    def native_pow(self, base, exp):
        return pow(base, exp)
    
    def native_sqrt(self, x):
        try:
            return math.sqrt(x)
        except:
            raise PulseRuntimeError("Cannot take square root of negative values")
    
    def native_min(self, *args):
        return min(args)
    
    def native_max(self, *args):
        return max(args)
    
    def native_len(self, x):
        return len(x)
    
    def visit_expression_stmt(self, stmt):
        self.evaluate(stmt.expression)
        return None
    
    def visit_literal_expr(self, expr):
        return expr.value
    
    def visit_variable_expr(self, expr):
        return self.environment.get(expr.name.lexeme)
    
    def visit_assign_expr(self, expr):
        value = self.evaluate(expr.value)
        self.environment.assign(expr.name.lexeme, value)
        return value
    
    def visit_grouping_expr(self, expr):
        return self.evaluate(expr.expression)
    
    def visit_unary_expr(self, expr):
        right = self.evaluate(expr.right)
        operator = expr.operator.lexeme
        
        if operator == '-':
            if isinstance(right, (int, float)):
                return -right
            raise PulseRuntimeError("Unary '-' requires a number")
        if operator == '!':
            return not self.is_truthy(right)
        
        raise PulseRuntimeError(f"Unknown unary operator: {operator}")
    
    def visit_binary_expr(self, expr):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)
        operator = expr.operator.lexeme
        
        if operator == '+':
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return left + right
            if isinstance(left, str) and isinstance(right, str):
                return left + right
            raise PulseRuntimeError("Operands must be two numbers or two strings")
        elif operator == '-':
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return left - right
            self.runtime_error(expr.operator, "Operands must be two numbers")
        elif operator == '*':
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return left * right
            raise PulseRuntimeError("Operands must be two numbers")
        elif operator == '/':
            if right == 0:
                raise PulseRuntimeError("Division by zero. Divisor cannot be zero")
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return left / right
            raise PulseRuntimeError("Operands must be two numbers")
        
        elif operator == '==':
            return left == right
        elif operator == '!=':
            return left != right
        elif operator == '<':
            return left < right
        elif operator == '<=':
            return left <= right
        elif operator == '>':
            return left > right
        elif operator == '>=':
            return left >= right
        
        raise PulseRuntimeError(f"Unknown binary operator: {operator}")
    
    def visit_logical_expr(self, expr):
        left = self.evaluate(expr.left)
        operator = expr.operator.lexeme
        
        if operator == "or":
            if self.is_truthy(left):
                return left
            return self.evaluate(expr.right)
        
        if operator == "and":
            if not self.is_truthy(left):
                return left
            return self.evaluate(expr.right)
        
        raise PulseRuntimeError(f"Unknown logical operator: {operator}")
    
    def visit_block_stmt(self, stmt):
        previous = self.environment
        self.environment = Environment(enclosing=previous)
        
        try:
            result = None
            for s in stmt.statements:
                result = self.execute(s)
            return result
        finally:
            self.environment = previous
    
    def visit_if_stmt(self, stmt):
        if self.is_truthy(self.evaluate(stmt.condition)):
            return self.execute(stmt.then_branch)
        
        for cond, branch in stmt.elif_branches:
            if self.is_truthy(self.evaluate(cond)):
                return self.execute(branch)
        
        if stmt.else_branch:
            return self.execute(stmt.else_branch)
        
        return None
    
    def visit_while_stmt(self, stmt):
        while self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)
        return None
    
    def visit_return_stmt(self, stmt):
        value = None
        if stmt.value:
            value = self.evaluate(stmt.value)
        raise ReturnException(value)
    
    def is_truthy(self, value):
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        return True
    
    def visit_call_expr(self, expr):
        callee = self.evaluate(expr.callee)
        arguments = [self.evaluate(arg) for arg in expr.arguments]
        
        if not callable(getattr(callee, "call", None)):
            raise PulseRuntimeError("Attempted to call a non-function")
        
        return callee.call(self, arguments)
    
    def visit_break_stmt(self, stmt):
        raise PulseRuntimeError("break not implemented yet")
    
    def visit_continue_stmt(self, stmt):
        raise PulseRuntimeError("continue not implemented yet")
    
    def visit_for_stmt(self, stmt):
        raise PulseRuntimeError("for loop not implemented yet")
    
    def visit_function_stmt(self, stmt):
        raise PulseRuntimeError("function not implemented yet")
    
    def visit_class_stmt(self, stmt):
        raise PulseRuntimeError("class not implemented yet")
    
    def visit_memberaccess_expr(self, expr):
        raise PulseRuntimeError("member access not implemented yet")
    
    def visit_pass_stmt(self, stmt):
        return None
    
    def visit_try_stmt(self, stmt):
        raise PulseRuntimeError("try/catch not implemented yet")