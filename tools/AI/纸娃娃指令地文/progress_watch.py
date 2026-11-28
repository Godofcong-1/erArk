# -*- coding: UTF-8 -*-
"""盯纸娃娃地文工作流的进度：每隔一段时间汇总一行（只在有变化时输出），子代理疑似停住时单独报一次

用法: .conda\\python.exe -u tools/AI/纸娃娃指令地文/progress_watch.py <运行目录> [--interval 300] [--stale 25]
运行目录：~/.claude/projects/<项目目录名>/<会话id>/subagents/workflows/<runId>
"""
import argparse
import json
import os
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
parser = argparse.ArgumentParser()
parser.add_argument("run_dir")
parser.add_argument("--interval", type=int, default=300)
parser.add_argument("--stale", type=float, default=25.0, help="子代理记录超过这么多分钟没更新就报疑似停住")
args = parser.parse_args()


def read_journal() -> tuple:
    """读 journal：返回 (agentId -> 标签, 已交卷的 agentId 集合)"""
    labels, done = {}, set()
    try:
        with open(os.path.join(args.run_dir, "journal.jsonl"), encoding="utf-8", errors="replace") as f:
            for line in f:
                try:
                    record = json.loads(line)
                except Exception:
                    continue
                if record.get("type") == "started":
                    labels[record.get("agentId")] = record.get("label", "")
                elif record.get("type") == "result":
                    done.add(record.get("agentId"))
    except OSError:
        pass
    return labels, done


last_summary = ""
reported_stale = set()
while True:
    labels, done = read_journal()
    count = {}
    running = []
    now = time.time()
    for agent_id, label in labels.items():
        stage = label.split(":")[0]
        if agent_id in done:
            count[stage] = count.get(stage, 0) + 1
            continue
        running.append(label)
        # 进行中的代理：记录文件太久没更新就报一次
        path = os.path.join(args.run_dir, f"agent-{agent_id}.jsonl")
        if os.path.exists(path) and (now - os.path.getmtime(path)) / 60 > args.stale and agent_id not in reported_stale:
            reported_stale.add(agent_id)
            print(f"{time.strftime('%H:%M')} 疑似停住：{label}（记录 {int((now - os.path.getmtime(path)) / 60)} 分钟没更新）", flush=True)
    summary = "，".join(f"{stage}交卷{n}" for stage, n in sorted(count.items())) + f"；进行中{len(running)}"
    if summary != last_summary:
        last_summary = summary
        print(f"{time.strftime('%H:%M')} {summary}", flush=True)
    time.sleep(args.interval)
