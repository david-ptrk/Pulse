import subprocess
import hashlib
from pathlib import Path

PULSE = ["python", "pulse.py"]

TEST_PROGRAM = Path("benchmarks/runtime_error_test.pul")
NORMAL_PROGRAM = Path("examples/hello_world.pul")

def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

TEST_PROGRAM.write_text(
    """x = 10
y = 0
print(x / y)
""",
    encoding="utf-8"
)

original_hash = file_hash(TEST_PROGRAM)

print("\nPulse Runtime Error Recovery Test")
print("=" * 35)

# 1. Run the program containing a runtime error
error_result = subprocess.run(
    PULSE + [str(TEST_PROGRAM)],
    capture_output=True,
    text=True
)

# 2. Check that the source file was not modified
unchanged = file_hash(TEST_PROGRAM) == original_hash

# 3. Check that an error was reported
error_reported = error_result.returncode != 0 and bool(error_result.stderr.strip())

# 4. Run a normal program afterward
normal_result = subprocess.run(
    PULSE + [str(NORMAL_PROGRAM)],
    capture_output=True,
    text=True
)

recovered = normal_result.returncode == 0

print(f"Runtime error detected : {'YES' if error_reported else 'NO'}")
print(f"Source file unchanged  : {'YES' if unchanged else 'NO'}")
print(f"Interpreter recovered  : {'YES' if recovered else 'NO'}")

if error_result.stderr.strip():
    print("\nRuntime error output:")
    print(error_result.stderr.strip())

print("\nNFR3 Result:",
    "PASS" if error_reported and unchanged and recovered else "FAIL")

# Clean up temporary test program
TEST_PROGRAM.unlink(missing_ok=True)
