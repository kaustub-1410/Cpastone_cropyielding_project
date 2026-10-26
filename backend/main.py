"""
Entrypoint for Vercel Serverless / Service deployment.
Exports the FastAPI app instance from app.main.
"""

from app.main import app

__all__ = ["app"]
