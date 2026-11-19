# -*- coding: UTF-8 -*-
"""
静态检查系统 - 补充盲点检查
本模块实现 SUPP-01…SUPP-08：不属于任何单一领域模块的盲点条目（来源编号 IO-01、IO-02、IO-05、
MO-03、NO-01、NO-03、NO-05、PO-02）。各检查以文档字符串完整表述不变式本身，文档字符串首行注明来源编号。

约定与全域前提（与其余领域模块一致，此处不重复展开）：
1. 全部字段访问一律使用getattr/dict.get加默认值防御，绝不能因老存档缺字段或类型不符而抛异常；
   若某个结构性假设本身就是不变量的一部分，则让比较结果记为"不变量失败"，而不是让检查器自己崩溃。
2. 配表访问一律走Script.Config.game_config，检查函数只在真正执行时才引用配表字典，一旦某个配表字段本身缺失，
   对应检查退化为跳过（返回空列表），不影响其余检查项。
3. severity约定：消息文本以"[warning] "为前缀的是警示级（已知存在合法/历史漂移窗口，仅作诊断参考）；
   无前缀的是错误级（无合法反例，命中即代表真实状态损坏）。
"""
from types import FunctionType
from typing import List

from Script.Core import cache_control, get_text
from Script.Config import game_config
from Script.Design import map_handle
from ..check_registry import CheckFailure, register_check, make_failure

# 场景路径列表 -> map_handle路径字符串；内部用os.sep拼接，禁止自己写分隔符
P = map_handle.get_map_system_path_str_for_list
# 翻译api，SUPP-02判定"客房"名称时需要与basement.py同样按本地化后的名称比对
_: FunctionType = get_text._


def _eff(ri, facility_cid: int):
    """
    参数:
        ri: cache.rhodes_island 罗德岛数据对象
        facility_cid (int): 设施配置cid（config_facility的键）
    返回值:
        int|None: 该设施在其当前等级下的效果数值(config_facility_effect.effect)，任何一环缺失/越界时返回None
    功能:
        _eff(fid)帮助函数：config_facility_effect[config_facility_effect_data[名字][等级]].effect，
        全程防御式访问，任一层级配置/存档字段缺失都安全地返回None而不抛异常
    """
    try:
        facility = game_config.config_facility.get(facility_cid)
        if facility is None:
            return None
        level = getattr(ri, "facility_level", {}).get(facility_cid)
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


def _all_current_effect_cids(ri) -> List[int]:
    """
    参数:
        ri: cache.rhodes_island 罗德岛数据对象
    返回值:
        List[int]: 全部设施在其当前等级下对应的效果cid列表，单个设施数据缺失时静默跳过该设施
    功能:
        对应basement.get_base_updata()中"遍历全设施清单，按当前等级取效果cid"的只读复刻，
        供SUPP-03的开放覆盖判定复用，一次性计算避免对每个待开放项重复全表扫描
    """
    result = []
    facility_level = getattr(ri, "facility_level", {}) or {}
    for facility_cid, facility_data in game_config.config_facility.items():
        try:
            level = facility_level.get(facility_cid)
            if type(level) is not int:
                continue
            facility_name = facility_data.name
            effect_data = game_config.config_facility_effect_data.get(facility_name)
            if effect_data is None or not (0 <= level < len(effect_data)):
                continue
            result.append(effect_data[level])
        except Exception:
            continue
    return result


