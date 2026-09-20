# -*- coding: UTF-8 -*-
"""
静态检查系统 - 可观察矛盾检查

本模块实现 OBS-01 ~ OBS-18 共18条不变量检查，覆盖玩家可直接从指令面板、角色标签、身体面板、
位置面板与助理设置中观察到的状态矛盾。

全流水线实现总则：
1. 禁止调用 Script/Design/handle_premise 中的正式前提函数；这些函数可能升级旧档结构、写异常位掩码、
   补写指令过滤键或通过 setdefault 修改存档。本模块只直读 cache/character_data 字段，并只调用已确认
   无副作用的地图路径与睡眠等级派生函数。
2. 每回合执行，角色检查保持单层 O(N) 遍历；配置表和场景路径等共享查表放在循环外。
3. 每条检查的文档字符串都说明健康存档为何恒不命中；无法给出该理由的候选不进入本模块。
4. 消息的 ``[warning] `` 前缀表示已确认会命中当前版本真实缺陷的探测器，不是容许误报的出口。
5. 沿用全局守卫：``["0", "0"]`` 是真实场景；路径由 map_handle 助手拼接；离线只认来源标记；
   target_character_id 不作为 H 绑定断言；时停与 debug 按每条规格单独守卫。
6. 全部读取采用 getattr/dict.get 与形状判断；结构异常交给既有形状检查，不重复报告。
7. 一个检查先收集全部失配，再合并为一条 failure，避免检查级日志去重吞掉同次快照中的其余证据。
"""
from typing import Iterator, List, Optional, Tuple

from Script.Config import normal_config
from Script.Core import cache_control, constant, game_type
from Script.Design import attr_calculation, map_handle
from ..check_registry import CheckFailure, make_failure, register_check

try:
    from Script.Config import game_config
except Exception:  # pragma: no cover - 独立运行环境下配置包可能尚未载入
    game_config = None


# 场景路径必须使用游戏自身助手拼接，不能写死平台分隔符。
_P = map_handle.get_map_system_path_str_for_list
_ASSISTANT_SERVICE_KEYS = {2, 3, 4, 5, 6, 7, 8, 10}
_PHYSIOLOGICAL_FLAGS = ("rest", "sleep", "pee", "eat_food", "help_buy_food", "help_make_food", "shower", "milk", "masturebate", "npc_masturebate_for_player")
_BATH_BEHAVIOR_TAGS = {
    constant.Behavior.SWIMMING: "Swimming_Pool",
    constant.Behavior.TAKE_SHOWER: "Bathroom",
    constant.Behavior.SOAK_FEET: "Foot_Bath",
    constant.Behavior.STEAM_SAUNA: "Sauna",
    constant.Behavior.HYDROTHERAPY_TREATMENT: "Spa_Room",
    constant.Behavior.ONSEN_BATH: "Onsen",
}


def _character_data(cache) -> Optional[dict]:
    """
    参数: cache 全局缓存对象
    返回值: Optional[dict] 角色字典；结构异常时返回 None
    功能: 防御式读取 character_data，避免各检查重复裸访问。
    """
    data = getattr(cache, "character_data", None) if cache is not None else None
    return data if isinstance(data, dict) else None


def _pl(cache):
    """
    参数: cache 全局缓存对象
    返回值: 玩家角色对象；角色字典未初始化或缺少 cid=0 时返回 None
    功能: 统一取得玩家对象。
    """
    data = _character_data(cache)
    return data.get(0) if data is not None else None


def _iter_npcs(cache) -> Iterator[Tuple[int, object]]:
    """
    参数: cache 全局缓存对象
    返回值: Iterator[Tuple[int, object]]，依次产出已获得且存在的非玩家角色
    功能: 以 npc_id_got 为域做单层遍历，并保护角色字典中的悬空 id。
    """
    data = _character_data(cache)
    got = getattr(cache, "npc_id_got", None) if cache is not None else None
    if data is None or not got:
        return
    for cid in got:
        if cid != 0 and cid in data:
            yield cid, data[cid]


def _iter_live(cache) -> Iterator[Tuple[int, object]]:
    """
    参数: cache 全局缓存对象
    返回值: Iterator[Tuple[int, object]]，依次产出玩家和已获得 NPC
    功能: 为检查域是 npc_id_got∪{0} 的条目提供统一遍历。
    """
    pl = _pl(cache)
    if pl is not None:
        yield 0, pl
    yield from _iter_npcs(cache)


def _name(chara) -> str:
    """
    参数: chara 角色对象
    返回值: str 角色名，缺失时返回问号
    功能: 防御式生成失败消息中的角色名。
    """
    return str(getattr(chara, "name", "?"))


