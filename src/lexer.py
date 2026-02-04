"""
lexer.py

Lexer (tokenizer) for the Pulse Programming Language.
Responsible for converting raw source code into a stream of tokens to be consumed by the parser.

This file defines:
- TokenType enum
- Token data structure
- Lexer implementation

"""

from src.tokens import (
    TokenType,
    Token,
    KEYWORDS,
)

# -------------------------------------------------------
# LexerError Class
# -------------------------------------------------------
class LexerError(Exception):
    """
    LexerError class helps in generating same format errors.
    """
    def __init__(self, message, line=None, lexeme=None):
        self.message = message
        self.line = line
        self.lexeme = lexeme
        super().__init__(self.__str__())
    def __str__(self):
        info = f"Line {self.line}" if self.line is not None else ""
        lex = f', Lexeme: "{self.lexeme}"' if self.lexeme else ""
        return f"LexerError: {self.message} {info}{lex}"


# -------------------------------------------------------
# Lexer Class
# -------------------------------------------------------
class Lexer:
    """
    The Lexer class scans source code and produces a list of tokens.
    It handles whitespace, comments, strings, numbers, identifiers, keywords,
    operators, and special tokens like indentation and tensor literals.
    """
    def __init__(self, source):
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.indent_stack = [0]

        # Single character tokens mapping for quick lookup
        self.single_char_tokens = {
            '(': TokenType.LEFT_PAREN,
            ')': TokenType.RIGHT_PAREN,
            '[': TokenType.LEFT_BRACKET,
            ']': TokenType.RIGHT_BRACKET,
            '{': TokenType.LEFT_BRACE,
            '}': TokenType.RIGHT_BRACE,
            '%': TokenType.MODULUS,
            ',': TokenType.COMMA,
            ':': TokenType.COLON,
            ';': TokenType.SEMICOLON,
            '.': TokenType.DOT,
        }

    # -------------------------------------------------------
    # Public Methods
    # -------------------------------------------------------
    def scan_tokens(self):
        """Main method to scan the entire source and return tokens list."""
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()

        # Close any remaining indents
        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            self.add_token(TokenType.DEDENT)
        
        # Append EOF token
        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def scan_token(self):
        """Scans a single lexeme and adds the corresponding token."""
        c = self.advance()

        # Newline and Indentation
        if c == '\n':
            self.line += 1
            self.handle_indentation()

            # Emit NEWLINE only if last token is not NEWLINE / INDENT / DEDENT
            if self.tokens and self.tokens[-1].type not in (
                TokenType.NEWLINE,
                TokenType.INDENT,
                TokenType.DEDENT,
            ):
                self.add_token(TokenType.NEWLINE)
            return

        # Skip Comments
        if c == "#":
            while self.peek() not in ['\n', '\0'] and not self.is_at_end():
                self.advance()
            return
        
        # Tensor literal
        if c == '@' and self.peek() == '[':
            self.tensor_literal( )
            return
        
        # Skip Whitespace character
        if c in (" ", "\r", "\t"):
            return

        # Strings literal
        if c == '"':
            self.string()
            return
        
        # Numbers literal
        if c.isdigit():
            self.number()
            return
        
        # Identifier or Keyword
        if c.isalpha() or c == "_":
            self.identifier()
            return
        
        # Multi-character operators
        if c == "!":
            if self.match("="):
                self.add_token(TokenType.BANG_EQUAL)
            else:
                raise LexerError("Unexpected '!' without '='", line=self.line, lexeme="!")
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
        
        if c == "=":
            self.add_token(TokenType.EQUALITY if self.match("=") else TokenType.ASSIGN)
            return
        
        # Single-character tokens
        if c in self.single_char_tokens:
            self.add_token(self.single_char_tokens[c])
            return

        # Unexpected character
        raise LexerError("Unexpected character", line=self.line, lexeme=c)
    
    def handle_indentation(self):
        """
        Handles spaces at the start of a line to generate INDENT/DEDENT tokens.
        Tab are not allowed.
        """
        spaces = 0
        pos = self.current

        # Count leading spaces
        while pos < len(self.source):
            ch = self.source[pos]
            if ch == ' ':
                spaces += 1
            elif ch == '\t':
                raise LexerError("Tabs are not allowed for identation", line=self.line)
            else:
                break
            pos += 1

        # Skip completely blank lines or comment lines
        if pos >= len(self.source) or self.source[pos] in ['\n', '#']:
            return

        last_indent = self.indent_stack[-1]

        if spaces > last_indent:
            self.indent_stack.append(spaces)
            self.start = self.current
            self.add_token(TokenType.INDENT)
        elif spaces < last_indent:
            if spaces not in self.indent_stack:
                raise LexerError("Invalid indentation level", line=self.line)
            while self.indent_stack and spaces < self.indent_stack[-1]:
                self.indent_stack.pop()
                self.start = self.current
                self.add_token(TokenType.DEDENT)

        # Move current pointer past indentation
        self.current = pos
    
    def string(self):
        """Handles string literals enclosed in double quotes"""
        while not self.is_at_end() and self.peek() != '"':
            if self.peek() == '\n':
                self.line += 1
            self.advance()

        if self.is_at_end():
            raise LexerError("Unterminated string", line=self.line, lexeme=self.source[self.start:self.current])
        
        self.advance()
        value = self.source[self.start+1 : self.current-1]
        self.add_token(TokenType.STRING, value)
    
    def number(self):
        """Handles integer and floating-point number literals."""
        while self.peek().isdigit():
            self.advance()
        
        # Fractional part
        if self.peek() == '.' and self.peek_next().isdigit():
            self.advance()
            while self.peek().isdigit():
                self.advance()
        
        text = self.source[self.start:self.current]
        value = float(text) if "." in text else int(text)
        self.add_token(TokenType.NUMBER, value)

    def identifier(self):
        """Handles identifiers and keywords."""
        while self.peek().isalnum() or self.peek() == '_':
            self.advance()
        
        text = self.source[self.start : self.current]

        if text in ("true", "false"):
            self.add_token(TokenType.BOOL, literal=(text=="true"))
            return
        
        token_type = KEYWORDS.get(text, TokenType.IDENTIFIER)
        self.add_token(token_type)

    # No strings allowed inside tensors for now
    def tensor_literal(self):
        """Handles multi-dimensional tensor literals prefixed with '@'."""
        self.start = self.current - 1
        depth = 0

        if self.peek() != '[':
            raise LexerError("Expected '[' after '@'", line=self.line)
        
        while not self.is_at_end():
            ch = self.advance()

            if ch == '"':
                raise LexerError("Strings are not allowed inside tensor literals", line=self.line)

            if ch == "[":
                depth += 1
            elif ch == "]":
                depth -= 1
                if depth == 0:
                    break

        if depth != 0:
            raise LexerError("Unterminated tensor literal", line=self.line, lexeme=self.source[self.start:self.current])

        # Capture entire tensor WITHOUT @
        value = self.source[self.start+1 : self.current]
        self.add_token(TokenType.TENSOR_LITERAL, value)

    # -------------------------------------------------------
    # Utility Methods
    # -------------------------------------------------------
    def is_at_end(self):
        """Checks if the lexer has reached the end of the source."""
        return self.current >= len(self.source)

    def peek(self):
        """Returns the current character without consuming it."""
        return '\0' if self.is_at_end() else self.source[self.current]

    def peek_next(self):
        """Returns the next character without consuming it."""
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]

    def advance(self):
        """Consume and returns the current character."""
        char = self.source[self.current]
        self.current += 1
        return char
    
    def add_token(self, type, literal=None):
        """Creates a token and appends it to the token list."""
        if type is None:
            raise LexerError("Invalid operator", line=self.line, lexeme=self.source[self.start:self.current])
        lexeme = self.source[self.start:self.current]
        if type == TokenType.NEWLINE:
            lexeme = "\\n"
        if type == TokenType.DEDENT:
            lexeme = ""
        self.tokens.append(Token(type, lexeme, literal, self.line))

    def match(self, expected):
        """Matches the next character if it equals 'expected' and consumes it."""
        if self.is_at_end():
            return False
        if self.source[self.current] != expected:
            return False
        self.current += 1
        return True

# -------------------------------------------------------
# Command-line Interface
# -------------------------------------------------------
if __name__ == "__main__":
    import sys
    path = sys.argv[1]

    if not path.endswith(".pul"):
        raise Exception(f'"{path}" is not a .pul file. Pulse only reads .pul, behave.')
    
    with open(path) as f:
        source = f.read()

    lexer = Lexer(source)
    tokens = lexer.scan_tokens()

    for token in tokens:
        print(token)