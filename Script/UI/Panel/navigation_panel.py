from typing import List, Dict
from types import FunctionType
from Script.UI.Moudle import draw, panel
from Script.Core import (
    get_text,
    cache_control,
    game_type,
    flow_handle,
    value_handle,
    text_handle,
    constant,
    py_cmd,
)
from Script.Design import map_handle, attr_text, character_move
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

class Base_function_class:
    """
    用于导航的基础功能类
    """

    def move_now(self, scene_path: List[str], sp_flag: int = 0):
        """
        控制基地移动至指定场景
        Keyword arguments:
        scene_path -- 目标场景路径
        sp_flag -- 0为正常，1为无法抵达非临近地点
        """
        if sp_flag == 0:
            py_cmd.clr_cmd()
            line_feed.draw()
            cache.wframe_mouse.w_frame_skip_wait_mouse = 1
            for birthplace_id in game_config.config_birthplace:
                birthplace_data = game_config.config_birthplace[birthplace_id]
                if birthplace_data.name == scene_path[-1]:
                    cache.rhodes_island.current_location[0] = birthplace_id
                    break
        elif sp_flag == 1:
            now_draw = draw.WaitDraw()
            now_draw.text = _("\n无法直接抵达非临近地点\n")
            now_draw.width = window_width
            now_draw.draw()


