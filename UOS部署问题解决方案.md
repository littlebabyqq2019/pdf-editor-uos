# UOS部署问题解决方案

## 问题：docker-compose版本不支持

### 错误信息
```
ERROR: Version in "./docker-compose.yml" is unsupported.
```

### 原因
UOS系统上的docker-compose版本较旧，不支持docker-compose版本3.8。

### ✅ 解决方案

已将`docker-compose.yml`版本从**3.8**降级到**3.3**，并移除了不兼容的配置。

---

## 🚀 现在可以使用的命令

### 方式1：使用更新后的docker-compose.yml（推荐）

```bash
# 确保在包含docker-compose.yml的目录中
cd ~/pdf-editor

# 启动服务
sudo docker-compose up -d

# 查看日志
sudo docker-compose logs -f

# 查看状态
sudo docker-compose ps

# 停止服务
sudo docker-compose stop

# 重启服务
sudo docker-compose restart
```

---

### 方式2：使用docker run命令

如果docker-compose仍有问题，可以直接使用docker run：

```bash
# 创建数据目录
mkdir -p ~/pdf-editor/uploads ~/pdf-editor/processed

# 启动容器
sudo docker run -d \
  --name pdf-editor-app \
  -p 5000:5000 \
  -e FLASK_APP=app.py \
  -e FLASK_ENV=production \
  -e TZ=Asia/Shanghai \
  -v ~/pdf-editor/uploads:/app/uploads \
  -v ~/pdf-editor/processed:/app/processed \
  --restart unless-stopped \
  pdf-editor-uos:lean

# 查看日志
sudo docker logs -f pdf-editor-app

# 查看状态
sudo docker ps | grep pdf-editor

# 停止容器
sudo docker stop pdf-editor-app

# 启动容器
sudo docker start pdf-editor-app

# 重启容器
sudo docker restart pdf-editor-app

# 删除容器（保留数据）
sudo docker rm -f pdf-editor-app
```

---

### 方式3：使用docker run并限制资源

如果需要限制CPU和内存：

```bash
sudo docker run -d \
  --name pdf-editor-app \
  -p 5000:5000 \
  -e FLASK_APP=app.py \
  -e FLASK_ENV=production \
  -e TZ=Asia/Shanghai \
  -v ~/pdf-editor/uploads:/app/uploads \
  -v ~/pdf-editor/processed:/app/processed \
  --restart unless-stopped \
  --cpus="2" \
  --memory="2g" \
  --memory-reservation="1g" \
  pdf-editor-uos:lean
```

---

## 🔍 验证部署

### 1. 检查容器状态

```bash
# 查看运行中的容器
sudo docker ps

# 预期输出类似：
# CONTAINER ID   IMAGE                  STATUS         PORTS
# xxxxx          pdf-editor-uos:lean    Up 2 minutes   0.0.0.0:5000->5000/tcp
```

### 2. 检查容器日志

```bash
# 查看最近的日志
sudo docker logs --tail 50 pdf-editor-app

# 实时查看日志
sudo docker logs -f pdf-editor-app

# 预期看到Flask启动信息，类似：
# * Running on http://0.0.0.0:5000
# * Debug mode: off
```

### 3. 测试访问

```bash
# 本地测试
curl http://localhost:5000

# 应该返回HTML内容

# 获取本机IP
ip addr show | grep "inet " | grep -v 127.0.0.1

# 然后在浏览器访问
# http://[本机IP]:5000
```

---

## 📊 docker-compose.yml 变更说明

### 修改内容

| 项目 | 修改前 | 修改后 | 原因 |
|------|--------|--------|------|
| **version** | 3.8 | 3.3 | 兼容旧版docker-compose |
| **platform** | linux/arm64 | 已移除 | version 3.3不支持 |
| **deploy** | 资源限制配置 | 已注释 | 非swarm模式不生效 |

### 保留的配置

✅ 以下配置完全保留：
- 镜像名称：`pdf-editor-uos:lean`
- 端口映射：5000:5000
- 环境变量
- 数据卷挂载
- 重启策略
- 健康检查
- 网络配置

---

## 🔧 常见问题

### Q1: 为什么移除了platform字段？

**A:** `platform`字段在docker-compose version 3.4+才支持。由于镜像已经是arm64架构构建的，Docker会自动识别和使用正确的架构，不需要显式指定。

