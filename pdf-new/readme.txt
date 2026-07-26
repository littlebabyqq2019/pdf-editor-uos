在虚拟环境中运行程序，按以下步骤操作（PowerShell 7）：

打开 PowerShell，进入项目目录： cd e:\dev\pdf-new0.2\pdf-new
激活虚拟环境： .\pdf_editor_env\Scripts\Activate.ps1 若提示执行策略限制，可先执行： Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass 然后再激活： .\pdf_editor_env\Scripts\Activate.ps1
安装依赖（已装可跳过）： python -m pip install -U pip pip install -r requirements.txt
启动程序： .venv\Scripts\python.exe app.py
快捷方式（已包含自动激活）：在 PowerShell 中运行
.\run.bat