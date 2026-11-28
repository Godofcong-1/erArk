# -*- coding: UTF-8 -*-
"""
静态检查系统 - 基建/宿舍/岗位/资源/娱乐经营域检查
覆盖 ISLAND-01…ISLAND-33，校验 cache.rhodes_island（罗德岛基建总数据）与相关派生结构（岗位集合与列表、
设施等级与开放表、资源仓储、生产/农业/招募/交易线、宿舍管理员、图书借阅、派对排期、动力区、外勤委托、
监狱、访客与外交官映射等）的内部一致性。

全域前提（详见需求文档"约定与全域前提"一节，各检查函数按需复用）：
- 离线判定只能读 sp_flag.field_commission / escaping / be_bagged / in_diplomatic_visit 这几个来源标记，
  绝不能用"是否在 cache.npc_id_got 里"或"position == ['0','0']"判断角色是否离线在场——外勤、越狱、被绑架、
  外派外交官都会把角色移出名单但保留其岗位/槽位数据。
- 派生表（岗位集合/列表等）只由玩家打开对应面板时触发重算，没有任何每日/每回合结算刷新点，因此"派生表与
  实时名单逐人相等"类断言天然可能长期漂移，此类条目统一为 warning 级。
- 本文件所有检查函数都只读 cache，不做任何写入；对 cache.rhodes_island 及角色字段的访问一律用
  getattr/.get 加默认值，避免老存档缺字段时检查函数自身抛出未被期望的异常掩盖真实问题。
"""
from collections import Counter
from typing import Any, Dict, List

from Script.Core import cache_control
from Script.Config import game_config
from Script.System.Dormitory_System import common as dorm_common
from ..check_registry import CheckFailure, register_check, make_failure


def _eff(ri, facility_cid: int):
    """
    参数:
        ri: cache.rhodes_island 罗德岛数据对象
        facility_cid (int): 设施配置cid（config_facility的键）
    返回值:
        int|None: 该设施在其当前等级下的效果数值(config_facility_effect.effect)，任何一环缺失/越界时返回None
    功能:
        对应需求文档中的 _eff(fid) 帮助函数：config_facility_effect[config_facility_effect_data[名字][等级]].effect，
        全程防御式访问，供多条检查复用，任一层级配置/存档字段缺失都安全地返回None而不抛异常
    """
    try:
        facility = game_config.config_facility.get(facility_cid)
        if facility is None:
            return None
        level = ri.facility_level.get(facility_cid)
        if type(level) is not int:
            return None
        effect_data = game_config.config_facility_effect_data.get(facility.name)
        if effect_data is None or not (0 <= level < len(effect_data)):
            return None
        effect_cid = effect_data[level]
        effect = game_config.config_facility_effect.get(effect_cid)
        if effect is None:
            return None
        return effect.effect
    except Exception:
        return None


def _chara_name(cd: Dict[int, Any], cid) -> str:
    """
    参数:
        cd (Dict[int, Any]): cache.character_data 角色数据字典
        cid: 待查询的角色id
    返回值:
        str: 角色名字，角色不存在时返回"(不存在)"
    功能:
        安全获取角色名字，供各失败消息拼接使用
    """
    ch = cd.get(cid)
    return getattr(ch, "name", "?") if ch is not None else "(不存在)"


def _sp_flag_brief(ch: Any) -> str:
    """
    参数:
        ch: 角色对象
    返回值:
        str: 该角色离线相关标记的简要描述，形如 "field_commission=3,escaping=False,be_bagged=False,in_diplomatic_visit=0"
    功能:
        统一提取全域前提中约定的四个离线来源标记，供失败消息展示，用于判断"离线残留"还是"真实联动缺陷"
    """
    sp_flag = getattr(ch, "sp_flag", None)
    return (
        f"field_commission={getattr(sp_flag, 'field_commission', '?')},"
        f"escaping={getattr(sp_flag, 'escaping', '?')},"
        f"be_bagged={getattr(sp_flag, 'be_bagged', '?')},"
        f"in_diplomatic_visit={getattr(sp_flag, 'in_diplomatic_visit', '?')}"
    )


@register_check("ISLAND-01", "干员名单引用完整性")
def check_island_01_npc_id_got_ref() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验cache.npc_id_got中的每个id都存在于cache.character_data，且0号玩家角色存在。大量核心循环拿名单id
        直接无保护索引角色数据，缺一个即崩。应先于本域其余检查运行——ISLAND-07/09/19等都会用名单id索引角色，
        缺失时它们会抛检查器异常而不是给出清晰结论
    """
    cache = cache_control.cache
    cd = cache.character_data
    failures = []
    if 0 not in cd:
        failures.append(make_failure("ISLAND-01", "干员名单引用完整性", "0号玩家角色在character_data中不存在", []))
    ghost_ids = [cid for cid in cache.npc_id_got if cid not in cd]
    if ghost_ids:
        failures.append(
            make_failure(
                "ISLAND-01",
                "干员名单引用完整性",
                f"npc_id_got中存在幽灵cid列表={ghost_ids}，len(npc_id_got)={len(cache.npc_id_got)}，"
                f"len(character_data)={len(cd)}，0 in character_data={0 in cd}",
                ghost_ids,
            )
        )
    return failures


@register_check("ISLAND-02", "设施等级键完整且落在配置区间")
def check_island_02_facility_level_range() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验当前配置的每个设施都在facility_level中有等级记录，且等级是int、落在该设施效果表的合法下标区间。
        缺键或越界会让config_facility_effect_data[name][level]直接下标失败。用<=而非==比较键集：读档只补当前
        配置缺键、从不删旧键，csv删设施后旧档会留多余键，多余键单独作迁移告警，不对多余键取config_facility[fid]
    """
    cache = cache_control.cache
    ri = cache.rhodes_island
    facility_level = getattr(ri, "facility_level", None)
    if not isinstance(facility_level, dict):
        return []
    failures = []
    missing = [fid for fid in game_config.config_facility if fid not in facility_level]
    violations = []
    for fid, facility in game_config.config_facility.items():
        if fid not in facility_level:
            continue
        lv = facility_level[fid]
        effect_data = game_config.config_facility_effect_data.get(facility.name, [])
        if type(lv) is not int or not (1 <= lv < len(effect_data)):
            violations.append((fid, facility.name, lv, len(effect_data) - 1))
    extra_keys = sorted(set(facility_level) - set(game_config.config_facility))
    if missing or violations:
        failures.append(
            make_failure(
                "ISLAND-02",
                "设施等级键完整且落在配置区间",
                f"缺失的fac_cid列表={missing}，违规(fac_cid,设施名,lv,该设施最高级)={violations}，"
                f"历史多余键={extra_keys}",
                [],
            )
        )
    return failures


@register_check("ISLAND-03", "非控制中枢设施等级不超过中枢等级+1")
def check_island_03_facility_level_vs_core() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验除控制中枢(cid 0)自身外，任一设施等级不得高于控制中枢等级+1。唯一升级写点的门槛正是如此约束，
        豁免范围恰好只有控制中枢自身
    """
    cache = cache_control.cache
    ri = cache.rhodes_island
    facility_level = getattr(ri, "facility_level", None)
    if not isinstance(facility_level, dict) or 0 not in facility_level:
        return []
    core_lv = facility_level[0]
    violations = [
        (fid, game_config.config_facility[fid].name, facility_level[fid])
        for fid in game_config.config_facility
        if fid != 0 and fid in facility_level and facility_level[fid] > core_lv + 1
    ]
    if violations:
        return [
            make_failure(
                "ISLAND-03",
                "非控制中枢设施等级不超过中枢等级+1",
                f"控制中枢等级facility_level[0]={core_lv}，违规(fac_cid,设施名,lv)={violations}",
                [],
            )
        ]
    return []


@register_check("ISLAND-04", "设施开放表键完整、值为0/1语义")
def check_island_04_facility_open_values() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验当前配置的每个可开放设施都在facility_open中有开放记录，值必须是True/False或语义等价的1/0。
        不能写type(v) is bool——debug面板"设施全满级、全开放"写的是整数1，一旦用过全表都变int
    """
    cache = cache_control.cache
    ri = cache.rhodes_island
    facility_open = getattr(ri, "facility_open", None)
    if not isinstance(facility_open, dict):
        return []
    missing = [oid for oid in game_config.config_facility_open if oid not in facility_open]
    illegal = [
        (oid, game_config.config_facility_open[oid].name, repr(facility_open[oid]), type(facility_open[oid]).__name__)
        for oid in game_config.config_facility_open
        if oid in facility_open and facility_open[oid] not in (True, False, 0, 1)
    ]
    if missing or illegal:
        return [
            make_failure(
                "ISLAND-04",
                "设施开放表键完整、值为0/1语义",
                f"缺失的open_cid列表={missing}，非法值的(open_cid,设施名,repr(value),type)={illegal}",
                [],
            )
        ]
    return []


