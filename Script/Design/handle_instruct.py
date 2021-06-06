import random
import time
import queue
from functools import wraps
from typing import Set, List
from types import FunctionType
from threading import Thread
from Script.Core import constant, cache_control, game_type, get_text, save_handle
from Script.Design import update, character, attr_calculation, course
from Script.UI.Panel import see_character_info_panel, see_save_info_panel
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
            save_handle.establish_save("auto")
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


@add_instruct(constant.Instruct.REST, constant.InstructType.DAILY, _("休息"), {})
def handle_rest():
    """处理休息指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 10
    character_data.behavior.behavior_id = constant.Behavior.REST
    character_data.state = constant.CharacterStatus.STATUS_REST
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.BUY_FOOD, constant.InstructType.DAILY, _("购买食物"), {constant.Premise.IN_CAFETERIA}
)
def handle_buy_food():
    """处理购买食物指令"""
    cache.now_panel_id = constant.Panel.FOOD_SHOP


@add_instruct(constant.Instruct.EAT, constant.InstructType.DAILY, _("进食"), {constant.Premise.HAVE_FOOD})
def handle_eat():
    """处理进食指令"""
    cache.now_panel_id = constant.Panel.FOOD_BAG


@add_instruct(constant.Instruct.MOVE, constant.InstructType.SYSTEM, _("移动"), {})
def handle_move():
    """处理移动指令"""
    cache.now_panel_id = constant.Panel.SEE_MAP


@add_instruct(
    constant.Instruct.SEE_ATTR, constant.InstructType.SYSTEM, _("查看属性"), {constant.Premise.HAVE_TARGET}
)
def handle_see_attr():
    """查看属性"""
    see_character_info_panel.line_feed.draw()
    now_draw = see_character_info_panel.SeeCharacterInfoInScenePanel(
        cache.character_data[0].target_character_id, width
    )
    now_draw.draw()


@add_instruct(constant.Instruct.SEE_OWNER_ATTR, constant.InstructType.SYSTEM, _("查看自身属性"), {})
def handle_see_owner_attr():
    """查看自身属性"""
    see_character_info_panel.line_feed.draw()
    now_draw = see_character_info_panel.SeeCharacterInfoInScenePanel(0, width)
    now_draw.draw()


@add_instruct(
    constant.Instruct.CHAT, constant.InstructType.DAILY, _("聊天"), {constant.Premise.HAVE_TARGET}
)
def handle_chat():
    """处理聊天指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data = cache.character_data[0]
    character_data.behavior.duration = 10
    character_data.behavior.behavior_id = constant.Behavior.CHAT
    character_data.state = constant.CharacterStatus.STATUS_CHAT
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.BUY_ITEM, constant.InstructType.DAILY, _("购买道具"), {constant.Premise.IN_SHOP}
)
def handle_buy_item():
    """处理购买道具指令"""
    cache.now_panel_id = constant.Panel.ITEM_SHOP



# @add_instruct(
#     constant.Instruct.PLAY_PIANO,
#     constant.InstructType.PLAY,
#     _("弹钢琴"),
#     {constant.Premise.IN_MUSIC_ROOM},
# )
# def handle_play_piano():
#     """处理弹钢琴指令"""
#     character.init_character_behavior_start_time(0, cache.game_time)
#     character_data = cache.character_data[0]
#     character_data.behavior.duration = 30
#     character_data.behavior.behavior_id = constant.Behavior.PLAY_PIANO
#     character_data.state = constant.CharacterStatus.STATUS_PLAY_PIANO
#     update.game_update_flow(30)


