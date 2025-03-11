from flask import Flask, send_from_directory, request, make_response, abort
import logging
from pathlib import Path

def setup_logger():
    # 创建日志目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # 配置日志
    logger = logging.getLogger("mirror_site")
    # logger 和 handler 不一样，这里和下边都设置日志级别是为了保证控制台和文件日志的一致性！
    logger.setLevel(logging.INFO)

    # 创建文件处理器
    file_handler = logging.FileHandler(log_dir / "server.log", encoding="utf-8")
    file_handler.setLevel(logging.INFO)

    # 创建格式化器
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # 添加处理器到日志记录器
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
    处理下载请求，返回对应目录下的 zip 文件
    
    Args:
        path: 请求路径，例如 'plus/templates/catalyst/download'
        
    Returns:
        Response: 包含 zip 文件的响应，Content-Type 为 application/octet-stream
    """
    logger.info(f"处理下载请求: {path}")
    
    # 去掉路径末尾的 '/download'
    base_path = path[:-9]  # 移除 '/download'
    
    # 提取最后一个路径部分作为文件名
    parts = base_path.split('/')
    filename = parts[-1] + '.zip'
    
    # 构建 zip 文件路径
    zip_path = Path('static') / base_path / filename
    
    logger.info(f"尝试下载文件: {zip_path}")
    
    # 检查文件是否存在
    if not zip_path.exists():
        logger.warning(f"下载文件不存在: {zip_path}")
        abort(404)
    
    # 读取文件内容
    with open(zip_path, 'rb') as f:
        file_data = f.read()
    
    # 构造响应
    response = make_response(file_data)
    response.headers['Content-Type'] = 'application/octet-stream'
    response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    logger.info(f"成功返回下载文件: {filename}")
    return response

@app.route('/')
def index():
    return send_from_directory('static/plus', 'index.html')

@app.route('/<path:path>')
def catch_all(path):
    logger.info(f"访问路径: {path}")
    
    # 处理下载请求
    if path.endswith('/download'):
        return handle_download(path)
    
    # 如果路径中包含后缀，那就直接提供文件
    if '.' in path:
        return send_from_directory('static', path)
    
    # 如果路径中不包含后缀，那就要分情况判断
    # 获取头部中的 x-inertia 字段
    x_inertia = request.headers.get('x-inertia')
    
    # 如果存在 x-inertia，说明是请求 JSON 数据
    if x_inertia:
        # 获取 snippet_lang
        snippet_lang = get_snippet_lang()
        clear_snippet_lang() # 即时清理，避免影响后续处理！
        
        if snippet_lang:
            file_path = Path('static') / path / f"{snippet_lang}.json"
        else:
            file_path = Path('static') / path / f"{DEFAULT_SNIPPET_LANG}.json"
            # 如果文件不存在，就用 index.json
            if not file_path.exists():
                file_path = Path('static') / path / 'index.json'

        if not file_path.exists():
            logger.warning(f"文件不存在: {file_path}")
            abort(404)
        
        # 读取 JSON 文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            json_data = f.read()
            
        # 构造自定义响应
        response = make_response(json_data)
        response.headers['content-type'] = 'application/json'
        response.headers['x-inertia'] = 'true'
        return response
    
    # 否则，返回 index.html
    return send_from_directory(f'static/{path}', 'index.html')


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
    app.run(debug=True)
