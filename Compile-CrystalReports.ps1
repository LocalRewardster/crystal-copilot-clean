# Crystal Reports PowerShell Compilation Script
# =============================================

Write-Host "Crystal Reports PowerShell Compiler" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green
Write-Host ""

# Check if RptToXml.cs exists
if (-not (Test-Path "RptToXml.cs")) {
    Write-Host "ERROR: RptToXml.cs not found in current directory" -ForegroundColor Red
    Write-Host "Current directory: $(Get-Location)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please ensure you're in the project directory with RptToXml.cs"
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Step 1: Finding Visual Studio and MSBuild..." -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# Find Visual Studio installation
$vsPath = $null
$msbuildPath = $null

$vsPaths = @(
    "C:\Program Files\Microsoft Visual Studio\2022\Community",
    "C:\Program Files\Microsoft Visual Studio\2022\Professional", 
    "C:\Program Files\Microsoft Visual Studio\2022\Enterprise",
    "C:\Program Files (x86)\Microsoft Visual Studio\2019\Community",
    "C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional",
    "C:\Program Files (x86)\Microsoft Visual Studio\2019\Enterprise"
)

foreach ($path in $vsPaths) {
    if (Test-Path $path) {
        $vsPath = $path
        $msbuildPath = Join-Path $path "MSBuild\Current\Bin\MSBuild.exe"
        if (Test-Path $msbuildPath) {
            Write-Host "FOUND: Visual Studio at $path" -ForegroundColor Green
            Write-Host "MSBuild: $msbuildPath" -ForegroundColor Green
            break
        }
    }
}

if (-not $msbuildPath -or -not (Test-Path $msbuildPath)) {
    Write-Host "ERROR: Visual Studio MSBuild not found" -ForegroundColor Red
    Write-Host ""
    Write-Host "Searched locations:" -ForegroundColor Yellow
    foreach ($path in $vsPaths) {
        Write-Host "  - $path" -ForegroundColor Gray
    }
    Write-Host ""
    Write-Host "Please ensure Visual Studio 2019 or 2022 is properly installed"
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Step 2: Finding Crystal Reports DLLs..." -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan

$crBase = "C:\Program Files (x86)\SAP BusinessObjects\Crystal Reports for .NET Framework 4.0"
Write-Host "Searching in: $crBase" -ForegroundColor Yellow

# Find Crystal Reports DLLs
$engineDll = $null
$sharedDll = $null

if (Test-Path $crBase) {
    # Search recursively for the DLLs
    $engineDll = Get-ChildItem -Path $crBase -Recurse -Filter "CrystalDecisions.CrystalReports.Engine.dll" -ErrorAction SilentlyContinue | Select-Object -First 1
    $sharedDll = Get-ChildItem -Path $crBase -Recurse -Filter "CrystalDecisions.Shared.dll" -ErrorAction SilentlyContinue | Select-Object -First 1
    
    if ($engineDll) {
        Write-Host "FOUND Engine DLL: $($engineDll.FullName)" -ForegroundColor Green
    }
    if ($sharedDll) {
        Write-Host "FOUND Shared DLL: $($sharedDll.FullName)" -ForegroundColor Green
    }
} else {
    Write-Host "ERROR: Crystal Reports base directory not found: $crBase" -ForegroundColor Red
}

if (-not $engineDll -or -not $sharedDll) {
    Write-Host ""
    Write-Host "ERROR: Required Crystal Reports DLLs not found" -ForegroundColor Red
    Write-Host "Please run find-crystal-dlls.bat first to locate them" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Step 3: Creating project file..." -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

$projectContent = @"
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net48</TargetFramework>
    <AssemblyName>RptToXml</AssemblyName>
    <UseWindowsForms>false</UseWindowsForms>
    <GenerateAssemblyInfo>false</GenerateAssemblyInfo>
  </PropertyGroup>

  <ItemGroup>
    <Reference Include="System" />
    <Reference Include="System.Xml" />
    <Reference Include="CrystalDecisions.CrystalReports.Engine">
      <HintPath>$($engineDll.FullName)</HintPath>
      <Private>true</Private>
    </Reference>
    <Reference Include="CrystalDecisions.Shared">
      <HintPath>$($sharedDll.FullName)</HintPath>
      <Private>true</Private>
    </Reference>
  </ItemGroup>

  <ItemGroup>
    <Compile Include="RptToXml.cs" />
  </ItemGroup>
</Project>
"@

$projectFile = "RptToXml.csproj"
$projectContent | Out-File -FilePath $projectFile -Encoding UTF8
Write-Host "Created: $projectFile" -ForegroundColor Green

Write-Host ""
Write-Host "Step 4: Compiling with MSBuild..." -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

Write-Host "Using MSBuild: $msbuildPath" -ForegroundColor Yellow
Write-Host ""

# Run MSBuild
$buildArgs = @($projectFile, "/p:Configuration=Release", "/p:Platform=AnyCPU", "/verbosity:minimal")
$process = Start-Process -FilePath $msbuildPath -ArgumentList $buildArgs -Wait -PassThru -NoNewWindow

if ($process.ExitCode -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "SUCCESS: Crystal Reports compilation!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    
    # Find and copy the executable
    $exePath = "bin\Release\net48\RptToXml.exe"
    if (Test-Path $exePath) {
        Copy-Item $exePath "RptToXml.exe" -Force
        Write-Host "Copied executable to current directory" -ForegroundColor Green
    }
    
    if (Test-Path "RptToXml.exe") {
        Write-Host ""
        Write-Host "Testing the compiled executable..." -ForegroundColor Yellow
        & ".\RptToXml.exe"
        Write-Host ""
        Write-Host "File details:" -ForegroundColor Yellow
        Get-ChildItem "RptToXml.exe" | Format-Table Name, Length, LastWriteTime
        Write-Host ""
        Write-Host "SUCCESS: RptToXml.exe is ready!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Usage: .\RptToXml.exe 'input.rpt' 'output.xml'" -ForegroundColor Cyan
    } else {
        Write-Host ""
        Write-Host "Compilation succeeded but executable not found in expected location" -ForegroundColor Yellow
        Write-Host "Checking bin directories..." -ForegroundColor Yellow
        Get-ChildItem -Path "bin" -Recurse -Filter "RptToXml.exe" -ErrorAction SilentlyContinue
    }
} else {
    Write-Host ""
    Write-Host "ERROR: MSBuild compilation failed" -ForegroundColor Red
    Write-Host ""
    Write-Host "You can try compiling manually in Visual Studio:" -ForegroundColor Yellow
    Write-Host "1. Open Visual Studio" -ForegroundColor Gray
    Write-Host "2. File > Open > Project/Solution" -ForegroundColor Gray
    Write-Host "3. Select RptToXml.csproj" -ForegroundColor Gray
    Write-Host "4. Build > Build Solution" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Cleaning up..." -ForegroundColor Yellow
Remove-Item $projectFile -ErrorAction SilentlyContinue
Remove-Item "bin" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "obj" -Recurse -Force -ErrorAction SilentlyContinue

Write-Host ""
Read-Host "Press Enter to exit" 