# -*- coding: UTF-8 -*-
"""
flow 线程排版耗时补丁（monkey-patch，不改动产品代码）

用途：
    包裹 Script/UI/Moudle/draw.py 与 panel.py 中的绘制类方法，
    统计 flow 线程侧"排版 + 入队"的分类耗时与数量，
    与 main_frame/io_init 中的受开关保护埋点配合，构成完整的 TK 渲染性能画像。

统计口径说明：
    - 各 key 之间存在嵌套包含关系（如 flow.panel.InScenePanel 包含其内部所有子绘制），
      分析时应以最外层 key 为总量、内层 key 看占比，不能简单相加。
    - flow.bar_cells 为比例条格数累计（每格对应一条图片消息，是消息量放大器指标）。
    - flow.text_index_cache 为 text_handle.get_text_index 的 lru_cache 命中统计采样，
      用于验证"逐字符前缀串把缓存打废"的假设。

使用：
    from profiling import ui_perf_patch
    ui_perf_patch.apply_flow_draw_patches()
    （需在 perf_hook.enabled = True 后由 game.py 或基准脚本调用）
"""
import time

from Script.Core import perf_hook, text_handle

_patched = False
""" 防止重复打补丁的标志 """


def _wrap_draw_method(cls, key: str, bar_cell_count: bool = False):
    """
    包裹一个绘制类的 draw 方法进行计时
    参数:
        cls (type) -- 目标绘制类（须自带 draw 方法定义）
        key (str) -- 计时分类键名
        bar_cell_count (bool) -- 是否额外累计比例条格数（len(self.draw_list)）
    返回值类型：无
    功能描述：把 cls.draw 替换为带 perf_hook 计时的包装函数，开关关闭时直通原函数
    """
    original = cls.__dict__.get("draw")
    if original is None:
        # 该类没有自己定义 draw（继承自父类），跳过以免重复计时
        return

    def _timed_draw(self, *args, **kwargs):
        # 性能开关关闭时直通，避免额外开销
        if not perf_hook.enabled:
            return original(self, *args, **kwargs)
        if bar_cell_count:
            perf_hook.hook_count("flow.bar_cells", len(getattr(self, "draw_list", ())))
        t0 = time.perf_counter()
        try:
            return original(self, *args, **kwargs)
        finally:
            perf_hook.hook_time(key, time.perf_counter() - t0)

    _timed_draw.__name__ = getattr(original, "__name__", "draw")
    _timed_draw.__doc__ = getattr(original, "__doc__", None)
    cls.draw = _timed_draw


def sample_text_index_cache():
    """
    采样 get_text_index 的 lru_cache 命中统计
    参数：无
    返回值类型：无
    功能描述：把 text_handle.get_text_index.cache_info() 的命中/未命中/当前容量
              写入采样值，随每屏报告输出，用于验证缓存是否被逐字符前缀串打废
    """
    if not perf_hook.enabled:
        return
    try:
        info = text_handle.get_text_index.cache_info()
    except AttributeError:
        # get_text_index 未使用 lru_cache 时跳过
        return
    perf_hook.hook_value(
        "flow.text_index_cache",
        {"hits": info.hits, "misses": info.misses, "currsize": info.currsize},
    )


def apply_flow_draw_patches():
    """
    应用全部 flow 侧排版计时补丁
    参数：无
    返回值类型：无
    功能描述：包裹 draw.py / panel.py / in_scene_panel.py 的关键绘制方法；
              幂等，重复调用只生效一次
    """
    global _patched
    if _patched:
        return
    _patched = True

    from Script.UI.Moudle import draw, panel

    # 基础文本绘制类（O(n²) 宽度测量的嫌疑点）
    _wrap_draw_method(draw.NormalDraw, "flow.draw.NormalDraw")
    _wrap_draw_method(draw.WaitDraw, "flow.draw.WaitDraw")
    _wrap_draw_method(draw.LineFeedWaitDraw, "flow.draw.LineFeedWaitDraw")
    _wrap_draw_method(draw.CenterDraw, "flow.draw.CenterDraw")
    _wrap_draw_method(draw.RightDraw, "flow.draw.RightDraw")
    if hasattr(draw, "LeftDraw"):
        _wrap_draw_method(draw.LeftDraw, "flow.draw.LeftDraw")
    # 比例条（每格一条图片消息的放大器）
    _wrap_draw_method(draw.BarDraw, "flow.draw.BarDraw", bar_cell_count=True)
    if hasattr(draw, "InfoBarDraw"):
        _wrap_draw_method(draw.InfoBarDraw, "flow.draw.InfoBarDraw")
    # 按钮类
    _wrap_draw_method(draw.Button, "flow.draw.Button")
    if hasattr(draw, "CenterButton"):
        _wrap_draw_method(draw.CenterButton, "flow.draw.CenterButton")
    if hasattr(draw, "LeftButton"):
        _wrap_draw_method(draw.LeftButton, "flow.draw.LeftButton")
    # 面板容器
    if hasattr(panel, "DrawTextListPanel"):
        _wrap_draw_method(panel.DrawTextListPanel, "flow.panel.DrawTextListPanel")

    # 主场景面板：整屏排版总耗时 + 每屏采样一次文本宽度缓存统计
    try:
        from Script.UI.Panel import in_scene_panel

        original_scene_draw = in_scene_panel.InScenePanel.__dict__.get("draw")
        if original_scene_draw is not None:

            def _timed_scene_draw(self, *args, **kwargs):
                # 性能开关关闭时直通
                if not perf_hook.enabled:
                    return original_scene_draw(self, *args, **kwargs)
                t0 = time.perf_counter()
                try:
                    return original_scene_draw(self, *args, **kwargs)
                finally:
                    perf_hook.hook_time("flow.panel.InScenePanel", time.perf_counter() - t0)
                    sample_text_index_cache()

            in_scene_panel.InScenePanel.draw = _timed_scene_draw
    except Exception:
        # 主场景面板导入失败不影响其余补丁
        pass
