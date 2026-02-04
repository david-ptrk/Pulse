"""
expressions.py

Defines the abstract syntax tree (AST) for expressions in the Pulse Programming Language.
Includes the Expr base class, concrete expression classes, and the ExprVisitor interface.
"""

from abc import ABC, abstractmethod
from typing import Any, List
from src.tokens import Token

# -------------------------------------------------------
# Visitor Interface
# -------------------------------------------------------
class ExprVisitor(ABC):
    @abstractmethod
    def visit_assign_expr(self, expr: 'Assign') -> Any: ...
    
    @abstractmethod
    def visit_binary_expr(self, expr: 'Binary') -> Any: ...
    
    @abstractmethod
    def visit_call_expr(self, expr: 'Call') -> Any: ...
    
    @abstractmethod
    def visit_get_expr(self, expr: 'Get') -> Any: ...
    
    @abstractmethod
    def visit_grouping_expr(self, expr: 'Grouping') -> Any: ...
    
    @abstractmethod
    def visit_literal_expr(self, expr: 'Literal') -> Any: ...
    
    @abstractmethod
    def visit_logical_expr(self, expr: 'Logical') -> Any: ...
    
    @abstractmethod
    def visit_set_expr(self, expr: 'Set') -> Any: ...
    
    @abstractmethod
    def visit_super_expr(self, expr: 'Super') -> Any: ...
    
    @abstractmethod
    def visit_this_expr(self, expr: 'This') -> Any: ...
    
    @abstractmethod
    def visit_unary_expr(self, expr: 'Unary') -> Any: ...
    
    @abstractmethod
    def visit_variable_expr(self, expr: 'Variable') -> Any: ...

# -------------------------------------------------------
# Base Expression Class
# -------------------------------------------------------
class Expr(ABC):
    @abstractmethod
    def accept(self, visitor: ExprVisitor) -> Any:
        pass

# -------------------------------------------------------
# Concrete Expression Classes
# -------------------------------------------------------
class Assign(Expr):
    def __init__(self, name: Token, value: Expr) -> None:
        self.name = name
        self.value = value
    
    def accept(self, visitor: ExprVisitor) -> Any:
        return visitor.visit_assign_expr(self)

class Binary(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr) -> None:
        self.left = left
        self.operator = operator
        self.right = right
    
    def accept(self, visitor: ExprVisitor) -> Any:
        return visitor.visit_binary_expr(self)

class Unary(Expr):
    def __init__(self, operator: Token, right: Expr) -> None:
        self.operator = operator
        self.right = right
    
    def accept(self, visitor: ExprVisitor) -> Any:
        return visitor.visit_unary_expr(self)

class Literal(Expr):
    def __init__(self, value: Any) -> None:
        self.value = value

    def accept(self, visitor: ExprVisitor) -> Any:
        return visitor.visit_literal_expr(self)

class Grouping(Expr):
    def __init__(self, expression: Expr) -> None:
        self.expression = expression
    
    def accept(self, visitor: ExprVisitor) -> Any:
        return visitor.visit_grouping_expr(self)

class Logical(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr) -> None:
        self.left = left
        self.operator = operator  # AND, OR
        self.right = right
    
    def accept(self, visitor: ExprVisitor) -> Any:
        return visitor.visit_logical_expr(self)

class Variable(Expr):
    def __init__(self, name: Token) -> None:
        self.name = name
    
    def accept(self, visitor: ExprVisitor) -> Any:
        return visitor.visit_variable_expr(self)

class Call(Expr):
    def __init__(self, callee: Expr, paren: Token, arguments: List[Expr]) -> None:
        self.callee = callee
        self.paren = paren
        self.arguments = arguments
    
    def accept(self, visitor: ExprVisitor) -> Any:
        return visitor.visit_call_expr(self)

class Get(Expr):
    def __init__(self, obj: Expr, name: Token) -> None:
        self.obj = obj
        self.name = name
    
    def accept(self, visitor: ExprVisitor) -> Any:
        return visitor.visit_get_expr(self)

class Set(Expr):
    def __init__(self, obj: Expr, name: Token, value: Expr) -> None:
        self.obj = obj
        self.name = name
        self.value = value
    
    def accept(self, visitor: ExprVisitor) -> Any:
        return visitor.visit_set_expr(self)

class This(Expr):
    def __init__(self, keyword: Token) -> None:
        self.keyword = keyword
    
    def accept(self, visitor: ExprVisitor) -> Any:
        return visitor.visit_this_expr(self)

class Super(Expr):
    def __init__(self, keyword: Token, method: Token) -> None:
        self.keyword = keyword
        self.method = method
    
    def accept(self, visitor: ExprVisitor) -> Any:
        return visitor.visit_super_expr(self)