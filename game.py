#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import sys
import logging
from types import FunctionType

if __name__ == "__main__":


    import auto_build_config
    from Script.Config import normal_config
    from Script.Core import game_type, cache_control

    #log输出等级
    # logging.basicConfig(format='等级：%(levelname)s，函数名：%(funcName)s，信息为：%(message)s', level = logging.DEBUG)
    logging.basicConfig(format='等级：%(levelname)s，函数名：%(funcName)s，信息为：%(message)s', level = logging.INFO)

    # 初始化游戏缓存数据
    cache_control.cache = game_type.Cache()
    # 初始化游戏基础配置数据
    normal_config.init_normal_config()

    from Script.Core import get_text
    from Script.Config import game_config, name_config, character_config

    _: FunctionType = get_text._
    """ 翻译api """

    # 载入游戏配置
    game_config.init()
    # 载入姓名配置，暂时去掉
    # name_config.init_name_data()
    # 初始化角色人物卡数据
    character_config.init_character_tem_data()

    # 载入地图数据
    from Script.Config import map_config
    map_config.init_map_data()

    from Script.Design import start_flow, character_handle, game_time
    from Script.Core import game_init
    import Script.Settle
    import Script.StateMachine
    import Script.UI.Flow

    # 载入角色人物卡数据
    character_handle.init_character_tem()

    # 初始化游戏时间
    game_time.init_time()
    # 初始化游戏
    game_init.run(start_flow.start_frame)