@register_check("SUPP-01", "供电策略合法性")
def check_power_supply_strategy_validity() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能:
        来源: IO-01。校验cache.rhodes_island.power_supply_strategy的键值域：键必须是当前配置中
        type==-1的大区块设施cid，值必须是game_config.config_supply_strategy的合法键。管理面板只为该类
        大区块初始化键并在合法值间轮换；消费端basement.calc_facility_efficiency先把子设施折算到父区块，
        再对策略配置做无保护索引，非法键说明派生表结构损坏，非法值会直接KeyError
    """
    cache = cache_control.cache
    ri = getattr(cache, "rhodes_island", None)
    strategy = getattr(ri, "power_supply_strategy", None)
    if not isinstance(strategy, dict):
        return []
    valid_zone_cids = {cid for cid, fac in game_config.config_facility.items() if getattr(fac, "type", None) == -1}
    valid_strategy_ids = set(game_config.config_supply_strategy)
    failures = []
    for zone_cid, strategy_id in strategy.items():
        if zone_cid not in valid_zone_cids:
            failures.append(
                make_failure(
                    "SUPP-01",
                    "供电策略合法性",
                    f"power_supply_strategy中的键zone_cid={zone_cid}不是当前配置中type==-1的大区块设施cid"
                    f"（合法区块集合={sorted(valid_zone_cids)}），basement.calc_facility_efficiency按此键折算子设施供电策略时会取到脏数据",
                    [],
                )
            )
        if strategy_id not in valid_strategy_ids:
            failures.append(
                make_failure(
                    "SUPP-01",
                    "供电策略合法性",
                    f"power_supply_strategy[{zone_cid}]={strategy_id}不在合法策略id集合{sorted(valid_strategy_ids)}中，"
                    f"basement.calc_facility_efficiency会对game_config.config_supply_strategy[{strategy_id}]做无保护索引，直接KeyError",
                    [],
                )
            )
    return failures


@register_check("SUPP-02", "生活娱乐/科研/士兵/访客上限派生一致")
def check_facility_derived_max_consistency() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能:
        来源: IO-02。校验life_zone_max/research_zone_max/soldier_max分别与设施cid 5/8/21
        当前等级效果一致，visitor_max与当前config_facility_open中名称含"客房"且facility_open为真的数量一致。
        级别为warning：这四个字段只由get_base_updata()在若干面板打开时派生刷新，没有每回合自动刷新点，
        跨版本配置变化或读档到首次打开相关面板之前，短暂/历史漂移是合法状态而非硬损坏
    """
    cache = cache_control.cache
    ri = getattr(cache, "rhodes_island", None)
    if ri is None:
        return []
    eff5 = _eff(ri, 5)
    eff8 = _eff(ri, 8)
    eff21 = _eff(ri, 21)
    if eff5 is None or eff8 is None or eff21 is None:
        return []
    facility_open = getattr(ri, "facility_open", {}) or {}
    expected_visitor_max = sum(
        1 for oid, room in game_config.config_facility_open.items() if _("客房") in getattr(room, "name", "") and facility_open.get(oid, False)
    )
    failures = []
    checks = (
        ("life_zone_max", eff5, 5),
        ("research_zone_max", eff8, 8),
        ("soldier_max", eff21, 21),
        ("visitor_max", expected_visitor_max, None),
    )
    for field_name, expected, facility_cid in checks:
        actual = getattr(ri, field_name, None)
        if actual != expected:
            failures.append(
                make_failure(
                    "SUPP-02",
                    "生活娱乐/科研/士兵/访客上限派生一致",
                    f"[warning] ri.{field_name}={actual}，重算期望值={expected}"
                    + (f"（_eff({facility_cid})，facility_level[{facility_cid}]={getattr(ri, 'facility_level', {}).get(facility_cid)}）" if facility_cid is not None else "（当前开放客房数）")
                    + "，可能是跨版本配置变化后尚未刷新，或某条设施更新路径漏调get_base_updata()",
                    [],
                )
            )
    return failures


