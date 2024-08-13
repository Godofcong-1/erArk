import random
from types import FunctionType
from Script.Core import cache_control, game_type, value_handle, get_text, constant
from Script.Design import map_handle, handle_premise
from Script.UI.Moudle import draw
from Script.Config import normal_config, game_config

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """


def handle_talk(character_id: int):
    """
    处理行为结算对话\n
    Keyword arguments:\n
    character_id -- 角色id\n
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    behavior_id = character_data.behavior.behavior_id
    # 检测是否是收藏模式#
    if cache.is_collection and character_id:
        player_data: game_type.Character = cache.character_data[0]
        if character_id not in player_data.collection_character:
            return
    # 智能跟随模式下，跟随博士性质的移动不显示移动文本
    if (
        character_id != 0 and
        character_data.sp_flag.is_follow == 1 and
        behavior_id == constant.Behavior.MOVE and
        (handle_premise.handle_player_leave_scene(0) or handle_premise.handle_target_come_scene(character_id))
    ):
        # print(f"debug 智能跟随模式下，{character_data.name}在跟随博士，不显示移动文本")
        return
    # 智能跟随模式下，博士离开时，跟随的角色不显示送别文本
    if (
        character_id == 0 and
        target_data.sp_flag.is_follow == 1 and
        behavior_id == constant.Behavior.MOVE and
        (handle_premise.handle_player_leave_scene(0) or handle_premise.handle_target_come_scene(0))
    ):
        # print(f"debug 智能跟随模式下，博士离开时，跟随的角色{target_data.name}不显示送别文本")
        return
    # 和玩家不在同一位置的NPC不显示文本
    if character_id != 0 and character_data.position != cache.character_data[0].position:
        # print(f"debug {character_data.name}和玩家不在同一位置，不显示文本")
        return
    # 第一段行为结算的口上
    now_talk_data = handle_talk_sub(character_id, behavior_id)
    handle_talk_draw(character_id, now_talk_data)

    # 玩家移动到NPC位置时，NPC的打招呼文本
    if character_id == 0 and behavior_id == constant.Behavior.MOVE:
        scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
        for chara_id in cache.scene_data[scene_path_str].character_list:
            if chara_id > 0:
                now_talk_data = handle_talk_sub(chara_id, behavior_id)
                handle_talk_draw(chara_id, now_talk_data)


def handle_second_talk(character_id: int):
    """
    处理二段行为结算对话\n
    Keyword arguments:\n
    character_id -- 角色id\n
    """
    character_data: game_type.Character = cache.character_data[character_id]
    # 检测是否是收藏模式#
    if cache.is_collection and character_id:
        player_data: game_type.Character = cache.character_data[0]
        if character_id not in player_data.collection_character:
            return

    # 自己
    for second_behavior_id, behavior_data in character_data.second_behavior.items():
        if behavior_data != 0:
            now_talk_data = handle_talk_sub(character_id, second_behavior_id)
            handle_talk_draw(character_id, now_talk_data, second_behavior_id)

    # 交互对象
    if character_id == 0 and character_data.target_character_id:
        target_character_id = character_data.target_character_id
        target_character_data: game_type.Character = cache.character_data[target_character_id]
        for second_behavior_id, behavior_data in target_character_data.second_behavior.items():
            if behavior_data != 0:
                now_talk_data = handle_talk_sub(target_character_id, second_behavior_id)
                handle_talk_draw(target_character_id, now_talk_data, second_behavior_id)


