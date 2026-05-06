"""
model_module.py

Pulse standard library module for machine learning models.
Wraps scikit-learn classifiers and regressors behind a unified
Pulse interface with optional auto-preprocessing and model selection.
"""

from __future__ import annotations
from src.values import PulseModule, PulseModel, PulseNumber, PulseBoolean, PulseTensor, PulseNull, PulseNamespace, PulseString, PulseDict, PulseList
from src.function import PulseNativeFunction, PulseNativeMethod
import numpy as np
from sklearn.linear_model import LinearRegression, LogisticRegression, Ridge
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.cluster import KMeans
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import cross_val_score
import warnings
import sys

# Explain helpers
def _weight_label(value: float) -> str:
    """Human-readable magnitude + direction label for a single weight."""
    abs_v = abs(value)
    if abs_v >= 10:
        mag = "very strong"
    elif abs_v >= 1:
        mag = "strong"
    elif abs_v >= 0.1:
        mag = "moderate"
    elif abs_v >= 0.01:
        mag = "weak"
    else:
        mag = "negligible"
    direction = "positive" if value >= 0 else "negative"
    return f"{mag} {direction}"

def _importance_bar(value: float, width: int = 20) -> str:
    """ASCII bar proportional to importance value (0-1)."""
    filled = max(0, min(width, round(value * width)))
    return "[" + "█" * filled + "░" * (width - filled) + "]"

def _rank_label(rank: int, total: int) -> str:
    if rank == 0:
        return "most important"
    if rank == total - 1:
        return "least important"
    return f"#{rank + 1} of {total}"

def _explain_linear(model_name: str, sklearn_model, feature_names: list[str] | None) -> PulseDict:
    """Explain LinearRegression of Ridge."""
    coef = np.atleast_1d(sklearn_model.coef_).flatten()
    intercept = float(np.atleast_1d(sklearn_model.intercept_)[0])
    n = len(coef)
    names = feature_names if feature_names and len(feature_names) == n else [f"Feature {i}" for i in range(n)]
    
    abs_coef = np.abs(coef)
    max_abs = abs_coef.max() if abs_coef.max() > 0 else 1.0
    order = np.argsort(-abs_coef)
    
    print(f"\n[Pulse] {model_name} — learned parameters")
    print(f"  {'Feature':<22} {'Weight':>10}  {'Bar':<22}  Influence")
    print(f"  {'─' * 22}  {'─' * 9}  {'─' * 22}  {'─' * 28}")
    for rank, i in enumerate(order):
        bar_val = abs_coef[i] / max_abs
        bar = _importance_bar(bar_val)
        label = _weight_label(coef[i])
        ranked = _rank_label(rank, n)
        print(f"  {names[i]:<22} {coef[i]:>+10.4f}  {bar}  {label} ({ranked})")
    print(f"\n  Bias (intercept): {intercept:+.4f}")
    print()
    
    feature_list = []
    for i in range(n):
        entry = PulseDict({
            PulseString("name"): PulseString(names[i]),
            PulseString("weight"): PulseNumber(float(coef[i])),
            PulseString("influence"): PulseString(_weight_label(coef[i])),
        })
        feature_list.append(entry)
    
    return PulseDict({
        PulseString("model"): PulseString(model_name),
        PulseString("type"): PulseString("linear"),
        PulseString("features"): PulseList(feature_list),
        PulseString("bias"): PulseNumber(intercept)
    })

