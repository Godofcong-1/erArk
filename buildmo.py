#!/usr/bin/python3
# -*- coding: UTF-8 -*-
"""
把 data/po 下各语言的 PO 文件编译成游戏运行时读取的 MO 文件

用法：
    python buildmo.py              MO 写在各 PO 旁边（data/po/<语言>/LC_MESSAGES/）
    python buildmo.py --out DIR    MO 写到 DIR/<语言>/LC_MESSAGES/，不动仓库里的 MO（用来先核对编译结果）

- 编译 data/po 下除 zh_CN 以外每种语言目录里的每个 .po。zh_CN 是原文语言：游戏用中文时直接显示原文、不读 MO，
  它的 PO 由 buildconfig.py / auto_build_config.py / buildpo.py 生成，只作为翻译的原文。
- 优先用 gettext 的 msgfmt；PATH 里没有 msgfmt 时改用 polib（pip install polib，游戏本身不依赖它）。
- 任何一个 PO 编译失败（例如文件里有重复的文件头或重复的 msgid）都会打印原因，并在全部处理完后以退出码 1 结束；
  失败的那个 PO 不会留下写了一半的 MO，原有的 MO 保持不变。
"""
import argparse
import os
import shutil
import subprocess
import sys
from typing import List, Tuple

PO_ROOT = os.path.join("data", "po")
""" 各语言 PO 文件所在的根目录 """
SOURCE_LANGUAGE = "zh_CN"
""" 原文语言，不编译 """


def find_po_files(po_root: str) -> List[Tuple[str, str]]:
    """
    列出要编译的 PO 文件
    Keyword arguments:
    po_root -- 各语言目录所在的根目录
    Return arguments:
    List[Tuple[str, str]] -- (语言, 不带扩展名的文件名) 的列表，按语言与文件名排序，不含原文语言
    """
    po_file_list: List[Tuple[str, str]] = []
    for language in sorted(os.listdir(po_root)):
        if language == SOURCE_LANGUAGE:
            continue
        message_dir = os.path.join(po_root, language, "LC_MESSAGES")
        if not os.path.isdir(message_dir):
            continue
        for file_name in sorted(os.listdir(message_dir)):
            if file_name.endswith(".po"):
                po_file_list.append((language, file_name[: -len(".po")]))
    return po_file_list


def compile_po(po_path: str, mo_path: str, msgfmt_path: str) -> str:
    """
    把一个 PO 文件编译成 MO 文件
    先编译到同目录下的临时文件，成功后再替换目标文件，失败时不留下残缺的 MO
    Keyword arguments:
    po_path -- PO 文件路径
    mo_path -- 要写出的 MO 文件路径
    msgfmt_path -- msgfmt 的路径，空串表示改用 polib
    Return arguments:
    str -- 失败原因，成功时为空串
    """
    tmp_path = mo_path + ".tmp"
    error_text = ""
    try:
        if msgfmt_path:
            result = subprocess.run([msgfmt_path, "-o", tmp_path, po_path], capture_output=True)
            if result.returncode != 0:
                error_text = result.stderr.decode("utf-8", errors="replace").strip() or "msgfmt 退出码 %d" % result.returncode
        else:
            import polib

            polib.pofile(po_path).save_as_mofile(tmp_path)
    except Exception as error:  # noqa: BLE001  任何原因的失败都只算这一个文件失败，继续编译其余文件
        error_text = repr(error)
    if not error_text and not os.path.exists(tmp_path):
        error_text = "没有生成 MO 文件"
    if error_text:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        return error_text
    os.replace(tmp_path, mo_path)
    return ""


def main() -> int:
    """
    读取命令行参数，编译每种语言的全部 PO 文件
    Keyword arguments:
    无
    Return arguments:
    int -- 退出码：全部成功为 0，有任何一个失败（或没有可用的编译工具）为 1
    """
    parser = argparse.ArgumentParser(description="把 data/po 下各语言的 PO 文件编译成 MO 文件")
    parser.add_argument("--out", help="MO 文件的输出根目录，默认写在各 PO 旁边")
    args = parser.parse_args()

    msgfmt_path = shutil.which("msgfmt") or ""
    if not msgfmt_path:
        try:
            import polib  # noqa: F401
        except ImportError:
            print("找不到 gettext 的 msgfmt，也没有安装 polib：请安装其中之一（pip install polib）")
            return 1
        print("PATH 里没有 msgfmt，改用 polib 编译")

    out_root = args.out if args.out else PO_ROOT
    fail_list: List[str] = []
    for language, name in find_po_files(PO_ROOT):
        po_path = os.path.join(PO_ROOT, language, "LC_MESSAGES", name + ".po")
        out_dir = os.path.join(out_root, language, "LC_MESSAGES")
        os.makedirs(out_dir, exist_ok=True)
        mo_path = os.path.join(out_dir, name + ".mo")
        error_text = compile_po(po_path, mo_path, msgfmt_path)
        if error_text:
            fail_list.append(po_path)
            print("[失败] %s\n%s" % (po_path, error_text))
        else:
            print("[完成] %s" % mo_path)
    if fail_list:
        print("有 %d 个 PO 文件编译失败，对应的 MO 没有更新：%s" % (len(fail_list), "、".join(fail_list)))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
