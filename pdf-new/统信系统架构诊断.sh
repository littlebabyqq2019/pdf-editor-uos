#!/bin/bash
# 统信系统Docker架构诊断脚本

echo "========================================="
echo "统信系统 Docker架构诊断"
echo "========================================="
echo ""

echo "【1】系统CPU架构："
ARCH=$(uname -m)
echo "    $ARCH"
echo ""

# 根据架构给出建议
case $ARCH in
    x86_64)
        echo "    ✅ 架构: AMD64 (x86_64)"
        echo "    📝 建议: 使用 pdf-editor-image.tar（当前已构建）"
        ARCH_MATCH="✅ 匹配"
        ;;
    aarch64|arm64)
        echo "    ⚠️  架构: ARM64 (aarch64)"
        echo "    📝 建议: 需要重新构建 ARM64 架构镜像"
        echo "    🔧 解决: 运行 docker-build-arm64.bat"
        ARCH_MATCH="❌ 不匹配（这是问题原因）"
        ;;
    armv7l)
        echo "    ⚠️  架构: ARMv7"
        echo "    📝 建议: 需要重新构建 ARM/v7 架构镜像"
        ARCH_MATCH="❌ 不匹配"
        ;;
    *)
        echo "    ⚠️  架构: $ARCH（未知）"
        ARCH_MATCH="❌ 可能不匹配"
        ;;
esac
echo ""

echo "【2】系统信息："
if [ -f /etc/os-release ]; then
    cat /etc/os-release | grep -E "PRETTY_NAME|VERSION" | head -2
else
    echo "    无法获取系统信息"
fi
echo ""

echo "【3】Docker状态："
if command -v docker &> /dev/null; then
    if sudo systemctl is-active --quiet docker 2>/dev/null; then
        echo "    ✅ Docker已安装并运行"
        DOCKER_VERSION=$(docker version --format '{{.Server.Version}}' 2>/dev/null)
        echo "    版本: $DOCKER_VERSION"
    else
        echo "    ⚠️  Docker已安装但未运行"
        echo "    启动命令: sudo systemctl start docker"
    fi
else
    echo "    ❌ Docker未安装"
    echo "    安装命令: sudo apt install docker.io"
fi
echo ""

echo "【4】Docker镜像检查："
if docker images pdf-editor:latest 2>/dev/null | grep -q pdf-editor; then
    echo "    ✅ 镜像已加载: pdf-editor:latest"
    
    # 检查镜像架构
    IMAGE_ARCH=$(docker inspect pdf-editor:latest 2>/dev/null | grep -A 1 "Architecture" | grep -v "Architecture" | tr -d ' ,"')
    if [ ! -z "$IMAGE_ARCH" ]; then
        echo "    镜像架构: $IMAGE_ARCH"
        
        # 对比系统架构
        if [ "$ARCH" = "x86_64" ] && [ "$IMAGE_ARCH" = "amd64" ]; then
            echo "    ✅ 镜像架构与系统匹配"
        elif [ "$ARCH" = "aarch64" ] && [ "$IMAGE_ARCH" = "arm64" ]; then
            echo "    ✅ 镜像架构与系统匹配"
        elif [ "$ARCH" = "arm64" ] && [ "$IMAGE_ARCH" = "arm64" ]; then
            echo "    ✅ 镜像架构与系统匹配"
        else
            echo "    ❌ 镜像架构不匹配！"
            echo "    系统架构: $ARCH"
            echo "    镜像架构: $IMAGE_ARCH"
            echo "    这就是 'exec format error' 的原因！"
        fi
    fi
else
    echo "    ⚠️  镜像未找到"
fi
echo ""

echo "【5】容器状态："
if docker ps -a | grep -q pdf-editor; then
    CONTAINER_STATUS=$(docker inspect --format='{{.State.Status}}' pdf-editor 2>/dev/null)
    echo "    容器存在，状态: $CONTAINER_STATUS"
    
    if [ "$CONTAINER_STATUS" != "running" ]; then
        echo "    查看错误日志:"
        echo "    ----------------------------------------"
        docker logs pdf-editor 2>&1 | tail -10
        echo "    ----------------------------------------"
    fi
else
    echo "    容器不存在"
fi
echo ""

echo "========================================="
echo "诊断结果"
echo "========================================="
echo ""
echo "系统架构: $ARCH"
echo "架构匹配: $ARCH_MATCH"
echo ""

if [ "$ARCH" = "x86_64" ]; then
    echo "✅ 您的系统是 x86_64 架构"
    echo "✅ 当前构建的镜像应该可以正常运行"
    echo ""
    echo "如果仍然出现错误，可能的原因："
    echo "  1. 镜像文件损坏，请重新下载"
    echo "  2. Docker版本问题，尝试升级Docker"
    echo "  3. 查看详细日志: docker logs pdf-editor"
else
    echo "❌ 您的系统是 $ARCH 架构"
    echo "❌ 当前镜像是为 AMD64 (x86_64) 架构构建的"
    echo ""
    echo "🔧 解决方案："
    echo ""
    echo "【方案一】在Windows电脑上重新构建ARM镜像："
    echo "  1. 在Windows电脑上运行:"
    echo "     docker-build-arm64.bat"
    echo ""
    echo "  2. 将生成的 pdf-editor-image-arm64.tar 传到统信系统"
    echo ""
    echo "  3. 在统信系统上执行:"
    echo "     docker stop pdf-editor 2>/dev/null"
    echo "     docker rm pdf-editor 2>/dev/null"
    echo "     docker rmi pdf-editor:latest 2>/dev/null"
    echo "     docker load -i pdf-editor-image-arm64.tar"
    echo "     docker run -d --name pdf-editor -p 5000:5000 \\"
    echo "       -v ~/pdf-editor/processed:/app/processed \\"
    echo "       -e TZ=Asia/Shanghai --restart unless-stopped \\"
    echo "       pdf-editor:latest"
    echo ""
    echo "【方案二】直接在统信系统上构建（需要源代码文件）："
    echo "  1. 将源代码文件传输到统信系统"
    echo "  2. 运行: docker build -t pdf-editor:latest ."
    echo "  3. 运行容器（同上）"
fi
echo ""
echo "========================================="

# 生成诊断报告文件
REPORT_FILE="docker-arch-report.txt"
{
    echo "Docker架构诊断报告"
    echo "生成时间: $(date)"
    echo "========================================"
    echo ""
    echo "系统架构: $ARCH"
    echo "系统信息:"
    cat /etc/os-release 2>/dev/null || echo "无法获取"
    echo ""
    echo "Docker版本:"
    docker version 2>/dev/null || echo "无法获取"
    echo ""
    echo "镜像列表:"
    docker images 2>/dev/null || echo "无法获取"
    echo ""
    echo "容器列表:"
    docker ps -a 2>/dev/null || echo "无法获取"
    echo ""
    echo "容器日志（最近20行）:"
    docker logs pdf-editor 2>&1 | tail -20 || echo "无法获取"
} > $REPORT_FILE

echo "📝 诊断报告已保存到: $REPORT_FILE"
echo ""