@register_check("ISLAND-05", "资源表键完整且库存为非负整数")
def check_island_05_resource_stock() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验当前Resource.csv的每种资源都在materials_resouce中有库存记录，值必须是非负int。负库存意味着某处
        扣减漏了余额检查。同样用<=比较键集：读档只补新增资源键、不删历史键。已知合法误报源：debug面板允许
        把龙门币/合成玉/粉红凭证输入成任意整数（含负数），失败上下文附带cache.debug_mode供排查时参考，
        但不作硬豁免
    """
    cache = cache_control.cache
    ri = cache.rhodes_island
    materials = getattr(ri, "materials_resouce", None)
    if not isinstance(materials, dict):
        return []
    missing = [rid for rid in game_config.config_resouce if rid not in materials]
    violations = [
        (rid, game_config.config_resouce[rid].name, materials[rid], type(materials[rid]).__name__)
        for rid in game_config.config_resouce
        if rid in materials and not (type(materials[rid]) is int and materials[rid] >= 0)
    ]
    extra_keys = sorted(set(materials) - set(game_config.config_resouce))
    if missing or violations:
        return [
            make_failure(
                "ISLAND-05",
                "资源表键完整且库存为非负整数",
                f"缺失的rid列表={missing}，违规(rid,资源名,数量,type)={violations}，历史多余键={extra_keys}，"
                f"cache.debug_mode={getattr(cache, 'debug_mode', '?')}",
                [],
            )
        ]
    return []


@register_check("ISLAND-06", "仓库容量与干员上限是设施等级的派生值")
def check_island_06_warehouse_and_people_max() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验warehouse_capacity == 仓储区(cid 3)当前等级效果 + 已用仓储扩展模块数*200，
        people_max == 宿舍区(cid 4)当前等级效果。唯一合法漂移窗口是跨版本改配置效果值后、玩家首次打开
        相关面板之前，效果表本身缺失时退化为跳过
    """
    cache = cache_control.cache
    ri = cache.rhodes_island
    eff3 = _eff(ri, 3)
    eff4 = _eff(ri, 4)
    if eff3 is None or eff4 is None:
        return []
    failures = []
    warehouse_capacity = getattr(ri, "warehouse_capacity", None)
    used_extra = getattr(ri, "used_extra_warehouse_capacity_module", 0)
    expected_warehouse = eff3 + used_extra * 200
    if warehouse_capacity != expected_warehouse:
        failures.append(
            make_failure(
                "ISLAND-06",
                "仓库容量与干员上限是设施等级的派生值",
                f"ri.warehouse_capacity={warehouse_capacity}，期望值=_eff(3)({eff3})+"
                f"used_extra_warehouse_capacity_module({used_extra})*200={expected_warehouse}，"
                f"facility_level[3]={getattr(ri, 'facility_level', {}).get(3)}，"
                f"本次读档后是否打开过基建/建造面板需人工排查",
                [],
            )
        )
    people_max = getattr(ri, "people_max", None)
    if people_max != eff4:
        failures.append(
            make_failure(
                "ISLAND-06",
                "仓库容量与干员上限是设施等级的派生值",
                f"ri.people_max={people_max}，期望值=_eff(4)={eff4}，"
                f"facility_level[4]={getattr(ri, 'facility_level', {}).get(4)}，"
                f"本次读档后是否打开过基建/建造面板需人工排查",
                [],
            )
        )
    return failures


@register_check("ISLAND-07", "已招募干员的岗位id必须合法")
def check_island_07_work_type_valid() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验每个在编非玩家干员的work.work_type存在于WorkType.csv。价值偏低但成本更低——
        all_work_npc_set[work_type].add(...)是无保护索引，非法值通常在下一次面板刷新时就KeyError崩溃，
        撑不到检查器看到；cid in cd的守卫交给ISLAND-01，这里再判一次只是防止本条自身抛异常
    """
    cache = cache_control.cache
    cd = cache.character_data
    valid_work_types = set(game_config.config_work_type)
    failures = []
    for cid in cache.npc_id_got:
        if cid == 0 or cid not in cd:
            continue
        work_type = cd[cid].work.work_type
        if work_type not in valid_work_types:
            failures.append(
                make_failure(
                    "ISLAND-07",
                    "已招募干员的岗位id必须合法",
                    f"角色cid={cid}({cd[cid].name})的work.work_type={work_type}不在合法岗位集合"
                    f"{sorted(valid_work_types)}中",
                    [cid],
                )
            )
    return failures


@register_check("ISLAND-08", "岗位集合键完整、成员合法且与自身键自洽")
def check_island_08_all_work_npc_set_self_consistent() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验all_work_npc_set的键必须等于岗位配置全集；集合里的每个id必须是存在的角色，且其work.work_type
        必须等于所在集合的键。绝不能加cid in cache.npc_id_got——外勤/关押/外派会把人移出名单而集合保留他，
        是主线玩法下的必现误报
    """
    cache = cache_control.cache
    ri = cache.rhodes_island
    cd = cache.character_data
    all_work_npc_set = getattr(ri, "all_work_npc_set", None)
    if not isinstance(all_work_npc_set, dict):
        return []
    config_keys = set(game_config.config_work_type)
    actual_keys = set(all_work_npc_set)
    key_diff_missing = sorted(config_keys - actual_keys)
    key_diff_extra = sorted(actual_keys - config_keys)
    violations = []
    for wid, ids in all_work_npc_set.items():
        for cid in ids:
            if cid not in cd:
                violations.append((wid, cid, "不存在", None))
            elif cd[cid].work.work_type != wid:
                violations.append((wid, cid, cd[cid].name, cd[cid].work.work_type))
    if key_diff_missing or key_diff_extra or violations:
        return [
            make_failure(
                "ISLAND-08",
                "岗位集合键完整、成员合法且与自身键自洽",
                f"缺失的work_id={key_diff_missing}，多余的work_id={key_diff_extra}，"
                f"违规(work_id,cid,name,实际work_type)={violations}",
                [v[1] for v in violations],
            )
        ]
    return []


@register_check("ISLAND-09", "岗位集合与在编名单的逐人重算一致")
def check_island_09_work_set_recompute() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验按当前在编名单逐人重算的岗位集合应与缓存一致。只能是告警，有两个合法漂移源：外交任免直接改
        work.work_type却不调update_work_people()；离线角色留在集合里而重算式扫不到他。报告时按sp_flag把
        "离线残留"与"面板漏刷新"分类
    """
    cache = cache_control.cache
    ri = cache.rhodes_island
    cd = cache.character_data
    all_work_npc_set = getattr(ri, "all_work_npc_set", None)
    if not isinstance(all_work_npc_set, dict):
        return []
    failures = []
    for wid in game_config.config_work_type:
        cached_set = all_work_npc_set.get(wid, set())
        recompute_set = {cid for cid in cache.npc_id_got if cid != 0 and cid in cd and cd[cid].work.work_type == wid}
        extra = cached_set - recompute_set
        missing = recompute_set - cached_set
        if not extra and not missing:
            continue
        detail = [
            f"cid={cid},name={_chara_name(cd, cid)},work_type={getattr(cd.get(cid), 'work', None) and cd[cid].work.work_type},{_sp_flag_brief(cd.get(cid))}"
            for cid in sorted(extra | missing)
        ]
        failures.append(
            make_failure(
                "ISLAND-09",
                "岗位集合与在编名单的逐人重算一致",
                f"[warning] 岗位work_id={wid}：多出的cid={sorted(extra)}，缺失的cid={sorted(missing)}，明细={detail}",
                sorted(extra | missing),
            )
        )
    return failures


@register_check("ISLAND-10", "在岗人数计数可由岗位集合重算")
def check_island_10_work_people_now() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验work_people_now必须等于所有非0岗位集合的规模之和。两者只由同一轮循环写入，不受面板触发式刷新
        影响。已知唯一破口：角色id重映射把两个旧id映到同一新id时集合会缩、计数不缩——正是要抓的真问题
    """
    cache = cache_control.cache
    ri = cache.rhodes_island
    all_work_npc_set = getattr(ri, "all_work_npc_set", None)
    if not isinstance(all_work_npc_set, dict):
        return []
    recompute = sum(len(ids) for wid, ids in all_work_npc_set.items() if wid != 0)
    work_people_now = getattr(ri, "work_people_now", None)
    if work_people_now != recompute:
        per_set = {wid: len(ids) for wid, ids in all_work_npc_set.items() if wid != 0}
        return [
            make_failure(
                "ISLAND-10",
                "在岗人数计数可由岗位集合重算",
                f"ri.work_people_now={work_people_now}，重算值={recompute}，各非零岗位集合规模={per_set}",
                [],
            )
        ]
    return []


