import random
from functools import wraps
from typing import List
from types import FunctionType
from Script.Core import get_text, constant, game_type, cache_control, flow_handle, py_cmd, io_init

from Script.Design import (
    handle_panel,
    character,
    character_handle,
    attr_calculation,
    basement,
)
from Script.UI.Moudle import panel, draw
from Script.Config import normal_config, game_config

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """
width = normal_config.config_normal.text_width
""" 屏幕宽度 """
line_feed_draw = draw.NormalDraw()
""" 绘制换行对象 """
line_feed_draw.text = "\n"
line = draw.LineDraw("=", width)
""" 标题线绘制对象 """


@handle_panel.add_panel(constant.Panel.CREATOR_CHARACTER)
def creator_character_panel():
    """创建角色面板"""
    cache.character_data[0] = game_type.Character()
    character_handle.init_character_list()
    while 1:
        confirm_game_info_panel()
        if input_name_panel():
            character.init_attr(0)
            # game_start()
            cache.rhodes_island = basement.get_base_zero()
            first_bonus_and_setting_updata()
            character_handle.first_NPC_work()
            io_init.init_style() # 刷新NPC的文本字体颜色
            if confirm_character_attr_panel():
                game_start()
                break
        cache.character_data[0] = game_type.Character()
    cache.now_panel_id = constant.Panel.IN_SCENE

def first_bonus_and_setting_updata():
    """刷新初始奖励和设定"""
    cache = cache_control.cache
    for cid in game_config.config_first_bonus:
        cache.first_bonus[cid] = False
    for cid in game_config.config_world_setting:
        cache.world_setting[cid] = 0
    cache.all_system_setting = attr_calculation.get_system_setting_zero()
    # 初始资源
    cache.rhodes_island.materials_resouce[1] = 20000
    cache.rhodes_island.materials_resouce[11] = 20
    # 体检设置
    cache.rhodes_island.physical_examination_setting = attr_calculation.get_physical_exam_setting_zero()

def game_start():
    """初始化游戏数据"""
    cache = cache_control.cache
    from Script.Design import cooking

    character_handle.init_character_dormitory()
    character_handle.init_character_position()
    character_handle.init_character_facility_open()
    character_handle.handle_character_setting()
    cooking.init_recipes()
    cooking.init_food_shop_data(new_day_flag=True)
    cache.all_system_setting = attr_calculation.get_system_setting_zero()
    cache.country = attr_calculation.get_country_reset(cache.country)
    basement.get_base_updata()
    character_handle.init_character_entertainment() # 需要设施开放的属性，所以放在设施后面
    # print(f"debug 2facility_open = {cache.base_resouce.facility_open}")

def confirm_game_info_panel():
    """确认游戏说明面板"""
    now_line = draw.LineDraw("-", width)
    now_line.draw()
    info_text = _("\n\n  免责声明：1.本游戏仅为开发者自娱自乐及代码练习所用，开发它是因为开发者趣味低下，思想低俗所致，无任何经济收益和利益驱动。\n\n\n            2.本游戏含有大量的R18色情内容，内容中可能会出现的有：多P、调教、轻度SM、非合意性行为、近亲相奸等，不会出现的有：NTR、重度SM、血腥、R18G等。\n\n\n            3.本游戏在设计理念和游戏内容上缝合了大量era与其他各类作品，仅适合era系列玩家或文字黄油爱好者进行游玩，不适合普通玩家游玩，特别是严格禁止未成年人游玩。\n\n\n            4.本游戏所使用的素材资源包括开发者自制、互联网收集与协力者提供，开发者与协力者来自于不同的国家和民族，彼此之间也不存在经济关系。\n\n\n            5.本游戏目前没有官方的公开发布地址，且因为游戏本身的性质，禁止在任何未成年人可以接触到的场合展示或传播本游戏，更禁止任何人通过任何方式使用本游戏进行盈利。\n\n\n            6.本游戏完全开源，在明确注明或保留游戏来源、不涉及任何商业目的和经济收益、并同样遵守本免责声明的情况下，允许他人与社区基于本游戏进行修改或二次开发。该授权将直接赋予本游戏的所有玩家，不需要专门征求开发者的明确同意。\n\n\n            7.本声明的解释权归开发者所有，且在版本更新中声明内容可能有所变更，请以最新版本为准。\n\n\n            8.基于以上叠了这么多层buff，建议有大胆想法的人请现在关掉窗口并立刻删除该游戏，只要不删就默认你已经理解并遵守该声明，在不遵守的情况下出现的任何事故和法律责任都和开发者没有任何关系。\n\n\n")
    askfor_list = [_("我读完并理解了以上8条，我对自己负责，我不删，我要玩")]
    askfor_panel = panel.OneMessageAndSingleColumnButton()
    askfor_panel.set(askfor_list, info_text, 0)
    while 1:
        askfor_panel.draw()
        askfor_panel_return_list = askfor_panel.get_return_list()
        ask_list = []
        ask_list.extend(askfor_panel_return_list.keys())
        yrn = flow_handle.askfor_all(ask_list)
        py_cmd.clr_cmd()
        if yrn in askfor_panel_return_list:
            break

def confirm_character_attr_panel():
    """确认角色属性面板"""
    # now_attr_panel = see_character_info_panel.SeeCharacterInfoPanel(0, width)
    askfor_panel = panel.OneMessageAndSingleColumnButton()
    while 1:
        line_feed_draw.draw()
        now_attr_panel = Character_creat_Handle()
        now_attr_panel.draw()
        ask_list = []
        ask_list.extend(now_attr_panel.return_list)
        line_feed_draw.draw()
        now_line = draw.LineDraw("~", width)
        now_line.draw()
        askfor_list = [_("睁开双眼"), _("重新设定")]
        start_id = 0
        now_id_judge = 0
        now_id_list = []
        for now_id in ask_list:
            if now_id.isdigit():
                now_id_judge = 1
                now_id_list.append(int(now_id))
        if now_id_judge:
            start_id = max(now_id_list) + 1
        askfor_panel.set(askfor_list, _("这样可以吗?"), start_id)
        askfor_panel.draw()
        askfor_panel_return_list = askfor_panel.get_return_list()
        ask_list.extend(askfor_panel_return_list.keys())
        yrn = flow_handle.askfor_all(ask_list)
        py_cmd.clr_cmd()
        if yrn in askfor_panel_return_list:
            return askfor_panel_return_list[yrn] == askfor_list[0]


def input_name_panel() -> bool:
    """
    输入角色名面板
    Return arguments:
    bool -- 完成角色创建校验
    """
    character_data = cache.character_data[0]
    character_data.name = character.input_name_func(_("你能回忆起自己的名字吗？（默认称呼为博士，此处仅输入姓名即可）"))
    character_data.nick_name = _("博士")
    return 1


class Character_creat_Handle:
    """
    角色创建页面对象
    Keyword arguments:
    """

    def __init__(self):
        """初始化绘制对象"""
        from Script.UI.Panel import see_character_info_panel

        self.width = normal_config.config_normal.text_width
        info_draw = see_character_info_panel.CharacterInfoHead(0, width)
        info_draw.draw_title = False
        sex_draw = Character_Sex(self.width)
        jj_draw = Character_JJ(self.width)
        debug_draw = Character_Debug(self.width)
        firstNpc_draw = Character_FirstNPC(self.width)
        bonus_draw = Character_Bonus(self.width)
        world_setting_draw = World_Setting(self.width)
        other_settings_draw = Other_Settings(self.width)
        # abi_draw = see_character_info_panel.CharacterabiText(0, width)
        # tal_draw = see_character_info_panel.CharacterTalentText(0, width, 8, 0)
        self.draw_list: List[draw.NormalDraw] = [
            info_draw,
            # sex_draw,
            jj_draw,
            debug_draw,
            firstNpc_draw,
            bonus_draw,
            world_setting_draw,
            other_settings_draw,
            # abi_draw,
            # tal_draw,
        ]
        """ 绘制的面板列表 """
        self.return_list: List[str] = []
        """ 当前面板监听的按钮列表 """

    def draw(self):
        """绘制面板"""
        line_feed_draw.draw()
        title_draw = draw.TitleLineDraw(_("详细设定"), self.width)
        title_draw.draw()
        for label in self.draw_list:
            label.draw()
            if "return_list" in label.__dict__:
                self.return_list.extend(label.return_list)



class Character_Sex:
    """
    角色性别面板
    Keyword arguments:
    character_id -- 角色id
    width -- 最大宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 当前最大可绘制宽度 """
        self.return_list: List[str] = []
        """ 监听的按钮列表 """

        character_data: game_type.Character = cache.character_data[0]
        sex_text = game_config.config_sex_tem[character_data.sex].name
        now_draw = panel.LeftDrawTextListPanel()

        sex_draw = draw.LeftDraw()
        # sex_draw.width = 1
        sex_draw.text = _("\n 性别：{0}      ").format(sex_text)
        now_draw.draw_list.append(sex_draw)
        now_draw.width += len(sex_draw.text)

        button_text = _("    [改变性别]")
        sex_button_draw = draw.LeftButton(
            _(button_text),
            _('改变性别'),
            self.width /10,
            cmd_func=self.change)
        self.return_list.append(sex_button_draw.return_text)

        now_draw.draw_list.append(sex_button_draw)
        now_draw.width += len(sex_button_draw.text)
        # now_draw.draw_list.append(line_feed_draw)

        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """
        self.draw_list.extend(now_draw.draw_list)

    def draw(self):
        """绘制面板"""
        for label in self.draw_list:
            if isinstance(label, list):
                for value in label:
                    value.draw()
                line_feed_draw.draw()
            else:
                label.draw()

    def change(self):
        """性别改变"""
        character_data: game_type.Character = cache.character_data[0]
        if character_data.sex:
            character_data.sex = 0
        else:
            character_data.sex = 1