### Q2: 资源限制还生效吗？

**A:** `deploy`部分的资源限制在非swarm模式下不生效。如需限制资源，请使用：

```bash
# 使用docker run的--cpus和--memory参数
sudo docker run -d \
  --cpus="2" \
  --memory="2g" \
  ...其他参数
```

或使用docker update：
```bash
sudo docker update --cpus="2" --memory="2g" pdf-editor-app
```

### Q3: 如何查看docker-compose版本？

```bash
docker-compose --version
# 或
docker-compose version
```

### Q4: 可以升级docker-compose吗？

可以，但不是必需的。如果想升级：

```bash
# 下载最新版本
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# 添加执行权限
sudo chmod +x /usr/local/bin/docker-compose

# 验证版本
docker-compose --version
```

### Q5: 端口5000被占用怎么办？

修改docker-compose.yml中的端口映射：

```yaml
ports:
  - "8080:5000"  # 主机使用8080端口
```

或在docker run中：
```bash
-p 8080:5000  # 主机使用8080端口
```

### Q6: 如何彻底卸载？

```bash
# 停止并删除容器
sudo docker-compose down
# 或
sudo docker rm -f pdf-editor-app

# 删除镜像
sudo docker rmi pdf-editor-uos:lean

# 删除数据（可选，会丢失上传的文件）
rm -rf ~/pdf-editor/uploads ~/pdf-editor/processed
```

---

## 📝 完整部署流程（推荐）

### 步骤1：确认文件

```bash
cd ~/pdf-editor
ls -lh

# 应该看到：
# pdf-editor-uos-lean-arm64.tar  (267MB)
# docker-compose.yml             (2KB)
```

### 步骤2：导入镜像

```bash
sudo docker load -i pdf-editor-uos-lean-arm64.tar

# 验证
sudo docker images | grep pdf-editor-uos
```

### 步骤3：启动服务

```bash
# 使用docker-compose（推荐）
sudo docker-compose up -d

# 或使用docker run
sudo docker run -d \
  --name pdf-editor-app \
  -p 5000:5000 \
  -e FLASK_APP=app.py \
  -e FLASK_ENV=production \
  -e TZ=Asia/Shanghai \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/processed:/app/processed \
  --restart unless-stopped \
  pdf-editor-uos:lean
```

### 步骤4：验证部署

```bash
# 检查容器
sudo docker ps | grep pdf-editor

# 查看日志
sudo docker logs pdf-editor-app

# 测试访问
curl http://localhost:5000
```

### 步骤5：浏览器访问

```bash
# 获取IP地址
hostname -I

# 在浏览器打开
# http://[你的IP]:5000
```

---

## 🎯 推荐配置总结

### 使用docker-compose（最简单）

```bash
# docker-compose.yml 已配置好：
# - 版本：3.3（兼容性好）
# - 镜像：pdf-editor-uos:lean（280MB）
# - 端口：5000
# - 自动重启：是
# - 健康检查：是

# 一键启动
sudo docker-compose up -d
```

### 使用docker run（更灵活）

```bash
# 可以自定义更多参数
# 适合需要特殊配置的场景
sudo docker run -d \
  --name pdf-editor-app \
  -p 5000:5000 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/processed:/app/processed \
  --restart unless-stopped \
  --cpus="2" \
  --memory="2g" \
  pdf-editor-uos:lean
```

---

## 📞 技术支持

如果仍有问题，请提供以下信息：

```bash
# 1. Docker版本
docker --version

# 2. Docker Compose版本
docker-compose --version

# 3. 系统信息
uname -a

# 4. 容器日志
sudo docker logs pdf-editor-app

# 5. 错误信息
# 完整的错误输出
```

---

## ✅ 部署检查清单

部署完成后，确认以下各项：

- [ ] 镜像已成功导入（280MB）
- [ ] 容器正在运行（docker ps）
- [ ] 端口5000已开放
- [ ] 可以访问 http://localhost:5000
- [ ] 可以从其他机器访问（如需要）
- [ ] 上传功能正常
- [ ] PDF处理功能正常
- [ ] 容器设置为自动重启

---

**文档版本：** 1.0  
**更新时间：** 2024-12-12  
**适用系统：** 统信UOS (arm64)  
**docker-compose版本：** 3.3  
**镜像：** pdf-editor-uos:lean (280MB)
