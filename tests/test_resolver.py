import pytest
from unittest.mock import MagicMock, call, patch
from src.resolver import Resolver, FunctionType, ClassType
from src.error import PulseSemanticError

def make_token(lexeme, line=1, column=0):
    tok = MagicMock()
    tok.lexeme = lexeme
    tok.line = line
    tok.column = column
    return tok

def make_interpreter():
    interp = MagicMock()
    interp.resolve = MagicMock()
    return interp

def make_resolver(interpreter=None):
    if interpreter is None:
        interpreter = make_interpreter()
    return Resolver(interpreter)

def literal_expr(value=42):
    node = MagicMock()
    node.accept = lambda visitor: visitor.visit_literal_expr(node)
    node.value = value
    return node

def variable_expr(name_lexeme, line=1):
    node = MagicMock()
    tok = make_token(name_lexeme, line=line)
    node.name = tok
    node.accept = lambda visitor: visitor.visit_variable_expr(node)
    return node

def assign_expr(name_lexeme, value_node=None):
    node = MagicMock()
    node.name = make_token(name_lexeme)
    node.value = value_node or literal_expr()
    node.accept = lambda visitor: visitor.visit_assign_expr(node)
    return node

def grouping_expr(inner=None):
    node = MagicMock()
    node.expression = inner or literal_expr()
    node.accept = lambda visitor: visitor.visit_grouping_expr(node)
    return node

def unary_expr(right=None):
    node = MagicMock()
    node.right = right or literal_expr()
    node.accept = lambda visitor: visitor.visit_unary_expr(node)
    return node

def binary_expr(left=None, right=None):
    node = MagicMock()
    node.left = left or literal_expr()
    node.right = right or literal_expr()
    node.accept = lambda visitor: visitor.visit_binary_expr(node)
    return node

def logical_expr(left=None, right=None):
    node = MagicMock()
    node.left = left or literal_expr()
    node.right = right or literal_expr()
    node.accept = lambda visitor: visitor.visit_logical_expr(node)
    return node

def call_expr(callee=None, args=None, kwargs=None):
    node = MagicMock()
    node.callee = callee or literal_expr()
    node.arguments = args or []
    node.keyword_arguments = kwargs or []
    node.accept = lambda visitor: visitor.visit_call_expr(node)
    return node

def list_expr(elements=None):
    node = MagicMock()
    node.elements = elements or []
    node.accept = lambda visitor: visitor.visit_list_expr(node)
    return node

def dict_expr(keys=None, values=None):
    node = MagicMock()
    node.keys = keys or []
    node.values = values or []
    node.accept = lambda visitor: visitor.visit_dict_expr(node)
    return node

def index_expr(obj=None, idx=None):
    node = MagicMock()
    node.object = obj or literal_expr()
    node.index = idx or literal_expr()
    node.accept = lambda visitor: visitor.visit_index_expr(node)
    return node

def setindex_expr(obj=None, idx=None, val=None):
    node = MagicMock()
    node.object = obj or literal_expr()
    node.index = idx or literal_expr()
    node.value = val or literal_expr()
    node.accept = lambda visitor: visitor.visit_setindex_expr(node)
    return node

def slice_expr(lower=None, upper=None):
    node = MagicMock()
    node.lower = lower
    node.upper = upper
    node.accept = lambda visitor: visitor.visit_slice_expr(node)
    return node

def multiindex_expr(obj=None, indices=None):
    node = MagicMock()
    node.object = obj or literal_expr()
    node.indices = indices or [literal_expr()]
    node.accept = lambda visitor: visitor.visit_multiindex_expr(node)
    return node

def memberaccess_expr(obj=None):
    node = MagicMock()
    node.object = obj or literal_expr()
    node.accept = lambda visitor: visitor.visit_memberaccess_expr(node)
    return node

def setmember_expr(obj=None, val=None):
    node = MagicMock()
    node.object = obj or literal_expr()
    node.value = val or literal_expr()
    node.accept = lambda visitor: visitor.visit_setmember_expr(node)
    return node

def fstring_expr(parts=None):
    node = MagicMock()
    node.parts = parts or [literal_expr()]
    node.accept = lambda visitor: visitor.visit_fstring_expr(node)
    return node

