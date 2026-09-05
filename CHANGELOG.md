# Changelog

All notable changes to the Samrat Programming Language project will be documented in this file.

## [V1.1.3] - 2026-09-05

### Changed
- Refreshed release documentation for the `V1.1.3` tag.

## [V1.1.5 / 2.0.0] - 2026-09-05

### Added
- **Complete Native Stack in Rust**: Rebuilt compiler toolchain from scratch into a 10-crate Cargo workspace (`samrat-cli`, `samrat-lexer`, `samrat-parser`, `samrat-semantic`, `samrat-ir`, `samrat-codegen`, `samrat-runtime`, `samrat-stdlib`, `samrat-pkg`, `samrat-debug`).
- **Conversational English Pipeline Support**: Support for natural English sentences such as `When the program starts, create numbers from 1 to 100, keep the even numbers, add them together, and show the total.`
- **Cranelift Codegen Lowering**: Full IR lowering for arithmetic, memory allocations, store/load, comparison, conditional branching, function calls, and range pipelines.
- **Unified Toolchain CLI**: `samrat build`, `samrat run`, `samrat check`, `samrat fmt`, `samrat test`, `samrat pkg`, `samrat debug`, `samrat doc`, `samrat clean`, and `samrat repl`.
- **System Linker Integration**: `samrat build` automatically invokes `cc`/`gcc`/`clang` to link compiled object files into executable binaries.
- **SourceMap Debugging & Package Manager**: Added `samrat debug` source map generation and `Samrat.toml` package manifest handling (`samrat pkg init`).
