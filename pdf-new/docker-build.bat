@echo off
chcp 65001 >nul
echo ======================================
echo PDF编辑工具 - Docker镜像构建脚本
echo ======================================
echo.

echo [1/3] 检查Docker环境...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] Docker未运行或未安装
    echo 请确保Docker Desktop已启动
    pause
    exit /b 1
)
echo [✓] Docker环境正常
echo.

echo [2/3] 构建Linux/AMD64镜像（适用于统信系统）...
echo 提示: 这将构建适用于x86_64 Linux系统的镜像
docker build --platform linux/amd64 -t pdf-editor:latest .
if %errorlevel% neq 0 (
    echo [错误] 镜像构建失败
    pause
    exit /b 1
)
echo [✓] 镜像构建成功
echo.

echo [3/3] 导出镜像文件...
docker save -o pdf-editor-image.tar pdf-editor:latest
if %errorlevel% neq 0 (
    echo [错误] 镜像导出失败
    pause
    exit /b 1
)
echo [✓] 镜像已导出为: pdf-editor-image.tar
echo.

echo ======================================
echo 构建完成！
echo ======================================
echo.
echo 镜像信息:
docker images pdf-editor:latest
echo.
echo 导出文件: pdf-editor-image.tar
for %%I in (pdf-editor-image.tar) do echo 文件大小: %%~zI 字节
echo.
echo 下一步操作:
echo 1. 将 pdf-editor-image.tar 传输到统信系统电脑
echo 2. 在统信系统上运行: docker load -i pdf-editor-image.tar
echo 3. 运行容器: docker run -d -p 5000:5000 --name pdf-editor pdf-editor:latest
echo 4. 访问: http://localhost:5000
echo.
pause

