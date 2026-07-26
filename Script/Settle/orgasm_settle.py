import random
from types import FunctionType
from Script.Core import cache_control, game_type, get_text
from Script.Design import attr_calculation, handle_premise, second_behavior
from Script.UI.Moudle import draw
from Script.Config import game_config, normal_config
from Script.UI.Panel import achievement_panel, ejaculation_panel

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
width = normal_config.config_normal.text_width
""" 屏幕宽度 """
_: FunctionType = get_text._
""" 翻译api """
orgasm_degree_order = {"small": 0, "normal": 1, "strong": 2, "super": 3}
""" 部位绝顶二段行为的程度排序，键为二段行为id中的程度后缀，值为程度序号，越大程度越高 """


def get_orgasm_part_and_degree(second_behavior_id: str) -> tuple:
    """
    从二段行为id中解析出部位绝顶行为所属的部位与绝顶程度
    Keyword arguments:
    second_behavior_id -- 二段行为id
    Return arguments:
    tuple -- (部位标识str, 程度序号int)，若不是部位绝顶行为则返回(None, -1)
    """
    # 部位绝顶行为的id格式为 {部位}_orgasm_{程度}，例如 v_orgasm_strong
    # 由此排除掉 extra_orgasm、plural_orgasm_2、x_orgasm_edge、b_orgasm_to_milk 等非部位程度绝顶行为
    id_split = second_behavior_id.split("_")
    if len(id_split) != 3 or id_split[1] != "orgasm":
        return None, -1
    if id_split[2] not in orgasm_degree_order:
        return None, -1
    return id_split[0], orgasm_degree_order[id_split[2]]


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
            # 无精液高潮：基础精液与临时精液合计不超过2ml时，作为高潮而非射精结算
            if handle_premise.handle_pl_semen_le_2(0):
                # 登记专用二段行为，不打开射精对象/部位选择面板，也不进行射精统计与目标效果
                second_behavior.character_get_second_behavior(0, "p_no_semen_climax")
                # 清空射精槽与忍住不射次数，避免同一次高潮被“停止忍耐”或普通H结束释放重复触发
                character_data.eja_point = 0
                character_data.h_state.endure_not_shot_count = 0
                return
            else:
                # 忍住射精
                if not skip_undure:
                    endure_flag = ejaculation_panel.show_endure_ejaculation_panel()
                    if endure_flag:
                        return
                # 普
                if character_data.h_state.endure_not_shot_count == 0:
                    second_behavior.character_get_second_behavior(0, "p_orgasm_small")
                # 超强
                elif character_data.h_state.endure_not_shot_count >= 4:
                    second_behavior.character_get_second_behavior(0, "p_orgasm_strong")
                # 强
                else:
                    second_behavior.character_get_second_behavior(0, "p_orgasm_normal")
            character_data.eja_point = 0
            now_draw = ejaculation_panel.Ejaculation_Panel(width)
            now_draw.draw()
            line = draw.LineDraw("-", width)
            line.draw()
    else:
        normal_orgasm_dict = {}  # 高潮结算字典
        extra_orgasm_dict = {}  # 额外高潮结算字典
        un_count_orgasm_dict = {}  # 不计数高潮结算字典
        for state_id in game_config.config_character_state:
            # 跳过非快感属性
            if game_config.config_character_state[state_id].type != 0:
                continue
            orgasm = state_id
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
        orgasm_settle_in_second_behavior(character_id, change_data, normal_orgasm_dict, extra_orgasm_dict, un_count_orgasm_dict)


