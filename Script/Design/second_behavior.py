from types import FunctionType
from Script.Core import cache_control, constant, game_type, get_text
from Script.Design import handle_premise, talk, settle_behavior
from Script.UI.Moudle import draw
from Script.Config import game_config, normal_config

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
width = normal_config.config_normal.text_width
""" 屏幕宽度 """
_: FunctionType = get_text._
""" 翻译api """

_orgasm_settle = None
""" orgasm_settle 模块的延迟导入缓存（规避与Script.Settle包的循环导入，同时消除热路径重复导入开销） """


def _get_orgasm_settle():
    """
    获取 orgasm_settle 模块（延迟导入并缓存）
    参数：无
    返回值类型：module
    功能描述：首次调用时导入 Script.Settle.orgasm_settle 并缓存，后续直接返回缓存引用
    """
    global _orgasm_settle
    if _orgasm_settle is None:
        from Script.Settle import orgasm_settle as _orgasm_settle_module
        _orgasm_settle = _orgasm_settle_module
    return _orgasm_settle

def character_get_second_behavior(character_id: int, second_behavior_id: str, reset: bool = False):
    """
    角色获得二段行为
    Keyword arguments:
    character_id -- 角色id
    second_behavior_id -- 二段行为id
    reset -- 是否重置该二段行为，默认为False
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if second_behavior_id not in character_data.second_behavior:
        character_data.second_behavior[second_behavior_id] = 0
    if reset:
        character_data.second_behavior[second_behavior_id] = 0
        # 如果该二段行为在必须结算列表中，则不再进行结算
        if second_behavior_id in game_config.config_behavior_must_settle_cid_list:
            if second_behavior_id in character_data.must_settle_second_behavior_id_list:
                character_data.must_settle_second_behavior_id_list.remove(second_behavior_id)
        # 如果该二段行为在必须显示列表中，则不再进行显示
        if second_behavior_id in game_config.config_behavior_must_show_cid_list:
            if second_behavior_id in character_data.must_show_second_behavior_id_list:
                character_data.must_show_second_behavior_id_list.remove(second_behavior_id)
    else:
        character_data.second_behavior[second_behavior_id] = 1
        # 如果该二段行为在必须结算列表中，则进行结算
        if second_behavior_id in game_config.config_behavior_must_settle_cid_list:
            character_data.must_settle_second_behavior_id_list.append(second_behavior_id)
        # 如果该二段行为在必须显示列表中，则进行显示
        if second_behavior_id in game_config.config_behavior_must_show_cid_list:
            character_data.must_show_second_behavior_id_list.append(second_behavior_id)

def check_second_effect(
        character_id: int,
        change_data: game_type.CharacterStatusChange,
        pl_to_npc: bool = False,
):
    """
    处理第二结算
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    pl_to_npc -- 玩家对NPC的行为结算
    """
    # 延迟导入，避免与Script.Settle包的循环导入
    orgasm_settle = _get_orgasm_settle()

    # print("进入第二结算")
    orgasm_list = []
    mark_list = []
    item_list = []
    character_data: game_type.Character = cache.character_data[character_id]
    # 仅在存在激活的二段行为时才构建分类列表：
    # 无激活行为时，下游 second_behavior_effect 会因"无任何二段行为"直接返回，
    # 列表内容不会被使用，跳过每次约两百次的子串扫描
    if any(character_data.second_behavior.values()):
        for second_behavior_id in character_data.second_behavior:
            if "orgasm" in second_behavior_id:
                orgasm_list.append(second_behavior_id)
            if "mark" in second_behavior_id:
                mark_list.append(second_behavior_id)
    # for cid in game_config.config_body_item:
    #     body_item_data = game_config.config_body_item[cid]
    #     item_list.append(body_item_data.behavior_id)

    # 玩家检测自己
    if character_id == 0:
        character_data = cache.character_data[0]
        # 高潮结算
        orgasm_settle.orgasm_judge(character_id, change_data)
        # 道具结算
        item_effect(character_id)
        # 进行结算
        second_behavior_effect(character_id, change_data)
        # NPC的刻印结算
        change_data.target_change.setdefault(character_data.target_character_id, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[character_data.target_character_id]
        mark_effect(character_data.target_character_id, target_change)
        # 单独遍历结算刻印
        second_behavior_effect(character_data.target_character_id, target_change, mark_list)

    # NPC自己检测自己
    if character_id != 0:
        # 初见和每日招呼结算
        judge_character_first_meet(character_id)
        # 阴茎位置结算
        insert_position_effect(character_id, change_data)
        # 道具结算
        item_effect(character_id)
        # 进行结算
        second_behavior_effect(character_id, change_data)
        # 高潮结算
        orgasm_settle.orgasm_judge(character_id, change_data)
        # 单独遍历结算高潮，按部位仅取最高绝顶程度触发口上
        second_behavior_effect(character_id, change_data, orgasm_list, orgasm_settle_flag=True)

        # 刻印结算
        mark_effect(character_id, change_data)
        # 单独遍历结算刻印
        second_behavior_effect(character_id, change_data, mark_list)


def second_behavior_effect(
        character_id: int,
        change_data: game_type.CharacterStatusChange,
        second_behavior_list: list = [],
        orgasm_settle_flag: bool = False,
        ):
    """
    触发二段行为的口上与效果
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    second_behavior_list -- 仅计算该范围内的二段行为id列表，默认为[]
    orgasm_settle_flag -- 是否为高潮结算调用，为True时按部位统计部位绝顶行为，每个部位仅程度最高的触发口上，其余仅结算效果，默认为False
    """
    # 延迟导入，避免与Script.Settle包的循环导入
    orgasm_settle = _get_orgasm_settle()

    character_data: game_type.Character = cache.character_data[character_id]

    # 如果没有任何二段行为，则直接返回
    if not any(character_data.second_behavior.values()):
        return

    # 检测是否与玩家处于同一位置，进行必须显示和必须结算的二段行为处理
    if (
            character_data.position != cache.character_data[0].position
            and character_data.behavior.move_src != cache.character_data[0].position
    ):
        talk.must_show_talk_check(character_id)
        must_settle_check(character_id)
        return

    # 在处理后，如果没有任何二段行为，则再次直接返回
    if not any(character_data.second_behavior.values()):
        return

    # 高潮结算调用时，先按部位统计本次待结算的部位绝顶行为，记录每个部位的最高绝顶程度
    part_max_degree_dict = {}
    if orgasm_settle_flag:
        for second_behavior_id, behavior_data in character_data.second_behavior.items():
            if behavior_data == 0:
                continue
            if second_behavior_list and second_behavior_id not in second_behavior_list:
                continue
            orgasm_part, orgasm_degree = orgasm_settle.get_orgasm_part_and_degree(second_behavior_id)
            # 跳过非部位绝顶行为
            if orgasm_part is None:
                continue
            if orgasm_degree > part_max_degree_dict.get(orgasm_part, -1):
                part_max_degree_dict[orgasm_part] = orgasm_degree

    # 遍历二段行为id，进行结算
    for second_behavior_id, behavior_data in character_data.second_behavior.items():
        if behavior_data != 0:
            if second_behavior_list and second_behavior_id not in second_behavior_list:
                continue
            talk_flag = True
            # 高潮结算时，同一部位内非最高程度的绝顶行为仅结算效果，不触发口上
            if part_max_degree_dict:
                orgasm_part, orgasm_degree = orgasm_settle.get_orgasm_part_and_degree(second_behavior_id)
                if orgasm_part is not None and orgasm_degree < part_max_degree_dict.get(orgasm_part, -1):
                    talk_flag = False
            # 触发二段行为的口上
            if talk_flag:
                talk.handle_second_talk(character_id, second_behavior_id)
            # 如果没找到对应的结算效果，则直接跳过
            if second_behavior_id not in game_config.config_behavior_effect_data:
                print(f"debug second_behavior_id = {second_behavior_id}没有找到对应的结算效果")
                continue
            # 遍历该二段行为的所有结算效果，挨个触发
            for effect_id in game_config.config_behavior_effect_data[second_behavior_id]:
                # 综合数值结算判定
                # 如果effect_id是str类型，则说明是综合数值结算
                if isinstance(effect_id, str) and "CVE" in effect_id:
                    effect_all_value_list = effect_id.split("_")[1:]
                    settle_behavior.handle_comprehensive_value_effect(character_id, effect_all_value_list, change_data)
                else:
                    if effect_id not in constant.settle_second_behavior_effect_data:
                        print(f"debug second_behavior_id = {second_behavior_id}，effect_id = {effect_id}没有找到对应的结算效果")
                        continue
                    constant.settle_second_behavior_effect_data[effect_id](character_id, change_data)
            # print(f"debug {character_data.name}触发二段行为效果，behavior_id = {behavior_id}")
            # 触发后该行为值归零
            character_data.second_behavior[second_behavior_id] = 0

def must_settle_check(character_id: int):
    """
    检查是否有必须计算但不必须显示的空白结算
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    # 遍历所有必须计算的二段行为
    for behavior_id in character_data.must_settle_second_behavior_id_list:
        # 跳过值为0的行为
        if behavior_id in character_data.second_behavior and character_data.second_behavior[behavior_id] == 0:
            continue
        # 遍历该二段行为的所有结算效果，挨个触发，但因为不在结算阶段，所以不会显示具体的结算数据
        change_data = game_type.CharacterStatusChange()
        for effect_id in game_config.config_behavior_effect_data[behavior_id]:
            # 综合数值结算判定
            # 如果effect_id是str类型，则说明是综合数值结算
            if isinstance(effect_id, str) and "CVE" in effect_id:
                effect_all_value_list = effect_id.split("_")[1:]
                settle_behavior.handle_comprehensive_value_effect(character_id, effect_all_value_list, change_data)
            else:
                constant.settle_second_behavior_effect_data[effect_id](character_id, change_data)
        # 触发后该行为值归零
        character_data.second_behavior[behavior_id] = 0
    character_data.must_settle_second_behavior_id_list = []

