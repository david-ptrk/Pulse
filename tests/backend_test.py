from src.backend_stub import (
    tensor_from_list,
    dot,
    tensor_add,
    shape,
)

def run_tests():
    print("TEST 1: tensor_from_list")
    t = tensor_from_list([1, 2, 3])
    print(t)
    
    print("\nTEST 2: dot")
    print(dot([1, 2], [3, 4]))
    
    print("\nTEST 3: tensor_add")
    print(tensor_add([1, 2], [3, 4]))
    
    print("\nTEST 4: shape")
    print(shape([[1, 2, 3], [4, 5, 6]]))

if __name__ == "__main__":
    run_tests()