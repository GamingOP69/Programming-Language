# Samrat Type System & Memory Model

## Type System
Samrat is a statically typed language with strong type safety and explicit conversions.

### Primitive Types
- `number`: 64-bit floating point or signed integer (represented as i64/f64)
- `int`: Signed 64-bit integer
- `uint`: Unsigned 64-bit integer
- `float`: 64-bit IEEE 754 float
- `boolean`: Boolean (`true` or `false`)
- `text` / `string`: UTF-8 encoded string sequence
- `null`: Representing absence of value

### Composite Types
- **Arrays**: Homogeneous dynamically sized sequences `[T]`
- **Maps**: Key-value associations `{K: V}`
- **Structs**: Custom composite data types with named fields
- **Enums**: Tagged unions with optional associated data
- **Option & Result**: Idiomatic algebraic types for optionality and error handling

## Memory Model
- **Hybrid Memory Model**: Deterministic reference counting with stack-allocated value types and minimal runtime allocation overhead.
- **Unsafe Mode**: Unsafe operations (raw pointer dereferences, low-level system calls) must be enclosed in an `unsafe` block:
```samrat
unsafe:
    # low-level direct memory operations
```
