# Testing & Verification Guide

This document records the automated testing suite and verification results for the Crop Yield Prediction System (BT195).

---

## 1. Automated Test Execution

The automated test suite is implemented using `pytest` and `fastapi.testclient.TestClient`.

### Running Tests on Windows

```powershell
cd backend
python -m pytest tests/test_api.py -v
```

### Verification Results

All 15 required acceptance criteria pass successfully:

| Test Case | Description | Result |
|---|---|---|
| `test_health_endpoint` | Verifies `/api/health` status, database connection, and diagnostics | **PASSED** |
| `test_metadata_endpoint` | Verifies `/api/metadata` crop lists, regions, and feature schemas | **PASSED** |
| `test_valid_prediction` | Validates single pre-harvest forecast, conformal interval, and XAI | **PASSED** |
| `test_invalid_prediction_input` | Validates rejection of inverted temperatures ($T_{\text{max}} < T_{\text{min}}$) with HTTP 422 | **PASSED** |
| `test_missing_features_prediction` | Tests graceful imputation of missing optional parameters with warnings | **PASSED** |
| `test_csv_upload_validation` | Tests CSV parsing, schema checking, and row minimum validation | **PASSED** |
| `test_preprocessor_missing_value_imputation` | Tests training-fitted median/mode replacement logic | **PASSED** |
| `test_regression_metrics_calculation` | Validates mathematical correctness of RMSE, MAE, R², and MAPE | **PASSED** |
| `test_conformal_interval_bounds` | Tests that $L \le \hat{y} \le U$ holds for 90% confidence intervals | **PASSED** |
| `test_anomaly_detection` | Tests drought, extreme heat (>42°C), and NPK deficiency identification | **PASSED** |
| `test_low_yield_alert_generation` | Tests sub-critical yield rule triggering and severity assignment | **PASSED** |
| `test_alert_lifecycle` | Tests acknowledgment and resolution state updates with audit timestamps | **PASSED** |
| `test_prediction_history_persistence` | Tests SQLite database persistence across requests | **PASSED** |
| `test_model_comparison_and_evaluation_endpoints` | Verifies naive baseline inclusion and evaluation endpoints | **PASSED** |
| `test_analytics_endpoints` | Verifies overview statistics, yield trends, and feature importance | **PASSED** |

**Summary:** 15 passed in 8.93s.
