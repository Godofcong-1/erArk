from itertools import count
from Script.UI.Flow import creator_character_flow
from uuid import UUID
from typing import Tuple, List
from types import FunctionType
from Script.UI.Moudle import draw, panel
from Script.UI.Panel import see_clothing_info_panel, see_item_info_panel
from Script.Core import (
    cache_control,
    get_text,
    value_handle,
    game_type,
    text_handle,
    py_cmd,
    flow_handle,
    constant,
)
from Script.Config import game_config, normal_config
from Script.Design import attr_text, map_handle, attr_calculation

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
        self.now_panel: str = _("属性（第一页）")
        """ 当前的属性页id """
        self.character_id: int = character_id
        """ 要绘制的角色id """
        self.return_list: List[str] = []
        """ 当前面板监听的按钮列表 """
        main_first_draw = SeeCharacterFirstPanel(character_id, width)
        main_second_draw = SeeCharacterSecondPanel(character_id, width)
        main_attr_draw = SeeCharacterMainAttrPanel(character_id, width)
        # see_status_draw = SeeCharacterStatusPanel(character_id, width, 5, 0)
        # see_clothing_draw = see_clothing_info_panel.SeeCharacterPutOnClothingListPanel(character_id, width)
        # see_item_draw = see_item_info_panel.SeeCharacterItemBagPanel(character_id, width)
        # see_knowledge_draw = SeeCharacterKnowledgePanel(character_id, width)
        # see_language_draw = SeeCharacterLanguagePanel(character_id, width)
        # see_nature_draw = SeeCharacterNaturePanel(character_id, width)
        # see_social_draw = SeeCharacterSocialContact(character_id, width)
        self.draw_data = {
            _("属性（第一页）"): main_first_draw,
            _("属性（第二页）"): main_second_draw,
            _("属性（原）"): main_attr_draw,
            # _("状态"): see_status_draw,
            # _("服装"): see_clothing_draw,
            # _("道具"): see_item_draw,
            # _("技能"): see_knowledge_draw,
            # _("语言"): see_language_draw,
            # _("性格"): see_nature_draw,
            # _("社交"): see_social_draw,
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
        self.draw_data[self.now_panel].draw()
        self.return_list = []
        self.return_list.extend(self.draw_data[self.now_panel].return_list)
        line_feed.draw()
        line = draw.LineDraw("=", self.width)
        line.draw()
        self.handle_panel.draw()
        self.return_list.extend(self.handle_panel.return_list)


class SeeCharacterFirstPanel:
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
        Talent_draw = CharacterTalentText(character_id, width,8, 0)
        abi_draw = CharacterabiText(character_id, width)
        self.draw_list: List[draw.NormalDraw] = [
            head_draw,
            image_draw,
            Talent_draw,
            abi_draw,
        ]
        """ 绘制的面板列表 """
        self.return_list: List[str] = []
        """ 当前面板监听的按钮列表 """

    def draw(self):
        """绘制面板"""
        for label in self.draw_list:
            label.draw()

class SeeCharacterSecondPanel:
    """
    显示角色属性面板第二页对象
    Keyword arguments:
    character_id -- 角色id
    width -- 绘制宽度
    """

    def __init__(self, character_id: int, width: int):
        """初始化绘制对象"""
        head_draw = CharacterInfoHead(character_id, width)
        experience_draw = CharacterExperienceText(character_id, width,8, 0)
        juel_draw = CharacterJuelText(character_id, width,8, 0)
        self.draw_list: List[draw.NormalDraw] = [
            head_draw,
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
        stature_draw = CharacterStatureText(character_id, width)
        room_draw = CharacterRoomText(character_id, width)
        birthday_draw = CharacterBirthdayText(character_id, width)
        sture_info_draw = CharacterStatureInfoText(character_id, width)
        measurement_draw = CharacterMeasurementsText(character_id, width)
        sex_experience_draw = CharacterSexExperienceText(character_id, width)
        self.draw_list: List[draw.NormalDraw] = [
            head_draw,
            stature_draw,
            room_draw,
            birthday_draw,
            sture_info_draw,
            measurement_draw,
            sex_experience_draw,
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
        for status_type in game_config.config_character_state_type_data:
            if status_type == type_number:
                type_data = game_config.config_character_state_type[status_type]
                type_line = draw.LittleTitleLineDraw(type_data.name, width, ":")
                # print("type_data.name :",type_data.name)
                self.draw_list.append(type_line)
                type_set = game_config.config_character_state_type_data[status_type]
                status_text_list = []
                for status_id in type_set:
                    # print("status_type :",status_type)
                    # print("status_id :",status_id)
                    # print("game_config.config_character_state[status_id] :",game_config.config_character_state[status_id])
                    # print("game_config.config_character_state[status_id].name :",game_config.config_character_state[status_id].name)
                    if status_type == 0:
                        if character_data.sex == 0:
                            if status_id in {2, 3, 7, 8}:
                                continue
                        elif character_data.sex == 1:
                            if status_id == 5:
                                continue
                    status_text = game_config.config_character_state[status_id].name
                    status_value = 0
                    if status_id in character_data.status:
                        status_value = character_data.status[status_id]
                    # if status_id in character_data.status:
                    #     status_value = character_data.status[status_id]
                    status_value = round(status_value)
                    status_value = int(attr_text.get_value_text(status_value))
                    status_level = attr_calculation.get_status_level(status_value)
                    now_text = f"  {status_text}:lv{status_level} {status_value}"
                    # print("status_value :",status_value)
                    status_text_list.append(now_text)
                    # print("status_text_list :",status_text_list)
                if self.center_status:
                    now_draw = panel.CenterDrawTextListPanel()
                else:
                    now_draw = panel.LeftDrawTextListPanel()
                now_draw.set(status_text_list, self.width, self.column)
                self.draw_list.extend(now_draw.draw_list)

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
        self.draw_title: bool = True
        """ 是否绘制面板标题 """
        character_data: game_type.Character = cache.character_data[character_id]
        sex_text = game_config.config_sex_tem[character_data.sex].name
        if character_id:
            social = 0
            if 0 in character_data.social_contact_data:
                social = character_data.social_contact_data[0]
            social_text = game_config.config_social_type[social].name
            favorability = character_data.favorability
            # print("favorability =",favorability)
            message = _("{character_name}（好感度： {favorability}，信赖度： {trust}） ").format(
                # character_id=character_id,
                character_name=character_data.name,
                favorability=int(character_data.favorability[0]),
                trust=character_data.trust,
                # sex_text=sex_text,
                # social_text=social_text,
            )
        else:
            message = _(
                "{character_name}{character_nick_name}"
            ).format(
                # character_id=character_id,
                character_name=character_data.name,
                character_nick_name=character_data.nick_name,
                # sex_text=sex_text,
            )
        message_draw = draw.CenterDraw()
        message_draw.width = width / 4
        message_draw.text = message
        hp_draw = draw.InfoBarDraw()
        hp_draw.width = width / 4
        hp_draw.scale = 0.8
        hp_draw.set(
            "HitPointbar",
            int(character_data.hit_point_max),
            int(character_data.hit_point),
            _("体力"),
        )
        mp_draw = draw.InfoBarDraw()
        mp_draw.width = width / 4
        mp_draw.scale = 0.8
        mp_draw.set(
            "ManaPointbar",
            int(character_data.mana_point_max),
            int(character_data.mana_point),
            _("气力"),
        )
        status_text = game_config.config_status[character_data.state].name
        status_draw = draw.CenterDraw()
        status_draw.width = width / 4
        status_draw.text = _(" ").format(status_text=status_text)
        self.draw_list: List[Tuple[draw.NormalDraw, draw.NormalDraw]] = [
            (message_draw, hp_draw),
            (status_draw, mp_draw),
        ]
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


class CharacterWearClothingList:
    """
    角色已穿戴服装列表
    Keyword arguments:
    character_id -- 角色id
    width -- 最大宽度
    column -- 每行服装最大个数
    """

    def __init__(self, character_id: int, width: int, column: int):
        """初始化绘制对象"""
        self.character_id: int = character_id
        """ 要绘制的角色id """
        self.width: int = width
        """ 当前最大可绘制宽度 """
        self.column: int = column
        """ 每行服装最大个数 """
        character_data: game_type.Character = cache.character_data[character_id]
        describe_list = [_("可爱的"), _("性感的"), _("帅气的"), _("清新的"), _("典雅的"), _("清洁的"), _("保暖的")]
        clothing_info_list = []
        title_draw = draw.LittleTitleLineDraw(_("衣着"), width, ":")
        self.draw_list = [title_draw]
        """ 绘制的对象列表 """
        for clothing_type in game_config.config_clothing_type:
            if clothing_type in character_data.put_on and isinstance(
                character_data.put_on[clothing_type], UUID
            ):
                now_id = character_data.put_on[clothing_type]
                now_clothing: game_type.Clothing = character_data.clothing[clothing_type][now_id]
                value_list = [
                    now_clothing.sweet,
                    now_clothing.sexy,
                    now_clothing.handsome,
                    now_clothing.fresh,
                    now_clothing.elegant,
                    now_clothing.cleanliness,
                    now_clothing.warm,
                ]
                describe_id = value_list.index(max(value_list))
                describe = describe_list[describe_id]
                now_clothing_config = game_config.config_clothing_tem[now_clothing.tem_id]
                clothing_name = f"[{now_clothing.evaluation}{describe}{now_clothing_config.name}]"
                clothing_info_list.append(clothing_name)
        now_draw = panel.LeftDrawTextListPanel()
        now_draw.set(clothing_info_list, self.width, self.column)
        self.draw_list.extend(now_draw.draw_list)

    def draw(self):
        """绘制对象"""
        for draw_list in self.draw_list:
            for now_draw in draw_list:
                now_draw.draw()
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
        age_text = _("年龄:{character_age}岁").format(character_age=character_data.age)
        birthday_text = _("生日:{birthday_month}月{birthday_day}日").format(
            birthday_month=character_data.birthday.month, birthday_day=character_data.birthday.day
        )
        self.info_list = [age_text, birthday_text]
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
        self.draw_list: List[draw.NormalDraw()] = []
        """ 绘制对象列表 """
        sex_tem = character_data.sex in (0, 3)
        organ_list = game_config.config_organ_data[sex_tem] | game_config.config_organ_data[2]
        for organ in organ_list:
            if organ!= 8:
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

class CharacterabiText_1:
    """
    角色能力面板
    Keyword arguments:
    character_id -- 角色id
    width -- 最大宽度
    """

    def __init__(self, character_id: int, width: int, type: int, column: int):
        """初始化绘制对象"""
        self.character_id = character_id
        """ 绘制的角色id """
        self.width = width
        """ 当前最大可绘制宽度 """
        self.type = type
        """ 当前绘制类型 """
        self.column = column
        """ 每行状态最大个数 """
        character_data = cache.character_data[self.character_id]
        """ 能力数据 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制对象列表 """
        ability_list = game_config.config_ability_type_data
        # print("ability_list :",ability_list)
        for anility_type in ability_list:
        # if anility_type == type:
            type_data = game_config.config_ability_type[anility_type]
            type_line = draw.LittleTitleLineDraw(type_data.name, width, ":")
            self.draw_list.append(type_line)
            type_set = ability_list[anility_type]
            ability_text_list = []
            for ability_id in type_set:
                if anility_type == 0:
                    if character_data.sex == 0:
                        if ability_id in {2, 4, 6, 7}:
                            continue
                    elif character_data.sex == 1:
                        if ability_id == 3:
                            continue
                now_draw = draw.NormalDraw()
                now_draw_1 = draw.NormalDraw()
                now_draw_value = draw.NormalDraw()
                now_draw.text = game_config.config_ability[ability_id].name
                now_draw_1.text = " "
                now_draw_1.width = 1
                now_draw.width = width / len(type_set)
                now_exp = 0
                if anility_type in character_data.ability:
                    now_exp = character_data.ability[ability_id]
                now_draw_value.text = str(now_exp)
                # level_draw = draw.ExpLevelDraw(now_exp)
                level_draw = attr_calculation.judge_grade(now_exp)
                now_text = f"  {now_draw.text}:{level_draw} {now_exp}"
                ability_text_list.append(now_text)
            now_draw = panel.LeftDrawTextListPanel()
            now_draw.set(ability_text_list, self.width, self.column)
            self.draw_list.extend(now_draw.draw_list)
    def draw(self):
        """绘制对象"""
        line_feed.draw()
        line = draw.LineDraw(".", self.width)
        line.draw()
        for label in self.draw_list:
            if isinstance(label, list):
                for value in label:
                    value.draw()
                line_feed.draw()
            else:
                label.draw()

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
        """ 性器官感度描述 """
        self.draw_list: List[draw.NormalDraw()] = []
        """ 绘制对象列表 """
        self.title_list: List[draw.NormalDraw()] = []
        """ 绘制标题列表 """
        ability_list = game_config.config_ability_type_data
        title_text = "能力"
        type_line = draw.LittleTitleLineDraw(title_text, width, ":")
        self.draw_list.append(type_line)
        #进入能力大类#
        for anility_type in ability_list:
            # if anility_type == type:
            type_set = ability_list[anility_type]
            for ability_id in type_set:
                #去掉与性别不符的感度#
                if character_data.sex == 0:
                    if ability_id in {2, 4, 7, 9, 12, 34, 39}:
                        continue
                elif character_data.sex == 1:
                    if ability_id == 3:
                        continue
                now_draw = draw.NormalDraw()
                now_draw_value = draw.NormalDraw()
                now_draw.text = game_config.config_ability[ability_id].name
                #这个_1是为了补空格让格式对齐#
                now_draw_1 = draw.NormalDraw()
                now_draw_1.text = " "
                now_draw_1.width = 1
                now_draw.width = width / len(type_set)
                now_exp = 0
                now_exp = character_data.ability[ability_id]
                now_draw_value.text = str(now_exp)
                level_draw = draw.ExpLevelDraw(now_exp)
                new_draw = draw.LeftMergeDraw(width / 10)
                new_draw.draw_list.append(now_draw_1)
                new_draw.draw_list.append(now_draw)
                new_draw.draw_list.append(now_draw_1)
                #根据不同的类型补不同数量的空格#
                if anility_type != 2 and anility_type != 4 and anility_type != 6:
                    new_draw.draw_list.append(now_draw_1)
                    new_draw.draw_list.append(now_draw_1)
                    if anility_type == 3 or anility_type == 5:
                        new_draw.draw_list.append(now_draw_1)
                        new_draw.draw_list.append(now_draw_1)
                new_draw.draw_list.append(level_draw)
                new_draw.draw_list.append(now_draw_1)
                new_draw.draw_list.append(now_draw_value)
                self.draw_list.append(new_draw)
            #只有不是最后一个类型就补个换行#
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
        character_data = cache.character_data[self.character_id]
        """ 角色属性 """
        self.draw_list: List[draw.NormalDraw()] = []
        """ 绘制对象列表 """
        self.title_list: List[draw.NormalDraw()] = []
        """ 绘制标题列表 """
        title_text = "立绘"
        type_line = draw.LittleTitleLineDraw(title_text, width, ":")
        self.title_list.append(type_line)
        self.image_name=character_data.name
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
            flow_handle.print_image_cmd(self.image_name,"立绘按钮")

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
        type_data = "经验"
        type_line = draw.LittleTitleLineDraw(type_data, width, ":")
        self.draw_list.append(type_line)
        experience_text_list = []
        for experience_id in game_config.config_experience:            
            if character_data.sex == 0:
                if experience_id in {2, 4, 7, 12, 14, 17, 20, 22, 26, 51, 54, 55, 58, 72, 74 ,77, 86, 100, 101, 102, 103, 104, 105, 106}:
                    continue
            elif character_data.sex == 1:
                if experience_id == {3,13,21,73}:
                    continue
            experience_text = game_config.config_experience[experience_id].name
            experience_value = 0
            if experience_id in character_data.experience:
                experience_value = character_data.experience[experience_id]
                now_text = f" {experience_text}:{experience_value}"
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
        type_data = "素质"
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
                conut = 1
            race_type = type_data.name
            if talent_type == 0:
                message_race = f"\n {race_type}  ："
            else:
                message_race = f"\n {race_type}："
            for talent_id in type_set:
                talent_text = game_config.config_talent[talent_id].name
                if talent_id in character_data.talent:
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
        type_data = "宝珠"
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



class SeeCharacterKnowledgePanel:
    """
    查看角色技能面板
    Keyword arguments:
    character_id -- 角色id
    width -- 绘制宽度
    """

    def __init__(self, character_id: int, width: int):
        """初始化绘制对象"""
        self.character_id = character_id
        """ 要绘制的角色id """
        self.width = width
        """ 面板最大宽度 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """
        self.return_list: List[str] = []
        """ 当前面板监听的按钮列表 """
        character_data = cache.character_data[character_id]
        for skill_type in game_config.config_knowledge_type_data:
            skill_set = game_config.config_knowledge_type_data[skill_type]
            type_config = game_config.config_knowledge_type[skill_type]
            type_draw = draw.LittleTitleLineDraw(type_config.name, self.width, ":")
            self.draw_list.append(type_draw)
            now_list = []
            skill_group = value_handle.list_of_groups(list(skill_set), 3)
            for skill_list in skill_group:
                for skill in skill_list:
                    skill_config = game_config.config_knowledge[skill]
                    skill_draw = draw.CenterMergeDraw(int(self.width / len(skill_group)))
                    now_text_draw = draw.NormalDraw()
                    now_text_draw.text = skill_config.name
                    now_text_draw.width = text_handle.get_text_index(skill_config.name)
                    now_exp = 0
                    if skill in character_data.knowledge:
                        now_exp = character_data.knowledge[skill]
                    now_level_draw = draw.ExpLevelDraw(now_exp)
                    skill_draw.draw_list.append(now_text_draw)
                    skill_draw.draw_list.append(now_level_draw)
                    skill_draw.width = int(self.width / len(skill_group))
                    now_list.append(skill_draw)
            self.draw_list.append(now_list)

    def draw(self):
        """绘制对象"""
        title_draw = draw.TitleLineDraw(_("人物技能"), self.width)
        title_draw.draw()
        for value in self.draw_list:
            if isinstance(value, list):
                now_draw = panel.VerticalDrawTextListGroup(self.width)
                now_group = value_handle.list_of_groups(value, 3)
                now_draw.draw_list = now_group
                now_draw.draw()
            else:
                value.draw()


class SeeCharacterLanguagePanel:
    """
    查看角色语言面板
    Keyword arguments:
    character_id -- 角色id
    width -- 绘制宽度
    """

    def __init__(self, character_id: int, width: int):
        """初始化绘制对象"""
        self.character_id: int = character_id
        """ 要绘制的角色id """
        self.width: int = width
        """ 面板最大宽度 """
        self.return_list: List[str] = []
        """ 当前面板监听的按钮列表 """
        character_data = cache.character_data[character_id]
        language_list = list(game_config.config_language.keys())
        language_text_list = []
        for language in language_list:
            now_exp = 0
            if language in character_data.language:
                now_exp = character_data.language[language]
            language_text_list.append((language, now_exp))
        self.handle_panel = panel.PageHandlePanel(
            language_text_list, LanguageNameDraw, 20, 6, width, 1, 1, 0, ""
        )
        """ 页面控制对象 """

    def draw(self):
        title_draw = draw.TitleLineDraw(_("人物语言"), self.width)
        title_draw.draw()
        self.handle_panel.update()
        self.handle_panel.draw()
        self.return_list = self.handle_panel.return_list


class LanguageNameDraw:
    """
    按语言id绘制语言名
    Keyword arguments:
    text -- 语言的配置数据 tuple[语言id,经验]
    width -- 最大宽度
    is_button -- 绘制按钮
    num_button -- 绘制数字按钮
    button_id -- 数字按钮的id
    """

    def __init__(self, text: str, width: int, is_button: bool, num_button: bool, button_id: int):
        """初始化绘制对象"""
        self.language_id: int = text[0]
        """ 语言id """
        self.language_exp: int = text[1]
        """ 语言经验 """
        self.draw_text: str = ""
        """ 语言名绘制文本 """
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
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的对象列表 """
        language_config = game_config.config_language[self.language_id]
        language_name = language_config.name
        name_draw = draw.NormalDraw()
        name_draw.width = self.width
        if is_button:
            button_text = ""
            if num_button:
                index_text = text_handle.id_index(button_id)
                button_text = f"{index_text} {language_name}:"
                name_draw = draw.Button(button_text, self.button_return, cmd_func=self.see_language_info)
            else:
                button_text = f"{language_name}:"
                name_draw = draw.Button(button_text, language_name, cmd_func=self.see_language_info)
                self.button_return = language_name
        else:
            name_draw.text = f"{language_name}:"
        level_draw = draw.ExpLevelDraw(self.language_exp)
        name_draw.width = self.width - len(level_draw)
        self.draw_list = [name_draw, level_draw]

    def draw(self):
        """绘制对象"""
        now_draw = draw.CenterMergeDraw(self.width)
        now_draw.draw_list = self.draw_list
        now_draw.draw()

    def see_language_info(self):
        """绘制语言描述信息"""
        now_draw = LanguageInfoDraw(self.language_id, window_width)
        now_draw.draw()


class LanguageInfoDraw:
    """
    按语言id绘制语言数据
    Keyword arguments:
    cid -- 语言id
    width -- 最大绘制宽度
    """

    def __init__(self, cid: int, width: int):
        """绘制语言信息"""
        self.cid: int = int(cid)
        """ 语言的配表id """
        self.width: int = width
        """ 最大宽度 """

    def draw(self):
        """绘制道具信息"""
        py_cmd.clr_cmd()
        language_config = game_config.config_language[self.cid]
        language_draw = draw.WaitDraw()
        language_draw.text = f"{language_config.name}:{language_config.info}\n"
        language_draw.width = self.width
        language_draw.draw()


class SeeCharacterNaturePanel:
    """
    显示角色性格面板对象
    Keyword arguments:
    character_id -- 角色id
    width -- 绘制宽度
    """

    def __init__(self, character_id: int, width: int):
        """初始化绘制对象"""
        self.character_id: int = character_id
        """ 要绘制的角色id """
        self.width: int = width
        """ 面板最大宽度 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """
        self.return_list: List[str] = []
        """ 当前面板监听的按钮列表 """
        character_data = cache.character_data[character_id]
        for nature_type in game_config.config_nature_tag:
            type_config = game_config.config_nature_tag[nature_type]
            nature_set = game_config.config_nature_tag_data[nature_type]
            type_value = 0
            nature_draw_list = []
            nature_group = value_handle.list_of_groups(list(nature_set), 1)
            for nature_list in nature_group:
                for nature_id in nature_list:
                    nature_config = game_config.config_nature[nature_id]
                    nature_value = 0
                    if nature_id in character_data.nature:
                        nature_value = character_data.nature[nature_id]
                    type_value += nature_value
                    good_judge = False
                    if nature_value >= 50:
                        good_judge = True
                    nature_draw = draw.CenterDraw()
                    if good_judge:
                        nature_draw.text = nature_config.good
                    else:
                        nature_draw.text = nature_config.bad
                    nature_draw.width = int(self.width / len(nature_group))
                    nature_draw_list.append(nature_draw)
            judge_value = len(nature_set) * 100 / 2
            nature_type_text = ""
            if type_value >= judge_value:
                nature_type_text = type_config.good
            else:
                nature_type_text = type_config.bad
            nature_draw = draw.LittleTitleLineDraw(nature_type_text, self.width, ":")
            self.draw_list.append(nature_draw)
            self.draw_list.append(nature_draw_list)

    def draw(self):
        """绘制对象"""
        title_draw = draw.TitleLineDraw(_("人物性格"), self.width)
        title_draw.draw()
        for value in self.draw_list:
            if isinstance(value, list):
                now_draw = panel.VerticalDrawTextListGroup(self.width)
                now_group = value_handle.list_of_groups(value, 1)
                now_draw.draw_list = now_group
                now_draw.draw()
            else:
                value.draw()


class SeeCharacterSocialContact:
    """
    显示角色社交关系面板对象
    Keyword arguments:
    character_id -- 角色id
    width -- 绘制宽度
    """

    def __init__(self, character_id: int, width: int):
        """初始化绘制对象"""
        self.character_id: int = character_id
        """ 要绘制的角色id """
        self.width: int = width
        """ 面板最大宽度 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """
        self.return_list: List[str] = []
        """ 当前面板监听的按钮列表 """
        character_data = cache.character_data[self.character_id]
        for social_type in game_config.config_social_type:
            if not social_type:
                continue
            type_config = game_config.config_social_type[social_type]
            type_draw = draw.LittleTitleLineDraw(type_config.name, self.width, ":")
            self.draw_list.append(type_draw)
            now_draw = draw.CenterDraw()
            if social_type in character_data.social_contact and len(
                character_data.social_contact[social_type]
            ):
                character_list = list(character_data.social_contact[social_type])
                now_draw = panel.PageHandlePanel(
                    character_list, SeeCharacterInfoByNameDraw, 10, 5, self.width, 1, 1, 0
                )
            else:
                now_draw.text = _("空无一人")
                now_draw.width = self.width
            self.draw_list.append(now_draw)
            self.draw_list.append(line_feed)

    def draw(self):
        title_draw = draw.TitleLineDraw(_("人物社交"), self.width)
        title_draw.draw()
        self.return_list = []
        now_start_id = 0
        for value in self.draw_list:
            if isinstance(value, panel.PageHandlePanel):
                value.button_start_id = now_start_id
                value.update()
                value.draw()
                self.return_list.extend(value.return_list)
                now_start_id = len(self.return_list)
            else:
                value.draw()


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
        now_panel_id = _("属性（第一页）")
        while 1:
            self.return_list = []
            now_character_panel = SeeCharacterInfoPanel(self.character_id, self.width)
            now_character_panel.change_panel(now_panel_id)
            now_character_panel.draw()
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


class GetUpCharacterInfoDraw:
    """
    起床面板按角色id绘制角色缩略信息
    Keyword arguments:
    text -- 角色id
    width -- 最大宽度
    is_button -- 绘制按钮
    num_button -- 绘制数字按钮
    button_id -- 数字按钮的id
    """

    def __init__(self, text: int, width: int, is_button: bool, num_button: bool, button_id: int):
        """初始化绘制对象"""
        self.text: int = text
        """ 角色id """
        self.draw_text: str = ""
        """ 角色缩略信息绘制文本 """
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
        character_data = cache.character_data[self.text]
        character_name = character_data.name
        # id_text = f"No.{self.text}"
        sex_config = game_config.config_sex_tem[character_data.sex]
        # sex_text = _(f"性别:{sex_config.name}")
        # age_text = _(f"年龄:{character_data.age}岁")
        hit_point_text = _(f"体力:({character_data.hit_point}/{character_data.hit_point_max})")
        mana_point_text = _(f"气力:({character_data.mana_point}/{character_data.mana_point_max})")
        now_text = f" {character_name} {hit_point_text} {mana_point_text}"
        if is_button:
            if num_button:
                index_text = text_handle.id_index(self.button_id)
                now_text_width = self.width - len(index_text)
                new_text = text_handle.align(now_text, "center", text_width=now_text_width)
                self.draw_text = f"{index_text}{new_text}"
                self.button_return = str(button_id)
            else:
                new_text = text_handle.align(now_text, "center", text_width=self.width)
                self.draw_text = new_text
                self.button_return = character_name
        else:
            new_text = text_handle.align(now_text, "center", text_width=self.width)
            self.draw_text = new_text

    def draw(self):
        """绘制对象"""
        if self.is_button:
            now_draw = draw.Button(self.draw_text, self.button_return, cmd_func=self.draw_character_info)
        else:
            now_draw = draw.NormalDraw()
            now_draw.text = self.draw_text
        now_draw.width = self.width
        now_draw.draw()

    def draw_character_info(self):
        """绘制角色信息"""
        line_feed.draw()
        py_cmd.clr_cmd()
        now_draw = SeeCharacterInfoHandle(self.text, window_width, list(cache.character_data.keys()))
        now_draw.draw()


class SeeCharacterInfoHandleInScene(SeeCharacterInfoHandle):
    """在场景中带切换控制的查看角色属性面板"""

    def old_character(self):
        """切换显示上一人"""
        if len(self.character_list):
            if self.character_id:
                now_index = self.character_list.index(self.character_id)
                if now_index:
                    now_index -= 1
                    self.character_id = self.character_list[now_index]
                else:
                    self.character_id = 0
            else:
                self.character_id = self.character_list[len(self.character_list) - 1]

    def next_character(self):
        """切换显示上一人"""
        if len(self.character_list):
            if self.character_id:
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
