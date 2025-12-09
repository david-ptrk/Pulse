from enum import Enum, auto

class TokenType(Enum):
    # Single charcters
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    LEFT_BRACKET = auto()
    RIGHT_BRACKET = auto()
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()
    MINUS = auto()
    PLUS = auto()
    STAR = auto()
    SLASH = auto()
    MODULUS = auto()
    COMMA = auto()
    COLON = auto()
    SEMICOLON = auto()
    DOT = auto()
    TRANSPOSE = auto()

    # Literals
    IDENTIFIER = auto()
    NUMBER = auto()
    STRING = auto()
    BOOL = auto()
    TENSOR_LITERAL = auto()

    # One or Two Characters
    EQUAL = auto()
    PLUS_EQUAL = auto()
    MINUS_EQUAL = auto()
    STAR_EQUAL = auto()
    SLASH_EQUAL = auto()
    EQUAL_EQUAL = auto()
    BANG_EQUAL = auto()
    LESS = auto()
    GREATER = auto()
    LESS_EQUAL = auto()
    GREATER_EQUAL = auto()

    # Special
    INDENT = auto()
    DEDENT = auto()
    NEWLINE = auto()
    COMMENT = auto()
    EOF = auto()

    # Keywords
    IF = auto()
    ELSE = auto()
    ELIF = auto()
    DEF = auto()
    RETURN = auto()
    WHILE = auto()
    FOR = auto()
    BREAK = auto()
    CONTINUE = auto()
    PASS = auto()
    TRY = auto()
    EXCEPT = auto()
    IMPORT = auto()
    FROM = auto()
    AS = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    CLASS = auto()
    SELF = auto()
    IN = auto()
    DEL = auto()

# Keywords
KEYWORDS = {
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "elif": TokenType.ELIF,
    "def": TokenType.DEF,
    "return": TokenType.RETURN,
    "while": TokenType.WHILE,
    "for": TokenType.FOR,
    "break": TokenType.BREAK,
    "continue": TokenType.CONTINUE,
    "pass": TokenType.PASS,
    "try": TokenType.TRY,
    "except": TokenType.EXCEPT,
    "import": TokenType.IMPORT,
    "from": TokenType.FROM,
    "as": TokenType.AS,
    "and": TokenType.AND,
    "or": TokenType.OR,
    "not": TokenType.NOT,
    "class": TokenType.CLASS,
    "self": TokenType.SELF,
    "in": TokenType.IN,
    "del": TokenType.DEL,
    "True": TokenType.BOOL,
    "False": TokenType.BOOL,
}

class Token:
    def __init__(self, type: TokenType, lexeme: str, literal: object, line: int):
        self.type = type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line
    
    def __repr__(self):
        return f"Token({self.type}, {self.lexeme}, {self.literal}, line={self.line})"

