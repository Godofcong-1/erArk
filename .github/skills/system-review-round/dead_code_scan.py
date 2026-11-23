# -*- coding: UTF-8 -*-
"""
死代码扫描（system-review-round skill，P0 基线）

把 Plan 29 / 30 复查里「按代码 token 统计引用（去掉注释与字符串）」的做法固化成脚本：
    1. 用 ast 收集目标目录里定义的顶层函数、类、类方法、模块级常量
    2. 用 tokenize 扫全仓库的 .py，只数 NAME token（注释与字符串是别的 token 类型，天然被排除），
       按「生产代码 / 测试代码」分开计数，再扣掉定义处本身
    3. 输出零引用清单，分三类：注册式（装饰器名以 register 或 add_ 开头，没有直接调用方是正常的）、
       只有测试引用（生产代码里没人用）、完全无引用

用法（在仓库根目录）：
    ./.conda/python.exe .github/skills/system-review-round/dead_code_scan.py Script/System/Education_System
    ./.conda/python.exe .github/skills/system-review-round/dead_code_scan.py Script/System/Education_System --list-all

局限：按名字计数，同名的方法 / 函数在别处被引用也会算作引用（只会漏报、不会误报）；
通过字符串反射调用（getattr(obj, "name")）的不算引用，这类要人工确认。
"""
import argparse
import ast
import collections
import os
import sys
import tokenize

SKIP_DIRS = {".git", ".conda", "__pycache__", "plan", "node_modules", ".venv", "venv", "build", "dist"}
""" 不扫描的目录名 """
REGISTER_PREFIXES = ("register", "add_")
""" 装饰器名以这些前缀开头即视为注册式定义（如 register_provider、add_premise、add_settle_behavior_effect） """


def find_root(start: str) -> str:
    """
    从起点向上找仓库根目录（含 game.py 的目录）
    Keyword arguments:
    start -- 起始目录
    Return arguments:
    str -- 仓库根目录；找不到时返回当前工作目录
    """
    path = os.path.abspath(start)
    while True:
        if os.path.isfile(os.path.join(path, "game.py")):
            return path
        parent = os.path.dirname(path)
        if parent == path:
            return os.getcwd()
        path = parent


def iter_py_files(base: str):
    """
    遍历目录下的全部 .py 文件（跳过 SKIP_DIRS）
    Keyword arguments:
    base -- 起始目录
    Return arguments:
    generator[str] -- .py 文件的绝对路径
    """
    for dir_path, dir_names, file_names in os.walk(base):
        dir_names[:] = [d for d in dir_names if d not in SKIP_DIRS]
        for file_name in file_names:
            if file_name.endswith(".py"):
                yield os.path.join(dir_path, file_name)


def is_test_file(path: str, root: str) -> bool:
    """
    判断一个文件是否属于测试代码
    Keyword arguments:
    path -- 文件绝对路径
    root -- 仓库根目录
    Return arguments:
    bool -- 在 tools/tests 下或文件名以 test_ 开头即为测试代码
    """
    rel = os.path.relpath(path, root).replace("\\", "/")
    return rel.startswith("tools/tests/") or os.path.basename(path).startswith("test_")


def decorator_name(node: ast.AST) -> str:
    """
    取装饰器的末端名字（@a.b.register_x(...) → register_x）
    Keyword arguments:
    node -- 装饰器节点
    Return arguments:
    str -- 名字，取不到时为空串
    """
    if isinstance(node, ast.Call):
        return decorator_name(node.func)
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Name):
        return node.id
    return ""


def is_registered(node: ast.AST) -> bool:
    """
    判断函数或类是否由注册式装饰器登记
    Keyword arguments:
    node -- 函数或类的定义节点
    Return arguments:
    bool -- 任一装饰器名以 REGISTER_PREFIXES 开头
    """
    return any(decorator_name(d).startswith(REGISTER_PREFIXES) for d in getattr(node, "decorator_list", []))


