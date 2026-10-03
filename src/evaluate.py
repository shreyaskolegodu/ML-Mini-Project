"""
Evaluation module and comprehensive visualization suite.
Generates all figures corresponding to Figures 2 through 11 in Poulos & Silva-Lopez,
plus quantitative comparison tables and residual analysis.
"""

import json
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, Any, List, Tuple
from pathlib import Path

from src.config import (
    FIGURES_DIR, DELIVERABLES_DIR, MODELS_DIR,
    DATA_PATH, SELECTED_FEATURES_PATH, PLOT_STYLE
)
from src.data_preprocessing import load_and_preprocess_data
from src.models import evaluate_predictions

# Apply consistent publication style
plt.style.use('default')
plt.rcParams.update(PLOT_STYLE)

def compute_binned_stats(
    x: np.ndarray,
    y: np.ndarray,
    num_bins: int = 25
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Computes bin centers, means, and 95% confidence intervals for moving averages."""
    bins = np.linspace(x.min(), x.max(), num_bins + 1)
    bin_centers = 0.5 * (bins[:-1] + bins[1:])
    means = []
    ci_lowers = []
    ci_uppers = []
    
    for i in range(len(bins) - 1):
        mask = (x >= bins[i]) & (x < bins[i + 1] if i < len(bins) - 2 else x <= bins[i + 1])
        vals = y[mask]
        if len(vals) > 2:
            m = np.mean(vals)
            se = np.std(vals, ddof=1) / np.sqrt(len(vals))
            ci = 1.96 * se
            means.append(m)
            ci_lowers.append(m - ci)
            ci_uppers.append(m + ci)
        else:
            means.append(np.nan)
            ci_lowers.append(np.nan)
            ci_uppers.append(np.nan)
            
    return bin_centers, np.array(means), np.array(ci_lowers), np.array(ci_uppers)

def plot_fig2_delta_theta_vs_distance(df: pd.DataFrame):
    """Figure 2: Δθ as a function of the distance between sites with moving average & 95% CI."""
    fig, ax = plt.subplots(figsize=(6, 4.5), dpi=300)
    
    # Scatter in background
    ax.scatter(df['distance_between_sites'], df['delta_theta'], color='#a6b8c7', alpha=0.35, s=12, label='Data')
    
    # Binned moving average
    x_c, m, ci_l, ci_u = compute_binned_stats(df['distance_between_sites'].values, df['delta_theta'].values, num_bins=35)
    valid = ~np.isnan(m)
    
    ax.errorbar(
        x_c[valid], m[valid], yerr=[m[valid] - ci_l[valid], ci_u[valid] - m[valid]],
        fmt='-o', color='black', ecolor='black', elinewidth=1.2, capsize=2.5, markersize=3.5,
        label='Moving average'
    )
    
    ax.set_xlabel('Distance between sites [km]', fontsize=11, fontweight='medium')
    ax.set_ylabel('Δθ [degrees]', fontsize=11, fontweight='medium')
    ax.set_xlim(0, 5.0)
    ax.set_ylim(0, 95)
    ax.set_yticks([0, 15, 30, 45, 60, 75, 90])
    ax.set_yticklabels(['0°', '15°', '30°', '45°', '60°', '75°', '90°'])
    ax.legend(frameon=True, facecolor='white', framealpha=0.9, loc='upper left')
    ax.set_title(r'$\mathbf{Figure\ 2:}\ \Delta\theta$ as a function of distance between sites', fontsize=11)
    
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "fig02_delta_theta_vs_distance.png")
    plt.close(fig)

def plot_fig3_delta_theta_vs_pga(df: pd.DataFrame):
    """Figure 3: Δθ as a function of average PGA with moving average & 95% CI."""
    fig, ax = plt.subplots(figsize=(6, 4.5), dpi=300)
    
    ax.scatter(df['average_pga'], df['delta_theta'], color='#a6b8c7', alpha=0.35, s=12, label='Data')
    
    pga_mask = df['average_pga'] <= 0.22
    x_c, m, ci_l, ci_u = compute_binned_stats(df.loc[pga_mask, 'average_pga'].values, df.loc[pga_mask, 'delta_theta'].values, num_bins=25)
    valid = ~np.isnan(m)
    
    ax.errorbar(
        x_c[valid], m[valid], yerr=[m[valid] - ci_l[valid], ci_u[valid] - m[valid]],
        fmt='-o', color='black', ecolor='black', elinewidth=1.2, capsize=2.5, markersize=3.5,
        label='Moving average'
    )
    
    ax.set_xlabel('Average peak ground acceleration [g]', fontsize=11, fontweight='medium')
    ax.set_ylabel('Δθ [degrees]', fontsize=11, fontweight='medium')
    ax.set_xlim(0.0, 0.22)
    ax.set_ylim(0, 95)
    ax.set_yticks([0, 15, 30, 45, 60, 75, 90])
    ax.set_yticklabels(['0°', '15°', '30°', '45°', '60°', '75°', '90°'])
    ax.legend(frameon=True, facecolor='white', framealpha=0.9, loc='upper right')
    ax.set_title(r'$\mathbf{Figure\ 3:}\ \Delta\theta$ as a function of average PGA', fontsize=11)
    
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "fig03_delta_theta_vs_pga.png")
    plt.close(fig)

def plot_scatter_train_test(
    y_tr_true: np.ndarray, y_tr_pred: np.ndarray,
    y_te_true: np.ndarray, y_te_pred: np.ndarray,
    model_name: str, r2_tr: float, r2_te: float,
    fig_filename: str, fig_title: str
):
    """Plots side-by-side Train and Test True vs Predicted scatter matching Figures 4, 5, 9."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.5, 4.2), dpi=300)
    
    # Train
    ax1.scatter(y_tr_true, y_tr_pred, color='#1f77b4', alpha=0.35, s=14, edgecolors='none')
    ax1.plot([0, 90], [0, 90], '--', color='red', alpha=0.7, linewidth=1.5)
    ax1.set_title(f'Training data, $R^2$ = {r2_tr:.4f}', fontsize=11, fontweight='medium')
    ax1.set_xlabel('True Δθ', fontsize=10)
    ax1.set_ylabel('Predicted Δθ', fontsize=10)
    ax1.set_xlim(0, 90)
    ax1.set_ylim(0, 90)
    ax1.grid(True, alpha=0.3)
    
    # Test
    ax2.scatter(y_te_true, y_te_pred, color='#1f77b4', alpha=0.45, s=14, edgecolors='none')
    ax2.plot([0, 90], [0, 90], '--', color='red', alpha=0.7, linewidth=1.5)
    ax2.set_title(f'Test data, $R^2$ = {r2_te:.4f}', fontsize=11, fontweight='medium')
    ax2.set_xlabel('True Δθ', fontsize=10)
    ax2.set_ylabel('Predicted Δθ', fontsize=10)
    ax2.set_xlim(0, 90)
    ax2.set_ylim(0, 90)
    ax2.grid(True, alpha=0.3)
    
    fig.suptitle(fig_title, fontsize=12, y=1.02)
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / fig_filename)
    plt.close(fig)