# 六个岗位派生列表 与 (对应的all_work_npc_set键, 是否每轮全量重建), ISLAND-11/ISLAND-12共用
_WORK_LIST_FIELDS = (
    ("production_worker_ids", 121, False),
    ("hr_operator_ids_list", 71, False),
    ("trade_operator_ids_list", 111, True),
    ("power_operator_ids_list", 11, False),
    ("herb_garden_operator_ids", 161, False),
    ("green_house_operator_ids", 162, False),
)


@register_check("ISLAND-11", "岗位人员列表引用合法、无重复、不漏在岗者")
def check_island_11_work_lists_superset() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验六个岗位派生列表的成员必须是存在的角色且岗位匹配、列表内不得重复；每个列表必须包含对应岗位集合
        的全部成员（漏人=真bug）。贸易员列表每轮全量重建，取严格相等；其余五个增量列表只断言超集，多出来的
        是离线残留（合法可达，交给ISLAND-12），少人才是刷新缺陷
    """
    cache = cache_control.cache
    ri = cache.rhodes_island
    cd = cache.character_data
    all_work_npc_set = getattr(ri, "all_work_npc_set", None)
    if not isinstance(all_work_npc_set, dict):
        return []
    failures = []
    for field, wid, is_exact in _WORK_LIST_FIELDS:
        lst = getattr(ri, field, None)
        if not isinstance(lst, list):
            continue
        dup = [cid for cid, cnt in Counter(lst).items() if cnt > 1]
        mismatched = [
            (cid, _chara_name(cd, cid), cd[cid].work.work_type if cid in cd else None)
            for cid in lst
            if cid not in cd or cd[cid].work.work_type != wid
        ]
        expected = all_work_npc_set.get(wid, set())
        missing = expected - set(lst)
        extra = set(lst) - expected if is_exact else set()
        if dup or mismatched or missing or extra:
            detail = [f"cid={cid},{_sp_flag_brief(cd.get(cid))}" for cid in sorted(set(dup) | missing | extra)]
            failures.append(
                make_failure(
                    "ISLAND-11",
                    "岗位人员列表引用合法、无重复、不漏在岗者",
                    f"列表{field}(work_id={wid})：重复cid={dup}，岗位不匹配(cid,name,work_type)={mismatched}，"
                    f"漏人(缺失的cid)={sorted(missing)}，残留(多出的cid)={sorted(extra)}，明细={detail}",
                    sorted(set(dup) | missing | extra),
                )
            )
    return failures


@register_check("ISLAND-12", "岗位人员列表的离线残留漂移")
def check_island_12_work_lists_stale_members() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        [warning] 校验五个增量维护的岗位列表应与对应岗位集合严格相等；出现多余成员说明列表在两次刷新之间
        滞后于成员实际状态。日结时update_work_people()会整体重置并按在编角色重建这些列表，本条覆盖的是
        两次重建之间可能出现的瞬态漂移
    """
    cache = cache_control.cache
    ri = cache.rhodes_island
    cd = cache.character_data
    all_work_npc_set = getattr(ri, "all_work_npc_set", None)
    if not isinstance(all_work_npc_set, dict):
        return []
    failures = []
    for field, wid, _is_exact in _WORK_LIST_FIELDS:
        lst = getattr(ri, field, None)
        if not isinstance(lst, list):
            continue
        expected = all_work_npc_set.get(wid, set())
        stale = set(lst) - expected
        if not stale:
            continue
        detail = [f"cid={cid},name={_chara_name(cd, cid)},{_sp_flag_brief(cd.get(cid))}" for cid in sorted(stale)]
        failures.append(
            make_failure(
                "ISLAND-12",
                "岗位人员列表的离线残留漂移",
                f"[warning] 列表{field}(work_id={wid})存在离线残留cid={sorted(stale)}，明细={detail}",
                sorted(stale),
            )
        )
    return failures


@register_check("ISLAND-13", "流水线结构、数量与配方id合法")
def check_island_13_assembly_line() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验制造加工区(cid 12)等级N恰好开放0..N-1号流水线；每条记录是长度5的list，当前配方与待切换配方都是
        合法配方id，结算小时在0..23。结构检查必须先于内容检查——存档迁移不补普通dict内部的键，也不补list长度，
        消费侧大量无保护下标
    """
    cache = cache_control.cache
    ri = cache.rhodes_island
    assembly_line = getattr(ri, "assembly_line", None)
    facility_level = getattr(ri, "facility_level", {})
    if not isinstance(assembly_line, dict) or 12 not in facility_level:
        return []
    failures = []
    expected_keys = set(range(facility_level[12]))
    actual_keys = set(assembly_line)
    if expected_keys != actual_keys:
        failures.append(
            make_failure(
                "ISLAND-13",
                "流水线结构、数量与配方id合法",
                f"facility_level[12]={facility_level[12]}，实际线号集合={sorted(actual_keys)}，"
                f"期望线号集合={sorted(expected_keys)}",
                [],
            )
        )
    violations = []
    for line_id, v in assembly_line.items():
        if not isinstance(v, list) or len(v) != 5:
            violations.append((line_id, v))
            continue
        if v[0] not in game_config.config_productformula or v[3] not in game_config.config_productformula:
            violations.append((line_id, v))
            continue
        if type(v[4]) is not int or not (0 <= v[4] <= 23):
            violations.append((line_id, v))
    if violations:
        failures.append(
            make_failure(
                "ISLAND-13",
                "流水线结构、数量与配方id合法",
                f"违规line_id与整条记录={violations}",
                [],
            )
        )
    return failures


@register_check("ISLAND-14", "农业线与招募线结构、种植类型合法")
def check_island_14_agriculture_and_recruit_line_structure() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验药田线与温室线每条是长度5的list，种植类型只能是0(停种)或该线唯一允许的资源——药田11、温室16；
        招募线每条至少4项。窄化到{0,11}/{0,16}已核实候选表硬编码；结算侧无保护下标[0]，结构守卫必须在前
    """
    cache = cache_control.cache
    ri = cache.rhodes_island
    failures = []

    def _check_line(field: str, allowed_types) -> None:
        line = getattr(ri, field, None)
        if not isinstance(line, dict):
            return
        violations = [
            (line_id, v)
            for line_id, v in line.items()
            if not (isinstance(v, list) and len(v) == 5 and v[0] in allowed_types)
        ]
        if violations:
            failures.append(
                make_failure(
                    "ISLAND-14",
                    "农业线与招募线结构、种植类型合法",
                    f"线{field}：违规line_id与整条记录={violations}，允许的种植类型v[0]={allowed_types}",
                    [],
                )
            )

    _check_line("herb_garden_line", (0, 11))
    _check_line("green_house_line", (0, 16))

    recruit_line = getattr(ri, "recruit_line", None)
    if isinstance(recruit_line, dict):
        violations = [
            (line_id, v) for line_id, v in recruit_line.items() if not (isinstance(v, list) and len(v) >= 4)
        ]
        if violations:
            failures.append(
                make_failure(
                    "ISLAND-14",
                    "农业线与招募线结构、种植类型合法",
                    f"线recruit_line：违规line_id与整条记录={violations}",
                    [],
                )
            )
    return failures


