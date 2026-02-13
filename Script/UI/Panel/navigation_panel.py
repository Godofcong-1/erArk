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
from Script.Design import map_handle, attr_text, game_time
from Script.Config import game_config, normal_config
from Script.UI.Panel import achievement_panel

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

def judge_arrive():
    """
    判断是否抵达指定地点
    Keyword arguments:
    """
    from Script.Settle import default

    if cache.rhodes_island.move_target_and_time[0] != 0:
        if game_time.judge_date_big_or_small(cache.game_time, cache.rhodes_island.move_target_and_time[2]):
            # 结算抵达
            now_scene_id = cache.rhodes_island.current_location[0]
            cache.rhodes_island.base_move_visitor_flag = True
            target_scene_id = cache.rhodes_island.move_target_and_time[0]
            target_scene_name = game_config.config_birthplace[target_scene_id].name
            cache.rhodes_island.current_location[0] = target_scene_id
            # 结算变动的外交官
            if now_scene_id in cache.rhodes_island.diplomat_of_country:
                now_diplomat_chara_id = cache.rhodes_island.diplomat_of_country[now_scene_id][0]
                if now_diplomat_chara_id != 0:
                    default.handle_chara_off_line(now_diplomat_chara_id, 1, change_data = game_type.CharacterStatusChange(), now_time = cache.game_time)
            if target_scene_id in cache.rhodes_island.diplomat_of_country:
                target_diplomat_chara_id = cache.rhodes_island.diplomat_of_country[target_scene_id][0]
                if target_diplomat_chara_id != 0:
                    default.handle_chara_on_line(target_diplomat_chara_id, 1, change_data = game_type.CharacterStatusChange(), now_time = cache.game_time)
            # 清零移动目标
            cache.rhodes_island.move_target_and_time = [0, 0, 0]
            # 绘制提示信息
            now_draw = draw.WaitDraw()
            now_draw.text = _("\n罗德岛已抵达目的地：{0}\n").format(target_scene_name)
            now_draw.width = window_width
            now_draw.style = "gold_enrod"
            now_draw.draw()
            # 如果炎不在列表中，则添加
            if 17 not in cache.achievement.visited_nation_list:
                cache.achievement.visited_nation_list.append(17)
            # 结算成就
            if target_scene_id not in cache.achievement.visited_nation_list:
                cache.achievement.visited_nation_list.append(target_scene_id)
            achievement_panel.achievement_flow(_("导航"))
            return True
    return False


