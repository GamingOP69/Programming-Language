"""
Samrat Programming Language — Semantic Analyzer

The semantic analyzer is the third phase of the Samrat compiler pipeline.
It walks the AST produced by the parser and validates semantic correctness
before the interpreter executes the code.

This analyzer:
- Resolves all identifiers to their declarations
- Validates type compatibility (strong typing)
- Enforces mutability rules (cannot reassign constants)
- Detects undefined variables, functions, and classes
- Validates function call arguments (count and types)
- Manages scopes (enter/leave blocks, functions, classes)
- Detects duplicate declarations in the same scope
- Validates return statements in functions
- Validates break/continue within loops
- Produces descriptive error messages with location info

Usage:
    from lexer import Lexer
    from parser import Parser
    from semantic import SemanticAnalyzer
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
"""

from ast_nodes import *
from symbol_table import SymbolTable, Symbol
from errors import SemanticError


# Type compatibility matrix
# (type_a, type_b) -> True if compatible for assignment/operation
TYPE_COMPATIBILITY = {
    ('int', 'int'): True,
    ('float', 'float'): True,
    ('float', 'int'): True,   # int can be assigned to float
    ('int', 'float'): True,   # int can be compared with float
    ('str', 'str'): True,
    ('bool', 'bool'): True,
    ('null', 'null'): True,
    ('null', 'int'): False,
    ('null', 'float'): False,
    ('null', 'str'): False,
    ('null', 'bool'): False,
}

# Types that support specific operators
ARITHMETIC_TYPES = {'int', 'float'}
COMPARISON_TYPES = {'int', 'float', 'str', 'bool'}
LOGICAL_TYPES = {'bool'}
BITWISE_TYPES = {'int'}
INDEXABLE_TYPES = {'str'}
SUBSCRIBABLE_TYPES = {'str'}


def type_name_from_value(value) -> str:
    """Infer the Samrat type name from a Python value."""
    if value is None:
        return 'null'
    elif isinstance(value, bool):
        return 'bool'
    elif isinstance(value, int):
        return 'int'
    elif isinstance(value, float):
        return 'float'
    elif isinstance(value, str):
        return 'str'
    elif isinstance(value, list):
        if value:
            # All elements must be same type
            elem_type = type_name_from_value(value[0])
            return f'[{elem_type}]'
        return '[]'
    elif isinstance(value, dict):
        return '{:}'
    else:
        return 'object'


def types_are_compatible(type_a: str, type_b: str) -> bool:
    """Check if two types are compatible for assignment or operation."""
    if type_a is None or type_b is None:
        return True  # Unknown types are compatible
    # Check direct compatibility
    key = (type_a, type_b)
    if key in TYPE_COMPATIBILITY:
        return TYPE_COMPATIBILITY[key]
    # Check array types
    if type_a.startswith('[') and type_b.startswith('['):
        inner_a = type_a[1:-1]
        inner_b = type_b[1:-1]
        return types_are_compatible(inner_a, inner_b)
    # Check map types
    if type_a.startswith('{') and type_b.startswith('{'):
        return True  # Map type compatibility is structural
    return False


