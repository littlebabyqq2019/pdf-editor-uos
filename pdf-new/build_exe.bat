@echo off
chcp 65001 >nul
echo ========================================
echo PDF编辑工具 - 打包为EXE
echo 版本: 1.5.1
echo ========================================
echo.

echo [1/5] 检查Python环境...
python --version
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python
    pause
    exit /b 1
)
echo.

echo [2/5] 创建图标文件...
python create_icon.py
if errorlevel 1 (
    echo [错误] 图标创建失败
    pause
    exit /b 1
)
echo.

echo [3/5] 创建版本信息...
python create_version_info.py
if errorlevel 1 (
    echo [错误] 版本信息创建失败
    pause
    exit /b 1
)
echo.

echo [4/5] 检查虚拟环境...
python -c "import sys; print('Python路径:', sys.executable)"
python -c "import flask, cv2, fitz, skimage; print('依赖检查: OK')"
if errorlevel 1 (
    echo [错误] 缺少必要的依赖包，请先运行: pip install -r requirements.txt
    pause
    exit /b 1
)
echo.

echo [5/5] 开始打包（使用当前环境的依赖）...
echo 这可能需要几分钟时间，请耐心等待...
pyinstaller --clean pdf-editor.spec
if errorlevel 1 (
    echo [错误] 打包失败，请检查错误信息
    pause
    exit /b 1
)
echo.

echo ========================================
echo 打包完成！
echo ========================================
echo.
echo 生成的文件位置：
echo   dist\PDF编辑工具\    （程序文件夹）
echo.
echo 文件夹大小：
dir "dist\PDF编辑工具" | find "个文件"
echo.
echo 使用说明：
echo 1. 进入 dist\PDF编辑工具 文件夹
echo 2. 双击运行 PDF编辑工具.exe
echo 3. 会弹出控制台窗口，显示启动信息（1-2秒启动）
echo 4. 打开浏览器，访问 http://localhost:5000
echo 5. 保持控制台窗口运行（关闭窗口会终止服务）
echo 6. 分发时需要复制整个文件夹（包含_internal文件夹）
echo.
pause

