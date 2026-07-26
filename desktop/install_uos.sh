#!/bin/bash
set -euo pipefail

TARGET_DIR="/opt/pdf-editor"
DESKTOP_DIR="$HOME/.local/share/applications"
SERVICE_DIR="/etc/systemd/system"
PORT="${PORT:-5000}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

sudo mkdir -p "$TARGET_DIR" "$DESKTOP_DIR" "$SERVICE_DIR"
sudo cp -r "$SCRIPT_DIR"/* "$TARGET_DIR"/
sudo chmod +x "$TARGET_DIR"/PDF编辑工具集成版 "$TARGET_DIR"/start_pdf_editor.sh "$TARGET_DIR"/run_with_port.sh "$TARGET_DIR"/install_uos.sh
sudo cp "$TARGET_DIR"/pdf-editor.desktop "$DESKTOP_DIR"/

cat > "$TARGET_DIR"/pdf-editor.env <<EOF
PORT=$PORT
EOF

sudo cp "$TARGET_DIR"/pdf-editor.service "$SERVICE_DIR"/pdf-editor.service
sudo sed -i "s|^ExecStart=.*|ExecStart=/opt/pdf-editor/run_with_port.sh ${PORT}|" "$SERVICE_DIR"/pdf-editor.service
sudo systemctl daemon-reload
sudo systemctl enable --now pdf-editor >/dev/null 2>&1 || true

cat <<EOF
安装完成。
- 可执行文件: /opt/pdf-editor/PDF编辑工具集成版
- 启动脚本: /opt/pdf-editor/start_pdf_editor.sh
- 桌面快捷方式: ~/.local/share/applications/pdf-editor.desktop
- 服务已尝试启用: systemctl enable --now pdf-editor
- 默认端口: ${PORT}
EOF