def collect_definitions(target: str, root: str) -> list:
    """
    收集目标目录里的定义
    Keyword arguments:
    target -- 目标目录的绝对路径
    root -- 仓库根目录
    Return arguments:
    list[dict] -- 每项含 name / kind / file / line / registered
    """
    result = []
    for path in iter_py_files(target):
        with open(path, "rb") as file:
            source = file.read()
        try:
            tree = ast.parse(source, filename=path)
        except SyntaxError as error:
            print(f"[跳过] 语法错误 {path}: {error}")
            continue
        rel = os.path.relpath(path, root).replace("\\", "/")

        # 模块顶层：函数、类、常量；类体内：方法
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                result.append({"name": node.name, "kind": "函数", "file": rel, "line": node.lineno, "registered": is_registered(node)})
            elif isinstance(node, ast.ClassDef):
                result.append({"name": node.name, "kind": "类", "file": rel, "line": node.lineno, "registered": is_registered(node)})
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and not (item.name.startswith("__") and item.name.endswith("__")):
                        result.append({"name": item.name, "kind": "方法", "file": rel, "line": item.lineno, "registered": is_registered(item)})
            elif isinstance(node, (ast.Assign, ast.AnnAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                for target_node in targets:
                    if isinstance(target_node, ast.Name) and not target_node.id.startswith("__"):
                        result.append({"name": target_node.id, "kind": "常量", "file": rel, "line": node.lineno, "registered": False})
    return result


def count_name_tokens(root: str):
    """
    统计全仓库 .py 的 NAME token 出现次数，按生产 / 测试分开
    Keyword arguments:
    root -- 仓库根目录
    Return arguments:
    tuple[Counter, Counter] -- (生产代码计数, 测试代码计数)
    """
    prod = collections.Counter()
    test = collections.Counter()
    for path in iter_py_files(root):
        counter = test if is_test_file(path, root) else prod
        try:
            with open(path, "rb") as file:
                for token in tokenize.tokenize(file.readline):
                    if token.type == tokenize.NAME:
                        counter[token.string] += 1
        except (tokenize.TokenError, SyntaxError, UnicodeDecodeError) as error:
            print(f"[跳过] 无法分词 {path}: {error}")
    return prod, test


def main():
    """
    命令行入口：扫描并打印报告
    Keyword arguments:
    无
    Return arguments:
    无
    """
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="按代码 token 统计引用的死代码扫描")
    parser.add_argument("target", help="要扫描的模块目录（相对仓库根目录或绝对路径）")
    parser.add_argument("--list-all", action="store_true", help="同时列出注册式与只有测试引用的定义")
    options = parser.parse_args()

    root = find_root(os.path.dirname(os.path.abspath(__file__)))
    target = options.target if os.path.isabs(options.target) else os.path.join(root, options.target)
    if not os.path.isdir(target):
        print(f"目录不存在：{target}")
        sys.exit(2)

    definitions = collect_definitions(target, root)
    prod, test = count_name_tokens(root)
    # 同名定义在目标目录里出现几次，就扣掉几次（定义处本身的那个 token）
    own = collections.Counter(d["name"] for d in definitions)

    registered, test_only, unused = [], [], []
    for d in definitions:
        prod_refs = prod[d["name"]] - own[d["name"]]
        if prod_refs > 0:
            continue
        if d["registered"]:
            registered.append(d)
        elif test[d["name"]] > 0:
            test_only.append(d)
        else:
            unused.append(d)

    kinds = collections.Counter(d["kind"] for d in definitions)
    print(f"扫描目录：{os.path.relpath(target, root)}")
    print(f"定义总数：{len(definitions)}（" + " / ".join(f"{k} {v}" for k, v in sorted(kinds.items())) + "）")
    print(f"生产代码零引用：注册式 {len(registered)}、只有测试引用 {len(test_only)}、完全无引用 {len(unused)}")

    def show(title: str, items: list):
        """
        打印一组定义
        Keyword arguments:
        title -- 分组标题
        items -- 定义列表
        Return arguments:
        无
        """
        print(f"\n== {title}（{len(items)}）")
        for d in items:
            print(f"  {d['file']}:{d['line']}  {d['kind']}  {d['name']}")

    show("完全无引用", unused)
    show("只有测试引用", test_only)
    if options.list_all:
        show("注册式（没有直接调用方是正常的）", registered)


if __name__ == "__main__":
    main()
