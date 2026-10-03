"""
Model architectures for Earthquake Ground Motion Directionality.
Directly implements:
1. Benchmark Model (Simple Linear Regression on distance d)
2. Ridge Regression with L2 regularization on 21 selected features
3. Deep Neural Network (MLP) with ReLU, Adam, and L2 regularization
4. Gradient Boosting Ensemble (Bonus state-of-the-art comparison)
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, List
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.neural_network import MLPRegressor
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

class BenchmarkModel:
    """
    Benchmark Model: Simple Linear Regression using ONLY the distance between sites (d).
    Equation: Δθ = c1 + c2 * d
    """
    def __init__(self):
        self.model = LinearRegression()
        self.distance_col = 'distance_between_sites'
        self.c1 = None
        self.c2 = None
        
    def fit(self, X: pd.DataFrame, y: pd.Series):
        if self.distance_col in X.columns:
            X_dist = X[[self.distance_col]].values
        else:
            # Fallback if first column is distance
            X_dist = X.iloc[:, [0]].values
        self.model.fit(X_dist, y.values)
        self.c1 = float(self.model.intercept_)
        self.c2 = float(self.model.coef_[0])
        return self
        
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if self.distance_col in X.columns:
            X_dist = X[[self.distance_col]].values
        else:
            X_dist = X.iloc[:, [0]].values
        preds = self.model.predict(X_dist)
        return np.clip(preds, 0.0, 90.0)

class RidgeRegressionModel:
    """
    Ridge Regression Model: Linear least squares with L2 penalty.
    min_β ||y - Xβ||_2^2 + α ||β||_2^2
    """
    def __init__(self, alpha: float = 1.5, random_state: int = 42):
        self.alpha = alpha
        self.random_state = random_state
        self.model = Ridge(alpha=alpha, random_state=random_state)
        
    def fit(self, X: pd.DataFrame, y: pd.Series):
        self.model.fit(X, y)
        return self
        
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        preds = self.model.predict(X)
        return np.clip(preds, 0.0, 90.0)

class NeuralNetworkModel:
    """
    Deep Neural Network (Multi-Layer Perceptron) for non-linear regression.
    Trained with Adam optimizer, ReLU activation, and L2 weight decay.
    """
    def __init__(
        self,
        hidden_layer_sizes: tuple = (400, 400, 300, 200, 100),
        alpha: float = 0.1,
        learning_rate_init: float = 0.001,
        max_iter: int = 350,
        random_state: int = 42,
        early_stopping: bool = True
    ):
        self.hidden_layer_sizes = hidden_layer_sizes
        self.alpha = alpha
        self.model = MLPRegressor(
            hidden_layer_sizes=hidden_layer_sizes,
            activation='relu',
            solver='adam',
            alpha=alpha,
            learning_rate='adaptive',
            learning_rate_init=learning_rate_init,
            max_iter=max_iter,
            random_state=random_state,
            early_stopping=early_stopping,
            validation_fraction=0.1,
            n_iter_no_change=25
        )
        
    def fit(self, X: pd.DataFrame, y: pd.Series):
        self.model.fit(X, y)
        return self
        
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        preds = self.model.predict(X)
        return np.clip(preds, 0.0, 90.0)

class GradientBoostingModel:
    """
    Gradient Boosted Trees Model for advanced comparison against Neural Networks.
    """
    def __init__(self, max_iter: int = 250, learning_rate: float = 0.05, random_state: int = 42):
        self.model = HistGradientBoostingRegressor(
            max_iter=max_iter,
            learning_rate=learning_rate,
            random_state=random_state,
            l2_regularization=0.1
        )
        
    def fit(self, X: pd.DataFrame, y: pd.Series):
        self.model.fit(X, y)
        return self
        
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        preds = self.model.predict(X)
        return np.clip(preds, 0.0, 90.0)

def evaluate_predictions(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """Computes R^2, Mean Absolute Error (MAE), and RMSE."""
    r2 = r2_score(y_true, y_pred)
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    corr = np.corrcoef(y_true, y_pred)[0, 1] if len(y_true) > 1 else 0.0
    return {
        "r2": float(r2),
        "mae": float(mae),
        "rmse": float(rmse),
        "correlation": float(corr)
    }
