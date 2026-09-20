# -*- coding: UTF-8 -*-
"""
静态检查系统 - 失败日志写入
负责将静态检查失败结果连同调试上下文与状态快照追加写入 static_check_error.log。

存储格式契约（与设计文档第6节一致）：
- 一个日志文件只服务一个游戏版本：文件首行为版本头，版本变化时现日志轮转为 .old（覆盖旧的 .old）后新开文件。
- 检查级去重：同一条检查（check_id）在一个版本的日志里只详写一次（记录其首个失败instance），
  由旁车状态文件 static_check_seen.json 持久化"已记录检查集合"，跨进程生效。
  刻意不以失败message参与去重——message常含随时间变化的数值，以其去重会在带错游玩时完全失效。
- 快照只转储新记录检查的涉事角色（见 snapshot.py），不做全量角色转储。
- 体积硬上限：日志超过 _MAX_LOG_BYTES 后本进程停止写入，只留一次说明行，作为防未知失效模式的最后一道防线。

本模块持有三项相互关联的进程运行态：_seen_check_ids缓存已记录检查，_log_cap_notice_written控制体积提示，
LOG_PATH/OLD_LOG_PATH/SEEN_STATE_PATH是一组联动的相对路径常量。同一进程内重复验证日志行为时，
必须同时重置前两个模块变量并成组改向三个路径常量，避免测试状态互相污染。
"""
import datetime
import json
import os
import traceback
from typing import List, Optional

from Script.Config import normal_config, game_config
from . import snapshot as snapshot_module
from .check_registry import CheckFailure, get_all_checks

# 日志文件路径：与error.log同一约定，使用相对于游戏进程工作目录（即仓库根目录）的相对路径
LOG_PATH = os.path.join("static_check_error.log")
# 版本轮转出的旧日志路径（只保留最近一份）
OLD_LOG_PATH = LOG_PATH + ".old"
# 旁车状态文件：记录当前日志服务的版本与已详写过的检查id集合，几KB量级
SEEN_STATE_PATH = os.path.join("static_check_seen.json")

# 日志文件首行版本头的固定前缀，轮转判断时解析
_VERSION_HEADER_PREFIX = "[静态检查日志] 游戏版本: "

# 日志文件体积硬上限：超过后本进程不再写入任何条目（只写一次说明行）
_MAX_LOG_BYTES: int = 50 * 1024 * 1024
_log_cap_notice_written: bool = False

# 进程内缓存的已记录检查id集合；None表示尚未初始化（首次写入时从旁车文件加载）
_seen_check_ids: Optional[set] = None


def _get_version_text() -> str:
    """
    参数:
        无
    返回值:
        str: 当前游戏版本号文本
    功能:
        从normal_config读取游戏版本号（字段名verson为游戏内既有拼写），读取失败时返回"未知"
    """
    return str(getattr(normal_config.config_normal, "verson", "未知"))


def _load_seen_state() -> set:
    """
    参数:
        无
    返回值:
        set: 旁车状态文件中记录的已详写检查id集合；文件缺失、损坏或版本不符时返回空集合
    功能:
        读取static_check_seen.json并校验其version字段与当前游戏版本一致；
        任何异常（文件不存在、JSON损坏、版本不符）都走"当作全新开始"路径，代价只是重记一遍，无害
    """
    try:
        with open(SEEN_STATE_PATH, "r", encoding="utf-8") as f:
            state = json.load(f)
        if state.get("version") == _get_version_text() and isinstance(state.get("seen"), list):
            return set(state["seen"])
    except Exception:
        pass
    return set()


def _save_seen_state(seen: set) -> None:
    """
    参数:
        seen (set): 当前版本已详写的检查id集合
    返回值:
        None
    功能:
        将当前版本号与已详写检查id集合写入旁车状态文件；写入失败时静默放弃（最多导致重启后重记一遍）
    """
    try:
        with open(SEEN_STATE_PATH, "w", encoding="utf-8") as f:
            json.dump({"version": _get_version_text(), "seen": sorted(seen)}, f, ensure_ascii=False)
    except Exception:
        pass


def _read_log_version() -> Optional[str]:
    """
    参数:
        无
    返回值:
        Optional[str]: 现有日志文件首行记录的版本号；文件不存在、首行不是版本头或读取失败时返回None
    功能:
        解析日志文件首行的版本头，供轮转判断使用
    """
    try:
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            first_line = f.readline().strip()
        if first_line.startswith(_VERSION_HEADER_PREFIX):
            return first_line[len(_VERSION_HEADER_PREFIX):]
    except Exception:
        pass
    return None


