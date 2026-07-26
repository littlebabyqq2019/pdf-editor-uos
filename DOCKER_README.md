# PDF编辑工具集成版 - Docker部署文档

## 概述

本文档说明如何将PDF编辑工具集成版打包为Docker镜像，并在国产统信UOS系统（arm64架构）上部署运行。

## 系统要求

### 开发/构建环境
- Docker 20.10+
- Docker Compose 2.0+ (可选)
- Linux/macOS/Windows系统

### 目标部署环境
- 统信UOS操作系统
- arm64架构
- Docker环境

## 快速开始

### 方法一：使用构建脚本（推荐）

```bash
# 给脚本添加执行权限
chmod +x build_docker.sh

# 运行构建脚本
./build_docker.sh
```

### 方法二：使用Docker Compose

```bash
# 构建并启动
docker-compose up -d --build

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 方法三：手动构建

```bash
# 1. 构建镜像
docker build --platform linux/arm64 -t pdf-editor-uos:latest .

# 2. 启动容器
docker run -d \
  --name pdf-editor \
  --platform linux/arm64 \
  -p 5000:5000 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/processed:/app/processed \
  pdf-editor-uos:latest

# 3. 查看日志
docker logs -f pdf-editor
```

## 镜像导出与导入

### 在构建机器上导出镜像

```bash
# 导出为tar文件
docker save -o pdf-editor-uos-arm64.tar pdf-editor-uos:latest

# 压缩（可选，节省传输空间）
gzip pdf-editor-uos-arm64.tar
```

### 在UOS系统上导入镜像

```bash
# 如果压缩过，先解压
gunzip pdf-editor-uos-arm64.tar.gz

# 导入镜像
docker load -i pdf-editor-uos-arm64.tar

# 验证镜像
docker images | grep pdf-editor-uos
```

### 在UOS系统上运行

```bash
# 创建必要的目录
mkdir -p uploads processed

# 启动容器
docker run -d \
  --name pdf-editor \
  --platform linux/arm64 \
  -p 5000:5000 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/processed:/app/processed \
  --restart unless-stopped \
  pdf-editor-uos:latest

# 查看容器状态
docker ps

# 查看日志
docker logs -f pdf-editor
```

## 访问应用

容器启动后，可以通过以下地址访问：

- **本机访问**: http://localhost:5000
- **局域网访问**: http://[UOS系统IP]:5000
- **PDF编辑器**: http://[UOS系统IP]:5000/editor

## 容器管理命令

```bash
# 启动容器
docker start pdf-editor

# 停止容器
docker stop pdf-editor

# 重启容器
docker restart pdf-editor

# 删除容器
docker rm -f pdf-editor

# 查看容器日志
docker logs -f pdf-editor

# 进入容器
docker exec -it pdf-editor bash

# 查看容器资源使用
docker stats pdf-editor

# 查看容器详细信息
docker inspect pdf-editor
```

## 使用Docker Compose管理（推荐）

如果使用Docker Compose，可以使用以下命令：

```bash
# 启动服务（后台运行）
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose stop

# 启动服务
docker-compose start

# 重启服务
docker-compose restart

# 停止并删除容器
docker-compose down

# 停止并删除容器、数据卷
docker-compose down -v
```

## 配置说明

### 端口配置

默认端口为5000，如需修改：

**方法1: 修改docker-compose.yml**
```yaml
ports:
  - "8080:5000"  # 将主机8080端口映射到容器5000端口
```

**方法2: docker run命令**
```bash
docker run -d -p 8080:5000 ...
```

### 数据持久化

容器使用数据卷挂载，确保数据持久化：

- `./uploads:/app/uploads` - 上传文件目录
- `./processed:/app/processed` - 处理后文件目录

### 资源限制

在`docker-compose.yml`中已配置资源限制：

- CPU限制: 最多2核，预留1核
- 内存限制: 最多2GB，预留1GB

如需调整，修改`docker-compose.yml`中的`deploy.resources`部分。

## 镜像信息

### 基础镜像
- `python:3.9-slim` (arm64)

### 已安装的主要依赖
- Flask 2.3.3
- PyMuPDF 1.23.8
- PyPDF2 3.0.1
- Pillow 10.0.1
- opencv-python 4.8.1.78
- numpy 1.24.3
- python-docx 0.8.11
- reportlab 4.0.4
- scikit-image >=0.21.0

### 镜像大小
预计约800MB-1GB（取决于依赖）

## 故障排除

### 问题1: 镜像构建失败

**原因**: 网络问题或依赖下载失败

**解决方案**:
```bash
# 使用国内镜像源重新构建
docker build --build-arg PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple -t pdf-editor-uos:latest .
```

### 问题2: 容器无法启动

**检查步骤**:
```bash
# 查看容器日志
docker logs pdf-editor

