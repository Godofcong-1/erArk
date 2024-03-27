import random
import time
import queue
from functools import wraps
from typing import Set, List
from types import FunctionType
from threading import Thread
from Script.Core import constant, constant_promise, cache_control, game_type, get_text, save_handle, flow_handle
from Script.Design import update, character, attr_calculation, character_handle, map_handle, handle_premise
from Script.UI.Panel import manage_assembly_line_panel, normal_panel, see_character_info_panel, see_save_info_panel, resource_exchange_panel, navigation_panel, ability_up_panel, agriculture_production_panel
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


def handle_instruct(instruct: int):
    """
    处理执行指令
    Keyword arguments:
    instruct -- 指令id
    """
    instruct_queue.put(instruct)
    if instruct in constant.instruct_premise_data:
        constant.handle_instruct_data[instruct]()


def add_instruct(instruct_id: int, instruct_type: int, name: str, premise_set: Set):
    """
    添加指令处理
    Keyword arguments:
    instruct_id -- 指令id
    instruct_type -- 指令类型
    name -- 指令绘制文本
    premise_set -- 指令所需前提集合
    """

    def decorator(func: FunctionType):
        @wraps(func)
        def return_wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        constant.handle_instruct_data[instruct_id] = return_wrapper
        constant.instruct_premise_data[instruct_id] = premise_set
        constant.instruct_type_data.setdefault(instruct_type, set())
        constant.instruct_type_data[instruct_type].add(instruct_id)
        constant.handle_instruct_name_data[instruct_id] = name
        return return_wrapper

    return decorator


def instruct_filter_H_change(on_off_flag: bool):
    """
    指令类型过滤器进出H变更
    Keyword arguments:
    on_off_flag -- true:进入H false:退出H
    """
    if on_off_flag:
        cache.instruct_type_filter_cache = cache.instruct_type_filter.copy()
        # 自动开启性爱面板并关闭其他面板
        cache.instruct_type_filter[6] = 1
        for i in {1, 2, 3, 4, 5}:
            cache.instruct_type_filter[i] = 0

    else:
        cache.instruct_type_filter = cache.instruct_type_filter_cache.copy()


@add_instruct(constant.Instruct.REST, constant.InstructType.DAILY, _("休息"),
              {constant_promise.Premise.NOT_H,
               constant_promise.Premise.HP_OR_MP_GE_80,
               constant_promise.Premise.PLACE_FURNITURE_GE_1,
               constant_promise.Premise.TIRED_LE_84}
              )
def handle_rest():
    """处理休息指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 60
    character_data.behavior.behavior_id = constant.Behavior.REST
    character_data.state = constant.CharacterStatus.STATUS_REST
    update.game_update_flow(60)


@add_instruct(
    constant.Instruct.BUY_FOOD, constant.InstructType.DAILY, _("购买食物"),
    {constant_promise.Premise.IN_FOOD_SHOP,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.TIRED_LE_84}
)
def handle_buy_food():
    """处理购买食物指令"""
    cache.now_panel_id = constant.Panel.FOOD_SHOP


@add_instruct(
    constant.Instruct.EAT, constant.InstructType.DAILY, _("进食"),
    {constant_promise.Premise.HAVE_FOOD,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.TIRED_LE_84}
)
def handle_eat():
    """处理进食指令"""
    cache.now_panel_id = constant.Panel.FOOD_BAG


@add_instruct(
    constant.Instruct.MOVE, constant.InstructType.SYSTEM, _("移动"),
    {constant_promise.Premise.NOT_H}
)
def handle_move():
    """处理移动指令"""
    cache.now_panel_id = constant.Panel.SEE_MAP


@add_instruct(
    constant.Instruct.SEE_ATTR, constant.InstructType.SYSTEM, _("查看属性"), {}
)
def handle_see_attr():
    """查看属性"""
    see_character_info_panel.line_feed.draw()
    now_draw = see_character_info_panel.SeeCharacterInfoInScenePanel(
        cache.character_data[0].target_character_id, width
    )
    now_draw.draw()


@add_instruct(
    constant.Instruct.CHAT, constant.InstructType.DAILY, _("聊天"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.TIRED_LE_84,
     constant_promise.Premise.T_ACTION_NOT_SLEEP,
     constant_promise.Premise.T_NORMAL_6,}
)
def handle_chat():
    """处理聊天指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data = cache.character_data[0]
    character_data.behavior.duration = 5
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.action_info.talk_count > character_data.ability[40] + 1:
        character_data.behavior.behavior_id = constant.Behavior.CHAT_FAILED
        character_data.state = constant.CharacterStatus.STATUS_CHAT_FAILED
    else:
        character_data.behavior.behavior_id = constant.Behavior.CHAT
        character_data.state = constant.CharacterStatus.STATUS_CHAT
    target_data.action_info.talk_count += 1
    # print("聊天计数器+1，现在为 ：",target_data.action_info.talk_count)
    update.game_update_flow(5)


@add_instruct(
    constant.Instruct.BUY_H_ITEM, constant.InstructType.DAILY, _("购买成人用品"),
    {constant_promise.Premise.IN_H_SHOP,
     constant_promise.Premise.NOT_H, }
)
def handle_buy_h_item():
    """处理购买成人用品指令"""
    cache.now_panel_id = constant.Panel.H_ITEM_SHOP


@add_instruct(
    constant.Instruct.ITEM, constant.InstructType.SYSTEM, _("道具"),
    {}
)
def handle_item():
    """处理道具指令"""
    cache.now_panel_id = constant.Panel.ITEM


@add_instruct(constant.Instruct.SAVE, constant.InstructType.SYSTEM, _("读写存档"),
              {constant_promise.Premise.NOT_H})
def handle_save():
    """处理读写存档指令"""
    now_panel = see_save_info_panel.SeeSaveListPanel(width, 1)
    now_panel.draw()


@add_instruct(
    constant.Instruct.ABL_UP, constant.InstructType.SYSTEM, _("属性上升"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.NOT_H, }
)
def handle_abl_up():
    """处理属性上升"""
    see_character_info_panel.line_feed.draw()
    now_draw = ability_up_panel.Character_abi_up_main_Handle(
        cache.character_data[0].target_character_id, width
    )
    now_draw.draw()


@add_instruct(
    constant.Instruct.OWNER_ABL_UP, constant.InstructType.SYSTEM, _("自身属性上升"),
    {constant_promise.Premise.NOT_H}
)
def handle_owner_abl_up():
    """处理自身属性上升"""
    see_character_info_panel.line_feed.draw()
    now_draw = ability_up_panel.Character_abi_up_main_Handle(
        0, width
    )
    now_draw.draw()


@add_instruct(constant.Instruct.SEE_DIRTY, constant.InstructType.SYSTEM, _("查看污浊情况"),
              {constant_promise.Premise.HAVE_TARGET})
def see_dirty():
    """处理查看污浊情况指令"""
    cache.now_panel_id = constant.Panel.DIRTY


@add_instruct(constant.Instruct.INSTRUCT_FILTER, constant.InstructType.SYSTEM, _("指令过滤"), {})
def instruct_filter():
    """处理指令过滤指令"""
    cache.now_panel_id = constant.Panel.INSTRUCT_FILTER


@add_instruct(constant.Instruct.DEBUG_MODE_ON, constant.InstructType.SYSTEM, _("开启DEBUG模式"),
              {constant_promise.Premise.DEBUG_MODE_SETTING_ON,
               constant_promise.Premise.DEBUG_MODE_OFF})
def debug_mode():
    """处理开启DEBUG模式指令"""
    cache.debug_mode = True


@add_instruct(constant.Instruct.DEBUG_MODE_OFF, constant.InstructType.SYSTEM, _("关闭DEBUG模式"),
              {constant_promise.Premise.DEBUG_MODE_SETTING_ON,
               constant_promise.Premise.DEBUG_MODE_ON
               })
def debug_mode_off():
    """处理关闭DEBUG模式指令"""
    cache.debug_mode = False


@add_instruct(constant.Instruct.DEBUG_ADJUST, constant.InstructType.SYSTEM, _("debug数值调整"),
              {constant_promise.Premise.DEBUG_MODE_ON})
def debug_adjust():
    """处理debug数值调整指令"""
    cache.now_panel_id = constant.Panel.DEBUG_ADJUST


@add_instruct(
    constant.Instruct.SYSTEM_SETTING,
    constant.InstructType.SYSTEM,
    _("系统设置"),
    {
    })
def handle_system_setting():
    """系统设置"""
    cache.now_panel_id = constant.Panel.SYSTEM_SETTING


@add_instruct(
    constant.Instruct.COLLECTION_NOW_PLACE,
    constant.InstructType.SYSTEM,
    _("收藏该地点"),
    {
        constant_promise.Premise.PLACE_NOT_IN_COLLECTION_LIST,
    })
def handle_collection_now_place():
    """收藏该地点"""
    pl_character_data: game_type.Character = cache.character_data[0]
    cache.collect_position_list.append(pl_character_data.position)


@add_instruct(
    constant.Instruct.CANCEL_COLLECTION_NOW_PLACE,
    constant.InstructType.SYSTEM,
    _("取消收藏地点"),
    {
        constant_promise.Premise.PALCE_IN_COLLECTION_LIST,
    })
def handle_cancel_collection_now_place():
    """取消收藏地点"""
    pl_character_data: game_type.Character = cache.character_data[0]
    cache.collect_position_list.remove(pl_character_data.position)


@add_instruct(
    constant.Instruct.SEE_COLLECTION,
    constant.InstructType.WORK,
    _("查看收藏品"),
    {
        constant_promise.Premise.IN_COLLECTION_ROOM
    })
def handle_see_collection():
    """处理查看收藏品指令"""
    cache.now_panel_id = constant.Panel.COLLECTION


@add_instruct(
    constant.Instruct.SEE_FRIDGE,
    constant.InstructType.WORK,
    _("查看冰箱"),
    {
        constant_promise.Premise.IN_KITCHEN
    })
def handle_see_fridge():
    """处理查看冰箱指令"""
    cache.now_panel_id = constant.Panel.FRIDGE


@add_instruct(
    constant.Instruct.TEACH,
    constant.InstructType.WORK,
    _("授课"),
    {constant_promise.Premise.STUDENT_NOT_STUDY_IN_CLASSROOM,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.IN_CLASS_ROOM,
     constant_promise.Premise.TIRED_LE_74}
)
def handle_teach():
    """处理授课指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
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


@add_instruct(
    constant.Instruct.BORROW_BOOK,
    constant.InstructType.PLAY,
    _("借阅书籍"),
    {
        constant_promise.Premise.IN_LIBRARY,
        constant_promise.Premise.NOT_H,
        constant_promise.Premise.TIRED_LE_84,
    })
def handle_borrow_book():
    """处理借阅书籍指令"""
    cache.now_panel_id = constant.Panel.BORROW_BOOK


@add_instruct(
    constant.Instruct.READ_BOOK,
    constant.InstructType.PLAY,
    _("读书"),
    {
        constant_promise.Premise.NOT_H,
        constant_promise.Premise.TIRED_LE_74,
        constant_promise.Premise.PLACE_FURNITURE_GE_2,
    })
def handle_read_book():
    """处理读书指令"""
    now_draw = normal_panel.Read_Book_Panel(width)
    now_draw.draw()


@add_instruct(
    constant.Instruct.MANAGE_LIBRARY,
    constant.InstructType.WORK,
    _("管理图书馆"),
    {
        constant_promise.Premise.NOT_H,
        constant_promise.Premise.TIRED_LE_84,
        constant_promise.Premise.IN_LIBRARY_OR_LIBRARY_OFFICE,
        constant_promise.Premise.T_WORK_IS_LIBRARY_MANAGER,
        constant_promise.Premise.T_NORMAL_24567,
    })
def handle_manage_library():
    """处理管理图书馆指令"""
    cache.now_panel_id = constant.Panel.MANAGE_LIBRARY


@add_instruct(
    constant.Instruct.MANAGE_ASSEMBLY_LINE,
    constant.InstructType.WORK,
    _("管理流水线"),
    {
        constant_promise.Premise.NOT_H,
        constant_promise.Premise.TIRED_LE_84,
        constant_promise.Premise.IN_PRODUCTION_WORKSHOP,
    })
def handle_manage_library():
    """处理管理流水线指令"""
    now_draw = manage_assembly_line_panel.Manage_Assembly_Line_Panel(width)
    now_draw.draw()


@add_instruct(
    constant.Instruct.MANAGE_AGRICULTURE,
    constant.InstructType.WORK,
    _("管理农业生产"),
    {
        constant_promise.Premise.NOT_H,
        constant_promise.Premise.TIRED_LE_84,
        constant_promise.Premise.IN_HERB_GARDEN,
    })
def handle_manage_agriculture():
    """处理管理农业生产指令"""
    now_draw = agriculture_production_panel.Agriculture_Production_Panel(width)
    now_draw.draw()


@add_instruct(
    constant.Instruct.RESOURCE_EXCHANGE,
    constant.InstructType.WORK,
    _("资源交易"),
    {
        constant_promise.Premise.NOT_H,
        constant_promise.Premise.TIRED_LE_84,
        constant_promise.Premise.IN_RESOURCE_EXCHANGE,
    })
def handle_manage_library():
    """处理资源交易指令"""
    now_draw = resource_exchange_panel.Resource_Exchange_Line_Panel(width)
    now_draw.draw()


@add_instruct(
    constant.Instruct.NAVIGATION,
    constant.InstructType.WORK,
    _("导航"),
    {
        constant_promise.Premise.NOT_H,
        constant_promise.Premise.IN_COMMAND_ROOM,
    })
def handle_navigation():
    """处理导航指令"""
    now_draw = navigation_panel.Navigation_Panel(width)
    now_draw.draw()


@add_instruct(
    constant.Instruct.MANAGE_BASEMENT,
    constant.InstructType.WORK,
    _("管理罗德岛"),
    {
        constant_promise.Premise.NOT_H,
        constant_promise.Premise.IN_DR_OFFICE
    })
def handle_manage_basement():
    """处理管理罗德岛指令"""
    cache.now_panel_id = constant.Panel.MANAGE_BASEMENT


# 以下为源石技艺#

@add_instruct(
    constant.Instruct.HYPNOSIS_ONE,
    constant.InstructType.ARTS,
    _("单人催眠"),
    {constant_promise.Premise.PRIMARY_HYPNOSIS,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.SCENE_ONLY_TWO,
     constant_promise.Premise.TARGET_NOT_IN_HYPNOSIS,
     constant_promise.Premise.T_NORMAL_5_6,
     constant_promise.Premise.SANITY_POINT_GE_5,
     constant_promise.Premise.TIRED_LE_84}
)
def handle_hypnosis_one():
    """处理单人催眠"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.HYPNOSIS_ONE
    character_data.state = constant.CharacterStatus.STATUS_HYPNOSIS_ONE
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.HYPNOSIS_ALL,
    constant.InstructType.ARTS,
    _("集体催眠"),
    {constant_promise.Premise.ADVANCED_HYPNOSIS,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.SCENE_OVER_TWO,
     constant_promise.Premise.TARGET_NOT_IN_HYPNOSIS,
     constant_promise.Premise.T_NORMAL_5_6,
     constant_promise.Premise.SANITY_POINT_GE_5,
     constant_promise.Premise.TIRED_LE_84}
)
def handle_hypnosis_all():
    """处理集体催眠"""
    character.init_character_behavior_start_time(0, cache.game_time)
    now_draw = normal_panel.Close_Door_Panel(width)
    now_draw.draw()
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.HYPNOSIS_ALL
    character_data.state = constant.CharacterStatus.STATUS_HYPNOSIS_ALL
    character_data.behavior.duration = 30
    update.game_update_flow(30)


@add_instruct(
    constant.Instruct.HYPNOSIS_CANCEL,
    constant.InstructType.ARTS,
    _("解除催眠"),
    {constant_promise.Premise.PRIMARY_HYPNOSIS,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.SCENE_ONLY_TWO,
     constant_promise.Premise.TARGET_IN_HYPNOSIS,
     constant_promise.Premise.SANITY_POINT_GE_5,
     constant_promise.Premise.TIRED_LE_84}
)
def handle_hypnosis_cancel():
    """处理解除催眠"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.HYPNOSIS_CANCEL
    character_data.state = constant.CharacterStatus.STATUS_HYPNOSIS_CANCEL
    character_data.behavior.duration = 5
    update.game_update_flow(5)


@add_instruct(
    constant.Instruct.PENETRATING_VISION_ON,
    constant.InstructType.ARTS,
    _("开启透视"),
    {constant_promise.Premise.PRIMARY_PENETRATING_VISION,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.PENETRATING_VISION_OFF,
     constant_promise.Premise.SANITY_POINT_GE_5,
     constant_promise.Premise.TIRED_LE_84}
)
def handle_penetrating_vision_on():
    """处理开启透视"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.PENETRATING_VISION_ON
    character_data.state = constant.CharacterStatus.STATUS_PENETRATING_VISION_ON
    character_data.behavior.duration = 5
    update.game_update_flow(5)


