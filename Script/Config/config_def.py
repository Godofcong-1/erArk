class Ability:
    """ 能力对应类型和文字描述 """

    cid: int
    """ 能力id """
    ability_type: int
    """ 类型(0:感觉,1:扩张,2:刻印,3:基础,4:技能,5:性技) """
    name: str
    """ 名字 """


class AbilityType:
    """ 角色能力类型 """

    cid: int
    """ 类型id """
    name: str
    """ 类型名 """


class AbilityUp:
    """ 能力对应类型和文字描述 """

    cid: int
    """ 编号id """
    ability_id: int
    """ 能力id """
    now_level: int
    """ 当前等级 """
    up_need: str
    """ 升级需求 """


class Aromatherapy_Recipes:
    """ 香薰疗愈配方 """

    cid: int
    """ 编号id """
    name: str
    """ 配方名 """
    formula: str
    """ 配方(序号为资源序号) """
    difficulty: int
    """ 难易度 """
    info: str
    """ 配方介绍 """


class AssistantServices:
    """ 助理服务 """

    cid: int
    """ 服务id """
    name: str
    """ 服务名 """
    require: str
    """ 服务需求(用#分隔每个选项的需求)(F好感，X信任) """
    option: str
    """ 各个选项 """


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
    effect_id: str
    """ 结算器id """


class Birthplace:
    """ 出生地列表 """

    cid: int
    """ 出生地id """
    name: str
    """ 出生地名 """
    inmap: int
    """ 是否出现在大地图中 """


class BodyPart:
    """ 身体部位表 """

    cid: int
    """ 配表id """
    name: str
    """ 部位名字 """
    volume_table: str
    """ 容积表 """
    normal_flow_table: str
    """ 正常流通表 """
    full_flow_table: str
    """ 满溢流通表 """
    extra_flow_table: str
    """ 额外流通表 """


class Book:
    """ 书籍配置表 """

    cid: int
    """ 书本id """
    name: str
    """ 名字 """
    type: int
    """ 类型 """
    use: int
    """ 特殊用途 """
    info: str
    """ 介绍 """


class BookType:
    """ 书籍类型表 """

    cid: int
    """ 书本类型id """
    father_type_name: str
    """ 书本大类 """
    son_type_name: str
    """ 书本小类 """


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


class CharaSetting:
    """ 角色设置 """

    cid: int
    """ 选项id """
    name: str
    """ 选项名 """
    info: str
    """ 选项介绍 """
    require: str
    """ 选项需求(F好感，X信任) """
    option: str
    """ 各个选项 """


class City:
    """ 势力列表 """

    cid: int
    """ 城市id """
    name: str
    """ 城市名 """
    country_id: int
    """ 所属国家id """


class ClothingTem:
    """ 服装模板 """

    cid: int
    """ 模板id """
    name: str
    """ 服装名字 """
    clothing_type: int
    """ 服装类型 """
    npc: int
    """ 服装角色限制 """
    tag: int
    """ 服装用途标签 """
    describe: str
    """ 描述 """


class ClothingType:
    """ 衣服种类配置 """

    cid: int
    """ 配表id """
    name: str
    """ 部位名字 """
    volume_table: str
    """ 容积表 """
    normal_flow_table: str
    """ 正常流通表 """
    full_flow_table: str
    """ 满溢流通表 """
    extra_flow_table: str
    """ 额外流通表 """


class ClothingUseType:
    """ 服装用途配置 """

    cid: int
    """ 用途id """
    name: str
    """ 用途名字 """


class Collection_bouns:
    """ 收藏物的奖励解锁 """

    cid: int
    """ 奖励id """
    type: str
    """ 收藏物类型 """
    count: int
    """ 解锁所需的收藏数量 """
    info: str
    """ 奖励信息 """


class Entertainment:
    """ 娱乐模板 """

    cid: int
    """ 模板id """
    name: str
    """ 娱乐名 """
    behavior_id: int
    """ 娱乐行动id """
    palce: str
    """ 娱乐地点 """
    need: str
    """ 必要条件 """
    tag: int
    """ 标签 """
    describe: str
    """ 描述 """


class Experience:
    """ 经验名字 """

    cid: int
    """ 经验id """
    name: str
    """ 经验名 """


class Facility:
    """ 基建系统内全设施一览 """

    cid: int
    """ 效果id """
    name: str
    """ 设施名字 """
    type: int
    """ 设施类型-1区块，-2通用，否则为cid归属下的小房间 """
    info: str
    """ 介绍信息 """


