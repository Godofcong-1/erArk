"""罗德岛全局数值的统一读写口（Plan 23 方案 §4.3）

公务事件里的部门事务要能读写资源、声望、公务量这类**不属于任何角色**的数值，
而 CVP/CVE 的主体只有 A1/A2/A3 三种角色（`settle_behavior.py:729-742` 的属性映射
是 `getattr(character_data, ...)` 硬绑角色对象的），够不着 `cache.rhodes_island`。

所以这里另开一个 `RI` 主体，前提写 `CVP_RI_<类型>_<运算>_<值>`、结算写 `CVE_RI_<类型>_<G/L/E>_<值>`，
两侧都从本模块取值与写值，免得同一个「龙门币」在前提、结算、面板三处各算各的。

写入一律走 `change_ri_value()` / `set_ri_value()`，不要在别处直接改 dict：
   夹逼（资源不为负、公务量不超总量、效率 50~200）与 `setdefault` 都在这里做，
   绕过去就会出现负数资源或越界效率。
"""
from types import FunctionType
from typing import Tuple

from Script.Core import cache_control, game_type, get_text

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """

RI_TYPE_RESOURCE = "R"
""" 素材资源，子id为 Resource.csv 的资源id（1龙门币/3至纯源石/13工业材料/15燃料…） """

RI_TYPE_REPUTATION = "Rep"
""" 势力声望，子id为势力id """

RI_TYPE_FACILITY = "Fac"
""" 设施等级，子id为设施cid。只读——设施升级要走基建系统的资源消耗，事件直接改会绕过成本 """

RI_TYPE_OFFICE_WORK = "Work"
""" 待处理的公务量 """

RI_TYPE_EFFECTIVENESS = "Eff"
""" 基地效率（50~200） """

RI_TYPE_POWER = "Power"
""" 电力储量 """

RI_TYPE_PEOPLE = "People"
""" 当前干员数。只读——干员数是角色表算出来的，不是一个能被赋值的数 """

READ_ONLY_TYPE_SET = {RI_TYPE_FACILITY, RI_TYPE_PEOPLE}
""" 只读的数值类型：写入请求会被静默忽略（校验工具会在写 CSV 时就拦下来） """

EFFECTIVENESS_MIN = 50
""" 基地效率的下限，与 basement.settle_office_work 的夹逼保持一致 """

EFFECTIVENESS_MAX = 200
""" 基地效率的上限，与 basement.settle_office_work 的夹逼保持一致 """


def parse_value_type(type_text: str) -> Tuple[str, int]:
    """
    把 token 里的类型段拆成 (类型, 子id)
    Keyword arguments:
    type_text -- 类型段文本，形如 "R|13" 或 "Work"
    Return arguments:
    Tuple[str, int] -- (类型str, 子id int)，没有子id时子id为0
    """
    if "|" not in type_text:
        return type_text, 0
    type_name, son_text = type_text.split("|", 1)
    son_id = 0
    if son_text.lstrip("-").isdigit():
        son_id = int(son_text)
    return type_name, son_id


def get_all_office_work() -> float:
    """
    取公务量的上限（总工作量）

    与 basement.settle_office_work 的算法一致：设施等级和×10 + 干员数。
    不去 import basement：那里是每日结算模块，事件系统在函数级引用它容易绕出循环导入
    Keyword arguments:
    无
    Return arguments:
    float -- 总工作量，异常时为0
    """
    all_facility_level = 0
    for facility_cid in cache.rhodes_island.facility_level:
        all_facility_level += cache.rhodes_island.facility_level[facility_cid]
    return all_facility_level * 10 + len(cache.npc_id_got)


def get_ri_value(type_text: str) -> float:
    """
    读取一项罗德岛全局数值，供 CVP_RI_ 前提、CVE_RI_ 结算与面板共用
    Keyword arguments:
    type_text -- 类型段文本，形如 "R|13" 或 "Work"
    Return arguments:
    float -- 数值，类型不认识时为0
    """
    type_name, son_id = parse_value_type(type_text)
    if type_name == RI_TYPE_RESOURCE:
        return float(cache.rhodes_island.materials_resouce.get(son_id, 0))
    if type_name == RI_TYPE_REPUTATION:
        return float(cache.country.nation_reputation.get(son_id, 0))
    if type_name == RI_TYPE_FACILITY:
        return float(cache.rhodes_island.facility_level.get(son_id, 0))
    if type_name == RI_TYPE_OFFICE_WORK:
        return float(cache.rhodes_island.office_work)
    if type_name == RI_TYPE_EFFECTIVENESS:
        return float(cache.rhodes_island.effectiveness)
    if type_name == RI_TYPE_POWER:
        return float(cache.rhodes_island.power_storage)
    if type_name == RI_TYPE_PEOPLE:
        return float(len(cache.npc_id_got))
    return 0.0


def set_ri_value(type_text: str, new_value: float):
    """
    把一项罗德岛全局数值直接设为指定值（CVE 的 E 运算）

    只读类型（设施等级、干员数）静默忽略：让事件直接改设施等级会绕过基建的资源成本
    Keyword arguments:
    type_text -- 类型段文本
    new_value -- 目标值
    Return arguments:
    无
    """
    type_name, son_id = parse_value_type(type_text)
    if type_name in READ_ONLY_TYPE_SET:
        # 静默返回会让作者以为自己写的结算生效了，把值名打出来才查得动
        print(f"\ndebug 公务事件试图改写只读的全局数值「{get_value_name(type_text)}」，已忽略\n")
        return
    if type_name == RI_TYPE_RESOURCE:
        # 资源不允许为负，否则仓库面板会显示出一个谁也还不上的负数
        cache.rhodes_island.materials_resouce[son_id] = max(0, int(new_value))
    elif type_name == RI_TYPE_REPUTATION:
        cache.country.nation_reputation[son_id] = new_value
    elif type_name == RI_TYPE_OFFICE_WORK:
        # 公务量夹在 0~总工作量之间，与每日结算的口径一致
        cache.rhodes_island.office_work = round(max(0.0, min(float(new_value), get_all_office_work())), 1)
    elif type_name == RI_TYPE_EFFECTIVENESS:
        cache.rhodes_island.effectiveness = round(max(EFFECTIVENESS_MIN, min(float(new_value), EFFECTIVENESS_MAX)), 1)
    elif type_name == RI_TYPE_POWER:
        cache.rhodes_island.power_storage = max(0, int(new_value))


def change_ri_value(type_text: str, add_value: float):
    """
    增减一项罗德岛全局数值（CVE 的 G/L 运算，正负已由调用方取好）
    Keyword arguments:
    type_text -- 类型段文本
    add_value -- 增减量
    Return arguments:
    无
    """
    type_name, _son_id = parse_value_type(type_text)
    if type_name in READ_ONLY_TYPE_SET:
        print(f"\ndebug 公务事件试图增减只读的全局数值「{get_value_name(type_text)}」，已忽略\n")
        return
    set_ri_value(type_text, get_ri_value(type_text) + add_value)


def get_value_name(type_text: str) -> str:
    """
    取一项全局数值的中文名，用于面板与调试输出
    Keyword arguments:
    type_text -- 类型段文本
    Return arguments:
    str -- 中文名，取不到时返回原文本
    """
    from Script.Config import game_config

    type_name, son_id = parse_value_type(type_text)
    if type_name == RI_TYPE_RESOURCE and son_id in game_config.config_resouce:
        return game_config.config_resouce[son_id].name
    if type_name == RI_TYPE_REPUTATION and son_id in game_config.config_nation:
        return _("{0}声望").format(game_config.config_nation[son_id].name)
    if type_name == RI_TYPE_FACILITY and son_id in game_config.config_facility:
        return _("{0}等级").format(game_config.config_facility[son_id].name)
    if type_name == RI_TYPE_OFFICE_WORK:
        return _("待处理公务量")
    if type_name == RI_TYPE_EFFECTIVENESS:
        return _("基地效率")
    if type_name == RI_TYPE_POWER:
        return _("电力储量")
    if type_name == RI_TYPE_PEOPLE:
        return _("干员数")
    return type_text