@add_instruct(
    constant.Instruct.PENETRATING_VISION_OFF,
    constant.InstructType.ARTS,
    _("关闭透视"),
    {constant_promise.Premise.PRIMARY_PENETRATING_VISION,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.PENETRATING_VISION_ON,
     constant_promise.Premise.TIRED_LE_84}
)
def handle_penetrating_vision_off():
    """处理关闭透视"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.PENETRATING_VISION_OFF
    character_data.state = constant.CharacterStatus.STATUS_PENETRATING_VISION_OFF
    character_data.behavior.duration = 5
    update.game_update_flow(5)


@add_instruct(
    constant.Instruct.HORMONE_ON,
    constant.InstructType.ARTS,
    _("开启信息素"),
    {constant_promise.Premise.PRIMARY_HORMONE,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.HORMONE_OFF,
     constant_promise.Premise.TIRED_LE_84}
)
def handle_hormone_on():
    """处理开启信息素"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.HORMONE_ON
    character_data.state = constant.CharacterStatus.STATUS_HORMONE_ON
    character_data.behavior.duration = 5
    update.game_update_flow(5)


@add_instruct(
    constant.Instruct.HORMONE_OFF,
    constant.InstructType.ARTS,
    _("关闭信息素"),
    {constant_promise.Premise.PRIMARY_HORMONE,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.HORMONE_ON,
     constant_promise.Premise.TIRED_LE_84}
)
def handle_hormone_off():
    """处理关闭信息素"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.HORMONE_OFF
    character_data.state = constant.CharacterStatus.STATUS_HORMONE_OFF
    character_data.behavior.duration = 5
    update.game_update_flow(5)


@add_instruct(
    constant.Instruct.SLEEP, constant.InstructType.DAILY, _("睡觉"),
    {constant_promise.Premise.IN_DORMITORY,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.TIRED_GE_75_OR_SLEEP_TIME}
)
def handle_sleep():
    """处理睡觉指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    now_draw = normal_panel.Sleep_Panel(width)
    now_draw.draw()


@add_instruct(
    constant.Instruct.TAKE_SHOWER,
    constant.InstructType.DAILY,
    _("淋浴"),
    {constant_promise.Premise.IN_BATHROOM,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.TIRED_LE_84}
)
def handle_take_shower():
    """处理淋浴指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 15
    character_data.behavior.behavior_id = constant.Behavior.TAKE_SHOWER
    character_data.state = constant.CharacterStatus.STATUS_TAKE_SHOWER
    update.game_update_flow(15)


# @add_instruct(
#     constant.Instruct.DRINK_SPRING, constant.InstructType.DAILY, _("喝泉水"), {constant_promise.Premise.IN_FOUNTAIN}
# )
# def handle_drink_spring():
#     """处理喝泉水指令"""
#     value = random.randint(0, 100)
#     now_draw = draw.WaitDraw()
#     now_draw.width = width
#     now_draw.text = "\n"
#     character_data: game_type.Character = cache.character_data[0]
#     if value <= 5 and not character_data.sex:
#         now_draw.text += _("喝到了奇怪的泉水！身体变化了！！！")
#         character_data.sex = 1
#         character_data.height = attr_calculation.get_height(1, character_data.age)
#         bmi = attr_calculation.get_bmi(character_data.weight_tem)
#         character_data.weight = attr_calculation.get_weight(bmi, character_data.height.now_height)
#         character_data.bodyfat = attr_calculation.get_body_fat(
#             character_data.sex, character_data.bodyfat_tem
#         )
#         character_data.measurements = attr_calculation.get_measurements(
#             character_data.sex,
#             character_data.height.now_height,
#             character_data.weight,
#             character_data.bodyfat,
#             character_data.bodyfat_tem,
#         )
#     else:
#         now_draw.text += _("喝到了甜甜的泉水～")
#         character_data.status[28] = 0
#     now_draw.text += "\n"
#     now_draw.draw()


@add_instruct(
    constant.Instruct.STROKE,
    constant.InstructType.DAILY,
    _("身体接触"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.T_NORMAL_256_OR_UNCONSCIOUS_FLAG,
     constant_promise.Premise.TIRED_LE_84}
)
def handle_stroke():
    """处理身体接触指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 10
    character_data.behavior.behavior_id = constant.Behavior.STROKE
    character_data.state = constant.CharacterStatus.STATUS_STROKE
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.MASSAGE,
    constant.InstructType.DAILY,
    _("按摩"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.TECHNIQUE_GE_3,
     constant_promise.Premise.T_NORMAL_256_OR_UNCONSCIOUS_FLAG,
     constant_promise.Premise.TIRED_LE_84}
)
def handle_massage():
    """处理按摩指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 30
    character_data.behavior.behavior_id = constant.Behavior.MASSAGE
    character_data.state = constant.CharacterStatus.STATUS_MASSAGE
    update.game_update_flow(30)


# @add_instruct(
#     constant.Instruct.COLLECTION_CHARACTER,
#     constant.InstructType.SYSTEM,
#     _("收藏角色"),
#     {constant_promise.Premise.TARGET_IS_NOT_COLLECTION, constant_promise.Premise.TARGET_NO_PLAYER},
# )
# def handle_collection_character():
#     """处理收藏角色指令"""
#     character_data: game_type.Character = cache.character_data[0]
#     target_character_id = character_data.target_character_id
#     if target_character_id not in character_data.collection_character:
#         character_data.collection_character.add(target_character_id)


# @add_instruct(
#     constant.Instruct.UN_COLLECTION_CHARACTER,
#     constant.InstructType.SYSTEM,
#     _("取消收藏"),
#     {constant_promise.Premise.TARGET_IS_COLLECTION, constant_promise.Premise.TARGET_NO_PLAYER},
# )
# def handle_un_collection_character():
#     """处理取消指令"""
#     character_data: game_type.Character = cache.character_data[0]
#     target_character_id = character_data.target_character_id
#     if target_character_id in character_data.collection_character:
#         character_data.collection_character.remove(target_character_id)


# @add_instruct(
#     constant.Instruct.COLLECTION_SYSTEM,
#     constant.InstructType.SYSTEM,
#     _("启用收藏模式"),
#     {constant_promise.Premise.UN_COLLECTION_SYSTEM},
# )
# def handle_collection_system():
#     """处理启用收藏模式指令"""
#     cache.is_collection = 1
#     now_draw = draw.WaitDraw()
#     now_draw.width = width
#     now_draw.text = _("\n现在只会显示被收藏的角色的信息了！\n")
#     now_draw.draw()


# @add_instruct(
#     constant.Instruct.UN_COLLECTION_SYSTEM,
#     constant.InstructType.SYSTEM,
#     _("关闭收藏模式"),
#     {constant_promise.Premise.IS_COLLECTION_SYSTEM},
# )
# def handle_un_collection_system():
#     """处理关闭收藏模式指令"""
#     cache.is_collection = 0
#     now_draw = draw.WaitDraw()
#     now_draw.width = width
#     now_draw.text = _("\n现在会显示所有角色的信息了！\n")
#     now_draw.draw()


# @add_instruct(
#     constant.Instruct.VIEW_THE_SCHOOL_TIMETABLE,
#     constant.InstructType.STUDY,
#     _("查看课程表"),
#     {},
# )
# def handle_view_school_timetable():
#     """处理查看课程表指令"""
#     cache.now_panel_id = constant.Panel.VIEW_SCHOOL_TIMETABLE


# @add_instruct(
#     constant.Instruct.ATTEND_CLASS,
#     constant.InstructType.WORK,
#     _("上课"),
#     {
#         constant_promise.Premise.ATTEND_CLASS_TODAY,
#         constant_promise.Premise.IN_CLASSROOM,
#         constant_promise.Premise.IN_CLASS_TIME,
#         constant_promise.Premise.IS_STUDENT,
#     },
# )
# def handle_attend_class():
#     """处理上课指令"""
#     character.init_character_behavior_start_time(0, cache.game_time)
#     character_data: game_type.Character = cache.character_data[0]
#     end_time = 0
#     school_id, phase = course.get_character_school_phase(0)
#     now_time_value = cache.game_time.hour * 100 + cache.game_time.minute
#     now_course_index = 0
#     for session_id in game_config.config_school_session_data[school_id]:
#         session_config = game_config.config_school_session[session_id]
#         if session_config.start_time <= now_time_value and session_config.end_time >= now_time_value:
#             now_value = int(now_time_value / 100) * 60 + now_time_value % 100
#             end_value = int(session_config.end_time / 100) * 60 + session_config.end_time % 100
#             end_time = end_value - now_value + 1
#             now_course_index = session_config.session
#             break
#     now_week = cache.game_time.weekday()
#     if not now_course_index:
#         now_course = random.choice(list(game_config.config_school_phase_course_data[school_id][phase]))
#     else:
#         now_course = cache.course_time_table_data[school_id][phase][now_week][now_course_index]
#     character_data.behavior.duration = end_time
#     character_data.behavior.behavior_id = constant.Behavior.ATTEND_CLASS
#     character_data.state = constant.CharacterStatus.STATUS_ATTEND_CLASS
#     character_data.behavior.course_id = now_course
#     update.game_update_flow(end_time)


# @add_instruct(
#     constant.Instruct.TEACH_A_LESSON,
#     constant.InstructType.WORK,
#     _("教课"),
#     {
#         constant_promise.Premise.ATTEND_CLASS_TODAY,
#         constant_promise.Premise.IN_CLASSROOM,
#         constant_promise.Premise.IN_CLASS_TIME,
#         constant_promise.Premise.IS_TEACHER,
#     },
# )
# def handle_teach_a_lesson():
#     """处理教课指令"""
#     character.init_character_behavior_start_time(0, cache.game_time)
#     character_data: game_type.Character = cache.character_data[0]
#     end_time = 0
#     now_week = cache.game_time.weekday()
#     now_time_value = cache.game_time.hour * 100 + cache.game_time.minute
#     timetable_list: List[game_type.TeacherTimeTable] = cache.teacher_school_timetable[0]
#     course = 0
#     end_time = 0
#     for timetable in timetable_list:
#         if timetable.week_day != now_week:
#             continue
#         if timetable.time <= now_time_value and timetable.end_time <= now_time_value:
#             now_value = int(now_time_value / 100) * 60 + now_time_value % 100
#             end_value = int(timetable.end_time / 100) * 60 + timetable.end_time % 100
#             end_time = end_value - now_value + 1
#             course = timetable.course
#             break
#     character_data.behavior.duration = end_time
#     character_data.behavior.behavior_id = constant.Behavior.TEACHING
#     character_data.state = constant.CharacterStatus.STATUS_TEACHING
#     character_data.behavior.course_id = course
#     update.game_update_flow(end_time)


# @add_instruct(
#     constant.Instruct.PLAY_GUITAR,
#     constant.InstructType.PLAY,
#     _("弹吉他"),
#     {constant_promise.Premise.HAVE_GUITAR},
# )
# def handle_play_guitar():
#     """处理弹吉他指令"""
#     character.init_character_behavior_start_time(0, cache.game_time)
#     character_data = cache.character_data[0]
#     character_data.behavior.duration = 10
#     character_data.behavior.behavior_id = constant.Behavior.PLAY_GUITAR
#     character_data.state = constant.CharacterStatus.STATUS_PLAY_GUITAR
#     update.game_update_flow(10)


# @add_instruct(
#     constant.Instruct.SELF_STUDY,
#     constant.InstructType.WORK,
#     _("自习"),
#     {
#         constant_promise.Premise.IN_CLASSROOM,
#         constant_promise.Premise.IS_STUDENT,
#     },
# )
# def handle_self_study():
#     """处理自习指令"""
#     character.init_character_behavior_start_time(0, cache.game_time)
#     character_data: game_type.Character = cache.character_data[0]
#     school_id, phase = course.get_character_school_phase(0)
#     now_course_list = list(game_config.config_school_phase_course_data[school_id][phase])
#     now_course = random.choice(now_course_list)
#     character_data.behavior.behavior_id = constant.Behavior.SELF_STUDY
#     character_data.behavior.duration = 10
#     character_data.state = constant.CharacterStatus.STATUS_SELF_STUDY
#     character_data.behavior.course_id = now_course
#     update.game_update_flow(10)


@add_instruct(
    constant.Instruct.WAIT,
    constant.InstructType.DAILY,
    _("等待五分钟"),
    {constant_promise.Premise.NOT_H},
)
def handle_wait():
    """处理等待五分钟指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.WAIT
    character_data.state = constant.CharacterStatus.STATUS_WAIT
    character_data.behavior.duration = 5
    update.game_update_flow(5)


@add_instruct(
    constant.Instruct.WAIT_1_HOUR,
    constant.InstructType.DAILY,
    _("等待一个小时"),
    {constant_promise.Premise.DEBUG_MODE_ON},
)
def handle_wait_1_hour():
    """处理等待一个小时指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.WAIT
    character_data.state = constant.CharacterStatus.STATUS_WAIT
    character_data.behavior.duration = 60
    cache.wframe_mouse.w_frame_skip_wait_mouse = 1
    update.game_update_flow(60)


@add_instruct(
    constant.Instruct.WAIT_6_HOUR,
    constant.InstructType.DAILY,
    _("等待六个小时"),
    {constant_promise.Premise.DEBUG_MODE_ON},
)
def handle_wait_6_hour():
    """处理等待六个小时指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.WAIT
    character_data.state = constant.CharacterStatus.STATUS_WAIT
    character_data.behavior.duration = 360
    cache.wframe_mouse.w_frame_skip_wait_mouse = 1
    update.game_update_flow(360)


@add_instruct(
    constant.Instruct.MAKE_COFFEE,
    constant.InstructType.DAILY,
    _("泡咖啡"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.PLACE_FURNITURE_GE_2,
     constant_promise.Premise.TIRED_LE_84,
     constant_promise.Premise.TARGET_URINATE_LE_49,
     constant_promise.Premise.T_NORMAL_24567,}
)
def handle_make_coffee():
    """处理泡咖啡指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 15
    character_data.behavior.behavior_id = constant.Behavior.MAKE_COFFEE
    character_data.state = constant.CharacterStatus.STATUS_MAKE_COFFEE
    update.game_update_flow(15)


@add_instruct(
    constant.Instruct.MAKE_COFFEE_ADD,
    constant.InstructType.OBSCENITY,
    _("泡咖啡（加料）"),
    {constant_promise.Premise.NOT_H,
     constant_promise.Premise.PLACE_FURNITURE_GE_2,
     constant_promise.Premise.SCENE_ONLY_ONE,
     constant_promise.Premise.TIRED_LE_84}
)
def handle_make_coffee_add():
    """处理泡咖啡（加料）指令"""
    from Script.UI.Panel import make_food_panel
    now_draw = make_food_panel.Make_food_Panel(width,make_food_type=1)
    now_draw.draw()


@add_instruct(
    constant.Instruct.ASK_MAKE_COFFEE,
    constant.InstructType.DAILY,
    _("让对方泡咖啡"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.PLACE_FURNITURE_GE_2,
     constant_promise.Premise.TIRED_LE_84,
     constant_promise.Premise.URINATE_LE_49,
     constant_promise.Premise.T_NORMAL_24567,}
)
def handle_ask_make_coffee():
    """处理让对方泡咖啡指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.ASK_MAKE_COFFEE
    character_data.state = constant.CharacterStatus.STATUS_ASK_MAKE_COFFEE
    character_data.behavior.duration = 15
    update.game_update_flow(15)


@add_instruct(
    constant.Instruct.MAKE_FOOD,
    constant.InstructType.DAILY,
    _("做饭"),
    {constant_promise.Premise.IN_KITCHEN,
     },
)
def handle_make_food():
    """做饭"""
    cache.now_panel_id = constant.Panel.MAKE_FOOD


@add_instruct(constant.Instruct.ALL_NPC_POSITION, constant.InstructType.DAILY, _("干员位置一览"),
              {
                  constant_promise.Premise.NOT_H,
              })
def handle_all_npc_position():
    """处理干员位置一览指令"""
    cache.now_panel_id = constant.Panel.ALL_NPC_POSITION


