from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, List, Tuple
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

    @abstractmethod
    def visit_call_expr(self, expr: 'Call') -> Any:
        pass

    @abstractmethod
    def visit_memberaccess_expr(self, expr: 'MemberAccess') -> Any:
        pass

    @abstractmethod
    def visit_logical_expr(self, expr: 'Logical') -> Any:
        pass

    @abstractmethod
    def visit_list_expr(self, expr: 'List') -> Any:
        pass

    @abstractmethod
    def visit_dict_expr(self, expr: 'Dict') -> Any:
        pass

    @abstractmethod
    def visit_index_expr(self, expr: 'Index') -> Any:
        pass

    @abstractmethod
    def visit_setindex_expr(self, expr: 'SetIndex') -> Any:
        pass

    @abstractmethod
    def visit_slice_expr(self, expr: 'Slice') -> Any:
        pass

    @abstractmethod
    def visit_multiindex_expr(self, expr: 'MultiIndex') -> Any:
        pass

    @abstractmethod
    def visit_setmember_expr(self, expr: 'SetMember') -> Any:
        pass

    @abstractmethod
    def visit_fstring_expr(self, expr: 'FString') -> Any:
        pass

    @abstractmethod
    def visit_tensor_expr(self, expr: 'Tensor') -> Any:
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

class Call(Expr):
    def __init__(self, callee: Expr, paren: Token, arguments: List[Expr], keyword_arguments: List[Tuple[Token, Expr]]) -> None:
        self.callee = callee
        self.paren = paren
        self.arguments = arguments
        self.keyword_arguments = keyword_arguments

    def accept(self, visitor: ExprVisitor) -> Any:
        return visitor.visit_call_expr(self)

class MemberAccess(Expr):
    def __init__(self, object: Expr, name: Token) -> None:
        self.object = object
        self.name = name

    def accept(self, visitor: ExprVisitor) -> Any:
        return visitor.visit_memberaccess_expr(self)

class Logical(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr) -> None:
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor: ExprVisitor) -> Any:
        return visitor.visit_logical_expr(self)

class List(Expr):
    def __init__(self, elements: List[Expr]) -> None:
        self.elements = elements

    def accept(self, visitor: ExprVisitor) -> Any:
        return visitor.visit_list_expr(self)

class Dict(Expr):
    def __init__(self, keys: List[Expr], values: List[Expr]) -> None:
        self.keys = keys
        self.values = values

    def accept(self, visitor: ExprVisitor) -> Any:
        return visitor.visit_dict_expr(self)

class Index(Expr):
    def __init__(self, object: Expr, index: Expr) -> None:
        self.object = object
        self.index = index

    def accept(self, visitor: ExprVisitor) -> Any:
        return visitor.visit_index_expr(self)

class SetIndex(Expr):
    def __init__(self, object: Expr, index: Expr, value: Expr) -> None:
        self.object = object
        self.index = index
        self.value = value

    def accept(self, visitor: ExprVisitor) -> Any:
        return visitor.visit_setindex_expr(self)

class Slice(Expr):
    def __init__(self, lower: Optional[Expr], upper: Optional[Expr]) -> None:
        self.lower = lower
        self.upper = upper

    def accept(self, visitor: ExprVisitor) -> Any:
        return visitor.visit_slice_expr(self)

class MultiIndex(Expr):
    def __init__(self, object: Expr, indices: List[Expr]) -> None:
        self.object = object
        self.indices = indices

    def accept(self, visitor: ExprVisitor) -> Any:
        return visitor.visit_multiindex_expr(self)

class SetMember(Expr):
    def __init__(self, object: Expr, name: Token, value: Expr) -> None:
        self.object = object
        self.name = name
        self.value = value

    def accept(self, visitor: ExprVisitor) -> Any:
        return visitor.visit_setmember_expr(self)

class FString(Expr):
    def __init__(self, parts: List[Expr]) -> None:
        self.parts = parts

    def accept(self, visitor: ExprVisitor) -> Any:
        return visitor.visit_fstring_expr(self)

class Tensor(Expr):
    def __init__(self, value: Any) -> None:
        self.value = value

    def accept(self, visitor: ExprVisitor) -> Any:
        return visitor.visit_tensor_expr(self)

