# Crystal Copilot Windows Development Guide

## 🪟 Prerequisites for Windows PC

### Required Software
1. **Windows 10/11** (Professional or Enterprise recommended)
2. **Administrator access** for installations
3. **Internet connection** for downloads

## 🚀 Quick Setup (5 minutes)

### Step 1: Download Setup Script
1. Download `setup-windows-dev.ps1` to your Windows PC
2. Right-click PowerShell → "Run as Administrator"
3. Run: `.\setup-windows-dev.ps1`

### Step 2: Install Crystal Reports SDK
1. The script downloads Crystal Reports Runtime automatically
2. **MANUAL STEP**: Install `CRforVS_13_0_33.exe` (requires GUI)
3. Choose "Complete" installation for full SDK

### Step 3: Clone Repository
```powershell
cd C:\CrystalCopilot
git clone https://github.com/your-username/crystal-copilot.git
cd crystal-copilot
```

### Step 4: Set API Key
Edit `C:\CrystalCopilot\crystal-copilot\.env`:
```
OPENAI_API_KEY=your-actual-api-key-here
```

### Step 5: Install Python Dependencies
```powershell
cd C:\CrystalCopilot\crystal-copilot
pip install -r requirements.txt
```

## 🏗️ Build Real RptToXml Tool

### Create the C# Tool
```powershell
# Navigate to tools directory
cd C:\CrystalCopilot\crystal-copilot\tools

# The Dockerfile.windows contains the C# source code
# Extract and compile it manually on Windows
```

### Compile Command
```powershell
# Find Crystal Reports DLLs
$crPath = "C:\Program Files (x86)\SAP BusinessObjects\Crystal Reports for .NET Framework 4.0\Common\SAP BusinessObjects Enterprise XI 4.0\win64_x64"

# Compile RptToXml.exe
csc.exe /target:exe /out:RptToXml.exe /reference:"$crPath\CrystalDecisions.CrystalReports.Engine.dll","$crPath\CrystalDecisions.Shared.dll" RptToXml.cs
```

## 🎯 Development Workflow

### Start Backend (Terminal 1)
```powershell
cd C:\CrystalCopilot\crystal-copilot
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Start Frontend (Terminal 2)
```powershell
cd C:\CrystalCopilot\crystal-copilot
streamlit run frontend/app.py --server.port 8501
```

### Access Application
- **Backend API**: http://localhost:8000
- **Frontend**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs

## 🧪 Testing with Real Crystal Reports

### Test RptToXml Tool
```powershell
# Test with sample report
.\tools\RptToXml.exe "sample_reports\your-report.rpt" "output.xml" --verbose
```

### Test Backend Integration
```powershell
# Upload a real .rpt file via the frontend
# Check that it uses RptToXml.exe instead of mock data
```

## 📦 Building Windows Container (Optional)

If you want to containerize for deployment:

```powershell
# Switch Docker to Windows containers
& "C:\Program Files\Docker\Docker\DockerCli.exe" -SwitchDaemon

# Build container
docker build -f Dockerfile.windows -t crystal-copilot-windows:latest .

# Run container
docker run -p 8000:8000 -v "C:\Reports:/app/reports" crystal-copilot-windows:latest
```

## 🚀 Production Deployment

### Option 1: Direct Windows Server
```powershell
# Copy entire project to production server
# Install same prerequisites
# Run with production settings
```

### Option 2: Windows Container
```powershell
# Build and push container
# Deploy to Windows Server with Docker
```

### Option 3: IIS Deployment
```powershell
# Use FastAPI with IIS
# Configure reverse proxy
```

## 🔧 Troubleshooting

### Crystal Reports SDK Issues
- Ensure full SDK installation (not just runtime)
- Check DLL paths in compilation
- Verify .NET Framework 4.0+ is installed

### Permission Issues
- Run PowerShell as Administrator
- Check folder permissions for C:\CrystalCopilot

### Port Conflicts
- Change ports in startup scripts if needed
- Check Windows Firewall settings

## 🎉 Advantages of Windows Development

1. **Real Crystal Reports SDK** - No mock data
2. **Direct testing** - Immediate feedback
3. **Full debugging** - Step through C# code
4. **Production parity** - Same environment as deployment
5. **Faster iteration** - No cloud build times

## 📁 Project Structure
```
C:\CrystalCopilot\
├── crystal-copilot\          # Your repository
│   ├── backend\               # FastAPI backend
│   ├── frontend\              # Streamlit frontend
│   ├── tools\                 # RptToXml.exe location
│   ├── sample_reports\        # Test .rpt files
│   └── .env                   # Environment variables
├── start-backend.bat          # Quick start scripts
├── start-frontend.bat
└── CRforVS_13_0_33.exe       # Crystal Reports installer
```

Ready to build real Crystal Reports modernization! 🚀
