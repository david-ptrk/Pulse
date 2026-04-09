"""
values.py
"""

class PulseValue:
    def type_name(self):
        return "object"
    
    def is_truthy(self):
        return True
    
    def __repr__(self):
        return "<value>"

class PulseNumber(PulseValue):
    def __init__(self, value):
        self.value = value
    
    def type_name(self):
        return "number"
    
    def __repr__(self):
        return str(self.value)

class PulseString(PulseValue):
    def __init__(self, value):
        self.value = value
    
    def type_name(self):
        return "string"
    
    def __repr__(self):
        return self.value

class PulseList(PulseValue):
    def __init__(self, elements):
        self.elements = elements
    
    def type_name(self):
        return "list"
    
    def __repr__(self):
        return str(self.elements)

class PulseNull(PulseValue):
    def type_name(self):
        return "null"
    
    def is_truthy(self):
        return False
    
    def __repr__(self):
        return "null"

class PulseBoolean(PulseValue):
    def __init__(self, value):
        self.value = value
    
    def type_name(self):
        return "boolean"
    
    def is_truthy(self):
        return self.value
    
    def __repr__(self):
        return "true" if self.value else "false"