# -*- coding: UTF-8 -*-
"""
静态检查系统 - H系统/群交/逆推/隐奸领域检查
本模块实现 HGROUP-01 ~ HGROUP-31 共31条不变量检查，来源为
final_invariants_h_group.md（H-xx + HS-xx 不变式清单）。

约定与踩坑说明（写在此处，避免散落在各检查函数注释里重复）：
1. `cid == 0` 恒为玩家角色(博士)。`NPCS = cache.npc_id_got - {0}`，`ALL = cache.npc_id_got | {0}`：
   统一用这两个集合而不是 `cache.character_data.keys()`——只有"已获得"角色会被结算逻辑写入，
   未获得角色可能带初始化/迁移残留数据。
2. "同场景" = `chara.position == pl.position`（position为List[str]）。
3. 隐奸模式1/2会主动把玩家is_h置False（hidden_sex_panel.py:439-441），凡以"玩家在H"为前提的
   检查都排除hidden_sex_mode!=0的情形；`ask_hidden_sex`效果链不含462，"隐奸模式3/4⇒玩家is_h"
   是假命题，本模块不实现该子句。
4. `target_character_id`可在H中被UI自由切换（无H守卫），任何条目都不把它当H绑定关系使用，
   只作为失败上下文里的诊断线索出现。
5. 时停回合完全跳过NPC结算（character_behavior.py NPC循环在time_stop_mode为真时break），
   凡依赖"NPC AI每回合自愈"的检查都用`not cache.time_stop_mode`守住。
6. 时停会把ALL全员(含玩家)的unconscious_h改写为3，关闭时全员写0，凡以unconscious_h为条件的
   检查在时停回合都换了语义，相关条目已加时停守卫或把该值放进失败上下文供triage。
7. 六九式(en_name sixty_nine)合法地同时占用mouth槽与侍奉槽，分类表把它归入"侍奉"组，
   HGROUP-09对mouth槽显式放行sixty_nine。
8. HGROUP-02/14/15使用警示级别(severity=warning)，消息前缀"[warning] "；HGROUP-02只诊断模式与人数不一致，
   不预设具体效果链成因，性技实操课允许仅1名学生。
9. 所有字段访问一律使用getattr/dict.get加默认值防御，绝不能因为老存档缺字段或类型不符而让
   检查器自身抛异常——异常本身会被框架转成"检查异常"记录，但这会掩盖真正的不变量证据。
"""
from typing import List, Optional, Set

from Script.Core import cache_control
from ..check_registry import CheckFailure, register_check, make_failure

try:
    from Script.Config import game_config
except Exception:  # pragma: no cover - 独立运行环境下Config包本身也可能不可导入
    game_config = None


# ---------------------------------------------------------------------------
# 公共辅助函数
# ---------------------------------------------------------------------------


def _pl(cache):
    """
    参数: cache 全局缓存对象
    返回值: 玩家角色对象(cid=0)，cache未初始化或0号角色不存在时返回None
    功能: 统一获取玩家角色对象
    """
    if cache is None:
        return None
    cd = getattr(cache, "character_data", None)
    if not isinstance(cd, dict):
        return None
    return cd.get(0)


def _npcs(cache) -> Set[int]:
    """
    参数: cache 全局缓存对象
    返回值: Set[int] 已获得的非玩家角色id集合，即npc_id_got - {0}
    功能: 提供不变式清单约定的NPCS集合，供各检查复用，避免每个检查函数各自求一遍差集
    """
    got = getattr(cache, "npc_id_got", None) if cache is not None else None
    if not got:
        return set()
    return set(got) - {0}


def _all(cache) -> Set[int]:
    """
    参数: cache 全局缓存对象
    返回值: Set[int] 已获得的全部角色id集合(含玩家)，即npc_id_got | {0}
    功能: 提供不变式清单约定的ALL集合，供各检查复用
    """
    got = getattr(cache, "npc_id_got", None) if cache is not None else None
    base = set(got) if got else set()
    return base | {0}


def _name(chara) -> str:
    """
    参数: chara 角色对象
    返回值: str 角色名，取不到时返回"?"
    功能: 防御式获取角色名用于拼接失败信息
    """
    return str(getattr(chara, "name", "?"))


def _behavior_id(chara) -> Optional[str]:
    """
    参数: chara 角色对象，允许为None
    返回值: Optional[str] 角色当前行为的behavior_id，取不到时返回None
    功能: 防御式获取角色当前行为id，用于失败上下文定位"上一条玩家/NPC指令"
    """
    if chara is None:
        return None
    b = getattr(chara, "behavior", None)
    return getattr(b, "behavior_id", None) if b is not None else None


def _pre_instr(cache) -> list:
    """
    参数: cache 全局缓存对象
    返回值: list 最近3条玩家行为指令(id)，字段缺失或非list时返回空列表
    功能: 防御式获取cache.pl_pre_behavior_instruce末尾3条，用于失败上下文定位"上一条玩家指令"
    """
    lst = getattr(cache, "pl_pre_behavior_instruce", None) if cache is not None else None
    if not isinstance(lst, list):
        return []
    return lst[-3:]


def _tpl_dict(pl):
    """
    参数: pl 玩家角色对象
    返回值: 玩家h_state.group_sex_body_template_dict，结构异常(非dict)时返回None
    功能: 统一取出玩家群交模板字典入口，供HGROUP-03~10共用，减少重复的getattr链
    """
    if pl is None:
        return None
    tpls = getattr(getattr(pl, "h_state", None), "group_sex_body_template_dict", None)
    return tpls if isinstance(tpls, dict) else None


def _group_sex_body_part_groups():
    """
    参数: 无
    返回值: (分组表, 行为配置表) 二元组；game_config包不可导入或对应数据未载入(独立脚本环境)时返回(None, None)
    功能: 统一获取HGROUP-09依赖的两张配置表，供该检查降级为跳过时判断
    """
    if game_config is None:
        return None, None
    g = getattr(game_config, "config_behavior_id_list_of_group_sex_body_part", None)
    cb = getattr(game_config, "config_behavior", None)
    if not g or not cb:
        return None, None
    return g, cb


# ---------------------------------------------------------------------------
# 一、群交
# ---------------------------------------------------------------------------


@register_check("HGROUP-01", "群交模式蕴含玩家在H")
def check_hgroup_01() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验cache.group_sex_mode为真时玩家必然带is_h标记：所有真正开启群交的效果链都同时给玩家挂462；
        若同时命中HGROUP-02，还存在群交模式与同场景在H的NPC人数不一致；本条不推断具体退出路径
    """
    cache = cache_control.cache
    pl = _pl(cache)
    if pl is None:
        return []
    if not getattr(cache, "group_sex_mode", False):
        return []
    if getattr(pl.sp_flag, "is_h", False):
        return []
    npcs = _npcs(cache)
    same_scene_h = [cid for cid in npcs if cid in cache.character_data and cache.character_data[cid].position == pl.position and getattr(cache.character_data[cid].sp_flag, "is_h", False)]
    msg = (
        f"cache.group_sex_mode=True但玩家(cid=0,{_name(pl)})sp_flag.is_h=False；behavior_id={_behavior_id(pl)} "
        f"state={getattr(pl, 'state', None)} 最近指令={_pre_instr(cache)} "
        f"group_sex_body_template_dict={getattr(pl.h_state, 'group_sex_body_template_dict', None)!r} 同场景在H角色id={same_scene_h}；"
        f"请同时查看HGROUP-02，确认同场景在H的NPC人数是否满足当前模式要求"
    )
    return [make_failure("HGROUP-01", "群交模式蕴含玩家在H", msg, [0])]


@register_check("HGROUP-02", "群交模式需满足场内在H的NPC人数")
def check_hgroup_02() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        [warning] 普通群交需同场景至少2名在H的NPC；性技实操课使用群交模式，但允许仅1名学生。
        模式开启而人数不足时报告当前状态，不把人数不足归因于某条效果链；两种模式下0名均不合法。
        时停守卫必需：时停回合玩家可离场且NPC不结算，按玩家当前场景计数会合法得到0
    """
    cache = cache_control.cache
    pl = _pl(cache)
    if pl is None:
        return []
    if not getattr(cache, "group_sex_mode", False) or getattr(cache, "time_stop_mode", False):
        return []
    npcs = _npcs(cache)
    in_h = []
    for cid in npcs:
        c = cache.character_data.get(cid)
        if c is None:
            continue
        if getattr(c.sp_flag, "is_h", False) and getattr(c, "position", None) == pl.position:
            in_h.append(c)
    sex_class_mode = getattr(cache, "sex_class_mode", False)
    minimum = 1 if sex_class_mode else 2
    if len(in_h) >= minimum:
        return []
    detail = [f"cid={c.cid} name={_name(c)} is_h={c.sp_flag.is_h} behavior_id={_behavior_id(c)} hit_point={getattr(c, 'hit_point', None)}" for c in in_h]
    msg = (
        f"[warning] cache.group_sex_mode=True但同场景在H的NPC数={len(in_h)}<{minimum}；sex_class_mode={sex_class_mode!r}；明细={detail}；"
        f"group_sex_body_template_dict={getattr(pl.h_state, 'group_sex_body_template_dict', None)!r} behavior_id={_behavior_id(pl)} 最近指令={_pre_instr(cache)}"
    )
    return [make_failure("HGROUP-02", "群交模式需满足场内在H的NPC人数", msg, [0] + [c.cid for c in in_h])]


