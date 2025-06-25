@echo off
echo Fixing Crystal Copilot Dependencies
echo ===================================
echo.

echo This will fix the OpenAI/httpx compatibility issue...
echo.

echo Step 1: Upgrading OpenAI library to compatible version...
pip install --upgrade openai==1.35.0

echo.
echo Step 2: Installing compatible httpx version...
pip install httpx==0.25.2

echo.
echo Step 3: Reinstalling all dependencies from requirements.txt...
pip install -r requirements.txt --upgrade

echo.
echo ========================================
echo DEPENDENCIES FIXED!
echo ========================================
echo.
echo You can now start the backend with:
echo .\start-backend.bat
echo.
pause 