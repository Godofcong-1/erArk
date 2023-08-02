from typing import Dict, Set
import game_type

now_file_path: str = ""
""" 当前事件数据文件路径 """
now_event_name: str = ""
""" 当前事件名称 """
now_event_data: Dict[str, game_type.Event] = {}
""" 当前事件数据 """
premise_data: dict = {}
""" 前提数据 """
premise_type_data: Dict[str, Set] = {}
""" 前提类型数据 """
status_data: dict = {}
""" 当前状态数据 """
now_status: str = "1"
""" 当前事件状态 """
now_type: str = "指令正常"
""" 当前事件类型 """
start_status: str = "开始"
""" 当前事件开始类型 """
now_adv_id: int = 0
""" 当前事件角色id """
now_event_id: str = ""
""" 当前事件id """
settle_data: Dict[str, str] = {}
""" 结算器数据 """
settle_type_data: Dict[str, Dict[set, Set]] = {}
""" 结算器类型数据 """
item_premise_list = None
""" 事件前提列表 """
item_effect_list = None
""" 事件结算列表 """
item_text_edit = None
""" 事件文本编辑框 """
effect_data: dict = {}
""" 结算数据 """
effect_type_data: Dict[str, Set] = {}
""" 结算类型数据 """
