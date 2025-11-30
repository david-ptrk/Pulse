# Tokenizer Test Documentation

This document describes the test cases used to verify the functionality of the Pulse Tiny Tokenizer (`tokenizer.py`).
Each test ensures that the tokenizer correctly identifies lexemes, literals, token types, and line numbers.

## 1. Test: Basic Symbols

Input:  
`() = , - + : / *`

Tokens:  
Token(TokenType.LEFT_PAREN, (, None, line=1)  
Token(TokenType.RIGHT_PAREN, ), None, line=1)  
Token(TokenType.ASSIGN, =, None, line=1)  
Token(TokenType.COMMA, ,, None, line=1)  
Token(TokenType.MINUS, -, None, line=1)  
Token(TokenType.PLUS, +, None, line=1)  
Token(TokenType.COLON, :, None, line=1)  
Token(TokenType.DIVIDE, /, None, line=1)  
Token(TokenType.STAR, \*, None, line=1)  
Token(TokenType.EOF, , None, line=1)

## 2. Test: Identifiers

Input:  
`x hello my_var_123`

Tokens:  
Token(TokenType.IDENTIFIER, x, None, line=1)  
Token(TokenType.IDENTIFIER, hello, None, line=1)  
Token(TokenType.IDENTIFIER, my_var_123, None, line=1)  
Token(TokenType.EOF, , None, line=1)

## 3. Test: Numbers

Input:  
`123 45.67`

Tokens:
Token(TokenType.NUMBER, 123, 123.0, line=1)  
Token(TokenType.NUMBER, 45.67, 45.67, line=1)  
Token(TokenType.EOF, , None, line=1)

## 4. Test: Strings

Input:  
`"hello world" "Pulse"`

Tokens:  
Token(TokenType.STRING, "hello world", hello world, line=1)  
Token(TokenType.STRING, "Pulse", Pulse, line=1)  
Token(TokenType.EOF, , None, line=1)

## 5. Test: Keywords

(Currently: "`if`" and "`else`" map to IDENTIFIER)

Input:  
`if else`

Tokens:  
Token(TokenType.IDENTIFIER, if, None, line=1)  
Token(TokenType.IDENTIFIER, else, None, line=1)  
Token(TokenType.EOF, , None, line=1)

(Will later change to `TokenType.IF`, `TokenType.ELSE`)

## 6. Test: Comments

Input:

```
# this is a comment
x = 10
```

Tokens:  
Token(TokenType.NEWLINE, \n, None, line=2)  
Token(TokenType.IDENTIFIER, x, None, line=2)  
Token(TokenType.ASSIGN, =, None, line=2)  
Token(TokenType.NUMBER, 10, 10.0, line=2)  
Token(TokenType.EOF, , None, line=2)

(Anything after `#` is ignored.)

## 7. Test: Newlines & Whitespace

Input:

```
x = 1
y = 2
```

Tokens:  
Token(TokenType.IDENTIFIER, x, None, line=1)  
Token(TokenType.ASSIGN, =, None, line=1)  
Token(TokenType.NUMBER, 1, 1.0, line=1)  
Token(TokenType.NEWLINE, \n, None, line=2)  
Token(TokenType.IDENTIFIER, y, None, line=2)  
Token(TokenType.ASSIGN, =, None, line=2)  
Token(TokenType.NUMBER, 2, 2.0, line=2)  
Token(TokenType.EOF, , None, line=2)

## 8. Test: Full Example (`examples/example1_tokenizer.pul`)

Input:

```
x = 10
y = x + 2
z = x + 2 - 1 * 3
print(y) # 12
```

Output:  
Token(TokenType.IDENTIFIER, x, None, line=1)  
Token(TokenType.ASSIGN, =, None, line=1)  
Token(TokenType.NUMBER, 10, 10.0, line=1)  
Token(TokenType.NEWLINE, \n, None, line=2)  
Token(TokenType.IDENTIFIER, y, None, line=2)  
Token(TokenType.ASSIGN, =, None, line=2)  
Token(TokenType.IDENTIFIER, x, None, line=2)  
Token(TokenType.PLUS, +, None, line=2)  
Token(TokenType.NUMBER, 2, 2.0, line=2)  
Token(TokenType.NEWLINE, \n, None, line=3)  
Token(TokenType.IDENTIFIER, z, None, line=3)  
Token(TokenType.ASSIGN, =, None, line=3)  
Token(TokenType.IDENTIFIER, x, None, line=3)  
Token(TokenType.PLUS, +, None, line=3)  
Token(TokenType.NUMBER, 2, 2.0, line=3)  
Token(TokenType.MINUS, -, None, line=3)  
Token(TokenType.NUMBER, 1, 1.0, line=3)  
Token(TokenType.STAR, \*, None, line=3)  
Token(TokenType.NUMBER, 3, 3.0, line=3)  
Token(TokenType.NEWLINE, \n, None, line=4)  
Token(TokenType.IDENTIFIER, print, None, line=4)  
Token(TokenType.LEFT_PAREN, (, None, line=4)  
Token(TokenType.IDENTIFIER, y, None, line=4)  
Token(TokenType.RIGHT_PAREN, ), None, line=4)  
Token(TokenType.EOF, , None, line=4)

## Summary

This document ensures:

- All token types are tested
- Comments work
- Strings, numbers, keywords, identifiers are validated
- Newlines produce NEWLINE tokens
- EOF is always appended
