# -*- coding: UTF-8 -*-
"""
静态检查系统（位置无关包）
这是随游戏发布的运行时自检代码，不可从发行包裁剪。游戏侧通过三个公开函数调用本模块：
run_turn_check() 在每次主场景等待输入前执行检查，run_load_repair() 在载入存档后保守修复已知脏数据，
run_all_checks() 只运行全部检查并返回失败列表；LOG_PATH 供游戏侧提示玩家提交日志。

分层约定：检查层只读当前全局状态且可重复执行；日志层刻意保留跨回合、跨进程的检查级去重记忆；
修复层会写入 cache，并把实际修改逐条留痕。总开关由游戏侧挂钩先行判断，本模块保留状态就绪守卫与绝不抛异常的兜底。
领域检查由 checks/ 子包中的模块通过 check_registry.register_check 装饰器注册，本框架不感知具体检查内容。
"""
import traceback
from typing import List

from Script.Core import cache_control

from . import check_log
from .check_log import LOG_PATH  # noqa: F401  供游戏侧提示文案引用
from .check_registry import CheckFailure, get_all_checks

__all__ = ["run_turn_check", "run_load_repair", "run_all_checks", "LOG_PATH"]

# 触发checks子包下各领域检查模块的导入，使其@register_check装饰器完成注册。
# 本包在主界面面板模块的载入期被导入，任何检查模块的导入期错误都不得阻止游戏启动；
# checks子包会逐模块隔离，外层仍保留总兜底，已注册的检查继续运行并尽力记录失败详情
try:
    from . import checks  # noqa: F401
except Exception as _import_error:
    check_log.write_self_error_log(_import_error)


def run_all_checks() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 所有已注册检查项跑一遍后收集到的失败记录列表，全部通过时返回空列表
    功能:
        对当前全局状态逐一执行全部已注册检查。每个检查函数单独隔离；检查内部异常会转换为一条带检查名的
        CheckFailure，不会中断其余检查项
    """
    failures: List[CheckFailure] = []
    for check_id, (check_name, check_func) in get_all_checks().items():
        try:
            failures.extend(check_func())
        except Exception:
            failures.append(CheckFailure(check_id, f"检查异常({check_name})", traceback.format_exc(), []))
    return failures


def run_turn_check() -> bool:
    """
    参数:
        无
    返回值:
        bool: 本轮是否真的向日志追加了新条目；检查级去重后无新增时返回False
    功能:
        总开关由调用方判断，本函数被调用即执行。cache未就绪时直接跳过；否则运行全部检查并记录本版本首次失败。
        返回True表示本轮新增日志，供游戏侧决定是否绘制提示。任何异常都只尝试留痕，不向调用方抛出
    """
    try:
        cache = cache_control.cache
        if cache is None:
            return False
        if not cache.character_data:
            return False
        if 0 not in cache.character_data:
            return False
        failures = run_all_checks()
        if failures:
            return check_log.write_error_log(failures, cache)
        return False
    except Exception as e:
        check_log.write_self_error_log(e)
        return False


def run_load_repair() -> List[dict]:
    """
    参数:
        无
    返回值:
        List[dict]: 全部实际发生的修复记录；游戏侧可忽略，验证脚本可据此断言
    功能:
        总开关由调用方判断。cache未就绪时直接跳过；就绪后惰性导入repair模块并执行全部修复。
        本层不是纯转发：repair导入期会执行修复注册，重复注册会抛ValueError，因此必须把导入推迟到载入时并兜住异常，
        不得阻断游戏启动。debug_mode下修复整体跳过而检查照常运行；任何异常都只尝试留痕，不向调用方抛出
    """
    try:
        cache = cache_control.cache
        if cache is None:
            return []
        if not cache.character_data:
            return []
        if 0 not in cache.character_data:
            return []
        from . import repair

        return repair.apply_all_repairs(cache)
    except Exception as e:
        check_log.write_self_error_log(e)
        return []
