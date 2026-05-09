"""
pulse.py

Entry point for the Pulse programming language.
"""

import sys
sys.setrecursionlimit(50000)

from src.tokens import TokenType
from src.lexer import Lexer
from src.parser import Parser
from src.interpreter import Interpreter
from src.resolver import Resolver
from src.environment import Environment
from src.error import PulseError, report_error
from src.runtime import PulseRuntimeException
from src.values import PulseNull
import argparse
from time import perf_counter

# Global runtime environment
global_env = Environment()
interpreter = Interpreter(global_env)

# Core pipeline
def run(source: str) -> any:
    # 1. Lexing
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    
    # 2. Parsing
    parser = Parser(tokens, source)
    statements = parser.parse()
    
    # 3. Resolving (static analysis)
    resolver = Resolver(interpreter)
    resolver.resolve(statements)
    
    # 4. Interpretation
    return interpreter.interpret(statements, source)

def run_with_time(source: str) -> any:
    total_start = perf_counter()
    
    start = perf_counter()
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    lex_time = perf_counter() - start
    
    start = perf_counter()
    parser = Parser(tokens, source)
    statements = parser.parse()
    parse_time = perf_counter() - start
    
    start = perf_counter()
    resolver = Resolver(interpreter)
    resolver.resolve(statements)
    resolve_time = perf_counter() - start
    
    start = perf_counter()
    result = interpreter.interpret(statements, source)
    interpret_time = perf_counter() - start
    
    total_time = perf_counter() - total_start
    
    print("\n=== Pipeline Timing ===")
    print(f"Lexing:        {lex_time:.6f}s")
    print(f"Parsing:       {parse_time:.6f}s")
    print(f"Resolving:     {resolve_time:.6f}s")
    print(f"Interpret:     {interpret_time:.6f}s")
    print(f"Total:         {total_time:.6f}s")
    
    return result

# File Execution
def run_file(path: str, show_time: bool) -> None:
    try:
        with open(path, "r", encoding="utf-8") as f:
            source = f.read()
    except FileNotFoundError:
        print(f"pulse: cannot open file '{path}': no such file", file=sys.stderr)
        sys.exit(1)
    
    try:
        if show_time:
            run_with_time(source)
        else:
            run(source)
    except PulseRuntimeException as e:
        report_error(e.error)
        sys.exit(1)
    except PulseError as e:
        report_error(e)
        sys.exit(1)

# REPL
_REPL_VERSION = "0.1"
_INDENT_KEYWORDS = (
    "if", "else", "elif", "for", "while", "def", "class", "try",
    "except", "finally", "match", "case",
)

def _is_incomplete(source: str) -> bool:
    stripped = source.strip()
    if not stripped:
        return False
    if stripped.count("(") > stripped.count(")"):
        return True
    if stripped.count("[") > stripped.count("]"):
        return True
    if stripped.count("{") > stripped.count("}"):
        return True
    if stripped.endswith(":"):
        return True
    return False

def _enable_history() -> None:
    try:
        import readline
        readline.parse_and_bind("tab: complete")
    except ImportError:
        pass

def run_prompt() -> None:
    _enable_history()
    
    print(f"Pulse {_REPL_VERSION} - interactive mode")
    print(f"Python {sys.version.split()[0]} on {sys.platform}")
    print('Type "exit" or press Ctrl+Z to quit.\n')
    
    buffer = []
    indent_level = 0
    
    while True:
        prompt = ("... " + "    " * indent_level) if buffer else ">>> "
        
        try:
            line = input(prompt)
        except EOFError:
            print()
            break
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt")
            buffer = []
            indent_level = 0
            continue
        
        if not buffer and line.strip() in ("exit", "exit()", "quit", "quit()"):
            print("Goodbye.")
            break
        
        if line.strip() == "":
            if buffer:
                source = "\n".join(buffer)
                buffer = []
                indent_level = 0
                _repl_run(source)
            continue
        
        indented_line = "    " * indent_level + line.strip()
        buffer.append(indented_line)
        
        stripped = line.strip()
        if stripped.endswith(":"):
            indent_level += 1
        elif stripped in ("pass", "break", "continue") or stripped.startswith("return"):
            indent_level = max(0, indent_level - 1)
        
        source = "\n".join(buffer)
        
        if not _is_incomplete(source) and not _is_in_block(buffer):
            buffer = []
            indent_level = 0
            _repl_run(source)

