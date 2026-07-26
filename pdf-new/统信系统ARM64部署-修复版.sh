#!/bin/bash
# PDF编辑工具 - 统信系统ARM64架构部署脚本（修复版）
# 修复: 添加seccomp安全策略放宽，解决pthread创建失败问题

echo "========================================"
echo "PDF编辑工具 - Docker容器部署 (ARM64 修复版)"
echo "========================================"
echo ""
echo "目标系统: 统信UOS (ARM64/鲲鹏处理器)"
echo "版本: v1.5 - 修复OpenBLAS线程问题"
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

echo "[5/5] 启动容器（带安全策略修复）..."
# 创建数据目录
mkdir -p ~/pdf-editor/processed

echo ""
echo "📌 重要修复:"
echo "   添加 --security-opt seccomp=unconfined"
echo "   解决 OpenBLAS pthread_create 权限问题"
echo "   添加 OPENBLAS_NUM_THREADS=1 环境变量"
echo ""

# 运行容器（添加安全策略放宽和环境变量）
sudo docker run -d \
  --name pdf-editor \
  -p 5000:5000 \
  -v ~/pdf-editor/processed:/app/processed \
  -e TZ=Asia/Shanghai \
  -e OPENBLAS_NUM_THREADS=1 \
  --security-opt seccomp=unconfined \
  --restart unless-stopped \
  pdf-editor:arm64

if [ $? -ne 0 ]; then
    echo "[错误] 容器启动失败"
    exit 1
fi
echo "[✓] 容器启动成功"
echo ""

# 等待服务启动
echo "等待服务启动（约30秒）..."
for i in {1..30}; do
    sleep 1
    if sudo docker logs pdf-editor 2>&1 | grep -q "PDF编辑工具"; then
        echo "[✓] 应用已启动！"
        break
    fi
    echo -n "."
done
echo ""

# 检查容器状态
if sudo docker ps | grep -q pdf-editor; then
    echo "[✓] 容器运行正常"
    echo ""
    
    # 检查是否有错误
    if sudo docker logs pdf-editor 2>&1 | grep -q "pthread_create failed"; then
        echo "[警告] 仍有OpenBLAS警告，但应用应该能正常运行"
        echo "        这些警告可以忽略"
    fi
    
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
    echo "✓ 安全策略: 已优化以支持numpy/OpenBLAS"
    echo ""
    echo "访问地址："
    echo "  本机访问: http://localhost:5000"
    echo "  局域网访问: http://$(hostname -I | awk '{print $1}'):5000"
    echo ""
    echo "常用命令："
    echo "  查看日志: sudo docker logs pdf-editor"
    echo "  实时日志: sudo docker logs -f pdf-editor"
    echo "  停止服务: sudo docker stop pdf-editor"
    echo "  启动服务: sudo docker start pdf-editor"
    echo "  重启服务: sudo docker restart pdf-editor"
    echo ""
    echo "数据目录: ~/pdf-editor/processed"
    echo ""
    echo "💡 提示："
    echo "  系统重启后，PDF编辑工具会自动启动"
    echo "  首次启动可能需要30秒"
    echo ""
    
    # 测试访问
    echo "正在测试服务..."
    sleep 5
    if curl -s http://localhost:5000 > /dev/null 2>&1; then
        echo "[✓] 服务访问正常！"
        echo ""
        echo "🎉 部署成功！请在浏览器打开："
        echo "   http://localhost:5000"
    else
        echo "[注意] 服务可能还在启动中"
        echo "       请等待30秒后访问: http://localhost:5000"
        echo "       或查看日志: sudo docker logs -f pdf-editor"
    fi
    echo ""
else
    echo "[错误] 容器未能正常运行"
    echo ""
    echo "查看详细日志:"
    sudo docker logs pdf-editor
    echo ""
    echo "尝试手动修复:"
    echo "  sudo docker restart pdf-editor"
    exit 1
fi

