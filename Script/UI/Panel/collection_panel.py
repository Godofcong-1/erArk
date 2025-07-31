from typing import List
from types import FunctionType
from Script.Core import cache_control, game_type, get_text, flow_handle, constant
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

def collapse_collection():
    """
    收起收集品
    """

    character_data: game_type.Character = cache.character_data[0]

    now_draw = draw.WaitDraw()
    now_draw.width = window_width
    now_draw.text = _("\n开始摆放藏品\n")
    now_draw.draw()
    now_draw = draw.NormalDraw()
    now_draw.width = window_width
    now_draw_text = ""

    # 内裤
    if len(character_data.pl_collection.npc_panties_tem):
        for npc_id in character_data.pl_collection.npc_panties_tem:
            if npc_id == 0:
                continue
            for pan_id in character_data.pl_collection.npc_panties_tem[npc_id]:
                # 如果该内裤不存在，则跳过
                if pan_id not in game_config.config_clothing_tem:
                    continue
                pan_name = game_config.config_clothing_tem[pan_id].name
                """
                # 如果已经重复持有，则进行提示
                # if pan_name in character_data.pl_collection.npc_panties[npc_id]:
                #     now_draw.text = _("\n已持有藏品：{0}的{1}").format(cache.character_data[npc_id].name, pan_name)
                # else:
                """
                # 改为可以重复持有
                character_data.pl_collection.npc_panties[npc_id].append(pan_name)
                now_draw_text += _("增加了藏品：{0}的{1}\n").format(cache.character_data[npc_id].name, pan_name)
                now_draw.draw()
        # 最后清空
        character_data.pl_collection.npc_panties_tem.clear()

    # 袜子
    if len(character_data.pl_collection.npc_socks_tem):
        for npc_id in character_data.pl_collection.npc_socks_tem:
            if npc_id == 0:
                continue
            for socks_id in character_data.pl_collection.npc_socks_tem[npc_id]:
                # 如果该袜子不存在，则跳过
                if socks_id not in game_config.config_clothing_tem:
                    continue
                socks_name = game_config.config_clothing_tem[socks_id].name
                """
                # 如果已经重复持有，则进行提示
                if socks_name in character_data.pl_collection.npc_socks[npc_id]:
                    now_draw.text = _("\n已持有藏品：{0}的{1}").format(cache.character_data[npc_id].name, socks_name)
                else:
                """
                # 改为可以重复持有
                character_data.pl_collection.npc_socks[npc_id].append(socks_name)
                now_draw_text += _("增加了藏品：{0}的{1}\n").format(cache.character_data[npc_id].name, socks_name)
                now_draw.draw()
        # 装完了之后清空
        character_data.pl_collection.npc_socks_tem.clear()

    now_draw.text = now_draw_text
    now_draw.draw()
    now_draw = draw.WaitDraw()
    now_draw.width = window_width
    now_draw.text = _("\n摆放藏品结束\n")
    now_draw.draw()


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

        pl_character_data: game_type.Character = cache.character_data[0]
        refresh_all_bonus()

        title_text = _("收藏品")
        collection_type_list = [_("信物"), _("内裤"), _("袜子")]

        title_draw = draw.TitleLineDraw(title_text, self.width)
        handle_token_panel = panel.PageHandlePanel([], Token_Draw, 10, 1, self.width, 1, 1, 0)
        handle_pan_panel = panel.PageHandlePanel([], Pan_Draw, 10, 1, self.width, 1, 1, 0)
        handle_socks_panel = panel.PageHandlePanel([], Socks_Draw, 10, 1, self.width, 1, 1, 0)
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
                un_lock_flag = not (cid in [1,101,201] or pl_character_data.pl_collection.collection_bonus[cid - 1])

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
                    if pl_character_data.pl_collection.collection_bonus[cid] or un_lock_flag:
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
                token_chara_list = []
                for npc_id in cache.npc_id_got:
                    if npc_id == 0:
                        continue
                    if pl_character_data.pl_collection.token_list[npc_id]:
                        token_chara_list.append(npc_id)
                        self.token_count += 1
                # 更新当前面板，并清空其他面板
                handle_token_panel.text_list = token_chara_list
                handle_token_panel.update()
                handle_pan_panel.text_list = []
                handle_socks_panel.text_list = []
                collection_text += _("\n当前共{0}个\n").format(self.token_count)

            elif self.now_panel == _("内裤"):

                # 统计当前内裤收集数
                self.pan_count = 0
                pan_chara_list = []

                for npc_id in cache.npc_id_got:
                    if npc_id == 0:
                        continue
                    # 如果有收集到该角色的处子胖次或其他普通胖次
                    if pl_character_data.pl_collection.first_panties[npc_id] != "" or len(pl_character_data.pl_collection.npc_panties[npc_id]):
                        pan_chara_list.append(npc_id)
                        # 处子血胖次
                        if npc_id in pl_character_data.pl_collection.first_panties and pl_character_data.pl_collection.first_panties[npc_id] != "":
                            self.pan_count += 1
                        if npc_id in pl_character_data.pl_collection.npc_panties:
                            # 统计当前角色的普通胖次数量
                            self.pan_count += len(pl_character_data.pl_collection.npc_panties[npc_id])

                # 更新当前面板，并清空其他面板
                handle_pan_panel.text_list = pan_chara_list
                handle_pan_panel.update()
                handle_token_panel.text_list = []
                handle_socks_panel.text_list = []
                collection_text += _("\n当前共{0}条\n").format(self.pan_count)


            elif self.now_panel == _("袜子"):

                # 统计当前袜子收集数
                self.sock_count = 0
                socks_chara_list = []

                for npc_id in cache.npc_id_got:
                    if npc_id == 0:
                        continue
                    if len(pl_character_data.pl_collection.npc_socks[npc_id]):
                        socks_chara_list.append(npc_id)
                        if npc_id in pl_character_data.pl_collection.npc_socks:
                            # 统计当前角色的袜子数量
                            self.sock_count += len(pl_character_data.pl_collection.npc_socks[npc_id])
                # 更新当前面板，并清空其他面板
                handle_socks_panel.text_list = socks_chara_list
                handle_socks_panel.update()
                handle_token_panel.text_list = []
                handle_pan_panel.text_list = []
                collection_text += _("\n当前共{0}双\n").format(self.sock_count)


            collection_draw.text = collection_text
            collection_draw.width = self.width
            collection_draw.draw()

            # 绘制信物、内裤、袜子信息
            if len(handle_token_panel.text_list):
                handle_token_panel.draw()
            if len(handle_pan_panel.text_list):
                handle_pan_panel.draw()
            if len(handle_socks_panel.text_list):
                handle_socks_panel.draw()

            return_list.extend(handle_token_panel.return_list)
            return_list.extend(handle_pan_panel.return_list)
            return_list.extend(handle_socks_panel.return_list)
            line_feed.draw()
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


