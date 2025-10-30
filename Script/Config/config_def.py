class Ability:
    """ 能力对应类型和文字描述 """

    cid: int
    """ 能力id """
    ability_type: int
    """ 类型(0:感度,1:扩张,2:刻印,3:基础,4:技能,5:性技) """
    name: str
    """ 名字 """
    sex_need: int
    """ 性别需求(-1都可0男1女) """


class AbilityType:
    """ 角色能力类型 """

    cid: int
    """ 类型id """
    name: str
    """ 类型名 """


class AbilityUp:
    """ 能力升级数据表 """

    cid: int
    """ 编号id """
    ability_id: int
    """ 能力id """
    now_level: int
    """ 当前等级 """
    up_need: str
    """ 升级需求 """
    up_need2: str
    """ 升级需求2 """


class Ability_Lv_Adjust:
    """ 能力等级的调整值 """

    cid: int
    """ 列表id """
    ability_lv: int
    """ 能力等级 """
    adjust_value: float
    """ 能力调整值 """


class Achievement:
    """ 成就数据表 """

    cid: int
    """ 成就cid """
    name: str
    """ 成就名 """
    type: str
    """ 成就类型 """
    difficulty: int
    """ 成就难度 """
    value: int
    """ 成就数值需求 """
    pre_id: int
    """ 前置成就需求id """
    special: int
    """ 是否为特殊成就 """
    todo: int
    """ 是否未实装 """
    description: str
    """ 成就介绍 """


class Ai_Chat_Send_Data:
    """ 向AI发送的数据 """

    cid: int
    """ 数据id """
    name: str
    """ 数据名 """
    required: int
    """ 是否必选 """
    data_size: int
    """ 数据量(1小2中3大) """
    default: int
    """ 是否默认已选 """
    prompt: str
    """ 提示词 """


class Ai_Chat_Setting:
    """ 角色设置 """

    cid: int
    """ 选项id """
    name: str
    """ 选项名 """
    info: str
    """ 选项介绍 """
    option: str
    """ 各个选项 """


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
    sex_need: int
    """ 性别需求(-1通用0男1女) """
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


class Behavior_Data:
    """ 状态描述配置 """

    cid: int
    """ 状态id """
    en_name: str
    """ 英文名称 """
    name: str
    """ 描述 """
    duration: int
    """ 耗时 """
    trigger: str
    """ 触发人 """
    tag: str
    """ 标签 """


class Behavior_Effect:
    """ 行为结算器配置 """

    cid: int
    """ 表id """
    behavior_id: str
    """ 行为id """
    effect_id: str
    """ 结算器id """


class Behavior_Effect_bak:
    """ 行为结算器配置 """

    cid: int
    """ 表id """
    behavior_id: int
    """ 行为id """
    effect_id: str
    """ 结算器id """


class Behavior_Introduce:
    """ 状态描述配置 """

    cid: int
    """ 状态id """
    en_name: str
    """ 英文名称 """
    name: str
    """ 描述 """
    introduce: str
    """ 状态介绍 """


class Birthplace:
    """ 出生地列表 """

    cid: int
    """ 出生地id """
    name: str
    """ 出生地名 """
    inmap: int
    """ 是否出现在大地图中 """
    infect_rate: float
    """ 初始源石病感染率 """


class Board_Game:
    """ 桌游类型表 """

    cid: int
    """ 桌游cid """
    name: str
    """ 桌游名字 """


class BodyPart:
    """ 身体部位表 """

    cid: int
    """ 配表id """
    name: str
    """ 部位名字 """
    max_volume: int
    """ 最大容积 """
    normal_flow_table: str
    """ 正常流通表 """
    full_flow_table: str
    """ 满溢流通表 """
    extra_flow_table: str
    """ 额外流通表 """


class Body_Item:
    """ 身体道具 """

    cid: int
    """ 身体道具id """
    name: str
    """ 身体道具名 """
    type: int
    """ 道具类型 """
    behavior_id: str
    """ 二段结算id """


