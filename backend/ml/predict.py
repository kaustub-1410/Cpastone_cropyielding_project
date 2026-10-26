"""
Standalone CLI prediction utility for Crop Yield Prediction System (BT195).
Demonstrates quick terminal inference without starting the API server.
"""

import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.schemas import PredictionInput
from app.services.prediction_service import run_single_prediction

def predict_cli():
    print("=" * 80)
    print("CROP YIELD PREDICTION SYSTEM (BT195) - CLI INFERENCE DEMO")
    print("=" * 80)

    # Example test sample: Wheat in Punjab
    sample_input = PredictionInput(
        field_id="FLD-DEMO-01",
        crop="Wheat",
        season="Rabi",
        region="Punjab",
        latitude=30.90,
        longitude=75.85,
        rainfall_mm=480.0,
        temperature_min_c=11.5,
        temperature_max_c=25.0,
        humidity=65.0,
        soil_ph=7.0,
        soil_nitrogen=150.0,
        soil_phosphorus=55.0,
        soil_potassium=50.0,
        soil_moisture=34.0,
        irrigation="Canal",
        fertilizer_usage=180.0,
        vegetation_index_ndvi=0.72,
        previous_season_yield=4.3
    )

    print(f"[*] Input Data: {sample_input.crop} in {sample_input.region} ({sample_input.season})")
    print(f"    Rainfall: {sample_input.rainfall_mm}mm | Temp: {sample_input.temperature_min_c}-{sample_input.temperature_max_c}°C | Soil pH: {sample_input.soil_ph}")
    
    response = run_single_prediction(sample_input)

    print("\n[+] PREDICTION RESULT:")
    print(f"    Predicted Yield: {response.predicted_yield_t_ha} t/ha")
    print(f"    Calibrated 90% Confidence Interval: [{response.lower_bound_t_ha} - {response.upper_bound_t_ha}] t/ha")
    print(f"    Model: {response.model_name} ({response.model_version})")

    print("\n[+] TOP EXPLAINABILITY DRIVERS:")
    for d in response.top_drivers:
        sign = "+" if d.impact > 0 else ""
        print(f"    - {d.feature_name}: {sign}{d.impact} t/ha ({d.direction}) -> {d.description}")

    if response.anomalies:
        print("\n[!] DETECTED ANOMALIES:")
        for a in response.anomalies:
            print(f"    - [{a.severity}] {a.type}: {a.explanation}")
    else:
        print("\n[*] No severe agronomic anomalies detected in input.")

    if response.alerts:
        print("\n[!] ACTIVE ALERTS:")
        for al in response.alerts:
            print(f"    - [{al.severity}] {al.rule_name}: {al.reason}")
    else:
        print("[*] No low-yield alerts triggered.")

    print("=" * 80)

if __name__ == "__main__":
    predict_cli()
