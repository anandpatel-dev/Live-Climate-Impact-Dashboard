@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" update_all.py
) else (
    python update_all.py
)
if errorlevel 1 (
    echo.
    echo Data refresh failed. Read the error above.
) else (
    echo.
    echo Data refresh completed successfully.
)
pause
