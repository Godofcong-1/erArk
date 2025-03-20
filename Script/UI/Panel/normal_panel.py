from typing import List
from types import FunctionType
from Script.UI.Moudle import draw, panel
from Script.Core import (
    cache_control,
    get_text,
    game_type,
    flow_handle,
    constant,
    py_cmd
)
from Script.Config import game_config, normal_config
from Script.Design import update, map_handle, character, game_time, cooking, handle_premise

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

def common_select_npc_button_list_func(now_draw_panel: panel.PageHandlePanel, title_text: str = '', info_text:str = '') -> list:
    """
    通用npc选择按钮列表函数\n
    Keyword arguments:\n
    now_draw_panel -- 当前绘制面板，即CommonSelectNPCButtonList\n
    now_draw_panel.text_list -- 最终按钮列表，每个子列表里\n：0号元素为角色id，1号元素为按钮要调用的函数source_func，2号元素为已选择角色id列表，默认值为空\n
    title_text -- 标题文本\n
    info_text -- 信息文本\n
    return\n
    return_list -- 返回按钮列表，包括返回按钮 "返回" \n
    """

    line_feed.draw()
    # 绘制标题
    if title_text:
        title_draw = draw.TitleLineDraw(title_text, window_width)
        title_draw.draw()
    # 绘制分割线
    else:
        line_draw = draw.LineDraw("-", window_width)
        line_draw.draw()
    line_feed.draw()
    # 绘制信息
    if info_text:
        info_draw = draw.NormalDraw()
        info_draw.text = info_text
        info_draw.width = window_width
        info_draw.draw()
        line_feed.draw()
    return_list = []

    # 绘制面板
    now_draw_panel.update()
    now_draw_panel.draw()
    return_list.extend(now_draw_panel.return_list)

    # 绘制返回按钮
    line_feed.draw()
    back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
    back_draw.draw()
    line_feed.draw()
    return_list.append(back_draw.return_text)

    return return_list

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
        # 如果当前地点已询问过关门，则在移动前不询问第二次
        if character_data.action_info.ask_close_door_flag:
            return 1
        else:
            character_data.action_info.ask_close_door_flag = True

        title_text = _("关门")

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
                info_text = _("\n当前地点无法关门，要继续吗：")
            elif now_scene_data.close_type == 1:
                info_text = _("\n当前地点可以关门，关上之后里面的人可以出去，但外面的人将不能进来，要关门吗：")
            else:
                info_text = _("\n你正在一个可以关门的小隔间内，关上后别人仍可以进入该地点，但无法发现隔间内的人，要关门吗：")

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
                elif now_scene_data.close_type == 0 and askfor_panel_return_list[yrn] == askfor_list[1]:
                    return -1
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

        title_text = _("读书")
        title_draw = draw.TitleLineDraw(title_text, self.width)

        while 1:
            return_list = []
            title_draw.draw()

            # 当前借书数量信息
            book_id_set = character_data.entertainment.borrow_book_id_set

            # 如果未借书的话直接输出提示信息
            if len(book_id_set) == 0:
                info_draw = draw.NormalDraw()
                borrow_limit_text = _("\n当前未持有书籍，请前去图书馆借书\n")
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
            if yrn in return_list:
                cache.now_panel_id = constant.Panel.IN_SCENE
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


