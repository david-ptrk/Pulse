"""
learn_module.py

Pulse standard library module for learning machine learning concepts.
Each example runs live code with step-by-step explanations printed between 
each stage so students can follow along and understand what is happening.
"""

from __future__ import annotations
import numpy as np
from src.values import PulseModule, PulseString, PulseNull, PulseNumber, PulseBoolean
from src.function import PulseNativeFunction

# Formatting helpers
def _header(title: str) -> None:
    line = "=" * 60
    print(f"\n{line}")
    print(f"  {title}")
    print(f"{line}\n")

def _step(n: int, title: str) -> None:
    print(f"\n[Step {n}] {title}")
    print("-" * 40)

def _explain(text: str) -> None:
    for line in text.strip().splitlines():
        print(f"  > {line.strip()}")

def _result(label: str, value) -> None:
    print(f"  {label}: {value}")

def _separator() -> None:
    print()

# Linear Regression
def _example_linear_regression() -> None:
    _header("Linear Regression")
    
    _explain("""
        Linear Regression finds the best straight line through your data.
        It learns a weight for each feature and a bias term so that:
            prediction = weight * feature1 + weight2 * feature2 + ... + bias
        It is used when the output is a continuous number (e.g., price, temperature).
    """)
    
    _step(1, "Generate sample data")
    _explain("""
        We create 80 samples with 1 feature (X) and a target (y).
        The true relationship is: y = 3.5 * X + 7 + some noise.
        In real life you would load this from a CSV or database.
    """)
    np.random.seed(42)
    X = np.random.rand(80, 1) * 10
    y = 3.5 * X.squeeze() + 7 + np.random.randn(80) * 2
    _result("Samples", len(X))
    _result("Features", X.shape[1])
    _result("First 3 X values", X[:3].squeeze().round(3).tolist())
    _result("First 3 y values", y[:3].round(3).tolist())
    
    _step(2, "Split data into training and test sets")
    _explain("""
        We never test a model on data it trained on - that would be cheating.
        80% of data goes to training, 20% to testing.
        The model learns from training data is evaluated on test data.
    """)
    split = int(0.8 * len(X))
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]
    _result("Training samples", len(X_train))
    _result("Test samples", len(X_test))
    
    _step(3, "Train the model")
    _explain("""
        Training means finding the best weights and bias.
        Linear Regression solves this mathematically using the least square method:
            it minimizes the sum of squared differences between predictions and true values.
        This is instant for small datasets.
    """)
    from sklearn.linear_model import LinearRegression
    model = LinearRegression()
    model.fit(X_train, y_train)
    _result("Learned weight (slope)", round(float(model.coef_[0]), 4))
    _result("Learned bias (intercept)", round(float(model.intercept_), 4))
    _explain("True relationship was: y = 3.5 * X + 7 — compare with learned values above.")
    
    _step(4, "Make predictions")
    _explain("""
        We pass the test features through the model.
        It multiplies each feature by the learned weight and adds the bias.
    """)
    predictions = model.predict(X_test)
    for i in range(3):
        _result(f"  X={X_test[i][0]:.2f}  predicted={predictions[i]:.2f}  actual={y_test[i]:.2f}", "")
    
    _step(5, "Evaluate the model")
    _explain("""
        R^2 (R-squared) measures how well the model explains the variance in data.
            R^2 = 1.0 -> perfect predictions
            R^2 = 0.0 -> model is no better than predicting the mean
            R^2 < 0.0 -> model is worse than predicting the mean
        MSE (Mean Squared Error) measures average squared prediction error.
        Lower MSE is better.
    """)
    score = model.score(X_test, y_test)
    mse = float(np.mean(predictions - y_test) ** 2)
    _result("R^2 Score", round(score, 4))
    _result("MSE", round(mse, 4))
    
    _separator()
    _explain("Linear Regression is best for continuous outputs with linear relationships.")

