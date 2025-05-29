from types import FunctionType
from Script.Design import (
    character_handle,
    map_handle,
    attr_calculation,
    handle_npc_ai,
    handle_premise,
)
from Script.Core import cache_control, game_type, get_text
from Script.Config import normal_config
from Script.UI.Moudle import draw
from Script.UI.Panel import ejaculation_panel, system_setting

import random, math

_: FunctionType = get_text._
""" 翻译api """
window_width: int = normal_config.config_normal.text_width
""" 窗体宽度 """
cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
width = normal_config.config_normal.text_width
""" 屏幕宽度 """

def base_chara_hp_mp_common_settle(
        character_id: int,
        add_time: int = 0,
        hp_value: int = 0,
        mp_value: int = 0,
        dregree: int = 0,
        target_flag: bool = False,
        change_data: game_type.CharacterStatusChange = None,
        change_data_to_target_change: game_type.CharacterStatusChange = None,
        ):
    """
    基础角色体力与气力通用结算函数\n
    Keyword arguments:\n
    character_id -- 角色id\n
    add_time -- 结算时间\n
    hp_value -- 体力值，-1为按程度减少，1为按程度增加，其他值则为具体值\n
    mp_value -- 气力值，-1为按程度减少，1为按程度增加，其他值则为具体值\n
    dregree -- 程度系数，0少，1中，2大\n
    target_flag -- 是否对交互对象也进行结算，默认为否，不可与change_data_to_target_change同时使用\n
    change_data -- 结算信息记录对象\n
    change_data_to_target_change -- 交互对象的结算信息记录对象\n
    """
    if add_time == 0 and hp_value == 0 and mp_value == 0:
        return
    # 时停下不结算
    if handle_premise.handle_time_stop_on(character_id):
        return
    character_data: game_type.Character = cache.character_data[character_id]
    target_character_id = character_data.target_character_id
    target_character_data: game_type.Character = cache.character_data[target_character_id]
    if character_data.dead:
        return
    # 程度定义
    dregree_dict = {
        0: [1, 3],
        1: [3, 6],
        2: [5, 10],
    }
    hp_adjust = dregree_dict[dregree][0]
    mp_adjust = dregree_dict[dregree][1]
    # 群交中消耗减少
    if handle_premise.handle_is_h(character_id) and handle_premise.handle_group_sex_mode_on(character_id):
        # 玩家减为三分之一
        if character_id == 0:
            hp_adjust /= 3
            mp_adjust /= 3
        # NPC减为二分之一
        else:
            hp_adjust /= 2
            mp_adjust /= 2
    # 气力结算
    if mp_value in [-1, 1]:
        mp_value *= add_time * mp_adjust
    if mp_value != 0:
        # 进行结算
        character_data.mana_point += mp_value
        # 结算信息记录
        if change_data != None:
            change_data.mana_point += mp_value
        if change_data_to_target_change != None:
            change_data_to_target_change.target_change.setdefault(character_id, game_type.TargetChange())
            target_change: game_type.TargetChange = change_data_to_target_change.target_change[character_id]
            target_change.mana_point += mp_value
        # 最小为0，最大为上限
        character_data.mana_point = max(0, character_data.mana_point)
        character_data.mana_point = min(character_data.mana_point_max, character_data.mana_point)
        # 如果气力为0则体力进行等值消耗
        if character_data.mana_point == 0 and mp_value < 0:
            character_data.hit_point += mp_value
            if change_data != None:
                change_data.hit_point += mp_value
            if change_data_to_target_change != None:
                change_data_to_target_change.target_change.setdefault(character_id, game_type.TargetChange())
                target_change: game_type.TargetChange = change_data_to_target_change.target_change[character_id]
                target_change.hit_point += mp_value
            character_data.hit_point = max(1, character_data.hit_point)
            handle_npc_ai.judge_character_tired_sleep(character_id)
        # 交互对象也同样
        if target_flag and target_character_id != character_id:
            # 结算信息记录
            change_data.target_change.setdefault(target_character_id, game_type.TargetChange())
            target_change: game_type.TargetChange = change_data.target_change[target_character_id]
            # 进行结算
            target_character_data.mana_point += mp_value
            target_change.mana_point += mp_value
            target_character_data.mana_point = max(0, target_character_data.mana_point)
            target_character_data.mana_point = min(target_character_data.mana_point_max, target_character_data.mana_point)
    # 体力结算
    if hp_value in [-1, 1]:
        hp_value *= add_time * hp_adjust
    if hp_value != 0:
        # 气力为0时体力消耗3倍
        if character_data.mana_point == 0 and hp_value < 0:
            hp_value_last = hp_value * 3
        else:
            hp_value_last = hp_value
        # 进行结算
        character_data.hit_point += hp_value_last
        # 结算信息记录
        if change_data != None:
            change_data.hit_point += hp_value_last
        if change_data_to_target_change != None:
            change_data_to_target_change.target_change.setdefault(character_id, game_type.TargetChange())
            target_change: game_type.TargetChange = change_data_to_target_change.target_change[character_id]
            target_change.hit_point += hp_value_last
        # 最小为1，最大为上限
        character_data.hit_point = max(1, character_data.hit_point)
        character_data.hit_point = min(character_data.hit_point_max, character_data.hit_point)
        # 检测hp1导致的疲劳
        handle_npc_ai.judge_character_tired_sleep(character_id)
        # 交互对象也同样
        if target_flag and target_character_id != character_id:
            if target_character_data.mana_point == 0 and hp_value < 0:
                hp_value_last = hp_value * 3
            else:
                hp_value_last = hp_value
            # 结算信息记录
            change_data.target_change.setdefault(target_character_id, game_type.TargetChange())
            target_change: game_type.TargetChange = change_data.target_change[target_character_id]
            # 进行结算
            target_character_data.hit_point += hp_value_last
            target_change.hit_point += hp_value_last
            target_character_data.hit_point = max(1, target_character_data.hit_point)
            target_character_data.hit_point = min(target_character_data.hit_point_max, target_character_data.hit_point)
            handle_npc_ai.judge_character_tired_sleep(target_character_id)


