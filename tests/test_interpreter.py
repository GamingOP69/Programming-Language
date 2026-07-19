"""Tests for the Samrat Interpreter."""
import sys
import os
import io
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from lexer import Lexer
from parser import Parser
from semantic import SemanticAnalyzer
from interpreter import Interpreter


def _run(source: str):
    """Helper: tokenize, parse, analyze, and interpret source code."""
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    analyzer = SemanticAnalyzer()
    if not analyzer.analyze(ast):
        errors = analyzer.get_errors()
        raise RuntimeError(f"Semantic errors: {[str(e) for e in errors]}")
    interpreter = Interpreter()
    return interpreter.interpret(ast)


def test_literal_integer():
    result = _run("42")
    assert result == 42
    print("  ✓ test_literal_integer")


def test_literal_float():
    result = _run("3.14")
    assert abs(result - 3.14) < 0.001
    print("  ✓ test_literal_float")


def test_literal_string():
    result = _run('"hello"')
    assert result == "hello"
    print("  ✓ test_literal_string")


def test_literal_bool():
    result = _run("true")
    assert result is True
    result2 = _run("false")
    assert result2 is False
    print("  ✓ test_literal_bool")


def test_literal_null():
    result = _run("null")
    assert result is None
    print("  ✓ test_literal_null")


def test_variable_declaration():
    result = _run("let x = 5")
    assert result == 5
    print("  ✓ test_variable_declaration")


def test_variable_reassignment():
    result = _run("let x = 5\nx = 10")
    assert result == 10
    print("  ✓ test_variable_reassignment")


def test_arithmetic():
    result = _run("2 + 3 * 4")
    assert result == 14  # Precedence: 3*4=12, 2+12=14
    print("  ✓ test_arithmetic")


def test_arithmetic_with_parens():
    result = _run("(2 + 3) * 4")
    assert result == 20
    print("  ✓ test_arithmetic_with_parens")


def test_comparison():
    result = _run("5 > 3")
    assert result is True
    result2 = _run("5 < 3")
    assert result2 is False
    print("  ✓ test_comparison")


def test_equality():
    result = _run("5 == 5")
    assert result is True
    result2 = _run("5 != 5")
    assert result2 is False
    print("  ✓ test_equality")


def test_logical_and():
    result = _run("true and true")
    assert result is True
    result2 = _run("true and false")
    assert result2 is False
    print("  ✓ test_logical_and")


def test_logical_or():
    result = _run("true or false")
    assert result is True
    result2 = _run("false or false")
    assert result2 is False
    print("  ✓ test_logical_or")


def test_logical_not():
    result = _run("not true")
    assert result is False
    result2 = _run("not false")
    assert result2 is True
    print("  ✓ test_logical_not")


def test_string_concatenation():
    result = _run('"Hello, " + "World!"')
    assert result == "Hello, World!"
    print("  ✓ test_string_concatenation")


def test_if_true():
    result = _run("""
if true {
    let x = 42
    x
}
""")
    assert result == 42
    print("  ✓ test_if_true")


def test_if_else():
    result = _run("""
if false {
    1
} else {
    2
}
""")
    assert result == 2
    print("  ✓ test_if_else")


def test_if_elif_else():
    result = _run("""
let x = 5
if x > 10 {
    1
} elif x > 3 {
    2
} else {
    3
}
""")
    assert result == 2
    print("  ✓ test_if_elif_else")


def test_while_loop():
    result = _run("""
let i = 0
let sum = 0
while i < 5 {
    sum = sum + i
    i = i + 1
}
sum
""")
    assert result == 10  # 0+1+2+3+4
    print("  ✓ test_while_loop")


def test_for_range_loop():
    result = _run("""
let sum = 0
for i in 0..5 {
    sum = sum + i
}
sum
""")
    assert result == 10  # 0+1+2+3+4
    print("  ✓ test_for_range_loop")


def test_function_call():
    result = _run("""
func add(a: int, b: int) -> int {
    return a + b
}
add(3, 4)
""")
    assert result == 7
    print("  ✓ test_function_call")


def test_recursive_factorial():
    result = _run("""
func factorial(n: int) -> int {
    if n <= 1 {
        return 1
    }
    return n * factorial(n - 1)
}
factorial(5)
""")
    assert result == 120
    print("  ✓ test_recursive_factorial")


def test_recursive_fibonacci():
    result = _run("""
func fib(n: int) -> int {
    if n <= 1 {
        return n
    }
    return fib(n - 1) + fib(n - 2)
}
fib(10)
""")
    assert result == 55
    print("  ✓ test_recursive_fibonacci")