@add_instruct(
    constant.Instruct.TOUCH_HEAD,
    constant.InstructType.OBSCENITY,
    _("摸头"),
    {constant.Premise.HAVE_TARGET},
)
def handle_touch_head():
    """处理摸头指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data = cache.character_data[0]
    character_data.behavior.duration = 2
    character_data.behavior.behavior_id = constant.Behavior.TOUCH_HEAD
    character_data.state = constant.CharacterStatus.STATUS_TOUCH_HEAD
    update.game_update_flow(2)


@add_instruct(constant.Instruct.SAVE, constant.InstructType.SYSTEM, _("读写存档"), {})
def handle_save():
    """处理读写存档指令"""
    now_panel = see_save_info_panel.SeeSaveListPanel(width, 1)
    now_panel.draw()


@add_instruct(constant.Instruct.SLEEP, constant.InstructType.DAILY, _("睡觉"), {constant.Premise.IN_DORMITORY})
def handle_sleep():
    """处理睡觉指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 480
    character_data.behavior.behavior_id = constant.Behavior.SLEEP
    character_data.state = constant.CharacterStatus.STATUS_SLEEP
    cache.wframe_mouse.w_frame_skip_wait_mouse = 1
    update.game_update_flow(480)


# @add_instruct(
#     constant.Instruct.DRINK_SPRING, constant.InstructType.DAILY, _("喝泉水"), {constant.Premise.IN_FOUNTAIN}
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
    constant.Instruct.EMBRACE, constant.InstructType.OBSCENITY, _("拥抱"), {constant.Premise.HAVE_TARGET}
)
def handle_embrace():
    """处理拥抱指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 3
    character_data.behavior.behavior_id = constant.Behavior.EMBRACE
    character_data.state = constant.CharacterStatus.STATUS_EMBRACE
    update.game_update_flow(3)


@add_instruct(
    constant.Instruct.KISS,
    constant.InstructType.OBSCENITY,
    _("亲吻"),
    {constant.Premise.HAVE_TARGET},
)
def handle_kiss():
    """处理亲吻指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 2
    character_data.behavior.behavior_id = constant.Behavior.KISS
    character_data.state = constant.CharacterStatus.STATUS_KISS
    update.game_update_flow(2)


@add_instruct(
    constant.Instruct.HAND_IN_HAND,
    constant.InstructType.OBSCENITY,
    _("牵手"),
    {constant.Premise.HAVE_TARGET},
)
def handle_handle_in_handle():
    """处理牵手指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 10
    character_data.behavior.behavior_id = constant.Behavior.HAND_IN_HAND
    character_data.state = constant.CharacterStatus.STATUS_HAND_IN_HAND
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.STROKE,
    constant.InstructType.DAILY,
    _("身体接触"),
    {constant.Premise.HAVE_TARGET},
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
    constant.Instruct.TOUCH_BREAST,
    constant.InstructType.OBSCENITY,
    _("摸胸"),
    {constant.Premise.HAVE_TARGET},
)
def handle_touch_breast():
    """处理摸胸指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 10
    character_data.behavior.behavior_id = constant.Behavior.TOUCH_BREAST
    character_data.state = constant.CharacterStatus.STATUS_TOUCH_BREAST
    update.game_update_flow(10)


# @add_instruct(
#     constant.Instruct.COLLECTION_CHARACTER,
#     constant.InstructType.SYSTEM,
#     _("收藏角色"),
#     {constant.Premise.TARGET_IS_NOT_COLLECTION, constant.Premise.TARGET_NO_PLAYER},
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
#     {constant.Premise.TARGET_IS_COLLECTION, constant.Premise.TARGET_NO_PLAYER},
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
#     {constant.Premise.UN_COLLECTION_SYSTEM},
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
#     {constant.Premise.IS_COLLECTION_SYSTEM},
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
#         constant.Premise.ATTEND_CLASS_TODAY,
#         constant.Premise.IN_CLASSROOM,
#         constant.Premise.IN_CLASS_TIME,
#         constant.Premise.IS_STUDENT,
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
#         constant.Premise.ATTEND_CLASS_TODAY,
#         constant.Premise.IN_CLASSROOM,
#         constant.Premise.IN_CLASS_TIME,
#         constant.Premise.IS_TEACHER,
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
#     {constant.Premise.HAVE_GUITAR},
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
#         constant.Premise.IN_CLASSROOM,
#         constant.Premise.IS_STUDENT,
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


#进入自加阶段#

