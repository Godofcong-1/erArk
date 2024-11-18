from typing import Dict, List
from types import FunctionType
from Script.Core import cache_control, game_type, get_text, flow_handle, constant
from Script.Design import basement, attr_calculation, handle_premise
from Script.UI.Moudle import draw, panel
from Script.UI.Panel import manage_vehicle_panel, see_character_info_panel
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

    while 1:
        basement.update_work_people()
        # 遍历全部门
        department_names = []
        for work_type_id in game_config.config_facility:
            facility_data = game_config.config_facility[work_type_id]
            if facility_data.type == -1:
                department_names.append(game_config.config_facility[work_type_id].name)

        # 遍历创建全部门的面板
        department_panels = []
        for department_name in range(len(department_names)+1):
            if normal_config.config_normal.language == "zh_CN":
                department_panels.append(panel.PageHandlePanel([], ChangeWorkButtonList, 999, 8, width, 1, 0, 0))
            else:
                department_panels.append(panel.PageHandlePanel([], ChangeWorkButtonList, 999, 6, width, 1, 0, 0))

        line = draw.LineDraw("-", width)
        line.draw()

        info_draw = draw.NormalDraw()
        info_draw.width = width
        return_list = []

        # 空闲干员
        info_text = _("\n  空闲干员：\n")
        info_draw.text = info_text
        info_draw.draw()
        idle_npc_list = []
        # 去掉玩家
        cache.npc_id_got.discard(0)
        # 去掉访客
        id_list = [i for i in cache.npc_id_got if i not in cache.rhodes_island.visitor_info]
        for id in id_list:
            if id in cache.rhodes_island.all_work_npc_set[0]:
                idle_npc_list.append(id)
        department_panels[0].text_list = idle_npc_list
        department_panels[0].update()
        department_panels[0].draw()
        return_list.extend(department_panels[0].return_list)
        if not len(department_panels[0].text_list):
            line_feed.draw()

        # 遍历全部门
        department_count = 1
        n_flag = True
        for department in department_names:

            # 部门名
            info_text = f"\n" if n_flag else ""
            info_text += f"  {department}："
            info_draw.text = info_text
            info_draw.draw()
            # 部门干员传给面板
            for work_type_id in game_config.config_work_type:
                work_type_data = game_config.config_work_type[work_type_id]
                if work_type_data.department == department:
                    if len(cache.rhodes_island.all_work_npc_set[work_type_id]):
                        department_panels[department_count].text_list += list(cache.rhodes_island.all_work_npc_set[work_type_id])
            if len(department_panels[department_count].text_list):
                n_flag = False
                line_feed.draw()
            else:
                n_flag = True
            department_panels[department_count].update()
            department_panels[department_count].draw()
            return_list.extend(department_panels[department_count].return_list)
            department_count += 1

        line_feed.draw()
        back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
        back_draw.draw()
        line_feed.draw()
        return_list.append(back_draw.return_text)
        yrn = flow_handle.askfor_all(return_list)
        if yrn == back_draw.return_text:
            break


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
                all_info_draw.text += _("\n ↓点击[部门名]或[系统名]可查看对应详情，没有系统也没有工作位的部门是未实装的空白部门\n\n")
                all_info_draw.draw()

                # 遍历全部门
                for department in department_text_list:
                    department_text = f"[{department}]"

                    # 输出部门按钮
                    space_draw = draw.NormalDraw()
                    space_draw.text = "  "
                    space_draw.draw()
                    button_draw = draw.CenterButton(
                        department_text,
                        f"\n{department}",
                        len(department_text) * 2,
                        cmd_func=self.show_department,
                        args=(department,),
                    )
                    button_draw.draw()
                    return_list.append(button_draw.return_text)

                    # 如果该部门有子系统的话，绘制子系统按钮
                    if department in department_son_panel_button_dict:
                        for button_text in department_son_panel_button_dict[department]:
                            button_draw = draw.CenterButton(
                                button_text,
                                f"\n{button_text}",
                                len(button_text) * 2,
                                cmd_func=self.jump_to_son_panel,
                                args=(button_text)
                            )
                            button_draw.draw()
                            return_list.append(button_draw.return_text)

                    # 输出部门工作人员数量
                    all_info_draw.text = "："
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

        from Script.UI.Panel import building_panel, manage_assembly_line_panel, manage_library, resource_exchange_panel, recruit_panel, nation_diplomacy_panel, invite_visitor_panel, agriculture_production_panel, field_commission_panel, manage_vehicle_panel

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
                now_text += _("\n  当前待检修地点：")
                maintenance_flag = True
                for chara_id in cache.rhodes_island.maintenance_place:
                    if len(cache.rhodes_island.maintenance_place[chara_id]):
                        now_text += f"{cache.rhodes_island.maintenance_place[chara_id]}"
                        maintenance_flag = False
                if maintenance_flag:
                    now_text += _(" 暂无")

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

            now_draw.text = now_text
            now_draw.width = self.width
            now_draw.draw()
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


