# -*- coding: UTF-8 -*-
"""
静态检查系统 - 服装/污浊/妊娠/身体素质领域检查
实现 BODY-01 ~ BODY-35 共35条不变式检查。
本模块内的检查函数只读取快照状态，绝不修改任何游戏数据；所有字段访问均做防御式处理，
即使存档结构异常也只会产生失败记录而不会抛出异常。
排序约定：BODY-01/10/31 为形状前置条件，后续检查在形状不成立时跳过对应条目而非二次报错。
"""
import datetime
import math
from typing import List, Optional, Tuple

from Script.Core import cache_control
from ..check_registry import CheckFailure, register_check, make_failure


def _num(x) -> bool:
    """
    参数:
        x: 任意值
    返回值:
        bool: x为有限的非bool数值时返回True
    功能:
        判断x是否为可安全参与大小比较的数值（排除bool与NaN/inf）
    """
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def _get_config_sets() -> Tuple[Optional[set], Optional[set], Optional[dict]]:
    """
    参数:
        无
    返回值:
        Tuple[Optional[set], Optional[set], Optional[dict]]: (服装部位id集合CT, 身体部位id集合BP, 服装模板配置表TEM)，配置未加载时对应项为None
    功能:
        统一获取本模块依赖的三张配置表；独立运行环境下配置可能未加载，此时相关检查退化为跳过
    """
    try:
        from Script.Config import game_config
    except Exception:
        return None, None, None
    ct = set(game_config.config_clothing_type) if getattr(game_config, "config_clothing_type", None) else None
    bp = set(game_config.config_body_part) if getattr(game_config, "config_body_part", None) else None
    tem = game_config.config_clothing_tem if getattr(game_config, "config_clothing_tem", None) else None
    return ct, bp, tem


def _iter_charas():
    """
    参数:
        无
    返回值:
        迭代器: 依次产出 (角色id, 角色对象) 二元组
    功能:
        遍历cache.character_data中的全部角色，cache未初始化时产出空序列
    """
    cache = cache_control.cache
    if cache is None or not isinstance(getattr(cache, "character_data", None), dict):
        return
    for cid, chara in cache.character_data.items():
        yield cid, chara


def _name(chara) -> str:
    """
    参数:
        chara: 角色对象
    返回值:
        str: 角色名，取不到时返回"?"
    功能:
        防御式获取角色名用于拼接失败信息
    """
    return str(getattr(chara, "name", "?"))


def _cloth_locs(chara) -> Optional[List[Tuple[str, dict]]]:
    """
    参数:
        chara: 角色对象
    返回值:
        Optional[List[Tuple[str, dict]]]: 四个服装容器的 (容器名, 字典) 列表；cloth结构缺失时返回None
    功能:
        统一取出穿着/脱下/大浴场衣柜/宿舍衣柜四个容器，供各服装检查复用
    """
    cloth = getattr(chara, "cloth", None)
    if cloth is None:
        return None
    locs = []
    for attr_name in ("cloth_wear", "cloth_off", "cloth_locker_in_shower", "cloth_locker_in_dormitory"):
        d = getattr(cloth, attr_name, None)
        if not isinstance(d, dict):
            return None
        locs.append((attr_name, d))
    return locs


def _talent_get(chara, talent_id: int) -> int:
    """
    参数:
        chara: 角色对象
        talent_id (int): 素质id
    返回值:
        int: 素质取值，结构异常时返回0
    功能:
        防御式读取素质值，避免素质表缺键时检查器自身抛KeyError
    """
    talent = getattr(chara, "talent", None)
    if not isinstance(talent, dict):
        return 0
    value = talent.get(talent_id, 0)
    return value if isinstance(value, int) and not isinstance(value, bool) else 0


def _dirty_tables(chara) -> Optional[List[Tuple[str, dict]]]:
    """
    参数:
        chara: 角色对象
    返回值:
        Optional[List[Tuple[str, dict]]]: 三张污浊表的 (表名, 字典) 列表；dirty结构缺失时返回None
    功能:
        统一取出身体/在穿服装/衣柜服装三张精液记录表
    """
    dirty = getattr(chara, "dirty", None)
    if dirty is None:
        return None
    tables = []
    for attr_name in ("body_semen", "cloth_semen", "cloth_locker_semen"):
        d = getattr(dirty, attr_name, None)
        if not isinstance(d, dict):
            return None
        tables.append((attr_name, d))
    return tables


def _semen_entry_ok(v) -> bool:
    """
    参数:
        v: 污浊表条目
    返回值:
        bool: 条目为 [名字str, 当前量, 等级, 总量] 合法四元列表时返回True
    功能:
        校验单条精液记录的形状，供多个检查作为前置守卫复用
    """
    return isinstance(v, list) and len(v) == 4 and isinstance(v[0], str) and _num(v[1]) and type(v[2]) is int and _num(v[3])


