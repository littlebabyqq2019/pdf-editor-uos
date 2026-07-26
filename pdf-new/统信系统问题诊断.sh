#!/bin/bash
# PDF编辑工具 - 问题诊断脚本

echo "========================================"
echo "PDF编辑工具 - 问题诊断"
echo "========================================"
echo ""
echo "正在诊断 localhost 连接被拒绝的问题..."
echo ""

# 1. 检查Docker服务
echo "【1】检查Docker服务状态"
echo "----------------------------------------"
if systemctl is-active --quiet docker 2>/dev/null || sudo systemctl is-active --quiet docker 2>/dev/null; then
    echo "✓ Docker服务正在运行"
    docker version 2>/dev/null | grep "Server:" -A 3 || sudo docker version 2>/dev/null | grep "Server:" -A 3
else
    echo "✗ Docker服务未运行"
    echo "  解决方法: sudo systemctl start docker"
    exit 1
fi
echo ""

# 2. 检查容器状态
echo "【2】检查容器状态"
echo "----------------------------------------"
CONTAINER_STATUS=$(docker ps -a --filter name=pdf-editor --format "{{.Status}}" 2>/dev/null || sudo docker ps -a --filter name=pdf-editor --format "{{.Status}}" 2>/dev/null)

if [ -z "$CONTAINER_STATUS" ]; then
    echo "✗ 容器不存在"
    echo "  解决方法: 运行部署脚本创建容器"
    exit 1
elif echo "$CONTAINER_STATUS" | grep -q "Up"; then
    echo "✓ 容器正在运行"
    docker ps --filter name=pdf-editor 2>/dev/null || sudo docker ps --filter name=pdf-editor 2>/dev/null
else
    echo "✗ 容器已停止"
    echo "  状态: $CONTAINER_STATUS"
    echo "  解决方法: sudo docker start pdf-editor"
    
    # 尝试启动容器
    echo ""
    echo "正在尝试启动容器..."
    sudo docker start pdf-editor
    sleep 3
fi
echo ""

# 3. 检查容器日志
echo "【3】检查容器日志（最近20行）"
echo "----------------------------------------"
docker logs --tail 20 pdf-editor 2>/dev/null || sudo docker logs --tail 20 pdf-editor 2>/dev/null
echo ""

# 4. 检查端口映射
echo "【4】检查端口映射"
echo "----------------------------------------"
PORT_MAPPING=$(docker port pdf-editor 2>/dev/null || sudo docker port pdf-editor 2>/dev/null)
if [ ! -z "$PORT_MAPPING" ]; then
    echo "✓ 端口映射配置:"
    echo "$PORT_MAPPING"
else
    echo "✗ 无端口映射"
fi
echo ""

# 5. 检查端口监听
echo "【5】检查端口监听"
echo "----------------------------------------"
if netstat -tuln 2>/dev/null | grep -q ":5000 "; then
    echo "✓ 5000端口正在监听"
    netstat -tuln | grep ":5000 "
elif ss -tuln 2>/dev/null | grep -q ":5000 "; then
    echo "✓ 5000端口正在监听"
    ss -tuln | grep ":5000 "
else
    echo "✗ 5000端口未监听"
    echo "  可能原因:"
    echo "  1. 容器内应用未启动"
    echo "  2. 端口映射错误"
    echo "  3. 应用启动失败"
fi
echo ""

# 6. 测试容器内部连接
echo "【6】测试容器内部连接"
echo "----------------------------------------"
if docker exec pdf-editor curl -s http://localhost:5000 >/dev/null 2>&1 || sudo docker exec pdf-editor curl -s http://localhost:5000 >/dev/null 2>&1; then
    echo "✓ 容器内部可以访问应用"
else
    echo "✗ 容器内部无法访问应用"
    echo "  说明: 应用可能未正常启动"
fi
echo ""

# 7. 测试宿主机连接
echo "【7】测试宿主机连接"
echo "----------------------------------------"
if curl -s http://localhost:5000 >/dev/null 2>&1; then
    echo "✓ 宿主机可以访问应用"
    echo ""
    echo "连接测试成功！应该可以在浏览器访问了。"
else
    echo "✗ 宿主机无法访问应用"
    echo "  正在进一步检查..."
    
    # 检查防火墙
    echo ""
    echo "【8】检查防火墙状态"
    echo "----------------------------------------"
    if command -v ufw &> /dev/null; then
        UFW_STATUS=$(sudo ufw status 2>/dev/null | grep "Status:" | awk '{print $2}')
        if [ "$UFW_STATUS" = "active" ]; then
            echo "⚠ UFW防火墙已启用"
            sudo ufw status | grep 5000
            echo "  建议: sudo ufw allow 5000/tcp"
        else
            echo "✓ UFW防火墙未启用"
        fi
    fi
    
    if command -v firewall-cmd &> /dev/null; then
        if sudo firewall-cmd --state 2>/dev/null | grep -q "running"; then
            echo "⚠ firewalld已启用"
            sudo firewall-cmd --list-ports 2>/dev/null | grep 5000
            echo "  建议: sudo firewall-cmd --permanent --add-port=5000/tcp"
            echo "        sudo firewall-cmd --reload"
        else
            echo "✓ firewalld未启用"
        fi
    fi
