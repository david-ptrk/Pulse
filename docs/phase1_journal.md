# Phase 1 Journal — Pulse

## Step 0: Prep

- Repository created: 07-11-2025
- Folder structure initialized
- Connected to GitHub
- `README.md` file created

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

## Step 3: Design Syntax by Examples (11–14 Nov 2025)

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