@register_check("BODY-01", "服装四容器的部位键完整")
def check_cloth_container_keys() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表，四个服装容器键集完整且值均为list时为空
    功能:
        校验每个角色的穿着/脱下/大浴场衣柜/宿舍衣柜四表都按全部服装类型建键且值为list；
        运行期到处裸下标访问这些表，缺键即KeyError。存档迁移只修三张表且完全不修cloth_off，
        cloth_off是本条最主要的捕获目标
    """
    ct, _, _ = _get_config_sets()
    if ct is None:
        return []
    failures = []
    for cid, chara in _iter_charas():
        cloth = getattr(chara, "cloth", None)
        if cloth is None:
            failures.append(make_failure("BODY-01", "服装四容器的部位键完整", f"角色id={cid}({_name(chara)})缺少cloth结构", [cid]))
            continue
        for attr_name in ("cloth_wear", "cloth_off", "cloth_locker_in_shower", "cloth_locker_in_dormitory"):
            d = getattr(cloth, attr_name, None)
            if not isinstance(d, dict):
                failures.append(make_failure("BODY-01", "服装四容器的部位键完整", f"角色id={cid}({_name(chara)})的{attr_name}不是dict: {type(d).__name__}", [cid]))
                continue
            missing = ct - set(d)
            extra = set(d) - ct
            bad_values = [t for t, lst in d.items() if not isinstance(lst, list)]
            if missing or extra or bad_values:
                failures.append(
                    make_failure(
                        "BODY-01",
                        "服装四容器的部位键完整",
                        f"角色id={cid}({_name(chara)})的{attr_name}键集异常: 缺失{sorted(missing)} 多余{sorted(extra)} 非list值槽位{sorted(bad_values)}",
                        [cid],
                    )
                )
    return failures


@register_check("BODY-02", "服装id有效且在正确槽位")
def check_cloth_id_validity() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验四容器内所有元素都是配置中存在的服装模板id（非0占位），且模板的clothing_type等于所在槽位号。
        服装模板id是载入期动态生成的，角色CSV增删服装列会让旧存档id指向另一件衣服，
        「id仍在但部位变了」与「陈旧id藏在衣柜里」两种损坏都能存活过迁移，是本条的捕获目标
    """
    ct, _, tem = _get_config_sets()
    if ct is None or tem is None:
        return []
    failures = []
    for cid, chara in _iter_charas():
        locs = _cloth_locs(chara)
        if locs is None:
            continue  # 形状问题由BODY-01负责报告
        for attr_name, d in locs:
            for t, lst in d.items():
                if not isinstance(lst, list):
                    continue
                for c in lst:
                    # 先判类型与存在性，再取模板属性，避免非法id让检查器自身KeyError
                    if type(c) is not int or c == 0 or c not in tem:
                        failures.append(make_failure("BODY-02", "服装id有效且在正确槽位", f"角色id={cid}({_name(chara)})的{attr_name}[{t}]含非法服装id: {c!r}", [cid]))
                    elif getattr(tem[c], "clothing_type", None) != t:
                        failures.append(
                            make_failure(
                                "BODY-02",
                                "服装id有效且在正确槽位",
                                f"角色id={cid}({_name(chara)})的{attr_name}[{t}]中服装id={c}({getattr(tem[c], 'name', '?')})的clothing_type={getattr(tem[c], 'clothing_type', None)}与槽位不符",
                                [cid],
                            )
                        )
    return failures


@register_check("BODY-03", "同一槽位内不得有重复服装id")
def check_cloth_slot_duplicates() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验同一容器同一槽位的列表内无重复模板id；重复说明某条穿戴路径重复append，
        会造成重复显示、重复移除、特殊装备叠加
    """
    failures = []
    for cid, chara in _iter_charas():
        locs = _cloth_locs(chara)
        if locs is None:
            continue
        for attr_name, d in locs:
            for t, lst in d.items():
                # 仅在元素全部可哈希（int）时判重，混入脏类型由BODY-02报告
                if not isinstance(lst, list) or any(type(c) is not int for c in lst):
                    continue
                if len(lst) != len(set(lst)):
                    dup = sorted({c for c in lst if lst.count(c) > 1})
                    failures.append(make_failure("BODY-03", "同一槽位内不得有重复服装id", f"角色id={cid}({_name(chara)})的{attr_name}[{t}]存在重复服装id{dup}: {lst}", [cid]))
    return failures


@register_check("BODY-04", "穿着与脱下不应相交")
def check_wear_off_disjoint() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验同一槽位的cloth_wear与cloth_off无交集。结算函数自身声明二者互斥，但其移除循环边迭代边remove会漏删；
        另有合法可达的污染路径（get_npc_cloth重填在身服装但不触碰cloth_off），故降为warning
    """
    failures = []
    for cid, chara in _iter_charas():
        locs = _cloth_locs(chara)
        if locs is None:
            continue
        loc_dict = dict(locs)
        wear, off = loc_dict.get("cloth_wear", {}), loc_dict.get("cloth_off", {})
        for t in wear:
            lst_w, lst_o = wear.get(t), off.get(t)
            if not isinstance(lst_w, list) or not isinstance(lst_o, list):
                continue
            if any(type(c) is not int for c in lst_w) or any(type(c) is not int for c in lst_o):
                continue
            inter = set(lst_w) & set(lst_o)
            if inter:
                failures.append(
                    make_failure("BODY-04", "穿着与脱下不应相交", f"[warning] 角色id={cid}({_name(chara)})槽位{t}的穿着与脱下同时含有{sorted(inter)}: wear={lst_w} off={lst_o}", [cid])
                )
    return failures


# BODY-05（已退役，2026-08-28，含其修复一并撤除）：曾断言"同一服装id不得同时出现在穿着/大浴场衣柜/宿舍
# 衣柜三处物理位置中的两处以上"。sol调查+opus复核确认该断言在当前数据模型下不可判定（不是"同一件算正常"，
# 而是数据结构本身不支持判断）：容器里存的是服装模板编号，不是每件实体的唯一UID，无法区分"同一件正在转移中
# 途留痕"与"两件模板号相同的不同实体各自摆在两处"；且存在两条会产生模板号跨位置重复的合法生成路径——
# 睡眠重掷（行为650→634）与get_npc_cloth的整套CSV驱动换装（RESTE_CLOTH效果）——双持在这个数据模型下是
# 正常噪声而非错配信号。曾配套的修复"按 穿着>宿舍>浴场 优先级去重"已证明对携带CSV专属内衣的角色有害：
# 从衣柜删掉"重复"项后，下次该角色重新换装会随机塞入替代服装，专属内衣永久丢失=内容损毁，故随检查一并
# 撤除，不保留降级版本。BODY-03/BODY-06继续覆盖穿着/脱下相交、专属服装归属错位等真实可判定的异常。


