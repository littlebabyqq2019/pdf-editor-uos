#!/bin/bash
cat <<'WELCOME'
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║        PDF编辑工具集成版 - 安装成功                            ║
║                                                                ║
║        版本: 1.0.0                                              ║
║        架构: ARM64 (国产统信 UOS)                              ║
║                                                                ║
║════════════════════════════════════════════════════════════════╝

✅ 安装成功！

📍 应用已安装到: /opt/pdf-editor

🚀 启动应用:
   - 方式1 (桌面): 在应用菜单中找到"PDF编辑工具集成版"
   - 方式2 (命令行): /opt/pdf-editor/start_pdf_editor.sh
   - 方式3 (系统服务): systemctl status pdf-editor

🌐 访问方式:
   - 本机: http://localhost:5000
   - 局域网: http://$(hostname -I | awk '{print $1}'):5000

📚 功能说明:
   ✏️ PDF编辑器: 在线编辑、标注、绘图
   📄 PDF处理: 去红头、去公章、页面管理
   🖼️ 图片处理: 去背景、转PDF

⚙️ 配置:
   - 默认端口: 5000
   - 自定义端口: PORT=8080 /opt/pdf-editor/start_pdf_editor.sh
   - 开机自启: 已启用 (systemctl enable pdf-editor)

📖 查看日志:
   systemctl status pdf-editor
   systemctl logs pdf-editor -f

❓ 需要帮助?
   查看文档: /opt/pdf-editor/README.txt
   查看服务状态: sudo systemctl status pdf-editor

====================================================================

感谢使用 PDF编辑工具集成版！

WELCOME
