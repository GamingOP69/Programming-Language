"""
Samrat Programming Language — Professional Command-Line Interface

Provides a full-featured CLI for the Samrat language:
    samrat run <file>       Run a Samrat file
    samrat build <file>     Build (compile) a Samrat file
    samrat compile <file>   Compile to bytecode
    samrat repl             Start interactive REPL
    samrat version          Show version info
    samrat help             Show help
    samrat test             Run the test suite
    samrat fmt <file>       Format a Samrat file
    samrat doctor           Check system setup
    samrat new <name>       Create a new Samrat project
    samrat init             Initialize a Samrat project in current dir
    samrat install <pkg>    Install a package (future)
    samrat uninstall <pkg>  Uninstall a package (future)
    samrat update           Update Samrat (future)

Usage:
    python cli.py run hello.sam
    python cli.py repl
    python cli.py version
"""

import sys
import os
import time
import shutil
import argparse

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lexer import Lexer
from parser import Parser
from semantic import SemanticAnalyzer
from interpreter import Interpreter
from compiler import Compiler
from vm import VM
from errors import LexerError, ParserError, SemanticError, RuntimeError_

# ─── Constants ─────────────────────────────────────────────────────────────

VERSION = "1.0.0"
VERSION_NAME = "Samrat v1.0.0"
COPYRIGHT = "Copyright (c) 2026 GamingOP. MIT License."


# ─── Color Support ─────────────────────────────────────────────────────────