# Logistic Regression
def _example_logistic_regression() -> None:
    _header("Logistic Regression")
    
    _explain("""
        Despite the name, Logistic Regression is a classification algorithm.
        It predicts the probability that a sample belongs to a class.
        It uses the sigmoid function to squash outputs between 0 and 1:
            P(class=1) = 1 / (1 + e^(-z))  where z = weight * X + bias
        If P >= 0.5 -> class 1, else -> class 0.
        Best used for binary classification problems.
    """)
    
    _step(1, "Generate binary classification data")
    _explain("""
        We create two groups of points in 2D space.
        Class 0 is centered at (2, 2), Class 1 is centered at (6, 6).
        In real life this could be: spam vs not-spam, sick vs healthy.
    """)
    np.random.seed(0)
    X0 = np.random.randn(50, 2) + [2, 2]
    X1 = np.random.randn(50, 2) + [6, 6]
    X = np.vstack([X0, X1])
    y = np.array([0] * 50 + [1] * 50)
    _result("Samples", len(X))
    _result("Features", X.shape[1])
    _result("Classes", "0 (group A) and 1 (group B)")
    
    _step(2, "Split into training and test sets")
    split = 80
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]
    _result("Training samples", len(X_train))
    _result("Test samples", len(X_test))
    
    _step(3, "Train the model")
    _explain("""
        Logistic Regression uses gradient descent to find weights that
        maximize the likelihood of the correct class labels.
        It iterates many times, adjusting weights each time to reduce error.
    """)
    from sklearn.linear_model import LogisticRegression
    model = LogisticRegression()
    model.fit(X_train, y_train)
    _result("Weights for feature 1", round(float(model.coef_[0][0]), 4))
    _result("Weights for feature 2", round(float(model.coef_[0][1]), 4))
    _result("Bias", round(float(model.intercept_[0]), 4))
    
    _step(4, "Make predictions")
    _explain("""
        For each test sample the model computes a probability.
        If probability >= 0.5 it predicts class 1, otherwise class 0.
    """)
    predictions = model.predict(X_test)
    probs = model.predict_proba(X_test)
    for i in range(3):
        _result(
            f"  features={X_test[i].round(2).tolist()}  "
            f"P(class=1)={probs[i][1]:.2f}  "
            f"predicted={predictions[i]}  actual={y_test[i]}", ""
        )
    
    _step(5, "Evaluate the model")
    _explain("""
        Accuracy = correct predictions / total predictions.
        A random classifier on 2 classes would score 0.50.
        Above 0.90 is generally considered good.
    """)
    accuracy = model.score(X_test, y_test)
    _result("Accuracy", round(accuracy, 4))
    
    _separator()
    _explain("Logistic Regression is fast, interpretable, and great for binary classification.")

# KNN
def _example_knn() -> None:
    _header("K-Nearest Neighbors (KNN)")
    
    _explain("""
        KNN is one of the simplest ML algorithms.
        To classify a new point, it looks at the K closest training points
        and takes a majority vote among their labels.
        No training phase - it memorizes the entire dataset.
        K is a hyperparameter you choose (typically 3, 5, or 7).
    """)
    
    _step(1, "Generate multi-class data")
    _explain("We create 3 classes of 40 points each in 2D space.")
    np.random.seed(1)
    X = np.vstack([
        np.random.randn(40, 2) + [0, 0],
        np.random.randn(40, 2) + [5, 0],
        np.random.randn(40, 2) + [2, 4],
    ])
    y = np.array([0]*40 + [1]*40 + [2]*40)
    _result("Samples", len(X))
    _result("Classes", 3)
    
    _step(2, "Split data")
    split = 100
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]
    _result("Training samples", len(X_train))
    _result("Test samples", len(X_test))
    
    _step(3, "Try different values of K")
    _explain("""
        K controls the bias-variance tradeoff:
            Small K (e.g., 1) -> low bias, high variance (overfits noise)
            Large K (e.g., 20) -> high bias, low variance (underfits)
        We try K = 1, 3, 5, 7 and compare accuracy.
    """)
    from sklearn.neighbors import KNeighborsClassifier
    for k in [1, 3, 5, 7]:
        m = KNeighborsClassifier(n_neighbors=k)
        m.fit(X_train, y_train)
        acc = m.score(X_test, y_test)
        _result(f"  K={k}  accuracy", round(acc, 4))
    
    _step(4, "Train final model with K=5")
    model = KNeighborsClassifier(n_neighbors=5)
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    _result("Final accuracy", round(model.score(X_test, y_test), 4))
    
    _step(5, "How prediction works")
    _explain("""
        For a new point, KNN computes the Euclidean distance to all training points.
        It picks the 5 nearest neighbors and takes majority vote.
    """)
    sample = X_test[0]
    distance = np.sqrt(((X_train - sample) ** 2).sum(axis=1))
    nearest = np.argsort(distance)[:5]
    _result("New point", sample.round(3).tolist())
    _result("5 nearest labels", y_train[nearest].tolist())
    _result("Predicted class", int(predictions[0]))
    _result("Actual class", int(y_test[0]))
    
    _separator()
    _explain("KNN is intuitive but slow on large datasets - it scans all points at prediction time.")

