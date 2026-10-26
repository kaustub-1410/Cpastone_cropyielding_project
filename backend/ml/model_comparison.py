"""
Model comparison benchmark script for Crop Yield Prediction System (BT195).
Prints formatted terminal table comparing Dummy Baseline against trained ML models.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.config import settings

def print_model_comparison():
    summary_path = settings.ARTIFACTS_DIR / "training_summary.json"
    if not summary_path.exists():
        print("[!] No training summary found. Please run 'python -m ml.train' first.")
        return

    with open(summary_path, "r") as f:
        summary = json.load(f)

    print("=" * 115)
    print(f"CROP YIELD PREDICTION SYSTEM (PROJECT BT195) - MODEL BENCHMARK COMPARISON")
    print("=" * 115)
    header = f"{'Model':<28} | {'Val RMSE':<9} | {'Val R²':<8} | {'Test RMSE':<9} | {'Test MAE':<8} | {'Test R²':<8} | {'Test MAPE':<9} | {'90% Cov':<8}"
    print(header)
    print("-" * 115)

    for key, data in summary.get("models", {}).items():
        v = data["val_metrics"]
        t = data["test_metrics"]
        name = data["name"]
        cov = f"{t.get('coverage_90', 'N/A')}%"
        row = f"{name:<28} | {v['rmse']:<9.4f} | {v['r2']:<8.4f} | {t['rmse']:<9.4f} | {t['mae']:<8.4f} | {t['r2']:<8.4f} | {t['mape']:<8.2f}% | {cov:<8}"
        print(row)

    print("=" * 115)
    print(f"Selected Active Model: {summary.get('selected_model_name')} (Key: {summary.get('selected_model_key')})")
    print(f"Calibrated 90% Conformal Residual: ±{summary.get('calibration_quantile_90')} t/ha")
    print(f"Dataset: {summary.get('dataset_rows')} rows | Train: {summary.get('train_size')} | Val: {summary.get('val_size')} | Test: {summary.get('test_size')}")
    print("=" * 115)

if __name__ == "__main__":
    print_model_comparison()
