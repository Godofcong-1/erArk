import random
import re
from types import FunctionType

from Script.Core import cache_control, game_type, value_handle, get_text, constant, rich_text
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
        handle_premise.handle_move_to_same_target_with_pl(character_data.target_character_id)
    ):
        # print(f"debug 智能跟随模式下，博士离开时，跟随的角色{target_data.name}不显示送别文本")
        return
    # 第一段行为结算的口上
    now_talk_data = handle_talk_sub(character_id, behavior_id)
    talk_text, now_talk_id = choice_talk_from_talk_data(now_talk_data, behavior_id)
    handle_talk_draw(character_id, talk_text, now_talk_id)

    # 玩家移动到NPC位置时，NPC的打招呼文本
    if character_id == 0 and behavior_id == constant.Behavior.MOVE:
        scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
        for chara_id in cache.scene_data[scene_path_str].character_list:
            # 要求对象是NPC，且没有跟随玩家
            if chara_id > 0 and handle_premise.handle_not_follow(chara_id):
                now_talk_data = handle_talk_sub(chara_id, behavior_id)
                talk_text, now_talk_id = choice_talk_from_talk_data(now_talk_data, behavior_id)
                handle_talk_draw(chara_id, talk_text, now_talk_id)


def handle_second_talk(character_id: int, behavior_id: str = "share_blankly"):
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
    if behavior_id == "share_blankly":
        for second_behavior_id, behavior_data in character_data.second_behavior.items():
            if behavior_data != 0:
                now_talk_data = handle_talk_sub(character_id, second_behavior_id)
                talk_text, now_talk_id = choice_talk_from_talk_data(now_talk_data, second_behavior_id)
                handle_talk_draw(character_id, talk_text, now_talk_id, second_behavior_id)
    else:
        now_talk_data = handle_talk_sub(character_id, behavior_id)
        talk_text, now_talk_id = choice_talk_from_talk_data(now_talk_data, behavior_id)
        handle_talk_draw(character_id, talk_text, now_talk_id, behavior_id)

    # 交互对象
    # if character_id == 0 and character_data.target_character_id:
    #     target_character_id = character_data.target_character_id
    #     target_character_data: game_type.Character = cache.character_data[target_character_id]
    #     for second_behavior_id, behavior_data in target_character_data.second_behavior.items():
    #         if behavior_data != 0:
    #             now_talk_data = handle_talk_sub(target_character_id, second_behavior_id)
    #             handle_talk_draw(target_character_id, now_talk_data, second_behavior_id)


def handle_talk_sub(character_id: int, behavior_id: str, unconscious_pass_flag = False):
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
            tem_talk_list += game_config.config_talk_data_by_chara_adv[behavior_id][0][1]
        # 获取触发者的口上版本
        character_version = 0
        if character_data.adv != 0:
            character_version = cache.all_system_setting.character_text_version[character_data.adv]
        # 获取触发者id的口上，需要自己adv不为0，有自己adv的口上，自己口上版本不是无
        if (
            character_data.adv != 0 and
            character_data.adv in game_config.config_talk_data_by_chara_adv[behavior_id] and
            character_version > 0 and
            character_version in game_config.config_talk_data_by_chara_adv[behavior_id][character_data.adv]
            ):
            tem_talk_list += game_config.config_talk_data_by_chara_adv[behavior_id][character_data.adv][character_version]
        # 获取交互目标的口上版本
        target_version = 0
        if target_data.adv != 0:
            target_version = cache.all_system_setting.character_text_version[target_data.adv]
        # 获取交互目标的口上
        if (
            target_data.adv != 0 and
            target_data.adv in game_config.config_talk_data_by_chara_adv[behavior_id] and
            target_version > 0 and
            target_version in game_config.config_talk_data_by_chara_adv[behavior_id][target_data.adv]
            ):
            tem_talk_list += game_config.config_talk_data_by_chara_adv[behavior_id][target_data.adv][target_version]
    # 正式口上数据
    now_talk_data = {}
    # 已计算过的前提字典
    calculated_premise_dict = {}
    # 遍历口上列表
    for talk_id in tem_talk_list:
        talk_config = game_config.config_talk[talk_id]
        # 角色专属口上则需要判定是否为该角色
        if talk_config.adv_id != 0:
            # print(character_data.name,target_data.name,talk_config.context,character_data.adv,target_data.adv,talk_config.adv_id)
            if character_data.adv != talk_config.adv_id and target_data.adv != talk_config.adv_id:
                continue
        # 系统设置中的是否使用通用文本
        if cache.all_system_setting.draw_setting[2] == 0 and talk_config.adv_id == 0:
            continue
        # 计算前提字典的总权重
        talk_premise_set = game_config.config_talk_premise_data[talk_id]
        now_weight, calculated_premise_dict = handle_premise.get_weight_from_premise_dict(talk_premise_set, character_id, calculated_premise_dict, weight_all_to_1_flag = True, unconscious_pass_flag = unconscious_pass_flag)
        if now_weight:
            # 如果该句文本是角色口上，则权重乘以角色专属文本权重倍数，默认10倍
            if talk_config.adv_id != 0:
                now_weight *= cache.all_system_setting.draw_setting.get(14, 10)
            # 计算特殊前提权重加成
            new_weight = handle_special_talk_weight(character_id, talk_premise_set)
            now_weight *= new_weight
            # 加入到正式口上数据中
            now_talk_data.setdefault(now_weight, set())
            now_talk_data[now_weight].add(talk_id)
    return now_talk_data

