FROM python:3.12.5-slim

# 注意：也可以使用 alpine 版本使镜像更小 (python:3.12.5-alpine)
# slim: 基于 Debian，体积适中(~120MB)，兼容性好
# alpine: 基于 Alpine Linux，体积极小(~40MB)，但可能有兼容性问题

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DOCKER_ENV=true \
    DEBUG=false

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 只复制必要的应用程序代码，不包括静态文件
# static 目录将通过 volume 挂载
COPY server.py .
# 如果有多个 Python 文件，单独复制
# COPY utils.py .
# COPY config.py .
# 如果有其他必要的非静态文件目录，可以单独复制
# COPY other_necessary_dir/ ./other_necessary_dir/

# 创建 static 目录的挂载点
RUN mkdir -p /app/static

# 暴露端口
EXPOSE 5000

# 启动 Gunicorn 服务器
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "server:create_app()"] 