def _sp(chara):
    """
    参数: chara 角色对象
    返回值: 角色 sp_flag 对象，缺失时返回 None
    功能: 缩短防御式特殊标记读取链。
    """
    return getattr(chara, "sp_flag", None)


def _hs(chara):
    """
    参数: chara 角色对象
    返回值: 角色 h_state 对象，缺失时返回 None
    功能: 缩短防御式 H 状态读取链。
    """
    return getattr(chara, "h_state", None)


def _behavior(chara):
    """
    参数: chara 角色对象
    返回值: 角色 behavior 对象，缺失时返回 None
    功能: 缩短防御式行为字段读取链。
    """
    return getattr(chara, "behavior", None)


def _fully_out_of_h(chara) -> bool:
    """
    参数: chara 角色对象
    返回值: bool，角色完全脱离普通H、无意识H、隐奸与露出时为 True
    功能: 复用 HGROUP-31 的完全脱离 H 四字段口径。
    """
    sp = _sp(chara)
    return sp is not None and not (
        getattr(sp, "is_h", False)
        or getattr(sp, "unconscious_h", 0) != 0
        or getattr(sp, "hidden_sex_mode", 0) != 0
        or getattr(sp, "exhibitionism_sex_mode", 0) != 0
    )


def _scene(cache, position):
    """
    参数: cache 全局缓存对象；position 期望为字符串列表
    返回值: 对应场景对象；路径或场景结构异常时返回 None
    功能: 使用游戏路径助手防御式解析角色当前位置。
    """
    scene_data = getattr(cache, "scene_data", None) if cache is not None else None
    if not isinstance(scene_data, dict) or not isinstance(position, list) or not position or not all(isinstance(x, str) for x in position):
        return None
    return scene_data.get(_P(position))


def _mask(chara) -> Optional[game_type.UnnormalFlagMask]:
    """
    参数: chara 角色对象
    返回值: Optional[UnnormalFlagMask]，旧档原始结构或缺字段时返回 None
    功能: 只读取得异常位掩码，绝不调用会就地迁移旧档的正式前提函数。
    """
    raw = getattr(_sp(chara), "unnormal_flag", None)
    return raw if isinstance(raw, game_type.UnnormalFlagMask) else None


def _sleep_level(chara) -> Optional[int]:
    """
    参数: chara 角色对象
    返回值: Optional[int] 睡眠等级；配置未载入或字段不可计算时返回 None
    功能: 调用已确认只读的睡眠等级派生函数，并把独立脚本缺配置降级为跳过。
    """
    if game_config is None or not getattr(game_config, "config_sleep_level", None):
        return None
    value = getattr(chara, "sleep_point", None)
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return None
    try:
        return attr_calculation.get_sleep_level(value)[0]
    except Exception:
        return None


def _positive_number(value) -> bool:
    """
    参数: value 任意字段值
    返回值: bool，value 是非 bool 数值且大于零时为 True
    功能: 为旧档字段做安全的正数判断，值域或类型异常时跳过而不让检查自身抛错。
    """
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0


def _offline_context(chara) -> str:
    """
    参数: chara 角色对象
    返回值: str 离线来源标记摘要
    功能: 仅把装袋、外勤、外交访问、逃跑等来源标记写入消息上下文，不把坐标误当离线哨兵。
    """
    sp = _sp(chara)
    return (
        f"be_bagged={getattr(sp, 'be_bagged', None)}, field_commission={getattr(sp, 'field_commission', None)}, "
        f"in_diplomatic_visit={getattr(sp, 'in_diplomatic_visit', None)}, escaping={getattr(sp, 'escaping', None)}, vistor={getattr(sp, 'vistor', None)}"
    )


