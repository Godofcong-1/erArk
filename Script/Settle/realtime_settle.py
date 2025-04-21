import random
import datetime
from types import FunctionType
from Script.Core import (
    cache_control,
    game_path_config,
    game_type,
    constant,
    get_text,
)
from Script.Design import (
    game_time,
    handle_premise,
    handle_npc_ai_in_h,
    attr_calculation,
)
from Script.UI.Moudle import draw
from Script.UI.Panel import ejaculation_panel
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

def judge_pl_real_time_data() -> int:
    """
    玩家实时数据结算\n
    Keyword arguments:
    无\n
    Return arguments:
    无
    """

    pl_character_data: game_type.Character = cache.character_data[0]

    # 酒店退房时间到了则退房
    if cache.rhodes_island.love_hotel_room_lv > 0:
        if game_time.judge_date_big_or_small(cache.game_time, pl_character_data.action_info.check_out_time) > 0:
            # 输出提示信息
            room_name = [_("标间"),_("情趣主题房"),_("顶级套房")]
            now_draw = draw.NormalDraw()
            now_draw.text = _("\n您入住的{0}到退房时间了，已自动退房\n").format(room_name[cache.rhodes_island.love_hotel_room_lv - 1])
            now_draw.draw()
            # 结算
            cache.rhodes_island.love_hotel_room_lv = 0
            pl_character_data.action_info.check_out_time = datetime.datetime(1, 1, 1)


