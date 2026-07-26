<#
.SYNOPSIS
    Build Docker image for UOS (arm64) using Dockerfile.lean
#>

$ErrorActionPreference = "Stop"

# Configuration
$ImageName = "pdf-editor-uos"
$Tag = "lean"
$FullImageName = "$ImageName`:$Tag"
$TarFileName = "pdf-editor-uos-lean-arm64.tar"
$Dockerfile = "Dockerfile.lean"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "PDF Editor Integrated - Docker Build" -ForegroundColor Cyan
Write-Host "Target Platform: UOS arm64" -ForegroundColor Cyan
Write-Host "Configuration: $Dockerfile" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 1. Check Docker Environment
Write-Host "`n[1/4] Checking Docker environment..." -ForegroundColor Yellow
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error "Docker is not installed. Please install Docker Desktop."
}

if (-not (docker info 2>&1 | Select-String "Server Version")) {
    Write-Error "Docker service is not running. Please start Docker Desktop."
}
Write-Host "Docker environment is ready." -ForegroundColor Green

# 2. Check Required Files
Write-Host "`n[2/4] Checking required files..." -ForegroundColor Yellow
$RequiredFiles = @("app.py", "requirements.txt", $Dockerfile)
foreach ($file in $RequiredFiles) {
    if (-not (Test-Path $file)) {
        Write-Error "Missing required file: $file"
    }
}
Write-Host "Required files present." -ForegroundColor Green

# 3. Build Image
Write-Host "`n[3/4] Building Docker image (this may take a few minutes)..." -ForegroundColor Yellow
Write-Host "Building for linux/arm64 architecture using standard docker build..." -ForegroundColor Gray
Write-Host "Note: Cross-platform build may be slow due to QEMU emulation." -ForegroundColor Gray

# Use standard docker build command which supports --platform in Docker Desktop
docker build --platform linux/arm64 -t $FullImageName -f $Dockerfile .

if ($LASTEXITCODE -eq 0) {
    Write-Host "Build success!" -ForegroundColor Green
} else {
    Write-Error "Build failed. Please check the logs."
}

# 4. Export Image
Write-Host "`n[4/4] Exporting image to tarball..." -ForegroundColor Yellow
$OutputPath = Join-Path "docker镜像" $TarFileName
if (-not (Test-Path "docker镜像")) {
    New-Item -ItemType Directory -Force -Path "docker镜像" | Out-Null
}

Write-Host "Saving image to $OutputPath ..." -ForegroundColor Gray
docker save -o $OutputPath $FullImageName

if (Test-Path $OutputPath) {
    $FileSize = (Get-Item $OutputPath).Length / 1MB
    Write-Host "Image export success!" -ForegroundColor Green
    Write-Host "File Path: $OutputPath" -ForegroundColor Green
    Write-Host "File Size: $([math]::Round($FileSize, 2)) MB" -ForegroundColor Green
    
    Write-Host "`n==========================================" -ForegroundColor Cyan
    Write-Host "Deployment Guide:" -ForegroundColor Cyan
    Write-Host "1. Copy $OutputPath to the UOS machine"
    Write-Host "2. Run: docker load -i $TarFileName"
    Write-Host "3. Run: docker run -d -p 5000:5000 --name pdf-editor $FullImageName"
    Write-Host "==========================================" -ForegroundColor Cyan
} else {
    Write-Error "Image export failed."
}
