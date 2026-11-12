@echo off
cd /d "%~dp0"
echo =========================================================================
echo Baseload LNG Plant-3 Train H — C3MR Operator Decision-Support Suite
echo MODE: READ-ONLY (DCS write-back strictly disabled)
echo =========================================================================
echo.
echo Launching Backend Service on http://localhost:3001...
start "C3MR Backend (FastAPI)" cmd /k "cd /d ""%~dp0backend"" && python main.py"

timeout /t 3 /nobreak > nul

echo Launching Frontend Web Server on http://localhost:5173...
start "C3MR Frontend (Vite)" cmd /k "cd /d ""%~dp0frontend"" && call npm.cmd run dev"

echo.
echo Application started. Open your web browser at:
echo http://localhost:5173
echo.
pause
