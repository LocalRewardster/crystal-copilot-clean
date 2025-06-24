# PowerShell script to build Windows container locally
Write-Host "Building Crystal Copilot Windows Container..."

# Switch to Windows containers
& "C:\Program Files\Docker\Docker\DockerCli.exe" -SwitchDaemon

# Build the container
docker build -f Dockerfile.windows -t crystal-copilot-windows:latest .

# Test the container
docker run --rm crystal-copilot-windows:latest python test_container.py

Write-Host "Build complete! Container ready for use."