@register_check("OBS-01", "玩家不在H时同场不得有在H的NPC")
def check_observable_01() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]，没有同场 H 残留时为空
    功能: 玩家完全退出普通H且不在隐奸/群交/时停时，同场 NPC 的 is_h 应已由结束链清零；健康存档的结束链对象一致，因此恒不命中。
    """
    cache = cache_control.cache
    pl = _pl(cache)
    if pl is None or getattr(cache, "debug_mode", False) or getattr(cache, "time_stop_mode", False) or getattr(cache, "group_sex_mode", False):
        return []
    pl_sp = _sp(pl)
    if pl_sp is None or getattr(pl_sp, "is_h", False) or getattr(pl_sp, "hidden_sex_mode", 0) != 0:
        return []
    bad = []
    for cid, chara in _iter_npcs(cache):
        if getattr(chara, "position", None) == getattr(pl, "position", None) and getattr(_sp(chara), "is_h", False):
            bad.append(cid)
    if not bad:
        return []
    details = [f"cid={cid}({_name(cache.character_data[cid])}) target={getattr(cache.character_data[cid], 'target_character_id', None)}" for cid in bad]
    return [make_failure("OBS-01", "玩家不在H时同场不得有在H的NPC", f"[warning] 已知缺陷机制：效果404按执行时target重置双方，错对象收尾会让真伙伴同场残留is_h；玩家已不在H但同场NPC仍在H：{details}；玩家target={getattr(pl, 'target_character_id', None)} position={getattr(pl, 'position', None)}", [0] + bad)]


@register_check("OBS-02", "玩家有性交体位时场内必须真有人被对应插入")
def check_observable_02() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]，玩家体位与场内插入状态一致时为空
    功能: 校验玩家独占体位字段与场内 NPC 插入位置相互支撑；健康存档的体位切换与拔出链同步维护两侧字段，因此恒不命中。
    """
    cache = cache_control.cache
    pl = _pl(cache)
    if pl is None or getattr(cache, "debug_mode", False) or getattr(cache, "time_stop_mode", False):
        return []
    hs = _hs(pl)
    if hs is None:
        return []
    sex_position = getattr(hs, "current_sex_position", None)
    womb_position = getattr(hs, "current_womb_sex_position", None)
    insertions = []
    h_in_scene = []
    for cid, chara in _iter_npcs(cache):
        if getattr(chara, "position", None) != getattr(pl, "position", None):
            continue
        pos = getattr(_hs(chara), "insert_position", None)
        if isinstance(pos, int) and not isinstance(pos, bool):
            insertions.append((cid, pos))
        if getattr(_sp(chara), "is_h", False):
            h_in_scene.append(cid)
    bad = []
    if isinstance(sex_position, int) and not isinstance(sex_position, bool) and sex_position != -1 and not any(pos in {6, 7, 8, 9} for _, pos in insertions):
        bad.append(f"current_sex_position={sex_position}但场内无人insert_position∈{{6,7,8,9}}")
    if isinstance(womb_position, int) and not isinstance(womb_position, bool) and womb_position != 0 and not any(pos == 7 for _, pos in insertions):
        bad.append(f"current_womb_sex_position={womb_position}但场内无人insert_position=7")
    if _fully_out_of_h(pl) and ((isinstance(sex_position, int) and not isinstance(sex_position, bool) and sex_position != -1) or (isinstance(womb_position, int) and not isinstance(womb_position, bool) and womb_position != 0)):
        bad.append("玩家已完全脱离H但体位字段仍非空")
    if not bad:
        return []
    return [make_failure("OBS-02", "玩家有性交体位时场内必须真有人被对应插入", f"{'; '.join(bad)}；场内插入={insertions}，场内is_h角色={h_in_scene}", [0])]


@register_check("OBS-03", "完全脱离H的角色不得残留口球")
def check_observable_03() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]，没有非H口球残留时为空
    功能: 检查完全脱离 H 的角色 body_item[14] 未仍处于装备状态；健康存档应在 H 重置时移除 H 装备，所以恒不命中。
    """
    cache = cache_control.cache
    if cache is None or getattr(cache, "debug_mode", False):
        return []
    bad = []
    for cid, chara in _iter_live(cache):
        if not _fully_out_of_h(chara):
            continue
        items = getattr(_hs(chara), "body_item", None)
        item = items.get(14) if isinstance(items, dict) else None
        if isinstance(item, (list, tuple)) and len(item) == 3 and bool(item[1]):
            bad.append(cid)
    if not bad:
        return []
    return [make_failure("OBS-03", "完全脱离H的角色不得残留口球", f"[warning] 已知配表缺陷机制：口球(14)被标为type=0，H重置会原样保留；以下角色出现非H口球残留：{bad}", bad)]


@register_check("OBS-04", "透视或信息素开关开启时玩家必须持有对应素质")
def check_observable_04() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]，技艺开关均有基础素质支撑时为空
    功能: 校验透视/信息素开关与其关闭指令所需基础素质一致；健康存档只能经持有素质的开启指令置位，所以恒不命中。
    """
    cache = cache_control.cache
    pl = _pl(cache)
    if pl is None or getattr(cache, "debug_mode", False):
        return []
    ability = getattr(pl, "pl_ability", None)
    talent = getattr(pl, "talent", None)
    if ability is None or not isinstance(talent, dict):
        return []
    bad = []
    if getattr(ability, "visual", False) and not talent.get(307, 0):
        bad.append("透视开关visual=True但基础透视素质307缺失，关闭指令不可用")
    if getattr(ability, "hormone", False) and not talent.get(304, 0):
        bad.append("信息素开关hormone=True但基础信息素素质304缺失，关闭指令不可用")
    if not bad:
        return []
    return [make_failure("OBS-04", "透视或信息素开关开启时玩家必须持有对应素质", f"[warning] 已知缺陷机制：旧档迁移或mod可让开关保留而素质消失；{'; '.join(bad)}", [0])]