def handle_special_talk_weight(character_id: int, talk_premise_set: set) -> int:
    """
    处理特殊前提的权重加成
    Keyword arguments:
    character_id -- 角色id
    talk_premise_set -- 口上前提集合
    Return arguments:
    new_weight -- 额外权重加成倍率
    """
    new_weight = 1
    judge_premise_and_weight_list = []
    from Script.Core import constant_promise
    # 时停解放
    if handle_premise.handle_self_time_stop_orgasm_relase(character_id) or handle_premise.handle_target_time_stop_orgasm_relase(character_id):
        time_stop_orgasm_relase_premise = [constant_promise.Premise.SELF_TIME_STOP_ORGASM_RELAESE, constant_promise.Premise.TARGET_TIME_STOP_ORGASM_RELAESE]
        judge_premise_and_weight_list.append(time_stop_orgasm_relase_premise)
    # 女儿
    if handle_premise.handle_self_is_player_daughter(character_id) or handle_premise.handle_target_is_player_daughter(character_id):
        daughter_premise = [constant_promise.Premise.SELF_IS_PLAYER_DAUGHTER, constant_promise.Premise.SELF_NOT_PLAYER_DAUGHTER]
        judge_premise_and_weight_list.append(daughter_premise)
    # 在爱情旅馆H
    if handle_premise.handle_h_in_love_hotel(character_id):
        h_in_love_hotel_premise = [constant_promise.Premise.H_IN_LOVE_HOTEL]
        judge_premise_and_weight_list.append(h_in_love_hotel_premise)
    # 在浴室中H
    if handle_premise.handle_h_in_bathroom(character_id):
        h_in_bathroom_premise = [constant_promise.Premise.H_IN_BATHROOM]
        judge_premise_and_weight_list.append(h_in_bathroom_premise)
    # 逆推
    if handle_premise.handle_npc_active_h(character_id) or handle_premise.handle_t_npc_active_h(character_id):
        reverse_premise = [constant_promise.Premise.NPC_ACTIVE_H, constant_promise.Premise.T_NPC_ACTIVE_H]
        judge_premise_and_weight_list.append(reverse_premise)
    # 隐奸
    if handle_premise.handle_hidden_sex_mode_ge_1(character_id) or handle_premise.handle_t_hidden_sex_mode_ge_1(character_id):
        hidden_sex_premise = [constant_promise.Premise.HIDDEN_SEX_MODE_GE_1, constant_promise.Premise.HIDDEN_SEX_MODE_1, constant_promise.Premise.HIDDEN_SEX_MODE_2, constant_promise.Premise.HIDDEN_SEX_MODE_3, constant_promise.Premise.HIDDEN_SEX_MODE_4, constant_promise.Premise.HIDDEN_SEX_MODE_1_OR_2, constant_promise.Premise.HIDDEN_SEX_MODE_3_OR_4, constant_promise.Premise.HIDDEN_SEX_MODE_1_OR_3, constant_promise.Premise.HIDDEN_SEX_MODE_2_OR_4, constant_promise.Premise.TARGET_HIDDEN_SEX_MODE_GE_1, constant_promise.Premise.TARGET_HIDDEN_SEX_MODE_1, constant_promise.Premise.TARGET_HIDDEN_SEX_MODE_2, constant_promise.Premise.TARGET_HIDDEN_SEX_MODE_3, constant_promise.Premise.TARGET_HIDDEN_SEX_MODE_4, constant_promise.Premise.TARGET_HIDDEN_SEX_MODE_1_OR_2, constant_promise.Premise.TARGET_HIDDEN_SEX_MODE_3_OR_4, constant_promise.Premise.TARGET_HIDDEN_SEX_MODE_1_OR_3, constant_promise.Premise.TARGET_HIDDEN_SEX_MODE_2_OR_4]
        judge_premise_and_weight_list.append(hidden_sex_premise)
    # 露出
    if handle_premise.handle_exhibitionism_sex_mode_ge_1(character_id):
        exhibitionism_sex_premise = [constant_promise.Premise.EXHIBITIONISM_SEX_MODE_GE_1, constant_promise.Premise.EXHIBITIONISM_SEX_MODE_1, constant_promise.Premise.EXHIBITIONISM_SEX_MODE_2, constant_promise.Premise.EXHIBITIONISM_SEX_MODE_3, constant_promise.Premise.EXHIBITIONISM_SEX_MODE_4, constant_promise.Premise.TARGET_EXHIBITIONISM_SEX_MODE_GE_1, constant_promise.Premise.TARGET_EXHIBITIONISM_SEX_MODE_1, constant_promise.Premise.TARGET_EXHIBITIONISM_SEX_MODE_2, constant_promise.Premise.TARGET_EXHIBITIONISM_SEX_MODE_3, constant_promise.Premise.TARGET_EXHIBITIONISM_SEX_MODE_4]
        judge_premise_and_weight_list.append(exhibitionism_sex_premise)
    # 群交
    if handle_premise.handle_group_sex_mode_on(character_id):
        group_sex_premise = [constant_promise.Premise.GROUP_SEX_MODE_ON]
        judge_premise_and_weight_list.append(group_sex_premise)
    # 监禁
    if handle_premise.handle_imprisonment_1(character_id) or handle_premise.handle_t_imprisonment_1(character_id):
        imprisonment_premise = [constant_promise.Premise.IMPRISONMENT_1, constant_promise.Premise.T_IMPRISONMENT_1]
        judge_premise_and_weight_list.append(imprisonment_premise)
    # 遍历所有需要判断的前提和对应权重
    for premise_list in judge_premise_and_weight_list:
        for premise in premise_list:
            # 如果口上前提中包含该前提，则进行权重加成
            if premise in talk_premise_set:
                new_weight *= cache.all_system_setting.draw_setting.get(15, 5)
                break
    return new_weight

