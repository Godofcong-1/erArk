from typing import List
from types import FunctionType
import random
from Script.Core import cache_control, game_type, get_text, flow_handle
from Script.Design import handle_talent, map_handle, attr_calculation
from Script.UI.Moudle import draw
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

unconscious_list = [_("无"),_("睡眠"),_("醉酒"),_("时停"),_("平然催眠"),_("空气催眠"),_("体控催眠"),_("心控催眠")]
""" 无意识状态列表 """

def calculate_hypnosis_sanity_cost(character_id: int) -> int:
    """
    计算催眠所需的理智消耗
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 预计会消耗的理智值
    """
    character_data: game_type.Character = cache.character_data[character_id]
    base_cost = 10
    if character_data.talent[73]:
        return 1
    elif character_data.talent[72]:
        return base_cost + 20
    elif character_data.talent[71]:
        return base_cost + 15
    else:
        return base_cost + 10

def hypnosis_degree_calculation(target_character_id: int) -> float:
    """
    计算催眠的增长程度
    Keyword arguments:
    target_character_id -- 角色id
    Return arguments:
    float -- 催眠增长值
    """
    pl_character_data: game_type.Character = cache.character_data[0]
    target_character_data: game_type.Character = cache.character_data[target_character_id]

    if target_character_id == 0:
        return 0

    # 如果已经达到当前玩家的能力上限，则不再增加
    hypnosis_degree_limit = hypnosis_degree_limit_calculation()
    if target_character_data.hypnosis.hypnosis_degree >= hypnosis_degree_limit:
        return 0

    base_addition = 1

    # 根据玩家的催眠能力，计算催眠增长系数
    hypnosis_degree_adjust = 2
    if pl_character_data.talent[334]:
        hypnosis_degree_adjust = 6
    elif pl_character_data.talent[333]:
        hypnosis_degree_adjust = 4

    # 调香的加成
    if target_character_data.sp_flag.aromatherapy == 6:
        hypnosis_degree_adjust += 5

    # 根据无觉刻印的等级，计算催眠增长系数
    hypnosis_degree_adjust *= attr_calculation.get_ability_adjust(target_character_data.ability[19])

    # 乘以0.5~1.5的随机系数
    hypnosis_degree_adjust *= random.uniform(0.5, 1.5)

    # 最后计算
    final_addition = base_addition * hypnosis_degree_adjust
    # 限制为1位小数
    final_addition = round(final_addition, 1)
    # print(f"debug final_addition = {final_addition}")

    return final_addition

def hypnosis_degree_limit_calculation() -> int:
    """
    计算催眠的上限
    Keyword arguments:
    target_character_id -- 角色id
    Return arguments:
    int -- 催眠上限
    """
    pl_character_data: game_type.Character = cache.character_data[0]

    # 如果已经达到当前玩家的能力上限，则不再增加
    hypnosis_degree_limit = 0
    for cid in game_config.config_hypnosis_talent_of_pl:
        hypnosis_data = game_config.config_hypnosis_talent_of_pl[cid]
        if pl_character_data.talent[hypnosis_data.hypnosis_talent_id]:
            hypnosis_degree_limit = max(hypnosis_degree_limit, hypnosis_data.max_hypnosis_degree)

    return hypnosis_degree_limit

