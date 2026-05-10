# Pulse Language - AST Node Types

This document defines the Abstract Syntax Tree (AST) node classes for Pulse.
Each node represents a syntactic construct in the language, used by the parser,
resolver, and interpreter.

---

## 1. Expression Nodes

| Node         | Description                                                                                                                   | Fields                                                                                                 |
| ------------ | ----------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| Literal      | Literal value — number, string, bool, null                                                                                    | `value: Any`                                                                                           |
| Variable     | Variable reference                                                                                                            | `name: Token`                                                                                          |
| Assign       | Variable assignment or augmented assignment                                                                                   | `name: Token`, `value: Expr`                                                                           |
| Binary       | Binary operation (`+`, `-`, `*`, `/`, `//`, `%`, `**`, `@`, `==`, `!=`, `<`, `>`, `<=`, `>=`, `in`, `not in`, `is`, `is not`) | `left: Expr`, `operator: Token`, `right: Expr`                                                         |
| Unary        | Unary operation (`-`, `not`)                                                                                                  | `operator: Token`, `right: Expr`                                                                       |
| Logical      | Short-circuit logical (`and`, `or`)                                                                                           | `left: Expr`, `operator: Token`, `right: Expr`                                                         |
| Grouping     | Parenthesised expression                                                                                                      | `expression: Expr`                                                                                     |
| Ternary      | Ternary expression (`x if cond else y`)                                                                                       | `then_expr: Expr`, `condition: Expr`, `else_expr: Expr`                                                |
| Call         | Function or method call                                                                                                       | `callee: Expr`, `paren: Token`, `arguments: List[Expr]`, `keyword_arguments: List[Tuple[Token, Expr]]` |
| MemberAccess | Attribute access (`obj.name`)                                                                                                 | `object: Expr`, `name: Token`                                                                          |
| SetMember    | Attribute assignment (`obj.name = value`)                                                                                     | `object: Expr`, `name: Token`, `value: Expr`                                                           |
| Index        | Single index access (`obj[i]`)                                                                                                | `object: Expr`, `index: Expr`                                                                          |
| SetIndex     | Index assignment (`obj[i] = value`)                                                                                           | `object: Expr`, `index: Expr`, `value: Expr`                                                           |
| Slice        | Slice expression (`start:stop`)                                                                                               | `lower: Optional[Expr]`, `upper: Optional[Expr]`                                                       |
| MultiIndex   | Multi-dimensional index (`tensor[0, 1]`)                                                                                      | `object: Expr`, `indices: List[Expr]`                                                                  |
| List         | List literal (`[1, 2, 3]`)                                                                                                    | `elements: List[Expr]`                                                                                 |
| Dict         | Dict literal (`{"key": value}`)                                                                                               | `keys: List[Expr]`, `values: List[Expr]`                                                               |
| Tensor       | Tensor literal (`@[[1, 2], [3, 4]]`)                                                                                          | `value: Any`                                                                                           |
| FString      | F-string literal (`f"hello {name}"`)                                                                                          | `parts: List[Expr]`                                                                                    |
| Lambda       | Anonymous function (`lambda x: x * 2`)                                                                                        | `params: List[Token]`, `body: Expr`                                                                    |
| ListComp     | List comprehension (`[x*2 for x in nums if x > 0]`)                                                                           | `element: Expr`, `var: Token`, `iterable: Expr`, `condition: Optional[Expr]`                           |
| Pipe         | Pipe operator (`value \|> fn`)                                                                                                | `left: Expr`, `right: Expr`                                                                            |
| Unpack       | Multi-variable unpack (`a, b = [1, 2]`)                                                                                       | `names: List[Token]`, `value: Expr`                                                                    |

---

## 2. Statement Nodes

