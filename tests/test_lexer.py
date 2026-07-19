"""
Tests for the Samrat Lexer.

This test suite verifies that the lexer correctly tokenizes all Samrat
language constructs including literals, identifiers, keywords, operators,
comments, and error handling.
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tokens import Token, TokenType, KEYWORDS
from lexer import Lexer
from errors import LexerError


def test_empty_source():
    """Empty source should produce only EOF token."""
    lexer = Lexer("")
    tokens = lexer.tokenize()
    assert len(tokens) == 1
    assert tokens[0].type == TokenType.EOF
    print("  ✓ test_empty_source")


def test_whitespace_only():
    """Whitespace-only source should produce only EOF token."""
    lexer = Lexer("   \t  \n  \n  ")
    tokens = lexer.tokenize()
    assert len(tokens) == 1
    assert tokens[0].type == TokenType.EOF
    print("  ✓ test_whitespace_only")


def test_integer_literals():
    """Test decimal integer literals."""
    lexer = Lexer("42 0 -17 1_000_000")
    tokens = lexer.tokenize()
    # Expected: INTEGER, INTEGER, MINUS, INTEGER, EOF
    assert tokens[0].type == TokenType.INTEGER
    assert tokens[0].value == 42
    assert tokens[1].type == TokenType.INTEGER
    assert tokens[1].value == 0
    assert tokens[2].type == TokenType.MINUS
    assert tokens[3].type == TokenType.INTEGER
    assert tokens[3].value == 17
    assert tokens[4].value == 1000000
    print("  ✓ test_integer_literals")


def test_hex_literals():
    """Test hexadecimal integer literals."""
    lexer = Lexer("0xFF 0x1A 0xabc")
    tokens = lexer.tokenize()
    assert tokens[0].value == 255
    assert tokens[1].value == 26
    assert tokens[2].value == 2748
    print("  ✓ test_hex_literals")


def test_binary_literals():
    """Test binary integer literals."""
    lexer = Lexer("0b1010 0b1111")
    tokens = lexer.tokenize()
    assert tokens[0].value == 10
    assert tokens[1].value == 15
    print("  ✓ test_binary_literals")


def test_octal_literals():
    """Test octal integer literals."""
    lexer = Lexer("0o77 0o10")
    tokens = lexer.tokenize()
    assert tokens[0].value == 63
    assert tokens[1].value == 8
    print("  ✓ test_octal_literals")


def test_float_literals():
    """Test floating-point literals."""
    lexer = Lexer("3.14 -0.5 1.0 2.5e10 1e-3")
    tokens = lexer.tokenize()
    assert tokens[0].type == TokenType.FLOAT
    assert abs(tokens[0].value - 3.14) < 0.001
    assert tokens[1].type == TokenType.MINUS
    assert tokens[2].type == TokenType.FLOAT
    assert abs(tokens[2].value - 0.5) < 0.001
    assert tokens[3].type == TokenType.FLOAT
    assert abs(tokens[3].value - 1.0) < 0.001
    assert tokens[4].type == TokenType.FLOAT
    assert abs(tokens[4].value - 2.5e10) < 0.001
    assert tokens[5].type == TokenType.FLOAT
    assert abs(tokens[5].value - 0.001) < 0.0001
    print("  ✓ test_float_literals")


def test_string_literals():
    """Test string literals."""
    lexer = Lexer('"hello" "world" ""')
    tokens = lexer.tokenize()
    assert tokens[0].value == "hello"
    assert tokens[1].value == "world"
    assert tokens[2].value == ""
    print("  ✓ test_string_literals")


def test_string_escape_sequences():
    """Test escape sequences in string literals."""
    lexer = Lexer('"hello\\nworld" "tab:\\there" "quote:\\""')
    tokens = lexer.tokenize()
    assert tokens[0].value == "hello\nworld"
    assert tokens[1].value == "tab:\there"
    assert tokens[2].value == 'quote:"'
    print("  ✓ test_string_escape_sequences")


def test_boolean_literals():
    """Test boolean literals."""
    lexer = Lexer("true false")
    tokens = lexer.tokenize()
    assert tokens[0].type == TokenType.TRUE
    assert tokens[1].type == TokenType.FALSE
    print("  ✓ test_boolean_literals")


def test_null_literal():
    """Test null literal."""
    lexer = Lexer("null")
    tokens = lexer.tokenize()
    assert tokens[0].type == TokenType.NULL
    print("  ✓ test_null_literal")


def test_identifiers():
    """Test identifier tokenization."""
    lexer = Lexer("hello _private myVar my_var value1")
    tokens = lexer.tokenize()
    for i, expected in enumerate(["hello", "_private", "myVar", "my_var", "value1"]):
        assert tokens[i].type == TokenType.IDENTIFIER
        assert tokens[i].value == expected
    print("  ✓ test_identifiers")


def test_keywords():
    """Test that all keywords are recognized."""
    keyword_source = "let const func return if elif else while for in break continue class constructor this and or not import from as try catch throw"
    lexer = Lexer(keyword_source)
    tokens = lexer.tokenize()
    expected_keywords = [
        TokenType.LET, TokenType.CONST, TokenType.FUNC, TokenType.RETURN,
        TokenType.IF, TokenType.ELIF, TokenType.ELSE, TokenType.WHILE,
        TokenType.FOR, TokenType.IN, TokenType.BREAK, TokenType.CONTINUE,
        TokenType.CLASS, TokenType.CONSTRUCTOR, TokenType.THIS,
        TokenType.AND, TokenType.OR, TokenType.NOT,
        TokenType.IMPORT, TokenType.FROM, TokenType.AS,
        TokenType.TRY, TokenType.CATCH, TokenType.THROW,
    ]
    for i, expected_type in enumerate(expected_keywords):
        assert tokens[i].type == expected_type, f"Token {i}: expected {expected_type}, got {tokens[i].type}"
    print("  ✓ test_keywords")


def test_type_keywords():
    """Test type annotation keywords."""
    lexer = Lexer("int float str bool void")
    tokens = lexer.tokenize()
    expected = [TokenType.INT, TokenType.FLOAT_TYPE, TokenType.STR, TokenType.BOOL, TokenType.VOID]
    for i, expected_type in enumerate(expected):
        assert tokens[i].type == expected_type
    print("  ✓ test_type_keywords")


def test_arithmetic_operators():
    """Test arithmetic operators."""
    lexer = Lexer("+ - * / % **")
    tokens = lexer.tokenize()
    expected = [TokenType.PLUS, TokenType.MINUS, TokenType.STAR, TokenType.SLASH,
                TokenType.PERCENT, TokenType.STAR_STAR]
    for i, expected_type in enumerate(expected):
        assert tokens[i].type == expected_type
    print("  ✓ test_arithmetic_operators")


def test_comparison_operators():
    """Test comparison operators."""
    lexer = Lexer("== != < > <= >=")
    tokens = lexer.tokenize()
    expected = [TokenType.EQUAL_EQUAL, TokenType.BANG_EQUAL, TokenType.LESS,
                TokenType.GREATER, TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL]
    for i, expected_type in enumerate(expected):
        assert tokens[i].type == expected_type
    print("  ✓ test_comparison_operators")


def test_assignment_operators():
    """Test assignment operators."""
    lexer = Lexer("= += -= *= /= %=")
    tokens = lexer.tokenize()
    expected = [TokenType.EQUAL, TokenType.PLUS_EQUAL, TokenType.MINUS_EQUAL,
                TokenType.STAR_EQUAL, TokenType.SLASH_EQUAL, TokenType.PERCENT_EQUAL]
    for i, expected_type in enumerate(expected):
        assert tokens[i].type == expected_type
    print("  ✓ test_assignment_operators")


def test_bitwise_operators():
    """Test bitwise operators."""
    lexer = Lexer("& | ^ ~ << >>")
    tokens = lexer.tokenize()
    expected = [TokenType.AMPERSAND, TokenType.PIPE, TokenType.CARET,
                TokenType.TILDE, TokenType.LESS_LESS, TokenType.GREATER_GREATER]
    for i, expected_type in enumerate(expected):
        assert tokens[i].type == expected_type
    print("  ✓ test_bitwise_operators")


def test_punctuation():
    """Test punctuation tokens."""
    lexer = Lexer("( ) [ ] { } , . : ; .. ->")
    tokens = lexer.tokenize()
    expected = [
        TokenType.LEFT_PAREN, TokenType.RIGHT_PAREN,
        TokenType.LEFT_BRACKET, TokenType.RIGHT_BRACKET,
        TokenType.LEFT_BRACE, TokenType.RIGHT_BRACE,
        TokenType.COMMA, TokenType.DOT,
        TokenType.COLON, TokenType.SEMICOLON,
        TokenType.DOT_DOT, TokenType.ARROW,
    ]
    for i, expected_type in enumerate(expected):
        assert tokens[i].type == expected_type, f"Token {i}: expected {expected_type}, got {tokens[i].type}"
    print("  ✓ test_punctuation")


def test_single_line_comment():
    """Test single-line comments are skipped."""
    lexer = Lexer("let x = 5 // this is a comment\n let y = 10")
    tokens = lexer.tokenize()
    # Should have: LET, IDENTIFIER, EQUAL, INTEGER, LET, IDENTIFIER, EQUAL, INTEGER, EOF
    assert tokens[0].type == TokenType.LET
    assert tokens[1].value == "x"
    assert tokens[4].type == TokenType.LET
    assert tokens[5].value == "y"
    print("  ✓ test_single_line_comment")


def test_multi_line_comment():
    """Test multi-line comments are skipped."""
    lexer = Lexer("let x = 5 /* block comment */ let y = 10")
    tokens = lexer.tokenize()
    assert tokens[0].type == TokenType.LET
    assert tokens[3].type == TokenType.INTEGER
    assert tokens[4].type == TokenType.LET
    print("  ✓ test_multi_line_comment")


def test_nested_comments():
    """Test nested multi-line comments."""
    lexer = Lexer("/* outer /* inner */ more outer */ let x = 1")
    tokens = lexer.tokenize()
    assert tokens[0].type == TokenType.LET
    assert tokens[1].value == "x"
    print("  ✓ test_nested_comments")


def test_logical_operators():
    """Test logical operator keywords."""
    lexer = Lexer("and or not")
    tokens = lexer.tokenize()
    assert tokens[0].type == TokenType.AND
    assert tokens[1].type == TokenType.OR
    assert tokens[2].type == TokenType.NOT
    print("  ✓ test_logical_operators")


def test_full_program():
    """Test tokenization of a complete Samrat program."""
    source = """
