import random
from functools import wraps
from typing import List
from types import FunctionType
from Script.Core import get_text, constant, game_type, cache_control, flow_handle, py_cmd

from Script.Design import (
    handle_panel,
    character,
    character_handle,
    cooking,
    map_handle,
    attr_calculation,
    basement,
)
from Script.UI.Moudle import panel, draw
from Script.UI.Panel import manage_basement_panel, see_character_info_panel, assistant_panel, normal_panel
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
            cache.base_resouce = basement.get_base_zero()
            first_bonus_updata()
            character_handle.first_NPC_work()
            if confirm_character_attr_panel():
                game_start()
                break
        cache.character_data[0] = game_type.Character()
    cache.now_panel_id = constant.Panel.IN_SCENE

def first_bonus_updata():
    """刷新初始奖励"""
    for cid in game_config.config_first_bonus:
        cache.first_bonus[cid] = False

def game_start():
    """初始化游戏数据"""
    character_handle.init_character_dormitory()
    character_handle.init_character_position()
    character_handle.init_character_facility_open()
    # course.init_phase_course_hour()
    # interest.init_character_interest()
    # course.init_character_knowledge()
    # course.init_class_teacher()
    # course.init_class_time_table()
    # course.init_teacher_table()
    cooking.init_recipes()
    cooking.init_restaurant_data()
    character_position = cache.character_data[0].position
    map_handle.character_move_scene(["0","0"], character_position, 0)
    # cache.school_longitude = random.uniform(120.9, 122.12)
    # cache.school_latitude = random.uniform(30.7, 31.53)
    basement.get_base_updata()
    character_handle.init_character_entertainment()
    # print(f"debug 2facility_open = {cache.base_resouce.facility_open}")

def confirm_game_info_panel():
    """确认游戏说明面板"""
    now_line = draw.LineDraw("-", width)
    now_line.draw()
    info_text = f"\n\n  免责声明：1.本游戏仅为开发者本人自娱自乐及代码练习所用，开发它是因为我个人趣味低下，思想低俗所至致，无任何经济收益和利益驱动。游戏仅为个人自用，不对外公开。\n\n\n            2.本游戏含有大量的R18色情内容，内容中可能会出现的有：调教、轻度SM、非合意性行为、近亲相奸等，不会出现的有：NTR、重度SM、血腥、暴力、R18G等。\n\n\n            3.本游戏在设计理念和游戏内容上缝合了大量era与其他各类作品，如有雷同都是正常的。\n\n\n            4.本游戏仅适合开发者本人游玩，不适合普通人游玩，特别是严厉禁止未成年人游玩，非开发者以外的任何人游玩该游戏出现的任何意外都和开发者本人无关。\n\n\n            5.本游戏禁止任何人在任何渠道对游戏本体或选取部分内容进行传播、交流、展示，公开和私底下都不行，禁止任何人用该游戏通过任何方式进行盈利。\n\n\n            6.基于以上叠了这么多层buff，建议有大胆想法的人请现在关掉窗口并立刻删除该游戏。\n\n\n            7.总之只要不删就默认你已经理解并遵守该声明，在不遵守的情况下出现的任何事故和法律责任都和开发者没有任何关系。\n\n\n"
    askfor_list = [_("我读完并理解了以上7条，我对自己负责，我不删，我要玩")]
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
    ask_name_panel = panel.AskForOneMessage()
    ask_name_panel.set(_("你能回忆起自己的名字吗？（默认称呼为博士，此处仅输入姓名即可）"), 10)
    line_feed_draw.draw()
    line.draw()
    not_num_error = draw.NormalDraw()
    not_num_error.text = _("角色名不能为纯数字，请重新输入\n")
    not_system_error = draw.NormalDraw()
    not_system_error.text = _("角色名不能为系统保留字，请重新输入\n")
    not_name_error = draw.NormalDraw()
    not_name_error.text = _("已有角色使用该姓名，请重新输入\n")
    create_judge = 0
    while 1:
        now_name = ask_name_panel.draw()
        if now_name.isdigit():
            not_num_error.draw()
            continue
        if now_name in get_text.translation_values or now_name in get_text.translation._catalog:
            not_system_error.draw()
            continue
        if now_name in cache.npc_name_data:
            not_name_error.draw()
            continue
        character_data.name = now_name
        character_data.nick_name = "博士"
        create_judge = 1

        break
    return create_judge


