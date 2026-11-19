# -*- coding: UTF-8 -*-
"""
静态检查系统 - 意识域（时停/催眠/无意识/睡眠）领域检查
本模块实现 MIND-01 ~ MIND-30 共30条不变量检查，覆盖时间停止、催眠深度/类型/子项、
角色扮演列表、异常位掩码5/6、睡眠/装睡、熟睡值等意识状态相关字段的一致性约束。
来源: final_invariants_mind.md（M-xx + MS-xx 不变式清单）。

约定与踩坑说明（写在此处，避免散落在各检查函数注释里重复）：
1. `cid == 0` 是玩家角色。`_quick_check_normal_by_mask`（handle_premise/__init__.py）对玩家恒返回"正常"，
   于是玩家的 unnormal_flag 第5/6位在开时停等场景下必然是"已知且未激活"——凡是断言该掩码的检查
   （MIND-26/MIND-27）必须显式排除玩家，否则每次开时停都会稳定误报。
2. `unnormal_flag` 字段在旧存档中可能仍是原始dict（未被 `_ensure_unnormal_flag_storage` 升级为
   `UnnormalFlagMask`）。本模块只读不写，绝不调用会回写角色数据的升级函数；遇到非 `UnnormalFlagMask`
   的原始值一律跳过该角色，见 `_mask()`。
3. `cache.debug_mode` 下debug面板可越过前提直接改素质、催眠深度/子项、角色扮演列表、熟睡值等，
   凡这些字段参与、且检查内容为"值来自合法结算路径"的不变式，都在检查体前加debug豁免；
   纯粹的存档结构/schema式检查（如MIND-22/28/29）不受debug模式影响，不加豁免。
4. `cache.npc_id_got` 不保证是 `cache.character_data` 的子集，一律用 `_iter_npcs()` 做存在性保护。
5. 场景key统一用 `map_handle.get_map_system_path_str_for_list`（`os.sep.join`），不是 "|".join。
6. `game_config.config_roleplay` 在独立脚本环境下可能未加载，相关检查（MIND-16）遇缺表时降级为跳过。
7. 全部字段访问一律使用 getattr/dict.get 加默认值防御，绝不能因为老存档缺字段或类型不符而让检查器自身抛异常。
"""
from typing import List, Optional

from Script.Core import cache_control, game_type
from Script.Design import map_handle
from ..check_registry import CheckFailure, register_check, make_failure


def _name(chara) -> str:
    """
    参数: chara 角色对象
    返回值: str 角色名，取不到时返回"?"
    功能: 防御式获取角色名用于拼接失败信息
    """
    return str(getattr(chara, "name", "?"))


def _pl():
    """
    参数: 无
    返回值: 玩家角色对象，cache未初始化或0号角色不存在时返回None
    功能: 统一获取玩家角色对象
    """
    cache = cache_control.cache
    if cache is None or not isinstance(getattr(cache, "character_data", None), dict):
        return None
    return cache.character_data.get(0)


def _iter_npcs():
    """
    参数: 无
    返回值: 迭代器，依次产出(角色id, 角色对象)
    功能: 遍历cache.npc_id_got中已登场且确实存在于character_data中的NPC；
        npc_id_got未必是character_data的子集，必须加存在性保护
    """
    cache = cache_control.cache
    if cache is None or not isinstance(getattr(cache, "character_data", None), dict):
        return
    npc_id_got = getattr(cache, "npc_id_got", None)
    if not npc_id_got:
        return
    for cid in npc_id_got:
        if cid and cid in cache.character_data:
            yield cid, cache.character_data[cid]


def _iter_all():
    """
    参数: 无
    返回值: 迭代器，依次产出(角色id, 角色对象)
    功能: 遍历cache.character_data全体（含未登场的访客/静态npc模板实例）
    """
    cache = cache_control.cache
    if cache is None or not isinstance(getattr(cache, "character_data", None), dict):
        return
    for cid, chara in cache.character_data.items():
        yield cid, chara


def _iter_pl_and_npcs():
    """
    参数: 无
    返回值: 迭代器，依次产出(角色id, 角色对象)，玩家(若存在)排在最前
    功能: 供"玩家 + 已登场干员"这一常见迭代范围复用
    """
    pl = _pl()
    if pl is not None:
        yield 0, pl
    yield from _iter_npcs()


def _talent_get(chara, talent_id: int) -> int:
    """
    参数:
        chara: 角色对象
        talent_id (int): 素质id
    返回值:
        int: 素质取值，结构异常或缺键时返回0
    功能:
        防御式读取素质值，避免素质表缺键或结构异常让检查器自身抛异常
    """
    talent = getattr(chara, "talent", None)
    if not isinstance(talent, dict):
        return 0
    value = talent.get(talent_id, 0)
    return value if isinstance(value, int) and not isinstance(value, bool) else 0


def _mask(chara) -> Optional["game_type.UnnormalFlagMask"]:
    """
    参数: chara 角色对象
    返回值: UnnormalFlagMask实例；旧存档里仍是dict、或sp_flag/unnormal_flag结构缺失时返回None
    功能: 只读获取角色的异常状态位掩码。绝不调用会回写角色数据的_ensure_unnormal_flag_storage，
        调用方在收到None时必须跳过该角色而不是报错
    """
    sp_flag = getattr(chara, "sp_flag", None)
    raw = getattr(sp_flag, "unnormal_flag", None)
    return raw if isinstance(raw, game_type.UnnormalFlagMask) else None


def _u(chara) -> int:
    """
    参数: chara 角色对象
    返回值: int sp_flag.unconscious_h取值，结构缺失时返回-1（不落在任何合法值域内，交由调用方处理）
    功能: 防御式读取无意识H状态
    """
    return getattr(getattr(chara, "sp_flag", None), "unconscious_h", -1)


def _behavior_id(chara) -> str:
    """
    参数: chara 角色对象
    返回值: str 当前行为id，结构缺失时返回"?"
    功能: 防御式读取behavior.behavior_id
    """
    return getattr(getattr(chara, "behavior", None), "behavior_id", "?")


def _scene_key(position) -> Optional[str]:
    """
    参数: position 角色/玩家的position字段
    返回值: Optional[str] 场景key字符串；position不是"全字符串的list"形状时返回None
    功能: 用map_handle.get_map_system_path_str_for_list(os.sep.join)统一生成场景key，
        供MIND-19/MIND-20按场景查cache.scene_data；坏形状交由调用方判失败而不是让本函数抛异常
    """
    if not isinstance(position, list) or not position or not all(isinstance(x, str) for x in position):
        return None
    return map_handle.get_map_system_path_str_for_list(position)


