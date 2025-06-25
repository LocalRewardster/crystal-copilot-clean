@echo off
echo Crystal Reports Compilation with Visual Studio
echo ===============================================
echo.

if not exist "RptToXml.cs" (
    echo ERROR: RptToXml.cs not found
    echo Please run this script from the project directory
    pause
    exit /b 1
)

echo Step 1: Finding Visual Studio and MSBuild...
echo =============================================

set "VS_PATH="
set "MSBUILD_PATH="
set "CSC_PATH="

REM Try Visual Studio 2022 locations
if exist "C:\Program Files\Microsoft Visual Studio\2022\Community" (
    set "VS_PATH=C:\Program Files\Microsoft Visual Studio\2022\Community"
    set "MSBUILD_PATH=C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe"
    set "CSC_PATH=C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\Roslyn\csc.exe"
    echo FOUND: Visual Studio 2022 Community
    goto :FOUND_VS
)

if exist "C:\Program Files\Microsoft Visual Studio\2022\Professional" (
    set "VS_PATH=C:\Program Files\Microsoft Visual Studio\2022\Professional"
    set "MSBUILD_PATH=C:\Program Files\Microsoft Visual Studio\2022\Professional\MSBuild\Current\Bin\MSBuild.exe"
    set "CSC_PATH=C:\Program Files\Microsoft Visual Studio\2022\Professional\MSBuild\Current\Bin\Roslyn\csc.exe"
    echo FOUND: Visual Studio 2022 Professional
    goto :FOUND_VS
)

if exist "C:\Program Files\Microsoft Visual Studio\2022\Enterprise" (
    set "VS_PATH=C:\Program Files\Microsoft Visual Studio\2022\Enterprise"
    set "MSBUILD_PATH=C:\Program Files\Microsoft Visual Studio\2022\Enterprise\MSBuild\Current\Bin\MSBuild.exe"
    set "CSC_PATH=C:\Program Files\Microsoft Visual Studio\2022\Enterprise\MSBuild\Current\Bin\Roslyn\csc.exe"
    echo FOUND: Visual Studio 2022 Enterprise
    goto :FOUND_VS
)

REM Try Visual Studio 2019 locations
if exist "C:\Program Files (x86)\Microsoft Visual Studio\2019\Community" (
    set "VS_PATH=C:\Program Files (x86)\Microsoft Visual Studio\2019\Community"
    set "MSBUILD_PATH=C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\MSBuild\Current\Bin\MSBuild.exe"
    set "CSC_PATH=C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\MSBuild\Current\Bin\Roslyn\csc.exe"
    echo FOUND: Visual Studio 2019 Community
    goto :FOUND_VS
)

if exist "C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional" (
    set "VS_PATH=C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional"
    set "MSBUILD_PATH=C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional\MSBuild\Current\Bin\MSBuild.exe"
    set "CSC_PATH=C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional\MSBuild\Current\Bin\Roslyn\csc.exe"
    echo FOUND: Visual Studio 2019 Professional
    goto :FOUND_VS
)

echo ERROR: Visual Studio not found in standard locations
echo.
echo Please check if Visual Studio is installed at:
echo - C:\Program Files\Microsoft Visual Studio\2022\
echo - C:\Program Files (x86)\Microsoft Visual Studio\2019\
echo.
pause
exit /b 1

:FOUND_VS
echo Visual Studio Path: %VS_PATH%
echo MSBuild Path: %MSBUILD_PATH%
echo.

echo Step 2: Finding Crystal Reports DLLs...
echo =======================================

set "CR_BASE=C:\Program Files (x86)\SAP BusinessObjects\Crystal Reports for .NET Framework 4.0"
set "CR_ENGINE="
set "CR_SHARED="

echo Searching for Crystal Reports DLLs...
echo Base path: %CR_BASE%
echo.

REM Search for the DLLs in the Crystal Reports installation
for /f "delims=" %%i in ('dir "%CR_BASE%" /s /b /a-d 2^>nul ^| findstr /i "CrystalDecisions.CrystalReports.Engine.dll"') do (
    set "CR_ENGINE=%%i"
    echo FOUND Engine DLL: %%i
)

for /f "delims=" %%i in ('dir "%CR_BASE%" /s /b /a-d 2^>nul ^| findstr /i "CrystalDecisions.Shared.dll"') do (
    set "CR_SHARED=%%i"
    echo FOUND Shared DLL: %%i
)

