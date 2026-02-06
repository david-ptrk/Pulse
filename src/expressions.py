from abc import ABC, abstractmethod
from typing import Any, List
from src.tokens import Token

class ExprVisitor(ABC):
    @abstractmethod
    def visit_assign_expr(self, expr: 'Assign') -> Any:
        pass

    @abstractmethod
    def visit_binary_expr(self, expr: 'Binary') -> Any:
        pass

    @abstractmethod
    def visit_unary_expr(self, expr: 'Unary') -> Any:
        pass

    @abstractmethod
    def visit_literal_expr(self, expr: 'Literal') -> Any:
        pass

    @abstractmethod
    def visit_variable_expr(self, expr: 'Variable') -> Any:
        pass

    @abstractmethod
    def visit_grouping_expr(self, expr: 'Grouping') -> Any:
        pass



class Expr(ABC):
    @abstractmethod
    def accept(self, visitor: ExprVisitor) -> Any:
        pass

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

class Variable(Expr):
    def __init__(self, name: Token) -> None:
        self.name = name

    def accept(self, visitor: ExprVisitor) -> Any:
        return visitor.visit_variable_expr(self)

class Grouping(Expr):
    def __init__(self, expression: Expr) -> None:
        self.expression = expression

    def accept(self, visitor: ExprVisitor) -> Any:
        return visitor.visit_grouping_expr(self)

