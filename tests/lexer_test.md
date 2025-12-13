# Lexer Test Documentation

This document describes the test cases used to verify the functionality of the Pulse's Lexer / Tokenizer (`lexer.py`).
Each test ensures that the tokenizer correctly identifies lexemes, literals, token types, and line numbers.

## 1. Test: Numbers

Input:

```
10
3.14
0.001
```

Tokens:  
Token(TokenType.NUMBER, 10, 10.0, line=1)  
Token(TokenType.NEWLINE, \n, None, line=2)  
Token(TokenType.NUMBER, 3.14, 3.14, line=2)  
Token(TokenType.NEWLINE, \n, None, line=3)  
Token(TokenType.NUMBER, 0.001, 0.001, line=3)  
Token(TokenType.EOF, , None, line=3)

## 2. Test: Identifiers vs Keywords

Input:

```
x = 5
while x < 10:
    pass
```

Tokens:  
Token(TokenType.IDENTIFIER, x, None, line=1)  
Token(TokenType.ASSIGN, =, None, line=1)  
Token(TokenType.NUMBER, 5, 5.0, line=1)  
Token(TokenType.NEWLINE, \n, None, line=2)  
Token(TokenType.WHILE, while, None, line=2)  
Token(TokenType.IDENTIFIER, x, None, line=2)  
Token(TokenType.LESS, <, None, line=2)  
Token(TokenType.NUMBER, 10, 10.0, line=2)  
Token(TokenType.COLON, :, None, line=2)  
Token(TokenType.INDENT, , None, line=3)  
Token(TokenType.PASS, pass, None, line=3)  
Token(TokenType.DEDENT, , None, line=3)  
Token(TokenType.EOF, , None, line=3)

## 3. Test: Operators & delimiters

Input:

```
a + b * (c - d)
```

Tokens:
Token(TokenType.IDENTIFIER, a, None, line=1)  
Token(TokenType.PLUS, +, None, line=1)  
Token(TokenType.IDENTIFIER, b, None, line=1)  
Token(TokenType.STAR, \*, None, line=1)  
Token(TokenType.LEFT_PAREN, (, None, line=1)  
Token(TokenType.IDENTIFIER, c, None, line=1)  
Token(TokenType.MINUS, -, None, line=1)  
Token(TokenType.IDENTIFIER, d, None, line=1)  
Token(TokenType.RIGHT_PAREN, ), None, line=1)  
Token(TokenType.EOF, , None, line=1)

## 4. Test: Lists (future tensors)

Input:

```
[1, 2, 3]
```

Tokens:  
Token(TokenType.LEFT_BRACKET, [, None, line=1)
Token(TokenType.NUMBER, 1, 1.0, line=1)
Token(TokenType.COMMA, ,, None, line=1)
Token(TokenType.NUMBER, 2, 2.0, line=1)
Token(TokenType.COMMA, ,, None, line=1)
Token(TokenType.NUMBER, 3, 3.0, line=1)
Token(TokenType.RIGHT_BRACKET, ], None, line=1)  
Token(TokenType.EOF, , None, line=1)

## 5. Test: Invalid character

Input:

```
x = 5 $
```

Tokens:  
Exception: Unexpected character "$" at line 1

## 6. Test: Full Example (`examples/example1_lexer.pul`)

Input:

```
# Pulse lexer final test

x = 10
y = 3.5

a = @[1, 2, 3]
b = @[[4, 5, 6]]

sum = x + y * 2
diff = x - y
prod = x * y
ratio = x / y

result = (sum + diff) * (prod - ratio)

if result > 10:
    return result
else:
    return 0
```

