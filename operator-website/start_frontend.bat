@echo off
cd /d "%~dp0"
echo Starting C3MR Operator Decision-Support Frontend (Vite)...
cd frontend
call npm.cmd run dev
pause
