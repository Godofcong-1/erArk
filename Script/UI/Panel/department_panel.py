from turtle import position
from typing import Tuple, List
from types import FunctionType
from uuid import UUID
from Script.Core import cache_control, game_type, get_text, flow_handle, text_handle, constant, py_cmd
from Script.Design import character
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

class Department_Panel:
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

        title_text = "部门运作情况"
        department_type_list = [_("部门总概况"),_("医疗部"),_("文职部"),_("宿舍")]

        title_draw = draw.TitleLineDraw(title_text, self.width)
        while 1:
            return_list = []
            title_draw.draw()

            # 绘制主面板
            for department_type in department_type_list:
                if department_type == self.now_panel:
                    now_draw = draw.CenterDraw()
                    now_draw.text = f"[{department_type}]"
                    now_draw.style = "onbutton"
                    now_draw.width = self.width / len(department_type_list)
                    now_draw.draw()
                else:
                    now_draw = draw.CenterButton(
                        f"[{department_type}]",
                        f"\n{department_type}",
                        self.width / len(department_type_list),
                        cmd_func=self.change_panel,
                        args=(department_type,),
                    )
                    now_draw.draw()
                    return_list.append(now_draw.return_text)
            line_feed.draw()
            line = draw.LineDraw("+", self.width)
            line.draw()

            # facility_draw = draw.NormalDraw()
            # facility_text = "\n当前设施情况："
            # facility_draw.text = facility_text
            # facility_draw.width = self.width
            # facility_draw.draw()

            now_draw = panel.LeftDrawTextListPanel()

            # 部门总概况
            if self.now_panel == "部门总概况":

                all_info_draw = draw.NormalDraw()
                all_info_text = "\n当前全部门总情况："

                # 统计各部门岗位的工作干员数量
                doctor_now,HR_now = cache.base_resouce.doctor_now,cache.base_resouce.HR_now
                doctor_all,HR_all = len(cache.base_resouce.doctor_id_set), len(cache.base_resouce.HR_id_set)
                work_people_now,people_max = cache.base_resouce.work_people_now,len(cache.npc_id_got)

                all_info_text += f"\n  当前工作中干员/总干员：{work_people_now}/{people_max}"
                all_info_text += f"\n  医疗部：{doctor_now}/{doctor_all}\n"
                all_info_text += f"\n  文职部：{HR_now}/{HR_all}\n"

                # 收入
                all_income = str(cache.base_resouce.all_income)
                all_info_text += f"\n  截至目前为止，今日各部门龙门币总收入为：{all_income}\n"

                all_info_draw.text = all_info_text
                all_info_draw.width = self.width
                now_draw.draw_list.append(all_info_draw)
                now_draw.width += len(all_info_draw.text)

                now_draw.draw_list.append(line_feed)
                now_draw.width += line_feed.width

                button_draw = draw.LeftButton(
                    f"[001]调整干员岗位",
                    f"\n1",
                    self.width ,
                    cmd_func=self.change_npc_work,
                )
                now_draw.draw_list.append(button_draw)
                now_draw.width += len(button_draw.text)
                return_list.append(button_draw.return_text)

            elif self.now_panel == "医疗部":

                medical_info_draw = draw.NormalDraw()
                medical_info_text = "\n当前医疗部门情况："
                patient_cured,patient_now = str(cache.base_resouce.patient_cured),str(cache.base_resouce.patient_now)
                medical_info_text += f"\n  今日已治疗患者数/排队中患者数：{patient_cured}/{patient_now}"
                medical_info_text += f"\n  当前正在坐诊的医生有："
                doctor_name_str = ""
                for npc_id in cache.base_resouce.doctor_id_set:
                    npc_name = cache.character_data[npc_id].name
                    doctor_name_str += f" {npc_name}"
                if len(doctor_name_str):
                    medical_info_text += doctor_name_str
                else:
                    medical_info_text += " 暂无"
                cure_income = str(cache.base_resouce.cure_income)
                medical_info_text += f"\n  截至目前为止，今日医疗部门龙门币总收入为：{cure_income}\n"

                medical_info_draw.text = medical_info_text
                medical_info_draw.width = self.width
                now_draw.draw_list.append(medical_info_draw)
                now_draw.width += len(medical_info_draw.text)

            elif self.now_panel == "文职部":

                civil_info_draw = draw.NormalDraw()
                civil_info_text = "\n当前文职部门情况："
                if len(cache.base_resouce.recruited_id):
                    civil_info_text += f"\n  当前已招募未确认干员人数为：{len(cache.base_resouce.recruited_id)}人，请前往博士办公室确认"
                else:
                    civil_info_text += f"\n  当前没有已招募干员，请等待招募完成"
                for i in {0,1,2}:
                    if i in cache.base_resouce.recruit_now:
                        civil_info_text += f"\n  {i+1}号招募位进度：{round(cache.base_resouce.recruit_now[0],1)}%/100%"
                civil_info_text += f"\n  当前正在进行招募工作的人事有："
                HR_name_str = ""
                for npc_id in cache.base_resouce.HR_id_set:
                    npc_name = cache.character_data[npc_id].name
                    HR_name_str += f" {npc_name}"
                if len(HR_name_str):
                    civil_info_text += HR_name_str
                else:
                    civil_info_text += " 暂无"
                civil_info_text += "\n"

                civil_info_draw.text = civil_info_text
                civil_info_draw.width = self.width
                now_draw.draw_list.append(civil_info_draw)
                now_draw.width += len(civil_info_draw.text)

            elif self.now_panel == "宿舍":

                dormitory_info_draw = draw.NormalDraw()
                dormitory_info_text = "\n当前宿舍情况："
                npc_count = str(len(cache.npc_id_got))
                dormitory_info_text += f"\n  干员总数/宿舍容量：{npc_count}/{cache.base_resouce.people_max}"
                dormitory_info_text += f"\n  具体居住情况："
                doctor_name_str = ""
                for dormitory_place in constant.place_data["Dormitory"]:
                    count = 0
                    dormitory_name = dormitory_place.split("\\")[-1]
                    dormitory_son_text = f"\n    {dormitory_name}："
                    for npc_id in cache.npc_id_got:
                        live_dormitory = cache.character_data[npc_id].dormitory
                        if live_dormitory == dormitory_place:
                            dormitory_son_text += f"{cache.character_data[npc_id].name}  "
                            count += 1
                        if count >= 2:
                            dormitory_info_text += dormitory_son_text
                            break
                dormitory_info_text += "\n"

                dormitory_info_draw.text = dormitory_info_text
                dormitory_info_draw.width = self.width
                now_draw.draw_list.append(dormitory_info_draw)
                now_draw.width += len(dormitory_info_draw.text)

            self.draw_list: List[draw.NormalDraw] = []
            """ 绘制的文本列表 """
            self.draw_list.extend(now_draw.draw_list)

            for label in self.draw_list:
                if isinstance(label, list):
                    for value in label:
                        value.draw()
                    line_feed.draw()
                else:
                    label.draw()

            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def change_panel(self, department_type: str):
        """
        切换当前面板显示
        Keyword arguments:
        department_type -- 要切换的面板类型
        """

        self.now_panel = department_type

    def change_npc_work(self):
        """
        调整干员的工作岗位
        """

        handle_leisure_panel = panel.PageHandlePanel([], ChangeWorkButtonList, 999, 10, self.width, 1, 1, 0)
        handle_doctor_panel = panel.PageHandlePanel([], ChangeWorkButtonList, 999, 10, self.width, 1, 1, 0)
        handle_HR_panel = panel.PageHandlePanel([], ChangeWorkButtonList, 999, 10, self.width, 1, 1, 0)

        while 1:
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
                if (
                    id not in cache.base_resouce.doctor_id_set
                    and id not in cache.base_resouce.HR_id_set
                ):
                    leisure_list.append(id)
            handle_leisure_panel.text_list = leisure_list
            handle_leisure_panel.update()
            handle_leisure_panel.draw()
            return_list.extend(handle_leisure_panel.return_list)

            # 医疗部
            info_text = f"\n  医疗部："
            info_draw.text = info_text
            info_draw.draw()
            handle_doctor_panel.text_list = list(cache.base_resouce.doctor_id_set)
            handle_doctor_panel.update()
            handle_doctor_panel.draw()
            return_list.extend(handle_doctor_panel.return_list)

            # 文职部
            info_text = f"\n  文职部："
            info_draw.text = info_text
            info_draw.draw()
            handle_HR_panel.text_list = list(cache.base_resouce.HR_id_set)
            handle_HR_panel.update()
            handle_HR_panel.draw()
            return_list.extend(handle_HR_panel.return_list)

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
            if target_data.work.work_type == 61:
                info_text += "坐诊(医疗部)"
            elif target_data.work.work_type == 71:
                info_text += "招募(文职部)"
            else:
                info_text += "无"
            info_text += "\n 可指派的新工作有：\n"
            info_draw.text = info_text
            info_draw.draw()

            # 遍历工作列表，获取每个工作的信息
            for cid in game_config.config_work_type.keys():
                if cid:
                    work_cid = game_config.config_work_type[cid].cid
                    work_name = game_config.config_work_type[cid].name
                    work_place = game_config.config_work_type[cid].department
                    work_describe = game_config.config_work_type[cid].describe

                    button_draw = draw.LeftButton(
                        f"[{work_cid}]{work_name}({work_place})：{work_describe}",
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
        character.update_work_people()
