@echo off
chcp 65001 >nul
echo ======================================
echo PDF编辑工具 - ARM64架构镜像构建脚本
echo ======================================
echo.
echo [重要] 这个脚本将构建ARM64架构的镜像
echo        适用于ARM架构的统信系统（aarch64）
echo.
echo 如果您的统信系统架构是 x86_64，请使用 docker-build.bat
echo.
pause

echo [1/4] 检查Docker环境...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] Docker未运行或未安装
    echo 请确保Docker Desktop已启动
    pause
    exit /b 1
)
echo [✓] Docker环境正常
echo.

echo [2/4] 清理旧镜像（如果存在）...
docker rmi pdf-editor:latest >nul 2>&1
echo [✓] 清理完成
echo.

echo [3/4] 构建ARM64架构镜像（适用于ARM统信系统）...
echo 提示: 跨架构构建需要较长时间（可能30分钟-1小时）
echo       请耐心等待...
echo.

docker build --platform linux/arm64 -t pdf-editor:latest .
if %errorlevel% neq 0 (
    echo [错误] 镜像构建失败
    pause
    exit /b 1
)
echo [✓] 镜像构建成功
echo.

echo [4/4] 导出ARM64镜像文件...
docker save -o pdf-editor-image-arm64.tar pdf-editor:latest
if %errorlevel% neq 0 (
    echo [错误] 镜像导出失败
    pause
    exit /b 1
)
echo [✓] 镜像已导出为: pdf-editor-image-arm64.tar
echo.

echo ======================================
echo 构建完成！
echo ======================================
echo.
echo 镜像信息:
docker images pdf-editor:latest
echo.
echo 导出文件: pdf-editor-image-arm64.tar
for %%I in (pdf-editor-image-arm64.tar) do echo 文件大小: %%~zI 字节
echo.
echo 下一步操作:
echo 1. 将 pdf-editor-image-arm64.tar 传输到统信系统
echo 2. 在统信系统上运行:
echo    docker stop pdf-editor 2^>^&1
echo    docker rm pdf-editor 2^>^&1
echo    docker rmi pdf-editor:latest 2^>^&1
echo    docker load -i pdf-editor-image-arm64.tar
echo 3. 运行容器:
echo    docker run -d --name pdf-editor -p 5000:5000 \
echo      -v ~/pdf-editor/processed:/app/processed \
echo      -e TZ=Asia/Shanghai --restart unless-stopped pdf-editor:latest
echo 4. 访问: http://localhost:5000
echo.
pause

