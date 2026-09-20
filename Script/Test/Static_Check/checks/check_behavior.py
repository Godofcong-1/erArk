# -*- coding: UTF-8 -*-
"""
静态检查系统 - 行为/时间/状态机/主循环完整性相关检查
覆盖角色行为(Behavior)、全局时钟(game_time/pre_game_time)、结算主循环状态标记(over_behavior_character等)相关的
21条不变式(BEHAV-01~BEHAV-22，不含已删除的BEHAV-13)。来源见规划文档final_invariants_behavior.md，钩子点为
Script/UI/Panel/in_scene_panel.py与Script/UI/Panel/in_scene_panel_web.py主循环重绘处、flow_handle.askfor_all()之前。

以下五条生命周期事实已烘焙进本文件全部检查，任何依赖它们的护栏都不得删除：
1. cache.over_behavior_character在结算开始时清空、结算结束后保留；钩子处可能是上一次结算的残留值，
   任何使用它的检查都必须容忍陈旧值。
2. Character.state的整数取值(constant.CharacterStatus)与行为配表cid是两套已经漂移的编号，
   任何"state必须等于/映射到行为cid"的断言一律不做。
3. 时停模式下玩家结算完即break、全局时间回退pl_duration分钟，NPC本轮完全未结算；
   玩家合法领先cache.game_time，NPC数据合法陈旧。
4. H中的NPC可以合法地持有已过期行为(handle_npc_ai.py的提前入集与character_behavior.py的H捷径都会让行为原样留存)。
5. 新开局到达钩子时没有任何结算跑过，因此任何"必须刚结算过"语义的断言都不成立。

执行顺序约束：BEHAV-07(字段类型)在语义上必须先于一切时间比较类检查；本文件中BEHAV-10/11/12/22各自复用
_behavior_type_ok()对同一角色重做一次同源判定，字段类型损坏时对该角色跳过判定(既不算失败也不算通过)，
避免把领域失败(类型损坏本身已由BEHAV-07单独报告)降级成时间比较抛异常、被框架记成"检查器自身异常"。
"""
import datetime
from typing import List

from Script.Core import cache_control
from Script.Config import game_config
from Script.Design import game_time
from ..check_registry import CheckFailure, register_check, make_failure


def _live_ids(cache) -> set:
    """
    参数:
        cache -- 全局缓存对象
    返回值:
        set -- 只遍历确实存在的角色id集合
    功能:
        计算0号玩家与cache.npc_id_got的并集，再与cache.character_data的键取交集，避免一个悬空id
        让整条检查降级成"检查器自身异常"；npc_id_got⊆character_data的存在性本身已由仓库现有的CORE-01覆盖，
        本域不重复报警
    """
    npc_id_got = getattr(cache, "npc_id_got", None) or set()
    character_data = getattr(cache, "character_data", None) or {}
    return ({0} | set(npc_id_got)) & set(character_data)


def _end(chara) -> datetime.datetime:
    """
    参数:
        chara -- 角色对象
    返回值:
        datetime.datetime -- 行为结束时间
    功能:
        与生产代码(character_behavior.py计算end_time处)同源地计算行为结束时间，必须调用
        game_time.get_sub_date而不能用datetime.timedelta近似——get_sub_date会把1/2月钳到3月、
        4/5钳到6月……用timedelta近似会在跨季当天把合法行为误判成"早已过期"
    """
    return game_time.get_sub_date(minute=chara.behavior.duration, old_date=chara.behavior.start_time)


def _behavior_type_ok(chara) -> bool:
    """
    参数:
        chara -- 角色对象
    返回值:
        bool -- behavior核心字段类型是否合法(判定逻辑与BEHAV-01的字段类型检查同源)
    功能:
        供BEHAV-10/11/12/22在字段类型损坏时跳过该角色的时间比较，避免抛异常被框架降级为"检查器自身异常"；
        type(...)is int而非isinstance，因为isinstance(True, int)为真，布尔值不应被当作合法分钟数
    """
    try:
        behavior = chara.behavior
        return (
            isinstance(behavior.behavior_id, str)
            and type(behavior.start_time) is datetime.datetime
            and behavior.start_time.tzinfo is None
            and type(behavior.duration) is int
        )
    except Exception:
        return False


