from Script.UI.Flow.make_food_flow import make_food_flow
import random
import time
import queue
from functools import wraps
from typing import Set, List
from types import FunctionType
from threading import Thread
from Script.Core import constant, cache_control, game_type, get_text, save_handle
from Script.Design import update, character, attr_calculation
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
    constant.Instruct.BUY_FOOD, constant.InstructType.DAILY, _("购买食物"),
    {constant.Premise.IN_DINING_HALL,
    constant.Premise.NOT_H}
)
def handle_buy_food():
    """处理购买食物指令"""
    cache.now_panel_id = constant.Panel.FOOD_SHOP


@add_instruct(
    constant.Instruct.EAT, constant.InstructType.DAILY, _("进食"),
    {constant.Premise.HAVE_FOOD,
    constant.Premise.NOT_H}
)
def handle_eat():
    """处理进食指令"""
    cache.now_panel_id = constant.Panel.FOOD_BAG


@add_instruct(
    constant.Instruct.MOVE, constant.InstructType.SYSTEM, _("移动"),
    {constant.Premise.NOT_H}
)
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
    constant.Instruct.CHAT, constant.InstructType.DAILY, _("聊天"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.NOT_H}
)
def handle_chat():
    """处理聊天指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data = cache.character_data[0]
    character_data.behavior.duration = 5
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.talk_count > character_data.ability[25] + 1:
        character_data.behavior.behavior_id = constant.Behavior.CHAT_FAILED
        character_data.state = constant.CharacterStatus.STATUS_CHAT_FAILED
    else:
        character_data.behavior.behavior_id = constant.Behavior.CHAT
        character_data.state = constant.CharacterStatus.STATUS_CHAT
    target_data.talk_count += 1
    # print("聊天计数器+1，现在为 ：",target_data.talk_count)
    update.game_update_flow(5)


@add_instruct(
    constant.Instruct.BUY_ITEM, constant.InstructType.DAILY, _("购买道具"),
    {constant.Premise.IN_SHOP,
    constant.Premise.NOT_H}
)
def handle_buy_item():
    """处理购买道具指令"""
    cache.now_panel_id = constant.Panel.ITEM_SHOP


@add_instruct(
    constant.Instruct.ABL_UP, constant.InstructType.SYSTEM, _("属性上升"), {constant.Premise.HAVE_TARGET}
)
def handle_abl_up():
    """处理属性上升"""
    see_character_info_panel.line_feed.draw()
    now_draw = see_character_info_panel.Character_abi_up_main_Handle(
        cache.character_data[0].target_character_id, width
    )
    now_draw.draw()


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


@add_instruct(constant.Instruct.SAVE, constant.InstructType.SYSTEM, _("读写存档"), {})
def handle_save():
    """处理读写存档指令"""
    now_panel = see_save_info_panel.SeeSaveListPanel(width, 1)
    now_panel.draw()


@add_instruct(
    constant.Instruct.SLEEP, constant.InstructType.DAILY, _("睡觉"),
    {constant.Premise.IN_DORMITORY,
    constant.Premise.NOT_H}
    )
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
    constant.Instruct.EMBRACE, constant.InstructType.OBSCENITY, _("拥抱"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.NOT_H}
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
    {constant.Premise.HAVE_TARGET,
    constant.Premise.NOT_H},
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
    constant.Instruct.STROKE,
    constant.InstructType.DAILY,
    _("身体接触"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.NOT_H},
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
    {constant.Premise.HAVE_TARGET,
    constant.Premise.NOT_H},
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
    {constant.Premise.NOT_H},
)
def handle_wait():
    """处理等待五分钟指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.MAKE_COFFEE,
    constant.InstructType.DAILY,
    _("冲咖啡"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.NOT_H},
)
def handle_make_coffee():
    """处理冲咖啡指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 15
    character_data.behavior.behavior_id = constant.Behavior.MAKE_COFFEE
    character_data.state = constant.CharacterStatus.STATUS_MAKE_COFFEE
    update.game_update_flow(15)

@add_instruct(
    constant.Instruct.MAKE_COFFEE_ADD,
    constant.InstructType.DAILY,
    _("冲咖啡（加料）"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.NOT_H},
)
def handle_make_coffee_add():
    """处理冲咖啡（加料）指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 15
    update.game_update_flow(15)