class Body_Manage_Requirement:
    """ 身体管理需要满足的条件 """

    cid: int
    """ 序号 """
    second_behavior_id: str
    """ 二段行为id """
    need_examine_id: str
    """ 需要的检查状态id """
    behavior_id: str
    """ 进行的一段行为id """
    need_value_1: int
    """ 需要数值1 """
    need_value_2: int
    """ 需要数值2 """
    need_value_3: int
    """ 需要数值3 """
    todo: int
    """ 未实装 """


class Bondage:
    """ 绳子捆绑 """

    cid: int
    """ 绳子捆绑id """
    name: str
    """ 绳子捆绑名 """
    level: int
    """ 捆绑等级 """
    affect_walking: int
    """ 影响行走 """
    need_facility: int
    """ 需要设施 """
    description: str
    """ 捆绑介绍 """


class Book:
    """ 书籍配置表 """

    cid: int
    """ 书本id """
    name: str
    """ 名字 """
    type: int
    """ 类型 """
    difficulty: int
    """ 难度 """
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
    exp_id: int
    """ 对应经验id """
    ability_id: int
    """ 对应能力id """


class Book_Excerpt:
    """ 书籍节选配置表 """

    cid: int
    """ 书本id """
    name: str
    """ 名字 """
    excerpt1: str
    """ 内容节选1 """
    excerpt2: str
    """ 内容节选2 """
    excerpt3: str
    """ 内容节选3 """
    excerpt4: str
    """ 内容节选4 """
    excerpt5: str
    """ 内容节选5 """


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


class Character_State_Level:
    """ 状态等级 """

    cid: int
    """ 状态等级cid """
    level: int
    """ 当前等级 """
    max_value: int
    """ 当前等级状态最大值 """


class CharaSetting:
    """ 角色设置 """

    cid: int
    """ 选项id """
    name: str
    """ 选项名 """
    info: str
    """ 选项介绍 """
    require: str
    """ 选项需求(F好感，X信任，G攻略等级) """
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
    max_volume: int
    """ 最大容积 """
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
    effect_1: int
    """ 奖励数据1 """
    effect_2: int
    """ 奖励数据2 """
    effect_3: int
    """ 奖励数据3 """
    info: str
    """ 奖励信息 """


class Commission:
    """ 委托任务表 """

    cid: int
    """ 委托id """
    name: str
    """ 委托名字 """
    country_id: int
    """ 国家id(-1为通用) """
    level: int
    """ 委托等级 """
    type: str
    """ 委托类型 """
    people: int
    """ 派遣人数 """
    time: int
    """ 耗时天数 """
    demand: str
    """ 具体需求 """
    reward: str
    """ 具体奖励(a能力、e经验、j宝珠、t_素质编号_0为取消1为获得、r资源、c_角色adv编号_0不包含1包含、招募_adv编号_0未招募1已招募、攻略_adv编号_程度0~4、m_委托编号_-1不可完成0可以进行1已完成、声望_0为当地其他为对应势力id_加值为小数点后两位) """
    related_id: int
    """ 关联的委托id """
    special: int
    """ 特殊委托 """
    description: str
    """ 委托介绍 """


class Confinement_Training_Setting:
    """ 监禁调教设置 """

    cid: int
    """ 选项id """
    name: str
    """ 选项名 """
    info: str
    """ 选项介绍 """
    option: str
    """ 各个选项 """


class Diplomatic_Policy:
    """ 外交政策 """

    cid: int
    """ 编号id """
    name: str
    """ 政策名 """
    difficulty: int
    """ 难易度 """
    need: str
    """ 其他需求 """
    info: str
    """ 政策介绍 """


