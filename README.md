# MyMirror

基于 Flask 的静态网站镜像服务，适合生产环境部署。

## 功能特点

- 提供静态文件服务
- 支持 JSON API 响应
- 支持文件下载功能
- 适配 Docker 容器化部署

## 部署方式

### 使用 Docker Compose（推荐）

1. 确保安装了 Docker 和 Docker Compose

2. 启动服务：

```bash
docker compose up -d
```

3. 访问服务：http://localhost

### 手动部署

1. 安装依赖：

```bash
pip install -r requirements.txt
```

2. 启动服务：

```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 server:create_app()
```

## 环境变量配置

- `HOST`: 监听地址，默认 0.0.0.0
- `PORT`: 监听端口，默认 5000
- `DEBUG`: 是否开启调试模式，默认 false
- `DOCKER_ENV`: 是否在 Docker 环境中运行，默认 false

## 目录结构

- `server.py`: 主应用程序
- `static/`: 静态文件目录
- `Dockerfile`: Docker 镜像构建文件
- `compose.yml`: Docker Compose 配置文件
- `nginx.conf`: Nginx 配置文件
- `requirements.txt`: 项目依赖
