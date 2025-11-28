# Pulse Language Specification v1

## 1. Keywords

```
def, return, if, elif, else, while, for, break, continue, pass, try, except, import, from, as, and, or, not, True, False, class, self, in, del, dot, transpose
```

## 2. Data Types

```
int, float, bool, string, list, tuple, set, dict, range, tensor, matrix
```

> Tensor and Matrix are AI-native types; the rest are standard.

## 3. Operators & Precedence

| Operator          | Description                   | Precedence |
| ----------------- | ----------------------------- | ---------- |
| `()`              | Grouping                      | 1          |
| `[]`              | Indexing / slicing            | 1          |
| `+` `-` (unary)   | Unary plus / minus            | 2          |
| `*` `/` `%`       | Multiplication, Division, Mod | 3          |
| `+` `-` (binary)  | Addition, Subtraction         | 4          |
| `dot`             | Dot product (tensor)          | 5          |
| `transpose`       | Transpose (matrix/tensor)     | 6          |
| `==` `!=`         | Equality / inequality         | 7          |
| `<` `>` `<=` `>=` | Comparison                    | 7          |
| `and` `or` `not`  | Logical operators             | 8          |

## 4. Core Grammar Rules (pseudo-BNF)

```
<program>       ::= { <statement> }

<statement>     ::= <assignment> | <if_stmt> | <while_stmt> | <for_stmt> | <func_def> | <expr_stmt>

<assignment>    ::= IDENTIFIER "=" <expression>

<if_stmt>       ::= "if" <expression> ":" <block> [ "elif" <expression> ":" <block> ]* [ "else" ":" <block> ]

<func_def>      ::= "def" IDENTIFIER "(" [IDENTIFIER {"," IDENTIFIER}* ] ")" ":" <block>

<expression>    ::= <term> { ("+" | "-") <term> }*

<term>          ::= <factor> { ("*" | "/" | "dot") <factor> }*

<factor>        ::= NUMBER | STRING | BOOL | IDENTIFIER | "tensor" "(" <expression_list> ")" | "matrix" "(" <expression_list> ")" | "(" <expression> ")"
```

## 5. Example Snippets

```pul
# Variable assignment
X = tensor([1, 2, 3])

# Function
def square(a):
    return a * a

# If/Else
if x[0] > 0:
    print("positive")
else:
    print("negative")

# For loop
for i in range(0, 5):
    print(i)

# While loop
while x[0] < 10:
    x = x + 1
```
