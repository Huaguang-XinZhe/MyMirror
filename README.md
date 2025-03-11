# MyMirror

MyMirror 是一个基于 Flask 的网站镜像服务，用于本地镜像和访问网站内容。该项目可以缓存和提供静态资源，并支持特定 API 请求的模拟响应。

## 功能特点

- 静态资源镜像：提供对静态文件（HTML、CSS、JS、图片等）的本地访问
- 智能路由处理：根据请求路径和头信息返回适当的内容
- 语言切换支持：处理语言切换请求并保持用户偏好
- 文件下载功能：支持以 `/download` 结尾的路径请求，返回对应的 zip 文件
- 详细日志记录：记录所有请求和响应信息，便于调试和分析

## 项目结构

```
MyMirror/
├── logs/                # 日志文件目录
├── static/              # 静态资源目录
│   ├── plus/            # 主要内容目录
│   └── plus-assets/     # 资源文件目录
├── server.py            # 主服务器脚本
├── requirements.txt     # 项目依赖
└── README.md            # 项目说明文档
```

## 安装与使用

### 环境要求

- Python 3.8 或更高版本
- 依赖包（见 requirements.txt）

### 安装步骤

1. 克隆或下载本项目到本地

2. 创建并激活虚拟环境（可选但推荐）

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

```bash
python -m venv .venv
source .venv/bin/activate
```

3. 安装依赖包

```powershell
pip install -r requirements.txt
```

### 运行服务器

```powershell
python server.py
```

服务器默认在 http://127.0.0.1:5000 启动，可以通过浏览器访问。

## 主要路由说明

- `/` - 主页
- `/<path>` - 通用路由，根据路径和请求头返回适当内容
- `/plus/ui-blocks/language` - 处理语言切换请求
- `*/download` - 处理文件下载请求，返回对应的 zip 文件

## 下载功能使用

访问以 `/download` 结尾的路径将触发文件下载。例如：

- `/plus/templates/catalyst/download` 将下载 `/static/plus/templates/catalyst/catalyst.zip` 文件

## 日志

服务器日志保存在 `logs/server.log` 文件中，记录了所有请求和响应信息，以及可能的错误。
