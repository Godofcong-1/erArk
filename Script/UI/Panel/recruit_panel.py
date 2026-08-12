from typing import List, Tuple
from types import FunctionType
from Script.Core import cache_control, game_type, get_text, flow_handle, constant
from Script.Design import attr_calculation, basement, handle_premise, handle_talent, handle_ability
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
    # 刷新文本输出信号标记，确保在执行指令时，文本输出会被记录下来并发送给前端
    cache.web_text_recording_flag = True

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

    for adv_id, tem_data in cache.npc_tem_data.items():
        chara_id = adv_id
        # 跳过玩家
        if chara_id == 0:
            continue
        # 跳过已有的
        if chara_id in cache.npc_id_got:
            continue
        # 跳过已在待确认招募列表中的
        if chara_id in cache.rhodes_island.recruited_id:
            continue
        # 跳过女儿
        if tem_data.Mother_id != 0 or tem_data.AdvNpc > 9000:
            continue
        # 跳过不存在的
        if chara_id not in cache.character_data:
            continue
        # 跳过访客
        if cache.character_data[chara_id].sp_flag.vistor == 1:
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
                if chara_id == 0 and recruitment_strategy != 0 and recruitment_strategy != 1:
                    break
            
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
        base_effect = 2 * handle_ability.get_ability_adjust(character_data.ability.get(40,0))
        if chara_id == line_main_id:
            total_bonus += base_effect
            hr_parts_str += _("主:{0}(话术lv{1}:{2}%)").format(main_name, character_data.ability.get(40,0), round(base_effect,1))
        elif chara_id in main_ids:
            pass
        else:
            sub_bonus += base_effect / 5
    # 如果文本为空，说明没有主招聘专员
    if hr_parts_str == "[":
        hr_parts_str += _("主:空缺(基础1.0%)")
        total_bonus = 1.0
    # 副专员
    total_bonus += sub_bonus
    hr_parts_str += _("，副:{0}%]").format(round(sub_bonus,1))
    
    # 乘以策略难度调整
    total_bonus *= recruitment_strategy_data.adjust
    strategy_str = _(" * 策略调整系数{0}%").format(int(recruitment_strategy_data.adjust * 100))
    
    # 乘以设施效率
    total_bonus *= facility_effect
    facility_effect_str = _("* 设施效率调整{0}%").format(round(facility_effect * 100,1))
    
    # 停止招募则为0
    if recruitment_strategy_id == 11:
        total_bonus = 0.0
        hr_parts_str += _("，已停止招募")
        
    detail_str = _("当前效率加成：{0} {1} {2} = {3}%").format(hr_parts_str, strategy_str, facility_effect_str, round(total_bonus, 1))
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
        self.show_detail_line: int = -1
        """ 当前展开详情的招募线编号 """

    def toggle_detail(self, line_id: int):
        """展开或收起招募详情"""
        if self.show_detail_line == line_id:
            self.show_detail_line = -1
        else:
            self.show_detail_line = line_id

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

        while 1:
            return_list = []
            title_draw.draw()

            all_info_draw = draw.NormalDraw()
            now_text = _("  当前设施等级为：{0}，可同时有{1}条招募线\n").format(now_level, line_count)
            
            # 取消掉原本的"当前国家可招募干员数量"的文字
            if len(cache.rhodes_island.recruited_id) == 0:
                now_text += _("  当前没有已招募待确认的干员\n")
            else:
                now_text += _("  当前已招募待确认的干员有：")
                for chara_id in cache.rhodes_island.recruited_id:
                    # 如果角色id不存在或为0，则pop并跳过
                    if chara_id == 0 or chara_id not in cache.character_data:
                        cache.rhodes_island.recruited_id.remove(chara_id)
                        continue
                    character_data: game_type.Character = cache.character_data[chara_id]
                    now_text += f" [{str(character_data.adv).rjust(4,'0')}]{character_data.name}"
                now_text += f"\n"

            all_info_draw.text = now_text
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

                # 计算本线当前策略能招募到的干员列表
                line_wait_id_list = []
                line_main_chara_id = cache.rhodes_island.recruit_line[recruit_line_id][2]
                if not isinstance(line_main_chara_id, int):
                    line_main_chara_id = 0
                
                for chara_id in recruitable_npc_id_list:
                    if recruitment_strategy_id == 11:
                        break
                    chara_data = cache.character_data[chara_id]
                    if recruitment_strategy_id == 0:
                        if chara_data.relationship.birthplace == cache.rhodes_island.current_location[0]:
                            line_wait_id_list.append(chara_id)
                    elif recruitment_strategy_id == 1:
                        line_wait_id_list.append(chara_id)
                    elif recruitment_strategy_id == 2:
                        if line_main_chara_id and chara_data.relationship.nation == cache.character_data[line_main_chara_id].relationship.nation:
                            line_wait_id_list.append(chara_id)
                    elif recruitment_strategy_id == 3:
                        if line_main_chara_id and chara_data.relationship.birthplace == cache.character_data[line_main_chara_id].relationship.birthplace:
                            line_wait_id_list.append(chara_id)
                    elif recruitment_strategy_id == 4:
                        if line_main_chara_id and chara_data.profession == cache.character_data[line_main_chara_id].profession:
                            line_wait_id_list.append(chara_id)
                    elif recruitment_strategy_id == 5:
                        if line_main_chara_id and chara_data.race == cache.character_data[line_main_chara_id].race:
                            line_wait_id_list.append(chara_id)
                    elif recruitment_strategy_id == 6:
                        if line_main_chara_id:
                            age_talent_id = handle_talent.have_age_talent(line_main_chara_id)
                            if chara_data.talent.get(age_talent_id) == 1:
                                line_wait_id_list.append(chara_id)
                    elif recruitment_strategy_id == 7:
                        if line_main_chara_id:
                            chest_talent_id = handle_talent.have_chest_talent(line_main_chara_id)
                            if chara_data.talent.get(chest_talent_id) == 1:
                                line_wait_id_list.append(chara_id)
                    elif recruitment_strategy_id == 8:
                        if line_main_chara_id:
                            hip_talent_id = handle_talent.have_hip_talent(line_main_chara_id)
                            if chara_data.talent.get(hip_talent_id) == 1:
                                line_wait_id_list.append(chara_id)

                # 绘制当前策略能招到的人数及详情按钮
                rem_count = len(line_wait_id_list)
                rem_prefix_draw = draw.NormalDraw()
                rem_prefix_draw.text = _("    当前策略剩余可招募干员数：")
                rem_prefix_draw.draw()

                rem_count_draw = draw.NormalDraw()
                rem_count_draw.text = str(rem_count)
                if rem_count == 0:
                    rem_count_draw.style = "red"  # 为0时标红色
                rem_count_draw.draw()

                if rem_count > 0:
                    detail_btn_text = _(" [详情] ")
                    detail_btn = draw.CenterButton(
                        detail_btn_text,
                        _("{0}_{1}").format(detail_btn_text, recruit_line_id),
                        len(detail_btn_text) * 2,
                        cmd_func=self.toggle_detail,
                        args=(recruit_line_id,)
                    )
                    detail_btn.draw()
                    return_list.append(detail_btn.return_text)
                line_feed.draw()

                # 如果点击详情，则展开所有名字
                if self.show_detail_line == recruit_line_id and rem_count > 0:
                    detail_names = "      " + "、".join([cache.character_data[cid].name for cid in line_wait_id_list])
                    detail_draw = draw.NormalDraw()
                    detail_draw.text = detail_names + "\n"
                    detail_draw.draw()

                # 计算本线当前效率
                detail_str, total_bonus = calculate_recruit_line_efficiency(recruit_line_id)
                if recruitment_strategy_id == 11:
                    cache.rhodes_island.recruit_line[recruit_line_id][0] = 0
                
                # 绘制效率加成文本，并将"空缺"标为橘色（warning样式）
                full_detail = "    " + detail_str
                vacant_str = _("空缺")
                if vacant_str in full_detail:
                    parts = full_detail.split(vacant_str)
                    for i, part in enumerate(parts):
                        pd = draw.NormalDraw()
                        pd.text = part
                        pd.draw()
                        if i < len(parts) - 1:
                            vd = draw.NormalDraw()
                            vd.text = vacant_str
                            vd.style = "warning"
                            vd.draw()
                else:
                    all_info_draw.text = full_detail
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
            
            # 检查是否有任何一条招募线的主招聘专员空缺
            has_vacant_main = False
            for recruit_line_id in cache.rhodes_island.recruit_line:
                main_id = cache.rhodes_island.recruit_line[recruit_line_id][2]
                if not isinstance(main_id, int) or main_id == 0:
                    has_vacant_main = True
                    break
            
            # 如果有空缺，将按钮的正常颜色改为 gold_enrod
            if has_vacant_main:
                button_draw.normal_style = "gold_enrod"

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

            info_text += _("\n\n 当前可以选择的策略有（系数越高越简单、招募越快）：\n")
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
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def select_npc_position(self):
        """招聘专员管理(任命各线主招聘专员)"""
        ri = cache.rhodes_island
        from Script.UI.Panel import manage_basement_panel
        from Script.Design import handle_ability, handle_talent
        
        page = 0
        items_per_page = 10
        
        # 輔助：固定寬度對齊
        def fmt(text, width):
            return attr_calculation.pad_display_width(str(text), width)
            
        # 輔助：建立每一行的文字
        def build_row_text(role, chara_id, is_main):
            if chara_id == 0:
                return "  " + fmt(role, 15) + " | " + fmt(_("空缺"), 12) + " | " + fmt("-", 8) + " | " + fmt("-", 6) + " | " + fmt("-", 10) + " | " + fmt("-", 10) + " | " + fmt("-", 8) + " | " + fmt("-", 8) + " | " + fmt("-", 6) + " | " + fmt("-", 6) + " | " + fmt("-", 6)
                
            chara = cache.character_data[chara_id]
            base_effect = 2 * handle_ability.get_ability_adjust(chara.ability.get(40,0))
            bonus = base_effect if is_main else base_effect / 5
            bonus_text = f"{round(bonus,1)}%"
            abi_lv = chara.ability.get(40,0)
            abi_str = f"{attr_calculation.judge_grade(abi_lv)} {abi_lv}"
            
            def safe_get(cfg, key):
                return cfg[key].name if key in cfg else "-"
            
            nation = safe_get(game_config.config_nation, chara.relationship.nation)
            birth = safe_get(game_config.config_birthplace, chara.relationship.birthplace)
            prof = safe_get(game_config.config_profession, chara.profession)
            race = safe_get(game_config.config_race, chara.race)
            age = safe_get(game_config.config_talent, handle_talent.have_age_talent(chara_id))
            chest = safe_get(game_config.config_talent, handle_talent.have_chest_talent(chara_id))
            hip = safe_get(game_config.config_talent, handle_talent.have_hip_talent(chara_id))
            
            return "  " + fmt(role, 15) + " | " + fmt(chara.name, 12) + " | " + fmt(bonus_text, 8) + " | " + fmt(abi_str, 6) + " | " + fmt(nation, 10) + " | " + fmt(birth, 10) + " | " + fmt(prof, 8) + " | " + fmt(race, 8) + " | " + fmt(age, 6) + " | " + fmt(chest, 6) + " | " + fmt(hip, 6)

        while 1:
            # 刷新一下
            basement.update_work_people()
            title = draw.TitleLineDraw(_("招聘专员管理"), self.width)
            title.draw()
            return_list = []

            info = draw.NormalDraw()
            info.text = _("  当前招聘专员数量：{0}      \n").format(len(ri.hr_operator_ids_list))
            info.draw()

            # 增减按钮
            button_text = _("[招聘专员增减]")
            button_draw = draw.CenterButton(
                _(button_text),
                _(button_text),
                len(button_text) * 2 + 2,
                cmd_func=manage_basement_panel.change_npc_work_out,
                args=(self.width, [132])
            )
            return_list.append(button_draw.return_text)
            button_draw.draw()
            line_feed.draw(); line_feed.draw()

            # 表头
            header_text = "  " + fmt(_("职位"), 15) + " | " + fmt(_("名字"), 12) + " | " + fmt(_("加成"), 8) + " | " + fmt(_("话术"), 6) + " | " + fmt(_("势力"), 10) + " | " + fmt(_("出生地"), 10) + " | " + fmt(_("职业"), 8) + " | " + fmt(_("种族"), 8) + " | " + fmt(_("外表"), 6) + " | " + fmt(_("胸部"), 6) + " | " + fmt(_("臀部"), 6)
            header_draw = draw.NormalDraw()
            header_draw.text = header_text + "\n"
            header_draw.draw()
            
            # 分割线
            div = draw.LineDraw("-", self.width)
            div.draw()

            # 显示各线主招聘专员
            for line_id in ri.recruit_line:
                main_id = ri.recruit_line[line_id][2]
                if not isinstance(main_id, int):
                    main_id = 0
                    
                role_str = _("主召聘专员({0}号)").format(line_id+1)
                row_text = build_row_text(role_str, main_id, True)

                def _make(line_idx):
                    return lambda : self._appoint_main_hr(line_idx)
                
                # 整排按钮，按下等同原 [任命]
                btn = draw.LeftButton(row_text, f"任命_{line_id+1}", self.width, cmd_func=_make(line_id))
                
                # 如果是空缺狀態，則整行按鈕標成橘色
                if main_id == 0:
                    btn.normal_style = "gold_enrod"
                    
                btn.draw(); return_list.append(btn.return_text)
                line_feed.draw()
                
            line_feed.draw()
            # 主副之间的分割线
            div.draw()
            line_feed.draw()

            # 其它副招聘专员
            main_ids = {ri.recruit_line[i][2] for i in ri.recruit_line if isinstance(ri.recruit_line[i][2], int)}
            other_ops = [cid for cid in ri.hr_operator_ids_list if cid not in main_ids and cid != 0]
            # 依话术等级从高到低排序
            other_ops.sort(key=lambda x: cache.character_data[x].ability.get(40,0), reverse=True)
            
            total_sub = len(other_ops)
            max_page = max(0, (total_sub - 1) // items_per_page)
            if page > max_page: page = max_page
            
            start_idx = page * items_per_page
            end_idx = start_idx + items_per_page
            curr_ops = other_ops[start_idx:end_idx]
            
            if not curr_ops:
                no_sub = draw.NormalDraw()
                no_sub.text = _("  副招聘专员：暂无\n")
                no_sub.draw()
            else:
                for cid in curr_ops:
                    row_text = build_row_text(_("副招聘专员"), cid, False)
                    row_draw = draw.NormalDraw()
                    row_draw.text = row_text + "\n"
                    row_draw.draw()
                    
            line_feed.draw(); line_feed.draw()

            # 副招聘专员翻页按钮
            if max_page > 0:
                def prev_p(): nonlocal page; page -= 1
                def next_p(): nonlocal page; page += 1
                
                prev_btn = draw.CenterButton(_("[上一页]"), _("上一页"), int(self.width/2), cmd_func=prev_p)
                next_btn = draw.CenterButton(_("[下一页]"), _("下一页"), int(self.width/2), cmd_func=next_p)
                
                if page > 0:
                    prev_btn.draw()
                    return_list.append(prev_btn.return_text)
                else:
                    null_btn = draw.CenterDraw()
                    null_btn.text = " "
                    null_btn.width = int(self.width/2)
                    null_btn.draw()
                    
                if page < max_page:
                    next_btn.draw()
                    return_list.append(next_btn.return_text)
                else:
                    null_btn = draw.CenterDraw()
                    null_btn.text = " "
                    null_btn.width = int(self.width/2)
                    null_btn.draw()
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
