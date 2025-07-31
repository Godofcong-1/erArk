from types import FunctionType
from typing import List
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

def achievement_flow(achievement_type: str):
    """
    成就系统流程\n
    输入：\n
    - achievement_type: str，成就类型\n
    功能：根据类型结算成就并绘制获得提示
    """
    # 成就类型与结算函数的映射字典
    achievement_type_func_dict = {
        _("周目"): settle_round_achievement,
        _("关系"): settle_chara_relationship,
        _("招募"): settle_recruit_achievement,
        _("访客"): settle_invite_achievement,
        _("囚犯"): settle_prisoner_achievement,
        _("龙门币"): settle_money_achievement,
    }
    # 根据类型获取对应的结算函数
    func = achievement_type_func_dict.get(achievement_type)
    if func is None:
        return
    # 调用结算函数，获得成就ID列表
    achievement_id_list = func()
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
        description = achievement_data.description
        # 绘制成就获得提示
        now_draw = draw.WaitDraw()
        draw_text = _("\n\n   ○ 获得成就：{name} ○\n").format(name=name)
        draw_text += _("      （{description}）\n\n\n").format(description=description)
        now_draw.text = draw_text
        now_draw.style = 'gold_enrod'
        now_draw.draw()

def settle_achievement(judge_value: int, achievement_ids):
    """
    通用成就结算函数（支持单个或批量）\n
    输入：\n
    - judge_value: int，判断值\n
    - achievement_ids: int 或 list[int]，成就ID或成就ID列表\n
    返回：\n
    - return_list: 成就列表，包含已达成的成就ID\n
    功能：判断是否达成成就，如果达成则更新缓存中的成就
    """
    # 如果achievement_ids是单个成就ID，则转换为列表
    if isinstance(achievement_ids, int):
        achievement_ids = [achievement_ids]
    return_list = []
    for achievement_id in achievement_ids:
        # 判断是否达成成就
        if judge_value >= game_config.config_achievement[achievement_id].value and not cache.achievement.achievement_dict.get(achievement_id, False):
            cache.achievement.achievement_dict[achievement_id] = True
            return_list.append(achievement_id)
    return return_list


def settle_round_achievement():
    """
    结算周目类的成就\n
    返回：\n
    - return_list: 成就列表，包含已达成的成就ID
    """
    return settle_achievement(cache.game_round, [1, 2])


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

    # 成就51，首次爱情线路
    if love_flag and cache.achievement.achievement_dict.get(51, False) == False:
        cache.achievement.achievement_dict[51] = True
        return_list.append(51)
    # 成就52，首个爱侣
    if lover_count >= game_config.config_achievement[52].value and cache.achievement.achievement_dict.get(52, False) == False:
        cache.achievement.achievement_dict[52] = True
        return_list.append(52)
    # 成就53，爱侣人数100
    if lover_count >= game_config.config_achievement[53].value and cache.achievement.achievement_dict.get(53, False) == False:
        cache.achievement.achievement_dict[53] = True
        return_list.append(53)
    # 成就61，首次隶属线路
    if obey_flag and cache.achievement.achievement_dict.get(61, False) == False:
        cache.achievement.achievement_dict[61] = True
        return_list.append(61)
    # 成就62，首个奴隶
    if slave_count >= game_config.config_achievement[62].value and cache.achievement.achievement_dict.get(62, False) == False:
        cache.achievement.achievement_dict[62] = True
        return_list.append(62)
    # 成就63，奴隶人数100
    if slave_count >= game_config.config_achievement[63].value and cache.achievement.achievement_dict.get(63, False) == False:
        cache.achievement.achievement_dict[63] = True
        return_list.append(63)
    return return_list

def settle_recruit_achievement():
    """
    结算招募干员数量的成就\n
    返回：\n
    - return_list: 成就列表，包含已达成的成就ID
    """
    return settle_achievement(cache.achievement.recruit_count, [101, 102])


def settle_invite_achievement():
    """
    结算邀请访客数量的成就\n
    返回：\n
    - return_list: 成就列表，包含已达成的成就ID
    """
    return settle_achievement(cache.achievement.visitor_count, [111, 112])