@add_instruct(
    constant.Instruct.FOLLOW,
    constant.InstructType.DAILY,
    _("邀请同行"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.T_NORMAL_2467,
     constant_promise.Premise.TARGET_NOT_FOLLOW},
)
def handle_followed():
    """处理邀请同行指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    character_data.behavior.behavior_id = constant.Behavior.FOLLOW
    character_data.state = constant.CharacterStatus.STATUS_FOLLOW
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    target_data.sp_flag.is_follow = 1
    # print("进入同行模式")
    # print("跟随指令交互目标的NPC编号为：",character_data.target_character_id)
    update.game_update_flow(5)

    now_draw = draw.NormalDraw()
    now_draw.text = f"\n{target_data.name}进入智能跟随模式\n"

    # 去掉其他NPC的跟随
    if not cache.debug_mode:
        for npc_id in cache.npc_id_got:
            if npc_id not in {0, character_data.target_character_id, character_data.assistant_character_id}:
                other_character_data = cache.character_data[npc_id]
                if other_character_data.sp_flag.is_follow:
                    other_character_data.sp_flag.is_follow = 0
                    now_draw.text += f"当前最大跟随数量：1人（助理除外），{other_character_data.name}退出跟随模式\n"
    now_draw.width = 1
    now_draw.draw()


@add_instruct(
    constant.Instruct.END_FOLLOW,
    constant.InstructType.DAILY,
    _("结束同行"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.T_NORMAL_2467,
     constant_promise.Premise.TARGET_IS_FOLLOW},
)
def handle_end_followed():
    """处理结束同行指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 1
    character_data.behavior.behavior_id = constant.Behavior.END_FOLLOW
    character_data.state = constant.CharacterStatus.STATUS_END_FOLLOW
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    target_data.sp_flag.is_follow = 0
    update.game_update_flow(1)


@add_instruct(
    constant.Instruct.APOLOGIZE,
    constant.InstructType.DAILY,
    _("道歉"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.TARGET_ANGRY_WITH_PLAYER,
     constant_promise.Premise.T_NORMAL_24567,
     constant_promise.Premise.TIRED_LE_74},
)
def handle_apologize():
    """处理道歉指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    # 根据口才获取调整值#
    character_data.ability.setdefault(25, 0)
    adjust = attr_calculation.get_ability_adjust(character_data.ability[40])
    value = 10 + adjust * 10
    # 减愤怒值
    target_data.angry_point -= value
    # 判定是否不生气了
    if target_data.angry_point <= 30:
        character_data.behavior.behavior_id = constant.Behavior.APOLOGIZE
        character_data.state = constant.CharacterStatus.STATUS_APOLOGIZE
        target_data.sp_flag.angry_with_player = False
    else:
        character_data.behavior.behavior_id = constant.Behavior.APOLOGIZE_FAILED
        character_data.state = constant.CharacterStatus.STATUS_APOLOGIZE_FAILED
    character_data.behavior.duration = 60
    update.game_update_flow(60)


@add_instruct(
    constant.Instruct.LISTEN_COMPLAINT,
    constant.InstructType.DAILY,
    _("听牢骚"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.TARGET_ABD_OR_ANGRY_MOOD,
     constant_promise.Premise.TARGET_NOT_ANGRY_WITH_PLAYER,
     constant_promise.Premise.T_NORMAL_24567,
     constant_promise.Premise.TIRED_LE_84, },
)
def handle_listen_complaint():
    """处理听牢骚指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    # 根据口才获取调整值#
    character_data.ability.setdefault(25, 0)
    adjust = attr_calculation.get_ability_adjust(character_data.ability[40])
    value = 10 + adjust * 10
    # 减愤怒值
    target_data.angry_point -= value
    character_data.behavior.behavior_id = constant.Behavior.LISTEN_COMPLAINT
    character_data.state = constant.CharacterStatus.STATUS_LISTEN_COMPLAINT
    character_data.behavior.duration = 45
    update.game_update_flow(45)


@add_instruct(
    constant.Instruct.ORIGINIUM_ARTS,
    constant.InstructType.SYSTEM,
    _("源石技艺"),
    {constant_promise.Premise.TIRED_LE_84,
     constant_promise.Premise.NOT_H},
)
def handle_originium_arts():
    """处理源石技艺指令"""
    cache.now_panel_id = constant.Panel.ORIGINIUM_ARTS


@add_instruct(
    constant.Instruct.LISTEN_INFLATION,
    constant.InstructType.DAILY,
    _("听肚子里的动静"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.NOT_IN_TOILET,
     constant_promise.Premise.T_INFLATION_1,
     constant_promise.Premise.TIRED_LE_84}
)
def handle_listen_inflation():
    """处理听肚子里的动静指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.LISTEN_INFLATION
    character_data.state = constant.CharacterStatus.STATUS_LISTEN_INFLATION
    character_data.behavior.duration = 5
    update.game_update_flow(5)


@add_instruct(
    constant.Instruct.PLAY_WITH_CHILD,
    constant.InstructType.DAILY,
    _("一起玩耍"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.NOT_IN_TOILET,
     constant_promise.Premise.T_CHILD_OR_LOLI_1,
     constant_promise.Premise.TIRED_LE_84}
)
def handle_play_with_child():
    """处理一起玩耍指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.PLAY_WITH_CHILD
    character_data.state = constant.CharacterStatus.STATUS_PLAY_WITH_CHILD
    character_data.behavior.duration = 30
    update.game_update_flow(30)


@add_instruct(
    constant.Instruct.TAKE_CARE_BABY,
    constant.InstructType.DAILY,
    _("照顾婴儿"),
    {constant_promise.Premise.NOT_H,
     constant_promise.Premise.IN_NURSERY,
     constant_promise.Premise.FLAG_BABY_EXIST,
     constant_promise.Premise.TIRED_LE_84},
)
def handle_take_care_baby():
    """处理照顾婴儿指令"""
    now_draw = normal_panel.Take_Care_Baby_Panel(width)
    now_draw.draw()


@add_instruct(
    constant.Instruct.LISTEN_MISSION,
    constant.InstructType.WORK,
    _("听取委托_未实装"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.TO_DO},
)
def handle_listen_mission():
    """处理听取委托指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)


@add_instruct(
    constant.Instruct.CHECK_LOCKER,
    constant.InstructType.OBSCENITY,
    _("检查衣柜"),
    {constant_promise.Premise.NOT_H,
     constant_promise.Premise.IN_LOCKER_ROOM_OR_DORMITORY,
     constant_promise.Premise.TIRED_LE_84},
)
def handle_check_locker():
    """处理检查衣柜指令"""
    cache.now_panel_id = constant.Panel.CHECK_LOCKER


@add_instruct(
    constant.Instruct.COLLCET_PANTY,
    constant.InstructType.DAILY,
    _("收起内裤_未实装"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.TO_DO},
)
def handle_collect_panty():
    """处理收起内裤指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)


@add_instruct(
    constant.Instruct.ASK_DATE,
    constant.InstructType.DAILY,
    _("邀请约会_未实装"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.TO_DO},
)
def handle_ask_date():
    """处理邀请约会指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)


@add_instruct(
    constant.Instruct.CONFESSION,
    constant.InstructType.OBSCENITY,
    _("告白"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.TARGET_LOVE_2,
     constant_promise.Premise.HAVE_RING,
     constant_promise.Premise.TIRED_LE_74}
)
def handle_confession():
    """处理告白指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    target_data = cache.character_data[character_data.target_character_id]
    if character.calculation_instuct_judege(0, character_data.target_character_id, _("告白"))[0]:
        character_data.behavior.behavior_id = constant.Behavior.CONFESSION
        character_data.state = constant.CharacterStatus.STATUS_CONFESSION
        # 将对象的恋慕转为恋人，对方获得戒指
        target_data.talent[202] = 0
        target_data.talent[203] = 1
        target_data.talent[205] = 1
        target_data.talent[411] = 1
        character_data.pl_collection.token_list[character_data.target_character_id] = 1
        now_draw = draw.WaitDraw()
        now_draw.width = width
        now_draw.text = _(f"\n告白成功，{target_data.name}收下了你赠予的[戒指]，[恋慕]转为[恋人]\n")
        now_draw.text += _(f"\n获得了{target_data.name}的信物：{target_data.token_text}\n")
        now_draw.draw()
    else:
        character_data.behavior.behavior_id = constant.Behavior.CONFESSION_FAILED
        character_data.state = constant.CharacterStatus.STATUS_CONFESSION_FAILED
        now_draw = draw.WaitDraw()
        now_draw.width = width
        now_draw.text = _("\n告白失败，需要[恋慕]且满足实行值\n")
        now_draw.draw()
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.GIVE_NECKLACE,
    constant.InstructType.OBSCENITY,
    _("戴上项圈"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.TARGET_OBEY_2,
     constant_promise.Premise.HAVE_COLLAR,
     constant_promise.Premise.TIRED_LE_74}
)
def handle_give_necklace():
    """处理戴上项圈指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    target_data = cache.character_data[character_data.target_character_id]
    if character.calculation_instuct_judege(0, character_data.target_character_id, _("戴上项圈"))[0]:
        character_data.behavior.behavior_id = constant.Behavior.GIVE_NECKLACE
        character_data.state = constant.CharacterStatus.STATUS_GIVE_NECKLACE
        # 将对象的驯服转为宠物，增加项圈素质
        target_data.talent[211] = 0
        target_data.talent[212] = 1
        target_data.talent[215] = 1
        target_data.talent[411] = 1
        character_data.pl_collection.token_list[character_data.target_character_id] = 1
        now_draw = draw.WaitDraw()
        now_draw.width = width
        now_draw.text = _(f"\n{target_data.name}接受了项圈，戴在了自己的脖子上，[驯服]转为[宠物]\n")
        now_draw.text += _(f"\n获得了{target_data.name}的信物：{target_data.token_text}\n")
        now_draw.draw()
    else:
        character_data.behavior.behavior_id = constant.Behavior.GIVE_NECKLACE_FAILED
        character_data.state = constant.CharacterStatus.STATUS_GIVE_NECKLACE_FAILED
        now_draw = draw.WaitDraw()
        now_draw.width = width
        now_draw.text = _("\n戴上项圈失败，需要[驯服]且满足实行值\n")
        now_draw.draw()
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.DRINK_ALCOHOL,
    constant.InstructType.DAILY,
    _("劝酒_未实装"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.TO_DO},
)
def handle_drink_alcohol():
    """处理劝酒指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)


@add_instruct(
    constant.Instruct.PEE,
    constant.InstructType.DAILY,
    _("解手"),
    {constant_promise.Premise.IN_TOILET_MAN,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.URINATE_GE_80,
     constant_promise.Premise.TIRED_LE_84},
)
def handle_pee():
    """处理解手指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.PEE
    character_data.state = constant.CharacterStatus.STATUS_PEE
    character_data.behavior.duration = 5
    update.game_update_flow(5)


@add_instruct(
    constant.Instruct.COLLECT,
    constant.InstructType.DAILY,
    _("摆放藏品"),
    {constant_promise.Premise.IN_COLLECTION_ROOM,
     constant_promise.Premise.HAVE_COLLECTION,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.TIRED_LE_84},
)
def handle_collect():
    """处理摆放藏品指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]

    # 内裤
    if len(character_data.pl_collection.npc_panties_tem):
        for npc_id in character_data.pl_collection.npc_panties_tem:
            if npc_id == 0:
                continue
            for pan_id in character_data.pl_collection.npc_panties_tem[npc_id]:
                # 如果该内裤不存在，则跳过
                if pan_id not in game_config.config_clothing_tem:
                    continue
                pan_name = game_config.config_clothing_tem[pan_id].name
                now_draw = draw.WaitDraw()
                now_draw.width = width
                # 如果已经重复持有，则进行提示
                if pan_name in character_data.pl_collection.npc_panties[npc_id]:
                    now_draw.text = _(f"\n已持有藏品：{cache.character_data[npc_id].name}的{pan_name}")
                else:
                    character_data.pl_collection.npc_panties[npc_id].append(pan_name)
                    now_draw.text = _(f"\n增加了藏品：{cache.character_data[npc_id].name}的{pan_name}")
                now_draw.draw()
        # 最后清空
        character_data.pl_collection.npc_panties_tem.clear()

    # 袜子
    if len(character_data.pl_collection.npc_socks_tem):
        for npc_id in character_data.pl_collection.npc_socks_tem:
            if npc_id == 0:
                continue
            for socks_id in character_data.pl_collection.npc_socks_tem[npc_id]:
                # 如果该袜子不存在，则跳过
                if socks_id not in game_config.config_clothing_tem:
                    continue
                socks_name = game_config.config_clothing_tem[socks_id].name
                now_draw = draw.WaitDraw()
                now_draw.width = width
                # 如果已经重复持有，则进行提示
                if socks_name in character_data.pl_collection.npc_socks[npc_id]:
                    now_draw.text = _(f"\n已持有藏品：{cache.character_data[npc_id].name}的{socks_name}")
                else:
                    character_data.pl_collection.npc_socks[npc_id].append(socks_name)
                    now_draw.text = _(f"\n增加了藏品：{cache.character_data[npc_id].name}的{socks_name}")
                now_draw.draw()
        # 装完了之后清空
        character_data.pl_collection.npc_socks_tem.clear()

    character_data.behavior.duration = 5
    update.game_update_flow(5)


@add_instruct(
    constant.Instruct.DO_H,
    constant.InstructType.OBSCENITY,
    _("邀请H"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.T_NORMAL_5_6,
     constant_promise.Premise.TIRED_LE_74}
)
def handle_do_h():
    """处理邀请H指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    target_data = cache.character_data[character_data.target_character_id]
    h_flag = False
    if character.calculation_instuct_judege(0, character_data.target_character_id, _("H模式"))[0]:
        now_draw = normal_panel.Close_Door_Panel(width)
        # if now_draw.draw():
        now_draw.draw()
        h_flag = True
        target_data.sp_flag.is_h = 1
        target_data.sp_flag.is_follow = 0
        character_data.behavior.behavior_id = constant.Behavior.H
        character_data.state = constant.CharacterStatus.STATUS_H
        now_draw = draw.WaitDraw()
        now_draw.width = width
        now_draw.text = _("\n进入H模式\n")
        now_draw.draw()

        instruct_filter_H_change(True)

    else:
        character_data.behavior.behavior_id = constant.Behavior.DO_H_FAIL
        character_data.state = constant.CharacterStatus.STATUS_DO_H_FAIL
    character_data.behavior.duration = 5
    update.game_update_flow(5)

    if not h_flag:
        now_draw = draw.WaitDraw()
        now_draw.width = width
        now_draw.text = _("\n进入H模式失败\n")
        now_draw.draw()


@add_instruct(
    constant.Instruct.SLEEP_OBSCENITY,
    constant.InstructType.OBSCENITY,
    _("睡眠猥亵"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.T_UNNORMAL_5_6,
     constant_promise.Premise.T_UNCONSCIOUS_FLAG_0,
     constant_promise.Premise.TIRED_LE_74}
)
def handle_sleep_obscenity():
    """处理睡眠猥亵指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    target_data = cache.character_data[character_data.target_character_id]
    now_draw = normal_panel.Close_Door_Panel(width)
    now_draw.draw()
    target_data.sp_flag.unconscious_h = 1
    now_draw = draw.WaitDraw()
    now_draw.width = width
    now_draw.text = _("\n进入睡眠猥亵模式\n")
    now_draw.draw()


@add_instruct(
    constant.Instruct.STOP_SLEEP_OBSCENITY,
    constant.InstructType.OBSCENITY,
    _("停止睡眠猥亵"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.T_UNNORMAL_5_6,
     constant_promise.Premise.T_UNCONSCIOUS_FLAG_1,
     constant_promise.Premise.TIRED_LE_74}
)
def handle_stop_sleep_obscenity():
    """处理停止睡眠猥亵指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    target_data = cache.character_data[character_data.target_character_id]
    target_data.sp_flag.unconscious_h = 0
    now_draw = draw.WaitDraw()
    now_draw.width = width
    now_draw.text = _("\n退出睡眠猥亵模式\n")
    now_draw.draw()
    from Script.Settle import default
    import datetime
    default.handle_door_close_reset(0,1,game_type.CharacterStatusChange,datetime.datetime)


@add_instruct(
    constant.Instruct.UNCONSCIOUS_H,
    constant.InstructType.OBSCENITY,
    _("无意识奸"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.T_UNCONSCIOUS_FLAG,
     constant_promise.Premise.TIRED_LE_74}
)
def handle_unconscious_h():
    """处理无意识奸指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    target_data = cache.character_data[character_data.target_character_id]
    now_draw = normal_panel.Close_Door_Panel(width)
    # if now_draw.draw():
    now_draw.draw()
    target_data.sp_flag.is_h = 1
    target_data.sp_flag.is_follow = 0
    character_data.behavior.behavior_id = constant.Behavior.H
    character_data.state = constant.CharacterStatus.STATUS_H
    now_draw = draw.WaitDraw()
    now_draw.width = width
    now_draw.text = _("\n进入无意识奸模式\n")
    now_draw.draw()

    instruct_filter_H_change(True)
    character_data.behavior.duration = 5
    update.game_update_flow(5)