def handle_talk_sub(character_id: int, behavior_id: int, must_show = False):
    """
    处理行为结算对话的内置循环部分
    Keyword arguments:
    character_id -- 角色id
    behavior_id -- 行为id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    now_talk_data = {}
    now_premise_data = {}
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
                    # 是否必须显示
                    if not must_show:
                        # 无意识模式判定
                        if target_data.sp_flag.unconscious_h != 0 and target_data.sp_flag.unconscious_h <= 5:
                            unconscious_h_pass_flag = False
                            # 需要前提里有无意识的判定，否则不显示
                            for premise in game_config.config_talk_premise_data[talk_id]:
                                if "unconscious" in premise:
                                    unconscious_h_pass_flag = True
                                    break
                            if not unconscious_h_pass_flag:
                                now_weight = 0
                                break
                    # 已录入前提的判定
                    if premise in now_premise_data:
                        if not now_premise_data[premise]:
                            now_weight = 0
                            break
                        else:
                            now_weight += now_premise_data[premise]
                            # 如果premise的前5个字符是"high_"，则将权重加上对应值，否则权重为1
                            if premise[:5] == "high_":
                                now_weight += now_premise_data[premise]
                            else:
                                now_weight += 1
                    else:
                        # 综合数值前提判定
                        if "CVP" in premise:
                            premise_all_value_list = premise.split("_")[1:]
                            now_add_weight = handle_premise.handle_comprehensive_value_premise(character_id, premise_all_value_list)
                            now_premise_data[premise] = now_add_weight
                        # 其他正常口上判定
                        else:
                            now_add_weight = constant.handle_premise_data[premise](character_id)
                            now_premise_data[premise] = now_add_weight
                        if now_add_weight:
                            # 如果premise的前5个字符是"high_"，则将权重加上对应值，否则权重为1
                            if premise[:5] == "high_":
                                now_add_weight = now_add_weight
                            else:
                                now_add_weight = 1
                            now_weight += now_add_weight
                        else:
                            now_weight = 0
                            break
            if now_weight:
                # 如果该句文本是角色口上，则权重乘以三
                if talk_config.adv_id != 0:
                    now_weight *= 3
                now_talk_data.setdefault(now_weight, set())
                now_talk_data[now_weight].add(talk_id)
    return now_talk_data


def handle_talk_draw(character_id: int, now_talk_data: dict, second_behavior_id = 0):
    """
    处理行为结算对话的输出
    Keyword arguments:
    character_id -- 角色id
    now_talk_data -- 口上数据
    second_behavior_id -- 二段行为id，默认为0
    """
    now_talk = ""
    if len(now_talk_data):
        talk_weight = value_handle.get_rand_value_for_value_region(list(now_talk_data.keys()))
        now_talk_id = random.choice(list(now_talk_data[talk_weight]))
        now_talk = game_config.config_talk[now_talk_id].context
        unusual_talk_flag = game_config.config_talk[now_talk_id].adv_id
    # 二段结算前会单独绘制一个信息文本
    if second_behavior_id > 0:
        second_behavior_info_text(character_id, second_behavior_id)
    if now_talk != "":
        now_talk_text = code_text_to_draw_text(now_talk, character_id)
        now_draw = draw.LineFeedWaitDraw()
        now_draw.text = now_talk_text
        now_draw.width = normal_config.config_normal.text_width
        if unusual_talk_flag:
            # 口上文本的，角色文本颜色
            character_data: game_type.Character = cache.character_data[character_id]
            target_character_data: game_type.Character = cache.character_data[character_data.target_character_id]
            text_color = character_data.text_color
            tar_text_color = target_character_data.text_color
            if text_color:
                now_draw.style = character_data.name
            elif tar_text_color:
                now_draw.style = target_character_data.name
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
                # 进行绘制
                now_talk_data = handle_talk_sub(character_id, second_behavior_id, True)
                handle_talk_draw(character_id, now_talk_data, second_behavior_id)
                # 遍历该二段行为的所有结算效果，挨个触发，但因为不在结算阶段，所以不会显示具体的结算数据
                change_data = game_type.CharacterStatusChange
                for effect_id in game_config.config_second_behavior_effect_data[second_behavior_id]:
                    constant.settle_second_behavior_effect_data[effect_id](character_id, change_data)
                # 触发后该行为值归零
                character_data.second_behavior[second_behavior_id] = 0


def second_behavior_info_text(character_id: int, second_behavior_id: int):
    """
    二段行为结算的信息文本
    Keyword arguments:
    character_id -- 角色id
    second_behavior_id -- 二段行为id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    chara_name = character_data.name
    info_draw = draw.WaitDraw()
    info_text = ""
    info_draw.style = "standard"
    # 部位绝顶
    if 1000 <= second_behavior_id < 1030:
        # 玩家
        if character_id == 0:
            orgasm_degree_list = [_("射精"), _("大量射精"), _("超大量射精")]
            orgasm_degree = _(orgasm_degree_list[second_behavior_id % 3 - 1])
            info_text = "\n{0}{1}\n".format(chara_name, orgasm_degree)
            info_draw.style = "semen"
        # NPC
        else:
            # 定义映射字典和列表
            orgasm_name_map = {
                range(1000, 1003): "N",
                range(1003, 1006): "B",
                range(1006, 1009): "C",
                range(1009, 1012): "P",
                range(1012, 1015): "V",
                range(1015, 1018): "A",
                range(1018, 1021): "U",
                range(1021, 1024): "W"
            }
            orgasm_degree_list = [_("小"), _("普"), _("强")]
            # 查找对应的部位名与绝顶程度名
            orgasm_name = next((name for key, name in orgasm_name_map.items() if second_behavior_id in key), None)
            orgasm_degree = _(orgasm_degree_list[second_behavior_id % 3 - 1])
            # 最后文本
            info_text = _("\n{0}{1}{2}绝顶\n").format(chara_name, orgasm_name, orgasm_degree)
    # 饮精绝顶
    elif second_behavior_id == 1027:
        info_text = _("\n{0}饮精绝顶\n").format(chara_name, count_name)
    # 多重绝顶
    elif 1081 <= second_behavior_id < 1090:
        count_name_list = [_("双重"), _("三重"), _("四重"), _("五重"), _("六重"), _("七重"), _("八重"), _("九重"), _("十重")]
        count_name = count_name_list[second_behavior_id - 1081]
        info_text = _("\n{0}{1}绝顶\n").format(chara_name, count_name)
    # 一般刻印
    elif 1030 <= second_behavior_id < 1050:
        # 定义映射字典和列表
        mark_name_map = {
            range(1030, 1033): "快乐",
            range(1033, 1036): "屈服",
            range(1036, 1039): "苦痛",
            range(1039, 1042): "时姦",
            range(1042, 1045): "恐怖",
            range(1045, 1048): "反发",
        }
        mark_name = next((name for key, name in mark_name_map.items() if second_behavior_id in key), None)
        mark_degree = (second_behavior_id % 3)
        if mark_degree == 0:
            mark_degree = 3
        info_text = _("\n{0}获得了{1}刻印{2}\n").format(chara_name, mark_name, mark_degree)
        # 如果是恐怖和反发刻印，则将绘制变成猩红
        if second_behavior_id in range(1042, 1048):
            info_draw.style = "crimson"
    # B绝顶喷乳
    elif second_behavior_id == 1071:
        info_text = _("\n{0}因B绝顶而被迫喷乳\n").format(chara_name)
        info_draw.style = "semen"
    # U绝顶漏尿
    elif second_behavior_id == 1072:
        info_text = _("\n{0}因U绝顶而被迫漏尿\n").format(chara_name)
        info_draw.style = "khaki"

    # 最后补一个换行
    if info_text != "":
        info_text += "\n"
        if info_draw.style == "standard":
            info_draw.style = "gold_enrod"
        info_draw.text = info_text
        info_draw.draw()

    return info_text


def code_text_to_draw_text(now_talk:str, character_id: int):
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
        all_food_count += 1
    if all_food_count > 1:
        all_food_name = all_food_name[:-1]

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
        MilkMl = character_data.behavior.milk_ml,
        HInterruptCharaName = character_data.behavior.h_interrupt_chara_name,

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