def pipe_expr(left=None, right=None):
    node = MagicMock()
    node.left = left or literal_expr()
    node.right = right or literal_expr()
    node.accept = lambda visitor: visitor.visit_pipe_expr(node)
    return node

def unpack_expr(names=None, val=None):
    node = MagicMock()
    node.value = val or literal_expr()
    node.names = names or [make_token("a"), make_token("b")]
    node.accept = lambda visitor: visitor.visit_unpack_expr(node)
    return node

def lambda_expr(params=None, body=None):
    node = MagicMock()
    node.params = [make_token(p) for p in (params or ["x"])]
    node.body = body or literal_expr()
    node.accept = lambda visitor: visitor.visit_lambda_expr(node)
    return node

def listcomp_expr(var_name="x", element=None, iterable=None, condition=None):
    node = MagicMock()
    node.var = make_token(var_name)
    node.element = element or literal_expr()
    node.iterable = iterable or literal_expr()
    node.condition = condition
    node.accept = lambda visitor: visitor.visit_listcomp_expr(node)
    return node

def ternary_expr(then=None, cond=None, else_=None):
    node = MagicMock()
    node.then_expr = then or literal_expr()
    node.condition = cond or literal_expr()
    node.else_expr = else_ or literal_expr()
    node.accept = lambda visitor: visitor.visit_ternary_expr(node)
    return node

def tensor_expr():
    node = MagicMock()
    node.accept = lambda visitor: visitor.visit_tensor_expr(node)
    return node

def expression_stmt(expr=None):
    stmt = MagicMock()
    stmt.expression = expr or literal_expr()
    stmt.accept = lambda visitor: visitor.visit_expression_stmt(stmt)
    return stmt

def block_stmt(stmts=None):
    stmt = MagicMock()
    stmt.statements = stmts or []
    stmt.accept = lambda visitor: visitor.visit_block_stmt(stmt)
    return stmt

def if_stmt(cond=None, then=None, elif_branches=None, else_branch=None):
    stmt = MagicMock()
    stmt.condition = cond or literal_expr()
    stmt.then_branch = then or block_stmt()
    stmt.elif_branches = elif_branches or []
    stmt.else_branch = else_branch
    stmt.accept = lambda visitor: visitor.visit_if_stmt(stmt)
    return stmt

def while_stmt(cond=None, body=None):
    stmt = MagicMock()
    stmt.condition = cond or literal_expr()
    stmt.body = body or block_stmt()
    stmt.accept = lambda visitor: visitor.visit_while_stmt(stmt)
    return stmt

def return_stmt(value=None):
    stmt = MagicMock()
    stmt.value = value
    stmt.accept = lambda visitor: visitor.visit_return_stmt(stmt)
    return stmt

def pass_stmt():
    stmt = MagicMock()
    stmt.accept = lambda visitor: visitor.visit_pass_stmt(stmt)
    return stmt

def break_stmt(keyword=None):
    stmt = MagicMock()
    stmt.keyword = keyword or make_token("break")
    stmt.accept = lambda visitor: visitor.visit_break_stmt(stmt)
    return stmt

def continue_stmt(keyword=None):
    stmt = MagicMock()
    stmt.keyword = keyword or make_token("continue")
    stmt.accept = lambda visitor: visitor.visit_continue_stmt(stmt)
    return stmt

def for_stmt(var_name=None, vars_=None, iterable=None, body=None):
    stmt = MagicMock()
    stmt.iterable = iterable or literal_expr()
    stmt.body = body or block_stmt()
    if vars_ is not None:
        stmt.vars = [make_token(v) for v in vars_]
        stmt.var = None
    else:
        stmt.vars = None
        stmt.var = make_token(var_name or "i")
    stmt.accept = lambda visitor: visitor.visit_for_stmt(stmt)
    return stmt

def function_stmt(name="foo", params=None, body=None, defaults=None, vararg=None, is_static=False):
    stmt = MagicMock()
    stmt.name = make_token(name)
    stmt.params = [make_token(p) for p in (params or [])]
    stmt.body = body or block_stmt()
    stmt.defaults = defaults or []
    stmt.vararg = make_token(vararg) if vararg else None
    stmt.is_static = is_static
    stmt.accept = lambda visitor: visitor.visit_function_stmt(stmt)
    return stmt