@register_check("BODY-06", "角色专属服装不得出现在他人处")
def check_exclusive_cloth_owner() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验专属服装（模板npc字段非0）只出现在adv与之相符的角色身上或衣柜里。
        玩家(cid 0)、动态新生儿、adv==0的角色语义不同，一律排除。
        角色替换迁移是否同步改写adv尚未确认，故暂列warning
    """
    _, _, tem = _get_config_sets()
    if tem is None:
        return []
    failures = []
    for cid, chara in _iter_charas():
        adv = getattr(chara, "adv", 0)
        if cid == 0 or not isinstance(adv, int) or adv <= 0:
            continue
        locs = _cloth_locs(chara)
        if locs is None:
            continue
        for attr_name, d in locs:
            for t, lst in d.items():
                if not isinstance(lst, list):
                    continue
                for c in lst:
                    if type(c) is int and c in tem:
                        owner = getattr(tem[c], "npc", 0)
                        if owner not in (0, adv):
                            failures.append(
                                make_failure(
                                    "BODY-06",
                                    "角色专属服装不得出现在他人处",
                                    f"[warning] 角色id={cid}({_name(chara)}, adv={adv})的{attr_name}[{t}]持有专属于npc={owner}的服装id={c}({getattr(tem[c], 'name', '?')})",
                                    [cid],
                                )
                            )
    return failures


@register_check("BODY-07", "内衣可见性字典形状")
def check_cloth_see_shape() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验cloth_see必须含6(胸衣)与9(内裤)两个被裸下标访问的键，偷袜子会合法加入10；键为int，值严格为bool。
        下界{6,9}不能省，空dict虽能过宽松检查但保障不了裸下标访问
    """
    failures = []
    for cid, chara in _iter_charas():
        cloth = getattr(chara, "cloth", None)
        if cloth is None:
            continue
        see = getattr(cloth, "cloth_see", None)
        ok = (
            isinstance(see, dict)
            and {6, 9} <= set(see) <= {6, 9, 10}
            and all(type(k) is int and type(v) is bool for k, v in see.items())
        )
        if not ok:
            failures.append(make_failure("BODY-07", "内衣可见性字典形状", f"角色id={cid}({_name(chara)})的cloth_see形状异常: {see!r}", [cid]))
    return failures


@register_check("BODY-08", "装备情况数值有界")
def check_equipment_condition_bound() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验equipment_condition为有限数值且在[-4, 2]内。下界-4来自6级委托的损坏概率表（该表必然产生-4），
        不要从状况配置表推导下界；保养会产生小数，不得断言int
    """
    failures = []
    for cid, chara in _iter_charas():
        cloth = getattr(chara, "cloth", None)
        if cloth is None:
            continue
        val = getattr(cloth, "equipment_condition", 0)
        if not _num(val) or not (-4 <= val <= 2):
            failures.append(make_failure("BODY-08", "装备情况数值有界", f"角色id={cid}({_name(chara)})的equipment_condition越界: {val!r} (合法范围[-4,2])", [cid]))
    return failures


@register_check("BODY-09", "装饰避孕套挂点合法")
def check_condom_decoration() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验condom_decoration的键为(部位类型,部位cid)二元组：类型0只允许头发(0,0)；类型1必须是合法服装部位
        且该部位当前有衣服；值为非负数值列表（允许空列表）。脱衣函数漏调remove_cloth_decoration会稳定留下
        悬空挂点，首轮命中应按bug处理，故降为warning
    """
    ct, _, _ = _get_config_sets()
    if ct is None:
        return []
    failures = []
    for cid, chara in _iter_charas():
        dirty = getattr(chara, "dirty", None)
        cloth = getattr(chara, "cloth", None)
        if dirty is None or cloth is None:
            continue
        deco = getattr(dirty, "condom_decoration", None)
        if deco is None:
            continue
        if not isinstance(deco, dict):
            failures.append(make_failure("BODY-09", "装饰避孕套挂点合法", f"[warning] 角色id={cid}({_name(chara)})的condom_decoration不是dict: {type(deco).__name__}", [cid]))
            continue
        wear = getattr(cloth, "cloth_wear", None)
        for k, v in deco.items():
            key_ok = isinstance(k, tuple) and len(k) == 2 and type(k[0]) is int and type(k[1]) is int
            if key_ok:
                if k == (0, 0):
                    pos_ok = True
                elif k[0] == 1 and k[1] in ct:
                    pos_ok = isinstance(wear, dict) and isinstance(wear.get(k[1]), list) and len(wear[k[1]]) > 0
                else:
                    pos_ok = False
            else:
                pos_ok = False
            value_ok = isinstance(v, list) and all(_num(x) and x >= 0 for x in v)
            if not (key_ok and pos_ok and value_ok):
                failures.append(make_failure("BODY-09", "装饰避孕套挂点合法", f"[warning] 角色id={cid}({_name(chara)})的condom_decoration存在非法挂点: 键={k!r} 值={v!r}", [cid]))
    return failures


