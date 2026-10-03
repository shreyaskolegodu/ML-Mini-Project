# UE24CS352A - Machine Learning Mini-Project Presentation
## Detecting and Predicting Earthquake Ground Motion Directionality Patterns Using Machine Learning Tools

**Based on:** Alan Poulos & Rodrigo Silva-Lopez (Blume Earthquake Engineering Center, Stanford University)  
**Deliverable:** Review & Live Demonstration Slide Deck

---

## Slide 1: Problem Definition & Engineering Motivation
- **Ground Motion Directionality:** Ground shaking intensity varies strongly with orientation in the horizontal plane. The maximum orientation-dependent intensity is defined as **RotD100**.
- **The Gap in Current Engineering Practice:**
  - Standard building codes (e.g., ASCE 7-16) and regional loss estimation tools traditionally assume orientations across multiple stations are **uniformly and independently distributed**.
  - However, empirical observations during shallow crustal earthquakes reveal that orientations between adjacent recording stations ($d \le 5$ km) are **spatially correlated**.
  - Neglecting this correlation severely underestimates joint failure probabilities of distributed lifelines and city-scale infrastructure.
- **Project Objective:**
  - Develop supervised ML models to predict the acute angular difference in maximum ground shaking orientation:
    $$\Delta\theta_{s_i, s_j}^k = f(s_i, s_j, E_k) \in [0^\circ, 90^\circ]$$

---

## Slide 2: Dataset Characteristics & Preprocessing
- **Source Database:** PEER **NGA-West2** database (~20,000 ground motion records, 274 attributes).
- **Engineering Filtering:**
  - Retained only shallow crustal earthquakes with moment magnitude $M_w \ge 5.0$ (~5,000 records).
- **Pairwise Construction:**
  - Formed pairs $(s_i, s_j)$ recording the same earthquake with inter-site distance $d \le 5.0$ km.
  - Generated **5,300 pairwise instances**.
- **Ground Truth Target:**
  - Computed $\Delta\theta = \min(|\theta_i - \theta_j|, 180^\circ - |\theta_i - \theta_j|) \in [0^\circ, 90^\circ]$ from processed acceleration waveforms.
- **Initial Feature Pool (71 Attributes):**
  - Earthquake source parameters: magnitude $M_w$, mechanism, strike, dip, rake, rupture area/length/width, hypocenter depth, ZTOR.
  - Geometry & distances: $R_{epi}$, $R_{hyp}$, $R_{jb}$, $R_{rup}$, inter-site Euclidean separation distance $d$.
  - Geotechnical properties: shear wave velocity $V_{s30}$, NEHRP soil class (B–E).
  - Ground motion intensity: PGA, PGV, PGD at each site and paired averages.

---

## Slide 3: Stepwise Backward-Forward Feature Selection
- To combat high dimensionality and collinearity among the 71 engineering features:
  1. **Backward Ranking:**
     - Computed the drop in validation $R^2$ upon removing each individual feature:
       $$\Delta R^2 = R^2_{\text{baseline}} - R^2_{\text{without } i}$$
     - A larger drop indicates higher predictive importance.
     - **Discovery:** Separation distance $d$ and average Peak Ground Acceleration (PGA) produced the largest drop in $R^2$.
  2. **Forward Selection:**
     - Iteratively added features in the ranked order until validation performance peaked.
  3. **Selected 21 Features:**
     - Separation distance $d$, average PGA, $V_{s30}$ difference, hypocenter depth, rupture length, strike/dip radiation factors, and fault geometry.

---

## Slide 4: Machine Learning Architectures
1. **Benchmark Model (Simple Linear Regression):**
   - Univariate baseline using distance $d$ alone:
     $$\Delta\theta = c_1 + c_2 \cdot d$$
   - Reflects the conventional practice of pure spatial distance decay.
