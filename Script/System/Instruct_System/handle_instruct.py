import time
import queue
import datetime
from functools import wraps
from typing import Set, List, Optional, Union
from types import FunctionType
from threading import Thread
from Script.Core import constant, constant_promise, cache_control, game_type, get_text, flow_handle
from Script.Design import handle_ability, update, map_handle, character_behavior, instuct_judege, handle_npc_ai_in_h, handle_premise
from Script.UI.Panel import achievement_panel, normal_panel
from Script.Config import normal_config, game_config
from Script.UI.Moudle import draw

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """
width: int = normal_config.config_normal.text_width
""" 屏幕宽度 """
instruct_queue = queue.Queue()
""" 待处理的指令队列 """


def init_instruct_handle_thread():
    """初始化指令处理线程"""
    while 1:
        if not instruct_queue.empty():
            instruct_queue.get()
            # 注释掉自动存档机制来解决卡顿问题
            # save_handle.establish_save("auto")
        time.sleep(1)


instruct_handle_thread = Thread(target=init_instruct_handle_thread)
""" 指令处理线程 """
instruct_handle_thread.start()


def handle_instruct(instruct: str):
    """
    处理执行指令
    Keyword arguments:
    instruct -- 指令id（字符串）
    """
    instruct_queue.put(instruct)
    if instruct in constant.instruct_premise_data:
        constant.handle_instruct_data[instruct]()


# ========== 指令类型映射 ==========
INSTRUCT_TYPE_MAP = {
    "SYSTEM": constant.InstructType.SYSTEM,
    "DAILY": constant.InstructType.DAILY,
    "PLAY": constant.InstructType.PLAY,
    "WORK": constant.InstructType.WORK,
    "ARTS": constant.InstructType.ARTS,
    "OBSCENITY": constant.InstructType.OBSCENITY,
    "SEX": constant.InstructType.SEX,
    "STUDY": 7,  # 如果存在
}

# ========== 子类型映射 ==========
SUB_TYPE_MAP = {
    "0": 0,
    "BASE": constant.SexInstructSubType.BASE if hasattr(constant, 'SexInstructSubType') else 0,
    "FOREPLAY": constant.SexInstructSubType.FOREPLAY if hasattr(constant, 'SexInstructSubType') else 1,
    "WAIT_UPON": constant.SexInstructSubType.WAIT_UPON if hasattr(constant, 'SexInstructSubType') else 2,
    "DRUG": constant.SexInstructSubType.DRUG if hasattr(constant, 'SexInstructSubType') else 3,
    "ITEM": constant.SexInstructSubType.ITEM if hasattr(constant, 'SexInstructSubType') else 4,
    "INSERT": constant.SexInstructSubType.INSERT if hasattr(constant, 'SexInstructSubType') else 5,
    "SM": constant.SexInstructSubType.SM if hasattr(constant, 'SexInstructSubType') else 6,
    "ARTS": 7,
}


def add_instruct(
    instruct_id: str,
    instruct_type: int = None,
    name: str = None,
    premise_set: Set = None,
    behavior_id: str = None,
    sub_type: int = None,
):
    """
    添加指令处理
    
    新版本：所有参数都可以从CSV配置中读取，装饰器参数优先级高于CSV配置
    
    Keyword arguments:
    instruct_id -- 指令id（字符串，如 "move", "chat"）
    instruct_type -- 指令类型（可选，不传则从CSV读取）
    name -- 指令绘制文本（可选，不传则从CSV读取）
    premise_set -- 指令所需前提集合（可选，不传则从CSV读取）
    behavior_id -- 行为id（可选，不传则从CSV读取）
    sub_type -- 指令子类型（可选，不传则从CSV读取）
    """

    def decorator(func: FunctionType):
        @wraps(func)
        def return_wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # 从CSV配置读取参数（如果未在装饰器中指定）
        csv_config_cid = game_config.config_instruct_by_id.get(instruct_id)
        csv_config = game_config.config_instruct.get(csv_config_cid) if csv_config_cid is not None else None
        
        # 解析指令类型
        actual_instruct_type = instruct_type
        if actual_instruct_type is None and csv_config:
            type_str = getattr(csv_config, 'instruct_type', None)
            if type_str:
                actual_instruct_type = INSTRUCT_TYPE_MAP.get(type_str, constant.InstructType.DAILY)
        if actual_instruct_type is None:
            actual_instruct_type = constant.InstructType.DAILY
        
        # 解析显示名称
        actual_name = name
        if actual_name is None and csv_config:
            actual_name = getattr(csv_config, 'name', None) or instruct_id
        if actual_name is None:
            actual_name = instruct_id
        
        # 解析前提条件集
        actual_premise_set = premise_set
        if actual_premise_set is None and csv_config:
            premise_str = getattr(csv_config, 'premise_set', None)
            if premise_str:
                actual_premise_set = set()
                for premise_name in premise_str.split('|'):
                    premise_name = premise_name.strip()
                    if premise_name and hasattr(constant_promise.Premise, premise_name):
                        actual_premise_set.add(getattr(constant_promise.Premise, premise_name))
            else:
                actual_premise_set = set()
        if actual_premise_set is None:
            actual_premise_set = set()
        
        # 解析行为ID
        actual_behavior_id = behavior_id
        if actual_behavior_id is None and csv_config:
            behavior_str = getattr(csv_config, 'behavior_id', None)
            if behavior_str and hasattr(constant.Behavior, behavior_str):
                actual_behavior_id = getattr(constant.Behavior, behavior_str)
            elif behavior_str:
                actual_behavior_id = behavior_str
        if actual_behavior_id is None:
            actual_behavior_id = "share_blankly"
        
        # 解析子类型
        actual_sub_type = sub_type
        if actual_sub_type is None and csv_config:
            sub_type_val = getattr(csv_config, 'instruct_sub_type', None)
            sub_type_str = str(sub_type_val) if sub_type_val is not None else "0"
            actual_sub_type = SUB_TYPE_MAP.get(sub_type_str, 0)
            if actual_sub_type == sub_type_str:  # 如果没找到映射，尝试转为整数
                try:
                    actual_sub_type = int(sub_type_str)
                except:
                    actual_sub_type = 0
        if actual_sub_type is None:
            actual_sub_type = 0

        # 注册指令处理函数
        constant.handle_instruct_data[instruct_id] = return_wrapper
        constant.instruct_premise_data[instruct_id] = actual_premise_set
        constant.instruct_type_data.setdefault(actual_instruct_type, set())
        constant.instruct_type_data[actual_instruct_type].add(instruct_id)
        constant.behavior_id_to_instruct_id[actual_behavior_id] = instruct_id
        constant.instruct_sub_type_data[instruct_id] = actual_sub_type
        constant.handle_instruct_name_data[instruct_id] = actual_name
        
        # 注册ID映射（从 CSV 中读取 cid）
        if csv_config:
            cid = getattr(csv_config, 'cid', None)
            if cid is not None:
                constant.instruct_id_to_cid[instruct_id] = cid
                constant.cid_to_instruct_id[cid] = instruct_id
        
        # ========== Web模式分类数据注册（从CSV数据库读取）==========
        major_type = None
        minor_type = None
        body_parts = []
        category = None
        
        if csv_config:
            # 从新的完整配置中读取web相关数据
            # 使用 getattr 安全访问属性，因为 CSV 空字段不会创建属性
            # 大类和小类现在使用字符串标识符，而非数字
            major_type_val = getattr(csv_config, 'web_major_type', None)
            if major_type_val is not None and major_type_val != '':
                # 现在 major_type 是字符串，如 'mouth', 'hand' 等
                if isinstance(major_type_val, str) and not major_type_val.isdigit():
                    major_type = major_type_val
                else:
                    major_type = None
            
            minor_type_val = getattr(csv_config, 'web_minor_type', None)
            if minor_type_val is not None and minor_type_val != '':
                # 现在 minor_type 是字符串，如 'mouth_talk', 'hand_touch' 等
                if isinstance(minor_type_val, str) and not minor_type_val.isdigit():
                    minor_type = minor_type_val
                else:
                    minor_type = None
            
            body_parts_val = getattr(csv_config, 'body_parts', None)
            body_parts = []
            if body_parts_val:
                body_parts = [p.strip() for p in body_parts_val.split('|') if p.strip()]
            
            category_val = getattr(csv_config, 'web_category', None)
            if category_val is not None and category_val != '':
                try:
                    category = int(category_val)
                except:
                    category = None

            panel_id = getattr(csv_config, 'panel_id', None)
            if panel_id is not None and panel_id != '':
                try:
                    panel_id = constant.Panel.__dict__[panel_id]
                except:
                    panel_id = None
                if panel_id is not None:
                    constant.instruct_panel_id_data[instruct_id] = panel_id

        # 自动推断指令大类（基于指令类型和函数源代码分析）
        actual_category = category
        actual_panel_id = panel_id
        
        if actual_category is None:
            # 尝试通过分析函数源代码自动推断
            import inspect
            import re
            try:
                source = inspect.getsource(func)
                # 检查是否是系统面板类：函数内容为 cache.now_panel_id = xxx
                if "cache.now_panel_id" in source and "now_panel.draw()" not in source:
                    actual_category = constant.InstructCategory.SYSTEM_PANEL
                    # 尝试提取 panel_id
                    match = re.search(r'cache\.now_panel_id\s*=\s*constant\.Panel\.(\w+)', source)
                    if match:
                        panel_name = match.group(1)
                        actual_panel_id = getattr(constant.Panel, panel_name, None)
                # 检查是否是角色交互面板类：函数内容带有 now_panel.draw()
                elif "now_panel.draw()" in source:
                    actual_category = constant.InstructCategory.CHARACTER_PANEL
                # 根据指令类型推断
                elif actual_instruct_type == constant.InstructType.SYSTEM:
                    actual_category = constant.InstructCategory.SYSTEM_PANEL
                elif actual_instruct_type in (constant.InstructType.OBSCENITY, constant.InstructType.SEX):
                    actual_category = constant.InstructCategory.CHARACTER
                else:
                    actual_category = constant.InstructCategory.CHARACTER
            except:
                # 无法获取源代码时使用默认推断
                if actual_instruct_type == constant.InstructType.SYSTEM:
                    actual_category = constant.InstructCategory.SYSTEM_PANEL
                elif actual_instruct_type in (constant.InstructType.OBSCENITY, constant.InstructType.SEX):
                    actual_category = constant.InstructCategory.CHARACTER
                else:
                    actual_category = constant.InstructCategory.CHARACTER
        
        constant.instruct_category_data[instruct_id] = actual_category
        
        # 记录面板ID（仅系统面板类有效）
        if actual_panel_id is not None:
            constant.instruct_panel_id_data[instruct_id] = actual_panel_id
        
        # 记录Web模式交互类型数据
        if major_type is not None:
            constant.instruct_major_type_data[instruct_id] = major_type
        if minor_type is not None:
            constant.instruct_minor_type_data[instruct_id] = minor_type
        constant.instruct_body_parts_data[instruct_id] = body_parts
        # ==========================================
        
        # print(f"debug 添加指令处理 instruct_id:{instruct_id} name:{actual_name}")
        return return_wrapper

    return decorator


def instruct_filter_H_change(on_off_flag: bool):
    """
    指令类型过滤器进出H变更（已弃用）
    Keyword arguments:
    on_off_flag -- true:进入H false:退出H
    """
    if on_off_flag:
        cache.instruct_type_filter_cache = cache.instruct_type_filter.copy()
        # 自动开启性爱面板并关闭其他面板
        cache.instruct_type_filter[6] = True
        for i in {1, 2, 3, 4, 5}:
            cache.instruct_type_filter[i] = False
        # print(f"debug 开启H面板，关闭其他面板")
    elif len(cache.instruct_type_filter_cache):
        cache.instruct_type_filter = cache.instruct_type_filter_cache.copy()
        # print(f"debug 关闭H面板，恢复其他面板")


def chara_handle_instruct_common_settle(
        behavior_id: str,
        character_id: int = 0,
        target_character_id: int = 0,
        duration: int = 0,
        judge: str = "",
        game_update_flag: bool = False,
        force_taget_wait: bool = False,
):
    """
    角色处理指令通用结算函数\n
    Keyword arguments:\n
    state_id -- 状态id\n
    character_id -- 角色id，默认=0时为玩家指令\n
    target_character_id -- 指定目标角色id，默认=0时没有指定目标角色\n
    behevior_id -- 行动id，默认=0时为同状态id\n
    duration -- 行动持续时间，默认=0时进行查表获得\n
    judge -- 进行指令判断，默认为空\n
    game_update_flag -- 是否强制更新游戏流程，默认=False\n
    force_taget_wait -- 是否强制目标等待，默认=False\n
    """
    from Script.System.Sex_System import group_sex_panel
    # print(f"debug 角色处理指令通用结算函数 state_id:{state_id} character_id:{character_id} behevior_id:{behevior_id} duration:{duration}")
    instuct_judege.init_character_behavior_start_time(character_id, cache.game_time)
    character_data: game_type.Character = cache.character_data[character_id]
    # 如果有指定目标角色id，则设置目标角色id
    if target_character_id != 0:
        character_data.target_character_id = target_character_id
    else:
        target_character_id = character_data.target_character_id
    # 如果有判断条件，则先进行判断
    if judge != "":
        judge_list = instuct_judege.calculation_instuct_judege(character_id, character_data.target_character_id, judge)
        if judge_list[0] == 0:
            judge_to_behavior_id = {
                _("初级骚扰"): constant.Behavior.LOW_OBSCENITY_ANUS,
                _("道具"): constant.Behavior.LOW_OBSCENITY_ANUS,
                _("口交"): constant.Behavior.LOW_OBSCENITY_ANUS,
                _("严重骚扰"): constant.Behavior.HIGH_OBSCENITY_ANUS,
                _("药物"): constant.Behavior.HIGH_OBSCENITY_ANUS,
                _("SM"): constant.Behavior.HIGH_OBSCENITY_ANUS,
                _("性交"): constant.Behavior.HIGH_OBSCENITY_ANUS,
                _("A性交"): constant.Behavior.HIGH_OBSCENITY_ANUS,
                _("U开发"): constant.Behavior.HIGH_OBSCENITY_ANUS,
                _("U性交"): constant.Behavior.HIGH_OBSCENITY_ANUS,
                _("亲吻"): constant.Behavior.KISS_FAIL,
                _("H模式"): constant.Behavior.DO_H_FAIL,
            }
            behavior_id = judge_to_behavior_id.get(judge, behavior_id)
        elif judge_list[0] == -1:
            return 0
    character_data.state = behavior_id
    # 获取行为数据
    behavior_data = game_config.config_behavior[behavior_id]
    character_data.behavior.behavior_id = behavior_id
    # 查表获取行动持续时间
    if duration == 0:
        duration = behavior_data.duration
        # 如果持续时间小于等于0，则持续时间为1
        if duration <= 0:
            duration = 1
    character_data.behavior.duration = duration
    # 如果强制目标等待，则将目标角色状态设置为等待
    if target_character_id != character_id and force_taget_wait:
        instuct_judege.init_character_behavior_start_time(target_character_id, cache.game_time)
        target_character_data: game_type.Character = cache.character_data[target_character_id]
        target_character_data.state = constant.CharacterStatus.STATUS_WAIT
        target_character_data.behavior.behavior_id = constant.Behavior.WAIT
        target_character_data.behavior.duration = duration
    # 群交结算
    group_sex_panel.group_sex_settle(character_id, target_character_id, behavior_id)
    # 仅在玩家指令时更新游戏流程
    if character_id == 0 or game_update_flag:
        update.game_update_flow(duration)


def handle_comprehensive_state_effect(
        effect_all_value_list: list,
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    综合指令行为结算
    Keyword arguments:
    effect_all_value_list -- 结算的各项数值
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    # print(f"debug effect_all_value_list:{effect_all_value_list}")
    character_data: game_type.Character = cache.character_data[0]
    # 进行主体A的判别，A1为自己，A2为交互对象，A3为指定id角色(格式为A3|15)
    if effect_all_value_list[0] == "A1":
        target_character_id = 0
    elif effect_all_value_list[0] == "A2":
        # 如果是NPC触发且该NPC不是玩家当前的交互对象，则将其设为交互对象
        if character_id != 0 and character_id != character_data.target_character_id:
            character_data.target_character_id = character_id
        # 如果没有交互对象，则返回0
        if character_data.target_character_id == 0:
            return 0
        target_character_id = character_data.target_character_id
    elif effect_all_value_list[0][:2] == "A3":
        target_character_id = int(effect_all_value_list[0][3:])
        # 如果还没拥有该角色，则返回0
        if target_character_id not in cache.npc_id_got:
            return 0

    behavior_id = effect_all_value_list[1]
    chara_handle_instruct_common_settle(behavior_id, target_character_id = target_character_id, game_update_flag = True)


@add_instruct(constant.Instruct.REST)
def handle_rest():
    """处理休息指令"""
    chara_handle_instruct_common_settle(constant.Behavior.REST, force_taget_wait = True)


@add_instruct(constant.Instruct.BUY_FOOD)
def handle_buy_food():
    """处理购买食物指令"""
    cache.now_panel_id = constant.Panel.FOOD_SHOP


@add_instruct(constant.Instruct.EAT)
def handle_eat():
    """处理进食指令"""
    cache.now_panel_id = constant.Panel.FOOD_BAG


@add_instruct(constant.Instruct.PUT_SELFMADE_FOOD_IN)
def handle_put_selfmade_food_in():
    """处理放入正常食物指令"""
    from Script.UI.Panel import food_shop_panel
    food_shop_panel.put_selfmade_food_in()


@add_instruct(constant.Instruct.MOVE)
def handle_move():
    """处理移动指令"""
    cache.now_panel_id = constant.Panel.SEE_MAP


@add_instruct(constant.Instruct.SEE_ATTR)
def handle_see_attr():
    """查看属性"""
    cache.now_panel_id = constant.Panel.SEE_ATTR


@add_instruct(constant.Instruct.CHAT)
def handle_chat():
    """处理聊天指令"""
    character_data = cache.character_data[0]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.action_info.talk_count > character_data.ability[40] + 1:
        chara_handle_instruct_common_settle(constant.Behavior.CHAT_FAILED)
    else:
        chara_handle_instruct_common_settle(constant.Behavior.CHAT)
    target_data.action_info.talk_count += 1
    # print("聊天计数器+1，现在为 ：",target_data.action_info.talk_count)


@add_instruct(constant.Instruct.BUY_H_ITEM)
def handle_buy_h_item():
    """处理购买成人用品指令"""
    cache.now_panel_id = constant.Panel.H_ITEM_SHOP


@add_instruct(constant.Instruct.ITEM)
def handle_item():
    """处理道具指令"""
    cache.now_panel_id = constant.Panel.ITEM


@add_instruct(constant.Instruct.SAVE)
def handle_save():
    """处理读写存档指令"""
    cache.now_panel_id = constant.Panel.SAVE


@add_instruct(constant.Instruct.ABL_UP)
def handle_abl_up():
    """处理属性上升"""
    cache.now_panel_id = constant.Panel.ABL_UP


@add_instruct(constant.Instruct.OWNER_ABL_UP)
def handle_owner_abl_up():
    """处理自身属性上升"""
    cache.now_panel_id = constant.Panel.OWNER_ABL_UP


@add_instruct(constant.Instruct.DEBUG_MODE_ON)
def debug_mode():
    """处理开启DEBUG模式指令"""
    cache.debug_mode = True


@add_instruct(constant.Instruct.DEBUG_MODE_OFF)
def debug_mode_off():
    """处理关闭DEBUG模式指令"""
    cache.debug_mode = False


@add_instruct(constant.Instruct.DEBUG_ADJUST)
def debug_adjust():
    """处理debug数值调整指令"""
    cache.now_panel_id = constant.Panel.DEBUG_ADJUST


@add_instruct(constant.Instruct.SYSTEM_SETTING)
def handle_system_setting():
    """系统设置"""
    cache.now_panel_id = constant.Panel.SYSTEM_SETTING


@add_instruct(constant.Instruct.TALK_QUICK_TEST)
def handle_talk_quick_test():
    """快速测试口上"""
    cache.now_panel_id = constant.Panel.TALK_QUICK_TEST


@add_instruct(constant.Instruct.CHAT_WITH_AI)
def handle_chat_with_ai():
    """与文本生成AI对话"""
    from Script.Design import handle_chat_ai
    handle_chat_ai.direct_chat_with_ai()


@add_instruct(constant.Instruct.TEACH)
def handle_teach():
    """处理授课指令"""
    instuct_judege.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.TEACH
    character_data.behavior.duration = 45
    character_data.state = constant.CharacterStatus.STATUS_TEACH
    # 将当前场景里所有工作是上学的角色变为学习状态
    # 遍历当前场景的其他角色
    scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    scene_data: game_type.Scene = cache.scene_data[scene_path_str]
    # 场景角色数大于等于2时进行检测
    if len(scene_data.character_list) >= 2:
        # 遍历当前角色列表
        for chara_id in scene_data.character_list:
            # 跳过自己
            if chara_id == 0:
                continue
            else:
                other_character_data: game_type.Character = cache.character_data[chara_id]
                # 让对方变成听课状态
                if other_character_data.work.work_type == 152:
                    other_character_data.behavior.behavior_id = constant.Behavior.ATTENT_CLASS
                    other_character_data.behavior.duration = 45
                    other_character_data.state = constant.CharacterStatus.STATUS_ATTENT_CLASS
    update.game_update_flow(45)


@add_instruct(constant.Instruct.BORROW_BOOK)
def handle_borrow_book():
    """处理借阅书籍指令"""
    cache.now_panel_id = constant.Panel.BORROW_BOOK


@add_instruct(constant.Instruct.READ_BOOK)
def handle_read_book():
    """处理读书指令"""
    cache.now_panel_id = constant.Panel.READ_BOOK


@add_instruct(constant.Instruct.MANAGE_LIBRARY)
def handle_manage_library():
    """处理管理图书馆指令"""
    cache.now_panel_id = constant.Panel.MANAGE_LIBRARY


@add_instruct(constant.Instruct.MANAGE_ASSEMBLY_LINE)
def handle_manage_assembly_line():
    """处理管理流水线指令"""
    cache.now_panel_id = constant.Panel.MANAGE_ASSEMBLY_LINE


@add_instruct(constant.Instruct.PLANT_MANAGE_CROP)
def handle_plant_manage_crop():
    """处理种植与养护作物指令"""
    chara_handle_instruct_common_settle(constant.Behavior.PLANT_MANAGE_CROP)


@add_instruct(constant.Instruct.MANAGE_AGRICULTURE)
def handle_manage_agriculture():
    """处理管理农业生产指令"""
    cache.now_panel_id = constant.Panel.MANAGE_AGRICULTURE


@add_instruct(constant.Instruct.MANAGE_VEHICLE)
def handle_manage_vehicle():
    """处理管理载具指令"""
    cache.now_panel_id = constant.Panel.MANAGE_VEHICLE


@add_instruct(constant.Instruct.PHYSICAL_CHECK_AND_MANAGE)
def handle_physical_check_and_manage():
    """处理身体检查与管理指令"""
    cache.now_panel_id = constant.Panel.PHYSICAL_CHECK_AND_MANAGE


@add_instruct(constant.Instruct.MANAGE_CONFINEMENT_AND_TRAINING)
def handle_manage_vonfinement_and_training():
    """处理管理监禁调教指令"""
    cache.now_panel_id = constant.Panel.MANAGE_CONFINEMENT_AND_TRAINING


@add_instruct(constant.Instruct.INVESTIGATE_RESOURCE_MARKET)
def handle_investigate_resource_market():
    """处理研判资源市场指令"""
    chara_handle_instruct_common_settle(constant.Behavior.INVESTIGATE_RESOURCE_MARKET)


@add_instruct(constant.Instruct.MANAGE_RESOURCE_EXCHANGE)
def handle_manage_resource_exchange():
    """处理管理资源交易指令"""
    cache.now_panel_id = constant.Panel.MANAGE_RESOURCE_EXCHANGE


@add_instruct(constant.Instruct.NAVIGATION)
def handle_navigation():
    """处理导航指令"""
    cache.now_panel_id = constant.Panel.NAVIGATION


@add_instruct(constant.Instruct.MANAGE_BASEMENT)
def handle_manage_basement():
    """处理管理罗德岛指令"""
    cache.now_panel_id = constant.Panel.MANAGE_BASEMENT


# 以下为源石技艺#

@add_instruct(constant.Instruct.HYPNOSIS_ONE)
def handle_hypnosis_one():
    """处理单人催眠"""
    character_data: game_type.Character = cache.character_data[0]
    now_scene_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    if cache.scene_data[now_scene_str].close_flag == 0:
        now_draw = normal_panel.Close_Door_Panel(width)
        door_return = now_draw.draw()
        if door_return == -1:
            return
    chara_handle_instruct_common_settle(constant.Behavior.HYPNOSIS_ONE)


@add_instruct(constant.Instruct.DEEPENING_HYPNOSIS)
def handle_deepening_hypnosis():
    """处理加深催眠"""
    chara_handle_instruct_common_settle(constant.Behavior.HYPNOSIS_ONE)


@add_instruct(constant.Instruct.HYPNOSIS_ALL)
def handle_hypnosis_all():
    """处理集体催眠"""
    character_data: game_type.Character = cache.character_data[0]
    now_scene_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    # 计算当前理智值是否足够进行催眠
    scene_data: game_type.Scene = cache.scene_data[now_scene_str]
    now_npc_num = len(scene_data.character_list) - 1
    sanity_point_cost = 10 + 10 * now_npc_num
    if character_data.sanity_point < sanity_point_cost:
        now_draw = draw.WaitDraw()
        draw_text = _("\n当前理智值不足，至少需要{0}点理智值，无法进行集体催眠\n").format(sanity_point_cost)
        now_draw.text = draw_text
        now_draw.draw()
        return
    if cache.scene_data[now_scene_str].close_flag == 0:
        now_draw = normal_panel.Close_Door_Panel(width)
        door_return = now_draw.draw()
        if door_return == -1:
            return
    chara_handle_instruct_common_settle(constant.Behavior.HYPNOSIS_ALL)


@add_instruct(constant.Instruct.CHANGE_HYPNOSIS_MODE)
def handle_change_hypnosis_mode():
    """处理切换催眠模式"""
    cache.now_panel_id = constant.Panel.CHANGE_HYPNOSIS_MODE


@add_instruct(constant.Instruct.HYPNOSIS_CANCEL)
def handle_hypnosis_cancel():
    """处理解除催眠"""
    chara_handle_instruct_common_settle(constant.Behavior.HYPNOSIS_CANCEL)


@add_instruct(constant.Instruct.HYPNOSIS_INCREASE_BODY_SENSITIVITY)
def handle_hypnosis_increase_body_sensitivity():
    """处理体控-敏感度提升"""
    chara_handle_instruct_common_settle(constant.Behavior.HYPNOSIS_INCREASE_BODY_SENSITIVITY)


@add_instruct(constant.Instruct.HYPNOSIS_FORCE_CLIMAX)
def handle_hypnosis_force_climax():
    """处理体控-强制高潮"""
    chara_handle_instruct_common_settle(constant.Behavior.HYPNOSIS_FORCE_CLIMAX)


@add_instruct(constant.Instruct.HYPNOSIS_FORCE_OVULATION)
def handle_hypnosis_force_ovulation():
    """处理体控-强制排卵"""
    chara_handle_instruct_common_settle(constant.Behavior.HYPNOSIS_FORCE_OVULATION)


@add_instruct(constant.Instruct.HYPNOSIS_BLOCKHEAD)
def handle_hypnosis_blockhead():
    """处理体控-木头人"""
    chara_handle_instruct_common_settle(constant.Behavior.HYPNOSIS_BLOCKHEAD)


@add_instruct(constant.Instruct.HYPNOSIS_ACTIVE_H)
def handle_hypnosis_active_h():
    """处理体控-逆推"""
    chara_handle_instruct_common_settle(constant.Behavior.HYPNOSIS_ACTIVE_H)


@add_instruct(constant.Instruct.HYPNOSIS_ROLEPLAY)
def handle_hypnosis_roleplay():
    """处理心控-角色扮演"""
    from Script.UI.Panel import hypnosis_panel
    now_draw = hypnosis_panel.Chose_Roleplay_Type_Panel(width)
    now_draw.draw()
    character_data: game_type.Character = cache.character_data[0]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.hypnosis.roleplay != []:
        chara_handle_instruct_common_settle(constant.Behavior.HYPNOSIS_ROLEPLAY)


@add_instruct(constant.Instruct.HYPNOSIS_PAIN_AS_PLEASURE)
def handle_hypnosis_pain_as_pleasure():
    """处理心控-苦痛快感化"""
    chara_handle_instruct_common_settle(constant.Behavior.HYPNOSIS_PAIN_AS_PLEASURE)


@add_instruct(constant.Instruct.PENETRATING_VISION_ON)
def handle_penetrating_vision_on():
    """处理开启透视"""
    chara_handle_instruct_common_settle(constant.Behavior.PENETRATING_VISION_ON)


@add_instruct(constant.Instruct.PENETRATING_VISION_OFF)
def handle_penetrating_vision_off():
    """处理关闭透视"""
    chara_handle_instruct_common_settle(constant.Behavior.PENETRATING_VISION_OFF)


@add_instruct(constant.Instruct.HORMONE_ON)
def handle_hormone_on():
    """处理开启信息素"""
    chara_handle_instruct_common_settle(constant.Behavior.HORMONE_ON)


@add_instruct(constant.Instruct.HORMONE_OFF)
def handle_hormone_off():
    """处理关闭信息素"""
    chara_handle_instruct_common_settle(constant.Behavior.HORMONE_OFF)


@add_instruct(constant.Instruct.TIME_STOP_ON)
def handle_time_stop_on():
    """处理时间停止流动"""
    chara_handle_instruct_common_settle(constant.Behavior.TIME_STOP_ON)


@add_instruct(constant.Instruct.TIME_STOP_OFF)
def handle_time_stop_off():
    """处理时间重新流动"""
    chara_handle_instruct_common_settle(constant.Behavior.TIME_STOP_OFF)


@add_instruct(constant.Instruct.TIME_STOP_OFF_IN_H)
def handle_time_stop_off_in_h():
    """处理在H中取消时停"""
    chara_handle_instruct_common_settle(constant.Behavior.TIME_STOP_OFF)


@add_instruct(constant.Instruct.CARRY_TARGET)
def handle_carry_target():
    """处理搬运对方"""
    chara_handle_instruct_common_settle(constant.Behavior.CARRY_TARGET)


@add_instruct(constant.Instruct.STOP_CARRY_TARGET)
def handle_stop_carry_target():
    """处理停止搬运对方"""
    chara_handle_instruct_common_settle(constant.Behavior.STOP_CARRY_TARGET)


@add_instruct(constant.Instruct.TARGET_FREE_IN_TIME_STOP)
def handle_target_free_in_time_stop():
    """处理让在时停中正常行动"""
    # TODO，到写隐奸和露出的时候一起写
    chara_handle_instruct_common_settle(constant.Behavior.TARGET_FREE_IN_TIME_STOP)


@add_instruct(constant.Instruct.TARGET_STOP_IN_TIME_STOP)
def handle_target_stop_in_time_stop():
    """处理在时停中再次停止"""
    # TODO，到写隐奸和露出的时候一起写
    chara_handle_instruct_common_settle(constant.Behavior.TARGET_STOP_IN_TIME_STOP)


@add_instruct(constant.Instruct.DIRAY)
def handle_diary():
    """处理日记指令"""
    from Script.UI.Panel import diary_panel
    now_draw = diary_panel.Diary_Panel(width)
    now_draw.draw()


@add_instruct(constant.Instruct.SLEEP)
def handle_sleep():
    """处理睡觉指令"""
    from Script.UI.Panel import sleep_panel
    now_draw = sleep_panel.Sleep_Panel(width)
    now_draw.draw()


@add_instruct(constant.Instruct.TAKE_SHOWER)
def handle_take_shower():
    """处理淋浴指令"""
    chara_handle_instruct_common_settle(constant.Behavior.TAKE_SHOWER)


@add_instruct(constant.Instruct.STROKE)
def handle_stroke():
    """处理身体接触指令"""
    chara_handle_instruct_common_settle(constant.Behavior.STROKE)

@add_instruct(constant.Instruct.MASSAGE)
def handle_massage():
    """处理按摩指令"""
    chara_handle_instruct_common_settle(constant.Behavior.MASSAGE)

@add_instruct(constant.Instruct.WAIT)
def handle_wait():
    """处理等待五分钟指令"""
    chara_handle_instruct_common_settle(constant.Behavior.WAIT, duration = 5)


@add_instruct(constant.Instruct.WAIT_1_HOUR)
def handle_wait_1_hour():
    """处理等待一个小时指令"""
    cache.wframe_mouse.w_frame_skip_wait_mouse = 1
    chara_handle_instruct_common_settle(constant.Behavior.WAIT, duration = 60)


@add_instruct(constant.Instruct.WAIT_6_HOUR)
def handle_wait_6_hour():
    """处理等待六个小时指令"""
    cache.wframe_mouse.w_frame_skip_wait_mouse = 1
    chara_handle_instruct_common_settle(constant.Behavior.WAIT, duration = 360)


@add_instruct(constant.Instruct.MAKE_COFFEE)
def handle_make_coffee():
    """处理泡咖啡指令"""
    chara_handle_instruct_common_settle(constant.Behavior.MAKE_COFFEE)


@add_instruct(constant.Instruct.MAKE_COFFEE_ADD)
def handle_make_coffee_add():
    """处理泡咖啡（加料）指令"""
    from Script.UI.Panel import make_food_panel
    now_draw = make_food_panel.Make_food_Panel(width,make_food_type=1)
    now_draw.draw()


@add_instruct(constant.Instruct.ASK_MAKE_COFFEE)
def handle_ask_make_coffee():
    """处理让对方泡咖啡指令"""
    chara_handle_instruct_common_settle(constant.Behavior.ASK_MAKE_COFFEE)


@add_instruct(constant.Instruct.MAKE_FOOD)
def handle_make_food():
    """做饭"""
    cache.now_panel_id = constant.Panel.MAKE_FOOD


@add_instruct(constant.Instruct.ALL_NPC_POSITION)
def handle_all_npc_position():
    """处理干员位置一览指令"""
    cache.now_panel_id = constant.Panel.ALL_NPC_POSITION


@add_instruct(constant.Instruct.FOLLOW)
def handle_followed():
    """处理邀请同行指令"""
    character_data: game_type.Character = cache.character_data[0]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]

    # 提示信息
    now_draw = draw.NormalDraw()
    now_draw.text = _("\n{0}进入智能跟随模式\n").format(target_data.name)

    # 去掉其他NPC的跟随
    if not cache.debug_mode:
        for npc_id in cache.npc_id_got:
            if npc_id not in {0, character_data.target_character_id, character_data.assistant_character_id}:
                other_character_data = cache.character_data[npc_id]
                if other_character_data.sp_flag.is_follow:
                    other_character_data.sp_flag.is_follow = 0
                    handle_premise.settle_chara_unnormal_flag(npc_id, 3)
                    now_draw.text += _("当前最大跟随数量：1人，{0}退出跟随模式\n").format(other_character_data.name)
    # now_draw.width = 1
    now_draw.draw()

    chara_handle_instruct_common_settle(constant.Behavior.FOLLOW, duration = 5)


@add_instruct(constant.Instruct.END_FOLLOW)
def handle_end_followed():
    """处理结束同行指令"""
    chara_handle_instruct_common_settle(constant.Behavior.END_FOLLOW, duration = 5)


@add_instruct(constant.Instruct.ASK_TARGET_REST)
def handle_ask_target_rest():
    """处理让对方休息指令"""
    character_data: game_type.Character = cache.character_data[0]
    target_character_data: game_type.Character = cache.character_data[character_data.target_character_id]
    target_character_data.sp_flag.rest = True
    handle_premise.settle_chara_unnormal_flag(character_data.target_character_id, 1)
    chara_handle_instruct_common_settle(constant.Behavior.WAIT, duration = 1)


@add_instruct(constant.Instruct.ASK_TARGET_SLEEP)
def handle_ask_target_sleep():
    """处理让对方睡觉指令"""
    character_data: game_type.Character = cache.character_data[0]
    target_character_data: game_type.Character = cache.character_data[character_data.target_character_id]
    target_character_data.sp_flag.tired = True
    chara_handle_instruct_common_settle(constant.Behavior.WAIT, duration = 1)


@add_instruct(constant.Instruct.APOLOGIZE)
def handle_apologize():
    """处理道歉指令"""
    instuct_judege.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    # 根据口才获取调整值#
    character_data.ability.setdefault(25, 0)
    adjust = handle_ability.get_ability_adjust(character_data.ability[40])
    value = int(10 + adjust * 10)
    # 减愤怒值
    target_data.angry_point -= value
    # 判定是否不生气了
    if target_data.angry_point <= 30:
        chara_handle_instruct_common_settle(constant.Behavior.APOLOGIZE, force_taget_wait = True)
    else:
        chara_handle_instruct_common_settle(constant.Behavior.APOLOGIZE_FAILED, force_taget_wait = True)


@add_instruct(constant.Instruct.LISTEN_COMPLAINT)
def handle_listen_complaint():
    """处理听牢骚指令"""
    instuct_judege.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    # 根据口才获取调整值#
    character_data.ability.setdefault(25, 0)
    adjust = handle_ability.get_ability_adjust(character_data.ability[40])
    value = int(10 + adjust * 10)
    # 减愤怒值
    target_data.angry_point -= value
    chara_handle_instruct_common_settle(constant.Behavior.LISTEN_COMPLAINT, force_taget_wait = True)


@add_instruct(constant.Instruct.GIVE_GIFT)
def handle_give_gift():
    """处理赠送礼物指令"""
    cache.now_panel_id = constant.Panel.GIVE_GIFT


@add_instruct(constant.Instruct.ORIGINIUM_ARTS)
def handle_originium_arts():
    """处理源石技艺指令"""
    cache.now_panel_id = constant.Panel.ORIGINIUM_ARTS


@add_instruct(constant.Instruct.TARGET_TO_SELF)
def handle_target_to_self():
    """处理对自己交互指令"""
    pl_character_data = cache.character_data[0]
    pl_character_data.target_character_id = 0
    chara_handle_instruct_common_settle(constant.Behavior.WAIT, duration = 1)


@add_instruct(constant.Instruct.DOOR_LOCK_INNER)
def handle_door_lock_inner():
    """处理锁上门内侧锁指令"""
    pl_character_data = cache.character_data[0]
    now_position = pl_character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    now_scene_data.close_flag = now_scene_data.close_type
    chara_handle_instruct_common_settle(constant.Behavior.WAIT, duration = 1)


@add_instruct(constant.Instruct.DOOR_UNLOCK_INNER)
def handle_door_unlock_inner():
    """处理解开门内侧锁指令"""
    pl_character_data = cache.character_data[0]
    now_position = pl_character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    now_scene_data.close_flag = 0
    chara_handle_instruct_common_settle(constant.Behavior.WAIT, duration = 1)


@add_instruct(constant.Instruct.CHARA_DIY_INSTRUCT)
def handle_chara_diy_instruct():
    """处理角色特殊指令"""
    # 本指令仅在下述函数中特殊调用，不会被正常调用
    # Script/UI/Panel/in_scene_panel.py/handle_chara_diy_instruct()
    pl_character_data = cache.character_data[0]
    event_id = pl_character_data.event.event_id
    event_data = game_config.config_event[event_id]
    # 将角色的行动事件改为事件文本中的时间
    new_duration = int(event_data.text.split("|")[1])
    chara_handle_instruct_common_settle(constant.Behavior.CHARA_DIY_INSTRUCT, duration=new_duration)


@add_instruct(constant.Instruct.TEST_INSTRUCT)
def handle_test_instruct():
    """处理测试用临时指令"""
    chara_handle_instruct_common_settle(constant.Behavior.TEST_INSTRUCT)


@add_instruct(constant.Instruct.LISTEN_INFLATION)
def handle_listen_inflation():
    """处理听肚子里的动静指令"""
    chara_handle_instruct_common_settle(constant.Behavior.LISTEN_INFLATION)


@add_instruct(constant.Instruct.PLAY_WITH_CHILD)
def handle_play_with_child():
    """处理一起玩耍指令"""
    chara_handle_instruct_common_settle(constant.Behavior.PLAY_WITH_CHILD)


@add_instruct(constant.Instruct.TAKE_CARE_BABY)
def handle_take_care_baby():
    """处理照顾婴儿指令"""
    cache.now_panel_id = constant.Panel.TAKE_CARE_BABY


@add_instruct(constant.Instruct.ORDER_HOTEL_ROOM)
def handle_order_hotel_room():
    """处理预定房间指令"""
    cache.now_panel_id = constant.Panel.ORDER_HOTEL_ROOM


@add_instruct(constant.Instruct.SEE_COLLECTION)
def handle_see_collection():
    """处理查看收藏品指令"""
    cache.now_panel_id = constant.Panel.COLLECTION


@add_instruct(constant.Instruct.SEE_ACHIEVEMENT)
def handle_see_achievement():
    """处理查看蚀刻章指令"""
    cache.now_panel_id = constant.Panel.SEE_ACHIEVEMENT


@add_instruct(constant.Instruct.SEE_FRIDGE)
def handle_see_fridge():
    """处理查看冰箱指令"""
    cache.now_panel_id = constant.Panel.FRIDGE


@add_instruct(constant.Instruct.FIELD_COMMISSION)
def handle_field_commission():
    """处理外勤委托指令"""
    cache.now_panel_id = constant.Panel.FIELD_COMMISSION


@add_instruct(constant.Instruct.CHECK_LOCKER)
def handle_check_locker():
    """处理检查衣柜指令"""
    cache.now_panel_id = constant.Panel.CHECK_LOCKER


@add_instruct(constant.Instruct.COLLCET_PANTY)
def handle_collect_panty():
    """处理收起内裤指令"""
    instuct_judege.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)


@add_instruct(constant.Instruct.ASK_DATE)
def handle_ask_date():
    """处理邀请约会指令"""
    instuct_judege.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)


@add_instruct(constant.Instruct.CONFESSION)
def handle_confession():
    """处理告白指令"""
    instuct_judege.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    target_data = cache.character_data[character_data.target_character_id]
    if handle_premise.handle_target_trust_ge_200(0) and instuct_judege.calculation_instuct_judege(0, character_data.target_character_id, _("告白"))[0]:
        character_data.behavior.behavior_id = constant.Behavior.CONFESSION
        character_data.state = constant.CharacterStatus.STATUS_CONFESSION
        # 将对象的恋慕转为恋人，对方获得戒指
        target_data.talent[202] = 0
        target_data.talent[203] = 1
        target_data.talent[205] = 1
        target_data.talent[411] = 1
        character_data.pl_collection.token_list[character_data.target_character_id] = True
        now_draw = draw.WaitDraw()
        now_draw.width = width
        now_draw.text = _("\n告白成功，{0}收下了你赠予的[戒指]，[恋慕]转为[恋人]\n").format(target_data.name)
        now_draw.text += _("\n获得了{0}的信物：{1}\n").format(target_data.name, target_data.token_text)
        now_draw.text += _("\n可以在[角色属性]-[角色设置]修改对彼此的称呼了\n")
        now_draw.draw()
    else:
        character_data.behavior.behavior_id = constant.Behavior.CONFESSION_FAILED
        character_data.state = constant.CharacterStatus.STATUS_CONFESSION_FAILED
        now_draw = draw.WaitDraw()
        now_draw.width = width
        now_draw.text = _("\n告白失败，需要[恋慕]、信赖≥200%、且满足实行值\n")
        now_draw.draw()
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(constant.Instruct.GIVE_NECKLACE)
def handle_give_necklace():
    """处理戴上项圈指令"""
    instuct_judege.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    target_data = cache.character_data[character_data.target_character_id]
    if handle_premise.handle_target_trust_ge_200(0) and instuct_judege.calculation_instuct_judege(0, character_data.target_character_id, _("戴上项圈"))[0]:
        character_data.behavior.behavior_id = constant.Behavior.GIVE_NECKLACE
        character_data.state = constant.CharacterStatus.STATUS_GIVE_NECKLACE
        # 将对象的驯服转为宠物，增加项圈素质
        target_data.talent[212] = 0
        target_data.talent[213] = 1
        target_data.talent[215] = 1
        target_data.talent[411] = 1
        character_data.pl_collection.token_list[character_data.target_character_id] = True
        now_draw = draw.WaitDraw()
        now_draw.width = width
        now_draw.text = _("\n{0}接受了项圈，戴在了自己的脖子上，[驯服]转为[宠物]\n").format(target_data.name)
        now_draw.text += _("\n获得了{0}的信物：{1}\n").format(target_data.name, target_data.token_text)
        now_draw.text += _("\n可以在[角色属性]-[角色设置]修改对彼此的称呼了\n")
        now_draw.draw()
    else:
        character_data.behavior.behavior_id = constant.Behavior.GIVE_NECKLACE_FAILED
        character_data.state = constant.CharacterStatus.STATUS_GIVE_NECKLACE_FAILED
        now_draw = draw.WaitDraw()
        now_draw.width = width
        now_draw.text = _("\n戴上项圈失败，需要[驯服]、信赖≥200%、且满足实行值\n")
        now_draw.draw()
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(constant.Instruct.DRINK_ALCOHOL)
def handle_drink_alcohol():
    """处理劝酒指令"""
    instuct_judege.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)


@add_instruct(constant.Instruct.PEE)
def handle_pee():
    """处理解手指令"""
    chara_handle_instruct_common_settle(constant.Behavior.PEE)


@add_instruct(constant.Instruct.COLLECT)
def handle_collect():
    """处理摆放藏品指令"""
    from Script.UI.Panel import collection_panel
    # 收起藏品
    collection_panel.collapse_collection()
    chara_handle_instruct_common_settle(constant.Behavior.WAIT, duration = 5)


@add_instruct(constant.Instruct.DO_H)
def handle_do_h():
    """处理邀请H指令"""
    character_data: game_type.Character = cache.character_data[0]
    target_data = cache.character_data[character_data.target_character_id]
    now_draw = draw.WaitDraw()
    now_draw.width = width
    now_draw_text = "\n"
    if instuct_judege.calculation_instuct_judege(0, character_data.target_character_id, _("H模式"))[0]:
        now_scene_str = map_handle.get_map_system_path_str_for_list(character_data.position)
        # 如果没关门，则自动将门关上
        if cache.scene_data[now_scene_str].close_flag == 0:
            cache.scene_data[now_scene_str].close_flag = cache.scene_data[now_scene_str].close_type
            now_draw_text += _("已自动关门\n")
        target_data.sp_flag.is_follow = 0
        target_data.action_info.last_conscious_h_time = cache.game_time
        handle_premise.settle_chara_unnormal_flag(character_data.target_character_id, 3)
        now_draw_text += _("进入H模式\n\n")
        now_draw.text = now_draw_text
        now_draw.style = 'gold_enrod'
        now_draw.draw()
        chara_handle_instruct_common_settle(constant.Behavior.H)
    else:
        now_draw.text = _("\n进入H模式失败\n\n")
        now_draw.style = 'warning'
        now_draw.draw()
        chara_handle_instruct_common_settle(constant.Behavior.DO_H_FAIL)


@add_instruct(constant.Instruct.DO_H_IN_LOVE_HOTEL)
def handle_do_h_in_love_hotel():
    """处理邀请在爱情旅馆H指令"""
    character_data: game_type.Character = cache.character_data[0]
    character_data.h_state.h_in_love_hotel = True
    target_data = cache.character_data[character_data.target_character_id]
    target_data.h_state.h_in_love_hotel = True
    handle_do_h()

@add_instruct(constant.Instruct.DO_H_IN_BATHROOM)
def handle_do_h_in_bathroom():
    """处理邀请在浴室H指令"""
    character_data: game_type.Character = cache.character_data[0]
    character_data.h_state.h_in_bathroom = True
    target_data = cache.character_data[character_data.target_character_id]
    target_data.h_state.h_in_bathroom = True
    handle_do_h()

@add_instruct(constant.Instruct.DO_H_WITH_DAUGHTER)
def handle_do_h_with_daughter():
    """处理邀请乱伦H指令"""
    handle_do_h()

@add_instruct(constant.Instruct.PREPARE_TRAINING)
def handle_prepare_training():
    """处理调教前准备指令"""
    from Script.UI.Panel import confinement_and_training
    instuct_judege.init_character_behavior_start_time(0, cache.game_time)
    confinement_and_training.prepare_training()
    update.game_update_flow(10)


@add_instruct(constant.Instruct.SWITCH_TO_H_INTERFACE)
def handle_switch_to_h_interface():
    """处理切换到H指令"""
    cache.show_non_h_in_hidden_sex = False


@add_instruct(constant.Instruct.SLEEP_OBSCENITY)
def handle_sleep_obscenity():
    """处理睡眠猥亵指令"""
    instuct_judege.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    target_data = cache.character_data[character_data.target_character_id]
    now_scene_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    if cache.scene_data[now_scene_str].close_flag == 0:
        now_draw = normal_panel.Close_Door_Panel(width)
        door_return = now_draw.draw()
        if door_return == -1:
            return
    target_data.sp_flag.unconscious_h = 1
    handle_premise.settle_chara_unnormal_flag(character_data.target_character_id, 5)
    handle_premise.settle_chara_unnormal_flag(character_data.target_character_id, 6)
    now_draw = draw.WaitDraw()
    now_draw.width = width
    now_draw.text = _("\n进入睡眠猥亵模式\n")
    now_draw.draw()
    # 虽然在无意识奸中会刷新该数值，但是为了防止仅睡奸猥亵不H，在这里也初始化一下
    cache.achievement.sleep_sex_record = {1: 0, 2: 0, 3: 0}


@add_instruct(constant.Instruct.STOP_SLEEP_OBSCENITY)
def handle_stop_sleep_obscenity():
    """处理停止睡眠猥亵指令"""
    from Script.Settle import default
    instuct_judege.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    target_data = cache.character_data[character_data.target_character_id]
    target_data.sp_flag.unconscious_h = 0
    handle_premise.settle_chara_unnormal_flag(character_data.target_character_id, 5)
    handle_premise.settle_chara_unnormal_flag(character_data.target_character_id, 6)
    now_draw = draw.WaitDraw()
    now_draw.width = width
    now_draw.text = _("\n退出睡眠猥亵模式\n")
    now_draw.draw()
    default.handle_door_close_reset(0,1,game_type.CharacterStatusChange(),datetime.datetime(1, 1, 1))

@add_instruct(constant.Instruct.IMPRISONMENT_H)
def handle_imprisonment_h():
    """处理监禁奸指令"""
    handle_do_h()

@add_instruct(constant.Instruct.UNCONSCIOUS_H)
def handle_unconscious_h():
    """处理无意识奸指令"""
    character_data: game_type.Character = cache.character_data[0]
    target_data = cache.character_data[character_data.target_character_id]
    now_scene_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    if cache.scene_data[now_scene_str].close_flag == 0 and handle_premise.handle_time_stop_off(0):
        now_draw = normal_panel.Close_Door_Panel(width)
        door_return = now_draw.draw()
        if door_return == -1:
            return
    target_data.sp_flag.is_follow = 0
    target_data.action_info.last_unconscious_h_time = cache.game_time
    handle_premise.settle_chara_unnormal_flag(character_data.target_character_id, 3)
    now_draw = draw.WaitDraw()
    now_draw.width = width
    now_draw.text = _("\n进入无意识奸模式\n")
    now_draw.draw()
    # 成就初始化
    if handle_premise.handle_unconscious_flag_1(character_data.target_character_id):
        cache.achievement.sleep_sex_record = {1: 0, 2: 0, 3: 0}
    chara_handle_instruct_common_settle(constant.Behavior.H)


@add_instruct(constant.Instruct.ASK_HIDDEN_SEX)
def handle_ask_hidden_sex():
    """处理邀请隐奸指令"""
    from Script.System.Sex_System.hidden_sex_panel import Select_Hidden_Sex_Mode_Panel
    now_panel = Select_Hidden_Sex_Mode_Panel(width)
    now_panel.draw()


@add_instruct(constant.Instruct.ASK_EXHIBITIONISM_SEX)
def handle_ask_exhibitionism_sex():
    """处理邀请露出指令"""
    from Script.System.Sex_System.exhibitionism_sex_panel import Select_Exhibitionism_Sex_Mode_Panel
    now_panel = Select_Exhibitionism_Sex_Mode_Panel(width)
    now_panel.draw()


@add_instruct(constant.Instruct.ASK_GROUP_SEX)
def handle_ask_group_sex():
    """处理邀请群交指令"""
    now_draw = draw.WaitDraw()
    now_draw.width = width

    instuct_judege.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    h_flag = True # 是否成功进入群交模式
    refuse_chara_list = [] # 拒绝的角色列表

    # 对场景内的全角色进行实行值判定
    scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    scene_data: game_type.Scene = cache.scene_data[scene_path_str]
    # 场景角色数大于等于2时进行检测
    if len(scene_data.character_list) >= 2:
        # 遍历当前角色列表
        for chara_id in scene_data.character_list:
            # 遍历非玩家的角色
            if chara_id == 0:
                continue
            instuct_judege.init_character_behavior_start_time(chara_id, cache.game_time)
            now_character_data = cache.character_data[chara_id]
            now_character_data.behavior.behavior_id = constant.Behavior.WAIT
            now_character_data.state = constant.CharacterStatus.STATUS_WAIT
            now_character_data.behavior.duration = 1
            # 开始判定，TODO 根据已同意人数而增加额外实行值加值
            if instuct_judege.calculation_instuct_judege(0, chara_id, _("群交"), not_draw_flag = True)[0] == False:
                h_flag = False
                refuse_chara_list.append(chara_id)

    # 成功进入群交模式
    if h_flag:
        character_data.behavior.behavior_id = constant.Behavior.ASK_GROUP_SEX
        character_data.state = constant.CharacterStatus.STATUS_ASK_GROUP_SEX
        now_draw.text = _("\n进入群交模式\n")
        now_draw.draw()
        for chara_id in scene_data.character_list:
            # 遍历非玩家的角色
            if chara_id == 0:
                continue
            chara_handle_instruct_common_settle(constant.Behavior.JOIN_GROUP_SEX, character_id=chara_id, target_character_id=0)
            # 手动结算该状态
            character_behavior.judge_character_status(chara_id)
    else:
        now_draw.text = _("\n进入群交模式失败\n")
        for chara_id in refuse_chara_list:
            now_draw.text += _("{0}拒绝了群交\n").format(cache.character_data[chara_id].name)
        now_draw.draw()
        character_data.action_info.ask_group_sex_refuse_chara_id_list = refuse_chara_list
        character_data.behavior.behavior_id = constant.Behavior.ASK_GROUP_SEX_FAIL
        character_data.state = constant.CharacterStatus.STATUS_ASK_GROUP_SEX_FAIL
    character_data.behavior.duration = 5
    update.game_update_flow(5)


@add_instruct(constant.Instruct.WAIT_5_MIN_IN_H)
def handle_wait_5_min_in_h():
    """处理等待五分钟指令"""
    # 如果场景里已经没有除自己以外的在H中的角色，则转为结束H
    now_scene_character_list = map_handle.get_chara_now_scene_all_chara_id_list(0, remove_own_character=True)
    h_in_scene_flag = False
    for now_chara_id in now_scene_character_list:
        if handle_premise.handle_self_is_h(now_chara_id):
            h_in_scene_flag = True
            break
    if not h_in_scene_flag:
        handle_h_end()
    # 否则正常等待五分钟
    else:
        chara_handle_instruct_common_settle(constant.Behavior.WAIT, duration = 5)

@add_instruct(constant.Instruct.H_END)
def handle_h_end():
    """处理H结束指令"""
    instuct_judege.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    special_end_list = constant.special_end_H_list

    # 非特殊中断的情况下，正常结束H
    if character_data.behavior.behavior_id not in special_end_list:
        character_data.behavior.behavior_id = constant.Behavior.END_H
        character_data.state = constant.CharacterStatus.STATUS_END_H
        # 异常126正常，则进入跟随
        if (
            handle_premise.handle_normal_1(character_data.target_character_id) and 
            handle_premise.handle_normal_2(character_data.target_character_id) and
            handle_premise.handle_normal_6(character_data.target_character_id)
            ):
            target_data.sp_flag.is_follow = 1
            handle_premise.settle_chara_unnormal_flag(character_data.target_character_id, 3)

    # 对方原地待机10分钟
    target_data.behavior.behavior_id = constant.Behavior.WAIT
    target_data.behavior.duration = 10
    target_data.behavior.start_time = character_data.behavior.start_time
    target_data.state = constant.CharacterStatus.STATUS_WAIT

    # H结束时的其他处理完毕
    now_draw = draw.WaitDraw()
    now_draw.width = width
    now_draw.text = _("\n结束H模式\n")
    now_draw.draw()
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(constant.Instruct.H_WITH_DAUGHTER_END)
def handle_h_with_daughter_end():
    """处理结束乱伦H指令"""
    cache.achievement.h_with_daughter_count += 1
    # 结算成就
    achievement_panel.achievement_flow(_("乱伦"))
    handle_h_end()

@add_instruct(constant.Instruct.IMPRISONMENT_H_END)
def handle_imprisonment_h_end():
    """处理结束监禁奸指令"""
    handle_h_end()

@add_instruct(constant.Instruct.UNCONSCIOUS_H_END)
def handle_unconscious_h_end():
    """处理结束无意识奸指令"""
    instuct_judege.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]

    character_data.behavior.behavior_id = constant.Behavior.NO_CONSCIOUS_H_END
    character_data.state = constant.CharacterStatus.STATUS_NO_CONSCIOUS_H_END
    # 结算成就
    achievement_panel.achievement_flow(_("睡奸"))

    # H结束时的其他处理完毕
    now_draw = draw.WaitDraw()
    now_draw.width = width
    now_draw.text = _("\n结束无意识奸\n")
    now_draw.draw()
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(constant.Instruct.HIDDEN_SEX_END)
def handle_hidden_sex_end():
    """处理结束隐奸指令"""
    instuct_judege.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]

    character_data.behavior.behavior_id = constant.Behavior.END_H
    character_data.state = constant.CharacterStatus.STATUS_END_H
    # 异常126正常，则进入跟随
    if (
        handle_premise.handle_normal_1(character_data.target_character_id) and 
        handle_premise.handle_normal_2(character_data.target_character_id) and
        handle_premise.handle_normal_6(character_data.target_character_id)
        ):
        target_data.sp_flag.is_follow = 1
        handle_premise.settle_chara_unnormal_flag(character_data.target_character_id, 3)
    # 结算成就
    achievement_panel.achievement_flow(_("隐奸"))

    # 对方原地待机10分钟
    target_data.behavior.behavior_id = constant.Behavior.WAIT
    target_data.behavior.duration = 10
    target_data.behavior.start_time = character_data.behavior.start_time
    target_data.state = constant.CharacterStatus.STATUS_WAIT

    # H结束时的其他处理完毕
    now_draw = draw.WaitDraw()
    now_draw.width = width
    now_draw.text = _("\n结束隐奸\n")
    now_draw.draw()
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(constant.Instruct.EXHIBITIONISM_SEX_END)
def handle_exhibitionism_sex_end():
    """处理结束露出指令"""
    instuct_judege.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]

    character_data.behavior.behavior_id = constant.Behavior.END_H
    character_data.state = constant.CharacterStatus.STATUS_END_H
    # 异常126正常，则进入跟随
    if (
        handle_premise.handle_normal_1(character_data.target_character_id) and 
        handle_premise.handle_normal_2(character_data.target_character_id) and
        handle_premise.handle_normal_6(character_data.target_character_id)
        ):
        target_data.sp_flag.is_follow = 1
        handle_premise.settle_chara_unnormal_flag(character_data.target_character_id, 3)
    # 结算成就
    achievement_panel.achievement_flow(_("露出"))

    # 对方原地待机10分钟
    target_data.behavior.behavior_id = constant.Behavior.WAIT
    target_data.behavior.duration = 10
    target_data.behavior.start_time = character_data.behavior.start_time
    target_data.state = constant.CharacterStatus.STATUS_WAIT

    # H结束时的其他处理完毕
    now_draw = draw.WaitDraw()
    now_draw.width = width
    now_draw.text = _("\n结束露出\n")
    now_draw.draw()
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(constant.Instruct.GROUP_SEX_END)
def handle_group_sex_end():
    """处理结束群交指令"""
    instuct_judege.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    special_end_list = constant.special_end_H_list

    # 非特殊中断的情况下，正常结束H
    if character_data.behavior.behavior_id not in special_end_list:
        character_data.behavior.behavior_id = constant.Behavior.GROUP_SEX_END
        character_data.state = constant.CharacterStatus.STATUS_GROUP_SEX_END

    # 场景内所有H中的角色原地待机10分钟
    now_scene_character_list = map_handle.get_chara_now_scene_all_chara_id_list(0,remove_own_character=True)
    for chara_id in now_scene_character_list:
        target_data: game_type.Character = cache.character_data[chara_id]
        # 跳过非H状态的角色
        if not handle_premise.handle_self_is_h(chara_id):
            continue
        target_data.behavior.behavior_id = constant.Behavior.WAIT
        target_data.behavior.duration = 10
        target_data.behavior.start_time = character_data.behavior.start_time
        target_data.state = constant.CharacterStatus.STATUS_WAIT

    # H结束时的其他处理完毕
    now_draw = draw.WaitDraw()
    now_draw.width = width
    now_draw.text = _("\n结束群交模式\n")
    now_draw.draw()
    character_data.behavior.duration = 5
    update.game_update_flow(5)


# 以下为娱乐#

@add_instruct(constant.Instruct.SINGING)
def handle_singing():
    """处理唱歌指令"""
    instuct_judege.init_character_behavior_start_time(0, cache.game_time)
    character_data = cache.character_data[0]
    # 如果音乐等级过低，且周围有其他角色，则进行需要确认再唱歌
    if character_data.ability[44] <= 2 and handle_premise.handle_scene_over_one(0):
        while 1:
            now_draw = draw.WaitDraw()
            now_draw.width = width
            now_draw.text = _("\n当前音乐能力小于等于2，可能会让对方感觉不适，确认要继续吗\n\n")
            now_draw.draw()
            return_list = []
            back_draw = draw.CenterButton(_("[取消]"), _("\n取消"), int(width / 3))
            back_draw.draw()
            return_list.append(back_draw.return_text)
            yes_draw = draw.CenterButton(_("[确定]"), _("\n确定"), int(width / 3))
            yes_draw.draw()
            return_list.append(yes_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                return
            elif yrn == yes_draw.return_text:
                break
    chara_handle_instruct_common_settle(constant.Behavior.SINGING)


@add_instruct(constant.Instruct.PLAY_INSTRUMENT)
def handle_play_instrument():
    """处理演奏乐器指令"""
    instuct_judege.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    # 如果音乐等级过低，且周围有其他角色，则进行需要确认再演奏
    if character_data.ability[44] <= 2 and handle_premise.handle_scene_over_one(0):
        while 1:
            now_draw = draw.WaitDraw()
            now_draw.width = width
            now_draw.text = _("\n当前音乐能力小于等于2，可能会让对方感觉不适，确认要继续吗\n\n")
            now_draw.draw()
            return_list = []
            back_draw = draw.CenterButton(_("[取消]"), _("\n取消"), int(width / 3))
            back_draw.draw()
            return_list.append(back_draw.return_text)
            yes_draw = draw.CenterButton(_("[确定]"), _("\n确定"), int(width / 3))
            yes_draw.draw()
            return_list.append(yes_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                return
            elif yrn == yes_draw.return_text:
                break
    chara_handle_instruct_common_settle(constant.Behavior.PLAY_INSTRUMENT)


@add_instruct(constant.Instruct.WATCH_MOVIE)
def handle_watch_movie():
    """处理看电影指令"""
    chara_handle_instruct_common_settle(constant.Behavior.WATCH_MOVIE, force_taget_wait = True)


@add_instruct(constant.Instruct.PHOTOGRAPHY)
def handle_photography():
    """处理摄影指令"""
    chara_handle_instruct_common_settle(constant.Behavior.PHOTOGRAPHY, force_taget_wait = True)


@add_instruct(constant.Instruct.PLAY_WATER)
def handle_play_water():
    """处理玩水指令"""
    chara_handle_instruct_common_settle(constant.Behavior.PLAY_WATER, force_taget_wait = True)


@add_instruct(constant.Instruct.PLAY_GOMOKU)
def handle_play_gomoku():
    """处理下五子棋指令"""
    from Script.UI.Panel import play_gomoku_panel
    now_draw = play_gomoku_panel.GomokuPanel(width)
    now_draw.draw()


@add_instruct(constant.Instruct.PLAY_CHESS)
def handle_play_chess():
    """处理下棋指令"""
    chara_handle_instruct_common_settle(constant.Behavior.PLAY_CHESS, force_taget_wait = True)


@add_instruct(constant.Instruct.PLAY_MAHJONG)
def handle_play_mahjong():
    """处理打麻将指令"""
    chara_handle_instruct_common_settle(constant.Behavior.PLAY_MAHJONG, force_taget_wait = True)


@add_instruct(constant.Instruct.PLAY_CARDS)
def handle_play_cards():
    """处理打牌指令"""
    chara_handle_instruct_common_settle(constant.Behavior.PLAY_CARDS, force_taget_wait = True)


@add_instruct(constant.Instruct.REHEARSE_DANCE)
def handle_rehearse_dance():
    """处理排演舞剧指令"""
    chara_handle_instruct_common_settle(constant.Behavior.REHEARSE_DANCE, force_taget_wait = True)


@add_instruct(constant.Instruct.PLAY_ARCADE_GAME)
def handle_play_arcade_game():
    """处理玩街机游戏指令"""
    chara_handle_instruct_common_settle(constant.Behavior.PLAY_ARCADE_GAME, force_taget_wait = True)


@add_instruct(constant.Instruct.SWIMMING)
def handle_swimming():
    """处理游泳指令"""
    chara_handle_instruct_common_settle(constant.Behavior.SWIMMING, force_taget_wait = True)

@add_instruct(constant.Instruct.TASTE_WINE)
def handle_taste_wine():
    """处理品酒指令"""
    chara_handle_instruct_common_settle(constant.Behavior.TASTE_WINE)


@add_instruct(constant.Instruct.TASTE_TEA)
def handle_taste_tea():
    """处理品茶指令"""
    chara_handle_instruct_common_settle(constant.Behavior.TASTE_TEA)


@add_instruct(constant.Instruct.TASTE_COFFEE)
def handle_taste_coffee():
    """处理品咖啡指令"""
    chara_handle_instruct_common_settle(constant.Behavior.TASTE_COFFEE)


@add_instruct(constant.Instruct.TASTE_DESSERT)
def handle_taste_dessert():
    """处理品尝点心指令"""
    chara_handle_instruct_common_settle(constant.Behavior.TASTE_DESSERT)


@add_instruct(constant.Instruct.TASTE_FOOD)
def handle_taste_food():
    """处理品尝美食指令"""
    chara_handle_instruct_common_settle(constant.Behavior.TASTE_FOOD)


@add_instruct(constant.Instruct.PLAY_HOUSE)
def handle_play_house():
    """处理过家家指令"""
    chara_handle_instruct_common_settle(constant.Behavior.PLAY_HOUSE, force_taget_wait = True)


@add_instruct(constant.Instruct.STYLE_HAIR)
def handle_style_hair():
    """处理修整发型指令"""
    chara_handle_instruct_common_settle(constant.Behavior.STYLE_HAIR)


@add_instruct(constant.Instruct.FULL_BODY_STYLING)
def handle_full_body_styling():
    """处理全身造型服务指令"""
    chara_handle_instruct_common_settle(constant.Behavior.FULL_BODY_STYLING)


@add_instruct(constant.Instruct.SOAK_FEET)
def handle_soak_feet():
    """处理泡脚指令"""
    chara_handle_instruct_common_settle(constant.Behavior.SOAK_FEET)


@add_instruct(constant.Instruct.STEAM_SAUNA)
def handle_steam_sauna():
    """处理蒸桑拿指令"""
    chara_handle_instruct_common_settle(constant.Behavior.STEAM_SAUNA)


@add_instruct(constant.Instruct.HYDROTHERAPY_TREATMENT)
def handle_hydrotherapy_treatment():
    """处理水疗护理指令"""
    chara_handle_instruct_common_settle(constant.Behavior.HYDROTHERAPY_TREATMENT)


@add_instruct(constant.Instruct.ONSEN_BATH)
def handle_onsen_bath():
    """处理泡温泉指令"""
    chara_handle_instruct_common_settle(constant.Behavior.ONSEN_BATH)


@add_instruct(constant.Instruct.AROMATHERAPY)
def handle_aromatherapy():
    """处理香薰疗愈指令"""
    cache.now_panel_id = constant.Panel.AROMATHERAPY


# 以下为工作#

@add_instruct(constant.Instruct.OFFICIAL_WORK)
def handle_official_work():
    """处理处理公务指令"""
    chara_handle_instruct_common_settle(constant.Behavior.OFFICIAL_WORK, force_taget_wait = True)


@add_instruct(constant.Instruct.BATTLE_COMMAND)
def handle_battle_command():
    """处理指挥作战指令"""
    instuct_judege.init_character_behavior_start_time(0, cache.game_time)
    character_data = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)


@add_instruct(constant.Instruct.ASSISTANT_ADJUSTMENTS)
def handle_ASSISTANT_ADJUSTMENTS():
    """处理助理相关调整指令"""
    cache.now_panel_id = constant.Panel.ASSISTANT


@add_instruct(constant.Instruct.BUILDING)
def handle_building():
    """处理基建系统指令"""
    cache.now_panel_id = constant.Panel.BUILDING


@add_instruct(constant.Instruct.EQUIPMENT_MAINTAIN)
def handle_equipment_maintain():
    """处理管理装备维护指令"""
    cache.now_panel_id = constant.Panel.EQUIPMENT_MAINTAIN


@add_instruct(constant.Instruct.RECRUITMENT)
def handle_recruiment():
    """处理招募情况指令"""
    cache.now_panel_id = constant.Panel.RECRUITMENT


@add_instruct(constant.Instruct.VISITOR_SYSTEM)
def handle_visitor_system():
    """处理访客系统指令"""
    cache.now_panel_id = constant.Panel.VISITOR


@add_instruct(constant.Instruct.NATION_DIPLOMACY)
def handle_nation_diplomacy():
    """处理势力与外交指令"""
    cache.now_panel_id = constant.Panel.NATION_DIPLOMACY


@add_instruct(constant.Instruct.INVITE_VISITOR)
def handle_invite_visitor():
    """处理邀请访客指令"""
    chara_handle_instruct_common_settle(constant.Behavior.INVITE_VISITOR, force_taget_wait = True)


@add_instruct(constant.Instruct.PRTS)
def handle_prts():
    """处理普瑞赛斯指令"""
    cache.now_panel_id = constant.Panel.PRTS


@add_instruct(constant.Instruct.TRAINING)
def handle_training():
    """处理战斗训练指令"""
    chara_handle_instruct_common_settle(constant.Behavior.TRAINING, force_taget_wait = True)


@add_instruct(constant.Instruct.EXERCISE)
def handle_exercise():
    """处理锻炼身体指令"""
    chara_handle_instruct_common_settle(constant.Behavior.EXERCISE, force_taget_wait = True)


@add_instruct(constant.Instruct.CURE_PATIENT)
def handle_cure_patient():
    """处理诊疗病人指令"""
    # 如果当前没有病人，输出提示并返回
    if not handle_premise.handle_patient_wait(0):
        now_draw = draw.WaitDraw()
        now_draw.width = width
        now_draw.text = _("\n当前没有需要诊疗的病人\n")
        now_draw.draw()
        return
    cache.now_panel_id = constant.Panel.CURE_PATIENT

@add_instruct(constant.Instruct.MANAGE_DEDICAL_DEPARTMENT)
def handle_manage_dedical_department():
    """处理管理医疗系统指令"""
    cache.now_panel_id = constant.Panel.MANAGE_DEDICAL_DEPARTMENT

@add_instruct(constant.Instruct.RECRUIT)
def handle_recruit():
    """处理招募干员指令"""
    chara_handle_instruct_common_settle(constant.Behavior.RECRUIT, force_taget_wait = True)


@add_instruct(constant.Instruct.CONFIM_RECRUIT)
def handle_confim_recruit():
    """处理确认已招募干员指令"""
    from Script.UI.Panel import recruit_panel
    if recruit_panel.recruit_new_chara():
        chara_handle_instruct_common_settle(constant.Behavior.WAIT, duration = 5)


@add_instruct(constant.Instruct.MAINTENANCE_FACILITIES)
def handle_maintenance_facilities():
    """处理维护设施指令"""
    chara_handle_instruct_common_settle(constant.Behavior.MAINTENANCE_FACILITIES)


@add_instruct(constant.Instruct.MANAGE_FACILITY_POWER)
def handle_manage_facility_power():
    """处理调控设施供能指令"""
    chara_handle_instruct_common_settle(constant.Behavior.MANAGE_FACILITY_POWER)


@add_instruct(constant.Instruct.MANAGE_POWER_SYSTEM)
def handle_manage_power_system():
    """处理管理能源系统指令"""
    cache.now_panel_id = constant.Panel.MANAGE_POWER_SYSTEM


@add_instruct(constant.Instruct.REPAIR_EQUIPMENT)
def handle_repair_equipment():
    """处理维修装备指令"""
    chara_handle_instruct_common_settle(constant.Behavior.REPAIR_EQUIPMENT)


# 以下为猥亵#


@add_instruct(constant.Instruct.EMBRACE)
def handle_embrace():
    """处理拥抱指令"""
    chara_handle_instruct_common_settle(constant.Behavior.EMBRACE, judge = _("初级骚扰"), force_taget_wait = True)


@add_instruct(constant.Instruct.KISS)
def handle_kiss():
    """处理亲吻指令"""
    chara_handle_instruct_common_settle(constant.Behavior.KISS, judge = _("亲吻"))


@add_instruct(constant.Instruct.TOUCH_HEAD)
def handle_touch_head():
    """处理摸头指令"""
    chara_handle_instruct_common_settle(constant.Behavior.TOUCH_HEAD, judge = _("初级骚扰"))


@add_instruct(constant.Instruct.TOUCH_BREAST)
def handle_touch_breast():
    """处理摸胸指令"""
    chara_handle_instruct_common_settle(constant.Behavior.TOUCH_BREAST, judge = _("初级骚扰"))


@add_instruct(constant.Instruct.TOUCH_BUTTOCKS)
def handle_touch_buttocks():
    """处理摸屁股指令"""
    chara_handle_instruct_common_settle(constant.Behavior.TOUCH_BUTTOCKS, judge = _("初级骚扰"))


@add_instruct(constant.Instruct.TOUCH_EARS)
def handle_touch_ears():
    """处理摸耳朵指令"""
    chara_handle_instruct_common_settle(constant.Behavior.TOUCH_EARS, judge = _("初级骚扰"))


@add_instruct(constant.Instruct.TOUCH_HORN)
def handle_touch_horn():
    """处理摸角指令"""
    chara_handle_instruct_common_settle(constant.Behavior.TOUCH_HORN, judge = _("初级骚扰"))


@add_instruct(constant.Instruct.TOUCH_TAIL)
def handle_touch_tail():
    """处理摸尾巴指令"""
    chara_handle_instruct_common_settle(constant.Behavior.TOUCH_TAIL, judge = _("初级骚扰"))


@add_instruct(constant.Instruct.TOUCH_RING)
def handle_touch_ring():
    """处理摸光环指令"""
    chara_handle_instruct_common_settle(constant.Behavior.TOUCH_RING, judge = _("初级骚扰"))


@add_instruct(constant.Instruct.TOUCH_WING)
def handle_touch_wing():
    """处理摸翅膀指令"""
    chara_handle_instruct_common_settle(constant.Behavior.TOUCH_WING, judge = _("初级骚扰"))


@add_instruct(constant.Instruct.TOUCH_TENTACLE)
def handle_touch_tentacle():
    """处理摸触手指令"""
    chara_handle_instruct_common_settle(constant.Behavior.TOUCH_TENTACLE, judge = _("初级骚扰"))


@add_instruct(constant.Instruct.TOUCH_CAR)
def handle_touch_car():
    """处理摸小车指令"""
    chara_handle_instruct_common_settle(constant.Behavior.TOUCH_CAR, judge = _("初级骚扰"))


@add_instruct(constant.Instruct.HAND_IN_HAND)
def handle_handle_in_handle():
    """处理牵手指令"""
    chara_handle_instruct_common_settle(constant.Behavior.HAND_IN_HAND, judge = _("初级骚扰"))


@add_instruct(constant.Instruct.LAP_PILLOW)
def handle_lap_pillow():
    """处理膝枕指令"""
    chara_handle_instruct_common_settle(constant.Behavior.LAP_PILLOW, judge = _("初级骚扰"))


@add_instruct(constant.Instruct.RAISE_SKIRT)
def handle_raise_skirt():
    """处理掀起裙子指令"""
    chara_handle_instruct_common_settle(constant.Behavior.RAISE_SKIRT, judge = _("严重骚扰"))


@add_instruct(constant.Instruct.ASK_FOR_PAN)
def handle_ask_for_pan():
    """处理索要内裤指令"""
    chara_handle_instruct_common_settle(constant.Behavior.ASK_FOR_PAN, judge = _("严重骚扰"))


@add_instruct(constant.Instruct.ASK_FOR_SOCKS)
def handle_ask_for_socks():
    """处理索要袜子指令"""
    chara_handle_instruct_common_settle(constant.Behavior.ASK_FOR_SOCKS, judge = _("严重骚扰"))


@add_instruct(constant.Instruct.INVITE_TO_BATH)
def handle_invite_to_bath():
    """处理一起洗澡指令"""
    chara_handle_instruct_common_settle(constant.Behavior.INVITE_TO_BATH, judge = _("严重骚扰"), force_taget_wait = True)


@add_instruct(constant.Instruct.STEAL_PAN)
def handle_steal_pan():
    """处理偷走内裤指令"""
    chara_handle_instruct_common_settle(constant.Behavior.STEAL_PAN)


@add_instruct(constant.Instruct.STEAL_SOCKS)
def handle_steal_socks():
    """处理偷走袜子指令"""
    chara_handle_instruct_common_settle(constant.Behavior.STEAL_SOCKS)


@add_instruct(constant.Instruct.STEAL_SCENE_ALL_PAN)
def handle_steal_scene_all_pan():
    """处理偷走所有人内裤指令"""
    chara_handle_instruct_common_settle(constant.Behavior.STEAL_SCENE_ALL_PAN)


@add_instruct(constant.Instruct.STEAL_SCENE_ALL_SOCKS)
def handle_steal_scene_all_socks():
    """处理偷走所有人袜子指令"""
    chara_handle_instruct_common_settle(constant.Behavior.STEAL_SCENE_ALL_SOCKS)


@add_instruct(constant.Instruct.TOUCH_CLITORIS)
def handle_touch_clitoris():
    """处理阴蒂爱抚指令"""
    chara_handle_instruct_common_settle(constant.Behavior.TOUCH_CLITORIS, judge = _("严重骚扰"))


@add_instruct(constant.Instruct.TOUCH_VAGINA)
def handle_touch_vagina():
    """处理手指插入（V）指令"""
    chara_handle_instruct_common_settle(constant.Behavior.TOUCH_VAGINA, judge = _("严重骚扰"))


@add_instruct(constant.Instruct.TOUCH_ANUS)
def handle_touch_anus():
    """处理手指插入（A）指令"""
    chara_handle_instruct_common_settle(constant.Behavior.TOUCH_ANUS, judge = _("严重骚扰"))


@add_instruct(constant.Instruct.MILK)
def handle_milk():
    """处理挤奶指令"""
    chara_handle_instruct_common_settle(constant.Behavior.MILK, judge = _("严重骚扰"))

@add_instruct(constant.Instruct.REMOTE_TOY_ON)
def handle_remote_toy_on():
    """处理遥控启动玩具指令"""
    chara_handle_instruct_common_settle(constant.Behavior.REMOTE_TURN_ON_SEX_TOY, judge = _("严重骚扰"))

@add_instruct(constant.Instruct.REMOTE_TOY_OFF)
def handle_remote_toy_off():
    """处理遥控关闭玩具指令"""
    chara_handle_instruct_common_settle(constant.Behavior.REMOTE_TURN_OFF_SEX_TOY)

@add_instruct(constant.Instruct.REMOTE_TOY_LEVEL_UP)
def handle_remote_toy_level_up():
    """处理调高玩具档位指令"""
    if handle_premise.handle_target_now_sex_toy_weak(0):
        chara_handle_instruct_common_settle(constant.Behavior.REMOTE_SET_SEX_TOY_WEAK_TO_MEDIUM, judge = _("严重骚扰"))
    else:
        chara_handle_instruct_common_settle(constant.Behavior.REMOTE_SET_SEX_TOY_STRONG, judge = _("严重骚扰"))

@add_instruct(constant.Instruct.REMOTE_TOY_LEVEL_DOWN)
def handle_remote_toy_level_down():
    """处理降低玩具档位指令"""
    if handle_premise.handle_target_now_sex_toy_strong(0):
        chara_handle_instruct_common_settle(constant.Behavior.REMOTE_SET_SEX_TOY_STRONG_TO_MEDIUM, judge = _("严重骚扰"))
    else:
        chara_handle_instruct_common_settle(constant.Behavior.REMOTE_SET_SEX_TOY_WEAK, judge = _("严重骚扰"))

@add_instruct(constant.Instruct.REMOTE_TOY_ALL_OFF)
def handle_remote_toy_all_off():
    """处理遥控关闭全员玩具指令"""
    chara_handle_instruct_common_settle(constant.Behavior.REMOTE_ALL_TURN_OFF_SEX_TOY, judge = _("严重骚扰"))

@add_instruct(constant.Instruct.REMOTE_ALL_SET_SEX_TOY_WEAK)
def handle_remote_all_set_sex_toy_weak():
    """处理全员玩具调到弱档指令"""
    chara_handle_instruct_common_settle(constant.Behavior.REMOTE_ALL_SET_SEX_TOY_WEAK, judge = _("严重骚扰"))

@add_instruct(constant.Instruct.REMOTE_ALL_SET_SEX_TOY_MEDIUM)
def handle_remote_all_set_sex_toy_medium():
    """处理全员玩具调到中档指令"""
    chara_handle_instruct_common_settle(constant.Behavior.REMOTE_ALL_SET_SEX_TOY_MEDIUM, judge = _("严重骚扰"))

@add_instruct(constant.Instruct.REMOTE_ALL_SET_SEX_TOY_STRONG)
def handle_remote_all_set_sex_toy_strong():
    """处理全员玩具调到强档指令"""
    chara_handle_instruct_common_settle(constant.Behavior.REMOTE_ALL_SET_SEX_TOY_STRONG, judge = _("严重骚扰"))

@add_instruct(constant.Instruct.BAGGING_AND_MOVING)
def handle_bagging_and_moving():
    """处理装袋搬走指令"""
    chara_handle_instruct_common_settle(constant.Behavior.BAGGING_AND_MOVING)


@add_instruct(constant.Instruct.RELEASE_FROM_BAG)
def handle_release_from_bag():
    """处理从袋中放出来指令"""
    pl_character_data = cache.character_data[0]
    pl_character_data.target_character_id = pl_character_data.sp_flag.bagging_chara_id
    chara_handle_instruct_common_settle(constant.Behavior.RELEASE_FROM_BAG,force_taget_wait = True)

@add_instruct(constant.Instruct.PUT_INTO_PRISON)
def handle_put_into_prision():
    """处理投入监牢指令"""
    pl_character_data = cache.character_data[0]
    pl_character_data.target_character_id = pl_character_data.sp_flag.bagging_chara_id
    chara_handle_instruct_common_settle(constant.Behavior.PUT_INTO_PRISON,force_taget_wait = True)


@add_instruct(constant.Instruct.SET_FREE)
def handle_set_free():
    """处理解除囚禁指令"""
    chara_handle_instruct_common_settle(constant.Behavior.SET_FREE)


# 以下为性爱#


@add_instruct(constant.Instruct.MAKING_OUT)
def handle_making_out():
    """处理身体爱抚指令"""
    chara_handle_instruct_common_settle(constant.Behavior.MAKING_OUT)


@add_instruct(constant.Instruct.KISS_H)
def handle_kiss_h():
    """处理接吻指令"""
    chara_handle_instruct_common_settle(constant.Behavior.KISS_H, judge = _("亲吻"))


@add_instruct(constant.Instruct.BREAST_CARESS)
def handle_breast_caress():
    """处理胸爱抚指令"""
    chara_handle_instruct_common_settle(constant.Behavior.BREAST_CARESS)


@add_instruct(constant.Instruct.TWIDDLE_NIPPLES)
def handle_twiddle_nipples():
    """处理玩弄乳头指令"""
    chara_handle_instruct_common_settle(constant.Behavior.TWIDDLE_NIPPLES)


@add_instruct(constant.Instruct.BREAST_SUCKING)
def handle_breast_sucking():
    """处理舔吸乳头指令"""
    chara_handle_instruct_common_settle(constant.Behavior.BREAST_SUCKING)


@add_instruct(constant.Instruct.EXTERNAL_WOMB_MASSAGE)
def handle_external_womb_massage():
    """处理体外子宫按摩指令"""
    chara_handle_instruct_common_settle(constant.Behavior.EXTERNAL_WOMB_MASSAGE)


@add_instruct(constant.Instruct.CLIT_CARESS)
def handle_cilt_caress():
    """处理阴蒂爱抚指令"""
    chara_handle_instruct_common_settle(constant.Behavior.CLIT_CARESS)


@add_instruct(constant.Instruct.OPEN_LABIA)
def handle_open_labia():
    """处理掰开阴唇观察指令"""
    chara_handle_instruct_common_settle(constant.Behavior.OPEN_LABIA)


@add_instruct(constant.Instruct.OPEN_ANUS)
def handle_open_anus():
    """处理掰开肛门观察指令"""
    chara_handle_instruct_common_settle(constant.Behavior.OPEN_ANUS)


@add_instruct(constant.Instruct.CUNNILINGUS)
def handle_cunnilingus():
    """处理舔阴指令"""
    chara_handle_instruct_common_settle(constant.Behavior.CUNNILINGUS)


@add_instruct(constant.Instruct.LICK_ANAL)
def handle_lict_anal():
    """处理舔肛指令"""
    chara_handle_instruct_common_settle(constant.Behavior.LICK_ANAL)


@add_instruct(constant.Instruct.FINGER_INSERTION)
def handle_finger_insertion():
    """处理手指插入(V)指令"""
    chara_handle_instruct_common_settle(constant.Behavior.FINGER_INSERTION)


@add_instruct(constant.Instruct.ANAL_CARESS)
def handle_anal_caress():
    """处理手指插入(A)指令"""
    chara_handle_instruct_common_settle(constant.Behavior.ANAL_CARESS)


@add_instruct(constant.Instruct.URETHRAL_FINGER_INSERTION)
def handle_urethral_finger_insertion():
    """处理尿道指姦指令"""
    chara_handle_instruct_common_settle(constant.Behavior.URETHRAL_FINGER_INSERTION, judge = _("U开发"))

@add_instruct(constant.Instruct.MAKE_MASTUREBATE)
def handle_make_masturebate():
    """处理命令对方自慰指令"""
    chara_handle_instruct_common_settle(constant.Behavior.MAKE_MASTUREBATE)


@add_instruct(constant.Instruct.MAKE_LICK_ANAL)
def handle_make_lick_anal():
    """处理命令对方舔自己肛门指令"""
    chara_handle_instruct_common_settle(constant.Behavior.MAKE_LICK_ANAL)

@add_instruct(constant.Instruct.ASK_PEE)
def handle_ask_pee():
    """处理命令对方小便指令"""
    chara_handle_instruct_common_settle(constant.Behavior.ASK_PEE, judge = _("严重骚扰"))

@add_instruct(constant.Instruct.SEDECU)
def handle_sedecu():
    """处理诱惑对方指令"""
    chara_handle_instruct_common_settle(constant.Behavior.SEDECU)


@add_instruct(constant.Instruct.HANDJOB)
def handle_handjob():
    """处理手交指令"""
    chara_handle_instruct_common_settle(constant.Behavior.HANDJOB)


@add_instruct(constant.Instruct.BLOWJOB)
def handle_blowjob():
    """处理口交指令"""
    chara_handle_instruct_common_settle(constant.Behavior.BLOWJOB, judge = _("口交"))


@add_instruct(constant.Instruct.PAIZURI)
def handle_paizuri():
    """处理乳交指令"""
    chara_handle_instruct_common_settle(constant.Behavior.PAIZURI)


@add_instruct(constant.Instruct.FOOTJOB)
def handle_footjob():
    """处理足交指令"""
    chara_handle_instruct_common_settle(constant.Behavior.FOOTJOB)


@add_instruct(constant.Instruct.HAIRJOB)
def handle_hairjob():
    """处理发交指令"""
    chara_handle_instruct_common_settle(constant.Behavior.HAIRJOB)


@add_instruct(constant.Instruct.AXILLAJOB)
def handle_axillajob():
    """处理腋交指令"""
    chara_handle_instruct_common_settle(constant.Behavior.AXILLAJOB)


@add_instruct(constant.Instruct.RUB_BUTTOCK)
def handle_rub_buttock():
    """处理素股指令"""
    chara_handle_instruct_common_settle(constant.Behavior.RUB_BUTTOCK)


@add_instruct(constant.Instruct.HAND_BLOWJOB)
def handle_hand_blowjob():
    """处理手交口交指令"""
    chara_handle_instruct_common_settle(constant.Behavior.HAND_BLOWJOB, judge = _("口交"))


@add_instruct(constant.Instruct.TITS_BLOWJOB)
def handle_tits_blowjob():
    """处理乳交口交指令"""
    chara_handle_instruct_common_settle(constant.Behavior.TITS_BLOWJOB, judge = _("口交"))


@add_instruct(constant.Instruct.FOCUS_BLOWJOB)
def handle_focus_blowjob():
    """处理真空口交指令"""
    chara_handle_instruct_common_settle(constant.Behavior.FOCUS_BLOWJOB, judge = _("口交"))


@add_instruct(constant.Instruct.DEEP_THROAT)
def handle_deep_throat():
    """处理深喉插入指令"""
    chara_handle_instruct_common_settle(constant.Behavior.DEEP_THROAT, judge = _("SM"))


@add_instruct(constant.Instruct.CLEAN_BLOWJOB)
def handle_clean_blowjob():
    """处理清洁口交指令"""
    chara_handle_instruct_common_settle(constant.Behavior.CLEAN_BLOWJOB, judge = _("口交"))


@add_instruct(constant.Instruct.SIXTY_NINE)
def handle_sixty_nine():
    """处理六九式指令"""
    chara_handle_instruct_common_settle(constant.Behavior.SIXTY_NINE, judge = _("口交"))


@add_instruct(constant.Instruct.LEGJOB)
def handle_legjob():
    """处理腿交指令"""
    chara_handle_instruct_common_settle(constant.Behavior.LEGJOB)


@add_instruct(constant.Instruct.TAILJOB)
def handle_tailjob():
    """处理尾交指令"""
    chara_handle_instruct_common_settle(constant.Behavior.TAILJOB)


@add_instruct(constant.Instruct.FACE_RUB)
def handle_face_rub():
    """处理阴茎蹭脸指令"""
    chara_handle_instruct_common_settle(constant.Behavior.FACE_RUB)


@add_instruct(constant.Instruct.HORN_RUB)
def handle_horn_rub():
    """处理阴茎蹭角指令"""
    chara_handle_instruct_common_settle(constant.Behavior.HORN_RUB)


@add_instruct(constant.Instruct.EARS_RUB)
def handle_eras_rub():
    """处理阴茎蹭耳朵指令"""
    chara_handle_instruct_common_settle(constant.Behavior.EARS_RUB)


@add_instruct(constant.Instruct.HAT_JOB)
def handle_hat_job():
    """处理帽子交指令"""
    chara_handle_instruct_common_settle(constant.Behavior.HAT_JOB)


@add_instruct(constant.Instruct.GLASSES_JOB)
def handle_glasses_job():
    """处理眼镜交指令"""
    chara_handle_instruct_common_settle(constant.Behavior.GLASSES_JOB)


@add_instruct(constant.Instruct.EAR_ORNAMENT_JOB)
def handle_ear_ornament_job():
    """处理耳饰交指令"""
    chara_handle_instruct_common_settle(constant.Behavior.EAR_ORNAMENT_JOB)


@add_instruct(constant.Instruct.NECK_ORNAMENT_JOB)
def handle_neck_ornament_job():
    """处理脖饰交指令"""
    chara_handle_instruct_common_settle(constant.Behavior.NECK_ORNAMENT_JOB)


@add_instruct(constant.Instruct.MOUTH_ORNAMENT_JOB)
def handle_mouth_ornament_job():
    """处理口罩交指令"""
    chara_handle_instruct_common_settle(constant.Behavior.MOUTH_ORNAMENT_JOB)


@add_instruct(constant.Instruct.TOP_JOB)
def handle_top_job():
    """处理上衣交指令"""
    chara_handle_instruct_common_settle(constant.Behavior.TOP_JOB)


@add_instruct(constant.Instruct.CORSET_JOB)
def handle_corset_job():
    """处理胸衣交指令"""
    chara_handle_instruct_common_settle(constant.Behavior.CORSET_JOB)


@add_instruct(constant.Instruct.GLOVES_JOB)
def handle_gloves_job():
    """处理手套交指令"""
    chara_handle_instruct_common_settle(constant.Behavior.GLOVES_JOB)


@add_instruct(constant.Instruct.SKIRT_JOB)
def handle_skirt_job():
    """处理裙子交指令"""
    chara_handle_instruct_common_settle(constant.Behavior.SKIRT_JOB)


@add_instruct(constant.Instruct.TROUSERS_JOB)
def handle_trousers_job():
    """处理裤子交指令"""
    chara_handle_instruct_common_settle(constant.Behavior.TROUSERS_JOB)


@add_instruct(constant.Instruct.UNDERWEAR_JOB)
def handle_underwear_job():
    """处理内裤交指令"""
    chara_handle_instruct_common_settle(constant.Behavior.UNDERWEAR_JOB)


@add_instruct(constant.Instruct.SOCKS_JOB)
def handle_socks_job():
    """处理袜子交指令"""
    chara_handle_instruct_common_settle(constant.Behavior.SOCKS_JOB)


@add_instruct(constant.Instruct.SHOES_JOB)
def handle_shoes_job():
    """处理鞋子交指令"""
    chara_handle_instruct_common_settle(constant.Behavior.SHOES_JOB)


@add_instruct(constant.Instruct.WEAPONS_JOB)
def handle_weapons_job():
    """处理武器交指令"""
    chara_handle_instruct_common_settle(constant.Behavior.WEAPONS_JOB)


@add_instruct(constant.Instruct.NIPPLE_CLAMP_ON)
def handle_nipple_clamp_on():
    """处理戴上乳头夹指令"""
    chara_handle_instruct_common_settle(constant.Behavior.NIPPLE_CLAMP_ON, judge = _("道具"))


@add_instruct(constant.Instruct.NIPPLE_CLAMP_OFF)
def handle_nipple_clamp_off():
    """处理取下乳头夹指令"""
    chara_handle_instruct_common_settle(constant.Behavior.NIPPLE_CLAMP_OFF)

@add_instruct(constant.Instruct.URETHRAL_SWAB)
def handle_urethral_swab():
    """处理尿道棉棒指令"""
    chara_handle_instruct_common_settle(constant.Behavior.URETHRAL_SWAB, judge = _("U开发"))

@add_instruct(constant.Instruct.NIPPLES_LOVE_EGG)
def handle_nipples_love_egg():
    """处理乳头跳蛋指令"""
    chara_handle_instruct_common_settle(constant.Behavior.NIPPLES_LOVE_EGG)


@add_instruct(constant.Instruct.CLIT_CLAMP_ON)
def handle_clit_clamp_on():
    """处理戴上阴蒂夹指令"""
    chara_handle_instruct_common_settle(constant.Behavior.CLIT_CLAMP_ON, judge = _("道具"))


@add_instruct(constant.Instruct.CLIT_CLAMP_OFF)
def handle_clit_clamp_off():
    """处理取下阴蒂夹指令"""
    chara_handle_instruct_common_settle(constant.Behavior.CLIT_CLAMP_OFF)


@add_instruct(constant.Instruct.CLIT_LOVE_EGG)
def handle_clit_love_egg():
    """处理阴蒂跳蛋指令"""
    chara_handle_instruct_common_settle(constant.Behavior.CLIT_LOVE_EGG)


@add_instruct(constant.Instruct.ELECTRIC_MESSAGE_STICK)
def handle_electric_message_stick():
    """处理电动按摩棒指令"""
    chara_handle_instruct_common_settle(constant.Behavior.ELECTRIC_MESSAGE_STICK)


@add_instruct(constant.Instruct.VIBRATOR_INSERTION)
def handle_vibrator_insertion():
    """处理插入震动棒指令"""
    chara_handle_instruct_common_settle(constant.Behavior.VIBRATOR_INSERTION, judge = _("道具"))


@add_instruct(constant.Instruct.VIBRATOR_INSERTION_ANAL)
def handle_vibrator_insertion_anal():
    """处理肛门插入震动棒指令"""
    chara_handle_instruct_common_settle(constant.Behavior.VIBRATOR_INSERTION_ANAL, judge = _("道具"))


@add_instruct(constant.Instruct.VIBRATOR_INSERTION_OFF)
def handle_vibrator_insertion_off():
    """处理拔出震动棒指令"""
    chara_handle_instruct_common_settle(constant.Behavior.VIBRATOR_INSERTION_OFF)


@add_instruct(constant.Instruct.VIBRATOR_INSERTION_ANAL_OFF)
def handle_vibrator_insertion_anal_off():
    """处理拔出肛门震动棒指令"""
    chara_handle_instruct_common_settle(constant.Behavior.VIBRATOR_INSERTION_ANAL_OFF)


@add_instruct(constant.Instruct.CLYSTER)
def handle_clyster():
    """处理灌肠指令"""
    chara_handle_instruct_common_settle(constant.Behavior.CLYSTER, judge = _("SM"))


@add_instruct(constant.Instruct.CONTINUE_CLYSTER)
def handle_continue_clyster():
    """处理继续灌肠指令"""
    chara_handle_instruct_common_settle(constant.Behavior.CLYSTER, judge = _("SM"))


@add_instruct(constant.Instruct.CLYSTER_END)
def handle_clyster_end():
    """处理拔出肛塞指令"""
    chara_handle_instruct_common_settle(constant.Behavior.CLYSTER_END)


@add_instruct(constant.Instruct.ANAL_PLUG)
def handle_anal_plug():
    """处理肛塞指令"""
    chara_handle_instruct_common_settle(constant.Behavior.ANAL_PLUG)


@add_instruct(constant.Instruct.ANAL_BEADS)
def handle_anal_beads():
    """处理塞入肛门拉珠指令"""
    chara_handle_instruct_common_settle(constant.Behavior.ANAL_BEADS, judge = _("道具"))


@add_instruct(constant.Instruct.ANAL_BEADS_OFF)
def handle_anal_beads_off():
    """处理拔出肛门拉珠指令"""
    chara_handle_instruct_common_settle(constant.Behavior.ANAL_BEADS_OFF)


@add_instruct(constant.Instruct.MILKING_MACHINE_ON)
def handle_milking_machine_on():
    """处理装上搾乳机指令"""
    chara_handle_instruct_common_settle(constant.Behavior.MILKING_MACHINE_ON, judge = _("道具"))


@add_instruct(constant.Instruct.MILKING_MACHINE_OFF)
def handle_milking_machine_off():
    """处理取下搾乳机指令"""
    chara_handle_instruct_common_settle(constant.Behavior.MILKING_MACHINE_OFF)


@add_instruct(constant.Instruct.URINE_COLLECTOR_ON)
def handle_urine_collector_on():
    """处理装上采尿器指令"""
    chara_handle_instruct_common_settle(constant.Behavior.URINE_COLLECTOR_ON, judge = _("U开发"))


@add_instruct(constant.Instruct.URINE_COLLECTOR_OFF)
def handle_urine_collector_off():
    """处理取下采尿器指令"""
    chara_handle_instruct_common_settle(constant.Behavior.URINE_COLLECTOR_OFF)

@add_instruct(constant.Instruct.REMOTE_TOY_ON_IN_H)
def handle_remote_toy_on_in_h():
    """处理遥控启动玩具指令"""
    chara_handle_instruct_common_settle(constant.Behavior.REMOTE_TURN_ON_SEX_TOY)

@add_instruct(constant.Instruct.REMOTE_TOY_OFF_IN_H)
def handle_remote_toy_off_in_h():
    """处理遥控关闭玩具指令"""
    chara_handle_instruct_common_settle(constant.Behavior.REMOTE_TURN_OFF_SEX_TOY)

@add_instruct(constant.Instruct.REMOTE_TOY_LEVEL_UP_IN_H)
def handle_remote_toy_level_up_in_h():
    """处理调高玩具档位指令"""
    if handle_premise.handle_target_now_sex_toy_weak(0):
        chara_handle_instruct_common_settle(constant.Behavior.REMOTE_SET_SEX_TOY_WEAK_TO_MEDIUM)
    else:
        chara_handle_instruct_common_settle(constant.Behavior.REMOTE_SET_SEX_TOY_STRONG)

@add_instruct(constant.Instruct.REMOTE_TOY_LEVEL_DOWN_IN_H)
def handle_remote_toy_level_down_in_h():
    """处理降低玩具档位指令"""
    if handle_premise.handle_target_now_sex_toy_strong(0):
        chara_handle_instruct_common_settle(constant.Behavior.REMOTE_SET_SEX_TOY_STRONG_TO_MEDIUM)
    else:
        chara_handle_instruct_common_settle(constant.Behavior.REMOTE_SET_SEX_TOY_WEAK)

@add_instruct(constant.Instruct.REMOTE_TOY_ALL_OFF_IN_H)
def handle_remote_toy_all_off_in_h():
    """处理遥控关闭全员玩具指令"""
    chara_handle_instruct_common_settle(constant.Behavior.REMOTE_ALL_TURN_OFF_SEX_TOY, judge = _("严重骚扰"))

@add_instruct(constant.Instruct.REMOTE_ALL_SET_SEX_TOY_WEAK_IN_H)
def handle_remote_all_set_sex_toy_weak_in_h():
    """处理全员玩具调到弱档指令"""
    chara_handle_instruct_common_settle(constant.Behavior.REMOTE_ALL_SET_SEX_TOY_WEAK, judge = _("严重骚扰"))

@add_instruct(constant.Instruct.REMOTE_ALL_SET_SEX_TOY_MEDIUM_IN_H)
def handle_remote_all_set_sex_toy_medium_in_h():
    """处理全员玩具调到中档指令"""
    chara_handle_instruct_common_settle(constant.Behavior.REMOTE_ALL_SET_SEX_TOY_MEDIUM, judge = _("严重骚扰"))

@add_instruct(constant.Instruct.REMOTE_ALL_SET_SEX_TOY_STRONG_IN_H)
def handle_remote_all_set_sex_toy_strong_in_h():
    """处理全员玩具调到强档指令"""
    chara_handle_instruct_common_settle(constant.Behavior.REMOTE_ALL_SET_SEX_TOY_STRONG, judge = _("严重骚扰"))

@add_instruct(constant.Instruct.BONDAGE)
def handle_bondage():
    """处理绳艺指令"""
    from Script.System.Sex_System import bondage_panel
    now_panel = bondage_panel.Bondage_Panel(width=width)
    now_panel.draw()


@add_instruct(constant.Instruct.PATCH_ON)
def handle_patch_on():
    """处理戴上眼罩指令"""
    chara_handle_instruct_common_settle(constant.Behavior.PATCH_ON)


@add_instruct(constant.Instruct.PATCH_OFF)
def handle_patch_off():
    """处理摘下眼罩指令"""
    chara_handle_instruct_common_settle(constant.Behavior.PATCH_OFF)


@add_instruct(constant.Instruct.GAG_ON)
def handle_gag_on():
    """处理戴上口球指令"""
    chara_handle_instruct_common_settle(constant.Behavior.GAG_ON)


@add_instruct(constant.Instruct.GAG_OFF)
def handle_gag_off():
    """处理摘下口球指令"""
    chara_handle_instruct_common_settle(constant.Behavior.GAG_OFF)


@add_instruct(constant.Instruct.WHIP)
def handle_whip():
    """处理鞭子指令"""
    chara_handle_instruct_common_settle(constant.Behavior.WHIP, judge = _("SM"))


@add_instruct(constant.Instruct.NEEDLE)
def handle_neddle():
    """处理针指令"""
    chara_handle_instruct_common_settle(constant.Behavior.NEEDLE, judge = _("SM"))


@add_instruct(constant.Instruct.PUT_CONDOM)
def handle_put_condom():
    """处理戴上避孕套指令"""
    chara_handle_instruct_common_settle(constant.Behavior.PUT_CONDOM)


@add_instruct(constant.Instruct.TAKE_CONDOM_OUT)
def handle_take_condom_out():
    """处理摘掉避孕套指令"""
    chara_handle_instruct_common_settle(constant.Behavior.TAKE_CONDOM_OUT)


@add_instruct(constant.Instruct.SAFE_CANDLES)
def handle_safe_candles():
    """处理滴蜡指令"""
    chara_handle_instruct_common_settle(constant.Behavior.SAFE_CANDLES, judge = _("SM"))


@add_instruct(constant.Instruct.BODY_LUBRICANT)
def handle_body_lubricant():
    """处理润滑液指令"""
    chara_handle_instruct_common_settle(constant.Behavior.BODY_LUBRICANT)


@add_instruct(constant.Instruct.PHILTER)
def handle_philter():
    """处理媚药指令"""
    chara_handle_instruct_common_settle(constant.Behavior.PHILTER, judge = _("药物"))


@add_instruct(constant.Instruct.ENEMAS)
def handle_enemas():
    """处理灌肠液指令"""
    instuct_judege.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)


@add_instruct(constant.Instruct.DIURETICS_ONCE)
def handle_diuretics_once():
    """处理一次性利尿剂指令"""
    chara_handle_instruct_common_settle(constant.Behavior.DIURETICS_ONCE, judge = _("药物"))


@add_instruct(constant.Instruct.DIURETICS_PERSISTENT)
def handle_diuretics_persistent():
    """处理持续性利尿剂指令"""
    chara_handle_instruct_common_settle(constant.Behavior.DIURETICS_PERSISTENT, judge = _("药物"))


@add_instruct(constant.Instruct.SLEEPING_PILLS)
def handle_sleeping_pills():
    """处理安眠药指令"""
    chara_handle_instruct_common_settle(constant.Behavior.SLEEPING_PILLS, judge = _("药物"))


@add_instruct(constant.Instruct.CLOMID)
def handle_clomid():
    """处理排卵促进药指令"""
    chara_handle_instruct_common_settle(constant.Behavior.CLOMID, judge = _("药物"))


@add_instruct(constant.Instruct.BIRTH_CONTROL_PILLS_BEFORE)
def handle_birth_control_pills_before():
    """处理事前避孕药指令"""
    chara_handle_instruct_common_settle(constant.Behavior.BIRTH_CONTROL_PILLS_BEFORE)


@add_instruct(constant.Instruct.BIRTH_CONTROL_PILLS_AFTER)
def handle_birth_control_pills_after():
    """处理事后避孕药指令"""
    chara_handle_instruct_common_settle(constant.Behavior.BIRTH_CONTROL_PILLS_AFTER)

@add_instruct(constant.Instruct.VAGINAL_SEX)
def handle_vaginal_sex():
    """处理阴道性交指令"""
    from Script.System.Sex_System import sex_position_panel
    now_panel = sex_position_panel.Sex_Position_Panel(width=width)
    now_panel.draw()

@add_instruct(constant.Instruct.CHANGE_VAGINAL_SEX_POSITION)
def handle_change_vaginal_sex_position():
    """处理换阴道性交体位指令"""
    from Script.System.Sex_System import sex_position_panel
    now_panel = sex_position_panel.Sex_Position_Panel(width=width, change_position=True)
    now_panel.draw()

@add_instruct(constant.Instruct.NORMAL_SEX)
def handle_normal_sex():
    """处理正常位指令"""
    chara_handle_instruct_common_settle(constant.Behavior.NORMAL_SEX, judge = _("性交"))

@add_instruct(constant.Instruct.BACK_SEX)
def handle_back_sex():
    """处理背后位指令"""
    chara_handle_instruct_common_settle(constant.Behavior.BACK_SEX, judge = _("性交"))

@add_instruct(constant.Instruct.RIDING_SEX)
def handle_riding_sex():
    """处理对面骑乘位指令"""
    chara_handle_instruct_common_settle(constant.Behavior.RIDING_SEX, judge = _("性交"))

@add_instruct(constant.Instruct.BACK_RIDING_SEX)
def handle_back_riding_sex():
    """处理背面骑乘位指令"""
    chara_handle_instruct_common_settle(constant.Behavior.BACK_RIDING_SEX, judge = _("性交"))

@add_instruct(constant.Instruct.FACE_SEAT_SEX)
def handle_face_seat_sex():
    """处理对面座位指令"""
    chara_handle_instruct_common_settle(constant.Behavior.FACE_SEAT_SEX, judge = _("性交"))

@add_instruct(constant.Instruct.BACK_SEAT_SEX)
def handle_back_seat_sex():
    """处理背面座位指令"""
    chara_handle_instruct_common_settle(constant.Behavior.BACK_SEAT_SEX, judge = _("性交"))

@add_instruct(constant.Instruct.FACE_STAND_SEX)
def handle_face_stand_sex():
    """处理对面立位指令"""
    chara_handle_instruct_common_settle(constant.Behavior.FACE_STAND_SEX, judge = _("性交"))

@add_instruct(constant.Instruct.BACK_STAND_SEX)
def handle_back_stand_sex():
    """处理背面立位指令"""
    chara_handle_instruct_common_settle(constant.Behavior.BACK_STAND_SEX, judge = _("性交"))

@add_instruct(constant.Instruct.FACE_HUG_SEX)
def handle_face_hug_sex():
    """处理对面抱位指令"""
    chara_handle_instruct_common_settle(constant.Behavior.FACE_HUG_SEX, judge=_("性交"))

@add_instruct(constant.Instruct.BACK_HUG_SEX)
def handle_back_hug_sex():
    """处理背面抱位指令"""
    chara_handle_instruct_common_settle(constant.Behavior.BACK_HUG_SEX, judge=_("性交"))

@add_instruct(constant.Instruct.FACE_LAY_SEX)
def handle_face_lay_sex():
    """处理对面卧位指令"""
    chara_handle_instruct_common_settle(constant.Behavior.FACE_LAY_SEX, judge=_("性交"))

@add_instruct(constant.Instruct.BACK_LAY_SEX)
def handle_back_lay_sex():
    """处理背面卧位指令"""
    chara_handle_instruct_common_settle(constant.Behavior.BACK_LAY_SEX, judge=_("性交"))

@add_instruct(constant.Instruct.STIMULATE_G_POINT)
def handle_stimulate_g_point():
    """处理刺激G点指令"""
    chara_handle_instruct_common_settle(constant.Behavior.STIMULATE_G_POINT, judge = _("性交"))

@add_instruct(constant.Instruct.WOMB_OS_CARESS)
def handle_womb_os_caress():
    """处理玩弄子宫口指令"""
    chara_handle_instruct_common_settle(constant.Behavior.WOMB_OS_CARESS, judge = _("性交"))

# @add_instruct(#     constant.Instruct.WOMB_INSERTION)
# def handle_womb_insertion():
#     """处理插入子宫口指令"""
#     chara_handle_instruct_common_settle(constant.Behavior.WOMB_INSERTION, judge = _("W性交"))

@add_instruct(constant.Instruct.CHANGE_CERVIX_SEX_POSITION)
def handle_change_cervix_sex_position():
    """处理换子宫姦口体位指令"""
    from Script.System.Sex_System import sex_position_panel
    now_panel = sex_position_panel.Sex_Position_Panel(width=width, sex_type=2, change_position=True)
    now_panel.draw()

@add_instruct(constant.Instruct.NORMAL_CERVIX_SEX)
def handle_normal_cervix_sex():
    """处理正常位子宫口姦指令"""
    chara_handle_instruct_common_settle(constant.Behavior.NORMAL_CERVIX_SEX, judge=_("W性交"))

@add_instruct(constant.Instruct.BACK_CERVIX_SEX)
def handle_back_cervix_sex():
    """处理后背位子宫口姦指令"""
    chara_handle_instruct_common_settle(constant.Behavior.BACK_CERVIX_SEX, judge=_("W性交"))

@add_instruct(constant.Instruct.RIDING_CERVIX_SEX)
def handle_riding_cervix_sex():
    """处理对面骑乘位子宫口姦指令"""
    chara_handle_instruct_common_settle(constant.Behavior.RIDING_CERVIX_SEX, judge=_("W性交"))

@add_instruct(constant.Instruct.BACK_RIDING_CERVIX_SEX)
def handle_back_riding_cervix_sex():
    """处理背面骑乘位子宫口姦指令"""
    chara_handle_instruct_common_settle(constant.Behavior.BACK_RIDING_CERVIX_SEX, judge=_("W性交"))

@add_instruct(constant.Instruct.FACE_SEAT_CERVIX_SEX)
def handle_face_seat_cervix_sex():
    """处理对面座位子宫口姦指令"""
    chara_handle_instruct_common_settle(constant.Behavior.FACE_SEAT_CERVIX_SEX, judge=_("W性交"))

@add_instruct(constant.Instruct.BACK_SEAT_CERVIX_SEX)
def handle_back_seat_cervix_sex():
    """处理背面座位子宫口姦指令"""
    chara_handle_instruct_common_settle(constant.Behavior.BACK_SEAT_CERVIX_SEX, judge=_("W性交"))

@add_instruct(constant.Instruct.FACE_STAND_CERVIX_SEX)
def handle_face_stand_cervix_sex():
    """处理对面立位子宫口姦指令"""
    chara_handle_instruct_common_settle(constant.Behavior.FACE_STAND_CERVIX_SEX, judge=_("W性交"))

@add_instruct(constant.Instruct.BACK_STAND_CERVIX_SEX)
def handle_back_stand_cervix_sex():
    """处理背面立位子宫口姦指令"""
    chara_handle_instruct_common_settle(constant.Behavior.BACK_STAND_CERVIX_SEX, judge=_("W性交"))

@add_instruct(constant.Instruct.FACE_HUG_CERVIX_SEX)
def handle_face_hug_cervix_sex():
    """处理对面抱位子宫口姦指令"""
    chara_handle_instruct_common_settle(constant.Behavior.FACE_HUG_CERVIX_SEX, judge=_("W性交"))

@add_instruct(constant.Instruct.BACK_HUG_CERVIX_SEX)
def handle_back_hug_cervix_sex():
    """处理背面抱位子宫口姦指令"""
    chara_handle_instruct_common_settle(constant.Behavior.BACK_HUG_CERVIX_SEX, judge=_("W性交"))

@add_instruct(constant.Instruct.FACE_LAY_CERVIX_SEX)
def handle_face_lay_cervix_sex():
    """处理对面卧位子宫口姦指令"""
    chara_handle_instruct_common_settle(constant.Behavior.FACE_LAY_CERVIX_SEX, judge=_("W性交"))

@add_instruct(constant.Instruct.BACK_LAY_CERVIX_SEX)
def handle_back_lay_cervix_sex():
    """处理背面卧位子宫口姦指令"""
    chara_handle_instruct_common_settle(constant.Behavior.BACK_LAY_CERVIX_SEX, judge=_("W性交"))


# @add_instruct(#     constant.Instruct.WOMB_SEX)
# def handle_womb_sex():
#     """处理子宫姦指令"""
#     chara_handle_instruct_common_settle(constant.Behavior.WOMB_SEX, judge = _("W性交"))

@add_instruct(constant.Instruct.CHANGE_WOMB_SEX_POSITION)
def handle_change_womb_sex_position():
    """处理换子宫姦体位指令"""
    from Script.System.Sex_System import sex_position_panel
    now_panel = sex_position_panel.Sex_Position_Panel(width=width, sex_type=3, change_position=True)
    now_panel.draw()

@add_instruct(constant.Instruct.NORMAL_WOMB_SEX)
def handle_normal_womb_sex():
    """处理正常位子宫姦指令"""
    chara_handle_instruct_common_settle(constant.Behavior.NORMAL_WOMB_SEX, judge=_("W性交"))

@add_instruct(constant.Instruct.BACK_WOMB_SEX)
def handle_back_womb_sex():
    """处理后背位子宫姦指令"""
    chara_handle_instruct_common_settle(constant.Behavior.BACK_WOMB_SEX, judge=_("W性交"))

@add_instruct(constant.Instruct.RIDING_WOMB_SEX)
def handle_riding_womb_sex():
    """处理对面骑乘位子宫姦指令"""
    chara_handle_instruct_common_settle(constant.Behavior.RIDING_WOMB_SEX, judge=_("W性交"))

@add_instruct(constant.Instruct.BACK_RIDING_WOMB_SEX)
def handle_back_riding_womb_sex():
    """处理背面骑乘位子宫姦指令"""
    chara_handle_instruct_common_settle(constant.Behavior.BACK_RIDING_WOMB_SEX, judge=_("W性交"))

@add_instruct(constant.Instruct.FACE_SEAT_WOMB_SEX)
def handle_face_seat_womb_sex():
    """处理对面座位子宫姦指令"""
    chara_handle_instruct_common_settle(constant.Behavior.FACE_SEAT_WOMB_SEX, judge=_("W性交"))

@add_instruct(constant.Instruct.BACK_SEAT_WOMB_SEX)
def handle_back_seat_womb_sex():
    """处理背面座位子宫姦指令"""
    chara_handle_instruct_common_settle(constant.Behavior.BACK_SEAT_WOMB_SEX, judge=_("W性交"))

@add_instruct(constant.Instruct.FACE_STAND_WOMB_SEX)
def handle_face_stand_womb_sex():
    """处理对面立位子宫姦指令"""
    chara_handle_instruct_common_settle(constant.Behavior.FACE_STAND_WOMB_SEX, judge=_("W性交"))

@add_instruct(constant.Instruct.BACK_STAND_WOMB_SEX)
def handle_back_stand_womb_sex():
    """处理背面立位子宫姦指令"""
    chara_handle_instruct_common_settle(constant.Behavior.BACK_STAND_WOMB_SEX, judge=_("W性交"))

@add_instruct(constant.Instruct.FACE_HUG_WOMB_SEX)
def handle_face_hug_womb_sex():
    """处理对面抱位子宫姦指令"""
    chara_handle_instruct_common_settle(constant.Behavior.FACE_HUG_WOMB_SEX, judge=_("W性交"))

@add_instruct(constant.Instruct.BACK_HUG_WOMB_SEX)
def handle_back_hug_womb_sex():
    """处理背面抱位子宫姦指令"""
    chara_handle_instruct_common_settle(constant.Behavior.BACK_HUG_WOMB_SEX, judge=_("W性交"))

@add_instruct(constant.Instruct.FACE_LAY_WOMB_SEX)
def handle_face_lay_womb_sex():
    """处理对面卧位子宫姦指令"""
    chara_handle_instruct_common_settle(constant.Behavior.FACE_LAY_WOMB_SEX, judge=_("W性交"))

@add_instruct(constant.Instruct.BACK_LAY_WOMB_SEX)
def handle_back_lay_womb_sex():
    """处理背面卧位子宫姦指令"""
    chara_handle_instruct_common_settle(constant.Behavior.BACK_LAY_WOMB_SEX, judge=_("W性交"))

@add_instruct(constant.Instruct.ANAL_SEX)
def handle_anal_sex():
    """处理肛门性交指令"""
    from Script.System.Sex_System import sex_position_panel
    now_panel = sex_position_panel.Sex_Position_Panel(width=width, sex_type=4)
    now_panel.draw()

@add_instruct(constant.Instruct.CHANGE_ANAL_SEX_POSITION)
def handle_change_anal_sex_position():
    """处理换肛交体位指令"""
    from Script.System.Sex_System import sex_position_panel
    now_panel = sex_position_panel.Sex_Position_Panel(width=width, sex_type=4, change_position=True)
    now_panel.draw()

@add_instruct(constant.Instruct.NORMAL_ANAL_SEX)
def handle_normal_anal_sex():
    """处理正常位肛交指令"""
    chara_handle_instruct_common_settle(constant.Behavior.NORMAL_ANAL_SEX, judge = _("A性交"))


@add_instruct(constant.Instruct.BACK_ANAL_SEX)
def handle_back_anal_sex():
    """处理后背位肛交指令"""
    chara_handle_instruct_common_settle(constant.Behavior.BACK_ANAL_SEX, judge = _("A性交"))

@add_instruct(constant.Instruct.RIDING_ANAL_SEX)
def handle_riding_anal_sex():
    """处理对面骑乘位肛交指令"""
    chara_handle_instruct_common_settle(constant.Behavior.RIDING_ANAL_SEX, judge = _("A性交"))

@add_instruct(constant.Instruct.BACK_RIDING_ANAL_SEX)
def handle_back_riding_anal_sex():
    """处理背面骑乘位肛交指令"""
    chara_handle_instruct_common_settle(constant.Behavior.BACK_RIDING_ANAL_SEX, judge = _("A性交"))

@add_instruct(constant.Instruct.FACE_SEAT_ANAL_SEX)
def handle_face_seat_anal_sex():
    """处理对面座位肛交指令"""
    chara_handle_instruct_common_settle(constant.Behavior.FACE_SEAT_ANAL_SEX, judge = _("A性交"))

@add_instruct(constant.Instruct.BACK_SEAT_ANAL_SEX)
def handle_back_seat_anal_sex():
    """处理背面座位肛交指令"""
    chara_handle_instruct_common_settle(constant.Behavior.BACK_SEAT_ANAL_SEX, judge = _("A性交"))

@add_instruct(constant.Instruct.FACE_STAND_ANAL_SEX)
def handle_face_stand_anal_sex():
    """处理对面立位肛交指令"""
    chara_handle_instruct_common_settle(constant.Behavior.FACE_STAND_ANAL_SEX, judge = _("A性交"))

@add_instruct(constant.Instruct.BACK_STAND_ANAL_SEX)
def handle_back_stand_anal_sex():
    """处理背面立位肛交指令"""
    chara_handle_instruct_common_settle(constant.Behavior.BACK_STAND_ANAL_SEX, judge = _("A性交"))


@add_instruct(constant.Instruct.FACE_HUG_ANAL_SEX)
def handle_face_hug_anal_sex():
    """处理对面抱位肛交指令"""
    chara_handle_instruct_common_settle(constant.Behavior.FACE_HUG_ANAL_SEX, judge=_("A性交"))

@add_instruct(constant.Instruct.BACK_HUG_ANAL_SEX)
def handle_back_hug_anal_sex():
    """处理背面抱位肛交指令"""
    chara_handle_instruct_common_settle(constant.Behavior.BACK_HUG_ANAL_SEX, judge=_("A性交"))

@add_instruct(constant.Instruct.FACE_LAY_ANAL_SEX)
def handle_face_lay_anal_sex():
    """处理对面卧位肛交指令"""
    chara_handle_instruct_common_settle(constant.Behavior.FACE_LAY_ANAL_SEX, judge=_("A性交"))

@add_instruct(constant.Instruct.BACK_LAY_ANAL_SEX)
def handle_back_lay_anal_sex():
    """处理背面卧位肛交指令"""
    chara_handle_instruct_common_settle(constant.Behavior.BACK_LAY_ANAL_SEX, judge=_("A性交"))

@add_instruct(constant.Instruct.STIMULATE_SIGMOID_COLON)
def handle_stimulate_sigmoid_colon():
    """处理玩弄s状结肠指令"""
    chara_handle_instruct_common_settle(constant.Behavior.STIMULATE_SIGMOID_COLON, judge = _("A性交"))

@add_instruct(constant.Instruct.STIMULATE_VAGINA)
def handle_stimulate_vagina():
    """处理隔着刺激阴道指令"""
    chara_handle_instruct_common_settle(constant.Behavior.STIMULATE_VAGINA, judge = _("A性交"))

@add_instruct(constant.Instruct.DOUBLE_PENETRATION)
def handle_double_penetration():
    """处理二穴插入指令"""
    instuct_judege.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(constant.Instruct.URETHRAL_SEX)
def handle_urethral_sex():
    """处理尿道姦指令"""
    from Script.System.Sex_System import sex_position_panel
    now_panel = sex_position_panel.Sex_Position_Panel(width=width, sex_type=5)
    now_panel.draw()


@add_instruct(constant.Instruct.CHANGE_URETHRAL_SEX_POSITION)
def handle_change_urethral_sex_position():
    """处理换尿道姦体位指令"""
    from Script.System.Sex_System import sex_position_panel
    now_panel = sex_position_panel.Sex_Position_Panel(width=width, sex_type=5, change_position=True)
    now_panel.draw()


@add_instruct(constant.Instruct.NORMAL_URETHRAL_SEX)
def handle_normal_urethral_sex():
    """处理正常位尿道姦指令"""
    chara_handle_instruct_common_settle(constant.Behavior.NORMAL_URETHRAL_SEX, judge=_("U性交"))

@add_instruct(constant.Instruct.BACK_URETHRAL_SEX)
def handle_back_urethral_sex():
    """处理后背位尿道姦指令"""
    chara_handle_instruct_common_settle(constant.Behavior.BACK_URETHRAL_SEX, judge=_("U性交"))

@add_instruct(constant.Instruct.RIDING_URETHRAL_SEX)
def handle_riding_urethral_sex():
    """处理对面骑乘位尿道姦指令"""
    chara_handle_instruct_common_settle(constant.Behavior.RIDING_URETHRAL_SEX, judge=_("U性交"))

@add_instruct(constant.Instruct.BACK_RIDING_URETHRAL_SEX)
def handle_back_riding_urethral_sex():
    """处理背面骑乘位尿道姦指令"""
    chara_handle_instruct_common_settle(constant.Behavior.BACK_RIDING_URETHRAL_SEX, judge=_("U性交"))

@add_instruct(constant.Instruct.FACE_SEAT_URETHRAL_SEX)
def handle_face_seat_urethral_sex():
    """处理对面座位尿道姦指令"""
    chara_handle_instruct_common_settle(constant.Behavior.FACE_SEAT_URETHRAL_SEX, judge=_("U性交"))

@add_instruct(constant.Instruct.BACK_SEAT_URETHRAL_SEX)
def handle_back_seat_urethral_sex():
    """处理背面座位尿道姦指令"""
    chara_handle_instruct_common_settle(constant.Behavior.BACK_SEAT_URETHRAL_SEX, judge=_("U性交"))

@add_instruct(constant.Instruct.FACE_STAND_URETHRAL_SEX)
def handle_face_stand_urethral_sex():
    """处理对面立位尿道姦指令"""
    chara_handle_instruct_common_settle(constant.Behavior.FACE_STAND_URETHRAL_SEX, judge=_("U性交"))

@add_instruct(constant.Instruct.BACK_STAND_URETHRAL_SEX)
def handle_back_stand_urethral_sex():
    """处理背面立位尿道姦指令"""
    chara_handle_instruct_common_settle(constant.Behavior.BACK_STAND_URETHRAL_SEX, judge=_("U性交"))

@add_instruct(constant.Instruct.FACE_HUG_URETHRAL_SEX)
def handle_face_hug_urethral_sex():
    """处理对面抱位尿道姦指令"""
    chara_handle_instruct_common_settle(constant.Behavior.FACE_HUG_URETHRAL_SEX, judge=_("U性交"))

@add_instruct(constant.Instruct.BACK_HUG_URETHRAL_SEX)
def handle_back_hug_urethral_sex():
    """处理背面抱位尿道姦指令"""
    chara_handle_instruct_common_settle(constant.Behavior.BACK_HUG_URETHRAL_SEX, judge=_("U性交"))

@add_instruct(constant.Instruct.FACE_LAY_URETHRAL_SEX)
def handle_face_lay_urethral_sex():
    """处理对面卧位尿道姦指令"""
    chara_handle_instruct_common_settle(constant.Behavior.FACE_LAY_URETHRAL_SEX, judge=_("U性交"))

@add_instruct(constant.Instruct.BACK_LAY_URETHRAL_SEX)
def handle_back_lay_urethral_sex():
    """处理背面卧位尿道姦指令"""
    chara_handle_instruct_common_settle(constant.Behavior.BACK_LAY_URETHRAL_SEX, judge=_("U性交"))

@add_instruct(constant.Instruct.BEAT_BREAST)
def handle_beat_breast():
    """处理打胸部指令"""
    instuct_judege.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)


@add_instruct(constant.Instruct.SPANKING)
def handle_spanking():
    """处理打屁股指令"""
    chara_handle_instruct_common_settle(constant.Behavior.SPANKING)


@add_instruct(constant.Instruct.SHAME_PLAY)
def handle_shame_play():
    """处理羞耻play指令"""
    instuct_judege.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)


@add_instruct(constant.Instruct.TAKE_SHOWER_H)
def handle_take_shower_h():
    """处理淋浴指令"""
    instuct_judege.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)


@add_instruct(constant.Instruct.BUBBLE_BATH)
def handle_bubble_bath():
    """处理泡泡浴指令"""
    instuct_judege.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)


@add_instruct(constant.Instruct.GIVE_BLOWJOB)
def handle_give_blowjob():
    """处理给对方口交指令"""
    instuct_judege.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)


@add_instruct(constant.Instruct.CHANGE_TOP_AND_BOTTOM)
def handle_change_top_and_bottom():
    """处理交给对方指令"""
    character_data: game_type.Character = cache.character_data[0]
    target_character_data: game_type.Character = cache.character_data[character_data.target_character_id]
    target_character_data.h_state.npc_active_h = True
    handle_npc_ai_in_h.npc_active_h()


@add_instruct(constant.Instruct.KEEP_ENJOY)
def handle_keep_enjoy():
    """处理继续享受指令"""
    handle_npc_ai_in_h.npc_active_h()


@add_instruct(constant.Instruct.TRY_PL_ACTIVE_H)
def handle_try_pl_active_h():
    """处理尝试掌握主动权指令"""
    character_data: game_type.Character = cache.character_data[0]
    target_character_data: game_type.Character = cache.character_data[character_data.target_character_id]
    target_character_data.h_state.npc_active_h = False

@add_instruct(constant.Instruct.UNDRESS)
def handle_undress():
    """处理脱衣服指令"""
    cache.now_panel_id = constant.Panel.UNDRESS

@add_instruct(constant.Instruct.ORGASM_EDGE_ON)
def handle_orgasm_edge_on():
    """处理绝顶寸止指令"""
    chara_handle_instruct_common_settle(constant.Behavior.ORGASM_EDGE_ON)

@add_instruct(constant.Instruct.ORGASM_EDGE_OFF)
def handle_orgasm_edge_off():
    """处理绝顶解放指令"""
    chara_handle_instruct_common_settle(constant.Behavior.ORGASM_EDGE_OFF)

@add_instruct(constant.Instruct.RUN_GROUP_SEX_TEMPLE)
def handle_run_group_sex_temple():
    """处理进行一次当前群交指令"""
    chara_handle_instruct_common_settle(constant.Behavior.WAIT, duration=10)

@add_instruct(constant.Instruct.RUN_ALL_GROUP_SEX_TEMPLE)
def handle_run_all_group_sex_temple():
    """处理进行一次轮流群交指令"""
    chara_handle_instruct_common_settle(constant.Behavior.WAIT, duration=10)

@add_instruct(constant.Instruct.EDIT_GROUP_SEX_TEMPLE)
def handle_edit_group_sex_temple():
    """处理编辑群交行动指令"""
    from Script.System.Sex_System import group_sex_panel
    now_panel = group_sex_panel.Edit_Group_Sex_Temple_Panel(width)
    now_panel.draw()


@add_instruct(constant.Instruct.SWITCH_TO_NON_H_INTERFACE)
def handle_switch_to_non_h_interface():
    """处理切换到非H指令"""
    cache.show_non_h_in_hidden_sex = True

@add_instruct(constant.Instruct.PULL_OUT_PENIS)
def handle_pull_out_penis():
    """处理拔出阴茎指令"""
    chara_handle_instruct_common_settle(constant.Behavior.PULL_OUT_PENIS)
