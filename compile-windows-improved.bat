@echo off
echo Crystal Copilot - Improved RptToXml Compilation
echo ===============================================

REM Check if we're in the right directory
if not exist "RptToXml.cs" (
    echo ERROR: RptToXml.cs not found in current directory
    echo Please run this script from the project root directory
    pause
    exit /b 1
)

echo Searching for Crystal Reports SDK...

REM Search for Crystal Reports DLLs in common locations
set CR_PATH=""
set CR_DLL_ENGINE=""
set CR_DLL_SHARED=""

REM Check 64-bit locations first
if exist "C:\Program Files (x86)\SAP BusinessObjects\Crystal Reports for .NET Framework 4.0\Common\SAP BusinessObjects Enterprise XI 4.0\win64_x64\CrystalDecisions.CrystalReports.Engine.dll" (
    set CR_PATH="C:\Program Files (x86)\SAP BusinessObjects\Crystal Reports for .NET Framework 4.0\Common\SAP BusinessObjects Enterprise XI 4.0\win64_x64"
    goto FOUND_CR
)

REM Check 32-bit locations
if exist "C:\Program Files (x86)\SAP BusinessObjects\Crystal Reports for .NET Framework 4.0\Common\SAP BusinessObjects Enterprise XI 4.0\win32_x86\CrystalDecisions.CrystalReports.Engine.dll" (
    set CR_PATH="C:\Program Files (x86)\SAP BusinessObjects\Crystal Reports for .NET Framework 4.0\Common\SAP BusinessObjects Enterprise XI 4.0\win32_x86"
    goto FOUND_CR
)

REM Check GAC (Global Assembly Cache)
for /f "delims=" %%i in ('dir "C:\Windows\Microsoft.NET\assembly" /s /b /a-d 2^>nul ^| findstr "CrystalDecisions.CrystalReports.Engine.dll" ^| head -1') do (
    set CR_DLL_ENGINE="%%i"
)

for /f "delims=" %%i in ('dir "C:\Windows\Microsoft.NET\assembly" /s /b /a-d 2^>nul ^| findstr "CrystalDecisions.Shared.dll" ^| head -1') do (
    set CR_DLL_SHARED="%%i"
)

if not %CR_DLL_ENGINE%=="" if not %CR_DLL_SHARED%=="" (
    echo Found Crystal Reports DLLs in GAC
    goto COMPILE_WITH_GAC
)

echo ERROR: Crystal Reports SDK not found
echo.
echo Please install Crystal Reports for Visual Studio:
echo 1. Download from: https://www.sap.com/products/technology-platform/crystal-reports.html
echo 2. Or search for "Crystal Reports for Visual Studio" on SAP website
echo 3. Install Crystal Reports Runtime 2019 or 2020
echo.
echo Common installation paths:
echo   C:\Program Files (x86)\SAP BusinessObjects\Crystal Reports for .NET Framework 4.0\...
echo.
pause
exit /b 1

:FOUND_CR
echo Found Crystal Reports SDK at: %CR_PATH%
set CR_DLL_ENGINE=%CR_PATH%\CrystalDecisions.CrystalReports.Engine.dll
set CR_DLL_SHARED=%CR_PATH%\CrystalDecisions.Shared.dll
set CR_DLL_REPORTSOURCE=%CR_PATH%\CrystalDecisions.ReportSource.dll

:COMPILE_WITH_GAC
echo.
echo Crystal Reports DLLs:
if not %CR_DLL_ENGINE%=="" echo   Engine: %CR_DLL_ENGINE%
if not %CR_DLL_SHARED%=="" echo   Shared: %CR_DLL_SHARED%

REM Try .NET Framework compilation first
echo.
echo Attempting .NET Framework compilation...

