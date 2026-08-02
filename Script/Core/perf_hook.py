# -*- coding: UTF-8 -*-
"""
轻量性能计时中心

用途：
    为 TK 绘制模式的性能剖析提供统一的计时/计数收集点。
    flow 线程（游戏逻辑/排版入队）与 GUI 线程（Tk 渲染）分别以
    "flow." / "gui." 前缀的 key 写入数据，在每屏渲染完成
    （GUI 侧输入上膛 _do_arm）时由 flush_screen_report() 落一行 JSONL。

设计约束：
    - 模块级开关 enabled 默认 False，所有钩子函数第一行判断开关，
      关闭时仅一次分支判断开销，不影响正常游戏。
    - 只依赖标准库，禁止导入任何 Script 包内模块（避免循环导入）。
    - 线程安全：flow / GUI 双线程并发写入，用一把粗粒度锁保护。
"""
import json
import os
import threading
import time

enabled = False
""" 总开关：False 时所有钩子为空操作 """

_lock = threading.Lock()
""" 保护累计数据的线程锁 """
_time_data = {}
""" 分类计时累计：key -> [调用次数, 总耗时秒, 单次最大耗时秒] """
_count_data = {}
""" 分类计数累计：key -> 次数 """
_value_data = {}
""" 最新采样值：key -> 数值（如 tag 总数等瞬时量） """
_mark_data = {}
""" 时间戳标记：key -> perf_counter 时间戳（用于跨线程配对） """
_total_time_data = {}
""" 会话级累计计时（跨屏不清零），结构同 _time_data """
_total_count_data = {}
""" 会话级累计计数（跨屏不清零） """
_screen_index = 0
""" 已 flush 的屏数 """
_output_path = ""
""" JSONL 输出文件路径，首次 flush 时创建 """
_session_start = time.time()
""" 会话开始的墙钟时间 """


def hook_time(key: str, dt: float):
    """
    累计一段耗时
    参数:
        key (str) -- 分类键名，flow 线程用 "flow." 前缀，GUI 线程用 "gui." 前缀
        dt (float) -- 本次耗时（秒）
    返回值类型：无
    功能描述：把一次耗时累计到分类字典（次数/总耗时/最大单次耗时）
    """
    if not enabled:
        return
    with _lock:
        rec = _time_data.get(key)
        if rec is None:
            _time_data[key] = [1, dt, dt]
        else:
            rec[0] += 1
            rec[1] += dt
            if dt > rec[2]:
                rec[2] = dt


def hook_count(key: str, n: int = 1):
    """
    累计一个计数
    参数:
        key (str) -- 分类键名
        n (int) -- 增量，默认 1
    返回值类型：无
    功能描述：把计数累计到分类字典（如消息条数、字节数）
    """
    if not enabled:
        return
    with _lock:
        _count_data[key] = _count_data.get(key, 0) + n


def hook_value(key: str, value):
    """
    记录一个瞬时采样值
    参数:
        key (str) -- 分类键名
        value -- 采样值（覆盖旧值）
    返回值类型：无
    功能描述：记录最新采样值（如 Text 控件当前 tag 总数），flush 时随屏报告输出
    """
    if not enabled:
        return
    with _lock:
        _value_data[key] = value


def mark(key: str):
    """
    记录一个时间戳标记
    参数:
        key (str) -- 标记键名
    返回值类型：无
    功能描述：记录 perf_counter 时间戳，用于跨线程端到端延迟配对
              （如 flow 侧入队完成 -> GUI 侧界面可交互）
    """
    if not enabled:
        return
    with _lock:
        _mark_data[key] = time.perf_counter()


def get_mark(key: str) -> float:
    """
    读取一个时间戳标记
    参数:
        key (str) -- 标记键名
    返回值类型：float -- perf_counter 时间戳，不存在返回 0.0
    功能描述：读取 mark() 记录的时间戳
    """
    with _lock:
        return _mark_data.get(key, 0.0)


