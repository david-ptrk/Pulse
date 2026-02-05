"""
generate_ast.py

Generates AST classes for Pulse using the Visitor pattern.
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
ASTDict = Dict[str, Tuple[str]]
INDENT = "    "

DEFAULT_IMPORTS: Tuple[str, ...] = (
    "from abc import ABC, abstractmethod",
)

EXPRESSIONS_IMPORTS: Tuple[str, ...] = DEFAULT_IMPORTS + (
    "from typing import Any, List",
    "from src.tokens import Token",
)

STATEMENTS_IMPORTS: Tuple[str, ...] = DEFAULT_IMPORTS + (
    "from typing import Any",
    "from src.expressions import Expr",
)

# Expressions
EXPRESSIONS: ASTDict = {
    "Assign":   ("name: Token", "value: Expr"),
    "Binary":   ("left: Expr", "operator: Token", "right: Expr"),
    "Call":     ("callee: Expr", "paren: Token", "arguments: List[Expr]"),
    "Get":      ("obj: Expr", "name: Token"),
    "Grouping": ("expression: Expr",),
    "Literal":  ("value: Any",),
    "Logical":  ("left: Expr", "operator: Token", "right: Expr"),
    "Set":      ("obj: Expr", "name: Token", "value: Expr"),
    "Unary":    ("operator: Token", "right: Expr"),
    "Variable": ("name: Token",),
    # Optional
    "This":     ("keyword: Token",),
    "Super":    ("keyword: Token", "method: Token"),
}

# Statements
STATEMENTS: ASTDict = {
    "Expression": ("expression: Expr",),
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