@add_instruct(
    constant.Instruct.MAKE_FOOD,
    constant.InstructType.DAILY,
    _("做饭"),
    {constant.Premise.IN_KITCHEN,
},
)
def handle_make_food():
    """做饭"""
    cache.now_panel_id = constant.Panel.MAKE_FOOD

@add_instruct(
    constant.Instruct.FOLLOW,
    constant.InstructType.DAILY,
    _("请求同行"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.NOT_H,
    constant.Premise.NOT_FOLLOW},
)
def handle_followed():
    """处理请求同行指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    target_data.talent[400] = 1
    # print("进入同行模式")
    # print("跟随指令交互目标的NPC编号为：",character_data.target_character_id)
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.END_FOLLOW,
    constant.InstructType.DAILY,
    _("结束同行"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.NOT_H,
    constant.Premise.IS_FOLLOW},
)
def handle_end_followed():
    """处理结束同行指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    target_data.talent[400] = 0
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.APOLOGIZE,
    constant.InstructType.DAILY,
    _("道歉"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.NOT_H},
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
    {constant.Premise.HAVE_TARGET,
    constant.Premise.NOT_H},
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
    {constant.Premise.HAVE_TARGET,
    constant.Premise.NOT_H},
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
    {constant.Premise.HAVE_TARGET,
    constant.Premise.NOT_H},
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
    {constant.Premise.HAVE_TARGET,
    constant.Premise.NOT_H},
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
    {constant.Premise.HAVE_TARGET,
    constant.Premise.NOT_H},
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
    {constant.Premise.HAVE_TARGET,
    constant.Premise.NOT_H},
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
    {constant.Premise.HAVE_TARGET,
    constant.Premise.NOT_H},
)
def handle_drink_alcohol():
    """处理劝酒指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)


@add_instruct(
    constant.Instruct.DO_H,
    constant.InstructType.DAILY,
    _("邀请H"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.NOT_H},
)
def handle_do_h():
    """处理邀请H指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    if character.calculation_instuct_judege(0,character_data.target_character_id,"DO_H"):
        cache.is_H = 1
        now_draw = draw.WaitDraw()
        now_draw.width = width
        now_draw.text = _("\n进入H模式\n")
        now_draw.draw()
    else:
        now_draw = draw.WaitDraw()
        now_draw.width = width
        now_draw.text = _("\n进入H模式失败\n")
        now_draw.draw()


