import random
from types import FunctionType
from Script.Core import cache_control, game_type, value_handle, get_text, constant
from Script.Design import map_handle, handle_premise, handle_premise_place
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
    # 和玩家不在同一位置的NPC不显示文本
    if character_id != 0 and character_data.position != cache.character_data[0].position:
        # print(f"debug {character_data.name}和玩家不在同一位置，不显示文本")
        return
    # 检测是否是收藏模式#
    if cache.is_collection and character_id:
        player_data: game_type.Character = cache.character_data[0]
        if character_id not in player_data.collection_character:
            return
    # 智能跟随模式下，博士离开时，跟随的角色不显示送别文本
    if (
        character_id == 0 and
        target_data.sp_flag.is_follow == 1 and
        behavior_id == constant.Behavior.MOVE and
        handle_premise_place.handle_move_to_same_target_with_pl(character_data.target_character_id)
    ):
        # print(f"debug 智能跟随模式下，博士离开时，跟随的角色{target_data.name}不显示送别文本")
        return
    # 避免多次触发NPC的移动口上
    if character_id != 0 and behavior_id == constant.Behavior.MOVE:
        # 跟随博士的移动不触发
        if character_data.sp_flag.is_follow == 1 and handle_premise_place.handle_move_to_same_target_with_pl(character_id):
            # print(f"debug 智能跟随模式下，{character_data.name}在跟随博士，不显示移动文本")
            return
        # 当前小时内已触发过的不触发
        if character_data.action_info.move_talk_time.hour == cache.game_time.hour and character_data.action_info.move_talk_time.year != 1:
            # print(f"debug {character_data.name}在当前小时内已触发过一次移动文本")
            return
    # 第一段行为结算的口上
    now_talk_data = handle_talk_sub(character_id, behavior_id)
    handle_talk_draw(character_id, now_talk_data)

    # 玩家移动到NPC位置时，NPC的打招呼文本
    if character_id == 0 and behavior_id == constant.Behavior.MOVE:
        scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
        for chara_id in cache.scene_data[scene_path_str].character_list:
            # 要求对象是NPC，且没有跟随玩家
            if chara_id > 0 and handle_premise.handle_not_follow(chara_id):
                now_talk_data = handle_talk_sub(chara_id, behavior_id)
                handle_talk_draw(chara_id, now_talk_data)


def handle_second_talk(character_id: int, behavior_id: int = 0):
    """
    处理二段行为结算对话\n
    Keyword arguments:\n
    character_id -- 角色id\n
    behavior_id -- 行为id，默认为0\n
    """
    character_data: game_type.Character = cache.character_data[character_id]
    # 检测是否是收藏模式#
    if cache.is_collection and character_id:
        player_data: game_type.Character = cache.character_data[0]
        if character_id not in player_data.collection_character:
            return

    # 自己
    if behavior_id == 0:
        for second_behavior_id, behavior_data in character_data.second_behavior.items():
            if behavior_data != 0:
                now_talk_data = handle_talk_sub(character_id, second_behavior_id)
                handle_talk_draw(character_id, now_talk_data, second_behavior_id)
    else:
        now_talk_data = handle_talk_sub(character_id, behavior_id)
        handle_talk_draw(character_id, now_talk_data, behavior_id)

    # 交互对象
    # if character_id == 0 and character_data.target_character_id:
    #     target_character_id = character_data.target_character_id
    #     target_character_data: game_type.Character = cache.character_data[target_character_id]
    #     for second_behavior_id, behavior_data in target_character_data.second_behavior.items():
    #         if behavior_data != 0:
    #             now_talk_data = handle_talk_sub(target_character_id, second_behavior_id)
    #             handle_talk_draw(target_character_id, now_talk_data, second_behavior_id)