# Decision Tree
def _example_decision_tree() -> None:
    _header("Decision Tree")
    
    _explain("""
        A Decision Tree learns a series of if/else rules from data.
        At each node it asks a question like: "Is feature X > 2.5?"
        It splits data to maximize purity (all one class in each branch).
        The measure of purity is called Gini impurity or Entropy.
        Easy to understand - you can literally read the learned rules.
    """)
    
    _step(1, "Load the Iris dataset")
    _explain("""
        The Iris dataset is a classic ML dataset.
        It has 150 flowers, 4 features (petal/sepal length and width),
        and 3 classes (Setosa, Versicolor, Virginica).
    """)
    from sklearn.datasets import load_iris
    iris = load_iris()
    X, y = iris.data, iris.target
    _result("Samples", len(X))
    _result("Features", X.shape[1])
    _result("Feature names", iris.feature_names)
    _result("Classes", iris.target_names.tolist())
    
    _step(2, "Split data")
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    _result("Training samples", len(X_train))
    _result("Test samples", len(X_test))
    
    _step(3, "Train the tree")
    _explain("""
        The tree is built top-down by greedily choosing the best split at each node.
        max_depth=3 limits the tree to 3 levels to prevent overfitting.
    """)
    from sklearn.tree import DecisionTreeClassifier
    model = DecisionTreeClassifier(max_depth=3, random_state=42)
    model.fit(X_train, y_train)
    _result("Tree depth", model.get_depth())
    _result("Tree leaves", model.get_n_leaves())
    
    _step(4, "Feature importance")
    _explain("""
        Feature importance tells us which features the tree relied on most.
        Higher value = more useful for making decisions.
    """)
    for name, imp in zip(iris.feature_names, model.feature_importances_):
        _result(f"  {name}", round(float(imp), 4))
    
    _step(5, "Evaluate")
    accuracy = model.score(X_test, y_test)
    _result("Accuracy", round(accuracy, 4))
    
    _separator()
    _explain("Decision Trees are interpretable but prone to overfiting without depth limits.")

# Random Forest
def _example_random_forest() -> None:
    _header("Random Forest")
    
    _explain("""
        A Random Forest builds many Decision Trees and combines their votes.
        Each tree is trained on a random subset of data (bagging) and
        uses a random subset of features at each split.
        This reduces overfitting and improves accuracy over a single tree.
        The final prediction is the majority vote across all trees.
    """)
    
    _step(1, "Load Iris dataset")
    from sklearn.datasets import load_iris
    iris = load_iris()
    X, y = iris.data, iris.target
    
    _step(2, "Split data")
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    _step(3, "Compare single tree vs forest")
    _explain("""
        We train a single Decision Tree and a Random Forest with 100 trees.
        The forest should consistently outperform the single tree.
    """)
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.ensemble import RandomForestClassifier
    
    tree = DecisionTreeClassifier(random_state=42)
    forest = RandomForestClassifier(n_estimators=100, random_state=42)
    
    tree.fit(X_train, y_train)
    forest.fit(X_train, y_train)
    
    _result("Single Decision Tree accuracy", round(tree.score(X_test, y_test), 4))
    _result("Random Forest accuracy (100 trees)", round(forest.score(X_test, y_test), 4))
    
    _step(4, "Effect of number of trees")
    _explain("More trees generaly means better accuracy but slower prediction.")
    for n in [1, 5, 10, 50, 100]:
        m = RandomForestClassifier(n_estimators=n, random_state=42)
        m.fit(X_train, y_train)
        acc = m.score(X_test, y_test)
        _result(f"  {n:>4} trees  accuracy", round(acc, 4))
    
    _step(5, "Feature importance")
    _explain("Random Forest aggregates feature importance across all trees.")
    for name, imp in zip(iris.feature_names, forest.feature_importances_):
        bar = "█" * int(imp * 30)
        _result(f"  {name:<30} {bar}", round(float(imp), 4))
    
    _separator()
    _explain("Random Forest is robust, handles noise well, and rarely overfits")