@register_check("OBS-05", "玩家的交互对象必须在当前场景名册里")
def check_observable_05() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]，非装袋交互对象在玩家场景名册中时为空
    功能: 校验指令面板轴心 target 与场景名册一致；健康存档中 Tk 会归一化目标，Web 也应只保留在场目标，装袋搬运是唯一明确例外。
    """
    cache = cache_control.cache
    pl = _pl(cache)
    data = _character_data(cache)
    if pl is None or data is None or getattr(cache, "debug_mode", False):
        return []
    target_id = getattr(pl, "target_character_id", None)
    if not isinstance(target_id, int) or isinstance(target_id, bool) or target_id == 0 or target_id not in data or target_id == getattr(_sp(pl), "bagging_chara_id", None):
        return []
    scene = _scene(cache, getattr(pl, "position", None))
    roster = getattr(scene, "character_list", None) if scene is not None else None
    if not isinstance(roster, (list, set, tuple)) or target_id in roster:
        return []
    target = data[target_id]
    pre = getattr(cache, "pl_pre_behavior_instruce", None)
    last_pre = pre[-1] if isinstance(pre, list) and pre else None
    web_draw = getattr(getattr(normal_config, "config_normal", None), "web_draw", None)
    return [make_failure("OBS-05", "玩家的交互对象必须在当前场景名册里", f"[warning] 已知缺陷机制：Web目标卡缺少Tk侧的在场归一化；target cid={target_id}({_name(target)})不在玩家当前场景名册，web_draw={web_draw}，pl.position={getattr(pl, 'position', None)}，target.position={getattr(target, 'position', None)}，离线来源={_offline_context(target)}，上一玩家指令={last_pre}", [0, target_id])]


@register_check("OBS-06", "同一角色不得同时处于隐奸模式与露出模式")
def check_observable_06() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]，隐奸与露出模式互斥时为空
    功能: 检查同一角色的两种 H 分流模式不会同时大于零；健康存档的入口与结束链应保持模式互斥，因此恒不命中。
    """
    cache = cache_control.cache
    if cache is None or getattr(cache, "debug_mode", False):
        return []
    bad = []
    details = []
    for cid, chara in _iter_live(cache):
        sp = _sp(chara)
        hidden = getattr(sp, "hidden_sex_mode", 0)
        exhibitionism = getattr(sp, "exhibitionism_sex_mode", 0)
        if isinstance(hidden, (int, float)) and isinstance(exhibitionism, (int, float)) and hidden > 0 and exhibitionism > 0:
            bad.append(cid)
            details.append(f"cid={cid}({_name(chara)}) hidden={hidden} exhibitionism={exhibitionism}({'玩家侧已知可达' if cid == 0 else 'NPC侧模式泄漏'})")
    if not bad:
        return []
    return [make_failure("OBS-06", "同一角色不得同时处于隐奸模式与露出模式", f"[warning] 已知缺陷机制：隐奸1/2清玩家is_h后可经NOT_H入口叠加露出模式；{details}", bad)]


@register_check("OBS-07", "性爱助手结算必须满足监狱长约束")
def check_observable_07() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]，性爱助手设置、监狱长与角色标记一致时为空
    功能: 校验群交调教现场有非零监狱长，且 sex_assist 只落在该监狱长身上；健康存档的助手结算应只写当前监狱长，因此恒不命中。
    """
    cache = cache_control.cache
    if cache is None or getattr(cache, "debug_mode", False) or getattr(cache, "time_stop_mode", False):
        return []
    island = getattr(cache, "rhodes_island", None)
    settings = getattr(island, "confinement_training_setting", None)
    if island is None or not isinstance(settings, dict):
        return []
    warden = getattr(island, "current_warden_id", None)
    bad_ids = []
    bad = []
    if _positive_number(settings.get(12, 0)) and warden == 0 and getattr(cache, "group_sex_mode", False):
        bad.append("群交现场已开启调教助手设置但current_warden_id=0，结算会把玩家当助手")
        bad_ids.append(0)
    data = _character_data(cache) or {}
    for cid, chara in data.items():
        if getattr(_hs(chara), "sex_assist", False) is True and (warden == 0 or cid != warden):
            bad.append(f"{'玩家' if cid == 0 else '角色'}cid={cid}({_name(chara)}) sex_assist=True但当前监狱长={warden}")
            bad_ids.append(cid)
    if not bad:
        return []
    return [make_failure("OBS-07", "性爱助手结算必须满足监狱长约束", f"[warning] 已知缺陷机制：助手结算直接把warden行为覆盖为助手行为，空监狱长会落到cid=0；{'; '.join(bad)}", sorted(set(bad_ids)))]


@register_check("OBS-08", "醉酒型无意识H不得在醉酒值耗尽后残留")
def check_observable_08() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]，unconscious_h=2 均仍有正醉酒值支撑时为空
    功能: 检查醉酒型无意识 H 不会在 drunk_point<=0 后继续残留；健康存档若来源消失就应同步退出该模式，因此恒不命中。
    """
    cache = cache_control.cache
    if cache is None or getattr(cache, "debug_mode", False) or getattr(cache, "time_stop_mode", False):
        return []
    bad = []
    details = []
    for cid, chara in _iter_live(cache):
        drunk_point = getattr(chara, "drunk_point", None)
        if getattr(_sp(chara), "unconscious_h", 0) == 2 and isinstance(drunk_point, (int, float)) and not isinstance(drunk_point, bool) and drunk_point <= 0:
            bad.append(cid)
            details.append(f"cid={cid}({_name(chara)}) drunk_point={drunk_point}")
    if not bad:
        return []
    return [make_failure("OBS-08", "醉酒型无意识H不得在醉酒值耗尽后残留", f"[warning] 已知缺陷机制：当前代码没有以酒醒为触发的unconscious_h清零路径；{details}", bad)]