@register_check("SUPP-03", "设施开放派生单调覆盖")
def check_facility_open_monotonic_coverage() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能:
        来源: IO-05。对当前config_facility_open中每个待开放项，只要其zone_cid已被全设施
        当前等级效果cid覆盖（相等，或同十位且个位数达标），对应facility_open[open_cid]就应为真。
        只迭代当前配置键，不查存档中的历史多余键；不检查反向"未覆盖就必须关闭"，因为开放只增不减，
        配置降级/mod可合法保留历史开放项。级别为warning：刷新同样只在打开面板时发生，跨版本读档到首次
        刷新前可合法不一致
    """
    cache = cache_control.cache
    ri = getattr(cache, "rhodes_island", None)
    if ri is None:
        return []
    effect_cids = _all_current_effect_cids(ri)
    if not effect_cids:
        return []
    facility_open = getattr(ri, "facility_open", {}) or {}

    def _covered(zone_cid: int) -> bool:
        """
        参数:
            zone_cid (int): 待开放项要求的区块等级cid
        返回值:
            bool: 是否被全设施当前效果cid集合覆盖
        功能:
            basement.get_base_updata()中判定式的只读复刻：effect_cid==zone_cid，或同十位且effect_cid个位数>=zone_cid个位数
        """
        return any(effect_cid == zone_cid or (effect_cid // 10 == zone_cid // 10 and effect_cid % 10 >= zone_cid % 10) for effect_cid in effect_cids)

    failures = []
    for open_cid, room in game_config.config_facility_open.items():
        zone_cid = getattr(room, "zone_cid", None)
        if type(zone_cid) is not int:
            continue
        if _covered(zone_cid) and not facility_open.get(open_cid, False):
            failures.append(
                make_failure(
                    "SUPP-03",
                    "设施开放派生单调覆盖",
                    f"[warning] 待开放项open_cid={open_cid}({getattr(room, 'name', '')})要求的zone_cid={zone_cid}已被当前设施等级效果覆盖，"
                    f"但facility_open.get({open_cid})={facility_open.get(open_cid, False)}，疑似开放派生表未刷新或get_base_updata()漏项",
                    [],
                )
            )
    return failures


@register_check("SUPP-04", "时停无意识值跨名单残留")
def check_time_stop_unconscious_survives_off_list() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能:
        来源: MO-03。非时停时，character_data中任何角色都不应残留专属时停无意识值
        unconscious_h==3；不得以是否在npc_id_got中过滤（TIME_STOP_ON/OFF都只扫描当时的npc_id_got|{0}，
        角色可能在时停中因访客离开或debug操作被移出名单，关闭时停后便再也清不到）。级别为warning：
        新周目继承整张character_data也可能把历史残留带入
    """
    cache = cache_control.cache
    if cache is None or getattr(cache, "time_stop_mode", False):
        return []
    character_data = getattr(cache, "character_data", {}) or {}
    npc_id_got = getattr(cache, "npc_id_got", set()) or set()
    failures = []
    for cid, c in character_data.items():
        sp_flag = getattr(c, "sp_flag", None)
        if getattr(sp_flag, "unconscious_h", 0) != 3:
            continue
        failures.append(
            make_failure(
                "SUPP-04",
                "时停无意识值跨名单残留",
                f"[warning] 角色id={cid} name={getattr(c, 'name', '')}的sp_flag.unconscious_h=3，但当前time_stop_mode=False；"
                f"是否在npc_id_got中={cid in npc_id_got}，field_commission={getattr(sp_flag, 'field_commission', None)}，"
                f"escaping={getattr(sp_flag, 'escaping', None)}，be_bagged={getattr(sp_flag, 'be_bagged', None)}，"
                f"vistor={getattr(sp_flag, 'vistor', None)}，position={getattr(c, 'position', None)}，"
                f"疑似TIME_STOP_OFF清理范围漏掉了时停中已离开名单的角色",
                [cid],
            )
        )
    return failures


