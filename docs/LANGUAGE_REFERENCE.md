# Samrat Language Reference

## Syntax Overview

Samrat uses braces `{}` for blocks, no semicolons. Statements are separated by newlines.

```
// Comments
// Single-line
/* Multi-line (nestable) */

// Literals
42           // int
3.14         // float
"hello"      // str
true         // bool
null         // null

// Variables
let x = 5
let name: str = "Samrat"
const PI = 3.14159

// Functions
func add(a: int, b: int) -> int {
    return a + b
}

// Control flow
if condition { } elif other { } else { }
while condition { }
for i in 0..10 { }
for item in collection { }

// Classes
class Person {
    let name: str
    constructor(name: str) {
        this.name = name
    }
    func greet() -> str {
        return "Hello, " + this.name
    }
}
```

## Data Types

| Type | Description | Examples |
|------|-------------|----------|
| `int` | Signed integer (arbitrary precision) | `42`, `-17`, `0xFF`, `0b1010` |
| `float` | IEEE 754 double-precision | `3.14`, `-0.5`, `1e10` |
| `str` | UTF-8 string | `"hello"`, `"line1\nline2"` |
| `bool` | Boolean | `true`, `false` |
| `null` | Null value | `null` |
| `[type]` | Array of elements | `[1, 2, 3]`, `["a", "b"]` |
| `{keyType: valType}` | Map/dictionary | `{"a": 1, "b": 2}` |

## Operators (Precedence High to Low)

| Level | Operators | Assoc |
|-------|-----------|-------|
| 1 | `()` `[]` `.` | Left |
| 2 | `not` `-` `~` (unary) | Right |
| 3 | `**` | Right |
| 4 | `*` `/` `%` | Left |
| 5 | `+` `-` | Left |
| 6 | `<<` `>>` | Left |
| 7 | `&` | Left |
| 8 | `^` | Left |
| 9 | `\|` | Left |
| 10 | `<` `>` `<=` `>=` | Left |
| 11 | `==` `!=` | Left |
| 12 | `and` | Left |
| 13 | `or` | Left |
| 14 | `=` `+=` `-=` `*=` `/=` `%=` | Right |
| 15 | `..` (range) | Left |

## Control Flow

```
// If-elif-else
if score >= 90 {
    print("A")
} elif score >= 80 {
    print("B")
} else {
    print("C")
}

// While
let i = 0
while i < 5 {
    print(i)
    i = i + 1
}

// For range (0..5 = 0, 1, 2, 3, 4)
for i in 0..5 {
    print(i)
}

// For collection
for fruit in ["apple", "banana"] {
    print(fruit)
}

// Break and continue
for i in 0..10 {
    if i == 3 { continue }
    if i == 7 { break }
    print(i)
}
```

## Functions

```
// Basic function
func add(a: int, b: int) -> int {
    return a + b
}

// No return type (returns null)
func greet(name: str) {
    print("Hi, " + name)
}

// Default parameters
func power(base: int, exp: int = 2) -> int {
    return base ** exp
}

// Recursion
func factorial(n: int) -> int {
    if n <= 1 { return 1 }
    return n * factorial(n - 1)
}
```

## Classes

```
class Rectangle {
    let width: float
    let height: float

    constructor(w: float, h: float) {
        this.width = w
        this.height = h
    }

    func area() -> float {
        return this.width * this.height
    }
}

let r = Rectangle(5.0, 3.0)
print(r.area())  // 15.0
```

## Error Handling

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
    print("Error: " + error)
}
```

## Modules

```
import math
print(math.sqrt(16))  // 4.0

import sqrt from math
print(sqrt(25))       // 5.0

import math as m
print(m.pi)           // 3.14159...
```

## Built-in Functions

| Function | Description |
|----------|-------------|
| `print(...)` | Print values to stdout |
| `input(prompt?)` | Read line from stdin |
| `int(value)` | Convert to integer |
| `float(value)` | Convert to float |
| `str(value)` | Convert to string |
| `bool(value)` | Convert to boolean |
| `type(value)` | Get type name as string |
| `len(collection)` | Get length of string, array, or map |