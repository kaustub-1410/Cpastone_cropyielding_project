"""
FastAPI Main Application Entry Point for Crop Yield Prediction System (BT195).
Precision Agriculture & AI/ML Capstone Project.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import init_db
from app.api import health, predictions, datasets, models, alerts, analytics
from app.models.model_loader import is_model_ready, get_model_and_preprocessor

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Database and check model readiness
    init_db()
    if not is_model_ready():
        print("[*] Initializing baseline models and synthetic demonstration dataset...")
        try:
            from ml.train import train_and_benchmark_models
            train_and_benchmark_models()
        except Exception as e:
            print(f"[!] Startup initialization error: {e}")
    else:
        # Pre-cache model into memory
        try:
            get_model_and_preprocessor()
            print("[OK] Active model pre-cached into memory.")
        except Exception as e:
            print(f"[!] Error pre-caching model: {e}")
            
    yield
    # Shutdown
    print("[*] Backend service shutting down gracefully.")


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        f"**Project ID: {settings.PROJECT_ID}** | "
        f"Team: {settings.PROJECT_MEMBERS} | Supervisor: {settings.PROJECT_SUPERVISOR}\n\n"
        "End-to-End Precision Agriculture Platform for Pre-Harvest Crop Yield Forecasting "
        "leveraging Meteorological observations, Soil physicochemical indices, "
        "Satellite remote sensing (NDVI), and Calibrated Machine Learning."
    ),
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permits local development ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal Server Error: {str(exc)}"}
    )

# Include Routers
app.include_router(health.router, prefix=settings.API_V1_STR)
app.include_router(predictions.router, prefix=settings.API_V1_STR)
app.include_router(datasets.router, prefix=settings.API_V1_STR)
app.include_router(models.router, prefix=settings.API_V1_STR)
app.include_router(alerts.router, prefix=settings.API_V1_STR)
app.include_router(analytics.router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "system": settings.APP_NAME,
        "project_id": settings.PROJECT_ID,
        "team": settings.PROJECT_MEMBERS,
        "supervisor": settings.PROJECT_SUPERVISOR,
        "docs_url": "/docs",
        "api_v1": settings.API_V1_STR,
        "status": "operational"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