class ChangeWorkButtonList:
    """
    点击后可选择NPC的工作的按钮对象
    Keyword arguments:
    text -- 选项名字
    width -- 最大宽度
    is_button -- 绘制按钮
    num_button -- 绘制数字按钮
    button_id -- 数字按钮id
    """

    def __init__(
        self, NPC_id: int, width: int, is_button: bool, num_button: bool, button_id: int
    ):
        """初始化绘制对象"""

        self.NPC_id: int = NPC_id
        """ 指令名字绘制文本 """
        self.draw_text: str = ""
        """ 绘制文本 """
        self.width: int = width
        """ 最大宽度 """
        self.num_button: bool = num_button
        """ 绘制数字按钮 """
        self.button_id: int = button_id
        """ 数字按钮的id """
        self.button_return: str = str(button_id)
        """ 按钮返回值 """

        target_data: game_type.Character = cache.character_data[NPC_id]
        button_text = f"[{target_data.adv}]：{target_data.name}"
        self.button_return = str(NPC_id)

        # 按钮绘制

        name_draw = draw.LeftButton(
            button_text, self.button_return, self.width, cmd_func=self.button_0
        )
        self.now_draw = name_draw
        self.draw_text = button_text

        """ 绘制的对象 """
        self.now_draw = name_draw


    def button_0(self):
        """选项1"""

        while 1:

            line = draw.LineDraw("-", window_width)
            line.draw()
            line_feed.draw()
            info_draw = draw.NormalDraw()
            info_draw.width = window_width
            return_list = []

            target_data: game_type.Character = cache.character_data[self.NPC_id]
            info_text = _("{0}的当前工作为：").format(target_data.name)
            work_data = game_config.config_work_type[target_data.work.work_type]
            info_text += f"{work_data.name}({work_data.department})"
            info_text += _("\n可指派的工作有：\n")
            info_draw.text = info_text
            info_draw.draw()

            # 遍历工作列表，获取每个工作的信息
            for cid in game_config.config_work_type.keys():
                work_cid = game_config.config_work_type[cid].cid
                work_name = game_config.config_work_type[cid].name
                work_tag = game_config.config_work_type[cid].tag
                work_place = game_config.config_work_type[cid].place
                work_describe = game_config.config_work_type[cid].describe

                # 判断是否开放，未开放则跳过
                flag_open = True
                # 必要条件判断
                if game_config.config_work_type[cid].need != _("无"):
                    need_data_all = game_config.config_work_type[cid].need
                    # 整理需要的条件
                    if "&" not in need_data_all:
                        need_data_list = [need_data_all]
                    else:
                        need_data_list = need_data_all.split('&')
                    judge, reason = attr_calculation.judge_require(need_data_list, self.NPC_id)
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
                if handle_premise.handle_self_is_child(self.NPC_id) and work_cid != 152:
                    flag_open = False
                # 特殊解锁的工作不直接开放
                if work_tag == 2:
                    flag_open = False
                    # 性爱练习生
                    if work_cid == 193 and handle_premise.handle_ask_one_exercises(self.NPC_id):
                        flag_open = True

                if flag_open:
                    work_text_before = f"[{str(work_cid).rjust(3,'0')}]{work_name}({work_place})"
                    # 将work_text_before统一对齐为18个全角字符
                    work_text = f"{work_text_before.ljust(18,'　')}：{work_describe}"
                    # 正常工作直接显示
                    if work_tag in {0, 2}:
                        button_draw = draw.LeftButton(
                            work_text,
                            f"\n{work_cid}",
                            window_width ,
                            cmd_func=self.select_new_work,
                            args=work_cid
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

    def draw(self):
        """绘制对象"""
        self.now_draw.draw()

    def select_new_work(self,work_id: int):
        """赋予新的工作id"""
        target_data: game_type.Character = cache.character_data[self.NPC_id]
        target_data.work.work_type = work_id
        basement.update_work_people()
        basement.update_facility_people()
