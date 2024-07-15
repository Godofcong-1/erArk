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

# 可能每种语言都有多个.mo文件，这里是.mo文件的名称列表
mo_files_per_language = {
    "en_US": ["erArk", "erArk_py", "erArk_csv", "erArk_talk"],
}

# 接受一个语言和对应的.mo文件列表，然后为这些文件创建一个GNUTranslations实例链
def create_translation_chain(language, mo_files):
    main_translation = None
    for mo_file in mo_files:
        try:
            translation = gettext.translation(mo_file, po_data, languages=[language])
            # print(f"Loaded {mo_file}.mo for {language}")
            if main_translation is None:
                main_translation = translation
            else:
                main_translation.add_fallback(translation)
        except FileNotFoundError:
            pass  # 如果.mo文件不存在，忽略该异常
    return main_translation

# 根据当前语言，创建翻译链
if now_language in mo_files_per_language:
    translation = create_translation_chain(now_language, mo_files_per_language[now_language])
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
else:
    def _translation_gettext(message, skip_translation=False, revert_translation=False):
        return message  # 如果没有找到对应语言的翻译，直接返回原文
    translation_values = set()

_: FunctionType = _translation_gettext
""" 翻译api """
