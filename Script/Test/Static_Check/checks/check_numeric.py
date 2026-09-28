# -*- coding: UTF-8 -*-
"""
静态检查系统 - 数值范围域检查
覆盖 NUM-01…NUM-30，校验角色六大数值字典（ability/experience/juel/status_data/talent/favorability）的键集完整性、
各类当前值/上限值的合法范围，以及基地资源、仓库容量等全局数值状态。所有检查均为一次快照内的纯读取，无历史依赖。

执行顺序说明：NUM-01（字段存在且为dict）概念上必须先于其余检查，但框架按注册顺序、每个检查项独立try/except调用，
不存在"NUM-01失败则跳过后续检查"的机制；因此本文件里每一条检查在访问六大字典/性别/上限等结构前，都会用
getattr/.get加默认值的方式廉价地重新自检一遍，确保即便NUM-01已经报过错，本检查也绝不会因为AttributeError/
TypeError而抛出未捕获异常，只会跟着报"结构不满足前置条件"或安静跳过。

配表访问一律走 Script.Config.game_config，检查函数只在真正执行时才引用配表字典（模块顶层不做config_xxx是否
存在的强校验），一旦某个配表字段本身缺失，对应检查退化为跳过（返回空列表），不影响其余检查项。
"""
import math
from typing import Dict, List

from Script.Core import cache_control
from Script.Config import game_config
from ..check_registry import CheckFailure, register_check, make_failure

# 六个数值容器字段名，NUM-01及后续多条检查复用
_NUMERIC_DICT_FIELDS = ("ability", "experience", "juel", "status_data", "talent", "favorability")


def _is_finite_number(v) -> bool:
    """
    参数:
        v: 任意待检测值
    返回值:
        bool: v的类型是int或float且为有限数（非NaN/inf）时返回True
    功能:
        判断数值是否为"类型合法且有限"的实数，先做类型短路再调用math.isfinite，避免对None/字符串等非数值类型
        直接调用math.isfinite触发TypeError；同时type(...) in (int, float)正确排除bool（bool是int子类会被isinstance
        误判，但这里用的是type()精确匹配，不受影响）
    """
    return type(v) in (int, float) and math.isfinite(v)


def _chara_name(chara) -> str:
    """
    参数:
        chara: 角色对象
    返回值:
        str: 角色名字，取不到时返回"?"
    功能:
        安全获取角色名字，避免坏档角色对象连name字段都缺失时检查函数自身抛异常
    """
    return getattr(chara, "name", "?")


def _dict_field_ok(chara, field: str) -> bool:
    """
    参数:
        chara: 角色对象
        field (str): 字段名
    返回值:
        bool: 该字段存在且类型为dict时返回True
    功能:
        NUM-01核心判据的单字段版本，供后续各检查在真正使用某个数值字典前廉价复核该字段是否可安全当作dict使用，
        使各检查在NUM-01已经失败的坏档上依然不会抛异常
    """
    return type(getattr(chara, field, None)) is dict


@register_check("NUM-01", "数值容器字段存在且为dict")
def check_num_01_numeric_dict_fields_exist() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验六个数值字典字段(ability/experience/juel/status_data/talent/favorability)在每个角色对象上都存在且
        类型为dict。存档走pickle反序列化，pickle不执行__init__，旧存档缺失的实例属性没有类属性兜底，
        getattr(..., None)会返回None，本检查旨在捕获这类"旧存档字段缺失"而非单纯的类型损坏。
        本检查须排在NUM-02…NUM-16之前跑（框架按注册顺序执行），否则那些检查会抛AttributeError/TypeError而不是
        给出干净的失败报告。
    """
    cache = cache_control.cache
    failures = []
    for cid, chara in cache.character_data.items():
        type_map = {f: type(getattr(chara, f, None)).__name__ for f in _NUMERIC_DICT_FIELDS}
        if not all(type(getattr(chara, f, None)) is dict for f in _NUMERIC_DICT_FIELDS):
            failures.append(
                make_failure(
                    "NUM-01",
                    "数值容器字段存在且为dict",
                    f"角色cid={cid} name={_chara_name(chara)} 数值容器字段类型异常: {type_map}",
                    [cid],
                )
            )
    return failures


@register_check("NUM-02", "能力字典键集覆盖配表且键为纯int")
def check_num_02_ability_dict_keys() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验config_ability的每个id都在chara.ability中存在（配表⊆角色，方向不可颠倒——补零与迁移只补不删，
        角色⊆配表或键集相等的方向会在每份升级存档上每回合误报），且chara.ability的键类型均为精确int
        （避免Python集合里True==1、1.0==1造成的伪装键）。多余键是合法的旧存档残留，仅记录不作为失败条件。
        若config_ability配表本身不存在（独立运行/未初始化），本检查退化为跳过。
    """
    cache = cache_control.cache
    config_ability = getattr(game_config, "config_ability", None)
    if not isinstance(config_ability, dict):
        return []
    config_keys = set(config_ability)
    failures = []
    for cid, chara in cache.character_data.items():
        if not _dict_field_ok(chara, "ability"):
            continue
        ability = chara.ability
        missing = config_keys - set(ability)
        bad_key_type = not all(type(k) is int for k in ability)
        if missing or bad_key_type:
            extra = set(ability) - config_keys
            failures.append(
                make_failure(
                    "NUM-02",
                    "能力字典键集覆盖配表且键为纯int",
                    f"角色cid={cid} name={_chara_name(chara)} ability缺键={missing} 多余键(仅记录)={extra} "
                    f"非int键存在={bad_key_type}",
                    [cid],
                )
            )
    return failures


