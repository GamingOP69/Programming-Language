# Samrat Compiler & Runtime Architecture

## Compiler Pipeline

```text
Source Code (.samrat)
      ↓
Lexer (crates/samrat-lexer)
      ↓ Tokens
Parser (crates/samrat-parser)
      ↓ AST (Abstract Syntax Tree)
Semantic Analyzer (crates/samrat-semantic)
      ↓ Typed AST & Symbol Table
High-Level IR & Optimization (crates/samrat-ir)
      ↓ Optimized IR
Code Generation (crates/samrat-codegen via Cranelift)
      ↓ Native Object File (.o / .obj)
Native Linker Integration (crates/samrat-codegen)
      ↓
Native Binary Executable
```

## Runtime Architecture (`crates/samrat-runtime`)
- Lightweight process initialization and startup routines
- High-performance memory allocator interface
- Reference counting and string management utilities
- Platform abstraction layer for Windows, Linux, and macOS OS calls
