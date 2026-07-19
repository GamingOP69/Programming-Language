"""
Samrat Programming Language — Symbol Table

The symbol table manages scopes and tracks all declared names (variables,
constants, functions, classes) along with their types and other metadata.
It is used by the semantic analyzer to validate name resolution and type
correctness.

Features:
- Nested scoping with parent chain
- Variable, constant, function, and class declarations
- Type information tracking
- Duplicate declaration detection
- Undefined reference detection
"""


class Symbol:
    """Represents a single symbol (variable, constant, function, class)."""

    def __init__(self, name: str, kind: str, symbol_type: str = None,
                 is_mutable: bool = True, line: int = 0, column: int = 0):
        self.name = name
        self.kind = kind          # 'variable', 'constant', 'function', 'class', 'parameter'
        self.symbol_type = symbol_type  # 'int', 'str', 'bool', 'float', '[int]', etc.
        self.is_mutable = is_mutable
        self.line = line
        self.column = column
        self.initialized = False  # Has this symbol been assigned a value?

    def __repr__(self) -> str:
        return (f"Symbol({self.name}, kind={self.kind}, "
                f"type={self.symbol_type}, mutable={self.is_mutable})")


class Scope:
    """
    A single scope level in the symbol table hierarchy.

    Each scope has:
    - A dictionary of symbols declared in this scope
    - A reference to the enclosing (parent) scope
    - A type (global, function, block, class)
    """

    def __init__(self, scope_type: str = 'block', parent=None):
        self.symbols = {}          # name -> Symbol
        self.parent = parent
        self.scope_type = scope_type  # 'global', 'function', 'block', 'class'

    def declare(self, symbol: Symbol) -> bool:
        """
        Declare a new symbol in this scope.

        Returns True if successful, False if symbol already exists in this scope.
        """
        if symbol.name in self.symbols:
            return False
        self.symbols[symbol.name] = symbol
        return True

    def lookup(self, name: str) -> Symbol:
        """
        Look up a symbol by name, searching this scope and all parent scopes.

        Returns the Symbol if found, None otherwise.
        """
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.lookup(name)
        return None

    def lookup_local(self, name: str) -> Symbol:
        """Look up a symbol only in this scope (not parents)."""
        return self.symbols.get(name)

    def has_symbol(self, name: str) -> bool:
        """Check if a symbol exists in this scope or any parent."""
        return self.lookup(name) is not None

    def __repr__(self) -> str:
        return f"Scope({self.scope_type}, {len(self.symbols)} symbols)"


class SymbolTable:
    """
    Manages the entire scope hierarchy for a program.

    Provides methods for entering/leaving scopes, declaring symbols,
    and looking up symbols by name.
    """

    def __init__(self):
        self.global_scope = Scope('global', parent=None)
        self.current_scope = self.global_scope
        self.scope_stack = [self.global_scope]

    def enter_scope(self, scope_type: str = 'block'):
        """Enter a new nested scope."""
        new_scope = Scope(scope_type, parent=self.current_scope)
        self.scope_stack.append(new_scope)
        self.current_scope = new_scope

    def leave_scope(self):
        """Leave the current scope and return to the parent."""
        if len(self.scope_stack) > 1:
            self.scope_stack.pop()
            self.current_scope = self.scope_stack[-1]

    def declare(self, name: str, kind: str, symbol_type: str = None,
                is_mutable: bool = True, line: int = 0, column: int = 0) -> bool:
        """
        Declare a new symbol in the current scope.

        Returns True if successful, False if duplicate in current scope.
        """
        symbol = Symbol(name, kind, symbol_type, is_mutable, line, column)
        return self.current_scope.declare(symbol)

    def lookup(self, name: str) -> Symbol:
        """Look up a symbol in the current scope chain."""
        return self.current_scope.lookup(name)

    def lookup_local(self, name: str) -> Symbol:
        """Look up a symbol only in the current scope."""
        return self.current_scope.lookup_local(name)

    def is_global_scope(self) -> bool:
        """Check if we're currently in the global scope."""
        return self.current_scope is self.global_scope

    def current_scope_type(self) -> str:
        """Get the type of the current scope."""
        return self.current_scope.scope_type

    def __repr__(self) -> str:
        return f"SymbolTable({len(self.scope_stack)} scopes)"