import subprocess
from pathlib import Path

PULSE = ["python", "pulse.py"]

VALID_PROGRAM = Path("benchmarks/syntax_valid_test.pul")
INVALID_PROGRAM = Path("benchmarks/syntax_invalid_test.pul")

VALID_PROGRAM.write_text(
    """x = 10
y = 20
if x < y:
    print("valid")
""",
    encoding="utf-8"
)

INVALID_PROGRAM.write_text(
    """x = 10
if x < 20
    print("invalid")
""",
    encoding="utf-8"
)

print("\nPulse Syntax Consistency Test")
print("=" * 35)

# Run valid syntax multiple times
valid_results = []

for _ in range(10):
    result = subprocess.run(
        PULSE + [str(VALID_PROGRAM)],
        capture_output=True,
        text=True
    )
    valid_results.append(result)

valid_pass = all(
    result.returncode == 0 and "valid" in result.stdout
    for result in valid_results
)

# Run invalid syntax multiple times
invalid_results = []

for _ in range(10):
    result = subprocess.run(
        PULSE + [str(INVALID_PROGRAM)],
        capture_output=True,
        text=True
    )
    invalid_results.append(result)

invalid_pass = all(
    result.returncode != 0
    for result in invalid_results
)

print(
    f"Valid syntax accepted consistently : "
    f"{'YES' if valid_pass else 'NO'}"
)

print(
    f"Invalid syntax rejected consistently : "
    f"{'YES' if invalid_pass else 'NO'}"
)

print(f"Valid executions tested           : {len(valid_results)}")
print(f"Invalid executions tested         : {len(invalid_results)}")

all_passed = valid_pass and invalid_pass

print("\nNFR6 Result:", "PASS" if all_passed else "FAIL")

VALID_PROGRAM.unlink(missing_ok=True)
INVALID_PROGRAM.unlink(missing_ok=True)