class Entertainment:
    """ 娱乐模板 """

    cid: int
    """ 模板id """
    name: str
    """ 娱乐名 """
    behavior_id: int
    """ 娱乐行动id """
    place: str
    """ 娱乐地点 """
    place_tag: str
    """ 地点tag """
    need: str
    """ 必要条件 """
    tag: int
    """ 标签 """
    auto_ai: int
    """ 是否使用自动ai行动 """
    auto_ai_move: str
    """ 自动ai移动数据 """
    auto_ai_entertainment: str
    """ 自动ai工作数据 """
    describe: str
    """ 描述 """


class Equipment_Condition:
    """ 装备情况等级 """

    cid: int
    """ 装备情况cid """
    name: str
    """ 装备情况名 """
    value: int
    """ 数值 """


class Equipment_Damage_Rate:
    """ 装备损坏概率 """

    cid: int
    """ 装备损坏概率cid """
    commision_lv: int
    """ 委托等级 """
    rate_0: float
    """ 不损坏概率 """
    rate_1: float
    """ 状况-1概率 """
    rate_2: float
    """ 状况-2概率 """
    rate_3: float
    """ 状况-3概率 """
    rate_4: float
    """ 状况-4概率 """


class Equipment_Maintain_Setting:
    """ 装备维修保养设置 """

    cid: int
    """ 选项id """
    name: str
    """ 选项名 """
    info: str
    """ 选项介绍 """
    option: str
    """ 各个选项 """


class Experience:
    """ 经验名字 """

    cid: int
    """ 经验id """
    name: str
    """ 经验名 """
    type: int
    """ 经验类型 """


class Experience_Relations:
    """ 快感经验之间的关系 """

    base_exp_id: int
    """ 基础经验id """
    base_exp_name: str
    """ 基础经验名 """
    climax_exp_id: int
    """ 绝顶经验id """
    sex_exp_id: int
    """ 性交经验id """
    unconscious_exp_id: int
    """ 无意识经验id """
    expansion_exp_id: int
    """ 扩张经验id """


class Experience_Types:
    """ 经验类型 """

    type_id: int
    """ 经验类型id """
    type_name: str
    """ 经验类型名 """
    description: str
    """ 经验类型具体说明 """


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


class Gift_Items:
    """ 礼物物品 """

    cid: int
    """ 编号id """
    item_id: int
    """ 道具id """
    type: int
    """ 礼物类型 """
    todo: int
    """ 是否未实装 """
    info: str
    """ 描述 """


class Hidden_Level:
    """ 隐蔽等级 """

    cid: int
    """ 隐蔽等级cid """
    name: str
    """ 等级名 """
    hidden_point: int
    """ 当前等级隐蔽值上限 """


class Hypnosis_Sub_Type:
    """ 催眠子类型 """

    cid: int
    """ 催眠类型id """
    name: str
    """ 名称 """
    behavior_id: str
    """ 行为名 """
    type: int
    """ 所属类型（3体控4心控） """
    introduce: str
    """ 介绍 """


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
    second_behavior_id: str
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
    color: str
    """ 颜色 """


class Instruct_Sex_Type:
    """ 指令类型配置 """

    cid: int
    """ 指令类型id """
    name: str
    """ 名字 """
    color: str
    """ 颜色 """


class Item:
    """ 道具配置数据 """

    cid: int
    """ 道具id """
    name: str
    """ 道具名 """
    type: str
    """ 类型 """
    tag: str
    """ 标签 """
    level: int
    """ 等级 """
    price: int
    """ 价格 """
    effect: int
    """ 效果 """
    h_item_id: int
    """ h道具的id """
    info: str
    """ 描述 """


class Item_h_equip:
    """ H用装备型道具 """

    cid: int
    """ 道具id """
    name: str
    """ 道具名 """
    item_id: int
    """ 道具id """


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


class Mark_Down:
    """ 刻印降级数据表 """

    cid: int
    """ 编号id """
    ability_id: int
    """ 能力id """
    now_level: int
    """ 当前等级 """
    need_juel_all_value: int
    """ 降级需求的总宝珠值 """
    need_juel_1: str
    """ 降级需求的宝珠1，1号同全快感珠 """
    need_juel_2: str
    """ 降级需求的宝珠2 """
    need_juel_3: str
    """ 降级需求的宝珠3 """


