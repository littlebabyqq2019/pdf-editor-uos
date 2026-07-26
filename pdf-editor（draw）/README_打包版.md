# PDF编辑器 v1.2 - 打包版

## 🎯 项目信息

- **应用名称**：PDF编辑器
- **版本号**：1.2
- **端口**：5002
- **控制台**：隐藏
- **打包方式**：PyInstaller 单文件

---

## 📦 快速开始

### 开发环境运行

```bash
# 1. 激活虚拟环境
venv\Scripts\activate

# 2. 运行应用
python app.py

# 3. 浏览器访问
http://localhost:5002
```

### 打包为EXE

```bash
# 方法1：使用脚本（推荐）
打包脚本.bat

# 方法2：手动打包
venv\Scripts\activate
pyinstaller --clean "PDF编辑器.spec"
```

### 运行打包后的程序

```bash
# 进入dist目录
cd dist

# 运行
PDF编辑器.exe

# 浏览器会自动打开 http://localhost:5002
```

---

## 📋 已完成的配置

### ✅ 端口配置
- 端口号：**5002**（已从5000修改）
- 配置位置：`app.py` 第42行

### ✅ 版本信息
- 版本号：**1.0**
- 显示位置：启动信息、版本文件
- 配置位置：
  - `app.py` 第11行
  - `file_version_info.txt`

### ✅ 打包配置
- **控制台窗口**：隐藏（`console=False`）
- **打包方式**：单文件
- **包含文件**：
  - ✅ static/ 目录
  - ✅ templates/ 目录
- **依赖模块**：使用虚拟环境中的包

### ✅ 自动功能
- 打包后自动打开浏览器
- 自动检测运行环境（开发/打包）
- 打包后禁用debug和reloader

---

## 📂 项目文件结构

```
pdf-editor4/
├── app.py                    # 主应用（已配置端口5002和版本1.0）
├── PDF编辑器.spec           # PyInstaller配置文件
├── file_version_info.txt    # Windows版本信息
├── 打包脚本.bat             # 自动打包脚本
├── 打包说明.md              # 详细打包说明
├── README_打包版.md         # 本文件
│
├── venv/                     # 虚拟环境（包含所有依赖）
│
├── static/                   # 静态资源
│   ├── css/
│   ├── js/
│   └── lib/
│
├── templates/                # HTML模板
│   └── index.html
│
├── dist/                     # 打包输出目录
│   └── PDF编辑器.exe        # 生成的可执行文件
│
└── build/                    # 临时构建文件
```

---

## 🚀 打包步骤

### 1. 准备环境
```bash
# 确保虚拟环境已创建
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate

# 安装依赖
pip install flask pyinstaller
```

### 2. 执行打包
```bash
# 双击运行
打包脚本.bat

# 或手动执行
pyinstaller --clean "PDF编辑器.spec"
```

### 3. 测试程序
```bash
cd dist
PDF编辑器.exe
```

---

## 🎨 核心配置说明

### app.py 关键配置

```python
# 版本信息
VERSION = "1.1"
APP_NAME = "PDF编辑器"

# 端口配置
PORT = 5002

# 打包检测
is_frozen = getattr(sys, 'frozen', False)

# 运行配置
app.run(
    host='0.0.0.0',
    port=PORT,
    debug=False if is_frozen else True,
    use_reloader=False if is_frozen else True
)
```

### PDF编辑器.spec 关键配置

```python
# 包含文件
datas=[
    ('static', 'static'),
    ('templates', 'templates'),
]

# 隐藏控制台（重要！）
console=False

# 版本信息
version='file_version_info.txt'
```

---

## ✨ 功能特性

### 打包后特性
- ✅ 双击运行，无需安装Python
- ✅ 无控制台窗口
- ✅ 自动打开默认浏览器
- ✅ 单个exe文件，方便分发
- ✅ 包含所有静态资源

### 编辑功能
- ✅ PDF文件上传和预览
- ✅ 多页面管理和切换
- ✅ 文字添加和编辑
- ✅ 擦除、高亮、下划线
- ✅ 形状绘制
- ✅ 撤销/重做
- ✅ 缩放功能（25%-400%）
- ✅ 导出编辑后的PDF

---

## 📊 版本信息

### 文件版本
- **文件版本**：1.2.0.0
- **产品版本**：1.2.0.0
- **公司名称**：（可自定义）
- **版权信息**：Copyright © 2025

### 应用版本
- **主版本**：1
- **次版本**：0
- **修订版本**：0
- **构建版本**：0

---

## 🔧 技术栈

### 后端
- Python 3.x
- Flask 2.x
- PyInstaller

### 前端
- HTML5
- CSS3（TailwindCSS）
- JavaScript (ES6+)
- PDF.js
- Fabric.js
- jsPDF

---

## 📝 使用说明

### 对于开发者

**运行开发服务器**：
```bash
venv\Scripts\activate
python app.py
# 访问 http://localhost:5002
```

**打包应用**：
```bash
打包脚本.bat
# 或
pyinstaller --clean "PDF编辑器.spec"
```

### 对于最终用户

**运行应用**：
1. 双击 `PDF编辑器.exe`
2. 等待浏览器自动打开
3. 开始编辑PDF文件

**手动访问**：
- 如浏览器未自动打开
- 访问：http://localhost:5002

---

## 🎯 分发说明

### 分发文件
- **单个文件**：`dist\PDF编辑器.exe`
- **文件大小**：约20-40 MB

### 用户要求
- **操作系统**：Windows 7/8/10/11
- **浏览器**：Chrome、Edge、Firefox等现代浏览器
- **无需安装Python**
- **无需安装其他依赖**

### 安装说明
1. 下载 `PDF编辑器.exe`
2. 放在任意文件夹
3. 双击运行
4. 开始使用

---

## 🔍 故障排除

### 常见问题

**Q: 双击后没反应？**
- 检查5002端口是否被占用
- 以管理员身份运行
- 检查防火墙设置

**Q: 浏览器未自动打开？**
- 手动访问 http://localhost:5002
- 检查默认浏览器设置

**Q: 上传PDF失败？**
- 检查PDF文件大小（最大100MB）
- 确认PDF文件未损坏

**Q: 导出的PDF无法打开？**
- 刷新页面重试
- 检查原始PDF是否正常

---

## 📞 联系方式

### 技术支持
- 查看详细文档：`打包说明.md`
- 查看更新日志：`更新日志1-8.md`

### 反馈渠道
- 提交Issue
- 发送反馈邮件

---

## 📅 更新历史

### v1.0 (2025-11-24)
- ✅ 初始版本发布
- ✅ 端口修改为5002
- ✅ 添加版本号显示
- ✅ 支持打包为exe
- ✅ 隐藏控制台窗口
- ✅ 自动打开浏览器

---

## 📄 许可证

本项目仅供学习和个人使用。

---

## 🎉 致谢

感谢以下开源项目：
- Flask
- PDF.js
- Fabric.js
- jsPDF
- PyInstaller
- TailwindCSS

---

**PDF编辑器 v1.2 - 专业的PDF编辑工具** 🚀
