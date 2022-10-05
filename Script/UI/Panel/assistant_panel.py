from typing import Tuple, Dict
from types import FunctionType
from uuid import UUID
from Script.Core import cache_control, game_type, get_text, flow_handle, text_handle, constant, py_cmd
from Script.Design import map_handle, cooking, update
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


class Assistant_Panel:
    """
    用于查看助理界面面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.now_panel = _("指派助理")
        """ 当前绘制的食物类型 """
        self.handle_panel: panel.PageHandlePanel = None
        """ 当前名字列表控制面板 """

    def draw(self):
        """绘制对象"""
        scene_position = cache.character_data[0].position
        scene_position_str = map_handle.get_map_system_path_str_for_list(scene_position)
        scene_name = cache.scene_data[scene_position_str].scene_name
        title_draw = draw.TitleLineDraw("指派助理", self.width)
        character_data: game_type.Character = cache.character_data[0]

        self.handle_panel = panel.PageHandlePanel([], SeeAssistantButtonList, 10, 1, self.width, 1, 1, 0)
        cooking.init_makefood_data()
        while 1:
            py_cmd.clr_cmd()
            if character_data.assistant_character_id != 0:
                button_text_list = ["选择助理","跟随服务","辅佐服务(未实装)","加班服务(未实装)","送饭服务(未实装)","早安服务(未实装)","晚安服务(未实装)","同居服务(未实装)","助攻服务(未实装)","性处理服务(未实装)"]
            else:
                button_text_list = ["选择助理"]

            self.handle_panel.text_list = button_text_list
            self.handle_panel.update()
            title_draw.draw()
            return_list = []

            line_feed.draw()
            self.handle_panel.draw()
            return_list.extend(self.handle_panel.return_list)
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

class SeeAssistantButtonList:
    """
    点击后可调整各助理选项的按钮对象
    Keyword arguments:
    text -- 选项名字
    width -- 最大宽度
    is_button -- 绘制按钮
    num_button -- 绘制数字按钮
    button_id -- 数字按钮id
    """

    def __init__(
        self, text: str, width: int, is_button: bool, num_button: bool, button_id: int
    ):
        """初始化绘制对象"""

        self.button_name_text: str = text
        """ 指令名字绘制文本 """
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

        character_data: game_type.Character = cache.character_data[0]
        target_data: game_type.Character = cache.character_data[character_data.assistant_character_id]

        # 按钮绘制
        name_draw = draw.NormalDraw()

        index_text = text_handle.id_index(button_id)
        button_text = f"{index_text}{self.button_name_text}"

        # 无助理时0号指令可以选择助理，其他指令不绘制
        if button_id == 0 or character_data.assistant_character_id != 0:
            '''
            选择助理 当前助理：阿米娅
            助理常时跟随 否/是
            仅由助理辅助工作系指令 否/是
            博士睡觉后自动加班到自己睡觉 否/是
            送饭服务 否/买午饭/买三餐/手制午饭/手制三餐
            早安服务 否/早安叫起床/早安吻/早安咬
            晚安服务 否/晚安叫起床/晚安吻/晚安咬
            同居服务 否/是
            助攻服务 否/是
            性处理服务 否/被动接受(非本番)/被动接受(含本番)/主动请求(非本番)/主动请求(含本番)
            '''
            # button_text_list = ["选择助理","助理常时跟随","仅由助理辅助工作系指令","博士睡觉后自动加班到自己睡觉","送饭服务","早安服务","晚安服务","同居服务","助攻服务","性处理服务"]

            # 0号指令,选择助理
            if self.button_id == 0:
                if character_data.assistant_character_id == 0:
                    button_text += f"    当前无助理"
                else:
                    assistant_name = target_data.name
                    button_text += f"    当前助理：{assistant_name}"

            # 1号指令,助理常时跟随
            elif self.button_id == 1:
                if target_data.assistant_state.always_follow == 0:
                    button_text += f"    否"
                elif target_data.assistant_state.always_follow == 1:
                    button_text += f"    智能跟随（在生理需求时，如吃饭/上厕所/需要休息等，会暂离，完成后再回来）"
                elif target_data.assistant_state.always_follow == 2:
                    button_text += f"    强制跟随（测试用，会影响一部分游戏机能）"
                elif target_data.assistant_state.always_follow == 3:
                    button_text += f"    在博士办公室一趟（抵达后会如果博士不在，则等待半小时）"

            # 2号指令,仅由助理辅助工作系指令
            elif self.button_id == 2:
                if target_data.assistant_state.always_help_work:
                    button_text += f"    是，仅由助理辅助工作系指令"
                else:
                    button_text += f"    否"

            # 3号指令,博士睡觉后自动加班到自己睡觉
            elif self.button_id == 3:
                if target_data.assistant_state.work_until_sleep:
                    button_text += f"    是，博士睡觉后会自动加班到自己睡觉"
                else:
                    button_text += f"    否"

            # 4号指令,送饭服务
            elif self.button_id == 4:
                if target_data.assistant_state.offer_food == 0:
                    button_text += f"    否"
                elif target_data.assistant_state.offer_food == 1:
                    button_text += f"    帮忙买午饭"
                elif target_data.assistant_state.offer_food == 2:
                    button_text += f"    帮忙买三餐"
                elif target_data.assistant_state.offer_food == 3:
                    button_text += f"    亲手做午饭"
                elif target_data.assistant_state.offer_food == 4:
                    button_text += f"    亲手做三餐"
                button_text += f"(强制跟随状态下无效)"

            # 5号指令,早安服务
            elif self.button_id == 5:
                if target_data.assistant_state.good_morning == 0:
                    button_text += f"    否"
                elif target_data.assistant_state.good_morning == 1:
                    button_text += f"    早安叫起床"
                elif target_data.assistant_state.good_morning == 2:
                    button_text += f"    叫起床+早安吻"
                elif target_data.assistant_state.good_morning == 3:
                    button_text += f"    叫起床+早安咬"

            # 6号指令,晚安服务
            elif self.button_id == 6:
                if target_data.assistant_state.good_evening == 0:
                    button_text += f"    否"
                elif target_data.assistant_state.good_evening == 1:
                    button_text += f"    晚安催睡觉"
                elif target_data.assistant_state.good_evening == 2:
                    button_text += f"    催睡觉+晚安吻"
                elif target_data.assistant_state.good_evening == 3:
                    button_text += f"    催睡觉+早安咬"

            # 7号指令,同居服务
            elif self.button_id == 7:
                if target_data.assistant_state.live_together:
                    button_text += f"    是"
                else:
                    button_text += f"    否"

            # 8号指令,助攻服务
            elif self.button_id == 8:
                if target_data.assistant_state.help_chase:
                    button_text += f"    是，会在攻略他人时提供加值"
                else:
                    button_text += f"    否"

            # 9号指令,性处理服务
            elif self.button_id == 9:
                if target_data.assistant_state.help_sex == 0:
                    button_text += f"  否"
                elif target_data.assistant_state.help_sex == 1:
                    button_text += f"  被动接受(非本番)"
                elif target_data.assistant_state.help_sex == 2:
                    button_text += f"  被动接受(含本番)"
                elif target_data.assistant_state.help_sex == 3:
                    button_text += f"  主动请求(非本番)"
                elif target_data.assistant_state.help_sex == 4:
                    button_text += f"  主动请求(含本番)"

            name_draw = draw.LeftButton(
                button_text, self.button_return, self.width, cmd_func=self.chose_button
            )
            self.button_return = text
            self.now_draw = name_draw
            self.draw_text = button_text

        """ 绘制的对象 """
        self.now_draw = name_draw

    def chose_button(self):
        """玩家点击了选项"""
        update.game_update_flow(0)
        character_data: game_type.Character = cache.character_data[0]
        target_data: game_type.Character = cache.character_data[character_data.assistant_character_id]

        # 0号指令,选择助理
        if self.button_id == 0:

            self.handle_panel = panel.PageHandlePanel([], SeeNPCButtonList, 999, 10, self.width, 1, 1, 0)

            while 1:

                # 显示当前助手
                character_data: game_type.Character = cache.character_data[0]
                target_data: game_type.Character = cache.character_data[character_data.assistant_character_id]
                line = draw.LineDraw("-", self.width)
                line.draw()
                now_npc_draw = draw.NormalDraw()
                if character_data.assistant_character_id != 0:
                    now_npc_text = f"当前助理为{target_data.name}，请选择新的助理："
                else:
                    now_npc_text = f"当前无助理，请选择新的助理："
                now_npc_draw.text = now_npc_text
                now_npc_draw.draw()
                line_feed.draw()

                # 遍历所有NPC
                id_list = [i + 1 for i in range(len(cache.npc_tem_data))]
                # print("debug id_list = ",id_list)
                self.handle_panel.text_list = id_list
                self.handle_panel.update()
                self.handle_panel.draw()
                return_list = []
                return_list.extend(self.handle_panel.return_list)
                back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
                back_draw.draw()
                line_feed.draw()
                return_list.append(back_draw.return_text)
                yrn = flow_handle.askfor_all(return_list)
                if yrn in return_list:
                    break

        # 1号指令,助理常时跟随
        elif self.button_id == 1:
            if target_data.assistant_state.always_follow == 3:
                target_data.assistant_state.always_follow = 0
            else:
                target_data.assistant_state.always_follow += 1
            # 同时结算跟随状态
            target_data.is_follow = target_data.assistant_state.always_follow

        # 2号指令,仅由助理辅助工作系指令
        elif self.button_id == 2:
            target_data.assistant_state.always_help_work = not target_data.assistant_state.always_help_work

        # 3号指令,博士睡觉后自动加班到自己睡觉
        elif self.button_id == 3:
            target_data.assistant_state.work_until_sleep = not target_data.assistant_state.work_until_sleep

        # 4号指令,送饭服务
        elif self.button_id == 4:
            if target_data.assistant_state.offer_food == 4:
                target_data.assistant_state.offer_food = 0
            else:
                target_data.assistant_state.offer_food += 1

        # 5号指令,早安服务
        elif self.button_id == 5:
            if target_data.assistant_state.good_morning == 3:
                target_data.assistant_state.good_morning = 0
            else:
                target_data.assistant_state.good_morning += 1

        # 6号指令,晚安服务
        elif self.button_id == 6:
            if target_data.assistant_state.good_evening == 3:
                target_data.assistant_state.good_evening = 0
            else:
                target_data.assistant_state.good_evening += 1

        # 7号指令,同居服务
        elif self.button_id == 7:
            target_data.assistant_state.live_together = not target_data.assistant_state.live_together

        # 8号指令,助攻服务
        elif self.button_id == 8:
            target_data.assistant_state.help_chase = not target_data.assistant_state.help_chase

        # 9号指令,性处理服务
        elif self.button_id == 9:
            if target_data.assistant_state.help_sex == 4:
                target_data.assistant_state.help_sex = 0
            else:
                target_data.assistant_state.help_sex += 1

    def button_0(self,ass_id: int):
        """选项1"""
        character_data: game_type.Character = cache.character_data[0]
        character_data.assistant_character_id = ass_id

    def draw(self):
        """绘制对象"""
        self.now_draw.draw()



class SeeNPCButtonList:
    """
    点击后可选择作为助理的NPC的按钮对象
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
        """ 指令名字绘制文本 """
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
        button_text = f"[{target_data.adv}：{target_data.name}]"

        # 按钮绘制

        name_draw = draw.CenterButton(
            button_text, self.button_return, self.width, cmd_func=self.button_0
        )
        # self.button_return = NPC_id
        self.now_draw = name_draw
        self.draw_text = button_text

        """ 绘制的对象 """
        self.now_draw = name_draw


    def button_0(self):
        """选项1"""
        character_data: game_type.Character = cache.character_data[0]

        # 去掉旧助理的跟随状态
        old_assistant_data: game_type.Character = cache.character_data[character_data.assistant_character_id]
        old_assistant_data.assistant_state.always_follow = 0

        # 判断旧助理是否是玩家自己
        pl_flag = False
        if character_data.assistant_character_id == 0:
            pl_flag = True

        line = draw.LineDraw("-", window_width)
        line.draw()
        info_draw = draw.WaitDraw()
        info_text = ""

        if self.NPC_id == character_data.assistant_character_id:
            character_data.assistant_character_id = 0
        else:
            character_data.assistant_character_id = self.NPC_id
            new_assistant_data: game_type.Character = cache.character_data[character_data.assistant_character_id]
            new_assistant_data.assistant_state.always_follow = 1
            info_text += f"\n{new_assistant_data.name}成为助理干员了，并默认开启智能跟随模式\n"
        if not pl_flag:
            info_text += f"\n\n{old_assistant_data.name}不再是助理干员了，她的跟随状态也一并取消\n\n"
        info_draw.text = info_text
        info_draw.width = self.width
        info_draw.draw()

    def draw(self):
        """绘制对象"""
        self.now_draw.draw()

