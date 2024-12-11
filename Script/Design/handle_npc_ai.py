import random
import datetime
from types import FunctionType
from typing import Dict
from Script.Core import (
    cache_control,
    game_path_config,
    game_type,
    constant,
    value_handle,
    get_text,
)
from Script.Design import (
    game_time,
    character,
    handle_premise,
    handle_premise_place,
    update,
    character_behavior,
    character_move,
    attr_calculation,
    map_handle,
)
from Script.UI.Moudle import draw
from Script.Config import game_config, normal_config
from Script.Settle import default

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


def judge_character_tired_sleep(character_id : int):
    """
    校验角色是否疲劳或困倦
    Keyword arguments:
    character_id -- 角色id
    """
    from Script.Design import handle_instruct

    character_data: game_type.Character = cache.character_data[character_id]
    #交互对象结算
    if character_id:
        # 疲劳判定
        if character_data.hit_point <= 1 and not character_data.sp_flag.tired:
            character_data.sp_flag.tired = True
        # 仅在H或跟随模式下再进行结算
        if character_data.sp_flag.is_h or character_data.sp_flag.is_follow:
            # 如果疲劳了
            if character_data.sp_flag.tired or (attr_calculation.get_tired_level(character_data.tired_point) >= 2):
                pl_character_data: game_type.Character = cache.character_data[0]
                # 输出基础文本
                now_draw = draw.WaitDraw()
                now_draw.width = window_width
                # 跟随时，忽略H后停留的情况
                if character_data.sp_flag.is_follow and character_data.behavior.behavior_id != constant.Behavior.WAIT:
                    draw_text = _("太累了，无法继续跟随\n") if character_data.sp_flag.tired else _("太困了，无法继续跟随\n")
                    now_draw.text = character_data.name + draw_text
                    now_draw.draw()
                    character_data.sp_flag.is_follow = 0
                # 群交时
                elif handle_premise.handle_group_sex_mode_on(character_id):
                    # 自己退出
                    character_data.target_character_id = character_id
                    handle_instruct.chara_handle_instruct_common_settle(constant.CharacterStatus.STATUS_GROUP_SEX_NPC_HP_0_END, character_id)
                    # 检测当前场景中的NPC角色数量
                    scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
                    scene_data: game_type.Scene = cache.scene_data[scene_path_str]
                    # 去掉自己和玩家
                    last_character_list = scene_data.character_list.copy()
                    last_character_list.discard(0)
                    last_character_list.discard(character_id)
                    # 如果自己退出后，剩余NPC角色数量小于等于1，则转为普通H
                    if len(last_character_list) == 1:
                        new_traget_id = last_character_list.pop()
                        pl_character_data.target_character_id = new_traget_id
                        handle_instruct.chara_handle_instruct_common_settle(constant.CharacterStatus.STATUS_GROUP_SEX_TO_H)
                    # 如果没有人了，则结束H
                    elif len(last_character_list) == 0:
                        handle_instruct.handle_end_h()

                # H时，有意识H则正常检测，无意识H则不检测疲劳，只检测HP
                elif (
                    character_data.sp_flag.is_h and
                    (
                        not character_data.sp_flag.unconscious_h or
                        (character_data.sp_flag.unconscious_h and character_data.hit_point <= 1))
                    ):
                    character_data.sp_flag.is_h = False
                    pl_character_data.behavior.behavior_id = constant.Behavior.T_H_HP_0
                    pl_character_data.state = constant.CharacterStatus.STATUS_T_H_HP_0
                    # 调用结束H的指令
                    handle_instruct.handle_end_h()

    # 玩家计算
    else:
        # 玩家只进行HP1的疲劳判定
        if character_data.hit_point <= 1:
            # 绘制文本
            now_draw = draw.WaitDraw()
            now_draw.width = window_width
            draw_text = _("太累了，无法继续H\n")
            now_draw.text = character_data.name + draw_text
            now_draw.draw()
            # 数据处理
            character_data.sp_flag.tired = False
            target_data = cache.character_data[character_data.target_character_id]
            # 群交时
            if handle_premise.handle_group_sex_mode_on(character_id):
                character_data.behavior.behavior_id = constant.Behavior.GROUP_SEX_PL_HP_0_END
                character_data.state = constant.CharacterStatus.STATUS_GROUP_SEX_PL_HP_0_END
                # 调用结束H的指令
                handle_instruct.handle_group_sex_end()
            # 普通H时
            elif target_data.sp_flag.is_h:
                character_data.behavior.behavior_id = constant.Behavior.H_HP_0
                character_data.state = constant.CharacterStatus.STATUS_H_HP_0
                # 调用结束H的指令
                handle_instruct.handle_end_h()