@register_check("BODY-10", "精液记录表键集与条目形状")
def check_semen_table_shape() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验body_semen覆盖全部身体部位、cloth_semen覆盖全部服装部位（均被裸下标访问）；
        cloth_locker_semen允许为空dict（新建角色经get_dirty_reset的合法基线，该函数不初始化此表），
        但非空时必须覆盖全部服装部位——半初始化才是危险状态。每个条目是[名字,当前量,等级,总量]四元list。
        用>=而非==，容忍存档里的旧多余键
    """
    ct, bp, _ = _get_config_sets()
    if ct is None or bp is None:
        return []
    failures = []
    for cid, chara in _iter_charas():
        tables = _dirty_tables(chara)
        if tables is None:
            failures.append(make_failure("BODY-10", "精液记录表键集与条目形状", f"角色id={cid}({_name(chara)})的污浊表结构缺失或类型错误", [cid]))
            continue
        table_dict = dict(tables)
        if not set(table_dict["body_semen"]) >= bp:
            failures.append(make_failure("BODY-10", "精液记录表键集与条目形状", f"角色id={cid}({_name(chara)})的body_semen缺失身体部位键{sorted(bp - set(table_dict['body_semen']))}", [cid]))
        if not set(table_dict["cloth_semen"]) >= ct:
            failures.append(make_failure("BODY-10", "精液记录表键集与条目形状", f"角色id={cid}({_name(chara)})的cloth_semen缺失服装部位键{sorted(ct - set(table_dict['cloth_semen']))}", [cid]))
        locker = table_dict["cloth_locker_semen"]
        if locker != {} and not set(locker) >= ct:
            failures.append(make_failure("BODY-10", "精液记录表键集与条目形状", f"角色id={cid}({_name(chara)})的cloth_locker_semen半初始化(非空但缺键{sorted(ct - set(locker))})，裸下标访问会KeyError", [cid]))
        for table_name, d in tables:
            for p, v in d.items():
                if not _semen_entry_ok(v):
                    failures.append(make_failure("BODY-10", "精液记录表键集与条目形状", f"角色id={cid}({_name(chara)})的{table_name}[{p!r}]条目形状异常: {v!r}", [cid]))
    return failures


@register_check("BODY-11", "精液量非负")
def check_semen_non_negative() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验三张污浊表的当前量[1]与累计量[3]均非负，以及累计吸收量非负。
        形状异常条目由BODY-10负责，此处跳过；数值可能是float（灌肠结算写入浮点），不强制int
    """
    failures = []
    for cid, chara in _iter_charas():
        tables = _dirty_tables(chara)
        if tables is None:
            continue
        for table_name, d in tables:
            for p, v in d.items():
                if _semen_entry_ok(v) and (v[1] < 0 or v[3] < 0):
                    failures.append(make_failure("BODY-11", "精液量非负", f"角色id={cid}({_name(chara)})的{table_name}[{p!r}]出现负量: 当前量={v[1]} 累计量={v[3]}", [cid]))
        absorbed = getattr(getattr(chara, "dirty", None), "absorbed_total_semen", 0)
        if not (_num(absorbed) and absorbed >= 0):
            failures.append(make_failure("BODY-11", "精液量非负", f"角色id={cid}({_name(chara)})的absorbed_total_semen非法: {absorbed!r}", [cid]))
    return failures


@register_check("BODY-12", "累计精液量不小于当前量")
def check_semen_total_ge_current() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表（聚合为至多一条）
    功能:
        校验累计量[3]恒>=当前量[1]。已知缺陷：衣柜精液并回在穿服装时只加当前量不加累计量，
        「脏衣服进浴场→再穿回」的常规循环会稳定违反本条，故降为warning并聚合上报避免逐角色刷屏
    """
    hits = []
    for cid, chara in _iter_charas():
        tables = _dirty_tables(chara)
        if tables is None:
            continue
        for table_name, d in tables:
            for p, v in d.items():
                if _semen_entry_ok(v) and v[3] < v[1]:
                    hits.append((cid, table_name, p, v[1], v[3]))
    if not hits:
        return []
    sample = "; ".join(f"cid={h[0]} {h[1]}[{h[2]!r}] 当前{h[3]}>累计{h[4]}" for h in hits[:5])
    return [
        make_failure(
            "BODY-12",
            "累计精液量不小于当前量",
            f"[warning] 共{len(hits)}处累计量小于当前量(已知衣柜并回路径缺陷的特征): {sample}{' ...' if len(hits) > 5 else ''}",
            sorted({h[0] for h in hits}),
        )
    ]


@register_check("BODY-13", "精液等级与当前量同步")
def check_semen_level_sync() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验等级[2]等于以当前量[1]重算的纯函数结果（get_semen_now_level），不一致说明某处改量未刷新等级，
        会让描述文本、灌肠量、受精率算错。只遍历配置内的键（跳过存档残留旧键），part_type对衣柜表传1即可（结果等价）
    """
    ct, bp, _ = _get_config_sets()
    if ct is None or bp is None:
        return []
    try:
        from Script.Design import attr_calculation
    except Exception:
        return []  # 独立运行环境缺依赖时退化为跳过
    failures = []
    for cid, chara in _iter_charas():
        tables = _dirty_tables(chara)
        if tables is None:
            continue
        table_dict = dict(tables)
        for table_name, key_set, part_type in (("body_semen", bp, 0), ("cloth_semen", ct, 1), ("cloth_locker_semen", ct, 1)):
            d = table_dict[table_name]
            for p, v in d.items():
                if p not in key_set or not _semen_entry_ok(v):
                    continue
                try:
                    expect = attr_calculation.get_semen_now_level(v[1], p, part_type)
                except Exception:
                    continue  # 配置不全时纯函数可能失败，跳过而非误报
                if v[2] != expect:
                    failures.append(make_failure("BODY-13", "精液等级与当前量同步", f"角色id={cid}({_name(chara)})的{table_name}[{p}]等级失步: 量={v[1]} 记录等级={v[2]} 期望等级={expect}", [cid]))
    return failures


