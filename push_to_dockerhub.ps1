<#
.SYNOPSIS
    Push local image to Docker Hub
#>

$ErrorActionPreference = "Stop"

# Configuration
$LocalImageName = "pdf-editor-uos"
$LocalTag = "lean"
$FullLocalImage = "$LocalImageName`:$LocalTag"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Push Image to Docker Hub" -ForegroundColor Cyan
Write-Host "Local Image: $FullLocalImage" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 1. Check Docker Status
if (-not (docker info 2>&1 | Select-String "Server Version")) {
    Write-Error "Docker is not running. Please start Docker Desktop."
}

# 2. Check Login Status
Write-Host "`n[1/4] Checking login status..." -ForegroundColor Yellow
try {
    docker login
} catch {
    Write-Error "Login failed. Please check your credentials."
}

# 3. Get Docker Hub Username
Write-Host "`n[2/4] Configuring repository..." -ForegroundColor Yellow
$HubUser = Read-Host "Please enter your Docker Hub username (e.g. myusername)"

if ([string]::IsNullOrWhiteSpace($HubUser)) {
    Write-Error "Username cannot be empty."
}

$TargetImage = "$HubUser/$LocalImageName`:$LocalTag"

# 4. Retag Image
Write-Host "`n[3/4] Retagging image..." -ForegroundColor Yellow
Write-Host "Tagging $FullLocalImage as $TargetImage ..." -ForegroundColor Gray

# Check if local image exists
if (-not (docker images -q $FullLocalImage)) {
    Write-Error "Local image $FullLocalImage not found. Please run build_uos_arm64.ps1 first."
}

docker tag $FullLocalImage $TargetImage
Write-Host "Tag success!" -ForegroundColor Green

# 5. Push Image
Write-Host "`n[4/4] Pushing to Docker Hub..." -ForegroundColor Yellow
Write-Host "Pushing $TargetImage (this may take a while)..." -ForegroundColor Gray

docker push $TargetImage

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n==========================================" -ForegroundColor Green
    Write-Host "Push Success!" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "You can now pull the image on UOS:" -ForegroundColor Cyan
    Write-Host "docker pull $TargetImage" -ForegroundColor Cyan
} else {
    Write-Host "`nPush Failed" -ForegroundColor Red
    Write-Host "Common reasons:" -ForegroundColor Gray
    Write-Host "1. Incorrect Docker Hub username" -ForegroundColor Gray
    Write-Host "2. Repository '$LocalImageName' does not exist (may need manual creation)" -ForegroundColor Gray
    Write-Host "3. Network connection issues" -ForegroundColor Gray
}
