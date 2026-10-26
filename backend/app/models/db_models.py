from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from app.database import Base

class DatasetRecord(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(String(64), unique=True, index=True)
    filename = Column(String(255), nullable=False)
    filepath = Column(String(512), nullable=False)
    row_count = Column(Integer, default=0)
    column_count = Column(Integer, default=0)
    columns_json = Column(Text, default="[]")
    missing_values_json = Column(Text, default="{}")
    summary_stats_json = Column(Text, default="{}")
    is_synthetic = Column(Boolean, default=False)
    provenance = Column(String(255), default="Uploaded CSV")
    is_training_eligible = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class ModelRecord(Base):
    __tablename__ = "models"

    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(String(64), unique=True, index=True)
    name = Column(String(128), nullable=False)
    algorithm = Column(String(64), nullable=False)
    version = Column(String(32), nullable=False)
    artifact_path = Column(String(512), nullable=False)
    features_json = Column(Text, default="[]")
    parameters_json = Column(Text, default="{}")
    
    # Validation Metrics (used for selection)
    val_rmse = Column(Float, nullable=True)
    val_mae = Column(Float, nullable=True)
    val_r2 = Column(Float, nullable=True)
    val_mape = Column(Float, nullable=True)
    
    # Test Metrics (held-out untouched evaluation)
    test_rmse = Column(Float, nullable=True)
    test_mae = Column(Float, nullable=True)
    test_r2 = Column(Float, nullable=True)
    test_mape = Column(Float, nullable=True)
    test_bias = Column(Float, nullable=True)
    test_coverage_90 = Column(Float, nullable=True)
    
    is_active = Column(Boolean, default=False)
    is_synthetic_trained = Column(Boolean, default=False)
    train_size = Column(Integer, default=0)
    val_size = Column(Integer, default=0)
    test_size = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class PredictionRecord(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(String(64), unique=True, index=True)
    field_id = Column(String(64), index=True)
    crop = Column(String(64), index=True)
    season = Column(String(32), index=True)
    region = Column(String(64), index=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    predicted_yield = Column(Float, nullable=False)
    lower_bound = Column(Float, nullable=True)
    upper_bound = Column(Float, nullable=True)
    confidence_level = Column(Float, default=0.90)
    actual_yield = Column(Float, nullable=True)
    
    model_id = Column(String(64), nullable=False)
    model_version = Column(String(32), nullable=False)
    
    input_data_json = Column(Text, default="{}")
    top_drivers_json = Column(Text, default="[]")
    anomalies_json = Column(Text, default="[]")
    alerts_json = Column(Text, default="[]")
    data_quality_warnings = Column(Text, default="[]")
    
    created_at = Column(DateTime, default=datetime.utcnow)


class AlertRecord(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String(64), unique=True, index=True)
    prediction_id = Column(String(64), index=True, nullable=True)
    field_id = Column(String(64), index=True)
    crop = Column(String(64), index=True)
    region = Column(String(64), index=True)
    severity = Column(String(16), default="Warning")  # Info, Warning, High, Critical
    rule_name = Column(String(128), nullable=False)
    reason = Column(Text, nullable=False)
    predicted_yield = Column(Float, nullable=True)
    threshold_value = Column(Float, nullable=True)
    suggested_action = Column(Text, nullable=False)
    status = Column(String(32), default="active")  # active, acknowledged, resolved
    created_at = Column(DateTime, default=datetime.utcnow)
    acknowledged_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
