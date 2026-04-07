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
from src.error import PulseSemanticError

class Resolver(ExprVisitor, StmtVisitor):
    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.scopes = [{}]
        self.current_class = None
        self.current_function = None
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
        for i in range(len(self.scopes) - 1, -1, -1):
            if name.lexeme in self.scopes[i]:
                distance = len(self.scopes) - 1 - i
                self.interpreter.resolve(expr, distance)
                return
        # Not Found -> Global
    
    def resolve_function(self, func, func_type):
        enclosing_function = self.current_function
        self.current_function = func_type
        self.begin_scope()
        
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
        
        if stmt.else_branch:
            self.resolve_stmt(stmt.else_branch)
    
    def visit_while_stmt(self, stmt):
        self.loop_depth += 1
        self.resolve_expr(stmt.condition)
        self.resolve_stmt(stmt.body)
        self.loop_depth -= 1
    
    def visit_return_stmt(self, stmt):
        if self.current_function is None:
            raise PulseSemanticError(
                "Cannot return from top-level code",
            )
        
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
        for i in range(len(self.scopes) - 1, -1, -1):
            scope = self.scopes[i]
            if expr.name.lexeme in scope:
                if scope[expr.name.lexeme] is False:
                    raise PulseSemanticError(
                        f"Cannot read local variable '{expr.name.lexeme}' before assignment",
                        token=expr.name
                    )
                break
        else:
            pass
        
        self.resolve_local(expr, expr.name)
    
    def visit_assign_expr(self, expr):
        self.resolve_expr(expr.value)
        self.resolve_local(expr, expr.name)
    
    def visit_call_expr(self, expr):
        self.resolve_expr(expr.callee)
        for arg in expr.arguments:
            self.resolve_expr(arg)
    
    def visit_list_expr(self, expr):
        for element in expr.elements:
            self.resolve_expr(element)
    
    def visit_function_stmt(self, stmt):
        self.declare(stmt.name)
        self.define(stmt.name)
        
        enclosing_function = self.current_function
        self.current_function = "METHOD" if self.current_class else "FUNCTION"
        
        self.resolve_function(stmt, self.current_function)
        self.current_function = enclosing_function
    
    def visit_class_stmt(self, stmt):
        # No inheritance yet
        self.declare(stmt.name)
        self.define(stmt.name)
        
        enclosing_class = self.current_class
        self.current_class = "CLASS"
        
        self.begin_scope()
        self.scopes[-1]["this"] = True
        for statement in stmt.body:
            self.resolve_stmt(statement)
        
        self.end_scope()
        self.current_class = enclosing_class
    
    def visit_memberaccess_expr(self, expr):
        self.resolve_expr(expr.object)
    
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