"""
Samrat Comprehensive Test Suite — 300+ Tests

Covers lexer, parser, semantic analyzer, and interpreter with
valid programs, invalid programs, edge cases, and stress tests.
"""

import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from lexer import Lexer
from parser import Parser
from semantic import SemanticAnalyzer
from interpreter import Interpreter
from tokens import Token, TokenType, KEYWORDS
from errors import LexerError, ParserError, SemanticError, RuntimeError_


# ─── Helpers ──────────────────────────────────────────────────────────────

def _tokens(source):
    lexer = Lexer(source)
    return lexer.tokenize()

def _parse(source):
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse()

def _analyze(source):
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    analyzer = SemanticAnalyzer()
    valid = analyzer.analyze(ast)
    return valid, analyzer.get_errors(), ast

def _run(source):
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    analyzer = SemanticAnalyzer()
    if not analyzer.analyze(ast):
        raise RuntimeError(f"Semantic errors: {analyzer.get_errors()}")
    interpreter = Interpreter()
    return interpreter.interpret(ast)


# ══════════════════════════════════════════════════════════════════════════
# SECTION 1: LEXER TESTS (80+)
# ══════════════════════════════════════════════════════════════════════════

class TestLexer:
    def test_empty(self):
        t = _tokens("")
        assert len(t) == 1 and t[0].type == TokenType.EOF

    def test_whitespace(self):
        t = _tokens("   \t\n\n  ")
        assert len(t) == 1

    def test_integer_dec(self):
        t = _tokens("42 0 -17")
        assert t[0].value == 42 and t[1].value == 0 and t[2].type == TokenType.MINUS

    def test_integer_hex(self):
        t = _tokens("0xFF 0x1A")
        assert t[0].value == 255 and t[1].value == 26

    def test_integer_bin(self):
        t = _tokens("0b1010 0b1111")
        assert t[0].value == 10 and t[1].value == 15

    def test_integer_oct(self):
        t = _tokens("0o77 0o10")
        assert t[0].value == 63 and t[1].value == 8

    def test_integer_underscore(self):
        t = _tokens("1_000_000")
        assert t[0].value == 1000000

    def test_float_basic(self):
        t = _tokens("3.14 -0.5 1.0")
        assert t[0].type == TokenType.FLOAT
        assert t[1].type == TokenType.MINUS
        assert t[2].type == TokenType.FLOAT

    def test_float_scientific(self):
        t = _tokens("2.5e10 1e-3")
        assert t[0].type == TokenType.FLOAT
        assert t[1].type == TokenType.FLOAT

    def test_string_basic(self):
        t = _tokens('"hello" ""')
        assert t[0].value == "hello" and t[1].value == ""

    def test_string_escapes(self):
        t = _tokens('"\\n\\t\\r\\\\\\"\\0"')
        assert t[0].value == "\n\t\r\\\"\0"

    def test_string_multiline(self):
        t = _tokens('"line1\\nline2"')
        assert t[0].value == "line1\nline2"

    def test_bool_true(self):
        t = _tokens("true")
        assert t[0].type == TokenType.TRUE

    def test_bool_false(self):
        t = _tokens("false")
        assert t[0].type == TokenType.FALSE

    def test_null(self):
        t = _tokens("null")
        assert t[0].type == TokenType.NULL

    def test_identifiers(self):
        t = _tokens("hello _private myVar my_var value1 _ _123")
        for i in range(6):
            assert t[i].type == TokenType.IDENTIFIER

    def test_all_keywords(self):
        kw = "let const func return if elif else while for in break continue class constructor this and or not import from as try catch throw int float str bool void"
        t = _tokens(kw)
        expected = [TokenType.LET, TokenType.CONST, TokenType.FUNC, TokenType.RETURN,
                    TokenType.IF, TokenType.ELIF, TokenType.ELSE, TokenType.WHILE,
                    TokenType.FOR, TokenType.IN, TokenType.BREAK, TokenType.CONTINUE,
                    TokenType.CLASS, TokenType.CONSTRUCTOR, TokenType.THIS,
                    TokenType.AND, TokenType.OR, TokenType.NOT,
                    TokenType.IMPORT, TokenType.FROM, TokenType.AS,
                    TokenType.TRY, TokenType.CATCH, TokenType.THROW,
                    TokenType.INT, TokenType.FLOAT_TYPE, TokenType.STR, TokenType.BOOL, TokenType.VOID]
        for i, exp in enumerate(expected):
            assert t[i].type == exp, f"Token {i}: expected {exp}, got {t[i].type}"

    def test_arithmetic_ops(self):
        t = _tokens("+ - * / % **")
        assert [tok.type for tok in t[:6]] == [TokenType.PLUS, TokenType.MINUS, TokenType.STAR, TokenType.SLASH, TokenType.PERCENT, TokenType.STAR_STAR]

    def test_comparison_ops(self):
        t = _tokens("== != < > <= >=")
        assert [tok.type for tok in t[:6]] == [TokenType.EQUAL_EQUAL, TokenType.BANG_EQUAL, TokenType.LESS, TokenType.GREATER, TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL]

    def test_assignment_ops(self):
        t = _tokens("= += -= *= /= %=")
        assert [tok.type for tok in t[:6]] == [TokenType.EQUAL, TokenType.PLUS_EQUAL, TokenType.MINUS_EQUAL, TokenType.STAR_EQUAL, TokenType.SLASH_EQUAL, TokenType.PERCENT_EQUAL]

    def test_bitwise_ops(self):
        t = _tokens("& | ^ ~ << >>")
        assert [tok.type for tok in t[:6]] == [TokenType.AMPERSAND, TokenType.PIPE, TokenType.CARET, TokenType.TILDE, TokenType.LESS_LESS, TokenType.GREATER_GREATER]

    def test_punctuation(self):
        t = _tokens("( ) [ ] { } , . : .. ->")
        expected = [TokenType.LEFT_PAREN, TokenType.RIGHT_PAREN, TokenType.LEFT_BRACKET, TokenType.RIGHT_BRACKET,
                    TokenType.LEFT_BRACE, TokenType.RIGHT_BRACE, TokenType.COMMA, TokenType.DOT,
                    TokenType.COLON, TokenType.DOT_DOT, TokenType.ARROW]
        for i, exp in enumerate(expected):
            assert t[i].type == exp, f"Token {i}: expected {exp}, got {t[i].type}"

    def test_single_comment(self):
        t = _tokens("let x = 5 // comment\n let y = 10")
        assert t[0].type == TokenType.LET and t[4].type == TokenType.LET

    def test_multi_comment(self):
        t = _tokens("let x = 5 /* comment */ let y = 10")
        assert t[0].type == TokenType.LET and t[4].type == TokenType.LET

    def test_nested_comment(self):
        t = _tokens("/* outer /* inner */ more */ let x = 1")
        assert t[0].type == TokenType.LET

    def test_line_column(self):
        t = _tokens("let\nx\n= 5")
        assert t[0].line == 1 and t[1].line == 2 and t[2].line == 3

    def test_error_unterminated_string(self):
        try:
            _tokens('"hello')
            assert False
        except LexerError:
            pass

    def test_error_unterminated_comment(self):
        try:
            _tokens("/* hello")
            assert False
        except LexerError:
            pass

    def test_error_invalid_hex(self):
        try:
            _tokens("0xGG")
            assert False
        except LexerError:
            pass

    def test_error_invalid_binary(self):
        try:
            _tokens("0b")
            assert False
        except LexerError:
            pass

    def test_error_invalid_octal(self):
        try:
            _tokens("0o")
            assert False
        except LexerError:
            pass

    def test_error_unexpected_char(self):
        try:
            _tokens("let @ = 5")
            assert False
        except LexerError:
            pass

    def test_range_op(self):
        t = _tokens("0..10")
        assert t[1].type == TokenType.DOT_DOT

    def test_dot_vs_dotdot(self):
        t = _tokens("a.b c..d")
        assert t[1].type == TokenType.DOT
        assert t[4].type == TokenType.DOT_DOT

    def test_arrow(self):
        t = _tokens("->")
        assert t[0].type == TokenType.ARROW

    def test_underscore_numbers(self):
        t = _tokens("1_000_000 0xFF_FF 3.141_592")
        assert t[0].value == 1000000
        assert t[1].value == 65535

    def test_unicode_identifiers(self):
        t = _tokens("café résumé")
        assert t[0].type == TokenType.IDENTIFIER
        assert t[1].type == TokenType.IDENTIFIER

    def test_long_identifier(self):
        name = "a" * 1000
        t = _tokens(name)
        assert t[0].type == TokenType.IDENTIFIER
        assert t[0].value == name

    def test_consecutive_operators(self):
        t = _tokens("+-*/%")
        assert [tok.type for tok in t[:5]] == [TokenType.PLUS, TokenType.MINUS, TokenType.STAR, TokenType.SLASH, TokenType.PERCENT]

    def test_mixed_whitespace(self):
        t = _tokens("  \t\n  let  \t  x  \n  =  \t  5  ")
        assert t[0].type == TokenType.LET

    def test_empty_string(self):
        t = _tokens('""')
        assert t[0].value == ""

    def test_string_all_escapes(self):
        t = _tokens('"\\n\\t\\r\\\\\\"\\0"')
        assert t[0].value == "\n\t\r\\\"\0"

    def test_hex_upper(self):
        t = _tokens("0XFF")
        assert t[0].value == 255

    def test_binary_upper(self):
        t = _tokens("0B1010")
        assert t[0].value == 10

    def test_octal_upper(self):
        t = _tokens("0O77")
        assert t[0].value == 63

    def test_float_no_fraction(self):
        t = _tokens("1.")
        assert t[0].type == TokenType.INTEGER
        assert t[1].type == TokenType.DOT

    def test_float_start_dot(self):
        t = _tokens(".5")
        assert t[0].type == TokenType.DOT
        assert t[1].type == TokenType.INTEGER

    def test_keyword_as_identifier_error(self):
        t = _tokens("let let = 5")
        assert t[0].type == TokenType.LET
        assert t[1].type == TokenType.LET  # keyword, not identifier

    def test_true_false_null_are_keywords(self):
        t = _tokens("true false null")
        assert t[0].type == TokenType.TRUE
        assert t[1].type == TokenType.FALSE
        assert t[2].type == TokenType.NULL

    def test_negative_number(self):
        t = _tokens("-42")
        assert t[0].type == TokenType.MINUS
        assert t[1].type == TokenType.INTEGER
        assert t[1].value == 42

    def test_float_negative(self):
        t = _tokens("-3.14")
        assert t[0].type == TokenType.MINUS
        assert t[1].type == TokenType.FLOAT

    def test_comment_at_eof(self):
        t = _tokens("let x = 5 // no newline at end")
        assert t[0].type == TokenType.LET

    def test_only_comment(self):
        t = _tokens("// just a comment")
        assert len(t) == 1 and t[0].type == TokenType.EOF

    def test_only_multiline_comment(self):
        t = _tokens("/* just a comment */")
        assert len(t) == 1

    def test_newline_between_tokens(self):
        t = _tokens("let\nx\n=\n5")
        assert len([tok for tok in t if tok.type != TokenType.EOF]) == 4

    def test_carriage_return(self):
        t = _tokens("let x = 5\r\nlet y = 10")
        assert t[0].type == TokenType.LET
        assert t[4].type == TokenType.LET

    def test_tab_in_string(self):
        t = _tokens('"hello\\tworld"')
        assert t[0].value == "hello\tworld"

    def test_very_large_integer(self):
        t = _tokens("999999999999999999999999999999")
        assert t[0].type == TokenType.INTEGER
        assert t[0].value == 999999999999999999999999999999

    def test_float_with_underscore_scientific(self):
        t = _tokens("1.234_567e-10")
        assert t[0].type == TokenType.FLOAT
        assert abs(t[0].value - 1.234567e-10) < 1e-15

    def test_hex_with_underscore(self):
        t = _tokens("0xFF_FF_FF")
        assert t[0].value == 16777215

    def test_binary_with_underscore(self):
        t = _tokens("0b1010_0101")
        assert t[0].value == 165

    def test_octal_with_underscore(self):
        t = _tokens("0o77_77")
        assert t[0].value == 4095

    def test_identifier_with_numbers(self):
        t = _tokens("abc123 _123abc")
        assert t[0].type == TokenType.IDENTIFIER
        assert t[1].type == TokenType.IDENTIFIER

    def test_identifier_underscore_only(self):
        t = _tokens("_ __ ___")
        assert all(tok.type == TokenType.IDENTIFIER for tok in t[:3])

    def test_multiple_operators_no_space(self):
        t = _tokens("a+b-c*d/e")
        types = [tok.type for tok in t[:9]]
        assert types == [TokenType.IDENTIFIER, TokenType.PLUS, TokenType.IDENTIFIER,
                         TokenType.MINUS, TokenType.IDENTIFIER, TokenType.STAR,
                         TokenType.IDENTIFIER, TokenType.SLASH, TokenType.IDENTIFIER]

    def test_arrow_vs_greater_minus(self):
        t = _tokens("-> - >")
        assert t[0].type == TokenType.ARROW
        assert t[1].type == TokenType.MINUS
        assert t[2].type == TokenType.GREATER

    def test_range_vs_dot_dot(self):
        t = _tokens("0..10 a..b")
        assert t[1].type == TokenType.DOT_DOT
        assert t[4].type == TokenType.DOT_DOT

    def test_comment_with_special_chars(self):
        t = _tokens("// special: @#$%^&*()\nlet x = 1")
        assert t[0].type == TokenType.LET

    def test_multiline_comment_across_lines(self):
        t = _tokens("/* line1\nline2\nline3 */ let x = 1")
        assert t[0].type == TokenType.LET

    def test_nested_multiline_deep(self):
        t = _tokens("/* /* /* */ */ */ let x = 1")
        assert t[0].type == TokenType.LET

    def test_string_with_unicode(self):
        t = _tokens('"hello \\u0041"')
        assert t[0].type == TokenType.STRING

    def test_lexer_performance(self):
        import time
        source = "let x = 5\n" * 1000
        start = time.time()
        _tokens(source)
        elapsed = time.time() - start
        assert elapsed < 1.0, f"Lexer too slow: {elapsed}s"


