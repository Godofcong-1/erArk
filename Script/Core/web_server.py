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

# 导入Flask相关模块
from flask import Flask, render_template, jsonify, request, current_app
from flask_socketio import SocketIO

# 导入游戏核心模块
from Script.Core import cache_control, constant, game_type

# 获取全局缓存
cache = cache_control.cache

# 创建Flask应用
app = Flask(__name__, 
            template_folder='../../templates', 
            static_folder='../../static')

# 配置Flask应用
app.config['SECRET_KEY'] = 'erArk_web_secret_key'
app.config['DEBUG'] = False
app.config['USE_RELOADER'] = False

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
    return render_template('index.html')

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
    
    data = request.json
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
    
    # 标记等待响应已触发
    with state_lock:
        wait_response_triggered = True
    
    logging.info("等待响应已触发")
    
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
    
    data = request.json
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
    
    data = request.json
    value = data.get('value')
    
    # 保存用户输入的整数
    try:
        with state_lock:
            input_response = int(value)
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
    
    # 获取游戏根目录的绝对路径
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
    
    # 构建完整的图片文件夹路径
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

def find_free_port(start_port=5000, max_attempts=10):
    """
    查找可用的端口号
    
    参数：
    start_port (int): 起始端口号，默认5000
    max_attempts (int): 最大尝试次数，默认10
    
    返回值类型：int
    功能描述：从起始端口开始查找可用的端口号，最多尝试max_attempts次
    """
    for port in range(start_port, start_port + max_attempts):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # 尝试绑定端口，成功则表示端口可用
            sock.bind(('0.0.0.0', port))
            sock.close()
            return port
        except socket.error:
            # 端口被占用，尝试下一个
            logging.info(f"端口 {port} 已被占用，尝试下一个端口")
            continue
    
    # 如果都失败了，返回一个随机端口
    return start_port + 1000 + (int(time.time()) % 1000)

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
    
    # 使用线程锁保护状态更新
    with state_lock:
        # 更新游戏状态数据
        game_state["text_content"] = elements if elements is not None else []
        game_state["panel_id"] = panel_id
        
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
    
    返回值类型：无
    功能描述：在单独的线程中启动Flask应用服务器
    """
    global server_running, server_thread, server_port
    
    # 避免重复启动
    if server_running:
        return
    
    # 设置状态为运行中
    server_running = True
    
    # 设置Flask日志级别为WARNING，减少控制台输出
    logging.getLogger('werkzeug').setLevel(logging.DEBUG)
    
    # 尝试查找可用端口
    server_port = find_free_port()
    host = '0.0.0.0'
    
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
            logging.error(f"服务器启动失败: {str(e)}")
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
    
    # 自动打开浏览器
    try:
        webbrowser.open(f'http://localhost:{server_port}')
    except:
        # 打开浏览器失败，不阻止程序运行
        pass
    
    print(f"游戏服务已启动，请访问: http://localhost:{server_port}")
    return server_port

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