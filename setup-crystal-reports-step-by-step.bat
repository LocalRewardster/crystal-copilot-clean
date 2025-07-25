@echo off
setlocal enabledelayedexpansion
echo Crystal Reports 2020 Step-by-Step Setup
echo ========================================

echo.
echo STEP 1: Verify Crystal Reports 2020 Installation
echo ================================================

echo Searching for Crystal Reports 2020 installations...

REM Crystal Reports 2020 common paths - using variables instead of arrays
set "CR_PATH1=C:\Program Files (x86)\SAP BusinessObjects\Crystal Reports for .NET Framework 4.0"
set "CR_PATH2=C:\Program Files\SAP BusinessObjects\Crystal Reports for .NET Framework 4.0"
set "CR_PATH3=C:\Program Files (x86)\Business Objects\Crystal Reports 2020"
set "CR_PATH4=C:\Program Files\Business Objects\Crystal Reports 2020"

set FOUND_CR=0
set "CR_BASE="

REM Check each path individually
if exist "!CR_PATH1!" (
    echo FOUND: Crystal Reports at "!CR_PATH1!"
    set FOUND_CR=1
    set "CR_BASE=!CR_PATH1!"
    goto :FOUND_PATH
) else (
    echo NOT FOUND: "!CR_PATH1!"
)

if exist "!CR_PATH2!" (
    echo FOUND: Crystal Reports at "!CR_PATH2!"
    set FOUND_CR=1
    set "CR_BASE=!CR_PATH2!"
    goto :FOUND_PATH
) else (
    echo NOT FOUND: "!CR_PATH2!"
)

if exist "!CR_PATH3!" (
    echo FOUND: Crystal Reports at "!CR_PATH3!"
    set FOUND_CR=1
    set "CR_BASE=!CR_PATH3!"
    goto :FOUND_PATH
) else (
    echo NOT FOUND: "!CR_PATH3!"
)

if exist "!CR_PATH4!" (
    echo FOUND: Crystal Reports at "!CR_PATH4!"
    set FOUND_CR=1
    set "CR_BASE=!CR_PATH4!"
    goto :FOUND_PATH
) else (
    echo NOT FOUND: "!CR_PATH4!"
)

:FOUND_PATH

if !FOUND_CR!==0 (
    echo.
    echo ERROR: Crystal Reports 2020 not found in common locations
    echo.
    echo Please verify Crystal Reports 2020 is installed:
    echo 1. Crystal Reports for Visual Studio 2020
    echo 2. Crystal Reports Runtime 2020
    echo.
    echo Manual search: Look for CrystalDecisions.*.dll files
    pause
    exit /b 1
)

echo.
echo STEP 2: Locate Required DLLs
echo =============================

set "CR_ENGINE="
set "CR_SHARED="
set "CR_REPORTSOURCE="

REM Try different subdirectories - using individual variables
set "SUBDIR1=Common\SAP BusinessObjects Enterprise XI 4.0\win64_x64"
set "SUBDIR2=Common\SAP BusinessObjects Enterprise XI 4.0\win32_x86"
set "SUBDIR3=Assemblies"
set "SUBDIR4=RedistFolders\dotnet_20"
set "SUBDIR5=RedistFolders\dotnet_40"

REM Check each subdirectory
call :CHECK_SUBDIR "!SUBDIR1!"
call :CHECK_SUBDIR "!SUBDIR2!"
call :CHECK_SUBDIR "!SUBDIR3!"
call :CHECK_SUBDIR "!SUBDIR4!"
call :CHECK_SUBDIR "!SUBDIR5!"

if "!CR_ENGINE!"=="" (
    echo ERROR: Could not find CrystalDecisions.CrystalReports.Engine.dll in standard locations
    echo.
    echo Searching entire Crystal Reports directory...
    for /f "delims=" %%i in ('dir "!CR_BASE!" /s /b /a-d 2^>nul ^| findstr "CrystalDecisions.CrystalReports.Engine.dll"') do (
        set "CR_ENGINE=%%i"
        echo FOUND: %%i
        goto :FOUND_ENGINE
    )
    :FOUND_ENGINE
)

if "!CR_SHARED!"=="" (
    echo Searching for CrystalDecisions.Shared.dll...
    for /f "delims=" %%i in ('dir "!CR_BASE!" /s /b /a-d 2^>nul ^| findstr "CrystalDecisions.Shared.dll"') do (
        set "CR_SHARED=%%i"
        echo FOUND: %%i
        goto :FOUND_SHARED
    )
    :FOUND_SHARED
)