@register_check("HGROUP-03", "非群交时玩家群交模板必须为空")
def check_hgroup_03() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验群交模式关闭时玩家A/B两套群交模板均已清空。群交结束会重置场景内全员h_state(含模板)，
        模式已关而模板非空说明某条退出路径漏了清理
    """
    cache = cache_control.cache
    pl = _pl(cache)
    if pl is None or getattr(cache, "group_sex_mode", False):
        return []
    tpls = _tpl_dict(pl)
    if tpls is None:
        return []
    failures = []
    for k in ("A", "B"):
        T = tpls.get(k)
        if not (isinstance(T, list) and len(T) == 2):
            continue  # 结构问题由HGROUP-04负责报告
        slots, serve = T
        if not isinstance(slots, dict):
            continue
        dirty_slots = {p: v for p, v in slots.items() if v != [-1, -1]}
        dirty_serve = serve != [[-1], -1]
        if dirty_slots or dirty_serve:
            failures.append(
                make_failure(
                    "HGROUP-03",
                    "非群交时玩家群交模板必须为空",
                    f"cache.group_sex_mode=False但玩家模板{k}未清空：单槽残留={dirty_slots} 侍奉={serve!r}；完整模板={tpls!r} "
                    f"behavior_id={_behavior_id(pl)} 最近指令={_pre_instr(cache)} group_sex_lock_flag={getattr(pl.h_state, 'group_sex_lock_flag', None)} "
                    f"all_group_sex_temple_run={getattr(pl.h_state, 'all_group_sex_temple_run', None)}",
                    [0],
                )
            )
    return failures


@register_check("HGROUP-04", "群交模板结构固定")
def check_hgroup_04() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验玩家群交模板字典恰含A/B两键，每套为[单槽字典,侍奉项]，单槽字典恰含5个部位键、每个单槽
        是长度2的列表，侍奉项是[list,state_id]。恒真型结构哨兵，成本极低，主要捕获旧存档迁移残留
    """
    cache = cache_control.cache
    pl = _pl(cache)
    if pl is None:
        return []
    tpls = getattr(getattr(pl, "h_state", None), "group_sex_body_template_dict", None)
    if not isinstance(tpls, dict):
        return [make_failure("HGROUP-04", "群交模板结构固定", f"玩家h_state.group_sex_body_template_dict不是dict: {type(tpls).__name__}", [0])]
    problems = []
    if set(tpls) != {"A", "B"}:
        problems.append(f"键集={sorted(tpls)}应为['A','B']")
    for k, T in tpls.items():
        if not (isinstance(T, list) and len(T) == 2):
            problems.append(f"模板{k}不是长度2的list: {T!r}")
            continue
        slots, serve = T
        if not isinstance(slots, dict) or set(slots) != {"mouth", "L_hand", "R_hand", "penis", "anal"}:
            problems.append(f"模板{k}单槽字典键集异常: {slots!r}")
        else:
            for p, v in slots.items():
                if not (isinstance(v, list) and len(v) == 2):
                    problems.append(f"模板{k}部位{p}不是长度2的list: {v!r}")
        if not (isinstance(serve, list) and len(serve) == 2 and isinstance(serve[0], list)):
            problems.append(f"模板{k}侍奉项结构异常: {serve!r}")
    if problems:
        return [make_failure("HGROUP-04", "群交模板结构固定", "; ".join(problems) + f"；完整模板={tpls!r}", [0])]
    return []


@register_check("HGROUP-05", "模板槽位不得半填")
def check_hgroup_05() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验单槽[对象id,指令id]不允许只填一半，侍奉项同理(有指令⇔列表不是[-1])。裁到"A + 启用时的B"：
        reset_unfinish_select只遍历A、B仅在all_group_sex_temple_run为真时才遍历，未启用的B可能长期
        留存半填槽
    """
    cache = cache_control.cache
    pl = _pl(cache)
    if pl is None:
        return []
    tpls = _tpl_dict(pl)
    if tpls is None:
        return []
    keys = ["A"]
    if getattr(pl.h_state, "all_group_sex_temple_run", False):
        keys.append("B")
    failures = []
    for k in keys:
        T = tpls.get(k)
        if not (isinstance(T, list) and len(T) == 2):
            continue
        slots, serve = T
        ctx = (
            f"group_sex_lock_flag={getattr(pl.h_state, 'group_sex_lock_flag', None)} "
            f"all_group_sex_temple_run={getattr(pl.h_state, 'all_group_sex_temple_run', None)} now_panel_id={getattr(cache, 'now_panel_id', None)}"
        )
        if isinstance(slots, dict):
            for p, v in slots.items():
                if not (isinstance(v, list) and len(v) == 2):
                    continue
                obj_id, state_id = v
                if (obj_id == -1) != (state_id == -1):
                    failures.append(make_failure("HGROUP-05", "模板槽位不得半填", f"模板{k}部位{p}半填: {v!r}；{ctx}", [0]))
        if isinstance(serve, list) and len(serve) == 2:
            ids, state_id = serve
            if (state_id == -1) != (ids == [-1]):
                failures.append(make_failure("HGROUP-05", "模板槽位不得半填", f"模板{k}侍奉项半填: {serve!r}；{ctx}", [0]))
    return failures


@register_check("HGROUP-06", "阴茎插入与侍奉互斥")
def check_hgroup_06() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验同一模板内penis槽与侍奉槽不能同时被占用。三条写入路径都维持互斥；六九式不是例外——
        它落在"侍奉"分组，走先清penis的分支，特例代码之后也没再动penis
    """
    cache = cache_control.cache
    pl = _pl(cache)
    if pl is None:
        return []
    tpls = _tpl_dict(pl)
    if tpls is None:
        return []
    failures = []
    for k in ("A", "B"):
        T = tpls.get(k)
        if not (isinstance(T, list) and len(T) == 2):
            continue
        slots, serve = T
        if not isinstance(slots, dict) or not (isinstance(serve, list) and len(serve) == 2):
            continue
        penis = slots.get("penis")
        if not (isinstance(penis, list) and len(penis) == 2):
            continue
        if penis[1] != -1 and serve[1] != -1:
            failures.append(
                make_failure(
                    "HGROUP-06",
                    "阴茎插入与侍奉互斥",
                    f"模板{k}同时占用penis={penis!r}与侍奉={serve!r}；behavior_id={_behavior_id(pl)} group_sex_lock_flag={getattr(pl.h_state, 'group_sex_lock_flag', None)}",
                    [0],
                )
            )
    return failures


