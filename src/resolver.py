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

from src.expressions import ExprVisitor
from src.statements import StmtVisitor

class Resolver(ExprVisitor, StmtVisitor):
    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.scopes = []
    
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
        if name in scope:
            raise Exception(f"Variable '{name.lexeme}' already declared in this scope")
        scope[name.lexeme] = False
    
    def define(self, name):
        if not self.scopes:
            return
        self.scopes[-1][name.lexeme] = True
    
    # Resolution Logic
    def resolve_local(self, expr, name):
        for i in range(len(self.scopes) - 1, -1, -1):
            if name.lexeme in self.scopes[i]:
                distance = len(self.scopes) - 1 - i
                self.interpreter.resolve(expr, distance)
                return
        # Not Found -> Global
    
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
        
        if stmt.else_branch:
            self.resolve_stmt(stmt.else_branch)
    
    def visit_while_stmt(self, stmt):
        self.resolve_expr(stmt.condition)
        self.resolve_stmt(stmt.body)
    
    def visit_return_stmt(self, stmt):
        if stmt.value:
            self.resolve_expr(stmt.value)
    
    def visit_pass_stmt(self, stmt):
        pass
    
    # Expressions
    def visit_literal_expr(self, expr):
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
    
    def visit_variable_expr(self, expr):
        if self.scopes:
            scope = self.scopes[-1]
            if expr.name.lexeme in scope and scope[expr.name.lexeme] is False:
                raise Exception(f"Cannot read local variable '{expr.name.lexeme}' before assignment")
        self.resolve_local(expr, expr.name)
    
    def visit_assign_expr(self, expr):
        self.resolve_expr(expr.value)
        self.resolve_local(expr, expr.name)
    
    def visit_call_expr(self, expr):
        self.resolve_expr(expr.callee)
        for arg in expr.arguments:
            self.resolve_expr(arg)
    
    # Not yet implemented
    def visit_function_stmt(self, stmt):
        pass
    
    def visit_class_stmt(self, stmt):
        pass
    
    def visit_memberaccess_expr(self, expr):
        pass
    
    def visit_for_stmt(self, stmt):
        pass
    
    def visit_try_stmt(self, stmt):
        pass
    
    def visit_continue_stmt(self, stmt):
        pass
    
    def visit_break_stmt(self, stmt):
        pass