def evaluate_hypnosis_completion(character_id: int):
    """
    判断与结算催眠完成\n
    Keyword arguments:\n
    character_id -- 角色id\n
    Return arguments:\n
    int -- 1完成，0未完成\n
    """
    pl_character_data: game_type.Character = cache.character_data[0]
    character_data: game_type.Character = cache.character_data[character_id]
    # 进行素质获得检测
    handle_talent.npc_gain_hypnosis_talent(character_id)
    # 计算催眠完成度
    now_hypnosis_type = pl_character_data.pl_ability.hypnosis_type
    hypnosis_degree_need = game_config.config_hypnosis_type[now_hypnosis_type].hypnosis_degree
    # 催眠完成，开始结算
    if character_data.hypnosis.hypnosis_degree >= hypnosis_degree_need:
        # 空气催眠
        if now_hypnosis_type == 2:
            # 限制为需要锁门的地点，并强制锁门
            now_position = pl_character_data.position
            now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
            now_scene_data = cache.scene_data[now_scene_str]
            if now_scene_data.close_type != 1:
                now_draw = draw.WaitDraw()
                draw_text = _("\n当前地点不能锁门，无法进行空气催眠\n")
                now_draw.text = draw_text
                now_draw.draw()
                return 0
            elif cache.scene_data[now_scene_str].close_flag == 0:
                cache.scene_data[now_scene_str].close_flag = now_scene_data.close_type
                now_draw = draw.WaitDraw()
                draw_text = _("\n为了防止有人打扰，将门锁上了\n")
                now_draw.text = draw_text
                now_draw.draw()
            # 更新记录当前地点
            pl_character_data.pl_ability.air_hypnosis_position = pl_character_data.position
        if now_hypnosis_type != 0:
            character_data.sp_flag.unconscious_h = now_hypnosis_type + 3
        else:
            character_data.sp_flag.unconscious_h = 0
        # print(f"debug {character_data.name} unconscious_h = {character_data.sp_flag.unconscious_h}")
        return 1
    # 未完成催眠
    else:
        now_draw = draw.NormalDraw()
        draw_text = _("\n{0}的催眠深度未达到{1}%，无法进入{2}催眠状态，需要切换更低的催眠模式或加深催眠程度\n").format(character_data.name, hypnosis_degree_need, game_config.config_hypnosis_type[now_hypnosis_type].name)
        now_draw.text = draw_text
        now_draw.draw()
        return 0


