# ARM64 Linux 可执行文件构建说明

## 目标

将应用打包为真正的 Linux arm64 可执行文件，而不是 Docker 镜像。

## 已添加文件

- [linux_arm64.spec](linux_arm64.spec)
- [build_linux_arm64_exe.sh](build_linux_arm64_exe.sh)
- [.github/workflows/build-arm64-release.yml](.github/workflows/build-arm64-release.yml)

## 构建方式

### GitHub Actions

1. 将仓库推送到 GitHub。
2. 打开 Actions 页面，执行工作流 `Build Linux ARM64 executable`。
3. 构建完成后下载产物 `pdf-editor-linux-arm64`。

产物是一个 `tar.gz`，解压后会得到可执行文件：

```bash
tar -xzf pdf-editor-linux-arm64.tar.gz
./PDF编辑工具集成版
```

### 本地构建

```bash
bash build_linux_arm64_exe.sh
```

## 说明

- 产物是 Linux 可执行文件，不依赖 Python 环境。
- 适合部署到 arm64 Linux 机器，例如国产统信 UOS arm64。
- 运行时需要给文件执行权限：

```bash
chmod +x PDF编辑工具集成版
```
