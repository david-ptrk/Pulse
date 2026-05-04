"""
preprocess_module.py

Pulse standard library module for data preprocessing utilities.
Provides tensor transformations commonly needed before model training
such as normalization, standardization, splitting, and encoding.
"""

from __future__ import annotations
from src.values import PulseModule, PulseTensor, PulseList, PulseNumber, PulseNull
from src.function import PulseNativeFunction
import numpy as np

def make(interp) -> PulseModule:
    """Build and return the Pulse 'preprocess' module."""
    
    def _check_tensor(val, fn_name: str, arg_name: str = "data"):
        """Raise if val is not a PulseTensor."""
        if not isinstance(val, PulseTensor):
            interp._raise(f"{fn_name}() expects a tensor for {arg_name}, got '{val.type_name()}'")
    
    def _normalize(data: PulseTensor) -> PulseTensor:
        """Normalize each column to unit length using L2 norm."""
        _check_tensor(data, "normalize")
        arr = data.array
        norm = np.linalg.norm(arr, axis=0, keepdims=True)
        norm = np.where(norm == 0, 1, norm)
        return PulseTensor(arr / norm)
    
    def _standardize(data: PulseTensor) -> PulseTensor:
        """Standardize each column to zero mean and unit variance."""
        _check_tensor(data, "standardize")
        arr = data.array
        mean = arr.mean(axis=0)
        std = arr.std(axis=0)
        std = np.where(std == 0, 1, std)
        return PulseTensor((arr - mean) / std)
    
    def _min_max_scale(data: PulseTensor) -> PulseTensor:
        """Scale each column to the range [0, 1] using min-max scaling."""
        _check_tensor(data, "min_max_scale")
        arr = data.array
        mn = arr.min(axis=0)
        mx = arr.max(axis=0)
        rng = np.where((mx - mn) == 0, 1, mx - mn)
        return PulseTensor((arr - mn) / rng)
    
    def _train_test_split(data: PulseTensor, labels: PulseTensor, test_size: PulseNumber) -> PulseList:
        """Split data and labels into train/test sets. Returns [X_train, X_test, y_train, y_test]."""
        _check_tensor(data, "train_test_split", "data")
        _check_tensor(labels, "train_test_split", "labels")
        if not isinstance(test_size, PulseNumber):
            interp._raise(f"train_test_split() expects a number for test_size, got '{test_size.type_name()}'")
        
        from sklearn.model_selection import train_test_split
        try:
            X_train, X_test, y_train, y_test = train_test_split(
                data.array, labels.array, test_size=test_size.value, random_state=42
            )
            return PulseList([PulseTensor(X_train), PulseTensor(X_test), PulseTensor(y_train), PulseTensor(y_test)])
        except Exception as e:
            interp._raise(f"train_test_split() failed: {e}")
    
    def _shuffle(data: PulseTensor) -> PulseTensor:
        """Randomly shuffle the rows of a tensor."""
        _check_tensor(data, "shuffle")
        arr = data.array.copy()
        np.random.shuffle(arr)
        return PulseTensor(arr)
    
    def _flatten_data(data: PulseTensor) -> PulseTensor:
        """Flatten each sample in a tensor to a 1D vector. Shape (n, ...) becomes (n, m)."""
        _check_tensor(data, "flatten_data")
        arr = data.array
        if arr.ndim == 1:
            return PulseTensor(arr)
        return PulseTensor(arr.reshape(arr.shape[0], -1))
    
    def _one_hot_encode(labels: PulseTensor) -> PulseTensor:
        """Convert integer class labels to a one-hot encoded tensor."""
        _check_tensor(labels, "one_hot_encode", "labels")
        arr = labels.array.astype(int)
        n_classes = int(arr.max()) + 1
        one_hot = np.zeros((len(arr), n_classes))
        one_hot[np.arange(len(arr)), arr] = 1
        return PulseTensor(one_hot)
    
    return PulseModule("preprocess", {
        "normalize": PulseNativeFunction("normalize", _normalize),
        "standardize": PulseNativeFunction("standardize", _standardize),
        "min_max_scale": PulseNativeFunction("min_max_scale", _min_max_scale),
        "train_test_split": PulseNativeFunction("train_test_split", _train_test_split),
        "shuffle": PulseNativeFunction("shuffle", _shuffle),
        "flatten_data": PulseNativeFunction("flatten_data", _flatten_data),
        "one_hot_encode": PulseNativeFunction("one_hot_encode", _one_hot_encode),
    })