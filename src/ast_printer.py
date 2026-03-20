"""
ast_printer.py

Provides utilities for printing the Abstract Syntax Tree (AST) of Pulse programs
in a human-readable format. This module is primarily used for debugging and
verifying that the parser correctly converts tokens into structured AST nodes.

The AST printer traverses expression and statement nodes, formatting them
with indentation and hierarchy to reflect the syntactic structure of the program.
It supports all AST node types defined in generate_ast.py, including expressions,
statements, control-flow constructs, and function/class definitions.

This module helps language developers:
- Visualize the structure of parsed Pulse code.
- Confirm that the parser and AST generator produce the intended tree.
- Debug and inspect complex expressions, nested statements, and other language constructs.

The output of this module is not used for execution; it is strictly a developer tool
to aid in language development and testing.
"""

from src import expressions
from src.tokens import Token, TokenType
import pathlib
from src.lexer import Lexer
from src.parser import Parser
import src.statements as stmt
from src.error import PulseLexError, PulseSyntaxError, PulseRuntimeError, report_error

class AstPrinter(expressions.ExprVisitor):
    def print(self, expr: expressions.Expr) -> str:
        return expr.accept(self)
    
    def parenthesize(self, name: str, *parts) -> str:
        pieces = []
        
        for p in parts:
            if isinstance(p, expressions.Expr):
                pieces.append(p.accept(self))
            elif isinstance(p, list):
                for item in p:
                    pieces.append(item.accept(self))
            else:
                pieces.append(str(p))
        
        return f"({name} {' '.join(pieces)})"
    
    def visit_assign_expr(self, expr: expressions.Assign) -> str:
        return self.parenthesize(
            "=",
            self.stringify(expr.name.lexeme),  # instead of expr.name.lexeme
            expr.value
        )
    
    def stringify(self, expr: expressions.Expr) -> str:
        if isinstance(expr, expressions.Variable):
            return expr.name.lexeme
        if isinstance(expr, expressions.MemberAccess):
            return f"{self.stringify(expr.object)}.{expr.name.lexeme}"
        # fallback for other expr types
        return str(expr)
    
    def visit_binary_expr(self, expr: expressions.Binary) -> str:
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)
    
    def visit_call_expr(self, expr: expressions.Call) -> str:
        return self.parenthesize("call", expr.callee, *expr.arguments)
    
    # def visit_get_expr(self, expr: expressions.Get) -> str:
    #     return self.parenthesize(".", expr.obj, expr.name.lexeme)
    
    def visit_grouping_expr(self, expr: expressions.Grouping) -> str:
        return self.parenthesize("group", expr.expression)
    
    def visit_literal_expr(self, expr: expressions.Literal) -> str:
        return "nil" if expr.value is None else str(expr.value)
    
    def visit_logical_expr(self, expr: expressions.Logical) -> str:
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)
    
    # def visit_this_expr(self, expr: expressions.This) -> str:
    #     return "this"
    
    # def visit_set_expr(self, expr: expressions.Set) -> str:
    #     return self.parenthesize("set", expr.obj, expr.name.lexeme, expr.value)
    
    # def visit_super_expr(self, expr: expressions.Super) -> str:
    #     return self.parenthesize("super", expr.method.lexeme)
    
    def visit_unary_expr(self, expr: expressions.Unary) -> str:
        return self.parenthesize(expr.operator.lexeme, expr.right)
    
    def visit_variable_expr(self, expr: expressions.Variable) -> str:
        return expr.name.lexeme
    
    def visit_block_stmt(self, node: stmt.Block):
        return self.parenthesize("block", node.statements)
    
    def visit_expression_stmt(self, node: stmt.Expression):
        return self.print(node.expression)
    
    def visit_if_stmt(self, node: stmt.If):
        text = "if " + self.print(node.condition)
        text += " then: " + self.print(node.then_branch)
        
        for cond, branch in node.elif_branches:
            text += " elif " + self.print(cond)
            text += " then: " + self.print(branch)
        
        if node.else_branch:
            text += " else: " + self.print(node.else_branch)

        return text
    
    def visit_while_stmt(self, node: stmt.While):
        return f"(while {self.print(node.condition)} {self.print(node.body)})"
    
    def visit_for_stmt(self, node: stmt.For):
        return f"(for {node.var.lexeme} in {self.print(node.iterable)} {self.print(node.body)})"
    
    def visit_break_stmt(self, node: stmt.Break):
        return "break"
    
    def visit_continue_stmt(self, node: stmt.Continue):
        return "continue"
    
    def visit_pass_stmt(self, node: stmt.Pass):
        return "pass"
    
    def visit_return_stmt(self, node: stmt.Return):
        if node.value is None:
            return "return"
        return f"(return {self.print(node.value)})"
    
    def visit_function_stmt(self, node: stmt.Function):
        params = ", ".join(p.lexeme for p in node.params)
        return f"(def {node.name.lexeme} ({params}) {self.print(node.body)})"
    
    def visit_class_stmt(self, node: stmt.Class):
        text = f"(class {node.name.lexeme}"        
        for s in node.body:
            text += " " + self.print(s)
        text += ")"
        
        return text
    
    def visit_try_stmt(self, node: stmt.Try) -> str:
        parts = [f"(try {self.print(node.try_block)}"]
        
        for exc_type, block in node.except_blocks:
            if exc_type:
                parts.append(f"(except {exc_type.lexeme} {self.print(block)})")
            else:
                parts.append(f"(except {self.print(block)})")
        
        if node.finally_block:
            parts.append(f"(finally {self.print(node.finally_block)})")
        
        return " ".join(parts) + ")"
    
    def visit_memberaccess_expr(self, expr: expressions.MemberAccess) -> str:
        return self.parenthesize(".", expr.object, expr.name.lexeme)

# -------------------------------------------------
# Quick test
# -------------------------------------------------
if __name__ == "__main__":
    import sys
    file_path = pathlib.Path(__file__).parent.parent / "tests/code.pul"
    with open(file_path) as f:
        source = f.read()
    
    try:
        lexer = Lexer(source)
        tokens = lexer.scan_tokens()
        
        parser = Parser(tokens, source)
        stmts = parser.parse()
        
        printer = AstPrinter()
        for s in stmts:
            if s is not None:
                print(printer.print(s))
    except (PulseLexError, PulseSyntaxError, PulseRuntimeError) as e:
        report_error(e)
        sys.exit(1)