def _num(x) -> bool:
    """
    参数: x 任意值
    返回值: bool x为非bool的int/float时返回True
    功能: 判断x是否为可安全参与大小比较的数值，排除bool（bool是int子类，会静默通过数值比较）
    """
    return isinstance(x, (int, float)) and not isinstance(x, bool)


# ============================== 一、时停 ==============================


@register_check("MIND-01", "时停开启时玩家处于时停无意识")
def check_time_stop_player_unconscious() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]
    功能:
        校验TIME_STOP_ON把npc_id_got|{0}全部置为3之后，玩家侧没有任何"上线重置"之类的合法例外路径；
        时停开着而玩家unconscious_h不是3，意味着有非指令路径改写了玩家意识状态。
        玩家半没有NPC半(MIND-02)已知的"时停中上线"例外，两者严重级别不同，故分列为error
    """
    cache = cache_control.cache
    if cache is None or not getattr(cache, "time_stop_mode", False):
        return []
    pl = _pl()
    if pl is None:
        return []
    u = _u(pl)
    if u == 3:
        return []
    return [
        make_failure(
            "MIND-01",
            "时停开启时玩家处于时停无意识",
            f"时停开启(time_stop_mode=True)但玩家sp_flag.unconscious_h={u}(应为3)，"
            f"behavior_id={_behavior_id(pl)}，累计时停时长={getattr(getattr(cache, 'achievement', None), 'time_stop_duration', '?')}",
            [0],
        )
    ]


@register_check("MIND-02", "时停开启时已登场干员处于时停无意识")
def check_time_stop_npc_unconscious() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]
    功能:
        校验时停开启时全体已登场干员的unconscious_h均为3；漏掉的干员会被AI与指令前提当作可正常交互对象。
        已知合法例外——时停中角色上线：handle_chara_on_line整体重建sp_flag(unconscious_h归0)，
        8个调用点里nation_diplomacy_panel.py/navigation_panel.py/character_handle.py没有补写3，
        故聚合上报并标为warning，不逐角色刷屏
    """
    cache = cache_control.cache
    if cache is None or not getattr(cache, "time_stop_mode", False):
        return []
    hits = []
    for cid, chara in _iter_npcs():
        u = _u(chara)
        if u != 3:
            hits.append((cid, _name(chara), u, _behavior_id(chara), getattr(chara, "position", "?")))
    if not hits:
        return []
    sample = "; ".join(f"cid={h[0]}({h[1]}) unconscious_h={h[2]} behavior={h[3]} position={h[4]}" for h in hits[:5])
    return [
        make_failure(
            "MIND-02",
            "时停开启时已登场干员处于时停无意识",
            f"[warning] 时停开启但共{len(hits)}名已登场干员unconscious_h≠3(已知合法例外:时停中上线未补写3，"
            f"见外交/导航面板调用点): {sample}{' ...' if len(hits) > 5 else ''}",
            [h[0] for h in hits],
        )
    ]


@register_check("MIND-03", "时停关闭后不得残留时停无意识")
def check_time_stop_off_no_residual() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]
    功能:
        校验TIME_STOP_OFF在同一次结算里先关time_stop_mode再清零npc_id_got|{0}的unconscious_h；
        残留的3会让角色被判为"完全无意识"永不行动，且可被玩家无限使用时停奸
        （InstructConfig.csv:5214前提仅T_UNCONSCIOUS_FLAG_3）
    """
    cache = cache_control.cache
    if cache is None or getattr(cache, "time_stop_mode", True):
        return []
    hits = []
    pl = _pl()
    if pl is not None and _u(pl) == 3:
        hits.append((0, _name(pl), _behavior_id(pl)))
    for cid, chara in _iter_npcs():
        if _u(chara) == 3:
            hits.append((cid, _name(chara), _behavior_id(chara)))
    if not hits:
        return []
    sample = "; ".join(f"cid={h[0]}({h[1]}) behavior={h[2]}" for h in hits[:5])
    return [
        make_failure(
            "MIND-03",
            "时停关闭后不得残留时停无意识",
            f"时停已关闭(time_stop_mode=False)但共{len(hits)}名角色unconscious_h仍为3(会被判为完全无意识永不行动): "
            f"{sample}{' ...' if len(hits) > 5 else ''}",
            [h[0] for h in hits],
        )
    ]


@register_check("MIND-04", "时停开启需要玩家持有窄域时停素质")
def check_time_stop_requires_talent_316() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]
    功能:
        校验时停开启时玩家持有素质316(唯一正常入口PRIMARY_TIME_STOP读素质316)；
        时停开着而玩家没有316，说明状态来自读档迁移/mod/debug。debug面板可在时停开启后删掉316，
        属明确调试例外，故加debug豁免
    """
    cache = cache_control.cache
    if cache is None or getattr(cache, "debug_mode", False) or not getattr(cache, "time_stop_mode", False):
        return []
    pl = _pl()
    if pl is None:
        return []
    if bool(_talent_get(pl, 316)):
        return []
    talents = {tid: _talent_get(pl, tid) for tid in (316, 317, 318)}
    return [
        make_failure(
            "MIND-04",
            "时停开启需要玩家持有窄域时停素质",
            f"[warning] 时停开启(time_stop_mode=True)但玩家未持有素质316: talent[316/317/318]={talents}",
            [0],
        )
    ]