def plot_windowed_comparisons(
    x_dist: np.ndarray, x_pga: np.ndarray,
    y_true: np.ndarray, y_pred: np.ndarray,
    model_name: str,
    fig_num_dist: int, fig_num_pga: int
):
    """
    Plots windowed average comparison of True vs Predicted over Distance and PGA
    matching Figures 6, 7, 10, 11.
    """
    # 1. Over Distance
    fig, ax = plt.subplots(figsize=(6, 4.2), dpi=300)
    x_c, m_true, _, _ = compute_binned_stats(x_dist, y_true, num_bins=20)
    _, m_pred, _, _ = compute_binned_stats(x_dist, y_pred, num_bins=20)
    valid = ~np.isnan(m_true) & ~np.isnan(m_pred)
    
    ax.plot(x_c[valid], m_true[valid], '-o', color='#e67e22', label='Moving average of data', linewidth=1.8, markersize=4.5)
    ax.plot(x_c[valid], m_pred[valid], '-s', color='#2980b9', label='Moving average of model', linewidth=1.8, markersize=4.5)
    ax.set_xlabel('Distance between sites [km]', fontsize=11)
    ax.set_ylabel('Δθ [degrees]', fontsize=11)
    ax.set_xlim(0, 5.0)
    ax.set_ylim(10, 70)
    ax.grid(True, alpha=0.3)
    ax.legend(frameon=True, facecolor='white', framealpha=0.9)
    ax.set_title(f'Figure {fig_num_dist}: Windowed average over distance for {model_name}', fontsize=11)
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / f"fig{fig_num_dist:02d}_{model_name.lower().replace(' ', '_')}_windowed_dist.png")
    plt.close(fig)
    
    # 2. Over PGA
    fig, ax = plt.subplots(figsize=(6, 4.2), dpi=300)
    mask = x_pga <= 0.20
    x_c, m_true, _, _ = compute_binned_stats(x_pga[mask], y_true[mask], num_bins=12)
    _, m_pred, _, _ = compute_binned_stats(x_pga[mask], y_pred[mask], num_bins=12)
    valid = ~np.isnan(m_true) & ~np.isnan(m_pred)
    
    ax.plot(x_c[valid], m_true[valid], '-o', color='#e67e22', label='Moving average of data', linewidth=1.8, markersize=4.5)
    ax.plot(x_c[valid], m_pred[valid], '-s', color='#2980b9', label='Moving average of model', linewidth=1.8, markersize=4.5)
    ax.set_xlabel('Average of PGA [g]', fontsize=11)
    ax.set_ylabel('Δθ [degrees]', fontsize=11)
    ax.set_xlim(0.0, 0.20)
    ax.set_ylim(10, 60)
    ax.grid(True, alpha=0.3)
    ax.legend(frameon=True, facecolor='white', framealpha=0.9)
    ax.set_title(f'Figure {fig_num_pga}: Windowed average over PGA for {model_name}', fontsize=11)
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / f"fig{fig_num_pga:02d}_{model_name.lower().replace(' ', '_')}_windowed_pga.png")
    plt.close(fig)

