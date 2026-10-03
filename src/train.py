"""
Training pipeline and hyperparameter tuning for Earthquake Ground Motion Directionality.
Performs:
1. Training Benchmark Linear Model
2. Ridge Regression tuning over alpha on validation set
3. Neural Network (MLP) Grid Search over architectures on validation set
4. Model serialization and performance logging
"""

import json
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from typing import Dict, Any, Tuple
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

from src.config import (
    MODELS_DIR, SELECTED_FEATURES_PATH, RANDOM_SEED,
    RIDGE_ALPHA_DEFAULT, NN_ALPHA_DEFAULT
)
from src.data_preprocessing import load_and_preprocess_data
from src.models import (
    BenchmarkModel, RidgeRegressionModel, NeuralNetworkModel,
    GradientBoostingModel, evaluate_predictions
)

def tune_ridge_alpha(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    y_val: pd.Series
) -> Tuple[float, Dict[float, float]]:
    """Tuning alpha parameter for Ridge Regression using validation set."""
    alphas = [0.01, 0.05, 0.1, 0.5, 1.0, 1.5, 2.0, 5.0, 10.0, 20.0, 50.0]
    best_alpha = 1.5
    best_r2 = -float('inf')
    alpha_history = {}
    
    for a in alphas:
        model = RidgeRegressionModel(alpha=a, random_state=RANDOM_SEED)
        model.fit(X_train, y_train)
        pred_val = model.predict(X_val)
        score = r2_score(y_val, pred_val)
        alpha_history[a] = score
        if score > best_r2:
            best_r2 = score
            best_alpha = a
            
    print(f"Optimal Ridge alpha: {best_alpha} (Validation R² = {best_r2:.4f})")
    return best_alpha, alpha_history

def grid_search_neural_network(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    y_val: pd.Series
) -> Tuple[tuple, pd.DataFrame]:
    """
    Performs grid search over neural network depths and neurons per layer.
    Directly corresponds to Figure 8 in Poulos & Silva-Lopez.
    """
    print("\nRunning Neural Network Grid Search across architectures...")
    layers_options = [1, 2, 3, 5]
    neurons_options = [50, 100, 200, 300]
    
    results = []
    best_arch = (200, 100)
    best_val_r2 = -float('inf')
    
    for l in layers_options:
        for n in neurons_options:
            arch = tuple([n] * l)
            nn = NeuralNetworkModel(
                hidden_layer_sizes=arch,
                alpha=NN_ALPHA_DEFAULT,
                max_iter=200,
                random_state=RANDOM_SEED,
                early_stopping=True
            )
            nn.fit(X_train, y_train)
            pred = nn.predict(X_val)
            val_r2 = r2_score(y_val, pred)
            results.append({
                "num_layers": l,
                "num_neurons": n,
                "val_r2": val_r2
            })
            if val_r2 > best_val_r2:
                best_val_r2 = val_r2
                best_arch = arch
                
    grid_df = pd.DataFrame(results)
    print(f"Best NN Architecture: {best_arch} (Validation R² = {best_val_r2:.4f})")
    return best_arch, grid_df

def run_training_pipeline() -> Dict[str, Any]:
    """Trains all models, executes hyperparameter search, and saves model artifacts."""
    print("=" * 60)
    print("STARTING MODEL TRAINING PIPELINE")
    print("=" * 60)
    
    X_train, X_val, X_test, y_train, y_val, y_test, all_features, scaler = load_and_preprocess_data()
    
    with open(SELECTED_FEATURES_PATH, 'r') as f:
        selected_21 = json.load(f)
        
    print(f"Loaded {len(selected_21)} selected features for regression calibration.")
    
    # 1. Benchmark Model
    print("\n--- Training Benchmark Model (Distance d only) ---")
    benchmark = BenchmarkModel()
    benchmark.fit(X_train, y_train)
    joblib.dump(benchmark, MODELS_DIR / "benchmark_model.joblib")
    print(f"Benchmark fitted: Δθ = {benchmark.c1:.3f} + {benchmark.c2:.3f} * d")
    
    # 2. Ridge Regression Model
    print("\n--- Tuning & Training Ridge Regression ---")
    best_alpha, alpha_hist = tune_ridge_alpha(X_train[selected_21], y_train, X_val[selected_21], y_val)
    ridge_model = RidgeRegressionModel(alpha=best_alpha, random_state=RANDOM_SEED)
    ridge_model.fit(X_train[selected_21], y_train)
    joblib.dump(ridge_model, MODELS_DIR / "ridge_model.joblib")
    
    # 3. Neural Network Model
    print("\n--- Grid Searching & Training Neural Network ---")
    best_arch, grid_df = grid_search_neural_network(X_train[selected_21], y_train, X_val[selected_21], y_val)
    grid_df.to_csv(MODELS_DIR / "nn_gridsearch_results.csv", index=False)
    
    # Deep high-capacity model matching paper
    nn_model = NeuralNetworkModel(
        hidden_layer_sizes=best_arch,
        alpha=NN_ALPHA_DEFAULT,
        max_iter=300,
        random_state=RANDOM_SEED,
        early_stopping=True
    )
    nn_model.fit(X_train[selected_21], y_train)
    joblib.dump(nn_model, MODELS_DIR / "neural_network_model.joblib")
    
    # 4. Gradient Boosting Model (Benchmark Comparison)
    print("\n--- Training Gradient Boosting Baseline ---")
    gb_model = GradientBoostingModel(random_state=RANDOM_SEED)
    gb_model.fit(X_train[selected_21], y_train)
    joblib.dump(gb_model, MODELS_DIR / "gradient_boosting_model.joblib")
    
    print("\nAll models trained and saved to:", MODELS_DIR)
    return {
        "benchmark": benchmark,
        "ridge": ridge_model,
        "neural_network": nn_model,
        "gradient_boosting": gb_model,
        "best_alpha": best_alpha,
        "best_arch": best_arch
    }

if __name__ == "__main__":
    run_training_pipeline()