@register_check("HGROUP-07", "侍奉槽结构与去重（不含人数上限）")
def check_hgroup_07() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验侍奉项要么是占位态[[-1],-1]，要么是"≥1个互不重复、均非-1的角色id + 非-1指令id"。
        绝不加回len(ids)<=4：4人上限只是UI约束，自动记录路径group_sex_settle对同一侍奉指令的
        新对象只做append且没有任何上限，5人以上群交可合法得到长度5
    """
    cache = cache_control.cache
    pl = _pl(cache)
    if pl is None:
        return []
    tpls = _tpl_dict(pl)
    if tpls is None:
        return []
    keys = ["A"]
    if getattr(pl.h_state, "all_group_sex_temple_run", False):
        keys.append("B")
    failures = []
    for k in keys:
        T = tpls.get(k)
        if not (isinstance(T, list) and len(T) == 2):
            continue
        _, serve = T
        if not (isinstance(serve, list) and len(serve) == 2):
            continue
        ids, state = serve
        if not isinstance(ids, list):
            continue
        ok_empty = ids == [-1] and state == -1
        ok_filled = len(ids) >= 1 and -1 not in ids and len(ids) == len(set(ids)) and state != -1
        if not (ok_empty or ok_filled):
            failures.append(
                make_failure(
                    "HGROUP-07",
                    "侍奉槽结构与去重（不含人数上限）",
                    f"模板{k}侍奉项非法: {serve!r}；cache.group_sex_mode={getattr(cache, 'group_sex_mode', None)} "
                    f"npc_ai_type_in_group_sex={getattr(pl.h_state, 'npc_ai_type_in_group_sex', None)} group_sex_lock_flag={getattr(pl.h_state, 'group_sex_lock_flag', None)}",
                    [0],
                )
            )
    return failures


@register_check("HGROUP-08", "模板中的角色必须是已获得NPC、在H、且同场景")
def check_hgroup_08() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验A/B模板中出现的每个非-1角色id，必须是已获得的非玩家角色，且正处于H并与玩家同场景。
        模板会被直接用于生成结算目标，残留已退场角色会让settle_behavior对不在场角色结算H行为。
        已知可命中的真泄漏：NPC离场清理只清is_h，不清模板，群交成员被弄出场景会留下陈旧id
    """
    cache = cache_control.cache
    pl = _pl(cache)
    if pl is None:
        return []
    tpls = _tpl_dict(pl)
    if tpls is None:
        return []
    npc_id_got = getattr(cache, "npc_id_got", None) or set()
    time_stop = getattr(cache, "time_stop_mode", False)
    ids = set()
    for k in ("A", "B"):
        T = tpls.get(k)
        if not (isinstance(T, list) and len(T) == 2):
            continue
        slots, serve = T
        if isinstance(slots, dict):
            for v in slots.values():
                if isinstance(v, list) and len(v) == 2 and v[0] != -1:
                    ids.add(v[0])
        if isinstance(serve, list) and len(serve) == 2 and isinstance(serve[0], list):
            for c in serve[0]:
                if c != -1:
                    ids.add(c)
    failures = []
    for c in ids:
        if c == 0 or c not in npc_id_got or c not in cache.character_data:
            failures.append(
                make_failure(
                    "HGROUP-08",
                    "模板中的角色必须是已获得NPC、在H、且同场景",
                    f"模板引用角色id={c}不是已获得的非玩家角色(npc_id_got成员={c in npc_id_got}, character_data成员={c in cache.character_data})；"
                    f"完整模板={tpls!r} cache.group_sex_mode={getattr(cache, 'group_sex_mode', None)} pl.position={pl.position}",
                    [c] if c != 0 else [0],
                )
            )
            continue
        chara = cache.character_data[c]
        if not getattr(chara.sp_flag, "is_h", False):
            failures.append(
                make_failure(
                    "HGROUP-08",
                    "模板中的角色必须是已获得NPC、在H、且同场景",
                    f"模板引用角色cid={c}({_name(chara)})不在H(is_h=False)；position={chara.position} behavior_id={_behavior_id(chara)}；"
                    f"完整模板={tpls!r} cache.group_sex_mode={getattr(cache, 'group_sex_mode', None)}",
                    [c],
                )
            )
        if not time_stop and getattr(chara, "position", None) != pl.position:
            failures.append(
                make_failure(
                    "HGROUP-08",
                    "模板中的角色必须是已获得NPC、在H、且同场景",
                    f"模板引用角色cid={c}({_name(chara)})不与玩家同场景: position={chara.position} pl.position={pl.position}；is_h={getattr(chara.sp_flag, 'is_h', None)} "
                    f"behavior_id={_behavior_id(chara)}；完整模板={tpls!r} cache.group_sex_mode={getattr(cache, 'group_sex_mode', None)}",
                    [c],
                )
            )
    return failures


@register_check("HGROUP-09", "模板指令id必须存在且匹配所占部位")
def check_hgroup_09() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验每个非-1的指令id必须存在于game_config.config_behavior，且属于该槽位对应的分组：
        mouth→口、L_hand/R_hand→手、penis→插入、anal→肛、侍奉槽→侍奉；mouth额外放行六九式(sixty_nine)，
        因其tag先命中"侍奉"被分类为侍奉组，但特例代码把它写进mouth槽。config表未载入(独立脚本环境)时降级为跳过
    """
    cache = cache_control.cache
    pl = _pl(cache)
    if pl is None:
        return []
    g, cb = _group_sex_body_part_groups()
    if g is None:
        return []  # 配置未加载，降级为跳过
    tpls = _tpl_dict(pl)
    if tpls is None:
        return []
    allowed = {
        "mouth": set(g.get("口", [])) | {"sixty_nine"},
        "L_hand": set(g.get("手", [])),
        "R_hand": set(g.get("手", [])),
        "penis": set(g.get("插入", [])),
        "anal": set(g.get("肛", [])),
    }
    serve_allowed = set(g.get("侍奉", []))
    failures = []
    for k in ("A", "B"):
        T = tpls.get(k)
        if not (isinstance(T, list) and len(T) == 2):
            continue
        slots, serve = T
        if isinstance(slots, dict):
            for p, v in slots.items():
                if not (isinstance(v, list) and len(v) == 2):
                    continue
                s = v[1]
                if s == -1:
                    continue
                exists = s in cb
                in_group = exists and s in allowed.get(p, set())
                if not (exists and in_group):
                    tag = getattr(cb.get(s), "tag", None) if exists else None
                    name = getattr(cb.get(s), "name", None) if exists else None
                    failures.append(
                        make_failure(
                            "HGROUP-09",
                            "模板指令id必须存在且匹配所占部位",
                            f"模板{k}部位{p}指令id={s!r}: 存在于config_behavior={exists}, tag={tag!r}, name={name!r}, 期望分组={p}；完整模板={tpls!r}",
                            [0],
                        )
                    )
        if isinstance(serve, list) and len(serve) == 2:
            s = serve[1]
            if s != -1:
                exists = s in cb
                in_group = exists and s in serve_allowed
                if not (exists and in_group):
                    tag = getattr(cb.get(s), "tag", None) if exists else None
                    name = getattr(cb.get(s), "name", None) if exists else None
                    failures.append(
                        make_failure(
                            "HGROUP-09",
                            "模板指令id必须存在且匹配所占部位",
                            f"模板{k}侍奉槽指令id={s!r}: 存在于config_behavior={exists}, tag={tag!r}, name={name!r}, 期望分组=侍奉；完整模板={tpls!r}",
                            [0],
                        )
                    )
    return failures


@register_check("HGROUP-10", "群交控制字段的值域与所有权")
def check_hgroup_10() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验三个群交全局开关只从玩家身上读写：玩家npc_ai_type_in_group_sex只能是0..3，两个flag必须是
        bool，NPC身上必须保持默认值。属于串写哨兵，正常游戏中恒真——若将来真给NPC侧加了写入，本条会先报
    """
    cache = cache_control.cache
    pl = _pl(cache)
    if pl is None:
        return []
    h = pl.h_state
    failures = []
    ai = getattr(h, "npc_ai_type_in_group_sex", None)
    if ai not in (0, 1, 2, 3):
        failures.append(
            make_failure(
                "HGROUP-10",
                "群交控制字段的值域与所有权",
                f"玩家npc_ai_type_in_group_sex={ai!r}越界(应为0..3)；cache.group_sex_mode={getattr(cache, 'group_sex_mode', None)} behavior_id={_behavior_id(pl)}",
                [0],
            )
        )
    lock = getattr(h, "group_sex_lock_flag", None)
    run = getattr(h, "all_group_sex_temple_run", None)
    if type(lock) is not bool or type(run) is not bool:
        failures.append(
            make_failure(
                "HGROUP-10",
                "群交控制字段的值域与所有权",
                f"玩家group_sex_lock_flag={lock!r}(type={type(lock).__name__})或all_group_sex_temple_run={run!r}(type={type(run).__name__})不是bool",
                [0],
            )
        )
    npcs = _npcs(cache)
    for cid in npcs:
        c = cache.character_data.get(cid)
        if c is None:
            continue
        hs = c.h_state
        bad = []
        if getattr(hs, "npc_ai_type_in_group_sex", 0) != 0:
            bad.append(f"npc_ai_type_in_group_sex={hs.npc_ai_type_in_group_sex!r}")
        if getattr(hs, "all_group_sex_temple_run", False) is not False:
            bad.append(f"all_group_sex_temple_run={hs.all_group_sex_temple_run!r}")
        if getattr(hs, "group_sex_lock_flag", False) is not False:
            bad.append(f"group_sex_lock_flag={hs.group_sex_lock_flag!r}")
        if bad:
            failures.append(
                make_failure(
                    "HGROUP-10",
                    "群交控制字段的值域与所有权",
                    f"NPC cid={cid}({_name(c)})的群交控制字段偏离默认值: {'; '.join(bad)}；cache.group_sex_mode={getattr(cache, 'group_sex_mode', None)}",
                    [cid],
                )
            )
    return failures