if "%CR_ENGINE%"=="" (
    echo ERROR: Could not find CrystalDecisions.CrystalReports.Engine.dll
    echo.
    echo The diagnostic script found Crystal Reports DLLs earlier.
    echo Let's try some common locations...
    
    REM Try common subdirectories
    if exist "%CR_BASE%\Assemblies\CrystalDecisions.CrystalReports.Engine.dll" (
        set "CR_ENGINE=%CR_BASE%\Assemblies\CrystalDecisions.CrystalReports.Engine.dll"
        echo FOUND in Assemblies: %CR_ENGINE%
    )
    
    if exist "%CR_BASE%\Assemblies\CrystalDecisions.Shared.dll" (
        set "CR_SHARED=%CR_BASE%\Assemblies\CrystalDecisions.Shared.dll"
        echo FOUND in Assemblies: %CR_SHARED%
    )
)

if "%CR_ENGINE%"=="" (
    echo.
    echo ERROR: Crystal Reports DLLs not found
    echo Please run find-crystal-dlls.bat first to locate them
    echo Then manually edit this script with the correct paths
    pause
    exit /b 1
)

echo.
echo Step 3: Creating Visual Studio project file...
echo ==============================================

echo Creating RptToXml.csproj...
(
echo ^<Project Sdk="Microsoft.NET.Sdk"^>
echo   ^<PropertyGroup^>
echo     ^<OutputType^>Exe^</OutputType^>
echo     ^<TargetFramework^>net48^</TargetFramework^>
echo     ^<AssemblyName^>RptToXml^</AssemblyName^>
echo     ^<UseWindowsForms^>false^</UseWindowsForms^>
echo     ^<GenerateAssemblyInfo^>false^</GenerateAssemblyInfo^>
echo     ^<EnableDefaultCompileItems^>false^</EnableDefaultCompileItems^>
echo   ^</PropertyGroup^>
echo.
echo   ^<ItemGroup^>
echo     ^<Reference Include="System" /^>
echo     ^<Reference Include="System.Xml" /^>
echo     ^<Reference Include="CrystalDecisions.CrystalReports.Engine"^>
echo       ^<HintPath^>%CR_ENGINE%^</HintPath^>
echo       ^<Private^>true^</Private^>
echo     ^</Reference^>
echo     ^<Reference Include="CrystalDecisions.Shared"^>
echo       ^<HintPath^>%CR_SHARED%^</HintPath^>
echo       ^<Private^>true^</Private^>
echo     ^</Reference^>
echo   ^</ItemGroup^>
echo.
echo   ^<ItemGroup^>
echo     ^<Compile Include="RptToXml.cs" /^>
echo   ^</ItemGroup^>
echo ^</Project^>
) > RptToXml.csproj

echo Project file created: RptToXml.csproj

echo.
echo Step 4: Compiling with MSBuild...
echo =================================

echo Using MSBuild: %MSBUILD_PATH%
echo.

"%MSBUILD_PATH%" RptToXml.csproj /p:Configuration=Release /p:Platform=AnyCPU /verbosity:minimal

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo SUCCESS: Crystal Reports compilation!
    echo ========================================
    
    REM Look for the executable in bin folders
    if exist "bin\Release\net48\RptToXml.exe" (
        copy "bin\Release\net48\RptToXml.exe" "RptToXml.exe"
        echo Copied executable to current directory
    )
    
    if exist "RptToXml.exe" (
        echo.
        echo Testing the compiled executable...
        RptToXml.exe
        echo.
        echo File details:
        dir RptToXml.exe
        echo.
        echo SUCCESS: RptToXml.exe is ready!
        echo Usage: RptToXml.exe "input.rpt" "output.xml"
    ) else (
        echo.
        echo Compilation succeeded but executable not found in expected location
        echo Checking bin directories...
        dir bin /s /b | findstr "RptToXml.exe"
    )
) else (
    echo.
    echo ERROR: MSBuild compilation failed
    echo.
    echo Try compiling manually in Visual Studio:
    echo 1. Open Visual Studio
    echo 2. File ^> Open ^> Project/Solution
    echo 3. Select RptToXml.csproj
    echo 4. Build ^> Build Solution
)

echo.
echo Cleaning up...
del RptToXml.csproj 2>nul
rmdir /s /q bin 2>nul
rmdir /s /q obj 2>nul

echo.
pause 