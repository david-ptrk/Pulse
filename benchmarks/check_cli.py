import subprocess
from pathlib import Path

PULSE = ["python", "pulse.py"]
TEST_PROGRAM = Path("benchmarks/cli_test.pul")

def run_cli(*args):
    return subprocess.run(
        PULSE + list(args),
        capture_output=True,
        text=True
    )

TEST_PROGRAM.write_text(
    """x = 10
y = 20
print(x + y)
""",
    encoding="utf-8"
)

print("\nPulse CLI Validation")
print("=" * 30)

# 1. Help command
help_result = run_cli("--help")
help_output = (help_result.stdout + help_result.stderr).lower()

help_pass = (
    help_result.returncode == 0
    and ("usage" in help_output or "help" in help_output)
)

# 2. Normal program execution
run_result = run_cli(str(TEST_PROGRAM))

execution_pass = (
    run_result.returncode == 0
    and "30" in run_result.stdout
)

# 3. Missing file handling
missing_result = run_cli("benchmarks/file_that_does_not_exist.pul")
missing_output = (
    missing_result.stdout + missing_result.stderr
).lower()

missing_pass = (
    missing_result.returncode != 0
    and any(word in missing_output for word in [
        "error",
        "not found",
        "no such file",
        "cannot"
    ])
)

# 4. Invalid option handling
invalid_result = run_cli("--invalid-option")
invalid_output = (
    invalid_result.stdout + invalid_result.stderr
).lower()

invalid_pass = (
    invalid_result.returncode != 0
    and any(word in invalid_output for word in [
        "error",
        "unknown",
        "invalid",
        "unrecognized",
        "usage"
    ])
)

checks = {
    "Help command works": help_pass,
    "Program execution works": execution_pass,
    "Missing file handled": missing_pass,
    "Invalid option handled": invalid_pass,
}

for name, passed in checks.items():
    print(f"{name:<30}: {'YES' if passed else 'NO'}")

all_passed = all(checks.values())

print("\nNFR5 Result:", "PASS" if all_passed else "FAIL")

TEST_PROGRAM.unlink(missing_ok=True)