def choice_talk_from_talk_data(now_talk_data: dict, behavior_id = "share_blankly"):
    """
    处理行为结算对话的输出
    Keyword arguments:
    now_talk_data -- 口上数据
    behavior_id -- 行为id，默认为"share_blankly"
    Return arguments:
    talk_text -- 口上文本
    """
    talk_text = ""
    now_talk_id = ""
    if len(now_talk_data):
        talk_weight = value_handle.get_rand_value_for_value_region(list(now_talk_data.keys()))
        now_talk_id = random.choice(list(now_talk_data[talk_weight]))
        talk_text = game_config.config_talk[now_talk_id].context
        unusual_talk_flag = game_config.config_talk[now_talk_id].adv_id
        # 如果不是特殊口上或是权重低于100的特殊口上，且行为id在通用口上列表中，则按照设置的几率使用纸娃娃地文
        if (
            (not unusual_talk_flag or talk_weight < 100) and
            behavior_id in game_config.config_talk_common_cid_list_by_type and
            cache.all_system_setting.draw_setting[2] == 1
            ):
            use_common_talk_rate = cache.all_system_setting.draw_setting[13]
            if random.randint(1, 100) <= use_common_talk_rate * 10:
                talk_text = '{' + behavior_id + '}'
                now_talk_id = ""
    else:
        # 在没有口上的情况下，如果行为id在通用口上列表中，则调用纸娃娃地文
        if behavior_id in game_config.config_talk_common_cid_list_by_type and cache.all_system_setting.draw_setting[2] == 1:
            talk_text = '{' + behavior_id + '}'
    return talk_text, now_talk_id

