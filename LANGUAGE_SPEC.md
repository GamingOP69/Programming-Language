# Samrat Programming Language — Language Specification

**Version:** 1.0.0 (Final)  
**Status:** Specification Frozen  
**Last Updated:** 2026-07-19

---

## Table of Contents

1. [Introduction & Philosophy](#1-introduction--philosophy)
2. [Version 1.0 Scope](#2-version-10-scope)
3. [Lexical Structure](#3-lexical-structure)
4. [Data Types](#4-data-types)
5. [Variables & Constants](#5-variables--constants)
6. [Operators](#6-operators)
7. [Expressions](#7-expressions)
8. [Statements](#8-statements)
9. [Functions](#9-functions)
10. [Control Flow](#10-control-flow)
11. [Classes & Objects](#11-classes--objects)
12. [Modules & Imports](#12-modules--imports)
13. [Error Handling](#13-error-handling)
14. [Built-in Functions](#14-built-in-functions)
15. [Standard Library](#15-standard-library)
16. [Formal Grammar](#16-formal-grammar)
17. [Example Programs](#17-example-programs)

---

## 1. Introduction & Philosophy

### 1.1 What is Samrat?

Samrat is a modern, general-purpose programming language designed for readability, simplicity, and power. It combines the clean, English-like syntax of Python with the expressiveness of systems languages like C++, Java, and Rust.

### 1.2 Design Principles

- **Readability over cleverness** — Code should be understandable at a glance. Explicit is better than implicit.
- **English-like syntax** — Keywords and constructs read like natural English sentences.
- **Consistency** — Similar constructs look and behave similarly. No surprises.
- **Strong static typing** — Catch type errors at compile time, not runtime.
- **Type inference** — Types are inferred when they are obvious. Annotations are optional.
- **Beginner-friendly** — Easy to learn, but powerful enough for real-world software.
- **Excellent error messages** — Every error shows: (a) what went wrong, (b) where (file:line:column), (c) the relevant source line with a caret pointer, and (d) a suggestion for how to fix it.
- **Cross-platform** — Runs on Windows, macOS, and Linux from a single codebase.
- **Minimal core** — The language is small and stable. Advanced features are added separately without breaking existing code.

### 1.3 Hello, World

```
print("Hello, World!")
```

---

## 2. Version 1.0 Scope

Samrat 1.0 includes only the following features. Everything else is deferred to future versions.

### Included in 1.0
- Variables (`let`) and constants (`const`) with block scoping
- Primitive types: `int`, `float`, `str`, `bool`, `null`
- Composite types: arrays `[type]`, maps `{keyType: valueType}`
- Functions with parameters, return types, default values, and recursion
- Control flow: `if`/`elif`/`else`, `while`, `for` over ranges and collections
- Classes with fields, constructor, and methods
- Error handling: `try`/`catch`/`throw`
- Module system: `import`/`from`/`as`
- File I/O via built-in functions
- Standard library: `math`, `string`, `time` modules (built-in, no file loading)
- Comments: `//` single-line, `/* */` multi-line (nestable)
- Built-in functions: `print`, `input`, `int`, `float`, `str`, `bool`, `type`, `len`, `range`

### Explicitly Excluded from 1.0 (Future)
- Generics, enums, interfaces/traits
- Pattern matching (reserved keywords: `match`, `case`, `default`)
- Lambda expressions / anonymous functions
- Async/await, concurrency
- Annotations / decorators
- Operator overloading
- Union types, nullable types
- Destructuring, slices, tuples
- Spread operator
- Compile-time execution / macros
- FFI (foreign function interface)
- Package manager

---

## 3. Lexical Structure

### 3.1 Character Set

Samrat source code is written in UTF-8 Unicode. The following characters are significant:

- Letters: `A-Z`, `a-z`, `_` (underscore)
- Digits: `0-9`
- Whitespace: space (0x20), tab (0x09), newline (0x0A), carriage return (0x0D)
- Operators and punctuation: see [Operators](#6-operators)

### 3.2 Comments

```
// This is a single-line comment.  It extends to the end of the line.

/* This is a
   multi-line comment. */
```

Comments are completely ignored by the lexer and do not appear in the token stream. Multi-line comments can be nested.

### 3.3 Identifiers

Identifiers name variables, constants, functions, classes, modules, and other program entities.

**Rules:**
- Must start with a letter (`a-z`, `A-Z`) or underscore (`_`)
- Subsequent characters can be letters, digits (`0-9`), or underscores
- Case-sensitive (`myVar` ≠ `myvar` ≠ `MyVar`)
- Cannot be a reserved keyword

**Valid identifiers:**
```
name           count          my_variable     _private
camelCase      PascalCase     value1          _temp
CONSTANT_NAME  is_valid       counter_100
```

**Invalid identifiers:**
```
1value       // ERROR: starts with digit
my-var       // ERROR: hyphen is an operator, not allowed in identifiers
class        // ERROR: reserved keyword
```

### 3.4 Keywords

The following identifiers are reserved keywords and cannot be used as identifiers. Keywords marked with `†` are reserved for future use and will cause a compile-time error if used in 1.0.

```
let         const       func        return
if          elif        else        while
for         in          break       continue
class       constructor this        new
true        false       null        and
or          not         import      from
as          try         catch       throw
int         float       str         bool
void        match†      case†       default†
```

### 3.5 Literals

#### Integer Literals
Integers are signed arbitrary-precision values.

| Format | Prefix | Example | Value |
|--------|--------|---------|-------|
| Decimal | — | `42` | 42 |
| Hexadecimal | `0x` or `0X` | `0xFF` | 255 |
| Binary | `0b` or `0B` | `0b1010` | 10 |
| Octal | `0o` or `0O` | `0o77` | 63 |

Underscores may be used as visual separators in any format: `1_000_000` = 1000000.

#### Float Literals
Floats are IEEE 754 double-precision values.

```
3.14      // Standard decimal
-0.5      // Negative float
1.0       // Whole number as float
2.5e10    // Scientific notation (2.5 × 10¹⁰)
1e-3      // Scientific notation (0.001)
```

A float literal requires at least one digit on both sides of the decimal point.

#### String Literals
Strings are sequences of Unicode characters enclosed in double quotes.

```
"Hello, World!"               // Simple string
"Line 1\nLine 2"              // Escape sequences
"Path: C:\\Users\\Name"       // Backslash escape
```

**Escape sequences:**

| Sequence | Meaning | Unicode |
|----------|---------|---------|
| `\n` | Newline | U+000A |
| `\t` | Tab | U+0009 |
| `\r` | Carriage return | U+000D |
| `\\` | Backslash | U+005C |
| `\"` | Double quote | U+0022 |
| `\0` | Null character | U+0000 |

Unrecognized escape sequences produce a compile-time warning and are treated as the literal characters following the backslash.

#### Boolean Literals
```
true
false
```

#### Null Literal
```
null
```

### 3.6 Operators and Punctuation

```
// Arithmetic
+     -     *     /     %     **

// Comparison
==    !=    <     >     <=    >=

// Assignment
=     +=    -=    *=    /=    %=

// Bitwise
&     |     ^     ~     <<    >>

// Member access and call
.     (     )     [     ]

// Other
,     :     ->    ..

// Braces for blocks and maps
{     }
```

Note: Samrat does **not** use `;` as a statement terminator. Statements are separated by newlines or blocks (`{}`). The `&&` and `||` operators are **not** used — use `and` and `or` instead.

---

## 4. Data Types

### 4.1 Primitive Types

| Type | Description | Values | Example |
|------|-------------|--------|---------|
| `int` | Signed integer (arbitrary precision) | `...`, `-2`, `-1`, `0`, `1`, `2`, `...` | `42`, `-17` |
| `float` | IEEE 754 double-precision float | ±1.7976×10³⁰⁸ to ±4.9407×10⁻³²⁴ | `3.14`, `-0.5` |
| `str` | UTF-8 Unicode string | Any valid UTF-8 text | `"hello"`, `"42"` |
| `bool` | Boolean | `true`, `false` | `true` |
| `null` | Null value (no type) | `null` | `null` |

### 4.2 Composite Types

#### Arrays

Arrays are zero-indexed, ordered, mutable collections of elements with the same type.

```
let numbers: [int] = [1, 2, 3, 4, 5]
let names: [str] = ["Alice", "Bob", "Charlie"]
let empty: [int] = []
```

**Access and mutation:**
```
let first = numbers[0]     // 1
numbers[1] = 10            // Mutate element at index 1
let length = len(numbers)  // 5
```

Out-of-bounds access raises a runtime error.

#### Maps

Maps are key-value collections. Keys must be of a hashable type (`int`, `str`, `bool`).

```
let scores: {str: int} = {"Alice": 95, "Bob": 87}
let empty_map: {str: int} = {}
```

**Access and mutation:**
```
let alice_score = scores["Alice"]   // 95
scores["Charlie"] = 92              // Add or update entry
```

Accessing a non-existent key raises a runtime error. Use `map.contains(key)` to check for key existence.

### 4.3 Type Annotations

Type annotations are optional. When omitted, the type is inferred from the initializer expression.

```
let name: str = "Samrat"     // Explicit type annotation
let age = 25                 // Inferred as int (from literal 25)
let price: float = 99.99     // Explicit type
let items = []               // ERROR: cannot infer type of empty array
let items: [int] = []        // OK: explicit type
```

Class field declarations always require a type annotation:

```
class Person {
    let name: str    // Required: no initializer to infer from
    let age: int     // Required
}
```

### 4.4 Type Conversion

Explicit type conversion is done via built-in function calls:

```
let x = int("42")       // str → int: 42
let y = str(42)         // int → str: "42"
let z = float("3.14")   // str → float: 3.14
let b = bool(1)         // int → bool: true
```

---

## 5. Variables & Constants

### 5.1 Variable Declaration (`let`)

Variables are declared with `let` and are mutable by default.

```
let name = "Samrat"
let count: int = 0
let price = 99.99

// Mutation
count = count + 1
name = "Samrat v2"
```

A variable without an initializer must have an explicit type annotation and defaults to the zero value for that type:

```
let ready: bool    // false
let count: int     // 0
let name: str      // ""
let items: [int]   // []
let data: {str: int}  // {}
```

### 5.2 Constant Declaration (`const`)

Constants are declared with `const` and cannot be reassigned after declaration. Constants must have an initializer.

```
const PI = 3.14159
const APP_NAME = "Samrat"

PI = 3.14    // COMPILE ERROR: Cannot reassign constant 'PI'
```

### 5.3 Scope

Variables and constants are block-scoped. A block is defined by `{ }`. Inner blocks can access outer scopes, but not vice versa.

```
let x = 10
{
    let y = 20
    print(x)   // 10 (outer scope accessible)
    print(y)   // 20
}
print(y)       // COMPILE ERROR: 'y' is not defined in this scope
```

Variables in the same scope cannot shadow function or class names, but can shadow variables from outer scopes.

---

## 6. Operators

### 6.1 Arithmetic Operators

| Operator | Description | Example | Result |
|----------|-------------|---------|--------|
| `+` | Addition | `5 + 3` | `8` |
| `-` | Subtraction | `5 - 3` | `2` |
| `*` | Multiplication | `5 * 3` | `15` |
| `/` | Float division | `5 / 2` | `2.5` |
| `%` | Integer modulo | `5 % 2` | `1` |
| `**` | Exponentiation | `2 ** 3` | `8` |

Integers promote to float when either operand in `/` is a float. The `%` operator requires integer operands.

### 6.2 Comparison Operators

| Operator | Description | Example | Result |
|----------|-------------|---------|--------|
| `==` | Equal to | `5 == 3` | `false` |
| `!=` | Not equal to | `5 != 3` | `true` |
| `<` | Less than | `5 < 3` | `false` |
| `>` | Greater than | `5 > 3` | `true` |
| `<=` | Less than or equal | `5 <= 3` | `false` |
| `>=` | Greater than or equal | `5 >= 3` | `true` |

Comparison operators work on `int`, `float`, `str`, and `bool`. Strings are compared lexicographically. Values of different types are never equal (even `int` and `float`).

### 6.3 Logical Operators

| Operator | Description | Example | Result |
|----------|-------------|---------|--------|
| `and` | Logical AND | `true and false` | `false` |
| `or` | Logical OR | `true or false` | `true` |
| `not` | Logical NOT | `not true` | `false` |

`and` and `or` short-circuit: the right operand is only evaluated if needed.

### 6.4 Assignment Operators

| Operator | Example | Equivalent to |
|----------|---------|---------------|
| `=` | `x = 5` | — |
| `+=` | `x += 3` | `x = x + 3` |
| `-=` | `x -= 3` | `x = x - 3` |
| `*=` | `x *= 3` | `x = x * 3` |
| `/=` | `x /= 3` | `x = x / 3` |
| `%=` | `x %= 3` | `x = x % 3` |

Compound assignments (`+=`, `-=`, etc.) are syntactic sugar. The left-hand side must be an assignable lvalue (variable, array element, or map entry).

### 6.5 Bitwise Operators

| Operator | Description | Example | Result |
|----------|-------------|---------|--------|
| `&` | Bitwise AND | `5 & 3` | `1` |
| `\|` | Bitwise OR | `5 \| 3` | `7` |
| `^` | Bitwise XOR | `5 ^ 3` | `6` |
| `~` | Bitwise NOT | `~5` | `-6` |
| `<<` | Left shift | `5 << 1` | `10` |
| `>>` | Right shift (arithmetic) | `5 >> 1` | `2` |

Bitwise operators require integer operands.

### 6.6 Other Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `.` | Member access | `person.name` |
| `[]` | Subscript / index | `arr[0]`, `map["key"]` |
| `()` | Function call | `add(1, 2)` |
| `..` | Exclusive range | `0..10` (yields 0, 1, ..., 9) |
| `->` | Return type arrow | `func f() -> int` |

### 6.7 Operator Precedence and Associativity

| Level | Category | Operators | Associativity |
|-------|----------|-----------|---------------|
| 1 (highest) | Postfix | `()` `[]` `.` | Left-to-right |
| 2 | Unary | `not` `-` `~` | Right-to-left |
| 3 | Exponentiation | `**` | Right-to-left |
| 4 | Multiplicative | `*` `/` `%` | Left-to-right |
| 5 | Additive | `+` `-` | Left-to-right |
| 6 | Shift | `<<` `>>` | Left-to-right |
| 7 | Bitwise AND | `&` | Left-to-right |
| 8 | Bitwise XOR | `^` | Left-to-right |
| 9 | Bitwise OR | `\|` | Left-to-right |
| 10 | Relational | `<` `>` `<=` `>=` | Left-to-right |
| 11 | Equality | `==` `!=` | Left-to-right |
| 12 | Logical AND | `and` | Left-to-right |
| 13 | Logical OR | `or` | Left-to-right |
| 14 (lowest) | Assignment | `=` `+=` `-=` `*=` `/=` `%=` | Right-to-left |
| 15 | Range | `..` | Left-to-right |

This table is consistent with the Formal Grammar in section 16.

---

## 7. Expressions

### 7.1 Literal Expressions

```
42          // integer
3.14        // float
"hello"     // string
true        // boolean
null        // null
```

### 7.2 Identifier Expressions

```
name        // variable reference
PI          // constant reference
add         // function reference
```

### 7.3 Binary Expressions

```
5 + 3       // addition
x * y       // multiplication
a and b     // logical AND
x == y      // equality comparison
0..10       // range expression
```

### 7.4 Unary Expressions

```
-x          // negation
not flag    // logical NOT
~bits       // bitwise NOT
```

### 7.5 Grouping Expressions

Parentheses override default precedence:

```
(5 + 3) * 2     // 16 (without parens: 5 + 3 * 2 = 11)
```

### 7.6 Member Access Expressions

```
person.name        // Field access
person.greet()     // Method call
```

### 7.7 Subscript Expressions

```
arr[0]             // Array element access
map["key"]         // Map value access
```

### 7.8 Function Call Expressions

```
add(1, 2)          // Call with two arguments
print("Hello")     // Call with one argument
f()                // Call with zero arguments
```

### 7.9 Range Expressions

```
0..10              // Sequence: 0, 1, 2, ..., 9
start..end         // start inclusive, end exclusive
```

---

## 8. Statements

### 8.1 Expression Statements

Any expression followed by a newline is a statement:

```
add(1, 2)
x + 5
person.greet()
```

### 8.2 Declaration Statements

```
let name = "Samrat"      // Variable declaration
let count: int = 0       // Variable with type annotation
const PI = 3.14159       // Constant declaration
```

### 8.3 Assignment Statements

```
count = 10               // Simple assignment
count += 5               // Compound assignment
name = "New Name"        // String assignment
arr[0] = 42              // Array element assignment
map["key"] = value       // Map entry assignment
```

### 8.4 Block Statements

```
{
    let x = 10
    print(x)
}
```

### 8.5 Return Statements

```
return                   // Return null
return value             // Return a value
return a + b             // Return expression result
```

### 8.6 Break and Continue

```
while true {
    if done {
        break            // Exit loop immediately
    }
    if skip {
        continue         // Skip to next iteration
    }
}
```

---

## 9. Functions

### 9.1 Function Definition

Functions are defined using the `func` keyword.

```
func function_name(param1: type1, param2: type2) -> return_type {
    // function body
    return value
}
```

**Rules:**
- Parameters require type annotations.
- Return type is optional. If omitted, the function returns `null`.
- A function without a `return` statement implicitly returns `null`.
- Functions are hoisted to the top of their scope (can be called before definition).

**Examples:**

```
// Function with parameters and return type
func add(a: int, b: int) -> int {
    return a + b
}

// Function with no return value (returns null)
func greet(name: str) {
    print("Hello, " + name + "!")
}

// Function with default parameter values
func power(base: int, exponent: int = 2) -> int {
    let result = 1
    let i = 0
    while i < exponent {
        result = result * base
        i = i + 1
    }
    return result
}

// Calling with default parameter
let squared = power(5)        // 25
let cubed = power(5, 3)       // 125
```

### 9.2 Return Values

- Functions without `return` or with bare `return` return `null`.
- Functions can have multiple `return` statements at different points.

```
func is_even(n: int) -> bool {
    if n % 2 == 0 {
        return true
    }
    return false
}
```

### 9.3 Recursion

Samrat supports recursive function calls.

```
func factorial(n: int) -> int {
    if n <= 1 {
        return 1
    }
    return n * factorial(n - 1)
}

func fibonacci(n: int) -> int {
    if n <= 1 {
        return n
    }
    return fibonacci(n - 1) + fibonacci(n - 2)
}
```

---

## 10. Control Flow

### 10.1 If-Elif-Else

```
if condition {
    // executed if condition is true
} elif other_condition {
    // executed if first condition is false and other_condition is true
} else {
    // executed if all conditions are false
}
```

**Rules:**
- The `if` branch is required. `elif` and `else` are optional.
- Multiple `elif` blocks are allowed.
- Conditions must evaluate to `bool` (no truthy/falsy coercion).

**Examples:**

```
let score = 85

if score >= 90 {
    print("Grade: A")
} elif score >= 80 {
    print("Grade: B")
} elif score >= 70 {
    print("Grade: C")
} else {
    print("Grade: F")
}
```

### 10.2 While Loop

```
while condition {
    // loop body
}
```

**Example:**

```
let i = 0
while i < 5 {
    print(i)
    i = i + 1
}
// Output: 0, 1, 2, 3, 4
```

### 10.3 For Loop

#### Range-based for loop

Iterates over a range `start..end` (start inclusive, end exclusive):

```
for variable in start..end {
    // loop body
}
```

**Example:**

```
for i in 0..5 {
    print(i)
}
// Output: 0, 1, 2, 3, 4
```

#### Collection-based for loop

Iterates over the elements of an array:

```
for item in collection {
    // loop body
}
```

**Example:**

```
let fruits = ["apple", "banana", "cherry"]
for fruit in fruits {
    print(fruit)
}
// Output: apple, banana, cherry
```

### 10.4 Break and Continue

- `break` — Exits the innermost loop immediately. Control resumes after the loop.
- `continue` — Skips the rest of the current iteration and proceeds to the next iteration.

```
for i in 0..10 {
    if i == 3 {
        continue    // Skip printing 3
    }
    if i == 7 {
        break       // Stop at 7
    }
    print(i)
}
// Output: 0, 1, 2, 4, 5, 6
```

`break` and `continue` are only valid inside loops. Using them outside a loop is a compile-time error.

---

## 11. Classes & Objects

### 11.1 Class Definition

Classes are defined using the `class` keyword.

```
class ClassName {
    // Fields (require type annotations, no initializers in 1.0)
    let field1: type1
    let field2: type2

    // Constructor (optional)
    constructor(param1: type1, param2: type2) {
        this.field1 = param1
        this.field2 = param2
    }

    // Methods
    func method_name() -> return_type {
        // method body
    }
}
```

### 11.2 Constructor

The `constructor` keyword defines the class constructor. It is called when creating a new instance. A class may have at most one constructor.

```
class Person {
    let name: str
    let age: int

    constructor(name: str, age: int) {
        this.name = name
        this.age = age
    }
}

let person = Person("Alice", 30)
```

### 11.3 The `this` Keyword

`this` refers to the current instance and is used to access fields and methods from within the class.

```
class Counter {
    let count: int

    constructor() {
        this.count = 0
    }

    func increment() {
        this.count = this.count + 1
    }

    func get_count() -> int {
        return this.count
    }
}
```

### 11.4 Method Calls and Field Access

```
let person = Person("Alice", 30)

// Method call
person.greet()

// Field access
print(person.name)

// Field mutation
person.age = 31
```

### 11.5 Example: Complete Class

```
class Rectangle {
    let width: float
    let height: float

    constructor(width: float, height: float) {
        this.width = width
        this.height = height
    }

    func area() -> float {
        return this.width * this.height
    }

    func perimeter() -> float {
        return 2 * (this.width + this.height)
    }

    func is_square() -> bool {
        return this.width == this.height
    }
}

let rect = Rectangle(5.0, 3.0)
print(rect.area())        // 15.0
print(rect.perimeter())   // 16.0
print(rect.is_square())   // false
```

---

## 12. Modules & Imports

### 12.1 Importing Modules

Samrat uses a file-based module system. Each `.samrat` file is a module.

```
// Import all public items from a module
import math

// Import specific items from a module
import sqrt, pow from math

// Import with alias
import math as m
```

### 12.2 Using Imported Items

Imported items are accessed using dot notation:

```
import math
print(math.sqrt(16))   // 4.0

import sqrt from math
print(sqrt(25))        // 5.0

import math as m
print(m.pow(2, 10))    // 1024.0
```

### 12.3 Module Resolution

Modules are resolved relative to the importing file's directory, then in standard library paths.

```
// In file main.samrat:
import utils           // Looks for utils.samrat in same directory
import io from "file"  // Looks for file.samrat in same directory
```

---

## 13. Error Handling

### 13.1 Try-Catch

```
try {
    // Code that might throw an error
    let result = risky_operation()
    print(result)
} catch error {
    // Handle the error
    print("Error: " + error)
}
```

The `catch` variable receives the thrown value as a string.

### 13.2 Throw

Errors are thrown using the `throw` keyword. Any value can be thrown (typically a string).

```
func divide(a: int, b: int) -> int {
    if b == 0 {
        throw "Division by zero"
    }
    return a / b
}

try {
    let result = divide(10, 0)
} catch error {
    print("Caught: " + error)   // "Caught: Division by zero"
}
```

---

## 14. Built-in Functions

### 14.1 Input/Output

| Function | Description | Example |
|----------|-------------|---------|
| `print(value)` | Prints value to stdout, followed by newline | `print("Hello")` |
| `print(v1, v2, ...)` | Prints multiple values separated by space | `print("a", 1, true)` |
| `input()` | Reads a line from stdin | `let name = input()` |
| `input(prompt)` | Prints prompt, then reads a line | `let name = input("Name: ")` |

### 14.2 Type Conversion

| Function | Description | Example |
|----------|-------------|---------|
| `int(value)` | Convert to int | `int("42")` → `42` |
| `float(value)` | Convert to float | `float("3.14")` → `3.14` |
| `str(value)` | Convert to string | `str(42)` → `"42"` |
| `bool(value)` | Convert to bool | `bool(1)` → `true` |

If conversion fails, a runtime error is thrown.

### 14.3 Type Inspection

| Function | Description | Example |
|----------|-------------|---------|
| `type(value)` | Returns the type name as a string | `type(42)` → `"int"` |

### 14.4 Collections

| Function | Description | Example |
|----------|-------------|---------|
| `len(collection)` | Returns the number of elements | `len([1,2,3])` → `3` |

### 14.5 Array Methods

| Method | Description | Example |
|--------|-------------|---------|
| `arr.append(value)` | Add element to end | `arr.append(4)` |
| `arr.pop()` | Remove and return last element | `let last = arr.pop()` |
| `arr.insert(index, value)` | Insert at index | `arr.insert(0, 99)` |
| `arr.remove(index)` | Remove element at index | `arr.remove(1)` |
| `arr.sort()` | Sort in place | `arr.sort()` |
| `arr.reverse()` | Reverse in place | `arr.reverse()` |
| `arr.contains(value)` | Check if value exists | `arr.contains(3)` → `true` |

### 14.6 Map Methods

| Method | Description | Example |
|--------|-------------|---------|
| `map.keys()` | Return array of keys | `map.keys()` |
| `map.values()` | Return array of values | `map.values()` |
| `map.contains(key)` | Check if key exists | `map.contains("key")` |

### 14.7 File I/O

| Function | Description | Example |
|----------|-------------|---------|
| `open(path, mode)` | Open a file | `let f = open("file.txt", "r")` |
| `file.read()` | Read entire file as string | `let content = f.read()` |
| `file.readline()` | Read one line (without newline) | `let line = f.readline()` |
| `file.write(content)` | Write string to file | `f.write("Hello")` |
| `file.close()` | Close the file | `f.close()` |

**Modes:** `"r"` (read), `"w"` (write, truncates), `"a"` (append), `"r+"` (read/write)

**Example:**
```
let file = open("data.txt", "r")
let content = file.read()
print(content)
file.close()

let out = open("output.txt", "w")
out.write("Hello, World!")
out.close()
```

---

## 15. Standard Library

The standard library modules are built-in (no file loading required). They are imported using the `import` statement.

### 15.1 `math` Module

```
import math

math.abs(-5)        // 5
math.sqrt(16)       // 4.0
math.pow(2, 10)     // 1024.0
math.floor(3.7)     // 3.0
math.ceil(3.2)      // 4.0
math.round(3.5)     // 4.0
math.max(3, 7)      // 7
math.min(3, 7)      // 3
math.pi             // 3.141592653589793
math.e              // 2.718281828459045
```

### 15.2 `string` Module

```
import string

string.upper("hello")       // "HELLO"
string.lower("HELLO")       // "hello"
string.trim("  hi  ")       // "hi"
string.split("a,b,c", ",")  // ["a", "b", "c"]
string.join([1, 2, 3], "-") // "1-2-3"
string.replace("hi there", "hi", "hello")  // "hello there"
```

### 15.3 `time` Module

```
import time

time.now()          // Current Unix timestamp (float seconds)
time.sleep(1.0)     // Sleep for 1 second
```

---

## 16. Formal Grammar

The grammar is written in EBNF notation. Non-terminals are lowercase; terminals are quoted strings or regex patterns.

```
// ─── Program ──────────────────────────────────────────────────────
program             = { statement }

// ─── Statements ───────────────────────────────────────────────────
statement           = var_declaration
                    | const_declaration
                    | assignment
                    | function_def
                    | class_def
                    | if_statement
                    | while_loop
                    | for_loop
                    | return_statement
                    | break_statement
                    | continue_statement
                    | try_statement
                    | throw_statement
                    | import_statement
                    | block
                    | expression_statement

block               = "{" { statement } "}"
expression_statement = expression

// ─── Variables and Constants ──────────────────────────────────────
var_declaration     = "let" identifier [ ":" type ] [ "=" expression ]
const_declaration   = "const" identifier [ ":" type ] "=" expression
assignment          = lvalue assignment_operator expression
lvalue              = identifier { "." identifier | "[" expression "]" }
assignment_operator = "=" | "+=" | "-=" | "*=" | "/=" | "%="

// ─── Functions ────────────────────────────────────────────────────
function_def        = "func" identifier "(" [ parameter_list ] ")" [ "->" type ] block
parameter_list      = parameter { "," parameter }
parameter           = identifier ":" type [ "=" expression ]
return_statement    = "return" [ expression ]

// ─── Classes ──────────────────────────────────────────────────────
class_def           = "class" identifier "{" { class_member } "}"
class_member        = var_declaration
                    | constructor_def
                    | method_def
constructor_def     = "constructor" "(" [ parameter_list ] ")" block
method_def          = "func" identifier "(" [ parameter_list ] ")" [ "->" type ] block

// ─── Control Flow ─────────────────────────────────────────────────
if_statement        = "if" expression block
                      { "elif" expression block }
                      [ "else" block ]
while_loop          = "while" expression block
for_loop            = "for" identifier "in" expression block
break_statement     = "break"
continue_statement  = "continue"

// ─── Error Handling ───────────────────────────────────────────────
try_statement       = "try" block "catch" identifier block
throw_statement     = "throw" expression

// ─── Modules ──────────────────────────────────────────────────────
import_statement    = "import" identifier [ "as" identifier ]
                    | "import" identifier_list "from" identifier [ "as" identifier ]
identifier_list     = identifier { "," identifier }

// ─── Expressions (Precedence Climbing) ────────────────────────────
expression          = or_expression
or_expression       = and_expression { "or" and_expression }
and_expression      = equality_expression { "and" equality_expression }
equality_expression = comparison_expression { ("==" | "!=") comparison_expression }
comparison_expression = bitwise_or_expression { ("<" | ">" | "<=" | ">=") bitwise_or_expression }
bitwise_or_expression  = bitwise_xor_expression { "|" bitwise_xor_expression }
bitwise_xor_expression = bitwise_and_expression { "^" bitwise_and_expression }
bitwise_and_expression = shift_expression { "&" shift_expression }
shift_expression    = additive_expression { ("<<" | ">>") additive_expression }
additive_expression = multiplicative_expression { ("+" | "-") multiplicative_expression }
multiplicative_expression = unary_expression { ("*" | "/" | "%") unary_expression }
unary_expression    = ("not" | "-" | "~") unary_expression
                    | exponentiation_expression
exponentiation_expression = postfix_expression [ "**" unary_expression ]
postfix_expression  = primary_expression { "(" [ argument_list ] ")"
                                         | "[" expression "]"
                                         | "." identifier }
primary_expression  = literal
                    | identifier
                    | "(" expression ")"
                    | "[" [ expression_list ] "]"
                    | "{" [ map_entry_list ] "}"
argument_list       = expression { "," expression }
expression_list     = expression { "," expression }
map_entry_list      = expression ":" expression { "," expression ":" expression }

// ─── Literals ─────────────────────────────────────────────────────
literal             = integer_literal
                    | float_literal
                    | string_literal
                    | "true"
                    | "false"
                    | "null"

// ─── Types ────────────────────────────────────────────────────────
type                = "int" | "float" | "str" | "bool" | "void"
                    | "[" type "]"
                    | "{" type ":" type "}"
                    | identifier

// ─── Identifiers ──────────────────────────────────────────────────
identifier          = letter { letter | digit | "_" }
letter              = "a".."z" | "A".."Z" | "_"
digit               = "0".."9"

// ─── Literals (Lexical Rules) ─────────────────────────────────────
integer_literal     = digit { digit | "_" }
                    | "0x" hex_digit { hex_digit | "_" }
                    | "0b" binary_digit { binary_digit | "_" }
                    | "0o" octal_digit { octal_digit | "_" }
float_literal       = digit { digit | "_" } "." digit { digit | "_" }
                    [ "e" [ "+" | "-" ] digit { digit | "_" } ]
string_literal      = '"' { character | escape_sequence } '"'
hex_digit           = digit | "a".."f" | "A".."F"
binary_digit        = "0" | "1"
octal_digit         = "0".."7"
escape_sequence     = "\\" ( "n" | "t" | "r" | "\\" | '"' | "0" )
```

---

## 17. Example Programs

### 17.1 Hello, World!

```
print("Hello, World!")
```

### 17.2 Fibonacci Sequence

```
func fibonacci(n: int) -> int {
    if n <= 1 {
        return n
    }
    return fibonacci(n - 1) + fibonacci(n - 2)
}

for i in 0..10 {
    print(fibonacci(i))
}
// Output:
// 0
// 1
// 1
// 2
// 3
// 5
// 8
// 13
// 21
// 34
```

### 17.3 FizzBuzz

```
for i in 1..101 {
    if i % 15 == 0 {
        print("FizzBuzz")
    } elif i % 3 == 0 {
        print("Fizz")
    } elif i % 5 == 0 {
        print("Buzz")
    } else {
        print(i)
    }
}
```

### 17.4 Student Grade Management

```
class Student {
    let name: str
    let age: int
    let grades: [int]

    constructor(name: str, age: int) {
        this.name = name
        this.age = age
        this.grades = []
    }

    func add_grade(grade: int) {
        this.grades.append(grade)
    }

    func average_grade() -> float {
        if len(this.grades) == 0 {
            return 0.0
        }
        let sum = 0
        for grade in this.grades {
            sum = sum + grade
        }
        return sum / len(this.grades)
    }

    func has_passed() -> bool {
        return this.average_grade() >= 60.0
    }
}

let students = [
    Student("Alice", 20),
    Student("Bob", 22),
    Student("Charlie", 21)
]

students[0].add_grade(85)
students[0].add_grade(90)
students[0].add_grade(78)

students[1].add_grade(55)
students[1].add_grade(60)

students[2].add_grade(95)
students[2].add_grade(88)
students[2].add_grade(92)

for student in students {
    print(student.name + ": " + str(student.average_grade()))
    if student.has_passed() {
        print("  Status: Passed")
    } else {
        print("  Status: Failed")
    }
}
```

### 17.5 Error Handling

```
func safe_divide(a: int, b: int) -> int {
    if b == 0 {
        throw "Cannot divide by zero"
    }
    return a / b
}

try {
    let result = safe_divide(10, 0)
    print("Result: " + str(result))
} catch error {
    print("Error occurred: " + error)
}
```

### 17.6 File Copy Program

```
func copy_file(source: str, destination: str) {
    let src = open(source, "r")
    let content = src.read()
    src.close()

    let dst = open(destination, "w")
    dst.write(content)
    dst.close()

    print("Copied " + source + " to " + destination)
}

copy_file("input.txt", "output.txt")
```

### 17.7 Recursive Factorial

```
func factorial(n: int) -> int {
    if n <= 1 {
        return 1
    }
    return n * factorial(n - 1)
}

print(factorial(5))   // 120
```

---

## Appendix A: Reserved Keywords

```
let         const       func        return
if          elif        else        while
for         in          break       continue
class       constructor this        new
true        false       null        and
or          not         import      from
as          try         catch       throw
int         float       str         bool
void        match       case        default
```

Note: `match`, `case`, and `default` are reserved for future use. Using them in 1.0 produces a compile-time error: "feature not available in Samrat 1.0".

## Appendix B: Error Message Format

All Samrat errors follow this consistent format:

```
<ErrorType> at <file>:<line>:<column>: <description>

    <source line with context>
    ^--- here

Suggestion: <how to fix the issue>
```

**LexerError example:**
```
LexerError at main.samrat:3:8: Unexpected character '@'

    let @ = 5
         ^--- here

Suggestion: Remove or replace the unexpected character '@'.
```

**SyntaxError (Parser) example:**
```
SyntaxError at main.samrat:1:15: Expected ')' after parameters for 'add'. Got '{' instead.
    Got: '{'

    func add(a: int, b: int {
                   ^--- here

Suggestion: Add a closing ')' before the '{'.
```

**SemanticError example:**
```
SemanticError at main.samrat:5:5: Undefined variable 'y'

    print(y)
          ^--- here

Suggestion: Declare 'y' before using it, or check the spelling.
```

**TypeError example:**
```
TypeError at main.samrat:2:13: Cannot add int and str

    let result = 5 + "hello"
                    ^--- here

Suggestion: Convert the string to int with int("hello") or use str(5).
```

## Appendix C: Operator Precedence Summary

| Precedence | Operators | Associativity |
|------------|-----------|---------------|
| 1 (highest) | `()` `[]` `.` | Left-to-right |
| 2 | `not` `-` unary `~` | Right-to-left |
| 3 | `**` | Right-to-left |
| 4 | `*` `/` `%` | Left-to-right |
| 5 | `+` `-` | Left-to-right |
| 6 | `<<` `>>` | Left-to-right |
| 7 | `&` | Left-to-right |
| 8 | `^` | Left-to-right |
| 9 | `\|` | Left-to-right |
| 10 | `<` `>` `<=` `>=` | Left-to-right |
| 11 | `==` `!=` | Left-to-right |
| 12 | `and` | Left-to-right |
| 13 | `or` | Left-to-right |
| 14 | `=` `+=` `-=` `*=` `/=` `%=` | Right-to-left |
| 15 (lowest) | `..` | Left-to-right |

## Appendix D: Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-07-19 | Initial specification. Core language frozen. |

---

*This specification is the definitive reference for Samrat 1.0. All implementations must conform to this document.*