def settle_prisoner_achievement():
    """
    结算囚犯数量的成就\n
    返回：\n
    - return_list: 成就列表，包含已达成的成就ID
    """
    prisoner_count = len(cache.rhodes_island.current_prisoners)
    return settle_achievement(prisoner_count, [121, 122])


def settle_money_achievement():
    """
    结算龙门币成就\n
    返回：\n
    - return_list: 成就列表，包含已达成的成就ID
    """
    money = cache.rhodes_island.materials_resouce[1]
    return settle_achievement(money, [201, 202, 203])

class Achievement_Panel:
    """
    用于显示成就界面面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """

    def draw(self):
        """绘制对象"""

        title_text = _("成就")

        title_draw = draw.TitleLineDraw(title_text, self.width)
        handle_sub_panel = panel.PageHandlePanel([], Achievement_Draw, 10, 1, self.width, 1, 1, 0)
        while 1:
            return_list = []
            title_draw.draw()

            info_text = _("○高难成就需要前置成就才能解锁，隐藏成就才达成前不显示解锁条件\n")
            info_text += _("当前成绩达成：")
            len_got = 0
            for cid in cache.achievement.achievement_dict:
                if cache.achievement.achievement_dict[cid]:
                    len_got += 1
            total = len(game_config.config_achievement)
            info_text += f"{len_got}/{total}\n"

            info_draw = draw.NormalDraw()
            info_draw.text = info_text
            info_draw.draw()

            line_feed.draw()

            # 遍历成就列表
            draw_achievement_list = []
            for cid in game_config.config_achievement:
                achievement_data = game_config.config_achievement[cid]
                cache.achievement.achievement_dict.setdefault(cid, False)
                # 跳过未实装的
                if achievement_data.todo == 1:
                    continue
                # 跳过有前置需求且前置需求没满足的
                if achievement_data.pre_id and not cache.achievement.achievement_dict.get(achievement_data.pre_id, False):
                    continue
                # 跳过未达成的隐藏成就
                if achievement_data.special and not cache.achievement.achievement_dict.get(cid, False):
                    continue
                draw_achievement_list.append(cid)

            # 更新当前面板
            handle_sub_panel.text_list = draw_achievement_list
            handle_sub_panel.update()
            handle_sub_panel.draw()

            return_list.extend(handle_sub_panel.return_list)
            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

class Achievement_Draw:
    """
    信物绘制对象
    Keyword arguments:
    text -- 道具id
    width -- 最大宽度
    """

    def __init__(self, achievement_cid: int, width: int, is_button: bool, num_button: bool, button_id: int):
        """初始化绘制对象"""
        self.achievement_cid: int = achievement_cid
        """ 成就id """
        self.draw_text: str = ""
        """ 绘制文本 """
        self.width: int = width
        """ 最大宽度 """
        self.is_button: bool = is_button
        """ 是否为按钮 """
        self.num_button: bool = num_button
        """ 是否为数字按钮 """
        self.button_id: int = button_id
        """ 按钮编号 """

        # 成就数据
        achievement_data = game_config.config_achievement[achievement_cid]
        # 判断是否已达成
        get_flag = cache.achievement.achievement_dict.get(achievement_cid, False)
        if get_flag:
            achievement_text = "●"
            draw_style = 'standard'
            # 特殊成就特殊标志
            if achievement_data.special:
                achievement_text = "★"
                draw_style = 'gold_enrod'
        else:
            achievement_text = "○"
            draw_style = 'deep_gray'

        achievement_name = achievement_data.name
        achievement_description = achievement_data.description
        achievement_text += f"{achievement_name}：{achievement_description}"
        # 绘制
        achievement_draw = draw.NormalDraw()
        achievement_draw.text = achievement_text
        achievement_draw.style = draw_style
        self.draw_text = ""
        self.now_draw = achievement_draw
        """ 绘制的对象 """

    def draw(self):
        """绘制对象"""
        self.now_draw.draw()
