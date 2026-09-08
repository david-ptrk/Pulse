import pytest
from src.lexer import Lexer
from src.parser import Parser
from src.tokens import TokenType
from src.error import PulseSyntaxError
from src import expressions as expr
from src import statements as stmt

def parse(source: str):
    tokens = Lexer(source).scan_tokens()
    return Parser(tokens, source).parse()

def parse_expr(source: str) -> expr.Expr:
    statements = parse(source)
    assert len(statements) == 1
    node = statements[0]
    assert isinstance(node, stmt.Expression)
    return node.expression

def parse_one(source: str) -> stmt.Stmt:
    statements = parse(source)
    assert len(statements) == 1
    return statements[0]

# Literals & Primary Expressions
class TestLiterals:
    def test_number_literal(self):
        node = parse_expr("42\n")
        assert isinstance(node, expr.Literal)
        assert node.value == 42
    
    def test_string_literal(self):
        node = parse_expr('"hello"\n')
        assert isinstance(node, expr.Literal)
        assert node.value == "hello"
    
    def test_bool_literal(self):
        node = parse_expr("True\n")
        assert isinstance(node, expr.Literal)
        assert node.value is True
    
    def test_null_literal(self):
        node = parse_expr("null\n")
        assert isinstance(node, expr.Literal)
        assert node.value is None
    
    def test_variable(self):
        node = parse_expr("age\n")
        assert isinstance(node, expr.Variable)
        assert node.name.lexeme == "age"
    
    def test_grouping_returns_inner_expressions(self):
        node = parse_expr("(1 + 2)\n")
        assert isinstance(node, expr.Binary)
    
    def test_list_literal(self):
        node = parse_expr("[1, 2, 3]\n")
        assert isinstance(node, expr.List)
        assert len(node.elements) == 3
        assert all(isinstance(e, expr.Literal) for e in node.elements)
    
    def test_empty_list_literal(self):
        node = parse_expr("[]\n")
        assert isinstance(node, expr.List)
        assert node.elements == []
    
    def test_dict_literal(self):
        node = parse_expr('{"a": 1, "b": 2}\n')
        assert isinstance(node, expr.Dict)
        assert len(node.keys) == 2
        assert len(node.values) == 2
    
    def test_empty_dict_literal(self):
        node = parse_expr("{}\n")
        assert isinstance(node, expr.Dict)
        assert node.keys == []
        assert node.values == []
    
    def test_tensor_literal(self):
        node = parse_expr("@[[1, 2], [3, 4]]\n")
        assert isinstance(node, expr.Tensor)
        assert node.value == [[1, 2], [3, 4]]
    
    def test_list_comprehension(self):
        node = parse_expr("[x for x in items]\n")
        assert isinstance(node, expr.ListComp)
        assert node.var.lexeme == "x"
        assert isinstance(node.iterable, expr.Variable)
        assert node.condition is None
    
    def test_list_comprehension_with_condition(self):
        node = parse_expr("[x for x in items if x > 0]\n")
        assert isinstance(node, expr.ListComp)
        assert isinstance(node.condition, expr.Binary)

