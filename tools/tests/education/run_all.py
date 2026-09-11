# -*- coding: UTF-8 -*-
"""逐个子进程跑 tools/tests/education/ 下的全部 test_*.py 并汇总

用法（仓库根目录）：
    .conda\\python.exe tools/tests/education/run_all.py            # 全部
    .conda\\python.exe tools/tests/education/run_all.py schedule   # 只跑文件名含 schedule 的

每个测试文件各起一个进程：游戏的导入链会起非守护线程且全局 cache 只能初始化一次，
   同进程串跑会互相污染。单个文件超时 240 秒即判失败（正常一个文件 5~20 秒）。
"""
import glob
import os
import re
import subprocess
import sys
import tempfile
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(TEST_DIR, "..", "..", ".."))
PYTHON = os.path.join(ROOT, ".conda", "python.exe")
if not os.path.exists(PYTHON):
    PYTHON = sys.executable
LOG_DIR = os.path.join(tempfile.gettempdir(), "erArk_education_tests")
os.makedirs(LOG_DIR, exist_ok=True)


def run_one(path: str) -> tuple:
    """
    跑一个测试文件
    Keyword arguments:
    path -- 测试文件路径
    Return arguments:
    tuple -- (通过数int, 失败数int, 状态str, 日志路径str)
    """
    name = os.path.splitext(os.path.basename(path))[0]
    log_path = os.path.join(LOG_DIR, name + ".log")
    start = time.time()
    with open(log_path, "wb") as log_file:
        try:
            proc = subprocess.run([PYTHON, "-u", path], cwd=ROOT, stdout=log_file, stderr=subprocess.STDOUT, timeout=240)
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
    print(f"{name:<28} {status:<10} PASS={pass_count:<4} FAIL={fail_count:<3} {time.time() - start:5.1f}s  {log_path}")
    if fail_count != 0 or status not in ("ok",):
        # 把失败断言与异常尾巴直接带出来，省得再去翻日志
        for line in text.splitlines():
            if "[FAIL]" in line or "Error" in line or "Traceback" in line:
                print("      ", line[:200])
    return pass_count, fail_count, status, log_path


def main():
    """
    入口：按文件名排序逐个跑，最后汇总
    Keyword arguments:
    无
    Return arguments:
    无
    """
    keyword = sys.argv[1] if len(sys.argv) > 1 else ""
    file_list = sorted(glob.glob(os.path.join(TEST_DIR, "test_*.py")))
    if keyword:
        file_list = [one for one in file_list if keyword in os.path.basename(one)]
    total_pass = 0
    total_fail = 0
    bad_file = []
    for path in file_list:
        pass_count, fail_count, status, _log = run_one(path)
        total_pass += max(0, pass_count)
        total_fail += max(0, fail_count)
        if status != "ok" or fail_count != 0:
            bad_file.append(os.path.basename(path))
    print("=" * 60)
    print(f"文件 {len(file_list)} 个，断言通过 {total_pass}，失败 {total_fail}，异常文件 {len(bad_file)}")
    for name in bad_file:
        print("  -", name)
    sys.exit(1 if bad_file else 0)


if __name__ == "__main__":
    main()
