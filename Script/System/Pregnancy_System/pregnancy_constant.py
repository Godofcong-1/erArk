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
STAGE_PREGNANCY = 3
""" 阶段枚举：妊娠 """
STAGE_HATCHING = 4
""" 阶段枚举：孵化中 """
STAGE_PARTURIENT = 5
""" 阶段枚举：临盆 """
STAGE_POSTPARTUM = 6
""" 阶段枚举：产后 """
STAGE_REARING = 7
""" 阶段枚举：育儿 """
STAGE_NAME_LIST = [_("全部"), _("受精"), _("持卵待鉴定"), _("妊娠"), _("孵化中"), _("临盆"), _("产后"), _("育儿")]
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
