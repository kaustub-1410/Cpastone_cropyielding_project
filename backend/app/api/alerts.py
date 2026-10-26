"""
Alerts & Anomalies management API endpoints.
Provides filtering, status tracking, acknowledgment, and resolution workflows.
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models.db_models import AlertRecord
from app.schemas import AlertResponse, AlertUpdateRequest

router = APIRouter(prefix="/alerts", tags=["Alerts & Anomalies"])

@router.get("", response_model=List[AlertResponse])
def get_alerts(
    severity: Optional[str] = Query(None, description="Filter by severity: Info, Warning, High, Critical"),
    status: Optional[str] = Query(None, description="Filter by status: active, acknowledged, resolved"),
    crop: Optional[str] = None,
    region: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Retrieves alerts with multi-dimensional filtering."""
    query = db.query(AlertRecord)

    if severity and severity != "all":
        query = query.filter(AlertRecord.severity == severity)
    if status and status != "all":
        query = query.filter(AlertRecord.status == status)
    if crop and crop != "all":
        query = query.filter(AlertRecord.crop == crop)
    if region and region != "all":
        query = query.filter(AlertRecord.region == region)

    records = query.order_by(desc(AlertRecord.created_at)).limit(limit).all()

    return [
        AlertResponse(
            alert_id=r.alert_id,
            field_id=r.field_id,
            crop=r.crop,
            region=r.region,
            severity=r.severity,
            rule_name=r.rule_name,
            reason=r.reason,
            predicted_yield=r.predicted_yield,
            threshold_value=r.threshold_value,
            suggested_action=r.suggested_action,
            status=r.status,
            created_at=r.created_at,
            acknowledged_at=r.acknowledged_at,
            resolved_at=r.resolved_at
        )
        for r in records
    ]


@router.patch("/{alert_id}", response_model=AlertResponse)
def update_alert_status(alert_id: str, req: AlertUpdateRequest, db: Session = Depends(get_db)):
    """Acknowledge or resolve an active alert with audit timestamp."""
    rec = db.query(AlertRecord).filter(AlertRecord.alert_id == alert_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail=f"Alert '{alert_id}' not found.")

    now = datetime.utcnow()
    rec.status = req.status
    if req.status == "acknowledged":
        rec.acknowledged_at = now
    elif req.status == "resolved":
        rec.resolved_at = now
        if not rec.acknowledged_at:
            rec.acknowledged_at = now

    db.commit()
    db.refresh(rec)

    return AlertResponse(
        alert_id=rec.alert_id,
        field_id=rec.field_id,
        crop=rec.crop,
        region=rec.region,
        severity=rec.severity,
        rule_name=rec.rule_name,
        reason=rec.reason,
        predicted_yield=rec.predicted_yield,
        threshold_value=rec.threshold_value,
        suggested_action=rec.suggested_action,
        status=rec.status,
        created_at=rec.created_at,
        acknowledged_at=rec.acknowledged_at,
        resolved_at=rec.resolved_at
    )