def base_chara_state_common_settle(
        character_id: int,
        add_time: int,
        state_id: int,
        base_value: int = 30,
        ability_level: int = -1,
        extra_adjust: float = 0,
        tenths_add: bool = True,
        change_data: game_type.CharacterStatusChange = None,
        change_data_to_target_change: game_type.CharacterStatusChange = None,
        ):
    """
    基础角色状态通用结算函数\n
    Keyword arguments:\n
    character_id -- 角色id\n
    add_time -- 结算时间\n
    state_id -- 状态id\n
    base_value -- 基础固定值\n
    ability_level -- 系数修正用能力等级\n
    extra_adjust -- 额外系数\n
    tenths_add -- 是否额外增加十分之一\n
    change_data -- 结算信息记录对象\n
    change_data_to_target_change -- 交互对象的结算信息记录对象
    """
    character_data: game_type.Character = cache.character_data[character_id]
    pl_character_data: game_type.Character = cache.character_data[0]
    if character_data.dead:
        return

    feel_state_set = {0, 1, 2, 3, 4, 5, 6, 7} # 快感状态，N~W快
    good_state_set = {8, 9, 10, 11, 12, 13, 14, 15, 16} # 正面状态
    bad_state_set = {18, 19, 20} # 负面状态，恐怖抑郁反感
    body_state_set = {8, 12, 17} # 身体状态，润滑欲情苦痛
    mentel_state_set = {9, 10, 11, 13, 14, 15, 16, 18, 19, 20} # 心智状态

    # 基础固定值
    time_base_value = add_time + base_value

    # 系数加成，区分快感状态和普通状态
    if state_id in feel_state_set:
        final_adjust = chara_feel_state_adjust(character_id, state_id, ability_level) + extra_adjust
    else:
        # 意识模糊下，不结算负面状态
        if state_id in bad_state_set and handle_premise.handle_unconscious_flag_ge_1(character_id):
           return
        # 深度无意识下，不结算身体物理外的一切状态
        elif state_id in mentel_state_set and not handle_premise.handle_normal_6(character_id):
            return
        final_adjust = chara_base_state_adjust(character_id, state_id, ability_level) + extra_adjust

    # 连续重复指令减值，非负面数值，仅玩家的交互对象
    if state_id not in bad_state_set and character_id == pl_character_data.target_character_id:
        # 判断是否为连续指令
        if len(cache.pl_pre_behavior_instruce) >= 2 and cache.pl_pre_behavior_instruce[-1] == cache.pl_pre_behavior_instruce[-2]:
            # 统计连续指令次数
            last_instr = cache.pl_pre_behavior_instruce[-1]
            # 如果last_instr属于基础指令则跳过连续相关处理
            if last_instr in [0, 1, 2]:
                pass
            else:
                instruct_count = 0
                # 从后往前遍历
                for instr in reversed(cache.pl_pre_behavior_instruce):
                    if instr == last_instr:
                        instruct_count += 1
                    else:
                        break
                # 连续指令次数大于2时减值，每次系数-0.15，最低为0.4
                if instruct_count > 2:
                    continuous_adjust = 1 - 0.15 * (instruct_count - 1)
                    continuous_adjust = max(0.4, continuous_adjust)
                    final_adjust *= continuous_adjust

    # 最终值
    final_value = time_base_value * final_adjust
    if tenths_add:
        # 最大不超过3倍最终值
        tenths_value = character_data.status_data[state_id] / 10
        tenths_value = min(3 * final_value, tenths_value)
        final_value += tenths_value

    # 心控-苦痛快感化，将苦痛状态转化为快感状态
    if state_id == 17 and handle_premise.handle_hypnosis_pain_as_pleasure(character_id):
        base_chara_state_common_settle(character_id, final_value, 0, 0, ability_level = character_data.ability[36], tenths_add = False, change_data = change_data, change_data_to_target_change = change_data_to_target_change)
        return

    # 结算最终值
    character_data.status_data[state_id] += final_value
    character_data.status_data[state_id] = min(99999, character_data.status_data[state_id])
    character_data.status_data[state_id] = max(0, character_data.status_data[state_id])

    # 露出对羞耻、施虐对先导、受虐对苦痛而产生的额外快感
    if state_id in [14, 16, 17]:
        extra_feel_settle(character_id, state_id, final_value, change_data, change_data_to_target_change)

    # 结算信息记录对象
    if change_data != None:
        change_data.status_data.setdefault(state_id, 0)
        change_data.status_data[state_id] += final_value
    if change_data_to_target_change != None:
        change_data_to_target_change.target_change.setdefault(character_id, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data_to_target_change.target_change[character_id]
        target_change.status_data.setdefault(state_id, 0)
        target_change.status_data[state_id] += final_value


def chara_feel_state_adjust(character_id: int, state_id: int, ability_level: int = -1):
    """
    角色快感系数获得的共用函数
    Keyword arguments:
    character_id -- 角色id
    state_id -- 状态id
    ability_level -- 系数修正用能力等级，此处为技巧能力等级
    """

    character_data: game_type.Character = cache.character_data[character_id]
    pl_character_data: game_type.Character = cache.character_data[0]

    # 系数加成
    final_adjust = 0
    # 部位感觉
    feel_adjust = attr_calculation.get_ability_adjust(character_data.ability[state_id])
    final_adjust += feel_adjust
    # 技巧
    if ability_level >= 0:
        tech_adjust = attr_calculation.get_ability_adjust(ability_level)
        final_adjust = math.sqrt(feel_adjust * tech_adjust)
    # 调香
    if character_data.sp_flag.aromatherapy == 4:
        final_adjust += 1
    # 催眠-敏感
    if character_data.hypnosis.increase_body_sensitivity:
        final_adjust += 2
    # 怀孕状态下加V和W快感
    if state_id in [4, 7] and handle_premise.handle_inflation_1(character_id):
        final_adjust += 1
    # 灌肠下会增加V和W快感
    if state_id in [4, 7] and handle_premise.handle_enema(character_id):
        final_adjust += character_data.dirty.enema_capacity * 0.2
    # 眼罩增加全部快感
    if handle_premise.handle_self_now_patch(character_id):
        final_adjust += 0.2
    # 无觉刻印会增加无意识状态下的部位快感系数
    if handle_premise.handle_unconscious_flag_ge_1(character_id):
        final_adjust += (attr_calculation.get_ability_adjust(character_data.ability[19]) - 1) * 2
    # 信物调整值
    now_token = pl_character_data.pl_collection.eqip_token[1]
    if len(now_token):
        # 信物干员的基础调整为0.5
        if character_id in now_token:
            final_adjust += 0.5
        # 全体干员+数量*0.01
        final_adjust += len(now_token) * 0.01
    # 群交中会因在场的其他干员人数进行调整
    if character_data.sp_flag.is_h and handle_premise.handle_group_sex_mode_on(character_id):
        scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
        scene_data: game_type.Scene = cache.scene_data[scene_path_str]
        other_npc_num = len(scene_data.character_list) - 2
        # 最大只能吃十个人的加成
        other_npc_num = min(10, other_npc_num)
        final_adjust += other_npc_num * 0.02
    # 系统难度修正
    now_difficulty = cache.all_system_setting.difficulty_setting[2]
    difficulty_adjust = system_setting.get_difficulty_coefficient(now_difficulty)
    final_adjust *= difficulty_adjust
    # 保证最终值不为负数
    final_adjust = max(0, final_adjust)

    return final_adjust


def chara_base_state_adjust(character_id: int, state_id: int, ability_level: int = -1):
    """
    角色状态系数获得的共用函数
    Keyword arguments:
    character_id -- 角色id
    state_id -- 状态id
    ability_level -- 系数修正用能力等级
    """

    character_data: game_type.Character = cache.character_data[character_id]
    pl_character_data: game_type.Character = cache.character_data[0]
    ability_level = max(0, ability_level)

    # 系数加成
    final_adjust = 0
    # 能力修正
    if state_id in [13, 15, 17, 18, 20]: # 与刻印相关的角色状态id
        feel_adjust = attr_calculation.get_mark_debuff_adjust(ability_level)
    else:
        feel_adjust = attr_calculation.get_ability_adjust(ability_level)
    final_adjust += feel_adjust
    # 素质修正
    if state_id in [9, 14]: # 习得、先导
        # 勤劳
        if character_data.talent[271] == 1:
            final_adjust += 0.3
        # 懒散
        elif character_data.talent[272] == 1:
            final_adjust -= 0.3
        # 教官
        if character_data.talent[358] == 1:
            final_adjust += 0.5
    if state_id in [10, 15]: # 恭顺、屈服
        # 脆弱
        if character_data.talent[273] == 1:
            final_adjust += 0.3
        # 坚强
        elif character_data.talent[274] == 1:
            final_adjust -= 0.3
        # 献身
        if character_data.talent[225] == 1:
            final_adjust += 0.4
    if state_id in [11, 13]: # 好意、快乐
        # 热情
        if character_data.talent[275] == 1:
            final_adjust += 0.3
        # 孤僻
        elif character_data.talent[276] == 1:
            final_adjust -= 0.3
    if state_id in [12, 16]: # 欲情、羞耻
        # 羞耻
        if character_data.talent[277] == 1:
            final_adjust += 0.3
        # 开放
        elif character_data.talent[278] == 1:
            final_adjust -= 0.3
    # 施虐狂
    if character_data.talent[229] == 1 and state_id == 14:
        final_adjust += 0.4
    # 受虐狂
    if character_data.talent[230] == 1 and state_id == 17:
        final_adjust += 0.4
    # 感情缺乏
    if character_data.talent[223] == 1:
        final_adjust -= 0.4
    # 信物修正
    now_token = pl_character_data.pl_collection.eqip_token[1]
    token_adjust = 0
    if len(now_token):
        # 信物干员的基础调整为0.5
        if character_id in now_token:
            token_adjust += 0.5
        # 全体干员+数量*0.01
        token_adjust += len(now_token) * 0.01
    # 调香
    if character_data.sp_flag.aromatherapy:
        if character_data.sp_flag.aromatherapy == 2 and state_id == 9:
            final_adjust += 1
        elif character_data.sp_flag.aromatherapy == 3 and state_id in [17, 18, 19, 20]:
            final_adjust -= 0.5
        elif character_data.sp_flag.aromatherapy == 4 and state_id == 12:
            final_adjust += 1
    # 催眠-敏感
    if character_data.hypnosis.increase_body_sensitivity and state_id == 12:
        final_adjust += 2
    # 群交中会因在场的其他干员人数进行调整
    if character_data.sp_flag.is_h and handle_premise.handle_group_sex_mode_on(character_id):
        scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
        scene_data: game_type.Scene = cache.scene_data[scene_path_str]
        other_npc_num = len(scene_data.character_list) - 2
        # 最大只能吃十个人的加成
        other_npc_num = min(10, other_npc_num)
        final_adjust += other_npc_num * 0.05
    # 系统难度修正
    now_difficulty = cache.all_system_setting.difficulty_setting[3]
    difficulty_adjust = system_setting.get_difficulty_coefficient(now_difficulty)
    # 对正面状态的加成
    if state_id in [8, 9, 10, 11, 12, 13, 14, 15, 16]:
        # 攻略进度素质
        character_fall_level = attr_calculation.get_character_fall_level(character_id)
        final_adjust += character_fall_level * 0.05
        # 信物
        final_adjust += token_adjust
        # 难度调整
        if difficulty_adjust > 1:
            final_adjust *= difficulty_adjust
        else:
            final_adjust /= difficulty_adjust
    # 对负面状态的
    elif state_id in [17, 18, 19, 20]:
        # 攻略进度素质
        character_fall_level = attr_calculation.get_character_fall_level(character_id)
        final_adjust -= character_fall_level * 0.2
        # 信物
        final_adjust -= token_adjust
        # 难度调整
        if difficulty_adjust > 1:
            final_adjust /= difficulty_adjust
        else:
            final_adjust *= difficulty_adjust
    # 保证最终值不为负数
    final_adjust = max(0, final_adjust)

    return final_adjust


def extra_feel_settle(character_id: int, state_id: int, final_value: float, change_data: game_type.CharacterStatusChange, change_data_to_target_change: game_type.CharacterStatusChange):
    """
    露出对羞耻、施虐对先导、受虐对苦痛而产生的额外快感
    Keyword arguments:
    character_id -- 角色id
    state_id -- 状态id
    final_value -- 最终值
    change_data -- 状态变更信息记录对象
    change_data_to_target_change -- 状态变更信息记录对象
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return
    final_value = max(10, final_value / 20)
    final_value = int(final_value)

    # 施虐对先导
    if state_id == 14 and character_data.ability[35] >= 5:
        base_chara_state_common_settle(character_id, final_value, 0, 0, ability_level = character_data.ability[35], tenths_add = False, change_data = change_data, change_data_to_target_change = change_data_to_target_change)
    # 露出对羞耻
    elif state_id == 16 and character_data.ability[34] >= 5:
        base_chara_state_common_settle(character_id, final_value, 0, 0, ability_level = character_data.ability[34], tenths_add = False, change_data = change_data, change_data_to_target_change = change_data_to_target_change)
    # 受虐对苦痛
    elif state_id == 17 and character_data.ability[36] >= 5:
        base_chara_state_common_settle(character_id, final_value, 0, 0, ability_level = character_data.ability[36], tenths_add = False, change_data = change_data, change_data_to_target_change = change_data_to_target_change)


def base_chara_favorability_and_trust_common_settle(
        character_id: int,
        add_time: int,
        favorability_flag: bool,
        base_value: int = 0,
        extra_adjust: float = 0,
        change_data: game_type.CharacterStatusChange = None,
        target_character_id: int = 0,
        ):
    """
    基础角色好感与信赖通用结算函数\n
    Keyword arguments:\n
    character_id -- 角色id\n
    add_time -- 结算时间\n
    favorability_flag -- true为好感,false为信赖\n
    base_value -- 基础固定值\n
    extra_adjust -- 额外系数\n
    """
    character_data: game_type.Character = cache.character_data[character_id]
    pl_character_data: game_type.Character = cache.character_data[0]

    # 判断交互对象
    if target_character_id == 0:
        target_character_id = character_data.target_character_id
    target_data: game_type.Character = cache.character_data[target_character_id]

    # 防止重复结算
    if character_id != target_character_id and (character_id != 0 or target_character_id != 0):
        if character_data.dead:
            return
        # 无意识状态下不结算
        if handle_premise.handle_unconscious_flag_ge_1(character_id):
            return
        if handle_premise.handle_unconscious_flag_ge_1(target_character_id):
            return
        # 时停状态下不结算
        if handle_premise.handle_time_stop_on(character_id):
            return

        # 信物调整值
        now_token = pl_character_data.pl_collection.eqip_token[1]
        token_adjust = 0
        if len(now_token):
            # 信物干员的基础调整为0.1
            if character_id in now_token or target_character_id in now_token:
                token_adjust += 0.1
            # 全体干员+数量*0.01
            token_adjust += len(now_token) * 0.01

        # 连续重复指令减值
        continuous_adjust = 1
        # 判断是否为连续指令
        if len(cache.pl_pre_behavior_instruce) >= 2 and cache.pl_pre_behavior_instruce[-1] == cache.pl_pre_behavior_instruce[-2]:
            # 统计连续指令次数
            last_instr = cache.pl_pre_behavior_instruce[-1]
            # 如果last_instr属于基础指令则跳过连续相关处理
            if last_instr in [0, 1, 2]:
                pass
            else:
                instruct_count = 0
                # 从后往前遍历
                for instr in reversed(cache.pl_pre_behavior_instruce):
                    if instr == last_instr:
                        instruct_count += 1
                    else:
                        break
                # 连续指令次数大于2时减值，每次系数-0.15，最低为0.4
                if instruct_count > 2:
                    continuous_adjust = 1 - 0.15 * (instruct_count - 1)
                    continuous_adjust = max(0.4, continuous_adjust)

        # 结算信息记录对象
        change_data.target_change.setdefault(target_character_id, game_type.TargetChange())
        target_change = change_data.target_change[target_character_id]

        # 好感
        if favorability_flag:
            # 基础固定值
            add_favorability = base_value + calculation_favorability(character_id, target_character_id, add_time)
            final_adjust = 1

            # 额外调整
            if extra_adjust != 0:
                final_adjust *= extra_adjust
                # 如果额外调整为负，则最终值也必须为负
                if extra_adjust < 0 and  final_adjust * add_favorability > 0:
                    final_adjust *= -1

            # 信物调整
            if token_adjust != 0:
                # 负数则减少，正数则增加
                if final_adjust > 0:
                    final_adjust *= (1 + token_adjust)
                else:
                    final_adjust *= (1 - token_adjust)

            if add_favorability > 0:
                # 连续重复减值
                final_adjust *= continuous_adjust
                # 系统难度修正
                now_difficulty = cache.all_system_setting.difficulty_setting[1]
                difficulty_adjust = system_setting.get_difficulty_coefficient(now_difficulty)
                final_adjust *= difficulty_adjust

            # 结算最终值
            add_favorability *= final_adjust
            character_handle.add_favorability(character_id, target_character_id, add_favorability, change_data, target_change)

        # 信赖
        else:
            if character_id == 0 and character_data.target_character_id != 0:
                add_trust = base_value + calculation_trust(character_id, target_character_id, add_time)
            else:
                add_trust = base_value + calculation_trust(target_character_id, character_id, add_time)
            final_adjust = 1

            # 额外调整
            if extra_adjust != 0:
                final_adjust *= extra_adjust
                # 如果额外调整为负，则最终值也必须为负
                if extra_adjust < 0 and  final_adjust * add_trust > 0:
                    final_adjust *= -1

            # 信物调整
            if token_adjust != 0:
                # 负数则减少，正数则增加
                if final_adjust > 0:
                    final_adjust *= (1 + token_adjust)
                else:
                    final_adjust *= (1 - token_adjust)

            if add_trust > 0:
                # 连续重复减值
                final_adjust *= continuous_adjust
                # 系统难度修正
                now_difficulty = cache.all_system_setting.difficulty_setting[1]
                difficulty_adjust = system_setting.get_difficulty_coefficient(now_difficulty)
                final_adjust *= difficulty_adjust

            # 结算最终值
            add_trust *= final_adjust
            if character_id == 0 and character_data.target_character_id != 0:
                target_data.trust += add_trust
                target_data.trust = min(300, target_data.trust)
                target_change.trust += add_trust
            else:
                character_data.trust += add_trust
                character_data.trust = min(300, character_data.trust)
                change_data.trust += add_trust

    else:
        return


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


def base_chara_climix_common_settle(
        character_id: int,
        part_id: int = 0,
        base_value: int = 500,
        adjust: int = -1,
        degree: int = -1,
        change_data: game_type.CharacterStatusChange = None,
        change_data_to_target_change: game_type.CharacterStatusChange = None,
        ):
    """
    基础角色绝顶通用结算函数\n
    Keyword arguments:\n
    character_id -- 角色id\n
    part_id -- 部位id，即性器官id\n
    base_value -- 基础固定值\n
    adjust -- 系数\n
    degree -- 绝顶程度，默认-1，0小1普2强3超\n
    change_data -- 结算信息记录对象
    change_data_to_target_change -- 结算信息记录对象
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return
    # 只能选择正确部位
    if part_id < 0 or part_id > 7:
        return
    # 只有玩家有P部位
    if character_id != 0 and part_id == 3:
        return

    # 部位快感
    if part_id != 3:
        random_adjust = random.uniform(0.8, 1.2)
        if adjust >= 0:
            adjust *= random_adjust
        else:
            adjust = random_adjust
        base_chara_state_common_settle(character_data.target_character_id, base_value, part_id, extra_adjust = adjust, change_data = change_data, change_data_to_target_change = change_data_to_target_change)

        # 触发绝顶
        part_dict = {0 : "n", 1 : "b", 2 : "c", 3 : "p", 4 : "v", 5 : "a", 6 : "u", 7 : "w"}
        degree_dict = {0 : "small", 1 : "normal", 2 : "strong", 3 : "super"}
        # 如果指定了程度，则直接使用指定的程度
        if degree >= 0:
            second_behavior_id = f"{part_dict[part_id]}_orgasm_{degree_dict[degree]}"
        # 否则根据之前的高潮程度来判断
        else:
            pre_data = character_data.h_state.orgasm_level[part_id] # 记录里的前高潮程度
            if pre_data % 3 == 0:
                degree = 0
            elif pre_data % 3 == 1:
                degree = 1
            elif pre_data % 3 == 2:
                degree = 2
            second_behavior_id = f"{part_dict[part_id]}_orgasm_{degree_dict[degree]}"
        character_data.second_behavior[second_behavior_id] = 1
        character_data.h_state.orgasm_level[part_id] += 1

    # 触发射精面板
    if part_id == 3:
        character_data.eja_point = 0
        now_draw = ejaculation_panel.Ejaculation_Panel(width)
        now_draw.draw()
        line = draw.LineDraw("-", width)
        line.draw()


def base_chara_experience_common_settle(
        character_id: int,
        experience_id: int,
        base_value: int = 1,
        target_flag: bool = False,
        change_data: game_type.CharacterStatusChange = None,
        change_data_to_target_change: game_type.CharacterStatusChange = None,
        ):
    """
    基础角色经验通用结算函数\n
    Keyword arguments:\n
    character_id -- 角色id\n
    experience_id -- 经验id\n
    base_value -- 基础固定值\n
    target_flag -- 是否加到交互对象身上\n
    change_data -- 状态变更信息记录对象\n
    change_data_to_target_change -- 交互对象结算信息记录对象
    """
    character_data: game_type.Character = cache.character_data[character_id]
    final_character_id = character_id
    if character_data.dead:
        return
    # 改为加到交互对象身上
    if target_flag:
        final_character_id = character_data.target_character_id
        character_data = cache.character_data[final_character_id]

    # 深度无意识下部分经验不结算
    conscious_experience_set = {30, 31, 32, 33, 34}
    if experience_id in conscious_experience_set and not handle_premise.handle_normal_6(final_character_id):
        return

    # 结算最终值
    character_data.experience.setdefault(experience_id, 0)
    character_data.experience[experience_id] += base_value
    character_data.experience[experience_id] = max(0, character_data.experience[experience_id])

    # 确认结算信息记录对象
    final_change_data = change_data
    if change_data != None and target_flag:
        change_data.target_change.setdefault(final_character_id, game_type.TargetChange())
        final_change_data: game_type.TargetChange = change_data.target_change[final_character_id]
    elif change_data_to_target_change != None:
        change_data_to_target_change.target_change.setdefault(character_id, game_type.TargetChange())
        final_change_data: game_type.TargetChange = change_data_to_target_change.target_change[character_id]

    # 结算信息记录对象增加经验
    if final_change_data != None:
        final_change_data.experience.setdefault(experience_id, 0)
        final_change_data.experience[experience_id] += base_value