def handle_talk_sub(character_id: int, behavior_id: int, unconscious_pass_flag = False):
    """
    处理行为结算对话的内置循环部分
    Keyword arguments:
    character_id -- 角色id
    behavior_id -- 行为id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    tem_talk_list = [] # 临时口上列表
    if behavior_id in game_config.config_talk_data_by_chara_adv:
        # 获取通用口上
        if 0 in game_config.config_talk_data_by_chara_adv[behavior_id]:
            tem_talk_list += game_config.config_talk_data_by_chara_adv[behavior_id][0]
        # 获取触发者id的口上
        if character_data.adv != 0 and character_data.adv in game_config.config_talk_data_by_chara_adv[behavior_id]:
            tem_talk_list += game_config.config_talk_data_by_chara_adv[behavior_id][character_data.adv]
        # 获取交互目标的口上
        if target_data.adv != 0 and target_data.adv in game_config.config_talk_data_by_chara_adv[behavior_id]:
            tem_talk_list += game_config.config_talk_data_by_chara_adv[behavior_id][target_data.adv]
    now_talk_data = {} # 正式口上数据
    # 遍历口上列表
    for talk_id in tem_talk_list:
        talk_config = game_config.config_talk[talk_id]
        # 角色专属口上则需要判定是否为该角色
        if talk_config.adv_id != 0:
            # print(character_data.name,target_data.name,talk_config.context,character_data.adv,target_data.adv,talk_config.adv_id)
            if character_data.adv != talk_config.adv_id and target_data.adv != talk_config.adv_id:
                continue
        # 系统设置中的是否使用通用文本
        if cache.system_setting[8] == 0 and talk_config.adv_id == 0:
            continue
        # 计算前提字典的总权重
        premise_dict = game_config.config_talk_premise_data[talk_id]
        now_weight = handle_premise.get_weight_from_premise_dict(premise_dict, character_id, weight_all_to_1_flag = True, unconscious_pass_flag = unconscious_pass_flag)
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
    from Script.UI.Panel import chat_ai_setting

    now_talk = ""
    character_data: game_type.Character = cache.character_data[character_id]
    if len(now_talk_data):
        talk_weight = value_handle.get_rand_value_for_value_region(list(now_talk_data.keys()))
        now_talk_id = random.choice(list(now_talk_data[talk_weight]))
        now_talk = game_config.config_talk[now_talk_id].context
        now_behavior_id = game_config.config_talk[now_talk_id].behavior_id
        unusual_talk_flag = game_config.config_talk[now_talk_id].adv_id
    # 二段结算前会单独绘制一个信息文本
    if second_behavior_id > 0:
        second_behavior_info_text(character_id, second_behavior_id)
    if now_talk != "":
        # 特殊符号检测
        tem_text, special_code = special_code_judge(now_talk)
        now_draw = draw.LineFeedWaitDraw()
        # 跳过每次的等待
        if special_code[0]:
            now_draw = draw.NormalDraw()
        now_talk_text = code_text_to_draw_text(now_talk, character_id)
        now_draw.text = now_talk_text
        now_draw.width = normal_config.config_normal.text_width
        # 角色口上
        if unusual_talk_flag:
            # 口上文本的，角色文本颜色
            target_character_data: game_type.Character = cache.character_data[character_data.target_character_id]
            text_color = character_data.text_color
            tar_text_color = target_character_data.text_color
            if text_color:
                now_draw.style = character_data.name
            elif tar_text_color:
                now_draw.style = target_character_data.name
            # 记录当前小时内已触发过一次的移动文本
            if character_data.behavior.behavior_id == constant.Behavior.MOVE:
                character_data.action_info.move_talk_time = cache.game_time
            # 翻译口上
            if normal_config.config_normal.language != "zh_CN" and cache.ai_setting.ai_chat_translator_setting == 2:
                now_talk_text = chat_ai_setting.judge_use_text_ai(character_id, now_behavior_id, now_talk_text, translator=True)
                now_draw.text = now_talk_text
        # 地文
        else:
            cache.ai_setting.ai_chat_setting.setdefault(1, 0)
            # 地文翻译
            if normal_config.config_normal.language != "zh_CN" and cache.ai_setting.ai_chat_translator_setting >= 1:
                now_talk_text = chat_ai_setting.judge_use_text_ai(character_id, now_behavior_id, now_talk_text, translator=True)
                now_draw.text = now_talk_text
            # 如果启用了文本生成ai
            elif cache.ai_setting.ai_chat_setting[1]:
                now_draw = draw.LineFeedWaitDraw()
                now_talk_text = chat_ai_setting.judge_use_text_ai(character_id, now_behavior_id, now_talk_text)
                now_draw.width = normal_config.config_normal.text_width
                now_draw.text = now_talk_text
        now_draw.draw()
        # 在最后进行一次换行和等待
        if special_code[0]:
            wait_draw = draw.LineFeedWaitDraw()
            wait_draw.text = " \n"
            wait_draw.draw()


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
                change_data = game_type.CharacterStatusChange()
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
    if 1000 <= second_behavior_id < 1030 or 1090 <= second_behavior_id < 1100:
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
                (1000, 1001, 1002, 1090): "N",
                (1003, 1004, 1005, 1091): "B",
                (1006, 1007, 1008, 1092): "C",
                (1009, 1010, 1011, 1093): "P",
                (1012, 1013, 1014, 1094): "V",
                (1015, 1016, 1017, 1095): "A",
                (1018, 1019, 1020, 1096): "U",
                (1021, 1022, 1023, 1097): "W",
                (1026,): "额外",
                (1027,): "饮精",
            }
            orgasm_degree_list = [_("小"), _("普"), _("强")]
            # 查找对应的部位名与绝顶程度名
            orgasm_name = next((name for key, name in orgasm_name_map.items() if second_behavior_id in key), None)
            orgasm_degree = _(orgasm_degree_list[second_behavior_id % 3 - 1])
            if second_behavior_id >= 1090:
                orgasm_degree = _("超强")
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


def special_code_judge(now_talk: str):
    """
    将文本中的代码转化为对应的文本 \n
    Keyword arguments: \n
    now_talk -- 输入的原文本 \n
    Return arguments:
    now_talk_text -- 去掉特殊符号后的文本
    special_code -- 特殊符号列表，[0非等待文本]
    """

    special_code = [False]

    # 不停顿的特殊换行符
    if "<jump>" in now_talk:
        now_talk = now_talk.replace("<jump>", "")
        now_talk = now_talk.replace("\\n", "\n")
        special_code[0] = True

    return now_talk, special_code



def code_text_to_draw_text(now_talk: str, character_id: int):
    """
    将文本中的代码转化为对应的文本 \n
    Keyword arguments: \n
    now_talk -- 输入的原文本 \n
    character_id -- 角色id \n
    Return arguments:
    now_talk_text -- 转化后的文本
    """
    character_data: game_type.Character = cache.character_data[character_id]
    player_data: game_type.Character = cache.character_data[0]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]

    # 输入的原文本
    now_talk_text, special_code = special_code_judge(now_talk)

    # 专属称呼处理
    nick_name = character_data.nick_name
    if nick_name == "":
        nick_name = character_data.name
    nick_name_to_pl = character_data.nick_name_to_pl
    if nick_name_to_pl == "":
        nick_name_to_pl = player_data.nick_name
    pl_nick_name = ""
    if character_id != 0:
        pl_nick_name = character_data.nick_name_to_pl
    elif character_data.target_character_id != 0:
        pl_nick_name = target_data.nick_name_to_pl
    if pl_nick_name == "":
        pl_nick_name = player_data.nick_name
    target_nick_name = target_data.nick_name
    if target_nick_name == "":
        target_nick_name = target_data.name
    target_nick_name_to_pl = target_data.nick_name_to_pl
    if target_nick_name_to_pl == "":
        target_nick_name_to_pl = player_data.nick_name

    # 包中食物
    all_food_name = ""
    all_food_count = 0
    for food_id in character_data.food_bag:
        food_data = character_data.food_bag[food_id]
        all_food_name += food_data.name + "、"
        all_food_count += 1
    if all_food_count > 1:
        all_food_name = all_food_name[:-1]

    # 桌游
    board_game_name = ""
    pl_board_game_type = player_data.behavior.board_game_type if hasattr(player_data.behavior, 'board_game_type') else 0
    if character_id == 0 and pl_board_game_type != 0:
        board_game_name = game_config.config_board_game[pl_board_game_type].name

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
    target_bra_name = ""
    if character_id == 0 and len(target_data.cloth.cloth_wear[6]):
        for BraId in target_data.cloth.cloth_wear[6]:
            target_bra_name += game_config.config_clothing_tem[BraId].name
    if target_bra_name == "":
        target_bra_name = _("没有穿胸罩的乳房")
    target_ski_name = ""
    if character_id == 0 and len(target_data.cloth.cloth_wear[8]):
        for SkiId in target_data.cloth.cloth_wear[8]:
            target_ski_name += game_config.config_clothing_tem[SkiId].name
    if target_ski_name == "":
        target_ski_name = _("没有穿裙子的胯部")
    target_pan_name = ""
    if character_id == 0 and len(target_data.cloth.cloth_wear[9]):
        for PanId in target_data.cloth.cloth_wear[9]:
            target_pan_name += game_config.config_clothing_tem[PanId].name
    elif player_data.behavior.pan_name != "":
        target_pan_name = player_data.behavior.pan_name
    if target_pan_name == "":
        target_pan_name = _("没有穿内裤的阴部")
    target_soc_name = ""
    if character_id == 0 and len(target_data.cloth.cloth_wear[10]):
        for SocId in target_data.cloth.cloth_wear[10]:
            target_soc_name += game_config.config_clothing_tem[SocId].name
    elif player_data.behavior.socks_name != "":
        target_soc_name = player_data.behavior.socks_name
    if target_soc_name == "":
        target_soc_name = _("没有穿袜子的双腿")
    pan_name = ""
    if character_id != 0 and len(character_data.cloth.cloth_wear[9]):
        for PanId in character_data.cloth.cloth_wear[9]:
            pan_name += game_config.config_clothing_tem[PanId].name
    elif player_data.behavior.pan_name != "":
        pan_name = player_data.behavior.pan_name
    if pan_name == "":
        pan_name = _("没有穿内裤的阴部")
    socks_name = ""
    if character_id != 0 and len(character_data.cloth.cloth_wear[10]):
        for SocId in character_data.cloth.cloth_wear[10]:
            socks_name += game_config.config_clothing_tem[SocId].name
    elif player_data.behavior.socks_name != "":
        socks_name = player_data.behavior.socks_name
    if socks_name == "":
        socks_name = _("没有穿袜子的双腿")

    # 最后总结转化
    now_talk_text = now_talk_text.format(
        Name=character_data.name,
        NickName=nick_name,
        NickNameToPl=nick_name_to_pl,
        PlayerName=player_data.name,
        PlayerNickName=pl_nick_name,
        TargetName=target_data.name,
        TargetNickName=target_nick_name,
        TargetNickNameToPl=target_nick_name_to_pl,

        FoodName=character_data.behavior.food_name,
        MakeFoodTime=character_data.behavior.make_food_time,
        AllFoodName=all_food_name,
        BookName = character_data.behavior.book_name,
        BoardGameName = board_game_name,
        MilkMl = character_data.behavior.milk_ml,
        HInterruptCharaName = character_data.behavior.h_interrupt_chara_name,

        SceneName=scene_name,
        SceneOneCharaName=random_chara_name,
        TargetSceneName=target_scene_name,
        TargetOneCharaName=tar_random_chara_name,
        SrcSceneName=src_scene_name,
        SrcOneCharaName=src_random_chara_name,

        TagetBraName=target_bra_name,
        TagetSkiName=target_ski_name,
        TagetPanName=target_pan_name,
        TagetSocName=target_soc_name,
        PanName=pan_name,
        SocName=socks_name,
    )

    return now_talk_text