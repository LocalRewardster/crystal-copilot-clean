@echo off
echo Crystal Copilot Windows Setup
echo =============================
echo.

echo Step 1: Installing Python dependencies...
echo ==========================================
pip install -r requirements.txt

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to install dependencies
    echo Please ensure Python and pip are installed
    pause
    exit /b 1
)

echo.
echo Step 2: Setting up environment...
echo =================================

if not exist ".env" (
    echo Creating .env file...
    (
    echo OPENAI_API_KEY=your_openai_api_key_here
    echo ENVIRONMENT=development
    echo DEBUG=True
    ) > .env
    
    echo.
    echo IMPORTANT: Please edit .env file and add your OpenAI API key
    echo.
)

echo.
echo Step 3: Copy RptToXml.exe to project root...
echo ============================================

if exist "RptToXml.exe" (
    echo RptToXml.exe found - ready for real Crystal Reports parsing!
) else (
    echo WARNING: RptToXml.exe not found
    echo The application will use mock data until you copy RptToXml.exe here
    echo.
)

echo.
echo ========================================
echo SETUP COMPLETE!
echo ========================================
echo.
echo To start Crystal Copilot:
echo.
echo 1. Backend:  start-backend.bat
echo 2. Frontend: start-frontend.bat
echo.
echo Or run manually:
echo 1. Backend:  python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
echo 2. Frontend: streamlit run frontend/app.py
echo.
pause 