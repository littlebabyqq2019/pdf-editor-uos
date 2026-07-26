#!/bin/bash
set -euo pipefail

# 读取版本信息
if [ -f .version ]; then
  source .version
else
  VERSION="1.0.0"
  VERSION_DATE="$(date +%Y-%m-%d)"
  BUILD_NUMBER="1"
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET_DIR="/opt/pdf-editor"
DESKTOP_DIR="$HOME/.local/share/applications"
SERVICE_DIR="/etc/systemd/system"
PORT="${PORT:-5000}"

echo ""
echo "════════════════════════════════════════════════════"
echo "  PDF编辑工具集成版 UOS 版 安装程序"
echo "  版本: $VERSION"
echo "════════════════════════════════════════════════════"
echo ""

# 检查必要文件
if [ ! -f "$SCRIPT_DIR/bin/PDF编辑工具集成版" ]; then
  echo "❌ 错误: 未找到可执行文件 bin/PDF编辑工具集成版"
  exit 1
fi

echo "📦 安装中..."

sudo mkdir -p "$TARGET_DIR" "$DESKTOP_DIR" "$SERVICE_DIR"

# 安装可执行文件和脚本
sudo cp "$SCRIPT_DIR/bin/PDF编辑工具集成版" "$TARGET_DIR/"
sudo cp -r "$SCRIPT_DIR/desktop"/* "$TARGET_DIR/desktop/" || true
sudo cp -r "$SCRIPT_DIR/icons" "$TARGET_DIR/" 2>/dev/null || true

sudo chmod +x "$TARGET_DIR/PDF编辑工具集成版" \
  "$TARGET_DIR/desktop/start_pdf_editor.sh" \
  "$TARGET_DIR/desktop/run_with_port.sh" \
  "$TARGET_DIR/desktop/post_install.sh" 2>/dev/null || true

# 安装桌面快捷方式
sudo cp "$TARGET_DIR/desktop/pdf-editor.desktop" "$DESKTOP_DIR/"
sudo sed -i "s|Icon=.*|Icon=$TARGET_DIR/icons/pdf-editor.png|" "$DESKTOP_DIR/pdf-editor.desktop"

# 创建环境文件
sudo tee "$TARGET_DIR/pdf-editor.env" > /dev/null <<EOF
PORT=$PORT
VERSION=$VERSION
VERSION_DATE=$VERSION_DATE
BUILD_NUMBER=$BUILD_NUMBER
EOF

# 安装systemd服务
sudo cp "$TARGET_DIR/desktop/pdf-editor.service" "$SERVICE_DIR/"
sudo sed -i "s|^ExecStart=.*|ExecStart=$TARGET_DIR/desktop/run_with_port.sh $PORT|" "$SERVICE_DIR/pdf-editor.service"
sudo sed -i "s|^WorkingDirectory=.*|WorkingDirectory=$TARGET_DIR|" "$SERVICE_DIR/pdf-editor.service"

# 启用服务
sudo systemctl daemon-reload
sudo systemctl enable pdf-editor 2>/dev/null || true
sudo systemctl restart pdf-editor 2>/dev/null || true

echo "✅ 安装完成！"
echo ""

# 显示欢迎页
if [ -x "$TARGET_DIR/desktop/post_install.sh" ]; then
  bash "$TARGET_DIR/desktop/post_install.sh"
fi

echo ""
echo "📖 下一步:"
echo "   1. 在应用菜单找到'PDF编辑工具集成版'启动"
echo "   2. 或在浏览器打开: http://localhost:$PORT"
echo ""