@register_check("ISLAND-15", "各生产/招募/交易线主负责人有效、岗位匹配、同类不重复")
def check_island_15_line_main_operator() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验流水线(岗位121)、药田(161)、温室(162)、招募线(71)的主负责人槽位与各资源类型主交易员(111)必须是
        0或一名存在的角色，岗位须与该线要求一致，且必须在对应岗位人员列表中；同类线内一人不得同时主理两条。
        不得要求主负责人在npc_id_got——主管/种植员/招聘专员都能被派外勤，岗位与槽位都保留
    """
    cache = cache_control.cache
    ri = cache.rhodes_island
    cd = cache.character_data
    failures = []
    main_list = {
        121: getattr(ri, "production_worker_ids", []),
        161: getattr(ri, "herb_garden_operator_ids", []),
        162: getattr(ri, "green_house_operator_ids", []),
        71: getattr(ri, "hr_operator_ids_list", []),
    }
    line_defs = (
        (getattr(ri, "assembly_line", None), 1, 121, "assembly_line"),
        (getattr(ri, "herb_garden_line", None), 1, 161, "herb_garden_line"),
        (getattr(ri, "green_house_line", None), 1, 162, "green_house_line"),
        (getattr(ri, "recruit_line", None), 2, 71, "recruit_line"),
    )
    for lines, idx, wid, line_name in line_defs:
        if not isinstance(lines, dict):
            continue
        mains = [
            (line_id, v[idx])
            for line_id, v in lines.items()
            if isinstance(v, list) and len(v) > idx and v[idx]
        ]
        occupant_count = Counter(m for _lid, m in mains)
        dup = {m for m, cnt in occupant_count.items() if cnt > 1}
        illegal = [
            (line_id, m)
            for line_id, m in mains
            if not (type(m) is int and m in cd and cd[m].work.work_type == wid and m in main_list.get(wid, []))
        ]
        if dup or illegal:
            dup_lines = sorted(line_id for line_id, m in mains if m in dup)
            detail = [f"line_id={lid},m={m},{_chara_name(cd, m)},work_type={cd[m].work.work_type if m in cd else None},{_sp_flag_brief(cd.get(m))}" for lid, m in illegal]
            failures.append(
                make_failure(
                    "ISLAND-15",
                    "各生产/招募/交易线主负责人有效、岗位匹配、同类不重复",
                    f"线{line_name}：重复占用的line_id列表={dup_lines}，非法槽位明细(line_id,槽位值)={illegal}，"
                    f"详情={detail}，岗位列表={main_list.get(wid)}",
                    [m for _lid, m in illegal if type(m) is int],
                )
            )
    resource_type_main_trader = getattr(ri, "resource_type_main_trader", None)
    if isinstance(resource_type_main_trader, dict):
        illegal_traders = [
            (rtype, m)
            for rtype, m in resource_type_main_trader.items()
            if m and not (m in cd and cd[m].work.work_type == 111)
        ]
        if illegal_traders:
            detail = [f"type={t},m={m},{_chara_name(cd, m)},work_type={cd[m].work.work_type if m in cd else None}" for t, m in illegal_traders]
            failures.append(
                make_failure(
                    "ISLAND-15",
                    "各生产/招募/交易线主负责人有效、岗位匹配、同类不重复",
                    f"resource_type_main_trader非法槽位={illegal_traders}，详情={detail}",
                    [m for _t, m in illegal_traders],
                )
            )
    return failures


@register_check("ISLAND-16", "宿舍管理员表结构与引用合法")
def check_island_16_dormitory_managers_structure() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验dormitory_managers的键只能是1..9层；值是0(未任命)或一名存在的角色；同一人不得同时管理两层。
        用<=而非==range(1,10)：init_dormitory_managers()全仓无调用点，旧档若存在残缺字典不会被修复；缺层
        不会崩溃，全部消费点都用.get(layer,0)。不要求管理员在npc_id_got（舍管可被派外勤）
    """
    cache = cache_control.cache
    ri = cache.rhodes_island
    cd = cache.character_data
    dormitory_managers = getattr(ri, "dormitory_managers", None)
    if not isinstance(dormitory_managers, dict):
        return []
    failures = []
    illegal_layers = [layer for layer in dormitory_managers if layer not in range(1, 10)]
    illegal_values = [
        (layer, m) for layer, m in dormitory_managers.items() if not (type(m) is int and m >= 0)
    ]
    non_zero = [(layer, m) for layer, m in dormitory_managers.items() if m]
    manager_ids = [m for _layer, m in non_zero]
    dup_managers = [m for m, cnt in Counter(manager_ids).items() if cnt > 1]
    ghost_ids = [(layer, m) for layer, m in non_zero if m not in cd]
    if illegal_layers or illegal_values or dup_managers or ghost_ids:
        return [
            make_failure(
                "ISLAND-16",
                "宿舍管理员表结构与引用合法",
                f"dormitory_managers全量={dormitory_managers}，非法层键={illegal_layers}，"
                f"非法值={illegal_values}，重复管理员及其层号={[(m, [l for l, mm in non_zero if mm == m]) for m in dup_managers]}，"
                f"不存在的cid={ghost_ids}",
                [m for m in manager_ids if m in dup_managers] + [m for _l, m in ghost_ids],
            )
        ]
    return []


@register_check("ISLAND-17", "宿舍管理员岗位联动与层键覆盖")
def check_island_17_dormitory_manager_work_type_and_layers() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        [warning] 校验每个被任命的管理员的work.work_type应为31，且1..9层键应齐全。前者失败指向一处真实的
        联动缺失（select_new_work把现任舍管改派成别的岗位时只改work.work_type，不碰dormitory_managers），
        后者指向旧档迁移残缺
    """
    cache = cache_control.cache
    ri = cache.rhodes_island
    cd = cache.character_data
    dormitory_managers = getattr(ri, "dormitory_managers", None)
    if not isinstance(dormitory_managers, dict):
        return []
    failures = []
    missing_layers = sorted(set(range(1, 10)) - set(dormitory_managers))
    if missing_layers:
        failures.append(
            make_failure(
                "ISLAND-17",
                "宿舍管理员岗位联动与层键覆盖",
                f"[warning] dormitory_managers缺失的层键={missing_layers}",
                [],
            )
        )
    mismatched = [
        (layer, m, _chara_name(cd, m), cd[m].work.work_type)
        for layer, m in dormitory_managers.items()
        if m and m in cd and cd[m].work.work_type != 31
    ]
    if mismatched:
        failures.append(
            make_failure(
                "ISLAND-17",
                "宿舍管理员岗位联动与层键覆盖",
                f"[warning] 管理员岗位不为31的(layer,manager_id,name,实际work_type)={mismatched}，"
                f"all_work_npc_set.get(31)={getattr(ri, 'all_work_npc_set', {}).get(31)}",
                [m for _layer, m, _n, _w in mismatched],
            )
        )
    return failures


@register_check("ISLAND-18", "已关闭楼层不得保留管理员")
def check_island_18_closed_layer_no_manager() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验层号高于当前宿舍区等级理论开放上限的层，其管理员必须为0。低优先级、近乎恒真的守卫；
        任命入口只对open_layers出按钮，实际只能抓存档编辑/mod
    """
    cache = cache_control.cache
    ri = cache.rhodes_island
    cd = cache.character_data
    dormitory_managers = getattr(ri, "dormitory_managers", None)
    if not isinstance(dormitory_managers, dict):
        return []
    try:
        max_open_layer = dorm_common.get_dormitory_max_open_layer()
    except Exception:
        return []
    violations = [
        (layer, mid, _chara_name(cd, mid))
        for layer, mid in dormitory_managers.items()
        if not (layer <= max_open_layer or mid == 0)
    ]
    if violations:
        return [
            make_failure(
                "ISLAND-18",
                "已关闭楼层不得保留管理员",
                f"facility_level[4]={getattr(ri, 'facility_level', {}).get(4)}，"
                f"get_dormitory_max_open_layer()={max_open_layer}，违规(layer,manager_id,name)={violations}",
                [v[1] for v in violations],
            )
        ]
    return []


