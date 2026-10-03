"""
Feature selection using Backward and Forward analysis with Ridge Regression.
Directly implements Section 3.3 of Poulos & Silva-Lopez (Stanford).
"""

import json
import numpy as np
import pandas as pd
from typing import List, Tuple
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score
from src.config import SELECTED_FEATURES_PATH, RIDGE_ALPHA_DEFAULT
from src.data_preprocessing import load_and_preprocess_data

def backward_feature_ranking(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    alpha: float = RIDGE_ALPHA_DEFAULT
) -> List[Tuple[str, float]]:
    """
    Ranks features by decrease in validation R^2 when feature is removed.
    Larger drop in R^2 => more important feature.
    """
    # Baseline model with all features
    base_model = Ridge(alpha=alpha)
    base_model.fit(X_train, y_train)
    y_pred_base = base_model.predict(X_val)
    base_r2 = r2_score(y_val, y_pred_base)
    
    feature_drops = []
    all_features = list(X_train.columns)
    
    for feat in all_features:
        remaining_feats = [f for f in all_features if f != feat]
        model_sub = Ridge(alpha=alpha)
        model_sub.fit(X_train[remaining_feats], y_train)
        y_pred_sub = model_sub.predict(X_val[remaining_feats])
        r2_sub = r2_score(y_val, y_pred_sub)
        
        drop = base_r2 - r2_sub
        feature_drops.append((feat, drop))
        
    # Sort descending by importance (drop in R^2)
    feature_drops.sort(key=lambda x: x[1], reverse=True)
    return feature_drops

def forward_feature_selection(
    ranked_features: List[Tuple[str, float]],
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    alpha: float = RIDGE_ALPHA_DEFAULT,
    target_k: int = 21
) -> Tuple[List[str], List[float]]:
    """
    Iteratively adds features in ranked order and monitors validation R^2.
    Returns the top target_k features and history of R^2 values.
    """
    selected_features = []
    r2_history = []
    
    for feat, _ in ranked_features:
        candidate_set = selected_features + [feat]
        model = Ridge(alpha=alpha)
        model.fit(X_train[candidate_set], y_train)
        y_pred = model.predict(X_val[candidate_set])
        r2 = r2_score(y_val, y_pred)
        
        selected_features.append(feat)
        r2_history.append(r2)
        
        if len(selected_features) >= target_k:
            break
            
    return selected_features, r2_history

def run_feature_selection(target_features: int = 21, alpha: float = RIDGE_ALPHA_DEFAULT) -> List[str]:
    """Runs full backward-forward analysis pipeline and saves 21 features."""
    X_train, X_val, X_test, y_train, y_val, y_test, all_features, _ = load_and_preprocess_data()
    
    print(f"Running Backward Analysis on {len(all_features)} initial attributes...")
    ranked = backward_feature_ranking(X_train, y_train, X_val, y_val, alpha=alpha)
    
    print("\nTop 10 features from Backward Ranking:")
    for rank, (feat, drop) in enumerate(ranked[:10], 1):
        print(f"  {rank:2d}. {feat:<35} | ΔR² drop: {drop:+.5f}")
        
    print(f"\nRunning Forward Selection up to {target_features} features...")
    selected_21, r2_curve = forward_feature_selection(
        ranked, X_train, y_train, X_val, y_val, alpha=alpha, target_k=target_features
    )
    
    # Save selected features to disk
    with open(SELECTED_FEATURES_PATH, 'w') as f:
        json.dump(selected_21, f, indent=2)
        
    print(f"\nSuccessfully selected {len(selected_21)} features and saved to {SELECTED_FEATURES_PATH}")
    print(f"Final Validation R² with {target_features} features: {r2_curve[-1]:.4f}")
    
    return selected_21

if __name__ == "__main__":
    run_feature_selection()