@register_check("BEHAV-01", "角色字典键与角色自身cid一致")
def check_character_dict_key_matches_cid() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure] -- 失败记录列表
    功能:
        校验cache.character_data的字典键与角色对象自身的cid一致。调度器按0与npc_id_got的id直接索引
        character_data，字典键与角色对象自身cid分裂会让一切按id定位的结算写错角色；旧存档载入流程专门跑
        fix_wrong_character修正这类编号错误，说明这是真实发生过的缺陷
    """
    cache = cache_control.cache
    character_data = getattr(cache, "character_data", None) or {}
    npc_id_got = getattr(cache, "npc_id_got", None) or set()
    failures = []
    for cid in _live_ids(cache):
        chara = character_data.get(cid)
        if chara is None:
            continue
        if getattr(chara, "cid", None) == cid:
            continue
        failures.append(
            make_failure(
                "BEHAV-01",
                "角色字典键与角色自身cid一致",
                f"character_data字典键cid={cid}对应的角色对象自身cid={getattr(chara, 'cid', None)!r}"
                f"(name={getattr(chara, 'name', '?')!r})，字典键与角色对象分裂会让按id定位的结算写错角色；"
                f"character_data键(前20个)={sorted(character_data.keys())[:20]}，npc_id_got(前20个)={sorted(npc_id_got)[:20]}",
                [cid],
            )
        )
    return failures


@register_check("BEHAV-02", "全局时钟健全性")
def check_global_clock_sanity() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure] -- 失败记录列表
    功能:
        校验cache.game_time/cache.pre_game_time都是已初始化的朴素datetime且只保留到分钟。三个写入源都不产生
        秒/微秒/时区，哨兵0001-01-01只可能来自旧存档缺字段被补默认值——那正是要抓的迁移缺陷；秒/微秒/时区那半
        是构造性真值(无写入通道)，保留是因为代价为零且能识别外部注入/反序列化损坏
    """
    cache = cache_control.cache
    game_t = getattr(cache, "game_time", None)
    pre_t = getattr(cache, "pre_game_time", None)
    failures = []
    for label, t in (("game_time", game_t), ("pre_game_time", pre_t)):
        ok = (
            type(t) is datetime.datetime
            and t != datetime.datetime(1, 1, 1)
            and t.second == 0
            and t.microsecond == 0
            and t.tzinfo is None
        )
        if ok:
            continue
        failures.append(
            make_failure(
                "BEHAV-02",
                "全局时钟健全性",
                f"cache.{label}={t!r}不是合法的已初始化朴素datetime(要求非哨兵0001-01-01、秒/微秒为0、无时区)；"
                f"game_time={game_t!r}, pre_game_time={pre_t!r}, now_panel_id={getattr(cache, 'now_panel_id', None)}",
                [],
            )
        )
    return failures


@register_check("BEHAV-03", "世界月份只能是四季月")
def check_world_month_is_seasonal() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure] -- 失败记录列表
    功能:
        校验cache.game_time与cache.pre_game_time的月份都属于四季月{3,6,9,12}。全年被折叠为四个月，
        get_sub_date会显式归并其他月份；出现第五种月份不只是数据脏，get_date_text()对第五种月份没有else分支，
        下一次绘制就会UnboundLocalError崩溃。已知唯一的合法绕过是调试面板直接replace月份——这正是本条要抓的
        非正常状态，不为它加豁免
    """
    cache = cache_control.cache
    game_t = getattr(cache, "game_time", None)
    pre_t = getattr(cache, "pre_game_time", None)
    ok = (
        isinstance(game_t, datetime.datetime)
        and game_t.month in {3, 6, 9, 12}
        and isinstance(pre_t, datetime.datetime)
        and pre_t.month in {3, 6, 9, 12}
    )
    if ok:
        return []
    return [
        make_failure(
            "BEHAV-03",
            "世界月份只能是四季月",
            f"game_time={game_t!r}(月={getattr(game_t, 'month', None)})或pre_game_time={pre_t!r}"
            f"(月={getattr(pre_t, 'month', None)})不属于四季月{{3,6,9,12}}；get_date_text()对第五种月份"
            f"没有else分支，下一次绘制会UnboundLocalError崩溃",
            [],
        )
    ]


@register_check("BEHAV-04", "上一循环时间不得晚于当前时间")
def check_pre_game_time_not_after_game_time() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure] -- 失败记录列表
    功能:
        校验cache.pre_game_time不晚于cache.game_time。pre_game_time只在初始化与每日刷新被赋成当时的
        cache.game_time，是单调追赶的锚点；时停的回退量与本回合推进量相抵，净变化为0。本条实际是时钟倒流探测器，
        真实可达路径是"等待至交互对象行动结束"的add_time未做下限钳制，对象行动已结束时为负会让全局时钟真的倒退
    """
    cache = cache_control.cache
    game_t = getattr(cache, "game_time", None)
    pre_t = getattr(cache, "pre_game_time", None)
    try:
        ok = pre_t <= game_t
    except Exception:
        # 类型损坏由BEHAV-02负责，本条只做时钟倒流探测，比较本身失败时跳过避免"检查器自身异常"
        return []
    if ok:
        return []
    character_data = getattr(cache, "character_data", None) or {}
    player = character_data.get(0)
    duration0 = getattr(getattr(player, "behavior", None), "duration", None)
    return [
        make_failure(
            "BEHAV-04",
            "上一循环时间不得晚于当前时间",
            f"pre_game_time={pre_t!r}晚于game_time={game_t!r}(差值={game_t - pre_t})，时钟疑似倒流；"
            f"time_stop_mode={getattr(cache, 'time_stop_mode', None)}, 0号角色behavior.duration={duration0!r}；"
            f"疑似命中'等待至交互对象行动结束'路径的add_time未做下限钳制导致全局时钟倒退",
            [],
        )
    ]


