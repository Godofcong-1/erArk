from types import FunctionType
from typing import Tuple
from Script.Core import cache_control, game_type, get_text
from Script.Config import game_config, normal_config
from Script.UI.Moudle import draw

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

def check_upgrade_requirements(need_list: list, character_id: int) -> Tuple[bool, dict]:
    """
    描述：判断角色是否满足能力升级的所有需求，并返回是否满足及需要消耗的珠。
    参数:
      need_list (list[str]): 升级需求列表，每个元素格式为 "X<number>|<数值>"。
      character_id (int): 角色ID。
    返回值:
      (bool, dict): 布尔值表示是否满足所有需求，字典包含需要消耗的珠信息。
    """
    character_data: game_type.Character = cache.character_data[character_id]
    jule_dict = {}
    for need_text in need_list:
        # 解析需求字符串
        need_type = need_text.split('|')[0][0]
        if len(need_text.split('|')[0]) >= 2:
            need_type_id = int(need_text.split('|')[0][1:])
        need_value = int(need_text.split('|')[1])
        # 检查不同类型的需求
        if need_type == "A":
            if character_data.ability[need_type_id] < need_value:
                return False, {}
        elif need_type == "T":
            if not character_data.talent[need_value]:
                return False, {}
        elif need_type == "J":
            jule_dict[need_type_id] = need_value
            if character_data.juel[need_type_id] < need_value:
                return False, {}
        elif need_type == "E":
            if character_data.experience[need_type_id] < need_value:
                return False, {}
        elif need_type == "F":
            if character_data.favorability[0] < need_value:
                return False, {}
        elif need_type == "X":
            if character_data.trust < need_value:
                return False, {}
    return True, jule_dict

def gain_ability(character_id: int):
    """
    结算可以获得的能力
    参数:
        character_id (int): 角色id
    返回值:
        None
    功能描述:
        遍历所有能力，判断是否满足升级条件，支持主需求和备选需求（AbilityUp.csv的up_need和up_need2），满足任一即可升级。
    """
    character_data: game_type.Character = cache.character_data[character_id]
    # 遍历全能力
    for ability_cid in game_config.config_ability:
        ability_data = game_config.config_ability[ability_cid]
        # 跳过刻印部分
        if ability_data.ability_type == 2:
            continue

        # 进行循环，以保证能力升级时可以继续升级，直到满足退出条件
        while True:
            ability_level = character_data.ability[ability_cid]
            # 最大8级
            if ability_level >= 8:
                break
            # 去掉与性别不符的感度与扩张
            if character_data.sex == 0:
                if ability_cid in {2, 4, 7, 9, 12, 73, 74}:
                    break
            elif character_data.sex == 1:
                if ability_cid == 3:
                    break

            # 先尝试主需求
            need_list = game_config.config_ability_up_data[ability_cid][ability_level]
            # 调用独立函数判断升级需求是否满足，并获取需要消耗的珠
            judge, jule_dict = check_upgrade_requirements(need_list, character_id)
            # 如果主需求不满足，尝试备选需求
            if not judge and ability_cid in game_config.config_ability_up2_data and ability_level in game_config.config_ability_up2_data[ability_cid]:
                need_list2 = game_config.config_ability_up2_data[ability_cid][ability_level]
                judge2, jule_dict2 = check_upgrade_requirements(need_list2, character_id)
                if judge2:
                    judge = True
                    jule_dict = jule_dict2
            # 能力的额外判断
            extra_judge = extra_ability_check(ability_id= ability_cid, character_id=character_id, draw_flag=False)
            # 如果额外条件不满足，则将judge置为0
            if extra_judge == 0:
                judge = False
            if not judge:
                break

            # 满足要求则升级能力
            character_data.ability[ability_cid] += 1
            ability_name = ability_data.name

            # 扣除相应的珠
            for need_type_id in jule_dict:
                character_data.juel[need_type_id] -= jule_dict[need_type_id]

            # 输出升级信息
            now_draw_succed = draw.NormalDraw()
            now_draw_succed.text = _("{0}的{1}提升到{2}级\n").format(character_data.name, ability_name, str(ability_level+1))
            now_draw_succed.draw()
    # print(f"debug {character_data.name}的睡觉结算素质结束")