@register_check("ISLAND-19", "已招募干员的宿舍路径必须是合法场景")
def check_island_19_dormitory_path_valid() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验每个在编非玩家干员的dormitory必须非空且是cache.scene_data的合法键，不得残留""或模板值"无"。
        面板是模态阻塞的，回合快照看不到面板中途状态，不因"可能在编辑面板内"而抑制本条
    """
    cache = cache_control.cache
    cd = cache.character_data
    failures = []
    for cid in cache.npc_id_got:
        if cid == 0 or cid not in cd:
            continue
        ch = cd[cid]
        dormitory = getattr(ch, "dormitory", None)
        if dormitory and dormitory in cache.scene_data:
            continue
        failures.append(
            make_failure(
                "ISLAND-19",
                "已招募干员的宿舍路径必须是合法场景",
                f"角色cid={cid}({ch.name})的dormitory={dormitory!r}非法（务必区分''/'无'/其他非法路径），"
                f"permanent_dormitory={getattr(ch, 'permanent_dormitory', None)!r}，work.work_type={ch.work.work_type}",
                [cid],
            )
        )
    return failures


@register_check("ISLAND-20", "普通宿舍房间不超过2人")
def check_island_20_dormitory_room_capacity() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        [warning] 校验普通宿舍房设计容量2人；超员说明分配逻辑或特殊搬迁把人塞进了满房。永不判失败——代码自身
        容忍超员（max(2,实际人数)撑容量），超员可以合法持续到玩家升级宿舍；本函数仅在确有超员时给出经营告警
    """
    cache = cache_control.cache
    cd = cache.character_data
    try:
        resident_ids = dorm_common.get_dormitory_resident_id_set()
    except Exception:
        return []
    occ: Dict[str, List[int]] = {}
    for cid in resident_ids:
        ch = cd.get(cid)
        if ch is None:
            continue
        occ.setdefault(ch.dormitory, []).append(cid)
    ri = cache.rhodes_island
    materials = getattr(ri, "materials_resouce", {})
    failures = []
    for path, cids in occ.items():
        try:
            layer = dorm_common.get_layer_by_dormitory_path(path)
        except Exception:
            layer = 0
        if not layer or len(cids) <= 2:
            continue
        residents = [(cid, cd[cid].name, cd[cid].work.work_type) for cid in cids]
        scene_name = getattr(cache.scene_data.get(path), "name", path) if path in getattr(cache, "scene_data", {}) else path
        failures.append(
            make_failure(
                "ISLAND-20",
                "普通宿舍房间不超过2人",
                f"[warning] 房间路径={path}(场景名={scene_name})，层号={layer}，人数={len(cids)}，住户={residents}，"
                f"materials_resouce仅供参考不代表空床数",
                cids,
            )
        )
    return failures


@register_check("ISLAND-21", "借书记录双向一致且不超借阅上限")
def check_island_21_book_borrow_consistency() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验book_borrow_dict[book]=借阅者id(-1未借出，0为玩家)与角色的entertainment.borrow_book_id_set必须
        互为反向索引；书籍id必须合法；单人持书不超过3本。两处状态必须成对更新，是典型易漏点；书籍id合法性
        不是冗余——自动借书直接索引config_book[book_id]，失效键会崩
    """
    cache = cache_control.cache
    ri = cache.rhodes_island
    cd = cache.character_data
    book_borrow_dict = getattr(ri, "book_borrow_dict", None)
    if not isinstance(book_borrow_dict, dict):
        return []
    failures = []
    for book, holder in book_borrow_dict.items():
        if book not in game_config.config_book:
            failures.append(
                make_failure(
                    "ISLAND-21",
                    "借书记录双向一致且不超借阅上限",
                    f"book_id={book}不在config_book中，holder={holder}",
                    [],
                )
            )
            continue
        book_name = game_config.config_book[book].name
        if holder == -1:
            continue
        if holder not in cd or book not in cd[holder].entertainment.borrow_book_id_set:
            failures.append(
                make_failure(
                    "ISLAND-21",
                    "借书记录双向一致且不超借阅上限",
                    f"book_id={book}({book_name})记录holder={holder}({_chara_name(cd, holder)})，"
                    f"但其borrow_book_id_set={cd[holder].entertainment.borrow_book_id_set if holder in cd else '(角色不存在)'}中不含该书",
                    [holder] if holder in cd else [],
                )
            )
    for cid, ch in cd.items():
        borrow_set = ch.entertainment.borrow_book_id_set
        if len(borrow_set) > 3:
            failures.append(
                make_failure(
                    "ISLAND-21",
                    "借书记录双向一致且不超借阅上限",
                    f"角色cid={cid}({ch.name})持书数={len(borrow_set)}超过上限3，borrow_book_id_set={borrow_set}",
                    [cid],
                )
            )
        mismatched = [b for b in borrow_set if book_borrow_dict.get(b) != cid]
        if mismatched:
            failures.append(
                make_failure(
                    "ISLAND-21",
                    "借书记录双向一致且不超借阅上限",
                    f"角色cid={cid}({ch.name})的borrow_book_id_set中book_id={mismatched}在book_borrow_dict里未指回该角色，"
                    f"反向不一致明细={[(b, book_borrow_dict.get(b)) for b in mismatched]}",
                    [cid],
                )
            )
    return failures


@register_check("ISLAND-22", "一周派对排期键值合法且同一娱乐不占两天")
def check_island_22_party_day_of_week() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验party_day_of_week必须是dict、键恰为0..6，值为合法娱乐id(0表示无活动)，且同一非零娱乐id不得同时
        占据两天。isinstance(dict)守卫不可省——debug面板允许把整个party_day_of_week直接替换成一个整数，
        否则检查器会抛异常而不是给出清晰结论
    """
    cache = cache_control.cache
    ri = cache.rhodes_island
    party_day_of_week = getattr(ri, "party_day_of_week", None)
    if not isinstance(party_day_of_week, dict):
        return [
            make_failure(
                "ISLAND-22",
                "一周派对排期键值合法且同一娱乐不占两天",
                f"ri.party_day_of_week不是dict，实际类型={type(party_day_of_week).__name__}，"
                f"cache.debug_mode={getattr(cache, 'debug_mode', '?')}",
                [],
            )
        ]
    failures = []
    key_set = set(party_day_of_week)
    if key_set != set(range(7)):
        failures.append(
            make_failure(
                "ISLAND-22",
                "一周派对排期键值合法且同一娱乐不占两天",
                f"party_day_of_week全量={party_day_of_week}，缺失键={sorted(set(range(7)) - key_set)}，"
                f"多余键={sorted(key_set - set(range(7)))}",
                [],
            )
        )
    illegal_values = [
        (day, v) for day, v in party_day_of_week.items() if not (type(v) is int and v in game_config.config_entertainment)
    ]
    if illegal_values:
        failures.append(
            make_failure(
                "ISLAND-22",
                "一周派对排期键值合法且同一娱乐不占两天",
                f"非法娱乐id的(day,v)={illegal_values}",
                [],
            )
        )
    non_zero_vals = [v for v in party_day_of_week.values() if type(v) is int and v]
    dup_vals = {v for v, cnt in Counter(non_zero_vals).items() if cnt > 1}
    if dup_vals:
        dup_days = {v: [d for d, vv in party_day_of_week.items() if vv == v] for v in dup_vals}
        failures.append(
            make_failure(
                "ISLAND-22",
                "一周派对排期键值合法且同一娱乐不占两天",
                f"重复出现的娱乐id与对应天={dup_days}，当前weekday={getattr(cache.game_time, 'weekday', lambda: '?')()}",
                [],
            )
        )
    return failures


