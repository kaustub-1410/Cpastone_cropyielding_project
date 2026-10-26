"""
Model training and benchmarking pipeline for Crop Yield Prediction System (BT195).
Trains Naive Dummy Baseline, Ridge, Random Forest, and XGBoost.
Calibrates Conformal Prediction Intervals using validation residuals.
Selects best model on Validation set and evaluates on untouched Test set.
"""

import os
import sys
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Tuple, Optional

import numpy as np
import pandas as pd
import joblib

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sklearn.dummy import DummyRegressor
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

try:
    from xgboost import XGBRegressor
    XGB_AVAILABLE = True
except ImportError:
    from sklearn.ensemble import GradientBoostingRegressor as XGBRegressor
    XGB_AVAILABLE = False

from app.config import settings
from app.database import SessionLocal, init_db
from app.models.db_models import ModelRecord, DatasetRecord
from app.services.preprocessing import AgriculturalPreprocessor
from app.services.evaluation_service import calculate_regression_metrics, benchmark_model_speed

def load_or_generate_dataset(dataset_path: Optional[Path] = None) -> pd.DataFrame:
    """Loads target dataset or generates sample dataset if none exists."""
    if dataset_path is None or not dataset_path.exists():
        sample_path = settings.SAMPLE_DATA_DIR / "crop_yield_sample_dataset.csv"
        if not sample_path.exists():
            from ml.generate_sample_data import save_sample_dataset
            sample_path = save_sample_dataset()
        dataset_path = sample_path

    print(f"[*] Loading training data from: {dataset_path}")
    df = pd.read_csv(dataset_path)
    return df, dataset_path


def split_agricultural_data(df: pd.DataFrame, test_ratio: float = 0.15, val_ratio: float = 0.15, seed: int = 42):
    """
    Creates leakage-safe splits.
    Uses temporal year split when multi-year data is present, otherwise stratified random split.
    """
    target_col = "actual_yield_t_ha"
    if target_col not in df.columns:
        raise ValueError(f"Target column '{target_col}' not found in dataset!")

    # Deduplicate before splitting so sample lengths stay perfectly aligned
    df = df.drop_duplicates(subset=[col for col in ["field_id", "crop", "season", "year", "region"] if col in df.columns])
    df = df.dropna(subset=[target_col])

    # Check for multi-year temporal split capability
    if "year" in df.columns and len(df["year"].unique()) >= 3:
        years = sorted(df["year"].unique())
        test_year = years[-1]
        val_year = years[-2]
        
        test_df = df[df["year"] == test_year].copy()
        val_df = df[df["year"] == val_year].copy()
        train_df = df[df["year"] < val_year].copy()
        
        # If train is too small, fallback to stratified split
        if len(train_df) < 50:
            train_val_df, test_df = train_test_split(df, test_size=test_ratio, random_state=seed)
            train_df, val_df = train_test_split(train_val_df, test_size=val_ratio / (1.0 - test_ratio), random_state=seed)
    else:
        train_val_df, test_df = train_test_split(df, test_size=test_ratio, random_state=seed)
        train_df, val_df = train_test_split(train_val_df, test_size=val_ratio / (1.0 - test_ratio), random_state=seed)

    print(f"[*] Data Splits: Train={len(train_df)}, Val={len(val_df)}, Test={len(test_df)}")
    return train_df, val_df, test_df