@register_check("MIND-05", "时停搬运/自由活动字段在正常游戏中恒为零")
def check_time_stop_carry_free_fields_zero() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]
    功能:
        校验pl_ability.carry_chara_id_in_time_stop与pl_ability.free_in_time_stop_chara_id恒为0。
        写carry_chara_id_in_time_stop的效果1243在Behavior_Effect.csv零引用；写free_in_time_stop_chara_id
        的效果1245虽挂在行为945上，但对应指令前提含TO_DO，非debug下handle_todo返回0——
        两字段在当前版本正常玩法中写不出非零值，非零只可能来自旧存档/debug/mod，加debug豁免。
        carry_chara_id_in_time_stop已废弃，现行搬运用action_info.carry_chara_id(见MIND-07)
    """
    cache = cache_control.cache
    if cache is None or getattr(cache, "debug_mode", False):
        return []
    pl = _pl()
    if pl is None:
        return []
    pl_ability = getattr(pl, "pl_ability", None)
    carry = getattr(pl_ability, "carry_chara_id_in_time_stop", 0)
    free = getattr(pl_ability, "free_in_time_stop_chara_id", 0)
    if carry == 0 and free == 0:
        return []
    return [
        make_failure(
            "MIND-05",
            "时停搬运/自由活动字段在正常游戏中恒为零",
            f"[warning] 迁移/脏状态: carry_chara_id_in_time_stop={carry!r} free_in_time_stop_chara_id={free!r} "
            f"(均应恒为0，当前版本正常路径写不出非零值)，time_stop_mode={getattr(cache, 'time_stop_mode', '?')}，"
            f"action_info.carry_chara_id={getattr(getattr(pl, 'action_info', None), 'carry_chara_id', '?')}",
            [0],
        )
    ]


@register_check("MIND-06", "时停开启时不应残留时停解放标记")
def check_time_stop_no_residual_release_flag() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]
    功能:
        校验time_stop_mode开启时，全体存活的已登场干员h_state.time_stop_release均为False。
        该标记是关时停那一刻给全体NPC的一次性状态(效果527，与TIME_STOP_OFF挂在同一行为上)，
        活着的NPC在下一次行动前检查中会清回False；重开时停时还挂着它说明上一轮解放结算没走完。
        死亡角色在character_behavior.py直接return，标记会永久残留，必须豁免；
        效果527的循环显式跳过玩家(chara_id==0则continue)，故本式不覆盖玩家
    """
    cache = cache_control.cache
    if cache is None or not getattr(cache, "time_stop_mode", False):
        return []
    hits = []
    for cid, chara in _iter_npcs():
        if getattr(chara, "dead", False):
            continue
        h_state = getattr(chara, "h_state", None)
        if getattr(h_state, "time_stop_release", False):
            count = getattr(h_state, "time_stop_orgasm_count", {})
            nonzero = {k: v for k, v in count.items() if v} if isinstance(count, dict) else count
            hits.append((cid, _name(chara), nonzero))
    if not hits:
        return []
    sample = "; ".join(f"cid={h[0]}({h[1]}) time_stop_orgasm_count非零项={h[2]!r}" for h in hits[:5])
    return [
        make_failure(
            "MIND-06",
            "时停开启时不应残留时停解放标记",
            f"[warning] 时停重新开启但共{len(hits)}名存活干员h_state.time_stop_release仍为True(上一轮解放结算未走完): "
            f"{sample}{' ...' if len(hits) > 5 else ''}",
            [h[0] for h in hits],
        )
    ]


@register_check("MIND-07", "被搬运的干员必须存在且与玩家同地点")
def check_carry_target_valid_and_colocated() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]
    功能:
        校验pl.action_info.carry_chara_id指向的角色存在、未死亡且与玩家同地点。搬运期间玩家每次
        结算都会把被搬运者移动到玩家所在地点(handle_npc_ai_in_h.py，位于玩家分支内，回合边界上必定已执行)，
        地点不同步或cid无效即"凭空跟随"的幽灵角色。有意不检查"被搬运者仍处于异常6"——异常位6是可失效缓存，
        被搬运的睡眠干员自然睡醒后会被刷回"正常"而搬运不会自动停止，纳入会误报
    """
    cache = cache_control.cache
    if cache is None:
        return []
    pl = _pl()
    if pl is None:
        return []
    cid = getattr(getattr(pl, "action_info", None), "carry_chara_id", 0)
    if cid == 0:
        return []
    character_data = getattr(cache, "character_data", {})
    target = character_data.get(cid) if isinstance(character_data, dict) else None
    if target is not None and not getattr(target, "dead", False) and getattr(target, "position", None) == getattr(pl, "position", None):
        return []
    mask = _mask(target) if target is not None else None
    bit6 = mask[6] if mask is not None else "?"
    target_pos = getattr(target, "position", "?") if target is not None else "?"
    pl_pos = getattr(pl, "position", "?")
    if target is None:
        reason = "不存在"
    elif getattr(target, "dead", False):
        reason = "已死亡"
    else:
        reason = f"position={target_pos}与玩家position={pl_pos}不同"
    return [
        make_failure(
            "MIND-07",
            "被搬运的干员必须存在且与玩家同地点",
            f"玩家action_info.carry_chara_id={cid}指向的角色{reason}，"
            f"该角色unconscious_h={_u(target) if target is not None else '?'}，异常位6={bit6}",
            [0, cid],
        )
    ]


# ============================== 二、催眠 ==============================


@register_check("MIND-08", "催眠深度值域")
def check_hypnosis_degree_bound() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]
    功能:
        校验hypnosis.hypnosis_degree为非bool数值且落在[0, 200]内。正常增长路径是
        min(新值, hypnosis_degree_limit_calculation())，配置最高上限200(Hypnosis_Talent_Of_Pl.csv的
        max_hypnosis_degree)，越界值说明有旁路直接写入。有意不检查"不超过玩家当前能力上限"——
        新周目可按比例继承NPC催眠深度而玩家源石技艺可选择完全不继承，"NPC深度高于当前玩家上限"是合法快照。
        debug面板直接赋值hypnosis_degree无任何钳位，加debug豁免
    """
    cache = cache_control.cache
    if cache is None or getattr(cache, "debug_mode", False):
        return []
    failures = []
    for cid, chara in _iter_npcs():
        degree = getattr(getattr(chara, "hypnosis", None), "hypnosis_degree", None)
        if _num(degree) and 0 <= degree <= 200:
            continue
        talents = {tid: _talent_get(chara, tid) for tid in (331, 332, 333, 334)}
        failures.append(
            make_failure(
                "MIND-08",
                "催眠深度值域",
                f"[warning] 角色id={cid}({_name(chara)})的hypnosis.hypnosis_degree越界: {degree!r}(类型{type(degree).__name__}，合法范围[0,200])，玩家talent[331-334]={talents}",
                [cid],
            )
        )
    return failures