@add_instruct(
    constant.Instruct.END_H,
    constant.InstructType.SEX,
    _("H结束"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H},
)
def handle_end_h():
    """处理H结束指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    special_end_list = [constant.Behavior.H_INTERRUPT, constant.Behavior.H_HP_0, constant.Behavior.T_H_HP_0]
    if character_data.behavior.behavior_id not in special_end_list:
        character_data.behavior.behavior_id = constant.Behavior.END_H
        character_data.state = constant.CharacterStatus.STATUS_END_H

    instruct_filter_H_change(False)

    # H结束时的其他处理
    if target_data.sp_flag.is_h == 1:
        target_data.sp_flag.is_h = 0
        target_data.sp_flag.unconscious_h = 0
        # 如果是非监禁对象，则进入跟随，并原地待机十分钟
        if not target_data.sp_flag.imprisonment:
            target_data.sp_flag.is_follow = 1
            character.init_character_behavior_start_time(character_data.target_character_id, cache.game_time)
            target_data.behavior.behavior_id = constant.Behavior.WAIT
            target_data.behavior.duration = 10
            target_data.state = constant.CharacterStatus.STATUS_WAIT
            target_data: game_type.Character = cache.character_data[character_data.target_character_id]

    # H结束时的其他处理完毕
    now_draw = draw.WaitDraw()
    now_draw.width = width
    now_draw.text = _(f"\n结束H模式\n")
    now_draw.draw()
    character_data.behavior.duration = 5
    update.game_update_flow(5)


# 以下为娱乐#

@add_instruct(
    constant.Instruct.SINGING,
    constant.InstructType.PLAY,
    _("唱歌"),
    {
        constant_promise.Premise.NOT_H,
        constant_promise.Premise.TIRED_LE_74}
)
def handle_singing():
    """处理唱歌指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data = cache.character_data[0]
    # 如果音乐等级过低，且周围有其他角色，则进行需要确认再唱歌
    if character_data.ability[44] <= 2 and handle_premise.handle_scene_over_one(0):
        while 1:
            now_draw = draw.WaitDraw()
            now_draw.width = width
            now_draw.text = _("\n当前音乐能力小于等于2，可能会让对方感觉不适，确认要继续吗\n\n")
            now_draw.draw()
            return_list = []
            back_draw = draw.CenterButton(_("[取消]"), _("\n取消"), width / 3)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            yes_draw = draw.CenterButton(_("[确定]"), _("\n确定"), width / 3,)
            yes_draw.draw()
            return_list.append(yes_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                return
            elif yrn == yes_draw.return_text:
                break
    character_data.behavior.duration = 10
    character_data.behavior.behavior_id = constant.Behavior.SINGING
    character_data.state = constant.CharacterStatus.STATUS_SINGING
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.PLAY_INSTRUMENT,
    constant.InstructType.PLAY,
    _("演奏乐器"),
    {
        constant_promise.Premise.NOT_H,
        constant_promise.Premise.HAVE_INSTRUMENT,
        constant_promise.Premise.TIRED_LE_74}
)
def handle_play_instrument():
    """处理演奏乐器指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    # 如果音乐等级过低，且周围有其他角色，则进行需要确认再演奏
    if character_data.ability[44] <= 2 and handle_premise.handle_scene_over_one(0):
        while 1:
            now_draw = draw.WaitDraw()
            now_draw.width = width
            now_draw.text = _("\n当前音乐能力小于等于2，可能会让对方感觉不适，确认要继续吗\n\n")
            now_draw.draw()
            return_list = []
            back_draw = draw.CenterButton(_("[取消]"), _("\n取消"), width / 3)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            yes_draw = draw.CenterButton(_("[确定]"), _("\n确定"), width / 3,)
            yes_draw.draw()
            return_list.append(yes_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                return
            elif yrn == yes_draw.return_text:
                break
    character_data.behavior.duration = 10
    character_data.behavior.behavior_id = constant.Behavior.PLAY_INSTRUMENT
    character_data.state = constant.CharacterStatus.STATUS_PLAY_INSTRUMENT
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.WATCH_MOVIE,
    constant.InstructType.PLAY,
    _("看电影"),
    {
        constant_promise.Premise.NOT_H,
        constant_promise.Premise.IN_MULTIMEDIA_ROOM,
        constant_promise.Premise.TIRED_LE_74}
)
def handle_watch_movie():
    """处理看电影指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 120
    character_data.behavior.behavior_id = constant.Behavior.WATCH_MOVIE
    character_data.state = constant.CharacterStatus.STATUS_WATCH_MOVIE
    update.game_update_flow(120)

@add_instruct(
    constant.Instruct.PHOTOGRAPHY,
    constant.InstructType.PLAY,
    _("摄影"),
    {
        constant_promise.Premise.NOT_H,
        constant_promise.Premise.IN_PHOTOGRAPHY_STUDIO,
        constant_promise.Premise.TIRED_LE_74}
)
def handle_photography():
    """处理摄影指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 60
    character_data.behavior.behavior_id = constant.Behavior.PHOTOGRAPHY
    character_data.state = constant.CharacterStatus.STATUS_PHOTOGRAPHY
    update.game_update_flow(60)


@add_instruct(
    constant.Instruct.PLAY_WATER,
    constant.InstructType.PLAY,
    _("玩水"),
    {
        constant_promise.Premise.NOT_H,
        constant_promise.Premise.IN_AQUAPIT_EXPERIENTORIUM,
        constant_promise.Premise.TIRED_LE_74}
)
def handle_play_water():
    """处理玩水指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 60
    character_data.behavior.behavior_id = constant.Behavior.PLAY_WATER
    character_data.state = constant.CharacterStatus.STATUS_PLAY_WATER
    update.game_update_flow(60)


@add_instruct(
    constant.Instruct.PLAY_CHESS,
    constant.InstructType.PLAY,
    _("下棋"),
    {
        constant_promise.Premise.NOT_H,
        constant_promise.Premise.HAVE_TARGET,
        constant_promise.Premise.IN_BOARD_GAMES_ROOM,
        constant_promise.Premise.TIRED_LE_74}
)
def handle_play_chess():
    """处理下棋指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 30
    character_data.behavior.behavior_id = constant.Behavior.PLAY_CHESS
    character_data.state = constant.CharacterStatus.STATUS_PLAY_CHESS
    update.game_update_flow(30)


@add_instruct(
    constant.Instruct.PLAY_MAHJONG,
    constant.InstructType.PLAY,
    _("打麻将"),
    {
        constant_promise.Premise.NOT_H,
        constant_promise.Premise.HAVE_TARGET,
        constant_promise.Premise.IN_BOARD_GAMES_ROOM,
        constant_promise.Premise.TIRED_LE_74}
)
def handle_play_mahjong():
    """处理打麻将指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 60
    character_data.behavior.behavior_id = constant.Behavior.PLAY_MAHJONG
    character_data.state = constant.CharacterStatus.STATUS_PLAY_MAHJONG
    update.game_update_flow(60)


@add_instruct(
    constant.Instruct.PLAY_CARDS,
    constant.InstructType.PLAY,
    _("打牌"),
    {
        constant_promise.Premise.NOT_H,
        constant_promise.Premise.HAVE_TARGET,
        constant_promise.Premise.IN_BOARD_GAMES_ROOM,
        constant_promise.Premise.TIRED_LE_74}
)
def handle_play_cards():
    """处理打牌指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 60
    character_data.behavior.behavior_id = constant.Behavior.PLAY_CARDS
    character_data.state = constant.CharacterStatus.STATUS_PLAY_CARDS
    update.game_update_flow(60)


@add_instruct(
    constant.Instruct.REHEARSE_DANCE,
    constant.InstructType.PLAY,
    _("排演舞剧"),
    {
        constant_promise.Premise.NOT_H,
        constant_promise.Premise.IN_FAIRY_BANQUET,
        constant_promise.Premise.TIRED_LE_74}
)
def handle_rehearse_dance():
    """处理排演舞剧指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 120
    character_data.behavior.behavior_id = constant.Behavior.REHEARSE_DANCE
    character_data.state = constant.CharacterStatus.STATUS_REHEARSE_DANCE
    update.game_update_flow(120)


@add_instruct(
    constant.Instruct.PLAY_ARCADE_GAME,
    constant.InstructType.PLAY,
    _("玩街机游戏"),
    {
        constant_promise.Premise.NOT_H,
        constant_promise.Premise.IN_AVANT_GARDE_ARCADE,
        constant_promise.Premise.TIRED_LE_74}
)
def handle_play_arcade_game():
    """处理玩街机游戏指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 60
    character_data.behavior.behavior_id = constant.Behavior.PLAY_ARCADE_GAME
    character_data.state = constant.CharacterStatus.STATUS_PLAY_ARCADE_GAME
    update.game_update_flow(60)


@add_instruct(
    constant.Instruct.SWIMMING,
    constant.InstructType.PLAY,
    _("游泳"),
    {
        constant_promise.Premise.NOT_H,
        constant_promise.Premise.IN_SWIMMING_POOL,
        constant_promise.Premise.TIRED_LE_74}
)
def handle_swimming():
    """处理游泳指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 60
    character_data.behavior.behavior_id = constant.Behavior.SWIMMING
    character_data.state = constant.CharacterStatus.STATUS_SWIMMING
    update.game_update_flow(60)


@add_instruct(
    constant.Instruct.TASTE_WINE,
    constant.InstructType.PLAY,
    _("品酒"),
    {
        constant_promise.Premise.NOT_H,
        constant_promise.Premise.IN_BAR,
        constant_promise.Premise.TIRED_LE_74}
)
def handle_taste_wine():
    """处理品酒指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 30
    character_data.behavior.behavior_id = constant.Behavior.TASTE_WINE
    character_data.state = constant.CharacterStatus.STATUS_TASTE_WINE
    update.game_update_flow(30)


@add_instruct(
    constant.Instruct.TASTE_TEA,
    constant.InstructType.PLAY,
    _("品茶"),
    {
        constant_promise.Premise.NOT_H,
        constant_promise.Premise.IN_TEAHOUSE,
        constant_promise.Premise.TIRED_LE_74}
)
def handle_taste_tea():
    """处理品茶指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 30
    character_data.behavior.behavior_id = constant.Behavior.TASTE_TEA
    character_data.state = constant.CharacterStatus.STATUS_TASTE_TEA
    update.game_update_flow(30)


@add_instruct(
    constant.Instruct.TASTE_COFFEE,
    constant.InstructType.PLAY,
    _("品咖啡"),
    {
        constant_promise.Premise.NOT_H,
        constant_promise.Premise.IN_CAFÉ,
        constant_promise.Premise.TIRED_LE_74}
)
def handle_taste_coffee():
    """处理品咖啡指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 30
    character_data.behavior.behavior_id = constant.Behavior.TASTE_COFFEE
    character_data.state = constant.CharacterStatus.STATUS_TASTE_COFFEE
    update.game_update_flow(30)


@add_instruct(
    constant.Instruct.TASTE_DESSERT,
    constant.InstructType.PLAY,
    _("品尝点心"),
    {
        constant_promise.Premise.NOT_H,
        constant_promise.Premise.IN_WALYRIA_CAKE_SHOP,
        constant_promise.Premise.TIRED_LE_74}
)
def handle_taste_dessert():
    """处理品尝点心指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 30
    character_data.behavior.behavior_id = constant.Behavior.TASTE_DESSERT
    character_data.state = constant.CharacterStatus.STATUS_TASTE_DESSERT
    update.game_update_flow(30)


@add_instruct(
    constant.Instruct.TASTE_FOOD,
    constant.InstructType.PLAY,
    _("品尝美食"),
    {
        constant_promise.Premise.NOT_H,
        constant_promise.Premise.IN_RESTAURANT,
        constant_promise.Premise.EAT_TIME,
        constant_promise.Premise.HUNGER_GE_80,
        constant_promise.Premise.TIRED_LE_74}
)
def handle_taste_food():
    """处理品尝美食指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 30
    character_data.behavior.behavior_id = constant.Behavior.TASTE_FOOD
    character_data.state = constant.CharacterStatus.STATUS_TASTE_FOOD
    update.game_update_flow(30)


@add_instruct(
    constant.Instruct.PLAY_HOUSE,
    constant.InstructType.PLAY,
    _("过家家"),
    {
        constant_promise.Premise.NOT_H,
        constant_promise.Premise.IN_GOLDEN_GAME_ROOM,
        constant_promise.Premise.TIRED_LE_74}
)
def handle_play_house():
    """处理过家家指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 60
    character_data.behavior.behavior_id = constant.Behavior.PLAY_HOUSE
    character_data.state = constant.CharacterStatus.STATUS_PLAY_HOUSE
    update.game_update_flow(60)


@add_instruct(
    constant.Instruct.STYLE_HAIR,
    constant.InstructType.PLAY,
    _("修整发型"),
    {
        constant_promise.Premise.NOT_H,
        constant_promise.Premise.IN_HAIR_SALON,
        constant_promise.Premise.TIRED_LE_74}
)
def handle_style_hair():
    """处理修整发型指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 60
    character_data.behavior.behavior_id = constant.Behavior.STYLE_HAIR
    character_data.state = constant.CharacterStatus.STATUS_STYLE_HAIR
    update.game_update_flow(60)


@add_instruct(
    constant.Instruct.FULL_BODY_STYLING,
    constant.InstructType.PLAY,
    _("全身造型服务"),
    {
        constant_promise.Premise.NOT_H,
        constant_promise.Premise.IN_STYLING_STUDIO,
        constant_promise.Premise.TIRED_LE_74}
)
def handle_full_body_styling():
    """处理全身造型服务指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 120
    character_data.behavior.behavior_id = constant.Behavior.FULL_BODY_STYLING
    character_data.state = constant.CharacterStatus.STATUS_FULL_BODY_STYLING
    update.game_update_flow(120)


@add_instruct(
    constant.Instruct.SOAK_FEET,
    constant.InstructType.PLAY,
    _("泡脚"),
    {
        constant_promise.Premise.NOT_H,
        constant_promise.Premise.IN_FOOT_BATH,
        constant_promise.Premise.TIRED_LE_74}
)
def handle_soak_feet():
    """处理泡脚指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 30
    character_data.behavior.behavior_id = constant.Behavior.SOAK_FEET
    character_data.state = constant.CharacterStatus.STATUS_SOAK_FEET
    update.game_update_flow(30)


@add_instruct(
    constant.Instruct.STEAM_SAUNA,
    constant.InstructType.PLAY,
    _("蒸桑拿"),
    {
        constant_promise.Premise.NOT_H,
        constant_promise.Premise.IN_SAUNA,
        constant_promise.Premise.TIRED_LE_74}
)
def handle_steam_sauna():
    """处理蒸桑拿指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 30
    character_data.behavior.behavior_id = constant.Behavior.STEAM_SAUNA
    character_data.state = constant.CharacterStatus.STATUS_STEAM_SAUNA
    update.game_update_flow(30)


@add_instruct(
    constant.Instruct.HYDROTHERAPY_TREATMENT,
    constant.InstructType.PLAY,
    _("水疗护理"),
    {
        constant_promise.Premise.NOT_H,
        constant_promise.Premise.IN_SPA_ROOM,
        constant_promise.Premise.TIRED_LE_74}
)
def handle_hydrotherapy_treatment():
    """处理水疗护理指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 60
    character_data.behavior.behavior_id = constant.Behavior.HYDROTHERAPY_TREATMENT
    character_data.state = constant.CharacterStatus.STATUS_HYDROTHERAPY_TREATMENT
    update.game_update_flow(60)


@add_instruct(
    constant.Instruct.ONSEN_BATH,
    constant.InstructType.PLAY,
    _("泡温泉"),
    {
        constant_promise.Premise.NOT_H,
        constant_promise.Premise.IN_ONSEN,
        constant_promise.Premise.TIRED_LE_74}
)
def handle_onsen_bath():
    """处理泡温泉指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 60
    character_data.behavior.behavior_id = constant.Behavior.ONSEN_BATH
    character_data.state = constant.CharacterStatus.STATUS_ONSEN_BATH
    update.game_update_flow(60)


@add_instruct(
    constant.Instruct.AROMATHERAPY, constant.InstructType.PLAY, _("香薰疗愈"),
    {
        constant_promise.Premise.NOT_H,
        constant_promise.Premise.IN_AROMATHERAPY_ROOM,
        constant_promise.Premise.HAVE_TARGET,
    }
)
def handle_aromatherapy():
    """处理香薰疗愈指令"""
    cache.now_panel_id = constant.Panel.AROMATHERAPY


# 以下为工作#