class Character_JJ:
    """
    角色阴茎面板
    Keyword arguments:
    character_id -- 角色id
    width -- 最大宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 当前最大可绘制宽度 """
        self.return_list: List[str] = []
        """ 监听的按钮列表 """

        character_data: game_type.Character = cache.character_data[0]
        jj_text = game_config.config_jj_tem[character_data.pl_ability.jj_size].name
        now_draw = panel.LeftDrawTextListPanel()

        jj_draw = draw.LeftDraw()
        # jj_draw.width = 1
        jj_draw.text = _("\n 阴茎大小：{0}      ").format(jj_text)
        now_draw.draw_list.append(jj_draw)
        now_draw.width += len(jj_draw.text)

        button_text = _("    [改变大小]")
        jj_button_draw = draw.LeftButton(
            _(button_text),
            _('改变大小'),
            self.width / 10,
            cmd_func=self.change)
        self.return_list.append(jj_button_draw.return_text)

        now_draw.draw_list.append(jj_button_draw)
        now_draw.width += len(jj_button_draw.text)

        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """
        self.draw_list.extend(now_draw.draw_list)

    def draw(self):
        """绘制面板"""
        if cache.character_data[0].sex == 0:
            for label in self.draw_list:
                if isinstance(label, list):
                    for value in label:
                        value.draw()
                    line_feed_draw.draw()
                else:
                    label.draw()

    def change(self):
        """大小改变"""
        character_data: game_type.Character = cache.character_data[0]
        if character_data.pl_ability.jj_size == 3:
            character_data.pl_ability.jj_size = 0
        else:
            character_data.pl_ability.jj_size += 1



class Character_Debug:
    """
    Debug面板
    Keyword arguments:
    character_id -- 角色id
    width -- 最大宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 当前最大可绘制宽度 """
        self.return_list: List[str] = []
        """ 监听的按钮列表 """

        now_draw = panel.LeftDrawTextListPanel()

        # debug按钮
        if normal_config.config_normal.debug:
            now_draw.draw_list.append(line_feed_draw)
            if cache.debug_mode:
                button_text = _("【关闭debug模式】")
            else:
                button_text = _("【开启debug模式】")
            button_draw = draw.CenterButton(
                _(button_text),
                _('debug'),
                self.width / 5,
                cmd_func=self.change)
            self.return_list.append(button_draw.return_text)

            now_draw.draw_list.append(button_draw)
            now_draw.width += len(button_draw.text)

        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """
        self.draw_list.extend(now_draw.draw_list)

    def draw(self):
        """绘制面板"""
        if cache.character_data[0].sex == 0:
            for label in self.draw_list:
                if isinstance(label, list):
                    for value in label:
                        value.draw()
                    line_feed_draw.draw()
                else:
                    label.draw()

    def change(self):
        """改变"""
        cache.debug_mode = not cache.debug_mode


