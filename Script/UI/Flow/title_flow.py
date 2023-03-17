import os
from types import FunctionType
from Script.Config import normal_config
from Script.UI.Moudle import panel, draw
from Script.UI.Panel import see_save_info_panel
from Script.Design import handle_panel
from Script.Core import constant, get_text, flow_handle, cache_control, game_type, py_cmd

config_normal = normal_config.config_normal
_: FunctionType = get_text._
""" 翻译api """
cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """


@handle_panel.add_panel(constant.Panel.TITLE)
def title_panel():
    """绘制游戏标题菜单"""
    clear_screen = panel.ClearScreenPanel()
    clear_screen.draw()
    width = config_normal.text_width
    title_info = panel.TitleAndRightInfoListPanel()
    info_list = [config_normal.author, config_normal.verson_time, config_normal.verson]
    title_info.set(config_normal.game_name, info_list, width)
    title_info.draw()
    lineFeed = draw.NormalDraw()
    lineFeed.width = 1
    lineFeed.text = "\n"
    lineFeed.draw()
    draw_logo()
    info = _("正在尝试与Rhodes Island(if_h)取得神经连接")
    lineFeed.draw()
    info_draw = draw.CenterDraw()
    info_draw.text = info
    info_draw.width = width
    info_draw.draw()
    lineFeed.draw()
    lineFeed.draw()
    line = draw.LineDraw("=", width)
    line.draw()
    now_list = [_(" -【初次唤醒】-"), _(" -【神经重载】-"), _(" -【断开连接】-")]
    button_panel = panel.OneMessageAndSingleColumnButton()
    button_panel.set(now_list, "", 0)
    button_panel.draw()
    return_list = button_panel.get_return_list()
    ans = flow_handle.askfor_all(return_list.keys())
    py_cmd.clr_cmd()
    now_key = return_list[ans]
    if now_key == now_list[0]:
        cache.now_panel_id = constant.Panel.CREATOR_CHARACTER
    elif now_key == now_list[1]:
        now_panel = see_save_info_panel.SeeSaveListPanel(width, 0)
        now_panel.draw()
    elif now_key == now_list[2]:
        os._exit(0)

def draw_logo():
    """绘制logo"""
    logo_text = []
    logo_text.append("┌----------------------------------┐")
    logo_text.append("|                                  |")
    logo_text.append("|              服务器              |")
    logo_text.append("|            泰拉(if_h)            |")
    logo_text.append("|                                  |")
    logo_text.append("|                                  |")
    logo_text.append("|      #                           |")
    logo_text.append("|      |¯¯ |¯¯\   /\               |")
    logo_text.append("|      |-- |__/  /__\  |/¯ |/      |")
    logo_text.append("60%         |      |__ |  \ /    \ |   |\      |         60%")
    logo_text.append("------------------------------------------------------------         |                                  |         ------------------------------------------------------------")
    logo_text.append("|                                  |")
    logo_text.append("|                                  |")
    logo_text.append("|                                  |")
    logo_text.append("|                                  |")
    logo_text.append("└----------------------------------┘")
    for i in range(len(logo_text)):
        info_draw = draw.CenterDraw()
        info_draw.text = logo_text[i]
        info_draw.width = config_normal.text_width
        info_draw.draw()
        lineFeed = draw.NormalDraw()
        lineFeed.width = 1
        lineFeed.text = "\n"
        lineFeed.draw()
