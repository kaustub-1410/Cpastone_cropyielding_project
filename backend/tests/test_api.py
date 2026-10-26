"""
Automated unit and integration test suite for Crop Yield Prediction System (BT195).
Tests all 15 required acceptance capabilities with pytest and FastAPI TestClient.
"""

import sys
import io
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
import numpy as np
import pandas as pd

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app
from app.services.evaluation_service import calculate_regression_metrics
from app.services.anomaly_service import detect_agronomic_anomalies
from app.services.alert_service import evaluate_and_generate_alerts
from app.services.preprocessing import AgriculturalPreprocessor
from app.schemas import PredictionInput

client = TestClient(app)

# 1. Health Endpoint Test
def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["project_id"] == "BT195"
    assert data["status"] in ["healthy", "degraded"]
    assert "model_trained" in data
    assert data["database_connected"] is True


# 2. Metadata Endpoint Test
def test_metadata_endpoint():
    response = client.get("/api/metadata")
    assert response.status_code == 200
    data = response.json()
    assert "Wheat" in data["supported_crops"]
    assert "Punjab" in data["supported_regions"]
    assert data["target_unit"] == "tonnes per hectare (t/ha)"
    assert len(data["feature_schema"]) > 10


# 3. Valid Prediction Input Test
def test_valid_prediction():
    payload = {
        "field_id": "TEST-FLD-01",
        "crop": "Wheat",
        "season": "Rabi",
        "region": "Punjab",
        "latitude": 30.90,
        "longitude": 75.85,
        "rainfall_mm": 500.0,
        "temperature_min_c": 12.0,
        "temperature_max_c": 26.0,
        "humidity": 60.0,
        "soil_ph": 6.8,
        "soil_nitrogen": 140.0,
        "soil_phosphorus": 55.0,
        "soil_potassium": 50.0,
        "soil_moisture": 32.0,
        "irrigation": "Canal",
        "fertilizer_usage": 160.0,
        "vegetation_index_ndvi": 0.70,
        "previous_season_yield": 4.1
    }
    response = client.post("/api/predictions", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "predicted_yield_t_ha" in data
    assert data["predicted_yield_t_ha"] > 0
    assert data["prediction_interval_calibrated"] is True
    assert data["lower_bound_t_ha"] <= data["predicted_yield_t_ha"] <= data["upper_bound_t_ha"]
    assert len(data["top_drivers"]) > 0


# 4. Invalid Prediction Input (Validation Error)
def test_invalid_prediction_input():
    # temperature_max_c lower than temperature_min_c
    invalid_payload = {
        "field_id": "BAD-FLD",
        "crop": "Wheat",
        "season": "Rabi",
        "region": "Punjab",
        "rainfall_mm": 500.0,
        "temperature_min_c": 35.0,
        "temperature_max_c": 15.0,  # Invalid: max < min
        "humidity": 60.0,
        "soil_ph": 6.8,
        "soil_nitrogen": 140.0,
        "soil_phosphorus": 55.0,
        "soil_potassium": 50.0,
        "soil_moisture": 32.0,
        "irrigation": "Canal",
        "fertilizer_usage": 160.0,
    }
    response = client.post("/api/predictions", json=invalid_payload)
    assert response.status_code == 422  # Unprocessable Entity


# 5. Missing Feature Handling
def test_missing_features_prediction():
    # Omits optional NDVI, previous yield, and GPS coordinates
    partial_payload = {
        "field_id": "PARTIAL-FLD",
        "crop": "Rice",
        "season": "Kharif",
        "region": "West Bengal",
        "rainfall_mm": 1100.0,
        "temperature_min_c": 22.0,
        "temperature_max_c": 33.0,
        "humidity": 80.0,
        "soil_ph": 6.5,
        "soil_nitrogen": 120.0,
        "soil_phosphorus": 45.0,
        "soil_potassium": 50.0,
        "soil_moisture": 40.0,
        "irrigation": "Canal",
        "fertilizer_usage": 150.0
    }
    response = client.post("/api/predictions", json=partial_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["predicted_yield_t_ha"] > 0
    assert len(data["data_quality_warnings"]) > 0


# 6. CSV Upload and Schema Validation
def test_csv_upload_validation():
    csv_content = (
        "field_id,crop,season,region,rainfall_mm,temperature_min_c,temperature_max_c,humidity,soil_ph,soil_nitrogen,soil_phosphorus,soil_potassium,soil_moisture,irrigation,fertilizer_usage,actual_yield_t_ha\n"
        "F1,Wheat,Rabi,Punjab,450,11,25,60,6.8,140,50,50,30,Canal,150,4.2\n"
        "F2,Rice,Kharif,Bihar,1200,22,34,80,6.5,130,45,55,40,Canal,160,3.8\n"
    )
    # Replicate to meet minimum 10 rows
    for i in range(3, 15):
        csv_content += f"F{i},Maize,Kharif,Karnataka,650,18,31,65,6.6,130,50,50,30,Drip,140,4.5\n"

    response = client.post(
        "/api/datasets/upload",
        files={"file": ("test_upload.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["target_present"] is True


# 7. Missing-Value Preprocessing Imputation
def test_preprocessor_missing_value_imputation():
    raw_df = pd.DataFrame([{
        "crop": "Wheat",
        "season": "Rabi",
        "region": "Punjab",
        "irrigation": "Canal",
        "rainfall_mm": np.nan,  # missing
        "temperature_min_c": 12.0,
        "temperature_max_c": 25.0,
        "soil_nitrogen": np.nan,  # missing
    }])
    prep = AgriculturalPreprocessor()
    # Mock medians
    prep.num_medians = {"rainfall_mm": 500.0, "soil_nitrogen": 120.0}
    prep.cat_modes = {"crop": "Wheat", "season": "Rabi", "region": "Punjab", "irrigation": "Canal"}
    cleaned, warnings = prep.validate_and_clean_dataframe(raw_df)
    assert len(cleaned) == 1
    assert "soil_ph" in cleaned.columns  # added with NaN for imputer


# 8. True Metric Calculation Logic
def test_regression_metrics_calculation():
    y_true = np.array([3.0, 4.0, 5.0, 2.0])
    y_pred = np.array([3.1, 3.9, 5.2, 2.1])
    lower = np.array([2.5, 3.5, 4.5, 1.5])
    upper = np.array([3.5, 4.5, 5.5, 2.5])

    metrics = calculate_regression_metrics(y_true, y_pred, lower, upper)
    assert metrics["rmse"] > 0
    assert metrics["mae"] > 0
    assert metrics["r2"] > 0.90
    assert metrics["coverage_90"] == 100.0


# 9. Conformal Prediction Interval Behavior
def test_conformal_interval_bounds():
    payload = {
        "field_id": "FLD-INTERVAL",
        "crop": "Wheat",
        "season": "Rabi",
        "region": "Haryana",
        "rainfall_mm": 450.0,
        "temperature_min_c": 11.0,
        "temperature_max_c": 26.0,
        "humidity": 55.0,
        "soil_ph": 7.0,
        "soil_nitrogen": 130.0,
        "soil_phosphorus": 50.0,
        "soil_potassium": 50.0,
        "soil_moisture": 30.0,
        "irrigation": "Canal",
        "fertilizer_usage": 150.0,
    }
    res = client.post("/api/predictions", json=payload).json()
    assert res["lower_bound_t_ha"] < res["upper_bound_t_ha"]
    # Check bounds encompass point estimate
    assert res["lower_bound_t_ha"] <= res["predicted_yield_t_ha"] <= res["upper_bound_t_ha"]


# 10. Anomaly Detection Logic
def test_anomaly_detection():
    # Extreme drought and heat stress input
    extreme_data = {
        "field_id": "STRESS-FLD-99",
        "crop": "Wheat",
        "rainfall_mm": 45.0,  # Severe drought
        "temperature_max_c": 44.5,  # Acute heat stress
        "soil_nitrogen": 30.0,  # Severe N depletion
        "vegetation_index_ndvi": 0.20,  # Severe stunting
        "soil_ph": 4.8,  # Severe acidity
    }
    anomalies = detect_agronomic_anomalies(extreme_data)
    anomaly_types = [a.type for a in anomalies]
    assert any("Drought" in t for t in anomaly_types)
    assert any("Heat Stress" in t for t in anomaly_types)
    assert any("Nitrogen" in t for t in anomaly_types)


# 11. Low-Yield Alert Generation
def test_low_yield_alert_generation():
    anomalies = []
    # Predicted yield 1.2 t/ha is below Wheat critical threshold (2.2 t/ha)
    alerts = evaluate_and_generate_alerts(
        data={"field_id": "TEST-ALERT-01", "crop": "Wheat", "region": "Punjab"},
        predicted_yield=1.2,
        anomalies=anomalies
    )
    assert len(alerts) >= 1
    assert alerts[0].severity == "Critical"
    assert "Sub-Critical" in alerts[0].rule_name


# 12. Alert Acknowledgment and Resolution API
def test_alert_lifecycle():
    # 1. Fetch existing alerts
    alerts_res = client.get("/api/alerts")
    assert alerts_res.status_code == 200
    alerts_list = alerts_res.json()

    if len(alerts_list) > 0:
        target_id = alerts_list[0]["alert_id"]
        # Acknowledge
        ack_res = client.patch(f"/api/alerts/{target_id}", json={"status": "acknowledged"})
        assert ack_res.status_code == 200
        assert ack_res.json()["status"] == "acknowledged"

        # Resolve
        res_res = client.patch(f"/api/alerts/{target_id}", json={"status": "resolved"})
        assert res_res.status_code == 200
        assert res_res.json()["status"] == "resolved"


# 13. Prediction History Persistence
def test_prediction_history_persistence():
    res = client.get("/api/predictions/history?limit=10")
    assert res.status_code == 200
    data = res.json()
    assert "total" in data
    assert "items" in data
    assert isinstance(data["items"], list)


# 14. Model Comparison & Evaluation API
def test_model_comparison_and_evaluation_endpoints():
    comp_res = client.get("/api/models")
    assert comp_res.status_code == 200
    comp_data = comp_res.json()
    assert len(comp_data["models"]) >= 2
    # Ensure Dummy Baseline is included
    algo_names = [m["algorithm"] for m in comp_data["models"]]
    assert "DummyRegressor" in algo_names

    eval_res = client.get("/api/models/evaluation")
    assert eval_res.status_code == 200
    eval_data = eval_res.json()
    assert "overall_metrics" in eval_data
    assert "scatter_points" in eval_data
    assert "residual_distribution" in eval_data


# 15. Analytics Dashboard Endpoints
def test_analytics_endpoints():
    ov = client.get("/api/analytics/overview")
    assert ov.status_code == 200
    assert "total_predictions" in ov.json()

    trends = client.get("/api/analytics/yield-trends")
    assert trends.status_code == 200
    assert "trends" in trends.json()

    fi = client.get("/api/analytics/feature-importance")
    assert fi.status_code == 200
    assert isinstance(fi.json(), list)
