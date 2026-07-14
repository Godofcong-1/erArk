# -*- coding: UTF-8 -*-
"""共享紧凑数值格式回归测试。"""

import ast
import copy
from pathlib import Path

import pytest


ATTR_TEXT_PATH = Path(__file__).resolve().parents[1] / "Script" / "Design" / "attr_text.py"


def load_get_value_text():
    """参数：无；返回：callable为源码中的格式函数；用途：隔离加载纯格式逻辑。"""
    source_tree = ast.parse(ATTR_TEXT_PATH.read_text(encoding="utf-8"), filename=str(ATTR_TEXT_PATH))
    function_node = next(node for node in source_tree.body if isinstance(node, ast.FunctionDef) and node.name == "get_value_text")
    module_node = ast.fix_missing_locations(ast.Module(body=[copy.deepcopy(function_node)], type_ignores=[]))
    namespace = {}
    exec(compile(module_node, str(ATTR_TEXT_PATH), "exec"), namespace)
    return namespace["get_value_text"]


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (999, "+999"),
        (-999, "-999"),
        (-500, "-500"),
        (1000, "+1K"),
        (-1000, "-1K"),
        (999999, "+999K"),
        (-999999, "-999K"),
        (1000000, "+1M"),
        (-1000000, "-1M"),
        (999999999, "+999M"),
        (-999999999, "-999M"),
        (1000000000, "+1G"),
        (-1000000000, "-1G"),
    ],
)
def test_compact_value_formatter_uses_approved_boundaries(value, expected):
    """参数：输入值与期望文本；返回：None；用途：锁定符号与K/M/G量级边界。"""
    assert load_get_value_text()(value) == expected


def test_compact_value_formatter_truncates_fractional_input():
    """参数：无；返回：None；用途：锁定新定义的调用入口小数截断契约。"""
    assert load_get_value_text()(999.9) == "+999"
    assert load_get_value_text()(-999.9) == "-999"