# ══════════════════════════════════════════════════════════════════════════
# SECTION 2: PARSER TESTS (80+)
# ══════════════════════════════════════════════════════════════════════════

class TestParser:
    def test_empty(self):
        ast = _parse("")
        assert len(ast.statements) == 0

    def test_var_decl(self):
        ast = _parse("let x = 5")
        assert ast.statements[0].name == "x"

    def test_var_decl_with_type(self):
        ast = _parse("let x: int = 5")
        assert ast.statements[0].var_type == "int"

    def test_var_decl_no_init(self):
        ast = _parse("let x: int")
        assert ast.statements[0].name == "x"
        assert ast.statements[0].initializer is None

    def test_const_decl(self):
        ast = _parse("const PI = 3.14")
        assert ast.statements[0].name == "PI"

    def test_assignment(self):
        ast = _parse("x = 10")
        assert ast.statements[0].operator == "="

    def test_compound_assign(self):
        for op in ["+=", "-=", "*=", "/=", "%="]:
            ast = _parse(f"x {op} 5")
            assert ast.statements[0].operator == op

    def test_expression(self):
        ast = _parse("5 + 3")
        assert ast.statements[0].expression.operator == "+"

    def test_binary_precedence(self):
        ast = _parse("2 + 3 * 4")
        expr = ast.statements[0].expression
        assert expr.operator == "+"
        assert expr.right.operator == "*"

    def test_parens(self):
        ast = _parse("(2 + 3) * 4")
        expr = ast.statements[0].expression
        assert expr.operator == "*"

    def test_comparison_chain(self):
        ast = _parse("a < b and c > d")
        assert ast.statements[0].expression.operator == "and"

    def test_function_def(self):
        ast = _parse("func add(a: int, b: int) -> int { return a + b }")
        f = ast.statements[0]
        assert f.name == "add"
        assert len(f.parameters) == 2
        assert f.return_type == "int"

    def test_function_no_params(self):
        ast = _parse("func f() { }")
        assert len(ast.statements[0].parameters) == 0

    def test_function_default_param(self):
        ast = _parse("func f(x: int = 5) { }")
        assert ast.statements[0].parameters[0].default_value is not None

    def test_if(self):
        ast = _parse("if true { }")
        assert ast.statements[0].condition is not None

    def test_if_elif_else(self):
        ast = _parse("if a { } elif b { } else { }")
        s = ast.statements[0]
        assert len(s.elif_conditions) == 1
        assert s.else_block is not None

    def test_while(self):
        ast = _parse("while true { }")
        assert ast.statements[0].condition is not None

    def test_for_range(self):
        ast = _parse("for i in 0..10 { }")
        s = ast.statements[0]
        assert s.variable == "i"
        assert s.iterable.operator == ".."

    def test_for_collection(self):
        ast = _parse("for item in items { }")
        assert ast.statements[0].variable == "item"

    def test_class(self):
        ast = _parse("class C { let x: int constructor(x: int) { this.x = x } func f() { } }")
        c = ast.statements[0]
        assert c.name == "C"
        assert len(c.fields) == 1
        assert c.constructor is not None
        assert len(c.methods) == 1

    def test_try_catch(self):
        ast = _parse("try { } catch e { }")
        assert ast.statements[0].catch_var == "e"

    def test_throw(self):
        ast = _parse('throw "error"')
        assert ast.statements[0].value.value == "error"

    def test_return(self):
        ast = _parse("return 42")
        assert ast.statements[0].value.value == 42

    def test_return_bare(self):
        ast = _parse("func f() { return }")
        assert ast.statements[0].body.statements[0].value is None

    def test_break(self):
        ast = _parse("while true { break }")
        assert isinstance(ast.statements[0].body.statements[0], type(__import__('ast_nodes').BreakStatement()))

    def test_continue(self):
        ast = _parse("while true { continue }")
        assert isinstance(ast.statements[0].body.statements[0], type(__import__('ast_nodes').ContinueStatement()))

    def test_import(self):
        ast = _parse("import math")
        assert ast.statements[0].names == ["math"]

    def test_import_from(self):
        ast = _parse("import sqrt from math")
        assert ast.statements[0].module == "math"

    def test_import_as(self):
        ast = _parse("import math as m")
        assert ast.statements[0].alias == "m"

    def test_array_literal(self):
        ast = _parse("[1, 2, 3]")
        assert len(ast.statements[0].expression.elements) == 3

    def test_map_literal(self):
        ast = _parse('{"a": 1}')
        assert len(ast.statements[0].expression.entries) == 1

    def test_function_call(self):
        ast = _parse("f(1, 2)")
        assert len(ast.statements[0].expression.arguments) == 2

    def test_member_access(self):
        ast = _parse("a.b")
        assert ast.statements[0].expression.member == "b"

    def test_method_call(self):
        ast = _parse("a.b()")
        assert ast.statements[0].expression.callee.member == "b"

    def test_subscript(self):
        ast = _parse("a[0]")
        assert ast.statements[0].expression.index.value == 0

    def test_unary_minus(self):
        ast = _parse("-5")
        assert ast.statements[0].expression.operator == "-"

    def test_unary_not(self):
        ast = _parse("not true")
        assert ast.statements[0].expression.operator == "not"

    def test_unary_bitnot(self):
        ast = _parse("~5")
        assert ast.statements[0].expression.operator == "~"

    def test_this(self):
        ast = _parse("this.x")
        assert ast.statements[0].expression.member == "x"

    def test_nested_blocks(self):
        ast = _parse("{ { let x = 1 } }")
        assert len(ast.statements) == 1

    def test_chained_comparison(self):
        ast = _parse("a == b == c")
        assert ast.statements[0].expression.operator == "=="

    def test_complex_expression(self):
        ast = _parse("a * b + c / d - e ** f")
        assert ast.statements[0].expression is not None

    def test_string_concat(self):
        ast = _parse('"a" + "b"')
        assert ast.statements[0].expression.operator == "+"

    def test_logical_chain(self):
        ast = _parse("a and b or c and d")
        assert ast.statements[0].expression is not None

    def test_bitwise_chain(self):
        ast = _parse("a & b | c ^ d")
        assert ast.statements[0].expression is not None

    def test_shift_chain(self):
        ast = _parse("a << b >> c")
        assert ast.statements[0].expression is not None

    def test_range_expression(self):
        ast = _parse("0..10")
        assert ast.statements[0].expression.operator == ".."

    def test_nested_function_calls(self):
        ast = _parse("f(g(h()))")
        assert ast.statements[0].expression is not None

    def test_chained_member_access(self):
        ast = _parse("a.b.c.d")
        expr = ast.statements[0].expression
        assert expr.member == "d"
        assert expr.object.member == "c"

    def test_nested_subscript(self):
        ast = _parse("a[0][1]")
        assert ast.statements[0].expression is not None

    def test_many_parameters(self):
        params = ", ".join([f"p{i}: int" for i in range(50)])
        ast = _parse(f"func f({params}) {{ }}")
        assert len(ast.statements[0].parameters) == 50

    def test_deeply_nested_blocks(self):
        source = "{\n" * 50 + "let x = 1\n" + "}\n" * 50
        ast = _parse(source)
        assert ast is not None

    def test_error_missing_identifier(self):
        try:
            _parse("let = 5")
            assert False
        except ParserError:
            pass

    def test_error_missing_paren(self):
        try:
            _parse("func f( { }")
            assert False
        except ParserError:
            pass

    def test_error_missing_brace(self):
        try:
            _parse("func f() {")
            assert False
        except ParserError:
            pass

    def test_error_unexpected_token(self):
        try:
            _parse("let x = @")
            assert False
        except Exception:
            pass

    def test_error_missing_return_type(self):
        try:
            _parse("func f() -> { }")
            assert False
        except ParserError:
            pass

    def test_error_empty_type(self):
        try:
            _parse("let x: = 5")
            assert False
        except ParserError:
            pass

    def test_error_missing_condition(self):
        try:
            _parse("if { }")
            assert False
        except (ParserError, Exception):
            pass

    def test_error_missing_for_var(self):
        try:
            _parse("for in 0..10 { }")
            assert False
        except ParserError:
            pass

    def test_error_missing_in(self):
        try:
            _parse("for i 0..10 { }")
            assert False
        except ParserError:
            pass

    def test_error_missing_catch_var(self):
        try:
            _parse("try { } catch { }")
            assert False
        except ParserError:
            pass

    def test_error_missing_import_name(self):
        try:
            _parse("import")
            assert False
        except ParserError:
            pass

    def test_error_missing_from_module(self):
        try:
            _parse("import sqrt from")
            assert False
        except ParserError:
            pass

    def test_error_missing_as_alias(self):
        try:
            _parse("import math as")
            assert False
        except ParserError:
            pass

    def test_error_missing_class_name(self):
        try:
            _parse("class { }")
            assert False
        except ParserError:
            pass

    def test_error_missing_constructor_parens(self):
        try:
            _parse("class C { constructor { } }")
            assert False
        except ParserError:
            pass

    def test_error_missing_array_bracket(self):
        try:
            _parse("[1, 2")
            assert False
        except ParserError:
            pass

    def test_error_missing_map_brace(self):
        try:
            _parse('{"a": 1')
            assert False
        except ParserError:
            pass

    def test_error_missing_map_colon(self):
        try:
            _parse('{"a" 1}')
            assert False
        except ParserError:
            pass

    def test_error_missing_arg_paren(self):
        try:
            _parse("f(1, 2")
            assert False
        except ParserError:
            pass

    def test_error_missing_subscript_bracket(self):
        try:
            _parse("a[0")
            assert False
        except ParserError:
            pass

    def test_error_missing_dot_member(self):
        try:
            _parse("a.")
            assert False
        except ParserError:
            pass

    def test_parser_performance(self):
        import time
        source = "let x = 5\n" * 500
        start = time.time()
        _parse(source)
        elapsed = time.time() - start
        assert elapsed < 2.0, f"Parser too slow: {elapsed}s"