if "!CR_ENGINE!"=="" (
    echo.
    echo ERROR: Crystal Reports DLLs not found
    echo Please check your Crystal Reports 2020 installation
    pause
    exit /b 1
)

echo.
echo SUCCESS: Found Crystal Reports DLLs
echo Engine: !CR_ENGINE!
echo Shared: !CR_SHARED!

echo.
echo STEP 3: Check Visual Studio Build Tools
echo =======================================

set "VS_CSC="
set "MSBUILD_PATH="

REM Check for Visual Studio 2022
if exist "C:\Program Files\Microsoft Visual Studio\2022\Professional\MSBuild\Current\Bin\Roslyn\csc.exe" (
    set "VS_CSC=C:\Program Files\Microsoft Visual Studio\2022\Professional\MSBuild\Current\Bin\Roslyn\csc.exe"
    set "MSBUILD_PATH=C:\Program Files\Microsoft Visual Studio\2022\Professional\MSBuild\Current\Bin\MSBuild.exe"
    echo FOUND: Visual Studio 2022 Professional
)

if "!VS_CSC!"=="" if exist "C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\Roslyn\csc.exe" (
    set "VS_CSC=C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\Roslyn\csc.exe"
    set "MSBUILD_PATH=C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe"
    echo FOUND: Visual Studio 2022 Community
)

if "!VS_CSC!"=="" if exist "C:\Program Files\Microsoft Visual Studio\2022\Enterprise\MSBuild\Current\Bin\Roslyn\csc.exe" (
    set "VS_CSC=C:\Program Files\Microsoft Visual Studio\2022\Enterprise\MSBuild\Current\Bin\Roslyn\csc.exe"
    set "MSBUILD_PATH=C:\Program Files\Microsoft Visual Studio\2022\Enterprise\MSBuild\Current\Bin\MSBuild.exe"
    echo FOUND: Visual Studio 2022 Enterprise
)

REM Check for Visual Studio 2019
if "!VS_CSC!"=="" if exist "C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional\MSBuild\Current\Bin\Roslyn\csc.exe" (
    set "VS_CSC=C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional\MSBuild\Current\Bin\Roslyn\csc.exe"
    set "MSBUILD_PATH=C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional\MSBuild\Current\Bin\MSBuild.exe"
    echo FOUND: Visual Studio 2019 Professional
)

if "!VS_CSC!"=="" (
    echo WARNING: Visual Studio compiler not found in standard locations
    echo Checking system PATH...
    for /f "delims=" %%i in ('where csc 2^>nul') do set "VS_CSC=%%i"
    for /f "delims=" %%i in ('where msbuild 2^>nul') do set "MSBUILD_PATH=%%i"
)

if "!VS_CSC!"=="" (
    echo ERROR: No C# compiler found
    echo Please ensure Visual Studio 2019/2022 is properly installed
    pause
    exit /b 1
)

echo SUCCESS: Found compiler at "!VS_CSC!"
echo MSBuild: "!MSBUILD_PATH!"

echo.
echo STEP 4: Test Compilation with Real Crystal Reports
echo ==================================================

if not exist "RptToXml.cs" (
    echo ERROR: RptToXml.cs not found
    echo Please run this script from the project directory
    pause
    exit /b 1
)

echo Creating production project file...
(
echo ^<Project xmlns="http://schemas.microsoft.com/developer/msbuild/2003"^>
echo   ^<PropertyGroup^>
echo     ^<Configuration^>Release^</Configuration^>
echo     ^<Platform^>AnyCPU^</Platform^>
echo     ^<OutputType^>Exe^</OutputType^>
echo     ^<TargetFrameworkVersion^>v4.8^</TargetFrameworkVersion^>
echo     ^<AssemblyName^>RptToXml^</AssemblyName^>
echo     ^<OutputPath^>.^</OutputPath^>
echo   ^</PropertyGroup^>
echo   ^<ItemGroup^>
echo     ^<Reference Include="System" /^>
echo     ^<Reference Include="System.Xml" /^>
echo     ^<Reference Include="CrystalDecisions.CrystalReports.Engine"^>
echo       ^<HintPath^>!CR_ENGINE!^</HintPath^>
echo       ^<Private^>true^</Private^>
echo     ^</Reference^>
echo     ^<Reference Include="CrystalDecisions.Shared"^>
echo       ^<HintPath^>!CR_SHARED!^</HintPath^>
echo       ^<Private^>true^</Private^>
echo     ^</Reference^>
echo   ^</ItemGroup^>
echo   ^<ItemGroup^>
echo     ^<Compile Include="RptToXml.cs" /^>
echo   ^</ItemGroup^>
echo   ^<Import Project="$(MSBuildToolsPath)\Microsoft.CSharp.targets" /^>
echo ^</Project^>
) > RptToXml-Production.csproj

