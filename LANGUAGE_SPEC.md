# Samrat Language Specification (V1.1.5)

## 1. Syntax Design

Samrat uses English-first conversational syntax. Keyword matching is case-insensitive, punctuation-resilient, and sentence-oriented.

### Core Entrypoint
```
When the program starts,
    <statements>
```

### Pipelines & Data Transformations
```
create numbers from <start> to <end>, keep the even numbers, add them together, and show the total.
```

### Variable Declarations & Control Flow
```
set total to 0.
if total is 0 then
    show "Zero!".
```

## 2. Type System & Semantics

- **Inferred & Static Types**: Primitive types include `Integer` (i64), `Float` (f64), `String`, `Boolean`, and `Pointer`.
- **Memory Safety**: ARC (Automatic Reference Counting) for high-level objects with unsafe manual allocation support for low-level performance code.
- **IR Representation**: ASTs are lowered into static single-assignment (SSA) IR prior to Cranelift native code generation.
