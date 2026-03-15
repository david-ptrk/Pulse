# Pulse Parser v1.0 Grammar

## Program

1. program → statement\* EOF

## Statements

2. statement -> block  
   | exprStmt  
   | ifStmt  
   | whileStmt  
   | breakStmt  
   | continueStmt  
   | returnStmt  
   | forStmt  
   | funcStmt  
   | classStmt  
   | tryStmt  
   | passStmt

3. exprStmt -> expression

## Expressions

4. expression -> assignment
5. assignment -> callOrMember "=" assignment | logical
6. logical -> equality ( ("and" | "or") equality )\*
7. equality -> comparison ( ("==" | "!=") comparison )\*
8. comparison -> term ( (">" | "<") term )\*
9. term -> factor ( ("+" | "-") factor )\*
10. factor -> unary ( ("\*" | "/") unary )
11. unary -> ("!" | "-") unary | primary

## Primary Expressions & Postfix

12. primary -> callOrMember
13. callOrMember -> base (postfix)\*
14. base -> NUMBER | IDENTIFIER | "(" expression ")"
15. postfix -> "." IDENTIFIER | "(" arguments? ")"
16. arguments -> expression ("," expression)\*
17. parameters -> IDENTIFIER ("," IDENTIFIER)\*

## Control Flow

18. ifStmt -> "if" expression ":" statement ("elif" expression ":" statement)\* ("else" ":" statement)?
19. whileStmt -> "while" expression ":" statement
20. block -> INDENT statement\* DEDENT
21. breakStmt -> "break"
22. continueStmt -> "continue"
23. passStmt -> "pass"
24. returnStmt -> "return" expression?
25. forStmt -> "for" IDENTIFIER "in" expression ":" statement

## Functions and Classes

26. funcStmt -> "def" IDENTIFIER "(" parameters? ")" ":" statement
27. classStmt -> "class" IDENTIFIER ":" INDENT classBody DEDENT
28. classBody -> (funcStmt | assignment | NEWLINE)\*

## Error Handling

29. tryStmt -> "try" ":" statement ("except" IDENTIFIER? ":" statement)+ ("finally" ":" statement)?

---

## Notes / v1.0 Limitations

- No array or dictionary literals yet.
- No list comprehensions or generators.
- No decorators or annotations.
- Only simple exception handling supported.
- Logical operators limited to `and` / `or` (no short-circuit optimizations yet).
