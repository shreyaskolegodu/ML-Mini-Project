"""
Main entry point for Earthquake Ground Motion Directionality ML Project.
Command-line interface to run data generation, feature selection, training,
evaluation, and live demonstration.
"""

import sys
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        description="Machine Learning Tools for Predicting Earthquake Ground Motion Directionality Patterns"
    )
    parser.add_argument(
        "--pipeline",
        action="store_true",
        help="Run full end-to-end pipeline: data generation, feature selection, training, evaluation, and figure generation."
    )
    parser.add_argument(
        "--generate-data",
        action="store_true",
        help="Generate synthetic NGA-West2 shallow crustal earthquake dataset (~5,300 site pairs)."
    )
    parser.add_argument(
        "--select-features",
        action="store_true",
        help="Execute backward-forward feature selection using Ridge regression to pick 21 optimal predictors."
    )
    parser.add_argument(
        "--train",
        action="store_true",
        help="Train Benchmark Linear Regression, Ridge Regression, Deep Neural Network, and Gradient Boosting."
    )
    parser.add_argument(
        "--evaluate",
        action="store_true",
        help="Evaluate models on test set and generate publication figures (Figures 2 to 12)."
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run interactive demonstration and scenario testing."
    )
    parser.add_argument(
        "--predict",
        action="store_true",
        help="Run single-point prediction with custom parameters."
    )
    parser.add_argument("--dist", type=float, default=1.5, help="Inter-site distance in km (0 to 5 km).")
    parser.add_argument("--pga", type=float, default=0.10, help="Average Peak Ground Acceleration in g.")
    parser.add_argument("--mag", type=float, default=6.5, help="Earthquake magnitude Mw.")
    parser.add_argument("--vs30", type=float, default=360.0, help="Average shear wave velocity Vs30 in m/s.")

    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    if args.generate_data or args.pipeline:
        from src.data_generator import save_nga_west2_data
        print("\n>>> STEP 1: Generating Dataset...")
        save_nga_west2_data()

    if args.select_features or args.pipeline:
        from src.feature_selection import run_feature_selection
        print("\n>>> STEP 2: Running Backward-Forward Feature Selection...")
        run_feature_selection(target_features=21)

    if args.train or args.pipeline:
        from src.train import run_training_pipeline
        print("\n>>> STEP 3: Training & Tuning Regression Models...")
        run_training_pipeline()

    if args.evaluate or args.pipeline:
        from src.evaluate import run_evaluation
        print("\n>>> STEP 4: Evaluating Models & Generating Publication Figures...")
        run_evaluation()

    if args.demo or args.pipeline:
        from src.app import run_interactive_demo
        print("\n>>> STEP 5: Interactive Demonstration...")
        run_interactive_demo()

    if args.predict:
        from src.app import DirectionalityPredictor
        predictor = DirectionalityPredictor()
        res = predictor.predict(
            distance_km=args.dist,
            avg_pga=args.pga,
            magnitude=args.mag,
            avg_vs30=args.vs30
        )
        print(f"\nPrediction for Distance={args.dist} km, PGA={args.pga} g, Mw={args.mag}, Vs30={args.vs30} m/s:")
        print(f"Regime: {res['regime']}")
        for m, v in res['predictions'].items():
            print(f"  • {m:<26}: {v:.2f}°")

if __name__ == "__main__":
    main()
