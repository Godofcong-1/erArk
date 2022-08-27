class Ability:
    """ 能力对应类型和文字描述 """

    cid: int
    """ 能力id """
    ability_type: int
    """ 类型(0:感觉,1:扩张,2:刻印,3:基础,4:技能,5:性技,6:中毒) """
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
    ability_up_id: int
    """ 对应的升级需求id """
    need_type: str
    """ 需求类型 """
    need_type_id: int
    """ 需求类型的子id """
    value: int
    """ 需求值 """


class AbilityUpType:
    """ 能力对应类型和文字描述 """

    cid: int
    """ 升级id """
    ability_id: int
    """ 能力id """
    now_level: int
    """ 当前等级 """


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


class InstructJudge:
    """ 每个指令的实行值判定数据 """

    cid: int
    """ 编号id """
    instruct_name: str
    """ 对应的指令名字 """
    need_type: str
    """ 需求类型（D为日常，S为性爱） """
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
    info: str
    """ 描述 """


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


class Organ:
    """ 器官对应性别限定和文字描述 """

    cid: int
    """ 器官id """
    organ_type: int
    """ 类型(0:女,1:男,2:通用) """
    name: str
    """ 名字 """


class Profession:
    """ 职业类型名称 """

    cid: int
    """ 职业id """
    name: str
    """ 职业名 """


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
    time: int
    """ 烹饪时间 """
    difficulty: int
    """ 烹饪难度 """


class Season:
    """ 季节配置 """

    cid: int
    """ 季节id """
    name: str
    """ 季节名 """


class SecondEffect:
    """ 行为结算器配置 """

    cid: int
    """ 表id """
    behavior_id: int
    """ 行为id """
    effect_id: int
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


class Talent:
    """ 素质对应类型和文字描述 """

    cid: int
    """ 素质id """
    Talent_type: int
    """ 类型(0:性素质,1:身体素质,2:精神素质,3:技术素质,4:其他素质) """
    name: str
    """ 名字 """
    info: str
    """ 备注说明 """


class TalentType:
    """ 角色能力类型 """

    cid: int
    """ 类型id """
    name: str
    """ 类型名 """


class TalentUp:
    """ 能力对应类型和文字描述 """

    cid: int
    """ 编号id """
    talent_id: int
    """ 对应的升级需求id """
    need_type: str
    """ 需求类型 """
    need_type_id: int
    """ 需求类型的子id """
    value: int
    """ 需求值 """


class WeekDay:
    """ 星期描述配置 """

    cid: int
    """ 周id """
    name: str
    """ 描述 """


class TalkPremise:
    """ 口上前提表 """

    cid: str
    """ 配表id """
    talk_id: str
    """ 所属口上id """
    premise: str
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
    effect_id: str
    """ 达成的效果id（即达成的前提id） """


class TargetPremise:
    """ 执行目标所需的前提id """

    cid: str
    """ 配表id """
    target_id: str
    """ 所属目标id """
    premise_id: str
    """ 所需前提id """


class Target:
    """ ai的目标 """

    cid: str
    """ 目标id """
    state_machine_id: int
    """ 执行的状态机id """
    remarks: str
    """ 备注 """