def _explain_logistic(sklearn_model, feature_names: list[str] | None) -> PulseDict:
    """Explain LogisticRegression (binary or multi-class)."""
    coef = sklearn_model.coef_
    intercept = sklearn_model.intercept_
    classes = sklearn_model.classes_
    n_features = coef.shape[1]
    names = feature_names if feature_names and len(feature_names) == n_features else [f"Feature {i}" for i in range(n_features)]
    
    print(f"\n[Pulse] LogisticRegression — learned parameters")
    print(f"  Classes: {classes.tolist()}")
    
    class_dicts = []
    for ci, cls in enumerate(classes):
        w = coef[ci] if len(classes) > 2 else coef[0]
        bias = float(intercept[ci]) if len(classes) > 2 else float(intercept[0])
        abs_w = np.abs(w)
        max_abs = abs_w.max() if abs_w.max() > 0 else 1.0
        order = np.argsort(-abs_w)
        
        print(f"\n  Class '{cls}'  (bias: {bias:+.4f})")
        print(f"    {'Feature':<22} {'Weight':>10}  Influence")
        print(f"    {'─' * 22}  {'─' * 9}  {'─' * 28}")
        for rank, i in enumerate(order):
            label = _weight_label(w[i])
            ranked = _rank_label(rank, n_features)
            print(f"    {names[i]:<22} {w[i]:>+10.4f}  {label} ({ranked})")
        
        feature_list = [
            PulseDict({
                PulseString("name"): PulseString(names[i]),
                PulseString("weight"): PulseNumber(float(w[i])),
                PulseString("influence"): PulseString(_weight_label(w[i])),
            })
            for i in range(n_features)
        ]
        class_dicts.append(PulseDict({
            PulseString("class"): PulseString(str(cls)),
            PulseString("bias"): PulseNumber(bias),
            PulseString("features"): PulseList(feature_list),
        }))
    
    print()
    return PulseDict({
        PulseString("model"): PulseString("LogisticRegression"),
        PulseString("type"): PulseString("logistic"),
        PulseString("classes"): PulseList([PulseString(str(c)) for c in classes]),
        PulseString("per_class_weights"): PulseList(class_dicts),
    })

def _explain_tree(model_name: str, sklearn_model, feature_names: list[str] | None) -> PulseDict:
    """Explain DecisionTreeClassifier or DecisionTreeRegressor."""
    importances = sklearn_model.feature_importances_
    n = len(importances)
    names = feature_names if feature_names and len(feature_names) == n else [f"Feature {i}" for i in range(n)]
    order = np.argsort(-importances)
    
    depth = sklearn_model.get_depth()
    n_leaves = sklearn_model.get_n_leaves()
    top_feature = names[order[0]]
    
    print(f"\n[Pulse] {model_name} — structure & feature importances")
    print(f"  Tree depth  : {depth}")
    print(f"  Leaf nodes  : {n_leaves}")
    print(f"  Top split on: '{top_feature}'")
    print()
    


