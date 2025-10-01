from typing import List, Tuple
from types import FunctionType
from Script.Core import cache_control, game_type, get_text, flow_handle, constant
from Script.Design import attr_calculation, basement, handle_premise, handle_talent
from Script.UI.Moudle import draw, panel
from Script.Config import game_config, normal_config

import random

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

def recruit_new_chara():
    """
    招募新干员\n
    输入：无\n
    返回：bool，是否招募成功\n
    说明：\n
    - 如果宿舍已满，则提示宿舍不足，无法招募\n
    - 如果有待确认的招募干员，则随机招募一名新干员，并更新缓存数据\n
    - 如果没有待确认的招募干员，则提示没有可招募的干员\n
    """
    from Script.Design import character_handle
    from Script.UI.Panel import achievement_panel
    now_draw = draw.WaitDraw()
    now_draw.width = window_width
    now_draw.style = "gold_enrod"
    now_draw.text = ""

    if len(cache.npc_id_got) >= cache.rhodes_island.people_max:
        now_draw.text += _("\n\n   ※ 空余宿舍不足，无法招募 ※\n\n")
        now_draw.draw()
        return False

    elif len(cache.rhodes_island.recruited_id):
        # 从待招募的干员中选择
        new_chara_id = cache.rhodes_island.recruited_id.pop()
        # 招募该干员
        character_handle.get_new_character(new_chara_id)
        character_data = cache.character_data[new_chara_id]
        now_draw.text += _("\n\n   ※ 成功招募了{0} ※\n\n").format(character_data.name)
        now_draw.draw()
        # 招募成就结算
        achievement_panel.achievement_flow(_("招募"))
        return True
    else:
        return False


def find_recruitable_npc() -> List[int]:
    """
    查找可招募的NPC\n
    Returns：\n
    List[int]: 可招募的NPC列表
    """

    recruitable_npc_id_list = []

    for i in range(len(cache.npc_tem_data)):
        chara_id = i + 1
        # 跳过已有的
        if chara_id in cache.npc_id_got:
            continue
        # 跳过女儿
        if cache.npc_tem_data[i].Mother_id != 0 or cache.npc_tem_data[i].AdvNpc > 9000:
            continue
        # 跳过不存在的
        if chara_id not in cache.character_data:
            continue
        # 跳过离线异常
        if not handle_premise.handle_normal_7(chara_id):
            continue
        # 跳过特殊NPC
        if cache.character_data[chara_id].name in constant.ban_NPC_name_set:
            continue
        # 如果设置了禁止，则跳过禁止干员
        if cache.all_system_setting.base_setting[7]:
            if chara_id in cache.forbidden_npc_id:
                continue
        recruitable_npc_id_list.append(chara_id)

    return recruitable_npc_id_list


