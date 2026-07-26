# Docker镜像源配置说明

## 问题
构建时出现 "EOF" 错误，说明当前配置的镜像源无法访问。

## 解决方案

### 方法一：通过Docker Desktop配置（推荐）

1. **打开Docker Desktop**
2. **点击设置图标**（右上角齿轮图标）
3. **选择 "Docker Engine"**
4. **修改配置文件**，将以下内容添加或替换到配置中：

```json
{
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://docker.1panel.live",
    "https://hub.rat.dev",
    "https://docker.chenby.cn",
    "https://docker.anyhub.us.kg"
  ],
  "builder": {
    "gc": {
      "defaultKeepStorage": "20GB",
      "enabled": true
    }
  },
  "experimental": false
}
```

5. **点击 "Apply & restart"** 重启Docker
6. **等待Docker重启完成后**，重新运行构建脚本

### 方法二：直接使用Docker Hub（如果VPN稳定）

如果您的VPN连接稳定，可以在Docker Desktop设置中清空镜像源配置：

```json
{
  "builder": {
    "gc": {
      "defaultKeepStorage": "20GB",
      "enabled": true
    }
  },
  "experimental": false
}
```

然后重启Docker。

### 方法三：使用代理（如果配置了代理）

在Docker Desktop设置中配置代理：
1. 打开 Settings > Resources > Proxies
2. 勾选 "Manual proxy configuration"
3. 填入代理地址
4. Apply & restart

## 重新构建

配置好镜像源后，运行：

```bash
.\docker-build.bat
```

或手动构建：

```bash
# 构建镜像
docker build --platform linux/amd64 -t pdf-editor:latest .

# 导出镜像
docker save -o pdf-editor-image.tar pdf-editor:latest
```

## 测试镜像源

配置后可以测试：

```bash
docker pull hello-world
```

如果能成功拉取，说明镜像源配置正确。

## 其他可用的镜像源（2025年10月）

如果上述镜像源仍然无法使用，可以尝试：

```json
{
  "registry-mirrors": [
    "https://dockerproxy.com",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ]
}
```

