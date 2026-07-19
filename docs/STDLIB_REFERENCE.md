# Samrat Standard Library Reference

## math Module

```
import math
```

| Function | Description | Example |
|----------|-------------|---------|
| `abs(x)` | Absolute value | `math.abs(-5)` → `5` |
| `sqrt(x)` | Square root | `math.sqrt(16)` → `4.0` |
| `pow(x, y)` | x raised to power y | `math.pow(2, 10)` → `1024.0` |
| `floor(x)` | Round down | `math.floor(3.7)` → `3.0` |
| `ceil(x)` | Round up | `math.ceil(3.2)` → `4.0` |
| `round(x)` | Round to nearest | `math.round(3.5)` → `4.0` |
| `max(a, b)` | Maximum of two values | `math.max(3, 7)` → `7` |
| `min(a, b)` | Minimum of two values | `math.min(3, 7)` → `3` |

| Constant | Value |
|----------|-------|
| `math.pi` | `3.141592653589793` |
| `math.e` | `2.718281828459045` |

## string Module

```
import string
```

| Function | Description | Example |
|----------|-------------|---------|
| `upper(s)` | Convert to uppercase | `string.upper("hello")` → `"HELLO"` |
| `lower(s)` | Convert to lowercase | `string.lower("HELLO")` → `"hello"` |
| `trim(s)` | Remove leading/trailing whitespace | `string.trim("  hi  ")` → `"hi"` |
| `split(s, sep)` | Split string by separator | `string.split("a,b,c", ",")` → `["a", "b", "c"]` |
| `join(items, sep)` | Join array with separator | `string.join([1, 2, 3], "-")` → `"1-2-3"` |
| `replace(s, old, new)` | Replace substring | `string.replace("hi there", "hi", "hello")` → `"hello there"` |

## time Module

```
import time
```

| Function | Description | Example |
|----------|-------------|---------|
| `now()` | Current Unix timestamp (float seconds) | `time.now()` → `1721400000.0` |
| `sleep(seconds)` | Sleep for specified duration | `time.sleep(1.0)` |

## Array Methods

Arrays are mutable, zero-indexed collections.

| Method | Description | Example |
|--------|-------------|---------|
| `arr.append(value)` | Add element to end | `arr.append(4)` |
| `arr.pop()` | Remove and return last element | `let last = arr.pop()` |
| `arr.insert(index, value)` | Insert element at index | `arr.insert(0, 99)` |
| `arr.remove(index)` | Remove element at index | `arr.remove(1)` |
| `arr.sort()` | Sort in place (ascending) | `arr.sort()` |
| `arr.reverse()` | Reverse in place | `arr.reverse()` |
| `arr.contains(value)` | Check if value exists | `arr.contains(3)` → `true` |

## Map Methods

Maps are key-value collections. Keys must be hashable (`int`, `str`, `bool`).

| Method | Description | Example |
|--------|-------------|---------|
| `map.keys()` | Return array of keys | `map.keys()` |
| `map.values()` | Return array of values | `map.values()` |
| `map.contains(key)` | Check if key exists | `map.contains("key")` → `true` |

## File I/O

| Function | Description | Example |
|----------|-------------|---------|
| `open(path, mode)` | Open a file | `let f = open("file.txt", "r")` |
| `file.read()` | Read entire file as string | `let content = f.read()` |
| `file.readline()` | Read one line (without newline) | `let line = f.readline()` |
| `file.write(content)` | Write string to file | `f.write("Hello")` |
| `file.close()` | Close the file | `f.close()` |

**File modes:** `"r"` (read), `"w"` (write, truncates), `"a"` (append), `"r+"` (read/write)

### Example

```
let file = open("data.txt", "r")
let content = file.read()
print(content)
file.close()

let out = open("output.txt", "w")
out.write("Hello, World!")
out.close()
```

## Built-in Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `print` | `print(...values)` | Print values to stdout, space-separated |
| `input` | `input(prompt?) -> str` | Read line from stdin (optional prompt) |
| `int` | `int(value) -> int` | Convert to integer |
| `float` | `float(value) -> float` | Convert to float |
| `str` | `str(value) -> str` | Convert to string |
| `bool` | `bool(value) -> bool` | Convert to boolean |
| `type` | `type(value) -> str` | Get type name as string |
| `len` | `len(collection) -> int` | Get length of string, array, or map |