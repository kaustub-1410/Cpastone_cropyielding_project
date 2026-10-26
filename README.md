# Crop Yield Prediction System Using AI/ML

**Capstone Project ID:** BT195  
**Domain:** Artificial Intelligence, Machine Learning, Precision Agriculture, Time-Series Analysis  
**Team Members:** Pawan Singh and Ishika Pandey  
**Project Supervisor:** Mr. Rishabh Srivastava  

---

## 1. Project Overview

The **Crop Yield Prediction System Using AI/ML** is an end-to-end precision agriculture intelligence platform designed to forecast crop yields prior to harvest. By synthesizing meteorological observations, soil physicochemical properties, farm-management practices, and satellite remote-sensing indices (Sentinel-2 NDVI), the system provides statistically sound predictions with calibrated uncertainty bounds for farmers, agronomists, and district-level agricultural planners.

### User Interface Options
1. **AgriSense AI Animated Landing Page (`index.html`):**
   - Single-file, standalone HTML5/CSS/JavaScript with zero npm dependencies.
   - Cinematic agricultural hero scenery, oversized typography, translucent navigation pill, and live API-connected prediction form.
   - Can be opened directly in any web browser by double-clicking `index.html`.
2. **Full Enterprise React Dashboard (`frontend/`):**
   - Comprehensive multi-page precision agriculture application with Leaflet GIS mapping, model retraining triggers, dataset preview tables, and alert lifecycle workflows.
   - Accessible at `http://localhost:5173` via `start_project.bat` or `npm run dev`.

---

## 2. Real Model Evaluation Benchmarks

All metrics shown below were dynamically computed during actual evaluation on 292 held-out test observations (70% Train, 15% Validation, 15% Test split):

| Model | Algorithm | Val RMSE | Val R² | Test RMSE (t/ha) | Test MAE (t/ha) | Test R² | Test MAPE (%) | 90% Conformal Coverage |
|---|---|---|---|---|---|---|---|---|
| **Dummy Baseline (Mean)** | `DummyRegressor` | 0.9386 | -0.0033 | 0.9595 | 0.8625 | -0.0000 | 34.95% | 92.12% |
| **Ridge Linear Regressor** *(Selected Active)* | `Ridge` | **0.2347** | **0.9372** | **0.2413** | **0.1926** | **0.9367** | **7.37%** | **91.10%** |
| **Random Forest Regressor** | `RandomForestRegressor` | 0.2781 | 0.9119 | 0.2667 | 0.2046 | 0.9227 | 7.87% | 90.07% |
| **XGBoost Regressor** | `XGBRegressor` | 0.2679 | 0.9183 | 0.2564 | 0.1936 | 0.9286 | 7.40% | 93.49% |

*Note: Model selection is conducted strictly on the validation set. Conformal residual quantile $q_{90} = \pm 0.387\text{ t/ha}$.*

---

## 3. Directory Structure