| Node       | Description                                   | Fields                                                                                                                                                 |
| ---------- | --------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Expression | Expression used as a statement                | `expression: Expr`                                                                                                                                     |
| Block      | Indented block of statements                  | `statements: List[Stmt]`                                                                                                                               |
| If         | Conditional (`if`/`elif`/`else`)              | `condition: Expr`, `then_branch: Stmt`, `elif_branches: List[Tuple[Expr, Stmt]]`, `else_branch: Optional[Stmt]`                                        |
| While      | While loop                                    | `condition: Expr`, `body: Stmt`                                                                                                                        |
| For        | For loop with optional tuple unpacking        | `var: Token`, `iterable: Expr`, `body: Stmt`, `vars: Optional[List[Token]]`                                                                            |
| Break      | Break out of a loop                           | `keyword: Token`                                                                                                                                       |
| Continue   | Continue to next loop iteration               | `keyword: Token`                                                                                                                                       |
| Pass       | No-op statement                               | —                                                                                                                                                      |
| Return     | Return from a function                        | `keyword: Token`, `value: Optional[Expr]`                                                                                                              |
| Function   | Function declaration                          | `name: Token`, `params: List[Token]`, `defaults: List[Optional[Expr]]`, `vararg: Optional[Token]`, `body: Block`, `is_method: bool`, `is_static: bool` |
| Class      | Class declaration with optional inheritance   | `name: Token`, `bases: List[Token]`, `methods: List[Function]`, `class_vars: List[Tuple[Token, Expr]]`                                                 |
| Try        | Exception handling                            | `try_block: Stmt`, `except_blocks: List[Tuple[Optional[Expr], Optional[Token], Stmt]]`, `finally_block: Optional[Stmt]`, `else_block: Optional[Stmt]`  |
| Raise      | Raise an exception                            | `keyword: Token`, `exception: Optional[Expr]`                                                                                                          |
| Del        | Delete a variable, index, or member           | `keyword: Token`, `targets: List[Expr]`                                                                                                                |
| Import     | Module import (`import x`, `from x import y`) | `keyword: Token`, `module_path: List[Token]`, `alias: Optional[Token]`, `names: Optional[List[Tuple[Token, Optional[Token]]]]`                         |
| Match      | Pattern matching (`match`/`case`)             | `keyword: Token`, `subject: Expr`, `cases: List[Tuple[Any, Optional[Expr], Stmt]]`                                                                     |

---

## 3. Pattern Types (used inside Match)

| Pattern  | Description                              | Structure                                 |
| -------- | ---------------------------------------- | ----------------------------------------- |
| Wildcard | Matches anything, no binding (`_`)       | `Token` with lexeme `"_"`                 |
| Capture  | Matches anything, binds to variable      | `Token` (IDENTIFIER)                      |
| Literal  | Matches an exact value                   | `Expr`                                    |
| OR       | Matches any of several values (`a \| b`) | `("or", List[pattern])`                   |
| Sequence | Matches a list structure (`[a, b]`)      | `("sequence", List[pattern])`             |
| Mapping  | Matches dict keys (`{"k": pattern}`)     | `("mapping", List[Tuple[Expr, pattern]])` |
| Guard    | Additional condition (`case x if x > 0`) | `Optional[Expr]` attached to any case     |

---

## 4. Notes

- Expression nodes produce values when evaluated; statement nodes control program flow.
- AST nodes are instantiated by the parser and traversed by the resolver and interpreter using the visitor pattern.
- The `Function` node is reused for both top-level functions and class methods — distinguished by `is_method` and `is_static` flags.
- The `Assign` node handles both plain assignment (`x = 1`) and augmented assignment (`x += 1`) — augmented forms are desugared into `Assign(x, Binary(x, op, value))` during parsing.
- The `For` node supports both single-variable (`for x in lst`) and tuple-unpacking (`for i, v in enumerate(lst)`) via the `vars` field.
- Tensor literals use Python's `ast` module internally to parse the literal value at parse time.
- Pattern matching cases are not separate AST nodes — they are stored as tuples `(pattern, guard, body)` inside the `Match` node.