class Facility_effect:
    """ 设施在不同等级下的效果 """

    cid: int
    """ 效果id """
    name: str
    """ 设施名字 """
    level: int
    """ 设施等级 """
    effect: int
    """ 设施效果数值 """
    power_use: int
    """ 耗电量 """
    resouce_use: int
    """ 升级需要的基建材料数量 """
    money_use: int
    """ 升级需要的龙门币数量 """
    info: str
    """ 介绍信息 """


class Facility_open:
    """ 待开放的设施一览 """

    cid: int
    """ 设施id """
    name: str
    """ 设施名字 """
    zone_cid: int
    """ 开放所需的区块等级cid """
    NPC_id: int
    """ 开放所需的干员id """
    info: str
    """ 介绍信息 """


class Favorability_Level:
    """ 好感等级 """

    cid: int
    """ 好感等级cid """
    Favorability_point: int
    """ 当前等级好感度最大值 """
    judge_add: int
    """ 实行值加成 """


class First_Bouns:
    """ 初期奖励 """

    cid: int
    """ 奖励id """
    name: str
    """ 奖励名 """
    consume: int
    """ 需要消耗的初期点数 """
    introduce: str
    """ 奖励介绍 """


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


class Food_Quality:
    """ 质量等级 """

    cid: int
    """ 食物质量cid """
    name: str
    """ 质量名 """
    ability_level: int
    """ 料理技能上限 """


class Hypnosis_Talent_Of_Npc:
    """ 干员获得被催眠素质 """

    cid: int
    """ cid """
    hypnosis_talent_id: int
    """ 该素质id """
    hypnosis_degree: int
    """ 催眠深度 """
    need_talent_id: int
    """ 前置素质id """
    second_behavior_id: int
    """ 二段行为id """


class Hypnosis_Talent_Of_Pl:
    """ 玩家升级催眠素质 """

    cid: int
    """ cid """
    hypnosis_talent_id: int
    """ 该素质id """
    need_talent_id: int
    """ 前置素质id """
    pl_experience: int
    """ 需要的玩家催眠经验 """
    max_hypnosis_degree: int
    """ 最高单角色催眠程度 """
    npc_hypnosis_degree: int
    """ 升级需要的NPC总催眠程度 """
    todo: int
    """ 未实装 """


class Hypnosis_Type:
    """ 催眠类型 """

    cid: int
    """ 催眠类型id """
    name: str
    """ 名称 """
    talent_id: int
    """ 需要的素质id """
    hypnosis_degree: int
    """ 需要的催眠程度 """
    introduce: str
    """ 介绍 """


class InstructJudge:
    """ 每个指令的实行值判定数据 """

    cid: int
    """ 编号id """
    instruct_name: str
    """ 对应的指令名字 """
    need_type: str
    """ 需求类型（D为日常，S为性爱，V为访客） """
    value: int
    """ 需求值 """


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
    price: int
    """ 价格 """
    info: str
    """ 描述 """


class JJ:
    """ 阴茎类型 """

    cid: int
    """ 阴茎id """
    name: str
    """ 阴茎名称 """


class Juel:
    """ 珠名字 """

    cid: int
    """ 珠id """
    name: str
    """ 珠名 """


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


class Nation:
    """ 势力列表 """

    cid: int
    """ 势力id """
    name: str
    """ 势力名 """


class Organ:
    """ 器官对应性别限定和文字描述 """

    cid: int
    """ 器官id """
    organ_type: int
    """ 类型(0:女,1:男,2:通用) """
    name: str
    """ 名字 """


class ProductFormula:
    """ 产品配方 """

    cid: int
    """ 编号id """
    product_id: int
    """ 产品的资源id """
    formula: str
    """ 配方(序号为资源序号) """
    difficulty: int
    """ 难易度 """


class Profession:
    """ 职业类型名称 """

    cid: int
    """ 职业id """
    name: str
    """ 职业名 """


class Prts:
    """ 教程的问题及回答 """

    cid: int
    """ 编号id """
    fater_type: int
    """ 父类id(0系统，1日常，2攻略，3H，4经营) """
    son_type: int
    """ 子类id """
    qa: str
    """ 问题还是回答 """
    text: str
    """ 内容 """


class Race:
    """ 种族类型名称 """

    cid: int
    """ 种族id """
    name: str
    """ 种族名 """


class Recipes:
    """ 菜谱配置 """

    cid: int
    """ 菜谱id """
    name: str
    """ 菜谱名字 """
    type: int
    """ 菜的类型（0正餐1零食2饮品3酒类4乳制品8加料咖啡9其他） """
    time: int
    """ 烹饪时间 """
    difficulty: int
    """ 烹饪难度 """
    money: int
    """ 价格 """
    introduce: str
    """ 说明介绍 """


class Recruitment_Strategy:
    """ 招聘策略配置 """

    cid: int
    """ 招聘策略id """
    name: str
    """ 招聘策略名 """
    introduce: str
    """ 招聘策略介绍 """