def character_aotu_change_value(character_id: int, now_time: datetime.datetime, pl_start_time: datetime.datetime):
    """
    结算角色随时间自动增加的数值
    Keyword arguments:
    character_id -- 角色id
    now_time -- 指定时间
    """
    now_character_data: game_type.Character = cache.character_data[character_id]
    if now_character_data.target_character_id not in cache.character_data:
        now_character_data.target_character_id = character_id
    target_data: game_type.Character = cache.character_data[now_character_data.target_character_id]
    add_time = now_character_data.behavior.duration
    # 真实的开始时间是当前角色行动开始时间和玩家行动开始时间中更晚的那个
    now_character_behavior_start_time = now_character_data.behavior.start_time
    true_start_time = max(now_character_behavior_start_time, pl_start_time)
    # 真实的结束时间是当前角色行动结束时间和当前时间中更早的那个
    now_character_end_time = game_time.get_sub_date(minute=add_time, old_date=now_character_behavior_start_time)
    true_end_time = min(now_character_end_time, now_time)
    # 真实的行动时间是真实的结束时间减去真实的开始时间
    true_add_time = int((true_end_time.timestamp() - true_start_time.timestamp()) / 60)
    # 避免负数
    true_add_time = max(true_add_time, 0)

    # 结算疲劳值
    tired_change = int(true_add_time / 6)
    # 基础行动结算1疲劳值
    if true_add_time == 5:
        tired_change = 1
    # 不睡觉时、且不是时停中，结算疲劳值
    if now_character_data.state not in {constant.CharacterStatus.STATUS_SLEEP} and handle_premise.handle_time_stop_off(character_id):
        now_character_data.tired_point += tired_change
        now_character_data.tired_point = min(now_character_data.tired_point,160)

    # 休息时回复体力、气力
    if now_character_data.state == constant.CharacterStatus.STATUS_REST:
        # 休息室对回复效果的影响
        if handle_premise.handle_in_rest_room_or_dormitory(character_id):
            final_adjust = 1
            # 休息室等级对回复效果的影响
            now_level = cache.rhodes_island.facility_level[31]
            facility_cid = game_config.config_facility_effect_data[_("休息室")][int(now_level)]
            facility_effect = game_config.config_facility_effect[facility_cid].effect
            facility_effect_adjust = 1 + facility_effect / 100
            final_adjust *= facility_effect_adjust
        # 非休息室的回复效果
        else:
            final_adjust = 0.3
        # 素质对回复效果的影响
        if now_character_data.talent[351]: # 回复慢
            final_adjust *= 0.7
        elif now_character_data.talent[352]: # 回复快
            final_adjust *= 1.5
        # 监禁时根据生活条件判定
        if handle_premise.handle_imprisonment_1(character_id):
            if cache.rhodes_island.confinement_training_setting[4] == 0:
                final_adjust *= 0.5
            elif cache.rhodes_island.confinement_training_setting[4] == 2:
                final_adjust *= 1.5
        # 回复体力、气力
        hit_point_add_base = now_character_data.hit_point_max * 0.003 + 10
        hit_point_add = int(hit_point_add_base * true_add_time * final_adjust)
        now_character_data.hit_point += hit_point_add
        now_character_data.hit_point = min(now_character_data.hit_point, now_character_data.hit_point_max)
        mana_point_add_base = now_character_data.mana_point_max * 0.006 + 20
        mana_point_add = int(mana_point_add_base * true_add_time * final_adjust)
        now_character_data.mana_point += mana_point_add
        now_character_data.mana_point = min(now_character_data.mana_point, now_character_data.mana_point_max)

    # 睡觉时大量减少疲劳值，增加熟睡值，回复体力、气力
    elif now_character_data.state == constant.CharacterStatus.STATUS_SLEEP:
        # 减少疲劳值
        tired_change *= 2
        now_character_data.tired_point -= tired_change
        now_character_data.tired_point = max(now_character_data.tired_point,0) # 最少为0
        # 熟睡值在到熟睡之前快速增加
        sleep_level,tem = attr_calculation.get_sleep_level(now_character_data.sleep_point)
        if sleep_level <= 1:
            add_sleep = int(true_add_time * 1.5)
            now_character_data.sleep_point += add_sleep
        # 熟睡值到熟睡后上下波动，加的可能性比减的可能性大一点点
        else:
            add_sleep = random.randint(int(true_add_time * -0.3),int(true_add_time * 0.6))
            now_character_data.sleep_point += add_sleep
        # 最高上限100
        now_character_data.sleep_point = min(now_character_data.sleep_point,100)
        # print(f"debug {now_character_data.name}疲劳值-{tired_change}={now_character_data.tired_point}，熟睡值+{add_sleep}={now_character_data.sleep_point}，当前时间={cache.game_time}")
        final_adjust = 1
        # 素质对回复效果的影响
        if now_character_data.talent[351]: # 回复慢
            final_adjust *= 0.7
        elif now_character_data.talent[352]: # 回复快
            final_adjust *= 1.5
        # 监禁时根据生活条件判定
        if handle_premise.handle_imprisonment_1(character_id):
            if cache.rhodes_island.confinement_training_setting[4] == 0:
                final_adjust *= 0.5
            elif cache.rhodes_island.confinement_training_setting[4] == 2:
                final_adjust *= 1.5
        # 回复体力、气力
        hit_point_add_base = now_character_data.hit_point_max * 0.0025 + 3
        hit_point_add = int(hit_point_add_base * true_add_time * final_adjust)
        now_character_data.hit_point += hit_point_add
        now_character_data.hit_point = min(now_character_data.hit_point, now_character_data.hit_point_max)
        mana_point_add_base = now_character_data.mana_point_max * 0.005 + 6
        mana_point_add = int(mana_point_add_base * true_add_time * final_adjust)
        now_character_data.mana_point += mana_point_add
        now_character_data.mana_point = min(now_character_data.mana_point, now_character_data.mana_point_max)

    # 结算尿意值
    if character_id == 0 and not cache.all_system_setting.difficulty_setting[12]:
        pass
    else:
        add_urinate = random.randint(int(true_add_time * 0.8), int(true_add_time * 1.2))
        add_urinate *= cache.all_system_setting.difficulty_setting[11] / 2
        now_character_data.urinate_point += int(add_urinate)
        now_character_data.urinate_point = min(now_character_data.urinate_point,300)

    # 结算饥饿值
    add_hunger = random.randint(int(true_add_time * 0.8), int(true_add_time * 1.2))
    now_character_data.hunger_point += add_hunger
    now_character_data.hunger_point = min(now_character_data.hunger_point,240)

    # 结算玩家部分
    if character_id == 0:

        # 非H模式下结算玩家的射精值减少
        if not now_character_data.sp_flag.is_h:
            # 上次射精时间距离现在超过30分钟则射精值减少
            last_time = now_character_data.action_info.last_eaj_add_time
            if (cache.game_time - last_time) > datetime.timedelta(minutes=30):
                now_character_data.eja_point -= true_add_time * 10
                now_character_data.eja_point = max(now_character_data.eja_point,0)

        # 玩家缓慢恢复精液量
        now_character_data.semen_point += int(true_add_time / 20)
        now_character_data.semen_point = min(now_character_data.semen_point,now_character_data.semen_point_max)

        # 结算玩家源石技艺的理智值消耗
        # 视觉系
        if now_character_data.pl_ability.visual:
            down_sp = max(int(true_add_time / 12),1)
            # 倍率计算
            multiple = now_character_data.talent[307] + now_character_data.talent[308] + now_character_data.talent[309]
            down_sp *= max(multiple, 1)
            # 用于消耗的理智值不得超过当前理智值
            down_sp = min(down_sp, now_character_data.sanity_point)
            now_character_data.sanity_point -= down_sp
            now_character_data.pl_ability.today_sanity_point_cost += down_sp
        # 时停系
        if handle_premise.handle_time_stop_on(character_id):
            down_sp = max(true_add_time * 2, 1)
            # 用于消耗的理智值不得超过当前理智值
            down_sp = min(down_sp, now_character_data.sanity_point)
            now_character_data.sanity_point -= down_sp
            now_character_data.pl_ability.today_sanity_point_cost += down_sp
        # 理智值不足则归零并中断所有开启中的源石技艺
        if handle_premise.handle_at_least_one_arts_on(character_id) and now_character_data.sanity_point <= 0:
            # 输出提示信息
            now_draw = draw.WaitDraw()
            now_draw.width = window_width
            now_draw.style = "red"
            now_draw.text = _("\n理智值不足，开启的源石技艺已全部中断\n")
            now_draw.draw()
            # 开始结算
            now_character_data.sanity_point = 0
            now_character_data.pl_ability.visual = False
            # 解除目标的催眠
            if target_data.sp_flag.unconscious_h >= 4:
                default.handle_hypnosis_cancel(0,1,game_type.CharacterStatusChange,datetime.datetime)
            # 时停中则进入时停解除状态
            if handle_premise.handle_time_stop_on(character_id):
                from Script.Design import handle_instruct
                handle_instruct.chara_handle_instruct_common_settle(constant.CharacterStatus.STATUS_TIME_STOP_OFF)

        # 结算对无意识对象的结算
        if target_data.sp_flag.unconscious_h:
            # 睡奸判定
            if target_data.state == constant.CharacterStatus.STATUS_SLEEP and target_data.sp_flag.unconscious_h == 1:
                # 如果是等待指令或安眠药中则无事发生
                if (
                    now_character_data.state == constant.CharacterStatus.STATUS_WAIT or
                    now_character_data.h_state.body_item[9][1] == 1
                ):
                    # 赋值为2来规避吵醒判定
                    sleep_level = 2
                # 如果是其他行动则判定是否吵醒
                else:
                    # 双倍扣除原本会增加的熟睡值
                    down_sleep = int(true_add_time * 3)
                    target_data.sleep_point -= down_sleep
                    # 计算当前熟睡等级
                    sleep_level,tem = attr_calculation.get_sleep_level(target_data.sleep_point)
                # 熟睡等级小于等于1时判定是否吵醒
                if sleep_level <= 1:
                    handle_npc_ai_in_h.judge_weak_up_in_sleep_h(character_id)

    # 结算非玩家部分
    else:
        # 结算精液流动
        if len(now_character_data.dirty.semen_flow):
            settle_semen_flow(character_id, true_add_time)

        # 结算乳汁量，仅结算有泌乳素质的
        if now_character_data.talent[27]:
            milk_change = int(true_add_time * 2 / 3)
            add_milk = random.randint(int(milk_change * 0.8), int(milk_change * 1.2))
            now_character_data.pregnancy.milk += add_milk
            now_character_data.pregnancy.milk = min(now_character_data.pregnancy.milk,now_character_data.pregnancy.milk_max)

        # 有意识下的部分持续结算
        if (
            handle_premise.handle_unconscious_flag_0(character_id) and
            handle_premise.handle_normal_5(character_id) and
            handle_premise.handle_normal_6(character_id)
            ):

            # 结算周围有其他人、状态12正常下，不穿胸衣和内裤时的羞耻值增加
            if (
                handle_premise.handle_not_wear_bra_or_pan(character_id) and 
                handle_premise.handle_scene_over_two(character_id) and 
                handle_premise.handle_normal_1(character_id) and 
                handle_premise.handle_normal_2(character_id)
                ):
                exposure_adjust = 0
                if handle_premise.handle_not_wear_bra(character_id):
                    exposure_adjust += 1
                if handle_premise.handle_not_wear_pan(character_id):
                    exposure_adjust += 2
                default.base_chara_state_common_settle(character_id, add_time=true_add_time, state_id=16, base_value=0, ability_level=now_character_data.ability[34], extra_adjust=exposure_adjust, tenths_add=False)

            # 结算灌肠中，苦痛值增加
            if handle_premise.handle_enema(character_id):
                enema_just = now_character_data.dirty.enema_capacity
                default.base_chara_state_common_settle(character_id, add_time=true_add_time, state_id=17, base_value=0, ability_level=now_character_data.ability[15], extra_adjust=enema_just, tenths_add=False)

            # 结算捆绑中，欲情、羞耻和苦痛增加
            if handle_premise.handle_self_now_bondage(character_id):
                bondage_id = now_character_data.h_state.bondage
                bondage_data = game_config.config_bondage[bondage_id]
                bondage_adjust = bondage_data.level * 0.5
                default.base_chara_state_common_settle(character_id, add_time=true_add_time, state_id=12, base_value=0, ability_level=now_character_data.ability[33], extra_adjust=bondage_adjust, tenths_add=False)
                default.base_chara_state_common_settle(character_id, add_time=true_add_time, state_id=16, base_value=0, ability_level=now_character_data.ability[34], extra_adjust=bondage_adjust, tenths_add=False)
                default.base_chara_state_common_settle(character_id, add_time=true_add_time, state_id=17, base_value=0, ability_level=now_character_data.ability[15], extra_adjust=bondage_adjust, tenths_add=False)

