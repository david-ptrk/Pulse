"""
generate_ast.py

Provides the definitions and utilities required to construct the
Abstract Syntax Tree (AST) for the Pulse programming language.

An Abstract Syntax Tree represents the structural and hierarchical
syntax of a program after it has been parsed. Instead of working with
raw tokens, the parser organizes program elements into AST nodes that
capture the logical relationships between expressions, statements,
and program blocks.

This module defines the different AST node types used throughout the
Pulse language implementation, such as expressions, statements, and
control-flow constructs. These node definitions allow the parser to
build a structured representation of the program that can later be
processed by the interpreter or compiler.

The AST generated using these structures serves as the core internal
representation of Pulse programs and is later traversed during
interpretation or further compilation stages.
"""

from argparse import ArgumentParser
from pathlib import Path
from typing import Dict, Iterable, Tuple, TextIO

# CLI
arg_parser = ArgumentParser(usage='generate_ast.py <output directory>')
arg_parser.add_argument(
    'output',
    help='Directory where generated AST files willbe written'
)
args = arg_parser.parse_args()

# Types
ASTDict = Dict[str, Tuple[str, ...]]
INDENT = "    "

DEFAULT_IMPORTS: Tuple[str, ...] = (
    "from __future__ import annotations",
    "from abc import ABC, abstractmethod",
)

EXPRESSIONS_IMPORTS: Tuple[str, ...] = DEFAULT_IMPORTS + (
    "from typing import Any, List, Tuple",
    "from src.tokens import Token",
)

STATEMENTS_IMPORTS: Tuple[str, ...] = DEFAULT_IMPORTS + (
    "from typing import Any, Optional, List, Tuple",
    "from src.expressions import Expr",
    "from src.tokens import Token"
)

# Expressions
EXPRESSIONS: ASTDict = {
    "Assign": ("name: Token", "value: Expr",),
    "Binary": ("left: Expr", "operator: Token", "right: Expr",),
    "Unary": ("operator: Token", "right: Expr",),
    "Literal": ("value: Any",),
    "Variable": ("name: Token",),
    "Grouping": ("expression: Expr",),
    "Call": ("callee: Expr", "paren: Token", "arguments: List[Expr]", "keyword_arguments: List[Tuple[Token, Expr]]",),
    "MemberAccess": ("object: Expr", "name: Token",),
    "Logical": ("left: Expr", "operator: Token", "right: Expr",),
    "List": ("elements: List[Expr]",),
    "Dict": ("keys: List[Expr]", "values: List[Expr]",),
    "Index": ("object: Expr", "index: Expr",),
    "SetIndex": ("object: Expr", "index: Expr", "value: Expr",),
    "Slice": ("lower: Optional[Expr]", "upper: Optional[Expr]",),
    "MultiIndex": ("object: Expr", "indices: List[Expr]",),
    "SetMember": ("object: Expr", "name: Token", "value: Expr",),
    "FString": ("parts: List[Expr]",),
    "Tensor": ("value: Any",),
    "Pipe": ("left: Expr", "right: Expr",),
    "Unpack": ("names: List[Token]", "value: Expr",),
}

# Statements
STATEMENTS: ASTDict = {
    "Expression": ("expression: Expr",),
    "Block": ("statements: List[Stmt]",),
    "If": ("condition: Expr", "then_branch: Stmt", "elif_branches: List[Tuple[Expr, Stmt]]", "else_branch: Optional[Stmt]",),
    "While": ("condition: Expr", "body: Stmt",),
    "For": ("var: Token", "iterable: Expr", "body: Stmt",),
    "Break": ("keyword: Token",),
    "Continue": ("keyword: Token",),
    "Return": ("keyword: Token", "value: Optional[Expr]",),
    "Function": ("name: Token", "params: List[Token]", "body: Block", "is_method: bool", "is_static: bool",),
    "Class": ("name: Token", "bases: List[Token]", "methods: List[Function]", "class_vars: List[Tuple[Token, Expr]]",),
    "Try": ("try_block: Stmt", "except_blocks: List[Tuple[Optional[Expr], Optional[Token], Stmt]]", "finally_block: Optional[Stmt]", "else_block: Optional[Stmt]",),
    "Pass": (),
    "Import": ("keyword: Token", "module_path: List[Token]", "alias: Optional[Token]", "names: Optional[List[Tuple[Token, Optional[Token]]]]",),
}

# Generator Functions
def define_ast(path: Path, base_name: str, types: ASTDict, imports: Tuple[str, ...]) -> None:
    class_name = base_name
    visitor_name = f"{base_name}Visitor"
    
    with path.open("w", encoding="utf-8") as file:
        define_imports(file, imports)
        define_visitor(file, base_name, types.keys())
        
        file.write("\n\n")
        
        file.write(f"class {class_name}(ABC):\n")
        file.write(f"{INDENT}@abstractmethod\n")
        file.write(f"{INDENT}def accept(self, visitor: {visitor_name}) -> Any:\n")
        file.write(f"{INDENT*2}pass\n\n")
        
        for type_name, fields in types.items():
            define_type(file, class_name, type_name, fields)
            file.write("\n")

def define_imports(file: TextIO, lines: Tuple[str, ...]) -> None:
    file.write("\n".join(lines))
    file.write("\n\n")

def define_type(file: TextIO, base_name: str, class_name: str, fields: Tuple[str, ...]) -> None:
    file.write(f"class {class_name}({base_name}):\n")
    
    params = ", ".join(fields)
    file.write(f"{INDENT}def __init__(self, {params}) -> None:\n")
    
    if not fields:
        file.write(f"{INDENT*2}pass\n")
    else:
        for field in fields:
            attr = field.split(":")[0]
            file.write(f"{INDENT*2}self.{attr} = {attr}\n")
    
    file.write("\n")
    
    file.write(f"{INDENT}def accept(self, visitor: {base_name}Visitor) -> Any:\n")
    file.write(f"{INDENT*2}return visitor.visit_{class_name.lower()}_{base_name.lower()}(self)\n")

def define_visitor(file: TextIO, base_name: str, types: Iterable[str]) -> None:
    visitor_name = f"{base_name}Visitor"
    lower = base_name.lower()

    file.write(f"class {visitor_name}(ABC):\n")

    for typ in types:
        file.write(f"{INDENT}@abstractmethod\n")
        file.write(f"{INDENT}def visit_{typ.lower()}_{lower}(self, expr: '{typ}') -> Any:\n")
        file.write(f"{INDENT*2}pass\n\n")

def main() -> None:
    output_path = Path(args.output).resolve()
    
    if not output_path.is_dir():
        arg_parser.error("Output must be an existing directory")
    
    define_ast(output_path / "expressions.py", "Expr", EXPRESSIONS, EXPRESSIONS_IMPORTS)
    define_ast(output_path / "statements.py", "Stmt", STATEMENTS, STATEMENTS_IMPORTS)

if __name__ == "__main__":
    main()