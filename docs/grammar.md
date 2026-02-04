# Pulse Language Grammar (Parser)

## Program

program → statement\* EOF

## Statements

statement → if_stmt
| while_stmt
| for_stmt
| func_def
| class_def
| return_stmt
| break_stmt
| continue_stmt
| pass_stmt
| expr_stmt

block → NEWLINE INDENT statement+ DEDENT

## Expressions

expression → assignment  
assignment → IDENTIFIER "=" assignment | logic*or  
logic_or → logic_and ("or" logic_and)*  
logic*and → equality ("and" equality)*  
equality → comparison (("==" | "!=") comparison)_  
comparison → term ((">" | "<" | ">=" | "<=") term)_  
term → factor (("+" | "-" ) factor)_  
factor → unary (("_" | "/" | "%") unary)\*  
unary → ("!" | "-") unary | primary

primary → NUMBER
| STRING
| BOOL
| IDENTIFIER
| "(" expression ")"
| TENSOR_LITERAL