def _ensure_log_file() -> None:
    """
    参数:
        无
    返回值:
        None
    功能:
        保证日志文件存在且服务于当前游戏版本：
        - 文件不存在：新建并写入版本头；
        - 文件存在且首行版本与当前一致：直接沿用；
        - 版本不一致或首行损坏：现日志改名为.old（覆盖上一份.old）后新建。
        自我修复不做特判：一切异常形态统一走轮转重开路径，旧内容进.old不丢证据
    """
    version_text = _get_version_text()
    if os.path.exists(LOG_PATH):
        if _read_log_version() == version_text:
            return
        try:
            os.replace(LOG_PATH, OLD_LOG_PATH)
        except Exception:
            # 改名失败（如权限问题）时退回直接覆盖，保证新日志版本头正确
            pass
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        f.write(_VERSION_HEADER_PREFIX + version_text + "\n")


def _init_if_needed() -> None:
    """
    参数:
        无
    返回值:
        None
    功能:
        首次写入前的一次性初始化：先做日志文件版本轮转，再从旁车文件加载已记录检查集合。
        顺序不可颠倒——轮转后（版本变化）旁车文件的版本校验会失败、自然返回空集合，两者保持一致
    """
    global _seen_check_ids
    if _seen_check_ids is None:
        # 轮转失败会由门面吞掉异常，_seen_check_ids保持None并在下回合重试，这是有意的降级策略
        _ensure_log_file()
        _seen_check_ids = _load_seen_state()


def _build_recent_input_text(cache) -> str:
    """
    参数:
        cache: 当前游戏缓存对象
    返回值:
        str: 最近输入指令的可读文本
    功能:
        取cache.input_cache末尾最多10条原始输入，拼接为日志展示用文本
    """
    recent_inputs = list(cache.input_cache[-10:]) if getattr(cache, "input_cache", None) else []
    return str(recent_inputs)


def _build_recent_behavior_text(cache) -> str:
    """
    参数:
        cache: 当前游戏缓存对象
    返回值:
        str: 最近行为指令（id+中文名）的可读文本
    功能:
        遍历cache.pl_pre_behavior_instruce，将每个行为id翻译为中文名称（查不到则仅保留id），拼接为日志展示用文本；
        翻译逻辑与Script/Core/game_init.py中崩溃日志的写法保持一致，使用try/except兜底防止个别未知id导致异常
    """
    behavior_id_list = getattr(cache, "pl_pre_behavior_instruce", []) or []
    text_list = []
    for behavior_id in behavior_id_list:
        try:
            behavior_data = game_config.config_behavior[behavior_id]
            text_list.append(f"{behavior_id}({behavior_data.name})")
        except Exception:
            text_list.append(f"{behavior_id}(未知行为)")
    return "，".join(text_list)


def _build_involved_character_text(cache, involved_character_ids: List[int]) -> str:
    """
    参数:
        cache: 当前游戏缓存对象
        involved_character_ids (List[int]): 涉及的角色id列表
    返回值:
        str: "id(角色名)"形式拼接的可读文本
    功能:
        将涉及角色id列表转换为便于排查的可读文本，角色名查不到时仅展示id
    """
    text_list = []
    for character_id in involved_character_ids:
        try:
            character_name = cache.character_data[character_id].name
            text_list.append(f"{character_id}({character_name})")
        except Exception:
            text_list.append(f"{character_id}(未知角色)")
    return "，".join(text_list)


def _log_size_exceeded() -> bool:
    """
    参数:
        无
    返回值:
        bool: 日志文件是否已超过体积硬上限
    功能:
        检查static_check_error.log当前体积是否超过_MAX_LOG_BYTES；超过时保证只写入一次说明行，
        此后本进程内所有写入直接跳过，作为防止日志膨胀的最后一道防线
    """
    global _log_cap_notice_written
    try:
        if os.path.exists(LOG_PATH) and os.path.getsize(LOG_PATH) >= _MAX_LOG_BYTES:
            if not _log_cap_notice_written:
                _log_cap_notice_written = True
                with open(LOG_PATH, "a", encoding="utf-8") as f:
                    f.write(f"[静态检查] 日志已超过{_MAX_LOG_BYTES // (1024 * 1024)}MB体积上限，本进程停止写入。如需继续记录请清空或另存本文件后重启游戏\n")
            return True
    except Exception:
        pass
    return False


def _build_entry_header_lines(cache, now_text: str) -> List[str]:
    """
    参数:
        cache: 当前游戏缓存对象
        now_text (str): 本条记录的现实时间ISO文本
    返回值:
        List[str]: 条目头部各行（分隔线、时间与游戏状态、最近输入、最近行为指令）
    功能:
        构造日志条目的公共头部，供失败条目与修复条目共用
    """
    game_time_text = getattr(cache, "game_time", "未知")
    game_round_text = getattr(cache, "game_round", "未知")
    lines = []
    lines.append("=" * 80)
    lines.append(f"[静态检查] 现实时间: {now_text} | 游戏时间: {game_time_text} | 周目: {game_round_text} | 已注册检查项: {len(get_all_checks())}")
    lines.append(f"最近输入(input_cache 末尾10条): {_build_recent_input_text(cache)}")
    lines.append(f"最近行为指令(pl_pre_behavior_instruce, id+名称): {_build_recent_behavior_text(cache)}")
    return lines


