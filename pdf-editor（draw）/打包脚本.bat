@echo off
chcp 65001 >nul
echo ========================================
echo PDF编辑器 v1.0 - 打包脚本
echo ========================================
echo.

echo [1/4] 检查虚拟环境...
if not exist "venv\Scripts\activate.bat" (
    echo ❌ 错误：未找到虚拟环境
    echo 请先创建虚拟环境：python -m venv venv
    pause
    exit /b 1
)

echo [2/4] 激活虚拟环境...
call venv\Scripts\activate.bat

echo [3/4] 安装PyInstaller（如果未安装）...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo 正在安装PyInstaller...
    pip install pyinstaller
)

echo [4/4] 开始打包应用...
echo.
echo 配置信息：
echo - 版本：1.0
echo - 端口：5002
echo - 控制台：隐藏
echo - 包含：static、templates
echo.

pyinstaller --clean "PDF编辑器.spec"

echo.
if exist "dist\PDF编辑器.exe" (
    echo ========================================
    echo ✅ 打包成功！
    echo ========================================
    echo.
    echo 📦 可执行文件位置：
    echo    dist\PDF编辑器.exe
    echo.
    echo 💡 使用说明：
    echo    1. 双击运行 PDF编辑器.exe
    echo    2. 浏览器访问 http://localhost:5002
    echo    3. 开始使用
    echo.
    echo 📂 可以将整个 dist 文件夹分发给用户
    echo ========================================
) else (
    echo ========================================
    echo ❌ 打包失败！
    echo ========================================
    echo 请检查错误信息
)

echo.
pause
