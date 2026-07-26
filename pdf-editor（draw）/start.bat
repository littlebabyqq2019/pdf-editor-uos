@echo off
chcp 65001 >nul
echo ====================================
echo PDF编辑器 - 启动脚本
echo ====================================
echo.

REM 检查虚拟环境是否存在
if not exist "venv\" (
    echo [步骤 1/3] 创建虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo 错误: 创建虚拟环境失败！请确保已安装Python 3.8或更高版本。
        pause
        exit /b 1
    )
    echo 虚拟环境创建成功！
    echo.
) else (
    echo [✓] 虚拟环境已存在
    echo.
)

REM 激活虚拟环境
echo [步骤 2/3] 激活虚拟环境...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo 错误: 激活虚拟环境失败！
    pause
    exit /b 1
)
echo 虚拟环境已激活！
echo.

REM 安装依赖
echo [步骤 3/3] 检查并安装依赖...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo 错误: 安装依赖失败！
    pause
    exit /b 1
)
echo 依赖安装完成！
echo.

REM 启动应用
echo ====================================
echo 正在启动PDF编辑器...
echo ====================================
echo.
python app.py

pause
