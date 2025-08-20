from typing import List
from types import FunctionType
from Script.UI.Moudle import draw
from Script.Core import (
    cache_control,
    get_text,
    game_type,
    text_handle,
    constant,
)
from Script.Config import game_config, normal_config
from Script.Design import attr_calculation
from Script.UI.Panel import hypnosis_panel

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

class CharacterInfoHead:
    """
    角色信息面板头部面板
    Keyword arguments:
    character_id -- 角色id
    width -- 最大宽度
    """

    def __init__(self, character_id: int, width: int):
        """初始化绘制对象"""
        self.character_id: int = character_id
        """ 要绘制的角色id """
        self.width: int = width
        """ 当前最大可绘制宽度 """
        self.return_list: List[str] = []
        """ 当前面板监听的按钮列表 """
        self.draw_title: bool = True
        """ 是否绘制面板标题 """

        from Script.Design import handle_premise
        from Script.UI.Panel.see_item_info_panel import use_drug, auto_use_sanity_drug

        character_data: game_type.Character = cache.character_data[character_id]
        # sex_text = game_config.config_sex_tem[character_data.sex].name

        # 好感与信赖
        favorability_and_trust_text = ""
        if character_id:
            favorability_lv,tem = attr_calculation.get_favorability_level(character_data.favorability[0])
            favorability_lv_letter = attr_calculation.judge_grade(favorability_lv)
            trust_lv,tem = attr_calculation.get_trust_level(character_data.trust)
            trust_lv_letter = attr_calculation.judge_grade(trust_lv)
            favorability_text = f"{int(character_data.favorability[0])}"
            trust_text = f"{round(character_data.trust, 1)}%"
            # 只显示等级
            if cache.all_system_setting.draw_setting[3] == 1:
                favorability_and_trust_text = _("好感度:{0}，信赖度:{1}").format(favorability_lv_letter, trust_lv_letter)
            # 显示数值和等级
            elif cache.all_system_setting.draw_setting[3] == 2:
                favorability_and_trust_text = _("好感度:{0}({1})，信赖度:{2}({3})").format(favorability_text, favorability_lv_letter, trust_text, trust_lv_letter)

        # 非0疲劳时输出当前疲劳状态
        sleep_draw = draw.LeftDraw()
        sleep_draw.style = "little_dark_slate_blue"
        sleep_lv = attr_calculation.get_tired_level(character_data.tired_point)
        sleep_text = " <" + constant.tired_text_list[sleep_lv] + ">"

        # if character_id != 0:
        #     print("debug character_id = ",character_id,"    character_data.tired_point = ",character_data.tired_point,"   sleep_text = ",sleep_text)
        # 0疲劳的清醒则不输出
        if sleep_text == _(" <清醒>" ):
            sleep_text = ""
        if character_id > 0:
            # 睡眠中则输出睡眠程度
            if handle_premise.handle_action_sleep(character_id) or handle_premise.handle_unconscious_flag_1(character_id):
                tem, sleep_name = attr_calculation.get_sleep_level(character_data.sleep_point)
                sleep_text = f" <{sleep_name}>"
            # 如果在装睡则输出装睡
            if handle_premise.handle_self_sleep_h_awake_but_pretend_sleep(character_id):
                sleep_text = _(" <装睡>")
        sleep_draw.text = sleep_text

        # hp1的完全疲劳状态
        tired_draw = draw.LeftDraw()
        tired_draw.style = "little_dark_slate_blue"
        tired_text = ""
        if handle_premise.handle_self_tired(character_id):
            tired_text = _(" <累>")
        tired_draw.text = tired_text

        # 非普通时输出当前心情
        angry_draw = draw.LeftDraw()
        angry_text = ""
        if character_id != 0:
            angry_text = attr_calculation.get_angry_text(character_data.angry_point)
            angry_text = "" if angry_text == _("普通") else " " + angry_text
        if angry_text == _(" 愉快"):
            angry_draw.style = "coral"
        else:
            angry_draw.style = "red"
        angry_draw.text = angry_text

        # 智能跟随状态
        follow_draw = draw.LeftDraw()
        follow_draw.style = "spring_green"
        follow_text = ""
        if handle_premise.handle_is_follow_1(character_id):
            follow_text = _(" <跟>")
        follow_draw.text = follow_text

        # 有尿意时进行提示
        urinate_draw = draw.LeftDraw()
        urinate_draw.style = "khaki"
        urinate_text = _(" <尿>") if handle_premise.handle_urinate_ge_80(character_id) else ""
        urinate_draw.text = urinate_text

        # 饥饿时进行提示
        hunger_draw = draw.LeftDraw()
        hunger_draw.style = "beige"
        hunger_text = ""
        if character_id != 0:
            hunger_text = _(" <饿>") if handle_premise.handle_hunger_ge_80(character_id) else ""
            start_time = character_data.behavior.start_time.hour
            hunger_text = hunger_text if start_time in {6, 7, 8, 11, 12, 13, 16, 17, 18} else ""
        hunger_draw.text = hunger_text

        # 射精欲不为零时进行提示
        eja_text = ""
        if character_id == 0 and character_data.eja_point > 0:
            if character_data.eja_point <= 300:
                eja_text = _(" <射精欲:低>")
            elif character_data.eja_point <= 600:
                eja_text = _(" <射精欲:中>")
            elif character_data.eja_point <= 900:
                eja_text = _(" <射精欲:高>")
            else:
                eja_text = _(" <射精欲:极>")

        # 催眠状态时进行显示
        # 首先需要判断是否开启了催眠显示，其次要么已经是某个催眠状态下，要么催眠度大于0而且开启了显示催眠度
        hypnosis_draw = draw.LeftDraw()
        hypnosis_text = ""
        if (
            cache.all_system_setting.draw_setting[4] and 
            (handle_premise.handle_unconscious_hypnosis_flag(character_id) or
            (character_data.hypnosis.hypnosis_degree > 0 and cache.all_system_setting.draw_setting[4] == 2))
        ):
            hypnosis_text = _(" <催眠")
            # 根据催眠程度来区分颜色
            hypnosis_draw.style = hypnosis_panel.get_hypnosis_degree_color(self.character_id)
            # 是否显示具体数值
            if cache.all_system_setting.draw_setting[4] == 2:
                # 显示到小数点后一位
                hypnosis_text += f"({round(character_data.hypnosis.hypnosis_degree, 1)}%)"
            # 是否显示催眠类型
            if handle_premise.handle_unconscious_hypnosis_flag(character_id):
                hypnosis_cid = character_data.sp_flag.unconscious_h - 3
                hypnosis_name = game_config.config_hypnosis_type[hypnosis_cid].name
                hypnosis_text += _(":{0}").format(hypnosis_name)
            if handle_premise.handle_hypnosis_increase_body_sensitivity(character_id):
                hypnosis_text += _("(敏感)")
            if handle_premise.handle_hypnosis_force_ovulation(character_id):
                hypnosis_text += _("(排卵)")
            if handle_premise.handle_hypnosis_blockhead(character_id):
                hypnosis_text += _("(木头人)")
            if handle_premise.handle_hypnosis_active_h(character_id):
                hypnosis_text += _("(逆推)")
            if handle_premise.handle_hypnosis_roleplay(character_id):
                hypnosis_text += _("(扮演")
                for role_play_cid in character_data.hypnosis.roleplay:
                    role_play_name = game_config.config_roleplay[role_play_cid].name
                    hypnosis_text += f"-{role_play_name}"
                hypnosis_text += ")"
            if handle_premise.handle_hypnosis_pain_as_pleasure(character_id):
                hypnosis_text += _("(痛→快感)")
            hypnosis_text += ">"
        hypnosis_draw.text = hypnosis_text

        # 携袋状态进行提示
        bag_text = ""
        if character_data.sp_flag.bagging_chara_id:
            bag_text = _(" <携袋:{0}>").format(cache.character_data[character_data.sp_flag.bagging_chara_id].name)

        # 监禁状态
        imprisonment_text = ""
        imprisonment_draw = draw.LeftDraw()
        imprisonment_draw.style = "crimson"
        if handle_premise.handle_imprisonment_1(character_id):
            imprisonment_text = _(" <监>")
        imprisonment_draw.text = imprisonment_text

        # 访客
        visitor_text = ""
        if character_data.sp_flag.vistor == 1:
            visitor_text = _(" <访>")

        # 逆推H
        active_h_text = ""
        active_h_draw = draw.LeftDraw()
        active_h_draw.style = "light_pink"
        if handle_premise.handle_npc_active_h(character_id):
            active_h_text = _(" <逆>")
        active_h_draw.text = active_h_text

        # 绝顶寸止
        orgasm_edge_text = ""
        orgasm_edge_draw = draw.LeftDraw()
        orgasm_edge_draw.style = "rose_pink"
        if handle_premise.handle_self_orgasm_edge(character_id):
            orgasm_edge_text = _(" <寸止>")
        orgasm_edge_draw.text = orgasm_edge_text

        # 时停
        time_stop_text = ""
        time_stop_draw = draw.LeftDraw()
        time_stop_draw.style = "light_sky_blue"
        if handle_premise.handle_unconscious_flag_3(character_id):
            time_stop_text = _(" <时停>")
        time_stop_draw.text = time_stop_text

        # 隐奸
        hidden_text = ""
        hidden_draw = draw.LeftDraw()
        hidden_draw.style = "deep_gray"
        if character_id == 0 and (handle_premise.handle_hidden_sex_mode_3(character_id) or handle_premise.handle_hidden_sex_mode_4(character_id)):
            hidden_text = _(" <隐>")
        elif character_id != 0 and (handle_premise.handle_hidden_sex_mode_2(character_id) or handle_premise.handle_hidden_sex_mode_4(character_id)):
            hidden_text = _(" <隐>")
        hidden_draw.text = hidden_text

        if character_id:
            message = (
                "{character_name} {favorability_and_trust}{visitor}").format(
                character_name=character_data.name,
                favorability_and_trust=favorability_and_trust_text,
                visitor=visitor_text,
            )
        else:
            message = (
                "{character_name}{character_nick_name}{eja}").format(
                # character_id=character_id,
                character_name=character_data.name,
                character_nick_name=character_data.nick_name,
                # sex_text=sex_text,
                eja=eja_text,
                bag=bag_text,
            )
        message_draw = draw.CenterDraw()
        # 根据其他状态的长度来调整文本的长度，同时也保证了一个最小长度
        text_width = text_handle.get_text_index(message)
        base_width = width / 3.5 - text_handle.get_text_index(follow_text + angry_text + sleep_text + tired_text + urinate_text + hypnosis_text + hunger_text + active_h_text + orgasm_edge_text + time_stop_text + hidden_text + imprisonment_text)
        max_width = max(base_width, text_width)
        message_draw.width = int(max_width)
        message_draw.text = message
        hp_draw = draw.InfoBarDraw()
        hp_draw.width = int(width / 6)
        hp_draw.scale = 0.8
        hp_draw.set(
            "HitPointbar",
            int(character_data.hit_point_max),
            int(character_data.hit_point),
            _("体力"),
        )
        mp_draw = draw.InfoBarDraw()
        mp_draw.width = int(width / 6)
        mp_draw.scale = 0.8
        mp_draw.set(
            "ManaPointbar",
            int(character_data.mana_point_max),
            int(character_data.mana_point),
            _("气力"),
        )
        if character_id == 0:
            sanity_point_draw = draw.InfoBarDraw()
            sanity_point_draw.width = int(width / 7.5)
            sanity_point_draw.scale = 1
            sanity_point_draw.set(
                "SanityPointbar",
                int(character_data.sanity_point_max),
                int(character_data.sanity_point),
                _("理智"),
            )
            sanity_item_draw = draw.LeftButton(
                "✚",
                _("快速使用最小理智剂"),
                1,
                normal_style = "sanity",
                cmd_func = auto_use_sanity_drug,
            )
            semen_point_draw = draw.InfoBarDraw()
            semen_point_draw.width = int(width / 7.5)
            semen_point_draw.scale = 1
            semen_point_draw.set(
                "SemenPointBar",
                int(character_data.semen_point_max),
                int(character_data.semen_point + character_data.tem_extra_semen_point),
                _("精液"),
            )
            semen_item_draw = draw.LeftButton(
                "✚",
                _("快速使用精力剂"),
                1,
                normal_style = "semen",
                cmd_func = use_drug,
                args = 11,
            )
        None_draw = draw.CenterDraw()
        None_draw.width = 1
        None_draw.text = (" ")
        self.draw_list: List = [
            (message_draw, follow_draw, angry_draw, hunger_draw, urinate_draw, sleep_draw, tired_draw, hypnosis_draw, active_h_draw, orgasm_edge_draw, imprisonment_draw, time_stop_draw, hidden_draw, hp_draw, None_draw, mp_draw),
        ]
        if character_id == 0:
            self.draw_list[0] = self.draw_list[0] + (None_draw, None_draw, sanity_point_draw,)
            # 如果有理智恢复剂的话，显示快捷键
            for item_id in [0, 1, 2, 3]:
                if character_data.item[item_id] > 0:
                    self.draw_list[0] = self.draw_list[0] + (sanity_item_draw,)
                    self.return_list.append(sanity_item_draw.return_text)
                    break
            self.draw_list[0] = self.draw_list[0] + (None_draw, None_draw, semen_point_draw,)
            # 如果有精力恢复剂的话，显示快捷键
            if character_data.item[11] > 0:
                self.draw_list[0] = self.draw_list[0] + (semen_item_draw,)
                self.return_list.append(semen_item_draw.return_text)
        """ 要绘制的面板列表 """

    def draw(self):
        """绘制面板"""
        if self.draw_title:
            title_draw = draw.TitleLineDraw(_("人物属性"), self.width)
            title_draw.draw()
        for draw_tuple in self.draw_list:
            for label in draw_tuple:
                label.draw()
            line_feed.draw()