class Character_FirstNPC:
    """
    角色初始干员面板
    Keyword arguments:
    width -- 最大宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 当前最大可绘制宽度 """
        self.return_list: List[str] = []
        """ 监听的按钮列表 """
        self.npc_select_now = 3
        """ 当前还可以选择的NPC数量 """
        self.normal_handle_panel = panel.PageHandlePanel([], SelectFirstNPCButton, 999, 6, self.width, 1, 0, 0)
        """ 一般干员选择面板 """
        self.talk_chara_handle_panel = panel.PageHandlePanel([], SelectFirstNPCButton, 999, 5, self.width, 1, 0, 0)
        """ 口上干员选择面板 """
        self.show_normal_handle_panel = False
        """ 是否显示一般干员选择面板 """
        self.show_talk_chara_handle_panel = True
        """ 是否显示口上干员选择面板 """
        self.show_special_chara_handle_panel = False
        """ 是否显示特殊干员选择面板 """
        self.id_list = [i + 1 for i in range(len(cache.npc_tem_data))]
        """ 当前显示的NPC列表 """
        self.talk_character_list = []
        """ 口上干员列表 """
        self.special_chara_list = []
        """ 特殊干员列表 """
        self.name_filter_flag = False
        """ 姓名筛选标记 """
        self.chest_filter_flag, self.chest_filter_id_dict = 0, {}
        """ 胸围筛选标记与ID字典 """
        self.age_filter_flag, self.age_filter_id_dict = 0, {}
        """ 年龄筛选标记与ID字典 """
        self.race_filter_flag, self.race_filter_id_dict = 0, {}
        """ 种族筛选标记与ID字典 """

        from Script.UI.Panel import manage_basement_panel

        # 去掉特殊干员
        for chara_id in self.id_list.copy():
            if cache.character_data[chara_id].name in constant.ban_NPC_name_set:
                self.id_list.remove(chara_id)
                self.special_chara_list.append(chara_id)

        now_draw = panel.LeftDrawTextListPanel()
        now_draw.draw_list.append(line_feed_draw)
        now_draw.draw_list.append(line_feed_draw)
        line = draw.LineDraw("↘", 1)
        now_draw.draw_list.append(line)

        info_draw = draw.LeftDraw()
        # info_draw.width = 1
        info_draw.text = _(" 当前初始干员有：")
        info_draw.text += _("\n   基础:")
        npc_id_got_list = sorted(cache.npc_id_got)
        for character_id in npc_id_got_list:
            npc_character_data = cache.character_data[character_id]
            if npc_character_data.name in constant.first_NPC_name_set:
                info_draw.text += f" ●{npc_character_data.name}"
        info_draw.text += _("\n   自选:")
        for character_id in cache.npc_id_got:
            npc_character_data = cache.character_data[character_id]
            if npc_character_data.name not in constant.first_NPC_name_set:
                info_draw.text += f" ●{npc_character_data.name}"

        now_draw.draw_list.append(info_draw)
        now_draw.width += len(info_draw.text)
        now_draw.draw_list.append(line_feed_draw)
        now_draw.width += 1

        button_text = _("[选择初期干员]")
        button_select_draw = draw.CenterButton(
            _(button_text),
            _('选择初期干员'),
            self.width/8,
            cmd_func=self.select_npc,
            )
        self.return_list.append(button_select_draw.return_text)
        now_draw.draw_list.append(button_select_draw)
        now_draw.width += len(button_select_draw.text)

        button_text = _("[指派干员工作]")
        button_select_draw = draw.CenterButton(
            _(button_text),
            _('指派干员工作'),
            self.width/8,
            cmd_func=manage_basement_panel.change_npc_work_out,
            args=self.width
            )
        self.return_list.append(button_select_draw.return_text)
        now_draw.draw_list.append(button_select_draw)
        now_draw.width += len(button_select_draw.text)

        now_draw.draw_list.append(line_feed_draw)
        now_draw.width += 1

        info_last_draw = draw.LeftDraw()
        # info_last_draw.width = 1
        if cache.debug_mode:
            self.npc_select_now = 999
        else:
            self.npc_select_now = 9 - len(cache.npc_id_got)
        if self.npc_select_now:
            info_last_draw.text = _(" 当前剩余可选干员数量 = {0}").format(self.npc_select_now)
            if cache.debug_mode:
                info_last_draw.text += _("  (debug模式下可选999个干员)")
        else:
            info_last_draw.text = _(" 已选择全部初始干员")

        work_people_now,people_max = cache.rhodes_island.work_people_now,len(cache.npc_id_got)
        info_last_draw.text += _("， 当前工作中干员/总干员：{0}/{1}").format(work_people_now, people_max)

        now_draw.draw_list.append(info_last_draw)
        now_draw.width += len(info_last_draw.text)

        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """
        self.draw_list.extend(now_draw.draw_list)

    def draw(self):
        """绘制面板"""
        for label in self.draw_list:
            if isinstance(label, list):
                for value in label:
                    value.draw()
                line_feed_draw.draw()
            else:
                label.draw()

    def select_npc(self):
        """选择初期干员"""

        # 过滤器相关变量定义
        chest_filter_list = [_("无")]
        age_filter_list = [_("无")]
        race_filter_list = []
        for cid in [121, 122, 123, 124, 125]:
            chest_name = game_config.config_talent[cid].name
            chest_filter_list.append(chest_name)
            self.chest_filter_id_dict[chest_name] = []
        for cid in [102, 103, 104, 105, 106, 107]:
            age_name = game_config.config_talent[cid].name
            age_filter_list.append(age_name)
            self.age_filter_id_dict[age_name] = []
        for cid in game_config.config_race:
            if cid == 0:
                continue
            race_name = game_config.config_race[cid].name
            race_filter_list.append(race_name)
            self.race_filter_id_dict[race_name] = []

        # 调用过滤准备函数
        self.prepare_filter()

        while 1:
            return_list = []

            # 显示当前助手
            line = draw.LineDraw("-", self.width)
            line.draw()
            now_npc_draw = draw.NormalDraw()
            if cache.debug_mode:
                self.npc_select_now = 999
            else:
                self.npc_select_now = 9 - len(cache.npc_id_got)
            now_npc_draw.text = ""
            now_npc_draw.text += _(" 有口上的角色会注明文本文件的大小，欢迎使用附带的编辑器erArkEditor，无需写代码仅写文本即可创作口上\n")
            now_npc_draw.text += _("\n 当前已选干员：")
            for character_id in cache.npc_id_got:
                npc_character_data = cache.character_data[character_id]
                if npc_character_data.name not in constant.first_NPC_name_set:
                    now_npc_draw.text += f" ●{npc_character_data.name}"
            now_npc_draw.text += _("\n 当前剩余可选干员数量 = {0}\n").format(self.npc_select_now)
            now_npc_draw.draw()

            # 绘制各按钮
            if cache.debug_mode:
                button_text = _(" [一键全选] ")
                button_draw = draw.CenterButton(button_text, button_text, len(button_text)*2, cmd_func=self.select_all)
                button_draw.draw()
                return_list.append(button_draw.return_text)
            button_text = _(" [随机选择] ")
            random_draw = draw.CenterButton(button_text, button_text, len(button_text)*2, cmd_func=self.random_select)
            random_draw.draw()
            return_list.append(random_draw.return_text)
            if len(self.talk_character_list) <= 0:
                button_text = _(" [口上筛选] ")
                button_draw = draw.CenterButton(button_text, button_text, len(button_text)*2, cmd_func=self.talk_filter)
                button_draw.draw()
                return_list.append(button_draw.return_text)
            if self.name_filter_flag:
                button_text = _(" [姓名筛选中] ")
                button_draw = draw.CenterButton(button_text, button_text, len(button_text)*2, normal_style="gold_enrod", cmd_func=self.name_filter)
            else:
                button_text = _(" [姓名筛选] ")
                button_draw = draw.CenterButton(button_text, _("请输入要筛选的名字："), len(button_text)*2, cmd_func=self.name_filter)
            button_draw.draw()
            return_list.append(button_draw.return_text)
            if self.chest_filter_flag:
                button_text = _(" [胸围筛选中-{0}] ").format(chest_filter_list[self.chest_filter_flag])
                button_draw = draw.CenterButton(button_text, button_text, len(button_text)*2, normal_style="gold_enrod", cmd_func=self.chest_filter)
            else:
                button_text = _(" [胸围筛选] ")
                button_draw = draw.CenterButton(button_text, button_text, len(button_text)*2, cmd_func=self.chest_filter)
            button_draw.draw()
            return_list.append(button_draw.return_text)
            if self.age_filter_flag:
                button_text = _(" [外表年龄筛选中-{0}] ").format(age_filter_list[self.age_filter_flag])
                button_draw = draw.CenterButton(button_text, button_text, len(button_text)*2, normal_style="gold_enrod", cmd_func=self.age_filter)
            else:
                button_text = _(" [外表年龄筛选] ")
                button_draw = draw.CenterButton(button_text, button_text, len(button_text)*2, cmd_func=self.age_filter)
            if self.race_filter_flag:
                button_text = _(" [种族筛选中-{0}] ").format(race_filter_list[self.race_filter_flag - 1])
                button_draw = draw.CenterButton(button_text, button_text, len(button_text)*2, normal_style="gold_enrod", cmd_func=self.race_filter)
            else:
                button_text = _(" [种族筛选] ")
                button_draw = draw.CenterButton(button_text, button_text, len(button_text)*2, cmd_func=self.race_filter)
            button_draw.draw()
            return_list.append(button_draw.return_text)
            button_text = _(" [重置选择] ")
            button_draw = draw.CenterButton(button_text, button_text, len(button_text)*2, cmd_func=self.reset_select)
            button_draw.draw()
            return_list.append(button_draw.return_text)
            line_feed_draw.draw()
            line_feed_draw.draw()

            # 面板绘制
            if self.show_normal_handle_panel:
                draw_text = _(" ▼一般干员")
            else:
                draw_text = _(" ▶一般干员")
            button_draw = draw.LeftButton(draw_text, draw_text, len(draw_text) * 2, cmd_func=self.show_handle_panel, args=(0))
            button_draw.draw()
            return_list.append(button_draw.return_text)
            line_feed_draw.draw()
            if not self.show_normal_handle_panel:
                line_feed_draw.draw()

            if self.show_normal_handle_panel:
                now_list = list(set(self.id_list) - set(self.talk_character_list))
                self.normal_handle_panel.text_list = now_list
                self.normal_handle_panel.update()
                self.normal_handle_panel.draw()
                return_list.extend(self.normal_handle_panel.return_list)
                line_feed_draw.draw()
            
            # 口上面板
            if len(self.talk_character_list) > 0:
                if self.show_talk_chara_handle_panel:
                    draw_text = _(" ▼口上干员")
                else:
                    draw_text = _(" ▶口上干员")
                button_draw = draw.LeftButton(draw_text, draw_text, len(draw_text) * 2, cmd_func=self.show_handle_panel, args=(1))
                button_draw.draw()
                return_list.append(button_draw.return_text)
                line_feed_draw.draw()
                if not self.show_talk_chara_handle_panel:
                    line_feed_draw.draw()
                if self.show_talk_chara_handle_panel:
                    self.talk_chara_handle_panel.text_list = self.talk_character_list
                    self.talk_chara_handle_panel.update()
                    self.talk_chara_handle_panel.draw()
                    return_list.extend(self.talk_chara_handle_panel.return_list)
                    line_feed_draw.draw()

            # 特殊角色
            if self.show_special_chara_handle_panel:
                draw_text = _(" ▼有口上但初期不可选的特殊干员")
            else:
                draw_text = _(" ▶有口上但初期不可选的特殊干员")
            button_draw = draw.LeftButton(draw_text, draw_text, len(draw_text) * 2, cmd_func=self.show_handle_panel, args=(2))
            button_draw.draw()
            return_list.append(button_draw.return_text)
            line_feed_draw.draw()
            # 特殊角色面板
            if self.show_special_chara_handle_panel:
                chara_count = 0
                for character_id in self.special_chara_list:
                    npc_character_data = cache.character_data[character_id]
                    # 跳过没有口上的
                    if not npc_character_data.talk_size:
                        continue
                    # 如果有口上颜色的话，使用口上颜色
                    if npc_character_data.text_color:
                        now_style = npc_character_data.name
                    # 否则使用标准颜色
                    else:
                        now_style = "standard"
                    # 绘制干员信息
                    npc_draw = draw.LeftDraw()
                    draw_text = f"[{str(npc_character_data.adv).rjust(4,'0')}]：{npc_character_data.name}"
                    draw_text += f"({npc_character_data.talk_size}kb)"
                    npc_draw.text = draw_text
                    npc_draw.width = self.width / 5
                    npc_draw.style = now_style
                    npc_draw.draw()
                    # 每五个换行
                    chara_count += 1
                    if chara_count % 5 == 0:
                        line_feed_draw.draw()
            line_feed_draw.draw()
            line_feed_draw.draw()

            # 返回按钮
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), self.width)
            back_draw.draw()
            line_feed_draw.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == random_draw.return_text or yrn == back_draw.return_text:
                break

    def show_handle_panel(self, panel_id):
        """切换面板显示"""
        if panel_id == 0:
            self.show_normal_handle_panel = not self.show_normal_handle_panel
        elif panel_id == 1:
            self.show_talk_chara_handle_panel = not self.show_talk_chara_handle_panel
        elif panel_id == 2:
            self.show_special_chara_handle_panel = not self.show_special_chara_handle_panel

    def prepare_filter(self):
        """完善各种过滤器"""

        for NPC_id in self.id_list:
            target_data: game_type.Character = cache.character_data[NPC_id]

            # 口上过滤
            if target_data.talk_size:
                self.talk_character_list.append(NPC_id)

            # 胸部过滤
            for cid in [121, 122, 123, 124, 125]:
                if target_data.talent[cid]:
                    self.chest_filter_id_dict[game_config.config_talent[cid].name].append(NPC_id)
                    break

            # 年龄过滤
            for cid in [102, 103, 104, 105, 106, 107]:
                if target_data.talent[cid]:
                    self.age_filter_id_dict[game_config.config_talent[cid].name].append(NPC_id)
                    break

            # 种族过滤
            race_cid = target_data.race
            race_name = game_config.config_race[race_cid].name
            if race_name in self.race_filter_id_dict:
                self.race_filter_id_dict[race_name].append(NPC_id)

    def select_all(self):
        """一键全选"""
        for i in range(len(cache.npc_tem_data)):
            npc_id = i + 1
            if npc_id not in cache.npc_id_got:
                cache.npc_id_got.add(npc_id)

    def random_select(self):
        """随机选择"""
        self.reset_select()
        # 获取当前未选择的NPC
        not_got_npc = [i+1 for i in range(len(cache.npc_tem_data)) if i+1 not in cache.npc_id_got]
        # 随机选择三个，然后加到列表中
        random_npc = random.sample(not_got_npc, 3)
        for npc_id in random_npc:
            cache.npc_id_got.add(npc_id)

    def talk_filter(self):
        """口上过滤"""
        self.age_filter_flag = 0
        self.chest_filter_flag = 0
        self.race_filter_flag = 0
        self.id_list = [i + 1 for i in range(len(cache.npc_tem_data))]
        self.prepare_filter()
        self.show_normal_handle_panel = False
        self.show_talk_chara_handle_panel = True

    def name_filter(self):
        """姓名筛选"""
        # 进入筛选模式
        if not self.name_filter_flag:
            # 获取用户输入的文字
            user_input = flow_handle.askfor_str(_("请输入要筛选的名字："))
            # 遍历所有 NPC 的姓名，找到包含用户输入的文字的 NPC
            npc_name_filter_id = []
            for character_id in cache.character_data:
                npc_character_data = cache.character_data[character_id]
                if npc_character_data.name not in constant.first_NPC_name_set and user_input in npc_character_data.name:
                    npc_name_filter_id.append(character_id)
            self.id_list = npc_name_filter_id
            self.talk_character_list = []
        # 退出筛选模式
        else:
            self.id_list = [i + 1 for i in range(len(cache.npc_tem_data))]
        self.name_filter_flag = not self.name_filter_flag
        self.show_normal_handle_panel = True

    def chest_filter(self):
        """胸围筛选"""
        self.chest_filter_flag = (self.chest_filter_flag + 1) % 6
        if self.chest_filter_flag == 0:
            self.id_list = [i + 1 for i in range(len(cache.npc_tem_data))]
        elif self.chest_filter_flag == 1:
            self.id_list = self.chest_filter_id_dict[_("绝壁")]
        elif self.chest_filter_flag == 2:
            self.id_list = self.chest_filter_id_dict[_("贫乳")]
        elif self.chest_filter_flag == 3:
            self.id_list = self.chest_filter_id_dict[_("普乳")]
        elif self.chest_filter_flag == 4:
            self.id_list = self.chest_filter_id_dict[_("巨乳")]
        elif self.chest_filter_flag == 5:
            self.id_list = self.chest_filter_id_dict[_("爆乳")]
        self.age_filter_flag = 0
        self.talk_character_list = []
        self.show_normal_handle_panel = True

    def age_filter(self):
        """外表年龄筛选"""
        self.age_filter_flag = (self.age_filter_flag + 1) % 7
        if self.age_filter_flag == 0:
            self.id_list = [i + 1 for i in range(len(cache.npc_tem_data))]
        elif self.age_filter_flag == 1:
            self.id_list = self.age_filter_id_dict[_("幼女")]
        elif self.age_filter_flag == 2:
            self.id_list = self.age_filter_id_dict[_("萝莉")]
        elif self.age_filter_flag == 3:
            self.id_list = self.age_filter_id_dict[_("少女")]
        elif self.age_filter_flag == 4:
            self.id_list = self.age_filter_id_dict[_("大姐姐")]
        elif self.age_filter_flag == 5:
            self.id_list = self.age_filter_id_dict[_("熟女")]
        elif self.age_filter_flag == 6:
            self.id_list = self.age_filter_id_dict[_("人妻")]
        self.chest_filter_flag = 0
        self.talk_character_list = []
        self.show_normal_handle_panel = True

    def race_filter(self):
        """种族筛选"""
        self.race_filter_flag = (self.race_filter_flag + 1) % len(game_config.config_race)
        if self.race_filter_flag == 0:
            self.id_list = [i + 1 for i in range(len(cache.npc_tem_data))]
        else:
            now_cid = self.race_filter_flag
            race_name = game_config.config_race[now_cid].name
            self.id_list = self.race_filter_id_dict[race_name]
        self.talk_character_list = []
        self.show_normal_handle_panel = True

    def reset_select(self):
        """重置选择"""
        # 获取当前已选择的NPC
        now_select_npc_ld_list = [character_id for character_id in cache.npc_id_got if cache.character_data[character_id].name not in constant.first_NPC_name_set]
        # 从列表中移除
        for character_id in now_select_npc_ld_list:
            cache.npc_id_got.remove(character_id)
        # 重置过滤器
        self.age_filter_flag = 0
        self.chest_filter_flag = 0
        self.race_filter_flag = 0
        self.id_list = [i + 1 for i in range(len(cache.npc_tem_data))]
        self.talk_character_list = []
        # 去掉特殊干员
        self.special_chara_list = []
        for chara_id in self.id_list.copy():
            if cache.character_data[chara_id].name in constant.ban_NPC_name_set:
                self.id_list.remove(chara_id)
                self.special_chara_list.append(chara_id)
        self.prepare_filter()


class SelectFirstNPCButton:
    """
    点击后可选择作为初期干员的NPC的按钮对象
    Keyword arguments:
    text -- 选项名字
    width -- 最大宽度
    is_button -- 绘制按钮
    num_button -- 绘制数字按钮
    button_id -- 数字按钮id
    """

    def __init__(
        self, NPC_id: int, width: int, is_button: bool, num_button: bool, button_id: int
    ):
        """初始化绘制对象"""

        self.NPC_id: int = NPC_id
        """ 干员角色编号 """
        self.draw_text: str = ""
        """ 绘制文本 """
        self.width: int = width
        """ 最大宽度 """
        self.num_button: bool = num_button
        """ 绘制数字按钮 """
        self.button_id: int = button_id
        """ 数字按钮的id """
        self.button_return: str = str(NPC_id)
        """ 按钮返回值 """

        target_data: game_type.Character = cache.character_data[NPC_id]
        button_text = f"[{str(target_data.adv).rjust(4,'0')}]：{target_data.name}"
        # 如果有口上的话，且版本已启用，输出大小
        if target_data.talk_size and cache.all_system_setting.character_text_version[target_data.adv] > 0:
            button_text += f"({target_data.talk_size}kb)"
        # 获得绘制颜色
        # 如果有口上颜色的话，使用口上颜色
        if target_data.text_color:
            now_style = target_data.name
        # 如果是已选择的干员，使用金色
        elif self.NPC_id in cache.npc_id_got:
            now_style = "gold_enrod"
        # 否则使用标准颜色
        else:
            now_style = "standard"

        name_draw = draw.LeftDraw()
        if self.NPC_id in cache.npc_id_got:
            if target_data.name in constant.first_NPC_name_set:
                button_text += _("(基础)")
                name_draw.text = button_text
                name_draw.width = self.width
                name_draw.style = now_style
            else:
                button_text += _("(自选)")
                name_draw = draw.LeftButton(button_text, self.button_return, self.width,normal_style = now_style, cmd_func=self.button_0)
        else:
            name_draw = draw.LeftButton(button_text, self.button_return, self.width,normal_style = now_style, cmd_func=self.button_0)

        # 按钮绘制
        # self.button_return = NPC_id
        self.draw_text = button_text

        """ 绘制的对象 """
        self.now_draw = name_draw

    def button_0(self):
        """选项1"""
        if self.NPC_id in cache.npc_id_got:
            cache.npc_id_got.remove(self.NPC_id)
        elif cache.debug_mode:
            cache.npc_id_got.add(self.NPC_id)
        elif 9 - len(cache.npc_id_got):
            cache.npc_id_got.add(self.NPC_id)

    def draw(self):
        """绘制对象"""
        self.now_draw.draw()


class Character_Bonus:
    """
    角色奖励点数面板
    Keyword arguments:
    character_id -- 角色id
    width -- 最大宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 当前最大可绘制宽度 """
        self.return_list: List[str] = []
        """ 监听的按钮列表 """

        character_data: game_type.Character = cache.character_data[0]
        bonus_all = 0
        now_draw = panel.LeftDrawTextListPanel()
        now_draw.draw_list.append(line_feed_draw)
        now_draw.draw_list.append(line_feed_draw)
        line = draw.LineDraw("↘", 1)
        now_draw.draw_list.append(line)

        # 提供的点数
        bonus_all += cache.game_round * 20
        if cache.debug_mode:
            bonus_all += 999
        self.bonus_now = bonus_all

        info_talent_draw = draw.LeftDraw()
        # info_talent_draw.width = 1
        info_talent_draw.text = _(" 可选奖励有：\n")
        info_talent_draw.text += _("  （未选择的源石能力均可在游戏中满足特定条件解锁）\n")
        now_draw.draw_list.append(info_talent_draw)
        now_draw.width += len(info_talent_draw.text)

        bonus_use_text = ""

        # 遍历可选奖励
        for cid in game_config.config_first_bonus:
            button_text = ""
            first_bonus_data = game_config.config_first_bonus[cid]
            # 判断是否已经选择，并输出对应前缀和预填消耗文本
            if cache.first_bonus[cid]:
                self.bonus_now -= first_bonus_data.consume
                button_text += f"   ●"
                draw_style = "gold_enrod"
                bonus_use_text += f" - [{first_bonus_data.name}({first_bonus_data.consume})])"
            else:
                button_text += f"   ○"
                draw_style = "standard"
            # 文本1
            button_text += f"{first_bonus_data.name}({first_bonus_data.consume})："
            # 文本2(部分奖励有特殊文本)
            if cache.first_bonus[cid]:
                if cid == 21:
                    ability_name = game_config.config_ability[cache.first_bonus[cid]].name
                    button_text += _("(已选{0})").format(ability_name)
                elif cid == 22:
                    target_data: game_type.Character = cache.character_data[character_data.assistant_character_id]
                    button_text += _("(已选{0})").format(target_data.name)
            # 文本3
            button_text += f"{first_bonus_data.introduce}"
            # 绘制按钮
            button_draw = draw.LeftButton(
                _(button_text),
                _(first_bonus_data.name),
                self.width,
                normal_style = draw_style,
                cmd_func=self.get_first_bonus,
                args=cid)
            self.return_list.append(button_draw.return_text)
            now_draw.draw_list.append(button_draw)
            now_draw.width += len(button_text)
            now_draw.draw_list.append(line_feed_draw)
            now_draw.width += 1

        info_draw = draw.LeftDraw()
        # info_draw.width = 1
        info_draw.text = _(" \n 当前为第 {0} 周目\n").format(str(cache.game_round))
        info_draw.text += _(" 当前剩余奖励点数 =")
        info_draw.text += _(" {0} = [周目数 * 20]").format(self.bonus_now)
        if cache.debug_mode:
            info_draw.text += _(" + [debug(999)]")
        info_draw.text += f"{bonus_use_text}\n"
        now_draw.draw_list.append(info_draw)
        now_draw.width += len(info_draw.text)

        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """
        self.draw_list.extend(now_draw.draw_list)

    def draw(self):
        """绘制面板"""
        for label in self.draw_list:
            if isinstance(label, list):
                for value in label:
                    value.draw()
                line_feed_draw.draw()
            else:
                label.draw()


    def get_first_bonus(self,first_bonus_id:int):
        """获得初期奖励"""
        from Script.UI.Panel import assistant_panel, normal_panel

        pl_character_data: game_type.Character = cache.character_data[0]
        fail_flag = False

        # 获得素质
        if first_bonus_id <= 10:
            if first_bonus_id == 1:
                talent_id = 304
            elif first_bonus_id == 2:
                talent_id = 307
            elif first_bonus_id == 3:
                talent_id = 331
            elif first_bonus_id == 4:
                talent_id = 316

            if pl_character_data.talent[talent_id]:
                pl_character_data.talent[talent_id] = 0
                cache.first_bonus[first_bonus_id] = False
            elif self.bonus_now >= 10:
                pl_character_data.talent[talent_id] = 1
                cache.first_bonus[first_bonus_id] = True
            else:
                fail_flag = True

        # 获得金钱
        elif first_bonus_id == 11:
            if cache.rhodes_island.materials_resouce[2]:
                cache.rhodes_island.materials_resouce[1] = 20000
                cache.rhodes_island.materials_resouce[2] = 0
                cache.rhodes_island.materials_resouce[4] = 0
                cache.rhodes_island.materials_resouce[11] = 20
                cache.first_bonus[first_bonus_id] = False
            elif self.bonus_now >= 5:
                cache.rhodes_island.materials_resouce[1] = 70000
                cache.rhodes_island.materials_resouce[2] = 6000
                cache.rhodes_island.materials_resouce[4] = 100
                cache.rhodes_island.materials_resouce[11] = 50
                cache.first_bonus[first_bonus_id] = True
            else:
                fail_flag = True

        # 自选部分
        elif first_bonus_id >= 21:

            # 领域专家
            if first_bonus_id == 21:
                if cache.first_bonus[first_bonus_id]:
                    pl_character_data.ability[cache.first_bonus[first_bonus_id]] = 0
                    cache.first_bonus[first_bonus_id] = False
                elif self.bonus_now >= 5:
                    now_panel = normal_panel.Chose_First_bonus_ability_Panel(self.width)
                    now_panel.draw()
                    if cache.first_bonus[first_bonus_id]:
                        pl_character_data.ability[cache.first_bonus[first_bonus_id]] = 5
                else:
                    fail_flag = True

            # 助理干员
            elif first_bonus_id == 22:

                # 旧助理的好感信赖清零
                if pl_character_data.assistant_character_id:
                    target_data: game_type.Character = cache.character_data[pl_character_data.assistant_character_id]
                    target_data.favorability[0] = 0
                    target_data.trust = 0
                    cache.first_bonus[first_bonus_id] = False
                
                # 这里直接沿用的助理页面的代码
                if self.bonus_now >= 5:
                    assistant_panel.chose_assistant()

                    # 在这里处理好感和信赖的增加
                    if pl_character_data.assistant_character_id:
                        target_data: game_type.Character = cache.character_data[pl_character_data.assistant_character_id]
                        target_data.favorability[0] = 1000
                        target_data.trust = 50
                        cache.first_bonus[first_bonus_id] = pl_character_data.assistant_character_id

                else:
                    fail_flag = True

        # 点数不足信息绘制
        if fail_flag:
            info_last_draw = draw.WaitDraw()
            # info_last_draw.width = 1
            info_last_draw.text = _("\n 当前剩余奖励不足\n")
            info_last_draw.draw()


