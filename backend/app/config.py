import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings

# Base directories
BACKEND_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = BACKEND_DIR.parent

IS_VERCEL = bool(os.environ.get("VERCEL"))

class Settings(BaseSettings):
    APP_NAME: str = "Crop Yield Prediction System Using AI/ML"
    PROJECT_ID: str = "BT195"
    PROJECT_MEMBERS: str = "Pawan Singh & Ishika Pandey"
    PROJECT_SUPERVISOR: str = "Mr. Rishabh Srivastava"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    ENVIRONMENT: str = "production" if IS_VERCEL else "development"

    # Paths
    BACKEND_PATH: Path = BACKEND_DIR
    DATA_DIR: Path = Path("/tmp/data") if IS_VERCEL else (BACKEND_DIR / "data")
    SAMPLE_DATA_DIR: Path = BACKEND_DIR / "data" / "sample"
    PROCESSED_DATA_DIR: Path = Path("/tmp/data/processed") if IS_VERCEL else (BACKEND_DIR / "data" / "processed")
    RAW_DATA_DIR: Path = Path("/tmp/data/raw") if IS_VERCEL else (BACKEND_DIR / "data" / "raw")
    ARTIFACTS_DIR: Path = BACKEND_DIR / "artifacts"

    # Database
    DATABASE_URL: str = "sqlite:////tmp/crop_yield.db" if IS_VERCEL else f"sqlite:///{BACKEND_DIR / 'data' / 'crop_yield.db'}"

    # Security & Uploads
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://localhost:4173",
        "*",
    ]
    MAX_UPLOAD_SIZE_MB: int = 25
    CONFIDENCE_LEVEL: float = 0.90  # 90% calibrated prediction interval

    class Config:
        env_file = str(BACKEND_DIR / ".env")
        extra = "allow"

settings = Settings()

# Ensure directories exist safely without raising Read-Only filesystem errors in cloud environments
for dir_path in [settings.DATA_DIR, settings.PROCESSED_DATA_DIR, settings.RAW_DATA_DIR]:
    try:
        dir_path.mkdir(parents=True, exist_ok=True)
    except OSError:
        pass

