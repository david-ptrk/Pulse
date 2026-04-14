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
from src.error import PulseRuntimeError
import src.runtime as runtime
from src.tokens import Token
from src.function import PulseFunction, PulseNativeFunction
import math
from src.runtime import PulseClass, PulseInstance
from src.values import PulseNumber, PulseString, PulseNull, PulseList, PulseBoolean, PulseDict, PulseRange

class Interpreter(ExprVisitor, StmtVisitor):
    def __init__(self, global_environment):
        self.environment = global_environment
        self.locals = {}
        self.source = ""
        
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
            ("range", PulseNativeFunction("range", self.native_range)),
            ("round", PulseNativeFunction("round", self.native_round)),
            ("floor", PulseNativeFunction("floor", self.native_floor)),
            ("ceil", PulseNativeFunction("ceil", self.native_ceil)),
        ])
        
        self.environment.define_many([
            ("Exception", runtime.PulseException),
            ("RuntimeError", runtime.PulseRuntimeException),
            ("ValueError", runtime.PulseValueError),
            ("TypeError", runtime.PulseTypeError),
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
    
    def resolve(self, expr, depth):
        self.locals[expr] = depth
    
    def runtime_error(self, token=None, message=None):
        raise runtime.PulseRuntimeException(
            PulseRuntimeError(message, token=token, context_source=self.source)
        )
    
    def pulse_stringify(self, val) -> str:
        if isinstance(val, PulseInstance):
            for magic in ("__str__", "__repr__"):
                method = val.klass.find_method(magic)
                if method is not None:
                    result = method.bind(val).call(self, [], {})
                    return repr(result) if result is not None else "null"
        return repr(val)
    
    # Native Functions
    def native_print(self, *args, **kwargs):
        sep = str(kwargs.get("sep", " "))
        end = str(kwargs.get("end", "\n"))
        
        output = sep.join(self.pulse_stringify(arg) for arg in args)
        print(output, end=end)
        return None
    
    def native_input(self, prompt=""):
        return input(prompt)
    
    def native_str(self, x):
        return PulseString(repr(x))
    
    def native_int(self, x):
        if isinstance(x, PulseNumber):
            return x
        
        if isinstance(x, PulseString):
            try:
                return PulseNumber(int(x.value))
            except:
                self.runtime_error(message="Invalid conversion to int")
        
        self.runtime_error(message="Invalid type for int()")
    
    def native_float(self, x):
        if isinstance(x, PulseNumber):
            return x
        
        if isinstance(x, PulseString):
            try:
                return PulseNumber(float(x.value))
            except:
                self.runtime_error(message="Invalid conversion to float")
        
        self.runtime_error(message="Invalid type for float()")
    
    def native_type(self, obj):
        return PulseString(obj.type_name())
    
    def native_abs(self, x):
        if isinstance(x, PulseNumber):
            return PulseNumber(abs(x.value))
        self.runtime_error(message="abs() expects number")
    
    def native_pow(self, base, exp):
        if isinstance(base, PulseNumber) and isinstance(exp, PulseNumber):
            return PulseNumber(pow(base.value, exp.value))
        self.runtime_error(message="pow() expects numbers")
    
    def native_sqrt(self, x):
        if isinstance(x, PulseNumber):
            if x.value < 0:
                self.runtime_error(message="Cannot take square root of negative values")
            return PulseNumber(math.sqrt(x.value))
        
        self.runtime_error(message="sqrt() expects number")
    
    def native_min(self, *args):
        if not all(isinstance(a, PulseNumber) for a in args):
            self.runtime_error(message="min() expects numbers")
        return PulseNumber(min(a.value for a in args))
    
    def native_max(self, *args):
        if not all(isinstance(a, PulseNumber) for a in args):
            self.runtime_error(message="max() expects numbers")
        return PulseNumber(max(a.value for a in args))
    
    def native_len(self, x):
        if isinstance(x, PulseList):
            return PulseNumber(len(x.elements))        
        if isinstance(x, PulseString):
            return PulseNumber(len(x.value))
        if isinstance(x, PulseDict):
            return PulseNumber(len(x.entries))
        if isinstance(x, PulseRange):
            return PulseNumber(len(x))
        
        self.runtime_error(message="Object has no length")
    
    def native_range(self, *args):
        int_args = []
        for a in args:
            if not isinstance(a, PulseNumber):
                self.runtime_error(message="range() expects numbers")
            int_args.append(int(a.value))
        
        if len(int_args) == 1:
            return PulseRange(0, int_args[0])
        if len(int_args) == 2:
            return PulseRange(int_args[0], int_args[1])
        if len(int_args) == 3:
            if int_args[2] == 0:
                self.runtime_error(message="range() step cannot be zero")
            return PulseRange(int_args[0], int_args[1], int_args[2])
        
        self.runtime_error(message="range() expects 1, 2, or 3, arguments")
    
    def native_round(self, x, digits=None):
        if not isinstance(x, PulseNumber):
            self.runtime_error(message="round() expects a number")
        if digits is None:
            return PulseNumber(round(x.value))
        if not isinstance(digits, PulseNumber):
            self.runtime_error(message="round() digits must be a number")
        return PulseNumber(round(x.value, int(digits.value)))
    
    def native_floor(self, x):
        if not isinstance(x, PulseNumber):
            self.runtime_error(message="floor() expects a number")
        return PulseNumber(math.floor(x.value))
    
    def native_ceil(self, x):
        if not isinstance(x, PulseNumber):
            self.runtime_error(message="ceil() expects a number")
        return PulseNumber(math.ceil(x.value))
    
    # Visit Functions
    def visit_expression_stmt(self, stmt):
        self.evaluate(stmt.expression)
    
    def visit_literal_expr(self, expr):
        value = expr.value
        
        if isinstance(value, bool):
            return PulseBoolean(value)
        if isinstance(value, (int, float)):
            return PulseNumber(value)
        if isinstance(value, str):
            return PulseString(value)
        if value is None:
            return PulseNull()
        
        return value
    
    def visit_variable_expr(self, expr):
        if expr.name.lexeme == "self":
            return self.environment.get("self")
        
        distance = self.locals.get(expr)
        if distance is not None:
            return self.environment.get_at(distance, expr.name.lexeme)
        return self.environment.get(expr.name.lexeme)
    
    def visit_assign_expr(self, expr):
        value = self.evaluate(expr.value)
        distance = self.locals.get(expr)
        if distance is not None:
            self.environment.assign_at(distance, expr.name.lexeme, value)
            return value
        
        try:
            self.environment.assign(expr.name.lexeme, value)
        except PulseRuntimeError:
            self.environment.define(expr.name.lexeme, value)
        
        return value
    
    def visit_grouping_expr(self, expr):
        return self.evaluate(expr.expression)
    
    def visit_unary_expr(self, expr):
        right = self.evaluate(expr.right)
        operator = expr.operator.lexeme
        
        if operator == '-':
            if isinstance(right, PulseNumber):
                return PulseNumber(-right.value)
            self.runtime_error(expr.operator, "Unary '-' requires a number")
        
        if operator == '!':
            return PulseBoolean(not right.is_truthy())
        
        self.runtime_error(expr.operator, f"Unknown unary operator: {operator}")
    
    def visit_binary_expr(self, expr):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)
        operator = expr.operator.lexeme
        
        if operator == '+':
            if isinstance(left, PulseNumber) and isinstance(right, PulseNumber):
                return PulseNumber(left.value + right.value)
            
            if isinstance(left, PulseString) and isinstance(right, PulseString):
                return PulseString(left.value + right.value)
            
            self.runtime_error(expr.operator, "Operands must be two numbers or two strings")
        elif operator == '-':
            if isinstance(left, PulseNumber) and isinstance(right, PulseNumber):
                return PulseNumber(left.value - right.value)
            
            self.runtime_error(expr.operator, "Operands must be two numbers")
        elif operator == '*':
            if isinstance(left, PulseNumber) and isinstance(right, PulseNumber):
                return PulseNumber(left.value * right.value)
            
            self.runtime_error(expr.operator, "Operands must be two numbers")
        elif operator == '/':
            if right.value == 0:
                self.runtime_error(expr.operator, "Division by zero. Divisor cannot be zero")
            if isinstance(left, PulseNumber) and isinstance(right, PulseNumber):
                return PulseNumber(left.value / right.value)
            
            self.runtime_error(expr.operator, "Operands must be two numbers")
        elif operator == '%':
            if isinstance(left, PulseNumber) and isinstance(right, PulseNumber):
                if right.value == 0:
                    self.runtime_error(expr.operator, "Modulo by zero")
                return PulseNumber(left.value % right.value)
            self.runtime_error(expr.operator, "Operands must be two numbers")
        elif operator == '//':
            if isinstance(left, PulseNumber) and isinstance(right, PulseNumber):
                if right.value == 0:
                    self.runtime_error(expr.operator, "Integer division by zero")
                return PulseNumber(int(left.value // right.value))
            self.runtime_error(expr.operator, "Operands must be two numbers")
        
        if operator == "==":
            return PulseBoolean(self.is_equal(left, right))
        
        if isinstance(left, PulseNumber) and isinstance(right, PulseNumber):
            if operator == '!=':
                return PulseBoolean(left.value != right.value)
            if operator == '<':
                return PulseBoolean(left.value < right.value)
            if operator == '<=':
                return PulseBoolean(left.value <= right.value)
            if operator == '>':
                return PulseBoolean(left.value > right.value)
            if operator == '>=':
                return PulseBoolean(left.value >= right.value)
        else:
            self.runtime_error(expr.operator, "Operands must be numbers")
        
        self.runtime_error(expr.operator, f"Unknown binary operator: {operator}")
    
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
        
        raise runtime.PulseRuntimeException(
            PulseRuntimeError(f"Unknown logical operator: {operator}")
        )
    
    def visit_list_expr(self, expr):
        return PulseList([self.evaluate(e) for e in expr.elements])
    
    def visit_dict_expr(self, expr):
        entries = {}
        for key_expr, val_expr in zip(expr.keys, expr.values):
            key = self.evaluate(key_expr)
            value = self.evaluate(val_expr)
            entries[key] = value
        return PulseDict(entries)
    
    def visit_index_expr(self, expr):
        obj = self.evaluate(expr.object)
        index = self.evaluate(expr.index)
        
        if isinstance(obj, PulseList):
            if not isinstance(index, PulseNumber):
                self.runtime_error(message="List index must be a number")
            idx = int(index.value)
            try:
                return obj.elements[idx]
            except IndexError:
                raise runtime.PulseRuntimeException(
                    PulseRuntimeError("Index out of bounds")
                )
        
        if isinstance(obj, PulseDict):
            result = obj.get(index)
            if isinstance(result, PulseNull) and not obj.has(index):
                self.runtime_error(message=f"Key not found in dict")
            return result
        
        if isinstance(obj, PulseString):
            if not isinstance(index, PulseNumber):
                self.runtime_error(message="String index must be a number")
            idx = int(index.value)
            try:
                return PulseString(obj.value[idx])
            except IndexError:
                self.runtime_error(message="String index out of bounds")
        
        self.runtime_error(message="Object is not indexable")
    
    def visit_setindex_expr(self, expr):
        obj = self.evaluate(expr.object)
        index = self.evaluate(expr.index)
        value = self.evaluate(expr.value)
        
        if isinstance(obj, PulseList):
            if not isinstance(index, PulseNumber):
                self.runtime_error(message="List index must be a number")
            idx = int(index.value)
            try:
                obj.elements[idx] = value
                return value
            except IndexError:
                self.runtime_error(message="Index out of bounds")
        
        if isinstance(obj, PulseDict):
            obj.set(index, value)
            return value
        
        if isinstance(obj, PulseString):
            self.runtime_error(message="Strings are immutable")
        
        self.runtime_error(message="Object does not support indexed assignment")
    
    def visit_setmember_expr(self, expr):
        obj = self.evaluate(expr.object)
        value = self.evaluate(expr.value)
        
        if isinstance(obj, PulseNull):
            self.runtime_error(expr.object, "Cannot set member on null")
        
        if isinstance(obj, PulseInstance):
            obj.set(expr.name.lexeme, value)
            return value
        
        if isinstance(obj, PulseClass):
            obj.class_vars[expr.name.lexeme] = value
            return value
        
        self.runtime_error(expr.object, "Only class objects support member assignment")
    
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
            try:
                self.execute(stmt.body)
            except runtime.BreakException:
                break
            except runtime.ContinueException:
                continue
    
    def visit_return_stmt(self, stmt):
        value = None
        if stmt.value:
            value = self.evaluate(stmt.value)
        raise runtime.ReturnException(value)
    
    def is_truthy(self, value):
        return value.is_truthy()
    
    def is_equal(self, a, b):
        if type(a) != type(b):
            return False
        
        if isinstance(a, PulseNumber):
            return a.value == b.value
        
        if isinstance(a, PulseString):
            return a.value == b.value
        
        if isinstance(a, PulseList):
            return a.elements == b.elements
    
    def num(self, value):
        if not isinstance(value, PulseNumber):
            self.runtime_error(message="Expected number")
        return value.value
    
    def visit_call_expr(self, expr):
        callee = self.evaluate(expr.callee)
        arguments = [self.evaluate(arg) for arg in expr.arguments]
        
        keyword_arguments = {
            name.lexeme: self.evaluate(value)
            for name, value in expr.keyword_arguments
        }
        
        if not callable(getattr(callee, "call", None)):
            raise runtime.PulseRuntimeException(
                PulseRuntimeError("Attempted to call a non-function")
            )
        
        return callee.call(self, arguments, keyword_arguments)
    
    def visit_break_stmt(self, stmt):
        raise runtime.BreakException()
    
    def visit_continue_stmt(self, stmt):
        raise runtime.ContinueException()
    
    def visit_for_stmt(self, stmt):
        iterable = self.evaluate(stmt.iterable)
        
        if isinstance(iterable, PulseList):
            iterable_values = iterable.elements
        elif isinstance(iterable, PulseDict):
            iterable_values = list(iterable.entries.keys())
        elif isinstance(iterable, PulseRange):
            iterable_values = iterable.to_list()
        elif isinstance(iterable, PulseString):
            iterable_values = [PulseString(c) for c in iterable.value]
        else:
            self.runtime_error(message="Object is not iterable")
        
        for value in iterable_values:
            loop_env = Environment(enclosing=self.environment)
            previous = self.environment
            self.environment = loop_env
            
            try:
                loop_env.define(stmt.var.lexeme, value)
                self.execute(stmt.body)
            except runtime.BreakException:
                break
            except runtime.ContinueException:
                continue
            finally:
                self.environment = previous
    
    def visit_function_stmt(self, stmt):
        func = PulseFunction(stmt, self.environment)
        self.environment.define(stmt.name.lexeme, func)
        return None
    
    def visit_class_stmt(self, stmt):
        self.environment.define(stmt.name.lexeme, None)
        
        bases = [self.environment.get(base) for base in stmt.bases]
        
        class_vars = {}
        for name_tok, value_expr in stmt.class_vars:
            value = self.evaluate(value_expr)
            class_vars[name_tok.lexeme] = value
        
        methods = {}
        for method in stmt.methods:
            function = PulseFunction(method, self.environment)
            methods[method.name.lexeme] = function
        
        class_object = PulseClass(stmt.name.lexeme, methods, class_vars, bases)
        self.environment.assign(stmt.name.lexeme, class_object)
    
    def visit_memberaccess_expr(self, expr):
        obj = self.evaluate(expr.object)
        name = expr.name.lexeme
        
        if isinstance(obj, PulseNull):
            self.runtime_error(message="Cannot access member of null")
        
        if isinstance(obj, PulseList):
            if name == "append":
                return PulseNativeFunction("append", lambda val: (
                    obj.elements.append(val), PulseNull()
                )[-1])
            if name == "pop":
                def list_pop(index=None):
                    if not obj.elements:
                        self.runtime_error(message="pop() on empty list")
                    if index is None:
                        return obj.elements.pop()
                    if not isinstance(index, PulseNumber):
                        self.runtime_error(message="pop() index must be a number")
                    idx = int(index.value)
                    try:
                        return obj.elements.pop(idx)
                    except IndexError:
                        self.runtime_error(message="pop() index out of range")
                return PulseNativeFunction("pop", list_pop)
            if name == "slice":
                def list_slice(start, end):
                    if not isinstance(start, PulseNumber) or not isinstance(end, PulseNumber):
                        self.runtime_error(message="slice() expects numbers")
                    return PulseList(obj.elements[int(start.value):int(end.value)])
                return PulseNativeFunction("slice", list_slice)
            if name == "contains":
                def list_contains(val):
                    for el in obj.elements:
                        if self.is_equal(el, val):
                            return PulseBoolean(True)
                    return PulseBoolean(False)
                return PulseNativeFunction("contains", list_contains)
            if name == "length":
                return PulseNativeFunction("length", lambda: PulseNumber(len(obj.elements)))
            self.runtime_error(message=f"List has no method '{name}'")
        
        if isinstance(obj, PulseString):
            if name == "upper":
                return PulseNativeFunction("upper", lambda: PulseString(obj.value.upper()))
            if name == "lower":
                return PulseNativeFunction("lower", lambda: PulseString(obj.value.lower()))
            if name == "trim":
                return PulseNativeFunction("trim", lambda: PulseString(obj.value.strip()))
            if name == "split":
                def str_split(sep=None):
                    if sep is None:
                        return PulseList([PulseString(s) for s in obj.value.split()])
                    if not isinstance(sep, PulseString):
                        self.runtime_error(message="split() separator must be a string")
                    return PulseList([PulseString(s) for s in obj.value.split(sep.value)])
                return PulseNativeFunction("split", str_split)
            if name == "join":
                def str_join(lst):
                    if not isinstance(lst, PulseList):
                        self.runtime_error(message="join() expects a list")
                    parts = []
                    for el in lst.elements:
                        if not isinstance(el, PulseString):
                            self.runtime_error(message="join() list elements must be strings")
                        parts.append(el.value)
                    return PulseString(obj.value.join(parts))
                return PulseNativeFunction("join", str_join)
            if name == "replace":
                def str_replace(old, new):
                    if not isinstance(old, PulseString) or not isinstance(new, PulseString):
                        self.runtime_error(message="replace() expects strings")
                    return PulseString(obj.value.replace(old.value, new.value))
                return PulseNativeFunction("replace", str_replace)
            if name == "starts_with":
                return PulseNativeFunction("starts_with", lambda s: PulseBoolean(
                    obj.value.startswith(s.value) if isinstance(s, PulseString)
                    else self.runtime_error(message="starts_with() expects a string")
                ))
            if name == "ends_with":
                return PulseNativeFunction("ends_with", lambda s: PulseBoolean(
                    obj.value.endswith(s.value) if isinstance(s, PulseString)
                    else self.runtime_error(message="ends_with() expects a string")
                ))
            if name == "length":
                return PulseNativeFunction("length", lambda: PulseNumber(len(obj.value)))
            self.runtime_error(message=f"String has no method '{name}'")
        
        if isinstance(obj, PulseDict):
            if name == "keys":
                return PulseNativeFunction("keys", lambda: PulseList(list(obj.entries.keys())))
            if name == "values":
                return PulseNativeFunction("values", lambda: PulseList(list(obj.entries.values())))
            if name == "items":
                return PulseNativeFunction("items", lambda: PulseList([
                    PulseList([k, v]) for k, v in obj.entries.items()
                ]))
            if name == "has":
                return PulseNativeFunction("has", lambda key: PulseBoolean(obj.has(key)))
            self.runtime_error(message=f"Dict has no method '{name}'")
        
        if isinstance(obj, PulseInstance):
            return obj.get(name)
        
        if isinstance(obj, PulseClass):
            return obj.get(name)
        
        self.runtime_error(message="Only class objects support member access")
    
    def visit_pass_stmt(self, stmt):
        return None
    
    def visit_try_stmt(self, stmt):
        try:
            self.execute(stmt.try_block)
        except runtime.PulseException as e:
            handled = False
            for exc_type_expr, var_token, block in stmt.except_blocks:
                if exc_type_expr is None:
                    match = True
                else:
                    exc_type = self.evaluate(exc_type_expr)
                    if not isinstance(exc_type, type):
                        self.runtime_error(message="Exception type must be a class")
                    match = isinstance(e, exc_type)
                
                if match:
                    handled = True
                    if var_token is not None:
                        self.environment.define(var_token.lexeme, e)
                    self.execute(block)
                    break
            if not handled:
                raise
        except (runtime.BreakException,
                runtime.ContinueException,
                runtime.ReturnException):
            raise
        else:
            if stmt.else_block is not None:
                self.execute(stmt.else_block)
        finally:
            if stmt.finally_block is not None:
                self.execute(stmt.finally_block)
    
    def visit_fstring_expr(self, expr):
        result = []
        for part in expr.parts:
            value = self.evaluate(part)
            result.append(repr(value))
        return PulseString("".join(result))