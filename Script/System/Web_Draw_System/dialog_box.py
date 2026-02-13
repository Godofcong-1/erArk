# -*- coding: utf-8 -*-
"""
对话框组件
负责处理Web模式下的对话框显示和文本推进

该组件提供全局对话框管理功能，供talk.py等模块使用
"""

from typing import Optional, List
from Script.Core import cache_control, game_type

cache: game_type.Cache = cache_control.cache

# 对话框每页最大行数
MAX_LINES_PER_PAGE = 4
# 对话框每行最大字符数（仅用于估算行数，不用于强制截断）
MAX_CHARS_PER_LINE = 50


def _split_text_to_pages(text: str, max_lines: int = MAX_LINES_PER_PAGE, max_chars_per_line: int = MAX_CHARS_PER_LINE) -> List[str]:
    """
    将文本按行数分页
    
    分页规则：
    1. 只按显式换行符(\n)进行分行，不强制按字符数截断
    2. 对于超长行，估算其显示行数（用于分页计算），但不实际截断
    3. 让前端CSS的word-wrap来处理超长行的自动换行
    
    Keyword arguments:
    text -- 原始文本
    max_lines -- 每页最大行数，默认为4
    max_chars_per_line -- 用于估算行数的参考字符数，默认为50
    
    Returns:
    List[str] -- 分页后的文本列表
    """
    if not text:
        return [""]
    
    # 将文本按换行符分割
    raw_lines = text.split('\n')
    
    # 计算每行的估算显示行数（用于分页计算）
    # 但保持原始行完整，不截断词语
    pages = []
    current_page_lines = []
    current_estimated_lines = 0
    
    for line in raw_lines:
        # 估算这一行会占用多少显示行数
        if not line:
            estimated_display_lines = 1  # 空行也算一行
        else:
            # 使用向上取整来估算行数
            import math
            estimated_display_lines = math.ceil(len(line) / max_chars_per_line) if len(line) > 0 else 1
        
        # 检查是否需要开新页
        if current_estimated_lines + estimated_display_lines > max_lines and current_page_lines:
            # 当前页已满，保存当前页并开新页
            pages.append('\n'.join(current_page_lines))
            current_page_lines = [line]
            current_estimated_lines = estimated_display_lines
        else:
            # 添加到当前页
            current_page_lines.append(line)
            current_estimated_lines += estimated_display_lines
    
    # 处理最后一页
    if current_page_lines:
        pages.append('\n'.join(current_page_lines))
    
    return pages if pages else [""]


def _trigger_state_update():
    """
    触发对话框状态更新推送到前端（内部辅助函数）
    
    功能描述：直接通过WebSocket发送对话框状态更新到前端
    """
    try:
        from Script.Core import web_server
        # 获取当前对话框状态
        dialog_state = get_dialog_state()
        # 直接发送对话框状态更新事件
        if hasattr(web_server, 'socketio'):
            web_server.socketio.emit('dialog_state_update', {
                'success': True,
                'dialog': dialog_state
            })
    except ImportError:
        pass  # Web模式未启用时忽略
    except Exception as e:
        import logging
        logging.warning(f"推送对话框状态失败: {e}")


def add_dialog_text(speaker_name: str, text: str, text_color: str = "standard", wait_input: bool = True, is_minor: bool = False, character_id: int = -1, target_character_id: int = -1):
    """
    添加对话文本到对话框队列（全局函数，供talk.py调用）
    
    Keyword arguments:
    speaker_name -- 说话者名称
    text -- 对话文本
    text_color -- 文本颜色样式，默认为"standard"
    wait_input -- 是否等待用户输入推进，默认为True
    is_minor -- 是否为其他角色的小对话框，默认为False
    character_id -- 角色ID，用于小对话框关联头像，默认为-1
    target_character_id -- 交互对象ID，用于显示交互对象姓名，默认为-1
    """
    # 确保队列已初始化
    if not hasattr(cache, 'web_dialog_queue') or cache.web_dialog_queue is None:
        cache.web_dialog_queue = []
    
    # 确保小对话框队列已初始化
    if not hasattr(cache, 'web_minor_dialog_queue') or cache.web_minor_dialog_queue is None:
        cache.web_minor_dialog_queue = []
    
    if is_minor:
        # 小对话框：只显示前10个字符
        truncated_text = text[:10] + "..." if len(text) > 10 else text
        # 移除换行符，只显示纯文本
        truncated_text = truncated_text.replace('\n', ' ')
        minor_entry = {
            "character_id": character_id,
            "speaker": speaker_name,
            "text": truncated_text,
            "full_text": text,  # 保存完整文本，点击时使用
            "text_color": text_color,
            "target_character_id": target_character_id,  # 保存该角色当时的交互对象ID
        }
        cache.web_minor_dialog_queue.append(minor_entry)
    else:
        # 主对话框：分页处理
        # 如果有交互对象，则将交互对象名称添加到说话者名称后
        display_speaker_name = speaker_name
        if target_character_id >= 0:
            target_character_data = cache.character_data.get(target_character_id)
            if target_character_data:
                display_speaker_name = f"{speaker_name} → {target_character_data.name}"
        
        pages = _split_text_to_pages(text)
        for i, page_text in enumerate(pages):
            dialog_entry = {
                "speaker": display_speaker_name,
                "text": page_text,
                "text_color": text_color,
                "wait_input": wait_input,
                "is_continuation": i > 0,  # 标记是否为续页
            }
            cache.web_dialog_queue.append(dialog_entry)
    
    # 如果对话框当前不可见且队列中有内容，立即显示
    if not is_minor and not cache.web_dialog_visible and len(cache.web_dialog_queue) > 0:
        advance_dialog()
    
    # 触发状态更新推送到前端
    _trigger_state_update()


