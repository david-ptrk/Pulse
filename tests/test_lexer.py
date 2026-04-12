import pytest
from src.lexer import Lexer
from src.tokens import TokenType

def lex(source):
    tokens = Lexer(source).scan_tokens()
    return [t.type for t in tokens if t.type != TokenType.EOF]

def test_number_integer():
    tokens = Lexer("42").scan_tokens()
    assert tokens[0].literal == 42
    assert tokens[0].type == TokenType.NUMBER

def test_number_float():
    tokens = Lexer("3.14").scan_tokens()
    assert tokens[0].literal == 3.14

def test_string_double_quote():
    tokens = Lexer('"hello"').scan_tokens()
    assert tokens[0].type == TokenType.STRING
    assert tokens[0].literal == "hello"

def test_string_single_quote():
    tokens = Lexer("'world'").scan_tokens()
    assert tokens[0].literal == "world"

def test_boolean_true():
    tokens = Lexer("true").scan_tokens()
    assert tokens[0].type == TokenType.BOOL
    assert tokens[0].literal == True

def test_boolean_false():
    tokens = Lexer("false").scan_tokens()
    assert tokens[0].literal == False

def test_plus():
    assert TokenType.PLUS in lex("1 + 2")

def test_minus():
    assert TokenType.MINUS in lex("1 - 2")

def test_equality():
    assert TokenType.EQUALITY in lex("a == b")

def test_not_equal():
    assert TokenType.BANG_EQUAL in lex("a != b")

def test_plus_equal():
    assert TokenType.PLUS_EQUAL in lex("x += 1")

def test_less_equal():
    assert TokenType.LESS_EQUAL in lex("x <= 5")

def test_comment_ignored():
    types = lex("# this is a comment\n42")
    assert TokenType.NUMBER in types
    # Comment text should not appear as a token
    assert TokenType.IDENTIFIER not in types

def test_string_escape_newline():
    tokens = Lexer(r'"hello\nworld"').scan_tokens()
    assert tokens[0].literal == "hello\nworld"

def test_string_escape_tab():
    tokens = Lexer(r'"col1\tcol2"').scan_tokens()
    assert tokens[0].literal == "col1\tcol2"

def test_tensor_literal():
    tokens = Lexer("@[1, 2, 3]").scan_tokens()
    assert tokens[0].type == TokenType.TENSOR_LITERAL

def test_unexpected_character():
    from src.error import PulseLexError
    with pytest.raises(PulseLexError):
        Lexer("$bad").scan_tokens()

def test_unterminated_string():
    from src.error import PulseLexError
    with pytest.raises(PulseLexError):
        Lexer('"not closed').scan_tokens()

def test_tabs_not_allowed():
    from src.error import PulseLexError
    with pytest.raises(PulseLexError):
        Lexer("if true:\n\tx = 1").scan_tokens()

def test_indent_dedent():
    source = "if true:\n    x = 1\n"
    types = lex(source)
    assert TokenType.INDENT in types
    assert TokenType.DEDENT in types