@add_instruct(
    constant.Instruct.WAIT,
    constant.InstructType.DAILY,
    _("等待五分钟"),
    {},
)
def handle_wait():
    """处理等待五分钟指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.MAKE_TEA,
    constant.InstructType.DAILY,
    _("泡茶"),
    {constant.Premise.HAVE_TARGET},
)
def handle_make_tea():
    """处理泡茶指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.MAKE_TEA_ADD,
    constant.InstructType.DAILY,
    _("泡茶（加料）"),
    {constant.Premise.HAVE_TARGET},
)
def handle_make_tea_add():
    """处理泡茶（加料）指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.MAKE_FOOD,
    constant.InstructType.DAILY,
    _("做饭"),
    {constant.Premise.HAVE_TARGET},
)
def handle_make_food():
    """做饭"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.FOLLOWED,
    constant.InstructType.DAILY,
    _("使跟随"),
    {constant.Premise.HAVE_TARGET},
)
def handle_followed():
    """处理使跟随指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.APOLOGIZE,
    constant.InstructType.DAILY,
    _("道歉"),
    {constant.Premise.HAVE_TARGET},
)
def handle_apologize():
    """处理道歉指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.LISTEN_COMPLAINT,
    constant.InstructType.DAILY,
    _("听牢骚"),
    {constant.Premise.HAVE_TARGET},
)
def handle_listen_complaint():
    """处理听牢骚指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.PRAY,
    constant.InstructType.DAILY,
    _("祈愿"),
    {constant.Premise.HAVE_TARGET},
)
def handle_pray():
    """处理祈愿指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.LISTEN_MISSION,
    constant.InstructType.WORK,
    _("听取委托"),
    {constant.Premise.HAVE_TARGET},
)
def handle_listen_mission():
    """处理听取委托指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.COLLCET_PANTY,
    constant.InstructType.DAILY,
    _("收起内裤"),
    {constant.Premise.HAVE_TARGET},
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
    _("邀请约会"),
    {constant.Premise.HAVE_TARGET},
)
def handle_ask_date():
    """处理邀请约会指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.CONFESSION,
    constant.InstructType.DAILY,
    _("告白"),
    {constant.Premise.HAVE_TARGET},
)
def handle_confession():
    """处理告白指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.DRINK_ALCOHOL,
    constant.InstructType.DAILY,
    _("劝酒"),
    {constant.Premise.HAVE_TARGET},
)
def handle_drink_alcohol():
    """处理劝酒指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.SINGING,
    constant.InstructType.DAILY,
    _("唱歌"),
    {})
def handle_singing():
    """处理唱歌指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data = cache.character_data[0]
    character_data.behavior.duration = 5
    character_data.behavior.behavior_id = constant.Behavior.SINGING
    character_data.state = constant.CharacterStatus.STATUS_SINGING
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.PLAY_INSTRUMENT,
    constant.InstructType.DAILY,
    _("演奏乐器"),
    {constant.Premise.HAVE_TARGET},
)
def handle_play_instrument():
    """处理演奏乐器指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