class SemanticAnalyzer:
    """
    Walks the AST and performs semantic validation.

    Attributes:
        symbol_table: The symbol table tracking all scopes and declarations.
        current_function: The name of the function currently being analyzed (None if at top level).
        current_return_type: The expected return type of the current function.
        loop_depth: The current nesting depth of loops (for break/continue validation).
        errors: List of semantic errors found during analysis.
    """

    def __init__(self):
        self.symbol_table = SymbolTable()
        self.current_function = None
        self.current_return_type = None
        self.current_class = None
        self.loop_depth = 0
        self.errors = []
        self._builtin_types = {'int', 'float', 'str', 'bool', 'void', 'null'}

    def analyze(self, node) -> bool:
        """
        Analyze a node and all its children for semantic correctness.

        Args:
            node: The AST node to analyze (typically a Program).

        Returns:
            True if the program is semantically valid, False otherwise.
        """
        self.errors = []
        self._visit(node)
        return len(self.errors) == 0

    def get_errors(self) -> list:
        """Return the list of semantic errors found."""
        return self.errors

    def _error(self, message: str, line: int, column: int):
        """Record a semantic error."""
        self.errors.append(SemanticError(message, line, column))

    # ─── Visitor Dispatch ────────────────────────────────────────────────

    def _visit(self, node):
        """Dispatch to the appropriate visitor method based on node type."""
        node_type = type(node).__name__
        visitor = getattr(self, f'_visit_{node_type}', self._visit_default)
        return visitor(node)

    def _visit_default(self, node):
        """Default visitor for unhandled node types."""
        pass  # Skip unknown nodes gracefully

    # ─── Program ──────────────────────────────────────────────────────────

    def _visit_Program(self, node: Program):
        """Visit program: analyze all top-level statements."""
        # Register built-in functions in global scope
        self._register_builtins()

        # Visit all statements
        for stmt in node.statements:
            self._visit(stmt)

    def _register_builtins(self):
        """Register built-in functions in the global scope."""
        builtins = [
            ('print', 'void'), ('input', 'str'),
            ('int', 'int'), ('float', 'float'), ('str', 'str'), ('bool', 'bool'),
            ('type', 'str'), ('len', 'int'),
        ]
        for name, return_type in builtins:
            self.symbol_table.declare(name, 'function', return_type,
                                      is_mutable=False, line=0, column=0)

    # ─── Statements ───────────────────────────────────────────────────────

    def _visit_VarDeclaration(self, node: VarDeclaration):
        """Analyze variable declaration."""
        # Check for duplicate in current scope
        if self.symbol_table.lookup_local(node.name) is not None:
            self._error(f"Variable '{node.name}' is already declared in this scope",
                        node.line, node.column)
            return

        # Analyze initializer if present
        inferred_type = None
        if node.initializer is not None:
            inferred_type = self._resolve_expression_type(node.initializer)

        # Determine the declared type
        declared_type = node.var_type

        # Validate type compatibility if both types are known
        if declared_type and inferred_type:
            if not types_are_compatible(declared_type, inferred_type):
                self._error(
                    f"Type mismatch: cannot assign {inferred_type} to variable "
                    f"'{node.name}' of type {declared_type}",
                    node.line, node.column
                )

        # Use declared type, then inferred type, then None
        final_type = declared_type or inferred_type

        # Declare the symbol
        self.symbol_table.declare(node.name, 'variable', final_type,
                                  is_mutable=True, line=node.line, column=node.column)

    def _visit_ConstDeclaration(self, node: ConstDeclaration):
        """Analyze constant declaration."""
        if self.symbol_table.lookup_local(node.name) is not None:
            self._error(f"Constant '{node.name}' is already declared in this scope",
                        node.line, node.column)
            return

        inferred_type = self._resolve_expression_type(node.initializer)
        declared_type = node.const_type

        if declared_type and inferred_type:
            if not types_are_compatible(declared_type, inferred_type):
                self._error(
                    f"Type mismatch: cannot assign {inferred_type} to constant "
                    f"'{node.name}' of type {declared_type}",
                    node.line, node.column
                )

        final_type = declared_type or inferred_type
        self.symbol_table.declare(node.name, 'constant', final_type,
                                  is_mutable=False, line=node.line, column=node.column)

    def _visit_Assignment(self, node: Assignment):
        """Analyze assignment statement."""
        # Resolve the target
        if isinstance(node.target, Identifier):
            symbol = self.symbol_table.lookup(node.target.name)
            if symbol is None:
                self._error(f"Undefined variable '{node.target.name}'",
                            node.line, node.column)
                return
            if not symbol.is_mutable:
                self._error(f"Cannot assign to constant '{node.target.name}'",
                            node.line, node.column)
                return

            # Validate type compatibility
            value_type = self._resolve_expression_type(node.value)
            if symbol.symbol_type and value_type:
                if not types_are_compatible(symbol.symbol_type, value_type):
                    self._error(
                        f"Type mismatch: cannot assign {value_type} to '{node.target.name}' "
                        f"of type {symbol.symbol_type}",
                        node.line, node.column
                    )
        elif isinstance(node.target, MemberAccess):
            # Allow assignment to fields (valid if within constructor)
            self._resolve_expression_type(node.target)
        elif isinstance(node.target, Subscript):
            # Allow array/map element assignment
            self._resolve_expression_type(node.target)
        else:
            self._error(f"Invalid assignment target",
                        node.line, node.column)

        self._resolve_expression_type(node.value)

    def _visit_ExpressionStatement(self, node: ExpressionStatement):
        """Analyze expression statement."""
        self._resolve_expression_type(node.expression)

    def _visit_Block(self, node: Block):
        """Analyze a block statement."""
        self.symbol_table.enter_scope('block')
        for stmt in node.statements:
            self._visit(stmt)
        self.symbol_table.leave_scope()

    def _visit_ReturnStatement(self, node: ReturnStatement):
        """Analyze return statement."""
        if self.current_function is None:
            self._error("'return' outside function", node.line, node.column)
            return

        if node.value is None:
            # Bare return: must match void/None return type
            if self.current_return_type and self.current_return_type != 'void':
                self._error(
                    f"Function '{self.current_function}' expects return type "
                    f"'{self.current_return_type}', but 'return' has no value",
                    node.line, node.column
                )
            return

        # Return with value
        value_type = self._resolve_expression_type(node.value)
        if self.current_return_type and value_type:
            if not types_are_compatible(self.current_return_type, value_type):
                self._error(
                    f"Type mismatch: function '{self.current_function}' expects "
                    f"return type '{self.current_return_type}', got '{value_type}'",
                    node.line, node.column
                )

    def _visit_BreakStatement(self, node: BreakStatement):
        """Analyze break statement."""
        if self.loop_depth == 0:
            self._error("'break' outside loop", node.line, node.column)

    def _visit_ContinueStatement(self, node: ContinueStatement):
        """Analyze continue statement."""
        if self.loop_depth == 0:
            self._error("'continue' outside loop", node.line, node.column)

    def _visit_FunctionDef(self, node: FunctionDef):
        """Analyze function definition."""
        # Check for duplicate
        existing = self.symbol_table.lookup_local(node.name)
        if existing is not None:
            self._error(f"Function '{node.name}' is already defined",
                        node.line, node.column)
            return

        # Register the function
        self.symbol_table.declare(node.name, 'function', node.return_type,
                                  is_mutable=False, line=node.line, column=node.column)

        # Analyze the function body
        previous_function = self.current_function
        previous_return_type = self.current_return_type
        self.current_function = node.name
        self.current_return_type = node.return_type

        self.symbol_table.enter_scope('function')

        # Declare parameters
        for param in node.parameters:
            self.symbol_table.declare(param.name, 'parameter', param.param_type,
                                      is_mutable=True, line=param.line, column=param.column)

        # Visit body
        self._visit(node.body)

        self.symbol_table.leave_scope()
        self.current_function = previous_function
        self.current_return_type = previous_return_type

    def _visit_ClassDef(self, node: ClassDef):
        """Analyze class definition."""
        if self.symbol_table.lookup_local(node.name) is not None:
            self._error(f"Class '{node.name}' is already defined",
                        node.line, node.column)
            return

        self.symbol_table.declare(node.name, 'class', node.name,
                                  is_mutable=False, line=node.line, column=node.column)

        previous_class = self.current_class
        self.current_class = node.name

        self.symbol_table.enter_scope('class')

        # Declare fields
        for field in node.fields:
            if self.symbol_table.lookup_local(field.name) is not None:
                self._error(f"Field '{field.name}' is already declared in class '{node.name}'",
                            field.line, field.column)
                continue
            self.symbol_table.declare(field.name, 'variable', field.var_type,
                                      is_mutable=True, line=field.line, column=field.column)

        # Analyze constructor
        if node.constructor:
            self._visit(node.constructor)

        # Analyze methods
        for method in node.methods:
            self._visit(method)

        self.symbol_table.leave_scope()
        self.current_class = previous_class

    def _visit_ConstructorDef(self, node: ConstructorDef):
        """Analyze constructor definition."""
        self.symbol_table.enter_scope('function')

        for param in node.parameters:
            self.symbol_table.declare(param.name, 'parameter', param.param_type,
                                      is_mutable=True, line=param.line, column=param.column)

        self._visit(node.body)
        self.symbol_table.leave_scope()

    def _visit_IfStatement(self, node: IfStatement):
        """Analyze if/elif/else statement."""
        cond_type = self._resolve_expression_type(node.condition)
        if cond_type and cond_type != 'bool':
            self._error(f"If condition must be bool, got {cond_type}",
                        node.condition.line, node.condition.column)

        self._visit(node.then_block)

        for i in range(len(node.elif_conditions)):
            elif_cond_type = self._resolve_expression_type(node.elif_conditions[i])
            if elif_cond_type and elif_cond_type != 'bool':
                self._error(f"Elif condition must be bool, got {elif_cond_type}",
                            node.elif_conditions[i].line, node.elif_conditions[i].column)
            self._visit(node.elif_blocks[i])

        if node.else_block:
            self._visit(node.else_block)

    def _visit_WhileLoop(self, node: WhileLoop):
        """Analyze while loop."""
        cond_type = self._resolve_expression_type(node.condition)
        if cond_type and cond_type != 'bool':
            self._error(f"While condition must be bool, got {cond_type}",
                        node.condition.line, node.condition.column)

        self.loop_depth += 1
        self._visit(node.body)
        self.loop_depth -= 1

    def _visit_ForLoop(self, node: ForLoop):
        """Analyze for loop."""
        iter_type = self._resolve_expression_type(node.iterable)

        self.loop_depth += 1
        self.symbol_table.enter_scope('block')
        # Declare loop variable
        self.symbol_table.declare(node.variable, 'variable', 'int',
                                  is_mutable=False, line=node.line, column=node.column)
        self._visit(node.body)
        self.symbol_table.leave_scope()
        self.loop_depth -= 1

    def _visit_TryStatement(self, node: TryStatement):
        """Analyze try/catch."""
        self._visit(node.try_block)
        self.symbol_table.enter_scope('block')
        self.symbol_table.declare(node.catch_var, 'variable', 'str',
                                  is_mutable=True, line=node.line, column=node.column)
        self._visit(node.catch_block)
        self.symbol_table.leave_scope()

    def _visit_ThrowStatement(self, node: ThrowStatement):
        """Analyze throw statement."""
        self._resolve_expression_type(node.value)

    def _visit_ImportStatement(self, node: ImportStatement):
        """Analyze import statement."""
        for name in node.names:
            if node.module:
                # Items from module: register under module namespace
                self.symbol_table.declare(name, 'function', None,
                                          is_mutable=False, line=node.line, column=node.column)
            else:
                # Module itself
                self.symbol_table.declare(name, 'module', None,
                                          is_mutable=False, line=node.line, column=node.column)

    # ─── Expression Type Resolution ───────────────────────────────────────

    def _resolve_expression_type(self, node):
        """
        Resolve the type of an expression, visiting children as needed.

        Returns the type string (e.g., 'int', 'str', 'bool') or None if unknown.
        """
        node_type = type(node).__name__
        resolver = getattr(self, f'_resolve_{node_type}', self._resolve_default)
        return resolver(node)

    def _resolve_default(self, node):
        """Default type resolver."""
        return None

    def _resolve_Literal(self, node: Literal) -> str:
        """Resolve literal type."""
        return type_name_from_value(node.value)

    def _resolve_Identifier(self, node: Identifier) -> str:
        """Resolve identifier type by looking up in symbol table."""
        symbol = self.symbol_table.lookup(node.name)
        if symbol is None:
            # Check for built-in names
            if node.name in {'true', 'false', 'null'}:
                return 'bool' if node.name in {'true', 'false'} else 'null'
            self._error(f"Undefined variable '{node.name}'",
                        node.line, node.column)
            return None
        return symbol.symbol_type

    def _resolve_BinaryOp(self, node: BinaryOp) -> str:
        """Resolve binary operation result type."""
        left_type = self._resolve_expression_type(node.left)
        right_type = self._resolve_expression_type(node.right)

        if left_type is None or right_type is None:
            return None

        op = node.operator

        # Range operator
        if op == '..':
            return 'range'

        # Arithmetic operators
        if op in ('+', '-', '*', '/', '%', '**'):
            if op == '+' and left_type == 'str' and right_type == 'str':
                return 'str'  # String concatenation
            if left_type in ARITHMETIC_TYPES and right_type in ARITHMETIC_TYPES:
                if op == '%':
                    if left_type == 'int' and right_type == 'int':
                        return 'int'
                    self._error("Modulo requires integer operands", node.line, node.column)
                    return None
                if '/' in op:
                    return 'float'
                if '**' in op:
                    return 'float' if left_type == 'float' or right_type == 'float' else 'int'
                return left_type if left_type == right_type else 'float'

        # Comparison operators
        if op in ('==', '!=', '<', '>', '<=', '>='):
            if left_type in COMPARISON_TYPES and right_type in COMPARISON_TYPES:
                # Different types for == and != are allowed (return false)
                if op in ('==', '!='):
                    return 'bool'
                # Ordering requires same type
                if left_type == right_type:
                    return 'bool'
                self._error(f"Cannot compare {left_type} and {right_type} with '{op}'",
                            node.line, node.column)
                return None
            self._error(f"Cannot compare {left_type} and {right_type} with '{op}'",
                        node.line, node.column)
            return None

        # Logical operators
        if op in ('and', 'or'):
            if left_type == 'bool' and right_type == 'bool':
                return 'bool'
            self._error(f"Logical '{op}' requires bool operands, got {left_type} and {right_type}",
                        node.line, node.column)
            return None

        # Bitwise operators
        if op in ('&', '|', '^', '<<', '>>'):
            if left_type == 'int' and right_type == 'int':
                return 'int'
            self._error(f"Bitwise '{op}' requires integer operands",
                        node.line, node.column)
            return None

        return None

    def _resolve_UnaryOp(self, node: UnaryOp) -> str:
        """Resolve unary operation result type."""
        operand_type = self._resolve_expression_type(node.operand)

        if node.operator == '-':
            if operand_type in ('int', 'float'):
                return operand_type
            self._error(f"Cannot negate {operand_type}", node.line, node.column)
            return None
        elif node.operator == 'not':
            if operand_type == 'bool':
                return 'bool'
            self._error(f"'not' requires bool operand, got {operand_type}",
                        node.line, node.column)
            return None
        elif node.operator == '~':
            if operand_type == 'int':
                return 'int'
            self._error(f"'~' requires integer operand, got {operand_type}",
                        node.line, node.column)
            return None

        return None

    def _resolve_MemberAccess(self, node: MemberAccess) -> str:
        """Resolve member access type."""
        obj_type = self._resolve_expression_type(node.object)

        if isinstance(node.object, ThisExpression):
            # Accessing fields/methods of current class
            if self.current_class:
                return None  # Type resolved at runtime
            self._error("'this' can only be used inside a class", node.line, node.column)
            return None

        # For method calls on arrays and maps, we know the return types
        if obj_type and obj_type.startswith('['):
            if node.member in ('append', 'pop', 'insert', 'remove', 'sort', 'reverse', 'contains'):
                return 'void' if node.member in ('append', 'insert', 'sort', 'reverse') else \
                       'int' if node.member == 'pop' else \
                       node.member  # Will be resolved when called
            return None

        if obj_type and obj_type.startswith('{'):
            if node.member in ('keys', 'values', 'contains'):
                return '[str]' if node.member in ('keys', 'values') else 'bool'

        return None

    def _resolve_Subscript(self, node: Subscript) -> str:
        """Resolve subscript expression type."""
        obj_type = self._resolve_expression_type(node.object)
        index_type = self._resolve_expression_type(node.index)

        if obj_type and obj_type.startswith('['):
            # Array element access
            inner_type = obj_type[1:-1]
            return inner_type

        if obj_type and obj_type.startswith('{'):
            # Map value access
            return 'str'  # Simplified for 1.0

        if obj_type == 'str':
            if index_type == 'int':
                return 'str'  # String indexing returns a string

        return None

    def _resolve_FunctionCall(self, node: FunctionCall) -> str:
        """Resolve function call expression type."""
        callee_type = self._resolve_expression_type(node.callee)

        # Visit arguments
        for arg in node.arguments:
            self._resolve_expression_type(arg)

        # Check argument counts for known functions
        if isinstance(node.callee, Identifier):
            name = node.callee.name
            builtin_arg_counts = {
                'print': (0, None),  # 0 or more
                'input': (0, 1),
                'int': (1, 1),
                'float': (1, 1),
                'str': (1, 1),
                'bool': (1, 1),
                'type': (1, 1),
                'len': (1, 1),
            }
            if name in builtin_arg_counts:
                min_args, max_args = builtin_arg_counts[name]
                if len(node.arguments) < min_args:
                    self._error(f"Function '{name}' expects at least {min_args} argument(s), "
                                f"got {len(node.arguments)}", node.line, node.column)
                elif max_args is not None and len(node.arguments) > max_args:
                    self._error(f"Function '{name}' expects at most {max_args} argument(s), "
                                f"got {len(node.arguments)}", node.line, node.column)

        # Return type is determined by the callee
        if callee_type and callee_type != 'void':
            return callee_type

        return None

    def _resolve_ArrayLiteral(self, node: ArrayLiteral) -> str:
        """Resolve array literal type."""
        if not node.elements:
            return '[]'  # Empty array, type unknown

        # All elements should have the same type
        element_types = []
        for elem in node.elements:
            elem_type = self._resolve_expression_type(elem)
            if elem_type:
                element_types.append(elem_type)

        if element_types:
            # Use the first non-None type
            return f'[{element_types[0]}]'
        return '[]'

    def _resolve_MapLiteral(self, node: MapLiteral) -> str:
        """Resolve map literal type."""
        for key, value in node.entries:
            self._resolve_expression_type(key)
            self._resolve_expression_type(value)
        return '{:}'

    def _resolve_ThisExpression(self, node: ThisExpression) -> str:
        """Resolve 'this' expression."""
        if self.current_class:
            return self.current_class
        self._error("'this' can only be used inside a class", node.line, node.column)
        return None

    def _resolve_RangeLiteral(self, node: RangeLiteral) -> str:
        """Resolve range literal type."""
        self._resolve_expression_type(node.start)
        self._resolve_expression_type(node.end)
        return 'range'