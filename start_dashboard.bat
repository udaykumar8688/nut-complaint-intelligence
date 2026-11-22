@echo off
cd /d "%~dp0"

if exist ".\.venv\Scripts\python.exe" (
  set "NUT_PYTHON=.\.venv\Scripts\python.exe"
) else (
  set "NUT_PYTHON=python"
)

start "NUT Complaint Intelligence server" /B "%NUT_PYTHON%" app.py
timeout /t 1 /nobreak > nul
start "" http://127.0.0.1:8000
echo NUT Complaint Intelligence is running at http://127.0.0.1:8000
echo Close this window to stop the dashboard.
pause
