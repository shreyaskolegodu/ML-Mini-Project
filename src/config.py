"""
Configuration and constants for Earthquake Ground Motion Directionality Project.
Based on Poulos & Silva-Lopez (Stanford University).
"""

import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
FIGURES_DIR = BASE_DIR / "figures"
DELIVERABLES_DIR = BASE_DIR / "deliverables"

for p in [DATA_DIR, MODELS_DIR, FIGURES_DIR, DELIVERABLES_DIR]:
    p.mkdir(parents=True, exist_ok=True)

DATA_PATH = DATA_DIR / "nga_west2_paired_sites.csv"
SELECTED_FEATURES_PATH = DATA_DIR / "selected_features.json"

# Random Seed for Reproducibility
RANDOM_SEED = 42

# Data Splitting
TRAIN_RATIO = 0.80
VAL_RATIO = 0.10
TEST_RATIO = 0.10

# Hyperparameter defaults matching paper
RIDGE_ALPHA_DEFAULT = 1.5
NN_ALPHA_DEFAULT = 0.1
NN_HIDDEN_LAYERS_DEFAULT = (400, 400, 300, 200, 100)  # High capacity deep MLP
NN_LEARNING_RATE_INIT = 0.001
NN_MAX_ITER = 300

# Plotting style
PLOT_STYLE = {
    "font.sans-serif": ["DejaVu Sans", "Helvetica", "Arial"],
    "axes.edgecolor": "#333333",
    "axes.linewidth": 0.8,
    "grid.color": "#e0e0e0",
    "grid.linestyle": "--",
    "grid.alpha": 0.7,
}
