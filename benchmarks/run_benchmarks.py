#!/usr/bin/env python3
import time
import subprocess
import os

def run_benchmark():
    print("Running Samrat v2.0 Compiler & Execution Benchmarks...")

    start_time = time.time()
    res = subprocess.run(["cargo", "check", "--workspace"], capture_output=True, text=True)
    compile_time = time.time() - start_time

    print(f"[Benchmark] Workspace Cargo Check Time: {compile_time:.3f}s")
    assert res.returncode == 0, "Cargo check failed"

    print("[Benchmark] All benchmarks completed successfully.")

if __name__ == "__main__":
    run_benchmark()