def update_recruit():
    """刷新招募栏位"""

    from Script.UI.Panel import recruit_panel

    # 遍历全招募栏
    for recruit_line_id in cache.rhodes_island.recruit_line:

        # 如果超过100则进行结算
        if cache.rhodes_island.recruit_line[recruit_line_id][0] >= 100:
            cache.rhodes_island.recruit_line[recruit_line_id][0] = 0

            # 招募策略
            recruitment_strategy = cache.rhodes_island.recruit_line[recruit_line_id][1]

            # 绘制信息
            now_draw = draw.WaitDraw()
            now_draw.width = window_width
            now_draw.style = "gold_enrod"

            # 开始获得招募npc的id
            recruitable_npc_id_list = recruit_panel.find_recruitable_npc()
            wait_id_list = []
            # 保证为int类型
            if not isinstance(cache.rhodes_island.recruit_line[recruit_line_id][2], int):
                cache.rhodes_island.recruit_line[recruit_line_id][2] = 0
            # 主招募专员
            line_main_chara_id = cache.rhodes_island.recruit_line[recruit_line_id][2]
            line_main_chara_data = cache.character_data[line_main_chara_id]
            for chara_id in recruitable_npc_id_list:
                # 本地招募
                if recruitment_strategy == 0:
                    character_data = cache.character_data[chara_id]
                    # 筛选出出生地是当前罗德岛所在地的角色
                    if character_data.relationship.birthplace != cache.rhodes_island.current_location[0]:
                        continue
                    wait_id_list.append(chara_id)
                # 全泰拉招募
                elif recruitment_strategy == 1:
                    wait_id_list.append(chara_id)
                # 同势力干员
                elif recruitment_strategy == 2:
                    character_data = cache.character_data[chara_id]
                    # 筛选出势力相同的角色
                    if character_data.relationship.nation != line_main_chara_data.relationship.nation:
                        continue
                    wait_id_list.append(chara_id)
                # 同出身地干员
                elif recruitment_strategy == 3:
                    character_data = cache.character_data[chara_id]
                    # 筛选出出身地相同的角色
                    if character_data.relationship.birthplace != line_main_chara_data.relationship.birthplace:
                        continue
                    wait_id_list.append(chara_id)
                # 同职业干员
                elif recruitment_strategy == 4:
                    character_data = cache.character_data[chara_id]
                    # 筛选出职业相同的角色
                    if character_data.profession != line_main_chara_data.profession:
                        continue
                    wait_id_list.append(chara_id)
                # 同种族干员
                elif recruitment_strategy == 5:
                    character_data = cache.character_data[chara_id]
                    # 筛选出种族相同的角色
                    if character_data.race != line_main_chara_data.race:
                        continue
                    wait_id_list.append(chara_id)
                # 同外表年龄干员
                elif recruitment_strategy == 6:
                    character_data = cache.character_data[chara_id]
                    line_main_chara_age_talent = handle_talent.have_age_talent(line_main_chara_id)
                    # 筛选出外表年龄相同的角色
                    if character_data.talent[line_main_chara_age_talent] != 1:
                        continue
                    wait_id_list.append(chara_id)
                # 同胸部大小干员
                elif recruitment_strategy == 7:
                    character_data = cache.character_data[chara_id]
                    line_main_chara_bust_talent = handle_talent.have_chest_talent(line_main_chara_id)
                    # 筛选出胸部大小相同的角色
                    if character_data.talent[line_main_chara_bust_talent] != 1:
                        continue
                    wait_id_list.append(chara_id)
                # 同臀部大小干员
                elif recruitment_strategy == 8:
                    character_data = cache.character_data[chara_id]
                    line_main_chara_hip_talent = handle_talent.have_hip_talent(line_main_chara_id)
                    # 筛选出臀部大小相同的角色
                    if character_data.talent[line_main_chara_hip_talent] != 1:
                        continue
                    wait_id_list.append(chara_id)
            if len(wait_id_list):
                choice_id = random.choice(wait_id_list)
                cache.rhodes_island.recruited_id.add(choice_id)

                now_draw.text = _("\n\n   ※ 招募到了新的干员，请前往博士办公室确认 ※\n\n")
                now_draw.draw()
            else:
                now_draw.text = _("\n\n   ※ 当前招募策略无可招募npc，招募失败，已自动停止招募，请调整招募策略 ※\n\n")
                now_draw.style = "warning"
                now_draw.draw()
                cache.rhodes_island.recruit_line[recruit_line_id][1] = 11

def calculate_recruit_line_efficiency(line_id: int) -> Tuple[str, float]:
    """
    计算某条招募线的效率，并返回描述字符串和效率值
    Keyword arguments:
    line_id -- 招募线id
    Returns:
    detail_str -- 描述字符串
    total_bonus -- 效率值
    """
    if line_id not in cache.rhodes_island.recruit_line:
        return _("无此招募线"), 0.0

    recruitment_strategy_id = cache.rhodes_island.recruit_line[line_id][1]
    recruitment_strategy_data = game_config.config_recruitment_strategy.get(recruitment_strategy_id)
    if not recruitment_strategy_data:
        return _("未知策略"), 0.0
    # 11号则直接返回
    if recruitment_strategy_id == 11:
        return _("已停止招募"), 0.0

    # 当前设施数据
    now_level = cache.rhodes_island.facility_level[7]
    # 当前设施效率
    facility_effect = basement.calc_facility_efficiency(7)

    # 如果变量类型不是int，则改为0
    if not isinstance(cache.rhodes_island.recruit_line[line_id][2], int):
        cache.rhodes_island.recruit_line[line_id][2] = 0
    # 招募效率(使用主/副招聘专员机制)
    line_main_id = cache.rhodes_island.recruit_line[line_id][2]
    main_name = cache.character_data[line_main_id].name if line_main_id in cache.character_data else _("空缺")
    # 全部主招聘专员
    main_ids = set()
    # 全部主招聘专员如果不是int，则改为0
    for i in cache.rhodes_island.recruit_line:
        if not isinstance(cache.rhodes_island.recruit_line[i][2], int):
            cache.rhodes_island.recruit_line[i][2] = 0
        main_ids.add(cache.rhodes_island.recruit_line[i][2])
    # 计算加成
    total_bonus = 0.0
    sub_bonus = 0.0
    # 文本
    hr_parts_str = "["
    # 遍历所有招聘专员
    for chara_id in cache.rhodes_island.hr_operator_ids_list:
        if chara_id not in cache.character_data:
            continue
        # 跳过玩家
        if chara_id == 0:
            continue
        character_data: game_type.Character = cache.character_data[chara_id]
        base_effect = 2 * attr_calculation.get_ability_adjust(character_data.ability.get(40,0))
        if chara_id == line_main_id:
            total_bonus += base_effect
            hr_parts_str += _("主:{0}(话术lv{1}:{2}%)").format(main_name, character_data.ability.get(40,0), round(base_effect,1))
        elif chara_id in main_ids:
            pass
        else:
            sub_bonus += base_effect / 5
    # 如果文本为空，说明没有主招聘专员
    if hr_parts_str == "[":
        hr_parts_str += _("主:空缺")
        total_bonus = 1.0
    # 副专员
    total_bonus += sub_bonus
    hr_parts_str += _("，副:{0}%]").format(round(sub_bonus,1))
    # 除以策略难度调整
    total_bonus /= recruitment_strategy_data.adjust
    strategy_str = _(" * 策略调整系数{0}%").format(int(recruitment_strategy_data.adjust * 100))
    # 乘以设施效率
    total_bonus *= facility_effect
    facility_effect_str = _("* 设施效率调整{0}%").format(round(facility_effect * 100,1))
    # 停止招募则为0
    if recruitment_strategy_id == 11:
        total_bonus = 0.0
        hr_parts_str += _("，已停止招募")
    detail_str = _("当前效率加成：{0} {1} {2} = {2}%").format(hr_parts_str, strategy_str, facility_effect_str, round(total_bonus, 1))
    return detail_str, total_bonus