```
c:\Users\kaust\Downloads\Capstone_Crope_Yield_Detetction_System\
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI application entrypoint & lifecycle
│   │   ├── config.py                # Pydantic environment configuration & directory paths
│   │   ├── database.py              # SQLite SQLAlchemy engine & session factory
│   │   ├── schemas.py               # Pydantic request/response validation schemas
│   │   ├── api/                     # REST API routers
│   │   │   ├── health.py            # /api/health and /api/metadata
│   │   │   ├── predictions.py       # Single, batch, history & detail endpoints
│   │   │   ├── datasets.py          # CSV upload, preview & synthetic generator
│   │   │   ├── models.py            # Registry, evaluation reports & retraining
│   │   │   ├── alerts.py            # Low-yield alerts & lifecycle updates
│   │   │   └── analytics.py         # Dashboard KPIs, yield trends & feature importance
│   │   ├── services/                # Business & agronomic logic
│   │   │   ├── preprocessing.py     # Imputation, encoding & standard scaling
│   │   │   ├── feature_engineering.py # GDD, aridity index, NPK balance, NDVI vigor
│   │   │   ├── prediction_service.py # Inference pipeline & conformal bounds
│   │   │   ├── explanation_service.py # SHAP & exact linear feature drivers
│   │   │   ├── anomaly_service.py   # Meteorological & soil stress detectors
│   │   │   ├── alert_service.py     # Rule engine with deduplication
│   │   │   └── evaluation_service.py # RMSE, MAE, R², MAPE, bias, coverage
│   │   └── models/
│   │       ├── db_models.py         # SQLAlchemy ORM tables (Predictions, Alerts, etc.)
│   │       └── model_loader.py      # In-memory cached model loading
│   ├── ml/
│   │   ├── generate_sample_data.py  # Agronomic synthetic data simulation
│   │   ├── train.py                 # Multi-model benchmarking & conformal calibration
│   │   ├── evaluate.py              # Test set evaluation & residual analysis
│   │   ├── predict.py               # Standalone CLI prediction demo
│   │   └── model_comparison.py     # Terminal benchmark table display
│   ├── artifacts/                   # Saved model joblibs & evaluation reports
│   ├── data/                        # SQLite DB & CSV storage
│   ├── tests/
│   │   └── test_api.py              # 15 automated pytest integration tests
│   ├── requirements.txt             # Python dependencies
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/layout/       # AppLayout with sidebar & live status widget
│   │   ├── pages/                   # 8 complete application pages
│   │   │   ├── OverviewPage.tsx     # KPIs, trends, crop distributions, alerts feed
│   │   │   ├── PredictionPage.tsx   # Interactive form, presets, conformal bounds, XAI
│   │   │   ├── DatasetsPage.tsx     # CSV upload, schema check, synthetic generator
│   │   │   ├── EvaluationPage.tsx   # Model comparison table, scatter, residuals
│   │   │   ├── GeographicPage.tsx   # OpenStreetMap Leaflet spatial visualization
│   │   │   ├── AlertsPage.tsx       # Severity filters & acknowledge/resolve workflow
│   │   │   ├── HistoryPage.tsx      # Searchable prediction table & CSV export
│   │   │   └── AboutPage.tsx        # Project BT195 details, equations, team info
│   │   ├── services/api.ts          # Axios API client functions
│   │   ├── types/index.ts           # TypeScript interfaces
│   │   ├── App.tsx                  # React Router configuration
│   │   ├── main.tsx
│   │   └── index.css                # Tailwind CSS & Leaflet styling
│   ├── package.json
│   └── vite.config.ts
├── docs/
│   ├── architecture.md
│   ├── api-documentation.md
│   └── testing.md
├── start_project.bat                # Windows one-click launcher
├── .gitignore
└── README.md
```

---

## 4. Windows Setup & Execution Guide

### Option A: One-Command Windows Launcher (Recommended)
Simply double-click or run from Command Prompt / PowerShell:
```cmd
start_project.bat
```
This launcher checks Python and Node.js, verifies model artifacts, starts the backend on port `8000`, starts the frontend on port `5173`, and opens your default web browser automatically.

---

### Option B: Manual Step-by-Step Setup

#### Step 1: Backend Setup
Open a Windows Command Prompt or PowerShell:
```cmd
cd backend
python -m pip install -r requirements.txt
```

Train baseline and machine learning models:
```cmd
python -m ml.train
```

Run evaluation and generate actual metrics:
```cmd
python -m ml.evaluate
```

View terminal comparison table:
```cmd
python -m ml.model_comparison
```

Test standalone CLI inference:
```cmd
python -m ml.predict
```

Run automated pytest test suite:
```cmd
python -m pytest tests/test_api.py -v
```

Start the FastAPI server:
```cmd
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
- **Backend Swagger UI:** `http://localhost:8000/docs`
- **Backend Health Check:** `http://localhost:8000/api/health`

#### Step 2: Frontend Setup
Open a second Command Prompt or PowerShell:
```cmd
cd frontend
npm install
npm run dev
```
- **React Dashboard:** `http://localhost:5173`

---

## 5. Technology Stack

- **Machine Learning & Backend:**
  - Python 3.11
  - FastAPI & Uvicorn (Asynchronous REST API)
  - scikit-learn (Preprocessing pipelines, Ridge, Random Forest, Metrics)
  - XGBoost (Gradient-boosted decision trees)
  - SHAP (Explainable AI feature attribution with linear fallback)
  - pandas & NumPy (Tabular data manipulation & numerical linear algebra)
  - SQLAlchemy & SQLite (Relational persistence)
  - Pydantic v2 (Strict schema validation)
  - pytest & httpx (Automated testing)
- **Frontend Dashboard:**
  - React 19 with Vite & TypeScript
  - Tailwind CSS (Precision agriculture emerald & slate palette)
  - Recharts (Interactive line, scatter, and bar charts)
  - Leaflet & React-Leaflet (OpenStreetMap spatial GIS visualization)
  - Lucide React (Icons)
  - Axios (Backend HTTP integration)
  - React Router v7 (Client-side routing)

---

## 6. Responsible Agronomic Use Notice

Yield forecasts provide empirical decision support for crop management, inputs planning, and regional procurement. They do not constitute guaranteed yields. Unforeseen microclimatic anomalies, localized pest infestations, sudden hail events, and unrecorded farm interventions may lead to variations in final harvested yields.