def class_stmt(name="MyClass", bases=None, class_vars=None, methods=None):
    stmt = MagicMock()
    stmt.name = make_token(name)
    stmt.bases = bases or []
    stmt.class_vars = class_vars or []
    stmt.methods = methods or []
    stmt.accept = lambda visitor: visitor.visit_class_stmt(stmt)
    return stmt

def try_stmt(try_block=None, except_blocks=None, finally_block=None):
    stmt = MagicMock()
    stmt.try_block = try_block or block_stmt()
    stmt.except_blocks = except_blocks or []
    stmt.finally_block = finally_block
    stmt.accept = lambda visitor: visitor.visit_try_stmt(stmt)
    return stmt

def import_stmt(module_path=None, names=None, alias=None):
    stmt = MagicMock()
    stmt.module_path = module_path or [make_token("mymod")]
    if names is not None:
        stmt.names = names
        stmt.alias = None
    else:
        stmt.names = None
        stmt.alias = make_token(alias) if alias else None
    stmt.accept = lambda visitor: visitor.visit_import_stmt(stmt)
    return stmt

def raise_stmt(exc=None):
    stmt = MagicMock()
    stmt.exception = exc
    stmt.accept = lambda visitor: visitor.visit_raise_stmt(stmt)
    return stmt

def del_stmt(targets=None):
    stmt = MagicMock()
    stmt.targets = targets or [literal_expr()]
    stmt.accept = lambda visitor: visitor.visit_del_stmt(stmt)
    return stmt

def match_stmt(subject=None, cases=None):
    stmt = MagicMock()
    stmt.subject = subject or literal_expr()
    stmt.cases = cases or []
    stmt.accept = lambda visitor: visitor.visit_match_stmt(stmt)
    return stmt

# Tests
class TestScopeManagement:
    def test_initial_scope_exists(self):
        r = make_resolver()
        assert len(r.scopes) == 1
    
    def test_begin_scope_adds_scope(self):
        r = make_resolver()
        r.begin_scope()
        assert len(r.scopes) == 2
    
    def test_end_scope_removes_scope(self):
        r = make_resolver()
        r.begin_scope()
        r.end_scope()
        assert len(r.scopes) == 1
    
    def test_declare_marks_false(self):
        r = make_resolver()
        tok = make_token("x")
        r.declare(tok)
        assert r.scopes[-1]["x"] is False
    
    def test_define_marks_true(self):
        r = make_resolver()
        tok = make_token("x")
        r.declare(tok)
        r.define(tok)
        assert r.scopes[-1]["x"] is True
    
    def test_declare_duplicate_raises(self):
        r = make_resolver()
        tok = make_token("x")
        r.declare(tok)
        with pytest.raises(PulseSemanticError, match="already declared"):
            r.declare(tok)
    
    def test_declare_in_new_scope_is_fine(self):
        r = make_resolver()
        tok = make_token("x")
        r.declare(tok)
        r.define(tok)
        r.begin_scope()
        r.declare(tok)
    
    def test_nested_scopes_are_independent(self):
        r = make_resolver()
        r.begin_scope()
        r.scopes[-1]["a"] = True
        r.begin_scope()
        assert "a" not in r.scopes[-1]
        r.end_scope()
        assert "a" in r.scopes[-1]

class TestResolveLocal:
    def test_resolves_distance_for_local_var(self):
        interp = make_interpreter()
        r = make_resolver(interp)
        r.begin_scope()
        r.scopes[-1]["x"] = True
        expr = variable_expr("x")
        r.resolve_local(expr, expr.name)
        interp.resolve.assert_called_once_with(expr, 0)
    
    def test_resolves_none_for_global_var(self):
        interp = make_interpreter()
        r = make_resolver(interp)
        r.scopes[0]["x"] = True
        expr = variable_expr("x")
        r.resolve_local(expr, expr.name)
        interp.resolve.assert_called_once_with(expr, None)
    
    def test_resolves_none_for_unknown_var(self):
        interp = make_interpreter()
        r = make_resolver(interp)
        expr = variable_expr("unknown")
        r.resolve_local(expr, expr.name)
        interp.resolve.assert_called_once_with(expr, None)
    
    def test_distance_two_scopes_deep(self):
        interp = make_interpreter()
        r = make_resolver(interp)
        r.begin_scope()
        r.scopes[-1]["x"] = True
        r.begin_scope()
        expr = variable_expr("x")
        r.resolve_local(expr, expr.name)
        interp.resolve.assert_called_once_with(expr, 1)