@register_check("MIND-09", "催眠类无意识状态需要对应的催眠深度")
def check_hypnosis_type_degree_threshold() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]
    功能:
        校验unconscious_h∈{4,5,6,7}(平然/空气/体控/心控)时催眠深度达到对应门槛(50/100/200/200，
        Hypnosis_Type.csv)。面板只在达标后才结算类型，深度不足却处于该状态说明状态被越级设置。
        这是近乎空真的纵深防御——对应通用效果在Behavior_Effect.csv零引用，也没有Python直接调用点，
        保留是为了挡mod/旧存档/未来剧情旁路，加debug豁免
    """
    cache = cache_control.cache
    if cache is None or getattr(cache, "debug_mode", False):
        return []
    thresholds = {4: 50, 5: 100, 6: 200, 7: 200}
    failures = []
    for cid, chara in _iter_npcs():
        u = _u(chara)
        if u not in thresholds:
            continue
        degree = getattr(getattr(chara, "hypnosis", None), "hypnosis_degree", 0)
        if _num(degree) and degree >= thresholds[u]:
            continue
        pl = _pl()
        failures.append(
            make_failure(
                "MIND-09",
                "催眠类无意识状态需要对应的催眠深度",
                f"[warning] 角色id={cid}({_name(chara)})unconscious_h={u}但hypnosis_degree={degree!r}未达门槛{thresholds[u]}，"
                f"玩家hypnosis_type={getattr(getattr(pl, 'pl_ability', None), 'hypnosis_type', '?') if pl is not None else '?'}，"
                f"talent[71/72/73]={ {tid: _talent_get(chara, tid) for tid in (71, 72, 73)} }",
                [cid],
            )
        )
    return failures


@register_check("MIND-10", "被催眠素质不早于深度阈值")
def check_hypnosis_talent_degree_order() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]
    功能:
        校验干员的被催眠素质71/72/73分别在深度达到50/100/200时才可能持有(Hypnosis_Talent_Of_Npc.csv)。
        有素质而深度不足，说明深度被回退或素质被越级授予。已核实新周目继承不构成合法反例——
        深度回填前先重建角色，talent不在回填之列会随之归零。唯一违反点是debug面板独立编辑素质与深度
    """
    cache = cache_control.cache
    if cache is None or getattr(cache, "debug_mode", False):
        return []
    failures = []
    for cid, chara in _iter_npcs():
        d = getattr(getattr(chara, "hypnosis", None), "hypnosis_degree", 0)
        if not _num(d):
            d = 0
        talents = {tid: _talent_get(chara, tid) for tid in (71, 72, 73)}
        ok = (not talents[71] or d >= 50) and (not talents[72] or d >= 100) and (not talents[73] or d >= 200)
        if not ok:
            failures.append(
                make_failure(
                    "MIND-10",
                    "被催眠素质不早于深度阈值",
                    f"[warning] 角色id={cid}({_name(chara)})的被催眠素质与深度失序: talent[71/72/73]={talents} hypnosis_degree={d!r}",
                    [cid],
                )
            )
    return failures


@register_check("MIND-11", "被催眠素质需要玩家持有对应前置素质")
def check_hypnosis_talent_requires_pl_prereq() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]
    功能:
        校验npc_gain_hypnosis_talent授予71/72/73前分别校验玩家的331/332/334(handle_talent.py)。
        干员有素质而玩家没有对应能力，说明素质来路不正。注意72的前置是332而73的前置是334(不是333)，
        以CSV为准。多周目会重建NPC素质，不构成合法反例，加debug豁免
    """
    cache = cache_control.cache
    if cache is None or getattr(cache, "debug_mode", False):
        return []
    pl = _pl()
    failures = []
    for cid, chara in _iter_npcs():
        talents = {tid: _talent_get(chara, tid) for tid in (71, 72, 73)}
        pl_talents = {tid: _talent_get(pl, tid) for tid in (331, 332, 334)} if pl is not None else {331: 0, 332: 0, 334: 0}
        ok = (not talents[71] or pl_talents[331]) and (not talents[72] or pl_talents[332]) and (not talents[73] or pl_talents[334])
        if not ok:
            failures.append(
                make_failure(
                    "MIND-11",
                    "被催眠素质需要玩家持有对应前置素质",
                    f"[warning] 角色id={cid}({_name(chara)})的talent[71/72/73]={talents}但玩家talent[331/332/334]={pl_talents}",
                    [cid],
                )
            )
    return failures


@register_check("MIND-12", "玩家催眠/时停素质链自洽")
def check_pl_talent_chain_consistency() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]
    功能:
        校验玩家素质链332←331、333←332、334←333(Hypnosis_Talent_Of_Pl.csv)、317←316、318←317
        (Talent_Of_Arts.csv)不存在跳级持有。正常购买界面校验need_id，新周目继承源石技艺时整体复制
        已持有项不会自造缺口，仅debug能造缺口
    """
    cache = cache_control.cache
    if cache is None or getattr(cache, "debug_mode", False):
        return []
    pl = _pl()
    if pl is None:
        return []
    pairs = [(332, 331), (333, 332), (334, 333), (317, 316), (318, 317)]
    bad = [(hi, lo) for hi, lo in pairs if _talent_get(pl, hi) and not _talent_get(pl, lo)]
    if not bad:
        return []
    talents = {tid: _talent_get(pl, tid) for tid in (316, 317, 318, 331, 332, 333, 334)}
    return [
        make_failure(
            "MIND-12",
            "玩家催眠/时停素质链自洽",
            f"[warning] 玩家素质链跳级持有: {bad}(要求hi蕴含lo)，talent[316-318,331-334]={talents}",
            [0],
        )
    ]


@register_check("MIND-13", "三种催眠行为模式互斥")
def check_hypnosis_behavior_mode_exclusive() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]
    功能:
        校验木头人blockhead/逆推active_h/角色扮演roleplay三个"行为主模式"至多一个生效。
        三个开启入口在写入前都调用clear_hypnosis_behavior_mode清理其余模式，两个同时为真会让
        H中AI逻辑(锁死不动 vs 主动逆推)互相打架。唯一违反点是debug面板逐项设置不执行清理，加debug豁免
    """
    cache = cache_control.cache
    if cache is None or getattr(cache, "debug_mode", False):
        return []
    failures = []
    for cid, chara in _iter_npcs():
        h = getattr(chara, "hypnosis", None)
        modes = [bool(getattr(h, "blockhead", False)), bool(getattr(h, "active_h", False)), bool(getattr(h, "roleplay", None))]
        if sum(modes) > 1:
            failures.append(
                make_failure(
                    "MIND-13",
                    "三种催眠行为模式互斥",
                    f"[warning] 角色id={cid}({_name(chara)})同时命中多个催眠行为模式: blockhead={modes[0]} active_h={modes[1]} roleplay非空={modes[2]}，"
                    f"unconscious_h={_u(chara)} behavior_id={_behavior_id(chara)}",
                    [cid],
                )
            )
    return failures


@register_check("MIND-14", "体控无意识必须由木头人或逆推支撑")
def check_body_control_unconscious_needs_mode() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]
    功能:
        校验unconscious_h==6(体控)时hypnosis.blockhead或hypnosis.active_h至少一个为真。
        u==6全仓只有木头人开启与逆推开启两个写入点，都在同一函数里连带写入对应模式标志，关闭效果也同步复位。
        方向已核实且不得写反：反方向(模式为真⇒u==6)会被时停开关、H结束整体重置h_state等合法路径打穿，
        故只做u==6⇒模式非空这一半
    """
    cache = cache_control.cache
    if cache is None or getattr(cache, "debug_mode", False):
        return []
    failures = []
    for cid, chara in _iter_npcs():
        if _u(chara) != 6:
            continue
        h = getattr(chara, "hypnosis", None)
        if getattr(h, "blockhead", False) or getattr(h, "active_h", False):
            continue
        h_state = getattr(chara, "h_state", None)
        failures.append(
            make_failure(
                "MIND-14",
                "体控无意识必须由木头人或逆推支撑",
                f"角色id={cid}({_name(chara)})unconscious_h=6但blockhead={getattr(h, 'blockhead', '?')} active_h={getattr(h, 'active_h', '?')} "
                f"roleplay={getattr(h, 'roleplay', '?')} h_state.npc_active_h={getattr(h_state, 'npc_active_h', '?')} "
                f"sp_flag.is_h={getattr(getattr(chara, 'sp_flag', None), 'is_h', '?')} time_stop_mode={getattr(cache, 'time_stop_mode', '?')} "
                f"behavior_id={_behavior_id(chara)}",
                [cid],
            )
        )
    return failures


