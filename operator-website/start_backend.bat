@echo off
cd /d "%~dp0"
echo Starting C3MR Operator Decision-Support Backend (FastAPI)...
cd backend
python main.py
pause
