"""
resolver.py

Performs static scope resolution for the Pulse language.

The resolver walks the AST before interpretation and determines
how many scopes away each variable is defined. This allows the
interpreter to perform fast and correct variable lookup using
lexical scoping instead of dynamic lookup.

It also detects errors such as:
- Using a variable before it is defined in the same scope
"""

from __future__ import annotations
from enum import Enum, auto
from typing import Any, Optional
from src.expressions import ExprVisitor
from src.statements import StmtVisitor
from src.tokens import Token
from src.error import PulseSemanticError

class FunctionType(Enum):
    NONE = auto()
    FUNCTION = auto()
    METHOD = auto()

class ClassType(Enum):
    NONE = auto()
    CLASS = auto()

class Resolver(ExprVisitor, StmtVisitor):
    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.scopes = [{}]
        self.current_class = ClassType.NONE
        self.current_function = FunctionType.NONE
        self.loop_depth = 0
    
    # Entry Point
    def resolve(self, statements):
        for stmt in statements:
            self.resolve_stmt(stmt)
    
    def resolve_stmt(self, stmt):
        stmt.accept(self)
    
    def resolve_expr(self, expr):
        expr.accept(self)
    
    # Scope Management
    def begin_scope(self):
        self.scopes.append({})
    
    def end_scope(self):
        self.scopes.pop()
    
    def declare(self, name):
        if not self.scopes:
            return
        scope = self.scopes[-1]
        if name.lexeme in scope:
            raise PulseSemanticError(
                f"Variable '{name.lexeme}' already declared in this scope",
                line=getattr(name, "line", None),
                column=getattr(name, "column", None)
            )
        scope[name.lexeme] = False
    
    def define(self, name):
        if not self.scopes:
            return
        self.scopes[-1][name.lexeme] = True
    
    # Resolution Logic
    def resolve_local(self, expr, name):
        found = False
        
        for i in range(len(self.scopes) - 1, -1, -1):
            if name.lexeme in self.scopes[i]:
                distance = len(self.scopes) - 1 - i
                self.interpreter.resolve(expr, distance)
                found = True
                return
        
        if not found:
            self.interpreter.resolve(expr, None)
    
    def resolve_function(self, func, func_type):
        enclosing_function = self.current_function
        self.current_function = func_type
        self.begin_scope()
        
        if func_type == FunctionType.METHOD and not func.is_static:
            self.scopes[-1]["self"] = True
        
        for param in func.params:
            self.scopes[-1][param.lexeme] = True
        
        self.resolve(func.body.statements)
        self.end_scope()
        self.current_function = enclosing_function
    
    # Statements
    def visit_block_stmt(self, stmt):
        self.begin_scope()
        self.resolve(stmt.statements)
        self.end_scope()
    
    def visit_expression_stmt(self, stmt):
        self.resolve_expr(stmt.expression)
    
    def visit_if_stmt(self, stmt):
        self.resolve_expr(stmt.condition)
        self.resolve_stmt(stmt.then_branch)
        
        for cond, branch in stmt.elif_branches:
            self.resolve_expr(cond)
            self.resolve_stmt(branch)
        
        if stmt.else_branch is not None:
            self.resolve_stmt(stmt.else_branch)
    
    def visit_while_stmt(self, stmt):
        self.loop_depth += 1
        self.resolve_expr(stmt.condition)
        self.resolve_stmt(stmt.body)
        self.loop_depth -= 1
    
    def visit_return_stmt(self, stmt):
        if self.current_function is FunctionType.NONE:
            raise PulseSemanticError(
                "Cannot return from top-level code",
            )
        
        if stmt.value is not None:
            self.resolve_expr(stmt.value)
    
    def visit_pass_stmt(self, stmt):
        pass
    
    def visit_function_stmt(self, stmt):
        self.declare(stmt.name)
        self.define(stmt.name)
        
        func_type = FunctionType.METHOD if self.current_class is not ClassType.NONE else FunctionType.FUNCTION
        self.resolve_function(stmt, func_type)
    
    def visit_class_stmt(self, stmt):
        self.declare(stmt.name)
        self.define(stmt.name)
        
        enclosing_class = self.current_class
        self.current_class = ClassType.CLASS
        
        for base in stmt.bases:
            self.resolve_local(stmt, base)
        
        self.begin_scope()
        for name_tok, value in stmt.class_vars:
            self.resolve_expr(value)
            self.scopes[-1][name_tok.lexeme] = True
        
        for method in stmt.methods:
            self.resolve_function(method, FunctionType.METHOD)
        
        self.end_scope()
        self.current_class = enclosing_class
    
    def visit_for_stmt(self, stmt):
        self.resolve_expr(stmt.iterable)
        self.begin_scope()
        
        self.scopes[-1][stmt.var.lexeme] = True
        self.loop_depth += 1
        self.resolve_stmt(stmt.body)
        self.loop_depth -= 1
        
        self.end_scope()
    
    def visit_try_stmt(self, stmt):
        self.resolve_stmt(stmt.try_block)
        
        for exc_type_expr, exception_var, block in stmt.except_blocks:
            self.begin_scope()
            
            if exception_var is not None:
                self.scopes[-1][exception_var.lexeme] = True
            
            if exc_type_expr is not None:
                self.resolve_expr(exc_type_expr)
            
            self.resolve_stmt(block)
            self.end_scope()
        
        if stmt.finally_block is not None:
            self.resolve_stmt(stmt.finally_block)
    
    def visit_continue_stmt(self, stmt):
        if self.loop_depth == 0:
            raise PulseSemanticError(
                "Cannot use 'continue' outside loop",
                token=stmt.keyword
            )
    
    def visit_break_stmt(self, stmt):
        if self.loop_depth == 0:
            raise PulseSemanticError(
                "Cannot use 'break' outside loop",
                token=stmt.keyword
            )
    
    def visit_import_stmt(self, stmt):
        pass
    
    # Expressions
    def visit_literal_expr(self, expr):
        pass
    
    def visit_tensor_expr(self, expr):
        pass
    
    def visit_grouping_expr(self, expr):
        self.resolve_expr(expr.expression)
    
    def visit_unary_expr(self, expr):
        self.resolve_expr(expr.right)
    
    def visit_binary_expr(self, expr):
        self.resolve_expr(expr.left)
        self.resolve_expr(expr.right)
    
    def visit_logical_expr(self, expr):
        self.resolve_expr(expr.left)
        self.resolve_expr(expr.right)
    
    def visit_variable_expr(self, expr) -> None:
        name_lexeme = expr.name.lexeme
        
        if name_lexeme == "self":
            return
        
        for i in range(len(self.scopes) - 1, -1, -1):
            scope = self.scopes[i]
            if name_lexeme in scope:
                if scope[name_lexeme] is False:
                    raise PulseSemanticError(
                        f"Cannot read local variable '{name_lexeme}' before assignment",
                        token=expr.name
                    )
                break
        
        self.resolve_local(expr, expr.name)
    
    def visit_assign_expr(self, expr):
        self.resolve_expr(expr.value)
        self.resolve_local(expr, expr.name)
    
    def visit_call_expr(self, expr):
        self.resolve_expr(expr.callee)
        for arg in expr.arguments:
            self.resolve_expr(arg)
        for _, value in expr.keyword_arguments:
            self.resolve_expr(value)
    
    def visit_list_expr(self, expr):
        for element in expr.elements:
            self.resolve_expr(element)
    
    def visit_dict_expr(self, expr):
        for key, value in zip(expr.keys, expr.values):
            self.resolve_expr(key)
            self.resolve_expr(value)
    
    def visit_index_expr(self, expr):
        self.resolve_expr(expr.object)
        self.resolve_expr(expr.index)
    
    def visit_setindex_expr(self, expr):
        self.resolve_expr(expr.object)
        self.resolve_expr(expr.index)
        self.resolve_expr(expr.value)
    
    def visit_slice_expr(self, expr):
        if expr.lower:
            self.resolve_expr(expr.lower)
        if expr.upper:
            self.resolve_expr(expr.upper)
    
    def visit_multiindex_expr(self, expr):
        self.resolve_expr(expr.object)
        for index in expr.indices:
            self.resolve_expr(index)
    
    def visit_setmember_expr(self, expr):
        self.resolve_expr(expr.object)
        self.resolve_expr(expr.value)
    
    def visit_memberaccess_expr(self, expr):
        self.resolve_expr(expr.object)
    
    def visit_fstring_expr(self, expr):
        for part in expr.parts:
            self.resolve_expr(part)