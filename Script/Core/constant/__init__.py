from typing import Dict, List, Set
from types import FunctionType
from Script.Core import get_text

from Script.Core.constant.CharacterStatus import CharacterStatus
from Script.Core.constant.Behavior import Behavior
from Script.Core.constant.StateMachine import StateMachine
from Script.Core.constant.SecondBehavior import SecondBehavior
from Script.Core.constant.Instruct import Instruct

_: FunctionType = get_text._
""" 翻译api """

class Panel:
    """面板id"""

    TITLE = 0
    """ 标题面板 """
    CREATOR_CHARACTER = 1
    """ 创建角色面板 """
    IN_SCENE = 2
    """ 场景互动面板 """
    SEE_MAP = 3
    """ 查看地图面板 """
    FOOD_SHOP = 4
    """ 食物商店面板 """
    FOOD_BAG = 5
    """ 食物背包面板 """
    H_ITEM_SHOP = 6
    """ 成人用品商店面板 """
    MAKE_FOOD = 7
    """ 做饭面板 """
    ALL_NPC_POSITION = 8
    """ 查询与召集面板 """
    EJACULATION = 9
    """ 射精面板 """
    DIRTY = 10
    """ 脏污面板 """
    ITEM = 11
    """ 道具面板 """
    ASSISTANT = 12
    """ 助理面板 """
    COLLECTION = 13
    """ 收藏品面板 """
    UNDRESS = 14
    """ 脱衣服面板 """
    BUILDING = 15
    """ 基建面板 """
    MANAGE_BASEMENT = 16
    """ 管理罗德岛面板 """
    INSTRUCT_FILTER = 17
    """ 指令过滤面板 """
    EVENT_OPTION = 18
    """ 事件选项面板 """
    CHECK_LOCKER = 19
    """ 检查衣柜面板 """
    BORROW_BOOK = 20
    """ 借阅书籍面板 """
    MANAGE_LIBRARY = 21
    """ 图书馆管理面板 """
    DEBUG_ADJUST = 22
    """ DEBUG面板 """
    ORIGINIUM_ARTS = 23
    """ 源石技艺面板 """
    PRTS = 24
    """ 普瑞赛斯面板 """
    NAVIGATION = 25
    """ 导航面板 """
    RECRUITMENT = 26
    """ 招募面板 """
    VISITOR = 27
    """ 访客面板 """
    FRIDGE = 28
    """ 冰箱面板 """
    SYSTEM_SETTING = 29
    """ 系统设置面板 """
    AROMATHERAPY = 30
    """ 香薰疗愈面板 """
    NATION_DIPLOMACY = 31
    """ 势力外交面板 """
    CHAT_AI_SETTING = 32
    """ 文本生成AI设置面板 """
    PHYSICAL_CHECK_AND_MANAGE = 35
    """ 身体检查与管理面板 """


class InstructType:
    """指令类型"""

    SYSTEM = 0
    """ 系统 """
    DAILY = 1
    """ 日常 """
    PLAY = 2
    """ 娱乐 """
    WORK = 3
    """ 工作 """
    ARTS = 4
    """ 技艺 """
    OBSCENITY = 5
    """ 猥亵 """
    SEX = 6
    """ 性爱 """


class SexInstructSubType:
    """性爱指令子类型"""

    BASE = 0
    """ 基础 """
    WAIT_UPON = 1
    """ 侍奉 """
    DRUG = 2
    """ 药物 """
    ITEM = 3
    """ 道具 """
    INSERT = 4
    """ 插入 """
    SM = 5
    """ SM """
    ARTS = 6
    """ 技艺 """



i = 0
for k in Instruct.__dict__:
    if isinstance(Instruct.__dict__[k], int):
        setattr(Instruct, k, i)
        i += 1


handle_premise_data: Dict[str, FunctionType] = {}
""" 前提处理数据 """
handle_instruct_data: Dict[int, FunctionType] = {}
""" 指令处理数据 """
handle_instruct_name_data: Dict[int, str] = {}
""" 指令对应文本 """
instruct_type_data: Dict[int, Set] = {}
""" 指令类型拥有的指令集合 """
instruct_sub_type_data: Dict[int, int] = {}
""" 指令的子类型数据，指令id:子类id """
state_id_to_instruct_id: Dict[int, int] = {}
""" 从状态id获取指令id，状态id:指令id """
instruct_premise_data: Dict[int, Set] = {}
""" 指令显示的所需前提集合 """
handle_state_machine_data: Dict[int, FunctionType] = {}
""" 角色状态机函数 """
family_region_list: Dict[int, str] = {}
""" 姓氏区间数据 """
boys_region_list: Dict[int, str] = {}
""" 男孩名字区间数据 """
girls_region_list: Dict[int, str] = {}
""" 女孩名字区间数据 """
family_region_int_list: List[int] = []
""" 姓氏权重区间数据 """
boys_region_int_list: List[int] = []
""" 男孩名字权重区间数据 """
girls_region_int_list: List[int] = []
""" 女孩名字权重区间数据 """
panel_data: Dict[int, FunctionType] = {}
"""
面板id对应的面板绘制函数集合
面板id:面板绘制函数对象
"""
place_data: Dict[str, List[str]] = {}
""" 按房间类型分类的场景列表 场景标签:场景路径列表 """
cmd_map: Dict[int, FunctionType] = {}
""" cmd存储 """
settle_behavior_effect_data: Dict[int, FunctionType] = {}
""" 角色行为结算处理器 处理器id:处理器 """
settle_second_behavior_effect_data: Dict[int, FunctionType] = {}
""" 角色二段行为结算处理器 处理器id:处理器 """

first_NPC_name_set = {_("阿米娅"),_("凯尔希"),_("可露希尔"),_("特蕾西娅"),_("华法琳"),_("杜宾")}
""" 初始就有的NPC的名字 """

ban_NPC_name_set = {_("普瑞赛斯"),_("炉芯终曲阿米娅"),_("老天师"),_("魔王"),_("菈玛莲"),_("塔露拉"),_("莉泽洛特"),_("希尔德加德"),_("坎黛拉"),_("克丽斯腾"),_("爱布拉娜"),_("温德米尔"),_("赫拉提娅"),_("文月"),_("年"),_("夕"),_("令"),_("黍")}
""" 无法直接招募到的NPC的名字 """

special_end_H_list = [Behavior.H_INTERRUPT, Behavior.H_HP_0, Behavior.T_H_HP_0, Behavior.GROUP_SEX_PL_HP_0_END]
""" 意外中断H的行为id列表 """

chat_ai_model_list = ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo', 'gpt-4o', 'gpt-4o-mini', 'gemini-1.5-pro', 'gemini-1.5-flash']
""" 文本生成的AI模型列表 """

tired_text_list = [_("清醒"), _("疲劳"), _("昏昏欲睡"), _("随时睡着")]
""" 困倦状态文本列表 """

# 协力名单，不分先后 依吹脆香，反R，幻白，无色树，灵鸠伊凛，诺伊，√，はるか