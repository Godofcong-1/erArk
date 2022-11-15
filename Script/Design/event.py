import random
from Script.Core import cache_control, game_type, value_handle, constant
from Script.Design import map_handle
from Script.UI.Panel import draw_event_text_panel
from Script.Config import normal_config, game_config

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """


def handle_event(character_id: int) -> (draw_event_text_panel.DrawEventTextPanel, str):
    """
    处理状态触发事件
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    draw.LineFeedWaitDraw -- 事件绘制文本
    str -- 事件id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    behavior_id = character_data.behavior.behavior_id
    now_event_data = {}
    now_premise_data = {}
    if (
        behavior_id in game_config.config_event_status_data
    ):
        for event_id in game_config.config_event_status_data[behavior_id]:
            now_weight = 1
            event_config = game_config.config_event[event_id]
            if len(event_config.premise):
                now_weight = 0 
                for premise in event_config.premise:
                    if premise in now_premise_data:
                        if not now_premise_data[premise]:
                            now_weight = 0
                            break
                        now_weight += now_premise_data[premise]
                    else:
                        now_add_weight = constant.handle_premise_data[premise](character_id)
                        now_premise_data[premise] = now_add_weight
                        if now_add_weight:
                            now_weight += now_add_weight
                        else:
                            now_weight = 0
                            break
            if now_weight:
                now_event_data.setdefault(now_weight, set())
                now_event_data[now_weight].add(event_id)
    now_event_id = ""
    if now_event_data:
        event_weight = value_handle.get_rand_value_for_value_region(list(now_event_data.keys()))
        now_event_id = random.choice(list(now_event_data[event_weight]))
    if now_event_id != "":
        return draw_event_text_panel.DrawEventTextPanel(now_event_id,character_id, event_config.type)
