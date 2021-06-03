class Ability:
    """ 能力对应类型和文字描述 """

    cid: int
    """ 能力id """
    ability_type: int
    """ 类型(0:感觉,1:扩张,2:刻印,3:基础) """
    name: str
    """ 名字 """


class AbilityType:
    """ 角色能力类型 """

    cid: int
    """ 类型id """
    name: str
    """ 类型名 """


class AgeJudgeSexExperienceTem:
    """ 不同性别不同年龄段对应生成不同性经验模板的权重 """

    cid: int
    """ 模板id """
    sex: int
    """ 性别类型 """
    age: int
    """ 年龄段 """
    sex_exp_tem: int
    """ 性经验模板 """
    weight: int
    """ 权重 """


class AgeTem:
    """ 不同年龄段模板的年龄范围 """

    cid: int
    """ 模板id """
    max_age: int
    """ 最大年龄 """
    min_age: int
    """ 最小年龄 """


class AttrTem:
    """ 性别对应的角色各项基础属性模板 """

    cid: int
    """ 模板id """
    sex: int
    """ 性别 """
    age_tem: int
    """ 年龄模板id """
    hit_point_tem: int
    """ HP模板id """
    mana_point_tem: int
    """ MP模板id """
    sex_experience: int
    """ 性经验模板id """
    weight_tem: int
    """ 体重模板id """
    body_fat_tem: int
    """ 体脂率模板id """


class BarConfig:
    """ 比例条名字对应的状态图片和绘制宽度 """

    cid: int
    """ 比例条id """
    name: str
    """ 比例条名字 """
    ture_bar: str
    """ 进度条图片 """
    null_bar: str
    """ 背景条图片 """
    width: int
    """ 图片绘制宽度 """


class BehaviorEffect:
    """ 行为结算器配置 """

    cid: int
    """ 表id """
    behavior_id: int
    """ 行为id """
    effect_id: int
    """ 结算器id """


class BodyFatTem:
    """ 按性别划分的体脂率模板和范围 """

    cid: int
    """ 模板id """
    sex_type: int
    """ 性别类型 0:男,1:女 """
    sub_type: int
    """ 体脂率子类型 """
    min_value: float
    """ 最小值 """
    max_value: float
    """ 最大值 """


class Book:
    """ 书籍配置表 """

    cid: int
    """ 书本id """
    name: str
    """ 名字 """
    info: str
    """ 介绍 """


class CharacterState:
    """ 角色状态属性表 """

    cid: int
    """ 配表id """
    name: str
    """ 状态名字 """
    type: int
    """ 状态类型 """


class CharacterStateType:
    """ 角色状态类型 """

    cid: int
    """ 类型id """
    name: str
    """ 类型名 """


class Chara_image:
    """ 角色ID对应的角色图片和绘制宽度 """

    cid: int
    """ 图片id """
    chara_id: str
    """ 角色id """
    image_name: str
    """ 图片名字 """
    width: int
    """ 图片绘制宽度 """


class ChestTem:
    """ 罩杯对应范围和生成权重 """

    cid: int
    """ 模板id """
    min_value: float
    """ 最小值 """
    max_value: float
    """ 最大值 """
    weight_fix: float
    """ 体重修正 """
    weight: int
    """ 权重 """
    info: str
    """ 描述 """


class ClothingEvaluate:
    """ 服装评价描述 """

    cid: int
    """ 评价id """
    name: str
    """ 评价名 """


class ClothingSuit:
    """ 套装配置数据 """

    cid: int
    """ 套装id """
    clothing_id: int
    """ 服装id """
    suit_type: int
    """ 套装编号 """
    sex: int
    """ 性别限制 """


class ClothingTem:
    """ 服装模板 """

    cid: int
    """ 模板id """
    name: str
    """ 服装名字 """
    clothing_type: int
    """ 服装类型 """
    sex: int
    """ 服装性别限制 """
    tag: int
    """ 服装用途标签 """
    describe: str
    """ 描述 """


class ClothingType:
    """ 衣服种类配置 """

    cid: int
    """ 类型id """
    name: str
    """ 类型名字 """


class ClothingUseType:
    """ 服装用途配置 """

    cid: int
    """ 用途id """
    name: str
    """ 用途名字 """


class Course:
    """ 课程配置数据 """

    cid: int
    """ 课程id """
    name: str
    """ 名字 """


class CourseSkillExperience:
    """ 课程获取技能经验配置 """

    cid: int
    """ 配置id """
    course: int
    """ 课程类型 """
    skill_type: int
    """ 技能类型0:知识1语言 """
    skill: int
    """ 技能id """
    experience: float
    """ 经验 """


class EndAgeTem:
    """ 性别对应平均寿命 """

    cid: int
    """ 模板id """
    sex: int
    """ 性别id """
    end_age: int
    """ 平均寿命 """


