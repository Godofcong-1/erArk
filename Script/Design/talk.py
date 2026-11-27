import random
import re
from contextlib import contextmanager
from types import FunctionType

from Script.Core import cache_control, game_type, value_handle, get_text, constant, rich_text
from Script.Core.web_server import emit_realtime_text
from Script.Design import map_handle, handle_premise, talk_image
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
    # 已计算过的前提字典
    calculated_premise_dict = {}
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
    now_talk_data, calculated_premise_dict = handle_talk_sub(character_id, behavior_id, calculated_premise_dict)
    talk_text, now_talk_id, common_behavior_id = choice_talk_from_talk_data(now_talk_data, behavior_id)
    handle_talk_draw(character_id, talk_text, now_talk_id, common_behavior_id=common_behavior_id)

    # 玩家移动到NPC位置时，NPC的打招呼文本
    if character_id == 0 and behavior_id == constant.Behavior.MOVE:
        scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
        for chara_id in cache.scene_data[scene_path_str].character_list:
            # 要求对象是NPC，且没有跟随玩家
            if chara_id > 0 and handle_premise.handle_not_follow(chara_id):
                # 每个NPC用独立的前提字典，避免复用玩家的缓存把sys_0(是否玩家)误判为1而刷屏
                now_talk_data, _ = handle_talk_sub(chara_id, behavior_id, {})
                talk_text, now_talk_id, common_behavior_id = choice_talk_from_talk_data(now_talk_data, behavior_id)
                handle_talk_draw(chara_id, talk_text, now_talk_id, common_behavior_id=common_behavior_id)


def handle_second_talk(character_id: int, behavior_id: str = "share_blankly"):
    """
    处理二段行为结算对话\n
    Keyword arguments:\n
    character_id -- 角色id\n
    behavior_id -- 行为id，默认为0\n
    """
    character_data: game_type.Character = cache.character_data[character_id]
    # 已计算过的前提字典
    calculated_premise_dict = {}
    # 检测是否是收藏模式#
    if cache.is_collection and character_id:
        player_data: game_type.Character = cache.character_data[0]
        if character_id not in player_data.collection_character:
            return

    # 自己
    if behavior_id == "share_blankly":
        for second_behavior_id, behavior_data in character_data.second_behavior.items():
            if behavior_data != 0:
                now_talk_data, calculated_premise_dict = handle_talk_sub(character_id, second_behavior_id, calculated_premise_dict)
                talk_text, now_talk_id, common_behavior_id = choice_talk_from_talk_data(now_talk_data, second_behavior_id)
                handle_talk_draw(character_id, talk_text, now_talk_id, second_behavior_id, common_behavior_id)
    else:
        now_talk_data, calculated_premise_dict = handle_talk_sub(character_id, behavior_id, calculated_premise_dict)
        talk_text, now_talk_id, common_behavior_id = choice_talk_from_talk_data(now_talk_data, behavior_id)
        handle_talk_draw(character_id, talk_text, now_talk_id, behavior_id, common_behavior_id)

    # 交互对象
    # if character_id == 0 and character_data.target_character_id:
    #     target_character_id = character_data.target_character_id
    #     target_character_data: game_type.Character = cache.character_data[target_character_id]
    #     for second_behavior_id, behavior_data in target_character_data.second_behavior.items():
    #         if behavior_data != 0:
    #             now_talk_data = handle_talk_sub(target_character_id, second_behavior_id)
    #             handle_talk_draw(target_character_id, now_talk_data, second_behavior_id)


