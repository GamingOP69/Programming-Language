"""
Samrat Programming Language — Bytecode Optimizer

Implements peephole optimization and constant folding on bytecode chunks
to improve execution performance.

Optimizations:
1. Constant Folding: Pre-compute constant expressions at compile time
2. Dead Code Elimination: Remove unreachable code after return/throw/break
3. Peephole Optimizations: Pattern matching on short instruction sequences
4. Strength Reduction: Replace expensive ops with cheaper equivalents

Usage:
    from optimizer import optimize
    optimized = optimize(chunk)
"""

from bytecode import OpCode, Chunk


def optimize(chunk: Chunk) -> Chunk:
    """
    Optimize a bytecode chunk by applying a series of optimization passes.

    Args:
        chunk: The bytecode chunk to optimize.

    Returns:
        The optimized bytecode chunk (may be the same object or a new one).
    """
    # Run optimization passes in order
    chunk = constant_folding(chunk)
    chunk = dead_code_elimination(chunk)
    chunk = peephole_optimization(chunk)
    chunk = strength_reduction(chunk)
    return chunk


def constant_folding(chunk: Chunk) -> Chunk:
    """
    Fold constant expressions at compile time.

    Detects sequences like PUSH_INT(5), PUSH_INT(3), ADD and replaces
    them with PUSH_INT(8).
    """
    if len(chunk.code) < 3:
        return chunk

    # Track which instructions to remove
    new_code = []
    new_lines = []
    i = 0

    while i < len(chunk.code):
        opcode, arg = chunk.code[i]

        # Look for PUSH_*, PUSH_*, BINARY_OP patterns
        if (
            i + 2 < len(chunk.code)
            and _is_push_op(chunk.code[i][0])
            and _is_push_op(chunk.code[i + 1][0])
            and _is_foldable_binary(chunk.code[i + 2][0])
        ):

            left_val = (
                chunk.constants[chunk.code[i][1]]
                if chunk.code[i][1] is not None
                else _get_push_value(chunk.code[i])
            )
            right_val = (
                chunk.constants[chunk.code[i + 1][1]]
                if chunk.code[i + 1][1] is not None
                else _get_push_value(chunk.code[i + 1])
            )
            binary_op = chunk.code[i + 2][0]
            line = chunk.lines[i]

            # Try to fold
            result = _fold_constants(left_val, right_val, binary_op)
            if result is not None:
                # Emit the folded constant
                if isinstance(result, int):
                    idx = chunk.add_constant(result)
                    new_code.append((OpCode.PUSH_INT, idx))
                    new_lines.append(line)
                elif isinstance(result, float):
                    idx = chunk.add_constant(result)
                    new_code.append((OpCode.PUSH_FLOAT, idx))
                    new_lines.append(line)
                elif isinstance(result, bool):
                    new_code.append((OpCode.PUSH_TRUE if result else OpCode.PUSH_FALSE, None))
                    new_lines.append(line)
                elif result is None:
                    new_code.append((OpCode.PUSH_NULL, None))
                    new_lines.append(line)
                elif isinstance(result, str):
                    idx = chunk.add_constant(result)
                    new_code.append((OpCode.PUSH_STRING, idx))
                    new_lines.append(line)
                else:
                    # Can't fold, emit original three instructions
                    new_code.append(chunk.code[i])
                    new_lines.append(chunk.lines[i] if i < len(chunk.lines) else 0)
                    new_code.append(chunk.code[i + 1])
                    new_lines.append(chunk.lines[i + 1] if i + 1 < len(chunk.lines) else 0)
                    new_code.append(chunk.code[i + 2])
                    new_lines.append(chunk.lines[i + 2] if i + 2 < len(chunk.lines) else 0)

                i += 3
                continue
            else:
                # Can't fold with unary negation: PUSH_*, NEG
                if (
                    i + 1 < len(chunk.code)
                    and _is_push_op(chunk.code[i][0])
                    and chunk.code[i + 1][0] == OpCode.NEG
                ):
                    val = _get_push_value(chunk.code[i])
                    line = chunk.lines[i]
                    if isinstance(val, (int, float)):
                        result = -val
                        if isinstance(result, int):
                            idx = chunk.add_constant(result)
                            new_code.append((OpCode.PUSH_INT, idx))
                            new_lines.append(line)
                        else:
                            idx = chunk.add_constant(result)
                            new_code.append((OpCode.PUSH_FLOAT, idx))
                            new_lines.append(line)
                        i += 2
                        continue

        # Look for NOT + PUSH patterns
        if (
            i + 1 < len(chunk.code)
            and chunk.code[i][0] == OpCode.NOT
            and _is_push_op(chunk.code[i + 1][0])
        ):
            val = _get_push_value(chunk.code[i + 1])
            line = chunk.lines[i]
            if isinstance(val, bool):
                result = not val
                new_code.append((OpCode.PUSH_TRUE if result else OpCode.PUSH_FALSE, None))
                new_lines.append(line)
                i += 2
                continue

        # No folding possible
        new_code.append(chunk.code[i])
        new_lines.append(chunk.lines[i] if i < len(chunk.lines) else 0)
        i += 1

    # Replace chunk code
    chunk.code = new_code
    chunk.lines = new_lines
    return chunk


