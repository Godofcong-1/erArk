from types import FunctionType
from Script.Core import cache_control, game_type, get_text, flow_handle, text_handle, constant, py_cmd
from Script.Design import handle_premise, attr_calculation, map_handle, second_behavior
from Script.UI.Moudle import draw, panel
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

def get_assistant_candidates():
    """
    获取助理候选角色id列表
    """
    candidates = []
    npc_id_got_list = sorted(cache.npc_id_got)
    for npc_id in npc_id_got_list:
        # 跳过玩家
        if npc_id == 0:
            continue
        # 跳过2、7异常
        if handle_premise.handle_unnormal_27(npc_id):
            continue
        # 跳过监狱长
        if npc_id == cache.rhodes_island.current_warden_id:
            continue
        # 跳过访客
        if npc_id in cache.rhodes_island.visitor_info:
            continue
        candidates.append(npc_id)
    return candidates

def chose_assistant():
    """选择助理"""
    from Script.UI.Panel import common_select_NPC
    now_draw_panel : panel.PageHandlePanel = panel.PageHandlePanel([], common_select_NPC.CommonSelectNPCButtonList, 80, 8, window_width, 1, 0, 0)
    select_state = {}
    while 1:
        # 显示当前助手
        character_data: game_type.Character = cache.character_data[0]
        target_data: game_type.Character = cache.character_data[character_data.assistant_character_id]
        if character_data.assistant_character_id != 0:
            now_npc_text = _("当前助理为 [{0}]{1}，请选择新的助理：\n").format(str(target_data.adv).rjust(4,'0'), target_data.name)
        else:
            now_npc_text = _("当前无助理，请选择新的助理：\n")
        # 已选择的角色id列表
        selected_id_list = [character_data.assistant_character_id]
        final_list = []
        # 遍历候选角色id
        for npc_id in get_assistant_candidates():
            now_list = [npc_id, assistant_replace, selected_id_list]
            final_list.append(now_list)
        now_draw_panel.text_list = final_list

        # 调用通用选择按钮列表函数
        return_list, other_return_list, select_state = common_select_NPC.common_select_npc_button_list_func(now_draw_panel, _("选择助理"), now_npc_text, select_state)

        yrn = flow_handle.askfor_all(return_list)
        if yrn in return_list and yrn not in other_return_list:
            break


def select_random_assistant():
    """
    随机选择助理\n
    Keyword arguments:
    无\n
    Return arguments:
    无
    """

    # 随机选择
    assistant_id = random.choice(get_assistant_candidates())
    # 绘制提示信息
    info_draw = draw.WaitDraw()
    info_text = _("\n○本周抽签选中了{0}作为{1}的助理\n").format(cache.character_data[assistant_id].name, cache.character_data[0].name)
    info_draw.text = info_text
    info_draw.width = window_width
    info_draw.draw()
    # 开始替换助理
    assistant_replace(assistant_id)


