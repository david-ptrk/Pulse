# Phase 2 Journal — Pulse

## Step 1: Lexer / Tokenizer (05-13 Dec 2025)

- Created TokenType, Token, and Lexer.
- Decided to ingnore comments entirely - no Token is generated for them.
- Created a syntax for Tensor Literal:  
  `a = @[[1, 2], [3, 4]]`
- Updated `docs/spec_v1.md` and `docs/tokens.md` to reflect changes.
- Updated examples in `examples/` accordingly.
- Tested Lexer to verify correct Tokens generation.
- Made additional TokenType adjustments were necessary.
- Documented Lexer code for readability.
- Created `LexerError` class for unified formatted errors reporting.

## Step 2: Parser / AST Construction (04 Feb - 15 Mar 2026)

- Created Parser, including `generate_ast`, `ast_printer`.
- Decided to limit grammar rules to some core functionalities.
- All grammar rules used in Pulse v1.0 are documented in `docs/grammar.md`.
- Verified Parser output to ensure correct AST generation.
- Pulse Parser v1.0 is now frozen - no structural changes will be made without prior documentation in this journal.

## Step 3: Error Reporting & Environment (16-19 Mar 2026)

- Implemented unified runtime error handling system.
- Added `Environment` class with lexical scoping support.
- Enabled variable definition, lookup, and assignment across nested scopes.
- Integrated environment structure to support future interpreter execution.

## Step 4: Interpreter (19 Mar - 9 May 2026)

- Implemented tree-walk interpreter using the visitor pattern.
- Supported evaluation of all expression types: literals, variables, binary, unary, logical, grouping, assignment, and member access.
- Implemented statament execution: variable declarations, blocks, if/elif/else, while, for loops, function definitions, class definitions, return, break, continue, pass.
- Added lexical scoping with closures - functions capture their definition environment.
- Implemented class system with inheritance, instance fields, methods, static methods, and `__init__`.
- Added try/except/else/finally error handling with typed exception matching.
- Implemented `import` and `from ... import ...` for built-in and user-defined `.pul` modules.
- Added resolver (static scope analysis) pass before interpretation to detect variable usage errors early.
- Implemented built-in functions: `print`, `input`, `str`, `int`, `float`, `bool`, `type`, `abs`, `pow`, `min`, `max`, `len`, `range`, `round`, `sum`, `any`, `all`, `enumerate`, `zip`.
- Added built-in exception classes: `Exception`, `RuntimeError`, `ValueError`, `TypeError`.
- Added list methods: `append`, `pop`, `insert`, `slice`, `contains`, `reverse`, `clear`, `sort`, `map`, `filter`, `index`, `find`, `extend`, `count`.
- Added string methods: `upper`, `lower`, `trim`, `split`, `join`, `replace`, `starts_with`, `ends_with`, `contains`, `length`, `find`, `index`, `count`, `format`.
- Added dict methods: `keys`, `values`, `item`, `has`, `remove`, `length`.
- Added tensor operations: arithmetic, matrix multiple, slicing, shape, reshape, flatten, sum, mean, min, max, transpose.
- Implemented f-strings and triple-quoted multi-line strings.
- Added pipe operator `|>`, ternary expressions, chained comparisons, `is`/`is not`, `in`/`not in`.
- Added augmented assignment operators: `+=`, `-=`, `*=`, `/=`, `%=`.
- Added lambda expressions, list comprehensions, `*args`, and default parameter values.
- Added `match/case` pattern matching with literal, capture, OR, guard, sequence, and mapping patterns.
- Added `del` for variables, list indices, and dict keys.
- Added `raise` for user-defined exceptions.
- Added power operator `**`.
- Offloaded module file I/O to C via `ctypes` for performance (`native/pulse_loader.c`).
- Offloaded math functions to C via `ctypes` for performance (`native/pulse_math.c`).
- Added `BuiltinFunction` fast-path in the interpreter, bypassing the full call pipeline for stdlib and built-in calls.
- Added module-level caching to prevent repeated lex/parse/execute on repeated imports.
- Implemented interactive REPL with multi-line input, auto-indent, error recovery, and arrow-key history.
- Added `--time` flag for pipeline timing breakdown (lexing, parsing, resolving, interpretation).
- Added `--info` flag with full language reference guide.

## Step 5: Standard Library (May 2026)

- `math` - mathematical functions backed by C: `sqrt`, `floor`, `ceil`, `log`, `log2`, `log10`, `exp`, `sin`, `cos`, `tan`, `abs`, `pow`; constants `pi`, `e`, `inf`, `tau`.
- `io` - file I/O: `read_file`, `write_file`, `append_file`, `file_exists`, `read_lines`.
- `time` - timing utilities: `now`, `clock`, `sleep`.
- `random` - random number generation: `random`, `randint`, `uniform`, `randrange`, `choice`, `choices`, `sample`, `shuffle`, `gauss`, `normalvariate`, `expovariate`, `triangular`, `seed`, `get_state`.
- `os` - operating system interface: directory management, file operations, path manipulation, environment variables, and system info.
- `models` - ML models: `LinearRegression`, `LogisticRegression`, `DecisionTree`, `RandomForest`, `KMeans`, `KNN`, `SVC`, `NeuralNetwork`, `Model.auto`; each with `train`, `predict`, `score`, `explain`; `auto_preprocess=True` for automatic preprocessing, and `verbose=True` mode for training output.
- `preprocess` - data preprocessing: `normalize`, `standardize`, `min_max_scale`, `train_test_split`, `shuffle`, `flatten_data`, `one_hot_encode`.
- `metrics` - model evaluation: `accuracy`, `precision`, `recall`, `f1`, `confusion_matrix`, `classification_report`, `mse`, `rmse`, `mae`, `r2`, `mape`, `summary`.
- `learn` - educational ML examples with step-by-step explanations: `linear_regression`, `logistic_regression`, `knn`, `decision_tree`, `random_forest`, `kmeans`, `neural_network`.
- `datasets` - dataset loading utilities: `iris`, `wine`, `digits`, `breast_cancer`, `diabetes`, `make_classification`, `make_regression`, `make_blobs`, `make_moons`, `make_circles`, `load_csv`.