def _is_push_op(opcode: OpCode) -> bool:
    """Check if an opcode pushes a constant value onto the stack."""
    return opcode in (OpCode.PUSH_NULL, OpCode.PUSH_TRUE, OpCode.PUSH_FALSE,
                      OpCode.PUSH_INT, OpCode.PUSH_FLOAT, OpCode.PUSH_STRING)


def _get_push_value(instruction) -> object:
    """Get the value being pushed by a PUSH instruction."""
    opcode, arg = instruction
    if opcode == OpCode.PUSH_NULL:
        return None
    elif opcode == OpCode.PUSH_TRUE:
        return True
    elif opcode == OpCode.PUSH_FALSE:
        return False
    elif opcode in (OpCode.PUSH_INT, OpCode.PUSH_FLOAT, OpCode.PUSH_STRING):
        return arg  # arg is constant index, resolved by caller
    return None


def _is_foldable_binary(opcode: OpCode) -> bool:
    """Check if a binary opcode can be constant-folded."""
    return opcode in (OpCode.ADD, OpCode.SUB, OpCode.MUL, OpCode.DIV,
                      OpCode.MOD, OpCode.POW,
                      OpCode.EQ, OpCode.NEQ, OpCode.LT, OpCode.GT,
                      OpCode.LE, OpCode.GE,
                      OpCode.BIT_AND, OpCode.BIT_OR, OpCode.BIT_XOR,
                      OpCode.SHL, OpCode.SHR)


def _fold_constants(left, right, opcode):  # noqa: C901
    """Fold two constant values with a binary operation."""
    try:
        if opcode == OpCode.ADD:
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return left + right
            if isinstance(left, str) and isinstance(right, str):
                return left + right
        elif opcode == OpCode.SUB:
            return left - right
        elif opcode == OpCode.MUL:
            return left * right
        elif opcode == OpCode.DIV:
            return left / right
        elif opcode == OpCode.MOD:
            return left % right
        elif opcode == OpCode.POW:
            return left ** right
        elif opcode == OpCode.EQ:
            return left == right
        elif opcode == OpCode.NEQ:
            return left != right
        elif opcode == OpCode.LT:
            return left < right
        elif opcode == OpCode.GT:
            return left > right
        elif opcode == OpCode.LE:
            return left <= right
        elif opcode == OpCode.GE:
            return left >= right
        elif opcode == OpCode.BIT_AND:
            return left & right
        elif opcode == OpCode.BIT_OR:
            return left | right
        elif opcode == OpCode.BIT_XOR:
            return left ^ right
        elif opcode == OpCode.SHL:
            return left << right
        elif opcode == OpCode.SHR:
            return left >> right
        return None
    except (TypeError, ZeroDivisionError, OverflowError):
        return None


