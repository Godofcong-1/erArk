from turtle import position
from typing import Tuple, List
from types import FunctionType
from uuid import UUID
from Script.Core import cache_control, game_type, get_text, flow_handle, text_handle, constant, py_cmd
from Script.Design import map_handle,attr_text,attr_calculation
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
        department_type_list = [_("部门总概况"),_("医疗部")]

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

                cache.base_resouce.work_people_now = 0
                for Clinic_place in constant.place_data["Clinic"]:
                    if len(cache.scene_data[Clinic_place].character_list):
                        for npc_id in cache.scene_data[Clinic_place].character_list:
                            if npc_id:
                                cache.base_resouce.work_people_now += 1

                work_people_now,people_max = str(cache.base_resouce.work_people_now),str(len(cache.npc_tem_data))

                all_info_text += f"\n  当前工作中干员/总干员：{work_people_now}/{people_max}"
                all_income = str(cache.base_resouce.all_income)
                all_info_text += f"\n  截至目前为止，今日各部门龙门币总收入为：{all_income}\n"

                all_info_draw.text = all_info_text
                all_info_draw.width = self.width
                now_draw.draw_list.append(all_info_draw)
                now_draw.width += len(all_info_draw.text)


            elif self.now_panel == "医疗部":

                medical_info_draw = draw.NormalDraw()
                medical_info_text = "\n当前医疗部门情况："
                patient_cured,patient_now = str(cache.base_resouce.patient_cured),str(cache.base_resouce.patient_now)
                medical_info_text += f"\n  今日已治疗患者数/排队中患者数：{patient_cured}/{patient_now}"
                medical_info_text += f"\n  当前正在坐诊的医生有："
                doctor_name_str = ""
                for Clinic_place in constant.place_data["Clinic"]:
                    if len(cache.scene_data[Clinic_place].character_list):
                        for npc_id in cache.scene_data[Clinic_place].character_list:
                            npc_name = cache.character_data[npc_id].name
                            doctor_name_str += f" {npc_name}"
                if len(doctor_name_str):
                    medical_info_text += doctor_name_str
                else:
                    medical_info_text += " 暂无坐诊中的医生"
                cure_income = str(cache.base_resouce.cure_income)
                medical_info_text += f"\n  截至目前为止，今日医疗部门龙门币总收入为：{cure_income}\n"

                medical_info_draw.text = medical_info_text
                medical_info_draw.width = self.width
                now_draw.draw_list.append(medical_info_draw)
                now_draw.width += len(medical_info_draw.text)

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