@register_check("NUM-03", "能力值必须是Ability_Lv_Adjust的合法键")
def check_num_03_ability_value_valid_lv() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验chara.ability的每个值都是config_ability_lv_adjust中的合法键（配表键仅0-10）。get_ability_adjust用能力值
        直接做字典下标且无.get兜底，越界值会在下一次进入该调用点时KeyError崩游戏。type(v) is int而非isinstance，
        避免False当键0、1.0当键1被放行。带cache.debug_mode守卫（debug面板可写任意整数）。
        若config_ability_lv_adjust配表不存在，本检查退化为跳过。
    """
    cache = cache_control.cache
    config_lv_adjust = getattr(game_config, "config_ability_lv_adjust", None)
    if not isinstance(config_lv_adjust, dict):
        return []
    if cache.debug_mode:
        return []
    config_ability = getattr(game_config, "config_ability", {}) if isinstance(getattr(game_config, "config_ability", None), dict) else {}
    valid_keys = set(config_lv_adjust)
    failures = []
    for cid, chara in cache.character_data.items():
        if not _dict_field_ok(chara, "ability"):
            continue
        for ability_id, value in chara.ability.items():
            if not (type(value) is int and value in valid_keys):
                ability_name = config_ability[ability_id].name if ability_id in config_ability else "?"
                failures.append(
                    make_failure(
                        "NUM-03",
                        "能力值必须是Ability_Lv_Adjust的合法键",
                        f"角色cid={cid} name={_chara_name(chara)} ability_id={ability_id}({ability_name}) "
                        f"value={value!r} 合法键={sorted(valid_keys)}",
                        [cid],
                    )
                )
    return failures


# NUM-04: 全库唯一可越过8级钳制的能力事件效果 CVE_A2_A|71_G_2（能力71=舌技），见 data/event/chara/0204_白金.json；
# 若日后新增能力事件效果，必须同步更新此白名单，否则本项退化为噪声
_NUM04_UNCLAMPED_ABILITY = {71}


@register_check("NUM-04", "能力等级不超过8（事件白名单除外）")
def check_num_04_ability_level_upper_bound() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验chara.ability的值不超过8（自动升级循环硬停在8）。能力71（舌技）在白名单内被排除——全库唯一一条能力
        事件效果CVE_A2_A|71_G_2可把已升到8的舌技推到10，不受此上限约束。超过8值得人工复核但不是硬失败，故为warning。
        带cache.debug_mode守卫。若config_ability配表不存在，取名字时退化为"?"，不影响主体判定。
    """
    cache = cache_control.cache
    if cache.debug_mode:
        return []
    config_ability = getattr(game_config, "config_ability", {}) if isinstance(getattr(game_config, "config_ability", None), dict) else {}
    failures = []
    for cid, chara in cache.character_data.items():
        if not _dict_field_ok(chara, "ability"):
            continue
        over = {k: v for k, v in chara.ability.items() if k not in _NUM04_UNCLAMPED_ABILITY and type(v) is int and v > 8}
        if over:
            detail = {k: (v, config_ability[k].name if k in config_ability else "?", config_ability[k].ability_type if k in config_ability else "?") for k, v in over.items()}
            failures.append(
                make_failure(
                    "NUM-04",
                    "能力等级不超过8（事件白名单除外）",
                    f"[warning] 角色cid={cid} name={_chara_name(chara)} adv={getattr(chara, 'adv', '?')} "
                    f"能力越界(id:(值,名字,类型))={detail}",
                    [cid],
                )
            )
    return failures


@register_check("NUM-05", "感度/扩张类能力与角色性别一致")
def check_num_05_ability_sex_consistency() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验sex_need标注为0(男)/1(女)的能力，对性别不符的角色应恒为0（自动升级明确跳过不符项）。非0说明角色性别
        被中途改写或存档串行。依赖NUM-02（键完整）与NUM-06（性别合法）先通过，本检查内部对二者做廉价复核以保持
        独立性。定为warning，因为也可能反映设计内的"双性/扶她"类扩展。带cache.debug_mode守卫。
    """
    cache = cache_control.cache
    if cache.debug_mode:
        return []
    config_ability = getattr(game_config, "config_ability", None)
    if not isinstance(config_ability, dict):
        return []
    failures = []
    for cid, chara in cache.character_data.items():
        sex = getattr(chara, "sex", None)
        if type(sex) is not int or sex not in (0, 1):
            continue  # 性别本身不合法，交由NUM-06报告，避免级联噪声
        if not _dict_field_ok(chara, "ability"):
            continue
        violations = {}
        for aid, d in config_ability.items():
            if d.sex_need in (0, 1) and d.sex_need != sex:
                value = chara.ability.get(aid)
                if value != 0:
                    violations[aid] = value
        if violations:
            detail = {k: (v, config_ability[k].name, config_ability[k].sex_need) for k, v in violations.items()}
            failures.append(
                make_failure(
                    "NUM-05",
                    "感度/扩张类能力与角色性别一致",
                    f"[warning] 角色cid={cid} name={_chara_name(chara)} sex={sex} "
                    f"性别不符的非零能力(id:(值,名字,sex_need))={detail}",
                    [cid],
                )
            )
    return failures


@register_check("NUM-06", "角色性别取值域")
def check_num_06_sex_domain() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验chara.sex只能是0或1。全库仅四处写.sex，均来自角色模板或玩家二选一创建流程，域外值无合法来源。
        本项是NUM-05的根因守卫。无debug_mode守卫（键集/取值域类检查不加该守卫）。
    """
    cache = cache_control.cache
    failures = []
    for cid, chara in cache.character_data.items():
        sex = getattr(chara, "sex", None)
        if not (type(sex) is int and sex in {0, 1}):
            failures.append(
                make_failure(
                    "NUM-06",
                    "角色性别取值域",
                    f"角色cid={cid} name={_chara_name(chara)} adv={getattr(chara, 'adv', '?')} sex={sex!r}",
                    [cid],
                )
            )
    return failures


