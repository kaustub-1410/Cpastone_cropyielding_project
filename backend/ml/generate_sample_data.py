"""
Sample agricultural dataset generator for Crop Yield Prediction System (BT195).
Generates realistic agro-climatic observations based on established agronomic principles.
NOTE: All generated records are synthetic simulations for development, testing, and benchmarking.
"""

import os
import sys
from pathlib import Path
import numpy as np
import pandas as pd

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.config import settings

CROPS = ["Wheat", "Rice", "Maize", "Soybean", "Cotton", "Barley", "Sorghum"]
SEASONS = ["Kharif", "Rabi", "Zaid"]
IRRIGATIONS = ["Canal", "Tube Well", "Drip", "Sprinkler", "Rainfed"]

REGIONS_COORDS = {
    "Punjab": (30.90, 75.85),
    "Haryana": (29.68, 76.99),
    "Uttar Pradesh": (26.44, 80.33),
    "Madhya Pradesh": (23.25, 77.41),
    "Maharashtra": (19.99, 73.78),
    "Karnataka": (15.45, 75.00),
    "Bihar": (25.59, 85.13),
    "Rajasthan": (26.91, 75.78),
    "West Bengal": (23.23, 87.86),
    "Gujarat": (22.56, 72.92),
}

# Agronomic optimal parameters per crop
CROP_PROFILES = {
    "Wheat": {
        "base_yield": 4.2,
        "opt_rain": 450,
        "opt_temp_min": 10.0,
        "opt_temp_max": 26.0,
        "opt_ph": 6.8,
        "n_demand": 140,
        "p_demand": 55,
        "k_demand": 50,
        "primary_season": "Rabi",
    },
    "Rice": {
        "base_yield": 3.8,
        "opt_rain": 1100,
        "opt_temp_min": 22.0,
        "opt_temp_max": 33.0,
        "opt_ph": 6.5,
        "n_demand": 130,
        "p_demand": 45,
        "k_demand": 55,
        "primary_season": "Kharif",
    },
    "Maize": {
        "base_yield": 4.6,
        "opt_rain": 650,
        "opt_temp_min": 18.0,
        "opt_temp_max": 31.0,
        "opt_ph": 6.6,
        "n_demand": 150,
        "p_demand": 60,
        "k_demand": 60,
        "primary_season": "Kharif",
    },
    "Soybean": {
        "base_yield": 2.2,
        "opt_rain": 750,
        "opt_temp_min": 20.0,
        "opt_temp_max": 30.0,
        "opt_ph": 6.5,
        "n_demand": 60,  # Legume fixates N
        "p_demand": 70,
        "k_demand": 65,
        "primary_season": "Kharif",
    },
    "Cotton": {
        "base_yield": 2.1,
        "opt_rain": 700,
        "opt_temp_min": 20.0,
        "opt_temp_max": 34.0,
        "opt_ph": 7.2,
        "n_demand": 120,
        "p_demand": 50,
        "k_demand": 70,
        "primary_season": "Kharif",
    },
    "Barley": {
        "base_yield": 3.2,
        "opt_rain": 380,
        "opt_temp_min": 9.0,
        "opt_temp_max": 25.0,
        "opt_ph": 7.0,
        "n_demand": 90,
        "p_demand": 40,
        "k_demand": 40,
        "primary_season": "Rabi",
    },
    "Sorghum": {
        "base_yield": 2.0,
        "opt_rain": 450,
        "opt_temp_min": 20.0,
        "opt_temp_max": 34.0,
        "opt_ph": 6.8,
        "n_demand": 80,
        "p_demand": 35,
        "k_demand": 45,
        "primary_season": "Kharif",
    },
}

