# Pulse Language — Token Types

This document defines all token categories used by the Pulse lexer.
Tokens are grouped by category and reflect the current implementation.

---

## 1. Identifiers & Literals

| Token          | Description                                                 | Examples                          |
| -------------- | ----------------------------------------------------------- | --------------------------------- |
| IDENTIFIER     | Variable names, function names, user-defined identifiers    | `x`, `_hidden`, `myModel`         |
| NUMBER         | Integer or floating-point numeric literal                   | `42`, `3.14`, `-7`, `0.5`         |
| STRING         | Single or double quoted string, or triple-quoted multi-line | `"hello"`, `'world'`, `"""..."""` |
| FSTRING        | F-string literal                                            | `f"hello {name}"`                 |
| BOOL           | Boolean literal                                             | `True`, `False`                   |
| NULL           | Null literal                                                | `null`                            |
| TENSOR_LITERAL | Tensor literal prefixed with `@`                            | `@[[1, 2], [3, 4]]`               |

### Identifier Rules

- Must start with a letter or underscore `_`
- Followed by any combination of letters, digits, or underscores
- Case-sensitive

---

## 2. Keywords

| Token    | Lexeme     | Description                       |
| -------- | ---------- | --------------------------------- |
| IF       | `if`       | Conditional statement             |
| ELIF     | `elif`     | Else-if branch                    |
| ELSE     | `else`     | Else branch                       |
| WHILE    | `while`    | While loop                        |
| FOR      | `for`      | For loop                          |
| BREAK    | `break`    | Break out of loop                 |
| CONTINUE | `continue` | Skip to next loop iteration       |
| PASS     | `pass`     | No-op statement                   |
| RETURN   | `return`   | Return from function              |
| DEF      | `def`      | Function definition               |
| CLASS    | `class`    | Class definition                  |
| STATIC   | `static`   | Static method modifier            |
| SELF     | `self`     | Instance reference inside methods |
| IMPORT   | `import`   | Module import                     |
| FROM     | `from`     | From-import statement             |
| AS       | `as`       | Alias in import or except         |
| TRY      | `try`      | Try block                         |
| EXCEPT   | `except`   | Exception handler                 |
| FINALLY  | `finally`  | Finally block                     |
| RAISE    | `raise`    | Raise an exception                |
| AND      | `and`      | Logical AND (short-circuit)       |
| OR       | `or`       | Logical OR (short-circuit)        |
| NOT      | `not`      | Logical NOT                       |
| IN       | `in`       | Membership test / for-loop        |
| IS       | `is`       | Identity comparison               |
| DEL      | `del`      | Delete variable, index, or member |
| MATCH    | `match`    | Pattern matching subject          |
| CASE     | `case`     | Pattern matching case             |
| LAMBDA   | `lambda`   | Anonymous function                |

---

## 3. Operators

### Arithmetic

| Token      | Lexeme | Description              |
| ---------- | ------ | ------------------------ |
| PLUS       | `+`    | Addition / string concat |
| MINUS      | `-`    | Subtraction / unary neg  |
| STAR       | `*`    | Multiplication           |
| STAR_STAR  | `**`   | Exponentiation           |
| SLASH      | `/`    | Division                 |
| INT_DIVIDE | `//`   | Integer division         |
| MODULUS    | `%`    | Modulo                   |
| AT         | `@`    | Matrix multiplication    |

### Assignment

| Token         | Lexeme | Description         |
| ------------- | ------ | ------------------- |
| ASSIGN        | `=`    | Assignment          |
| PLUS_EQUAL    | `+=`   | Add and assign      |
| MINUS_EQUAL   | `-=`   | Subtract and assign |
| STAR_EQUAL    | `*=`   | Multiply and assign |
| SLASH_EQUAL   | `/=`   | Divide and assign   |
| PERCENT_EQUAL | `%=`   | Modulo and assign   |

### Comparison

| Token         | Lexeme | Description           |
| ------------- | ------ | --------------------- |
| EQUALITY      | `==`   | Equal                 |
| BANG_EQUAL    | `!=`   | Not equal             |
| LESS          | `<`    | Less than             |
| LESS_EQUAL    | `<=`   | Less than or equal    |
| GREATER       | `>`    | Greater than          |
| GREATER_EQUAL | `>=`   | Greater than or equal |

### Special Operators

| Token | Lexeme | Description                        |
| ----- | ------ | ---------------------------------- |
| PIPE  | `\|>`  | Pipe operator (`value \|> fn`)     |
| BAR   | `\|`   | Pattern OR separator in match/case |

---

## 4. Punctuation & Delimiters

| Token         | Lexeme | Description                    |
| ------------- | ------ | ------------------------------ |
| LEFT_PAREN    | `(`    | Open parenthesis               |
| RIGHT_PAREN   | `)`    | Close parenthesis              |
| LEFT_BRACKET  | `[`    | Open bracket                   |
| RIGHT_BRACKET | `]`    | Close bracket                  |
| LEFT_BRACE    | `{`    | Open brace                     |
| RIGHT_BRACE   | `}`    | Close brace                    |
| COMMA         | `,`    | Argument / element separator   |
| COLON         | `:`    | Block opener, dict separator   |
| SEMICOLON     | `;`    | Statement separator (reserved) |
| DOT           | `.`    | Member access                  |

---

## 5. Structural Tokens

Pulse uses indentation-based block structure (Python-style).
The lexer emits these tokens automatically based on leading spaces.

| Token   | Description                                                     |
| ------- | --------------------------------------------------------------- |
| INDENT  | Start of an indented block — emitted when indentation increases |
| DEDENT  | End of an indented block — emitted when indentation decreases   |
| NEWLINE | End of a logical line                                           |
| EOF     | End of source file                                              |

### Indentation Rules

- Only spaces are allowed for indentation — tabs raise a `LexerError`
- Each indent level must be consistent within a block
- Blank lines and comment lines are ignored for indentation purposes

---

## 6. Removed / Reserved Tokens

| Token     | Status   | Notes                                             |
| --------- | -------- | ------------------------------------------------- |
| TRANSPOSE | Reserved | Kept in TokenType but not used in current grammar |
| SEMICOLON | Reserved | Tokenized but not used as a statement separator   |
| ERROR     | Removed  | Replaced by `PulseLexError` raised directly       |