@register_check("ISLAND-23", "干员娱乐安排固定三项且id合法")
def check_island_23_entertainment_type() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验每个角色的entertainment.entertainment_type必须是长度恰为3的list，每项都是Entertainment.csv中的
        合法cid(0=无)。会真实崩溃的非法态——无保护索引config_entertainment[…]。检查范围取全部角色而非在编
        名单：该字段是角色自带属性，离线角色归队后同样会被AI读取。已知合法误报源：debug面板允许输入任意三元组
    """
    cache = cache_control.cache
    cd = cache.character_data
    failures = []
    for cid, ch in cd.items():
        et = ch.entertainment.entertainment_type
        if isinstance(et, list) and len(et) == 3 and all(type(e) is int and e in game_config.config_entertainment for e in et):
            continue
        illegal_items = [e for e in et if not (isinstance(et, list) and type(e) is int and e in game_config.config_entertainment)] if isinstance(et, list) else et
        failures.append(
            make_failure(
                "ISLAND-23",
                "干员娱乐安排固定三项且id合法",
                f"角色cid={cid}({ch.name})的entertainment_type={et!r}不合法，非法项={illegal_items}，"
                f"cache.debug_mode={getattr(cache, 'debug_mode', '?')}",
                [cid],
            )
        )
    return failures


@register_check("ISLAND-24", "自动交易设置键与阈值合法")
def check_island_24_auto_trade_setting() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验每个自动交易资源id必须存在于资源配置；设置字典必须含六个标准键；库存阈值在0..仓库容量，价格
        百分比在0..300，开关是0/1或True/False。开关不能写type(...) is bool——_ensure_trade_setting对缺失
        键统一setdefault(key,0)，补进去的是整数0
    """
    cache = cache_control.cache
    ri = cache.rhodes_island
    resource_type_auto_trade_setting = getattr(ri, "resource_type_auto_trade_setting", None)
    if not isinstance(resource_type_auto_trade_setting, dict):
        return []
    keys_required = {"buy_on", "buy_stock", "buy_price_percent", "sell_on", "sell_stock", "sell_price_percent"}
    warehouse_capacity = getattr(ri, "warehouse_capacity", 0)
    failures = []
    for rid, s in resource_type_auto_trade_setting.items():
        if rid not in game_config.config_resouce or not isinstance(s, dict) or not (keys_required <= set(s)):
            failures.append(
                make_failure(
                    "ISLAND-24",
                    "自动交易设置键与阈值合法",
                    f"resource_id={rid}({game_config.config_resouce[rid].name if rid in game_config.config_resouce else '不存在'})，"
                    f"完整setting字典={s}，缺失的键={sorted(keys_required - set(s)) if isinstance(s, dict) else '(非dict)'}",
                    [],
                )
            )
            continue
        out_of_range = []
        if s["buy_on"] not in (True, False, 0, 1):
            out_of_range.append(("buy_on", s["buy_on"]))
        if s["sell_on"] not in (True, False, 0, 1):
            out_of_range.append(("sell_on", s["sell_on"]))
        if not (0 <= s["buy_stock"] <= warehouse_capacity):
            out_of_range.append(("buy_stock", s["buy_stock"]))
        if not (0 <= s["sell_stock"] <= warehouse_capacity):
            out_of_range.append(("sell_stock", s["sell_stock"]))
        if not (0 <= s["buy_price_percent"] <= 300):
            out_of_range.append(("buy_price_percent", s["buy_price_percent"]))
        if not (0 <= s["sell_price_percent"] <= 300):
            out_of_range.append(("sell_price_percent", s["sell_price_percent"]))
        if out_of_range:
            failures.append(
                make_failure(
                    "ISLAND-24",
                    "自动交易设置键与阈值合法",
                    f"resource_id={rid}({game_config.config_resouce[rid].name})，完整setting字典={s}，"
                    f"ri.warehouse_capacity={warehouse_capacity}，越界字段={out_of_range}",
                    [],
                )
            )
    return failures


@register_check("ISLAND-25", "载具在外数量与进行中委托占用一致")
def check_island_25_vehicle_usage_consistency() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验每种载具记录形如[总数,外勤中数量]，满足0<=外勤中<=总数，且"外勤中"精确等于所有进行中委托占用
        该型载具的台数之和；委托引用的载具型号必须同时存在于配置与载具表。必须先扫委托再扫载具表——只遍历
        vehicles会漏掉"委托引用了不在载具表里的型号"这一类
    """
    cache = cache_control.cache
    ri = cache.rhodes_island
    ongoing = getattr(ri, "ongoing_field_commissions", None)
    vehicles = getattr(ri, "vehicles", None)
    if not isinstance(ongoing, dict) or not isinstance(vehicles, dict):
        return []
    failures = []
    used = Counter()
    used_by = {}
    for com_id, c in ongoing.items():
        if not (isinstance(c, list) and len(c) >= 3 and isinstance(c[2], list)):
            failures.append(
                make_failure(
                    "ISLAND-25",
                    "载具在外数量与进行中委托占用一致",
                    f"委托com_id={com_id}的记录结构非法：{c!r}",
                    [],
                )
            )
            continue
        for vid in c[2]:
            if vid not in game_config.config_vehicle or vid not in vehicles:
                failures.append(
                    make_failure(
                        "ISLAND-25",
                        "载具在外数量与进行中委托占用一致",
                        f"委托com_id={com_id}引用的载具vid={vid}不在config_vehicle或vehicles中",
                        [],
                    )
                )
                continue
            used[vid] += 1
            used_by.setdefault(vid, []).append(com_id)
    for vid, v in vehicles.items():
        vehicle_name = game_config.config_vehicle[vid].name if vid in game_config.config_vehicle else "?"
        if not (isinstance(v, list) and len(v) == 2 and all(type(x) is int for x in v)):
            failures.append(
                make_failure(
                    "ISLAND-25",
                    "载具在外数量与进行中委托占用一致",
                    f"vid={vid}({vehicle_name})的记录结构非法：{v!r}",
                    [],
                )
            )
            continue
        total, out = v
        used_count = used.get(vid, 0)
        if not (0 <= out <= total) or out != used_count:
            failures.append(
                make_failure(
                    "ISLAND-25",
                    "载具在外数量与进行中委托占用一致",
                    f"vid={vid}({vehicle_name})，total={total}，out={out}，实际委托占用used={used_count}，"
                    f"占用该载具的委托id列表={used_by.get(vid, [])}",
                    [],
                )
            )
    return failures


@register_check("ISLAND-26", "外勤派遣名单与干员外勤标记一致")
def check_island_26_field_commission_flag_consistency() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验每个进行中委托的id必须合法；成员必须是存在的角色、不被两个委托同时派遣、其sp_flag.field_commission
        等于该委托id；反过来，任何field_commission!=0的角色都必须恰好出现在对应委托的名单里。反向检查必须
        遍历character_data而不是npc_id_got——外勤成员必然不在npc_id_got里，用名单遍历会必现漏检
    """
    cache = cache_control.cache
    ri = cache.rhodes_island
    cd = cache.character_data
    ongoing = getattr(ri, "ongoing_field_commissions", None)
    if not isinstance(ongoing, dict):
        return []
    failures = []
    seen = set()
    for com_id, c in ongoing.items():
        if com_id not in game_config.config_commission:
            failures.append(
                make_failure(
                    "ISLAND-26",
                    "外勤派遣名单与干员外勤标记一致",
                    f"委托com_id={com_id}不在config_commission中",
                    [],
                )
            )
            continue
        commission_name = game_config.config_commission[com_id].name
        if not (isinstance(c, list) and len(c) >= 1 and isinstance(c[0], list)):
            failures.append(
                make_failure(
                    "ISLAND-26",
                    "外勤派遣名单与干员外勤标记一致",
                    f"委托com_id={com_id}({commission_name})的记录结构非法：{c!r}",
                    [],
                )
            )
            continue
        for cid in c[0]:
            if cid not in cd:
                failures.append(
                    make_failure(
                        "ISLAND-26",
                        "外勤派遣名单与干员外勤标记一致",
                        f"委托com_id={com_id}({commission_name})名单中的cid={cid}在character_data中不存在",
                        [],
                    )
                )
                continue
            if cid in seen:
                failures.append(
                    make_failure(
                        "ISLAND-26",
                        "外勤派遣名单与干员外勤标记一致",
                        f"重复派遣的cid={cid}({cd[cid].name})同时出现在多个委托名单中",
                        [cid],
                    )
                )
                continue
            seen.add(cid)
            ch = cd[cid]
            if ch.sp_flag.field_commission != com_id:
                failures.append(
                    make_failure(
                        "ISLAND-26",
                        "外勤派遣名单与干员外勤标记一致",
                        f"委托com_id={com_id}({commission_name})名单含cid={cid}({ch.name})，但其"
                        f"sp_flag.field_commission={ch.sp_flag.field_commission}，与委托id不符，"
                        f"cid in cache.npc_id_got={cid in cache.npc_id_got}",
                        [cid],
                    )
                )
    for cid, ch in cd.items():
        if cid == 0:
            continue
        if ch.sp_flag.field_commission != 0 and cid not in seen:
            failures.append(
                make_failure(
                    "ISLAND-26",
                    "外勤派遣名单与干员外勤标记一致",
                    f"角色cid={cid}({ch.name})的sp_flag.field_commission={ch.sp_flag.field_commission}(悬空标记)，"
                    f"但未出现在任何进行中委托名单里",
                    [cid],
                )
            )
    return failures


