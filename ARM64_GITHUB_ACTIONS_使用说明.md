# GitHub Actions 构建 UOS ARM64 可运行包

## 目标

通过 GitHub Actions 自动构建一个适配 arm64 架构的 Docker 镜像，产物可在没有 Python 环境的国产统信 UOS 机器上直接使用。

## 已添加内容

- [.github/workflows/build-arm64-release.yml](.github/workflows/build-arm64-release.yml)
  - 自动触发构建
  - 使用 Docker Buildx 构建 linux/arm64 镜像
  - 导出为 tar.gz 工件并上传到 GitHub Actions
  - 当打 tag 时自动发布到 GitHub Release

- [build_arm64_release.sh](build_arm64_release.sh)
  - 本地手动执行同样的构建流程

## 使用步骤

1. 将仓库推送到 GitHub。
2. 打开 Actions 页面，选择 "Build UOS ARM64 release"。
3. 点击 "Run workflow" 手动触发，或推送到 main/master 分支、打 tag `v*` 自动触发。
4. 构建完成后，在 Actions 页面下载产物 `pdf-editor-uos-arm64`。

## 在统信 UOS 机器上使用

1. 将下载得到的 `pdf-editor-uos-arm64.tar.gz` 拷贝到目标机器。
2. 解压：
   ```bash
   gzip -d pdf-editor-uos-arm64.tar.gz
   ```
3. 导入镜像：
   ```bash
   docker load -i pdf-editor-uos-arm64.tar
   ```
4. 运行容器：
   ```bash
   docker run -d --name pdf-editor -p 5000:5000 pdf-editor-uos:arm64
   ```
5. 打开浏览器访问：
   ```text
   http://localhost:5000
   ```

## 说明

这个方案的优点是：
- 不依赖目标机器上的 Python 环境
- 兼容 arm64 架构的国产系统
- 构建过程稳定，适合 CI/CD

如果你后续想要“单文件可执行程序”而不是 Docker 镜像，也可以继续扩展成 PyInstaller + Linux arm64 的构建流程。