class Experience:
    """ 经验名字 """

    cid: int
    """ 经验id """
    name: str
    """ 经验名 """


class FontConfig:
    """ 字体样式配置数据(富文本用) """

    cid: int
    """ 样式id """
    name: str
    """ 字体名 """
    foreground: str
    """ 前景色 """
    background: str
    """ 背景色 """
    font: str
    """ 字体 """
    font_size: int
    """ 字体大小 """
    bold: bool
    """ 加粗 """
    underline: bool
    """ 下划线 """
    italic: bool
    """ 斜体 """
    selectbackground: str
    """ 选中时背景色 """
    info: str
    """ 备注 """


class Food:
    """ 食材配置数据 """

    cid: int
    """ 食材id """
    name: str
    """ 食材名字 """
    cook: bool
    """ 可烹饪 """
    eat: bool
    """ 可食用 """
    seasoning: bool
    """ 可作为调料 """
    fruit: bool
    """ 是水果 """


class FoodFeel:
    """ 食材效果配置数据 """

    cid: int
    """ 表id """
    food_id: int
    """ 所属食材id """
    feel_id: int
    """ 效果id """
    feel_value: float
    """ 效果数值 """


class FoodQualityWeight:
    """ 烹饪技能等级制造食物品质权重配置 """

    cid: int
    """ 配置表id """
    level: int
    """ 烹饪技能等级 """
    quality: int
    """ 食物品质 """
    weight: int
    """ 权重 """


class HeightTem:
    """ 身高预期权值模板 """

    cid: int
    """ 模板id """
    sex: int
    """ 性别id """
    max_value: float
    """ 最大值 """
    min_value: float
    """ 最小值 """


class HitPointTem:
    """ hp模板对应平均值 """

    cid: int
    """ 模板id """
    max_value: int
    """ 最大值 """


class InstructType:
    """ 指令类型配置 """

    cid: int
    """ 指令类型id """
    name: str
    """ 名字 """


class Item:
    """ 道具配置数据 """

    cid: int
    """ 道具id """
    name: str
    """ 道具名 """
    tag: str
    """ 标签 """
    info: str
    """ 描述 """


class Juel:
    """ 珠名字 """

    cid: int
    """ 珠id """
    name: str
    """ 珠名 """


class Knowledge:
    """ 技能配置信息 """

    cid: int
    """ 技能id """
    name: str
    """ 名字 """
    type: int
    """ 类型 """


class KnowledgeType:
    """ 技能类型配置信息 """

    cid: int
    """ 技能类型id """
    name: str
    """ 名字 """


class Language:
    """ 语言配置信息 """

    cid: int
    """ 语言id """
    name: str
    """ 名字 """
    difficulty: int
    """ 学习难度 """
    family: int
    """ 语族 """
    info: str
    """ 描述 """


class ManaPointTem:
    """ mp模板对应平均值 """

    cid: int
    """ 模板id """
    max_value: int
    """ 最大值 """


class Moon:
    """ 月相配置(明日更满为正反之为负) """

    cid: int
    """ 月相id """
    name: str
    """ 月相 """
    type: int
    """ 月相类型 """
    min_phase: float
    """ 最小亮度 """
    max_phase: float
    """ 最大亮度 """


class MoveMenuType:
    """ 移动菜单类型 """

    cid: int
    """ 移动类型id """
    name: str
    """ 名字 """


class Nature:
    """ 性格倾向配置 """

    cid: int
    """ 性格id """
    nature_type: int
    """ 类型 """
    good: str
    """ 正面倾向 """
    bad: str
    """ 负面倾向 """


class NatureTag:
    """ 性格倾向标签 """

    cid: int
    """ 性格标签id """
    good: str
    """ 正面倾向 """
    bad: str
    """ 负面倾向 """


class OccupationAgeRegion:
    """ 学生和老师的年龄段生成权重区间配置 """

    cid: int
    """ 区间id """
    occupation: str
    """ 职业 """
    age_region: int
    """ 年龄段 """
    region: int
    """ 权重区间 """


class OccupationBMIRegion:
    """ 学生和老师各自肥胖率配置 """

    cid: int
    """ 区间id """
    occupation: str
    """ 职业 """
    bmi_type: int
    """ bmi类型 """
    region: int
    """ 权重区间 """


class OccupationBodyFatRegion:
    """ 年龄段下体重对应各体脂率范围权重 """

    cid: int
    """ 模板id """
    occupation: str
    """ 职业 """
    bmi_id: int
    """ 体重模板 """
    bodyfat_type: int
    """ 体脂率模板 """
    region: int
    """ 权重区间 """


class Organ:
    """ 器官对应性别限定和文字描述 """

    cid: int
    """ 器官id """
    organ_type: int
    """ 类型(0:女,1:男,2:通用) """
    name: str
    """ 名字 """