class Recruit_Panel:
    """
    用于招募的面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.now_panel = _("招募")
        """ 当前绘制的页面 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """

    def draw(self):
        """绘制对象"""
        # 刷新一下
        basement.get_base_updata()

        title_text = _("招募")
        title_draw = draw.TitleLineDraw(title_text, self.width)
        # 当前设施数据
        now_level = cache.rhodes_island.facility_level[7]
        line_count = len(cache.rhodes_island.recruit_line)

        # 开始获得招募npc的id
        recruitable_npc_id_list = find_recruitable_npc()
        wait_id_list = []
        for chara_id in recruitable_npc_id_list:
            character_data = cache.character_data[chara_id]
            # 筛选出出生地是当前罗德岛所在地的角色
            if character_data.relationship.birthplace != cache.rhodes_island.current_location[0]:
                continue
            else:
                wait_id_list.append(chara_id)

        while 1:
            return_list = []
            title_draw.draw()

            all_info_draw = draw.NormalDraw()
            now_text = _("  当前设施等级为：{0}，可同时有{1}条招募线\n").format(now_level, line_count)
            # 输出当前国家剩余可招募干员的数量
            now_text += _("  当前国家剩余可招募干员数量（不含委托特殊招募）：{0}\n").format(len(wait_id_list))
            if len(cache.rhodes_island.recruited_id) == 0:
                now_text += _("  当前没有已招募待确认的干员\n")
            else:
                now_text += _("  当前已招募待确认的干员有：")
                for chara_id in cache.rhodes_island.recruited_id:
                    character_data: game_type.Character = cache.character_data[chara_id]
                    now_text += f" [{str(character_data.adv).rjust(4,'0')}]{character_data.name}"
                now_text += f"\n"

            all_info_draw.text = now_text
            all_info_draw.width = self.width
            all_info_draw.draw()

            for recruit_line_id in cache.rhodes_island.recruit_line:
                # 招募进度，保留一位小数
                now_dregree = cache.rhodes_island.recruit_line[recruit_line_id][0]
                now_dregree = round(now_dregree, 1)
                now_text = _("\n {0}号招募进度：{1}%").format(recruit_line_id+1, now_dregree)
                all_info_draw.text = now_text
                all_info_draw.draw()

                # 基础数据
                recruitment_strategy_id = cache.rhodes_island.recruit_line[recruit_line_id][1]
                recruitment_strategy_data = game_config.config_recruitment_strategy[recruitment_strategy_id]

                # 招募策略
                now_text = _("\n    招募策略：{0}      ").format(recruitment_strategy_data.name)
                all_info_draw.text = now_text
                all_info_draw.draw()
                button_text = _(" [调整策略] ")
                button_draw = draw.CenterButton(
                    _(button_text),
                    _("{0}_{1}").format(button_text, recruit_line_id),
                    len(button_text) * 2,
                    cmd_func=self.select_recruitment_strategy,
                    args=recruit_line_id,
                    )
                return_list.append(button_draw.return_text)
                button_draw.draw()
                line_feed.draw()

                # 计算本线当前效率
                detail_str, total_bonus = calculate_recruit_line_efficiency(recruit_line_id)
                if recruitment_strategy_id == 11:
                    cache.rhodes_island.recruit_line[recruit_line_id][0] = 0
                all_info_draw.text = "    " + detail_str
                all_info_draw.draw()

                line_feed.draw()
            line_feed.draw()

            button_text = _("[001]招聘专员管理")
            button_draw = draw.LeftButton(
                _(button_text),
                _(button_text),
                int(self.width / 3),
                cmd_func=self.select_npc_position,
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
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def select_recruitment_strategy(self, recruit_line_id):
        """选择招募策略"""
        while 1:
            line = draw.LineDraw("-", window_width)
            line.draw()
            info_draw = draw.NormalDraw()
            info_draw.width = window_width
            return_list = []

            recruitment_strategy_id = cache.rhodes_island.recruit_line[recruit_line_id][1]
            recruitment_strategy_data = game_config.config_recruitment_strategy[recruitment_strategy_id]

            info_text = ""
            info_text += _(" {0}号招募当前的策略为：{1}").format(recruit_line_id+1, recruitment_strategy_data.name)

            info_text += _("\n\n 当前可以选择的策略有（系数越高越简单）：\n")
            info_draw.text = info_text
            info_draw.draw()
            line_feed.draw()

            # 当前设施等级
            now_level = cache.rhodes_island.facility_level[7]

            # 遍历策略列表，获取每个策略的信息
            for cid in game_config.config_recruitment_strategy.keys():
                recruitment_strategy_data = game_config.config_recruitment_strategy[cid]
                # 如果设施等级不够，则跳过
                if now_level < recruitment_strategy_data.lv:
                    continue

                # 输出策略信息
                button_draw_text = f"[{str(cid).rjust(2,'0')}]"
                button_draw_text += attr_calculation.pad_display_width(recruitment_strategy_data.name, 24)
                button_draw_text += _("(调整系数{0})").format(recruitment_strategy_data.adjust)
                button_draw_text += "："
                button_draw_text += recruitment_strategy_data.introduce
                # 主招聘专员id
                line_main_chara_id = cache.rhodes_island.recruit_line[recruit_line_id][2]
                # 招聘当地随机干员
                if cid == 0:
                    birthplace_id = cache.rhodes_island.current_location[0]
                    add_text = game_config.config_birthplace[birthplace_id].name
                    button_draw_text += _("（{0}）").format(add_text)
                # 对于同主招聘专员的策略，进行补充说明
                elif cid in (2, 3, 4, 5, 6, 7, 8) and line_main_chara_id != 0:
                    line_main_chara_data = cache.character_data[line_main_chara_id]
                    add_text = ""
                    if cid == 2:
                        nation_id = line_main_chara_data.relationship.nation
                        add_text = game_config.config_nation[nation_id].name
                    elif cid == 3:
                        birthplace_id = line_main_chara_data.relationship.birthplace
                        add_text = game_config.config_birthplace[birthplace_id].name
                    elif cid == 4:
                        profession_id = line_main_chara_data.profession
                        add_text = game_config.config_profession[profession_id].name
                    elif cid == 5:
                        race_id = line_main_chara_data.race
                        add_text = game_config.config_race[race_id].name
                    elif cid == 6:
                        age_talent_id = handle_talent.have_age_talent(line_main_chara_id)
                        add_text = game_config.config_talent[age_talent_id].name
                    elif cid == 7:
                        chest_talent_id = handle_talent.have_chest_talent(line_main_chara_id)
                        add_text = game_config.config_talent[chest_talent_id].name
                    elif cid == 8:
                        hip_talent_id = handle_talent.have_hip_talent(line_main_chara_id)
                        add_text = game_config.config_talent[hip_talent_id].name    
                    button_draw_text += _("（{0}）").format(add_text)
                button_draw = draw.LeftButton(
                    button_draw_text,
                    f"\n{cid}",
                    window_width ,
                    cmd_func=self.change_recruit_line_produce,
                    args=(recruit_line_id ,cid)
                )
                button_draw.draw()
                return_list.append(button_draw.return_text)

                line_feed.draw()

            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn in return_list:
                break

    def select_npc_position(self):
        """招聘专员管理(任命各线主招聘专员)"""
        ri = cache.rhodes_island
        from Script.UI.Panel import manage_basement_panel
        while 1:
            # 刷新一下
            basement.update_work_people()
            title = draw.TitleLineDraw(_("招聘专员管理"), self.width)
            title.draw()
            return_list = []

            info = draw.NormalDraw(); info.width = self.width
            info.text = _("当前招聘专员数量：{0}").format(len(ri.hr_operator_ids_list))
            info.text += "      "
            info.draw()

            # 增减按钮
            button_text = _("[招聘专员增减]")
            button_draw = draw.CenterButton(
                _(button_text),
                _(button_text),
                len(button_text) * 2 + 2,
                cmd_func=manage_basement_panel.change_npc_work_out,
                args=self.width
            )
            return_list.append(button_draw.return_text)
            button_draw.draw()
            line_feed.draw(); line_feed.draw()

            # 显示各线主招聘专员
            for line_id in ri.recruit_line:
                main_id = ri.recruit_line[line_id][2]
                name = cache.character_data[main_id].name if main_id != 0 else _("(空缺)")
                row = draw.NormalDraw(); row.width = self.width
                row.text = _("{0}号招募线 主招聘专员: {1}  ").format(line_id+1, name)
                row.draw()
                def _make(line_idx):
                    return lambda : self._appoint_main_hr(line_idx)
                btn = draw.CenterButton(_("[任命]"), _("任命")+str(line_id+1), 12, cmd_func=_make(line_id))
                btn.draw(); return_list.append(btn.return_text)
                line_feed.draw()
            line_feed.draw()

            # 其它副招聘专员
            main_ids = {ri.recruit_line[i][2] for i in ri.recruit_line}
            other_ops = [cid for cid in ri.hr_operator_ids_list if cid not in main_ids]
            other_draw = draw.NormalDraw(); other_draw.width = self.width
            if other_ops:
                names = [cache.character_data[cid].name for cid in other_ops if cid in cache.character_data]
                other_draw.text = _("副招聘专员：") + "、".join(names) + "\n"
            else:
                other_draw.text = _("副招聘专员：暂无\n")
            other_draw.draw()
            line_feed.draw(); line_feed.draw()

            back = draw.CenterButton(_("[返回]"), _("返回"), self.width)
            back.draw(); return_list.append(back.return_text)
            line_feed.draw()
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back.return_text:
                break

    def _appoint_main_hr(self, line_id: int):
        """任命某条招募线主招聘专员(重复选择同一人可撤销)"""
        ri = cache.rhodes_island
        from Script.UI.Panel import common_select_NPC
        now_draw_panel : panel.PageHandlePanel = panel.PageHandlePanel([], common_select_NPC.CommonSelectNPCButtonList, 50, 5, window_width, True, False, 0)
        select_state = {}
        def _make(chara_id):
            self._do_appoint_main_hr(line_id, chara_id)
        while 1:
            info_text = _("请选择一名招聘专员担任第{0}号招募线主招聘专员:\n").format(line_id+1)
            final_list = []
            for npc_id in ri.hr_operator_ids_list:
                if npc_id == 0:
                    continue
                final_list.append([npc_id, _make, [ri.recruit_line[line_id][2]]])
            now_draw_panel.text_list = final_list
            return_list, other_return_list, select_state = common_select_NPC.common_select_npc_button_list_func(now_draw_panel, _("任命主招聘专员"), info_text, select_state)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == _("返回"):
                break

    def _do_appoint_main_hr(self, line_id: int, chara_id: int):
        ri = cache.rhodes_island
        if chara_id not in ri.hr_operator_ids_list:
            return
        # 如果已经是该线主，则撤销
        if ri.recruit_line[line_id][2] == chara_id:
            ri.recruit_line[line_id][2] = 0
        else:
            # 先清除其在其它线的主身份
            for lid in ri.recruit_line:
                if lid != line_id and ri.recruit_line[lid][2] == chara_id:
                    ri.recruit_line[lid][2] = 0
            ri.recruit_line[line_id][2] = chara_id

    def change_recruit_line_produce(self, asrecruit_line_id, recruitment_strategy_cid):
        """更改招募线的策略"""
        cache.rhodes_island.recruit_line[asrecruit_line_id][1] = recruitment_strategy_cid

    def settle_npc_id(self, chara_id):
        """结算干员的id变更"""
        self.now_chara_id = chara_id

    def settle_assembly_line_id(self, asrecruit_line_id):
        """结算流水线的id变更"""
        self.target_position = asrecruit_line_id
