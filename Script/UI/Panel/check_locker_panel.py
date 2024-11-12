from typing import Tuple, Dict, List
from types import FunctionType
from Script.Core import cache_control, game_type, get_text, flow_handle, text_handle, constant, py_cmd
from Script.Design import map_handle, attr_calculation, update, attr_text
from Script.UI.Moudle import draw, panel
from Script.Config import game_config, normal_config
from Script.UI.Panel import ejaculation_panel

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


class Check_locker_Panel:
    """
    总面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.handle_panel: panel.PageHandlePanel = None
        """ 当前名字列表控制面板 """

    def draw(self):
        """绘制对象"""
        pl_data: game_type.Character = cache.character_data[0]

        # 获得地图相关的数据
        now_map = map_handle.get_map_for_path(pl_data.position)
        map_name = attr_text.get_map_path_text(now_map)
        map_path_str = map_handle.get_map_system_path_str_for_list(pl_data.position)
        map_data = cache.scene_data[map_path_str]
        title_draw = draw.TitleLineDraw(_("{0}的衣柜").format(map_name), self.width)

        self.handle_panel = panel.PageHandlePanel([], FindDraw, 20, 8, self.width, 1, 1, 0)
        while 1:
            py_cmd.clr_cmd()
            title_draw.draw()
            npc_id_list = []

            # 宿舍的情况
            if "Dormitory" in map_data.scene_tag:
                # 读取当前宿舍的npc列表
                for npc_id in cache.npc_id_got:
                    if npc_id:
                        character_data = cache.character_data[npc_id]
                        if map_path_str == character_data.dormitory:
                            for clothing_type in game_config.config_clothing_type:
                                if len(character_data.cloth.cloth_locker_in_dormitory[clothing_type]):
                                    npc_id_list.append(npc_id)
                                    break

            # 更衣室的情况
            elif "Locker_Room" in map_data.scene_tag:
                # 读取所有人物是否有在衣柜里存放衣服
                for npc_id in cache.npc_id_got:
                    if npc_id:
                        character_data = cache.character_data[npc_id]
                        for clothing_type in game_config.config_clothing_type:
                            if len(character_data.cloth.cloth_locker_in_shower[clothing_type]):
                                npc_id_list.append(npc_id)
                                break

            info_draw = draw.NormalDraw()
            if len(npc_id_list):
                info_draw.text = _("\n发现以下衣柜里有衣服\n\n")
            else:
                info_draw.text = _("\n所有衣柜都是空的\n\n")
            info_draw.width = self.width
            info_draw.draw()

            self.handle_panel.text_list = npc_id_list
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
    显示可点击的NPC名字按钮对象
    Keyword arguments:
    text -- 食物名字
    width -- 最大宽度
    is_button -- 绘制按钮
    num_button -- 绘制数字按钮
    button_id -- 数字按钮id
    """

    def __init__(
        self, npc_id: int, width: int, is_button: bool, num_button: bool, button_id: int
    ):
        """初始化绘制对象"""
        self.npc_id = npc_id
        """ 角色id """
        self.character_data = cache.character_data[npc_id]
        """ 角色数据 """
        self.pl_data: game_type.Character = cache.character_data[0]
        """ 玩家角色数据 """
        self.draw_text: str = ""
        """ 名字绘制文本 """
        self.width: int = width
        """ 最大宽度 """
        self.num_button: bool = num_button
        """ 绘制数字按钮 """
        self.button_id: int = button_id
        """ 数字按钮的id """
        self.button_return: str = str(button_id)
        """ 按钮返回值 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """

        # 获得地图相关的数据
        pl_character_data: game_type.Character = cache.character_data[0]
        map_path_str = map_handle.get_map_system_path_str_for_list(pl_character_data.position)
        map_data = cache.scene_data[map_path_str]

        # 获取当前衣柜是哪个衣柜
        if "Locker_Room" in map_data.scene_tag:
            self.now_locker = self.character_data.cloth.cloth_locker_in_shower
        elif "Dormitory" in map_data.scene_tag:
            self.now_locker = self.character_data.cloth.cloth_locker_in_dormitory

        name_draw = draw.NormalDraw()
        # print("text :",text)
        if is_button:
            if num_button:
                index_text = text_handle.id_index(button_id)
                button_text = _("{0}{1}的衣柜").format(index_text, self.character_data.name)
                name_draw = draw.LeftButton(
                    button_text, self.button_return, self.width, cmd_func=self.check_cloth
                )
            self.draw_text = button_text
        self.now_draw = name_draw
        """ 绘制的对象 """

    def draw(self):
        """绘制对象"""
        self.now_draw.draw()

    def check_cloth(self):
        """点击后进入衣服操作子界面"""
        # title_draw = draw.TitleLineDraw(self.text, window_width)
        return_list = []
        # title_draw.draw()
        cloth_show_draw = draw.NormalDraw()
        self.pl_data.target_character_id = self.npc_id
        while 1:
            line = draw.LineDraw("-", window_width)
            line.draw()
            cloth_show_text = _("\n{0}的衣柜里放着刚脱下来的：\n").format(self.character_data.name)
            for clothing_type in game_config.config_clothing_type:
                cloth_list = self.now_locker[clothing_type]
                # 检查是否有该衣服的污浊信息，如果没有的话则补上
                if len(self.character_data.dirty.cloth_locker_semen) <= clothing_type:
                    # 首先先尝试看角色身上的服装污浊信息是否可以同步过去
                    if len(self.character_data.dirty.cloth_semen[clothing_type]):
                        self.character_data.dirty.cloth_locker_semen = self.character_data.dirty.cloth_semen
                    # 如果角色身上的服装污浊信息为空，则补上
                    else:
                        part_name = game_config.config_clothing_type[clothing_type].name
                        self.character_data.dirty.cloth_locker_semen.append([part_name,0,0,0])

                if len(cloth_list):
                    for cloth_id in cloth_list:
                        # 跳过序号不存在的服装
                        if cloth_id not in game_config.config_clothing_tem:
                            continue
                        cloth_name = game_config.config_clothing_tem[cloth_id].name
                        cloth_show_text += f" {cloth_name}"
                    semen_now_count = self.character_data.dirty.cloth_locker_semen[clothing_type][1]
                    if semen_now_count:
                        cloth_show_text += _("({0}ml精液)").format(semen_now_count)
            cloth_show_draw.text = cloth_show_text + "\n\n"
            cloth_show_draw.draw()

            # 选项面板
            # button_all_draw = panel.LeftDrawTextListPanel()

            button0_text = _("[001]把内衣拿起来闻一闻味道")
            button0_draw = draw.LeftButton(
                _(button0_text),
                _("1"),
                window_width,
                cmd_func=self.smell,
                args=(),
                )
            line_feed.draw()
            button0_draw.draw()
            return_list.append(button0_draw.return_text)

            if len(self.now_locker[9]):
                button1_text = _("[002]偷走内裤")
                button1_draw = draw.LeftButton(
                    _(button1_text),
                    _("2"),
                    window_width,
                    cmd_func=self.get_pan,
                    args=(),
                    )
                line_feed.draw()
                button1_draw.draw()
                return_list.append(button1_draw.return_text)

            if len(self.now_locker[10]):
                button2_text = _("[003]偷走袜子")
                button2_draw = draw.LeftButton(
                    _(button2_text),
                    _("3"),
                    window_width,
                    cmd_func=self.get_socks,
                    args=(),
                    )
                line_feed.draw()
                button2_draw.draw()
                return_list.append(button2_draw.return_text)

            button3_text = _("[004]用衣服冲，射在上面")
            button3_draw = draw.LeftButton(
                _(button3_text),
                _("4"),
                window_width,
                cmd_func=self.shoot_in_cloth,
                args=(),
                )
            line_feed.draw()
            button3_draw.draw()
            return_list.append(button3_draw.return_text)

            # return_list.append(button0_draw.return_text)
            # button_all_draw.draw_list.append(button0_draw)
            # button_all_draw.width += len(button0_draw.text)
            # button_all_draw.draw_list.append(line_feed)
            # button_all_draw.width += 1

            # self.draw_list.extend(button_all_draw.draw_list)
            # for label in self.draw_list:
            #     if isinstance(label, list):
            #         for value in label:
            #             value.draw()
            #         line_feed.draw()
            #     else:
            #         label.draw()

            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                break

    def smell(self):
        """闻味道"""

        self.pl_data.behavior.duration = 1
        self.pl_data.behavior.behavior_id = constant.Behavior.SMELL_UNDERWEAR
        self.pl_data.state = constant.CharacterStatus.STATUS_SMELL_UNDERWEAR
        update.game_update_flow(1)

    def get_pan(self):
        """偷内裤"""

        pan_id = self.now_locker[9][-1]
        pan_name = game_config.config_clothing_tem[pan_id].name
        self.pl_data.pl_collection.npc_panties_tem.setdefault(self.npc_id, [])
        self.pl_data.pl_collection.npc_panties_tem[self.npc_id].append(pan_id)
        self.now_locker[9] = []
        now_draw = draw.WaitDraw()
        now_draw.width = window_width
        now_draw.text = _("\n获得了{0}的{1}，可在藏品馆里纳入收藏\n").format( self.character_data.name, pan_name)
        now_draw.draw()

    def get_socks(self):
        """偷袜子"""

        socks_id = self.now_locker[10][-1]
        socks_name = game_config.config_clothing_tem[socks_id].name
        self.pl_data.pl_collection.npc_socks_tem.setdefault(self.npc_id, [])
        self.pl_data.pl_collection.npc_socks_tem[self.npc_id].append(socks_id)
        self.now_locker[10] = []
        now_draw = draw.WaitDraw()
        now_draw.width = window_width
        now_draw.text = _("\n获得了{0}的{1}，可在藏品馆里纳入收藏\n").format( self.character_data.name, socks_name)
        now_draw.draw()

    def shoot_in_cloth(self):
        """射在衣服上"""

        shoot_in_cloth_panel = panel.PageHandlePanel([], Ejaculation_NameDraw, 20, 1, window_width, 1, 1, 0)

        while 1:
            return_list = []
            line_feed.draw()
            line = draw.LineDraw("-", window_width)
            line.draw()

            cloth_type_list = []
            for clothing_type in game_config.config_clothing_type:
                cloth_list = self.now_locker[clothing_type]
                if len(cloth_list):
                    cloth_type_list.append([clothing_type, self.npc_id])
            # print(f"debug cloth_type_list = {cloth_type_list}")

            # 绘制面板本体
            shoot_in_cloth_panel.text_list = cloth_type_list
            shoot_in_cloth_panel.update()
            shoot_in_cloth_panel.draw()
            return_list.extend(shoot_in_cloth_panel.return_list)
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)

            # 在非页面切换时退出面板
            if yrn == back_draw.return_text:
                break


