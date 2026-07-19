# Changelog

## [1.0.0] — 2026-07-19

### Initial Release

Samrat v1.0.0 is the first stable release of the Samrat programming language.

#### Language Features
- Variables (`let`) and constants (`const`) with block scoping
- Primitive types: `int`, `float`, `str`, `bool`, `null`
- Composite types: arrays `[type]`, maps `{keyType: valueType}`
- Type inference with optional type annotations
- Functions with parameters, return types, default values, and recursion
- Control flow: `if`/`elif`/`else`, `while`, `for` over ranges and collections
- Classes with fields, constructor, methods, and `this`
- Error handling: `try`/`catch`/`throw`
- Module system: `import`/`from`/`as`
- Comments: `//` single-line, `/* */` nestable multi-line

#### Standard Library
- `math` module: `abs`, `sqrt`, `pow`, `floor`, `ceil`, `round`, `max`, `min`, `pi`, `e`
- `string` module: `upper`, `lower`, `trim`, `split`, `join`, `replace`
- `time` module: `now`, `sleep`
- Array methods: `append`, `pop`, `insert`, `remove`, `sort`, `reverse`, `contains`
- Map methods: `keys`, `values`, `contains`
- File I/O: `open`, `read`, `readline`, `write`, `close`
- Built-in functions: `print`, `input`, `int`, `float`, `str`, `bool`, `type`, `len`

#### Implementation
- Hand-written lexer with line/column tracking
- Recursive-descent parser with precedence climbing
- Semantic analyzer with type checking and scope management
- Tree-walking interpreter
- Bytecode compiler with stack-based virtual machine
- Interactive REPL with multi-line support
- Comprehensive test suite (300+ tests)
- Zero external dependencies — pure Python standard library

#### Documentation
- Full language specification (`LANGUAGE_SPEC.md`)
- Language reference (`LANGUAGE_REFERENCE.md`)
- Standard library reference (`STDLIB_REFERENCE.md`)
- Installation guide (`INSTALL.md`)
- Contributing guide (`CONTRIBUTING.md`)
- Future features roadmap (`future_features.md`)
- 18 example programs