@register_check("BEHAV-05", "跨日刷新已经完成")
def check_daily_refresh_completed() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure] -- 失败记录列表
    功能:
        校验若game_time与pre_game_time的日期不同，说明主循环的跨日刷新(比较日期并调用每日刷新，把
        pre_game_time推到当前)钩子处仍未完成，今日事件记录/每日计数器等都没清；用date()而非.day是本条要抓的
        缺口(生产代码只比较.day，月/年不同但日号相同会被生产代码放过)。时停整条跳过：时停下玩家结算完即提前
        break，走不到每日刷新那一步。定为warning：这类状态会连续告警至多一个游戏日后自愈
    """
    cache = cache_control.cache
    if getattr(cache, "time_stop_mode", False):
        return []
    game_t = getattr(cache, "game_time", None)
    pre_t = getattr(cache, "pre_game_time", None)
    try:
        ok = game_t.date() == pre_t.date()
    except Exception:
        return []
    if ok:
        return []
    character_data = getattr(cache, "character_data", None) or {}
    player = character_data.get(0)
    behavior0 = getattr(player, "behavior", None)
    today_event = getattr(cache, "today_taiggered_event_record", None) or set()
    return [
        make_failure(
            "BEHAV-05",
            "跨日刷新已经完成",
            f"[warning] game_time={game_t!r}与pre_game_time={pre_t!r}日期不同，跨日刷新(今日事件记录/每日计数器)"
            f"疑似尚未执行；0号角色behavior.behavior_id={getattr(behavior0, 'behavior_id', None)!r}, "
            f"duration={getattr(behavior0, 'duration', None)!r}, today_taiggered_event_record长度={len(today_event)}",
            [],
        )
    ]


@register_check("BEHAV-06", "更新流程嵌套深度必须归零")
def check_update_flow_depth_zero() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure] -- 失败记录列表
    功能:
        校验cache.game_update_flow_running恒为0。game_update_flow用该计数器限制递归并在finally恢复，
        钩子只能从顶层面板派发到达，不存在从结算内部重入场景面板的路径，因此语义值恒为0；非0直接暴露
        "结算过程中重绘了主面板"这类重入错误。上限本身是空转(达到上限会提前return、finally保证恢复)，
        因此收紧为严格==0而非区间
    """
    cache = cache_control.cache
    v = getattr(cache, "game_update_flow_running", None)
    if type(v) is int and v == 0:
        return []
    character_data = getattr(cache, "character_data", None) or {}
    player = character_data.get(0)
    behavior0 = getattr(player, "behavior", None)
    return [
        make_failure(
            "BEHAV-06",
            "更新流程嵌套深度必须归零",
            f"cache.game_update_flow_running={v!r}不等于0，暴露'结算过程中重绘主面板'一类重入错误；"
            f"now_panel_id={getattr(cache, 'now_panel_id', None)}, game_time={getattr(cache, 'game_time', None)}, "
            f"0号角色behavior.behavior_id={getattr(behavior0, 'behavior_id', None)!r}",
            [],
        )
    ]


@register_check("BEHAV-07", "行为核心字段类型正确")
def check_behavior_core_field_types() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure] -- 失败记录列表
    功能:
        校验每个被调度角色的behavior有字符串id、朴素datetime起时、非布尔整数分钟数。旧存档迁移直接复用整个
        behavior对象，老存档里behavior_id可能还是int，类型损坏必须先于时间运算被识别。本条失败时，
        BEHAV-10/11/12/22对同一角色跳过判定，避免时间比较抛异常被框架记成"检查器自身异常"而丢掉本该有的诊断
    """
    cache = cache_control.cache
    character_data = getattr(cache, "character_data", None) or {}
    failures = []
    for cid in _live_ids(cache):
        chara = character_data.get(cid)
        if chara is None or _behavior_type_ok(chara):
            continue
        behavior = getattr(chara, "behavior", None)
        failures.append(
            make_failure(
                "BEHAV-07",
                "行为核心字段类型正确",
                f"角色cid={cid}(name={getattr(chara, 'name', '?')!r})的behavior字段类型损坏："
                f"behavior类型={type(behavior).__name__}, behavior_id={getattr(behavior, 'behavior_id', None)!r}, "
                f"start_time={getattr(behavior, 'start_time', None)!r}, duration={getattr(behavior, 'duration', None)!r}；"
                f"类型损坏必须先于时间比较类检查被识别，BEHAV-10/11/12/22对该角色本轮跳过判定",
                [cid],
            )
        )
    return failures


@register_check("BEHAV-08", "当前行为id必须已注册")
def check_behavior_id_registered() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure] -- 失败记录列表
    功能:
        校验每个被调度角色的behavior_id都能在game_config.config_behavior(键为en_name)中查到。未注册id会让
        生产代码的直接下标必KeyError。旧存档携带已删除行为id会触发——那属于应当迁移处理的真问题，不加豁免。
        若config_behavior配表本身未加载(空)，视为独立跑本模块之类的场景，降级为跳过本条
    """
    cache = cache_control.cache
    config_behavior = getattr(game_config, "config_behavior", None)
    if not config_behavior:
        return []
    character_data = getattr(cache, "character_data", None) or {}
    failures = []
    for cid in _live_ids(cache):
        chara = character_data.get(cid)
        if chara is None:
            continue
        behavior = getattr(chara, "behavior", None)
        behavior_id = getattr(behavior, "behavior_id", None)
        if behavior_id in config_behavior:
            continue
        failures.append(
            make_failure(
                "BEHAV-08",
                "当前行为id必须已注册",
                f"角色cid={cid}(name={getattr(chara, 'name', '?')!r})的behavior.behavior_id={behavior_id!r}"
                f"未在game_config.config_behavior中注册，直接下标会KeyError；state={getattr(chara, 'state', None)!r}, "
                f"last_behavior_id_list={getattr(chara, 'last_behavior_id_list', None)!r}",
                [cid],
            )
        )
    return failures


