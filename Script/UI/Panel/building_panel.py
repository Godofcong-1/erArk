from turtle import position
from typing import Tuple, List
from types import FunctionType
from uuid import UUID
from Script.Core import cache_control, game_type, get_text, flow_handle, text_handle, constant, py_cmd
from Script.Design import basement,attr_text,attr_calculation
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
            money = str(cache.base_resouce.materials_resouce[1])
            resouce_text += f"\n  当前龙门币数量    ：{money}\n"
            # 碳素建材的编号是15
            # building_materials = str(cache.base_resouce.materials_resouce[15])
            # resouce_text += f"\n  当前碳素建材数量  ：{building_materials}\n"


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

        self.now_panel = building_type

    def level_up_info(self, facility_cid: int):
        """
        显示建筑升级的详细信息
        Keyword arguments:
        facility_cid -- 建筑效果编号
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
                info_draw.text += f"\n  升级需要的龙门币：{facility_data_next.money_use}\n"
                # info_draw.text += f"\n  升级需要的龙门币：{facility_data_next.money_use}\n  升级需要的基建材料：{facility_data_next.resouce_use}\n"
                info_draw.width = self.width
                info_draw.draw()

                # 最后展示资源情况
                resouce_draw = draw.NormalDraw()
                resouce_text = "\n当前资源情况："
                power_use,power_max = str(cache.base_resouce.power_use),str(cache.base_resouce.power_max)
                resouce_text += f"\n  当前使用电力/当前总供电：{power_use}/{power_max}"
                money = str(cache.base_resouce.materials_resouce[1])
                resouce_text += f"\n  当前龙门币数量    ：{money}\n"
                # 碳素建材的编号是15
                # building_materials = str(cache.base_resouce.materials_resouce[15])
                # resouce_text += f"\n  当前碳素建材数量  ：{building_materials}\n"

                resouce_draw.text = resouce_text
                resouce_draw.width = self.width
                resouce_draw.draw()

                # 判定是否可以升级
                level_up_flag = True
                up_info_draw = draw.NormalDraw()
                up_info_draw.text = "当前无法升级："
                # 电量
                if cache.base_resouce.power_max - cache.base_resouce.power_use - facility_data_next.power_use + facility_data_now.power_use >= 0:
                    pass
                else:
                    up_info_draw.text += "\n  升级所需电量不足"
                    level_up_flag = False
                # 龙门币
                if cache.base_resouce.materials_resouce[1] >= facility_data_next.money_use:
                    pass
                else:
                    up_info_draw.text += "\n  升级所需龙门币不足"
                    level_up_flag = False
                # 控制中枢等级
                if facility_cid <= 9 or facility_data_next.level <= cache.base_resouce.facility_level[0] + 1:
                    pass
                else:
                    up_info_draw.text += "\n  升级需要更高的控制中枢等级"
                    level_up_flag = False
                # 建材
                # if cache.base_resouce.materials_resouce[15] - facility_data_next.resouce_use >= 0:
                #     level_up_flag += 1
                # else:
                #     up_info_draw.text += "\n  升级所需碳素建材不足"
                up_info_draw.width = self.width

                if level_up_flag:
                    now_draw = draw.CenterButton(
                        f"【升级】",
                        f"\n【升级】",
                        self.width / 10,
                        cmd_func=self.level_up,
                        args=(facility_cid,),
                    )
                    now_draw.draw()
                    return_list.append(now_draw.return_text)
                else:
                    up_info_draw.draw()
                line_feed.draw()

            else:
                info_draw.text = "\n  当前建筑已是最高级\n\n"
                info_draw.width = self.width
                info_draw.draw()

            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text or yrn in return_list:
                break


    def level_up(self, facility_cid: int):
        """
        显示建筑升级的详细信息
        Keyword arguments:
        facility_cid -- 建筑效果编号
        """
        for all_cid in game_config.config_facility:
            facility_data = game_config.config_facility[all_cid]
            facility_data_next = game_config.config_facility_effect[facility_cid+1]
            facility_data_now = game_config.config_facility_effect[facility_cid]

            # 寻找和当前设施名一样的
            if facility_data.name == facility_data_now.name:
                cache.base_resouce.materials_resouce[1] -= facility_data_next.money_use
                cache.base_resouce.facility_level[all_cid] += 1
                basement.get_base_updata()

                # 输出提示信息
                line = draw.LineDraw("-", self.width)
                line.draw()
                info_draw = draw.WaitDraw()
                info_draw.text = f"\n{facility_data_now.name}提升到{str(cache.base_resouce.facility_level[all_cid])}级了！\n"
                info_draw.width = self.width
                info_draw.draw()
                break
