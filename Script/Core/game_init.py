# -*- coding: UTF-8 -*-
import os
import traceback
from types import FunctionType
from Script.Core import flow_handle, io_init, key_listion_event, cache_control, game_type, constant, py_cmd, get_text, save_handle
from Script.Config import game_config, normal_config
from Script.UI.Moudle import panel
from Script.Design import game_time

_: FunctionType = get_text._
""" 翻译api """
cache: game_type.Cache = cache_control.cache

# 字符串定义###########################################################
NO_EVENT_FUNC = "no_event_func"

# 系统函数#############################################################
# 初始化函数
_main_flow = None
error_path = os.path.join("error.log")


def init(main_flow: object):
    """
    游戏流程初始化
    Keyword argument:
    main_flow -- 游戏主流程
    """
    global def_style
    io_init.clear_screen()
    io_init.clear_order()
    flow_handle.cmd_clear()
    # 载入按键监听
    key_listion_event.on_wframe_listion()
    # 设置背景颜色
    io_init.set_background(normal_config.config_normal.background)
    # 初始化字体
    io_init.init_style()
    # 初始化地图数据
    global _main_flow
    _main_flow = main_flow

    _have_run = False

    def run_main_flow():
        nonlocal _have_run
        while True:
            if not _have_run:
                main_flow()
                _have_run = True
            askfor_order()
            flow_handle.call_default_flow()
            if flow_handle.exit_flag:
                break

    while True:

        try:
            run_main_flow()
        except Exception:
            # 最近玩家指令状态
            instruct_cn_name_list = ""
            for behavior_id in cache.pl_pre_behavior_instruce:
                if behavior_id in game_config.config_behavior:
                    behavior_data = game_config.config_behavior[behavior_id]
                    instruct_cn_name_list += behavior_data.name + "，"
            if len(instruct_cn_name_list) and instruct_cn_name_list[-1] == "，":
                instruct_cn_name_list = instruct_cn_name_list[:-1]
            # 向error_log写入回溯用信息
            with open(error_path, "a", encoding="utf-8") as e:
                e.write(f"\n版本信息：{normal_config.config_normal.verson}\n")
                e.write(f"最近输入指令：{cache.input_cache}\n")
                e.write(f"玩家最近状态：{instruct_cn_name_list}\n")
                e.write(f"当前游戏内时间：{game_time.get_date_text(cache.game_time)}\n")
            traceback.print_exc(file=open(error_path, "a"))
            # 向游戏内写入错误信息
            error_text = "\n"
            error_text += _("版本信息：{0}\n").format(normal_config.config_normal.verson)
            error_text += _("最近输入指令：{0}\n").format(cache.input_cache)
            error_text += _("玩家最近状态：{0}\n").format(instruct_cn_name_list)
            error_text += _("当前游戏内时间：{0}\n").format(game_time.get_date_text(cache.game_time))
            error_text += traceback.format_exc()
            error_text += _("\n\n游戏发生错误，已将上述错误信息写入error.log\n\n")
            error_text += _("报错数据文件已保存至99号档位，请将error.log和存档发送给游戏作者以帮助解决问题\n\n")
            save_handle.establish_save("99")
            # 输出选择面板
            ask_list = []
            askfor_panel = panel.OneMessageAndSingleColumnButton()
            askfor_list = [(_("回到标题画面")), (_("退出游戏"))]
            askfor_panel.set(askfor_list, (error_text), 0)
            askfor_panel.draw()
            askfor_panel_return_list = askfor_panel.get_return_list()
            ask_list.extend(askfor_panel_return_list.keys())
            yrn = flow_handle.askfor_all(ask_list)
            py_cmd.clr_cmd()
            # 回到标题画面
            if yrn == "0":
                io_init.clear_screen()
                io_init.clear_order()
                flow_handle.cmd_clear()
                cache.now_panel_id = constant.Panel.TITLE
            else:
                os._exit(0)


def run(main_func: object):
    """
    执行游戏主流程
    Keyword arguments:
    main_func -- 游戏主流程
    """

    def _init():
        init(main_func)

    io_init.run(_init)


def console_log(string: str):
    """
    向后台打印日志
    Keyword arguments:
    string -- 游戏日志信息
    """
    print("game log:")
    print(string + "\n")


# 请求输入命令
askfor_order = flow_handle.order_deal

# 请求输入一个字符串
askfor_str = flow_handle.askfor_str

# 请求输入一个数字
askfor_int = flow_handle.askfor_int
askfor_all = flow_handle.askfor_all

# 设置尾命令处理函数
set_deal_cmd_func = flow_handle.set_tail_deal_cmd_func

# 设置尾命令处理函数装饰器
set_deal_cmd_func_deco = flow_handle.deco_set_tail_deal_cmd_func