class Colors:
    """ANSI color codes for terminal output."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"

    @staticmethod
    def supports_color() -> bool:
        """Check if the terminal supports color output."""
        if not sys.stdout.isatty():
            return False
        if os.name == 'nt':
            # Windows 10+ supports ANSI in most terminals
            return True
        return 'TERM' in os.environ and os.environ['TERM'] != 'dumb'


# Only use colors if supported
USE_COLOR = Colors.supports_color()


def c(text: str, color: str) -> str:
    """Apply color to text if color is supported."""
    if USE_COLOR:
        return f"{color}{text}{Colors.RESET}"
    return text


# ─── Core Pipeline ─────────────────────────────────────────────────────────

def run_source(source: str, filename: str = "<stdin>", use_vm: bool = False) -> bool:
    """
    Run a Samrat source string through the full pipeline.

    Args:
        source: The Samrat source code.
        filename: The source filename (for error messages).
        use_vm: If True, use the bytecode compiler + VM instead of the interpreter.

    Returns:
        True if execution succeeded, False otherwise.
    """
    # Phase 1: Lexing
    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()
    except LexerError as e:
        print(c(f"LexerError: {e}", Colors.RED))
        return False

    # Phase 2: Parsing
    try:
        parser = Parser(tokens)
        ast = parser.parse()
    except ParserError as e:
        print(c(f"SyntaxError: {e}", Colors.RED))
        return False

    # Phase 3: Semantic Analysis
    analyzer = SemanticAnalyzer()
    if not analyzer.analyze(ast):
        for error in analyzer.get_errors():
            print(c(f"SemanticError: {error}", Colors.YELLOW))
        return False

    # Phase 4: Execution
    try:
        if use_vm:
            compiler = Compiler()
            chunk = compiler.compile(ast)
            vm = VM()
            # Register function chunks
            for name, func_chunk, param_count in compiler.function_chunks:
                vm._function_chunks[name] = (func_chunk, param_count)
            result = vm.run(chunk)
        else:
            interpreter = Interpreter()
            result = interpreter.interpret(ast)
        return True
    except RuntimeError_ as e:
        print(c(f"RuntimeError: {e}", Colors.RED))
        return False
    except Exception as e:
        print(c(f"Unexpected error: {e}", Colors.RED))
        return False


def run_file(path: str, use_vm: bool = False) -> bool:
    """
    Run a Samrat source file.

    Args:
        path: Path to the .samrat file.
        use_vm: If True, use the bytecode compiler + VM.

    Returns:
        True if execution succeeded, False otherwise.
    """
    if not os.path.exists(path):
        print(c(f"Error: File '{path}' not found", Colors.RED))
        return False

    with open(path, 'r', encoding='utf-8') as f:
        source = f.read()

    return run_source(source, path, use_vm)


# ─── REPL ──────────────────────────────────────────────────────────────────

def run_repl(use_vm: bool = False):
    """Run the Samrat REPL (Read-Eval-Print-Loop)."""
    banner = [
        c("=" * 50, Colors.CYAN),
        c(f"  {VERSION_NAME}", Colors.CYAN),
        c("  Type 'exit()' or 'quit()' to exit", Colors.CYAN),
        c("  Type 'help' for commands", Colors.CYAN),
        c("=" * 50, Colors.CYAN),
        "",
    ]
    for line in banner:
        print(line)

    # Track accumulated input for multi-line statements
    buffer = ""
    brace_count = 0
    paren_count = 0
    bracket_count = 0

    while True:
        # Show prompt
        if buffer:
            prompt = c("... ", Colors.DIM)
        else:
            prompt = c(">>> ", Colors.GREEN)

        try:
            line = input(prompt)
        except (EOFError, KeyboardInterrupt):
            print()
            break

        line = line.rstrip()

        if line.strip() == 'exit()' or line.strip() == 'quit()':
            break

        if line.strip() == 'help':
            _print_repl_help()
            continue

        if line.strip() == 'version':
            print(f"{VERSION_NAME} ({COPYRIGHT})")
            continue

        # Add to buffer
        buffer += line + "\n"

        # Track braces, parens, brackets
        for ch in line:
            if ch == '{':
                brace_count += 1
            elif ch == '}':
                brace_count -= 1
            elif ch == '(':
                paren_count += 1
            elif ch == ')':
                paren_count -= 1
            elif ch == '[':
                bracket_count += 1
            elif ch == ']':
                bracket_count -= 1

        # If we have balanced braces and non-empty buffer, execute
        if brace_count <= 0 and paren_count <= 0 and bracket_count <= 0 and buffer.strip():
            try:
                lexer = Lexer(buffer)
                tokens = lexer.tokenize()
                parser = Parser(tokens)
                ast = parser.parse()
                analyzer = SemanticAnalyzer()

                if analyzer.analyze(ast):
                    if use_vm:
                        compiler = Compiler()
                        chunk = compiler.compile(ast)
                        vm = VM()
                        for name, func_chunk, param_count in compiler.function_chunks:
                            vm._function_chunks[name] = (func_chunk, param_count)
                        result = vm.run(chunk)
                    else:
                        interpreter = Interpreter()
                        result = interpreter.interpret(ast)
                    if result is not None:
                        print(c(interpreter._stringify(result) if not use_vm else vm._stringify(result), Colors.GREEN))
                else:
                    for error in analyzer.get_errors():
                        print(c(f"SemanticError: {error}", Colors.YELLOW))
            except LexerError as e:
                print(c(f"LexerError: {e}", Colors.RED))
            except ParserError as e:
                print(c(f"SyntaxError: {e}", Colors.RED))
            except RuntimeError_ as e:
                print(c(f"RuntimeError: {e}", Colors.RED))
            except Exception as e:
                print(c(f"Error: {e}", Colors.RED))

            # Reset buffer
            buffer = ""
            brace_count = 0
            paren_count = 0
            bracket_count = 0


def _print_repl_help():
    """Print REPL help text."""
    help_text = [
        c("Samrat REPL Commands:", Colors.BOLD),
        "  exit() / quit()    Exit the REPL",
        "  help               Show this help message",
        "  version            Show version information",
        "",
        c("Language Features:", Colors.BOLD),
        "  let x = 5          Variable declaration",
        "  const PI = 3.14    Constant declaration",
        "  func f() { }       Function definition",
        "  class C { }        Class definition",
        "  if/elif/else       Conditional statements",
        "  while/for          Loops",
        "  try/catch/throw    Error handling",
        "  import             Module imports",
        "",
        c("Examples:", Colors.BOLD),
        '  >>> print("Hello, World!")',
        "  >>> let x = 5 + 3",
        "  >>> func add(a, b) { return a + b }",
    ]
    for line in help_text:
        print(line)


# ─── CLI Commands ──────────────────────────────────────────────────────────

def cmd_run(args):
    """Run a Samrat file."""
    if not args.file:
        print(c("Error: No file specified. Usage: samrat run <file>", Colors.RED))
        return 1
    success = run_file(args.file, use_vm=args.vm)
    return 0 if success else 1


def cmd_build(args):
    """Build (compile) a Samrat file using the VM."""
    if not args.file:
        print(c("Error: No file specified. Usage: samrat build <file>", Colors.RED))
        return 1
    print(c(f"Building {args.file}...", Colors.BLUE))
    start = time.time()
    success = run_file(args.file, use_vm=True)
    elapsed = time.time() - start
    if success:
        print(c(f"Build successful ({elapsed:.3f}s)", Colors.GREEN))
    return 0 if success else 1


def cmd_compile(args):
    """Compile a Samrat file to bytecode and display disassembly."""
    if not args.file:
        print(c("Error: No file specified. Usage: samrat compile <file>", Colors.RED))
        return 1

    if not os.path.exists(args.file):
        print(c(f"Error: File '{args.file}' not found", Colors.RED))
        return 1

    with open(args.file, 'r', encoding='utf-8') as f:
        source = f.read()

    # Lex
    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()
    except LexerError as e:
        print(c(f"LexerError: {e}", Colors.RED))
        return 1

    # Parse
    try:
        parser = Parser(tokens)
        ast = parser.parse()
    except ParserError as e:
        print(c(f"SyntaxError: {e}", Colors.RED))
        return 1

    # Semantic analysis
    analyzer = SemanticAnalyzer()
    if not analyzer.analyze(ast):
        for error in analyzer.get_errors():
            print(c(f"SemanticError: {error}", Colors.YELLOW))
        return 1

    # Compile
    compiler = Compiler()
    chunk = compiler.compile(ast)

    # Display disassembly
    print(c(f"\nBytecode for '{args.file}':", Colors.BOLD))
    print(c("-" * 60, Colors.DIM))
    _disassemble_chunk(chunk)

    if compiler.function_chunks:
        for name, func_chunk, param_count in compiler.function_chunks:
            print(c(f"\nFunction '{name}' ({param_count} params):", Colors.BOLD))
            print(c("-" * 60, Colors.DIM))
            _disassemble_chunk(func_chunk)

    print(c(f"\nTotal: {len(chunk.code)} instructions, {len(chunk.constants)} constants", Colors.DIM))
    return 0


def _disassemble_chunk(chunk):
    """Print a disassembly of a bytecode chunk."""
    from bytecode import OpCode
    opcode_names = {op: op.name for op in OpCode}

    for i, (opcode, arg) in enumerate(chunk.code):
        line_info = f"{chunk.lines[i]:4d}" if i < len(chunk.lines) else "    "
        name = opcode_names.get(opcode, f"UNKNOWN({opcode.value})")
        if arg is not None:
            if opcode in (OpCode.PUSH_INT, OpCode.PUSH_FLOAT, OpCode.PUSH_STRING,
                          OpCode.LOAD_GLOBAL, OpCode.STORE_GLOBAL,
                          OpCode.GET_ATTR, OpCode.SET_ATTR,
                          OpCode.MAKE_FUNCTION, OpCode.MAKE_CLASS):
                const_val = chunk.constants[arg] if arg < len(chunk.constants) else "?"
                print(f"  {i:4d}  {line_info}  {name:20s}  ({arg})  ; {const_val!r}")
            else:
                print(f"  {i:4d}  {line_info}  {name:20s}  ({arg})")
        else:
            print(f"  {i:4d}  {line_info}  {name}")


def cmd_repl(args):
    """Start the interactive REPL."""
    run_repl(use_vm=args.vm)
    return 0


def cmd_version(args):
    """Show version information."""
    print(f"{VERSION_NAME}")
    print(f"{COPYRIGHT}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Platform: {sys.platform}")
    return 0


def cmd_help(args):
    """Show help information."""
    print(c(f"{VERSION_NAME}", Colors.BOLD))
    print(c("=" * 60, Colors.DIM))
    print()
    print(c("Usage:", Colors.BOLD))
    print("  samrat <command> [options]")
    print()
    print(c("Commands:", Colors.BOLD))
    print("  run <file>         Run a Samrat file (interpreter)")
    print("  build <file>       Build and run a Samrat file (VM)")
    print("  compile <file>     Compile to bytecode and show disassembly")
    print("  repl               Start interactive REPL")
    print("  version            Show version information")
    print("  help               Show this help message")
    print("  test               Run the test suite")
    print("  fmt <file>         Format a Samrat file")
    print("  doctor             Check system setup")
    print("  new <name>         Create a new Samrat project")
    print("  init               Initialize Samrat in current directory")
    print("  install <pkg>      Install a package (future)")
    print("  uninstall <pkg>    Uninstall a package (future)")
    print("  update             Update Samrat (future)")
    print()
    print(c("Options:", Colors.BOLD))
    print("  --vm               Use bytecode VM instead of interpreter")
    print("  --version          Show version and exit")
    print()
    print(c("Examples:", Colors.BOLD))
    print("  samrat run hello.sam")
    print("  samrat build hello.sam")
    print("  samrat compile hello.sam")
    print("  samrat repl")
    print("  samrat new my_project")
    print("  samrat fmt hello.sam")
    print()
    print(c("Documentation:", Colors.BOLD))
    print("  See docs/ directory for full documentation")
    print("  https://github.com/GamingOP69/Programming-Language")
    return 0


def cmd_test(args):
    """Run the test suite."""
    test_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tests')
    if not os.path.exists(test_dir):
        print(c("Error: Test directory not found", Colors.RED))
        return 1

    print(c("Running Samrat test suite...", Colors.BLUE))
    print()

    # Run comprehensive tests
    sys.path.insert(0, test_dir)
    try:
        from test_comprehensive import run_all
        success = run_all()
        return 0 if success else 1
    except ImportError as e:
        print(c(f"Error importing tests: {e}", Colors.RED))
        return 1


def cmd_fmt(args):
    """Format a Samrat file (basic formatting)."""
    if not args.file:
        print(c("Error: No file specified. Usage: samrat fmt <file>", Colors.RED))
        return 1

    if not os.path.exists(args.file):
        print(c(f"Error: File '{args.file}' not found", Colors.RED))
        return 1

    with open(args.file, 'r', encoding='utf-8') as f:
        source = f.read()

    # Parse to validate
    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
    except (LexerError, ParserError) as e:
        print(c(f"Error: Cannot format file with syntax errors: {e}", Colors.RED))
        return 1

    # Basic formatting: normalize whitespace, ensure consistent indentation
    formatted = _format_source(source)

    # Write back
    with open(args.file, 'w', encoding='utf-8') as f:
        f.write(formatted)

    print(c(f"Formatted {args.file}", Colors.GREEN))
    return 0


def _format_source(source: str) -> str:
    """
    Basic source code formatter for Samrat.

    Normalizes whitespace, ensures consistent indentation (2 spaces),
    and adds newlines after certain tokens.
    """
    lines = source.split('\n')
    formatted = []
    indent_level = 0
    indent_size = 2

    for line in lines:
        stripped = line.strip()
        if not stripped:
            formatted.append('')
            continue

        # Skip comments
        if stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*'):
            formatted.append(line)
            continue

        # Decrease indent for closing braces
        if stripped.startswith('}') or stripped.startswith('])'):
            indent_level = max(0, indent_level - 1)

        # Apply indentation
        indent = ' ' * (indent_level * indent_size)
        formatted_line = indent + stripped

        # Increase indent after opening braces
        for ch in stripped:
            if ch == '{':
                indent_level += 1
            elif ch == '[':
                indent_level += 1

        # Decrease indent for closing braces at end
        if stripped.endswith('}') or stripped.endswith(']'):
            indent_level = max(0, indent_level - 1)

        formatted.append(formatted_line)

    return '\n'.join(formatted)


def cmd_doctor(args):
    """Check system setup for Samrat."""
    print(c("Samrat Doctor", Colors.BOLD))
    print(c("=" * 40, Colors.DIM))
    print()

    checks = []

    # Python version
    py_version = sys.version_info
    checks.append((
        "Python version",
        py_version >= (3, 8),
        f"{py_version.major}.{py_version.minor}.{py_version.micro}",
        "3.8+ required"
    ))

    # Source files
    src_dir = os.path.dirname(os.path.abspath(__file__))
    required_files = ['lexer.py', 'parser.py', 'semantic.py', 'interpreter.py',
                      'compiler.py', 'vm.py', 'bytecode.py', 'tokens.py', 'errors.py']
    missing = [f for f in required_files if not os.path.exists(os.path.join(src_dir, f))]
    checks.append((
        "Source files",
        len(missing) == 0,
        f"{len(required_files) - len(missing)}/{len(required_files)} present",
        f"Missing: {', '.join(missing)}" if missing else "OK"
    ))

    # Test files
    test_dir = os.path.join(os.path.dirname(src_dir), 'tests')
    test_files = ['test_comprehensive.py', 'test_compiler.py', 'test_lexer.py',
                  'test_parser.py', 'test_semantic.py', 'test_interpreter.py']
    test_missing = [f for f in test_files if not os.path.exists(os.path.join(test_dir, f))]
    checks.append((
        "Test files",
        len(test_missing) == 0,
        f"{len(test_files) - len(test_missing)}/{len(test_files)} present",
        f"Missing: {', '.join(test_missing)}" if test_missing else "OK"
    ))

    # Example files
    examples_dir = os.path.join(os.path.dirname(src_dir), 'examples')
    if os.path.exists(examples_dir):
        example_count = len([f for f in os.listdir(examples_dir) if f.endswith('.samrat')])
        checks.append((
            "Example programs",
            example_count > 0,
            f"{example_count} examples",
            "OK"
        ))
    else:
        checks.append(("Example programs", False, "0", "Missing examples/ directory"))

    # Print results
    all_pass = True
    for name, passed, detail, message in checks:
        status = c("✓", Colors.GREEN) if passed else c("✗", Colors.RED)
        print(f"  {status} {name}: {detail}")
        if not passed:
            print(f"       {c(message, Colors.YELLOW)}")
            all_pass = False

    print()
    if all_pass:
        print(c("  All checks passed! Samrat is ready to use.", Colors.GREEN))
    else:
        print(c("  Some checks failed. See above for details.", Colors.YELLOW))

    return 0 if all_pass else 1


def cmd_new(args):
    """Create a new Samrat project."""
    if not args.name:
        print(c("Error: No project name specified. Usage: samrat new <name>", Colors.RED))
        return 1

    project_dir = os.path.join(os.getcwd(), args.name)
    if os.path.exists(project_dir):
        print(c(f"Error: Directory '{args.name}' already exists", Colors.RED))
        return 1

    os.makedirs(project_dir)
    os.makedirs(os.path.join(project_dir, 'src'))
    os.makedirs(os.path.join(project_dir, 'examples'))
    os.makedirs(os.path.join(project_dir, 'tests'))

    # Create main.samrat
    with open(os.path.join(project_dir, 'main.sam'), 'w', encoding='utf-8') as f:
        f.write('// Samrat Programming Language\n')
        f.write(f'// Project: {args.name}\n')
        f.write('// Created with samrat new\n\n')
        f.write('func main() {\n')
        f.write('  print("Hello from Samrat!")\n')
        f.write('}\n\n')
        f.write('main()\n')

    # Create README
    with open(os.path.join(project_dir, 'README.md'), 'w', encoding='utf-8') as f:
        f.write(f'# {args.name}\n\n')
        f.write('A Samrat programming language project.\n\n')
        f.write('## Usage\n\n')
        f.write('```bash\n')
        f.write('samrat run main.sam\n')
        f.write('```\n')

    print(c(f"Created new Samrat project in '{args.name}/'", Colors.GREEN))
    print(f"  {args.name}/")
    print(f"  {args.name}/main.sam")
    print(f"  {args.name}/src/")
    print(f"  {args.name}/examples/")
    print(f"  {args.name}/tests/")
    print(f"  {args.name}/README.md")
    return 0


def cmd_init(args):
    """Initialize a Samrat project in the current directory."""
    project_dir = os.getcwd()
    project_name = os.path.basename(project_dir)

    # Create directories if they don't exist
    for d in ['src', 'examples', 'tests']:
        d_path = os.path.join(project_dir, d)
        if not os.path.exists(d_path):
            os.makedirs(d_path)

    # Create main.sam if it doesn't exist
    main_path = os.path.join(project_dir, 'main.sam')
    if not os.path.exists(main_path):
        with open(main_path, 'w', encoding='utf-8') as f:
            f.write('// Samrat Programming Language\n')
            f.write(f'// Project: {project_name}\n\n')
            f.write('print("Hello from Samrat!")\n')

    print(c(f"Initialized Samrat project in '{project_dir}'", Colors.GREEN))
    return 0


def cmd_install(args):
    """Install a package (future feature)."""
    print(c("Package management is not yet implemented.", Colors.YELLOW))
    print("This feature is planned for a future release.")
    return 0


def cmd_uninstall(args):
    """Uninstall a package (future feature)."""
    print(c("Package management is not yet implemented.", Colors.YELLOW))
    print("This feature is planned for a future release.")
    return 0


def cmd_update(args):
    """Update Samrat (future feature)."""
    print(c("Auto-update is not yet implemented.", Colors.YELLOW))
    print("This feature is planned for a future release.")
    return 0


# ─── Main Entry Point ──────────────────────────────────────────────────────

def main():
    """Main CLI entry point."""
    args_list = sys.argv[1:] if len(sys.argv) > 1 else []

    # Handle --version
    if '--version' in args_list:
        cmd_version(None)
        return 0

    # Handle -h / --help
    if '-h' in args_list or '--help' in args_list or not args_list:
        cmd_help(None)
        return 0

    # Extract --vm flag
    use_vm = '--vm' in args_list
    args_list = [a for a in args_list if a != '--vm']

    # First argument is the command, rest are positional args
    command = args_list[0] if args_list else None
    positional = args_list[1:] if len(args_list) > 1 else []

    class Args:
        pass

    args = Args()
    args.vm = use_vm
    args.file = None
    args.name = None

    # Parse positional args based on command
    if len(positional) > 0:
        args.file = positional[0]
        args.name = positional[1] if len(positional) > 1 else None

    # Handle the case where command is a file (backward compat: python main.py file.sam)
    if command and command not in (
        'run', 'build', 'compile', 'repl', 'version', 'help',
        'test', 'fmt', 'doctor', 'new', 'init',
        'install', 'uninstall', 'update'
    ) and not command.startswith('-'):
        # Treat as file to run (backward compatibility)
        args.file = command
        return cmd_run(args)

    # Dispatch commands
    commands = {
        'run': cmd_run,
        'build': cmd_build,
        'compile': cmd_compile,
        'repl': cmd_repl,
        'version': cmd_version,
        'help': cmd_help,
        'test': cmd_test,
        'fmt': cmd_fmt,
        'doctor': cmd_doctor,
        'new': cmd_new,
        'init': cmd_init,
        'install': cmd_install,
        'uninstall': cmd_uninstall,
        'update': cmd_update,
    }

    if command in commands:
        return commands[command](args)
    else:
        print(c(f"Unknown command: '{command}'", Colors.RED))
        print("Use 'samrat help' for available commands.")
        return 1


if __name__ == "__main__":
    sys.exit(main())