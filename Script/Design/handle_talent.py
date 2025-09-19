from types import FunctionType
from Script.Design import attr_calculation, handle_premise
from Script.Core import cache_control, game_type, get_text
from Script.Config import game_config, normal_config
from Script.UI.Moudle import draw
from Script.UI.Panel import achievement_panel

_: FunctionType = get_text._
""" 翻译api """
cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """

line_feed = draw.NormalDraw()
""" 换行绘制对象 """
line_feed.text = "\n"
line_feed.width = 1
window_width = normal_config.config_normal.text_width
""" 屏幕宽度 """

def gain_talent(character_id: int, now_gain_type: int, traget_talent_id = 0):
    """
    结算可以获得的素质\n
    Keyword arguments:
    character_id -- 角色id\n
    now_gain_type -- 素质获得类型(0随时自动，1手动，2指令绑定，3睡觉自动)\n
    """
    character_data: game_type.Character = cache.character_data[character_id]
    gain_talent_flag = False
    # 遍历全素质获得
    for gain_talent_cid in game_config.config_talent_gain:
        gain_talent_data = game_config.config_talent_gain[gain_talent_cid]
        gain_type = gain_talent_data.gain_type
        talent_id = gain_talent_data.talent_id

        # 大前提是NPC没有该素质
        if character_data.talent[talent_id]:
            continue

        # 手动结算的话跳过判断直接获得对应素质
        judge = 0
        if now_gain_type == 1 and traget_talent_id == talent_id:
            judge = 1
        # 需要为对应的结算时机
        elif gain_type != 1 and gain_type == now_gain_type:

            # 以&为分割判定是否有多个需求
            if "&" not in gain_talent_data.gain_need:
                need_list = []
                need_list.append(gain_talent_data.gain_need)
            else:
                need_list = gain_talent_data.gain_need.split('&')
            judge, reason = attr_calculation.judge_require(need_list, character_id)

        # 如果符合获得条件，则获得该素质
        if judge:
            character_data.talent[talent_id] = 1
            gain_talent_flag = True
            talent_name = game_config.config_talent[talent_id].name

            # 触发对应的二段行为结算
            if gain_talent_data.second_behavior_id:
                second_behavior_id = gain_talent_data.second_behavior_id
                character_data.second_behavior[second_behavior_id] = 1

            # 判断是否需要进行替代旧素质
            if gain_talent_data.replace_talent_id:
                old_talent_id = gain_talent_data.replace_talent_id
                character_data.talent[old_talent_id] = 0

            now_draw_succed = draw.WaitDraw()
            now_draw_succed.text = _("\n{0}获得了【{1}】\n").format(character_data.name, talent_name)
            now_draw_succed.draw()
    # print(f"debug {character_data.name}的睡觉结算素质结束，judge = {judge}")

    # 结算陷落素质的成就
    if gain_talent_flag:
        achievement_panel.achievement_flow(_("关系"))

    # 特殊素质获得
    if now_gain_type == 0:
        npc_gain_and_lost_cumflation(character_id)
        npc_gain_semen_drinking_climax_talent(character_id)
        npc_b_talent_change_for_lactation_flag(character_id)
    if now_gain_type == 3:
        npc_lost_no_menarche_talent(character_id)

def have_age_talent(character_id: int):
    """
    返回年龄素质\n
    """
    character_data = cache.character_data[character_id]
    for talent_id in [101, 102, 103, 104, 105, 106, 107]:
        if character_data.talent[talent_id]:
            return talent_id
    return 0

def have_chest_talent(character_id: int):
    """
    返回胸部大小素质\n
    """
    character_data = cache.character_data[character_id]
    for talent_id in [121, 122, 123, 124, 125]:
        if character_data.talent[talent_id]:
            return talent_id
    return 0

def have_hip_talent(character_id: int):
    """
    返回臀部大小素质\n
    """
    character_data = cache.character_data[character_id]
    for talent_id in [126, 127, 128]:
        if character_data.talent[talent_id]:
            return talent_id
    return 0

def have_leg_talent(character_id: int):
    """
    返回腿部大小素质\n
    """
    character_data = cache.character_data[character_id]
    for talent_id in [129, 130]:
        if character_data.talent[talent_id]:
            return talent_id
    return 0

def have_foot_talent(character_id: int):
    """
    返回脚部大小素质\n
    """
    character_data = cache.character_data[character_id]
    for talent_id in [131, 132]:
        if character_data.talent[talent_id]:
            return talent_id
    return 0

def have_hypnosis_talent():
    """
    验证是否有催眠系素质\n
    """
    pl_character_data = cache.character_data[0]
    for talent_id in [331,332,333,334]:
        if pl_character_data.talent[talent_id]:
            return talent_id
    return 0

def have_hormone_talent():
    """
    验证是否有激素系素质\n
    """
    pl_character_data = cache.character_data[0]
    for talent_id in [306,305,304]:
        if pl_character_data.talent[talent_id]:
            return talent_id
    return 0

def have_visual_talent():
    """
    验证是否有视觉系素质\n
    """
    pl_character_data = cache.character_data[0]
    for talent_id in [309,308,307]:
        if pl_character_data.talent[talent_id]:
            return talent_id
    return 0

def have_tactile_talent():
    """
    验证是否有触觉系素质\n
    """
    pl_character_data = cache.character_data[0]
    for talent_id in [312,311,310]:
        if pl_character_data.talent[talent_id]:
            return talent_id
    return 0

def have_fall_talent(character_id: int):
    """
    验证是否有陷落素质\n
    """
    character_data = cache.character_data[character_id]
    for talent_id in [201,202,203,204,211,212,213,214]:
        if character_data.talent[talent_id]:
            return talent_id
    return 0

def npc_gain_hypnosis_talent(character_id: int):
    """
    干员获得被催眠素质\n
    """
    pl_character_data = cache.character_data[0]
    character_data = cache.character_data[character_id]
    if character_data.hypnosis.hypnosis_degree < 1:
        return

    for cid in game_config.config_hypnosis_talent_of_npc:
        now_data = game_config.config_hypnosis_talent_of_npc[cid]
        # 如果已经有该素质则跳过
        if character_data.talent[now_data.hypnosis_talent_id]:
            continue
        # 如果玩家没有对应的前置素质则跳过
        if not pl_character_data.talent[now_data.need_talent_id]:
            continue

        if character_data.hypnosis.hypnosis_degree >= now_data.hypnosis_degree:
            character_data.talent[now_data.hypnosis_talent_id] = 1
            talent_name = game_config.config_talent[now_data.hypnosis_talent_id].name
            # 触发对应的二段行为结算
            character_data.second_behavior[now_data.second_behavior_id] = 1
            # 替换旧素质
            # if now_data.hypnosis_talent_id > 71:
            #     old_talent_id = now_data.hypnosis_talent_id - 1
            #     character_data.talent[old_talent_id] = 0
            # 绘制获得素质提示
            now_draw_succed = draw.WaitDraw()
            now_draw_succed.text = _("\n○{0}的催眠深度达到{1}%，获得了[{2}]\n").format(character_data.name, now_data.hypnosis_degree, talent_name)
            now_draw_succed.draw()
            break
    achievement_panel.achievement_flow(_("催眠"))

def npc_gain_and_lost_cumflation(character_id: int):
    """
    干员获得和失去精液膨腹素质\n
    """
    pl_character_data = cache.character_data[0]
    character_data = cache.character_data[character_id]

    # 计算腹部精液总量
    abdomen_all_semen = 0
    for i in [5,7,8,15]:
        # 如果没有第[i]个，则补上
        if len(character_data.dirty.body_semen) <= i:
            part_name = game_config.config_body_part[i].name
            character_data.dirty.body_semen[i] = [part_name,0,0,0]
        abdomen_all_semen += character_data.dirty.body_semen[i][1]

    # 判断是否获得或失去精液膨腹
    now_draw_text = ""
    if abdomen_all_semen >= 6000 and not character_data.talent[32]:
        character_data.talent[32] = 1
        now_draw_text += _("\n○{0}获得了[精液膨腹]\n").format(character_data.name)
    elif abdomen_all_semen < 6000 and character_data.talent[32]:
        character_data.talent[32] = 0
        now_draw_text += _("\n○{0}失去了[精液膨腹]\n").format(character_data.name)

    # 绘制获得素质提示
    if now_draw_text != "" and character_data.position == pl_character_data.position:
        now_draw_succed = draw.WaitDraw()
        now_draw_succed.text = now_draw_text
        now_draw_succed.draw()

def npc_gain_semen_drinking_climax_talent(character_id: int):
    """
    干员获得饮精绝顶素质\n
    """
    character_data = cache.character_data[character_id]
    if character_data.talent[31]:
        return
    if character_data.experience[111] >= 50:
        character_data.talent[31] = 1
        now_draw_text = _("\n{0}因为经常性地在绝顶的同时被口内射精，因此以后尝到精液的味道就会条件反射性地绝顶了\n").format(character_data.name)
        now_draw_text += _("{0}获得了[饮精绝顶]\n").format(character_data.name)
        now_draw_succed = draw.WaitDraw()
        now_draw_succed.text = now_draw_text
        now_draw_succed.draw()

def npc_b_talent_change_for_lactation_flag(character_id: int):
    """
    干员因涨奶而发生的罩杯变化\n
    """
    character_data = cache.character_data[character_id]
    if not character_data.talent[27]:
        return

    # 乳汁量大于80时，罩杯变大
    if handle_premise.handle_milk_ge_80(character_id) and character_data.pregnancy.lactation_flag == False:
        if body_part_talent_update(character_id, [121, 122, 123, 124, 125], True, _("胸部")):
            character_data.pregnancy.lactation_flag = True
    # 乳汁量小于80时，罩杯变小
    elif handle_premise.handle_milk_le_79(character_id) and character_data.pregnancy.lactation_flag == 1:
        character_data.pregnancy.lactation_flag = False
        if body_part_talent_update(character_id, [121, 122, 123, 124, 125], False, _("胸部")):
            pass

def npc_lost_no_menarche_talent(character_id: int):
    """
    干员失去未初潮素质\n
    """
    character_data = cache.character_data[character_id]
    if character_data.talent[6]:
        # 需要W相关开发至少为4级
        if character_data.ability[7] + character_data.ability[12] >= 4:
            character_data.talent[6] = 0
            now_draw_text = _("\n在对子宫的持续开发下，{0}提前迎来了性成熟，可以受精怀孕了\n").format(character_data.name)
            now_draw_text += _("○{0}失去了[未初潮]\n").format(character_data.name)
            now_draw_succed = draw.WaitDraw()
            now_draw_succed.text = now_draw_text
            now_draw_succed.draw()

def body_part_talent_update(character_id, talent_ids, increase, body_part):
    """
    根据素质id表来使角色的身体部位素质变大或变小
    Keyword arguments:
    character_id -- 角色id
    talent_ids -- 素质id列表
    increase -- 是否增加
    body_part -- 身体部位
    """
    now_character_data = cache.character_data[character_id]
    # 获取当前素质id
    now_talent_id = -1
    for talent_id in talent_ids:
        if now_character_data.talent[talent_id] == 1:
            now_talent_id = talent_id
            break
    if now_talent_id == -1:
        return _("未找到目标素质，无法进行变化\n")
    # 更新素质id
    if increase:
        new_talent_id = min(now_talent_id + 1, talent_ids[-1])
    else:
        new_talent_id = max(now_talent_id - 1, talent_ids[0])
    # 如果已经是极限值，则不进行变化
    if now_talent_id == new_talent_id:
        return ""
    now_character_data.talent[now_talent_id] = 0
    now_character_data.talent[new_talent_id] = 1
    # 输出信息
    change_text = _("变大了") if increase else _("变小了")
    return_text = _("{0}的{1}{2}，现在是【{3}】\n".format(now_character_data.name, body_part, change_text, game_config.config_talent[new_talent_id].name))
    return return_text