def plot_nn_gridsearch_heatmap():
    """Figure 8: Gridsearch over hyperparameters of the neural network."""
    csv_path = MODELS_DIR / "nn_gridsearch_results.csv"
    if not csv_path.exists():
        return
    grid_df = pd.read_csv(csv_path)
    pivot = grid_df.pivot(index="num_neurons", columns="num_layers", values="val_r2")
    
    fig, ax = plt.subplots(figsize=(6.5, 4.8), dpi=300)
    im = ax.imshow(pivot.values, cmap='viridis', origin='lower', aspect='auto')
    
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Coefficient of determination ($R^2$)', fontsize=10)
    
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)
    
    ax.set_xlabel('Number of Layers', fontsize=11)
    ax.set_ylabel('Number of Neurons', fontsize=11)
    ax.set_title(r'$\mathbf{Figure\ 8:}$ Gridsearch over hyperparameters of the neural network', fontsize=11)
    
    # Highlight maximum
    max_idx = np.unravel_index(np.argmax(pivot.values), pivot.values.shape)
    ax.scatter(max_idx[1], max_idx[0], marker='*', color='#e74c3c', s=220, edgecolors='white', label='Optimal model')
    ax.legend(loc='lower right', frameon=True, facecolor='white', framealpha=0.85)
    
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "fig08_nn_gridsearch_heatmap.png")
    plt.close(fig)