@register_check("BEHAV-09", "运行中行为时长为非负整数")
def check_behavior_duration_non_negative_int() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure] -- 失败记录列表
    功能:
        校验每个被调度角色的behavior.duration是非负整数。负时长会让结束时间早于开始时间，负值源真实存在且
        未被钳制(助理同居睡眠duration = min_to_wake_time - 10没有下限)。不设上界：1440是经验值而非程序约束，
        睡眠时长由运行时算出；0是合法值(Behavior()默认、H中add_time==0的分支)
    """
    cache = cache_control.cache
    character_data = getattr(cache, "character_data", None) or {}
    failures = []
    for cid in _live_ids(cache):
        chara = character_data.get(cid)
        if chara is None:
            continue
        behavior = getattr(chara, "behavior", None)
        duration = getattr(behavior, "duration", None)
        if type(duration) is int and duration >= 0:
            continue
        wake_time = getattr(getattr(chara, "action_info", None), "wake_time", None)
        failures.append(
            make_failure(
                "BEHAV-09",
                "运行中行为时长为非负整数",
                f"角色cid={cid}(name={getattr(chara, 'name', '?')!r})的behavior.duration={duration!r}不是非负整数"
                f"(不设上界)；behavior_id={getattr(behavior, 'behavior_id', None)!r}, "
                f"start_time={getattr(behavior, 'start_time', None)!r}, action_info.wake_time={wake_time!r}",
                [cid],
            )
        )
    return failures


@register_check("BEHAV-10", "活动角色的行为起时不得是哨兵")
def check_behavior_start_time_not_sentinel() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure] -- 失败记录列表
    功能:
        校验每个被调度角色的behavior.start_time不是哨兵0001-01-01。主循环在每个角色处理开头就会把哨兵修成
        玩家起时，钩子处仍见哨兵即意味着该角色被跳过。新开局不会误伤：角色初始化与新上线访客都会显式写入起时。
        字段类型损坏(BEHAV-07已报告)的角色本条跳过判定，避免时间比较异常
    """
    cache = cache_control.cache
    character_data = getattr(cache, "character_data", None) or {}
    sentinel = datetime.datetime(1, 1, 1)
    over_behavior_character = getattr(cache, "over_behavior_character", None) or set()
    failures = []
    for cid in _live_ids(cache):
        chara = character_data.get(cid)
        if chara is None or not _behavior_type_ok(chara):
            continue
        behavior = chara.behavior
        if behavior.start_time != sentinel:
            continue
        failures.append(
            make_failure(
                "BEHAV-10",
                "活动角色的行为起时不得是哨兵",
                f"角色cid={cid}(name={getattr(chara, 'name', '?')!r})的behavior.start_time仍是哨兵0001-01-01，"
                f"说明该角色被主循环跳过未处理；behavior_id={behavior.behavior_id!r}, "
                f"game_time={getattr(cache, 'game_time', None)!r}, cid in over_behavior_character={cid in over_behavior_character}",
                [cid],
            )
        )
    return failures


@register_check("BEHAV-11", "行为起时不得晚于游戏时间")
def check_behavior_start_time_not_future() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure] -- 失败记录列表
    功能:
        校验每个被调度角色的behavior.start_time不晚于cache.game_time。judge_character_status_time_over()
        开头会把未来的start_time无条件钳到当前时间，钩子处出现"起时在未来"意味着某条路径绕过了主循环。
        时停模式下整条跳过(不能只跳过玩家)：装袋释放/投监两条路径会在时停期间把NPC的start_time写成回退前的
        推进后时刻，随后主循环回退全局时钟，该NPC合法领先
    """
    cache = cache_control.cache
    if getattr(cache, "time_stop_mode", False):
        return []
    character_data = getattr(cache, "character_data", None) or {}
    game_t = getattr(cache, "game_time", None)
    over_behavior_character = getattr(cache, "over_behavior_character", None) or set()
    failures = []
    for cid in _live_ids(cache):
        chara = character_data.get(cid)
        if chara is None or not _behavior_type_ok(chara):
            continue
        behavior = chara.behavior
        try:
            ok = behavior.start_time <= game_t
        except Exception:
            continue
        if ok:
            continue
        failures.append(
            make_failure(
                "BEHAV-11",
                "行为起时不得晚于游戏时间",
                f"角色cid={cid}(name={getattr(chara, 'name', '?')!r})的behavior.start_time={behavior.start_time!r}"
                f"晚于cache.game_time={game_t!r}；behavior_id={behavior.behavior_id!r}, duration={behavior.duration!r}, "
                f"time_stop_mode={getattr(cache, 'time_stop_mode', None)}, cid in over_behavior_character={cid in over_behavior_character}",
                [cid],
            )
        )
    return failures


@register_check("BEHAV-12", "不得残留已过期的行为")
def check_no_stale_expired_behavior() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure] -- 失败记录列表
    功能:
        校验非H、duration>0的被调度角色，其行为结束时间END()不早于cache.game_time。主循环靠
        "结束时间已到就重跑一次"推进，钩子处不该再有结束时间早于当前时间的角色。必须用END()(get_sub_date)，
        不能用timedelta近似，跨季当天生产代码会把月份钳位、timedelta近似会稳定误报。非严格>=且不排除玩家：
        新开局全体角色是Behavior()默认值(duration 0)，部分路径会让玩家带着duration=5、
        start_time==game_time-5走到钩子，此时END==game_time恰好是合法边界。H中角色豁免、时停整条跳过；
        duration<=0被过滤：完成分支会把behavior重置为duration=0，属于合法终态
    """
    cache = cache_control.cache
    if getattr(cache, "time_stop_mode", False):
        return []
    character_data = getattr(cache, "character_data", None) or {}
    game_t = getattr(cache, "game_time", None)
    group_sex_mode = getattr(cache, "group_sex_mode", None)
    failures = []
    for cid in _live_ids(cache):
        chara = character_data.get(cid)
        if chara is None or not _behavior_type_ok(chara):
            continue
        sp_flag = getattr(chara, "sp_flag", None)
        if getattr(sp_flag, "is_h", False):
            continue
        behavior = chara.behavior
        if behavior.duration <= 0:
            continue
        try:
            end_time = _end(chara)
            ok = end_time >= game_t
        except Exception:
            continue
        if ok:
            continue
        failures.append(
            make_failure(
                "BEHAV-12",
                "不得残留已过期的行为",
                f"角色cid={cid}(name={getattr(chara, 'name', '?')!r})的行为已过期未被结算：behavior_id={behavior.behavior_id!r}, "
                f"start_time={behavior.start_time!r}, duration={behavior.duration!r}, END={end_time!r} < game_time={game_t!r}；"
                f"is_h={getattr(sp_flag, 'is_h', None)}, unconscious_h={getattr(sp_flag, 'unconscious_h', None)}, "
                f"time_stop_mode={getattr(cache, 'time_stop_mode', None)}, group_sex_mode={group_sex_mode}, "
                f"target_character_id={getattr(chara, 'target_character_id', None)}",
                [cid],
            )
        )
    return failures


