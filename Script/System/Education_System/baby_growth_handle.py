"""胎教与婴儿期早教（Plan 22 四期 §3.27 / §3.20）

覆盖养成链最前面的两段：

    1. 妊娠期胎教 —— 玩家对孕肚说话 / 放音乐 / 抚摸，每次给母亲的 pregnancy.prenatal_point +0.5；
       生产时逐个**全额**转写给每个新生儿（多胎不平分：胎教是对着孕肚做的，双胞胎都听见了），
       在孩子身上落为**全科目少量**初始经验，然后母亲侧清零。
    2. 婴儿期照料 —— 6 个照料行为各自的养成方向大多直接写在 Behavior_Effect.csv 的 CVE 效果串里
       （照料值与性格倾向走 CVE_A2_Growth，技能初始经验走 CVE_A2_E），只有「喂奶」多一段
       体质与玩家亲自照料的加成，需要专用结算器，常量放在本模块。

转写是"全科目少量"而不是"单科大量"：胎教发生在孩子还没有"科目"概念的阶段，
   把它做成某一科的先修既不合逻辑，也会逼玩家在孕期就决定孩子将来学什么。
"""
from types import FunctionType
from typing import Dict, List

from Script.Core import cache_control, game_type, get_text
from Script.System.Education_System import education_constant, growth_handle

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """

# ---------------------------------------------------------------------------
# 母亲侧的胎教累积
# ---------------------------------------------------------------------------


def get_prenatal_point(mother_id: int) -> float:
    """
    取母亲当前累积的胎教值
    Keyword arguments:
    mother_id -- 母亲的角色id
    Return arguments:
    float -- 胎教值，角色不存在或旧档缺字段时为0
    """
    if mother_id not in cache.character_data:
        return 0.0
    pregnancy_data = cache.character_data[mother_id].pregnancy
    return float(getattr(pregnancy_data, "prenatal_point", 0.0))


def add_prenatal_point(mother_id: int, value: float = education_constant.PRENATAL_POINT_PER_TIME) -> float:
    """
    给母亲累积一次胎教值（封顶 PRENATAL_POINT_MAX）
    Keyword arguments:
    mother_id -- 母亲的角色id
    value -- 累积量，默认每次 0.5
    Return arguments:
    float -- 累积后的胎教值
    """
    if mother_id not in cache.character_data:
        return 0.0
    pregnancy_data = cache.character_data[mother_id].pregnancy
    now_point = float(getattr(pregnancy_data, "prenatal_point", 0.0))
    now_point = min(education_constant.PRENATAL_POINT_MAX, now_point + value)
    pregnancy_data.prenatal_point = now_point
    return now_point


def clear_prenatal_point(mother_id: int) -> None:
    """
    清零母亲侧的胎教累积（生产结算完成后调用，下一胎从头攒）
    Keyword arguments:
    mother_id -- 母亲的角色id
    Return arguments:
    无
    """
    if mother_id not in cache.character_data:
        return
    cache.character_data[mother_id].pregnancy.prenatal_point = 0.0


# ---------------------------------------------------------------------------
# 出生时的转写
# ---------------------------------------------------------------------------


def get_prenatal_count(mother_id: int) -> int:
    """
    把母亲的胎教累积值折回做过的次数（供身体信息面板与生产面板共用一个算口）
    Keyword arguments:
    mother_id -- 母亲的角色id
    Return arguments:
    int -- 做过的胎教次数
    """
    return int(get_prenatal_point(mother_id) / education_constant.PRENATAL_POINT_PER_TIME)


def get_prenatal_exp_value(prenatal_point: float) -> int:
    """
    把胎教值换算成每门科目的初始经验
    Keyword arguments:
    prenatal_point -- 胎教值
    Return arguments:
    int -- 每科经验，向下取整
    """
    return int(max(0.0, prenatal_point) * education_constant.PRENATAL_EXP_PER_POINT)


def settle_prenatal_to_child(mother_id: int, child_id: int) -> str:
    """
    把母亲累积的胎教值转写给一个新生儿：记到 child_growth.prenatal_point，并按科目发初始经验

    这里**不清零母亲侧**——多胎要逐个全额转写，清零由生产面板在全部孩子创建完之后统一做。
    经验直接写 experience 字典而不走 base_chara_experience_common_settle：那个函数会记进
       行为的变更记录并触发能力升级判定，出生时既没有行为也不该刷一屏"升级"提示。
    Keyword arguments:
    mother_id -- 母亲的角色id
    child_id -- 新生儿的角色id
    Return arguments:
    str -- 给生产面板显示的说明文本，没有胎教累积时为空串
    """
    prenatal_point = get_prenatal_point(mother_id)
    if prenatal_point <= 0 or child_id not in cache.character_data:
        return ""
    growth_data = growth_handle.get_child_growth(child_id)
    growth_data.prenatal_point = prenatal_point
    exp_value = get_prenatal_exp_value(prenatal_point)
    child_data: game_type.Character = cache.character_data[child_id]
    if exp_value > 0:
        for ability_id in education_constant.FEMALE_SUBJECT_LIST:
            exp_id = growth_handle.get_subject_exp_id(ability_id)
            if not exp_id:
                continue
            child_data.experience.setdefault(exp_id, 0)
            child_data.experience[exp_id] += exp_value
    if exp_value > 0:
        return _("\n{0}在孕期听过{1}次胎教，底子比别的孩子好一些：全部科目各获得了{2}点初始经验\n").format(
            child_data.name, get_prenatal_count(mother_id), exp_value
        )
    return _("\n{0}在孕期听过几次胎教，虽然还不足以留下什么，但她一定记得那个声音\n").format(child_data.name)


def get_prenatal_exp_dict(child_id: int) -> Dict[int, int]:
    """
    按科目列出某孩子出生时由胎教获得的经验（供面板与测试查看）
    Keyword arguments:
    child_id -- 孩子的角色id
    Return arguments:
    Dict[int, int] -- {科目能力id: 经验值}，没有养成数据时为空
    """
    if child_id not in cache.character_data:
        return {}
    growth_data = cache.character_data[child_id].child_growth
    if growth_data is None:
        return {}
    exp_value = get_prenatal_exp_value(growth_data.prenatal_point)
    if not exp_value:
        return {}
    return {ability_id: exp_value for ability_id in education_constant.FEMALE_SUBJECT_LIST}