def handle_talk_draw(character_id: int, talk_text: str, now_talk_id: str, second_behavior_id = ""):
    """
    处理行为结算对话的输出
    Keyword arguments:
    character_id -- 角色id
    talk_text -- 口上文本
    now_talk_id -- 当前口上id
    second_behavior_id -- 二段行为id，默认为""
    """
    from Script.Design import handle_chat_ai

    character_data: game_type.Character = cache.character_data[character_id]
    # 二段结算前会单独绘制一个信息文本
    if second_behavior_id != "":
        second_behavior_info_text(character_id, second_behavior_id)
    if talk_text != "":
        # 更新行为id和特殊口上标志
        now_behavior_id = ""
        unusual_talk_flag = 0
        # 如果存在当前口上id，则获取当前行为id和特殊口上标志
        if now_talk_id and now_talk_id in game_config.config_talk:
            now_behavior_id = game_config.config_talk[now_talk_id].behavior_id
            unusual_talk_flag = game_config.config_talk[now_talk_id].adv_id
        # 如果口上文本是大括号的地文文本，则获取行为id
        elif talk_text.startswith("{") and talk_text.endswith("}"):
            now_behavior_id = talk_text[1:-1]
        # 玩家读书时额外绘制当前书籍的内容节选
        if character_id == 0 and now_behavior_id == constant.Behavior.READ_BOOK:
            from Script.UI.Panel import read_book_panel
            read_book_panel.draw_book_fragment(character_data.behavior.book_id)
        # 检测是否需要跳过
        not_draw_flag = check_not_draw_talk(character_id, now_behavior_id, unusual_talk_flag)
        if not_draw_flag:
            return
        # 特殊符号检测
        tem_text, special_code = special_code_judge(talk_text)
        now_draw = draw.LineFeedWaitDraw()
        # 跳过每次的等待
        if special_code[0]:
            now_draw = draw.NormalDraw()
        now_talk_text = code_text_to_draw_text(talk_text, character_id)
        now_draw.text = now_talk_text
        now_draw.width = normal_config.config_normal.text_width
        # 角色口上
        final_color = "standard"
        if unusual_talk_flag:
            # 口上文本的，角色文本颜色
            target_character_data: game_type.Character = cache.character_data[character_data.target_character_id]
            text_color = character_data.text_color
            tar_text_color = target_character_data.text_color
            if text_color:
                now_draw.style = character_data.name
                final_color = character_data.name
            elif tar_text_color:
                now_draw.style = target_character_data.name
                final_color = target_character_data.name
            # 翻译口上
            if normal_config.config_normal.language != "zh_CN" and cache.ai_setting.ai_chat_translator_setting == 2:
                now_talk_text = handle_chat_ai.judge_use_text_ai(character_id, now_behavior_id, now_talk_text, translator=True)
                now_draw.text = now_talk_text
        # 地文
        else:
            cache.ai_setting.ai_chat_setting.setdefault(1, 0)
            # 地文翻译
            if normal_config.config_normal.language != "zh_CN" and cache.ai_setting.ai_chat_translator_setting >= 1:
                now_talk_text = handle_chat_ai.judge_use_text_ai(character_id, now_behavior_id, now_talk_text, translator=True)
                now_draw.text = now_talk_text
            # 如果启用了文本生成ai
            elif cache.ai_setting.ai_chat_setting[1]:
                now_draw = draw.LineFeedWaitDraw()
                now_talk_text = handle_chat_ai.judge_use_text_ai(character_id, now_behavior_id, now_talk_text)
                now_draw.width = normal_config.config_normal.text_width
                now_draw.text = now_talk_text
        # 进行原文本的绘制，现已被富文本绘制替代
        # now_draw.draw()
        # 进行富文本的绘制
        rich_text_draw_list = rich_text.get_rich_text_draw_list(now_talk_text, base_style=final_color, wait_flag=True)
        for rich_text_draw in rich_text_draw_list:
            rich_text_draw.width = normal_config.config_normal.text_width
            rich_text_draw.draw()
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
    # 遍历所有必须显示的二段行为
    for behavior_id in character_data.must_show_second_behavior_id_list:
        # 跳过值为0的行为
        if behavior_id in character_data.second_behavior and character_data.second_behavior[behavior_id] == 0:
            continue
        # 进行绘制
        now_talk_data = handle_talk_sub(character_id, behavior_id, True)
        talk_text, now_talk_id = choice_talk_from_talk_data(now_talk_data, behavior_id)
        handle_talk_draw(character_id, talk_text, now_talk_id, behavior_id)
        # 遍历该二段行为的所有结算效果，挨个触发，但因为不在结算阶段，所以不会显示具体的结算数据
        change_data = game_type.CharacterStatusChange()
        for effect_id in game_config.config_behavior_effect_data[behavior_id]:
            constant.settle_second_behavior_effect_data[effect_id](character_id, change_data)
        # 触发后该行为值归零
        character_data.second_behavior[behavior_id] = 0
    character_data.must_show_second_behavior_id_list = []


