# UOS 桌面版使用说明

## 产物内容

构建完成后，压缩包中会包含：
- PDF编辑工具集成版（可执行文件）
- start_pdf_editor.sh（启动脚本）
- pdf-editor.desktop（桌面快捷方式）
- pdf-editor.service（systemd 服务配置）
- install_desktop.sh（安装脚本）
- icons/ 目录（图标资源）

## 在 UOS 上使用

### 方式 1：直接双击运行
1. 将压缩包解压到某个目录，例如：
   ```bash
   mkdir -p ~/pdf-editor
   tar -xzf pdf-editor-linux-arm64.tar.gz -C ~/pdf-editor
   ```
2. 进入目录后执行：
   ```bash
   chmod +x ~/pdf-editor/PDF编辑工具集成版
   chmod +x ~/pdf-editor/start_pdf_editor.sh
   ```
3. 双击 `start_pdf_editor.sh` 即可启动。

### 方式 2：安装到系统应用菜单
```bash
chmod +x ~/pdf-editor/install_desktop.sh
~/pdf-editor/install_desktop.sh
```

### 方式 3：开机自启
```bash
sudo cp ~/pdf-editor/pdf-editor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now pdf-editor
```

## 说明

- 程序默认监听 5000 端口。
- 浏览器访问：
  - http://localhost:5000
  - http://[UOSIP]:5000
