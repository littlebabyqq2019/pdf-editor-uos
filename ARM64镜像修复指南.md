# ARM64镜像修复指南

## 问题描述
在麒麟系统上运行Docker容器时出现 `ModuleNotFoundError: No module named 'flask'` 错误。

## 原因分析
构建过程中Python依赖安装可能不完整，特别是在ARM64模拟环境下。

## 解决方案

### 方案一：使用新构建的镜像（推荐）
使用最新构建的 `pdf-editor-uos-lean:arm64-v2` 镜像，该镜像已修复依赖问题。

```bash
# 删除旧容器
docker rm -f pdf-editor

# 使用新镜像运行
docker run -d \
  --name pdf-editor \
  -p 5000:5000 \
  --restart unless-stopped \
  pdf-editor-uos-lean:arm64-v2
```

### 方案二：手动修复现有容器
如果需要修复现有容器：

```bash
# 进入容器
docker exec -it pdf-editor bash

# 安装缺失的依赖
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple \
  Flask==2.3.3 \
  Werkzeug==2.3.7 \
  PyPDF2==3.0.1 \
  Pillow==10.0.1 \
  python-docx==0.8.11 \
  reportlab==4.0.4 \
  PyMuPDF==1.23.8

# 退出容器
exit

# 重启容器
docker restart pdf-editor
```

### 方案三：重新构建镜像
在统信/麒麟系统上直接构建（推荐在目标系统上构建）：

```bash
# 克隆或传输源码到目标系统
# 使用简化的Dockerfile
docker build -f Dockerfile.minimal -t pdf-editor-local:latest .

# 运行本地构建的镜像
docker run -d \
  --name pdf-editor \
  -p 5000:5000 \
  --restart unless-stopped \
  pdf-editor-local:latest
```

## 验证修复
```bash
# 检查容器状态
docker ps | grep pdf-editor

# 查看容器日志
docker logs pdf-editor

# 测试Flask是否可用
docker exec pdf-editor python -c "import flask; print('Flask OK')"

# 访问应用
curl http://localhost:5000
```

## 预防措施
1. 在目标ARM64系统上直接构建镜像，避免跨架构模拟问题
2. 使用多阶段构建减少镜像大小
3. 固定依赖版本避免兼容性问题

## 技术说明
- 原镜像可能在ARM64模拟构建时pip安装步骤未完全成功
- 新镜像 `arm64-v2` 已重新构建并验证依赖完整性
- 镜像大小从121MB增加到274MB，包含了完整的Python依赖