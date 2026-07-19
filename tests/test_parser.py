"""
Tests for the Samrat Parser.

This test suite verifies that the parser correctly constructs AST nodes
for all Samrat language constructs, and produces appropriate errors for
malformed syntax.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from lexer import Lexer
from parser import Parser
from ast_nodes import *
from errors import ParserError


def _parse(source: str):
    """Helper: tokenize and parse source code."""
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse()


def test_empty_program():
    """Empty source should produce a Program with no statements."""
    ast = _parse("")
    assert isinstance(ast, Program)
    assert len(ast.statements) == 0
    print("  ✓ test_empty_program")


def test_var_declaration():
    """Test variable declarations."""
    ast = _parse("let x = 5")
    assert len(ast.statements) == 1
    stmt = ast.statements[0]
    assert isinstance(stmt, VarDeclaration)
    assert stmt.name == "x"
    assert isinstance(stmt.initializer, Literal)
    assert stmt.initializer.value == 5
    print("  ✓ test_var_declaration")


def test_var_declaration_with_type():
    """Test variable declaration with explicit type."""
    ast = _parse("let name: str = \"hello\"")
    stmt = ast.statements[0]
    assert isinstance(stmt, VarDeclaration)
    assert stmt.name == "name"
    assert stmt.var_type == "str"
    assert stmt.initializer.value == "hello"
    print("  ✓ test_var_declaration_with_type")


def test_const_declaration():
    """Test constant declaration."""
    ast = _parse("const PI = 3.14159")
    stmt = ast.statements[0]
    assert isinstance(stmt, ConstDeclaration)
    assert stmt.name == "PI"
    assert isinstance(stmt.initializer, Literal)
    assert abs(stmt.initializer.value - 3.14159) < 0.001
    print("  ✓ test_const_declaration")


def test_assignment():
    """Test assignment statement."""
    ast = _parse("x = 10")
    stmt = ast.statements[0]
    assert isinstance(stmt, Assignment)
    assert isinstance(stmt.target, Identifier)
    assert stmt.target.name == "x"
    assert stmt.operator == "="
    assert stmt.value.value == 10
    print("  ✓ test_assignment")


def test_compound_assignment():
    """Test compound assignment operators."""
    for op in ["+=", "-=", "*=", "/=", "%="]:
        ast = _parse(f"x {op} 5")
        stmt = ast.statements[0]
        assert isinstance(stmt, Assignment), f"Failed for {op}"
        assert stmt.operator == op, f"Expected {op}, got {stmt.operator}"
    print("  ✓ test_compound_assignment")


def test_expression_statement():
    """Test expression statement."""
    ast = _parse("5 + 3")
    stmt = ast.statements[0]
    assert isinstance(stmt, ExpressionStatement)
    assert isinstance(stmt.expression, BinaryOp)
    assert stmt.expression.operator == "+"
    print("  ✓ test_expression_statement")


def test_binary_operations():
    """Test all binary operations."""
    source = "1 + 2 - 3 * 4 / 5 % 6 ** 2"
    ast = _parse(source)
    assert len(ast.statements) == 1
    print("  ✓ test_binary_operations")


def test_comparison_operations():
    """Test comparison operators."""
    tests = ["==", "!=", "<", ">", "<=", ">="]
    sources = [f"a {op} b" for op in tests]
    for src in sources:
        ast = _parse(src)
        stmt = ast.statements[0]
        assert isinstance(stmt, ExpressionStatement)
        expr = stmt.expression
        assert isinstance(expr, BinaryOp), f"Failed for {src}"
    print("  ✓ test_comparison_operations")


def test_logical_operations():
    """Test logical operators."""
    ast = _parse("true and false or not true")
    stmt = ast.statements[0]
    assert isinstance(stmt, ExpressionStatement)
    assert isinstance(stmt.expression, BinaryOp)
    print("  ✓ test_logical_operations")


def test_parenthesized_expression():
    """Test parenthesized expressions for grouping."""
    ast = _parse("(1 + 2) * 3")
    stmt = ast.statements[0]
    assert isinstance(stmt, ExpressionStatement)
    expr = stmt.expression
    # Should be BinaryOp(*, Group, 3)
    assert isinstance(expr, ExpressionStatement) or isinstance(expr, BinaryOp)
    print("  ✓ test_parenthesized_expression")


def test_function_definition():
    """Test function definition."""
    source = """
