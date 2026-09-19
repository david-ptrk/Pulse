import subprocess
import time

TOTAL_RUNS = 1000
PROGRAM = "examples/hello_world.pul"

successful = 0
failed = 0
failures = []

start_time = time.time()

for i in range(1, TOTAL_RUNS + 1):
    result = subprocess.run(["python", "pulse.py", PROGRAM], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    
    if result.returncode == 0:
        successful += 1
    else:
        failed += 1
        failures.append((i, result.stderr.strip()))

elapsed = time.time() - start_time
success_rate = (successful / TOTAL_RUNS) * 100

print("\nPulse Reliability Test")
print("=" * 30)
print(f"Total executions : {TOTAL_RUNS}")
print(f"Successful       : {successful}")
print(f"Failed           : {failed}")
print(f"Success rate     : {success_rate:.2f}%")
print(f"Total test time   : {elapsed:.2f} seconds")

if failures:
    print("\nFailures:")
    for run, error in failures:
        print(f"Run {run}: {error}")

print("\nNFR2 Result:", "PASS" if success_rate >= 99 else "FAIL")