def judge_character_follow(character_id: int) -> int:
    """
    处理跟随模式
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    bool -- 本次update时间切片内活动是否已完成
    """
    character_data: game_type.Character = cache.character_data[character_id]

    # 正常状态下的助理跟随，未智能跟随则变成智能跟随
    if (
        handle_premise.handle_not_follow(character_id) and
        handle_premise.handle_is_assistant(character_id) and
        handle_premise.handle_assistant_follow_1(character_id) and
        handle_premise.handle_action_not_sleep(character_id) and
        handle_premise.handle_normal_1(character_id)
        ):
        character_data.sp_flag.is_follow = 1

    # 智能跟随
    if character_data.sp_flag.is_follow == 1:
        # 取消所有工作和娱乐状态
        default.handle_cancel_all_work_and_entertainment_flag(character_id, 1, game_type.CharacterStatusChange, datetime.datetime)

    # 维持强制跟随的状态
    if character_data.sp_flag.is_follow == 2:
        character.init_character_behavior_start_time(character_id, cache.game_time)
        character_data.behavior.behavior_id = constant.Behavior.FOLLOW
        character_data.state = constant.CharacterStatus.STATUS_FOLLOW
        if character_data.position != cache.character_data[0].position:
            # print("检测到跟随，NPC编号为：",character_id)
            to_dr = cache.character_data[0].position
            tem_1, tem_2, move_path, move_time = character_move.character_move(character_id, to_dr)
            # print("开始移动，路径为：",move_path,"，时间为：",move_time)
            character_data.behavior.behavior_id = constant.Behavior.MOVE
            character_data.behavior.move_target = move_path
            character_data.behavior.duration = move_time
            character_data.state = constant.CharacterStatus.STATUS_MOVE
    return 1


def judge_character_h_obscenity_unconscious(character_id: int) -> int:
    """
    判断H状态、猥亵与无意识\n
    Keyword arguments:
    character_id -- 角色id\n
    Return arguments:
    bool -- 本次update时间切片内活动是否已完成
    """
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
        # 刚刚射精状态下，用计数的方式来判断是否重置
        if character_data.h_state.just_shoot == 1:
            character_data.h_state.just_shoot = 2
        else:
            character_data.h_state.just_shoot = 0
        # 二次确认H意外结束的归零结算
        special_end_list = constant.special_end_H_list
        if len(cache.pl_pre_status_instruce) and cache.pl_pre_status_instruce[-1] in special_end_list and character_data.behavior.behavior_id not in special_end_list:
            default.handle_both_h_state_reset(0, 1, change_data=game_type.CharacterStatusChange, now_time=datetime.datetime)
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
        default.handle_self_orgasm_edge_off(character_id, 1, change_data=game_type.CharacterStatusChange, now_time=datetime.datetime)
    # 将时停解放状态改为False
    if handle_premise.handle_self_time_stop_orgasm_relase(character_id):
        character_data.h_state.time_stop_release = False

    # H状态或木头人时，行动锁死为等待不动
    if character_data.sp_flag.is_h or character_data.hypnosis.blockhead:
        # 睡奸时例外
        if character_data.state == constant.CharacterStatus.STATUS_SLEEP:
            return 1
        # 群交时则进行群交AI判断处理
        if handle_premise.handle_group_sex_mode_on(character_id) and not handle_premise.handle_npc_ai_type_0_in_group_sex(character_id):
            npc_ai_in_group_sex(character_id)
            return 1
        character_data.behavior.behavior_id = constant.Behavior.WAIT
        character_data.state = constant.CharacterStatus.STATUS_WAIT
        character_data.behavior.start_time = pl_character_data.behavior.start_time
        character_data.behavior.duration = pl_character_data.behavior.duration
        character_data.target_character_id = character_id

    # 如果不在同一位置
    if handle_premise_place.handle_not_in_player_scene(character_id):

        # 如果不在同一位置，则结束H状态和无意识状态
        if character_data.sp_flag.is_h:
            character_data.sp_flag.is_h = False
            character_data.sp_flag.unconscious_h = 0
            character_data.behavior.behavior_id = constant.Behavior.END_H
            character_data.state = constant.CharacterStatus.STATUS_END_H
            character_data.behavior.start_time = pl_character_data.behavior.start_time
            character_data.behavior.duration = pl_character_data.behavior.duration
            character_data.target_character_id = character_id

        # 如果不在同一位置，则结束睡眠猥亵状态
        elif character_data.sp_flag.unconscious_h == 1:
            character_data.sp_flag.unconscious_h = 0

        # 如果不在同一位置，则结束空气催眠
        elif character_data.sp_flag.unconscious_h == 5 and character_data.position != pl_character_data.pl_ability.air_hypnosis_position:
            character_data.sp_flag.unconscious_h = 0

    return 1