def second_behavior_info_text(character_id: int, second_behavior_id: str):
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
    # 多重绝顶
    if "plural_orgasm" in second_behavior_id:
        count_name_list = [_("双重"), _("三重"), _("四重"), _("五重"), _("六重"), _("七重"), _("八重"), _("九重"), _("十重")]
        count_int =  int(second_behavior_id.split("plural_orgasm_")[-1])
        count_name = count_name_list[count_int - 2]
        info_text = _("\n{0}{1}绝顶\n").format(chara_name, count_name)
    # 饮精绝顶
    elif second_behavior_id == "semen_drinking_climax":
        info_text = _("\n{0}饮精绝顶\n").format(chara_name)
    # 额外绝顶
    elif second_behavior_id == "extra_orgasm":
        info_text = _("\n{0}额外绝顶\n").format(chara_name)
    # 部位绝顶
    elif "orgasm" in second_behavior_id:
        # 玩家
        if character_id == 0:
            if "normal" in second_behavior_id:
                orgasm_degree = _("大量射精")
            elif "strong" in second_behavior_id:
                orgasm_degree = _("超大量射精")
            else:
                orgasm_degree = _("射精")
            info_text = "\n{0}{1}\n".format(chara_name, orgasm_degree)
            info_draw.style = "semen"
        # NPC
        else:
            # 获取部位名称
            if second_behavior_id[0] == "n":
                orgasm_name = _("通用")
            elif second_behavior_id[0] == "b":
                orgasm_name = _("胸部")
            elif second_behavior_id[0] == "c":
                orgasm_name = _("阴蒂")
            elif second_behavior_id[0] == "v":
                orgasm_name = _("阴道")
            elif second_behavior_id[0] == "a":
                orgasm_name = _("肛肠")
            elif second_behavior_id[0] == "u":
                orgasm_name = _("尿道")
            elif second_behavior_id[0] == "w":
                orgasm_name = _("子宫")
            elif second_behavior_id[0] == "s":
                orgasm_name = _("皮肤")
            elif second_behavior_id[0] == "m":
                orgasm_name = _("口喉")
            elif second_behavior_id[0] == "f":
                orgasm_name = _("兽部")
            elif second_behavior_id[0] == "h":
                orgasm_name = _("心理")
            # 绝顶程度
            if "normal" in second_behavior_id:
                orgasm_degree = _("绝顶")
            elif "strong" in second_behavior_id:
                orgasm_degree = _("强绝顶")
            elif "super" in second_behavior_id:
                orgasm_degree = _("超强绝顶")
            elif "edge" in second_behavior_id:
                orgasm_degree = _("绝顶寸止")
            else:
                orgasm_degree = _("小绝顶")
            # 最后文本
            info_text = _("\n{0}{1}{2}\n").format(chara_name, orgasm_name, orgasm_degree)
    # 一般刻印
    elif "mark" in second_behavior_id:
        # 获取刻印名称
        if "happy" in second_behavior_id:
            mark_name = _("快乐")
        elif "yield" in second_behavior_id:
            mark_name = _("屈服")
        elif "pain" in second_behavior_id:
            mark_name = _("苦痛")
        elif "time" in second_behavior_id:
            mark_name = _("时姦")
        elif "terror" in second_behavior_id:
            mark_name = _("恐怖")
        elif "hate" in second_behavior_id:
            mark_name = _("反发")
        elif "unconscious" in second_behavior_id:
            mark_name = _("无觉")
        # 获取刻印程度
        mark_degree = second_behavior_id[-1]
        info_text = _("\n{0}获得了{1}刻印{2}\n").format(chara_name, mark_name, mark_degree)
        # 如果是恐怖和反发刻印，则将绘制变成猩红
        if mark_name == _("恐怖") or mark_name == _("反发"):
            info_draw.style = "crimson"
    # B绝顶喷乳
    elif second_behavior_id == "b_orgasm_to_milk":
        info_text = _("\n{0}因B绝顶而被迫喷乳\n").format(chara_name)
        info_draw.style = "semen"
    # U绝顶漏尿
    elif second_behavior_id == "u_orgasm_to_pee":
        info_text = _("\n{0}因U绝顶而被迫漏尿\n").format(chara_name)
        info_draw.style = "khaki"
    # 初吻
    elif second_behavior_id == "first_kiss":
        info_text = _("\n{0}失去了【初吻】\n").format(chara_name)
        info_draw.style = "gold_enrod"
    # v处女
    elif second_behavior_id == "first_sex":
        info_text = _("\n{0}失去了【阴道处女】\n").format(chara_name)
        info_draw.style = "gold_enrod"
    # a处女
    elif second_behavior_id == "first_a_sex":
        info_text = _("\n{0}失去了【肛门处女】\n").format(chara_name)
        info_draw.style = "gold_enrod"
    # u处女
    elif second_behavior_id == "first_u_sex":
        info_text = _("\n{0}失去了【尿道处女】\n").format(chara_name)
        info_draw.style = "gold_enrod"
    # w处女
    elif second_behavior_id == "first_w_sex":
        info_text = _("\n{0}失去了【子宫处女】\n").format(chara_name)
        info_draw.style = "gold_enrod"

    # 最后补一个换行
    if info_text != "":
        info_text += "\n"
        if info_draw.style == "standard":
            info_draw.style = "gold_enrod"
        info_draw.text = info_text
        info_draw.draw()

    return info_text


