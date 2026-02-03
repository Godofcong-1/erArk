# -*- coding: utf-8 -*-
"""
结算阶段管理器
负责处理Web模式下的结算演出流程

结算流程：
1. 指令执行后进入结算阶段
2. 收集所有角色的对话和数值变化
3. 依次显示对话，推进文本
4. 显示数值变化动画
5. 结算完成，恢复交互
"""

from enum import IntEnum
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from Script.Core import cache_control, game_type

cache: game_type.Cache = cache_control.cache


class SettlementPhase(IntEnum):
    """
    结算阶段枚举
    """
    IDLE = 0
    """ 空闲状态，可以进行交互 """
    
    SETTLING = 1
    """ 正在结算，处理角色行为 """
    
    DIALOG = 2
    """ 显示对话阶段 """
    
    VALUE_CHANGE = 3
    """ 显示数值变化阶段 """
    
    WAITING_INPUT = 4
    """ 等待玩家输入继续 """


@dataclass
class DialogEntry:
    """
    对话条目
    """
    character_id: int
    """ 角色ID """
    
    character_name: str
    """ 角色名称 """
    
    text: str
    """ 对话文本 """
    
    is_player_or_target: bool = False
    """ 是否为玩家或交互对象（决定显示方式） """
    
    text_lines: List[str] = field(default_factory=list)
    """ 拆分后的文本行 """


@dataclass
class ValueChangeEntry:
    """
    数值变化条目
    """
    character_id: int
    """ 角色ID """
    
    stat_name: str
    """ 状态名称 """
    
    old_value: float
    """ 旧值 """
    
    new_value: float
    """ 新值 """
    
    change: float = 0
    """ 变化量 """
    
    display_position: str = "default"
    """ 显示位置：player_info/target_info/default """


