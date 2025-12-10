# Pulse Language — Token Types

This document defines all token categories used by the Pulse lexer. Tokens are grouped for clarity (keywords, literals, operators, punctuation, structural tokens).

## 1. Identifiers

| Token      | Description                                              |
| ---------- | -------------------------------------------------------- |
| IDENTIFIER | Variable names, function names, user-defined identifiers |

Rules:

- Start with letter or \_
- Followed by letters, digits, \_
- Examples: `x`, `_hidden`, `myTensor3`

## 2. Literals

| Token          | Description                                       |
| -------------- | ------------------------------------------------- |
| NUMBER         | Integer or float numeric literal                  |
| STRING         | `"hello"` style string                            |
| BOOL           | `True` or `False`                                 |
| TENSOR_LITERAL | Tensor literal, e.g. `[1, 2, 3]`, `[[1,2],[3,4]]` |

## 3. Keywords

Pulse Keywords:

`def`, `return`, `if`, `elif`, `else`, `while`, `for`, `break`, `continue`, `pass`, `try`, `except`, `import`, `from`, `as`, `and`, `or`, `not`, `True`, `False`, `class`, `self`, `in`, `del`, `dot`, `transpose`

## 4. Operators

### Arithmetic

`+ - * / %`

### Tensor / Linear Algebra

`dot` `transpose`

### Assignment

`= += -= \*= /=`

### Comparison

`== != < > <= >=`

### Logical

`and` `or` `not`

## 5. Punctuation & Delimiters

`( )  [ ]  { }  ,  :  ;`

## 6. Structural Tokens

Indentation-based (Python-style)

`INDENT`
`DEDENT`
`NEWLINE`

## 7. Special Tokens

`EOF` - End of file  
`ERROR` - Invalid or unrecognized token