@register_check("NUM-07", "经验字典键集覆盖配表且键为纯int")
def check_num_07_experience_dict_keys() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验config_experience的每个id都在chara.experience中存在（配表⊆角色），键类型均为精确int。能力升级需求
        裸下标chara.experience[need_type_id]，缺键即崩。多余键是合法残留，仅记录。
        若config_experience配表不存在，退化为跳过。
    """
    cache = cache_control.cache
    config_experience = getattr(game_config, "config_experience", None)
    if not isinstance(config_experience, dict):
        return []
    config_keys = set(config_experience)
    failures = []
    for cid, chara in cache.character_data.items():
        if not _dict_field_ok(chara, "experience"):
            continue
        experience = chara.experience
        missing = config_keys - set(experience)
        bad_key_type = not all(type(k) is int for k in experience)
        if missing or bad_key_type:
            extra = set(experience) - config_keys
            failures.append(
                make_failure(
                    "NUM-07",
                    "经验字典键集覆盖配表且键为纯int",
                    f"角色cid={cid} name={_chara_name(chara)} experience缺键={missing} 多余键(仅记录)={extra} "
                    f"非int键存在={bad_key_type}",
                    [cid],
                )
            )
    return failures


@register_check("NUM-08", "经验为非负整数")
def check_num_08_experience_non_negative() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验chara.experience的每个值都是非负整数。通用经验结算在任何增减后执行max(0, ...)，事件通道的经验操作
        转发给同一函数，因此也走同一套下限钳制。带cache.debug_mode守卫（debug面板允许负数直写）。
    """
    cache = cache_control.cache
    if cache.debug_mode:
        return []
    failures = []
    for cid, chara in cache.character_data.items():
        if not _dict_field_ok(chara, "experience"):
            continue
        bad = {k: v for k, v in chara.experience.items() if type(v) is not int or v < 0}
        if bad:
            failures.append(
                make_failure(
                    "NUM-08",
                    "经验为非负整数",
                    f"角色cid={cid} name={_chara_name(chara)} 非法经验值={bad}",
                    [cid],
                )
            )
    return failures


@register_check("NUM-09", "宝珠字典键集覆盖配表且键为纯int")
def check_num_09_juel_dict_keys() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验config_juel的每个id都在chara.juel中存在（配表⊆角色），键类型均为精确int。升级需求解析出的
        J<id>裸下标chara.juel[need_type_id]。多余键是合法残留，仅记录。若config_juel配表不存在，退化为跳过。
    """
    cache = cache_control.cache
    config_juel = getattr(game_config, "config_juel", None)
    if not isinstance(config_juel, dict):
        return []
    config_keys = set(config_juel)
    failures = []
    for cid, chara in cache.character_data.items():
        if not _dict_field_ok(chara, "juel"):
            continue
        juel = chara.juel
        missing = config_keys - set(juel)
        bad_key_type = not all(type(k) is int for k in juel)
        if missing or bad_key_type:
            extra = set(juel) - config_keys
            failures.append(
                make_failure(
                    "NUM-09",
                    "宝珠字典键集覆盖配表且键为纯int",
                    f"角色cid={cid} name={_chara_name(chara)} juel缺键={missing} 多余键(仅记录)={extra} "
                    f"非int键存在={bad_key_type}",
                    [cid],
                )
            )
    return failures


@register_check("NUM-10", "宝珠为非负整数")
def check_num_10_juel_non_negative() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验chara.juel的每个值都是非负整数。全部扣除路径都有前置校验或数学下界（升级前先比较再扣、面板夹到
        持有量、睡眠反发珠双侧扣减不透支）。带cache.debug_mode守卫（debug面板可写负数）。
    """
    cache = cache_control.cache
    if cache.debug_mode:
        return []
    failures = []
    for cid, chara in cache.character_data.items():
        if not _dict_field_ok(chara, "juel"):
            continue
        bad = {k: v for k, v in chara.juel.items() if type(v) is not int or v < 0}
        if bad:
            failures.append(
                make_failure(
                    "NUM-10",
                    "宝珠为非负整数",
                    f"角色cid={cid} name={_chara_name(chara)} 非法宝珠值={bad}",
                    [cid],
                )
            )
    return failures


