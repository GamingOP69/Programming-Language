"""
Samrat Benchmark Suite

Measures performance of lexer, parser, semantic analyzer, interpreter,
and bytecode VM on programs of varying sizes.

Usage:
    python benchmarks.py              # Run all benchmarks
    python benchmarks.py --quick      # Run quick benchmarks only
    python benchmarks.py --json       # Output as JSON
"""

import sys
import os
import time
import json
import statistics

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from lexer import Lexer
from parser import Parser
from semantic import SemanticAnalyzer
from interpreter import Interpreter
from compiler import Compiler
from vm import VM
from optimizer import optimize


# ─── Test Programs ─────────────────────────────────────────────────────────

SMALL_PROGRAM = """
let x = 5
let y = 10
let z = x + y
print(z)
"""

MEDIUM_PROGRAM = """
func fibonacci(n: int) -> int {
    if n <= 1 {
        return n
    }
    return fibonacci(n - 1) + fibonacci(n - 2)
}

func factorial(n: int) -> int {
    if n <= 1 {
        return 1
    }
    return n * factorial(n - 1)
}

let result_fib = fibonacci(10)
let result_fact = factorial(10)
print("Fibonacci(10): " + str(result_fib))
print("Factorial(10): " + str(result_fact))

let sum = 0
for i in 0..100 {
    sum = sum + i
}
print("Sum 0..99: " + str(sum))
"""

LARGE_PROGRAM = """
func fibonacci(n: int) -> int {
    if n <= 1 {
        return n
    }
    return fibonacci(n - 1) + fibonacci(n - 2)
}

func factorial(n: int) -> int {
    if n <= 1 {
        return 1
    }
    return n * factorial(n - 1)
}

func is_prime(n: int) -> bool {
    if n <= 1 {
        return false
    }
    let i = 2
    while i * i <= n {
        if n % i == 0 {
            return false
        }
        i = i + 1
    }
    return true
}

func gcd(a: int, b: int) -> int {
    if b == 0 {
        return a
    }
    return gcd(b, a % b)
}

func lcm(a: int, b: int) -> int {
    return a * b / gcd(a, b)
}

// Test all functions
let fib_result = fibonacci(15)
let fact_result = factorial(10)
let prime_count = 0
let prime_sum = 0

for i in 2..50 {
    if is_prime(i) {
        prime_count = prime_count + 1
        prime_sum = prime_sum + i
    }
}

let gcd_result = gcd(48, 18)
let lcm_result = lcm(12, 18)

print("Fibonacci(15): " + str(fib_result))
print("Factorial(10): " + str(fact_result))
print("Primes 2..49: " + str(prime_count))
print("Prime sum: " + str(prime_sum))
print("GCD(48,18): " + str(gcd_result))
print("LCM(12,18): " + str(lcm_result))

// Array operations
let arr = []
for i in 0..100 {
    arr.append(i)
}
arr.reverse()
let arr_sum = 0
for i in 0..100 {
    arr_sum = arr_sum + arr[i]
}
print("Array sum: " + str(arr_sum))

// Map operations
let map = {}
for i in 0..50 {
    map[str(i)] = i * 2
}
let map_sum = 0
let keys = map.keys()
for k in keys {
    map_sum = map_sum + map[k]
}
print("Map sum: " + str(map_sum))
"""


# ─── Benchmark Runner ──────────────────────────────────────────────────────

class BenchmarkResult:
    """Stores benchmark results for a single test."""
    def __init__(self, name: str):
        self.name = name
        self.phases = {}  # phase_name -> elapsed_time
        self.total_time = 0.0

    def add_phase(self, phase: str, elapsed: float):
        self.phases[phase] = elapsed
        self.total_time += elapsed

    def __repr__(self) -> str:
        parts = [f"{self.name}: {self.total_time*1000:.1f}ms"]
        for phase, elapsed in self.phases.items():
            parts.append(f"  {phase}: {elapsed*1000:.1f}ms")
        return '\n'.join(parts)


def run_benchmark(name: str, source: str, iterations: int = 3) -> BenchmarkResult:
    """Run a full pipeline benchmark on a source program."""
    result = BenchmarkResult(name)

    # Warmup
    for _ in range(2):
        lexer = Lexer(source)
        lexer.tokenize()

    # Lexer benchmark
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        times.append(time.perf_counter() - start)
    result.add_phase('lexer', statistics.median(times))

    # Parser benchmark
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        parser = Parser(tokens)
        ast = parser.parse()
        times.append(time.perf_counter() - start)
    result.add_phase('parser', statistics.median(times))

    # Semantic analyzer benchmark
    parser = Parser(tokens)
    ast = parser.parse()
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast)
        times.append(time.perf_counter() - start)
    result.add_phase('semantic', statistics.median(times))

    # Interpreter benchmark
    parser = Parser(tokens)
    ast = parser.parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        interpreter = Interpreter()
        interpreter.interpret(ast)
        times.append(time.perf_counter() - start)
    result.add_phase('interpreter', statistics.median(times))

    # Compiler benchmark
    parser = Parser(tokens)
    ast = parser.parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        compiler = Compiler()
        chunk = compiler.compile(ast)
        times.append(time.perf_counter() - start)
    result.add_phase('compiler', statistics.median(times))

    # Optimizer benchmark
    compiler = Compiler()
    chunk = compiler.compile(ast)
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        optimized = optimize(chunk)
        times.append(time.perf_counter() - start)
    result.add_phase('optimizer', statistics.median(times))

    # VM benchmark
    compiler = Compiler()
    chunk = compiler.compile(ast)
    vm = VM()
    for name_, func_chunk, param_count in compiler.function_chunks:
        vm._function_chunks[name_] = (func_chunk, param_count)
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        vm.run(chunk)
        times.append(time.perf_counter() - start)
    result.add_phase('vm', statistics.median(times))

    # Optimized VM benchmark
    compiler = Compiler()
    chunk = compiler.compile(ast)
    optimized = optimize(chunk)
    vm = VM()
    for name_, func_chunk, param_count in compiler.function_chunks:
        vm._function_chunks[name_] = (func_chunk, param_count)
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        vm.run(optimized)
        times.append(time.perf_counter() - start)
    result.add_phase('vm_optimized', statistics.median(times))

    return result


