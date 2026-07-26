#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

mkdir -p dist/linux-arm64 artifacts
python3 desktop/generate_icon.py --png dist/linux-arm64/desktop/icons/pdf-editor.png --ico dist/linux-arm64/desktop/icons/pdf-editor.ico >/dev/null 2>&1 || true
cp -r desktop dist/linux-arm64/desktop

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 未安装" >&2
  exit 1
fi

python3 -m pip install --upgrade pip setuptools wheel pyinstaller >/dev/null
python3 -m pip install -r requirements.txt >/dev/null

python3 -m PyInstaller --clean --noconfirm --distpath dist/linux-arm64 --workpath build/pyinstaller-arm64 linux_arm64.spec
chmod +x dist/linux-arm64/PDF编辑工具集成版

if [ -f dist/linux-arm64/PDF编辑工具集成版 ]; then
  tar -czf artifacts/pdf-editor-linux-arm64.tar.gz -C dist/linux-arm64 PDF编辑工具集成版
else
  echo "未找到可执行文件" >&2
  exit 1
fi

echo "构建完成：artifacts/pdf-editor-linux-arm64.tar.gz"
