# PDF编辑器 - Web版

一个功能完整的基于Web的PDF编辑软件，支持局域网访问。

## 功能特性

- ✅ PDF文件上传（拖拽或点击）
- ✅ 页面预览与管理（拖拽排序、删除页面）
- ✅ 文字编辑（字体、颜色、大小、加粗、斜体）
- ✅ 图片删除
- ✅ 擦除工具（白色覆盖）
- ✅ 高亮显示
- ✅ 下划线
- ✅ 形状绘制（矩形、圆形等）
- ✅ 标尺与辅助线系统
- ✅ PDF生成与下载
- ✅ 前端处理，数据不上传服务器

## 技术栈

### 后端
- Python 3.8+
- Flask 2.3.0

### 前端
- PDF.js - PDF渲染
- Fabric.js - Canvas编辑
- jsPDF - PDF生成
- html2canvas - Canvas转图片
- Sortable.js - 拖拽排序
- TailwindCSS - 样式框架

## 安装与运行

### 1. 创建虚拟环境

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 运行应用

```bash
python app.py
```

### 4. 访问应用

- 本机访问: http://localhost:5000
- 局域网访问: http://[你的IP地址]:5000

获取局域网IP地址：
```bash
# Windows
ipconfig

# Linux/Mac
ifconfig
```

## 使用说明

1. **上传PDF**: 点击上传按钮或拖拽PDF文件到页面
2. **页面管理**: 在左侧预览面板拖拽调整页面顺序，右键或点击删除按钮删除页面
3. **编辑工具**: 使用顶部工具栏选择不同的编辑工具
4. **保存下载**: 编辑完成后点击"保存并下载"按钮

## 项目结构

```
pdf-editor4/
├── venv/                      # 虚拟环境
├── app.py                     # Flask主程序
├── requirements.txt           # Python依赖
├── README.md                  # 项目说明
├── static/                    # 静态资源
│   ├── css/
│   │   └── style.css         # 主样式文件
│   └── js/
│       ├── app.js            # 主应用逻辑
│       ├── pdfHandler.js     # PDF处理
│       ├── editor.js         # 编辑功能
│       ├── ruler.js          # 标尺和辅助线
│       └── pdfGenerator.js   # PDF生成
└── templates/
    └── index.html            # 主页面
```

## 注意事项

- 所有PDF处理在前端完成，数据不会上传到服务器
- 建议使用现代浏览器（Chrome、Firefox、Edge等）
- 处理大型PDF文件时可能需要较长时间

## License

MIT License
