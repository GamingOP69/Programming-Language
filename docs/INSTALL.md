# Installation & Setup (V1.1.5)

## System Requirements
- Rust 1.70 or higher (`cargo`, `rustc`)
- C compiler (`cc`, `gcc`, or `clang`) for native binary linking

## Building Samrat Native Compiler

```bash
git clone https://github.com/samrat/samrat.git
cd samrat
cargo build --release --workspace
```

The resulting binary will be at `./target/release/samrat`.

## Verification

```bash
cargo test --workspace
./target/release/samrat run examples/hello.samrat
```
