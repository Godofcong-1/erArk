from typing import List
from types import FunctionType
from Script.Core import cache_control, game_type, get_text, flow_handle, constant
from Script.Design import handle_talent
from Script.UI.Moudle import draw
from Script.Config import game_config, normal_config
import random

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

def evaluate_hypnosis_completion(character_id: int):
    """
    判断与结算催眠完成\n
    Keyword arguments:\n
    character_id -- 角色id\n
    Return arguments:\n
    int -- 1完成，0未完成\n
    """
    pl_character_data: game_type.Character = cache.character_data[0]
    character_data: game_type.Character = cache.character_data[character_id]
    # 计算催眠完成度
    now_hypnosis_type = pl_character_data.pl_ability.hypnosis_type
    hypnosis_degree_need = game_config.config_hypnosis_type[now_hypnosis_type].hypnosis_degree
    # 催眠完成，开始结算
    if character_data.hypnosis.hypnosis_degree >= hypnosis_degree_need:
        # 如果是手动选择，则先进入选择面板
        if now_hypnosis_type == 0:
            chose_hypnosis_type_panel = Chose_Hypnosis_Type_Panel(window_width)
            chose_hypnosis_type_panel.draw()
            now_hypnosis_type = pl_character_data.pl_ability.hypnosis_type
        character_data.sp_flag.unconscious_h = now_hypnosis_type + 3
        # print(f"debug {character_data.name} unconscious_h = {character_data.sp_flag.unconscious_h}")
        # 进行素质获得检测
        handle_talent.npc_gain_hypnosis_talent(character_id)
        return 1
    # 未完成催眠
    else:
        return 0


class Chose_Hypnosis_Type_Panel:
    """
    用于选择催眠类型的面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """

    def draw(self):
        """绘制对象"""

        title_text = "选择催眠类型"
        title_draw = draw.TitleLineDraw(title_text, self.width)
        while 1:
            return_list = []
            title_draw.draw()
            pl_character_data: game_type.Character = cache.character_data[0]
            cinfo_draw = draw.NormalDraw()
            info_text = f"\n要使用哪一种催眠类型呢？\n"
            cinfo_draw.text = info_text
            cinfo_draw.draw()

            for cid in game_config.config_hypnosis_type:
                # 去掉手动选择
                if cid == 0:
                    continue
                hypnosis_type_data = game_config.config_hypnosis_type[cid]
                draw_text = f"  [{hypnosis_type_data.name}]"
                draw_text += f"(需要[{game_config.config_talent[hypnosis_type_data.talent_id].name}]，且催眠深度达到{hypnosis_type_data.hypnosis_degree}%)"
                draw_text += f"：{hypnosis_type_data.introduce}"
                # 已解锁则绘制按钮
                if pl_character_data.talent[hypnosis_type_data.talent_id]:
                    button_draw = draw.LeftButton(
                        _(draw_text),
                        _(hypnosis_type_data.name),
                        window_width,
                        cmd_func=self.ability_switch,
                        args=(cid,),
                    )
                    return_list.append(button_draw.return_text)
                    button_draw.draw()
                    line_feed.draw()
                # 未解锁则绘制灰色文本
                else:
                    now_draw = draw.NormalDraw()
                    draw_text += f"\n"
                    now_draw.text = _(draw_text)
                    now_draw.style = "deep_gray"
                    now_draw.draw()
            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn in return_list:
                break

    def ability_switch(self, hypnosis_type_cid):
        """能力开关"""
        pl_character_data: game_type.Character = cache.character_data[0]
        pl_character_data.pl_ability.hypnosis_type = hypnosis_type_cid


