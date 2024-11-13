import random
import datetime
from types import FunctionType
from Script.Core import (
    cache_control,
    get_text,
    constant,
    game_type,
    text_handle,
    flow_handle,
)
from Script.Design import (
    map_handle,
    attr_calculation,
    clothing,
    game_time,
    handle_talent,
    handle_premise,
)
from Script.Config import game_config, normal_config
from Script.UI.Moudle import panel, draw

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """

_: FunctionType = get_text._
""" 翻译api """
line_feed = draw.NormalDraw()
""" 换行绘制对象 """
line_feed.text = "\n"
line_feed.width = 1
window_width: int = normal_config.config_normal.text_width
""" 窗体宽度 """


def init_attr(character_id: int):
    """
    初始化角色属性
    Keyword arguments:
    character_id -- 角色id
    """
    # print("进入第二步的init_attr")
    # print("进入第二步的character_id :",character_id)
    character_data: game_type.Character = cache.character_data[character_id]
    # character_data.birthday = attr_calculation.get_rand_npc_birthday(character_data.age)
    # character_data.height = attr_calculation.get_height(character_data.sex, character_data.age)
    # character_data.weight = attr_calculation.get_weight(bmi, character_data.height.now_height)

    # 一系列归零函数
    character_data.ability = attr_calculation.get_ability_zero(character_data.ability)
    character_data.status_data = attr_calculation.get_status_zero(character_data.status_data)
    character_data.talent = attr_calculation.get_talent_zero(character_data.talent)
    character_data.experience = attr_calculation.get_experience_zero(character_data.experience)
    character_data.juel = attr_calculation.get_juel_zero(character_data.juel)
    character_data.second_behavior = attr_calculation.get_second_behavior_zero(character_data.second_behavior)
    character_data.dirty = attr_calculation.get_dirty_reset(character_data.dirty)
    character_data.item = attr_calculation.get_item_zero(character_data.item)
    character_data.h_state = attr_calculation.get_h_state_reset(character_data.h_state)
    character_data.first_record = attr_calculation.get_first_record_zero()
    character_data.action_info = attr_calculation.get_action_info_state_zero()
    character_data.event = attr_calculation.get_event_zero()
    character_data.work = attr_calculation.get_work_zero()
    character_data.entertainment = attr_calculation.get_entertainment_zero()
    character_data.pregnancy = attr_calculation.get_pregnancy_zero()
    character_data.sp_flag = game_type.SPECIAL_FLAG()
    character_data.chara_setting = attr_calculation.get_chara_setting_zero()
    character_data.assistant_services = attr_calculation.get_assistant_services_zero()
    character_data.body_manage = attr_calculation.get_body_manage_zero()
    # character_data.relationship = attr_calculation.get_relationship_zero(character_data.relationship)

    # 主角的初始处理，HP和MP的最大值默认为1000，EP最大值默认为1000，初始化信物，困倦程度归零
    if character_id == 0:
        character_data.talent = attr_calculation.get_Dr_talent_zero(character_data.talent)
        character_data.hit_point_max = 1000
        character_data.mana_point_max = 1000
        character_data.eja_point = 0
        character_data.eja_point_max = 1000
        character_data.sanity_point = 100
        character_data.sanity_point_max = 100
        character_data.semen_point = 100
        character_data.semen_point_max = 100
        character_data.pl_collection.token_list = attr_calculation.get_token_zero(
            character_data.pl_collection.token_list)
        character_data.tired_point = 0
        character_data.pl_ability = attr_calculation.get_pl_ability_zero()
        character_data.pl_collection = attr_calculation.get_collection_zero()
        character_data.cloth = attr_calculation.get_cloth_zero()
        character_data.favorability = {0:0}
        character_data.dormitory = map_handle.get_map_system_path_str_for_list(["中枢", "博士房间"]) # 此处不可使用翻译
        character_data.pre_dormitory = map_handle.get_map_system_path_str_for_list(["中枢", "博士房间"])
        # 初始收藏地点
        cache.collect_position_list.append(['中枢', '博士房间'])
        cache.collect_position_list.append(['中枢', '博士办公室'])
        cache.collect_position_list.append(['贸易', '成人用品店'])
        cache.collect_position_list.append(['书', '藏品馆'])

    # 一系列初始化函数
    init_character_behavior_start_time(character_id,cache.game_time)
    character_data.hit_point = character_data.hit_point_max
    character_data.mana_point = character_data.mana_point_max
    character_data.angry_point = random.randrange(1, 35)
    character_data.hunger_point = 240
    if character_id:
        clothing.get_underwear(character_id)
    # default_clothing_data = clothing.creator_suit(character_data.clothing_tem, character_data.sex)
    # for clothing_id in default_clothing_data:
    #     clothing_data = default_clothing_data[clothing_id]
    #     character_data.clothing.setdefault(clothing_id, {})
    #     character_data.clothing[clothing_id][clothing_data.uid] = clothing_data
    #     character_data.clothing_data.setdefault(clothing_data.tem_id, set())
    #     character_data.clothing_data[clothing_data.tem_id].add(clothing_data.uid)
    # init_class(character_data)


def input_name_func(ask_text: str) -> str:
    """
    输入角色名函数
    Keyword arguments:
    ask_text -- 询问的文本
    Return arguments:
    str -- 角色名
    """
    ask_name_panel = panel.AskForOneMessage()
    ask_name_panel.set(ask_text, 10)
    line_feed.draw()
    line = draw.LineDraw("=", width=window_width)
    line.draw()
    # 几种错误提示
    not_num_error = draw.NormalDraw()
    not_num_error.text = _("角色名不能为纯数字，请重新输入\n")
    not_system_error = draw.NormalDraw()
    not_system_error.text = _("角色名不能为系统保留字，请重新输入\n")
    not_name_error = draw.NormalDraw()
    not_name_error.text = _("已有角色使用该姓名，请重新输入\n")
    # 返回的角色名
    return_name = ""
    # 开始循环
    while 1:
        now_name = ask_name_panel.draw()
        if now_name.isdigit():
            not_num_error.draw()
            continue
        if now_name in get_text.translation_values:
            not_system_error.draw()
            continue
        if now_name in cache.npc_name_data:
            not_name_error.draw()
            continue
        return_name = now_name
        break

    return return_name


def init_character_behavior_start_time(character_id: int, now_time: datetime.datetime):
    """
    将角色的行动开始时间同步为指定时间
    Keyword arguments:
    character_id -- 角色id
    now_time -- 指定时间
    """
    character_data = cache.character_data[character_id]
    start_time = datetime.datetime(
        now_time.year,
        now_time.month,
        now_time.day,
        now_time.hour,
        now_time.minute,
    )
    character_data.behavior.start_time = start_time


def character_rest_to_time(character_id: int, need_time: int):
    """
    设置角色状态为休息指定时间
    Keyword arguments:
    character_id -- 角色id
    need_time -- 休息时长(分钟)
    """
    character_data = cache.character_data[character_id]
    character_data.behavior["Duration"] = need_time
    character_data.behavior["BehaviorId"] = constant.Behavior.REST
    character_data.state = constant.CharacterStatus.STATUS_REST


def calculation_favorability(character_id: int, target_character_id: int, favorability: int) -> int:
    """
    按角色当前状态、素质和能力计算最终增加的好感值
    Keyword arguments:
    character_id -- 角色id
    target_character_id -- 目标角色id
    favorability -- 基础好感值
    Return arguments:
    int -- 最终的好感值
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[target_character_id]
    fix = 1.0
    # 状态相关计算#

    # 恭顺、好意、欲情、快乐每级+0.1倍#
    for i in {10, 11, 12, 13}:
        status_level = attr_calculation.get_status_level(target_data.status_data[i])
        fix += status_level * 0.1
    # 羞耻、苦痛每级-0.1倍#
    for i in {16, 17}:
        status_level = attr_calculation.get_status_level(target_data.status_data[i])
        fix -= status_level * 0.1
    # 恐怖、抑郁、反感每级-0.3倍#
    for i in {18, 19, 20}:
        status_level = attr_calculation.get_status_level(target_data.status_data[i])
        fix -= status_level * 0.3

    # 能力相关计算#
    # 亲密、快乐刻印、屈服刻印每级+0.2倍#
    for i in {13, 14, 32}:
        ability_level = target_data.ability[i]
        fix += ability_level * 0.2
    # 苦痛刻印、恐怖刻印每级-0.3倍#
    for i in {15, 17}:
        ability_level = target_data.ability[i]
        fix -= ability_level * 0.3
    # 反发刻印每级-1.0倍#
    for i in {18}:
        ability_level = target_data.ability[i]
        fix -= ability_level * 1.0

    # 素质相关计算#
    # 爱情与隶属系加成0.5~2.0#
    if target_data.talent[201] or target_data.talent[211]:
        fix += 0.25
    if target_data.talent[202] or target_data.talent[212]:
        fix += 0.5
    if target_data.talent[203] or target_data.talent[213]:
        fix += 0.75
    if target_data.talent[204] or target_data.talent[214]:
        fix += 1.0
    # 受精、妊娠、育儿均+0.5#
    if target_data.talent[20] or target_data.talent[21] or target_data.talent[22]:
        fix += 0.5
    # 感情缺乏-0.2#
    if target_data.talent[223]:
        fix -= 0.2
    # 讨厌男性-0.2#
    if target_data.talent[227]:
        fix -= 0.2
    # 博士信息素每级+0.25#
    if character_data.talent[306]:
        fix += 0.75
    elif character_data.talent[305]:
        fix += 0.5
    elif character_data.talent[304]:
        fix += 0.25
    # 好感香薰修正
    if character_data.sp_flag.aromatherapy == 5 or target_data.sp_flag.aromatherapy == 5:
        fix += 0.5
    # 空气催眠置为零
    if target_data.sp_flag.unconscious_h == 5 and character_data.position == character_data.pl_ability.air_hypnosis_position:
        fix = 0
    favorability *= fix
    return favorability

