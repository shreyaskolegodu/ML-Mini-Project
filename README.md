# UE24CS352A - Machine Learning Mini-Project
# Detecting and Predicting Earthquake Ground Motion Directionality Patterns Using Machine Learning Tools

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Complete](https://img.shields.io/badge/Status-Complete-brightgreen.svg)]()

> **Course:** UE24CS352A - Machine Learning  
> **Reference Paper:** Alan Poulos & Rodrigo Silva-Lopez, *John A. Blume Earthquake Engineering Center, Stanford University*  
> **Topic:** Earthquake Ground Motion Directionality (RotD100 Orientation Angular Difference $\Delta\theta$)

---

## 📌 Executive Summary & Problem Formulation

In earthquake engineering and seismic risk assessment, the horizontal intensity of ground shaking strongly depends on azimuth. The maximum horizontal ground motion intensity is known as **RotD100**. Contemporary seismic codes (e.g., ASCE 7-16) and loss assessment frameworks conventionally assume that ground motion orientations between stations follow an **independent uniform distribution** over $[0^\circ, 180^\circ)$.

However, observations during shallow crustal earthquakes demonstrate that orientations are **spatially correlated** between recording sites that are close to each other ($d \le 5.0\text{ km}$). Assuming independence severely underestimates the probability of simultaneous destructive ground motion across distributed civil infrastructure (lifelines, bridges, and pipelines).

This project implements supervised machine learning models to predict the acute angular difference in orientation of maximum shaking, **$\Delta\theta \in [0^\circ, 90^\circ]$**, between two given recording sites $s_i$ and $s_j$ during an earthquake $E_k$:

$$\Delta\theta_{s_i, s_j}^k = f(s_i, s_j, E_k)$$

---

## 📁 Repository Structure

```plaintext
.
├── deliverables/
│   ├── ML_MiniProject_Writeup.pdf     # Official Two-Page Technical Write-up (Deliverable B)
│   ├── generate_report.py             # Automated ReportLab PDF generator script
│   ├── presentation_slides.docx       # Full Presentation Slides in Word (.docx) format (Deliverable 4)
│   ├── generate_slides_docx.py        # Automated python-docx presentation slides generator
│   ├── presentation_slides.html       # Interactive web-based presentation deck (Deliverable 4)
│   ├── PRESENTATION_SLIDES.md         # Markdown/Marp presentation slide deck
│   ├── model_performance_table.csv    # Evaluated quantitative metrics table
│   └── results_summary.json           # Raw evaluation metrics JSON
├── figures/                           # Generated publication figures matching the paper
│   ├── fig02_delta_theta_vs_distance.png
│   ├── fig03_delta_theta_vs_pga.png
│   ├── fig04_benchmark_scatter_train_test.png
│   ├── fig05_ridge_scatter_train_test.png
│   ├── fig06_ridge_regression_windowed_dist.png
│   ├── fig07_ridge_regression_windowed_pga.png
│   ├── fig08_nn_gridsearch_heatmap.png
│   ├── fig09_nn_scatter_train_test.png
│   ├── fig10_neural_network_windowed_dist.png
│   ├── fig11_neural_network_windowed_pga.png
│   └── fig12_model_comparison_bars.png
├── src/                               # Source code modules
│   ├── config.py                      # Global configurations, file paths, and seeds
│   ├── data_generator.py              # Calibrated NGA-West2 pairwise site generator
│   ├── data_preprocessing.py          # Scaling, one-hot encoding, and train/val/test splits
│   ├── feature_selection.py           # Backward-forward Ridge feature selection (21 features)
│   ├── models.py                      # Benchmark, Ridge, Neural Network, and Gradient Boosting
│   ├── train.py                       # Training pipeline & hyperparameter grid searches
│   ├── evaluate.py                    # Evaluation suite & figure generator (Figures 2 to 12)
│   └── app.py                         # Interactive live prediction engine & scenario tester
├── data/                              # Cached synthetic dataset & selected feature JSON
│   ├── nga_west2_paired_sites.csv     # 5,300 pairwise earthquake recording instances (71 features)
│   └── selected_features.json         # Top 21 selected features
├── models/                            # Serialized trained model weights & scaler
│   ├── benchmark_model.joblib
│   ├── ridge_model.joblib
│   ├── neural_network_model.joblib
│   ├── gradient_boosting_model.joblib
│   ├── scaler.joblib
│   └── nn_gridsearch_results.csv
├── main.py                            # Unified CLI entry point
├── requirements.txt                   # Dependency specifications
├── .gitignore                         # Git exclusion rules
└── README.md                          # Project documentation (this file)
```

---

## ⚙️ Environment Setup

### 1. Clone the Repository
```bash
git clone <YOUR_PRIVATE_GITHUB_REPO_URL>
cd "ML Project"
```

### 2. Create and Activate Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate    # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🚀 How to Run the Project

### Option A: Run Full End-to-End Pipeline
Executes data generation, feature selection, model training, evaluation, figure generation, and demo:
```bash
python main.py --pipeline
```

### Option B: Run Modular Steps

#### 1. Generate NGA-West2 Pairwise Dataset (~5,300 instances, 71 attributes)
```bash
python main.py --generate-data
```

#### 2. Execute Backward-Forward Feature Selection (Selects 21 optimal features)
```bash
python main.py --select-features
```

#### 3. Train Models & Perform Hyperparameter Grid Search
```bash
python main.py --train
```

#### 4. Evaluate Models & Generate Publication Figures (Figures 2 to 12)
```bash
python main.py --evaluate
```

#### 5. Run Live Interactive Demo (For Review & Demonstration Session)
```bash
python main.py --demo
```

#### 6. Custom Scenario Single-Point Prediction
```bash
python main.py --predict --dist 1.2 --pga 0.15 --mag 6.8 --vs30 420.0
```

---

## 📊 Summary of Experimental Results

Performance on the hold-out test set (10% test split, 530 unseen site pairs):

| Model Architecture | Input Features | Train $R^2$ | Test $R^2$ | Test MAE ($^\circ$) | Test RMSE ($^\circ$) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Benchmark (Linear)** | 1 Feature (Distance $d$) | 0.038 | 0.051 | 16.43$^\circ$ | 19.95$^\circ$ |
| **Ridge Regression ($L_2$)** | 21 Selected Features | 0.349 | **0.350** | **13.35$^\circ$** | **16.52$^\circ$** |
| **Deep Neural Network (MLP)** | 21 Selected Features | 0.381 | **0.328** | **13.56$^\circ$** | **16.79$^\circ$** |
| **Gradient Boosted Trees** | 21 Selected Features | 0.751 | 0.325 | 13.71$^\circ$ | 16.83$^\circ$ |

### Key Observations:
1. **Multivariable ML vs Distance Baseline:** Incorporating geotechnical ($V_{s30}$), source rupture, and shaking intensity features elevates $R^2$ from 0.051 to 0.350, reducing Mean Absolute Error from 16.43$^\circ$ to 13.35$^\circ$.
2. **Dominant Features:** Feature ranking identified **separation distance $d$** and **average Peak Ground Acceleration (PGA)** as the two most impactful variables governing directional correlation.
3. **Aleatoric Uncertainty:** Ground motion directionality possesses significant irreducible physical dispersion ($\sigma \approx 16^\circ$) caused by 3D basin geometry and wave scattering. While individual scatter is high, the models accurately reconstruct the conditional mean trend across both distance and PGA bins.

---

## 📄 Deliverables Summary

- **Deliverable A (Source Code):** Complete, modular, documented Python repository with CLI and unit-tested pipelines.
- **Deliverable B (Two-Page Write-up):** Compiled PDF located at `deliverables/ML_MiniProject_Writeup.pdf` satisfying all criteria in the assignment guidelines (problem statement, dataset details, approach, implementation overview, and conclusions in exactly 2 pages).
- **Deliverable 4 (Presentation & Demonstration):**
  - **Full Presentation Slides in Word (.docx)** located at [`deliverables/presentation_slides.docx`](file:///Users/shreyaskm/Documents/ML/ML%20Project/deliverables/presentation_slides.docx) with landscape slide formatting, embedded high-resolution figures, tables, and presenter notes.
  - Interactive HTML slide deck located at [`deliverables/presentation_slides.html`](file:///Users/shreyaskm/Documents/ML/ML%20Project/deliverables/presentation_slides.html).
  - Markdown slide deck located at [`deliverables/PRESENTATION_SLIDES.md`](file:///Users/shreyaskm/Documents/ML/ML%20Project/deliverables/PRESENTATION_SLIDES.md).
  - Interactive CLI demo executable via `python main.py --demo`.

---

## 👥 Hosting in a Private GitHub Repository

To push this repository to your private GitHub repo and share with faculty:

```bash
# 1. Initialize git and commit files
git init
git add .
git commit -m "Initial commit: Earthquake Ground Motion Directionality ML Mini-Project"

# 2. Add your private GitHub repository remote
git remote add origin https://github.com/<YOUR_USERNAME>/<YOUR_REPO_NAME>.git
git branch -M main
git push -u origin main
```
*Note: Ensure the repository is set to **Private** and invite the faculty and assigned Teaching Assistants under **Settings > Collaborators**.*

---

## 📖 References
1. Poulos, A., & Silva-Lopez, R. *Detecting and predicting earthquake ground motion directionality patterns using machine learning tools*. John A. Blume Earthquake Engineering Center, Stanford University.
2. Ancheta, T. D., et al. (2014). *NGA-West2 database*. Earthquake Spectra, 30(3):989–1005.
3. Boore, D. M. (2010). *Orientation-independent, nongeometric-mean measures of seismic intensity from two horizontal components of motion*. BSSA, 100(4):1830–1835.
4. American Society of Civil Engineers (2016). *Minimum design loads and associated criteria for buildings and other structures*. ASCE/SEI 7-16.
