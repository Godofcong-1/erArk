from uuid import UUID
from typing import Tuple, List
from types import FunctionType
from Script.UI.Moudle import draw, panel
from Script.Core import (
    cache_control,
    get_text,
    game_type,
    text_handle,
    py_cmd,
    flow_handle,
    constant,
)
from Script.Config import game_config, normal_config
from Script.Design import attr_text, map_handle, attr_calculation, game_time, instuct_judege, character_image
from Script.UI.Panel import body_info_panel

panel_info_data = {}

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


class SeeCharacterInfoPanel:
    """
    用于查看角色属性的面板对象
    Keyword arguments:
    character_id -- 角色id
    width -- 绘制宽度
    """

    def __init__(self, character_id: int, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.now_panel: str = _("基础属性")
        """ 当前的属性页id """
        self.character_id: int = character_id
        """ 要绘制的角色id """
        self.return_list: List[str] = []
        """ 当前面板监听的按钮列表 """
        base_attributes_draw = See_Character_Base_Attributes_Panel(character_id, width)
        detailed_attributes_draw = See_Character_Detailed_Attributes_Panel(character_id, width)
        main_third_draw = SeeCharacterThirdPanel(character_id, width)
        setting_draw = See_Character_Setting_Panel(character_id, width)
        if character_id == 0:
            self.draw_data = {
                _("基础属性"): base_attributes_draw,
                _("能力、经验与宝珠"): detailed_attributes_draw,
                _("玩家能力"): main_third_draw,
                _("角色设定"): setting_draw,
            }
        else:
            self.draw_data = {
                _("基础属性"): base_attributes_draw,
                _("能力、经验与宝珠"): detailed_attributes_draw,
                # _("日程与喜好"): see_daily_draw,
                _("肉体情况"): main_third_draw,
                _("角色设定"): setting_draw,
            }
        """ 按钮文本对应属性面板 """
        self.handle_panel = panel.CenterDrawButtonListPanel()
        """ 属性列表的控制面板 """
        self.handle_panel.set(
            [f"[{text}]" for text in self.draw_data.keys()],
            list(self.draw_data.keys()),
            width,
            4,
            f"[{self.now_panel}]",
            self.change_panel,
        )

    def change_panel(self, panel_id: str):
        """
        切换当前面板
        Keyword arguments:
        panel_id -- 要切换的面板id
        """
        self.now_panel = panel_id
        self.handle_panel.set(
            [f"[{text}]" for text in self.draw_data.keys()],
            list(self.draw_data.keys()),
            self.width,
            4,
            f"[{self.now_panel}]",
            self.change_panel,
        )

    def draw(self):
        """绘制面板"""
        if self.now_panel == _("玩家能力") and _("玩家能力") not in self.draw_data:
            self.now_panel = _("肉体情况")
        elif self.now_panel == _("肉体情况") and _("肉体情况") not in self.draw_data:
            self.now_panel = _("玩家能力")
        self.draw_data[self.now_panel].draw()
        self.return_list = []
        self.return_list.extend(self.draw_data[self.now_panel].return_list)
        line_feed.draw()
        line = draw.LineDraw("=", self.width)
        line.draw()
        self.handle_panel.draw()
        self.return_list.extend(self.handle_panel.return_list)


class See_Character_Base_Attributes_Panel:
    """
    显示角色属性面板第一页对象
    Keyword arguments:
    character_id -- 角色id
    width -- 绘制宽度
    """

    def __init__(self, character_id: int, width: int):
        """初始化绘制对象"""
        head_draw = CharacterInfoHead(character_id, width)
        image_draw = CharacterImage(character_id, width)
        Talent_draw = CharacterTalentText(character_id, width, 8, 0)
        Daily_draw = CharacterDailyText(character_id, width, 8, 0)
        if character_id == 0:
            self.draw_list: List[draw.NormalDraw] = [
                head_draw,
                image_draw,
                Talent_draw,
            ]
        else:
            self.draw_list: List[draw.NormalDraw] = [
                head_draw,
                image_draw,
                Talent_draw,
                Daily_draw,
            ]
        # 如果是访客则再加一个访客栏
        if character_id in cache.rhodes_island.visitor_info:
            visitor_draw = CharacterVisitorText(character_id, width, 8, 0)
            self.draw_list.append(visitor_draw)
        """ 绘制的面板列表 """
        self.return_list: List[str] = []
        """ 当前面板监听的按钮列表 """

    def draw(self):
        """绘制面板"""
        for label in self.draw_list:
            label.draw()


class See_Character_Detailed_Attributes_Panel:
    """
    显示角色属性面板第二页对象
    Keyword arguments:
    character_id -- 角色id
    width -- 绘制宽度
    """

    def __init__(self, character_id: int, width: int):
        """初始化绘制对象"""
        head_draw = CharacterInfoHead(character_id, width)
        abi_draw = CharacterabiText(character_id, width)
        experience_draw = CharacterExperienceText(character_id, width, 8, 0)
        juel_draw = CharacterJuelText(character_id, width, 8, 0)
        self.draw_list: List[draw.NormalDraw] = [
            head_draw,
            abi_draw,
            experience_draw,
            juel_draw,
        ]
        """ 绘制的面板列表 """
        self.return_list: List[str] = []
        """ 当前面板监听的按钮列表 """

    def draw(self):
        """绘制面板"""
        for label in self.draw_list:
            label.draw()


class SeeCharacterThirdPanel:
    """
    显示角色属性面板第三页对象
    Keyword arguments:
    character_id -- 角色id
    width -- 绘制宽度
    """

    def __init__(self, character_id: int, width: int):
        """初始化绘制对象"""
        head_draw = CharacterInfoHead(character_id, width)
        body_draw = body_info_panel.CharacterBodyText(character_id, width, 8, 0)
        ability_draw = PlayerAbilityText(character_id, width, 8, 0)
        if character_id == 0:
            self.draw_list: List[draw.NormalDraw] = [
                head_draw,
                ability_draw,
            ]
        else:
            self.draw_list: List[draw.NormalDraw] = [
                head_draw,
                body_draw,
            ]
        """ 绘制的面板列表 """
        self.return_list: List[str] = []
        """ 当前面板监听的按钮列表 """

    def draw(self):
        """绘制面板"""
        for label in self.draw_list:
            label.draw()
            self.return_list.extend(label.return_list)


class See_Character_Setting_Panel:
    """
    显示角色属性面板中的角色设置面板
    Keyword arguments:
    character_id -- 角色id
    width -- 绘制宽度
    """

    def __init__(self, character_id: int, width: int):
        """初始化绘制对象"""

        from Script.UI.Panel import character_setting

        head_draw = CharacterInfoHead(character_id, width)
        setting_draw = character_setting.CharacterSetting(character_id, width, 8, 0)
        self.draw_list: List[draw.NormalDraw] = [
            head_draw,
            setting_draw,
        ]
        """ 绘制的面板列表 """
        self.return_list: List[str] = []
        """ 当前面板监听的按钮列表 """

    def draw(self):
        """绘制面板"""
        for label in self.draw_list:
            label.draw()
            self.return_list.extend(label.return_list)


class SeeCharacterMainAttrPanel:
    """
    显示角色主属性面板对象
    Keyword arguments:
    character_id -- 角色id
    width -- 绘制宽度
    """

    def __init__(self, character_id: int, width: int):
        """初始化绘制对象"""
        head_draw = CharacterInfoHead(character_id, width)
        # stature_draw = CharacterStatureText(character_id, width)
        room_draw = CharacterRoomText(character_id, width)
        birthday_draw = CharacterBirthdayText(character_id, width)
        # sture_info_draw = CharacterStatureInfoText(character_id, width)
        # measurement_draw = CharacterMeasurementsText(character_id, width)
        # sex_experience_draw = CharacterSexExperienceText(character_id, width)
        self.draw_list: List[draw.NormalDraw] = [
            head_draw,
            # stature_draw,
            room_draw,
            birthday_draw,
            # sture_info_draw,
            # measurement_draw,
            # sex_experience_draw,
        ]
        """ 绘制的面板列表 """
        self.return_list: List[str] = []
        """ 当前面板监听的按钮列表 """

    def draw(self):
        """绘制面板"""
        for label in self.draw_list:
            label.draw()


class SeeCharacterStatusPanel:
    """
    显示角色状态面板对象
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
        character_data = cache.character_data[character_id]
        # print("game_config.config_character_state_type :",game_config.config_character_state_type)
        # print("game_config.config_character_state_type_data :",game_config.config_character_state_type_data)

        # 润滑单独处理，归到快感里
        other_status_ids = [8]

        for status_type in game_config.config_character_state_type_data:
            type_data = game_config.config_character_state_type[status_type]
            type_line = draw.LittleTitleLineDraw(type_data.name, width, ":")
            # print("type_data.name :",type_data.name)
            self.draw_list.append(type_line)
            type_list = game_config.config_character_state_type_data[status_type]
            draw_count = 0
            
            # 如果是状态类型0，需要特殊处理快感状态的顺序
            if status_type == 0:
                
                # 先处理快感状态
                for status_id in type_list:
                    if self._draw_status_bar(character_data, status_id):
                        draw_count += 1
                        if draw_count % self.column == 0:
                            self.draw_list.append(line_feed)
                
                # 然后处理其他状态
                for status_id in other_status_ids:
                    if self._draw_status_bar(character_data, status_id):
                        draw_count += 1
                        if draw_count % self.column == 0:
                            self.draw_list.append(line_feed)

                # 进行一次换行
                if draw_count % self.column != 0:
                    draw_count = 0
                    self.draw_list.append(line_feed)
            else:
                # 其他类型按原有顺序处理
                for status_id in type_list:
                    # 跳过其他类
                    if status_id in other_status_ids:
                        continue
                    if self._draw_status_bar(character_data, status_id):
                        draw_count += 1
                        if draw_count % self.column == 0:
                            self.draw_list.append(line_feed)
            
            # 确保在该类型结束时换行
            if draw_count % self.column != 0:
                self.draw_list.append(line_feed)
    
    def _draw_status_bar(self, character_data, status_id):
        """绘制单个状态条
        返回True表示成功绘制，False表示跳过"""
        # 性别过滤
        if status_id in {2, 4, 7} and character_data.sex == 0:
            return False
        if status_id == 3 and character_data.sex == 1:
            return False
        
        # 计算状态数值和等级
        status_text = game_config.config_character_state[status_id].name
        status_value = 0
        if status_id in character_data.status_data:
            status_value = character_data.status_data[status_id]
        status_value = round(status_value)
        status_level = attr_calculation.get_status_level(status_value)
        
        # 计算当前等级的最大值
        next_level_value = game_config.config_character_state_level[status_level].max_value
        now_text = f"{status_text}lv{status_level}"
        
        # 绘制状态条
        bar_draw = draw.InfoBarDraw()
        bar_draw.width = self.width / self.column
        bar_draw.scale = 0.8
        bar_draw.chara_state = True
        bar_draw.set(
            "StatusPointbar",
            next_level_value,
            status_value,
            now_text,
        )
        self.draw_list.append(bar_draw)
        return True

    def draw(self):
        """绘制面板"""
        # title_draw = draw.TitleLineDraw(_("人物状态"), self.width)
        # title_draw.draw()
        line_feed.draw()
        for label in self.draw_list:
            if isinstance(label, list):
                for value in label:
                    value.draw()
                line_feed.draw()
            else:
                label.draw()


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
                tem,sleep_name = attr_calculation.get_sleep_level(character_data.sleep_point)
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
            if character_data.hypnosis.hypnosis_degree < 50:
                hypnosis_draw.style = "pink"
            elif character_data.hypnosis.hypnosis_degree < 100:
                hypnosis_draw.style = "hot_pink"
            elif character_data.hypnosis.hypnosis_degree < 200:
                hypnosis_draw.style = "deep_pink"
            else:
                hypnosis_draw.style = "purple"
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
        message_draw.width = max_width
        message_draw.text = message
        hp_draw = draw.InfoBarDraw()
        hp_draw.width = width / 6
        hp_draw.scale = 0.8
        hp_draw.set(
            "HitPointbar",
            int(character_data.hit_point_max),
            int(character_data.hit_point),
            _("体力"),
        )
        mp_draw = draw.InfoBarDraw()
        mp_draw.width = width / 6
        mp_draw.scale = 0.8
        mp_draw.set(
            "ManaPointbar",
            int(character_data.mana_point_max),
            int(character_data.mana_point),
            _("气力"),
        )
        if character_id == 0:
            sanity_point_draw = draw.InfoBarDraw()
            sanity_point_draw.width = width / 7.5
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
            semen_point_draw.width = width / 7.5
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
        self.draw_list: List[Tuple[draw.NormalDraw, draw.NormalDraw]] = [
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


class CharacterStatureText:
    """
    身材描述信息面板
    Keyword arguments:
    character_id -- 角色id
    width -- 最大宽度
    """

    def __init__(self, character_id: int, width: int):
        """初始化绘制对象"""
        self.character_id = character_id
        """ 要绘制的角色id """
        self.width = width
        """ 当前最大可绘制宽度 """
        player_data = cache.character_data[0]
        description = attr_text.get_stature_text(character_id)
        description = description.format(
            Name=player_data.name,
            NickName=player_data.nick_name,
        )
        self.description = description
        """ 身材描述文本 """

    def draw(self):
        """绘制面板"""
        line = draw.LineDraw(":", self.width)
        line.draw()
        info_draw = draw.CenterDraw()
        info_draw.text = self.description
        info_draw.width = self.width
        info_draw.draw()
        line_feed.draw()


class CharacterRoomText:
    """
    角色宿舍/教室和办公室地址显示面板
    Keyword arguments:
    character_id -- 角色id
    width -- 最大宽度
    """

    def __init__(self, character_id: int, width: int):
        """初始化绘制对象"""
        self.character_id = character_id
        """ 要绘制的角色id """
        self.width = width
        """ 当前最大可绘制宽度 """
        character_data: game_type.Character = cache.character_data[self.character_id]
        dormitory = character_data.dormitory
        dormitory_text = ""
        if dormitory == "":
            dormitory_text = _("暂无")
        else:
            dormitory_path = map_handle.get_map_system_path_for_str(dormitory)
            dormitory_text = attr_text.get_scene_path_text(dormitory_path)
        self.dormitory_text = _("宿舍位置:") + dormitory_text
        """ 宿舍位置文本 """
        # classroom = character_data.classroom
        # now_classroom_text = _("教室位置:")
        # if classroom != "":
        #     classroom_path = map_handle.get_map_system_path_for_str(classroom)
        #     classroom_text = attr_text.get_scene_path_text(classroom_path)
        #     now_classroom_text += classroom_text
        # else:
        #     now_classroom_text += _("暂无")
        # self.classroom_text = now_classroom_text
        # """ 教室位置文本 """
        officeroom = character_data.officeroom
        now_officeroom_text = _("办公室位置:")
        if len(officeroom):
            officeroom_text = attr_text.get_scene_path_text(officeroom)
            now_officeroom_text += officeroom_text
        else:
            now_officeroom_text += _("暂无")
        self.officeroom_text = now_officeroom_text
        """ 办公室位置文本 """

    def draw(self):
        """绘制面板"""
        line = draw.LineDraw(".", self.width)
        line.draw()
        info_draw = panel.CenterDrawTextListPanel()
        # info_draw.set([self.dormitory_text, self.classroom_text, self.officeroom_text], self.width, 3)
        info_draw.draw()


class CharacterBirthdayText:
    """
    角色年龄/生日信息显示面板
    Keyword arguments:
    character_id -- 角色id
    width -- 最大宽度
    """

    def __init__(self, character_id: int, width: int):
        """初始化绘制对象"""
        self.character_id = character_id
        """ 要绘制的角色id """
        self.width = width
        """ 当前最大可绘制宽度 """
        character_data = cache.character_data[self.character_id]
        # age_text = _("年龄:{character_age}岁").format(character_age=character_data.age)
        birthday_text = _("生日:{birthday_month}月{birthday_day}日").format(
            birthday_month=character_data.birthday.month, birthday_day=character_data.birthday.day
        )
        # self.info_list = [age_text, birthday_text]
        self.info_list = [birthday_text]
        """ 绘制的文本列表 """

    def draw(self):
        """绘制面板"""
        line = draw.LineDraw(".", self.width)
        line.draw()
        info_draw = panel.CenterDrawTextListPanel()
        info_draw.set(self.info_list, self.width, 2)
        info_draw.draw()


class CharacterStatureInfoText:
    """
    角色身高体重罩杯信息显示面板
    Keyword arguments:
    character_id -- 角色id
    width -- 最大宽度
    """

    def __init__(self, character_id: int, width: int):
        """初始化绘制对象"""
        self.character_id = character_id
        """ 要绘制的角色id """
        self.width = width
        """ 当前最大可绘制宽度 """
        character_data: game_type.Character = cache.character_data[self.character_id]
        now_height = str(round(character_data.height.now_height, 2))
        now_height_text = _("身高:") + now_height + "cm"
        now_weight = str(round(character_data.weight, 2))
        now_weight_text = _("体重:") + now_weight + "kg"
        now_chest_tem_id = attr_calculation.judge_chest_group(character_data.chest.now_chest)
        now_chest_tem = game_config.config_chest[now_chest_tem_id]
        body_fat = str(round(character_data.bodyfat, 2))
        body_fat_text = _("体脂率:") + body_fat + "%"
        now_chest_text = _("罩杯:") + now_chest_tem.info
        self.info_list = [now_height_text, now_weight_text, now_chest_text, body_fat_text]
        """ 绘制的文本列表 """

    def draw(self):
        """绘制面板"""
        line = draw.LineDraw(".", self.width)
        line.draw()
        info_draw = panel.CenterDrawTextListPanel()
        info_draw.set(self.info_list, self.width, 4)
        info_draw.draw()


class CharacterMeasurementsText:
    """
    角色三围信息显示面板
    Keyword arguments:
    character_id -- 角色id
    width -- 最大宽度
    """

    def __init__(self, character_id: int, width: int):
        """初始化绘制对象"""
        self.character_id = character_id
        """ 要绘制的角色id """
        self.width = width
        """ 当前最大可绘制宽度 """
        character_data = cache.character_data[self.character_id]
        character_data.measurements.bust
        character_data.measurements.hip
        character_data.measurements.waist
        now_bust = str(round(character_data.measurements.bust, 2))
        now_hip = str(round(character_data.measurements.hip, 2))
        now_waist = str(round(character_data.measurements.waist, 2))
        now_bust_text = _("胸围:") + now_bust + "cm"
        now_waist_text = _("腰围:") + now_waist + "cm"
        now_hip_text = _("臀围") + now_hip + "cm"
        self.info_list = [now_bust_text, now_waist_text, now_hip_text]
        """ 绘制的文本列表 """

    def draw(self):
        """绘制面板"""
        line = draw.LineDraw(".", self.width)
        line.draw()
        info_draw = panel.CenterDrawTextListPanel()
        info_draw.set(self.info_list, self.width, 3)
        info_draw.draw()


class CharacterSexExperienceText:
    """
    角色性经验信息面板
    Keyword arguments:
    character_id -- 角色id
    width -- 最大宽度
    """

    def __init__(self, character_id: int, width: int):
        """初始化绘制对象"""
        self.character_id = character_id
        """ 绘制的角色id """
        self.width = width
        """ 当前最大可绘制宽度 """
        character_data = cache.character_data[self.character_id]
        self.experience_text_data = {
            0: _("Ｎ感觉:"),
            1: _("Ｂ感觉:"),
            2: _("Ｃ感觉:"),
            3: _("Ｐ感觉:"),
            4: _("Ｖ感觉:"),
            5: _("Ａ感觉:"),
            6: _("Ｕ感觉:"),
            7: _("Ｗ感觉:"),
        }
        """ 性器官开发度描述 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制对象列表 """
        sex_tem = character_data.sex in (0, 3)
        organ_list = game_config.config_organ_data[sex_tem] | game_config.config_organ_data[2]
        for organ in organ_list:
            if organ != 8:
                now_draw = draw.NormalDraw()
                now_draw_1 = draw.NormalDraw()
                now_draw_2 = draw.NormalDraw()
                now_draw_value = draw.NormalDraw()
                now_draw.text = self.experience_text_data[organ]
                now_draw_1.text = " "
                now_draw_2.text = "  "
                now_draw.width = width / len(organ_list)
                now_exp = 0
                if organ in character_data.sex_experience:
                    now_exp = character_data.sex_experience[organ]
                now_draw_value.text = str(now_exp)
                level_draw = draw.ExpLevelDraw(now_exp)
                new_draw = draw.CenterMergeDraw(width / len(organ_list))
                # print("width :",width)
                # print("len(organ_list) :",len(organ_list))
                new_draw.draw_list.append(now_draw)
                new_draw.draw_list.append(now_draw_1)
                new_draw.draw_list.append(level_draw)
                new_draw.draw_list.append(now_draw_2)
                new_draw.draw_list.append(now_draw_value)
                self.draw_list.append(new_draw)

    def draw(self):
        """绘制对象"""
        line = draw.LineDraw(".", self.width)
        line.draw()
        for value in self.draw_list:
            value.draw()


class CharacterabiText:
    """
    角色能力面板
    Keyword arguments:
    character_id -- 角色id
    width -- 最大宽度
    """

    def __init__(self, character_id: int, width: int):
        """初始化绘制对象"""
        self.character_id = character_id
        """ 绘制的角色id """
        self.width = width
        """ 当前最大可绘制宽度 """
        self.type = type
        """ 当前绘制类型 """
        # self.column = column
        # """ 每行状态最大个数 """
        character_data = cache.character_data[self.character_id]
        """ 角色数据 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制对象列表 """
        self.title_list: List[draw.NormalDraw] = []
        """ 绘制标题列表 """
        ability_list = game_config.config_ability_type_data
        title_text = _("能力")
        type_line = draw.LittleTitleLineDraw(title_text, width, ":")
        self.draw_list.append(type_line)
        # 进入能力大类#
        for anility_type in ability_list:
            # if anility_type == type:
            type_set = ability_list[anility_type]
            # 去掉玩家的若干能力#
            if self.character_id == 0:
                if anility_type in {0, 1, 2, 6}:
                    continue
            for ability_id in type_set:
                # 去掉与性别不符的能力#
                if character_data.sex == 0:
                    if ability_id in {73, 74, 75}:
                        continue
                elif character_data.sex == 1:
                    if ability_id == 3:
                        continue
                # 去掉时奸刻印
                if ability_id == 16:
                    continue
                now_draw = draw.NormalDraw()
                now_draw_value = draw.NormalDraw()
                now_draw.text = game_config.config_ability[ability_id].name
                # 这个_1是为了补空格让格式对齐#
                now_draw_1 = draw.NormalDraw()
                now_draw_1.text = "　"
                now_draw_1.width = 2
                now_exp = 0
                now_exp = character_data.ability[ability_id]
                now_draw_value.text = str(now_exp)
                level_draw = draw.ExpLevelDraw(now_exp)
                new_draw = draw.LeftMergeDraw(self.width / 16)
                # 同类能力里在八个前补个换行
                if ability_id == 48 or ability_id == 101:
                    new_draw_n = draw.NormalDraw()
                    new_draw_n.text = "\n"
                    new_draw_n.width = 1
                    new_draw.draw_list.append(new_draw_n)
                new_draw.draw_list.append(now_draw_1)
                new_draw.draw_list.append(now_draw)
                new_draw.draw_list.append(now_draw_1)
                # 根据不同的类型补不同数量的空格#
                if anility_type == 3 or anility_type == 5:
                    new_draw.draw_list.append(now_draw_1)
                    new_draw.draw_list.append(now_draw_1)
                new_draw.draw_list.append(level_draw)
                new_draw.draw_list.append(now_draw_1)
                new_draw.draw_list.append(now_draw_value)
                if anility_type == 3 or anility_type == 5:
                    new_draw.draw_list.append(now_draw_1)
                    new_draw.draw_list.append(now_draw_1)
                self.draw_list.append(new_draw)
            # 只有不是最后一个类型就补个换行#
            if anility_type != 6:
                new_draw_n = draw.NormalDraw()
                new_draw_n.text = "\n"
                new_draw_n.width = 1
                self.draw_list.append(new_draw_n)

    def draw(self):
        """绘制对象"""
        line_feed.draw()
        for value in self.draw_list:
            value.draw()


class CharacterImage:
    """
    角色立绘面板
    Keyword arguments:
    character_id -- 角色id
    width -- 最大宽度
    """

    def __init__(self, character_id: int, width: int):
        """初始化绘制对象"""
        self.character_id = character_id
        """ 绘制的角色id """
        self.width = width
        """ 当前最大可绘制宽度 """
        # self.type = type
        # """ 当前绘制类型 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制对象列表 """
        self.title_list: List[draw.NormalDraw] = []
        """ 绘制标题列表 """
        title_text = _("立绘")
        type_line = draw.LittleTitleLineDraw(title_text, width, ":")
        self.title_list.append(type_line)

        self.image_name = character_image.find_character_image_name(character_id)

        now_draw_1 = draw.NormalDraw()
        now_draw_1.text = "  "
        now_draw_1.width = 2
        self.draw_list.append(now_draw_1)

    def draw(self):
        """绘制对象"""
        if self.character_id != 0:
            for value in self.title_list:
                value.draw()
            # for value in self.draw_list:
            #     value.draw()
            now_draw_1 = draw.NormalDraw()
            now_draw_1.text = " "
            now_draw_1.width = 1
            now_draw_1.draw()
            flow_handle.print_image_cmd(self.image_name, "立绘按钮")


class CharacterExperienceText:
    """
    显示角色经验面板对象
    Keyword arguments:
    character_id -- 角色id
    width -- 绘制宽度
    column -- 每行状态最大个数
    type_number -- 显示的状态类型
    """

    def __init__(self, character_id: int, width: int, column: int, center_status: bool = True):
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
        character_data = cache.character_data[character_id]
        type_data = _("经验")
        type_line = draw.LittleTitleLineDraw(type_data, width, ":")
        self.draw_list.append(type_line)
        experience_text_list = []
        for experience_id in game_config.config_experience:
            if character_data.sex == 0:
                if experience_id in {2, 4, 7, 12, 14, 17, 20, 22, 26, 51, 54, 55, 58, 72, 74, 77, 86, 100, 101, 102,
                                     103, 104, 105, 106}:
                    continue
            elif character_data.sex == 1:
                if experience_id == {3, 13, 21, 73}:
                    continue
            experience_text = game_config.config_experience[experience_id].name
            experience_value = 0
            if experience_id in character_data.experience:
                experience_value = character_data.experience[experience_id]
                now_text = f" {experience_text}:{experience_value}"
            if experience_value > 0:
                experience_text_list.append(now_text)
        if self.center_status:
            now_draw = panel.CenterDrawTextListPanel()
        else:
            now_draw = panel.LeftDrawTextListPanel()
        now_draw.set(experience_text_list, self.width, self.column)
        self.draw_list.extend(now_draw.draw_list)

    def draw(self):
        """绘制面板"""
        # title_draw = draw.TitleLineDraw(_("人物状态"), self.width)
        # title_draw.draw()
        line_feed.draw()
        count = 0
        for label in self.draw_list:
            if isinstance(label, list):
                for value in label:
                    value.draw()
                    count += 1
                line_feed.draw()
            else:
                label.draw()
        if count <= 8:
            line_feed.draw()
            if count == 0:
                line_feed.draw()


class CharacterTalentText:
    """
    显示角色素质面板对象
    Keyword arguments:
    character_id -- 角色id
    width -- 绘制宽度
    column -- 每行状态最大个数
    type_number -- 显示的状态类型
    """

    def __init__(self, character_id: int, width: int, column: int, center_status: bool = True):
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
        character_data = cache.character_data[character_id]
        profession_text = game_config.config_profession[character_data.profession].name
        race_text = game_config.config_race[character_data.race].name
        # 如果birthplace是str的话，将其转换为int
        if isinstance(character_data.relationship.birthplace, str):
            character_data.relationship.birthplace = int(character_data.relationship.birthplace)
        birthplace_text = game_config.config_birthplace[character_data.relationship.birthplace].name
        # 如果nation是str的话，将其转换为int
        if isinstance(character_data.relationship.nation, str):
            character_data.relationship.nation = int(character_data.relationship.nation)
        nation_text = game_config.config_nation[character_data.relationship.nation].name
        type_data = _("素质")
        type_line = draw.LittleTitleLineDraw(type_data, width, ":")
        self.draw_list.append(type_line)
        talent_list = game_config.config_talent_type_data
        # print("进入for之前")
        conut = 0
        for talent_type in talent_list:
            type_data = game_config.config_talent_type[talent_type]
            type_line = draw.LittleTitleLineDraw(type_data.name, width, ":")
            # print("type_data.name :",type_data.name)
            type_set = talent_list[talent_type]
            talent_text_list = []
            if conut == 0:
                message_profession = _(" 职业    ：[{profession_text}]").format(
                    profession_text=profession_text,
                )
                talent_text_list.append(message_profession)
                message_race = _("\n 种族    ：[{race_text}]").format(
                    race_text=race_text,
                )
                talent_text_list.append(message_race)
                message_nation = _("\n 势力    ：[{nation_text}]").format(
                    nation_text=nation_text,
                )
                talent_text_list.append(message_nation)
                message_birthplace = _("\n 出身地  ：[{birthplace_text}]").format(
                    birthplace_text=birthplace_text,
                )
                talent_text_list.append(message_birthplace)
                conut = 1
            race_type = type_data.name
            if talent_type == 0:
                message_race = f"\n {race_type}  ："
            else:
                message_race = f"\n {race_type}："
            for talent_id in type_set:
                talent_text = game_config.config_talent[talent_id].name
                if character_data.talent[talent_id]:
                    now_text = f"[{talent_text}]"
                    message_race += now_text
            talent_text_list.append(message_race)
            if self.center_status:
                now_draw = panel.CenterDrawTextListPanel()
            else:
                now_draw = panel.LeftDrawTextListPanel()
            now_draw.set(talent_text_list, self.width, self.column)
            self.draw_list.extend(now_draw.draw_list)

    def draw(self):
        """绘制面板"""
        line_feed.draw()
        for label in self.draw_list:
            if isinstance(label, list):
                for value in label:
                    value.draw()
                # line_feed.draw()
            else:
                label.draw()


class CharacterDailyText:
    """
    显示角色日程面板对象
    Keyword arguments:
    character_id -- 角色id
    width -- 绘制宽度
    column -- 每行状态最大个数
    type_number -- 显示的状态类型
    """

    def __init__(self, character_id: int, width: int, column: int, center_status: bool = True):
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
        character_data = cache.character_data[character_id]
        work_text = game_config.config_work_type[character_data.work.work_type].name
        entertainment_text_list = []
        for entertainment_type in character_data.entertainment.entertainment_type:
            entertainment_name = game_config.config_entertainment[entertainment_type].name
            entertainment_text_list.append(entertainment_name)


        type_data = _("日程")
        type_line = draw.LittleTitleLineDraw(type_data, width, ":")
        self.draw_list.append(type_line)

        now_draw = panel.LeftDrawTextListPanel()
        text_list = _("当前工作：{0}     ").format(work_text)
        if game_time.judge_work_today(character_id) and character_data.work.work_type:
            text_list += _(" 今日上午：工作    今日下午：工作    今日晚上：{0}").format(entertainment_text_list[2])
        else:
            text_list += _(" 今日上午：{0}    今日下午：{1}    今日晚上：{2}").format(entertainment_text_list[0], entertainment_text_list[1], entertainment_text_list[2])

        text_draw = draw.LeftDraw()
        text_draw.text = text_list
        text_draw.width = self.width
        now_draw.draw_list.append(text_draw)
        now_draw.width += len(text_draw.text)
        self.draw_list.extend(now_draw.draw_list)

    def draw(self):
        """绘制面板"""
        line_feed.draw()
        for label in self.draw_list:
            if isinstance(label, list):
                for value in label:
                    value.draw()
                # line_feed.draw()
            else:
                label.draw()


class CharacterVisitorText:
    """
    显示角色访客信息子面板对象
    Keyword arguments:
    character_id -- 角色id
    width -- 绘制宽度
    column -- 每行状态最大个数
    type_number -- 显示的状态类型
    """

    def __init__(self, character_id: int, width: int, column: int, center_status: bool = True):
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
        character_data = cache.character_data[character_id]

        type_data = _("访客")
        type_line = draw.LittleTitleLineDraw(type_data, width, ":")
        self.draw_list.append(type_line)

        now_draw = panel.LeftDrawTextListPanel()
        text_list = ""
        # 计算访客留下概率
        tem_1, tem_2, stay_posibility = instuct_judege.calculation_instuct_judege(0, character_id, _("访客留下"))
        # 遍历所有留下态度
        for attitude_id in game_config.config_visitor_stay_attitude:
            attitude_data = game_config.config_visitor_stay_attitude[attitude_id]
            if stay_posibility >= attitude_data.rate:
                continue
            # 获得留下态度对应的文本
            stay_text = attitude_data.name
            break
        leav_time = game_time.get_date_until_day(cache.rhodes_island.visitor_info[character_id])
        live_room = character_data.dormitory.split("\\")[-1]
        text_list += _("留下意愿：{0}     ").format(stay_text)
        text_list += _("离开时间：{0}     ").format(leav_time)
        text_list += _("居住房间：{0}").format(live_room)

        text_draw = draw.LeftDraw()
        text_draw.text = text_list
        text_draw.width = self.width
        now_draw.draw_list.append(text_draw)
        now_draw.width += len(text_draw.text)
        self.draw_list.extend(now_draw.draw_list)

    def draw(self):
        """绘制面板"""
        line_feed.draw()
        for label in self.draw_list:
            if isinstance(label, list):
                for value in label:
                    value.draw()
                # line_feed.draw()
            else:
                label.draw()


class CharacterJuelText:
    """
    显示角色宝珠面板对象
    Keyword arguments:
    character_id -- 角色id
    width -- 绘制宽度
    column -- 每行状态最大个数
    type_number -- 显示的状态类型
    """

    def __init__(self, character_id: int, width: int, column: int, center_status: bool = True):
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
        character_data = cache.character_data[character_id]
        type_data = _("宝珠")
        type_line = draw.LittleTitleLineDraw(type_data, width, ":")
        self.draw_list.append(type_line)
        juel_text_list = []
        for juel_id in game_config.config_juel:
            if character_data.sex == 0:
                if juel_id in {2, 4, 7}:
                    continue
            elif character_data.sex == 1:
                if juel_id == {3}:
                    continue
            juel_text = game_config.config_juel[juel_id].name
            juel_value = 0
            if juel_id in character_data.juel:
                juel_value = character_data.juel[juel_id]
            now_text = f" {juel_text}:{juel_value}"
            juel_text_list.append(now_text)
        if self.center_status:
            now_draw = panel.CenterDrawTextListPanel()
        else:
            now_draw = panel.LeftDrawTextListPanel()
        now_draw.set(juel_text_list, self.width, self.column)
        self.draw_list.extend(now_draw.draw_list)

    def draw(self):
        """绘制面板"""
        line_feed.draw()
        for label in self.draw_list:
            if isinstance(label, list):
                for value in label:
                    value.draw()
                line_feed.draw()
            else:
                label.draw()


class CharacterTokenText:
    """
    显示角色信物面板对象
    Keyword arguments:
    character_id -- 角色id
    width -- 绘制宽度
    column -- 每行状态最大个数
    type_number -- 显示的状态类型
    """

    def __init__(self, character_id: int, width: int, column: int, center_status: bool = True):
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
        character_data = cache.character_data[character_id]
        type_data = _("信物")
        type_line = draw.LittleTitleLineDraw(type_data, width, ":")
        self.draw_list.append(type_line)
        token_text_list = []
        for token_id in range(len(character_data.pl_collection.token_list)):
            if token_id == 0:
                continue
            if character_data.pl_collection.token_list[token_id] == 1:
                target_character_data = cache.character_data[token_id]
                character_name = target_character_data.name
                token_text = target_character_data.token_text
                now_text = _(" 已拥有{0}的信物:{1}").format(character_name, token_text)
                token_text_list.append(now_text)
        if self.center_status:
            now_draw = panel.CenterDrawTextListPanel()
        else:
            now_draw = panel.LeftDrawTextListPanel()
        now_draw.set(token_text_list, self.width, self.column)
        self.draw_list.extend(now_draw.draw_list)

    def draw(self):
        """绘制面板"""
        line_feed.draw()
        for label in self.draw_list:
            if isinstance(label, list):
                for value in label:
                    value.draw()
                line_feed.draw()
            else:
                label.draw()


class PlayerAbilityText:
    """
    显示玩家能力面板对象
    Keyword arguments:
    character_id -- 角色id
    width -- 绘制宽度
    column -- 每行状态最大个数
    type_number -- 显示的状态类型
    """

    def __init__(self, character_id: int, width: int, column: int, center_status: bool = True):
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
        character_data = cache.character_data[character_id]
        type_data = _("玩家能力")
        type_line = draw.LittleTitleLineDraw(type_data, width, ":")
        self.draw_list.append(type_line)
        ability_text_list = []

        # 定义能力与素质的对应字典
        abilities = {
            _("视觉系"): {307, 308, 309},
            _("触觉系"): {310, 311, 312},
            _("激素系"): {304, 305, 306},
            _("催眠系"): {331, 332, 333, 334},
            _("时间系"): {316, 317, 318}
        }

        # 遍历能力字典，获取对应的文本
        for ability_name, ids in abilities.items():
            now_text = _("\n 【{}】\n".format(ability_name))
            for i in ids:
                if character_data.talent[i]:
                    talent_name = game_config.config_talent[i].name
                    talent_info = game_config.config_talent[i].info
                    now_text += f"  {talent_name}：{talent_info}\n"
            ability_text_list.append(now_text)

        if self.center_status:
            now_draw = panel.CenterDrawTextListPanel()
        else:
            now_draw = panel.LeftDrawTextListPanel()
        now_draw.set(ability_text_list, self.width, self.column)
        self.draw_list.extend(now_draw.draw_list)

        # 绘制装备信物的信息
        info_text = _("装备信物")
        now_draw = draw.LittleTitleLineDraw(info_text, width, ":")
        self.draw_list.append(now_draw)
        # 绘制提示信息
        now_text = "\n"
        now_text += _("○装备信物时，信物干员正面数值结算+10%，负面数值结算-10%，其他干员为+1%和-1%（可叠加，上限同装备信物上限）\n")
        # 可装备数量
        pl_character_data = cache.character_data[0]
        # 此处修正一下旧版本导致的信物数据
        if pl_character_data.pl_collection.eqip_token == [0, [0]]:
            pl_character_data.pl_collection.eqip_token = [1, []]
        equip_number = pl_character_data.pl_collection.eqip_token[0]
        now_text += _("  当前最大可装备数量：{0}\n\n").format(equip_number)
        now_text += _("  当前装备的信物：\n")
        # 当前正在装备的信物展示
        for chara_id in pl_character_data.pl_collection.eqip_token[1]:
            if chara_id == 0:
                continue
            now_text += f"  {cache.character_data[chara_id].name}："
            token_text = cache.character_data[chara_id].token_text
            now_text += f"{token_text}\n"
        now_draw = draw.LeftDraw()
        now_draw.text = now_text
        now_draw.width = self.width
        self.draw_list.append(now_draw)
        self.draw_list.append(line_feed)
        # 更改装备信物的按钮
        button_text = _("[更改装备信物]")
        now_draw = draw.CenterButton(
            button_text, button_text, self.width / 4, cmd_func=self.change_token
        )
        self.return_list.append(now_draw.return_text)
        self.draw_list.append(now_draw)
        self.draw_list.append(line_feed)

    def draw(self):
        """绘制面板"""
        line_feed.draw()
        for label in self.draw_list:
            if isinstance(label, list):
                for value in label:
                    value.draw()
                line_feed.draw()
            else:
                label.draw()

    def change_token(self):
        """更改装备信物"""
        pl_character_data = cache.character_data[0]
        equip_number = pl_character_data.pl_collection.eqip_token[0]

        while 1:
            # 初始化变量
            now_equiped = pl_character_data.pl_collection.eqip_token[1]
            return_list = []
            # 横线
            line = draw.LineDraw("-", self.width)
            line.draw()
            # 绘制提示信息
            info_text = _("\n更改装备信物\n")
            info_text += _("当前已装备数量/最大可装备数量：{0}/{1}\n").format(len(now_equiped), equip_number)
            info_text += _("请选择要装备的信物：\n")
            info_draw = draw.LeftDraw()
            info_draw.text = info_text
            info_draw.width = self.width
            info_draw.draw()
            line_feed.draw()
            # 绘制可选择的装备信物
            count = 0
            for character_id in cache.npc_id_got:
                if character_id == 0:
                    continue
                # 跳过未拥有信物的
                if pl_character_data.pl_collection.token_list[character_id] == 0:
                    continue
                draw_style = "standard"
                # 如果已经选择，则绘制为金色
                if character_id in now_equiped:
                    draw_style = "gold_enrod"
                character_data: game_type.Character = cache.character_data[character_id]
                character_name = character_data.name
                character_adv = character_data.adv
                character_token = character_data.token_text
                draw_text = f"[{str(character_adv).rjust(4,'0')}]{character_name}：{character_token}"
                # 如果可以选择，则正常绘制按钮
                if len(now_equiped) < equip_number or character_id in now_equiped:
                    button_draw = draw.LeftButton(
                        draw_text,
                        f"\n{character_id}",
                        self.width,
                        normal_style = draw_style,
                        cmd_func = self.select_this_token,
                        args=character_id,
                    )
                    button_draw.draw()
                    return_list.append(button_draw.return_text)
                # 如果当前人数已经满足，则不再绘制按钮，只绘制文本
                else:
                    info_draw = draw.LeftDraw()
                    info_draw.text = draw_text
                    info_draw.width = self.width
                    info_draw.style = "deep_gray"
                    info_draw.draw()
                count += 1
                line_feed.draw()
            # 如果没有可以选择的，则绘制提示信息
            if count == 0:
                info_text = _("  当前没有可以选择的信物\n")
                info_draw = draw.LeftDraw()
                info_draw.text = info_text
                info_draw.width = self.width
                info_draw.draw()

            line_feed.draw()
            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                break

    def select_this_token(self, character_id):
        """选择信物"""
        pl_character_data = cache.character_data[0]
        if character_id in pl_character_data.pl_collection.eqip_token[1]:
            pl_character_data.pl_collection.eqip_token[1].remove(character_id)
        else:
            pl_character_data.pl_collection.eqip_token[1].append(character_id)

# class SeeCharacterSocialContact:
#     """
#     显示角色社交关系面板对象
#     Keyword arguments:
#     character_id -- 角色id
#     width -- 绘制宽度
#     """

#     def __init__(self, character_id: int, width: int):
#         """初始化绘制对象"""
#         self.character_id: int = character_id
#         """ 要绘制的角色id """
#         self.width: int = width
#         """ 面板最大宽度 """
#         self.draw_list: List[draw.NormalDraw] = []
#         """ 绘制的文本列表 """
#         self.return_list: List[str] = []
#         """ 当前面板监听的按钮列表 """
#         character_data = cache.character_data[self.character_id]
#         for social_type in game_config.config_social_type:
#             if not social_type:
#                 continue
#             type_config = game_config.config_social_type[social_type]
#             type_draw = draw.LittleTitleLineDraw(type_config.name, self.width, ":")
#             self.draw_list.append(type_draw)
#             now_draw = draw.CenterDraw()
#             if social_type in character_data.social_contact and len(
#                 character_data.social_contact[social_type]
#             ):
#                 character_list = list(character_data.social_contact[social_type])
#                 now_draw = panel.PageHandlePanel(
#                     character_list, SeeCharacterInfoByNameDraw, 10, 5, self.width, 1, 1, 0
#                 )
#             else:
#                 now_draw.text = _("空无一人")
#                 now_draw.width = self.width
#             self.draw_list.append(now_draw)
#             self.draw_list.append(line_feed)

#     def draw(self):
#         title_draw = draw.TitleLineDraw(_("人物社交"), self.width)
#         title_draw.draw()
#         self.return_list = []
#         now_start_id = 0
#         for value in self.draw_list:
#             if isinstance(value, panel.PageHandlePanel):
#                 value.button_start_id = now_start_id
#                 value.update()
#                 value.draw()
#                 self.return_list.extend(value.return_list)
#                 now_start_id = len(self.return_list)
#             else:
#                 value.draw()


class SeeCharacterInfoByNameDraw:
    """
    点击后可查看角色属性的角色名字按钮对象
    Keyword arguments:
    text -- 角色id
    width -- 最大宽度
    is_button -- 绘制按钮
    num_button -- 绘制数字按钮
    button_id -- 数字按钮的id
    """

    def __init__(self, text: str, width: int, is_button: bool, num_button: bool, button_id: int):
        """初始化绘制对象"""
        self.character_id: int = int(text)
        """ 角色id """
        self.draw_text: str = ""
        """ 角色名绘制文本 """
        self.width: int = width
        """ 最大宽度 """
        self.is_button: bool = is_button
        """ 绘制按钮 """
        self.num_button: bool = num_button
        """ 绘制数字按钮 """
        self.button_id: int = button_id
        """ 数字按钮的id """
        self.button_return: str = str(button_id)
        """ 按钮返回值 """
        character_data = cache.character_data[self.character_id]
        character_name = character_data.name
        name_draw = draw.NormalDraw()
        if is_button:
            if num_button:
                index_text = text_handle.id_index(button_id)
                button_text = f"{index_text} {character_name}"
                name_draw = draw.CenterButton(
                    button_text, self.button_return, self.width, cmd_func=self.see_character
                )
            else:
                button_text = f"[{character_name}]"
                name_draw = draw.CenterButton(
                    button_text, character_name, self.width, cmd_func=self.see_character
                )
                self.button_return = character_name
            self.draw_text = button_text
        else:
            character_name = f"[{character_name}]"
            character_name = text_handle.align(character_name, "center", 0, 1, self.width)
            name_draw.text = character_name
            self.draw_text = character_name
        name_draw.width = self.width
        self.now_draw = name_draw
        """ 绘制的对象 """

    def draw(self):
        """绘制对象"""
        self.now_draw.draw()

    def see_character(self):
        """绘制角色信息"""
        py_cmd.clr_cmd()
        now_draw = SeeCharacterInfoOnSocialPanel(self.character_id, window_width)
        now_draw.draw()


class SeeCharacterInfoByNameDrawInScene:
    """场景中点击后切换目标角色的角色名字按钮对象"""

    def __init__(self, text: str, width: int, is_button: bool, num_button: bool, button_id: int):
        """初始化绘制对象"""
        self.character_id: int = int(text)
        """ 角色id """
        self.draw_text: str = ""
        """ 角色名绘制文本 """
        self.width: int = width
        """ 最大宽度 """
        self.is_button: bool = is_button
        """ 绘制按钮 """
        self.num_button: bool = num_button
        """ 绘制数字按钮 """
        self.button_id: int = button_id
        """ 数字按钮的id """
        self.button_return: str = str(button_id)
        """ 按钮返回值 """
        character_data: game_type.Character = cache.character_data[self.character_id]
        sex_text = game_config.config_sex_tem[character_data.sex].name
        character_name = character_data.name
        # character_name = character_data.name + f"({sex_text})"
        name_draw = draw.NormalDraw()
        if is_button:
            if num_button:
                index_text = text_handle.id_index(button_id)
                button_text = f"{index_text} {character_name}"
                name_draw = draw.CenterButton(
                    button_text, self.button_return, self.width, cmd_func=self.see_character
                )
            else:
                button_text = f"[{character_name}]"
                name_draw = draw.CenterButton(
                    button_text, character_name, self.width, cmd_func=self.see_character
                )
                self.button_return = character_name
            self.draw_text = button_text
        else:
            character_name = f"[{character_name}]"
            character_name = text_handle.align(character_name, "center", 0, 1, self.width)
            name_draw.text = character_name
            self.draw_text = character_name
        name_draw.width = self.width
        self.now_draw = name_draw
        """ 绘制的对象 """

    def draw(self):
        """绘制对象"""
        if isinstance(self.now_draw, draw.NormalDraw):
            self.now_draw.style = "onbutton"
        self.now_draw.draw()

    def see_character(self):
        """切换目标角色"""
        cache.character_data[0].target_character_id = self.character_id
        py_cmd.clr_cmd()


class SeeCharacterInfoByimageDrawInScene:
    """场景中点击后切换目标角色的角色立绘按钮对象"""

    def __init__(self, text: str, width: int, is_button: bool, num_button: bool, button_id: int):
        """初始化绘制对象"""
        self.character_id: int = int(text)
        """ 角色id """
        self.draw_text: str = ""
        """ 角色名绘制文本 """
        self.width: int = width
        """ 最大宽度 """
        self.is_button: bool = is_button
        """ 绘制按钮 """
        self.num_button: bool = num_button
        """ 绘制数字按钮 """
        self.button_id: int = button_id
        """ 数字按钮的id """
        self.button_return: str = str(button_id)
        """ 按钮返回值 """
        character_data: game_type.Character = cache.character_data[self.character_id]
        # sex_text = game_config.config_sex_tem[character_data.sex].name
        character_name = character_data.name
        # character_name = character_data.name + f"({sex_text})"
        button_text = f"{character_name}"
        name_draw = draw.ImageButton(
            button_text, self.button_return, self.width, cmd_func=self.see_character
        )
        character_name = f"[{character_name}]"
        character_name = text_handle.align(character_name, "center", 0, 1, self.width)
        name_draw.text = character_name
        self.draw_text = character_name
        name_draw.width = self.width
        self.now_draw = name_draw
        """ 绘制的对象 """

    def draw(self):
        """绘制对象"""
        if isinstance(self.now_draw, draw.NormalDraw):
            self.now_draw.style = "onbutton"
        self.now_draw.draw()

    def see_character(self):
        """切换目标角色"""
        cache.character_data[0].target_character_id = self.character_id
        py_cmd.clr_cmd()


class SeeCharacterInfoOnSocialPanel:
    """
    在社交面板里查看角色属性
    Keyword arguments:
    character_id -- 角色id
    width -- 最大宽度
    """

    def __init__(self, character_id: int, width: int):
        """初始化绘制对象"""
        self.character_id: int = character_id
        """ 要绘制的角色id """
        self.width: int = width
        """ 面板最大宽度 """
        self.return_list: List[str] = []
        """ 当前面板监听的按钮列表 """
        self.now_draw: SeeCharacterInfoPanel = SeeCharacterInfoHandle(
            character_id, width, list(cache.character_data.keys())
        )
        """ 角色属性面板 """

    def draw(self):
        """绘制面板"""
        line_feed.draw()
        self.now_draw.draw()


class SeeCharacterInfoHandle:
    """
    带切换控制的查看角色属性面板
    Keyword arguments:
    character_id -- 角色id
    width -- 最大宽度
    character_list -- 角色id列表
    """

    def __init__(self, character_id: int, width: int, character_list: List[int]):
        """初始化绘制对象"""
        self.character_id: int = character_id
        """ 要绘制的角色id """
        self.width: int = width
        """ 面板最大宽度 """
        self.return_list: List[str] = []
        """ 当前面板监听的按钮列表 """
        self.character_list: List[int] = character_list
        """ 当前面板所属的角色id列表 """

    def draw(self):
        """绘制面板"""
        old_button_draw = draw.CenterButton(
            _("[上一人]"), _("上一人"), self.width / 3, cmd_func=self.old_character
        )
        next_button_draw = draw.CenterButton(
            _("[下一人]"), _("下一人"), self.width / 3, cmd_func=self.next_character
        )
        back_draw = draw.CenterButton(_("[返回]"), _("返回"), self.width / 3)
        now_panel_id = _("基础属性")
        while 1:
            self.return_list = []
            now_character_panel = SeeCharacterInfoPanel(self.character_id, self.width)
            now_character_panel.change_panel(now_panel_id)
            now_character_panel.draw()
            line_feed.draw()
            old_button_draw.draw()
            back_draw.draw()
            next_button_draw.draw()
            line_feed.draw()
            self.return_list.extend(now_character_panel.return_list)
            self.return_list.append(old_button_draw.return_text)
            self.return_list.append(back_draw.return_text)
            self.return_list.append(next_button_draw.return_text)
            yrn = flow_handle.askfor_all(self.return_list)
            py_cmd.clr_cmd()
            line_feed.draw()
            if yrn == back_draw.return_text:
                break
            elif yrn in now_character_panel.draw_data:
                now_panel_id = yrn

    def old_character(self):
        """切换显示上一人"""
        now_index = self.character_list.index(self.character_id)
        self.character_id = self.character_list[now_index - 1]

    def next_character(self):
        """切换显示下一人"""
        now_index = self.character_list.index(self.character_id) + 1
        if now_index > len(self.character_list) - 1:
            now_index = 0
        self.character_id = self.character_list[now_index]


class SeeCharacterInfoHandleInScene(SeeCharacterInfoHandle):
    """在场景中带切换控制的查看角色属性面板"""

    def old_character(self):
        """切换显示上一人"""
        if len(self.character_list):
            if self.character_id:
                if self.character_id in self.character_list:
                    now_index = self.character_list.index(self.character_id)
                    if now_index:
                        now_index -= 1
                        self.character_id = self.character_list[now_index]
                    else:
                        self.character_id = 0
            else:
                self.character_id = self.character_list[len(self.character_list) - 1]

    def next_character(self):
        """切换显示下一人"""
        if len(self.character_list):
            if self.character_id:
                if self.character_id in self.character_list:
                    now_index = self.character_list.index(self.character_id)
                    if now_index == len(self.character_list) - 1:
                        self.character_id = 0
                    else:
                        self.character_id = self.character_list[now_index + 1]
            else:
                self.character_id = self.character_list[0]


class SeeCharacterInfoInScenePanel:
    """
    在场景中查看角色属性的控制对象
    Keyword arguments:
    target_id -- 目标id
    width -- 绘制宽度
    """

    def __init__(self, target_id: int, width: int):
        """初始化绘制对象"""
        self.target_id: int = target_id
        """ 查看属性的目标 """
        self.width: int = width
        """ 绘制宽度 """
        position = cache.character_data[0].position
        position_str = map_handle.get_map_system_path_str_for_list(position)
        scene_data: game_type.Scene = cache.scene_data[position_str]
        if cache.is_collection:
            character_data: game_type.Character = cache.character_data[0]
            now_list = [i for i in scene_data.character_list if i in character_data.collection_character]
        else:
            now_list = list(scene_data.character_list)
            now_list.remove(0)
        self.handle_panel = SeeCharacterInfoHandleInScene(target_id, width, now_list)
        """ 绘制控制面板 """

    def draw(self):
        """绘制对象"""
        self.handle_panel.draw()
        cache.now_panel_id = constant.Panel.IN_SCENE

