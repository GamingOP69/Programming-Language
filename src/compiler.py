"""
Samrat Programming Language — Bytecode Compiler

Compiles Samrat AST into bytecode chunks for execution by the VM.
Each function gets its own chunk. Local variables are accessed by
stack slot index. Constants are stored in a pool.

Usage:
    from compiler import Compiler
    compiler = Compiler()
    chunk = compiler.compile(ast)
"""

from bytecode import OpCode, Chunk
from ast_nodes import (
    Program, ExpressionStatement, Block, VarDeclaration, ConstDeclaration,
    Assignment, Identifier, Subscript, MemberAccess, ReturnStatement,
    BreakStatement, ContinueStatement, IfStatement, WhileLoop, ForLoop,
    FunctionDef, ClassDef, TryStatement, ThrowStatement, ImportStatement,
    Literal, ThisExpression, RangeLiteral, BinaryOp, UnaryOp, FunctionCall,
    ArrayLiteral, MapLiteral,
)


class Compiler:
    """
    Compiles AST nodes into bytecode chunks.

    Attributes:
        chunk: The current chunk being compiled.
        locals: List of local variable names for the current function.
        globals: Set of global variable names.
        loop_stack: Stack of loop start/end/continue offsets for break/continue.
        function_chunks: List of (name, chunk) for all compiled functions.
    """

    def __init__(self):
        self.chunk = Chunk("<script>")
        self.locals = []          # List of local variable names
        self.globals = set()      # Set of global variable names
        self.loop_stack = []      # Stack of (start_ip, end_ip, continue_ip)
        self.function_chunks = []  # List of (name, chunk, param_count)
        self.current_line = 0
        self._class_info = None   # Current class being compiled

    def compile(self, node) -> Chunk:
        """Compile an AST node into the current chunk."""
        self._visit(node)
        self.chunk.emit(OpCode.HALT, line=self.current_line)
        return self.chunk

    def _visit(self, node):
        """Dispatch to the appropriate compiler method."""
        node_type = type(node).__name__
        visitor = getattr(self, f'_visit_{node_type}', self._visit_default)
        return visitor(node)

    def _visit_default(self, node):
        pass

    def _line(self, node):
        """Track line number from node."""
        if hasattr(node, 'line') and node.line:
            self.current_line = node.line

    # ─── Program ──────────────────────────────────────────────────────────

    def _visit_Program(self, node: Program):
        for i, stmt in enumerate(node.statements):
            is_last = (i == len(node.statements) - 1)
            self._last_stmt = is_last
            self._visit(stmt)
        self._last_stmt = False

    # ─── Statements ───────────────────────────────────────────────────────

    def _visit_ExpressionStatement(self, node: ExpressionStatement):
        self._visit(node.expression)
        if not getattr(self, '_last_stmt', False):
            self.chunk.emit(OpCode.POP, line=self.current_line)

    def _visit_Block(self, node: Block):
        saved_locals = len(self.locals)
        for stmt in node.statements:
            self._visit(stmt)
        # Restore locals (pop any declared in this block)
        while len(self.locals) > saved_locals:
            self.locals.pop()

    def _visit_VarDeclaration(self, node: VarDeclaration):
        self._line(node)
        if node.initializer:
            self._visit(node.initializer)
        else:
            # Default values
            if node.var_type == 'int':
                self.chunk.emit(OpCode.PUSH_INT, self.chunk.add_constant(0), self.current_line)
            elif node.var_type == 'float':
                self.chunk.emit(OpCode.PUSH_FLOAT, self.chunk.add_constant(0.0), self.current_line)
            elif node.var_type == 'str':
                self.chunk.emit(OpCode.PUSH_STRING, self.chunk.add_constant(""), self.current_line)
            elif node.var_type == 'bool':
                self.chunk.emit(OpCode.PUSH_FALSE, line=self.current_line)
            else:
                self.chunk.emit(OpCode.PUSH_NULL, line=self.current_line)
        # Store in local or global
        if self._is_global_scope():
            if getattr(self, '_last_stmt', False):
                self.chunk.emit(OpCode.DUP, line=self.current_line)
            idx = self.chunk.add_constant(node.name)
            self.chunk.emit(OpCode.STORE_GLOBAL, idx, self.current_line)
            self.globals.add(node.name)
        else:
            self.locals.append(node.name)
            slot = len(self.locals) - 1
            self.chunk.emit(OpCode.STORE, slot, self.current_line)

    def _visit_ConstDeclaration(self, node: ConstDeclaration):
        self._line(node)
        self._visit(node.initializer)
        if self._is_global_scope():
            idx = self.chunk.add_constant(node.name)
            self.chunk.emit(OpCode.STORE_GLOBAL, idx, self.current_line)
            self.globals.add(node.name)
        else:
            self.locals.append(node.name)
            slot = len(self.locals) - 1
            self.chunk.emit(OpCode.STORE, slot, self.current_line)

    def _visit_Assignment(self, node: Assignment):
        self._line(node)
        if isinstance(node.target, Identifier):
            name = node.target.name
            self._visit(node.value)
            if getattr(self, '_last_stmt', False):
                self.chunk.emit(OpCode.DUP, line=self.current_line)
            if name in self.globals or (self._is_global_scope() and name not in self.locals):
                idx = self.chunk.add_constant(name)
                self.chunk.emit(OpCode.STORE_GLOBAL, idx, self.current_line)
            else:
                try:
                    slot = self.locals.index(name)
                    self.chunk.emit(OpCode.STORE, slot, self.current_line)
                except ValueError:
                    idx = self.chunk.add_constant(name)
                    self.chunk.emit(OpCode.STORE_GLOBAL, idx, self.current_line)
        elif isinstance(node.target, Subscript):
            self._visit(node.target.object)
            self._visit(node.target.index)
            self._visit(node.value)
            self.chunk.emit(OpCode.SET_ITEM, line=self.current_line)
        elif isinstance(node.target, MemberAccess):
            self._visit(node.target.object)
            self._visit(node.value)
            idx = self.chunk.add_constant(node.target.member)
            self.chunk.emit(OpCode.SET_ATTR, idx, self.current_line)

    def _visit_ReturnStatement(self, node: ReturnStatement):
        self._line(node)
        if node.value:
            self._visit(node.value)
        else:
            self.chunk.emit(OpCode.PUSH_NULL, line=self.current_line)
        self.chunk.emit(OpCode.RETURN, line=self.current_line)

    def _visit_BreakStatement(self, node: BreakStatement):
        self._line(node)
        if self.loop_stack:
            self.chunk.emit(OpCode.JMP, self.loop_stack[-1][1], self.current_line)

    def _visit_ContinueStatement(self, node: ContinueStatement):
        self._line(node)
        if self.loop_stack:
            self.chunk.emit(OpCode.JMP, self.loop_stack[-1][2], self.current_line)

    def _visit_IfStatement(self, node: IfStatement):
        self._line(node)
        # Condition
        self._visit(node.condition)
        self.chunk.emit(OpCode.JMP_IF_FALSE, 0, self.current_line)  # placeholder
        false_jump = len(self.chunk.code) - 1

        # Then block
        self._visit(node.then_block)

        # Elif blocks
        elif_end_jumps = []
        for i in range(len(node.elif_conditions)):
            # Jump over elif if then was taken
            self.chunk.emit(OpCode.JMP, 0, self.current_line)
            elif_end_jumps.append(len(self.chunk.code) - 1)

            # Patch previous false jump to here
            self.chunk.code[false_jump] = (OpCode.JMP_IF_FALSE, len(self.chunk.code))

            # Elif condition
            self._visit(node.elif_conditions[i])
            self.chunk.emit(OpCode.JMP_IF_FALSE, 0, self.current_line)
            false_jump = len(self.chunk.code) - 1

            # Elif block
            self._visit(node.elif_blocks[i])

        # Else block
        if node.else_block:
            self.chunk.emit(OpCode.JMP, 0, self.current_line)
            else_end = len(self.chunk.code) - 1
            self.chunk.code[false_jump] = (OpCode.JMP_IF_FALSE, len(self.chunk.code))
            self._visit(node.else_block)
            self.chunk.code[else_end] = (OpCode.JMP, len(self.chunk.code))
        else:
            self.chunk.code[false_jump] = (OpCode.JMP_IF_FALSE, len(self.chunk.code))

        # Patch elif end jumps
        for jmp_idx in elif_end_jumps:
            self.chunk.code[jmp_idx] = (OpCode.JMP, len(self.chunk.code))

    def _visit_WhileLoop(self, node: WhileLoop):
        self._line(node)
        loop_start = len(self.chunk.code)
        self._visit(node.condition)
        self.chunk.emit(OpCode.JMP_IF_FALSE, 0, self.current_line)
        exit_jump = len(self.chunk.code) - 1

        self.loop_stack.append((loop_start, 0, loop_start))  # continue goes to condition

        self._visit(node.body)

        self.chunk.emit(OpCode.JMP, loop_start, self.current_line)
        self.chunk.code[exit_jump] = (OpCode.JMP_IF_FALSE, len(self.chunk.code))

        self.loop_stack.pop()

    def _visit_ForLoop(self, node: ForLoop):
        self._line(node)
        # For loops are handled by the interpreter at runtime
        # We compile the body and use a special approach
        # For now, compile to use the interpreter's for-loop handling
        # by evaluating the iterable and calling a built-in for-each
        self._visit(node.iterable)
        # Store iterable
        self.chunk.emit(OpCode.DUP, line=self.current_line)
        iter_slot = len(self.locals)
        self.locals.append('__iter__')
        self.chunk.emit(OpCode.STORE, iter_slot, self.current_line)

        # Loop start
        loop_start = len(self.chunk.code)

        # Load iterable, check if done
        self.chunk.emit(OpCode.LOAD, iter_slot, self.current_line)
        self.chunk.emit(OpCode.LEN, line=self.current_line)
        self.chunk.emit(OpCode.PUSH_INT, self.chunk.add_constant(0), self.current_line)
        self.chunk.emit(OpCode.EQ, line=self.current_line)
        self.chunk.emit(OpCode.JMP_IF_TRUE, 0, self.current_line)
        exit_jump = len(self.chunk.code) - 1

        # Pop first element from iterable (simplified: just use index 0)
        self.chunk.emit(OpCode.LOAD, iter_slot, self.current_line)
        self.chunk.emit(OpCode.PUSH_INT, self.chunk.add_constant(0), self.current_line)
        self.chunk.emit(OpCode.GET_ITEM, line=self.current_line)

        # Store loop variable
        self.locals.append(node.variable)
        var_slot = len(self.locals) - 1
        self.chunk.emit(OpCode.STORE, var_slot, self.current_line)

        # Remove first element from iterable
        self.chunk.emit(OpCode.LOAD, iter_slot, self.current_line)
        self.chunk.emit(OpCode.PUSH_INT, self.chunk.add_constant(0), self.current_line)
        self.chunk.emit(OpCode.GET_ITEM, line=self.current_line)
        self.chunk.emit(OpCode.POP, line=self.current_line)

        # Loop body
        self.loop_stack.append((loop_start, 0, loop_start))
        self._visit(node.body)
        self.locals.pop()  # Remove loop variable

        self.chunk.emit(OpCode.JMP, loop_start, self.current_line)
        self.chunk.code[exit_jump] = (OpCode.JMP_IF_TRUE, len(self.chunk.code))

        self.locals.pop()  # Remove __iter__
        self.loop_stack.pop()

    def _visit_FunctionDef(self, node: FunctionDef):
        self._line(node)
        # Create a new chunk for this function
        func_chunk = Chunk(node.name)
        saved_chunk = self.chunk
        saved_locals = self.locals
        saved_globals = self.globals

        self.chunk = func_chunk
        self.locals = []
        self.globals = set()

        # Declare parameters as locals
        for param in node.parameters:
            self.locals.append(param.name)

        # Compile body
        self._visit(node.body)

        # Ensure return at end
        self.chunk.emit(OpCode.PUSH_NULL, line=self.current_line)
        self.chunk.emit(OpCode.RETURN, line=self.current_line)

        self.function_chunks.append((node.name, func_chunk, len(node.parameters)))

        self.chunk = saved_chunk
        self.locals = saved_locals
        self.globals = saved_globals

        # Emit MAKE_FUNCTION in current chunk
        idx = self.chunk.add_constant(node.name)
        self.chunk.emit(OpCode.MAKE_FUNCTION, idx, self.current_line)
        # Store function
        if self._is_global_scope():
            g_idx = self.chunk.add_constant(node.name)
            self.chunk.emit(OpCode.STORE_GLOBAL, g_idx, self.current_line)
            self.globals.add(node.name)
        else:
            self.locals.append(node.name)
            slot = len(self.locals) - 1
            self.chunk.emit(OpCode.STORE, slot, self.current_line)

    def _visit_ClassDef(self, node: ClassDef):
        self._line(node)
        # Simplified: store class info for method compilation
        self._class_info = node.name
        # For now, classes are handled by the interpreter
        # We emit a placeholder
        idx = self.chunk.add_constant(node.name)
        self.chunk.emit(OpCode.MAKE_CLASS, idx, self.current_line)
        if self._is_global_scope():
            g_idx = self.chunk.add_constant(node.name)
            self.chunk.emit(OpCode.STORE_GLOBAL, g_idx, self.current_line)
            self.globals.add(node.name)
        self._class_info = None

    def _visit_TryStatement(self, node: TryStatement):
        self._line(node)
        # Push handler
        self.chunk.emit(OpCode.PUSH_HANDLER, 0, self.current_line)
        handler_idx = len(self.chunk.code) - 1

        self._visit(node.try_block)

        # Pop handler
        self.chunk.emit(OpCode.POP_HANDLER, line=self.current_line)
        self.chunk.emit(OpCode.JMP, 0, self.current_line)
        after_catch = len(self.chunk.code) - 1

        # Patch handler to point here
        self.chunk.code[handler_idx] = (OpCode.PUSH_HANDLER, len(self.chunk.code))

        # Catch block
        self.locals.append(node.catch_var)
        slot = len(self.locals) - 1
        self.chunk.emit(OpCode.STORE, slot, self.current_line)
        self._visit(node.catch_block)
        self.locals.pop()

        self.chunk.code[after_catch] = (OpCode.JMP, len(self.chunk.code))

    def _visit_ThrowStatement(self, node: ThrowStatement):
        self._line(node)
        self._visit(node.value)
        self.chunk.emit(OpCode.THROW, line=self.current_line)

    def _visit_ImportStatement(self, node: ImportStatement):
        self._line(node)
        # Imports are handled at runtime
        pass

    # ─── Expressions ──────────────────────────────────────────────────────

    def _visit_Literal(self, node: Literal):
        self._line(node)
        val = node.value
        if val is None:
            self.chunk.emit(OpCode.PUSH_NULL, line=self.current_line)
        elif isinstance(val, bool):
            if val:
                self.chunk.emit(OpCode.PUSH_TRUE, line=self.current_line)
            else:
                self.chunk.emit(OpCode.PUSH_FALSE, line=self.current_line)
        elif isinstance(val, int):
            idx = self.chunk.add_constant(val)
            self.chunk.emit(OpCode.PUSH_INT, idx, self.current_line)
        elif isinstance(val, float):
            idx = self.chunk.add_constant(val)
            self.chunk.emit(OpCode.PUSH_FLOAT, idx, self.current_line)
        elif isinstance(val, str):
            idx = self.chunk.add_constant(val)
            self.chunk.emit(OpCode.PUSH_STRING, idx, self.current_line)

    def _visit_Identifier(self, node: Identifier):
        self._line(node)
        name = node.name
        if name in self.locals:
            slot = self.locals.index(name)
            self.chunk.emit(OpCode.LOAD, slot, self.current_line)
        elif name in self.globals:
            idx = self.chunk.add_constant(name)
            self.chunk.emit(OpCode.LOAD_GLOBAL, idx, self.current_line)
        else:
            # Assume global (will be resolved at runtime)
            idx = self.chunk.add_constant(name)
            self.chunk.emit(OpCode.LOAD_GLOBAL, idx, self.current_line)

    def _visit_BinaryOp(self, node: BinaryOp):
        self._line(node)
        op = node.operator

        # Short-circuit logical operators
        if op == 'and':
            self._visit(node.left)
            self.chunk.emit(OpCode.DUP, line=self.current_line)
            self.chunk.emit(OpCode.JMP_IF_FALSE, 0, self.current_line)
            jmp = len(self.chunk.code) - 1
            self.chunk.emit(OpCode.POP, line=self.current_line)
            self._visit(node.right)
            self.chunk.code[jmp] = (OpCode.JMP_IF_FALSE, len(self.chunk.code))
            return
        elif op == 'or':
            self._visit(node.left)
            self.chunk.emit(OpCode.DUP, line=self.current_line)
            self.chunk.emit(OpCode.JMP_IF_TRUE, 0, self.current_line)
            jmp = len(self.chunk.code) - 1
            self.chunk.emit(OpCode.POP, line=self.current_line)
            self._visit(node.right)
            self.chunk.code[jmp] = (OpCode.JMP_IF_TRUE, len(self.chunk.code))
            return

        # Range operator
        if op == '..':
            self._visit(node.left)
            self._visit(node.right)
            self.chunk.emit(OpCode.MAKE_RANGE, line=self.current_line)
            return

        # Standard binary operators
        self._visit(node.left)
        self._visit(node.right)

        op_map = {
            '+': OpCode.ADD, '-': OpCode.SUB, '*': OpCode.MUL,
            '/': OpCode.DIV, '%': OpCode.MOD, '**': OpCode.POW,
            '==': OpCode.EQ, '!=': OpCode.NEQ, '<': OpCode.LT,
            '>': OpCode.GT, '<=': OpCode.LE, '>=': OpCode.GE,
            '&': OpCode.BIT_AND, '|': OpCode.BIT_OR, '^': OpCode.BIT_XOR,
            '<<': OpCode.SHL, '>>': OpCode.SHR,
        }
        if op in op_map:
            self.chunk.emit(op_map[op], line=self.current_line)

    def _visit_UnaryOp(self, node: UnaryOp):
        self._line(node)
        self._visit(node.operand)
        if node.operator == '-':
            self.chunk.emit(OpCode.NEG, line=self.current_line)
        elif node.operator == 'not':
            self.chunk.emit(OpCode.NOT, line=self.current_line)
        elif node.operator == '~':
            self.chunk.emit(OpCode.BIT_NOT, line=self.current_line)

    def _visit_MemberAccess(self, node: MemberAccess):
        self._line(node)
        self._visit(node.object)
        idx = self.chunk.add_constant(node.member)
        self.chunk.emit(OpCode.GET_ATTR, idx, self.current_line)

    def _visit_Subscript(self, node: Subscript):
        self._line(node)
        self._visit(node.object)
        self._visit(node.index)
        self.chunk.emit(OpCode.GET_ITEM, line=self.current_line)

    def _visit_FunctionCall(self, node: FunctionCall):
        self._line(node)
        # Evaluate arguments
        for arg in node.arguments:
            self._visit(arg)
        # Evaluate callee
        self._visit(node.callee)
        self.chunk.emit(OpCode.CALL, len(node.arguments), self.current_line)

    def _visit_ArrayLiteral(self, node: ArrayLiteral):
        self._line(node)
        for elem in node.elements:
            self._visit(elem)
        self.chunk.emit(OpCode.MAKE_ARRAY, len(node.elements), self.current_line)

    def _visit_MapLiteral(self, node: MapLiteral):
        self._line(node)
        for key, value in node.entries:
            self._visit(key)
            self._visit(value)
        self.chunk.emit(OpCode.MAKE_MAP, len(node.entries), self.current_line)

    def _visit_ThisExpression(self, node: ThisExpression):
        self._line(node)
        self.chunk.emit(OpCode.LOAD_THIS, line=self.current_line)

    def _visit_RangeLiteral(self, node: RangeLiteral):
        self._line(node)
        self._visit(node.start)
        self._visit(node.end)
        self.chunk.emit(OpCode.MAKE_RANGE, line=self.current_line)

    def _is_global_scope(self) -> bool:
        """Check if we're currently in global scope."""
        return len(self.locals) == 0 and self.chunk.name == "<script>"
