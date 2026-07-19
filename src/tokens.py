"""
Samrat Programming Language — Token Definitions

This module defines all token types and the Token class used by the lexer.
Each token represents a meaningful unit of source code (keyword, identifier,
literal, operator, punctuation, etc.) with its location information for
producing excellent error messages.
"""

from enum import Enum, auto


class TokenType(Enum):
    """All possible token types in the Samrat language."""

    # Literals
    INTEGER = auto()  # 42, 0xFF, 0b1010
    FLOAT = auto()  # 3.14, 1e10
    STRING = auto()  # "hello"
    TRUE = auto()  # true
    FALSE = auto()  # false
    NULL = auto()  # null

    # Identifiers
    IDENTIFIER = auto()  # variable names, function names, etc.

    # Keywords
    LET = auto()  # let
    CONST = auto()  # const
    FUNC = auto()          # func
    RETURN = auto()        # return
    IF = auto()            # if
    ELIF = auto()          # elif
    ELSE = auto()          # else
    WHILE = auto()         # while
    FOR = auto()           # for
    IN = auto()            # in
    BREAK = auto()         # break
    CONTINUE = auto()      # continue
    CLASS = auto()         # class
    CONSTRUCTOR = auto()   # constructor
    THIS = auto()          # this
    NEW = auto()           # new
    AND = auto()           # and
    OR = auto()            # or
    NOT = auto()           # not
    IMPORT = auto()        # import
    FROM = auto()          # from
    AS = auto()            # as
    TRY = auto()           # try
    CATCH = auto()         # catch
    THROW = auto()         # throw
    INT = auto()           # int (type keyword)
    FLOAT_TYPE = auto()    # float (type keyword)
    STR = auto()           # str (type keyword)
    BOOL = auto()          # bool (type keyword)
    VOID = auto()          # void (type keyword)
    MATCH = auto()         # match (reserved for future)
    CASE = auto()          # case (reserved for future)
    DEFAULT = auto()  # default (reserved for future)

    # Operators
    PLUS = auto()  # +
    MINUS = auto()  # -
    STAR = auto()  # *
    SLASH = auto()  # /
    PERCENT = auto()  # %
    STAR_STAR = auto()  # ** (exponentiation)
    EQUAL_EQUAL = auto()  # ==
    BANG_EQUAL = auto()  # !=
    LESS = auto()  # <
    GREATER = auto()  # >
    LESS_EQUAL = auto()  # <=
    GREATER_EQUAL = auto()  # >=
    EQUAL = auto()  # =
    PLUS_EQUAL = auto()  # +=
    MINUS_EQUAL = auto()  # -=
    STAR_EQUAL = auto()  # *=
    SLASH_EQUAL = auto()  # /=
    PERCENT_EQUAL = auto()  # %=
    AMPERSAND = auto()  # &
    PIPE = auto()  # |
    CARET = auto()  # ^
    TILDE = auto()  # ~
    LESS_LESS = auto()  # <<
    GREATER_GREATER = auto()  # >>
    DOT = auto()  # .
    COMMA = auto()  # ,
    COLON = auto()  # :
    SEMICOLON = auto()  # ;
    ARROW = auto()  # ->
    DOT_DOT = auto()  # .. (range)

    # Punctuation
    LEFT_PAREN = auto()  # (
    RIGHT_PAREN = auto()  # )
    LEFT_BRACKET = auto()  # [
    RIGHT_BRACKET = auto()  # ]
    LEFT_BRACE = auto()  # {
    RIGHT_BRACE = auto()  # }

    # Special
    EOF = auto()  # End of file
    NEWLINE = auto()  # Newline (significant for statement separation)
    INDENT = auto()  # Indentation (not used in brace-based syntax, reserved)
    DEDENT = auto()  # Dedentation (not used in brace-based syntax, reserved)

    # Error
    ERROR = auto()  # Lexer error token


# Mapping of keyword strings to their token types
KEYWORDS = {
    'let': TokenType.LET,
    'const': TokenType.CONST,
    'func': TokenType.FUNC,
    'return': TokenType.RETURN,
    'if': TokenType.IF,
    'elif': TokenType.ELIF,
    'else': TokenType.ELSE,
    'while': TokenType.WHILE,
    'for': TokenType.FOR,
    'in': TokenType.IN,
    'break': TokenType.BREAK,
    'continue': TokenType.CONTINUE,
    'class': TokenType.CLASS,
    'constructor': TokenType.CONSTRUCTOR,
    'this': TokenType.THIS,
    'new': TokenType.NEW,
    'and': TokenType.AND,
    'or': TokenType.OR,
    'not': TokenType.NOT,
    'import': TokenType.IMPORT,
    'from': TokenType.FROM,
    'as': TokenType.AS,
    'try': TokenType.TRY,
    'catch': TokenType.CATCH,
    'throw': TokenType.THROW,
    'int': TokenType.INT,
    'float': TokenType.FLOAT_TYPE,
    'str': TokenType.STR,
    'bool': TokenType.BOOL,
    'void': TokenType.VOID,
    'match': TokenType.MATCH,
    'case': TokenType.CASE,
    'default': TokenType.DEFAULT,
    'true': TokenType.TRUE,
    'false': TokenType.FALSE,
    'null': TokenType.NULL,
}


class Token:
    """
    Represents a single token produced by the lexer.

    Attributes:
        type: The TokenType of this token.
        value: The literal value of the token (e.g., the actual number for
               INTEGER tokens, the string content for STRING tokens).
        lexeme: The raw text of the token as it appears in source code.
        line: The line number where the token starts (1-based).
        column: The column number where the token starts (1-based).
    """

    def __init__(self, token_type: TokenType, value: object,
                 lexeme: str, line: int, column: int):
        self.type = token_type
        self.value = value
        self.lexeme = lexeme
        self.line = line
        self.column = column

    def __repr__(self) -> str:
        return (f"Token({self.type.name}, "
                f"value={self.value!r}, "
                f"lexeme={self.lexeme!r}, "
                f"line={self.line}, col={self.column})")

    def __str__(self) -> str:
        return f"{self.type.name}({self.lexeme!r}) at {self.line}:{self.column}"