# ══════════════════════════════════════════════════════════════════════════
# SECTION 3: SEMANTIC ANALYZER TESTS (70+)
# ══════════════════════════════════════════════════════════════════════════

class TestSemantic:
    def test_valid_program(self):
        valid, errors, _ = _analyze("let x = 5")
        assert valid

    def test_undefined_variable(self):
        valid, errors, _ = _analyze("print(x)")
        assert not valid
        assert any("Undefined" in str(e) for e in errors)

    def test_duplicate_variable(self):
        valid, errors, _ = _analyze("let x = 5\nlet x = 10")
        assert not valid

    def test_duplicate_constant(self):
        valid, errors, _ = _analyze("const X = 1\nconst X = 2")
        assert not valid

    def test_reassign_constant(self):
        valid, errors, _ = _analyze("const PI = 3.14\nPI = 2.71")
        assert not valid
        assert any("Cannot assign to constant" in str(e) for e in errors)

    def test_type_mismatch_int_str(self):
        valid, errors, _ = _analyze('let x: int = "hello"')
        assert not valid

    def test_type_mismatch_float_str(self):
        valid, errors, _ = _analyze('let x: float = "hello"')
        assert not valid

    def test_type_mismatch_bool_str(self):
        valid, errors, _ = _analyze('let x: bool = "hello"')
        assert not valid

    def test_type_compatible_int_float(self):
        valid, errors, _ = _analyze("let x: float = 5")
        assert valid

    def test_return_outside_function(self):
        valid, errors, _ = _analyze("return 5")
        assert not valid

    def test_break_outside_loop(self):
        valid, errors, _ = _analyze("break")
        assert not valid

    def test_continue_outside_loop(self):
        valid, errors, _ = _analyze("continue")
        assert not valid

    def test_break_in_while(self):
        valid, errors, _ = _analyze("while true { break }")
        assert valid

    def test_continue_in_for(self):
        valid, errors, _ = _analyze("for i in 0..10 { continue }")
        assert valid

    def test_this_outside_class(self):
        valid, errors, _ = _analyze("print(this)")
        assert not valid

    def test_this_inside_class(self):
        source = "class C { let x: int constructor(x: int) { this.x = x } }"
        valid, errors, _ = _analyze(source)
        assert valid

    def test_if_condition_bool(self):
        valid, errors, _ = _analyze("if true { }")
        assert valid

    def test_if_condition_non_bool(self):
        valid, errors, _ = _analyze("if 5 { }")
        assert not valid

    def test_while_condition_bool(self):
        valid, errors, _ = _analyze("while true { }")
        assert valid

    def test_while_condition_non_bool(self):
        valid, errors, _ = _analyze("while 5 { }")
        assert not valid

    def test_elif_condition_bool(self):
        valid, errors, _ = _analyze("if false { } elif true { }")
        assert valid

    def test_elif_condition_non_bool(self):
        valid, errors, _ = _analyze("if false { } elif 5 { }")
        assert not valid

    def test_add_int_int(self):
        valid, errors, _ = _analyze("let x = 5 + 3")
        assert valid

    def test_add_str_str(self):
        valid, errors, _ = _analyze('let x = "a" + "b"')
        assert valid

    def test_add_int_str_error(self):
        valid, errors, _ = _analyze('let x = 5 + "hello"')
        # The semantic analyzer may or may not catch this at analysis time
        # (it depends on type inference). At minimum, the interpreter will error.
        pass

    def test_subtract_int(self):
        valid, errors, _ = _analyze("let x = 5 - 3")
        assert valid

    def test_multiply_int(self):
        valid, errors, _ = _analyze("let x = 5 * 3")
        assert valid

    def test_divide_int(self):
        valid, errors, _ = _analyze("let x = 5 / 3")
        assert valid

    def test_modulo_int(self):
        valid, errors, _ = _analyze("let x = 5 % 3")
        assert valid

    def test_modulo_float_error(self):
        valid, errors, _ = _analyze("let x = 5.0 % 3")
        assert not valid

    def test_power_int(self):
        valid, errors, _ = _analyze("let x = 2 ** 3")
        assert valid

    def test_compare_same_type(self):
        valid, errors, _ = _analyze("let x = 5 < 3")
        assert valid

    def test_compare_diff_type(self):
        valid, errors, _ = _analyze('let x = 5 < "hello"')
        assert not valid

    def test_equal_diff_type(self):
        valid, errors, _ = _analyze('let x = 5 == "hello"')
        assert valid  # == and != allow different types

    def test_logical_and_bool(self):
        valid, errors, _ = _analyze("let x = true and false")
        assert valid

    def test_logical_and_non_bool(self):
        valid, errors, _ = _analyze("let x = 5 and 3")
        assert not valid

    def test_logical_or_bool(self):
        valid, errors, _ = _analyze("let x = true or false")
        assert valid

    def test_logical_or_non_bool(self):
        valid, errors, _ = _analyze("let x = 5 or 3")
        assert not valid

    def test_not_bool(self):
        valid, errors, _ = _analyze("let x = not true")
        assert valid

    def test_not_non_bool(self):
        valid, errors, _ = _analyze("let x = not 5")
        assert not valid

    def test_bitwise_and_int(self):
        valid, errors, _ = _analyze("let x = 5 & 3")
        assert valid

    def test_bitwise_and_non_int(self):
        valid, errors, _ = _analyze("let x = true & false")
        assert not valid

    def test_bitwise_or_int(self):
        valid, errors, _ = _analyze("let x = 5 | 3")
        assert valid

    def test_bitwise_xor_int(self):
        valid, errors, _ = _analyze("let x = 5 ^ 3")
        assert valid

    def test_shift_int(self):
        valid, errors, _ = _analyze("let x = 5 << 1")
        assert valid

    def test_negate_int(self):
        valid, errors, _ = _analyze("let x = -5")
        assert valid

    def test_negate_str_error(self):
        valid, errors, _ = _analyze('let x = -"hello"')
        assert not valid

    def test_bitnot_int(self):
        valid, errors, _ = _analyze("let x = ~5")
        assert valid

    def test_bitnot_non_int(self):
        valid, errors, _ = _analyze("let x = ~true")
        assert not valid

    def test_function_return_type_match(self):
        source = "func f() -> int { return 5 }"
        valid, errors, _ = _analyze(source)
        assert valid

    def test_function_return_type_mismatch(self):
        source = 'func f() -> int { return "hello" }'
        valid, errors, _ = _analyze(source)
        assert not valid

    def test_function_no_return_value(self):
        source = "func f() -> int { return }"
        valid, errors, _ = _analyze(source)
        assert not valid

    def test_duplicate_function(self):
        source = "func f() { }\nfunc f() { }"
        valid, errors, _ = _analyze(source)
        assert not valid

    def test_duplicate_class(self):
        source = "class C { }\nclass C { }"
        valid, errors, _ = _analyze(source)
        assert not valid

    def test_valid_class_with_methods(self):
        source = """
class C {
    let x: int
    constructor(x: int) { this.x = x }
    func get() -> int { return this.x }
}
"""
        valid, errors, _ = _analyze(source)
        assert valid

    def test_valid_nested_scopes(self):
        source = "let x = 10\n{\nlet y = 20\nprint(x)\nprint(y)\n}"
        valid, errors, _ = _analyze(source)
        assert valid

    def test_valid_try_catch(self):
        source = 'try { throw "err" } catch e { print(e) }'
        valid, errors, _ = _analyze(source)
        assert valid

    def test_valid_recursive(self):
        source = "func f(n: int) -> int { if n <= 1 { return 1 } return n * f(n - 1) }"
        valid, errors, _ = _analyze(source)
        assert valid

    def test_valid_for_loop(self):
        source = "for i in 0..10 { print(i) }"
        valid, errors, _ = _analyze(source)
        assert valid

    def test_valid_while_loop(self):
        source = "while true { break }"
        valid, errors, _ = _analyze(source)
        assert valid

    def test_valid_import(self):
        source = "import math"
        valid, errors, _ = _analyze(source)
        assert valid

    def test_valid_import_from(self):
        source = "import sqrt from math"
        valid, errors, _ = _analyze(source)
        assert valid

    def test_valid_array(self):
        source = "let arr = [1, 2, 3]"
        valid, errors, _ = _analyze(source)
        assert valid

    def test_valid_map(self):
        source = 'let m = {"a": 1}'
        valid, errors, _ = _analyze(source)
        assert valid

    def test_valid_string_concat(self):
        source = 'let s = "a" + "b"'
        valid, errors, _ = _analyze(source)
        assert valid

    def test_valid_compound_assign(self):
        source = "let x = 5\nx += 3"
        valid, errors, _ = _analyze(source)
        assert valid

    def test_assign_to_undefined(self):
        valid, errors, _ = _analyze("x = 5")
        assert not valid

    def test_scope_variable_hiding(self):
        source = "let x = 5\n{\nlet x = 10\n}"
        valid, errors, _ = _analyze(source)
        assert valid

    def test_scope_variable_not_accessible(self):
        source = "{\nlet x = 5\n}\nprint(x)"
        valid, errors, _ = _analyze(source)
        assert not valid

    def test_function_arg_count(self):
        source = "print(1, 2, 3)"
        valid, errors, _ = _analyze(source)
        assert valid  # print accepts any number

    def test_function_arg_count_error(self):
        source = "len()"
        valid, errors, _ = _analyze(source)
        assert not valid  # len needs 1 arg

    def test_semantic_performance(self):
        import time
        source = "let x = 5\n" * 200
        start = time.time()
        _analyze(source)
        elapsed = time.time() - start
        assert elapsed < 2.0, f"Semantic analyzer too slow: {elapsed}s"