@register_check("HGROUP-11", "NPC自身的群交模板必须为空")
def check_hgroup_11() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验群交模板虽挂在所有角色h_state上，但业务上只读写玩家(cid=0)的模板；NPC模板出现非空槽
        即为串写或旧状态未清。串写哨兵，成本低，唯一潜在写入者是旧存档迁移
    """
    cache = cache_control.cache
    if cache is None:
        return []
    npcs = _npcs(cache)
    failures = []
    for cid in npcs:
        c = cache.character_data.get(cid)
        if c is None:
            continue
        tpls = getattr(c.h_state, "group_sex_body_template_dict", None)
        if not isinstance(tpls, dict):
            continue
        for k, T in tpls.items():
            if not (isinstance(T, list) and len(T) == 2):
                continue
            slots, serve = T
            dirty_slots = isinstance(slots, dict) and any(v != [-1, -1] for v in slots.values())
            dirty_serve = serve != [[-1], -1]
            if dirty_slots or dirty_serve:
                failures.append(
                    make_failure(
                        "HGROUP-11",
                        "NPC自身的群交模板必须为空",
                        f"NPC cid={cid}({_name(c)})模板{k}非空: {T!r}；is_h={getattr(c.sp_flag, 'is_h', None)} cache.group_sex_mode={getattr(cache, 'group_sex_mode', None)}",
                        [cid],
                    )
                )
    return failures


@register_check("HGROUP-12", "「群交自慰」标记的成立条件")
def check_hgroup_12() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验sp_flag.masturebate==3只能出现在群交开启、在H、与玩家同场景的非玩家角色身上。三处置位点
        全在群交AI内且前置is_h==False或群交模式关则return。已知可命中的真泄漏：群交中有人从无意识
        恢复时先关group_sex_mode再清理其余角色，但清理函数不清masturebate⇒关群交后3值残留
    """
    cache = cache_control.cache
    pl = _pl(cache)
    if pl is None:
        return []
    all_ids = _all(cache)
    time_stop = getattr(cache, "time_stop_mode", False)
    failures = []
    for cid in all_ids:
        c = cache.character_data.get(cid)
        if c is None:
            continue
        if getattr(c.sp_flag, "masturebate", 0) != 3:
            continue
        if cid == 0:
            failures.append(
                make_failure(
                    "HGROUP-12",
                    "「群交自慰」标记的成立条件",
                    f"玩家(cid=0)自身masturebate=3，该值只应出现在NPC身上；cache.group_sex_mode={getattr(cache, 'group_sex_mode', None)}",
                    [0],
                )
            )
            continue
        bad = []
        if not getattr(cache, "group_sex_mode", False):
            bad.append("cache.group_sex_mode=False")
        if not getattr(c.sp_flag, "is_h", False):
            bad.append("is_h=False")
        if not time_stop and getattr(c, "position", None) != pl.position:
            bad.append(f"position={c.position}!=pl.position={pl.position}")
        if bad:
            failures.append(
                make_failure(
                    "HGROUP-12",
                    "「群交自慰」标记的成立条件",
                    f"NPC cid={cid}({_name(c)})masturebate=3但{'; '.join(bad)}；npc_ai_type_in_group_sex={getattr(pl.h_state, 'npc_ai_type_in_group_sex', None)} "
                    f"behavior_id={_behavior_id(c)}",
                    [cid],
                )
            )
    return failures


@register_check("HGROUP-13", "玩家不得带有「前往参与群交」标记")
def check_hgroup_13() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验玩家sp_flag.go_to_join_group_sex恒为False：该标记是给"被邀请、正从远处赶来"的NPC用的，
        置位点只有群交邀请面板与SELF_JOIN_GROUP_SEX_ON，都作用在被邀请的NPC上，玩家自己永远不该带
    """
    cache = cache_control.cache
    pl = _pl(cache)
    if pl is None:
        return []
    if getattr(pl.sp_flag, "go_to_join_group_sex", False):
        return [
            make_failure(
                "HGROUP-13",
                "玩家不得带有「前往参与群交」标记",
                f"玩家(cid=0)sp_flag.go_to_join_group_sex=True；behavior_id={_behavior_id(pl)} cache.group_sex_mode={getattr(cache, 'group_sex_mode', None)} 最近指令={_pre_instr(cache)}",
                [0],
            )
        ]
    return []


@register_check("HGROUP-14", "「前往参与群交」标记的生命周期")
def check_hgroup_14() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        [warning已知泄漏探测器] 带go_to_join_group_sex标记的NPC应处在"群交仍开着、自己尚未进入H、
        尚未到达玩家场景"的途中状态。已知泄漏：group_sex_end的407只覆盖玩家所在场景的角色，仍在路上
        的受邀NPC不在场景内，会带着该标记残留而group_sex_mode已为False——"提前结束群交"是常见操作，
        故频次高、定为warning
    """
    cache = cache_control.cache
    pl = _pl(cache)
    if pl is None:
        return []
    time_stop = getattr(cache, "time_stop_mode", False)
    npcs = _npcs(cache)
    failures = []
    for cid in npcs:
        c = cache.character_data.get(cid)
        if c is None:
            continue
        if not getattr(c.sp_flag, "go_to_join_group_sex", False):
            continue
        bad = []
        if not getattr(cache, "group_sex_mode", False):
            bad.append("cache.group_sex_mode=False(已知bug: group_sex_end的407只清玩家所在场景成员，途中受邀NPC残留标记)")
        if getattr(c.sp_flag, "is_h", False):
            bad.append("is_h=True")
        if not time_stop and getattr(c, "position", None) == pl.position:
            bad.append("position==pl.position(已到场未清)")
        if bad:
            second_behavior = getattr(c, "second_behavior", None)
            invited = second_behavior.get("be_invited_join_group_sex") if isinstance(second_behavior, dict) else None
            failures.append(
                make_failure(
                    "HGROUP-14",
                    "「前往参与群交」标记的生命周期",
                    f"[warning] NPC cid={cid}({_name(c)})go_to_join_group_sex=True但{'; '.join(bad)}；position={c.position} pl.position={pl.position} "
                    f"behavior_id={_behavior_id(c)} state={getattr(c, 'state', None)} be_invited_join_group_sex={invited} game_time={getattr(cache, 'game_time', None)}",
                    [cid],
                )
            )
    return failures


# ---------------------------------------------------------------------------
# 二、隐奸与露出
# ---------------------------------------------------------------------------


