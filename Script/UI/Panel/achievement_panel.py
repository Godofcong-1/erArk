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

def achievement_flow(achievement_type: str, achievement_id: int = 0):
    """
    成就系统流程\n
    输入：\n
    - achievement_type: str，成就类型\n
    - achievement_id: int，强制成功的成就ID（默认为0）\n
    功能：根据类型结算成就并绘制获得提示
    """
    pl_character_data: game_type.Character = cache.character_data[0]
    # 成就类型与结算函数的映射字典
    achievement_type_func_dict = {
        _("关系"): settle_chara_relationship,
        _("收藏服装"): settle_chara_clothing,
        _("技能"): settle_chara_ability,
        _("催眠"): settle_chara_hypnosis,
    }
    # 统计载具数量
    vehicles_count = 0
    for cid in cache.rhodes_island.vehicles:
        vehicles_count += cache.rhodes_island.vehicles[cid][0]
    # 成就类型与结算值的映射字典
    achievement_type_value_dict = {
        _("周目"): [cache.game_round, [1, 2]],
        _("招募"): [cache.achievement.recruit_count, [101, 102]],
        _("访客"): [cache.achievement.visitor_count, [111, 112]],
        _("囚犯"): [len(cache.rhodes_island.current_prisoners), [121, 122]],
        _("龙门币"): [cache.rhodes_island.materials_resouce[1], [201, 202, 203]],
        _("购买道具"): [len(cache.achievement.buy_item_count_list), [211, 212]],
        _("外勤"): [cache.achievement.field_commission_count, [301, 302, 303]],
        _("载具"): [vehicles_count, [311, 312]],
        _("维修"): [cache.achievement.equipment_repair_count, [321, 322, 323]],
        _("保养"): [cache.achievement.equipment_maintenance_count, [331, 332, 333]],
        _("锻炼"): [min(pl_character_data.hit_point_max, pl_character_data.mana_point_max), [401, 402, 403]],
        _("时停"): [cache.achievement.time_stop_duration, [601, 602, 603]],
        _("生育"): [len(pl_character_data.relationship.child_id_list), [701, 702, 703]],
        _("生产"): [cache.achievement.production_count, [801, 802, 803]],
        _("种植"): [cache.achievement.harvest_count, [811, 812, 813]],
        _("公务"): [cache.achievement.handle_official_business_count, [1001, 1002, 1003]],
        _("读书"): [cache.achievement.read_book_count, [1011, 1012, 1013]],
        _("烹饪"): [cache.achievement.make_food_count, [1021, 1022, 1023]],
        _("礼物"): [cache.achievement.gift_count, [1031, 1032]],
        _("身体检查"): [cache.achievement.health_check_count, [1041, 1042, 1043]],
        _("体检报告"): [len(cache.achievement.body_report_chara_count_list), [1051, 1052]],
        _("调香"): [cache.achievement.aromatherapy_count, [1061, 1062]],
    }
    # 根据类型获取对应的结算函数
    func = achievement_type_func_dict.get(achievement_type, None)
    # 如果是其他类型，则使用结算值进行结算
    judge_value, achievement_ids = achievement_type_value_dict.get(achievement_type, (None, None))
    achievement_id_list = []
    # 如果成就id不为0，则强制结算该成就
    if achievement_id != 0:
        achievement_id_list = settle_achievement(1, achievement_id, force=True)
    # 如果有对应的结算函数，则调用它
    elif func is not None:
        achievement_id_list = func()
    # 如果有对应的结算值，则使用settle_achievement进行结算
    elif judge_value is not None and achievement_ids is not None:
        achievement_id_list = settle_achievement(judge_value, achievement_ids)
    # 绘制成就获得提示
    draw_achievement_notice(achievement_id_list)

def settle_achievement(judge_value: int, achievement_ids, force: bool = False):
    """
    通用成就结算函数（支持单个或批量）\n
    输入：\n
    - judge_value: int，判断值\n
    - achievement_ids: int 或 list[int]，成就ID或成就ID列表\n
    - force: bool，是否强制结算成功（默认为False）\n
    返回：\n
    - return_list: 成就列表，包含已达成的成就ID\n
    功能：判断是否达成成就，如果达成则更新缓存中的成就
    """
    # 如果achievement_ids是单个成就ID，则转换为列表
    if isinstance(achievement_ids, int):
        achievement_ids = [achievement_ids]
    return_list = []
    # 遍历成就ID列表
    for achievement_id in achievement_ids:
        # 需要未达成该成就
        if not cache.achievement.achievement_dict.get(achievement_id, False):
            # 强制结算或判断值满足条件
            if force or judge_value >= game_config.config_achievement[achievement_id].value:
                cache.achievement.achievement_dict[achievement_id] = True
                return_list.append(achievement_id)
    return return_list

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

