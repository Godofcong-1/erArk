from typing import List
from types import FunctionType
from Script.Core import cache_control, game_type, get_text, flow_handle, constant
from Script.Design import handle_talent, map_handle
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

unconscious_list = [_("无"),_("睡眠"),_("醉酒"),_("时停"),_("平然催眠"),_("空气催眠"),_("体控催眠"),_("心控催眠")]
""" 无意识状态列表 """

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
        # 空气催眠
        if now_hypnosis_type == 2:
            # 限制为需要锁门的地点，并强制锁门
            now_position = pl_character_data.position
            now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
            now_scene_data = cache.scene_data[now_scene_str]
            if now_scene_data.close_type != 1:
                now_draw = draw.WaitDraw()
                draw_text = _("\n当前地点不能锁门，无法进行空气催眠\n")
                now_draw.text = draw_text
                now_draw.draw()
                return 0
            elif cache.scene_data[now_scene_str].close_flag == 0:
                cache.scene_data[now_scene_str].close_flag = now_scene_data.close_type
                now_draw = draw.WaitDraw()
                draw_text = _("\n为了防止有人打扰，将门锁上了\n")
                now_draw.text = draw_text
                now_draw.draw()
            # 更新记录当前地点
            pl_character_data.pl_ability.air_hypnosis_position = pl_character_data.position
        if now_hypnosis_type != 0:
            character_data.sp_flag.unconscious_h = now_hypnosis_type + 3
        else:
            character_data.sp_flag.unconscious_h = 0
        # print(f"debug {character_data.name} unconscious_h = {character_data.sp_flag.unconscious_h}")
        # 进行素质获得检测
        handle_talent.npc_gain_hypnosis_talent(character_id)
        return 1
    # 未完成催眠
    else:
        return 0


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


        title_text = _("源石技艺")
        title_draw = draw.TitleLineDraw(title_text, self.width)
        while 1:
            return_list = []
            title_draw.draw()
            # line = draw.LineDraw("-", window_width)
            # line.draw()
            pl_character_data: game_type.Character = cache.character_data[0]
            target_data: game_type.Character = cache.character_data[pl_character_data.target_character_id]
            cinfo_draw = draw.NormalDraw()
            info_text = _("\n要使用哪一个源石技艺呢？\n")
            cinfo_draw.text = info_text
            cinfo_draw.draw()

            # 选项面板
            # button_all_draw = panel.LeftDrawTextListPanel()

            DNT_Panel = Down_Negative_Talent_Panel(self.width)
            button1_text = _("[001]消除负面刻印")
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
                button2_text = _("[002]时间停止(未实装)")
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
                button3_text = _("[003]催眠")
                now_type_id = self.pl_character_data.pl_ability.hypnosis_type
                now_type_name = game_config.config_hypnosis_type[now_type_id].name
                button3_text += _("（当前默认催眠类型：{0}）").format(now_type_name)
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
                button4_text = _("[004]自我强化(未实装)")
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
                button5_text = _("[005]激素系能力：")
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
                button6_text = _("[006]视觉系能力：")
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
                button6_text += _("({0}理智/h)").format(count*5)
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
                button7_text = _("[007]触觉系能力(未实装)")
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
                button11_text = _("[011]能力获得与升级")
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
        now_draw.text = _("\n暂未实装\n")
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
                info_text += _("\n○进行催眠时会消耗理智，催眠结束后会自动合理化催眠过程中的记忆，未被催眠的干员也不会对催眠中的行为起疑\n")
                info_text += _("\n催眠系能力：\n")
                # 催眠能力
                info_draw.text = _(info_text)
                info_draw.draw()
                for cid in game_config.config_hypnosis_talent_of_pl:
                    hypnosis_data = game_config.config_hypnosis_talent_of_pl[cid]
                    talent_id = hypnosis_data.hypnosis_talent_id
                    max_degree = hypnosis_data.max_hypnosis_degree
                    talent_name = game_config.config_talent[talent_id].name
                    talent_info = game_config.config_talent[talent_id].info
                    draw_text = _("  {0}(最高催眠深度{1}%)：{2}\n").format(talent_name, max_degree, talent_info)
                    now_draw = draw.NormalDraw()
                    if not self.pl_character_data.talent[talent_id]:
                        draw_text = _("  {0}(未解锁)：{1}\n").format(talent_name, talent_info)
                        now_draw.style = "deep_gray"
                    now_draw.text = _(draw_text)
                    now_draw.draw()
                # 催眠类型
                info_text = _("\n催眠类型：\n")
                info_draw.text = _(info_text)
                info_draw.draw()
                for cid in game_config.config_hypnosis_type:
                    hypnosis_type_data = game_config.config_hypnosis_type[cid]
                    draw_text = f"  [{hypnosis_type_data.name}]"
                    draw_text += _("(需要[{0}]，且催眠深度达到{1}%)").format(game_config.config_talent[hypnosis_type_data.talent_id].name, hypnosis_type_data.hypnosis_degree)
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
                    info_text = _("\n激素系能力（不消耗理智）：\n")
                # 视觉系
                elif ability_type == 6:
                    talent_id_list = [307,308,309]
                    info_text = _("\n视觉系能力（每级消耗5理智/h）：\n")
                info_draw.text = _(info_text)
                info_draw.draw()
                # 遍历输出该能力的全素质
                for talent_id in talent_id_list:
                    talent_name = game_config.config_talent[talent_id].name
                    talent_info = game_config.config_talent[talent_id].info
                    draw_text = f"  {talent_name}：{talent_info}\n"
                    now_draw = draw.NormalDraw()
                    if not self.pl_character_data.talent[talent_id]:
                        draw_text = _("  {0}(未解锁)：{1}\n").format(talent_name, talent_info)
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
            info_text += _("\n能力可以直接消耗至纯源石或满足特定条件解锁，当前至纯源石：{0}\n").format(cache.rhodes_island.materials_resouce[3])
            info_text += _("\n当前可以获得/升级的能力有：\n\n")
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
                # 通用的源石获得方式，花费为10的cost次方
                money_cost = 10 ** (talent_of_arts_data.level - 1)
                if cache.rhodes_island.materials_resouce[3] < money_cost:
                    now_draw = draw.NormalDraw()
                    draw_text = _("  {0}({1}至纯源石-当前源石不足)：{2}\n").format(talent_name, money_cost, talent_info)
                    now_draw.text = _(draw_text)
                    now_draw.style = "deep_gray"
                    now_draw.draw()
                elif talent_of_arts_data.todo:
                    now_draw = draw.NormalDraw()
                    draw_text = _("  {0}(未实装)：{1}\n").format(talent_name, talent_info)
                    now_draw.text = _(draw_text)
                    now_draw.style = "deep_gray"
                    now_draw.draw()
                else:
                    draw_text = _("  {0}( {1} 至纯源石)：{2}").format(talent_name, money_cost, talent_info)
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
                # 每个技能树单独的获得方式
                # 催眠系
                if talent_id in game_config.config_hypnosis_talent_of_pl:
                    up_data = game_config.config_hypnosis_talent_of_pl[talent_id]
                    need_exp = up_data.pl_experience
                    now_exp = self.pl_character_data.experience[122]
                    need_degree = up_data.npc_hypnosis_degree
                    now_degree = 0
                    # 计算全获得干员的催眠深度
                    for chara_id in cache.npc_id_got:
                        character_data = cache.character_data[chara_id]
                        now_degree += character_data.hypnosis.hypnosis_degree
                    # 绘制
                    draw_text = f"  {talent_name}"
                    if up_data.todo:
                        draw_text += _("(未实装)")
                    draw_text += _("：需要博士催眠经验≥{0}（当前{1}），需要全干员总催眠深度≥{2}%（当前{3}%）").format(need_exp, now_exp, need_degree, now_degree)
                    # 可以解锁则绘制按钮
                    if not up_data.todo and now_exp >= need_exp and now_degree >= need_degree:
                        now_draw = draw.LeftButton(
                            _(draw_text),
                            _(str(cid) + "1"),
                            window_width,
                            cmd_func=self.gain_and_upgrade_ability_which,
                            args=(cid,True),
                            )
                        return_list.append(now_draw.return_text)
                        now_draw.draw()
                    # 不可解锁则绘制灰色文本
                    else:
                        now_draw = draw.NormalDraw()
                        now_draw.text = _(draw_text)
                        now_draw.style = "deep_gray"
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

    def gain_and_upgrade_ability_which(self, cid, no_cost_flag = False):
        """获得或升级能力"""
        talent_of_arts_data = game_config.config_talent_of_arts[cid]
        talent_id = talent_of_arts_data.talent_id
        talent_name = game_config.config_talent[talent_id].name
        # 花费为10的cost次方
        money_cost = 10 ** (talent_of_arts_data.level - 1)
        # 不消耗直接获得或升级
        if no_cost_flag:
            pass
        else:
            # 花费大于当前拥有的至纯源石则返回
            if cache.rhodes_island.materials_resouce[3] < money_cost:
                return
            cache.rhodes_island.materials_resouce[3] -= money_cost
        # 升级或获得能力
        self.pl_character_data.talent[talent_id] = 1
        info_text = _("\n习得了{0}\n").format(talent_name)
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

        title_text = _("降低负面素质")
        title_draw = draw.TitleLineDraw(title_text, self.width)
        self.ability_id_list = [15,17,18]

        while 1:
            return_list = []
            # title_draw.draw()

            # 输出提示信息
            info_draw = draw.NormalDraw()
            info_text = _("\n当前拥有苦痛刻印、反发刻印或恐怖刻印的角色有：\n\n")
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
                info_text = _("  没有符合条件的角色\n")
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
            info_text = _("\n要降低[{0}]的哪个刻印呢？(需要消耗该角色已收藏至藏品馆的5条内裤，当前共{1}条，优先消耗重复款式)\n\n").format(name, len(panties_data))
            if cache.debug_mode:
                info_text += _("当前为debug模式，不需要消耗内裤\n\n")
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
        if len(pl_character_data.pl_collection.npc_panties[self.chara_id]) >= 5 or cache.debug_mode:
            # debug模式下不消耗内裤
            if not cache.debug_mode:

                # 先统计每种内裤的数量
                pan_counts = {}
                for pan in pl_character_data.pl_collection.npc_panties[self.chara_id]:
                    pan_counts[pan] = pan_counts.get(pan, 0) + 1
                # 遍历全部内裤，优先删除重复款式的内裤，如果删除的数量不够5个，则从前往后删除
                pop_pan_count = 0
                for pan, count in pan_counts.items():
                    # 优先删除重复款式的内裤
                    if count > 1:
                        remove_count = min(count - 1, 5 - pop_pan_count)
                        for tem in range(remove_count):
                            pl_character_data.pl_collection.npc_panties[self.chara_id].remove(pan)
                        pop_pan_count += remove_count
                        if pop_pan_count >= 5:
                            break
                # 从前往后删除
                while pop_pan_count < 5:
                    if pop_pan_count < 5:
                        pl_character_data.pl_collection.npc_panties[self.chara_id].pop(0)
                        pop_pan_count += 1

            # 降低刻印
            character_data.ability[ability_id] -= 1
            # 也降低刻印对应的主状态值
            if ability_id == 15:
                character_data.status_data[17] = 0
            elif ability_id == 17:
                character_data.status_data[18] = 0
            elif ability_id == 18:
                character_data.status_data[20] = 0
            info_text = _("  随着一阵火焰，5条内裤化为一缕青烟，消散在空中\n")
            info_text += _("  {0}感觉心里轻松了很多，对{1}的印象有些改观了，{2}下降到了{3}级\n").format(character_data.name, pl_character_data.name, game_config.config_ability[ability_id].name, character_data.ability[ability_id])
        else:
            info_text = _("  内裤数量不足\n")
        info_draw.text = info_text
        info_draw.draw()
        line = draw.LineDraw("-", self.width)
        line.draw()


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

        title_text = _("选择催眠类型")
        title_draw = draw.TitleLineDraw(title_text, self.width)
        while 1:
            return_list = []
            title_draw.draw()
            pl_character_data: game_type.Character = cache.character_data[0]
            cinfo_draw = draw.NormalDraw()
            info_text = _("\n要使用哪一种催眠类型呢？\n")
            cinfo_draw.text = info_text
            cinfo_draw.draw()

            for cid in game_config.config_hypnosis_type:
                # 去掉手动选择
                if cid == 0:
                    continue
                hypnosis_type_data = game_config.config_hypnosis_type[cid]
                draw_text = f"  [{hypnosis_type_data.name}]"
                draw_text += _("(需要[{0}]，且催眠深度达到{1}%)").format(game_config.config_talent[hypnosis_type_data.talent_id].name, hypnosis_type_data.hypnosis_degree)
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