@register_check("HGROUP-15", "隐奸模式必须双向一致且至多一对")
def check_hgroup_15() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        [warning已知bug探测器] 进入隐奸时玩家与对象被写入同一个hidden_sex_mode值，隐奸恒为"玩家+
        恰好一名NPC"的对称状态。已知泄漏：settle_discovered只清调用者(玩家)一侧的hidden_sex_mode，
        被发现面板的"[1]用花言巧语支开对方"分支判定通过后直接结束流程，NPC的hidden_sex_mode永久
        残留而玩家已归0。不得把"隐奸NPC必须等于pl.target_character_id"加回来：切换交互对象是无H
        守卫的自由UI动作
    """
    cache = cache_control.cache
    pl = _pl(cache)
    if pl is None:
        return []
    m = getattr(pl.sp_flag, "hidden_sex_mode", 0)
    npcs = _npcs(cache)
    hidden = []
    for cid in npcs:
        c = cache.character_data.get(cid)
        if c is None:
            continue
        if getattr(c.sp_flag, "hidden_sex_mode", 0) > 0:
            hidden.append(c)

    def _ctx():
        detail = [f"cid={h.cid} name={_name(h)} position={h.position} mode={h.sp_flag.hidden_sex_mode} is_h={h.sp_flag.is_h} behavior_id={_behavior_id(h)}" for h in hidden]
        return (
            f"pl.hidden_sex_mode={m} 明细={detail} pl.position={pl.position} "
            f"hidden_sex_discovery_dregree={getattr(pl.h_state, 'hidden_sex_discovery_dregree', None)} behavior_id={_behavior_id(pl)} 最近指令={_pre_instr(cache)}；"
            "可观察后果：玩家模式为3/4（男隐/双隐）且场内无任何隐奸对象时，指令面板对每个指令类型执行continue；当前对象非隐奸对象时整类指令被跳过"
        )

    failures = []
    known_bug = "已知bug探测(settle_discovered只清玩家一侧hidden_sex_mode，『用花言巧语支开对方』分支未收口NPC侧)"
    if len(hidden) > 1:
        failures.append(
            make_failure("HGROUP-15", "隐奸模式必须双向一致且至多一对", f"[warning] {known_bug}：同时有{len(hidden)}名NPC带hidden_sex_mode>0，应至多1名；{_ctx()}", [c.cid for c in hidden])
        )
        return failures
    if m > 0:
        if len(hidden) != 1:
            failures.append(make_failure("HGROUP-15", "隐奸模式必须双向一致且至多一对", f"[warning] {known_bug}：玩家hidden_sex_mode={m}>0但同场景带对应模式的NPC数={len(hidden)}!=1；{_ctx()}", [0]))
        else:
            t = hidden[0]
            if getattr(t.sp_flag, "hidden_sex_mode", None) != m:
                failures.append(make_failure("HGROUP-15", "隐奸模式必须双向一致且至多一对", f"[warning] 隐奸模式不对称：玩家={m} NPC cid={t.cid}({_name(t)})={t.sp_flag.hidden_sex_mode}；{_ctx()}", [0, t.cid]))
            if not getattr(cache, "time_stop_mode", False) and getattr(t, "position", None) != pl.position:
                failures.append(
                    make_failure(
                        "HGROUP-15", "隐奸模式必须双向一致且至多一对", f"[warning] 隐奸对象不同场景：cid={t.cid}({_name(t)}) position={t.position} pl.position={pl.position}；{_ctx()}", [0, t.cid]
                    )
                )
    else:
        if hidden:
            failures.append(make_failure("HGROUP-15", "隐奸模式必须双向一致且至多一对", f"[warning] {known_bug}：玩家hidden_sex_mode=0但存在带该模式的NPC；{_ctx()}", [c.cid for c in hidden]))
    return failures


@register_check("HGROUP-16", "隐奸对象在H；模式1/2时玩家不在H")
def check_hgroup_16() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验ask_hidden_sex带464使对象进入H；选择模式1/2(博士不隐藏)时面板会主动清掉玩家自己的H
        标记。"模式3/4⇒玩家is_h"已被证伪，不实现该子句。已知可达的误报路径(登记为已知可触发，不因此
        删条)：隐奸模式1/2下玩家is_h=False，切换交互对象到非H第三者后NOT_H成立，ask_exhibitionism_sex
        可用，其效果链带462⇒玩家重新is_h=True而隐奸模式仍是1/2，命中时先看exhibitionism_sex_mode
        是否非0来区分
    """
    cache = cache_control.cache
    pl = _pl(cache)
    if pl is None:
        return []
    m = getattr(pl.sp_flag, "hidden_sex_mode", 0)
    if m <= 0:
        return []
    npcs = _npcs(cache)
    failures = []
    for cid in npcs:
        c = cache.character_data.get(cid)
        if c is None:
            continue
        if getattr(c.sp_flag, "hidden_sex_mode", 0) > 0 and not getattr(c.sp_flag, "is_h", False):
            failures.append(
                make_failure(
                    "HGROUP-16",
                    "隐奸对象在H；模式1/2时玩家不在H",
                    f"隐奸模式={m}下NPC cid={cid}({_name(c)})hidden_sex_mode={c.sp_flag.hidden_sex_mode}但is_h=False；behavior_id={_behavior_id(c)} 最近指令={_pre_instr(cache)}",
                    [cid],
                )
            )
    if m in (1, 2) and getattr(pl.sp_flag, "is_h", False):
        exhib = getattr(pl.sp_flag, "exhibitionism_sex_mode", 0)
        failures.append(
            make_failure(
                "HGROUP-16",
                "隐奸对象在H；模式1/2时玩家不在H",
                f"隐奸模式={m}(博士不隐藏)下玩家is_h=True，应已被清空；exhibitionism_sex_mode={exhib}(若非0，疑为切换对象后走"
                f"ask_exhibitionism_sex重新进H，属已知可达误报路径，非本条描述的泄漏)；behavior_id={_behavior_id(pl)} target_character_id={pl.target_character_id} "
                f"最近指令={_pre_instr(cache)}",
                [0],
            )
        )
    return failures


@register_check("HGROUP-17", "隐奸与群交互斥（玩家侧）")
def check_hgroup_17() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验玩家不能同时处于隐奸和群交。守卫是双向的：ask_group_sex前提带HIDDEN_SEX_MODE_0，被发现
        后从隐奸转群交先由settle_discovered清玩家隐奸、再由效果473清双方。有意只查玩家侧：NPC侧残留
        已由HGROUP-15的对称性覆盖，避免同一已知bug报两条
    """
    cache = cache_control.cache
    pl = _pl(cache)
    if pl is None:
        return []
    m = getattr(pl.sp_flag, "hidden_sex_mode", 0)
    if m > 0 and getattr(cache, "group_sex_mode", False):
        npcs = _npcs(cache)
        scene_hidden = {cid: cache.character_data[cid].sp_flag.hidden_sex_mode for cid in npcs if cid in cache.character_data and getattr(cache.character_data[cid].sp_flag, "hidden_sex_mode", 0) > 0}
        return [
            make_failure(
                "HGROUP-17",
                "隐奸与群交互斥（玩家侧）",
                f"玩家同时hidden_sex_mode={m}>0且cache.group_sex_mode=True；behavior_id={_behavior_id(pl)} 最近指令={_pre_instr(cache)} 场景各角色hidden_sex_mode={scene_hidden}",
                [0],
            )
        ]
    return []


@register_check("HGROUP-18", "隐奸发现度：0..100，且只有玩家可能非0")
def check_hgroup_18() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验隐蔽值只对角色0结算并被夹在[0,100]，NPC身上出现非0值即为错误写入。唯一写入点显式
        min/max夹紧，字段名的拼写dregree与真实定义一致，不要"顺手修正"
    """
    cache = cache_control.cache
    pl = _pl(cache)
    if pl is None:
        return []
    failures = []
    d = getattr(pl.h_state, "hidden_sex_discovery_dregree", None)
    if not (isinstance(d, (int, float)) and not isinstance(d, bool) and 0 <= d <= 100):
        failures.append(
            make_failure(
                "HGROUP-18",
                "隐奸发现度：0..100，且只有玩家可能非0",
                f"玩家hidden_sex_discovery_dregree={d!r}越界(应为0..100)；hidden_sex_mode={getattr(pl.sp_flag, 'hidden_sex_mode', None)} is_h={getattr(pl.sp_flag, 'is_h', None)}",
                [0],
            )
        )
    npcs = _npcs(cache)
    for cid in npcs:
        c = cache.character_data.get(cid)
        if c is None:
            continue
        v = getattr(c.h_state, "hidden_sex_discovery_dregree", 0)
        if v != 0:
            ability = getattr(c, "ability", None)
            ability_90 = ability.get(90) if isinstance(ability, dict) else None
            behavior = getattr(c, "behavior", None)
            failures.append(
                make_failure(
                    "HGROUP-18",
                    "隐奸发现度：0..100，且只有玩家可能非0",
                    f"NPC cid={cid}({_name(c)})hidden_sex_discovery_dregree={v!r}应为0；hidden_sex_mode={getattr(c.sp_flag, 'hidden_sex_mode', None)} "
                    f"is_h={getattr(c.sp_flag, 'is_h', None)} ability[90]={ability_90} behavior_id={_behavior_id(c)} duration={getattr(behavior, 'duration', None)}",
                    [cid],
                )
            )
    return failures