func factorial(n: int) -> int {
    if n <= 1 {
        return 1
    }
    return n * factorial(n - 1)
}

let result = factorial(5)
print(result)
"""
    lexer = Lexer(source)
    tokens = lexer.tokenize()

    # Verify the structure of the token stream
    assert tokens[0].type == TokenType.FUNC
    assert tokens[1].value == "factorial"
    assert tokens[2].type == TokenType.LEFT_PAREN
    assert tokens[3].value == "n"
    assert tokens[4].type == TokenType.COLON
    assert tokens[5].type == TokenType.INT
    assert tokens[6].type == TokenType.RIGHT_PAREN
    assert tokens[7].type == TokenType.ARROW
    assert tokens[8].type == TokenType.INT
    assert tokens[9].type == TokenType.LEFT_BRACE
    assert tokens[10].type == TokenType.IF
    assert tokens[11].value == "n"

    # Check we have many tokens and end with EOF
    assert len(tokens) > 20
    assert tokens[-1].type == TokenType.EOF
    print("  ✓ test_full_program")


def test_line_column_tracking():
    """Test that line and column positions are tracked correctly."""
    source = "let\nx\n= 5"
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    assert tokens[0].line == 1  # let
    assert tokens[1].line == 2  # x
    assert tokens[2].line == 3  # =
    assert tokens[3].line == 3  # 5
    assert tokens[3].column == 3  # 5 is at column 3 (after '= ')
    print("  ✓ test_line_column_tracking")


def test_error_unterminated_string():
    """Test that unterminated strings produce an error."""
    lexer = Lexer('"hello')
    try:
        tokens = lexer.tokenize()
        assert False, "Expected LexerError was not raised"
    except LexerError as e:
        assert "Unterminated string literal" in str(e)
        print("  ✓ test_error_unterminated_string")


def test_error_unterminated_comment():
    """Test that unterminated multi-line comments produce an error."""
    lexer = Lexer("/* this comment never ends")
    try:
        tokens = lexer.tokenize()
        assert False, "Expected LexerError was not raised"
    except LexerError as e:
        assert "Unterminated multi-line comment" in str(e)
        print("  ✓ test_error_unterminated_comment")


def test_error_invalid_hex():
    """Test that invalid hex literals produce an error."""
    lexer = Lexer("0xGG")
    try:
        tokens = lexer.tokenize()
        assert False, "Expected LexerError was not raised"
    except LexerError as e:
        assert "Invalid hexadecimal literal" in str(e)
        print("  ✓ test_error_invalid_hex")


def test_error_invalid_binary():
    """Test that invalid binary literals produce an error."""
    lexer = Lexer("0b")
    try:
        tokens = lexer.tokenize()
        assert False, "Expected LexerError was not raised"
    except LexerError as e:
        assert "Invalid binary literal" in str(e)
        print("  ✓ test_error_invalid_binary")


def test_error_invalid_octal():
    """Test that invalid octal literals produce an error."""
    lexer = Lexer("0o")
    try:
        tokens = lexer.tokenize()
        assert False, "Expected LexerError was not raised"
    except LexerError as e:
        assert "Invalid octal literal" in str(e)
        print("  ✓ test_error_invalid_octal")


def test_error_unexpected_character():
    """Test that unexpected characters produce an error."""
    lexer = Lexer("let @ = 5")
    try:
        tokens = lexer.tokenize()
        assert False, "Expected LexerError was not raised"
    except LexerError as e:
        assert "Unexpected character" in str(e)
        print("  ✓ test_error_unexpected_character")


def test_range_operator():
    """Test the range operator '..' ."""
    lexer = Lexer("0..10")
    tokens = lexer.tokenize()
    assert tokens[0].type == TokenType.INTEGER
    assert tokens[1].type == TokenType.DOT_DOT
    assert tokens[2].type == TokenType.INTEGER
    print("  ✓ test_range_operator")


def test_dot_vs_dotdot():
    """Test that '.' and '..' are distinguished."""
    lexer = Lexer("a.b c..d")
    tokens = lexer.tokenize()
    assert tokens[1].type == TokenType.DOT       # a.b
    assert tokens[4].type == TokenType.DOT_DOT   # c..d
    print("  ✓ test_dot_vs_dotdot")


def test_arrow_operator():
    """Test the -> arrow operator."""
    lexer = Lexer("->")
    tokens = lexer.tokenize()
    assert tokens[0].type == TokenType.ARROW
    print("  ✓ test_arrow_operator")


def test_underscore_in_numbers():
    """Test underscores in numeric literals."""
    lexer = Lexer("1_000_000 0xFF_FF 3.141_592")
    tokens = lexer.tokenize()
    assert tokens[0].value == 1000000
    assert tokens[1].value == 65535
    assert abs(tokens[2].value - 3.141592) < 0.000001
    print("  ✓ test_underscore_in_numbers")


def test_class_definition():
    """Test tokenization of a class definition."""
    source = """
