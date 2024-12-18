import random
from Script.Core import cache_control, game_type, value_handle, constant
from Script.Design import handle_premise
from Script.UI.Panel import draw_event_text_panel
from Script.Config import normal_config, game_config

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """


def handle_event(character_id: int, event_before_instrust_flag = False) -> (draw_event_text_panel.DrawEventTextPanel, str):
    """
    处理状态触发事件
    Keyword arguments:
    character_id -- 角色id
    event_before_instrust_flag -- 是否是事件在前，指令在后（或跳过指令）
    Return arguments:
    draw.LineFeedWaitDraw -- 事件绘制文本
    str -- 事件id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_character_id = character_data.target_character_id
    target_character_data = cache.character_data[target_character_id]
    behavior_id = character_data.behavior.behavior_id
    now_event_data = {}
    now_premise_data = {}
    if (
        behavior_id in game_config.config_event_status_data
    ):
        for event_id in game_config.config_event_status_data[behavior_id]:
            now_weight = 1
            event_config = game_config.config_event[event_id]
            # 如果是角色专有事件，则判断角色id是否符合
            if event_config.adv_id not in {"","0"}:
                event_adv_id = int(event_config.adv_id)
                # print(f"debug event_config.adv_id:{event_config.adv_id}")
                # 事件由玩家触发，但交互对象不是该id，则跳过
                if "sys_0" in event_config.premise and event_adv_id != target_character_data.adv:
                    continue
                # 事件由NPC触发，但自己不是该id，则跳过
                elif "sys_1" in event_config.premise and event_adv_id != character_data.adv:
                    continue
                # 既不是自己id也不是交互对象id，则跳过
                else:
                    if event_adv_id != character_data.adv and event_adv_id != target_character_data.adv:
                        continue
            # 如果是事件在前，指令在后，判断是否需要跳过
            if event_before_instrust_flag:
                if event_config.type == 1:
                    continue
            # 和触发记录相关的前提
            if "this_event_in_triggered_record" in event_config.premise:
                if event_id not in cache.taiggered_event_record:
                    continue
            if "this_event_not_in_triggered_record" in event_config.premise:
                if event_id in cache.taiggered_event_record:
                    continue
            if "this_event_in_today_triggered_record" in event_config.premise:
                if event_id not in cache.today_taiggered_event_record:
                    continue
            if "this_event_not_in_today_triggered_record" in event_config.premise:
                if event_id in cache.today_taiggered_event_record:
                    continue
            if len(event_config.premise):
                # 计算前提字典的总权重
                premise_dict = event_config.premise
                now_weight = handle_premise.get_weight_from_premise_dict(premise_dict, character_id, unconscious_pass_flag = True)
            if now_weight:
                now_event_data.setdefault(now_weight, set())
                now_event_data[now_weight].add(event_id)
    now_event_id = ""
    if now_event_data:
        event_weight = value_handle.get_rand_value_for_value_region(list(now_event_data.keys()))
        now_event_id = random.choice(list(now_event_data[event_weight]))
        event_config = game_config.config_event[now_event_id]
    if now_event_id != "":
        # print(f"debug now_event_id:{now_event_id}")
        return draw_event_text_panel.DrawEventTextPanel(now_event_id, character_id, event_config.type)
