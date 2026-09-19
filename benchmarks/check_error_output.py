import subprocess
from pathlib import Path

PULSE = ["python", "pulse.py"]
TEST_PROGRAM = Path("benchmarks/error_output_test.pul")

TEST_PROGRAM.write_text(
    """x = 10
y = 0
print(x / y)
""",
    encoding="utf-8"
)

print("\nPulse Error Output Validation")
print("=" * 35)

result = subprocess.run(
    PULSE + [str(TEST_PROGRAM)],
    capture_output=True,
    text=True
)

error_output = result.stderr.strip()

checks = {
    "Error type shown": "[Runtime Error]" in error_output,
    "Error description shown": "Division by zero" in error_output,
    "Source location shown": "<pulse>:3:9" in error_output,
    "Line number shown": "3 |" in error_output,
    "Source code shown": "print(x / y)" in error_output,
    "Error indicator shown": "^" in error_output,
}

for name, passed in checks.items():
    print(f"{name:<30}: {'YES' if passed else 'NO'}")

all_passed = all(checks.values())

print("\nNFR4 Result:", "PASS" if all_passed else "FAIL")

TEST_PROGRAM.unlink(missing_ok=True)