class Chose_Hypnosis_Type_Panel:
    """
    用于选择催眠类型的面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int, instruct_flag: bool = False):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.instruct_flag: bool = instruct_flag
        """ 是否为指令模式 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """

    def draw(self):
        """绘制对象"""

        title_text = _("选择催眠类型")
        title_draw = draw.TitleLineDraw(title_text, self.width)
        while 1:
            return_list = []
            title_draw.draw()
            pl_character_data: game_type.Character = cache.character_data[0]
            target_character_data: game_type.Character = cache.character_data[pl_character_data.target_character_id]

            info_draw = draw.NormalDraw()
            info_text = ""

            info_text += _("\n○进行催眠时会消耗理智，催眠结束后会自动合理化催眠过程中的记忆，未被催眠的干员也不会对催眠中的行为起疑\n")
            if pl_character_data.target_character_id > 0:
                info_text += _("○当前催眠对象：{0}，催眠深度：{1}%\n").format(target_character_data.name, target_character_data.hypnosis.hypnosis_degree)
            info_text += _("\n催眠系能力：\n")
            # 催眠能力
            info_draw.text = _(info_text)
            info_draw.draw()
            for cid in game_config.config_hypnosis_talent_of_pl:
                hypnosis_data = game_config.config_hypnosis_talent_of_pl[cid]
                talent_id = hypnosis_data.hypnosis_talent_id
                max_degree = hypnosis_data.max_hypnosis_degree
                talent_name = game_config.config_talent[talent_id].name
                talent_info = game_config.config_talent[talent_id].info
                draw_text = _("  {0}(最高催眠深度{1}%)：{2}\n").format(talent_name, max_degree, talent_info)
                now_draw = draw.NormalDraw()
                if not pl_character_data.talent[talent_id]:
                    draw_text = _("  {0}(未解锁)：{1}\n").format(talent_name, talent_info)
                    now_draw.style = "deep_gray"
                now_draw.text = _(draw_text)
                now_draw.draw()
            # 催眠类型
            info_text = _("\n可用的催眠类型：\n")
            info_draw.text = _(info_text)
            info_draw.draw()
            for cid in game_config.config_hypnosis_type:
                hypnosis_type_data = game_config.config_hypnosis_type[cid]
                draw_text = f"  [{hypnosis_type_data.name}]"
                draw_text += _("(需要[{0}]，且催眠深度达到{1}%)").format(game_config.config_talent[hypnosis_type_data.talent_id].name, hypnosis_type_data.hypnosis_degree)
                draw_text += f"：{hypnosis_type_data.introduce}"
                # 已解锁则绘制按钮，需要已有该能力，且当前没有对象，或有对象且该对象催眠深度达到要求
                if (
                    pl_character_data.talent[hypnosis_type_data.talent_id] 
                    and (
                        pl_character_data.target_character_id == 0 or 
                         (pl_character_data.target_character_id > 0 and target_character_data.hypnosis.hypnosis_degree >= hypnosis_type_data.hypnosis_degree)
                         )
                    ):
                    button_draw = draw.LeftButton(
                        _(draw_text),
                        _(hypnosis_type_data.name),
                        window_width,
                        cmd_func=self.change_hypnosis_type,
                        args=(cid,),
                    )
                    return_list.append(button_draw.return_text)
                    button_draw.draw()
                    line_feed.draw()
                # 未解锁则绘制灰色文本
                else:
                    now_draw = draw.NormalDraw()
                    draw_text += f"\n"
                    now_draw.text = _(draw_text)
                    now_draw.style = "deep_gray"
                    now_draw.draw()

            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn in return_list:
                break

    def change_hypnosis_type(self, hypnosis_type_cid):
        """改变当前的催眠类型"""
        pl_character_data: game_type.Character = cache.character_data[0]
        pl_character_data.pl_ability.hypnosis_type = hypnosis_type_cid
        target_data: game_type.Character = cache.character_data[pl_character_data.target_character_id]
        line_draw = draw.LineDraw("-", self.width)
        line_draw.draw()

        if hypnosis_type_cid > 0:
            hypnosis_type_name = game_config.config_hypnosis_type[hypnosis_type_cid].name
            now_draw = draw.WaitDraw()
            draw_text = _("\n已切换为{0}催眠模式\n\n").format(hypnosis_type_name)
            now_draw.style = "pink"
            now_draw.text = draw_text
            now_draw.draw()
            # 如果当前有交互对象
            if self.instruct_flag and pl_character_data.target_character_id:
                now_draw = draw.WaitDraw()
                now_draw.style = "pink"
                if hypnosis_type_cid == 1:
                    draw_text = _("\n{0}会理所当然地接受{1}的不合理行为了\n\n").format(target_data.name, pl_character_data.name)
                    now_draw.text = draw_text
                    now_draw.draw()
                elif hypnosis_type_cid == 2:
                    draw_text = _("\n{0}会把{1}视为空气了\n\n").format(target_data.name, pl_character_data.name)
                    now_draw.text = draw_text
                    now_draw.draw()
                elif hypnosis_type_cid == 3:
                    draw_text = _("\n{0}可以随意地操纵{1}的身体了\n\n").format(pl_character_data.name, target_data.name)
                    now_draw.text = draw_text
                    now_draw.draw()
                    self.body_or_mind_control_option(0)
                elif hypnosis_type_cid == 4:
                    draw_text = _("\n{0}可以向{1}的潜意识灌输指令了\n\n").format(pl_character_data.name, target_data.name)
                    now_draw.text = draw_text
                    now_draw.draw()
                    self.body_or_mind_control_option(1)

    def body_or_mind_control_option(self, body_or_mind_flag = 0):
        """
        身体或心灵的控制选项
        Keyword arguments:
        body_or_mind_flag -- 0为身体控制，1为心灵控制
        """
        pl_character_data: game_type.Character = cache.character_data[0]
        target_data: game_type.Character = cache.character_data[pl_character_data.target_character_id]
        range_list = []
        for cid in game_config.config_behavior:
            behavior_data = game_config.config_behavior[cid]
            if body_or_mind_flag == 0:
                type_text = _("身体")
                if "体控" in behavior_data.tag:
                    range_list.append(cid)
            else:
                type_text = _("心灵")
                if "心控" in behavior_data.tag:
                    range_list.append(cid)
        while 1:
            return_list = []
            title_draw = draw.TitleLineDraw(_("选择{0}控制选项").format(type_text), self.width)
            title_draw.draw()
            info_draw = draw.NormalDraw()
            info_text = _("\n可以对{0}使用的控制指令：\n\n").format(target_data.name)
            info_draw.text = info_text
            info_draw.draw()
            # 遍历选项数据库，输出按钮
            count = 0
            for cid in range_list:
                # 如果不存在该选项则跳过
                if cid not in game_config.config_behavior:
                    continue
                behavior_data = game_config.config_behavior[cid]
                draw_text = f"[{count}]{behavior_data.name}"
                button_draw = draw.LeftButton(
                    _(draw_text),
                    _(behavior_data.name),
                    window_width,
                    cmd_func=self.son_instruct,
                    args=(cid,),
                )
                return_list.append(button_draw.return_text)
                button_draw.draw()
                line_feed.draw()
                count += 1
            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn in return_list:
                break

    def son_instruct(self, cid):
        """进行子选项"""
        from Script.Design import handle_instruct
        line_draw = draw.LineDraw("-", self.width)
        line_draw.draw()

        # 心控-角色扮演需要单独绘制面板
        if cid == "hypnosis_roleplay":
            now_draw = Chose_Roleplay_Type_Panel(self.width)
            now_draw.draw()
            character_data: game_type.Character = cache.character_data[0]
            target_data: game_type.Character = cache.character_data[character_data.target_character_id]
            if len(target_data.hypnosis.roleplay) != 0:
                handle_instruct.chara_handle_instruct_common_settle(cid)
        else:
            handle_instruct.chara_handle_instruct_common_settle(cid)

class Chose_Roleplay_Type_Panel:
    """
    用于选择心控催眠-角色扮演的面板对象
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

        title_text = _("选择角色扮演类型")
        title_draw = draw.TitleLineDraw(title_text, self.width)
        while 1:
            return_list = []
            title_draw.draw()
            pl_character_data: game_type.Character = cache.character_data[0]
            target_data: game_type.Character = cache.character_data[pl_character_data.target_character_id]
            info_draw = draw.NormalDraw()
            info_text = _("\n○被催眠后会完全带入对应的角色或场景，直到催眠解除为止\n")
            info_text += _("  （当前版本中，该催眠的文本对应较少，仅有功能和数值上的效果）\n")
            info_text += _("\n  要催眠为哪一种角色扮演呢？")
            info_text += _("（当前为：")

            # 如果当前没有角色扮演则显示无
            if len(target_data.hypnosis.roleplay) == 0:
                info_text += _("无）\n")
            # 如果有角色扮演则遍历输出
            else:
                # 先排序角色扮演ID
                target_data.hypnosis.roleplay.sort()
                # 遍历角色扮演ID，输出对应的名称
                for role_play_cid in target_data.hypnosis.roleplay:
                    # 如果角色扮演ID不存在则跳过
                    if role_play_cid not in game_config.config_roleplay:
                        continue
                    role_play_cid_data = game_config.config_roleplay[role_play_cid]
                    # 如果角色扮演名称为无则跳过
                    if role_play_cid_data.name == _("无"):
                        continue
                    info_text += _("{0} ").format(role_play_cid_data.name)
                # 输出结束括号
                info_text += "）\n"
            info_draw.text = info_text
            info_draw.draw()
            line_feed.draw()

            # 遍历角色扮演数据库，输出按钮
            for cid in game_config.config_roleplay:
                if cid == 0:
                    continue
                roleplay_data = game_config.config_roleplay[cid]
                draw_text = f"[{cid}]{roleplay_data.name}"
                button_draw = draw.LeftButton(
                    _(draw_text),
                    _(roleplay_data.name),
                    window_width,
                    cmd_func=self.choose_this_type,
                    args=(cid,),
                )
                return_list.append(button_draw.return_text)
                button_draw.draw()
                line_feed.draw()

            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn in return_list:
                break

    def choose_this_type(self, cid):
        """选择该类型"""
        pl_character_data: game_type.Character = cache.character_data[0]
        target_data: game_type.Character = cache.character_data[pl_character_data.target_character_id]
        if cid not in game_config.config_roleplay:
            return
        if cid not in target_data.hypnosis.roleplay:
            target_data.hypnosis.roleplay.append(cid)
            # 绘制提示信息
            info_draw = draw.WaitDraw()
            info_draw.style = "purple"
            info_text = _("\n{0}被催眠了，开始进行{1}的扮演\n\n").format(target_data.name, game_config.config_roleplay[cid].name)
            info_draw.text = info_text
            info_draw.draw()
        else:
            target_data.hypnosis.roleplay.remove(cid)
            # 绘制提示信息
            info_draw = draw.WaitDraw()
            info_draw.style = "purple"
            info_text = _("\n{0}停止进行{1}的扮演了\n\n").format(target_data.name, game_config.config_roleplay[cid].name)
            info_draw.text = info_text
            info_draw.draw()