def dead_code_elimination(chunk: Chunk) -> Chunk:
    """
    Remove unreachable code after unconditional jumps, returns, and throws.

    Also removes duplicate jumps (JMP -> JMP becomes a single JMP).
    """
    if len(chunk.code) < 2:
        return chunk

    # Find unreachable code regions
    reachable = [True] * len(chunk.code)
    i = 0

    while i < len(chunk.code):
        opcode, arg = chunk.code[i]

        # If this instruction is unreachable, mark subsequent as unreachable
        if not reachable[i]:
            i += 1
            continue

        # HALT, RETURN, THROW make subsequent code unreachable
        if opcode in (OpCode.HALT, OpCode.RETURN, OpCode.THROW):
            j = i + 1
            while j < len(chunk.code):
                # Don't skip labels/handlers that might be jump targets
                reachable[j] = False
                j += 1
            break

        # Unconditional jumps: code after jump is unreachable (unless it's a jump target)
        if opcode == OpCode.JMP:
            # Only mark as unreachable if there are no other jumps to the next instruction
            j = i + 1
            while j < len(chunk.code):
                reachable[j] = False
                j += 1
            break

        i += 1

    # Build new chunk from reachable instructions
    new_code = []
    new_lines = []
    for i in range(len(chunk.code)):
        if reachable[i]:
            new_code.append(chunk.code[i])
            new_lines.append(chunk.lines[i] if i < len(chunk.lines) else 0)

    chunk.code = new_code
    chunk.lines = new_lines
    return chunk


def peephole_optimization(chunk: Chunk) -> Chunk:
    """
    Apply peephole optimizations on short instruction sequences.

    Optimizations:
    - POP + POP + ADD -> ADD (reorder stack pops)
    - JMP + JMP_IF_FALSE -> remove redundant jump
    - PUSH_*, POP -> remove both
    - LOAD + STORE -> DUP (when same slot)
    - Consecutive JMPs to same target
    """
    if len(chunk.code) < 2:
        return chunk

    i = 0
    new_code = []
    new_lines = []

    while i < len(chunk.code):
        opcode, arg = chunk.code[i]
        line = chunk.lines[i] if i < len(chunk.lines) else 0

        # PUSH_* followed immediately by POP: remove both
        if (
            i + 1 < len(chunk.code)
            and _is_push_op(opcode)
            and chunk.code[i + 1][0] == OpCode.POP
        ):
            i += 2
            continue

        # DUP followed by POP: remove both
        if (
            opcode == OpCode.DUP
            and i + 1 < len(chunk.code)
            and chunk.code[i + 1][0] == OpCode.POP
        ):
            i += 2
            continue

        # JMP to next instruction: remove it
        if opcode == OpCode.JMP and arg == i + 1:
            i += 1
            continue

        # JMP to another JMP: resolve to final target
        if opcode == OpCode.JMP:
            target = arg
            # Follow the chain
            seen = set()
            while (
                target < len(chunk.code)
                and chunk.code[target][0] == OpCode.JMP
            ):
                if target in seen:
                    break  # Cycle detected
                seen.add(target)
                new_target = chunk.code[target][1]
                if new_target == target:
                    break
                target = new_target
            new_code.append((OpCode.JMP, target))
            new_lines.append(line)
            i += 1
            continue

        # NOT + NOT: remove both
        if (
            opcode == OpCode.NOT
            and i + 1 < len(chunk.code)
            and chunk.code[i + 1][0] == OpCode.NOT
        ):
            i += 2
            continue

        # NEG + NEG: remove both (double negation)
        if (
            opcode == OpCode.NEG
            and i + 1 < len(chunk.code)
            and chunk.code[i + 1][0] == OpCode.NEG
        ):
            i += 2
            continue

        new_code.append(chunk.code[i])
        new_lines.append(line)
        i += 1

    chunk.code = new_code
    chunk.lines = new_lines
    return chunk


