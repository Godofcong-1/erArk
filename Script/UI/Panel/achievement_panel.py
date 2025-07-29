from types import FunctionType
from Script.Core import cache_control, game_type, get_text, flow_handle, constant
from Script.Design import handle_premise
from Script.UI.Moudle import draw, panel
from Script.Config import game_config, normal_config

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """
line_feed = draw.NormalDraw()
""" 换行绘制对象 """
line_feed.text = "\n"
line_feed.width = 1
window_width: int = normal_config.config_normal.text_width
""" 窗体宽度 """

def achievement_flow():
    """
    成就系统流程\n
    1. 结算成就获得\n
    2. 绘制成就获得提示
    """
    achievement_id_list = []
    # 结算角色关系类成就
    relationship_achievement_list = settle_chara_relationship()
    achievement_id_list.extend(relationship_achievement_list)
    # 绘制成就获得提示
    draw_achievement_notice(achievement_id_list)


def draw_achievement_notice(achievement_id_list: list[int]):
    """
    绘制获得了一个成就的提示\n
    输入：\n
    - achievement_id_list: 成就ID列表
    """
    if not achievement_id_list:
        return
    # 遍历成就
    for achievement_id in achievement_id_list:
        # 获取成就信息
        achievement_data = game_config.config_achievement[achievement_id]
        name = achievement_data.name
        # 绘制成就获得提示
        now_draw = draw.NormalDraw()
        draw_text = _("\n获得成就：{name}\n").format(name=name)
        now_draw.text = draw_text
        now_draw.style = 'gold_enrod'
        now_draw.draw()

def settle_chara_relationship():
    """
    结算角色关系类的成就\n
    返回：\n
    - return_list: 成就列表，包含已达成的成就ID
    """
    return_list = []
    # 存在爱情或隶属路线的角色
    love_flag, obey_flag = False, False
    # 爱侣人数与奴隶人数
    lover_count, slave_count = 0, 0
    for chara_id in cache.character_data:
        # 跳过非角色
        if chara_id == 0:
            continue
        # 跳过不在当前角色列表也不在异常状态7中的
        if chara_id not in cache.npc_id_got and handle_premise.handle_normal_7(chara_id):
            continue
        # 有爱情系陷落
        if love_flag == False and handle_premise.handle_self_fall_love(chara_id):
            love_flag = True
        # 有隶属系陷落
        if obey_flag == False and handle_premise.handle_self_fall_obey(chara_id):
            obey_flag = True
        # 计算爱侣人数
        if handle_premise.handle_self_love_4(chara_id):
            lover_count += 1
        # 计算奴隶人数
        if handle_premise.handle_self_obey_4(chara_id):
            slave_count += 1

    pl_character_data = cache.character_data[0]
    # 成就51，首次爱情线路
    if love_flag and pl_character_data.achievement.achievement_dict.get(51, False) == False:
        pl_character_data.achievement.achievement_dict[51] = True
        return_list.append(51)
    # 成就52，首个爱侣
    if lover_count > 0 and pl_character_data.achievement.achievement_dict.get(52, False) == False:
        pl_character_data.achievement.achievement_dict[52] = True
        return_list.append(52)
    # 成就53，爱侣人数100
    if lover_count >= 100 and pl_character_data.achievement.achievement_dict.get(53, False) == False:
        pl_character_data.achievement.achievement_dict[53] = True
        return_list.append(53)
    # 成就61，首次隶属线路
    if obey_flag and pl_character_data.achievement.achievement_dict.get(61, False) == False:
        pl_character_data.achievement.achievement_dict[61] = True
        return_list.append(61)
    # 成就62，首个奴隶
    if slave_count > 0 and pl_character_data.achievement.achievement_dict.get(62, False) == False:
        pl_character_data.achievement.achievement_dict[62] = True
        return_list.append(62)
    # 成就63，奴隶人数100
    if slave_count >= 100 and pl_character_data.achievement.achievement_dict.get(63, False) == False:
        pl_character_data.achievement.achievement_dict[63] = True
        return_list.append(63)
    return return_list
