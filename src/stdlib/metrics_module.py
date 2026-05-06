"""
metrics_module.py

Pulse standard library module for evaluating machine learning models.
Provides common classification and regression metrics so students can
measure and understand model performance after training.
"""

from __future__ import annotations
import numpy as np
from src.values import PulseModule, PulseString, PulseNull, PulseNumber, PulseList, PulseDict, PulseBoolean, PulseTensor
from src.function import PulseNativeFunction

def make(interp) -> PulseModule:
    """Build and return the Pulse 'metrics' module."""
    
    def _check_tensor(val, name: str) -> np.ndarray:
        """Raise if val is not a PulseTensor, then return its numpy array."""
        if not isinstance(val, PulseTensor):
            interp._raise(f"{name} must be a tensor, got '{val.type_name()}'")
        return val.array
    
    def _check_same_length(a: np.ndarray, b: np.ndarray, fn: str) -> None:
        """Raise if two arrays have different lengths."""
        if len(a) != len(b):
            interp._raise(
                f"{fn}() y_true and y_pred must have the same length, "
                f"got {len(a)} and {len(b)}"
            )
    
    # Classification
    def _accuracy(y_true, y_pred) -> PulseNumber:
        """
        Return the fraction of correct predictions.
        accuracy = correct predictions / total predictions.
        Range: 0.0 (worst) to 1.0 (perfect).
        """
        yt = _check_tensor(y_true, "accuracy() y_true")
        yp = _check_tensor(y_pred, "accuracy() y_pred")
        _check_same_length(yt, yp, "accuracy")
        return PulseNumber(float(np.mean(yt == yp)))
    
    def _precision(y_true, y_pred) -> PulseNumber:
        """
        Return precision = TP / (TP + FP).
        Of all predicted positives, what fraction were actually positive?
        Uses macro averaging for multi-class problems.
        """
        yt = _check_tensor(y_true, "precision() y_true")
        yp = _check_tensor(y_pred, "precision() y_pred")
        _check_same_length(yt, yp, "precision")
        from sklearn.metrics import precision_score
        try:
            score = precision_score(yt, yp, average="macro", zero_division=0)
            return PulseNumber(float(score))
        except Exception as e:
            interp._raise(f"precision() failed: {e}")
    
    def _recall(y_true, y_pred) -> PulseNumber:
        """
        Return recall = TP / (TP + FN).
        Of all actual positives, what fraction did the model find?
        Uses macro averaging for multi-class problems.
        """
        yt = _check_tensor(y_true, "recall() y_true")
        yp = _check_tensor(y_pred, "recall() y_pred")
        _check_same_length(yt, yp, "recall")
        from sklearn.metrics import recall_score
        try:
            score = recall_score(yt, yp, average="macro", zero_division=0)
            return PulseNumber(float(score))
        except Exception as e:
            interp._raise(f"recall() failed: {e}")
    
    def _f1(y_true, y_pred) -> PulseNumber:
        """
        Return F1 score = 2 * (precision * recall) / (precision + recall).
        Harmonic mean of precision and recall.
        Uses macro averaging for multi-class problems.
        """
        yt = _check_tensor(y_true, "f1() y_true")
        yp = _check_tensor(y_pred, "f1() y_pred")
        _check_same_length(yt, yp, "f1")
        from sklearn.metrics import f1_score
        try:
            score = f1_score(yt, yp, average="macro", zero_division=0)
            return PulseNumber(float(score))
        except Exception as e:
            interp._raise(f"f1() failed: {e}")
    
    def _confusion_matrix(y_true, y_pred) -> PulseNull:
        """
        Print a formatted confusion matrix.
        Rows = true labels, columns = predicted labels.
        Diagonal = correct predictions.
        """
        yt = _check_tensor(y_true, "confusion_matrix() y_true")
        yp = _check_tensor(y_pred, "confusion_matrix() y_pred")
        _check_same_length(yt, yp, "confusion_matrix")
        
        from sklearn.metrics import confusion_matrix
        try:
            cm = confusion_matrix(yt, yp)
            labels = sorted(set(yt.astype(int).tolist()))
            
            print("\nConfusion Matrix (rows=true, cols=predicted):")
            print("       " + "  ".join(f"{l:>4}" for l in labels))
            print("      " + "-" * (6 * len(labels)))
            for i, row in zip(labels, cm):
                print(f"  {i:>3} | " + "  ".join(f"{v:>4}" for v in row))
            print()
            
            # per-class accuracy
            print("  Per-class accuracy:")
            for i, (label, row) in enumerate(zip(labels, cm)):
                total = row.sum()
                correct = cm[i][i]
                pct = round(100 * correct / total, 1) if total > 0 else 0
                print(f"    Class {label}: {correct}/{total} correct ({pct}%)")
            print()
        
        except Exception as e:
            interp._raise(f"confusion_matrix() failed: {e}")
        
        return PulseNull()
    
    def _classsification_report(y_true, y_pred) -> PulseNull:
        """Print a full classification report with precision, recall, and F1 per class."""
        yt = _check_tensor(y_true, "classification_report() y_true")
        yp = _check_tensor(y_pred, "classification_report() y_pred")
        _check_same_length(yt, yp, "classification_report")
        from sklearn.metrics import classification_report
        try:
            print("\nClassification Report:")
            print(classification_report(yt, yp, zero_division=0))
        except Exception as e:
            interp._raise(f"classification_report() failed: {e}")
        return PulseNull()
    
    # Regression
    def _mse(y_true, y_pred) -> PulseNumber:
        """
        Return Mean Squared Error = mean((y_true - y_pred)^2).
        Penalizes large errors heavily. Lower is better.
        Smae units as y^2.
        """
        yt = _check_tensor(y_true, "mse() y_true")
        yp = _check_tensor(y_pred, "mse() y_pred")
        _check_same_length(yt, yp, "mse")
        return PulseNumber(float(np.mean((yt - yp) ** 2)))
    
    def _rmse(y_true, y_pred) -> PulseNumber:
        """
        Return Root Mean Squared Error = sqrt(MSE).
        Same units as y - easier to interpret than MSE.
        Lower is better.
        """
        yt = _check_tensor(y_true, "rmse() y_true")
        yp = _check_tensor(y_pred, "rmse() y_pred")
        _check_same_length(yt, yp, "rmse")
        return PulseNumber(float(np.sqrt(np.mean((yt - yp) ** 2))))
    
    def _mae(y_true, y_pred) -> PulseNumber:
        """
        Return Mean Absolute Error = mean(|y_true - y_pred|).
        Robust to outliers. Lower is better. Same units as y.
        """
        yt = _check_tensor(y_true, "mae() y_true")
        yp = _check_tensor(y_pred, "mae() y_pred")
        _check_same_length(yt, yp, "mae")
        return PulseNumber(float(np.mean(np.abs(yt - yp))))
    
    def _r2(y_true, y_pred) -> PulseNumber:
        """
        Return R^2 (coefficient of determination).
        Measures how well predictions explain variance in true values.
        R^2=1.0 perfect, R^2=0.0 predicts mean, R^2<0 worse than mean.
        """
        yt = _check_tensor(y_true, "r2() y_true")
        yp = _check_tensor(y_pred, "r2() y_pred")
        _check_same_length(yt, yp, "r2")
        ss_res = np.sum((yt - yp) ** 2)
        ss_tot = np.sum((yt - np.mean(yt)) ** 2)
        if ss_tot == 0:
            return PulseNumber(1.0 if ss_res == 0 else 0.0)
        return PulseNumber(float(1 - ss_res / ss_tot))
    
    def _mape(y_true, y_pred) -> PulseNumber:
        """
        Return Mean Absolute Percentage Error = meean(|y_true - y_pred| / |y_true|) * 100.
        Expressed as a percentage. Lower is better.
        Avoids division by zero by skipping zero true values.
        """
        yt = _check_tensor(y_true, "mape() y_true")
        yp = _check_tensor(y_pred, "mape() y_pred")
        _check_same_length(yt, yp, "mape")
        mask = yt != 0
        if not mask.any():
            interp._raise("mape() all true values are zero - cannot compute percentage error")
        return PulseNumber(float(np.mean(np.abs((yt[mask] - yp[mask]) / yt[mask])) * 100))
    
    # Summary
    def _summary(y_true, y_pred, mode=None) -> PulseNull:
        """
        Print a full metrics summary.
        mode='classification' or mode='regression'.
        If mode is not given it is inferred from the data.
        """
        yt = _check_tensor(y_true, "summary() y_true")
        yp = _check_tensor(y_pred, "summary() y_pred")
        _check_same_length(yt, yp, "summary")
        
        # infer mode
        if mode is not None and isinstance(mode, PulseString):
            is_classification = mode.value == "classification"
        else:
            unique = np.unique(yt)
            is_classification = (len(unique) <= 20 and np.all(unique == unique.astype(int)))
        
        line = "=" * 50
        print(f"\n{line}")
        print(f"  Metrics Summary — {'Classification' if is_classification else 'Regression'}")
        print(f"{line}")
        
        if is_classification:
            from sklearn.metrics import precision_score, recall_score, f1_score
            acc = float(np.mean(yt == yp))
            prec = float(precision_score(yt, yp, average="macro", zero_division=0))
            rec = float(recall_score(yt, yp, average="macro", zero_division=0))
            f1 = float(f1_score(yt, yp, average="macro", zero_division=0))
            print(f"  Accuracy  : {acc:.4f}")
            print(f"  Precision : {prec:.4f}  (macro avg)")
            print(f"  Recall    : {rec:.4f}  (macro avg)")
            print(f"  F1 Score  : {f1:.4f}  (macro avg)")
            print(f"{line}\n")
            _confusion_matrix(y_true, y_pred)
        else:
            mse = float(np.mean((yt - yp) ** 2))
            rmse = float(np.sqrt(mse))
            mae = float(np.mean(np.abs(yt - yp)))
            ss_res = np.sum((yt - yp) ** 2)
            ss_tot = np.sum((yt - np.mean(yt)) ** 2)
            r2 = float(1 - ss_res / ss_tot) if ss_tot != 0 else 1.0
            print(f"  MSE       : {mse:.4f}")
            print(f"  RMSE      : {rmse:.4f}")
            print(f"  MAE       : {mae:.4f}")
            print(f"  R² Score  : {r2:.4f}")
            print(f"{line}\n")
        
        return PulseNull()
    
    return PulseModule("metrics", {
        "accuracy": PulseNativeFunction("accuracy", _accuracy),
        "precision": PulseNativeFunction("precision", _precision),
        "recall": PulseNativeFunction("recall", _recall),
        "f1": PulseNativeFunction("f1", _f1),
        "confusion_matrix": PulseNativeFunction("confusion_matrix", _confusion_matrix),
        "classification_report": PulseNativeFunction("classification_report", _classsification_report),
        "mse": PulseNativeFunction("mse", _mse),
        "rmse": PulseNativeFunction("rmse", _rmse),
        "mae": PulseNativeFunction("mae", _mae),
        "r2": PulseNativeFunction("r2", _r2),
        "mape": PulseNativeFunction("mape", _mape),
        "summary": PulseNativeFunction("summary", _summary),
    })