@register_check("HGROUP-19", "露出模式必须双向一致且至多一对")
def check_hgroup_19() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验选择露出模式时双方被写入同一个值，且入口效果链让双方都进入H；露出恒为"玩家+至多一名
        NPC"的对称状态，与隐奸不同，露出侧"双方is_h"是真命题。"至多一对"的依据是ask_exhibitionism_sex
        前提含EXHIBITIONISM_SEX_MODE_0(玩家自己)，无法在露出中再邀请第二人
    """
    cache = cache_control.cache
    pl = _pl(cache)
    if pl is None:
        return []
    e = getattr(pl.sp_flag, "exhibitionism_sex_mode", 0)
    npcs = _npcs(cache)
    ex = []
    for cid in npcs:
        c = cache.character_data.get(cid)
        if c is None:
            continue
        if getattr(c.sp_flag, "exhibitionism_sex_mode", 0) > 0:
            ex.append(c)

    def _ctx():
        detail = [f"cid={x.cid} name={_name(x)} position={x.position} mode={x.sp_flag.exhibitionism_sex_mode} is_h={x.sp_flag.is_h}" for x in ex]
        return f"pl.exhibitionism_sex_mode={e} 明细={detail} pl.position={pl.position} hidden_sex_mode={getattr(pl.sp_flag, 'hidden_sex_mode', None)} behavior_id={_behavior_id(pl)}"

    failures = []
    if len(ex) > 1:
        failures.append(make_failure("HGROUP-19", "露出模式必须双向一致且至多一对", f"同时有{len(ex)}名NPC带exhibitionism_sex_mode>0，应至多1名；{_ctx()}", [c.cid for c in ex]))
        return failures
    if e > 0:
        if len(ex) != 1:
            failures.append(make_failure("HGROUP-19", "露出模式必须双向一致且至多一对", f"玩家exhibitionism_sex_mode={e}>0但同场景带对应模式的NPC数={len(ex)}!=1；{_ctx()}", [0]))
        else:
            t = ex[0]
            probs = []
            if getattr(t.sp_flag, "exhibitionism_sex_mode", None) != e:
                probs.append(f"NPC模式{t.sp_flag.exhibitionism_sex_mode}!=玩家模式{e}")
            if not getattr(t.sp_flag, "is_h", False):
                probs.append("NPC is_h=False")
            if not getattr(pl.sp_flag, "is_h", False):
                probs.append("玩家is_h=False")
            if not getattr(cache, "time_stop_mode", False) and getattr(t, "position", None) != pl.position:
                probs.append(f"position不同场景: {t.position}!={pl.position}")
            if probs:
                failures.append(make_failure("HGROUP-19", "露出模式必须双向一致且至多一对", f"NPC cid={t.cid}({_name(t)})：{'; '.join(probs)}；{_ctx()}", [0, t.cid]))
    else:
        if ex:
            failures.append(make_failure("HGROUP-19", "露出模式必须双向一致且至多一对", f"玩家exhibitionism_sex_mode=0但存在带该模式的NPC；{_ctx()}", [c.cid for c in ex]))
    return failures


@register_check("HGROUP-20", "露出与群交互斥（玩家侧）")
def check_hgroup_20() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验玩家不能同时处于露出和群交。ask_group_sex前提含SCENE_ALL_NOT_H而露出中双方都是is_h⇒
        群交邀请不可见；被发现后转群交的效果链带476先清双方露出再开群交。有意只查玩家侧：NPC侧残留
        由HGROUP-19的对称性覆盖
    """
    cache = cache_control.cache
    pl = _pl(cache)
    if pl is None:
        return []
    e = getattr(pl.sp_flag, "exhibitionism_sex_mode", 0)
    if getattr(cache, "group_sex_mode", False) and e > 0:
        return [
            make_failure(
                "HGROUP-20",
                "露出与群交互斥（玩家侧）",
                f"玩家同时cache.group_sex_mode=True且exhibitionism_sex_mode={e}>0；behavior_id={_behavior_id(pl)} 最近指令={_pre_instr(cache)}",
                [0],
            )
        ]
    return []


@register_check("HGROUP-21", "隐奸/露出模式值域")
def check_hgroup_21() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验hidden_sex_mode与exhibitionism_sex_mode都只能是0..4。近乎恒真的哨兵，只能抓存档损坏/
        mod写入/迁移越界；成本极低故保留
    """
    cache = cache_control.cache
    if cache is None:
        return []
    all_ids = _all(cache)
    failures = []
    for cid in all_ids:
        c = cache.character_data.get(cid)
        if c is None:
            continue
        hm = getattr(c.sp_flag, "hidden_sex_mode", None)
        em = getattr(c.sp_flag, "exhibitionism_sex_mode", None)
        bad = []
        if hm not in (0, 1, 2, 3, 4):
            bad.append(f"hidden_sex_mode={hm!r}")
        if em not in (0, 1, 2, 3, 4):
            bad.append(f"exhibitionism_sex_mode={em!r}")
        if bad:
            failures.append(
                make_failure(
                    "HGROUP-21",
                    "隐奸/露出模式值域",
                    f"角色cid={cid}({_name(c)}) {'; '.join(bad)}越界(应为0..4)；is_h={getattr(c.sp_flag, 'is_h', None)} position={getattr(c, 'position', None)} "
                    f"behavior_id={_behavior_id(c)}",
                    [cid],
                )
            )
    return failures


# ---------------------------------------------------------------------------
# 三、H通用状态、逆推、无意识H
# ---------------------------------------------------------------------------


@register_check("HGROUP-22", "在H的NPC必须与玩家同场景")
def check_hgroup_22() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验本作所有H都以玩家为中心，离开玩家场景的NPC会在NPC行为循环里被强制退出H。时停守卫必需：
        隐奸模式1/2下玩家is_h=False时切换交互对象到非H第三者，move的NOT_H前提成立，配合中级时停放行，
        玩家可在时停中带着在H的NPC离场，而NPC自愈循环被跳过；非时停时该路径同样可发生，但NPC循环会
        在快照前清干净
    """
    cache = cache_control.cache
    pl = _pl(cache)
    if pl is None or getattr(cache, "time_stop_mode", False):
        return []
    npcs = _npcs(cache)
    failures = []
    for cid in npcs:
        c = cache.character_data.get(cid)
        if c is None:
            continue
        if getattr(c.sp_flag, "is_h", False) and getattr(c, "position", None) != pl.position:
            failures.append(
                make_failure(
                    "HGROUP-22",
                    "在H的NPC必须与玩家同场景",
                    f"NPC cid={cid}({_name(c)})is_h=True但position={c.position}!=pl.position={pl.position}；behavior_id={_behavior_id(c)} state={getattr(c, 'state', None)} "
                    f"unconscious_h={getattr(c.sp_flag, 'unconscious_h', None)} hidden_sex_mode={getattr(c.sp_flag, 'hidden_sex_mode', None)} "
                    f"exhibitionism_sex_mode={getattr(c.sp_flag, 'exhibitionism_sex_mode', None)} cache.group_sex_mode={getattr(cache, 'group_sex_mode', None)} "
                    f"cache.time_stop_mode={getattr(cache, 'time_stop_mode', None)}",
                    [cid],
                )
            )
    return failures


