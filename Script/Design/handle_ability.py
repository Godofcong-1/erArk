from types import FunctionType
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

def gain_ability(character_id: int):
    """
    结算可以获得的能力\n
    Keyword arguments:
    character_id -- 角色id\n
    """
    character_data: game_type.Character = cache.character_data[character_id]
    # 遍历全能力
    for ability_cid in game_config.config_ability:
        ability_data = game_config.config_ability[ability_cid]
        # 跳过刻印部分
        if ability_data.ability_type == 2:
            continue
        ability_level = character_data.ability[ability_cid]
        # 最大8级
        if ability_level >= 8:
            continue
        # 去掉与性别不符的感度与扩张
        if character_data.sex == 0:
            if ability_cid in {2, 4, 7, 9, 12, 73, 74}:
                continue
        elif character_data.sex == 1:
            if ability_cid == 3:
                continue

        need_list = game_config.config_ability_up_data[ability_cid][ability_level]

        # 遍历升级需求，判断是否符合升级要求
        judge = 1
        jule_dict = {}
        for need_text in need_list:
            need_type = need_text.split('|')[0][0]
            # need_type_id = int(need_text.split('|')[0][1:])
            if len(need_text.split('|')[0]) >= 2:
                need_type_id = int(need_text.split('|')[0][1:])
            need_value = int(need_text.split('|')[1])
            # print(f"debug need_type = {need_type},need_type_id = {need_type_id},need_value = {need_value}")
            if need_type == "A":
                if character_data.ability[need_type_id] < need_value:
                    judge = 0
                    break
            elif need_type == "T":
                if not character_data.talent[need_value]:
                    judge = 0
                    break
            elif need_type == "J":
                jule_dict[need_type_id] = need_value
                if character_data.juel[need_type_id] < need_value:
                    judge = 0
                    break
            elif need_type == "E":
                if character_data.experience[need_type_id] < need_value:
                    judge = 0
                    break
            elif need_type == "F":
                if character_data.favorability[0] < need_value:
                    judge = 0
                    break
            elif need_type == "X":
                if character_data.trust < need_value:
                    judge = 0
                    break

        # 如果符合获得条件，则该能力升级
        if judge:
            character_data.ability[ability_cid] += 1
            ability_name = ability_data.name

            # 减少对应的珠
            for need_type_id in jule_dict:
                character_data.juel[need_type_id] -= jule_dict[need_type_id]

            now_draw_succed = draw.NormalDraw()
            now_draw_succed.text = _("{0}的{1}提升到{2}级\n").format(character_data.name, ability_name, str(ability_level+1))
            now_draw_succed.draw()
    # print(f"debug {character_data.name}的睡觉结算素质结束")