class Person {
    let name: str
    let age: int

    constructor(name: str, age: int) {
        this.name = name
        this.age = age
    }

    func greet() -> str {
        return "Hello, " + this.name
    }
}
"""
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    assert tokens[0].type == TokenType.CLASS
    assert tokens[1].value == "Person"
    assert tokens[2].type == TokenType.LEFT_BRACE
    assert tokens[3].type == TokenType.LET
    assert tokens[4].value == "name"
    assert tokens[5].type == TokenType.COLON
    assert tokens[6].type == TokenType.STR
    assert tokens[7].type == TokenType.LET
    assert tokens[8].value == "age"
    assert tokens[9].type == TokenType.COLON
    assert tokens[10].type == TokenType.INT
    assert tokens[11].type == TokenType.CONSTRUCTOR
    assert tokens[33].type == TokenType.FUNC
    assert tokens[-1].type == TokenType.EOF
    print("  ✓ test_class_definition")


def test_import_statement():
    """Test tokenization of import statements."""
    lexer = Lexer("import math\nimport sqrt from math\nimport math as m")
    tokens = lexer.tokenize()
    assert tokens[0].type == TokenType.IMPORT
    assert tokens[1].value == "math"
    assert tokens[2].type == TokenType.IMPORT
    assert tokens[3].value == "sqrt"
    assert tokens[4].type == TokenType.FROM
    assert tokens[5].value == "math"
    assert tokens[6].type == TokenType.IMPORT
    assert tokens[7].value == "math"
    assert tokens[8].type == TokenType.AS
    assert tokens[9].value == "m"
    print("  ✓ test_import_statement")


def test_try_catch():
    """Test tokenization of try/catch."""
    lexer = Lexer("try { risky() } catch error { print(error) }")
    tokens = lexer.tokenize()
    assert tokens[0].type == TokenType.TRY
    assert tokens[6].type == TokenType.CATCH
    assert tokens[7].value == "error"
    print("  ✓ test_try_catch")


def run_all_tests():
    """Run all lexer tests."""
    print("Running Lexer Tests...")
    print()

    # Collect all test functions
    tests = []
    for name, obj in globals().items():
        if name.startswith('test_') and callable(obj):
            tests.append(obj)

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"  ✗ {test.__name__}: FAILED - {e}")
            failed += 1

    print()
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)} tests")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)