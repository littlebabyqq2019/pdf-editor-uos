@echo off
chcp 65001 >nul
echo ====================================
echo PDF编辑器 - 测试脚本
echo ====================================
echo.

echo [测试 1/4] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未检测到Python环境
    echo    请先安装Python 3.8或更高版本
    goto :end
) else (
    python --version
    echo ✓ Python环境正常
)
echo.

echo [测试 2/4] 检查虚拟环境...
if exist "venv\" (
    echo ✓ 虚拟环境已创建
) else (
    echo ❌ 虚拟环境未创建
    echo    运行 start.bat 将自动创建虚拟环境
)
echo.

echo [测试 3/4] 检查项目文件...
set MISSING_FILES=0

if not exist "app.py" (
    echo ❌ 缺少文件: app.py
    set MISSING_FILES=1
)
if not exist "requirements.txt" (
    echo ❌ 缺少文件: requirements.txt
    set MISSING_FILES=1
)
if not exist "templates\index.html" (
    echo ❌ 缺少文件: templates\index.html
    set MISSING_FILES=1
)
if not exist "static\css\style.css" (
    echo ❌ 缺少文件: static\css\style.css
    set MISSING_FILES=1
)
if not exist "static\js\app.js" (
    echo ❌ 缺少文件: static\js\app.js
    set MISSING_FILES=1
)

if %MISSING_FILES%==0 (
    echo ✓ 所有必需文件完整
) else (
    echo ⚠ 部分文件缺失，可能影响运行
)
echo.

echo [测试 4/4] 检查网络端口...
netstat -an | find ":5000" >nul 2>&1
if errorlevel 1 (
    echo ✓ 端口5000可用
) else (
    echo ⚠ 端口5000已被占用
    echo    请关闭占用该端口的程序或修改app.py中的端口号
)
echo.

echo ====================================
echo 测试完成！
echo ====================================
echo.
echo 如果所有测试都通过，您可以运行 start.bat 启动应用
echo.

:end
pause
