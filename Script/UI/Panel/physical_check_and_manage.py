from typing import List
from types import FunctionType
from Script.Core import cache_control, game_type, get_text, flow_handle, constant
from Script.Design import handle_premise, handle_instruct
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


class Physical_Check_And_Manage_Panel:
    """
    用于身体检查与管理的面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.now_panel = _("身体检查与管理")
        """ 当前绘制的页面 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """
        self.pl_character_data = cache.character_data[0]
        """ 玩家的角色数据 """
        self.last_check_status_id = 0
        """ 上次检查指令的状态id """

    def draw(self):
        """绘制对象"""

        title_text = _("身体检查与管理")
        title_draw = draw.TitleLineDraw(title_text, self.width)
        while 1:
            return_list = []
            title_draw.draw()
            cinfo_draw = draw.NormalDraw()
            info_text = _("\n要做什么呢？\n")
            cinfo_draw.text = info_text
            cinfo_draw.draw()

            if handle_premise.handle_have_target(0):
                target_character_id = self.pl_character_data.target_character_id
                target_character_data = cache.character_data[target_character_id]
                button1_text = _("[001]查看{0}的身体情况").format(target_character_data.name)
                button1_draw = draw.LeftButton(
                    _(button1_text),
                    _("1"),
                    self.width,
                    cmd_func=self.check_target_physical,
                    args=(target_character_id,),
                )
                line_feed.draw()
                button1_draw.draw()
                return_list.append(button1_draw.return_text)
            else:
                button1_text = _("[001]查看身体情况（当前没有查看对象）\n")
                button1_draw = draw.NormalDraw()
                button1_draw.text = button1_text
                button1_draw.style = "deep_gray"
                button1_draw.width = self.width
                button1_draw.draw()

            if handle_premise.handle_have_target(0):
                target_character_id = self.pl_character_data.target_character_id
                target_character_data = cache.character_data[target_character_id]
                button2_text = _("[002]对{0}进行身体管理").format(target_character_data.name)
                button2_draw = draw.LeftButton(
                    _(button2_text),
                    _("2"),
                    self.width,
                    cmd_func=self.manage_target_physical,
                    args=(target_character_id,),
                )
                line_feed.draw()
                button2_draw.draw()
                return_list.append(button2_draw.return_text)
            else:
                button2_text = _("[002]进行身体管理（当前没有管理对象）\n")
                button2_draw = draw.NormalDraw()
                button2_draw.text = button2_text
                button2_draw.style = "deep_gray"
                button2_draw.width = self.width
                button2_draw.draw()

            if 1:
                button3_text = _("[003]调整体检日程")
                button3_draw = draw.LeftButton(
                    _(button3_text),
                    _("3"),
                    window_width,
                    cmd_func=self.adjust_physical_check_schedule,
                    args=(),
                    )
                line_feed.draw()
                button3_draw.draw()
                return_list.append(button3_draw.return_text)

            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def check_target_physical(self, target_character_id: int):
        """查看目标角色的身体情况"""
        target_character_data = cache.character_data[target_character_id]

        # 指令与前置指令的对应表
        cmd_able_dict = {
            853: 852,
            856: 855,
            859: 858,
            861: 860,
            873: 872,
            874: 872,
            875: 872,
            877: 876,
            879: 878,
            882: 881,
            888: 887,
        }

        while 1:
            return_list = []
            line_feed.draw()
            line = draw.LineDraw("-", window_width)
            line.draw()
            # 绘制提示信息
            info_text = _("\n请选择要对{0}进行的身体检查：\n\n").format(target_character_data.name)
            info_draw = draw.NormalDraw()
            info_draw.text = info_text
            info_draw.draw()
            # 检索所有的身体检查状态
            all_obscenity_examine_status_list = []
            count = 0
            for status_id in range(850, 899):
                if status_id in game_config.config_status:
                    count += 1
                    all_obscenity_examine_status_list.append(status_id)
                    # 部分指令需要有前置指令才能使用
                    if status_id in cmd_able_dict and self.last_check_status_id != cmd_able_dict[status_id]:
                        continue
                    # 部分指令需要破处后才能使用
                    if status_id == 874 or status_id == 875 and target_character_data.talent[0]:
                        continue
                    elif status_id == 877 and target_character_data.talent[1]:
                        continue
                    # 绘制按钮
                    status_data = game_config.config_status[status_id]
                    status_text = f"[{str(count).rjust(2,'0')}]：{status_data.name}"
                    status_draw = draw.LeftButton(
                        _(status_text),
                        _(str(count)),
                        window_width,
                        cmd_func=self.settle_target_physical_status,
                        args=(status_id),
                    )
                    line_feed.draw()
                    status_draw.draw()
                    return_list.append(status_draw.return_text)

            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def settle_target_physical_status(self, status_id: int):
        """结算目标角色的身体状态"""
        self.last_check_status_id = status_id
        handle_instruct.chara_handle_instruct_common_settle(status_id, force_taget_wait = True)

    def manage_target_physical(self, target_character_id: int):
        """对目标角色进行身体管理"""
        # TODO
        pass

    def adjust_physical_check_schedule(self):
        """调整体检日程"""
        # TODO
        pass