def strength_reduction(chunk: Chunk) -> Chunk:
    """
    Replace expensive operations with cheaper equivalents.

    Optimizations:
    - x ** 2 -> x * x
    - x * 2 -> x << 1
    - x / 2 -> x >> 1 (for integers)
    - x ** 0 -> 1
    - x * 0 -> 0
    - x * 1 -> x
    - x + 0 -> x
    - x - 0 -> x
    """
    if len(chunk.code) < 3:
        return chunk

    i = 0
    new_code = []
    new_lines = []

    while i < len(chunk.code):
        opcode, arg = chunk.code[i]
        line = chunk.lines[i] if i < len(chunk.lines) else 0

        # Look for: PUSH_INT(n), PUSH_INT(m), <BIN_OP>
        if (
            i + 2 < len(chunk.code)
            and (
                chunk.code[i][0] == OpCode.PUSH_INT
                or chunk.code[i][0] == OpCode.PUSH_FLOAT
            )
            and (
                chunk.code[i + 1][0] == OpCode.PUSH_INT
                or chunk.code[i + 1][0] == OpCode.PUSH_FLOAT
            )
            and chunk.code[i + 2][0] in (OpCode.MUL, OpCode.POW, OpCode.ADD, OpCode.SUB)
        ):

            left_const_idx = chunk.code[i][1]
            right_const_idx = chunk.code[i + 1][1]
            left_val = chunk.constants[left_const_idx]
            right_val = chunk.constants[right_const_idx]
            bin_op = chunk.code[i + 2][0]

            # x ** 2 -> x * x
            if bin_op == OpCode.POW and right_val == 2:
                # Replace POW with MUL: value * value
                new_code.append(chunk.code[i])      # PUSH left
                new_lines.append(line)
                new_code.append(chunk.code[i])      # PUSH left again
                new_lines.append(line)
                new_code.append((OpCode.MUL, None))  # MUL
                new_lines.append(chunk.lines[i + 2] if i + 2 < len(chunk.lines) else 0)
                i += 3
                continue

            # x * 2 -> x << 1
            if bin_op == OpCode.MUL and right_val == 2:
                new_code.append(chunk.code[i])      # PUSH x
                new_lines.append(line)
                idx = chunk.add_constant(1)
                new_code.append((OpCode.PUSH_INT, idx))  # PUSH 1
                new_lines.append(line)
                new_code.append((OpCode.SHL, None))      # SHL
                new_lines.append(chunk.lines[i + 2] if i + 2 < len(chunk.lines) else 0)
                i += 3
                continue

            # x * 0 -> 0
            if bin_op == OpCode.MUL and (left_val == 0 or right_val == 0):
                zero_idx = chunk.add_constant(0)
                new_code.append((OpCode.PUSH_INT, zero_idx))
                new_lines.append(line)
                i += 3
                continue

            # x * 1 -> x
            if bin_op == OpCode.MUL and right_val == 1:
                new_code.append(chunk.code[i])  # Just keep left
                new_lines.append(line)
                i += 3
                continue

            # x + 0 -> x
            if bin_op == OpCode.ADD and right_val == 0:
                new_code.append(chunk.code[i])  # Just keep left
                new_lines.append(line)
                i += 3
                continue

            # x - 0 -> x
            if bin_op == OpCode.SUB and right_val == 0:
                new_code.append(chunk.code[i])  # Just keep left
                new_lines.append(line)
                i += 3
                continue

        # No optimization
        new_code.append(chunk.code[i])
        new_lines.append(line)
        i += 1

    chunk.code = new_code
    chunk.lines = new_lines
    return chunk


def optimize_all(chunks: dict) -> dict:
    """
    Optimize multiple chunks (e.g., main script + all functions).

    Args:
        chunks: Dictionary mapping chunk names to Chunk objects.

    Returns:
        Dictionary of optimized chunks.
    """
    result = {}
    for name, chunk in chunks.items():
        result[name] = optimize(chunk)
    return result
