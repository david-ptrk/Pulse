"""
py_helpers.py

Example Python backend functions, loaded from Pulse via
pybridge.load_file("examples/ai/py_helpers.py").
"""

def celsius_to_fahrenheit(c):
    return c * 9 / 5 + 32

def greet(name):
    return f"Hello from Python, {name}!"
