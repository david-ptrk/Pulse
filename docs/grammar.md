# Pulse Parser v1.0 Grammar

## Program

1. program → statement\* EOF

## Statements

2. statement -> block  
   | exprStmt  
   | ifStmt  
   | whileStmt  
   | forStmt  
   | breakStmt  
   | continueStmt  
   | returnStmt  
   | funcStmt  
   | classStmt  
   | tryStmt  
   | passStmt  
   | importStmt  
   | raiseStmt  
   | delStmt  
   | matchStmt  
   | unpackStmt

3. exprStmt -> expression NEWLINE

## Expressions

4. expression -> assignment
5. assignment -> pipeline ("=" assignment)? | pipeline augAssign assigment | ternary
6. augAssign -> "+=" | "-=" | "\*=" | "/=" | "%="
7. ternary -> pipeline "if" expression "else" assignment
8. pipeline -> logical ("|>" logical)\*
9. logical -> equality (("and" | "or") equality)\*
10. equality -> comparison (("==" | "!=" | "in" | "not in" | "is" | "is not") comparison)\*
11. comparison -> addition ((">" | ">=" | "<" | "<=") addition)\*
    -> (chained: addition op addition op addition)
12. addition -> multiplication (("+" | "-") multiplication)\*
13. multiplication -> power (("\*" | "/" | "//" | "%" | "@") power)\*
14. power -> unary ("\*\*" unary)\*
15. unary -> ("not" | "-") unary | call
16. call -> primary (postfix)\*
17. postfix -> "." IDENTIFIER | "(" arguments? keywordArguments? ")" | "[" indexOrSlice ("," indexOrSlice)* "]"
18. primary -> NUMBER | STRING | BOOL | NULL | FSTRING | TENSOR_LITERAL | IDENTIFIER | "(" expression ")" | "[" listLiteral | listComp "]" | "{" dictLiteral "}" | "lambda" params? ":" expression

## Arguments & Parameters

19. arguments -> expression ("," expression)\*
20. keywordArguments -> IDENTIFIER "=" expression ("," IDENTIFIER "=" expression)\*
21. params = param ("," param)\* ("," "\*" IDENTIFER)?
22. param = IDENTIFIER ("=" expression)?

## List & Dict Literals

23. listLiteral -> expression ("," expression)\*
24. listComp -> expression "for" IDENTIFER "in" expression ("if" expression)?
25. dictLiteral -> (expression ":" expression) ("," expression ":" expression)\*

## Index & Slice

26. indexOrSlice -> expression | expression? ":" expression?

## Unpack

27. unpackStmt -> IDENTIFIER ("," IDENTIFIER)+ "=" expression NEWLINE

## Control Flow

28. ifStmt -> "if" expression ":" block ("elif" expression ":" block)\* ("else" ":" block)?
29. whileStmt -> "while" expression ":" block
30. forStmt -> "for" IDENTIFIER ("," IDENTIFIER)\* "in" expression ":" block
31. block -> NEWLINE INDENT statement\* DEDENT
32. breakStmt -> "break" NEWLINE
33. continueStmt -> "continue" NEWLINE
34. passStmt -> "pass" NEWLINE
35. returnStmt -> "return" expression? NEWLINE

## Match / Case

36. matchStmt -> "match" expression ":" NEWLINE INDENT caseClause+ DEDENT
37. caseClause -> "case" pattern ("if" expression)? ":" block
38. pattern -> "\_" | IDENTIFIER | expression ("|" expression)+ | "[" pattern ("," pattern)\* "]" | "{" (expression ":" pattern)\* "}" | expression

## Functions and Classes

39. funcStmt -> "def" IDENTIFIER "(" params? ")" ":" block
40. classStmt -> "class" IDENTIFIER ("(" IDENTIFIER ("," IDENTIFER)\* ")") ":" NEWLINE INDENT classBody DEDENT
41. classBody -> (funcStmt | "static" funcStmt | assignment | "pass" | NEWLINE)\*

## Error Handling

42. tryStmt -> "try" ":" block ("except" expression? ("as" IDENTIFIER)? ":" block)\* ("else" ":" block)? ("finally" ":" block)?
43. raiseStmt -> "raise" expression? NEWLINE

## Import

44. importStmt -> "import" modulePath ("as" IDENTIFIER)? NEWLINE | "from" modulePath "import" importNames NEWLINE
45. modulePath -> IDENTIFIER ("." IDENTIFIER)\*
46. importNames -> IDENTIFIER ("as" IDENTIFIER)? ("," IDENTIFIER ("as" IDENTIFIER)?)\*

## Delete

47. delStmt -> "del" delTarget ("," delTarget)\* NEWLINE
48. delTarget -> IDENTIFIER | IDENTIFIER "[" expression "]" | IDENTIFIER "." IDENTIFIER

---