class Character_creat_Handle:
    """
    角色创建页面对象
    Keyword arguments:
    """

    def __init__(self):
        """初始化绘制对象"""
        self.width = normal_config.config_normal.text_width
        info_draw = see_character_info_panel.CharacterInfoHead(0, width)
        info_draw.draw_title = False
        sex_draw = Character_Sex(self.width)
        jj_draw = Character_JJ(self.width)
        debug_draw = Character_Debug(self.width)
        firstNpc_draw = Character_FirstNPC(self.width)
        bonus_draw = Character_Bonus(self.width)
        # abi_draw = see_character_info_panel.CharacterabiText(0, width)
        # tal_draw = see_character_info_panel.CharacterTalentText(0, width, 8, 0)
        self.draw_list: List[draw.NormalDraw] = [
            info_draw,
            sex_draw,
            jj_draw,
            debug_draw,
            firstNpc_draw,
            bonus_draw,
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
        sex_draw.width = 1
        sex_draw.text = f"\n 性别：{sex_text}      "
        now_draw.draw_list.append(sex_draw)
        now_draw.width += len(sex_draw.text)

        button_text = f"    【改变性别】"
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
        jj_draw.width = 1
        jj_draw.text = f"\n 阴茎大小：{jj_text}      "
        now_draw.draw_list.append(jj_draw)
        now_draw.width += len(jj_draw.text)

        button_text = f"    【改变大小】"
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
        now_draw.draw_list.append(line_feed_draw)

        if cache.debug_mode:
            button_text = f"【关闭debug模式】"
        else:
            button_text = f"【开启debug模式】"
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

        now_draw = panel.LeftDrawTextListPanel()
        now_draw.draw_list.append(line_feed_draw)
        now_draw.draw_list.append(line_feed_draw)
        line = draw.LineDraw("↘", 1)
        now_draw.draw_list.append(line)

        info_draw = draw.LeftDraw()
        info_draw.width = 1
        info_draw.text = f" 当前初始干员有："
        info_draw.text += f"\n   基础:"
        for character_id in cache.npc_id_got:
            npc_character_data = cache.character_data[character_id]
            if npc_character_data.name in constant.first_NPC_name_set:
                info_draw.text += f" ●{npc_character_data.name}"
        info_draw.text += f"\n   自选:"
        for character_id in cache.npc_id_got:
            npc_character_data = cache.character_data[character_id]
            if npc_character_data.name not in constant.first_NPC_name_set:
                info_draw.text += f" ●{npc_character_data.name}"

        now_draw.draw_list.append(info_draw)
        now_draw.width += len(info_draw.text)
        now_draw.draw_list.append(line_feed_draw)
        now_draw.width += 1

        button_text = f"【选择初期干员】"
        button_select_draw = draw.CenterButton(
            _(button_text),
            _('选择初期干员'),
            self.width/8,
            cmd_func=self.select_npc,
            )
        self.return_list.append(button_select_draw.return_text)
        now_draw.draw_list.append(button_select_draw)
        now_draw.width += len(button_select_draw.text)

        button_text = f"【指派干员工作】"
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
        info_last_draw.width = 1
        if cache.debug_mode:
            self.npc_select_now = 999
        else:
            self.npc_select_now = 9 - len(cache.npc_id_got)
        if self.npc_select_now:
            info_last_draw.text = f" 当前剩余可选干员数量 = {self.npc_select_now}"
            if cache.debug_mode:
                info_last_draw.text += f"  (debug模式下可选999个干员)"
        else:
            info_last_draw.text = f" 已选择全部初始干员"

        work_people_now,people_max = cache.base_resouce.work_people_now,len(cache.npc_id_got)
        info_last_draw.text += f"\n 当前工作中干员/总干员：{work_people_now}/{people_max}"

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

        self.handle_panel = panel.PageHandlePanel([], SelectFirstNPCButton, 999, 6, self.width, 1, 1, 0)
        self.id_list = [i + 1 for i in range(len(cache.npc_tem_data))]
        self.name_filter_flag = False

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
            now_npc_draw.text = f"\n 当前已选干员："
            for character_id in cache.npc_id_got:
                npc_character_data = cache.character_data[character_id]
                if npc_character_data.name not in constant.first_NPC_name_set:
                    now_npc_draw.text += f" ●{npc_character_data.name}"
            now_npc_draw.text += f"\n 当前剩余可选干员数量 = {self.npc_select_now}\n"
            now_npc_draw.draw()

            # 绘制各按钮
            if cache.debug_mode:
                button_text = " [一键全选] "
                button_draw = draw.CenterButton(button_text, button_text, len(button_text)*2, cmd_func=self.select_all)
                button_draw.draw()
                return_list.append(button_draw.return_text)
            button_text = " [随机选择] "
            button_draw = draw.CenterButton(button_text, button_text, len(button_text)*2, cmd_func=self.random_select)
            button_draw.draw()
            return_list.append(button_draw.return_text)
            if self.name_filter_flag:
                button_text = " [姓名筛选中] "
                button_draw = draw.CenterButton(button_text, button_text, len(button_text)*2, normal_style="nowmap", cmd_func=self.name_filter)
            else:
                button_text = " [姓名筛选] "
                button_draw = draw.CenterButton(button_text, "请输入要筛选的名字：", len(button_text)*2, cmd_func=self.name_filter)
            button_draw.draw()
            return_list.append(button_draw.return_text)
            button_text = " [重置选择] "
            button_draw = draw.CenterButton(button_text, button_text, len(button_text)*2, cmd_func=self.reset_select)
            button_draw.draw()
            return_list.append(button_draw.return_text)
            line_feed_draw.draw()
            line_feed_draw.draw()

            # 遍历所有NPC
            # print("debug id_list = ",id_list)
            self.handle_panel.text_list = self.id_list
            self.handle_panel.update()
            self.handle_panel.draw()
            return_list.extend(self.handle_panel.return_list)
            line_feed_draw.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), self.width)
            back_draw.draw()
            line_feed_draw.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                break

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
        # 退出筛选模式
        else:
            self.id_list = [i + 1 for i in range(len(cache.npc_tem_data))]
        self.name_filter_flag = not self.name_filter_flag

    def reset_select(self):
        """重置选择"""
        # 获取当前已选择的NPC
        now_select_npc_ld_list = [character_id for character_id in cache.npc_id_got if cache.character_data[character_id].name not in constant.first_NPC_name_set]
        # 从列表中移除
        for character_id in now_select_npc_ld_list:
            cache.npc_id_got.remove(character_id)


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
        self.button_return: str = str(button_id)
        """ 按钮返回值 """

        target_data: game_type.Character = cache.character_data[NPC_id]
        button_text = f"[{str(target_data.adv).rjust(4,'0')}]：{target_data.name}"
        name_draw = draw.LeftDraw()
        if self.NPC_id in cache.npc_id_got:
            if target_data.name in constant.first_NPC_name_set:
                button_text += f" (基础)"
                name_draw.text = button_text
                name_draw.width = self.width
                name_draw.style = "nowmap"
            else:
                button_text += f" (自选)"
                name_draw = draw.LeftButton(button_text, self.button_return, self.width,normal_style = "nowmap", cmd_func=self.button_0)
        else:
            name_draw = draw.LeftButton(button_text, self.button_return, self.width, cmd_func=self.button_0)

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

        if cache.game_round == 1:
            bonus_all += 20
        if cache.debug_mode:
            bonus_all += 999
        self.bonus_now = bonus_all

        info_talent_draw = draw.LeftDraw()
        info_talent_draw.width = 1
        info_talent_draw.text = f" 可选奖励有：\n"
        now_draw.draw_list.append(info_talent_draw)
        now_draw.width += len(info_talent_draw.text)

        bonus_use_text = ""

        # 遍历可选奖励
        for cid in game_config.config_first_bonus:
            button_text = ""
            first_bonus_date = game_config.config_first_bonus[cid]
            # 判断是否已经选择，并输出对应前缀和预填消耗文本
            if cache.first_bonus[cid]:
                self.bonus_now -= first_bonus_date.consume
                button_text += f"   ●"
                draw_style = "nowmap"
                bonus_use_text += f" - [{first_bonus_date.name}({first_bonus_date.consume})])"
            else:
                button_text += f"   ○"
                draw_style = "standard"
            # 文本1
            button_text += f"{first_bonus_date.name}({first_bonus_date.consume})："
            # 文本2(部分奖励有特殊文本)
            if cache.first_bonus[cid]:
                if cid == 21:
                    ability_name = game_config.config_ability[cache.first_bonus[cid]].name
                    button_text += f"(已选{ability_name})"
                elif cid == 22:
                    target_data: game_type.Character = cache.character_data[character_data.assistant_character_id]
                    button_text += f"(已选{target_data.name})"
            # 文本3
            button_text += f"{first_bonus_date.introduce}"
            # 绘制按钮
            button_draw = draw.LeftButton(
                _(button_text),
                _(first_bonus_date.name),
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
        info_draw.width = 1
        info_draw.text = f" \n 当前为第 {str(cache.game_round)} 周目\n"
        info_draw.text += f" 当前剩余奖励点数 ="
        info_draw.text += f" {self.bonus_now} = [新玩家奖励(20)]"
        if cache.debug_mode:
            info_draw.text += f" + [debug(999)]"
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
        pl_character_data: game_type.Character = cache.character_data[0]
        fail_flag = False

        # 获得素质
        if first_bonus_id <= 10:
            if first_bonus_id == 1:
                talent_id = 304
            elif first_bonus_id == 2:
                talent_id = 307

            if pl_character_data.talent[talent_id]:
                pl_character_data.talent[talent_id] = 0
                cache.first_bonus[first_bonus_id] = False
            elif self.bonus_now >= 10:
                pl_character_data.talent[talent_id] = 1
                cache.first_bonus[first_bonus_id] = True
                # 获得对应素质则同步至对应收集解锁页面
                if talent_id == 304:
                    pl_character_data.pl_collection.collection_bonus[1] = True
                elif talent_id == 307:
                    pl_character_data.pl_collection.collection_bonus[101] = True
            else:
                fail_flag = True

        # 获得金钱
        elif first_bonus_id == 11:
            if cache.base_resouce.materials_resouce[1]:
                cache.base_resouce.materials_resouce[1] = 0
                cache.base_resouce.materials_resouce[2] = 0
                cache.base_resouce.materials_resouce[4] = 0
                cache.first_bonus[first_bonus_id] = False
            elif self.bonus_now >= 5:
                cache.base_resouce.materials_resouce[1] = 50000
                cache.base_resouce.materials_resouce[2] = 6000
                cache.base_resouce.materials_resouce[4] = 100
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
                    pl_character_data.assistant_character_id = 0
                    cache.first_bonus[first_bonus_id] = False
                
                # 这里直接沿用的助理页面的代码
                elif self.bonus_now >= 5:
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
            info_last_draw.width = 1
            info_last_draw.text = f"\n 当前剩余奖励不足\n"
            info_last_draw.draw()