@add_instruct(
    constant.Instruct.STOP_H,
    constant.InstructType.DAILY,
    _("H结束"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_do_h():
    """处理H结束指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    cache.is_H = 0
    now_draw = draw.WaitDraw()
    now_draw.width = width
    now_draw.text = _("\n结束H模式\n")
    now_draw.draw()

# @add_instruct(
#     constant.Instruct.SINGING,
#     constant.InstructType.DAILY,
#     _("唱歌"),
#     {})
# def handle_singing():
#     """处理唱歌指令"""
#     character.init_character_behavior_start_time(0, cache.game_time)
#     character_data = cache.character_data[0]
#     character_data.behavior.duration = 5
#     character_data.behavior.behavior_id = constant.Behavior.SINGING
#     character_data.state = constant.CharacterStatus.STATUS_SINGING
#     update.game_update_flow(5)

# @add_instruct(
#     constant.Instruct.PLAY_INSTRUMENT,
#     constant.InstructType.DAILY,
#     _("演奏乐器"),
#     {constant.Premise.HAVE_TARGET},
# )
# def handle_play_instrument():
#     """处理演奏乐器指令"""
#     character.init_character_behavior_start_time(0, cache.game_time)
#     character_data: game_type.Character = cache.character_data[0]
#     character_data.behavior.duration = 5
#     update.game_update_flow(5)

#以下为猥亵#

@add_instruct(
    constant.Instruct.TOUCH_HEAD,
    constant.InstructType.OBSCENITY,
    _("摸头"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.NOT_H},
)
def handle_touch_head():
    """处理摸头指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data = cache.character_data[0]
    character_data.behavior.duration = 10
    character_data.behavior.behavior_id = constant.Behavior.TOUCH_HEAD
    character_data.state = constant.CharacterStatus.STATUS_TOUCH_HEAD
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.TOUCH_BUTTOCKS,
    constant.InstructType.OBSCENITY,
    _("摸屁股"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.NOT_H},
)
def handle_touch_buttocks():
    """处理摸屁股指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 10
    character_data.behavior.behavior_id = constant.Behavior.TOUCH_BUTTOCKS
    character_data.state = constant.CharacterStatus.STATUS_TOUCH_BUTTOCKS
    update.game_update_flow(10)

@add_instruct(
    constant.Instruct.TOUCH_EARS,
    constant.InstructType.OBSCENITY,
    _("摸耳朵"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.NOT_H,
    constant.Premise.TARGET_HAVE_EARS,},
)
def handle_touch_ears():
    """处理摸耳朵指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 10
    character_data.behavior.behavior_id = constant.Behavior.TOUCH_EARS
    character_data.state = constant.CharacterStatus.STATUS_TOUCH_EARS
    update.game_update_flow(10)

@add_instruct(
    constant.Instruct.TOUCH_HORN,
    constant.InstructType.OBSCENITY,
    _("摸角"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.NOT_H,
    constant.Premise.TARGET_HAVE_HORN,},
)
def handle_touch_horn():
    """处理摸角指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 10
    character_data.behavior.behavior_id = constant.Behavior.TOUCH_HORN
    character_data.state = constant.CharacterStatus.STATUS_TOUCH_HORN
    update.game_update_flow(10)

@add_instruct(
    constant.Instruct.TOUCH_TAIL,
    constant.InstructType.OBSCENITY,
    _("摸尾巴"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.NOT_H,
    constant.Premise.TARGET_HAVE_TAIL,},
)
def handle_touch_tail():
    """处理摸尾巴指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 10
    character_data.behavior.behavior_id = constant.Behavior.TOUCH_TAIL
    character_data.state = constant.CharacterStatus.STATUS_TOUCH_TAIL
    update.game_update_flow(10)

@add_instruct(
    constant.Instruct.TOUCH_RING,
    constant.InstructType.OBSCENITY,
    _("摸光环"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.NOT_H,
    constant.Premise.TARGET_HAVE_RING,},
)
def handle_touch_ring():
    """处理摸光环指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 10
    character_data.behavior.behavior_id = constant.Behavior.TOUCH_RING
    character_data.state = constant.CharacterStatus.STATUS_TOUCH_RING
    update.game_update_flow(10)

@add_instruct(
    constant.Instruct.TOUCH_WING,
    constant.InstructType.OBSCENITY,
    _("摸光翼"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.NOT_H,
    constant.Premise.TARGET_HAVE_WING,},
)
def handle_touch_wing():
    """处理摸光翼指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 10
    character_data.behavior.behavior_id = constant.Behavior.TOUCH_WING
    character_data.state = constant.CharacterStatus.STATUS_TOUCH_WING
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.TOUCH_TENTACLE,
    constant.InstructType.OBSCENITY,
    _("摸触手"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.NOT_H,
    constant.Premise.TARGET_HAVE_TENTACLE,},
)
def handle_touch_tentacle():
    """处理摸触手指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 10
    character_data.behavior.behavior_id = constant.Behavior.TOUCH_TENTACLE
    character_data.state = constant.CharacterStatus.STATUS_TOUCH_TENTACLE
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.TOUCH_CAR,
    constant.InstructType.OBSCENITY,
    _("摸小车"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.NOT_H,
    constant.Premise.TARGET_HAVE_CAR,},
)
def handle_touch_car():
    """处理摸小车指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 10
    character_data.behavior.behavior_id = constant.Behavior.TOUCH_CAR
    character_data.state = constant.CharacterStatus.STATUS_TOUCH_CAR
    update.game_update_flow(10)


