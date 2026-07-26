# PDF编辑工具集成版 - Docker镜像构建脚本 (PowerShell版本)
# 适配国产统信UOS系统 (arm64架构)

param(
    [switch]$CleanOld = $false
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "PDF编辑工具集成版 - Docker镜像构建" -ForegroundColor Cyan
Write-Host "目标平台: UOS arm64" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 镜像名称和标签
$ImageName = "pdf-editor-uos"
$ImageTag = "latest"
$FullImageName = "${ImageName}:${ImageTag}"

# 检查Docker是否安装
try {
    $dockerVersion = docker --version
    Write-Host "✓ Docker已安装: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ 错误: Docker未安装，请先安装Docker Desktop" -ForegroundColor Red
    Write-Host "下载地址: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

# 检查Docker服务是否运行
try {
    docker info | Out-Null
    Write-Host "✓ Docker服务正在运行" -ForegroundColor Green
} catch {
    Write-Host "✗ 错误: Docker服务未运行，请启动Docker Desktop" -ForegroundColor Red
    exit 1
}

# 检查必要文件
Write-Host ""
Write-Host "检查必要文件..." -ForegroundColor Cyan
$requiredFiles = @(
    "Dockerfile",
    "app.py",
    "requirements.txt",
    "pdf-new\requirements.txt",
    "pdf-editor（draw）\requirements.txt"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "✓ $file" -ForegroundColor Green
    } else {
        Write-Host "✗ 缺少必要文件: $file" -ForegroundColor Red
        exit 1
    }
}

# 清理旧镜像（可选）
if ($CleanOld) {
    Write-Host ""
    Write-Host "清理旧镜像..." -ForegroundColor Yellow
    try {
        docker rmi -f $FullImageName 2>$null
        Write-Host "✓ 旧镜像已清理" -ForegroundColor Green
    } catch {
        Write-Host "! 未找到旧镜像或清理失败" -ForegroundColor Yellow
    }
}

# 构建镜像
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "开始构建Docker镜像..." -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "镜像名称: $FullImageName" -ForegroundColor Yellow
Write-Host "目标架构: linux/arm64" -ForegroundColor Yellow
Write-Host ""

# 检查是否支持buildx
$useBuildx = $false
try {
    docker buildx version | Out-Null
    $useBuildx = $true
    Write-Host "使用 docker buildx 构建..." -ForegroundColor Cyan
} catch {
    Write-Host "使用 docker build 构建..." -ForegroundColor Cyan
}

# 执行构建
try {
    if ($useBuildx) {
        docker buildx build --platform linux/arm64 -t $FullImageName --load .
    } else {
        docker build --platform linux/arm64 -t $FullImageName .
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "==========================================" -ForegroundColor Green
        Write-Host "✓ Docker镜像构建成功！" -ForegroundColor Green
        Write-Host "==========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "镜像信息:" -ForegroundColor Cyan
        docker images $ImageName
        Write-Host ""
        Write-Host "下一步操作:" -ForegroundColor Green
        Write-Host "1. 启动容器:" -ForegroundColor White
        Write-Host "   docker-compose up -d" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "2. 或使用docker run启动:" -ForegroundColor White
        Write-Host "   docker run -d -p 5000:5000 --name pdf-editor $FullImageName" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "3. 查看日志:" -ForegroundColor White
        Write-Host "   docker logs -f pdf-editor" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "4. 导出镜像(用于UOS系统):" -ForegroundColor White
        Write-Host "   docker save -o pdf-editor-uos-arm64.tar $FullImageName" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "5. 在UOS系统上导入镜像:" -ForegroundColor White
        Write-Host "   docker load -i pdf-editor-uos-arm64.tar" -ForegroundColor Yellow
        Write-Host ""
    } else {
        throw "构建失败"
    }
} catch {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Red
    Write-Host "✗ Docker镜像构建失败！" -ForegroundColor Red
    Write-Host "==========================================" -ForegroundColor Red
    Write-Host "错误信息: $_" -ForegroundColor Red
    exit 1
}

# 询问是否立即导出镜像
Write-Host ""
$export = Read-Host "是否现在导出镜像文件? (Y/N)"
if ($export -eq 'Y' -or $export -eq 'y') {
    $outputFile = "pdf-editor-uos-arm64.tar"
    Write-Host "正在导出镜像到 $outputFile ..." -ForegroundColor Cyan
    docker save -o $outputFile $FullImageName
    if ($LASTEXITCODE -eq 0) {
        $fileSize = (Get-Item $outputFile).Length / 1MB
        Write-Host "✓ 镜像已导出: $outputFile (约 $([math]::Round($fileSize, 2)) MB)" -ForegroundColor Green
        Write-Host "可以将此文件传输到UOS系统进行部署" -ForegroundColor Yellow
    } else {
        Write-Host "✗ 镜像导出失败" -ForegroundColor Red
    }
}
