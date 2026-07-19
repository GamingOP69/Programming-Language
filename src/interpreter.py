"""
Samrat Programming Language — Tree-Walking Interpreter

The interpreter is the fourth and final phase of the Samrat compiler pipeline
for Version 1.0. It walks the AST and executes the program directly.

This interpreter:
- Evaluates expressions and executes statements
- Manages runtime environments with nested scopes
- Supports all Samrat language features
- Implements built-in functions
- Handles runtime errors with descriptive messages
- Supports recursion, closures, and class instantiation

Usage:
    from lexer import Lexer
    from parser import Parser
    from semantic import SemanticAnalyzer
    from interpreter import Interpreter
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    analyzer = SemanticAnalyzer()
    if analyzer.analyze(ast):
        interpreter = Interpreter()
        result = interpreter.interpret(ast)
"""

from ast_nodes import (
    Program, ExpressionStatement, Block, VarDeclaration, ConstDeclaration,
    Assignment, Identifier, MemberAccess, Subscript, ReturnStatement,
    BreakStatement, ContinueStatement, IfStatement, WhileLoop, ForLoop,
    FunctionDef, ClassDef, ConstructorDef, TryStatement, ThrowStatement,
    ImportStatement, Literal, ThisExpression, RangeLiteral, BinaryOp,
    UnaryOp, FunctionCall, ArrayLiteral, MapLiteral,
)
from errors import RuntimeError_, TypeError_


class ReturnValue(Exception):
    """Exception used to unwind the call stack on return statements."""

    def __init__(self, value):
        self.value = value


class BreakException(Exception):
    """Exception used to exit loops on break statements."""
    pass


class ContinueException(Exception):
    """Exception used to skip to next loop iteration."""
    pass


class Environment:
    """
    Runtime environment for variable storage with scope chaining.

    Each environment has:
    - A dictionary of variable bindings
    - A reference to the enclosing (parent) environment
    """

    def __init__(self, parent=None):
        self.values = {}
        self.parent = parent

    def define(self, name: str, value):
        """Define a new variable in the current environment."""
        self.values[name] = value

    def get(self, name: str):
        """Get a variable value, searching parent environments."""
        if name in self.values:
            return self.values[name]
        if self.parent:
            return self.parent.get(name)
        raise RuntimeError_(f"Undefined variable '{name}'")

    def assign(self, name: str, value):
        """Assign to an existing variable, searching parent environments."""
        if name in self.values:
            self.values[name] = value
            return
        if self.parent:
            self.parent.assign(name, value)
            return
        raise RuntimeError_(f"Undefined variable '{name}'")

    def has(self, name: str) -> bool:
        """Check if a variable exists in this environment or parents."""
        if name in self.values:
            return True
        if self.parent:
            return self.parent.has(name)
        return False