@add_instruct(
    constant.Instruct.HAND_IN_HAND,
    constant.InstructType.OBSCENITY,
    _("牵手"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.NOT_H},
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
    constant.Instruct.LAP_PILLOW,
    constant.InstructType.OBSCENITY,
    _("膝枕"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.NOT_H},
)
def handle_lap_pillow():
    """处理膝枕指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 30
    character_data.behavior.behavior_id = constant.Behavior.LAP_PILLOW
    character_data.state = constant.CharacterStatus.STATUS_LAP_PILLOW
    update.game_update_flow(30)

@add_instruct(
    constant.Instruct.RAISE_SKIRT,
    constant.InstructType.OBSCENITY,
    _("掀起裙子"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.NOT_H},
)
def handle_raise_skirt():
    """处理掀起裙子指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    character_data.behavior.behavior_id = constant.Behavior.RAISE_SKIRT
    character_data.state = constant.CharacterStatus.STATUS_RAISE_SKIRT
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.TOUCH_CLITORIS,
    constant.InstructType.OBSCENITY,
    _("阴蒂爱抚"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.NOT_H},
)
def handle_touch_clitoris():
    """处理阴蒂爱抚指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.TOUCH_CLITORIS
    character_data.state = constant.CharacterStatus.STATUS_TOUCH_CLITORIS
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.TOUCH_VAGINA,
    constant.InstructType.OBSCENITY,
    _("手指插入（V）"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.NOT_H},
)
def handle_touch_vagina():
    """处理手指插入（V）指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.TOUCH_VAGINA
    character_data.state = constant.CharacterStatus.STATUS_TOUCH_VAGINA
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.TOUCH_ANUS,
    constant.InstructType.OBSCENITY,
    _("手指插入（A）"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.NOT_H},
)
def handle_touch_anus():
    """处理手指插入（A）指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.TOUCH_ANUS
    character_data.state = constant.CharacterStatus.STATUS_TOUCH_ANUS
    character_data.behavior.duration = 5
    update.game_update_flow(5)

#以下为性爱#


@add_instruct(
    constant.Instruct.MAKING_OUT,
    constant.InstructType.SEX,
    _("身体爱抚"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_making_out():
    """处理身体爱抚指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.TOUCH_ANUS
    character_data.state = constant.CharacterStatus.STATUS_TOUCH_ANUS
    character_data.behavior.duration = 10
    update.game_update_flow(10)