class Ejaculation_NameDraw:
    """
    点击后可选择射精部位按钮对象
    Keyword arguments:
    text -- 部位名
    width -- 最大宽度
    is_button -- 绘制按钮
    num_button -- 绘制数字按钮
    button_id -- 数字按钮id
    """

    def __init__(self, text: list, width: int, is_button: bool, num_button: bool, button_id: int):
        """初始化绘制对象"""
        self.index = text[0]
        """ 部位id """
        self.npc_id = text[1]
        """ 角色id """
        self.draw_text: str = ""
        """ 部位名字绘制文本 """
        self.width: int = width
        """ 最大宽度 """
        self.num_button: bool = num_button
        """ 绘制数字按钮 """
        self.button_id: int = button_id
        """ 数字按钮的id """
        self.button_return: str = str(button_id)
        """ 按钮返回值 """

        # 获得地图相关的数据
        pl_character_data: game_type.Character = cache.character_data[0]
        target_data: game_type.Character = cache.character_data[self.npc_id]
        map_path_str = map_handle.get_map_system_path_str_for_list(pl_character_data.position)
        map_data = cache.scene_data[map_path_str]

        # 获取当前衣柜是哪个衣柜
        if "Locker_Room" in map_data.scene_tag:
            now_locker = target_data.cloth.cloth_locker_in_shower
            self.locker_type = 2
        elif "Dormitory" in map_data.scene_tag:
            now_locker = target_data.cloth.cloth_locker_in_dormitory
            self.locker_type = 3

        # 获取衣服名字
        now_text = game_config.config_clothing_type[self.index].name
        cloth_name_text = ":"
        for cloth_id in now_locker[self.index]:
            cloth_name_text += f" {game_config.config_clothing_tem[cloth_id].name}"
        now_text += cloth_name_text
        # print(f"debug text = {text}, self.text = {self.text}")

        # 绘制按钮
        if is_button:
            if num_button:
                index_text = text_handle.id_index(button_id)
                button_text = f"{index_text} {now_text}"
                if target_data.dirty.cloth_locker_semen[self.index][1] != 0:
                    button_text += _(" ({0}ml精液)").format(str(target_data.dirty.cloth_locker_semen[self.index][1]))
                name_draw = draw.LeftButton(
                    button_text, self.button_return, self.width, cmd_func=self.shoot_here
                )
            else:
                button_text = f"[{now_text}]"
                name_draw = draw.CenterButton(
                    button_text, now_text, self.width, cmd_func=self.shoot_here
                )
                self.button_return = now_text
            self.draw_text = button_text
        self.now_draw = name_draw
        """ 绘制的对象 """

    def draw(self):
        """绘制对象"""
        self.now_draw.draw()

    def shoot_here(self):
        py_cmd.clr_cmd()
        # 调用射精流程
        ejaculation_panel.ejaculation_flow(part_cid=self.index, part_type=self.locker_type, target_character_id=self.npc_id, draw_flag=True)

