"""
run_benchmarks.py

Times each Pulse/Python benchmark pair externally (subprocess wall-clock,
not self-reported by either language), runs multiple trials per program,
and prints a results table plus the ratio between them.
"""

import subprocess
import sys
import time
import statistics
from pathlib import Path

TRIALS = 5
BENCH_DIR = Path(__file__).parent
PULSE_DIR = BENCH_DIR / "pulse"
PYTHON_DIR = BENCH_DIR / "python"
PROJECT_ROOT = BENCH_DIR.parent
PULSE_ENTRY = PROJECT_ROOT / "pulse.py"

PAIRS = [
    ("Loop summation (200,000 iterations)", "loop_sum.pul", "loop_sum.py"),
    ("Recursive fibonacci (fib(24))", "fibonacci.pul", "fibonacci.py"),
    ("List comprehension (50,000 elements)", "list_build.pul", "list_build.py"),
    ("Matrix multiply 80x80 x20 (numpy-backed)", "matrix_multiply_tensor.pul", "matrix_multiply_numpy.py"),
    ("Matrix multiply 80x80 x20 (pure Python baseline)", "matrix_multiply_tensor.pul", "matrix_multiply_pure.py"),
]

def time_command(cmd, trials=TRIALS):
    times = []
    for _ in range(trials):
        start = time.perf_counter()
        result = subprocess.run(cmd, capture_output=True, text=True)
        elapsed = time.perf_counter() - start
        if result.returncode != 0:
            print(f"  [error running {' '.join(cmd)}]: {result.stderr.strip()[:300]}", file=sys.stderr)
            return None
        times.append(elapsed)
    return times

def main():
    print(f"Trials per program: {TRIALS}\n")
    header = f"{'Benchmark':<50} {'Pulse median (s)':>18} {'Python median (s)':>19} {'Ratio (Pulse/Python)':>22}"
    print(header)
    print("-" * len(header))
    
    for label, pulse_file, python_file in PAIRS:
        pulse_path = PULSE_DIR / pulse_file
        python_path = PYTHON_DIR / python_file
        
        pulse_times = time_command([sys.executable, str(PULSE_ENTRY), str(pulse_path)])
        python_times = time_command([sys.executable, str(python_path)])
        
        if pulse_times is None or python_times is None:
            print(f"{label:<50} {'ERROR':>18} {'ERROR':>19} {'-':>22}")
            continue
        
        pulse_median = statistics.median(pulse_times)
        python_median = statistics.median(python_times)
        ratio = pulse_median / python_median if python_median > 0 else float("inf")
        
        print(f"{label:<50} {pulse_median:>18.4f} {python_median:>19.4f} {ratio:>21.1f}x")
    
    print("\nRaw per-trial times can be obtained by editing TRIALS or adding --verbose if needed.")

if __name__ == "__main__":
    main()
