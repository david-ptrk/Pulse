import subprocess
from pathlib import Path

PULSE = ["python", "pulse.py"]

USER_GUIDE = Path("spec/Pulse_Language_User_Guide.pdf")
EXAMPLES_DIR = Path("examples")

print("\nPulse Documentation & Sample Validation")
print("=" * 40)

# 1. Check user guide
user_guide_exists = (
    USER_GUIDE.exists()
    and USER_GUIDE.is_file()
    and USER_GUIDE.stat().st_size > 0
)

# 2. Find sample programs
sample_programs = sorted(EXAMPLES_DIR.glob("*.pul"))
samples_exist = len(sample_programs) > 0

print(
    f"User guide available       : "
    f"{'YES' if user_guide_exists else 'NO'}"
)

print(
    f"Sample programs available  : "
    f"{'YES' if samples_exist else 'NO'}"
)

print(f"Sample programs found      : {len(sample_programs)}")

# 3. Execute every sample program
successful = 0
failed = 0
failures = []

for program in sample_programs:
    result = subprocess.run(
        PULSE + [str(program)],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        successful += 1
    else:
        failed += 1
        failures.append(
            (program.name, result.stderr.strip())
        )

execution_pass = (
    samples_exist
    and failed == 0
)

print(f"Successful samples        : {successful}")
print(f"Failed samples            : {failed}")

if failures:
    print("\nFailed sample programs:")
    for name, error in failures:
        print(f"\n{name}")
        print(error)

all_passed = (
    user_guide_exists
    and samples_exist
    and execution_pass
)

print(
    "\nNFR7 Result:",
    "PASS" if all_passed else "FAIL"
)