class TestVariableExpr:
    def test_variable_before_assignment_raises(self):
        r = make_resolver()
        r.begin_scope()
        r.scopes[-1]["x"] = False
        with pytest.raises(PulseSemanticError, match="before assignment"):
            r.visit_variable_expr(variable_expr("x"))
    
    def test_variable_after_assignment_ok(self):
        interp = make_interpreter()
        r = make_resolver(interp)
        r.begin_scope()
        r.scopes[-1]["x"] = True
        r.visit_variable_expr(variable_expr("x"))
    
    def test_self_is_skipped(self):
        interp = make_interpreter()
        r = make_resolver(interp)
        r.visit_variable_expr(variable_expr("self"))
        interp.resolve.assert_not_called()
    
    def test_unknown_variable_does_not_raise(self):
        r = make_resolver()
        r.visit_variable_expr(variable_expr("undefined_var"))

class TestAssignExpr:
    def test_assign_resolves_value_and_name(self):
        interp = make_interpreter()
        r = make_resolver(interp)
        r.begin_scope()
        r.scopes[-1]["x"] = True
        expr = assign_expr("x", literal_expr(99))
        r.visit_assign_expr(expr)
        interp.resolve.assert_called()

class TestReturnStatement:
    def test_return_outside_function_raises(self):
        r = make_resolver()
        with pytest.raises(PulseSemanticError, match="top-level"):
            r.visit_return_stmt(return_stmt())
    
    def test_return_inside_function_ok(self):
        r = make_resolver()
        r.current_function = FunctionType.FUNCTION
        r.visit_return_stmt(return_stmt())
    
    def test_return_with_value_inside_function_ok(self):
        r = make_resolver()
        r.current_function = FunctionType.FUNCTION
        r.visit_return_stmt(return_stmt(value=literal_expr(1)))

class TestBreakContinueStatements:
    def test_break_outside_loop_raises(self):
        r = make_resolver()
        with pytest.raises(PulseSemanticError, match="'break'"):
            r.visit_break_stmt(break_stmt())
    
    def test_continue_outside_loop_raises(self):
        r = make_resolver()
        with pytest.raises(PulseSemanticError, match="'continue'"):
            r.visit_continue_stmt(continue_stmt())
    
    def test_break_inside_loop_ok(self):
        r = make_resolver()
        r.loop_depth = 1
        r.visit_break_stmt(break_stmt())
    
    def test_continue_inside_loop_ok(self):
        r = make_resolver()
        r.loop_depth = 1
        r.visit_continue_stmt(continue_stmt())

class TestWhileStatement:
    def test_while_increments_and_decrements_loop_depth(self):
        r = make_resolver()
        depths = []
        original_resolve_stmt = r.resolve_stmt
        def track_depth(stmt):
            depths.append(r.loop_depth)
            original_resolve_stmt(stmt)
        r.resolve_stmt = track_depth
        body = block_stmt()
        stmt = while_stmt(body=body)
        r.visit_while_stmt(stmt)
        assert depths[0] == 1
        assert r.loop_depth == 0
    
    def test_while_resolves_condition(self):
        interp = make_interpreter()
        r = make_resolver(interp)
        cond = literal_expr()
        resolved = []
        cond.accept = lambda v: resolved.append(True)
        r.visit_while_stmt(while_stmt(cond=cond))
        assert resolved

class TestForStatement:
    def test_for_single_var_in_scope(self):
        r = make_resolver()
        r.visit_for_stmt(for_stmt(var_name="item"))
        assert r.loop_depth == 0
    
    def test_for_multi_var_unpacking(self):
        r = make_resolver()
        r.visit_for_stmt(for_stmt(vars_=["a", "b"]))
    
    def test_for_loop_depth(self):
        depths = []
        r = make_resolver()
        orig = r.resolve_stmt
        def capture(s):
            depths.append(r.loop_depth)
            orig(s)
        r.resolve_stmt = capture
        r.visit_for_stmt(for_stmt())
        assert 1 in depths
        assert r.loop_depth == 0

