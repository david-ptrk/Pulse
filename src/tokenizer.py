from enum import Enum, auto

class TokenType(Enum):
    # Single characters
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    COMMA = auto()
    MINUS = auto()
    PLUS = auto()
    COLON = auto()
    SLASH = auto()
    STAR = auto()
    
    # Literals
    IDENTIFIER = auto()
    NUMBER = auto()
    STRING = auto()
    
    # Special
    NEWLINE = auto()
    EOF = auto()

# Add keywords here
KEYWORDS = {
    "if": TokenType.IDENTIFIER, # TokenType here will be changed to TokenType.IF
    "else": TokenType.IDENTIFIER,
}

class Token:
    def __init__(self, type, lexeme, literal, line):
        self.type = type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line
    
    def __repr__(self):
        return f"Token({self.type}, {self.lexeme!r}, {self.literal}, line={self.line})"

class Tokenize:
    def __init__(self, source):
        self.source = source
        self.start = 0
        self.current = 0
        self.line = 1
        self.tokens = []

        self.single_char_tokens = {
            '(': TokenType.LEFT_PAREN,
            ')': TokenType.RIGHT_PAREN,
            ',': TokenType.COMMA,
            '-': TokenType.MINUS,
            '+': TokenType.PLUS,
            ':': TokenType.COLON,
            '*': TokenType.STAR,
        }
    
    def scanTokens(self):
        while not self.isAtEnd():
            self.start = self.current
            self.scanToken()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens
    
    def scanToken(self):
        c = self.advance()

        # Single-character tokens via map
        if c in self.single_char_tokens:
            self.addToken(self.single_char_tokens[c])
            return

        # Slash or comment
        if c == '/':
            if self.peek() == '/':
                while self.peek() != '\n' and not self.isAtEnd():
                    self.advance()
            else:
                self.addToken(TokenType.SLASH)
            return

        # Whitespace
        if c in (' ', '\r', '\t'):
            return

        # Newline
        if c == '\n':
            self.line += 1
            self.addToken(TokenType.NEWLINE)
            return

        # String literal
        if c == '"':
            self.string()
            return

        # Number literal
        if c.isdigit():
            self.number()
            return

        # Identifier or keyword
        if c.isalpha() or c == '_':
            self.identifier()
            return

        raise Exception(f"Unexpected character '{c}' at line {self.line}")
    
    def string(self):
        while not self.isAtEnd() and self.peek() != '"':
            if self.peek() == '\n':
                self.line += 1
            self.advance()

        if self.isAtEnd():
            raise Exception(f"Unterminated string at line {self.line}")

        self.advance()  # closing "
        value = self.source[self.start+1 : self.current-1]
        self.addToken(TokenType.STRING, value)

    def number(self):
        while self.peek().isdigit():
            self.advance()

        # Fractional part
        if self.peek() == '.' and self.peekNext().isdigit():
            self.advance()
            while self.peek().isdigit():
                self.advance()

        num_literal = float(self.source[self.start:self.current])
        self.addToken(TokenType.NUMBER, num_literal)

    def identifier(self):
        while self.peek().isalnum() or self.peek() == '_':
            self.advance()

        text = self.source[self.start:self.current]
        token_type = KEYWORDS.get(text, TokenType.IDENTIFIER)
        self.addToken(token_type)

    def isAtEnd(self):
        return self.current >= len(self.source)

    def peek(self):
        return '\0' if self.isAtEnd() else self.source[self.current]

    def peekNext(self):
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]

    def advance(self):
        char = self.source[self.current]
        self.current += 1
        return char

    def addToken(self, type, literal=None):
        text = self.source[self.start:self.current]
        self.tokens.append(Token(type, text, literal, self.line))

if __name__ == "__main__":
    import sys
    path = sys.argv[1]
    source = open(path).read()

    tokenizer = Tokenize(source)
    tokens = tokenizer.scanTokens()

    for t in tokens:
        print(t)