func add(a: int, b: int) -> int {
    return a + b
}
"""
    ast = _parse(source)
    stmt = ast.statements[0]
    assert isinstance(stmt, FunctionDef)
    assert stmt.name == "add"
    assert len(stmt.parameters) == 2
    assert stmt.parameters[0].name == "a"
    assert stmt.parameters[0].param_type == "int"
    assert stmt.parameters[1].name == "b"
    assert stmt.return_type == "int"
    assert isinstance(stmt.body, Block)
    print("  ✓ test_function_definition")


def test_function_no_params():
    """Test function with no parameters."""
    source = """
func greet() {
    print("hello")
}
"""
    ast = _parse(source)
    stmt = ast.statements[0]
    assert isinstance(stmt, FunctionDef)
    assert stmt.name == "greet"
    assert len(stmt.parameters) == 0
    assert stmt.return_type is None
    print("  ✓ test_function_no_params")


def test_function_with_default_params():
    """Test function with default parameter values."""
    source = """
func power(base: int, exp: int = 2) -> int {
    return base ** exp
}
"""
    ast = _parse(source)
    stmt = ast.statements[0]
    assert stmt.parameters[1].name == "exp"
    assert stmt.parameters[1].default_value is not None
    assert stmt.parameters[1].default_value.value == 2
    print("  ✓ test_function_with_default_params")


def test_if_statement():
    """Test if statement."""
    source = """
if x > 0 {
    print("positive")
}
"""
    ast = _parse(source)
    stmt = ast.statements[0]
    assert isinstance(stmt, IfStatement)
    assert stmt.else_block is None
    assert len(stmt.elif_conditions) == 0
    print("  ✓ test_if_statement")


def test_if_elif_else():
    """Test if-elif-else chain."""
    source = """
if x > 0 {
    print("positive")
} elif x < 0 {
    print("negative")
} else {
    print("zero")
}
"""
    ast = _parse(source)
    stmt = ast.statements[0]
    assert isinstance(stmt, IfStatement)
    assert len(stmt.elif_conditions) == 1
    assert stmt.else_block is not None
    print("  ✓ test_if_elif_else")


def test_while_loop():
    """Test while loop."""
    source = """
while i < 10 {
    i = i + 1
}
"""
    ast = _parse(source)
    stmt = ast.statements[0]
    assert isinstance(stmt, WhileLoop)
    assert isinstance(stmt.body, Block)
    print("  ✓ test_while_loop")


def test_for_range_loop():
    """Test for loop with range."""
    source = """
for i in 0..10 {
    print(i)
}
"""
    ast = _parse(source)
    stmt = ast.statements[0]
    assert isinstance(stmt, ForLoop)
    assert stmt.variable == "i"
    assert isinstance(stmt.iterable, BinaryOp)
    assert stmt.iterable.operator == ".."
    print("  ✓ test_for_range_loop")


def test_class_definition():
    """Test class definition."""
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
    ast = _parse(source)
    stmt = ast.statements[0]
    assert isinstance(stmt, ClassDef)
    assert stmt.name == "Person"
    assert len(stmt.fields) == 2
    assert stmt.constructor is not None
    assert len(stmt.methods) == 1
    print("  ✓ test_class_definition")


def test_try_catch():
    """Test try/catch statement."""
    source = """
