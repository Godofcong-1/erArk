# -*- coding: UTF-8 -*-
"""英文环境下的多语言回归检查（_language_checks.py）：行为标签比较、群交模板与调教助手、外勤委托奖励、烹饪阶段、宿舍与地点、按干员编号认人、管理罗德岛面板、专属服装分类"""
import os

os.environ["ERARK_TEST_LANGUAGE"] = "en_US"
from _bootstrap import *  # noqa: F401,F403,E402
from _language_checks import run_language_checks  # noqa: E402

run_language_checks("en_US")
finish()