class TestIfStatement:
    def test_if_with_elif_and_else(self):
        r = make_resolver()
        elif_cond = literal_expr()
        elif_branch = block_stmt()
        else_branch = block_stmt()
        stmt = if_stmt(
            elif_branches=[(elif_cond, elif_branch)],
            else_branch=else_branch
        )
        r.visit_if_stmt(stmt)
    
    def test_if_without_else(self):
        r = make_resolver()
        r.visit_if_stmt(if_stmt())

class TestBlockStatement:
    def test_block_creates_and_destroys_scope(self):
        r = make_resolver()
        initial = len(r.scopes)
        r.visit_block_stmt(block_stmt())
        assert len(r.scopes) == initial
    
    def test_block_resolves_inner_statements(self):
        r = make_resolver()
        resolved = []
        inner = MagicMock()
        inner.accept = lambda v: resolved.append(True)
        r.visit_block_stmt(block_stmt(stmts=[inner]))
        assert resolved

class TestFunctionStatement:
    def test_function_declares_and_defines_name(self):
        r = make_resolver()
        r.visit_function_stmt(function_stmt(name="greet"))
        assert r.scopes[-1]["greet"] is True
    
    def test_function_duplicate_name_raises(self):
        r = make_resolver()
        r.visit_function_stmt(function_stmt(name="greet"))
        with pytest.raises(PulseSemanticError, match="already declared"):
            r.visit_function_stmt(function_stmt(name="greet"))
    
    def test_function_type_is_function_outside_class(self):
        r = make_resolver()
        recorded = []
        original = r.resolve_function
        def capture(func, ft): recorded.append(ft); original(func, ft)
        r.resolve_function = capture
        r.visit_function_stmt(function_stmt())
        assert recorded[0] == FunctionType.FUNCTION
    
    def test_function_type_is_method_inside_class(self):
        r = make_resolver()
        r.current_class = ClassType.CLASS
        recorded = []
        original = r.resolve_function
        def capture(func, ft): recorded.append(ft); original(func, ft)
        r.resolve_function = capture
        r.visit_function_stmt(function_stmt())
        assert recorded[0] == FunctionType.METHOD
    
    def test_function_params_in_scope(self):
        r = make_resolver()
        captured_scopes = []
        original_resolve = r.resolve
        def capture_scopes(stmts):
            captured_scopes.append(dict(r.scopes[-1]))
            original_resolve(stmts)
        r.resolve = capture_scopes
        r.visit_function_stmt(function_stmt(name="f", params=["a", "b"]))
        inner = captured_scopes[0]
        assert inner.get("a") is True
        assert inner.get("b") is True
    
    def test_function_vararg_in_scope(self):
        r = make_resolver()
        captured = []
        orig = r.resolve
        def cap(stmts): captured.append(dict(r.scopes[-1])); orig(stmts)
        r.resolve = cap
        r.visit_function_stmt(function_stmt(name="f", vararg="args"))
        assert captured[0].get("args") is True
    
    def test_function_restores_current_function_after(self):
        r = make_resolver()
        r.current_function = FunctionType.NONE
        r.visit_function_stmt(function_stmt())
        assert r.current_function == FunctionType.NONE
    
    def test_method_self_in_scope(self):
        r = make_resolver()
        r.current_class = ClassType.CLASS
        captured = []
        orig = r.resolve
        def cap(stmts): captured.append(dict(r.scopes[-1])); orig(stmts)
        r.resolve = cap
        method = function_stmt(name="do_thing")
        method.is_static = False
        r.visit_function_stmt(method)
        assert captured[0].get("self") is True
    
    def test_static_method_no_self(self):
        r = make_resolver()
        r.current_class = ClassType.CLASS
        captured = []
        orig = r.resolve
        def cap(stmts): captured.append(dict(r.scopes[-1])); orig(stmts)
        r.resolve = cap
        method = function_stmt(name="static_fn")
        method.is_static = True
        r.visit_function_stmt(method)
        assert "self" not in captured[0]

