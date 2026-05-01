JMJ

# Pulse — The AI-Native Programming Language

**Pulse** is a domain-specific programming language designed for AI and machine learning. Unlike gerenal-purpose languages that rely heavily on external libraries, this language integrates AI-focused operations directly into its syntax.

## Folder Structure

- `src/` — interpreter source code
- `native/` - C source files for native extensions
- `bin/` - compilder native binaries (generated, not committed)
- `docs/` — documentation and journals
- `examples/` — example Pulse programs
- `tests/` — test scripts and validation
- `website/` — official website for the Pulse Language

## Building Native Extensions

Requires [MinGW](https://www.mingw-w64.org/) gcc on Windows.

```bat
cd native
.\build.bat
```

Output `.dll` files will be placed in `bin/`. This step is required before running the interpreter.

## Running

```bat
py pulse.py <path_to_file.pul>
```

## Authors

- Daud Anjum
- Hafiz Muhammad Ahmad

## License

This project is licensed under the MIT License.