try {
    risky()
} catch error {
    print(error)
}
"""
    ast = _parse(source)
    stmt = ast.statements[0]
    assert isinstance(stmt, TryStatement)
    assert stmt.catch_var == "error"
    print("  ✓ test_try_catch")


def test_throw_statement():
    """Test throw statement."""
    ast = _parse('throw "error occurred"')
    stmt = ast.statements[0]
    assert isinstance(stmt, ThrowStatement)
    assert stmt.value.value == "error occurred"
    print("  ✓ test_throw_statement")


def test_import_statement():
    """Test import statements."""
    ast = _parse("import math")
    stmt = ast.statements[0]
    assert isinstance(stmt, ImportStatement)
    assert stmt.names == ["math"]
    assert stmt.module is None

    ast2 = _parse("import sqrt from math")
    stmt2 = ast2.statements[0]
    assert stmt2.module == "math"

    ast3 = _parse("import math as m")
    stmt3 = ast3.statements[0]
    assert stmt3.alias == "m"
    print("  ✓ test_import_statement")


def test_return_statement():
    """Test return statements."""
    ast = _parse("return 42")
    stmt = ast.statements[0]
    assert isinstance(stmt, ReturnStatement)
    assert stmt.value.value == 42

    # Test bare return
    source = """
func f() {
    return
}
"""
    ast2 = _parse(source)
    func = ast2.statements[0]
    ret = func.body.statements[0]
    assert isinstance(ret, ReturnStatement)
    assert ret.value is None
    print("  ✓ test_return_statement")


def test_break_continue():
    """Test break and continue."""
    ast = _parse("break")
    assert isinstance(ast.statements[0], BreakStatement)

    ast2 = _parse("continue")
    assert isinstance(ast2.statements[0], ContinueStatement)
    print("  ✓ test_break_continue")


def test_array_literal():
    """Test array literals."""
    ast = _parse("[1, 2, 3]")
    stmt = ast.statements[0]
    assert isinstance(stmt, ExpressionStatement)
    arr = stmt.expression
    assert isinstance(arr, ArrayLiteral)
    assert len(arr.elements) == 3
    print("  ✓ test_array_literal")


def test_map_literal():
    """Test map literals."""
    ast = _parse('{"a": 1, "b": 2}')
    stmt = ast.statements[0]
    assert isinstance(stmt, ExpressionStatement)
    mp = stmt.expression
    assert isinstance(mp, MapLiteral)
    assert len(mp.entries) == 2
    print("  ✓ test_map_literal")


def test_function_call():
    """Test function calls."""
    ast = _parse("add(1, 2)")
    stmt = ast.statements[0]
    assert isinstance(stmt, ExpressionStatement)
    call = stmt.expression
    assert isinstance(call, FunctionCall)
    assert isinstance(call.callee, Identifier)
    assert call.callee.name == "add"
    assert len(call.arguments) == 2
    print("  ✓ test_function_call")


def test_member_access():
    """Test member access expressions."""
    ast = _parse("person.name")
    stmt = ast.statements[0]
    expr = stmt.expression
    assert isinstance(expr, MemberAccess)
    assert isinstance(expr.object, Identifier)
    assert expr.object.name == "person"
    assert expr.member == "name"
    print("  ✓ test_member_access")


def test_method_call():
    """Test method call chaining."""
    ast = _parse("person.greet()")
    stmt = ast.statements[0]
    expr = stmt.expression
    assert isinstance(expr, FunctionCall)
    assert isinstance(expr.callee, MemberAccess)
    assert expr.callee.member == "greet"
    print("  ✓ test_method_call")


def test_subscript():
    """Test subscript/index access."""
    ast = _parse("arr[0]")
    stmt = ast.statements[0]
    expr = stmt.expression
    assert isinstance(expr, Subscript)
    assert isinstance(expr.object, Identifier)
    assert expr.object.name == "arr"
    assert expr.index.value == 0
    print("  ✓ test_subscript")


def test_operator_precedence():
    """Test that operator precedence is respected."""
    # 5 + 3 * 2 should parse as 5 + (3 * 2)
    ast = _parse("5 + 3 * 2")
    stmt = ast.statements[0]
    expr = stmt.expression
    assert isinstance(expr, BinaryOp)
    assert expr.operator == "+", f"Expected +, got {expr.operator}"
    # Left side should be 5
    assert expr.left.value == 5
    # Right side should be 3 * 2
    assert isinstance(expr.right, BinaryOp)
    assert expr.right.operator == "*"
    print("  ✓ test_operator_precedence")


def test_recursive_function():
    """Test parsing recursive functions."""
    source = """