def test_array_literal():
    result = _run("[1, 2, 3]")
    assert result == [1, 2, 3]
    print("  ✓ test_array_literal")


def test_array_index():
    result = _run("""
let arr = [10, 20, 30]
arr[1]
""")
    assert result == 20
    print("  ✓ test_array_index")


def test_array_append():
    result = _run("""
let arr = [1, 2, 3]
arr.append(4)
len(arr)
""")
    assert result == 4
    print("  ✓ test_array_append")


def test_array_pop():
    result = _run("""
let arr = [1, 2, 3]
arr.pop()
""")
    assert result == 3
    print("  ✓ test_array_pop")


def test_map_literal():
    result = _run('{"a": 1, "b": 2}')
    assert result == {"a": 1, "b": 2}
    print("  ✓ test_map_literal")


def test_map_access():
    result = _run("""
let m = {"x": 10, "y": 20}
m["x"]
""")
    assert result == 10
    print("  ✓ test_map_access")


def test_class_instantiation():
    result = _run("""
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
let p = Person("Alice", 30)
p.name
""")
    assert result == "Alice"
    print("  ✓ test_class_instantiation")


def test_method_call():
    result = _run("""
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
let p = Person("Alice", 30)
p.greet()
""")
    assert result == "Hello, Alice"
    print("  ✓ test_method_call")


def test_break_in_loop():
    result = _run("""
let sum = 0
for i in 0..10 {
    if i == 5 {
        break
    }
    sum = sum + i
}
sum
""")
    assert result == 10  # 0+1+2+3+4
    print("  ✓ test_break_in_loop")


def test_continue_in_loop():
    result = _run("""
let sum = 0
for i in 0..5 {
    if i == 2 {
        continue
    }
    sum = sum + i
}
sum
""")
    assert result == 8  # 0+1+3+4
    print("  ✓ test_continue_in_loop")


def test_nested_scopes():
    result = _run("""
let x = 10
{
    let y = 20
    x + y
}
""")
    assert result == 30
    print("  ✓ test_nested_scopes")


def test_compound_assignment():
    result = _run("""
let x = 10
x += 5
x
""")
    assert result == 15
    print("  ✓ test_compound_assignment")


def test_range_expression():
    result = _run("0..5")
    assert result == range(0, 5)
    print("  ✓ test_range_expression")


def test_builtin_len():
    result = _run('len("hello")')
    assert result == 5
    print("  ✓ test_builtin_len")


def test_builtin_type():
    result = _run("type(42)")
    assert result == "int"
    print("  ✓ test_builtin_type")


def test_builtin_str_conversion():
    result = _run("str(42)")
    assert result == "42"
    print("  ✓ test_builtin_str_conversion")


def test_builtin_int_conversion():
    result = _run('int("42")')
    assert result == 42
    print("  ✓ test_builtin_int_conversion")


def test_builtin_float_conversion():
    result = _run('float("3.14")')
    assert abs(result - 3.14) < 0.001
    print("  ✓ test_builtin_float_conversion")


def test_builtin_bool_conversion():
    result = _run("bool(1)")
    assert result is True
    result2 = _run("bool(0)")
    assert result2 is False
    print("  ✓ test_builtin_bool_conversion")


def test_throw_and_catch():
    result = _run("""
try {
    throw "error occurred"
} catch err {
    "caught: " + err
}
""")
    assert result == "caught: error occurred"
    print("  ✓ test_throw_and_catch")


def test_fizzbuzz():
    """Test a complete FizzBuzz program."""
    result = _run("""
let output = []
for i in 1..16 {
    if i % 15 == 0 {
        output.append("FizzBuzz")
    } elif i % 3 == 0 {
        output.append("Fizz")
    } elif i % 5 == 0 {
        output.append("Buzz")
    } else {
        output.append(i)
    }
}
output
""")
    expected = [1, 2, "Fizz", 4, "Buzz", "Fizz", 7, 8, "Fizz", "Buzz", 11, "Fizz", 13, 14, "FizzBuzz"]
    assert result == expected, f"Expected {expected}, got {result}"
    print("  ✓ test_fizzbuzz")


def test_hello_world():
    """Test that print works (capture stdout)."""
    import io
    from contextlib import redirect_stdout
    f = io.StringIO()
    with redirect_stdout(f):
        _run('print("Hello, World!")')
    output = f.getvalue().strip()
    assert output == "Hello, World!"
    print("  ✓ test_hello_world")


def run_all_tests():
    print("Running Interpreter Tests...\n")
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