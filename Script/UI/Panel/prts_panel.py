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

class Prts_Panel:
    """
    用于显示教程界面面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        # self.now_panel = _("部门总概况")
        # """ 当前绘制的页面 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """

    def draw(self):
        """绘制对象"""

        title_text = "普瑞赛斯"

        title_draw = draw.TitleLineDraw(title_text, self.width)

        while 1:
            title_draw.draw()

            info_draw = draw.NormalDraw()
            info_draw.width = self.width
            return_list = []
            now_draw = panel.LeftDrawTextListPanel()

            pl_name = cache.character_data[0].name
            info_text = f"身份验证通过，最高权限账户——管理员账户\n\n"
            info_text += f"Dr.{pl_name}，欢迎访问普瑞赛斯终端，请问我可以为您做什么？\n\n"
            info_text += f"○请注意，本终端内的资料查询功能会直接涉及游戏流程和实际内容的介绍和剧透，如果更倾向于自己体验和摸索的话，请仅在必要时刻再使用本功能。\n\n"
            info_draw.text = info_text
            info_draw.draw()

            # 要输出的变量名称以及注释
            draw_text_list = []
            draw_text_list.append(f"[000]查询系统本身的相关资料")
            draw_text_list.append(f"[001]获得日常生活的建议")
            draw_text_list.append(f"[002]询问如何与干员相处")
            draw_text_list.append(f"[003]与干员发生肉体关系时的注意事项")
            draw_text_list.append(f"[004]怎么样才能更好的经营罗德岛")
            draw_text_list.append(f"[011]与普瑞赛斯闲聊（未实装）")

            # 循环输出以上各个问题
            for i in range(len(draw_text_list)):
                button_draw = draw.LeftButton(
                    draw_text_list[i],
                    f"\n{i}",
                    self.width ,
                    cmd_func=self.select_question,
                    args=i
                )
                now_draw.draw_list.append(button_draw)
                now_draw.width += len(button_draw.text)
                now_draw.draw_list.append(line_feed)
                return_list.append(button_draw.return_text)

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

            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def change_panel(self, prts_type: str):
        """
        切换当前面板显示
        Keyword arguments:
        prts_type -- 要切换的面板类型
        """

        self.now_panel = prts_type

    def select_question(self,key_index):
        """
        选择问题
        """

        while 1:
            self.fater_type = key_index
            line = draw.LineDraw("-", self.width)
            line.draw()
            return_list = []

            # 还没实装对话
            if self.fater_type == 5:
                break

            # 循环输出该父分类下的每个子类的问题
            for son_type in game_config.config_prts_data[self.fater_type]:
                Q_data = game_config.config_prts_data[self.fater_type][son_type][0]
                now_text = f"[{str(son_type).rjust(3,'0')}]{Q_data.text}"
                button_draw = draw.LeftButton(
                    _(now_text),
                    _(now_text),
                     self.width,
                    cmd_func=self.show_answer,
                    args=(son_type,),
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
                break

    def show_answer(self,key_index):
        """
        显示答案
        """

        while 1:
            line = draw.LineDraw("-", self.width)
            line.draw()

            A_data = game_config.config_prts_data[self.fater_type][key_index][1]
            answer_text_list = A_data.text.split('\\n')
            answer_text = ""
            for sub_text in answer_text_list:
                answer_text += f" {sub_text}\n"

            answer_draw = draw.WaitDraw()
            answer_draw.text = answer_text
            answer_draw.width = self.width
            answer_draw.draw()

            line_feed.draw()
            break

