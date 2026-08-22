from typing import Dict, List, Tuple
from types import FunctionType

from Script.Core import cache_control, game_type, get_text, flow_handle
from Script.Config import game_config, normal_config
from Script.Design import handle_premise
from Script.UI.Moudle import draw
from Script.System.Item_System import condom_handle

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """

line_feed = draw.NormalDraw()
""" 换行绘制对象 """
line_feed.text = "\n"
line_feed.width = 1
window_width = normal_config.config_normal.text_width
""" 屏幕宽度 """


class Condom_Select_Panel:
    """
    避孕套选择面板对象，供挂装饰/取回装饰/饮用/挤出四个指令共用\n
    Keyword arguments:\n
    width -- 绘制宽度\n
    mode -- 操作类型，hang=挂装饰，take_back=取回装饰，drink=饮用，squeeze=挤出
    """

    def __init__(self, width: int, mode: str):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.mode: str = mode
        """ 操作类型 """
        self.select_index_set: set = set()
        """ 已勾选的条目下标集合 """

    def draw(self):
        """
        绘制对象，玩家确认选择后直接调用对应的结算函数完成数据结算\n
        Return arguments:\n
        int -- 结算完成返回1，取消时返回-1
        """
        character_data: game_type.Character = cache.character_data[0]
        target_character_id = character_data.target_character_id

        # 取回装饰模式下选择的是对方身上的装饰，其他模式选择的是存量池
        if self.mode == "take_back":
            select_result = self.select_decoration(target_character_id)
            if select_result == -1:
                return -1
            condom_handle.settle_take_back(target_character_id, select_result)
            return 1

        condom_index_list = self.select_condoms()
        if condom_index_list == -1:
            return -1
        # 饮用模式无需选择部位，确认后直接结算
        if self.mode == "drink":
            condom_handle.settle_drink(target_character_id, condom_index_list)
            return 1
        # 挂装饰与挤出模式需要二级选择目标部位，确认后直接结算
        part_result = self.select_part(target_character_id)
        if part_result == -1:
            return -1
        if self.mode == "hang":
            condom_handle.settle_hang(target_character_id, part_result[0], part_result[1], condom_index_list)
        else:
            condom_handle.settle_squeeze(target_character_id, part_result[0], part_result[1], condom_index_list)
        return 1

    def select_condoms(self):
        """
        绘制存量池多选页面\n
        Return arguments:\n
        List[int] -- 勾选的存量池下标列表，取消时返回-1
        """
        mode_text_data = {
            "hang": _("挂上避孕套装饰"),
            "drink": _("饮用避孕套精液"),
            "squeeze": _("挤出避孕套精液"),
        }
        title_draw = draw.TitleLineDraw(mode_text_data.get(self.mode, _("避孕套")), self.width)
        self.select_index_set = set()
        while 1:
            return_list = []
            title_draw.draw()

            used_condoms = condom_handle.get_used_condoms()
            info_draw = draw.NormalDraw()
            info_draw.text = _("\n当前共有{0}个用过的避孕套，请勾选要使用的：\n").format(len(used_condoms))
            info_draw.width = self.width
            info_draw.draw()

            # 逐个绘制存量池中的避孕套勾选按钮
            for index in range(len(used_condoms)):
                select_text = "●" if index in self.select_index_set else "○"
                button_text = _("[{0} 避孕套{1}（{2}ml）]").format(select_text, str(index + 1), str(used_condoms[index]))
                return_text = f"condom_{index}"
                now_button = draw.Button(button_text, return_text)
                now_button.width = self.width
                now_button.draw()
                line_feed.draw()
                return_list.append(return_text)

            yrn = self.draw_confirm_and_cancel(return_list)
            if yrn == "cancel":
                return -1
            if yrn == "confirm":
                if len(self.select_index_set):
                    return sorted(self.select_index_set)
                continue
            # 勾选切换
            index = int(yrn.split("_")[1])
            if index in self.select_index_set:
                self.select_index_set.remove(index)
            else:
                self.select_index_set.add(index)

    def select_decoration(self, target_character_id: int):
        """
        绘制对方身上装饰的多选页面\n
        Keyword arguments:\n
        target_character_id -- 交互对象角色id\n
        Return arguments:\n
        List[((部位类型, 部位cid), 下标)] -- 勾选的装饰位置列表，取消时返回-1
        """
        title_draw = draw.TitleLineDraw(_("取回避孕套装饰"), self.width)
        self.select_index_set = set()
        while 1:
            return_list = []
            title_draw.draw()

            # 展平装饰字典为条目列表，每个条目为((部位类型, 部位cid), 部位内下标, 精液量)
            decoration_dict = condom_handle.get_decoration_dict(target_character_id)
            entry_list = []
            for location_key in sorted(decoration_dict.keys()):
                for index in range(len(decoration_dict[location_key])):
                    entry_list.append((location_key, index, decoration_dict[location_key][index]))

            info_draw = draw.NormalDraw()
            info_draw.text = _("\n对方身上共挂着{0}个用过的避孕套，请勾选要取回的：\n").format(len(entry_list))
            info_draw.width = self.width
            info_draw.draw()

            for entry_index in range(len(entry_list)):
                location_key, _index, semen_count = entry_list[entry_index]
                part_name = get_location_name(location_key[0], location_key[1])
                select_text = "●" if entry_index in self.select_index_set else "○"
                button_text = _("[{0} {1}上的避孕套（{2}ml）]").format(select_text, part_name, str(semen_count))
                return_text = f"decoration_{entry_index}"
                now_button = draw.Button(button_text, return_text)
                now_button.width = self.width
                now_button.draw()
                line_feed.draw()
                return_list.append(return_text)

            yrn = self.draw_confirm_and_cancel(return_list)
            if yrn == "cancel":
                return -1
            if yrn == "confirm":
                if len(self.select_index_set):
                    return [(entry_list[entry_index][0], entry_list[entry_index][1]) for entry_index in sorted(self.select_index_set)]
                continue
            entry_index = int(yrn.split("_")[1])
            if entry_index in self.select_index_set:
                self.select_index_set.remove(entry_index)
            else:
                self.select_index_set.add(entry_index)

    def select_part(self, target_character_id: int):
        """
        绘制目标部位单选页面\n
        Keyword arguments:\n
        target_character_id -- 交互对象角色id\n
        Return arguments:\n
        (部位类型, 部位cid) -- 选中的部位，取消时返回-1
        """
        target_data: game_type.Character = cache.character_data[target_character_id]
        title_draw = draw.TitleLineDraw(_("选择部位"), self.width)
        while 1:
            return_list = []
            title_draw.draw()

            info_draw = draw.NormalDraw()
            info_draw.text = _("\n请选择目标部位：\n")
            info_draw.width = self.width
            info_draw.draw()

            part_list = []
            # 挂装饰模式：仅头发 + 已穿着的服装部位
            if self.mode == "hang":
                part_list.append((0, 0))
            # 挤出模式：全部可及身体部位（口腔/子宫/胃部走饮用，兽类部位需对应素质）
            else:
                for part_cid in game_config.config_body_part:
                    if part_cid in {2, 7, 15}:
                        continue
                    if part_cid == 12 and handle_premise.handle_target_have_no_tail(0):
                        continue
                    if part_cid == 13 and handle_premise.handle_target_have_no_horn(0):
                        continue
                    if part_cid == 14 and handle_premise.handle_target_have_no_eras(0):
                        continue
                    part_list.append((0, part_cid))
            # 已穿着的服装部位
            for clothing_type in game_config.config_clothing_type:
                if len(target_data.cloth.cloth_wear[clothing_type]):
                    part_list.append((1, clothing_type))

            # 每行绘制5个居中按钮，每个按钮宽度为行宽的五分之一
            for part_index in range(len(part_list)):
                part_type, part_cid = part_list[part_index]
                part_name = get_location_name(part_type, part_cid)
                return_text = f"part_{part_index}"
                now_button = draw.CenterButton(f"[{part_name}]", return_text, self.width // 5)
                now_button.draw()
                return_list.append(return_text)
                if part_index % 5 == 4:
                    line_feed.draw()
            if len(part_list) % 5:
                line_feed.draw()

            yrn = self.draw_confirm_and_cancel(return_list, confirm_flag=False)
            if yrn == "cancel":
                return -1
            part_index = int(yrn.split("_")[1])
            return part_list[part_index]

    def draw_confirm_and_cancel(self, return_list: List[str], confirm_flag: bool = True) -> str:
        """
        绘制确认与取消按钮并等待玩家输入\n
        Keyword arguments:\n
        return_list -- 当前页面已有的响应文本列表\n
        confirm_flag -- 是否绘制确认按钮\n
        Return arguments:\n
        str -- 玩家选择的响应文本
        """
        line_feed.draw()
        if confirm_flag:
            confirm_button = draw.Button(_("[确认]"), "confirm")
            confirm_button.width = self.width // 2
            confirm_button.draw()
            return_list.append("confirm")
        cancel_button = draw.Button(_("[取消]"), "cancel")
        cancel_button.width = self.width // 2
        cancel_button.draw()
        return_list.append("cancel")
        line_feed.draw()
        return flow_handle.askfor_all(return_list)


def get_location_name(part_type: int, part_cid: int) -> str:
    """
    获取装饰部位的显示名称\n
    Keyword arguments:\n
    part_type -- 部位类型，0=身体，1=服装部位\n
    part_cid -- 部位cid\n
    Return arguments:\n
    str -- 部位显示名称
    """
    if part_type == 0:
        return game_config.config_body_part[part_cid].name
    return game_config.config_clothing_type[part_cid].name
