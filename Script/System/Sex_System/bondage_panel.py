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
from Script.Config import game_config, normal_config
from Script.Design import handle_premise

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

        title_text = _("绳艺")
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
            info_text += _("  越高级的捆绑需要越高级的[指技]才能施展\n")
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
                # 用于判断是否可以施展捆绑
                cant_flag = False

                # 用于在捆绑等级变化时更新文本
                if bondage_lvel > level_count:
                    level_count = bondage_lvel
                    line_feed.draw()
                    level_text = level_text_list[level_count]
                    level_draw = draw.NormalDraw()
                    level_draw.text = "●" + level_text + "：\n"
                    level_draw.draw()

                    # 指技等级判定
                    need_lv = bondage_lvel * 2
                    if character_data.ability[70] < need_lv:
                        level_draw.text = _("(需要[指技]等级>={0})").format(need_lv)
                        cant_flag = True
                        level_draw.draw()
                        break

                # 地点判定
                if bondage_data.need_facility and handle_premise.handle_not_in_humiliation_room(0):
                    bondage_text += _("(需要在调教室施展)")
                    cant_flag = True

                # 如果不能施展则不显示按钮，仅打印灰色文本
                if cant_flag:
                    text_draw = draw.NormalDraw()
                    text_draw.text = bondage_text
                    text_draw.style = 'deep_gray'
                    text_draw.draw()
                # 如果可以施展则显示按钮
                else:
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
        from Script.System.Instruct_System import handle_instruct
        character_data: game_type.Character = cache.character_data[0]
        target_character_id = character_data.target_character_id
        target_character_data: game_type.Character = cache.character_data[target_character_id]
        target_character_data.h_state.bondage = bondage_id
        # 如果捆绑id为0，则解除捆绑
        if bondage_id == 0:
            handle_instruct.chara_handle_instruct_common_settle(constant.Behavior.UNBIND, judge = _("SM"), force_taget_wait=True)
        # 否则进行捆绑
        else:
            handle_instruct.chara_handle_instruct_common_settle(constant.Behavior.BIND, judge = _("SM"), force_taget_wait=True)