class Token_Draw:
    """
    信物绘制对象
    Keyword arguments:
    text -- 道具id
    width -- 最大宽度
    """

    def __init__(self, character_id: int, width: int, is_button: bool, num_button: bool, button_id: int):
        """初始化绘制对象"""
        self.character_id: int = character_id
        """ 角色id """
        self.draw_text: str = ""
        """ 绘制文本 """
        self.width: int = width
        """ 最大宽度 """
        self.is_button: bool = is_button
        """ 是否为按钮 """
        self.num_button: bool = num_button
        """ 是否为数字按钮 """
        self.button_id: int = button_id
        """ 按钮编号 """

        token_draw = draw.NormalDraw()
        npc_name = cache.character_data[self.character_id].name
        npc_token = cache.character_data[self.character_id].token_text
        token_text = f"\n  {npc_name}：{npc_token}"
        token_draw.text = token_text
        self.draw_text = ""
        self.now_draw = token_draw
        """ 绘制的对象 """

    def draw(self):
        """绘制对象"""
        self.now_draw.draw()


class Pan_Draw:
    """
    内裤绘制对象
    Keyword arguments:
    text -- 道具id
    width -- 最大宽度
    """

    def __init__(self, character_id: int, width: int, is_button: bool, num_button: bool, button_id: int):
        """初始化绘制对象"""
        self.character_id: int = character_id
        """ 角色id """
        self.draw_text: str = ""
        """ 绘制文本 """
        self.width: int = width
        """ 最大宽度 """
        self.is_button: bool = is_button
        """ 是否为按钮 """
        self.num_button: bool = num_button
        """ 是否为数字按钮 """
        self.button_id: int = button_id
        """ 按钮编号 """

        pl_character_data: game_type.Character = cache.character_data[0]
        npc_name = cache.character_data[self.character_id].name

        pan_text = f"\n  {npc_name}："
        # 处子血胖次
        if self.character_id in pl_character_data.pl_collection.first_panties and pl_character_data.pl_collection.first_panties[self.character_id] != "":
            pan_text += f" {pl_character_data.pl_collection.first_panties[self.character_id]}"
        # 常规胖次
        if self.character_id in pl_character_data.pl_collection.npc_panties:
            # 通过字典统计，输出每种内裤的数量
            pan_counts = {}
            for pan in pl_character_data.pl_collection.npc_panties[self.character_id]:
                pan_counts[pan] = pan_counts.get(pan, 0) + 1
            
            for pan, count in pan_counts.items():
                pan_text += f" {pan}({count})"

        # 创建绘制对象
        pan_draw = draw.NormalDraw()
        pan_draw.text = pan_text
        self.draw_text = ""
        self.now_draw = pan_draw
        """ 绘制的对象 """

    def draw(self):
        """绘制对象"""
        self.now_draw.draw()


class Socks_Draw:
    """
    袜子绘制对象
    Keyword arguments:
    text -- 道具id
    width -- 最大宽度
    """

    def __init__(self, character_id: int, width: int, is_button: bool, num_button: bool, button_id: int):
        """初始化绘制对象"""
        self.character_id: int = character_id
        """ 角色id """
        self.draw_text: str = ""
        """ 绘制文本 """
        self.width: int = width
        """ 最大宽度 """
        self.is_button: bool = is_button
        """ 是否为按钮 """
        self.num_button: bool = num_button
        """ 是否为数字按钮 """
        self.button_id: int = button_id
        """ 按钮编号 """

        pl_character_data: game_type.Character = cache.character_data[0]
        npc_name = cache.character_data[self.character_id].name

        socks_text = f"\n  {npc_name}："
        # 常规胖次
        if self.character_id in pl_character_data.pl_collection.npc_socks:
            # 通过字典统计，输出每种袜子的数量
            sock_counts = {}
            for sock in pl_character_data.pl_collection.npc_socks[self.character_id]:
                sock_counts[sock] = sock_counts.get(sock, 0) + 1
            for sock, count in sock_counts.items():
                socks_text += f" {sock}({count})"

        # 创建绘制对象
        socks_draw = draw.NormalDraw()
        socks_draw.text = socks_text
        self.draw_text = ""
        self.now_draw = socks_draw
        """ 绘制的对象 """

    def draw(self):
        """绘制对象"""
        self.now_draw.draw()