def judge_character_first_meet(character_id: int):
    """
    判断初见和每日招呼\n
    Keyword arguments:
    character_id -- 角色id\n
    Return arguments:
    bool -- 本次update时间切片内活动是否已完成
    """
    character_data: game_type.Character = cache.character_data[character_id]
    pl_character_data: game_type.Character = cache.character_data[0]

    # 需要NPC状态6正常，且不是睡觉状态，玩家不在男隐或双隐的隐奸中，且没在睡觉
    if (
        handle_premise.handle_normal_6(character_id) and
        handle_premise.handle_action_not_sleep(character_id) and
        not handle_premise.handle_hidden_sex_mode_3_or_4(0) and
        handle_premise.handle_action_not_sleep(0)
        ):
        # 优先输出初见，次要输出每日招呼
        if character_data.first_record.first_meet and character_data.position == pl_character_data.position:
            character_get_second_behavior(character_id, "first_meet")
            character_data.first_record.first_meet = 0
            character_data.first_record.day_first_meet = 0
        elif character_data.first_record.day_first_meet and character_data.position == pl_character_data.position:
            # 如果是要早安问候的助理，则不每日招呼
            if handle_premise.handle_assistant_morning_salutation_on(character_id):
                pass
            else:
                character_get_second_behavior(character_id, "day_hello")
            character_data.first_record.day_first_meet = 0
            # 判断上交内裤与袜子
            if handle_premise.handle_wear_pan(character_id) and handle_premise.handle_ask_give_pan_everyday(character_id):
                character_get_second_behavior(character_id, "give_pan_in_day_first_meet")
            if handle_premise.handle_wear_socks(character_id) and handle_premise.handle_ask_give_socks_everyday(character_id):
                character_get_second_behavior(character_id, "give_socks_in_day_first_meet")