@register_check("HGROUP-23", "玩家在H时场内必须有在H的NPC")
def check_hgroup_23() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验普通H(非群交、非隐奸、非时停)中玩家的H标记必然伴随至少一名同场景的在H NPC——所有给玩家
        挂462的行为都同时给对象挂464。原H-02断言"pl.target_character_id指向的角色在H且同场景"已拆除：
        交互对象可在H中被自由切换，target_character_id只保留在失败上下文里当线索。已知可命中的真泄漏：
        NPC在H中被弄出玩家场景时，离场清理把NPC的target_character_id改成它自己再转END_H，玩家的is_h
        无人清理
    """
    cache = cache_control.cache
    pl = _pl(cache)
    if pl is None:
        return []
    if not (
        getattr(pl.sp_flag, "is_h", False)
        and not getattr(cache, "group_sex_mode", False)
        and getattr(pl.sp_flag, "hidden_sex_mode", 0) == 0
        and not getattr(cache, "time_stop_mode", False)
    ):
        return []
    npcs = _npcs(cache)
    same_scene_h = []
    scene_list = []
    for cid in npcs:
        c = cache.character_data.get(cid)
        if c is None:
            continue
        if getattr(c, "position", None) == pl.position:
            scene_list.append(cid)
            if getattr(c.sp_flag, "is_h", False):
                same_scene_h.append(cid)
    if same_scene_h:
        return []
    target = pl.target_character_id
    tinfo = "无"
    if target and target in cache.character_data:
        t = cache.character_data[target]
        tinfo = f"cid={target} is_h={getattr(t.sp_flag, 'is_h', None)} position={t.position}"
    return [
        make_failure(
            "HGROUP-23",
            "玩家在H时场内必须有在H的NPC",
            f"玩家is_h=True(非群交/非隐奸/非时停)但同场景无任何在H的NPC；pl.position={pl.position} behavior_id={_behavior_id(pl)} "
            f"exhibitionism_sex_mode={getattr(pl.sp_flag, 'exhibitionism_sex_mode', None)} unconscious_h={getattr(pl.sp_flag, 'unconscious_h', None)} "
            f"target_character_id线索={tinfo} 同场景NPC列表={scene_list} 最近指令={_pre_instr(cache)}",
            [0],
        )
    ]


@register_check("HGROUP-24", "逆推标记必须在H、同场景、且不在群交中")
def check_hgroup_24() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验h_state.npc_active_h(NPC主动逆推)是H内局部状态，只可能出现在非玩家、在H、非群交、
        (非时停时)同场景的角色身上。target绑定已拆除。已知可命中的真泄漏：离场清理只清is_h不重建
        h_state，npc_active_h可能残留在已退场角色身上
    """
    cache = cache_control.cache
    pl = _pl(cache)
    if pl is None:
        return []
    all_ids = _all(cache)
    time_stop = getattr(cache, "time_stop_mode", False)
    failures = []
    for cid in all_ids:
        c = cache.character_data.get(cid)
        if c is None:
            continue
        if not getattr(c.h_state, "npc_active_h", False):
            continue
        bad = []
        if cid == 0:
            bad.append("cid==0(玩家不应带此标记)")
        if not getattr(c.sp_flag, "is_h", False):
            bad.append("is_h=False")
        if getattr(cache, "group_sex_mode", False):
            bad.append("cache.group_sex_mode=True")
        if not time_stop and getattr(c, "position", None) != pl.position:
            bad.append(f"position={c.position}!=pl.position={pl.position}")
        if bad:
            failures.append(
                make_failure(
                    "HGROUP-24",
                    "逆推标记必须在H、同场景、且不在群交中",
                    f"角色cid={cid}({_name(c)})npc_active_h=True但{'; '.join(bad)}；hypnosis.active_h={getattr(c.hypnosis, 'active_h', None)} "
                    f"hypnosis.blockhead={getattr(c.hypnosis, 'blockhead', None)} unconscious_h={getattr(c.sp_flag, 'unconscious_h', None)} "
                    f"target_character_id(玩家)={pl.target_character_id} behavior_id={_behavior_id(c)}",
                    [cid],
                )
            )
    return failures


@register_check("HGROUP-25", "催眠行为模式互斥（木头人/逆推）")
def check_hgroup_25() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验每次开启某个催眠行为模式前都会先clear_hypnosis_behavior_mode复位全部模式，木头人与逆推
        不可能同时为真。普通H结束不动hypnosis结构，也造不出二者同真
    """
    cache = cache_control.cache
    if cache is None:
        return []
    all_ids = _all(cache)
    failures = []
    for cid in all_ids:
        c = cache.character_data.get(cid)
        if c is None:
            continue
        if getattr(c.hypnosis, "blockhead", False) and getattr(c.hypnosis, "active_h", False):
            failures.append(
                make_failure(
                    "HGROUP-25",
                    "催眠行为模式互斥（木头人/逆推）",
                    f"角色cid={cid}({_name(c)})hypnosis.blockhead与hypnosis.active_h同时为True；roleplay={getattr(c.hypnosis, 'roleplay', None)} "
                    f"unconscious_h={getattr(c.sp_flag, 'unconscious_h', None)} is_h={getattr(c.sp_flag, 'is_h', None)}",
                    [cid],
                )
            )
    return failures


@register_check("HGROUP-26", "无意识H档位值域")
def check_hgroup_26() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验unconscious_h取值只能是0..7([0否,1睡眠,2醉酒,3时停,4平然,5空气,6体控,7心控])。恒真型
        哨兵，主要防debug面板与存档迁移写入越界值
    """
    cache = cache_control.cache
    if cache is None:
        return []
    all_ids = _all(cache)
    failures = []
    for cid in all_ids:
        c = cache.character_data.get(cid)
        if c is None:
            continue
        v = getattr(c.sp_flag, "unconscious_h", None)
        if v not in range(0, 8):
            failures.append(
                make_failure(
                    "HGROUP-26",
                    "无意识H档位值域",
                    f"角色cid={cid}({_name(c)})unconscious_h={v!r}越界(应为0..7)；hypnosis.blockhead={getattr(c.hypnosis, 'blockhead', None)} "
                    f"hypnosis.active_h={getattr(c.hypnosis, 'active_h', None)} is_h={getattr(c.sp_flag, 'is_h', None)} behavior_id={_behavior_id(c)}",
                    [cid],
                )
            )
    return failures


@register_check("HGROUP-27", "时停开关与unconscious_h==3双向一致")
def check_hgroup_27() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验开启时停会给ALL全员(含玩家自己)写unconscious_h=3，关闭时全员写0，除时停外没有第二处写3。
        本条是其余条目时停守卫的根状态验证：先确认时停标记本身没断链，才能放心把位置类误报归因于时停。
        迭代范围必须正好是cache.npc_id_got | {0}，与写入侧的集合一致
    """
    cache = cache_control.cache
    if cache is None:
        return []
    all_ids = _all(cache)
    ts = getattr(cache, "time_stop_mode", False)
    pl_behavior_id = _behavior_id(cache.character_data.get(0)) if isinstance(getattr(cache, "character_data", None), dict) else None
    failures = []
    for cid in all_ids:
        c = cache.character_data.get(cid)
        if c is None:
            continue
        v = getattr(c.sp_flag, "unconscious_h", None)
        if ts and v != 3:
            failures.append(
                make_failure(
                    "HGROUP-27",
                    "时停开关与unconscious_h==3双向一致",
                    f"cache.time_stop_mode=True但角色cid={cid}({_name(c)})unconscious_h={v!r}!=3；position={c.position} is_h={getattr(c.sp_flag, 'is_h', None)} "
                    f"game_time={getattr(cache, 'game_time', None)} pl.behavior_id={pl_behavior_id}",
                    [cid],
                )
            )
        elif not ts and v == 3:
            failures.append(
                make_failure(
                    "HGROUP-27",
                    "时停开关与unconscious_h==3双向一致",
                    f"cache.time_stop_mode=False但角色cid={cid}({_name(c)})unconscious_h=3(未随时停关闭写回)；position={c.position} "
                    f"is_h={getattr(c.sp_flag, 'is_h', None)} game_time={getattr(cache, 'game_time', None)} pl.behavior_id={pl_behavior_id}",
                    [cid],
                )
            )
    return failures


@register_check("HGROUP-28", "装睡必须建立在睡奸醒来状态上")
def check_hgroup_28() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验h_state.pretend_sleep=True必须同时满足sp_flag.sleep_h_awake=True、
        sp_flag.unconscious_h==1、sp_flag.is_h=True。唯一置真点一次性写全三项。唯一已知例外是时停：
        handle_time_stop_on会把该NPC的unconscious_h覆盖成3，若装睡期间开时停，本条会误报——命中时
        先核对cache.time_stop_mode再判定，故失败上下文附带该值供triage，不在检查体内加时停豁免
        (原始不变式给出的检查体本身未加该豁免)
    """
    cache = cache_control.cache
    if cache is None:
        return []
    all_ids = _all(cache)
    failures = []
    for cid in all_ids:
        c = cache.character_data.get(cid)
        if c is None:
            continue
        if not getattr(c.h_state, "pretend_sleep", False):
            continue
        awake = getattr(c.sp_flag, "sleep_h_awake", False)
        uh = getattr(c.sp_flag, "unconscious_h", None)
        ih = getattr(c.sp_flag, "is_h", False)
        if not (awake and uh == 1 and ih):
            failures.append(
                make_failure(
                    "HGROUP-28",
                    "装睡必须建立在睡奸醒来状态上",
                    f"角色cid={cid}({_name(c)})pretend_sleep=True但sleep_h_awake={awake} unconscious_h={uh!r}(应为1) is_h={ih}；"
                    f"behavior_id={_behavior_id(c)} sleep_point={getattr(c, 'sleep_point', None)} "
                    f"cache.time_stop_mode={getattr(cache, 'time_stop_mode', None)}(若为True，已知会因HGROUP-27的时停覆写而误报，请先排除)",
                    [cid],
                )
            )
    return failures