def train_and_benchmark_models(
    dataset_path: Optional[Path] = None,
    preferred_algo: Optional[str] = None
) -> Dict[str, Any]:
    """
    Complete end-to-end training, conformal calibration, and comparison.
    """
    init_db()
    df, resolved_path = load_or_generate_dataset(dataset_path)
    is_synthetic = bool(df.get("is_synthetic", pd.Series([False])).any())
    provenance = str(df.get("provenance", pd.Series(["Synthetic Agronomic Simulation"])).iloc[0])

    train_df, val_df, test_df = split_agricultural_data(df)
    target_col = "actual_yield_t_ha"

    y_train = train_df[target_col].values
    y_val = val_df[target_col].values
    y_test = test_df[target_col].values

    # 1. Fit Preprocessor exclusively on Train Split
    preprocessor = AgriculturalPreprocessor()
    preprocessor.fit(train_df)
    preprocessor_path = settings.ARTIFACTS_DIR / "fitted_preprocessor.joblib"
    preprocessor.save(preprocessor_path)

    X_train = preprocessor.transform(train_df)
    X_val = preprocessor.transform(val_df)
    X_test = preprocessor.transform(test_df)

    feature_names = preprocessor.feature_names

    # 2. Candidate Models
    candidate_models = {
        "dummy_baseline": {
            "name": "Dummy Baseline (Mean)",
            "algorithm": "DummyRegressor",
            "model": DummyRegressor(strategy="mean"),
            "params": {"strategy": "mean"},
        },
        "ridge_regression": {
            "name": "Ridge Linear Regressor",
            "algorithm": "Ridge",
            "model": Ridge(alpha=1.5, random_state=42),
            "params": {"alpha": 1.5},
        },
        "random_forest": {
            "name": "Random Forest Regressor",
            "algorithm": "RandomForestRegressor",
            "model": RandomForestRegressor(n_estimators=100, max_depth=12, min_samples_split=4, random_state=42, n_jobs=-1),
            "params": {"n_estimators": 100, "max_depth": 12},
        },
        "xgboost": {
            "name": "XGBoost Regressor" if XGB_AVAILABLE else "Gradient Boosting Regressor",
            "algorithm": "XGBRegressor" if XGB_AVAILABLE else "GradientBoostingRegressor",
            "model": XGBRegressor(n_estimators=120, max_depth=5, learning_rate=0.07, random_state=42),
            "params": {"n_estimators": 120, "max_depth": 5, "learning_rate": 0.07},
        },
    }

    results = {}
    best_val_rmse = float("inf")
    best_key = None
    calibration_quantiles = {}

    # 3. Train each model, compute validation metrics & conformal quantile
    for key, info in candidate_models.items():
        print(f"[*] Training {info['name']}...")
        model = info["model"]
        model.fit(X_train, y_train)

        # Validation prediction
        val_pred = model.predict(X_val)

        # Compute Conformal Prediction Interval Quantile on Validation Residuals
        # 90% confidence level: alpha = 0.10
        val_residuals = np.abs(y_val - val_pred)
        alpha = 0.10
        n_val = len(y_val)
        # Finite-sample conformal quantile level
        q_level = min(1.0, (1.0 - alpha) * (1.0 + 1.0 / n_val))
        calibrated_q = float(np.quantile(val_residuals, q_level))
        calibration_quantiles[key] = calibrated_q

        # Validation bounds
        val_lower = np.maximum(0.0, val_pred - calibrated_q)
        val_upper = val_pred + calibrated_q
        val_metrics = calculate_regression_metrics(y_val, val_pred, val_lower, val_upper)

        # Test prediction & coverage
        test_pred = model.predict(X_test)
        test_lower = np.maximum(0.0, test_pred - calibrated_q)
        test_upper = test_pred + calibrated_q
        test_metrics = calculate_regression_metrics(y_test, test_pred, test_lower, test_upper)

        # Latency & throughput
        speed_stats = benchmark_model_speed(model, X_test[:min(100, len(X_test))])

        model_artifact_path = settings.ARTIFACTS_DIR / f"{key}_model.joblib"
        joblib.dump(model, model_artifact_path)

        results[key] = {
            "key": key,
            "name": info["name"],
            "algorithm": info["algorithm"],
            "params": info["params"],
            "val_metrics": val_metrics,
            "test_metrics": test_metrics,
            "calibration_quantile_90": round(calibrated_q, 4),
            "speed": speed_stats,
            "artifact_path": str(model_artifact_path),
        }

        # Model selection strictly based on validation performance
        if val_metrics["rmse"] < best_val_rmse:
            best_val_rmse = val_metrics["rmse"]
            best_key = key

    # If preferred algorithm specified and valid, respect it, otherwise choose best validation performer
    selected_key = preferred_algo if preferred_algo in candidate_models else best_key
    selected_model_info = results[selected_key]
    print(f"\n[+] Selected Best Model based on Validation RMSE: {selected_model_info['name']} (Val RMSE: {selected_model_info['val_metrics']['rmse']}, Test R²: {selected_model_info['test_metrics']['r2']})")

    # Save active model symlink / file
    best_model_obj = candidate_models[selected_key]["model"]
    active_model_path = settings.ARTIFACTS_DIR / "active_model.joblib"
    joblib.dump(best_model_obj, active_model_path)

    # Save full training metadata
    training_summary = {
        "timestamp": datetime.utcnow().isoformat(),
        "selected_model_key": selected_key,
        "selected_model_name": selected_model_info["name"],
        "selected_model_version": "v1.0.0",
        "calibration_quantile_90": selected_model_info["calibration_quantile_90"],
        "is_synthetic_trained": is_synthetic,
        "provenance": provenance,
        "dataset_path": str(resolved_path),
        "dataset_rows": len(df),
        "train_size": len(train_df),
        "val_size": len(val_df),
        "test_size": len(test_df),
        "feature_names": feature_names,
        "models": results,
    }

    summary_file = settings.ARTIFACTS_DIR / "training_summary.json"
    with open(summary_file, "w") as f:
        json.dump(training_summary, f, indent=2)

    # 4. Save/Update records in SQLite DB
    db = SessionLocal()
    try:
        # Register Dataset in DB
        existing_ds = db.query(DatasetRecord).filter(DatasetRecord.filepath == str(resolved_path)).first()
        if not existing_ds:
            ds_rec = DatasetRecord(
                dataset_id=str(uuid.uuid4())[:8],
                filename=resolved_path.name,
                filepath=str(resolved_path),
                row_count=len(df),
                column_count=len(df.columns),
                columns_json=json.dumps(list(df.columns)),
                is_synthetic=is_synthetic,
                provenance=provenance,
                is_training_eligible=True,
                created_at=datetime.utcnow()
            )
            db.add(ds_rec)
            db.commit()

        # Update or Insert Model Records
        for m_key, m_data in results.items():
            is_active = (m_key == selected_key)
            existing_model = db.query(ModelRecord).filter(ModelRecord.model_id == f"mod-{m_key}").first()
            if existing_model:
                existing_model.is_active = is_active
                existing_model.val_rmse = m_data["val_metrics"]["rmse"]
                existing_model.val_mae = m_data["val_metrics"]["mae"]
                existing_model.val_r2 = m_data["val_metrics"]["r2"]
                existing_model.val_mape = m_data["val_metrics"]["mape"]
                existing_model.test_rmse = m_data["test_metrics"]["rmse"]
                existing_model.test_mae = m_data["test_metrics"]["mae"]
                existing_model.test_r2 = m_data["test_metrics"]["r2"]
                existing_model.test_mape = m_data["test_metrics"]["mape"]
                existing_model.test_bias = m_data["test_metrics"]["bias"]
                existing_model.test_coverage_90 = m_data["test_metrics"]["coverage_90"]
            else:
                m_rec = ModelRecord(
                    model_id=f"mod-{m_key}",
                    name=m_data["name"],
                    algorithm=m_data["algorithm"],
                    version="1.0.0",
                    artifact_path=m_data["artifact_path"],
                    features_json=json.dumps(feature_names),
                    parameters_json=json.dumps(m_data["params"]),
                    val_rmse=m_data["val_metrics"]["rmse"],
                    val_mae=m_data["val_metrics"]["mae"],
                    val_r2=m_data["val_metrics"]["r2"],
                    val_mape=m_data["val_metrics"]["mape"],
                    test_rmse=m_data["test_metrics"]["rmse"],
                    test_mae=m_data["test_metrics"]["mae"],
                    test_r2=m_data["test_metrics"]["r2"],
                    test_mape=m_data["test_metrics"]["mape"],
                    test_bias=m_data["test_metrics"]["bias"],
                    test_coverage_90=m_data["test_metrics"]["coverage_90"],
                    is_active=is_active,
                    is_synthetic_trained=is_synthetic,
                    train_size=len(train_df),
                    val_size=len(val_df),
                    test_size=len(test_df),
                    created_at=datetime.utcnow()
                )
                db.add(m_rec)
        db.commit()
    finally:
        db.close()

    print("[OK] Training & Model Registry update completed successfully!")
    return training_summary

if __name__ == "__main__":
    train_and_benchmark_models()
