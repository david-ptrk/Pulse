"""
tokens.py

Defines the token system used by the Pulse programming language lexer.

In the compilation pipeline, raw source code is first processed by the
lexer (scanner), which converts the stream of characters into a sequence
of tokens. A token represents the smallest meaningful unit of the language,
such as identifiers, keywords, operators, literals, and punctuation.

This module provides:
- The TokenType enumeration containing all token categories used by Pulse.
- The Token class, which stores information about a token instance
    (type, lexeme, literal value, and source location).
- Keyword mappings used by the lexer to distinguish identifiers from 
    reserved language keywords.

These tokens are later consumed by the parser to construct the Abstract
Syntax Tree (AST), which represents the structural syntax of a Pulse program.
"""

from __future__ import annotations
from enum import Enum, auto
from typing import Any

# -------------------------------------------------------
# TokenType Enum
# -------------------------------------------------------
class TokenType(Enum):
    # Single character tokens
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
    AT = auto()
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
    NULL = auto()
    TENSOR_LITERAL = auto()
    
    # One or Two Characters operators
    ASSIGN = auto()
    EQUALITY = auto()
    PLUS_EQUAL = auto()
    MINUS_EQUAL = auto()
    STAR_EQUAL = auto()
    SLASH_EQUAL = auto()
    PERCENT_EQUAL = auto()
    BANG_EQUAL = auto()
    LESS = auto()
    GREATER = auto()
    LESS_EQUAL = auto()
    GREATER_EQUAL = auto()
    
    # Special tokens
    INDENT = auto()
    DEDENT = auto()
    NEWLINE = auto()
    EOF = auto()
    FSTRING = auto()
    INT_DIVIDE = auto()
    STATIC = auto()
    PIPE = auto()
    LAMBDA = auto()
    
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
    FINALLY = auto()
    IMPORT = auto()
    FROM = auto()
    AS = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    CLASS = auto()
    IN = auto()
    DEL = auto()
    SELF = auto()

# Mapping of string keywords to TokenType for easy lookup
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
    "finally": TokenType.FINALLY,
    "import": TokenType.IMPORT,
    "from": TokenType.FROM,
    "as": TokenType.AS,
    "and": TokenType.AND,
    "or": TokenType.OR,
    "not": TokenType.NOT,
    "class": TokenType.CLASS,
    "in": TokenType.IN,
    "del": TokenType.DEL,
    "dot": TokenType.DOT,
    "transpose": TokenType.TRANSPOSE,
    "null": TokenType.NULL,
    "None": TokenType.NULL,
    "static": TokenType.STATIC,
    "NaN": TokenType.NUMBER,
    "lambda": TokenType.LAMBDA,
}

# -------------------------------------------------------
# Token Class
# -------------------------------------------------------
class Token:
    """
    Represents a single token in the source code.
    Attributes:
        type (TokenType): Type of the token
        lexeme (str): Original text in source code
        literal (object): Parsed value of token
        line (int): Line number in source file
    """
    __slots__ = ("type", "lexeme", "literal", "line", "column")
    
    def __init__(self, type: TokenType, lexeme: str, literal: Any, line: int, column: int) -> None:
        self.type = type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line
        self.column = column
    
    def __repr__(self) -> str:
        return f"Token({self.type}, '{self.lexeme}', {self.literal}, line={self.line}, column={self.column})"
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Token):
            return NotImplemented
        return (
            self.type == other.type
            and self.lexeme == other.lexeme
            and self.literal == other.literal
        )
    
    def __hash__(self) -> int:
        return hash((self.type, self.lexeme, self.literal))