@register_check("MIND-15", "心控无意识必须有角色扮演项")
def check_mind_control_unconscious_needs_roleplay() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]
    功能:
        校验unconscious_h==7(心控)时hypnosis.roleplay非空。u==7的唯一写入点是提交非空角色扮演列表
        的分支，提交空列表时同一函数会把7清回0，处于7却无扮演项说明列表被清而状态没跟上。
        只做单向(非空⇔7中的7⇒非空这一半)——心控效果会持续到玩家主动解除，而unconscious_h会被
        时停开关、睡眠猥亵、睡奸反复覆写，三者都不动roleplay，双向等价会被打穿
    """
    cache = cache_control.cache
    if cache is None or getattr(cache, "debug_mode", False):
        return []
    failures = []
    for cid, chara in _iter_npcs():
        if _u(chara) != 7:
            continue
        h = getattr(chara, "hypnosis", None)
        if getattr(h, "roleplay", None):
            continue
        failures.append(
            make_failure(
                "MIND-15",
                "心控无意识必须有角色扮演项",
                f"角色id={cid}({_name(chara)})unconscious_h=7但hypnosis.roleplay={getattr(h, 'roleplay', '?')!r}(应非空)，"
                f"blockhead={getattr(h, 'blockhead', '?')} active_h={getattr(h, 'active_h', '?')}",
                [cid],
            )
        )
    return failures


@register_check("MIND-16", "角色扮演列表的形状与内容合法")
def check_roleplay_list_shape() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]
    功能:
        校验hypnosis.roleplay是list，元素为正整数且均属于game_config.config_roleplay，且无重复。
        UI只append config_roleplay中的正整数cid，旧存档int被粗暴迁移成空列表；损坏/重复编号不会被
        MIND-13/MIND-15捕获，却会让角色信息面板与角色扮演前提读出无效项进而KeyError。
        config_roleplay在独立脚本环境下可能未加载，缺表时降级跳过；debug面板append无校验，加debug豁免
    """
    cache = cache_control.cache
    if cache is None or getattr(cache, "debug_mode", False):
        return []
    try:
        from Script.Config import game_config
    except Exception:
        return []
    roleplay_config = getattr(game_config, "config_roleplay", None)
    if not roleplay_config:
        return []
    failures = []
    for cid, chara in _iter_npcs():
        rp = getattr(getattr(chara, "hypnosis", None), "roleplay", None)
        if not isinstance(rp, list):
            failures.append(make_failure("MIND-16", "角色扮演列表的形状与内容合法", f"[warning] 角色id={cid}({_name(chara)})的hypnosis.roleplay不是list: {type(rp).__name__}", [cid]))
            continue
        bad_type = [x for x in rp if type(x) is not int or x <= 0]
        dup = sorted({x for x in rp if type(x) is int and rp.count(x) > 1})
        bad_id = [x for x in rp if type(x) is int and x > 0 and x not in roleplay_config]
        if bad_type or dup or bad_id:
            failures.append(
                make_failure(
                    "MIND-16",
                    "角色扮演列表的形状与内容合法",
                    f"[warning] 角色id={cid}({_name(chara)})的roleplay含非法内容: 非正整数项{bad_type} 重复项{dup} 不在config_roleplay中的编号{bad_id}，"
                    f"unconscious_h={_u(chara)}",
                    [cid],
                )
            )
    return failures


@register_check("MIND-17", "体控/心控子项需要「被完全催眠」素质")
def check_body_mind_control_sub_item_requires_talent_73() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]
    功能:
        校验六个体控/心控子项(增加敏感度/强制排卵/木头人/逆推/角色扮演/苦痛快感化)任一为真时角色必须
        持有素质73(被完全催眠)。四个直接指令都以TARGET_HAS_BEEN_COMPLETE_HYPNOSIS(素质73)为前提。
        本式会在一条完全合法的操作序列上触发，那是真实旁路而非误报：催眠面板的体控/心控子项直接调
        chara_handle_instruct_common_settle绕过InstructConfig前提，而npc_gain_hypnosis_talent每次调用
        授予一个素质后就break，于是干员首次达到200%时可能只拿到71却已能从面板开启子项。
        命中时应向游戏侧提bug，不要放宽本式；加debug豁免
    """
    cache = cache_control.cache
    if cache is None or getattr(cache, "debug_mode", False):
        return []
    failures = []
    for cid, chara in _iter_npcs():
        h = getattr(chara, "hypnosis", None)
        sub_items = {
            "increase_body_sensitivity": bool(getattr(h, "increase_body_sensitivity", False)),
            "force_ovulation": bool(getattr(h, "force_ovulation", False)),
            "blockhead": bool(getattr(h, "blockhead", False)),
            "active_h": bool(getattr(h, "active_h", False)),
            "roleplay": bool(getattr(h, "roleplay", None)),
            "pain_as_pleasure": bool(getattr(h, "pain_as_pleasure", False)),
        }
        if not any(sub_items.values()) or _talent_get(chara, 73):
            continue
        pl = _pl()
        failures.append(
            make_failure(
                "MIND-17",
                "体控/心控子项需要「被完全催眠」素质",
                f"角色id={cid}({_name(chara)})缺素质73但已开启子项{[k for k, v in sub_items.items() if v]}，"
                f"talent[71/72/73]={ {tid: _talent_get(chara, tid) for tid in (71, 72, 73)} }，"
                f"hypnosis_degree={getattr(h, 'hypnosis_degree', '?')}，"
                f"玩家hypnosis_type={getattr(getattr(pl, 'pl_ability', None), 'hypnosis_type', '?') if pl is not None else '?'}",
                [cid],
            )
        )
    return failures


@register_check("MIND-18", "空气催眠者必须与玩家同处已记录的催眠地点")
def check_air_hypnosis_colocated_with_anchor() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]
    功能:
        校验全体unconscious_h==5(空气催眠)的角色的position都等于共享锚点pl_ability.air_hypnosis_position
        且等于玩家当前position。进入空气催眠时把玩家当前位置记入该共享字段，玩家/NPC离开记录地点各自
        有清理路径。已知真实成因——集体催眠+单体解除：集体催眠可让多人同时进入5，而单人解除催眠/理智
        耗尽只清当前交互对象状态却把共享锚点整个置""，剩下的人立刻违反本式；该状态会在玩家离开该地点时
        自愈，故为warning。迭代范围有意不限于npc_id_got，访客也可能被催眠
    """
    cache = cache_control.cache
    if cache is None:
        return []
    pl = _pl()
    if pl is None:
        return []
    air = getattr(getattr(pl, "pl_ability", None), "air_hypnosis_position", "")
    pl_pos = getattr(pl, "position", None)
    hits = []
    for cid, chara in _iter_all():
        if _u(chara) != 5:
            continue
        pos = getattr(chara, "position", None)
        if isinstance(air, str) and air != "" and pos == air == pl_pos:
            continue
        hits.append((cid, _name(chara), pos))
    if not hits:
        return []
    sample = "; ".join(f"cid={h[0]}({h[1]}) position={h[2]}" for h in hits[:5])
    return [
        make_failure(
            "MIND-18",
            "空气催眠者必须与玩家同处已记录的催眠地点",
            f"[warning] 玩家position={pl_pos} air_hypnosis_position={air!r}，共{len(hits)}名unconscious_h=5的角色锚点/位置不一致"
            f"(已知成因:集体催眠+单体解除清空共享锚点): {sample}{' ...' if len(hits) > 5 else ''}",
            [h[0] for h in hits],
        )
    ]