class Navigation_Panel(Base_function_class):
    """
    用于导航的面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.now_map: List[str] = ['泰拉']
        """ 当前查看的地图坐标 """

    def draw(self):
        """绘制对象"""
        move_menu_panel_data = {
            0: MapSceneNameDraw(self.now_map, self.width),
        }
        move_menu_panel = MoveMenuPanel(self.width)
        while 1:
            line_feed.draw()
            map_path_str = map_handle.get_map_system_path_str_for_list(self.now_map)
            map_data: game_type.Map = cache.map_data[map_path_str]
            map_name = attr_text.get_map_path_text(self.now_map)
            title_draw = draw.TitleLineDraw(map_name, self.width)
            title_draw.draw()
            now_draw_list: game_type.MapDraw = map_data.map_draw
            # 当前位置
            now_country_id = cache.rhodes_island.current_location[0]
            now_country_name = game_config.config_birthplace[now_country_id].name
            now_city_id = cache.rhodes_island.current_location[1]
            now_city_name = game_config.config_city[now_city_id].name
            base_scene_name = now_country_name
            # 临近地点
            path_edge = map_data.path_edge
            scene_path = path_edge[base_scene_name].copy()
            if base_scene_name in scene_path:
                del scene_path[base_scene_name]
            near_scene_path_list = list(scene_path.keys())
            # print(f"debug self.now_map = {self.now_map}, map_path_str = {map_path_str}，map_name = {map_name}, character_data.position = {character_data.position}, character_scene_id = {character_scene_name}")
            return_list = []
            index = 0
            for now_draw_line in now_draw_list.draw_text:
                fix_width = int((self.width - now_draw_line.width) / 2)
                fix_text = " " * fix_width
                fix_draw = draw.NormalDraw()
                fix_draw.text = fix_text
                fix_draw.width = fix_width
                fix_draw.draw()
                for draw_text in now_draw_line.draw_list:
                    # print(f"debug draw_text.text = {draw_text.text}")

                    # 首先需要是地点按钮
                    if "is_button" in draw_text.__dict__ and draw_text.is_button:

                        # 获取地点路径
                        scene_path = map_handle.get_scene_path_for_map_scene_id(
                            self.now_map, draw_text.text
                        )

                        # 如果不是基地所在的地点，则绘制按钮
                        if draw_text.text != base_scene_name:
                            # 临近地点正常绘制
                            if draw_text.text in near_scene_path_list:
                                now_draw = draw.Button(
                                    draw_text.text, draw_text.text, cmd_func=self.move_now, args=(scene_path,)
                                )
                                # TODO 如果是有特殊事件在那么显示为绿色
                                # if len(cache.scene_data[full_scene_str].character_list):
                                #     now_draw.normal_style = "green"
                            # 非临近地点则绘制灰色按钮
                            else:
                                now_draw = draw.Button(
                                    draw_text.text, draw_text.text,normal_style="deep_gray", cmd_func=self.move_now, args=(scene_path,1)
                                )
                            now_draw.width = self.width
                            now_draw.draw()
                            return_list.append(now_draw.return_text)

                        else:
                            # 如果是基地所在的地点，则高亮显示文本
                            now_draw = draw.NormalDraw()
                            now_draw.style = "gold_enrod"
                            now_draw.text = draw_text.text
                            now_draw.width = self.width
                            now_draw.draw()
                    # 如果不是地点按钮，则正常绘制文本
                    else:
                        now_draw = draw.NormalDraw()
                        now_draw.style = draw_text.style
                        now_draw.text = draw_text.text
                        now_draw.width = self.width
                        now_draw.draw()
                line_feed.draw()

            scene_id_list = list(path_edge.keys())
            now_index = len(scene_id_list)
            index = now_index
            move_menu_panel.update()
            move_menu_panel.draw()
            return_list.extend(move_menu_panel.return_list)
            if move_menu_panel.now_type in move_menu_panel_data:
                now_move_menu = move_menu_panel_data[move_menu_panel.now_type]
                now_move_menu.update(self.now_map, index)
                now_move_menu.draw()
                now_index = now_move_menu.end_index + 1
                return_list.extend(now_move_menu.return_list)
            line = draw.LineDraw("=", self.width)
            line.draw()
            back_id = text_handle.id_index(now_index)
            now_text = back_id + _("返回")
            back_button = draw.CenterButton(now_text, str(now_index), self.width / 3)
            back_button.draw()
            return_list.append(back_button.return_text)
            now_index += 1
            line_feed.draw()
            yrn = flow_handle.askfor_all(return_list)
            py_cmd.clr_cmd()
            if yrn == back_button.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break


class MoveMenuPanel:
    """
    快捷移动菜单面板
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 最大绘制宽度 """
        self.return_list: List[str] = []
        """ 监听的按钮列表 """
        self.now_type: int = 0
        """ 当前的移动菜单类型 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的对象列表 """
        self.move_type_id_data: Dict[str, int] = {
            game_config.config_move_menu_type[i].name: i for i in game_config.config_move_menu_type
        }
        """ 移动类型名字对应配表id """

    def update(self):
        """更新绘制面板"""
        line = draw.LineDraw(".", self.width)
        self.draw_list = []
        self.return_list = []
        self.draw_list.append(line)
        menu_draw = panel.CenterDrawButtonListPanel()
        move_name_list = [
            game_config.config_move_menu_type[i].name for i in game_config.config_move_menu_type
        ]
        move_name_draw_list = [f"[{name}]" for name in move_name_list]
        menu_draw.set(
            move_name_draw_list,
            move_name_list,
            self.width,
            len(game_config.config_move_menu_type),
            move_name_draw_list[self.now_type],
            self.change_type,
        )
        self.draw_list.append(menu_draw)
        self.return_list.extend(menu_draw.return_list)

    def change_type(self, to_type: str):
        """
        改变当前快捷移动菜单类型
        Keyword arguments:
        to_type -- 指定的新类型id
        """
        self.now_type = self.move_type_id_data[to_type]
        py_cmd.clr_cmd()

    def draw(self):
        """绘制面板"""
        for now_draw in self.draw_list:
            now_draw.draw()
        line = draw.LineDraw("-.-", self.width)
        line.draw()


class MapSceneNameDraw(Base_function_class):
    """
    绘制指定地图地图场景id对应场景名列表
    Keyword arguments:
    now_map -- 地图路径
    width -- 绘制宽度
    """

    def __init__(self, now_map: List[str], width: int):
        self.width: int = width
        """ 绘制的最大宽度 """
        self.now_map: List[str] = now_map
        """ 当前查看的地图坐标 """
        self.return_list: List[str] = []
        """ 当前面板的按钮返回 """
        self.end_index: int = 0
        """ 结束按钮id """

    def update(self, now_map: List[str], start_index: int):
        """
        更新当前面板对象
        Keyword arguments:
        now_map -- 当前地图
        start_index -- 起始按钮id
        """
        self.now_map = now_map

    def draw(self):
        """绘制面板"""
        self.return_list = []

        map_path_str = map_handle.get_map_system_path_str_for_list(self.now_map)
        map_data: game_type.Map = cache.map_data[map_path_str]
        map_name = attr_text.get_map_path_text(self.now_map)
        title_draw = draw.TitleLineDraw(map_name, self.width)
        title_draw.draw()
        now_draw_list: game_type.MapDraw = map_data.map_draw
        # 当前位置
        now_country_id = cache.rhodes_island.current_location[0]
        now_country_name = game_config.config_birthplace[now_country_id].name
        now_city_id = cache.rhodes_island.current_location[1]
        now_city_name = game_config.config_city[now_city_id].name
        base_scene_name = now_country_name
        # 临近地点
        path_edge = map_data.path_edge
        scene_path = path_edge[base_scene_name].copy()
        if base_scene_name in scene_path:
            del scene_path[base_scene_name]
        near_scene_path_list = list(scene_path.keys())

        if len(near_scene_path_list):
            draw_list = []
            for scene_id in near_scene_path_list:
                # print(f"debug scene_id = {scene_id}")
                load_scene_data = map_handle.get_scene_data_for_map(map_path_str, scene_id)
                now_scene_path = map_handle.get_map_system_path_for_str(load_scene_data.scene_path)

                # now_id_text = f"{scene_id}:{load_scene_data.scene_name}"
                if scene_id == base_scene_name:
                    continue
                else:
                    now_id_text = f"→{load_scene_data.scene_name}"

                now_draw = draw.LeftButton(
                    now_id_text, now_id_text, self.width, cmd_func=self.move_now, args=(now_scene_path,)
                )
                self.return_list.append(now_draw.return_text)
                draw_list.append(now_draw)
            draw_group = value_handle.list_of_groups(draw_list, 8)
            now_width_index = 0
            for now_draw_list in draw_group:
                if len(now_draw_list) > now_width_index:
                    now_width_index = len(now_draw_list)
            now_width = self.width / now_width_index
            for now_draw_list in draw_group:
                for now_draw in now_draw_list:
                    now_draw.width = now_width
                    now_draw.draw()
                line_feed.draw()
        self.end_index = len(near_scene_path_list) - 1
