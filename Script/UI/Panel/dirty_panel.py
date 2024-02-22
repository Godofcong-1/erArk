from turtle import position
from typing import Tuple, List
from types import FunctionType
from uuid import UUID
from Script.Core import cache_control, game_type, get_text, flow_handle, text_handle, constant, py_cmd
from Script.Design import map_handle, attr_text, attr_calculation
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


class Dirty_Panel:
    """
    用于显示污浊界面面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.now_panel = _("身体")
        """ 当前绘制的页面 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """

    def draw(self):
        """绘制对象"""

        character_data: game_type.Character = cache.character_data[0]
        target_data: game_type.Character = cache.character_data[character_data.target_character_id]

        title_text = target_data.name + "污浊情况"
        dirty_type_list = [_("身体"), _("服装")]

        title_draw = draw.TitleLineDraw(title_text, self.width)
        handle_panel = panel.PageHandlePanel([], Dirty_Draw, 10, 5, self.width, 1, 1, 0)
        while 1:
            return_list = []
            title_draw.draw()

            # 绘制主面板
            for dirty_type in dirty_type_list:
                if dirty_type == self.now_panel:
                    now_draw = draw.CenterDraw()
                    now_draw.text = f"[{dirty_type}]"
                    now_draw.style = "onbutton"
                    now_draw.width = self.width / len(dirty_type_list)
                    now_draw.draw()
                else:
                    now_draw = draw.CenterButton(
                        f"[{dirty_type}]",
                        dirty_type,
                        self.width / len(dirty_type_list),
                        cmd_func=self.change_panel,
                        args=(dirty_type,),
                    )
                    now_draw.draw()
                    return_list.append(now_draw.return_text)
            line_feed.draw()
            line = draw.LineDraw("+", self.width)
            line.draw()

            name_draw = draw.NormalDraw()

            # 遍历全部位并输出结果
            if self.now_panel == "身体":
                a_clean_list = [" <脏污>", " <灌肠中>", " <已灌肠清洁过>", " <精液灌肠中>", " <已精液灌肠过>"]
                now_text = "\n"
                for i in range(len(game_config.config_body_part)):
                    now_text += "  " + target_data.dirty.body_semen[i][0] + "："

                    # 腔内透视判定
                    if i in {6,7,8,9}:
                        if not (character_data.pl_ability.visual and character_data.talent[308]):
                            now_text += "<未知>（需要腔内透视）\n"
                            continue

                    # 小穴
                    if i == 6:
                        # 处女判定
                        if not target_data.talent[0]:
                            now_day = cache.game_time.day
                            first_day = target_data.first_record.first_sex_time.day
                            if now_day == first_day:
                                now_text += " <破处血>"

                        # 润滑判定
                        if target_data.status_data[8]:
                            level = attr_calculation.get_status_level(target_data.status_data[8])
                            if level <= 2:
                                now_text += " <些许爱液>"
                            elif level <= 4:
                                now_text += " <充分湿润>"
                            elif level <= 6:
                                now_text += " <泛滥的一塌糊涂>"
                            else:
                                now_text += " <泛滥的一塌糊涂>"

                    # 后穴
                    if i == 8:
                        a_clean_text = a_clean_list[target_data.dirty.a_clean]
                        now_text += a_clean_text

                    # 尿道
                    if i == 9:
                        if target_data.urinate_point <= 30:
                            now_text += " <残留的尿渍>"
                        elif target_data.urinate_point <= 120:
                            now_text += " <洁净>"
                        elif target_data.urinate_point <= 191:
                            now_text += " <些许尿意>"
                        elif target_data.urinate_point >= 192:
                            now_text += " <充盈的尿意>"
                    if target_data.dirty.body_semen[i][1]:
                        now_text += f" <{str(target_data.dirty.body_semen[i][1])}ml精液>"
                    now_text += "\n"
                now_text += "\n"

            elif self.now_panel == "服装":

                now_text = ""
                # 遍历全部衣服类型
                for clothing_type in game_config.config_clothing_type:
                    type_name = game_config.config_clothing_type[clothing_type].name
                    # 当该类型里有衣服存在的时候才显示
                    if len(target_data.cloth.cloth_wear[clothing_type]):
                        now_text += f"  [{type_name}]:"
                        # 正常情况下不显示胸部和内裤的服装,debug或该部位可以显示则显示
                        if clothing_type in {6, 9} and not cache.debug_mode:
                            if not target_data.cloth.cloth_see[clothing_type]:
                                now_text += " 未知（需要内衣透视）\n"
                                continue
                        # 如果有多件衣服，则依次显示
                        for cloth_id in target_data.cloth.cloth_wear[clothing_type]:
                            cloth_name = game_config.config_clothing_tem[cloth_id].name
                            now_text += f" {cloth_name}"
                            # 如果该部位有精液，则显示精液信息
                            if target_data.dirty.cloth_semen[clothing_type][1] != 0:
                                now_text += f" ({str(target_data.dirty.cloth_semen[clothing_type][1])}ml精液)"
                        now_text += "\n"

            name_draw.text = now_text
            name_draw.width = self.width
            name_draw.draw()

            return_list.extend(handle_panel.return_list)
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def change_panel(self, dirty_type: str):
        """
        切换当前面板显示
        Keyword arguments:
        dirty_type -- 要切换的面板类型
        """

        self.now_panel = dirty_type


class Dirty_Draw:
    """
    污浊绘制对象
    Keyword arguments:
    text -- 道具id
    width -- 最大宽度
    """

    def __init__(self, text: int, width: int):
        """初始化绘制对象"""
        self.draw_text: str = ""
        """ 绘制文本 """
        self.width: int = width
        """ 最大宽度 """

        name_draw = draw.NormalDraw()

        name_draw.text = ""
        name_draw.width = self.width
        self.draw_text = ""
        self.now_draw = name_draw
        """ 绘制的对象 """

    def draw(self):
        """绘制对象"""
        self.now_draw.draw()


class SeeCharacterBodyPanel:
    """
    显示角色身体面板对象
    Keyword arguments:
    character_id -- 角色id
    width -- 绘制宽度
    column -- 每行状态最大个数
    type_number -- 显示的状态类型
    """

    def __init__(self, character_id: int, width: int, column: int, type_number: int, center_status: bool = True):
        """初始化绘制对象"""
        self.character_id = character_id
        """ 要绘制的角色id """
        self.width = width
        """ 面板最大宽度 """
        self.column = column
        """ 每行状态最大个数 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """
        self.return_list: List[str] = []
        """ 当前面板监听的按钮列表 """
        self.center_status: bool = center_status
        """ 居中绘制状态文本 """
        self.type_number = type_number
        """ 显示的状态类型 """
        character_data = cache.character_data[0]
        target_character_data = cache.character_data[character_data.target_character_id]
        # print("game_config.config_character_state_type :",game_config.config_character_state_type)
        # print("game_config.config_character_state_type_data :",game_config.config_character_state_type_data)

        type_line = draw.LittleTitleLineDraw("身体", width, ":")
        # print("type_data.name :",type_data.name)
        now_draw = panel.LeftDrawTextListPanel()
        text_draw = draw.NormalDraw()

        # 全部位文本
        all_part_text = ""
        # 腹部整体精液量统计
        abdomen_all_semen = 0

        # 遍历全部位并输出结果
        for i in range(len(game_config.config_body_part)):
            body_part_data = game_config.config_body_part[i]
            part_name = body_part_data.name
            now_part_text = f" {part_name}"
            now_part_show_flag = False

            # 检查脏污数据中是否包含该部位，如果没有则补上
            if len(target_character_data.dirty.body_semen) <= i:
                target_character_data.dirty.body_semen.append([part_name,0,0,0])

            # 污浊判定
            if target_character_data.dirty.body_semen[i][2]:
                now_part_show_flag = True
                semen_level = target_character_data.dirty.body_semen[i][2]
                dirty_text_cid = f"{part_name}精液污浊{str(semen_level)}"
                dirty_text_context = game_config.ui_text_data['dirty'][dirty_text_cid]
                now_part_text += f"{dirty_text_context}"

            # 小穴
            if i == 6:
                # 润滑判定
                if target_character_data.status_data[8]:
                    if now_part_show_flag:
                        now_part_text += ","
                    else:
                        now_part_show_flag = True
                    level = attr_calculation.get_status_level(target_character_data.status_data[8])
                    if level <= 2:
                        now_part_text += "有些许爱液"
                    elif level <= 4:
                        now_part_text += "充分湿润着爱液"
                    elif level <= 6:
                        now_part_text += "爱液泛滥的一塌糊涂"
                    else:
                        now_part_text += "爱液像泉水一样涌出"

            # 腹部整体的精液量累积
            if i in [5,7,8,15]:
                abdomen_all_semen += target_character_data.dirty.body_semen[i][1]

            # 腔内透视判定
            if i in {6,7,8,9,15}:
                if not (character_data.pl_ability.visual and character_data.talent[308]):
                    now_part_show_flag = False

            # 如果当前部位有污浊，则加入到总文本中
            if now_part_show_flag:
                all_part_text += now_part_text

        # 如果有生理透视，则显示当前生理周期与受精概率
        if character_data.pl_ability.visual and character_data.talent[309]:
            # 生理周期文本
            reproduction_periods = {
                0: "安全期",
                1: "普通期",
                2: "危险期",
                3: "排卵期"
            }
            reproduction_period = target_character_data.pregnancy.reproduction_period
            now_reproduction_period_type = game_config.config_reproduction_period[reproduction_period].type
            reproduction_text = reproduction_periods.get(now_reproduction_period_type, "未知期")
            # 受精概率文本
            fertilization_text = f"受精概率{target_character_data.pregnancy.fertilization_rate}%"
            # 组合文本
            now_part_text = f" 当前为{reproduction_text},{fertilization_text}"
            all_part_text += now_part_text

        # 如果腹部整体有精液，则显示腹部整体精液污浊
        if abdomen_all_semen:
            now_part_show_flag = True
            now_level = attr_calculation.get_semen_now_level(abdomen_all_semen, 20, 0)
            dirty_text_cid = f"腹部整体精液污浊{str(now_level)}"
            dirty_text_context = game_config.ui_text_data['dirty'][dirty_text_cid]
            now_part_text = f" {dirty_text_context}"
            all_part_text += now_part_text

        # 如果没有H状态，则不显示该栏
        if all_part_text != "":
            self.draw_list.append(type_line)
            all_part_text += "\n"
        text_draw.text = all_part_text
        now_draw.draw_list.append(text_draw)
        now_draw.width += len(text_draw.text)

        self.draw_list.extend(now_draw.draw_list)

    def draw(self):
        """绘制面板"""
        for label in self.draw_list:
            if isinstance(label, list):
                for value in label:
                    value.draw()
                line_feed.draw()
            else:
                label.draw()