@register_check("NUM-11", "素质字典键集覆盖配表且值为int")
def check_num_11_talent_dict_keys() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验config_talent的每个id都在chara.talent中存在（配表⊆角色），键与值类型均为精确int（排除bool）。
        素质在能力升级需求T<n>中被裸下标chara.talent[need_value]。不需要对玩家(cid 0)放宽——玩家先经
        get_talent_zero取得完整config_talent键集，再由get_Dr_talent_zero额外设置几项，只增不减。多余键是迁移
        残留，仅记录。若config_talent配表不存在，退化为跳过。
    """
    cache = cache_control.cache
    config_talent = getattr(game_config, "config_talent", None)
    if not isinstance(config_talent, dict):
        return []
    config_keys = set(config_talent)
    failures = []
    for cid, chara in cache.character_data.items():
        if not _dict_field_ok(chara, "talent"):
            continue
        talent = chara.talent
        missing = config_keys - set(talent)
        bad_key_type = not all(type(k) is int for k in talent)
        bad_value_type = not all(type(v) is int for v in talent.values())
        if missing or bad_key_type or bad_value_type:
            extra = set(talent) - config_keys
            failures.append(
                make_failure(
                    "NUM-11",
                    "素质字典键集覆盖配表且值为int",
                    f"角色cid={cid} name={_chara_name(chara)} talent缺键={missing} 多余键(仅记录)={extra} "
                    f"非int键存在={bad_key_type} 非int值存在={bad_value_type}",
                    [cid],
                )
            )
    return failures


@register_check("NUM-12", "状态值字典键集覆盖配表且键为纯int")
def check_num_12_status_data_dict_keys() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验config_character_state的每个id都在chara.status_data中存在（配表⊆角色），键类型均为精确int。
        刻印升级判定、二段行为判定、AI判定都按状态id裸下标。多余键是合法残留，仅记录。
        若config_character_state配表不存在，退化为跳过。
    """
    cache = cache_control.cache
    config_state = getattr(game_config, "config_character_state", None)
    if not isinstance(config_state, dict):
        return []
    config_keys = set(config_state)
    failures = []
    for cid, chara in cache.character_data.items():
        if not _dict_field_ok(chara, "status_data"):
            continue
        status_data = chara.status_data
        missing = config_keys - set(status_data)
        bad_key_type = not all(type(k) is int for k in status_data)
        if missing or bad_key_type:
            extra = set(status_data) - config_keys
            failures.append(
                make_failure(
                    "NUM-12",
                    "状态值字典键集覆盖配表且键为纯int",
                    f"角色cid={cid} name={_chara_name(chara)} status_data缺键={missing} 多余键(仅记录)={extra} "
                    f"非int键存在={bad_key_type}",
                    [cid],
                )
            )
    return failures


@register_check("NUM-13", "状态值为非负整数")
def check_num_13_status_data_non_negative() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验chara.status_data的每个值都是非负整数。通用状态结算写入前int()转换、写入后max(0, ...)，全库其余直写
        路径也逐行钳制且均为非负。带cache.debug_mode守卫。
    """
    cache = cache_control.cache
    if cache.debug_mode:
        return []
    failures = []
    for cid, chara in cache.character_data.items():
        if not _dict_field_ok(chara, "status_data"):
            continue
        bad = {k: v for k, v in chara.status_data.items() if type(v) is not int or v < 0}
        if bad:
            failures.append(
                make_failure(
                    "NUM-13",
                    "状态值为非负整数",
                    f"角色cid={cid} name={_chara_name(chara)} 非法状态值={bad} "
                    f"behavior_id={getattr(getattr(chara, 'behavior', None), 'behavior_id', '?')}",
                    [cid],
                )
            )
    return failures


@register_check("NUM-14", "状态值不超过99999")
def check_num_14_status_data_upper_bound() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验chara.status_data的每个值不超过99999。通用结算min(99999, ...)钳制，100000是等级表的哨兵阈值而非
        可保存的状态值。全库最大的状态事件效果远低于此值，越界属于罕见旁路，故为warning而非error。
        带cache.debug_mode守卫。
    """
    cache = cache_control.cache
    if cache.debug_mode:
        return []
    config_state = getattr(game_config, "config_character_state", {}) if isinstance(getattr(game_config, "config_character_state", None), dict) else {}
    failures = []
    for cid, chara in cache.character_data.items():
        if not _dict_field_ok(chara, "status_data"):
            continue
        over = {k: v for k, v in chara.status_data.items() if type(v) in (int, float) and v > 99999}
        if over:
            detail = {k: (v, config_state[k].name if k in config_state else "?") for k, v in over.items()}
            failures.append(
                make_failure(
                    "NUM-14",
                    "状态值不超过99999",
                    f"[warning] 角色cid={cid} name={_chara_name(chara)} 越界状态(id:(值,名字))={detail} "
                    f"behavior_id={getattr(getattr(chara, 'behavior', None), 'behavior_id', '?')}",
                    [cid],
                )
            )
    return failures