def assistant_replace(new_assistant_id: int):
    """
    助理替换\n
    Keyword arguments:
    new_assistant_id -- 新助理角色id
    """
    character_data: game_type.Character = cache.character_data[0]

    # 判断是否有旧助理
    old_assistant_flag = True
    if character_data.assistant_character_id != 0:
        # 去掉旧助理的跟随状态
        old_assistant_data: game_type.Character = cache.character_data[character_data.assistant_character_id]
        old_assistant_data.sp_flag.is_follow = 0
        # 去掉旧助理的同居状态
        if character_data.assistant_character_id != 0 and old_assistant_data.dormitory == map_handle.get_map_system_path_str_for_list(["中枢", "博士房间"]):
            old_assistant_data.dormitory = old_assistant_data.pre_dormitory
        # 重置旧助理的助理服务数据体
        old_assistant_data.assistant_services = attr_calculation.get_assistant_services_zero()
    # 没有旧助理
    else:
        old_assistant_flag = False

    line = draw.LineDraw("-", window_width)
    line.draw()
    info_draw = draw.WaitDraw()
    info_text = ""

    # 新助理是旧助理时，仅取消该助理
    if new_assistant_id == character_data.assistant_character_id:
        character_data.assistant_character_id = 0
    # 新助理状态异常时，无法任命
    elif handle_premise.handle_unnormal_27(new_assistant_id):
        new_assistant_data: game_type.Character = cache.character_data[new_assistant_id]
        info_text += _("\n{0}的状态异常，无法任命为助理干员\n").format(new_assistant_data.name)
        old_assistant_flag = False
    # 正常情况下，设置新助理
    else:
        character_data.assistant_character_id = new_assistant_id
        new_assistant_data: game_type.Character = cache.character_data[character_data.assistant_character_id]
        new_assistant_data.sp_flag.is_follow = 1
        new_assistant_data.assistant_services[2] = 1
        second_behavior.character_get_second_behavior(new_assistant_id, "not_as_assistant", reset=True)
        second_behavior.character_get_second_behavior(new_assistant_id, "chosen_as_assistant")
        info_text += _("\n{0}成为助理干员了，并默认开启智能跟随模式\n").format(new_assistant_data.name)
        # 同步换助理的选项
        if old_assistant_flag:
            if 10 in old_assistant_data.assistant_services and old_assistant_data.assistant_services[10] == 1:
                new_assistant_data.assistant_services[10] = 1
    # 取消旧助理的结算
    if old_assistant_flag:
        second_behavior.character_get_second_behavior(new_assistant_id, "chosen_as_assistant", reset=True)
        second_behavior.character_get_second_behavior(old_assistant_data.adv, "not_as_assistant")
        info_text += _("\n\n{0}不再是助理干员了，已清零助理服务相关的设置\n\n").format(old_assistant_data.name)
    info_draw.text = info_text
    info_draw.width = window_width
    info_draw.draw()


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
        title_draw = draw.TitleLineDraw(_("助理相关调整"), self.width)

        while 1:
            character_data: game_type.Character = cache.character_data[0]
            target_data: game_type.Character = cache.character_data[character_data.assistant_character_id]

            title_draw.draw()
            py_cmd.clr_cmd()
            return_list = []

            info_draw = draw.NormalDraw()
            info_draw.text = _("\n●助理会自动获得打开玩家房门的权限，因此在执行问候、同居等服务时可以自由进出玩家房间\n\n")
            info_draw.draw()


            button_text = _("[001]助理服务")
            if character_data.assistant_character_id == 0:
                button_text += _("    当前无助理")
            else:
                assistant_name = target_data.name
                button_text += _("    当前助理：{0}").format(assistant_name)

            button_draw = draw.LeftButton(button_text, button_text, self.width, cmd_func=self.chose_button, args=(0,1))
            button_draw.draw()
            return_list.append(button_draw.return_text)
            line_feed.draw()

            if character_data.assistant_character_id != 0:

                # 如果数值超限则归零
                if target_data.sp_flag.is_follow > 4:
                    target_data.sp_flag.is_follow = 0

                # 开始遍历全部助理服务
                for cid in game_config.config_assistant_services:
                    # 跳过未实装的服务
                    if cid == 9:
                        continue
                    # 获取助理服务数据
                    service_data = game_config.config_assistant_services[cid]
                    service_option_data = game_config.config_assistant_services_option[cid]
                    service_option_text_all = service_option_data[0]
                    target_data.assistant_services.setdefault(cid, 0)
                    service_option_text_now = service_option_text_all[target_data.assistant_services[cid]]
                    service_option_len = len(service_option_text_all)

                    # 绘制输出文本
                    button_text = f"[{str(cid).rjust(3,'0')}]{service_data.name}"
                    button_text += f"    {service_option_text_now}"
                    button_draw = draw.LeftButton(button_text, button_text, self.width, cmd_func=self.chose_button, args=(cid,service_option_len))
                    button_draw.draw()
                    return_list.append(button_draw.return_text)
                    line_feed.draw()

                    # 早安服务的时间变更按钮
                    if cid == 5 and target_data.assistant_services[cid]:
                        button_text = _("  [更改早安服务预定时间]——当前预定时间：{0}:{1}").format(str(character_data.action_info.plan_to_wake_time[0]).rjust(2,'0'), str(character_data.action_info.plan_to_wake_time[1]).rjust(2,'0'))
                        button_draw = draw.LeftButton(button_text, button_text, self.width, cmd_func=self.select_morning_salutation_time)
                        button_draw.draw()
                        return_list.append(button_draw.return_text)
                        line_feed.draw()
                    # 晚安服务的时间变更按钮
                    if cid == 6 and target_data.assistant_services[cid]:
                        button_text = _("  [更改晚安服务预定时间]——当前预定时间：{0}:{1}").format(str(character_data.action_info.plan_to_sleep_time[0]).rjust(2,'0'), str(character_data.action_info.plan_to_sleep_time[1]).rjust(2,'0'))
                        button_draw = draw.LeftButton(button_text, button_text, self.width, cmd_func=self.select_night_salutation_time)
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
            target_data.assistant_services.setdefault(service_cid, 0)
            target_data.assistant_services[service_cid] = not target_data.assistant_services[service_cid]
            if target_data.sp_flag.is_follow == 1 or target_data.sp_flag.is_follow > 4:
                target_data.sp_flag.is_follow = 0
            else:
                target_data.sp_flag.is_follow += 1
        # 其他服务
        else:
            target_data.assistant_services.setdefault(service_cid, 0)
            if target_data.assistant_services[service_cid] == service_option_len - 1:
                target_data.assistant_services[service_cid] = 0
            else:
                # 判断是否符合解锁条件
                service_option_data = game_config.config_assistant_services_option[service_cid]
                service_option_text_all = service_option_data[0]
                service_option_text_next = service_option_text_all[target_data.assistant_services[service_cid]+1]
                service_require_text_all = service_option_data[1]
                service_require_text_next = service_require_text_all[target_data.assistant_services[service_cid]+1]
                judge, reason = attr_calculation.judge_require([service_require_text_next], character_data.assistant_character_id, hypnosis_replace_trust_flag = True)

                if judge:
                    target_data.assistant_services[service_cid] += 1
                # debug模式下不判断解锁条件
                elif cache.debug_mode:
                    target_data.assistant_services[service_cid] += 1
                # 不符合解锁条件时输出提示信息并归零
                else:
                    info_draw = draw.WaitDraw()
                    info_text = _("\n  ○更改失败，[{0}]{1}\n").format(service_option_text_next, reason)
                    info_draw.text = info_text
                    info_draw.draw()
                    target_data.assistant_services[service_cid] = 0
                    return

            # 结算附带的属性变化
            self.settlement_of_associated_attribute(service_cid, service_option_len)


    def settlement_of_associated_attribute(self, service_cid:int, service_option_len:int):
        """结算附带的属性变化"""
        # 跳过没有变化的
        if service_cid in {10}:
            return
        character_data: game_type.Character = cache.character_data[0]
        target_data: game_type.Character = cache.character_data[character_data.assistant_character_id]


        # 去掉选助理的1号选项
        if service_cid >= 2:
            # 定义多选项行为前缀
            behavior_prefixes = {
                2: "ai_follow_",
                4: "assistant_send_food_",
                5: "morning_service_",
                6: "night_service_"
            }
            # 定义二值开关行为前缀
            binary_prefixes = {
                3: "support_service_",
                7: "cohabitation_",
                8: "love_support_"
            }

            # 处理多选项行为
            if service_cid in behavior_prefixes:
                prefix = behavior_prefixes[service_cid]
                # 清除同类所有二段结算标记
                for i in range(service_option_len):
                    key = f"{prefix}{i}"
                    second_behavior.character_get_second_behavior(character_data.assistant_character_id, key, reset=True)
                # 设置当前选项对应的二段结算
                current_index = target_data.assistant_services[service_cid]
                key_now = f"{prefix}{current_index}"
                second_behavior.character_get_second_behavior(character_data.assistant_character_id, key_now)
            # 处理二值开关行为
            elif service_cid in binary_prefixes:
                prefix = binary_prefixes[service_cid]
                # 清除“on”和“off”旧状态
                key_on = f"{prefix}on"
                key_off = f"{prefix}off"
                second_behavior.character_get_second_behavior(character_data.assistant_character_id, key_on, reset=True)
                second_behavior.character_get_second_behavior(character_data.assistant_character_id, key_off, reset=True)
                # 根据当前服务开关状态赋值
                if target_data.assistant_services[service_cid]:
                    second_behavior.character_get_second_behavior(character_data.assistant_character_id, key_on)
                else:
                    second_behavior.character_get_second_behavior(character_data.assistant_character_id, key_off)


            # 同居服务的宿舍改变
            # 此处不可以用翻译地点
            if service_cid == 7:
                if target_data.assistant_services[service_cid] == 1:
                    target_data.pre_dormitory = target_data.dormitory
                    target_data.dormitory = map_handle.get_map_system_path_str_for_list(["中枢", "博士房间"])
                elif target_data.dormitory == map_handle.get_map_system_path_str_for_list(["中枢", "博士房间"]):
                    target_data.dormitory = target_data.pre_dormitory
                # print(f"debug target_data.dormitory = {target_data.dormitory}")

    def select_morning_salutation_time(self):
        """选择早安服务的时间"""
        character_data: game_type.Character = cache.character_data[0]
        return_list = []

        while 1:
            line_feed.draw()
            line_draw = draw.LineDraw("-", self.width)
            line_draw.draw()
            line_feed.draw()
            # 显示当前时间
            plan_to_wake_time = character_data.action_info.plan_to_wake_time
            now_time_hour, now_time_minute = plan_to_wake_time[0], plan_to_wake_time[1]
            now_time_text = _("当前预定早安服务时间为：{0}:{1}\n\n").format(str(now_time_hour).rjust(2,'0'), str(now_time_minute).rjust(2,'0'))
            now_time_text += _("除非太累了等特殊情况，助理干员会在该时间之前醒来，并前往博士位置\n")
            now_time_text += _("如果这个时间博士还没醒来，助理干员会来到博士床前，悄悄进行早安问候，然后一直等待到博士醒来为止\n")
            now_time_text += _("如果这个时间博士已经醒来，助理干员会直接前往博士身边，进行早安服务后离开\n")
            now_time_text += _("\n○同居状态下，如果助理干员提前醒来，也有可能提前进行早安服务\n")
            now_time_draw = draw.NormalDraw()
            now_time_draw.text = now_time_text
            now_time_draw.width = window_width
            now_time_draw.draw()
            line_feed.draw()

            # 更改小时与分钟的按钮
            hour_button = draw.CenterButton(_("[更改小时 (24小时制) ]"), _("更改小时，不得晚于9时"), int(window_width / 6), cmd_func=self.change_hour, args=(True,))
            hour_button.draw()
            return_list.append(hour_button.return_text)
            minute_button = draw.CenterButton(_("[更改分钟]"), _("更改分钟"), int(window_width / 6), cmd_func=self.change_minute, args=(True,))
            minute_button.draw()
            return_list.append(minute_button.return_text)
            line_feed.draw()
            line_feed.draw()

            # 返回按钮
            back_button = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_button.draw()
            line_feed.draw()
            return_list.append(back_button.return_text)

            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_button.return_text:
                break

    def select_night_salutation_time(self):
        """选择晚安服务的时间"""
        character_data: game_type.Character = cache.character_data[0]
        return_list = []

        while 1:
            line_feed.draw()
            line_draw = draw.LineDraw("-", self.width)
            line_draw.draw()
            line_feed.draw()
            # 显示当前时间
            plan_to_sleep_time = character_data.action_info.plan_to_sleep_time
            now_time_hour, now_time_minute = plan_to_sleep_time[0], plan_to_sleep_time[1]
            now_time_text = _("当前预定晚安服务时间为：{0}:{1}\n\n").format(str(now_time_hour).rjust(2,'0'), str(now_time_minute).rjust(2,'0'))
            now_time_text += _("如果这个时间博士还没有入睡，助理干员会前来催促睡觉，一直到博士睡前进行晚安服务后再离开\n")
            now_time_text += _("如果这个时间博士已经入睡，助理干员会来到博士床前，悄悄进行晚安服务后离开\n")
            now_time_draw = draw.NormalDraw()
            now_time_draw.text = now_time_text
            now_time_draw.width = window_width
            now_time_draw.draw()
            line_feed.draw()

            # 更改小时与分钟的按钮
            hour_button = draw.CenterButton(_("[更改小时 (24小时制) ]"), _("更改小时，不得早于18时"), int(window_width / 6), cmd_func=self.change_hour, args=(False,))
            hour_button.draw()
            return_list.append(hour_button.return_text)
            minute_button = draw.CenterButton(_("[更改分钟]"), _("更改分钟"), int(window_width / 6), cmd_func=self.change_minute, args=(False,))
            minute_button.draw()
            return_list.append(minute_button.return_text)
            line_feed.draw()
            line_feed.draw()

            # 返回按钮
            back_button = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_button.draw()
            line_feed.draw()
            return_list.append(back_button.return_text)

            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_button.return_text:
                break

    def change_hour(self, morning_flag : bool = True):
        """更改小时"""
        character_data: game_type.Character = cache.character_data[0]
        while 1:
            user_input = flow_handle.askfor_str(_(_("请输入小时(24小时制)：")))
            try:
                user_input = int(user_input)
            except:
                continue
            if morning_flag:
                if user_input <= 0:
                    user_input = 0
                elif user_input > 9:
                    user_input = 9
                character_data.action_info.plan_to_wake_time[0] = user_input
                break
            else:
                if user_input <= 18:
                    user_input = 18
                elif user_input > 0:
                    if user_input > 23:
                        user_input = 23
                    character_data.action_info.plan_to_sleep_time[0] = user_input
                    break

    def change_minute(self, morning_flag : bool = True):
        """更改分钟"""
        character_data: game_type.Character = cache.character_data[0]
        while 1:
            user_input = flow_handle.askfor_str(_(_("请输入分钟：")))
            try:
                user_input = int(user_input)
            except:
                continue
            if user_input < 0:
                continue
            elif user_input >= 0:
                if user_input > 59:
                    user_input = 59
                if morning_flag:
                    character_data.action_info.plan_to_wake_time[1] = user_input
                else:
                    character_data.action_info.plan_to_sleep_time[1] = user_input
                break


class SeeNPCButtonList:
    """
    点击后可选择作为助理的NPC的按钮对象
    Keyword arguments:
    chara_id -- 角色id
    width -- 最大宽度
    is_button -- 绘制按钮
    num_button -- 绘制数字按钮
    button_id -- 数字按钮id
    """

    def __init__(
        self, chara_id: int, width: int, is_button: bool, num_button: bool, button_id: int
    ):
        """初始化绘制对象"""

        self.chara_id: int = chara_id
        """ 角色id """
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

        target_data: game_type.Character = cache.character_data[self.chara_id]
        button_text = f"[{str(target_data.adv).rjust(4,'0')}]：{target_data.name}"

        # 按钮绘制

        name_draw = draw.LeftButton(
            button_text, self.button_return, self.width, cmd_func=assistant_replace, args=(self.chara_id,)
        )
        # self.button_return = NPC_id
        """ 绘制的对象 """
        self.now_draw = name_draw
        self.draw_text = button_text

    def draw(self):
        """绘制对象"""
        self.now_draw.draw()
