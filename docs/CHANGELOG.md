# Changelog

All notable changes to the Samrat Programming Language project will be documented in this file.

## [V1.1.5 / 2.0.0] - 2026-09-05

### Added
- Native Cranelift code generation lowering in Rust.
- Multi-crate toolchain architecture under `crates/`.
- Native executable linking via CC toolchain.
- Interactive and automated developer tooling commands (`fmt`, `test`, `doc`, `debug`).

## [1.1.0] — 2026-07-19

### New Language Features

#### Operators
- **Pipe operator (`|>`)** — Chain function calls
- **Null coalescing (`??`)** — Default values for null
- **Lambda arrow (`=>`)** — Function shorthand
- **Ternary (`?`)** — Inline conditionals
- **Spread (`...`)** — Array/map expansion

## [1.0.0] — 2026-07-19

### Initial Release
- Hand-written lexer, recursive-descent parser, semantic analyzer, interpreter, and VM.