@register_check("SUPP-05", "愤怒值下界")
def check_angry_point_lower_bound() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能:
        来源: NO-01。校验每个角色的angry_point类型为int且不小于0。道歉和听牢骚等指令路径的减法写点
        已用max(..., 0)钳制下界，本条为保护性检查，守住该不变量不被新写点破坏。下游把<=30当作正常阈值，
        显示逻辑又会把负数落入最低愤怒档，因此负值一旦出现即语义不成立。级别为warning
    """
    cache = cache_control.cache
    character_data = getattr(cache, "character_data", {}) or {}
    failures = []
    for cid, c in character_data.items():
        angry_point = getattr(c, "angry_point", 0)
        if type(angry_point) is not int or angry_point < 0:
            failures.append(
                make_failure(
                    "SUPP-05",
                    "愤怒值下界",
                    f"[warning] 角色id={cid} name={getattr(c, 'name', '')}的angry_point={angry_point}，类型或值不满足"
                    f"type是int且>=0",
                    [cid],
                )
            )
    return failures


@register_check("SUPP-06", "模板对象别名")
def check_no_template_object_aliasing() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能:
        来源: NO-03。校验任一角色实例的ability/experience/talent字典都不得与任一NPC模板
        对应字典是同一个对象（用id()判等，不比较值）。角色新建时把模板的Ability/Experience/Talent直接赋给
        实例，成长会原地修改并污染进程级模板、跨周目泄漏。先收集全部模板对象id集合做O(1)查找，
        不做角色×模板的嵌套恒等比较。级别为warning：当前代码对按模板创建的角色会立即命中，属既存缺陷探测
    """
    cache = cache_control.cache
    npc_tem_data = getattr(cache, "npc_tem_data", {}) or {}
    character_data = getattr(cache, "character_data", {}) or {}
    template_ability_ids = {id(t.Ability) for t in npc_tem_data.values() if hasattr(t, "Ability")}
    template_experience_ids = {id(t.Experience) for t in npc_tem_data.values() if hasattr(t, "Experience")}
    template_talent_ids = {id(t.Talent) for t in npc_tem_data.values() if hasattr(t, "Talent")}
    failures = []
    for cid, c in character_data.items():
        hit_fields = []
        if hasattr(c, "ability") and id(c.ability) in template_ability_ids:
            hit_fields.append("ability")
        if hasattr(c, "experience") and id(c.experience) in template_experience_ids:
            hit_fields.append("experience")
        if hasattr(c, "talent") and id(c.talent) in template_talent_ids:
            hit_fields.append("talent")
        if hit_fields:
            failures.append(
                make_failure(
                    "SUPP-06",
                    "模板对象别名",
                    f"[warning] 角色id={cid} name={getattr(c, 'name', '')}的字段{hit_fields}与某个NPC模板的对应字典共享对象identity，"
                    f"adv={getattr(c, 'adv', None)}；该角色的成长会原地修改并污染进程级模板，导致后续新角色/新周目继承脏数据",
                    [cid],
                )
            )
    return failures


@register_check("SUPP-07", "仓储扩展模块使用数非负")
def check_used_extra_warehouse_capacity_module_non_negative() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能:
        来源: NO-05（只取独立于NUM-26的后半式）。校验cache.rhodes_island.
        used_extra_warehouse_capacity_module类型为int且不小于0。该计数参与
        warehouse_capacity=base+used*200并在装配线面板增量更新容量，负数没有玩法语义，
        且会把派生仓储容量向下扣减，可能在基础容量仍足够大时绕过既有的warehouse_capacity>=0检查。
        使用type(v) is int以拒绝bool
    """
    cache = cache_control.cache
    ri = getattr(cache, "rhodes_island", None)
    if ri is None:
        return []
    used = getattr(ri, "used_extra_warehouse_capacity_module", 0)
    if type(used) is not int or used < 0:
        return [
            make_failure(
                "SUPP-07",
                "仓储扩展模块使用数非负",
                f"cache.rhodes_island.used_extra_warehouse_capacity_module={used}，类型或值不满足type是int且>=0；"
                f"warehouse_capacity={getattr(ri, 'warehouse_capacity', None)}，facility_level[3]={getattr(ri, 'facility_level', {}).get(3)}",
                [],
            )
        ]
    return []


@register_check("SUPP-08", "办公室场景引用合法")
def check_officeroom_reference_valid() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能:
        来源: PO-02。校验character_data中每个角色的officeroom（列表字段）只允许是空列表或
        cache.scene_data的合法键。officeroom非空时会被角色信息面板交给get_scene_path_text，后者把坐标
        拼成路径后直接索引cache.scene_data；存档迁移只原样复制而不校验。级别为warning：当前主要后果是
        打开角色信息时渲染失败，且旧档兼容是主要来源
    """
    cache = cache_control.cache
    character_data = getattr(cache, "character_data", {}) or {}
    scene_data = getattr(cache, "scene_data", {}) or {}
    failures = []
    for cid, c in character_data.items():
        officeroom = getattr(c, "officeroom", None)
        if not officeroom:
            continue
        if not (isinstance(officeroom, list) and all(isinstance(p, str) for p in officeroom) and P(officeroom) in scene_data):
            failures.append(
                make_failure(
                    "SUPP-08",
                    "办公室场景引用合法",
                    f"[warning] 角色id={cid} name={getattr(c, 'name', '')}的officeroom={officeroom}非空但不是cache.scene_data的合法键，"
                    f"打开该角色信息面板时get_scene_path_text会索引失败；position={getattr(c, 'position', None)}",
                    [cid],
                )
            )
    return failures
