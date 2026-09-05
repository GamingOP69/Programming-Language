# Samrat Lexical Grammar

## 1. Case Rules
- **Keywords**: Case-insensitive. `When`, `WHEN`, and `when` are lexically identical.
- **Identifiers**: Case-sensitive. `myVar` and `myvar` are distinct identifiers.

## 2. Statement Termination
- Primary statement separator: Newline (`\n`).
- Optional statement terminator: Period (`.`) when unambiguous.

## 3. Keywords
Key phrase and word tokens include:
- `create`, `variable`, `called`, `set`, `to`, `as`
- `when`, `the`, `program`, `starts`, `show`, `display`, `print`
- `if`, `else`, `otherwise`, `then`, `while`, `for`, `each`, `in`, `repeat`
- `function`, `returns`, `takes`, `with`
- `struct`, `enum`, `type`, `unsafe`, `try`, `catch`, `throw`
- `true`, `false`, `null`, `and`, `or`, `not`

## 4. Literals
- **Integer**: Decimal (`123`), Hex (`0x1A`), Binary (`0b1010`), Octal (`0o777`), with optional underscores (`1_000_000`).
- **Float**: Standard (`3.14159`), Scientific (`1e10`), with optional underscores.
- **String**: Enclosed in double quotes `"..."` supporting escapes (`\n`, `\t`, `\"`, `\\`, `\u{...}`).
- **Boolean**: `true` or `false`.
- **Null**: `null`.
