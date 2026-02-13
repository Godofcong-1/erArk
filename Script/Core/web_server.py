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

# 结算管理器实例（延迟初始化）
_settlement_manager = None

def get_settlement_manager():
    """
    获取结算管理器实例（单例模式）
    
    返回值类型：SettlementManager
    功能描述：返回全局结算管理器实例，如果不存在则创建
    """
    global _settlement_manager
    if _settlement_manager is None:
        from Script.System.Web_Draw_System.settlement_manager import SettlementManager
        _settlement_manager = SettlementManager()
    return _settlement_manager

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
    功能描述：返回游戏主页面，所有面板都在同一个页面中动态渲染
    """
    try:
        return render_template('index.html')
    except Exception as e:
        import traceback
        error_msg = f"渲染主页时出错: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        logging.error(error_msg)
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

@app.route('/api/toggle_extra_info_section', methods=['POST'])
def toggle_extra_info_section():
    """
    切换交互对象附加信息栏位的展开/收起状态
    
    参数：section - 栏位名称 (clothing, body, group_sex, hidden_sex)
    
    返回值类型：JSON
    功能描述：切换指定栏位的显示状态
    """
    from Script.Core import cache_control
    cache = cache_control.cache
    
    data = request.json or {}
    section = data.get('section')
    
    # 栏位索引映射
    section_index_map = {
        'clothing': 1,  # cache.scene_panel_show[1]
        'body': 2,      # cache.scene_panel_show[2]
    }
    
    if section in section_index_map:
        index = section_index_map[section]
        if hasattr(cache, 'scene_panel_show') and index < len(cache.scene_panel_show):
            cache.scene_panel_show[index] = not cache.scene_panel_show[index]
            logging.info(f"切换栏位 {section} 状态为: {cache.scene_panel_show[index]}")
            return jsonify({"success": True})
    
    # 群交和隐奸栏位由系统状态控制，不需要手动切换
    return jsonify({"success": True})

@app.route('/api/toggle_detailed_dirty', methods=['POST'])
def toggle_detailed_dirty():
    """
    切换详细污浊显示状态
    
    参数：无
    
    返回值类型：JSON
    功能描述：切换是否显示详细污浊文本，并返回更新后的附加信息数据
    """
    from Script.Core import cache_control
    from Script.System.Web_Draw_System.status_panel import StatusPanel
    cache = cache_control.cache
    
    if hasattr(cache, 'all_system_setting') and hasattr(cache.all_system_setting, 'draw_setting'):
        cache.all_system_setting.draw_setting[10] = not cache.all_system_setting.draw_setting[10]
        logging.info(f"切换详细污浊显示为: {cache.all_system_setting.draw_setting[10]}")
        
        # 获取更新后的附加信息数据
        status_panel = StatusPanel()
        character_id = cache.character_data[0].target_character_id if hasattr(cache.character_data[0], 'target_character_id') else 0
        extra_info = status_panel.get_target_extra_info(character_id)
        
        return jsonify({
            "success": True,
            "extra_info": extra_info
        })
    
    return jsonify({"success": False, "error": "无法访问系统设置"})

@app.route('/api/toggle_all_body_parts', methods=['POST'])
def toggle_all_body_parts():
    """
    切换全部位显示状态
    
    参数：无
    
    返回值类型：JSON
    功能描述：切换是否始终显示所有身体部位按钮（不需要鼠标悬停），并返回更新后的附加信息数据和交互对象信息
    """
    from Script.Core import cache_control
    from Script.System.Web_Draw_System.status_panel import StatusPanel
    cache = cache_control.cache
    
    if hasattr(cache, 'all_system_setting') and hasattr(cache.all_system_setting, 'draw_setting'):
        # 使用draw_setting[18]存储全部位显示状态
        current_value = cache.all_system_setting.draw_setting.get(18, 0)
        cache.all_system_setting.draw_setting[18] = 0 if current_value else 1
        logging.info(f"切换全部位显示为: {cache.all_system_setting.draw_setting[18]}")
        
        # 获取更新后的附加信息数据
        status_panel = StatusPanel()
        character_id = cache.character_data[0].target_character_id if hasattr(cache.character_data[0], 'target_character_id') else 0
        extra_info = status_panel.get_target_extra_info(character_id)
        
        # 获取更新后的交互对象信息（包含可选部位列表）
        target_info = status_panel.get_target_info(character_id)
        
        return jsonify({
            "success": True,
            "extra_info": extra_info,
            "target_info": target_info
        })
    
    return jsonify({"success": False, "error": "无法访问系统设置"})

@app.route('/api/quick_use_drug', methods=['POST'])
def quick_use_drug():
    """
    快速使用药剂（理智药或精力剂）
    
    参数：drug_type - 药剂类型 ('sanity' 或 'semen')
    
    返回值类型：JSON
    功能描述：快速使用玩家拥有的理智药或精力剂
    数值变化通过 cache.web_value_changes 传递给前端显示浮动文本
    """
    import time
    from Script.Core import cache_control
    from Script.UI.Panel.see_item_info_panel import use_drug, auto_use_sanity_drug
    cache = cache_control.cache
    
    data = request.json or {}
    drug_type = data.get('drug_type')
    
    if drug_type not in ['sanity', 'semen']:
        return jsonify({"success": False, "message": "无效的药剂类型"})
    
    try:
        pl_data = cache.character_data.get(0)
        if not pl_data:
            return jsonify({"success": False, "message": "玩家数据不存在"})
        
        # 记录使用前的数值
        old_sanity = pl_data.sanity_point
        old_semen = pl_data.semen_point
        
        if drug_type == 'sanity':
            # 使用理智药
            has_drug = False
            for item_id in [0, 1, 2, 3]:
                if pl_data.item.get(item_id, 0) > 0:
                    has_drug = True
                    break
            
            if not has_drug:
                return jsonify({"success": False, "message": "没有理智药剂"})
            
            # 调用自动使用理智药函数
            auto_use_sanity_drug()
            message = "已使用理智药"
            
        elif drug_type == 'semen':
            # 使用精力剂（ID=11）
            if pl_data.item.get(11, 0) <= 0:
                return jsonify({"success": False, "message": "没有精力剂"})
            
            # 调用使用精力剂函数
            use_drug(11)
            message = "已使用精力剂"
        
        # 计算数值变化并添加到 web_value_changes
        timestamp = time.time()
        
        # 确保 web_value_changes 列表存在
        if not hasattr(cache, 'web_value_changes') or cache.web_value_changes is None:
            cache.web_value_changes = []
        
        # 记录理智变化
        sanity_change = pl_data.sanity_point - old_sanity
        if sanity_change != 0:
            cache.web_value_changes.append({
                'character_id': 0,
                'field': 'sanity_point',
                'field_name': '理智',
                'value': int(sanity_change),
                'color': 'sanity',
                'timestamp': timestamp
            })
        
        # 记录精液变化
        semen_change = pl_data.semen_point - old_semen
        if semen_change != 0:
            cache.web_value_changes.append({
                'character_id': 0,
                'field': 'semen_point',
                'field_name': '精液',
                'value': int(semen_change),
                'color': 'semen',
                'timestamp': timestamp
            })
        
        # 获取更新后的玩家信息（包含 value_changes）
        from Script.System.Web_Draw_System.status_panel import StatusPanel
        status_panel = StatusPanel()
        updated_player_info = status_panel.get_player_info()
        
        logging.info(f"快速使用药剂成功: {drug_type}")
        return jsonify({
            "success": True, 
            "message": message,
            "player_info": updated_player_info
        })
    
    except Exception as e:
        logging.error(f"使用药剂失败: {str(e)}")
        return jsonify({"success": False, "message": f"使用失败: {str(e)}"})


@app.route('/api/toggle_cloth', methods=['POST'])
def toggle_cloth():
    """
    切换衣服穿脱状态
    
    参数：cloth_id - 衣服ID, cloth_type - 衣服类型, is_worn - 当前是否穿着
    
    返回值类型：JSON
    功能描述：切换指定衣服的穿脱状态
    """
    from Script.Core import cache_control
    from Script.Design import handle_premise
    cache = cache_control.cache
    
    data = request.json or {}
    cloth_id = data.get('cloth_id')
    cloth_type = data.get('cloth_type')
    is_worn = data.get('is_worn')
    
    if cloth_id is None or cloth_type is None:
        return jsonify({"success": False, "error": "缺少参数"})
    
    try:
        cloth_id = int(cloth_id)
        cloth_type = int(cloth_type)
        
        pl_data = cache.character_data.get(0)
        if not pl_data:
            return jsonify({"success": False, "error": "玩家数据不存在"})
        
        target_id = pl_data.target_character_id
        target_data = cache.character_data.get(target_id)
        if not target_data:
            return jsonify({"success": False, "error": "目标角色数据不存在"})
        
        # 切换穿脱状态
        if is_worn:
            # 当前穿着，需要脱下
            if cloth_id in target_data.cloth.cloth_wear[cloth_type]:
                target_data.cloth.cloth_wear[cloth_type].remove(cloth_id)
                target_data.cloth.cloth_off[cloth_type].append(cloth_id)
        else:
            # 当前脱下，需要穿上
            if cloth_id in target_data.cloth.cloth_off[cloth_type]:
                target_data.cloth.cloth_off[cloth_type].remove(cloth_id)
                target_data.cloth.cloth_wear[cloth_type].append(cloth_id)
        
        # 更新异常标记
        handle_premise.settle_chara_unnormal_flag(target_id, 4)
        
        logging.info(f"切换衣服 {cloth_id} 类型 {cloth_type} 穿脱状态")
        return jsonify({"success": True})
    
    except Exception as e:
        logging.error(f"切换衣服状态失败: {e}")
        return jsonify({"success": False, "error": str(e)})

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

@app.route('/api/cropped_image/<path:filename>')
def serve_cropped_image(filename):
    """
    提供裁切透明区域后的游戏图片文件
    
    参数：
    filename (str): 图片文件的相对路径
    
    返回值类型：Response对象
    功能描述：
    1. 从游戏根目录下的image文件夹中读取图片
    2. 自动裁切掉图片四周的透明区域
    3. 将裁切后的图片通过缓存机制提供给前端
    4. 同时在响应头中返回裁切元数据
    
    响应头包含：
    - X-Original-Width: 原始图片宽度
    - X-Original-Height: 原始图片高度
    - X-Cropped-Width: 裁切后图片宽度
    - X-Cropped-Height: 裁切后图片高度
    - X-Offset-X: 裁切区域X偏移
    - X-Offset-Y: 裁切区域Y偏移
    """
    from flask import send_file, abort, make_response
    from Script.System.Web_Draw_System.image_processor import get_cropped_image, is_image_processor_available
    import io
    
    # 检查图片处理功能是否可用
    if not is_image_processor_available():
        # 如果PIL不可用，回退到原始图片服务
        return serve_image(filename)
    
    # 根据环境确定基础目录和图片文件夹路径
    if hasattr(sys, '_MEIPASS'):
        base_dir = os.path.dirname(sys.executable)
        image_dir = os.path.join(base_dir, 'image')
    else:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
        image_dir = os.path.join(base_dir, 'image')
    
    # 构建完整的图片路径
    full_path = os.path.join(image_dir, filename)
    
    # 检查文件是否存在
    if not os.path.exists(full_path):
        abort(404)
    
    # 获取裁切后的图片
    result = get_cropped_image(full_path)
    
    if result is None:
        # 如果裁切失败，回退到原始图片服务
        return serve_image(filename)
    
    image_bytes, metadata = result
    
    # 创建响应
    response = make_response(send_file(
        io.BytesIO(image_bytes),
        mimetype='image/png',
        download_name=os.path.basename(filename)
    ))
    
    # 添加元数据到响应头
    response.headers['X-Original-Width'] = str(metadata['original_width'])
    response.headers['X-Original-Height'] = str(metadata['original_height'])
    response.headers['X-Cropped-Width'] = str(metadata['cropped_width'])
    response.headers['X-Cropped-Height'] = str(metadata['cropped_height'])
    response.headers['X-Offset-X'] = str(metadata['offset_x'])
    response.headers['X-Offset-Y'] = str(metadata['offset_y'])
    
    # 允许跨域访问这些自定义头
    response.headers['Access-Control-Expose-Headers'] = 'X-Original-Width, X-Original-Height, X-Cropped-Width, X-Cropped-Height, X-Offset-X, X-Offset-Y'
    
    return response

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
    # 连接后立即发送当前完整游戏状态
    try:
        send_full_game_state()
    except Exception as e:
        logging.error(f"发送初始游戏状态失败: {str(e)}")
        import traceback
        traceback.print_exc()

@socketio.on('disconnect')
def handle_disconnect():
    """
    处理客户端断开连接事件
    
    参数：无
    
    返回值类型：无
    功能描述：处理WebSocket客户端断开连接事件
    """
    logging.info("客户端已断开连接")

@socketio.on('refresh_state')
def handle_refresh_state(data=None):
    """
    处理刷新游戏状态请求事件
    
    参数：
    data (dict): 可选的请求参数
    
    返回值类型：无
    功能描述：刷新并发送完整的游戏状态到客户端
    """
    logging.info("收到刷新状态请求")
    try:
        send_full_game_state()
    except Exception as e:
        logging.error(f"刷新游戏状态失败: {str(e)}")
        import traceback
        traceback.print_exc()

@socketio.on('request_game_state')
def handle_request_game_state(data=None):
    """
    处理游戏状态请求事件（Web新UI）
    
    参数：
    data (dict): 可选的请求参数
    
    返回值类型：无
    功能描述：发送完整的游戏状态到客户端
    """
    logging.info("收到游戏状态请求")
    try:
        send_full_game_state()
    except Exception as e:
        logging.error(f"处理游戏状态请求失败: {str(e)}")
        import traceback
        traceback.print_exc()

# ========== Web模式专用的新SocketIO事件处理器 ==========

@socketio.on('select_interaction_type')
def handle_select_interaction_type(data):
    """
    处理交互类型选择事件（Web新UI）
    
    参数：
    data (dict): 包含 type_id 的字典
    
    返回值类型：无
    功能描述：接收前端的交互类型选择，更新游戏状态并返回可用的部位列表和指令列表
    """
    from Script.System.Instruct_System import instruct_meta
    from Script.System.Instruct_System.instruct_category import BODY_PART_NAMES
    
    type_id = data.get('type_id')
    logging.info(f"选择交互类型: {type_id}")
    
    # 获取该交互类型下的所有指令
    instructs = instruct_meta.get_instructs_by_interaction_type_from_constant(type_id)
    
    # 获取该交互类型涉及的所有身体部位
    body_parts = instruct_meta.get_body_parts_for_interaction_type_from_constant(type_id)
    
    # 构建返回数据
    instruct_list = []
    for instruct_id in instructs:
        info = instruct_meta.get_web_instruct_info(instruct_id)
        if info:
            instruct_list.append({
                'id': instruct_id,
                'name': info['name'],
                'body_parts': info['body_parts'],
                'single_part': info['is_single_part'],
            })
    
    # 构建部位数据（包含中文名）
    body_parts_data = []
    for part in body_parts:
        body_parts_data.append({
            'id': part,
            'name': BODY_PART_NAMES.get(part, part),
        })
    
    # 更新缓存中的当前交互类型
    cache.current_interaction_type = type_id
    
    socketio.emit('interaction_type_selected', {
        'type_id': type_id,
        'available_body_parts': body_parts_data,
        'available_instructs': instruct_list,
    })

@socketio.on('click_body_part')
def handle_click_body_part(data):
    """
    处理身体部位点击事件（Web新UI）
    
    参数：
    data (dict): 包含 part_name 的字典
    
    返回值类型：无
    功能描述：接收前端的部位点击，返回该部位可执行的指令列表
              如果点击的是臀部或头部：
              - 已选择小类时：显示该小类下所有子部位的可用指令
              - 未选择小类时：展开子部位菜单
              头部子部位中，兽角和兽耳需要角色有对应特征才显示
    """
    from Script.System.Instruct_System import instruct_meta
    from Script.System.Instruct_System.instruct_category import (
        BODY_PART_NAMES, 
        BodyPart, 
        HIP_SUB_PARTS,
        HEAD_SUB_PARTS
    )
    from Script.Design import web_interaction_manager
    
    part_name = data.get('part_name')
    logging.info(f"点击身体部位: {part_name}")
    
    # 获取当前选中的交互小类
    current_minor_type = web_interaction_manager.get_current_minor_type()
    
    # 检查是否是臀部点击
    if part_name == BodyPart.HIP or part_name == "臀部":
        if current_minor_type is not None:
            # 已选择小类时，收集该小类下所有臀部子部位的可用指令
            all_instructs = []
            hip_sub_parts = list(HIP_SUB_PARTS) + [BodyPart.CROTCH]  # 包含胯部
            
            for sub_part in hip_sub_parts:
                instructs = web_interaction_manager.get_instructs_by_body_part(
                    sub_part, 
                    minor_type=current_minor_type,
                    check_premise=True
                )
                for instruct_id in instructs:
                    if instruct_id not in [i['id'] for i in all_instructs]:
                        info = instruct_meta.get_web_instruct_info(instruct_id)
                        if info:
                            all_instructs.append({
                                'id': instruct_id,
                                'name': info['name'],
                            })
            
            # 获取部位中文名
            part_name_cn = BODY_PART_NAMES.get(BodyPart.HIP, "臀部")
            
            socketio.emit('body_part_clicked', {
                'part_name': part_name,
                'part_name_cn': part_name_cn,
                'available_instructs': all_instructs,
                'single_instruct': len(all_instructs) == 1,
            })
            return
        else:
            # 未选择小类时，展开子部位菜单
            sub_parts = []
            for sub_part in HIP_SUB_PARTS:
                sub_parts.append({
                    'part_id': sub_part,
                    'part_name_cn': BODY_PART_NAMES.get(sub_part, sub_part)
                })
            
            socketio.emit('hip_sub_menu', {
                'part_name': part_name,
                'part_name_cn': BODY_PART_NAMES.get(BodyPart.HIP, "臀部"),
                'sub_parts': sub_parts,
            })
            return
    
    # 检查是否是头部点击
    if part_name == BodyPart.HEAD or part_name == "头部":
        # 获取交互对象是否有兽耳/兽角特征
        pl_character_data = cache.character_data[0]
        target_id = pl_character_data.target_character_id
        has_beast_ears = False
        has_horn = False
        
        if target_id > 0:
            target_data = cache.character_data.get(target_id)
            if target_data and hasattr(target_data, 'talent'):
                has_beast_ears = target_data.talent.get(111, 0) == 1
                has_horn = target_data.talent.get(112, 0) == 1
        
        if current_minor_type is not None:
            # 已选择小类时，收集该小类下所有头部子部位的可用指令
            all_instructs = []
            
            for sub_part in HEAD_SUB_PARTS:
                # 跳过角色没有的特征对应的部位
                if sub_part == BodyPart.HORN and not has_horn:
                    continue
                # 注意：兽耳已从 HEAD_SUB_PARTS 中移除，作为独立部位处理
                
                instructs = web_interaction_manager.get_instructs_by_body_part(
                    sub_part, 
                    minor_type=current_minor_type,
                    check_premise=True
                )
                for instruct_id in instructs:
                    if instruct_id not in [i['id'] for i in all_instructs]:
                        info = instruct_meta.get_web_instruct_info(instruct_id)
                        if info:
                            all_instructs.append({
                                'id': instruct_id,
                                'name': info['name'],
                            })
            
            # 获取部位中文名
            part_name_cn = BODY_PART_NAMES.get(BodyPart.HEAD, "头部")
            
            socketio.emit('body_part_clicked', {
                'part_name': part_name,
                'part_name_cn': part_name_cn,
                'available_instructs': all_instructs,
                'single_instruct': len(all_instructs) == 1,
            })
            return
        else:
            # 未选择小类时，展开子部位菜单
            # 注意：兽耳已从 HEAD_SUB_PARTS 中移除，作为独立部位处理
            sub_parts = []
            for sub_part in HEAD_SUB_PARTS:
                # 头发始终显示
                # 兽角需要角色有对应特征
                if sub_part == BodyPart.HAIR:
                    sub_parts.append({
                        'part_id': sub_part,
                        'part_name_cn': BODY_PART_NAMES.get(sub_part, sub_part)
                    })
                elif sub_part == BodyPart.HORN and has_horn:
                    sub_parts.append({
                        'part_id': sub_part,
                        'part_name_cn': BODY_PART_NAMES.get(sub_part, sub_part)
                    })
            
            socketio.emit('head_sub_menu', {
                'part_name': part_name,
                'part_name_cn': BODY_PART_NAMES.get(BodyPart.HEAD, "头部"),
                'sub_parts': sub_parts,
                'has_beast_ears': has_beast_ears,
                'has_horn': has_horn,
            })
            return
    
    # 将中文部位名转换为英文（用于与指令的body_parts匹配）
    # 反向查找：从中文名查找英文id
    part_name_en = part_name  # 默认使用原始值
    for en_name, cn_name in BODY_PART_NAMES.items():
        if cn_name == part_name or en_name == part_name:
            part_name_en = en_name
            break
    # 处理左右部位的情况（如"左手部"“右耳部"等）
    if part_name_en == part_name:  # 没有找到直接匹配
        # 尝试去除"左"/"右"前缀后再匹配
        cleaned_name = part_name.replace('左', '').replace('右', '')
        for en_name, cn_name in BODY_PART_NAMES.items():
            if cn_name == cleaned_name:
                part_name_en = en_name
                break
    
    logging.info(f"部位名转换: {part_name} -> {part_name_en}, 当前小类: {current_minor_type}")
    
    # 获取该部位可执行的指令列表
    if current_minor_type is not None:
        # 如果选择了小类，使用web_interaction_manager过滤
        instructs = web_interaction_manager.get_instructs_by_body_part(
            part_name_en,
            minor_type=current_minor_type,
            check_premise=True
        )
    else:
        # 未选择小类，返回该部位的所有指令
        instructs = web_interaction_manager.get_instructs_by_body_part(
            part_name_en,
            check_premise=True
        )
    
    # 构建返回数据
    instruct_list = []
    for instruct_id in instructs:
        info = instruct_meta.get_web_instruct_info(instruct_id)
        if info:
            instruct_list.append({
                'id': instruct_id,
                'name': info['name'],
            })
    
    # 获取部位中文名
    part_name_cn = BODY_PART_NAMES.get(part_name, part_name)
    
    socketio.emit('body_part_clicked', {
        'part_name': part_name,
        'part_name_cn': part_name_cn,
        'available_instructs': instruct_list,
        'single_instruct': len(instruct_list) == 1,
    })

# 刷新信号常量，与 in_scene_panel_web.py 中的 WEB_REFRESH_SIGNAL 保持一致
WEB_REFRESH_SIGNAL = "__WEB_REFRESH__"

@socketio.on('execute_instruct')
def handle_execute_instruct(data):
    """
    处理指令执行事件（Web新UI）
    
    参数：
    data (dict): 包含 instruct_id 的字典
    
    返回值类型：无
    功能描述：接收前端的指令执行请求，执行指令并触发结算流程，
              完成后设置刷新信号以通知主面板循环刷新数据
    """
    global button_click_response
    
    from Script.System.Instruct_System import handle_instruct as instruct_handler
    from Script.Core import constant
    
    instruct_id = data.get('instruct_id')
    logging.info(f"执行指令: {instruct_id}")
    
    try:
        # 检查指令是否存在
        if instruct_id not in constant.handle_instruct_data:
            socketio.emit('instruct_executed', {
                'instruct_id': instruct_id,
                'success': False,
                'error': '指令不存在'
            })
            return
        
        # 执行指令
        instruct_handler.handle_instruct(instruct_id)
        
        # 设置刷新信号，通知主面板循环刷新数据
        # 这会唤醒 askfor_all 并让主循环进入下一次迭代，重新收集并发送最新数据
        with state_lock:
            button_click_response = WEB_REFRESH_SIGNAL
        
        socketio.emit('instruct_executed', {
            'instruct_id': instruct_id,
            'success': True
        })
        
    except Exception as e:
        logging.error(f"执行指令失败: {e}")
        socketio.emit('instruct_executed', {
            'instruct_id': instruct_id,
            'success': False,
            'error': str(e)
        })

@socketio.on('switch_target')
def handle_switch_target(data):
    """
    处理切换交互对象事件（Web新UI）
    
    参数：
    data (dict): 包含 character_id 的字典
    
    返回值类型：无
    功能描述：接收前端的切换交互对象请求，更新玩家的交互对象，并触发UI刷新
    
    当被点击的角色有待显示的行为指令文本时：
    1. 将该角色的行为文本移动到主对话框队列进行显示
    2. 刷新该角色的数值变化时间戳，确保能正确显示浮动文本
    """
    import time
    from Script.System.Web_Draw_System.dialog_box import add_dialog_text
    
    character_id = data.get('character_id')
    logging.info(f"切换交互对象: {character_id}")
    
    try:
        # 获取玩家角色数据
        pl_character_data = cache.character_data[0]
        
        # 检查目标角色是否存在
        if character_id not in cache.character_data:
            socketio.emit('target_switched', {
                'character_id': character_id,
                'success': False,
                'error': '角色不存在'
            })
            return
        
        # 更新交互对象
        pl_character_data.target_character_id = character_id
        
        # 获取目标角色信息用于返回
        target_data = cache.character_data[character_id]
        
        # ========== 处理待显示的行为指令文本 ==========
        # 检查该角色是否有待显示的 minor_dialog
        if hasattr(cache, 'web_minor_dialog_queue') and cache.web_minor_dialog_queue:
            # 查找该角色的 minor_dialog
            minor_dialog_to_show = None
            remaining_dialogs = []
            for dialog in cache.web_minor_dialog_queue:
                if dialog.get('character_id') == character_id:
                    minor_dialog_to_show = dialog
                else:
                    remaining_dialogs.append(dialog)
            
            # 如果找到该角色的待显示文本，将其移动到主对话框显示
            if minor_dialog_to_show:
                # 将完整文本添加到主对话框队列
                speaker_name = minor_dialog_to_show.get('speaker', target_data.name)
                full_text = minor_dialog_to_show.get('full_text', minor_dialog_to_show.get('text', ''))
                text_color = minor_dialog_to_show.get('text_color', 'standard')
                # 使用记录时保存的交互对象ID，而不是被切换到的角色ID
                # 避免因为角色指令结算完毕后交互对象变更导致显示错误的交互对象名字
                saved_target_id = minor_dialog_to_show.get('target_character_id', -1)
                add_dialog_text(speaker_name, full_text, text_color, wait_input=True, target_character_id=saved_target_id)
                
                # 从 minor_dialog 队列中移除该角色的条目
                cache.web_minor_dialog_queue = remaining_dialogs
                logging.info(f"将角色 {target_data.name} 的行为文本移动到主对话框显示")
        
        # ========== 刷新该角色的数值变化时间戳 ==========
        # 确保该角色的 value_changes 不会因为2秒超时被过滤掉
        if hasattr(cache, 'web_value_changes') and cache.web_value_changes:
            current_time = time.time()
            for change in cache.web_value_changes:
                if change.get('character_id') == character_id:
                    change['timestamp'] = current_time
        
        # 发送切换成功事件
        socketio.emit('target_switched', {
            'character_id': character_id,
            'character_name': target_data.name,
            'success': True
        })
        
        # 标记需要刷新状态（让前端知道需要重新渲染）
        # 设置一个标志让 InScenePanelWeb 知道需要发送完整状态
        cache.web_need_full_refresh = True
        
        # 设置刷新信号，通知主面板循环刷新数据
        # 这会唤醒 askfor_all 并让主循环进入下一次迭代，重新收集并发送最新数据
        global button_click_response
        with state_lock:
            button_click_response = WEB_REFRESH_SIGNAL
        
    except Exception as e:
        logging.error(f"切换交互对象失败: {e}")
        socketio.emit('target_switched', {
            'character_id': character_id,
            'success': False,
            'error': str(e)
        })

@socketio.on('click_panel_tab')
def handle_click_panel_tab(data):
    """
    处理面板选项卡点击事件（Web新UI）
    
    参数：
    data (dict): 包含 tab_id (即 instruct_id) 的字典
    
    返回值类型：无
    功能描述：接收前端的面板选项卡点击，执行对应的面板类指令
    """
    from Script.System.Instruct_System import handle_instruct as instruct_handler
    from Script.Core import constant
    
    tab_id = data.get('tab_id')
    logging.info(f"点击面板选项卡: {tab_id}")
    
    try:
        # tab_id 就是指令ID
        instruct_id = tab_id
        
        # 检查指令是否存在
        if instruct_id not in constant.handle_instruct_data:
            socketio.emit('panel_tab_clicked', {
                'tab_id': tab_id,
                'success': False,
                'error': '指令不存在'
            })
            return
        
        # 执行面板类指令
        instruct_handler.handle_instruct(instruct_id)
        
        socketio.emit('panel_tab_clicked', {
            'tab_id': tab_id,
            'success': True
        })
        
    except Exception as e:
        logging.error(f"执行面板指令失败: {e}")
        socketio.emit('panel_tab_clicked', {
            'tab_id': tab_id,
            'success': False,
            'error': str(e)
        })

@socketio.on('get_interaction_types')
def handle_get_interaction_types(data):
    """
    获取可用的交互类型列表（Web新UI）
    
    参数：
    data (dict): 空字典
    
    返回值类型：无
    功能描述：返回所有可用的交互类型列表供前端显示
    """
    from Script.System.Instruct_System import instruct_meta
    
    logging.info("获取交互类型列表")
    
    try:
        # 获取所有可用的交互类型
        interaction_types = instruct_meta.get_available_interaction_types_from_constant()
        
        socketio.emit('interaction_types_list', {
            'types': interaction_types,
            'success': True
        })
        
    except Exception as e:
        logging.error(f"获取交互类型列表失败: {e}")
        socketio.emit('interaction_types_list', {
            'types': [],
            'success': False,
            'error': str(e)
        })

@socketio.on('get_panel_instructs')
def handle_get_panel_instructs(data):
    """
    获取面板类指令列表（Web新UI）
    
    参数：
    data (dict): 空字典
    
    返回值类型：无
    功能描述：返回所有面板类指令供顶部选项卡栏显示
    """
    from Script.System.Instruct_System import instruct_meta
    from Script.Core import constant
    
    logging.info("获取面板类指令列表")
    
    try:
        # 获取所有面板类指令
        panel_instructs = instruct_meta.get_panel_instructs_from_constant()
        
        # 构建返回数据
        instruct_list = []
        for instruct_id in panel_instructs:
            name = constant.handle_instruct_name_data.get(instruct_id, f"指令{instruct_id}")
            instruct_list.append({
                'id': instruct_id,
                'name': name,
            })
        
        socketio.emit('panel_instructs_list', {
            'instructs': instruct_list,
            'success': True
        })
        
    except Exception as e:
        logging.error(f"获取面板类指令列表失败: {e}")
        socketio.emit('panel_instructs_list', {
            'instructs': [],
            'success': False,
            'error': str(e)
        })

# ========== Web模式新交互类型系统API（大类/小类） ==========

@socketio.on('get_major_types')
def handle_get_major_types(data):
    """
    获取可用的交互大类型列表（Web新UI）
    
    参数：
    data (dict): 空字典
    
    返回值类型：无
    功能描述：返回所有可用的大类型列表（嘴/手/阴茎/道具/其他）
    """
    from Script.Design import web_interaction_manager
    
    logging.info("获取交互大类型列表")
    
    try:
        major_types = web_interaction_manager.get_available_major_types()
        
        socketio.emit('major_types_list', {
            'types': major_types,
            'current_major_type': cache.web_current_major_type,
            'success': True
        })
    except Exception as e:
        logging.error(f"获取大类型列表失败: {e}")
        socketio.emit('major_types_list', {
            'types': [],
            'success': False,
            'error': str(e)
        })


@socketio.on('select_major_type')
def handle_select_major_type(data):
    """
    选择交互大类型（Web新UI）
    
    参数：
    data (dict): 包含 major_type_id 的字典
    
    返回值类型：无
    功能描述：选择大类型，返回该大类下的小类型列表，并恢复之前记忆的小类选择
    """
    from Script.Design import web_interaction_manager
    from Script.Core import constant
    
    major_type_id = data.get('major_type_id')
    # major_type_id 现在是字符串类型（如 'mouth', 'hand', 'arts', 'stop' 等）
    logging.info(f"选择交互大类型: {major_type_id}")
    
    try:
        # 选择大类型，返回记忆的小类型
        remembered_minor = web_interaction_manager.select_major_type(major_type_id)
        
        # 获取该大类下的小类型列表
        minor_types = web_interaction_manager.get_available_minor_types(major_type_id)
        
        logging.info(f"大类型 {major_type_id} 对应的小类型列表: {minor_types}")
        
        socketio.emit('major_type_selected', {
            'major_type_id': major_type_id,
            'major_type_name': constant.get_major_type_name(major_type_id),
            'minor_types': minor_types,
            'remembered_minor_type': remembered_minor,
            'success': True
        })
    except Exception as e:
        logging.error(f"选择大类型失败: {e}")
        socketio.emit('major_type_selected', {
            'major_type_id': major_type_id,
            'success': False,
            'error': str(e)
        })


@socketio.on('select_minor_type')
def handle_select_minor_type(data):
    """
    选择交互小类型（Web新UI）
    
    参数：
    data (dict): 包含 minor_type_id 的字典
    
    返回值类型：无
    功能描述：选择小类型，返回该小类型下可用的指令列表，同时返回更新后的target_info以刷新右侧面板
    """
    from Script.Design import web_interaction_manager
    from Script.Core import constant
    from Script.System.Web_Draw_System.status_panel import StatusPanel
    
    minor_type_id = data.get('minor_type_id')
    # minor_type_id 现在是字符串类型（如 'mouth_talk', 'hand_touch', 'arts_hypnosis' 等）
    logging.info(f"选择交互小类型: {minor_type_id}")
    
    try:
        # 选择小类型
        web_interaction_manager.select_minor_type(minor_type_id)
        
        # 获取该小类型下可用的指令列表
        instructs = web_interaction_manager.get_instructs_by_minor_type(minor_type_id)
        
        # 构建指令信息列表
        instruct_list = []
        for instruct_id in instructs:
            name = constant.handle_instruct_name_data.get(instruct_id, f"指令{instruct_id}")
            body_parts = constant.instruct_body_parts_data.get(instruct_id, [])
            instruct_list.append({
                'id': instruct_id,
                'name': name,
                'body_parts': body_parts,
            })
        
        # 获取更新后的交互对象信息（包含可选部位列表）
        status_panel = StatusPanel()
        character_id = cache.character_data[0].target_character_id if hasattr(cache.character_data[0], 'target_character_id') else 0
        target_info = status_panel.get_target_info(character_id)
        
        socketio.emit('minor_type_selected', {
            'minor_type_id': minor_type_id,
            'minor_type_name': constant.get_minor_type_name(minor_type_id),
            'instructs': instruct_list,
            'target_info': target_info,
            'success': True
        })
    except Exception as e:
        logging.error(f"选择小类型失败: {e}")
        socketio.emit('minor_type_selected', {
            'minor_type_id': minor_type_id,
            'success': False,
            'error': str(e)
        })


@socketio.on('clear_interaction_selection')
def handle_clear_interaction_selection(data):
    """
    清空交互类型选择（Web新UI）
    
    参数：
    data (dict): 空字典
    
    返回值类型：无
    功能描述：清空当前选择的大类和小类，同时返回更新后的target_info以刷新右侧面板
    """
    from Script.Design import web_interaction_manager
    from Script.System.Web_Draw_System.status_panel import StatusPanel
    
    logging.info("清空交互类型选择")
    
    try:
        # 清空选择
        web_interaction_manager.clear_selection()
        
        # 获取更新后的交互对象信息（包含可选部位列表）
        status_panel = StatusPanel()
        character_id = cache.character_data[0].target_character_id if hasattr(cache.character_data[0], 'target_character_id') else 0
        target_info = status_panel.get_target_info(character_id)
        
        socketio.emit('interaction_selection_cleared', {
            'success': True,
            'target_info': target_info
        })
    except Exception as e:
        logging.error(f"清空交互选择失败: {e}")
        socketio.emit('interaction_selection_cleared', {
            'success': False,
            'error': str(e)
        })


@socketio.on('get_drug_list')
def handle_get_drug_list(data):
    """
    获取药物列表（Web新UI - 道具大类专用）
    
    参数：
    data (dict): 空字典
    
    返回值类型：无
    功能描述：返回可用的药物列表
    """
    from Script.Design import web_interaction_manager
    
    logging.info("获取药物列表")
    
    try:
        drug_list = web_interaction_manager.get_drug_list()
        
        socketio.emit('drug_list', {
            'drugs': drug_list,
            'selected_drug_id': cache.web_selected_drug_id,
            'success': True
        })
    except Exception as e:
        logging.error(f"获取药物列表失败: {e}")
        socketio.emit('drug_list', {
            'drugs': [],
            'success': False,
            'error': str(e)
        })


@socketio.on('get_item_list')
def handle_get_item_list(data):
    """
    获取道具列表（Web新UI - 道具大类专用）
    
    参数：
    data (dict): 空字典
    
    返回值类型：无
    功能描述：返回可用的道具列表
    """
    from Script.Design import web_interaction_manager
    
    logging.info("获取道具列表")
    
    try:
        item_list = web_interaction_manager.get_item_list()
        
        socketio.emit('item_list', {
            'items': item_list,
            'selected_item_id': cache.web_selected_item_id,
            'success': True
        })
    except Exception as e:
        logging.error(f"获取道具列表失败: {e}")
        socketio.emit('item_list', {
            'items': [],
            'success': False,
            'error': str(e)
        })


@socketio.on('select_drug')
def handle_select_drug(data):
    """
    选择药物（Web新UI - 道具大类专用）
    
    参数：
    data (dict): 包含 drug_id 的字典
    
    返回值类型：无
    功能描述：选择要使用的药物
    """
    from Script.Design import web_interaction_manager
    
    drug_id = data.get('drug_id')
    logging.info(f"选择药物: {drug_id}")
    
    try:
        web_interaction_manager.select_drug(drug_id)
        
        socketio.emit('drug_selected', {
            'drug_id': drug_id,
            'success': True
        })
    except Exception as e:
        logging.error(f"选择药物失败: {e}")
        socketio.emit('drug_selected', {
            'drug_id': drug_id,
            'success': False,
            'error': str(e)
        })


@socketio.on('select_item')
def handle_select_item(data):
    """
    选择道具（Web新UI - 道具大类专用）
    
    参数：
    data (dict): 包含 item_id 的字典
    
    返回值类型：无
    功能描述：选择要使用的道具
    """
    from Script.Design import web_interaction_manager
    
    item_id = data.get('item_id')
    logging.info(f"选择道具: {item_id}")
    
    try:
        web_interaction_manager.select_item(item_id)
        
        socketio.emit('item_selected', {
            'item_id': item_id,
            'success': True
        })
    except Exception as e:
        logging.error(f"选择道具失败: {e}")
        socketio.emit('item_selected', {
            'item_id': item_id,
            'success': False,
            'error': str(e)
        })


@socketio.on('get_interaction_state')
def handle_get_interaction_state(data):
    """
    获取当前交互状态（Web新UI）
    
    参数：
    data (dict): 空字典
    
    返回值类型：无
    功能描述：返回当前的交互状态，包括大类/小类选择、药物/道具选择等
    """
    from Script.Design import web_interaction_manager
    
    logging.info("获取交互状态")
    
    try:
        state = web_interaction_manager.get_interaction_state()
        
        socketio.emit('interaction_state', {
            'state': state,
            'success': True
        })
    except Exception as e:
        logging.error(f"获取交互状态失败: {e}")
        socketio.emit('interaction_state', {
            'state': {},
            'success': False,
            'error': str(e)
        })


@socketio.on('get_all_scene_characters')
def handle_get_all_scene_characters(data):
    """
    获取场景内所有角色信息（Web新UI）
    
    参数：
    data (dict): 空字典
    
    返回值类型：无
    功能描述：返回当前场景内所有角色的头像信息列表（包括玩家和交互对象）
    用于"显示场景内全部角色"面板
    """
    from Script.System.Web_Draw_System import character_renderer
    
    logging.info("获取场景内所有角色")
    
    try:
        # 创建渲染器实例
        renderer = character_renderer.CharacterRenderer()
        
        # 获取所有场景角色（不排除任何角色）
        all_characters = renderer.get_scene_characters_avatars(exclude_ids=[0])
        
        socketio.emit('all_scene_characters', {
            'characters': all_characters,
            'success': True
        })
    except Exception as e:
        logging.error(f"获取场景角色失败: {e}")
        socketio.emit('all_scene_characters', {
            'characters': [],
            'success': False,
            'error': str(e)
        })

# ========== 结束：Web模式新交互类型系统API ==========

@socketio.on('advance_dialog')
def handle_advance_dialog(data):
    """
    处理对话推进事件（Web新UI）
    
    参数：
    data (dict): 可包含 skip 参数表示是否跳过当前角色对话
    
    返回值类型：无
    功能描述：推进对话文本显示，返回当前对话状态
    """
    skip = data.get('skip', False)
    logging.info(f"推进对话, 跳过={skip}")
    
    try:
        # 使用新的dialog_box模块处理对话
        from Script.System.Web_Draw_System.dialog_box import (
            advance_dialog, skip_all_dialogs, get_dialog_state
        )
        
        if skip:
            skip_all_dialogs()
            has_more = False
        else:
            has_more = advance_dialog()
        
        # 获取当前对话状态
        dialog_state = get_dialog_state()
        
        socketio.emit('dialog_advanced', {
            'success': True,
            'has_more': has_more,
            'dialog': dialog_state
        })
    except Exception as e:
        logging.error(f"推进对话时出错: {str(e)}")
        socketio.emit('dialog_advanced', {
            'success': False,
            'error': str(e)
        })


@socketio.on('skip_all_dialogs')
def handle_skip_all_dialogs(data):
    """
    跳过所有剩余对话（Web新UI）
    
    参数：
    data (dict): 请求参数（可选）
    
    返回值类型：无
    功能描述：清空对话队列并隐藏对话框
    """
    logging.info("跳过所有对话")
    
    try:
        from Script.System.Web_Draw_System.dialog_box import (
            skip_all_dialogs, get_dialog_state
        )
        
        skip_all_dialogs()
        dialog_state = get_dialog_state()
        
        socketio.emit('dialogs_skipped', {
            'success': True,
            'dialog': dialog_state
        })
    except Exception as e:
        logging.error(f"跳过对话时出错: {str(e)}")
        socketio.emit('dialogs_skipped', {
            'success': False,
            'error': str(e)
        })


@socketio.on('get_settlement_state')
def handle_get_settlement_state(data):
    """
    获取当前结算状态（Web新UI）
    
    参数：
    data (dict): 请求参数（可选）
    
    返回值类型：无
    功能描述：返回当前结算阶段的完整状态信息
    """
    try:
        manager = get_settlement_manager()
        state = manager.get_state()
        
        socketio.emit('settlement_state', {
            'success': True,
            'settlement_state': state
        })
    except Exception as e:
        logging.error(f"获取结算状态时出错: {str(e)}")
        socketio.emit('settlement_state', {
            'success': False,
            'error': str(e)
        })


@socketio.on('get_character_dialog')
def handle_get_character_dialog(data):
    """
    获取指定角色的完整对话（Web新UI）
    
    参数：
    data (dict): 包含 character_id 参数
    
    返回值类型：无
    功能描述：当点击场景中其他角色头像时，返回该角色的完整对话文本
    """
    character_id = data.get('character_id')
    
    if character_id is None:
        socketio.emit('character_dialog', {
            'success': False,
            'error': '缺少 character_id 参数'
        })
        return
    
    try:
        manager = get_settlement_manager()
        full_text = manager.get_full_dialog(character_id)
        
        # 获取角色名称
        char_name = ""
        if character_id in cache.character_data:
            char_name = cache.character_data[character_id].name
        
        socketio.emit('character_dialog', {
            'success': True,
            'character_id': character_id,
            'character_name': char_name,
            'dialog_text': full_text,
            'has_dialog': full_text is not None
        })
    except Exception as e:
        logging.error(f"获取角色对话时出错: {str(e)}")
        socketio.emit('character_dialog', {
            'success': False,
            'error': str(e)
        })


def push_game_state(state_data: dict, diff_only: bool = True):
    """
    推送游戏状态到前端（Web新UI专用）
    
    参数：
    state_data (dict): 游戏状态数据
    diff_only (bool): 是否仅推送差异数据，默认True
    
    返回值类型：无
    功能描述：向所有连接的Web客户端推送游戏状态更新
    """
    try:
        with state_lock:
            if diff_only:
                # 推送差异数据
                socketio.emit('game_state_diff', state_data)
            else:
                # 推送完整状态
                socketio.emit('game_state_full', state_data)
        logging.debug(f"推送游戏状态: diff_only={diff_only}, 数据大小={len(str(state_data))}")
    except Exception as e:
        logging.error(f"推送游戏状态失败: {str(e)}")

# ========== 原有代码继续 ==========

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

def send_full_game_state():
    """
    发送完整的游戏状态到前端（包含新UI所需的所有数据）
    
    参数：无
    
    返回值类型：无
    功能描述：构建并发送包含玩家信息、交互对象、场景角色、面板选项卡等完整数据的游戏状态
    """
    try:
        # 导入必要的模块
        from Script.Design import web_interaction_manager
        from Script.System.Instruct_System import instruct_meta
        
        # 构建完整游戏状态
        full_state = {}
        
        # 基础状态（旧API兼容）
        with state_lock:
            full_state["text_content"] = game_state.get("text_content", [])
            full_state["buttons"] = game_state.get("buttons", [])
            full_state["panel_id"] = game_state.get("panel_id")
            full_state["skip_wait"] = game_state.get("skip_wait", False)
        
        # 玩家信息
        if hasattr(cache, 'character_data') and 0 in cache.character_data:
            player_data = cache.character_data[0]
            full_state["player_info"] = {
                "name": player_data.name,
                "nickname": getattr(player_data, 'nick_name', ''),
                "hp": getattr(player_data, 'hit_point', 0),
                "hp_max": getattr(player_data, 'hit_point_max', 100),
                "mp": getattr(player_data, 'mana_point', 0),
                "mp_max": getattr(player_data, 'mana_point_max', 100),
                "sanity": getattr(player_data, 'sanity_point', 0),
                "sanity_max": getattr(player_data, 'sanity_point_max', 100),
            }
        
        # 交互对象信息 - 使用 StatusPanel 获取完整信息
        from Script.System.Web_Draw_System.status_panel import StatusPanel
        status_panel = StatusPanel()
        target_id = -1
        if hasattr(cache, 'character_data') and 0 in cache.character_data:
            player_data_for_target = cache.character_data[0]
            target_id = getattr(player_data_for_target, 'target_character_id', -1)
        
        if target_id >= 0 and target_id in cache.character_data:
            full_state["target_info"] = status_panel.get_target_info(target_id)
        
        # 场景信息
        if hasattr(cache, 'now_panel_id'):
            full_state["current_panel_id"] = cache.now_panel_id
        
        # 可用交互大类
        full_state["interaction_major_types"] = web_interaction_manager.get_available_major_types()
        
        # 当前选中的大类和小类
        current_major = web_interaction_manager.get_current_major_type()
        current_minor = web_interaction_manager.get_current_minor_type()
        full_state["current_major_type"] = current_major
        full_state["current_minor_type"] = current_minor
        
        # 如果有选中的大类，获取其小类列表
        if current_major is not None:
            full_state["interaction_minor_types"] = web_interaction_manager.get_available_minor_types(current_major)
        
        # 面板选项卡（系统面板类指令）
        panel_instructs = instruct_meta.get_system_panel_instructs()
        full_state["panel_tabs"] = [
            {
                "instruct_id": iid,
                "name": constant.handle_instruct_name_data.get(iid, ""),
                "active": cache.now_panel_id == constant.instruct_panel_id_data.get(iid)
            }
            for iid in panel_instructs
            if iid in constant.instruct_panel_id_data
        ]
        
        # 对话框状态
        from Script.System.Web_Draw_System.dialog_box import get_dialog_state
        full_state["dialog"] = get_dialog_state()
        
        logging.debug(f"发送完整游戏状态: {len(full_state)} 个字段")
        socketio.emit('game_state_update', full_state)
        
    except Exception as e:
        logging.error(f"构建完整游戏状态失败: {str(e)}")
        import traceback
        traceback.print_exc()
        # 至少发送基础状态
        with state_lock:
            socketio.emit('game_state_update', game_state)

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
    
    # 添加对话框状态
    try:
        from Script.System.Web_Draw_System.dialog_box import get_dialog_state
        local_state["dialog"] = get_dialog_state()
    except Exception as e:
        logging.warning(f"获取对话框状态失败: {e}")
    
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