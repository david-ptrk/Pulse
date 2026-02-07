from abc import ABC, abstractmethod
from typing import Any
from src.expressions import Expr

class StmtVisitor(ABC):
    @abstractmethod
    def visit_expression_stmt(self, expr: 'Expression') -> Any:
        pass

    @abstractmethod
    def visit_if_stmt(self, expr: 'If') -> Any:
        pass



class Stmt(ABC):
    @abstractmethod
    def accept(self, visitor: StmtVisitor) -> Any:
        pass

class Expression(Stmt):
    def __init__(self, expression: Expr) -> None:
        self.expression = expression

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_expression_stmt(self)

class If(Stmt):
    def __init__(self, condition: Expr, then_branch: Stmt, else_branch: Stmt | None) -> None:
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_if_stmt(self)