# KMeans
def _example_kmeans() -> None:
    _header("K-Means Clustering")
    
    _explain("""
        K-Means is an unsupervised algorithm - there is no labels.
        It groups data in K clusters by minimizing the distance
        between each point and its cluster center (centroid).
        Algorithm:
            1. Place K centroids randomly
            2. Assig each point to the nearest centroid
            3. Move each centroid to the mean of its assigned points
            4. Repeat steps 2-3 until centroids stop moving
    """)
    
    _step(1, "Generate unlabeled data")
    _explain("Three natural groups of points - but we pretend we don't know the labels.")
    np.random.seed(5)
    X = np.vstack([
        np.random.randn(50, 2) + [0, 0],
        np.random.randn(50, 2) + [6, 0],
        np.random.randn(50, 2) + [3, 5],
    ])
    true_labels = np.array([0]*50 + [1]*50 + [2]*50)
    _result("Samples", len(X))
    _result("True clusters (hidden from model)", 3)
    
    _step(2, "Choosing K with the Elbow method")
    _explain("""
        Inertia = sum of squared distances from each point to its centroid.
        As K increases, inertia always decreases.
        The 'elbow' - where inertia stops dropping sharply - is the best K.
    """)
    from sklearn.cluster import KMeans
    for k in range(1, 7):
        m = KMeans(n_clusters=k, random_state=42, n_init=10)
        m.fit(X)
        _result(f"  K={k}  inertia", round(float(m.inertia_), 2))
    
    _step(3, "Train with K=3")
    model = KMeans(n_clusters=3, random_state=42, n_init=10)
    model.fit(X)
    labels = model.labels_
    _result("Cluster centers", [c.round(2).tolist() for c in model.cluster_centers_])
    _result("Iterations to converge", model.n_iter_)
    
    _step(4, "Evaluate clustering quality")
    _explain("""
        Since we know the true labels, we can measure clustering quality.
        Adjusted Rand Index (ARI):
            1.0 = perfect match with true labels
            0.0 = random labeling
    """)
    from sklearn.metrics import adjusted_rand_score
    ari = adjusted_rand_score(true_labels, labels)
    _result("Adjusted Rand Index", round(float(ari), 4))
    
    _step(5, "Predict cluster for a new point")
    new_point = np.array([[3.1, 4.8]])
    prediction = model.predict(new_point)
    distances = np.sqrt(((model.cluster_centers_ - new_point) ** 2).sum(axis=1))
    _result("New point", new_point[0].tolist())
    _result("Distance to cluster 0", round(float(distances[0]), 3))
    _result("Distance to cluster 1", round(float(distances[1]), 3))
    _result("Distance to cluster 2", round(float(distances[2]), 3))
    _result("Assigned to cluster", int(prediction[0]))
    
    _separator()
    _explain("K-Means works well on round, similarly-sized clusters. Use Elbow method to pick K.")