def calculation_trust(character_id: int, target_character_id: int, add_time: int) -> int:
    """
    按角色当前状态、素质和能力计算最终增加的信赖度
    Keyword arguments:
    character_id -- 角色id
    target_character_id -- 目标角色id
    add_time -- 指令的时间
    Return arguments:
    int -- 最终的信赖度
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[target_character_id]
    fix = 1.0

    # 能力相关计算#
    # 亲密、快乐刻印、屈服刻印每级+0.2倍#
    for i in {13, 14, 32}:
        ability_level = target_data.ability[i]
        fix += ability_level * 0.2
    # 苦痛刻印、恐怖刻印每级-0.3倍#
    for i in {15, 17}:
        ability_level = target_data.ability[i]
        fix -= ability_level * 0.3
    # 反发刻印每级-1.0倍#
    for i in {18}:
        ability_level = target_data.ability[i]
        fix -= ability_level * 1.0

    # 素质相关计算#
    # 爱情与隶属系加成0.5~2.0#
    if target_data.talent[201] or target_data.talent[211]:
        fix += 0.25
    if target_data.talent[202] or target_data.talent[212]:
        fix += 0.5
    if target_data.talent[203] or target_data.talent[213]:
        fix += 0.75
    if target_data.talent[204] or target_data.talent[214]:
        fix += 1.0
    # 受精、妊娠、育儿均+0.5#
    if target_data.talent[20] or target_data.talent[21] or target_data.talent[22]:
        fix += 0.5
    # 感情缺乏-0.2#
    if target_data.talent[223]:
        fix -= 0.2
    # 讨厌男性-0.2#
    if target_data.talent[227]:
        fix -= 0.2
    # 博士信息素每级+0.25#
    if character_data.talent[306]:
        fix += 0.75
    elif character_data.talent[305]:
        fix += 0.5
    elif character_data.talent[304]:
        fix += 0.25
    # 好感香薰修正
    if character_data.sp_flag.aromatherapy == 5 or target_data.sp_flag.aromatherapy == 5:
        fix += 0.5
    # 空气催眠置为零
    if target_data.sp_flag.unconscious_h == 5 and character_data.position == character_data.pl_ability.air_hypnosis_position:
        fix = 0
    trust_add = add_time / 60 * fix
    return trust_add


def calculation_instuct_judege(character_id: int, target_character_id: int, instruct_name: str, not_draw_flag = False):
    """
    根据角色和目标角色的各属性来计算总实行值\n
    Keyword arguments:\n
    character_id -- 角色id\n
    target_character_id -- 目标角色id\n
    instruct_name -- 指令名字\n
    not_draw_flag -- 是否不输出文本\n
    Return arguments:\n
    int -- 1成功,0失败,-1无副作用返回\n
    int -- 实行值\n
    float -- 实行值与目标值的比值\n
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[target_character_id]

    # 对玩家为目标的指令是必定成功的
    if target_character_id == 0:
        return [1, 1, 1.0]

    for judge_id in game_config.config_instruct_judge_data:
        # 匹配到能力的id与能力等级对应的前提#
        if game_config.config_instruct_judge_data[judge_id].instruct_name == instruct_name:
            judge_data = game_config.config_instruct_judge_data[judge_id]
            judge_data_type = judge_data.need_type
            judge_data_value = judge_data.value
            break

    calculation_text = ""
    if judge_data_type == "D":
        calculation_text += _("需要基础实行值至少为") + str(judge_data_value) + "\n"
    elif judge_data_type == "S":
        calculation_text += _("需要性爱实行值至少为") + str(judge_data_value) + "\n"
    calculation_text += _("当前值为：")

    judge = 0

    # 好感判定#
    favorability_level,judge_favorability = attr_calculation.get_favorability_level(target_data.favorability[0])
    calculation_text += _("好感修正(") + str(judge_favorability) + ")"
    judge += judge_favorability

    # 信赖判定#
    trust_level,judge_trust = attr_calculation.get_trust_level(target_data.trust)
    judge += judge_trust
    calculation_text += _("+信赖修正(") + str(judge_trust) + ")"

    # 状态修正，好意(11)和欲情(12)修正#
    status_level_sum =  attr_calculation.get_status_level(target_data.status_data[11]) + attr_calculation.get_status_level(target_data.status_data[12])
    judge_status = status_level_sum * 10
    judge += judge_status
    if judge_status:
        calculation_text += _("+状态修正(") + str(judge_status) + ")"

    # 能力修正，亲密(32)和欲望(33)修正#
    judge_ability = target_data.ability[32] * 10 + target_data.ability[33] * 5
    judge += judge_ability
    if judge_ability:
        calculation_text += _("+能力修正(") + str(judge_ability) + ")"

    # 刻印修正，快乐(13)、屈服(14)、苦痛(15)、时停(16)、恐怖(17)、反发(18)、无觉(19)修正#
    judge_mark = target_data.ability[13] * 50 + target_data.ability[14] * 50 + target_data.ability[15] * 10 + target_data.ability[19] * 25
    judge_mark -= min(target_data.ability[17] - target_data.ability[16], 0) * 50 + target_data.ability[18] * 100
    judge += judge_mark
    if judge_mark:
        calculation_text += _("+全刻印总修正(") + str(judge_mark) + ")"

    # 心情修正，好心情+10，坏心情-10，愤怒-30
    judge_angry = attr_calculation.get_angry_level(target_data.angry_point) * 20
    judge += judge_angry
    if judge_angry:
        calculation_text += _("+心情修正(") + str(judge_angry) + ")"

    # 陷落素质判定，第一阶段~第四阶段分别为30,50,80,100#
    judge_fall = target_data.talent[201] * 30 + target_data.talent[202] * 50 + target_data.talent[203] * 80 + \
                 target_data.talent[204] * 100 + target_data.talent[211] * 30 + target_data.talent[212] * 50 + \
                 target_data.talent[213] * 80 + target_data.talent[214] * 100
    judge += judge_fall
    if judge_fall:
        calculation_text += _("+陷落修正(") + str(judge_fall) + ")"
    # 讨厌男性修正#
    judge_hate = target_data.talent[227] * 30
    judge -= judge_hate
    if judge_hate:
        calculation_text += _("+讨厌男性(-") + str(judge_hate) + ")"
    # 难以越过的底线修正#
    judge_hardlove = target_data.talent[224] * 100
    judge -= judge_hardlove
    if judge_hardlove:
        calculation_text += _("+难以越过的底线(-") + str(judge_hardlove) + ")"
    # 被对方持有把柄修正
    judge_weakness = target_data.talent[401] * 100
    judge -= judge_weakness
    if judge_weakness:
        calculation_text += _("+被对方持有把柄(-") + str(judge_weakness) + ")"
    # 持有对方把柄修正
    judge_weakness = target_data.talent[402] * 100
    judge += judge_weakness
    if judge_weakness:
        calculation_text += _("+持有对方把柄(+") + str(judge_weakness) + ")"

    # 仅性爱指令
    if judge_data_type == "S":
        # 淫乱相关属性修正#
        if target_data.talent[40]:
            judge += 50
            calculation_text += _("+淫乱(+50)")
        # 性好奇
        if target_data.talent[220]:
            judge += 30
            calculation_text += _("+性好奇(+30)")
        # 性冷漠
        if target_data.talent[221]:
            judge -= 30
            calculation_text += _("+性冷漠(-30)")
        # 性无知
        if target_data.talent[222]:
            judge += 30
            calculation_text += _("+性无知(+30)")
        # 爱情旅馆修正
        if target_data.h_state.h_in_love_hotel:
            if cache.rhodes_island.love_hotel_room_lv == 1:
                judge += 25
                calculation_text += _("+标间(+25)")
            elif cache.rhodes_island.love_hotel_room_lv == 2:
                judge += 50
                calculation_text += _("+情趣主题房(+50)")
            elif cache.rhodes_island.love_hotel_room_lv == 3:
                judge += 100
                calculation_text += _("+顶级套房(+100)")

    # 激素系能力修正#
    if character_data.pl_ability.hormone:
        judge_information = character_data.talent[304] * 25 + character_data.talent[305] * 50 + character_data.talent[306] * 100
        judge += judge_information
        talent_id = handle_talent.have_hormone_talent()
        talent_name = game_config.config_talent[talent_id].name
        if judge_information:
            calculation_text += f"+{talent_name}({str(judge_information)})"

    # 访客不判定的部分
    if judge_data_type != "V":

        # 当前场景有人修正
        scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
        scene_data = cache.scene_data[scene_path_str]
        if len(scene_data.character_list) > 2:
            other_chara_count = len(scene_data.character_list) - 2
            if judge_data_type == "S":
                judge_other_people = 40 + 40 * other_chara_count
            else:
                judge_other_people = 25 + 25 * other_chara_count
            # 露出修正
            adjust = attr_calculation.get_ability_adjust(target_data.ability[34])
            judge_other_people = int(judge_other_people * (adjust - 1.4))
            judge += judge_other_people
            calculation_text += _("+有别人在时的露出修正(") + text_handle.number_to_symbol_string(judge_other_people) + ")"

        # 助理助攻修正
        if character_data.assistant_character_id != target_character_id and character_data.assistant_character_id in scene_data.character_list:
            assistant_character_data = cache.character_data[character_data.assistant_character_id]
            if assistant_character_data.assistant_services[8]:
                judge += 50
                calculation_text += _("+助理助攻(+50)")

        # 今天H被打断了修正
        if judge_data_type == "S":
            judge_h_interrupt = character_data.action_info.h_interrupt * 50
            judge -= judge_h_interrupt
            if judge_h_interrupt:
                calculation_text += _("+今天H被打断过(-") + str(judge_h_interrupt) + ")"

        # 监禁模式修正
        if handle_premise.handle_imprisonment_1(target_character_id):
            judge += 500
            calculation_text += _("+监禁中(+500)")

        # 睡眠修正
        if handle_premise.handle_unconscious_flag_1(target_character_id):
            judge += 999
            calculation_text += _("+睡眠(+999)")

        # 时停修正
        if handle_premise.handle_unconscious_flag_3(target_character_id):
            judge += 9999
            calculation_text += _("+时停(+9999)")

    # 处女修正
    if instruct_name == _("性交") and target_data.talent[0]:
        judge -= 250
        calculation_text += _("+处女(-250)")

    # A处女修正
    if instruct_name == _("A性交") and target_data.talent[1]:
        judge -= 350
        calculation_text += _("+Ａ处女(-350)")

    # U处女修正
    if instruct_name == _("U性交") and target_data.talent[2]:
        judge -= 400
        calculation_text += _("+Ｕ处女(-400)")

    # 初吻修正
    if instruct_name == _("亲吻") and target_data.talent[4]:
        judge -= 125
        calculation_text += _("+初吻(-125)")

    # 性交的避孕相关修正
    if instruct_name == _("性交"):
        # 妊娠合意、避孕套、避孕中出合意+事前避孕药、性无知，以上可直接通过
        if (
            target_data.talent[14] or
            character_data.h_state.body_item[13][1] or
            (target_data.talent[13] and target_data.h_state.body_item[11][1]) or
            target_data.talent[222]
            ):
            pass
        else:
            if handle_premise.handle_reproduction_period_0(target_character_id):
                # 避孕中出合意合意
                if target_data.talent[13]:
                    pass
                else:
                    judge -= 10
                    calculation_text += _("+安全期(-10)")
            elif handle_premise.handle_reproduction_period_1(target_character_id):
                judge -= 50
                calculation_text += _("+普通期(-50)")
            elif handle_premise.handle_reproduction_period_2(target_character_id):
                judge -= 200
                calculation_text += _("+危险期(-200)")
            elif handle_premise.handle_reproduction_period_3(target_character_id):
                judge -= 300
                calculation_text += _("+排卵期(-300)")

    # 催眠系能力的最后补正，仅在催眠、性爱判定、且实行值不足时生效
    judge_hypnosis = 0 # 初始为零，方便其他修正判断是否进行了催眠
    if target_data.sp_flag.unconscious_h in [4,5,6,7] and judge_data_type == "S" and judge < judge_data_value:
        # 性骚扰级别需要至少50%催眠深度，性行为需要2级催眠和至少100%催眠深度
        if (
            ((_("骚扰") in instruct_name or _("亲吻") in instruct_name) and target_data.hypnosis.hypnosis_degree >= 50) or 
            (character_data.talent[332] and target_data.hypnosis.hypnosis_degree >= 100)
        ):
            # 实行值不够的差值为
            unenough = judge_data_value - judge
            # 催眠基础补正为100，再不足的部分用理智折算为实行值
            if unenough <= 100:
                judge_hypnosis = 100
                sanity_point_cost = 10
            else:
                # 1理智折算为10实行值
                judge_hypnosis = unenough
                sanity_point_cost = round(unenough / 10)
            # 最后的总结算
            if sanity_point_cost <= character_data.sanity_point:
                judge += judge_hypnosis
                calculation_text += _("+催眠(+{0},消耗{1}理智)").format(judge_hypnosis, sanity_point_cost)
                character_data.sanity_point -= sanity_point_cost
                character_data.pl_ability.today_sanity_point_cost += sanity_point_cost
            else:
                calculation_text += _("+催眠(+0,理智不足,催眠解除)")
                target_data.sp_flag.unconscious_h = 0

    # debug模式修正
    if cache.debug_mode == True:
        judge += 99999
        calculation_text += _("+debug模式(+99999)")

    # 是否通过
    if judge >= judge_data_value:
        final_judge = 1
    else:
        final_judge = 0
    judge_rate = judge / judge_data_value

    # 是否进行相关信息的绘制与结算
    if not not_draw_flag:

        # 询问信息
        ask_text = ""
        if instruct_name == _("亲吻") and target_data.talent[4]:
            ask_text += _("\n\n 是否要夺走{0}的初吻？").format(target_data.name)
        if instruct_name == _("口交") and target_data.talent[4]:
            ask_text += _("\n\n 是否要用阴茎夺走{0}的初吻？").format(target_data.name)
        elif instruct_name == _("性交") and target_data.talent[0]:
            ask_text += _("\n\n 是否要夺走{0}的处女？").format(target_data.name)
        elif instruct_name == _("A性交") and target_data.talent[1]:
            ask_text += _("\n\n 是否要夺走{0}的A处女？").format(target_data.name)
        # 询问戴套，True为已戴套
        if character_data.h_state.body_item[13][1]:
            condom_flag = True
        else:
            condom_flag = False
        if instruct_name == _("性交"):
            # 避孕套、已显示过该信息，以上可直接通过
            if (
                character_data.h_state.body_item[13][1] or
                target_data.h_state.condom_info_show_flag == False
                ):
                pass
            else:
                # 无意识
                if target_data.sp_flag.unconscious_h:
                    ask_text += _("当前正在对{0}无意识奸，是否不戴套？\n").format(target_data.name)
                # 妊娠合意
                elif target_data.talent[14]:
                    ask_text += _("{0}已经做好了随时都可以怀孕的准备，是否不戴套？\n").format(target_data.name)
                # 避孕中出合意+事前避孕药
                elif target_data.talent[13] and target_data.h_state.body_item[11][1]:
                    ask_text += _("{0}已经吃过事前避孕药了，所以内射也不会怀孕，是否不戴套？\n").format(target_data.name)
                # 性无知
                elif target_data.talent[222]:
                    ask_text += _("{0}似乎对性和避孕都一无所知，是否不戴套？\n").format(target_data.name)
                elif judge_rate < 0.5:
                    ask_text += _("{0}坚决地要求你必须戴上避孕套，是否坚持不带套？\n").format(target_data.name)
                elif judge_rate < 1:
                    ask_text += _("{0}希望你戴上避孕套，是否坚持不带套？\n").format(target_data.name)
                else:
                    ask_text += _("{0}提醒你还没有戴避孕套，但也表示可以不戴就这样继续，是否不带套？\n").format(target_data.name)
                target_data.h_state.condom_info_show_flag = False
        if len(ask_text):
            # 判断态度
            ask_text += _(" (对方的态度：")
            if judge_rate < 0.5:
                ask_text += _("拒绝)\n")
            elif judge_rate < 1:
                ask_text += _("犹豫)\n")
            else:
                ask_text += _("接受)\n")
            while 1:
                return_list = []
                ask_draw = draw.WaitDraw()
                ask_draw.width = 1
                ask_draw.text = ask_text
                ask_draw.draw()

                line_feed.draw()
                line_feed.draw()
                yes_draw = draw.CenterButton(_("[确定]"), _("确定"), window_width / 2)
                yes_draw.draw()
                return_list.append(yes_draw.return_text)
                back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width / 2)
                back_draw.draw()
                line_feed.draw()
                return_list.append(back_draw.return_text)
                yrn = flow_handle.askfor_all(return_list)
                if yrn == back_draw.return_text:
                    return [-1, judge, judge_rate]
                elif yrn == yes_draw.return_text:
                    break

        # 正常直接判定，并输出文本
        if judge_data_type != "V":
            calculation_text += " = " + str(judge) + "\n"
            now_draw = draw.WaitDraw()
            now_draw.width = 1
            now_draw.text = calculation_text
            now_draw.draw()

        # 合意获得的结算，大前提是1.5倍实行值、有意识、非监禁
        if judge_rate >= 1.5 and target_data.sp_flag.unconscious_h == 0 and handle_premise.handle_imprisonment_0(target_character_id):
            agree_draw = draw.WaitDraw()
            agree_draw.width = 1
            draw_text = ""
            if instruct_name == _("亲吻") and target_data.talent[11] == 0:
                target_data.talent[11] = 1
                draw_text += _("\n 获得了{0}的【亲吻合意】\n").format(target_data.name)
            if instruct_name == _("性交") and target_data.talent[12] == 0:
                target_data.talent[12] = 1
                draw_text += _("\n 获得了{0}的【本番合意】\n").format(target_data.name)
            if instruct_name == _("A性交") and target_data.talent[15] == 0:
                target_data.talent[15] = 1
                draw_text += _("\n 获得了{0}的【Ａ性交合意】\n").format(target_data.name)
            if instruct_name == _("U性交") and target_data.talent[16] == 0:
                target_data.talent[16] = 1
                draw_text += _("\n 获得了{0}的【Ｕ性交合意】\n").format(target_data.name)
            # 避孕相关合意
            # 避孕中出合意需要在非处女、不带套、安全期时，通过判定才可获得
            if (
                handle_premise.handle_no_virgin(target_character_id) and
                instruct_name == _("性交") and
                target_data.talent[13] == 0 and
                condom_flag == False and
                handle_premise.handle_reproduction_period_0(target_character_id)
                ):
                target_data.talent[13] = 1
                draw_text += _("\n 获得了{0}的【避孕中出合意】\n").format(target_data.name)
            # 妊娠合意需要在非处女、不带套、非安全期时，通过判定才可获得
            if (
                handle_premise.handle_no_virgin(target_character_id) and
                instruct_name == _("性交") and
                target_data.talent[14] == 0 and
                condom_flag == False and
                (handle_premise.handle_reproduction_period_2(target_character_id) or handle_premise.handle_reproduction_period_3(target_character_id))
                ):
                target_data.talent[14] = 1
                draw_text += _("\n 获得了{0}的【妊娠合意】\n").format(target_data.name)
            if len(draw_text):
                agree_draw.text = draw_text
                agree_draw.draw()

    # 返回判定结果
    return [final_judge, judge, judge_rate]