def handle_talk_sub(character_id: int, behavior_id: str, calculated_premise_dict: dict = {}, unconscious_pass_flag = False):
    """
    处理行为结算对话的内置循环部分
    Keyword arguments:
    character_id -- 角色id
    behavior_id -- 行为id
    calculated_premise_dict -- 已计算过的前提字典
    unconscious_pass_flag -- 是否无视昏迷状态，默认为False
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
        if character_data.adv != 0 and character_data.adv in cache.all_system_setting.character_text_version:
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
        if target_data.adv != 0 and target_data.adv in cache.all_system_setting.character_text_version:
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
    return now_talk_data, calculated_premise_dict

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
        time_stop_orgasm_relase_premise = {constant_promise.Premise.SELF_TIME_STOP_ORGASM_RELAESE, constant_promise.Premise.TARGET_TIME_STOP_ORGASM_RELAESE}
        judge_premise_and_weight_list.append(time_stop_orgasm_relase_premise)
    # 女儿
    if handle_premise.handle_self_is_player_daughter(character_id) or handle_premise.handle_target_is_player_daughter(character_id):
        daughter_premise = {constant_promise.Premise.SELF_IS_PLAYER_DAUGHTER, constant_promise.Premise.SELF_NOT_PLAYER_DAUGHTER}
        judge_premise_and_weight_list.append(daughter_premise)
    # 在爱情旅馆H
    if handle_premise.handle_h_in_love_hotel(character_id):
        h_in_love_hotel_premise = {constant_promise.Premise.H_IN_LOVE_HOTEL}
        judge_premise_and_weight_list.append(h_in_love_hotel_premise)
    # 在浴室中H
    if handle_premise.handle_h_in_bathroom(character_id):
        h_in_bathroom_premise = {constant_promise.Premise.H_IN_BATHROOM}
        judge_premise_and_weight_list.append(h_in_bathroom_premise)
    # 逆推
    if handle_premise.handle_npc_active_h(character_id) or handle_premise.handle_t_npc_active_h(character_id):
        reverse_premise = {constant_promise.Premise.NPC_ACTIVE_H, constant_promise.Premise.T_NPC_ACTIVE_H}
        judge_premise_and_weight_list.append(reverse_premise)
    # 隐奸
    if handle_premise.handle_hidden_sex_mode_ge_1(character_id) or handle_premise.handle_t_hidden_sex_mode_ge_1(character_id):
        hidden_sex_premise = {constant_promise.Premise.HIDDEN_SEX_MODE_GE_1, constant_promise.Premise.HIDDEN_SEX_MODE_1, constant_promise.Premise.HIDDEN_SEX_MODE_2, constant_promise.Premise.HIDDEN_SEX_MODE_3, constant_promise.Premise.HIDDEN_SEX_MODE_4, constant_promise.Premise.HIDDEN_SEX_MODE_1_OR_2, constant_promise.Premise.HIDDEN_SEX_MODE_3_OR_4, constant_promise.Premise.HIDDEN_SEX_MODE_1_OR_3, constant_promise.Premise.HIDDEN_SEX_MODE_2_OR_4, constant_promise.Premise.TARGET_HIDDEN_SEX_MODE_GE_1, constant_promise.Premise.TARGET_HIDDEN_SEX_MODE_1, constant_promise.Premise.TARGET_HIDDEN_SEX_MODE_2, constant_promise.Premise.TARGET_HIDDEN_SEX_MODE_3, constant_promise.Premise.TARGET_HIDDEN_SEX_MODE_4, constant_promise.Premise.TARGET_HIDDEN_SEX_MODE_1_OR_2, constant_promise.Premise.TARGET_HIDDEN_SEX_MODE_3_OR_4, constant_promise.Premise.TARGET_HIDDEN_SEX_MODE_1_OR_3, constant_promise.Premise.TARGET_HIDDEN_SEX_MODE_2_OR_4}
        judge_premise_and_weight_list.append(hidden_sex_premise)
    # 露出
    if handle_premise.handle_exhibitionism_sex_mode_ge_1(character_id):
        exhibitionism_sex_premise = {constant_promise.Premise.EXHIBITIONISM_SEX_MODE_GE_1, constant_promise.Premise.EXHIBITIONISM_SEX_MODE_1, constant_promise.Premise.EXHIBITIONISM_SEX_MODE_2, constant_promise.Premise.EXHIBITIONISM_SEX_MODE_3, constant_promise.Premise.EXHIBITIONISM_SEX_MODE_4, constant_promise.Premise.TARGET_EXHIBITIONISM_SEX_MODE_GE_1, constant_promise.Premise.TARGET_EXHIBITIONISM_SEX_MODE_1, constant_promise.Premise.TARGET_EXHIBITIONISM_SEX_MODE_2, constant_promise.Premise.TARGET_EXHIBITIONISM_SEX_MODE_3, constant_promise.Premise.TARGET_EXHIBITIONISM_SEX_MODE_4}
        judge_premise_and_weight_list.append(exhibitionism_sex_premise)
    # 群交
    if handle_premise.handle_group_sex_mode_on(character_id):
        group_sex_premise = {constant_promise.Premise.GROUP_SEX_MODE_ON}
        judge_premise_and_weight_list.append(group_sex_premise)
    # 监禁
    if handle_premise.handle_imprisonment_1(character_id) or handle_premise.handle_t_imprisonment_1(character_id):
        imprisonment_premise = {constant_promise.Premise.IMPRISONMENT_1, constant_promise.Premise.T_IMPRISONMENT_1}
        judge_premise_and_weight_list.append(imprisonment_premise)
    # 遍历所有需要判断的前提和对应权重
    for judge_premise_set in judge_premise_and_weight_list:
        for premise in talk_premise_set:
            # 如果口上前提中存在该前提，则进行权重加成
            if premise in judge_premise_set:
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
    now_talk_id -- 口上ID
    common_behavior_id -- 选择器生成纸娃娃地文时的行为ID，否则为None
    """
    talk_text = ""
    now_talk_id = ""
    common_behavior_id = None
    if len(now_talk_data):
        talk_weight = value_handle.get_rand_value_for_value_region(list(now_talk_data.keys()))
        now_talk_id = random.choice(list(now_talk_data[talk_weight]))
        talk_text = game_config.config_talk[now_talk_id].context
        unusual_talk_flag = game_config.config_talk[now_talk_id].adv_id
        # 如果是非特殊口上且是权重低于100的地文，且行为id在通用口上列表中，则按照设置的几率使用纸娃娃地文
        if (
            (not unusual_talk_flag or talk_weight < 100) and
            behavior_id in game_config.config_talk_common_cid_list_by_type and
            cache.all_system_setting.draw_setting[2] == 1
            ):
            use_common_talk_rate = cache.all_system_setting.draw_setting[13]
            if random.randint(1, 100) <= use_common_talk_rate * 10:
                talk_text = '{' + behavior_id + '}'
                now_talk_id = ""
                common_behavior_id = behavior_id
    else:
        # 在没有口上的情况下，如果行为id在通用口上列表中，则调用纸娃娃地文
        if behavior_id in game_config.config_talk_common_cid_list_by_type and cache.all_system_setting.draw_setting[2] == 1:
            talk_text = '{' + behavior_id + '}'
            common_behavior_id = behavior_id
    return talk_text, now_talk_id, common_behavior_id

