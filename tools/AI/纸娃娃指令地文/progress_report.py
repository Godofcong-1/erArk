# -*- coding: UTF-8 -*-
"""汇总一次纸娃娃地文工作流停下时每个指令走到了哪一步（只读 journal.jsonl，不改任何文件）

用法（仓库根目录）:
    .conda\\python.exe tools/AI/纸娃娃指令地文/progress_report.py <运行目录> [--args 参数.json]
运行目录：~/.claude/projects/<项目目录名>/<会话id>/subagents/workflows/<runId>
--args 传入启动时的参数文件，可以把一次都没开始的指令也列出来

journal.jsonl 每行一条记录：
    {"type": "started", "agentId": ..., "label": "写作:口交", "phase": "Write"}   子代理启动
    {"type": "result",  "agentId": ..., "result": {...}}                          子代理交卷（result 为结构化返回值）
同一个 agentId 只有 started 没有 result，就是停下时还在跑的那一步
"""
import argparse
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
parser = argparse.ArgumentParser()
parser.add_argument("run_dir")
parser.add_argument("--args", help="启动时的参数文件（含 instructions 列表）")
options = parser.parse_args()

STAGE_ORDER = ["写作", "续写", "评审", "修订"]

# 读 journal：agentId -> (指令名, 步骤)，以及交卷结果
started = {}
results = {}
with open(os.path.join(options.run_dir, "journal.jsonl"), encoding="utf-8", errors="replace") as f:
    for line in f:
        try:
            record = json.loads(line)
        except Exception:
            continue
        if record.get("type") == "started":
            stage, _, name = record.get("label", "").partition(":")
            started[record.get("agentId")] = (name, stage)
        elif record.get("type") == "result":
            result = record.get("result")
            if isinstance(result, str):
                try:
                    result = json.loads(result)
                except Exception:
                    pass
            results[record.get("agentId")] = result


def describe(stage: str, result) -> str:
    """把一步的交卷结果压成一个短状态"""
    if not isinstance(result, dict):
        return "已交卷（无结构化结果）"
    if stage in ("写作", "续写"):
        return f"校验{'通过' if result.get('check_passed') else '未通过'}，{result.get('line_count', '?')}条"
    if stage == "评审":
        return f"意见{len(result.get('issues', []))}条"
    if stage == "修订":
        return f"采纳{result.get('applied', '?')}条，校验{'通过' if result.get('check_passed') else '未通过'}"
    return "已交卷"


# 按指令汇总每一步的状态
table = {}
for agent_id, (name, stage) in started.items():
    status = describe(stage, results[agent_id]) if agent_id in results else "停下时进行中"
    table.setdefault(name, {})[stage] = status

order = list(table)
if options.args:
    with open(options.args, encoding="utf-8") as f:
        order = [item["name"] for item in json.load(f)["instructions"]]

finished, running, not_started = [], [], []
for name in order:
    stages = table.get(name)
    if not stages:
        not_started.append(name)
        continue
    cells = [f"{stage}：{stages[stage]}" for stage in STAGE_ORDER if stage in stages]
    print(f"{name}｜" + "｜".join(cells))
    if any(status == "停下时进行中" for status in stages.values()):
        running.append(name)
    elif "修订" in stages or ("评审" in stages and stages["评审"] == "意见0条"):
        finished.append(name)
    else:
        running.append(name)

print()
print(f"已走完全部步骤 {len(finished)} 个：{'、'.join(finished) or '无'}")
print(f"走到一半（停下时进行中或下一步未启动） {len(running)} 个：{'、'.join(running) or '无'}")
print(f"一次都没开始 {len(not_started)} 个：{'、'.join(not_started) or '无'}")
