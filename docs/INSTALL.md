# Installing Samrat

## System Requirements

- **Python 3.8 or higher**
- **Operating System**: Windows 10/11, macOS 10.15+, or Linux
- **Disk Space**: ~5 MB
- **No external dependencies required**

## Installation

### From Source

1. **Clone or download the repository**

```bash
git clone https://github.com/yourusername/samrat.git
cd samrat
```

Or download and extract the ZIP file.

2. **Verify Python installation**

```bash
python --version
# Should output Python 3.8.x or higher
```

3. **Run the REPL**

```bash
python src/main.py
```

## Verifying Installation

Run the test suite to verify everything works:

```bash
python tests/test_lexer.py
python tests/test_parser.py
python tests/test_semantic.py
python tests/test_interpreter.py
```

All tests should pass with 0 failures.

## Running Samrat Programs

### Run a file

```bash
python src/main.py path/to/your/program.samrat
```

### Start the interactive REPL

```bash
python src/main.py
```

Type `exit()` or `quit()` to exit the REPL.

## Troubleshooting

### "Python is not recognized"
Make sure Python is in your PATH. Try `python3` instead of `python` on macOS/Linux.

### "Module not found"
Make sure you're running from the `samrat/` directory (the one containing `src/` and `tests/`).

### Encoding errors
Samrat source files should be saved as UTF-8. Most editors default to UTF-8.

### Permission denied (Linux/macOS)
```bash
chmod +x src/main.py