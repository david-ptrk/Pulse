# Phase 2 Journal — Pulse

## Step 1: Lexer / Tokenizer (05-13 Dec 2025)

- Created TokenType, Token, and Lexer
- Decided to ingnore comments at all, and not generate any Token for it
- Created a syntax for Tensor Literal:  
  `a = @[[1, 2], [3, 4]]`
- Updated `docs/spec_v1.md` and `docs/tokens.md` to reflect some changes
- Also updated examples in `examples/` to reflect these changes
- Tested Lexer so that if generates correct Tokens
- Few changes made in TokenType as I think they were necessary
- Test result file for lexer is created `tests/lexer_test.md`
- Lexer's code documented for understanding easily
- Created LexerError class for unified formatted errors

## Step 2: Parser / AST Construction (04-?? Feb 2026)

-
