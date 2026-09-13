import numpy as np

def build_matrix(n):
    rows = []
    for i in range(n):
        row = []
        for j in range(n):
            row.append((i + j) % 7)
        rows.append(row)
    return rows

n = 80
a = np.array(build_matrix(n), dtype=float)
b = np.array(build_matrix(n), dtype=float)

for k in range(20):
    c = a @ b

print(c.shape)