@register_check("NUM-15", "好感键有效且必含玩家")
def check_num_15_favorability_keys() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        本域唯一方向为"角色⊆全局"的键集检查：校验chara.favorability的每个目标id都必须是cache.character_data
        中现存角色，且必须含键0（玩家）——能力升级需求F<n>与事件通道均裸取/裸写favorability[0]。键类型均为
        精确int。未招募角色的历史好感不构成假阳性（每个模板NPC都建有character_data条目）；真正会命中的是存档
        迁移的悬空引用。
    """
    cache = cache_control.cache
    failures = []
    valid_cids = set(cache.character_data)
    for cid, chara in cache.character_data.items():
        if not _dict_field_ok(chara, "favorability"):
            continue
        favorability = chara.favorability
        dangling = set(favorability) - valid_cids
        bad_key_type = not all(type(k) is int for k in favorability)
        has_player = 0 in favorability
        if dangling or bad_key_type or not has_player:
            failures.append(
                make_failure(
                    "NUM-15",
                    "好感键有效且必含玩家",
                    f"角色cid={cid} name={_chara_name(chara)} 悬空目标id={dangling} 非int键存在={bad_key_type} "
                    f"含玩家键0={has_player}",
                    [cid],
                )
            )
    return failures


@register_check("NUM-16", "好感值为整数")
def check_num_16_favorability_type() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        只检查chara.favorability值的类型为int，不设上下界。下界：extra_adjust允许为负且无max(0,..)，负好感是
        设计内合法态。上界：事件直写与可重复的外勤委托奖励都不钳制100000，满好感角色再吃一次奖励即越界，属合法
        流程假阳性，因此上界只作观测信息随失败一并输出，不构成失败条件本身。带cache.debug_mode守卫。
    """
    cache = cache_control.cache
    if cache.debug_mode:
        return []
    failures = []
    for cid, chara in cache.character_data.items():
        if not _dict_field_ok(chara, "favorability"):
            continue
        favorability = chara.favorability
        bad = {k: v for k, v in favorability.items() if type(v) is not int}
        if bad:
            observe_over = {k: v for k, v in favorability.items() if type(v) in (int, float) and v > 100000}
            failures.append(
                make_failure(
                    "NUM-16",
                    "好感值为整数",
                    f"角色cid={cid} name={_chara_name(chara)} 非int好感值={bad} 观测(>100000,非失败条件)={observe_over}",
                    [cid],
                )
            )
    return failures


@register_check("NUM-17", "信赖与催眠程度为有限实数")
def check_num_17_trust_hypnosis_finite() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验chara.trust与chara.hypnosis.hypnosis_degree都是类型合法(int/float)且有限(非NaN/inf)的实数。一旦某个
        连乘系数产出NaN，min(300, nan)会静默返回nan，之后所有比较恒False，角色行为诡异"卡住"而不报错，是最难
        靠日志发现的一类bug。不加上界（同NUM-16理由：事件与外勤委托的+=不钳制且可重复触发）。
        绝不先裸调math.isfinite——_is_finite_number先做类型短路，避免坏档写入None/字符串时检查器自身抛异常。
    """
    cache = cache_control.cache
    failures = []
    for cid, chara in cache.character_data.items():
        trust = getattr(chara, "trust", None)
        hypnosis = getattr(chara, "hypnosis", None)
        hypnosis_degree = getattr(hypnosis, "hypnosis_degree", None)
        if not (_is_finite_number(trust) and _is_finite_number(hypnosis_degree)):
            failures.append(
                make_failure(
                    "NUM-17",
                    "信赖与催眠程度为有限实数",
                    f"角色cid={cid} name={_chara_name(chara)} trust={trust!r} hypnosis_degree={hypnosis_degree!r} "
                    f"target_character_id={getattr(chara, 'target_character_id', '?')}",
                    [cid],
                )
            )
    return failures


@register_check("NUM-18", "体力/气力上限为正整数")
def check_num_18_hp_mp_max_positive() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验hit_point_max/mana_point_max均为正整数。实时结算每回合无保护地做hit_point/hit_point_max与
        mana_point/mana_point_max，上限为0直接ZeroDivisionError。对全体角色成立（NPC由模板赋值，玩家固定值）。
        带cache.debug_mode守卫（debug面板允许把上限改为0或负数）。
    """
    cache = cache_control.cache
    if cache.debug_mode:
        return []
    failures = []
    for cid, chara in cache.character_data.items():
        hp_max = getattr(chara, "hit_point_max", None)
        mp_max = getattr(chara, "mana_point_max", None)
        if not (type(hp_max) is int and hp_max > 0 and type(mp_max) is int and mp_max > 0):
            failures.append(
                make_failure(
                    "NUM-18",
                    "体力/气力上限为正整数",
                    f"角色cid={cid} name={_chara_name(chara)} adv={getattr(chara, 'adv', '?')} "
                    f"hit_point_max={hp_max!r} mana_point_max={mp_max!r}",
                    [cid],
                )
            )
    return failures


