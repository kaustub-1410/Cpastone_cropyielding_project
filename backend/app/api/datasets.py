"""
Dataset ingestion and management API endpoints.
Supports CSV validation, summary calculation, and synthetic sample generation.
"""

from typing import List, Optional
import io
import json
import uuid
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
import pandas as pd
import numpy as np

from app.config import settings
from app.database import get_db
from app.models.db_models import DatasetRecord
from app.schemas import GenerateSampleDataRequest, DatasetSummaryResponse
from app.services.preprocessing import AgriculturalPreprocessor
from ml.generate_sample_data import generate_agricultural_dataset

router = APIRouter(prefix="/datasets", tags=["Datasets"])

@router.post("/upload")
async def upload_csv_dataset(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Uploads, validates schema, and registers an agricultural CSV dataset."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files (.csv) are accepted.")

    contents = await file.read()
    if len(contents) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File exceeds maximum size limit of {settings.MAX_UPLOAD_SIZE_MB}MB.")

    try:
        df = pd.read_csv(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV file: {str(e)}")

    if len(df) < 10:
        raise HTTPException(status_code=400, detail="Dataset must contain at least 10 observations.")

    # Save to raw storage
    file_id = str(uuid.uuid4())[:8]
    clean_name = f"{file_id}_{file.filename}"
    save_path = settings.RAW_DATA_DIR / clean_name
    save_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(save_path, index=False)

    # Validate against expected schema
    preprocessor = AgriculturalPreprocessor()
    cleaned_df, warnings = preprocessor.validate_and_clean_dataframe(df, drop_duplicates=True)
    
    # Check target
    target_present = "actual_yield_t_ha" in df.columns
    eligible_for_training = target_present and (len(df) >= 30)

    # Missing values count
    missing_dict = {col: int(df[col].isna().sum()) for col in df.columns}
    
    # Summary stats for numeric columns
    num_cols = df.select_dtypes(include=[np.number]).columns
    stats = {}
    for col in num_cols:
        series = df[col].dropna()
        if len(series) > 0:
            stats[col] = {
                "mean": round(float(series.mean()), 2),
                "std": round(float(series.std()), 2),
                "min": round(float(series.min()), 2),
                "max": round(float(series.max()), 2),
            }

    # DB record
    ds_record = DatasetRecord(
        dataset_id=file_id,
        filename=file.filename,
        filepath=str(save_path),
        row_count=len(df),
        column_count=len(df.columns),
        columns_json=json.dumps(list(df.columns)),
        missing_values_json=json.dumps(missing_dict),
        summary_stats_json=json.dumps(stats),
        is_synthetic=False,
        provenance=f"User Upload: {file.filename}",
        is_training_eligible=eligible_for_training,
        created_at=datetime.utcnow()
    )
    db.add(ds_record)
    db.commit()
    db.refresh(ds_record)

    return {
        "status": "success",
        "dataset_id": file_id,
        "filename": file.filename,
        "row_count": len(df),
        "column_count": len(df.columns),
        "columns": list(df.columns),
        "target_present": target_present,
        "is_training_eligible": eligible_for_training,
        "warnings": warnings,
        "missing_values": missing_dict,
    }


@router.get("")
def list_datasets(db: Session = Depends(get_db)):
    """Lists registered agricultural datasets."""
    records = db.query(DatasetRecord).order_by(desc(DatasetRecord.created_at)).all()
    return [
        {
            "dataset_id": r.dataset_id,
            "filename": r.filename,
            "row_count": r.row_count,
            "column_count": r.column_count,
            "is_synthetic": r.is_synthetic,
            "provenance": r.provenance,
            "is_training_eligible": r.is_training_eligible,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in records
    ]


@router.get("/summary")
def get_active_dataset_summary(db: Session = Depends(get_db)):
    """Returns summary of the active or most recent training dataset."""
    ds = db.query(DatasetRecord).order_by(desc(DatasetRecord.created_at)).first()
    if not ds:
        # Fallback to sample dataset
        sample_path = settings.SAMPLE_DATA_DIR / "crop_yield_sample_dataset.csv"
        if not sample_path.exists():
            from ml.generate_sample_data import save_sample_dataset
            save_sample_dataset()
        df = pd.read_csv(sample_path)
        missing_dict = {col: int(df[col].isna().sum()) for col in df.columns}
        return {
            "dataset_id": "sample-default",
            "filename": sample_path.name,
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": list(df.columns),
            "missing_values": missing_dict,
            "summary_stats": {},
            "is_synthetic": True,
            "provenance": "Synthetic Agronomic Simulation - Capstone BT195",
            "is_training_eligible": True,
            "created_at": datetime.utcnow().isoformat()
        }

    return {
        "dataset_id": ds.dataset_id,
        "filename": ds.filename,
        "row_count": ds.row_count,
        "column_count": ds.column_count,
        "columns": json.loads(ds.columns_json or "[]"),
        "missing_values": json.loads(ds.missing_values_json or "{}"),
        "summary_stats": json.loads(ds.summary_stats_json or "{}"),
        "is_synthetic": ds.is_synthetic,
        "provenance": ds.provenance,
        "is_training_eligible": ds.is_training_eligible,
        "created_at": ds.created_at.isoformat() if ds.created_at else None
    }


@router.get("/{dataset_id}/preview")
def get_dataset_preview(dataset_id: str, limit: int = Query(25, ge=5, le=100), db: Session = Depends(get_db)):
    """Previews top rows of a specific registered dataset."""
    ds = db.query(DatasetRecord).filter(DatasetRecord.dataset_id == dataset_id).first()
    if not ds or not Path(ds.filepath).exists():
        sample_path = settings.SAMPLE_DATA_DIR / "crop_yield_sample_dataset.csv"
        if sample_path.exists():
            df = pd.read_csv(sample_path)
        else:
            raise HTTPException(status_code=404, detail=f"Dataset '{dataset_id}' not found.")
    else:
        df = pd.read_csv(ds.filepath)

    preview_df = df.head(limit)
    return {
        "dataset_id": dataset_id,
        "total_rows": len(df),
        "returned_rows": len(preview_df),
        "columns": list(df.columns),
        "records": preview_df.to_dict(orient="records")
    }


@router.post("/generate-sample")
def generate_sample_dataset_endpoint(req: GenerateSampleDataRequest, db: Session = Depends(get_db)):
    """Generates a fresh synthetic dataset with agronomic equations."""
    sample_id = str(uuid.uuid4())[:8]
    file_path = settings.SAMPLE_DATA_DIR / f"synthetic_agri_{sample_id}.csv"
    
    df = generate_agricultural_dataset(num_records=req.num_samples)
    df.to_csv(file_path, index=False)

    missing_dict = {col: 0 for col in df.columns}
    num_cols = df.select_dtypes(include=[np.number]).columns
    stats = {}
    for col in num_cols:
        stats[col] = {
            "mean": round(float(df[col].mean()), 2),
            "std": round(float(df[col].std()), 2),
            "min": round(float(df[col].min()), 2),
            "max": round(float(df[col].max()), 2),
        }

    rec = DatasetRecord(
        dataset_id=sample_id,
        filename=file_path.name,
        filepath=str(file_path),
        row_count=len(df),
        column_count=len(df.columns),
        columns_json=json.dumps(list(df.columns)),
        missing_values_json=json.dumps(missing_dict),
        summary_stats_json=json.dumps(stats),
        is_synthetic=True,
        provenance="Synthetic Agronomic Simulation - Capstone BT195",
        is_training_eligible=True,
        created_at=datetime.utcnow()
    )
    db.add(rec)
    db.commit()

    return {
        "status": "success",
        "dataset_id": sample_id,
        "filename": file_path.name,
        "row_count": len(df),
        "is_synthetic": True,
        "provenance": "Synthetic Agronomic Simulation - Capstone BT195",
        "message": f"Successfully generated {len(df)} synthetic agricultural records."
    }