#以下为猥亵#
@add_instruct(
    constant.Instruct.TOUCH_BUTTOCKS,
    constant.InstructType.OBSCENITY,
    _("摸屁股"),
    {constant.Premise.HAVE_TARGET},
)
def handle_touch_buttocks():
    """处理摸屁股指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.TOUCH_EARS,
    constant.InstructType.OBSCENITY,
    _("摸耳朵"),
    {constant.Premise.HAVE_TARGET},
)
def handle_touch_ears():
    """处理摸耳朵指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.TOUCH_HORN,
    constant.InstructType.OBSCENITY,
    _("摸角"),
    {constant.Premise.HAVE_TARGET},
)
def handle_touch_horn():
    """处理摸角指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.TOUCH_TAIL,
    constant.InstructType.OBSCENITY,
    _("摸尾巴"),
    {constant.Premise.HAVE_TARGET},
)
def handle_touch_tail():
    """处理摸尾巴指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.TOUCH_RING,
    constant.InstructType.OBSCENITY,
    _("摸光环"),
    {constant.Premise.HAVE_TARGET},
)
def handle_touch_ring():
    """处理摸光环指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.TOUCH_WING,
    constant.InstructType.OBSCENITY,
    _("摸光翼"),
    {constant.Premise.HAVE_TARGET},
)
def handle_touch_wing():
    """处理摸光翼指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.LAP_PILLOW,
    constant.InstructType.OBSCENITY,
    _("膝枕"),
    {constant.Premise.HAVE_TARGET},
)
def handle_lap_pillow():
    """处理膝枕指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.RAISE_SKIRT,
    constant.InstructType.OBSCENITY,
    _("掀起裙子"),
    {constant.Premise.HAVE_TARGET},
)
def handle_raise_skirt():
    """处理掀起裙子指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.TOUCH_CLITORIS,
    constant.InstructType.OBSCENITY,
    _("阴蒂爱抚"),
    {constant.Premise.HAVE_TARGET},
)
def handle_touch_clitoris():
    """处理阴蒂爱抚指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.TOUCH_VAGINA,
    constant.InstructType.OBSCENITY,
    _("手指插入（V）"),
    {constant.Premise.HAVE_TARGET},
)
def handle_touch_vagina():
    """处理手指插入（V）指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.TOUCH_ANUS,
    constant.InstructType.OBSCENITY,
    _("手指插入（A）"),
    {constant.Premise.HAVE_TARGET},
)
def handle_touch_anus():
    """处理手指插入（A）指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

#以下为性爱#


@add_instruct(
    constant.Instruct.MAKING_OUT,
    constant.InstructType.SEX,
    _("身体爱抚"),
    {constant.Premise.HAVE_TARGET},
)
def handle_making_out():
    """处理身体爱抚指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.KISS_H,
    constant.InstructType.SEX,
    _("接吻"),
    {constant.Premise.HAVE_TARGET},
)
def handle_kiss_h():
    """处理接吻指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.BREAST_CARESS,
    constant.InstructType.SEX,
    _("胸爱抚"),
    {constant.Premise.HAVE_TARGET},
)
def handle_breast_caress():
    """处理胸爱抚指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.TWIDDLE_NIPPLES,
    constant.InstructType.SEX,
    _("玩弄乳头"),
    {constant.Premise.HAVE_TARGET},
)
def handle_twiddle_nipples():
    """处理玩弄乳头指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.BREAST_SUCKING,
    constant.InstructType.SEX,
    _("舔吸乳头"),
    {constant.Premise.HAVE_TARGET},
)
def handle_breast_sucking():
    """处理舔吸乳头指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.CLIT_CARESS,
    constant.InstructType.SEX,
    _("阴蒂爱抚"),
    {constant.Premise.HAVE_TARGET},
)
def handle_cilt_caress():
    """处理阴蒂爱抚指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.OPEN_LABIA,
    constant.InstructType.SEX,
    _("掰开阴唇"),
    {constant.Premise.HAVE_TARGET},
)
def handle_open_labia():
    """处理掰开阴唇指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.OPEN_ANUS,
    constant.InstructType.SEX,
    _("掰开肛门"),
    {constant.Premise.HAVE_TARGET},
)
def handle_open_anus():
    """处理掰开肛门指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.CUNNILINGUS,
    constant.InstructType.SEX,
    _("舔阴"),
    {constant.Premise.HAVE_TARGET},
)
def handle_cunnilingus():
    """处理舔阴指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.LICK_ANAL,
    constant.InstructType.SEX,
    _("舔肛"),
    {constant.Premise.HAVE_TARGET},
)
def handle_lict_anal():
    """处理舔肛指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.FINGER_INSERTION,
    constant.InstructType.SEX,
    _("手指插入"),
    {constant.Premise.HAVE_TARGET},
)
def handle_finger_insertion():
    """处理手指插入指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.ANAL_CARESS,
    constant.InstructType.SEX,
    _("肛门爱抚"),
    {constant.Premise.HAVE_TARGET},
)
def handle_anal_caress():
    """处理肛门爱抚指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)
