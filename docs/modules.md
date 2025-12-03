# Pulse Architecture — Module Responsibilities (Phase 2)

This document defines all modules that will be implemented in Phase 2 of Pulse v1. Each module has a clear responsibility and maps directly to the interpreter architecture.

## 1. `tokenizer/`

Files:  
`tokenizer.py`  
`tokens.py`

Responsibilities:

- Convert raw `.pul` source code into a stream of tokens.
- Handle identifiers, numbers, strings, operators, punctuation, whitespace, comments, and EOF.
- Provide consistent error reporting for illegal characters.
- Output: list of Token objects.

## 2. `parser/`

Files:  
`parser.py`  
`grammar.md` (optional reference)

Responsibilities:

- Read tokens and produce an Abstract Syntax Tree (AST).
- Implement recursive-descent parsing using the grammar from `spec_v1.md`.
- Detect and report syntax errors.
- AST types produced: expressions, statements, declarations.

## 3. `ast/`

Files:  
`ast.py`  
`visitor.py` (optional)

Responsibilities:

- Define AST node classes (BinaryExpr, UnaryExpr, CallExpr, Literal, VarDecl, IfStmt, WhileStmt, ForStmt, FuncDecl, ClassDecl, etc.).
- Define base Visitor interface if using the visitor pattern.
- Provide a clean, typed tree representation for the interpreter.

## 4. `interpreter/`

Files:  
`interpreter.py`  
`environment.py`  
`builtins.py`

Responsibilities:

- Walk the AST and execute program behavior.
- Implement evaluation rules for expressions and statements.
- Manage variable scopes and lexical environments.
- Execute built-in functions (print, tensor(), matrix(), length(), etc.).
- Handle runtime errors.

## 5. `backend/`

Files:  
`python_backend.py`

Responsibilities:

- Provide Python-side implementation for: tensors (NumPy arrays), matrix ops, dot product, reshape, broadcasting.
- Pulse interpreter calls these when AI/tensor features appear in code.

## 6. `repl/`

Files:  
`repl.py`

Responsibilities:

- Provide an interactive REPL for Pulse.
- Accept input, tokenize → parse → interpret line-by-line.
- Support multiline blocks (if, while, function, etc.).

## 7. `errors/`

Files:  
`lexer_error.py`  
`parser_error.py`  
`runtime_error.py`

Responsibilities:

- Centralized and consistent error formatting.
- Pretty printed errors with line number + snippet.
- Stop interpretation cleanly on fatal errors.

## 8. `tests/`

Files:  
`tokenizer.md`  
`parser.md`  
`interpreter.md`

Responsibilities:

- Manual and automated tests for each phase.
- Example .pul programs converted into expected outputs.

## 9. `pulse.py`

Responsibilities:

- Main entrypoint that:
  - accepts a .pul file
  - runs tokenizer → parser → interpreter pipeline
  - enforces ".pul only" rule

## Summary

This module plan ensures that:

- Each module has one job.
- No circular garbage.
- The interpreter stays clean, readable, and expandable for AI features later.
