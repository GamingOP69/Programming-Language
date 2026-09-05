# Samrat Language Roadmap

## Completed (V1.1.5 / 2.0.0 Architecture)
- [x] Complete native Rust compiler stack (`samrat-lexer` through `samrat-codegen`).
- [x] Cranelift-backed native machine code emission.
- [x] English-first conversational syntax parser & IR pipeline lowering.
- [x] Unified CLI toolchain with `build`, `run`, `check`, `fmt`, `test`, `pkg`, `debug`, `doc`.
- [x] System linker CC/GCC/Clang execution support.

## Future Plans (V2.1+)
- [ ] LLVM backend plugin for higher optimization levels (`-O3`).
- [ ] Self-hosting compiler written in Samrat conversational syntax.
- [ ] Standard library network & async HTTP server modules.
