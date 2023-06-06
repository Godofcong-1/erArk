from turtle import position
from typing import Dict, List
from types import FunctionType
from uuid import UUID
from Script.Core import cache_control, game_type, get_text, flow_handle, text_handle, constant, py_cmd
from Script.Design import basement
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
        self.now_panel = _("部门总概况")
        """ 当前绘制的页面 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """

    def draw(self):
        """绘制对象"""

        title_text = "管理罗德岛"
        panel_list = [_("部门总概况")]

        title_draw = draw.TitleLineDraw(title_text, self.width)

        # 进行一轮刷新
        basement.update_work_people()
        basement.update_facility_people()

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


            # 部门总概况
            if self.now_panel == "部门总概况":

                all_info_draw = draw.NormalDraw()

                self.department_text_list = ["工程部", "生活娱乐区", "医疗部", "文职部", "训练场", "图书馆", "教育区", "宿舍"]

                # 统计各部门岗位的工作干员数量
                patient_now = cache.base_resouce.patient_now
                work_people_now,people_max = cache.base_resouce.work_people_now,len(cache.npc_id_got)

                all_info_draw.text = f"\n 当前工作中干员/总干员：{work_people_now}/{people_max}\n\n"
                all_info_draw.draw()

                # 遍历全部门
                for department in self.department_text_list:
                    department_text = f"[{department}]"

                    # 输出部门按钮
                    space_draw = draw.NormalDraw()
                    space_draw.text = "  "
                    space_draw.draw()
                    button_draw = draw.CenterButton(
                        department_text,
                        department,
                        len(department_text)*2,
                        cmd_func=self.show_department,
                        args=(department,),
                    )
                    button_draw.draw()
                    return_list.append(button_draw.return_text)

                    # 输出部门工作人员数量
                    all_info_draw.text = "："
                    for all_cid in game_config.config_work_type:
                        work_data = game_config.config_work_type[all_cid]
                        if work_data.department == department:
                            all_info_draw.text += f"  {work_data.name} — {len(cache.base_resouce.all_work_npc_set[all_cid])}"
                    if department == "医疗部":
                        all_info_draw.text += f"  病人 — {patient_now}"
                    all_info_draw.draw()
                    line_feed.draw()

                # 收入
                all_income = str(cache.base_resouce.all_income)
                all_info_draw.text = f"\n  截至目前为止，今日各部门龙门币总收入为：{all_income}\n\n"
                all_info_draw.width = self.width
                all_info_draw.draw()

                button_draw = draw.LeftButton(
                    f"[001]调整干员岗位",
                    f"\n1",
                    self.width ,
                    cmd_func=self.change_npc_work,
                )
                button_draw.draw()
                return_list.append(button_draw.return_text)


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

            now_text = f"\n当前{department}部门情况："
            for all_cid in game_config.config_work_type:
                work_data = game_config.config_work_type[all_cid]
                if work_data.department == department:
                    now_text+= f"\n  当前正在工作的{work_data.name}："
                    if len(cache.base_resouce.all_work_npc_set[all_cid]):
                        for npc_id in cache.base_resouce.all_work_npc_set[all_cid]:
                            npc_name = cache.character_data[npc_id].name
                            now_text += f" {npc_name}"
                    else:
                        now_text += " 暂无"

            if department == "医疗部":
                patient_cured,patient_now = str(cache.base_resouce.patient_cured),str(cache.base_resouce.patient_now)
                now_text += f"\n  今日已治疗患者数/排队中患者数：{patient_cured}/{patient_now}"
                cure_income = str(cache.base_resouce.cure_income)
                now_text += f"\n  截至目前为止，今日医疗部门龙门币总收入为：{cure_income}\n"

            elif department == "文职部":
                if len(cache.base_resouce.recruited_id):
                    now_text += f"\n  当前已招募未确认干员人数为：{len(cache.base_resouce.recruited_id)}人，请前往博士办公室确认"
                else:
                    now_text += f"\n  当前没有已招募干员，请等待招募完成"
                for i in {0,1,2}:
                    if i in cache.base_resouce.recruit_now:
                        now_text += f"\n  {i+1}号招募位进度：{round(cache.base_resouce.recruit_now[0],1)}%/100%"

            elif department == "图书馆":
                reader_count = cache.base_resouce.reader_now
                now_text += f"\n  当前读者人数：{reader_count} 人"

            elif department == "宿舍":
                npc_count = str(len(cache.npc_id_got))
                now_text += f"\n  干员总数/宿舍容量：{npc_count}/{cache.base_resouce.people_max}"
                now_text += f"\n  具体居住情况："
                live_npc_id_set = cache.npc_id_got.copy()
                Dormitory_all = constant.place_data["Dormitory"] + constant.place_data["Special_Dormitory"] # 合并普通和特殊宿舍
                # 遍历所有宿舍
                for dormitory_place in Dormitory_all:
                    count = 0
                    tem_remove_id_set = set() # 用来保存需要删除id的临时set
                    dormitory_name = dormitory_place.split("\\")[-1]
                    dormitory_son_text = f"\n    {dormitory_name}："
                    # 遍历角色id
                    for npc_id in live_npc_id_set:
                        live_dormitory = cache.character_data[npc_id].dormitory
                        # 如果该角色住在该宿舍，则在text中加入名字信息
                        if live_dormitory == dormitory_place:
                            dormitory_son_text += f"{cache.character_data[npc_id].name}  "
                            count += 1
                            tem_remove_id_set.add(npc_id)
                        # 宿舍满2人则中断循环
                        if count >= 2:
                            break
                    # 在id集合中删掉本次已经出现过的id
                    for npc_id in tem_remove_id_set:
                        live_npc_id_set.discard(npc_id)
                    # 宿舍有人则显示该宿舍
                    if count:
                        now_text += dormitory_son_text
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

    def change_npc_work(self):
        """
        调整干员的工作岗位
        """

        while 1:
            # 遍历创建全部门的面板
            handle_panel_list = []
            for department_id in range(len(self.department_text_list)+1):
                handle_panel_list.append(panel.PageHandlePanel([], ChangeWorkButtonList, 999, 9, self.width, 1, 0, 0))

            line = draw.LineDraw("-", self.width)
            line.draw()

            info_draw = draw.NormalDraw()
            info_draw.width = self.width
            return_list = []

            # 空闲干员
            info_text = f"\n  空闲干员："
            info_draw.text = info_text
            info_draw.draw()
            leisure_list = []
            cache.npc_id_got.discard(0)
            for id in cache.npc_id_got:
                if id in cache.base_resouce.all_work_npc_set[0]:
                    leisure_list.append(id)
            handle_panel_list[0].text_list = leisure_list
            handle_panel_list[0].update()
            handle_panel_list[0].draw()
            return_list.extend(handle_panel_list[0].return_list)
            if not len(handle_panel_list[0].text_list):
                line_feed.draw()

            # 遍历全部门
            department_count = 1
            n_flag = True
            for department in self.department_text_list:

                info_text = f"\n" if n_flag else ""
                info_text += f"  {department}："
                info_draw.text = info_text
                info_draw.draw()
                for all_cid in game_config.config_work_type:
                    work_data = game_config.config_work_type[all_cid]
                    if work_data.department == department:
                        if len(cache.base_resouce.all_work_npc_set[all_cid]):
                            handle_panel_list[department_count].text_list += list(cache.base_resouce.all_work_npc_set[all_cid])
                n_flag = False if len(handle_panel_list[department_count].text_list) else True
                handle_panel_list[department_count].update()
                handle_panel_list[department_count].draw()
                return_list.extend(handle_panel_list[department_count].return_list)
                department_count += 1

            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                break


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
        button_text = f"[{target_data.adv}：{target_data.name}]"
        self.button_return = str(NPC_id)

        # 按钮绘制

        name_draw = draw.CenterButton(
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
            info_text = f"{target_data.name}的当前工作为："
            work_data = game_config.config_work_type[target_data.work.work_type]
            info_text += f"{work_data.name}({work_data.department})"
            info_text += "\n可指派的新工作有：\n"
            info_draw.text = info_text
            info_draw.draw()

            # 遍历工作列表，获取每个工作的信息
            for cid in game_config.config_work_type.keys():
                work_cid = game_config.config_work_type[cid].cid
                work_name = game_config.config_work_type[cid].name
                work_place = game_config.config_work_type[cid].place
                work_describe = game_config.config_work_type[cid].describe

                # 判断当前工作的地点是否开放，未开放则跳过
                flag_open = True
                for open_cid in game_config.config_facility_open:
                    if game_config.config_facility_open[open_cid].name == work_place:
                        if not cache.base_resouce.facility_open[open_cid]:
                            flag_open = False
                        break

                if flag_open:
                    button_draw = draw.LeftButton(
                        f"[{str(work_cid).rjust(3,'0')}]{work_name}({work_place})：{work_describe}",
                        f"\n{work_cid}",
                        window_width ,
                        cmd_func=self.select_new_work,
                        args=work_cid
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

    def draw(self):
        """绘制对象"""
        self.now_draw.draw()

    def select_new_work(self,work_id: int):
        """赋予新的工作id"""
        target_data: game_type.Character = cache.character_data[self.NPC_id]
        target_data.work.work_type = work_id
        basement.update_work_people()
        basement.update_facility_people()
