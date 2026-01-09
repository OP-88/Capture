# Capture - Docker run script for Windows (PowerShell)
# Launches the Capture GUI application in a Docker container

Write-Host "🐳 Starting Capture in Docker (Windows)..." -ForegroundColor Cyan

# Check if Docker Desktop is running
$dockerRunning = Get-Process "Docker Desktop" -ErrorAction SilentlyContinue
if (-not $dockerRunning) {
    Write-Host "❌ Error: Docker Desktop is not running" -ForegroundColor Red
    Write-Host "Please start Docker Desktop and try again" -ForegroundColor Yellow
    exit 1
}

# Check for WSL2
$wslVersion = wsl --list --verbose 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error: WSL2 is not installed" -ForegroundColor Red
    Write-Host "Please install WSL2: https://docs.microsoft.com/en-us/windows/wsl/install" -ForegroundColor Yellow
    exit 1
}

# Check if X server is running (VcXsrv or Xming)
$xServerRunning = Get-Process "vcxsrv","Xming" -ErrorAction SilentlyContinue
if (-not $xServerRunning) {
    Write-Host "⚠️  Warning: No X server detected (VcXsrv or Xming)" -ForegroundColor Yellow
    Write-Host "Please install and start VcXsrv: https://sourceforge.net/projects/vcxsrv/" -ForegroundColor Yellow
    Write-Host "Configure VcXsrv with: -ac -multiwindow" -ForegroundColor Yellow
    $continue = Read-Host "Continue anyway? (y/N)"
    if ($continue -ne "y") {
        exit 0
    }
}

# Get Windows host IP for WSL2
$hostIP = (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias "vEthernet (WSL)").IPAddress
if (-not $hostIP) {
    $hostIP = "host.docker.internal"
}

Write-Host "Using Display: ${hostIP}:0" -ForegroundColor Green

# Set DISPLAY variable
$env:DISPLAY = "${hostIP}:0"

# Determine image source
if ($args -contains "--local") {
    $image = "capture:latest"
    Write-Host "Using locally built image" -ForegroundColor Green
} else {
    $image = "ogq0w3efq/capture:latest"
    Write-Host "Using Docker Hub image (ogq0w3efq/capture:latest)" -ForegroundColor Green
    Write-Host "Pulling latest version..." -ForegroundColor Cyan
    docker pull $image
}

# Run the container
Write-Host "Launching Capture GUI..." -ForegroundColor Cyan
docker run --rm `
    -e DISPLAY=$env:DISPLAY `
    -v capture-data:/app/data `
    --name capture `
    $image

Write-Host "✅ Capture stopped" -ForegroundColor Green