def insert_position_effect(character_id: int, change_data: game_type.CharacterStatusChange):
    """
    处理第二结算中的阴茎位置结算
    Keyword arguments:
    character_id -- 角色id
    change_data: game_type.CharacterStatusChange,
    """
    # 导入常用结算函数，避免循环导入
    from Script.Settle.common_default import base_chara_experience_common_settle

    character_data: game_type.Character = cache.character_data[character_id]
    pl_character_data: game_type.Character = cache.character_data[0]
    # 当前不在H中，当前有阴茎插入，则重置插入
    if not handle_premise.handle_self_is_h(character_id) and character_data.h_state.insert_position != -1:
        # 重置插入位置
        character_data.h_state.insert_position = -1
        character_data.h_state.insert_position_change_save = -1
    # 当前有阴茎插入、当前位置为玩家位置
    if (
        character_data.h_state.insert_position != -1 and
        character_data.position == pl_character_data.position
        ):
        # 非群交模式
        if handle_premise.handle_group_sex_mode_off(character_id):
            # 如果不等于，则说明是本次指令改变了插入位置，因此不触发二段结算
            if character_data.h_state.insert_position_change_save != character_data.h_state.insert_position:
                character_data.h_state.insert_position_change_save = character_data.h_state.insert_position
            else:
                # 区分是身体还是服装
                if character_data.h_state.insert_position < 20:
                    second_behavior_id = f"penis_in_body_{character_data.h_state.insert_position}"
                else:
                    second_behavior_id = f"penis_in_cloth_{character_data.h_state.insert_position - 20}"
                    # 如果是下衣，则进一步区分是裙子还是裤子
                    if character_data.h_state.insert_position == 28:
                        if handle_premise.handle_wear_skirt(character_id):
                            second_behavior_id += "_skirt"
                        else:
                            second_behavior_id += "_trousers"
                character_get_second_behavior(character_id, second_behavior_id)
        # 如果玩家当前有性交姿势数据
        if pl_character_data.h_state.current_sex_position != -1:
            # 自己增加对应姿势的经验
            exp_id = 140 + pl_character_data.h_state.current_sex_position
            base_chara_experience_common_settle(character_id, exp_id, change_data = change_data)
            # 玩家增加对应姿势的经验
            base_chara_experience_common_settle(0, exp_id, change_data_to_target_change = change_data)


