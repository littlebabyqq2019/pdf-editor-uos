#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

IMAGE_NAME="pdf-editor-uos"
TAG="arm64"
ARTIFACT_DIR="$ROOT_DIR/artifacts"
mkdir -p "$ARTIFACT_DIR"

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker 未安装，无法构建。" >&2
  exit 1
fi

if ! docker buildx version >/dev/null 2>&1; then
  echo "Docker Buildx 不可用，正在尝试启用。" >&2
  exit 1
fi

echo "开始构建 arm64 镜像..."
docker buildx build \
  --platform linux/arm64 \
  --file Dockerfile.lean \
  --tag "${IMAGE_NAME}:${TAG}" \
  --load \
  .

echo "导出镜像为 tar.gz..."
docker save "${IMAGE_NAME}:${TAG}" | gzip > "$ARTIFACT_DIR/pdf-editor-uos-arm64.tar.gz"

echo "构建完成，产物：${ARTIFACT_DIR}/pdf-editor-uos-arm64.tar.gz"
