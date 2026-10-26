"""
Model evaluation service for Crop Yield Prediction System (BT195).
Computes exact, un-hardcoded metrics for model validation and test benchmarks.
"""

from typing import Dict, Any, Optional, List, Tuple
import time
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

def calculate_regression_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    lower_bounds: Optional[np.ndarray] = None,
    upper_bounds: Optional[np.ndarray] = None
) -> Dict[str, float]:
    """
    Computes RMSE, MAE, R², MAPE, Mean Bias, and Prediction-Interval Coverage.
    Handles zero/near-zero yields with epsilon protection.
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)

    if len(y_true) == 0:
        return {
            "rmse": 0.0,
            "mae": 0.0,
            "r2": 0.0,
            "mape": 0.0,
            "bias": 0.0,
            "coverage_90": 0.0,
        }

    # 1. RMSE & MAE
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    mae = float(mean_absolute_error(y_true, y_pred))

    # 2. R-squared (handling zero variance edge case)
    if np.var(y_true) < 1e-9:
        r2 = 0.0
    else:
        r2 = float(r2_score(y_true, y_pred))

    # 3. MAPE with safe denominator
    safe_denom = np.maximum(np.abs(y_true), 0.1)
    mape = float(np.mean(np.abs((y_true - y_pred) / safe_denom)) * 100.0)

    # 4. Mean Prediction Bias (positive means over-prediction, negative under-prediction)
    bias = float(np.mean(y_pred - y_true))

    # 5. Prediction-interval empirical coverage
    coverage_90 = None
    if lower_bounds is not None and upper_bounds is not None:
        in_bounds = (y_true >= lower_bounds) & (y_true <= upper_bounds)
        coverage_90 = float(np.mean(in_bounds) * 100.0)

    return {
        "rmse": round(rmse, 4),
        "mae": round(mae, 4),
        "r2": round(r2, 4),
        "mape": round(mape, 2),
        "bias": round(bias, 4),
        "coverage_90": round(coverage_90, 2) if coverage_90 is not None else None,
    }


def benchmark_model_speed(model: Any, X_sample: np.ndarray, num_runs: int = 5) -> Dict[str, float]:
    """Measures actual inference latency (ms per sample) and throughput (predictions/sec)."""
    if len(X_sample) == 0:
        return {"latency_ms_per_sample": 0.0, "throughput_preds_per_sec": 0.0}

    times = []
    for _ in range(num_runs):
        start = time.perf_counter()
        _ = model.predict(X_sample)
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    mean_elapsed = np.mean(times)
    sample_count = len(X_sample)
    latency_ms = (mean_elapsed / sample_count) * 1000.0
    throughput = sample_count / (mean_elapsed + 1e-9)

    return {
        "latency_ms_per_sample": round(latency_ms, 3),
        "throughput_preds_per_sec": round(throughput, 1),
    }