def get_now_state_all_value_and_text_from_mark_up_data(mark_up_id: int, character_id: int) -> tuple:
    """
    从刻印数据中获取刻印的总值和提示文本
    Keyword arguments:
    mark_up_id -- 刻印id
    character_id -- 角色id
    Return arguments:
    tuple -- 总值,提示文本
    """
    # 本地化常用对象，减少每次循环访问全局模块属性的成本
    character_data: game_type.Character = cache.character_data[character_id]
    character_status_data = character_data.status_data
    mark_up_data_need_state_list = game_config.config_mark_up_data_need_state_list[mark_up_id]
    mark_up_data_all_value = 0
    mark_up_data_text = ""
    for need_state in mark_up_data_need_state_list:
        # 跳过空值
        if need_state == ['0'] or need_state == [0]:
            continue
        # 如果长度为2，说明有权重调整
        if len(need_state) == 2:
            state_id = need_state[0]
            adjust = need_state[1]
            # 计算当前状态值
            now_state_value = int(character_status_data[state_id] * adjust)
            mark_up_data_all_value += now_state_value
            mark_up_data_text += f" {game_config.config_character_state[state_id].name}*{adjust} = {now_state_value} "
        else:
            state_id = need_state[0]
            now_state_value = character_status_data[state_id]
            mark_up_data_all_value += now_state_value
            mark_up_data_text += f" {game_config.config_character_state[state_id].name} = {now_state_value} "
    return mark_up_data_all_value, mark_up_data_text

def get_now_juel_all_value_and_text_from_mark_down_data(mark_down_id: int, character_id: int) -> tuple:
    """
    从刻印数据中获取刻印的总值和提示文本
    Keyword arguments:
    mark_down_id -- 刻印id
    character_id -- 角色id
    Return arguments:
    tuple -- 总值,提示文本
    """
    character_data: game_type.Character = cache.character_data[character_id]
    mark_down_data = game_config.config_mark_down_data[mark_down_id]
    mark_down_data_need_juel_list = []
    mark_down_data_need_juel_list.append(mark_down_data.need_juel_1)
    mark_down_data_need_juel_list.append(mark_down_data.need_juel_2)
    mark_down_data_need_juel_list.append(mark_down_data.need_juel_3)
    # 如果有1号，则替换为全快感珠
    if '1' in mark_down_data_need_juel_list:
        mark_down_data_need_juel_list.remove('1')
        for state_id in game_config.config_character_state:
            if game_config.config_character_state[state_id].type == 0:
                mark_down_data_need_juel_list.append(str(state_id))
    mark_down_data_all_value = 0
    mark_down_data_text = ""
    for need_juel in mark_down_data_need_juel_list:
        # 跳过空值
        if need_juel == '0':
            continue
        # 如果存在|符号，说明有权重调整
        if '|' in need_juel:
            juel_id = int(need_juel.split('|')[0])
            adjust = float(need_juel.split('|')[1])
            # 计算当前宝珠值
            now_juel_value = int(character_data.juel[juel_id] * adjust)
            mark_down_data_all_value += now_juel_value
            mark_down_data_text += f" {game_config.config_juel[juel_id].name}*{adjust} = {now_juel_value} "
        else:
            juel_id = int(need_juel)
            now_juel_value = int(character_data.juel[juel_id])
            mark_down_data_all_value += now_juel_value
            mark_down_data_text += f" {game_config.config_juel[juel_id].name} = {now_juel_value} "
    return mark_down_data_all_value, mark_down_data_text

