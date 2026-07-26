# PDF文件编辑软件

一个基于Python Flask的Web应用程序，提供PDF文件的多种编辑功能，包括去红头、去公章、转换格式等。

## 功能特性

- **文件上传**: 支持拖拽上传PDF和图片文件
- **文件预览**: 支持PDF和图片文件的在线预览
- **去红头及公章**: 智能识别并移除PDF中的红头文字和公章
- **去公章**: 仅移除PDF中的公章，保留其他内容
- **转图片后去红头及公章**: 将文本型PDF转为图片型后处理
- **去背景**: 清理扫描型PDF的背景杂色，增强文字对比度
- **转Word**: 将PDF转换为Word文档，保持原有格式
- **图片转PDF**: 将多张图片合并为A4格式的PDF文件

## 系统要求

- Python 3.7+
- Windows/Linux/macOS

## 安装步骤

### 1. 创建虚拟环境

```bash
# 创建虚拟环境
python -m venv pdf_editor_env

# 激活虚拟环境
# Windows:
pdf_editor_env\Scripts\activate
# Linux/macOS:
source pdf_editor_env/bin/activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 安装额外依赖

#### Windows系统
下载并安装 Tesseract OCR:
- 访问 https://github.com/UB-Mannheim/tesseract/wiki
- 下载Windows安装包并安装
- 将安装路径添加到系统PATH环境变量

#### Linux系统
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-chi-sim  # 中文支持
```

#### macOS系统
```bash
brew install tesseract
```

## 运行应用

```bash
python app.py
```

应用将在 `http://localhost:5000` 启动，支持局域网访问。

## 使用说明

### 1. 文件上传
- 点击上传区域或拖拽文件到指定区域
- 支持PDF和图片文件（JPG、PNG、BMP、TIFF）
- 系统会自动识别PDF类型（文本型或扫描型）

### 2. 文件管理
- 上传后的文件会显示在文件列表中
- 每个文件显示文件名、类型和大小
- 可以预览或删除单个文件

### 3. 功能操作
- **预览**: 查看PDF页面或图片内容，支持点击放大
- **去红头及公章**: 根据PDF类型采用不同处理方法
- **去公章**: 仅移除公章，保留其他内容
- **转图片后去红头及公章**: 先转换为图片型PDF再处理
- **去背景**: 清理背景杂色，适用于扫描型PDF
- **转Word**: 转换为Word格式，保持原有布局
- **图片转PDF**: 将图片合并为PDF文件

### 4. 文件下载
- 处理完成后文件会自动下载
- 单个文件直接下载
- 多个文件会打包为ZIP文件下载

## 技术架构

- **后端**: Flask + Python
- **前端**: HTML5 + CSS3 + JavaScript
- **PDF处理**: PyMuPDF (fitz)
- **图像处理**: OpenCV + Pillow
- **文档转换**: python-docx + reportlab

## 文件结构

```
pdf-new/
├── app.py                 # 主应用文件
├── file_manager.py        # 文件管理模块
├── pdf_processor.py       # PDF处理模块
├── image_processor.py     # 图像处理模块
├── requirements.txt       # 依赖包列表
├── templates/
│   └── index.html        # Web界面模板
├── uploads/              # 上传文件目录
├── processed/            # 处理后文件目录
└── README.md            # 说明文档
```

## 注意事项

1. **红头文字识别**: 程序会自动识别PDF首页上部的红色文字区域
2. **公章处理**: 识别红色圆形图案，处理时保留下方的黑色文字
3. **文件类型**: 系统根据PDF首页文本量判断是文本型还是扫描型
4. **内存使用**: 处理大文件时可能占用较多内存
5. **网络访问**: 应用支持局域网访问，其他设备可通过IP地址访问

## 故障排除

### 常见问题

1. **Tesseract未找到**
   - 确保Tesseract已正确安装并添加到PATH
   - Windows用户检查环境变量设置

2. **内存不足**
   - 处理大文件时关闭其他应用程序
   - 考虑分批处理多个文件

3. **文件上传失败**
   - 检查文件大小是否超过100MB限制
   - 确认文件格式是否支持

4. **处理结果不理想**
   - 红头和公章的识别基于颜色和形状特征
   - 复杂布局的文档可能需要手动调整

## 许可证

本项目仅供学习和研究使用。

## 更新日志

### v1.0.0
- 初始版本发布
- 支持基本的PDF编辑功能
- Web界面和文件管理
- 支持局域网访问