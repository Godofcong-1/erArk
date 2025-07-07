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
            # 技巧能力的额外判断
            if ability_cid == 30:
                now_other_ability_level = 0
                # 需要其他性技能力等级满足要求
                for tem_ability_cid in game_config.config_ability:
                    if game_config.config_ability[tem_ability_cid].ability_type == 5:
                        now_other_ability_level += character_data.ability[tem_ability_cid]
                if now_other_ability_level < ability_level * 3:
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