# Operator Precedence & Associativity
class TestExpressions:
    def test_addition(self):
        node = parse_expr("1 + 2\n")
        assert isinstance(node, expr.Binary)
        assert node.operator.type == TokenType.PLUS
        assert node.left.value == 1
        assert node.right.value == 2
    
    def test_multiplication_binds_tighter_than_addition(self):
        node = parse_expr("1 + 2 * 3\n")
        assert isinstance(node, expr.Binary)
        assert node.operator.type == TokenType.PLUS
        assert isinstance(node.right, expr.Binary)
        assert node.right.operator.type == TokenType.STAR
    
    def test_power_is_right_associative(self):
        node = parse_expr("2 ** 3 ** 2\n")
        assert isinstance(node, expr.Binary)
        assert node.operator.type == TokenType.STAR_STAR
        assert node.left.value == 2
        assert isinstance(node.right, expr.Binary)
        assert node.right.operator.type == TokenType.STAR_STAR
    
    def test_unary_minus(self):
        node = parse_expr("-5\n")
        assert isinstance(node, expr.Unary)
        assert node.operator.type == TokenType.MINUS
    
    def test_logical_not(self):
        node = parse_expr("not True\n")
        assert isinstance(node, expr.Unary)
        assert node.operator.type == TokenType.NOT
    
    def test_logical_and_or(self):
        node = parse_expr("a and b or c\n")
        assert isinstance(node, expr.Logical)
        assert node.operator.type == TokenType.OR
        assert isinstance(node.left, expr.Logical)
        assert node.left.operator.type == TokenType.AND
    
    def test_chained_comparison(self):
        node = parse_expr("0 < x < 10\n")
        assert isinstance(node, expr.Logical)
        assert node.operator.type == TokenType.AND
        assert isinstance(node.left, expr.Binary)
        assert node.left.operator.type == TokenType.LESS
        assert isinstance(node.right, expr.Binary)
        assert node.right.operator.type == TokenType.LESS
    
    def test_in_operator(self):
        node = parse_expr("x in items\n")
        assert isinstance(node, expr.Binary)
        assert node.operator.type == TokenType.IN
    
    def test_not_in_operator(self):
        node = parse_expr("x not in items\n")
        assert isinstance(node, expr.Binary)
        assert node.operator.lexeme == "not in"
    
    def test_is_operator(self):
        node = parse_expr("x is null\n")
        assert isinstance(node, expr.Binary)
        assert node.operator.type == TokenType.IS
    
    def test_is_not_operator(self):
        node = parse_expr("x is not null\n")
        assert isinstance(node, expr.Binary)
        assert node.operator.lexeme == "is not"
    
    def test_ternary(self):
        node = parse_expr("1 if flag else 2\n")
        assert isinstance(node, expr.Ternary)
        assert node.then_expr.value == 1
        assert isinstance(node.condition, expr.Variable)
        assert node.else_expr.value == 2
    
    def test_pipe_operator(self):
        node = parse_expr("value |> transform\n")
        assert isinstance(node, expr.Pipe)
        assert isinstance(node.left, expr.Variable)
        assert isinstance(node.right, expr.Variable)
    
    def test_lambda(self):
        node = parse_expr("lambda x: x * 2\n")
        assert isinstance(node, expr.Lambda)
        assert [p.lexeme for p in node.params] == ["x"]
        assert isinstance(node.body, expr.Binary)
    
    def test_lambda_no_params(self):
        node = parse_expr("lambda: 1\n")
        assert isinstance(node, expr.Lambda)
        assert node.params == []
    
    def test_fstring(self):
        node = parse_expr('f"Hello, {name}!"\n')
        assert isinstance(node, expr.FString)
        assert isinstance(node.parts[0], expr.Literal)
        assert node.parts[0].value == "Hello, "
        assert isinstance(node.parts[1], expr.Variable)
        assert node.parts[1].name.lexeme == "name"
        assert isinstance(node.parts[2], expr.Literal)
        assert node.parts[2].value == "!"

# Assignment
class TestAssignment:
    def test_simple_assignment(self):
        node = parse_expr("x = 5\n")
        assert isinstance(node, expr.Assign)
        assert node.name.lexeme == "x"
        assert node.value.value == 5
    
    def test_member_assignment(self):
        node = parse_expr("obj.x = 5\n")
        assert isinstance(node, expr.SetMember)
        assert node.name.lexeme == "x"
        assert isinstance(node.object, expr.Variable)
    
    def test_index_assignment(self):
        node = parse_expr("arr[0] = 5\n")
        assert isinstance(node, expr.SetIndex)
        assert isinstance(node.index, expr.Literal)
    
    def test_augmented_assignment_plus(self):
        node = parse_expr("x += 1\n")
        assert isinstance(node, expr.Assign)
        assert isinstance(node.value, expr.Binary)
        assert node.value.operator.type == TokenType.PLUS
        assert node.value.left.name.lexeme == "x"
    
    def test_augmented_assignment_on_member(self):
        node = parse_expr("obj.count += 1\n")
        assert isinstance(node, expr.SetMember)
        assert isinstance(node.value, expr.Binary)
    
    def test_augmented_assignment_on_index(self):
        node = parse_expr("arr[0] -= 1\n")
        assert isinstance(node, expr.SetIndex)
        assert node.value.operator.type == TokenType.MINUS
    
    def test_invalid_assignment_target_raises(self):
        with pytest.raises(PulseSyntaxError):
            parse("1 = 2\n")
    
    def test_unpack_assignment(self):
        node = parse_expr("a, b = pair\n")
        assert isinstance(node, expr.Unpack)
        assert [n.lexeme for n in node.names] == ["a", "b"]
        assert isinstance(node.value, expr.Variable)

