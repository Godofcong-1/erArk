# -*- coding: UTF-8 -*-
"""逐个子进程跑 tools/tests/ 下全部套件的 test_*.py 并汇总

套件 = tools/tests/ 下的子目录（名字不以 _ 或 . 开头、里面有 test_*.py），自动发现，新增套件不用改 CI。

用法（仓库根目录）：
    .conda\\python.exe tools/tests/run_all.py                  # 全部套件
    .conda\\python.exe tools/tests/run_all.py core             # 只跑路径（套件/文件名）里含 core 的
    .conda\\python.exe tools/tests/run_all.py core/test_map    # 只跑某一个文件

每个测试文件各起一个进程：游戏的全局 cache 只能初始化一次，
   同进程串跑会互相污染。单个文件超时 240 秒即判失败（正常一个文件 5~20 秒）。
日志写在 %TEMP%/erArk_tests/<套件>/<文件名>.log，CI 失败时由 Show Test Logs 一步打出末尾。
"""
import glob
import os
import re
import subprocess
import sys
import tempfile
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
""" tools/tests 目录 """
ROOT = os.path.abspath(os.path.join(TESTS_DIR, "..", ".."))
""" 仓库根目录 """
PYTHON = os.path.join(ROOT, ".conda", "python.exe")
if not os.path.exists(PYTHON):
    # CI 里没有 .conda，退回当前解释器
    PYTHON = sys.executable
LOG_ROOT = os.path.join(tempfile.gettempdir(), "erArk_tests")
""" 日志根目录 """
FILE_TIMEOUT = 240
""" 单个测试文件的超时秒数 """


def discover_suites() -> list:
    """
    发现全部测试套件
    Keyword arguments:
    无
    Return arguments:
    list -- 套件目录名列表，按名字排序
    """
    suite_list = []
    for name in sorted(os.listdir(TESTS_DIR)):
        path = os.path.join(TESTS_DIR, name)
        if not os.path.isdir(path) or name.startswith(("_", ".")):
            continue
        if glob.glob(os.path.join(path, "test_*.py")):
            suite_list.append(name)
    return suite_list


def run_one(suite: str, path: str) -> tuple:
    """
    跑一个测试文件
    Keyword arguments:
    suite -- 所属套件名
    path -- 测试文件路径
    Return arguments:
    tuple -- (通过数int, 失败数int, 状态str, 日志路径str, 已知问题名list)
    """
    name = os.path.splitext(os.path.basename(path))[0]
    log_dir = os.path.join(LOG_ROOT, suite)
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, name + ".log")
    start = time.time()
    with open(log_path, "wb") as log_file:
        try:
            proc = subprocess.run([PYTHON, "-u", path], cwd=ROOT, stdout=log_file, stderr=subprocess.STDOUT, timeout=FILE_TIMEOUT)
            code = proc.returncode
            status = "ok" if code == 0 else f"exit {code}"
        except subprocess.TimeoutExpired:
            status = "timeout"
    text = open(log_path, "rb").read().decode("utf-8", errors="replace")
    match = re.search(r"PASS=(\d+) FAIL=(\d+)", text)
    pass_count = int(match.group(1)) if match else 0
    fail_count = int(match.group(2)) if match else -1
    if match is None:
        status = "crash" if status == "ok" else status
    # 已知问题（headless_base.known_issue）：不算失败，但在汇总里列出来，免得被遗忘
    known_list = [line.strip()[len("[KNOWN] "):].split(" —— ")[0] for line in text.splitlines() if line.strip().startswith("[KNOWN] ")]
    label = f"{suite}/{name}"
    known_text = f"KNOWN={len(known_list)}" if known_list else ""
    print(f"{label:<40} {status:<10} PASS={pass_count:<4} FAIL={fail_count:<3} {time.time() - start:5.1f}s  {known_text:<9} {log_path}")
    if fail_count != 0 or status not in ("ok",):
        # 把失败断言与异常尾巴直接带出来，省得再去翻日志
        for line in text.splitlines():
            if "[FAIL]" in line or "Error" in line or "Traceback" in line:
                print("      ", line[:200])
    return pass_count, fail_count, status, log_path, known_list


def main(suite_list: list = None, keyword: str = None):
    """
    入口：按套件名、文件名排序逐个跑，最后汇总，有失败时以退出码 1 结束
    Keyword arguments:
    suite_list -- 只跑这些套件，None 为自动发现的全部套件
    keyword -- 只跑「套件/文件名」里含这个关键字的文件，None 时取命令行第一个参数
    Return arguments:
    无
    """
    if keyword is None:
        keyword = sys.argv[1] if len(sys.argv) > 1 else ""
    keyword = keyword.replace("\\", "/")
    if suite_list is None:
        suite_list = discover_suites()
    job_list = []
    for suite in suite_list:
        for path in sorted(glob.glob(os.path.join(TESTS_DIR, suite, "test_*.py"))):
            label = f"{suite}/{os.path.basename(path)}"
            if keyword and keyword not in label:
                continue
            job_list.append((suite, path))
    if not job_list:
        print(f"没有匹配的测试文件（套件：{', '.join(suite_list) or '无'}，关键字：{keyword or '无'}）")
        sys.exit(1)
    total_pass = 0
    total_fail = 0
    bad_file = []
    all_known = []
    for suite, path in job_list:
        pass_count, fail_count, status, _log, known_list = run_one(suite, path)
        total_pass += max(0, pass_count)
        total_fail += max(0, fail_count)
        all_known.extend(f"{suite}/{os.path.basename(path)}：{name}" for name in known_list)
        if status != "ok" or fail_count != 0:
            bad_file.append(f"{suite}/{os.path.basename(path)}")
    print("=" * 60)
    suite_count = len({suite for suite, _path in job_list})
    print(f"套件 {suite_count} 个，文件 {len(job_list)} 个，断言通过 {total_pass}，失败 {total_fail}，异常文件 {len(bad_file)}，已知问题 {len(all_known)}")
    for name in bad_file:
        print("  -", name)
    for name in all_known:
        print("  ~", name)
    sys.exit(1 if bad_file else 0)


if __name__ == "__main__":
    main()
