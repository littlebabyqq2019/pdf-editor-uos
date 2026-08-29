# 精简版Dockerfile - 模仿之前的400MB镜像
# 只复制必要文件，不复制整个项目
FROM docker.m.daocloud.io/library/python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_APP=app.py \
    FLASK_ENV=production \
    TZ=Asia/Shanghai

# 安装系统依赖
# fonts-wqy-microhei/fonts-wqy-zenhei: 中文字体，watermark_processor.py 渲染中文水印
# 依赖 /usr/share/fonts/truetype/wqy/ 下的字体文件，缺失时会报错
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgl1 \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libtiff-dev \
    libwebp-dev \
    tzdata \
    fonts-wqy-microhei \
    fonts-wqy-zenhei \
    fontconfig \
    && fc-cache -f -v \
    && ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && echo "Asia/Shanghai" > /etc/timezone \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 合并requirements
COPY requirements.txt /tmp/requirements_main.txt
COPY pdf-new/requirements.txt /tmp/requirements_pdf_new.txt
COPY pdf-editor（draw）/requirements.txt /tmp/requirements_pdf_editor.txt

# 安装Python依赖
# cache bust: 2026-08-03 修复 GHA 构建缓存返回空 site-packages 导致的 ModuleNotFoundError 问题
RUN cat /tmp/requirements_main.txt /tmp/requirements_pdf_new.txt /tmp/requirements_pdf_editor.txt | \
    grep -v "^#" | grep -v "^$" | grep -v "pyinstaller" | sort -u > /tmp/requirements_final.txt && \
    pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r /tmp/requirements_final.txt && \
    rm -rf /tmp/requirements_*.txt && \
    # 清理pip缓存和编译文件
    find /usr/local/lib/python3.11 -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true && \
    find /usr/local/lib/python3.11 -type f -name '*.pyc' -delete && \
    find /usr/local/lib/python3.11 -type f -name '*.pyo' -delete

# 安装 Aspose.Words for Python (Linux x86_64 版本)
COPY Aspose.Words/python专用whl包/aspose_words-25.9.0-py3-none-manylinux1_x86_64.whl /tmp/
RUN pip install --no-cache-dir /tmp/aspose_words-25.9.0-py3-none-manylinux1_x86_64.whl && \
    rm /tmp/aspose_words-25.9.0-py3-none-manylinux1_x86_64.whl

# 构建期校验：确保关键依赖已真正安装，避免因构建缓存异常而悄悄产出缺依赖的镜像
RUN python -c "import flask, PyPDF2, PIL, cv2, numpy, docx, reportlab, fitz, skimage, aspose.words; print('[build-check] 依赖校验通过')"

# 只复制必要的应用文件（不复制整个项目！）
COPY app.py /app/
COPY pdf_processor.py /app/
COPY image_processor.py /app/
COPY file_manager.py /app/
COPY watermark_processor.py /app/
COPY aspose.words.lic /app/

# 复制模板和静态文件
COPY templates/ /app/templates/
COPY static/ /app/static/

# 复制pdf-new模块（只复制必要文件）
COPY pdf-new/app.py /app/pdf-new/app.py
COPY pdf-new/file_manager.py /app/pdf-new/file_manager.py
COPY pdf-new/pdf_processor.py /app/pdf-new/pdf_processor.py
COPY pdf-new/image_processor.py /app/pdf-new/image_processor.py
COPY pdf-new/templates/ /app/pdf-new/templates/

# 复制pdf-editor模块（只复制必要文件）
COPY pdf-editor（draw）/app.py /app/pdf-editor（draw）/app.py
COPY pdf-editor（draw）/static/ /app/pdf-editor（draw）/static/
COPY pdf-editor（draw）/templates/ /app/pdf-editor（draw）/templates/

# 创建必要的目录
RUN mkdir -p /app/uploads /app/processed /app/config

# 设置权限
RUN chmod -R 755 /app && \
    chmod -R 777 /app/uploads /app/processed /app/config

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/', timeout=5)" || exit 1

CMD ["python", "app.py"]