def extra_ability_check(ability_id : int, character_id : int, draw_flag : bool = True):
    """
    能力升级的额外条件检查
    参数:
    ability_id: int -- 能力id
    character_id: int -- 角色id
    draw_flag: bool -- 是否绘制额外条件信息
    返回:
    judge: int -- 主条件是否满足
    """
    judge = 1
    character_data = cache.character_data[character_id]
    ability_data = game_config.config_ability[ability_id]
    info_text = ""
    # 技巧
    if ability_data.name == _("技巧"):
        # 玩家的情况
        if character_id == 0:
            now_ability_level = character_data.ability[ability_id]
            now_other_ability_level = 0
            # 统计所有子性技等级之和
            for tem_ability_cid in game_config.config_ability:
                if game_config.config_ability[tem_ability_cid].ability_type == 5:
                    now_other_ability_level += character_data.ability[tem_ability_cid]
            info_text = _("\n○博士的技巧升级需要额外满足以下条件：\n")
            info_text += _("  [指技]、[舌技]、[腰技]、[隐蔽]能力等级之和大于等于技巧等级*2\n")
            info_text += _("  当前技巧等级为{0}，当前[指技]、[舌技]、[腰技]等级之和为{1}\n").format(now_ability_level, now_other_ability_level)
            if now_other_ability_level < now_ability_level * 2:
                judge = 0
        # NPC的情况
        else:
            now_ability_level = character_data.ability[ability_id]
            now_other_ability_level = 0
            # 统计所有子性技等级之和
            for tem_ability_cid in game_config.config_ability:
                if game_config.config_ability[tem_ability_cid].ability_type == 5:
                    now_other_ability_level += character_data.ability[tem_ability_cid]
            info_text = _("\n○干员的技巧升级需要额外满足以下条件：\n")
            info_text += _("  全子性技的等级之和，即[指技]、[舌技]、[足技]、[胸技]、[膣技]、[肛技]、[隐蔽]能力等级之和大于等于技巧等级*3\n")
            info_text += _("  当前技巧等级为{0}，当前全子性技的等级和为{1}\n").format(now_ability_level, now_other_ability_level)
            if now_other_ability_level < now_ability_level * 3:
                judge = 0
    # 顺从
    elif ability_data.name == _("顺从"):
        # 在提升至4、6、8级时分别需要屈服刻印1、2、3级
        need_mark_level = 0
        if character_data.ability[ability_id] >= 7:
            need_mark_level = 3
        elif character_data.ability[ability_id] >= 5:
            need_mark_level = 2
        elif character_data.ability[ability_id] >= 3:
            need_mark_level = 1
        # 获取屈服刻印等级
        yield_ability_id = 14
        for tem_ability_cid in game_config.config_ability:
            if game_config.config_ability[tem_ability_cid].name == _("屈服刻印"):
                yield_ability_id = tem_ability_cid
                break
        yield_mark_level = character_data.ability[yield_ability_id]
        # 绘制额外条件信息
        info_text = _("\n○顺从能力的提升需要额外满足以下条件：\n")
        info_text += _("  屈服刻印等级大于等于{0}级\n").format(need_mark_level)
        info_text += _("  当前屈服刻印等级为{0}级\n").format(yield_mark_level)
        # 如果屈服刻印等级不满足，则判定为不满足
        if yield_mark_level < need_mark_level:
            judge = 0
    # 欲望
    elif ability_data.name == _("欲望"):
        # 在提升至4、6、8级时分别需要快乐刻印1、2、3级
        need_mark_level = 0
        if character_data.ability[ability_id] >= 7:
            need_mark_level = 3
        elif character_data.ability[ability_id] >= 5:
            need_mark_level = 2
        elif character_data.ability[ability_id] >= 3:
            need_mark_level = 1
        # 获取快乐刻印等级
        happy_ability_id = 13
        for tem_ability_cid in game_config.config_ability:
            if game_config.config_ability[tem_ability_cid].name == _("快乐刻印"):
                happy_ability_id = tem_ability_cid
                break
        happy_mark_level = character_data.ability[happy_ability_id]
        # 绘制额外条件信息
        info_text = _("\n○欲望能力的提升需要额外满足以下条件：\n")
        info_text += _("  快乐刻印等级大于等于{0}级\n").format(need_mark_level)
        info_text += _("  当前快乐刻印等级为{0}级\n").format(happy_mark_level)
        # 如果快乐刻印等级不满足，则判定为不满足
        if happy_mark_level < need_mark_level:
            judge = 0
    # 受虐
    elif ability_data.name == _("受虐"):
        # 在提升至4、6、8级时分别需要苦痛刻印1、2、3级
        need_mark_level = 0
        if character_data.ability[ability_id] >= 7:
            need_mark_level = 3
        elif character_data.ability[ability_id] >= 5:
            need_mark_level = 2
        elif character_data.ability[ability_id] >= 3:
            need_mark_level = 1
        # 获取苦痛刻印等级
        pain_ability_id = 15
        for tem_ability_cid in game_config.config_ability:
            if game_config.config_ability[tem_ability_cid].name == _("苦痛刻印"):
                pain_ability_id = tem_ability_cid
                break
        pain_mark_level = character_data.ability[pain_ability_id]
        # 绘制额外条件信息
        info_text = _("\n○受虐能力的提升需要额外满足以下条件：\n")
        info_text += _("  苦痛刻印等级大于等于{0}级\n").format(need_mark_level)
        info_text += _("  当前苦痛刻印等级为{0}级\n").format(pain_mark_level)
        # 如果苦痛刻印等级不满足，则判定为不满足
        if pain_mark_level < need_mark_level:
            judge = 0
    # 绘制额外条件信息
    if draw_flag:
        now_draw = draw.NormalDraw()
        now_draw.text = info_text
        now_draw.draw()
    return judge