def judge_character_cant_move(character_id: int) -> int:
    """
    无法自由移动的角色\n
    Keyword arguments:
    character_id -- 角色id\n
    Return arguments:
    bool -- 本次update时间切片内活动是否已完成
    """
    character_data: game_type.Character = cache.character_data[character_id]

    cant_move_flag = False

    # 被囚禁
    if character_data.sp_flag.imprisonment:
        cant_move_flag = True
        # character.init_character_behavior_start_time(character_id, cache.game_time)
        # character_data.behavior.behavior_id = constant.Behavior.WAIT
        # character_data.state = constant.CharacterStatus.STATUS_WAIT

    # 临盆和产后
    if character_data.talent[22] == 1 or character_data.talent[23] == 1:
        cant_move_flag = True
        # character.init_character_behavior_start_time(character_id, cache.game_time)
        # character_data.behavior.behavior_id = constant.Behavior.WAIT
        # character_data.state = constant.CharacterStatus.STATUS_WAIT

        # 检测当前位置是否在医疗部的住院部，如果不在的话则移动至住院部
        now_position = character_data.position
        now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
        now_scene_data = cache.scene_data[now_scene_str]
        if "Inpatient_Department" not in now_scene_data.scene_tag:
            to_Inpatient_Department = map_handle.get_map_system_path_for_str(random.choice(constant.place_data["Inpatient_Department"]))
            map_handle.character_move_scene(character_data.position, to_Inpatient_Department, character_id)
    return cant_move_flag


