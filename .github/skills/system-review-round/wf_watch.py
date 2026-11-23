# -*- coding: utf-8 -*-
"""
检查一次 Workflow 运行有没有停住（system-review-round 用，别的 Workflow 也能用）。

一次性检查（仓库根目录）：
    ./.conda/python.exe .claude/skills/system-review-round/wf_watch.py <运行目录> [--stale 10] [--dump 结果.json]
挂在 Monitor 上持续盯，只在某个代理状态变化时打一行，交卷数够了就退出：
    ./.conda/python.exe -u .claude/skills/system-review-round/wf_watch.py <运行目录> --watch 60 --expect 5 [--stale 10]

运行目录：~/.claude/projects/<项目目录名>/<会话id>/subagents/workflows/<runId>
（Workflow 启动时返回的 runId 就是 wf_xxx）

每个子代理判成一种状态：
- 已交卷：journal 里有它的 result 记录
- 等命令：它发出的某个工具调用超过阈值还没回结果，多半是测试或构建挂住，会顺带列出跑了很久的 python 进程
- 疑似停住：记录超过阈值没更新，也没有未回结果的工具调用
- 进行中：其余
判据与处理见 tools/Workflow编排.md「运行中：怎么判断停没停住」
"""
import argparse
import datetime
import glob
import json
import os
import re
import subprocess
import sys
import time

# 控制台默认 GBK，统一改成 UTF-8，免得中文乱码
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def load_lines(path):
    """
    读 jsonl，坏行（含正在写的半行）跳过
    参数：path (str) 文件路径
    返回：list[dict]
    """
    out = []
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    out.append(json.loads(line))
                except Exception:
                    pass
    except OSError:
        pass
    return out


def short(value, limit=150):
    """
    压成一行并截断
    参数：value 任意值；limit (int) 最长字符数
    返回：str
    """
    text = str(value).replace("\r", " ").replace("\n", " ")
    return text if len(text) <= limit else text[:limit] + "…"


def parse_ts(text):
    """
    解析记录里的 ISO 时间戳
    参数：text (str)
    返回：float|None 时间戳秒
    """
    if not text:
        return None
    try:
        return datetime.datetime.fromisoformat(str(text).replace("Z", "+00:00")).timestamp()
    except Exception:
        return None


def tool_result_text(block):
    """
    取 tool_result 块的文本
    参数：block (dict)
    返回：str
    """
    content = block.get("content")
    if isinstance(content, list):
        return " ".join(item.get("text", "") for item in content if isinstance(item, dict))
    return str(content)


def read_journal(run_dir):
    """
    读 journal，分出每个代理的标签与交卷记录
    参数：run_dir (str) 运行目录
    返回：tuple(dict 代理id→标签, dict 代理id→result 记录, list 全部记录)
    """
    labels, results = {}, {}
    entries = load_lines(os.path.join(run_dir, "journal.jsonl"))
    for entry in entries:
        agent_id = entry.get("agentId")
        if not agent_id:
            continue
        if entry.get("type") == "started":
            labels[agent_id] = entry.get("label") or agent_id
        elif entry.get("type") == "result":
            results[agent_id] = entry
    return labels, results, entries