@register_check("OBS-09", "非群交下至多一名NPC处于阴茎插入中")
def check_observable_09() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]，非群交快照中至多一名 NPC 有插入位置时为空
    功能: 校验玩家单一阴茎不会在普通 H 中同时记录插入多名 NPC；健康存档换位与拔出链会清旧对象，所以恒不命中。
    """
    cache = cache_control.cache
    if cache is None or getattr(cache, "debug_mode", False) or getattr(cache, "time_stop_mode", False) or getattr(cache, "group_sex_mode", False):
        return []
    bad = []
    for cid, chara in _iter_npcs(cache):
        pos = getattr(_hs(chara), "insert_position", -1)
        if isinstance(pos, int) and not isinstance(pos, bool) and pos != -1:
            bad.append(cid)
    if len(bad) < 2:
        return []
    details = [f"cid={cid}({_name(cache.character_data[cid])}) insert_position={getattr(_hs(cache.character_data[cid]), 'insert_position', None)}" for cid in bad]
    return [make_failure("OBS-09", "非群交下至多一名NPC处于阴茎插入中", f"[warning] 已知低频残留机制：普通H换位仅有少数复位点，旧对象可能保留insert_position；{details}", bad)]


@register_check("OBS-10", "异常位掩码第5和第6位的反向一致性")
def check_observable_10() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]，已知且激活的意识异常位仍有来源支撑、或醉酒源不可判定时为空
    功能: 保守反向复算第5/6位来源，对照 handle_normal_5/6（Script/Design/handle_premise/__init__.py:1010-1058）：
        睡眠项复用 MIND-27 已有的睡眠等级安全推导（attr_calculation.get_sleep_level，纯读）配合行为/unconscious_h==1
        直读；unconscious_h 3/4/5 与时停直读字段；醉酒项采保守口径——只有 drunk_point<=0 时才断言"醉酒源必不成立"
        （酒量素质是乘数，0 乘任何数仍为等级0），drunk_point>0 时视为醉酒源可能成立，整条放行、不判该角色，禁止
        复制 get_drunk_level 的乘数公式或调用 drunk_sex_common（会间接触发正式前提函数，违反总则1）。健康存档中
        缓存激活该位时，至少一个原始来源仍成立，或醉酒值未耗尽而放行，因此恒不命中。
    """
    cache = cache_control.cache
    if cache is None or getattr(cache, "debug_mode", False):
        return []
    if game_config is None or not getattr(game_config, "config_sleep_level", None):
        return []
    time_stop = getattr(cache, "time_stop_mode", False)
    bad = []
    details = []
    for cid, chara in _iter_npcs(cache):
        mask = _mask(chara)
        if mask is None or not (mask.is_known(5) and mask.check(5)) and not (mask.is_known(6) and mask.check(6)):
            continue
        sp = _sp(chara)
        u = getattr(sp, "unconscious_h", None)
        if not isinstance(u, int) or isinstance(u, bool):
            continue
        drunk_point = getattr(chara, "drunk_point", None)
        if not isinstance(drunk_point, (int, float)) or isinstance(drunk_point, bool):
            continue
        if drunk_point > 0:
            # 醉酒源可能成立（乘数未知，保守放行），不对该角色下判定。
            continue
        sleep_level = _sleep_level(chara)
        if sleep_level is None:
            continue
        behavior_id = getattr(_behavior(chara), "behavior_id", None)
        sleeping = behavior_id == constant.Behavior.SLEEP or u == 1
        if mask.is_known(6) and mask.check(6):
            source6 = (sleep_level >= 1 and sleeping) or u == 5 or time_stop or u == 3
            if not source6:
                bad.append(cid)
                details.append(
                    f"cid={cid}({_name(chara)})第6位已知且异常但四组来源全不成立: sleep_level={sleep_level} sleeping={sleeping} "
                    f"unconscious_h={u} time_stop={time_stop} drunk_point={drunk_point}"
                )
        if mask.is_known(5) and mask.check(5):
            source5 = (sleep_level == 0 and sleeping) or u == 4
            if not source5:
                bad.append(cid)
                details.append(
                    f"cid={cid}({_name(chara)})第5位已知且异常但三组来源全不成立: sleep_level={sleep_level} sleeping={sleeping} "
                    f"unconscious_h={u} drunk_point={drunk_point}"
                )
    if not bad:
        return []
    return [make_failure("OBS-10", "异常位掩码第5和第6位的反向一致性", f"[warning] 保守反向陈旧探测（drunk_point<=0时醉酒源必不成立）：{'; '.join(details)}", sorted(set(bad)))]


