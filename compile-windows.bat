@echo off
echo Crystal Copilot - Compiling RptToXml Tool
echo ==========================================

REM Check if we're in the right directory
if not exist "RptToXml.cs" (
    echo ERROR: RptToXml.cs not found in current directory
    echo Please run this script from the tools directory
    pause
    exit /b 1
)

echo Locating Crystal Reports SDK...

REM Find Crystal Reports DLL path
set CR_PATH="C:\Program Files (x86)\SAP BusinessObjects\Crystal Reports for .NET Framework 4.0\Common\SAP BusinessObjects Enterprise XI 4.0\win64_x64"

if not exist %CR_PATH% (
    echo ERROR: Crystal Reports SDK not found at %CR_PATH%
    echo Please install Crystal Reports for Visual Studio SDK
    echo Download from: https://downloads.businessobjects.com/
    pause
    exit /b 1
)

echo Found Crystal Reports SDK at: %CR_PATH%

REM Find C# compiler
set CSC_PATH=""
for /f "delims=" %%i in ('where csc 2^>nul') do set CSC_PATH="%%i"

if %CSC_PATH%=="" (
    echo Searching for Visual Studio C# compiler...
    
    REM Try Visual Studio 2022
    if exist "C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\Roslyn\csc.exe" (
        set CSC_PATH="C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\Roslyn\csc.exe"
    )
    
    REM Try Visual Studio 2019
    if %CSC_PATH%=="" if exist "C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional\MSBuild\Current\Bin\Roslyn\csc.exe" (
        set CSC_PATH="C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional\MSBuild\Current\Bin\Roslyn\csc.exe"
    )
    
    REM Try .NET SDK
    if %CSC_PATH%=="" (
        for /f "delims=" %%i in ('where dotnet 2^>nul') do (
            echo Found .NET SDK, using dotnet build instead...
            goto DOTNET_BUILD
        )
    )
)

if %CSC_PATH%=="" (
    echo ERROR: C# compiler not found
    echo Please install:
    echo - Visual Studio 2019/2022 with C# workload, OR
    echo - .NET SDK 6.0+
    pause
    exit /b 1
)

echo Found C# compiler at: %CSC_PATH%

REM Compile with CSC
echo Compiling RptToXml.exe...
%CSC_PATH% /target:exe /out:RptToXml.exe ^
    /reference:%CR_PATH%\CrystalDecisions.CrystalReports.Engine.dll ^
    /reference:%CR_PATH%\CrystalDecisions.Shared.dll ^
    /reference:%CR_PATH%\CrystalDecisions.ReportSource.dll ^
    RptToXml.cs

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Compilation failed
    pause
    exit /b 1
)

goto SUCCESS

:DOTNET_BUILD
echo Creating temporary .csproj file...
(
echo ^<Project Sdk="Microsoft.NET.Sdk"^>
echo   ^<PropertyGroup^>
echo     ^<OutputType^>Exe^</OutputType^>
echo     ^<TargetFramework^>net48^</TargetFramework^>
echo   ^</PropertyGroup^>
echo   ^<ItemGroup^>
echo     ^<Reference Include="CrystalDecisions.CrystalReports.Engine"^>
echo       ^<HintPath^>%CR_PATH%\CrystalDecisions.CrystalReports.Engine.dll^</HintPath^>
echo     ^</Reference^>
echo     ^<Reference Include="CrystalDecisions.Shared"^>
echo       ^<HintPath^>%CR_PATH%\CrystalDecisions.Shared.dll^</HintPath^>
echo     ^</Reference^>
echo     ^<Reference Include="CrystalDecisions.ReportSource"^>
echo       ^<HintPath^>%CR_PATH%\CrystalDecisions.ReportSource.dll^</HintPath^>
echo     ^</Reference^>
echo   ^</ItemGroup^>
echo ^</Project^>
) > RptToXml.csproj

echo Compiling with .NET SDK...
dotnet build -c Release -o .

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: .NET compilation failed
    del RptToXml.csproj 2>nul
    pause
    exit /b 1
)

del RptToXml.csproj 2>nul

:SUCCESS
echo.
echo ========================================
echo SUCCESS: RptToXml.exe compiled successfully!
echo ========================================

if exist "RptToXml.exe" (
    echo File location: %CD%\RptToXml.exe
    
    REM Test the executable
    echo.
    echo Testing the tool...
    RptToXml.exe
    
    echo.
    echo Tool is ready for use!
    echo.
    echo Usage examples:
    echo   RptToXml.exe "C:\Reports\MyReport.rpt" "C:\Output\MyReport.xml"
    echo   RptToXml.exe report.rpt output.xml --verbose
) else (
    echo ERROR: RptToXml.exe was not created
)

echo.
pause
