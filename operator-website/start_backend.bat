@echo off
cd /d "%~dp0"
echo Starting Badak LNG C3MR Operator Decision-Support Backend (FastAPI)...
cd backend
python main.py
pause
