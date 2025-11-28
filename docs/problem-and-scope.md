# Pulse — Problem Statement & Scope

_Date: 28-11-2025_

---

## Problem Statement

**AI and ML** development today depends on heavy, **general-purpose languages** (Python, R, MATLAB, etc.) stuffed with external libraries, complex environment setups, and tons of boilerplate code. These languages are **not AI-native** and they treat tensors, matrices, and ML operations as add-ons instead of first-class citizens.

This makes AI development **slow, complex, and unfriendly** for beginners. Debugging becomes harder, prototypes take longer, and rapid experimentation suffers. There is no lightweight, beginner-friendly AI-native programming language designed purely for ML workflows.

## Problem Solution

**Pulse** is designed to solve this gap by introducing a **minimal AI-first programming language**, built to express tensor computations, matrix algebra, and AI workflows with direct, readable syntax. It aims to provide the clarity of Python with the precision of a dedicated DSL — offering a clean interpreter built in Python that executes tensor operations via NumPy (and later, GPU frameworks). Pulse cuts away boilerplate, reduces dependency chaos, and makes AI development smoother, faster, and more accessible.

Pulse primarily benefits:

- **AI/ML students** learning how interpreters and tensor operations connect
- **Researchers** prototyping simple models or tensor math quickly
- **Educators** demonstrating the core ideas behind AI languages without heavy frameworks

---

## Project Scope

### **In Scope (v1)**

- Tokenizer / Lexer
- Parser and Abstract Syntax Tree (AST)
- Tree-walk Interpreter in Python
- Tensor data type mapped to NumPy
- Basic mathematical and tensor operations (`+`, `-`, `*`, `@`, `reshape`, etc.)
- REPL (interactive shell) for quick experimentation
- Basic error handling and diagnostics
- Simple standard library (print, shape, zeros, ones, etc.)

### **Out of Scope (v1)**

- JIT compilation or bytecode optimization
- GPU driver-level execution (CUDA, ROCm)
- Advanced type inference
- Package management
- Multi-threading or async execution
- Deep learning model abstraction (planned for v2)

---

## Summary

Pulse v1 focuses on **clarity, learning, and foundation** — proving that an AI-first language can be elegant, minimal, and practical. Later phases will explore **performance (JIT)**, **types**, and **GPU extensions**, but the current goal is to establish a **working interpreter prototype** that supports clean tensor computation semantics.
