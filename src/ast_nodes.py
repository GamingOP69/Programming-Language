"""
Samrat Programming Language — Abstract Syntax Tree (AST) Nodes

This module defines all AST node types used by the parser. Each node
represents a language construct in the tree structure that the parser
produces and the interpreter consumes.

The AST is organized hierarchically:
- Program (root) contains Statements
- Statements contain Expressions
- Expressions form the leaves of the tree

Every node stores its source location (line, column) for error reporting.
"""


class ASTNode:
    """Base class for all AST nodes."""

    def __init__(self, line: int = 0, column: int = 0):
        self.line = line
        self.column = column

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


# ─── Statements ───────────────────────────────────────────────────────────

class Program(ASTNode):
    """Root node. Contains a list of statements."""

    def __init__(self, statements: list, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.statements = statements

    def __repr__(self) -> str:
        return f"Program({len(self.statements)} statements)"


class Block(ASTNode):
    """A block of statements enclosed in { }."""

    def __init__(self, statements: list, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.statements = statements

    def __repr__(self) -> str:
        return f"Block({len(self.statements)} statements)"


class ExpressionStatement(ASTNode):
    """A statement that consists of a single expression."""

    def __init__(self, expression, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.expression = expression

    def __repr__(self) -> str:
        return f"ExpressionStatement({self.expression})"


class VarDeclaration(ASTNode):
    """Variable declaration: let name[: type] = value"""

    def __init__(self, name: str, var_type: str, initializer,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.name = name
        self.var_type = var_type  # None if type is inferred
        self.initializer = initializer

    def __repr__(self) -> str:
        return f"VarDeclaration({self.name}, type={self.var_type})"


class ConstDeclaration(ASTNode):
    """Constant declaration: const name[: type] = value"""

    def __init__(self, name: str, const_type: str, initializer,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.name = name
        self.const_type = const_type
        self.initializer = initializer

    def __repr__(self) -> str:
        return f"ConstDeclaration({self.name}, type={self.const_type})"


class Assignment(ASTNode):
    """Assignment: target = value or target op= value"""

    def __init__(self, target, value, operator: str = '=',
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.target = target        # Usually an Identifier or MemberAccess
        self.value = value
        self.operator = operator    # '=', '+=', '-=', '*=', '/=', '%='

    def __repr__(self) -> str:
        return f"Assignment({self.target} {self.operator} {self.value})"


class IfStatement(ASTNode):
    """If-elif-else conditional."""

    def __init__(self, condition, then_block,
                 elif_conditions: list = None, elif_blocks: list = None,
                 else_block=None,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.condition = condition
        self.then_block = then_block
        self.elif_conditions = elif_conditions or []
        self.elif_blocks = elif_blocks or []
        self.else_block = else_block

    def __repr__(self) -> str:
        parts = ["If"]
        parts.append(f"elif count: {len(self.elif_conditions)}")
        if self.else_block:
            parts.append("has else")
        return f"IfStatement({' | '.join(parts)})"


class WhileLoop(ASTNode):
    """While loop: while condition { body }"""

    def __init__(self, condition, body,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.condition = condition
        self.body = body

    def __repr__(self) -> str:
        return f"WhileLoop({self.condition})"


class ForLoop(ASTNode):
    """For loop: for variable in iterable { body }"""

    def __init__(self, variable: str, iterable, body,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.variable = variable
        self.iterable = iterable
        self.body = body

    def __repr__(self) -> str:
        return f"ForLoop({self.variable} in {self.iterable})"


class BreakStatement(ASTNode):
    """Break statement."""

    def __init__(self, line: int = 0, column: int = 0):
        super().__init__(line, column)

    def __repr__(self) -> str:
        return "BreakStatement()"


class ContinueStatement(ASTNode):
    """Continue statement."""

    def __init__(self, line: int = 0, column: int = 0):
        super().__init__(line, column)

    def __repr__(self) -> str:
        return "ContinueStatement()"


class ReturnStatement(ASTNode):
    """Return statement: return [value]"""

    def __init__(self, value=None, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.value = value

    def __repr__(self) -> str:
        return f"ReturnStatement({self.value})"


class FunctionDef(ASTNode):
    """Function definition: func name(params) -> return_type { body }"""

    def __init__(self, name: str, parameters: list, return_type: str,
                 body, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.name = name
        self.parameters = parameters  # List of Parameter
        self.return_type = return_type
        self.body = body

    def __repr__(self) -> str:
        return (f"FunctionDef({self.name}, "
                f"{len(self.parameters)} params, "
                f"returns {self.return_type})")


class Parameter(ASTNode):
    """Function parameter: name: type [= default]"""

    def __init__(self, name: str, param_type: str, default_value=None,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.name = name
        self.param_type = param_type
        self.default_value = default_value

    def __repr__(self) -> str:
        return f"Parameter({self.name}: {self.param_type})"


class ClassDef(ASTNode):
    """Class definition: class Name { members }"""

    def __init__(self, name: str, fields: list, constructor, methods: list,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.name = name
        self.fields = fields           # List of VarDeclaration
        self.constructor = constructor  # ConstructorDef or None
        self.methods = methods         # List of FunctionDef

    def __repr__(self) -> str:
        return (f"ClassDef({self.name}, "
                f"{len(self.fields)} fields, "
                f"{len(self.methods)} methods)")


class ConstructorDef(ASTNode):
    """Constructor definition: constructor(params) { body }"""

    def __init__(self, parameters: list, body,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.parameters = parameters
        self.body = body

    def __repr__(self) -> str:
        return f"ConstructorDef({len(self.parameters)} params)"


class TryStatement(ASTNode):
    """Try-catch: try { body } catch error_var { handler }"""

    def __init__(self, try_block, catch_var: str, catch_block,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.try_block = try_block
        self.catch_var = catch_var
        self.catch_block = catch_block

    def __repr__(self) -> str:
        return f"TryStatement(catch {self.catch_var})"


class ThrowStatement(ASTNode):
    """Throw statement: throw value"""

    def __init__(self, value, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.value = value

    def __repr__(self) -> str:
        return f"ThrowStatement({self.value})"


class ImportStatement(ASTNode):
    """Import statement: import name or import names from module"""

    def __init__(self, names: list, module: str = None, alias: str = None,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.names = names      # List of identifiers to import
        self.module = module    # Module name (None if importing module itself)
        self.alias = alias      # Optional alias

    def __repr__(self) -> str:
        return f"ImportStatement({self.names}, from={self.module})"


# ─── Expressions ──────────────────────────────────────────────────────────

class Literal(ASTNode):
    """A literal value (int, float, str, bool, null)."""

    def __init__(self, value, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.value = value

    def __repr__(self) -> str:
        return f"Literal({self.value!r})"


class Identifier(ASTNode):
    """An identifier reference (variable name, function name, etc.)."""

    def __init__(self, name: str, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.name = name

    def __repr__(self) -> str:
        return f"Identifier({self.name})"


class BinaryOp(ASTNode):
    """Binary operation: left operator right"""

    def __init__(self, left, operator: str, right,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self) -> str:
        return f"BinaryOp({self.left} {self.operator} {self.right})"


class UnaryOp(ASTNode):
    """Unary operation: operator operand"""

    def __init__(self, operator: str, operand,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.operator = operator
        self.operand = operand

    def __repr__(self) -> str:
        return f"UnaryOp({self.operator} {self.operand})"


class MemberAccess(ASTNode):
    """Member access: object.member"""

    def __init__(self, obj, member: str,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.object = obj       # The object being accessed
        self.member = member    # The member name (string for `.name`)

    def __repr__(self) -> str:
        return f"MemberAccess({self.object}.{self.member})"


class Subscript(ASTNode):
    """Subscript/index access: object[index]"""

    def __init__(self, obj, index,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.object = obj
        self.index = index

    def __repr__(self) -> str:
        return f"Subscript({self.object}[{self.index}])"


class FunctionCall(ASTNode):
    """Function call: callee(arguments)"""

    def __init__(self, callee, arguments: list,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.callee = callee        # The function being called
        self.arguments = arguments  # List of argument expressions

    def __repr__(self) -> str:
        return f"FunctionCall({self.callee}, {len(self.arguments)} args)"


class ArrayLiteral(ASTNode):
    """Array literal: [element, element, ...]"""

    def __init__(self, elements: list,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.elements = elements

    def __repr__(self) -> str:
        return f"ArrayLiteral({len(self.elements)} elements)"


class MapLiteral(ASTNode):
    """Map literal: {key: value, key: value, ...}"""

    def __init__(self, entries: list,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.entries = entries  # List of (key, value) tuples

    def __repr__(self) -> str:
        return f"MapLiteral({len(self.entries)} entries)"


class RangeLiteral(ASTNode):
    """Range literal: start..end (inclusive start, exclusive end)"""

    def __init__(self, start, end,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.start = start
        self.end = end

    def __repr__(self) -> str:
        return f"RangeLiteral({self.start}..{self.end})"


class ThisExpression(ASTNode):
    """The 'this' keyword expression."""

    def __init__(self, line: int = 0, column: int = 0):
        super().__init__(line, column)

    def __repr__(self) -> str:
        return "ThisExpression()"