# OBS-11（已删除，2026-08-28）：曾断言"异地智能跟随者必须正在赶路或门外等待"（is_follow==1 且异地却处于
# SHARE_BLANKLY 即报）。sol 调查 + opus 复核确认该单帧断言结构性不成立：(1) 行为结束重置
# （character_behavior.py:327-350，time_judge==2）在采样点（指令面板绘制后）必然产生临时 SHARE_BLANKLY；
# (2) 合法"门外等待"WAIT 结束同样重置为同一形态；(3) is_follow==1 本就由 AI 目标表驱动而非每回合直接派发
# （is_follow==2 才是），断言"恒驱动 MOVE/WAIT"对 1 结构性错。真正的滞留（跟随目标丢失、寻路卡死）几乎必然
# 表现为角色卡死不动或 is_follow 被自动归 0，以"持续 SHARE_BLANKLY 且 is_follow 仍为 1"的形态存在的真故障
# 类别近乎为空；要做成能立住的持久化版本需要跨帧状态与经验阈值，违反本模块单帧只读设计前提。


@register_check("OBS-12", "助理跟随服务开启时恢复正常的空闲助理必须在跟随")
def check_observable_12() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]，已恢复正常的空闲助理与跟随服务设置一致时为空
    功能: 检查服务2开启后，非疲劳、非困倦、无生理意图、非H的空闲在线助理不会丢失跟随；健康存档的服务承诺应维持 is_follow=1，因此恒不命中。
    """
    cache = cache_control.cache
    pl = _pl(cache)
    data = _character_data(cache)
    if pl is None or data is None or getattr(cache, "debug_mode", False) or getattr(cache, "time_stop_mode", False):
        return []
    assistant_id = getattr(pl, "assistant_character_id", None)
    got_raw = getattr(cache, "npc_id_got", None)
    if not isinstance(got_raw, (set, list, tuple)):
        return []
    got = set(got_raw)
    if not isinstance(assistant_id, int) or isinstance(assistant_id, bool) or assistant_id not in data or assistant_id not in got or assistant_id == 0:
        return []
    assistant = data[assistant_id]
    services = getattr(assistant, "assistant_services", None)
    if not isinstance(services, dict) or not bool(services.get(2, 0)):
        return []
    sp = _sp(assistant)
    follow = getattr(sp, "is_follow", None)
    if follow in {2, 3, 4} or follow != 0 or getattr(_behavior(assistant), "behavior_id", None) != constant.Behavior.SHARE_BLANKLY:
        return []
    sleep_level = _sleep_level(assistant)
    if sleep_level is None or getattr(sp, "tired", False) or sleep_level >= 2:
        return []
    physiological = (
        getattr(sp, "rest", False)
        or getattr(sp, "sleep", False)
        or getattr(sp, "pee", False)
        or _positive_number(getattr(sp, "eat_food", 0))
        or _positive_number(getattr(sp, "help_buy_food", 0))
        or _positive_number(getattr(sp, "help_make_food", 0))
        or _positive_number(getattr(sp, "shower", 0))
        or getattr(sp, "milk", False)
        or _positive_number(getattr(sp, "masturebate", 0))
        or getattr(sp, "npc_masturebate_for_player", False)
    )
    if physiological or getattr(sp, "is_h", False) or getattr(sp, "unconscious_h", 0) != 0:
        return []
    if getattr(sp, "be_bagged", False) or getattr(sp, "field_commission", 0) or getattr(sp, "escaping", False) or getattr(sp, "in_diplomatic_visit", 0):
        return []
    return [make_failure("OBS-12", "助理跟随服务开启时恢复正常的空闲助理必须在跟随", f"[warning] 已知缺陷机制：疲劳/困倦会清is_follow，而白天恢复后没有重挂路径，只有跨日睡眠恢复；助理cid={assistant_id}({_name(assistant)}) services[2]={services.get(2)!r} is_follow={follow} sleep_level={sleep_level}", [0, assistant_id])]


@register_check("OBS-13", "非当前助理的角色助理服务位必须全为0")
def check_observable_13() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]，只有当前助理持有已实装服务位时为空
    功能: 全量检查非玩家、非当前助理角色的已实装服务位均归零；健康存档在替换或取消助理时会清旧服务，因此恒不命中。
    """
    cache = cache_control.cache
    pl = _pl(cache)
    data = _character_data(cache)
    if pl is None or data is None:
        return []
    assistant_id = getattr(pl, "assistant_character_id", None)
    if not isinstance(assistant_id, int) or isinstance(assistant_id, bool):
        return []
    bad = []
    details = []
    for cid, chara in data.items():
        if cid == 0 or cid == assistant_id:
            continue
        services = getattr(chara, "assistant_services", None)
        if not isinstance(services, dict):
            continue
        active = {key: services.get(key) for key in _ASSISTANT_SERVICE_KEYS if services.get(key)}
        if active:
            bad.append(cid)
            details.append(f"cid={cid}({_name(chara)}) active_services={active}")
    if not bad:
        return []
    return [make_failure("OBS-13", "非当前助理的角色助理服务位必须全为0", f"当前助理cid={assistant_id}，但以下非助理角色仍持有会被AI消费的服务位：{details}", bad)]


