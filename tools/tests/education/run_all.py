# -*- coding: UTF-8 -*-
"""只跑生长养成系统这一个套件（tools/tests/education/），实际由上一级的 tools/tests/run_all.py 执行

用法（仓库根目录）：
    .conda\\python.exe tools/tests/education/run_all.py            # 本套件全部
    .conda\\python.exe tools/tests/education/run_all.py schedule   # 只跑文件名含 schedule 的

跑全部套件用 tools/tests/run_all.py；日志写在 %TEMP%/erArk_tests/education/<文件名>.log。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import run_all as _suite_runner  # noqa: E402  tools/tests/run_all.py

if __name__ == "__main__":
    _suite_runner.main(["education"])