def settle_semen_flow(character_id: int, true_add_time: int):
    """
    结算精液流动\n
    Keyword arguments:\n
    character_id -- 角色id\n
    true_add_time -- 实际行动时间\n
    """
    now_character_data: game_type.Character = cache.character_data[character_id]
    # 计算流动的精液量
    flow_semen_max = int(true_add_time * 2)
    # print(f"debug {now_character_data.name}的精液流动最大量为{flow_semen_max}，add_time = {true_add_time}")

    new_flow_list = []
    # 遍历每个部位的精液流动
    for all_flow_dict in now_character_data.dirty.semen_flow:
        # 实际流动的精液总量
        all_real_flow = 0
        # 源头数据
        source_id = all_flow_dict["source"]["id"]
        source_type = all_flow_dict["source"]["type"]
        new_target_list = []
        # 如果all_flow_dict没有键"targets"，则跳过
        if "targets" not in all_flow_dict:
            continue
        # 遍历每个流动的目标
        for now_flow_dict in all_flow_dict["targets"]:
            if now_flow_dict["remaining_volume"] > 0:
                # 计算该部位的精液流动
                now_flow = min(flow_semen_max, now_flow_dict["remaining_volume"])
                all_real_flow += now_flow
                now_flow_dict["remaining_volume"] -= now_flow
                now_part_cid = now_flow_dict["id"]
                # print(f"debug {now_character_data.name}，{now_flow_dict['type']}的{now_part_cid}部位，精液流动{now_flow}，剩余{now_flow_dict['remaining_volume']}")
                # 目标部位的精液增加
                ejaculation_panel.update_semen_dirty(character_id=character_id, part_cid=now_part_cid, part_type=now_flow_dict["type"], semen_count=now_flow, update_shoot_position_flag=False)
                # 如果目标部位的精液流动完毕，则将其从流动列表中移除
                if now_flow_dict["remaining_volume"] > 0:
                    new_target_list.append(now_flow_dict)
        # 更新流动的目标列表
        all_flow_dict["targets"] = new_target_list
        # 遍历完全目标后，如果实际流动的精液总量大于0，则在源头部位减少相应的精液量
        if all_real_flow > 0:
            ejaculation_panel.update_semen_dirty(character_id=character_id, part_cid=source_id, part_type=source_type, semen_count=-all_real_flow, update_shoot_position_flag=False)
        # 如果源头部位的精液流动完毕，则将其从流动列表中移除，否则将其加入新的流动列表
        if len(all_flow_dict["targets"]):
            new_flow_list.append(all_flow_dict)
    # 更新流动的源头列表
    now_character_data.dirty.semen_flow = new_flow_list
    # print(f"debug {now_character_data.name}的精液流动完毕，剩余流动列表为{now_character_data.dirty.semen_flow}")


