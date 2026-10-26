"""
Model registry, evaluation reports, and training execution API endpoints.
"""

from typing import List, Optional
import json
import threading
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.config import settings
from app.database import get_db, SessionLocal
from app.models.db_models import ModelRecord, DatasetRecord
from app.schemas import TrainModelRequest, ModelComparisonReport, ModelEvaluationSummary, ModelMetrics
from app.models.model_loader import reload_model
from ml.train import train_and_benchmark_models
from ml.evaluate import run_evaluation

router = APIRouter(prefix="/models", tags=["Models & Training"])

_TRAINING_IN_PROGRESS = False

def _background_train_task(dataset_path: Optional[Path], preferred_algo: Optional[str]):
    global _TRAINING_IN_PROGRESS
    try:
        train_and_benchmark_models(dataset_path=dataset_path, preferred_algo=preferred_algo)
        run_evaluation()
        reload_model()
    finally:
        _TRAINING_IN_PROGRESS = False


@router.get("", response_model=ModelComparisonReport)
def list_models(db: Session = Depends(get_db)):
    """Returns registered candidate models, benchmarks, and validation/test metrics."""
    models = db.query(ModelRecord).order_by(ModelRecord.val_rmse.asc()).all()
    
    summaries: List[ModelEvaluationSummary] = []
    selected_id = None
    
    for m in models:
        if m.is_active:
            selected_id = m.model_id
        summaries.append(ModelEvaluationSummary(
            model_id=m.model_id,
            name=m.name,
            algorithm=m.algorithm,
            version=m.version,
            is_active=m.is_active,
            is_synthetic_trained=m.is_synthetic_trained,
            validation_metrics=ModelMetrics(
                rmse=m.val_rmse,
                mae=m.val_mae,
                r2=m.val_r2,
                mape=m.val_mape
            ),
            test_metrics=ModelMetrics(
                rmse=m.test_rmse,
                mae=m.test_mae,
                r2=m.test_r2,
                mape=m.test_mape,
                bias=m.test_bias,
                coverage_90=m.test_coverage_90
            ),
            train_size=m.train_size,
            val_size=m.val_size,
            test_size=m.test_size,
            created_at=m.created_at
        ))

    # Read summary file for split strategy
    summary_path = settings.ARTIFACTS_DIR / "training_summary.json"
    dataset_name = "crop_yield_sample_dataset.csv"
    if summary_path.exists():
        with open(summary_path, "r") as f:
            data = json.load(f)
            dataset_name = Path(data.get("dataset_path", "")).name

    return ModelComparisonReport(
        models=summaries,
        selected_model_id=selected_id,
        evaluation_dataset=dataset_name,
        split_strategy="Temporal / Regionally Stratified (70% Train, 15% Val, 15% Test)",
        target_unit="tonnes per hectare (t/ha)"
    )


@router.get("/evaluation")
def get_evaluation_metrics():
    """Returns actual evaluation charts data: scatter points, residuals, per-crop breakdown."""
    report_path = settings.ARTIFACTS_DIR / "evaluation_report.json"
    if not report_path.exists():
        # Generate on demand
        return run_evaluation()

    with open(report_path, "r") as f:
        return json.load(f)


@router.post("/train")
def train_model_endpoint(req: TrainModelRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Triggers model training run in background with non-blocking execution."""
    global _TRAINING_IN_PROGRESS
    if _TRAINING_IN_PROGRESS:
        raise HTTPException(status_code=409, detail="A training job is already in progress. Please wait.")

    dataset_path = None
    if req.dataset_id:
        ds = db.query(DatasetRecord).filter(DatasetRecord.dataset_id == req.dataset_id).first()
        if ds and Path(ds.filepath).exists():
            dataset_path = Path(ds.filepath)
        else:
            raise HTTPException(status_code=404, detail=f"Dataset with ID '{req.dataset_id}' not found.")

    _TRAINING_IN_PROGRESS = True
    background_tasks.add_task(_background_train_task, dataset_path, req.selected_algorithm)

    return {
        "status": "started",
        "message": f"Training initiated in background for algorithm '{req.selected_algorithm}'. Check /api/models for status updates.",
        "dataset": str(dataset_path.name) if dataset_path else "Default dataset"
    }


@router.get("/status")
def get_training_status():
    """Checks if a background training run is active."""
    return {"training_in_progress": _TRAINING_IN_PROGRESS}