def generate_agricultural_dataset(num_records: int = 1500, random_seed: int = 42) -> pd.DataFrame:
    """Generate realistic synthetic agricultural records with domain physics."""
    rng = np.random.default_rng(random_seed)
    
    records = []
    years = [2020, 2021, 2022, 2023, 2024]
    
    for i in range(num_records):
        field_num = rng.integers(100, 999)
        field_id = f"FLD-{field_num}"
        crop = rng.choice(CROPS)
        profile = CROP_PROFILES[crop]
        
        region = rng.choice(list(REGIONS_COORDS.keys()))
        base_lat, base_lon = REGIONS_COORDS[region]
        lat = round(base_lat + rng.normal(0, 0.4), 4)
        lon = round(base_lon + rng.normal(0, 0.4), 4)
        
        # Season with bias toward crop's primary season
        season = profile["primary_season"] if rng.random() > 0.25 else rng.choice(SEASONS)
        year = int(rng.choice(years))
        
        # Weather variables
        rain_scale = profile["opt_rain"]
        rainfall_mm = max(40.0, float(rng.normal(rain_scale, rain_scale * 0.25)))
        
        temp_min = float(np.clip(rng.normal(profile["opt_temp_min"], 3.0), 4.0, 32.0))
        temp_max = float(np.clip(temp_min + rng.uniform(8.0, 16.0), temp_min + 3.0, 48.0))
        humidity = float(np.clip(rng.normal(65.0, 15.0), 20.0, 95.0))
        
        # Soil variables
        soil_ph = float(np.clip(rng.normal(profile["opt_ph"], 0.6), 4.5, 9.2))
        soil_n = float(np.clip(rng.normal(profile["n_demand"], 35.0), 30.0, 380.0))
        soil_p = float(np.clip(rng.normal(profile["p_demand"], 18.0), 10.0, 140.0))
        soil_k = float(np.clip(rng.normal(profile["k_demand"], 22.0), 20.0, 260.0))
        soil_moisture = float(np.clip(rng.normal(32.0, 8.0), 8.0, 58.0))
        
        # Farm management
        irrigation = rng.choice(IRRIGATIONS, p=[0.35, 0.30, 0.15, 0.10, 0.10])
        irrigation_factor = {
            "Drip": 1.15,
            "Sprinkler": 1.08,
            "Canal": 1.02,
            "Tube Well": 1.00,
            "Rainfed": 0.85
        }[irrigation]
        
        fertilizer_usage = float(np.clip(rng.normal(160.0, 40.0), 30.0, 350.0))
        
        # NDVI vegetation index
        ndvi_base = 0.65 if rainfall_mm > 500 else 0.48
        ndvi = float(np.clip(rng.normal(ndvi_base, 0.12), 0.15, 0.92))
        
        # Previous season yield
        prev_yield = float(np.clip(rng.normal(profile["base_yield"] * 0.95, 0.6), 0.8, 8.5))
        
        # --- AGRONOMIC RESPONSE CALCULATION ---
        # 1. Rain response (diminishing returns, penalty for drought or waterlogging)
        rain_ratio = rainfall_mm / (profile["opt_rain"] + 1e-5)
        water_score = np.exp(-0.5 * ((rain_ratio - 1.0) / 0.45) ** 2)
        
        # 2. Temperature response (GDD and heat stress penalty)
        avg_temp = (temp_min + temp_max) / 2.0
        opt_avg = (profile["opt_temp_min"] + profile["opt_temp_max"]) / 2.0
        temp_score = np.exp(-0.5 * ((avg_temp - opt_avg) / 5.0) ** 2)
        if temp_max > 38.0:
            temp_score *= (1.0 - (temp_max - 38.0) * 0.05)  # Heat stress penalty
            
        # 3. Soil fertility response (Liebig Law of the Minimum on NPK)
        n_ratio = min(1.3, soil_n / profile["n_demand"])
        p_ratio = min(1.3, soil_p / profile["p_demand"])
        k_ratio = min(1.3, soil_k / profile["k_demand"])
        fertility_score = (0.5 * min(n_ratio, p_ratio, k_ratio) + 0.5 * np.mean([n_ratio, p_ratio, k_ratio]))
        
        # 4. Soil pH response
        ph_diff = abs(soil_ph - profile["opt_ph"])
        ph_score = max(0.6, 1.0 - (ph_diff * 0.15))
        
        # 5. NDVI correlation
        ndvi_score = 0.7 + (ndvi * 0.5)
        
        # 6. Autoregressive soil productivity heritage
        prev_ratio = prev_yield / profile["base_yield"]
        
        # Yield synthesis
        yield_raw = (
            profile["base_yield"]
            * (0.30 * water_score * irrigation_factor)
            + profile["base_yield"] * (0.25 * temp_score)
            + profile["base_yield"] * (0.20 * fertility_score * (fertilizer_usage / 160.0) ** 0.2)
            + profile["base_yield"] * (0.10 * ph_score)
            + profile["base_yield"] * (0.15 * ndvi_score)
        )
        # Combine with previous season yield
        yield_final = 0.75 * yield_raw + 0.25 * (prev_ratio * profile["base_yield"])
        
        # Realistic noise
        yield_final = yield_final + rng.normal(0, 0.18)
        actual_yield = round(float(np.clip(yield_final, 0.6, 9.5)), 2)
        
        records.append({
            "field_id": field_id,
            "crop": crop,
            "season": season,
            "year": year,
            "region": region,
            "latitude": lat,
            "longitude": lon,
            "rainfall_mm": round(rainfall_mm, 1),
            "temperature_min_c": round(temp_min, 1),
            "temperature_max_c": round(temp_max, 1),
            "humidity": round(humidity, 1),
            "soil_ph": round(soil_ph, 2),
            "soil_nitrogen": round(soil_n, 1),
            "soil_phosphorus": round(soil_p, 1),
            "soil_potassium": round(soil_k, 1),
            "soil_moisture": round(soil_moisture, 1),
            "irrigation": irrigation,
            "fertilizer_usage": round(fertilizer_usage, 1),
            "vegetation_index_ndvi": round(ndvi, 3),
            "previous_season_yield": round(prev_yield, 2),
            "actual_yield_t_ha": actual_yield,
            "is_synthetic": True,
            "provenance": "Synthetic Agronomic Simulation - Capstone BT195",
        })
        
    df = pd.DataFrame(records)
    return df

def save_sample_dataset(filepath: Path = None, num_records: int = 1500) -> Path:
    if filepath is None:
        filepath = settings.SAMPLE_DATA_DIR / "crop_yield_sample_dataset.csv"
    filepath.parent.mkdir(parents=True, exist_ok=True)
    df = generate_agricultural_dataset(num_records=num_records)
    df.to_csv(filepath, index=False)
    print(f"[OK] Generated {len(df)} synthetic records to {filepath}")
    return filepath

if __name__ == "__main__":
    out_path = save_sample_dataset()
    print("Sample generation completed successfully.")
