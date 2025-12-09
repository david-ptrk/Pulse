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
    DOT = auto()
    TRANSPOSE = auto()

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
    "dot": TokenType.DOT,
    "transpose": TokenType.TRANSPOSE,
    "True": TokenType.BOOL,
    "False": TokenType.BOOL,
}

class Token:
    def __init__(self, type: TokenType, lexeme: str, literal: object, line: int):
        self.type = type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line
    
    def __str__(self):
        return f"{self.type.name} {self.lexeme} {self.literal}"
    
    def __repr__(self):
        return f"Token(type={self.type}, lex='{self.lexeme}', lit={self.literal}, line={self.line})"

class Lexer:
    def __init__(self, source):
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1

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
        while not self.isAtEnd():
            self.start = self.current
            self.scan_token()
        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def scan_token(self):
        c = self.advance()

        if c == '#':  # comment
            while self.peek() != '\n' and not self.isAtEnd():
                self.advance()
            return

        if c in self.single_char_tokens:
            self.addToken(self.single_char_tokens[c])
            return

        if c in (' ', '\r', '\t'):
            return

        if c == '\n':
            self.line += 1
            self.addToken(TokenType.NEWLINE)
            return

        if c == '"':
            self.string()
            return

        if c.isdigit():
            self.number()
            return

        if c.isalpha() or c == '_':
            self.identifier()
            return

        # Multi-char operators
        if c == '!':
            self.addToken(TokenType.BANG_EQUAL if self.match('=') else None)
            if self.tokens[-1].type is None:
                raise Exception(f'Unexpected "!" at line {self.line}')
            return
        elif c == '=':
            self.addToken(TokenType.EQUAL_EQUAL if self.match('=') else TokenType.EQUAL)
            return
        elif c == '<':
            self.addToken(TokenType.LESS_EQUAL if self.match('=') else TokenType.LESS)
            return
        elif c == '>':
            self.addToken(TokenType.GREATER_EQUAL if self.match('=') else TokenType.GREATER)
            return

        raise Exception(f'Unexpected character "{c}" at line {self.line}')

    def isAtEnd(self):
        return self.current >= len(self.source)

    # TODO: implement advance(), peek(), match(), addToken(), string(), number(), identifier()
