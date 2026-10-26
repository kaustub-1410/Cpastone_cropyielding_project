"""
Prediction API endpoints for single and batch agricultural forecasts.
"""

from typing import List, Optional
import json
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models.db_models import PredictionRecord
from app.schemas import PredictionInput, BatchPredictionInput, PredictionResponse, BatchPredictionResponse
from app.services.prediction_service import run_single_prediction, run_batch_predictions

router = APIRouter(prefix="/predictions", tags=["Predictions"])

@router.post("", response_model=PredictionResponse)
def create_prediction(input_data: PredictionInput, db: Session = Depends(get_db)):
    """Generates yield prediction, calibrated bounds, feature contributions, and alerts."""
    try:
        return run_single_prediction(input_data, db=db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")


@router.post("/batch", response_model=BatchPredictionResponse)
def create_batch_prediction(batch_input: BatchPredictionInput, db: Session = Depends(get_db)):
    """Processes multiple agricultural field observations."""
    if len(batch_input.items) > 500:
        raise HTTPException(status_code=400, detail="Batch size limit is 500 records per request.")
    try:
        results = run_batch_predictions(batch_input.items, db=db)
        return BatchPredictionResponse(total=len(results), predictions=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch inference error: {str(e)}")


@router.get("/history")
def get_prediction_history(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    crop: Optional[str] = None,
    region: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Retrieves paginated historical predictions."""
    query = db.query(PredictionRecord)

    if crop and crop != "all":
        query = query.filter(PredictionRecord.crop == crop)
    if region and region != "all":
        query = query.filter(PredictionRecord.region == region)
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (PredictionRecord.field_id.ilike(search_filter)) |
            (PredictionRecord.prediction_id.ilike(search_filter))
        )

    total = query.count()
    records = (
        query.order_by(desc(PredictionRecord.created_at))
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    items = []
    for r in records:
        try:
            top_drivers = json.loads(r.top_drivers_json) if r.top_drivers_json else []
            anomalies = json.loads(r.anomalies_json) if r.anomalies_json else []
            alerts = json.loads(r.alerts_json) if r.alerts_json else []
            input_summary = json.loads(r.input_data_json) if r.input_data_json else {}
        except Exception:
            top_drivers, anomalies, alerts, input_summary = [], [], [], {}

        items.append({
            "prediction_id": r.prediction_id,
            "field_id": r.field_id,
            "crop": r.crop,
            "season": r.season,
            "region": r.region,
            "latitude": r.latitude,
            "longitude": r.longitude,
            "predicted_yield_t_ha": r.predicted_yield,
            "lower_bound_t_ha": r.lower_bound,
            "upper_bound_t_ha": r.upper_bound,
            "confidence_level": r.confidence_level,
            "actual_yield": r.actual_yield,
            "model_id": r.model_id,
            "model_version": r.model_version,
            "top_drivers": top_drivers,
            "anomalies": anomalies,
            "alerts": alerts,
            "input_summary": input_summary,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        })

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "items": items
    }


@router.get("/{prediction_id}")
def get_prediction_detail(prediction_id: str, db: Session = Depends(get_db)):
    """Retrieves full prediction record by UUID."""
    r = db.query(PredictionRecord).filter(PredictionRecord.prediction_id == prediction_id).first()
    if not r:
        raise HTTPException(status_code=404, detail=f"Prediction '{prediction_id}' not found.")

    return {
        "prediction_id": r.prediction_id,
        "field_id": r.field_id,
        "crop": r.crop,
        "season": r.season,
        "region": r.region,
        "latitude": r.latitude,
        "longitude": r.longitude,
        "predicted_yield_t_ha": r.predicted_yield,
        "lower_bound_t_ha": r.lower_bound,
        "upper_bound_t_ha": r.upper_bound,
        "confidence_level": r.confidence_level,
        "actual_yield": r.actual_yield,
        "model_id": r.model_id,
        "model_version": r.model_version,
        "top_drivers": json.loads(r.top_drivers_json or "[]"),
        "anomalies": json.loads(r.anomalies_json or "[]"),
        "alerts": json.loads(r.alerts_json or "[]"),
        "input_summary": json.loads(r.input_data_json or "{}"),
        "data_quality_warnings": json.loads(r.data_quality_warnings or "[]"),
        "created_at": r.created_at.isoformat() if r.created_at else None,
    }
