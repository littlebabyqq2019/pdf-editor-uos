@echo off
echo PDF文件编辑软件 - 安装脚本
echo ================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到Python，请先安装Python 3.7或更高版本
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)

echo 检测到Python版本：
python --version
echo.

REM 创建虚拟环境
echo 正在创建虚拟环境...
if exist pdf_editor_env (
    echo 虚拟环境已存在，跳过创建步骤
) else (
    python -m venv pdf_editor_env
    if errorlevel 1 (
        echo 创建虚拟环境失败
        pause
        exit /b 1
    )
    echo 虚拟环境创建成功
)
echo.

REM 激活虚拟环境
echo 正在激活虚拟环境...
call pdf_editor_env\Scripts\activate.bat
if errorlevel 1 (
    echo 激活虚拟环境失败
    pause
    exit /b 1
)
echo.

REM 升级pip
echo 正在升级pip...
python -m pip install --upgrade pip
echo.

REM 安装依赖包
echo 正在安装依赖包...
pip install -r requirements.txt
if errorlevel 1 (
    echo 安装依赖包失败，请检查网络连接
    pause
    exit /b 1
)
echo.

REM 创建必要的目录
echo 正在创建必要的目录...
if not exist uploads mkdir uploads
if not exist processed mkdir processed
if not exist templates mkdir templates
echo.

echo ================================
echo 安装完成！
echo.
echo 注意事项：
echo 1. 如果需要OCR功能，请安装Tesseract OCR
echo    下载地址：https://github.com/UB-Mannheim/tesseract/wiki
echo 2. 运行 run.bat 启动应用程序
echo 3. 应用将在 http://localhost:5000 启动
echo.
echo 按任意键退出...
pause