class Base_function_class:
    """
    用于导航的基础功能类
    """

    def move_judge(self, scene_path: List, sp_flag: int = 0):
        """
        判断基地是否移动至指定场景
        Keyword arguments:
        scene_path -- 目标场景路径，0为场景名，1为抵达该场景的距离
        sp_flag -- 0为正常，1为无法抵达非临近地点，2为移动中
        """
        scene_path[0] = _(scene_path[0])
        # 距离
        distance = scene_path[1]
        need_time = 7 + distance * 3
        # print(f"debug scene_path = {scene_path}")
        if sp_flag == 0:
            # 当前燃料
            now_fuel = cache.rhodes_island.materials_resouce[15]
            need_fuel = 1000 * distance
            if now_fuel < need_fuel and not cache.debug_mode:
                now_draw = draw.WaitDraw()
                now_draw.text = _("\n\n移动至{0}需要消耗{1}燃料，当前有{2}单位燃料，燃料不足，无法移动\n").format(scene_path[0], need_fuel, now_fuel)
                now_draw.width = window_width
                now_draw.draw()
            else:
                while 1:
                    ask_list = []
                    askfor_panel = panel.OneMessageAndSingleColumnButton()
                    askfor_list = [_("是"), _("否")]
                    askfor_panel.set(askfor_list, _("\n移动至{0}需要消耗{1}燃料，当前有{2}单位燃料，需要{3}天移动到目的地，确定要移动吗\n").format(scene_path[0], need_fuel, now_fuel, need_time), 0)
                    askfor_panel.draw()
                    askfor_panel_return_list = askfor_panel.get_return_list()
                    ask_list.extend(askfor_panel_return_list.keys())
                    yrn = flow_handle.askfor_all(ask_list)
                    py_cmd.clr_cmd()
                    if yrn == "0":
                        self.move_to_scene(scene_path[0], need_fuel, need_time)
                        break
                    elif yrn == "1":
                        break
                    else:
                        now_draw = draw.WaitDraw()
                        now_draw.text = _("\n输入错误，请重新输入\n")
                        now_draw.width = window_width
                        now_draw.draw()
        elif sp_flag == 1:
            now_draw = draw.WaitDraw()
            now_draw.text = _("\n无法直接抵达非临近地点\n")
            now_draw.width = window_width
            now_draw.draw()
        elif sp_flag == 2:
            now_draw = draw.WaitDraw()
            now_draw.text = _("\n罗德岛正在移动中，无法再次移动\n")
            now_draw.width = window_width
            now_draw.draw()


    def move_to_scene(self, scene_name: str, need_fuel: int, need_time: int):
        """
        移动至指定场景
        Keyword arguments:
        scene_name -- 目标国家名字
        need_fuel -- 移动所需燃料
        need_time -- 移动所需时间
        """
        py_cmd.clr_cmd()
        line_feed.draw()
        cache.wframe_mouse.w_frame_skip_wait_mouse = 1
        for birthplace_id in game_config.config_birthplace:
            birthplace_data = game_config.config_birthplace[birthplace_id]
            if birthplace_data.name == scene_name:
                cache.rhodes_island.move_target_and_time[0] = birthplace_id
                arrive_time = game_time.get_sub_date(day = need_time, old_date = cache.game_time)
                # debug模式下直接抵达
                if cache.debug_mode:
                    arrive_time = cache.game_time
                cache.rhodes_island.move_target_and_time[2] = arrive_time
                cache.rhodes_island.materials_resouce[15] -= need_fuel
                break


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
            # TODO 在处理好中文地图路径之后再改回来
            base_scene_name = _(now_country_name, revert_translation = True)
            # 移动中的目标地点
            if cache.rhodes_island.move_target_and_time[0] != 0:
                target_scene_id = cache.rhodes_island.move_target_and_time[0]
                target_scene_name = game_config.config_birthplace[target_scene_id].name
                now_draw = draw.NormalDraw()
                now_draw.text = _("\n罗德岛正在移动至{0}，预计抵达时间为{1}\n").format(target_scene_name, game_time.get_date_until_day(cache.rhodes_island.move_target_and_time[2]))
                now_draw.width = self.width
                now_draw.draw()
            # 临近地点
            path_edge = map_data.path_edge
            near_scene_path = path_edge[base_scene_name].copy()
            if base_scene_name in near_scene_path:
                del near_scene_path[base_scene_name]
            near_scene_path_name_list = list(near_scene_path.keys())
            return_list = []
            index = 0
            # 使用地图最大行宽来计算统一的居中偏移，使所有行左对齐
            # 兼容旧存档：如果 max_width 属性不存在，则动态计算
            if hasattr(now_draw_list, 'max_width'):
                map_max_width = now_draw_list.max_width
            else:
                map_max_width = max((line.width for line in now_draw_list.draw_text), default=0)
            fix_width = int((self.width - map_max_width) / 2)
            for now_draw_line in now_draw_list.draw_text:
                fix_text = " " * fix_width
                fix_draw = draw.NormalDraw()
                fix_draw.text = fix_text
                fix_draw.width = fix_width
                fix_draw.web_type = "map-padding"
                fix_draw.draw()
                for draw_text in now_draw_line.draw_list:
                    # print(f"debug draw_text.text = {draw_text.text}")
                    # 查询当前绘制是否为最后一个绘制
                    if draw_text == now_draw_line.draw_list[-1]:
                        now_draw_web_type = "map-last"
                    else:
                        now_draw_web_type = "map"

                    # 首先需要是地点按钮
                    if "is_button" in draw_text.__dict__ and draw_text.is_button:


                        # 如果不是基地所在的地点，则绘制按钮
                        if draw_text.text != base_scene_name:
                            # 初始化目标地点路径
                            target_scene = [draw_text.text, 1]
                            # 如果正在移动中，则目标为红色，其他为灰色
                            if cache.rhodes_island.move_target_and_time[0] != 0:
                                if draw_text.text == target_scene_name:
                                    now_draw = draw.Button(
                                        draw_text.text, draw_text.text, normal_style = "red", cmd_func=self.move_judge, args=(target_scene,2), web_type=now_draw_web_type
                                    )
                                else:
                                    now_draw = draw.Button(
                                        draw_text.text, draw_text.text,normal_style="deep_gray", cmd_func=self.move_judge, args=(target_scene,2), web_type=now_draw_web_type
                                    )
                            else:
                                # 临近地点正常绘制
                                if draw_text.text in near_scene_path_name_list:

                                    # 获取目标地点路径，包括地点名和抵达该地点的距离
                                    target_scene = [draw_text.text, near_scene_path[draw_text.text]]
                                    # 绘制按钮
                                    now_draw = draw.Button(
                                        draw_text.text, draw_text.text, cmd_func=self.move_judge, args=(target_scene,), web_type=now_draw_web_type
                                    )
                                    # TODO 如果是有特殊事件在那么显示为绿色
                                    # if len(cache.scene_data[full_scene_str].character_list):
                                    #     now_draw.normal_style = "green"
                                # 非临近地点则绘制灰色按钮
                                else:
                                    now_draw = draw.Button(
                                        draw_text.text, draw_text.text,normal_style="deep_gray", cmd_func=self.move_judge, args=(target_scene,1), web_type=now_draw_web_type
                                    )
                            now_draw.width = self.width
                            now_draw.draw()
                            return_list.append(now_draw.return_text)

                        else:
                            # 如果是基地所在的地点，则高亮显示文本
                            now_draw = draw.NormalDraw()
                            now_draw.style = "gold_enrod"
                            now_draw.text = draw_text.text
                            now_draw.web_type = now_draw_web_type
                            now_draw.draw()
                    # 如果不是地点按钮，则正常绘制文本
                    else:
                        now_draw = draw.NormalDraw()
                        now_draw.style = draw_text.style
                        now_draw.text = draw_text.text
                        now_draw.web_type = now_draw_web_type
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
            back_button = draw.CenterButton(now_text, str(now_index), int(self.width / 3))
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
        move_name_draw_list = [f"[{_(name)}]" for name in move_name_list]
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
        # TODO 在处理好中文地图路径之后再改回来
        base_scene_name = _(now_country_name, revert_translation = True)
        # 临近地点
        path_edge = map_data.path_edge
        scene_path = path_edge[base_scene_name].copy()
        if base_scene_name in scene_path:
            del scene_path[base_scene_name]
        near_scene_path_name_list = list(scene_path.keys())

        if len(near_scene_path_name_list):
            draw_list = []
            for scene_name in near_scene_path_name_list:
                # print(f"debug scene_id = {scene_id}")
                load_scene_data = map_handle.get_scene_data_for_map(map_path_str, scene_name)
                now_scene_path = map_handle.get_map_system_path_for_str(load_scene_data.scene_path)
                target_scene = [scene_name, scene_path[scene_name]]

                # now_id_text = f"{scene_id}:{load_scene_data.scene_name}"
                if scene_name == base_scene_name:
                    continue
                # 当前在移动中则也跳过
                if cache.rhodes_island.move_target_and_time[0] != 0:
                    continue
                else:
                    now_id_text = f"→{_(load_scene_data.scene_name)}"

                now_draw = draw.LeftButton(
                    now_id_text, now_id_text, self.width, cmd_func=self.move_judge, args=(target_scene,)
                )
                self.return_list.append(now_draw.return_text)
                draw_list.append(now_draw)
            draw_group = value_handle.list_of_groups(draw_list, 8)
            now_width_index = 1
            for now_draw_list in draw_group:
                if len(now_draw_list) > now_width_index:
                    now_width_index = len(now_draw_list)
            now_width = self.width / now_width_index
            for now_draw_list in draw_group:
                for now_draw in now_draw_list:
                    now_draw.width = now_width
                    now_draw.draw()
                line_feed.draw()
        self.end_index = len(near_scene_path_name_list) - 1
