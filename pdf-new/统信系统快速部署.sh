#!/bin/bash
# PDF编辑工具 - 统信系统快速部署脚本

echo "========================================"
echo "PDF编辑工具 - Docker容器部署"
echo "========================================"
echo ""

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "[错误] Docker未安装或未找到"
    echo "请先安装Docker: sudo apt install docker.io"
    exit 1
fi

echo "[1/5] 检查Docker服务状态..."
if ! sudo systemctl is-active --quiet docker; then
    echo "Docker服务未运行，正在启动..."
    sudo systemctl start docker
fi

# 设置Docker服务开机自启
echo "配置Docker服务开机自启..."
sudo systemctl enable docker
echo "[✓] Docker服务正常并已设置开机自启"
echo ""

# 检查镜像文件是否存在
if [ ! -f "pdf-editor-image.tar" ]; then
    echo "[错误] 未找到镜像文件 pdf-editor-image.tar"
    echo "请确保 pdf-editor-image.tar 文件在当前目录"
    exit 1
fi

echo "[2/5] 加载Docker镜像..."
sudo docker load -i pdf-editor-image.tar
if [ $? -ne 0 ]; then
    echo "[错误] 镜像加载失败"
    exit 1
fi
echo "[✓] 镜像加载成功"
echo ""

echo "[3/5] 停止并删除旧容器（如果存在）..."
sudo docker stop pdf-editor 2>/dev/null
sudo docker rm pdf-editor 2>/dev/null
echo "[✓] 清理完成"
echo ""

echo "[4/5] 启动容器..."
# 创建数据目录
mkdir -p ~/pdf-editor/processed

# 运行容器（配置自动重启策略）
sudo docker run -d \
  --name pdf-editor \
  -p 5000:5000 \
  -v ~/pdf-editor/processed:/app/processed \
  -e TZ=Asia/Shanghai \
  --restart unless-stopped \
  pdf-editor:latest

if [ $? -ne 0 ]; then
    echo "[错误] 容器启动失败"
    exit 1
fi
echo "[✓] 容器启动成功"
echo ""

# 等待服务启动
echo "等待服务启动..."
sleep 3

# 检查容器状态
if sudo docker ps | grep -q pdf-editor; then
    echo "[✓] 容器运行正常"
    echo ""
    
    echo "[5/5] 验证开机自启配置..."
    # 检查Docker服务自启状态
    if sudo systemctl is-enabled docker &>/dev/null; then
        echo "[✓] Docker服务已配置开机自启"
    else
        echo "[警告] Docker服务未配置开机自启"
    fi
    
    # 检查容器重启策略
    restart_policy=$(sudo docker inspect --format='{{.HostConfig.RestartPolicy.Name}}' pdf-editor 2>/dev/null)
    if [ "$restart_policy" = "unless-stopped" ]; then
        echo "[✓] 容器已配置自动重启策略"
    else
        echo "[警告] 容器重启策略: $restart_policy"
    fi
    echo ""
    
    echo "========================================"
    echo "部署完成！"
    echo "========================================"
    echo ""
    echo "✓ Docker服务已配置开机自启"
    echo "✓ 容器已配置自动重启（系统重启后自动运行）"
    echo ""
    echo "访问地址："
    echo "  本机访问: http://localhost:5000"
    echo "  局域网访问: http://$(hostname -I | awk '{print $1}'):5000"
    echo ""
    echo "常用命令："
    echo "  查看日志: sudo docker logs pdf-editor"
    echo "  停止服务: sudo docker stop pdf-editor"
    echo "  启动服务: sudo docker start pdf-editor"
    echo "  重启服务: sudo docker restart pdf-editor"
    echo "  删除容器: sudo docker rm -f pdf-editor"
    echo ""
    echo "数据目录: ~/pdf-editor/processed"
    echo ""
    echo "💡 提示："
    echo "  系统重启后，PDF编辑工具会自动启动"
    echo "  可以通过 'sudo docker ps' 查看容器运行状态"
    echo ""
else
    echo "[错误] 容器未能正常运行"
    echo "查看日志: sudo docker logs pdf-editor"
    exit 1
fi