def write_error_log(failures: List[CheckFailure], cache, context: dict = None) -> bool:
    """
    参数:
        failures (List[CheckFailure]): 待写入日志的静态检查失败列表，为空时不写入
        cache: 当前游戏缓存对象
        context (dict): 随日志一并写入的上下文包（context packet），默认为None时不输出上下文行
    返回值:
        bool: 本次是否真正向日志追加了新条目（供调用方决定是否向玩家绘制提示）
    功能:
        按检查级去重后，将"本版本首次失败"的检查连同现实时间、游戏时间、周目、最近输入、最近行为指令、
        上下文包与涉事角色快照，以追加方式写入static_check_error.log：
        - 每条检查只详写其首个失败instance；同一检查后续再失败（无论哪个角色触发）不再写入任何内容；
        - 快照只转储本条目新记录检查的涉事角色（并集，上限见snapshot.MAX_SNAPSHOT_CHARACTERS）；
        - 已详写检查集合持久化到旁车文件，游戏重启不重记；游戏版本变化时日志轮转、集合重置
    """
    if not failures:
        return False
    _init_if_needed()
    if _log_size_exceeded():
        return False

    # 检查级去重：只保留本版本尚未详写过的检查，每条检查取其首个失败instance
    new_failures = {}
    for failure in failures:
        if failure.check_id not in _seen_check_ids and failure.check_id not in new_failures:
            new_failures[failure.check_id] = failure
    if not new_failures:
        return False

    now_text = datetime.datetime.now().isoformat()
    lines = _build_entry_header_lines(cache, now_text)
    if context:
        try:
            context_text = json.dumps(context, ensure_ascii=False, default=repr)
        except Exception as e:
            context_text = f"<上下文包序列化失败: {e}>"
        lines.append(f"上下文包(context packet): {context_text}")
    lines.append(f"新记录失败检查 {len(new_failures)} 项（每检查只记录首个失败instance，本版本内不再重复记录）:")
    involved_ids = set()
    for failure in new_failures.values():
        involved_text = _build_involved_character_text(cache, failure.involved_character_ids)
        lines.append(f"  - [{failure.check_id}] {failure.check_name}: {failure.message} (涉及角色: {involved_text})")
        involved_ids.update(failure.involved_character_ids)
    lines.append("快照(仅涉事角色与玩家):")
    lines.append(snapshot_module.dump_snapshot_json(cache, involved_ids))

    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    _seen_check_ids.update(new_failures.keys())
    _save_seen_state(_seen_check_ids)
    return True


def write_repair_log(repair_records: List[dict], cache) -> None:
    """
    参数:
        repair_records (List[dict]): 修复记录列表，每条含check_id、target(修复对象描述)、field(字段路径)、
                                     old_value(修复前值)、new_value(修复后值)
        cache: 当前游戏缓存对象
    返回值:
        None
    功能:
        将载入存档时自动修复的操作留痕写入日志：逐条记录修复了什么、修复前后的值各是什么。
        修复条目不参与检查级去重（修复是一次性事件，每次实际发生都值得留痕）
    """
    if not repair_records:
        return
    _init_if_needed()
    if _log_size_exceeded():
        return
    now_text = datetime.datetime.now().isoformat()
    lines = _build_entry_header_lines(cache, now_text)
    lines.append(f"载入存档自动修复 {len(repair_records)} 项（旧值→新值均已留痕）:")
    for record in repair_records:
        lines.append(
            f"  * [{record.get('check_id', '?')}] {record.get('target', '?')} 字段={record.get('field', '?')} 旧值={record.get('old_value')!r} 新值={record.get('new_value')!r}"
        )
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def write_self_error_log(exc: Exception) -> None:
    """
    参数:
        exc (Exception): 静态检查器自身发生的异常对象
    返回值:
        None
    功能:
        当静态检查器自身运行出现异常（框架代码bug，而非某个检查项内部异常）时，
        以最简形式追加一条"检查器自身异常"记录到日志，携带完整traceback。
        日志写入本身失败时彻底吞掉，因此本函数在任何情况下都不抛出
    """
    try:
        now_text = datetime.datetime.now().isoformat()
        # 从异常对象本身取traceback，而非依赖"正处于except块中"这一调用环境假设
        if exc is not None:
            trace_text = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        else:
            trace_text = traceback.format_exc()
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write(f"[静态检查] {now_text} 检查器自身异常:\n")
            f.write(trace_text + "\n")
    except Exception:
        # 日志写入本身失败时彻底放弃，保证不会向上抛出
        pass
