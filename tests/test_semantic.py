"""Tests for the Samrat Semantic Analyzer."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from lexer import Lexer
from parser import Parser
from semantic import SemanticAnalyzer


def _analyze(source: str):
    """Helper: tokenize, parse, and analyze source code."""
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    analyzer = SemanticAnalyzer()
    valid = analyzer.analyze(ast)
    return valid, analyzer.get_errors(), ast


def test_valid_program():
    """A simple valid program should pass semantic analysis."""
    valid, errors, _ = _analyze("let x = 5")
    assert valid, f"Expected valid, got errors: {errors}"
    print("  ✓ test_valid_program")


def test_undefined_variable():
    """Using an undefined variable should produce an error."""
    valid, errors, _ = _analyze("print(x)")
    assert not valid, "Expected invalid"
    assert any("Undefined" in str(e) for e in errors)
    print("  ✓ test_undefined_variable")


def test_duplicate_variable():
    """Declaring the same variable twice in the same scope should error."""
    valid, errors, _ = _analyze("let x = 5\nlet x = 10")
    assert not valid
    assert any("already declared" in str(e) for e in errors)
    print("  ✓ test_duplicate_variable")


def test_reassign_constant():
    """Reassigning a constant should error."""
    valid, errors, _ = _analyze("const PI = 3.14\nPI = 2.71")
    assert not valid
    assert any("Cannot assign to constant" in str(e) for e in errors)
    print("  ✓ test_reassign_constant")


def test_type_mismatch():
    """Assigning wrong type should error."""
    valid, errors, _ = _analyze("let x: int = \"hello\"")
    assert not valid
    assert any("Type mismatch" in str(e) for e in errors)
    print("  ✓ test_type_mismatch")


def test_return_outside_function():
    """Return outside function should error."""
    valid, errors, _ = _analyze("return 5")
    assert not valid
    assert any("outside function" in str(e) for e in errors)
    print("  ✓ test_return_outside_function")


def test_break_outside_loop():
    """Break outside loop should error."""
    valid, errors, _ = _analyze("break")
    assert not valid
    assert any("outside loop" in str(e) for e in errors)
    print("  ✓ test_break_outside_loop")


def test_continue_outside_loop():
    """Continue outside loop should error."""
    valid, errors, _ = _analyze("continue")
    assert not valid
    assert any("outside loop" in str(e) for e in errors)
    print("  ✓ test_continue_outside_loop")


def test_valid_function():
    """A valid function should pass."""
    source = """
func add(a: int, b: int) -> int {
    return a + b
}
"""
    valid, errors, _ = _analyze(source)
    assert valid, f"Expected valid, got errors: {errors}"
    print("  ✓ test_valid_function")


def test_function_return_type_mismatch():
    """Returning wrong type from function should error."""
    source = """
func get_name() -> int {
    return "hello"
}
"""
    valid, errors, _ = _analyze(source)
    assert not valid
    assert any("Type mismatch" in str(e) for e in errors)
    print("  ✓ test_function_return_type_mismatch")


def test_if_condition_must_be_bool():
    """If condition must be bool."""
    valid, errors, _ = _analyze("if 5 { print(\"hi\") }")
    assert not valid
    assert any("must be bool" in str(e) for e in errors)
    print("  ✓ test_if_condition_must_be_bool")


def test_while_condition_must_be_bool():
    """While condition must be bool."""
    valid, errors, _ = _analyze("while 5 { print(\"hi\") }")
    assert not valid
    assert any("must be bool" in str(e) for e in errors)
    print("  ✓ test_while_condition_must_be_bool")


def test_this_outside_class():
    """'this' outside class should error."""
    valid, errors, _ = _analyze("print(this)")
    assert not valid
    assert any("'this' can only be used inside a class" in str(e) for e in errors)
    print("  ✓ test_this_outside_class")


def test_valid_class():
    """A valid class should pass."""
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
    valid, errors, _ = _analyze(source)
    assert valid, f"Expected valid, got errors: {errors}"
    print("  ✓ test_valid_class")


def test_valid_recursive_function():
    """Recursive functions should pass."""
    source = """