@add_instruct(
    constant.Instruct.KISS_H,
    constant.InstructType.SEX,
    _("接吻"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
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
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
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
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
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
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
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
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
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
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
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
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
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
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
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
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
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
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
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
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_anal_caress():
    """处理肛门爱抚指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.MAKE_MASTUREBATE,
    constant.InstructType.SEX,
    _("让对方自慰"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_make_masturebate():
    """处理让对方自慰指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.MAKE_LICK_ANAL,
    constant.InstructType.SEX,
    _("让对方舔肛门"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_make_lick_anal():
    """处理让对方舔肛门指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)
    
@add_instruct(
    constant.Instruct.DO_NOTHING,
    constant.InstructType.SEX,
    _("什么也不做"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_do_nothing():
    """处理什么也不做指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.SEDECU,
    constant.InstructType.SEX,
    _("诱惑"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_sedecu():
    """处理诱惑指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.NIPPLE_CLAMP,
    constant.InstructType.SEX,
    _("乳头夹"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_nipple_clamp():
    """处理乳头夹指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)
 
@add_instruct(
    constant.Instruct.NIPPLES_LOVE_EGG,
    constant.InstructType.SEX,
    _("乳头跳蛋"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_nipples_love_egg():
    """处理乳头跳蛋指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.CLIT_CLAMP,
    constant.InstructType.SEX,
    _("阴蒂夹"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_clit_clamp():
    """处理阴蒂夹指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.CLIT_LOVE_EGG,
    constant.InstructType.SEX,
    _("阴蒂跳蛋"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_clit_love_egg():
    """处理阴蒂跳蛋指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.ELECTRIC_MESSAGE_STICK,
    constant.InstructType.SEX,
    _("电动按摩棒"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_electric_message_stick():
    """处理电动按摩棒指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.VIBRATOR_INSERTION,
    constant.InstructType.SEX,
    _("震动棒"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_vibrator_insertion():
    """处理震动棒指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.VIBRATOR_INSERTION_ANAL,
    constant.InstructType.SEX,
    _("肛门振动棒"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_vibrator_insertion_anal():
    """处理肛门振动棒指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.MILKING_MACHINE,
    constant.InstructType.SEX,
    _("搾乳机"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_milking_machine():
    """处理搾乳机指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.URINE_COLLECTOR,
    constant.InstructType.SEX,
    _("采尿器"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_urine_collector():
    """处理采尿器指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.BONDAGE,
    constant.InstructType.SEX,
    _("绳子"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_bondage():
    """处理绳子指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.PATCH,
    constant.InstructType.SEX,
    _("眼罩"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_patch():
    """处理眼罩指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.PUT_CONDOM,
    constant.InstructType.SEX,
    _("避孕套"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_put_condom():
    """处理避孕套指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.BIRTH_CONTROL_PILLS,
    constant.InstructType.SEX,
    _("避孕药"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_birth_control_pills():
    """处理避孕药指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.BODY_LUBRICANT,
    constant.InstructType.SEX,
    _("润滑液"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_body_lubricant():
    """处理润滑液指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.PHILTER,
    constant.InstructType.SEX,
    _("媚药"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_philter():
    """处理媚药指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.DIURETICS,
    constant.InstructType.SEX,
    _("利尿剂"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_diuretics():
    """处理利尿剂指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.SLEEPING_PILLS,
    constant.InstructType.SEX,
    _("睡眠药"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_sleeping_pills():
    """处理睡眠药指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.HANDJOB,
    constant.InstructType.SEX,
    _("手交"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_handjob():
    """处理手交指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.BLOWJOB,
    constant.InstructType.SEX,
    _("口交"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_blowjob():
    """处理口交指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.PAIZURI,
    constant.InstructType.SEX,
    _("乳交"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_paizuri():
    """处理乳交指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.FOOTJOB,
    constant.InstructType.SEX,
    _("足交"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_footjob():
    """处理足交指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.HAIRJOB,
    constant.InstructType.SEX,
    _("发交"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_hairjob():
    """处理发交指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.AXILLAJOB,
    constant.InstructType.SEX,
    _("腋交"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_axillajob():
    """处理腋交指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.RUB_BUTTOCK,
    constant.InstructType.SEX,
    _("素股"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_rub_buttock():
    """处理素股指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.HAND_BLOWJOB,
    constant.InstructType.SEX,
    _("手交口交"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_hand_blowjob():
    """处理手交口交指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.TITS_BLOWJOB,
    constant.InstructType.SEX,
    _("乳交口交"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_tits_blowjob():
    """处理乳交口交指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.FOCUS_BLOWJOB,
    constant.InstructType.SEX,
    _("真空口交"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_focus_blowjob():
    """处理真空口交指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.DEEP_THROAT,
    constant.InstructType.SEX,
    _("深喉插入"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_deep_throat():
    """处理深喉插入指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.SIXTY_NINE,
    constant.InstructType.SEX,
    _("六九式"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_sixty_nine():
    """处理六九式指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.NORMAL_SEX,
    constant.InstructType.SEX,
    _("正常位"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_normal_sex():
    """处理正常位指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.BACK_SEX,
    constant.InstructType.SEX,
    _("背后位"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_back_sex():
    """处理背后位指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.RIDING_SEX,
    constant.InstructType.SEX,
    _("骑乘位"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_riding_sex():
    """处理骑乘位指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.FACE_SEAT_SEX,
    constant.InstructType.SEX,
    _("对面座位"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_face_seat_sex():
    """处理对面座位指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.BACK_SEAT_SEX,
    constant.InstructType.SEX,
    _("背面座位"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_back_seat_sex():
    """处理背面座位指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.FACE_STAND_SEX,
    constant.InstructType.SEX,
    _("对面立位"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_face_stand_sex():
    """处理对面立位指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.BACK_STAND_SEX,
    constant.InstructType.SEX,
    _("背面立位"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_back_stand_sex():
    """处理背面立位指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.STIMULATE_G_POINT,
    constant.InstructType.SEX,
    _("刺激G点"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_stimulate_g_point():
    """处理刺激G点指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.WOMB_OS_CARESS,
    constant.InstructType.SEX,
    _("玩弄子宫口"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_womb_os_caress():
    """处理玩弄子宫口指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.WOMB_INSERTION,
    constant.InstructType.SEX,
    _("插入子宫"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_womb_insertion():
    """处理插入子宫指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.NORMAL_ANAL_SEX,
    constant.InstructType.SEX,
    _("正常位肛交"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_normal_anal_sex():
    """处理正常位肛交指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.BACK_ANAL_SEX,
    constant.InstructType.SEX,
    _("后背位肛交"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_back_anal_sex():
    """处理后背位肛交指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.RIDING_ANAL_SEX,
    constant.InstructType.SEX,
    _("骑乘位肛交"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_riding_anal_sex():
    """处理骑乘位肛交指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.FACE_SEAT_ANAL_SEX,
    constant.InstructType.SEX,
    _("对面座位肛交"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_face_seat_anal_sex():
    """处理对面座位肛交指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.BACK_SEAT_ANAL_SEX,
    constant.InstructType.SEX,
    _("背面座位肛交"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_back_seat_anal_sex():
    """处理背面座位肛交指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.FACE_STAND_ANAL_SEX,
    constant.InstructType.SEX,
    _("对面立位肛交"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_face_stand_anal_sex():
    """处理对面立位肛交指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.BACK_STAND_ANAL_SEX,
    constant.InstructType.SEX,
    _("背面立位肛交"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_back_stand_anal_sex():
    """处理背面立位肛交指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.STIMULATE_SIGMOID_COLON,
    constant.InstructType.SEX,
    _("玩弄s状结肠"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_stimulate_sigmoid_colon():
    """处理玩弄s状结肠指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.STIMULATE_VAGINA,
    constant.InstructType.SEX,
    _("隔着刺激阴道"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_stimulate_vagina():
    """处理隔着刺激阴道指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.DOUBLE_PENETRATION,
    constant.InstructType.SEX,
    _("二穴插入"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
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
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_urethral_swab():
    """处理尿道棉棒指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.PISSING_PLAY,
    constant.InstructType.SEX,
    _("放尿play"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
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
    _("尿道插入"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_urethral_insertion():
    """处理尿道插入指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.BEAT_BREAST,
    constant.InstructType.SEX,
    _("打胸部"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
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
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
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
    _("羞耻play"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
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
    _("拘束play"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_bundled_play():
    """处理拘束play指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)

@add_instruct(
    constant.Instruct.TAKE_SHOWER,
    constant.InstructType.SEX,
    _("淋浴"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
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
    _("泡泡浴"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
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
    _("交给对方"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
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
    _("给对方口交"),
    {constant.Premise.HAVE_TARGET,
    constant.Premise.IS_H},
)
def handle_give_blowjob():
    """处理给对方口交指令"""
    character.init_character_behavior_start_time(0, cache.game_time)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.duration = 5
    update.game_update_flow(5)