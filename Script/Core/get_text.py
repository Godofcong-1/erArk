# -*- coding: UTF-8 -*-
import gettext
import os
from types import FunctionType
from Script.Config import normal_config

po_data = os.path.join("data", "po")
""" po文件路径 """
normal_config.config_normal.language = "zh_CN"
translation: gettext.GNUTranslations = gettext.translation(
    "erArk", po_data, [normal_config.config_normal.language, "zh_CN"]
)
""" 翻译对象类型 """
translation_values = set(translation._catalog.values())
""" 翻译后的文本数据 """

_: FunctionType = translation.gettext
""" 翻译api """
