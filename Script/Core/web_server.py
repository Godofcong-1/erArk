#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Web服务器模块，用于启动Flask服务器并处理请求
"""

# 重要: 在其他任何导入之前进行monkey patching
# 设置环境变量，禁用socket重用以避免端口冲突
import os
os.environ["EVENTLET_NO_GREENDNS"] = "yes"

# 导入标准库模块
import threading
import webbrowser
import json
import logging
import sys
import time
import socket
import psutil
from typing import List

# 导入Flask相关模块
from flask import Flask, render_template, jsonify, request, current_app
from flask_socketio import SocketIO

# 导入游戏核心模块
from Script.Core import cache_control, constant, game_type

# 获取全局缓存
cache = cache_control.cache

# 获取当前脚本的绝对路径，用于确定模板和静态文件的位置
current_dir = os.path.dirname(os.path.abspath(__file__))
# 项目根目录（从 Script/Core 向上两级）
project_root = os.path.dirname(os.path.dirname(current_dir))

# 检查是否在打包环境中运行
if hasattr(sys, '_MEIPASS'):
    # PyInstaller打包后的环境
    # 在打包后，templates和static文件夹应该在exe同级目录
    exe_dir = os.path.dirname(sys.executable)
    template_folder = os.path.join(exe_dir, 'templates')
    static_folder = os.path.join(exe_dir, 'static')
    print(f"检测到打包环境，使用exe目录: {exe_dir}")
else:
    # 开发环境
    template_folder = os.path.join(project_root, 'templates')
    static_folder = os.path.join(project_root, 'static')
    print(f"检测到开发环境，使用项目根目录: {project_root}")

print(f"模板文件夹路径: {template_folder}")
print(f"静态文件夹路径: {static_folder}")
print(f"模板文件夹存在: {os.path.exists(template_folder)}")
print(f"静态文件夹存在: {os.path.exists(static_folder)}")

# 创建Flask应用
app = Flask(__name__, 
            template_folder=template_folder, 
            static_folder=static_folder)

# 配置Flask应用
app.config['SECRET_KEY'] = 'erArk_web_secret_key'
app.config['DEBUG'] = False
app.config['USE_RELOADER'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True  # 传播异常以便更好地调试

# 初始化SocketIO，指定异步模式和超时配置
socketio = SocketIO(app, 
                    cors_allowed_origins="*",
                    async_mode='threading',
                    ping_timeout=60,
                    ping_interval=25,
                    logger=False,
                    engineio_logger=False)

# 游戏状态数据
game_state = {
    "text_content": [],  # 当前面板的文本内容
    "buttons": [],       # 当前面板的按钮
    "panel_id": None,    # 当前面板ID
    "skip_wait": False,  # 是否处于跳过等待模式
}

# 用于存储按钮点击响应
button_click_response = None
wait_response_triggered = False
input_response = None

# 全局服务器线程对象
server_thread = None
server_running = False
# 服务器端口
server_port = 5000
# 锁对象，用于线程同步
state_lock = threading.Lock()

@app.route('/')
def index():
    """
    渲染主页
    
    参数：无
    
    返回值类型：str
    功能描述：返回主页HTML内容
    """
    try:
        return render_template('index.html')
    except Exception as e:
        import traceback
        error_msg = f"渲染主页时出错: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        logging.error(error_msg)
        # 返回错误信息以便调试
        return f"<pre>{error_msg}</pre>", 500

@app.route('/api/get_state')
def get_state():
    """
    获取当前游戏状态
    
    参数：无
    
    返回值类型：JSON
    功能描述：返回包含当前游戏状态的JSON数据
    """
    with state_lock:
        return jsonify(game_state)

@app.route('/api/button_click', methods=['POST'])
def button_click():
    """
    处理按钮点击事件
    
    参数：无（从request.json获取数据）
    
    返回值类型：JSON
    功能描述：接收前端的按钮点击事件并返回处理结果
    """
    global button_click_response
    
    data = request.json or {}
    button_id = data.get('button_id')
    
    # 保存按钮ID为响应
    with state_lock:
        button_click_response = button_id
    
    # 记录按钮点击事件
    logging.info(f"按钮点击: {button_id}")
    
    return jsonify({"success": True})

@app.route('/api/wait_response', methods=['POST'])
def wait_response():
    """
    处理等待响应
    
    参数：无
    
    返回值类型：JSON
    功能描述：接收前端的等待响应事件并返回处理结果
    """
    global wait_response_triggered
    
    # print("[web_server] wait_response received")
    # 标记等待响应已触发
    with state_lock:
        wait_response_triggered = True
    
    logging.info("等待响应已触发")
    
    return jsonify({"success": True})


@app.route('/api/skip_wait', methods=['POST'])
def skip_wait():
    """处理跳过等待的请求"""
    global wait_response_triggered

    print("[web_server] skip_wait received")
    with state_lock:
        wframe_mouse = getattr(cache, "wframe_mouse", None)
        if wframe_mouse is not None:
            wframe_mouse.w_frame_skip_wait_mouse = 1
            setattr(wframe_mouse, "mouse_right", 1)
        setattr(cache, "text_wait", 0)
        wait_response_triggered = True
        game_state["skip_wait"] = True

    logging.info("跳过等待已触发")
    _emit_game_state_update()

    return jsonify({"success": True})

@app.route('/api/string_input', methods=['POST'])
def string_input():
    """
    处理字符串输入
    
    参数：无（从request.json获取数据）
    
    返回值类型：JSON
    功能描述：接收前端提交的字符串输入并返回处理结果
    """
    global input_response
    
    data = request.json or {}
    value = data.get('value')
    
    # 保存用户输入的字符串
    with state_lock:
        input_response = value
    
    logging.info(f"字符串输入: {value}")
    
    return jsonify({"success": True})

@app.route('/api/integer_input', methods=['POST'])
def integer_input():
    """
    处理整数输入
    
    参数：无（从request.json获取数据）
    
    返回值类型：JSON
    功能描述：接收前端提交的整数输入并返回处理结果
    """
    global input_response
    
    data = request.json or {}
    value = data.get('value')
    
    # 保存用户输入的整数
    try:
        with state_lock:
            input_response = int(value) if value is not None else 0
    except (ValueError, TypeError):
        with state_lock:
            input_response = 0
    
    logging.info(f"整数输入: {input_response}")
    
    return jsonify({"success": True})

@app.route('/api/get_image_paths')
def get_image_paths():
    """
    获取游戏所有图片文件的路径
    
    参数：无
    
    返回值类型：JSON
    功能描述：从era_image.py的image_path_data字典获取所有图片路径，返回图片路径列表
    """
    # 导入image_path_data字典
    from Script.Core.era_image import image_path_data
    
    # 处理图片路径，转换为相对路径格式
    image_paths = []
    
    # 根据环境确定基础目录
    if hasattr(sys, '_MEIPASS'):
        # 打包环境：使用exe所在目录
        base_dir = os.path.dirname(sys.executable)
    else:
        # 开发环境：使用项目根目录
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
    
    # 遍历image_path_data字典，将所有图片路径转换为相对于web根目录的路径
    for image_name, image_path in image_path_data.items():
        # 转换为相对于根目录的路径（以/开头）
        rel_path = image_path.replace(base_dir, '').replace('\\', '/')
        if not rel_path.startswith('/'):
            rel_path = '/' + rel_path
            
        # 添加到结果列表
        image_paths.append({
            "name": image_name,
            "path": rel_path
        })
    
    # 记录找到的图片数量
    logging.info(f"已找到 {len(image_paths)} 个图片文件")
    
    # 返回所有图片路径的列表
    return jsonify(image_paths)

@app.route('/favicon.ico')
def favicon():
    """
    提供网站图标
    
    参数：无
    
    返回值类型：Response对象
    功能描述：返回网站图标，使用游戏根目录下的image/logo.png
    """
    from flask import send_from_directory, abort
    import os
    
    # 根据环境确定基础目录和图片文件夹路径
    if hasattr(sys, '_MEIPASS'):
        # 打包环境：图片文件夹在exe同级目录
        base_dir = os.path.dirname(sys.executable)
        image_dir = os.path.join(base_dir, 'image')
    else:
        # 开发环境：使用项目根目录
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
        image_dir = os.path.join(base_dir, 'image')
    
    # 尝试提供logo.png作为网站图标
    try:
        return send_from_directory(image_dir, 'logo.png')
    except:
        # 如果文件不存在，返回204 No Content，避免404错误
        abort(204)

@app.route('/image/<path:filename>')
def serve_image(filename):
    """
    提供游戏图片文件
    
    参数：
    filename (str): 图片文件的相对路径
    
    返回值类型：Response对象
    功能描述：从游戏根目录下的image文件夹中提供图片文件
    """
    from flask import send_from_directory
    import os
    
    # 根据环境确定基础目录和图片文件夹路径
    if hasattr(sys, '_MEIPASS'):
        # 打包环境：图片文件夹在exe同级目录
        base_dir = os.path.dirname(sys.executable)
        image_dir = os.path.join(base_dir, 'image')
    else:
        # 开发环境：使用项目根目录
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
        image_dir = os.path.join(base_dir, 'image')
    
    # 使用send_from_directory提供文件，自动处理中文路径编码问题
    return send_from_directory(image_dir, filename)

@app.route('/api/get_font_config')
def get_font_config():
    """
    获取游戏所有字体配置数据
    
    参数：无
    
    返回值类型：JSON
    功能描述：从game_config.py中的config_font字典获取所有字体配置，返回字体配置列表
    """
    # 导入字体配置字典
    from Script.Config.game_config import config_font
    
    # 处理字体配置，转换为前端可用的格式
    font_configs = []
    
    # 遍历config_font字典，将所有字体配置转换为列表
    for font_id, font_config in config_font.items():
        # 添加到结果列表
        # 将字体配置转换为字典格式，如果某一项不存在，则赋值为空
        font_configs.append({
            "cid": font_id,  # 字体配置ID
            "name": getattr(font_config, 'name', ""),  # 字体名称
            "foreground": getattr(font_config, 'foreground', ""),  # 前景色
            "background": getattr(font_config, 'background', ""),  # 背景色
            "font": getattr(font_config, 'font', ""),  # 字体
            "font_size": getattr(font_config, 'font_size', ""),  # 字体大小
            "bold": getattr(font_config, 'bold', ""),  # 是否加粗
            "underline": getattr(font_config, 'underline', ""),  # 是否下划线
            "italic": getattr(font_config, 'italic', ""),  # 是否斜体
            "selectbackground": getattr(font_config, 'selectbackground', "")  # 选中背景色
        })
    
    # 记录找到的字体配置数量
    logging.info(f"已找到 {len(font_configs)} 个字体配置")
    
    # 返回所有字体配置的列表
    return jsonify(font_configs)

# SocketIO事件处理器
@socketio.on('connect')
def handle_connect():
    """
    处理客户端连接事件
    
    参数：无
    
    返回值类型：无
    功能描述：处理WebSocket客户端连接事件
    """
    logging.info("客户端已连接")
    # 连接后立即发送当前状态
    try:
        with state_lock:
            socketio.emit('game_state_update', game_state)
    except Exception as e:
        logging.error(f"发送初始游戏状态失败: {str(e)}")

@socketio.on('disconnect')
def handle_disconnect():
    """
    处理客户端断开连接事件
    
    参数：无
    
    返回值类型：无
    功能描述：处理WebSocket客户端断开连接事件
    """
    logging.info("客户端已断开连接")

@app.errorhandler(Exception)
def handle_exception(e):
    """
    全局异常处理器
    
    参数：
    e (Exception): 捕获的异常
    
    返回值类型：tuple
    功能描述：处理所有未捕获的异常并返回错误信息
    """
    import traceback
    error_msg = f"服务器内部错误: {str(e)}\n{traceback.format_exc()}"
    print(error_msg)
    logging.error(error_msg)
    return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

def find_free_port(start_port=5000, max_attempts=50):
    """
    查找可用的端口号
    
    参数：
    start_port (int): 起始端口号，默认5000
    max_attempts (int): 最大尝试次数，默认50
    
    返回值类型：int
    功能描述：从起始端口开始查找可用的端口号，最多尝试max_attempts次
    """
    print(f"正在查找可用端口，从端口 {start_port} 开始...")
    
    # 首先检查默认端口的占用情况
    is_occupied, process_info = check_port_usage(start_port)
    if is_occupied and process_info:
        print(f"检测到端口 {start_port} 被占用:")
        print(f"  进程名: {process_info['name']}")
        print(f"  进程ID: {process_info['pid']}")
        if process_info['cmdline']:
            print(f"  命令行: {process_info['cmdline']}")
        print(f"正在自动查找其他可用端口...")
    
    for port in range(start_port + 1, start_port + max_attempts):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # 设置socket选项，允许端口重用
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # 尝试绑定端口，成功则表示端口可用
            sock.bind(('0.0.0.0', port))
            sock.close()
            if port != start_port:
                print(f"已找到可用端口: {port}")
            else:
                print(f"端口 {port} 可用")
            return port
        except socket.error as e:
            # 端口被占用，尝试下一个
            if port == start_port:
                pass  # 已经在上面显示了详细信息
            else:
                logging.debug(f"端口 {port} 已被占用，继续尝试下一个端口")
            sock.close()
            continue
    
    # 如果前面的端口都被占用，尝试使用更高的端口范围
    print(f"端口 {start_port}-{start_port + max_attempts - 1} 都被占用，尝试使用更高的端口...")
    fallback_port = start_port + 1000 + (int(time.time()) % 1000)
    print(f"使用备用端口 {fallback_port}")
    return fallback_port

def check_port_usage(port):
    """
    检查指定端口的占用情况
    
    参数:
    port (int): 要检查的端口号
    
    返回值类型：tuple
    功能描述：返回(是否被占用, 占用进程信息)的元组
    """
    try:
        # 获取所有网络连接
        connections = psutil.net_connections()
        for conn in connections:
            laddr = getattr(conn, "laddr", None)
            status = getattr(conn, "status", None)
            conn_port = getattr(laddr, "port", None)
            if conn_port is None and isinstance(laddr, tuple) and len(laddr) > 1:
                conn_port = laddr[1]
            if conn_port == port and status == psutil.CONN_LISTEN:
                try:
                    # 获取进程信息
                    process = psutil.Process(conn.pid)
                    return True, {
                        'pid': conn.pid,
                        'name': process.name(),
                        'cmdline': ' '.join(process.cmdline()[:3])  # 只取前3个命令行参数
                    }
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    return True, {'pid': conn.pid, 'name': '未知进程', 'cmdline': ''}
        return False, None
    except Exception as e:
        logging.debug(f"检查端口占用时出错: {e}")
        return False, None

def update_input_request(current_input_request):
    """
    更新输入请求状态并向前端推送更新
    
    参数:
    current_input_request (dict): 当前输入请求数据，包含请求类型、提示文本和默认值
    
    返回值类型：无
    功能描述：更新游戏状态中的输入请求数据并通过WebSocket推送到前端
    """
    global game_state
    
    # 使用线程锁保护状态更新
    with state_lock:
        # 更新游戏状态数据中的输入请求部分
        # 如果 game_state 中尚不存在 input_request 键，则初始化它
        if "input_request" not in game_state:
            game_state["input_request"] = {}
            
        game_state["input_request"] = current_input_request
    
    # 使用函数来发送更新
    # 这会发送整个 game_state，包括更新后的 input_request
    _emit_game_state_update()
    
    # 日志记录，辅助调试
    logging.debug(f"输入请求已更新: {current_input_request}")


def update_game_state(elements, panel_id=None):
    """
    更新游戏状态并向前端推送更新
    
    参数:
    elements (list): 绘制元素列表
    panel_id (str): 当前面板ID，默认为None
    
    返回值类型：无
    功能描述：更新游戏状态数据并通过WebSocket推送到前端
    """
    global game_state
    
    highlight = []
    skip_wait_flag = bool(
        getattr(getattr(cache, "wframe_mouse", object()), "w_frame_skip_wait_mouse", False)
    )
    if elements:
        for elem in elements:
            if isinstance(elem, dict) and elem.get("type") in {"line_wait", "wait"}:
                text_preview = elem.get("text", "") or ""
                if isinstance(text_preview, str) and len(text_preview) > 20:
                    text_preview = text_preview[:17] + "..."
                highlight.append(
                    {
                        "type": elem.get("type"),
                        "wait_id": elem.get("wait_id"),
                        "text": text_preview,
                    }
                )
    if highlight:
        print(
            # f"[web_server] update_game_state panel={panel_id} wait_entries={highlight} total_elements={len(elements) if elements else 0}"
        )
    # 使用线程锁保护状态更新
    with state_lock:
        # 更新游戏状态数据
        game_state["text_content"] = elements if elements is not None else []
        game_state["panel_id"] = panel_id
        game_state["skip_wait"] = skip_wait_flag
        
        # 提取按钮元素
        buttons = []
        if elements:
            # 遍历元素列表，识别并提取按钮类型的元素
            for elem in elements:
                if isinstance(elem, dict) and elem.get("type") == "button":
                    buttons.append({
                        "id": elem.get("return_text"),
                        "text": elem.get("text"),
                        "style": elem.get("style", "standard")
                    })
        
        # 更新按钮列表
        game_state["buttons"] = buttons
    
    # 使用函数来发送更新
    _emit_game_state_update()
    
    # 日志记录，辅助调试
    logging.debug(f"游戏状态已更新: {len(elements) if elements else 0} 个元素")

def _emit_game_state_update():
    """
    发送游戏状态更新到前端
    
    参数：无
    
    返回值类型：无
    功能描述：通过WebSocket将游戏状态推送给所有连接的客户端
    """
    # 创建一个本地副本，避免长时间持有锁
    with state_lock:
        local_state = game_state.copy()
    
    try:
        # 在一个单独的线程中发送，避免阻塞主线程
        socketio.emit('game_state_update', local_state)
    except Exception as e:
        # 记录推送失败的错误
        logging.error(f"推送游戏状态失败: {str(e)}")

def get_button_response():
    """
    获取按钮点击响应
    
    参数：无
    
    返回值类型：str或None
    功能描述：返回用户点击的按钮ID，获取后清空
    """
    global button_click_response
    
    with state_lock:
        response = button_click_response
        button_click_response = None
    
    return response

def get_wait_response():
    """
    获取等待响应状态
    
    参数：无
    
    返回值类型：bool
    功能描述：返回等待响应是否被触发，获取后重置
    """
    global wait_response_triggered
    
    with state_lock:
        if wait_response_triggered:
            wait_response_triggered = False
            print("[web_server] wait_response detected")
            return True
        return False

def get_input_response():
    """
    获取输入响应
    
    参数：无
    
    返回值类型：str、int或None
    功能描述：返回用户输入的内容，获取后清空
    """
    global input_response
    
    with state_lock:
        response = input_response
        input_response = None
    
    return response

def start_server():
    """
    启动Web服务器
    
    参数：无
    
    返回值类型：int
    功能描述：在单独的线程中启动Flask应用服务器，返回实际使用的端口号
    """
    global server_running, server_thread, server_port
    
    # 避免重复启动
    if server_running:
        return server_port
    
    # 设置状态为运行中
    server_running = True
    
    # 设置Flask日志级别
    logging.getLogger('werkzeug').setLevel(logging.WARNING)  # 提高日志级别以减少输出
    # 设置Flask应用日志级别
    app.logger.setLevel(logging.DEBUG)
    # 启用详细的错误日志
    logging.basicConfig(level=logging.DEBUG)
    
    # 最大重试次数
    max_retries = 3
    host = '0.0.0.0'
    
    for attempt in range(max_retries):
        try:
            # 尝试查找可用端口
            server_port = find_free_port(start_port=5000 + attempt * 10)
            
            # 创建一个单独的线程启动服务器
            def run_server():
                """
                内部函数：运行服务器
                
                参数：无
                
                返回值类型：无
                功能描述：实际启动socketio服务器的函数
                """
                try:
                    # 使用线程模式运行SocketIO应用
                    socketio.run(app, host=host, port=server_port, debug=False, use_reloader=False, allow_unsafe_werkzeug=True)
                except Exception as e:
                    logging.error(f"服务器在端口 {server_port} 启动失败: {str(e)}")
                    global server_running
                    server_running = False
            
            # 确保之前的服务器线程已关闭
            if server_thread and server_thread.is_alive():
                try:
                    socketio.stop()
                    time.sleep(0.5)  # 给予服务器关闭的时间
                except:
                    pass
            
            # 在专用线程中启动服务器
            server_thread = threading.Thread(target=run_server)
            server_thread.daemon = True  # 设置为守护线程，主程序退出时自动结束
            server_thread.start()
            
            # 等待服务器启动
            time.sleep(2)
            
            # 检查服务器是否成功启动
            if server_running and server_thread.is_alive():
                print(f"游戏服务已启动，请访问: http://localhost:{server_port} 或 http://127.0.0.1:{server_port}")
                
                # 获取并显示局域网IP地址
                def get_lan_ip():
                    """获取局域网IP地址"""
                    import platform
                    import subprocess
                    
                    # 方法1: 使用UDP socket连接外部地址来获取路由IP
                    try:
                        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        s.connect(("8.8.8.8", 80))
                        ip = s.getsockname()[0]
                        s.close()
                        if ip and not ip.startswith("127.") and not ip.startswith("198.18."):
                            return [ip]
                    except:
                        pass
                    
                    # 方法2: 在Windows上使用更可靠的方法
                    if platform.system() == "Windows":
                        try:
                            # 尝试使用socket.getaddrinfo获取更准确的地址
                            host_name = socket.gethostname()
                            info = socket.getaddrinfo(host_name, None, socket.AF_INET, socket.SOCK_DGRAM)
                            ips = list(set([addr[4][0] for addr in info]))
                            valid_ips: List[str] = []
                            for ip in ips:
                                ip_str = str(ip)
                                if ip_str.startswith("192.168.") or ip_str.startswith("10.") or ip_str.startswith("172."):
                                    valid_ips.append(ip_str)
                            if valid_ips:
                                return valid_ips
                        except:
                            pass
                    
                    # 方法3: 尝试获取所有网络接口
                    try:
                        import subprocess
                        if platform.system() == "Windows":
                            # 使用ipconfig命令获取IP地址
                            result = subprocess.run(['ipconfig'], capture_output=True, text=True, encoding='gbk')
                            lines = result.stdout.split('\n')
                            ips = []
                            for i, line in enumerate(lines):
                                if "IPv4" in line or "IP Address" in line:
                                    # 提取IP地址
                                    parts = line.split(':')
                                    if len(parts) > 1:
                                        ip = parts[1].strip()
                                        if ip and (ip.startswith("192.168.") or ip.startswith("10.") or ip.startswith("172.")):
                                            ips.append(ip)
                            if ips:
                                return ips
                    except:
                        pass
                    
                    return []
                
                try:
                    lan_ips = get_lan_ip()
                    if lan_ips:
                        print(f"已自动检测到局域网ip，同一局域网内的设备也可以访问以下地址:")
                        for ip in lan_ips:
                            print(f"http://{ip}:{server_port}")
                    else:
                        logging.debug("无法自动获取局域网IP地址")
                except Exception as e:
                    logging.debug(f"获取IP地址时出错: {e}")
                
                # 自动打开浏览器
                try:
                    print("正在尝试自动打开默认浏览器...")
                    webbrowser.open(f'http://localhost:{server_port}')
                except:
                    # 打开浏览器失败，不阻止程序运行
                    pass
                
                return server_port
            else:
                print(f"服务器在端口 {server_port} 启动失败，尝试重新启动...")
                server_running = False
                
        except Exception as e:
            print(f"第 {attempt + 1} 次启动尝试失败: {str(e)}")
            server_running = False
            
        # 如果不是最后一次尝试，等待一下再重试
        if attempt < max_retries - 1:
            time.sleep(1)
    
    # 所有尝试都失败了
    print("服务器启动失败，已尝试多个端口但均无法启动")
    server_running = False
    raise Exception("无法启动Web服务器，请检查端口占用情况或系统防火墙设置")

def stop_server():
    """
    停止Web服务器
    
    参数：无
    
    返回值类型：无
    功能描述：停止运行中的Flask应用服务器
    """
    global server_running
    
    if not server_running:
        return
    
    # 设置状态为非运行
    server_running = False
    
    try:
        # 关闭socketio服务器
        socketio.stop()
    except Exception as e:
        logging.error(f"关闭服务器时发生错误: {str(e)}")
        
    print("游戏服务器已关闭")