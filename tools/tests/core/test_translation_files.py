# -*- coding: UTF-8 -*-
"""翻译文件的静态检查：data/po 下各翻译语言的每个 PO 只有一个文件头、没有重复的原文；入库的 MO 与它的 PO 的已译条目逐条相同（游戏运行时读的是 MO，改了 PO 要跑 buildmo.py）"""
import gettext
import re

from _bootstrap import *  # noqa: F401,F403

PO_ROOT = os.path.join(ROOT, "data", "po")
SOURCE_LANGUAGE = "zh_CN"
""" 原文语言：它的 PO 由构建生成、只作翻译原文，游戏不读它的 MO """
ESCAPE = {"n": "\n", "t": "\t", "r": "\r", '"': '"', "\\": "\\"}


def unquote(text: str) -> str:
    """
    把 PO 里一段带引号的字符串还原成原文
    Keyword arguments:
    text -- 形如 "…" 的一段（两端带双引号）
    Return arguments:
    str -- 去掉引号并还原转义后的文本
    """
    text = text.strip()
    assert len(text) >= 2 and text[0] == '"' and text[-1] == '"', text
    return re.sub(r"\\(.)", lambda match: ESCAPE.get(match.group(1), match.group(1)), text[1:-1])


def parse_po(po_path: str) -> tuple:
    """
    只用标准库读一个 PO 文件（CI 上没有 polib，也没有 msgfmt）
    Keyword arguments:
    po_path -- PO 文件路径
    Return arguments:
    tuple -- (原文 → 译文 的字典（不含文件头，不含标了 fuzzy 的条目）, 文件头个数, 重复出现的原文列表)
    """
    entry_dict = {}
    header_count = 0
    duplicate_list = []
    seen_set = set()
    msgid, msgstr, field, fuzzy = None, "", "", False

    def flush():
        """把读完的一条登记进去"""
        nonlocal msgid, msgstr, field, fuzzy, header_count
        if msgid is not None:
            if msgid == "":
                header_count += 1
            else:
                if msgid in seen_set:
                    duplicate_list.append(msgid)
                seen_set.add(msgid)
                if not fuzzy:
                    entry_dict[msgid] = msgstr
        msgid, msgstr, field, fuzzy = None, "", "", False

    with open(po_path, encoding="utf-8") as po_file:
        for line in po_file:
            line = line.strip()
            if line.startswith("#~"):
                continue
            if line.startswith("#,") and "fuzzy" in line:
                flush()
                fuzzy = True
            elif line.startswith("msgid "):
                if msgid is not None:
                    flush()
                msgid, field = unquote(line[len("msgid "):]), "msgid"
            elif line.startswith("msgstr "):
                msgstr, field = unquote(line[len("msgstr "):]), "msgstr"
            elif line.startswith('"'):
                if field == "msgid":
                    msgid += unquote(line)
                elif field == "msgstr":
                    msgstr += unquote(line)
            elif not line:
                flush()
    flush()
    return entry_dict, header_count, duplicate_list


section("1. 各翻译语言的 PO 与入库的 MO")
structure_problem = {}
content_problem = {}
file_count = 0
for language in sorted(os.listdir(PO_ROOT)):
    message_dir = os.path.join(PO_ROOT, language, "LC_MESSAGES")
    if language == SOURCE_LANGUAGE or not os.path.isdir(message_dir):
        continue
    for file_name in sorted(os.listdir(message_dir)):
        if not file_name.endswith(".po"):
            continue
        file_count += 1
        label = "%s/%s" % (language, file_name[:-3])
        po_dict, header_count, duplicate_list = parse_po(os.path.join(message_dir, file_name))
        if header_count != 1 or duplicate_list:
            structure_problem[label] = ("文件头 %d 个" % header_count, "重复的原文 %d 条" % len(duplicate_list), duplicate_list[:3])
        mo_path = os.path.join(message_dir, file_name[:-3] + ".mo")
        if not os.path.exists(mo_path):
            content_problem[label] = "没有对应的 MO"
            continue
        with open(mo_path, "rb") as mo_file:
            mo_dict = {key: value for key, value in gettext.GNUTranslations(mo_file)._catalog.items() if key != ""}
        translated_dict = {key: value for key, value in po_dict.items() if value}
        only_mo = [key for key in mo_dict if key not in translated_dict]
        only_po = [key for key in translated_dict if key not in mo_dict]
        different = [key for key in translated_dict if key in mo_dict and mo_dict[key] != translated_dict[key]]
        if only_mo or only_po or different:
            content_problem[label] = ("MO 有而 PO 没译 %d 条" % len(only_mo), "PO 已译而 MO 没有 %d 条" % len(only_po), "译文不同 %d 条" % len(different), [key[:20] for key in (only_mo + only_po + different)[:3]])
check("仓库里有翻译语言的 PO（下面两条才有意义）", file_count >= 5, file_count)
check("每个 PO 只有一个文件头、没有重复的原文（否则 msgfmt 编译不了）", not structure_problem, structure_problem)
check("入库的 MO 与它的 PO 的已译条目逐条相同（不同时跑 buildmo.py 重新编译）", not content_problem, content_problem)

section("2. 游戏要读的翻译域")
missing = []
for language, domain_list in get_text.mo_files_per_language.items():
    for domain in domain_list:
        po_path = os.path.join(PO_ROOT, language, "LC_MESSAGES", domain + ".po")
        if os.path.exists(po_path) and not os.path.exists(po_path[:-3] + ".mo"):
            missing.append("%s/%s" % (language, domain))
check("游戏会读取的翻译域里，有 PO 的都有编译好的 MO", not missing, missing)

finish()