@register_check("BODY-14", "衣柜精液与在穿精液不得共享list对象")
def check_semen_list_aliasing() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表（聚合为至多一条）
    功能:
        校验cloth_semen[t]与cloth_locker_semen[t]不是同一个list对象。已知真实别名缺陷：
        脱袜子鞋子进浴场时直接赋值不拷贝，会在10/11槽稳定命中；此后改一处会静默连带改另一处。
        聚合上报避免刷屏
    """
    ct, _, _ = _get_config_sets()
    if ct is None:
        return []
    hits = []
    for cid, chara in _iter_charas():
        dirty = getattr(chara, "dirty", None)
        if dirty is None:
            continue
        cloth_semen = getattr(dirty, "cloth_semen", None)
        locker_semen = getattr(dirty, "cloth_locker_semen", None)
        if not isinstance(cloth_semen, dict) or not isinstance(locker_semen, dict):
            continue
        if cloth_semen is locker_semen:
            hits.append((cid, "整表同一对象"))
            continue
        for t in ct:
            if t in cloth_semen and t in locker_semen and cloth_semen[t] is locker_semen[t] and isinstance(cloth_semen[t], list):
                hits.append((cid, f"槽位{t}共享同一list(id={id(cloth_semen[t])})"))
    if not hits:
        return []
    sample = "; ".join(f"cid={h[0]} {h[1]}" for h in hits[:5])
    return [make_failure("BODY-14", "衣柜精液与在穿精液不得共享list对象", f"[warning] 共{len(hits)}处发现别名共享(已知脱袜入浴场路径缺陷): {sample}{' ...' if len(hits) > 5 else ''}", sorted({h[0] for h in hits}))]


@register_check("BODY-15", "兽部有精液则须有对应兽部素质")
def check_beast_part_semen_talent() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验尾巴12/兽角13/兽耳14的当前精液量非零时角色必须持有对应素质113/112/111
        （射精入口按素质拦截，有量无素质说明数据被别的路径写脏）。用当前量而非累计量，避免历史残留误报
    """
    failures = []
    for cid, chara in _iter_charas():
        tables = _dirty_tables(chara)
        if tables is None:
            continue
        body_semen = dict(tables)["body_semen"]
        for part, talent_id in ((12, 113), (13, 112), (14, 111)):
            v = body_semen.get(part)
            if _semen_entry_ok(v) and v[1] > 0 and not _talent_get(chara, talent_id):
                failures.append(make_failure("BODY-15", "兽部有精液则须有对应兽部素质", f"角色id={cid}({_name(chara)})的body_semen[{part}]有量{v[1]}但缺少素质{talent_id}", [cid]))
    return failures


@register_check("BODY-16", "灌肠状态与容量配对")
def check_enema_state() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验a_clean∈{0..4}、enema_capacity∈{0..6}（上界以代码封顶为准，注释的1~5不准确），
        且正容量只应出现在「灌肠中1/精液灌肠中3」两个进行态。用type is int排除bool
    """
    failures = []
    for cid, chara in _iter_charas():
        dirty = getattr(chara, "dirty", None)
        if dirty is None:
            continue
        a_clean = getattr(dirty, "a_clean", 0)
        capacity = getattr(dirty, "enema_capacity", 0)
        ok = type(a_clean) is int and 0 <= a_clean <= 4 and type(capacity) is int and 0 <= capacity <= 6 and (capacity == 0 or a_clean in (1, 3))
        if not ok:
            failures.append(make_failure("BODY-16", "灌肠状态与容量配对", f"角色id={cid}({_name(chara)})的灌肠状态非法: a_clean={a_clean!r} enema_capacity={capacity!r}", [cid]))
    return failures


@register_check("BODY-17", "精液流通表结构合法")
def check_semen_flow_shape() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验semen_flow每项含source(type/id)与targets；源类型0身体/1服装，目标类型0/1/2（2为环境滴落，id恒0）；
        remaining_volume为正整数。不得要求targets非空——流通表配置为「无」的部位会合法生成空targets条目，
        清理只发生在下一次实时结算，快照可能落在两者之间
    """
    ct, bp, _ = _get_config_sets()
    if ct is None or bp is None:
        return []
    failures = []
    for cid, chara in _iter_charas():
        flow = getattr(getattr(chara, "dirty", None), "semen_flow", None)
        if flow is None:
            continue
        if not isinstance(flow, list):
            failures.append(make_failure("BODY-17", "精液流通表结构合法", f"角色id={cid}({_name(chara)})的semen_flow不是list: {type(flow).__name__}", [cid]))
            continue
        for f in flow:
            ok = (
                isinstance(f, dict)
                and set(f) == {"source", "targets"}
                and isinstance(f.get("source"), dict)
                and set(f["source"]) == {"type", "id"}
                and ((f["source"]["type"] == 0 and f["source"]["id"] in bp) or (f["source"]["type"] == 1 and f["source"]["id"] in ct))
                and isinstance(f.get("targets"), list)
                and all(
                    isinstance(t, dict)
                    and set(t) == {"type", "id", "remaining_volume"}
                    and ((t["type"] == 0 and t["id"] in bp) or (t["type"] == 1 and t["id"] in ct) or (t["type"] == 2 and t["id"] == 0))
                    and type(t["remaining_volume"]) is int
                    and t["remaining_volume"] > 0
                    for t in f["targets"]
                )
            )
            if not ok:
                failures.append(make_failure("BODY-17", "精液流通表结构合法", f"角色id={cid}({_name(chara)})的semen_flow含非法条目: {f!r}", [cid]))
    return failures