Output:
Token(TokenType.IDENTIFIER, x, None, line=3)  
Token(TokenType.ASSIGN, =, None, line=3)  
Token(TokenType.NUMBER, 10, 10.0, line=3)  
Token(TokenType.NEWLINE, \n, None, line=4)  
Token(TokenType.IDENTIFIER, y, None, line=4)  
Token(TokenType.ASSIGN, =, None, line=4)  
Token(TokenType.NUMBER, 3.5, 3.5, line=4)  
Token(TokenType.NEWLINE, \n, None, line=5)  
Token(TokenType.IDENTIFIER, a, None, line=6)  
Token(TokenType.ASSIGN, =, None, line=6)  
Token(TokenType.TENSOR*LITERAL, @[1, 2, 3], [1, 2, 3], line=6)  
Token(TokenType.NEWLINE, \n, None, line=7)  
Token(TokenType.IDENTIFIER, b, None, line=7)  
Token(TokenType.ASSIGN, =, None, line=7)  
Token(TokenType.TENSOR_LITERAL, @[[4, 5, 6]], [[4, 5, 6]], line=7)  
Token(TokenType.NEWLINE, \n, None, line=8)  
Token(TokenType.IDENTIFIER, sum, None, line=9)  
Token(TokenType.ASSIGN, =, None, line=9)  
Token(TokenType.IDENTIFIER, x, None, line=9)  
Token(TokenType.PLUS, +, None, line=9)  
Token(TokenType.IDENTIFIER, y, None, line=9)  
Token(TokenType.STAR, *, None, line=9)  
Token(TokenType.NUMBER, 2, 2.0, line=9)  
Token(TokenType.NEWLINE, \n, None, line=10)  
Token(TokenType.IDENTIFIER, diff, None, line=10)  
Token(TokenType.ASSIGN, =, None, line=10)  
Token(TokenType.IDENTIFIER, x, None, line=10)  
Token(TokenType.MINUS, -, None, line=10)  
Token(TokenType.IDENTIFIER, y, None, line=10)  
Token(TokenType.NEWLINE, \n, None, line=11)  
Token(TokenType.IDENTIFIER, prod, None, line=11)  
Token(TokenType.ASSIGN, =, None, line=11)  
Token(TokenType.IDENTIFIER, x, None, line=11)  
Token(TokenType.STAR, \*, None, line=11)  
Token(TokenType.IDENTIFIER, y, None, line=11)  
Token(TokenType.NEWLINE, \n, None, line=12)  
Token(TokenType.IDENTIFIER, ratio, None, line=12)  
Token(TokenType.ASSIGN, =, None, line=12)  
Token(TokenType.IDENTIFIER, x, None, line=12)  
Token(TokenType.SLASH, /, None, line=12)  
Token(TokenType.IDENTIFIER, y, None, line=12)  
Token(TokenType.NEWLINE, \n, None, line=13)  
Token(TokenType.IDENTIFIER, result, None, line=14)  
Token(TokenType.ASSIGN, =, None, line=14)  
Token(TokenType.LEFT_PAREN, (, None, line=14)  
Token(TokenType.IDENTIFIER, sum, None, line=14)  
Token(TokenType.PLUS, +, None, line=14)  
Token(TokenType.IDENTIFIER, diff, None, line=14)  
Token(TokenType.RIGHT_PAREN, ), None, line=14)  
Token(TokenType.STAR, \*, None, line=14)  
Token(TokenType.LEFT_PAREN, (, None, line=14)  
Token(TokenType.IDENTIFIER, prod, None, line=14)  
Token(TokenType.MINUS, -, None, line=14)  
Token(TokenType.IDENTIFIER, ratio, None, line=14)  
Token(TokenType.RIGHT_PAREN, ), None, line=14)  
Token(TokenType.NEWLINE, \n, None, line=15)  
Token(TokenType.IF, if, None, line=16)  
Token(TokenType.IDENTIFIER, result, None, line=16)  
Token(TokenType.GREATER, >, None, line=16)  
Token(TokenType.NUMBER, 10, 10.0, line=16)  
Token(TokenType.COLON, :, None, line=16)  
Token(TokenType.INDENT, , None, line=17)  
Token(TokenType.RETURN, return, None, line=17)  
Token(TokenType.IDENTIFIER, result, None, line=17)  
Token(TokenType.DEDENT, , None, line=18)  
Token(TokenType.ELSE, else, None, line=18)  
Token(TokenType.COLON, :, None, line=18)  
Token(TokenType.INDENT, , None, line=19)  
Token(TokenType.RETURN, return, None, line=19)  
Token(TokenType.NUMBER, 0, 0.0, line=19)  
Token(TokenType.DEDENT, , None, line=19)  
Token(TokenType.EOF, , None, line=19)

## Summary

This document ensures:

- Numbers are recognized and their literals are correctly stored.
- Identifiers and keywords are distinguished based on the Pulse keyword set.
- Operators and delimiters are correctly tokenized, including single- and multi-character operators.
- Lists and future tensor structures are properly tokenized using brackets, commas, and numbers.
- Invalid characters produce clear, descriptive errors with accurate line numbers.
- Full example code is tokenized consistently with Pulse’s Pythonic syntax and dynamic semantics.
