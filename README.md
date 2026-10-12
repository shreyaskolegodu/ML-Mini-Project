# Earthquake Ground Motion Directionality ML Pipeline

This project predicts the angular difference in maximum horizontal ground-motion orientation between two nearby earthquake recording sites. The target variable is `delta_theta`, measured in degrees and bounded between 0 and 90 degrees.

The project implements synthetic NGA-West2-style paired-site data generation, feature selection, regression-model training, evaluation, visualization, and scenario prediction.

## Quick Start

The complete workflow is controlled from one notebook:

1. Open [earthquake_directionality_pipeline.ipynb](earthquake_directionality_pipeline.ipynb) in VS Code or Jupyter.
2. Select the project virtual environment as the notebook kernel.
3. Run all cells from top to bottom.

The notebook executes the following stages:

1. Generate the synthetic paired-site dataset.
2. Select the 21 most useful predictor features.
3. Train and tune all regression models.
4. Evaluate the models and generate publication figures.
5. Run three demonstration scenarios.
6. Preserve the existing PDF report without regenerating it.
7. Run an example single-site-pair prediction.

All executable project code is contained in the notebook. The `src/` directory is not required and can be removed before pushing the project to Git. The existing PDF is preserved and is not rebuilt during **Run All**.

## Project Structure

```text
.
├── earthquake_directionality_pipeline.ipynb  # Main entry point: run all cells
├── requirements.txt                          # Python dependencies
├── deliverables/
│   ├── ML_MiniProject_Writeup.pdf            # Existing PDF deliverable; not regenerated
│   ├── model_performance_table.csv           # Generated evaluation table
│   └── results_summary.json                  # Generated evaluation summary
├── data/                                     # Generated dataset and selected features
├── models/                                   # Generated models and preprocessing artifacts
└── figures/                                  # Generated evaluation figures
```

The `data/`, `models/`, and `figures/` directories are created automatically during execution. They do not need to exist before the first notebook run.

## Environment Setup

Python 3.10 or newer is recommended.

### Create a virtual environment

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Register the environment as a notebook kernel if it is not already visible in VS Code:

```bash
python -m ipykernel install --user --name earthquake-directionality --display-name "Python (Earthquake Directionality)"
```

## Running the Notebook

Open the notebook from the repository root. The first code cell initializes all paths, imports, data-generation logic, preprocessing, model classes, training, evaluation, figure-generation, and prediction helpers directly in the notebook.

Use **Run All** to execute the full workflow. The data-generation and feature-selection stages are intentionally rerun each time so that the complete pipeline is reproducible from a clean workspace. The project uses a fixed random seed of 42.

The neural-network grid search and feature-selection stage can take several minutes depending on the computer and installed scikit-learn version.

## Pipeline Details

### 1. Dataset generation

The notebook creates approximately 5,300 paired recording-site examples using synthetic earthquake source, rupture, site, distance, and ground-motion variables. It creates the target `delta_theta` from distance, PGA, site-condition differences, rupture properties, nonlinear physical interactions, and random ground-motion variability.

The generated dataset is saved as:

```text
data/nga_west2_paired_sites.csv
```

### 2. Preprocessing

The notebook preprocessing functions perform the following operations:

- Loads the generated CSV file.
- Removes `delta_theta` from the predictors and excludes `eq_id` as an identifier.
- One-hot encodes `focal_mechanism`, `s1_nehrp`, and `s2_nehrp`.
- Splits the data into 80% training, 10% validation, and 10% test sets.
- Standardizes the predictor columns using a training-only `StandardScaler`.
- Saves the scaler to `models/scaler.joblib`.

### 3. Feature selection

The notebook uses Ridge regression in two stages:

- Backward ranking measures the validation $R^2$ decrease caused by removing each feature.
- Forward selection adds features in ranked order until 21 predictors have been selected.

The selected feature names are saved to:

```text
data/selected_features.json
```

### 4. Model training

The notebook trains four models:

- **Benchmark linear model:** uses only inter-site distance.
- **Ridge regression:** uses the 21 selected features and tunes the regularization parameter on the validation set.
- **Neural network:** uses an `MLPRegressor` and searches across several layer depths and widths.
- **Gradient boosting:** uses `HistGradientBoostingRegressor` as an additional comparison model.

Model files are saved under `models/`:

```text
models/benchmark_model.joblib
models/ridge_model.joblib
models/neural_network_model.joblib
models/gradient_boosting_model.joblib
models/scaler.joblib
models/nn_gridsearch_results.csv
```

### 5. Evaluation and figures

The notebook evaluation cell calculates training and test metrics including:

- $R^2$
- Mean absolute error
- Root mean squared error
- Prediction correlation

The metrics are saved to:

```text
deliverables/model_performance_table.csv
deliverables/results_summary.json
```

The evaluation cell generates figures 2 through 12 directly from notebook code and displays them inline while also saving PNG copies in `figures/`. These include distance and PGA trends, train/test prediction scatter plots, windowed comparisons, the neural-network grid-search heatmap, and the model-comparison bar chart.

### 6. Demonstration and prediction

The notebook prediction cell uses the trained models and saved scaler to run three predefined scenarios:

- Near-field strong shaking
- Mid-range separation with moderate intensity
- Far separation with weak shaking

The final notebook cell demonstrates a custom prediction using:

- Inter-site distance
- Average PGA
- Earthquake magnitude
- Average Vs30

The prediction returns model estimates and a qualitative physical regime.

### 7. Existing PDF report

The existing two-page technical report is preserved at:

```text
deliverables/ML_MiniProject_Writeup.pdf
```

The notebook prints the report location but does not regenerate the PDF during **Run All**.

## Expected Outputs

After a successful Run All, the workspace should contain:

```text
data/nga_west2_paired_sites.csv
data/selected_features.json
models/*.joblib
models/nn_gridsearch_results.csv
figures/fig02_*.png
figures/fig03_*.png
...
figures/fig12_*.png
deliverables/model_performance_table.csv
deliverables/results_summary.json
deliverables/ML_MiniProject_Writeup.pdf
```

## Re-running From a Clean Workspace

The notebook can be run after deleting generated outputs. Only the notebook and dependency manifest are needed:

```bash
rm -rf data models figures
rm -f deliverables/model_performance_table.csv deliverables/results_summary.json
```

Then reopen the notebook and select **Run All**. The notebook recreates the output directories and regenerates the dataset, models, metrics, and figures. The existing PDF is left untouched.

## Troubleshooting

### `FileNotFoundError` for a dataset or model

Run the notebook cells from the beginning. Training and evaluation depend on artifacts created by earlier cells.

### Existing PDF is missing

The PDF is an existing deliverable and is intentionally not generated by the notebook. Restore `deliverables/ML_MiniProject_Writeup.pdf` separately if it is removed.

### Notebook kernel is unavailable

Install and register Jupyter support in the active environment:

```bash
python -m pip install jupyter ipykernel
python -m ipykernel install --user --name earthquake-directionality --display-name "Python (Earthquake Directionality)"
```

### Results differ slightly across machines

The project fixes its NumPy and scikit-learn random seeds, but differences can still occur across library versions, operating systems, and numerical backends. Treat small metric differences as expected; use the same dependency versions when exact reproduction is important.

## Reproducibility and Scope

This project uses synthetically generated data designed to reproduce the structure and physical trends of a paired-site NGA-West2-style dataset. It is intended for the associated machine-learning project workflow and demonstration, not as a replacement for analysis of the original NGA-West2 recordings.

The target is an angular difference in the range $[0^\circ, 90^\circ]$. Predictions are clipped to that interval by the model wrappers.
