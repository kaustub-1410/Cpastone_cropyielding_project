from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

class PredictionInput(BaseModel):
    field_id: str = Field("FLD-101", description="Field or plot identifier")
    crop: str = Field(..., description="Crop type (e.g., Wheat, Rice, Maize, Soybean, Cotton)")
    season: str = Field("Kharif", description="Agricultural season (e.g. Kharif, Rabi, Zaid, Annual)")
    region: str = Field(..., description="Geographical region or state")
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0, description="Latitude in decimal degrees")
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0, description="Longitude in decimal degrees")
    
    rainfall_mm: float = Field(..., ge=0.0, le=4000.0, description="Total rainfall during crop duration in mm")
    temperature_min_c: float = Field(..., ge=-15.0, le=45.0, description="Minimum temperature in °C")
    temperature_max_c: float = Field(..., ge=0.0, le=55.0, description="Maximum temperature in °C")
    humidity: float = Field(..., ge=0.0, le=100.0, description="Relative humidity in percentage")
    
    soil_ph: float = Field(..., ge=3.0, le=11.0, description="Soil pH level (typically 5.5 - 8.5)")
    soil_nitrogen: float = Field(..., ge=0.0, le=600.0, description="Soil Available Nitrogen (N) in kg/ha")
    soil_phosphorus: float = Field(..., ge=0.0, le=300.0, description="Soil Available Phosphorus (P) in kg/ha")
    soil_potassium: float = Field(..., ge=0.0, le=600.0, description="Soil Available Potassium (K) in kg/ha")
    soil_moisture: float = Field(..., ge=0.0, le=100.0, description="Soil volumetric moisture percentage")
    
    irrigation: str = Field("Canal", description="Primary irrigation source (e.g., Canal, Tube Well, Drip, Sprinkler, Rainfed)")
    fertilizer_usage: float = Field(..., ge=0.0, le=1000.0, description="Total fertilizer application rate in kg/ha")
    vegetation_index_ndvi: Optional[float] = Field(None, ge=-0.2, le=1.0, description="Mean peak NDVI vegetation index (-0.2 to 1.0)")
    previous_season_yield: Optional[float] = Field(None, ge=0.0, le=30.0, description="Yield in previous season in t/ha")
    actual_yield_t_ha: Optional[float] = Field(None, ge=0.0, le=30.0, description="Observed ground-truth yield in t/ha if available")

    @field_validator("temperature_max_c")
    @classmethod
    def validate_temp_range(cls, v, info):
        min_temp = info.data.get("temperature_min_c")
        if min_temp is not None and v < min_temp:
            raise ValueError(f"temperature_max_c ({v}) cannot be lower than temperature_min_c ({min_temp})")
        return v


class BatchPredictionInput(BaseModel):
    items: List[PredictionInput]


class FeatureDriver(BaseModel):
    feature: str
    feature_name: str
    impact: float
    direction: str  # "positive", "negative", "neutral"
    description: str


class AnomalyItem(BaseModel):
    type: str
    severity: str  # "Info", "Warning", "High", "Critical"
    affected_field: str
    triggering_value: float
    reference_range: str
    explanation: str
    suggested_action: str


class AlertItem(BaseModel):
    alert_id: str
    field_id: str
    crop: str
    region: str
    severity: str
    rule_name: str
    reason: str
    predicted_yield: Optional[float] = None
    threshold_value: Optional[float] = None
    suggested_action: str
    status: str = "active"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PredictionResponse(BaseModel):
    prediction_id: str
    field_id: str
    crop: str
    season: str
    region: str
    predicted_yield_t_ha: float
    lower_bound_t_ha: Optional[float] = None
    upper_bound_t_ha: Optional[float] = None
    prediction_interval_calibrated: bool = False
    confidence_level: float = 0.90
    forecast_date: datetime
    model_name: str
    model_version: str
    input_summary: Dict[str, Any]
    top_drivers: List[FeatureDriver]
    anomalies: List[AnomalyItem]
    alerts: List[AlertItem]
    data_quality_warnings: List[str]
    disclaimer: str = (
        "Agricultural forecast generated via empirical ML modeling. Yields are subject to field-level "
        "microclimate, pathogen dynamics, and management events not captured in the feature space."
    )