class Bondage_Panel:
    """
    用于绳子的面板对象
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

        character_data: game_type.Character = cache.character_data[0]

        title_text = _("绳子")
        title_draw = draw.TitleLineDraw(title_text, self.width)

        while 1:
            return_list = []
            title_draw.draw()

            # 交互对象的捆绑状态
            target_character_id = character_data.target_character_id
            target_character_data: game_type.Character = cache.character_data[target_character_id]
            now_bondage_id = target_character_data.h_state.bondage
            now_bondage_data = game_config.config_bondage[now_bondage_id]

            # 输出提示信息
            info_draw = draw.NormalDraw()
            info_text = _("\n○捆绑下会持续获得欲情与苦痛，根据绑法的不同分为三级捆绑程度，程度越高的绑法获得的欲情与苦痛值越多\n")
            info_text += _("  当前被捆绑的状态为：")
            info_text += now_bondage_data.name
            info_draw.text = info_text
            info_draw.draw()
            line_feed.draw()

            # 四段捆绑等级
            level_text_list = [_("无"), _("低"), _("中"), _("高")]
            # 初始化捆绑计数
            level_count = -1

            # 遍历绳子捆绑数据
            for bondage_id in game_config.config_bondage:
                bondage_data = game_config.config_bondage[bondage_id]
                bondage_id_text = str(bondage_id).rjust(2,'0')
                bondage_lvel = bondage_data.level
                bondage_text = f"[{bondage_id_text}]{bondage_data.name}"

                # 用于在捆绑等级变化时更新文本
                if bondage_lvel > level_count:
                    level_count = bondage_lvel
                    line_feed.draw()
                    level_text = level_text_list[level_count]
                    level_draw = draw.NormalDraw()
                    level_draw.text = "  " + level_text + "："
                    level_draw.draw()

                button_draw = draw.LeftButton(
                    _(bondage_text),
                    _(str(bondage_id)),
                    20,
                    cmd_func=self.select_bondage,
                    args=(bondage_id,),
                    )
                # print(f"debug button_draw.text = {button_draw.text},button_draw.normal_style = {button_draw.normal_style}")
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
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def select_bondage(self, bondage_id):
        """赋予选择的捆绑"""
        from Script.Design import handle_instruct
        character_data: game_type.Character = cache.character_data[0]
        target_character_id = character_data.target_character_id
        target_character_data: game_type.Character = cache.character_data[target_character_id]
        target_character_data.h_state.bondage = bondage_id
        # 如果捆绑id为0，则解除捆绑
        if bondage_id == 0:
            handle_instruct.chara_handle_instruct_common_settle(constant.CharacterStatus.STATUS_UNBIND, judge = _("SM"))
        # 否则进行捆绑
        else:
            handle_instruct.chara_handle_instruct_common_settle(constant.CharacterStatus.STATUS_BIND, judge = _("SM"))


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

        title_text = _("照顾婴儿")
        title_draw = draw.TitleLineDraw(title_text, self.width)

        while 1:
            return_list = []
            title_draw.draw()

            # 输出提示信息
            info_draw = draw.NormalDraw()
            info_text = _("\n当前育儿室正在照料的婴儿有：\n\n")
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
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def choice_take_care(self, chara_id):
        """选择照顾的方式"""
        self.target_chara_id = chara_id
        name = cache.character_data[self.target_chara_id].name

        button_text_list = [_("抱一抱她"),_("哼唱儿歌"),_("喂奶"),_("换尿布"),_("教她说话"),_("给她玩玩具")]

        while 1:
            return_list = []

            # 输出提示信息
            info_draw = draw.NormalDraw()
            info_text = _("\n选择照顾[{0}]的方式：\n\n").format(name)
            info_draw.text = info_text
            info_draw.draw()

            for button_id in range(len(button_text_list)):
                button_text = _("[00{0}]:{1}").format(button_id, button_text_list[button_id])
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
                now_npc_text = _("当前选择的能力为{0}，请选择新的能力：").format(ability_name)
            else:
                now_npc_text = _("当前没有选择能力，请选择：")
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


class Fridge_Panel:
    """
    用于查看冰箱的面板
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """

    def draw(self):
        """绘制对象"""

        title_text = _("冰箱")
        title_draw = draw.TitleLineDraw(title_text, self.width)

        while 1:
            return_list = []
            title_draw.draw()
            now_draw = draw.NormalDraw()
            draw_text = _("\n 【母乳】\n")
            draw_text += _("  ○母乳可以被博士带走饮用或制作其他乳制品，有效期截止当天24点，到期后背包和冰箱里未使用的母乳会全部转化为资源【鲜母乳】\n")
            draw_text += _("  当前冰箱内各干员母乳情况：\n")
            now_draw.text = draw_text
            now_draw.draw()

            if len(cache.rhodes_island.milk_in_fridge) == 0:
                draw_text = _("\n    当前冰箱里没有母乳\n")
                now_draw.text = draw_text
                now_draw.draw()

            # 获得冰箱内的乳制品
            for character_id in cache.rhodes_island.milk_in_fridge:
                character_data = cache.character_data[character_id]
                character_name = character_data.name
                character_milk = cache.rhodes_island.milk_in_fridge[character_id]
                draw_text = ("  [{0}]{1}：{2}ml").format(str(character_data.adv).rjust(4,'0'), character_name, character_milk)
                draw_text = draw_text.ljust(20, "　")
                now_draw.text = draw_text
                now_draw.draw()
                # 拿走按钮
                button_text = _("  [带走]  ")
                button_draw = draw.CenterButton(
                    _(button_text),
                    _(button_text + f"_{character_id}"),
                    len(button_text)*2,
                    cmd_func=self.take_milk,
                    args=character_id,
                    )
                button_draw.draw()
                return_list.append(button_draw.return_text)
                # 转化按钮
                button_text = _("  [转化]  ")
                button_draw = draw.CenterButton(
                    _(button_text),
                    _(button_text + f"_{character_id}"),
                    len(button_text)*2,
                    cmd_func=self.turn_milk,
                    args=character_id,
                    )
                button_draw.draw()
                return_list.append(button_draw.return_text)
                line_feed.draw()

            line_feed.draw()
            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回\n"), window_width)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            line_feed.draw()

            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def take_milk(self, character_id: int):
        """拿走母乳并放进玩家背包"""
        pl_character_data: game_type.Character = cache.character_data[0]
        character_data = cache.character_data[character_id]

        # 创建食物对象，并放进玩家的背包里
        new_food = cooking.create_food("", 1001, 5, character_data.name)
        new_food.milk_ml = cache.rhodes_island.milk_in_fridge[character_id]
        pl_character_data.food_bag[new_food.uid] = new_food

        # 删除冰箱里的母乳
        del cache.rhodes_island.milk_in_fridge[character_id]

        now_draw = draw.WaitDraw()
        draw_text = _("\n  你将{0}的母乳（{1}ml）放进了背包\n").format(character_data.name, new_food.milk_ml)
        now_draw.text = draw_text
        now_draw.draw()

    def turn_milk(self, character_id: int):
        """转化母乳为资源【鲜母乳】"""
        character_data = cache.character_data[character_id]

        # 转化母乳为鲜母乳
        cache.rhodes_island.materials_resouce[31] += cache.rhodes_island.milk_in_fridge[character_id]

        now_draw = draw.WaitDraw()
        draw_text = _("\n  你将{0}的母乳（{1}ml）转化为了【鲜母乳】\n").format(character_data.name, cache.rhodes_island.milk_in_fridge[character_id])
        now_draw.text = draw_text
        now_draw.draw()

        # 删除冰箱里的母乳
        del cache.rhodes_island.milk_in_fridge[character_id]


class Order_Hotel_Room_Panel:
    """
    用于预订房间的面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.now_panel = _("预订房间")
        """ 当前绘制的页面 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """

    def draw(self):
        """绘制对象"""

        title_text = _("预订房间")
        title_draw = draw.TitleLineDraw(title_text, self.width)

        while 1:
            return_list = []
            title_draw.draw()

            # 输出提示信息
            info_draw = draw.NormalDraw()
            now_draw_text = ""
            now_draw_text += _("\n○酒店有标间、情趣主题房和顶级套房三种选择，高级的房间能够提供更好的氛围，本区的四家酒店可任意选择入住，退房时间均为次日中午12点\n")
            now_draw_text += _("  情趣主题房会免费赠送一瓶润滑液和五个避孕套，顶级套房则在时限内无限量供应所有H消耗品，并免费提供所有H道具的租用服务\n")
            now_draw_text += _("  请问要入住哪种房间呢？\n\n")
            info_draw.text = now_draw_text
            info_draw.draw()

            # 如果未预订房间的话直接输出按钮
            if cache.rhodes_island.love_hotel_room_lv == 0:
                room_text_list = [_("标间(2粉红凭证)"),_("情趣主题房(10粉红凭证)"),_("顶级套房(100粉红凭证)")]
                # 遍历房间类型并输出按钮
                for i in range(len(room_text_list)):
                    room_text = room_text_list[i]
                    button_draw = draw.LeftButton(
                        _(f"[{i}]" + room_text),
                        _(str(i)),
                        self.width,
                        cmd_func=self.order_room,
                        args=(i,),
                        )
                    return_list.append(button_draw.return_text)
                    button_draw.draw()
                    line_feed.draw()
            # 已预订房间则输出提示信息
            else:
                room_name = [_("标间"),_("情趣主题房"),_("顶级套房")]
                draw_text = _("当前已预订{0}，退房时间为{1}日12点\n").format(room_name[cache.rhodes_island.love_hotel_room_lv - 1], cache.character_data[0].action_info.check_out_time.day)
                info_draw.text = draw_text
                info_draw.draw()

            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def order_room(self, room_id):
        """预订房间"""
        room_price = [2, 10, 100]
        room_name = [_("标间"),_("情趣主题房"),_("顶级套房")]
        # 判断粉红凭证是否足够
        if cache.rhodes_island.materials_resouce[4] < room_price[room_id]:
            now_draw = draw.WaitDraw()
            draw_text = _("\n粉红凭证不足，无法预订{0}\n").format(room_name[room_id])
            now_draw.text = draw_text
            now_draw.draw()
            return
        # 进行结算
        cache.rhodes_island.materials_resouce[4] -= room_price[room_id]
        cache.rhodes_island.love_hotel_room_lv = room_id + 1
        pl_character_data: game_type.Character = cache.character_data[0]
        pl_character_data.action_info.check_out_time = game_time.get_sub_date(day=1, old_date=cache.game_time)
        pl_character_data.action_info.check_out_time = pl_character_data.action_info.check_out_time.replace(hour=12)
        # 情趣房的赠送
        if room_id == 1:
            pl_character_data.item[100] += 1
            pl_character_data.item[120] += 5
        # 输出预订成功信息
        now_draw = draw.WaitDraw()
        draw_text = _("\n成功预订了{0}，退房时间为{1}\n").format(room_name[room_id], pl_character_data.action_info.check_out_time)
        now_draw.text = draw_text
        now_draw.draw()

