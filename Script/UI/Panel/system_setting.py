from typing import List
from types import FunctionType
from Script.Core import cache_control, game_type, get_text, flow_handle, constant
from Script.UI.Moudle import draw
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

def get_difficulty_coefficient(difficulty: int) -> float:
    """根据设定的难度值返回修正系数"""
    coefficients = [0.25, 0.5, 0.75, 1.0, 1.25, 2.0, 4.0]
    if 0 <= difficulty < len(coefficients):
        return coefficients[difficulty]
    else:
        return 1.0


class System_Setting_Panel:
    """
    用于系统设置的面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        # self.now_panel = _("系统设置")
        # """ 当前绘制的页面 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """
        self.pl_character_data = cache.character_data[0]
        """ 玩家的属性 """
        self.type_show = {_("基础"): True, _("难度"): False, _("绘制"): False}
        """ 当前显示的设置类型 """

    def draw(self):
        """绘制对象"""

        title_text = _("系统设置")
        title_draw = draw.TitleLineDraw(title_text, self.width)
        while 1:
            return_list = []
            title_draw.draw()

            # 输出提示信息
            now_draw = draw.NormalDraw()
            info_text = _(" \n ○点击[选项标题]显示[选项介绍]，点击[选项本身]即可[改变该选项]\n\n")
            now_draw.text = info_text
            now_draw.width = self.width
            now_draw.draw()

            # 遍历设置
            for key in self.type_show:
                return_list = self.draw_option(key, return_list)

            # 添加“文本生成AI设置”按钮
            ai_chat_setting_button_text = _(" [文本生成AI设置] ")
            ai_chat_setting_button = draw.CenterButton(
                ai_chat_setting_button_text,
                ai_chat_setting_button_text,
                len(ai_chat_setting_button_text) * 2,
                cmd_func=self.chat_ai_setting_panel_draw,
                )
            ai_chat_setting_button.draw()
            return_list.append(ai_chat_setting_button.return_text)

            # 添加“指令过滤”按钮
            command_filter_button_text = _(" [指令过滤] ")
            command_filter_button = draw.CenterButton(
                command_filter_button_text,
                command_filter_button_text,
                len(command_filter_button_text) * 2,
                cmd_func=self.chat_filter_panel_draw,
                )
            command_filter_button.draw()
            return_list.append(command_filter_button.return_text)

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

    def change_type_show(self, type_name):
        """改变当前显示的设置类型"""
        self.type_show[type_name] = not self.type_show[type_name]

    def chat_ai_setting_panel_draw(self):
        """绘制文本生成AI设置面板"""
        from Script.UI.Panel import chat_ai_setting
        now_panel = chat_ai_setting.Chat_Ai_Setting_Panel(self.width)
        now_panel.draw()

    def chat_filter_panel_draw(self):
        """绘制指令过滤面板"""
        from Script.UI.Panel import instruct_filter_panel
        now_panel = instruct_filter_panel.Instruct_filter_Panel(self.width)
        now_panel.draw()

    def draw_option(self, type_name: str, return_list: List[str]):
        """绘制选项"""
        if type_name == _("基础"):
            setting_data = game_config.config_system_setting
            setting_option = game_config.config_system_setting_option
            setting = cache.all_system_setting.base_setting
        elif type_name == _("难度"):
            setting_data = game_config.config_difficulty_setting
            setting_option = game_config.config_difficulty_setting_option
            setting = cache.all_system_setting.difficulty_setting
        elif type_name == _("绘制"):
            setting_data = game_config.config_draw_setting
            setting_option = game_config.config_draw_setting_option
            setting = cache.all_system_setting.draw_setting

        # 绘制选项标题
        if self.type_show[type_name]:
            type_text = _(" ▼[{0}设置]").format(type_name)
        else:
            type_text = _(" ▶[{0}设置]").format(type_name)
        type_button_draw = draw.LeftButton(
            type_text,
            type_text,
            len(type_text) * 2,
            cmd_func=self.change_type_show,
            args=(type_name)
        )
        type_button_draw.draw()
        return_list.append(type_button_draw.return_text)
        line_feed.draw()

        # 开始绘制选项
        if self.type_show[type_name]:
            for cid in setting_data:
                system_setting_data = setting_data[cid]
                # 选项名
                button_text = f"  [{system_setting_data.name}]： "
                button_len = max(len(button_text) * 2, 60)
                button_draw = draw.LeftButton(button_text, button_text, button_len, cmd_func=self.option_name_info, args=(type_name, cid))
                button_draw.draw()
                return_list.append(button_draw.return_text)

                # 如果没有该键，则创建一个，并置为0
                if cid not in setting:
                    setting[cid] = 0
                now_setting_flag = setting[cid] # 当前设置的值
                option_len = len(setting_option[cid]) # 选项的长度

                # 当前选择的选项的名字
                button_text = f" [{setting_option[cid][now_setting_flag]}] "
                button_len = max(len(button_text) * 2, 20)
                button_draw = draw.LeftButton(button_text, str(cid) + button_text, button_len, cmd_func=self.change_setting_value, args=(type_name, cid, option_len))
                button_draw.draw()
                return_list.append(button_draw.return_text)
                line_feed.draw()

                # 如果是基础设置的第7项的话，则加一个[修改已禁止干员列表]的按钮
                if type_name == "基础" and cid == 7 and cache.all_system_setting.base_setting[cid]:
                    new_button_text = _(" [修改已禁止干员列表] ")
                    new_button_len = max(len(new_button_text) * 2, 30)
                    new_button_draw = draw.LeftButton(new_button_text, "11" + new_button_text, new_button_len, cmd_func=self.change_ban_list)
                    new_button_draw.draw()
                    return_list.append(new_button_draw.return_text)
                    line_feed.draw()

        line_feed.draw()
    
        return return_list

    def option_name_info(self, type_name: str, cid: int):
        """绘制选项介绍信息"""
        line = draw.LineDraw("-", self.width)
        line.draw()
        now_draw = draw.WaitDraw()
        if type_name == _("基础"):
            setting_data = game_config.config_system_setting[cid]
        elif type_name == _("难度"):
            setting_data = game_config.config_difficulty_setting[cid]
        elif type_name == _("绘制"):
            setting_data = game_config.config_draw_setting[cid]
        info_text = f"\n {setting_data.info}\n"
        now_draw.text = info_text
        now_draw.width = self.width
        now_draw.draw()
        line = draw.LineDraw("-", self.width)
        line.draw()

    def change_setting_value(self, type_name: str, cid: int, option_len: int):
        """修改选项设置"""
        if type_name == _("基础"):
            setting = cache.all_system_setting.base_setting
        elif type_name == _("难度"):
            setting = cache.all_system_setting.difficulty_setting
        elif type_name == _("绘制"):
            setting = cache.all_system_setting.draw_setting
        if setting[cid] < option_len - 1:
            setting[cid] += 1
        else:
            setting[cid] = 0
        # 全角色是否使用通用文本
        if type_name == _("绘制") and cid == 2:
            for character_id in cache.character_data:
                character_data = cache.character_data[character_id]
                character_data.chara_setting[1] = cache.all_system_setting.draw_setting[cid]

    def change_ban_list(self):
        """修改已禁止干员列表"""
        while 1:
            now_set = cache.forbidden_npc_id
            return_list = []
            title_text = _("已禁止干员列表")
            title_draw = draw.TitleLineDraw(title_text, self.width)
            title_draw.draw()
            line_feed.draw()
            npc_count = 0 # 计数
            # 遍历全部干员
            for npc_id in cache.character_data:
                # 跳过玩家
                if npc_id == 0:
                    continue
                npc_data = cache.character_data[npc_id]
                button_text = f"[{str(npc_data.adv).rjust(4,'0')}]：{npc_data.name}"
                # 已禁止的干员显示为灰色，其他显示为白色
                draw_style = 'standard'
                if npc_id in now_set:
                    draw_style = 'deep_gray'
                # 绘制按钮
                button_draw = draw.LeftButton(button_text, str(npc_id), self.width/6,normal_style=draw_style, cmd_func=self.change_ban_list_cmd, args=(npc_id))
                button_draw.draw()
                return_list.append(button_draw.return_text)
                # 每行显示6个干员
                npc_count += 1
                if npc_count % 6 == 0:
                    line_feed.draw()
            line_feed.draw()
            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                break

    def change_ban_list_cmd(self, npc_id):
        """修改已禁止干员列表"""
        from Script.Settle import default
        if npc_id in cache.forbidden_npc_id:
            cache.forbidden_npc_id.remove(npc_id)
        else:
            cache.forbidden_npc_id.add(npc_id)
            # 如果该干员已被招募，则离岛
            if npc_id in cache.npc_id_got:
                default.handle_chara_off_line(npc_id, 1, change_data = game_type.CharacterStatusChange(), now_time = cache.game_time)
                # 输出提示信息
                now_draw = draw.NormalDraw()
                info_text = _("\n\n{0}干员已离岛\n\n").format(cache.character_data[npc_id].name)
                now_draw.text = info_text
                now_draw.width = self.width
                now_draw.draw()