@register_check("OBS-14", "异常位掩码第4位必须与当前穿着重算一致")
def check_observable_14() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]，服装异常缓存与当前穿着一致时为空
    功能: 直读 cloth_wear 复算全裸或大致全裸，不调用会写掩码的 handle_normal_4；健康存档的换衣路径会同步刷新第4位，因此恒不命中。
    """
    cache = cache_control.cache
    clothing_types = getattr(game_config, "config_clothing_type", None) if game_config is not None else None
    if cache is None or getattr(cache, "debug_mode", False) or not clothing_types:
        return []
    type_ids = tuple(clothing_types.keys())
    bad = []
    details = []
    for cid, chara in _iter_npcs(cache):
        mask = _mask(chara)
        if mask is None or not mask.is_known(4):
            continue
        wear = getattr(getattr(chara, "cloth", None), "cloth_wear", None)
        if not isinstance(wear, dict) or any(key not in wear or not isinstance(wear.get(key), list) for key in type_ids) or any(key not in wear or not isinstance(wear.get(key), list) for key in (5, 6, 8, 9)):
            continue
        cloth_off = True
        for clothing_type in type_ids:
            slot = wear[clothing_type]
            if not slot:
                continue
            if clothing_type == 3 and slot == [352]:
                continue
            if clothing_type == 7 and slot == [751]:
                continue
            cloth_off = False
            break
        cloth_most_off = all(not wear[key] for key in (5, 6, 8, 9))
        recomputed = cloth_off or cloth_most_off
        if mask.check(4) != recomputed:
            bad.append(cid)
            details.append(f"cid={cid}({_name(chara)}) mask.check(4)={mask.check(4)} 重算={recomputed} cloth_off={cloth_off} cloth_most_off={cloth_most_off}")
    if not bad:
        return []
    return [make_failure("OBS-14", "异常位掩码第4位必须与当前穿着重算一致", f"[warning] {details}", bad)]


@register_check("OBS-15", "异常位掩码第1位必须与基础生理来源重算一致")
def check_observable_15() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]，第1位缓存与全部生理意图来源一致时为空
    功能: 直读来源 flag 复算基础生理异常，不调用会写掩码的 handle_normal_1；健康存档在来源变化时同步更新缓存，因此恒不命中。
    """
    cache = cache_control.cache
    if cache is None or getattr(cache, "debug_mode", False):
        return []
    bad = []
    details = []
    for cid, chara in _iter_npcs(cache):
        mask = _mask(chara)
        sp = _sp(chara)
        if mask is None or not mask.is_known(1) or sp is None:
            continue
        values = {name: getattr(sp, name, None) for name in _PHYSIOLOGICAL_FLAGS}
        if any(value is None for value in values.values()):
            continue
        try:
            recomputed = bool(
                values["rest"] == 1
                or values["sleep"] == 1
                or values["pee"] == 1
                or values["eat_food"] >= 1
                or values["help_buy_food"] >= 1
                or values["help_make_food"] >= 1
                or values["shower"] in {1, 2, 3}
                or values["milk"] == 1
                or values["masturebate"] > 0
                or values["npc_masturebate_for_player"]
            )
        except (TypeError, ValueError):
            continue
        if mask.check(1) != recomputed:
            bad.append(cid)
            details.append(f"cid={cid}({_name(chara)}) mask.check(1)={mask.check(1)} 重算={recomputed} sources={values}")
    if not bad:
        return []
    return [make_failure("OBS-15", "异常位掩码第1位必须与基础生理来源重算一致", f"基础生理异常缓存与来源flag不一致：{details}", bad)]


