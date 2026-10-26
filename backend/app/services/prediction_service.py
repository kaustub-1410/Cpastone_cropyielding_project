"""
Prediction Service for Crop Yield Prediction System (BT195).
Orchestrates preprocessing, feature engineering, model inference,
conformal prediction intervals, SHAP explanation, anomaly detection, and alert engine.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import uuid
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from app.config import settings
from app.models.model_loader import get_model_and_preprocessor
from app.models.db_models import PredictionRecord
from app.schemas import PredictionInput, PredictionResponse, FeatureDriver, AnomalyItem, AlertItem
from app.services.explanation_service import explain_prediction
from app.services.anomaly_service import detect_agronomic_anomalies
from app.services.alert_service import evaluate_and_generate_alerts

def run_single_prediction(
    input_data: PredictionInput,
    db: Optional[Session] = None
) -> PredictionResponse:
    """
    Executes full prediction pipeline for a single agricultural observation.
    """
    model, preprocessor, metadata = get_model_and_preprocessor()
    input_dict = input_data.model_dump()
    
    # Check data quality warnings
    data_quality_warnings = []
    if input_dict.get("vegetation_index_ndvi") is None:
        data_quality_warnings.append("Vegetation index (NDVI) was not supplied; domain mean used for vigor estimate.")
    if input_dict.get("previous_season_yield") is None:
        data_quality_warnings.append("Historical previous-season yield unavailable; autoregressive prior omitted.")
    if input_dict.get("latitude") is None or input_dict.get("longitude") is None:
        data_quality_warnings.append("Precise geographic GPS coordinates were not provided; regional centroid will be used.")

    # 1. Convert to single-row DataFrame and transform
    df_raw = pd.DataFrame([input_dict])
    X_trans = preprocessor.transform(df_raw)
    
    # 2. Raw Model Prediction
    pred_raw = float(model.predict(X_trans)[0])
    pred_yield = round(max(0.2, pred_raw), 2)  # Non-negative physiological yield

    # 3. Calibrated Conformal Prediction Interval (90% confidence)
    calibrated_q = metadata.get("calibration_quantile_90", 0.40)
    lower_bound = round(max(0.0, pred_yield - calibrated_q), 2)
    upper_bound = round(pred_yield + calibrated_q, 2)

    # 4. Feature Explanations (SHAP / exact linear attribution)
    feature_names = preprocessor.feature_names
    top_drivers = explain_prediction(model, X_trans, feature_names, input_dict, top_k=5)

    # 5. Anomaly Detection
    anomalies = detect_agronomic_anomalies(input_dict)

    # 6. Low-Yield Alert Engine
    prediction_uuid = f"PRD-{uuid.uuid4().hex[:8].upper()}"
    alerts = evaluate_and_generate_alerts(
        data=input_dict,
        predicted_yield=pred_yield,
        anomalies=anomalies,
        db=db,
        prediction_id=prediction_uuid
    )

    # 7. Persist to SQLite Database
    if db is not None:
        rec = PredictionRecord(
            prediction_id=prediction_uuid,
            field_id=input_data.field_id,
            crop=input_data.crop,
            season=input_data.season,
            region=input_data.region,
            latitude=input_data.latitude,
            longitude=input_data.longitude,
            predicted_yield=pred_yield,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            confidence_level=0.90,
            actual_yield=input_data.actual_yield_t_ha,
            model_id=f"mod-{metadata.get('selected_model_key', 'ridge_regression')}",
            model_version=metadata.get("selected_model_version", "v1.0.0"),
            input_data_json=json.dumps(input_dict),
            top_drivers_json=json.dumps([d.model_dump() for d in top_drivers]),
            anomalies_json=json.dumps([a.model_dump() for a in anomalies]),
            alerts_json=json.dumps([al.model_dump() for al in alerts], default=str),
            data_quality_warnings=json.dumps(data_quality_warnings),
            created_at=datetime.utcnow()
        )
        db.add(rec)
        db.commit()

    return PredictionResponse(
        prediction_id=prediction_uuid,
        field_id=input_data.field_id,
        crop=input_data.crop,
        season=input_data.season,
        region=input_data.region,
        predicted_yield_t_ha=pred_yield,
        lower_bound_t_ha=lower_bound,
        upper_bound_t_ha=upper_bound,
        prediction_interval_calibrated=True,
        confidence_level=0.90,
        forecast_date=datetime.utcnow(),
        model_name=metadata.get("selected_model_name", "Ridge Linear Regressor"),
        model_version=metadata.get("selected_model_version", "v1.0.0"),
        input_summary=input_dict,
        top_drivers=top_drivers,
        anomalies=anomalies,
        alerts=alerts,
        data_quality_warnings=data_quality_warnings
    )


def run_batch_predictions(
    items: List[PredictionInput],
    db: Optional[Session] = None
) -> List[PredictionResponse]:
    """Runs batch inference efficiently."""
    return [run_single_prediction(item, db=db) for item in items]
