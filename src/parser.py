from typing import List, Optional

from src import expressions as expr
from src import statements as stmt
from src.tokens import Token, TokenType

class ParseError(RuntimeError):
    def __init__(self, token: Token, message: str) -> None:
        super().__init__(message)
        self.token = token


class Parser:
    def __init__(self, tokens: List[Token]) -> None:
        self.tokens = tokens
        self.current = 0
    
    # Core helper functions
    def peek(self) -> Token:
        return self.tokens[self.current]
    
    def previous(self) -> Token:
        return self.tokens[self.current - 1]
    
    def is_at_end(self) -> bool:
        return self.peek().type == TokenType.EOF
    
    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1
        return self.previous()
    
    def check(self, typ: TokenType) -> bool:
        if self.is_at_end():
            return False
        return self.peek().type == typ
    
    def match(self, *types: TokenType) -> bool:
        for t in types:
            if self.check(t):
                self.advance()
                return True
        return False
    
    def consume(self, typ: TokenType, message: str) -> Token:
        if self.check(typ):
            return self.advance()
        raise ParseError(self.peek(), message)
    
    # Entry
    def parse(self) -> List[stmt.Stmt]:
        statements: List[stmt.Stmt] = []
        
        while not self.is_at_end():
            statements.append(self.statement())
        
        return statements
    
    def statement(self) -> Optional[stmt.Stmt]:
        if self.match(TokenType.INDENT):
            return self.block()
        
        if self.match(TokenType.DEF):
            return self.parse_func_stmt()
        if self.match(TokenType.CLASS):
            return self.parse_class_stmt()
        
        if self.match(TokenType.IF):
            return self.parse_if_stmt()
        if self.match(TokenType.WHILE):
            return self.parse_while_stmt()
        if self.match(TokenType.FOR):
            return self.parse_for_stmt()
        
        if self.match(TokenType.TRY):
            return self.parse_try_stmt()
        
        if self.match(TokenType.BREAK):
            return stmt.Break()
        if self.match(TokenType.CONTINUE):
            return stmt.Continue()
        if self.match(TokenType.RETURN):
            return self.parse_return_stmt()
        if self.match(TokenType.PASS):
            return stmt.Pass()
        
        # Skip empty statements
        if self.match(TokenType.NEWLINE):
            return None        
        # Stop parsing expressions if we hit block end
        if self.check(TokenType.DEDENT) or self.is_at_end():
            return None
        
        expr_stmt = self.expression()
        self.match(TokenType.NEWLINE)
        return stmt.Expression(expr_stmt)

    def block(self) -> stmt.Stmt:
        statements: List[stmt.Stmt] = []
        
        while not self.check(TokenType.DEDENT) and not self.is_at_end():
            s = self.statement()
            if s is not None:
                statements.append(s)
        
        self.consume(TokenType.DEDENT, "Block not closed")
        return stmt.Block(statements)
    
    def parse_if_stmt(self) -> stmt.Stmt:
        condition = self.expression()
        self.match(TokenType.COLON)
        
        then_branch = self.statement()
        
        elif_branches = []
        while self.match(TokenType.ELIF):
            elif_condition = self.expression()
            self.match(TokenType.COLON)
            elif_stmt = self.statement()
            elif_branches.append((elif_condition, elif_stmt))
        
        else_branch = None
        if self.match(TokenType.ELSE):
            self.match(TokenType.COLON)
            else_branch = self.statement()
        
        return stmt.If(condition, then_branch, elif_branches, else_branch)
    
    def parse_while_stmt(self) -> stmt.Stmt:
        condition = self.expression()
        self.consume(TokenType.COLON, "Expected ':' after while condition")
        body = self.statement()  # single statement for now
        return stmt.While(condition, body)
    
    def parse_for_stmt(self) -> stmt.Stmt:
        var_token = self.consume(TokenType.IDENTIFIER, "Expected loop variable after 'for'")
        self.consume(TokenType.IN, "Expected 'in' after loop variable")
        iterable = self.expression()
        self.consume(TokenType.COLON, "Expected ':' after iterable")
        
        # Will work for loop depths later
        # self.loop_depth += 1
        body = self.statement()
        # self.loop_depth -= 1
        
        return stmt.For(var_token, iterable, body)
    
    def parse_func_stmt(self) -> stmt.Stmt:
        name = self.consume(TokenType.IDENTIFIER, "Expect function name.")
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after function name.")
        
        params: list[Token] = []
        if not self.check(TokenType.RIGHT_PAREN):
            params.append(
                self.consume(TokenType.IDENTIFIER, "Expect parameter name.")
            )
            while self.match(TokenType.COMMA):
                if self.check(TokenType.RIGHT_PAREN):
                    break
                params.append(
                    self.consume(TokenType.IDENTIFIER, "Expect parameter name.")
                )
        
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")
        self.consume(TokenType.COLON, "Expect ':' before function body.")
        
        self.consume(TokenType.INDENT, "Expect block indentation")
        body = self.block()
        return stmt.Function(name, params, body)
    
    def parse_class_stmt(self) -> stmt.Stmt:
        name = self.consume(TokenType.IDENTIFIER, "Expect class name.")
        self.consume(TokenType.COLON, "Expect ':' after class name.")
        
        self.consume(TokenType.INDENT, "Expect class body indentation")
        
        body: list[stmt.Stmt] = []
        while not self.check(TokenType.DEDENT) and not self.is_at_end():
            # Skip empty lines
            if self.match(TokenType.NEWLINE):
                continue
            # Methods
            if self.match(TokenType.DEF):
                body.append(self.parse_func_stmt())
            # Assignments at class level
            else:
                expr_stmt = self.expression()
                self.match(TokenType.NEWLINE)
                body.append(stmt.Expression(expr_stmt))
        
        self.consume(TokenType.DEDENT, "Class body not closed")
        return stmt.Class(name, body)
    
    def parse_try_stmt(self) -> stmt.Stmt:
        self.consume(TokenType.COLON, "Expected ':' after 'try'")
        try_block = self.statement()
        
        self.consume(TokenType.EXCEPT, "Expected 'except' keyword")
        self.consume(TokenType.COLON, "Expected ':' after 'except'")
        except_block = self.statement()
        
        finally_block = None
        if self.match(TokenType.FINALLY):
            self.consume(TokenType.COLON, "Expected ':' after 'finally'")
            finally_block = self.statement()
        
        return stmt.Try(try_block, except_block, finally_block)
    
    def parse_return_stmt(self) -> stmt.Stmt:
        value = None        
        if not (self.check(TokenType.NEWLINE) or self.check(TokenType.DEDENT) or self.is_at_end()):
            value = self.expression()
        
        self.match(TokenType.NEWLINE)
        return stmt.Return(value)
    
    
    def expression(self) -> expr.Expr:
        return self.assignment()
    
    def assignment(self) -> expr.Expr:
        left = self.logic()
        
        if self.match(TokenType.ASSIGN):
            equals = self.previous()
            value = self.assignment()
            
            if isinstance(left, expr.Variable):
                return expr.Assign(left.name, value)
            
            raise ParseError("Invalid assignment target")
        
        return left
    
    def logic(self) -> expr.Expr:
        node = self.equality()
        
        while self.match(TokenType.AND, TokenType.OR):
            op = self.previous()
            right = self.equality()
            node = expr.Logical(node, op, right)
        
        return node
    
    def equality(self) -> expr.Expr:
        node = self.comparison()
        
        while self.match(TokenType.EQUALITY, TokenType.BANG_EQUAL):
            op = self.previous()
            right = self.comparison()
            node = expr.Binary(node, op, right)
        
        return node
    
    def comparison(self) -> expr.Expr:
        node = self.addition()
        
        while self.match(
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL
        ):
            op = self.previous()
            right = self.addition()
            node = expr.Binary(node, op, right)
        
        return node
    
    def addition(self) -> expr.Expr:
        node = self.multiplication()
        
        while self.match(TokenType.PLUS, TokenType.MINUS):
            op = self.previous()
            right = self.multiplication()
            node = expr.Binary(node, op, right)
        
        return node
    
    def multiplication(self) -> expr.Expr:
        node = self.unary()
        
        while self.match(TokenType.STAR, TokenType.SLASH, TokenType.MODULUS):
            op = self.previous()
            right = self.unary()
            node = expr.Binary(node, op, right)
        
        return node
    
    def unary(self) -> expr.Expr:
        if self.match(TokenType.MINUS, TokenType.NOT):
            op = self.previous()
            right = self.unary()
            return expr.Unary(op, right)
        
        return self.primary()
    
    # Primary
    def primary(self) -> expr.Expr:
        if self.match(TokenType.NUMBER, TokenType.STRING, TokenType.BOOL):
            return expr.Literal(self.previous().literal)
        
        if self.match(TokenType.IDENTIFIER):
            name_token = self.previous()
            if self.match(TokenType.LEFT_PAREN):
                arguments: list[expr.Expr] = []
                if not self.check(TokenType.RIGHT_PAREN):
                    while True:
                        arguments.append(self.expression())
                        if not self.match(TokenType.COMMA):
                            break
                paren = self.consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments")
                return expr.Call(expr.Variable(name_token), paren, arguments)
            return expr.Variable(name_token)
        
        if self.match(TokenType.LEFT_PAREN):
            e = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')'")
            return expr.Grouping(e)
        
        raise ParseError(self.peek(), "Expect expression")