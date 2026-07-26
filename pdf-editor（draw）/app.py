"""
PDF编辑器 - Flask后端应用
提供静态文件服务和HTML页面渲染
版本：1.2
"""

from flask import Flask, render_template, send_from_directory
import os

# 版本信息
VERSION = "1.2"
APP_NAME = "PDF编辑器"

app = Flask(__name__)

# 配置
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 最大上传100MB
app.config['SECRET_KEY'] = 'pdf-editor-secret-key-2024'

@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')

@app.route('/static/<path:path>')
def send_static(path):
    """提供静态文件"""
    return send_from_directory('static', path)

@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return '页面未找到', 404

@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    return '服务器内部错误', 500

if __name__ == '__main__':
    # 配置端口
    PORT = 5002
    
    # 获取本机IP地址
    import socket
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    print("\n" + "="*60)
    print(f"🚀 {APP_NAME} v{VERSION} 启动成功！")
    print("="*60)
    print(f"📍 本机访问: http://localhost:{PORT}")
    print(f"📍 本机访问: http://127.0.0.1:{PORT}")
    print(f"🌐 局域网访问: http://{local_ip}:{PORT}")
    print("="*60)
    print("💡 按 Ctrl+C 停止服务器")
    print("="*60 + "\n")
    
    # 检测是否为打包后的exe运行
    import sys
    is_frozen = getattr(sys, 'frozen', False)
    
    # 如果是打包后的exe，自动打开浏览器
    if is_frozen:
        import webbrowser
        import threading
        
        def open_browser():
            import time
            time.sleep(1.5)  # 等待服务器启动
            webbrowser.open(f'http://localhost:{PORT}')
        
        threading.Thread(target=open_browser, daemon=True).start()
    
    # 启动Flask服务器
    app.run(
        host='0.0.0.0',  # 允许外部访问
        port=PORT,
        debug=False if is_frozen else True,  # 打包后禁用debug
        use_reloader=False if is_frozen else True  # 打包后禁用reloader
    )
