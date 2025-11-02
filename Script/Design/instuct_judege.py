import datetime
from types import FunctionType
from Script.Core import (
    cache_control,
    get_text,
    game_type,
    text_handle,
    flow_handle,
)
from Script.Design import (
    handle_ability,
    map_handle,
    attr_calculation,
    handle_talent,
    handle_premise,
)
from Script.Config import game_config, normal_config
from Script.UI.Moudle import draw

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

    # 状态修正
    # 欲情和快乐为低正修正，恭顺和屈服为高正修正，羞耻和抑郁低小负修正，苦痛和恐怖和反感为高负修正
    add_status_level_sum_s =  attr_calculation.get_status_level(target_data.status_data[12]) + attr_calculation.get_status_level(target_data.status_data[13])
    add_status_level_sum_l =  attr_calculation.get_status_level(target_data.status_data[10]) + attr_calculation.get_status_level(target_data.status_data[15])
    down_status_level_sum_s = attr_calculation.get_status_level(target_data.status_data[16]) + attr_calculation.get_status_level(target_data.status_data[19])
    down_status_level_sum_l = attr_calculation.get_status_level(target_data.status_data[17]) + attr_calculation.get_status_level(target_data.status_data[18]) + attr_calculation.get_status_level(target_data.status_data[20])
    judge_status = add_status_level_sum_s * 5 +  add_status_level_sum_l * 10 - down_status_level_sum_s * 5 - down_status_level_sum_l * 10
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
    # 女儿修正
    judge_daughter = target_data.talent[451] * 100
    judge += judge_daughter
    if judge_daughter:
        calculation_text += _("+女儿(+") + str(judge_daughter) + ")"

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
            judge += 100
            calculation_text += _("+性无知(+100)")
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
        # 找博士逆推自慰修正
        if target_data.sp_flag.npc_masturebate_for_player:
            judge += 50
            calculation_text += _("+找博士逆推(+50)")

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
            if instruct_name in {_("群交"), _("隐奸")}:
                judge_other_people = 60 + 60 * other_chara_count
            elif judge_data_type == "S":
                judge_other_people = 40 + 40 * other_chara_count
            else:
                judge_other_people = 25 + 25 * other_chara_count
            # 露出修正
            adjust = handle_ability.get_ability_adjust(target_data.ability[34])
            judge_other_people = int(judge_other_people * (adjust - 1.6))
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
            judge += 9999
            calculation_text += _("+监禁中(+9999)")

        # 睡眠修正
        if handle_premise.handle_unconscious_flag_1(target_character_id):
            judge += 9999
            calculation_text += _("+睡眠(+9999)")

        # 时停修正
        if handle_premise.handle_unconscious_flag_3(target_character_id):
            judge += 9999
            calculation_text += _("+时停(+9999)")

    # 处女修正
    if instruct_name == _("性交") and handle_premise.handle_have_virgin(target_character_id) and handle_premise.handle_self_sexual_ignorance_0(target_character_id):
        judge -= 250
        calculation_text += _("+处女(-250)")

    # A处女修正
    if instruct_name == _("A性交") and target_data.talent[1] and handle_premise.handle_self_sexual_ignorance_0(target_character_id):
        judge -= 350
        calculation_text += _("+Ａ处女(-350)")

    # U处女修正
    if instruct_name == _("U性交") and target_data.talent[2] and handle_premise.handle_self_sexual_ignorance_0(target_character_id):
        judge -= 400
        calculation_text += _("+Ｕ处女(-400)")

    # 初吻修正
    if instruct_name == _("亲吻") and target_data.talent[4] and handle_premise.handle_self_sexual_ignorance_0(target_character_id):
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

    # 催眠系能力的最后补正
    judge_hypnosis = 0 # 初始为零，方便其他修正判断是否进行了催眠
    # 需要在催眠状态中，性爱判定
    if target_data.sp_flag.unconscious_h in {4,5,6,7} and judge_data_type == "S":
        # 完全催眠直接通过
        if handle_premise.handle_self_has_been_complete_hypnosis(target_character_id):
            judge_hypnosis = 9999
            judge += judge_hypnosis
            calculation_text += _("+完全催眠(+9999)")
        # 否则仅在实行值不足时生效，需要消耗理智
        elif judge < judge_data_value:
            # 性骚扰级别需要至少50%催眠深度，性行为需要2级催眠和至少100%催眠深度
            if (
                ((_("骚扰") in instruct_name or _("亲吻") in instruct_name) and handle_premise.handle_self_has_been_primary_hypnosis(target_character_id)) or 
                (handle_premise.handle_intermediate_hypnosis(character_id) and handle_premise.handle_self_has_been_deep_hypnosis(target_character_id))
            ):
                # 实行值不够的差值为
                unenough = judge_data_value - judge
                # 催眠基础补正为100，再不足的部分用理智折算为实行值
                if unenough <= 100:
                    judge_hypnosis = 100
                    sanity_point_cost = 5
                else:
                    # 刚好补齐需要的差值
                    judge_hypnosis = unenough
                    # 深层催眠下，1理智折算为20实行值
                    if handle_premise.handle_self_has_been_deep_hypnosis(target_character_id):
                        sanity_point_cost = round(unenough / 20)
                    # 否则1理智折算为10实行值
                    else:
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
                    handle_premise.settle_chara_unnormal_flag(character_data.target_character_id, 5)
                    handle_premise.settle_chara_unnormal_flag(character_data.target_character_id, 6)

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
                # ask_draw.width = 1
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
            # now_draw.width = 1
            now_draw.text = calculation_text
            now_draw.draw()

        # 合意获得的结算，大前提是1.5倍实行值、有意识、非监禁
        if judge_rate >= 1.5 and handle_premise.handle_unconscious_flag_0(target_character_id) and handle_premise.handle_imprisonment_0(target_character_id):
            agree_draw = draw.WaitDraw()
            # agree_draw.width = 1
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

