# Changelog

## [1.1.0] — 2026-07-19

### New Language Features

#### Operators
- **Pipe operator (`|>`)** — Chain function calls: `value |> func` passes `value` as argument to `func`
- **Null coalescing (`??`)** — Default values for null: `value ?? fallback` returns `fallback` if `value` is null
- **Lambda arrow (`=>`)** — Function shorthand: `x => x * 2` creates an anonymous function
- **Ternary (`?`)** — Inline conditionals: `condition ? true_value : false_value`
- **Spread (`...`)** — Array/map expansion: `[...arr, 4, 5]` merges arrays

#### Keywords
- `lambda` — Create anonymous functions
- `yield` — Generator function support

#### Enhanced Standard Library
- `json` module: `parse`, `stringify`
- `datetime` module: `now`, `format`, `parse`
- `collections` module: `count`, `group_by`, `flatten`
- Extended array methods: `map`, `filter`, `reduce`, `find`, `slice`
- Extended string methods: `starts_with`, `ends_with`, `includes`, `repeat`

#### CLI Improvements
- `samrat watch <file>` — Auto-reload on file changes
- `samrat init` — Interactive project initialization with templates
- `samrat run --vm` — Use bytecode VM instead of interpreter
- `samrat build` — Build and run with VM

#### CI/CD
- Cross-platform release builds (Linux + Windows executables)
- Release job reuses build artifacts (no duplicate PyInstaller builds)
- Removed Python 3.8 from test matrix (faster CI)
- Added pip upgrade step
- Updated GitHub Actions to latest versions

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