import random
from types import FunctionType
from Script.Core import cache_control, constant, game_type, get_text
from Script.Design import attr_calculation, handle_premise, talk, settle_behavior
from Script.UI.Moudle import draw
from Script.Config import game_config, normal_config
from Script.UI.Panel import achievement_panel, ejaculation_panel

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
width = normal_config.config_normal.text_width
""" 屏幕宽度 """
_: FunctionType = get_text._
""" 翻译api """

def character_get_second_behavior(character_id: int, second_behavior_id: str, reset: bool = False):
    """
    角色获得二段行为
    Keyword arguments:
    character_id -- 角色id
    second_behavior_id -- 二段行为id
    reset -- 是否重置该二段行为，默认为False
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if second_behavior_id not in character_data.second_behavior:
        character_data.second_behavior[second_behavior_id] = 0
    if reset:
        character_data.second_behavior[second_behavior_id] = 0
        # 如果该二段行为在必须计算结算列表中，则不再进行显示结算
        if second_behavior_id in game_config.config_behavior_must_settle_cid_list:
            if second_behavior_id in character_data.must_settle_second_behavior_id_list:
                character_data.must_settle_second_behavior_id_list.remove(second_behavior_id)
        # 如果该二段行为在必须显示结算列表中，则不再进行显示结算
        if second_behavior_id in game_config.config_behavior_must_show_cid_list:
            if second_behavior_id in character_data.must_show_second_behavior_id_list:
                character_data.must_show_second_behavior_id_list.remove(second_behavior_id)
    else:
        character_data.second_behavior[second_behavior_id] = 1
        # 如果该二段行为在必须计算结算列表中，则进行显示结算
        if second_behavior_id in game_config.config_behavior_must_settle_cid_list:
            character_data.must_settle_second_behavior_id_list.append(second_behavior_id)
        # 如果该二段行为在必须显示结算列表中，则进行显示结算
        if second_behavior_id in game_config.config_behavior_must_show_cid_list:
            character_data.must_show_second_behavior_id_list.append(second_behavior_id)

def check_second_effect(
        character_id: int,
        change_data: game_type.CharacterStatusChange,
        pl_to_npc: bool = False,
):
    """
    处理第二结算
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    pl_to_npc -- 玩家对NPC的行为结算
    """
    # print("进入第二结算")
    orgasm_list = []
    mark_list = []
    item_list = []
    character_data: game_type.Character = cache.character_data[character_id]
    for second_behavior_id in character_data.second_behavior:
        if "orgasm" in second_behavior_id:
            orgasm_list.append(second_behavior_id)
        if "mark" in second_behavior_id:
            mark_list.append(second_behavior_id)
    # for cid in game_config.config_body_item:
    #     body_item_data = game_config.config_body_item[cid]
    #     item_list.append(body_item_data.behavior_id)

    # 玩家检测自己
    if character_id == 0:
        character_data = cache.character_data[0]
        # 高潮结算
        orgasm_judge(character_id, change_data)
        # 道具结算
        item_effect(character_id)
        # 进行结算
        second_behavior_effect(character_id, change_data)
        # NPC的刻印结算
        change_data.target_change.setdefault(character_data.target_character_id, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[character_data.target_character_id]
        mark_effect(character_data.target_character_id, target_change)
        # 单独遍历结算刻印
        second_behavior_effect(character_data.target_character_id, target_change, mark_list)

    # NPC自己检测自己
    if character_id != 0:
        # 初见和每日招呼结算
        judge_character_first_meet(character_id)
        # 阴茎位置结算
        insert_position_effect(character_id, change_data)
        # 道具结算
        item_effect(character_id)
        # 进行结算
        second_behavior_effect(character_id, change_data)
        # 高潮结算
        orgasm_judge(character_id, change_data)
        # 单独遍历结算高潮
        second_behavior_effect(character_id, change_data, orgasm_list)

        # 刻印结算
        mark_effect(character_id, change_data)
        # 单独遍历结算刻印
        second_behavior_effect(character_id, change_data, mark_list)


def second_behavior_effect(
        character_id: int,
        change_data: game_type.CharacterStatusChange,
        second_behavior_list: list = [],
        ):
    """
    触发二段行为的口上与效果
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    second_behavior_list -- 仅计算该范围内的二段行为id列表，默认为[]
    """
    character_data: game_type.Character = cache.character_data[character_id]

    # 检测是否与玩家处于同一位置#
    if (
            character_data.position != cache.character_data[0].position
            and character_data.behavior.move_src != cache.character_data[0].position
    ):
        talk.must_show_talk_check(character_id)
        must_settle_check(character_id)
        return

    # 如果没有任何二段行为，则直接返回
    if not any(character_data.second_behavior.values()):
        return

    # 遍历二段行为id，进行结算
    for second_behavior_id, behavior_data in character_data.second_behavior.items():
        if behavior_data != 0:
            if second_behavior_list and second_behavior_id not in second_behavior_list:
                continue
            # 触发二段行为的口上
            talk.handle_second_talk(character_id, second_behavior_id)
            # 如果没找到对应的结算效果，则直接跳过
            if second_behavior_id not in game_config.config_behavior_effect_data:
                print(f"debug second_behavior_id = {second_behavior_id}没有找到对应的结算效果")
                continue
            # 遍历该二段行为的所有结算效果，挨个触发
            for effect_id in game_config.config_behavior_effect_data[second_behavior_id]:
                # 综合数值结算判定
                # 如果effect_id是str类型，则说明是综合数值结算
                if isinstance(effect_id, str) and "CVE" in effect_id:
                    effect_all_value_list = effect_id.split("_")[1:]
                    settle_behavior.handle_comprehensive_value_effect(character_id, effect_all_value_list, change_data)
                else:
                    if effect_id not in constant.settle_second_behavior_effect_data:
                        print(f"debug second_behavior_id = {second_behavior_id}，effect_id = {effect_id}没有找到对应的结算效果")
                        continue
                    constant.settle_second_behavior_effect_data[effect_id](character_id, change_data)
            # print(f"debug {character_data.name}触发二段行为效果，behavior_id = {behavior_id}")
            # 触发后该行为值归零
            character_data.second_behavior[second_behavior_id] = 0

def must_settle_check(character_id: int):
    """
    检查是否有必须计算但不必须显示的空白结算
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    # 遍历所有必须计算的二段行为
    for behavior_id in character_data.must_settle_second_behavior_id_list:
        # 跳过值为0的行为
        if behavior_id in character_data.second_behavior and character_data.second_behavior[behavior_id] == 0:
            continue
        # 遍历该二段行为的所有结算效果，挨个触发，但因为不在结算阶段，所以不会显示具体的结算数据
        change_data = game_type.CharacterStatusChange()
        for effect_id in game_config.config_behavior_effect_data[behavior_id]:
            # 综合数值结算判定
            # 如果effect_id是str类型，则说明是综合数值结算
            if isinstance(effect_id, str) and "CVE" in effect_id:
                effect_all_value_list = effect_id.split("_")[1:]
                settle_behavior.handle_comprehensive_value_effect(character_id, effect_all_value_list, change_data)
            else:
                constant.settle_second_behavior_effect_data[effect_id](character_id, change_data)
        # 触发后该行为值归零
        character_data.second_behavior[behavior_id] = 0
    character_data.must_settle_second_behavior_id_list = []