@register_check("ISLAND-27", "储能与供能设施结构、绝对范围合法")
def check_island_27_power_structure_and_range() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验当前储能落在[0, power_storage_max]；三个供能列表结构固定(副反应炉2项、其他清洁能源3项、蓄电池
        3项)；所有数量与已用扩展位计数非负。不加"设施数<=基础位+当前模块库存"等上界断言——交易卖出不检查
        已用计数，可把模块库存卖到低于已建设施需求，这类上界只适合做经营告警，此处不实现
    """
    cache = cache_control.cache
    ri = cache.rhodes_island
    failures = []
    power_storage = getattr(ri, "power_storage", None)
    power_storage_max = getattr(ri, "power_storage_max", None)
    if power_storage is None or power_storage_max is None or not (0 <= power_storage <= power_storage_max):
        failures.append(
            make_failure(
                "ISLAND-27",
                "储能与供能设施结构、绝对范围合法",
                f"ri.power_storage={power_storage}，ri.power_storage_max={power_storage_max}，超出[0, max]范围",
                [],
            )
        )
    orundum_reactor_list = getattr(ri, "orundum_reactor_list", None)
    other_power_facility_list = getattr(ri, "other_power_facility_list", None)
    battery_list = getattr(ri, "battery_list", None)
    if not (isinstance(orundum_reactor_list, list) and len(orundum_reactor_list) == 2):
        failures.append(
            make_failure(
                "ISLAND-27",
                "储能与供能设施结构、绝对范围合法",
                f"ri.orundum_reactor_list结构非法：{orundum_reactor_list!r}，期望长度2",
                [],
            )
        )
    if not (isinstance(other_power_facility_list, list) and len(other_power_facility_list) == 3):
        failures.append(
            make_failure(
                "ISLAND-27",
                "储能与供能设施结构、绝对范围合法",
                f"ri.other_power_facility_list结构非法：{other_power_facility_list!r}，期望长度3",
                [],
            )
        )
    if not (isinstance(battery_list, list) and len(battery_list) == 3):
        failures.append(
            make_failure(
                "ISLAND-27",
                "储能与供能设施结构、绝对范围合法",
                f"ri.battery_list结构非法：{battery_list!r}，期望长度3",
                [],
            )
        )
    all_counts = []
    for lst in (battery_list, other_power_facility_list, orundum_reactor_list):
        if isinstance(lst, list):
            all_counts.extend(lst)
    negative_or_bad = [n for n in all_counts if type(n) is not int or n < 0]
    if negative_or_bad:
        failures.append(
            make_failure(
                "ISLAND-27",
                "储能与供能设施结构、绝对范围合法",
                f"供能列表中存在非法数量={negative_or_bad}，battery_list={battery_list}，"
                f"other_power_facility_list={other_power_facility_list}，orundum_reactor_list={orundum_reactor_list}",
                [],
            )
        )
    used_clean = getattr(ri, "now_used_extra_clean_energy_module_count", None)
    used_battery = getattr(ri, "now_used_extra_battery_count", None)
    if used_clean is not None and used_clean < 0:
        failures.append(
            make_failure(
                "ISLAND-27",
                "储能与供能设施结构、绝对范围合法",
                f"ri.now_used_extra_clean_energy_module_count={used_clean}为负",
                [],
            )
        )
    if used_battery is not None and used_battery < 0:
        failures.append(
            make_failure(
                "ISLAND-27",
                "储能与供能设施结构、绝对范围合法",
                f"ri.now_used_extra_battery_count={used_battery}为负",
                [],
            )
        )
    return failures


@register_check("ISLAND-28", "主供能调控员槽位有效且不重复")
def check_island_28_main_power_operator_slots() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验main_power_facility_operator_ids是固定4槽(火/水/风/光)，每个非0值必须是存在的角色且
        work.work_type==11，四槽互不重复。不要求在npc_id_got（调控员可被派外勤，岗位与槽位都保留）
    """
    cache = cache_control.cache
    ri = cache.rhodes_island
    cd = cache.character_data
    slots = getattr(ri, "main_power_facility_operator_ids", None)
    if not (isinstance(slots, list) and len(slots) == 4):
        return [
            make_failure(
                "ISLAND-28",
                "主供能调控员槽位有效且不重复",
                f"main_power_facility_operator_ids结构非法：{slots!r}，期望长度4的list",
                [],
            )
        ]
    non_zero = [m for m in slots if m]
    dup = {m for m, cnt in Counter(non_zero).items() if cnt > 1}
    illegal = [m for m in non_zero if not (m in cd and cd[m].work.work_type == 11)]
    if dup or illegal:
        detail = [
            f"cid={m},{_chara_name(cd, m)},work_type={cd[m].work.work_type if m in cd else None},{_sp_flag_brief(cd.get(m))}"
            for m in sorted(set(dup) | set(illegal))
        ]
        return [
            make_failure(
                "ISLAND-28",
                "主供能调控员槽位有效且不重复",
                f"四槽全量={slots}，重复占用cid={sorted(dup)}，非法槽位cid={illegal}，明细={detail}，"
                f"power_operator_ids_list={getattr(ri, 'power_operator_ids_list', None)}，"
                f"all_work_npc_set.get(11)={getattr(ri, 'all_work_npc_set', {}).get(11)}",
                sorted(set(dup) | set(illegal)),
            )
        ]
    return []


@register_check("ISLAND-29", "监狱长引用与囚犯数据自洽")
def check_island_29_warden_and_prisoners() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验current_warden_id为0或指向一名存在的、work.work_type==191的角色；每个囚犯id必须存在，逃脱概率
        落在0..100。去掉了"在npc_id_got"子句——监狱长可能被关押或逃脱而离线，此时work_type仍是191，引用合法
    """
    cache = cache_control.cache
    ri = cache.rhodes_island
    cd = cache.character_data
    failures = []
    warden_id = getattr(ri, "current_warden_id", 0)
    if warden_id != 0 and not (warden_id in cd and cd[warden_id].work.work_type == 191):
        actual_wardens = [cid for cid, ch in cd.items() if ch.work.work_type == 191]
        ch = cd.get(warden_id)
        failures.append(
            make_failure(
                "ISLAND-29",
                "监狱长引用与囚犯数据自洽",
                f"ri.current_warden_id={warden_id}({_chara_name(cd, warden_id)})不是合法监狱长引用，"
                f"实际work_type={getattr(ch, 'work', None) and ch.work.work_type}，{_sp_flag_brief(ch)}，"
                f"实际work_type==191的角色列表={actual_wardens}",
                [warden_id],
            )
        )
    current_prisoners = getattr(ri, "current_prisoners", None)
    if isinstance(current_prisoners, dict):
        illegal = [
            (p, v)
            for p, v in current_prisoners.items()
            if not (p in cd and isinstance(v, list) and len(v) >= 2 and 0 <= v[1] <= 100)
        ]
        if illegal:
            failures.append(
                make_failure(
                    "ISLAND-29",
                    "监狱长引用与囚犯数据自洽",
                    f"current_prisoners中的违规(囚犯id,记录)={illegal}",
                    [p for p, _v in illegal if p in cd],
                )
            )
    return failures


@register_check("ISLAND-30", "设施损坏数据与检修分派自洽")
def check_island_30_facility_damage_and_maintenance() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验facility_damage_data的键必须是合法场景路径、值为正整数(<=0时代码会pop)；maintenance_place的键
        必须是存在的、work.work_type==21的角色，值必须是合法场景路径。不要求检修工程师在npc_id_got（外勤中
        的工程师不会被清maintenance_place）；不要求检修目标当前仍有损坏记录（无损坏时会随机选目标）
    """
    cache = cache_control.cache
    ri = cache.rhodes_island
    cd = cache.character_data
    failures = []
    facility_damage_data = getattr(ri, "facility_damage_data", None)
    if isinstance(facility_damage_data, dict):
        illegal_damage = [
            (p, v) for p, v in facility_damage_data.items() if not (p in cache.scene_data and type(v) is int and v >= 1)
        ]
        if illegal_damage:
            failures.append(
                make_failure(
                    "ISLAND-30",
                    "设施损坏数据与检修分派自洽",
                    f"facility_damage_data非法键/值明细={illegal_damage}",
                    [],
                )
            )
    maintenance_place = getattr(ri, "maintenance_place", None)
    if isinstance(maintenance_place, dict):
        illegal_maintenance = [
            (cid, place)
            for cid, place in maintenance_place.items()
            if not (cid in cd and cd[cid].work.work_type == 21 and place in cache.scene_data)
        ]
        if illegal_maintenance:
            detail = [
                f"cid={cid},{_chara_name(cd, cid)},work_type={cd[cid].work.work_type if cid in cd else None},"
                f"{_sp_flag_brief(cd.get(cid))},place_in_scene_data={place in cache.scene_data}"
                for cid, place in illegal_maintenance
            ]
            failures.append(
                make_failure(
                    "ISLAND-30",
                    "设施损坏数据与检修分派自洽",
                    f"maintenance_place非法明细={illegal_maintenance}，涉及角色详情={detail}",
                    [cid for cid, _place in illegal_maintenance if cid in cd],
                )
            )
    return failures


