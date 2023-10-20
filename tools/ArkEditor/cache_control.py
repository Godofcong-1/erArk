from typing import Dict, Set, List
import game_type

now_file_path: str = ""
""" 当前事件数据文件路径 """
now_edit_type_flag = 1
""" 当前编辑器编辑类型，0为口上，1为事件 """

now_talk_data: Dict[str, game_type.Talk] = {}
""" 当前口上数据 """


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
status_type_data: Dict[str, List] = {}
""" 状态类型数据 """
now_status: str = "1"
""" 当前事件状态 """
now_type: str = "跳过指令"
""" 当前事件类型 """
start_status: str = "开始"
""" 当前事件开始类型 """
now_adv_id: int = 0
""" 当前事件角色id """
now_select_id: str = ""
""" 当前选择的项目id """
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
ability_data: dict = {}
""" 能力数据 """
state_data: dict = {}
""" 当日子状态数据 """
experience_data: dict = {}
""" 经验数据 """
juel_data: dict = {}
""" 宝珠数据 """
talent_data: dict = {}
""" 素质数据 """