class BatchPredictionResponse(BaseModel):
    total: int
    predictions: List[PredictionResponse]


class DatasetSummaryResponse(BaseModel):
    dataset_id: str
    filename: str
    row_count: int
    column_count: int
    columns: List[str]
    missing_values: Dict[str, int]
    summary_stats: Dict[str, Dict[str, float]]
    is_synthetic: bool
    provenance: str
    is_training_eligible: bool
    created_at: datetime


class GenerateSampleDataRequest(BaseModel):
    num_samples: int = Field(1200, ge=100, le=10000, description="Number of synthetic agricultural records to generate")
    noise_level: float = Field(0.08, ge=0.01, le=0.3, description="Stochastic agronomic variance level")


class ModelMetrics(BaseModel):
    rmse: Optional[float] = None
    mae: Optional[float] = None
    r2: Optional[float] = None
    mape: Optional[float] = None
    bias: Optional[float] = None
    coverage_90: Optional[float] = None


class ModelEvaluationSummary(BaseModel):
    model_id: str
    name: str
    algorithm: str
    version: str
    is_active: bool
    is_synthetic_trained: bool
    validation_metrics: ModelMetrics
    test_metrics: ModelMetrics
    train_size: int
    val_size: int
    test_size: int
    created_at: datetime


class ModelComparisonReport(BaseModel):
    models: List[ModelEvaluationSummary]
    selected_model_id: Optional[str]
    evaluation_dataset: str
    split_strategy: str = "Temporal / Regionally Stratified (70% Train, 15% Val, 15% Test)"
    target_unit: str = "tonnes per hectare (t/ha)"


class TrainModelRequest(BaseModel):
    dataset_id: Optional[str] = None
    selected_algorithm: Optional[str] = "xgboost"  # dummy, ridge, random_forest, xgboost, all
    test_ratio: float = 0.15
    val_ratio: float = 0.15


class AlertUpdateRequest(BaseModel):
    status: str = Field(..., pattern="^(acknowledged|resolved)$")


class AlertResponse(BaseModel):
    alert_id: str
    field_id: str
    crop: str
    region: str
    severity: str
    rule_name: str
    reason: str
    predicted_yield: Optional[float]
    threshold_value: Optional[float]
    suggested_action: str
    status: str
    created_at: datetime
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None


class AnalyticsOverview(BaseModel):
    total_fields: int
    total_predictions: int
    average_predicted_yield: float
    active_alerts_count: int
    critical_alerts_count: int
    active_model_name: str
    active_model_version: str
    active_model_r2: Optional[float]
    active_model_rmse: Optional[float]
    is_synthetic_data: bool
    top_crops: List[Dict[str, Any]]
    recent_predictions: List[Dict[str, Any]]
    recent_alerts: List[AlertResponse]


class FeatureImportanceItem(BaseModel):
    feature: str
    label: str
    importance: float
    category: str  # "Weather", "Soil", "Crop/Management", "Satellite"


class SystemHealthResponse(BaseModel):
    status: str
    project_id: str
    project_title: str
    team_members: str
    supervisor: str
    backend_version: str
    active_model: Optional[str]
    model_version: Optional[str]
    model_trained: bool
    database_connected: bool
    xgboost_available: bool
    shap_available: bool
    timestamp: datetime


class SystemMetadataResponse(BaseModel):
    supported_crops: List[str]
    supported_regions: List[str]
    supported_seasons: List[str]
    irrigation_types: List[str]
    feature_schema: List[Dict[str, Any]]
    active_model_info: Optional[Dict[str, Any]]
    target_variable: str = "actual_yield_t_ha"
    target_unit: str = "tonnes per hectare (t/ha)"
