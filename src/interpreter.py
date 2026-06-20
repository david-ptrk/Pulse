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

from __future__ import annotations
import os
from typing import Any, NoReturn, Optional
from src.expressions import ExprVisitor
from src.statements import StmtVisitor
from src.environment import Environment
from src.error import PulseRuntimeError
import src.runtime as runtime
from src.tokens import Token
from src.function import PulseFunction, PulseNativeFunction, PulseNativeMethod, PulseLambda, BuiltinFunction
from src.runtime import PulseClass, PulseInstance
from src.values import (
    PulseNumber, PulseString, PulseNull, PulseNamespace,
    PulseList, PulseBoolean, PulseDict, PulseRange,
    PulseTensor, PulseValue, PulseModule, PulseModel, PulseDataset,
)
import numpy as np
import src.expressions as expressions
from src.lexer import Lexer
from src.parser import Parser
from src.native import find_module, read_file

class Interpreter(ExprVisitor, StmtVisitor):
    def __init__(self, global_environment: Environment) -> None:
        self.environment = global_environment
        self.globals = global_environment
        self.locals: dict[Any, int] = {}
        self.source: str = ""
        self._call_depth = 0
        self._max_call_depth = 1000
        
        # Built-in functions
        self.environment.define_many([
            ("print", PulseNativeFunction("print", self._bi_print)),
            ("input", PulseNativeFunction("input", self._bi_input)),
            ("str", PulseNativeFunction("str", self._bi_str)),
            ("int", PulseNativeFunction("int", self._bi_int)),
            ("float", PulseNativeFunction("float", self._bi_float)),
            ("type", PulseNativeFunction("type", self._bi_type)),
            ("abs", PulseNativeFunction("abs", self._bi_abs)),
            ("pow", PulseNativeFunction("pow", self._bi_pow)),
            ("min", PulseNativeFunction("min", self._bi_min)),
            ("max", PulseNativeFunction("max", self._bi_max)),
            ("len", PulseNativeFunction("len", self._bi_len)),
            ("range", PulseNativeFunction("range", self._bi_range)),
            ("round", PulseNativeFunction("round", self._bi_round)),
            ("bool", PulseNativeFunction("bool", self._bi_bool)),
            ("enumerate", PulseNativeFunction("enumerate", self._bi_enumerate)),
            ("zip", PulseNativeFunction("zip", self._bi_zip)),
            ("sum", PulseNativeFunction("sum", self._bi_sum)),
            ("any", PulseNativeFunction("any", self._bi_any)),
            ("all", PulseNativeFunction("all", self._bi_all)),
        ])
        
        # Built-in exception classes
        self.environment.define_many([
            ("Exception", runtime.PulseException),
            ("RuntimeError", runtime.PulseRuntimeException),
            ("ValueError", runtime.PulseValueError),
            ("TypeError", runtime.PulseTypeError),
            ("IndexError", runtime.PulseIndexError),
            ("KeyError", runtime.PulseKeyError),
            ("AttributeError", runtime.PulseAttributeError),
            ("ZeroDivisionError", runtime.PulseZeroDivisionError),
            ("NameError", runtime.PulseNameError),
            ("NotImplementedError", runtime.PulseNotImplementedError),
        ])
    
    # Entry points
    def interpret(self, statements: list, source: str)-> Any:
        """Execute a full list of top-level AST statements."""
        self.source = source
        
        result = None
        for stmt in statements:
            result = self.execute(stmt)
        return result
    
    def execute(self, stmt) -> Any:
        return stmt.accept(self)
    
    def evaluate(self, expr) -> Any:
        return expr.accept(self)
    
    def resolve(self, expr, depth: int) -> None:
        self.locals[expr] = depth
    
    # Error helpers
    def _raise(self, message: str, token: Token | None = None) -> NoReturn:
        raise runtime.PulseRuntimeException(
            PulseRuntimeError(
                message=message,
                token=token,
                context_source=self.source,
            )
        )
    
    def _raise_type(self, message: str, token: Token | None = None) -> NoReturn:
        raise runtime.PulseTypeError(
            PulseRuntimeError(
                message=message,
                token=token,
                context_source=self.source,
            )
        )
    
    def _raise_value(self, message: str, token: Token | None = None) -> NoReturn:
        raise runtime.PulseValueError(
            PulseRuntimeError(
                message=message,
                token=token,
                context_source=self.source,
            )
        )
    
    def _raise_index(self, message: str, token: Token | None = None) -> NoReturn:
        raise runtime.PulseIndexError(
            PulseRuntimeError(
                message=message,
                token=token,
                context_source=self.source,
            )
        )
    
    def _raise_key(self, message: str, token: Token | None = None) -> NoReturn:
        raise runtime.PulseKeyError(
            PulseRuntimeError(
                message=message,
                token=token,
                context_source=self.source,
            )
        )
    
    def _raise_attr(self, message: str, token: Token | None = None) -> NoReturn:
        raise runtime.PulseAttributeError(
            PulseRuntimeError(
                message=message,
                token=token,
                context_source=self.source,
            )
        )
    
    def _raise_zerodiv(self, message: str, token: Token | None = None) -> NoReturn:
        raise runtime.PulseZeroDivisionError(
            PulseRuntimeError(
                message=message,
                token=token,
                context_source=self.source,
            )
        )
    
    def _raise_name(self, message: str, token: Token | None = None) -> NoReturn:
        raise runtime.PulseNameError(
            PulseRuntimeError(
                message=message,
                token=token,
                context_source=self.source,
            )
        )
    
    def _check_number(self, value: Any, token: Token | None, label: str = "Operand") -> PulseNumber:
        if not isinstance(value, PulseNumber):
            self._raise_type(f"{label} must be a number, got {value.type_name()}", token)
        return value
    
    # Truthiness & equality
    def _is_truthy(self, value: Any) -> bool:
        return value.is_truthy()
    
    def _is_equal(self, a: Any, b: Any) -> bool:
        if isinstance(a, PulseBoolean) and isinstance(b, PulseNumber):
            return (1 if a.value else 0) == b.value
        if isinstance(a, PulseNumber) and isinstance(b, PulseBoolean):
            return a.value == (1 if b.value else 0)
        
        if type(a) is not type(b):
            return False
        
        if isinstance(a, PulseNull):
            return True
        if isinstance(a, PulseBoolean):
            return a.value == b.value
        if isinstance(a, PulseNumber):
            return a.value == b.value
        if isinstance(a, PulseString):
            return a.value == b.value
        
        if isinstance(a, PulseList):
            if len(a.elements) != len(b.elements):
                return False
            for x, y, in zip(a.elements, b.elements):
                if not self._is_equal(x, y):
                    return False
            return True
        
        if isinstance(a, PulseDict):
            if len(a.entries) != len(b.entries):
                return False
            for key in a.entries:
                if key not in b.entries:
                    return False
                if not self._is_equal(a.entries[key], b.entries[key]):
                    return False
            return True
        
        return a is b
    
    def _contains(self, container: Any, item: Any, token) -> bool:
        if isinstance(container, PulseList):
            return any(self._is_equal(item, el) for el in container.elements)
        
        if isinstance(container, PulseDict):
            return container.has(item)
        
        if isinstance(container, PulseString):
            if not isinstance(item, PulseString):
                self._raise_type("'in' on string requires a string operand", token)
            return item.value in container.value
        
        if isinstance(container, PulseRange):
            items = container.to_list()
            return any(self._is_equal(item, el) for el in items)
        
        self._raise_type(f"'in' operator not supported for type '{container.type_name()}'", token)
    
    def _is_same(self, a: Any, b: Any) -> bool:
        if isinstance(a, PulseNull) and isinstance(b, PulseNull):
            return True
        if isinstance(a, PulseBoolean) and isinstance(b, PulseBoolean):
            return a.value is b.value
        return a is b
    
    # Stringification
    def _stringify(self, val: Any) -> str:
        if isinstance(val, PulseInstance):
            for magic in ("__str__", "__repr__"):
                method = val.klass.find_method(magic)
                if method is not None:
                    result = method.bind(val).call(self, [], {})
                    return repr(result) if result is not None else "null"
        if isinstance(val, str):
            return val
        return repr(val)
    
    # File Loaders
    def _load_module(self, name: str, token) -> PulseModule:
        builtin = self._load_builtin_module(name, token)
        if builtin is not None:
            return builtin
        
        return self._load_pulse_file(name, token)
    
    def _load_builtin_module(self, name: str, token) -> Optional[PulseModule]:
        from src.stdlib import STDLIB_MODULES
        if name in STDLIB_MODULES:
            return STDLIB_MODULES[name](self)
        
        return None
    
    def _load_pulse_file(self, name: str, token) -> PulseModule:
        search_dirs = [os.getcwd(), os.path.dirname(__file__)]
        
        path = find_module(name, search_dirs)
        if path is None:
            self._raise(f"Module '{name}' not found", token)
        
        return self._execute_pulse_file(path, name)
    
    def _execute_pulse_file(self, path: str, name: str) -> PulseModule:
        source = read_file(path)
        if source is None:
            self._raise(f"Could not read module file: {path}", None)
        
        tokens = Lexer(source).scan_tokens()
        ast = Parser(tokens, source).parse()
        
        module_env = Environment(enclosing=self.environment)
        previous_env = self.environment
        self.environment = module_env
        
        try:
            for s in ast:
                self.execute(s)
        finally:
            self.environment = previous_env
        
        return PulseModule(name, dict(module_env.values))
    
    # Built-in functions
    def _bi_print(self, *args, **kwargs) -> PulseNull:
        sep = str(kwargs.get("sep", " "))
        end = str(kwargs.get("end", "\n"))
        
        print(sep.join(self._stringify(a) for a in args), end=end)
        return PulseNull()
    
    def _bi_input(self, prompt: Any = PulseString("")) -> PulseString:
        return PulseString(input(self._stringify(prompt)))
    
    def _bi_str(self, x: Any) -> PulseString:
        return PulseString(self._stringify(x))
    
    def _bi_int(self, x: Any) -> PulseNumber:
        if isinstance(x, PulseNumber):
            return PulseNumber(int(x.value))
        if isinstance(x, PulseString):
            try:
                return PulseNumber(int(x.value))
            except ValueError:
                self._raise_value(f"Cannot convert '{x.value}' to int")
        if isinstance(x, PulseBoolean):
            try:
                return PulseNumber(int(x.value))
            except ValueError:
                self._raise_value(f"Cannot convert '{x.value}' to int")
        self._raise_type(f"int() expects a number, string, or boolean, got {x.type_name()}")
    
    def _bi_float(self, x: Any) -> PulseNumber:
        if isinstance(x, PulseNumber):
            return PulseNumber(float(x.value))
        if isinstance(x, PulseString):
            try:
                return PulseNumber(float(x.value))
            except ValueError:
                self._raise_value(f"Cannot convert '{x.value}' to float")
        self._raise_type(f"float() expects a number or string, got {x.type_name()}")
    
    def _bi_type(self, obj: Any) -> PulseString:
        return PulseString(obj.type_name())
    
    def _bi_abs(self, x: Any) -> PulseNumber:
        self._check_number(x, None, "abs() argument")
        return PulseNumber(abs(x.value))
    
    def _bi_pow(self, base: Any, exp: Any) -> PulseNumber:
        self._check_number(base, None, "pow() base")
        self._check_number(exp,  None, "pow() exponent")
        return PulseNumber(pow(base.value, exp.value))
    
    def _bi_min(self, *args: Any) -> PulseNumber:
        if not args:
            self._raise_value("min() expects at least one argument")
        for a in args:
            self._check_number(a, None, "min() argument")
        return PulseNumber(min(a.value for a in args))
    
    def _bi_max(self, *args: Any) -> PulseNumber:
        if not args:
            self._raise_value("max() expects at least one argument")
        for a in args:
            self._check_number(a, None, "max() argument")
        return PulseNumber(max(a.value for a in args))
    
    def _bi_len(self, x: Any) -> PulseNumber:
        if isinstance(x, PulseList):
            return PulseNumber(len(x.elements))        
        if isinstance(x, PulseString):
            return PulseNumber(len(x.value))
        if isinstance(x, PulseDict):
            return PulseNumber(len(x.entries))
        if isinstance(x, PulseRange):
            return PulseNumber(len(x))
        self._raise_type(f"len() not supported for type '{x.type_name()}'")
    
    def _bi_range(self, *args: Any) -> PulseRange:
        int_args: list[int] = []
        for a in args:
            self._check_number(a, None, "range() argument")
            int_args.append(int(a.value))
        
        if len(int_args) == 1:
            return PulseRange(0, int_args[0])
        if len(int_args) == 2:
            return PulseRange(int_args[0], int_args[1])
        if len(int_args) == 3:
            if int_args[2] == 0:
                self._raise_value("range() step cannot be zero")
            return PulseRange(int_args[0], int_args[1], int_args[2])
        
        self._raise_value("range() expects 1, 2, or 3, arguments")
    
    def _bi_round(self, x: Any, digits: Any = None) -> PulseNumber:
        self._check_number(x, None, "round() argument")
        if digits is None:
            return PulseNumber(round(x.value))
        self._check_number(digits, None, "round() digits")
        return PulseNumber(round(x.value, int(digits.value)))
    
    def _bi_bool(self, x: Any) -> PulseBoolean:
        return PulseBoolean(self._is_truthy(x))
    
    def _bi_enumerate(self, iterable: Any, start: Any = None) -> PulseList:
        offset = 0
        if start is not None:
            self._check_number(start, None, "enumerate() start")
            offset = int(start.value)
        
        if isinstance(iterable, PulseList):
            items = iterable.elements
        elif isinstance(iterable, PulseString):
            items = [PulseString(c) for c in iterable.value]
        elif isinstance(iterable, PulseRange):
            items = iterable.to_list()
        else:
            self._raise_type(f"enumerate() argument must be iterable, got '{iterable.type_name()}'")
        
        return PulseList([
            PulseList([PulseNumber(i + offset), el])
            for i, el in enumerate(items)
        ])
    
    def _bi_zip(self, *iterables: Any) -> PulseList:
        if not iterables:
            return PulseList([])
        
        def to_items(obj):
            if isinstance(obj, PulseList):
                return obj.elements
            if isinstance(obj, PulseString):
                return [PulseString(c) for c in obj.value]
            if isinstance(obj, PulseRange):
                return obj.to_list()
            self._raise_type(f"zip() argument must be iterable, got '{obj.type_name()}'")
        
        lists = [to_items(it) for it in iterables]
        return PulseList([
            PulseList(list(group))
            for group in zip(*lists)
        ])
    
    def _bi_sum(self, iterable: Any, start: Any = None) -> PulseNumber:
        if isinstance(iterable, PulseList):
            items = iterable.elements
        elif isinstance(iterable, PulseRange):
            items = iterable.to_list()
        else:
            self._raise_type(f"sum() argument must be iterable, got '{iterable.type_name()}'")
        
        total = start.value if start is not None else 0
        for item in items:
            self._check_number(item, None, "sum() element")
            total += item.value
        return PulseNumber(total)
    
    def _bi_any(self, iterable: Any) -> PulseBoolean:
        if isinstance(iterable, PulseList):
            items = iterable.elements
        elif isinstance(iterable, PulseRange):
            items = iterable.to_list()
        else:
            self._raise_type(f"any() argument must be iterable, got '{iterable.type_name()}'")
        return PulseBoolean(any(self._is_truthy(el) for el in items))
    
    def _bi_all(self, iterable: Any) -> PulseBoolean:
        if isinstance(iterable, PulseList):
            items = iterable.elements
        elif isinstance(iterable, PulseRange):
            items = iterable.to_list()
        else:
            self._raise_type(f"all() argument must be iterable, got '{iterable.type_name()}'")
        return PulseBoolean(all(self._is_truthy(el) for el in items))
    
    # Statement visitors
    def visit_expression_stmt(self, stmt) -> Any:
        return self.evaluate(stmt.expression)
    
    def visit_pass_stmt(self, stmt) -> None:
        return None
    
    def visit_block_stmt(self, stmt) -> Any:
        previous = self.environment
        self.environment = Environment(enclosing=previous)
        
        try:
            result = None
            for s in stmt.statements:
                result = self.execute(s)
            return result
        finally:
            self.environment = previous
    
    def visit_if_stmt(self, stmt) -> Any:
        if self._is_truthy(self.evaluate(stmt.condition)):
            return self.execute(stmt.then_branch)
        
        for cond, branch in stmt.elif_branches:
            if self._is_truthy(self.evaluate(cond)):
                return self.execute(branch)
        
        if stmt.else_branch is not None:
            return self.execute(stmt.else_branch)
        
        return None
    
    def visit_while_stmt(self, stmt) -> None:
        while self._is_truthy(self.evaluate(stmt.condition)):
            try:
                self.execute(stmt.body)
            except runtime.BreakException:
                break
            except runtime.ContinueException:
                continue
    
    def visit_for_stmt(self, stmt) -> None:
        iterable = self.evaluate(stmt.iterable)
        
        if isinstance(iterable, PulseList):
            items = iterable.elements
        elif isinstance(iterable, PulseDict):
            items = list(iterable.entries.keys())
        elif isinstance(iterable, PulseRange):
            items = iterable.to_list()
        elif isinstance(iterable, PulseString):
            items = [PulseString(c) for c in iterable.value]
        else:
            self._raise_type(f"Object of type '{iterable.type_name()}' is not iterable")
        
        previous = self.environment
        for value in items:
            loop_env = Environment(enclosing=previous)
            self.environment = loop_env
            
            try:
                if stmt.vars is not None:
                    if not isinstance(value, PulseList):
                        self._raise(f"Cannot unpack non-list value in for loop")
                    if len(value.elements) != len(stmt.vars):
                        self._raise_value(
                            f"Cannot unpack {len(value.elements)} values "
                            f"into {len(stmt.vars)} variables"
                        )
                    for var, el in zip(stmt.vars, value.elements):
                        loop_env.define(var.lexeme, el)
                else:                
                    loop_env.define(stmt.var.lexeme, value)
                
                self.execute(stmt.body)
            except runtime.BreakException:
                break
            except runtime.ContinueException:
                continue
            finally:
                self.environment = previous
    
    def visit_break_stmt(self, stmt) -> NoReturn:
        raise runtime.BreakException()
    
    def visit_continue_stmt(self, stmt) -> NoReturn:
        raise runtime.ContinueException()
    
    def visit_return_stmt(self, stmt) -> NoReturn:
        value = self.evaluate(stmt.value) if stmt.value is not None else PulseNull()
        raise runtime.ReturnException(value)
    
    def visit_function_stmt(self, stmt) -> None:
        func = PulseFunction(stmt, self.environment)
        self.environment.define(stmt.name.lexeme, func)
    
    def visit_class_stmt(self, stmt) -> None:
        self.environment.define(stmt.name.lexeme, None)
        
        bases = [self.environment.get(base) for base in stmt.bases]
        
        class_vars: dict[str, Any] = {}
        for name_tok, value_expr in stmt.class_vars:
            class_vars[name_tok.lexeme] = self.evaluate(value_expr)
        
        methods: dict[str, PulseFunction] = {}
        for method in stmt.methods:
            methods[method.name.lexeme] = PulseFunction(method, self.environment)
        
        klass = PulseClass(stmt.name.lexeme, methods, class_vars, bases)
        self.environment.assign(stmt.name.lexeme, klass)
    
    def visit_try_stmt(self, stmt) -> Any:
        result = None
        try:
            self.execute(stmt.try_block)
        except (runtime.BreakException,
                runtime.ContinueException,
                runtime.ReturnException):
            raise
        
        except runtime.PulseException as exc:
            handled = False
            for exc_type_expr, var_token, block in stmt.except_blocks:
                if exc_type_expr is None:
                    match = True
                else:
                    exc_type = self.evaluate(exc_type_expr)
                    if not isinstance(exc_type, type):
                        self._raise("Exception type in 'except' must be a class")
                    match = isinstance(exc, exc_type)
                
                if match:
                    handled = True
                    if var_token is not None:
                        self.environment.define(var_token.lexeme, exc.message)
                    result = self.execute(block)
                    break
            
            if not handled:
                raise
        
        else:
            if stmt.else_block is not None:
                result = self.execute(stmt.else_block)
        
        finally:
            if stmt.finally_block is not None:
                self.execute(stmt.finally_block)
        
        return result
    
    def visit_import_stmt(self, stmt) -> None:
        module_name = ".".join(t.lexeme for t in stmt.module_path)
        module = self._load_module(module_name, stmt.keyword)
        
        if stmt.names is not None:
            for name_token, alias_token in stmt.names:
                key = name_token.lexeme
                val = module.get(key)
                if val is None:
                    self._raise_attr(f"Module '{module_name}' has no member '{key}'", name_token)
                binding =alias_token.lexeme if alias_token else key
                self.environment.define(binding, val)
        else:
            binding = stmt.alias.lexeme if stmt.alias else stmt.module_path[-1].lexeme
            self.environment.define(binding, module)
    
    def visit_raise_stmt(self, stmt) -> NoReturn:
        if stmt.exception is None:
            self._raise("raise requires an exception", stmt.keyword)
        
        exc = self.evaluate(stmt.exception)
        
        if isinstance(exc, runtime.PulseException):
            raise exc
        
        if isinstance(exc, PulseString):
            self._raise(exc.value, stmt.keyword)
        
        self._raise(self._stringify(exc), stmt.keyword)
    
    def visit_del_stmt(self, stmt) -> None:
        for target in stmt.targets:
            if isinstance(target, expressions.Variable):
                name = target.name.lexeme
                if not self.environment.has(name):
                    self._raise_name(f"Cannot delete undefined variable '{name}'", stmt.keyword)
                self.environment.delete(name)
            
            elif isinstance(target, expressions.Index):
                obj = self.evaluate(target.object)
                index = self.evaluate(target.index)
                if isinstance(obj, PulseList):
                    self._check_number(index, stmt.keyword, "List index")
                    idx = int(index.value)
                    if idx < -len(obj.elements) or idx >= len(obj.elements):
                        self._raise_index(f"List index {idx} out of range", stmt.keyword)
                    obj.elements.pop(idx)
                elif isinstance(obj, PulseDict):
                    if not obj.has(index):
                        self._raise_key(f"Key '{self._stringify(index)}' not found in dict", stmt.keyword)
                    obj.remove(index)
                else:
                    self._raise_type(f"Cannot delete index on type '{obj.type_name()}'", stmt.keyword)
            
            elif isinstance(target, expressions.MemberAccess):
                obj = self.evaluate(target.object)
                if isinstance(obj, PulseInstance):
                    obj.fields.pop(target.name.lexeme, None)
                else:
                    self._raise_attr(f"Cannot delete member on type '{obj.type_name()}'", stmt.keyword)
            
            else:
                self._raise("Invalid del target", stmt.keyword)
    
    def visit_match_stmt(self, stmt) -> Any:
        subject = self.evaluate(stmt.subject)
        
        for pattern, guard, body in stmt.cases:
            bindings = {}
            if self._match_pattern(pattern, subject, bindings):
                if guard is not None:
                    prev = self.environment
                    guard_env = Environment(enclosing=prev)
                    for k, v in bindings.items():
                        guard_env.define(k, v)
                    self.environment = guard_env
                    try:
                        passed = self._is_truthy(self.evaluate(guard))
                    finally:
                        self.environment = prev
                    if not passed:
                        continue
                
                prev = self.environment
                case_env = Environment(enclosing=prev)
                for k, v in bindings.items():
                    case_env.define(k, v)
                self.environment = case_env
                try:
                    return self.execute(body)
                finally:
                    self.environment = prev
        
        return None
    
    def _match_pattern(self, pattern, subject, bindings: dict) -> bool:
        if isinstance(pattern, Token) and pattern.lexeme == "_":
            return True
        
        if isinstance(pattern, Token):
            bindings[pattern.lexeme] = subject
            return True
        
        if isinstance(pattern, tuple) and pattern[0] == "or":
            return any(self._match_pattern(alt, subject, {}) for alt in pattern[1])
        
        if isinstance(pattern, tuple) and pattern[0] == "sequence":
            if not isinstance(subject, PulseList):
                return False
            sub_patterns = pattern[1]
            if len(sub_patterns) != len(subject.elements):
                return False
            for sub_pat, el in zip(sub_patterns, subject.elements):
                sub_bindings = {}
                if not self._match_pattern(sub_pat, el, sub_bindings):
                    return False
                bindings.update(sub_bindings)
            return True
        
        if isinstance(pattern, tuple) and pattern[0] == "mapping":
            if not isinstance(subject, PulseDict):
                return False
            for key_expr, val_pattern in pattern[1]:
                key = self.evaluate(key_expr)
                if not subject.has(key):
                    return False
                val = subject.get(key)
                sub_bindings = {}
                if not self._match_pattern(val_pattern, val, sub_bindings):
                    return False
                bindings.update(sub_bindings)
            return True
        
        value = self.evaluate(pattern)
        return self._is_equal(subject, value)
    
    # Expression visitors
    def visit_literal_expr(self, expr) -> Any:
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
    
    def visit_tensor_expr(self, expr) -> PulseTensor:
        try:
            array = np.array(expr.value, dtype=float)
        except (ValueError, TypeError) as e:
            self._raise_value(f"Invalid tensor data: {e}")
        return PulseTensor(array)
    
    def visit_variable_expr(self, expr) -> Any:
        name = expr.name.lexeme
        if name == "self":
            return self.environment.get("self")
        
        distance = self.locals.get(expr)
        try:
            if distance is not None:
                return self.environment.get_at(distance, name)
            return self.environment.get(name)
        except runtime.PulseRuntimeException:
            self._raise_name(f"Undefined variable '{name}'", expr.name)
    
    def visit_assign_expr(self, expr) -> Any:
        value = self.evaluate(expr.value)
        name = expr.name.lexeme
        
        distance = self.locals.get(expr)
        if distance is not None:
            self.environment.assign_at(distance, name, value)
        else:
            if name in self.globals.values:
                self.globals.assign(name, value)
            else:
                self.globals.define(name, value)
        
        return value
    
    def visit_grouping_expr(self, expr) -> Any:
        return self.evaluate(expr.expression)
    
    def visit_unary_expr(self, expr) -> Any:
        right = self.evaluate(expr.right)
        operator = expr.operator.lexeme
        
        if operator == "-":
            self._check_number(right, expr.operator, "Unary '-' operand")
            return PulseNumber(-right.value)
        
        if operator in ("not", "!"):
            return PulseBoolean(not self._is_truthy(right))
        
        self._raise(f"Unknown unary operator '{operator}'", expr.operator)
    
    def visit_binary_expr(self, expr) -> Any:
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)
        operator = expr.operator.lexeme
        tok = expr.operator
        
        if isinstance(left, PulseTensor) or isinstance(right, PulseTensor):
            if isinstance(left, PulseNumber) and isinstance(right, PulseTensor):
                left, right = right, left
            
            if isinstance(left, PulseTensor) and isinstance(right, PulseNumber):
                scalar = right.value
                try:
                    if operator == "+":
                        return PulseTensor(left.array + scalar)
                    if operator == "-":
                        return PulseTensor(left.array - scalar)
                    if operator == "*":
                        return PulseTensor(left.array * scalar)
                    if operator == "/":
                        if scalar == 0:
                            self._raise_zerodiv("Division by zero", tok)
                        return PulseTensor(left.array / scalar)
                    self._raise_type(f"Tensor does not support operator '{operator}' with scalar", tok)
                except ValueError as e:
                    self._raise_value(f"Tensor operation failed: {e}", tok)
            
            if not isinstance(left, PulseTensor) or not isinstance(right, PulseTensor):
                self._raise_type(
                    f"Both operands must be tensors, "
                    f"got '{left.type_name()}' and '{right.type_name()}'",
                    tok,
                )
            try:
                if operator == "+":
                    return PulseTensor(left.array + right.array)
                if operator == "-":
                    return PulseTensor(left.array - right.array)
                if operator == "*":
                    return PulseTensor(left.array * right.array)
                if operator == "/":
                    return PulseTensor(left.array / right.array)
                if operator == "@":
                    return PulseTensor(left.array @ right.array)
                if operator == "==":
                    return PulseBoolean(np.array_equal(left.array, right.array))
                if operator == "!=":
                    return PulseBoolean(not np.array_equal(left.array, right.array))
                self._raise_type(f"Tensor does not support operator '{operator}'", tok)
            except ValueError as e:
                self._raise_value(f"Tensor operation failed: {e}", tok)
        
        if operator == "==":
            return PulseBoolean(self._is_equal(left, right))
        if operator == "!=":
            return PulseBoolean(not self._is_equal(left, right))
        
        if operator == "in":
            return PulseBoolean(self._contains(right, left, tok))
        if operator == "not in":
            return PulseBoolean(not self._contains(right, left, tok))
        
        if operator == "is":
            return PulseBoolean(self._is_same(left, right))
        if operator == "is not":
            return PulseBoolean(not self._is_same(left, right))
        
        if operator == "+" and isinstance(left, PulseString) and isinstance(right, PulseString):
            return PulseString(left.value + right.value)
        
        if operator == "+" and isinstance(left, PulseList) and isinstance(right, PulseList):
            return PulseList(left.elements + right.elements)
        
        if operator in ("+", "-", "*", "/", "%", "//", "**", "<", "<=", ">", ">="):
            if not isinstance(left, PulseNumber) or not isinstance(right, PulseNumber):
                if operator == "+":
                    self._raise_type(
                        "'+' requires two numbers or two strings, "
                        f"got '{left.type_name()}' and '{right.type_name()}'",
                        tok,
                    )
                self._raise_type(
                    f"'{operator}' requires two numbers, "
                    f"got '{left.type_name()}' and '{right.type_name()}'",
                    tok,
                )
            
            lv, rv = left.value, right.value
            
            if operator == "+":
                return PulseNumber(lv + rv)
            if operator == "-":
                return PulseNumber(lv - rv)
            if operator == "*":
                return PulseNumber(lv * rv)
            
            if operator == "/":
                if rv == 0:
                    self._raise_zerodiv("Division by zero", tok)
                return PulseNumber(lv / rv)
            
            if operator == "%":
                if rv == 0:
                    self._raise_zerodiv("Modulo by zero", tok)
                return PulseNumber(lv % rv)
            
            if operator == "//":
                if rv == 0:
                    self._raise_zerodiv("Integer division by zero", tok)
                return PulseNumber(int(lv // rv))
            
            if operator == "**":
                if not isinstance(left, PulseNumber) or not isinstance(right, PulseNumber):
                    self._raise_type(f"'**' requires two numbers, got '{left.type_name()}' and '{right.type_name()}'", tok)
                return PulseNumber(left.value ** right.value)
            
            if operator == "<":
                return PulseBoolean(lv < rv)
            if operator == "<=":
                return PulseBoolean(lv <= rv)
            if operator == ">":
                return PulseBoolean(lv > rv)
            if operator == ">=":
                return PulseBoolean(lv >= rv)
        
        self._raise(f"Unknown binary operator '{operator}'", tok)
    
    def visit_logical_expr(self, expr) -> Any:
        left = self.evaluate(expr.left)
        operator = expr.operator.lexeme
        
        if operator == "or":
            return left if self._is_truthy(left) else self.evaluate(expr.right)
        if operator == "and":
            return left if not self._is_truthy(left) else self.evaluate(expr.right)
        
        self._raise(f"Unknown logical operator '{operator}'", expr.operator)
    
    def visit_list_expr(self, expr) -> PulseList:
        return PulseList([self.evaluate(e) for e in expr.elements])
    
    def visit_dict_expr(self, expr) -> PulseDict:
        entries: dict[Any, Any] = {}
        for key_expr, val_expr in zip(expr.keys, expr.values):
            entries[self.evaluate(key_expr)] = self.evaluate(val_expr)
        return PulseDict(entries)
    
    def visit_index_expr(self, expr) -> Any:
        obj = self.evaluate(expr.object)
        index = self.evaluate(expr.index)
        
        if isinstance(obj, PulseList):
            self._check_number(index, None, "List index")
            idx = int(index.value)
            if idx < -len(obj.elements) or idx >= len(obj.elements):
                self._raise_index(f"List index {idx} out of range (length {len(obj.elements)})")
            return obj.elements[idx]
        
        if isinstance(obj, PulseDict):
            if not obj.has(index):
                self._raise_key(f"Key '{self._stringify(index)}' not found in dict")
            return obj.get(index)
        
        if isinstance(obj, PulseString):
            self._check_number(index, None, "String index")
            idx = int(index.value)
            if idx < -len(obj.value) or idx >= len(obj.value):
                self._raise_index(f"String index {idx} out of range (length {len(obj.value)})")
            return PulseString(obj.value[idx])
        
        if isinstance(obj, PulseTensor):
            self._check_number(index, None, "Tensor index")
            idx = int(index.value)
            if idx < 0 or idx >= len(obj.array):
                self._raise_index("Tensor index out of range")
            
            result = obj.array[idx]
            if isinstance(result, np.ndarray):
                return PulseTensor(result)
            return PulseNumber(float(result))
        
        self._raise_type(f"Object of type '{obj.type_name()}' does not support indexing")
    
    def visit_setindex_expr(self, expr) -> Any:
        obj = self.evaluate(expr.object)
        index = self.evaluate(expr.index)
        value = self.evaluate(expr.value)
        
        if isinstance(obj, PulseList):
            self._check_number(index, None, "List index")
            idx = int(index.value)
            if idx < -len(obj.elements) or idx >= len(obj.elements):
                self._raise_index(f"List index {idx} out of range (length {len(obj.elements)})")
            obj.elements[idx] = value
            return value
        
        if isinstance(obj, PulseDict):
            obj.set(index, value)
            return value
        
        if isinstance(obj, PulseString):
            self._raise_type("Strings are immutable and do not support index assignment")
        
        self._raise_type(f"Object of type '{obj.type_name()}' does not support indexed assignment")
    
    def visit_slice_expr(self, expr) -> Any:
        self._raise("Slice used outside of index expression")
    
    def visit_multiindex_expr(self, expr) -> Any:
        obj = self.evaluate(expr.object)
        
        def resolve_index(index_expr):
            if isinstance(index_expr, expressions.Slice):
                lower = int(self.evaluate(index_expr.lower).value) if index_expr.lower else None
                upper = int(self.evaluate(index_expr.upper).value) if index_expr.upper else None
                return slice(lower, upper)
            else:
                val = self.evaluate(index_expr)
                return int(val.value)
        
        if isinstance(obj, PulseList):
            if len(expr.indices) != 1 or not isinstance(expr.indices[0], expressions.Slice):
                self._raise_type("Lists only support single slice indexing")
            s = resolve_index(expr.indices[0])
            return PulseList(obj.elements[s])
        
        if isinstance(obj, PulseString):
            if len(expr.indices) != 1 or not isinstance(expr.indices[0], expressions.Slice):
                self._raise_type("Strings only support single slice indexing")
            s = resolve_index(expr.indices[0])
            return PulseString(obj.value[s])
        
        if isinstance(obj, PulseTensor):
            idx = tuple(resolve_index(i) for i in expr.indices)
            key = idx[0] if len(idx) == 1 else idx
            try:
                result = obj.array[key]
            except IndexError as e:
                self._raise_index(f"Tensor index out of range: {e}")
            
            if isinstance(result, np.ndarray):
                return PulseTensor(result)
            return PulseNumber(float(result))
        
        self._raise_type(f"Object of type '{obj.type_name()}' does not support slicing")
    
    def visit_setmember_expr(self, expr) -> Any:
        obj = self.evaluate(expr.object)
        value = self.evaluate(expr.value)
        
        if isinstance(obj, PulseInstance):
            obj.set(expr.name.lexeme, value)
            return value
        
        if isinstance(obj, PulseClass):
            obj.class_vars[expr.name.lexeme] = value
            return value
        
        self._raise_attr(
            f"Cannot assign member '{expr.name.lexeme}' on "
            f"object of type '{obj.type_name()}'",
            expr.name,
        )
    
    def visit_call_expr(self, expr) -> Any:
        self._call_depth += 1
        if self._call_depth > self._max_call_depth:
            self._call_depth = 0
            self._raise("Maximum recursion depth exceeded", expr.paren)
        
        callee = self.evaluate(expr.callee)
        arguments = [self.evaluate(arg) for arg in expr.arguments]
        
        kwargs = {
            name.lexeme: self.evaluate(value)
            for name, value in expr.keyword_arguments
        }
        
        if isinstance(callee, BuiltinFunction):
            try:
                result = callee.func(*arguments, **kwargs)
                return result
            except Exception as e:
                self._raise(str(e), expr.paren)
            finally:
                self._call_depth -= 1
        
        if (isinstance(callee, PulseFunction) and not callee.is_bound and not callee.declaration.is_static and callee.declaration.is_method):
            if arguments and isinstance(arguments[0], PulseInstance):
                callee = callee.bind(arguments[0])
                arguments = arguments[1:]
            else:
                self._raise_type(f"{callee.declaration.name.lexeme}() missing required argument: 'self'. Calling non-static")
        
        if isinstance(callee, type) and issubclass(callee, runtime.PulseException):
            msg = self._stringify(arguments[0]) if arguments else ""
            raise callee(msg)
        
        if not callable(getattr(callee, "call", None)):
            self._raise_type("Attempted to call a non-callable value")
        
        func_name = getattr(getattr(callee, "declaration", None), "name", None)
        func_name = func_name.lexeme if func_name else repr(callee)
        call_line = expr.paren.line if hasattr(expr, "paren") else None
        PulseRuntimeError.push_stack(func_name, call_line)
        
        try:
            return callee.call(self, arguments, kwargs)
        except RecursionError:
            self._call_depth = 0
            self._raise("Maximum recursion depth exceeded", expr.paren)
        finally:
            PulseRuntimeError.pop_stack()
            self._call_depth -= 1
    
    def visit_memberaccess_expr(self, expr) -> Any:
        obj = self.evaluate(expr.object)
        name = expr.name.lexeme
        
        if isinstance(obj, PulseNull):
            self._raise_attr("Cannot access member of null", expr.name)
        
        if isinstance(obj, PulseList):
            return self._list_method(obj, name, expr.name)
        
        if isinstance(obj, PulseString):
            return self._string_method(obj, name, expr.name)
        
        if isinstance(obj, PulseDict):
            return self._dict_method(obj, name, expr.name)
        
        if isinstance(obj, PulseTensor):
            return self._tensor_property(obj, name, expr.name)
        
        if isinstance(obj, PulseModel):
            if not hasattr(obj, 'methods') or name not in obj.methods:
                self._raise_attr(f"Model '{obj.model_name}' has no method '{name}'", expr.name)
            return obj.methods[name]
        
        if isinstance(obj, PulseDataset):
            if name not in obj.methods:
                self._raise_attr(f"Dataset has no method '{name}'", expr.name)
            return obj.methods[name]
        
        if isinstance(obj, PulseInstance):
            return obj.get(name)
        
        if isinstance(obj, PulseClass):
            return obj.get(name)
        
        if isinstance(obj, PulseModule):
            val = obj.get(name)
            if val is None:
                self._raise_attr(f"Module '{obj.name}' has no member '{name}'", expr.name)
            return val
        
        if isinstance(obj, PulseNamespace):
            if name not in obj.members:
                self._raise_attr(f"'{obj.name}' has no member '{name}'", expr.name)
            return obj.members[name]
        
        self._raise_attr(
            f"Object of type '{obj.type_name()}' does not support member access",
            expr.name,
        )
    
    def visit_fstring_expr(self, expr) -> PulseString:
        result = []
        for part in expr.parts:
            value = self.evaluate(part)
            result.append(self._stringify(value))
        return PulseString("".join(result))
    
    def visit_pipe_expr(self, expr) -> Any:
        left_val = self.evaluate(expr.left)
        right_val = self.evaluate(expr.right)
        
        if not callable(getattr(right_val, "call", None)):
            self._raise_type("Right side of '|>' must be a callable")
        
        PulseRuntimeError.push_stack(repr(right_val), line_number=None)
        try:
            return right_val.call(self, [left_val], {})
        finally:
            PulseRuntimeError.pop_stack()
    
    def visit_lambda_expr(self, expression) -> Any:
        return PulseLambda(expression.params, expression.body, self.environment)
    
    def visit_unpack_expr(self, expr) -> Any:
        value = self.evaluate(expr.value)
        
        if isinstance(value, PulseList):
            elements = value.elements
        elif isinstance(value, PulseTensor):
            elements = []
            for i in range(len(value.array)):
                row = value.array[i]
                if isinstance(row, np.ndarray):
                    elements.append(PulseTensor(row))
                else:
                    elements.append(PulseNumber(float(row)))
        else:
            self._raise_type(f"Cannot unpack value of type '{value.type_name()}'")
        
        if len(expr.names) != len(elements):
            self._raise_value(f"Cannot unpack {len(elements)} values into {len(expr.names)} variables")
        
        for name_tok, val in zip(expr.names, elements):
            self.environment.define(name_tok.lexeme, val)
        
        return value
    
    def visit_listcomp_expr(self, expr) -> PulseList:
        iterable = self.evaluate(expr.iterable)
        
        if isinstance(iterable, PulseList):
            items = iterable.elements
        elif isinstance(iterable, PulseRange):
            items = iterable.to_list()
        elif isinstance(iterable, PulseString):
            items = [PulseString(c) for c in iterable.value]
        else:
            self._raise_type(f"List comprehension iterable must be iterable, got '{iterable.type_name()}'")
        
        results = []
        previous = self.environment
        for item in items:
            loop_env = Environment(enclosing=previous)
            loop_env.define(expr.var.lexeme, item)
            self.environment = loop_env
            try:
                if expr.condition is not None:
                    if not self._is_truthy(self.evaluate(expr.condition)):
                        continue
                results.append(self.evaluate(expr.element))
            finally:
                self.environment = previous
        
        return PulseList(results)
    
    def visit_ternary_expr(self, expr) -> Any:
        if self._is_truthy(self.evaluate(expr.condition)):
            return self.evaluate(expr.then_expr)
        return self.evaluate(expr.else_expr)
    
    # Built-in method dispatch
    def _list_method(self, obj: PulseList, name: str, token: Token) -> PulseNativeFunction:
        if name == "append":
            def _append(val: Any) -> PulseNull:
                obj.elements.append(val)
                return PulseNull()
            return PulseNativeFunction("append", _append)
        
        if name == "pop":
            def _pop(index: Any = None) -> Any:
                if not obj.elements:
                    self._raise_index("pop() called on empty list")
                if index is None:
                    return obj.elements.pop()
                self._check_number(index, token, "pop() index")
                idx = int(index.value)
                if idx < -len(obj.elements) or idx >= len(obj.elements):
                    self._raise_index(f"pop() index {idx} out of range")
                return obj.elements.pop(idx)
            return PulseNativeFunction("pop", _pop)
        
        if name == "slice":
            def _slice(start: Any, end: Any) -> PulseList:
                self._check_number(start, token, "slice() start")
                self._check_number(end, token, "slice() end")
                return PulseList(obj.elements[int(start.value):int(end.value)])
            return PulseNativeFunction("slice", _slice)
        
        if name == "contains":
            def _contains(val: Any) -> PulseBoolean:
                return PulseBoolean(any(self._is_equal(el, val) for el in obj.elements))
            return PulseNativeFunction("contains", _contains)
        
        if name == "length":
            return PulseNativeFunction("length", lambda: PulseNumber(len(obj.elements)))
        
        if name == "reverse":
            def _reverse() -> PulseNull:
                obj.elements.reverse()
                return PulseNull()
            return PulseNativeFunction("reverse", _reverse)
        
        if name == "clear":
            def _clear() -> PulseNull:
                obj.elements.clear()
                return PulseNull()
            return PulseNativeFunction("clear", _clear)
        
        if name == "sort":
            def _sort(key=None, reverse=None) -> PulseNull:
                rev = False
                if reverse is not None:
                    if not isinstance(reverse, PulseBoolean):
                        self._raise_type("sort() 'reverse' must be a boolean", token)
                    rev = reverse.value
                
                try:
                    if key is None:
                        def default_key(el):
                            if isinstance(el, PulseNumber):
                                return el.value
                            if isinstance(el, PulseString):
                                return el.value
                            self._raise_type(f"sort() cannot compare values of type '{el.type_name()}'", token)
                        obj.elements.sort(key=default_key, reverse=rev)
                    else:
                        if not callable(getattr(key, "call", None)):
                            self._raise_type("sort() key must be a callable", token)
                        def pulse_key(el):
                            result = key.call(self, [el], {})
                            if isinstance(result, PulseNumber):
                                return result.value
                            if isinstance(result, PulseString):
                                return result.value
                            self._raise_type(f"sort() key function must return a number or string", token)
                        obj.elements.sort(key=pulse_key, reverse=rev)
                except PulseRuntimeError:
                    raise
                
                return PulseNull()
            return PulseNativeFunction("sort", _sort)
        
        if name == "map":
            def _map(fn: Any) -> PulseList:
                if not callable(getattr(fn, "call", None)):
                    self._raise_type("map() argument must be a callable", token)
                return PulseList([fn.call(self, [el], {}) for el in obj.elements])
            return PulseNativeFunction("map", _map)
        
        if name == "filter":
            def _filter(fn: Any) -> PulseList:
                if not callable(getattr(fn, "call", None)):
                    self._raise_type("filter() argument must be a callable", token)
                return PulseList([
                    el for el in obj.elements
                    if self._is_truthy(fn.call(self, [el], {}))
                ])
            return PulseNativeFunction("filter", _filter)
        
        if name == "index":
            def _index(val: Any, start: Any = None) -> PulseNumber:
                s = int(start.value) if start is not None else 0
                for i, el in enumerate(obj.elements[s:], s):
                    if self._is_equal(el, val):
                        return PulseNumber(i)
                self._raise_value(f"Value not found in list", token)
            return PulseNativeFunction("index", _index)
        
        if name == "find":
            def _find(val: Any, start: Any = None) -> PulseNumber:
                s = int(start.value) if start is not None else 0
                for i, el in enumerate(obj.elements[s:], s):
                    if self._is_equal(el, val):
                        return PulseNumber(i)
                return PulseNumber(-1)
            return PulseNativeFunction("find", _find)
        
        if name == "insert":
            def _insert(index: Any, val: Any) -> PulseNull:
                self._check_number(index, token, "insert() index")
                idx = int(index.value)
                obj.elements.insert(idx, val)
                return PulseNull()
            return PulseNativeFunction("insert", _insert)
        
        if name == "extend":
            def _extend(other: Any) -> PulseNull:
                if isinstance(other, PulseList):
                    obj.elements.extend(other.elements)
                elif isinstance(other, PulseRange):
                    obj.elements.extend(other.to_list())
                else:
                    self._raise_type(f"extend() argument must be a list or range, got '{other.type_name()}'", token)
                return PulseNull()
            return PulseNativeFunction("extend", _extend)
        
        if name == "count":
            def _count(val: Any) -> PulseNumber:
                return PulseNumber(sum(1 for el in obj.elements if self._is_equal(el, val)))
            return PulseNativeFunction("count", _count)
        
        self._raise_attr(f"List has no method '{name}'", token)
    
    def _string_method(self, obj: PulseString, name: str, token: Token) -> PulseNativeFunction:
        if name == "upper":
            return PulseNativeFunction("upper", lambda: PulseString(obj.value.upper()))
        
        if name == "lower":
            return PulseNativeFunction("lower", lambda: PulseString(obj.value.lower()))
        
        if name == "trim":
            return PulseNativeFunction("trim", lambda: PulseString(obj.value.strip()))
        
        if name == "split":
            def _split(sep: Any = None) -> PulseList:
                if sep is None:
                    return PulseList([PulseString(s) for s in obj.value.split()])
                if not isinstance(sep, PulseString):
                    self._raise_type("split() separator must be a string", token)
                return PulseList([PulseString(s) for s in obj.value.split(sep.value)])
            return PulseNativeFunction("split", _split)
        
        if name == "join":
            def _join(lst: Any) -> PulseString:
                if not isinstance(lst, PulseList):
                    self._raise_type("join() expects a list", token)
                parts: list[str] = []
                for el in lst.elements:
                    if not isinstance(el, PulseString):
                        self._raise_type("join() list elements must all be strings", token)
                    parts.append(el.value)
                return PulseString(obj.value.join(parts))
            return PulseNativeFunction("join", _join)
        
        if name == "replace":
            def _replace(old: Any, new: Any) -> PulseString:
                if not isinstance(old, PulseString) or not isinstance(new, PulseString):
                    self._raise_type("replace() expects two string arguments", token)
                return PulseString(obj.value.replace(old.value, new.value))
            return PulseNativeFunction("replace", _replace)
        
        if name == "starts_with":
            def _starts_with(s: Any) -> PulseBoolean:
                if not isinstance(s, PulseString):
                    self._raise_type("starts_with() expects a string", token)
                return PulseBoolean(obj.value.startswith(s.value))
            return PulseNativeFunction("starts_with", _starts_with)
        
        if name == "ends_with":
            def _ends_with(s: Any) -> PulseBoolean:
                if not isinstance(s, PulseString):
                    self._raise_type("ends_with() expects a string", token)
                return PulseBoolean(obj.value.endswith(s.value))
            return PulseNativeFunction("ends_with", _ends_with)
        
        if name == "contains":
            def _contains(s: Any) -> PulseBoolean:
                if not isinstance(s, PulseString):
                    self._raise_type("contains() expects a string", token)
                return PulseBoolean(s.value in obj.value)
            return PulseNativeFunction("contains", _contains)
        
        if name == "length":
            return PulseNativeFunction("length", lambda: PulseNumber(len(obj.value)))
        
        if name == "find":
            def _find(sub: Any, start: Any = None) -> PulseNumber:
                if not isinstance(sub, PulseString):
                    self._raise_type("find() argument must be a string", token)
                s = int(start.value) if start is not None else 0
                return PulseNumber(obj.value.find(sub.value, s))
            return PulseNativeFunction("find", _find)
        
        if name == "index":
            def _index(sub: Any, start: Any = None) -> PulseNumber:
                if not isinstance(sub, PulseString):
                    self._raise_type("index() argument must be a string", token)
                s = int(start.value) if start is not None else 0
                try:
                    return PulseNumber(obj.value.index(sub.value, s))
                except ValueError:
                    self._raise_value(f"'{sub.value}' not found in string", token)
            return PulseNativeFunction("index", _index)
        
        if name == "count":
            def _count(sub: Any) -> PulseNumber:
                if not isinstance(sub, PulseString):
                    self._raise_type("count() argument must be a string", token)
                return PulseNumber(obj.value.count(sub.value))
            return PulseNativeFunction("count", _count)
        
        if name == "format":
            def _format(*args: Any) -> PulseString:
                result = obj.value
                for arg in args:
                    if "{}" not in result:
                        self._raise_value("Too many arguments for format()", token)
                    result = result.replace("{}", self._stringify(arg), 1)
                if "{}" in result:
                    self._raise_value("Not enough arguments for format()", token)
                return PulseString(result)
            return PulseNativeFunction("format", _format)
        
        self._raise_attr(f"String has no method '{name}'", token)
    
    def _dict_method(self, obj: PulseDict, name: str, token: Token) -> PulseNativeFunction:
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
        
        if name == "remove":
            def _remove(key: Any) -> PulseNull:
                if not obj.has(key):
                    self._raise_key(f"Key '{self._stringify(key)}' not found in dict", token)
                obj.remove(key)
                return PulseNull()
            return PulseNativeFunction("remove", _remove)
        
        if name == "length":
            return PulseNativeFunction("length", lambda: PulseNumber(len(obj.entries)))
        
        self._raise_attr(f"Dict has no method '{name}'", token)
    
    def _tensor_property(self, tensor: PulseTensor, name: str, token) -> Any:
        if name == "shape":
            return PulseList([PulseNumber(d) for d in tensor.shape])
        if name == "ndim":
            return PulseNumber(tensor.ndim)
        if name == "T":
            return tensor.T
        if name == "size":
            return PulseNumber(tensor.array.size)
        if name == "dtype":
            return PulseString(str(tensor.array.dtype))
        
        if name == "flatten":
            def flatten():
                return PulseTensor(tensor.array.flatten())
            return PulseNativeMethod(flatten, arity=0)
        
        if name == "reshape":
            def reshape(*args):
                dims = [int(a.value) for a in args]
                try:
                    return PulseTensor(tensor.array.reshape(dims))
                except ValueError as e:
                    self._raise_value(f"reshape failed: {e}", token)
            return PulseNativeMethod(reshape, arity=-1)
        
        if name == "sum":
            def sum_():
                return PulseNumber(float(tensor.array.sum()))
            return PulseNativeMethod(sum_, arity=0)
        
        if name == "mean":
            def mean():
                return PulseNumber(float(tensor.array.mean()))
            return PulseNativeMethod(mean, arity=0)
        
        if name == "max":
            def max_():
                return PulseNumber(float(tensor.array.max()))
            return PulseNativeMethod(max_, arity=0)
        
        if name == "min":
            def min_():
                return PulseNumber(float(tensor.array.min()))
            return PulseNativeMethod(min_, arity=0)
        
        self._raise_attr(f"Tensor has no property '{name}'", token)