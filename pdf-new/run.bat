@echo off
echo 启动PDF文件编辑软件...
echo.

REM 检查是否在虚拟环境中
if not defined VIRTUAL_ENV (
    echo 正在激活虚拟环境...
    if exist pdf_editor_env\Scripts\activate.bat (
        call pdf_editor_env\Scripts\activate.bat
    ) else (
        echo 虚拟环境不存在，请先运行 setup.bat 创建虚拟环境
        pause
        exit /b 1
    )
)

echo 启动Web服务器...
echo 应用将在 http://localhost:5000 启动
echo 局域网用户可通过您的IP地址访问
echo 按 Ctrl+C 停止服务器
echo.

python app.py

pause