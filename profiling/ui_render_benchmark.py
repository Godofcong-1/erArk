#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
erArk TK 渲染性能自动化基准脚本

原理：
    加载存档后，直接进入主场景面板 InScenePanel 的真实 while-1 重绘循环，
    但把 flow_handle.askfor_all 替换为"入队上膛标记 -> 等待 GUI 线程渲染完成 -> 直接返回"，
    从而无人值守地驱动 N 次完整主界面重绘（真实 Tk 窗口、真实渲染路径）。
    每屏的分类耗时由 Script/Core/perf_hook.py + main_frame/io_init 埋点 +
    profiling/ui_perf_patch.py 排版补丁收集，逐屏写入 JSONL，结束时输出会话汇总。

使用示例：
    python -m profiling.ui_render_benchmark --load-save 1 --screens 30

输出：
    profiling_output/ui_perf_<时间戳>.jsonl            —— 每屏分类耗时明细
    profiling_output/ui_render_benchmark_<时间戳>.json —— 会话汇总（分类耗时总表 + 每屏端到端延迟）
"""
import argparse
import json
import os
import sys
import time
import traceback
from datetime import datetime
from types import SimpleNamespace

PROFILE_DIR = "profiling_output"
os.makedirs(PROFILE_DIR, exist_ok=True)


def log(msg):
    """
    输出带前缀的日志
    参数:
        msg (str) -- 日志内容
    返回值类型：无
    功能描述：统一日志前缀，便于与游戏自身输出区分
    """
    print(f"[ui_benchmark] {msg}", flush=True)


def parse_args():
    """
    解析命令行参数
    参数：无
    返回值类型：argparse.Namespace
    功能描述：提供存档号、重绘屏数、单屏超时等参数
    """
    ap = argparse.ArgumentParser()
    ap.add_argument("--load-save", type=str, default="1", help="要加载的存档 id（数字或 auto）")
    ap.add_argument("--screens", type=int, default=30, help="要执行的主界面完整重绘次数")
    ap.add_argument("--timeout-per-screen", type=float, default=60.0, help="单屏渲染等待超时（秒）")
    ap.add_argument("--summary-name", type=str, default="ui_render_benchmark", help="汇总输出文件前缀")
    ap.add_argument("--panel", type=str, default="scene", choices=["scene", "map"], help="基准面板：scene=主场景互动界面，map=查看地图界面")
    ap.add_argument("--warmup-screens", type=int, default=0, help="预热屏数：先绘制N屏（不计入统计）让Tk完成字形/行度量，然后清屏再开始正式测量，用于验证启动期预热方案的效果")
    ap.add_argument("--no-warmup-clear", action="store_true", help="预热后不清屏（对照实验：区分尖峰来自字形度量还是清屏后重建）")
    ap.add_argument("--prewarm", action="store_true", help="调用产品化预热函数 io_init.warm_up_text_metrics()（等价于真实启动流程 game_init.init 中的预热）")
    return ap.parse_args()


def main():
    """
    基准主入口
    参数：无
    返回值类型：无
    功能描述：初始化游戏环境 -> 打开性能埋点 -> 替换输入等待函数 ->
              启动 Tk 主循环与 flow 线程执行 N 次主界面重绘 -> 输出汇总后退出进程
    """
    args = parse_args()

    # 复用无渲染基准脚本的环境初始化（不打 IO 补丁，保留真实绘制）
    from profiling.run_profile import init_game_environment

    env_args = SimpleNamespace(
        with_premise_profiler=False,
        load_save=args.load_save,
        try_load_auto=False,
    )
    init_game_environment(env_args)

    from Script.Core import perf_hook

    # 打开性能埋点并应用 flow 侧排版补丁
    perf_hook.enabled = True
    from profiling import ui_perf_patch

    ui_perf_patch.apply_flow_draw_patches()

    from Script.Core import cache_control, constant, flow_handle, io_init
    from Script.Config import normal_config

    cache = cache_control.cache

    if not cache.character_data or 0 not in cache.character_data:
        log("错误：存档未正确加载（无玩家数据），中止。")
        sys.exit(1)
    log(f"存档已加载：NPC 数量 = {len(cache.npc_id_got)}")

    # 基准运行状态
    state = {
        "screens_done": 0,
        "screen_wall_times": [],
        "warmup_wall_times": [],
        "warmup_cleared": False,
        "aborted": False,
    }
    total_screens = args.screens + args.warmup_screens

    def benchmark_askfor_all(input_list, print_order=False):
        """
        askfor_all 的基准替身
        参数:
            input_list (list) -- 原函数的可选项列表（此处忽略）
            print_order (bool) -- 原函数的回显开关（此处忽略）
        返回值类型：str -- 恒为空字符串（InScenePanel 不使用其返回值）
        功能描述：推送上膛标记触发 GUI 侧本屏 flush，轮询等待渲染完成后返回，
                  达到目标屏数后修改面板 id 使 InScenePanel 的重绘循环退出
        """
        screen_before = perf_hook.get_screen_count()
        t0 = time.perf_counter()
        io_init.arm_input()
        deadline = time.time() + args.timeout_per_screen
        while perf_hook.get_screen_count() == screen_before:
            time.sleep(0.005)
            if time.time() > deadline:
                log(f"警告：第 {state['screens_done'] + 1} 屏等待渲染超时（{args.timeout_per_screen}s），中止。")
                state["aborted"] = True
                break
        wall = time.perf_counter() - t0
        state["screens_done"] += 1
        # 预热屏与正式测量屏分开记录
        if state["screens_done"] <= args.warmup_screens:
            state["warmup_wall_times"].append(wall)
            log(f"预热屏 {state['screens_done']}/{args.warmup_screens} 完成，flow等待GUI渲染 {wall * 1000:.1f} ms")
        else:
            state["screen_wall_times"].append(wall)
            measured = state["screens_done"] - args.warmup_screens
            if measured % 5 == 0 or measured == 1:
                log(f"屏 {measured}/{args.screens} 完成，flow等待GUI渲染 {wall * 1000:.1f} ms")
        # 预热结束后清屏一次，模拟"启动期预热后清屏进入正式界面"（--no-warmup-clear 时跳过）
        if args.warmup_screens and state["screens_done"] == args.warmup_screens and not state["warmup_cleared"]:
            state["warmup_cleared"] = True
            if not args.no_warmup_clear:
                io_init.clear_screen()
        if state["screens_done"] >= total_screens or state["aborted"]:
            # 让面板的 while-1 循环在下一次条件检查时退出
            cache.now_panel_id = -999
        return ""

    flow_handle.askfor_all = benchmark_askfor_all

    def benchmark_flow():
        """
        flow 线程主函数
        参数：无
        返回值类型：无
        功能描述：初始化样式后进入真实的主场景面板重绘循环，
                  结束后输出汇总 JSON 并退出整个进程（关闭 Tk 窗口）
        """
        exit_code = 0
        try:
            # 样式注册需经队列发给 GUI 线程
            io_init.init_style()
            # 产品化预热：与真实启动流程（game_init.init）相同的预热函数
            if args.prewarm:
                t_prewarm = time.perf_counter()
                io_init.warm_up_text_metrics()
                # 固定等待 GUI 线程处理完预热批（含 metrics_sync，实测约4秒），避免其成本混入首屏测量
                # 注：gui.metrics_sync 计时要到首个屏边界 flush 才进入会话汇总，无法轮询其出现
                time.sleep(8)
                log(f"产品化预热完成（flow侧入队+等待GUI共 {(time.perf_counter() - t_prewarm) * 1000:.1f}ms，GUI侧耗时见 gui.metrics_sync）")
            width = normal_config.config_normal.text_width
            log(f"开始基准：面板={args.panel}，{args.screens} 屏完整重绘，文本宽度 {width}")
            t_total = time.perf_counter()
            if args.panel == "map":
                # 查看地图界面：SeeMapPanel 的 while-1 循环同样以 now_panel_id 为退出条件
                cache.now_panel_id = constant.Panel.SEE_MAP
                from Script.UI.Panel import see_map_panel

                panel = see_map_panel.SeeMapPanel(width)
            else:
                cache.now_panel_id = constant.Panel.IN_SCENE
                from Script.UI.Panel import in_scene_panel

                panel = in_scene_panel.InScenePanel(width)
            panel.draw()
            total_wall = time.perf_counter() - t_total
            log(f"重绘循环结束：{state['screens_done']} 屏，总墙钟 {total_wall:.2f}s")

            # 汇总输出
            summary = {
                "screens_requested": args.screens,
                "screens_done": len(state["screen_wall_times"]),
                "warmup_screens": args.warmup_screens,
                "warmup_wall_ms": [round(t * 1000, 1) for t in state["warmup_wall_times"]],
                "aborted": state["aborted"],
                "npc_count": len(cache.npc_id_got),
                "total_wall_s": round(total_wall, 3),
                "screen_wall_ms": [round(t * 1000, 1) for t in state["screen_wall_times"]],
                "session": perf_hook.get_session_summary(),
                "jsonl_path": perf_hook.get_output_path(),
            }
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            summary_path = os.path.join(PROFILE_DIR, f"{args.summary_name}_{ts}.json")
            with open(summary_path, "w", encoding="utf-8") as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)

            # 控制台输出分类耗时 Top 表
            times = summary["session"]["times_ms"]
            log("=" * 60)
            log(f"分类耗时汇总（{state['screens_done']} 屏累计，按总耗时降序）：")
            for key, rec in sorted(times.items(), key=lambda kv: kv[1]["total_ms"], reverse=True)[:25]:
                log(f"  {key:<40} calls={rec['calls']:<7} total={rec['total_ms']:>10.1f}ms max={rec['max_ms']:>8.2f}ms")
            log(f"消息计数：{summary['session']['counts']}")
            wall_list = state["screen_wall_times"]
            if wall_list:
                sorted_wall = sorted(wall_list)
                log(
                    f"每屏flow等待GUI耗时: mean={sum(wall_list) / len(wall_list) * 1000:.1f}ms "
                    f"p50={sorted_wall[len(sorted_wall) // 2] * 1000:.1f}ms "
                    f"max={sorted_wall[-1] * 1000:.1f}ms"
                )
            log(f"每屏明细 JSONL: {summary['jsonl_path']}")
            log(f"会话汇总 JSON: {summary_path}")
            log("基准完成。")
        except Exception:
            log("基准执行异常：")
            traceback.print_exc()
            exit_code = 1
        finally:
            # 退出整个进程以关闭 Tk 窗口（主线程阻塞在 mainloop 中）
            os._exit(exit_code)

    # 主线程运行 Tk mainloop，flow 线程执行基准
    io_init.run(benchmark_flow)


if __name__ == "__main__":
    main()
