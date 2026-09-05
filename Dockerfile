# 使用官方 Python 镜像（基于 Debian）
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖：gcc, make, gzip, wget, libc6-dev 等
# libc6-dev 提供编译 C 程序所需的标准头文件和库
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    make \
    gzip \
    wget \
    libc6-dev \
    && rm -rf /var/lib/apt/lists/*

# 将本地 RTKLIB 源码包复制到镜像内
COPY rtklib_2.4.3+dfsg1.orig.tar.gz /tmp/rtklib.tar.gz

# 解压并编译 convbin 工具（路径为 app/convbin/gcc）
RUN tar -xzf /tmp/rtklib.tar.gz -C /tmp/ \
    && cd /tmp/rtklib-*/app/convbin/gcc \
    && make \
    && cp convbin /usr/local/bin/ \
    && rm -rf /tmp/rtklib* /tmp/rtklib.tar.gz

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY app/ ./app/

# 暴露 Web 端口
EXPOSE 5000

# 设置环境变量（可被 docker run -e 覆盖）
ENV DATA_DIR=/data
ENV LOG_DIR=/logs
ENV SOURCE_PRIORITY="wuhan_rnx4,ign,bkg"
ENV AUTO_DOWNGRADE=true

# 创建数据目录
RUN mkdir -p $DATA_DIR $LOG_DIR

# 启动应用
CMD ["python", "app/app.py"]