class TestClassStatement:
    def test_class_declares_and_defines(self):
        r = make_resolver()
        r.visit_class_stmt(class_stmt(name="Dog"))
        assert r.scopes[-1]["Dog"] is True
    
    def test_class_restores_class_type(self):
        r = make_resolver()
        r.current_class = ClassType.NONE
        r.visit_class_stmt(class_stmt())
        assert r.current_class == ClassType.NONE
    
    def test_class_sets_class_type_during_resolution(self):
        r = make_resolver()
        recorded = []
        method = function_stmt(name="method")
        orig_resolve_function = r.resolve_function
        def capture(func, ft): recorded.append(r.current_class); orig_resolve_function(func, ft)
        r.resolve_function = capture
        r.visit_class_stmt(class_stmt(methods=[method]))
        assert recorded[0] == ClassType.CLASS
    
    def test_class_with_class_vars(self):
        r = make_resolver()
        val_expr = literal_expr()
        r.visit_class_stmt(class_stmt(class_vars=[(make_token("count"), val_expr)]))
    
    def test_class_duplicate_raises(self):
        r = make_resolver()
        r.visit_class_stmt(class_stmt(name="Foo"))
        with pytest.raises(PulseSemanticError, match="already declared"):
            r.visit_class_stmt(class_stmt(name="Foo"))

class TestTryStatement:
    def test_try_with_except(self):
        r = make_resolver()
        exc_var = make_token("e")
        exc_type = literal_expr()
        block = block_stmt()
        stmt = try_stmt(except_blocks=[(exc_type, exc_var, block)])
        r.visit_try_stmt(stmt)
    
    def test_try_with_finally(self):
        r = make_resolver()
        stmt = try_stmt(finally_block=block_stmt())
        r.visit_try_stmt(stmt)
    
    def test_try_except_var_in_scope(self):
        r = make_resolver()
        captured = []
        orig_resolve_stmt = r.resolve_stmt
        def cap(s): captured.append(dict(r.scopes[-1])); orig_resolve_stmt(s)
        r.resolve_stmt = cap
        exc_var = make_token("err")
        stmt = try_stmt(except_blocks=[(None, exc_var, block_stmt())])
        r.visit_try_stmt(stmt)
        assert any("err" in s for s in captured)
    
    def test_try_without_except_var(self):
        r = make_resolver()
        stmt = try_stmt(except_blocks=[(None, None, block_stmt())])
        r.visit_try_stmt(stmt)

class TestImportStatement:
    def test_import_module_no_alias(self):
        r = make_resolver()
        stmt = import_stmt(module_path=[make_token("math")])
        r.visit_import_stmt(stmt)
        assert r.scopes[-1].get("math") is True
    
    def test_import_module_with_alias(self):
        r = make_resolver()
        stmt = import_stmt(module_path=[make_token("numpy")], alias="np")
        r.visit_import_stmt(stmt)
        assert r.scopes[-1].get("np") is True
    
    def test_import_name_symbols(self):
        r = make_resolver()
        sym = (make_token("sqrt"), None)
        sym_aliased = (make_token("pi"), make_token("PI"))
        stmt = MagicMock()
        stmt.names = [sym, sym_aliased]
        stmt.accept = lambda v: v.visit_import_stmt(stmt)
        r.visit_import_stmt(stmt)
        assert r.scopes[-1].get("sqrt") is True
        assert r.scopes[-1].get("PI") is True