@register_check("MIND-19", "空气催眠地点必须处于锁门状态")
def check_air_hypnosis_scene_locked() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]
    功能:
        校验unconscious_h==5的角色所在场景close_type==1(可锁门)且close_flag!=0(已锁门)。空气催眠只允许
        可锁门地点并在施放时强制锁门，仍有人处于5而门已开说明锁被别的结算解掉了。已知会命中的真实缺口：
        H结束效果会开门却不解除空气催眠，命中时应向游戏侧提缺口，故为warning而非直接放宽
    """
    cache = cache_control.cache
    if cache is None:
        return []
    scene_data = getattr(cache, "scene_data", None)
    if not isinstance(scene_data, dict):
        return []
    pl = _pl()
    failures = []
    for cid, chara in _iter_all():
        if _u(chara) != 5:
            continue
        key = _scene_key(getattr(chara, "position", None))
        scene = scene_data.get(key) if key is not None else None
        if scene is not None and getattr(scene, "close_type", 0) == 1 and getattr(scene, "close_flag", 0) != 0:
            continue
        failures.append(
            make_failure(
                "MIND-19",
                "空气催眠地点必须处于锁门状态",
                f"[warning] 角色id={cid}({_name(chara)})unconscious_h=5但所在场景{key!r}未处于锁门状态: "
                f"close_type={getattr(scene, 'close_type', '?') if scene is not None else '场景不存在'} "
                f"close_flag={getattr(scene, 'close_flag', '?') if scene is not None else '?'}，"
                f"玩家position={getattr(pl, 'position', '?') if pl is not None else '?'}，"
                f"air_hypnosis_position={getattr(getattr(pl, 'pl_ability', None), 'air_hypnosis_position', '?') if pl is not None else '?'}",
                [cid],
            )
        )
    return failures


@register_check("MIND-20", "空气催眠地点记录的形状可解析")
def check_air_hypnosis_anchor_shape() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]
    功能:
        校验pl_ability.air_hypnosis_position为""，或为可解析成合法场景的字符串list。字段类型注解是
        str=""，但当前成功路径赋的是position(List[str])，混入任意字符串会让位置比较永远失真，无法解析
        的路径还会让MIND-19取场景时KeyError。有意不写len(air)==2——场景路径不是固定两段
    """
    cache = cache_control.cache
    if cache is None:
        return []
    pl = _pl()
    if pl is None:
        return []
    air = getattr(getattr(pl, "pl_ability", None), "air_hypnosis_position", "")
    if air == "":
        return []
    scene_data = getattr(cache, "scene_data", None)
    key = _scene_key(air) if isinstance(air, list) else None
    ok = isinstance(air, list) and bool(air) and all(isinstance(x, str) for x in air) and isinstance(scene_data, dict) and key in scene_data
    if ok:
        return []
    has_air_u5 = any(_u(chara) == 5 for _, chara in _iter_all())
    return [
        make_failure(
            "MIND-20",
            "空气催眠地点记录的形状可解析",
            f"[warning] 玩家air_hypnosis_position无法解析成合法场景: 取值={air!r}(类型{type(air).__name__}) "
            f"scene_key={key!r}，玩家position={getattr(pl, 'position', '?')}，当前是否有u=5的角色={has_air_u5}",
            [0],
        )
    ]


@register_check("MIND-21", "玩家当前催眠类型合法且已解锁")
def check_pl_hypnosis_type_valid() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]
    功能:
        校验pl_ability.hypnosis_type∈{0,1,2,3,4}，且1需素质331、2需333、3/4需334(Hypnosis_Type.csv的
        talent_id列)。越界或未解锁的类型会让催眠完成判定去读不存在的配置或越级授予状态。类型0(无/每次
        手动选择)是字段默认值，必须豁免素质检查——CSV里类型0也写talent_id=331，但没有331的新玩家合法地
        处于0。类型2(空气)的前置是333而非332，以CSV为准
    """
    cache = cache_control.cache
    if cache is None or getattr(cache, "debug_mode", False):
        return []
    pl = _pl()
    if pl is None:
        return []
    t = getattr(getattr(pl, "pl_ability", None), "hypnosis_type", None)
    prereq = {1: 331, 2: 333, 3: 334, 4: 334}
    ok = isinstance(t, int) and not isinstance(t, bool) and t in (0, 1, 2, 3, 4) and (t == 0 or bool(_talent_get(pl, prereq[t])))
    if ok:
        return []
    talents = {tid: _talent_get(pl, tid) for tid in (331, 332, 333, 334)}
    return [
        make_failure(
            "MIND-21",
            "玩家当前催眠类型合法且已解锁",
            f"[warning] 玩家pl_ability.hypnosis_type={t!r}(类型{type(t).__name__})非法或未解锁对应前置素质，talent[331-334]={talents}",
            [0],
        )
    ]


# ============================== 三、无意识与睡眠 ==============================


@register_check("MIND-22", "无意识状态取值域")
def check_unconscious_h_range() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]
    功能:
        校验sp_flag.unconscious_h∈[0,7]。存档/schema护栏，越界值会让所有unconscious_flag_N前提全部
        落空，角色进入"既非正常也非任何已知无意识"的黑洞状态。全仓所有写入点都是0-7的字面量，
        当前代码下不可能失败，归入迁移/存档完整性组，按warning处理
    """
    failures = []
    for cid, chara in _iter_pl_and_npcs():
        u = getattr(getattr(chara, "sp_flag", None), "unconscious_h", None)
        if isinstance(u, bool) or not isinstance(u, int) or not (0 <= u <= 7):
            failures.append(
                make_failure(
                    "MIND-22",
                    "无意识状态取值域",
                    f"[warning] 角色id={cid}({_name(chara)})的sp_flag.unconscious_h越界: {u!r}，"
                    f"is_h={getattr(getattr(chara, 'sp_flag', None), 'is_h', '?')} behavior_id={_behavior_id(chara)} state={getattr(chara, 'state', '?')}",
                    [cid],
                )
            )
    return failures