# Calls, Member Access, Indexing, and Slicing
class TestCallsAndAccess:
    def test_call_no_args(self):
        node = parse_expr("foo()\n")
        assert isinstance(node, expr.Call)
        assert node.arguments == []
        assert node.keyword_arguments == []
    
    def test_call_positional_args(self):
        node = parse_expr("foo(1, 2)\n")
        assert isinstance(node, expr.Call)
        assert len(node.arguments) == 2
    
    def test_call_keyword_args(self):
        node = parse_expr("foo(1, verbose=True)\n")
        assert isinstance(node, expr.Call)
        assert len(node.arguments) == 1
        assert len(node.keyword_arguments) == 1
        assert node.keyword_arguments[0][0].lexeme == "verbose"
    
    def test_positional_after_keyword_raises(self):
        with pytest.raises(PulseSyntaxError):
            parse("foo(a=1, 2)\n")
    
    def test_member_access(self):
        node = parse_expr("obj.name\n")
        assert isinstance(node, expr.MemberAccess)
        assert node.name.lexeme == "name"
    
    def test_chained_member_and_call(self):
        node = parse_expr("obj.method().value\n")
        assert isinstance(node, expr.MemberAccess)
        assert isinstance(node.object, expr.Call)
    
    def test_index(self):
        node = parse_expr("arr[0]\n")
        assert isinstance(node, expr.Index)
    
    def test_slice(self):
        node = parse_expr("arr[1:3]\n")
        assert isinstance(node, expr.MultiIndex)
        assert len(node.indices) == 1
        assert isinstance(node.indices[0], expr.Slice)
        slice_node = node.indices[0]
        assert slice_node.lower.value == 1
        assert slice_node.upper.value == 3
    
    def test_slice_open_ended(self):
        node = parse_expr("arr[1:]\n")
        assert isinstance(node, expr.MultiIndex)
        assert isinstance(node.indices[0], expr.Slice)
        slice_node = node.indices[0]
        assert slice_node.lower.value == 1
        assert slice_node.upper is None
    
    def test_multi_index(self):
        node = parse_expr("t[0, 1]\n")
        assert isinstance(node, expr.MultiIndex)
        assert len(node.indices) == 2

# Statements: if / while/ for
class TestControlFlow:
    def test_if_else(self):
        source = (
            "if x > 0:\n"
            "    print(x)\n"
            "else:\n"
            "    print(0)\n"
        )
        node = parse_one(source)
        assert isinstance(node, stmt.If)
        assert isinstance(node.condition, expr.Binary)
        assert node.elif_branches == []
        assert node.else_branch is not None
    
    def test_if_elif_else(self):
        source = (
            "if a:\n"
            "    pass\n"
            "elif b:\n"
            "    pass\n"
            "else:\n"
            "    pass\n"
        )
        node = parse_one(source)
        assert isinstance(node, stmt.If)
        assert len(node.elif_branches) == 1
        assert node.else_branch is not None
    
    def test_if_without_else(self):
        source = "if a:\n    pass\n"
        node = parse_one(source)
        assert isinstance(node, stmt.If)
        assert node.else_branch is None
    
    def test_while_loop(self):
        source = "while x > 0:\n    x -= 1\n"
        node = parse_one(source)
        assert isinstance(node, stmt.While)
        assert isinstance(node.body, stmt.Block)
    
    def test_for_loop_single_var(self):
        source = "for item in items:\n    print(item)\n"
        node = parse_one(source)
        assert isinstance(node, stmt.For)
        assert node.var.lexeme == "item"
        assert node.vars is None
    
    def test_for_loop_multi_var(self):
        source = "for i, val in enumerate(items):\n    print(i, val)\n"
        node = parse_one(source)
        assert isinstance(node, stmt.For)
        assert node.var.lexeme == "i"
        assert [t.lexeme for t in node.vars] == ["i", "val"]
    
    def test_break_and_continue(self):
        source = (
            "while True:\n"
            "    break\n"
        )
        node = parse_one(source)
        body = node.body
        assert isinstance(body.statements[0], stmt.Break)
    
    def test_missing_colon_raises(self):
        with pytest.raises(PulseSyntaxError):
            parse("if x\n    pass\n")
    
    def test_block_closes_at_eof(self):
        source = (
            "if True:\n"
            "    print('hello')\n"
        )
        parse(source)