@register_check("ISLAND-31", "访客集合与待确认招募集合合法")
def check_island_31_visitor_and_recruited_id() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验visitor_info是dict，键均为存在的角色，访客数不超过visitor_max；recruited_id是集合、不含0、
        成员均存在，且与已招募名单不相交。不断言"访客必须在npc_id_got"（访客同样可能被绑架而离线）；不断言
        "干员数<=people_max"（访客计入名单但只受客房数约束，属设计内流程，不在本条硬检查范围）
    """
    cache = cache_control.cache
    ri = cache.rhodes_island
    cd = cache.character_data
    failures = []
    visitor_info = getattr(ri, "visitor_info", None)
    visitor_max = getattr(ri, "visitor_max", None)
    if isinstance(visitor_info, dict):
        ghost_visitors = [v for v in visitor_info if v not in cd]
        if ghost_visitors or (visitor_max is not None and len(visitor_info) > visitor_max):
            failures.append(
                make_failure(
                    "ISLAND-31",
                    "访客集合与待确认招募集合合法",
                    f"len(visitor_info)={len(visitor_info)}，visitor_max={visitor_max}，幽灵访客id={ghost_visitors}",
                    ghost_visitors,
                )
            )
    recruited_id = getattr(ri, "recruited_id", None)
    if isinstance(recruited_id, set):
        conflict = recruited_id & cache.npc_id_got
        ghost_recruited = [r for r in recruited_id if r not in cd]
        if 0 in recruited_id or ghost_recruited or conflict:
            conflict_detail = [(r, _chara_name(cd, r)) for r in conflict]
            failures.append(
                make_failure(
                    "ISLAND-31",
                    "访客集合与待确认招募集合合法",
                    f"recruited_id含0={0 in recruited_id}，幽灵成员={ghost_recruited}，"
                    f"recruited_id与npc_id_got交集={conflict_detail}",
                    list(conflict) + ghost_recruited,
                )
            )
    return failures


@register_check("ISLAND-32", "贸易子设施列表与开放表一致、不超上限、无重复")
def check_island_32_shop_open_list() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验shop_open_list无重名、长度不超过贸易区(cid 11)当前等级效果值，且其中每个名称都对应一个贸易区
        可建设施且该设施已开放。反向不成立、禁止加：贸易区5级会经zone_cid规则自动开放全部151-168号子设施
        而不append到shop_open_list，"facility_open为真⇒名字在列表里"是必现误报
    """
    cache = cache_control.cache
    ri = cache.rhodes_island
    shop_open_list = getattr(ri, "shop_open_list", None)
    if not isinstance(shop_open_list, list):
        return []
    eff11 = _eff(ri, 11)
    trade_open = {
        o.name: oid for oid, o in game_config.config_facility_open.items() if 111 <= o.zone_cid <= 115
    }
    facility_open = getattr(ri, "facility_open", {})
    failures = []
    dup_names = [n for n, cnt in Counter(shop_open_list).items() if cnt > 1]
    if dup_names:
        failures.append(
            make_failure(
                "ISLAND-32",
                "贸易子设施列表与开放表一致、不超上限、无重复",
                f"shop_open_list重复名={dup_names}，全量={shop_open_list}",
                [],
            )
        )
    if eff11 is not None and len(shop_open_list) > eff11:
        failures.append(
            make_failure(
                "ISLAND-32",
                "贸易子设施列表与开放表一致、不超上限、无重复",
                f"len(shop_open_list)={len(shop_open_list)}超过_eff(11)={eff11}，"
                f"facility_level[11]={getattr(ri, 'facility_level', {}).get(11)}",
                [],
            )
        )
    unmatched = [
        (name, trade_open.get(name)) for name in shop_open_list
        if name not in trade_open or not facility_open.get(trade_open[name], False)
    ]
    if unmatched:
        failures.append(
            make_failure(
                "ISLAND-32",
                "贸易子设施列表与开放表一致、不超上限、无重复",
                f"在列表中但facility_open为假(或未匹配到设施)的设施名与open_cid={unmatched}",
                [],
            )
        )
    return failures


@register_check("ISLAND-33", "外交官映射、岗位与外派标记三方一致")
def check_island_33_diplomat_mapping_consistency() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        [warning] 校验diplomat_of_country[国家][0]的非零角色必须存在、sp_flag.in_diplomatic_visit等于该国家、
        work.work_type==131，且一人不得同时负责两国；反过来任何in_diplomatic_visit!=0的角色都必须正是该国
        映射所指的人。定为告警是因为有UI可达的破坏路径（改派现任外交官为别的岗位、任命候选表不排除已负责
        他国的角色），都是设计缺陷而非数据损坏
    """
    cache = cache_control.cache
    ri = cache.rhodes_island
    cd = cache.character_data
    diplomat_of_country = getattr(ri, "diplomat_of_country", None)
    if not isinstance(diplomat_of_country, dict):
        return []
    failures = []
    seen: Dict[int, int] = {}
    for country, v in diplomat_of_country.items():
        if not (isinstance(v, list) and len(v) >= 2):
            failures.append(
                make_failure(
                    "ISLAND-33",
                    "外交官映射、岗位与外派标记三方一致",
                    f"[warning] country_id={country}的diplomat_of_country记录结构非法：{v!r}",
                    [],
                )
            )
            continue
        did = v[0]
        if not did:
            continue
        if did not in cd:
            failures.append(
                make_failure(
                    "ISLAND-33",
                    "外交官映射、岗位与外派标记三方一致",
                    f"[warning] country_id={country}指向的diplomat_id={did}在character_data中不存在",
                    [],
                )
            )
            continue
        if did in seen:
            failures.append(
                make_failure(
                    "ISLAND-33",
                    "外交官映射、岗位与外派标记三方一致",
                    f"[warning] diplomat_id={did}({cd[did].name})同时被country_id={seen[did]}与country_id={country}"
                    f"两国映射引用，一人负责的全部国家列表={[seen[did], country]}",
                    [did],
                )
            )
            continue
        seen[did] = country
        ch = cd[did]
        if ch.sp_flag.in_diplomatic_visit != country or ch.work.work_type != 131:
            failures.append(
                make_failure(
                    "ISLAND-33",
                    "外交官映射、岗位与外派标记三方一致",
                    f"[warning] country_id={country}，diplomat_id={did}({ch.name})，"
                    f"实际work.work_type={ch.work.work_type}(期望131)，"
                    f"实际sp_flag.in_diplomatic_visit={ch.sp_flag.in_diplomatic_visit}(期望{country})，"
                    f"current_location[0]={getattr(ri, 'current_location', [None])[0] if getattr(ri, 'current_location', None) else None}",
                    [did],
                )
            )
    for cid, ch in cd.items():
        if cid and ch.sp_flag.in_diplomatic_visit:
            if seen.get(cid) != ch.sp_flag.in_diplomatic_visit:
                failures.append(
                    make_failure(
                        "ISLAND-33",
                        "外交官映射、岗位与外派标记三方一致",
                        f"[warning] 角色cid={cid}({ch.name})的sp_flag.in_diplomatic_visit={ch.sp_flag.in_diplomatic_visit}，"
                        f"但diplomat_of_country[{ch.sp_flag.in_diplomatic_visit}]未指回该角色"
                        f"(实际映射到seen.get(cid)={seen.get(cid)})",
                        [cid],
                    )
                )
    return failures
