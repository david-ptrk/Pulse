from __future__ import annotations
from src.values import PulseModule, PulseModel, PulseNumber, PulseBoolean, PulseTensor, PulseNull
from src.function import PulseNativeFunction, PulseNativeMethod
import numpy as np

def make(interp) -> PulseModule:
    def _make_model(name: str, sklearn_model):
        pulse_model = PulseModel(name, sklearn_model)
        
        def train(data: PulseTensor, labels: PulseTensor) -> PulseNull:
            if not isinstance(data, PulseTensor):
                interp._raise(f"train() expects a tensor for data, got '{data.type_name()}'")
            if not isinstance(labels, PulseTensor):
                interp._raise(f"train() expects a tensor for labels, got '{labels.type_name()}'")
            try:
                pulse_model.sklearn_model.fit(data.array, labels.array)
                pulse_model.is_trained = True
            except Exception as e:
                interp._raise(f"Training failed: {e}")
            return PulseNull()
        
        def predict(data: PulseTensor) -> PulseTensor:
            if not isinstance(data, PulseTensor):
                interp._raise(f"predict() expects a tensor, got '{data.type_name()}'")
            if not pulse_model.is_trained:
                interp._raise(f"Model '{name}' must be trained before calling predict()")
            try:
                result = pulse_model.sklearn_model.predict(data.array)
                return PulseTensor(np.array(result, dtype=float))
            except Exception as e:
                interp._raise(f"Prediction failed: {e}")
        
        def score(data: PulseTensor, labels: PulseTensor) -> PulseNumber:
            if not isinstance(data, PulseTensor):
                interp._raise(f"score() expects a tensor for data, got '{data.type_name()}'")
            if not isinstance(labels, PulseTensor):
                interp._raise(f"score() expects a tensor for labels, got '{labels.type_name()}'")
            if not pulse_model.is_trained:
                interp._raise(f"Model '{name}' must be trained before calling score()")
            try:
                s = pulse_model.sklearn_model.score(data.array, labels.array)
                return PulseNumber(float(s))
            except Exception as e:
                interp._raise(f"Score failed: {e}")
        
        def is_trained_fn() -> PulseBoolean:
            return PulseBoolean(pulse_model.is_trained)
        
        pulse_model.methods = {
            "train": PulseNativeMethod(train, arity=2),
            "predict": PulseNativeMethod(predict, arity=1),
            "score": PulseNativeMethod(score, arity=2),
            "is_trained": PulseNativeMethod(is_trained_fn, arity=0)
        }
        
        return pulse_model
    
    def _linear_regression() -> PulseModel:
        from sklearn.linear_model import LinearRegression
        return _make_model("LinearRegression", LinearRegression())
    
    def _logistic_regression() -> PulseModel:
        from sklearn.linear_model import LogisticRegression
        return _make_model("LogisticRegression", LogisticRegression())
    
    def _decision_tree() -> PulseModel:
        from sklearn.tree import DecisionTreeClassifier
        return _make_model("DecisionTree", DecisionTreeClassifier())
    
    def _random_forest() -> PulseModel:
        from sklearn.ensemble import RandomForestClassifier
        return _make_model("RandomForest", RandomForestClassifier())
    
    def _kmeans(k: PulseNumber) -> PulseModel:
        if not isinstance(k, PulseNumber):
            interp._raise(f"KMeans() expects a number for k, got '{k.type_name()}'")
        from sklearn.cluster import KMeans
        return _make_model("KMeans", KMeans(n_clusters=int(k.value)))
    
    def _knn(k: PulseNumber) -> PulseModel:
        if not isinstance(k, PulseNumber):
            interp._raise(f"KNN() expects a number for k, got '{k.type_name()}'")
        from sklearn.neighbors import KNeighborsClassifier
        return _make_model("KNN", KNeighborsClassifier(n_neighbors=int(k.value)))
    
    def _svc() -> PulseModel:
        from sklearn.svm import SVC
        return _make_model("SVC", SVC())
    
    def _neural_network() -> PulseModel:
        from sklearn.neural_network import MLPClassifier
        return _make_model("NeuralNetwork", MLPClassifier(max_iter=1000))
    
    return PulseModule("models", {
        "LinearRegression": PulseNativeFunction("LinearRegression", _linear_regression),
        "LogisticRegression": PulseNativeFunction("LogisticRegression", _logistic_regression),
        "DecisionTree": PulseNativeFunction("DecisionTree", _decision_tree),
        "RandomForest": PulseNativeFunction("RandomForest", _random_forest),
        "KMeans": PulseNativeFunction("KMeans", _kmeans),
        "KNN": PulseNativeFunction("KNN", _knn),
        "SVC": PulseNativeFunction("SVC", _svc),
        "NeuralNetwork": PulseNativeFunction("NeuralNetwork", _neural_network),
    })