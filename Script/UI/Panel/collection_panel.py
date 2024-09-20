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

def refresh_all_bonus():
    """
    刷新所有未获得的解锁奖励
    """
    pl_character = cache.character_data[0]

    # 遍历全部收集奖励
    for bonus_id in game_config.config_collection_bonus_data:
        # 目前仅刷新前10个奖励
        if bonus_id >= 10:
            break
        bonus_data = game_config.config_collection_bonus_data[bonus_id]
        if pl_character.pl_collection.collection_bonus[bonus_id]:
            # 刷新信物的上限解锁奖励
            pl_character.pl_collection.eqip_token[0] = max(pl_character.pl_collection.eqip_token[0], bonus_data.effect_2)


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
        refresh_all_bonus()

        title_text = _("收藏品")
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
            bonus_text = _("\n收集解锁要素：")
            bonus_draw.text = bonus_text
            bonus_draw.width = self.width
            bonus_draw.draw()

            # print(f"debug character_data.pl_collection.collection_bonus = {character_data.pl_collection.collection_bonus}")

            # 遍历全部收集奖励
            for cid in game_config.config_collection_bonus_data:

                # 判断是否已经解锁前段奖励
                un_lock_flag = not (cid in [1,101,201] or character_data.pl_collection.collection_bonus[cid - 1])

                now_bonus = game_config.config_collection_bonus_data[cid]
                bonus_text = ""
                draw_flag = False

                # 创建一个映射字典
                bonus_type_text = {
                    _("信物"): _("个信物后，"),
                    _("内裤"): _("条内裤后，"),
                    _("袜子"): _("双袜子后，")
                }

                # 使用循环替代多个if语句
                for bonus_type, text in bonus_type_text.items():
                    if now_bonus.type == bonus_type and self.now_panel == bonus_type:
                        bonus_text = _("累积获得{0}{1}").format(str(now_bonus.count).rjust(3,' '), text)
                        draw_flag = True
                        break

                bonus_text += " ？？？" if un_lock_flag else f"{now_bonus.info}"

                # 仅绘制当前面板，且根据是否已解锁来判断是绘制文本还是按钮
                if draw_flag:
                    line_feed.draw()
                    if character_data.pl_collection.collection_bonus[cid] or un_lock_flag:
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
            if self.now_panel == _("信物"):
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
                collection_text += _("\n当前共{0}个\n").format(self.token_count)

            elif self.now_panel == _("内裤"):

                # 统计当前内裤收集数
                self.pan_count = 0

                for npc_id in cache.npc_id_got:
                    if npc_id != 0:

                        # 如果有收集到该角色的处子胖次或其他普通胖次则开始绘制
                        if character_data.pl_collection.first_panties[npc_id] != "" or len(character_data.pl_collection.npc_panties[npc_id]):

                            # 首先对列表进行排序
                            character_data.pl_collection.npc_panties[npc_id].sort()

                            npc_name = cache.character_data[npc_id].name
                            collection_text += f"\n  {npc_name}："
                            if npc_id in character_data.pl_collection.first_panties and character_data.pl_collection.first_panties[npc_id] != "":
                                collection_text += f" {character_data.pl_collection.first_panties[npc_id]}"
                                self.pan_count += 1
                            if npc_id in character_data.pl_collection.npc_panties:

                                # 统计当前角色的普通胖次数量
                                self.pan_count += len(character_data.pl_collection.npc_panties[npc_id])

                                # 通过字典统计，输出每种内裤的数量
                                pan_counts = {}
                                for pan in character_data.pl_collection.npc_panties[npc_id]:
                                    pan_counts[pan] = pan_counts.get(pan, 0) + 1
                                
                                for pan, count in pan_counts.items():
                                    collection_text += f" {pan}({count})"

                            collection_text += f"\n"
                collection_text += _("\n当前共{0}条\n").format(self.pan_count)



            elif self.now_panel == _("袜子"):

                # 统计当前袜子收集数
                self.sock_count = 0

                for npc_id in cache.npc_id_got:
                    if npc_id != 0:

                        if len(character_data.pl_collection.npc_socks[npc_id]):

                            # 首先对列表进行排序
                            character_data.pl_collection.npc_socks[npc_id].sort()

                            npc_name = cache.character_data[npc_id].name
                            collection_text += f"\n  {npc_name}："
                            if npc_id in character_data.pl_collection.npc_socks:

                                # 统计当前角色的袜子数量
                                self.sock_count += len(character_data.pl_collection.npc_socks[npc_id])

                                # 通过字典统计，输出每种袜子的数量
                                sock_counts = {}
                                for sock in character_data.pl_collection.npc_socks[npc_id]:
                                    sock_counts[sock] = sock_counts.get(sock, 0) + 1

                                for sock, count in sock_counts.items():
                                    collection_text += f" {sock}({count})"

                            collection_text += f"\n"
                collection_text += _("\n当前共{0}双\n").format(self.sock_count)


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
        originium_prime_flag = False
        token_flag = False

        # 比对相应的收集物数量，判断是否解锁成功
        if bonus_data.type == _("信物"):
            if self.token_count >= bonus_data.count or cache.debug_mode:
                character_data.pl_collection.collection_bonus[bonus_id] = True
                originium_prime_flag = True
                token_flag = True
        elif bonus_data.type == _("内裤"):
            if self.pan_count >= bonus_data.count or cache.debug_mode:
                character_data.pl_collection.collection_bonus[bonus_id] = True
                if bonus_id == 101:
                    originium_prime_flag = True
        elif bonus_data.type == _("袜子"):
            if self.sock_count >= bonus_data.count or cache.debug_mode:
                character_data.pl_collection.collection_bonus[bonus_id] = True
                if bonus_id == 201:
                    originium_prime_flag = True

        # 获得至纯源石
        if originium_prime_flag:
            cache.rhodes_island.materials_resouce[3] += bonus_data.effect_1
        # 解锁信物装备上限
        if token_flag:
            character_data.pl_collection.eqip_token[0] = max(character_data.pl_collection.eqip_token[0], bonus_data.effect_2)

        # 输出提示信息
        info_draw = draw.NormalDraw()
        if originium_prime_flag:
            info_draw.text = _("\n  解锁成功\n")
        else:
            info_draw.text = _("\n  未满足条件，解锁失败\n")
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

