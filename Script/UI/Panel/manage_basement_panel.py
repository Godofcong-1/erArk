from typing import Dict, List
from types import FunctionType
from Script.Core import cache_control, game_type, get_text, flow_handle, constant
from Script.Design import basement, attr_calculation, handle_premise, game_time
from Script.UI.Moudle import draw, panel
from Script.UI.Panel import  see_character_info_panel
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


def change_npc_work_out(width):
    """
    调整干员的工作岗位
    """
    now_panel = Change_Npc_Work_Panel(width)
    now_panel.draw()


class Manage_Basement_Panel:
    """
    用于显示基建界面面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.now_panel = _("罗德岛资源总览")
        """ 当前绘制的页面 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """
        self.show_resource_type_dict: Dict = {_("货币"): True,_("材料"): False, _("药剂"): False, _("乳制品"): False, _("香水"): False}

    def draw(self):
        """绘制对象"""

        title_text = _("管理罗德岛")
        panel_list = [(_("罗德岛资源总览")), (_("各部门工作概况")), (_("全干员一览"))]
        department_son_panel_button_dict = {
            _("工程部"):[_("[基建系统]")],
            _("制造加工区"):[_("[生产系统]")],
            _("图书馆"):[_("[图书馆管理系统]")],
            _("贸易区"):[_("[资源交易系统]")],
            _("文职部"):[_("[招募系统]")],
            _("访客区"):[_("[势力外交系统]"), _("[邀请访客系统]")],
            _("机库"):[_("[外勤委托系统]"), _("[载具管理系统]")],
            _("疗养庭院"):[_("[农业系统]")],
            _("关押区"):[_("[监禁调教系统]")],
            }

        title_draw = draw.TitleLineDraw(title_text, self.width)

        # 进行一轮刷新
        basement.update_work_people()
        basement.update_facility_people()
        basement.get_base_updata()

        while 1:
            return_list = []
            title_draw.draw()

            # 绘制主面板
            for now_panel in panel_list:
                if now_panel == self.now_panel:
                    now_draw = draw.CenterDraw()
                    now_draw.text = f"[{now_panel}]"
                    now_draw.style = "onbutton"
                    now_draw.width = self.width / len(panel_list)
                    now_draw.draw()
                else:
                    now_draw = draw.CenterButton(
                        f"[{now_panel}]",
                        f"\n{now_panel}",
                        self.width / len(panel_list),
                        cmd_func=self.change_panel,
                        args=(now_panel,),
                    )
                    now_draw.draw()
                    return_list.append(now_draw.return_text)
            line_feed.draw()
            line = draw.LineDraw("+", self.width)
            line.draw()

            # 罗德岛资源总览
            if self.now_panel == _("罗德岛资源总览"):

                self.resouce_list = [_("货币"), _("材料"), _("药剂"), _("乳制品"), _("香水")]

                all_info_draw = draw.NormalDraw()
                all_info_draw.text = ""
                all_info_draw.text += _(" 当前仓库容量（单资源存放上限）：{0}\n\n").format(cache.rhodes_island.warehouse_capacity)
                all_info_draw.width = self.width
                all_info_draw.draw()

                # 遍历全资源类型
                for resouce in self.resouce_list:

                    # 判断是否显示该类型的资源
                    if self.show_resource_type_dict[resouce]:
                        draw_text = f" ▼[{resouce}]"
                    else:
                        draw_text = f" ▶[{resouce}]"
                    button_draw = draw.LeftButton(
                    f"{draw_text}",
                    f"{resouce}",
                    len(draw_text) * 2,
                    cmd_func=self.settle_show_resource_type,
                    args=(resouce)
                    )
                    button_draw.draw()
                    return_list.append(button_draw.return_text)
                    line_feed.draw()

                    if not self.show_resource_type_dict[resouce]:
                        line_feed.draw()
                        continue

                    # 遍历该类型的资源
                    all_info_draw = draw.NormalDraw()
                    all_info_draw.width = self.width
                    all_info_draw.text = ""
                    for material_id in cache.rhodes_island.materials_resouce:
                        material_data  = game_config.config_resouce[material_id]
                        if material_data.type == resouce:
                            all_info_draw.text += f"\n  {material_data.name}：{cache.rhodes_island.materials_resouce[material_id]}"
                    all_info_draw.text += "\n"
                    all_info_draw.draw()
                    line_feed.draw()

            # 各部门工作概况
            elif self.now_panel == _("各部门工作概况"):

                # 遍历全部门
                department_text_list = []
                for all_cid in game_config.config_facility:
                    facility_data = game_config.config_facility[all_cid]
                    if facility_data.type == -1:
                        department_text_list.append(game_config.config_facility[all_cid].name)

                all_info_draw = draw.NormalDraw()

                # 统计各部门岗位的工作干员数量
                work_people_now,people_max = cache.rhodes_island.work_people_now,len(cache.npc_id_got)

                all_info_draw.text = _("\n 当前工作中干员/总干员：{0}/{1}").format(work_people_now, people_max)
                all_info_draw.text += _("\n ↓点击[部门名]或[系统名]可查看对应详情，没有系统也没有工作的部门是未实装的空白部门\n\n")
                all_info_draw.draw()

                # 遍历全部门
                for department in department_text_list:
                    department_text = f"[{department}]"
                    draw_width = max(len(department_text) * 2, 18)

                    # 输出部门按钮
                    space_draw = draw.NormalDraw()
                    space_draw.text = "  "
                    space_draw.draw()
                    button_draw = draw.CenterButton(
                        department_text,
                        f"\n{department}",
                        draw_width,
                        cmd_func=self.show_department,
                        args=(department,),
                    )
                    button_draw.draw()
                    return_list.append(button_draw.return_text)

                    # 输出冒号
                    space_draw = draw.NormalDraw()
                    space_draw.text = "："
                    space_draw.draw()

                    # 如果该部门有子系统的话，绘制子系统按钮
                    department_count = 2
                    if department in department_son_panel_button_dict:
                        for button_text in department_son_panel_button_dict[department]:
                            draw_width = max(len(button_text) * 2, 22)
                            button_draw = draw.CenterButton(
                                button_text,
                                f"\n{button_text}",
                                draw_width,
                                cmd_func=self.jump_to_son_panel,
                                args=(button_text)
                            )
                            button_draw.draw()
                            return_list.append(button_draw.return_text)
                            department_count -= 1
                    # 为没有部门子系统的部门补齐空白绘制
                    while department_count > 0:
                        space_draw = draw.NormalDraw()
                        space_draw.text = " " * 22
                        space_draw.draw()
                        department_count -= 1
                    # 输出冒号
                    space_draw = draw.NormalDraw()
                    space_draw.text = "："
                    space_draw.draw()

                    # 输出部门工作人员数量
                    all_info_draw.text = ""
                    for all_cid in game_config.config_work_type:
                        work_data = game_config.config_work_type[all_cid]
                        if work_data.department == department:
                            all_info_draw.text += f"  {work_data.name} — {len(cache.rhodes_island.all_work_npc_set[all_cid])}"
                    if department == _("医疗部"):
                        patient_now = cache.rhodes_island.patient_now
                        all_info_draw.text += _("  病人 — {0}").format(patient_now)
                    elif department == _("机库"):
                        field_people_now = 0
                        for cid in cache.rhodes_island.ongoing_field_commissions:
                            field_people_now += len(cache.rhodes_island.ongoing_field_commissions[cid][0])
                        all_info_draw.text += _("  外勤干员 — {0}").format(field_people_now)
                    elif department == _("关押区"):
                        prisoner_now = len(cache.rhodes_island.current_prisoners)
                        all_info_draw.text += _("  囚犯 — {0}").format(prisoner_now)
                    all_info_draw.draw()
                    line_feed.draw()

                # 收入
                all_income = str(cache.rhodes_island.all_income)
                all_info_draw.text = _("\n  截至目前为止，今日各部门龙门币总收入为：{0}\n\n").format(all_income)
                all_info_draw.width = self.width
                all_info_draw.draw()

                button_draw = draw.LeftButton(
                    _("[001]调整干员岗位"),
                    f"\n1",
                    self.width ,
                    cmd_func=change_npc_work_out,
                    args=self.width
                )
                button_draw.draw()
                return_list.append(button_draw.return_text)

            # 全干员一览
            elif self.now_panel == _("全干员一览"):
                chara_count = 0
                for character_id in cache.npc_id_got:
                    character_data = cache.character_data[character_id]
                    name = character_data.name
                    id = str(character_data.adv).rjust(4,'0')
                    draw_width = self.width / 6
                    # 输出干员名字
                    now_draw_text = f"[{id}]{name}"
                    name_draw = draw.LeftButton(
                        now_draw_text, name, draw_width, cmd_func=self.see_attr, args=(character_id,)
                    )
                    name_draw.draw()
                    return_list.append(name_draw.return_text)
                    chara_count += 1
                    if chara_count % 6 == 0:
                        line_feed.draw()

            line_feed.draw()
            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def change_panel(self, now_panel: str):
        """
        切换当前面板显示
        Keyword arguments:
        panel -- 要切换的面板类型
        """

        self.now_panel = now_panel

    def jump_to_son_panel(self, son_panel: str):
        """
        跳转子面板
        Keyword arguments:
        panel -- 要切换的面板类型
        """

        from Script.UI.Panel import building_panel, manage_assembly_line_panel, manage_library, resource_exchange_panel, recruit_panel, nation_diplomacy_panel, invite_visitor_panel, agriculture_production_panel, field_commission_panel, manage_vehicle_panel, confinement_and_training

        if _("基建系统") in son_panel:
            now_panel = building_panel.Building_Panel(self.width)
        elif _("生产系统") in son_panel:
            now_panel = manage_assembly_line_panel.Manage_Assembly_Line_Panel(self.width)
        elif _("图书馆管理系统") in son_panel:
            now_panel = manage_library.Manage_Library_Panel(self.width)
        elif _("资源交易系统") in son_panel:
            now_panel = resource_exchange_panel.Resource_Exchange_Line_Panel(self.width)
        elif _("招募系统") in son_panel:
                now_panel =recruit_panel.Recruit_Panel(self.width)
        elif _("势力外交系统") in son_panel:
            now_panel = nation_diplomacy_panel.Nation_Diplomacy_Panel(self.width)
        elif _("邀请访客系统") in son_panel:
            now_panel = invite_visitor_panel.Invite_Visitor_Panel(self.width)
        elif _("外勤委托系统") in son_panel:
            now_panel = field_commission_panel.Field_Commission_Panel(self.width)
        elif _("载具管理系统") in son_panel:
            now_panel = manage_vehicle_panel.Manage_Vehicle_Panel(self.width)
        elif _("农业系统") in son_panel:
            now_panel = agriculture_production_panel.Agriculture_Production_Panel(self.width)
        elif _("监禁调教系统") in son_panel:
            # 如果没有监狱长，则不显示监禁调教系统
            if not handle_premise.handle_have_warden(0):
                info_draw = draw.WaitDraw()
                info_draw.text = _("\n○未任命监狱长，无法进入监禁调教系统\n")
                info_draw.style = "gold_enrod"
                info_draw.width = self.width
                info_draw.draw()
                return
            else:
                now_panel = confinement_and_training.Confinement_And_Training_Manage_Panel(self.width)
        now_panel.draw()

    def show_department(self, department: str):
        """
        显示部门情况
        Keyword arguments:
        department -- 要显示的部门
        """

        while 1:
            title_draw = draw.TitleLineDraw(department, self.width)
            title_draw.draw()
            return_list = []
            now_draw = draw.NormalDraw()

            now_text = _("\n当前{0}部门情况：").format(department)
            for all_cid in game_config.config_work_type:
                work_data = game_config.config_work_type[all_cid]
                if work_data.department == department:
                    now_text+= _("\n  当前正在工作的{0}：").format(work_data.name)
                    if len(cache.rhodes_island.all_work_npc_set[all_cid]):
                        for npc_id in cache.rhodes_island.all_work_npc_set[all_cid]:
                            npc_name = cache.character_data[npc_id].name
                            now_text += f" {npc_name}"
                    else:
                        now_text += _(" 暂无")

            if department == _("工程部"):
                # 故障地点与设施损坏数
                now_text += _("\n  当前故障地点与设施损坏数：")
                facility_damage_text = ""
                now_count = 0
                for scene_path_str in cache.rhodes_island.facility_damage_data:
                    # 每行显示3个
                    if now_count % 3 == 0:
                        facility_damage_text += "\n"
                    facility_damage_text += f"    {scene_path_str}-{cache.rhodes_island.facility_damage_data[scene_path_str]}"
                    now_count += 1
                if facility_damage_text == "":
                    facility_damage_text = _("\n    无")
                now_text += facility_damage_text
                # 检修人员与其负责地点
                now_text += _("\n  当前检修人员与其负责地点：")
                npc_and_place_text = ""
                now_count = 0
                for chara_id in cache.rhodes_island.maintenance_place:
                    if len(cache.rhodes_island.maintenance_place[chara_id]):
                        if now_count % 3 == 0:
                            npc_and_place_text += "\n"
                        chara_name = cache.character_data[chara_id].name
                        npc_and_place_text += f"    {chara_name}-{cache.rhodes_island.maintenance_place[chara_id]}"
                        now_count += 1
                if npc_and_place_text == "":
                    npc_and_place_text = _("\n    无")
                now_text += npc_and_place_text

            elif department == _("医疗部"):
                patient_cured,patient_now = str(cache.rhodes_island.patient_cured),str(cache.rhodes_island.patient_now)
                now_text += _("\n  今日已治疗患者数/排队中患者数：{0}/{1}").format(patient_cured, patient_now)
                cure_income = str(cache.rhodes_island.cure_income)
                now_text += _("\n  截至目前为止，今日医疗部门龙门币总收入为：{0}\n").format(cure_income)

            elif department == _("文职部"):
                if len(cache.rhodes_island.recruited_id):
                    now_text += _("\n  当前已招募未确认干员人数为：{0}人，请前往博士办公室确认").format(len(cache.rhodes_island.recruited_id))
                else:
                    now_text += _("\n  当前没有已招募干员，请等待招募完成")
                for i in {0,1,2,3}:
                    if i in cache.rhodes_island.recruit_line:
                        now_text += _("\n  {0}号招募位进度：{1}%/100%").format(i+1, round(cache.rhodes_island.recruit_line[i][0],1))

            elif department == _("图书馆"):
                reader_count = cache.rhodes_island.reader_now
                now_text += _("\n  当前读者人数：{0} 人").format(reader_count)

            elif department == _("宿舍区"):
                npc_count = str(len(cache.npc_id_got))
                now_text += _("\n  干员总数/宿舍容量：{0}/{1}").format(npc_count, cache.rhodes_island.people_max)
                now_text += _("\n  具体居住情况：\n")
                live_npc_id_set = cache.npc_id_got.copy()
                Dormitory_all = constant.place_data["Dormitory"] + constant.place_data["Special_Dormitory"] # 合并普通和特殊宿舍
                # 遍历所有宿舍
                dormitory_count = 0 # 用来计数宿舍总数量
                pre_dormitory_name = "100" # 用来保存上一个宿舍名字
                for dormitory_place in Dormitory_all:
                    count = 0
                    tem_remove_id_set = set() # 用来保存需要删除id的临时set
                    dormitory_name = dormitory_place.split("\\")[-1]
                    dormitory_son_text = f"    [{dormitory_name}]："
                    # 遍历角色id
                    dormitory_npc_name = ""
                    for npc_id in live_npc_id_set:
                        live_dormitory = cache.character_data[npc_id].dormitory
                        # 如果该角色住在该宿舍，则在text中加入名字信息
                        if live_dormitory == dormitory_place:
                            dormitory_npc_name += f"{cache.character_data[npc_id].name}  "
                            # W的名字需要单独处理，减掉一个空格
                            if cache.character_data[npc_id].name == "W":
                                dormitory_npc_name = dormitory_npc_name[:-1]
                            count += 1
                            tem_remove_id_set.add(npc_id)
                        # 宿舍满2人则中断循环
                        if count >= 2:
                            break
                    dormitory_son_text += f"{str(dormitory_npc_name).ljust(15,'　')}" # 对齐为15个全角字符
                    # 在id集合中删掉本次已经出现过的id
                    for npc_id in tem_remove_id_set:
                        live_npc_id_set.discard(npc_id)
                    # 宿舍有人则显示该宿舍
                    if count:
                        # 换区或者单独宿舍则换行
                        if dormitory_name[0] != pre_dormitory_name[0]:
                            now_text += "\n"
                            dormitory_count = 0
                            if dormitory_name[0] not in {"梅","莱"}:
                                now_text += "\n"
                        # 每5个宿舍换行
                        elif dormitory_count % 5 == 0:
                            now_text += "\n"
                        pre_dormitory_name = dormitory_name # 更新上一个宿舍名字
                        now_text += dormitory_son_text
                        dormitory_count += 1
                now_text += "\n"

            elif department == _("机库"):
                now_text += _("\n  当前外勤委托情况：")
                # 输出委托信息
                for commision_id in cache.rhodes_island.ongoing_field_commissions:
                    commision_data = game_config.config_commission[commision_id]
                    commision_name = commision_data.name
                    # 参与干员名字
                    commision_chara_id_list = cache.rhodes_island.ongoing_field_commissions[commision_id][0]
                    commision_chara_name_list = [cache.character_data[chara_id].name for chara_id in commision_chara_id_list]
                    commision_chara_name_str = "、".join(commision_chara_name_list)
                    # 剩余返回天数
                    return_time = cache.rhodes_island.ongoing_field_commissions[commision_id][1]
                    last_days = game_time.count_day_for_datetime(cache.game_time, return_time)
                    if last_days <= 0:
                        last_days = _("不足一天")
                    else:
                        last_days = _("{0}天").format(last_days)
                    now_text += _("\n  [{0}]：{1}，剩余{2}").format(commision_name, commision_chara_name_str, last_days)
                if not len(cache.rhodes_island.ongoing_field_commissions):
                    now_text += _("\n  无")
                now_text += _("\n  当前载具情况：")
                # 输出载具信息
                for vehicle_id in cache.rhodes_island.vehicles:
                    # 如果未持有，则跳过
                    if cache.rhodes_island.vehicles[vehicle_id][0] == 0 and cache.rhodes_island.vehicles[vehicle_id][1] == 0:
                        continue
                    vehicle_data = game_config.config_vehicle[vehicle_id]
                    vehicle_name = vehicle_data.name
                    # 载具数量
                    now_vehicle_count = cache.rhodes_island.vehicles[vehicle_id][0]
                    out_vehicle_count = cache.rhodes_island.vehicles[vehicle_id][1]
                    now_text += _("\n  [{0}]：可用{1}辆，出动中{2}辆").format(vehicle_name, now_vehicle_count, out_vehicle_count)

            now_draw.text = now_text
            now_draw.width = self.width
            now_draw.draw()
            line_feed.draw()

            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                break

    def settle_show_resource_type(self, resouce_type):
        """设置显示的资源类型"""
        self.show_resource_type_dict[resouce_type] = not self.show_resource_type_dict[resouce_type]

    def see_attr(self, character_id: int):
        now_draw = see_character_info_panel.SeeCharacterInfoInScenePanel(
            character_id, self.width
        )
        now_draw.draw()


class Change_Npc_Work_Panel:
    """
    调整干员的工作岗位的面板对象
    Keyword arguments:
    text -- 选项名字
    width -- 最大宽度
    is_button -- 绘制按钮
    num_button -- 绘制数字按钮
    button_id -- 数字按钮id
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 最大宽度 """
        self.work_type_state: Dict[int, bool] = {wt_id: False for wt_id in game_config.config_work_type}
        """ 工作类型id和是否展开的状态 """
        self.work_type_state[0] = True
        """ 默认展开第一个工作类型 """

    def draw(self):
        """绘制对象"""

        title_text = _("调整干员工作岗位")
        title_draw = draw.TitleLineDraw(title_text, self.width)

        while 1:
            title_draw.draw()
            basement.update_work_people()
            return_list = []

            # 展开与收起所有类别按钮
            expand_all_text = _("[展开所有类别]")
            collapse_all_text = _("[收起所有类别]")
            expand_all_draw = draw.CenterButton(expand_all_text, expand_all_text, len(expand_all_text) * 2, cmd_func=self.expand_all)
            collapse_all_draw = draw.CenterButton(collapse_all_text, collapse_all_text, len(collapse_all_text) * 2, cmd_func=self.collapse_all)
            expand_all_draw.draw()
            collapse_all_draw.draw()
            return_list.append(expand_all_draw.return_text)
            return_list.append(collapse_all_draw.return_text)
            line_feed.draw()
            line_feed.draw()

            # 定义一个字典，用来表示各工作类型id下的干员id列表
            self.work_type_npc_dict = {}
            for work_type_id in game_config.config_work_type:
                self.work_type_npc_dict[work_type_id] = []

            # 遍历所有干员，将其加入对应的工作类型id列表中
            for npc_id in cache.npc_id_got:
                # 去掉玩家
                if npc_id == 0:
                    continue
                # 去掉访客
                if npc_id in cache.rhodes_island.visitor_info:
                    continue
                # 去掉2、7异常
                if not handle_premise.handle_normal_2(npc_id):
                    continue
                if not handle_premise.handle_normal_7(npc_id):
                    continue
                npc_data = cache.character_data[npc_id]
                work_type_id = npc_data.work.work_type
                if work_type_id in self.work_type_npc_dict:
                    self.work_type_npc_dict[work_type_id].append(npc_id)

            info_draw = draw.NormalDraw()
            info_draw.width = self.width

            # 遍历全部工作类型
            for work_type_id in game_config.config_work_type:
                work_type_data = game_config.config_work_type[work_type_id]
                work_type_name = work_type_data.name

                # 绘制工作类型按钮
                symbol = "▼" if self.work_type_state[work_type_id] else "▶"
                # 为了美观，在这里不显示工作类型的id
                # button_text = f"{symbol}[{str(work_type_id).rjust(3,'0')}]{work_type_name}({len(self.work_type_npc_dict[work_type_id])}人)"
                button_text = f"{symbol} {work_type_name}({len(self.work_type_npc_dict[work_type_id])}人)"
                draw_width = self.width / 7
                type_button_draw = draw.LeftButton(
                    button_text, work_type_name, draw_width,
                    cmd_func=self.toggle_work_type, args=(work_type_id,)
                )
                type_button_draw.draw()
                return_list.append(type_button_draw.return_text)

                # 如果展开，则绘制该工作类型下的干员列表
                if self.work_type_state[work_type_id]:
                    npc_list = self.work_type_npc_dict[work_type_id]
                    chara_count = 0
                    # 遍历干员列表，获取每个干员的信息
                    for npc_id in npc_list:
                        character_data = cache.character_data[npc_id]
                        name = character_data.name
                        adv_id = str(character_data.adv).rjust(4, '0')
                        button_text = f"[{adv_id}]{name}"
                        name_draw = draw.LeftButton(
                            button_text, name, draw_width, cmd_func=self.button_0, args=(npc_id,)
                        )
                        name_draw.draw()
                        return_list.append(name_draw.return_text)
                        chara_count += 1
                        if chara_count % 6 == 0:
                            line_feed.draw()
                            space_draw = draw.NormalDraw()
                            space_draw.text = " " * int(draw_width + 1)
                            space_draw.draw()
                    line_feed.draw()
                else:
                    line_feed.draw()

            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                break

    def toggle_work_type(self, work_type_id: int) -> None:
        """切换工作类型展开或收起状态
        参数:
            work_type_id: int, 工作类型id
        返回:
            None
        """
        self.work_type_state[work_type_id] = not self.work_type_state[work_type_id]

    def expand_all(self) -> None:
        """展开所有工作类型
        参数:
            无
        返回:
            None
        """
        for key in self.work_type_state:
            self.work_type_state[key] = True

    def collapse_all(self) -> None:
        """收起所有工作类型
        参数:
            无
        返回:
            None
        """
        for key in self.work_type_state:
            self.work_type_state[key] = False

    def button_0(self, character_id: int):
        """选项1"""

        while 1:

            line = draw.LineDraw("-", window_width)
            line.draw()
            line_feed.draw()
            info_draw = draw.NormalDraw()
            info_draw.width = window_width
            return_list = []

            target_data: game_type.Character = cache.character_data[character_id]
            info_text = _("{0}的当前工作为：").format(target_data.name)
            work_data = game_config.config_work_type[target_data.work.work_type]
            info_text += f"{work_data.name}({work_data.department})"
            info_text += _("\n可指派的工作有：\n")
            info_draw.text = info_text
            info_draw.draw()

            # 遍历工作列表，获取每个工作的信息
            for cid in game_config.config_work_type.keys():
                work_data = game_config.config_work_type[cid]
                work_cid = work_data.cid
                work_name = work_data.name
                work_tag = work_data.tag
                work_place = work_data.place
                work_describe = work_data.describe
                work_ability_id = work_data.ability_id
                work_ability_name = game_config.config_ability[work_ability_id].name[:2]
                chara_ability_lv = cache.character_data[character_id].ability[work_ability_id]

                # 判断是否开放，未开放则跳过
                flag_open = True
                # 必要条件判断
                if work_data.need != _("无"):
                    need_data_all = work_data.need
                    # 整理需要的条件
                    if "&" not in need_data_all:
                        need_data_list = [need_data_all]
                    else:
                        need_data_list = need_data_all.split('&')
                    judge, reason = attr_calculation.judge_require(need_data_list, character_id)
                    if not judge:
                        flag_open = False
                # 当前工作的地点名字判断
                # （应该已经被上面的必要条件判断所取代了，姑且还是保留一下）
                if flag_open:
                    if work_place in game_config.config_facility_open_name_set:
                        open_cid = game_config.config_facility_open_name_to_cid[work_place]
                        if not cache.rhodes_island.facility_open[open_cid]:
                            flag_open = False
                # 幼女不能进行学生以外的工作
                if handle_premise.handle_self_is_child(character_id) and work_cid != 152:
                    flag_open = False
                # 特殊解锁的工作不直接开放
                if work_tag == 2:
                    flag_open = False
                    # 监狱长，需要有囚犯在关押，且至少为三级陷落
                    if work_cid == 191 and handle_premise.handle_prisoner_in_custody(character_id) and (handle_premise.handle_self_fall_3(character_id) or handle_premise.handle_self_fall_4(character_id)):
                        flag_open = True
                    # 性爱练习生
                    if work_cid == 193 and handle_premise.handle_ask_one_exercises(character_id):
                        flag_open = True

                if flag_open:
                    work_text = ""
                    # 基础信息
                    work_text_before = f"[{str(work_cid).rjust(3,'0')}]{work_name}({work_place})"
                    work_text += work_text_before.ljust(18,'　')
                    # 在有能力要求的情况下，显示干员的能力
                    if work_ability_id != 0:
                        ability_text = f"({work_ability_name}:{chara_ability_lv})"
                        work_text += ability_text.ljust(6,'　')
                    else:
                        work_text += "　" * 4
                    # 工作描述
                    work_text += f"：{work_describe}"
                    # 正常工作直接显示
                    if work_tag in {0, 2}:
                        button_draw = draw.LeftButton(
                            work_text,
                            f"\n{work_cid}",
                            window_width ,
                            cmd_func=self.select_new_work,
                            args=(work_cid, character_id)
                        )
                        # 特殊工作则高亮显示
                        if work_tag == 2:
                            button_draw.normal_style = "gold_enrod"
                        button_draw.draw()
                        return_list.append(button_draw.return_text)
                    # 特殊工作显示为灰色，无法选择
                    elif work_tag == 1:
                        now_draw = draw.LeftDraw()
                        now_draw.text = work_text
                        now_draw.style = "deep_gray"
                        now_draw.width = window_width
                        now_draw.draw()
                    line_feed.draw()

            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn in return_list:
                break


    def select_new_work(self, work_id: int, character_id: int):
        """赋予新的工作id"""
        target_data: game_type.Character = cache.character_data[character_id]
        # 如果原工作是性爱练习生的话，则重置性爱练习
        if target_data.work.work_type == 193:
            for i in target_data.body_manage:
                if i in range(30,40) and target_data.body_manage[i]:
                    target_data.body_manage[i] = 0
        # 如果当前工作是监狱长
        if work_id == 191:
            from Script.Design import map_handle
            # 如果有旧的监狱长，则解除监狱长身份，并重置宿舍
            if handle_premise.handle_have_warden(0):
                old_warden = cache.character_data[cache.rhodes_island.current_warden_id]
                old_warden.work.work_type = 0
                old_warden.dormitory = old_warden.pre_dormitory
            # 更新监狱长id
            cache.rhodes_island.current_warden_id = character_id
            # 更新监狱长的宿舍
            target_data.pre_dormitory = target_data.dormitory
            target_data.dormitory = map_handle.get_map_system_path_str_for_list(["关押", "休息室"])
        # 赋予新工作
        target_data.work.work_type = work_id
        # 更新罗德岛的工作人员及状态
        basement.update_work_people()
        basement.update_facility_people()
