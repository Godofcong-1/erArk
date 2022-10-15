#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import sys
import logging
from types import FunctionType
import auto_build_config
from Script.Config import normal_config
from Script.Core import game_type, cache_control

#log输出等级
# logging.basicConfig(format='等级：%(levelname)s，函数名：%(funcName)s，信息为：%(message)s', level = logging.DEBUG)
logging.basicConfig(format='等级：%(levelname)s，函数名：%(funcName)s，信息为：%(message)s', level = logging.INFO)


cache_control.cache = game_type.Cache()
normal_config.init_normal_config()


from Script.Core import get_text
from Script.Config import game_config, name_config, character_config

_: FunctionType = get_text._
""" 翻译api """

game_config.init()
name_config.init_name_data()
character_config.init_character_tem_data()


from Script.Config import map_config

map_config.init_map_data()


from Script.Design import start_flow, handle_premise, game_time
from Script.Core import game_init
import Script.Settle
import Script.StateMachine
import Script.UI.Flow
import multiprocessing


if __name__ == "__main__":
    multiprocessing.freeze_support()

game_time.init_time()
game_init.run(start_flow.start_frame)
