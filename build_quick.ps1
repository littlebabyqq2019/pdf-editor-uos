# 快速构建脚本 - 自动添加Docker到PATH并构建
$env:PATH += ";C:\Program Files\Docker\Docker\resources\bin"

Write-Host "检查Docker服务状态..." -ForegroundColor Cyan
$retries = 0
$maxRetries = 30

while ($retries -lt $maxRetries) {
    try {
        docker info | Out-Null
        Write-Host "✓ Docker服务已就绪" -ForegroundColor Green
        break
    } catch {
        $retries++
        Write-Host "等待Docker服务启动... ($retries/$maxRetries)" -ForegroundColor Yellow
        Start-Sleep -Seconds 2
    }
}

if ($retries -eq $maxRetries) {
    Write-Host "✗ Docker服务启动超时，请手动检查Docker Desktop" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "开始构建Docker镜像..." -ForegroundColor Cyan
Write-Host "镜像: pdf-editor-uos:latest" -ForegroundColor Yellow
Write-Host "平台: linux/arm64" -ForegroundColor Yellow
Write-Host ""

docker build --platform linux/arm64 -t pdf-editor-uos:latest .

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "✓ 构建成功！" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "镜像信息:" -ForegroundColor Cyan
    docker images pdf-editor-uos
    Write-Host ""
    Write-Host "导出镜像: docker save -o pdf-editor-uos-arm64.tar pdf-editor-uos:latest" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "✗ 构建失败" -ForegroundColor Red
    exit 1
}