@register_check("BODY-18", "玩家不应有精液流通")
def check_player_no_semen_flow() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验玩家(cid 0)的semen_flow恒为空列表——流通构造与实时结算的玩家分支都不处理流通表，
        玩家身上出现流通项说明写错了对象
    """
    cache = cache_control.cache
    if cache is None or not isinstance(getattr(cache, "character_data", None), dict) or 0 not in cache.character_data:
        return []
    flow = getattr(getattr(cache.character_data[0], "dirty", None), "semen_flow", None)
    if isinstance(flow, list) and flow == []:
        return []
    if flow is None:
        return []
    return [make_failure("BODY-18", "玩家不应有精液流通", f"玩家的semen_flow应为空列表，实际: {flow!r}", [0])]


@register_check("BODY-19", "无意识精液记录列表有效且去重")
def check_unconscious_semen_lists() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验body_semen_in_unconscious/cloth_semen_in_unconscious两列表元素为合法部位号int且无重复
        （写入处用not in判重，重复即状态破损）。元素类型检查先于set()，避免不可哈希元素让检查器自身崩溃
    """
    ct, bp, _ = _get_config_sets()
    if ct is None or bp is None:
        return []
    failures = []
    for cid, chara in _iter_charas():
        dirty = getattr(chara, "dirty", None)
        if dirty is None:
            continue
        for attr_name, key_set in (("body_semen_in_unconscious", bp), ("cloth_semen_in_unconscious", ct)):
            lst = getattr(dirty, attr_name, None)
            if lst is None:
                continue
            if not isinstance(lst, list) or any(type(x) is not int for x in lst):
                failures.append(make_failure("BODY-19", "无意识精液记录列表有效且去重", f"角色id={cid}({_name(chara)})的{attr_name}类型异常: {lst!r}", [cid]))
                continue
            if not set(lst) <= key_set or len(set(lst)) != len(lst):
                failures.append(make_failure("BODY-19", "无意识精液记录列表有效且去重", f"角色id={cid}({_name(chara)})的{attr_name}含越界或重复元素: {lst}", [cid]))
    return failures


@register_check("BODY-20", "阴茎污浊字典键值")
def check_penis_dirty_dict() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验penis_dirty_dict的键仅为"semen"/"blood"，值严格为bool；默认空dict合法
    """
    failures = []
    for cid, chara in _iter_charas():
        d = getattr(getattr(chara, "dirty", None), "penis_dirty_dict", None)
        if d is None:
            continue
        ok = isinstance(d, dict) and set(d) <= {"semen", "blood"} and all(type(v) is bool for v in d.values())
        if not ok:
            failures.append(make_failure("BODY-20", "阴茎污浊字典键值", f"角色id={cid}({_name(chara)})的penis_dirty_dict形状异常: {d!r}", [cid]))
    return failures


@register_check("BODY-21", "生理周期日为配置内合法值")
def check_reproduction_period() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验reproduction_period是int且存在于config_reproduction_period（该值被直接当配置下标，越界即KeyError）。
        用配置成员判断而非range(7)，既跟随配置又避免True被判合法
    """
    try:
        from Script.Config import game_config
    except Exception:
        return []
    period_config = getattr(game_config, "config_reproduction_period", None)
    if not period_config:
        return []
    failures = []
    for cid, chara in _iter_charas():
        period = getattr(getattr(chara, "pregnancy", None), "reproduction_period", None)
        if period is None:
            continue
        if type(period) is not int or period not in period_config:
            failures.append(make_failure("BODY-21", "生理周期日为配置内合法值", f"角色id={cid}({_name(chara)})的reproduction_period非法: {period!r} (配置键{sorted(period_config)})", [cid]))
    return failures


@register_check("BODY-22", "受精/妊娠/临盆三阶段互斥")
def check_pregnancy_stage_exclusive() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验素质20受精/21妊娠/22临盆至多持有一个（单向迁移，每次先清旧再置新，同持两个即状态机破裂）。
        育儿24不纳入：代码显式允许育儿中再次受精
    """
    failures = []
    for cid, chara in _iter_charas():
        stages = [i for i in (20, 21, 22) if _talent_get(chara, i)]
        if len(stages) > 1:
            failures.append(make_failure("BODY-22", "受精/妊娠/临盆三阶段互斥", f"角色id={cid}({_name(chara)})同时持有妊娠阶段素质{stages}", [cid]))
    return failures


@register_check("BODY-23", "产后/育儿互斥且须有可追溯的孩子")
def check_postpartum_child() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验素质23产后与24育儿互斥；两者任一成立时child_id_list须为非空list且末位id存在于character_data
        （推进函数无保护读取child_id_list[-1]并索引character_data，空列表或悬空id直接崩溃）。
        [-1]取值写在长度判断之后，避免检查器自身IndexError
    """
    cache = cache_control.cache
    failures = []
    for cid, chara in _iter_charas():
        t23, t24 = _talent_get(chara, 23), _talent_get(chara, 24)
        if t23 and t24:
            failures.append(make_failure("BODY-23", "产后/育儿互斥且须有可追溯的孩子", f"角色id={cid}({_name(chara)})同时持有产后23与育儿24", [cid]))
        if t23 or t24:
            child_list = getattr(getattr(chara, "relationship", None), "child_id_list", None)
            if not (isinstance(child_list, list) and len(child_list) > 0 and child_list[-1] in cache.character_data):
                failures.append(make_failure("BODY-23", "产后/育儿互斥且须有可追溯的孩子", f"角色id={cid}({_name(chara)})处于产后/育儿阶段但child_id_list无效: {child_list!r} (崩溃级)", [cid]))
    return failures


@register_check("BODY-24", "怀孕中须有有效受精时间")
def check_fertilization_time() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验处于素质20/21/22任一阶段的角色，其fertilization_time是有效datetime（非默认值年份1）且不晚于当前游戏时间
        （阶段推进全靠该时间差，默认值或未来值会让角色瞬间跳到临盆或永远卡住）。未受精角色的默认值合法
    """
    cache = cache_control.cache
    game_time = getattr(cache, "game_time", None) if cache is not None else None
    if not isinstance(game_time, datetime.datetime):
        return []
    failures = []
    for cid, chara in _iter_charas():
        if not any(_talent_get(chara, i) for i in (20, 21, 22)):
            continue
        ft = getattr(getattr(chara, "pregnancy", None), "fertilization_time", None)
        if not (isinstance(ft, datetime.datetime) and ft.year > 1 and ft <= game_time):
            failures.append(make_failure("BODY-24", "怀孕中须有有效受精时间", f"角色id={cid}({_name(chara)})处于妊娠阶段但fertilization_time无效: {ft!r} (game_time={game_time})", [cid]))
    return failures


@register_check("BODY-25", "孕肚素质与妊娠/临盆绑定")
def check_pregnancy_belly_talent() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验素质26孕肚成立当且仅当角色处于21妊娠或22临盆（进入妊娠时授予、分娩时移除）。
        debug面板可单独改素质造成失步，debug模式下跳过，故为warning
    """
    cache = cache_control.cache
    if cache is not None and getattr(cache, "debug_mode", False):
        return []
    failures = []
    for cid, chara in _iter_charas():
        belly = bool(_talent_get(chara, 26))
        pregnant = bool(_talent_get(chara, 21) or _talent_get(chara, 22))
        if belly != pregnant:
            failures.append(make_failure("BODY-25", "孕肚素质与妊娠/临盆绑定", f"[warning] 角色id={cid}({_name(chara)})孕肚素质失步: talent26={belly} 妊娠/临盆={pregnant}", [cid]))
    return failures


