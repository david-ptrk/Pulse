# Crafting Interpreters → Pulse Mapping

This document maps key chapters from **Crafting Interpreters** by Robert Nystrom to the planned implementation stages of **Pulse**, the AI-focused programming language. Each chapter represents a conceptual block that will guide Pulse’s design and interpreter development.

---

| Chapter                                      | Topic                | What It Does in _Crafting Interpreters_                                           | How It Maps to **Pulse**                                                                                                                                       |
| -------------------------------------------- | -------------------- | --------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **A Tree-Walk Interpreter**                  | Introduction         | Explains how a high-level language can be implemented as a tree-walk interpreter. | Foundation for Pulse’s interpreter model (Phase 1). Pulse will start as a tree-walk interpreter before adding performance optimizations for tensor operations. |
| **4. Scanning**                              | Lexer / Scanner      | Breaks raw source into tokens like identifiers, numbers, strings, etc.            | Pulse’s lexer will tokenize identifiers, numbers, tensor literals, operators (`+`, `*`, `@`), and keywords (`tensor`, `fn`, `import`, etc.).                   |
| _Design Note: Implicit Semicolons_           | Design consideration | Talks about how semicolons can be optional in syntax.                             | Decide whether Pulse syntax should be semicolon-free (Pythonic) or use semicolons for clarity.                                                                 |
| **5. Representing Code**                     | AST structure        | Builds the internal representation (classes) for expressions and statements.      | Define AST node types for Pulse: expressions, tensor ops, assignments, control flow structures, etc.                                                           |
| **6. Parsing Expressions**                   | Parser foundation    | Parses expressions into ASTs using recursive descent.                             | Pulse parser will handle tensor expressions (`A * B`), scalar math, and logical conditions.                                                                    |
| _Design Note: Logic Versus History_          | Parsing strategy     | Discusses why certain parsing rules evolved.                                      | Helps keep Pulse’s grammar modern and readable — avoid legacy syntax patterns.                                                                                 |
| **7. Evaluating Expressions**                | Interpreter core     | Walks the AST to evaluate expressions.                                            | Pulse interpreter will evaluate tensor and scalar expressions, delegating heavy ops to NumPy/PyTorch in early versions.                                        |
| _Design Note: Static and Dynamic Typing_     | Type systems         | Discusses benefits of static vs dynamic typing.                                   | Guides Pulse to be mostly dynamic (like Python) with optional type annotations for tensors.                                                                    |
| **8. Statements and State**                  | Variables and scope  | Adds variable declarations, assignments, scope tracking.                          | Pulse will use symbol tables for tensor/variable management — possibly with keywords like `let` or implicit declarations.                                      |
| _Design Note: Implicit Variable Declaration_ | Design sugar         | Talks about implicit variable creation.                                           | Decide if Pulse should allow automatic variable creation (like Python) or enforce declarations.                                                                |
| **9. Control Flow**                          | Branching & loops    | Implements `if`, `else`, `while`, `for`.                                          | Pulse will support standard control flow; later might extend for parallel/tensor batch operations.                                                             |
| _Design Note: Spoonfuls of Syntactic Sugar_  | Syntax shortcuts     | Discusses making code easier to read.                                             | Plan Pulse’s syntax sugar — e.g., decorators like `@gpu` or shorthand tensor ops (`A += B`).                                                                   |
| **10. Functions**                            | Function objects     | Adds user-defined functions, parameters, and returns.                             | Pulse will support user-defined functions for tensor/matrix ops — possibly GPU-aware or parallel functions later.                                              |
| **11. Resolving and Binding**                | Scope resolution     | Ensures variables and functions bind to the correct scope.                        | Pulse will need this for proper variable scoping, especially in nested AI functions.                                                                           |
| **12. Classes**                              | Object system        | Adds classes and instances.                                                       | Pulse may skip full OOP at first, but later adapt for Tensor objects or lightweight model structures.                                                          |
| _Design Note: Prototypes and Power_          | Class design         | Discusses prototypes vs classes.                                                  | Optional — might influence future Pulse design for defining model-like structures.                                                                             |
| **13. Inheritance**                          | Class hierarchy      | Enables subclassing.                                                              | Optional — could later be used for extending base tensor classes or AI model hierarchies.                                                                      |

---

### ✅ Summary

- Chapters **4–7** → Core interpreter (Lexer, Parser, AST, Evaluator)
- Chapters **8–10** → Runtime and control flow (Variables, Functions, Loops)
- Chapters **11–13** → Advanced features (Scope resolution, optional OOP)

---

**Next Step:**  
Proceed to **Step 2 — Language Concept Draft**, where the design identity, syntax style, and purpose of Pulse will be clearly defined.
