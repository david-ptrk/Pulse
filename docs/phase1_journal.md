# Phase 1 Journal — Pulse

## Step 0: Prep

- Repository created: 07-11-2025
- Folder structure initialized.
- Connected to GitHub.
- `README.md` file created.

## Step 1: Mapping (07 Nov 2025)

- Revisited _Crafting Interpreters_ chapters.
- Created `docs/mapping.md` linking each chapter to corresponding Pulse implementation components.
- Defined which features from Lox will be reused or extended (Lexer, Parser, AST, Interpreter).
- Decided Pulse will start as a tree-walk interpreter with tensor support added later.

## Step 2: Problem Statement & Scope (28 Nov 2025)

- Wrote the formal problem statement explaining why Pulse is needed and who benefits.
- Defined project scope for v1: Lexer, Parser, AST, Interpreter, REPL, and NumPy-backed tensor operations.
- Listed out-of-scope features for v1: JIT, GPU execution, advanced type system, full OOP, modules.
- Created `docs/problem-and-scope.md` as the official deliverable.

## Step 3: Design Syntax by Examples (28 Nov 2025)

- Created **28 example programs** in `examples/` folder demonstrating Pulse core syntax, AI constructs, and control structures.
- Examples cover:
  - Variable assignment, arithmetic, print
  - Functions, recursion
  - Conditionals: if, elif, else
  - Loops: for, while, break, continue, pass
  - Tensor and matrix creation, indexing, slicing, dot product, reshape
  - Classes, inheritance, model training and evaluation
  - Console I/O, file I/O, exception handling
- Each example written in **Pythonic Pulse pseudo-code** for readability, serving as a reference for interpreter implementation.
- Compiled `docs/examples.md` listing all examples with one-line descriptions and usage instructions.
- Decisions made:
  - Extension `.pul` chosen for Pulse files.
  - Python-like syntax kept for now; will evolve as more AI-specific constructs are added.
  - Each file is self-contained and demonstrates one or more language features.

## Step 4: Draft Language Specification (28 Nov 2025)

- Created `docs/spec_v1.md` as the initial **Pulse language specification** for v1.
- Included keywords.
- Defined data types.
- Compiled operators & precedence table.
- **Drafted core grammar rules** (pseudo-BNF).
- Purpose: Provide a clear reference for parser and interpreter implementation in **Pulse v1**.
- Decisions made:
  - Syntax remains **Pythonic** for readability.
  - AI-specific functions (tensor(), matrix()) included as **first-class** constructs.
  - Pseudo-BNF rules sufficient to start implementing parser without full language coverage.

## Step 5: Define Token & AST Shapes (29 Nov 2025)

- Created `docs/tokens.md` defining all Pulse token types for the lexer. Categories include: identifiers, literals, keywords, operators, punctuation, structural tokens, and special tokens.
- Created `docs/ast.md` outlining AST node shapes for the parser. Node classes include: BinaryExpr, UnaryExpr, Literal, VarDecl, FuncDecl, CallExpr, TensorLiteral, MatrixLiteral, IfStmt, WhileStmt, ForStmt, ClassDecl, AttributeAccess, Assignment.
- Decisions made:
  - Tokens and AST nodes designed to cover Pythonic syntax with AI-specific extensions (tensor, matrix, dot, transpose).
  - Focused on minimal, explicit rules to get the lexer and parser started.

## Step 6: Implement Tokenizer & Write Tokenizer Tests (30 Nov 2025)

- Implemented complete `tokenizer.py` under `src/`.
- Ran internal tests using example file `examples/example1_tokenizer.pul`.
- Verified that the tokenizer correctly outputs lexemes, literals, and line numbers.
- Documentation Added. Created `tests/tokenizer.md` documenting 8 formal test cases.
- Tokenizer is minimal but **stable** enough to support Phase 2 (Parser).
