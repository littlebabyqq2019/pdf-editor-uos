# PDF编辑工具 - ARM64 Docker镜像部署指南

## 镜像信息
- **镜像名称**: pdf-editor-uos-lean:arm64-v2
- **镜像文件**: pdf-editor-uos-lean-arm64-v2.tar
- **镜像大小**: 274 MB
- **适用系统**: ARM64架构Linux系统（统信UOS、麒麟等国产操作系统）
- **应用版本**: 1.1
- **构建日期**: 2026-01-19

## 部署步骤

### 1. 传输镜像文件
将 `pdf-editor-uos-lean-arm64-v2.tar` 文件传输到目标ARM64服务器

### 2. 加载Docker镜像
```bash
docker load -i pdf-editor-uos-lean-arm64-v2.tar
```

### 3. 验证镜像
```bash
docker images | grep pdf-editor
```
应该看到：
```
pdf-editor-uos-lean   arm64-v2   b74c8f2d133e   274MB
```

### 4. 运行容器

#### 方式一：直接运行（推荐）
```bash
docker run -d \
  --name pdf-editor \
  -p 5000:5000 \
  --restart unless-stopped \
  pdf-editor-uos-lean:arm64-v2
```

#### 方式二：使用docker-compose
创建 `docker-compose.yml` 文件：
```yaml
version: '3.8'

services:
  pdf-editor:
    image: pdf-editor-uos-lean:arm64-v2
    container_name: pdf-editor
    ports:
      - "5000:5000"
    restart: unless-stopped
    environment:
      - TZ=Asia/Shanghai
    volumes:
      - ./uploads:/app/uploads
      - ./processed:/app/processed
```

启动服务：
```bash
docker-compose up -d
```

### 5. 访问应用
- **PDF处理工具**: http://服务器IP:5000
- **PDF编辑器**: http://服务器IP:5000/editor

## 容器管理命令

### 查看容器状态
```bash
docker ps | grep pdf-editor
```

### 查看容器日志
```bash
docker logs pdf-editor
```

### 停止容器
```bash
docker stop pdf-editor
```

### 启动容器
```bash
docker start pdf-editor
```

### 重启容器
```bash
docker restart pdf-editor
```

### 删除容器
```bash
docker rm -f pdf-editor
```

## 功能说明

### PDF处理工具（主页）
- PDF页面管理（删除、排序、提取）
- PDF合并
- PDF拆分
- 去除页眉页脚和公章
- PDF转Word

### PDF编辑器
- 在线PDF编辑
- 添加文字、图片
- 绘图标注
- 签名功能

## 系统要求
- Docker版本: 20.10+
- 系统架构: ARM64
- 内存: 建议2GB以上
- 磁盘: 建议500MB以上可用空间

## 端口说明
- **5000**: Web服务端口（HTTP）

## 数据持久化
如需持久化上传和处理的文件，可以挂载数据卷：
```bash
docker run -d \
  --name pdf-editor \
  -p 5000:5000 \
  -v /data/pdf-uploads:/app/uploads \
  -v /data/pdf-processed:/app/processed \
  --restart unless-stopped \
  pdf-editor-uos-lean:arm64
```

## 故障排查

### 容器无法启动
```bash
# 查看详细日志
docker logs pdf-editor

# 检查端口占用
netstat -tunlp | grep 5000
```

### 无法访问Web界面
1. 检查防火墙是否开放5000端口
2. 检查容器是否正常运行：`docker ps`
3. 检查容器日志：`docker logs pdf-editor`

### 性能优化
如果处理大文件较慢，可以增加容器内存限制：
```bash
docker run -d \
  --name pdf-editor \
  -p 5000:5000 \
  --memory="2g" \
  --restart unless-stopped \
  pdf-editor-uos-lean:arm64
```

## 技术支持
- 应用版本: 1.1
- 构建时间: 2026-01-19
- Python版本: 3.9
- 基础镜像: python:3.9-slim (ARM64)
