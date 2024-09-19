from typing import List
from types import FunctionType
from Script.Core import cache_control, game_type, get_text
from Script.UI.Moudle import draw
from Script.Config import game_config, normal_config
from Script.Design import attr_calculation

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


class CharacterSetting:
    """
    显示角色设置面板对象
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

    def draw(self):
        """绘制面板"""
        character_data = cache.character_data[self.character_id]
        type_data = _("角色设置")
        type_line = draw.LittleTitleLineDraw(type_data, self.width, ":")
        type_line.draw()
        now_draw = draw.NormalDraw()
        # NPC的设置
        if self.character_id != 0:

            # 输出提示信息
            info_text = _(" \n ○点击[选项标题]显示[选项介绍]，点击[选项本身]即可[改变该选项]\n")
            now_draw.text = info_text
            now_draw.width = self.width
            now_draw.draw()

            # 遍历全部设置
            for cid in game_config.config_chara_setting:
                line_feed.draw()
                chara_setting_data = game_config.config_chara_setting[cid]
                # 选项名
                button_text = f" [{chara_setting_data.name}]： "
                button_draw = draw.CenterButton(button_text, button_text, len(button_text)*2, cmd_func=self.draw_info, args=(cid))
                button_draw.draw()
                self.return_list.append(button_draw.return_text)

                # 如果没有该键，则创建一个，并置为0
                if cid not in character_data.chara_setting:
                    character_data.chara_setting[cid] = 0
                now_setting_flag = character_data.chara_setting[cid] # 当前设置的值
                option_len = len(game_config.config_chara_setting_option[cid]) # 选项的长度

                # 当前选择的选项的名字
                button_text = f" {game_config.config_chara_setting_option[cid][now_setting_flag]} "

                # 判断是否符合条件
                require_text = game_config.config_chara_setting[cid].require
                # 整理需要的条件
                if "&" not in require_text:
                    require_text_list = [require_text]
                else:
                    require_text_list = require_text.split('&')
                judge, reason = attr_calculation.judge_require(require_text_list,self.character_id)

                if judge:
                    button_draw = draw.CenterButton(button_text, button_text, len(button_text)*2, cmd_func=self.change_setting, args=(cid, option_len))
                    button_draw.draw()
                    self.return_list.append(button_draw.return_text)
                else:
                    info_text = _(" {0}(  更改{1})").format(button_text, reason)
                    now_draw.text = info_text
                    now_draw.width = self.width
                    now_draw.draw()

            line_feed.draw()

        # 玩家的设置
        else:
            info_text = _(" \n 暂无设置\n")
            now_draw.text = info_text
            now_draw.width = self.width
            now_draw.draw()
        # yrn = flow_handle.askfor_all(return_list)

    def draw_info(self, cid):
        """绘制选项介绍信息"""
        line = draw.LineDraw("-", self.width)
        line.draw()
        now_draw = draw.WaitDraw()
        chara_setting_data = game_config.config_chara_setting[cid]
        info_text = f"\n {chara_setting_data.info}\n"
        now_draw.text = info_text
        now_draw.width = self.width
        now_draw.draw()
        line = draw.LineDraw("-", self.width)
        line.draw()

    def change_setting(self, cid, option_len):
        """修改设置"""
        character_data = cache.character_data[self.character_id]
        if character_data.chara_setting[cid] < option_len - 1:
            character_data.chara_setting[cid] += 1
        else:
            character_data.chara_setting[cid] = 0
