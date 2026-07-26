#!/bin/bash
set -euo pipefail

TARGET_DIR="/opt/pdf-editor"
DESKTOP_DIR="$HOME/.local/share/applications"
mkdir -p "$TARGET_DIR" "$DESKTOP_DIR"

cp -r "$(cd "$(dirname "$0")" && pwd)"/* "$TARGET_DIR"/
chmod +x "$TARGET_DIR"/PDF编辑工具集成版 "$TARGET_DIR"/start_pdf_editor.sh
cp "$TARGET_DIR"/pdf-editor.desktop "$DESKTOP_DIR"/

cat <<'EOF'
安装完成。
请在应用菜单中查找“PDF编辑工具集成版”。
EOF