def clear_mark(key: str):
    """
    清除一个时间戳标记
    参数:
        key (str) -- 标记键名
    返回值类型：无
    功能描述：清除标记，使 get_mark 返回 0.0（用于"每屏第一次"类判定的复位）
    """
    if not enabled:
        return
    with _lock:
        _mark_data.pop(key, None)


def _ensure_output_path() -> str:
    """
    确保 JSONL 输出文件路径已初始化
    参数：无
    返回值类型：str -- 输出文件路径
    功能描述：首次调用时在 profiling_output/ 下按启动时间创建输出文件路径
    """
    global _output_path
    if not _output_path:
        out_dir = "profiling_output"
        os.makedirs(out_dir, exist_ok=True)
        stamp = time.strftime("%Y%m%d_%H%M%S", time.localtime(_session_start))
        _output_path = os.path.join(out_dir, f"ui_perf_{stamp}.jsonl")
    return _output_path


def flush_screen_report(extra: dict = None):
    """
    输出本屏性能报告并清零屏内累计
    参数:
        extra (dict) -- 附加字段（如端到端延迟），会合并进本行 JSON
    返回值类型：无
    功能描述：把自上次 flush 以来累计的计时/计数落一行 JSONL 到
              profiling_output/ui_perf_<启动时间>.jsonl，随后清零屏内数据；
              同时把屏内数据并入会话级累计（供基准脚本最终汇总）。
              一般由 GUI 线程在输入上膛（_do_arm）时调用，即"一屏"的边界。
    """
    global _screen_index
    if not enabled:
        return
    with _lock:
        # 空屏（无任何计时和计数）不落盘，避免空 arm 产生噪声行
        if not _time_data and not _count_data:
            return
        _screen_index += 1
        report = {
            "screen": _screen_index,
            "wall_time": round(time.time() - _session_start, 3),
            "times_ms": {
                k: {
                    "calls": v[0],
                    "total_ms": round(v[1] * 1000, 3),
                    "max_ms": round(v[2] * 1000, 3),
                }
                for k, v in sorted(_time_data.items())
            },
            "counts": dict(sorted(_count_data.items())),
            "values": dict(sorted(_value_data.items())),
        }
        if extra:
            report.update(extra)
        # 并入会话级累计
        for k, v in _time_data.items():
            rec = _total_time_data.get(k)
            if rec is None:
                _total_time_data[k] = list(v)
            else:
                rec[0] += v[0]
                rec[1] += v[1]
                if v[2] > rec[2]:
                    rec[2] = v[2]
        for k, v in _count_data.items():
            _total_count_data[k] = _total_count_data.get(k, 0) + v
        _time_data.clear()
        _count_data.clear()
        path = _ensure_output_path()
    # 文件写入放在锁外，避免磁盘慢时阻塞钩子调用方
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(report, ensure_ascii=False) + "\n")
    except OSError:
        pass


def get_screen_count() -> int:
    """
    获取已 flush 的屏数
    参数：无
    返回值类型：int -- 已落盘的屏报告数量
    功能描述：供自动化基准脚本轮询"GUI 侧是否已渲染完当前屏"
    """
    with _lock:
        return _screen_index


def get_session_summary() -> dict:
    """
    获取会话级累计汇总
    参数：无
    返回值类型：dict -- {"screens": 屏数, "times_ms": 分类计时, "counts": 分类计数}
    功能描述：返回自启动以来所有已 flush 屏的累计数据，供基准脚本结束时输出总表
    """
    with _lock:
        return {
            "screens": _screen_index,
            "times_ms": {
                k: {
                    "calls": v[0],
                    "total_ms": round(v[1] * 1000, 3),
                    "max_ms": round(v[2] * 1000, 3),
                }
                for k, v in sorted(_total_time_data.items())
            },
            "counts": dict(sorted(_total_count_data.items())),
        }


def get_output_path() -> str:
    """
    获取当前 JSONL 输出文件路径
    参数：无
    返回值类型：str -- 输出文件路径（尚未 flush 过则为将要使用的路径）
    功能描述：供外部脚本/日志提示输出位置
    """
    with _lock:
        return _ensure_output_path()
