import random
import datetime
from types import FunctionType
from typing import Dict
from Script.Core import (
    cache_control,
    game_path_config,
    game_type,
    constant,
    get_text,
)
from Script.Design import (
    character,
    handle_premise,
    handle_premise_place,
    update,
    character_behavior,
    attr_calculation,
    map_handle,
)
from Script.UI.Moudle import draw
from Script.Config import game_config, normal_config

game_path = game_path_config.game_path
cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """
window_width: int = normal_config.config_normal.text_width
""" 窗体宽度 """
line_feed = draw.NormalDraw()
""" 换行绘制对象 """
line_feed.text = "\n"
line_feed.width = 1

def judge_character_h_obscenity_unconscious(character_id: int, pl_start_time: datetime.datetime) -> int:
    """
    判断H状态、猥亵与无意识\n
    Keyword arguments:
    character_id -- 角色id\n
    pl_start_time -- 玩家行动开始时间\n
    Return arguments:
    bool -- 本次update时间切片内活动是否已完成
    """
    from Script.Settle import default
    character_data: game_type.Character = cache.character_data[character_id]
    pl_character_data: game_type.Character = cache.character_data[0]

    # 玩家部分
    if character_id == 0:
        # 清空空气催眠位置
        if character_data.position != character_data.pl_ability.air_hypnosis_position:
            character_data.pl_ability.air_hypnosis_position = ""
        # 如果前指令是口交类型则重置所有阴茎污浊状态
        if handle_premise.handle_last_cmd_blowjob_type(0):
            for dirty_key in character_data.dirty.penis_dirty_dict:
                character_data.dirty.penis_dirty_dict[dirty_key] = False
        # 当前有H体位下，如果进行手、口、胸类则清零H体位数据
        if character_data.h_state.current_sex_position != -1:
            if handle_premise.handle_last_cmd_handjob_type(0) or handle_premise.handle_last_cmd_blowjob_type(0) or handle_premise.handle_last_cmd_paizuri_type(0):
                character_data.h_state.current_sex_position = -1
        # 刚刚射精状态下，用计数的方式来判断是否重置
        if character_data.h_state.just_shoot == 1:
            character_data.h_state.just_shoot = 2
        else:
            character_data.h_state.just_shoot = 0
        # 二次确认H意外结束的归零结算
        special_end_list = constant.special_end_H_list
        if len(cache.pl_pre_status_instruce) and cache.pl_pre_status_instruce[-1] in special_end_list and character_data.behavior.behavior_id not in special_end_list:
            default.handle_both_h_state_reset(0, 1, change_data=game_type.CharacterStatusChange(), now_time=datetime.datetime)
        # 如果在时停中搬运角色，则直接移动到玩家同一地点
        if (
            handle_premise.handle_time_stop_on(character_id) and 
            handle_premise.handle_carry_somebody_in_time_stop(character_id)
            ):
            now_carry_chara_id = pl_character_data.pl_ability.carry_chara_id_in_time_stop
            now_carry_character_data = cache.character_data[now_carry_chara_id]
            map_handle.character_move_scene(now_carry_character_data.position, pl_character_data.position, now_carry_chara_id)


    # 玩家部分终止，以下为NPC部分
    if character_id == 0:
        return 1

    # 将绝顶解放状态改为关闭绝顶寸止
    if handle_premise.handle_self_orgasm_edge_relase(character_id):
        default.handle_self_orgasm_edge_off(character_id, 1, change_data=game_type.CharacterStatusChange(), now_time=datetime.datetime)
    # 将时停解放状态改为False
    if handle_premise.handle_self_time_stop_orgasm_relase(character_id):
        character_data.h_state.time_stop_release = False

    # H状态或木头人时，行动锁死为等待不动
    if character_data.sp_flag.is_h or character_data.hypnosis.blockhead:
        # 睡奸时例外
        if character_data.state == constant.CharacterStatus.STATUS_SLEEP:
            return 1
        # 6异常时例外
        if not handle_premise.handle_normal_6(character_id):
            return 1
        # 群交时
        if handle_premise.handle_group_sex_mode_on(character_id):
            # 仅自慰类型和部位类型由群交AI判断处理
            if(
                handle_premise.handle_npc_ai_type_1_in_group_sex(character_id) or handle_premise.handle_npc_ai_type_2_in_group_sex(character_id)
            ):
                npc_ai_in_group_sex(character_id)
                return 1
            # 如果已经获得性爱助手行为，则结算助手行动
            elif character_data.h_state.sex_assist:
                # 手动结算性爱助手行动
                character_behavior.judge_character_status(character_id)
                character_data.h_state.sex_assist = False
        character_data.behavior.behavior_id = constant.Behavior.WAIT
        character_data.state = constant.CharacterStatus.STATUS_WAIT
        character_data.behavior.start_time = pl_start_time
        character_data.behavior.duration = pl_character_data.behavior.duration
        character_data.target_character_id = character_id
        # 防止行为的时间为0
        if character_data.behavior.duration == 0:
            past_time = int((cache.game_time.timestamp() - pl_start_time.timestamp()) / 60)
            character_data.behavior.duration = past_time

    # 如果不在同一位置
    if handle_premise_place.handle_not_in_player_scene(character_id):

        # 如果不在同一位置，则结束H状态和无意识状态
        if character_data.sp_flag.is_h:
            character_data.sp_flag.is_h = False
            character_data.sp_flag.unconscious_h = 0
            character_data.behavior.behavior_id = constant.Behavior.END_H
            character_data.state = constant.CharacterStatus.STATUS_END_H
            character_data.behavior.start_time = pl_start_time
            character_data.behavior.duration = 1
            character_data.target_character_id = character_id

        # 如果不在同一位置，则结束睡眠猥亵状态
        elif character_data.sp_flag.unconscious_h == 1:
            character_data.sp_flag.unconscious_h = 0

        # 如果不在同一位置，则结束空气催眠
        elif character_data.sp_flag.unconscious_h == 5 and character_data.position != pl_character_data.pl_ability.air_hypnosis_position:
            character_data.sp_flag.unconscious_h = 0

    return 1


def recover_from_unconscious_h(character_id: int, info_text: str = ""):
    """
    从无意识H中恢复意识的结算\n
    Keyword arguments:\n
    character_id -- 角色id\n
    """
    from Script.Settle import default
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]

    # 如果角色不在无意识H状态，则直接返回
    if character_data.sp_flag.unconscious_h == 0:
        return

    # 停止对方的无意识状态与H状态
    target_data.sp_flag.unconscious_h = 0
    target_data.sp_flag.is_h = False

    # 是否继续H
    continue_h = False

    # 输出提示信息
    now_draw = draw.WaitDraw()
    now_draw.width = window_width
    if info_text == "":
        now_draw.text = _("\n{0}从无意识状态中恢复过来\n").format(target_data.name)
    else:
        now_draw.text = info_text
    now_draw.draw()

    # 终止对方的行动
    character_behavior.judge_character_status_time_over(character_data.target_character_id, cache.game_time, end_now = 2)
    # 睡眠中，则对方获得睡奸醒来状态
    if handle_premise.handle_action_sleep(character_data.target_character_id):
        target_data.sp_flag.sleep_h_awake = True
    # 同步玩家的行动开始时间
    character.init_character_behavior_start_time(character_id, cache.game_time)
    # 玩家的行动时间设为10分钟，对方的行动时间设为15分钟
    character_data.behavior.duration = 10
    target_data.behavior.duration = 15

    # 如果交互对象是监禁状态，则直接通过
    if handle_premise.handle_t_imprisonment_1(character_id):
        continue_h = True
    # 检测是否满足高级性骚扰的实行值需求
    elif handle_premise.handle_instruct_judge_high_obscenity(character_data.target_character_id):
        # 获取陷落状态
        character_fall_level = attr_calculation.get_character_fall_level(character_data.target_character_id, minus_flag=True)
        # 3级及以上的陷落时会通过
        if character_fall_level >= 3:
            continue_h = True
        # 爱情线会变成轻度性骚扰
        elif character_fall_level > 0:
            character_data.behavior.behavior_id = constant.Behavior.LOW_OBSCENITY_ANUS
            character_data.state = constant.CharacterStatus.STATUS_LOW_OBSCENITY_ANUS
        # 隶属线会愤怒生气
        elif character_fall_level < 0:
            target_data.angry_point += 100
            target_data.sp_flag.angry_with_player = True
        # 如果没有陷落的话，会变成高级性骚扰
        else:
            character_data.behavior.behavior_id = constant.Behavior.HIGH_OBSCENITY_ANUS
            character_data.state = constant.CharacterStatus.STATUS_HIGH_OBSCENITY_ANUS
    # 不满足的话，设为H失败
    else:
        character_data.behavior.behavior_id = constant.Behavior.DO_H_FAIL
        character_data.state = constant.CharacterStatus.STATUS_DO_H_FAIL

    # 如果继续H
    if continue_h:
        character_data.behavior.behavior_id = constant.Behavior.H
        character_data.state = constant.CharacterStatus.STATUS_H
        target_data.behavior.behavior_id = constant.Behavior.WAIT
        target_data.state = constant.CharacterStatus.STATUS_WAIT
       # 睡眠中，则对方获得装睡状态
        if handle_premise.handle_action_sleep(character_data.target_character_id):
            target_data.h_state.pretend_sleep = True
    # 否则
    else:
        # 重置双方H结构体和相关数据
        default.handle_both_h_state_reset(0, 1, game_type.CharacterStatusChange, datetime.datetime)

    # 时间推进十分钟
    update.game_update_flow(10)


def judge_weak_up_in_sleep_h(character_id: int):
    """
    判断睡奸中是否醒来\n
    Keyword arguments:\n
    character_id -- 角色id\n
    """
    now_character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[now_character_data.target_character_id]

    # 浅睡和半梦半醒时递增苏醒概率
    weak_rate = game_config.config_sleep_level[1].sleep_point - target_data.sleep_point
    if target_data.sleep_point <= game_config.config_sleep_level[0].sleep_point:
        weak_rate += game_config.config_sleep_level[0].sleep_point - target_data.sleep_point
    # 判定是否吵醒
    if weak_rate >= random.randint(1,100):
        # 清空疲劳和睡眠程度
        target_data.tired_point = 0
        target_data.sleep_point = 0
        # 提示信息
        info_text = _("\n因为{0}的动作，{1}从梦中惊醒过来\n").format(now_character_data.name, target_data.name)
        # 结算醒来
        recover_from_unconscious_h(character_id, info_text)


def evaluate_npc_body_part_prefs(character_id: int) -> int:
    """
    判断NPC的部位喜好\n
    Return arguments:
    int -- 选择的部位
    """

    character_data = cache.character_data[character_id]

    # 如果自己不是NPC，则返回
    if character_id == 0:
        return 0

    # 按照部位统计权重，初始权重为1
    part_weight = {}
    for i in range(8):
        part_weight[i] = 1

    # 部位经验权重为1
    for experience_id in game_config.config_experience:
        # 去掉非部位的经验
        if (
            20 <= experience_id <= 60 or
            experience_id >= 78
        ):
            continue

        # 取除以10的余数
        part_id = experience_id % 10
        if experience_id in {61,65}:
            part_id = 4
        elif experience_id in {62,66}:
            part_id = 5
        elif experience_id in {63,67}:
            part_id = 6
        elif experience_id in {64,68}:
            part_id = 7
        now_exp = character_data.experience[experience_id]
        part_weight[part_id] += now_exp

    # 能力等级权重为10
    for ability_id in game_config.config_ability:
        # 去掉非部位的能力
        if ability_id >= 13:
            continue
        if ability_id <= 8:
            part_id = ability_id
        # 将扩张的序号转换为部位序号
        else:
            part_id = ability_id - 5
        now_ability = character_data.ability[ability_id]
        part_weight[part_id] += now_ability * 10

    # 在最后将阴茎的权重置为0
    part_weight[3] = 0

    # 根据权重，随机选择一个部位
    part_id = random.choices(list(part_weight.keys()), weights=list(part_weight.values()), k=1)[0]
    # print(f"debug {character_data.name}的逆推ai选择了{game_config.config_organ[part_id].name}部位，总权重为{part_weight}")

    # 以防万一，如果因为BUG选中了阴茎，则返回
    if part_id == 3:
        return 0

    # 返回选择的部位
    return part_id

def npc_active_h():
    """
    判断NPC的逆推ai\n
    Return arguments:
    bool -- 0为失败，1为正常逆推
    """
    from Script.UI.Panel import in_scene_panel

    pl_character_data: game_type.Character = cache.character_data[0]
    target_character_id = pl_character_data.target_character_id
    target_character_data = cache.character_data[target_character_id]

    # 如果对方不是主动H状态，则返回
    if target_character_data.hypnosis.active_h == False and target_character_data.h_state.npc_active_h == False:
        return 0

    # 根据NPC的部位喜好，选择一个部位
    part_id = evaluate_npc_body_part_prefs(target_character_id)

    # 遍历全状态
    all_stastus_list = []
    now_premise_data = {}
    for status_id in game_config.config_status:
        # 获得各状态的tag
        status_data = game_config.config_status[status_id]
        status_tag_list = status_data.tag.split("|")
        # 跳过其中非性爱类，道具类、药物类、SM类、非逆推类
        if(
            _("性爱") not in status_tag_list or
            _("道具") in status_tag_list or
            _("药物") in status_tag_list or
            _("SM") in status_tag_list or
            _("非逆推") in status_tag_list
        ):
            continue
        # 如果NPC为处，则跳过破处类
        if part_id == 0 and target_character_data.talent[4] and _("破处") in status_tag_list:
            continue
        if part_id == 4 and target_character_data.talent[0] and _("破处") in status_tag_list:
            continue
        if part_id == 5 and target_character_data.talent[1] and _("破处") in status_tag_list:
            continue
        if part_id == 6 and target_character_data.talent[2] and _("破处") in status_tag_list:
            continue
        if part_id == 7 and target_character_data.talent[3] and _("破处") in status_tag_list:
            continue

        # 跳过非当前部位
        if part_id == 0 and "N" not in status_tag_list:
            continue
        elif part_id == 1 and "B" not in status_tag_list:
            continue
        elif part_id == 2 and "C" not in status_tag_list:
            continue
        elif part_id == 4 and "V" not in status_tag_list:
            continue
        elif part_id == 5 and "A" not in status_tag_list:
            continue
        elif part_id == 6 and "U" not in status_tag_list:
            continue
        elif part_id == 7 and "W" not in status_tag_list:
            continue

        # 跳过不满足前提的
        if status_id in constant.state_id_to_instruct_id:
            # 获取指令id
            instruct_id = constant.state_id_to_instruct_id[status_id]
            # 检查指令是否可用
            filter_judge, now_premise_data = in_scene_panel.judge_single_instruct_filter(instruct_id, now_premise_data, constant.InstructType.SEX, use_type_filter_flag=False)
            # 跳过
            if not filter_judge:
                continue

        # 开始加入列表中
        all_stastus_list.append(status_id)

    # 如果没有符合条件的状态，则返回
    if len(all_stastus_list) == 0:
        return 0

    # print(f"debug 全列表为{all_stastus_list}")

    # 随机选择一个状态
    status_id = random.choice(all_stastus_list)

    # 赋予给玩家
    character.init_character_behavior_start_time(0, cache.game_time)
    pl_character_data.behavior.behavior_id = status_id
    pl_character_data.state = status_id
    pl_character_data.behavior.duration = 10
    update.game_update_flow(10)


def npc_ai_in_group_sex(character_id: int):
    """
    NPC在群交中的AI，不含抢占\n
    Keyword arguments:\n
    character_id -- 角色id\n
    """
    from Script.UI.Panel import group_sex_panel

    # 玩家则返回
    if character_id == 0:
        return
    # 如果自己已在群交模板中，则返回
    group_sex_chara_id_list = group_sex_panel.count_group_sex_character_list()
    if character_id in group_sex_chara_id_list:
        return

    character_data: game_type.Character = cache.character_data[character_id]
    pl_character_data: game_type.Character = cache.character_data[0]
    A_template_data = pl_character_data.h_state.group_sex_body_template_dict["A"]

    # 如果不是H状态+群交，则返回
    if character_data.sp_flag.is_h == False or handle_premise.handle_group_sex_mode_off(character_id):
        return

    # 被绳子捆绑则返回
    if handle_premise.handle_self_now_bondage(character_id):
        return

    # 如果设定NPC为仅自慰，则进入要自慰后返回
    if handle_premise.handle_npc_ai_type_1_in_group_sex(character_id):
        character_data.sp_flag.masturebate = 3
        character_data.state = constant.CharacterStatus.STATUS_ARDER
        # print(f"debug {character_data.name}进入了要自慰状态")
        return

    # 获取当前模板的空缺部位和非空缺部位
    now_template_empty_part_list, now_template_not_empty_part_list = group_sex_panel.get_now_template_part_list()

    # 如果有空缺，则随机选择一个部位
    if len(now_template_empty_part_list):
        body_part = random.choice(now_template_empty_part_list)
        # 如果是加入侍奉，则直接加入
        if body_part == _("加入侍奉"):
            A_template_data[1][0].append(character_id)
            # print(f"debug {character_data.name}加入侍奉{game_config.config_status[ A_template_data[1][1]].name}")
        else:
            # 获取该部位的状态id列表
            pl_character_data.target_character_id = character_id
            new_status_id_list = group_sex_panel.get_status_id_list_from_group_sex_body_part(body_part)
            # 如果没有可用的状态，则返回
            if len(new_status_id_list) == 0:
                return
            # 随机选择一个状态
            status_id = random.choice(new_status_id_list)
            # 如果是侍奉
            if body_part == _("侍奉"):
                A_template_data[1] = [[character_id], status_id]
            # 如果是对单
            else:
                A_template_data[0][body_part] = [character_id, status_id]
            # print(f"debug {character_data.name}对{body_part}选择了{game_config.config_status[status_id].name}")
    # 否则，自己进入要自慰状态
    else:
        character_data.sp_flag.masturebate = 3
        character_data.state == constant.CharacterStatus.STATUS_ARDER
        # print(f"debug {character_data.name}进入了要自慰状态")

def npc_ai_in_group_sex_type_3():
    """
    NPC在群交中的抢占AI\n
    Keyword arguments:\n
    character_id -- 角色id\n
    """
    from Script.UI.Panel import group_sex_panel

    pl_character_data: game_type.Character = cache.character_data[0]
    A_template_data = pl_character_data.h_state.group_sex_body_template_dict["A"]
    group_sex_chara_id_list = group_sex_panel.count_group_sex_character_list()
    scene_path_str = map_handle.get_map_system_path_str_for_list(pl_character_data.position)
    scene_data = cache.scene_data[scene_path_str]
    now_scene_chara_id_list = scene_data.character_list

    # 筛选角色列表
    new_chara_id_list = []
    for character_id in now_scene_chara_id_list:
        character_data: game_type.Character = cache.character_data[character_id]
        # 如果自己已在群交模板中，则跳过
        if character_id in group_sex_chara_id_list:
            continue
        # 如果不是H状态+群交，则跳过
        if character_data.sp_flag.is_h == False or handle_premise.handle_group_sex_mode_off(character_id):
            continue
        new_chara_id_list.append(character_id)

    # 获取当前模板的空缺部位和非空缺部位
    now_template_empty_part_list, now_template_not_empty_part_list = group_sex_panel.get_now_template_part_list()

    # 遍历空缺部位
    for body_part in now_template_empty_part_list:
        # 如果新角色列表空了，则退出循环
        if len(new_chara_id_list) <= 0:
            break
        # 从新角色列表中选择一个随机角色
        character_id = random.choice(new_chara_id_list)
        # 从列表中去掉该角色
        new_chara_id_list.remove(character_id)
        # 如果是加入侍奉，则直接加入
        if body_part == _("加入侍奉"):
            A_template_data[1][0].append(character_id)
            # print(f"debug {character_data.name}加入侍奉{game_config.config_status[ A_template_data[1][1]].name}")
        else:
            # 获取该部位的状态id列表
            pl_character_data.target_character_id = character_id
            new_status_id_list = group_sex_panel.get_status_id_list_from_group_sex_body_part(body_part)
            # 随机选择一个状态
            status_id = random.choice(new_status_id_list)
            # 如果是侍奉
            if body_part == _("侍奉"):
                A_template_data[1] = [[character_id], status_id]
            # 如果是对单
            else:
                A_template_data[0][body_part] = [character_id, status_id]
            # print(f"debug {character_data.name}对{body_part}选择了{game_config.config_status[status_id].name}")

    # 遍历非空缺部位
    for body_part in now_template_not_empty_part_list:
        # 如果新角色列表空了，则退出循环
        if len(new_chara_id_list) <= 0:
            break
        # 二分之一的几率不结算该部位
        if random.randint(0,1):
            continue
        # 从新角色列表中选择一个随机角色
        character_id = random.choice(new_chara_id_list)
        # 从列表中去掉该角色
        new_chara_id_list.remove(character_id)
        # 如果是侍奉，则加入角色列表，并踢出列表中的第0个角色
        if body_part == _("侍奉"):
            A_template_data[1][0].append(character_id)
            A_template_data[1][0].pop(0)
        # 否则代替原角色
        else:
            A_template_data[0][body_part][0] = character_id

    # 剩下的角色进入要自慰状态
    for character_id in new_chara_id_list:
        character_data = cache.character_data[character_id]
        character_data.sp_flag.masturebate = 3
        character_data.state == constant.CharacterStatus.STATUS_ARDER
        # print(f"debug {character_data.name}进入了要自慰状态")

