# 使用 Python 3.13 作为基础镜像
FROM python:3.13-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TZ=Asia/Shanghai \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100

# 更换为国内 apt 镜像源（清华大学）
RUN sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list.d/debian.sources && \
    sed -i 's|security.debian.org|mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list.d/debian.sources

# 配置 pip 使用国内镜像源
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn

# 安装系统依赖（一次性完成，减少层数）
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 先复制依赖文件（利用 Docker 缓存）
COPY requirements.txt .

# 分步安装依赖，先安装基础依赖，再安装大型库
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# 复制项目文件（放在最后，避免代码改动导致重新安装依赖）
COPY . .

# 创建必要的目录
RUN mkdir -p /app/data /app/record /app/image

# 启动命令
CMD ["python", "main.py"]