# BEHAV-13（已删除，2026-08-31）：曾断言"behavior_id为share_blankly、非H的角色，state必须落在
# (0, 'share_blankly')两个空闲哨兵值之内"。用户裁定该断言结构性过严：生产代码合法存在的一阶段等待过渡——
# behavior已经重置为share_blankly、但state尚未同步到空闲哨兵值——会被误报为异常，而这只是同一次结算内
# 两个字段先后落地的正常中间态，不是脱节故障。不做收窄，直接删除。


@register_check("BEHAV-14", "移动行为必须带着可执行的路径")
def check_move_behavior_has_executable_path() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure] -- 失败记录列表
    功能:
        校验behavior_id为move的角色带着可执行的路径快照。玩家指令记录会无保护地取
        move_src[-1]/move_target[-1]，末项为"0"时还取[-2]，空列表直接IndexError；正常寻路只在
        move_time>0时提交移动，零时长空路径属于非法快照。move_src只对玩家(cid==0)要求：NPC通用移动只写
        move_target/move_final_target，消费move_src的函数只对0号调用。不加state白名单：
        judge_same_position_npc_follow提交move时完全不写state，跟随者会带着state==0通过钩子。
        duration>0对H角色豁免：寻路失败时非H角色会被重置后重跑，H角色可能被H捷径保留
    """
    cache = cache_control.cache
    character_data = getattr(cache, "character_data", None) or {}
    failures = []
    for cid in _live_ids(cache):
        chara = character_data.get(cid)
        if chara is None:
            continue
        behavior = getattr(chara, "behavior", None)
        if getattr(behavior, "behavior_id", None) != "move":
            continue
        sp_flag = getattr(chara, "sp_flag", None)
        is_h = getattr(sp_flag, "is_h", False)
        duration = getattr(behavior, "duration", None)
        move_target = getattr(behavior, "move_target", None)
        move_src = getattr(behavior, "move_src", None)
        problems = []
        target_ok = isinstance(move_target, list) and len(move_target) >= 1 and all(isinstance(x, str) for x in move_target)
        if not target_ok:
            problems.append(f"move_target非法: {move_target!r}")
        if not (is_h or (type(duration) is int and duration > 0)):
            problems.append(f"非H角色但duration不为正: duration={duration!r}")
        if target_ok and move_target[-1] == "0" and len(move_target) < 2:
            problems.append(f"move_target末项为哨兵'0'且长度不足2，取[-2]会IndexError: move_target={move_target!r}")
        if cid == 0:
            src_ok = isinstance(move_src, list) and len(move_src) >= 1
            if not src_ok:
                problems.append(f"玩家move_src非法: {move_src!r}")
            elif move_src[-1] == "0" and len(move_src) < 2:
                problems.append(f"玩家move_src末项为哨兵'0'且长度不足2: move_src={move_src!r}")
        if not problems:
            continue
        failures.append(
            make_failure(
                "BEHAV-14",
                "移动行为必须带着可执行的路径",
                f"角色cid={cid}(name={getattr(chara, 'name', '?')!r})的move行为快照非法：{'; '.join(problems)}；"
                f"position={getattr(chara, 'position', None)!r}, move_final_target={getattr(behavior, 'move_final_target', None)!r}, "
                f"duration={duration!r}, state={getattr(chara, 'state', None)!r}, is_follow={getattr(sp_flag, 'is_follow', None)!r}",
                [cid],
            )
        )
    return failures


@register_check("BEHAV-15", '"谁在跟我互动"的记录必须指向真实角色')
def check_interacting_character_end_info_valid() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure] -- 失败记录列表
    功能:
        校验每个角色的action_info.interacting_character_end_info[0]（结算交互行为时写进对方的"发起方id"）
        要么是哨兵-1，要么指向character_data中真实存在的角色。旧存档id重映射会让这个字段失效，报出的悬空id
        就是迁移缺陷信号，属于期望捕获，不加豁免。与CORE-02不重复：CORE-02查的是target_character_id
    """
    cache = cache_control.cache
    character_data = getattr(cache, "character_data", None) or {}
    failures = []
    for cid in _live_ids(cache):
        chara = character_data.get(cid)
        if chara is None:
            continue
        action_info = getattr(chara, "action_info", None)
        info = getattr(action_info, "interacting_character_end_info", None)
        if not (isinstance(info, (list, tuple)) and len(info) >= 1):
            continue
        other_id = info[0]
        if other_id == -1 or other_id in character_data:
            continue
        failures.append(
            make_failure(
                "BEHAV-15",
                '"谁在跟我互动"的记录必须指向真实角色',
                f"角色cid={cid}(name={getattr(chara, 'name', '?')!r})的action_info.interacting_character_end_info="
                f"{info!r}指向的角色id={other_id!r}既不是哨兵-1也不在character_data中；"
                f"game_time={getattr(cache, 'game_time', None)!r}, character_data键(前20个)={sorted(character_data.keys())[:20]}",
                [cid],
            )
        )
    return failures


