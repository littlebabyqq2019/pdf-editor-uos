#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

# 读取版本信息
if [ -f .version ]; then
  source .version
else
  VERSION="${1:-1.0.0}"
  VERSION_DATE="$(date +%Y-%m-%d)"
  BUILD_NUMBER="1"
fi

VERSION="${1:-$VERSION}"
RELEASE_NAME="PDF编辑工具-UOS-arm64-v$VERSION"
PKG_DIR="$ROOT_DIR/dist/$RELEASE_NAME"
ARTIFACT_PATH="$ROOT_DIR/dist/$RELEASE_NAME.tar.gz"

rm -rf "$PKG_DIR" "$ARTIFACT_PATH"
mkdir -p "$PKG_DIR"/{bin,desktop,icons,docs}

if [ -f dist/linux-arm64/PDF编辑工具集成版 ]; then
  cp dist/linux-arm64/PDF编辑工具集成版 "$PKG_DIR/bin/"
else
  echo "未找到可执行文件 dist/linux-arm64/PDF编辑工具集成版" >&2
  exit 1
fi

cp -r desktop/* "$PKG_DIR/desktop/" 2>/dev/null || true
cp -r desktop/icons/* "$PKG_DIR/icons/" 2>/dev/null || true
cp CHANGELOG_UOS.md "$PKG_DIR/docs/CHANGELOG.md" 2>/dev/null || true

cat > "$PKG_DIR/README.md" <<'EOF'
# PDF编辑工具集成版 - UOS 版

## 版本信息
- **应用名**: PDF编辑工具集成版
- **版本**: 1.0.0
- **架构**: ARM64
- **目标系统**: 统信 UOS v20.04+

## 快速安装

### 方式1: 一键安装 (推荐)
```bash
cd PDF编辑工具-UOS-arm64-v1.0.0
chmod +x ./desktop/install_uos_final.sh
./desktop/install_uos_final.sh
```

### 方式2: 手动安装
```bash
chmod +x ./bin/PDF编辑工具集成版
./desktop/start_pdf_editor.sh
```

## 功能特性

- ✏️ **PDF编辑**: 在线编辑、标注、绘图、撤销/重做
- 📄 **PDF处理**: 去红头、去公章、页面管理、合并拆分
- 🖼️ **图片处理**: 去背景、图片转PDF、批量处理
- 🌐 **Web应用**: 无需安装依赖，浏览器直接使用

## 使用说明

### 启动应用
- **桌面模式**: 在应用菜单搜索"PDF编辑工具集成版"
- **命令行**: `/opt/pdf-editor/start_pdf_editor.sh`
- **自定义端口**: `PORT=8080 /opt/pdf-editor/start_pdf_editor.sh`

### 访问应用
- 本机: http://localhost:5000
- 局域网: http://192.168.x.x:5000
- PDF编辑器: http://localhost:5000/editor

### 开机自启
安装脚本已自动配置，无需额外设置。

## 系统要求
- 统信 UOS v20.04 或更高版本
- ARM64 架构
- 2GB 以上内存
- 50MB 磁盘空间

## 支持和反馈
如有问题，请查看 docs/CHANGELOG.md 或联系开发者。

EOF

cat > "$PKG_DIR/INSTALL.txt" <<'EOF'
PDF编辑工具集成版 UOS 版安装指南

快速安装步骤:
================================

1. 进入解压目录:
   cd PDF编辑工具-UOS-arm64-v1.0.0

2. 运行一键安装脚本:
   chmod +x ./desktop/install_uos_final.sh
   ./desktop/install_uos_final.sh

3. 根据提示完成安装

4. 启动应用:
   - 在应用菜单找到 "PDF编辑工具集成版"
   - 或命令行执行: /opt/pdf-editor/start_pdf_editor.sh

访问方式:
   http://localhost:5000

注意:
- 首次启动可能需要几秒钟
- 默认端口为 5000
- 需要 sudo 权限进行系统级安装

卸载方法:
   sudo rm -rf /opt/pdf-editor
   sudo systemctl disable pdf-editor
   rm ~/.local/share/applications/pdf-editor.desktop

EOF

chmod +x "$PKG_DIR/bin/PDF编辑工具集成版" \
  "$PKG_DIR/desktop/start_pdf_editor.sh" \
  "$PKG_DIR/desktop/install_uos_final.sh" \
  "$PKG_DIR/desktop/post_install.sh" 2>/dev/null || true

tar -czf "$ARTIFACT_PATH" -C "$ROOT_DIR/dist" "$RELEASE_NAME"

echo ""
echo "✅ 已生成发布包: $ARTIFACT_PATH"
echo "   名称: $RELEASE_NAME"
echo "   大小: $(du -h "$ARTIFACT_PATH" | cut -f1)"
echo ""
