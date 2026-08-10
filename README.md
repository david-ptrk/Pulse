JMJ

# Pulse — The AI-Native Programming Language

**Pulse** is a domain-specific programming language designed for artificial intelligence and machine learning. Unlike general-purpose languages that rely heavily on external libraries, Pulse aims to integrate AI-focused operations directly into the language.

## Features

* AI and machine-learning focused syntax
* Tensor-based operations
* Built-in AI-oriented functionality
* Native extensions for performance-critical operations
* Python-based interpreter with native components

## Project Structure

```text
src/       — Interpreter source code
native/    — C source files for native extensions
bin/       — Generated native binaries (not committed)
docs/      — Documentation and development notes
examples/  — Example Pulse programs
tests/     — Test suite and validation
website/   — Official Pulse website
```

## Building

Pulse currently requires its native components to be built before running the interpreter.

### Windows

Requires [MinGW](https://www.mingw-w64.org/).

```bat
cd native
.\build.bat
```

The generated `.dll` files will be placed in `bin/`.

### Linux

```bash
cd native
./build.sh
```

The generated native libraries will be placed in `bin/`.

## Running Pulse

After building the native components:

```bash
python pulse.py <path_to_file.pul>
```

For example:

```bash
python pulse.py examples/example.pul
```

## Development

Create and activate a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the project dependencies:

```bash
pip install -r requirements.txt
```

Run the test suite:

```bash
pytest
```

## Authors

* Daud Anjum
* Hafiz Muhammad Ahmad

## License

This project is licensed under the MIT License.