REM Create proper .NET Framework project file
echo Creating .NET Framework project...
(
echo ^<Project Sdk="Microsoft.NET.Sdk"^>
echo   ^<PropertyGroup^>
echo     ^<OutputType^>Exe^</OutputType^>
echo     ^<TargetFramework^>net48^</TargetFramework^>
echo     ^<UseWindowsForms^>true^</UseWindowsForms^>
echo     ^<GenerateAssemblyInfo^>false^</GenerateAssemblyInfo^>
echo   ^</PropertyGroup^>
echo   ^<ItemGroup^>
if not %CR_PATH%=="" (
echo     ^<Reference Include="CrystalDecisions.CrystalReports.Engine"^>
echo       ^<HintPath^>%CR_PATH%\CrystalDecisions.CrystalReports.Engine.dll^</HintPath^>
echo       ^<Private^>false^</Private^>
echo     ^</Reference^>
echo     ^<Reference Include="CrystalDecisions.Shared"^>
echo       ^<HintPath^>%CR_PATH%\CrystalDecisions.Shared.dll^</HintPath^>
echo       ^<Private^>false^</Private^>
echo     ^</Reference^>
echo     ^<Reference Include="CrystalDecisions.ReportSource"^>
echo       ^<HintPath^>%CR_PATH%\CrystalDecisions.ReportSource.dll^</HintPath^>
echo       ^<Private^>false^</Private^>
echo     ^</Reference^>
) else (
echo     ^<Reference Include="CrystalDecisions.CrystalReports.Engine" /^>
echo     ^<Reference Include="CrystalDecisions.Shared" /^>
echo     ^<Reference Include="CrystalDecisions.ReportSource" /^>
)
echo   ^</ItemGroup^>
echo ^</Project^>
) > RptToXml.csproj

echo Compiling with .NET Framework target...
dotnet build RptToXml.csproj -c Release -o . -f net48

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo SUCCESS: RptToXml.exe compiled successfully!
    echo ========================================
    goto TEST_EXE
)

echo .NET Framework compilation failed, trying legacy CSC...

REM Try direct CSC compilation
set CSC_PATH=""
for /f "delims=" %%i in ('where csc 2^>nul') do set CSC_PATH="%%i"

if %CSC_PATH%=="" (
    REM Try Visual Studio locations
    if exist "C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\Roslyn\csc.exe" (
        set CSC_PATH="C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\Roslyn\csc.exe"
    )
    if exist "C:\Program Files\Microsoft Visual Studio\2022\Professional\MSBuild\Current\Bin\Roslyn\csc.exe" (
        set CSC_PATH="C:\Program Files\Microsoft Visual Studio\2022\Professional\MSBuild\Current\Bin\Roslyn\csc.exe"
    )
    if exist "C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional\MSBuild\Current\Bin\Roslyn\csc.exe" (
        set CSC_PATH="C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional\MSBuild\Current\Bin\Roslyn\csc.exe"
    )
)

if %CSC_PATH%=="" (
    echo ERROR: No C# compiler found
    echo Please install Visual Studio Build Tools or .NET Framework Developer Pack
    del RptToXml.csproj 2>nul
    pause
    exit /b 1
)

echo Found C# compiler: %CSC_PATH%
echo Compiling with CSC...

%CSC_PATH% /target:exe /out:RptToXml.exe /platform:x86 ^
    /reference:%CR_DLL_ENGINE% ^
    /reference:%CR_DLL_SHARED% ^
    RptToXml.cs

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: CSC compilation failed
    del RptToXml.csproj 2>nul
    pause
    exit /b 1
)

:TEST_EXE
echo.
if exist "RptToXml.exe" (
    echo Testing the compiled tool...
    RptToXml.exe
    echo.
    echo ========================================
    echo COMPILATION SUCCESSFUL!
    echo ========================================
    echo.
    echo File location: %CD%\RptToXml.exe
    echo.
    echo Usage examples:
    echo   RptToXml.exe "report.rpt" "output.xml"
    echo   RptToXml.exe "report.rpt" "output.xml" --verbose
    echo.
) else (
    echo ERROR: RptToXml.exe was not created
)

REM Clean up
del RptToXml.csproj 2>nul

echo.
pause 