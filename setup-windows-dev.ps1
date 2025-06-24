# Crystal Copilot Windows Development Environment Setup Script
# Run this on your Windows PC as Administrator

Write-Host "Setting up Crystal Copilot Development Environment" -ForegroundColor Green
Write-Host "============================================================"

# Check if running as Administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "SUCCESS: Running as Administrator" -ForegroundColor Green

# Install Chocolatey if not present
if (!(Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Chocolatey..." -ForegroundColor Yellow
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    refreshenv
} else {
    Write-Host "SUCCESS: Chocolatey already installed" -ForegroundColor Green
}

# Install essential development tools
Write-Host "Installing development tools..." -ForegroundColor Yellow

$packages = @(
    "python312",
    "git", 
    "vscode",
    "docker-desktop",
    "dotnetfx",
    "vcredist2019"
)

foreach ($package in $packages) {
    Write-Host "Installing $package..." -ForegroundColor Cyan
    choco install $package -y --no-progress
}

# Refresh environment
refreshenv

Write-Host "SUCCESS: Development tools installed" -ForegroundColor Green

# Install Poetry for Python dependency management
Write-Host "Installing Poetry..." -ForegroundColor Yellow
if (!(Get-Command poetry -ErrorAction SilentlyContinue)) {
    (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
    $poetryPath = Join-Path $env:APPDATA "Python\Scripts"
    $env:PATH += ";$poetryPath"
    Write-Host "SUCCESS: Poetry installed" -ForegroundColor Green
} else {
    Write-Host "SUCCESS: Poetry already installed" -ForegroundColor Green
}

# Create development directory
$devDir = "C:\CrystalCopilot"
if (!(Test-Path $devDir)) {
    New-Item -ItemType Directory -Path $devDir -Force
    Write-Host "SUCCESS: Created development directory: $devDir" -ForegroundColor Green
}

# Download Crystal Reports Runtime (requires manual installation)
Write-Host "Downloading Crystal Reports Runtime..." -ForegroundColor Yellow
$crRuntimeUrl = "https://downloads.businessobjects.com/akdlm/crnetruntime/win/32bit/CRforVS_13_0_33.exe"
$crRuntimePath = Join-Path $devDir "CRforVS_13_0_33.exe"

try {
    Invoke-WebRequest -Uri $crRuntimeUrl -OutFile $crRuntimePath -UseBasicParsing
    Write-Host "SUCCESS: Crystal Reports Runtime downloaded to: $crRuntimePath" -ForegroundColor Green
    Write-Host "MANUAL STEP: Please install Crystal Reports Runtime manually" -ForegroundColor Yellow
    Write-Host "Run: $crRuntimePath" -ForegroundColor Cyan
} catch {
    Write-Host "WARNING: Could not download Crystal Reports Runtime automatically" -ForegroundColor Yellow
    Write-Host "Please download manually from SAP website" -ForegroundColor Cyan
}

# Create project structure
Write-Host "Creating project structure..." -ForegroundColor Yellow
$projectDirs = @(
    (Join-Path $devDir "crystal-copilot"),
    (Join-Path $devDir "crystal-copilot\reports"),
    (Join-Path $devDir "crystal-copilot\logs"),
    (Join-Path $devDir "crystal-copilot\tools")
)

foreach ($dir in $projectDirs) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force
    }
}

Write-Host "SUCCESS: Project structure created" -ForegroundColor Green

# Create environment file template
$envPath = Join-Path $devDir "crystal-copilot\.env"
$envContent = @'
# Crystal Copilot Environment Configuration
OPENAI_API_KEY=your-openai-api-key-here
CRYSTAL_RUNTIME_PATH=C:\Program Files (x86)\SAP BusinessObjects\Crystal Reports for .NET Framework 4.0\Common\SAP BusinessObjects Enterprise XI 4.0\win64_x64\
RPTTOXML_PATH=C:\CrystalCopilot\crystal-copilot\tools\RptToXml.exe
PYTHONPATH=C:\CrystalCopilot\crystal-copilot
ENVIRONMENT=development
DEBUG=true
'@

$envContent | Out-File -FilePath $envPath -Encoding UTF8
Write-Host "SUCCESS: Environment file created at: $envPath" -ForegroundColor Green

# Create batch files for common tasks
$backendBatPath = Join-Path $devDir "start-backend.bat"
$backendScript = @'
@echo off
echo Starting Crystal Copilot Development Server...
cd /d C:\CrystalCopilot\crystal-copilot
poetry run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
pause
'@

$backendScript | Out-File -FilePath $backendBatPath -Encoding ASCII

$frontendBatPath = Join-Path $devDir "start-frontend.bat"
$frontendScript = @'
@echo off
echo Starting Crystal Copilot Frontend...
cd /d C:\CrystalCopilot\crystal-copilot
poetry run streamlit run frontend/app.py --server.port 8501
pause
'@

$frontendScript | Out-File -FilePath $frontendBatPath -Encoding ASCII

Write-Host "SUCCESS: Startup scripts created" -ForegroundColor Green

Write-Host "" 
Write-Host "Windows Development Environment Setup Complete!" -ForegroundColor Green
Write-Host "============================================================"
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Install Crystal Reports Runtime: $crRuntimePath" -ForegroundColor Cyan
Write-Host "2. Clone your repository to: $(Join-Path $devDir 'crystal-copilot')" -ForegroundColor Cyan
Write-Host "3. Set your OpenAI API key in: $envPath" -ForegroundColor Cyan
Write-Host "4. Run poetry install in the project directory" -ForegroundColor Cyan
Write-Host "5. Run: $backendBatPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "Development Directory: $devDir" -ForegroundColor Green
Write-Host "Happy coding!" -ForegroundColor Green