class Lexer:
    def __init__(self, source):
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.indent_stack = [0]

        self.single_char_tokens = {
            '(': TokenType.LEFT_PAREN,
            ')': TokenType.RIGHT_PAREN,
            '[': TokenType.LEFT_BRACKET,
            ']': TokenType.RIGHT_BRACKET,
            '{': TokenType.LEFT_BRACE,
            '}': TokenType.RIGHT_BRACE,
            '-': TokenType.MINUS,
            '+': TokenType.PLUS,
            '*': TokenType.STAR,
            '/': TokenType.SLASH,
            '%': TokenType.MODULUS,
            ',': TokenType.COMMA,
            ':': TokenType.COLON,
            ';': TokenType.SEMICOLON,
        }

    def scan_tokens(self):
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()

        # Close remaining indents
        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            self.add_token(TokenType.DEDENT)
        
        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def scan_token(self):
        c = self.advance()

        # Whitespace at start of line for identation
        if c == '\n':
            self.add_token(TokenType.NEWLINE)
            self.line += 1

            # Check identation of next line
            spaces = 0
            while not self.is_at_end() and self.peek() in [' ', '\t']:
                spaces += 4 if self.peek() == '\t' else 1
                self.advance()
            
            if self.peek() == '\n' or self.peek() == '#':
                return
            
            last_indent = self.indent_stack[-1]
            if spaces > last_indent:
                self.indent_stack.append(spaces)
                self.add_token(TokenType.INDENT)
            elif spaces < last_indent:
                while self.indent_stack and spaces < self.indent_stack[-1]:
                    self.indent_stack.pop()
                    self.add_token(TokenType.DEDENT)
            return

        # Comments
        if c == "#":
            while self.peek() not in ['\n', '\0'] and not self.is_at_end():
                self.advance()
            comment_text = self.source[self.start+1 : self.current]
            self.add_token(TokenType.COMMENT, comment_text)
            return
        
        # Tensor literal
        if c == '@' and self.peek() == '[' and self.peek_next() == '[':
            self.advance()
            self.advance() 
            self.tensor_literal( )
            return
        
        # Whitespace
        if c in [" ", "\r", "\t"]:
            return

        # Strings
        if c == '"':
            self.string()
            return
        
        # Numbers
        if c.isdigit():
            self.number()
            return
        
        # Identifier / Keywords
        if c.isalpha() or c == "_":
            self.identifier()
            return
        
        # Multi-char operators
        if c == "!":
            if self.match("="):
                self.add_token(TokenType.BANG_EQUAL)
            else:
                raise Exception(f'Unexpected "!" at line {self.line}')
            return
        elif c in "+-*/":
            if self.match("="):
                t = {
                    '+': TokenType.PLUS_EQUAL,
                    '-': TokenType.MINUS_EQUAL,
                    '*': TokenType.STAR_EQUAL,
                    '/': TokenType.SLASH_EQUAL,
                }[c]
            else :
                t = {
                    '+': TokenType.PLUS,
                    '-': TokenType.MINUS,
                    '*': TokenType.STAR,
                    '/': TokenType.SLASH,
                }[c]
            self.add_token(t)
            return
        
        if c == "<":
            self.add_token(TokenType.LESS_EQUAL if self.match("=") else TokenType.LESS)
            return
        
        if c == ">":
            self.add_token(TokenType.GREATER_EQUAL if self.match("=") else TokenType.GREATER)
            return
        
        # Single-character tokens
        if c in self.single_char_tokens:
            self.add_token(self.single_char_tokens[c])
            return

        raise Exception(f'Unexpected character "{c}" at line {self.line}')
    
    def string(self):
        while not self.is_at_end() and self.peek() != '"':
            if self.peek() == '\n':
                self.line += 1
            self.advance()

        if self.is_at_end():
            raise Exception(f'Unterminated string at line {self.line}')
        
        self.advance()
        value = self.source[self.start+1 : self.current-1]
        self.add_token(TokenType.STRING, value)
    
    def number(self):
        while self.peek().isdigit():
            self.advance()
        
        # Fractional part
        if self.peek() == '.' and self.peek_next().isdigit():
            self.advance()
            while self.peek().isdigit():
                self.advance()
        
        value = float(self.source[self.start : self.current])
        self.add_token(TokenType.NUMBER, value)

    def identifier(self):
        while self.peek().isalnum() or self.peek() == '_':
            self.advance()
        
        text = self.source[self.start : self.current]

        if text in ("True", "False"):
            self.add_token(TokenType.BOOL, literal=(text=="True"))
            return
        
        token_type = KEYWORDS.get(text, TokenType.IDENTIFIER)
        self.add_token(token_type)

    def tensor_literal(self):
        depth = 2
        in_string = False

        while not self.is_at_end() and depth > 0:
            ch = self.advance()

            if ch == '"' and self.source[self.current - 2] != "\\":
                in_string = not in_string

            if not in_string:
                if ch == "[":
                    depth += 1
                elif ch == "]":
                    depth -= 1

        if depth != 0:
            raise Exception(f"Unterminated tensor literal at line {self.line}")

        value = self.source[self.start:self.current]
        self.add_token(TokenType.TENSOR_LITERAL, value)
    
    def is_at_end(self):
        return self.current >= len(self.source)

    def peek(self):
        return '\0' if self.is_at_end() else self.source[self.current]

    def peek_next(self):
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]

    def advance(self):
        char = self.source[self.current]
        self.current += 1
        return char
    
    def add_token(self, type, literal=None):
        if type is None:
            raise Exception(f"Invalid operator at line {self.line}")
        lexeme = self.source[self.start:self.current]
        if type == TokenType.NEWLINE:
            lexeme = "\\n"
        self.tokens.append(Token(type, lexeme, literal, self.line))

    def match(self, expected):
        if self.is_at_end():
            return False
        if self.source[self.current] != expected:
            return False
        self.current += 1
        return True