def make(interp) -> PulseModule:
    """Build and return the Pulse 'models' module."""
    
    def _check_tensor(val, fn_name: str, arg_name: str = "data"):
        """Raise if val is not a PulseTensor."""
        if not isinstance(val, PulseTensor):
            interp._raise(f"{fn_name}() expects a tensor for {arg_name}, got '{val.type_name()}'")
    
    def _make_model(name: str, sklearn_model):
        """Wrap a scikit-learn model in a PulseModel with train/predict/score methods."""
        pulse_model = PulseModel(name, sklearn_model)
        
        def train(data: PulseTensor, labels: PulseTensor, auto_preprocess=None) -> PulseNull:
            """Fit the model on data and labels. Optionally standardize and impute missing values."""
            if not isinstance(data, PulseTensor):
                interp._raise(f"train() expects a tensor for data, got '{data.type_name()}'")
            if not isinstance(labels, PulseTensor):
                interp._raise(f"train() expects a tensor for labels, got '{labels.type_name()}'")
            
            X = data.array.copy()
            y = labels.array.copy()
            
            if auto_preprocess is not None and isinstance(auto_preprocess, PulseBoolean) and auto_preprocess.value:
                steps = []
                
                # Step 1 - fill missing values with column mean
                if np.isnan(X).any():
                    col_means = np.nanmean(X, axis=0)
                    nan_mask = np.isnan(X)
                    X[nan_mask] = np.take(col_means, np.where(nan_mask)[1])
                    steps.append("Missing values filled with column mean")
                
                # Step 2 - standardize features
                mean = X.mean(axis=0)
                std = X.std(axis=0)
                std = np.where(std == 0, 1, std)
                X = (X - mean) / std
                steps.append("Features standardized")
                
                # Store scalar params for predict
                pulse_model._scalar_mean = mean
                pulse_model._scalar_std = std
                pulse_model._auto_preprocess = True
                
                print("[Pulse] Auto-preprocessing applied:")
                for step in steps:
                    print(f"  -> {step}")
            else:
                pulse_model._auto_preprocess = False
            
            try:
                pulse_model.sklearn_model.fit(X, y)
                pulse_model.is_trained = True
            except Exception as e:
                interp._raise(f"Training failed: {e}")
            
            return PulseNull()
        
        def predict(data: PulseTensor) -> PulseTensor:
            """Run inference on data and return predictions as a tensor."""
            if not isinstance(data, PulseTensor):
                interp._raise(f"predict() expects a tensor, got '{data.type_name()}'")
            if not pulse_model.is_trained:
                interp._raise(f"Model '{name}' must be trained before calling predict()")
            
            X = data.array.copy()
            
            if getattr(pulse_model, '_auto_preprocess', False):
                if np.isnan(X).any():
                    col_means = pulse_model._scalar_mean
                    nan_mask = np.isnan(X)
                    X[nan_mask] = np.take(col_means, np.where(nan_mask)[1])
                X = (X - pulse_model._scalar_mean) / pulse_model._scalar_std
            
            try:
                result = pulse_model.sklearn_model.predict(X)
                return PulseTensor(np.array(result, dtype=float))
            except Exception as e:
                interp._raise(f"Prediction failed: {e}")
        
        def score(data: PulseTensor, labels: PulseTensor) -> PulseNumber:
            """Return the model's accuracy or R2 score on data and labels."""
            if not isinstance(data, PulseTensor):
                interp._raise(f"score() expects a tensor for data, got '{data.type_name()}'")
            if not isinstance(labels, PulseTensor):
                interp._raise(f"score() expects a tensor for labels, got '{labels.type_name()}'")
            if not pulse_model.is_trained:
                interp._raise(f"Model '{name}' must be trained before calling score()")
            
            X = data.array.copy()
            
            if getattr(pulse_model, '_auto_preprocess', False):
                if np.isnan(X).any():
                    col_means = pulse_model._scalar_mean
                    nan_mask = np.isnan(X)
                    X[nan_mask] = np.take(col_means, np.where(nan_mask)[1])
                X = (X - pulse_model._scalar_mean) / pulse_model._scalar_std
            
            try:
                s = pulse_model.sklearn_model.score(X, labels.array)
                return PulseNumber(float(s))
            except Exception as e:
                interp._raise(f"Score failed: {e}")
        
        def is_trained_fn() -> PulseBoolean:
            """Return True if the model has been trained."""
            return PulseBoolean(pulse_model.is_trained)
        
        pulse_model.methods = {
            "train": PulseNativeMethod(train, arity=-1),
            "predict": PulseNativeMethod(predict, arity=1),
            "score": PulseNativeMethod(score, arity=2),
            "is_trained": PulseNativeMethod(is_trained_fn, arity=0)
        }
        
        return pulse_model
    
    def _linear_regression() -> PulseModel:
        """Create a LinearRegression model."""
        return _make_model("LinearRegression", LinearRegression())
    
    def _logistic_regression() -> PulseModel:
        """Create a LogisticsRegression model."""
        return _make_model("LogisticRegression", LogisticRegression())
    
    def _decision_tree() -> PulseModel:
        """Create a DecisionTreeClassifier model."""
        return _make_model("DecisionTree", DecisionTreeClassifier())
    
    def _random_forest() -> PulseModel:
        """Create a RandomForestClassifer model."""
        return _make_model("RandomForest", RandomForestClassifier())
    
    def _kmeans(k: PulseNumber) -> PulseModel:
        """Create a KMeans clustering model with k clusters."""
        if not isinstance(k, PulseNumber):
            interp._raise(f"KMeans() expects a number for k, got '{k.type_name()}'")
        return _make_model("KMeans", KMeans(n_clusters=int(k.value)))
    
    def _knn(k: PulseNumber) -> PulseModel:
        """Create a KNeighborsClassfier model with k neighbors."""
        if not isinstance(k, PulseNumber):
            interp._raise(f"KNN() expects a number for k, got '{k.type_name()}'")
        return _make_model("KNN", KNeighborsClassifier(n_neighbors=int(k.value)))
    
    def _svc() -> PulseModel:
        """Create a Support Vector Classifier model."""
        return _make_model("SVC", SVC())
    
    def _neural_network() -> PulseModel:
        """Create a MLPClassifier neural network model."""
        return _make_model("NeuralNetwork", MLPClassifier(max_iter=1000))
    
    def _model_auto(data: PulseTensor, labels: PulseTensor, mode: "PulseString | PulseNull" = None, auto_preprocess=None) -> PulseModel:
        """
        Automatically select and train the best model for the given data.
        Tries multiple candidates using cross-validation and returns the winner.
        mode can be 'classification' or 'regression' - inferred it not provided.
        """
        _check_tensor(data, "Model.auto", "data")
        _check_tensor(labels, "Model.auto", "labels")
        
        X = data.array.copy()
        y = labels.array.copy()
        
        scalar_mean = None
        scalar_std = None
        did_preprocess = False
        
        if auto_preprocess is not None and isinstance(auto_preprocess, PulseBoolean) and auto_preprocess.value:
            steps = []
            
            # Step 1 - fill missing values with column mean
            if np.isnan(X).any():
                col_means = np.nanmean(X, axis=0)
                nan_mask = np.isnan(X)
                X[nan_mask] = np.take(col_means, np.where(nan_mask)[1])
                steps.append("Missing values filled with column mean")
                
            # Step 2 - standardize features
            scalar_mean = X.mean(axis=0)
            scalar_std = X.std(axis=0)
            scalar_std = np.where(scalar_std == 0, 1, scalar_std)
            X = (X - scalar_mean) / scalar_std
            steps.append("Features standardized")
            
            did_preprocess = True
            print("[Pulse] Auto-preprocessing applied:")
            for step in steps:
                print(f"  -> {step}")
        
        n_samples = X.shape[0] if X.ndim > 1 else len(X)
        
        if mode is not None and isinstance(mode, PulseString):
            if mode.value == "classification":
                is_classification = True
                unique_values = np.unique(y)
                if not np.all(unique_values == unique_values.astype(int)):
                    interp._raise(
                        "Model.auto() mode='classification' requires integer class labels, "
                        f"got continuous values like {unique_values[:3].tolist()}"
                    )
            elif mode.value == "regression":
                is_classification = False
            else:
                interp._raise(f"Model.auto() mode must be 'classification' or 'regression', got '{mode.value}'")
        else:
            unique_values = np.unique(y)
            is_classification = (
                len(unique_values) <= 20 and
                np.all(unique_values == unique_values.astype(int))
            )
        
        cv_folds = min(3, n_samples // 2)
        cv_folds = max(cv_folds, 2)
        min_samples_per_fold = n_samples // cv_folds
        
        if is_classification:
            candidates = [
                ("LogisticRegression", LogisticRegression(max_iter=1000)),
                ("DecisionTree", DecisionTreeClassifier()),
            ]
            if min_samples_per_fold >= 6:
                n_neighbors = min(5, min_samples_per_fold - 1)
                candidates.append(("KNN", KNeighborsClassifier(n_neighbors=n_neighbors)))
            if n_samples >= 20:
                candidates.append(("RandomForest", RandomForestClassifier()))
            if n_samples >= 20:
                candidates.append(("SVC", SVC()))
            scoring = "accuracy"
        else:
            candidates = [
                ("LinearRegression", LinearRegression()),
                ("Ridge", Ridge()),
            ]
            if n_samples >= 20:
                candidates.append(("RandomForest", RandomForestRegressor()))
            scoring = "r2"
        
        best_name = None
        best_score = -float("inf")
        best_sklearn = None
        
        for name, sk_model in candidates:
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    scores = cross_val_score(sk_model, X, y, cv=cv_folds, scoring=scoring)
                mean_score = float(np.nanmean(scores))
                if mean_score > best_score:
                    best_score = mean_score
                    best_name = name
                    best_sklearn = sk_model
            except Exception:
                continue
        
        if best_sklearn is None:
            interp._raise("Model.auto() could not find a suitable model for the given data")
        
        best_sklearn.fit(X, y)
        model = _make_model(best_name, best_sklearn)
        model.is_trained = True
        model.auto_score = best_score
        
        if did_preprocess:
            model._auto_preprocess=True
            model._scalar_mean = scalar_mean
            model._scalar_std = scalar_std
        
        return model
    
    model_namespace = PulseNamespace("Model", {
        "auto": PulseNativeFunction("auto", _model_auto),
    })
    
    return PulseModule("models", {
        "LinearRegression": PulseNativeFunction("LinearRegression", _linear_regression),
        "LogisticRegression": PulseNativeFunction("LogisticRegression", _logistic_regression),
        "DecisionTree": PulseNativeFunction("DecisionTree", _decision_tree),
        "RandomForest": PulseNativeFunction("RandomForest", _random_forest),
        "KMeans": PulseNativeFunction("KMeans", _kmeans),
        "KNN": PulseNativeFunction("KNN", _knn),
        "SVC": PulseNativeFunction("SVC", _svc),
        "NeuralNetwork": PulseNativeFunction("NeuralNetwork", _neural_network),
        "Model": model_namespace,
    })