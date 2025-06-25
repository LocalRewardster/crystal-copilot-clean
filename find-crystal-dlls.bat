@echo off
echo Crystal Reports DLL Finder
echo ==========================
echo.

set "CR_BASE=C:\Program Files (x86)\SAP BusinessObjects\Crystal Reports for .NET Framework 4.0"

if not exist "%CR_BASE%" (
    echo ERROR: Crystal Reports directory not found at:
    echo "%CR_BASE%"
    echo.
    echo Please verify the installation path.
    pause
    exit /b 1
)

echo Searching for Crystal Reports DLLs in:
echo "%CR_BASE%"
echo.

echo === ALL CRYSTAL REPORTS DLLs ===
dir "%CR_BASE%" /s /b /a-d | findstr /i "crystal"

echo.
echo === SPECIFIC DLLs WE NEED ===
echo.

echo Looking for CrystalDecisions.CrystalReports.Engine.dll:
for /f "delims=" %%i in ('dir "%CR_BASE%" /s /b /a-d 2^>nul ^| findstr /i "CrystalDecisions.CrystalReports.Engine"') do (
    echo FOUND: %%i
)

echo.
echo Looking for CrystalDecisions.Shared.dll:
for /f "delims=" %%i in ('dir "%CR_BASE%" /s /b /a-d 2^>nul ^| findstr /i "CrystalDecisions.Shared"') do (
    echo FOUND: %%i
)

echo.
echo Looking for CrystalDecisions.ReportSource.dll:
for /f "delims=" %%i in ('dir "%CR_BASE%" /s /b /a-d 2^>nul ^| findstr /i "CrystalDecisions.ReportSource"') do (
    echo FOUND: %%i
)

echo.
echo === DIRECTORY STRUCTURE ===
echo.
echo Main directories under Crystal Reports:
dir "%CR_BASE%" /ad /b

echo.
echo === ALTERNATIVE SEARCH LOCATIONS ===
echo.

REM Check GAC (Global Assembly Cache)
echo Checking GAC for Crystal Reports assemblies:
if exist "C:\Windows\Microsoft.NET\assembly" (
    dir "C:\Windows\Microsoft.NET\assembly" /s /b /a-d | findstr /i "CrystalDecisions" | findstr /i "Engine"
)

echo.
echo Checking Program Files for other Crystal Reports installations:
if exist "C:\Program Files\SAP BusinessObjects" (
    echo Found: C:\Program Files\SAP BusinessObjects
    dir "C:\Program Files\SAP BusinessObjects" /s /b /a-d | findstr /i "CrystalDecisions.CrystalReports.Engine"
)

if exist "C:\Program Files (x86)\Business Objects" (
    echo Found: C:\Program Files (x86)\Business Objects  
    dir "C:\Program Files (x86)\Business Objects" /s /b /a-d | findstr /i "CrystalDecisions.CrystalReports.Engine"
)

echo.
echo === REGISTRY CHECK ===
echo.
echo Checking registry for Crystal Reports installations:
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\SAP BusinessObjects" /s 2>nul | findstr /i "Crystal"
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\SAP BusinessObjects" /s 2>nul | findstr /i "Crystal"

echo.
echo === SUMMARY ===
echo If DLLs were found above, use those paths in the compilation.
echo If no DLLs found, Crystal Reports SDK might not be fully installed.
echo.
pause 