def _is_in_block(buffer: list[str]) -> bool:
    for line in reversed(buffer):
        if line.strip():
            return line.startswith(" ") or line.startswith("\t")
        return False

def _repl_run(source: str) -> None:
    try:
        result = run(source)
        if result is not None and not isinstance(result, PulseNull):
            print(repr(result))
    except PulseRuntimeException as e:
        report_error(e.error)
    except PulseError as e:
        report_error(e)
    except Exception as e:
        print(f"[Internal Error] {e}")

def _show_help() -> None:
    line = "=" * 60
    line2 = "-" * 60
    
    print(f"""
{line}
  Pulse Programming Language - Reference Guide
{line}

USAGE
  py pulse.py <file.pul>          Run a Pulse program
  py pulse.py                     Start interactive REPL
  py pulse.py <file.pul> --time   Run with pipeline timing
  py pulse.py --info              Show this reference guide


{line2}
  LANGUAGE FEATURES
{line2}

TYPES
  number       42, 3.14, -7, 0.5
  string       "hello", 'world'
  boolean      True, False
  null         null, None
  list         [1, 2, 3]
  dict         {{ "key": "value" }}
  range        range(0, 10)
  tensor       @[[1, 2], [3, 4]]

VARIABLES
  x = 10
  name = "Pulse"
  x += 1    x -= 1

OPERATIONS
  Arithmetic   +  -  *  /  //  %  **
  Comparison   ==  !=  <  >  <=  >=  is  is not
  Logical      and  or  not
  Membership   in  not in
  Chained      0 < x < 10
  Pipe         value |> function
  Ternary      x if condition else y

STRINGS
  "Hello, " + name
  f"Hello, {{ name }}!"
  "Hello, {{  }}".format(name)
  \"\"\"multi
  line\"\"\"

CONTROL FLOW
  if x > 0:
      print("positive")
  elif x == 0:
      print("zero")
  else:
      print("negative")

  while x > 0:
      x -= 1

  for item in [1, 2, 3]:
      print(item)

  for i, val in enumerate(items):
      print(i, val)

  match status:
      case 200:
          print("OK")
      case 404 | 405:
          print("Not Found")
      case n if n >= 500:
          print("Server Error")
      case _:
          print("Unknown")

FUNCTIONS
  def add(a, b):
      return a + b

  def greet(name, msg="hello"):
      print(f"{{msg}}, {{name}}!")

  def sum_all(*args):
      total = 0
      for n in args:
          total += n
      return total

  double = lambda x: x * 2

CLASSES
  class Animal:
      name = "unknown"
      def __init__(self, name):
          self.name = name
      def speak(self):
          print(f"{{self.name}} speaks")

  class Dog(Animal):
      def speak(self):
          print(f"{{self.name}} barks")

ERROR HANDLING
  try:
      result = divide(a, b)
  except ValueError as e:
      print("Value error")
  except:
      print("Unknown error")
  else:
      print("Success")
  finally:
      print("Done")

  raise ValueError("something went wrong")

LIST OPERATIONS
  nums = [3, 1, 4, 1, 5]
  nums.append(9)
  nums.pop()
  nums.insert(0, 0)
  nums.sort()
  nums.sort(key=lambda x: -x, reverse=True)
  nums.reverse()
  nums.extend([6, 7])
  nums.map(lambda x: x * 2)
  nums.filter(lambda x: x > 2)
  nums.index(4)
  nums.find(99)       # returns -1 if not found
  nums.count(1)
  nums.contains(3)
  nums.slice(1, 3)
  nums.clear()

STRING METHODS
  s.upper()    s.lower()    s.trim()
  s.split()    s.join(lst)  s.replace(old, new)
  s.starts_with(p)          s.ends_with(p)
  s.contains(sub)           s.length()
  s.find(sub)  s.index(sub) s.count(sub)
  s.format(a, b)

DICT METHODS
  d.keys()    d.values()    d.items()
  d.has(key)  d.remove(key) d.length()

COMPREHENSIONS & UNPACKING
  d.keys()    d.values()    d.items()
  d.has(key)  d.remove(key) d.length()

IMPORTS
  import math
  from math import sqrt, pi
  import math as m

DEL
  del x
  del nums[0]
  del d["key"]


{line2}
  BUILT-IN FUNCTIONS
{line2}

  print(x, sep=" ", end="\\n")
  input(prompt)
  str(x)      int(x)      float(x)    bool(x)
  type(x)     len(x)      abs(x)      round(x, digits)
  pow(b, e)   min(...)    max(...)    sum(iterable)
  any(iter)   all(iter)
  range(stop)
  range(start, stop)
  range(start, stop, step)
  enumerate(iter, start=0)
  zip(iter1, iter2)


{line2}
  STANDARD LIBRARY
{line2}

  math        sqrt, floor, ceil, log, log2, log10, exp,
              sin, cos, tan, abs, pow, pi, e, inf, tau

  io          read_file, write_file, append_file,
              file_exists, read_lines

  os          getcwd, chdir, listdir, mkdir, makedirs,
              rmdir, removedirs, rmtree, remove, rename, copy,
              exists, is_file, is_dir, is_abs, join, basename,
              dirname, abspath, splitext, split, getsize,
              stat, getenv, setenv, env_vars, platform, sep

  time        now, clock, sleep

  random      random, randint, uniform, randrange,
              choice, choices, sample, shuffle,
              gauss, normalvariate, expovariate,
              triangular, seed, get_state

  models      LinearRegression, LogisticRegression,
              DecisionTree, RandomForest, KMeans,
              KNN, SVC, NeuralNetwork, Model.auto
              → model.train(X, y, auto_preprocess=True, verbose=True)
              → model.predict(X)
              → model.score(X, y)
              → model.explain(feature_names)

  preprocess  normalize, standardize, min_max_scale,
              train_test_split, shuffle, flatten_data,
              one_hot_encode

  metrics     accuracy, precision, recall, f1,
              confusion_matrix, classification_report,
              mse, rmse, mae, r2, mape, summary

  learn       example, topics
              → learn.example("linear_regression")
              → learn.example("logistic_regression")
              → learn.example("knn")
              → learn.example("decision_tree")
              → learn.example("random_forest")
              → learn.example("kmeans")
              → learn.example("neural_network")

  datasets    iris, wine, digits, breast_cancer,
              diabetes, make_classfication, make_regression,
              make_blobs, make_moons, make_circles, load_csv


{line2}
  TENSOR OPERATIONS
{line2}

  t = @[[1, 2, 3], [4, 5, 6]]
  t.shape      t.ndim       t.size       t.dtype
  t.T          t.flatten()  t.reshape(2, 3)
  t.sum()      t.mean()     t.min()      t.max()
  t + s        t - s        t * s        t / s
  t @ s        (matrix multiply)
  t[0]         t[0, 1]      t[1:]

{line}
""")

def main() -> int:
    parser = argparse.ArgumentParser(prog="pulse", description="Pulse Programming Language", add_help=True)
    
    parser.add_argument("file", nargs="?", help="Pulse source file (.pul)")
    parser.add_argument("--time", action="store_true", help="Show pipeline timing")
    parser.add_argument("--info", action="store_true", help="Show language reference")
    args = parser.parse_args()
    
    if args.info:
        _show_help()
        return 0
    
    # REPL mode
    if args.file is None:
        run_prompt()
        return 0
    
    # Validate extension
    if not args.file.lower().endswith(".pul"):
        report_error(PulseError(f'Unsupported file type: "{args.file}". Expected a .pul file.'))
        return 1
    
    run_file(args.file, args.time)
    return 0

# Entry point
if __name__ == "__main__":
    sys.exit(main())