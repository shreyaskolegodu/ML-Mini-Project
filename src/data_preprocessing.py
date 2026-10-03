"""
Data preprocessing, feature encoding, scaling, and train/val/test splitting.
Follows methodology from Poulos & Silva-Lopez (Stanford).
"""

import pandas as pd
import numpy as np
import json
import joblib
from typing import Tuple, List, Dict
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from src.config import DATA_PATH, MODELS_DIR, RANDOM_SEED, TRAIN_RATIO, VAL_RATIO, TEST_RATIO

def load_and_preprocess_data(
    filepath: str = DATA_PATH,
    seed: int = RANDOM_SEED
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, pd.Series, List[str], StandardScaler]:
    """
    Loads dataset, performs one-hot encoding on categorical variables,
    splits into 80% train, 10% val, 10% test, and scales numerical features.
    
    Returns:
        X_train_scaled, X_val_scaled, X_test_scaled,
        y_train, y_val, y_test,
        feature_names, scaler
    """
    df = pd.read_csv(filepath)
    
    # Target variable
    y = df['delta_theta']
    
    # Drop target and event identifier
    drop_cols = ['delta_theta', 'eq_id']
    X_raw = df.drop(columns=[col for col in drop_cols if col in df.columns])
    
    # Categorical columns to one-hot encode
    cat_cols = ['focal_mechanism', 's1_nehrp', 's2_nehrp']
    existing_cat = [c for c in cat_cols if c in X_raw.columns]
    
    X_encoded = pd.get_dummies(X_raw, columns=existing_cat, drop_first=True, dtype=float)
    
    feature_names = list(X_encoded.columns)
    
    # 80% train, 10% val, 10% test
    # First split off 80% train and 20% temp
    X_train_df, X_temp_df, y_train, y_temp = train_test_split(
        X_encoded, y, test_size=(1.0 - TRAIN_RATIO), random_state=seed
    )
    
    # Then split temp 50-50 into val and test (each 10% of total)
    val_fraction_of_temp = VAL_RATIO / (VAL_RATIO + TEST_RATIO)
    X_val_df, X_test_df, y_val, y_test = train_test_split(
        X_temp_df, y_temp, test_size=(1.0 - val_fraction_of_temp), random_state=seed
    )
    
    # Standardize numerical features to zero mean and unit variance
    scaler = StandardScaler()
    X_train_scaled = pd.DataFrame(
        scaler.fit_transform(X_train_df),
        columns=feature_names,
        index=X_train_df.index
    )
    X_val_scaled = pd.DataFrame(
        scaler.transform(X_val_df),
        columns=feature_names,
        index=X_val_df.index
    )
    X_test_scaled = pd.DataFrame(
        scaler.transform(X_test_df),
        columns=feature_names,
        index=X_test_df.index
    )
    
    # Save scaler
    joblib.dump(scaler, MODELS_DIR / "scaler.joblib")
    
    return X_train_scaled, X_val_scaled, X_test_scaled, y_train, y_val, y_test, feature_names, scaler

if __name__ == "__main__":
    X_tr, X_va, X_te, y_tr, y_va, y_te, f_names, _ = load_and_preprocess_data()
    print(f"Dataset split summary:")
    print(f"  Training set:   {X_tr.shape[0]} samples, {X_tr.shape[1]} features")
    print(f"  Validation set: {X_va.shape[0]} samples")
    print(f"  Test set:       {X_te.shape[0]} samples")
