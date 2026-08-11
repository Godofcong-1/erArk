from typing import List
from types import FunctionType
from Script.Core import cache_control, game_type, get_text, flow_handle, constant
from Script.UI.Moudle import draw, panel
from Script.Config import game_config, normal_config
from Script.Design import game_time, attr_calculation, talk, handle_premise

from Script.System.Field_Commission_System.field_commission_function import get_commission_demand_and_reward, process_commission_text

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


class Field_Commission_Panel:
    """
    用于显示外勤委托界面面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.now_panel = _("常规外勤")
        """ 当前绘制的页面 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """
        self.send_npc_list = []
        """ 派遣人员列表 """
        self.send_vehicle_dict = {}
        """ 派遣载具字典 """

    def draw(self):
        """绘制对象"""

        title_text = _("外勤委托")
        commission_type_list = [_("常规外勤"), _("特殊外勤")]
        commission_type_list_len = int(self.width / len(commission_type_list))
        self.handle_panel = panel.PageHandlePanel([], CommissionDraw, 20, 1, self.width)

        title_draw = draw.TitleLineDraw(title_text, self.width)
        while 1:
            return_list = []
            title_draw.draw()

            # 绘制面板类型切换
            for commission_type in commission_type_list:
                if commission_type == self.now_panel:
                    now_draw = draw.CenterDraw()
                    now_draw.text = f"[{commission_type}]"
                    now_draw.style = "onbutton"
                    now_draw.width = commission_type_list_len
                    now_draw.draw()
                else:
                    now_draw = draw.CenterButton(
                        f"[{commission_type}]",
                        f"\n{commission_type}",
                        commission_type_list_len,
                        cmd_func=self.change_panel,
                        args=(commission_type,),
                    )
                    now_draw.draw()
                    return_list.append(now_draw.return_text)
            line_feed.draw()
            line = draw.LineDraw("+", self.width)
            line.draw()

            # 设施信息
            now_level = cache.rhodes_island.facility_level[14]
            facility_info_text = ""
            facility_info_text += _("○通用委托无论在哪里都可以接到，地区委托则需要罗德岛移动到对应地区时才可接到，能接到的委托等级与机库的等级有关\n")
            facility_info_text += _("○常规外勤委托可以多次反复完成，特殊外勤只能完成一次\n")
            facility_info_text += _("○罗德岛的移动：控制中枢-指挥室-导航，购买载具：机库-格纳库-管理载具\n")
            facility_info_text += _("○当前机库等级：{0}，最高可接到{1}级的委托\n").format(now_level, now_level + 1)

            facility_info_draw = draw.NormalDraw()
            facility_info_draw.text = facility_info_text
            facility_info_draw.draw()
            line = draw.LineDraw("+", self.width)
            line.draw()

            # 绘制提示信息
            info_text_list = [_("委托等级"), _("委托类型"), _("委托名称"), _("派遣人数与耗时天数"), _("需求类型"), _("奖励类型")]
            info_draw_len = int(self.width / len(info_text_list))
            for info_text in info_text_list:
                info_draw = draw.CenterDraw()
                info_draw.text = attr_calculation.pad_display_width(info_text, info_draw_len, "center")
                info_draw.width = info_draw_len
                info_draw.draw()
            line_feed.draw()
            line = draw.LineDraw("~", self.width)
            line.draw()

            # 获取当前国家的委托列表
            now_country_id = cache.rhodes_island.current_location[0]
            if now_country_id in game_config.config_commission_id_by_country:
                now_country_commision_list = game_config.config_commission_id_by_country[now_country_id]
            else:
                now_country_commision_list = []
            common_commision_list = game_config.config_commission_id_by_country[-1]
            # 根据委托的等级对委托列表进行排序
            now_country_commision_list.sort(key=lambda x: game_config.config_commission[x].level)
            common_commision_list.sort(key=lambda x: game_config.config_commission[x].level)
            all_commision_list = now_country_commision_list + common_commision_list

            # 绘制委托信息
            final_commision_list = []
            for commision_id in all_commision_list:
                commision_data = game_config.config_commission[commision_id]
                # 跳过非当前面板的委托
                if self.now_panel == _("常规外勤") and commision_data.special != 0:
                    continue
                if self.now_panel == _("特殊外勤") and commision_data.special == 0:
                    continue
                # 以下为非debug模式下会进行的跳过判断
                if not cache.debug_mode:
                    # 跳过未满足前置委托的委托
                    if commision_data.related_id != -1 and commision_data.related_id not in cache.rhodes_island.finished_field_commissions_set:
                        continue
                    # 特殊外勤只能接受一次
                    if commision_data.special != 0 and commision_id in cache.rhodes_island.finished_field_commissions_set:
                        continue
                    # 跳过已经关闭的委托
                    if commision_id in cache.rhodes_island.shut_down_field_commissions_set:
                        continue
                    # 跳过等级大于设施等级+1的委托
                    if commision_data.level > cache.rhodes_island.facility_level[14] + 1:
                        continue
                    # 跳过含有角色出场且还没有招募到该角色的角色类委托
                    if "c_" in commision_data.demand and commision_data.type == _("角色"):
                        chara_adv = int(commision_data.demand.split("_")[1])
                        for character_id in cache.npc_id_got:
                            if cache.character_data[character_id].adv == chara_adv:
                                break
                        else:
                            continue
                # 如果满足条件，则加入最终委托列表
                final_commision_list.append(commision_id)

            # 遍历最终委托列表，绘制委托信息
            self.handle_panel.text_list = final_commision_list
            self.handle_panel.update()
            self.handle_panel.draw()
            return_list.extend(self.handle_panel.return_list)

            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def change_panel(self, building_type: str):
        """
        切换当前面板显示
        Keyword arguments:
        building_type -- 要切换的面板类型
        """

        self.now_panel = building_type

class CommissionDraw:
    """
    用于绘制外勤委托的绘制对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, commission_id: int, width: int, is_button: bool, num_button: bool, button_id: int):
        """初始化绘制对象"""
        self.commission_id: int = commission_id
        """ 委托编号 """
        self.width: int = width
        """ 绘制的最大宽度 """
        self.is_button: bool = is_button
        """ 是否为按钮 """
        self.num_button: bool = num_button
        """ 是否为数字按钮 """
        self.button_id: int = button_id
        """ 按钮编号 """
        self.draw_text: str = ""
        """ 绘制文本 """
        self.button_return: str = ""
        """ 按钮返回文本 """
        self.send_npc_list = []
        """ 派遣人员列表 """
        self.send_vehicle_dict = {}
        """ 派遣载具字典 """

        info_text_list = ["委托等级", "委托类型", "委托名称", "派遣人数与耗时天数", "需求类型", "奖励类型"]
        # 修正文本宽度
        text_width = int((self.width - 1) / (len(info_text_list)))

        commission_data = game_config.config_commission[self.commission_id]
        # 委托信息
        commission_name = commission_data.name
        
        # [修改] 已经完成的委托前面加星号
        if self.commission_id in cache.rhodes_island.finished_field_commissions_set:
            commission_name = "⭐" + commission_name
            
        if self.commission_id in cache.rhodes_island.ongoing_field_commissions:
            commission_name += _("（进行中）")
            
        commission_name = attr_calculation.pad_display_width(commission_name, text_width, "center")
        commission_level = attr_calculation.pad_display_width(str(commission_data.level), text_width, "center")
        commission_type = attr_calculation.pad_display_width(commission_data.type, text_width, "center")
        commission_people = str(commission_data.people) + _("人")
        commission_time = str(commission_data.time) + _("天")
        commission_people_and_time = attr_calculation.pad_display_width(f"{commission_people}  {commission_time}", text_width, "center")
        demand_return_list = get_commission_demand_and_reward(self.commission_id, self.send_npc_list)
        reward_return_list = get_commission_demand_and_reward(self.commission_id, self.send_npc_list, True)
        
        commission_demand = attr_calculation.pad_display_width(demand_return_list[1], text_width, "center")
        # 列表为了排版对齐，这里奖励仍显示简略版类型(如：材料、金钱)
        commision_reward = attr_calculation.pad_display_width(reward_return_list[1], text_width, "center")
        # 最终文本
        commision_text = f"{commission_level}{commission_type}{commission_name}{commission_people_and_time}{commission_demand}{commision_reward}"

        # 可以进行的，绘制为按钮
        if self.commission_id not in cache.rhodes_island.ongoing_field_commissions:
            commision_draw = draw.LeftButton(
                commision_text,
                "\n" + commission_data.name,  # 返回时不带星号
                self.width,
                cmd_func=self.commision_info,
                args=(self.commission_id,),
            )
            self.button_return = commision_draw.return_text
        # 正在进行的，绘制为灰色文字
        else:
            commision_draw = draw.NormalDraw()
            commision_draw.text = commision_text
            commision_draw.width = self.width
            commision_draw.style = "deep_gray"
        self.draw_text = commision_draw.text
        self.now_draw = commision_draw

    def draw(self):
        """绘制对象"""
        self.now_draw.draw()


    def commision_info(self, commision_id: int):
        """
        显示委托详细信息
        Keyword arguments:
        commision_id -- 委托编号
        """

        # 委托信息
        commision_data = game_config.config_commission[commision_id]
        commision_name = commision_data.name
        
        # [修改] 委托介绍的名称加星号
        if commision_id in cache.rhodes_island.finished_field_commissions_set:
            commision_name = "⭐" + commision_name
            
        commision_level = str(commision_data.level)
        commision_people = str(commision_data.people) + _("人")
        commision_time = str(commision_data.time) + _("天")
        commision_capacity_int = (commision_data.time - 1) * commision_data.people
        
        # [修改] 改为获取并列出实际报酬的全文
        reward_return_list = get_commission_demand_and_reward(commision_id, self.send_npc_list, True)
        commision_reward = reward_return_list[2] # 索引2为包含具体数值的full_text
        
        commision_description = commision_data.description
        # 将\n替换为换行符
        if "\\n" in commision_description:
            commision_description = commision_description.replace("\\n", "\n      ")

        # --- 解析委托的动态需求 (能力与特定干员) ---
        required_ability = {}
        required_chars_adv = []
        try:
            if commision_data.demand and commision_data.demand != "无" and str(commision_data.demand) != "-1":
                for d in str(commision_data.demand).split("&"):
                    parts = d.split("_")
                    if parts[0] == "a" and len(parts) >= 3:
                        required_ability[int(parts[1])] = int(parts[2])
                    elif parts[0] == "c" and len(parts) >= 2:
                        required_chars_adv.append(int(parts[1]))
        except Exception:
            pass # 容错处理

        # 派遣人员与载具
        self.send_npc_list = []
        self.send_vehicle_dict = {}

        while 1:
            # 获取当前干员满足的其他需求情况 (底层自带结算，用于判断逻辑)
            demand_return_list = get_commission_demand_and_reward(commision_id, self.send_npc_list)
            deman_satify = demand_return_list[0]

            return_list = []
            line = draw.LineDraw("-", self.width)
            line.draw()

            # 绘制委托基础信息
            info_draw = draw.NormalDraw()
            info_draw.text = _("\n委托名称：{0}").format(commision_name)
            info_draw.text += _("\n委托等级：{0}").format(commision_level)
            info_draw.text += _("\n耗时天数：{0}").format(commision_time)
            info_draw.text += _("\n奖励：{0}").format(commision_reward)
            info_draw.text += _("\n介绍：{0}").format(commision_description)
            info_draw.width = self.width
            info_draw.draw()

            # 计算载具总运载量
            now_capacity = 0 # 当前运载量
            for vehicle_id in self.send_vehicle_dict:
                now_capacity += game_config.config_vehicle[vehicle_id].capacity * self.send_vehicle_dict[vehicle_id]

            # 判定各项是否满足
            people_sat = len(self.send_npc_list) >= commision_data.people
            cap_sat = now_capacity >= commision_capacity_int
            all_satisfy = people_sat and cap_sat and deman_satify

            # 绘制派遣人员与载具列表
            info_draw_2_text = _("\n\n派遣人员：")
            if not self.send_npc_list:
                info_draw_2_text += _(" 无")
            for chara_id in self.send_npc_list:
                chara_data = cache.character_data[chara_id]
                chara_name = chara_data.name
                info_draw_2_text += f"  {chara_name}"
            
            info_draw_2_text += _("\n\n派遣载具：")
            if not self.send_vehicle_dict:
                info_draw_2_text += _(" 无")
            for vehicle_id in self.send_vehicle_dict:
                vehicle_name = game_config.config_vehicle[vehicle_id].name
                info_draw_2_text += f"  {vehicle_name} * {self.send_vehicle_dict[vehicle_id]}"
            
            # [修改] 增加耗时计算展示 (并显示在派遣载具下方)
            now_speed = 9
            if not self.send_vehicle_dict:
                now_speed = 1
            else:
                for vehicle_id in self.send_vehicle_dict:
                    v_speed = game_config.config_vehicle[vehicle_id].speed
                    now_speed = min(now_speed, v_speed)
                    
            if now_speed > 1:
                c_time_min = commision_data.time * 1440
                c_time_min = int(c_time_min * (0.9 ** now_speed))
                calc_day = round(c_time_min / 1440, 1)
            else:
                calc_day = commision_data.time
                
            info_draw_2_text += f"\n  (当前队伍速度: {now_speed} ，预计耗时计算: {calc_day}天)"
            
            info_draw_2_text += _("\n\n需求满足情况：\n")
            info_draw_2 = draw.NormalDraw()
            info_draw_2.text = info_draw_2_text
            info_draw_2.width = self.width
            info_draw_2.draw()

            # 绘制各项需求的达成度 (带颜色与A/B格式)
            p_text = f"  人数：{len(self.send_npc_list)} / {commision_data.people}"
            p_draw = draw.NormalDraw()
            p_draw.text = p_text.ljust(15)
            p_draw.style = "spring_green" if people_sat else "red"
            p_draw.draw()

            c_text = f"  运量：{now_capacity} / {commision_capacity_int} [{commision_data.time - 1}(天-1) * {commision_data.people}(人)]"
            c_draw = draw.NormalDraw()
            c_draw.text = c_text.ljust(35)
            c_draw.style = "spring_green" if cap_sat else "red"
            c_draw.draw()
            
            line_feed.draw()

            demand_label = draw.NormalDraw()
            demand_label.text = _("  其他需求：")
            demand_label.draw()
            
            # 使用底层原生函数动态解析每一个需求（包含金钱、能力、限定角色等所有类型）
            demand_str = str(commision_data.demand)
            if not demand_str or demand_str == "无" or demand_str == "-1":
                d = draw.NormalDraw()
                d.text = "无"
                d.style = "spring_green"
                d.draw()
            else:
                for part in demand_str.split("&"):
                    _temp_type, t_full, t_sat = process_commission_text(part, False, False, self.send_npc_list, "", "", True)
                    d = draw.NormalDraw()
                    d.text = f"[{t_full.strip()}] "
                    d.style = "spring_green" if t_sat else "red"
                    d.draw()

            line_feed.draw()

            # --- 调整派遣人员按钮 (未满足条件变黄) ---
            line_feed.draw()
            btn_npc_style = "standard" if (people_sat and deman_satify) else "gold_enrod"
            adjust_NPC_button_draw = draw.CenterButton(
                _("【调整派遣人员】"),
                _("调整派遣人员"),
                int(self.width / 2),
                cmd_func=self.adjust_send_npc,
                args=(commision_id,),
                normal_style=btn_npc_style
            )
            adjust_NPC_button_draw.draw()
            return_list.append(adjust_NPC_button_draw.return_text)

            # --- 调整使用载具按钮 (未满足条件变黄) ---
            btn_veh_style = "standard" if cap_sat else "gold_enrod"
            adjust_vehicle_button_draw = draw.CenterButton(
                _("【调整使用载具】"),
                _("调整使用载具"),
                int(self.width / 2),
                cmd_func=self.adjust_send_vehicle,
                args=(commision_capacity_int,),
                normal_style=btn_veh_style
            )
            adjust_vehicle_button_draw.draw()
            return_list.append(adjust_vehicle_button_draw.return_text)
            
            line_feed.draw()
            line_feed.draw()
            line.draw()

            # --- 执行委托按钮 (满足变绿且可点，不满足变灰不可点，占满单行) ---
            if all_satisfy:
                yes_draw = draw.CenterButton(
                    _("[执行委托]"),
                    _("执行委托"),
                    self.width,
                    cmd_func=self.send_commision,
                    args=(commision_id,),
                    normal_style="spring_green"
                )
                yes_draw.draw()
                return_list.append(yes_draw.return_text)
            else:
                yes_draw = draw.CenterDraw()
                yes_draw.text = _("[执行委托]")
                yes_draw.style = "deep_gray"
                yes_draw.width = self.width
                yes_draw.draw()

            line_feed.draw()
            
            # --- 返回按钮 (占满单行) ---
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), self.width)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            
            yrn = flow_handle.askfor_all(return_list)
            
            if yrn == _("执行委托") or yrn == back_draw.return_text:
                break

    def adjust_send_npc(self, commision_id: int):
        """
        调整派遣人员
        Keyword arguments:
        commision_id -- 委托编号
        """

        commision_data = game_config.config_commission[commision_id]
        commision_people = commision_data.people
        self.now_commision_id = commision_id

        # --- 解析限定干员用于自动勾选 ---
        required_chars_adv = []
        try:
            if commision_data.demand and commision_data.demand != "无" and str(commision_data.demand) != "-1":
                for d in str(commision_data.demand).split("&"):
                    parts = d.split("_")
                    if parts[0] == "c" and len(parts) >= 2:
                        required_chars_adv.append(int(parts[1]))
        except Exception:
            pass # 容错处理

        # --- 自动勾选限定干员 ---
        for npc_id in cache.npc_id_got:
            if npc_id == 0: continue
            if cache.character_data[npc_id].adv in required_chars_adv:
                if npc_id not in self.send_npc_list:
                    # 检查是否满足最基本的出勤前提，满足才自动勾选
                    if (handle_premise.handle_normal_2(npc_id) and 
                        handle_premise.handle_normal_7(npc_id) and 
                        not handle_premise.handle_self_equipment_damaged_ge_3(npc_id) and 
                        not handle_premise.handle_work_is_warden(npc_id) and 
                        not handle_premise.handle_is_assistant(npc_id) and 
                        not handle_premise.handle_self_visitor_flag_1(npc_id)):
                        self.send_npc_list.append(npc_id)

        # --- 修复原版Bug：保留已有队长，或指定第一个选中的人为队长 ---
        if getattr(self, 'lead_chara_id', 0) == 0 and len(self.send_npc_list) > 0:
            self.lead_chara_id = self.send_npc_list[0]
        elif not hasattr(self, 'lead_chara_id'):
            self.lead_chara_id = 0

        # 分页、筛选与排序的局部状态
        chara_list_page = 0
        sort_skill_id = 0
        filter_work = 0         # 0:不筛选, 1:有工作, 2:无工作
        filter_fall = 0         # 0:不筛选, 1:无, 2:有, 3:爱情, 4:隶属
        filter_daughter = 0     # 0:不筛选, 1:是, 2:否
        filter_collection = 0   # 0:不筛选, 1:是, 2:否
        
        sort_selected_first = True   # 已选优先(默认开启)
        sort_collection_first = False# 收藏优先(默认关闭)
        sort_work_toggle = False     # 工作排序(默认关闭)
        
        show_equip_modifier = True # 是否在面板中计算装备加成
        
        def pass_func(): pass

        # 辅助函数：计算字母Rank
        def get_rank_letter(value: int) -> str:
            if value >= 6: return "EX"
            if value == 5: return "S "
            if value == 4: return "A "
            if value == 3: return "B "
            if value == 2: return "C "
            if value == 1: return "D "
            return "E "

        # 辅助函数：获取Rank对应的颜色样式
        def get_rank_color(value: int) -> str:
            if value >= 6: return "levelex"      # 紫色/彩色
            if value == 5: return "gold_enrod"   # 金色
            if value == 4: return "spring_green" # 绿色
            if value == 3: return "light_sky_blue" # 蓝色
            if value == 2: return "standard"     # 白色
            if value == 1: return "deep_gray"    # 灰色
            return "deep_gray"                   # E也是深灰

        # 辅助函数：计算中英文混合字符串的显示宽度
        def get_display_width(text: str) -> int:
            return sum(2 if ord(c) > 127 else 1 for c in text)

        # 辅助函数：根据开关获取最终能力值 (加入装备判定)
        def get_eff_ability(n_id: int, a_id: int) -> int:
            val = cache.character_data[n_id].ability.get(a_id, 0)
            if show_equip_modifier:
                if handle_premise.handle_self_equipment_maintenance_ge_2(n_id) and val < 8:
                    val += 1
                if handle_premise.handle_self_equipment_damaged_ge_2(n_id) and val > 0:
                    val -= 1
            return val

        # 动态获取需要显示的工作技能字典，并过滤掉多余字符
        skill_columns = []
        for tem_ability_cid in game_config.config_ability:
            ability_data = game_config.config_ability[tem_ability_cid]
            if ability_data.ability_type == 4:  # 4 代表工作技能
                col_name = ability_data.name.replace(_("技能"), "")
                skill_columns.append((col_name, tem_ability_cid))

        while 1:
            return_list = []
            line = draw.LineDraw("-", self.width)
            line.draw()

            # --- 1. 绘制当前进度指示器 ---
            demand_label = draw.NormalDraw()
            demand_label.text = "\n当前派遣进度： "
            demand_label.draw()
            
            # 人数
            current_people = len(self.send_npc_list)
            people_col = "spring_green" if current_people >= commision_people else "red"
            people_draw = draw.NormalDraw()
            people_draw.text = f"[人数({current_people}/{commision_people})] "
            people_draw.style = people_col
            people_draw.draw()
            
            # 使用原生引擎直接解析并绘制其他所有需求进度（包括龙门币、材料、能力、限定角色等）
            demand_str = str(commision_data.demand)
            if demand_str and demand_str != "无" and demand_str != "-1":
                for part in demand_str.split("&"):
                    _temp_type, t_full, t_sat = process_commission_text(part, False, False, self.send_npc_list, "", "", True)
                    d = draw.NormalDraw()
                    d.text = f"[{t_full.strip()}] "
                    d.style = "spring_green" if t_sat else "red"
                    d.draw()
                
            line_feed.draw()

            # --- 2. 绘制当前派遣信息 ---
            info_text = _("（无意识/重伤/特殊职位等无法出勤）\n")
            info_text += _("队长：")
            if self.lead_chara_id != 0:
                info_text += cache.character_data[self.lead_chara_id].name
            else:
                info_text += _("无")
            info_text += _("。队员：")
            for npc_id in self.send_npc_list:
                if npc_id == self.lead_chara_id: continue
                info_text += cache.character_data[npc_id].name + " "
            
            info_draw = draw.NormalDraw()
            info_draw.text = info_text + "\n\n"
            info_draw.width = self.width
            info_draw.draw()

            # --- 3. 绘制筛选与排序按钮区 ---
            # 3. 绘制筛选与排序按钮区
            filter_draw = draw.NormalDraw()
            filter_draw.text = _(" 筛选: ")
            filter_draw.draw()
            
            btn_width = 18
            work_filter_names = [_("不筛选"), _("有"), _("无")]
            fall_filter_names = [_("不筛选"), _("无"), _("有"), _("爱情"), _("隶属")]
            bool_filter_names = [_("不筛选"), _("是"), _("否")]

            btn_work = draw.LeftButton(_("[工作:{0}]").format(work_filter_names[filter_work]), "filter_work", btn_width, cmd_func=pass_func, normal_style="gold_enrod" if filter_work else "standard")
            btn_work.draw()
            return_list.append(btn_work.return_text)

            btn_fall = draw.LeftButton(_("[陷落:{0}]").format(fall_filter_names[filter_fall]), "filter_fall", btn_width, cmd_func=pass_func, normal_style="gold_enrod" if filter_fall else "standard")
            btn_fall.draw()
            return_list.append(btn_fall.return_text)
            
            btn_daughter = draw.LeftButton(_("[女儿:{0}]").format(bool_filter_names[filter_daughter]), "filter_daughter", btn_width, cmd_func=pass_func, normal_style="gold_enrod" if filter_daughter else "standard")
            btn_daughter.draw()
            return_list.append(btn_daughter.return_text)
            
            btn_collection = draw.LeftButton(_("[收藏:{0}]").format(bool_filter_names[filter_collection]), "filter_collection", btn_width, cmd_func=pass_func, normal_style="gold_enrod" if filter_collection else "standard")
            btn_collection.draw()
            return_list.append(btn_collection.return_text)
            
            line_feed.draw()
            
            sort_draw = draw.NormalDraw()
            sort_draw.text = _(" 排序: ")
            sort_draw.draw()
            
            btn_sort_sel = draw.LeftButton(_("[已选优先]"), "sort_sel", 12, cmd_func=pass_func, normal_style="gold_enrod" if sort_selected_first else "standard")
            btn_sort_sel.draw()
            return_list.append(btn_sort_sel.return_text)
            
            btn_sort_col = draw.LeftButton(_("[收藏优先]"), "sort_col", 12, cmd_func=pass_func, normal_style="gold_enrod" if sort_collection_first else "standard")
            btn_sort_col.draw()
            return_list.append(btn_sort_col.return_text)
            
            btn_sort_work = draw.LeftButton(_("[工作排序]"), "sort_work", 12, cmd_func=pass_func, normal_style="gold_enrod" if sort_work_toggle else "standard")
            btn_sort_work.draw()
            return_list.append(btn_sort_work.return_text)
            
            equip_toggle_status = _("开") if show_equip_modifier else _("关")
            btn_equip_toggle = draw.LeftButton(_("[装备加成:{0}] ").format(equip_toggle_status), "toggle_equip", 18, cmd_func=pass_func, normal_style="gold_enrod" if show_equip_modifier else "standard")
            btn_equip_toggle.draw()
            return_list.append(btn_equip_toggle.return_text)

            line_feed.draw()
            
            sort_draw2 = draw.NormalDraw()
            sort_draw2.text = _(" 技能排序: ")
            sort_draw2.draw()
            
            btn_default = draw.LeftButton(
                _("[默认ID] "), "sort_0", 10, 
                cmd_func=pass_func, normal_style="gold_enrod" if sort_skill_id == 0 else "standard"
            )
            btn_default.draw()
            return_list.append(btn_default.return_text)
            
            # 技能排序按钮
            for name, sid in skill_columns:
                btn_text = f"[{name}] "
                btn_width = get_display_width(btn_text)
                btn = draw.LeftButton(
                    btn_text, f"sort_{sid}", btn_width, 
                    cmd_func=pass_func, normal_style="gold_enrod" if sort_skill_id == sid else "standard"
                )
                btn.draw()
                return_list.append(btn.return_text)

            line_feed.draw()
            line_feed.draw()
            line.draw()

            # --- 4. 绘制表头 (包含动态高亮与独立的豎槓) ---
            name_btn_width = 24 
            
            prefix_draw = draw.NormalDraw()
            prefix_draw.text = " " * name_btn_width
            prefix_draw.draw()
            
            for col_name, _id in skill_columns:
                col_draw = draw.NormalDraw()
                col_draw.text = f"{col_name}"
                if sort_skill_id == _id:
                    col_draw.style = "gold_enrod"
                else:
                    col_draw.style = "standard"
                col_draw.draw()
                
                bar_draw = draw.NormalDraw()
                bar_draw.text = "|"
                bar_draw.draw()
                
            suffix_draw = draw.NormalDraw()
            suffix_draw.text = "装备|当前工作"
            suffix_draw.draw()
            
            line_feed.draw()

            # --- 5. 获取并过滤人员列表 ---
            valid_npc_list = []
            for npc_id in cache.npc_id_got:
                if npc_id == 0: continue
                if handle_premise.handle_self_visitor_flag_1(npc_id): continue
                if handle_premise.handle_is_assistant(npc_id): continue
                if handle_premise.handle_work_is_warden(npc_id): continue
                if not handle_premise.handle_normal_2(npc_id): continue
                if not handle_premise.handle_normal_7(npc_id): continue
                if handle_premise.handle_self_equipment_damaged_ge_3(npc_id): continue
                
                char_data = cache.character_data[npc_id]
                
                # 筛选工作
                has_work = char_data.work.work_type != 0
                if filter_work == 1 and not has_work: continue
                if filter_work == 2 and has_work: continue
                
                # 筛选陷落 (0:不筛选, 1:无, 2:有, 3:爱情, 4:隶属)
                is_love = any(char_data.talent.get(i) for i in [201, 202, 203, 204])
                is_obey = any(char_data.talent.get(i) for i in [211, 212, 213, 214])
                has_fall = is_love or is_obey
                if filter_fall == 1 and has_fall: continue
                if filter_fall == 2 and not has_fall: continue
                if filter_fall == 3 and not is_love: continue
                if filter_fall == 4 and not is_obey: continue

                # 筛选女儿 (0:不筛选, 1:是, 2:否)
                is_daughter = char_data.talent.get(311) or char_data.talent.get(312) or (hasattr(char_data, 'relationship') and char_data.relationship.father_id == 0)
                if filter_daughter == 1 and not is_daughter: continue
                if filter_daughter == 2 and is_daughter: continue

                # 筛选收藏 (0:不筛选, 1:是, 2:否) (值为1即代表收藏)
                is_collected = char_data.chara_setting.get(2, 0) == 1
                if filter_collection == 1 and not is_collected: continue
                if filter_collection == 2 and is_collected: continue

                valid_npc_list.append(npc_id)
            
            # 执行综合排序逻辑
            valid_npc_list.sort(
                key=lambda x: (
                    0 if (sort_selected_first and x in self.send_npc_list) else 1,
                    0 if (sort_collection_first and cache.character_data[x].chara_setting.get(2, 0) == 1) else 1,
                    -get_eff_ability(x, sort_skill_id) if sort_skill_id != 0 else 0,
                    cache.character_data[x].work.work_type if sort_work_toggle else 0,
                    x
                )
            )

            # --- 6. 分页计算 ---
            chara_per_page = 20
            total_pages = max(1, (len(valid_npc_list) + chara_per_page - 1) // chara_per_page)
            if chara_list_page >= total_pages: chara_list_page = total_pages - 1
            if chara_list_page < 0: chara_list_page = 0
            
            start_idx = chara_list_page * chara_per_page
            end_idx = min(start_idx + chara_per_page, len(valid_npc_list))
            current_page_charas = valid_npc_list[start_idx:end_idx]

            # --- 7. 遍历渲染当前页干员 ---
            for npc_id in current_page_charas:
                character_data = cache.character_data[npc_id]
                name = character_data.name
                id_str = str(character_data.adv).rjust(4, '0')
                
                # 勾选框、星号与名字
                check_mark = "√" if npc_id in self.send_npc_list else " "
                is_collected = character_data.chara_setting.get(2, 0) == 1
                star_str = "⭐" if is_collected else "  "
                
                name_str = f"[{check_mark}][{id_str}]{star_str}{name}"
                btn_style = "gold_enrod" if npc_id in self.send_npc_list else "standard"
                display_name_len = get_display_width(name_str)
                name_pad = " " * max(0, name_btn_width - display_name_len)
                
                name_btn = draw.LeftButton(
                    name_str + name_pad, str(npc_id), name_btn_width, 
                    normal_style=btn_style,
                    cmd_func=self.select_this_npc, args=(npc_id,)
                )
                name_btn.draw()
                return_list.append(name_btn.return_text)

                # 渲染工作技能数值数据
                for col_name, col_id in skill_columns:
                    val = get_eff_ability(npc_id, col_id)
                    rank = get_rank_letter(val)
                    rank_color = get_rank_color(val)
                    
                    rank_draw = draw.NormalDraw()
                    rank_draw.text = rank
                    rank_draw.style = rank_color
                    rank_draw.draw()
                    
                    val_draw = draw.NormalDraw()
                    col_width = get_display_width(col_name)
                    val_str = f"{val}".rjust(2, " ")
                    padding = " " * max(0, col_width - 4)
                    val_draw.text = f"{val_str}{padding}|"
                    val_draw.draw()
                
                # 渲染装备状态
                equip_text = "正常"
                equip_color = "standard"
                if handle_premise.handle_self_equipment_damaged_ge_2(npc_id):
                    equip_text = "损坏"
                    equip_color = "red"
                elif handle_premise.handle_self_equipment_maintenance_ge_2(npc_id):
                    equip_text = "完美"
                    equip_color = "spring_green"
                
                equip_draw = draw.NormalDraw()
                equip_draw.text = f"{equip_text}"
                equip_draw.style = equip_color
                equip_draw.draw()

                # 將裝備與工作間的 | 符號獨立繪製
                bar_draw = draw.NormalDraw()
                bar_draw.text = "|"
                bar_draw.draw()

                # 渲染当前工作
                work_type_id = character_data.work.work_type
                work_name = game_config.config_work_type[work_type_id].name
                work_draw = draw.NormalDraw()
                work_draw.text = f"{work_name}"
                work_draw.draw()
                
                line_feed.draw()

            # --- 8. 绘制底部：翻页操作区 ---
            line_feed.draw()
            line.draw()
            
            if chara_list_page > 0:
                prev_page_btn = draw.LeftButton("[888]上一页", "888", 12, cmd_func=pass_func)
                prev_page_btn.draw()
                return_list.append(prev_page_btn.return_text)
            else:
                prev_page_btn = draw.NormalDraw()
                prev_page_btn.text = "[888]上一页"
                prev_page_btn.style = "deep_gray"
                prev_page_btn.width = 12
                prev_page_btn.draw()
            
            page_info = draw.NormalDraw()
            page_info.text = f"  [{chara_list_page + 1}/{total_pages}页]  "
            page_info.draw()
            
            if chara_list_page < total_pages - 1:
                next_page_btn = draw.LeftButton("[222]下一页", "222", 12, cmd_func=pass_func)
                next_page_btn.draw()
                return_list.append(next_page_btn.return_text)
            else:
                next_page_btn = draw.NormalDraw()
                next_page_btn.text = "[222]下一页"
                next_page_btn.style = "deep_gray"
                next_page_btn.width = 12
                next_page_btn.draw()

            line_feed.draw()
            line_feed.draw()
            back_draw = draw.CenterButton(_("[完成 / 返回]"), _("返回"), window_width)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            
            # --- 9. 处理界面按键 ---
            yrn = flow_handle.askfor_all(return_list)
            
            if yrn == "888":
                chara_list_page -= 1
            elif yrn == "222":
                chara_list_page += 1
            elif yrn == "filter_work":
                filter_work = (filter_work + 1) % 3
                chara_list_page = 0
            elif yrn == "filter_fall":
                filter_fall = (filter_fall + 1) % 5
                chara_list_page = 0
            elif yrn == "filter_daughter":
                filter_daughter = (filter_daughter + 1) % 3
                chara_list_page = 0
            elif yrn == "filter_collection":
                filter_collection = (filter_collection + 1) % 3
                chara_list_page = 0
            elif yrn == "sort_sel":
                sort_selected_first = not sort_selected_first
                chara_list_page = 0
            elif yrn == "sort_col":
                sort_collection_first = not sort_collection_first
                chara_list_page = 0
            elif yrn == "sort_work":
                sort_work_toggle = not sort_work_toggle
                chara_list_page = 0
            elif yrn == "toggle_equip":
                show_equip_modifier = not show_equip_modifier
            elif yrn.startswith("sort_"):
                sort_skill_id = int(yrn.split("_")[1])
                chara_list_page = 0
            elif yrn == back_draw.return_text:
                break

    def select_this_npc(self, character_id: int):
        """
        选择当前人物
        Keyword arguments:
        character_id -- 人物id
        """
        if character_id in self.send_npc_list:
            self.send_npc_list.remove(character_id)
            # 如果队长被取消
            if character_id == self.lead_chara_id:
                # 如果还有其他人，则第一个人为队长
                if len(self.send_npc_list):
                    self.lead_chara_id = self.send_npc_list[0]
                else:
                    self.lead_chara_id = 0
        else:
            # 如果人数已经满了，则不添加
            max_people = game_config.config_commission[self.now_commision_id].people
            if len(self.send_npc_list) >= max_people:
                return
            self.send_npc_list.append(character_id)
            # 第一个被任命的人为队长
            if len(self.send_npc_list) == 1:
                self.lead_chara_id = character_id

    def add_this_vehicle(self, vehicle_id: int):
        """
        增加一辆载具
        Keyword arguments:
        vehicle_id -- 载具id
        """
        if vehicle_id not in self.send_vehicle_dict:
            self.send_vehicle_dict[vehicle_id] = 1
        else:
            self.send_vehicle_dict[vehicle_id] += 1
        # 最大不会超过可派遣数量
        vehicle_count = cache.rhodes_island.vehicles[vehicle_id][0] - cache.rhodes_island.vehicles[vehicle_id][1]
        if self.send_vehicle_dict[vehicle_id] > vehicle_count:
            self.send_vehicle_dict[vehicle_id] = vehicle_count

    def reduce_this_vehicle(self, vehicle_id: int):
        """
        减少一辆载具
        Keyword arguments:
        vehicle_id -- 载具id
        """
        if vehicle_id in self.send_vehicle_dict:
            self.send_vehicle_dict[vehicle_id] -= 1
            if self.send_vehicle_dict[vehicle_id] <= 0:
                self.send_vehicle_dict.pop(vehicle_id)

    def send_commision(self, commision_id: int):
        """
        派遣委托
        Keyword arguments:
        commision_id -- 委托编号
        """
        from Script.Design import second_behavior

        commision_data = game_config.config_commission[commision_id]
        commision_people = commision_data.people
        if len(self.send_npc_list) < commision_people:
            return

        # 结算队长
        if self.lead_chara_id:
            # 将队长的id调为列表的第一位
            self.send_npc_list.remove(self.lead_chara_id)
            self.send_npc_list.insert(0, self.lead_chara_id)
            # 二段行为
            second_behavior.character_get_second_behavior(self.lead_chara_id, "start_field_commission_as_leader")
            talk.must_show_talk_check(self.lead_chara_id)

        # 初步预估时间
        commision_time = int(commision_data.time)
        new_time = game_time.get_sub_date(day=commision_time)

        # 添加到进行中的委托
        cache.rhodes_island.ongoing_field_commissions[commision_id] = [self.send_npc_list, new_time, []]
        # 消耗资源
        get_commission_demand_and_reward(commision_id, self.send_npc_list, False, True)
        # 遍历派遣人员，设为派遣状态，并离线
        from Script.Settle import default
        for character_id in self.send_npc_list:
            cache.character_data[character_id].sp_flag.field_commission = commision_id
            handle_premise.settle_chara_unnormal_flag(character_id, 7)
            default.handle_chara_off_line(character_id, 1, change_data = game_type.CharacterStatusChange(), now_time = cache.game_time)
        # 结算派遣的载具
        now_vehicle_list = []
        for vehicle_id in self.send_vehicle_dict:
            cache.rhodes_island.vehicles[vehicle_id][1] += self.send_vehicle_dict[vehicle_id]
            for i in range(self.send_vehicle_dict[vehicle_id]):
                now_vehicle_list.append(vehicle_id)
        cache.rhodes_island.ongoing_field_commissions[commision_id][2] = now_vehicle_list
        
        # 结算速度对时间的影响
        min_speed = 9
        # [修改] 修复没带载具时原版默认算作9速的bug
        if not now_vehicle_list:
            min_speed = 1
            
        for vehicle_id in now_vehicle_list:
            vehicle_speed = game_config.config_vehicle[vehicle_id].speed
            min_speed = min(min_speed, vehicle_speed)
            
        # 如果有实际速度加成，则减少时间
        if min_speed > 1:
            commision_time_by_min = commision_time * 1440
            # 每点速度则将总时间乘以0.9
            commision_time_by_min = int(commision_time_by_min * (0.9 ** min_speed))
            new_time_by_speed = game_time.get_sub_date(minute=commision_time_by_min)
            new_day = round(commision_time_by_min / 1440, 1)
            # 重新设置时间
            cache.rhodes_island.ongoing_field_commissions[commision_id][1] = new_time_by_speed
        # 如果没有实际速度加成，则不减少时间
        else:
            new_time_by_speed = new_time
            new_day = commision_time

        # 绘制委托信息
        draw_text = ""
        draw_text += _("\n\n已派遣 ")
        for character_id in self.send_npc_list:
            character_data = cache.character_data[character_id]
            character_name = character_data.name
            draw_text += f"{character_name} "
        draw_text += _("执行委托：")
        commision_name = commision_data.name
        draw_text += commision_name
        draw_text += _("，耗时：")
        draw_text += str(new_day)
        draw_text += _("天，将在 ")
        new_time_text = game_time.get_date_until_day(new_time_by_speed)
        draw_text += new_time_text
        draw_text += _(" 返回\n\n")
        info_draw = draw.WaitDraw()
        info_draw.text = draw_text
        info_draw.style = "gold_enrod"
        info_draw.width = window_width
        info_draw.draw()

        # 清空派遣人员与载具
        self.send_npc_list = []
        self.send_vehicle_dict = {}


    def adjust_send_vehicle(self, commision_capacity_int: int):
        """
        调整派遣载具
        Keyword arguments:
        commision_capacity_int -- 需要的载具运量
        """
        
        # 辅助函数：计算中英文混合字符串的显示宽度
        def get_display_width(text: str) -> int:
            return sum(2 if ord(c) > 127 else 1 for c in text)

        while 1:
            return_list = []
            line = draw.LineDraw("-", self.width)
            line.draw()

            # 绘制可派遣载具
            info_draw_2 = draw.NormalDraw()
            info_draw_2.text = _("\n 可派遣载具：\n\n")
            info_draw_2.width = self.width
            info_draw_2.draw()

            for vehicle_cid in cache.rhodes_island.vehicles:
                # 如果没有可以派遣的载具，则不绘制
                vehicle_count = cache.rhodes_island.vehicles[vehicle_cid][0] - cache.rhodes_island.vehicles[vehicle_cid][1]
                if vehicle_count <= 0:
                    continue
                
                vehicle_data = game_config.config_vehicle[vehicle_cid]
                vehicle_speed = str(vehicle_data.speed).rjust(2)
                vehicle_capacity = str(vehicle_data.capacity).rjust(3)
                vehicle_special = vehicle_data.special
                
                now_choice_count = 0
                if vehicle_cid in self.send_vehicle_dict:
                    now_choice_count = self.send_vehicle_dict[vehicle_cid]

                # 排版载具信息，利用 get_display_width 补齐空格并遵循多语言格式化规范
                base_str = f"[{str(vehicle_cid).rjust(2,'0')}]{vehicle_data.name}"
                pad_1 = " " * max(0, 24 - get_display_width(base_str))
                
                stats_str = _("| 速度:{0} | 运载:{1} | 特效:{2}").format(vehicle_speed, vehicle_capacity, vehicle_special)
                pad_2 = " " * max(0, 48 - get_display_width(stats_str))
                
                count_str = _("| 选定: {0}/{1}").format(now_choice_count, vehicle_count)
                pad_3 = " " * max(0, 16 - get_display_width(count_str))
                
                draw_text = " " + base_str + pad_1 + stats_str + pad_2 + count_str + pad_3

                info_draw = draw.NormalDraw()
                info_draw.text = draw_text
                # 有选择的载具标为橘色
                info_draw.style = "gold_enrod" if now_choice_count > 0 else "standard"
                info_draw.draw()

                # 增加一辆
                button_draw_add = draw.LeftButton(
                    _("[+1]"),
                    f"\n{vehicle_cid}+1",
                    6,
                    cmd_func=self.add_this_vehicle,
                    args=vehicle_cid,
                )
                button_draw_add.draw()
                return_list.append(button_draw_add.return_text)
                
                # 加上小空格分隔按钮
                space_draw = draw.NormalDraw()
                space_draw.text = " "
                space_draw.draw()

                # 减少一辆
                button_draw_sub = draw.LeftButton(
                    _("[-1]"),
                    f"\n{vehicle_cid}-1",
                    6,
                    cmd_func=self.reduce_this_vehicle,
                    args=vehicle_cid,
                )
                button_draw_sub.draw()
                return_list.append(button_draw_sub.return_text)

                line_feed.draw()

            now_capacity = 0 # 当前运载量
            now_speed = 99 # 当前速度
            now_effect = [] # 当前效果

            # 遍历已选择的载具
            for vehicle_id in self.send_vehicle_dict:
                vehicle_data = game_config.config_vehicle[vehicle_id]
                now_capacity += vehicle_data.capacity * self.send_vehicle_dict[vehicle_id]
                now_speed = min(now_speed, vehicle_data.speed)
                if vehicle_data.special != "无" and vehicle_data.special not in now_effect:
                    now_effect.append(vehicle_data.special)
            
            # 如果没有选择载具，速度算作1
            if now_speed == 99:
                now_speed = 1

            # 遍历效果，输出效果文本
            effect_text = ""
            for effect in now_effect:
                effect_text += f"{effect} "
            if not effect_text:
                effect_text = "无"

            # 结合当前速度与基础时间，计算实际消耗天数
            commision_data = game_config.config_commission[self.commission_id]
            if now_speed > 1:
                c_time_min = commision_data.time * 1440
                c_time_min = int(c_time_min * (0.9 ** now_speed))
                calc_day = round(c_time_min / 1440, 1)
            else:
                calc_day = commision_data.time

            # 绘制当前载具的总信息
            line_feed.draw()
            
            info_draw_1 = draw.NormalDraw()
            info_draw_1.text = _("\n 当前总运载量 / 需求运载量：")
            info_draw_1.draw()
            
            # 运量不足标红，足够标绿
            info_draw_cap = draw.NormalDraw()
            info_draw_cap.text = f"{now_capacity} / {commision_capacity_int}\n"
            info_draw_cap.style = "spring_green" if now_capacity >= commision_capacity_int else "red"
            info_draw_cap.draw()
            
            info_draw_3 = draw.NormalDraw()
            info_draw_3.text = _(" 当前队伍速度：{0} (预计耗时计算: {1}天)\n").format(now_speed, calc_day)
            info_draw_3.text += _(" 附加特殊效果：{0}\n").format(effect_text)
            info_draw_3.draw()

            line_feed.draw()
            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                break
