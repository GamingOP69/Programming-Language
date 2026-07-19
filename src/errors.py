"""
Samrat Programming Language — Error Handling

This module defines all custom error classes used throughout the Samrat
compiler pipeline. Each error type carries location information and
produces clear, descriptive messages that help developers quickly
understand and fix issues.
"""


class SamratError(Exception):
    """Base class for all Samrat errors."""

    def __init__(self, message: str, line: int = 0, column: int = 0):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(str(self))

    def __str__(self) -> str:
        if self.line > 0 and self.column > 0:
            return f"Error at {self.line}:{self.column}: {self.message}"
        elif self.line > 0:
            return f"Error at line {self.line}: {self.message}"
        else:
            return f"Error: {self.message}"


class LexerError(SamratError):
    """
    Error raised by the lexer when it encounters invalid characters
    or malformed tokens in the source code.

    Examples:
        - Unrecognized character (e.g., '@', '$', '?')
        - Unterminated string literal
        - Invalid number literal (e.g., multiple decimal points)
    """

    def __init__(self, message: str, line: int, column: int,
                 source_line: str = ""):
        self.source_line = source_line
        super().__init__(message, line, column)

    def __str__(self) -> str:
        result = f"LexerError at {self.line}:{self.column}: {self.message}"
        if self.source_line:
            # Show the source line with a caret pointing to the error
            pointer = " " * (self.column - 1) + "^"
            result += f"\n    {self.source_line}"
            result += f"\n    {pointer}"
        return result


class ParserError(SamratError):
    """
    Error raised by the parser when it encounters unexpected tokens
    or malformed syntax.

    Examples:
        - Missing closing parenthesis
        - Unexpected token in expression
        - Missing function body (block)
        - Expected ':' after parameter type annotation
    """

    def __init__(self, message: str, line: int, column: int,
                 found_token: str = ""):
        self.found_token = found_token
        detail = f"found '{found_token}'" if found_token else ""
        full_msg = f"{message}. {detail}" if detail else message
        super().__init__(full_msg, line, column)

    def __str__(self) -> str:
        result = f"SyntaxError at {self.line}:{self.column}: {self.message}"
        if self.found_token:
            result += f"\n    Got: '{self.found_token}'"
        return result


class SemanticError(SamratError):
    """
    Error raised by the semantic analyzer when it detects semantic issues.

    Examples:
        - Using an undefined variable
        - Type mismatch in assignment or function call
        - Reassigning a constant
        - Calling a non-function value
        - Duplicate variable/function/class declaration in same scope
    """

    def __init__(self, message: str, line: int, column: int):
        super().__init__(message, line, column)

    def __str__(self) -> str:
        return f"SemanticError at {self.line}:{self.column}: {self.message}"


class RuntimeError_(SamratError):
    """
    Error raised by the interpreter during program execution.

    Examples:
        - Division by zero
        - Index out of bounds
        - Calling a non-function value
        - Accessing a property on null
        - Type conversion failure
    """

    def __init__(self, message: str, line: int = 0, column: int = 0):
        super().__init__(message, line, column)

    def __str__(self) -> str:
        if self.line > 0 and self.column > 0:
            return f"RuntimeError at {self.line}:{self.column}: {self.message}"
        elif self.line > 0:
            return f"RuntimeError at line {self.line}: {self.message}"
        else:
            return f"RuntimeError: {self.message}"


class TypeError_(SamratError):
    """
    Error raised when there is a type mismatch.

    Examples:
        - Adding int and str
        - Passing str argument where int expected
        - Returning wrong type from function
    """

    def __init__(self, message: str, line: int = 0, column: int = 0):
        super().__init__(message, line, column)

    def __str__(self) -> str:
        return f"TypeError at {self.line}:{self.column}: {self.message}"


class IOError_(SamratError):
    """
    Error raised for file I/O operations.

    Examples:
        - File not found
        - Permission denied
        - Cannot write to read-only file
    """

    def __init__(self, message: str, line: int = 0, column: int = 0):
        super().__init__(message, line, column)

    def __str__(self) -> str:
        if self.line > 0:
            return f"IOError at {self.line}:{self.column}: {self.message}"
        return f"IOError: {self.message}"


def format_error_with_context(error: SamratError, source_lines: list) -> str:
    """
    Format an error with source context for more readable error messages.

    Args:
        error: The SamratError to format.
        source_lines: List of source code lines (0-indexed).

    Returns:
        A formatted error string with surrounding context and caret pointer.
    """
    result = str(error)

    if error.line > 0 and error.line <= len(source_lines):
        line_idx = error.line - 1
        # Show the problematic line
        result += "\n\n" + source_lines[line_idx].rstrip()

        # Show caret pointer if column is valid
        if error.column > 0:
            # Calculate column position (respect tabs)
            pointer_pos = error.column - 1
            # Build the pointer line
            if pointer_pos >= 0:
                # Handle tabs: count positions properly
                prefix = source_lines[line_idx][:pointer_pos]
                display_col = len(prefix.expandtabs())
                result += "\n" + " " * display_col + "^--- here"

        # Show a couple of lines of context
        if line_idx > 0:
            result = "\n" + source_lines[line_idx - 1].rstrip() + "\n" + result
        if line_idx + 1 < len(source_lines):
            result += "\n" + source_lines[line_idx + 1].rstrip()

    return result