# Functions
class TestFunctions:
    def test_simple_function(self):
        source = (
            "def add(a, b):\n"
            "    return a + b\n"
        )
        node = parse_one(source)
        assert isinstance(node, stmt.Function)
        assert node.name.lexeme == "add"
        assert [p.lexeme for p in node.params] == ["a", "b"]
        assert node.defaults == [None, None]
        assert node.vararg is None
        assert node.is_method is False
        assert node.is_static is False
    
    def test_function_with_default(self):
        source = (
            'def greet(name, msg="hi"):\n'
            "    return msg\n"
        )
        node = parse_one(source)
        assert isinstance(node, stmt.Function)
        assert node.defaults[0] is None
        assert isinstance(node.defaults[1], expr.Literal)
        assert node.defaults[1].value == "hi"
    
    def test_non_default_after_default_raises(self):
        source = (
            "def bad(a=1, b):\n"
            "    pass\n"
        )
        with pytest.raises(PulseSyntaxError):
            parse(source)
    
    def test_varargs(self):
        source = (
            "def sum_all(*args):\n"
            "    return args\n"
        )
        node = parse_one(source)
        assert node.vararg.lexeme == "args"
        assert node.params == []
    
    def test_return_with_no_value(self):
        source = (
            "def f():\n"
            "    return\n"
        )
        node = parse_one(source)
        return_stmt = node.body.statements[0]
        assert isinstance(return_stmt, stmt.Return)
        assert return_stmt.value is None
    
    def test_return_with_value(self):
        source = (
            "def f():\n"
            "    return 1\n"
        )
        node = parse_one(source)
        return_stmt = node.body.statements[0]
        assert isinstance(return_stmt.value, expr.Literal)

# Classes
class TestClasses:
    def test_simple_class(self):
        source = (
            "class Animal:\n"
            "    def speak(self):\n"
            "        pass\n"
        )
        node = parse_one(source)
        assert isinstance(node, stmt.Class)
        assert node.name.lexeme == "Animal"
        assert node.bases == []
        assert len(node.methods) == 1
        assert node.methods[0].is_method is True
    
    def test_class_with_base(self):
        source = (
            "class Dog(Animal):\n"
            "    def speak(self):\n"
            "        pass\n"
        )
        node = parse_one(source)
        assert [b.lexeme for b in node.bases] == ["Animal"]
    
    def test_class_variable(self):
        source = (
            "class Animal:\n"
            '    name = "unknown"\n'
            "    def speak(self):\n"
            "        pass\n"
        )
        node = parse_one(source)
        assert len(node.class_vars) == 1
        var_name, value = node.class_vars[0]
        assert var_name.lexeme == "name"
        assert isinstance(value, expr.Literal)
    
    def test_static_method(self):
        source = (
            "class Util:\n"
            "    static def helper():\n"
            "        pass\n"
        )
        node = parse_one(source)
        assert node.methods[0].is_static is True
    
    def test_static_without_def_raises(self):
        source = (
            "class Util:\n"
            "    static x = 1\n"
        )
        with pytest.raises(PulseSyntaxError):
            parse(source)

# Try / Except / Finally / Raise
class TestExceptions:
    def test_try_except(self):
        source = (
            "try:\n"
            "    risky()\n"
            "except ValueError as e:\n"
            "    print(e)\n"
        )
        node = parse_one(source)
        assert isinstance(node, stmt.Try)
        assert len(node.except_blocks) == 1
        exc_type, exc_name, _ = node.except_blocks[0]
        assert isinstance(exc_type, expr.Variable)
        assert exc_name.lexeme == "e"
    
    def test_bare_except(self):
        source = (
            "try:\n"
            "    risky()\n"
            "except:\n"
            "    handle()\n"
        )
        node = parse_one(source)
        exc_type, exc_name, _ = node.except_blocks[0]
        assert exc_type is None
        assert exc_name is None
    
    def test_try_finally_without_except(self):
        source = (
            "try:\n"
            "    risky()\n"
            "finally:\n"
            "    cleanup()\n"
        )
        node = parse_one(source)
        assert node.except_blocks == []
        assert node.finally_block is not None
    
    def test_try_without_except_or_finally_raises(self):
        source = "try:\n    risky()\n"
        with pytest.raises(PulseSyntaxError):
            parse(source)
    
    def test_try_else(self):
        source = (
            "try:\n"
            "    risky()\n"
            "except:\n"
            "    pass\n"
            "else:\n"
            "    success()\n"
        )
        node = parse_one(source)
        assert node.else_block is not None
    
    def test_raise_with_exception(self):
        node = parse_one('raise ValueError("bad")\n')
        assert isinstance(node, stmt.Raise)
        assert isinstance(node.exception, expr.Call)
    
    def test_bare_raise(self):
        node = parse_one("raise\n")
        assert isinstance(node, stmt.Raise)
        assert node.exception is None

