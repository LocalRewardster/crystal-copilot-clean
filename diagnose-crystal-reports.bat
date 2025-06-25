@echo off
echo Crystal Reports Installation Diagnostic
echo =======================================

echo.
echo 1. Searching for Crystal Reports DLLs on entire system...
echo    (This may take a moment)

for /f "delims=" %%i in ('dir C:\ /s /b /a-d 2^>nul ^| findstr "CrystalDecisions.CrystalReports.Engine.dll"') do (
    echo    FOUND: %%i
)

echo.
echo 2. Checking common installation paths...

set LOCATIONS[0]="C:\Program Files (x86)\SAP BusinessObjects\Crystal Reports for .NET Framework 4.0\Common\SAP BusinessObjects Enterprise XI 4.0\win64_x64"
set LOCATIONS[1]="C:\Program Files (x86)\SAP BusinessObjects\Crystal Reports for .NET Framework 4.0\Common\SAP BusinessObjects Enterprise XI 4.0\win32_x86"
set LOCATIONS[2]="C:\Program Files\SAP BusinessObjects\Crystal Reports for .NET Framework 4.0\Common\SAP BusinessObjects Enterprise XI 4.0\win64_x64"
set LOCATIONS[3]="C:\Program Files\SAP BusinessObjects\Crystal Reports for .NET Framework 4.0\Common\SAP BusinessObjects Enterprise XI 4.0\win32_x86"

for /L %%i in (0,1,3) do (
    call :CHECK_PATH %%i
)

echo.
echo 3. Checking Global Assembly Cache (GAC)...
for /f "delims=" %%i in ('dir "C:\Windows\Microsoft.Net\assembly" /s /b /a-d 2^>nul ^| findstr "CrystalDecisions"') do (
    echo    GAC: %%i
)

echo.
echo 4. Checking .NET Framework versions...
dir "C:\Program Files (x86)\Reference Assemblies\Microsoft\Framework\.NETFramework" 2>nul
dir "C:\Program Files\Reference Assemblies\Microsoft\Framework\.NETFramework" 2>nul

echo.
echo 5. Checking Visual Studio Crystal Reports...
for /f "delims=" %%i in ('dir "C:\Program Files*" /s /b /a-d 2^>nul ^| findstr "Crystal"') do (
    echo    VS: %%i
)

echo.
echo 6. Checking if RptToXml.cs has proper Main method...
if exist "RptToXml.cs" (
    findstr /n "static.*Main" RptToXml.cs
    if %ERRORLEVEL% EQU 0 (
        echo    SUCCESS: Main method found in RptToXml.cs
    ) else (
        echo    ERROR: No Main method found in RptToXml.cs
    )
) else (
    echo    ERROR: RptToXml.cs not found
)

echo.
echo 7. Checking .NET SDK version...
dotnet --version

echo.
echo =======================================
echo DIAGNOSIS COMPLETE
echo =======================================
echo.
echo If Crystal Reports DLLs were found above, note their exact paths.
echo If no DLLs were found, you need to install Crystal Reports Runtime.
echo.
pause
goto :EOF

:CHECK_PATH
setlocal enabledelayedexpansion
set idx=%~1
set path=!LOCATIONS[%idx%]!
if exist %path% (
    echo    FOUND PATH: %path%
    if exist %path%\CrystalDecisions.CrystalReports.Engine.dll (
        echo      - CrystalDecisions.CrystalReports.Engine.dll: YES
    ) else (
        echo      - CrystalDecisions.CrystalReports.Engine.dll: NO
    )
    if exist %path%\CrystalDecisions.Shared.dll (
        echo      - CrystalDecisions.Shared.dll: YES
    ) else (
        echo      - CrystalDecisions.Shared.dll: NO
    )
) else (
    echo    PATH NOT FOUND: %path%
)
endlocal
goto :EOF 