def scan_agent(path, now):
    """
    读一个子代理的记录，找出未回结果的工具调用与最近几步
    参数：path (str) agent-*.jsonl；now (float) 当前时间戳
    返回：dict id / age_min 记录多久没更新 / lines 行数 / pending [(工具名, 入参摘要, 已等分钟)] / recent 最近几步
    """
    agent_id = os.path.basename(path)[len("agent-") : -len(".jsonl")]
    pending = {}
    recent = []
    lines = load_lines(path)
    for entry in lines:
        ts = parse_ts(entry.get("timestamp"))
        message = entry.get("message") or {}
        content = message.get("content")
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict):
                continue
            kind = block.get("type")
            if kind == "tool_use":
                brief = short(json.dumps(block.get("input"), ensure_ascii=False), 160)
                pending[block.get("id")] = (block.get("name"), brief, ts)
                recent.append("调用 " + str(block.get("name")) + " " + brief)
            elif kind == "tool_result":
                pending.pop(block.get("tool_use_id"), None)
                recent.append("结果 " + short(tool_result_text(block), 120))
            elif kind == "text" and message.get("role") == "assistant":
                recent.append("说 " + short(block.get("text"), 120))
    pending_list = [(name, brief, round((now - ts) / 60, 1) if ts else None) for name, brief, ts in pending.values()]
    try:
        age = (now - os.path.getmtime(path)) / 60
    except OSError:
        age = 0.0
    return {"id": agent_id, "age_min": round(age, 1), "lines": len(lines), "pending": pending_list, "recent": recent[-4:]}


def list_old_python(min_age_min):
    """
    列出已经跑了 min_age_min 分钟以上的 python 进程（Windows，借 PowerShell 查），用来找挂住的测试或构建
    参数：min_age_min (float)
    返回：list[str] 每个进程一行：pid、已跑分钟、命令行
    """
    script = (
        "[Console]::OutputEncoding=[Text.Encoding]::UTF8; "
        "Get-CimInstance Win32_Process | Where-Object { $_.Name -like 'python*' } | "
        "Select-Object ProcessId,CreationDate,CommandLine | ConvertTo-Json -Compress"
    )
    try:
        out = subprocess.run(["powershell", "-NoProfile", "-Command", script], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60).stdout
        data = json.loads(out) if out.strip() else []
    except Exception:
        return []
    if isinstance(data, dict):
        data = [data]
    rows = []
    now = time.time()
    for proc in data:
        created = str(proc.get("CreationDate"))
        # PowerShell 5.1 把时间写成 /Date(毫秒)/，7.x 写成 ISO 串
        match = re.search(r"\d{10,}", created)
        start = int(match.group(0)) / 1000 if match else parse_ts(created)
        if start is None:
            continue
        age = (now - start) / 60
        if age >= min_age_min:
            rows.append(f"pid {proc.get('ProcessId')} 已跑 {age:.0f} 分钟：{short(proc.get('CommandLine'), 160)}")
    return rows


def classify(info, results, stale):
    """
    判一个代理的状态
    参数：info (dict) scan_agent 的结果；results (dict) 已交卷的代理；stale (float) 阈值分钟
    返回：str 已交卷 / 等命令 / 疑似停住 / 进行中
    """
    if info["id"] in results:
        return "已交卷"
    if any(waited is not None and waited >= stale for _, _, waited in info["pending"]):
        return "等命令"
    if info["age_min"] >= stale:
        return "疑似停住"
    return "进行中"


def snapshot(run_dir, stale):
    """
    给整个运行目录拍一次快照
    参数：run_dir (str)；stale (float) 阈值分钟
    返回：tuple(dict 标签, dict 交卷记录, list[(代理id, 标签, 状态, info|None)])
    """
    now = time.time()
    labels, results, _ = read_journal(run_dir)
    rows = []
    seen = set()
    for path in sorted(glob.glob(os.path.join(run_dir, "agent-*.jsonl"))):
        info = scan_agent(path, now)
        seen.add(info["id"])
        rows.append((info["id"], labels.get(info["id"], info["id"]), classify(info, results, stale), info))
    # journal 里已开始、但还没写出记录文件的代理
    for agent_id, label in labels.items():
        if agent_id not in seen:
            rows.append((agent_id, label, "已交卷" if agent_id in results else "刚开始", None))
    return labels, results, rows