# Import / from-import / del
class TestImportsAndDel:
    def test_simple_import(self):
        node = parse_one("import math\n")
        assert isinstance(node, stmt.Import)
        assert [t.lexeme for t in node.module_path] == ["math"]
        assert node.alias is None
        assert node.names is None
    
    def test_import_with_alias(self):
        node = parse_one("import math as m\n")
        assert node.alias.lexeme == "m"
    
    def test_dotted_import(self):
        node = parse_one("import a.b.c\n")
        assert [t.lexeme for t in node.module_path] == ["a", "b", "c"]
    
    def test_from_import(self):
        node = parse_one("from math import sqrt, pi\n")
        assert isinstance(node, stmt.Import)
        assert [t.lexeme for t in node.module_path] == ["math"]
        names = [n.lexeme for n, _ in node.names]
        assert names == ["sqrt", "pi"]
    
    def test_from_import_with_alias(self):
        node = parse_one("from math import sqrt as s\n")
        name, alias = node.names[0]
        assert name.lexeme == "sqrt"
        assert alias.lexeme == "s"
    
    def test_del_single_target(self):
        node = parse_one("del x\n")
        assert isinstance(node, stmt.Del)
        assert len(node.targets) == 1
    
    def test_del_multiple_targets(self):
        node = parse_one('del x, d["key"]\n')
        assert len(node.targets) == 2
        assert isinstance(node.targets[1], expr.Index)

# Match Statement
class TestMatch:
    def test_match_literal_cases(self):
        source = (
            "match status:\n"
            "    case 200:\n"
            "        print(\"OK\")\n"
            "    case _:\n"
            "        print(\"Unknown\")\n"
        )
        node = parse_one(source)
        assert isinstance(node, stmt.Match)
        assert isinstance(node.subject, expr.Variable)
        assert len(node.cases) == 2
    
    def test_match_or_pattern(self):
        source = (
            "match status:\n"
            "    case 404 | 405:\n"
            "        print(\"Not Found\")\n"
        )
        node = parse_one(source)
        pattern, guard, _ = node.cases[0]
        assert isinstance(pattern, tuple)
        assert pattern[0] == "or"
    
    def test_match_case_with_guard(self):
        source = (
            "match status:\n"
            "    case n if n >= 500:\n"
            "        print(\"Server Error\")\n"
        )
        node = parse_one(source)
        pattern, guard, _ = node.cases[0]
        assert guard is not None
    
    def test_match_sequence_pattern(self):
        source = (
            "match pair:\n"
            "    case [a, b]:\n"
            "        print(a)\n"
        )
        node = parse_one(source)
        pattern, _, _ = node.cases[0]
        assert isinstance(pattern, tuple)
        assert pattern[0] == "sequence"

# Long-control Keyword Misuse / General Error Handling
class TestErrorHandling:
    def test_unexpected_token_raises(self):
        with pytest.raises(PulseSyntaxError):
            parse("+ 1\n")
    
    def test_unclosed_paren_raises(self):
        with pytest.raises(PulseSyntaxError):
            parse("(1 + 2\n")
    
    def test_unclosed_bracket_raises(self):
        with pytest.raises(PulseSyntaxError):
            parse("[1, 2\n")
    
    def test_missing_function_name_raises(self):
        with pytest.raises(PulseSyntaxError):
            parse("def (a, b):\n    pass\n")
    
    def test_error_carries_line_number(self):
        source = "x = 1\ny = (\n"
        with pytest.raises(PulseSyntaxError) as excinfo:
            parse(source)
        print("ERROR LINE:", excinfo.value.line)
        print("ERROR:", excinfo.value)
        assert excinfo.value.line == 2

# Multiple Statements / Blocks
class TestProgramStructure:
    def test_multiple_top_level_statements(self):
        source = "x = 1\ny = 2\nprint(x + y)\n"
        statements = parse(source)
        assert len(statements) == 3
        assert isinstance(statements[0], stmt.Expression)
        assert isinstance(statements[1], stmt.Expression)
        assert isinstance(statements[2], stmt.Expression)
    
    def test_empty_source_yields_no_statements(self):
        assert parse("") == []
    
    def test_pass_statement(self):
        node = parse_one("pass\n")
        assert isinstance(node, stmt.Pass)
    
    def test_nested_blocks(self):
        source = (
            "if a:\n"
            "    if b:\n"
            "        c\n"
        )
        node = parse_one(source)
        inner = node.then_branch.statements[0]
        assert isinstance(inner, stmt.If)