def orgasm_settle_in_second_behavior(
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

    # 在修改任何部位状态前收集本次高潮计数；若处于寸止状态，则只做一次共同寸止判定
    supported_orgasm_list = [orgasm for orgasm in part_dict if orgasm != 3]
    orgasm_work_flag = any(
        normal_orgasm_dict.get(orgasm, 0) > 0
        or extra_orgasm_dict.get(orgasm, 0) > 0
        or un_count_orgasm_dict.get(orgasm, 0) > 0
        for orgasm in supported_orgasm_list
    )
    time_stop_flag = orgasm_work_flag and handle_premise.handle_unconscious_flag_3(character_id)
    orgasm_edge_flag = orgasm_work_flag and not time_stop_flag and handle_premise.handle_self_orgasm_edge(character_id)
    orgasm_edge_success_flag = False
    if orgasm_edge_flag:
        candidate_orgasm_edge_count = character_data.h_state.orgasm_edge_count.copy()
        crossed_part_count = 0
        for orgasm in supported_orgasm_list:
            normal_orgasm_data = normal_orgasm_dict.get(orgasm, 0)
            extra_orgasm_data = extra_orgasm_dict.get(orgasm, 0)
            un_count_orgasm_data = un_count_orgasm_dict.get(orgasm, 0)
            if normal_orgasm_data > 0 or extra_orgasm_data > 0 or un_count_orgasm_data > 0:
                candidate_orgasm_edge_count[orgasm] = candidate_orgasm_edge_count.get(orgasm, 0) + normal_orgasm_data + un_count_orgasm_data
                crossed_part_count += 1
        orgasm_edge_success_flag = judge_orgasm_edge_success(character_id, candidate_orgasm_edge_count, crossed_part_count)
        # 共同寸止失败时，将已累积的寸止计数并入本次不计数高潮一起解放，清空寸止计数并进入解放状态
        if not orgasm_edge_success_flag:
            release_orgasm_dict = un_count_orgasm_dict.copy()
            for orgasm in supported_orgasm_list:
                held_count = character_data.h_state.orgasm_edge_count.get(orgasm, 0)
                if held_count > 0:
                    release_orgasm_dict[orgasm] = release_orgasm_dict.get(orgasm, 0) + held_count
            character_data.h_state.orgasm_edge_count.clear()
            character_data.h_state.orgasm_edge = 2
            un_count_orgasm_dict = release_orgasm_dict

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
            if time_stop_flag:
                # 绝顶计入时停计数
                character_data.h_state.time_stop_orgasm_count.setdefault(orgasm, 0)
                character_data.h_state.time_stop_orgasm_count[orgasm] += climax_count
                continue
            # 如果本次共同寸止成功，则记录该部位并跳过普通结算
            if orgasm_edge_success_flag:
                # 绝顶计入寸止计数
                character_data.h_state.orgasm_edge_count.setdefault(orgasm, 0)
                character_data.h_state.orgasm_edge_count[orgasm] += climax_count
                # 赋予寸止行为
                second_behavior_id = f"{part_dict[orgasm]}_orgasm_edge"
                second_behavior.character_get_second_behavior(character_id, second_behavior_id)
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
            # 解放状态（含寸止解放与时停解放）下每部位只结算一次绝顶：累计≥3次由下方超强/强分支结算并跳过掷骰循环，1-2次掷骰一次；其余状态按累计次数逐次掷骰
            release_flag = handle_premise.handle_self_orgasm_edge_relase_or_time_stop_orgasm_relase(character_id)
            roll_count = (0 if climax_count >= 3 else 1) if release_flag else climax_count
            # 开始根据概率计算
            for i in range(roll_count):
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
                second_behavior.character_get_second_behavior(character_id, second_behavior_id)
            # 绝顶解放状态下（含寸止解放与时停解放），如果次数大于等于3，则触发超强绝顶
            if release_flag and climax_count >= 3:
                # 超强绝顶需要该部位敏感度至少为6级，否则变为强绝顶
                now_degree = 3
                if orgasm <= 7:
                    ability_id = orgasm
                else:
                    ability_id = orgasm + 79
                if character_data.ability[ability_id] < 6:
                    now_degree = 2
                second_behavior_id = f"{part_dict[orgasm]}_orgasm_{degree_dict[now_degree]}"
                second_behavior.character_get_second_behavior(character_id, second_behavior_id)
            # B绝顶喷乳，需要乳汁量到80%
            if orgasm == 1 and handle_premise.handle_milk_ge_80(character_id):
                # now_draw.text += _("\n触发B绝顶喷乳\n")
                second_behavior.character_get_second_behavior(character_id, "b_orgasm_to_milk")
            # U绝顶排尿，需要尿意条到80%
            if orgasm == 6 and handle_premise.handle_urinate_ge_80(character_id):
                # now_draw.text += _("\n触发U绝顶排尿\n")
                second_behavior.character_get_second_behavior(character_id, "u_orgasm_to_pee")
            # 如果发生了额外高潮，则进行额外高潮结算
            if extra_orgasm_data > 0:
                # now_draw.text += _("\n触发额外高潮\n")
                second_behavior.character_get_second_behavior(character_id, "extra_orgasm")
            # now_draw.draw()

    if part_count >= 1:
        # 饮精绝顶经验
        if character_data.h_state.shoot_position_body in [2, 15]:
            base_chara_experience_common_settle(character_id, 111, change_data=change_data)
    # 如果部位高潮计数大于等于2，则结算多重绝顶
    if part_count >= 2:
        second_behavior_id = f"plural_orgasm_{part_count}"
        second_behavior.character_get_second_behavior(character_id, second_behavior_id)
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


def release_orgasm_edge_now(character_id: int, change_data) -> None:
    """
    将该角色累计的寸止计数解放为绝顶，清零寸止计数后，在当前H阶段内立即结算本次新增绝顶的口上与数值
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象（自身结算传根对象，交互对象或群交成员传其TargetChange）
    """
    character_data: game_type.Character = cache.character_data[character_id]
    # 未处于寸止累计时无需解放
    if character_data.h_state.orgasm_edge == 0:
        return
    # 变为寸止解放状态
    character_data.h_state.orgasm_edge = 2
    # 将寸止计数转化为绝顶
    orgasm_settle_in_second_behavior(character_id, change_data, un_count_orgasm_dict=character_data.h_state.orgasm_edge_count)
    # 清零寸止计数
    for state_id in game_config.config_character_state:
        if game_config.config_character_state[state_id].type == 0:
            character_data.h_state.orgasm_edge_count[state_id] = 0
    # 立即结算刚解放绝顶的口上与数值，使其落在退出重置与退出奖励之前，同样按部位仅取最高绝顶程度触发口上
    second_behavior.second_behavior_effect(character_id, change_data, orgasm_settle_flag=True)


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


def judge_orgasm_edge_success(character_id: int, orgasm_edge_count: dict = dict(), crossed_part_count: int = 1) -> bool:
    """
    判断高潮寸止是否成功
    Keyword arguments:
    character_id -- 角色id
    orgasm_edge_count -- 用于本次判定的寸止计数字典，None时使用角色实时寸止计数
    crossed_part_count -- 本次同时跨过绝顶阈值的部位数，成功率按max(1, 该数/2)取幂，多部位同时寸止更难
    Return arguments:
    bool -- 是否成功
    """
    orgasm_edge_success_flag = False
    character_data: game_type.Character = cache.character_data[character_id]
    # 目前的高潮寸止数量，同一部位寸止次数越多，成功率越低
    all_orgasm_edge_count = 0
    if not orgasm_edge_count:
        orgasm_edge_count = character_data.h_state.orgasm_edge_count
    for key, value in orgasm_edge_count.items():
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
    # 否则，每超出一次，则有15%的概率失败
    else:
        fail_rate = 0.15 * over_count * -1
        # 多部位同时寸止时，单部位成功率按max(1, 跨阈部位数/2)取幂（p^max(1,k/2)），据此换算总失败率
        # 先把单部位成功率夹到[0,1]，避免fail_rate>1时负底数取偶次幂反而降低失败率
        success_rate = max(0.0, 1 - fail_rate) ** max(1, crossed_part_count / 2)
        fail_rate = 1 - success_rate
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
