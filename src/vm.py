"""
Samrat Programming Language — Stack-Based Virtual Machine

Executes bytecode chunks produced by the compiler. Features:
- Value stack for all operations
- Call frames for function calls
- Global variable dictionary
- Exception handling with try/catch
- Built-in function implementations

Usage:
    from vm import VM
    vm = VM()
    result = vm.run(chunk)
"""

from bytecode import OpCode, Chunk
from errors import RuntimeError_


class VM:
    """
    Stack-based virtual machine that executes Samrat bytecode.

    Attributes:
        stack: The value stack.
        globals: Dictionary of global variables.
        frames: Stack of call frames.
        ip: Instruction pointer (index into chunk.code).
        chunk: Current chunk being executed.
        handler_stack: Stack of (catch_ip, chunk) for exception handling.
    """

    def __init__(self):
        self.stack = []
        self.globals = {}
        self.frames = []  # Stack of (ip, chunk, locals) for calls
        self.ip = 0
        self.chunk = None
        self.handler_stack = []
        self._function_chunks = {}  # name -> (chunk, param_count)
        self._current_instance = None

        # Register built-in functions
        self._register_builtins()

    def _register_builtins(self):
        self.globals['print'] = BuiltInVM('print', self._builtin_print)
        self.globals['input'] = BuiltInVM('input', self._builtin_input)
        self.globals['int'] = BuiltInVM('int', self._builtin_int)
        self.globals['float'] = BuiltInVM('float', self._builtin_float)
        self.globals['str'] = BuiltInVM('str', self._builtin_str)
        self.globals['bool'] = BuiltInVM('bool', self._builtin_bool)
        self.globals['type'] = BuiltInVM('type', self._builtin_type)
        self.globals['len'] = BuiltInVM('len', self._builtin_len)

    def _builtin_print(self, args):
        print(' '.join(self._stringify(a) for a in args))
        return None

    def _builtin_input(self, args):
        return input()

    def _builtin_int(self, args):
        return int(args[0])

    def _builtin_float(self, args):
        return float(args[0])

    def _builtin_str(self, args):
        return self._stringify(args[0])

    def _builtin_bool(self, args):
        return bool(args[0])

    def _builtin_type(self, args):
        return self._type_name(args[0])

    def _builtin_len(self, args):
        return len(args[0])

    def run(self, chunk: Chunk):
        """Execute a bytecode chunk."""
        self.chunk = chunk
        self.ip = 0
        self.stack = []

        try:
            while self.ip < len(self.chunk.code):
                opcode, arg = self.chunk.code[self.ip]
                self.ip += 1
                self._execute(opcode, arg)
        except ReturnException as ret:
            return ret.value
        except RuntimeError_ as e:
            print(f"RuntimeError: {e}")
            return None

        # Return value on top of stack if any
        if self.stack:
            return self.stack[-1]
        return None

    def _execute(self, opcode: OpCode, arg):  # noqa: C901
        """Execute a single instruction."""

        # ─── Stack Operations ──────────────────────────────────────────
        if opcode == OpCode.PUSH_NULL:
            self.stack.append(None)
        elif opcode == OpCode.PUSH_TRUE:
            self.stack.append(True)
        elif opcode == OpCode.PUSH_FALSE:
            self.stack.append(False)
        elif opcode == OpCode.PUSH_INT:
            self.stack.append(self.chunk.constants[arg])
        elif opcode == OpCode.PUSH_FLOAT:
            self.stack.append(self.chunk.constants[arg])
        elif opcode == OpCode.PUSH_STRING:
            self.stack.append(self.chunk.constants[arg])
        elif opcode == OpCode.POP:
            self.stack.pop()

        # ─── Arithmetic ────────────────────────────────────────────────
        elif opcode == OpCode.ADD:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a + b)
        elif opcode == OpCode.SUB:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a - b)
        elif opcode == OpCode.MUL:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a * b)
        elif opcode == OpCode.DIV:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a / b)
        elif opcode == OpCode.MOD:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a % b)
        elif opcode == OpCode.POW:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a ** b)
        elif opcode == OpCode.NEG:
            a = self.stack.pop()
            self.stack.append(-a)

        # ─── Comparison ────────────────────────────────────────────────
        elif opcode == OpCode.EQ:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a == b)
        elif opcode == OpCode.NEQ:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a != b)
        elif opcode == OpCode.LT:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a < b)
        elif opcode == OpCode.GT:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a > b)
        elif opcode == OpCode.LE:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a <= b)
        elif opcode == OpCode.GE:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a >= b)

        # ─── Logical ──────────────────────────────────────────────────
        elif opcode == OpCode.NOT:
            a = self.stack.pop()
            self.stack.append(not self._truthy(a))
        elif opcode == OpCode.AND:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(self._truthy(a) and self._truthy(b))
        elif opcode == OpCode.OR:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(self._truthy(a) or self._truthy(b))

        # ─── Bitwise ──────────────────────────────────────────────────
        elif opcode == OpCode.BIT_AND:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a & b)
        elif opcode == OpCode.BIT_OR:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a | b)
        elif opcode == OpCode.BIT_XOR:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a ^ b)
        elif opcode == OpCode.BIT_NOT:
            a = self.stack.pop()
            self.stack.append(~a)
        elif opcode == OpCode.SHL:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a << b)
        elif opcode == OpCode.SHR:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a >> b)

        # ─── Control Flow ──────────────────────────────────────────────
        elif opcode == OpCode.JMP:
            self.ip = arg
        elif opcode == OpCode.JMP_IF_FALSE:
            val = self.stack[-1] if self.stack else None
            if not self._truthy(val):
                self.ip = arg
        elif opcode == OpCode.JMP_IF_TRUE:
            val = self.stack[-1] if self.stack else None
            if self._truthy(val):
                self.ip = arg

        # ─── Variables ─────────────────────────────────────────────────
        elif opcode == OpCode.LOAD:
            # Load local variable (from current frame's locals or stack)
            if self.frames:
                self.stack.append(self.frames[-1][3][arg])
            else:
                self.stack.append(self.stack[arg])
        elif opcode == OpCode.STORE:
            val = self.stack.pop()
            if self.frames:
                self.frames[-1][3][arg] = val
            else:
                while len(self.stack) <= arg:
                    self.stack.append(None)
                self.stack[arg] = val
        elif opcode == OpCode.LOAD_GLOBAL:
            name = self.chunk.constants[arg]
            if name in self.globals:
                self.stack.append(self.globals[name])
            else:
                raise RuntimeError_(f"Undefined variable '{name}'")
        elif opcode == OpCode.STORE_GLOBAL:
            name = self.chunk.constants[arg]
            val = self.stack.pop()
            self.globals[name] = val

        # ─── Functions ─────────────────────────────────────────────────
        elif opcode == OpCode.CALL:
            arg_count = arg
            callee = self.stack.pop() if self.stack else None
            args = []
            for _ in range(arg_count):
                args.insert(0, self.stack.pop())

            if isinstance(callee, SamratFunctionVM):
                # User-defined function
                func_chunk, param_count = self._function_chunks[callee.name]
                # Create locals for parameters
                func_locals = list(args) + [None] * (param_count - len(args))
                # Save state
                self.frames.append((self.ip, self.chunk, len(self.stack), func_locals))
                # Switch to function chunk
                self.chunk = func_chunk
                self.ip = 0
            elif isinstance(callee, BuiltInVM):
                result = callee.call(args)
                if result is not None:
                    self.stack.append(result)
            elif callable(callee):
                result = callee(*args)
                if result is not None:
                    self.stack.append(result)
            else:
                raise RuntimeError_(f"'{type(callee).__name__}' is not callable")

        elif opcode == OpCode.RETURN:
            ret_val = self.stack.pop() if self.stack else None
            if self.frames:
                # Restore previous frame
                self.ip, self.chunk, stack_size, _ = self.frames.pop()
                # Trim stack to previous size
                while len(self.stack) > stack_size:
                    self.stack.pop()
                self.stack.append(ret_val)
            else:
                raise ReturnException(ret_val)

        elif opcode == OpCode.MAKE_FUNCTION:
            name = self.chunk.constants[arg]
            # Function chunks are already registered during compilation
            # Just push a placeholder
            if name in self._function_chunks:
                self.stack.append(SamratFunctionVM(name))

        # ─── Data Structures ────────────────────────────────────────────
        elif opcode == OpCode.MAKE_ARRAY:
            count = arg
            arr = []
            for _ in range(count):
                arr.insert(0, self.stack.pop())
            self.stack.append(arr)

        elif opcode == OpCode.MAKE_MAP:
            count = arg
            result = {}
            for _ in range(count):
                val = self.stack.pop()
                key = self.stack.pop()
                result[key] = val
            self.stack.append(result)

        elif opcode == OpCode.GET_ITEM:
            index = self.stack.pop()
            obj = self.stack.pop()
            if isinstance(obj, list):
                self.stack.append(obj[index])
            elif isinstance(obj, dict):
                self.stack.append(obj[index])
            elif isinstance(obj, str):
                self.stack.append(obj[index])

        elif opcode == OpCode.SET_ITEM:
            val = self.stack.pop()
            index = self.stack.pop()
            obj = self.stack.pop()
            if isinstance(obj, list):
                obj[index] = val
            elif isinstance(obj, dict):
                obj[index] = val
            self.stack.append(val)

        elif opcode == OpCode.GET_ATTR:
            name = self.chunk.constants[arg]
            obj = self.stack.pop()
            if hasattr(obj, name):
                attr = getattr(obj, name)
                if callable(attr):
                    self.stack.append(BuiltInVM(name, lambda args, f=attr: f(*args)))
                else:
                    self.stack.append(attr)
            elif isinstance(obj, dict) and name in obj:
                self.stack.append(obj[name])
            else:
                raise RuntimeError_(f"'{type(obj).__name__}' has no attribute '{name}'")

        elif opcode == OpCode.SET_ATTR:
            name = self.chunk.constants[arg]
            val = self.stack.pop()
            obj = self.stack.pop()
            setattr(obj, name, val)

        elif opcode == OpCode.DUP:
            if self.stack:
                self.stack.append(self.stack[-1])

        # ─── Built-in Functions ─────────────────────────────────────────
        elif opcode == OpCode.PRINT:
            count = arg
            parts = []
            for _ in range(count):
                parts.insert(0, self._stringify(self.stack.pop()))
            print(' '.join(parts))

        elif opcode == OpCode.INPUT_:
            try:
                self.stack.append(input())
            except EOFError:
                self.stack.append('')

        elif opcode == OpCode.INT_CONV:
            val = self.stack.pop()
            self.stack.append(int(val))

        elif opcode == OpCode.FLOAT_CONV:
            val = self.stack.pop()
            self.stack.append(float(val))

        elif opcode == OpCode.STR_CONV:
            val = self.stack.pop()
            self.stack.append(self._stringify(val))

        elif opcode == OpCode.BOOL_CONV:
            val = self.stack.pop()
            self.stack.append(bool(val))

        elif opcode == OpCode.TYPE:
            val = self.stack.pop()
            self.stack.append(self._type_name(val))

        elif opcode == OpCode.LEN:
            val = self.stack.pop()
            self.stack.append(len(val))

        # ─── Error Handling ─────────────────────────────────────────────
        elif opcode == OpCode.THROW:
            val = self.stack.pop()
            raise RuntimeError_(self._stringify(val))

        elif opcode == OpCode.PUSH_HANDLER:
            self.handler_stack.append((arg, self.chunk))

        elif opcode == OpCode.POP_HANDLER:
            if self.handler_stack:
                self.handler_stack.pop()

        # ─── Class Support ──────────────────────────────────────────────
        elif opcode == OpCode.MAKE_CLASS:
            name = self.chunk.constants[arg]
            self.stack.append(type(name, (), {}))

        elif opcode == OpCode.LOAD_THIS:
            if self._current_instance:
                self.stack.append(self._current_instance)
            else:
                raise RuntimeError_("'this' used outside of class context")

        elif opcode == OpCode.MAKE_RANGE:
            end = self.stack.pop()
            start = self.stack.pop()
            self.stack.append(range(start, end))

        elif opcode == OpCode.HALT:
            self.ip = len(self.chunk.code)  # Stop execution

    def _truthy(self, value) -> bool:
        """Determine truthiness of a value."""
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, int):
            return value != 0
        if isinstance(value, float):
            return value != 0.0
        if isinstance(value, str):
            return len(value) > 0
        if isinstance(value, list):
            return len(value) > 0
        if isinstance(value, dict):
            return len(value) > 0
        return True

    def _stringify(self, value) -> str:
        """Convert value to string representation."""
        if value is None:
            return 'null'
        if isinstance(value, bool):
            return 'true' if value else 'false'
        if isinstance(value, float):
            if value == int(value):
                return str(int(value))
            return str(value)
        if isinstance(value, list):
            return '[' + ', '.join(self._stringify(e) for e in value) + ']'
        if isinstance(value, dict):
            entries = [f'{self._stringify(k)}: {self._stringify(v)}' for k, v in value.items()]
            return '{' + ', '.join(entries) + '}'
        return str(value)

    def _type_name(self, value) -> str:
        """Get the type name of a value."""
        if value is None:
            return 'null'
        if isinstance(value, bool):
            return 'bool'
        if isinstance(value, int):
            return 'int'
        if isinstance(value, float):
            return 'float'
        if isinstance(value, str):
            return 'str'
        if isinstance(value, list):
            return '[' + str(len(value)) + ' elements]'
        if isinstance(value, dict):
            return '{' + str(len(value)) + ' entries}'
        return 'object'


class ReturnException(Exception):
    """Used to unwind the stack on function returns."""
    def __init__(self, value):
        self.value = value


class SamratFunctionVM:
    """Represents a compiled Samrat function in the VM."""
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f'<function {self.name}>'


class BuiltInVM:
    """Represents a built-in function in the VM."""
    def __init__(self, name: str, impl):
        self.name = name
        self.impl = impl

    def call(self, args: list):
        return self.impl(args)

    def __repr__(self):
        return f'<built-in function {self.name}>'