# 检查端口是否被占用
netstat -tlnp | grep 5000

# 检查容器状态
docker inspect pdf-editor
```

### 问题3: 权限问题

**解决方案**:
```bash
# 确保挂载目录有正确权限
sudo chmod -R 777 uploads processed

# 或使用root用户运行容器
docker run --user root ...
```

### 问题4: arm64架构不兼容

**检查系统架构**:
```bash
# 在UOS系统上检查
uname -m
# 应显示: aarch64 或 arm64

# 检查Docker支持的平台
docker version
```

### 问题5: 健康检查失败

**原因**: 应用启动慢或端口未正确绑定

**解决方案**:
```bash
# 增加启动等待时间，修改docker-compose.yml
healthcheck:
  start_period: 60s  # 从40s增加到60s
```

## 安全建议

1. **不要使用root用户运行**（当前配置已避免）
2. **限制容器资源使用**（已配置资源限制）
3. **定期更新依赖包**
4. **使用防火墙限制访问**
5. **启用HTTPS**（生产环境建议）

## 性能优化

### 1. 构建优化

```bash
# 使用构建缓存
docker build --cache-from pdf-editor-uos:latest -t pdf-editor-uos:latest .

# 多阶段构建（可选，进一步减小镜像）
# 需要修改Dockerfile
```

### 2. 运行优化

```bash
# 使用专用网络
docker network create pdf-network

# 设置CPU亲和性
docker run --cpuset-cpus="0-1" ...

# 调整内存限制
docker run -m 2g --memory-swap 2g ...
```

## 备份与恢复

### 备份数据

```bash
# 备份上传和处理的文件
tar -czf pdf-data-backup-$(date +%Y%m%d).tar.gz uploads processed

# 备份容器配置
docker inspect pdf-editor > pdf-editor-config.json
```

### 恢复数据

```bash
# 恢复文件
tar -xzf pdf-data-backup-20241211.tar.gz

# 重新启动容器
docker-compose up -d
```

## 更新升级

### 更新应用代码

```bash
# 1. 停止容器
docker-compose down

# 2. 拉取最新代码或更新文件

# 3. 重新构建镜像
docker-compose build --no-cache

# 4. 启动容器
docker-compose up -d
```

### 更新依赖

```bash
# 1. 更新requirements.txt文件

# 2. 重新构建镜像
docker build --no-cache -t pdf-editor-uos:latest .

# 3. 重新启动容器
docker-compose up -d
```

## 监控与日志

### 查看实时日志

```bash
# Docker Compose
docker-compose logs -f

# Docker
docker logs -f pdf-editor
```

### 限制日志大小

在`docker-compose.yml`中添加：

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

### 监控容器资源

```bash
# 实时监控
docker stats pdf-editor

# 或使用第三方工具
# 如: Portainer, Grafana + Prometheus
```

## 附录

### 目录结构

```
pdf-editor(2in1)/
├── Dockerfile              # Docker镜像定义
├── .dockerignore          # Docker构建忽略文件
├── docker-compose.yml     # Docker Compose配置
├── build_docker.sh        # 构建脚本
├── DOCKER_README.md       # 本文档
├── app.py                 # 主应用
├── requirements.txt       # 依赖列表
├── pdf-new/               # PDF处理工具
│   └── requirements.txt
├── pdf-editor（draw）/     # PDF编辑器
│   └── requirements.txt
├── uploads/               # 上传目录（挂载）
└── processed/             # 处理目录（挂载）
```

### 相关资源

- Docker官方文档: https://docs.docker.com/
- 统信UOS文档: https://www.uniontech.com/
- Flask文档: https://flask.palletsprojects.com/

## 技术支持

如有问题，请联系开发团队或查看项目文档。

---

**版本**: 1.0  
**更新日期**: 2024-12-11  
**适用系统**: 统信UOS (arm64)
