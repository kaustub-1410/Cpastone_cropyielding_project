# REST API Documentation

**Base URL:** `http://localhost:8000/api`  
**Interactive Swagger UI:** `http://localhost:8000/docs`  
**Alternative ReDoc:** `http://localhost:8000/redoc`  

---

## Endpoints Overview

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Returns service status, model readiness, and diagnostic checks |
| `GET` | `/metadata` | Returns supported crops, regions, seasons, and feature schemas |
| `POST` | `/predictions` | Generates a single pre-harvest crop yield prediction |
| `POST` | `/predictions/batch` | Generates predictions for up to 500 field records |
| `GET` | `/predictions/history` | Returns paginated prediction records with search & filters |
| `GET` | `/predictions/{id}` | Returns complete prediction detail with XAI and anomalies |
| `POST` | `/datasets/upload` | Validates and imports a CSV dataset |
| `GET` | `/datasets` | Lists registered datasets and provenance metadata |
| `GET` | `/datasets/summary` | Returns summary statistics of the active training dataset |
| `GET` | `/datasets/{id}/preview` | Returns preview records from a registered dataset |
| `POST` | `/datasets/generate-sample` | Generates realistic synthetic agricultural dataset |
| `GET` | `/models` | Returns model registry and comparative validation/test benchmarks |
| `GET` | `/models/evaluation` | Returns actual evaluation scatter points, residuals, and per-crop stats |
| `POST` | `/models/train` | Triggers background model training run |
| `GET` | `/models/status` | Returns whether background training is active |
| `GET` | `/alerts` | Returns low-yield alerts with multi-dimensional filtering |
| `PATCH` | `/alerts/{alert_id}` | Acknowledges or resolves an active alert |
| `GET` | `/analytics/overview` | Returns live executive dashboard metrics and top crops |
| `GET` | `/analytics/yield-trends` | Returns temporal multi-year yield trajectories |
| `GET` | `/analytics/feature-importance` | Returns global feature importance ranking |
| `GET` | `/analytics/crops` | Returns crop-specific agronomic summary statistics |

---

## Example: Create Yield Prediction

**Request:**
`POST /api/predictions`
```json
{
  "field_id": "FLD-101",
  "crop": "Wheat",
  "season": "Rabi",
  "region": "Punjab",
  "latitude": 30.90,
  "longitude": 75.85,
  "rainfall_mm": 480.0,
  "temperature_min_c": 11.5,
  "temperature_max_c": 25.0,
  "humidity": 65.0,
  "soil_ph": 6.9,
  "soil_nitrogen": 155.0,
  "soil_phosphorus": 55.0,
  "soil_potassium": 52.0,
  "soil_moisture": 33.0,
  "irrigation": "Canal",
  "fertilizer_usage": 175.0,
  "vegetation_index_ndvi": 0.74,
  "previous_season_yield": 4.4
}
```

**Response (`200 OK`):**
```json
{
  "prediction_id": "PRD-A480FE21",
  "field_id": "FLD-101",
  "crop": "Wheat",
  "season": "Rabi",
  "region": "Punjab",
  "predicted_yield_t_ha": 3.97,
  "lower_bound_t_ha": 3.58,
  "upper_bound_t_ha": 4.36,
  "prediction_interval_calibrated": true,
  "confidence_level": 0.90,
  "forecast_date": "2026-10-27T01:10:45Z",
  "model_name": "Ridge Linear Regressor",
  "model_version": "v1.0.0",
  "top_drivers": [
    {
      "feature": "crop_Wheat",
      "feature_name": "Wheat",
      "impact": 0.651,
      "direction": "positive",
      "description": "Wheat contributes positively (+0.65 t/ha) to predicted yield."
    }
  ],
  "anomalies": [],
  "alerts": [],
  "data_quality_warnings": []
}
```