# def calculation_favorability(character_id: int, target_character_id: int, favorability: int) -> int:
#     """
#     按角色性格和关系计算最终增加的好感值
#     Keyword arguments:
#     character_id -- 角色id
#     target_character_id -- 目标角色id
#     favorability -- 基础好感值
#     Return arguments:
#     int -- 最终的好感值
#     """
#     character_data: game_type.Character = cache.character_data[character_id]
#     target_data: game_type.Character = cache.character_data[target_character_id]
#     fix = 1.0
#     for i in {0, 1, 2, 5, 13, 14, 15, 16}:
#         now_fix = 0
#         if character_data.nature[i] > 50:
#             nature_value = character_data.nature[i] - 50
#             now_fix -= nature_value / 50
#         else:
#             now_fix += character_data.nature[i] / 50
#         if target_data.nature[i] > 50:
#             nature_value = target_data.nature[i] - 50
#             if now_fix < 0:
#                 now_fix *= -1
#                 now_fix += nature_value / 50
#                 now_fix = now_fix / 2
#             else:
#                 now_fix += nature_value / 50
#         else:
#             nature_value = target_data.nature[i]
#             if now_fix < 0:
#                 now_fix += nature_value / 50
#             else:
#                 now_fix -= nature_value / 50
#                 now_fix = now_fix / 2
#         fix += now_fix
#     if character_id in target_data.social_contact_data:
#         fix += target_data.social_contact_data[character_id]
#     favorability *= fix
#     return favorability


def judge_character_time_over_24(character_id: int) -> bool:
    """
    校验角色的时间是否已过24点
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    start_time: datetime.datetime = character_data.behavior.start_time
    end_time = game_time.get_sub_date(minute=character_data.behavior.duration, old_date=start_time)

    if end_time.day != start_time.day:
        return 1
    return 0

def get_character_id_from_adv(adv_id: int) -> int:
    """
    通过剧情id获取角色id
    Keyword arguments:
    adv_id -- 剧情id
    Return arguments:
    int -- 角色id
    """
    for character_id in cache.character_data:
        if cache.character_data[character_id].adv == adv_id:
            return character_id
    return 0