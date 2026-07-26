@echo off
chcp 65001 >nul
echo ============================================================
echo PDF编辑工具集成版 v2.0 - 启动脚本
echo ============================================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Python，请先安装Python 3.8或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [信息] Python环境检测通过
echo.

REM 检查是否需要安装依赖
if not exist "venv" (
    echo [信息] 首次运行，正在安装依赖...
    echo.
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [错误] 依赖安装失败，请检查网络连接
        pause
        exit /b 1
    )
    echo.
    echo [信息] 依赖安装完成
    echo.
)

REM 启动应用
echo [信息] 正在启动PDF编辑工具集成版...
echo.
python app.py

pause