func factorial(n: int) -> int {
    if n <= 1 {
        return 1
    }
    return n * factorial(n - 1)
}
"""
    valid, errors, _ = _analyze(source)
    assert valid, f"Expected valid, got errors: {errors}"
    print("  ✓ test_valid_recursive_function")


def test_valid_nested_scopes():
    """Nested scopes should work correctly."""
    source = """
let x = 10
{
    let y = 20
    print(x)
    print(y)
}
"""
    valid, errors, _ = _analyze(source)
    assert valid, f"Expected valid, got errors: {errors}"
    print("  ✓ test_valid_nested_scopes")


def test_logical_operator_type_check():
    """Logical operators require bool operands."""
    valid, errors, _ = _analyze("5 and 3")
    assert not valid
    assert any("requires bool" in str(e) for e in errors)
    print("  ✓ test_logical_operator_type_check")


def test_bitwise_operator_type_check():
    """Bitwise operators require int operands."""
    valid, errors, _ = _analyze("true & false")
    assert not valid
    assert any("requires integer" in str(e) for e in errors)
    print("  ✓ test_bitwise_operator_type_check")


def test_string_concatenation():
    """String concatenation with + should work."""
    valid, errors, _ = _analyze('let x = "hello" + " world"')
    assert valid, f"Expected valid, got errors: {errors}"
    print("  ✓ test_string_concatenation")


def test_valid_try_catch():
    """Try/catch should pass."""
    source = """
try {
    let x = 5
} catch error {
    print(error)
}
"""
    valid, errors, _ = _analyze(source)
    assert valid, f"Expected valid, got errors: {errors}"
    print("  ✓ test_valid_try_catch")


def test_valid_for_loop():
    """For loop should pass."""
    source = """
for i in 0..10 {
    print(i)
}
"""
    valid, errors, _ = _analyze(source)
    assert valid, f"Expected valid, got errors: {errors}"
    print("  ✓ test_valid_for_loop")


def test_break_in_loop():
    """Break inside a loop should pass."""
    source = """
while true {
    break
}
"""
    valid, errors, _ = _analyze(source)
    assert valid, f"Expected valid, got errors: {errors}"
    print("  ✓ test_break_in_loop")


def test_continue_in_loop():
    """Continue inside a loop should pass."""
    source = """
for i in 0..10 {
    continue
}
"""
    valid, errors, _ = _analyze(source)
    assert valid, f"Expected valid, got errors: {errors}"
    print("  ✓ test_continue_in_loop")


def test_duplicate_function():
    """Duplicate function definition should error."""
    source = """
func foo() {}
func foo() {}
"""
    valid, errors, _ = _analyze(source)
    assert not valid
    assert any("already defined" in str(e) for e in errors)
    print("  ✓ test_duplicate_function")


def test_negate_non_numeric():
    """Negating a non-numeric value should error."""
    valid, errors, _ = _analyze('let x = -"hello"')
    assert not valid
    assert any("Cannot negate" in str(e) for e in errors)
    print("  ✓ test_negate_non_numeric")


def test_not_non_bool():
    """Using 'not' on non-bool should error."""
    valid, errors, _ = _analyze("not 5")
    assert not valid
    assert any("requires bool" in str(e) for e in errors)
    print("  ✓ test_not_non_bool")


def test_full_program_valid():
    """A complete valid program should pass."""
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
    valid, errors, _ = _analyze(source)
    assert valid, f"Expected valid, got errors: {errors}"
    print("  ✓ test_full_program_valid")


def run_all_tests():
    print("Running Semantic Analyzer Tests...\n")
    tests = [obj for name, obj in globals().items() if name.startswith('test_') and callable(obj)]
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
    print(f"\nResults: {passed} passed, {failed} failed out of {len(tests)} tests")
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)