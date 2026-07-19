# Samrat Programming Language

**Version 1.0.0** — A modern, readable, English-like programming language built from scratch.

Samrat combines the clean syntax of Python with the expressiveness of C++/Java/Rust. It features strong static typing, type inference, classes, recursion, and a full standard library — all implemented in pure Python with zero dependencies.

## Features

- **English-like syntax** — Keywords read like natural English (`let`, `func`, `constructor`, `and`/`or`/`not`)
- **Strong static typing** with type inference — Catch errors at compile time, not runtime
- **Multi-paradigm** — Imperative, object-oriented, and functional patterns
- **Rich standard library** — `math`, `string`, `time` modules built in
- **File I/O** — Read and write files with a simple API
- **Error handling** — `try`/`catch`/`throw` for robust programs
- **Classes** — With fields, constructors, methods, and `this`
- **Recursion** — Full support for recursive functions
- **No dependencies** — Pure Python standard library only
- **Cross-platform** — Runs on Windows, macOS, and Linux

## Quick Start

```bash
# Clone or download the project
cd samrat

# Run the REPL (interactive mode)
python src/main.py

# Run a .samrat file
python src/main.py examples/hello.samrat
```

### Hello World

```samrat
print("Hello, World!")
```

### Fibonacci

```samrat
func fibonacci(n: int) -> int {
    if n <= 1 {
        return n
    }
    return fibonacci(n - 1) + fibonacci(n - 2)
}

for i in 0..10 {
    print(fibonacci(i))
}
```

### FizzBuzz

```samrat
for i in 1..101 {
    if i % 15 == 0 {
        print("FizzBuzz")
    } elif i % 3 == 0 {
        print("Fizz")
    } elif i % 5 == 0 {
        print("Buzz")
    } else {
        print(i)
    }
}
```

## Using the REPL

```
$ python src/main.py
==================================================
  Samrat Programming Language v1.0.0
  Type 'exit()' or 'quit()' to exit
==================================================

>>> print("Hello!")
Hello!
>>> let x = 5
>>> x + 3
8
>>> func square(n: int) -> int {
...     return n * n
... }
>>> square(4)
16
>>> exit()
```

## Project Structure

```
samrat/
├── LANGUAGE_SPEC.md          # Full language specification
├── src/
│   ├── main.py               # Entry point (REPL + file runner)
│   ├── tokens.py             # Token type definitions
│   ├── errors.py             # Error handling classes
│   ├── lexer.py              # Lexer / tokenizer
│   ├── ast_nodes.py          # AST node definitions
│   ├── parser.py             # Recursive-descent parser
│   ├── symbol_table.py       # Symbol table and scoping
│   ├── semantic.py           # Semantic analysis and type checking
│   ├── interpreter.py        # Tree-walking interpreter
│   ├── bytecode.py           # Bytecode instruction set (compiler)
│   ├── compiler.py           # Bytecode compiler
│   ├── vm.py                 # Stack-based virtual machine
│   └── compiler_main.py      # Compiler entry point
├── tests/
│   ├── test_lexer.py         # Lexer tests
│   ├── test_parser.py        # Parser tests
│   ├── test_semantic.py      # Semantic analysis tests
│   ├── test_interpreter.py   # Interpreter tests
│   ├── test_comprehensive.py # Comprehensive test suite
│   └── test_compiler.py      # Compiler/VM tests
├── examples/                 # Example .samrat programs
└── docs/                     # Documentation
    ├── README.md
    ├── INSTALL.md
    ├── CONTRIBUTING.md
    ├── CHANGELOG.md
    ├── LANGUAGE_REFERENCE.md
    ├── STDLIB_REFERENCE.md
    └── future_features.md
```

## Running Tests

```bash
# Run individual test suites
python tests/test_lexer.py
python tests/test_parser.py
python tests/test_semantic.py
python tests/test_interpreter.py

# Run comprehensive test suite
python tests/test_comprehensive.py

# Run compiler/VM tests
python tests/test_compiler.py
```

## License

Samrat is open source. See LICENSE for details.