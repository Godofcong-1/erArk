from turtle import position
from typing import Tuple, List
from types import FunctionType
from uuid import UUID
from Script.Core import cache_control, game_type, get_text, flow_handle, text_handle, constant, py_cmd
from Script.Design import map_handle,attr_text,attr_calculation
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

class Building_Panel:
    """
    用于显示基建界面面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.now_panel = _("区块总览")
        """ 当前绘制的页面 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """

    def draw(self):
        """绘制对象"""

        character_data: game_type.Character = cache.character_data[0]

        title_text = "基建系统"
        building_type_list = [_("区块总览"), _("特殊房间")]

        title_draw = draw.TitleLineDraw(title_text, self.width)
        handle_panel = panel.PageHandlePanel([], building_Draw, 10, 5, self.width, 1, 1, 0)
        while 1:
            return_list = []
            title_draw.draw()

            # 绘制主面板
            for building_type in building_type_list:
                if building_type == self.now_panel:
                    now_draw = draw.CenterDraw()
                    now_draw.text = f"[{building_type}]"
                    now_draw.style = "onbutton"
                    now_draw.width = self.width / len(building_type_list)
                    now_draw.draw()
                else:
                    now_draw = draw.CenterButton(
                        f"[{building_type}]",
                        f"\n{building_type}",
                        self.width / len(building_type_list),
                        cmd_func=self.change_panel,
                        args=(building_type,),
                    )
                    now_draw.draw()
                    return_list.append(now_draw.return_text)
            line_feed.draw()
            line = draw.LineDraw("+", self.width)
            line.draw()

            resouce_draw = draw.NormalDraw()
            resouce_text = "\n当前资源情况："
            power_use,power_max = str(cache.base_resouce.power_use),str(cache.base_resouce.power_max)
            resouce_text += f"\n  当前使用电力/当前总供电：{power_use}/{power_max}"
            money = str(cache.base_resouce.money)
            resouce_text += f"\n  当前龙门币数量    ：{money}"
            # 碳素建材的编号是15
            building_materials = str(cache.base_resouce.materials_resouce[15])
            resouce_text += f"\n  当前碳素建材数量  ：{building_materials}\n"


            resouce_draw.text = resouce_text
            resouce_draw.width = self.width
            resouce_draw.draw()

            facility_draw = draw.NormalDraw()
            facility_text = "\n当前设施情况："
            facility_draw.text = facility_text
            facility_draw.width = self.width
            facility_draw.draw()

            # 开始区块总览信息
            now_draw = panel.LeftDrawTextListPanel()

            if self.now_panel == "区块总览":
                now_draw.draw_list.append(line_feed)
                now_draw.width += 1

                for all_cid in game_config.config_facility:
                    facility_data = game_config.config_facility[all_cid]
                    if facility_data.type == -1:

                        # 获取该区块的一系列信息
                        facility_name = facility_data.name
                        now_level = str(cache.base_resouce.facility_level[all_cid])
                        facility_cid = game_config.config_facility_effect_data[facility_name][int(now_level)]
                        facility_power_use = str(game_config.config_facility_effect[facility_cid].power_use)
                        facility_info = facility_data.info

                        if all_cid == 1:
                            facility_power_give = str(game_config.config_facility_effect[facility_cid].effect)
                            info_head = f"{facility_name.ljust(5,'　')} (lv{now_level}) (供电:{facility_power_give})"
                        else:
                            info_head = f"{facility_name.ljust(5,'　')} (lv{now_level}) (耗电:{facility_power_use})"
                        building_text = f"  {info_head}：{facility_info}"

                        button_building_draw = draw.LeftButton(
                            _(building_text),
                            _(facility_name),
                            self.width,
                            cmd_func=self.level_up_info,
                            args=(facility_cid,),
                            )
                        return_list.append(button_building_draw.return_text)
                        now_draw.draw_list.append(button_building_draw)
                        now_draw.width += len(button_building_draw.text)
                        now_draw.draw_list.append(line_feed)
                        now_draw.width += 1


            elif self.now_panel == "特殊房间":
                now_draw.draw_list.append(line_feed)
                now_draw.width += 1

                for all_cid in game_config.config_facility:
                    facility_data = game_config.config_facility[all_cid]
                    if facility_data.type != -1:

                        facility_name = facility_data.name
                        now_level = str(cache.base_resouce.facility_level[all_cid])
                        facility_cid = game_config.config_facility_effect_data[facility_name][int(now_level)]
                        facility_power_use = str(game_config.config_facility_effect[facility_cid].power_use)
                        facility_info = facility_data.info

                        info_head = f"{facility_name.ljust(5,'　')} (lv{now_level}) (耗电:{facility_power_use})"
                        building_text = f"  {info_head}：{facility_info}"

                        button_building_draw = draw.LeftButton(
                            _(building_text),
                            _(facility_name),
                            self.width,
                            cmd_func=self.level_up_info,
                            args=(facility_cid,),
                            )
                        return_list.append(button_building_draw.return_text)
                        now_draw.draw_list.append(button_building_draw)
                        now_draw.width += len(button_building_draw.text)
                        now_draw.draw_list.append(line_feed)
                        now_draw.width += 1

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

            return_list.extend(handle_panel.return_list)
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def change_panel(self, building_type: str):
        """
        切换当前面板显示
        Keyword arguments:
        building_type -- 要切换的面板类型
        """

        if building_type == "区块总览":
            self.now_panel = "区块总览"
        elif building_type == "特殊房间":
            self.now_panel = "特殊房间"

    def level_up_info(self, facility_cid: int):
        """
        进行建筑升级
        Keyword arguments:
        bonus_id -- 奖励编号
        """

        while 1:
            return_list = []
            line = draw.LineDraw("-", self.width)
            line.draw()

            # 如果等级不是5级则显示具体信息
            info_draw = draw.NormalDraw()
            facility_data_now = game_config.config_facility_effect[facility_cid]
            if facility_data_now.level != 5:
                facility_data_next = game_config.config_facility_effect[facility_cid+1]
                info_draw.text = f"\n{facility_data_now.name}："
                info_draw.text += f"\n  当前等级：{facility_data_now.level}，当前耗电量:{facility_data_now.power_use}，当前效果：{facility_data_now.info}"
                info_draw.text += f"\n  下一等级：{facility_data_next.level}，下一等级耗电量:{facility_data_next.power_use}，下一等级效果：{facility_data_next.info}"
                info_draw.text += f"\n  升级需要的龙门币：{facility_data_next.money_use}，升级需要的基建材料：{facility_data_next.resouce_use}\n"
            else:
                info_draw.text = "\n  当前建筑已是最高级\n"
            info_draw.text += "\n"

            # 输出提示信息
            # if bonus_flag:
            #     info_draw.text = "\n  解锁成功\n"
            # else:
            #     info_draw.text = "\n  未满足条件，解锁失败\n"
            info_draw.width = self.width
            info_draw.draw()


            # 最后展示资源情况
            resouce_draw = draw.NormalDraw()
            resouce_text = "\n当前资源情况："
            power_use,power_max = str(cache.base_resouce.power_use),str(cache.base_resouce.power_max)
            resouce_text += f"\n  当前使用电力/当前总供电：{power_use}/{power_max}"
            money = str(cache.base_resouce.money)
            resouce_text += f"\n  当前龙门币数量    ：{money}"
            # 碳素建材的编号是15
            building_materials = str(cache.base_resouce.materials_resouce[15])
            resouce_text += f"\n  当前碳素建材数量  ：{building_materials}\n"

            resouce_draw.text = resouce_text
            resouce_draw.width = self.width
            resouce_draw.draw()


            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break


class building_Draw:
    """
    收藏品绘制对象
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

