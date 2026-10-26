# System Architecture & Technical Specifications

**Project Title:** Crop Yield Prediction System Using AI/ML  
**Project ID:** BT195  
**Domain:** Artificial Intelligence, Machine Learning, Precision Agriculture, Time-Series Analysis  
**Team Members:** Pawan Singh & Ishika Pandey  
**Project Supervisor:** Mr. Rishabh Srivastava  

---

## 1. Architectural Pipeline

The system is architected as an end-to-end, decoupled micro-monolith:

```
┌────────────────────────────────────────────────────────────────────────┐
│                          Data Ingestion Layer                          │
│   • Multi-feature CSV parsing (weather, soil, satellite NDVI, yield)   │
│   • Schema integrity verification & type coercion                      │
│   • Duplicate detection & provenance recording                         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   Preprocessing & Feature Engineering                  │
│   • Missing-value imputation (median for numerical, mode for cat)      │
│   • Growing Degree Days: GDD = max(0, T_avg - 10.0)                    │
│   • De Martonne Aridity Index: I = Rain / (T_avg + 10.0)               │
│   • Soil NPK Interaction: NPK_total, N/(P+K) balance ratio             │
│   • Effective Soil Moisture & NDVI vegetative vigor score              │
│   • One-Hot categorical encoding with standard scaling (zero leakage)  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   Machine Learning & Benchmarking                      │
│   • Leakage-safe Train (70%) / Validation (15%) / Test (15%) split     │
│   • Multi-model tournament:                                            │
│       - DummyRegressor (Mean Baseline)                                 │
│       - Ridge Linear Regressor                                         │
│       - Random Forest Regressor (100 trees, depth 12)                  │
│       - XGBoost Regressor (120 estimators, lr 0.07)                    │
│   • Model Selection strictly based on Validation RMSE                  │
│   • Final Evaluation on held-out untouched Test Set                    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                  Conformal Prediction & Explainability                 │
│   • Calibrated 90% Conformal Prediction Intervals                      │
│   • Nonconformity residual quantile computed on validation set         │
│   • Explainable AI (XAI): Linear Shapley Attribution & Tree Importance │
│   • Anomaly detection (drought, acute heat >42°C, pH abnormalities)    │
│   • Low-Yield Rule Alert Engine with deduplication & lifecycle state   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                         FastAPI REST Engine                            │
│   • Asynchronous Swagger / OpenAPI endpoints                           │
│   • SQLite ORM with SQLAlchemy persistence                             │
│   • Sub-millisecond in-memory model inference caching                  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        Modern React Dashboard                          │
│   • Precision Agriculture UI (Tailwind CSS emerald/slate theme)        │
│   • Recharts for Actual vs Predicted, Trends & Residual Distributions  │
│   • OpenStreetMap Leaflet geographic spatial visualization             │
│   • Alert management with Acknowledge / Resolve audit trail            │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Agronomic Feature Engineering Formulations

1. **Growing Degree Days (GDD):**
   $$\text{GDD} = \max\left(0, \frac{T_{\text{min}} + T_{\text{max}}}{2} - T_{\text{base}}\right), \quad T_{\text{base}} = 10.0^\circ\text{C}$$

2. **De Martonne Aridity Index:**
   $$I_{\text{aridity}} = \frac{\text{Rainfall (mm)}}{\overline{T} + 10.0}$$

3. **NPK Macronutrient Balance:**
   $$\text{NPK}_{\text{total}} = N + P + K, \quad \text{NPK}_{\text{ratio}} = \frac{N}{P + K + 10^{-5}}$$

4. **Soil pH Optimality Deviation:**
   $$\Delta \text{pH} = |\text{pH} - 6.8|$$

---

## 3. Conformal Prediction Interval Estimation

Instead of arbitrary confidence bands, we employ distribution-free, split-conformal inference:
1. On validation set $D_{\text{val}} = \{(x_i, y_i)\}_{i=1}^{n_{\text{val}}}$, calculate nonconformity absolute residuals:
   $$R_i = |y_i - \hat{\mu}(x_i)|$$
2. For confidence level $1 - \alpha = 0.90$, determine the calibrated finite-sample quantile:
   $$q = \text{Quantile}\left(\{R_i\}, \min\left(1.0, (1 - \alpha)\left(1 + \frac{1}{n_{\text{val}}}\right)\right)\right)$$
3. The prediction interval for a new observation $x_{\text{new}}$ is:
   $$C(x_{\text{new}}) = \left[\max(0, \hat{y} - q), \hat{y} + q\right]$$
4. Guaranteed coverage property:
   $$P(Y \in C(X)) \ge 1 - \alpha$$