def change_character_persistent_state(character_id: int):
    """
    结算角色的状态是否会持续\n
    Keyword arguments:\n
    character_id -- 角色id\n
    """
    now_character_data: game_type.Character = cache.character_data[character_id]
    # 因为睡眠时间很长，会导致持续状态的时间超过了当前时间，所以改为使用当前时间
    # start_time = now_character_data.behavior.start_time
    # now_time = game_time.get_sub_date(minute=now_character_data.behavior.duration, old_date=start_time)
    now_time = cache.game_time

    # H下结算全部持续状态
    if now_character_data.sp_flag.is_h:
        # 结算H状态的持续时间
        for i in range(len(now_character_data.h_state.body_item)):
            if now_character_data.h_state.body_item[i][1]:
                end_time = now_character_data.h_state.body_item[i][2]
                if end_time != None and game_time.judge_date_big_or_small(now_time,end_time):
                    now_character_data.h_state.body_item[i][1] = False
                    now_character_data.h_state.body_item[i][2] = None
    # 非H下结算部分药物
    else:
        for i in [8, 9]:
            if now_character_data.h_state.body_item[i][1]:
                end_time = now_character_data.h_state.body_item[i][2]
                if end_time != None and game_time.judge_date_big_or_small(now_time,end_time):
                    now_character_data.h_state.body_item[i][1] = False
                    now_character_data.h_state.body_item[i][2] = None
