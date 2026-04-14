"""
values.py

Defines the runtime value types for the Pulse programming language.
Each class wraps a native Python value and provides Pulse-specific
behavior such as type naming, truthiness, and string representation.
"""

from typing import Any, List, Dict

class PulseValue:
    def type_name(self) -> str:
        return "object"
    
    def is_truthy(self) -> bool:
        return True
    
    def __repr__(self) -> str:
        return "<value>"

class PulseNumber(PulseValue):
    def __init__(self, value: int | float) -> None:
        self.value = value
    
    def type_name(self) -> str:
        return "number"
    
    def __repr__(self) -> str:
        if isinstance(self.value, float) and self.value.is_integer():
            return str(int(self.value))
        return str(self.value)

class PulseString(PulseValue):
    def __init__(self, value: str) -> None:
        self.value = value
    
    def type_name(self) -> str:
        return "string"
    
    def is_truthy(self) -> bool:
        return len(self.value) > 0
    
    def __repr__(self) -> str:
        return self.value

class PulseBoolean(PulseValue):
    def __init__(self, value: bool) -> None:
        self.value = value
    
    def type_name(self) -> str:
        return "boolean"
    
    def is_truthy(self) -> bool:
        return self.value
    
    def __repr__(self) -> str:
        return "true" if self.value else "false"

class PulseNull(PulseValue):
    def type_name(self) -> str:
        return "null"
    
    def is_truthy(self) -> bool:
        return False
    
    def __repr__(self) -> str:
        return "null"

class PulseList(PulseValue):
    def __init__(self, elements: List[PulseValue]) -> None:
        self.elements = elements
    
    def type_name(self) -> str:
        return "list"
    
    def is_truthy(self) -> bool:
        return len(self.elements) > 0
    
    def __repr__(self) -> str:
        inner = ", ".join(repr(el) for el in self.elements)
        return f"[{inner}]"

class PulseDict(PulseValue):
    def __init__(self, entries: Dict[PulseValue, PulseValue]) -> None:
        self.entries = entries
    
    def type_name(self) -> str:
        return "dict"
    
    def is_truthy(self) -> bool:
        return len(self.entries) > 0
    
    def get(self, key: PulseValue) -> PulseValue:
        raw_key = self._to_raw(key)
        for k, v in self.entries.items():
            if self._to_raw(k) == raw_key:
                return v
        return PulseNull()
    
    def set(self, key: PulseValue, value: PulseValue) -> None:
        raw_key = self._to_raw(key)
        for k in list(self.entries):
            if self._to_raw(k) == raw_key:
                self.entries[k] = value
                return
        self.entries[key] = value
    
    def has(self, key: PulseValue) -> bool:
        raw_key = self._to_raw(key)
        return any(self._to_raw(k) == raw_key for k in self.entries)
    
    @staticmethod
    def _to_raw(key: PulseValue) -> Any:
        if isinstance(key, (PulseString, PulseNumber, PulseBoolean)):
            return key.value
        if isinstance(key, PulseNull):
            return None
        raise TypeError(f"Unhashable dict key type: {key.type_name()}")
    
    def __repr__(self) -> str:
        pairs = ", ".join(
            f"{repr(k)}: {repr(v)}" for k, v in self.entries.items()
        )
        return "{" + pairs + "}"

class PulseRange(PulseValue):
    def __init__(self, start: int, stop: int, step: int = 1) -> None:
        if step == 0:
            raise ValueError("Range step cannot be zero")
        self.start = start
        self.stop = stop
        self.step = step
    
    def type_name(self) -> str:
        return "range"
    
    def is_truthy(self) -> bool:
        return len(self) > 0
    
    def to_list(self) -> list:
        return [PulseNumber(i) for i in range(self.start, self.stop, self.step)]
    
    def __len__(self) -> int:
        if self.step > 0:
            return max(0, (self.stop - self.start + self.step - 1) // self.step)
        return max(0, (self.start - self.stop - self.step - 1) // -self.step)
    
    def __repr__(self) -> str:
        if self.step == 1:
            return f"range({self.start, self.stop})"
        return f"range({self.start}, {self.stop}, {self.step})"