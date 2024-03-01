from typing import Tuple, Dict
from types import FunctionType
from uuid import UUID
from Script.Core import cache_control, game_type, get_text, flow_handle, text_handle, constant, py_cmd
from Script.Design import handle_premise, attr_calculation, update, character_handle
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

def chose_assistant():
    """选择助理"""

    handle_panel = panel.PageHandlePanel([], SeeNPCButtonList, 999, 8, window_width, 1, 1, 0)

    while 1:

        # 显示当前助手
        character_data: game_type.Character = cache.character_data[0]
        target_data: game_type.Character = cache.character_data[character_data.assistant_character_id]
        line = draw.LineDraw("-", window_width)
        line.draw()
        now_npc_draw = draw.NormalDraw()
        if character_data.assistant_character_id != 0:
            now_npc_text = f"当前助理为{target_data.name}，请选择新的助理："
        else:
            now_npc_text = f"当前无助理，请选择新的助理："
        now_npc_draw.text = now_npc_text
        now_npc_draw.draw()
        line_feed.draw()
        line_feed.draw()

        # 去掉玩家
        cache.npc_id_got.discard(0)
        # 去掉访客
        id_list = [i for i in cache.npc_id_got if i not in cache.rhodes_island.visitor_info]
        # print("debug id_list = ",id_list)
        handle_panel.text_list = id_list
        handle_panel.update()
        handle_panel.draw()
        return_list = []
        return_list.extend(handle_panel.return_list)
        line_feed.draw()
        back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
        back_draw.draw()
        line_feed.draw()
        return_list.append(back_draw.return_text)
        yrn = flow_handle.askfor_all(return_list)
        if yrn in return_list:
            break


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
        self.now_panel = _("助理相关调整")
        """ 当前绘制的食物类型 """

    def draw(self):
        """绘制对象"""
        title_draw = draw.TitleLineDraw("助理相关调整", self.width)

        while 1:
            character_data: game_type.Character = cache.character_data[0]
            target_data: game_type.Character = cache.character_data[character_data.assistant_character_id]

            title_draw.draw()
            py_cmd.clr_cmd()
            return_list = []

            info_draw = draw.NormalDraw()
            info_draw.text = f"\n●助理会自动获得打开玩家房门的权限，因此在执行问候、同居等服务时可以自由进出玩家房间\n\n"
            info_draw.draw()


            button_text = f"[001]助理服务"
            if character_data.assistant_character_id == 0:
                button_text += f"    当前无助理"
            else:
                assistant_name = target_data.name
                button_text += f"    当前助理：{assistant_name}"

            button_draw = draw.LeftButton(button_text, button_text, self.width, cmd_func=self.chose_button, args=(0,1))
            button_draw.draw()
            return_list.append(button_draw.return_text)
            line_feed.draw()

            if character_data.assistant_character_id != 0:

                # 跟随服务
                button_text = f"[002]跟随服务"

                if target_data.sp_flag.is_follow == 0:
                    button_text += f"    否"
                elif target_data.sp_flag.is_follow == 1:
                    button_text += f"    智能跟随（在吃饭/上厕所/休息/睡觉等生理需求时会暂离，其他情况下跟随）"
                elif target_data.sp_flag.is_follow == 2:
                    button_text += f"    强制跟随（测试用，会影响一部分游戏机能）"
                elif target_data.sp_flag.is_follow == 3:
                    button_text += f"    来博士办公室一趟（抵达后会如果博士不在，则最多等待半小时）"
                elif target_data.sp_flag.is_follow == 4:
                    button_text += f"    前往博士当前位置（抵达后会最多等待半小时）"

                button_draw = draw.LeftButton(button_text, button_text, self.width, cmd_func=self.chose_button, args=(2,4))
                button_draw.draw()
                return_list.append(button_draw.return_text)
                line_feed.draw()

                # 开始遍历全部助理服务
                for cid in game_config.config_assistant_services:
                    # 跳过未实装的服务
                    if cid == 9:
                        continue
                    # 获取助理服务数据
                    service_data = game_config.config_assistant_services[cid]
                    service_option_data = game_config.config_assistant_services_option[cid]
                    service_option_text_all = service_option_data[0]
                    service_option_text_now = service_option_text_all[target_data.assistant_services[cid]]
                    service_option_len = len(service_option_text_all)

                    # 绘制输出文本
                    button_text = f"[{str(cid).rjust(3,'0')}]{service_data.name}"
                    button_text += f"    {service_option_text_now}"
                    button_draw = draw.LeftButton(button_text, button_text, self.width, cmd_func=self.chose_button, args=(cid,service_option_len))
                    button_draw.draw()
                    return_list.append(button_draw.return_text)
                    line_feed.draw()

            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break


    def chose_button(self, service_cid:int, service_option_len:int):
        """玩家点击了选项"""
        character_data: game_type.Character = cache.character_data[0]
        target_data: game_type.Character = cache.character_data[character_data.assistant_character_id]

        # 选择助理
        if service_cid == 0:
            chose_assistant()
        # 跟随服务
        elif service_cid == 2:
            if target_data.sp_flag.is_follow == 1:
                target_data.sp_flag.is_follow = 0
            else:
                target_data.sp_flag.is_follow += 1
        # 其他服务
        else:
            if target_data.assistant_services[service_cid] == service_option_len - 1:
                target_data.assistant_services[service_cid] = 0
            else:
                # 判断是否符合解锁条件
                service_option_data = game_config.config_assistant_services_option[service_cid]
                service_option_text_all = service_option_data[0]
                service_option_text_next = service_option_text_all[target_data.assistant_services[service_cid]+1]
                service_require_text_all = service_option_data[1]
                service_require_text_next = service_require_text_all[target_data.assistant_services[service_cid]+1]
                judge, reason = attr_calculation.judge_require([service_require_text_next], character_data.assistant_character_id)

                if judge:
                    target_data.assistant_services[service_cid] += 1
                # debug模式下不判断解锁条件
                elif cache.debug_mode:
                    target_data.assistant_services[service_cid] += 1
                # 不符合解锁条件时输出提示信息并归零
                else:
                    info_draw = draw.WaitDraw()
                    info_text = f"\n  ○更改失败，[{service_option_text_next}]{reason}\n"
                    info_draw.text = info_text
                    info_draw.draw()
                    target_data.assistant_services[service_cid] = 0

            # 结算附带的属性变化
            self.settlement_of_associated_attribute(service_cid, service_option_len)


    def settlement_of_associated_attribute(self, service_cid:int, service_option_len:int):
        """结算附带的属性变化"""
        character_data: game_type.Character = cache.character_data[0]
        target_data: game_type.Character = cache.character_data[character_data.assistant_character_id]

        # 计算二段结算的开头、结尾、当前索引
        start_index_dict = {3:1406, 4:1408, 5:1412, 6:1416, 7:1419, 8:1421}
        start_index = start_index_dict[service_cid]
        end_index = start_index + service_option_len
        now_index = start_index + target_data.assistant_services[service_cid]
        # print(f"debug start_index = {start_index}, end_index = {end_index}, now_index = {now_index}")

        # 去掉选助理的1号选项
        if service_cid >= 2:

            # 清除和赋予二段结算
            # 跟随服务单独计算
            if service_cid == 2:
                for i in {1403,1404,1405}:
                    target_data.second_behavior[i] = 0
                now_index = target_data.sp_flag.is_follow + 1403
                target_data.second_behavior[now_index] = 1
            else:
                # 先清零同类下的其他二段结算
                for i in range(start_index, end_index):
                    target_data.second_behavior[i] = 0
                # 再设置当前二段结算
                target_data.second_behavior[now_index] = 1

            # 同居服务的宿舍改变
            if service_cid == 7:
                if target_data.assistant_services[service_cid] == 1:
                    target_data.pre_dormitory = target_data.dormitory
                    target_data.dormitory = "中枢\博士房间"
                elif target_data.dormitory == "中枢\博士房间":
                    target_data.dormitory = target_data.pre_dormitory
                # print(f"debug target_data.dormitory = {target_data.dormitory}")


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
        button_text = f"[{str(target_data.adv).rjust(4,'0')}]：{target_data.name}"

        # 按钮绘制

        name_draw = draw.LeftButton(
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
        old_assistant_data.sp_flag.is_follow = 0
        # 去掉旧助理的同居状态
        if old_assistant_data.dormitory == "中枢\博士房间":
            old_assistant_data.dormitory = old_assistant_data.pre_dormitory
        # 重置旧助理的助理服务数据体
        old_assistant_data.assistant_services = attr_calculation.get_assistant_services_zero()

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
        elif handle_premise.handle_unnormal_27(self.NPC_id):
            info_text += f"\n{new_assistant_data.name}的状态异常，无法任命为助理干员\n"
            pl_flag = True
        else:
            character_data.assistant_character_id = self.NPC_id
            new_assistant_data: game_type.Character = cache.character_data[character_data.assistant_character_id]
            new_assistant_data.sp_flag.is_follow = 1
            new_assistant_data.second_behavior[1401] = 1
            info_text += f"\n{new_assistant_data.name}成为助理干员了，并默认开启智能跟随模式\n"
        if not pl_flag:
            old_assistant_data.second_behavior[1402] = 1
            info_text += f"\n\n{old_assistant_data.name}不再是助理干员了，已清零助理服务相关的设置\n\n"
        info_draw.text = info_text
        info_draw.width = self.width
        info_draw.draw()

    def draw(self):
        """绘制对象"""
        self.now_draw.draw()

