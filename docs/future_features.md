# Samrat — Future Features (Post 1.0)

This document catalogs features planned for future versions of Samrat.
They are **not** part of the Version 1.0 specification and will not be implemented
until the core language is stable and proven.

---

## 1. Generics (Type Parameters)

Define functions, classes, and data structures that operate on multiple types.

```
func identity<T>(value: T) -> T {
    return value
}

class Box<T> {
    let value: T

    constructor(value: T) {
        this.value = value
    }
}

let box = Box<int>(42)
```

## 2. Enumerations (Enums)

Define types with a fixed set of variants, optionally carrying data.

```
enum Option<T> {
    Some(T),
    None
}

enum Color {
    Red,
    Green,
    Blue
}
```

## 3. Interfaces / Traits

Define shared behavior across unrelated types.

```
interface Drawable {
    func draw()
}

class Circle : Drawable {
    // ...
    func draw() {
        // implementation
    }
}
```

## 4. Pattern Matching

Match values against patterns with destructuring.

```
match value {
    case 0 -> print("zero")
    case 1 -> print("one")
    case n -> print("other: " + str(n))
}
```

## 5. Async/Await

Concurrent and asynchronous programming without manual thread management.

```
async func fetch_data(url: str) -> str {
    let response = await http.get(url)
    return response
}
```

## 6. Lambda Expressions (Anonymous Functions)

Create functions inline without naming them.

```
let numbers = [1, 2, 3, 4, 5]
let doubled = numbers.map(func (x) { return x * 2 })
// Or shorthand:
let doubled = numbers.map(x => x * 2)
```

## 7. Annotations / Decorators

Metadata attached to declarations for frameworks, serialization, validation, etc.

```
@json
class User {
    @field(name = "user_name")
    let name: str
}
```

## 8. Operator Overloading

Define custom behavior for operators on user-defined types.

```
class Vector {
    // ...
    func operator+(other: Vector) -> Vector {
        // ...
    }
}
```

## 9. Union Types

A value that can be one of several types.

```
let value: int | str = 42
value = "hello"  // also valid
```

## 10. Null Safety / Optional Types

Compile-time guarantee that null values are handled explicitly.

```
let name: str? = null  // nullable
// Cannot use 'name' without checking for null first
if name != null {
    print(name)
}
```

## 11. Destructuring Assignment

Unpack arrays and objects into individual variables.

```
let [a, b, c] = [1, 2, 3]
let {name, age} = person
```

## 12. Slices and Range Types

Efficient views into arrays and strings.

```
let arr = [1, 2, 3, 4, 5]
let slice = arr[1:4]  // [2, 3, 4]
```

## 13. Tuples

Fixed-size ordered collections of potentially different types.

```
let pair: (int, str) = (42, "hello")
```

## 14. Spread Operator

Expand arrays and maps into function calls or literals.

```
let arr = [1, 2, 3]
let combined = [...arr, 4, 5]
```

## 15. Constants in Types (Const Generics)

Generic parameters that are values rather than types.

```
func fixed_array<T, const N: int>() -> [T; N] {
    // ...
}
```

## 16. Compile-Time Execution / Macros

Execute code at compile time for metaprogramming.

```
const computed = comptime {
    fibonacci(100)
}
```

## 17. FFI (Foreign Function Interface)

Call functions written in C and other languages.

```
extern func puts(s: str) -> int
```

---

## Versioning Strategy

| Version | Focus |
|---------|-------|
| 1.0     | Core language: lexer, parser, semantic analysis, interpreter |
| 1.1     | Generics, enums, pattern matching |
| 1.2     | Async/await, lambdas, interfaces |
| 2.0     | Compiler target, native executables, FFI |
| 2.x+    | Advanced features: macros, dependent types, etc. |