def check_not_draw_talk(character_id: int, now_behavior_id: str, unusual_talk_flag: int):
    """
    检测是否需要跳过
    Keyword arguments:
    character_id -- 角色id
    now_behavior_id -- 当前行为id
    unusual_talk_flag -- 是否是特殊文本
    """
    character_data: game_type.Character = cache.character_data[character_id]
    # 未触发文本
    if not now_behavior_id:
        return True

    # NPC的移动
    if character_id != 0 and now_behavior_id == constant.Behavior.MOVE:
        # 设置为屏蔽的不触发
        if cache.all_system_setting.draw_setting[8] == 0:
            # print(f"debug {character_data.name}设置为屏蔽，不显示移动文本")
            return True
        # 跟随博士的移动不触发
        if character_data.sp_flag.is_follow == 1 and handle_premise.handle_move_to_same_target_with_pl(character_id):
            # print(f"debug 智能跟随模式下，{character_data.name}在跟随博士，不显示移动文本")
            return True
        # 当前小时内已触发过的不触发
        if character_data.action_info.move_talk_time.hour == cache.game_time.hour and character_data.action_info.move_talk_time.year != 1:
            # print(f"debug {character_data.name}在当前小时内已触发过一次移动文本")
            return True
        else:
            # 重置移动文本触发时间
            character_data.action_info.move_talk_time = cache.game_time
            return False

    # NPC的等待
    if character_id != 0 and now_behavior_id == constant.Behavior.WAIT:
        # 当前行动中已触发过的不触发
        if character_data.action_info.have_shown_waiting_in_now_instruct:
            # print(f"debug {character_data.name}在当前行动中已触发过一次等待文本")
            return True
        else:
            # 重置当前行动中已触发过等待文本标记
            character_data.action_info.have_shown_waiting_in_now_instruct = True
            return False

    # NPC的每日招呼
    if character_id != 0 and now_behavior_id == constant.SecondBehavior.DAY_HELLO:
        # 全屏蔽
        if cache.all_system_setting.draw_setting[9] == 0:
            # print(f"debug {character_data.name}设置为屏蔽，不显示每日招呼文本")
            return True
        # 仅屏蔽地文
        elif cache.all_system_setting.draw_setting[9] == 2 and not unusual_talk_flag:
            # print(f"debug {character_data.name}设置为仅屏蔽地文，不显示地文的每日招呼文本")
            return True

    return False

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