fi
echo ""

# 9. 检查架构匹配
echo "【9】检查架构匹配"
echo "----------------------------------------"
SYSTEM_ARCH=$(uname -m)
IMAGE_ARCH=$(docker inspect pdf-editor --format='{{.Architecture}}' 2>/dev/null || sudo docker inspect pdf-editor --format='{{.Architecture}}' 2>/dev/null)
echo "系统架构: $SYSTEM_ARCH"
echo "镜像架构: $IMAGE_ARCH"

if [ "$SYSTEM_ARCH" = "aarch64" ] || [ "$SYSTEM_ARCH" = "arm64" ]; then
    if [ "$IMAGE_ARCH" = "arm64" ]; then
        echo "✓ 架构匹配"
    else
        echo "✗ 架构不匹配！"
        echo "  系统是ARM64，但镜像是 $IMAGE_ARCH"
        echo "  需要使用 pdf-editor:arm64 镜像"
    fi
elif [ "$SYSTEM_ARCH" = "x86_64" ]; then
    if [ "$IMAGE_ARCH" = "amd64" ]; then
        echo "✓ 架构匹配"
    else
        echo "✗ 架构不匹配！"
        echo "  系统是x86_64，但镜像是 $IMAGE_ARCH"
    fi
fi
echo ""

# 10. 检查容器健康状态
echo "【10】检查容器健康状态"
echo "----------------------------------------"
HEALTH_STATUS=$(docker inspect --format='{{.State.Health.Status}}' pdf-editor 2>/dev/null || sudo docker inspect --format='{{.State.Health.Status}}' pdf-editor 2>/dev/null)
if [ ! -z "$HEALTH_STATUS" ]; then
    echo "健康状态: $HEALTH_STATUS"
else
    echo "未配置健康检查"
fi
echo ""

# 总结和建议
echo "========================================"
echo "诊断总结"
echo "========================================"
echo ""

# 获取容器状态
RUNNING=$(docker ps --filter name=pdf-editor --format "{{.Names}}" 2>/dev/null || sudo docker ps --filter name=pdf-editor --format "{{.Names}}" 2>/dev/null)

if [ ! -z "$RUNNING" ]; then
    if curl -s http://localhost:5000 >/dev/null 2>&1; then
        echo "✅ 诊断结果: 应用运行正常"
        echo ""
        echo "访问地址: http://localhost:5000"
        echo "          http://$(hostname -I | awk '{print $1}'):5000"
    else
        echo "⚠️ 诊断结果: 容器运行但无法访问"
        echo ""
        echo "可能的原因和解决方法:"
        echo ""
        echo "1. 应用还在启动中"
        echo "   等待30秒后重试"
        echo ""
        echo "2. 应用启动失败"
        echo "   查看完整日志: sudo docker logs pdf-editor"
        echo ""
        echo "3. 端口被占用"
        echo "   检查端口: netstat -tuln | grep 5000"
        echo "   更换端口: sudo docker rm -f pdf-editor"
        echo "            sudo docker run -d -p 8080:5000 ... pdf-editor:arm64"
        echo ""
        echo "4. 防火墙阻止"
        echo "   开放端口: sudo ufw allow 5000/tcp"
        echo ""
        echo "5. Docker网络问题"
        echo "   重启容器: sudo docker restart pdf-editor"
        echo "   重启Docker: sudo systemctl restart docker"
    fi
else
    echo "❌ 诊断结果: 容器未运行"
    echo ""
    echo "解决方法:"
    echo "1. 启动容器: sudo docker start pdf-editor"
    echo "2. 查看错误: sudo docker logs pdf-editor"
    echo "3. 重新部署: ./统信系统ARM64部署.sh"
fi

echo ""
echo "========================================"
echo "快速修复命令"
echo "========================================"
echo ""
echo "# 查看详细日志"
echo "sudo docker logs -f pdf-editor"
echo ""
echo "# 重启容器"
echo "sudo docker restart pdf-editor"
echo ""
echo "# 重启Docker服务"
echo "sudo systemctl restart docker"
echo ""
echo "# 停止并重新创建容器"
echo "sudo docker stop pdf-editor"
echo "sudo docker rm pdf-editor"
echo "./统信系统ARM64部署.sh"
echo ""

# 生成诊断报告
REPORT_FILE="诊断报告-$(date +%Y%m%d-%H%M%S).txt"
{
    echo "PDF编辑工具诊断报告"
    echo "生成时间: $(date)"
    echo "========================================"
    echo ""
    echo "系统信息:"
    uname -a
    echo ""
    echo "Docker版本:"
    docker version 2>/dev/null || sudo docker version 2>/dev/null
    echo ""
    echo "容器状态:"
    docker ps -a --filter name=pdf-editor 2>/dev/null || sudo docker ps -a --filter name=pdf-editor 2>/dev/null
    echo ""
    echo "容器日志:"
    docker logs --tail 50 pdf-editor 2>&1 || sudo docker logs --tail 50 pdf-editor 2>&1
    echo ""
    echo "端口监听:"
    netstat -tuln | grep 5000 2>/dev/null || ss -tuln | grep 5000 2>/dev/null
} > "$REPORT_FILE"

echo "📝 诊断报告已保存到: $REPORT_FILE"
echo ""

