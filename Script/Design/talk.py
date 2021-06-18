import random
from Script.Core import cache_control, game_type, value_handle, constant
from Script.Design import map_handle
from Script.UI.Moudle import draw
from Script.Config import normal_config, game_config

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """


def handle_talk(character_id: int):
    """
    处理行为结算对话
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    behavior_id = character_data.behavior.behavior_id
    now_talk_data = {}
    now_premise_data = {}
    #检测是否是收藏模式#
    if cache.is_collection and character_id:
        player_data: game_type.Character = cache.character_data[0]
        if character_id not in player_data.collection_character:
            return
    #检测是否与玩家处于同一位置#
    if (
        character_data.position != cache.character_data[0].position
        and character_data.behavior.move_src != cache.character_data[0].position
    ):
        return
    if behavior_id in game_config.config_talk_data:
        for talk_id in game_config.config_talk_data[behavior_id]:
            talk_config = game_config.config_talk[talk_id]
            if talk_config.adv_id != 0:
                target_data: game_type.Character = cache.character_data[character_data.target_character_id]
                print(character_data.name,target_data.name,talk_config.context,character_data.adv,target_data.adv,talk_config.adv_id)
                if character_data.adv != talk_config.adv_id:
                    if target_data.adv != talk_config.adv_id:
                        continue
            now_weight = 1
            if talk_id in game_config.config_talk_premise_data:
                now_weight = 0
                for premise in game_config.config_talk_premise_data[talk_id]:
                    if premise in now_premise_data:
                        if not now_premise_data[premise]:
                            now_weight = 0
                            break
                        else:
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
                now_talk_data.setdefault(now_weight, set())
                now_talk_data[now_weight].add(talk_id)
    now_talk = ""
    if len(now_talk_data):
        talk_weight = value_handle.get_rand_value_for_value_region(list(now_talk_data.keys()))
        now_talk_id = random.choice(list(now_talk_data[talk_weight]))
        now_talk = game_config.config_talk[now_talk_id].context
    if now_talk != "":
        now_talk_text: str = now_talk
        scene_path = character_data.position
        scene_path_str = map_handle.get_map_system_path_str_for_list(scene_path)
        scene_data: game_type.Scene = cache.scene_data[scene_path_str]
        scene_name = scene_data.scene_name
        player_data: game_type.Character = cache.character_data[0]
        target_data: game_type.Character = cache.character_data[character_data.target_character_id]
        now_talk_text = now_talk_text.format(
            NickName=character_data.nick_name,
            FoodName=character_data.behavior.food_name,
            Name=character_data.name,
            SceneName=scene_name,
            PlayerNickName=player_data.nick_name,
            TargetName=target_data.name,
        )
        now_draw = draw.LineFeedWaitDraw()
        now_draw.text = now_talk_text
        now_draw.width = normal_config.config_normal.text_width
        now_draw.draw()