class Originium_Arts_Panel:
    """
    用于源石技艺的面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        # self.now_panel = _("源石技艺")
        # """ 当前绘制的页面 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """
        self.pl_character_data = cache.character_data[0]
        """ 玩家的属性 """

    def draw(self):
        """绘制对象"""


        title_text = "源石技艺"
        title_draw = draw.TitleLineDraw(title_text, self.width)
        while 1:
            return_list = []
            title_draw.draw()
            # line = draw.LineDraw("-", window_width)
            # line.draw()
            pl_character_data: game_type.Character = cache.character_data[0]
            target_data: game_type.Character = cache.character_data[pl_character_data.target_character_id]
            cinfo_draw = draw.NormalDraw()
            info_text = f"\n要使用哪一个源石技艺呢？\n"
            cinfo_draw.text = info_text
            cinfo_draw.draw()

            # 选项面板
            # button_all_draw = panel.LeftDrawTextListPanel()

            DNT_Panel = Down_Negative_Talent_Panel(self.width)
            button1_text = f"[001]消除负面刻印"
            button1_draw = draw.LeftButton(
                _(button1_text),
                _("1"),
                window_width,
                cmd_func=DNT_Panel.draw
                )
            line_feed.draw()
            button1_draw.draw()
            return_list.append(button1_draw.return_text)

            if 0:
                button2_text = f"[002]时间停止(未实装)"
                button2_draw = draw.LeftButton(
                    _(button2_text),
                    _("2"),
                    window_width,
                    cmd_func=self.to_do,
                    args=(),
                    )
                line_feed.draw()
                button2_draw.draw()
                return_list.append(button2_draw.return_text)

            if handle_talent.have_hypnosis_talent():
                button3_text = f"[003]催眠"
                now_type_id = self.pl_character_data.pl_ability.hypnosis_type
                now_type_name = game_config.config_hypnosis_type[now_type_id].name
                button3_text += f"（当前默认催眠类型：{now_type_name}）"
                button3_draw = draw.LeftButton(
                    _(button3_text),
                    _("3"),
                    window_width,
                    cmd_func=self.arts_show,
                    args=(3),
                    )
                line_feed.draw()
                button3_draw.draw()
                return_list.append(button3_draw.return_text)

            if 0:
                button4_text = f"[004]自我强化(未实装)"
                button4_draw = draw.LeftButton(
                    _(button4_text),
                    _("4"),
                    window_width,
                    cmd_func=self.to_do,
                    args=(),
                    )
                line_feed.draw()
                button4_draw.draw()
                return_list.append(button4_draw.return_text)

            if handle_talent.have_hormone_talent():
                button5_text = f"[005]激素系能力："
                # 输出当前开启的视觉系能力
                talent_id_list = [304,305,309]
                count = 0
                for talent_id in talent_id_list:
                    if not self.pl_character_data.talent[talent_id]:
                        continue
                    talent_name = game_config.config_talent[talent_id].name
                    if talent_id != 304:
                        button5_text += "+"
                    button5_text += f"{talent_name}"
                    count += 1
                button5_draw = draw.LeftButton(
                    _(button5_text),
                    _("5"),
                    window_width,
                    cmd_func=self.arts_show,
                    args=(5),
                    )
                line_feed.draw()
                button5_draw.draw()
                return_list.append(button5_draw.return_text)

            if handle_talent.have_visual_talent():
                button6_text = f"[006]视觉系能力："
                # 输出当前开启的视觉系能力
                talent_id_list = [307,308,309]
                count = 0
                for talent_id in talent_id_list:
                    if not self.pl_character_data.talent[talent_id]:
                        continue
                    talent_name = game_config.config_talent[talent_id].name
                    if talent_id != 307:
                        button6_text += "+"
                    button6_text += f"{talent_name}"
                    count += 1
                # 输出理智消耗
                button6_text += f"({count*5}理智/h)"
                button6_draw = draw.LeftButton(
                    _(button6_text),
                    _("6"),
                    window_width,
                    cmd_func=self.arts_show,
                    args=(6),
                    )
                line_feed.draw()
                button6_draw.draw()
                return_list.append(button6_draw.return_text)

            if handle_talent.have_tactile_talent():
                button7_text = f"[007]触觉系能力(未实装)"
                button7_draw = draw.LeftButton(
                    _(button7_text),
                    _("7"),
                    window_width,
                    cmd_func=self.to_do,
                    args=(7),
                    )
                line_feed.draw()
                button7_draw.draw()
                return_list.append(button7_draw.return_text)

            if 1:
                button11_text = f"[011]能力获得与升级"
                button11_draw = draw.LeftButton(
                    _(button11_text),
                    _("11"),
                    window_width,
                    cmd_func=self.gain_and_upgrade_ability,
                    args=(),
                    )
                line_feed.draw()
                button11_draw.draw()
                return_list.append(button11_draw.return_text)

            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def to_do(self, n):
        """暂未实装"""

        now_draw = draw.WaitDraw()
        now_draw.width = window_width
        now_draw.text = _(f"\n暂未实装\n")
        now_draw.draw()

    def arts_show(self, ability_type):
        """源石技艺展示"""
        line_draw = draw.LineDraw("-", self.width)
        line_draw.draw()
        while 1:
            return_list = []
            info_draw = draw.NormalDraw()
            info_text = ""
            # 催眠系
            if ability_type == 3:
                info_text = f"\n催眠系能力（在进行催眠时消耗理智）：\n"
                # 催眠能力
                info_draw.text = _(info_text)
                info_draw.draw()
                talent_and_degree_dict = {331:50,332:100,333:100,334:200}
                for talent_id in talent_and_degree_dict:
                    talent_name = game_config.config_talent[talent_id].name
                    talent_info = game_config.config_talent[talent_id].info
                    draw_text = f"  {talent_name}(最高催眠深度{talent_and_degree_dict[talent_id]}%)：{talent_info}\n"
                    now_draw = draw.NormalDraw()
                    if not self.pl_character_data.talent[talent_id]:
                        draw_text = f"  {talent_name}(未解锁)：{talent_info}\n"
                        now_draw.style = "deep_gray"
                    now_draw.text = _(draw_text)
                    now_draw.draw()
                # 催眠类型
                info_text = f"\n催眠类型：\n"
                info_draw.text = _(info_text)
                info_draw.draw()
                for cid in game_config.config_hypnosis_type:
                    hypnosis_type_data = game_config.config_hypnosis_type[cid]
                    draw_text = f"  [{hypnosis_type_data.name}]"
                    draw_text += f"(需要[{game_config.config_talent[hypnosis_type_data.talent_id].name}]，且催眠深度达到{hypnosis_type_data.hypnosis_degree}%)"
                    draw_text += f"：{hypnosis_type_data.introduce}"
                    # 已解锁则绘制按钮
                    if self.pl_character_data.talent[hypnosis_type_data.talent_id]:
                        button_draw = draw.LeftButton(
                            _(draw_text),
                            _(hypnosis_type_data.name),
                            window_width,
                            cmd_func=self.change_hypnosis_type,
                            args=(cid,),
                        )
                        return_list.append(button_draw.return_text)
                        button_draw.draw()
                        line_feed.draw()
                    # 未解锁则绘制灰色文本
                    else:
                        now_draw = draw.NormalDraw()
                        draw_text += f"\n"
                        now_draw.text = _(draw_text)
                        now_draw.style = "deep_gray"
                        now_draw.draw()
            else:
                # 激素系
                if ability_type == 5:
                    talent_id_list = [304,305,306]
                    info_text = f"\n激素系能力（不消耗理智）：\n"
                # 视觉系
                elif ability_type == 6:
                    talent_id_list = [307,308,309]
                    info_text = f"\n视觉系能力（每级消耗5理智/h）：\n"
                info_draw.text = _(info_text)
                info_draw.draw()
                # 遍历输出该能力的全素质
                for talent_id in talent_id_list:
                    talent_name = game_config.config_talent[talent_id].name
                    talent_info = game_config.config_talent[talent_id].info
                    draw_text = f"  {talent_name}：{talent_info}\n"
                    now_draw = draw.NormalDraw()
                    if not self.pl_character_data.talent[talent_id]:
                        draw_text = f"  {talent_name}(未解锁)：{talent_info}\n"
                        now_draw.style = "deep_gray"
                    now_draw.text = _(draw_text)
                    now_draw.draw()
            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn in return_list:
                break

    def gain_and_upgrade_ability(self):
        """能力获得与升级"""
        while 1:
            return_list = []
            line_draw = draw.LineDraw("-", self.width)
            line_draw.draw()
            info_draw = draw.NormalDraw()
            info_text = ""
            info_text += f"\n当前至纯源石：{cache.rhodes_island.materials_resouce[3]}\n"
            info_text += f"\n当前可以获得/升级的能力有：\n\n"
            info_draw.text = _(info_text)
            info_draw.draw()
            # 遍历输出该能力的全素质
            for cid in game_config.config_talent_of_arts:
                talent_of_arts_data = game_config.config_talent_of_arts[cid]
                # 检查是否已经获得
                if self.pl_character_data.talent[talent_of_arts_data.talent_id]:
                    continue
                # 检查是否有前置素质
                if talent_of_arts_data.need_id:
                    if not self.pl_character_data.talent[talent_of_arts_data.need_id]:
                        continue
                talent_id = talent_of_arts_data.talent_id
                talent_name = game_config.config_talent[talent_id].name
                talent_info = game_config.config_talent[talent_id].info
                # 花费为10的cost次方
                money_cost = 10 ** (talent_of_arts_data.level - 1)
                if cache.rhodes_island.materials_resouce[3] < money_cost:
                    now_draw = draw.NormalDraw()
                    draw_text = f"  {talent_name}({money_cost}至纯源石-当前源石不足)：{talent_info}\n"
                    now_draw.text = _(draw_text)
                    now_draw.style = "deep_gray"
                    now_draw.draw()
                elif talent_of_arts_data.todo:
                    now_draw = draw.NormalDraw()
                    draw_text = f"  {talent_name}(未实装)：{talent_info}\n"
                    now_draw.text = _(draw_text)
                    now_draw.style = "deep_gray"
                    now_draw.draw()
                else:
                    draw_text = f"  {talent_name}( {money_cost} 至纯源石)：{talent_info}"
                    now_draw = draw.LeftButton(
                        _(draw_text),
                        _(str(cid)),
                        window_width,
                        cmd_func=self.gain_and_upgrade_ability_which,
                        args=(cid,),
                        )
                    return_list.append(now_draw.return_text)
                    now_draw.draw()
                    line_feed.draw()
            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                break

    def change_hypnosis_type(self, hypnosis_type_cid):
        """改变当前的催眠类型"""
        self.pl_character_data.pl_ability.hypnosis_type = hypnosis_type_cid

    def gain_and_upgrade_ability_which(self, cid):
        """获得或升级能力"""
        talent_of_arts_data = game_config.config_talent_of_arts[cid]
        talent_id = talent_of_arts_data.talent_id
        talent_name = game_config.config_talent[talent_id].name
        # 花费为10的cost次方
        money_cost = 10 ** (talent_of_arts_data.level - 1)
        # 花费大于当前拥有的至纯源石则返回
        if cache.rhodes_island.materials_resouce[3] < money_cost:
            return
        # 花费至纯源石
        cache.rhodes_island.materials_resouce[3] -= money_cost
        # 升级或获得能力
        self.pl_character_data.talent[talent_id] = 1
        info_text = f"\n习得了{talent_name}\n"
        info_draw = draw.WaitDraw()
        info_draw.text = _(info_text)
        info_draw.draw()


class Down_Negative_Talent_Panel:
    """
    用于降低负面素质的面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """

    def draw(self):
        """绘制对象"""

        title_text = "降低负面素质"
        title_draw = draw.TitleLineDraw(title_text, self.width)
        self.ability_id_list = [17,18]

        while 1:
            return_list = []
            # title_draw.draw()

            # 输出提示信息
            info_draw = draw.NormalDraw()
            info_text = "\n当前拥有反发刻印或恐怖刻印的角色有：\n\n"
            info_draw.text = info_text
            info_draw.draw()

            chara_exist_flag = False

            # 遍历备选人物名字并输出按钮
            for chara_id in cache.npc_id_got:
                character_data = cache.character_data[chara_id]

                for ability_id in self.ability_id_list:
                    if character_data.ability[ability_id]:
                        chara_exist_flag = True
                        name = character_data.name
                        adv_id = character_data.adv
                        button_text = f"[{str(adv_id).rjust(4,'0')}]:{name} "

                        button_draw = draw.LeftButton(
                            _(button_text),
                            _(str(adv_id)),
                            self.width,
                            cmd_func=self.choice_down_which,
                            args=(chara_id,),
                            )
                        # print(f"debug button_draw.text = {button_draw.text},button_draw.normal_style = {button_draw.normal_style}")
                        return_list.append(button_draw.return_text)
                        button_draw.draw()
                        line_feed.draw()
                        break # 单角色满足条件则只出现一次

            if not chara_exist_flag:
                info_draw = draw.NormalDraw()
                info_text = "  没有符合条件的角色\n"
                info_draw.text = info_text
                info_draw.draw()

            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                break

    def choice_down_which(self, chara_id):
        """选择降低哪一个"""
        character_data = cache.character_data[chara_id]
        self.chara_id = chara_id
        name = character_data.name

        pl_character_data = cache.character_data[0]
        if self.chara_id not in pl_character_data.pl_collection.npc_panties:
            pl_character_data.pl_collection.npc_panties[self.chara_id] = []
        panties_data = pl_character_data.pl_collection.npc_panties[self.chara_id]


        while 1:
            return_list = []

            # 输出提示信息
            info_draw = draw.NormalDraw()
            info_text = f"\n要降低[{name}]的哪个刻印呢？(需要消耗5条内裤，当前共{len(panties_data)}条)\n\n"
            if cache.debug_mode:
                info_text += "当前为debug模式，不需要消耗内裤\n\n"
            info_draw.text = info_text
            info_draw.draw()

            for ability_id in self.ability_id_list:
                if character_data.ability[ability_id]:
                    ability_name = game_config.config_ability[ability_id].name
                    ability_lv = character_data.ability[ability_id]
                    button_text = f"  {ability_name}[lv{ability_lv}]"

                    button_draw = draw.LeftButton(
                        _(button_text),
                        _(str(ability_id)),
                        self.width,
                        cmd_func=self.settle_down,
                        args=(ability_id,),
                        )
                    # print(f"debug button_draw.text = {button_draw.text},button_draw.normal_style = {button_draw.normal_style}")
                    return_list.append(button_draw.return_text)
                    button_draw.draw()
                    line_feed.draw()

            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                break


    def settle_down(self, ability_id):
        """结算刻印降低"""
        info_draw = draw.NormalDraw()
        character_data = cache.character_data[self.chara_id]

        # 计算当前该角色的胖次数量，大于五则成功，不足则弹出失败提示
        pl_character_data = cache.character_data[0]
        panties_data = pl_character_data.pl_collection.npc_panties[self.chara_id]
        if len(panties_data) >= 5 or cache.debug_mode:
            if not cache.debug_mode:
                for i in range(5):
                    panties_data.pop()
            character_data.ability[ability_id] -= 1
            # 也降低刻印对应的主状态值
            if ability_id == 17:
                character_data.status_data[18] = 0
            elif ability_id == 18:
                character_data.status_data[20] = 0
            info_text = "  随着一阵火焰，5条内裤化为一缕青烟，消散在空中\n"
            info_text += f"  {character_data.name}感觉心里轻松了很多，对{pl_character_data.name}的印象有些改观了，{game_config.config_ability[ability_id].name}下降到了{character_data.ability[ability_id]}级\n"
        else:
            info_text = "  内裤数量不足\n"
        info_draw.text = info_text
        info_draw.draw()
        line = draw.LineDraw("-", self.width)
        line.draw()