def judge_character_first_meet(character_id: int):
    """
    判断初见和每日招呼\n
    Keyword arguments:
    character_id -- 角色id\n
    Return arguments:
    bool -- 本次update时间切片内活动是否已完成
    """
    character_data: game_type.Character = cache.character_data[character_id]
    pl_character_data: game_type.Character = cache.character_data[0]

    # 需要NPC状态6正常，且不是睡觉状态，玩家不在男隐或双隐的隐奸中，且没在睡觉
    if (
        handle_premise.handle_normal_6(character_id) and
        handle_premise.handle_action_not_sleep(character_id) and
        not handle_premise.handle_hidden_sex_mode_3_or_4(0) and
        handle_premise.handle_action_not_sleep(0)
        ):
        # 优先输出初见，次要输出每日招呼
        if character_data.first_record.first_meet and character_data.position == pl_character_data.position:
            character_get_second_behavior(character_id, "first_meet")
            character_data.first_record.first_meet = 0
            character_data.first_record.day_first_meet = 0
        elif character_data.first_record.day_first_meet and character_data.position == pl_character_data.position:
            # 如果是要早安问候的助理，则不每日招呼
            if handle_premise.handle_assistant_morning_salutation_on(character_id):
                pass
            else:
                character_get_second_behavior(character_id, "day_hello")
            character_data.first_record.day_first_meet = 0
            # 判断上交内裤与袜子
            if handle_premise.handle_wear_pan(character_id) and handle_premise.handle_ask_give_pan_everyday(character_id):
                character_get_second_behavior(character_id, "give_pan_in_day_first_meet")
            if handle_premise.handle_wear_socks(character_id) and handle_premise.handle_ask_give_socks_everyday(character_id):
                character_get_second_behavior(character_id, "give_socks_in_day_first_meet")


def insert_position_effect(character_id: int, change_data: game_type.CharacterStatusChange):
    """
    处理第二结算中的阴茎位置结算
    Keyword arguments:
    character_id -- 角色id
    change_data: game_type.CharacterStatusChange,
    """
    # 导入常用结算函数，避免循环导入
    from Script.Settle.common_default import base_chara_experience_common_settle

    character_data: game_type.Character = cache.character_data[character_id]
    pl_character_data: game_type.Character = cache.character_data[0]
    # 当前不在H中，当前有阴茎插入，则重置插入
    if not handle_premise.handle_self_is_h(character_id) and character_data.h_state.insert_position != -1:
        # 重置插入位置
        character_data.h_state.insert_position = -1
        character_data.h_state.insert_position_change_save = -1
    # 当前有阴茎插入、当前位置为玩家位置
    if (
        character_data.h_state.insert_position != -1 and
        character_data.position == pl_character_data.position
        ):
        # 非群交模式
        if handle_premise.handle_group_sex_mode_off(character_id):
            # 如果不等于，则说明是本次指令改变了插入位置，因此不触发二段结算
            if character_data.h_state.insert_position_change_save != character_data.h_state.insert_position:
                character_data.h_state.insert_position_change_save = character_data.h_state.insert_position
            else:
                # 区分是身体还是服装
                if character_data.h_state.insert_position < 20:
                    second_behavior_id = f"penis_in_body_{character_data.h_state.insert_position}"
                else:
                    second_behavior_id = f"penis_in_cloth_{character_data.h_state.insert_position - 20}"
                    # 如果是下衣，则进一步区分是裙子还是裤子
                    if character_data.h_state.insert_position == 28:
                        if handle_premise.handle_wear_skirt(character_id):
                            second_behavior_id += "_skirt"
                        else:
                            second_behavior_id += "_trousers"
                character_get_second_behavior(character_id, second_behavior_id)
        # 如果玩家当前有性交姿势数据
        if pl_character_data.h_state.current_sex_position != -1:
            # 自己增加对应姿势的经验
            exp_id = 140 + pl_character_data.h_state.current_sex_position
            base_chara_experience_common_settle(character_id, exp_id, change_data = change_data)
            # 玩家增加对应姿势的经验
            base_chara_experience_common_settle(0, exp_id, change_data_to_target_change = change_data)