def settle_chara_relationship():
    """
    结算角色关系类的成就\n
    返回：\n
    - return_list: 成就列表，包含已达成的成就ID
    """
    # 统计各类关系成就的判断值
    love_flag, obey_flag = 0, 0  # 是否有爱情/隶属线路
    lover_count, slave_count = 0, 0      # 爱侣人数与奴隶人数
    for chara_id in cache.character_data:
        # 跳过非角色
        if chara_id == 0:
            continue
        # 跳过不在当前角色列表也不在异常状态7中的
        if chara_id not in cache.npc_id_got and handle_premise.handle_normal_7(chara_id):
            continue
        # 有爱情系陷落
        if not love_flag and handle_premise.handle_self_fall_love(chara_id):
            love_flag = 1
        # 有隶属系陷落
        if not obey_flag and handle_premise.handle_self_fall_obey(chara_id):
            obey_flag = 1
        # 计算爱侣人数
        if handle_premise.handle_self_love_4(chara_id):
            lover_count += 1
        # 计算奴隶人数
        if handle_premise.handle_self_obey_4(chara_id):
            slave_count += 1
    # 构建成就结算列表
    achievement_checks = [
        # (判断值, 成就ID)
        (love_flag, 51),   # 首次爱情线路
        (lover_count, 52),      # 首个爱侣
        (lover_count, 53),      # 爱侣人数100
        (obey_flag, 61),   # 首次隶属线路
        (slave_count, 62),      # 首个奴隶
        (slave_count, 63),      # 奴隶人数100
    ]
    return_list = []
    # 统一调用settle_achievement进行批量结算
    for judge_value, achievement_id in achievement_checks:
        return_list.extend(settle_achievement(judge_value, achievement_id))
    return return_list

def settle_chara_clothing():
    """
    结算角色服装类的成就\n
    返回：\n
    - return_list: 成就列表，包含已达成的成就ID
    """
    return_list = []
    # 统计服装数量
    clothing_count = 0
    pl_character_data: game_type.Character = cache.character_data[0]
    # 统计干员服装数量
    for chara_id in pl_character_data.pl_collection.first_panties:
        clothing_count += len(pl_character_data.pl_collection.first_panties[chara_id])
    for chara_id in pl_character_data.pl_collection.npc_panties:
        clothing_count += len(pl_character_data.pl_collection.npc_panties[chara_id])
    for chara_id in pl_character_data.pl_collection.npc_socks:
        clothing_count += len(pl_character_data.pl_collection.npc_socks[chara_id])
    # 构建成就结算列表
    return_list = settle_achievement(clothing_count, [221, 222, 223])
    return return_list

def settle_chara_ability():
    """
    结算角色能力类的成就\n
    返回：\n
    - return_list: 成就列表，包含已达成的成就ID
    """
    return_list = []
    pl_character_data: game_type.Character = cache.character_data[0]
    
    # 构建成就结算列表
    achievement_checks = [
        # (判断值, 成就ID)
        (pl_character_data.ability[40], 501),
        (pl_character_data.ability[40], 502),
        (pl_character_data.ability[40], 503),
        (pl_character_data.ability[41], 506),
        (pl_character_data.ability[41], 507),
        (pl_character_data.ability[41], 508),
        (pl_character_data.ability[42], 511),
        (pl_character_data.ability[42], 512),
        (pl_character_data.ability[42], 513),
        (pl_character_data.ability[43], 516),
        (pl_character_data.ability[43], 517),
        (pl_character_data.ability[43], 518),
        (pl_character_data.ability[44], 521),
        (pl_character_data.ability[44], 522),
        (pl_character_data.ability[44], 523),
        (pl_character_data.ability[45], 526),
        (pl_character_data.ability[45], 527),
        (pl_character_data.ability[45], 528),
        (pl_character_data.ability[46], 531),
        (pl_character_data.ability[46], 532),
        (pl_character_data.ability[46], 533),
        (pl_character_data.ability[47], 536),
        (pl_character_data.ability[47], 537),
        (pl_character_data.ability[47], 538),
        (pl_character_data.ability[48], 541),
        (pl_character_data.ability[48], 542),
        (pl_character_data.ability[48], 543),
        (pl_character_data.ability[49], 546),
        (pl_character_data.ability[49], 547),
        (pl_character_data.ability[49], 548),
    ]
    # 统一调用settle_achievement进行批量结算
    for judge_value, achievement_id in achievement_checks:
        return_list.extend(settle_achievement(judge_value, achievement_id))
    return return_list

def settle_chara_hypnosis():
    """
    结算催眠类的成就\n
    返回：\n
    - return_list: 成就列表，包含已达成的成就ID
    """
    return_list = []
    # 已催眠角色
    hypnosis_flag = 0
    # 完全催眠的角色数量
    full_hypnosis_count = 0
    for chara_id in cache.character_data:
        # 跳过非角色
        if chara_id == 0:
            continue
        # 跳过不在当前角色列表也不在异常状态7中的
        if chara_id not in cache.npc_id_got and handle_premise.handle_normal_7(chara_id):
            continue
        # 角色被催眠
        if not hypnosis_flag and handle_premise.handle_self_hypnosis_ne_0(chara_id):
            hypnosis_flag = 1
        # 角色完全催眠
        if handle_premise.handle_self_has_been_complete_hypnosis(chara_id):
            full_hypnosis_count += 1

    # 构建成就结算列表
    achievement_checks = [
        # (判断值, 成就ID)
        (hypnosis_flag, 621),  # 首次催眠
        (full_hypnosis_count, 622),  # 完全催眠人数1
        (full_hypnosis_count, 623),  # 完全催眠人数50
    ]
    # 统一调用settle_achievement进行批量结算
    for judge_value, achievement_id in achievement_checks:
        return_list.extend(settle_achievement(judge_value, achievement_id))
    return return_list


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