@register_check("MIND-23", "睡眠行为与角色状态ID对齐")
def check_sleep_behavior_state_alignment() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]
    功能:
        校验behavior.behavior_id=="sleep"时state==111。设置睡眠的两处(玩家睡眠面板、NPC睡觉状态机)
        都同时写这两个字段，二者分裂会让行为驱动的睡眠结算与状态驱动的显示/事件对不上。只做单向，
        有意不写双条件——state会在其他场景被赋成字符串行为id，双向式会以"类型不符"而非"状态不同步"的
        形式失败。行为正常/强制结束时二者一起重置，不产生半态
    """
    failures = []
    for cid, chara in _iter_pl_and_npcs():
        if _behavior_id(chara) != "sleep":
            continue
        state = getattr(chara, "state", None)
        if state == 111:
            continue
        behavior = getattr(chara, "behavior", None)
        failures.append(
            make_failure(
                "MIND-23",
                "睡眠行为与角色状态ID对齐",
                f"角色id={cid}({_name(chara)})behavior_id=sleep但state={state!r}(类型{type(state).__name__}，应为111)，"
                f"start_time={getattr(behavior, 'start_time', '?')} duration={getattr(behavior, 'duration', '?')} sleep_point={getattr(chara, 'sleep_point', '?')}",
                [cid],
            )
        )
    return failures


@register_check("MIND-24", "熟睡值值域")
def check_sleep_point_bound() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]
    功能:
        校验sleep_point为非bool数值且落在[0,100]内(Sleep_Level.csv最高档上限100)。越界会让睡眠等级
        落入错误档位，负数尤其会被get_sleep_level判成"半梦半醒"。已实测判定值域可被打破——实时结算中
        add_sleep可为负，而白天分支只有下界、常规分支只有上界，负add_sleep能让最终值越出对侧边界，
        本式抓的是真bug；debug面板可直接改熟睡值，加debug豁免
    """
    cache = cache_control.cache
    if cache is None or getattr(cache, "debug_mode", False):
        return []
    failures = []
    for cid, chara in _iter_pl_and_npcs():
        sp = getattr(chara, "sleep_point", None)
        if _num(sp) and 0 <= sp <= 100:
            continue
        failures.append(
            make_failure(
                "MIND-24",
                "熟睡值值域",
                f"角色id={cid}({_name(chara)})的sleep_point越界: {sp!r}(合法范围[0,100])，"
                f"tired_point={getattr(chara, 'tired_point', '?')} behavior_id={_behavior_id(chara)} unconscious_h={_u(chara)}",
                [cid],
            )
        )
    return failures


@register_check("MIND-25", "睡眠无意识必须依附睡眠行为或装睡")
def check_sleep_unconscious_needs_sleep_or_pretend() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]
    功能:
        校验unconscious_h==1(睡眠)时behavior_id=="sleep"或h_state.pretend_sleep为真。进入睡奸/睡眠
        猥亵的前提都含T_ACTION_SLEEP，退出时unconscious_h归零；u==1却既不在睡也不在装睡，等于对一个
        清醒角色持续跑无意识H结算。pretend_sleep是必要的合法例外，即便该分支当前不可达(见MIND-30)也要
        保留。已知真实失败途径：睡奸中NPC睡眠行为自然到期时只重置behavior并刷新第5/6位，不动unconscious_h
    """
    failures = []
    for cid, chara in _iter_npcs():
        if _u(chara) != 1:
            continue
        if _behavior_id(chara) == "sleep" or getattr(getattr(chara, "h_state", None), "pretend_sleep", False):
            continue
        sp_flag = getattr(chara, "sp_flag", None)
        failures.append(
            make_failure(
                "MIND-25",
                "睡眠无意识必须依附睡眠行为或装睡",
                f"角色id={cid}({_name(chara)})unconscious_h=1但既不在sleep行为中也未装睡: behavior_id={_behavior_id(chara)} "
                f"pretend_sleep={getattr(getattr(chara, 'h_state', None), 'pretend_sleep', '?')} sleep_h_awake={getattr(sp_flag, 'sleep_h_awake', '?')} "
                f"sleep_point={getattr(chara, 'sleep_point', '?')} state={getattr(chara, 'state', '?')}",
                [cid],
            )
        )
    return failures


@register_check("MIND-26", "异常位掩码5/6不得与意识状态相矛盾")
def check_unnormal_flag_5_6_consistency() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]
    功能:
        校验时停模式/unconscious_h==3/5时若已知第6位则必须为异常，unconscious_h==4时若已知第5位则
        必须为异常。unnormal_flag把"异常1-7"的判定结果缓存成位掩码，只在显式调用settle_chara_unnormal_flag
        时刷新，是典型的失效缓存来源；缓存说"正常"而实际无意识，会让AI与指令前提把该角色当成可正常交互对象。
        三条必须保留的防误报措施：(1)排除玩家——_quick_check_normal_by_mask对cid 0恒返回"正常"，纳入会
        每个开时停回合恒假；(2)只查is_known的位，避开惰性缓存的合法unknown；(3)只做单向(无意识⇒该位为
        异常)，不反向要求，避免醉酒等级/睡眠等级等其他异常来源带来的误报
    """
    cache = cache_control.cache
    if cache is None:
        return []
    time_stop = getattr(cache, "time_stop_mode", False)
    failures = []
    for cid, chara in _iter_npcs():
        f = _mask(chara)
        if f is None:
            continue
        u = _u(chara)
        cond6 = (not f.is_known(6)) or not (u in (3, 5) or time_stop) or f[6]
        cond5 = (not f.is_known(5)) or u != 4 or f[5]
        if cond6 and cond5:
            continue
        failures.append(
            make_failure(
                "MIND-26",
                "异常位掩码5/6不得与意识状态相矛盾",
                f"角色id={cid}({_name(chara)})unconscious_h={u} time_stop_mode={time_stop}但unnormal_flag第5/6位与之矛盾: "
                f"第5位known={f.is_known(5)} val={f[5]}(cond5={cond5})，第6位known={f.is_known(6)} val={f[6]}(cond6={cond6})，"
                f"behavior_id={_behavior_id(chara)} sleep_point={getattr(chara, 'sleep_point', '?')} drunk_point={getattr(chara, 'drunk_point', '?')}",
                [cid],
            )
        )
    return failures


