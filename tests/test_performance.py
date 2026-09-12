import time
import pytest
from src.lexer import Lexer
from src.parser import Parser
from src.resolver import Resolver
from src.interpreter import Interpreter
from src.environment import Environment
from pulse import run

def timed_run(source: str, env: Environment = None) -> float:
    if env is None:
        env = Environment()
    
    def output(text, end="\n"):
        pass
    
    start = time.perf_counter()
    run(source, output=output, env=env)
    return time.perf_counter() - start

def timed_pipeline_stages(source: str) -> dict:
    timings = {}
    
    start = time.perf_counter()
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    timings["lex"] = time.perf_counter() - start
    
    start = time.perf_counter()
    parser = Parser(tokens, source)
    statements = parser.parse()
    timings["parse"] = time.perf_counter() - start
    
    env = Environment()
    interpreter = Interpreter(env)
    
    start = time.perf_counter()
    resolver = Resolver(interpreter)
    resolver.resolve(statements)
    timings["resolve"] = time.perf_counter() - start
    
    start = time.perf_counter()
    interpreter.interpret(statements, source)
    timings["interpret"] = time.perf_counter() - start
    
    return timings

def make_counting_loop_source(iterations: int) -> str:
    return (
        "total = 0\n"
        "i = 0\n"
        f"while i < {iterations}:\n"
        "    total += i\n"
        "    i += 1\n"
    )

def make_large_source(statement_count: int) -> str:
    lines = [f"x{i} = {i}\n" for i in range(statement_count)]
    return "".join(lines)

class TestPipelineStagePerformance:
    def test_lexer_handles_large_source_quickly(self):
        source = make_large_source(5000)
        start = time.perf_counter()
        tokens = Lexer(source).scan_tokens()
        elapsed = time.perf_counter() - start
        
        assert len(tokens) > 0
        assert elapsed < 5.0, f"Lexing 5000 statements took {elapsed:.3f}s, expected < 5.0s"
    
    def test_parser_handles_large_source_quickly(self):
        source = make_large_source(5000)
        tokens = Lexer(source).scan_tokens()
        
        start = time.perf_counter()
        statements = Parser(tokens, source).parse()
        elapsed = time.perf_counter() - start
        
        assert len(statements) == 5000
        assert elapsed < 5.0, f"Parsing 5000 statements took {elapsed:.3f}s, expected < 5.0s"
    
    def test_full_pipeline_stage_breakdown_stays_bounded(self):
        source = make_large_source(2000)
        timings = timed_pipeline_stages(source)
        
        for stage, elapsed in timings.items():
            assert elapsed < 5.0, f"Stage '{stage}' took {elapsed:.3f}s, expected < 5.0s"

class TestLoopPerformance:
    def test_moderate_while_loop_completes_quickly(self):
        source = make_counting_loop_source(10_000)
        elapsed = timed_run(source)
        assert elapsed < 10.0, f"10k-iteration while loop took {elapsed:.3f}s, expected < 10.0s"
    
    def test_for_loop_over_large_list_completes_quickly(self):
        source = (
            "total = 0\n"
            "for i in range(10000):\n"
            "    total += i\n"
        )
        elapsed = timed_run(source)
        assert elapsed < 10.0, f"10k-iteration for loop took {elapsed:.3f}s, expected < 10.0s"
    
    def test_nested_loops_stay_within_bound(self):
        source = (
            "total = 0\n"
            "for i in range(100):\n"
            "    for j in range(100):\n"
            "        total += i * j\n"
        )
        elapsed = timed_run(source)
        assert elapsed < 10.0, f"100x100 nested loop took {elapsed:.3f}s, expected < 10.0s"

class TestFunctionCallPerformance:
    def test_many_sequential_function_calls(self):
        source = (
            "def square(x):\n"
            "    return x * x\n"
            "\n"
            "total = 0\n"
            "i = 0\n"
            "while i < 5000:\n"
            "    total += square(i)\n"
            "    i += 1\n"
        )
        elapsed = timed_run(source)
        assert elapsed < 10.0, f"5000 function calls took {elapsed:.3f}s, expected < 10.0s"
    
    def test_recursive_fibonacci_moderate_depth(self):
        source = (
            "def fib(n):\n"
            "    if n <= 1:\n"
            "        return n\n"
            "    return fib(n - 1) + fib(n - 2)\n"
            "\n"
            "print(fib(20))\n"
        )
        elapsed = timed_run(source)
        assert elapsed < 15.0, f"fib(20) took {elapsed:.3f}s, expected < 15.0s"
    
    def test_recursion_depth_within_configured_limit(self):
        source = (
            "def count_down(n):\n"
            "    if n <= 0:\n"
            "        return 0\n"
            "    return count_down(n - 1)\n"
            "\n"
            "count_down(1000)\n"
        )
        elapsed = timed_run(source)
        assert elapsed < 10.0, f"1000-deep recursion took {elapsed:.3f}s, expected < 10.0s"

class TestDataStructurePerformance:
    def test_list_append_loop(self):
        source = (
            "items = []\n"
            "i = 0\n"
            "while i < 5000:\n"
            "    items.append(i)\n"
            "    i += 1\n"
        )
        elapsed = timed_run(source)
        assert elapsed < 10.0, f"5000 list appends took {elapsed:.3f}s, expected < 10.0s"
    
    def test_dict_insert_loop(self):
        source = (
            "d = {}\n"
            "i = 0\n"
            "while i < 5000:\n"
            '    d[str(i)] = i\n'
            "    i += 1\n"
        )
        elapsed = timed_run(source)
        assert elapsed < 10.0, f"5000 dict inserts took {elapsed:.3f}s, expected < 10.0s"
    
    def test_list_comprehension_over_large_range(self):
        source = "squares = [x * x for x in range(5000)]\n"
        elapsed = timed_run(source)
        assert elapsed < 10.0, f"5000-element list comprehension took {elapsed:.3f}s, expected < 10.0s"

class TestTensorPerformance:
    def test_tensor_elementwise_addition(self):
        source = (
            "a = @[[1, 2, 3], [4, 5, 6], [7, 8, 9]]\n"
            "b = @[[1, 1, 1], [1, 1, 1], [1, 1, 1]]\n"
            "for i in range(1000):\n"
            "    c = a + b\n"
        )
        elapsed = timed_run(source)
        assert elapsed < 15.0, f"1000 tensor additions took {elapsed:.3f}s, expected < 15.0s"
    
    def test_tensor_matmul(self):
        source = (
            "a = @[[1, 2], [3, 4]]\n"
            "b = @[[5, 6], [7, 8]]\n"
            "for i in range(500):\n"
            "    c = a @ b\n"
        )
        elapsed = timed_run(source)
        assert elapsed < 15.0, f"500 tensor matmuls took {elapsed:.3f}s, expected < 15.0s"

class TestRepeatedRunPerformance:
    def test_many_sequential_run_calls_on_shared_env_stay_bounded(self):
        env = Environment()
        start = time.perf_counter()
        for i in range(500):
            run(f"x = {i}\n", env=env)
        elapsed = time.perf_counter() - start
        assert elapsed < 10.0, f"500 sequential run() calls took {elapsed:.3f}s, expected < 10.0s"
