"""
Analytics & Intelligence API endpoints for dashboard visualizations.
"""

from typing import List, Dict, Any, Optional
import json
from pathlib import Path
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import pandas as pd

from app.config import settings
from app.database import get_db
from app.models.db_models import PredictionRecord, AlertRecord, ModelRecord
from app.schemas import AnalyticsOverview, FeatureImportanceItem, AlertResponse
from app.models.model_loader import get_model_and_preprocessor, is_model_ready
from app.services.explanation_service import get_global_feature_importance

router = APIRouter(prefix="/analytics", tags=["Analytics & Insights"])

@router.get("/overview", response_model=AnalyticsOverview)
def get_analytics_overview(db: Session = Depends(get_db)):
    """Computes real-time overview metrics for the executive dashboard."""
    # 1. Prediction counts
    total_preds = db.query(PredictionRecord).count()
    total_fields = db.query(func.count(func.distinct(PredictionRecord.field_id))).scalar() or 0
    avg_yield = db.query(func.avg(PredictionRecord.predicted_yield)).scalar() or 0.0

    # 2. Alert counts
    active_alerts = db.query(AlertRecord).filter(AlertRecord.status.in_(["active", "acknowledged"])).count()
    critical_alerts = db.query(AlertRecord).filter(
        AlertRecord.status.in_(["active", "acknowledged"]),
        AlertRecord.severity == "Critical"
    ).count()

    # 3. Active Model
    active_model = db.query(ModelRecord).filter(ModelRecord.is_active == True).first()
    model_name = active_model.name if active_model else "Not Initialized"
    model_ver = active_model.version if active_model else "N/A"
    model_r2 = active_model.test_r2 if active_model else None
    model_rmse = active_model.test_rmse if active_model else None
    is_synth = active_model.is_synthetic_trained if active_model else True

    # 4. Top Crops Summary
    top_crops_query = (
        db.query(
            PredictionRecord.crop,
            func.count(PredictionRecord.id).label("count"),
            func.avg(PredictionRecord.predicted_yield).label("avg_yield")
        )
        .group_by(PredictionRecord.crop)
        .order_by(desc("count"))
        .limit(6)
        .all()
    )
    top_crops = [
        {"crop": r.crop, "prediction_count": r.count, "avg_yield": round(float(r.avg_yield), 2)}
        for r in top_crops_query
    ]

    # 5. Recent Predictions
    recent_p = (
        db.query(PredictionRecord)
        .order_by(desc(PredictionRecord.created_at))
        .limit(5)
        .all()
    )
    recent_preds = [
        {
            "prediction_id": r.prediction_id,
            "field_id": r.field_id,
            "crop": r.crop,
            "region": r.region,
            "predicted_yield_t_ha": r.predicted_yield,
            "lower_bound_t_ha": r.lower_bound,
            "upper_bound_t_ha": r.upper_bound,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in recent_p
    ]

    # 6. Recent Alerts
    recent_a = (
        db.query(AlertRecord)
        .order_by(desc(AlertRecord.created_at))
        .limit(5)
        .all()
    )
    recent_alerts = [
        AlertResponse(
            alert_id=r.alert_id,
            field_id=r.field_id,
            crop=r.crop,
            region=r.region,
            severity=r.severity,
            rule_name=r.rule_name,
            reason=r.reason,
            predicted_yield=r.predicted_yield,
            threshold_value=r.threshold_value,
            suggested_action=r.suggested_action,
            status=r.status,
            created_at=r.created_at,
            acknowledged_at=r.acknowledged_at,
            resolved_at=r.resolved_at
        )
        for r in recent_a
    ]

    return AnalyticsOverview(
        total_fields=total_fields,
        total_predictions=total_preds,
        average_predicted_yield=round(float(avg_yield), 2),
        active_alerts_count=active_alerts,
        critical_alerts_count=critical_alerts,
        active_model_name=model_name,
        active_model_version=model_ver,
        active_model_r2=model_r2,
        active_model_rmse=model_rmse,
        is_synthetic_data=is_synth,
        top_crops=top_crops,
        recent_predictions=recent_preds,
        recent_alerts=recent_alerts
    )


@router.get("/yield-trends")
def get_yield_trends(crop: Optional[str] = None, region: Optional[str] = None):
    """Returns historical and forecast yield trends aggregated by crop/season."""
    sample_path = settings.SAMPLE_DATA_DIR / "crop_yield_sample_dataset.csv"
    if not sample_path.exists():
        from ml.generate_sample_data import save_sample_dataset
        sample_path = save_sample_dataset()

    df = pd.read_csv(sample_path)
    if crop and crop != "all":
        df = df[df["crop"] == crop]
    if region and region != "all":
        df = df[df["region"] == region]

    # Aggregate by Year & Crop
    if "year" in df.columns:
        grouped = df.groupby(["year", "crop"])["actual_yield_t_ha"].mean().reset_index()
        trends = []
        for year in sorted(grouped["year"].unique()):
            sub = grouped[grouped["year"] == year]
            entry = {"year": int(year)}
            for _, row in sub.iterrows():
                entry[str(row["crop"])] = round(float(row["actual_yield_t_ha"]), 2)
            trends.append(entry)
        return {"trends": trends, "group_by": "year"}
    else:
        # Fallback to season
        grouped = df.groupby("season")["actual_yield_t_ha"].mean().to_dict()
        return {"trends": [{"season": k, "avg_yield": round(v, 2)} for k, v in grouped.items()]}


@router.get("/feature-importance", response_model=List[FeatureImportanceItem])
def get_model_feature_importance():
    """Computes global feature importance for the active model."""
    if not is_model_ready():
        return []
    try:
        model, preprocessor, _ = get_model_and_preprocessor()
        return get_global_feature_importance(model, preprocessor.feature_names, top_n=12)
    except Exception:
        return []


@router.get("/crops")
def get_crop_analytics():
    """Returns detailed statistics per crop."""
    sample_path = settings.SAMPLE_DATA_DIR / "crop_yield_sample_dataset.csv"
    if not sample_path.exists():
        from ml.generate_sample_data import save_sample_dataset
        sample_path = save_sample_dataset()

    df = pd.read_csv(sample_path)
    stats = []
    for c in df["crop"].unique():
        sub = df[df["crop"] == c]
        stats.append({
            "crop": c,
            "observations": len(sub),
            "mean_yield": round(float(sub["actual_yield_t_ha"].mean()), 2),
            "min_yield": round(float(sub["actual_yield_t_ha"].min()), 2),
            "max_yield": round(float(sub["actual_yield_t_ha"].max()), 2),
            "optimal_rainfall": round(float(sub["rainfall_mm"].mean()), 1),
            "optimal_temp": round(float(sub["temperature_max_c"].mean()), 1),
        })
    return stats
