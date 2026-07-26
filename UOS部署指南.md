# PDF编辑工具集成版 - UOS系统部署指南

## 构建完成信息

✓ **Docker镜像构建成功**  

### 精简版镜像（推荐使用）⭐
- **镜像名称：** pdf-editor-uos:lean  
- **目标平台：** 统信UOS (arm64)  
- **镜像大小：** 280MB  
- **导出文件：** pdf-editor-uos-lean-arm64.tar (267MB)  
- **优化比例：** 比原版小 78.8%
- **构建时间：** 2024-12-11

### 原始版镜像（已不推荐）
- **镜像名称：** pdf-editor-uos:latest  
- **镜像大小：** 1.32GB  
- **导出文件：** pdf-editor-uos-arm64.tar (1.26GB)  

## 文件清单

在当前目录下已生成以下文件：
- `pdf-editor-uos-lean-arm64.tar` - **精简版Docker镜像（推荐）** ⭐
- `pdf-editor-uos-arm64.tar` - 原始版镜像（可删除以节省空间）
- `Dockerfile.lean` - 精简版镜像定义文件
- `Dockerfile` - 原始镜像定义文件
- `docker-compose.yml` - 编排配置文件（已更新为精简版）
- `.dockerignore` - 构建忽略规则
- `DOCKER_README.md` - 详细Docker文档
- `镜像优化结果.md` - 优化报告
- `build_docker.sh` - Linux构建脚本
- `build_docker.ps1` - Windows构建脚本

## 部署步骤

### 第一步：传输文件到UOS系统

将以下文件传输到UOS系统：

```bash
# 必需文件（推荐使用精简版）⭐
pdf-editor-uos-lean-arm64.tar  # 精简版Docker镜像（267MB，推荐）
docker-compose.yml             # 编排配置（可选）

# 可选文件
DOCKER_README.md              # 部署文档
UOS部署指南.md                # 本文件
镜像优化结果.md               # 优化说明

# 原始版本（不推荐，可忽略）
# pdf-editor-uos-arm64.tar    # 原始镜像（1.26GB，已不推荐）
```

**传输时间对比：**
- 精简版（267MB）：约 3-5分钟（USB 3.0）
- 原始版（1.26GB）：约 15-20分钟（USB 3.0）
- **节省时间：** 75%

传输方式：
- U盘拷贝（推荐，快速）
- SCP/SFTP
- 局域网共享

### 第二步：在UOS系统上安装Docker

如果UOS系统未安装Docker：

```bash
# 检查Docker是否已安装
docker --version

# 如未安装，使用以下命令安装
sudo apt update
sudo apt install docker.io docker-compose -y

# 启动Docker服务
sudo systemctl start docker
sudo systemctl enable docker

# 将当前用户添加到docker组（避免每次使用sudo）
sudo usermod -aG docker $USER

# 注销并重新登录使组权限生效
```

### 第三步：导入Docker镜像

在UOS系统上导入镜像：

```bash
# 进入镜像文件所在目录
cd /path/to/your/files

# 导入精简版镜像（推荐）
docker load -i pdf-editor-uos-lean-arm64.tar

# 验证镜像导入成功
docker images | grep pdf-editor-uos
```

预期输出：
```
pdf-editor-uos   lean     73717c92ce1c   280MB
```

**导入时间对比：**
- 精简版：约 1-2分钟
- 原始版：约 5-8分钟

**如使用原始版镜像：**
```bash
# 不推荐，仅供参考
docker load -i pdf-editor-uos-arm64.tar
# 输出: pdf-editor-uos   latest   b86eff1a0f3f   1.32GB
```

### 第四步：启动应用

#### 方式一：使用docker-compose（推荐）

```bash
# 确保docker-compose.yml在当前目录

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 查看状态
docker-compose ps
```

#### 方式二：使用docker run

```bash
# 创建数据目录
mkdir -p uploads processed

# 启动容器（使用精简版镜像）
docker run -d \
  --name pdf-editor \
  --platform linux/arm64 \
  -p 5000:5000 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/processed:/app/processed \
  --restart unless-stopped \
  pdf-editor-uos:lean

# 查看日志
docker logs -f pdf-editor

# 查看状态
docker ps | grep pdf-editor
```

### 第五步：访问应用

启动成功后，在浏览器中访问：

- **本机访问：** http://localhost:5000
- **局域网访问：** http://[UOS系统IP]:5000
- **PDF编辑器：** http://[UOS系统IP]:5000/editor

获取UOS系统IP地址：
```bash
ip addr show | grep inet
# 或
hostname -I
```

## 验证部署

### 1. 检查容器状态

```bash
# 查看运行中的容器
docker ps

# 预期输出应包含
CONTAINER ID   IMAGE                    STATUS         PORTS
xxxxx          pdf-editor-uos:latest    Up xx minutes  0.0.0.0:5000->5000/tcp
```

### 2. 检查应用日志

```bash
# 使用docker-compose
docker-compose logs

# 或使用docker
docker logs pdf-editor

# 预期看到Flask启动信息
```

### 3. 测试访问

```bash
# 测试健康检查
curl http://localhost:5000/

# 应返回HTML内容
```

## 常用管理命令

### 容器管理

```bash
# 启动
docker start pdf-editor
# 或
docker-compose start

# 停止
docker stop pdf-editor
# 或
docker-compose stop

# 重启
docker restart pdf-editor
# 或
docker-compose restart

# 删除容器（保留数据）
docker rm -f pdf-editor
# 或
docker-compose down

# 删除容器和数据卷
docker-compose down -v
```

### 日志查看