@add_instruct(
    constant.Instruct.OFFICIAL_WORK,
    constant.InstructType.WORK,
    _("处理公务"),
    {constant_promise.Premise.NOT_H,
     constant_promise.Premise.IN_DR_OFFICE,
     constant_promise.Premise.HAVE_OFFICE_WORK_NEED_TO_DO,
     constant_promise.Premise.TIRED_LE_74}
)
def handle_official_work():
    """处理处理公务指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data = cache.character_data[0]
    character_data.behavior.duration = 60
    character_data.behavior.behavior_id = constant.Behavior.OFFICIAL_WORK
    character_data.state = constant.CharacterStatus.STATUS_OFFICIAL_WORK
    update.game_update_flow(60)


@add_instruct(
    constant.Instruct.BATTLE_COMMAND,
    constant.InstructType.WORK,
    _("指挥作战（未实装）"),
    {constant_promise.Premise.NOT_H,
     constant_promise.Premise.IN_COMMAND_ROOM,
     constant_promise.Premise.TO_DO,
     constant_promise.Premise.TIRED_LE_74}
)
def handle_battle_command():
    """处理指挥作战指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)


@add_instruct(
    constant.Instruct.ASSISTANT_ADJUSTMENTS, constant.InstructType.WORK, _("助理相关调整"),
    {constant_promise.Premise.NOT_H,
     constant_promise.Premise.IN_DR_OFFICE, }
)
def handle_ASSISTANT_ADJUSTMENTS():
    """处理助理相关调整指令"""
    cache.now_panel_id = constant.Panel.ASSISTANT


@add_instruct(
    constant.Instruct.BUILDING, constant.InstructType.WORK, _("基建系统"),
    {constant_promise.Premise.NOT_H,
     constant_promise.Premise.IN_BUILDING_ROOM, }
)
def handle_building():
    """处理基建系统指令"""
    cache.now_panel_id = constant.Panel.BUILDING


@add_instruct(
    constant.Instruct.RECRUITMENT, constant.InstructType.WORK, _("招募情况"),
    {constant_promise.Premise.NOT_H,
     constant_promise.Premise.IN_HR_OFFICE, }
)
def handle_recruiment():
    """处理招募情况指令"""
    cache.now_panel_id = constant.Panel.RECRUITMENT


@add_instruct(
    constant.Instruct.VISITOR_SYSTEM, constant.InstructType.WORK, _("访客系统"),
    {constant_promise.Premise.NOT_H,
     constant_promise.Premise.IN_DIPLOMATIC_OFFICE, 
     constant_promise.Premise.VISITOR_ZONE_GE_2, }
)
def handle_visitor_system():
    """处理访客系统指令"""
    cache.now_panel_id = constant.Panel.VISITOR


@add_instruct(
    constant.Instruct.INVITE_VISITOR, constant.InstructType.WORK, _("邀请访客"),
    {constant_promise.Premise.NOT_H,
     constant_promise.Premise.IN_DIPLOMATIC_OFFICE, 
     constant_promise.Premise.VISITOR_ZONE_GE_2, }
)
def handle_invite_visitor():
    """处理邀请访客指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data = cache.character_data[0]
    character_data.behavior.duration = 60
    character_data.behavior.behavior_id = constant.Behavior.INVITE_VISITOR
    character_data.state = constant.CharacterStatus.STATUS_INVITE_VISITOR
    update.game_update_flow(60)


@add_instruct(
    constant.Instruct.PRTS, constant.InstructType.WORK, _("普瑞赛斯"),
    {constant_promise.Premise.NOT_H,
     constant_promise.Premise.IN_DR_OFF_OR_SERVER_ROOM_OR_DEBUG, }
)
def handle_prts():
    """处理普瑞赛斯指令"""
    cache.now_panel_id = constant.Panel.PRTS


@add_instruct(
    constant.Instruct.TRAINING,
    constant.InstructType.WORK,
    _("战斗训练"),
    {constant_promise.Premise.NOT_H,
     constant_promise.Premise.IN_TRAINING_ROOM,
     constant_promise.Premise.TIRED_LE_74}
)
def handle_training():
    """处理战斗训练指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data = cache.character_data[0]
    character_data.behavior.duration = 120
    character_data.behavior.behavior_id = constant.Behavior.TRAINING
    character_data.state = constant.CharacterStatus.STATUS_TRAINING
    update.game_update_flow(120)


@add_instruct(
    constant.Instruct.EXERCISE,
    constant.InstructType.PLAY,
    _("锻炼身体"),
    {constant_promise.Premise.NOT_H,
     constant_promise.Premise.IN_GYM_ROOM,
     constant_promise.Premise.TIRED_LE_74}
)
def handle_exercise():
    """处理锻炼身体指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data = cache.character_data[0]
    character_data.behavior.duration = 60
    character_data.behavior.behavior_id = constant.Behavior.EXERCISE
    character_data.state = constant.CharacterStatus.STATUS_EXERCISE
    update.game_update_flow(60)


@add_instruct(
    constant.Instruct.CURE_PATIENT,
    constant.InstructType.WORK,
    _("诊疗病人"),
    {constant_promise.Premise.NOT_H,
     constant_promise.Premise.IN_CLINIC,
     constant_promise.Premise.PATIENT_WAIT,
     constant_promise.Premise.TIRED_LE_74}
)
def handle_cure_patient():
    """处理诊疗病人指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data = cache.character_data[0]
    character_data.behavior.duration = 30
    character_data.behavior.behavior_id = constant.Behavior.CURE_PATIENT
    character_data.state = constant.CharacterStatus.STATUS_CURE_PATIENT
    update.game_update_flow(30)


@add_instruct(
    constant.Instruct.RECRUIT,
    constant.InstructType.WORK,
    _("招募干员"),
    {constant_promise.Premise.NOT_H,
     constant_promise.Premise.IN_HR_OFFICE,
     constant_promise.Premise.TIRED_LE_74}
)
def handle_recruit():
    """处理招募干员指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data = cache.character_data[0]
    character_data.behavior.duration = 60
    character_data.behavior.behavior_id = constant.Behavior.RECRUIT
    character_data.state = constant.CharacterStatus.STATUS_RECRUIT
    update.game_update_flow(60)


@add_instruct(
    constant.Instruct.CONFIM_RECRUIT,
    constant.InstructType.WORK,
    _("确认已招募干员"),
    {constant_promise.Premise.NOT_H,
     constant_promise.Premise.IN_DR_OFFICE,
     constant_promise.Premise.NEW_NPC_WAIT,
     constant_promise.Premise.TIRED_LE_74}
)
def handle_confim_recruit():
    """处理确认已招募干员指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    now_draw = draw.WaitDraw()
    now_draw.width = width
    now_draw.style = "gold_enrod"
    now_draw.text = ""

    if len(cache.npc_id_got) >= cache.rhodes_island.people_max:
        now_draw.text += _(f"\n\n   ※ 空余宿舍不足，无法招募 ※\n\n")

    elif len(cache.rhodes_island.recruited_id):
        new_chara_id = cache.rhodes_island.recruited_id.pop()
        character_handle.get_new_character(new_chara_id)
        character_data = cache.character_data[new_chara_id]
        now_draw.text += _(f"\n\n   ※ 成功招募了{character_data.name} ※\n\n")
        character_data.behavior.behavior_id = constant.Behavior.WAIT
        character_data.state = constant.CharacterStatus.STATUS_WAIT
        character_data.behavior.duration = 5
        update.game_update_flow(5)

    now_draw.draw()


@add_instruct(
    constant.Instruct.MAINTENANCE_FACILITIES,
    constant.InstructType.WORK,
    _("维护设施"),
    {constant_promise.Premise.NOT_H,
     constant_promise.Premise.IN_ANY_MAINTENANCE_PLACE,
     constant_promise.Premise.TIRED_LE_74}
)
def handle_maintenance_facilities():
    """处理维护设施指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data = cache.character_data[0]
    character_data.behavior.duration = 60
    character_data.behavior.behavior_id = constant.Behavior.MAINTENANCE_FACILITIES
    character_data.state = constant.CharacterStatus.STATUS_MAINTENANCE_FACILITIES
    update.game_update_flow(60)


@add_instruct(
    constant.Instruct.REPAIR_EQUIPMENT,
    constant.InstructType.WORK,
    _("维修装备"),
    {constant_promise.Premise.NOT_H,
     constant_promise.Premise.IN_BLACKSMITH_SHOP,
     constant_promise.Premise.TIRED_LE_74}
)
def handle_repair_equipment():
    """处理维修装备指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data = cache.character_data[0]
    character_data.behavior.duration = 60
    character_data.behavior.behavior_id = constant.Behavior.REPAIR_EQUIPMENT
    character_data.state = constant.CharacterStatus.STATUS_REPAIR_EQUIPMENT
    update.game_update_flow(60)


# 以下为猥亵#


@add_instruct(
    constant.Instruct.EMBRACE, constant.InstructType.OBSCENITY, _("拥抱"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.T_NORMAL_256_OR_UNCONSCIOUS_FLAG,
     constant_promise.Premise.TIRED_LE_84}
)
def handle_embrace():
    """处理拥抱指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    if character.calculation_instuct_judege(0, character_data.target_character_id, _("初级骚扰"))[0]:
        character_data.behavior.behavior_id = constant.Behavior.EMBRACE
        character_data.state = constant.CharacterStatus.STATUS_EMBRACE
    else:
        character_data.behavior.behavior_id = constant.Behavior.LOW_OBSCENITY_ANUS
        character_data.state = constant.CharacterStatus.STATUS_LOW_OBSCENITY_ANUS
    character_data.behavior.duration = 3
    update.game_update_flow(3)


@add_instruct(
    constant.Instruct.KISS,
    constant.InstructType.OBSCENITY,
    _("亲吻"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.T_NORMAL_256_OR_UNCONSCIOUS_FLAG,
     constant_promise.Premise.TIRED_LE_84}
)
def handle_kiss():
    """处理亲吻指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    if character.calculation_instuct_judege(0, character_data.target_character_id, _("亲吻"))[0]:
        character_data.behavior.behavior_id = constant.Behavior.KISS
        character_data.state = constant.CharacterStatus.STATUS_KISS
    else:
        character_data.behavior.behavior_id = constant.Behavior.KISS_FAIL
        character_data.state = constant.CharacterStatus.STATUS_KISS_FAIL
    update.game_update_flow(5)


@add_instruct(
    constant.Instruct.TOUCH_HEAD,
    constant.InstructType.OBSCENITY,
    _("摸头"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.T_NORMAL_256_OR_UNCONSCIOUS_FLAG,
     constant_promise.Premise.TIRED_LE_84}
)
def handle_touch_head():
    """处理摸头指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data = cache.character_data[0]
    character_data.behavior.duration = 10
    if character.calculation_instuct_judege(0, character_data.target_character_id, _("初级骚扰"))[0]:
        character_data.behavior.behavior_id = constant.Behavior.TOUCH_HEAD
        character_data.state = constant.CharacterStatus.STATUS_TOUCH_HEAD
    else:
        character_data.behavior.behavior_id = constant.Behavior.LOW_OBSCENITY_ANUS
        character_data.state = constant.CharacterStatus.STATUS_LOW_OBSCENITY_ANUS
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.TOUCH_BREAST,
    constant.InstructType.OBSCENITY,
    _("摸胸"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.T_NORMAL_256_OR_UNCONSCIOUS_FLAG,
     constant_promise.Premise.TIRED_LE_84}
)
def handle_touch_breast():
    """处理摸胸指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 10
    if character.calculation_instuct_judege(0, character_data.target_character_id, _("严重骚扰"))[0]:
        character_data.behavior.behavior_id = constant.Behavior.TOUCH_BREAST
        character_data.state = constant.CharacterStatus.STATUS_TOUCH_BREAST
    else:
        character_data.behavior.behavior_id = constant.Behavior.HIGH_OBSCENITY_ANUS
        character_data.state = constant.CharacterStatus.STATUS_HIGH_OBSCENITY_ANUS
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.TOUCH_BUTTOCKS,
    constant.InstructType.OBSCENITY,
    _("摸屁股"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.T_NORMAL_256_OR_UNCONSCIOUS_FLAG,
     constant_promise.Premise.TIRED_LE_84}
)
def handle_touch_buttocks():
    """处理摸屁股指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 10
    if character.calculation_instuct_judege(0, character_data.target_character_id, _("严重骚扰"))[0]:
        character_data.behavior.behavior_id = constant.Behavior.TOUCH_BUTTOCKS
        character_data.state = constant.CharacterStatus.STATUS_TOUCH_BUTTOCKS
    else:
        character_data.behavior.behavior_id = constant.Behavior.HIGH_OBSCENITY_ANUS
        character_data.state = constant.CharacterStatus.STATUS_HIGH_OBSCENITY_ANUS
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.TOUCH_EARS,
    constant.InstructType.OBSCENITY,
    _("摸耳朵"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.T_NORMAL_256_OR_UNCONSCIOUS_FLAG,
     constant_promise.Premise.TIRED_LE_84, },
)
def handle_touch_ears():
    """处理摸耳朵指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 10
    if character.calculation_instuct_judege(0, character_data.target_character_id, _("初级骚扰"))[0]:
        character_data.behavior.behavior_id = constant.Behavior.TOUCH_EARS
        character_data.state = constant.CharacterStatus.STATUS_TOUCH_EARS
    else:
        character_data.behavior.behavior_id = constant.Behavior.LOW_OBSCENITY_ANUS
        character_data.state = constant.CharacterStatus.STATUS_LOW_OBSCENITY_ANUS
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.TOUCH_HORN,
    constant.InstructType.OBSCENITY,
    _("摸角"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.T_NORMAL_256_OR_UNCONSCIOUS_FLAG,
     constant_promise.Premise.TARGET_HAVE_HORN,
     constant_promise.Premise.TIRED_LE_84,},
)
def handle_touch_horn():
    """处理摸角指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 10
    if character.calculation_instuct_judege(0, character_data.target_character_id, _("初级骚扰"))[0]:
        character_data.behavior.behavior_id = constant.Behavior.TOUCH_HORN
        character_data.state = constant.CharacterStatus.STATUS_TOUCH_HORN
    else:
        character_data.behavior.behavior_id = constant.Behavior.LOW_OBSCENITY_ANUS
        character_data.state = constant.CharacterStatus.STATUS_LOW_OBSCENITY_ANUS
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.TOUCH_TAIL,
    constant.InstructType.OBSCENITY,
    _("摸尾巴"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.T_NORMAL_256_OR_UNCONSCIOUS_FLAG,
     constant_promise.Premise.TARGET_HAVE_TAIL,
     constant_promise.Premise.TIRED_LE_84,},
)
def handle_touch_tail():
    """处理摸尾巴指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 10
    if character.calculation_instuct_judege(0, character_data.target_character_id, _("初级骚扰"))[0]:
        character_data.behavior.behavior_id = constant.Behavior.TOUCH_TAIL
        character_data.state = constant.CharacterStatus.STATUS_TOUCH_TAIL
    else:
        character_data.behavior.behavior_id = constant.Behavior.LOW_OBSCENITY_ANUS
        character_data.state = constant.CharacterStatus.STATUS_LOW_OBSCENITY_ANUS
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.TOUCH_RING,
    constant.InstructType.OBSCENITY,
    _("摸光环"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.T_NORMAL_256_OR_UNCONSCIOUS_FLAG,
     constant_promise.Premise.TARGET_HAVE_RING,
     constant_promise.Premise.TIRED_LE_84,},
)
def handle_touch_ring():
    """处理摸光环指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 10
    if character.calculation_instuct_judege(0, character_data.target_character_id, _("初级骚扰"))[0]:
        character_data.behavior.behavior_id = constant.Behavior.TOUCH_RING
        character_data.state = constant.CharacterStatus.STATUS_TOUCH_RING
    else:
        character_data.behavior.behavior_id = constant.Behavior.LOW_OBSCENITY_ANUS
        character_data.state = constant.CharacterStatus.STATUS_LOW_OBSCENITY_ANUS
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.TOUCH_WING,
    constant.InstructType.OBSCENITY,
    _("摸光翼"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.T_NORMAL_256_OR_UNCONSCIOUS_FLAG,
     constant_promise.Premise.TARGET_HAVE_WING,
     constant_promise.Premise.TIRED_LE_84,},
)
def handle_touch_wing():
    """处理摸光翼指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 10
    if character.calculation_instuct_judege(0, character_data.target_character_id, _("初级骚扰"))[0]:
        character_data.behavior.behavior_id = constant.Behavior.TOUCH_WING
        character_data.state = constant.CharacterStatus.STATUS_TOUCH_WING
    else:
        character_data.behavior.behavior_id = constant.Behavior.LOW_OBSCENITY_ANUS
        character_data.state = constant.CharacterStatus.STATUS_LOW_OBSCENITY_ANUS
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.TOUCH_TENTACLE,
    constant.InstructType.OBSCENITY,
    _("摸触手"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.T_NORMAL_256_OR_UNCONSCIOUS_FLAG,
     constant_promise.Premise.TARGET_HAVE_TENTACLE,
     constant_promise.Premise.TIRED_LE_84,},
)
def handle_touch_tentacle():
    """处理摸触手指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 10
    if character.calculation_instuct_judege(0, character_data.target_character_id, _("初级骚扰"))[0]:
        character_data.behavior.behavior_id = constant.Behavior.TOUCH_TENTACLE
        character_data.state = constant.CharacterStatus.STATUS_TOUCH_TENTACLE
    else:
        character_data.behavior.behavior_id = constant.Behavior.LOW_OBSCENITY_ANUS
        character_data.state = constant.CharacterStatus.STATUS_LOW_OBSCENITY_ANUS
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.TOUCH_CAR,
    constant.InstructType.OBSCENITY,
    _("摸小车"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.T_NORMAL_256_OR_UNCONSCIOUS_FLAG,
     constant_promise.Premise.TARGET_HAVE_CAR,
     constant_promise.Premise.TIRED_LE_84,},
)
def handle_touch_car():
    """处理摸小车指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 10
    if character.calculation_instuct_judege(0, character_data.target_character_id, _("初级骚扰"))[0]:
        character_data.behavior.behavior_id = constant.Behavior.TOUCH_CAR
        character_data.state = constant.CharacterStatus.STATUS_TOUCH_CAR
    else:
        character_data.behavior.behavior_id = constant.Behavior.LOW_OBSCENITY_ANUS
        character_data.state = constant.CharacterStatus.STATUS_LOW_OBSCENITY_ANUS
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.HAND_IN_HAND,
    constant.InstructType.OBSCENITY,
    _("牵手"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.T_NORMAL_256_OR_UNCONSCIOUS_FLAG,
     constant_promise.Premise.TIRED_LE_84}
)
def handle_handle_in_handle():
    """处理牵手指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 10
    if character.calculation_instuct_judege(0, character_data.target_character_id, _("初级骚扰"))[0]:
        character_data.behavior.behavior_id = constant.Behavior.HAND_IN_HAND
        character_data.state = constant.CharacterStatus.STATUS_HAND_IN_HAND
    else:
        character_data.behavior.behavior_id = constant.Behavior.LOW_OBSCENITY_ANUS
        character_data.state = constant.CharacterStatus.STATUS_LOW_OBSCENITY_ANUS
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.LAP_PILLOW,
    constant.InstructType.OBSCENITY,
    _("膝枕"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.T_NORMAL_256_OR_UNCONSCIOUS_FLAG,
     constant_promise.Premise.PLACE_FURNITURE_GE_1,
     constant_promise.Premise.TIRED_LE_84}
)
def handle_lap_pillow():
    """处理膝枕指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 30
    if character.calculation_instuct_judege(0, character_data.target_character_id, _("初级骚扰"))[0]:
        character_data.behavior.behavior_id = constant.Behavior.LAP_PILLOW
        character_data.state = constant.CharacterStatus.STATUS_LAP_PILLOW
    else:
        character_data.behavior.behavior_id = constant.Behavior.LOW_OBSCENITY_ANUS
        character_data.state = constant.CharacterStatus.STATUS_LOW_OBSCENITY_ANUS
    update.game_update_flow(30)


