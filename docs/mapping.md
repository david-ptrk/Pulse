# Crafting Interpreters → Pulse Mapping

This document maps key chapters from **Crafting Interpreters** by Robert Nystrom to the planned implementation stages of **Pulse**, the AI-Native programming language. Each chapter represents a conceptual block that will guide Pulse’s design and interpreter development.

---

| Chapter                       | Topic               | What It Does in _Crafting Interpreters_                                           | How It Maps to **Pulse**                                                                                                                                       |
| ----------------------------- | ------------------- | --------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **A Tree-Walk Interpreter**   | Introduction        | Explains how a high-level language can be implemented as a tree-walk interpreter. | Foundation for Pulse’s interpreter model (Phase 1). Pulse will start as a tree-walk interpreter before adding performance optimizations for tensor operations. |
| **4. Scanning**               | Lexer / Scanner     | Breaks raw source into tokens like identifiers, numbers, strings, etc.            | Pulse’s lexer will tokenize identifiers, numbers, tensor literals, operators (`+`, `*`, `@`), and keywords (`tensor`, `fn`, `import`, etc.).                   |
| **5. Representing Code**      | AST structure       | Builds the internal representation (classes) for expressions and statements.      | Define AST node types for Pulse: expressions, tensor ops, assignments, control flow structures, etc.                                                           |
| **6. Parsing Expressions**    | Parser foundation   | Parses expressions into ASTs using recursive descent.                             | Pulse parser will handle tensor expressions (`A * B`), scalar math, and logical conditions.                                                                    |
| **7. Evaluating Expressions** | Interpreter core    | Walks the AST to evaluate expressions.                                            | Pulse interpreter will evaluate tensor and scalar expressions, delegating heavy ops to NumPy/PyTorch in early versions.                                        |
| **8. Statements and State**   | Variables and scope | Adds variable declarations, assignments, scope tracking.                          | Pulse will use symbol tables for tensor/variable management — possibly with keywords like `let` or implicit declarations.                                      |
| **9. Control Flow**           | Branching & loops   | Implements `if`, `else`, `while`, `for`.                                          | Pulse will support standard control flow; later might extend for parallel/tensor batch operations.                                                             |
| **10. Functions**             | Function objects    | Adds user-defined functions, parameters, and returns.                             | Pulse will support user-defined functions for tensor/matrix ops — possibly GPU-aware or parallel functions later.                                              |
| **11. Resolving and Binding** | Scope resolution    | Ensures variables and functions bind to the correct scope.                        | Pulse will need this for proper variable scoping, especially in nested AI functions.                                                                           |
| **12. Classes**               | Object system       | Adds classes and instances.                                                       | Pulse may skip full OOP at first, but later adapt for Tensor objects or lightweight model structures.                                                          |
| **13. Inheritance**           | Class hierarchy     | Enables subclassing.                                                              | Optional — could later be used for extending base tensor classes or AI model hierarchies.                                                                      |

---

### ✅ Summary

- Chapters **4–7** → Core interpreter (Lexer, Parser, AST, Evaluator)
- Chapters **8–10** → Runtime and control flow (Variables, Functions, Loops)
- Chapters **11–13** → Advanced features (Scope resolution, optional OOP)

---