```bash
# 实时查看日志
docker logs -f pdf-editor
docker-compose logs -f

# 查看最近100行
docker logs --tail 100 pdf-editor

# 查看最近10分钟的日志
docker logs --since 10m pdf-editor
```

### 资源监控

```bash
# 查看容器资源使用
docker stats pdf-editor

# 查看容器详细信息
docker inspect pdf-editor
```

## 故障排查

### 问题1：容器无法启动

**检查步骤：**
```bash
# 查看容器日志
docker logs pdf-editor

# 检查端口占用
sudo netstat -tlnp | grep 5000

# 检查镜像架构
docker inspect pdf-editor-uos:latest | grep Architecture
# 应显示: "Architecture": "arm64"
```

### 问题2：无法访问应用

**检查步骤：**
```bash
# 检查容器是否运行
docker ps | grep pdf-editor

# 检查防火墙
sudo ufw status
sudo ufw allow 5000/tcp

# 测试本地连接
curl http://localhost:5000
```

### 问题3：权限问题

**解决方案：**
```bash
# 修复目录权限
chmod -R 777 uploads processed

# 或以root运行
docker run --user root ...
```

### 问题4：架构不匹配

**验证：**
```bash
# 检查系统架构
uname -m
# 应显示: aarch64 或 arm64

# 检查镜像架构
docker inspect pdf-editor-uos:latest | grep Architecture
```

## 性能优化

### 1. 限制资源使用

修改`docker-compose.yml`：
```yaml
deploy:
  resources:
    limits:
      cpus: '4'      # 增加CPU限制
      memory: 4G     # 增加内存限制
```

### 2. 启用日志轮转

添加到`docker-compose.yml`：
```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

### 3. 使用专用网络

```bash
# 创建网络
docker network create pdf-network

# 在该网络中运行
docker run --network pdf-network ...
```

## 数据备份

### 备份上传和处理的文件

```bash
# 创建备份
tar -czf pdf-data-backup-$(date +%Y%m%d).tar.gz uploads processed

# 恢复备份
tar -xzf pdf-data-backup-20241211.tar.gz
```

### 备份容器配置

```bash
# 导出容器配置
docker inspect pdf-editor > pdf-editor-config.json
```

## 更新升级

### 更新应用

1. 停止当前容器：
```bash
docker-compose down
```

2. 重新构建或导入新镜像

3. 启动新容器：
```bash
docker-compose up -d
```

## 卸载

### 完全卸载

```bash
# 1. 停止并删除容器
docker-compose down -v

# 2. 删除镜像
docker rmi pdf-editor-uos:latest

# 3. 删除数据（可选）
rm -rf uploads processed

# 4. 删除配置文件
rm docker-compose.yml Dockerfile .dockerignore
```

## 安全建议

1. **网络安全**
   - 配置防火墙规则
   - 使用反向代理（Nginx）
   - 启用HTTPS（生产环境）

2. **访问控制**
   - 限制访问IP范围
   - 添加身份验证
   - 定期更新系统

3. **数据安全**
   - 定期备份数据
   - 设置合理的目录权限
   - 监控磁盘使用

## 开机自启动

### 设置Docker服务自启动

```bash
sudo systemctl enable docker
```

### 设置容器自启动

docker-compose.yml中已配置：
```yaml
restart: unless-stopped
```

或手动设置：
```bash
docker update --restart=unless-stopped pdf-editor
```

## 监控与维护

### 定期维护任务

```bash
# 清理未使用的镜像
docker image prune -a

# 清理未使用的容器
docker container prune

# 清理未使用的卷
docker volume prune

# 查看磁盘使用
docker system df
```

### 日志管理

```bash
# 清理容器日志
sudo truncate -s 0 $(docker inspect --format='{{.LogPath}}' pdf-editor)
```

## 技术支持

### 查看版本信息

```bash
# Docker版本
docker --version

# 容器信息
docker inspect pdf-editor | grep -i version

# 系统信息
uname -a
```

### 收集诊断信息

```bash
# 生成诊断报告
docker logs pdf-editor > pdf-editor.log
docker inspect pdf-editor > pdf-editor-inspect.json
docker stats pdf-editor --no-stream > pdf-editor-stats.txt
```

## 附录

### A. 端口说明

- **5000：** Flask应用主端口
- **5000/editor：** PDF编辑器页面

### B. 目录结构

```
/app/                          # 应用根目录
├── app.py                     # 主应用文件
├── uploads/                   # 上传文件目录（挂载）
├── processed/                 # 处理后文件目录（挂载）
├── static/                    # 静态资源
├── templates/                 # 模板文件
├── pdf-new/                   # PDF处理工具
├── pdf-editor（draw）/        # PDF编辑器
├── pdf_processor.py           # PDF处理模块
├── image_processor.py         # 图像处理模块
└── file_manager.py            # 文件管理模块
```

### C. 环境变量

容器中设置的环境变量：
```
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1
FLASK_APP=app.py
FLASK_ENV=production
TZ=Asia/Shanghai
```

### D. 健康检查

容器每30秒执行一次健康检查：
```bash
python -c "import requests; requests.get('http://localhost:5000/', timeout=5)"
```

## 快速参考命令

```bash
# 启动
docker-compose up -d

# 停止
docker-compose down

# 查看日志
docker-compose logs -f

# 重启
docker-compose restart

# 查看状态
docker-compose ps

# 进入容器
docker exec -it pdf-editor bash

# 导出镜像
docker save -o backup.tar pdf-editor-uos:latest

# 导入镜像
docker load -i backup.tar
```

---

**文档版本：** 1.0  
**创建日期：** 2024-12-11  
**适用系统：** 统信UOS (arm64)  
**应用版本：** PDF编辑工具集成版 v2.0