def orgasm_judge(character_id: int, change_data: game_type.CharacterStatusChange, skip_undure: bool = False):
    """
    判断第二结算中的高潮，都发生哪些高潮，各多少次
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    skip_undure -- 是否跳过忍耐高潮的结算
    """
    # print()
    character_data: game_type.Character = cache.character_data[character_id]
    # print(f"进入{character_data.name}的高潮结算")

    # 检测射精
    if character_id == 0:
        if character_data.eja_point >= character_data.eja_point_max or skip_undure:
            # 如果已经没有精液了则只能进行普通射精
            if handle_premise.handle_pl_semen_le_2(0):
                character_get_second_behavior(0, "p_orgasm_small")
            else:
                # 忍住射精
                if not skip_undure:
                    endure_flag = ejaculation_panel.show_endure_ejaculation_panel()
                    if endure_flag:
                        return
                # 普
                if character_data.h_state.endure_not_shot_count == 0:
                    character_get_second_behavior(0, "p_orgasm_small")
                # 超强
                elif character_data.h_state.endure_not_shot_count >= 4:
                    character_get_second_behavior(0, "p_orgasm_strong")
                # 强
                else:
                    character_get_second_behavior(0, "p_orgasm_normal")
            character_data.eja_point = 0
            now_draw = ejaculation_panel.Ejaculation_Panel(width)
            now_draw.draw()
            line = draw.LineDraw("-", width)
            line.draw()
    else:
        normal_orgasm_dict = {}  # 高潮结算字典
        extra_orgasm_dict = {}  # 额外高潮结算字典
        un_count_orgasm_dict = {}  # 不计数高潮结算字典
        orgasm_part_list = []  # 高潮部位列表
        for state_id in game_config.config_character_state:
            if game_config.config_character_state[state_id].type == 0:
                orgasm_part_list.append(state_id)
        for orgasm in orgasm_part_list:
            # 跳过射精槽
            if orgasm == 3:
                continue
            # 10级前检测人物的各感度数据是否等于该人物的高潮记录程度数据
            # now_data -- 当前高潮程度
            # pre_data -- 记录里的前高潮程度
            # un_count_data -- 不计数的本次临时高潮数
            # extra_add -- 额外高潮次数
            now_data = attr_calculation.get_status_level(character_data.status_data[orgasm])
            pre_data = character_data.h_state.orgasm_level[orgasm]
            un_count_data = 0
            extra_add = 0
            # 字典初始化
            normal_orgasm_dict[orgasm] = 0
            extra_orgasm_dict[orgasm] = 0
            un_count_orgasm_dict[orgasm] = 0
            # 饮精绝顶
            if orgasm == 21 and character_data.talent[31]:
                if character_data.h_state.shoot_position_body in [2, 15]:
                    un_count_data += 1
                    # 触发了饮精绝顶后当场重置射精位置，以免重复触发
                    character_data.h_state.shoot_position_body = -1
            un_count_orgasm_dict[orgasm] = un_count_data
            # 如果已经到了10级，则进行额外高潮结算
            if pre_data >= 10:
                character_data.h_state.extra_orgasm_feel.setdefault(orgasm, 0)
                change_data.status_data.setdefault(orgasm, 0)
                character_data.h_state.extra_orgasm_feel[orgasm] += int(change_data.status_data[orgasm])
                # 额外高潮次数
                extra_count = pre_data - 10
                # 基础阈值为2w，每次高潮则乘以0.9的若干次方
                now_threshold = 20000 * (0.9 ** extra_count)
                now_threshold = max(1000, now_threshold)
                # 如果超过阈值，则进行额外高潮结算
                extra_add = int(character_data.h_state.extra_orgasm_feel[orgasm] // now_threshold)
                now_data = pre_data + extra_add
                character_data.h_state.extra_orgasm_feel[orgasm] -= int(extra_add * now_threshold)
                character_data.h_state.extra_orgasm_count += extra_add
                extra_orgasm_dict[orgasm] = extra_add
            # 计算普通高潮次数
            normal_orgasm_dict[orgasm] = now_data - pre_data
        # 高潮结算函数
        orgasm_settle(character_id, change_data, normal_orgasm_dict, extra_orgasm_dict, un_count_orgasm_dict)
        # 寸止失败解放
        if character_data.h_state.orgasm_edge == 3:
            character_data.h_state.orgasm_edge = 2
            orgasm_settle(character_id, change_data, normal_orgasm_dict, extra_orgasm_dict, character_data.h_state.orgasm_edge_count)


def orgasm_settle(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
    normal_orgasm_dict: dict = {},
    extra_orgasm_dict: dict = {},
    un_count_orgasm_dict: dict = {},
    ):
    """
    处理第二结算中的高潮结算
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    normal_orgasm_dict -- 普通高潮字典
    extra_orgasm_dict -- 额外高潮字典
    un_count_orgasm_dict -- 不计数高潮字典
    """
    # 导入常用结算函数，避免循环导入
    from Script.Settle.common_default import base_chara_experience_common_settle
    from Script.UI.Panel.manage_power_system_panel import store_power_by_human_power

    character_data = cache.character_data[character_id]
    # print(f"进入{character_data.name}的高潮结算")
    part_dict = {0 : "s", 1 : "b", 2 : "c", 3 : "p", 4 : "v", 5 : "a", 6 : "u", 7 : "w", 21 : "m", 22 : "f", 23 : "h"}
    degree_dict = {0 : "small", 1 : "normal", 2 : "strong", 3 : "super"}

    part_count = 0  # 部位高潮计数
    tem_orgasm_set = set()  # 临时高潮部位集合
    for orgasm in part_dict:
        # 跳过射精槽
        if orgasm == 3:
            continue

        pre_data = character_data.h_state.orgasm_level[orgasm] # 记录里的前高潮程度

        normal_orgasm_data = 0
        if orgasm in normal_orgasm_dict:
            normal_orgasm_data = normal_orgasm_dict[orgasm]
        extra_orgasm_data = 0
        if orgasm in extra_orgasm_dict:
            extra_orgasm_data = extra_orgasm_dict[orgasm]
        un_count_orgasm_data = 0
        if orgasm in un_count_orgasm_dict:
            un_count_orgasm_data = un_count_orgasm_dict[orgasm]

        # 如果已经进入额外高潮，则将额外高潮次数加入到高潮次数中
        if extra_orgasm_data > 0:
            now_data = pre_data + extra_orgasm_data
        # 否则加入普通高潮次数
        else:
            now_data = pre_data + normal_orgasm_data

        # 如果当前高潮程度大于记录的高潮程度，或者有额外高潮，则进行高潮结算
        if normal_orgasm_data > 0 or extra_orgasm_data > 0 or un_count_orgasm_data > 0:
            # 高潮次数统计
            climax_count = normal_orgasm_data + un_count_orgasm_data
            # 刷新记录
            character_data.h_state.orgasm_level[orgasm] = now_data
            # 时停状态下
            if handle_premise.handle_unconscious_flag_3(character_id):
                # 绝顶计入寸止计数
                character_data.h_state.time_stop_orgasm_count.setdefault(orgasm, 0)
                character_data.h_state.time_stop_orgasm_count[orgasm] += climax_count
                continue
            # 如果开启了绝顶寸止，则进行寸止结算，然后跳过
            if handle_premise.handle_self_orgasm_edge(character_id):
                # 根据技巧而绝顶的能够进行寸止的次数限制
                orgasm_edge_success_flag = judge_orgasm_edge_success(character_id)
                # 寸止失败
                if not orgasm_edge_success_flag:
                    # 进入解放状态，返回以便重新进行结算
                    character_data.h_state.orgasm_edge = 3
                    return
                # 绝顶计入寸止计数
                character_data.h_state.orgasm_edge_count.setdefault(orgasm, 0)
                character_data.h_state.orgasm_edge_count[orgasm] += climax_count
                # 赋予寸止行为
                second_behavior_id = f"{part_dict[orgasm]}_orgasm_edge"
                character_get_second_behavior(character_id, second_behavior_id)
                continue
            # 群交状态下
            if handle_premise.handle_group_sex_mode_on(character_id):
                # 成就统计
                cache.achievement.group_sex_record.setdefault(2, [])
                if character_id not in cache.achievement.group_sex_record[2]:
                    cache.achievement.group_sex_record[2].append(character_id)
            # 隐奸状态下
            elif handle_premise.handle_hidden_sex_mode_ge_1(character_id):
                # 成就统计
                cache.achievement.hidden_sex_record.setdefault(4, 0)
                cache.achievement.hidden_sex_record[4] += 1
            # 露出状态下
            elif handle_premise.handle_exhibitionism_sex_mode_ge_1(character_id):
                # 成就统计
                cache.achievement.exhibitionism_sex_record.setdefault(4, 0)
                cache.achievement.exhibitionism_sex_record[4] += 1
            # 睡奸状态下
            if handle_premise.handle_unconscious_flag_1(character_id):
                # 成就统计
                cache.achievement.sleep_sex_record.setdefault(3, 0)
                cache.achievement.sleep_sex_record[3] += 1
            # 该部位高潮计数+1
            part_count += 1
            # 加入高潮部位记录
            tem_orgasm_set.add(orgasm)
            # 开始根据概率计算
            for i in range(climax_count):
                # 判断高潮程度
                now_degree = judge_orgasm_degree(now_data)
                # 强绝顶需要该部位敏感度至少为3级
                if now_degree >= 2:
                    if orgasm <= 7:
                        ability_id = orgasm
                    else:
                        ability_id = orgasm + 79
                    if character_data.ability[ability_id] < 3:
                        now_degree = 1
                # 赋予二次行为
                second_behavior_id = f"{part_dict[orgasm]}_orgasm_{degree_dict[now_degree]}"
                character_get_second_behavior(character_id, second_behavior_id)
            # 绝顶解放状态下（含寸止解放与时停解放），如果次数大于等于3，则触发超强绝顶
            if handle_premise.handle_self_orgasm_edge_relase_or_time_stop_orgasm_relase(character_id) and climax_count >= 3:
                # 超强绝顶需要该部位敏感度至少为6级，否则变为强绝顶
                now_degree = 3
                if orgasm <= 7:
                    ability_id = orgasm
                else:
                    ability_id = orgasm + 79
                if character_data.ability[ability_id] < 6:
                    now_degree = 2
                second_behavior_id = f"{part_dict[orgasm]}_orgasm_{degree_dict[now_degree]}"
                character_get_second_behavior(character_id, second_behavior_id)
            # B绝顶喷乳，需要乳汁量到80%
            if orgasm == 1 and handle_premise.handle_milk_ge_80(character_id):
                # now_draw.text += _("\n触发B绝顶喷乳\n")
                character_get_second_behavior(character_id, "b_orgasm_to_milk")
            # U绝顶排尿，需要尿意条到80%
            if orgasm == 6 and handle_premise.handle_urinate_ge_80(character_id):
                # now_draw.text += _("\n触发U绝顶排尿\n")
                character_get_second_behavior(character_id, "u_orgasm_to_pee")
            # 如果发生了额外高潮，则进行额外高潮结算
            if extra_orgasm_data > 0:
                # now_draw.text += _("\n触发额外高潮\n")
                character_get_second_behavior(character_id, "extra_orgasm")
            # now_draw.draw()

    if part_count >= 1:
        # 饮精绝顶经验
        if character_data.h_state.shoot_position_body in [2, 15]:
            base_chara_experience_common_settle(character_id, 111, change_data=change_data)
    # 如果部位高潮计数大于等于2，则结算多重绝顶
    if part_count >= 2:
        second_behavior_id = f"plural_orgasm_{part_count}"
        character_get_second_behavior(character_id, second_behavior_id)
        character_data.h_state.plural_orgasm_set = tem_orgasm_set.copy()
        # 结算成就
        if part_count >= 2:
            achievement_panel.achievement_flow(_("绝顶"), 1221)
        if part_count >= 6:
            achievement_panel.achievement_flow(_("绝顶"), 1222)
        if part_count >= 10:
            achievement_panel.achievement_flow(_("绝顶"), 1223)
        # 如果在人力发电室中，则增加人力发电量
        if handle_premise.handle_in_human_power_room(character_id):
            draw_flag = False
            # 如果和玩家在同一位置，则进行显示
            if handle_premise.handle_in_player_scene(character_id):
                draw_flag = True
            store_power_by_human_power(part_count + 3, character_id, draw_flag)

def judge_orgasm_degree(level_count: int) -> int:
    """
    判断高潮程度
    Keyword arguments:
    level_count -- 高潮次数，10级以下为当前等级，以上则为10+额外高潮次数
    Return arguments:
    int -- 高潮程度，0小绝顶，1普通绝顶，2强绝顶，3超强绝顶
    """
    # 小、普、强的基础概率
    base_probability = [0.98, 0.02, 0.00]
    # 开始根据高潮次数计算概率
    for _ in range(level_count - 1):
        # 前半段减少小的，增加普的和强的
        if base_probability[0] > 0:
            base_probability[0] -= 0.12
            base_probability[1] += 0.10
            base_probability[2] += 0.02
        # 后半段减少普的0.05，增加强的0.05
        else:
            base_probability[1] -= 0.05
            base_probability[2] += 0.05
    # 确保概率不为负数
    base_probability = [max(0, p) for p in base_probability]
    # 随机抽取概率
    random_num = random.uniform(0, sum(base_probability))
    # 判断高潮程度
    if random_num < base_probability[0]:
        return 0
    elif random_num < base_probability[0] + base_probability[1]:
        return 1
    else:
        return 2


def judge_orgasm_edge_success(character_id: int) -> bool:
    """
    判断高潮寸止是否成功
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    bool -- 是否成功
    """
    orgasm_edge_success_flag = False
    character_data: game_type.Character = cache.character_data[character_id]
    # 目前的高潮寸止数量，同一部位寸止次数越多，成功率越低
    all_orgasm_edge_count = 0
    for key, value in character_data.h_state.orgasm_edge_count.items():
        all_orgasm_edge_count += value * value
    # 玩家的高潮寸止技巧
    pl_character_data: game_type.Character = cache.character_data[0]
    skill_ability_lv = pl_character_data.ability[30]
    info_draw_text = "\n"
    over_count = skill_ability_lv * 3 - all_orgasm_edge_count
    # 如果次数小于技巧等级*3，则成功
    if over_count >= 0:
        orgasm_edge_success_flag = True
        if over_count <= 2:
            info_draw_text += _("成功寸止了{0}的绝顶，但差不多也到了能控制住的极限了，还是尽快释放出来比较好\n").format(character_data.name)
        else:
            info_draw_text += _("成功寸止了{0}的绝顶\n").format(character_data.name)
    # 否则，每超出一次，则有20%的概率失败
    else:
        fail_rate = 0.2 * over_count * -1
        random_num = random.uniform(0, 1)
        if random_num < fail_rate:
            orgasm_edge_success_flag = False
            info_draw_text += _("尝试寸止{0}的绝顶，但失败了\n").format(character_data.name)
        else:
            orgasm_edge_success_flag = True
            info_draw_text += _("成功寸止了{0}的绝顶，但已经超过了能控制住的极限，随时都可能释放出来\n").format(character_data.name)
    # 绘制提示信息
    info_draw = draw.NormalDraw()
    info_draw.text = info_draw_text
    info_draw.draw()
    return orgasm_edge_success_flag

def get_now_state_all_value_and_text_from_mark_up_data(mark_up_id: int, character_id: int) -> tuple:
    """
    从刻印数据中获取刻印的总值和提示文本
    Keyword arguments:
    mark_up_id -- 刻印id
    character_id -- 角色id
    Return arguments:
    tuple -- 总值,提示文本
    """
    # 本地化常用对象，减少每次循环访问全局模块属性的成本
    character_data: game_type.Character = cache.character_data[character_id]
    character_status_data = character_data.status_data
    mark_up_data_need_state_list = game_config.config_mark_up_data_need_state_list[mark_up_id]
    mark_up_data_all_value = 0
    mark_up_data_text = ""
    for need_state in mark_up_data_need_state_list:
        # 跳过空值
        if need_state == '0':
            continue
        # 如果长度为2，说明有权重调整
        if len(need_state) == 2:
            state_id = need_state[0]
            adjust = need_state[1]
            # 计算当前状态值
            now_state_value = int(character_status_data[state_id] * adjust)
            mark_up_data_all_value += now_state_value
            mark_up_data_text += f" {game_config.config_character_state[state_id].name}*{adjust} = {now_state_value} "
        else:
            state_id = need_state[0]
            now_state_value = character_status_data[state_id]
            mark_up_data_all_value += now_state_value
            mark_up_data_text += f" {game_config.config_character_state[state_id].name} = {now_state_value} "
    return mark_up_data_all_value, mark_up_data_text

def get_now_juel_all_value_and_text_from_mark_down_data(mark_down_id: int, character_id: int) -> tuple:
    """
    从刻印数据中获取刻印的总值和提示文本
    Keyword arguments:
    mark_down_id -- 刻印id
    character_id -- 角色id
    Return arguments:
    tuple -- 总值,提示文本
    """
    character_data: game_type.Character = cache.character_data[character_id]
    mark_down_data = game_config.config_mark_down_data[mark_down_id]
    mark_down_data_need_juel_list = []
    mark_down_data_need_juel_list.append(mark_down_data.need_juel_1)
    mark_down_data_need_juel_list.append(mark_down_data.need_juel_2)
    mark_down_data_need_juel_list.append(mark_down_data.need_juel_3)
    # 如果有1号，则替换为全快感珠
    if '1' in mark_down_data_need_juel_list:
        mark_down_data_need_juel_list.remove('1')
        for state_id in game_config.config_character_state:
            if game_config.config_character_state[state_id].type == 0:
                mark_down_data_need_juel_list.append(str(state_id))
    mark_down_data_all_value = 0
    mark_down_data_text = ""
    for need_juel in mark_down_data_need_juel_list:
        # 跳过空值
        if need_juel == '0':
            continue
        # 如果存在|符号，说明有权重调整
        if '|' in need_juel:
            juel_id = int(need_juel.split('|')[0])
            adjust = float(need_juel.split('|')[1])
            # 计算当前宝珠值
            now_juel_value = int(character_data.juel[juel_id] * adjust)
            mark_down_data_all_value += now_juel_value
            mark_down_data_text += f" {game_config.config_juel[juel_id].name}*{adjust} = {now_juel_value} "
        else:
            juel_id = int(need_juel)
            now_juel_value = int(character_data.juel[juel_id])
            mark_down_data_all_value += now_juel_value
            mark_down_data_text += f" {game_config.config_juel[juel_id].name} = {now_juel_value} "
    return mark_down_data_all_value, mark_down_data_text

def mark_effect(character_id: int, change_data: game_type.CharacterStatusChange):
    """
    处理第二结算中的刻印结算
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """

    # print()
    # print("进入刻印结算")
    character_data: game_type.Character = cache.character_data[character_id]
    # print(f"name = {character_data.name},change_data.status_data = {change_data.status_data}")
    now_draw = draw.WaitDraw()
    now_draw_text = ""

    if character_id == 0:
        return

    # 快乐刻印检测单指令全部位总高潮次数，2次快乐1,8次快乐2,16次快乐3
    # 或检测单次H中总绝顶次数，5次快乐1,20次快乐2,50次快乐3
    single_happy_count = 0
    all_happy_count = 0
    for state_id in game_config.config_character_state:
        if game_config.config_character_state[state_id].type == 0:
            single_happy_count += character_data.h_state.orgasm_count[state_id][0]
            all_happy_count += character_data.h_state.orgasm_count[state_id][1]
    # print(f"debug happy_count = {happy_count}")
    if character_data.ability[13] <= 0 and (single_happy_count >= 2 or all_happy_count >= 5):
        character_data.ability[13] = 1
        character_get_second_behavior(character_id, "happy_mark_1")
        # 至少提升为欲望1
        if character_data.ability[33] < 0:
            character_data.ability[33] = 1
            now_draw_text += _("在快乐刻印的影响下，{0}的欲望提升至1级\n").format(character_data.name)
    if character_data.ability[13] <= 1 and (single_happy_count >= 8 or all_happy_count >= 20):
        character_data.ability[13] = 2
        character_get_second_behavior(character_id, "happy_mark_2")
        # 至少提升为欲望3
        if character_data.ability[33] < 3:
            character_data.ability[33] = 3
            now_draw_text += _("在快乐刻印的影响下，{0}的欲望提升至3级\n").format(character_data.name)
    if character_data.ability[13] <= 2 and (single_happy_count >= 16 or all_happy_count >= 50):
        character_data.ability[13] = 3
        character_get_second_behavior(character_id, "happy_mark_3")
        # 至少提升为欲望5
        if character_data.ability[33] < 5:
            character_data.ability[33] = 5
            now_draw_text += _("在快乐刻印的影响下，{0}的欲望提升至5级\n").format(character_data.name)

    # 屈服刻印检测屈服+恭顺+羞耻/5，30000屈服1，50000屈服2，100000屈服3
    yield_count, yield_count_text = get_now_state_all_value_and_text_from_mark_up_data(10, character_id)
    # 进行判断
    if yield_count >= game_config.config_mark_up_data[10].need_state_all_value and character_data.ability[14] <= 0:
        character_data.ability[14] = 1
        character_get_second_behavior(character_id, "yield_mark_1")
        # 至少提升为顺从1
        if character_data.ability[31] < 1:
            character_data.ability[31] = 1
            now_draw_text += _("在屈服刻印的影响下，{0}的顺从提升至1级\n").format(character_data.name)
    if yield_count >= game_config.config_mark_up_data[11].need_state_all_value and character_data.ability[14] <= 1:
        character_data.ability[14] = 2
        character_get_second_behavior(character_id, "yield_mark_2")
        # 至少提升为顺从3
        if character_data.ability[31] < 3:
            character_data.ability[31] = 3
            now_draw_text += _("在屈服刻印的影响下，{0}的顺从提升至3级\n").format(character_data.name)
    if yield_count >= game_config.config_mark_up_data[12].need_state_all_value and character_data.ability[14] <= 2:
        character_data.ability[14] = 3
        character_get_second_behavior(character_id, "yield_mark_3")
        # 至少提升为顺从5
        if character_data.ability[31] < 5:
            character_data.ability[31] = 5
            now_draw_text += _("在屈服刻印的影响下，{0}的顺从提升至5级\n").format(character_data.name)

    # 苦痛刻印检测苦痛，20000苦痛1，40000苦痛2，80000苦痛3
    pain_count, pain_count_text = get_now_state_all_value_and_text_from_mark_up_data(21, character_id)
    # 单次增加量
    if 17 in change_data.status_data:
        pain_count += change_data.status_data[17] * 5
    # 需要非深度无意识，且非心控-苦痛快感化
    if handle_premise.handle_normal_6(character_id) and handle_premise.handle_not_hypnosis_pain_as_pleasure(character_id):
        if pain_count >= game_config.config_mark_up_data[21].need_state_all_value and character_data.ability[15] <= 0:
            character_data.ability[15] = 1
            character_get_second_behavior(character_id, "pain_mark_1")
            # 至少提升为受虐1
            if character_data.ability[36] < 1:
                character_data.ability[36] = 1
                now_draw_text += _("在苦痛刻印的影响下，{0}的受虐提升至1级\n").format(character_data.name)
        if pain_count >= game_config.config_mark_up_data[22].need_state_all_value and character_data.ability[15] <= 1:
            character_data.ability[15] = 2
            character_get_second_behavior(character_id, "pain_mark_2")
            # 至少提升为受虐3
            if character_data.ability[36] < 3:
                character_data.ability[36] = 3
                now_draw_text += _("在苦痛刻印的影响下，{0}的受虐提升至3级\n").format(character_data.name)
        if pain_count >= game_config.config_mark_up_data[23].need_state_all_value and character_data.ability[15] <= 2:
            character_data.ability[15] = 3
            character_get_second_behavior(character_id, "pain_mark_3")
            # 至少提升为受虐5
            if character_data.ability[36] < 5:
                character_data.ability[36] = 5
                now_draw_text += _("在苦痛刻印的影响下，{0}的受虐提升至5级\n").format(character_data.name)

    # 无觉刻印检测无意识下的绝顶，前3级同快乐，后3级仅检测无意识绝顶经验
    if handle_premise.handle_unconscious_flag_ge_1(character_id):
        all_happy_count = 0
        for state_id in game_config.config_character_state:
            if game_config.config_character_state[state_id].type == 0:
                single_happy_count += character_data.h_state.orgasm_count[state_id][0]
        all_happy_count = character_data.experience[78]
        # print(f"debug happy_count = {happy_count}")
        if character_data.ability[19] <= 0 and (single_happy_count >= 2 or all_happy_count >= 5):
            character_data.ability[19] = 1
            character_get_second_behavior(character_id, "unconscious_mark_1")
        if character_data.ability[19] <= 1 and (single_happy_count >= 8 or all_happy_count >= 20):
            character_data.ability[19] = 2
            character_get_second_behavior(character_id, "unconscious_mark_2")
        if character_data.ability[19] <= 2 and (single_happy_count >= 16 or all_happy_count >= 50):
            character_data.ability[19] = 3
            character_get_second_behavior(character_id, "unconscious_mark_3")
        if character_data.ability[19] <= 3 and all_happy_count >= 100:
            character_data.ability[19] = 4
            character_get_second_behavior(character_id, "unconscious_mark_4")
            # 至少提升为欲望6
            if character_data.ability[33] < 6:
                character_data.ability[33] = 6
                now_draw_text += _("在无觉刻印的影响下，{0}的欲望提升至6级\n").format(character_data.name)
        if character_data.ability[19] <= 4 and all_happy_count >= 200:
            character_data.ability[19] = 5
            character_get_second_behavior(character_id, "unconscious_mark_5")
            # 至少提升为欲望7
            if character_data.ability[33] < 7:
                character_data.ability[33] = 7
                now_draw_text += _("在无觉刻印的影响下，{0}的欲望提升至7级\n").format(character_data.name)
        if character_data.ability[19] <= 5 and all_happy_count >= 500:
            character_data.ability[19] = 6
            character_get_second_behavior(character_id, "unconscious_mark_6")
            # 至少提升为欲望8
            if character_data.ability[33] < 8:
                character_data.ability[33] = 8
                now_draw_text += _("在无觉刻印的影响下，{0}的欲望提升至8级\n").format(character_data.name)

    # 恐怖刻印检测恐怖+苦痛/5，20000恐怖1，40000恐怖2，80000恐怖3
    terror_count, terror_count_text = get_now_state_all_value_and_text_from_mark_up_data(41, character_id)
    # 单次增加量
    if 18 in change_data.status_data:
        terror_count += change_data.status_data[18] * 5
    if 17 in change_data.status_data:
        terror_count += change_data.status_data[17]
    if terror_count >= game_config.config_mark_up_data[41].need_state_all_value and character_data.ability[17] <= 0:
        character_data.ability[17] = 1
        character_get_second_behavior(character_id, "terror_mark_1")
    if terror_count >= game_config.config_mark_up_data[42].need_state_all_value and character_data.ability[17] <= 1:
        character_data.ability[17] = 2
        character_get_second_behavior(character_id, "terror_mark_2")
    if terror_count >= game_config.config_mark_up_data[43].need_state_all_value and character_data.ability[17] <= 2:
        character_data.ability[17] = 3
        character_get_second_behavior(character_id, "terror_mark_3")

    # 反发刻印检测反感+抑郁+恐怖+苦痛，10000反发1，30000反发2，80000反发3
    hate_count, hate_count_text = get_now_state_all_value_and_text_from_mark_up_data(51, character_id)
    # 单次增加量
    if 20 in change_data.status_data:
        hate_count += change_data.status_data[20] * 5
    if 18 in change_data.status_data:
        hate_count += change_data.status_data[18]
    if 19 in change_data.status_data:
        hate_count += change_data.status_data[19]
    if 17 in change_data.status_data:
        hate_count += change_data.status_data[17]
    # 需要非深度无意识
    if handle_premise.handle_normal_6(character_id):
        if hate_count >= game_config.config_mark_up_data[51].need_state_all_value and character_data.ability[18] <= 0:
            character_data.ability[18] = 1
            character_get_second_behavior(character_id, "hate_mark_1")
        if hate_count >= game_config.config_mark_up_data[52].need_state_all_value and character_data.ability[18] <= 1:
            character_data.ability[18] = 2
            character_get_second_behavior(character_id, "hate_mark_2")
        if hate_count >= game_config.config_mark_up_data[53].need_state_all_value and character_data.ability[18] <= 2:
            character_data.ability[18] = 3
            character_get_second_behavior(character_id, "hate_mark_3")

    if len(now_draw_text) > 0:
        now_draw_text += "\n"
    now_draw.text = now_draw_text
    now_draw.draw()

def item_effect(character_id: int):
    """
    处理第二结算中的道具结算
    Keyword arguments:
    character_id -- 角色id
    """

    # print()
    # print(f"进入道具结算")
    character_data: game_type.Character = cache.character_data[character_id]

    # NPC对自己进行道具结算
    if character_id != 0:

        # 疑似没有用了，所以注释掉
        # # 玩家在H中正在对该NPC进行交互时，仅计算一遍，避免二次结算
        # if pl_to_npc:
        #     pass
        # elif pl_character_data.target_character_id == character_id and character_data.sp_flag.is_h:
        #     return

        for i in range(len(character_data.h_state.body_item)):
            if character_data.h_state.body_item[i][1]:
                # 事前避孕药的结算仅在每日问候的时候出现一起，其他时候不出现
                if i == 11 and character_data.second_behavior["day_hello"] != 0:
                    continue
                body_item_data = game_config.config_body_item[i]
                # 如果是猥亵型装备且当前不在H中，则判断该道具是否在开启中
                if body_item_data.type == 2 and not handle_premise.handle_self_is_h(character_id):
                    # 如果没有开启，则跳过
                    if handle_premise.handle_self_now_sex_toy_off(character_id):
                        continue
                    # 如果与玩家不在同一场景，则将该道具置为关闭状态然后跳过
                    if not handle_premise.handle_in_player_scene(character_id):
                        character_data.sp_flag.sex_toy_level = 0
                        continue
                second_behavior_id = body_item_data.behavior_id
                character_get_second_behavior(character_id, second_behavior_id)

        # 绳子捆绑
        if handle_premise.handle_self_now_bondage(character_id):
            character_get_second_behavior(character_id, "condage")
