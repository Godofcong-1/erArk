"""
怀孕系统常量统一定义文件

本子系统（Script/System/Pregnancy_System）内的全部模块级常量集中在此定义、记录与管理，
各模块通过 `from Script.System.Pregnancy_System import pregnancy_constant` 引用，
子系统外的代码（礼物面板、前提、状态机等）同样从本文件引用，不得在各自文件内重复定义。

分组：
1. 胎生孕程天数阈值
2. 加速药剂量
3. 孩子成长天数阈值
4. 卵生
5. 怀孕总览面板阶段枚举
6. 生育谱系图排版
7. 生育方式与多胎
"""
from types import FunctionType
from Script.Core import get_text

_: FunctionType = get_text._
""" 翻译api """

# ==== 1. 胎生孕程天数阈值（基准为受精时间，天数经 pregnancy_handle.get_pregnancy_past_day 计入妊娠加速药） ====
PREGNANCY_DAY = 90
""" 受精转妊娠的天数阈值 """
PARTURIENT_DAY = 260
""" 妊娠转临盆的天数阈值（临盆后每过一天+20%生产概率） """
PREGNANCY_TOTAL_DAY = 270
""" 名义孕期总天数（妊娠加速药剂量公式的基数） """
POSTPARTUM_REST_DAY = 2
""" 产后休养转育儿的天数阈值（基准为最新一个孩子的出生时间） """

# ==== 2. 加速药剂量（妊娠加速药与孵化加速药共用） ====
ACCELERATION_MAX_DAY = 250
""" 加速药额外加速时间的累计上限（天） """
ACCELERATION_RATE = 0.3
""" 加速药单次剂量：剩余期（基数-当前有效天数）的比例 """

# ==== 3. 孩子成长天数阈值（基准为孩子出生时间，天数经 pregnancy_handle.get_child_grow_day 计入成长加速药） ====
REARING_COMPLETE_DAY = 90
""" 婴儿成长为幼女（育儿完成）所需的有效成长天数 """
GROW_TO_LOLI_DAY = 270
""" 幼女成长为萝莉所需的有效成长天数 """
GROW_TO_GIRL_DAY = 450
""" 萝莉成长为少女所需的有效成长天数 """

# ==== 4. 卵生 ====
HATCH_TOTAL_DAY = 265
""" 孵化总天数（与胎生受精→标准生产时长一致，基准为卵的排出时间） """
TEND_EGGS_ENTERTAINMENT_ID = 175
""" 照料卵娱乐的模板id（Entertainment.csv） """
NURSERY_WORKER_WORK_ID = 153
""" 保育员工作的模板id（WorkType.csv） """

# ==== 5. 怀孕总览面板阶段枚举 ====
STAGE_NONE = 0
""" 阶段枚举：无 """
STAGE_FERTILIZATION = 1
""" 阶段枚举：受精 """
STAGE_EGG_WAIT = 2
""" 阶段枚举：持卵待鉴定 """
STAGE_SOFT_EGG_WAIT = 3
""" 阶段枚举：体外卵待受精（无壳卵生，卵在玩家收藏品的体外卵字典中） """
STAGE_PREGNANCY = 4
""" 阶段枚举：妊娠 """
STAGE_HATCHING = 5
""" 阶段枚举：孵化中 """
STAGE_PARTURIENT = 6
""" 阶段枚举：临盆 """
STAGE_POSTPARTUM = 7
""" 阶段枚举：产后 """
STAGE_REARING = 8
""" 阶段枚举：育儿 """
STAGE_NAME_LIST = [_("全部"), _("受精"), _("持卵待鉴定"), _("卵块待受精"), _("妊娠"), _("孵化中"), _("临盆"), _("产后"), _("育儿")]
""" 阶段名列表（下标与阶段枚举一致，0位为筛选用的全部） """

# ==== 6. 生育谱系图排版 ====
UP_GEN = 2
""" 谱系图向上显示的代数（上2代+中心+下4代，共7代） """
DOWN_GEN = 4
""" 谱系图向下显示的代数 """
GAP = 2
""" 相邻家庭块之间的最小间隔（半角单位），保证排版行的连线段互不粘连 """

# ==== 7. 生育方式与多胎（Race.csv birth_type / multiple_birth_num 列） ====
BIRTH_TYPE_SINGLE = 1
""" 生育方式：单胎胎生（默认） """
BIRTH_TYPE_MULTIPLE = 2
""" 生育方式：多胎胎生（受精时按种族产胎数量范围进行多轮判定） """
BIRTH_TYPE_EGG = 11
""" 生育方式：带壳卵生 """
BIRTH_TYPE_EGG_SOFT = 12
""" 生育方式：无壳卵生（未实装，get_birth_type 归一化为单胎胎生） """
MULTIPLE_BIRTH_SEMEN_DECAY = 0.3
""" 多胎受精判定中，每轮判定后临时精液量的衰减比例 """
IDENTICAL_TWINS_RATE = 1
""" 单胎胎生种族受精成功后为同卵双胞胎的概率（百分比） """

# ==== 8. 无壳卵生（体外排卵 → 体外受精） ====
EXTERNAL_OVULATION_RATE = {1: 5, 2: 10, 3: 15}
""" 体外排卵基础概率（百分比），键为绝顶程度（1普通、2强、3超强；小绝顶不触发），其他部位的基准值 """
EXTERNAL_OVULATION_V_MULT = 2
""" 阴道绝顶的体外排卵概率倍率 """
EXTERNAL_OVULATION_W_MULT = 4
""" 子宫绝顶的体外排卵概率倍率（子宫超强绝顶固定100%） """
EXTERNAL_OVULATION_DRUG_MULT = 2
""" 排卵促进药 / 催眠强制排卵各自对体外排卵概率的倍率（保留到当日排卵机会结束） """
SOFT_EGG_SEMEN_TRANSFER_RATE = 0.8
""" 体外排卵时，子宫与小穴中转移到卵上的精液比例 """
SOFT_EGG_FERTILIZATION_DELAY_HOUR = 1
""" 体外卵自排出起到进行受精判定的时间（小时） """
SOFT_EGG_MIN_SEMEN = 5
""" 体外受精多轮判定的终止阈值：剩余精液量低于该值（毫升）即停止 """
SOFT_EGG_RATE_DIVISOR = 1500
""" 体外受精基础概率公式的精液量除数（部位受精为1000，体外更难） """
SOFT_EGG_LEVEL_RATE = 3
""" 体外受精基础概率公式中每级精液污浊等级的加成（部位受精为5） """
SOFT_EGG_SEMEN_LEVEL_MAX_VOLUME = 5000
""" 体外卵精液污浊 1~10 级换算的基数（毫升） """
SOFT_EGG_SEMEN_LEVEL_EXTRA_STEP = 1000
""" 体外卵精液量超过基数后，每多出该量（毫升）污浊等级+1 """
SOFT_EGG_SEMEN_LEVEL_MAX = 15
""" 体外卵精液污浊等级上限 """
LAY_SOFT_EGG_SECOND_BEHAVIOR = "lay_soft_egg"
""" 体外排卵的二段行为id """
SOFT_EGG_FERTILIZED_SECOND_BEHAVIOR = "soft_egg_fertilized"
""" 体外卵受精的二段行为id """
SOFT_EGG_BORN_SECOND_BEHAVIOR = "soft_egg_born"
""" 无壳卵孵化生产的二段行为id """
