# -*- coding: UTF-8 -*-
"""韩文环境下的多语言回归检查（_language_checks.py）：检查项与英文相同；韩文另有阿米娅与阿玛雅译名相同、「烹饪」「角色」有译文两种只在韩文出现的情形"""
import os

os.environ["ERARK_TEST_LANGUAGE"] = "ko_KR"
from _bootstrap import *  # noqa: F401,F403,E402
from _language_checks import run_language_checks  # noqa: E402

run_language_checks("ko_KR")
finish()