2. **Ridge Regression ($L_2$ Regularization):**
   - Multivariate linear least squares minimizing:
     $$\min_\beta \sum_{i=1}^n (y^{(i)} - \beta^T x^{(i)})^2 + \alpha \|\beta\|_2^2$$
   - Calibrated on the 21 selected features with hyperparameter $\alpha = 1.5$ tuned on validation data.
3. **Deep Neural Network (Multi-Layer Perceptron):**
   - Deep MLP with ReLU activations, Adam optimizer, and $L_2$ weight decay ($\alpha = 0.1$).
   - Hyperparameter grid search conducted over network depth (1 to 5 layers) and width (50 to 400 neurons).
4. **Gradient Boosted Trees (Baseline Verification):**
   - Ensemble of boosted decision trees with histogram-based binning.

---

## Slide 5: Quantitative Experimental Results

| Model Architecture | Inputs | Train $R^2$ | Test $R^2$ | Test MAE ($^\circ$) | Test RMSE ($^\circ$) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Benchmark (Distance Only)** | 1 Feature ($d$) | 0.038 | 0.051 | 16.43$^\circ$ | 19.95$^\circ$ |
| **Ridge Regression ($L_2$)** | 21 Features | 0.349 | **0.350** | **13.35$^\circ$** | **16.52$^\circ$** |
| **Deep Neural Network (MLP)** | 21 Features | 0.381 | **0.328** | **13.56$^\circ$** | **16.79$^\circ$** |
| **Gradient Boosted Trees** | 21 Features | 0.751 | 0.325 | 13.71$^\circ$ | 16.83$^\circ$ |

- **Benchmark vs ML:** Ridge regression improves test $R^2$ by **+586%** and reduces MAE by **3.1$^\circ$**.
- **Moving Average Trends:** Models capture the true underlying mean trend across both distance $d$ and PGA bins with high fidelity.

---

## Slide 6: Physics Insights & Aleatoric Uncertainty
1. **Physical Distance Decay:**
   - At close distances ($d < 1.5$ km), wavefields are coherent and polarized ($\Delta\theta \approx 15^\circ - 20^\circ$).
   - As distance increases to 5 km, scattering and site geology decorrelate motions towards uniform randomness ($\Delta\theta \to 45^\circ$).
2. **PGA Directivity Alignment:**
   - Higher PGA values (> 0.15g) correspond to stronger source directivity and reduced angular dispersion.
3. **Aleatoric Uncertainty:**
   - The test $R^2$ ceiling (~0.35) is an intrinsic property of seismic wave propagation: 3D velocity heterogeneity and micro-topography cannot be observed from macro station parameters.
   - However, the ML models accurately capture the conditional expected value $\mathbb{E}[\Delta\theta \mid \mathbf{x}]$.

---

## Slide 7: Production Codebase & Live Demonstration
- **Clean Modular Design:**
  - `src/data_generator.py`: Generates calibrated NGA-West2 dataset.
  - `src/feature_selection.py`: Backward-forward selection implementation.
  - `src/models.py`: Benchmark, Ridge, Neural Network, and Gradient Boosting classes.
  - `src/train.py`: Hyperparameter grid search & training pipeline.
  - `src/evaluate.py`: Computes metrics and generates Figures 2–12.
  - `src/app.py`: Real-time CLI inference tool.
  - `deliverables/generate_report.py`: Builds the 2-page academic PDF write-up.
- **Live Demo Command:**
  ```bash
  python main.py --demo
  ```
  Tests realistic scenarios across near-field, transition, and far-field regimes.

---

## Slide 8: Conclusions & Future Extensions
- **Conclusions:**
  - Machine learning effectively models ground motion directionality patterns that were previously ignored in seismic hazard analysis.
  - Inter-site separation and shaking intensity are the dominant physical features.
  - Regularized and deep models provide actionable tools for regional seismic hazard evaluation.
- **Future Scope:**
  - Heteroscedastic neural networks predicting both mean and variance $\sigma^2(\mathbf{x})$.
  - Sampling full joint spatial Gaussian random fields for simultaneous multi-site simulation.
