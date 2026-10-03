"""
Interactive demonstration and prediction module.
Provides live inference for site-pair ground motion directionality prediction
during review and demonstration sessions.
"""

import sys
import json
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any

from src.config import MODELS_DIR, SELECTED_FEATURES_PATH, DATA_PATH

class DirectionalityPredictor:
    def __init__(self):
        self.scaler = joblib.load(MODELS_DIR / "scaler.joblib")
        self.benchmark = joblib.load(MODELS_DIR / "benchmark_model.joblib")
        self.ridge = joblib.load(MODELS_DIR / "ridge_model.joblib")
        self.nn = joblib.load(MODELS_DIR / "neural_network_model.joblib")
        
        with open(SELECTED_FEATURES_PATH) as f:
            self.selected_features = json.load(f)
            
        # Load raw dataset to establish unscaled median baseline
        df = pd.read_csv(DATA_PATH)
        drop_cols = ['delta_theta', 'eq_id']
        X_raw = df.drop(columns=[c for c in drop_cols if c in df.columns])
        cat_cols = ['focal_mechanism', 's1_nehrp', 's2_nehrp']
        existing_cat = [c for c in cat_cols if c in X_raw.columns]
        X_encoded = pd.get_dummies(X_raw, columns=existing_cat, drop_first=True, dtype=float)
        
        self.feature_columns = list(X_encoded.columns)
        self.raw_medians = X_encoded.median().to_dict()
        
    def predict(
        self,
        distance_km: float,
        avg_pga: float = 0.08,
        magnitude: float = 6.5,
        avg_vs30: float = 380.0,
        diff_vs30: float = 80.0,
        strike_angle: float = 120.0,
        dip_angle: float = 80.0
    ) -> Dict[str, Any]:
        """Runs predictions across all models for a specific station-pair scenario."""
        row = dict(self.raw_medians)
        row['distance_between_sites'] = distance_km
        row['average_pga'] = avg_pga
        row['s1_pga'] = avg_pga * 1.05
        row['s2_pga'] = avg_pga * 0.95
        row['earthquake_magnitude'] = magnitude
        row['average_vs30'] = avg_vs30
        row['diff_vs30'] = diff_vs30
        row['strike_angle'] = strike_angle
        row['dip_angle'] = dip_angle
        row['log_pga_avg'] = np.log10(avg_pga + 1e-4)
        row['radiation_strike_diff'] = float(np.abs(np.cos(np.radians(strike_angle))))
        row['radiation_dip_factor'] = float(np.sin(np.radians(dip_angle)))
        
        df_unscaled = pd.DataFrame([[row[c] for c in self.feature_columns]], columns=self.feature_columns)
        
        # Scale for Ridge and NN
        scaled_values = self.scaler.transform(df_unscaled)
        df_scaled = pd.DataFrame(scaled_values, columns=self.feature_columns)
        
        # Inferences
        p_bench = float(self.benchmark.predict(df_unscaled)[0])
        p_ridge = float(self.ridge.predict(df_scaled[self.selected_features])[0])
        p_nn = float(self.nn.predict(df_scaled[self.selected_features])[0])
        
        # Physical regime
        if distance_km < 1.5 and avg_pga > 0.10:
            regime = "High Wave Coherence & Strong Directivity (Strong Orientation Alignment)"
        elif distance_km > 3.5 or avg_pga < 0.04:
            regime = "High Wave Dispersion / Scattered Wavefield (Decorrelated Orientations)"
        else:
            regime = "Intermediate Transition Zone"
            
        return {
            "inputs": {
                "distance_km": distance_km,
                "avg_pga_g": avg_pga,
                "magnitude": magnitude,
                "avg_vs30_ms": avg_vs30,
                "diff_vs30_ms": diff_vs30
            },
            "predictions": {
                "Benchmark (Distance only)": p_bench,
                "Ridge Regression": p_ridge,
                "Deep Neural Network (MLP)": p_nn
            },
            "regime": regime
        }

def run_interactive_demo():
    """Runs interactive demonstration in terminal."""
    predictor = DirectionalityPredictor()
    
    scenarios = [
        {
            "name": "Scenario A: Near-Field Strong Shaking (Close Sites, High PGA)",
            "dist": 0.75, "pga": 0.18, "mag": 6.9, "vs30": 420.0, "diff_vs30": 30.0
        },
        {
            "name": "Scenario B: Mid-Range Separation & Moderate Intensity",
            "dist": 2.50, "pga": 0.08, "mag": 6.3, "vs30": 360.0, "diff_vs30": 110.0
        },
        {
            "name": "Scenario C: Far Separation & Weak Shaking (Scattering Dominant)",
            "dist": 4.80, "pga": 0.02, "mag": 5.4, "vs30": 290.0, "diff_vs30": 180.0
        }
    ]
    
    print("\n" + "=" * 76)
    print("EARTHQUAKE GROUND MOTION DIRECTIONALITY PREDICTION - LIVE DEMO")
    print("=" * 76)
    print("Predicting Absolute Angular Difference Δθ [0°, 90°] Between Recording Sites\n")
    
    for sc in scenarios:
        res = predictor.predict(
            distance_km=sc["dist"],
            avg_pga=sc["pga"],
            magnitude=sc["mag"],
            avg_vs30=sc["vs30"],
            diff_vs30=sc["diff_vs30"]
        )
        print(f"▶ {sc['name']}")
        print(f"  Parameters: Distance={sc['dist']} km | PGA={sc['pga']} g | Mw={sc['mag']} | Vs30={sc['vs30']} m/s")
        print(f"  Physical Regime: {res['regime']}")
        print("  Predicted Directionality Difference (Δθ):")
        for model_name, val in res["predictions"].items():
            bar = "█" * int(val / 2.5) + "░" * (36 - int(val / 2.5))
            print(f"    • {model_name:<28}: {val:5.1f}° | [{bar}]")
        print("-" * 76)
        
    print("\nLive demo completed successfully.\n")

if __name__ == "__main__":
    run_interactive_demo()
