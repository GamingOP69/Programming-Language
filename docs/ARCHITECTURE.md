# Samrat Architecture Overview (V1.1.5 / 2.0.0)

Samrat is designed as a multi-stage native compiler and runtime stack implemented in Rust.

```
[ Natural English Source (.samrat) ]
              │
              ▼
    [ samrat-lexer ] ── (Token Stream)
              │
              ▼
   [ samrat-parser ] ── (Abstract Syntax Tree)
              │
              ▼
 [ samrat-semantic ] ── (Type & Symbol Checked AST)
              │
              ▼
       [ samrat-ir ] ── (Typed SSA IR & Constant Folding)
              │
              ▼
  [ samrat-codegen ] ── (Cranelift Machine Code Generation)
              │
              ▼
   [ Native Linker ] ── (Executable Binary / Object Code)
```

## Workspace Crate Breakdown

1. `samrat-cli`: Unified binary entrypoint (`samrat`).
2. `samrat-lexer`: Case-insensitive tokenization for conversational English constructs.
3. `samrat-parser`: LL(k) parser producing structured AST nodes.
4. `samrat-semantic`: Symbol table, scope analysis, and type checking.
5. `samrat-ir`: SSA intermediate representation builder and optimizer.
6. `samrat-codegen`: Cranelift backend for x86-64 and ARM64.
7. `samrat-runtime`: GC/ARC hybrid memory management and threading.
8. `samrat-stdlib`: High-level and low-level system library bindings.
9. `samrat-pkg`: Dependency manager and `Samrat.toml` parser.
10. `samrat-debug`: Source map generator and debugger metadata handler.
