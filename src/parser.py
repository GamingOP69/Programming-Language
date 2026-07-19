"""
Samrat Programming Language — Recursive-Descent Parser

The parser is the second phase of the Samrat compiler pipeline. It consumes
tokens from the lexer and produces an Abstract Syntax Tree (AST) that the
semantic analyzer and interpreter can process.

This parser:
- Uses recursive-descent parsing with one token of lookahead
- Implements operator precedence via a Pratt-like precedence climbing
- Produces clear, descriptive syntax error messages with location info
- Handles all Samrat language constructs

Usage:
    from lexer import Lexer
    from parser import Parser
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
"""

from tokens import Token, TokenType
from ast_nodes import (
    Program, Block, ExpressionStatement,
    VarDeclaration, ConstDeclaration, Assignment,
    IfStatement, WhileLoop, ForLoop,
    BreakStatement, ContinueStatement, ReturnStatement,
    FunctionDef, Parameter, ClassDef, ConstructorDef,
    TryStatement, ThrowStatement, ImportStatement,
    Literal, Identifier, BinaryOp, UnaryOp,
    MemberAccess, Subscript, FunctionCall,
    ArrayLiteral, MapLiteral, ThisExpression,
)
from errors import ParserError


# Operator precedence levels (higher = binds tighter)
# Note: Assignment operators (=, +=, etc.) are NOT in this table.
# They are handled at the statement level in _parse_expression_or_assignment.
PRECEDENCE = {
    TokenType.DOT_DOT: 1,          # .. (range)
    TokenType.OR: 2,               # or
    TokenType.AND: 3,              # and
    TokenType.EQUAL_EQUAL: 4,      # ==
    TokenType.BANG_EQUAL: 4,       # !=
    TokenType.LESS: 5,             # <
    TokenType.GREATER: 5,          # >
    TokenType.LESS_EQUAL: 5,       # <=
    TokenType.GREATER_EQUAL: 5,    # >=
    TokenType.PIPE: 6,             # |
    TokenType.CARET: 7,            # ^
    TokenType.AMPERSAND: 8,        # &
    TokenType.LESS_LESS: 9,        # <<
    TokenType.GREATER_GREATER: 9,  # >>
    TokenType.PLUS: 10,            # +
    TokenType.MINUS: 10,           # -
    TokenType.STAR: 11,            # *
    TokenType.SLASH: 11,           # /
    TokenType.PERCENT: 11,         # %
    TokenType.STAR_STAR: 12,       # **
    TokenType.NOT: 13,             # not (unary)
    TokenType.TILDE: 13,           # ~ (unary)
}

# Tokens that can start an expression
EXPRESSION_START_TOKENS = {
    TokenType.INTEGER, TokenType.FLOAT, TokenType.STRING,
    TokenType.TRUE, TokenType.FALSE, TokenType.NULL,
    TokenType.IDENTIFIER, TokenType.THIS,
    TokenType.LEFT_PAREN, TokenType.LEFT_BRACKET, TokenType.LEFT_BRACE,
    TokenType.MINUS, TokenType.NOT, TokenType.TILDE,
    TokenType.PLUS,
}

# Tokens that can start a statement
STATEMENT_START_TOKENS = {
    TokenType.LET, TokenType.CONST, TokenType.FUNC, TokenType.CLASS,
    TokenType.IF, TokenType.WHILE, TokenType.FOR,
    TokenType.RETURN, TokenType.BREAK, TokenType.CONTINUE,
    TokenType.TRY, TokenType.THROW, TokenType.IMPORT,
    TokenType.LEFT_BRACE,
    TokenType.IDENTIFIER, TokenType.THIS,
    TokenType.INTEGER, TokenType.FLOAT, TokenType.STRING,
    TokenType.TRUE, TokenType.FALSE, TokenType.NULL,
    TokenType.LEFT_PAREN, TokenType.LEFT_BRACKET, TokenType.LEFT_BRACE,
    TokenType.MINUS, TokenType.NOT, TokenType.TILDE,
    TokenType.PLUS,
}


