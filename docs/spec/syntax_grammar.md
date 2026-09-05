# Samrat Syntax & Controlled English Grammar

Samrat uses a deterministic controlled-English syntax. Every construct maps to a well-defined AST node.

## Variable Declarations

```samrat
create a number called age set to 25
create text called name set to "Samrat"
```

Equivalently with optional punctuation and articles:
```samrat
Create a number called age set to 25.
Create text called name set to "Samrat".
```

## Reassignment
```samrat
set age to 26
```

## Entry Point
```samrat
When the program starts, show "Hello, World!"
```

## Functions
```samrat
create function add taking a as number, b as number returning number:
    return a + b
```

## Conditional Statements
```samrat
if age is greater than 18:
    show "Adult"
otherwise:
    show "Minor"
```

## Loops
```samrat
while age is less than 30:
    set age to age + 1

for each x in range from 1 to 100:
    show x
```
