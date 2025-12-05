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