@register_check("HGROUP-29", "「为玩家逆推而自慰」与去洗手间/宿舍自慰互斥")
def check_hgroup_29() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验状态机在"去找玩家逆推"和"找地方自慰"之间二选一，两者不能同时成立。不写成masturebate!=0：
        值3(群交自慰)是完全独立的写入链，不检查npc_masturebate_for_player，真正的二选一只在
        StateMachine/default.py的if/else上，对应值1/2
    """
    cache = cache_control.cache
    if cache is None:
        return []
    all_ids = _all(cache)
    failures = []
    for cid in all_ids:
        c = cache.character_data.get(cid)
        if c is None:
            continue
        mfp = getattr(c.sp_flag, "npc_masturebate_for_player", False)
        mb = getattr(c.sp_flag, "masturebate", 0)
        if mfp and mb in (1, 2):
            failures.append(
                make_failure(
                    "HGROUP-29",
                    "「为玩家逆推而自慰」与去洗手间/宿舍自慰互斥",
                    f"角色cid={cid}({_name(c)})npc_masturebate_for_player=True且masturebate={mb}(应二选一)；target_character_id={getattr(c, 'target_character_id', None)} "
                    f"behavior_id={_behavior_id(c)} follow_wait_time={getattr(c, 'follow_wait_time', None)} cache.group_sex_mode={getattr(cache, 'group_sex_mode', None)}",
                    [cid],
                )
            )
    return failures


@register_check("HGROUP-30", "体位字段的值域与「仅博士持有」")
def check_hgroup_30() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验玩家current_sex_position/pre_sex_position只能是-1或1..12，current_womb_sex_position只能
        是0..2；所有NPC这三个"仅博士有的数据"必须保持默认值-1/-1/0。所有权侧比原描述更强——这些效果
        函数无视传入的character_id、硬编码cache.character_data[0]，故NPC侧恒为默认值。恒真型哨兵，
        能抓的只有"某天有人把[0]改成[character_id]"这类回归
    """
    cache = cache_control.cache
    pl = _pl(cache)
    if pl is None:
        return []
    h = pl.h_state
    failures = []
    cur = getattr(h, "current_sex_position", None)
    pre = getattr(h, "pre_sex_position", None)
    womb = getattr(h, "current_womb_sex_position", None)
    valid_pos = set(range(1, 13)) | {-1}
    if cur not in valid_pos:
        failures.append(
            make_failure("HGROUP-30", "体位字段的值域与「仅博士持有」", f"玩家current_sex_position={cur!r}越界(应为-1或1..12)；target_character_id={pl.target_character_id} behavior_id={_behavior_id(pl)}", [0])
        )
    if pre not in valid_pos:
        failures.append(
            make_failure("HGROUP-30", "体位字段的值域与「仅博士持有」", f"玩家pre_sex_position={pre!r}越界(应为-1或1..12)；target_character_id={pl.target_character_id} behavior_id={_behavior_id(pl)}", [0])
        )
    if womb not in (0, 1, 2):
        failures.append(
            make_failure("HGROUP-30", "体位字段的值域与「仅博士持有」", f"玩家current_womb_sex_position={womb!r}越界(应为0..2)；target_character_id={pl.target_character_id} behavior_id={_behavior_id(pl)}", [0])
        )
    npcs = _npcs(cache)
    for cid in npcs:
        c = cache.character_data.get(cid)
        if c is None:
            continue
        hs = c.h_state
        vals = (getattr(hs, "current_sex_position", None), getattr(hs, "pre_sex_position", None), getattr(hs, "current_womb_sex_position", None))
        if vals != (-1, -1, 0):
            t = cache.character_data.get(getattr(c, "target_character_id", None))
            insert_pos = getattr(t.h_state, "insert_position", None) if t is not None else None
            failures.append(
                make_failure(
                    "HGROUP-30",
                    "体位字段的值域与「仅博士持有」",
                    f"NPC cid={cid}({_name(c)})(current_sex_position,pre_sex_position,current_womb_sex_position)={vals}应为(-1,-1,0)；"
                    f"target_character_id={getattr(c, 'target_character_id', None)} 其insert_position={insert_pos} behavior_id={_behavior_id(c)} "
                    f"last_behavior_id_list={getattr(c, 'last_behavior_id_list', None)}",
                    [cid],
                )
            )
    return failures


@register_check("HGROUP-31", "完全脱离H的角色不应残留H局部状态")
def check_hgroup_31() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验既不在H、也不在隐奸/露出/无意识H中的角色，其插入位置、逆推标记、性爱助手、装睡、寸止、绳缚等H内局部
        字段必须已归零；寸止徽章与绳缚描述会直接显示在角色标签/身体面板，绳缚残留还会持续参与每回合结算。go_to_join_group_sex不在本条字段集内：该字段是给"不在H、正在从远处赶来"的NPC用
        的，纳入本条会在群交期间必然误报，其生命周期由HGROUP-13/14单独负责。副作用提示：时停回合全员
        unconscious_h==3，本条在时停回合自动静默，无需额外守卫
    """
    cache = cache_control.cache
    if cache is None:
        return []
    all_ids = _all(cache)
    failures = []
    for cid in all_ids:
        c = cache.character_data.get(cid)
        if c is None:
            continue
        sp = c.sp_flag
        if not (getattr(sp, "is_h", False) or getattr(sp, "hidden_sex_mode", 0) != 0 or getattr(sp, "exhibitionism_sex_mode", 0) != 0 or getattr(sp, "unconscious_h", 0) != 0):
            hs = c.h_state
            bad = []
            if getattr(hs, "insert_position", -1) != -1:
                bad.append(f"insert_position={hs.insert_position!r}")
            if getattr(hs, "npc_active_h", False) is not False:
                bad.append(f"npc_active_h={hs.npc_active_h!r}")
            if getattr(hs, "sex_assist", False) is not False:
                bad.append(f"sex_assist={hs.sex_assist!r}")
            if getattr(hs, "pretend_sleep", False) is not False:
                bad.append(f"pretend_sleep={hs.pretend_sleep!r}")
            if getattr(hs, "orgasm_edge", 0) != 0:
                bad.append(f"orgasm_edge={getattr(hs, 'orgasm_edge', None)!r}")
            if getattr(hs, "bondage", 0) != 0:
                bad.append(f"bondage={getattr(hs, 'bondage', None)!r}")
            if bad:
                failures.append(
                    make_failure(
                        "HGROUP-31",
                        "完全脱离H的角色不应残留H局部状态",
                        f"角色cid={cid}({_name(c)}, position={c.position})已完全脱离H但残留: {'; '.join(bad)}；behavior_id={_behavior_id(c)} "
                        f"last_behavior_id_list={getattr(c, 'last_behavior_id_list', None)} cache.group_sex_mode={getattr(cache, 'group_sex_mode', None)} "
                        f"cache.time_stop_mode={getattr(cache, 'time_stop_mode', None)} hypnosis.active_h={getattr(c.hypnosis, 'active_h', None)}",
                        [cid],
                    )
                )
    return failures