@register_check("BEHAV-16", "生效中的身体道具不得已过期")
def check_active_body_item_not_expired() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure] -- 失败记录列表
    功能:
        校验h_state.body_item中"生效中(item[1]为真)"的道具，其结束时间item[2]要么为None要么晚于
        cache.game_time。每个参与结算的角色每轮都会跑一次持续状态结算，H中结算全部部位、非H只结算8号
        (持续性利尿剂)与9号(安眠药)，结束时间已到(相等也算到期)的置为失效；钩子处还留着"生效中+结束时间≤当前
        时间"说明该角色本轮没被结算到。非H时必须收窄到8/9，否则会把"H中挂上、退出H后自然留存"的道具误报成脏数据。
        时停模式下只查玩家：NPC本轮完全未结算持续状态。比较用严格>：生产用judge_date_big_or_small判到期，
        相等返回2(真)，即item[2]<=game_time才算过期
    """
    cache = cache_control.cache
    character_data = getattr(cache, "character_data", None) or {}
    time_stop = getattr(cache, "time_stop_mode", False)
    game_t = getattr(cache, "game_time", None)
    failures = []
    for cid in _live_ids(cache):
        if time_stop and cid != 0:
            continue
        chara = character_data.get(cid)
        if chara is None:
            continue
        h_state = getattr(chara, "h_state", None)
        body_item = getattr(h_state, "body_item", None)
        if not isinstance(body_item, dict):
            continue
        sp_flag = getattr(chara, "sp_flag", None)
        is_h = getattr(sp_flag, "is_h", False)
        indices = range(len(body_item)) if is_h else (8, 9)
        for i in indices:
            if i not in body_item:
                continue
            item = body_item[i]
            try:
                item_name, active, end_time = item[0], item[1], item[2]
            except Exception:
                continue
            if not active:
                continue
            if end_time is None or end_time > game_t:
                continue
            failures.append(
                make_failure(
                    "BEHAV-16",
                    "生效中的身体道具不得已过期",
                    f"角色cid={cid}(name={getattr(chara, 'name', '?')!r})部位{i}({item_name!r})生效中(active=True)"
                    f"但结束时间{end_time!r}已<=当前game_time={game_t!r}，说明该角色本轮未被结算到；"
                    f"is_h={is_h}, unconscious_h={getattr(sp_flag, 'unconscious_h', None)}, time_stop_mode={time_stop}",
                    [cid],
                )
            )
    return failures


@register_check("BEHAV-17", "二段行为取值与待结算id合法")
def check_second_behavior_values_and_pending_ids() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure] -- 失败记录列表
    功能:
        校验second_behavior(二段行为id→0/1触发标记字典)的取值只能是0或1的int，以及
        must_settle_second_behavior_id_list/must_show_second_behavior_id_list两个待处理id列表中的每个id都在
        game_config.config_behavior_effect_data中——must_settle_check()与must_show_talk_check()都会无保护地
        下标该配表，键错即KeyError。不要求second_behavior的键都在效果配表里(普通路径对未知键是continue)；
        不要求待处理id必须同时存在于second_behavior(两个消费函数键不存在时也会直接结算)；
        不要求钩子处所有值都为0(可以在结算之外置1，残留的1是合法中间态)。只查取值类型，不查键类型：
        旧存档可能带int键。配表未加载时，待结算id合法性部分降级为跳过
    """
    cache = cache_control.cache
    character_data = getattr(cache, "character_data", None) or {}
    config_effect = getattr(game_config, "config_behavior_effect_data", None)
    failures = []
    for cid in _live_ids(cache):
        chara = character_data.get(cid)
        if chara is None:
            continue
        second_behavior = getattr(chara, "second_behavior", None) or {}
        try:
            values = list(second_behavior.values())
        except Exception:
            values = []
        must_settle = getattr(chara, "must_settle_second_behavior_id_list", None) or []
        must_show = getattr(chara, "must_show_second_behavior_id_list", None) or []
        behavior_id = getattr(getattr(chara, "behavior", None), "behavior_id", None)
        is_h = getattr(getattr(chara, "sp_flag", None), "is_h", None)
        for v in values:
            if type(v) is int and v in (0, 1):
                continue
            failures.append(
                make_failure(
                    "BEHAV-17",
                    "二段行为取值与待结算id合法",
                    f"角色cid={cid}(name={getattr(chara, 'name', '?')!r})的second_behavior存在非法取值v={v!r}"
                    f"(type={type(v).__name__})，要求type是int且取值只能是0或1；"
                    f"must_settle_second_behavior_id_list={must_settle!r}, must_show_second_behavior_id_list={must_show!r}, "
                    f"behavior_id={behavior_id!r}, is_h={is_h}",
                    [cid],
                )
            )
        if not config_effect:
            continue  # 效果配表未加载，降级为跳过待结算id合法性部分
        for bid in list(must_settle) + list(must_show):
            if bid in config_effect:
                continue
            failures.append(
                make_failure(
                    "BEHAV-17",
                    "二段行为取值与待结算id合法",
                    f"角色cid={cid}(name={getattr(chara, 'name', '?')!r})的待处理二段行为id={bid!r}不在"
                    f"game_config.config_behavior_effect_data中，must_settle_check()/must_show_talk_check()会"
                    f"无保护KeyError；must_settle_second_behavior_id_list={must_settle!r}, "
                    f"must_show_second_behavior_id_list={must_show!r}, behavior_id={behavior_id!r}, is_h={is_h}",
                    [cid],
                )
            )
    return failures