def handle_talk_draw(character_id: int, talk_text: str, now_talk_id: str, second_behavior_id = "", common_behavior_id: str | None = None):
    """
    处理行为结算对话的输出
    Keyword arguments:
    character_id -- 角色id
    talk_text -- 口上文本
    now_talk_id -- 当前口上id
    second_behavior_id -- 二段行为id，默认为""
    common_behavior_id -- 选择器生成纸娃娃地文时的行为ID，默认为None
    """
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
        # 如果选择器返回纸娃娃地文，则使用其明确的行为ID
        elif common_behavior_id is not None:
            now_behavior_id = common_behavior_id
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
        # 检测并绘制图片
        talk_text = talk_image.draw_image_in_talk(talk_text)
        # 获取最终输出文本
        now_talk_text = code_text_to_draw_text(talk_text, character_id, common_behavior_id is not None)
        draw_talk_text(character_id, now_talk_text, special_code[0], now_behavior_id, unusual_talk_flag)


def draw_talk_text(character_id: int, now_talk_text: str, no_wait_flag: bool, now_behavior_id: str, unusual_talk_flag: int):
    """
    绘制已转换好的口上或地文：决定文本颜色、按需翻译或交给文本生成AI，再按Tk或Web模式输出
    Keyword arguments:
    character_id -- 触发文本的角色id
    now_talk_text -- 已经过 code_text_to_draw_text 转换的最终文本
    no_wait_flag -- 是否不在文本后等待玩家输入（文本里带 <jump> 时为True）
    now_behavior_id -- 文本所属的行为id，供翻译与文本生成AI使用
    unusual_talk_flag -- 角色口上所属的角色adv，0为地文
    Return arguments:
    无
    """
    from Script.Design import handle_chat_ai

    character_data: game_type.Character = cache.character_data[character_id]
    now_draw = draw.LineFeedWaitDraw()
    # 跳过每次的等待
    if no_wait_flag:
        now_draw = draw.NormalDraw()
    now_draw.text = now_talk_text
    now_draw.width = normal_config.config_normal.text_width
    # 角色口上
    final_color = "standard"
    if unusual_talk_flag:
        # 首选当前口上所对应的角色id的文本颜色
        talk_character_data = cache.character_data[unusual_talk_flag]
        if talk_character_data.text_color:
            now_draw.style = talk_character_data.name
            final_color = talk_character_data.name
        # 如果没有，则根据当前角色与交互对象来决定文本颜色
        else:
            # 口上文本的，角色文本颜色
            text_color = character_data.text_color
            # 优先选角色自己
            if text_color:
                now_draw.style = character_data.name
                final_color = character_data.name
            # 如果还没有则选择交互对象
            else:
                target_character_data: game_type.Character = cache.character_data[character_data.target_character_id]
                tar_text_color = target_character_data.text_color
                if tar_text_color:
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
    
    # ========== Web模式处理 ==========
    # 在Web模式下，将口上对话文本发送到对话框区域显示，同时记录到文本回溯缓存
    if hasattr(cache, 'web_mode') and cache.web_mode:
        # 将描述文本添加到Web指令文本缓存，用于文本回溯功能
        if now_talk_text:
            cache.web_instruct_texts.append(now_talk_text)
            # 实时推送文本到前端
            emit_realtime_text(now_talk_text, "instruct")
        from Script.System.Web_Draw_System.dialog_box import add_dialog_text
        # 获取说话者名称
        speaker_name = character_data.name
        # 不需要等待的情况（如跳过模式）
        wait_input = not no_wait_flag
        
        # 判断是否为当前交互对象
        # 玩家(0)的交互对象 或 玩家自己 显示在主对话框
        # 其他角色显示在头像下方的小对话框
        player_data = cache.character_data[0]
        target_character_id = player_data.target_character_id
        
        if character_id == 0 or character_id == target_character_id:
            # 主对话框：显示当前交互对象或玩家的台词
            # 获取当前角色的交互对象ID
            # 注意：target_character_id 为 0 时表示交互对象是玩家，需要保留，不能用 if x 判断
            current_target_id = character_data.target_character_id if character_data.target_character_id != character_data.cid else -1
            add_dialog_text(speaker_name, now_talk_text, final_color, wait_input, target_character_id=current_target_id)
        else:
            # 其他角色：显示在头像下方的小对话框
            # 获取该角色当时的交互对象ID，用于切换到该角色时正确显示
            # 注意：target_character_id 为 0 时表示交互对象是玩家，需要保留，不能用 if x 判断
            other_char_target_id = character_data.target_character_id if character_data.target_character_id != character_data.cid else -1
            add_dialog_text(speaker_name, now_talk_text, final_color, wait_input=False, is_minor=True, character_id=character_id, target_character_id=other_char_target_id)
        return
    # ==========================================
    
    # 进行原文本的绘制，现已被富文本绘制替代
    # now_draw.draw()
    # 先绘制一个空白的换行
    line_feed_draw = draw.NormalDraw()
    line_feed_draw.text = "\n"
    line_feed_draw.draw()
    # 进行富文本的绘制
    rich_text_draw_list = rich_text.get_rich_text_draw_list(now_talk_text, base_style=final_color, wait_flag=True)
    for rich_text_draw in rich_text_draw_list:
        rich_text_draw.width = normal_config.config_normal.text_width
        rich_text_draw.draw()
    # 在最后进行一次换行和等待
    if no_wait_flag:
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
    # 已计算过的前提字典
    calculated_premise_dict = {}
    # 遍历所有必须显示的二段行为
    for behavior_id in character_data.must_show_second_behavior_id_list:
        # 跳过值为0的行为
        if behavior_id in character_data.second_behavior and character_data.second_behavior[behavior_id] == 0:
            continue
        # 进行绘制
        now_talk_data, calculated_premise_dict = handle_talk_sub(character_id, behavior_id, calculated_premise_dict, True)
        talk_text, now_talk_id, common_behavior_id = choice_talk_from_talk_data(now_talk_data, behavior_id)
        handle_talk_draw(character_id, talk_text, now_talk_id, behavior_id, common_behavior_id)
        # 遍历该二段行为的所有结算效果，挨个触发，但因为不在结算阶段，所以不会显示具体的结算数据
        change_data = game_type.CharacterStatusChange()
        for effect_id in game_config.config_behavior_effect_data[behavior_id]:
            constant.settle_second_behavior_effect_data[effect_id](character_id, change_data)
        # 触发后该行为值归零
        character_data.second_behavior[behavior_id] = 0
    character_data.must_show_second_behavior_id_list = []