class Chose_Roleplay_Type_Panel:
    """
    用于选择心控催眠-角色扮演的面板对象
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

        title_text = _("选择角色扮演类型")
        title_draw = draw.TitleLineDraw(title_text, self.width)
        while 1:
            return_list = []
            title_draw.draw()
            pl_character_data: game_type.Character = cache.character_data[0]
            target_data: game_type.Character = cache.character_data[pl_character_data.target_character_id]
            info_draw = draw.NormalDraw()
            info_text = _("\n○被催眠后会完全带入对应的角色或场景，直到催眠解除为止\n")
            info_text += _("\n  要催眠为哪一种角色扮演呢？")
            info_text += _("（当前为：")

            if target_data.hypnosis.roleplay == 0:
                info_text += _("无）\n")
            else:
                info_text += _("{0}）\n").format(game_config.config_roleplay[target_data.hypnosis.roleplay].name)
            info_draw.text = info_text
            info_draw.draw()
            line_feed.draw()

            # 遍历角色扮演数据库，输出按钮
            for cid in game_config.config_roleplay:
                if cid == 0:
                    continue
                roleplay_data = game_config.config_roleplay[cid]
                draw_text = f"[{cid}]{roleplay_data.name}"
                button_draw = draw.LeftButton(
                    _(draw_text),
                    _(roleplay_data.name),
                    window_width,
                    cmd_func=self.choose_this_type,
                    args=(cid,),
                )
                return_list.append(button_draw.return_text)
                button_draw.draw()
                line_feed.draw()

            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn in return_list:
                break

    def choose_this_type(self, cid):
        """选择该类型"""
        pl_character_data: game_type.Character = cache.character_data[0]
        target_data: game_type.Character = cache.character_data[pl_character_data.target_character_id]
        target_data.hypnosis.roleplay = cid

        # 绘制提示信息
        info_draw = draw.WaitDraw()
        info_draw.style = "gold_enrod"
        info_text = _("\n{0}被催眠了，开始进行{1}的扮演\n\n").format(target_data.name, game_config.config_roleplay[cid].name)
        info_draw.text = info_text
        info_draw.draw()