@register_check("NUM-19", "玩家专属槽位上限为正整数")
def check_num_19_player_only_max_fields() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        仅校验cid 0（玩家）的sanity_point_max/eja_point_max/semen_point_max均为正整数，且sanity_point_max<=9999。
        这三个字段只在玩家分支被赋值，NPC分支只设hit_point_max/mana_point_max，三项对NPC原封不动停在类默认值0；
        对NPC检查会产生"每回合每NPC一条"的必然误报，故迭代范围严格限定为cid==0。高潮判定
        eja_point>=eja_point_max在上限为0时恒真，会让玩家每次结算都触发高潮。带cache.debug_mode守卫。
    """
    cache = cache_control.cache
    if cache.debug_mode:
        return []
    chara = cache.character_data.get(0)
    if chara is None:
        return []
    fields = ("sanity_point_max", "eja_point_max", "semen_point_max")
    values = {f: getattr(chara, f, None) for f in fields}
    ok = all(type(v) is int and v > 0 for v in values.values()) and type(values["sanity_point_max"]) is int and values["sanity_point_max"] <= 9999
    if not ok:
        failures = [
            make_failure(
                "NUM-19",
                "玩家专属槽位上限为正整数",
                f"玩家cid=0 sanity_point_max={values['sanity_point_max']!r} eja_point_max={values['eja_point_max']!r} "
                f"semen_point_max={values['semen_point_max']!r} sanity_point={getattr(chara, 'sanity_point', '?')} "
                f"eja_point={getattr(chara, 'eja_point', '?')} semen_point={getattr(chara, 'semen_point', '?')}",
                [0],
            )
        ]
    else:
        failures = []
    return failures


@register_check("NUM-20", "当前体力在[1,上限]")
def check_num_20_hit_point_range() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验chara.hit_point在[1, hit_point_max]范围内（力竭底线为1而非0）。死亡角色豁免——死亡角色被结算函数
        直接return，HP冻结在旧值，不代表越界。HP并非每回合统一双向clamp，只在对应结算发生时钳制，本项本质是
        找出绕过通用结算的直写路径。带cache.debug_mode守卫。
    """
    cache = cache_control.cache
    if cache.debug_mode:
        return []
    failures = []
    for cid, chara in cache.character_data.items():
        if getattr(chara, "dead", False):
            continue
        hp = getattr(chara, "hit_point", None)
        hp_max = getattr(chara, "hit_point_max", None)
        if type(hp) is not int or type(hp_max) not in (int, float) or not (1 <= hp <= hp_max):
            failures.append(
                make_failure(
                    "NUM-20",
                    "当前体力在[1,上限]",
                    f"角色cid={cid} name={_chara_name(chara)} hit_point={hp!r} hit_point_max={hp_max!r} "
                    f"dead={getattr(chara, 'dead', '?')} behavior_id={getattr(getattr(chara, 'behavior', None), 'behavior_id', '?')}",
                    [cid],
                )
            )
    return failures


@register_check("NUM-21", "当前气力在[0,上限]")
def check_num_21_mana_point_range() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验chara.mana_point在[0, mana_point_max]范围内。通用增减与休息回复都钳制此范围。上限为0时本式退化为
        mana_point==0，NUM-18会先报出根因。死亡角色同样被结算跳过，但MP下界0恒成立，无需dead豁免。
        带cache.debug_mode守卫。
    """
    cache = cache_control.cache
    if cache.debug_mode:
        return []
    failures = []
    for cid, chara in cache.character_data.items():
        mp = getattr(chara, "mana_point", None)
        mp_max = getattr(chara, "mana_point_max", None)
        if type(mp) is not int or type(mp_max) not in (int, float) or not (0 <= mp <= mp_max):
            failures.append(
                make_failure(
                    "NUM-21",
                    "当前气力在[0,上限]",
                    f"角色cid={cid} name={_chara_name(chara)} mana_point={mp!r} mana_point_max={mp_max!r} "
                    f"hit_point={getattr(chara, 'hit_point', '?')} "
                    f"behavior_id={getattr(getattr(chara, 'behavior', None), 'behavior_id', '?')}",
                    [cid],
                )
            )
    return failures


@register_check("NUM-22", "当前理智在[0,上限]")
def check_num_22_sanity_point_range() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验chara.sanity_point在[0, sanity_point_max]范围内。消耗侧一律max(x-y,0)、实时消耗先min再扣、指令判定
        先比较再扣、恢复侧以上限封顶。对NPC本式空洞成立（sanity_point_max恒为0且理智被强制压回0），不产生假
        阳性，可对全体跑，但真正有意义的只有cid 0。带cache.debug_mode守卫。
    """
    cache = cache_control.cache
    if cache.debug_mode:
        return []
    failures = []
    for cid, chara in cache.character_data.items():
        sp = getattr(chara, "sanity_point", None)
        sp_max = getattr(chara, "sanity_point_max", None)
        if type(sp) is not int or type(sp_max) not in (int, float) or not (0 <= sp <= sp_max):
            extra = ""
            if cid == 0:
                pl_ability = getattr(chara, "pl_ability", None)
                extra = f" today_sanity_point_cost={getattr(pl_ability, 'today_sanity_point_cost', '?')}"
            failures.append(
                make_failure(
                    "NUM-22",
                    "当前理智在[0,上限]",
                    f"角色cid={cid} name={_chara_name(chara)} sanity_point={sp!r} sanity_point_max={sp_max!r}{extra}",
                    [cid],
                )
            )
    return failures