class Interpreter:
    """
    Tree-walking interpreter for Samrat programs.

    Attributes:
        environment: The current runtime environment.
        globals: The global environment (for built-in functions).
    """

    def __init__(self):
        self.environment = Environment()
        self.globals = self.environment
        self._register_builtins()

    def interpret(self, node) -> object:
        """
        Interpret (execute) an AST node.

        Args:
            node: The AST node to execute (typically a Program).

        Returns:
            The result of the program execution.
        """
        try:
            return self._visit(node)
        except RuntimeError_ as e:
            print(f"RuntimeError: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise

    def _register_builtins(self):
        """Register all built-in functions in the global environment."""
        self.globals.define('print', BuiltInFunction('print', 0, None, self._builtin_print))
        self.globals.define('input', BuiltInFunction('input', 0, 1, self._builtin_input))
        self.globals.define('int', BuiltInFunction('int', 1, 1, self._builtin_int))
        self.globals.define('float', BuiltInFunction('float', 1, 1, self._builtin_float))
        self.globals.define('str', BuiltInFunction('str', 1, 1, self._builtin_str))
        self.globals.define('bool', BuiltInFunction('bool', 1, 1, self._builtin_bool))
        self.globals.define('type', BuiltInFunction('type', 1, 1, self._builtin_type))
        self.globals.define('len', BuiltInFunction('len', 1, 1, self._builtin_len))

    # ─── Built-in Function Implementations ────────────────────────────────

    def _builtin_print(self, args: list):
        """print(value1, value2, ...)"""
        strings = [str(self._stringify(a)) for a in args]
        print(' '.join(strings))

    def _builtin_input(self, args: list):
        """input(prompt?)"""
        if args:
            print(str(self._stringify(args[0])), end='')
        try:
            return input()
        except EOFError:
            return ''

    def _builtin_int(self, args: list):
        """int(value)"""
        val = args[0]
        if isinstance(val, int):
            return val
        if isinstance(val, float):
            return int(val)
        if isinstance(val, str):
            try:
                return int(val)
            except ValueError:
                raise RuntimeError_(f"Cannot convert '{val}' to int")
        if isinstance(val, bool):
            return 1 if val else 0
        raise RuntimeError_(f"Cannot convert {type(val).__name__} to int")

    def _builtin_float(self, args: list):
        """float(value)"""
        val = args[0]
        if isinstance(val, float):
            return val
        if isinstance(val, int):
            return float(val)
        if isinstance(val, str):
            try:
                return float(val)
            except ValueError:
                raise RuntimeError_(f"Cannot convert '{val}' to float")
        if isinstance(val, bool):
            return 1.0 if val else 0.0
        raise RuntimeError_(f"Cannot convert {type(val).__name__} to float")

    def _builtin_str(self, args: list):
        """str(value)"""
        return self._stringify(args[0])

    def _builtin_bool(self, args: list):
        """bool(value)"""
        val = args[0]
        if isinstance(val, bool):
            return val
        if isinstance(val, int):
            return val != 0
        if isinstance(val, float):
            return val != 0.0
        if isinstance(val, str):
            return len(val) > 0
        if val is None:
            return False
        if isinstance(val, list):
            return len(val) > 0
        if isinstance(val, dict):
            return len(val) > 0
        return True

    def _builtin_type(self, args: list):
        """type(value)"""
        val = args[0]
        if val is None:
            return 'null'
        if isinstance(val, bool):
            return 'bool'
        if isinstance(val, int):
            return 'int'
        if isinstance(val, float):
            return 'float'
        if isinstance(val, str):
            return 'str'
        if isinstance(val, list):
            return f'[{len(val)} elements]'
        if isinstance(val, dict):
            return f'{{{len(val)} entries}}'
        if isinstance(val, SamratObject):
            return val.class_name
        return 'object'

    def _builtin_len(self, args: list):
        """len(collection)"""
        val = args[0]
        if isinstance(val, str):
            return len(val)
        if isinstance(val, list):
            return len(val)
        if isinstance(val, dict):
            return len(val)
        raise RuntimeError_(f"Cannot get length of {type(val).__name__}")

    def _stringify(self, value) -> str:
        """Convert a Samrat value to its string representation."""
        if value is None:
            return 'null'
        if isinstance(value, bool):
            return 'true' if value else 'false'
        if isinstance(value, float):
            if value == int(value):
                return str(int(value))
            return str(value)
        if isinstance(value, list):
            elements = [self._stringify(e) for e in value]
            return '[' + ', '.join(elements) + ']'
        if isinstance(value, dict):
            entries = [f'{self._stringify(k)}: {self._stringify(v)}' for k, v in value.items()]
            return '{' + ', '.join(entries) + '}'
        if isinstance(value, SamratObject):
            return f'<{value.class_name} instance>'
        return str(value)

    # ─── Visitor Dispatch ────────────────────────────────────────────────

    def _visit(self, node):
        """Dispatch to the appropriate visitor method."""
        node_type = type(node).__name__
        visitor = getattr(self, f'_visit_{node_type}', self._visit_default)
        return visitor(node)

    def _visit_default(self, node):
        """Default visitor."""
        return None

    # ─── Program ──────────────────────────────────────────────────────────

    def _visit_Program(self, node: Program):
        """Execute all top-level statements."""
        result = None
        for stmt in node.statements:
            result = self._visit(stmt)
        return result

    # ─── Statements ───────────────────────────────────────────────────────

    def _visit_ExpressionStatement(self, node: ExpressionStatement):
        """Evaluate an expression statement."""
        return self._visit(node.expression)

    def _visit_Block(self, node: Block):
        """Execute a block with a new environment."""
        previous = self.environment
        self.environment = Environment(previous)
        try:
            result = None
            for stmt in node.statements:
                result = self._visit(stmt)
            return result
        finally:
            self.environment = previous

    def _visit_VarDeclaration(self, node: VarDeclaration):
        """Execute a variable declaration."""
        value = None
        if node.initializer:
            value = self._visit(node.initializer)
        else:
            # Default values based on type
            if node.var_type == 'int':
                value = 0
            elif node.var_type == 'float':
                value = 0.0
            elif node.var_type == 'str':
                value = ''
            elif node.var_type == 'bool':
                value = False
            elif node.var_type and node.var_type.startswith('['):
                value = []
            elif node.var_type and node.var_type.startswith('{'):
                value = {}
            else:
                value = None
        self.environment.define(node.name, value)
        return value

    def _visit_ConstDeclaration(self, node: ConstDeclaration):
        """Execute a constant declaration."""
        value = self._visit(node.initializer)
        self.environment.define(node.name, value)
        return value

    def _visit_Assignment(self, node: Assignment):
        """Execute an assignment."""
        value = self._visit(node.value)

        if isinstance(node.target, Identifier):
            name = node.target.name
            # Apply compound assignment operators
            if node.operator != '=':
                current = self.environment.get(name)
                value = self._apply_compound_op(current, value, node.operator)
            self.environment.assign(name, value)
        elif isinstance(node.target, MemberAccess):
            obj = self._visit(node.target.object)
            if isinstance(obj, SamratObject):
                obj.set_field(node.target.member, value)
            elif isinstance(obj, dict):
                obj[node.target.member] = value
        elif isinstance(node.target, Subscript):
            obj = self._visit(node.target.object)
            index = self._visit(node.target.index)
            if isinstance(obj, list):
                if not isinstance(index, int):
                    raise RuntimeError_(f"Array index must be int, got {type(index).__name__}")
                if index < 0 or index >= len(obj):
                    raise RuntimeError_(f"Index {index} out of bounds for array of length {len(obj)}")
                obj[index] = value
            elif isinstance(obj, dict):
                obj[index] = value
        return value

    def _apply_compound_op(self, current, value, operator: str):
        """Apply a compound assignment operator."""
        ops = {
            '+=': lambda a, b: a + b,
            '-=': lambda a, b: a - b,
            '*=': lambda a, b: a * b,
            '/=': lambda a, b: a / b,
            '%=': lambda a, b: a % b,
        }
        if operator in ops:
            return ops[operator](current, value)
        return value

    def _visit_ReturnStatement(self, node: ReturnStatement):
        """Execute a return statement."""
        value = None
        if node.value:
            value = self._visit(node.value)
        raise ReturnValue(value)

    def _visit_BreakStatement(self, node: BreakStatement):
        """Execute a break statement."""
        raise BreakException()

    def _visit_ContinueStatement(self, node: ContinueStatement):
        """Execute a continue statement."""
        raise ContinueException()

    def _visit_IfStatement(self, node: IfStatement):
        """Execute an if/elif/else statement."""
        condition = self._visit(node.condition)
        if self._is_truthy(condition):
            return self._visit(node.then_block)
        for i in range(len(node.elif_conditions)):
            elif_cond = self._visit(node.elif_conditions[i])
            if self._is_truthy(elif_cond):
                return self._visit(node.elif_blocks[i])
        if node.else_block:
            return self._visit(node.else_block)
        return None

    def _visit_WhileLoop(self, node: WhileLoop):
        """Execute a while loop."""
        result = None
        while True:
            condition = self._visit(node.condition)
            if not self._is_truthy(condition):
                break
            try:
                result = self._visit(node.body)
            except BreakException:
                break
            except ContinueException:
                continue
        return result

    def _visit_ForLoop(self, node: ForLoop):  # noqa: C901
        """Execute a for loop."""
        iterable = self._visit(node.iterable)
        result = None

        # Create a new environment for the loop variable
        previous = self.environment
        self.environment = Environment(previous)

        try:
            if isinstance(iterable, range):
                for i in iterable:
                    self.environment.define(node.variable, i)
                    try:
                        result = self._visit(node.body)
                    except BreakException:
                        break
                    except ContinueException:
                        continue
            elif isinstance(iterable, list):
                for i, item in enumerate(iterable):
                    self.environment.define(node.variable, item)
                    try:
                        result = self._visit(node.body)
                    except BreakException:
                        break
                    except ContinueException:
                        continue
            elif isinstance(iterable, str):
                for char in iterable:
                    self.environment.define(node.variable, char)
                    try:
                        result = self._visit(node.body)
                    except BreakException:
                        break
                    except ContinueException:
                        continue
        finally:
            self.environment = previous

        return result

    def _visit_FunctionDef(self, node: FunctionDef):
        """Define a function."""
        func = SamratFunction(node.name, node.parameters, node.body,
                              self.environment)
        self.environment.define(node.name, func)
        return func

    def _visit_ClassDef(self, node: ClassDef):
        """Define a class."""
        cls = SamratClass(node.name, node.fields, node.constructor, node.methods)
        self.environment.define(node.name, cls)
        return cls

    def _visit_ConstructorDef(self, node: ConstructorDef):
        """Constructor is handled during class instantiation."""
        return None

    def _visit_TryStatement(self, node: TryStatement):
        """Execute a try/catch statement."""
        try:
            return self._visit(node.try_block)
        except RuntimeError_ as e:
            # Catch the error - extract just the message part
            error_msg = e.message if hasattr(e, 'message') else str(e)
            previous = self.environment
            self.environment = Environment(previous)
            self.environment.define(node.catch_var, error_msg)
            try:
                result = self._visit(node.catch_block)
                return result
            finally:
                self.environment = previous
        except Exception as e:
            # Catch any other runtime errors
            error_msg = str(e)
            previous = self.environment
            self.environment = Environment(previous)
            self.environment.define(node.catch_var, error_msg)
            try:
                result = self._visit(node.catch_block)
                return result
            finally:
                self.environment = previous

    def _visit_ThrowStatement(self, node: ThrowStatement):
        """Execute a throw statement."""
        value = self._visit(node.value)
        raise RuntimeError_(self._stringify(value))

    def _visit_ImportStatement(self, node: ImportStatement):
        """Execute an import statement (register module)."""
        # For 1.0, standard library modules are built-in
        module_name = node.module or node.names[0]
        if module_name in ('math', 'string', 'time'):
            module = self._create_standard_module(module_name)
            if node.alias:
                self.environment.define(node.alias, module)
            elif node.module:
                # import name from module
                for name in node.names:
                    if hasattr(module, name):
                        self.environment.define(name, getattr(module, name))
            else:
                self.environment.define(module_name, module)
        return None

    def _create_standard_module(self, name: str):
        """Create a standard library module object."""
        if name == 'math':
            import math
            return math
        elif name == 'string':
            return StringModule()
        elif name == 'time':
            import time
            return time
        return {}

    # ─── Expressions ──────────────────────────────────────────────────────

    def _visit_Literal(self, node: Literal):
        """Return the literal value."""
        return node.value

    def _visit_Identifier(self, node: Identifier):
        """Look up and return the identifier's value."""
        return self.environment.get(node.name)

    def _visit_BinaryOp(self, node: BinaryOp):  # noqa: C901
        """Evaluate a binary operation."""
        left = self._visit(node.left)
        right = self._visit(node.right)
        op = node.operator

        # Range operator
        if op == '..':
            if not isinstance(left, int) or not isinstance(right, int):
                raise RuntimeError_(
                    f"Range requires integer bounds, got {type(left).__name__} "
                    f"and {type(right).__name__}"
                )
            return range(left, right)

        # Arithmetic
        if op == '+':
            if isinstance(left, str) and isinstance(right, str):
                return left + right
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return left + right
            raise TypeError_(f"Cannot add {type(left).__name__} and {type(right).__name__}")
        if op == '-':
            return left - right
        if op == '*':
            return left * right
        if op == '/':
            if isinstance(left, int) and isinstance(right, int):
                return left / right  # Returns float
            return left / right
        if op == '%':
            return left % right
        if op == '**':
            return left ** right

        # Comparison
        if op == '==':
            return left == right
        if op == '!=':
            return left != right
        if op == '<':
            return left < right
        if op == '>':
            return left > right
        if op == '<=':
            return left <= right
        if op == '>=':
            return left >= right

        # Logical
        if op == 'and':
            return self._is_truthy(left) and self._is_truthy(right)
        if op == 'or':
            return self._is_truthy(left) or self._is_truthy(right)

        # Bitwise
        if op == '&':
            return left & right
        if op == '|':
            return left | right
        if op == '^':
            return left ^ right
        if op == '<<':
            return left << right
        if op == '>>':
            return left >> right

        raise RuntimeError_(f"Unknown operator '{op}'")

    def _visit_UnaryOp(self, node: UnaryOp):
        """Evaluate a unary operation."""
        operand = self._visit(node.operand)

        if node.operator == '-':
            return -operand
        if node.operator == 'not':
            return not self._is_truthy(operand)
        if node.operator == '~':
            return ~operand

        raise RuntimeError_(f"Unknown unary operator '{node.operator}'")

    def _visit_MemberAccess(self, node: MemberAccess):  # noqa: C901
        """Evaluate member access."""
        obj = self._visit(node.object)

        if isinstance(obj, SamratObject):
            return obj.get_field(node.member)
        if isinstance(obj, list):
            if node.member == 'append':
                return BuiltInFunction('append', 1, 1, lambda args: obj.append(args[0]))
            if node.member == 'pop':
                return BuiltInFunction('pop', 0, 0, lambda args: obj.pop())
            if node.member == 'insert':
                return BuiltInFunction('insert', 2, 2, lambda args: obj.insert(args[0], args[1]))
            if node.member == 'remove':
                return BuiltInFunction('remove', 1, 1, lambda args: obj.remove(args[0]))
            if node.member == 'sort':
                return BuiltInFunction('sort', 0, 0, lambda args: obj.sort())
            if node.member == 'reverse':
                return BuiltInFunction('reverse', 0, 0, lambda args: obj.reverse())
            if node.member == 'contains':
                return BuiltInFunction('contains', 1, 1, lambda args: args[0] in obj)
        if isinstance(obj, dict):
            if node.member == 'keys':
                return BuiltInFunction('keys', 0, 0, lambda args: list(obj.keys()))
            if node.member == 'values':
                return BuiltInFunction('values', 0, 0, lambda args: list(obj.values()))
            if node.member == 'contains':
                return BuiltInFunction('contains', 1, 1, lambda args: args[0] in obj)

        # Try to get attribute from the object
        if hasattr(obj, node.member):
            attr = getattr(obj, node.member)
            if callable(attr):
                return BuiltInFunction(node.member, 0, None, lambda args, f=attr: f(*args))
            return attr

        raise RuntimeError_(f"'{type(obj).__name__}' has no member '{node.member}'")

    def _visit_Subscript(self, node: Subscript):
        """Evaluate subscript/index access."""
        obj = self._visit(node.object)
        index = self._visit(node.index)

        if isinstance(obj, list):
            if not isinstance(index, int):
                raise RuntimeError_(f"Array index must be int, got {type(index).__name__}")
            if index < 0 or index >= len(obj):
                raise RuntimeError_(f"Index {index} out of bounds for array of length {len(obj)}")
            return obj[index]
        if isinstance(obj, dict):
            if index not in obj:
                raise RuntimeError_(f"Key '{index}' not found in map")
            return obj[index]
        if isinstance(obj, str):
            if not isinstance(index, int):
                raise RuntimeError_(f"String index must be int, got {type(index).__name__}")
            if index < 0 or index >= len(obj):
                raise RuntimeError_(f"Index {index} out of bounds for string of length {len(obj)}")
            return obj[index]

        raise RuntimeError_(f"Cannot subscript {type(obj).__name__}")

    def _visit_FunctionCall(self, node: FunctionCall):
        """Evaluate a function call."""
        callee = self._visit(node.callee)

        # Evaluate arguments
        args = [self._visit(arg) for arg in node.arguments]

        if isinstance(callee, SamratFunction):
            return callee.call(self, args)
        if isinstance(callee, BuiltInFunction):
            return callee.call(args)
        if isinstance(callee, SamratClass):
            return callee.instantiate(self, args)
        if isinstance(callee, BoundMethod):
            return callee.call(self, args)
        if callable(callee):
            return callee(*args)

        raise RuntimeError_(f"'{type(callee).__name__}' is not callable")

    def _visit_ArrayLiteral(self, node: ArrayLiteral):
        """Evaluate an array literal."""
        return [self._visit(elem) for elem in node.elements]

    def _visit_MapLiteral(self, node: MapLiteral):
        """Evaluate a map literal."""
        result = {}
        for key, value in node.entries:
            k = self._visit(key)
            v = self._visit(value)
            result[k] = v
        return result

    def _visit_ThisExpression(self, node: ThisExpression):
        """Evaluate 'this' expression."""
        if hasattr(self, '_current_instance') and self._current_instance:
            return self._current_instance
        raise RuntimeError_("'this' used outside of class context")

    def _visit_RangeLiteral(self, node: RangeLiteral):
        """Evaluate a range literal (should be handled by BinaryOp with '..')."""
        start = self._visit(node.start)
        end = self._visit(node.end)
        return range(start, end)

    # ─── Helper Methods ───────────────────────────────────────────────────

    def _is_truthy(self, value) -> bool:
        """Determine the truthiness of a value."""
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


# ─── Runtime Objects ──────────────────────────────────────────────────────

class SamratFunction:
    """Represents a user-defined Samrat function."""

    def __init__(self, name: str, parameters: list, body, closure: Environment):
        self.name = name
        self.parameters = parameters
        self.body = body
        self.closure = closure

    def call(self, interpreter: Interpreter, args: list):
        """Call the function with the given arguments."""
        # Create a new environment with the closure as parent
        env = Environment(self.closure)

        # Bind parameters to arguments
        for i, param in enumerate(self.parameters):
            if i < len(args):
                env.define(param.name, args[i])
            elif param.default_value is not None:
                env.define(param.name, interpreter._visit(param.default_value))
            else:
                env.define(param.name, None)

        # Execute the function body
        previous = interpreter.environment
        interpreter.environment = env

        try:
            result = interpreter._visit(self.body)
            return result
        except ReturnValue as ret:
            return ret.value
        finally:
            interpreter.environment = previous

    def __repr__(self):
        return f'<function {self.name}>'


class BuiltInFunction:
    """Represents a built-in Samrat function."""

    def __init__(self, name: str, min_args: int, max_args, impl):
        self.name = name
        self.min_args = min_args
        self.max_args = max_args  # None means unlimited
        self.impl = impl

    def call(self, args: list):
        """Call the built-in function with the given arguments."""
        if len(args) < self.min_args:
            raise RuntimeError_(f"Function '{self.name}' expects at least {self.min_args} argument(s), got {len(args)}")
        if self.max_args is not None and len(args) > self.max_args:
            raise RuntimeError_(f"Function '{self.name}' expects at most {self.max_args} argument(s), got {len(args)}")
        return self.impl(args)

    def __repr__(self):
        return f'<built-in function {self.name}>'


class SamratClass:
    """Represents a user-defined Samrat class."""

    def __init__(self, name: str, fields: list, constructor, methods: list):
        self.name = name
        self.fields = fields
        self.constructor = constructor
        self.methods = methods

    def instantiate(self, interpreter: Interpreter, args: list):
        """Create a new instance of this class."""
        instance = SamratObject(self.name, self.fields, self.methods)

        # Call constructor if present
        if self.constructor:
            previous_instance = getattr(interpreter, '_current_instance', None)
            interpreter._current_instance = instance

            # Create environment for constructor
            env = Environment(interpreter.environment)
            env.define('this', instance)

            for i, param in enumerate(self.constructor.parameters):
                if i < len(args):
                    env.define(param.name, args[i])
                elif param.default_value is not None:
                    env.define(param.name, interpreter._visit(param.default_value))
                else:
                    env.define(param.name, None)

            previous = interpreter.environment
            interpreter.environment = env

            try:
                interpreter._visit(self.constructor.body)
            except ReturnValue:
                pass
            finally:
                interpreter.environment = previous
                interpreter._current_instance = previous_instance

        return instance

    def __repr__(self):
        return f'<class {self.name}>'


class SamratObject:
    """Represents an instance of a Samrat class."""

    def __init__(self, class_name: str, fields: list, methods: list):
        self.class_name = class_name
        self.fields = {}
        self.methods = {}

        # Initialize fields with defaults
        for field in fields:
            if field.var_type == 'int':
                self.fields[field.name] = 0
            elif field.var_type == 'float':
                self.fields[field.name] = 0.0
            elif field.var_type == 'str':
                self.fields[field.name] = ''
            elif field.var_type == 'bool':
                self.fields[field.name] = False
            elif field.var_type and field.var_type.startswith('['):
                self.fields[field.name] = []
            elif field.var_type and field.var_type.startswith('{'):
                self.fields[field.name] = {}
            else:
                self.fields[field.name] = None

        # Store methods
        for method in methods:
            self.methods[method.name] = method

    def get_field(self, name: str):
        """Get a field value or method."""
        if name in self.fields:
            return self.fields[name]
        if name in self.methods:
            method = self.methods[name]
            # Create a bound method
            return BoundMethod(self, method)
        raise RuntimeError_(f"'{self.class_name}' has no attribute '{name}'")

    def set_field(self, name: str, value):
        """Set a field value."""
        if name in self.fields:
            self.fields[name] = value
        else:
            raise RuntimeError_(f"'{self.class_name}' has no field '{name}'")

    def __repr__(self):
        return f'<{self.class_name} instance>'


class BoundMethod:
    """Represents a method bound to an instance."""

    def __init__(self, instance: SamratObject, method: FunctionDef):
        self.instance = instance
        self.method = method

    def call(self, interpreter: Interpreter, args: list):
        """Call the bound method."""
        previous_instance = getattr(interpreter, '_current_instance', None)
        interpreter._current_instance = self.instance

        env = Environment(interpreter.environment)
        env.define('this', self.instance)

        for i, param in enumerate(self.method.parameters):
            if i < len(args):
                env.define(param.name, args[i])
            elif param.default_value is not None:
                env.define(param.name, interpreter._visit(param.default_value))
            else:
                env.define(param.name, None)

        previous = interpreter.environment
        interpreter.environment = env

        try:
            result = interpreter._visit(self.method.body)
            return result
        except ReturnValue as ret:
            return ret.value
        finally:
            interpreter.environment = previous
            interpreter._current_instance = previous_instance

    def __repr__(self):
        return f'<bound method {self.method.name}>'


class StringModule:
    """The 'string' standard library module."""

    @staticmethod
    def upper(s: str) -> str:
        return s.upper()

    @staticmethod
    def lower(s: str) -> str:
        return s.lower()

    @staticmethod
    def trim(s: str) -> str:
        return s.strip()

    @staticmethod
    def split(s: str, sep: str = ' ') -> list:
        return s.split(sep)

    @staticmethod
    def join(items: list, sep: str = '') -> str:
        return sep.join(str(item) for item in items)

    @staticmethod
    def replace(s: str, old: str, new: str) -> str:
        return s.replace(old, new)
