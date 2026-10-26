"""
Health & Metadata endpoints for Crop Yield Prediction System (BT195).
"""

from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.config import settings
from app.database import get_db
from app.schemas import SystemHealthResponse, SystemMetadataResponse
from app.models.model_loader import is_model_ready, get_model_and_preprocessor
from ml.generate_sample_data import CROPS, REGIONS_COORDS, SEASONS, IRRIGATIONS

router = APIRouter(tags=["System & Health"])

@router.get("/health", response_model=SystemHealthResponse)
def get_health_status(db: Session = Depends(get_db)):
    """Returns real-time service health, model readiness, and package diagnostics."""
    # Check DB
    db_ok = True
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_ok = False

    model_ready = is_model_ready()
    active_model_name = None
    model_version = None

    if model_ready:
        try:
            _, _, meta = get_model_and_preprocessor()
            active_model_name = meta.get("selected_model_name")
            model_version = meta.get("selected_model_version")
        except Exception:
            pass

    # Check XGBoost & SHAP availability
    try:
        import xgboost
        xgb_ok = True
    except Exception:
        xgb_ok = False

    try:
        import shap
        shap_ok = True
    except Exception:
        shap_ok = False

    return SystemHealthResponse(
        status="healthy" if (db_ok and model_ready) else "degraded",
        project_id=settings.PROJECT_ID,
        project_title=settings.APP_NAME,
        team_members=settings.PROJECT_MEMBERS,
        supervisor=settings.PROJECT_SUPERVISOR,
        backend_version=settings.VERSION,
        active_model=active_model_name,
        model_version=model_version,
        model_trained=model_ready,
        database_connected=db_ok,
        xgboost_available=xgb_ok,
        shap_available=shap_ok,
        timestamp=datetime.utcnow()
    )


@router.get("/metadata", response_model=SystemMetadataResponse)
def get_system_metadata():
    """Returns supported crops, regions, seasons, features, and target units."""
    active_info = None
    if is_model_ready():
        try:
            _, _, meta = get_model_and_preprocessor()
            active_info = {
                "name": meta.get("selected_model_name"),
                "version": meta.get("selected_model_version"),
                "algorithm": meta.get("selected_model_key"),
                "calibrated_uncertainty_bound": meta.get("calibration_quantile_90"),
                "is_synthetic_trained": meta.get("is_synthetic_trained"),
                "dataset_rows": meta.get("dataset_rows"),
            }
        except Exception:
            pass

    feature_schema = [
        {"name": "field_id", "type": "string", "label": "Field Identifier", "unit": "ID", "required": False},
        {"name": "crop", "type": "string", "label": "Crop Name", "unit": "Category", "required": True},
        {"name": "season", "type": "string", "label": "Agricultural Season", "unit": "Category", "required": True},
        {"name": "region", "type": "string", "label": "State / District", "unit": "Category", "required": True},
        {"name": "latitude", "type": "float", "label": "Latitude", "unit": "Degrees", "required": False},
        {"name": "longitude", "type": "float", "label": "Longitude", "unit": "Degrees", "required": False},
        {"name": "rainfall_mm", "type": "float", "label": "Cumulative Rainfall", "unit": "mm", "required": True},
        {"name": "temperature_min_c", "type": "float", "label": "Min Temperature", "unit": "°C", "required": True},
        {"name": "temperature_max_c", "type": "float", "label": "Max Temperature", "unit": "°C", "required": True},
        {"name": "humidity", "type": "float", "label": "Relative Humidity", "unit": "%", "required": True},
        {"name": "soil_ph", "type": "float", "label": "Soil Reaction (pH)", "unit": "pH scale", "required": True},
        {"name": "soil_nitrogen", "type": "float", "label": "Available Nitrogen (N)", "unit": "kg/ha", "required": True},
        {"name": "soil_phosphorus", "type": "float", "label": "Available Phosphorus (P)", "unit": "kg/ha", "required": True},
        {"name": "soil_potassium", "type": "float", "label": "Available Potassium (K)", "unit": "kg/ha", "required": True},
        {"name": "soil_moisture", "type": "float", "label": "Volumetric Moisture", "unit": "%", "required": True},
        {"name": "irrigation", "type": "string", "label": "Irrigation Method", "unit": "Category", "required": True},
        {"name": "fertilizer_usage", "type": "float", "label": "Fertilizer Input", "unit": "kg/ha", "required": True},
        {"name": "vegetation_index_ndvi", "type": "float", "label": "Sentinel-2 NDVI", "unit": "Index (-0.2 to 1.0)", "required": False},
        {"name": "previous_season_yield", "type": "float", "label": "Previous Harvest Yield", "unit": "t/ha", "required": False},
    ]

    return SystemMetadataResponse(
        supported_crops=CROPS,
        supported_regions=list(REGIONS_COORDS.keys()),
        supported_seasons=SEASONS,
        irrigation_types=IRRIGATIONS,
        feature_schema=feature_schema,
        active_model_info=active_info,
        target_variable="actual_yield_t_ha",
        target_unit="tonnes per hectare (t/ha)"
    )