@register_check("NUM-23", "射精槽非负且不设上限")
def check_num_23_eja_point_non_negative() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验chara.eja_point非负，不检查<=eja_point_max——槽满时"忍住射精"会直接return，合法保留
        eja_point>=eja_point_max。类型放宽到(int, float)：default.py:3298处的+=写入产出float而漏了int()转换，
        属已知缺陷，硬性type is int会误报此路径；缺陷修好后本项可收紧回int。带cache.debug_mode守卫。
    """
    cache = cache_control.cache
    if cache.debug_mode:
        return []
    failures = []
    for cid, chara in cache.character_data.items():
        eja = getattr(chara, "eja_point", None)
        if not (type(eja) in (int, float) and eja >= 0):
            h_state = getattr(chara, "h_state", None)
            sp_flag = getattr(chara, "sp_flag", None)
            failures.append(
                make_failure(
                    "NUM-23",
                    "射精槽非负且不设上限",
                    f"角色cid={cid} name={_chara_name(chara)} eja_point={eja!r} eja_point_max={getattr(chara, 'eja_point_max', '?')} "
                    f"endure_not_shot_count={getattr(h_state, 'endure_not_shot_count', '?')} is_h={getattr(sp_flag, 'is_h', '?')}",
                    [cid],
                )
            )
    return failures


@register_check("NUM-24", "精液槽与临时精液槽范围")
def check_num_24_semen_point_range() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验chara.semen_point在[0, semen_point_max]，chara.tem_extra_semen_point在[0, semen_point_max*4]。
        恢复侧封顶semen_point_max，临时槽封顶4倍，射精面板先扣临时槽再扣基础槽并max(0,...)。对NPC（两值均为0）
        退化为0<=0<=0，不产生假阳性，可对全体跑。带cache.debug_mode守卫。
    """
    cache = cache_control.cache
    if cache.debug_mode:
        return []
    failures = []
    for cid, chara in cache.character_data.items():
        semen = getattr(chara, "semen_point", None)
        semen_max = getattr(chara, "semen_point_max", None)
        tem_extra = getattr(chara, "tem_extra_semen_point", None)
        ok = (
            type(semen) is int
            and type(tem_extra) is int
            and type(semen_max) in (int, float)
            and 0 <= semen <= semen_max
            and 0 <= tem_extra <= semen_max * 4
        )
        if not ok:
            failures.append(
                make_failure(
                    "NUM-24",
                    "精液槽与临时精液槽范围",
                    f"角色cid={cid} name={_chara_name(chara)} semen_point={semen!r} semen_point_max={semen_max!r} "
                    f"tem_extra_semen_point={tem_extra!r}",
                    [cid],
                )
            )
    return failures


@register_check("NUM-25", "基地资源键集覆盖配表且为非负整数")
def check_num_25_base_resource() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验config_resouce的每个id都在cache.rhodes_island.materials_resouce中存在（配表⊆资源，方向同NUM-02——
        存档迁移只补不删已下线的资源id，多余键合法），且键为精确int、值为非负整数（各面板按固定id裸下标，
        没有任何统一的max(0,...)兜底，负资源意味着某条支付路径漏判）。不检查库存<=warehouse_capacity——裁剪只
        在日结与产线两处发生，日内多条入库路径不钳制，检查器挂在场景面板输入前拿不到"刚完成日结"的阶段标记。
        龙门币为资源id 1，键集条件独立于debug_mode（键集/容器类不加该守卫），但数值下界受debug_mode守卫
        （debug模式购买跳过余额校验，资源可合法为负）。若config_resouce配表或rhodes_island结构不存在，
        本检查对应部分退化为跳过。
    """
    cache = cache_control.cache
    config_resouce = getattr(game_config, "config_resouce", None)
    if not isinstance(config_resouce, dict):
        return []
    rhodes_island = getattr(cache, "rhodes_island", None)
    materials = getattr(rhodes_island, "materials_resouce", None)
    if not isinstance(materials, dict):
        return []
    config_keys = set(config_resouce)
    missing = config_keys - set(materials)
    key_type_ok = all(type(k) is int for k in materials)
    failures = []
    value_bad = {} if cache.debug_mode else {k: v for k, v in materials.items() if type(v) is not int or v < 0}
    if missing or not key_type_ok or value_bad:
        detail_names = {k: config_resouce[k].name for k in list(value_bad) + list(missing) if k in config_resouce}
        failures.append(
            make_failure(
                "NUM-25",
                "基地资源键集覆盖配表且为非负整数",
                f"资源缺键={missing} 键类型合法={key_type_ok} 非法值={value_bad} 涉及资源名={detail_names} "
                f"game_time={getattr(cache, 'game_time', '?')} warehouse_capacity={getattr(rhodes_island, 'warehouse_capacity', '?')}",
            )
        )
    return failures


@register_check("NUM-26", "仓库容量为非负整数")
def check_num_26_warehouse_capacity() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验cache.rhodes_island.warehouse_capacity为非负整数。该值被直接用作资源裁剪的上限值，负容量会在日结时
        把母乳(资源31)与精液药材(资源12)写成负数，比NUM-25更靠近根因。下界取>=0而非>0——仓储区未建成时容量为0
        是合法初态。带cache.debug_mode守卫。
    """
    cache = cache_control.cache
    if cache.debug_mode:
        return []
    rhodes_island = getattr(cache, "rhodes_island", None)
    capacity = getattr(rhodes_island, "warehouse_capacity", None)
    if type(capacity) is int and capacity >= 0:
        return []
    materials = getattr(rhodes_island, "materials_resouce", None)
    materials = materials if isinstance(materials, dict) else {}
    return [
        make_failure(
            "NUM-26",
            "仓库容量为非负整数",
            f"warehouse_capacity={capacity!r} facility_level[3]={getattr(rhodes_island, 'facility_level', {}).get(3) if isinstance(getattr(rhodes_island, 'facility_level', None), dict) else '?'} "
            f"used_extra_warehouse_capacity_module={getattr(rhodes_island, 'used_extra_warehouse_capacity_module', '?')} "
            f"materials_resouce[31]={materials.get(31)} materials_resouce[12]={materials.get(12)}",
        )
    ]


