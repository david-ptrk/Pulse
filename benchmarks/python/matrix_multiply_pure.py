def build_matrix(n):
    rows = []
    for i in range(n):
        row = []
        for j in range(n):
            row.append((i + j) % 7)
        rows.append(row)
    return rows

def matmul(a, b, n):
    result = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            total = 0
            for k in range(n):
                total += a[i][k] * b[k][j]
            result[i][j] = total
    return result

n = 80
a = build_matrix(n)
b = build_matrix(n)

for k in range(20):
    c = matmul(a, b, n)

print(len(c), len(c[0]))