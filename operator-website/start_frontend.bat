@echo off
cd /d "%~dp0"
echo Starting Badak LNG C3MR Operator Decision-Support Frontend (Vite)...
cd frontend
call npm.cmd run dev
pause