@register_check("OBS-16", "洗浴和游泳类行为必须发生在对应设施")
def check_observable_16() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]，六类行为均位于对应设施时为空
    功能: 校验 NPC 当前洗浴/游泳行为与场景标签匹配；健康存档只会在带目标设施前提的状态机中启动行为，移动又会替换行为，因此恒不命中。
    """
    cache = cache_control.cache
    if cache is None or getattr(cache, "debug_mode", False) or getattr(cache, "time_stop_mode", False):
        return []
    bad = []
    details = []
    for cid, chara in _iter_npcs(cache):
        behavior_id = getattr(_behavior(chara), "behavior_id", None)
        expected = _BATH_BEHAVIOR_TAGS.get(behavior_id)
        if expected is None:
            continue
        scene = _scene(cache, getattr(chara, "position", None))
        tags = getattr(scene, "scene_tag", None) if scene is not None else None
        if not isinstance(tags, (list, set, tuple)):
            continue
        if expected not in tags:
            bad.append(cid)
            details.append(f"cid={cid}({_name(chara)}) behavior={behavior_id} position={getattr(chara, 'position', None)} scene_tags={tags} 期望={expected}")
    if not bad:
        return []
    return [make_failure("OBS-16", "洗浴和游泳类行为必须发生在对应设施", f"行为与设施标签矛盾：{details}", bad)]


@register_check("OBS-17", "移动行为中的NPC必须带非空最终目的地")
def check_observable_17() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]，所有移动中的 NPC 都带非空 move_final_target 时为空
    功能: 检查位置面板可见的移动行为拥有最终目的地；健康存档的寻路提交会同步填写该字段，抵达或取消时会退出移动行为，因此恒不命中。
    """
    cache = cache_control.cache
    if cache is None or getattr(cache, "debug_mode", False) or getattr(cache, "time_stop_mode", False):
        return []
    bad = []
    details = []
    for cid, chara in _iter_npcs(cache):
        behavior = _behavior(chara)
        if getattr(behavior, "behavior_id", None) == constant.Behavior.MOVE and getattr(behavior, "move_final_target", None) == []:
            bad.append(cid)
            details.append(
                f"cid={cid}({_name(chara)}) position={getattr(chara, 'position', None)} move_src={getattr(behavior, 'move_src', None)} "
                f"move_target={getattr(behavior, 'move_target', None)} duration={getattr(behavior, 'duration', None)} start_time={getattr(behavior, 'start_time', None)} "
                f"is_follow={getattr(_sp(chara), 'is_follow', None)} is_h={getattr(_sp(chara), 'is_h', None)}"
            )
    if not bad:
        return []
    return [make_failure("OBS-17", "移动行为中的NPC必须带非空最终目的地", f"[warning] 已知缺陷机制：抵达清空或cancel_movement_plan可留下原作者标注BUG的移动空目的地尾态；{details}", bad)]


@register_check("OBS-18", "绳缚值必须是合法配置键")
def check_observable_18() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]，所有非零 bondage 都能索引配置表时为空
    功能: 防止 realtime_settle 以非法绳缚键直接索引 config_bondage 崩溃；健康存档只由绳缚面板写配置表中的合法键，因此恒不命中。
    """
    cache = cache_control.cache
    data = _character_data(cache)
    bondage_config = getattr(game_config, "config_bondage", None) if game_config is not None else None
    if data is None or not bondage_config:
        return []
    bad = []
    details = []
    for cid, chara in data.items():
        bondage = getattr(_hs(chara), "bondage", 0)
        if bondage == 0:
            continue
        try:
            invalid = bondage not in bondage_config
        except TypeError:
            # 不可哈希的非零bondage本身就是结算侧config_bondage[bondage]会抛TypeError崩溃的情形，必须记为非法。
            invalid = True
        if invalid:
            bad.append(cid)
            details.append(f"cid={cid}({_name(chara)}) bondage={bondage!r}")
    if not bad:
        return []
    return [make_failure("OBS-18", "绳缚值必须是合法配置键", f"非法绳缚值会在realtime_settle直接索引config_bondage并崩溃：{details}", bad)]