class Mark_Up:
    """ 刻印升级数据表 """

    cid: int
    """ 编号id """
    ability_id: int
    """ 能力id """
    now_level: int
    """ 当前等级 """
    second_behavior: str
    """ 二段行为id """
    need_state_all_value: int
    """ 升级需求的总状态值 """
    need_state_1: str
    """ 升级需求的状态1 """
    need_state_2: str
    """ 升级需求的状态2 """
    need_state_3: str
    """ 升级需求的状态3 """
    need_state_4: str
    """ 升级需求的状态4 """
    need_juel_type: int
    """ 升级需求的宝珠类型 """


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
    country: int
    """ 所属国别(见Birthplace.csv) """
    leader: str
    """ 领导人 """
    introduction: str
    """ 介绍 """


class New_Round_Inherit:
    """ 新周目继承时的各类数据计算 """

    cid: int
    """ 继承cid """
    inherit_type: int
    """ 继承类型id(0源石技艺，1玩家能力经验，2玩家HPMP理智精液额外上限，3收集品，4好感信赖，5干员能力经验) """
    inherit_lv: int
    """ 继承等级 """
    inherit_rate: int
    """ 继承比例 """
    point_cost: int
    """ 周目点数消耗 """


class Organ:
    """ 器官对应性别限定和文字描述 """

    cid: int
    """ 器官id """
    organ_type: int
    """ 类型(0:女,1:男,2:通用) """
    name: str
    """ 名字 """


class Physical_Exam_Setting:
    """ 体检日程设置 """

    cid: int
    """ 选项id """
    name: str
    """ 选项名 """
    info: str
    """ 选项介绍 """
    option: str
    """ 各个选项 """


class Pleasure_Relations:
    """ 快感属性之间的关系 """

    cid: int
    """ 角色快感id """
    state_name: str
    """ 快感名 """
    ability_id: int
    """ 能力id """
    experience_id: int
    """ 经验id """


class Power_Generation:
    """ 发电数据 """

    cid: int
    """ 编号 """
    category: str
    """ 类别 """
    level: int
    """ 等级或分类 """
    value: float
    """ 数值 """
    unit: str
    """ 单位 """
    note: str
    """ 说明 """


class Power_Storage:
    """ 蓄电数据 """

    cid: int
    """ 编号 """
    category: str
    """ 类别 """
    level: int
    """ 等级 """
    value: float
    """ 数值 """
    unit: str
    """ 单位 """
    note: str
    """ 说明 """


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
    """ 菜的类型（0正餐1零食2饮品3酒类4乳制品5预制食物8加料咖啡9其他） """
    time: int
    """ 烹饪时间 """
    difficulty: int
    """ 烹饪难度 """
    money: int
    """ 价格 """
    restaurant: int
    """ 餐馆id """
    introduce: str
    """ 说明介绍 """


class Recruitment_Strategy:
    """ 招聘策略配置 """

    cid: int
    """ 招聘策略id """
    name: str
    """ 招聘策略名 """
    lv: int
    """ 开放该策略所需的设施等级 """
    adjust: float
    """ 策略难度调整，越大越容易 """
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


class Reputation_Level:
    """ 声望等级 """

    cid: int
    """ 声望等级cid """
    name: str
    """ 声望等级名 """
    threshold: int
    """ 声望阈值 """


class Resource:
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
    specialty: int
    """ 地区特产(对应出身地cid) """
    info: str
    """ 介绍信息 """


class Restaurant:
    """ 餐馆名字 """

    cid: int
    """ 餐馆id """
    name: str
    """ 餐馆名 """
    tag_name: str
    """ 餐馆标签 """


