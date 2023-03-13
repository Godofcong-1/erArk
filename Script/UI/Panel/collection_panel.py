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

class Collection_Panel:
    """
    用于显示收藏品界面面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.now_panel = _("信物")
        """ 当前绘制的页面 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """

    def draw(self):
        """绘制对象"""

        character_data: game_type.Character = cache.character_data[0]

        title_text = "收藏品"
        collection_type_list = [_("信物"), _("内裤"), _("袜子")]

        title_draw = draw.TitleLineDraw(title_text, self.width)
        handle_panel = panel.PageHandlePanel([], collection_Draw, 10, 5, self.width, 1, 1, 0)
        while 1:
            return_list = []
            title_draw.draw()

            # 绘制主面板
            for collection_type in collection_type_list:
                if collection_type == self.now_panel:
                    now_draw = draw.CenterDraw()
                    now_draw.text = f"[{collection_type}]"
                    now_draw.style = "onbutton"
                    now_draw.width = self.width / len(collection_type_list)
                    now_draw.draw()
                else:
                    now_draw = draw.CenterButton(
                        f"[{collection_type}]",
                        collection_type,
                        self.width / len(collection_type_list),
                        cmd_func=self.change_panel,
                        args=(collection_type,),
                    )
                    now_draw.draw()
                    return_list.append(now_draw.return_text)
            line_feed.draw()
            line = draw.LineDraw("+", self.width)
            line.draw()


            bonus_draw = draw.NormalDraw()
            bonus_text = "\n收集解锁要素："
            bonus_draw.text = bonus_text
            bonus_draw.width = self.width
            bonus_draw.draw()

            # print(f"debug character_data.pl_collection.collection_bonus = {character_data.pl_collection.collection_bonus}")

            # 遍历全部收集奖励
            for cid in game_config.config_collection_bonus_data:

                now_bonus = game_config.config_collection_bonus_data[cid]
                draw_flag = False
                if now_bonus.type == "信物" and self.now_panel == "信物":
                    bonus_text = f"累积获得{now_bonus.count}个信物后，{now_bonus.info}"
                    draw_flag = True
                elif now_bonus.type == "内裤" and self.now_panel == "内裤":
                    bonus_text = f"累积获得{now_bonus.count}条内裤后，{now_bonus.info}"
                    draw_flag = True
                elif now_bonus.type == "袜子" and self.now_panel == "袜子":
                    bonus_text = f"累积获得{now_bonus.count}双袜子后，{now_bonus.info}"
                    draw_flag = True

                # 仅绘制当前面板，且根据是否已解锁来判断是绘制文本还是按钮
                if draw_flag:
                    line_feed.draw()
                    if character_data.pl_collection.collection_bonus[cid]:
                        bonus_draw = draw.NormalDraw()
                        bonus_draw.text = "  ●" + bonus_text
                        # bonus_draw.style = "onbutton"
                        bonus_draw.width = self.width
                        bonus_draw.draw()
                    else:
                        bonus_draw = draw.LeftButton(
                            "  ○" + bonus_text,
                            str(cid),
                            self.width,
                            cmd_func=self.get_bonus,
                            args=(cid,),
                        )
                        bonus_draw.draw()
                        return_list.append(bonus_draw.return_text)
            line_feed.draw()


            # 开始绘制收藏品信息
            collection_draw = draw.NormalDraw()

            collection_text = ""
            if self.now_panel == "信物":
                # 统计当前信物收集数
                self.token_count = 0
                for npc_id in cache.npc_id_got:
                    if npc_id == 0:
                        continue
                    if character_data.pl_collection.token_list[npc_id]:
                        npc_name = cache.character_data[npc_id].name
                        npc_token = cache.character_data[npc_id].token_text
                        collection_text += f"\n  {npc_name}：{npc_token}"
                        self.token_count += 1
                collection_text += f"\n当前共{self.token_count}个\n"

            elif self.now_panel == "内裤":

                # 统计当前内裤收集数
                self.pan_count = 0

                for npc_id in cache.npc_id_got:
                    if npc_id != 0:

                        # 如果有收集到该角色的处子胖次或其他普通胖次则开始绘制
                        if character_data.pl_collection.first_panties[npc_id] != "" or len(character_data.pl_collection.npc_panties[npc_id]):
                            npc_name = cache.character_data[npc_id].name
                            collection_text += f"\n  {npc_name}："
                            if npc_id in character_data.pl_collection.first_panties:
                                collection_text += f" {character_data.pl_collection.first_panties[npc_id]}"
                                self.pan_count += 1
                            if npc_id in character_data.pl_collection.npc_panties:
                                for pan in character_data.pl_collection.npc_panties[npc_id]:
                                    collection_text += f" {pan}"
                                    self.pan_count += 1
                            collection_text += f"\n"
                collection_text += f"\n当前共{self.pan_count}条\n"



            elif self.now_panel == "袜子":

                # 统计当前袜子收集数
                self.sock_count = 0

                for npc_id in cache.npc_id_got:
                    if npc_id != 0:

                        if len(character_data.pl_collection.npc_socks[npc_id]):
                            npc_name = cache.character_data[npc_id].name
                            collection_text += f"\n  {npc_name}："
                            if npc_id in character_data.pl_collection.npc_socks:
                                for socks in character_data.pl_collection.npc_socks[npc_id]:
                                    collection_text += f" {socks}"
                                    self.sock_count += 1
                            collection_text += f"\n"
                collection_text += f"\n当前共{self.sock_count}双\n"


            collection_draw.text = collection_text
            collection_draw.width = self.width
            collection_draw.draw()


            return_list.extend(handle_panel.return_list)
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break


    def change_panel(self, collection_type: str):
        """
        切换当前面板显示
        Keyword arguments:
        collection_type -- 要切换的面板类型
        """

        self.now_panel = collection_type

    def get_bonus(self, bonus_id: int):
        """
        获得解锁奖励
        Keyword arguments:
        bonus_id -- 奖励编号
        """
        character_data: game_type.Character = cache.character_data[0]
        bonus_data = game_config.config_collection_bonus_data[bonus_id]
        bonus_flag = False

        # 比对相应的收集物数量，判断是否解锁成功
        if bonus_data.type == "信物":
            if self.token_count >= bonus_data.count or cache.debug_mode:
                character_data.pl_collection.collection_bonus[bonus_id] = True
                bonus_flag = True
        if bonus_data.type == "内裤":
            if self.pan_count >= bonus_data.count or cache.debug_mode:
                character_data.pl_collection.collection_bonus[bonus_id] = True
                bonus_flag = True
        if bonus_data.type == "袜子":
            if self.sock_count >= bonus_data.count or cache.debug_mode:
                character_data.pl_collection.collection_bonus[bonus_id] = True
                bonus_flag = True

        # 获得素质类型的当场触发
        if bonus_flag:
            if bonus_id == 1:
                character_data.talent[304] = 1
            if bonus_id == 2:
                character_data.talent[305] = 1
            if bonus_id == 3:
                character_data.talent[306] = 1
            elif bonus_id == 101:
                character_data.talent[307] = 1

        # 输出提示信息
        info_draw = draw.NormalDraw()
        if bonus_flag:
            info_draw.text = "\n  解锁成功\n"
        else:
            info_draw.text = "\n  未满足条件，解锁失败\n"
        info_draw.width = self.width
        info_draw.draw()



class collection_Draw:
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

