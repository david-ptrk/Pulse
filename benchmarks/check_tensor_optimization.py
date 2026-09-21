import subprocess
import time
import sys

PULSE_PROGRAM = "benchmarks/pulse/matrix_multiply_tensor.pul"

print("Pulse Tensor Optimization Test")
print("==============================")

start = time.perf_counter()

result = subprocess.run(
    [sys.executable, "pulse.py", PULSE_PROGRAM],
    capture_output=True,
    text=True
)

elapsed = time.perf_counter() - start

output = result.stdout + result.stderr

successful = result.returncode == 0
correct_shape = "[80, 80]" in output

print(f"Execution successful : {'YES' if successful else 'NO'}")
print(f"Result shape correct : {'YES' if correct_shape else 'NO'}")
print(f"Execution time       : {elapsed:.3f} sec")

if successful and correct_shape:
    print("Tensor operation executed successfully.")
    print("NFR10 Result: REVIEW")
    print("Tensor multiplication is delegated to NumPy's optimized backend,")
    print("but end-to-end performance is slower than equivalent Python/NumPy.")
else:
    print("NFR10 Result: FAIL")