@register_check("BEHAV-18", "行为历史队列有界且条目可比")
def check_last_behavior_id_list_bounded() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure] -- 失败记录列表
    功能:
        校验last_behavior_id_list是长度在[1,5]的list，且每个元素要么是0要么是字符串。初值[0]，完成行为时
        追加并裁到5，是全仓库唯一写入点；长度是生产语义的一部分，用last_behavior_id_list[-1]判睡醒后刷新
        异常位，空列表会IndexError。定为warning而非error：旧存档迁移原样复制列表且不裁剪，超长列表每轮只
        缩短1项，会连续多个合法回合告警。不加x in game_config.config_behavior成员校验(旧存档必然噪声)；
        不并入全局cache.pl_pre_behavior_instruce(它没有任何读档裁剪路径)
    """
    cache = cache_control.cache
    character_data = getattr(cache, "character_data", None) or {}
    failures = []
    for cid in _live_ids(cache):
        chara = character_data.get(cid)
        if chara is None:
            continue
        lst = getattr(chara, "last_behavior_id_list", None)
        ok = isinstance(lst, list) and 1 <= len(lst) <= 5 and all(x == 0 or isinstance(x, str) for x in lst)
        if ok:
            continue
        behavior_id = getattr(getattr(chara, "behavior", None), "behavior_id", None)
        length = len(lst) if isinstance(lst, list) else None
        failures.append(
            make_failure(
                "BEHAV-18",
                "行为历史队列有界且条目可比",
                f"[warning] 角色cid={cid}(name={getattr(chara, 'name', '?')!r})的last_behavior_id_list={lst!r}"
                f"(长度{length})不满足'非空列表、长度<=5、元素为0或字符串'；用[-1]判睡醒后刷新异常位，"
                f"空列表会IndexError；behavior_id={behavior_id!r}",
                [cid],
            )
        )
    return failures


@register_check("BEHAV-19", "时停中玩家必须处于时停无意识态")
def check_time_stop_player_unconscious() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure] -- 失败记录列表
    功能:
        校验time_stop_mode为真时，0号玩家的sp_flag.unconscious_h必须等于3(时停语义)。开启时停会把玩家与
        全体已获得干员置3，关闭时置0；玩家这一侧脱节说明时停开关只跑了一半。只保留玩家单向：不扩展到全体NPC
        的双向一致性，时停期间角色上线有多个入口，只有装袋释放/投监两条显式补写3，其他入口直接重置sp_flag，
        NPC侧差异只适合另做告警
    """
    cache = cache_control.cache
    if not getattr(cache, "time_stop_mode", False):
        return []
    character_data = getattr(cache, "character_data", None) or {}
    player = character_data.get(0)
    if player is None:
        return []
    sp_flag = getattr(player, "sp_flag", None)
    if getattr(sp_flag, "unconscious_h", None) == 3:
        return []
    unconscious_npcs = []
    for cid in _live_ids(cache):
        other = character_data.get(cid)
        if getattr(getattr(other, "sp_flag", None), "unconscious_h", None) == 3:
            unconscious_npcs.append(cid)
        if len(unconscious_npcs) >= 10:
            break
    achievement = getattr(cache, "achievement", None)
    return [
        make_failure(
            "BEHAV-19",
            "时停中玩家必须处于时停无意识态",
            f"[warning] time_stop_mode=True但0号玩家sp_flag.unconscious_h={getattr(sp_flag, 'unconscious_h', None)!r}"
            f"!=3，时停开关可能只跑了一半；is_h={getattr(sp_flag, 'is_h', None)}, "
            f"已置3的NPC样本(至多10个)={unconscious_npcs}, time_stop_duration={getattr(achievement, 'time_stop_duration', None)!r}",
            [0],
        )
    ]


