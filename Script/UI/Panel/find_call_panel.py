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
        self.handle_panel = panel.PageHandlePanel([], FindDraw, 20, 3, self.width, 1, 1, 0)
        while 1:
            py_cmd.clr_cmd()
            npc_list = []
            title_draw.draw()
            info_draw = draw.NormalDraw()
            follow_count = cache.character_data[0].pl_ability.follow_count
            if not cache.debug_mode:
                info_draw.text = "●当前最大同时跟随角色数量：" + str(follow_count) + "\n\n"
            else:
                info_draw.text = "●当前最大同时跟随角色数量：999(debug模式)\n\n"
            info_draw.width = self.width
            # 暂不输出跟随角色信息，等加了该功能后再输出
            # info_draw.draw()
            line_feed.draw()
            # 遍历角色id
            for npc_id in cache.npc_id_got:
                if npc_id != 0:
                    npc_list.append(npc_id)
            self.handle_panel.text_list = npc_list
            self.handle_panel.update()
            return_list = []
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
        self, NPC_id: int, width: int, is_button: bool, num_button: bool, button_id: int
    ):
        """初始化绘制对象"""
        self.npc_id: int = NPC_id
        """ 干员角色编号 """
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

        character_data = cache.character_data[self.npc_id]
        name = character_data.name
        id = str(character_data.adv).rjust(4,'0')
        scene_position = character_data.position
        scene_position_str = map_handle.get_map_system_path_str_for_list(scene_position)
        if scene_position_str[-2] == "\\" and scene_position_str[-1] == "0":
            scene_position_str = scene_position_str[:-2] + "入口"
        # scene_name = cache.scene_data[scene_position_str].scene_name
        now_draw_text = f"[{id}]{name}:{scene_position_str}   "

        # 输出跟随信息
        if character_data.sp_flag.is_follow == 1:
            now_draw_text += "智能跟随中"
        elif character_data.sp_flag.is_follow == 2:
            now_draw_text += "强制跟随中"
        elif character_data.sp_flag.is_follow == 3:
            now_draw_text += "前往博士办公室中"
        else:
            status_text = game_config.config_status[character_data.state].name
            now_draw_text += f"正在：{status_text}"

        button_text = f"{now_draw_text}"
        name_draw = draw.LeftButton(
            button_text, self.button_return, self.width, cmd_func=self.see_call_list
        )
        self.draw_text = button_text
        self.now_draw = name_draw
        """ 绘制的对象 """


    def draw(self):
        """绘制对象"""
        self.now_draw.draw()

    def see_call_list(self):
        """点击后进行召集"""
        # title_draw = draw.TitleLineDraw(self.text, window_width)
        return_list = []
        # title_draw.draw()
        line = draw.LineDraw("-", window_width)
        line.draw()
        character_data: game_type.Character = cache.character_data[self.npc_id]
        if character_data.sp_flag.is_follow == 0:
            if cache.debug_mode:
                character_data.sp_flag.is_follow = 1
                now_draw = draw.NormalDraw()
                now_draw.text = character_data.name + "进入跟随模式\n"
            else:
                character_data.sp_flag.is_follow = 3
                now_draw = draw.NormalDraw()
                now_draw.text = character_data.name + "正在前往博士办公室\n"

            # 去掉其他NPC的跟随
            # if not cache.debug_mode:
            #     for npc_id in cache.npc_id_got:
            #         if npc_id != 0 and npc_id != character_id:
            #             other_character_data = cache.character_data[npc_id]
            #             if other_character_data.sp_flag.is_follow:
            #                 other_character_data.sp_flag.is_follow = 0
            #                 now_draw.text += other_character_data.name + "退出跟随模式\n"
        elif character_data.sp_flag.is_follow == 1 and cache.debug_mode:
            character_data.sp_flag.is_follow = 3
            now_draw = draw.NormalDraw()
            now_draw.text = character_data.name + "正在前往博士办公室\n"

        else:
            character_data.sp_flag.is_follow = 0
            now_draw = draw.NormalDraw()
            now_draw.text = character_data.name + "退出跟随模式\n"
        now_draw.width = 1
        now_draw.draw()
        # back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
        # back_draw.draw()
        # line_feed.draw()
        # return_list.append(back_draw.return_text)
        # yrn = flow_handle.askfor_all(return_list)
        # if yrn == back_draw.return_text:
        #     break
