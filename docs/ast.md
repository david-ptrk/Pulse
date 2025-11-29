# Pulse Language — AST Node Types

This document defines the Abstract Syntax Tree (AST) node classes for Pulse. Each node represents a syntactic construct in the language. These nodes will be used by the parser and evaluator.

## 1. Expression Nodes

| Node Name     | Description                                   | Fields / Children                           |
| ------------- | --------------------------------------------- | ------------------------------------------- |
| BinaryExpr    | Binary operation (a + b, a \* b, a dot b)     | left (Expr), operator (Token), right (Expr) |
| UnaryExpr     | Unary operation (-a, not a)                   | operator (Token), operand (Expr)            |
| LiteralExpr   | Literal values (number, string, bool, tensor) | value                                       |
| VariableExpr  | Variable reference                            | name (Token)                                |
| AssignExpr    | Variable assignment                           | name (Token), value (Expr)                  |
| CallExpr      | Function or method call                       | callee (Expr), arguments (list of Expr)     |
| GetAttrExpr   | Access attribute (obj.attr)                   | object (Expr), name (Token)                 |
| SetAttrExpr   | Set attribute (obj.attr = val)                | object (Expr), name (Token), value (Expr)   |
| TensorLiteral | Tensor creation literal                       | values (list of Expr or nested lists)       |
| MatrixLiteral | Matrix creation literal                       | values (list of lists of Expr)              |

## 2. Statement Nodes

| Node Name     | Description                | Fields / Children                                                   |
| ------------- | -------------------------- | ------------------------------------------------------------------- |
| ExprStmt      | Expression as a statement  | expression (Expr)                                                   |
| PrintStmt     | Print statement            | expression (Expr)                                                   |
| VarDeclStmt   | Variable declaration       | name (Token), initializer (Expr)                                    |
| BlockStmt     | Block of statements        | statements (list of Stmt)                                           |
| IfStmt        | Conditional if/elif/else   | condition (Expr), then_branch (Stmt), else_branch (Stmt)            |
| WhileStmt     | While loop                 | condition (Expr), body (Stmt)                                       |
| ForStmt       | For loop                   | initializer (Stmt), condition (Expr), increment (Expr), body (Stmt) |
| FuncDeclStmt  | Function declaration       | name (Token), params (list of Token), body (BlockStmt)              |
| ReturnStmt    | Return statement           | value (Expr)                                                        |
| ClassDeclStmt | Class declaration          | name (Token), methods (list of FuncDeclStmt)                        |
| TryStmt       | Exception handling         | try_block (BlockStmt), except_block (BlockStmt)                     |
| BreakStmt     | Break statement in loop    | –                                                                   |
| ContinueStmt  | Continue statement in loop | –                                                                   |
| PassStmt      | Pass (no-op)               | –                                                                   |

## 3. Notes

- Expressions are usually evaluated to produce values; statements control program flow.
- AST nodes will be instantiated by the parser during parsing and later used by the interpreter.
- Tensor and matrix literals are treated as specialized literal expressions for AI-specific operations.
- This AST structure is minimal but sufficient for starting the interpreter.
