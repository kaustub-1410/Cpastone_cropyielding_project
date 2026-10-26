import os
import sys
from pathlib import Path

# Ensure paths are added for Vercel Serverless Function resolution
CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent if CURRENT_DIR.name == "api" else CURRENT_DIR
BACKEND_DIR = ROOT_DIR / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Set Vercel environment flag
os.environ["VERCEL"] = "1"

# Import ASGI FastAPI app
from app.main import app

# Export for Vercel Serverless
__all__ = ["app"]