@register_check("BEHAV-20", "群交模式必须有玩家在H中")
def check_group_sex_mode_player_in_h() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure] -- 失败记录列表
    功能:
        校验cache.group_sex_mode为真时，0号玩家的sp_flag.is_h必须为真。群交是玩家主导的H场景，标记为真但
        玩家不在H意味着模式泄漏，之后NPC的AI会一直走群交分支。级别为warning：GROUP_SEX_MODE_OFF是配表驱动的
        结算效果，能结束群交的行为是否都挂了该效果并无逐条保证，可能存在合法但暂时不同步的窗口。隐奸把玩家
        is_h清零的路径用的是hidden_sex_mode而非group_sex_mode，不构成本条反例
    """
    cache = cache_control.cache
    if not getattr(cache, "group_sex_mode", False):
        return []
    character_data = getattr(cache, "character_data", None) or {}
    player = character_data.get(0)
    if player is None:
        return []
    sp_flag = getattr(player, "sp_flag", None)
    if getattr(sp_flag, "is_h", False):
        return []
    h_npcs = []
    for cid in _live_ids(cache):
        other = character_data.get(cid)
        if getattr(getattr(other, "sp_flag", None), "is_h", False):
            h_npcs.append(cid)
        if len(h_npcs) >= 10:
            break
    return [
        make_failure(
            "BEHAV-20",
            "群交模式必须有玩家在H中",
            f"[warning] cache.group_sex_mode=True但0号玩家sp_flag.is_h=False，模式可能已泄漏，NPC的AI会一直走"
            f"群交分支；behavior_id={getattr(getattr(player, 'behavior', None), 'behavior_id', None)!r}, "
            f"当前在H中的角色样本(至多10个)={h_npcs}, time_stop_mode={getattr(cache, 'time_stop_mode', None)}",
            [0],
        )
    ]


@register_check("BEHAV-21", "完成集合里只能是存在的角色id")
def check_over_behavior_character_ids_exist() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure] -- 失败记录列表
    功能:
        校验cache.over_behavior_character(结算完成集合)是set，且其中每个元素都是int且指向character_data中
        真实存在的角色。集合的五个写入点传入的都是循环变量character_id，来源只有字面量0与npc_id_got，
        出现不存在的角色id是野指针信号。成员域只能放宽到"存在的角色"，绝不收紧回active_ids：
        日界访客离开/新周目重建等多条合法路径会让覆盖/子集关系合法失效
    """
    cache = cache_control.cache
    over_set = getattr(cache, "over_behavior_character", None)
    character_data = getattr(cache, "character_data", None) or {}
    if not isinstance(over_set, set):
        return [
            make_failure(
                "BEHAV-21",
                "完成集合里只能是存在的角色id",
                f"cache.over_behavior_character类型为{type(over_set).__name__}，期望set",
                [],
            )
        ]
    bad = sorted(x for x in over_set if not (type(x) is int and x in character_data))
    if not bad:
        return []
    npc_id_got = getattr(cache, "npc_id_got", None) or set()
    involved = [x for x in bad if isinstance(x, int)]
    return [
        make_failure(
            "BEHAV-21",
            "完成集合里只能是存在的角色id",
            f"cache.over_behavior_character中存在不是'存在角色id'的元素(野指针信号): {bad!r}，"
            f"集合总长度={len(over_set)}, npc_id_got(前20个)={sorted(npc_id_got)[:20]}, "
            f"time_stop_mode={getattr(cache, 'time_stop_mode', None)}",
            involved,
        )
    ]


@register_check("BEHAV-22", "行为起时落在四季月上")
def check_behavior_start_time_seasonal_month() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure] -- 失败记录列表
    功能:
        校验每个被调度角色(排除哨兵值)的behavior.start_time月份属于四季月{3,6,9,12}。start_time的所有来源
        要么是cache.game_time的拷贝，要么是get_sub_date的输出，因此继承BEHAV-03的月份约束。显式排除哨兵，
        以免与BEHAV-10双重报警。级别为warning：保留的价值在于旧存档迁移会原样复制整个behavior对象，是唯一可能
        带进历史月份的通道，读档后、任何一次结算之前的窗口内触发属于迁移问题而非运行期缺陷
    """
    cache = cache_control.cache
    character_data = getattr(cache, "character_data", None) or {}
    sentinel = datetime.datetime(1, 1, 1)
    failures = []
    for cid in _live_ids(cache):
        chara = character_data.get(cid)
        if chara is None or not _behavior_type_ok(chara):
            continue
        behavior = chara.behavior
        if behavior.start_time == sentinel:
            continue
        if behavior.start_time.month in {3, 6, 9, 12}:
            continue
        failures.append(
            make_failure(
                "BEHAV-22",
                "行为起时落在四季月上",
                f"[warning] 角色cid={cid}(name={getattr(chara, 'name', '?')!r})的behavior.start_time="
                f"{behavior.start_time!r}月份不属于四季月{{3,6,9,12}}，疑似旧存档迁移带入的历史月份；"
                f"behavior_id={behavior.behavior_id!r}, game_time={getattr(cache, 'game_time', None)!r}",
                [cid],
            )
        )
    return failures