class Reproduction_period:
    """ 生理期周期 """

    cid: int
    """ 模板id """
    name: str
    """ 日期名 """
    type: int
    """ 日期类型(0安全1普通2危险3排卵) """


class Resouce:
    """ 各类基地使用资源一览 """

    cid: int
    """ 资源id """
    name: str
    """ 资源名字 """
    type: str
    """ 资源类型 """
    price: int
    """ 资源价格 """
    cant_buy: int
    """ 是否无法购买 """
    info: str
    """ 介绍信息 """


class Season:
    """ 季节配置 """

    cid: int
    """ 季节id """
    name: str
    """ 季节名 """


class Seasoning:
    """ 特殊调味表 """

    cid: int
    """ 配表id """
    name: str
    """ 调味名字 """


class SecondEffect:
    """ 行为结算器配置 """

    cid: int
    """ 表id """
    behavior_id: int
    """ 行为id """
    effect_id: str
    """ 结算器id """


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


class Sleep_Level:
    """ 睡眠等级 """

    cid: int
    """ 睡眠等级cid """
    name: str
    """ 等级名 """
    sleep_point: int
    """ 当前等级熟睡值上限 """


class SolarPeriod:
    """ 节气配置 """

    cid: int
    """ 节气id """
    name: str
    """ 节气名 """
    season: int
    """ 所属季节id """


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


class System_Setting:
    """ 角色设置 """

    cid: int
    """ 选项id """
    name: str
    """ 选项名 """
    info: str
    """ 选项介绍 """
    option: str
    """ 各个选项 """


class Talent:
    """ 素质对应类型和文字描述 """

    cid: int
    """ 素质id """
    Talent_type: int
    """ 类型(0:性素质,1:身体素质,2:精神素质,3:技术素质,4:其他素质) """
    name: str
    """ 名字 """
    heredity: int
    """ 是否可遗传 """
    info: str
    """ 备注说明 """


class TalentGain:
    """ 素质的获得 """

    cid: int
    """ 编号id """
    talent_id: int
    """ 素质id """
    second_behavior_id: int
    """ 二段行为结算id """
    gain_type: int
    """ 获得类型(0随时自动，1手动，2指令绑定，3睡觉自动) """
    gain_need: str
    """ 获得需求(F好感，X信任) """
    replace_talent_id: int
    """ 取代的旧素质id """


class TalentType:
    """ 角色能力类型 """

    cid: int
    """ 类型id """
    name: str
    """ 类型名 """


class Talent_Of_Arts:
    """ 源石技艺素质 """

    cid: int
    """ 序号 """
    talent_id: int
    """ 素质id """
    need_id: int
    """ 前置需求素质id """
    level: int
    """ 能力等级 """
    todo: int
    """ 未实装 """


class Tip:
    """ 提示信息 """

    cid: int
    """ 提示id """
    type: str
    """ 提示类型 """
    info: str
    """ 提示内容 """


class Trust_Level:
    """ 信赖等级 """

    cid: int
    """ 信赖等级cid """
    Trust_point: int
    """ 当前等级信赖最大值 """
    judge_add: int
    """ 实行值加成 """


class Visitor_Stay_Attitude:
    """ 访客停留态度 """

    cid: int
    """ 态度id """
    name: str
    """ 态度名 """
    rate: float
    """ 态度几率 """


class WeekDay:
    """ 星期描述配置 """

    cid: int
    """ 周id """
    name: str
    """ 描述 """


class WorkType:
    """ 工作模板 """

    cid: int
    """ 模板id """
    name: str
    """ 工作名 """
    department: str
    """ 工作部门 """
    place: str
    """ 工作地点 """
    tag: int
    """ 标签 """
    need: str
    """ 必要条件 """
    describe: str
    """ 描述 """


class World_Setting:
    """ 世界设定 """

    cid: int
    """ 设定id """
    name: str
    """ 设定名 """
    introduce: str
    """ 设定介绍 """


class Talk:
    """ 口上配置数据 """

    cid: str
    """ 口上id """
    behavior_id: int
    """ 触发口上的行为id """
    adv_id: int
    """ 口上限定的剧情npcid """
    premise: str
    """ 前提id """
    context: str
    """ 口上内容 """


class TargetEffect:
    """ 执行目标所能达成的效果id """

    cid: str
    """ 配表id """
    target_id: str
    """ 所属目标id """
    effect_id: str
    """ 达成的效果id（即达成的前提id） """


class Target:
    """ ai的目标 """

    cid: str
    """ 目标id """
    state_machine_id: int
    """ 执行的状态机id """
    premise_id: str
    """ 所需前提id """
    remarks: str
    """ 备注 """