def advance_dialog() -> bool:
    """
    推进对话文本（全局函数）
    
    Returns:
    bool -- True表示还有更多文本显示，False表示对话结束
    """
    # 确保队列已初始化
    if not hasattr(cache, 'web_dialog_queue') or cache.web_dialog_queue is None:
        cache.web_dialog_queue = []
    
    if cache.web_dialog_queue:
        next_dialog = cache.web_dialog_queue.pop(0)
        cache.web_dialog_visible = True
        cache.web_dialog_speaker = next_dialog.get("speaker", "")
        cache.web_dialog_text = next_dialog.get("text", "")
        cache.web_dialog_text_color = next_dialog.get("text_color", "standard")
        cache.web_dialog_wait_input = next_dialog.get("wait_input", True)
        return True
    else:
        hide_dialog()
        return False


def hide_dialog():
    """隐藏对话框（全局函数）"""
    cache.web_dialog_visible = False
    cache.web_dialog_speaker = ""
    cache.web_dialog_text = ""
    cache.web_dialog_text_color = "standard"
    cache.web_dialog_wait_input = False


def clear_dialog_queue():
    """清空对话队列（全局函数）"""
    if hasattr(cache, 'web_dialog_queue'):
        cache.web_dialog_queue = []
    hide_dialog()


def get_dialog_state() -> dict:
    """
    获取对话框当前状态（全局函数）
    
    Returns:
    dict -- 对话框状态数据
    """
    # 确保所有字段已初始化
    if not hasattr(cache, 'web_dialog_visible'):
        cache.web_dialog_visible = False
    if not hasattr(cache, 'web_dialog_speaker'):
        cache.web_dialog_speaker = ""
    if not hasattr(cache, 'web_dialog_text'):
        cache.web_dialog_text = ""
    if not hasattr(cache, 'web_dialog_text_color'):
        cache.web_dialog_text_color = "standard"
    if not hasattr(cache, 'web_dialog_queue'):
        cache.web_dialog_queue = []
    if not hasattr(cache, 'web_dialog_wait_input'):
        cache.web_dialog_wait_input = False
    if not hasattr(cache, 'web_minor_dialog_queue'):
        cache.web_minor_dialog_queue = []
    
    return {
        "visible": cache.web_dialog_visible,
        "speaker": cache.web_dialog_speaker,
        "text": cache.web_dialog_text,
        "text_color": cache.web_dialog_text_color,
        "has_more": len(cache.web_dialog_queue) > 0,
        "wait_input": cache.web_dialog_wait_input,
        "minor_dialogs": list(cache.web_minor_dialog_queue),  # 其他角色的小对话框列表
    }


def clear_minor_dialogs():
    """清空其他角色的小对话框（全局函数）"""
    if hasattr(cache, 'web_minor_dialog_queue'):
        cache.web_minor_dialog_queue = []


def skip_all_dialogs():
    """跳过所有剩余对话（全局函数）"""
    clear_dialog_queue()


class DialogBox:
    """
    对话框管理器
    负责管理对话框的显示状态和文本内容
    
    注意：此类现在是全局cache字段的封装器，用于面板组件的兼容性
    核心状态存储在cache.web_dialog_*字段中
    """

    def __init__(self):
        """初始化对话框管理器"""
        pass  # 状态现在由cache全局管理

    @property
    def is_visible(self) -> bool:
        """对话框是否可见"""
        return cache.web_dialog_visible if hasattr(cache, 'web_dialog_visible') else False

    @property
    def current_speaker(self) -> str:
        """当前说话者名称"""
        return cache.web_dialog_speaker if hasattr(cache, 'web_dialog_speaker') else ""

    @property
    def current_text(self) -> str:
        """当前对话文本"""
        return cache.web_dialog_text if hasattr(cache, 'web_dialog_text') else ""

    def show(self, speaker_name: str, text: str, text_color: str = "standard"):
        """
        显示对话框
        
        Keyword arguments:
        speaker_name -- 说话者名称
        text -- 对话文本
        text_color -- 文本颜色样式
        """
        add_dialog_text(speaker_name, text, text_color, wait_input=True)

    def hide(self):
        """隐藏对话框"""
        hide_dialog()

    def add_to_queue(self, speaker_name: str, text: str, text_color: str = "standard"):
        """
        将对话添加到队列
        
        Keyword arguments:
        speaker_name -- 说话者名称
        text -- 对话文本
        text_color -- 文本颜色样式
        """
        add_dialog_text(speaker_name, text, text_color, wait_input=True)

    def clear_queue(self):
        """清空对话队列"""
        clear_dialog_queue()

    def advance_text(self) -> bool:
        """
        推进对话文本
        
        Returns:
        bool -- True表示还有更多文本，False表示对话结束
        """
        return advance_dialog()

    def start_skip(self):
        """开始跳过模式"""
        skip_all_dialogs()

    def stop_skip(self):
        """停止跳过模式"""
        pass  # 跳过模式由前端控制

    @property
    def is_skipping(self) -> bool:
        """是否处于跳过模式"""
        return False  # 跳过模式由前端控制

    def get_state(self) -> dict:
        """
        获取对话框当前状态
        
        Returns:
        dict -- 对话框状态数据
        """
        return get_dialog_state()

    def skip_all(self):
        """跳过所有剩余对话"""
        skip_all_dialogs()
