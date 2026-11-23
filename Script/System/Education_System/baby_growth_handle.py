"""胎教与婴儿期早教（Plan 22 四期 §3.27 / §3.20，Plan 26 §3.2 改为出生时折习得珠）

覆盖养成链最前面的两段：

    1. 妊娠期胎教 —— 玩家对孕肚说话 / 放音乐 / 抚摸，每次给母亲的 pregnancy.prenatal_point +0.5；
       生产时逐个**全额**转写给每个新生儿（多胎不平分：胎教是对着孕肚做的，双胞胎都听见了），
       在孩子身上折成习得珠（每 1 点 PRENATAL_JUEL_PER_POINT 个），然后母亲侧清零。
    2. 婴儿期照料 —— 6 个照料行为各自的养成方向大多直接写在 Behavior_Effect.csv 的 CVE 效果串里
       （照料值与性格倾向走 CVE_A2_Growth，技能初始经验走 CVE_A2_E），只有「喂奶」多一段
       体质与玩家亲自照料的加成，需要专用结算器，常量放在本模块。

折成习得珠而不是发经验（Plan 26，用户改判）：孕期谈不上学会了什么。经验是分科的「已经会」，
   珠是通用的「学得快」——满胎教的孩子每门课仍要自己攒经验才升得上去。
   原先按 17 门科目各发初始经验，其中 7 门性技解出的是真实性交经验，新生儿会带着手交 / 阴道性交 / 精液经验出生。
"""
from types import FunctionType

from Script.Config import game_config
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


def get_prenatal_juel_value(prenatal_point: float) -> int:
    """
    把胎教值换算成孩子出生时得到的习得珠数
    Keyword arguments:
    prenatal_point -- 胎教值
    Return arguments:
    int -- 习得珠数，向下取整
    """
    return int(max(0.0, prenatal_point) * education_constant.PRENATAL_JUEL_PER_POINT)


def get_learn_juel_name() -> str:
    """
    取习得珠的显示名（生产面板、身体信息面板、养成总览共用）
    Keyword arguments:
    无
    Return arguments:
    str -- 珠名，取自配置（载入时已翻译过，不再包 _()）；查不到时为空串
    """
    juel_data = game_config.config_juel.get(education_constant.LEARN_STATE_ID)
    if juel_data is None:
        return ""
    return juel_data.name


def settle_prenatal_to_child(mother_id: int, child_id: int) -> str:
    """
    把母亲累积的胎教值转写给一个新生儿：记到 child_growth.prenatal_point，并折成习得珠（Plan 26 §3.2）

    这里**不清零母亲侧**——多胎要逐个全额转写，清零由生产面板在全部孩子创建完之后统一做。
    珠直接写 juel 字典而不走结算：出生时既没有行为，也不该刷一屏变更记录。
       婴儿不在 npc_id_got 里、不进睡眠结算的自动升级，这些珠整个婴儿期都不会被花掉，
       成长为幼女上线后，才随着各门课攒下的经验兑现成等级
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
    juel_value = get_prenatal_juel_value(prenatal_point)
    child_data: game_type.Character = cache.character_data[child_id]
    if juel_value > 0:
        child_data.juel.setdefault(education_constant.LEARN_STATE_ID, 0)
        child_data.juel[education_constant.LEARN_STATE_ID] += juel_value
        return _("\n{0}在孕期听过{1}次胎教，底子比别的孩子好一些：获得了{2}个{3}\n").format(
            child_data.name, get_prenatal_count(mother_id), juel_value, get_learn_juel_name()
        )
    # 按现行比例 0.5 点也折得出珠，只有把 PRENATAL_JUEL_PER_POINT 调低时才会走到这里
    return _("\n{0}在孕期听过几次胎教，虽然还不足以留下什么，但她一定记得那个声音\n").format(child_data.name)


def get_child_prenatal_juel(child_id: int) -> int:
    """
    取某孩子出生时由胎教折得的习得珠数（供养成总览与测试查看）
    Keyword arguments:
    child_id -- 孩子的角色id
    Return arguments:
    int -- 习得珠数，没有养成数据或没做过胎教时为0
    功能: 由记下的 child_growth.prenatal_point 按现行比例现算，不另存字段。
          Plan 26 之前出生的孩子当年拿的是经验，这里仍按珠显示，不回溯（方案 §6）
    """
    if child_id not in cache.character_data:
        return 0
    growth_data = cache.character_data[child_id].child_growth
    if growth_data is None:
        return 0
    return get_prenatal_juel_value(growth_data.prenatal_point)


def get_child_prenatal_count(child_id: int) -> int:
    """
    取某孩子在孕期听过的胎教次数（由记下的 child_growth.prenatal_point 折回，养成总览用）
    Keyword arguments:
    child_id -- 孩子的角色id
    Return arguments:
    int -- 胎教次数，没有养成数据时为0
    """
    if child_id not in cache.character_data:
        return 0
    growth_data = cache.character_data[child_id].child_growth
    if growth_data is None:
        return 0
    return int(growth_data.prenatal_point / education_constant.PRENATAL_POINT_PER_TIME)
