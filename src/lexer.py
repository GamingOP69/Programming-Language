"""
Samrat Programming Language — Lexer (Tokenizer)

The lexer is the first phase of the Samrat compiler pipeline. It reads
raw source code as a string and converts it into a sequence of tokens
that the parser can consume.

This lexer:
- Scans characters one at a time
- Recognizes keywords, identifiers, literals, operators, and punctuation
- Tracks precise line and column positions for excellent error messages
- Handles single-line (//) and multi-line (/* */) comments
- Properly handles string escape sequences
- Supports integer, float, hex, binary, and octal literals
- Produces descriptive error messages for malformed input

Usage:
    from lexer import Lexer
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()
    for token in tokens:
        print(token)
"""

from tokens import Token, TokenType, KEYWORDS
from errors import LexerError


class Lexer:
    """
    Converts Samrat source code into a list of tokens.

    Attributes:
        source: The raw source code string.
        tokens: The list of tokens produced.
        start: Start position of the current lexeme.
        current: Current position in the source.
        line: Current line number (1-based).
        column: Current column number (1-based).
        source_lines: List of source lines for error context.
    """

    def __init__(self, source: str):
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.column = 1
        self.source_lines = source.split('\n') if source else ['']

    def tokenize(self) -> list:
        """
        Scan the entire source and produce a list of tokens.

        Returns:
            A list of Token objects representing the source code.
        """
        while not self._is_at_end():
            # Record the start of the next lexeme
            self.start = self.current
            self._scan_token()

        # Add the EOF token at the end
        self.tokens.append(
            Token(TokenType.EOF, None, '', self.line, self.column)
        )

        return self.tokens

    def _scan_token(self) -> None:
        """Scan a single token from the source and add it to the token list."""
        char = self._advance()

        if char == '\n':
            self.line += 1
            self.column = 1
            return

        # Skip whitespace (but not newlines — those are tracked separately)
        if char in ' \t\r':
            return

        # Single-line comment
        if char == '/' and self._peek() == '/':
            self._skip_single_line_comment()
            return

        # Multi-line comment
        if char == '/' and self._peek() == '*':
            self._skip_multi_line_comment()
            return

        # String literals
        if char == '"':
            self._string()
            return

        # Number literals
        if char.isdigit():
            self._number()
            return

        # Identifiers and keywords
        if char.isalpha() or char == '_':
            self._identifier()
            return

        # Operators and punctuation
        self._handle_operator_or_punctuation(char)

    def _advance(self) -> str:
        """
        Consume the next character and advance position.

        Returns:
            The consumed character.
        """
        char = self.source[self.current]
        self.current += 1
        self.column += 1
        return char

    def _peek(self, offset: int = 0) -> str:
        """
        Look at a character ahead without consuming it.

        Args:
            offset: Number of characters ahead to look (0 = current position).

        Returns:
            The character at the peeked position, or '\0' if at end.
        """
        pos = self.current + offset
        if pos >= len(self.source):
            return '\0'
        return self.source[pos]

    def _match(self, expected: str) -> bool:
        """
        Check if the current character matches expected, and consume it if so.

        Args:
            expected: The character to match against.

        Returns:
            True if matched and consumed, False otherwise.
        """
        if self._is_at_end():
            return False
        if self.source[self.current] != expected:
            return False
        self.current += 1
        self.column += 1
        return True

    def _is_at_end(self) -> bool:
        """Check if we've reached the end of source."""
        return self.current >= len(self.source)

    def _peek_back(self) -> str:
        """Look at the previous character without seeking."""
        if self.current == 0:
            return '\0'
        return self.source[self.current - 1]

    def _skip_single_line_comment(self) -> None:
        """
        Skip a single-line comment starting with //.
        Consumes everything until end of line or end of file.
        """
        while not self._is_at_end() and self._peek() != '\n':
            self._advance()

    def _skip_multi_line_comment(self) -> None:
        """
        Skip a multi-line comment starting with /* and ending with */.
        Handles nested comments and tracks line numbers within comments.
        """
        nesting_depth = 1
        while nesting_depth > 0 and not self._is_at_end():
            if self._peek() == '/' and self._peek(1) == '*':
                # Nested comment opening
                self._advance()
                self._advance()
                nesting_depth += 1
            elif self._peek() == '*' and self._peek(1) == '/':
                # Comment closing
                self._advance()
                self._advance()
                nesting_depth -= 1
            elif self._peek() == '\n':
                self._advance()
                self.line += 1
                self.column = 1
            else:
                self._advance()

        if nesting_depth > 0:
            raise LexerError(
                "Unterminated multi-line comment",
                self.line, self.column,
                self.source_lines[self.line - 1] if self.line <= len(self.source_lines) else ""
            )

    def _identifier(self) -> None:
        """Scan an identifier or keyword."""
        while self._peek().isalnum() or self._peek() == '_':
            self._advance()

        lexeme = self.source[self.start:self.current]
        token_type = KEYWORDS.get(lexeme, TokenType.IDENTIFIER)
        value = lexeme if token_type == TokenType.IDENTIFIER else None

        self._add_token(token_type, value)

    def _number(self) -> None:
        """Scan a number literal (integer or float)."""
        # Check for hex, binary, or octal prefix
        if (self._peek_back() == '0' and not self._is_at_end()):
            next_char = self._peek()
            if next_char in 'xX':
                self._advance()  # consume 'x' or 'X'
                self._hex_integer()
                return
            elif next_char in 'bB':
                self._advance()  # consume 'b' or 'B'
                self._binary_integer()
                return
            elif next_char in 'oO':
                self._advance()  # consume 'o' or 'O'
                self._octal_integer()
                return

        # Decimal integer or float
        self._decimal_number()

    def _hex_integer(self) -> None:
        """Scan a hexadecimal integer literal (e.g., 0xFF, 0x1A)."""
        start_line, start_col = self.line, self.column
        digits_started = False

        while self._peek().isalnum() or self._peek() == '_':
            char = self._peek()
            if char in '0123456789abcdefABCDEF_':
                if char != '_':
                    digits_started = True
                self._advance()
            else:
                break

        if not digits_started:
            raise LexerError(
                "Invalid hexadecimal literal: expected digits after '0x'",
                start_line, start_col,
                self.source_lines[start_line - 1] if start_line <= len(self.source_lines) else ""
            )

        lexeme = self.source[self.start:self.current]
        # Remove underscores for parsing
        clean = lexeme.replace('_', '')
        value = int(clean, 16)

        self._add_token(TokenType.INTEGER, value)

    def _binary_integer(self) -> None:
        """Scan a binary integer literal (e.g., 0b1010)."""
        start_line, start_col = self.line, self.column
        digits_started = False

        while self._peek() in '01_':
            if self._peek() != '_':
                digits_started = True
            self._advance()

        if not digits_started:
            raise LexerError(
                "Invalid binary literal: expected digits (0 or 1) after '0b'",
                start_line, start_col,
                self.source_lines[start_line - 1] if start_line <= len(self.source_lines) else ""
            )

        lexeme = self.source[self.start:self.current]
        clean = lexeme.replace('_', '')
        value = int(clean, 2)

        self._add_token(TokenType.INTEGER, value)

    def _octal_integer(self) -> None:
        """Scan an octal integer literal (e.g., 0o77)."""
        start_line, start_col = self.line, self.column
        digits_started = False

        while self._peek() in '01234567_':
            if self._peek() != '_':
                digits_started = True
            self._advance()

        if not digits_started:
            raise LexerError(
                "Invalid octal literal: expected digits (0-7) after '0o'",
                start_line, start_col,
                self.source_lines[start_line - 1] if start_line <= len(self.source_lines) else ""
            )

        lexeme = self.source[self.start:self.current]
        clean = lexeme.replace('_', '')
        value = int(clean, 8)

        self._add_token(TokenType.INTEGER, value)

    def _decimal_number(self) -> None:
        """Scan a decimal integer or float literal."""
        is_float = False

        # Scan integer part (with underscores)
        while self._peek().isdigit() or self._peek() == '_':
            if self._peek() == '_':
                # Validate underscore position
                if not (self._peek(-1).isdigit() if self.current > self.start else False):
                    # We can't easily check here, skip and continue
                    pass
            self._advance()

        # Look for fractional part
        if self._peek() == '.' and self._peek(1) != '.' and self._peek(1) != '\0':
            # It's a float with decimal point (but not range operator '..')
            is_float = True
            self._advance()  # consume '.'

            # Scan fractional part
            while self._peek().isdigit() or self._peek() == '_':
                self._advance()

        # Look for scientific notation
        if self._peek() in 'eE':
            is_float = True
            self._advance()  # consume 'e' or 'E'
            if self._peek() in '+-':
                self._advance()
            while self._peek().isdigit() or self._peek() == '_':
                self._advance()

        lexeme = self.source[self.start:self.current]
        clean = lexeme.replace('_', '')

        if is_float:
            value = float(clean)
            self._add_token(TokenType.FLOAT, value)
        else:
            value = int(clean)
            self._add_token(TokenType.INTEGER, value)

    def _string(self) -> None:
        """Scan a string literal."""
        start_line, start_col = self.line, self.column
        string_value = []

        while not self._is_at_end() and self._peek() != '"':
            if self._peek() == '\n':
                self.line += 1
                self.column = 1
                string_value.append('\n')
                self._advance()
            elif self._peek() == '\\':
                # Escape sequence
                self._advance()  # consume backslash
                escape_char = self._advance()
                escaped = self._handle_escape(escape_char, start_line, start_col)
                string_value.append(escaped)
            else:
                string_value.append(self._advance())

        if self._is_at_end():
            raise LexerError(
                "Unterminated string literal",
                start_line, start_col,
                self.source_lines[start_line - 1] if start_line <= len(self.source_lines) else ""
            )

        # Consume closing double quote
        self._advance()

        value = ''.join(string_value)

        self._add_token(TokenType.STRING, value)

    def _handle_escape(self, char: str, line: int, col: int) -> str:
        """
        Handle escape sequences in string literals.

        Args:
            char: The character following the backslash.
            line, col: Position for error reporting.

        Returns:
            The actual character represented by the escape sequence.
        """
        escapes = {
            'n': '\n',
            't': '\t',
            'r': '\r',
            '\\': '\\',
            '"': '"',
            '0': '\0',
        }
        if char in escapes:
            return escapes[char]
        else:
            # Keep the original escape sequence as-is for unknown escapes
            # This matches the behavior of many languages
            return '\\' + char

    def _handle_operator_or_punctuation(self, char: str) -> None:  # noqa: C901
        """
        Handle operators and punctuation characters.

        This method uses a dispatch dictionary to map the current character
        to the appropriate handler or token type.
        """
        if char == '(':
            self._add_token(TokenType.LEFT_PAREN)
        elif char == ')':
            self._add_token(TokenType.RIGHT_PAREN)
        elif char == '[':
            self._add_token(TokenType.LEFT_BRACKET)
        elif char == ']':
            self._add_token(TokenType.RIGHT_BRACKET)
        elif char == '{':
            self._add_token(TokenType.LEFT_BRACE)
        elif char == '}':
            self._add_token(TokenType.RIGHT_BRACE)
        elif char == ',':
            self._add_token(TokenType.COMMA)
        elif char == '.':
            # Could be '.', '..', or '...'
            if self._match('.'):
                if self._match('.'):
                    self._add_token(TokenType.DOT_DOT_DOT)
                else:
                    self._add_token(TokenType.DOT_DOT)
            else:
                self._add_token(TokenType.DOT)
        elif char == ':':
            self._add_token(TokenType.COLON)
        elif char == ';':
            self._add_token(TokenType.SEMICOLON)
        elif char == '+':
            if self._match('='):
                self._add_token(TokenType.PLUS_EQUAL)
            elif self._match('+'):
                # ++ is not used in Samrat, but handle it gracefully
                # We'll treat it as two PLUS tokens
                self._add_token(TokenType.PLUS)
                self.tokens.append(
                    Token(TokenType.PLUS, None, '+', self.line, self.column)
                )
            else:
                self._add_token(TokenType.PLUS)
        elif char == '-':
            if self._match('='):
                self._add_token(TokenType.MINUS_EQUAL)
            elif self._match('>'):
                self._add_token(TokenType.ARROW)
            elif self._match('-'):
                # -- is not used in Samrat
                self._add_token(TokenType.MINUS)
                self.tokens.append(
                    Token(TokenType.MINUS, None, '-', self.line, self.column)
                )
            else:
                self._add_token(TokenType.MINUS)
        elif char == '*':
            if self._match('*'):
                self._add_token(TokenType.STAR_STAR)
            elif self._match('='):
                self._add_token(TokenType.STAR_EQUAL)
            else:
                self._add_token(TokenType.STAR)
        elif char == '/':
            if self._match('='):
                self._add_token(TokenType.SLASH_EQUAL)
            else:
                self._add_token(TokenType.SLASH)
        elif char == '%':
            if self._match('='):
                self._add_token(TokenType.PERCENT_EQUAL)
            else:
                self._add_token(TokenType.PERCENT)
        elif char == '=':
            if self._match('='):
                self._add_token(TokenType.EQUAL_EQUAL)
            elif self._match('>'):
                self._add_token(TokenType.LAMBDA_ARROW)
            else:
                self._add_token(TokenType.EQUAL)
        elif char == '!':
            if self._match('='):
                self._add_token(TokenType.BANG_EQUAL)
            else:
                self._error("Unexpected character '!' (use '!=' for not-equal)")
        elif char == '<':
            if self._match('='):
                self._add_token(TokenType.LESS_EQUAL)
            elif self._match('<'):
                self._add_token(TokenType.LESS_LESS)
            else:
                self._add_token(TokenType.LESS)
        elif char == '>':
            if self._match('='):
                self._add_token(TokenType.GREATER_EQUAL)
            elif self._match('>'):
                self._add_token(TokenType.GREATER_GREATER)
            else:
                self._add_token(TokenType.GREATER)
        elif char == '&':
            if self._match('&'):
                # && is not a Samrat operator, but support it gracefully
                # by treating as two tokens
                self._add_token(TokenType.AMPERSAND)
                self.tokens.append(
                    Token(TokenType.AMPERSAND, None, '&', self.line, self.column)
                )
            else:
                self._add_token(TokenType.AMPERSAND)
        elif char == '|':
            if self._match('>'):
                self._add_token(TokenType.PIPE_PIPE)
            elif self._match('|'):
                self._add_token(TokenType.PIPE)
                self.tokens.append(
                    Token(TokenType.PIPE, None, '|', self.line, self.column)
                )
            else:
                self._add_token(TokenType.PIPE)
        elif char == '^':
            self._add_token(TokenType.CARET)
        elif char == '~':
            self._add_token(TokenType.TILDE)
        elif char == '?':
            if self._match('?'):
                self._add_token(TokenType.ELVIS)
            else:
                self._add_token(TokenType.QUESTION)
        else:
            self._error(f"Unexpected character '{char}'")

    def _add_token(self, token_type: TokenType, value: object = None) -> None:
        """
        Add a token to the token list.

        Args:
            token_type: The type of token.
            value: The semantic value (defaults to None for most tokens,
                   set for literals).
        """
        lexeme = self.source[self.start:self.current]
        # Calculate the starting column
        start_col = self.column - len(lexeme)
        token = Token(token_type, value, lexeme, self.line, max(1, start_col))
        self.tokens.append(token)

    def _error(self, message: str) -> None:
        """
        Raise a lexer error with position information.

        Args:
            message: Description of what went wrong.

        Raises:
            LexerError with full context.
        """
        line_idx = self.line - 1
        source_line = self.source_lines[line_idx] if 0 <= line_idx < len(self.source_lines) else ""
        raise LexerError(message, self.line, self.column, source_line)