# Neural Network
def _example_neural_network() -> None:
    _header("Neural Network (MLP)")
    
    _explain("""
        A Neural Network (Multi-Layer Perceptron) consists of layers of neurons.
        Each neuron computes: output = activation(weights * inputs + bias)
        Common activation functions: ReLU, Sigmoid, Tanh.
        Layers:
            Input layer   -> receives raw features
            Hidden layers -> learn intermediate representations
            Output layer  -> produces final prediction
        Training uses backpropagation - errors flow backward to update weights.
    """)
    
    _step(1, "Load the Digits dataset")
    _explain("""
        The Digits dataset has 1797 handwritten digit images (0-9).
        Each image is 8x8 pixels = 64 features.
        Goal: classify which digit (0-9) each image represents.
    """)
    from sklearn.datasets import load_digits
    digits = load_digits()
    X, y = digits.data, digits.target
    X = X / 16.0
    _result("Samples", len(X))
    _result("Features", X.shape[1])
    _result("Classes", 10)
    
    _step(2, "Split data")
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    _result("Training samples", len(X_train))
    _result("Test samples", len(X_test))
    
    _step(3, "Effect of network architecture")
    _explain("""
        Architecture means the number and size of hidden layers.
        (64,) = one hidden layer with 64 neurons
        (128, 64) = two hidden layers
        More neurons = more capacity but slower and more data needed.
    """)
    from sklearn.neural_network import MLPClassifier
    for arch in [(32,), (64,), (128,), (64, 32), (128, 64)]:
        m = MLPClassifier(hidden_layer_sizes=arch, max_iter=500, random_state=42)
        m.fit(X_train, y_train)
        acc = m.score(X_test, y_test)
        _result(f"  architecture={arch}", round(acc, 4))
    
    _step(4, "Train final model")
    _explain("""
        We use two hidden layers (128, 64) with ReLU activation.
        Adam optimizer adjusts the learning rate automatically.
    """)
    model = MLPClassifier(
        hidden_layer_sizes=(128, 64),
        activation="relu",
        solver="adam",
        max_iter=500,
        random_state=42,
    )
    model.fit(X_train, y_train)
    _result("Training accuracy", round(model.score(X_train, y_train), 4))
    _result("Test accuracy", round(model.score(X_test,  y_test),  4))
    _result("Training loss (final iteration)", round(float(model.loss_), 6))
    
    _step(5, "Confusion matrix insight")
    _explain("""
        A confusion matrix shows which digits get confused with each other.
        Each row = true label, each column = predicted label.
        Diagonal = correct predictions.
    """)
    from sklearn.metrics import confusion_matrix
    predictions = model.predict(X_test)
    cm = confusion_matrix(y_test, predictions)
    print("  Confusion Matrix (rows=true, cols=predicted):")
    print("     " + "  ".join(str(i) for i in range(10)))
    for i, row in enumerate(cm):
        print(f"  {i}  " + "  ".join(f"{v:2}" for v in row))
    
    _separator()
    _explain("Neural Networks are powerful but need more data and tuning than simpler models.")


# Topics list
_EXAMPLES = {
    "linear_regression": _example_linear_regression,
    "logistic_regression": _example_logistic_regression,
    "knn": _example_knn,
    "decision_tree": _example_decision_tree,
    "random_forest": _example_random_forest,
    "kmeans": _example_kmeans,
    "neural_network": _example_neural_network,
}

# Module factory
def make(interp) -> PulseModule:
    """Build and return the Pulse 'learn' module."""
    
    def _example(topic) -> PulseNull:
        """Run a step-by-step educational example for the given ML topic."""
        if not isinstance(topic, PulseString):
            interp._raise(f"learn.example() expects a string, got '{topic.type_name()}'")
        
        key = topic.value.lower().replace(" ", "_").replace("-", "_")
        
        if key not in _EXAMPLES:
            available = ", ".join(f'"{k}"' for k in _EXAMPLES)
            interp._raise(
                f"learn.example() unknown topic '{topic.value}'.\n"
                f"  Available topics: {available}"
            )
        
        _EXAMPLES[key]()
        return PulseNull()
    
    def _topics() -> PulseNull:
        """Print all available learning topics."""
        _header("Available Learning Topics")
        for key in _EXAMPLES:
            print(f"  learn.example(\"{key}\")")
        print()
        return PulseNull()
    
    return PulseModule("learn", {
        "example": PulseNativeFunction("example", _example),
        "topics": PulseNativeFunction("topics", _topics),
    })