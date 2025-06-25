@echo off
echo Starting Crystal Copilot Backend...
echo ==================================
echo.

if exist "RptToXml.exe" (
    echo Real Crystal Reports parser detected: RptToXml.exe
) else (
    echo Using mock data (RptToXml.exe not found)
)

echo.
echo Backend will be available at: http://localhost:8000
echo API docs available at: http://localhost:8000/docs
echo.

python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 