class SettlementManager:
    """
    结算阶段管理器
    负责管理结算流程中的对话和数值变化显示
    """

    def __init__(self):
        """初始化结算管理器"""
        self.phase: SettlementPhase = SettlementPhase.IDLE
        """ 当前结算阶段 """
        
        self.dialog_queue: List[DialogEntry] = []
        """ 对话队列 """
        
        self.current_dialog_index: int = 0
        """ 当前对话索引 """
        
        self.current_line_index: int = 0
        """ 当前文本行索引 """
        
        self.value_changes: List[ValueChangeEntry] = []
        """ 数值变化列表 """
        
        self.other_characters_dialogs: Dict[int, DialogEntry] = {}
        """ 其他角色的简略对话（用于头像上方显示） """
        
        # 回调函数
        self._on_phase_change: Optional[Callable[[SettlementPhase], None]] = None
        self._on_dialog_update: Optional[Callable[[DialogEntry, int], None]] = None
        self._on_value_change_show: Optional[Callable[[ValueChangeEntry], None]] = None

    def start_settlement(self, duration: int = 0):
        """
        开始结算阶段
        
        Keyword arguments:
        duration -- 结算持续时间（分钟），0表示不限
        """
        self.phase = SettlementPhase.SETTLING
        self.dialog_queue.clear()
        self.value_changes.clear()
        self.other_characters_dialogs.clear()
        self.current_dialog_index = 0
        self.current_line_index = 0
        
        if self._on_phase_change:
            self._on_phase_change(self.phase)

    def add_dialog(
        self,
        character_id: int,
        text: str,
        is_player_or_target: bool = False
    ):
        """
        添加对话到队列
        
        Keyword arguments:
        character_id -- 角色ID
        text -- 对话文本
        is_player_or_target -- 是否为玩家或交互对象
        """
        char_data = cache.character_data.get(character_id)
        char_name = char_data.name if char_data else f"角色{character_id}"
        
        # 拆分多行文本
        text_lines = text.split('\n') if text else []
        
        entry = DialogEntry(
            character_id=character_id,
            character_name=char_name,
            text=text,
            is_player_or_target=is_player_or_target,
            text_lines=text_lines
        )
        
        if is_player_or_target:
            self.dialog_queue.append(entry)
        else:
            # 其他角色的对话存储到单独的字典
            self.other_characters_dialogs[character_id] = entry

    def add_value_change(
        self,
        character_id: int,
        stat_name: str,
        old_value: float,
        new_value: float,
        display_position: str = "default"
    ):
        """
        添加数值变化记录
        
        Keyword arguments:
        character_id -- 角色ID
        stat_name -- 状态名称
        old_value -- 旧值
        new_value -- 新值
        display_position -- 显示位置
        """
        change = new_value - old_value
        if change == 0:
            return  # 无变化则不添加
        
        entry = ValueChangeEntry(
            character_id=character_id,
            stat_name=stat_name,
            old_value=old_value,
            new_value=new_value,
            change=change,
            display_position=display_position
        )
        self.value_changes.append(entry)

    def start_dialog_phase(self):
        """
        进入对话显示阶段
        """
        if not self.dialog_queue:
            # 没有对话，直接进入数值变化阶段
            self.start_value_change_phase()
            return
        
        self.phase = SettlementPhase.DIALOG
        self.current_dialog_index = 0
        self.current_line_index = 0
        
        if self._on_phase_change:
            self._on_phase_change(self.phase)
        
        # 显示第一条对话
        self._show_current_dialog()

    def advance_dialog(self, skip: bool = False) -> bool:
        """
        推进对话
        
        Keyword arguments:
        skip -- 是否跳过当前角色的所有对话
        
        Returns:
        bool -- 是否还有更多对话
        """
        if self.phase != SettlementPhase.DIALOG:
            return False
        
        if not self.dialog_queue:
            self.start_value_change_phase()
            return False
        
        current_dialog = self.dialog_queue[self.current_dialog_index]
        
        if skip:
            # 跳过当前角色的对话
            self.current_dialog_index += 1
            self.current_line_index = 0
        else:
            # 推进到下一行
            self.current_line_index += 1
            
            # 检查当前对话是否完成
            if self.current_line_index >= len(current_dialog.text_lines):
                self.current_dialog_index += 1
                self.current_line_index = 0
        
        # 检查是否所有对话完成
        if self.current_dialog_index >= len(self.dialog_queue):
            self.start_value_change_phase()
            return False
        
        # 显示下一条对话
        self._show_current_dialog()
        return True

    def _show_current_dialog(self):
        """
        显示当前对话
        """
        if self.current_dialog_index >= len(self.dialog_queue):
            return
        
        dialog = self.dialog_queue[self.current_dialog_index]
        
        if self._on_dialog_update:
            self._on_dialog_update(dialog, self.current_line_index)

    def start_value_change_phase(self):
        """
        进入数值变化显示阶段
        """
        if not self.value_changes:
            # 没有数值变化，结算完成
            self.finish_settlement()
            return
        
        self.phase = SettlementPhase.VALUE_CHANGE
        
        if self._on_phase_change:
            self._on_phase_change(self.phase)
        
        # 显示所有数值变化
        for entry in self.value_changes:
            if self._on_value_change_show:
                self._on_value_change_show(entry)

    def finish_settlement(self):
        """
        结束结算阶段
        """
        self.phase = SettlementPhase.IDLE
        
        if self._on_phase_change:
            self._on_phase_change(self.phase)

    def get_state(self) -> Dict:
        """
        获取当前结算状态数据
        
        Returns:
        Dict -- 状态数据
        """
        current_dialog = None
        current_line = ""
        
        if (self.phase == SettlementPhase.DIALOG 
            and self.current_dialog_index < len(self.dialog_queue)):
            dialog = self.dialog_queue[self.current_dialog_index]
            current_dialog = {
                "character_id": dialog.character_id,
                "character_name": dialog.character_name,
                "is_player_or_target": dialog.is_player_or_target,
            }
            if self.current_line_index < len(dialog.text_lines):
                current_line = dialog.text_lines[self.current_line_index]
        
        # 构建其他角色的简略对话数据
        other_dialogs = {}
        for char_id, entry in self.other_characters_dialogs.items():
            # 截取前20个字符
            short_text = entry.text[:20] + "..." if len(entry.text) > 20 else entry.text
            other_dialogs[char_id] = {
                "character_name": entry.character_name,
                "short_text": short_text,
                "has_full_text": len(entry.text) > 20,
            }
        
        return {
            "phase": self.phase,
            "phase_name": self.phase.name,
            "is_settling": self.phase != SettlementPhase.IDLE,
            "current_dialog": current_dialog,
            "current_line": current_line,
            "dialog_progress": {
                "current": self.current_dialog_index,
                "total": len(self.dialog_queue),
            },
            "other_characters_dialogs": other_dialogs,
            "value_changes": [
                {
                    "character_id": vc.character_id,
                    "stat_name": vc.stat_name,
                    "change": vc.change,
                    "display_position": vc.display_position,
                }
                for vc in self.value_changes
            ]
        }

    def get_full_dialog(self, character_id: int) -> Optional[str]:
        """
        获取某个角色的完整对话（用于头像点击查看）
        
        Keyword arguments:
        character_id -- 角色ID
        
        Returns:
        Optional[str] -- 完整对话文本，如果不存在返回None
        """
        entry = self.other_characters_dialogs.get(character_id)
        if entry:
            return entry.text
        return None

    def set_on_phase_change(self, callback: Callable[[SettlementPhase], None]):
        """设置阶段变化回调"""
        self._on_phase_change = callback

    def set_on_dialog_update(self, callback: Callable[[DialogEntry, int], None]):
        """设置对话更新回调"""
        self._on_dialog_update = callback

    def set_on_value_change_show(self, callback: Callable[[ValueChangeEntry], None]):
        """设置数值变化显示回调"""
        self._on_value_change_show = callback

    def clear(self):
        """清除所有状态"""
        self.phase = SettlementPhase.IDLE
        self.dialog_queue.clear()
        self.value_changes.clear()
        self.other_characters_dialogs.clear()
        self.current_dialog_index = 0
        self.current_line_index = 0
