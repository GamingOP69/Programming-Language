# Samrat Language Reference (V1.1.5)

## Overview

Samrat supports English-first conversational syntax as well as traditional structured syntax.
Keyword matching in conversational mode is case-insensitive and sentence-oriented.

## Conversational English Syntax Examples

```samrat
When the program starts, create numbers from 1 to 100, keep the even numbers, add them together, and show the total.
```

```samrat
When the program starts, set total to 0.
```

## Structured Syntax Overview

```
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
```

## Toolchain Integration

Compile using the unified `samrat` CLI:
- `samrat build <file>`
- `samrat run <file>`
- `samrat check <file>`
- `samrat fmt <file>`
- `samrat test`
- `samrat debug <file>`
- `samrat doc`