class Roleplay:
    """ 角色扮演列表 """

    cid: int
    """ 角色扮演id """
    name: str
    """ 角色扮演名 """
    type: str
    """ 角色扮演类型 """
    sub_type: str
    """ 角色扮演子类型 """
    info: str
    """ 角色扮演介绍 """


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


class Semen_Shoot_Amount:
    """ 射出精液量 """

    cid: int
    """ 精液量id """
    behavior_id: str
    """ 行动指令名 """
    base_semen_amount: int
    """ 基础射精量，单位ml """


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


class Sex_Position:
    """ 性交姿势列表 """

    cid: int
    """ 性交姿势id """
    name: str
    """ 性交姿势名 """
    type: str
    """ 性交姿势类型 """
    info: str
    """ 性交姿势介绍 """


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


class SunTime:
    """ 太阳时间配置 """

    cid: int
    """ 太阳时间id """
    name: str
    """ 太阳时间名 """


class Supply_Strategy:
    """ 供电策略 """

    cid: int
    """ 供电策略cid """
    name: str
    """ 策略名 """
    adjust: float
    """ 策略系数 """


class System_Setting:
    """ 系统设置 """

    cid: int
    """ 选项id """
    type: str
    """ 选项类型 """
    name: str
    """ 选项名 """
    info: str
    """ 选项介绍 """
    option: str
    """ 各个选项 """
    default_value: int
    """ 默认值 """


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
    second_behavior_id: str
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
    lv_up_value1: int
    """ 升级用数值1 """
    lv_up_value2: int
    """ 升级用数值2 """
    todo: int
    """ 未实装 """


class Target_Type:
    """ AI行动目标的类型表 """

    cid: int
    """ 类型id """
    father_type: str
    """ 父类 """
    name: str
    """ 名字 """


class Tip:
    """ 提示信息 """

    cid: int
    """ 提示id """
    type: str
    """ 提示类型 """
    facility_id: int
    """ 设施区块id """
    info: str
    """ 提示内容 """


class Tip_Chara:
    """ 角色文本说明 """

    cid: int
    """ 提示id """
    chara_adv_id: int
    """ 角色adv_id """
    version_id: int
    """ 版本id """
    writer_name: str
    """ 作者名 """
    talk_file_path: str
    """ 口上文件路径 """
    event_file_path: str
    """ 事件文件路径 """
    text: str
    """ 文本内容 """


class Trust_Level:
    """ 信赖等级 """

    cid: int
    """ 信赖等级cid """
    Trust_point: int
    """ 当前等级信赖最大值 """
    judge_add: int
    """ 实行值加成 """


class Vehicle:
    """ 载具表 """

    cid: int
    """ 载具id """
    name: str
    """ 名字 """
    speed: int
    """ 速度 """
    capacity: int
    """ 运载量 """
    acquiring: str
    """ 获得方式 """
    price: int
    """ 价格 """
    special: str
    """ 特殊效果 """
    description: str
    """ 介绍 """


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
    place_tag: str
    """ 工作地点标签 """
    tag: int
    """ 标签(1为灰色显示，2为特殊解锁不直接显示) """
    ability_id: int
    """ 工作需要的能力id """
    need: str
    """ 必要条件 """
    auto_ai: int
    """ 是否使用自动ai行动 """
    auto_ai_move: str
    """ 自动ai移动数据 """
    auto_ai_work: str
    """ 自动ai工作数据 """
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
    behavior_id: str
    """ 触发口上的行为id """
    adv_id: int
    """ 口上限定的剧情npcid """
    premise: str
    """ 前提id """
    context: str
    """ 口上内容 """

class Talk_Common:
    """ 组件配置数据 """

    cid: str
    """ 组件id """
    type_id: str
    """ 组件类型名 """
    adv_id: int
    """ 组件限定的剧情npcid """
    premise: str
    """ 前提id """
    context: str
    """ 组件内容 """



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
    type: int
    """ 行动类型（见Target_Type） """
    remarks: str
    """ 备注 """
