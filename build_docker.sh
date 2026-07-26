#!/bin/bash
# PDF编辑工具集成版 - Docker镜像构建脚本
# 适配国产统信UOS系统 (arm64架构)

set -e

echo "=========================================="
echo "PDF编辑工具集成版 - Docker镜像构建"
echo "目标平台: UOS arm64"
echo "=========================================="

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 镜像名称和标签
IMAGE_NAME="pdf-editor-uos"
IMAGE_TAG="latest"
FULL_IMAGE_NAME="${IMAGE_NAME}:${IMAGE_TAG}"

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误: Docker未安装，请先安装Docker${NC}"
    exit 1
fi

# 检查Docker服务是否运行
if ! docker info &> /dev/null; then
    echo -e "${RED}错误: Docker服务未运行，请启动Docker服务${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker环境检查通过${NC}"

# 检查必要文件
echo ""
echo "检查必要文件..."
required_files=("Dockerfile" "app.py" "requirements.txt" "pdf-new/requirements.txt" "pdf-editor（draw）/requirements.txt")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}错误: 缺少必要文件 $file${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ $file${NC}"
done

# 清理旧镜像（可选）
echo ""
read -p "是否清理旧的Docker镜像? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "清理旧镜像..."
    docker rmi -f ${FULL_IMAGE_NAME} 2>/dev/null || true
    echo -e "${GREEN}✓ 旧镜像已清理${NC}"
fi

# 构建镜像
echo ""
echo "=========================================="
echo "开始构建Docker镜像..."
echo "=========================================="
echo -e "${YELLOW}镜像名称: ${FULL_IMAGE_NAME}${NC}"
echo -e "${YELLOW}目标架构: linux/arm64${NC}"
echo ""

# 使用docker buildx构建arm64镜像
if docker buildx version &> /dev/null; then
    echo "使用 docker buildx 构建..."
    docker buildx build \
        --platform linux/arm64 \
        -t ${FULL_IMAGE_NAME} \
        --load \
        .
else
    echo "使用 docker build 构建..."
    docker build \
        --platform linux/arm64 \
        -t ${FULL_IMAGE_NAME} \
        .
fi

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo -e "${GREEN}✓ Docker镜像构建成功！${NC}"
    echo "=========================================="
    echo ""
    echo "镜像信息:"
    docker images ${IMAGE_NAME}
    echo ""
    echo -e "${GREEN}下一步操作:${NC}"
    echo "1. 启动容器:"
    echo "   docker-compose up -d"
    echo ""
    echo "2. 或使用docker run启动:"
    echo "   docker run -d -p 5000:5000 --name pdf-editor ${FULL_IMAGE_NAME}"
    echo ""
    echo "3. 查看日志:"
    echo "   docker logs -f pdf-editor"
    echo ""
    echo "4. 导出镜像(用于UOS系统):"
    echo "   docker save -o pdf-editor-uos-arm64.tar ${FULL_IMAGE_NAME}"
    echo ""
    echo "5. 在UOS系统上导入镜像:"
    echo "   docker load -i pdf-editor-uos-arm64.tar"
    echo ""
else
    echo ""
    echo "=========================================="
    echo -e "${RED}✗ Docker镜像构建失败！${NC}"
    echo "=========================================="
    exit 1
fi