def find_character_target(character_id: int, now_time: datetime.datetime):
    """
    查询角色可用目标活动并赋给角色
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    start_time = character_data.behavior.start_time
    all_target_list = list(game_config.config_target.keys())
    premise_data = {}
    target_weight_data = {}
    null_target_set = set()

    # 如果该NPC在H模式
    if character_data.sp_flag.is_h:
        # 群交中+要群交自慰时，才能继续下去
        if handle_premise.handle_group_sex_mode_on(character_id) and handle_premise.handle_masturebate_flag_3(character_id):
            pass
        # 否则不赋予新活动，且直接加入结束列表
        else:
            cache.over_behavior_character.add(character_id)
            return

    # 如果玩家在对该NPC交互，则等待flag=1，此操作暂时不进行
    # safe_instruct = [constant.CharacterStatus.STATUS_WAIT,constant.CharacterStatus.STATUS_REST,constant.CharacterStatus.STATUS_SLEEP]
    # if PC_character_data.target_character_id == character_id:
    #     # print(f"debug character_id = {character_data.name}，state = {PC_character_data.state}")
    #     if character_data.state not in safe_instruct:
    #         character_data.sp_flag.wait_flag = 1

    # 首先判定是否有高优先级的行动
    type_0_target_list = game_config.config_target_type_index[0]
    target, weight, judge, new_premise_data = search_target(character_id, type_0_target_list, null_target_set, premise_data, target_weight_data)
    # 将行动列表加到null_target中，将新的前提数据加到premise_data中
    null_target_set.update(type_0_target_list)
    premise_data = new_premise_data
    # 然后判断需求，先判断需求链中的需求，再判断非链中的需求，最后判断是否需要进入需求链
    if judge == 0 and not handle_premise.handle_normal_1(character_id):
        now_target_list = game_config.config_target_type_index[12]
        target, weight, judge, new_premise_data = search_target(character_id, now_target_list, null_target_set, premise_data, target_weight_data)
        null_target_set.update(now_target_list)
        premise_data = new_premise_data
    # 非链中的需求
    if judge == 0 and handle_premise.handle_unnormal_27(character_id):
        now_target_list = game_config.config_target_type_index[13]
        target, weight, judge, new_premise_data = search_target(character_id, now_target_list, null_target_set, premise_data, target_weight_data)
        null_target_set.update(now_target_list)
        premise_data = new_premise_data
    # 进入需求链
    if judge == 0:
        now_target_list = game_config.config_target_type_index[11]
        target, weight, judge, new_premise_data = search_target(character_id, now_target_list, null_target_set, premise_data, target_weight_data)
        null_target_set.update(now_target_list)
        premise_data = new_premise_data
    # 然后判断助理，先判断助理服务链，再判断非链中的助理服务，最后判断是否要进入助理服务链
    if judge == 0 and handle_premise.handle_is_assistant(character_id):
        # 是否正在助理服务链中
        if judge == 0 and handle_premise.handle_assistant_salutation_of_ai_disable(character_id):
            now_target_list = game_config.config_target_type_index[42]
            target, weight, judge, new_premise_data = search_target(character_id, now_target_list, null_target_set, premise_data, target_weight_data)
            null_target_set.update(now_target_list)
            premise_data = new_premise_data
        # 是否进行非链的助理服务
        if judge == 0:
            now_target_list = game_config.config_target_type_index[43]
            target, weight, judge, new_premise_data = search_target(character_id, now_target_list, null_target_set, premise_data, target_weight_data)
            null_target_set.update(now_target_list)
            premise_data = new_premise_data
        # 是否进入助理服务链
        if judge == 0:
            now_target_list = game_config.config_target_type_index[41]
            target, weight, judge, new_premise_data = search_target(character_id, now_target_list, null_target_set, premise_data, target_weight_data)
            null_target_set.update(now_target_list)
            premise_data = new_premise_data
    # 然后判断工作，需要有工作，且在工作时间或到岗时间
    if judge == 0 and handle_premise.handle_have_work(character_id) and handle_premise.handle_to_work_time_or_work_time(character_id):
        # 进行工作
        if judge == 0:
            now_target_list = game_config.config_target_type_index[22]
            target, weight, judge, new_premise_data = search_target(character_id, now_target_list, null_target_set, premise_data, target_weight_data)
            null_target_set.update(now_target_list)
            premise_data = new_premise_data
        # 工作准备
        if judge == 0:
            now_target_list = game_config.config_target_type_index[21]
            target, weight, judge, new_premise_data = search_target(character_id, now_target_list, null_target_set, premise_data, target_weight_data)
            null_target_set.update(now_target_list)
            premise_data = new_premise_data
    # 然后判断娱乐，需要在娱乐时间
    if judge == 0 and handle_premise.handle_all_entertainment_time(character_id):
        # 进行娱乐
        if judge == 0:
            now_target_list = game_config.config_target_type_index[32]
            target, weight, judge, new_premise_data = search_target(character_id, now_target_list, null_target_set, premise_data, target_weight_data)
            null_target_set.update(now_target_list)
            premise_data = new_premise_data
        # 娱乐后处理
        if judge == 0:
            now_target_list = game_config.config_target_type_index[33]
            target, weight, judge, new_premise_data = search_target(character_id, now_target_list, null_target_set, premise_data, target_weight_data)
            null_target_set.update(now_target_list)
            premise_data = new_premise_data
        # 娱乐准备
        if judge == 0:
            now_target_list = game_config.config_target_type_index[31]
            target, weight, judge, new_premise_data = search_target(character_id, now_target_list, null_target_set, premise_data, target_weight_data)
            null_target_set.update(now_target_list)
            premise_data = new_premise_data

    # 如果以上都没有，则开始遍历各大类的目标行动
    if judge == 0:
        now_target_list = []
        target_type_list = []

        # 如果已经有now_target_list了，则直接使用
        if len(now_target_list):
            now_target_list = now_target_list
        # 或者有target_type_list，则遍历后加入now_target_list
        elif len(target_type_list):
            for target_type in target_type_list:
                now_target_list.extend(game_config.config_target_type_index[target_type])
        # 如果还是没有，则遍历所有大类
        else:
            now_target_list = all_target_list

        target, weight, judge, new_premise_data = search_target(
            character_id,
            now_target_list,
            null_target_set,
            premise_data,
            target_weight_data,
        )
        # if character_data.name == "阿米娅":
        #     print(f"\ndebug 阿米娅的target = {target},weight = {weight},now_time = {now_time}")
        #     if 5 <= int(target) <= 30:
        #         print(f"debug position = {character_data.position},move_final_target = {character_data.behavior.move_final_target}")
    if judge:
        # print(f"debug {character_data.name}")
        # print(f"debug null_target_set = {null_target_set}")
        # print(f"debug premise_data = {premise_data}")
        # if character_data.name == "阿米娅":
        #     print(f"debug {character_data.name}的target = {target},weight = {weight},now_time = {now_time}")
        target_config = game_config.config_target[target]
        state_machine_id = target_config.state_machine_id
        #如果上个AI行动是普通交互指令，则将等待flag设为1
        # if state_machine_id >= 100:
        #     character_data.sp_flag.wait_flag = 1
            # print(f"debug 前一个状态机id = ",state_machine_id,",flag变为1,character_name =",character_data.name)
        constant.handle_state_machine_data[state_machine_id](character_id)
        # if character_data.name == "阿米娅":
        #     print(f"debug 中：{character_data.name}，behavior_id = {game_config.config_status[character_data.state].name}，start_time = {character_data.behavior.start_time}, game_time = {now_time}")
    else:
        now_judge = game_time.judge_date_big_or_small(start_time, now_time)
        if now_judge:
            cache.over_behavior_character.add(character_id)
        else:
            next_time = game_time.get_sub_date(minute=1, old_date=start_time)
            cache.character_data[character_id].behavior.start_time = next_time


def search_target(
    character_id: int,
    target_list: list,
    null_target: set,
    premise_data: Dict[int, int],
    target_weight_data: Dict[int, int],
):
    """
    查找可用目标\n
    Keyword arguments:\n
    character_id -- 角色id\n
    target_list -- 检索的目标列表\n
    null_target -- 被排除的目标\n
    premise_data -- 已算出的前提权重\n
    target_weight_data -- 已算出权重的目标列表\n
    Return arguments:\n
    int -- 目标id\n
    int -- 目标权重\n
    bool -- 前提是否能够被满足\n
    """
    target_data = {}
    for target in target_list:
        if target in null_target:
            continue
        if target in target_weight_data:
            target_data.setdefault(target_weight_data[target], set())
            target_data[target_weight_data[target]].add(target)
            continue
        if target not in game_config.config_target_premise_data:
            target_data.setdefault(1, set())
            target_data[1].add(target)
            target_weight_data[target] = 1
            continue
        target_premise_list = game_config.config_target_premise_data[target]
        now_weight = 0
        now_target_pass_judge = 0
        now_target_data = {}
        premise_judge = 1
        for premise in target_premise_list:
            premise_judge = 0
            if premise in premise_data:
                premise_judge = premise_data[premise]
            else:
                premise_judge = handle_premise.handle_premise(premise, character_id)
                premise_judge = max(premise_judge, 0)
                premise_data[premise] = premise_judge
            if premise_judge:
                now_weight += premise_judge
            else:
                if premise in game_config.config_effect_target_data and premise not in premise_data:
                    pass
                    # 暂时不用该功能
                    """
                    now_target_list = game_config.config_effect_target_data[premise] - null_target
                    now_target, now_target_weight, now_judge = search_target(
                        character_id,
                        now_target_list,
                        null_target,
                        premise_data,
                        target_weight_data,
                    )
                    if now_judge:
                        now_target_data.setdefault(now_target_weight, set())
                        now_target_data[now_target_weight].add(now_target)
                        now_weight += now_target_weight
                    else:
                        now_target_pass_judge = 1
                        break
                    """
                else:
                    now_target_pass_judge = 1
                    break
        if now_target_pass_judge:
            null_target.add(target)
            target_weight_data[target] = 0
            continue
        if premise_judge:
            target_data.setdefault(now_weight, set())
            target_data[now_weight].add(target)
            target_weight_data[target] = now_weight
            # 如果权重已经大于100，则直接返回
            if now_weight >= 100:
                # print(f"debug now_weight = {now_weight}")
                return target, now_weight, 1, premise_data
        else:
            now_value_weight = value_handle.get_rand_value_for_value_region(list(now_target_data.keys()))
            target_data.setdefault(now_weight, set())
            target_data[now_weight].add(random.choice(list(now_target_data[now_value_weight])))
    if len(target_data):
        value_weight = value_handle.get_rand_value_for_value_region(list(target_data.keys()))
        final_target = random.choice(list(target_data[value_weight]))
        # if character_id == 1:
        #     print(f"debug target_data = {target_data} , final_target = {final_target} , value_weight = {value_weight}")
        #     if final_target == "531":
        #         print(f"debug value_weight = {value_weight}")
        #     print(f"debug value_weight = {value_weight}")
        return final_target, value_weight, 1, premise_data
    return "", 0, 0, premise_data


def judge_interrupt_character_behavior(character_id: int) -> int:
    """
    判断是否需要打断角色的当前行动\n
    Keyword arguments:
    character_id -- 角色id\n
    interrupt_type -- 打断类型\n
    Return arguments:
    bool -- 是否打断
    """
    character_data: game_type.Character = cache.character_data[character_id]

    # 休息中的相关判断
    if handle_premise.handle_action_rest(character_id):
        # 疲劳归零，且HP、MP满值时，则立刻结束休息
        if (
            handle_premise.handle_tired_le_0(character_id) and
            handle_premise.handle_hp_max(character_id) and
            handle_premise.handle_mp_max(character_id)
        ):
            character_behavior.judge_character_status_time_over(character_id, cache.game_time, end_now = 2)
            return 1

    # 睡觉中的相关判断，需要没有被安眠药
    elif handle_premise.handle_action_sleep(character_id) and handle_premise.handle_self_not_sleep_pills(character_id):
        # ①睡觉中，早安问候服务开启中，今日未问候，角色行动结束时间晚于游戏时间，则将行动结束时间设为问候时间
        if (
            handle_premise.handle_assistant_morning_salutation_on(character_id) and
            handle_premise.handle_morning_salutation_flag_0(character_id) and
            handle_premise.handle_chara_behavior_end_time_lateer_than_game_time(character_id)
        ):
            # 角色醒来时间
            start_time = character_data.behavior.start_time
            end_time = game_time.get_sub_date(minute=character_data.behavior.duration, old_date=start_time)
            # 玩家醒来时间
            pl_character_data = cache.character_data[0]
            plan_to_wake_time = pl_character_data.action_info.plan_to_wake_time
            wake_time_hour, wake_time_minute = plan_to_wake_time[0], plan_to_wake_time[1]
            # 正确的醒来时间是end_time的时间中小时和分钟被替换为玩家醒来时间的小时和分钟
            judge_wake_up_time = end_time.replace(hour=wake_time_hour, minute=wake_time_minute)
            # 如果角色的行动结束时间在玩家醒来时间之后，则将行动结束时间设为玩家醒来时间
            # 通过判定行动时间来限制只触发一次
            if game_time.judge_date_big_or_small(end_time, judge_wake_up_time) and character_data.behavior.duration == 480:
                new_duration = int((judge_wake_up_time - start_time).seconds / 60)
                # print(f"debug {character_data.name}早安问候服务开启中，今日未问候，将行动结束时间设为问候时间，玩家醒来时间={pl_character_data.action_info.wake_time}，角色行动结束时间={end_time},原行动时间={character_data.behavior.duration}分钟，新行动时间={new_duration}分钟")
                character_data.behavior.duration = new_duration

        # ②睡觉中，疲劳归零，且HP、MP满值时，当前非睡觉时间，角色行动结束时间晚于游戏时间，则立刻结束睡觉
        if (
            handle_premise.handle_tired_le_0(character_id) and
            handle_premise.handle_hp_max(character_id) and
            handle_premise.handle_mp_max(character_id) and
            not handle_premise.handle_game_time_is_sleep_time(character_id) and
            handle_premise.handle_chara_behavior_end_time_lateer_than_game_time(character_id)
        ):
            character_behavior.judge_character_status_time_over(character_id, cache.game_time, end_now = 2)
            # print(f"debug {character_data.name}疲劳归零，结束睡觉，当前时间={cache.game_time}")
            return 1

    # 工作或娱乐中的相关判断
    elif handle_premise.handle_action_work_or_entertainment(character_id):
        # 今日未洗澡，到了淋浴时间，距离行动结束时间还有至少30分钟，正常状态下，则立刻结束工作或娱乐
        if (
            handle_premise.handle_shower_flag_0(character_id) and
            handle_premise.handle_shower_time(character_id) and
            handle_premise.handle_still_30_minutes_before_end(character_id) and
            handle_premise.handle_normal_all(character_id)
        ):
            character_behavior.judge_character_status_time_over(character_id, cache.game_time, end_now = 2)
            # print(f"debug {character_data.name}立刻结束工作或娱乐，当前时间={cache.game_time}")
            return 1

    return 0


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
    # 判定是否吵醒，吵醒则先结算当前行动然后进入重度性骚扰失败状态
    if weak_rate >= random.randint(1,100):
        target_data.tired_point = 0
        target_data.sleep_point = 0
        # 输出提示信息
        now_draw = draw.WaitDraw()
        now_draw.width = window_width
        now_draw.text = _("\n因为{0}的动作，{1}从梦中惊醒过来\n").format(now_character_data.name, target_data.name)
        now_draw.draw()
        # 终止对方的睡眠
        character_behavior.judge_character_status_time_over(now_character_data.target_character_id, cache.game_time, end_now = 2)
        # 停止对方的无意识状态与H状态
        target_data.sp_flag.unconscious_h = 0
        target_data.sp_flag.is_h = False
        # 对方获得睡奸醒来状态
        target_data.sp_flag.sleep_h_awake = True
        # 重置双方H结构体和相关数据
        default.handle_both_h_state_reset(0, 1, game_type.CharacterStatusChange, datetime.datetime)
        # 检测是否满足高级性骚扰的实行值需求
        if handle_premise.handle_instruct_judge_high_obscenity(0):
            # 如果已经陷落的话
            if handle_premise.handle_target_fall(character_id):
            # 爱情线会变成轻度性骚扰
                if handle_premise.handle_target_love_ge_1(character_id):
                    now_character_data.behavior.behavior_id = constant.Behavior.LOW_OBSCENITY_ANUS
                    now_character_data.state = constant.CharacterStatus.STATUS_LOW_OBSCENITY_ANUS
                # 隶属线会愤怒生气
                elif handle_premise.handle_target_obey_ge_1(character_id):
                    target_data.angry_point += 100
                    target_data.sp_flag.angry_with_player = True
                # 如果没有陷落的话，会变成高级性骚扰
                else:
                    now_character_data.behavior.behavior_id = constant.Behavior.HIGH_OBSCENITY_ANUS
                    now_character_data.state = constant.CharacterStatus.STATUS_HIGH_OBSCENITY_ANUS
            # 如果没有陷落的话，会变成高级性骚扰
            else:
                now_character_data.behavior.behavior_id = constant.Behavior.HIGH_OBSCENITY_ANUS
                now_character_data.state = constant.CharacterStatus.STATUS_HIGH_OBSCENITY_ANUS
        # 不满足的话，设为H失败
        else:
            now_character_data.behavior.behavior_id = constant.Behavior.DO_H_FAIL
            now_character_data.state = constant.CharacterStatus.STATUS_DO_H_FAIL
        now_character_data.behavior.duration = 10
        # 为了让惊醒正常运作，需要时间推进十分钟
        update.game_update_flow(10)


def judge_same_position_npc_follow():
    """
    判断同位置的NPC是否跟随玩家\n
    Keyword arguments:\n
    无
    """
    pl_character_data: game_type.Character = cache.character_data[0]
    for character_id in cache.npc_id_got:
        character_data: game_type.Character = cache.character_data[character_id]
        # 跳过不在同一位置的NPC
        if character_data.position != pl_character_data.position:
            continue
        # 智能跟随、异常状态267正常
        if (
            character_data.sp_flag.is_follow == 1 and
            handle_premise.handle_normal_267(character_id)
            ):

            # 变成移动状态，目标为玩家位置
            tem_1, tem_2, move_path, move_time = character_move.character_move(character_id, pl_character_data.behavior.move_final_target)
            move_flag, wait_flag = character_move.judge_character_move_to_private(character_id, move_path)
            if move_flag:
                character_data.behavior.behavior_id = constant.Behavior.MOVE
                character_data.state = constant.CharacterStatus.STATUS_MOVE
                character_data.behavior.move_target = move_path
                character_data.behavior.move_final_target = pl_character_data.behavior.move_final_target
                character_data.behavior.duration = move_time
                character_data.behavior.start_time = pl_character_data.behavior.start_time
                character_data.target_character_id = character_id
                character_data.action_info.follow_wait_time = 0
            elif wait_flag:
                character_data.state = constant.CharacterStatus.STATUS_WAIT
                character_data.behavior.behavior_id = constant.Behavior.WAIT
                character_data.behavior.duration = 5
                character_data.action_info.follow_wait_time += 5

            # print(f"debug {character_data.name}跟随玩家，当前位置为{character_data.position}，当前目标位置为{move_path}，最终目标位置为{pl_character_data.behavior.move_final_target}，行动时间为{move_time}分钟, start_time = {character_data.behavior.start_time}")


def get_chara_entertainment(character_id: int):
    """
    刷新角色的娱乐活动\n
    Keyword arguments:\n
    character_id -- 角色id
    """
    week_day = cache.game_time.weekday()
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id:
        # 重置基础数据
        character_data.sp_flag.swim = 0

        # 如果当天有派对的话，则全员当天娱乐为该娱乐
        if hasattr(cache.rhodes_island, 'party_day_of_week') and cache.rhodes_island.party_day_of_week[week_day]:
            for i in range(3):
                character_data.entertainment.entertainment_type[i] = cache.rhodes_island.party_day_of_week[week_day]

        # 否则随机当天的娱乐活动
        else:
            # 幼女只能进行过家家的娱乐活动
            if handle_premise.handle_self_is_child(character_id):
                for i in range(3):
                    character_data.entertainment.entertainment_type[i] = 151
                return
            entertainment_list = [i for i in game_config.config_entertainment]
            entertainment_list.remove(0)
            # 循环获得上午、下午、晚上的三个娱乐活动
            for i in range(3):

                # 进入主循环
                while 1:
                    # 开始随机
                    choice_entertainment_id = random.choice(entertainment_list)
                    entertainment_data = game_config.config_entertainment[choice_entertainment_id]
                    # if choice_entertainment_id in {92, 151}:
                    #     print(f"debug {character_data.name}: {choice_entertainment_id}")
                    # 首先检查娱乐地点的场所是否开放
                    if entertainment_data.palce in game_config.config_facility_open_name_set:
                        facility_open_cid = game_config.config_facility_open_name_to_cid[entertainment_data.palce]
                        # 如果该娱乐活动的场所未开放，则去掉该id后重新随机
                        if cache.rhodes_island.facility_open[facility_open_cid] == 0:
                            entertainment_list.remove(choice_entertainment_id)
                            continue
                    # 检查该娱乐活动是否需要特定的条件
                    if entertainment_data.need == "无":
                        break
                    else:
                        need_data_all = entertainment_data.need
                        # 整理需要的条件
                        if "&" not in need_data_all:
                            need_data_list = [need_data_all]
                        else:
                            need_data_list = need_data_all.split('&')
                        judge, reason = attr_calculation.judge_require(need_data_list, character_id)
                        # 如果满足条件则选择该娱乐活动，否则去掉该id后重新随机
                        if judge:
                            break
                        else:
                            entertainment_list.remove(choice_entertainment_id)
                            continue

                # 跳出循环后，将该娱乐活动赋值给角色
                character_data.entertainment.entertainment_type[i] = choice_entertainment_id
                entertainment_list.remove(choice_entertainment_id) # 从列表中去掉该娱乐活动，防止重复


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

    # 能力等级权重为20
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
        part_weight[part_id] += now_ability * 20

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
        if part_id == 0 and "N" in status_tag_list:
            all_stastus_list.append(status_id)
        elif part_id == 1 and "B" in status_tag_list:
            all_stastus_list.append(status_id)
        elif part_id == 2 and "C" in status_tag_list:
            all_stastus_list.append(status_id)
        elif part_id == 4 and "V" in status_tag_list:
            all_stastus_list.append(status_id)
        elif part_id == 5 and "A" in status_tag_list:
            all_stastus_list.append(status_id)
        elif part_id == 6 and "U" in status_tag_list:
            all_stastus_list.append(status_id)
        elif part_id == 7 and "W" in status_tag_list:
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
    NPC在群交中的AI\n
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

    # 如果设定NPC为仅自慰，则进入要自慰后返回
    if handle_premise.handle_npc_ai_type_1_in_group_sex(character_id):
        character_data.sp_flag.masturebate = 3
        character_data.state = constant.CharacterStatus.STATUS_ARDER
        # print(f"debug {character_data.name}进入了要自慰状态")
        return

    # 首先看玩家当前是否有部位空缺
    now_template_empty_part_list = []
    wait_upon_flag = True # 侍奉是否可选
    wait_upon_state_id = A_template_data[1][1] # 侍奉的状态id
    # 对单
    for body_part in A_template_data[0]:
        state_id = A_template_data[0][body_part][1]
        if state_id == -1:
            # 如果不是阴茎，则直接加入
            if body_part != "penis":
                now_template_empty_part_list.append(body_part)
            # 如果是阴茎，则需要未选侍奉
            elif wait_upon_state_id == -1:
                now_template_empty_part_list.append(body_part)
        # 如果阴茎已选，则侍奉不可选
        elif body_part == "penis":
            wait_upon_flag = False
    # 侍奉
    if wait_upon_flag:
        target_chara_id_list = A_template_data[1][0]
        if wait_upon_state_id == -1:
            now_template_empty_part_list.append(_("侍奉"))
        elif wait_upon_state_id != -1 and len(target_chara_id_list) < 4:
            now_template_empty_part_list.append(_("加入侍奉"))

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
