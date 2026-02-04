import numpy as np

def tensor_from_list(lst):
    return np.array(lst)

def dot(a, b):
    return np.dot(a, b)

def tensor_add(a, b):
    return np.add(a, b)

def shape(a):
    arr = np.array(a)
    return arr.shape