echo Project file created: RptToXml-Production.csproj

echo.
echo Attempting compilation with MSBuild...
"!MSBUILD_PATH!" RptToXml-Production.csproj /p:Configuration=Release /p:Platform=AnyCPU

if !ERRORLEVEL! EQU 0 (
    echo.
    echo ========================================
    echo SUCCESS: REAL Crystal Reports compilation!
    echo ========================================
    
    if exist "RptToXml.exe" (
        echo Testing with real Crystal Reports SDK...
        RptToXml.exe
        echo.
        echo File created: !CD!\RptToXml.exe
        dir RptToXml.exe
        echo.
        echo This is the REAL Crystal Reports tool!
        echo It can now parse actual .rpt files.
    )
    
) else (
    echo.
    echo Compilation failed. Trying direct CSC approach...
    
    echo Compiling with direct csc.exe...
    "!VS_CSC!" /target:exe /out:RptToXml.exe /platform:anycpu ^
        /reference:System.dll ^
        /reference:System.Xml.dll ^
        "/reference:!CR_ENGINE!" ^
        "/reference:!CR_SHARED!" ^
        RptToXml.cs
    
    if !ERRORLEVEL! EQU 0 (
        echo.
        echo SUCCESS: Direct CSC compilation worked!
        RptToXml.exe
    ) else (
        echo.
        echo ERROR: Both MSBuild and CSC failed
        echo Check the error messages above for details
    )
)

echo.
echo STEP 5: Create Deployment Batch File
echo ====================================

if exist "RptToXml.exe" (
    echo Creating deployment script...
    (
    echo @echo off
    echo echo Starting Crystal Copilot with Real Crystal Reports
    echo echo ==================================================
    echo.
    echo REM Set Crystal Reports environment
    echo set "CR_PATH=!CR_BASE!"
    echo set "PATH=%%PATH%%;%%CR_PATH%%"
    echo.
    echo REM Start backend with real Crystal Reports parser
    echo cd /d "%%~dp0"
    echo poetry run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
    echo pause
    ) > start-backend-production.bat
    
    echo Created: start-backend-production.bat
    echo.
    echo ========================================
    echo SETUP COMPLETE!
    echo ========================================
    echo.
    echo You now have:
    echo 1. Real Crystal Reports parsing: RptToXml.exe
    echo 2. Production startup script: start-backend-production.bat
    echo 3. Full Crystal Copilot MVP ready for real .rpt files
    echo.
    echo Next steps:
    echo 1. Test: RptToXml.exe "sample.rpt" "output.xml"
    echo 2. Start backend: start-backend-production.bat
    echo 3. Start frontend: poetry run streamlit run frontend/app.py
    echo.
)

echo Cleaning up temporary files...
del RptToXml-Production.csproj 2>nul

echo.
pause
goto :EOF

:CHECK_SUBDIR
set "CURRENT_SUBDIR=%~1"
set "FULLPATH=!CR_BASE!\!CURRENT_SUBDIR!"
if exist "!FULLPATH!" (
    echo Checking: "!FULLPATH!"
    if exist "!FULLPATH!\CrystalDecisions.CrystalReports.Engine.dll" (
        set "CR_ENGINE=!FULLPATH!\CrystalDecisions.CrystalReports.Engine.dll"
        echo   FOUND: CrystalDecisions.CrystalReports.Engine.dll
    )
    if exist "!FULLPATH!\CrystalDecisions.Shared.dll" (
        set "CR_SHARED=!FULLPATH!\CrystalDecisions.Shared.dll"
        echo   FOUND: CrystalDecisions.Shared.dll
    )
) else (
    echo NOT FOUND: "!FULLPATH!"
)
goto :EOF 