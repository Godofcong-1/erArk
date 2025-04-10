from typing import List
from types import FunctionType
from Script.UI.Moudle import draw
from Script.Core import (
    cache_control,
    get_text,
    game_type,
    flow_handle,
    constant,
)
from Script.Config import normal_config
from Script.Design import handle_premise_place

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


class Select_Hidden_Sex_Mode_Panel:
    """
    用于选择隐奸模式的面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.now_panel = _("选择隐奸模式")
        """ 当前绘制的页面 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """

    def draw(self):
        """绘制对象"""

        title_text = _("选择隐奸模式")
        title_draw = draw.TitleLineDraw(title_text, self.width)

        while 1:
            return_list = []
            title_draw.draw()

            # 输出提示信息
            info_draw = draw.NormalDraw()
            info_text = _("\n请选择要进行的隐奸：\n")
            info_text += _("○需要在没有其他人，或者其他人都无意识下才可以选择单方或者双方隐藏\n")
            info_text += _("  隐奸被发现的概率取决于隐奸模式、隐蔽技能等级、指令动作、在场人数、地点环境等\n")
            info_text += "\n"
            info_draw.text = info_text
            info_draw.draw()

            button_text_list = []
            button_text_list.append(_("[1]不隐藏：双方身体均暴露在外，仅靠视线遮挡来避免被发现，容易被察觉"))
            button_text_list.append(_("[2]干员隐藏：博士不隐藏，干员藏起来不让别人看见，隐蔽程度中等"))
            button_text_list.append(_("[3]博士隐藏：干员不隐藏，博士藏起来不让别人看见，隐蔽程度中等"))
            button_text_list.append(_("[4]双方隐藏：博士和干员都藏起来不让别人看见，很难被察觉"))
            for i in range(len(button_text_list)):
                button_text = button_text_list[i]
                can_use = True
                if i >= 1:
                    can_use = False
                    if handle_premise_place.handle_scene_only_two(0) or handle_premise_place.handle_scene_all_others_unconscious_or_sleep(0):
                        can_use = True
                if can_use:
                    button_draw = draw.LeftButton(
                        button_text,
                        str(i + 1),
                        self.width,
                        cmd_func=self.select_this_mode,
                        args=(i + 1,),
                    )
                    button_draw.draw()
                    return_list.append(button_draw.return_text)
                # 否则为灰色文字，不可选
                else:
                    now_draw = draw.NormalDraw()
                    now_draw.text = button_text
                    now_draw.style = "deep_gray"
                    now_draw.draw()
                line_feed.draw()

            line_feed.draw()
            yrn = flow_handle.askfor_all(return_list)
            if yrn in return_list:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def select_this_mode(self, mode_id):
        """选择隐奸模式"""
        character_data: game_type.Character = cache.character_data[0]
        character_data.sp_flag.hidden_sex_mode = mode_id
        target_character_id = character_data.target_character_id
        target_character_data: game_type.Character = cache.character_data[target_character_id]
        target_character_data.sp_flag.hidden_sex_mode = mode_id
