from turtle import position
from typing import Dict, List
from types import FunctionType
from Script.Core import cache_control, game_type, get_text, flow_handle, text_handle, constant, py_cmd
from Script.Design import game_time
from Script.UI.Moudle import draw, panel
from Script.Config import game_config, normal_config
import os

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

class Diary_Panel:
    """
    用于显示日记界面面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """
        self.time_text = game_time.get_date_until_day()
        """ 日期文本 """
        self.all_insert_text: str = ""
        """ 插入的文本 """

    def draw(self):
        """绘制对象"""

        title_text = _("日记(实装中)")

        title_draw = draw.TitleLineDraw(title_text, self.width)

        while 1:
            title_draw.draw()

            info_draw = draw.NormalDraw()
            info_draw.width = self.width
            return_list = []

            info_text = ""
            info_text += _("{0}\n\n").format(self.time_text)
            for i in cache.daily_intsruce:
                info_text += i
            info_text += "\n\n"
            info_text += _("{0}\n\n").format(self.all_insert_text)
            info_draw.text = info_text
            info_draw.draw()

            draw_text = "[001]在最后增加文本"
            button_draw = draw.LeftButton(
                draw_text,
                draw_text,
                self.width ,
                cmd_func=self.insert_text,
            )
            button_draw.draw()
            line_feed.draw()
            return_list.append(button_draw.return_text)

            draw_text = "[002]清零增加文本"
            button_draw = draw.LeftButton(
                draw_text,
                draw_text,
                self.width ,
                cmd_func=self.clear_text,
            )
            button_draw.draw()
            line_feed.draw()
            return_list.append(button_draw.return_text)

            draw_text = "[003]保存并更新日记文件"
            save_button_draw = draw.LeftButton(
                draw_text,
                draw_text,
                self.width ,
                cmd_func=self.save_diary,
            )
            save_button_draw.draw()
            line_feed.draw()
            return_list.append(save_button_draw.return_text)

            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text or yrn == save_button_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def insert_text(self):
        """插入文本"""
        insert_text_panel = panel.AskForOneMessage()
        insert_text_panel.set(_(" 插入的文本为"), 100)
        text = insert_text_panel.draw()
        self.all_insert_text += text

    def clear_text(self):
        """清零增加文本"""
        self.all_insert_text = ""

    def save_diary(self):
        """保存并更新日记文件"""
        diary_files_path = os.path.join("save", "diary")
        if not os.path.exists(diary_files_path):
            os.makedirs(diary_files_path)
        pl_name = cache.character_data[0].name
        time = f"_{cache.game_time.year}_{cache.game_time.month}_{cache.game_time.day}"
        diray_file_name = pl_name + time + ".txt"
        diray_file_path = os.path.join(diary_files_path, diray_file_name)
        # 开始写入
        with open(diray_file_path, "w", encoding="utf-8") as f:
            f.write(self.time_text)
            f.write("\n\n")
            for i in cache.daily_intsruce:
                f.write(i)
            f.write("\n\n")
            f.write(self.all_insert_text)
        # 清空缓存
        cache.daily_intsruce = []
        self.all_insert_text = ""
        # 输出提示信息
        now_draw = draw.WaitDraw()
        now_draw.text = _("\n日记已保存至{0}\n").format(diray_file_path)
        now_draw.draw()
