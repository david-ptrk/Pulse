# ast_nodes.py

class Expr:
    pass

class Binary(Expr):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right
    def __repr__(self):
        return f"({self.left} {self.operator.lexeme} {self.right})"

class Literal(Expr):
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return str(self.value)

class Stmt:
    pass

class ExpressionStmt(Stmt):
    def __init__(self, expression):
        self.expression = expression
    def __repr__(self):
        return f"{self.expression};"

class AssignStmt(Stmt):
    def __init__(self, name, value):
        self.name = name
        self.value = value
    def __repr__(self):
        return f"{self.name.lexeme} = {self.value}"
