""""
datasets_module.py

Pulse standard library module for datasets. All datasets are lazy-loaded.
Provides:
- Built-in sklearn classic datasets (iris, wine, digits, breast_cancer, diabeters)
- Synthetic dataset generators (make_classification, make_regression, make_blobs, make_moons, make_circles)
- CSV file loading with auto-detection of separator, header, and missing values.
- A PulseDataset wrapper with manipulation methods.
"""

from __future__ import annotations
import os
from src.values import PulseModule, PulseNumber, PulseBoolean, PulseTensor, PulseNull, PulseString, PulseList, PulseDict, PulseDataset
from src.function import PulseNativeFunction, PulseNativeMethod
import numpy as np

# Helpers
def _is_numeric(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False

def _wrap(X, y, feature_names, target_names, description, interp) -> PulseDataset:
    ds = PulseDataset(X, y, feature_names, target_names, description)
    _attach_methods(ds, interp)
    return ds

# Dataset manipulation methods
def _dataset_split(ds: PulseDataset, interp):
    def split(ratio=None) -> PulseDict:
        r = 0.0
        if ratio is not None:
            if not isinstance(ratio, PulseNumber):
                interp._raise_type("split() ratio must be a number")
            r = float(ratio.value)
            if not (0.0 < r < 1.0):
                interp._raise_value("split() ratio must be between 0 and 1 exclusive")
        
        n = len(ds.X)
        split_idx = int(n * r)
        
        train_ds = _wrap(ds.X[:split_idx], ds.y[:split_idx] if ds.y is not None else None, ds.feature_names, ds.target_names, ds.description, interp)
        test_ds = _wrap(ds.X[split_idx:], ds.y[split_idx:] if ds.y is not None else None, ds.feature_names, ds.target_names, ds.description, interp)
        return PulseDict({
            PulseString("train"): train_ds,
            PulseString("test"): test_ds,
        })
    return PulseNativeMethod(split, arity=1)

def _dataset_shuffle(ds: PulseDataset, interp):
    def shuffle(seed=None) -> PulseDataset:
        s = int(seed.value) if isinstance(seed, PulseNumber) else None
        rng = np.random.default_rng(s)
        idx = rng.permutation(len(ds.X))
        
        return _wrap(ds.X[idx], ds.y[idx] if ds.y is not None else None, ds.feature_names, ds.target_names, ds.description, interp)
    return PulseNativeMethod(shuffle, arity=-1)

def _dataset_normalize(ds: PulseDataset, interp):
    def normalize(method=None) -> PulseDataset:
        m = "standard"
        if method is not None:
            if not isinstance(method, PulseString):
                interp._raise_type("normalize() method must be a string")
            m = method.value
            if m not in ("standard", "minmax"):
                interp._raise_value("normalize() method must be 'standard' or 'minmax'")
        
        X = ds.X.copy()
        if m == "standard":
            std = X.std(axis=0)
            std = np.where(std == 0, 1.0, std)
            X = (X - X.mean(axis=0)) / std
        else:
            lo = X.min(axis=0)
            rng = X.max(axis=0) - lo
            rng = np.where(rng == 0, 1.0, rng)
            X = (X - lo) / rng
        
        return _wrap(X, ds.y, ds.feature_names, ds.target_names, ds.description, interp)
    return PulseNativeMethod(normalize, arity=-1)

def _dataset_head(ds: PulseDataset, interp):
    def head(n=None) -> PulseDataset:
        k = max(1, int(n.value)) if isinstance(n, PulseNumber) else 5
        return _wrap(ds.X[:k], ds.y[:k] if ds.y is not None else None, ds.feature_names, ds.target_names, ds.description, interp)
    return PulseNativeMethod(head, arity=-1)

def _dataset_describe(ds: PulseDataset, interp):
    def describe() -> PulseDict:
        X = ds.X if ds.X.ndim > 1 else ds.X.reshape(-1, 1)
        rows = X.shape[0]
        cols = X.shape[1]
        
        print(f"\n[Pulse] Dataset — {ds.description or 'no description'}")
        print(f"  Samples  : {rows}")
        print(f"  Features : {cols}")
        print(f"  Labels   : {'yes' if ds.y is not None else 'no'}")
        if ds.target_names:
            print(f"  Classes  : {ds.target_names}")
        print()
        print(f"  {'Feature':<24}  {'Min':>9}  {'Max':>9}  {'Mean':>9}  {'Std':>9}  {'NaN':>5}")
        print(f"  {'─'*24}  {'─'*9}  {'─'*9}  {'─'*9}  {'─'*9}  {'─'*5}")
        
        feature_stats = []
        for i, name in enumerate(ds.feature_names):
            col = X[:, i]
            missing = int(np.isnan(col).sum())
            valid = col[~np.isnan(col)]
            mn = float(valid.min()) if len(valid) else float("nan")
            mx = float(valid.max()) if len(valid) else float("nan")
            avg = float(valid.mean()) if len(valid) else float("nan")
            std = float(valid.std()) if len(valid) else float("nan")
            print(f"  {name:<24}  {mn:>9.4f}  {mx:>9.4f}  {avg:>9.4f}  {std:>9.4f}  {missing:>5}")
            
            feature_stats.append(PulseDict({
                PulseString("name"): PulseString(name),
                PulseString("min"): PulseNumber(mn if not np.isnan(mn) else 0.0),
                PulseString("max"): PulseNumber(mx if not np.isnan(mx) else 0.0),
                PulseString("mean"): PulseNumber(avg if not np.isnan(avg) else 0.0),
                PulseString("std"): PulseNumber(std if not np.isnan(std) else 0.0),
                PulseString("missing"): PulseNumber(float(missing)),
            }))
        print()
        
        return PulseDict({
            PulseString("n_samples"): PulseNumber(float(rows)),
            PulseString("n_features"): PulseNumber(float(cols)),
            PulseString("has_labels"): PulseBoolean(ds.y is not None),
            PulseString("features"): PulseList(feature_stats),
        })
    return PulseNativeMethod(describe, arity=0)

def _dataset_features(ds: PulseDataset, interp):
    def features() -> PulseTensor:
        return PulseTensor(ds.X.copy())
    return PulseNativeMethod(features, arity=0)

def _dataset_labels(ds: PulseDataset, interp):
    def labels() -> "PulseTensor | PulseNull":
        return PulseTensor(ds.y.copy()) if ds.y is not None else PulseNull()
    return PulseNativeMethod(labels, arity=0)

def _dataset_feature_names(ds: PulseDataset, interp):
    def feature_names() -> PulseList:
        return PulseList([PulseString(n) for n in ds.feature_names])
    return PulseNativeMethod(feature_names, arity=0)

def _dataset_target_names(ds: PulseDataset, interp):
    def target_names() -> PulseList:
        return PulseList([PulseString(n) for n in ds.target_names])
    return PulseNativeMethod(target_names, arity=0)

def _attach_methods(ds: PulseDataset, interp) -> None:
    ds.methods = {
        "split": _dataset_split(ds, interp),
        "shuffle": _dataset_shuffle(ds, interp),
        "normalize": _dataset_normalize(ds, interp),
        "head": _dataset_head(ds, interp),
        "describe": _dataset_describe(ds, interp),
        "features": _dataset_features(ds, interp),
        "labels": _dataset_labels(ds, interp),
        "feature_names": _dataset_feature_names(ds, interp),
        "target_names": _dataset_target_names(ds, interp),
    }

# sklearn classic loaders
def _load_iris(interp):
    def iris() -> PulseDataset:
        from sklearn.datasets import load_iris as _load
        d = _load()
        return _wrap(d.data, d.target, list(d.feature_names), list(d.target_names), "Iris — 150 samples, 4 features, 3 classes (classification)", interp)
    return PulseNativeFunction("iris", iris)

def _load_wine(interp):
    def wine() -> PulseDataset:
        from sklearn.datasets import load_wine as _load
        d = _load()
        return _wrap(d.data, d.target, list(d.feature_names), list(d.target_names), "Wine — 178 samples, 13 features, 3 classes (classification)", interp)
    return PulseNativeFunction("wine", wine)

def _load_digits(interp):
    def digits() -> PulseDataset:
        from sklearn.datasets import load_digits as _load
        d = _load()
        return _wrap(d.data, d.target, [f"pixel_{i}" for i in range(d.data.shape[1])], [str(c) for c in d.target_names], "Digits - 1797 samples, 64 pixel features, 10 classes (classification)", interp)
    return PulseNativeFunction("digits", digits)

def _load_breast_cancer(interp):
    def breast_cancer() -> PulseDataset:
        from sklearn.datasets import load_breast_cancer as _load
        d = _load()
        return _wrap(d.data, d.target, list(d.feature_names), list(d.target_names), "Breast cancer — 569 samples, 30 features, 2 classes (classification)", interp)
    return PulseNativeFunction("breast_cancer", breast_cancer)

def _load_diabetes(interp):
    def diabetes() -> PulseDataset:
        from sklearn.datasets import load_diabetes as _load
        d = _load()
        return _wrap(d.data, d.target, list(d.feature_names), [], "Diabetes - 442 samples, 10 features, continuous target (regression)", interp)
    return PulseNativeFunction("diabetes", diabetes)

# Synthetic generators
def _make_classification(interp):
    def make_classification(n_samples=None, n_features=None, n_classes=None, n_informative=None, seed=None) -> PulseDataset:
        from sklearn.datasets import make_classification as _make
        n = int(n_samples.value) if isinstance(n_samples, PulseNumber) else 200
        nf = int(n_features.value) if isinstance(n_features, PulseNumber) else 10
        nc = int(n_classes.value) if isinstance(n_classes, PulseNumber) else 2
        ni = int(n_informative.value) if isinstance(n_informative, PulseNumber) else min(4, nf)
        rs = int(seed.value) if isinstance(seed, PulseNumber) else None
        if ni > nf:
            interp._raise_value("make_classification() n_informative cannot exceed n_features")
        if nc < 2:
            interp._raise_value("make_classification() n_classes must be >= 2")
        X, y = _make(n_samples=n, n_features=nf, n_informative=ni, n_classes=nc, random_state=rs)
        return _wrap(X, y, [f"feature_{i}" for i in range(nf)], [str(c) for c in range(nc)], f"Synthetic classification - {n} samples, {nf} features, {nc} classes", interp)
    return PulseNativeFunction("make_classification", make_classification)

def _make_regression(interp):
    def make_regression(n_samples=None, n_features=None, noise=None, seed=None) -> PulseDataset:
        from sklearn.datasets import make_regression as _make
        n = int(n_samples.value) if isinstance(n_samples, PulseNumber) else 200
        nf = int(n_features.value) if isinstance(n_features, PulseNumber) else 5
        ns = float(noise.value) if isinstance(noise, PulseNumber) else 0.1
        rs = int(seed.value) if isinstance(seed, PulseNumber) else None
        X, y = _make(n_samples=n, n_features=nf, noise=ns, random_state=rs)
        return _wrap(X, y, [f"feature_{i}" for i in range(nf)], [], f"Synthetic regression - {n} samples, {nf} features, noise={ns}", interp)
    return PulseNativeFunction("make_regression", make_regression)

def _make_blobs(interp):
    def make_blobs(n_samples=None, n_features=None, centers=None, seed=None) -> PulseDataset:
        from sklearn.datasets import make_blobs as _make
        n = int(n_samples.value) if isinstance(n_samples, PulseNumber) else 200
        nf = int(n_features.value) if isinstance(n_features, PulseNumber) else 2
        nc = int(centers.value) if isinstance(centers, PulseNumber) else 3
        rs = int(seed.value) if isinstance(seed, PulseNumber) else None
        X, y = _make(n_samples=n, n_features=nf, centers=nc, random_state=rs)
        return _wrap(X, y, [f"feature_{i}" for i in range(nf)], [str(c) for c in range(nc)], f"Synthetic blobs - {n} samples, {nf} features, {nc} clusters", interp)
    return PulseNativeFunction("make_blobs", make_blobs)

def _make_moons(interp):
    def make_moons(n_samples=None, noise=None, seed=None) -> PulseDataset:
        from sklearn.datasets import make_moons as _make
        n = int(n_samples.value) if isinstance(n_samples, PulseNumber) else 200
        ns = float(noise.value) if isinstance(noise, PulseNumber) else 0.1
        rs = int(seed.value) if isinstance(seed, PulseNumber) else None
        X, y = _make(n_samples=n, noise=ns, random_state=rs)
        return _wrap(X, y, ["x", "y"], ["0", "1"], f"Synthetic moons - {n} samples, 2 features, 2 classes", interp)
    return PulseNativeFunction("make_moons", make_moons)

def _make_circles(interp):
    def make_circles(n_samples=None, noise=None, seed=None) -> PulseDataset:
        from sklearn.datasets import make_circles as _make
        n = int(n_samples.value) if isinstance(n_samples, PulseNumber) else 200
        ns = float(noise.value) if isinstance(noise, PulseNumber) else 0.05
        rs = int(seed.value) if isinstance(seed, PulseNumber) else None
        X, y = _make(n_samples=n, noise=ns, random_state=rs)
        return _wrap(X, y, ["x", "y"], ["inner", "outer"], f"Synthetic circles - {n} samples, 2 features, 2 classes", interp)
    return PulseNativeFunction("make_circles", make_circles)

# CSV loader
def _load_csv(interp):
    def load_csv(path_arg, label_col=None, sep_arg=None, has_header=None) -> PulseDataset:
        """
        Load a CSV file into a PulseDataset.
        
        path       : string - path to the CSV file
        label_col  : number | string - column index or name to use as labels (optional)
        sep        : string - delimiter e.g., "," or "\\t" (auto-detected if omitted)
        has_header : bool - whether the first row is a header (auto-detected it omitted)
        """
        if not isinstance(path_arg, PulseString):
            interp._raise_type("load_csv() path must be a string")
        
        path = path_arg.value
        if not os.path.isfile(path):
            interp._raise(f"load_csv() file not found: '{path}'")
        
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                raw = fh.read()
        except OSError as e:
            interp._raise(f"load_csv() could not read file: {e}")
        
        lines = [l for l in raw.splitlines() if l.strip()]
        if not lines:
            interp._raise(f"load_csv() file is empty: '{path}'")
        
        # auto-detect separator
        if isinstance(sep_arg, PulseString):
            sep = sep_arg.value
        else:
            counts = {d: lines[0].count(d) for d in (",", "\t", ";", "|")}
            sep = max(counts, key=counts.get)
            if counts[sep] == 0:
                sep = ","
        
        # auto-detect header
        if isinstance(has_header, PulseBoolean):
            use_header = has_header.value
        else:
            first_cells = lines[0].split(sep)
            use_header = sum(1 for c in first_cells if not _is_numeric(c.strip())) > 0
        
        header_names: list[str] = []
        data_lines = lines
        
        if use_header:
            header_names = [c.strip().strip('"').strip("'") for c in lines[0].split(sep)]
            data_lines = lines[1:]
        
        if not data_lines:
            interp._raise(f"load_csv() has a header but no data rows: '{path}'")
        
        # parse rows
        n_cols = len(lines[0].split(sep))
        rows: list[list[float]] = []
        
        _MISSING = {"", "NA", "na", "N/A", "n/a", "nan", "NaN", "NULL", "null", "?"}
        
        for line in data_lines:
            cells = line.split(sep)
            if len(cells) < n_cols:
                cells += [""] * (n_cols - len(cells))
            row = []
            for c in cells[:n_cols]:
                c = c.strip().strip('"').strip("'")
                row.append(float("nan") if (c in _MISSING or not _is_numeric(c)) else float(c))
            rows.append(row)
        
        if not rows:
            interp._raise(f"load_csv() no valid data rows in: '{path}'")
        
        matrix = np.array(rows, dtype=float)
        col_names = header_names if use_header else [f"col_{i}" for i in range(n_cols)]
        
        # resolve label column
        label_idx: int | None = None
        if label_col is not None:
            if isinstance(label_col, PulseNumber):
                label_idx = int(label_col.value)
                if not (0 <= label_idx < matrix.shape[1]):
                    interp._raise_index(
                        f"load_csv() label_col {label_idx} out of range "
                        f"(file has {matrix.shape[1]} columns)"
                    )
            elif isinstance(label_col, PulseString):
                name = label_col.value
                if name not in col_names:
                    interp._raise_key(f"load_csv() label column '{name}' not found in header")
                label_idx = col_names.index(name)
            else:
                interp._raise_type("load_csv() label_col must be a number or string")
        
        if label_idx is not None:
            y = matrix[:, label_idx]
            X = np.delete(matrix, label_idx, axis=1)
            feat_names = [col_names[i] for i in range(len(col_names)) if i != label_idx]
        else:
            y = None
            X = matrix
            feat_names = col_names
        
        desc = (
            f"CSV '{os.path.basename(path)}' — {X.shape[0]} samples, {X.shape[1]} features"
            + (f", label='{col_names[label_idx]}'" if label_idx is not None else "")
        )
        return _wrap(X, y, feat_names, [], desc, interp)
    
    return PulseNativeFunction("load_csv", load_csv)

# Module Factory
def make(interp) -> PulseModule:
    return PulseModule("datasets", {
        "iris": _load_iris(interp),
        "wine": _load_wine(interp),
        "digits": _load_digits(interp),
        "breast_cancer": _load_breast_cancer(interp),
        "diabetes": _load_diabetes(interp),
        "make_classification": _make_classification(interp),
        "make_regression": _make_regression(interp),
        "make_blobs": _make_blobs(interp),
        "make_moons": _make_moons(interp),
        "make_circles": _make_circles(interp),
        "load_csv": _load_csv(interp),
    })