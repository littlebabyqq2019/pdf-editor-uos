# 重新构建精简版Docker镜像
# 预计大小：500-600MB（比当前的1.32GB小60%）

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "  重新构建精简版Docker镜像" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# 添加Docker到PATH
$env:PATH += ";C:\Program Files\Docker\Docker\resources\bin"

# 检查Docker
Write-Host "检查Docker状态..." -ForegroundColor Yellow
try {
    docker info | Out-Null
    Write-Host "✓ Docker运行正常" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker未运行，请先启动Docker Desktop" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "当前镜像大小对比：" -ForegroundColor Cyan
docker images pdf-editor-uos

Write-Host ""
Write-Host "----------------------------------------" -ForegroundColor Yellow
Write-Host "即将构建的优化版本特点：" -ForegroundColor Cyan
Write-Host "  • 只复制必要文件（不用COPY . /app/）" -ForegroundColor White
Write-Host "  • 添加Python缓存清理" -ForegroundColor White
Write-Host "  • 改进的.dockerignore" -ForegroundColor White
Write-Host "  • 预计大小：500-600MB" -ForegroundColor Green
Write-Host "  • 比当前版本小：700-800MB (60%)" -ForegroundColor Green
Write-Host "----------------------------------------" -ForegroundColor Yellow
Write-Host ""

# 询问是否继续
$continue = Read-Host "是否继续构建？(y/n)"
if ($continue -ne 'y' -and $continue -ne 'Y') {
    Write-Host "已取消" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "开始构建精简版镜像..." -ForegroundColor Cyan
Write-Host "镜像标签: pdf-editor-uos:lean" -ForegroundColor Yellow
Write-Host "Dockerfile: Dockerfile.lean" -ForegroundColor Yellow
Write-Host "平台: linux/arm64" -ForegroundColor Yellow
Write-Host ""
Write-Host "⏰ 预计需要50-60分钟（arm64模拟构建）" -ForegroundColor Magenta
Write-Host ""

$startTime = Get-Date

# 构建镜像
docker build -f Dockerfile.lean --platform linux/arm64 -t pdf-editor-uos:lean .

if ($LASTEXITCODE -eq 0) {
    $endTime = Get-Date
    $duration = $endTime - $startTime
    
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "✓ 构建成功！" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "构建耗时: $($duration.TotalMinutes.ToString('0.0'))分钟" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "镜像大小对比：" -ForegroundColor Cyan
    docker images | Select-String "pdf-editor-uos"
    
    Write-Host ""
    Write-Host "----------------------------------------" -ForegroundColor Yellow
    Write-Host "下一步操作：" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. 导出镜像：" -ForegroundColor White
    Write-Host "   docker save -o pdf-editor-uos-lean-arm64.tar pdf-editor-uos:lean" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. 压缩镜像（可选）：" -ForegroundColor White
    Write-Host "   gzip pdf-editor-uos-lean-arm64.tar" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. 测试镜像：" -ForegroundColor White
    Write-Host "   docker run -d -p 5000:5000 pdf-editor-uos:lean" -ForegroundColor Gray
    Write-Host "----------------------------------------" -ForegroundColor Yellow
    Write-Host ""
    
    # 询问是否导出
    $export = Read-Host "是否立即导出镜像？(y/n)"
    if ($export -eq 'y' -or $export -eq 'Y') {
        Write-Host ""
        Write-Host "正在导出镜像..." -ForegroundColor Cyan
        docker save -o pdf-editor-uos-lean-arm64.tar pdf-editor-uos:lean
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ 导出成功！" -ForegroundColor Green
            $tarFile = Get-Item "pdf-editor-uos-lean-arm64.tar"
            $sizeMB = [math]::Round($tarFile.Length / 1MB, 2)
            Write-Host "文件: $($tarFile.Name)" -ForegroundColor White
            Write-Host "大小: $sizeMB MB" -ForegroundColor White
            
            # 对比原始文件
            if (Test-Path "pdf-editor-uos-arm64.tar") {
                $oldFile = Get-Item "pdf-editor-uos-arm64.tar"
                $oldSizeMB = [math]::Round($oldFile.Length / 1MB, 2)
                $saved = $oldSizeMB - $sizeMB
                $percent = [math]::Round(($saved / $oldSizeMB) * 100, 1)
                
                Write-Host ""
                Write-Host "大小对比：" -ForegroundColor Cyan
                Write-Host "  原始版本: $oldSizeMB MB" -ForegroundColor White
                Write-Host "  精简版本: $sizeMB MB" -ForegroundColor Green
                Write-Host "  节省空间: $saved MB ($percent%)" -ForegroundColor Green
            }
        } else {
            Write-Host "✗ 导出失败" -ForegroundColor Red
        }
    }
    
} else {
    Write-Host ""
    Write-Host "✗ 构建失败" -ForegroundColor Red
    Write-Host "请检查错误信息" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "完成！" -ForegroundColor Green