def talk_common_judge(now_talk: str, character_id: int) -> str:
    """
    转换文本中的通用占位符为对应文本
    参数:
        now_talk (str): 原始文本，包含 {key} 占位符
        character_id (int): 角色ID，用于获取相关配置
    返回:
        str: 转换后的文本
    """
    # 固定为玩家触发
    pl_character_id = 0
    pl_character_data: game_type.Character = cache.character_data[0]
    # 已计算过的前提字典
    calculated_premise_dict = {}
    # 遍历所有通用占位符的 key 和对应的 cid 集合
    for key, cid_list in game_config.config_talk_common_cid_list_by_type.items():
        # 构造匹配 "{key}" 的正则表达式
        pattern = re.compile(r'\{' + re.escape(key) + r'\}')
        # 如果文本中存在该占位符
        if pattern.search(now_talk):
            # print(f"debug 在纸娃娃地文中处理通用占位符 {key}，角色ID: {character_id}")
            # 该角色非玩家，非玩家交互对象，与玩家在同一地点，则将玩家的交互对象设置为该角色
            if character_id != 0 and pl_character_data.target_character_id != character_id and handle_premise.handle_in_player_scene(character_id):
                pl_character_data.target_character_id = character_id
            # 如果该key存在于部位列表中
            if key in game_config.config_talk_common_cid_list_by_part:
                # 获取对应的部位字典
                part_dict = game_config.config_talk_common_cid_list_by_part[key]
                # 如果是部位的短词，则把通用A也加到A键里
                if "_s" in key and "penis" not in key and "hair" not in key:
                    common_s_A_list = game_config.config_talk_common_cid_list_by_part["common_s"]["A"]
                    if "A" in part_dict:
                        part_dict["A"] += common_s_A_list
                # 定义替换函数：每次匹配都随机挑选每个部位一条文本进行拼接
                def _part_replacer(match):
                    """
                    部位占位符替换函数，每次匹配都随机挑选每个部位一条文本进行拼接
                    参数:
                        match: 正则匹配对象（未使用）
                    返回:
                        str: 替换后的文本
                    """
                    nonlocal calculated_premise_dict  # 声明使用外部变量
                    part_str = ""
                    for part in part_dict:
                        now_talk_data: dict = {}
                        talk_common_cid_list = part_dict[part]
                        for talk_common_cid in talk_common_cid_list:
                            # 读取前提配置
                            premise_set = game_config.config_talk_common_premise_data[talk_common_cid]
                            # 判断是部位类还是动作类，部位类则跳过无意识判断
                            body_part_flag = True
                            type_id = game_config.config_talk_common_data[talk_common_cid].type_id
                            if 'action' in type_id:
                                body_part_flag = False
                            # 计算权重
                            weight, calculated_premise_dict = handle_premise.get_weight_from_premise_dict(
                                premise_set, pl_character_id, calculated_premise_dict, weight_all_to_1_flag=True, unconscious_pass_flag=body_part_flag
                            )
                            if weight:
                                now_talk_data.setdefault(weight, []).append(talk_common_cid)
                        # 如果有可替换的候选文本
                        if now_talk_data:
                            w = value_handle.get_rand_value_for_value_region(list(now_talk_data.keys()))
                            cid = random.choice(now_talk_data[w])
                            part_str += game_config.config_talk_common_data[cid].context
                            # 如果是动作类，则添加换行符
                            if 'action' in game_config.config_talk_common_data[cid].type_id:
                                part_str += '\n'
                        else:
                            part_str += ""
                    return part_str
                # 使用 sub 回调逐个替换相同的占位符
                now_talk = pattern.sub(_part_replacer, now_talk)
            # 否则为非部位占位符
            else:
                # 构建权重字典：weight -> set(cid)
                now_talk_data: dict = {}
                for talk_common_cid in cid_list:
                    # 读取前提配置
                    premise_set = game_config.config_talk_common_premise_data[talk_common_cid]
                    # 判断是部位类还是动作类，部位类则跳过无意识判断
                    body_part_flag = True
                    type_id = game_config.config_talk_common_data[talk_common_cid].type_id
                    if 'action' in type_id:
                        body_part_flag = False
                    # 计算权重
                    weight, calculated_premise_dict = handle_premise.get_weight_from_premise_dict(
                        premise_set, pl_character_id, calculated_premise_dict, weight_all_to_1_flag=True, unconscious_pass_flag=body_part_flag
                    )
                    if weight:
                        now_talk_data.setdefault(weight, []).append(talk_common_cid)
                # 如果有可替换的候选文本
                if now_talk_data:
                    # 定义替换函数：每次匹配都随机挑选一条文本
                    def _replacer(match):
                        w = value_handle.get_rand_value_for_value_region(list(now_talk_data.keys()))
                        cid = random.choice(now_talk_data[w])
                        return game_config.config_talk_common_data[cid].context
                    # 使用 sub 回调逐个替换相同的占位符
                    now_talk = pattern.sub(_replacer, now_talk)
    return now_talk

