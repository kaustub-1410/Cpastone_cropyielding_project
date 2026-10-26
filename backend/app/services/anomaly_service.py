"""
Agronomic Anomaly Detection Service for Crop Yield Prediction System (BT195).
Identifies extreme weather events, soil nutrient deficiencies, abnormal NDVI drops, and out-of-distribution inputs.
Distinguishes abnormal observations from confirmed crop failures.
"""

from typing import List, Dict, Any, Optional
from app.schemas import AnomalyItem

def detect_agronomic_anomalies(data: Dict[str, Any]) -> List[AnomalyItem]:
    """
    Evaluates input parameters against physiological and statistical thresholds.
    Returns structured list of detected anomalies with recommended verification actions.
    """
    anomalies: List[AnomalyItem] = []
    field_id = str(data.get("field_id", "Field"))
    crop = str(data.get("crop", "Unknown"))

    # 1. Extreme Drought or Flood / Waterlogging
    rainfall = float(data.get("rainfall_mm", 500.0))
    if rainfall < 120.0:
        anomalies.append(AnomalyItem(
            type="Severe Moisture Deficit / Drought Risk",
            severity="High",
            affected_field=field_id,
            triggering_value=rainfall,
            reference_range="350 - 1400 mm",
            explanation=f"Cumulative rainfall of {rainfall:.1f} mm indicates severe meteorological drought during crop cycle.",
            suggested_action="Verify supplementary irrigation capacity (drip/canal) and assess soil moisture tension."
        ))
    elif rainfall > 2200.0:
        anomalies.append(AnomalyItem(
            type="Excessive Rainfall / Waterlogging Risk",
            severity="Warning",
            affected_field=field_id,
            triggering_value=rainfall,
            reference_range="350 - 1400 mm",
            explanation=f"Excessive rainfall ({rainfall:.1f} mm) may cause root hypoxia, nutrient leaching, and root rot diseases.",
            suggested_action="Inspect field drainage channels and monitor for foliar fungal diseases."
        ))

    # 2. Extreme Thermal Heat Stress
    t_max = float(data.get("temperature_max_c", 30.0))
    if t_max >= 42.0:
        anomalies.append(AnomalyItem(
            type="Acute Thermal Heat Stress",
            severity="Critical" if t_max >= 44.0 else "High",
            affected_field=field_id,
            triggering_value=t_max,
            reference_range="20.0 - 36.0 °C",
            explanation=f"Maximum temperature reached {t_max:.1f} °C, exceeding thermal limits for anthesis/grain-filling in {crop}.",
            suggested_action="Schedule light nighttime/sprinkler irrigation to mitigate canopy microclimate overheating."
        ))

    # 3. Abnormal NDVI / Vegetative Stunting
    ndvi = data.get("vegetation_index_ndvi")
    if ndvi is not None:
        ndvi_val = float(ndvi)
        if ndvi_val < 0.28:
            anomalies.append(AnomalyItem(
                type="Severe Vegetative Canopy Stunting (NDVI)",
                severity="High",
                affected_field=field_id,
                triggering_value=ndvi_val,
                reference_range="0.45 - 0.85 NDVI",
                explanation=f"NDVI value of {ndvi_val:.3f} indicates drastically sparse photosynthetic biomass or germination failure.",
                suggested_action="Conduct drone/ground scouting to detect potential pest outbreak, herbicide drift, or seedling damping-off."
            ))

    # 4. Critical Soil Nutrient Depletion (NPK)
    soil_n = float(data.get("soil_nitrogen", 120.0))
    soil_p = float(data.get("soil_phosphorus", 50.0))
    soil_k = float(data.get("soil_potassium", 50.0))

    if soil_n < 50.0:
        anomalies.append(AnomalyItem(
            type="Severe Available Nitrogen Depletion",
            severity="Warning",
            affected_field=field_id,
            triggering_value=soil_n,
            reference_range="90 - 250 kg/ha",
            explanation=f"Soil available nitrogen ({soil_n:.1f} kg/ha) is deficient for optimal chlorophyll synthesis in {crop}.",
            suggested_action="Consider split-application top dressing of urea or bio-fertilizers based on leaf color chart."
        ))

    if soil_p < 15.0 or soil_k < 25.0:
        anomalies.append(AnomalyItem(
            type="Critical Mineral Nutrient Deficiency (P/K)",
            severity="Warning",
            affected_field=field_id,
            triggering_value=min(soil_p, soil_k),
            reference_range="P: 25-80 kg/ha, K: 40-200 kg/ha",
            explanation="Phosphorus or Potassium levels are below the critical threshold for root vigor and water regulation.",
            suggested_action="Perform lab soil test and plan basal DAP/MOP replenishment."
        ))

    # 5. Extreme Soil Reaction (Acidity / Alkalinity)
    soil_ph = float(data.get("soil_ph", 6.8))
    if soil_ph < 5.2:
        anomalies.append(AnomalyItem(
            type="Severe Soil Acidification",
            severity="High",
            affected_field=field_id,
            triggering_value=soil_ph,
            reference_range="6.0 - 7.5 pH",
            explanation=f"Strong soil acidity (pH {soil_ph:.2f}) causes aluminum/manganese toxicity and locks phosphorus availability.",
            suggested_action="Apply agricultural lime (calcium carbonate) or dolomite to raise soil buffering capacity."
        ))
    elif soil_ph > 8.7:
        anomalies.append(AnomalyItem(
            type="Severe Soil Alkalinity / Sodicity",
            severity="High",
            affected_field=field_id,
            triggering_value=soil_ph,
            reference_range="6.0 - 7.5 pH",
            explanation=f"Strongly alkaline soil (pH {soil_ph:.2f}) causes micronutrient deficiencies (Zinc, Iron) and dispersion.",
            suggested_action="Apply agricultural gypsum and organic green manure to leach sodium and improve permeability."
        ))

    # 6. Low Soil Moisture with Rainfed Irrigation
    moisture = float(data.get("soil_moisture", 30.0))
    irrigation = str(data.get("irrigation", "Canal"))
    if moisture < 14.0 and irrigation == "Rainfed":
        anomalies.append(AnomalyItem(
            type="Critical Soil Moisture Depletion (Rainfed)",
            severity="Critical",
            affected_field=field_id,
            triggering_value=moisture,
            reference_range="22 - 45 % Volumetric Moisture",
            explanation="Volumetric soil moisture is approaching permanent wilting point without irrigation infrastructure.",
            suggested_action="Implement mulching, emergency water hauling, or anti-transpirant foliar spray if feasible."
        ))

    return anomalies