def report(run_dir, stale):
    """
    一次性检查：打印每个代理的状态、未回结果的调用与最近几步；有可疑的代理时列出跑了很久的 python 进程
    参数：run_dir (str)；stale (float) 阈值分钟
    返回：无
    """
    labels, results, rows = snapshot(run_dir, stale)
    print("现在", datetime.datetime.now().strftime("%H:%M:%S"), "；阈值", stale, "分钟；已开始", len(labels), "个代理，已交卷", len(results), "个")
    journal_path = os.path.join(run_dir, "journal.jsonl")
    if os.path.exists(journal_path):
        print("journal 最后更新", round((time.time() - os.path.getmtime(journal_path)) / 60, 1), "分钟前")
    need_procs = False
    for agent_id, label, state, info in rows:
        print(f"== {label}（{agent_id}）：{state}")
        if info is None:
            continue
        print(f"   记录 {info['lines']} 行，最后写入 {info['age_min']} 分钟前")
        for name, brief, waited in info["pending"]:
            print(f"   未回结果的调用：{name}，已等 {waited} 分钟：{brief}")
        for step in info["recent"]:
            print("   ", step)
        if state in ("等命令", "疑似停住"):
            need_procs = True
    if need_procs:
        print("== 跑了", stale, "分钟以上的 python 进程")
        for row in list_old_python(stale) or ["（没有）"]:
            print("  ", row)


def watch(run_dir, stale, interval, expect):
    """
    持续监视（给 Monitor 用）：某个代理状态变化时打一行，交卷数达到 expect 后退出
    参数：run_dir (str)；stale (float) 阈值分钟；interval (float) 轮询秒数；expect (int) 预期交卷数，0 为不自动退出
    返回：无
    """
    previous = {}
    while True:
        _, results, rows = snapshot(run_dir, stale)
        stamp = datetime.datetime.now().strftime("%H:%M")
        alarm = False
        for agent_id, label, state, info in rows:
            if previous.get(agent_id) == state:
                continue
            previous[agent_id] = state
            line = f"{stamp} {label}：{state}"
            if info is not None and state == "等命令" and info["pending"]:
                name, brief, waited = max(info["pending"], key=lambda p: p[2] or 0)
                line += f"（{name} 已等 {waited} 分钟：{short(brief, 100)}）"
                alarm = True
            elif info is not None and state == "疑似停住":
                line += f"（记录 {info['age_min']} 分钟没更新）"
                alarm = True
            print(line, flush=True)
        if alarm:
            for row in list_old_python(stale)[:5]:
                print(f"{stamp}   {row}", flush=True)
        if expect and len(results) >= expect:
            print(f"{stamp} 已交卷 {len(results)} 个，达到预期 {expect} 个，停止监视", flush=True)
            return
        time.sleep(interval)


def dump(run_dir, out_path):
    """
    把 journal 里的交卷结果写成 UTF-8 JSON，便于主代理逐条核对
    参数：run_dir (str)；out_path (str) 输出文件
    返回：无
    """
    labels, results, _ = read_journal(run_dir)
    data = [{"label": labels.get(agent_id, agent_id), "agentId": agent_id, "result": entry.get("result")} for agent_id, entry in results.items()]
    text = json.dumps(data, ensure_ascii=False, indent=2)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)
    print("已写", out_path, "：", len(data), "份结果")


def main():
    """入口：解析参数，按模式分派"""
    parser = argparse.ArgumentParser(description="检查 Workflow 运行有没有停住")
    parser.add_argument("run_dir", help="运行目录 subagents/workflows/wf_xxx")
    parser.add_argument("--stale", type=float, default=10.0, help="记录或工具调用多少分钟没动静算可疑，默认 10")
    parser.add_argument("--watch", type=float, default=0, help="持续监视的轮询间隔秒数；不给则只查一次")
    parser.add_argument("--expect", type=int, default=0, help="持续监视时，交卷数达到这个值就退出")
    parser.add_argument("--dump", default="", help="把 journal 里的交卷结果写到这个文件")
    args = parser.parse_args()
    if args.dump:
        dump(args.run_dir, args.dump)
    if args.watch > 0:
        watch(args.run_dir, args.stale, args.watch, args.expect)
    elif not args.dump:
        report(args.run_dir, args.stale)


if __name__ == "__main__":
    main()
