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

# 创建一个字典来存储原始字符串和它们的翻译
translation_dict = {}

# 如果是中文，不进行翻译，直接返回原文，否则进行翻译
if now_language == "zh_CN":
    def _translation_gettext(message, skip_translation=False, revert_translation=False):
        return message
    translation_values = set()
else:
    translation: gettext.GNUTranslations = gettext.translation(
        "erArk", po_data, [normal_config.config_normal.language, "zh_CN"]
    )
    def _translation_gettext(message, skip_translation=False, revert_translation=False):
        # 如果需要跳过翻译，直接返回原文
        if skip_translation:
            return message
        # 如果需要恢复原始字符串，查找字典
        elif revert_translation:
            for original, translated in translation_dict.items():
                if translated == message:
                    return original
            return message  # 如果找不到，返回翻译后的字符串
        else:
            translated = translation.gettext(message)
            # 存储原始字符串和它的翻译
            translation_dict[message] = translated
            return translated
    translation_values = set(translation._catalog.values())


_: FunctionType = _translation_gettext
""" 翻译api """
