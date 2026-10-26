"""
Low-Yield Alert Engine for Crop Yield Prediction System (BT195).
Evaluates rule-based thresholds, prevents duplicate active alerts, and persists records in SQLite.
Supports lifecycle status: 'active' -> 'acknowledged' -> 'resolved'.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
from sqlalchemy.orm import Session

from app.models.db_models import AlertRecord
from app.schemas import AlertItem

# Crop baseline low-yield warning thresholds in tonnes per hectare (t/ha)
CROP_YIELD_ALERT_THRESHOLDS = {
    "Wheat": {"critical": 2.2, "warning": 2.8},
    "Rice": {"critical": 2.0, "warning": 2.6},
    "Maize": {"critical": 2.5, "warning": 3.2},
    "Soybean": {"critical": 1.2, "warning": 1.6},
    "Cotton": {"critical": 1.1, "warning": 1.5},
    "Barley": {"critical": 1.6, "warning": 2.1},
    "Sorghum": {"critical": 1.0, "warning": 1.4},
}

def evaluate_and_generate_alerts(
    data: Dict[str, Any],
    predicted_yield: float,
    anomalies: List[Any],
    db: Optional[Session] = None,
    prediction_id: Optional[str] = None
) -> List[AlertItem]:
    """
    Evaluates rule criteria, filters duplicates against active DB alerts,
    and returns newly generated or active alerts.
    """
    alerts: List[AlertItem] = []
    field_id = str(data.get("field_id", "Field-01"))
    crop = str(data.get("crop", "Wheat"))
    region = str(data.get("region", "General"))

    thresholds = CROP_YIELD_ALERT_THRESHOLDS.get(crop, {"critical": 1.5, "warning": 2.2})

    # Rule 1: Predicted yield below critical threshold
    if predicted_yield < thresholds["critical"]:
        alerts.append(AlertItem(
            alert_id=f"ALT-{uuid.uuid4().hex[:8].upper()}",
            field_id=field_id,
            crop=crop,
            region=region,
            severity="Critical",
            rule_name="Predicted Yield Sub-Critical Threshold",
            reason=f"Predicted yield ({predicted_yield:.2f} t/ha) is critically below viable economic benchmark ({thresholds['critical']} t/ha) for {crop}.",
            predicted_yield=round(predicted_yield, 2),
            threshold_value=thresholds["critical"],
            suggested_action="Urgent agronomist inspection required. Verify germination rate and consider emergency rescue fertilization/irrigation."
        ))
    elif predicted_yield < thresholds["warning"]:
        alerts.append(AlertItem(
            alert_id=f"ALT-{uuid.uuid4().hex[:8].upper()}",
            field_id=field_id,
            crop=crop,
            region=region,
            severity="High",
            rule_name="Predicted Yield Below Regional Warning Level",
            reason=f"Predicted yield ({predicted_yield:.2f} t/ha) is below the warning threshold ({thresholds['warning']} t/ha).",
            predicted_yield=round(predicted_yield, 2),
            threshold_value=thresholds["warning"],
            suggested_action="Review soil nutrient status, moisture levels, and weed competition in the target field."
        ))

    # Rule 2: Sharp drop (>25%) compared to previous season yield
    prev_yield = data.get("previous_season_yield")
    if prev_yield is not None:
        prev_val = float(prev_yield)
        if prev_val > 0.5:
            drop_pct = ((prev_val - predicted_yield) / prev_val) * 100.0
            if drop_pct > 25.0:
                alerts.append(AlertItem(
                    alert_id=f"ALT-{uuid.uuid4().hex[:8].upper()}",
                    field_id=field_id,
                    crop=crop,
                    region=region,
                    severity="High" if drop_pct > 40.0 else "Warning",
                    rule_name="Severe Year-over-Year Yield Decline",
                    reason=f"Forecast yield reflects a {drop_pct:.1f}% reduction relative to previous season historical yield ({prev_val:.2f} t/ha).",
                    predicted_yield=round(predicted_yield, 2),
                    threshold_value=round(prev_val * 0.75, 2),
                    suggested_action="Analyze whether soil depletion, suboptimal weather, or pest incidence caused this divergence."
                ))

    # Rule 3: Cascading anomaly alerts (severe drought or heat)
    for anom in anomalies:
        anom_severity = getattr(anom, "severity", None) or (anom.get("severity") if isinstance(anom, dict) else None)
        anom_type = getattr(anom, "type", None) or (anom.get("type") if isinstance(anom, dict) else "")
        if anom_severity in ["Critical", "High"]:
            alerts.append(AlertItem(
                alert_id=f"ALT-{uuid.uuid4().hex[:8].upper()}",
                field_id=field_id,
                crop=crop,
                region=region,
                severity=anom_severity,
                rule_name=f"Agronomic Stress Anomaly: {anom_type}",
                reason=getattr(anom, "explanation", "") or (anom.get("explanation", "") if isinstance(anom, dict) else ""),
                predicted_yield=round(predicted_yield, 2),
                threshold_value=getattr(anom, "triggering_value", None) or (anom.get("triggering_value") if isinstance(anom, dict) else None),
                suggested_action=getattr(anom, "suggested_action", "") or (anom.get("suggested_action", "") if isinstance(anom, dict) else "")
            ))

    # Deduplicate and Persist into SQLite DB if db session provided
    if db is not None:
        persisted_alerts: List[AlertItem] = []
        for alt in alerts:
            # Check if an unresolved alert for the same field and rule already exists
            existing = (
                db.query(AlertRecord)
                .filter(
                    AlertRecord.field_id == alt.field_id,
                    AlertRecord.rule_name == alt.rule_name,
                    AlertRecord.status.in_(["active", "acknowledged"])
                )
                .first()
            )
            if existing:
                # Return the existing active alert without creating duplicate
                persisted_alerts.append(AlertItem(
                    alert_id=existing.alert_id,
                    field_id=existing.field_id,
                    crop=existing.crop,
                    region=existing.region,
                    severity=existing.severity,
                    rule_name=existing.rule_name,
                    reason=existing.reason,
                    predicted_yield=existing.predicted_yield,
                    threshold_value=existing.threshold_value,
                    suggested_action=existing.suggested_action,
                    status=existing.status,
                    created_at=existing.created_at
                ))
            else:
                db_record = AlertRecord(
                    alert_id=alt.alert_id,
                    prediction_id=prediction_id,
                    field_id=alt.field_id,
                    crop=alt.crop,
                    region=alt.region,
                    severity=alt.severity,
                    rule_name=alt.rule_name,
                    reason=alt.reason,
                    predicted_yield=alt.predicted_yield,
                    threshold_value=alt.threshold_value,
                    suggested_action=alt.suggested_action,
                    status="active",
                    created_at=datetime.utcnow()
                )
                db.add(db_record)
                db.commit()
                db.refresh(db_record)
                persisted_alerts.append(alt)
        return persisted_alerts

    return alerts
