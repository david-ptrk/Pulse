import subprocess
import sys
import time
from pathlib import Path

PULSE = ["python", "pulse.py"]

TEST_PROGRAM = Path("benchmarks/memory_test.pul")
PYTHON_PROGRAM = Path("benchmarks/memory_test.py")

TEST_PROGRAM.write_text(
    """values = []
for i in range(100000):
    values = values + [i]

print(len(values))
""",
    encoding="utf-8"
)

PYTHON_PROGRAM.write_text(
    """values = []
for i in range(100000):
    values.append(i)

print(len(values))
""",
    encoding="utf-8"
)

def get_peak_memory(command):
    """Run a command through /usr/bin/time and return peek RSS in KB."""
    result = subprocess.run(
        [
            "/usr/bin/time",
            "-f",
            "%M",
            *command
        ],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("Program failed:")
        print(result.stderr)
        return None
    
    # /usr/bin/time writes %M to stderr.
    lines = result.stderr.strip().splitlines()
    
    for line in reversed(lines):
        line = line.strip()
        if line.isdigit():
            return int(line)
    
    return None

print("\nPulse Memory Usage Test")
print("=" * 30)

pulse_memory = get_peak_memory(
    PULSE + [str(TEST_PROGRAM)]
)

python_memory = get_peak_memory(
    [sys.executable, str(PYTHON_PROGRAM)]
)

if pulse_memory is not None:
    print(f"Pulse peak memory   : {pulse_memory:,} KB")
else:
    print("Pulse peak memory   : FAILED")

if python_memory is not None:
    print(f"Python peak memory  : {python_memory:,} KB")
else:
    print("Python peak memory  : FAILED")

if pulse_memory is not None and python_memory is not None:
    ratio = pulse_memory / python_memory
    
    print(f"Memory ratio        : {ratio:.2f}x")
    
    # This is a measurement rather than an arbitrary pass/fail threshold.
    # NFR9 should be evaluated using the observed memory overhead.
    if ratio <= 1.5:
        print("NFR9 Result: PASS")
        print("Pulse memory usage is within 50% of equivalent Python.")
    else:
        print("NFR9 Result: REVIEW")
        print("Pulse uses substantially more memory than equivalent Python.")

TEST_PROGRAM.unlink(missing_ok=True)
PYTHON_PROGRAM.unlink(missing_ok=True)