def get_npc_orgasm_name(second_behavior_id: str) -> tuple:
    """
    取NPC部位绝顶类二段行为在提示行里的部位名与绝顶程度名
    Keyword arguments:
    second_behavior_id -- 二段行为id，如 v_orgasm_strong、b_orgasm_edge
    Return arguments:
    tuple -- (部位名str, 绝顶程度名str)，首字母不是已知部位时部位名为空串
    """
    # 获取部位名称
    orgasm_name = ""
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
    return orgasm_name, orgasm_degree


def second_behavior_info_text(character_id: int, second_behavior_id: str, plural_part_behavior_id_list: list | None = None):
    """
    二段行为结算的信息文本
    Keyword arguments:
    character_id -- 角色id
    second_behavior_id -- 二段行为id
    plural_part_behavior_id_list -- 多重绝顶组合文本时参与的各部位绝顶行为id（每部位取最高程度），给出时把各部位的程度合并进多重绝顶的提示行，默认为None
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
        # 组合文本时把各部位的绝顶程度合并进同一行，替代各部位各自的提示行
        if plural_part_behavior_id_list:
            part_text_list = ["".join(get_npc_orgasm_name(part_behavior_id)) for part_behavior_id in plural_part_behavior_id_list]
            info_text = _("\n{0}{1}绝顶（{2}）\n").format(chara_name, count_name, _("、").join(part_text_list))
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
            orgasm_name, orgasm_degree = get_npc_orgasm_name(second_behavior_id)
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


TALK_COMMON_MAX_PASS = 10
""" 通用占位符最多替换的遍数：最坏顺序下嵌套几层就需要几遍，上限防止数据里出现循环嵌套时死循环 """


def talk_common_judge(now_talk: str, character_id: int) -> str:
    """
    转换文本中的通用占位符为对应文本
    通用文本里会嵌套其他通用占位符（例如 m_orgasm_* 插入 {mouth}），而替换一遍只按加载顺序把每个占位符看一次，
    所以重复替换一遍，直到文本不再变化（最多 TALK_COMMON_MAX_PASS 遍）
    文本中有占位符时，可能把玩家的交互对象改为 character_id（由调用方 code_text_to_draw_text 还原）
    参数:
        now_talk (str): 原始文本，包含 {key} 占位符
        character_id (int): 角色ID，用于获取相关配置
    返回:
        str: 转换后的文本
    """
    for _pass in range(TALK_COMMON_MAX_PASS):
        new_talk = talk_common_judge_one_pass(now_talk, character_id)
        if new_talk == now_talk:
            break
        now_talk = new_talk
    return now_talk


def talk_common_judge_one_pass(now_talk: str, character_id: int) -> str:
    """
    按 config_talk_common_cid_list_by_type 的顺序把每种通用占位符处理一遍：部位占位符总是替换（无候选时为空串），非部位占位符有候选文本时替换同种占位符的所有出现
    文本中有占位符时，可能把玩家的交互对象改为 character_id（由调用方 code_text_to_draw_text 还原）
    参数:
        now_talk (str): 原始文本，包含 {key} 占位符
        character_id (int): 角色ID，用于获取相关配置
    返回:
        str: 替换一遍后的文本
    """
    # 固定为玩家触发（前提在 get_talk_common_weight_data 里按玩家求值）
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
                # 交互对象已变更，前提均是针对交互对象求值的，缓存结论全部失效，需清空以免跨角色误用
                calculated_premise_dict = {}
            # 如果该key存在于部位列表中
            if key in game_config.config_talk_common_cid_list_by_part:
                # 获取对应的部位字典
                part_dict = game_config.config_talk_common_cid_list_by_part[key]
                # 如果是部位的短词，则把通用A也加到A键里
                # 此处必须用endswith而非in，否则a_orgasm_small等含"_s"子串的高潮类key会被误判为部位短词
                if key.endswith("_s") and "penis" not in key and "hair" not in key:
                    common_s_A_list = game_config.config_talk_common_cid_list_by_part["common_s"]["A"]
                    if "A" in part_dict:
                        part_dict = {**part_dict, "A": part_dict["A"].copy()}
                        part_dict["A"] += common_s_A_list
                # 定义替换函数：每次匹配都随机挑选每个部位一条文本进行拼接
                def _part_replacer(match, part_dict=part_dict, key=key):
                    """
                    部位占位符替换函数，每次匹配都随机挑选每个部位一条文本进行拼接
                    参数:
                        match: 正则匹配对象（未使用）
                        part_dict (dict): 部位字典，以默认参数固化当前循环的取值，避免闭包晚绑定
                        key (str): 当前占位符的类型名，以默认参数固化当前循环的取值，避免闭包晚绑定
                    返回:
                        str: 替换后的文本
                    """
                    nonlocal calculated_premise_dict  # 声明使用外部变量
                    part_str = ""
                    # 待拼接的分段列表，部位短词(body_part_*)保持原样全段拼接
                    draw_part_list = list(part_dict)
                    # 纸娃娃地文详细程度分档：仅对动作类(action_part_*)生效
                    if key in game_config.config_talk_common_action_part_type_set:
                        # 显式指定A→B→C的顺序，不依赖part_dict的插入序
                        draw_part_list = [part for part in ("A", "B", "C") if part in part_dict]
                        detail_level = cache.all_system_setting.draw_setting.get(20, 1)
                        # 低档：A/B/C三段中等概率随机只取一段
                        if detail_level == 0:
                            draw_part_list = [random.choice(draw_part_list)] if draw_part_list else []
                        # 中档：整体动作段A + B/C中等概率随机取一段
                        elif detail_level == 1:
                            extra_part_list = [part for part in draw_part_list if part in ("B", "C")]
                            draw_part_list = [part for part in draw_part_list if part == "A"]
                            if extra_part_list:
                                draw_part_list.append(random.choice(extra_part_list))
                        # 高档：不做裁剪，保持三段全出
                    for part in draw_part_list:
                        now_talk_data, calculated_premise_dict = get_talk_common_weight_data(part_dict[part], calculated_premise_dict)
                        # 如果有可替换的候选文本
                        if now_talk_data:
                            cid = choice_id_from_weight_data(now_talk_data)
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
                # 构建权重字典：weight -> [cid]
                now_talk_data, calculated_premise_dict = get_talk_common_weight_data(cid_list, calculated_premise_dict)
                # 如果有可替换的候选文本
                if now_talk_data:
                    # 定义替换函数：每次匹配都随机挑选一条文本
                    def _replacer(match, now_talk_data=now_talk_data):
                        """
                        非部位占位符替换函数，每次匹配都随机挑选一条文本
                        参数:
                            match: 正则匹配对象（未使用）
                            now_talk_data (dict): 权重->cid列表，以默认参数固化当前循环的取值，避免闭包晚绑定
                        返回:
                            str: 替换后的文本
                        """
                        cid = choice_id_from_weight_data(now_talk_data)
                        return game_config.config_talk_common_data[cid].context
                    # 使用 sub 回调逐个替换相同的占位符
                    now_talk = pattern.sub(_replacer, now_talk)
    return now_talk


def get_talk_common_weight_data(cid_list: list, calculated_premise_dict: dict) -> tuple:
    """
    计算一组纸娃娃地文候选的权重：前提固定以玩家为主体求值（交互对象即文本描写的干员），动作类文本照常做无意识判定，部位短词跳过
    Keyword arguments:
    cid_list -- 纸娃娃地文cid列表
    calculated_premise_dict -- 已计算过的前提字典（同一主体与交互对象下可复用）
    Return arguments:
    tuple -- (权重->cid列表的dict（不含权重为0的候选）, 更新后的已计算前提字典)
    """
    now_talk_data: dict = {}
    for talk_common_cid in cid_list:
        # 读取前提配置
        premise_set = game_config.config_talk_common_premise_data[talk_common_cid]
        # 判断是部位类还是动作类，部位类则跳过无意识判断
        body_part_flag = "action" not in game_config.config_talk_common_data[talk_common_cid].type_id
        # 计算权重
        weight, calculated_premise_dict = handle_premise.get_weight_from_premise_dict(
            premise_set, 0, calculated_premise_dict, weight_all_to_1_flag=True, unconscious_pass_flag=body_part_flag
        )
        if weight:
            now_talk_data.setdefault(weight, []).append(talk_common_cid)
    return now_talk_data, calculated_premise_dict


def choice_id_from_weight_data(weight_data: dict) -> str:
    """
    从权重->id集合的候选里按权重抽一个id：先按权重值抽权重档，再在该档内等概率抽取
    Keyword arguments:
    weight_data -- 权重->id列表或集合的dict，不能为空
    Return arguments:
    str -- 抽中的id
    """
    now_weight = value_handle.get_rand_value_for_value_region(list(weight_data.keys()))
    return random.choice(list(weight_data[now_weight]))


@contextmanager
def player_target_as(character_id: int):
    """
    临时把玩家的交互对象设为指定的干员，退出时还原：纸娃娃地文的前提与人称都以玩家为主体、交互对象为文本描写的干员
    Keyword arguments:
    character_id -- 文本描写的干员id，为0时不改动
    Return arguments:
    无（上下文管理器）
    """
    player_data: game_type.Character = cache.character_data[0]
    original_target_character_id = player_data.target_character_id
    if character_id != 0:
        player_data.target_character_id = character_id
    try:
        yield
    finally:
        player_data.target_character_id = original_target_character_id


PLURAL_ORGASM_COMBINE_ADULT_TALENT_SET = {105, 106, 107}
""" 组合文本要求的成年阶段素质（大姐姐 / 熟女 / 人妻）：游戏没有年龄字段，年龄只由阶段素质表示，没有成年阶段素质的一律视为年龄不明 """
PLURAL_ORGASM_COMBINE_EXCLUDE_AREA_SET = {"教", "关押"}
""" 不使用组合文本的区域：教育区（课堂与实践教室）、关押区 """
PLURAL_ORGASM_COMBINE_SEGMENT_ORDER = {"A": 0, "B": 1, "C": 2}
""" 组合文本里各段的分组顺序：先拼全部 A 段，再拼 B 段，最后拼 C 段 """


def get_ancestor_id_set(character_id: int) -> set:
    """
    沿父母链向上收集该角色本人及全部已知祖先的id（玩家为0）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    set -- 本人与祖先的id集合
    """
    ancestor_id_set = set()
    pending_id_list = [character_id]
    while pending_id_list:
        now_id = pending_id_list.pop()
        # 跳过已收集的角色，防止数据里成环
        if now_id in ancestor_id_set:
            continue
        ancestor_id_set.add(now_id)
        if now_id not in cache.character_data:
            continue
        relationship = cache.character_data[now_id].relationship
        for parent_id in (relationship.father_id, relationship.mother_id):
            if parent_id >= 0:
                pending_id_list.append(parent_id)
    return ancestor_id_set


def judge_plural_orgasm_combine_talk(character_id: int) -> bool:
    """
    判断该干员的多重绝顶能否使用组合纸娃娃地文；不能时按原流程逐部位出文本、再出多重绝顶的地文
    Keyword arguments:
    character_id -- 绝顶的干员id
    Return arguments:
    bool -- 可以使用组合文本时为True
    功能: 只有明确成年、清醒、未受胁迫、与在场的H参与者没有血缘时才使用组合文本，以下任一情形都不用：
          年龄：有未成年素质或婴儿 / 幼女 / 萝莉 / 少女阶段，或没有大姐姐 / 熟女 / 人妻阶段素质（年龄不明）；
          校园：学生岗位，或身在教育区；
          血缘：是玩家的后代，或同一场景里在H中的其他角色与她有共同祖先（母女、姐妹等）；
          意识：任何无意识状态（睡眠、醉酒、时停、平然 / 空气 / 体控 / 心控催眠），或身上仍有催眠子状态；
          胁迫：时停解放、被监禁、正在逃跑、被装袋搬运、身在关押区、对博士生气
    """
    from Script.System.Education_System import education_constant

    character_data: game_type.Character = cache.character_data[character_id]
    hypnosis_data = character_data.hypnosis
    # 年龄
    if not handle_premise.handle_self_adult(character_id):
        return False
    if not any(character_data.talent.get(talent_id, 0) for talent_id in PLURAL_ORGASM_COMBINE_ADULT_TALENT_SET):
        return False
    # 校园
    if character_data.work.work_type == education_constant.STUDENT_WORK_TYPE:
        return False
    if character_data.position and character_data.position[0] in PLURAL_ORGASM_COMBINE_EXCLUDE_AREA_SET:
        return False
    # 血缘
    ancestor_id_set = get_ancestor_id_set(character_id)
    if 0 in ancestor_id_set:
        return False
    scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    if scene_path_str in cache.scene_data:
        for other_id in cache.scene_data[scene_path_str].character_list:
            if other_id in {0, character_id} or other_id not in cache.character_data:
                continue
            if not cache.character_data[other_id].sp_flag.is_h:
                continue
            if ancestor_id_set & get_ancestor_id_set(other_id):
                return False
    # 意识
    if handle_premise.handle_unconscious_flag_ge_1(character_id) or character_data.sp_flag.sleep_h_awake:
        return False
    if (
        hypnosis_data.blockhead
        or hypnosis_data.active_h
        or hypnosis_data.roleplay
        or hypnosis_data.pain_as_pleasure
        or hypnosis_data.increase_body_sensitivity
        or hypnosis_data.force_ovulation
    ):
        return False
    # 胁迫
    if handle_premise.handle_self_time_stop_orgasm_relase(character_id):
        return False
    if character_data.sp_flag.imprisonment or character_data.sp_flag.escaping or character_data.sp_flag.be_bagged:
        return False
    if character_data.sp_flag.angry_with_player:
        return False
    return True


def handle_plural_orgasm_talk(character_id: int, plural_behavior_id: str, part_behavior_id_list: list):
    """
    多重绝顶的组合文本：一行合并的提示行，然后一段组合纸娃娃地文，最后是有角色口上的部位各自的口上
    组合文本逐部位取一段：有符合条件的纸娃娃地文时从该部位该程度的 A/B/C 全部分段里合并抽一条，
    没有时从该部位原本的单部位地文里抽一条补位；有符合条件的角色口上的部位不进组合，改为单独显示口上
    取好的各段先按 A→B→C 分组、组内再按部位顺序排列后拼接（补位的单部位地文是完整的一段描写，归入 A 组）
    Keyword arguments:
    character_id -- 绝顶的干员id
    plural_behavior_id -- 多重绝顶的二段行为id，如 plural_orgasm_3
    part_behavior_id_list -- 参与的各部位绝顶行为id（每部位取最高程度），已按部位顺序排列
    Return arguments:
    无
    """
    # 收藏模式下只显示收藏角色的文本（同 handle_second_talk）
    if cache.is_collection and character_id:
        if character_id not in cache.character_data[0].collection_character:
            return
    # 合并的提示行
    second_behavior_info_text(character_id, plural_behavior_id, part_behavior_id_list)
    use_common_talk_flag = cache.all_system_setting.draw_setting[2] == 1
    calculated_premise_dict = {}
    common_calculated_premise_dict = {}
    segment_list = []  # 组合文本的各段：(分段序号, 部位序号, 原文本, 是否为纸娃娃地文)
    adv_talk_id_list = []  # 单独显示的角色口上id
    for part_index, part_behavior_id in enumerate(part_behavior_id_list):
        # 该部位原本的口上与地文候选（以绝顶的干员为主体求值）
        now_talk_data, calculated_premise_dict = handle_talk_sub(character_id, part_behavior_id, calculated_premise_dict)
        adv_talk_data = {}
        common_talk_data = {}
        for talk_weight, talk_id_set in now_talk_data.items():
            for talk_id in talk_id_set:
                if game_config.config_talk[talk_id].adv_id:
                    adv_talk_data.setdefault(talk_weight, []).append(talk_id)
                else:
                    common_talk_data.setdefault(talk_weight, []).append(talk_id)
        # 有角色口上的部位单独显示口上
        if adv_talk_data:
            adv_talk_id_list.append(choice_id_from_weight_data(adv_talk_data))
            continue
        # 纸娃娃地文：该部位该程度的 A/B/C 分段都登记在同一个类型下，合并抽一条
        if use_common_talk_flag and part_behavior_id in game_config.config_talk_common_cid_list_by_type:
            with player_target_as(character_id):
                talk_common_data, common_calculated_premise_dict = get_talk_common_weight_data(
                    game_config.config_talk_common_cid_list_by_type[part_behavior_id], common_calculated_premise_dict
                )
            if talk_common_data:
                talk_common_cid = choice_id_from_weight_data(talk_common_data)
                talk_common_config = game_config.config_talk_common_data[talk_common_cid]
                # 分段字母取类型名的末位（同 game_config.load_talk_common），不分段的整段文本按 A 段处理
                segment_part = talk_common_config.type_id[-1] if "part" in talk_common_config.type_id else "A"
                segment_list.append((PLURAL_ORGASM_COMBINE_SEGMENT_ORDER.get(segment_part, 0), part_index, talk_common_config.context, True))
                continue
        # 没有纸娃娃地文时，用该部位原本的单部位地文补位，归入 A 组
        if common_talk_data:
            talk_id = choice_id_from_weight_data(common_talk_data)
            segment_list.append((PLURAL_ORGASM_COMBINE_SEGMENT_ORDER["A"], part_index, game_config.config_talk[talk_id].context, False))
    # 组合文本：先按 A→B→C 分组、组内按部位顺序排列，各段按各自的视角转换后拼接，整段一次输出
    if segment_list:
        segment_list.sort(key=lambda segment: (segment[0], segment[1]))
        no_wait_flag = False
        combine_text = ""
        for _segment_order, _part_index, segment_text, common_flag in segment_list:
            segment_text, special_code = special_code_judge(segment_text)
            no_wait_flag = no_wait_flag or special_code[0]
            segment_text = talk_image.draw_image_in_talk(segment_text)
            # 纸娃娃地文以玩家为主体、交互对象为该干员；单部位地文以该干员为主体
            if common_flag:
                with player_target_as(character_id):
                    combine_text += code_text_to_draw_text(segment_text, character_id, True)
            else:
                combine_text += code_text_to_draw_text(segment_text, character_id)
            combine_text += "\n"
        draw_talk_text(character_id, combine_text, no_wait_flag, plural_behavior_id, 0)
    # 有角色口上的部位，口上在组合文本之后逐条显示
    for talk_id in adv_talk_id_list:
        handle_talk_draw(character_id, game_config.config_talk[talk_id].context, talk_id)

def get_wear_cloth_name(character_data: game_type.Character, clothing_type: int) -> str:
    """
    取角色某服装部位正穿着的衣物名，供文本占位符使用 \n
    Keyword arguments: \n
    character_data -- 角色数据 \n
    clothing_type -- 服装部位cid（同 ClothingType.csv） \n
    Return arguments:
    str -- 衣物名，同一部位穿戴多件时用顿号连接；没有穿戴时为空字符串
    """
    return "、".join(game_config.config_clothing_tem[cloth_id].name for cloth_id in character_data.cloth.cloth_wear.get(clothing_type, []))


def code_text_to_draw_text(talk_text: str, character_id: int, common_talk_flag: bool = False):
    """
    将文本中的代码转化为对应的文本 \n
    Keyword arguments: \n
    talk_text -- 输入的原文本 \n
    character_id -- 角色id \n
    common_talk_flag -- 是否为选择器生成的纸娃娃地文，默认为False \n
    Return arguments:
    now_talk_text -- 转化后的文本
    """
    character_data: game_type.Character = cache.character_data[character_id]
    player_data: game_type.Character = cache.character_data[0]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]

    # 输入的原文本
    now_talk_text, special_code = special_code_judge(talk_text)

    # 替换通用文本
    original_target_character_id = player_data.target_character_id
    try:
        now_talk_text = talk_common_judge(now_talk_text, character_id)
        common_target_character_id = player_data.target_character_id
    finally:
        player_data.target_character_id = original_target_character_id

    # 如果是纸娃娃地文文本，则将当前id改为玩家id
    if common_talk_flag:
        character_id = 0
        character_data = cache.character_data[character_id]
        target_data = cache.character_data[common_target_character_id]

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
    elif (common_target_character_id if common_talk_flag else character_data.target_character_id) != 0 and target_data.nick_name_to_pl != "":
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
    pl_target_id = common_target_character_id
    pl_target_name = ""
    if pl_target_id != 0:
        pl_target_data: game_type.Character = cache.character_data[pl_target_id]
        pl_target_name = pl_target_data.name

    # 当前行为食物
    behavior_food_name = ""
    if character_data.behavior.target_food:
        behavior_food_name = character_data.behavior.target_food.name

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

    # 服装名占位符：来自说话者或交互对象当前穿戴的衣服，内裤和袜子还可能来自偷取/索要等行动记下的名字
    #   逐项为 (占位符名去掉前缀的部分, 服装部位cid, 都取不到时的兜底文本)；每项生成两个占位符：
    #   Target+名 为交互对象的，只在玩家视角（character_id 为 0）下取；Self+名 为说话者自己的，只在 NPC 视角下取
    cloth_slot_list = (
        ("HatName", 0, _("没戴帽子的头顶")),
        ("GlassesName", 1, _("没戴眼镜的双眼")),
        ("EarDecoName", 2, _("没戴耳饰的耳朵")),
        ("NeckDecoName", 3, _("没戴脖饰的脖颈")),
        ("MouthDecoName", 4, _("没戴口饰的嘴边")),
        ("UpClothName", 5, _("没有穿上衣的裸露身体")),
        ("BraName", 6, _("没有穿胸罩的乳房")),
        ("GloveName", 7, _("没戴手套的双手")),
        ("DownClothName", 8, _("没有穿下衣的裸露身体")),
        ("SkiName", 8, _("没有穿裙子的胯部")),
        ("PanName", 9, _("没有穿内裤的阴部")),
        ("SocName", 10, _("没有穿袜子的双腿")),
        ("ShoeName", 11, _("没穿鞋子的双脚")),
        ("WeaponName", 12, _("没拿武器的双手")),
        ("AttachmentName", 13, _("没戴附属物的身体")),
    )
    # 取不到正穿戴的内裤、袜子时，先用偷取/索要等行动记下的名字，再用兜底文本
    behavior_cloth_name_dict = {9: player_data.behavior.pan_name, 10: player_data.behavior.socks_name}
    owner_data_dict = {
        "Target": target_data if character_id == 0 else None,
        "Self": character_data if character_id != 0 else None,
    }
    cloth_name_dict = {}
    for name_suffix, clothing_type, empty_text in cloth_slot_list:
        for owner_prefix, owner_data in owner_data_dict.items():
            cloth_name = get_wear_cloth_name(owner_data, clothing_type) if owner_data is not None else ""
            if cloth_name == "":
                cloth_name = behavior_cloth_name_dict.get(clothing_type, "")
            if cloth_name == "":
                cloth_name = empty_text
            cloth_name_dict[owner_prefix + name_suffix] = cloth_name
    # 不带前缀的旧占位符同为说话者自己的穿戴，保留给已有文本使用
    for name_suffix in ("UpClothName", "DownClothName", "PanName", "SocName"):
        cloth_name_dict[name_suffix] = cloth_name_dict["Self" + name_suffix]
    # 玩家没有服装数据，玩家视角下「自己的上衣 / 下衣」固定写成兜帽与长裤（旧名 UpClothName / DownClothName 不受影响）
    if character_id == 0:
        cloth_name_dict["SelfUpClothName"] = _("兜帽")
        cloth_name_dict["SelfDownClothName"] = _("长裤")

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

        FoodName=behavior_food_name,
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

        **cloth_name_dict,
    )

    return now_talk_text