@add_instruct(
    constant.Instruct.RAISE_SKIRT,
    constant.InstructType.OBSCENITY,
    _("掀起裙子"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.T_NORMAL_256_OR_UNCONSCIOUS_FLAG,
     constant_promise.Premise.TARGET_WEAR_SKIRT,
     constant_promise.Premise.TIRED_LE_84}
)
def handle_raise_skirt():
    """处理掀起裙子指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    if character.calculation_instuct_judege(0, character_data.target_character_id, _("严重骚扰"))[0]:
        character_data.behavior.behavior_id = constant.Behavior.RAISE_SKIRT
        character_data.state = constant.CharacterStatus.STATUS_RAISE_SKIRT
    else:
        character_data.behavior.behavior_id = constant.Behavior.HIGH_OBSCENITY_ANUS
        character_data.state = constant.CharacterStatus.STATUS_HIGH_OBSCENITY_ANUS
    update.game_update_flow(5)


@add_instruct(
    constant.Instruct.ASK_FOR_PAN,
    constant.InstructType.OBSCENITY,
    _("索要内裤"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.T_NORMAL_256_OR_UNCONSCIOUS_FLAG,
     constant_promise.Premise.TARGET_WEAR_PAN,
     constant_promise.Premise.COLLECT_BONUS_102,
     constant_promise.Premise.TIRED_LE_84}
)
def handle_ask_for_pan():
    """处理索要内裤指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    if character.calculation_instuct_judege(0, character_data.target_character_id, _("严重骚扰"))[0]:
        character_data.behavior.behavior_id = constant.Behavior.ASK_FOR_PAN
        character_data.state = constant.CharacterStatus.STATUS_ASK_FOR_PAN
    else:
        character_data.behavior.behavior_id = constant.Behavior.HIGH_OBSCENITY_ANUS
        character_data.state = constant.CharacterStatus.STATUS_HIGH_OBSCENITY_ANUS
    update.game_update_flow(5)


@add_instruct(
    constant.Instruct.ASK_FOR_SOCKS,
    constant.InstructType.OBSCENITY,
    _("索要袜子"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.T_NORMAL_256_OR_UNCONSCIOUS_FLAG,
     constant_promise.Premise.TARGET_WEAR_SOCKS,
     constant_promise.Premise.COLLECT_BONUS_202,
     constant_promise.Premise.TIRED_LE_84}
)
def handle_ask_for_socks():
    """处理索要袜子指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    if character.calculation_instuct_judege(0, character_data.target_character_id, _("严重骚扰"))[0]:
        character_data.behavior.behavior_id = constant.Behavior.ASK_FOR_SOCKS
        character_data.state = constant.CharacterStatus.STATUS_ASK_FOR_SOCKS
    else:
        character_data.behavior.behavior_id = constant.Behavior.HIGH_OBSCENITY_ANUS
        character_data.state = constant.CharacterStatus.STATUS_HIGH_OBSCENITY_ANUS
    update.game_update_flow(5)


@add_instruct(
    constant.Instruct.STEAL_PAN,
    constant.InstructType.OBSCENITY,
    _("偷走内裤"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.T_UNNORMAL_5_6,
     constant_promise.Premise.TARGET_WEAR_PAN,
     constant_promise.Premise.TIRED_LE_84}
)
def handle_steal_pan():
    """处理偷走内裤指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    character_data.behavior.behavior_id = constant.Behavior.STEAL_PAN
    character_data.state = constant.CharacterStatus.STATUS_STEAL_PAN
    update.game_update_flow(5)


@add_instruct(
    constant.Instruct.STEAL_SOCKS,
    constant.InstructType.OBSCENITY,
    _("偷走袜子"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.T_UNNORMAL_5_6,
     constant_promise.Premise.TARGET_WEAR_SOCKS,
     constant_promise.Premise.TIRED_LE_84}
)
def handle_steal_socks():
    """处理偷走袜子指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data = cache.character_data[0]
    character_data.behavior.duration = 5
    character_data.behavior.behavior_id = constant.Behavior.STEAL_SOCKS
    character_data.state = constant.CharacterStatus.STATUS_STEAL_SOCKS
    update.game_update_flow(5)


@add_instruct(
    constant.Instruct.TOUCH_CLITORIS,
    constant.InstructType.OBSCENITY,
    _("阴蒂爱抚"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.T_NORMAL_256_OR_UNCONSCIOUS_FLAG,
     constant_promise.Premise.TIRED_LE_84}
)
def handle_touch_clitoris():
    """处理阴蒂爱抚指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    if character.calculation_instuct_judege(0, character_data.target_character_id, _("严重骚扰"))[0]:
        character_data.behavior.behavior_id = constant.Behavior.TOUCH_CLITORIS
        character_data.state = constant.CharacterStatus.STATUS_TOUCH_CLITORIS
    else:
        character_data.behavior.behavior_id = constant.Behavior.HIGH_OBSCENITY_ANUS
        character_data.state = constant.CharacterStatus.STATUS_HIGH_OBSCENITY_ANUS
    character_data.behavior.duration = 5
    update.game_update_flow(5)


@add_instruct(
    constant.Instruct.TOUCH_VAGINA,
    constant.InstructType.OBSCENITY,
    _("手指插入（V）"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.T_NORMAL_256_OR_UNCONSCIOUS_FLAG,
     constant_promise.Premise.TIRED_LE_84}
)
def handle_touch_vagina():
    """处理手指插入（V）指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    if character.calculation_instuct_judege(0, character_data.target_character_id, _("严重骚扰"))[0]:
        character_data.behavior.behavior_id = constant.Behavior.TOUCH_VAGINA
        character_data.state = constant.CharacterStatus.STATUS_TOUCH_VAGINA
    else:
        character_data.behavior.behavior_id = constant.Behavior.HIGH_OBSCENITY_ANUS
        character_data.state = constant.CharacterStatus.STATUS_HIGH_OBSCENITY_ANUS
    character_data.behavior.duration = 5
    update.game_update_flow(5)


@add_instruct(
    constant.Instruct.TOUCH_ANUS,
    constant.InstructType.OBSCENITY,
    _("手指插入（A）"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.T_NORMAL_256_OR_UNCONSCIOUS_FLAG,
     constant_promise.Premise.TIRED_LE_84}
)
def handle_touch_anus():
    """处理手指插入（A）指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    if character.calculation_instuct_judege(0, character_data.target_character_id, _("严重骚扰"))[0]:
        character_data.behavior.behavior_id = constant.Behavior.TOUCH_ANUS
        character_data.state = constant.CharacterStatus.STATUS_TOUCH_ANUS
    else:
        character_data.behavior.behavior_id = constant.Behavior.HIGH_OBSCENITY_ANUS
        character_data.state = constant.CharacterStatus.STATUS_HIGH_OBSCENITY_ANUS
    character_data.behavior.duration = 5
    update.game_update_flow(5)


@add_instruct(
    constant.Instruct.MILK,
    constant.InstructType.OBSCENITY,
    _("挤奶"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.T_NORMAL_256_OR_UNCONSCIOUS_FLAG,
     constant_promise.Premise.TARGET_MILK_GE_30,
     constant_promise.Premise.TIRED_LE_84}
)
def handle_milk():
    """处理挤奶指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    if character.calculation_instuct_judege(0, character_data.target_character_id, _("严重骚扰"))[0]:
        character_data.behavior.behavior_id = constant.Behavior.MILK
        character_data.state = constant.CharacterStatus.STATUS_MILK
    else:
        character_data.behavior.behavior_id = constant.Behavior.HIGH_OBSCENITY_ANUS
        character_data.state = constant.CharacterStatus.STATUS_HIGH_OBSCENITY_ANUS
    character_data.behavior.duration = 30
    update.game_update_flow(30)


@add_instruct(
    constant.Instruct.BAGGING_AND_MOVING,
    constant.InstructType.OBSCENITY,
    _("装袋搬走"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.NOT_H,
     constant_promise.Premise.HAVE_BAG,
     constant_promise.Premise.T_IMPRISONMENT_0,
     constant_promise.Premise.T_UNNORMAL_6,
    #  constant_promise.Premise.T_UNCONSCIOUS_FLAG_0,
     constant_promise.Premise.SCENE_ONLY_TWO,
     constant_promise.Premise.PL_NOT_BAGGING_CHARA,
     constant_promise.Premise.TIRED_LE_74}
)
def handle_bagging_and_moving():
    """处理装袋搬走指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.BAGGING_AND_MOVING
    character_data.state = constant.CharacterStatus.STATUS_BAGGING_AND_MOVING
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.PUT_INTO_PRISON,
    constant.InstructType.OBSCENITY,
    _("投入监牢"),
    {constant_promise.Premise.NOT_H,
     constant_promise.Premise.IN_PRISON,
     constant_promise.Premise.SCENE_ONLY_ONE,
     constant_promise.Premise.PL_BAGGING_CHARA,
     constant_promise.Premise.TIRED_LE_74}
)
def handle_put_into_prision():
    """处理投入监牢指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.PUT_INTO_PRISON
    character_data.state = constant.CharacterStatus.STATUS_PUT_INTO_PRISON
    character_data.behavior.duration = 10
    character_data.target_character_id = character_data.sp_flag.bagging_chara_id
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.SET_FREE,
    constant.InstructType.OBSCENITY,
    _("解除囚禁"),
    {constant_promise.Premise.NOT_H,
     constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IN_PRISON,
     constant_promise.Premise.SCENE_ONLY_TWO,
     constant_promise.Premise.T_IMPRISONMENT_1,
     constant_promise.Premise.TIRED_LE_74}
)
def handle_set_free():
    """处理解除囚禁指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.SET_FREE
    character_data.state = constant.CharacterStatus.STATUS_SET_FREE
    character_data.behavior.duration = 10
    update.game_update_flow(10)


# 以下为性爱#