class Recipes:
    """ 菜谱配置 """

    cid: int
    """ 菜谱id """
    name: str
    """ 菜谱名字 """
    time: int
    """ 烹饪时间 """


class RecipesFormula:
    """ 菜谱配方配置 """

    cid: int
    """ 配方id """
    recipe_id: int
    """ 所属菜谱id """
    formula_type: int
    """ 配方类型 """
    food_id: int
    """ 食材id """


class RecipesFormulaType:
    """ 菜谱配方类型 """

    cid: int
    """ 表id """
    name: str
    """ 菜谱配方名字 """


class School:
    """ 学校配置 """

    cid: int
    """ 学校id """
    name: str
    """ 名字 """
    day: int
    """ 每周上课天数 """
    min_age: int
    """ 最小年龄 """
    max_age: int
    """ 最大年龄 """


class SchoolPhaseCourse:
    """ 各学校各年级教学科目配置 """

    cid: int
    """ 配表id """
    school: int
    """ 学校id """
    phase: int
    """ 年级 """
    course: int
    """ 课程id """


class SchoolSession:
    """ 各学校上课时间配置 """

    cid: int
    """ 配表id """
    school_id: int
    """ 学校id """
    session: int
    """ 当天课时编号 """
    start_time: int
    """ 开始时间 """
    end_time: int
    """ 结束时间 """


class Season:
    """ 季节配置 """

    cid: int
    """ 季节id """
    name: str
    """ 季节名 """


class SexExperience:
    """ 性经验丰富程度模板对应器官性经验模板 """

    cid: int
    """ 表id """
    sex_exp_type: int
    """ 性经验丰富程度大类 """
    organ_id: int
    """ 器官id """
    exp_tem: int
    """ 经验模板 """


class SexExperienceTem:
    """ 器官类型性经验丰富程度对应经验范围 """

    cid: int
    """ 模板id """
    sex_exp_tem_type: int
    """ 器官类型 """
    sub_type: int
    """ 子类型 """
    max_exp: int
    """ 最大经验 """
    min_exp: int
    """ 最小经验 """


class SexTem:
    """ 性别对应描述和性别器官模板 """

    cid: int
    """ 性别id """
    name: str
    """ 性别名称 """
    has_man_organ: bool
    """ 是否有男性器官 """
    has_woman_organ: bool
    """ 是否有女性器官 """
    region: int
    """ 随机npc生成性别权重 """


class SocialType:
    """ 关系类型配置 """

    cid: int
    """ 关系id """
    name: str
    """ 名字 """


class SolarPeriod:
    """ 节气配置 """

    cid: int
    """ 节气id """
    name: str
    """ 节气名 """
    season: int
    """ 所属季节id """


class StatureDescriptionPremise:
    """ 身材描述文本依赖前提配置 """

    cid: int
    """ 配表id """
    stature_type: int
    """ 描述文本id """
    premise: int
    """ 前提id """


class StatureDescriptionText:
    """ 角色身材描述文本 """

    cid: int
    """ 描述文本id """
    text: str
    """ 文本 """


class Status:
    """ 状态描述配置 """

    cid: int
    """ 状态id """
    name: str
    """ 描述 """


class SunTime:
    """ 太阳时间配置 """

    cid: int
    """ 太阳时间id """
    name: str
    """ 太阳时间名 """


class WaistHipProportion:
    """ 不同肥胖程度腰臀比例差值配置 """

    cid: int
    """ 比例id """
    weitht_tem: int
    """ 肥胖程度模板id """
    value: float
    """ 差值比 """


class WeekDay:
    """ 星期描述配置 """

    cid: int
    """ 周id """
    name: str
    """ 描述 """


class WeightTem:
    """ 体重模板对应体重范围 """

    cid: int
    """ 模板id """
    min_value: float
    """ 最小值 """
    max_value: float
    """ 最大值 """


class TalkPremise:
    """ 口上前提表 """

    cid: str
    """ 配表id """
    talk_id: str
    """ 所属口上id """
    premise: int
    """ 前提id """


class Talk:
    """ 口上配置数据 """

    cid: str
    """ 口上id """
    behavior_id: int
    """ 触发口上的行为id """
    adv_id: int
    """ 口上限定的剧情npcid """
    context: str
    """ 口上内容 """


































































































class TargetEffect:
    """ 执行目标所能达成的效果id """

    cid: str
    """ 配表id """
    target_id: str
    """ 所属目标id """
    effect_id: int
    """ 达成的效果id """


class TargetPremise:
    """ 执行目标所需的前提id """

    cid: str
    """ 配表id """
    target_id: str
    """ 所属目标id """
    premise_id: int
    """ 所需前提id """


class Target:
    """ ai的目标 """

    cid: str
    """ 目标id """
    state_machine_id: int
    """ 执行的状态机id """
    remarks: str
    """ 备注 """
