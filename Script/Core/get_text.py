# -*- coding: UTF-8 -*-
import gettext
import os
from types import FunctionType
from Script.Config import normal_config

po_data = os.path.join("data", "po")
""" po文件路径 """
# 如果language在normal_config.config_normal中，就使用normal_config.config_normal.language，否则使用zh_CN
now_language = normal_config.config_normal.language if hasattr(normal_config.config_normal, 'language') else "zh_CN"
# print(now_language)

# 如果是中文，不进行翻译，直接返回原文，否则进行翻译
if now_language == "zh_CN":
    def _translation_gettext(message):
        return message
    translation_values = set()
else:
    translation: gettext.GNUTranslations = gettext.translation(
        "erArk", po_data, [normal_config.config_normal.language, "zh_CN"]
    )
    _translation_gettext = translation.gettext
    translation_values = set(translation._catalog.values())


_: FunctionType = _translation_gettext
""" 翻译api """