@add_instruct(
    constant.Instruct.MAKING_OUT,
    constant.InstructType.SEX,
    _("身体爱抚"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H},
)
def handle_making_out():
    """处理身体爱抚指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.MAKING_OUT
    character_data.state = constant.CharacterStatus.STATUS_MAKING_OUT
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.KISS_H,
    constant.InstructType.SEX,
    _("接吻"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H},
)
def handle_kiss_h():
    """处理接吻指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.KISS_H
    character_data.state = constant.CharacterStatus.STATUS_KISS_H
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.BREAST_CARESS,
    constant.InstructType.SEX,
    _("胸爱抚"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H},
)
def handle_breast_caress():
    """处理胸爱抚指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.BREAST_CARESS
    character_data.state = constant.CharacterStatus.STATUS_BREAST_CARESS
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.TWIDDLE_NIPPLES,
    constant.InstructType.SEX,
    _("玩弄乳头"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H},
)
def handle_twiddle_nipples():
    """处理玩弄乳头指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.TWIDDLE_NIPPLES
    character_data.state = constant.CharacterStatus.STATUS_TWIDDLE_NIPPLES
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.BREAST_SUCKING,
    constant.InstructType.SEX,
    _("舔吸乳头"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H},
)
def handle_breast_sucking():
    """处理舔吸乳头指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.BREAST_SUCKING
    character_data.state = constant.CharacterStatus.STATUS_BREAST_SUCKING
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.CLIT_CARESS,
    constant.InstructType.SEX,
    _("阴蒂爱抚"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H},
)
def handle_cilt_caress():
    """处理阴蒂爱抚指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.CLIT_CARESS
    character_data.state = constant.CharacterStatus.STATUS_CLIT_CARESS
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.OPEN_LABIA,
    constant.InstructType.SEX,
    _("掰开阴唇观察"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H},
)
def handle_open_labia():
    """处理掰开阴唇观察指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.OPEN_LABIA
    character_data.state = constant.CharacterStatus.STATUS_OPEN_LABIA
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.OPEN_ANUS,
    constant.InstructType.SEX,
    _("掰开肛门观察"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H},
)
def handle_open_anus():
    """处理掰开肛门观察指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.OPEN_ANUS
    character_data.state = constant.CharacterStatus.STATUS_OPEN_ANUS
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.CUNNILINGUS,
    constant.InstructType.SEX,
    _("舔阴"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H},
)
def handle_cunnilingus():
    """处理舔阴指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.CUNNILINGUS
    character_data.state = constant.CharacterStatus.STATUS_CUNNILINGUS
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.LICK_ANAL,
    constant.InstructType.SEX,
    _("舔肛"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H},
)
def handle_lict_anal():
    """处理舔肛指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.LICK_ANAL
    character_data.state = constant.CharacterStatus.STATUS_LICK_ANAL
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.FINGER_INSERTION,
    constant.InstructType.SEX,
    _("手指插入(V)"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H},
)
def handle_finger_insertion():
    """处理手指插入(V)指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.FINGER_INSERTION
    character_data.state = constant.CharacterStatus.STATUS_FINGER_INSERTION
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.ANAL_CARESS,
    constant.InstructType.SEX,
    _("手指插入(A)"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H},
)
def handle_anal_caress():
    """处理手指插入(A)指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.ANAL_CARESS
    character_data.state = constant.CharacterStatus.STATUS_ANAL_CARESS
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.MAKE_MASTUREBATE,
    constant.InstructType.SEX,
    _("命令对方自慰"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H},
)
def handle_make_masturebate():
    """处理命令对方自慰指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.MAKE_MASTUREBATE
    character_data.state = constant.CharacterStatus.STATUS_MAKE_MASTUREBATE
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.MAKE_LICK_ANAL,
    constant.InstructType.SEX,
    _("命令对方舔自己肛门"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H},
)
def handle_make_lick_anal():
    """处理命令对方舔自己肛门指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.MAKE_LICK_ANAL
    character_data.state = constant.CharacterStatus.STATUS_MAKE_LICK_ANAL
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.DO_NOTHING,
    constant.InstructType.SEX,
    _("什么也不做"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H},
)
def handle_do_nothing():
    """处理什么也不做指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.DO_NOTHING
    character_data.state = constant.CharacterStatus.STATUS_DO_NOTHING
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.SEDECU,
    constant.InstructType.SEX,
    _("诱惑对方"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H},
)
def handle_sedecu():
    """处理诱惑对方指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.SEDECU
    character_data.state = constant.CharacterStatus.STATUS_SEDECU
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.HANDJOB,
    constant.InstructType.SEX,
    _("手交"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H},
)
def handle_handjob():
    """处理手交指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.HANDJOB
    character_data.state = constant.CharacterStatus.STATUS_HANDJOB
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.BLOWJOB,
    constant.InstructType.SEX,
    _("口交"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H},
)
def handle_blowjob():
    """处理口交指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.BLOWJOB
    character_data.state = constant.CharacterStatus.STATUS_BLOWJOB
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.PAIZURI,
    constant.InstructType.SEX,
    _("乳交"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H},
)
def handle_paizuri():
    """处理乳交指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.PAIZURI
    character_data.state = constant.CharacterStatus.STATUS_PAIZURI
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.FOOTJOB,
    constant.InstructType.SEX,
    _("足交"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.TARGET_TECHNIQUE_GE_3},
)
def handle_footjob():
    """处理足交指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.FOOTJOB
    character_data.state = constant.CharacterStatus.STATUS_FOOTJOB
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.HAIRJOB,
    constant.InstructType.SEX,
    _("发交"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.TARGET_TECHNIQUE_GE_3},
)
def handle_hairjob():
    """处理发交指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.HAIRJOB
    character_data.state = constant.CharacterStatus.STATUS_HAIRJOB
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.AXILLAJOB,
    constant.InstructType.SEX,
    _("腋交"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.TARGET_TECHNIQUE_GE_5},
)
def handle_axillajob():
    """处理腋交指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.AXILLAJOB
    character_data.state = constant.CharacterStatus.STATUS_AXILLAJOB
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.RUB_BUTTOCK,
    constant.InstructType.SEX,
    _("素股"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H},
)
def handle_rub_buttock():
    """处理素股指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.RUB_BUTTOCK
    character_data.state = constant.CharacterStatus.STATUS_RUB_BUTTOCK
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.HAND_BLOWJOB,
    constant.InstructType.SEX,
    _("手交口交"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.LAST_CMD_BLOWJOB_OR_HANDJOB,
     constant_promise.Premise.TARGET_TECHNIQUE_GE_3},
)
def handle_hand_blowjob():
    """处理手交口交指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.HAND_BLOWJOB
    character_data.state = constant.CharacterStatus.STATUS_HAND_BLOWJOB
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.TITS_BLOWJOB,
    constant.InstructType.SEX,
    _("乳交口交"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.LAST_CMD_BLOWJOB_OR_PAIZURI,
     constant_promise.Premise.TARGET_TECHNIQUE_GE_3},
)
def handle_tits_blowjob():
    """处理乳交口交指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.TITS_BLOWJOB
    character_data.state = constant.CharacterStatus.STATUS_TITS_BLOWJOB
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.FOCUS_BLOWJOB,
    constant.InstructType.SEX,
    _("真空口交"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.LAST_CMD_BLOWJOB,
     constant_promise.Premise.TARGET_TECHNIQUE_GE_3},
)
def handle_focus_blowjob():
    """处理真空口交指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.FOCUS_BLOWJOB
    character_data.state = constant.CharacterStatus.STATUS_FOCUS_BLOWJOB
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.DEEP_THROAT,
    constant.InstructType.SEX,
    _("深喉插入"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.LAST_CMD_BLOWJOB,
     constant_promise.Premise.TARGET_TECHNIQUE_GE_3},
)
def handle_deep_throat():
    """处理深喉插入指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.DEEP_THROAT
    character_data.state = constant.CharacterStatus.STATUS_DEEP_THROAT
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.SIXTY_NINE,
    constant.InstructType.SEX,
    _("六九式"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.PLACE_FURNITURE_3,
     constant_promise.Premise.LAST_CMD_BLOWJOB_OR_CUNNILINGUS,
     constant_promise.Premise.TECHNIQUE_GE_3,
     constant_promise.Premise.TARGET_TECHNIQUE_GE_3},
)
def handle_sixty_nine():
    """处理六九式指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.SIXTY_NINE
    character_data.state = constant.CharacterStatus.STATUS_SIXTY_NINE
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.LEGJOB,
    constant.InstructType.SEX,
    _("腿交"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H},
)
def handle_legjob():
    """处理腿交指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.LEGJOB
    character_data.state = constant.CharacterStatus.STATUS_LEGJOB
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.TAILJOB,
    constant.InstructType.SEX,
    _("尾交"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.TARGET_HAVE_TAIL,
     constant_promise.Premise.IS_H},
)
def handle_tailjob():
    """处理尾交指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.TAILJOB
    character_data.state = constant.CharacterStatus.STATUS_TAILJOB
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.FACE_RUB,
    constant.InstructType.SEX,
    _("阴茎蹭脸"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H},
)
def handle_face_rub():
    """处理阴茎蹭脸指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.FACE_RUB
    character_data.state = constant.CharacterStatus.STATUS_FACE_RUB
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.HORN_RUB,
    constant.InstructType.SEX,
    _("阴茎蹭角"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.TARGET_HAVE_HORN,
     constant_promise.Premise.IS_H},
)
def handle_horn_rub():
    """处理阴茎蹭角指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.HORN_RUB
    character_data.state = constant.CharacterStatus.STATUS_HORN_RUB
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.EARS_RUB,
    constant.InstructType.SEX,
    _("阴茎蹭耳朵"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.TARGET_HAVE_EARS,
     constant_promise.Premise.IS_H},
)
def handle_eras_rub():
    """处理阴茎蹭耳朵指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.EARS_RUB
    character_data.state = constant.CharacterStatus.STATUS_EARS_RUB
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.NIPPLE_CLAMP_ON,
    constant.InstructType.SEX,
    _("戴上乳头夹"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.HAVE_NIPPLE_CLAMP,
     constant_promise.Premise.TARGET_NOT_NIPPLE_CLAMP},
)
def handle_nipple_clamp_on():
    """处理戴上乳头夹指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.NIPPLE_CLAMP_ON
    character_data.state = constant.CharacterStatus.STATUS_NIPPLE_CLAMP_ON
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.NIPPLE_CLAMP_OFF,
    constant.InstructType.SEX,
    _("取下乳头夹"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.HAVE_NIPPLE_CLAMP,
     constant_promise.Premise.TARGET_NOW_NIPPLE_CLAMP},
)
def handle_nipple_clamp_off():
    """处理取下乳头夹指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.NIPPLE_CLAMP_OFF
    character_data.state = constant.CharacterStatus.STATUS_NIPPLE_CLAMP_OFF
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.NIPPLES_LOVE_EGG,
    constant.InstructType.SEX,
    _("乳头跳蛋"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.HAVE_LOVE_EGG},
)
def handle_nipples_love_egg():
    """处理乳头跳蛋指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.NIPPLES_LOVE_EGG
    character_data.state = constant.CharacterStatus.STATUS_NIPPLES_LOVE_EGG
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.CLIT_CLAMP_ON,
    constant.InstructType.SEX,
    _("戴上阴蒂夹"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.HAVE_CLIT_CLAMP,
     constant_promise.Premise.TARGET_NOT_CLIT_CLAMP},
)
def handle_clit_clamp_on():
    """处理戴上阴蒂夹指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.CLIT_CLAMP_ON
    character_data.state = constant.CharacterStatus.STATUS_CLIT_CLAMP_ON
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.CLIT_CLAMP_OFF,
    constant.InstructType.SEX,
    _("取下阴蒂夹"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.HAVE_CLIT_CLAMP,
     constant_promise.Premise.TARGET_NOW_CLIT_CLAMP},
)
def handle_clit_clamp_off():
    """处理取下阴蒂夹指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.CLIT_CLAMP_OFF
    character_data.state = constant.CharacterStatus.STATUS_CLIT_CLAMP_OFF
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.CLIT_LOVE_EGG,
    constant.InstructType.SEX,
    _("阴蒂跳蛋"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.HAVE_LOVE_EGG},
)
def handle_clit_love_egg():
    """处理阴蒂跳蛋指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.CLIT_LOVE_EGG
    character_data.state = constant.CharacterStatus.STATUS_CLIT_LOVE_EGG
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.ELECTRIC_MESSAGE_STICK,
    constant.InstructType.SEX,
    _("电动按摩棒"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.HAVE_ELECTRIC_MESSAGE_STICK},
)
def handle_electric_message_stick():
    """处理电动按摩棒指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.ELECTRIC_MESSAGE_STICK
    character_data.state = constant.CharacterStatus.STATUS_ELECTRIC_MESSAGE_STICK
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.VIBRATOR_INSERTION,
    constant.InstructType.SEX,
    _("插入震动棒"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.HAVE_VIBRATOR,
     constant_promise.Premise.TARGET_NOT_VIBRATOR_INSERTION},
)
def handle_vibrator_insertion():
    """处理插入震动棒指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.VIBRATOR_INSERTION
    character_data.state = constant.CharacterStatus.STATUS_VIBRATOR_INSERTION
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.VIBRATOR_INSERTION_ANAL,
    constant.InstructType.SEX,
    _("肛门插入震动棒"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.HAVE_VIBRATOR,
     constant_promise.Premise.TARGET_NOT_VIBRATOR_INSERTION_ANAL},
)
def handle_vibrator_insertion_anal():
    """处理肛门插入震动棒指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.VIBRATOR_INSERTION_ANAL
    character_data.state = constant.CharacterStatus.STATUS_VIBRATOR_INSERTION_ANAL
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.VIBRATOR_INSERTION_OFF,
    constant.InstructType.SEX,
    _("拔出震动棒"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.HAVE_VIBRATOR,
     constant_promise.Premise.TARGET_NOW_VIBRATOR_INSERTION},
)
def handle_vibrator_insertion_off():
    """处理拔出震动棒指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.VIBRATOR_INSERTION_OFF
    character_data.state = constant.CharacterStatus.STATUS_VIBRATOR_INSERTION_OFF
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.VIBRATOR_INSERTION_ANAL_OFF,
    constant.InstructType.SEX,
    _("拔出肛门震动棒"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.HAVE_VIBRATOR,
     constant_promise.Premise.TARGET_NOW_VIBRATOR_INSERTION_ANAL},
)
def handle_vibrator_insertion_anal_off():
    """处理拔出肛门震动棒指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.VIBRATOR_INSERTION_ANAL_OFF
    character_data.state = constant.CharacterStatus.STATUS_VIBRATOR_INSERTION_ANAL_OFF
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.CLYSTER,
    constant.InstructType.SEX,
    _("灌肠"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.HAVE_CLYSTER_TOOLS,
     constant_promise.Premise.T_NOT_ENEMA,
     constant_promise.Premise.HAVE_ENEMAS},
)
def handle_clyster():
    """处理灌肠指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.CLYSTER
    character_data.state = constant.CharacterStatus.STATUS_CLYSTER
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.CLYSTER_END,
    constant.InstructType.SEX,
    _("拔出肛塞"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.HAVE_CLYSTER_TOOLS,
     constant_promise.Premise.T_ENEMA,
     },
)
def handle_clyster_end():
    """处理拔出肛塞指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.CLYSTER_END
    character_data.state = constant.CharacterStatus.STATUS_CLYSTER_END
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.ANAL_PLUG,
    constant.InstructType.SEX,
    _("肛塞_未实装"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.HAVE_ANAL_PLUG,
     constant_promise.Premise.TO_DO},
)
def handle_anal_plug():
    """处理肛塞指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.ANAL_PLUG
    character_data.state = constant.CharacterStatus.STATUS_ANAL_PLUG
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.ANAL_BEADS,
    constant.InstructType.SEX,
    _("塞入肛门拉珠"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.HAVE_ANAL_BEADS,
     constant_promise.Premise.TARGET_NOT_ANAL_BEADS},
)
def handle_anal_beads():
    """处理塞入肛门拉珠指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.ANAL_BEADS
    character_data.state = constant.CharacterStatus.STATUS_ANAL_BEADS
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.ANAL_BEADS_OFF,
    constant.InstructType.SEX,
    _("拔出肛门拉珠"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.HAVE_ANAL_BEADS,
     constant_promise.Premise.TARGET_NOW_ANAL_BEADS},
)
def handle_anal_beads_off():
    """处理拔出肛门拉珠指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.ANAL_BEADS_OFF
    character_data.state = constant.CharacterStatus.STATUS_ANAL_BEADS_OFF
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.MILKING_MACHINE_ON,
    constant.InstructType.SEX,
    _("装上搾乳机"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.T_LACTATION_1,
     constant_promise.Premise.TARGET_MILK_GE_30,
     constant_promise.Premise.TARGET_NOT_MILKING_MACHINE,
     constant_promise.Premise.HAVE_MILKING_MACHINE},
)
def handle_milking_machine_on():
    """处理装上搾乳机指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.MILKING_MACHINE_ON
    character_data.state = constant.CharacterStatus.STATUS_MILKING_MACHINE_ON
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.MILKING_MACHINE_OFF,
    constant.InstructType.SEX,
    _("取下搾乳机"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.T_LACTATION_1,
     constant_promise.Premise.TARGET_NOW_MILKING_MACHINE,
     constant_promise.Premise.HAVE_MILKING_MACHINE},
)
def handle_milking_machine_off():
    """处理取下搾乳机指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.MILKING_MACHINE_OFF
    character_data.state = constant.CharacterStatus.STATUS_MILKING_MACHINE_OFF
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.URINE_COLLECTOR,
    constant.InstructType.SEX,
    _("采尿器"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.TO_DO,
     constant_promise.Premise.HAVE_URINE_COLLECTOR},
)
def handle_urine_collector():
    """处理采尿器指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.URINE_COLLECTOR
    character_data.state = constant.CharacterStatus.STATUS_URINE_COLLECTOR
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.BONDAGE,
    constant.InstructType.SEX,
    _("绳子"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.TO_DO,
     constant_promise.Premise.HAVE_BONDAGE},
)
def handle_bondage():
    """处理绳子指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.BONDAGE
    character_data.state = constant.CharacterStatus.STATUS_BONDAGE
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.PATCH,
    constant.InstructType.SEX,
    _("眼罩"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.TO_DO,
     constant_promise.Premise.HAVE_PATCH},
)
def handle_patch():
    """处理眼罩指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.PATCH
    character_data.state = constant.CharacterStatus.STATUS_PATCH
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.WHIP,
    constant.InstructType.SEX,
    _("鞭子"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.TO_DO,
     constant_promise.Premise.HAVE_WHIP},
)
def handle_whip():
    """处理鞭子指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.WHIP
    character_data.state = constant.CharacterStatus.STATUS_WHIP
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.NEEDLE,
    constant.InstructType.SEX,
    _("针"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.TO_DO,
     constant_promise.Premise.HAVE_NEEDLE},
)
def handle_neddle():
    """处理针指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.NEEDLE
    character_data.state = constant.CharacterStatus.STATUS_NEEDLE
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.PUT_CONDOM,
    constant.InstructType.SEX,
    _("戴上避孕套"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.HAVE_CONDOM},
)
def handle_put_condom():
    """处理戴上避孕套指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.PUT_CONDOM
    character_data.state = constant.CharacterStatus.STATUS_PUT_CONDOM
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.SAFE_CANDLES,
    constant.InstructType.SEX,
    _("滴蜡"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.TO_DO,
     constant_promise.Premise.HAVE_SAFE_CANDLES},
)
def handle_safe_candles():
    """处理滴蜡指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.SAFE_CANDLES
    character_data.state = constant.CharacterStatus.STATUS_SAFE_CANDLES
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.BODY_LUBRICANT,
    constant.InstructType.SEX,
    _("润滑液"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.HAVE_BODY_LUBRICANT},
)
def handle_body_lubricant():
    """处理润滑液指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.BODY_LUBRICANT
    character_data.state = constant.CharacterStatus.STATUS_BODY_LUBRICANT
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.PHILTER,
    constant.InstructType.SEX,
    _("媚药"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.HAVE_PHILTER},
)
def handle_philter():
    """处理媚药指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.PHILTER
    character_data.state = constant.CharacterStatus.STATUS_PHILTER
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.ENEMAS,
    constant.InstructType.SEX,
    _("灌肠液_未实装"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.HAVE_ENEMAS,
     constant_promise.Premise.TO_DO},
)
def handle_enemas():
    """处理灌肠液指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)


@add_instruct(
    constant.Instruct.DIURETICS_ONCE,
    constant.InstructType.SEX,
    _("一次性利尿剂"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.HAVE_DIURETICS_ONCE},
)
def handle_diuretics_once():
    """处理一次性利尿剂指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.DIURETICS_ONCE
    character_data.state = constant.CharacterStatus.STATUS_DIURETICS_ONCE
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.DIURETICS_PERSISTENT,
    constant.InstructType.SEX,
    _("持续性利尿剂"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.HAVE_DIURETICS_PERSISTENT},
)
def handle_diuretics_persistent():
    """处理持续性利尿剂指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.DIURETICS_PERSISTENT
    character_data.state = constant.CharacterStatus.STATUS_DIURETICS_PERSISTENT
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.SLEEPING_PILLS,
    constant.InstructType.SEX,
    _("安眠药"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.HAVE_SLEEPING_PILLS},
)
def handle_sleeping_pills():
    """处理安眠药指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.SLEEPING_PILLS
    character_data.state = constant.CharacterStatus.STATUS_SLEEPING_PILLS
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.CLOMID,
    constant.InstructType.SEX,
    _("排卵促进药"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.HAVE_CLOMID},
)
def handle_clomid():
    """处理排卵促进药指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    if character.calculation_instuct_judege(0, character_data.target_character_id, _("性交"))[0]:
        character_data.behavior.behavior_id = constant.Behavior.CLOMID
        character_data.state = constant.CharacterStatus.STATUS_CLOMID
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.BIRTH_CONTROL_PILLS_BEFORE,
    constant.InstructType.SEX,
    _("事前避孕药"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.HAVE_BIRTH_CONTROL_PILLS_BEFORE},
)
def handle_birth_control_pills_before():
    """处理事前避孕药指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.BIRTH_CONTROL_PILLS_BEFORE
    character_data.state = constant.CharacterStatus.STATUS_BIRTH_CONTROL_PILLS_BEFORE
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.BIRTH_CONTROL_PILLS_AFTER,
    constant.InstructType.SEX,
    _("事后避孕药"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.HAVE_BIRTH_CONTROL_PILLS_AFTER},
)
def handle_birth_control_pills_after():
    """处理事后避孕药指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.BIRTH_CONTROL_PILLS_AFTER
    character_data.state = constant.CharacterStatus.STATUS_BIRTH_CONTROL_PILLS_AFTER
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.NORMAL_SEX,
    constant.InstructType.SEX,
    _("正常位"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.PLACE_FURNITURE_3,
     constant_promise.Premise.TARGET_NOT_VIBRATOR_INSERTION},
)
def handle_normal_sex():
    """处理正常位指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    if character.calculation_instuct_judege(0, character_data.target_character_id, _("性交"))[0]:
        character_data.behavior.behavior_id = constant.Behavior.NORMAL_SEX
        character_data.state = constant.CharacterStatus.STATUS_NORMAL_SEX
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.BACK_SEX,
    constant.InstructType.SEX,
    _("背后位"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.PLACE_FURNITURE_3,
     constant_promise.Premise.TARGET_NOT_VIBRATOR_INSERTION},
)
def handle_back_sex():
    """处理背后位指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    if character.calculation_instuct_judege(0, character_data.target_character_id, _("性交"))[0]:
        character_data.behavior.behavior_id = constant.Behavior.BACK_SEX
        character_data.state = constant.CharacterStatus.STATUS_BACK_SEX
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.RIDING_SEX,
    constant.InstructType.SEX,
    _("骑乘位"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.PLACE_FURNITURE_3,
     constant_promise.Premise.TARGET_NOT_VIBRATOR_INSERTION},
)
def handle_riding_sex():
    """处理骑乘位指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    if character.calculation_instuct_judege(0, character_data.target_character_id, _("性交"))[0]:
        character_data.behavior.behavior_id = constant.Behavior.RIDING_SEX
        character_data.state = constant.CharacterStatus.STATUS_RIDING_SEX
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.FACE_SEAT_SEX,
    constant.InstructType.SEX,
    _("对面座位"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.PLACE_FURNITURE_GE_2,
     constant_promise.Premise.TARGET_NOT_VIBRATOR_INSERTION},
)
def handle_face_seat_sex():
    """处理对面座位指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    if character.calculation_instuct_judege(0, character_data.target_character_id, _("性交"))[0]:
        character_data.behavior.behavior_id = constant.Behavior.FACE_SEAT_SEX
        character_data.state = constant.CharacterStatus.STATUS_FACE_SEAT_SEX
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.BACK_SEAT_SEX,
    constant.InstructType.SEX,
    _("背面座位"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.PLACE_FURNITURE_GE_2,
     constant_promise.Premise.TARGET_NOT_VIBRATOR_INSERTION},
)
def handle_back_seat_sex():
    """处理背面座位指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    if character.calculation_instuct_judege(0, character_data.target_character_id, _("性交"))[0]:
        character_data.behavior.behavior_id = constant.Behavior.BACK_SEAT_SEX
        character_data.state = constant.CharacterStatus.STATUS_BACK_SEAT_SEX
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.FACE_STAND_SEX,
    constant.InstructType.SEX,
    _("对面立位"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.TARGET_NOT_VIBRATOR_INSERTION},
)
def handle_face_stand_sex():
    """处理对面立位指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    if character.calculation_instuct_judege(0, character_data.target_character_id, _("性交"))[0]:
        character_data.behavior.behavior_id = constant.Behavior.FACE_STAND_SEX
        character_data.state = constant.CharacterStatus.STATUS_FACE_STAND_SEX
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.BACK_STAND_SEX,
    constant.InstructType.SEX,
    _("背面立位"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.TARGET_NOT_VIBRATOR_INSERTION},
)
def handle_back_stand_sex():
    """处理背面立位指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    if character.calculation_instuct_judege(0, character_data.target_character_id, _("性交"))[0]:
        character_data.behavior.behavior_id = constant.Behavior.BACK_STAND_SEX
        character_data.state = constant.CharacterStatus.STATUS_BACK_STAND_SEX
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.STIMULATE_G_POINT,
    constant.InstructType.SEX,
    _("刺激G点"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.LAST_CMD_SEX,
     constant_promise.Premise.TARGET_NOT_VIBRATOR_INSERTION,
     constant_promise.Premise.TECHNIQUE_GE_3},
)
def handle_stimulate_g_point():
    """处理刺激G点指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    if character.calculation_instuct_judege(0, character_data.target_character_id, _("性交"))[0]:
        character_data.behavior.behavior_id = constant.Behavior.STIMULATE_G_POINT
        character_data.state = constant.CharacterStatus.STATUS_STIMULATE_G_POINT
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.WOMB_OS_CARESS,
    constant.InstructType.SEX,
    _("玩弄子宫口"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.LAST_CMD_SEX,
     constant_promise.Premise.TARGET_NOT_VIBRATOR_INSERTION,
     constant_promise.Premise.TECHNIQUE_GE_3},
)
def handle_womb_os_caress():
    """处理玩弄子宫口指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    if character.calculation_instuct_judege(0, character_data.target_character_id, _("性交"))[0]:
        character_data.behavior.behavior_id = constant.Behavior.WOMB_OS_CARESS
        character_data.state = constant.CharacterStatus.STATUS_WOMB_OS_CARESS
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.WOMB_INSERTION,
    constant.InstructType.SEX,
    _("插入子宫"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.LAST_CMD_SEX,
     constant_promise.Premise.TARGET_NOT_VIBRATOR_INSERTION,
     constant_promise.Premise.TECHNIQUE_GE_3},
)
def handle_womb_insertion():
    """处理插入子宫指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    if character.calculation_instuct_judege(0, character_data.target_character_id, _("性交"))[0]:
        character_data.behavior.behavior_id = constant.Behavior.WOMB_INSERTION
        character_data.state = constant.CharacterStatus.STATUS_WOMB_INSERTION
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.NORMAL_ANAL_SEX,
    constant.InstructType.SEX,
    _("正常位肛交"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.PLACE_FURNITURE_3,
     constant_promise.Premise.TARGET_NOT_VIBRATOR_INSERTION_ANAL},
)
def handle_normal_anal_sex():
    """处理正常位肛交指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    if character.calculation_instuct_judege(0, character_data.target_character_id, _("A性交"))[0]:
        character_data.behavior.behavior_id = constant.Behavior.NORMAL_ANAL_SEX
        character_data.state = constant.CharacterStatus.STATUS_NORMAL_ANAL_SEX
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.BACK_ANAL_SEX,
    constant.InstructType.SEX,
    _("后背位肛交"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.PLACE_FURNITURE_3,
     constant_promise.Premise.TARGET_NOT_VIBRATOR_INSERTION_ANAL},
)
def handle_back_anal_sex():
    """处理后背位肛交指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    if character.calculation_instuct_judege(0, character_data.target_character_id, _("A性交"))[0]:
        character_data.behavior.behavior_id = constant.Behavior.BACK_ANAL_SEX
        character_data.state = constant.CharacterStatus.STATUS_BACK_ANAL_SEX
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.RIDING_ANAL_SEX,
    constant.InstructType.SEX,
    _("骑乘位肛交"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.PLACE_FURNITURE_3,
     constant_promise.Premise.TARGET_NOT_VIBRATOR_INSERTION_ANAL},
)
def handle_riding_anal_sex():
    """处理骑乘位肛交指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    if character.calculation_instuct_judege(0, character_data.target_character_id, _("A性交"))[0]:
        character_data.behavior.behavior_id = constant.Behavior.RIDING_ANAL_SEX
        character_data.state = constant.CharacterStatus.STATUS_RIDING_ANAL_SEX
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.FACE_SEAT_ANAL_SEX,
    constant.InstructType.SEX,
    _("对面座位肛交"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.TARGET_NOT_VIBRATOR_INSERTION_ANAL,
     constant_promise.Premise.PLACE_FURNITURE_2},
)
def handle_face_seat_anal_sex():
    """处理对面座位肛交指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    if character.calculation_instuct_judege(0, character_data.target_character_id, _("A性交"))[0]:
        character_data.behavior.behavior_id = constant.Behavior.FACE_SEAT_ANAL_SEX
        character_data.state = constant.CharacterStatus.STATUS_FACE_SEAT_ANAL_SEX
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.BACK_SEAT_ANAL_SEX,
    constant.InstructType.SEX,
    _("背面座位肛交"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.PLACE_FURNITURE_2,
     constant_promise.Premise.TARGET_NOT_VIBRATOR_INSERTION_ANAL},
)
def handle_back_seat_anal_sex():
    """处理背面座位肛交指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    if character.calculation_instuct_judege(0, character_data.target_character_id, _("A性交"))[0]:
        character_data.behavior.behavior_id = constant.Behavior.BACK_SEAT_ANAL_SEX
        character_data.state = constant.CharacterStatus.STATUS_BACK_SEAT_ANAL_SEX
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.FACE_STAND_ANAL_SEX,
    constant.InstructType.SEX,
    _("对面立位肛交"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.TARGET_NOT_VIBRATOR_INSERTION_ANAL},
)
def handle_face_stand_anal_sex():
    """处理对面立位肛交指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    if character.calculation_instuct_judege(0, character_data.target_character_id, _("A性交"))[0]:
        character_data.behavior.behavior_id = constant.Behavior.FACE_STAND_ANAL_SEX
        character_data.state = constant.CharacterStatus.STATUS_FACE_STAND_ANAL_SEX
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.BACK_STAND_ANAL_SEX,
    constant.InstructType.SEX,
    _("背面立位肛交"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.TARGET_NOT_VIBRATOR_INSERTION_ANAL},
)
def handle_back_stand_anal_sex():
    """处理背面立位肛交指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    if character.calculation_instuct_judege(0, character_data.target_character_id, _("A性交"))[0]:
        character_data.behavior.behavior_id = constant.Behavior.BACK_STAND_ANAL_SEX
        character_data.state = constant.CharacterStatus.STATUS_BACK_STAND_ANAL_SEX
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.STIMULATE_SIGMOID_COLON,
    constant.InstructType.SEX,
    _("玩弄s状结肠"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.TARGET_NOT_VIBRATOR_INSERTION_ANAL,
     constant_promise.Premise.LAST_CMD_A_SEX,
     constant_promise.Premise.TECHNIQUE_GE_3},
)
def handle_stimulate_sigmoid_colon():
    """处理玩弄s状结肠指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    if character.calculation_instuct_judege(0, character_data.target_character_id, _("A性交"))[0]:
        character_data.behavior.behavior_id = constant.Behavior.STIMULATE_SIGMOID_COLON
        character_data.state = constant.CharacterStatus.STATUS_STIMULATE_SIGMOID_COLON
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.STIMULATE_VAGINA,
    constant.InstructType.SEX,
    _("隔着刺激阴道"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.TARGET_NOT_VIBRATOR_INSERTION_ANAL,
     constant_promise.Premise.LAST_CMD_A_SEX,
     constant_promise.Premise.TECHNIQUE_GE_3},
)
def handle_stimulate_vagina():
    """处理隔着刺激阴道指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    if character.calculation_instuct_judege(0, character_data.target_character_id, _("A性交"))[0]:
        character_data.behavior.behavior_id = constant.Behavior.STIMULATE_VAGINA
        character_data.state = constant.CharacterStatus.STATUS_STIMULATE_VAGINA
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.DOUBLE_PENETRATION,
    constant.InstructType.SEX,
    _("二穴插入_未实装"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.TECHNIQUE_GE_5},
)
def handle_double_penetration():
    """处理二穴插入指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)


@add_instruct(
    constant.Instruct.URETHRAL_SWAB,
    constant.InstructType.SEX,
    _("尿道棉棒"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.HAVE_COTTON_STICK},
)
def handle_urethral_swab():
    """处理尿道棉棒指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.URETHRAL_SWAB
    character_data.state = constant.CharacterStatus.STATUS_URETHRAL_SWAB
    character_data.behavior.duration = 10
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.PISSING_PLAY,
    constant.InstructType.SEX,
    _("放尿play_未实装"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.TO_DO},
)
def handle_pissing_play():
    """处理放尿play指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)


@add_instruct(
    constant.Instruct.URETHRAL_INSERTION,
    constant.InstructType.SEX,
    _("尿道插入_未实装"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.TECHNIQUE_GE_5},
)
def handle_urethral_insertion():
    """处理尿道插入指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    # if character.calculation_instuct_judege(0,character_data.target_character_id,"U性交")[0]:
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)


