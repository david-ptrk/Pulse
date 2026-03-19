# Phase 2 Journal — Pulse

## Step 1: Lexer / Tokenizer (05-13 Dec 2025)

- Created TokenType, Token, and Lexer.
- Decided to ingnore comments at all, and not generate any Token for it.
- Created a syntax for Tensor Literal:  
  `a = @[[1, 2], [3, 4]]`
- Updated `docs/spec_v1.md` and `docs/tokens.md` to reflect some changes.
- Also updated examples in `examples/` to reflect these changes.
- Tested Lexer so that if generates correct Tokens.
- Few changes made in TokenType as I think they were necessary.
- Test result file for lexer is created `tests/lexer_test.md`.
- Lexer's code documented for understanding easily.
- Created LexerError class for unified formatted errors.

## Step 2: Parser / AST Construction (04 Feb - 15 Mar 2026)

- Created Parser, including `generate_ast`, `ast_printer`.
- Decided to limit grammar rules to some core functionalities.
- All grammar rules used in v1.0 of Pulse's Parser are written in `docs/grammar.md`.
- Verified Parser output to ensure correct AST generation.
- Tests are documented in `tests/parser_test.md`.
- Pulse Parser v1.0 is now frozen; no structural changes will be made without prior documentation in this journal.

## Step 3: Error Reporting & Environment (16-19 Mar 2026)

- Implemented unified runtime error handling system.
- Added Environment class with lexical scoping support.
- Enabled variable definition, lookup, and assignment across nested scopes.
- Integrated environment structure to support future interpreter execution.

## Step 4: Interpreter (19 Mar)
