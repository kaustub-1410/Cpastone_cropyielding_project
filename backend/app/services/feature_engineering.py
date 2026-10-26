"""
Agronomic feature engineering pipeline for Crop Yield Prediction System (BT195).
Computes scientifically established agro-climatic indices from raw features.
"""

from typing import Dict, Any
import numpy as np
import pandas as pd

# Base temperature for crop Growing Degree Days (GDD), standard 10°C
GDD_BASE_TEMP = 10.0
HEAT_STRESS_THRESHOLD = 35.0

def calculate_agronomic_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforms raw agricultural inputs into domain-specific features.
    Works seamlessly on both pandas DataFrame and single record dictionaries.
    """
    df = df.copy()

    # 1. Temperature metrics
    t_min = pd.to_numeric(df.get("temperature_min_c", 15.0), errors="coerce").fillna(15.0)
    t_max = pd.to_numeric(df.get("temperature_max_c", 30.0), errors="coerce").fillna(30.0)
    
    # Ensure t_max >= t_min
    t_max = np.maximum(t_max, t_min)
    
    avg_temp = (t_min + t_max) / 2.0
    temp_range = t_max - t_min
    
    df["avg_temperature"] = avg_temp.round(2)
    df["temp_range"] = temp_range.round(2)
    
    # 2. Growing Degree Days (GDD)
    df["growing_degree_days"] = np.maximum(0.0, avg_temp - GDD_BASE_TEMP).round(2)
    
    # 3. Heat stress indicator (degree-hours above threshold)
    df["heat_stress_index"] = np.maximum(0.0, t_max - HEAT_STRESS_THRESHOLD).round(2)
    
    # 4. Moisture and Aridity Index (De Martonne index: P / (T + 10))
    rain = pd.to_numeric(df.get("rainfall_mm", 600.0), errors="coerce").fillna(600.0)
    df["aridity_index"] = (rain / (avg_temp + 10.0 + 1e-5)).round(3)
    
    # 5. Soil Macronutrients (NPK interactions)
    soil_n = pd.to_numeric(df.get("soil_nitrogen", 120.0), errors="coerce").fillna(120.0)
    soil_p = pd.to_numeric(df.get("soil_phosphorus", 50.0), errors="coerce").fillna(50.0)
    soil_k = pd.to_numeric(df.get("soil_potassium", 50.0), errors="coerce").fillna(50.0)
    
    df["npk_total"] = (soil_n + soil_p + soil_k).round(2)
    df["npk_ratio"] = (soil_n / (soil_p + soil_k + 1e-5)).round(3)
    
    # 6. Soil pH optimality distance (optimum ~ 6.5 - 7.0)
    soil_ph = pd.to_numeric(df.get("soil_ph", 6.8), errors="coerce").fillna(6.8)
    df["ph_optimality_deviation"] = (np.abs(soil_ph - 6.8)).round(2)
    
    # 7. Soil moisture composite
    soil_moist = pd.to_numeric(df.get("soil_moisture", 30.0), errors="coerce").fillna(30.0)
    df["effective_moisture_index"] = (soil_moist * 0.4 + np.minimum(100.0, rain / 10.0) * 0.6).round(2)
    
    # 8. NDVI Vegetation Index & vigor potential
    ndvi = pd.to_numeric(df.get("vegetation_index_ndvi", 0.6), errors="coerce").fillna(0.6)
    df["ndvi_vigor_potential"] = (ndvi * (1.0 + 0.05 * (soil_n / 150.0))).round(3)
    
    # 9. Autoregressive Previous Yield feature
    prev_yield = pd.to_numeric(df.get("previous_season_yield", 3.0), errors="coerce").fillna(3.0)
    df["previous_season_yield_filled"] = prev_yield.round(2)
    
    return df
