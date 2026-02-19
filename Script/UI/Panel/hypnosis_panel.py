from typing import List
from types import FunctionType
import random
from Script.Core import cache_control, game_type, get_text, flow_handle, constant
from Script.Design import handle_premise, handle_talent, map_handle, handle_ability
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
    hypnosis_degree_adjust *= handle_ability.get_ability_adjust(target_character_data.ability[19])

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
        handle_premise.settle_chara_unnormal_flag(character_id, 5)
        handle_premise.settle_chara_unnormal_flag(character_id, 6)
        # print(f"debug {character_data.name} unconscious_h = {character_data.sp_flag.unconscious_h}")
        return 1
    # 未完成催眠
    else:
        now_draw = draw.NormalDraw()
        draw_text = _("\n{0}的催眠深度未达到{1}%，无法进入{2}催眠状态，需要切换更低的催眠模式或加深催眠程度\n").format(character_data.name, hypnosis_degree_need, game_config.config_hypnosis_type[now_hypnosis_type].name)
        now_draw.text = draw_text
        now_draw.draw()
        return 0

def get_hypnosis_degree_color(hypnosis_degree: float) -> str:
    """
    输入催眠等级，输出角色催眠状态对应的字体颜色
    参数:
        hypnosis_degree (float): 催眠等级
    输出:
        str: 催眠等级对应的字体颜色
    功能:
        根据角色的催眠等级返回对应的字体颜色字符串
    """
    if hypnosis_degree == 0:
        font_color = "standard"
    elif hypnosis_degree < 50:
        font_color = "pink"
    elif hypnosis_degree < 100:
        font_color = "hot_pink"
    elif hypnosis_degree < 200:
        font_color = "deep_pink"
    else:
        font_color = "purple"
    return font_color

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
                cache.now_panel_id = constant.Panel.IN_SCENE
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
        for behavbior_cid in game_config.config_behavior:
            behavior_data = game_config.config_behavior[behavbior_cid]
            if body_or_mind_flag == 0:
                type_text = _("身体")
                if "体控" in behavior_data.tag:
                    range_list.append(behavbior_cid)
            else:
                type_text = _("心灵")
                if "心控" in behavior_data.tag:
                    range_list.append(behavbior_cid)
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
            for behavbior_cid in range_list:
                # 如果不存在该选项则跳过
                if behavbior_cid not in game_config.config_behavior:
                    continue
                behavior_data = game_config.config_behavior[behavbior_cid]
                sub_type_id = game_config.config_hypnosis_sub_type_by_behaivor.get(behavbior_cid, 0)
                draw_text = f"[{count}]{behavior_data.name}"
                if sub_type_id > 0:
                    sub_type_data = game_config.config_hypnosis_sub_type[sub_type_id]
                    draw_text += f"：{sub_type_data.introduce}"
                button_draw = draw.LeftButton(
                    _(draw_text),
                    _(behavior_data.name),
                    window_width,
                    cmd_func=self.son_instruct,
                    args=(behavbior_cid,),
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

    def son_instruct(self, behavbior_cid):
        """进行子选项"""
        from Script.System.Instruct_System import handle_instruct
        line_draw = draw.LineDraw("-", self.width)
        line_draw.draw()

        # 心控-角色扮演需要单独绘制面板
        if behavbior_cid == "hypnosis_roleplay":
            now_draw = Chose_Roleplay_Type_Panel(self.width)
            now_draw.draw()
            character_data: game_type.Character = cache.character_data[0]
            target_data: game_type.Character = cache.character_data[character_data.target_character_id]
            if len(target_data.hypnosis.roleplay) != 0:
                handle_instruct.chara_handle_instruct_common_settle(behavbior_cid)
        else:
            # 如果是强制排卵，则检测是否满足条件
            if behavbior_cid == "hypnosis_force_ovulation":
                if handle_premise.handle_t_reproduction_period_3(0) or handle_premise.handle_t_fertilization_or_pregnancy(0):
                    now_draw = draw.WaitDraw()
                    now_draw.text = _("\n当前干员不满足条件，无法进行强制排卵\n")
                    now_draw.draw()
                    return

            handle_instruct.chara_handle_instruct_common_settle(behavbior_cid)

class Chose_Roleplay_Type_Panel:
    """
    用于选择心控催眠-角色扮演的面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """
        初始化绘制对象
        参数：
            width (int): 绘制的最大宽度
        输出：
            None
        功能：
            初始化面板宽度、文本列表和类型展开标志
        """
        self.width: int = width
        # 绘制的最大宽度
        self.draw_list: List[draw.NormalDraw] = []
        # 绘制的文本列表
        # 统计所有type类型，初始化展开标志为False（收起）
        self.type_expand_flag = {}
        # 获取所有type类型，保持顺序，并将sub_type为"特殊"的归为特殊类
        type_list = []  # 用于存储普通类型，保持顺序
        special_type = _("特殊")
        has_special = False
        for cid in game_config.config_roleplay:
            if cid == 0:
                continue
            roleplay_data = game_config.config_roleplay[cid]
            # 判断是否为特殊类
            if roleplay_data.sub_type == special_type:
                has_special = True
                continue
            # 普通类型按顺序加入
            if roleplay_data.type not in type_list:
                type_list.append(roleplay_data.type)
        # 初始化普通类型的flag
        for t in type_list:
            self.type_expand_flag[t] = False
        # 如果有特殊类，添加特殊类flag
        if has_special:
            self.type_expand_flag[special_type] = False
        # 保存type_list和特殊类名，供draw使用
        self.type_list = type_list
        self.special_type = special_type
        self.has_special = has_special
        # 初始化角色扮演选择缓存
        self.selected_roleplay_cache = []
        pl_character_data: game_type.Character = cache.character_data[0]
        target_data: game_type.Character = cache.character_data[pl_character_data.target_character_id]
        # 如果对方有角色扮演数据，则将其缓存到selected_roleplay_cache中
        if len(target_data.hypnosis.roleplay):
            self.selected_roleplay_cache = target_data.hypnosis.roleplay[:]

    def draw(self):
        """
        绘制对象
        输入：无
        输出：无
        功能：
            绘制角色扮演类型选择界面，支持按类型展开/收起
        """
        title_text = _("选择角色扮演类型")
        title_draw = draw.TitleLineDraw(title_text, self.width)
        while 1:
            return_list = []
            title_draw.draw()
            info_draw = draw.NormalDraw()
            info_text = _("\n○被催眠后会完全带入对应的角色或场景，直到催眠解除为止\n")
            info_text += _("○非特殊类里，每类可各选一个，同时起效\n")
            info_text += _("○特殊类与其他催眠相冲突，只能单独起效\n")
            info_text += _("  （当前版本中，该催眠的文本对应较少，仅有功能和数值上的效果）\n")
            info_text += _("\n  要催眠为哪一种角色扮演呢？")
            info_text += _("（当前为：")

            # 显示缓存中的内容
            if len(self.selected_roleplay_cache) == 0:
                info_text += _("无）\n")
            # 如果有角色扮演则遍历输出
            else:
                self.selected_roleplay_cache.sort()
                for role_play_cid in self.selected_roleplay_cache:
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

            # 构建type到cid的映射，特殊类单独处理
            type_dict = {}
            special_type = self.special_type
            for t in self.type_list:
                type_dict[t] = []
            if self.has_special:
                type_dict[special_type] = []
            for cid in game_config.config_roleplay:
                if cid == 0:
                    continue
                roleplay_data = game_config.config_roleplay[cid]
                # 特殊类归入特殊
                if roleplay_data.sub_type == special_type:
                    if self.has_special:
                        type_dict[special_type].append(cid)
                else:
                    if roleplay_data.type in type_dict:
                        type_dict[roleplay_data.type].append(cid)

            # 检查当前已选的特殊类cid
            selected_special_cid = None
            for cid in self.selected_roleplay_cache:
                if cid in type_dict.get(special_type, []):
                    selected_special_cid = cid
                    break

            # 记录每个普通类型已选的cid
            selected_type_cid = {}
            for t in self.type_list:
                for cid in type_dict[t]:
                    if cid in self.selected_roleplay_cache:
                        selected_type_cid[t] = cid
                        break

            # 按type_list顺序绘制普通类型
            for t in self.type_list:
                line_feed.draw()
                # 按类型绘制展开/收起按钮
                if self.type_expand_flag.get(t, False):
                    btn_text = f"▼{t}"
                else:
                    btn_text = f"▶{t}"
                button_draw = draw.LeftButton(
                    _(btn_text),
                    _(btn_text),
                    window_width / 4,
                    cmd_func=self.toggle_type_expand,
                    args=(t,),
                )
                return_list.append(button_draw.return_text)
                button_draw.draw()
                line_feed.draw()
                # 如果该类型已展开，绘制该类型下的所有角色扮演选项
                if self.type_expand_flag.get(t, False):
                    count = 0
                    for cid in type_dict[t]:
                        roleplay_data = game_config.config_roleplay[cid]
                        can_select = self.judge_can_select(cid, selected_special_cid, selected_type_cid, t, self.selected_roleplay_cache)
                        # 可选（未选或是已选项）
                        if can_select or cid in self.selected_roleplay_cache:
                            draw_text = f"[{cid}]"
                            # 有子类则在前缀显示子类
                            if roleplay_data.sub_type != _("无"):
                                draw_text += f"({roleplay_data.sub_type})"
                            draw_text += roleplay_data.name
                            draw_style = "standard"
                            if cid in self.selected_roleplay_cache:
                                # 如果是已选项，则显示为已选
                                draw_style = "gold_enrod"
                                draw_text += _("(已选)")
                            button_draw = draw.LeftButton(
                                _(draw_text),
                                _(roleplay_data.name),
                                window_width / 5,
                                normal_style=draw_style,
                                cmd_func=self.choose_this_type,
                                args=(cid,),
                            )
                            return_list.append(button_draw.return_text)
                            button_draw.draw()
                        # 不可选（已选特殊类或是其他已选项）
                        else:
                            draw_text = f"[{cid}]"
                            if roleplay_data.sub_type != _("无"):
                                draw_text += f"({roleplay_data.sub_type})"
                            draw_text += roleplay_data.name
                            now_draw = draw.LeftDraw()
                            now_draw.text = _(draw_text)
                            now_draw.style = "deep_gray"
                            now_draw.width = window_width / 5
                            now_draw.draw()
                        # 每5个选项后换行
                        count += 1
                        if count % 5 == 0:
                            line_feed.draw()
                    line_feed.draw()
            # 最后绘制特殊类
            if self.has_special:
                line_feed.draw()
                t = special_type
                if self.type_expand_flag.get(t, False):
                    btn_text = f"▼{t}"
                else:
                    btn_text = f"▶{t}"
                button_draw = draw.LeftButton(
                    _(btn_text),
                    _(btn_text),
                    window_width / 4,
                    cmd_func=self.toggle_type_expand,
                    args=(t,),
                )
                return_list.append(button_draw.return_text)
                button_draw.draw()
                line_feed.draw()
                if self.type_expand_flag.get(t, False):
                    count = 0
                    for cid in type_dict[t]:
                        roleplay_data = game_config.config_roleplay[cid]
                        # 如果已选特殊类，只有已选项可取消
                        if selected_special_cid is not None and cid != selected_special_cid:
                            draw_text = f"[{cid}]{roleplay_data.name}"
                            now_draw = draw.LeftDraw()
                            now_draw.text = _(draw_text)
                            now_draw.style = "deep_gray"
                            now_draw.width = window_width / 5
                            now_draw.draw()
                        else:
                            draw_text = f"[{cid}]{roleplay_data.name}"
                            button_draw = draw.LeftButton(
                                _(draw_text),
                                _(roleplay_data.name),
                                window_width / 5,
                                cmd_func=self.choose_this_type,
                                args=(cid,),
                            )
                            return_list.append(button_draw.return_text)
                            button_draw.draw()
                        # 每5个选项后换行
                        count += 1
                        if count % 5 == 0:
                            line_feed.draw()
                    line_feed.draw()

            line_feed.draw()
            yes_draw = draw.CenterButton(_("[确认]"), _("确认"), window_width / 2)
            return_list.append(yes_draw.return_text)
            if len(self.selected_roleplay_cache):
                yes_draw.draw()
            back_draw = draw.CenterButton(_("[返回]"), _( "返回"), window_width / 2)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == yes_draw.return_text:
                # 结算角色扮演选择
                self.settle_roleplay_selection()
                cache.now_panel_id = constant.Panel.IN_SCENE
                break
            elif yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def toggle_type_expand(self, t):
        """
        切换类型展开/收起状态
        参数：
            t (str): 类型名
        输出：
            None
        功能：
            切换type_expand_flag中对应类型的布尔值
        """
        self.type_expand_flag[t] = not self.type_expand_flag.get(t, False)

    def judge_can_select(self, cid, selected_special_cid, selected_type_cid, t, selected_roleplay_cache):
        """
        判断是否可以选择该角色扮演类型
        参数：
            cid (int): 角色扮演ID
            selected_special_cid (int): 已选的特殊类ID，如果没有则为None
            selected_type_cid (dict): 已选的普通类ID字典，键为类型名，值为已选的角色扮演ID
            t (str): 当前类型名
            selected_roleplay_cache (list): 当前已选的角色扮演ID缓存
        输出：
            bool: 是否可以选择该角色扮演类型
        功能：
            根据当前已选的特殊类和普通类判断是否可以选择该角色扮演类型。
        """
        roleplay_data = game_config.config_roleplay[cid]
        can_select = True
        main_type = roleplay_data.type
        sub_type = roleplay_data.sub_type
        # 如果已选特殊类，则普通类全部不可选
        if selected_special_cid is not None:
            can_select = False
        # 如果该类已选，且cid不是已选的那个，则不可选
        elif t in selected_type_cid and cid != selected_type_cid[t]:
            can_select = False
        # 如果当前子类是非家庭，且已选家庭，则不可选
        if can_select and sub_type == _("非家庭") and selected_type_cid.get(_("家庭"), None) is not None:
            can_select = False
        # 如果当前大类是非职业，且子类是非通用和无
        if can_select and main_type != _("职业") and sub_type not in [_("通用"), _("无")]:
            can_select = False
            # 如果没选职业则不可选
            if selected_type_cid.get(_("职业"), None) is None:
                can_select = False
            else:
                # 遍历已选的职业
                for selected_cid in selected_roleplay_cache:
                    if selected_cid in game_config.config_roleplay and game_config.config_roleplay[selected_cid].type == _("职业"):
                        # 如果当前子类与已选职业的子类相同，则可选
                        if game_config.config_roleplay[selected_cid].sub_type == sub_type:
                            can_select = True
                            break
        # 如果关系是同学的话对方的职业是教师则不可选
        if can_select and roleplay_data.name == _("同学"):
            can_select = True
            for selected_cid in selected_roleplay_cache:
                if selected_cid in game_config.config_roleplay and game_config.config_roleplay[selected_cid].name == _("教师"):
                    can_select = False
                    break
        return can_select

    def choose_this_type(self, cid):
        """
        选择该类型
        参数：
            cid (int): 角色扮演ID
        输出：
            None
        功能：
            选择普通类时，若已选特殊类则先移除特殊类；选择特殊类时，清空所有，仅保留自己。
        """
        if cid not in game_config.config_roleplay:
            return
        # 操作缓存而不是直接操作数据
        if cid not in self.selected_roleplay_cache:
            while 1:
                line = draw.LineDraw("-", self.width)
                line.draw()
                return_list = []
                line_feed.draw()
                role_play_data = game_config.config_roleplay[cid]
                # 处理绘制信息
                info_text = _("\n{0}：{1}\n").format(role_play_data.name, role_play_data.info)
                if role_play_data.type == _("职业") and role_play_data.sub_type != _("无"):
                    info_text += _("进行该扮演后，可进一步选择其他类中带有{0}前缀的子项。\n").format(role_play_data.sub_type)
                info_text += _("是否确定进行该扮演？\n")
                # 绘制提示信息
                info_draw = draw.NormalDraw()
                info_draw.text = info_text
                info_draw.draw()
                line_feed.draw()
                # 绘制确认按钮
                confirm_draw = draw.CenterButton(
                    _("[确认]"),
                    _( "确认"),
                    window_width / 2,
                    cmd_func=self.confirm_roleplay,
                    args=(cid,),
                )
                confirm_draw.draw()
                return_list.append(confirm_draw.return_text)
                # 绘制取消按钮
                cancel_draw = draw.CenterButton(
                    _("[取消]"),
                    _( "取消"),
                    window_width / 2,
                )
                cancel_draw.draw()
                return_list.append(cancel_draw.return_text)
                line_feed.draw()
                # 等待用户选择
                yrn = flow_handle.askfor_all(return_list)
                if yrn in return_list:
                    break
        else:
            self.selected_roleplay_cache.remove(cid)

    def confirm_roleplay(self, cid):
        """
        确认进行角色扮演
        参数：
            cid (int): 角色扮演ID
        输出：
            None
        功能：
            将角色扮演添加到缓存中
        """
        # 新增：只操作缓存，不直接操作数据
        # 获取特殊类cid集合
        special_cids = set()
        special_type = self.special_type
        for scid in game_config.config_roleplay:
            if scid == 0:
                continue
            roleplay_data = game_config.config_roleplay[scid]
            if roleplay_data.sub_type == special_type:
                special_cids.add(scid)
        # 判断是否为特殊类
        if cid in special_cids:
            # 选择特殊类，清空所有，仅保留自己
            self.selected_roleplay_cache.clear()
        # 如果当前是家庭或职业类，则清空所有非家庭或职业类的角色扮演
        roleplay_data = game_config.config_roleplay[cid]
        if roleplay_data.type in [_("家庭"), _( "职业")]:
            # 清空所有非家庭或职业类的角色扮演
            for rid in self.selected_roleplay_cache[:]:
                if rid in game_config.config_roleplay and game_config.config_roleplay[rid].type not in [_("家庭"), _( "职业")]:
                    self.selected_roleplay_cache.remove(rid)
        # 添加角色扮演到缓存
        self.selected_roleplay_cache.append(cid)

    def settle_roleplay_selection(self):
        """
        结算角色扮演选择，将缓存的值赋予到目标角色的催眠状态中
        输入：无
        输出：无
        功能：
            将self.selected_roleplay_cache赋值到target_data.hypnosis.roleplay，并输出提示信息
        """
        pl_character_data: game_type.Character = cache.character_data[0]
        target_data: game_type.Character = cache.character_data[pl_character_data.target_character_id]
        # 赋值缓存到数据
        target_data.hypnosis.roleplay = self.selected_roleplay_cache[:]
        # 输出提示信息
        info_draw = draw.WaitDraw()
        info_draw.style = "purple"
        info_text = _("\n已为{0}开始进行以下的角色扮演了：").format(target_data.name)
        if not target_data.hypnosis.roleplay:
            info_text += _( "无\n")
        else:
            for cid in target_data.hypnosis.roleplay:
                if cid in game_config.config_roleplay:
                    info_text += _("{0} ").format(game_config.config_roleplay[cid].name)
            info_text += "\n"
        info_draw.text = info_text
        info_draw.draw()
