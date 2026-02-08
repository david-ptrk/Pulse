from abc import ABC, abstractmethod
from typing import Any
from src.expressions import Expr

class StmtVisitor(ABC):
    @abstractmethod
    def visit_expression_stmt(self, expr: 'Expression') -> Any:
        pass

    @abstractmethod
    def visit_block_stmt(self, expr: 'Block') -> Any:
        pass

    @abstractmethod
    def visit_if_stmt(self, expr: 'If') -> Any:
        pass

    @abstractmethod
    def visit_while_stmt(self, expr: 'While') -> Any:
        pass

    @abstractmethod
    def visit_break_stmt(self, expr: 'Break') -> Any:
        pass

    @abstractmethod
    def visit_continue_stmt(self, expr: 'Continue') -> Any:
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

class Block(Stmt):
    def __init__(self, statements: list[Stmt]) -> None:
        self.statements = statements

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_block_stmt(self)

class If(Stmt):
    def __init__(self, condition: Expr, then_branch: Stmt, else_branch: Stmt | None) -> None:
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_if_stmt(self)

class While(Stmt):
    def __init__(self, condition: Expr, body: Stmt) -> None:
        self.condition = condition
        self.body = body

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_while_stmt(self)

class Break(Stmt):
    def __init__(self, ) -> None:
        pass

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_break_stmt(self)

class Continue(Stmt):
    def __init__(self, ) -> None:
        pass

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_continue_stmt(self)