@register_check("NUM-27", "疲劳/饥饿/熟睡/醉酒在各自量程内")
def check_num_27_fatigue_family_range() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验tired_point∈[0,160]、hunger_point∈[0,240]、sleep_point∈[0,100]、drunk_point∈[0,100]。这四项都是按
        分钟累加、并在累加处双向封顶的计量值，出界说明有直接赋值旁路。带cache.debug_mode守卫
        （debug面板可直接改写这些字段）。
    """
    cache = cache_control.cache
    if cache.debug_mode:
        return []
    bounds = {"tired_point": 160, "hunger_point": 240, "sleep_point": 100, "drunk_point": 100}
    failures = []
    for cid, chara in cache.character_data.items():
        bad_fields = {}
        for field, upper in bounds.items():
            v = getattr(chara, field, None)
            if not (type(v) is int and 0 <= v <= upper):
                bad_fields[field] = v
        if bad_fields:
            failures.append(
                make_failure(
                    "NUM-27",
                    "疲劳/饥饿/熟睡/醉酒在各自量程内",
                    f"角色cid={cid} name={_chara_name(chara)} 越界字段={bad_fields} "
                    f"behavior_id={getattr(getattr(chara, 'behavior', None), 'behavior_id', '?')} "
                    f"state={getattr(chara, 'state', '?')} unconscious_h={getattr(getattr(chara, 'sp_flag', None), 'unconscious_h', '?')}",
                    [cid],
                )
            )
    return failures


@register_check("NUM-28", "尿意值非负且为整数")
def check_num_28_urinate_point_non_negative() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验chara.urinate_point为非负整数。排尿结算清零，无任何无钳制的减法，下界稳固。上界另见NUM-29。
        带cache.debug_mode守卫。
    """
    cache = cache_control.cache
    if cache.debug_mode:
        return []
    failures = []
    for cid, chara in cache.character_data.items():
        urinate = getattr(chara, "urinate_point", None)
        if not (type(urinate) is int and urinate >= 0):
            failures.append(
                make_failure(
                    "NUM-28",
                    "尿意值非负且为整数",
                    f"角色cid={cid} name={_chara_name(chara)} urinate_point={urinate!r} "
                    f"drunk_point={getattr(chara, 'drunk_point', '?')} "
                    f"behavior_id={getattr(getattr(chara, 'behavior', None), 'behavior_id', '?')}",
                    [cid],
                )
            )
    return failures


@register_check("NUM-29", "角色尿意值不超过300")
def check_num_29_urinate_point_upper_bound() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验所有角色（含玩家cid=0）的urinate_point不超过300（设计上界，realtime_settle与
        drunk_sex_common两处min(300,...)体现；其余写入点均为固定值≤240或自带回落上界）。
        已知default.py:9506,9528两处裸 += 60缺失钳制（上游PR #303钳制之），在未含该修复的
        游戏本体上300可被合法突破，故降为warning而非error；#303合入上游后本项可升回error。
        带cache.debug_mode守卫。
    """
    cache = cache_control.cache
    if cache.debug_mode:
        return []
    difficulty_setting = getattr(getattr(cache, "all_system_setting", None), "difficulty_setting", None)
    difficulty_setting = difficulty_setting if isinstance(difficulty_setting, dict) else {}
    failures = []
    for cid, chara in cache.character_data.items():
        urinate = getattr(chara, "urinate_point", None)
        if type(urinate) in (int, float) and urinate > 300:
            failures.append(
                make_failure(
                    "NUM-29",
                    "角色尿意值不超过300",
                    f"[warning] 角色cid={cid} name={_chara_name(chara)} urinate_point={urinate!r} "
                    f"behavior_id={getattr(getattr(chara, 'behavior', None), 'behavior_id', '?')} "
                    f"difficulty_setting[11]={difficulty_setting.get(11)} difficulty_setting[12]={difficulty_setting.get(12)}",
                    [cid],
                )
            )
    return failures


@register_check("NUM-30", "欲望值为非负整数且不设上限")
def check_num_30_desire_point_non_negative() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表
    功能:
        校验chara.desire_point为非负整数，不强制<=100——尽管字段注释称100为最大，逐日结算逐日累加且无任何
        钳制，前提函数在>=100时权重仍随数值单调增长，说明设计上预期会超过100。下界0由结算侧的max(...,0)与
        NPC AI的置0维护。带cache.debug_mode守卫。
    """
    cache = cache_control.cache
    if cache.debug_mode:
        return []
    failures = []
    for cid, chara in cache.character_data.items():
        desire = getattr(chara, "desire_point", None)
        if not (type(desire) is int and desire >= 0):
            ability = getattr(chara, "ability", None)
            ability_33 = ability.get(33) if isinstance(ability, dict) else None
            failures.append(
                make_failure(
                    "NUM-30",
                    "欲望值为非负整数且不设上限",
                    f"角色cid={cid} name={_chara_name(chara)} desire_point={desire!r} ability[33]={ability_33} "
                    f"game_time={getattr(cache, 'game_time', '?')}",
                    [cid],
                )
            )
    return failures
