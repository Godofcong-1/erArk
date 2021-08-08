from typing import Tuple, Dict
from types import FunctionType
from uuid import UUID
from Script.Core import cache_control, game_type, get_text, flow_handle, text_handle, constant, py_cmd
from Script.Design import map_handle, cooking, update
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


class Find_call_Panel:
    """
    总面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.now_panel = _("干员位置一览")
        """ 当前绘制的食物类型 """
        self.handle_panel: panel.PageHandlePanel = None
        """ 当前名字列表控制面板 """

    def draw(self):
        """绘制对象"""
        title_draw = draw.TitleLineDraw("干员位置一览", self.width)
        self.handle_panel = panel.PageHandlePanel([], FindDraw, 10, 5, self.width, 1, 1, 0)
        while 1:
            py_cmd.clr_cmd()
            npc_list = {}
            #读取人物的位置情报与跟随情报#
            for npc_id in cache.character_data:
                if npc_id != 0:
                    character_data = cache.character_data[npc_id]
                    name = character_data.name
                    scene_position = character_data.position
                    scene_position_str = map_handle.get_map_system_path_str_for_list(scene_position)
                    scene_name = cache.scene_data[scene_position_str].scene_name
                    if character_data.is_follow == 1:
                        npc_list[npc_id-1] = name + " : " + scene_name + "   跟随中"
                    else:
                        npc_list[npc_id-1] = name + " : " + scene_name + "   未跟随"
                    # print("npc_list[npc_id-1] :",npc_list[npc_id-1])
            self.handle_panel.text_list = npc_list
            self.handle_panel.update()
            title_draw.draw()
            return_list = []
            line_feed.draw()
            self.handle_panel.draw()
            return_list.extend(self.handle_panel.return_list)
            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

class FindDraw:
    """
    显示可点击的NPC名字+位置按钮对象
    Keyword arguments:
    text -- 食物名字
    width -- 最大宽度
    is_button -- 绘制按钮
    num_button -- 绘制数字按钮
    button_id -- 数字按钮id
    """

    def __init__(
        self, text: Tuple[str, str], width: int, is_button: bool, num_button: bool, button_id: int
    ):
        """初始化绘制对象"""
        self.text = text
        """ 食物名字 """
        self.cid = text[0]
        """ 食物在食堂内的表id """
        self.draw_text: str = ""
        """ 食物名字绘制文本 """
        self.width: int = width
        """ 最大宽度 """
        self.num_button: bool = num_button
        """ 绘制数字按钮 """
        self.button_id: int = button_id
        """ 数字按钮的id """
        self.button_return: str = str(button_id)
        """ 按钮返回值 """
        name_draw = draw.NormalDraw()
        # print("text :",text)
        if is_button:
            if num_button:
                index_text = text_handle.id_index(button_id)
                button_text = f"{index_text}{text}"
                name_draw = draw.LeftButton(
                    button_text, self.button_return, self.width, cmd_func=self.see_call_list
                )
            else:
                button_text = f"[{text}]"
                name_draw = draw.CenterButton(
                    button_text, text, self.width, cmd_func=self.see_call_list
                )
                self.button_return = text
            self.draw_text = button_text
        else:
            name_draw = draw.CenterDraw()
            name_draw.text = f"[{text}]"
            name_draw.width = self.width
            self.draw_text = name_draw.text
        self.now_draw = name_draw
        """ 绘制的对象 """


    def draw(self):
        """绘制对象"""
        self.now_draw.draw()

    def see_call_list(self):
        """点击后进行召集"""
        title_draw = draw.TitleLineDraw(self.text, window_width)
        return_list = []
        title_draw.draw()
        character_id = self.button_id + 1
        character_data: game_type.Character = cache.character_data[character_id]
        if character_data.is_follow == 0:
            character_data.is_follow = 1
            now_draw = draw.NormalDraw()
            now_draw.text = character_data.name + "进入跟随模式"
        else:
            character_data.is_follow = 0
            now_draw = draw.NormalDraw()
            now_draw.text = character_data.name + "退出跟随模式"
        now_draw.width = 1
        now_draw.draw()
        line_feed.draw()
        # back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
        # back_draw.draw()
        # line_feed.draw()
        # return_list.append(back_draw.return_text)
        # yrn = flow_handle.askfor_all(return_list)
        # if yrn == back_draw.return_text:
        #     break
