from src import expressions
from src.tokens import Token, TokenType

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
    
    # def visit_call_expr(self, expr: expressions.Call) -> str:
    #     return self.parenthesize("call", expr.callee, *expr.arguments)
    
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
    import pathlib
    file_path = pathlib.Path(__file__).parent.parent / "tests/code.pul"
    with open(file_path) as f:
        source = f.read()
    
    from src.lexer import Lexer
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    
    from src.parser import Parser
    parser = Parser(tokens)
    stmts = parser.parse()
    
    import src.statements as stmt
    printer = AstPrinter()
    for s in stmts:
        if isinstance(s, stmt.Expression):
            print(printer.print(s.expression))
        elif isinstance(s, stmt.Print):
            print("print", printer.print(s.expression))
