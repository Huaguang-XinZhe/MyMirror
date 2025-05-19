from flask import Flask, request, make_response, abort, redirect
import logging
from pathlib import Path
import os
import sys

# 确定应用程序的基础路径
def get_base_path():
    # 检查是否是 Vercel 环境
    if os.environ.get('VERCEL_ENV'):
        # 在 Vercel 环境中使用当前目录
        base_path = Path(os.getcwd())
    # 检查是否是 PyInstaller 打包的环境
    elif getattr(sys, 'frozen', False):
        # 如果是打包环境，使用 _MEIPASS
        base_path = Path(sys._MEIPASS)
    else:
        # 如果是开发环境，使用当前目录
        base_path = Path(__file__).parent
    return base_path

# 获取基础路径
BASE_PATH = get_base_path()
# GitHub Pages 静态资源的基础 URL
STATIC_BASE_URL = "https://huaguang-xinzhe.github.io/MyMirror-Static"

def setup_logger():
    # 创建日志记录器
    logger = logging.getLogger("mirror_site")
    logger.setLevel(logging.INFO)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 检查是否是 Vercel 环境或打包环境，非这两种环境才创建文件日志
    if not (os.environ.get('VERCEL_ENV') or getattr(sys, 'frozen', False)):
        # 创建日志目录
        log_dir = Path(__file__).parent / "logs"
        log_dir.mkdir(exist_ok=True)
        
        # 创建文件处理器
        file_handler = logging.FileHandler(log_dir / "server.log", encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

logger = setup_logger()

app = Flask(__name__)

# 将自定义日志记录器设置为 Flask 的日志记录器
# 这样 Flask 内部的日志也会使用我们的配置
app.logger = logger

# 创建一个全局变量用于存储最近的请求体
last_language_request_body = None

# 默认 snippet_lang
DEFAULT_SNIPPET_LANG = 'react-v4'

def get_snippet_lang():
    """
    获取请求体中的 snippet_lang
    Returns:
        str: snippet_lang 的值
        None: 如果没有请求体
    """
    if last_language_request_body is None:
        return None
    return last_language_request_body.get('snippet_lang')

# 清理 snippet_lang
def clear_snippet_lang():
    global last_language_request_body
    last_language_request_body = None

def handle_download(path):
    """
    处理下载请求，重定向到 GitHub Pages 上的 zip 文件
    
    Args:
        path: 请求路径，例如 'plus/templates/catalyst/download'
        
    Returns:
        Response: 重定向到 GitHub Pages 上的 zip 文件
    """
    logger.info(f"处理下载请求: {path}")
    
    # 去掉路径末尾的 '/download'
    base_path = path[:-9]  # 移除 '/download'
    
    # 提取最后一个路径部分作为文件名
    parts = base_path.split('/')
    filename = parts[-1] + '.zip'
    
    # 构建 GitHub Pages 上的 zip 文件 URL
    zip_url = f"{STATIC_BASE_URL}/{base_path}/{filename}"
    
    logger.info(f"重定向到 GitHub Pages 上的文件: {zip_url}")
    
    # 重定向到 GitHub Pages
    return redirect(zip_url)

@app.route('/')
def index():
    # 重定向到 GitHub Pages 上的主页
    return redirect(f"{STATIC_BASE_URL}/plus/index.html")

@app.route('/<path:path>')
def catch_all(path):
    logger.info(f"访问路径: {path}")
    
    # 处理下载请求
    if path.endswith('/download'):
        return handle_download(path)
    
    # 如果路径中包含后缀，那就重定向到 GitHub Pages
    if '.' in path:
        return redirect(f"{STATIC_BASE_URL}/{path}")
    
    # 如果路径中不包含后缀，那就要分情况判断
    # 获取头部中的 x-inertia 字段
    x_inertia = request.headers.get('x-inertia')
    
    # 如果存在 x-inertia，说明是请求 JSON 数据
    if x_inertia:
        # 获取 snippet_lang
        snippet_lang = get_snippet_lang()
        clear_snippet_lang() # 即时清理，避免影响后续处理！
        
        # 构建 JSON 文件的 URL
        if snippet_lang:
            json_url = f"{STATIC_BASE_URL}/{path}/{snippet_lang}.json"
        else:
            json_url = f"{STATIC_BASE_URL}/{path}/{DEFAULT_SNIPPET_LANG}.json"
            # 如果文件不存在，可能需要处理 index.json 的情况
            # 但这需要在客户端处理，因为我们无法检查 GitHub Pages 上文件是否存在
        
        # 重定向到 GitHub Pages 上的 JSON 文件
        # 注意：这里可能需要更复杂的处理，因为重定向会改变请求头
        # 可能需要在前端代码中直接请求 GitHub Pages
        return redirect(json_url)
    
    # 否则，重定向到 GitHub Pages 上的 index.html
    return redirect(f"{STATIC_BASE_URL}/{path}/index.html")


@app.route('/plus/ui-blocks/language', methods=['PUT'])
def language_redirect():
    """
    处理 /plus/ui-blocks/language 路径的PUT请求
    返回303重定向响应，根据referer重定向到其他路径
    """
    global last_language_request_body
    
    logger.info("收到 /plus/ui-blocks/language 的PUT请求")
    
    try:
        # 获取请求体并存储在全局变量中
        body = request.get_json(silent=True)
        if body is None:
            # 如果不是 JSON 格式，尝试获取原始数据
            body = request.get_data(as_text=True)
            logger.info(f"请求体不是 JSON 格式，原始内容: {body}")
        else:
            logger.info(f"请求体内容: {body}")
        
        # 存储请求体到全局变量
        last_language_request_body = body
        logger.info(f"已存储请求体到全局变量")
        
        # 获取 referer
        referer = request.headers.get('referer', '')
        logger.info(f"请求的 referer: {referer}")
        
        # 如果没有 referer，返回 404
        if not referer:
            logger.warning("请求没有 referer，返回 404")
            abort(404)
        
        # 构造重定向响应
        response = make_response('', 303)
        response.headers['location'] = referer
        
        logger.info(f"重定向到: {referer}")
        return response
    except Exception as e:
        logger.error(f"处理请求时发生错误: {str(e)}")
        abort(500)


if __name__ == '__main__':
    logger.info("服务器启动")
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
