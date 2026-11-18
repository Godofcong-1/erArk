# -*- coding: UTF-8 -*-
"""中文环境下跑一遍多语言回归检查（_language_checks.py）：同一组检查在默认语言下也必须成立，防止为英文 / 韩文做的修正改坏中文下的行为"""
import os

os.environ["ERARK_TEST_LANGUAGE"] = "zh_CN"
from _bootstrap import *  # noqa: F401,F403,E402
from _language_checks import run_language_checks  # noqa: E402

run_language_checks("zh_CN")
finish()
