1. 将整个目录复制到 UOS 机器的 /opt/pdf-editor/
2. 运行：
   chmod +x /opt/pdf-editor/PDF编辑工具集成版
   chmod +x /opt/pdf-editor/start_pdf_editor.sh
   chmod +x /opt/pdf-editor/install_uos.sh
3. 双击桌面启动脚本 start_pdf_editor.sh，或运行安装脚本完成桌面快捷方式安装。
4. 安装脚本将自动完成：
   - 复制到 /opt/pdf-editor
   - 生成桌面快捷方式
   - 配置 systemd 自启动
   - 设置默认端口（可由 PORT 环境变量覆盖）
5. 如需手动开机自启：
   sudo cp /opt/pdf-editor/pdf-editor.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable --now pdf-editor
