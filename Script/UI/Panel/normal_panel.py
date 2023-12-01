from typing import List
from types import FunctionType
from Script.UI.Moudle import draw, panel
from Script.Core import (
    cache_control,
    get_text,
    game_type,
    flow_handle,
    constant,
)
from Script.Config import game_config, normal_config
from Script.Design import update, map_handle, character, game_time

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


class Close_Door_Panel:
    """
    用于关门的面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.now_panel = _("关门")
        """ 当前绘制的页面 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """

    def draw(self):
        """绘制对象"""

        character_data: game_type.Character = cache.character_data[0]

        title_text = "关门"

        title_draw = draw.TitleLineDraw(title_text, self.width)
        while 1:
            return_list = []
            title_draw.draw()

            now_position = character_data.position
            now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
            now_scene_data = cache.scene_data[now_scene_str]
            now_draw = panel.LeftDrawTextListPanel()

            # 地点关门判定的三个分支
            if now_scene_data.close_type == 0:
                info_text = "\n当前地点无法关门，要继续吗："
            elif now_scene_data.close_type == 1:
                info_text = "\n当前地点可以关门，关上之后其他人就进不来了，要关门吗："
            else:
                info_text = "\n当前地点有可以关门的小隔间，关上后别人无法发现隔间内的人，但仍可以进入该地点，要关门吗："

            askfor_panel = panel.OneMessageAndSingleColumnButton()
            askfor_list = [_("是"), _("否")]
            askfor_panel.set(askfor_list, _(info_text), 0)
            askfor_panel_return_list = askfor_panel.get_return_list()
            return_list.extend(askfor_panel_return_list.keys())
            now_draw.draw_list.append(askfor_panel)

            self.draw_list: List[draw.NormalDraw] = []
            """ 绘制的文本列表 """
            self.draw_list.extend(now_draw.draw_list)

            for label in self.draw_list:
                if isinstance(label, list):
                    for value in label:
                        value.draw()
                    line_feed.draw()
                else:
                    label.draw()

            yrn = flow_handle.askfor_all(return_list)
            if yrn in return_list:
                if askfor_panel_return_list[yrn] == askfor_list[0]:
                    cache.scene_data[now_scene_str].close_flag = now_scene_data.close_type
                    return 1
                return 0


class Read_Book_Panel:
    """
    用于读书的面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.now_panel = _("读书")
        """ 当前绘制的页面 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """

    def draw(self):
        """绘制对象"""

        character_data: game_type.Character = cache.character_data[0]

        title_text = "读书"
        title_draw = draw.TitleLineDraw(title_text, self.width)

        while 1:
            return_list = []
            title_draw.draw()

            # 当前借书数量信息
            book_id_set = character_data.entertainment.borrow_book_id_set

            # 如果未借书的话直接输出提示信息
            if len(book_id_set) == 0:
                info_draw = draw.NormalDraw()
                borrow_limit_text = f"\n当前未持有书籍，请前去图书馆借书\n"
                info_draw.text = borrow_limit_text
                info_draw.width = self.width
                info_draw.draw()
            # 已借书则遍历输出按钮
            else:
                for book_id in book_id_set:
                    book_data = game_config.config_book[book_id]
                    son_type_name = game_config.config_book_type[book_data.type].son_type_name
                    book_text = f"  [{str(book_id).rjust(3,'0')}]({son_type_name}){book_data.name}"

                    button_draw = draw.LeftButton(
                        _(book_text),
                        _(str(book_id)),
                        self.width,
                        cmd_func=self.read,
                        args=(book_id,),
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

    def read(self, book_id):
        """读选择的书"""
        character.init_character_behavior_start_time(0, cache.game_time)
        character_data: game_type.Character = cache.character_data[0]
        book_data = game_config.config_book[book_id]
        character_data.behavior.behavior_id = constant.Behavior.READ_BOOK
        character_data.state = constant.CharacterStatus.STATUS_READ_BOOK
        character_data.behavior.book_id = book_id
        character_data.behavior.book_name = book_data.name
        character_data.behavior.duration = 30
        update.game_update_flow(30)


class Take_Care_Baby_Panel:
    """
    用于照顾婴儿的面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.now_panel = _("照顾婴儿")
        """ 当前绘制的页面 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """

    def draw(self):
        """绘制对象"""

        title_text = "照顾婴儿"
        title_draw = draw.TitleLineDraw(title_text, self.width)

        while 1:
            return_list = []
            title_draw.draw()

            # 输出提示信息
            info_draw = draw.NormalDraw()
            info_text = "\n当前育儿室正在照料的婴儿有：\n\n"
            info_draw.text = info_text
            info_draw.draw()

            # 遍历婴儿名字并输出按钮
            for i in range(len(cache.npc_tem_data)):
                chara_id = i + 1
                if cache.character_data[chara_id].talent[101]:
                    name = cache.character_data[chara_id].name
                    adv_id = cache.character_data[chara_id].adv
                    button_text = f"[{str(adv_id).rjust(4,'0')}]:{name} "

                    button_draw = draw.LeftButton(
                        _(button_text),
                        _(str(adv_id)),
                        self.width,
                        cmd_func=self.choice_take_care,
                        args=(chara_id,),
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

    def choice_take_care(self, chara_id):
        """选择照顾的方式"""
        self.target_chara_id = chara_id
        name = cache.character_data[self.target_chara_id].name

        button_text_list = ["抱一抱她","哼唱儿歌","喂奶","换尿布","教她说话","给她玩玩具"]

        while 1:
            return_list = []

            # 输出提示信息
            info_draw = draw.NormalDraw()
            info_text = f"\n选择照顾[{name}]的方式：\n\n"
            info_draw.text = info_text
            info_draw.draw()

            for button_id in range(len(button_text_list)):
                button_text = f"[00{button_id}]:{button_text_list[button_id]}"
                button_draw = draw.LeftButton(
                    _(button_text),
                    _(str(button_id)),
                    self.width,
                    cmd_func=self.settle_take_care,
                    args=(button_id,),
                    )
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


    def settle_take_care(self, instruct_id):
        """结算照顾指令"""
        character.init_character_behavior_start_time(0, cache.game_time)
        character_data: game_type.Character = cache.character_data[0]
        character_data.target_character_id = self.target_chara_id

        # button_text_list = ["抱一抱她","哼唱儿歌","喂奶","换尿布","教她说话","给她玩玩具"]

        if instruct_id == 0:
            character_data.behavior.behavior_id = constant.Behavior.HOLD_CHILD
            character_data.state = constant.CharacterStatus.STATUS_HOLD_CHILD
        elif instruct_id == 1:
            character_data.behavior.behavior_id = constant.Behavior.SING_CHILDREN_SONG
            character_data.state = constant.CharacterStatus.STATUS_SING_CHILDREN_SONG
        elif instruct_id == 2:
            character_data.behavior.behavior_id = constant.Behavior.NUIRSE_CHILD
            character_data.state = constant.CharacterStatus.STATUS_NUIRSE_CHILD
        elif instruct_id == 3:
            character_data.behavior.behavior_id = constant.Behavior.CHANGE_DIAPERS
            character_data.state = constant.CharacterStatus.STATUS_CHANGE_DIAPERS
        elif instruct_id == 4:
            character_data.behavior.behavior_id = constant.Behavior.TEACH_TALK
            character_data.state = constant.CharacterStatus.STATUS_TEACH_TALK
        elif instruct_id == 5:
            character_data.behavior.behavior_id = constant.Behavior.GIVE_TOY
            character_data.state = constant.CharacterStatus.STATUS_GIVE_TOY

        character_data.behavior.duration = 30
        update.game_update_flow(30)


class Chose_First_bonus_ability_Panel:
    """
    用于初始奖励中的能力选择的面板
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.chose_ability_id = 0
        """ 选择的能力ID """

    def draw(self):
        """绘制对象"""

        while 1:
            return_list = []
            line = draw.LineDraw("-", window_width)
            line.draw()
            now_npc_draw = draw.NormalDraw()
            if self.chose_ability_id != 0:
                ability_name = game_config.config_ability[self.chose_ability_id].name
                now_npc_text = f"当前选择的能力为{ability_name}，请选择新的能力："
            else:
                now_npc_text = f"当前没有选择能力，请选择："
            now_npc_draw.text = now_npc_text
            now_npc_draw.draw()
            line_feed.draw()

            # 遍历所有可以提升的能力
            for cid in game_config.config_ability:
                if 40 <= cid <= 49:
                    ability_data = game_config.config_ability[cid]
                    button_text = f"[{cid}]{ability_data.name}"
                    button_draw = draw.LeftButton(
                    _(button_text),
                    _(button_text),
                    int(len(button_text)*2),
                    cmd_func=self.chose_this_ability,
                    args=cid,
                    )
                    button_draw.draw()
                    return_list.append(button_draw.return_text)

            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn in return_list:
                break

    def chose_this_ability(self, ability_id):
        """选项1"""
        self.chose_ability_id = ability_id
        cache.first_bonus[21] = ability_id


class Sleep_Panel:
    """
    用于选择睡眠时间的面板
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.close_door_flag = True
        """ 关门情况 """

    def draw(self):
        """绘制对象"""
        pl_character_data: game_type.Character = cache.character_data[0]

        # 计算回复时间
        hp_recover_time = int((pl_character_data.hit_point_max - pl_character_data.hit_point) / 100 / 60)
        mp_recover_time = int((pl_character_data.mana_point_max - pl_character_data.mana_point) / 150 / 60)
        need_time = max(hp_recover_time, mp_recover_time)
        need_time = max(need_time, 1)
        self.sleep_time = need_time

        while 1:
            return_list = []
            line = draw.LineDraw("-", window_width)
            line.draw()
            now_draw = draw.NormalDraw()

            # 计算地点数据
            now_position = pl_character_data.position
            now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
            now_scene_data = cache.scene_data[now_scene_str]

            # 地点关门判定的三个分支
            if now_scene_data.close_type == 0:
                info_text = "\n 当前地点无法关门，"
            elif now_scene_data.close_type == 1:
                info_text = "\n 当前地点可以关门，关上之后其他人就进不来了，"
            else:
                info_text = "\n 当前地点有可以关门的小隔间，关上后别人无法发现隔间内的人，但仍可以进入该地点，"
            info_text += "当前：   "
            now_draw.text = info_text
            now_draw.draw()

            # 绘制关门按钮
            button_text = " [关门] " if self.close_door_flag else " [不关门] "
            button_draw = draw.CenterButton(button_text, button_text, len(button_text)*2, cmd_func=self.close_door_switch)
            button_draw.draw()
            return_list.append(button_draw.return_text)

            now_draw_text = f"\n\n 预计完全回复最少需要{need_time}小时，当前睡眠时间为：{self.sleep_time}小时     "
            now_draw.text = now_draw_text
            now_draw.draw()

            now_draw_text = f"\n 睡眠时间选择："
            now_draw.text = now_draw_text
            now_draw.draw()
            for i in [1,4,8]:
                button_text = f" [{i}小时] "
                button_draw = draw.CenterButton(button_text, button_text, len(button_text)*2, cmd_func=self.fast_choice_sleep_time, args=i)
                button_draw.draw()
                return_list.append(button_draw.return_text)

            button_text = " [自定义睡眠时间] "
            button_draw = draw.CenterButton(button_text, "请输入睡眠时间(最小1小时，最大8小时)：", len(button_text)*2, cmd_func=self.input_sleep_time)
            button_draw.draw()
            return_list.append(button_draw.return_text)

            line_feed.draw()
            line_feed.draw()
            line_feed.draw()
            yes_draw = draw.CenterButton(_("[确定]"), _("确定\n\n"), window_width/2)
            yes_draw.draw()
            return_list.append(yes_draw.return_text)
            back_draw = draw.CenterButton(_("[返回]"), _("返回\n"), window_width/2)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            line_feed.draw()
            line_feed.draw()

            yrn = flow_handle.askfor_all(return_list)
            if yrn == yes_draw.return_text:
                # 关门
                if self.close_door_flag:
                    cache.scene_data[now_scene_str].close_flag = now_scene_data.close_type
                # 睡眠
                sleep_time = self.sleep_time * 60
                pl_character_data.behavior.duration = sleep_time
                pl_character_data.behavior.behavior_id = constant.Behavior.SLEEP
                pl_character_data.state = constant.CharacterStatus.STATUS_SLEEP

                pl_character_data.action_info.sleep_time = cache.game_time # 记录睡觉时间
                pl_character_data.action_info.wake_time = game_time.get_sub_date(minute=sleep_time, old_date=cache.game_time) # 记录醒来时间
                # print(f"debug 玩家睡觉，睡觉时间 = {pl_character_data.action_info.sleep_time},醒来时间 = {pl_character_data.action_info.wake_time}")
                cache.wframe_mouse.w_frame_skip_wait_mouse = 1
                update.game_update_flow(sleep_time)
                break
            elif yrn == back_draw.return_text:
                break

    def input_sleep_time(self):
        """输入睡眠时间"""
        while 1:
            user_input = flow_handle.askfor_str(_("请输入睡眠时间(最小1小时，最大8小时)："))
            try:
                user_input = int(user_input)
            except:
                continue
            if user_input <= 0:
                continue
            elif user_input > 0:
                if user_input > 8:
                    user_input = 8
                self.sleep_time = user_input
                break

    def fast_choice_sleep_time(self, sleep_time):
        """快速选择睡眠时间"""
        self.sleep_time = sleep_time

    def close_door_switch(self):
        """关门开关"""
        self.close_door_flag = not self.close_door_flag