def plot_model_comparison_bars(results: Dict[str, Dict[str, float]]):
    """Summary bar chart comparing all models."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.2), dpi=300)
    
    models = list(results.keys())
    r2_scores = [results[m]['test_r2'] for m in models]
    mae_scores = [results[m]['test_mae'] for m in models]
    
    colors = ['#7f8c8d', '#2980b9', '#27ae60', '#8e44ad']
    
    bars1 = ax1.bar(models, r2_scores, color=colors, width=0.55, edgecolor='black', linewidth=0.8)
    ax1.set_ylabel('Test $R^2$ (higher is better)', fontsize=11)
    ax1.set_title('Predictive Accuracy ($R^2$)', fontsize=11, fontweight='medium')
    ax1.set_ylim(0, max(r2_scores) * 1.25)
    for bar in bars1:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2.0, yval + 0.012, f'{yval:.3f}', ha='center', va='bottom', fontsize=9.5, fontweight='bold')
    ax1.set_xticks(range(len(models)))
    ax1.set_xticklabels(models, rotation=15, ha='right', fontsize=9.5)
    ax1.grid(axis='y', alpha=0.3)
    
    bars2 = ax2.bar(models, mae_scores, color=colors, width=0.55, edgecolor='black', linewidth=0.8)
    ax2.set_ylabel('Test MAE [degrees] (lower is better)', fontsize=11)
    ax2.set_title('Mean Absolute Error (degrees)', fontsize=11, fontweight='medium')
    ax2.set_ylim(0, max(mae_scores) * 1.25)
    for bar in bars2:
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2.0, yval + 0.5, f'{yval:.1f}°', ha='center', va='bottom', fontsize=9.5, fontweight='bold')
    ax2.set_xticks(range(len(models)))
    ax2.set_xticklabels(models, rotation=15, ha='right', fontsize=9.5)
    ax2.grid(axis='y', alpha=0.3)
    
    fig.suptitle('Model Evaluation & Benchmark Comparison', fontsize=12, y=1.02)
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "fig12_model_comparison_bars.png")
    plt.close(fig)

def run_evaluation() -> Dict[str, Any]:
    """Runs complete evaluation suite, generates plots and metrics tables."""
    print("=" * 60)
    print("RUNNING COMPREHENSIVE EVALUATION AND FIGURE GENERATION")
    print("=" * 60)
    
    # 1. Load data
    df = pd.read_csv(DATA_PATH)
    X_train, X_val, X_test, y_train, y_val, y_test, _, _ = load_and_preprocess_data()
    
    with open(SELECTED_FEATURES_PATH) as f:
        selected_21 = json.load(f)
        
    # 2. Load trained models
    bench = joblib.load(MODELS_DIR / "benchmark_model.joblib")
    ridge = joblib.load(MODELS_DIR / "ridge_model.joblib")
    nn = joblib.load(MODELS_DIR / "neural_network_model.joblib")
    gb = joblib.load(MODELS_DIR / "gradient_boosting_model.joblib")
    
    # 3. Predict Train & Test
    preds = {
        "Benchmark": {
            "train": bench.predict(X_train),
            "test": bench.predict(X_test)
        },
        "Ridge regression": {
            "train": ridge.predict(X_train[selected_21]),
            "test": ridge.predict(X_test[selected_21])
        },
        "Neural network": {
            "train": nn.predict(X_train[selected_21]),
            "test": nn.predict(X_test[selected_21])
        },
        "Gradient boosting": {
            "train": gb.predict(X_train[selected_21]),
            "test": gb.predict(X_test[selected_21])
        }
    }
    
    # 4. Compute Metrics Table
    results = {}
    table_rows = []
    
    for name, p in preds.items():
        tr_stats = evaluate_predictions(y_train.values, p["train"])
        te_stats = evaluate_predictions(y_test.values, p["test"])
        results[name] = {
            "train_r2": tr_stats["r2"],
            "train_mae": tr_stats["mae"],
            "test_r2": te_stats["r2"],
            "test_mae": te_stats["mae"],
            "test_rmse": te_stats["rmse"],
            "test_corr": te_stats["correlation"]
        }
        table_rows.append({
            "Model": name,
            "Train R²": f"{tr_stats['r2']:.4f}",
            "Test R²": f"{te_stats['r2']:.4f}",
            "Train MAE (°)": f"{tr_stats['mae']:.2f}",
            "Test MAE (°)": f"{te_stats['mae']:.2f}",
            "Test RMSE (°)": f"{te_stats['rmse']:.2f}"
        })
        
    results_df = pd.DataFrame(table_rows)
    results_df.to_csv(DELIVERABLES_DIR / "model_performance_table.csv", index=False)
    with open(DELIVERABLES_DIR / "results_summary.json", 'w') as f:
        json.dump(results, f, indent=2)
        
    print("\n" + "=" * 70)
    print("Table 1: Performance metrics of each model (Benchmark comparison)")
    print("=" * 70)
    print(results_df.to_string(index=False))
    print("=" * 70)
    
    # 5. Generate Figures
    print("\nGenerating Figures...")
    
    # Figure 2 & 3: Raw trend curves
    plot_fig2_delta_theta_vs_distance(df)
    plot_fig3_delta_theta_vs_pga(df)
    print("  ✓ Figure 2 & 3: Distance and PGA moving averages saved.")
    
    # Figures 4, 5, 9: Train vs Test scatter
    plot_scatter_train_test(
        y_train.values, preds["Benchmark"]["train"],
        y_test.values, preds["Benchmark"]["test"],
        "Benchmark", results["Benchmark"]["train_r2"], results["Benchmark"]["test_r2"],
        "fig04_benchmark_scatter_train_test.png",
        "Figure 4: True vs predicted values by linear regression benchmark"
    )
    plot_scatter_train_test(
        y_train.values, preds["Ridge regression"]["train"],
        y_test.values, preds["Ridge regression"]["test"],
        "Ridge regression", results["Ridge regression"]["train_r2"], results["Ridge regression"]["test_r2"],
        "fig05_ridge_scatter_train_test.png",
        "Figure 5: True vs predicted values by ridge linear regression"
    )
    plot_scatter_train_test(
        y_train.values, preds["Neural network"]["train"],
        y_test.values, preds["Neural network"]["test"],
        "Neural network", results["Neural network"]["train_r2"], results["Neural network"]["test_r2"],
        "fig09_nn_scatter_train_test.png",
        "Figure 9: True vs predicted values by the neural network"
    )
    print("  ✓ Figure 4, 5, 9: True vs Predicted scatter plots saved.")
    
    # Figures 6, 7: Ridge windowed comparison
    test_idx = X_test.index
    test_raw = df.loc[test_idx]
    plot_windowed_comparisons(
        test_raw['distance_between_sites'].values,
        test_raw['average_pga'].values,
        y_test.values, preds["Ridge regression"]["test"],
        "Ridge regression", 6, 7
    )
    print("  ✓ Figure 6 & 7: Ridge windowed average comparisons saved.")
    
    # Figure 8: Neural Network Grid Search
    plot_nn_gridsearch_heatmap()
    print("  ✓ Figure 8: Neural Network Grid Search heatmap saved.")
    
    # Figures 10, 11: NN windowed comparison
    plot_windowed_comparisons(
        test_raw['distance_between_sites'].values,
        test_raw['average_pga'].values,
        y_test.values, preds["Neural network"]["test"],
        "Neural network", 10, 11
    )
    print("  ✓ Figure 10 & 11: Neural Network windowed average comparisons saved.")
    
    # Figure 12: Summary bars
    plot_model_comparison_bars(results)
    print("  ✓ Figure 12: Model comparison bar chart saved.")
    
    print(f"\nAll publication figures successfully written to: {FIGURES_DIR}")
    return results

if __name__ == "__main__":
    run_evaluation()
