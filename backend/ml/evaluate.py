"""
Model evaluation script for Crop Yield Prediction System (BT195).
Computes actual-versus-predicted distributions, residuals, and per-crop/region metrics on the held-out test split.
Outputs machine-readable evaluation report.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any
import numpy as np
import pandas as pd
import joblib

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings
from app.services.preprocessing import AgriculturalPreprocessor
from app.services.evaluation_service import calculate_regression_metrics
from ml.train import load_or_generate_dataset, split_agricultural_data

def run_evaluation(model_name_or_key: str = "active") -> Dict[str, Any]:
    summary_path = settings.ARTIFACTS_DIR / "training_summary.json"
    if not summary_path.exists():
        from ml.train import train_and_benchmark_models
        train_and_benchmark_models()

    with open(summary_path, "r") as f:
        summary = json.load(f)

    # Load preprocessor
    prep_path = settings.ARTIFACTS_DIR / "fitted_preprocessor.joblib"
    preprocessor = AgriculturalPreprocessor.load(prep_path)

    # Load model
    if model_name_or_key == "active":
        model_path = settings.ARTIFACTS_DIR / "active_model.joblib"
        model = joblib.load(model_path)
        selected_key = summary.get("selected_model_key", "ridge_regression")
    else:
        model_path = settings.ARTIFACTS_DIR / f"{model_name_or_key}_model.joblib"
        model = joblib.load(model_path)
        selected_key = model_name_or_key

    calibrated_q = summary.get("calibration_quantile_90", 0.40)

    # Load test split
    df, _ = load_or_generate_dataset(Path(summary["dataset_path"]))
    _, _, test_df = split_agricultural_data(df)

    y_test = test_df["actual_yield_t_ha"].values
    X_test = preprocessor.transform(test_df)
    y_pred = model.predict(X_test)

    # Bounds
    lower_bounds = np.maximum(0.0, y_pred - calibrated_q)
    upper_bounds = y_pred + calibrated_q

    overall_metrics = calculate_regression_metrics(y_test, y_pred, lower_bounds, upper_bounds)

    # Actual vs Predicted sample points (up to 120 representative points for charts)
    scatter_points = []
    sample_indices = np.linspace(0, len(y_test) - 1, min(120, len(y_test)), dtype=int)
    for idx in sample_indices:
        scatter_points.append({
            "actual": round(float(y_test[idx]), 2),
            "predicted": round(float(y_pred[idx]), 2),
            "lower": round(float(lower_bounds[idx]), 2),
            "upper": round(float(upper_bounds[idx]), 2),
            "crop": str(test_df.iloc[idx]["crop"]),
            "region": str(test_df.iloc[idx]["region"]),
            "field_id": str(test_df.iloc[idx].get("field_id", f"FLD-{idx}")),
        })

    # Residual Distribution
    residuals = y_pred - y_test
    hist, bin_edges = np.histogram(residuals, bins=12)
    residual_distribution = []
    for count, b_start, b_end in zip(hist, bin_edges[:-1], bin_edges[1:]):
        residual_distribution.append({
            "bin": f"{round(float(b_start), 2)} to {round(float(b_end), 2)}",
            "count": int(count),
            "midpoint": round(float((b_start + b_end) / 2.0), 2),
        })

    # Per-Crop Breakdown
    per_crop = {}
    for crop in test_df["crop"].unique():
        mask = (test_df["crop"].values == crop)
        if np.sum(mask) >= 3:
            crop_metrics = calculate_regression_metrics(
                y_test[mask], y_pred[mask], lower_bounds[mask], upper_bounds[mask]
            )
            per_crop[str(crop)] = {
                "sample_count": int(np.sum(mask)),
                "rmse": crop_metrics["rmse"],
                "mae": crop_metrics["mae"],
                "r2": crop_metrics["r2"],
                "mape": crop_metrics["mape"],
            }

    # Per-Region Breakdown
    per_region = {}
    for region in test_df["region"].unique():
        mask = (test_df["region"].values == region)
        if np.sum(mask) >= 3:
            reg_metrics = calculate_regression_metrics(
                y_test[mask], y_pred[mask], lower_bounds[mask], upper_bounds[mask]
            )
            per_region[str(region)] = {
                "sample_count": int(np.sum(mask)),
                "rmse": reg_metrics["rmse"],
                "mae": reg_metrics["mae"],
                "r2": reg_metrics["r2"],
            }

    report = {
        "model_key": selected_key,
        "model_name": summary["models"][selected_key]["name"],
        "algorithm": summary["models"][selected_key]["algorithm"],
        "version": summary["selected_model_version"],
        "test_sample_size": len(test_df),
        "overall_metrics": overall_metrics,
        "calibration_quantile_90": round(calibrated_q, 4),
        "is_synthetic_evaluation": summary.get("is_synthetic_trained", True),
        "provenance": summary.get("provenance", "Synthetic Agronomic Simulation"),
        "scatter_points": scatter_points,
        "residual_distribution": residual_distribution,
        "per_crop_metrics": per_crop,
        "per_region_metrics": per_region,
    }

    report_path = settings.ARTIFACTS_DIR / "evaluation_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"[OK] Evaluation report generated at {report_path}")
    print(f"     Test RMSE: {overall_metrics['rmse']} t/ha | Test MAE: {overall_metrics['mae']} t/ha | Test R²: {overall_metrics['r2']}")
    return report

if __name__ == "__main__":
    run_evaluation()
