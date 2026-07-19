# Samrat Architecture Guide

## Overview

Samrat is a multi-paradigm programming language implemented as a tree-walking
interpreter with an optional bytecode compiler and stack-based virtual machine.
The entire implementation is ~4000 lines of Python using only the standard library.

## Pipeline Architecture

```
Source Code
    │
    ▼
┌─────────────┐
│   Lexer     │  Phase 1: Tokenization
│  (lexer.py) │  Character-by-character scanning
└─────────────┘          │ Produces: List of Tokens
    │
    ▼
┌─────────────┐
│   Parser    │  Phase 2: Parsing
│  (parser.py)│  Recursive-descent with precedence climbing
└─────────────┘          │ Produces: Abstract Syntax Tree (AST)
    │
    ▼
┌──────────────┐
│  Semantic    │  Phase 3: Semantic Analysis
│  Analyzer    │  Type checking, name resolution, scoping
│ (semantic.py)│
└──────────────┘          │ Validates: AST is semantically correct
    │
    ├────────────────────────────────────┐
    ▼                                    ▼
┌──────────────┐              ┌──────────────────┐
│ Interpreter  │  OR          │    Compiler      │  Phase 4a
│(interpreter.py)│             │  (compiler.py)    │
│ Tree-walking │              │  AST → Bytecode   │
└──────────────┘              └──────────────────┘
    │                                    │
    │                                    ▼
    │                         ┌──────────────────┐
    │                         │   Optimizer      │  Phase 4b
    │                         │ (optimizer.py)    │
    │                         │ Constant folding, │
    │                         │ DCE, peephole     │
    │                         └──────────────────┘
    │                                    │
    │                                    ▼
    │                         ┌──────────────────┐
    │                         │   Virtual Machine│  Phase 4c
    │                         │    (vm.py)        │
    │                         │  Stack-based VM   │
    │                         └──────────────────┘
    │                                    │
    ▼                                    ▼
┌──────────────────────────────────────────────┐
│                 Output / Result               │
└──────────────────────────────────────────────┘
```

## Module Breakdown

### Phase 1: Lexer (lexer.py + tokens.py)

**Purpose**: Converts raw source code into a stream of tokens.

**Key Classes**:
- `TokenType` (Enum) — 55+ token types covering all language constructs
- `Token` — Represents a single token with type, value, lexeme, line, and column
- `Lexer` — Character-by-character scanner

**Features**:
- Line and column tracking for precise error messages
- Integer literals: decimal, hex (0xFF), binary (0b1010), octal (0o77)
- Underscore separators in numbers (1_000_000)
- Float literals with scientific notation (2.5e10)
- String escape sequences (\n, \t, \r, \\, \", \0)
- Single-line (//) and multi-line (/* */) comments
- Nested multi-line comments

### Phase 2: Parser (parser.py + ast_nodes.py)

**Purpose**: Converts a token stream into an Abstract Syntax Tree (AST).

**Key Classes**:
- `Parser` — Recursive-descent parser with one token of lookahead
- 30+ AST node types covering all language constructs

**Parsing Strategy**: Recursive descent with precedence climbing (Pratt-like)
for expressions. Operator precedence is defined in a 15-level table.

**Supported Constructs**:
- Variable/constant declarations with type annotations
- Functions with parameters, default values, and return types
- Classes with fields, constructor, and methods
- If/elif/else conditionals
- While and for loops
- Try/catch/throw error handling
- Import/module system
- Arrays, maps, and ranges
- Member access, subscripts, function calls
- All standard operators (arithmetic, comparison, logical, bitwise)

### Phase 3: Semantic Analyzer (semantic.py + symbol_table.py)

**Purpose**: Validates the semantic correctness of the AST before execution.

**Key Classes**:
- `SymbolTable` — Manages scope hierarchy (global, function, block, class)
- `Symbol` — Represents a declared name with type and mutability info
- `SemanticAnalyzer` — AST visitor that performs validation

**Validations**:
- Undefined variable detection
- Duplicate declaration detection
- Constant reassignment prevention
- Type compatibility checking
- Function argument count validation
- Return type matching
- Break/continue inside loop validation
- `this` usage inside class validation

### Phase 4a: Interpreter (interpreter.py)

**Purpose**: Directly executes the AST without compilation.

**Key Classes**:
- `Environment` — Runtime variable storage with scope chaining
- `Interpreter` — AST visitor that evaluates nodes
- `SamratFunction` — User-defined function representation
- `SamratClass` / `SamratObject` — Class and instance representations
- `BoundMethod` — Method bound to an instance

**Features**:
- Tree-walking execution
- Closures and lexical scoping
- Recursion support
- Class instantiation with constructor
- Method dispatch with `this` binding
- Built-in functions (print, input, type, len, type conversions)
- Array methods (append, pop, insert, remove, sort, reverse, contains)
- Map methods (keys, values, contains)
- Standard library modules (math, string, time)

### Phase 4b: Compiler (compiler.py + bytecode.py)

**Purpose**: Compiles AST into bytecode for the virtual machine.

**Key Classes**:
- `Chunk` — A unit of bytecode with constants and line info
- `Compiler` — AST visitor that emits bytecode instructions

**Bytecode Design**:
- 55 instructions covering all operations
- Stack-based architecture (like JVM or CPython)
- Instructions are (OpCode, arg) tuples
- Constants stored in a pool, referenced by index
- Each function gets its own chunk

### Phase 4c: Optimizer (optimizer.py)

**Purpose**: Optimizes bytecode for better performance.

**Optimization Passes**:
1. Constant Folding — Pre-compute constant expressions at compile time
2. Dead Code Elimination — Remove unreachable code after return/throw/break
3. Peephole Optimization — Pattern matching on short instruction sequences
4. Strength Reduction — Replace expensive ops with cheaper equivalents

### Phase 4d: Virtual Machine (vm.py)

**Purpose**: Executes compiled bytecode.

**Key Classes**:
- `VM` — Stack-based execution engine with call frames

**Features**:
- Value stack for all operations
- Call frames for function calls
- Global variable dictionary
- Exception handling with try/catch
- Built-in function dispatch

## CLI Architecture (cli.py)

The CLI provides 14 commands:

| Command     | Description                              |
|-------------|------------------------------------------|
| `run`       | Execute a .sam file (interpreter)        |
| `build`     | Execute a .sam file (compiler + VM)      |
| `compile`   | Compile to bytecode and show disassembly |
| `repl`      | Start interactive REPL                   |
| `version`   | Show version information                 |
| `help`      | Show help message                        |
| `test`      | Run the test suite                       |
| `fmt`        | Format a Samrat file                     |
| `doctor`    | Check system setup                       |
| `new`       | Create a new Samrat project              |
| `init`      | Initialize Samrat in current directory   |
| `install`   | Install a package (future)               |
| `uninstall` | Uninstall a package (future)             |
| `update`    | Update Samrat (future)                   |

## File Extension

Samrat source files use `.sam` or `.samrat` extensions.

## Version Information

Current version: 1.0.0
License: MIT