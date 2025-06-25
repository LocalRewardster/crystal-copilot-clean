@echo off
echo Simple Crystal Reports Compilation (GAC References)
echo ==================================================
echo.

if not exist "RptToXml.cs" (
    echo ERROR: RptToXml.cs not found
    echo Please run this script from the project directory
    pause
    exit /b 1
)

echo Method 1: Using GAC references (most reliable)
echo ==============================================

REM Find C# compiler
set "CSC_PATH="

REM Check for .NET Framework compiler (most compatible with Crystal Reports)
if exist "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe" (
    set "CSC_PATH=C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
    echo Using .NET Framework 4.0 compiler (64-bit)
) else if exist "C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe" (
    set "CSC_PATH=C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe"
    echo Using .NET Framework 4.0 compiler (32-bit)
) else (
    echo ERROR: .NET Framework compiler not found
    echo Please ensure .NET Framework 4.0+ is installed
    pause
    exit /b 1
)

echo.
echo Compiling with GAC references...
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
        echo Testing the compiled tool...
        echo.
        RptToXml.exe
        echo.
        echo File created: %CD%\RptToXml.exe
        dir RptToXml.exe
        echo.
        echo SUCCESS: Real Crystal Reports tool ready!
    )
) else (
    echo.
    echo Method 1 failed. Trying Method 2: Project file approach
    echo ======================================================
    
    echo Creating simple project file...
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
    echo     ^<Reference Include="CrystalDecisions.CrystalReports.Engine" /^>
    echo     ^<Reference Include="CrystalDecisions.Shared" /^>
    echo   ^</ItemGroup^>
    echo   ^<ItemGroup^>
    echo     ^<Compile Include="RptToXml.cs" /^>
    echo   ^</ItemGroup^>
    echo   ^<Import Project="$(MSBuildToolsPath)\Microsoft.CSharp.targets" /^>
    echo ^</Project^>
    ) > RptToXml-Simple.csproj
    
    REM Try to find MSBuild
    set "MSBUILD_PATH="
    
    if exist "C:\Program Files\Microsoft Visual Studio\2022\Professional\MSBuild\Current\Bin\MSBuild.exe" (
        set "MSBUILD_PATH=C:\Program Files\Microsoft Visual Studio\2022\Professional\MSBuild\Current\Bin\MSBuild.exe"
    ) else if exist "C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe" (
        set "MSBUILD_PATH=C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe"
    ) else if exist "C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional\MSBuild\Current\Bin\MSBuild.exe" (
        set "MSBUILD_PATH=C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional\MSBuild\Current\Bin\MSBuild.exe"
    ) else (
        echo ERROR: MSBuild not found
        echo Please install Visual Studio or Build Tools
        pause
        exit /b 1
    )
    
    echo Using MSBuild: "%MSBUILD_PATH%"
    "%MSBUILD_PATH%" RptToXml-Simple.csproj /p:Configuration=Release
    
    if %ERRORLEVEL% EQU 0 (
        echo.
        echo SUCCESS: MSBuild compilation worked!
        if exist "RptToXml.exe" (
            RptToXml.exe
        )
    ) else (
        echo.
        echo ERROR: Both compilation methods failed
        echo.
        echo This likely means:
        echo 1. Crystal Reports SDK is not properly installed
        echo 2. DLLs are not in GAC or accessible
        echo 3. Need to install Crystal Reports Developer Edition
        echo.
        echo Please run find-crystal-dlls.bat to diagnose the issue
    )
    
    REM Clean up
    del RptToXml-Simple.csproj 2>nul
)

echo.
pause 