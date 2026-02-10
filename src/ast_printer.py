from src import expressions
from src.tokens import Token, TokenType
import pathlib
from src.lexer import Lexer
from src.parser import Parser
import src.statements as stmt

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
        return self.parenthesize("=", expr.name.lexeme, expr.value)
    
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
    
    # def visit_logical_expr(self, expr: expressions.Logical) -> str:
    #     return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)
    
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
        return f"(try {self.print(node.try_block)} (except {self.print(node.except_block)}))"

# -------------------------------------------------
# Quick test
# -------------------------------------------------
if __name__ == "__main__":
    # exp = expressions.Binary(
    #     expressions.Unary(
    #         Token(TokenType.MINUS, "-", "", 1),
    #         expressions.Literal(123)
    #     ),
    #     Token(TokenType.STAR, "*", "", 1),
    #     expressions.Grouping(expressions.Literal(45.67))
    # )
    file_path = pathlib.Path(__file__).parent.parent / "tests/code.pul"
    with open(file_path) as f:
        source = f.read()
    
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    
    parser = Parser(tokens)
    stmts = parser.parse()
    
    printer = AstPrinter()
    for s in stmts:
        if s is not None:
            print(printer.print(s))
        # if isinstance(s, stmt.Expression):
        #     print(printer.print(s.expression))
        # elif isinstance(s, stmt.If):
        #     print("if", printer.print(s.condition))
        #     print("then:", printer.print(s.then_branch))
        #     if s.else_branch:
        #         print("else:", printer.print(s.else_branch))