class World_Setting:
    """
    世界设定面板
    Keyword arguments:
    character_id -- 角色id
    width -- 最大宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 当前最大可绘制宽度 """
        self.return_list: List[str] = []
        """ 监听的按钮列表 """

        now_draw = panel.LeftDrawTextListPanel()
        now_draw.draw_list.append(line_feed_draw)
        line = draw.LineDraw("↘", 1)
        now_draw.draw_list.append(line)

        setting_info_draw = draw.LeftDraw()
        # setting_info_draw.width = 1
        draw_text = _(" 当前世界设定为：\n")
        draw_text += _("   ●基础世界设定：美好的黄油IF世界线，无具体时间线和剧情线，凡是有立绘的角色（包括敌我双方、路人、已便当的）均可招募上岛\n")
        draw_text += _("   ●基础角色设定：NPC为纯女性角色（伪娘、扶她均不存在，女性小车存在），且全员处女\n")
        setting_info_draw.text = draw_text
        now_draw.draw_list.append(setting_info_draw)
        now_draw.width += len(setting_info_draw.text)

        # 遍历可选设定
        for cid in game_config.config_world_setting:
            button_text = ""
            world_setting_data = game_config.config_world_setting[cid]
            # 判断是否已经选择，并输出对应前缀和预填消耗文本
            if cache.world_setting[cid]:
                button_text += f"   ●"
                draw_style = "gold_enrod"
            else:
                button_text += f"   ○"
                draw_style = "standard"
            # 文本
            button_text += f"{world_setting_data.name}：{world_setting_data.introduce}"
            # 绘制按钮
            button_draw = draw.LeftButton(
                _(button_text),
                _(world_setting_data.name),
                self.width,
                normal_style = draw_style,
                cmd_func=self.select_setting,
                args=cid)
            self.return_list.append(button_draw.return_text)
            now_draw.draw_list.append(button_draw)
            now_draw.width += len(button_text)
            now_draw.draw_list.append(line_feed_draw)
            now_draw.width += 1


        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """
        self.draw_list.extend(now_draw.draw_list)

    def draw(self):
        """绘制面板"""
        for label in self.draw_list:
            if isinstance(label, list):
                for value in label:
                    value.draw()
                line_feed_draw.draw()
            else:
                label.draw()

    def select_setting(self,setting_cid : int):
        """选择该设定"""
        cache.world_setting[setting_cid] = not cache.world_setting[setting_cid]

class Other_Settings:
    """
    其他设定面板
    Keyword arguments:
    character_id -- 角色id
    width -- 最大宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 当前最大可绘制宽度 """
        self.return_list: List[str] = []
        """ 监听的按钮列表 """
        from Script.UI.Panel import prts_panel

        now_draw = panel.LeftDrawTextListPanel()
        now_draw.draw_list.append(line_feed_draw)
        line = draw.LineDraw("↘", 1)
        now_draw.draw_list.append(line)

        setting_info_draw = draw.LeftDraw()
        # setting_info_draw.width = 1
        draw_text = _(" 其他设定：\n")
        setting_info_draw.text = draw_text
        now_draw.draw_list.append(setting_info_draw)
        now_draw.width += len(setting_info_draw.text)

        # 绘制按钮
        button_text = _(" [系统设定] ")
        button_draw = draw.CenterButton(
            button_text,
            button_text,
            len(button_text) * 2,
            cmd_func=self.system_setting_draw,
            )
        self.return_list.append(button_draw.return_text)
        now_draw.draw_list.append(button_draw)
        now_draw.width += len(button_text)

        button_text = _(" [口上版本设定] ")
        button_draw = draw.CenterButton(
            button_text,
            button_text,
            len(button_text) * 2,
            cmd_func=prts_panel.chara_talk_info,
            )
        self.return_list.append(button_draw.return_text)
        now_draw.draw_list.append(button_draw)
        now_draw.width += len(button_text)
        now_draw.draw_list.append(line_feed_draw)
        now_draw.width += 1

        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """
        self.draw_list.extend(now_draw.draw_list)

    def system_setting_draw(self):
        """系统设定"""
        from Script.UI.Panel import system_setting
        now_panel = system_setting.System_Setting_Panel(width)
        now_panel.draw()

    def draw(self):
        """绘制面板"""
        for label in self.draw_list:
            if isinstance(label, list):
                for value in label:
                    value.draw()
                line_feed_draw.draw()
            else:
                label.draw()
