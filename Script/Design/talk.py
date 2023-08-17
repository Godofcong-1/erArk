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
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    behavior_id = character_data.behavior.behavior_id
    now_talk_data = {}
    now_premise_data = {}
    # 检测是否是收藏模式#
    if cache.is_collection and character_id:
        player_data: game_type.Character = cache.character_data[0]
        if character_id not in player_data.collection_character:
            return
    # 检测是否与玩家处于同一位置#
    if (
            character_data.position != cache.character_data[0].position
            and character_data.behavior.move_src != cache.character_data[0].position
    ):
        must_show_talk_check(character_id)
        return
    # 第一段行为结算的口上
    if behavior_id in game_config.config_talk_data:
        for talk_id in game_config.config_talk_data[behavior_id]:
            talk_config = game_config.config_talk[talk_id]
            if talk_config.adv_id != 0:
                # print(character_data.name,target_data.name,talk_config.context,character_data.adv,target_data.adv,talk_config.adv_id)
                if character_data.adv != talk_config.adv_id:
                    if target_data.adv != talk_config.adv_id:
                        continue
            now_weight = 1
            if talk_id in game_config.config_talk_premise_data:
                now_weight = 0
                for premise in game_config.config_talk_premise_data[talk_id]:
                    # 无意识模式判定
                    if target_data.sp_flag.unconscious_h and ("is_unconscious_h" not in game_config.config_talk_premise_data[talk_id]):
                        now_weight = 0
                        break
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
    handle_talk_draw(character_id, now_talk_data)


    # 第二段行为结算的口上

    # 自己
    now_talk_data = {}
    now_premise_data = {}
    for second_behavior_id, behavior_data in character_data.second_behavior.items():
        if behavior_data != 0:
            now_talk_data = handle_talk_sub(character_id, second_behavior_id)
            # 触发后该行为值归零
            character_data.second_behavior[second_behavior_id] = 0
            handle_talk_draw(character_id, now_talk_data)

    # 交互对象
    now_talk_data = {}
    now_premise_data = {}
    if character_id == 0 and character_data.target_character_id:
        target_character_id = character_data.target_character_id
        target_character_data: game_type.Character = cache.character_data[target_character_id]
        for second_behavior_id, behavior_data in target_character_data.second_behavior.items():
            if behavior_data != 0:
                now_talk_data = handle_talk_sub(target_character_id, second_behavior_id)
                # 触发后该行为值归零
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
    now_talk = ""
    if len(now_talk_data):
        talk_weight = value_handle.get_rand_value_for_value_region(list(now_talk_data.keys()))
        now_talk_id = random.choice(list(now_talk_data[talk_weight]))
        now_talk = game_config.config_talk[now_talk_id].context
    if now_talk != "":
        now_talk_text = code_text_to_draw_text(now_talk, character_id)
        now_draw = draw.LineFeedWaitDraw()
        now_draw.text = now_talk_text
        now_draw.width = normal_config.config_normal.text_width
        now_draw.draw()


