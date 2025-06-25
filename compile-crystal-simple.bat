@echo off
echo Crystal Reports Simple Compiler
echo ================================
echo.

if not exist "RptToXml.cs" (
    echo ERROR: RptToXml.cs not found in current directory
    echo Current directory: %CD%
    echo.
    echo Please ensure you're in the project directory with RptToXml.cs
    pause
    exit /b 1
)

echo Step 1: Checking for .NET Framework and compilers...
echo =====================================================

REM Check .NET Framework installations
echo Checking .NET Framework installations:
if exist "C:\Windows\Microsoft.NET\Framework64" (
    echo Found: .NET Framework 64-bit
    dir "C:\Windows\Microsoft.NET\Framework64" /ad /b | findstr "v4"
)

if exist "C:\Windows\Microsoft.NET\Framework" (
    echo Found: .NET Framework 32-bit  
    dir "C:\Windows\Microsoft.NET\Framework" /ad /b | findstr "v4"
)

echo.
echo Checking for C# compilers:

set "CSC_PATH="
set "COMPILER_TYPE="

REM Method 1: Try .NET Framework 4.8 (most common)
if exist "C:\Program Files (x86)\Microsoft SDKs\Windows\v10.0A\bin\NETFX 4.8 Tools\csc.exe" (
    set "CSC_PATH=C:\Program Files (x86)\Microsoft SDKs\Windows\v10.0A\bin\NETFX 4.8 Tools\csc.exe"
    set "COMPILER_TYPE=Windows SDK .NET Framework 4.8"
    echo FOUND: %COMPILER_TYPE%
    goto :COMPILE
)

REM Method 2: Try .NET Framework 4.7.2
if exist "C:\Program Files (x86)\Microsoft SDKs\Windows\v10.0A\bin\NETFX 4.7.2 Tools\csc.exe" (
    set "CSC_PATH=C:\Program Files (x86)\Microsoft SDKs\Windows\v10.0A\bin\NETFX 4.7.2 Tools\csc.exe"
    set "COMPILER_TYPE=Windows SDK .NET Framework 4.7.2"
    echo FOUND: %COMPILER_TYPE%
    goto :COMPILE
)

REM Method 3: Try standard .NET Framework locations
if exist "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe" (
    set "CSC_PATH=C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
    set "COMPILER_TYPE=.NET Framework 4.0 (64-bit)"
    echo FOUND: %COMPILER_TYPE%
    goto :COMPILE
)

if exist "C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe" (
    set "CSC_PATH=C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe"
    set "COMPILER_TYPE=.NET Framework 4.0 (32-bit)"
    echo FOUND: %COMPILER_TYPE%
    goto :COMPILE
)

REM Method 4: Try Visual Studio 2022
if exist "C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\Roslyn\csc.exe" (
    set "CSC_PATH=C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\Roslyn\csc.exe"
    set "COMPILER_TYPE=Visual Studio 2022 Community"
    echo FOUND: %COMPILER_TYPE%
    goto :COMPILE
)

if exist "C:\Program Files\Microsoft Visual Studio\2022\Professional\MSBuild\Current\Bin\Roslyn\csc.exe" (
    set "CSC_PATH=C:\Program Files\Microsoft Visual Studio\2022\Professional\MSBuild\Current\Bin\Roslyn\csc.exe"
    set "COMPILER_TYPE=Visual Studio 2022 Professional"
    echo FOUND: %COMPILER_TYPE%
    goto :COMPILE
)

REM Method 5: Try system PATH
echo Checking system PATH for csc.exe...
where csc.exe >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    for /f "delims=" %%i in ('where csc.exe') do (
        set "CSC_PATH=%%i"
        set "COMPILER_TYPE=System PATH"
        echo FOUND: %COMPILER_TYPE% at %%i
        goto :COMPILE
    )
)

echo.
echo ERROR: No C# compiler found!
echo.
echo You need to install one of:
echo 1. .NET Framework Developer Pack 4.8 (recommended)
echo    Download: https://dotnet.microsoft.com/download/dotnet-framework/net48
echo 2. Visual Studio 2022 Community (free)
echo    Download: https://visualstudio.microsoft.com/downloads/
echo 3. Build Tools for Visual Studio 2022
echo    Download: https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022
echo.
pause
exit /b 1

:COMPILE
echo.
echo Step 2: Compiling Crystal Reports tool...
echo ========================================
echo Using: %COMPILER_TYPE%
echo Path: %CSC_PATH%
echo.

echo Attempting compilation with GAC references...
"%CSC_PATH%" /target:exe /out:RptToXml.exe /platform:anycpu ^
    /reference:System.dll ^
    /reference:System.Xml.dll ^
    /reference:CrystalDecisions.CrystalReports.Engine ^
    /reference:CrystalDecisions.Shared ^
    RptToXml.cs

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo SUCCESS: Crystal Reports compilation!
    echo ========================================
    
    if exist "RptToXml.exe" (
        echo.
        echo Testing the compiled executable...
        RptToXml.exe
        echo.
        echo File details:
        dir RptToXml.exe
        echo.
        echo SUCCESS: RptToXml.exe is ready to parse Crystal Reports!
        echo.
        echo Usage: RptToXml.exe "input.rpt" "output.xml"
    ) else (
        echo WARNING: Compilation reported success but RptToXml.exe not found
    )
) else (
    echo.
    echo ERROR: Compilation failed
    echo.
    echo This usually means:
    echo 1. Crystal Reports assemblies not found in GAC
    echo 2. Crystal Reports SDK not properly installed
    echo 3. Need Crystal Reports Developer Edition
    echo.
    echo Try installing Crystal Reports for Visual Studio:
    echo https://www.sap.com/products/technology-platform/crystal-reports.html
)

echo.
pause 