def run_stress_test():
    """Run a stress test with a large generated program."""
    print("\n[Stress Test]")
    print("-" * 60)

    # Generate a large program with many variables and operations
    lines = []
    for i in range(500):
        lines.append(f"let x{i} = {i}")
    for i in range(499):
        lines.append(f"let y{i} = x{i} + x{i + 1}")
    source = '\n'.join(lines)

    # Lexer
    start = time.perf_counter()
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    lex_time = time.perf_counter() - start
    print(f"  Lexer: {lex_time*1000:.1f}ms ({len(tokens)} tokens)")

    # Parser
    start = time.perf_counter()
    parser = Parser(tokens)
    ast = parser.parse()
    parse_time = time.perf_counter() - start
    print(f"  Parser: {parse_time*1000:.1f}ms")

    # Semantic
    start = time.perf_counter()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    sem_time = time.perf_counter() - start
    print(f"  Semantic: {sem_time*1000:.1f}ms")

    # Interpreter
    start = time.perf_counter()
    interpreter = Interpreter()
    interpreter.interpret(ast)
    interp_time = time.perf_counter() - start
    print(f"  Interpreter: {interp_time*1000:.1f}ms")

    # Compiler
    start = time.perf_counter()
    compiler = Compiler()
    chunk = compiler.compile(ast)
    comp_time = time.perf_counter() - start
    print(f"  Compiler: {comp_time*1000:.1f}ms ({len(chunk.code)} instructions)")

    # VM
    vm = VM()
    for name_, func_chunk, param_count in compiler.function_chunks:
        vm._function_chunks[name_] = (func_chunk, param_count)
    start = time.perf_counter()
    vm.run(chunk)
    vm_time = time.perf_counter() - start
    print(f"  VM: {vm_time*1000:.1f}ms")

    total = lex_time + parse_time + sem_time + interp_time
    print(f"  Total (interpreter): {total*1000:.1f}ms")
    print(f"  Total (VM): {(lex_time + parse_time + sem_time + comp_time + vm_time)*1000:.1f}ms")


def run_all(quick: bool = False, output_json: bool = False):
    """Run all benchmarks."""
    print("=" * 60)
    print("  Samrat Benchmark Suite")
    print("=" * 60)
    print()

    programs = [
        ("Small Program", SMALL_PROGRAM, 5),
        ("Medium Program", MEDIUM_PROGRAM, 3),
    ]

    if not quick:
        programs.append(("Large Program", LARGE_PROGRAM, 2))

    results = []

    for name, source, iterations in programs:
        print(f"\n[{name}] ({len(source)} chars, {iterations} iterations)")
        print("-" * 60)
        result = run_benchmark(name, source, iterations)
        print(result)
        results.append(result)

    # Stress test
    if not quick:
        run_stress_test()

    # Summary
    print("\n" + "=" * 60)
    print("  Summary")
    print("=" * 60)
    print(f"{'Program':20s} {'Lexer':>8s} {'Parser':>8s} {'Semantic':>8s} {'Interp':>8s} {'Compiler':>8s} {'VM':>8s} {'VM+Opt':>8s}")
    print("-" * 84)
    for r in results:
        lex = f"{r.phases.get('lexer', 0)*1000:.1f}ms"
        par = f"{r.phases.get('parser', 0)*1000:.1f}ms"
        sem = f"{r.phases.get('semantic', 0)*1000:.1f}ms"
        interp = f"{r.phases.get('interpreter', 0)*1000:.1f}ms"
        comp = f"{r.phases.get('compiler', 0)*1000:.1f}ms"
        vm = f"{r.phases.get('vm', 0)*1000:.1f}ms"
        vm_opt = f"{r.phases.get('vm_optimized', 0)*1000:.1f}ms"
        print(f"{r.name:20s} {lex:>8s} {par:>8s} {sem:>8s} {interp:>8s} {comp:>8s} {vm:>8s} {vm_opt:>8s}")

    if output_json:
        json_results = []
        for r in results:
            json_results.append({
                'name': r.name,
                'phases': r.phases,
                'total_time': r.total_time,
            })
        print("\n" + json.dumps(json_results, indent=2))

    return True


if __name__ == "__main__":
    quick = '--quick' in sys.argv
    output_json = '--json' in sys.argv
    run_all(quick=quick, output_json=output_json)