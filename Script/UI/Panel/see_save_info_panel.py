import datetime
from typing import List
from types import FunctionType
from Script.Core import (
    cache_control,
    get_text,
    save_handle,
    text_handle,
    constant,
    flow_handle,
    game_type,
    py_cmd,
)
from Script.Config import normal_config
from Script.UI.Moudle import panel, draw

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """
window_width = normal_config.config_normal.text_width
""" 屏幕宽度 """
line_feed = draw.NormalDraw()
""" 换行绘制对象 """
line_feed.text = "\n"
line_feed.width = 1


class SeeSaveListPanel:
    """
    查看存档列表面板
    width -- 绘制宽度
    write_save -- 是否存储存档
    """

    def __init__(self, width: int, write_save: bool = True):
        """初始化绘制对象"""
        self.width: int = width
        """ 最大绘制宽度 """
        self.return_list: List[str] = []
        """ 当前面板监听的按钮列表 """
        self.back_to_main: bool = write_save
        """ 是否返回主菜单 """
        now_list = [(i, write_save) for i in range(normal_config.config_normal.max_save)]
        self.handle_panel = panel.PageHandlePanel(
            now_list, SaveInfoDraw, normal_config.config_normal.save_page, 1, width, True, True, 0, "-"
        )
        """ 页面控制对象 """
        # 如果配置文件里有上次的页码，则将分页面板跳到该页
        try:
            last_page = save_handle.get_last_save_page()
            self.handle_panel.now_page = last_page
        except Exception:
            pass

    def draw(self):
        """绘制对象"""
        while 1:
            if cache.back_save_panel:
                cache.back_save_panel = False
                break
            line_feed.draw()
            title_draw = draw.TitleLineDraw(_("神经连接柜"), self.width)
            title_draw.draw()
            self.return_list = []
            auto_save_draw = SaveInfoDraw(["auto", 0], self.width, True, False, 0)
            auto_save_draw.draw()
            line_feed.draw()
            self.return_list.append("auto")
            now_line = draw.LineDraw(".", self.width)
            now_line.draw()
            self.handle_panel.update()
            self.handle_panel.draw()
            self.return_list.extend(self.handle_panel.return_list)
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), self.width)
            back_draw.draw()
            line_feed.draw()
            self.return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(self.return_list)
            py_cmd.clr_cmd()
            if yrn == back_draw.return_text:
                break
        if self.back_to_main:
            cache.now_panel_id = constant.Panel.IN_SCENE


class SaveInfoDraw:
    """
    绘制存档信息按钮
    Keyword arguments:
    text -- 存档id
    width -- 最大宽度
    is_button -- 绘制按钮
    num_button -- 绘制数字按钮
    button_id -- 数字按钮的id
    """

    def __init__(self, text: List, width: int, is_button: bool, num_button: bool, button_id: int):
        """初始化绘制对象"""
        self.text: str = str(text[0])
        """ 存档id """
        self.write_save: bool = text[1]
        """ 是否存储存档 """
        self.draw_text: str = ""
        """ 存档信息绘制文本 """
        self.width: int = width
        """ 最大宽度 """
        self.is_button: bool = is_button
        """ 绘制按钮 """
        self.is_num_button: bool = num_button
        """ 绘制数字按钮 """
        self.button_id: int = button_id
        """ 数字按钮的id """
        self.button_return: str = str(button_id)
        """ 按钮返回值 """
        self.save_exist_judge = save_handle.judge_save_file_exist(self.text)
        """ 存档位是否已存在 """
        save_name = _("空槽位")
        if self.save_exist_judge:
            save_head = save_handle.load_save_info_head(self.text)
            game_time: datetime.datetime = save_head["game_time"]
            save_time: datetime.datetime = save_head["save_time"]

            # 更改月份的输出
            if game_time.month == 3:
                month_text = _("春")
            elif game_time.month == 6:
                month_text = _("夏")
            elif game_time.month == 9:
                month_text = _("秋")
            elif game_time.month == 12:
                month_text = _("冬")
            game_time_text = (_("{year}年{month}月{day}日{hour}点{minute}分")).format(
                year=game_time.year,
                month=month_text,
                day=game_time.day,
                hour=game_time.hour,
                minute=game_time.minute,
            )

            game_time_text = _("游戏时间:") + game_time_text
            save_time_text = _("存档时间:") + save_time.strftime("%Y-%m-%d %H:%M")
            save_name = f"No.{self.text} {save_head['game_verson']} {game_time_text}"
            save_name += _(" {0}博士").format(save_head['character_name'])
            save_name += f" {save_time_text}"
            # 标记最新存档
            try:
                last_id = save_handle.get_last_save_id()
                # 如果是最新存档，则在名字后面加上标记
                if last_id != "" and str(last_id) == str(self.text):
                    save_name += _(" (新!)")
            except Exception:
                pass
        if is_button:
            if num_button:
                index_text = text_handle.id_index(button_id)
                now_text_width = self.width - len(index_text)
                new_text = text_handle.align(save_name, "center", text_width=now_text_width)
                self.draw_text = f"{index_text}{new_text}"
                self.button_return = str(button_id)
            else:
                new_text = text_handle.align(save_name, "center", text_width=self.width)
                self.draw_text = new_text
                self.button_return = text[0]
        else:
            new_text = text_handle.align(save_name, "center", text_width=self.width)
            self.draw_text = new_text

    def draw(self):
        """绘制对象"""
        if self.is_button and (self.save_exist_judge or self.write_save):
            now_draw = draw.Button(self.draw_text, self.button_return, cmd_func=self.draw_save_handle)
        else:
            now_draw = draw.NormalDraw()
            now_draw.text = self.draw_text
        now_draw.width = self.width
        now_draw.draw()

    def draw_save_handle(self):
        """处理读写存档"""
        # py_cmd.clr_cmd()
        line_feed.draw()
        if self.save_exist_judge:
            now_ask_list = []
            now_id = 0
            load_save_button = draw.Button(
                text_handle.id_index(now_id) + _("读取"), str(now_id), cmd_func=self.load_save
            )
            load_save_button.width = self.width
            load_save_button.draw()
            line_feed.draw()
            now_ask_list.append(str(now_id))
            now_id += 1
            if self.write_save:
                re_write_save_button = draw.Button(
                    text_handle.id_index(now_id) + _("覆盖"),
                    str(now_id),
                    cmd_func=self.re_write_save,
                )
                re_write_save_button.width = self.width
                re_write_save_button.draw()
                now_ask_list.append(str(now_id))
                line_feed.draw()
                now_id += 1
            delete_save_button = draw.Button(
                text_handle.id_index(now_id) + _("删除"), str(now_id), cmd_func=self.delete_save
            )
            delete_save_button.width = self.width
            delete_save_button.draw()
            now_ask_list.append(str(now_id))
            now_id += 1
            line_feed.draw()
            back_button = draw.Button(text_handle.id_index(now_id) + _("返回"), str(now_id))
            back_button.width = self.width
            back_button.draw()
            line_feed.draw()
            now_ask_list.append(str(now_id))
            flow_handle.askfor_all(now_ask_list)
            py_cmd.clr_cmd()
        else:
            # 创建新存档，同时记录该存档所在的页码到缓存
            save_handle.establish_save(self.text)
            try:
                # 仅处理数字存档位
                save_id = int(self.text)
                page = int(save_id / normal_config.config_normal.save_page)
                save_handle.set_last_save_page(page)
                # 记录最后保存的存档id
                save_handle.set_last_save_id(self.text)
            except Exception:
                pass

    def load_save(self):
        """载入存档"""
        # 进行二次确认
        while 1:
            line_feed.draw()
            sure_draw = draw.LeftButton(_("[000]确认读取存档"), _("0"), self.width)
            sure_draw.draw()
            line_feed.draw()
            back_draw = draw.LeftButton(_("[001]取消"), _("1"), self.width)
            back_draw.draw()
            line_feed.draw()
            yrn = flow_handle.askfor_all([sure_draw.return_text, back_draw.return_text])
            py_cmd.clr_cmd()
            if yrn == sure_draw.return_text:
                break
            elif yrn == back_draw.return_text:
                return
        save_handle.input_load_save(str(self.text))
        cache.now_panel_id = constant.Panel.IN_SCENE
        cache.back_save_panel = True

    def delete_save(self):
        """删除存档"""
        # 进行二次确认
        while 1:
            line_feed.draw()
            sure_draw = draw.LeftButton(_("[000]确认删除存档"), _("0"), self.width)
            sure_draw.draw()
            line_feed.draw()
            back_draw = draw.LeftButton(_("[001]取消"), _("1"), self.width)
            back_draw.draw()
            line_feed.draw()
            yrn = flow_handle.askfor_all([sure_draw.return_text, back_draw.return_text])
            py_cmd.clr_cmd()
            if yrn == sure_draw.return_text:
                break
            elif yrn == back_draw.return_text:
                return
        save_handle.remove_save(self.text)

    def re_write_save(self):
        """覆盖存档"""
        # 进行二次确认
        while 1:
            line_feed.draw()
            sure_draw = draw.LeftButton(_("[000]确认覆盖存档"), _("0"), self.width)
            sure_draw.draw()
            line_feed.draw()
            back_draw = draw.LeftButton(_("[001]取消"), _("1"), self.width)
            back_draw.draw()
            line_feed.draw()
            yrn = flow_handle.askfor_all([sure_draw.return_text, back_draw.return_text])
            py_cmd.clr_cmd()
            if yrn == sure_draw.return_text:
                break
            elif yrn == back_draw.return_text:
                return
        save_handle.establish_save(self.text)
        # 尝试记录该存档所在的页码到缓存
        try:
            save_id = int(self.text)
            page = int(save_id / normal_config.config_normal.save_page)
            save_handle.set_last_save_page(page)
            # 记录最后保存的存档id
            save_handle.set_last_save_id(self.text)
        except Exception:
            pass