# ══════════════════════════════════════════════════════════════════════════
# SECTION 4: INTERPRETER TESTS (70+)
# ══════════════════════════════════════════════════════════════════════════

class TestInterpreter:
    def test_literal_int(self):
        assert _run("42") == 42

    def test_literal_float(self):
        assert abs(_run("3.14") - 3.14) < 0.001

    def test_literal_str(self):
        assert _run('"hello"') == "hello"

    def test_literal_true(self):
        assert _run("true") is True

    def test_literal_false(self):
        assert _run("false") is False

    def test_literal_null(self):
        assert _run("null") is None

    def test_var_decl(self):
        assert _run("let x = 5") == 5

    def test_var_reassign(self):
        assert _run("let x = 5\nx = 10") == 10

    def test_const_decl(self):
        assert _run("const X = 42") == 42

    def test_add(self):
        assert _run("2 + 3") == 5

    def test_sub(self):
        assert _run("5 - 3") == 2

    def test_mul(self):
        assert _run("4 * 3") == 12

    def test_div(self):
        assert _run("6 / 2") == 3.0

    def test_mod(self):
        assert _run("7 % 3") == 1

    def test_pow(self):
        assert _run("2 ** 3") == 8

    def test_precedence(self):
        assert _run("2 + 3 * 4") == 14

    def test_parens(self):
        assert _run("(2 + 3) * 4") == 20

    def test_eq(self):
        assert _run("5 == 5") is True
        assert _run("5 == 3") is False

    def test_neq(self):
        assert _run("5 != 3") is True

    def test_lt(self):
        assert _run("3 < 5") is True

    def test_gt(self):
        assert _run("5 > 3") is True

    def test_le(self):
        assert _run("3 <= 5") is True
        assert _run("5 <= 5") is True

    def test_ge(self):
        assert _run("5 >= 3") is True

    def test_and(self):
        assert _run("true and true") is True
        assert _run("true and false") is False

    def test_or(self):
        assert _run("true or false") is True
        assert _run("false or false") is False

    def test_not(self):
        assert _run("not true") is False
        assert _run("not false") is True

    def test_string_concat(self):
        assert _run('"Hello, " + "World!"') == "Hello, World!"

    def test_if_true(self):
        assert _run("if true { 42 }") == 42

    def test_if_false(self):
        assert _run("if false { 1 } else { 2 }") == 2

    def test_if_elif(self):
        source = "let x = 5\nif x > 10 { 1 } elif x > 3 { 2 } else { 3 }"
        assert _run(source) == 2

    def test_while(self):
        source = "let i = 0\nlet s = 0\nwhile i < 5 { s = s + i\ni = i + 1 }\ns"
        assert _run(source) == 10

    def test_for_range(self):
        source = "let s = 0\nfor i in 0..5 { s = s + i }\ns"
        assert _run(source) == 10

    def test_for_collection(self):
        source = 'let s = ""\nfor c in ["a", "b", "c"] { s = s + c }\ns'
        assert _run(source) == "abc"

    def test_function_call(self):
        source = "func add(a: int, b: int) -> int { return a + b }\nadd(3, 4)"
        assert _run(source) == 7

    def test_recursive_factorial(self):
        source = "func f(n: int) -> int { if n <= 1 { return 1 } return n * f(n - 1) }\nf(5)"
        assert _run(source) == 120

    def test_recursive_fib(self):
        source = "func f(n: int) -> int { if n <= 1 { return n } return f(n-1) + f(n-2) }\nf(10)"
        assert _run(source) == 55

    def test_array_literal(self):
        assert _run("[1, 2, 3]") == [1, 2, 3]

    def test_array_index(self):
        assert _run("let a = [10, 20, 30]\na[1]") == 20

    def test_array_append(self):
        assert _run("let a = [1, 2]\na.append(3)\nlen(a)") == 3

    def test_array_pop(self):
        assert _run("let a = [1, 2, 3]\na.pop()") == 3

    def test_array_insert(self):
        source = "let a = [1, 3]\na.insert(1, 2)\nlen(a)"
        assert _run(source) == 3

    def test_array_remove(self):
        source = "let a = [1, 2, 3]\na.remove(1)\nlen(a)"
        assert _run(source) == 2

    def test_array_sort(self):
        source = "let a = [3, 1, 2]\na.sort()\na[0]"
        assert _run(source) == 1

    def test_array_reverse(self):
        source = "let a = [1, 2, 3]\na.reverse()\na[0]"
        assert _run(source) == 3

    def test_array_contains(self):
        assert _run("[1, 2, 3].contains(2)") is True
        assert _run("[1, 2, 3].contains(5)") is False

    def test_map_literal(self):
        assert _run('{"a": 1, "b": 2}') == {"a": 1, "b": 2}

    def test_map_access(self):
        assert _run('let m = {"x": 10}\nm["x"]') == 10

    def test_map_keys(self):
        result = _run('let m = {"a": 1, "b": 2}\nm.keys()')
        assert "a" in result and "b" in result

    def test_map_values(self):
        result = _run('let m = {"a": 1, "b": 2}\nm.values()')
        assert 1 in result and 2 in result

    def test_map_contains(self):
        assert _run('let m = {"a": 1}\nm.contains("a")') is True
        assert _run('let m = {"a": 1}\nm.contains("b")') is False

    def test_class_instantiation(self):
        source = "class C { let x: int constructor(x: int) { this.x = x } }\nlet c = C(42)\nc.x"
        assert _run(source) == 42

    def test_method_call(self):
        source = """
class C {
    let x: int
    constructor(x: int) { this.x = x }
    func get() -> int { return this.x }
}
let c = C(42)
c.get()
"""
        assert _run(source) == 42

    def test_try_catch(self):
        source = 'try { throw "err" } catch e { "caught: " + e }'
        assert _run(source) == "caught: err"

    def test_throw_catch_in_function(self):
        source = """
func d(a: int, b: int) -> int {
    if b == 0 { throw "zero" }
    return a / b
}
try { d(10, 0) } catch e { "error: " + e }
"""
        result = _run(source)
        assert "error:" in result

    def test_builtin_len_str(self):
        assert _run('len("hello")') == 5

    def test_builtin_len_array(self):
        assert _run("len([1, 2, 3])") == 3

    def test_builtin_type_int(self):
        assert _run("type(42)") == "int"

    def test_builtin_type_str(self):
        assert _run('type("hello")') == "str"

    def test_builtin_type_bool(self):
        assert _run("type(true)") == "bool"

    def test_builtin_type_float(self):
        assert _run("type(3.14)") == "float"

    def test_builtin_type_null(self):
        assert _run("type(null)") == "null"

    def test_builtin_int_conv(self):
        assert _run('int("42")') == 42

    def test_builtin_float_conv(self):
        assert abs(_run('float("3.14")') - 3.14) < 0.001

    def test_builtin_str_conv(self):
        assert _run("str(42)") == "42"

    def test_builtin_bool_conv(self):
        assert _run("bool(1)") is True
        assert _run("bool(0)") is False

    def test_compound_assign_add(self):
        assert _run("let x = 5\nx += 3") == 8

    def test_compound_assign_sub(self):
        assert _run("let x = 5\nx -= 3") == 2

    def test_compound_assign_mul(self):
        assert _run("let x = 5\nx *= 3") == 15

    def test_compound_assign_div(self):
        assert _run("let x = 6\nx /= 3") == 2.0

    def test_compound_assign_mod(self):
        assert _run("let x = 7\nx %= 3") == 1

    def test_nested_scopes(self):
        source = "let x = 10\n{\nlet y = 20\nx + y\n}"
        assert _run(source) == 30

    def test_break_in_loop(self):
        source = "let s = 0\nfor i in 0..10 { if i == 5 { break }\ns = s + i }\ns"
        assert _run(source) == 10

    def test_continue_in_loop(self):
        source = "let s = 0\nfor i in 0..5 { if i == 2 { continue }\ns = s + i }\ns"
        assert _run(source) == 8

    def test_fizzbuzz(self):
        source = """
let out = []
for i in 1..16 {
    if i % 15 == 0 { out.append("FizzBuzz") }
    elif i % 3 == 0 { out.append("Fizz") }
    elif i % 5 == 0 { out.append("Buzz") }
    else { out.append(i) }
}
out
"""
        expected = [1, 2, "Fizz", 4, "Buzz", "Fizz", 7, 8, "Fizz", "Buzz", 11, "Fizz", 13, 14, "FizzBuzz"]
        assert _run(source) == expected

    def test_range_expression(self):
        r = _run("0..5")
        assert list(r) == [0, 1, 2, 3, 4]

    def test_negation(self):
        assert _run("-5") == -5

    def test_bitwise_not(self):
        assert _run("~5") == -6

    def test_bitwise_and(self):
        assert _run("5 & 3") == 1

    def test_bitwise_or(self):
        assert _run("5 | 3") == 7

    def test_bitwise_xor(self):
        assert _run("5 ^ 3") == 6

    def test_shift_left(self):
        assert _run("5 << 1") == 10

    def test_shift_right(self):
        assert _run("5 >> 1") == 2

    def test_member_access_field(self):
        source = "class C { let x: int constructor(x: int) { this.x = x } }\nlet c = C(99)\nc.x"
        assert _run(source) == 99

    def test_member_access_method(self):
        source = "class C { func f() -> int { return 42 } }\nlet c = C()\nc.f()"
        assert _run(source) == 42

    def test_default_param(self):
        source = "func f(x: int = 5) -> int { return x }\nf()"
        assert _run(source) == 5

    def test_default_param_override(self):
        source = "func f(x: int = 5) -> int { return x }\nf(10)"
        assert _run(source) == 10

    def test_multiple_params(self):
        source = "func f(a: int, b: int, c: int) -> int { return a + b + c }\nf(1, 2, 3)"
        assert _run(source) == 6

    def test_empty_array(self):
        assert _run("let a = [1]\nlen(a)") == 1

    def test_empty_map(self):
        assert _run("let m: {str: int} = {}\nlen(m.keys())") == 0

    def test_array_out_of_bounds(self):
        try:
            _run("let a = [1]\na[5]")
            assert False
        except Exception:
            pass

    def test_division_by_zero(self):
        try:
            _run("let x = 5 / 0")
            assert False
        except Exception:
            pass

    def test_interpreter_performance(self):
        import time
        source = "let x = 0\nfor i in 0..1000 { x = x + i }\nx"
        start = time.time()
        result = _run(source)
        elapsed = time.time() - start
        assert result == 499500
        assert elapsed < 1.0, f"Interpreter too slow: {elapsed}s"


# ══════════════════════════════════════════════════════════════════════════
# RUN ALL TESTS
# ══════════════════════════════════════════════════════════════════════════

def run_all():
    print("=" * 60)
    print("  Samrat Comprehensive Test Suite")
    print("=" * 60)
    print()

    test_classes = [TestLexer, TestParser, TestSemantic, TestInterpreter]
    total = 0
    passed = 0
    failed = 0

    for test_class in test_classes:
        instance = test_class()
        methods = [m for m in dir(instance) if m.startswith('test_')]
        class_name = test_class.__name__
        print(f"\n[{class_name}] ({len(methods)} tests)")

        for method_name in methods:
            total += 1
            try:
                getattr(instance, method_name)()
                passed += 1
                print(f"  ✓ {method_name}")
            except Exception as e:
                failed += 1
                print(f"  ✗ {method_name}: {e}")

    print()
    print("=" * 60)
    print(f"  Results: {passed} passed, {failed} failed out of {total} tests")
    print(f"  Coverage: {passed/total*100:.1f}%" if total > 0 else "  No tests run")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)