class CommonSelectNPCButtonList:
    """
    通用的从列表中选择目标干员的面板
    Keyword arguments:
    chara_info -- 列表，0号元素为角色id，1号元素为按钮要调用的函数source_func，2号元素为已选择角色id列表，默认值为空
    width -- 最大宽度
    is_button -- 绘制按钮
    num_button -- 绘制数字按钮
    button_id -- 数字按钮id
    """

    def __init__(
        self, chara_info: list, width: int, is_button: bool, num_button: bool, button_id: int
    ):
        """初始化绘制对象"""

        self.chara_id: int = chara_info[0]
        """ 角色id """
        self.source_func = chara_info[1]
        """ 按钮调用的函数 """
        self.chara_id_list: List[int] = chara_info[2] if len(chara_info) > 2 else []
        """ 已选择角色id列表 """
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

        character_data: game_type.Character = cache.character_data[self.chara_id]
        button_text = f"[{str(character_data.adv).rjust(4,'0')}]：{character_data.name}"

        draw_style = 'standard'
        # 如果当前角色已经被选择，则更改按钮样式
        if self.chara_id in self.chara_id_list:
            draw_style = 'gold_enrod'
        # 如果未选中且是有口上颜色的角色，则显示口上颜色
        elif character_data.text_color:
            draw_style = character_data.name

        # 按钮绘制
        name_draw = draw.LeftButton(
            button_text, character_data.name, self.width, normal_style=draw_style, cmd_func=self.source_func, args=(self.chara_id,)
        )
        self.button_return = name_draw.return_text
        """ 绘制的对象 """
        self.now_draw = name_draw
        self.draw_text = button_text

    def draw(self):
        """绘制对象"""
        self.now_draw.draw()
