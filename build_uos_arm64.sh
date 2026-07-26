#!/bin/bash
# PDF编辑工具集成版 - Docker镜像构建脚本
# 适配国产统信UOS系统 (arm64架构)
# 使用 Dockerfile.lean

set -e

# 配置
IMAGE_NAME="pdf-editor-uos"
TAG="lean"
FULL_IMAGE_NAME="${IMAGE_NAME}:${TAG}"
TAR_FILE="docker镜像/pdf-editor-uos-lean-arm64.tar"
DOCKERFILE="Dockerfile.lean"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}==========================================${NC}"
echo -e "${GREEN}PDF编辑工具集成版 - Docker镜像构建${NC}"
echo -e "${GREEN}目标平台: UOS arm64${NC}"
echo -e "${GREEN}使用配置: ${DOCKERFILE}${NC}"
echo -e "${GREEN}==========================================${NC}"

# 1. 检查Docker
echo ""
echo -e "${YELLOW}[1/4] 检查Docker环境...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误: Docker未安装${NC}"
    exit 1
fi
echo -e "${GREEN}Docker环境正常${NC}"

# 2. 检查文件
echo ""
echo -e "${YELLOW}[2/4] 检查必要文件...${NC}"
if [ ! -f "$DOCKERFILE" ]; then
    echo -e "${RED}错误: 找不到 $DOCKERFILE${NC}"
    exit 1
fi
echo -e "${GREEN}必要文件存在${NC}"

# 3. 构建
echo ""
echo -e "${YELLOW}[3/4] 开始构建...${NC}"

# 尝试使用 buildx
if docker buildx version &> /dev/null; then
    echo "使用 docker buildx 构建..."
    docker buildx build \
        --platform linux/arm64 \
        -t ${FULL_IMAGE_NAME} \
        -f ${DOCKERFILE} \
        --load \
        .
else
    echo "使用 docker build 构建..."
    docker build \
        --platform linux/arm64 \
        -t ${FULL_IMAGE_NAME} \
        -f ${DOCKERFILE} \
        .
fi

# 4. 导出
echo ""
echo -e "${YELLOW}[4/4] 导出镜像...${NC}"
mkdir -p docker镜像
docker save -o ${TAR_FILE} ${FULL_IMAGE_NAME}

echo ""
echo -e "${GREEN}==========================================${NC}"
echo -e "${GREEN}构建完成！${NC}"
echo -e "镜像文件: ${TAR_FILE}"
ls -lh ${TAR_FILE}
echo -e "${GREEN}==========================================${NC}"
