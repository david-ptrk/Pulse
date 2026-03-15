# Parser Test Documentation

This document describes the test cases used to verify the functionality of the Pulse's Parser (`parser.py`).

## 1. Simple Expression / Assignment

Input:

```
x = 5
y = x + 3 * 2
z = y - 4 / 2
```

Output:

```
(= x 5)
(= y (+ x (* 3 2)))
(= z (- y (/ 4 2)))
```

## 2. If / Elif / Else

Input:

```
if x > 10:
    y = 1
elif x == 10:
    y = 2
else:
    y = 3
```

Output:

```
if (> x 10) then: (block (= y 1)) elif (== x 10) then: (block (= y 2)) else: (block (= y 3))
```

## 3. While Loop

Input:

```
i = 0
while i < 5:
    i = i + 1
```

Output:

```
(= i 0)
(while (< i 5) (block (= i (+ i 1))))
```

## 4. For Loop

Input:

```
for j in 0:
    x = x + j
```

Output:

```
(for j in 0 (block (= x (+ x j))))
```

## 5. Function Declaration & Call

Input:

```
def add(a, b):
    return a + b

result = add(5, 7)
```

Output:

```
(def add (a, b) (block (return (+ a b))))
(= result (call add 5 7))
```

## 6. Class Definition & Member Access

Input:

```
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

p = Point(1, 2)
px = p.x
```

Output:

```
(class Point (def __init__ (self, x, y) (block (= self.x x) (= self.y y))))
(= p (call Point 1 2))
(= px (. p x))
```

## 7. Chained Calls / Member Access

Input:

```
obj.method1().method2(5).value
```

Output:

```
(. (call (. (call (. obj method1)) method2) 5) value)
```

## 8. Try / Except / Finally

Input:

```
try:
    x = 1 / 0
except:
    x = 0
finally:
    print(x)
```

Output:

```
(try (block (= x (/ 1 0))) (except (block (= x 0))) (finally (block (call print x))))
```

## 9. Logical Operators

Input:

```
a = True
b = False
c = a and not b or b
```

Output:

```
(= a True)
(= b False)
(= c (or (and a (not b)) b))
```

## 10. Break / Continue

Input:

```
i = 0
while i < 10:
    i = i + 1
    if i == 5:
        break
    else:
        continue
```

Output:

```
(while (< i 10) (block (= i (+ i 1)) if (== i 5) then: (block break) else: (block continue)))
```