class Parser:
    """
    Recursive-descent parser that converts a token stream into an AST.

    Attributes:
        tokens: The list of tokens from the lexer.
        current: Current position in the token list.
    """

    def __init__(self, tokens: list):
        self.tokens = tokens
        self.current = 0

    def parse(self) -> Program:
        """
        Parse the entire token stream into a Program AST node.

        Returns:
            A Program node containing all top-level statements.
        """
        statements = []
        while not self._is_at_end():
            stmt = self._parse_statement()
            if stmt is not None:
                statements.append(stmt)

        return Program(statements)

    # ─── Statement Parsing ────────────────────────────────────────────────

    def _parse_statement(self):  # noqa: C901
        """Parse a single statement based on the current token."""
        if self._check(TokenType.LET):
            return self._parse_var_declaration()
        elif self._check(TokenType.CONST):
            return self._parse_const_declaration()
        elif self._check(TokenType.FUNC):
            return self._parse_function_def()
        elif self._check(TokenType.CLASS):
            return self._parse_class_def()
        elif self._check(TokenType.IF):
            return self._parse_if_statement()
        elif self._check(TokenType.WHILE):
            return self._parse_while_loop()
        elif self._check(TokenType.FOR):
            return self._parse_for_loop()
        elif self._check(TokenType.RETURN):
            return self._parse_return_statement()
        elif self._check(TokenType.BREAK):
            return self._parse_break_statement()
        elif self._check(TokenType.CONTINUE):
            return self._parse_continue_statement()
        elif self._check(TokenType.TRY):
            return self._parse_try_statement()
        elif self._check(TokenType.THROW):
            return self._parse_throw_statement()
        elif self._check(TokenType.IMPORT):
            return self._parse_import_statement()
        elif self._check(TokenType.LEFT_BRACE):
            # Peek ahead to determine if this is a block or a map literal
            # If the first token inside { is a statement keyword, it's a block
            # Otherwise, it's an expression (map literal or block expression)
            if self._is_block_start():
                return self._parse_block()
            else:
                return self._parse_expression_or_assignment()
        elif self._check(TokenType.EOF):
            return None
        else:
            # Try to parse as expression statement or assignment
            return self._parse_expression_or_assignment()

    def _parse_var_declaration(self) -> VarDeclaration:
        """Parse: let identifier [: type] [= expression]"""
        token = self._advance()  # consume 'let'
        name_token = self._consume(TokenType.IDENTIFIER, "Expected variable name after 'let'")

        var_type = None
        if self._match(TokenType.COLON):
            var_type = self._parse_type()

        initializer = None
        if self._match(TokenType.EQUAL):
            initializer = self._parse_expression()

        return VarDeclaration(
            name_token.value, var_type, initializer,
            line=token.line, column=token.column
        )

    def _parse_const_declaration(self) -> ConstDeclaration:
        """Parse: const identifier [: type] = expression"""
        token = self._advance()  # consume 'const'
        name_token = self._consume(TokenType.IDENTIFIER, "Expected constant name after 'const'")

        const_type = None
        if self._match(TokenType.COLON):
            const_type = self._parse_type()

        self._consume(TokenType.EQUAL, f"Expected '=' in constant declaration for '{name_token.value}'")
        initializer = self._parse_expression()

        return ConstDeclaration(
            name_token.value, const_type, initializer,
            line=token.line, column=token.column
        )

    def _parse_function_def(self) -> FunctionDef:
        """Parse: func name(params) [-> return_type] { body }"""
        token = self._advance()  # consume 'func'
        name_token = self._consume(TokenType.IDENTIFIER, "Expected function name after 'func'")

        self._consume(TokenType.LEFT_PAREN, f"Expected '(' after function name '{name_token.value}'")
        parameters = self._parse_parameter_list()
        self._consume(TokenType.RIGHT_PAREN, f"Expected ')' after parameters for '{name_token.value}'")

        return_type = None
        if self._match(TokenType.ARROW):
            return_type = self._parse_type()

        body = self._parse_block()

        return FunctionDef(
            name_token.value, parameters, return_type, body,
            line=token.line, column=token.column
        )

    def _parse_parameter_list(self) -> list:
        """Parse a list of parameters: param [: type] [= default], ..."""
        parameters = []
        if self._check(TokenType.RIGHT_PAREN):
            return parameters

        while True:
            param_token = self._consume(TokenType.IDENTIFIER, "Expected parameter name")
            param_type = None
            if self._match(TokenType.COLON):
                param_type = self._parse_type()

            default_value = None
            if self._match(TokenType.EQUAL):
                default_value = self._parse_expression()

            parameters.append(Parameter(
                param_token.value, param_type, default_value,
                line=param_token.line, column=param_token.column
            ))

            if not self._match(TokenType.COMMA):
                break

        return parameters

    def _parse_class_def(self) -> ClassDef:
        """Parse: class Name { fields constructor methods }"""
        token = self._advance()  # consume 'class'
        name_token = self._consume(TokenType.IDENTIFIER, "Expected class name after 'class'")
        self._consume(TokenType.LEFT_BRACE, f"Expected '{{' after class name '{name_token.value}'")

        fields = []
        constructor = None
        methods = []

        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            if self._check(TokenType.LET):
                fields.append(self._parse_var_declaration())
            elif self._check(TokenType.CONSTRUCTOR):
                constructor = self._parse_constructor_def()
            elif self._check(TokenType.FUNC):
                methods.append(self._parse_function_def())
            else:
                self._error(f"Unexpected token in class body: {self._peek().lexeme}")

        self._consume(TokenType.RIGHT_BRACE, f"Expected '}}' after class body for '{name_token.value}'")

        return ClassDef(
            name_token.value, fields, constructor, methods,
            line=token.line, column=token.column
        )

    def _parse_constructor_def(self) -> ConstructorDef:
        """Parse: constructor(params) { body }"""
        token = self._advance()  # consume 'constructor'
        self._consume(TokenType.LEFT_PAREN, "Expected '(' after 'constructor'")
        parameters = self._parse_parameter_list()
        self._consume(TokenType.RIGHT_PAREN, "Expected ')' after constructor parameters")
        body = self._parse_block()

        return ConstructorDef(parameters, body, line=token.line, column=token.column)

    def _parse_if_statement(self) -> IfStatement:
        """Parse: if condition { block } [elif condition { block }] [else { block }]"""
        token = self._advance()  # consume 'if'
        condition = self._parse_expression()
        then_block = self._parse_block()

        elif_conditions = []
        elif_blocks = []

        while self._match(TokenType.ELIF):
            elif_conditions.append(self._parse_expression())
            elif_blocks.append(self._parse_block())

        else_block = None
        if self._match(TokenType.ELSE):
            else_block = self._parse_block()

        return IfStatement(
            condition, then_block,
            elif_conditions, elif_blocks, else_block,
            line=token.line, column=token.column
        )

    def _parse_while_loop(self) -> WhileLoop:
        """Parse: while condition { body }"""
        token = self._advance()  # consume 'while'
        condition = self._parse_expression()
        body = self._parse_block()

        return WhileLoop(condition, body, line=token.line, column=token.column)

    def _parse_for_loop(self) -> ForLoop:
        """Parse: for identifier in iterable { body }"""
        token = self._advance()  # consume 'for'
        var_token = self._consume(TokenType.IDENTIFIER, "Expected loop variable after 'for'")
        self._consume(TokenType.IN, f"Expected 'in' after loop variable '{var_token.value}'")
        iterable = self._parse_expression()
        body = self._parse_block()

        return ForLoop(var_token.value, iterable, body, line=token.line, column=token.column)

    def _parse_return_statement(self) -> ReturnStatement:
        """Parse: return [expression]"""
        token = self._advance()  # consume 'return'
        value = None
        if not self._is_at_end() and self._peek().type in EXPRESSION_START_TOKENS:
            value = self._parse_expression()

        return ReturnStatement(value, line=token.line, column=token.column)

    def _parse_break_statement(self) -> BreakStatement:
        """Parse: break"""
        token = self._advance()
        return BreakStatement(line=token.line, column=token.column)

    def _parse_continue_statement(self) -> ContinueStatement:
        """Parse: continue"""
        token = self._advance()
        return ContinueStatement(line=token.line, column=token.column)

    def _parse_try_statement(self) -> TryStatement:
        """Parse: try { body } catch identifier { handler }"""
        token = self._advance()  # consume 'try'
        try_block = self._parse_block()
        self._consume(TokenType.CATCH, "Expected 'catch' after try block")
        catch_var = self._consume(TokenType.IDENTIFIER, "Expected error variable name after 'catch'")
        catch_block = self._parse_block()

        return TryStatement(
            try_block, catch_var.value, catch_block,
            line=token.line, column=token.column
        )

    def _parse_throw_statement(self) -> ThrowStatement:
        """Parse: throw expression"""
        token = self._advance()  # consume 'throw'
        value = self._parse_expression()
        return ThrowStatement(value, line=token.line, column=token.column)

    def _parse_import_statement(self) -> ImportStatement:
        """Parse: import name [as alias] | import name, ... from module [as alias]"""
        token = self._advance()  # consume 'import'

        # Parse the first name
        name_token = self._consume(TokenType.IDENTIFIER, "Expected module or name after 'import'")
        names = [name_token.value]

        # Check if it's "import names from module" form
        if self._match(TokenType.COMMA):
            # Parse additional names
            while True:
                n_token = self._consume(TokenType.IDENTIFIER, "Expected name in import list")
                names.append(n_token.value)
                if not self._match(TokenType.COMMA):
                    break
            self._consume(TokenType.FROM, "Expected 'from' after import names")
            module_token = self._consume(TokenType.IDENTIFIER, "Expected module name after 'from'")
            module = module_token.value
        elif self._match(TokenType.FROM):
            # "import name from module" form
            module_token = self._consume(TokenType.IDENTIFIER, "Expected module name after 'from'")
            module = module_token.value
        else:
            # "import module" form
            module = None

        alias = None
        if self._match(TokenType.AS):
            alias_token = self._consume(TokenType.IDENTIFIER, "Expected alias name after 'as'")
            alias = alias_token.value

        return ImportStatement(names, module, alias, line=token.line, column=token.column)

    def _parse_block(self) -> Block:
        """Parse: { statement* }"""
        token = self._advance()  # consume '{'
        statements = []

        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            stmt = self._parse_statement()
            if stmt is not None:
                statements.append(stmt)

        self._consume(TokenType.RIGHT_BRACE, "Expected '}' after block")
        return Block(statements, line=token.line, column=token.column)

    def _parse_expression_or_assignment(self):
        """Parse an expression that might be an assignment statement."""
        expr = self._parse_expression()

        # Check if this is an assignment
        if self._check(TokenType.EQUAL):
            self._advance()
            value = self._parse_expression()
            return Assignment(expr, value, '=', line=expr.line, column=expr.column)
        elif self._check(TokenType.PLUS_EQUAL):
            self._advance()
            value = self._parse_expression()
            return Assignment(expr, value, '+=', line=expr.line, column=expr.column)
        elif self._check(TokenType.MINUS_EQUAL):
            self._advance()
            value = self._parse_expression()
            return Assignment(expr, value, '-=', line=expr.line, column=expr.column)
        elif self._check(TokenType.STAR_EQUAL):
            self._advance()
            value = self._parse_expression()
            return Assignment(expr, value, '*=', line=expr.line, column=expr.column)
        elif self._check(TokenType.SLASH_EQUAL):
            self._advance()
            value = self._parse_expression()
            return Assignment(expr, value, '/=', line=expr.line, column=expr.column)
        elif self._check(TokenType.PERCENT_EQUAL):
            self._advance()
            value = self._parse_expression()
            return Assignment(expr, value, '%=', line=expr.line, column=expr.column)

        return ExpressionStatement(expr, line=expr.line, column=expr.column)

    # ─── Expression Parsing (Precedence Climbing) ─────────────────────────

    def _parse_expression(self, min_precedence: int = 0):
        """
        Parse an expression using precedence climbing.

        Args:
            min_precedence: The minimum precedence level to respect.

        Returns:
            An AST node representing the expression.
        """
        expr = self._parse_primary()

        while True:
            token = self._peek()
            if token.type == TokenType.EOF:
                break

            # Handle postfix operators (function calls, member access, subscript)
            if token.type == TokenType.LEFT_PAREN:
                expr = self._parse_function_call(expr)
                continue
            elif token.type == TokenType.DOT:
                self._advance()
                member_token = self._consume(TokenType.IDENTIFIER, "Expected member name after '.'")
                expr = MemberAccess(expr, member_token.value,
                                    line=expr.line, column=expr.column)
                continue
            elif token.type == TokenType.LEFT_BRACKET:
                expr = self._parse_subscript(expr)
                continue

            # Handle binary operators
            precedence = PRECEDENCE.get(token.type)
            if precedence is None or precedence < min_precedence:
                break

            self._advance()  # consume the operator

            # Handle right-associative operators
            next_min = precedence
            if token.type in (TokenType.STAR_STAR,):
                next_min = precedence  # right-associative: same precedence

            right = self._parse_expression(next_min)

            # Map token type to operator string
            op_map = {
                TokenType.PLUS: '+', TokenType.MINUS: '-',
                TokenType.STAR: '*', TokenType.SLASH: '/',
                TokenType.PERCENT: '%', TokenType.STAR_STAR: '**',
                TokenType.EQUAL_EQUAL: '==', TokenType.BANG_EQUAL: '!=',
                TokenType.LESS: '<', TokenType.GREATER: '>',
                TokenType.LESS_EQUAL: '<=', TokenType.GREATER_EQUAL: '>=',
                TokenType.AND: 'and', TokenType.OR: 'or',
                TokenType.AMPERSAND: '&', TokenType.PIPE: '|',
                TokenType.CARET: '^',
                TokenType.LESS_LESS: '<<', TokenType.GREATER_GREATER: '>>',
                TokenType.DOT_DOT: '..',
            }
            operator = op_map.get(token.type, token.lexeme)

            expr = BinaryOp(expr, operator, right,
                            line=expr.line, column=expr.column)

        return expr

    def _parse_primary(self):  # noqa: C901
        """Parse a primary expression (the highest precedence)."""
        token = self._advance()

        # Literals
        if token.type == TokenType.INTEGER:
            return Literal(token.value, line=token.line, column=token.column)
        elif token.type == TokenType.FLOAT:
            return Literal(token.value, line=token.line, column=token.column)
        elif token.type == TokenType.STRING:
            return Literal(token.value, line=token.line, column=token.column)
        elif token.type == TokenType.TRUE:
            return Literal(True, line=token.line, column=token.column)
        elif token.type == TokenType.FALSE:
            return Literal(False, line=token.line, column=token.column)
        elif token.type == TokenType.NULL:
            return Literal(None, line=token.line, column=token.column)

        # Identifiers
        elif token.type == TokenType.IDENTIFIER:
            return Identifier(token.value, line=token.line, column=token.column)

        # Type keywords used as function names (int(), str(), etc.)
        # Use token.lexeme since token.value is None for keyword tokens
        elif token.type in (TokenType.INT, TokenType.FLOAT_TYPE,
                            TokenType.STR, TokenType.BOOL):
            return Identifier(token.lexeme, line=token.line, column=token.column)

        # 'this' keyword
        elif token.type == TokenType.THIS:
            return ThisExpression(line=token.line, column=token.column)

        # Grouping
        elif token.type == TokenType.LEFT_PAREN:
            expr = self._parse_expression()
            self._consume(TokenType.RIGHT_PAREN, "Expected ')' after expression")
            return expr

        # Array literal
        elif token.type == TokenType.LEFT_BRACKET:
            return self._parse_array_literal(token)

        # Map literal or block (but block is handled in statement parsing)
        elif token.type == TokenType.LEFT_BRACE:
            return self._parse_map_literal(token)

        # Unary operators
        elif token.type == TokenType.MINUS:
            operand = self._parse_expression(PRECEDENCE.get(TokenType.MINUS, 14))
            return UnaryOp('-', operand, line=token.line, column=token.column)
        elif token.type == TokenType.NOT:
            operand = self._parse_expression(PRECEDENCE.get(TokenType.NOT, 14))
            return UnaryOp('not', operand, line=token.line, column=token.column)
        elif token.type == TokenType.TILDE:
            operand = self._parse_expression(PRECEDENCE.get(TokenType.TILDE, 14))
            return UnaryOp('~', operand, line=token.line, column=token.column)
        elif token.type == TokenType.PLUS:
            # Unary plus is a no-op, just parse the operand
            operand = self._parse_expression(PRECEDENCE.get(TokenType.PLUS, 14))
            return operand

        self._error(f"Unexpected token: '{token.lexeme}'")

    def _parse_function_call(self, callee) -> FunctionCall:
        """Parse: callee(arg1, arg2, ...)"""
        self._advance()  # consume '('
        arguments = []

        if not self._check(TokenType.RIGHT_PAREN):
            while True:
                arguments.append(self._parse_expression())
                if not self._match(TokenType.COMMA):
                    break

        self._consume(TokenType.RIGHT_PAREN, "Expected ')' after function arguments")
        return FunctionCall(callee, arguments, line=callee.line, column=callee.column)

    def _parse_subscript(self, obj) -> Subscript:
        """Parse: obj[index]"""
        self._advance()  # consume '['
        index = self._parse_expression()
        self._consume(TokenType.RIGHT_BRACKET, "Expected ']' after subscript index")
        return Subscript(obj, index, line=obj.line, column=obj.column)

    def _parse_array_literal(self, token) -> ArrayLiteral:
        """Parse: [element, element, ...]"""
        elements = []

        if not self._check(TokenType.RIGHT_BRACKET):
            while True:
                elements.append(self._parse_expression())
                if not self._match(TokenType.COMMA):
                    break

        self._consume(TokenType.RIGHT_BRACKET, "Expected ']' after array elements")
        return ArrayLiteral(elements, line=token.line, column=token.column)

    def _parse_map_literal(self, token) -> MapLiteral:
        """Parse: {key: value, key: value, ...}"""
        entries = []

        if not self._check(TokenType.RIGHT_BRACE):
            while True:
                key = self._parse_expression()
                self._consume(TokenType.COLON, "Expected ':' after map key")
                value = self._parse_expression()
                entries.append((key, value))
                if not self._match(TokenType.COMMA):
                    break

        self._consume(TokenType.RIGHT_BRACE, "Expected '}' after map entries")
        return MapLiteral(entries, line=token.line, column=token.column)

    def _parse_type(self) -> str:
        """Parse a type annotation: int, float, str, bool, void, [type], {type: type}"""
        token = self._peek()

        if token.type == TokenType.LEFT_BRACKET:
            self._advance()  # consume '['
            inner_type = self._parse_type()
            self._consume(TokenType.RIGHT_BRACKET, "Expected ']' after array type")
            return f"[{inner_type}]"
        elif token.type == TokenType.LEFT_BRACE:
            self._advance()  # consume '{'
            key_type = self._parse_type()
            self._consume(TokenType.COLON, "Expected ':' in map type")
            value_type = self._parse_type()
            self._consume(TokenType.RIGHT_BRACE, "Expected '}' after map type")
            return f"{{{key_type}: {value_type}}}"
        elif token.type in (TokenType.INT, TokenType.FLOAT_TYPE,
                            TokenType.STR, TokenType.BOOL, TokenType.VOID):
            self._advance()
            type_names = {
                TokenType.INT: 'int',
                TokenType.FLOAT_TYPE: 'float',
                TokenType.STR: 'str',
                TokenType.BOOL: 'bool',
                TokenType.VOID: 'void',
            }
            return type_names[token.type]
        elif token.type == TokenType.IDENTIFIER:
            self._advance()
            return token.value
        else:
            self._error(f"Expected a type, got '{token.lexeme}'")

    # ─── Helper Methods ───────────────────────────────────────────────────

    def _advance(self) -> Token:
        """Consume and return the current token."""
        token = self.tokens[self.current]
        self.current += 1
        return token

    def _peek(self) -> Token:
        """Return the current token without consuming it."""
        return self.tokens[self.current]

    def _previous(self) -> Token:
        """Return the previously consumed token."""
        return self.tokens[self.current - 1]

    def _check(self, token_type: TokenType) -> bool:
        """Check if the current token is of the given type."""
        if self._is_at_end():
            return False
        return self._peek().type == token_type

    def _match(self, token_type: TokenType) -> bool:
        """If the current token matches, consume and return True."""
        if self._check(token_type):
            self._advance()
            return True
        return False

    def _consume(self, token_type: TokenType, message: str) -> Token:
        """
        Consume the current token if it matches the expected type.
        Otherwise, raise a ParserError.
        """
        if self._check(token_type):
            return self._advance()
        found = self._peek()
        self._error(f"{message}. Got '{found.lexeme}' instead")

    def _is_block_start(self) -> bool:
        """
        Peek ahead to determine if a '{' starts a block or a map literal.
        If we see a statement keyword (let, const, func, class, if, while, for,
        return, break, continue, try, throw, import, or another '{'), it's a block.
        """
        # Save current position
        saved = self.current
        result = False
        # Skip past the '{'
        self.current += 1
        # Skip whitespace-like tokens (not relevant since lexer doesn't produce them)
        # Check the first meaningful token
        if not self._is_at_end():
            token = self._peek()
            if token.type in (TokenType.LET, TokenType.CONST, TokenType.FUNC,
                              TokenType.CLASS, TokenType.IF, TokenType.WHILE,
                              TokenType.FOR, TokenType.RETURN, TokenType.BREAK,
                              TokenType.CONTINUE, TokenType.TRY, TokenType.THROW,
                              TokenType.IMPORT, TokenType.LEFT_BRACE):
                result = True
            elif token.type == TokenType.RIGHT_BRACE:
                # Empty block { }
                result = True
        # Restore position
        self.current = saved
        return result

    def _is_at_end(self) -> bool:
        """Check if we've reached the end of the token stream."""
        return self._peek().type == TokenType.EOF

    def _error(self, message: str):
        """Raise a parser error with position information."""
        token = self._peek()
        raise ParserError(message, token.line, token.column, token.lexeme)
