"""
Model loader utility for runtime inference.
Caches active model and preprocessor in memory for sub-millisecond API response times.
"""

from typing import Tuple, Optional, Dict, Any
import json
from pathlib import Path
import joblib

from app.config import settings
from app.services.preprocessing import AgriculturalPreprocessor

_CACHED_MODEL: Optional[Any] = None
_CACHED_PREPROCESSOR: Optional[AgriculturalPreprocessor] = None
_CACHED_METADATA: Optional[Dict[str, Any]] = None

def get_model_and_preprocessor() -> Tuple[Any, AgriculturalPreprocessor, Dict[str, Any]]:
    """Retrieves cached model, preprocessor, and metadata, loading from disk on first call."""
    global _CACHED_MODEL, _CACHED_PREPROCESSOR, _CACHED_METADATA

    if _CACHED_MODEL is not None and _CACHED_PREPROCESSOR is not None and _CACHED_METADATA is not None:
        return _CACHED_MODEL, _CACHED_PREPROCESSOR, _CACHED_METADATA

    active_model_path = settings.ARTIFACTS_DIR / "active_model.joblib"
    prep_path = settings.ARTIFACTS_DIR / "fitted_preprocessor.joblib"
    meta_path = settings.ARTIFACTS_DIR / "training_summary.json"

    if not active_model_path.exists() or not prep_path.exists() or not meta_path.exists():
        # Trigger training if artifacts don't exist yet
        from ml.train import train_and_benchmark_models
        train_and_benchmark_models()

    _CACHED_MODEL = joblib.load(active_model_path)
    _CACHED_PREPROCESSOR = AgriculturalPreprocessor.load(prep_path)
    with open(meta_path, "r") as f:
        _CACHED_METADATA = json.load(f)

    return _CACHED_MODEL, _CACHED_PREPROCESSOR, _CACHED_METADATA

def reload_model():
    """Forces cache refresh after retraining."""
    global _CACHED_MODEL, _CACHED_PREPROCESSOR, _CACHED_METADATA
    _CACHED_MODEL = None
    _CACHED_PREPROCESSOR = None
    _CACHED_METADATA = None
    return get_model_and_preprocessor()

def is_model_ready() -> bool:
    """Checks if trained model and preprocessing artifacts exist."""
    active_model_path = settings.ARTIFACTS_DIR / "active_model.joblib"
    prep_path = settings.ARTIFACTS_DIR / "fitted_preprocessor.joblib"
    return active_model_path.exists() and prep_path.exists()
