# Contributing to Samrat

## Code of Conduct

Be respectful, inclusive, and constructive. We welcome contributors of all skill levels.

## How to Contribute

1. **Report bugs** — Open an issue with a minimal reproduction
2. **Suggest features** — Open an issue describing the feature and use case
3. **Submit code** — Fork the repo, make changes, submit a pull request

## Development Setup

```bash
git clone https://github.com/yourusername/samrat.git
cd samrat
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

No dependencies to install — Samrat uses only the Python standard library.

## Coding Standards

- **Python**: Follow PEP 8. Use 4-space indentation. Max line length: 100 characters.
- **Samrat**: Follow the language specification in `LANGUAGE_SPEC.md`.
- **Documentation**: All public functions and classes must have docstrings.
- **Type hints**: Use Python type hints for all function signatures.

## Testing Guidelines

- All new features must include tests.
- Run the full test suite before submitting:
  ```bash
  python tests/test_lexer.py
  python tests/test_parser.py
  python tests/test_semantic.py
  python tests/test_interpreter.py
  python tests/test_comprehensive.py
  ```
- Aim for high code coverage. Edge cases matter.
- Test both valid and invalid programs.

## Pull Request Process

1. Fork the repository and create a feature branch
2. Make your changes with clear commit messages
3. Add or update tests as needed
4. Run the full test suite to ensure nothing is broken
5. Submit the PR with a clear description of the changes

## Project Architecture

```
src/
├── tokens.py        # Token type definitions
├── errors.py        # Error handling classes
├── lexer.py         # Source code → tokens
├── ast_nodes.py     # AST node definitions
├── parser.py        # Tokens → AST
├── symbol_table.py  # Scope and symbol management
├── semantic.py      # Type checking and validation
├── interpreter.py   # AST execution (tree-walking)
├── bytecode.py      # Bytecode instruction set
├── compiler.py      # AST → bytecode
├── vm.py            # Bytecode execution
└── main.py          # Entry point
```

## Issue Reporting

Include:
- Samrat version
- Python version
- Operating system
- Minimal code that reproduces the issue
- Expected vs actual behavior