def code_text_to_draw_text(talk_text: str, character_id: int):
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

    # 如果口上文本是大括号的地文文本，则获取行为id
    common_talk_flag = False
    if talk_text.startswith("{") and talk_text.endswith("}"):
        common_talk_flag = True

    # 输入的原文本
    now_talk_text, special_code = special_code_judge(talk_text)

    # 替换通用文本
    now_talk_text = talk_common_judge(now_talk_text, character_id)

    # 如果是纸娃娃地文文本，则将当前id改为玩家id
    if common_talk_flag:
        character_id = 0
        character_data = cache.character_data[character_id]
        target_data = cache.character_data[character_data.target_character_id]

    # 专属称呼处理
    # 他人对自己的称呼
    nick_name = character_data.nick_name
    if nick_name == "":
        nick_name = character_data.name
    # 自己对玩家的称呼
    if character_data.nick_name_to_pl != "":
        nick_name_to_pl = character_data.nick_name_to_pl
    elif player_data.nick_name != "":
        nick_name_to_pl = player_data.nick_name
    else:
        nick_name_to_pl = player_data.name
    # 玩家的称呼
    if character_id != 0 and character_data.nick_name_to_pl != "":
        pl_nick_name = character_data.nick_name_to_pl
    elif character_data.target_character_id != 0 and target_data.nick_name_to_pl != "":
        pl_nick_name = target_data.nick_name_to_pl
    elif player_data.nick_name != "":
        pl_nick_name = player_data.nick_name
    else:
        pl_nick_name = player_data.name
    # 对交互对象的称呼
    if target_data.nick_name != "":
        target_nick_name = target_data.nick_name
    else:
        target_nick_name = target_data.name
    # 交互对象对玩家的称呼
    target_nick_name_to_pl = target_data.nick_name_to_pl
    if target_nick_name_to_pl == "":
        target_nick_name_to_pl = player_data.nick_name

    # 玩家的交互对象
    pl_target_id = player_data.target_character_id
    pl_target_name = ""
    if pl_target_id != 0:
        pl_target_data: game_type.Character = cache.character_data[pl_target_id]
        pl_target_name = pl_target_data.name

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
    self_up_cloth_name = ""
    if character_id != 0 and len(character_data.cloth.cloth_wear[5]):
        for Up_cloth_Id in character_data.cloth.cloth_wear[5]:
            self_up_cloth_name += game_config.config_clothing_tem[Up_cloth_Id].name
    if self_up_cloth_name == "":
        self_up_cloth_name = _("没有穿上衣的裸露身体")
        if character_id == 0:
            self_up_cloth_name = _("兜帽")
    self_down_cloth_name = ""
    if character_id != 0 and len(character_data.cloth.cloth_wear[8]):
        for Down_cloth_Id in character_data.cloth.cloth_wear[8]:
            self_down_cloth_name += game_config.config_clothing_tem[Down_cloth_Id].name
    if self_down_cloth_name == "":
        self_down_cloth_name = _("没有穿下衣的裸露身体")
        if character_id == 0:
            self_down_cloth_name = _("长裤")
    target_up_cloth_name = ""
    if character_id == 0 and len(target_data.cloth.cloth_wear[5]):
        for Up_cloth_Id in target_data.cloth.cloth_wear[5]:
            target_up_cloth_name += game_config.config_clothing_tem[Up_cloth_Id].name
    if target_up_cloth_name == "":
        target_up_cloth_name = _("没有穿上衣的裸露身体")
    target_down_cloth_name = ""
    if character_id == 0 and len(target_data.cloth.cloth_wear[8]):
        for Down_cloth_Id in target_data.cloth.cloth_wear[8]:
            target_down_cloth_name += game_config.config_clothing_tem[Down_cloth_Id].name
    if target_down_cloth_name == "":
        target_down_cloth_name = _("没有穿下衣的裸露身体")
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
    up_cloth_name = ""
    if character_id != 0 and len(character_data.cloth.cloth_wear[5]):
        for Up_cloth_Id in character_data.cloth.cloth_wear[5]:
            up_cloth_name += game_config.config_clothing_tem[Up_cloth_Id].name
    if up_cloth_name == "":
        up_cloth_name = _("没有穿上衣的裸露身体")
    down_cloth_name = ""
    if character_id != 0 and len(character_data.cloth.cloth_wear[8]):
        for Down_cloth_Id in character_data.cloth.cloth_wear[8]:
            down_cloth_name += game_config.config_clothing_tem[Down_cloth_Id].name
    if down_cloth_name == "":
        down_cloth_name = _("没有穿下衣的裸露身体")

    # 最后总结转化
    now_talk_text = now_talk_text.format(
        Name=character_data.name,
        NickName=nick_name,
        NickNameToPl=nick_name_to_pl,
        PlayerName=player_data.name,
        PlayerNickName=pl_nick_name,
        PlayerTargetName=pl_target_name,
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

        SelfUpClothName=self_up_cloth_name,
        SelfDownClothName=self_down_cloth_name,
        TargetUpClothName=target_up_cloth_name,
        TargetDownClothName=target_down_cloth_name,
        TargetBraName=target_bra_name,
        TargetSkiName=target_ski_name,
        TargetPanName=target_pan_name,
        TargetSocName=target_soc_name,
        UpClothName=up_cloth_name,
        DownClothName=down_cloth_name,
        PanName=pan_name,
        SocName=socks_name,
    )

    return now_talk_text