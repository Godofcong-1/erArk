import random
from functools import wraps
from typing import List
from types import FunctionType
from Script.Core import get_text, constant, game_type, cache_control, flow_handle
from Script.Design import (
    handle_panel,
    character,
    character_handle,
    course,
    cooking,
    map_handle,
    interest,
    attr_calculation,
)
from Script.UI.Moudle import panel, draw
from Script.UI.Panel import see_character_info_panel
from Script.Config import normal_config, game_config

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """
width = normal_config.config_normal.text_width
""" 屏幕宽度 """
line_feed_draw = draw.NormalDraw()
""" 绘制换行对象 """
line_feed_draw.text = "\n"
line = draw.LineDraw("=", width)
""" 标题线绘制对象 """


@handle_panel.add_panel(constant.Panel.CREATOR_CHARACTER)
def creator_character_panel():
    """创建角色面板"""
    cache.character_data[0] = game_type.Character()
    character_handle.init_character_list()
    while 1:
        if input_name_panel():
            character.init_attr(0)
            game_start()
            if confirm_character_attr_panel():
                break
        cache.character_data[0] = game_type.Character()
    cache.now_panel_id = constant.Panel.IN_SCENE


def game_start():
    """初始化游戏数据"""
    character_handle.init_character_dormitory()
    character_handle.init_character_position()
    course.init_phase_course_hour()
    interest.init_character_interest()
    # course.init_character_knowledge()
    # course.init_class_teacher()
    # course.init_class_time_table()
    # course.init_teacher_table()
    cooking.init_recipes()
    cooking.init_restaurant_data()
    character_position = cache.character_data[0].position
    map_handle.character_move_scene(["0"], character_position, 0)
    cache.school_longitude = random.uniform(120.9, 122.12)
    cache.school_latitude = random.uniform(30.7, 31.53)


def confirm_character_attr_panel():
    """确认角色属性面板"""
    now_attr_panel = see_character_info_panel.SeeCharacterInfoPanel(0, width)
    askfor_panel = panel.OneMessageAndSingleColumnButton()
    while 1:
        line_feed_draw.draw()
        now_attr_panel.draw()
        ask_list = []
        ask_list.extend(now_attr_panel.return_list)
        now_line = draw.LineDraw("~", width)
        now_line.draw()
        askfor_list = [_("就这样开始新的人生吧"), _("重头再来一次")]
        start_id = 0
        now_id_judge = 0
        now_id_list = []
        for now_id in ask_list:
            if now_id.isdigit():
                now_id_judge = 1
                now_id_list.append(int(now_id))
        if now_id_judge:
            start_id = max(now_id_list) + 1
        askfor_panel.set(askfor_list, _("就这样了可以吗?"), start_id)
        askfor_panel.draw()
        askfor_panel_return_list = askfor_panel.get_return_list()
        ask_list.extend(askfor_panel_return_list.keys())
        yrn = flow_handle.askfor_all(ask_list)
        if yrn in askfor_panel_return_list:
            return askfor_panel_return_list[yrn] == askfor_list[0]


def input_name_panel() -> bool:
    """
    输入角色名面板
    Return arguments:
    bool -- 完成角色创建校验
    """
    character_data = cache.character_data[0]
    ask_name_panel = panel.AskForOneMessage()
    ask_name_panel.set(_("你能回忆起自己的名字吗？（默认称呼为博士，此处仅输入姓名即可）"), 10)
    line_feed_draw.draw()
    line.draw()
    not_num_error = draw.NormalDraw()
    not_num_error.text = _("角色名不能为纯数字，请重新输入\n")
    not_system_error = draw.NormalDraw()
    not_system_error.text = _("角色名不能为系统保留字，请重新输入\n")
    not_name_error = draw.NormalDraw()
    not_name_error.text = _("已有角色使用该姓名，请重新输入\n")
    create_judge = 0
    while 1:
        now_name = ask_name_panel.draw()
        if now_name.isdigit():
            not_num_error.draw()
            continue
        if now_name in get_text.translation_values or now_name in get_text.translation._catalog:
            not_system_error.draw()
            continue
        if now_name in cache.npc_name_data:
            not_name_error.draw()
            continue
        character_data.name = now_name
        create_judge = input_nick_name_panel()
        break
    return create_judge


def input_nick_name_panel() -> bool:
    """
    输入角色昵称面板
    Return arguments:
    bool -- 完成角色创建校验
    """
    create_judge = 0
    character_data = cache.character_data[0]
    # ask_nick_name_panel = panel.AskForOneMessage()
    # ask_nick_name_panel.set(_("该怎么称呼{character_name}好呢？").format(character_name=character_data.name), 10)
    # line_feed_draw.draw()
    # line.draw()
    # not_num_error = draw.NormalDraw()
    # not_num_error.text = _("角色昵称不能为纯数字，请重新输入")
    # not_system_error = draw.NormalDraw()
    # not_system_error.text = _("角色昵称不能为系统保留字，请重新输入")
    # while 1:
    #     nick_name = ask_nick_name_panel.draw()
    #     if nick_name.isdigit():
    #         not_num_error.draw()
    #         continue
    #     if nick_name in get_text.translation_values or nick_name in get_text.translation._catalog:
    #         not_system_error.draw()
    #         continue
    #     character_data.nick_name = nick_name
    #     create_judge = input_sex_panel()
    #     break
    character_data.nick_name = "博士"
    create_judge = input_sex_panel()
    return create_judge


def input_sex_panel() -> bool:
    """
    选择性别面板
    Return arguments:
    bool -- 完成角色创建校验
    """
    character_data: game_type.Character = cache.character_data[0]
    sex_list = [game_config.config_sex_tem[x].name for x in game_config.config_sex_tem] + [_("随机")]
    button_panel = panel.OneMessageAndSingleColumnButton()
    button_panel.set(
        sex_list, _("那么{character_name}{character_nick_name}的性别是？").format(character_name=character_data.name,character_nick_name=character_data.nick_name)
    )
    return_list = button_panel.get_return_list()
    line_feed_draw.draw()
    line.draw()
    button_panel.draw()
    ans = flow_handle.askfor_all(return_list.keys())
    now_id = int(ans)
    if now_id == len(return_list) - 1:
        now_id = random.randint(0, now_id - 1)
    character_data.sex = now_id
    if character_data.sex in {1, 2}:
        character_data.chest_tem = attr_calculation.get_rand_npc_chest_tem()
    create_judge = input_setting_panel()
    return create_judge


def input_setting_panel() -> bool:
    """
    询问设置详细信息面板
    Return arguments:
    bool -- 完成角色创建流程
    """
    # character_data = cache.character_data[0]
    # ask_list = [_("是"), _("否")]
    # button_panel = panel.OneMessageAndSingleColumnButton()
    # button_panel.set(
        # ask_list,
        # _("是否需要设置详细属性呢？将会随机抽取十道题目供{character_nick_name}进行选择。").format(
        #     character_nick_name=character_data.nick_name
        # ),
    # )
    # return_list = button_panel.get_return_list()
    # line_feed_draw.draw()
    # line.draw()
    # button_panel.draw()
    # ans = flow_handle.askfor_all(return_list.keys())
    # if int(ans):
    #     return 1
    # return input_setting_now()
    return 1


def input_setting_now() -> bool:
    """启动详细信息设置"""
    panel_list = random.sample(setting_panel_data, len(setting_panel_data))
    for now_panel in panel_list:
        line_feed_draw.draw()
        line.draw()
        now_panel()
    return 1


setting_panel_data: List[FunctionType] = []
""" 设置详细信息面板数据 """


def add_setting_panel() -> FunctionType:
    """
    添加创建角色时设置详细信息面板
    Return arguments:
    FunctionType -- 面板对象处理函数
    """

    def decoraror(func):
        @wraps(func)
        def return_wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        setting_panel_data.append(return_wrapper)
        return return_wrapper

    return decoraror


@add_setting_panel()
def setting_age_tem_panel():
    """设置年龄模板"""
    character_data: game_type.Character = cache.character_data[0]
    message = _("{character_nick_name}是一个小孩子吗？").format(character_nick_name=character_data.nick_name)
    ask_list = [
        _("嘎呜～嘎呜～"),
        _("才，才不是小孩子！"),
        _("已经成年了哦～"),
        _("我也想回到小时候呢～"),
        _("你说什么？我听不清～"),
    ]
    button_panel = panel.OneMessageAndSingleColumnButton()
    button_panel.set(ask_list, message)
    return_list = button_panel.get_return_list()
    button_panel.draw()
    ans = flow_handle.askfor_all(return_list.keys())
    character_data.age = attr_calculation.get_age(int(ans))


@add_setting_panel()
def setting_weight_panel():
    """设置体重模板"""
    character_data = cache.character_data[0]
    message = _("{character_nick_name}对自己的体重有自信吗？").format(character_nick_name=character_data.nick_name)
    ask_list = [
        _("很轻，就像一张纸一样，风一吹就能飘起来。"),
        _("普普通通，健康的身材。"),
        _("略沉，不过从外表不怎么能够看得出来。"),
        _("肉眼可辨的比别人要胖很多。"),
        _("人类的极限，看上去像是相扑选手一样。"),
    ]
    button_panel = panel.OneMessageAndSingleColumnButton()
    button_panel.set(ask_list, message)
    return_list = button_panel.get_return_list()
    button_panel.draw()
    ans = flow_handle.askfor_all(return_list.keys())
    character_data.weight_tem = int(ans)


@add_setting_panel()
def setting_sex_experience_panel():
    """设置性经验模板"""
    character_data = cache.character_data[0]
    message = _("{character_nick_name}是否有过性经验呢？").format(character_nick_name=character_data.nick_name)
    ask_list = [
        _("性经验什么的完全没有过，你在问什么呢！变态！"),
        _("只有极少的性经验哦，说是纯情也不为过。"),
        _("大概只是普通的程度吧？不多也不少的样子。"),
        _("经验非常丰富，特别有技巧哦，哼哼。"),
    ]
    button_panel = panel.OneMessageAndSingleColumnButton()
    button_panel.set(ask_list, message)
    return_list = button_panel.get_return_list()
    button_panel.draw()
    ans = flow_handle.askfor_all(return_list.keys())
    character_data.sex_experience_tem = int(ans)


@add_setting_panel()
def setting_nature_0_panel():
    """设置性格倾向:活跃"""
    character_data = cache.character_data[0]
    message = _("{character_nick_name}是否是一个有话就说，从来不憋在心里的人呢？").format(
        character_nick_name=character_data.nick_name
    )
    ask_list = [_("是"), _("不是")]
    button_panel = panel.OneMessageAndSingleColumnButton()
    button_panel.set(ask_list, message)
    return_list = button_panel.get_return_list()
    button_panel.draw()
    ans = flow_handle.askfor_all(return_list.keys())
    character_data.nature[0] = abs(random.randint(0, 100) - int(ans) * 50)


@add_setting_panel()
def setting_nature_1_panel():
    """设置性格倾向:合群"""
    character_data = cache.character_data[0]
    message = _("{character_nick_name}在参加聚会时，会很自然的融入进人群里吗？").format(
        character_nick_name=character_data.nick_name
    )
    ask_list = [_("会"), _("不会")]
    button_panel = panel.OneMessageAndSingleColumnButton()
    button_panel.set(ask_list, message)
    return_list = button_panel.get_return_list()
    button_panel.draw()
    ans = flow_handle.askfor_all(return_list.keys())
    character_data.nature[1] = abs(random.randint(0, 100) - int(ans) * 50)


@add_setting_panel()
def setting_nature_2_panel():
    """设置性格倾向:乐观"""
    character_data = cache.character_data[0]
    message = _("{character_nick_name}有憧憬过未来的人生吗？").format(character_nick_name=character_data.nick_name)
    ask_list = [_("有"), _("没有")]
    button_panel = panel.OneMessageAndSingleColumnButton()
    button_panel.set(ask_list, message)
    return_list = button_panel.get_return_list()
    button_panel.draw()
    ans = flow_handle.askfor_all(return_list.keys())
    character_data.nature[2] = abs(random.randint(0, 100) - int(ans) * 50)


@add_setting_panel()
def setting_nature_3_panel():
    """设置性格倾向:守信"""
    character_data = cache.character_data[0]
    message = _("承诺过的事情就一定要做到？")
    ask_list = [_("会"), _("视情况而定")]
    button_panel = panel.OneMessageAndSingleColumnButton()
    button_panel.set(ask_list, message)
    return_list = button_panel.get_return_list()
    button_panel.draw()
    ans = flow_handle.askfor_all(return_list.keys())
    character_data.nature[3] = abs(random.randint(0, 100) - int(ans) * 50)


@add_setting_panel()
def setting_nature_4_panel():
    """设置性格区间:无私"""
    character_data = cache.character_data[0]
    message = _("考虑问题时会顾及到别人的利益吗？")
    ask_list = [_("会"), _("不会")]
    button_panel = panel.OneMessageAndSingleColumnButton()
    button_panel.set(ask_list, message)
    return_list = button_panel.get_return_list()
    button_panel.draw()
    ans = flow_handle.askfor_all(return_list.keys())
    character_data.nature[4] = abs(random.randint(0, 100) - int(ans) * 50)


@add_setting_panel()
def setting_nature_5_panel():
    """设置性格区间:重情"""
    character_data = cache.character_data[0]
    message = _("关心别人的时候会让自己感到快乐？")
    ask_list = [_("会"), _("不会")]
    button_panel = panel.OneMessageAndSingleColumnButton()
    button_panel.set(ask_list, message)
    return_list = button_panel.get_return_list()
    button_panel.draw()
    ans = flow_handle.askfor_all(return_list.keys())
    character_data.nature[5] = abs(random.randint(0, 100) - int(ans) * 50)


@add_setting_panel()
def setting_nature_6_panel():
    """设置性格区间:严谨"""
    character_data = cache.character_data[0]
    message = _("对于自己的任务，会一丝不苟的去完成吗？")
    ask_list = [_("会"), _("不会")]
    button_panel = panel.OneMessageAndSingleColumnButton()
    button_panel.set(ask_list, message)
    return_list = button_panel.get_return_list()
    button_panel.draw()
    ans = flow_handle.askfor_all(return_list.keys())
    character_data.nature[6] = abs(random.randint(0, 100) - int(ans) * 50)


@add_setting_panel()
def setting_nature_7_panel():
    """设置性格区间:自律"""
    character_data = cache.character_data[0]
    message = _("{character_nick_name}是一个即使不会被发现，也绝不弄虚作假的人吗？").format(
        character_nick_name=character_data.nick_name
    )
    ask_list = [_("当然"), _("不是")]
    button_panel = panel.OneMessageAndSingleColumnButton()
    button_panel.set(ask_list, message)
    return_list = button_panel.get_return_list()
    button_panel.draw()
    ans = flow_handle.askfor_all(return_list.keys())
    character_data.nature[7] = abs(random.randint(0, 100) - int(ans) * 50)


@add_setting_panel()
def setting_nature_8_panel():
    """设置性格区间:沉稳"""
    character_data = cache.character_data[0]
    message = _("即使在一些很随便的场合，也会表现得很严肃对吗？")
    ask_list = [_("会"), _("不会")]
    button_panel = panel.OneMessageAndSingleColumnButton()
    button_panel.set(ask_list, message)
    return_list = button_panel.get_return_list()
    button_panel.draw()
    ans = flow_handle.askfor_all(return_list.keys())
    character_data.nature[8] = abs(random.randint(0, 100) - int(ans) * 50)


@add_setting_panel()
def setting_nature_9_panel():
    """设置性格区间:决断"""
    character_data = cache.character_data[0]
    message = _("{character_nick_name}总是很轻率的做出了决定对吗？").format(character_nick_name=character_data.nick_name)
    ask_list = [_("是"), _("不是")]
    button_panel = panel.OneMessageAndSingleColumnButton()
    button_panel.set(ask_list, message)
    return_list = button_panel.get_return_list()
    button_panel.draw()
    ans = flow_handle.askfor_all(return_list.keys())
    character_data.nature[9] = abs(random.randint(0, 100) - int(ans) * 50)


@add_setting_panel()
def setting_nature_10_panel():
    """设置性格区间:坚韧"""
    character_data = cache.character_data[0]
    message = _("不会轻易的放弃自己的理想？")
    ask_list = [_("是"), _("不是")]
    button_panel = panel.OneMessageAndSingleColumnButton()
    button_panel.set(ask_list, message)
    return_list = button_panel.get_return_list()
    button_panel.draw()
    ans = flow_handle.askfor_all(return_list.keys())
    character_data.nature[10] = abs(random.randint(0, 100) - int(ans) * 50)


@add_setting_panel()
def setting_nature_11_panel():
    """设置性格区间:机敏"""
    character_data = cache.character_data[0]
    message = _("喜欢多与对{character_nick_name}有利的人交往对吗？").format(character_nick_name=character_data.nick_name)
    ask_list = [_("是"), _("不是")]
    button_panel = panel.OneMessageAndSingleColumnButton()
    button_panel.set(ask_list, message)
    return_list = button_panel.get_return_list()
    button_panel.draw()
    ans = flow_handle.askfor_all(return_list.keys())
    character_data.nature[11] = abs(random.randint(0, 100) - int(ans) * 50)


@add_setting_panel()
def setting_nature_12_panel():
    """设置性格区间:耐性"""
    character_data = cache.character_data[0]
    message = _("对工作会倾注全部的热情？")
    ask_list = [_("是"), _("不是")]
    button_panel = panel.OneMessageAndSingleColumnButton()
    button_panel.set(ask_list, message)
    return_list = button_panel.get_return_list()
    button_panel.draw()
    ans = flow_handle.askfor_all(return_list.keys())
    character_data.nature[12] = abs(random.randint(0, 100) - int(ans) * 50)


@add_setting_panel()
def setting_nature_13_panel():
    """设置性格区间:爽直"""
    character_data = cache.character_data[0]
    message = _("{character_nick_name}是一个心直口快，想到什么说什么的人对吗？").format(
        character_nick_name=character_data.nick_name
    )
    ask_list = [_("是"), _("不是")]
    button_panel = panel.OneMessageAndSingleColumnButton()
    button_panel.set(ask_list, message)
    return_list = button_panel.get_return_list()
    button_panel.draw()
    ans = flow_handle.askfor_all(return_list.keys())
    character_data.nature[13] = abs(random.randint(0, 100) - int(ans) * 50)
