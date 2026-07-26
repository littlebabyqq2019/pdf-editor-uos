#!/bin/bash
# PDF编辑工具 - 统信系统ARM64架构部署脚本

echo "========================================"
echo "PDF编辑工具 - Docker容器部署 (ARM64)"
echo "========================================"
echo ""
echo "目标系统: 统信UOS (ARM64/鲲鹏处理器)"
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
if [ ! -f "pdf-editor-image-arm64.tar" ]; then
    echo "[错误] 未找到镜像文件 pdf-editor-image-arm64.tar"
    echo "请确保 pdf-editor-image-arm64.tar 文件在当前目录"
    exit 1
fi

echo "[2/5] 加载Docker镜像 (ARM64架构)..."
sudo docker load -i pdf-editor-image-arm64.tar
if [ $? -ne 0 ]; then
    echo "[错误] 镜像加载失败"
    exit 1
fi
echo "[✓] 镜像加载成功"
echo ""

echo "[3/5] 验证镜像架构..."
IMAGE_ARCH=$(sudo docker inspect pdf-editor:arm64 2>/dev/null | grep -A 1 "Architecture" | grep -v "Architecture" | tr -d ' ,"')
SYSTEM_ARCH=$(uname -m)
echo "系统架构: $SYSTEM_ARCH"
echo "镜像架构: $IMAGE_ARCH"

if [ "$IMAGE_ARCH" = "arm64" ] && ([ "$SYSTEM_ARCH" = "aarch64" ] || [ "$SYSTEM_ARCH" = "arm64" ]); then
    echo "[✓] 架构匹配！"
else
    echo "[警告] 架构可能不匹配，但仍将尝试部署"
fi
echo ""

echo "[4/5] 停止并删除旧容器（如果存在）..."
sudo docker stop pdf-editor 2>/dev/null
sudo docker rm pdf-editor 2>/dev/null
echo "[✓] 清理完成"
echo ""

echo "[5/5] 启动容器..."
# 创建数据目录
mkdir -p ~/pdf-editor/processed

# 运行容器（配置自动重启策略）
sudo docker run -d \
  --name pdf-editor \
  -p 5000:5000 \
  -v ~/pdf-editor/processed:/app/processed \
  -e TZ=Asia/Shanghai \
  --restart unless-stopped \
  pdf-editor:arm64

if [ $? -ne 0 ]; then
    echo "[错误] 容器启动失败"
    exit 1
fi
echo "[✓] 容器启动成功"
echo ""

# 等待服务启动
echo "等待服务启动..."
sleep 5

# 检查容器状态
if sudo docker ps | grep -q pdf-editor; then
    echo "[✓] 容器运行正常"
    echo ""
    
    # 验证开机自启配置
    if sudo systemctl is-enabled docker &>/dev/null; then
        echo "[✓] Docker服务已配置开机自启"
    fi
    
    restart_policy=$(sudo docker inspect --format='{{.HostConfig.RestartPolicy.Name}}' pdf-editor 2>/dev/null)
    if [ "$restart_policy" = "unless-stopped" ]; then
        echo "[✓] 容器已配置自动重启策略"
    fi
    echo ""
    
    echo "========================================"
    echo "部署完成！"
    echo "========================================"
    echo ""
    echo "✓ Docker服务已配置开机自启"
    echo "✓ 容器已配置自动重启（系统重启后自动运行）"
    echo "✓ 架构: ARM64 (适配华为鲲鹏处理器)"
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
    
    # 测试访问
    echo "正在测试服务..."
    sleep 3
    if curl -s http://localhost:5000 > /dev/null; then
        echo "[✓] 服务访问正常"
    else
        echo "[注意] 服务可能还在启动中，请稍后再试"
    fi
    echo ""
else
    echo "[错误] 容器未能正常运行"
    echo "查看日志: sudo docker logs pdf-editor"
    exit 1
fi