@register_check("BODY-26", "乳汁量有界且上限为正")
def check_milk_bounds() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验milk/milk_max为有限数值、milk_max>0（被当分母，<=0会ZeroDivisionError）、0<=milk<=milk_max。
        先确认有限非bool数值，NaN会静默绕过两侧比较。催乳存在瞬时超限中间态，但每回合一次的检查点看不到
    """
    failures = []
    for cid, chara in _iter_charas():
        preg = getattr(chara, "pregnancy", None)
        if preg is None:
            continue
        milk = getattr(preg, "milk", 0)
        milk_max = getattr(preg, "milk_max", 0)
        if not (_num(milk) and _num(milk_max) and milk_max > 0 and 0 <= milk <= milk_max):
            failures.append(make_failure("BODY-26", "乳汁量有界且上限为正", f"角色id={cid}({_name(chara)})乳汁量非法: milk={milk!r} milk_max={milk_max!r}", [cid]))
    return failures


@register_check("BODY-27", "涨奶标记蕴含泌乳素质")
def check_lactation_flag() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验lactation_flag为真时素质27必为1。素质27被关掉后既无法清flag也无法缩回罩杯，
        该永久残留可由合法操作（礼物面板关素质）触发，正是要抓的漏洞，故保留但标为warning
    """
    failures = []
    for cid, chara in _iter_charas():
        flag = getattr(getattr(chara, "pregnancy", None), "lactation_flag", False)
        if flag and _talent_get(chara, 27) != 1:
            failures.append(make_failure("BODY-27", "涨奶标记蕴含泌乳素质", f"[warning] 角色id={cid}({_name(chara)})的lactation_flag残留但素质27已失去", [cid]))
    return failures


@register_check("BODY-28", "罩杯素质有且只有一个")
def check_cup_talent_unique() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验非玩家、非机械体角色的罩杯素质121~125恰好持有一个（胸部成长函数假定必有其一，
        缺失会UnboundLocalError，崩溃级）。玩家与机械体(race==2)模板无罩杯素质，必须排除
    """
    failures = []
    for cid, chara in _iter_charas():
        if cid == 0 or getattr(chara, "race", 0) == 2:
            continue
        hit = [i for i in range(121, 126) if _talent_get(chara, i)]
        if len(hit) != 1:
            failures.append(make_failure("BODY-28", "罩杯素质有且只有一个", f"角色id={cid}({_name(chara)})罩杯素质数异常: 命中{hit} (崩溃级)", [cid]))
    return failures


@register_check("BODY-29", "臀/腿/足素质各组至多一个")
def check_body_part_talent_groups() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验126-128(臀)、129-130(腿)、131-132(足)三组互斥档位各至多持有一个。
        用<=1而非==1：成长函数对全0有兜底，机械模板全0合法
    """
    failures = []
    for cid, chara in _iter_charas():
        for group in ((126, 127, 128), (129, 130), (131, 132)):
            hit = [i for i in group if _talent_get(chara, i)]
            if len(hit) > 1:
                failures.append(make_failure("BODY-29", "臀/腿/足素质各组至多一个", f"角色id={cid}({_name(chara)})互斥素质组{group}同时命中{hit}", [cid]))
    return failures


@register_check("BODY-30", "动态女儿年龄阶段素质有且只有一个")
def check_age_stage_talent() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验动态女儿（cid!=0且relationship.father_id==0，即父亲为玩家的新生角色）的年龄阶段素质101~107
        恰好持有一个（108长生者可叠加体质不参与）。范围必须收窄到动态女儿：静态干员模板存在同持两档或
        全无年龄档的情况，全域检查会稳定误报；father_id默认-1，动态出生时才写0
    """
    failures = []
    for cid, chara in _iter_charas():
        if cid == 0 or getattr(getattr(chara, "relationship", None), "father_id", -1) != 0:
            continue
        hit = [i for i in range(101, 108) if _talent_get(chara, i)]
        if len(hit) != 1:
            failures.append(make_failure("BODY-30", "动态女儿年龄阶段素质有且只有一个", f"角色id={cid}({_name(chara)})年龄阶段素质数异常: 命中{hit}", [cid]))
    return failures


@register_check("BODY-31", "素质字典完整且取值为0/1")
def check_talent_dict_shape() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验talent字典覆盖config_talent全部键（全库大量裸下标访问，缺键即KeyError），键为int、值为int且取值0/1。
        必须是配置⊆存档方向：迁移只补缺失键、从不删除废弃键；type is int排除True/False。
        本条是BODY-22/28/29/30的前置条件；迁移的len()守卫在多余键数恰好等于缺失键数时不修复，本条正好能报出这类存档
    """
    try:
        from Script.Config import game_config
    except Exception:
        return []
    talent_config = getattr(game_config, "config_talent", None)
    if not talent_config:
        return []
    config_keys = set(talent_config)
    failures = []
    for cid, chara in _iter_charas():
        talent = getattr(chara, "talent", None)
        if not isinstance(talent, dict):
            failures.append(make_failure("BODY-31", "素质字典完整且取值为0/1", f"角色id={cid}({_name(chara)})的talent不是dict: {type(talent).__name__}", [cid]))
            continue
        missing = config_keys - set(talent)
        bad = [(k, v) for k, v in talent.items() if type(k) is not int or type(v) is not int or v not in (0, 1)]
        if missing or bad:
            failures.append(make_failure("BODY-31", "素质字典完整且取值为0/1", f"角色id={cid}({_name(chara)})素质表异常: 缺失键{sorted(missing)} 非法键值{bad[:10]}", [cid]))
    return failures