def must_show_talk_check(character_id: int):
    """
    检查是否有必须显示的二段行为文本
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    for second_behavior_id, behavior_data in character_data.second_behavior.items():
        if behavior_data != 0:
            # print(f"debug 检测到{second_behavior_id}可能需要显示")
            # 需要有必须显示
            if 998 in game_config.config_second_behavior_effect_data[second_behavior_id]:
                now_talk_data = handle_talk_sub(character_id, second_behavior_id)
                # 触发后该行为值归零
                character_data.second_behavior[second_behavior_id] = 0
                handle_talk_draw(character_id, now_talk_data)


def code_text_to_draw_text(now_talk:str , character_id: int):
    """
    将文本中的代码转化为对应的文本 \n
    Keyword arguments: \n
    now_talk -- 输入的原文本 \n
    character_id -- 角色id \n
    now_talk_text -- 转化后的文本
    """
    character_data: game_type.Character = cache.character_data[character_id]
    player_data: game_type.Character = cache.character_data[0]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]

    # 输入的原文本
    now_talk_text: str = now_talk

    # 包中食物
    all_food_name = ""
    all_food_count = 0
    for food_id in character_data.food_bag:
        food_data = character_data.food_bag[food_id]
        all_food_name += food_data.name + "、"
        if all_food_count > 1:
            all_food_name = all_food_name[:-1]
        all_food_count += 1

    # 地点
    scene_path = character_data.position
    scene_path_str = map_handle.get_map_system_path_str_for_list(scene_path)
    scene_data: game_type.Scene = cache.scene_data[scene_path_str]
    scene_name = scene_data.scene_name

    # 移动前地点
    src_scene_name,src_random_chara_name = "",""
    if len(player_data.behavior.move_src):
        src_scene_path_str = map_handle.get_map_system_path_str_for_list(player_data.behavior.move_src)
        src_scene_data: game_type.Scene = cache.scene_data[src_scene_path_str]
        src_scene_name = src_scene_data.scene_name
        for chara_id in src_scene_data.character_list:
            if chara_id:
                src_random_chara_name = cache.character_data[chara_id].name
                break

    # 移动后地点
    target_scene_name,tar_random_chara_name = "",""
    if len(character_data.behavior.move_target):
        target_scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.behavior.move_target)
        target_scene_data: game_type.Scene = cache.scene_data[target_scene_path_str]
        target_scene_name = target_scene_data.scene_name
        for chara_id in target_scene_data.character_list:
            if chara_id:
                tar_random_chara_name = cache.character_data[chara_id].name
                break

    # 地点角色
    random_chara_name = ""
    for chara_id in scene_data.character_list:
        if chara_id:
            random_chara_name = cache.character_data[chara_id].name
            break

    # 服装，来自于NPC当前穿的衣服，或行动传入的变量
    if character_id == 0 and len(target_data.cloth.cloth_wear[6]):
        TagetBraId = target_data.cloth.cloth_wear[6][0]
        TBraName = game_config.config_clothing_tem[TagetBraId].name
    else:
        TBraName = ""
    if character_id == 0 and len(target_data.cloth.cloth_wear[8]):
        TagetSkiId = target_data.cloth.cloth_wear[8][0]
        TSkiName = game_config.config_clothing_tem[TagetSkiId].name
    else:
        TSkiName = ""
    if character_id == 0 and len(target_data.cloth.cloth_wear[9]):
        TagetPanId = target_data.cloth.cloth_wear[9][0]
        TPanName = game_config.config_clothing_tem[TagetPanId].name
    elif character_id == 0 and player_data.behavior.pan_name != "":
        TPanName = player_data.behavior.pan_name
    else:
        TPanName = ""
    if character_id == 0 and len(target_data.cloth.cloth_wear[10]):
        TagetSocId = target_data.cloth.cloth_wear[10][0]
        TSocName = game_config.config_clothing_tem[TagetSocId].name
    elif character_id == 0 and player_data.behavior.socks_name != "":
        TSocName = player_data.behavior.socks_name
    else:
        TSocName = ""

    # 最后总结转化
    now_talk_text = now_talk_text.format(
        Name=character_data.name,
        NickName=character_data.nick_name,
        PlayerName=player_data.name,
        PlayerNickName=player_data.nick_name,
        TargetName=target_data.name,

        FoodName=character_data.behavior.food_name,
        MakeFoodTime=character_data.behavior.make_food_time,
        AllFoodName=all_food_name,
        BookName = character_data.behavior.book_name,

        SceneName=scene_name,
        SceneOneCharaName=random_chara_name,
        TargetSceneName=target_scene_name,
        TargetOneCharaName=tar_random_chara_name,
        SrcSceneName=src_scene_name,
        SrcOneCharaName=src_random_chara_name,

        TagetBraName=TBraName,
        TagetSkiName=TSkiName,
        TagetPanName=TPanName,
        TagetSocName=TSocName,
    )

    return now_talk_text