class TestMatchStatement:
    def test_match_with_token_pattern(self):
        from src.tokens import Token
        r = make_resolver()
        pat = make_token("x")
        cases = [(pat, None, block_stmt())]
        r.visit_match_stmt(match_stmt(cases=cases))
    
    def test_match_with_wildcard_pattern(self):
        r = make_resolver()
        pat = make_token("_")
        cases = [(pat, None, block_stmt())]
        r.visit_match_stmt(match_stmt(cases=cases))
    
    def test_match_with_or_pattern(self):
        r = make_resolver()
        pat = ("or", [literal_expr(), literal_expr()])
        cases = [(pat, None, block_stmt())]
        r.visit_match_stmt(match_stmt(cases=cases))
    
    def test_match_with_sequence_pattern(self):
        r = make_resolver()
        sub1 = make_token("a")
        sub2 = make_token("b")
        pat = ("sequence", [sub1, sub2])
        cases = [(pat, None, block_stmt())]
        r.visit_match_stmt(match_stmt(cases=cases))
    
    def test_match_with_mapping_pattern(self):
        r = make_resolver()
        key_expr = literal_expr()
        val_pat = make_token("v")
        pat = ("mapping", [(key_expr, val_pat)])
        cases = [(pat, None, block_stmt())]
        r.visit_match_stmt(match_stmt(cases=cases))
    
    def test_match_with_guard(self):
        r = make_resolver()
        guard = literal_expr()
        pat = make_token("_")
        cases = [(pat, guard, block_stmt())]
        r.visit_match_stmt(match_stmt(cases=cases))
    
    def test_match_scope_per_case(self):
        r = make_resolver()
        initial = len(r.scopes)
        r.visit_match_stmt(match_stmt(cases=[
            (make_token("_"), None, block_stmt()),
            (make_token("_"), None, block_stmt()),
        ]))
        assert len(r.scopes) == initial

class TestExpressionVisitors:
    def test_literal_expr(self):
        r = make_resolver()
        r.visit_literal_expr(literal_expr())
    
    def test_tensor_expr(self):
        r = make_resolver()
        r.visit_tensor_expr(tensor_expr())
    
    def test_grouping_expr(self):
        r = make_resolver()
        r.visit_grouping_expr(grouping_expr())
    
    def test_unary_expr(self):
        r = make_resolver()
        r.visit_unary_expr(unary_expr())
    
    def test_binary_expr(self):
        r = make_resolver()
        r.visit_binary_expr(binary_expr())
    
    def test_logical_expr(self):
        r = make_resolver()
        r.visit_logical_expr(logical_expr())
    
    def test_call_expr_no_args(self):
        r = make_resolver()
        r.visit_call_expr(call_expr())
    
    def test_call_expr_with_args_and_kwargs(self):
        r = make_resolver()
        r.visit_call_expr(call_expr(
            args=[literal_expr()],
            kwargs=[(make_token("key"), literal_expr())]
        ))
    
    def test_list_expr_empty(self):
        r = make_resolver()
        r.visit_list_expr(list_expr())
    
    def test_list_expr_with_elements(self):
        r = make_resolver()
        r.visit_list_expr(list_expr([literal_expr(), literal_expr()]))
    
    def test_dict_expr(self):
        r = make_resolver()
        r.visit_dict_expr(dict_expr(
            keys=[literal_expr()],
            values=[literal_expr()]
        ))
    
    def test_index_expr(self):
        r = make_resolver()
        r.visit_index_expr(index_expr())
    
    def test_setindex_expr(self):
        r = make_resolver()
        r.visit_setindex_expr(setindex_expr())
    
    def test_slice_expr_both_bounds(self):
        r = make_resolver()
        r.visit_slice_expr(slice_expr(lower=literal_expr(), upper=literal_expr()))
    
    def test_slice_expr_no_bounds(self):
        r = make_resolver()
        r.visit_slice_expr(slice_expr())
    
    def test_slice_expr_only_lower(self):
        r = make_resolver()
        r.visit_slice_expr(slice_expr(lower=literal_expr()))
    
    def test_multiindex_expr(self):
        r = make_resolver()
        r.visit_multiindex_expr(multiindex_expr())
    
    def test_memberaccess_expr(self):
        r = make_resolver()
        r.visit_memberaccess_expr(memberaccess_expr())
    
    def test_setmember_expr(self):
        r = make_resolver()
        r.visit_setmember_expr(setmember_expr())
    
    def test_fstring_expr(self):
        r = make_resolver()
        r.visit_fstring_expr(fstring_expr())
    
    def test_pipe_expr(self):
        r = make_resolver()
        r.visit_pipe_expr(pipe_expr())
    
    def test_unpack_expr(self):
        interp = make_interpreter()
        r = make_resolver(interp)
        r.visit_unpack_expr(unpack_expr())
    
    def test_ternary_expr(self):
        r = make_resolver()
        r.visit_ternary_expr(ternary_expr())
    
    def test_lambda_expr(self):
        r = make_resolver()
        r.visit_lambda_expr(lambda_expr())
    
    def test_lambda_creates_new_scope(self):
        r = make_resolver()
        initial = len(r.scopes)
        r.visit_lambda_expr(lambda_expr())
        assert len(r.scopes) == initial
    
    def test_lambda_sets_and_restores_function_type(self):
        r = make_resolver()
        r.current_function = FunctionType.NONE
        r.visit_lambda_expr(lambda_expr())
        assert r.current_function == FunctionType.NONE
    
    def test_listcomp_expr_no_condition(self):
        r = make_resolver()
        r.visit_listcomp_expr(listcomp_expr())
    
    def test_listcomp_expr_with_condition(self):
        r = make_resolver()
        r.visit_listcomp_expr(listcomp_expr(condition=literal_expr()))
    
    def test_listcomp_scope_cleaned_up(self):
        r = make_resolver()
        initial = len(r.scopes)
        r.visit_listcomp_expr(listcomp_expr())
        assert len(r.scopes) == initial

