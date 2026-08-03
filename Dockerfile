# 适配国产统信UOS系统 (arm64架构) 的Dockerfile
# 使用arm64架构的Python基础镜像
# 注意：如果网络问题，请配置Docker镜像加速器
# 注意：ofd2img>=0.1.0 要求 Python>=3.10，不可降回 3.9
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_APP=app.py \
    FLASK_ENV=production \
    TZ=Asia/Shanghai

# 安装系统依赖
# 这些是OpenCV、Pillow和其他图像处理库所需的系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    # OpenCV依赖
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgl1 \
    # Pillow依赖
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libtiff-dev \
    libwebp-dev \
    # 其他工具
    tzdata \
    && ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && echo "Asia/Shanghai" > /etc/timezone \
    && rm -rf /var/lib/apt/lists/*

# 合并所有requirements.txt并去重
# 首先复制requirements文件
COPY requirements.txt /tmp/requirements_main.txt
COPY pdf-new/requirements.txt /tmp/requirements_pdf_new.txt
COPY pdf-editor（draw）/requirements.txt /tmp/requirements_pdf_editor.txt

# 合并并安装Python依赖
RUN cat /tmp/requirements_main.txt /tmp/requirements_pdf_new.txt /tmp/requirements_pdf_editor.txt | \
    grep -v "^#" | grep -v "^$" | sort -u > /tmp/requirements_merged.txt && \
    # 移除pyinstaller，Docker环境不需要
    grep -v "pyinstaller" /tmp/requirements_merged.txt > /tmp/requirements_final.txt && \
    pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r /tmp/requirements_final.txt && \
    rm -rf /tmp/requirements_*.txt

# 复制应用代码
COPY . /app/

# 创建必要的目录
RUN mkdir -p /app/uploads /app/processed /app/static /app/templates

# 设置目录权限
RUN chmod -R 755 /app && \
    chmod -R 777 /app/uploads /app/processed

# 暴露应用端口
EXPOSE 5000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/', timeout=5)" || exit 1

# 启动应用
CMD ["python", "app.py"]
