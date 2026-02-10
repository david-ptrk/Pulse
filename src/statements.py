from abc import ABC, abstractmethod
from typing import Any
from src.expressions import Expr
from src.tokens import Token

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
    def visit_for_stmt(self, expr: 'For') -> Any:
        pass

    @abstractmethod
    def visit_break_stmt(self, expr: 'Break') -> Any:
        pass

    @abstractmethod
    def visit_continue_stmt(self, expr: 'Continue') -> Any:
        pass

    @abstractmethod
    def visit_return_stmt(self, expr: 'Return') -> Any:
        pass

    @abstractmethod
    def visit_function_stmt(self, expr: 'Function') -> Any:
        pass

    @abstractmethod
    def visit_class_stmt(self, expr: 'Class') -> Any:
        pass

    @abstractmethod
    def visit_try_stmt(self, expr: 'Try') -> Any:
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

class For(Stmt):
    def __init__(self, var: Token, iterable: Expr, body: Stmt) -> None:
        self.var = var
        self.iterable = iterable
        self.body = body

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_for_stmt(self)

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

class Return(Stmt):
    def __init__(self, value: Expr | None) -> None:
        self.value = value

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_return_stmt(self)

class Function(Stmt):
    def __init__(self, name: Token, params: list[Token], body: list[Stmt]) -> None:
        self.name = name
        self.params = params
        self.body = body

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_function_stmt(self)

class Class(Stmt):
    def __init__(self, name: Token, body: list[Stmt]) -> None:
        self.name = name
        self.body = body

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_class_stmt(self)

class Try(Stmt):
    def __init__(self, try_block: Stmt, except_block: Stmt) -> None:
        self.try_block = try_block
        self.except_block = except_block

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_try_stmt(self)

