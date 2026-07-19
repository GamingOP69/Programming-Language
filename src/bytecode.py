"""
Samrat Programming Language — Bytecode Instruction Set

Defines the bytecode instruction set for the Samrat virtual machine.
Each instruction is a single byte opcode, optionally followed by operands.

Architecture: Stack-based VM (like JVM or CPython)
- All operations work on a value stack
- Local variables accessed by stack slot index
- Constants stored in a pool and referenced by index
- Each function has its own Chunk of bytecode
"""

from enum import Enum, auto


class OpCode(Enum):
    """All bytecode instructions for the Samrat VM."""

    # Stack operations
    PUSH_NULL = auto()       # Push null onto stack
    PUSH_TRUE = auto()       # Push true onto stack
    PUSH_FALSE = auto()      # Push false onto stack
    PUSH_INT = auto()        # Push integer constant (arg: const index)
    PUSH_FLOAT = auto()      # Push float constant (arg: const index)
    PUSH_STRING = auto()     # Push string constant (arg: const index)
    POP = auto()             # Pop value from stack

    # Arithmetic
    ADD = auto()             # a + b
    SUB = auto()             # a - b
    MUL = auto()             # a * b
    DIV = auto()             # a / b
    MOD = auto()             # a % b
    POW = auto()             # a ** b
    NEG = auto()             # -a

    # Comparison
    EQ = auto()              # a == b
    NEQ = auto()             # a != b
    LT = auto()              # a < b
    GT = auto()              # a > b
    LE = auto()              # a <= b
    GE = auto()              # a >= b

    # Logical
    AND = auto()             # a and b (short-circuit)
    OR = auto()              # a or b (short-circuit)
    NOT = auto()             # not a

    # Bitwise
    BIT_AND = auto()         # a & b
    BIT_OR = auto()          # a | b
    BIT_XOR = auto()         # a ^ b
    BIT_NOT = auto()         # ~a
    SHL = auto()             # a << b
    SHR = auto()             # a >> b

    # Control flow
    JMP = auto()             # Unconditional jump (arg: offset)
    JMP_IF_FALSE = auto()    # Pop and jump if false (arg: offset)
    JMP_IF_TRUE = auto()     # Pop and jump if true (arg: offset)

    # Functions
    CALL = auto()            # Call function (arg: arg count)
    RETURN = auto()          # Return from function
    MAKE_FUNCTION = auto()   # Create function object (arg: const index for name)

    # Variables
    LOAD = auto()            # Load local variable (arg: slot index)
    STORE = auto()           # Store to local variable (arg: slot index)
    LOAD_GLOBAL = auto()     # Load global variable (arg: const index for name)
    STORE_GLOBAL = auto()    # Store to global variable (arg: const index for name)

    # Data structures
    MAKE_ARRAY = auto()      # Make array (arg: element count)
    MAKE_MAP = auto()        # Make map (arg: entry count)
    GET_ITEM = auto()        # Get item (obj[index])
    SET_ITEM = auto()        # Set item (obj[index] = value)
    GET_ATTR = auto()        # Get attribute (obj.name) (arg: const index for name)
    SET_ATTR = auto()        # Set attribute (obj.name = value) (arg: const index for name)
    DUP = auto()             # Duplicate top of stack

    # Built-in functions
    PRINT = auto()           # Print (arg: arg count)
    INPUT_ = auto()          # Input
    INT_CONV = auto()        # int()
    FLOAT_CONV = auto()      # float()
    STR_CONV = auto()        # str()
    BOOL_CONV = auto()       # bool()
    TYPE = auto()            # type()
    LEN = auto()             # len()

    # Error handling
    THROW = auto()           # Throw exception
    PUSH_HANDLER = auto()    # Push exception handler (arg: catch offset)
    POP_HANDLER = auto()     # Pop exception handler

    # Class support
    MAKE_CLASS = auto()      # Create class
    MAKE_INSTANCE = auto()   # Create instance (arg: field count)
    LOAD_THIS = auto()       # Load 'this'

    # Range
    MAKE_RANGE = auto()      # Create range object

    # Halt
    HALT = auto()            # Stop execution


class Chunk:
    """
    A chunk of bytecode with associated constants and line info.

    Attributes:
        code: List of (opcode, arg) tuples. arg is None for no-arg instructions.
        constants: List of constant values referenced by index.
        lines: List of line numbers corresponding to each instruction.
        name: Name of this chunk (function name or "<script>").
    """

    def __init__(self, name: str = "<script>"):
        self.code = []          # List of (OpCode, arg) tuples
        self.constants = []     # List of constant values
        self.lines = []         # List of line numbers
        self.name = name

    def emit(self, opcode: OpCode, arg=None, line: int = 0):
        """Emit a single instruction."""
        self.code.append((opcode, arg))
        self.lines.append(line)

    def add_constant(self, value) -> int:
        """Add a constant to the pool and return its index."""
        self.constants.append(value)
        return len(self.constants) - 1

    def __repr__(self) -> str:
        return f"Chunk({self.name}, {len(self.code)} instr, {len(self.constants)} consts)"