def mark_effect(character_id: int, change_data: game_type.CharacterStatusChange):
    """
    处理第二结算中的刻印结算
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """

    # print()
    # print("进入刻印结算")
    character_data: game_type.Character = cache.character_data[character_id]
    # print(f"name = {character_data.name},change_data.status_data = {change_data.status_data}")
    now_draw = draw.WaitDraw()
    now_draw_text = ""

    if character_id == 0:
        return

    # 快乐刻印检测单指令全部位总高潮次数，2次快乐1,8次快乐2,16次快乐3
    # 或检测单次H中总绝顶次数，5次快乐1,20次快乐2,50次快乐3
    single_happy_count = 0
    all_happy_count = 0
    for state_id in game_config.config_character_state:
        if game_config.config_character_state[state_id].type == 0:
            single_happy_count += character_data.h_state.orgasm_count[state_id][0]
            all_happy_count += character_data.h_state.orgasm_count[state_id][1]
    # print(f"debug happy_count = {happy_count}")
    if character_data.ability[13] <= 0 and (single_happy_count >= 2 or all_happy_count >= 5):
        character_data.ability[13] = 1
        character_get_second_behavior(character_id, "happy_mark_1")
        # 至少提升为欲望1
        if character_data.ability[33] < 0:
            character_data.ability[33] = 1
            now_draw_text += _("在快乐刻印的影响下，{0}的欲望提升至1级\n").format(character_data.name)
    if character_data.ability[13] <= 1 and (single_happy_count >= 8 or all_happy_count >= 20):
        character_data.ability[13] = 2
        character_get_second_behavior(character_id, "happy_mark_2")
        # 至少提升为欲望3
        if character_data.ability[33] < 3:
            character_data.ability[33] = 3
            now_draw_text += _("在快乐刻印的影响下，{0}的欲望提升至3级\n").format(character_data.name)
    if character_data.ability[13] <= 2 and (single_happy_count >= 16 or all_happy_count >= 50):
        character_data.ability[13] = 3
        character_get_second_behavior(character_id, "happy_mark_3")
        # 至少提升为欲望5
        if character_data.ability[33] < 5:
            character_data.ability[33] = 5
            now_draw_text += _("在快乐刻印的影响下，{0}的欲望提升至5级\n").format(character_data.name)

    # 屈服刻印检测屈服+恭顺+羞耻/5，30000屈服1，50000屈服2，100000屈服3
    yield_count, yield_count_text = get_now_state_all_value_and_text_from_mark_up_data(10, character_id)
    # 进行判断
    if yield_count >= game_config.config_mark_up_data[10].need_state_all_value and character_data.ability[14] <= 0:
        character_data.ability[14] = 1
        character_get_second_behavior(character_id, "yield_mark_1")
        # 至少提升为顺从1
        if character_data.ability[31] < 1:
            character_data.ability[31] = 1
            now_draw_text += _("在屈服刻印的影响下，{0}的顺从提升至1级\n").format(character_data.name)
    if yield_count >= game_config.config_mark_up_data[11].need_state_all_value and character_data.ability[14] <= 1:
        character_data.ability[14] = 2
        character_get_second_behavior(character_id, "yield_mark_2")
        # 至少提升为顺从3
        if character_data.ability[31] < 3:
            character_data.ability[31] = 3
            now_draw_text += _("在屈服刻印的影响下，{0}的顺从提升至3级\n").format(character_data.name)
    if yield_count >= game_config.config_mark_up_data[12].need_state_all_value and character_data.ability[14] <= 2:
        character_data.ability[14] = 3
        character_get_second_behavior(character_id, "yield_mark_3")
        # 至少提升为顺从5
        if character_data.ability[31] < 5:
            character_data.ability[31] = 5
            now_draw_text += _("在屈服刻印的影响下，{0}的顺从提升至5级\n").format(character_data.name)

    # 苦痛刻印检测苦痛，20000苦痛1，40000苦痛2，80000苦痛3
    pain_count, pain_count_text = get_now_state_all_value_and_text_from_mark_up_data(21, character_id)
    # 单次增加量
    if 17 in change_data.status_data:
        pain_count += change_data.status_data[17] * 5
    # 需要非深度无意识，且非心控-苦痛快感化
    if handle_premise.handle_normal_6(character_id) and handle_premise.handle_not_hypnosis_pain_as_pleasure(character_id):
        if pain_count >= game_config.config_mark_up_data[21].need_state_all_value and character_data.ability[15] <= 0:
            character_data.ability[15] = 1
            character_get_second_behavior(character_id, "pain_mark_1")
            # 至少提升为受虐1
            if character_data.ability[36] < 1:
                character_data.ability[36] = 1
                now_draw_text += _("在苦痛刻印的影响下，{0}的受虐提升至1级\n").format(character_data.name)
        if pain_count >= game_config.config_mark_up_data[22].need_state_all_value and character_data.ability[15] <= 1:
            character_data.ability[15] = 2
            character_get_second_behavior(character_id, "pain_mark_2")
            # 至少提升为受虐3
            if character_data.ability[36] < 3:
                character_data.ability[36] = 3
                now_draw_text += _("在苦痛刻印的影响下，{0}的受虐提升至3级\n").format(character_data.name)
        if pain_count >= game_config.config_mark_up_data[23].need_state_all_value and character_data.ability[15] <= 2:
            character_data.ability[15] = 3
            character_get_second_behavior(character_id, "pain_mark_3")
            # 至少提升为受虐5
            if character_data.ability[36] < 5:
                character_data.ability[36] = 5
                now_draw_text += _("在苦痛刻印的影响下，{0}的受虐提升至5级\n").format(character_data.name)

    # 无觉刻印检测无意识下的绝顶，前3级同快乐，后3级仅检测无意识绝顶经验
    if handle_premise.handle_unconscious_flag_ge_1(character_id):
        all_happy_count = 0
        for state_id in game_config.config_character_state:
            if game_config.config_character_state[state_id].type == 0:
                single_happy_count += character_data.h_state.orgasm_count[state_id][0]
        all_happy_count = character_data.experience[78]
        # print(f"debug happy_count = {happy_count}")
        if character_data.ability[19] <= 0 and (single_happy_count >= 2 or all_happy_count >= 5):
            character_data.ability[19] = 1
            character_get_second_behavior(character_id, "unconscious_mark_1")
        if character_data.ability[19] <= 1 and (single_happy_count >= 8 or all_happy_count >= 20):
            character_data.ability[19] = 2
            character_get_second_behavior(character_id, "unconscious_mark_2")
        if character_data.ability[19] <= 2 and (single_happy_count >= 16 or all_happy_count >= 50):
            character_data.ability[19] = 3
            character_get_second_behavior(character_id, "unconscious_mark_3")
        if character_data.ability[19] <= 3 and all_happy_count >= 100:
            character_data.ability[19] = 4
            character_get_second_behavior(character_id, "unconscious_mark_4")
            # 至少提升为欲望6
            if character_data.ability[33] < 6:
                character_data.ability[33] = 6
                now_draw_text += _("在无觉刻印的影响下，{0}的欲望提升至6级\n").format(character_data.name)
        if character_data.ability[19] <= 4 and all_happy_count >= 200:
            character_data.ability[19] = 5
            character_get_second_behavior(character_id, "unconscious_mark_5")
            # 至少提升为欲望7
            if character_data.ability[33] < 7:
                character_data.ability[33] = 7
                now_draw_text += _("在无觉刻印的影响下，{0}的欲望提升至7级\n").format(character_data.name)
        if character_data.ability[19] <= 5 and all_happy_count >= 500:
            character_data.ability[19] = 6
            character_get_second_behavior(character_id, "unconscious_mark_6")
            # 至少提升为欲望8
            if character_data.ability[33] < 8:
                character_data.ability[33] = 8
                now_draw_text += _("在无觉刻印的影响下，{0}的欲望提升至8级\n").format(character_data.name)

    # 恐怖刻印检测恐怖+苦痛/5，20000恐怖1，40000恐怖2，80000恐怖3
    terror_count, terror_count_text = get_now_state_all_value_and_text_from_mark_up_data(41, character_id)
    # 单次增加量
    if 18 in change_data.status_data:
        terror_count += change_data.status_data[18] * 5
    if 17 in change_data.status_data:
        terror_count += change_data.status_data[17]
    if terror_count >= game_config.config_mark_up_data[41].need_state_all_value and character_data.ability[17] <= 0:
        character_data.ability[17] = 1
        character_get_second_behavior(character_id, "terror_mark_1")
    if terror_count >= game_config.config_mark_up_data[42].need_state_all_value and character_data.ability[17] <= 1:
        character_data.ability[17] = 2
        character_get_second_behavior(character_id, "terror_mark_2")
    if terror_count >= game_config.config_mark_up_data[43].need_state_all_value and character_data.ability[17] <= 2:
        character_data.ability[17] = 3
        character_get_second_behavior(character_id, "terror_mark_3")

    # 反发刻印检测反感+抑郁+恐怖+苦痛，10000反发1，30000反发2，80000反发3
    hate_count, hate_count_text = get_now_state_all_value_and_text_from_mark_up_data(51, character_id)
    # 单次增加量
    if 20 in change_data.status_data:
        hate_count += change_data.status_data[20] * 5
    if 18 in change_data.status_data:
        hate_count += change_data.status_data[18]
    if 19 in change_data.status_data:
        hate_count += change_data.status_data[19]
    if 17 in change_data.status_data:
        hate_count += change_data.status_data[17]
    # 需要非深度无意识
    if handle_premise.handle_normal_6(character_id):
        if hate_count >= game_config.config_mark_up_data[51].need_state_all_value and character_data.ability[18] <= 0:
            character_data.ability[18] = 1
            character_get_second_behavior(character_id, "hate_mark_1")
        if hate_count >= game_config.config_mark_up_data[52].need_state_all_value and character_data.ability[18] <= 1:
            character_data.ability[18] = 2
            character_get_second_behavior(character_id, "hate_mark_2")
        if hate_count >= game_config.config_mark_up_data[53].need_state_all_value and character_data.ability[18] <= 2:
            character_data.ability[18] = 3
            character_get_second_behavior(character_id, "hate_mark_3")

    if len(now_draw_text) > 0:
        now_draw_text += "\n"
    now_draw.text = now_draw_text
    now_draw.draw()

