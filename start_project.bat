@echo off
setlocal enabledelayedexpansion

echo ===============================================================================
echo   CROP YIELD PREDICTION SYSTEM USING AI/ML (CAPSTONE BT195)
echo   Project Members: Pawan Singh ^& Ishika Pandey
echo   Project Supervisor: Mr. Rishabh Srivastava
echo ===============================================================================
echo.

:: 1. Check Python
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.11+ from https://www.python.org/
    pause
    exit /b 1
)
python --version

:: 2. Check Node.js
where node >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH!
    echo Please install Node.js v18+ from https://nodejs.org/
    pause
    exit /b 1
)
node --version
echo.

:: 3. Check Backend Initialization
echo [*] Checking Backend ML Artifacts...
cd backend
if not exist "artifacts\active_model.joblib" (
    echo [*] Training initial models and generating sample dataset...
    python -m ml.train
) else (
    echo [OK] Active model artifacts verified.
)
cd ..

:: 4. Start Backend Server
echo [*] Launching FastAPI Backend on http://localhost:8000 ...
start "Crop Yield Backend (FastAPI)" cmd /k "cd backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

:: 5. Start Frontend Dev Server
echo [*] Launching React Dashboard on http://localhost:5173 ...
start "Crop Yield Frontend (React/Vite)" cmd /k "cd frontend && npm run dev"

:: 6. Wait and Open Browser
echo.
echo [*] Services are booting up...
timeout /t 4 /nobreak >nul
echo [*] Opening application dashboard in your default browser...
start http://localhost:5173

echo.
echo ===============================================================================
echo   SYSTEM IS OPERATIONAL
echo   - Frontend Dashboard:      http://localhost:5173
echo   - Backend Swagger API:     http://localhost:8000/docs
echo   - Alternative ReDoc API:   http://localhost:8000/redoc
echo ===============================================================================
echo Keep the opened terminal windows running while using the system.
echo.