@register_check("MIND-27", "睡眠异常位与可推导的睡眠等级一致")
def check_sleep_unnormal_flag_matches_sleep_level() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]
    功能:
        校验正在睡眠(behavior_id=="sleep")或处于睡眠无意识(unconscious_h==1)的角色，已知的异常位5/6
        与熟睡等级一致：sleep_point<=30(等级0，半梦半醒)时第5位应为异常，>30(等级>=1)时第6位应为异常
        (handle_premise/__init__.py，0档上限30来自Sleep_Level.csv)。这是同一份缓存的另一条失效路径，
        实时结算在每次熟睡值变化后重算两位。同MIND-26，必须排除玩家并做dict保护，只查"应激活"方向
    """
    failures = []
    for cid, chara in _iter_npcs():
        f = _mask(chara)
        if f is None:
            continue
        if _behavior_id(chara) != "sleep" and _u(chara) != 1:
            continue
        sp = getattr(chara, "sleep_point", 0)
        if not _num(sp):
            continue
        if sp <= 30:
            ok = (not f.is_known(5)) or f[5]
        else:
            ok = (not f.is_known(6)) or f[6]
        if ok:
            continue
        failures.append(
            make_failure(
                "MIND-27",
                "睡眠异常位与可推导的睡眠等级一致",
                f"角色id={cid}({_name(chara)})sleep_point={sp} behavior_id={_behavior_id(chara)} unconscious_h={_u(chara)}"
                f"但对应异常位与睡眠等级不符: 第5位known={f.is_known(5)} val={f[5]}，第6位known={f.is_known(6)} val={f[6]}",
                [cid],
            )
        )
    return failures


@register_check("MIND-28", "时停高潮计数结构合法")
def check_time_stop_orgasm_count_shape() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]
    功能:
        校验h_state.time_stop_orgasm_count是dict，键为int、值为非负整数。存档/schema护栏，每个部位的
        时停高潮计数必须是非负整数，负数或非整数会破坏any(values())判定与解除时停时的高潮换算。
        当前代码下不可失败——键来自config_character_state的int主键，值来自orgasm_settle.py的
        += climax_count(两个非负int之和)，旧存档由setdefault补齐，归入迁移组，按warning处理
    """
    cache = cache_control.cache
    failures = []
    for cid, chara in _iter_npcs():
        h_state = getattr(chara, "h_state", None)
        d = getattr(h_state, "time_stop_orgasm_count", None)
        ok = isinstance(d, dict) and all(type(k) is int and _num(v) and v >= 0 for k, v in d.items())
        if not ok:
            failures.append(
                make_failure(
                    "MIND-28",
                    "时停高潮计数结构合法",
                    f"[warning] 角色id={cid}({_name(chara)})的h_state.time_stop_orgasm_count结构非法: {d!r}，"
                    f"time_stop_release={getattr(h_state, 'time_stop_release', '?')} time_stop_mode={getattr(cache, 'time_stop_mode', '?') if cache is not None else '?'}",
                    [cid],
                )
            )
    return failures


@register_check("MIND-29", "睡眠计划时分字段合法")
def check_sleep_plan_time_shape() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]
    功能:
        校验action_info.plan_to_sleep_time与plan_to_wake_time均为[时,分]形状的二元int列表，
        小时0-23、分钟0-59。存档/schema护栏，坏值会在datetime.replace()或AI时间比较处炸开。
        唯一写入点全部经过钳位且只写玩家(cid 0)，NPC永远保持默认[6,0]/[18,0]，当前代码下不可失败，
        归入迁移组，按warning处理
    """
    failures = []
    for cid, chara in _iter_pl_and_npcs():
        action_info = getattr(chara, "action_info", None)
        sleep_t = getattr(action_info, "plan_to_sleep_time", None)
        wake_t = getattr(action_info, "plan_to_wake_time", None)

        def _time_ok(t) -> bool:
            """检查单个[时,分]字段是否合法"""
            return isinstance(t, list) and len(t) == 2 and type(t[0]) is int and type(t[1]) is int and 0 <= t[0] <= 23 and 0 <= t[1] <= 59

        if _time_ok(sleep_t) and _time_ok(wake_t):
            continue
        failures.append(
            make_failure(
                "MIND-29",
                "睡眠计划时分字段合法",
                f"[warning] 角色id={cid}({_name(chara)})的睡眠计划时分字段非法: plan_to_sleep_time={sleep_t!r} plan_to_wake_time={wake_t!r}，"
                f"sleep_time={getattr(action_info, 'sleep_time', '?')} wake_time={getattr(action_info, 'wake_time', '?')}",
                [cid],
            )
        )
    return failures


@register_check("MIND-30", "装睡标记在当前版本不应出现")
def check_pretend_sleep_should_be_unreachable() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]
    功能:
        校验h_state.pretend_sleep恒为False。全仓只有一个写入点，而该分支因赋值顺序不可达：同函数内
        先调用judge_character_status_time_over(end_now=2)把behavior整体换成默认Behavior(behavior_id
        回到share_blankly)，导致后续两次handle_action_sleep判定必然为假。这是一条"死代码复活警报"，
        不是状态一致性断言——合取式版本(pretend_sleep⇒is_h and u==1)今天恒为空真，且一旦顺序bug被修好
        就立刻变成误报源(玩家离开场景会清is_h/unconscious_h却不重置h_state)，故只做"不应出现"这一半
    """
    failures = []
    for cid, chara in _iter_npcs():
        h_state = getattr(chara, "h_state", None)
        if not getattr(h_state, "pretend_sleep", False):
            continue
        sp_flag = getattr(chara, "sp_flag", None)
        failures.append(
            make_failure(
                "MIND-30",
                "装睡标记在当前版本不应出现",
                f"[warning] 角色id={cid}({_name(chara)})的h_state.pretend_sleep=True(当前版本该写入路径应不可达，属死代码复活警报): "
                f"is_h={getattr(sp_flag, 'is_h', '?')} unconscious_h={_u(chara)} behavior_id={_behavior_id(chara)} "
                f"sleep_h_awake={getattr(sp_flag, 'sleep_h_awake', '?')}",
                [cid],
            )
        )
    return failures