def item_effect(character_id: int):
    """
    处理第二结算中的道具结算
    Keyword arguments:
    character_id -- 角色id
    """

    # print()
    # print(f"进入道具结算")
    character_data: game_type.Character = cache.character_data[character_id]

    # NPC对自己进行道具结算
    if character_id != 0:

        # 疑似没有用了，所以注释掉
        # # 玩家在H中正在对该NPC进行交互时，仅计算一遍，避免二次结算
        # if pl_to_npc:
        #     pass
        # elif pl_character_data.target_character_id == character_id and character_data.sp_flag.is_h:
        #     return

        for i in range(len(character_data.h_state.body_item)):
            if character_data.h_state.body_item[i][1]:
                # 事前避孕药的结算仅在每日问候的时候出现一起，其他时候不出现
                if i == 11 and character_data.second_behavior["day_hello"] != 0:
                    continue
                body_item_data = game_config.config_body_item[i]
                # 如果是猥亵型装备且当前不在H中，则判断该道具是否在开启中
                if body_item_data.type == 2 and not handle_premise.handle_self_is_h(character_id):
                    # 如果没有开启，则跳过
                    if handle_premise.handle_self_now_sex_toy_off(character_id):
                        continue
                    # 如果与玩家不在同一场景，则将该道具置为关闭状态然后跳过
                    if not handle_premise.handle_in_player_scene(character_id):
                        character_data.sp_flag.sex_toy_level = 0
                        continue
                second_behavior_id = body_item_data.behavior_id
                character_get_second_behavior(character_id, second_behavior_id)

        # 绳子捆绑
        if handle_premise.handle_self_now_bondage(character_id):
            character_get_second_behavior(character_id, "condage")