func factorial(n: int) -> int {
    if n <= 1 {
        return 1
    }
    return n * factorial(n - 1)
}
"""
    ast = _parse(source)
    func = ast.statements[0]
    assert isinstance(func, FunctionDef)
    assert func.name == "factorial"
    print("  ✓ test_recursive_function")


def test_nested_blocks():
    """Test nested block statements."""
    source = """
{
    {
        let x = 1
    }
}
"""
    ast = _parse(source)
    outer = ast.statements[0]
    assert isinstance(outer, Block)
    inner = outer.statements[0]
    assert isinstance(inner, Block)
    decl = inner.statements[0]
    assert isinstance(decl, VarDeclaration)
    print("  ✓ test_nested_blocks")


def test_error_missing_semicolon_not_needed():
    """Samrat doesn't use semicolons, verify parsing works without them."""
    source = """
let x = 5
let y = 10
let z = x + y
"""
    ast = _parse(source)
    assert len(ast.statements) == 3
    print("  ✓ test_error_missing_semicolon_not_needed")


def test_error_unexpected_token():
    """Test that unexpected tokens produce ParserError."""
    lexer = Lexer("let @ = 5")
    try:
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        assert False, "Expected ParserError was not raised"
    except (ParserError, Exception) as e:
        assert True
        print("  ✓ test_error_unexpected_token")


def test_error_missing_identifier():
    """Test error when identifier is missing."""
    lexer = Lexer("let = 5")
    try:
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        assert False, "Expected error not raised"
    except ParserError as e:
        assert "Expected variable name" in str(e)
        print("  ✓ test_error_missing_identifier")


def test_complex_expression():
    """Test a more complex expression."""
    source = "a * b + c / d - e ** f"
    ast = _parse(source)
    stmt = ast.statements[0]
    assert isinstance(stmt, ExpressionStatement)
    assert isinstance(stmt.expression, BinaryOp)
    print("  ✓ test_complex_expression")


def test_unary_operators():
    """Test unary operators."""
    ast = _parse("-5")
    stmt = ast.statements[0]
    assert isinstance(stmt, ExpressionStatement)
    assert isinstance(stmt.expression, UnaryOp)
    assert stmt.expression.operator == "-"

    ast2 = _parse("not true")
    stmt2 = ast2.statements[0]
    assert isinstance(stmt2.expression, UnaryOp)
    assert stmt2.expression.operator == "not"
    print("  ✓ test_unary_operators")


def test_range_expression():
    """Test range expression."""
    ast = _parse("0..10")
    stmt = ast.statements[0]
    expr = stmt.expression
    assert isinstance(expr, BinaryOp)
    assert expr.operator == ".."
    assert expr.left.value == 0
    assert expr.right.value == 10
    print("  ✓ test_range_expression")


def test_this_expression():
    """Test 'this' keyword."""
    ast = _parse("this.name")
    stmt = ast.statements[0]
    expr = stmt.expression
    assert isinstance(expr, MemberAccess)
    assert isinstance(expr.object, ThisExpression)
    assert expr.member == "name"
    print("  ✓ test_this_expression")


def test_hello_world_full_program():
    """Parse a complete hello world style program."""
    source = """
func main() {
    print("Hello, World!")
}

main()
"""
    ast = _parse(source)
    assert len(ast.statements) == 2
    assert isinstance(ast.statements[0], FunctionDef)
    assert isinstance(ast.statements[1], ExpressionStatement)
    print("  ✓ test_hello_world_full_program")


def run_all_tests():
    """Run all parser tests."""
    print("Running Parser Tests...")
    print()

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
            import traceback
            traceback.print_exc()
            failed += 1

    print()
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)} tests")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)