@add_instruct(
    constant.Instruct.BEAT_BREAST,
    constant.InstructType.SEX,
    _("打胸部_未实装"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.TO_DO},
)
def handle_beat_breast():
    """处理打胸部指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)


@add_instruct(
    constant.Instruct.SPANKING,
    constant.InstructType.SEX,
    _("打屁股"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H},
)
def handle_spanking():
    """处理打屁股指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)


@add_instruct(
    constant.Instruct.SHAME_PLAY,
    constant.InstructType.SEX,
    _("羞耻play_未实装"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.TO_DO},
)
def handle_shame_play():
    """处理羞耻play指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)


@add_instruct(
    constant.Instruct.BUNDLED_PLAY,
    constant.InstructType.SEX,
    _("拘束play_未实装"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.TO_DO},
)
def handle_bundled_play():
    """处理拘束play指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)


@add_instruct(
    constant.Instruct.TAKE_SHOWER_H,
    constant.InstructType.SEX,
    _("淋浴_未实装"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.TO_DO},
)
def handle_take_shower():
    """处理淋浴指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)


@add_instruct(
    constant.Instruct.BUBBLE_BATH,
    constant.InstructType.SEX,
    _("泡泡浴_未实装"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.TO_DO},
)
def handle_bubble_bath():
    """处理泡泡浴指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)


@add_instruct(
    constant.Instruct.CHANGE_TOP_AND_BOTTOM,
    constant.InstructType.SEX,
    _("交给对方_未实装"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.TO_DO},
)
def handle_change_top_and_bottom():
    """处理交给对方指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)


@add_instruct(
    constant.Instruct.GIVE_BLOWJOB,
    constant.InstructType.SEX,
    _("给对方口交_未实装"),
    {constant_promise.Premise.HAVE_TARGET,
     constant_promise.Premise.IS_H,
     constant_promise.Premise.TO_DO},
)
def handle_give_blowjob():
    """处理给对方口交指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)


@add_instruct(
    constant.Instruct.UNDRESS,
    constant.InstructType.SEX,
    _("脱衣服"),
    {
        constant_promise.Premise.HAVE_TARGET,
        constant_promise.Premise.IS_H,
    })
def handle_undress():
    """处理脱衣服指令"""
    cache.now_panel_id = constant.Panel.UNDRESS
