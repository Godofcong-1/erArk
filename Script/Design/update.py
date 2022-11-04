import logging, time
from Script.Design import character_behavior, game_time, event
from Script.Core import py_cmd


def game_update_flow(add_time: int):
    """
    游戏流程刷新
    Keyword arguments:
    add_time -- 游戏步进的时间
    """
    character_behavior.init_character_behavior()
    now_event = event.handle_event(0,1)
    # if now_event != None:
    #     now_event.draw()
    game_time.sub_time_now(add_time)
    logging.debug(f'————————')
    logging.debug(f'进入第二次结算')
    character_behavior.init_character_behavior()
    py_cmd.focus_cmd()
    # logging.debug(f'————————')
