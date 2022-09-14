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
    #第一段行为结算的口上
    if behavior_id in game_config.config_talk_data:
        for talk_id in game_config.config_talk_data[behavior_id]:
            talk_config = game_config.config_talk[talk_id]
            if talk_config.adv_id != 0:
                target_data: game_type.Character = cache.character_data[character_data.target_character_id]
                # print(character_data.name,target_data.name,talk_config.context,character_data.adv,target_data.adv,talk_config.adv_id)
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
            MakeFoodTime=character_data.behavior.make_food_time,
            Name=character_data.name,
            SceneName=scene_name,
            PlayerNickName=player_data.nick_name,
            TargetName=target_data.name,
        )
        now_draw = draw.LineFeedWaitDraw()
        now_draw.text = now_talk_text
        now_draw.width = normal_config.config_normal.text_width
        now_draw.draw()

    #第二段行为结算的口上

    #自己
    now_talk_data = {}
    now_premise_data = {}
    for second_behavior_id,behavior_data in character_data.second_behavior.items():
        if behavior_data != 0:
            now_talk_data = handle_talk_sub(character_id, second_behavior_id)
            #触发后该行为值归零
            character_data.second_behavior[second_behavior_id] = 0
            handle_talk_draw(character_id, now_talk_data)

    #交互对象
    now_talk_data = {}
    now_premise_data = {}
    if character_id == 0 and character_data.target_character_id:
        target_character_id = character_data.target_character_id
        target_character_data : game_type.Character = cache.character_data[target_character_id]
        for second_behavior_id,behavior_data in target_character_data.second_behavior.items():
            if behavior_data != 0:
                now_talk_data = handle_talk_sub(target_character_id, second_behavior_id)
                #触发后该行为值归零
                target_character_data.second_behavior[second_behavior_id] = 0
                handle_talk_draw(target_character_id, now_talk_data)



def handle_talk_sub(character_id: int, behavior_id: int):
    """
    处理行为结算对话的内置循环部分
    Keyword arguments:
    character_id -- 角色id
    behavior_id -- 行为id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_talk_data = {}
    now_premise_data = {}
    if behavior_id in game_config.config_talk_data:
        for talk_id in game_config.config_talk_data[behavior_id]:
            talk_config = game_config.config_talk[talk_id]
            if talk_config.adv_id != 0:
                target_data: game_type.Character = cache.character_data[character_data.target_character_id]
                # print(character_data.name,target_data.name,talk_config.context,character_data.adv,target_data.adv,talk_config.adv_id)
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
    return now_talk_data


def handle_talk_draw(character_id: int, now_talk_data: dict):
    """
    处理行为结算对话的输出
    Keyword arguments:
    character_id -- 角色id
    now_talk_data -- 口上数据
    """
    character_data: game_type.Character = cache.character_data[character_id]
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
            MakeFoodTime=character_data.behavior.make_food_time,
            Name=character_data.name,
            SceneName=scene_name,
            PlayerNickName=player_data.nick_name,
            TargetName=target_data.name,
        )
        now_draw = draw.LineFeedWaitDraw()
        now_draw.text = now_talk_text
        now_draw.width = normal_config.config_normal.text_width
        now_draw.draw()