@register_check("BODY-32", "精液流通源须仍有可扣减的容器")
def check_semen_flow_source_container() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表（聚合为至多一条）
    功能:
        校验semen_flow中源为服装部位(类型1)的条目，其源槽位当前必须有衣服——结算先给目标加量再对源扣量，
        源槽已无衣服时扣量函数提前return，导致凭空复制精液。H过程中脱衣即可产生该状态，命中较频繁，
        聚合统计上报，每次命中都对应一次真实的量凭空增加
    """
    hits = []
    for cid, chara in _iter_charas():
        dirty = getattr(chara, "dirty", None)
        cloth = getattr(chara, "cloth", None)
        if dirty is None or cloth is None:
            continue
        flow = getattr(dirty, "semen_flow", None)
        wear = getattr(cloth, "cloth_wear", None)
        if not isinstance(flow, list) or not isinstance(wear, dict):
            continue
        for f in flow:
            if not isinstance(f, dict) or not isinstance(f.get("source"), dict):
                continue  # 结构问题由BODY-17负责
            src = f["source"]
            if src.get("type") == 1:
                slot = wear.get(src.get("id"))
                if isinstance(slot, list) and len(slot) == 0:
                    hits.append((cid, src.get("id")))
    if not hits:
        return []
    sample = "; ".join(f"cid={h[0]} 源槽位{h[1]}" for h in hits[:5])
    return [make_failure("BODY-32", "精液流通源须仍有可扣减的容器", f"[warning] 共{len(hits)}条流通的服装源槽位已无衣服(扣量将落空、凭空复制): {sample}{' ...' if len(hits) > 5 else ''}", sorted({h[0] for h in hits}))]


@register_check("BODY-33", "机械体妊娠须有生育模组")
def check_mechanical_pregnancy() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验机械体(race==2)角色处于素质20/21/22/26任一阶段时必须持有素质171生育模组
        （受精入口对无模组机械体显式拦截并清零受精率，无正常产生路径）。
        素质171可能被通用素质开关授予后又关掉，构成合法误报，且debug存档常见，故为warning且debug模式跳过
    """
    cache = cache_control.cache
    if cache is not None and getattr(cache, "debug_mode", False):
        return []
    failures = []
    for cid, chara in _iter_charas():
        if getattr(chara, "race", 0) != 2 or _talent_get(chara, 171):
            continue
        hit = [i for i in (20, 21, 22, 26) if _talent_get(chara, i)]
        if hit:
            failures.append(make_failure("BODY-33", "机械体妊娠须有生育模组", f"[warning] 机械体角色id={cid}({_name(chara)})无素质171却处于妊娠相关阶段{hit}", [cid]))
    return failures


@register_check("BODY-34", "产后/育儿所引用的孩子须有有效出生时间")
def check_child_born_time() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验处于素质23/24阶段的角色，其末位孩子的born_time是有效datetime（非默认年份1）且不晚于当前游戏时间
        （阶段推进直接用该时间算天数，默认值会让状态瞬间跨过阈值）。
        仅在BODY-23的孩子引用有效时才评估，避免空列表/悬空id让检查器自身崩溃；
        debug面板会改写born_time推进育儿，故为warning
    """
    cache = cache_control.cache
    game_time = getattr(cache, "game_time", None) if cache is not None else None
    if not isinstance(game_time, datetime.datetime):
        return []
    failures = []
    for cid, chara in _iter_charas():
        if not (_talent_get(chara, 23) or _talent_get(chara, 24)):
            continue
        child_list = getattr(getattr(chara, "relationship", None), "child_id_list", None)
        # BODY-23前置条件：孩子引用必须有效，否则由BODY-23报告，此处跳过
        if not (isinstance(child_list, list) and len(child_list) > 0 and child_list[-1] in cache.character_data):
            continue
        child = cache.character_data[child_list[-1]]
        born_time = getattr(getattr(child, "pregnancy", None), "born_time", None)
        if not (isinstance(born_time, datetime.datetime) and born_time.year > 1 and born_time <= game_time):
            failures.append(
                make_failure(
                    "BODY-34",
                    "产后/育儿所引用的孩子须有有效出生时间",
                    f"[warning] 角色id={cid}({_name(chara)})的末位孩子id={child_list[-1]}({_name(child)})的born_time无效: {born_time!r} (game_time={game_time})",
                    [cid, child_list[-1]],
                )
            )
    return failures


@register_check("BODY-35", "个人服装模板列表有效")
def check_clothing_tem_list() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验clothing_tem为有效服装模板id组成的list。本条近乎空转（该字段写入后无改动路径），
        级别为最低优先级warning；不做去重要求（无证据表明模板列表会去重）
    """
    _, _, tem = _get_config_sets()
    if tem is None:
        return []
    failures = []
    for cid, chara in _iter_charas():
        lst = getattr(getattr(chara, "cloth", None), "clothing_tem", None)
        if lst is None:
            continue
        if not isinstance(lst, list) or any(type(x) is not int or x not in tem for x in lst):
            bad = lst if not isinstance(lst, list) else [x for x in lst if type(x) is not int or x not in tem]
            failures.append(make_failure("BODY-35", "个人服装模板列表有效", f"[warning] 角色id={cid}({_name(chara)}, adv={getattr(chara, 'adv', '?')})的clothing_tem含无效项: {bad!r}", [cid]))
    return failures