class TestLexicalScopingCorrectness:
    def test_shadowing_in_inner_scope(self):
        interp = make_interpreter()
        r = make_resolver(interp)
        r.scopes[0]["x"] = True
        r.begin_scope()
        r.scopes[-1]["x"] = True
        expr = variable_expr("x")
        r.resolve_local(expr, expr.name)
        interp.resolve.assert_called_with(expr, 0)
    
    def test_closure_captures_outer_variable(self):
        interp = make_interpreter()
        r = make_resolver(interp)
        r.begin_scope()
        r.scopes[-1]["captured"] = True
        r.begin_scope()
        expr = variable_expr("captured")
        r.resolve_local(expr, expr.name)
        interp.resolve.assert_called_with(expr, 1)
    
    def test_global_not_accessible_in_nested_function_through_distance(self):
        interp = make_interpreter()
        r = make_resolver(interp)
        r.scopes[0]["g"] = True
        r.begin_scope()
        r.begin_scope()
        expr = variable_expr("g")
        r.resolve_local(expr, expr.name)
        interp.resolve.assert_called_with(expr, None)
    
    def test_full_function_resolution_flow(self):
        interp = make_interpreter()
        r = make_resolver(interp)
        body = block_stmt()
        stmt = function_stmt(name="add", params=["a", "b"], body=body)
        r.resolve([stmt])
        assert r.scopes[-1]["add"] is True
    
    def test_nested_function_does_not_leak_scope(self):
        r = make_resolver()
        inner = function_stmt(name="inner", params=["z"])
        outer = function_stmt(name="outer", params=["y"], body=block_stmt(stmts=[inner]))
        r.resolve([outer])
        assert "inner" not in r.scopes[-1]
        assert "y" not in r.scopes[-1]
        assert "z" not in r.scopes[-1]
    
    def test_variable_use_before_declare_raises(self):
        r = make_resolver()
        r.begin_scope()
        r.scopes[-1]["x"] = False
        with pytest.raises(PulseSemanticError, match="before assignment"):
            r.visit_variable_expr(variable_expr("x"))

class TestPassRaiseDel:
    def test_pass_stmt(self):
        r = make_resolver()
        r.visit_pass_stmt(pass_stmt())
    
    def test_raise_with_exception(self):
        r = make_resolver()
        r.visit_raise_stmt(raise_stmt(exc=literal_expr()))
    
    def test_raise_without_exception(self):
        r = make_resolver()
        r.visit_raise_stmt(raise_stmt(exc=None))
    
    def test_del_stmt(self):
        r = make_resolver()
        r.visit_del_stmt(del_stmt(targets=[literal_expr(), literal_expr()]))

class TestResolveEntry:
    def test_resolve_empty_list(self):
        r = make_resolver()
        r.resolve([])
    
    def test_resolve_multiple_statements(self):
        r = make_resolver()
        r.resolve([pass_stmt(), pass_stmt(), pass_stmt()])
    
    def test_resolve_expr_delegates(self):
        r = make_resolver()
        visited = []
        expr = MagicMock()
        expr.accept = lambda v: visited.append(True)
        r.resolve_expr(expr)
        assert visited
    
    def test_resolve_stmt_delegates(self):
        r = make_resolver()
        visited = []
        stmt = MagicMock()
        stmt.accept = lambda v: visited.append(True)
        r.resolve_stmt(stmt)
        assert visited