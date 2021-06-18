import os
from typing import Dict, List, Set
from Script.Config import config_def
from Script.Core import json_handle, get_text



data_path = os.path.join("data", "data.json")
""" 原始json数据文件路径 """
character_path = os.path.join("data", "Character.json")
""" 原始角色数据文件路径 """
config_data = {}
""" 原始json数据 """
character_data = {}
""" 原始角色数据 """
config_bar: Dict[int, config_def.BarConfig] = {}
""" 比例条配置数据 """
config_bar_data: Dict[str, int] = {}
""" 比例条名字对应比例条id """
config_image_data: Dict[int, int] = {}
""" 人物图片对应图片id """
config_behavior_effect: Dict[int, config_def.BehaviorEffect] = {}
""" 行为结算器配置 """
config_behavior_effect_data: Dict[int, Set] = {}
""" 行为所包含的结算器id数据 """
config_book: Dict[int, config_def.Book] = {}
""" 书籍配表数据 """
config_character_state: Dict[int, config_def.CharacterState] = {}
""" 角色状态属性配表数据 """
config_character_state_type: Dict[int, config_def.CharacterStateType] = {}
""" 角色状态类型配表数据 """
config_character_state_type_data: Dict[int, Set] = {}
""" 角色状态类型下状态属性集合 类型id:属性集合 """
config_clothing_evaluate: Dict[int, config_def.ClothingEvaluate] = {}
""" 服装评价配置数据 """
config_clothing_evaluate_list: List[str] = []
""" 服装评价配置列表 """
config_clothing_suit: Dict[int, config_def.ClothingSuit] = {}
""" 衣服套装配置列表 """
config_clothing_suit_data: Dict[int, Dict[int, Set]] = {}
"""
衣服套装搭配数据
套装编号:性别id:服装集合
"""
config_clothing_tem: Dict[int, config_def.ClothingTem] = {}
""" 服装模板配置数据 """
config_clothing_type: Dict[int, config_def.ClothingType] = {}
""" 衣服种类配置数据 """
config_clothing_use_type: Dict[int, config_def.ClothingUseType] = {}
""" 衣服用途配置数据 """
config_course: Dict[int, config_def.Course] = {}
""" 课程配置数据 """
config_font: Dict[int, config_def.FontConfig] = {}
""" 字体配置数据 """
config_font_data: Dict[str, int] = {}
""" 字体名字对应字体id """
config_food: Dict[int, config_def.Food] = {}
""" 食材配置数据 """
config_food_feel: Dict[int, config_def.FoodFeel] = {}
""" 食材效果配置 """
config_food_feel_data: Dict[int, Dict[int, int]] = {}
"""
食材效果配置数据
食材id:效果id:效果
"""
config_food_quality_weight: Dict[int, config_def.FoodQualityWeight] = {}
""" 烹饪技能等级制造食物品质权重配置 """
config_food_quality_weight_data: Dict[int, Dict[int, int]] = {}
"""
烹饪技能等级制造食物品质权重表
技能等级:食物品质:权重
"""
config_hitpoint_tem: Dict[int, config_def.HitPointTem] = {}
""" HP模板对应平均值 """
config_instruct_type: Dict[int, config_def.InstructType] = {}
""" 指令类型配置 """
config_item: Dict[int, config_def.Item] = {}
""" 道具配置数据 """
config_item_tag_data: Dict[str, Set] = {}
"""
道具标签配置数据
标签:道具id集合
"""
config_manapoint_tem: Dict[int, config_def.ManaPointTem] = {}
""" MP模板对应平均值 """
config_moon: Dict[int, config_def.Moon] = {}
""" 月相配置 """
config_moon_data: Dict[int, Set] = {}
""" 月相类型对应配置id集合 """
config_move_menu_type: Dict[int, config_def.MoveMenuType] = {}
""" 移动菜单过滤类型配置 """
config_nature: Dict[int, config_def.Nature] = {}
""" 性格配置数据 """
config_nature_tag: Dict[int, config_def.NatureTag] = {}
""" 性格标签配置数据 """
config_nature_tag_data: Dict[int, Set] = {}
""" 性格标签下性格id配置数据 """
config_organ: Dict[int, config_def.Organ] = {}
""" 器官种类配置 """
config_organ_data: Dict[int, Set] = {}
"""
性别对应器官列表配置数据
性别 0:女 1:男 2: 通用
"""
config_ability_type: Dict[int, config_def.AbilityType] = {}
""" 能力种类配置 """
config_ability_type_data: Dict[int, Set] = {}
"""
类型对应能力列表配置数据
类型 0:感觉,1:扩张,2:刻印,3:基础
"""
config_ability: Dict[int,config_def.Ability] = {}
""" 能力类型表 """
config_experience: Dict[int, config_def.Experience] = {}
""" 经验配置 """
config_juel: Dict[int, config_def.Juel] = {}
""" 宝珠配置 """
config_profession: Dict[int, config_def.Profession] = {}
""" 职业配置 """
config_race: Dict[int, config_def.Race] = {}
""" 种族配置 """
config_talent_type: Dict[int, config_def.TalentType] = {}
""" 素质种类配置 """
config_talent_type_data: Dict[int, Set] = {}
"""
类型对应素质列表配置数据
类型 0:性素质,1:身体素质,2:精神素质,3:技术素质,4:其他素质
"""
config_talent: Dict[int,config_def.Talent] = {}
""" 素质类型表 """
config_recipes: Dict[int, config_def.Recipes] = {}
""" 菜谱配置 """
config_recipes_formula: Dict[int, config_def.RecipesFormula] = {}
""" 菜谱配方配置 """
config_recipes_formula_type: Dict[int, config_def.RecipesFormulaType] = {}
""" 菜谱配方材料类型配置 """
config_recipes_formula_data: Dict[int, Dict[int, Set]] = {}
""" 菜谱配方材料配置数据 """
config_school: Dict[int, config_def.School] = {}
""" 学校配置数据 """
config_school_phase_course: Dict[int, config_def.SchoolPhaseCourse] = {}
""" 各学校各年级科目配置 """
config_school_phase_course_data: Dict[int, Dict[int, Set]] = {}
"""
各学校各年级科目配置数据
学校id:年级id:科目集合
"""
config_school_session: Dict[int, config_def.SchoolSession] = {}
""" 学校上课时间配置 """
config_school_session_data: Dict[int, Dict[int, int]] = {}
"""
学校上课时间配置数据
学校id:课时编号:配表id
"""
config_season: Dict[int, config_def.Season] = {}
""" 季节配置数据 """
config_sex_tem: Dict[int, config_def.SexTem] = {}
""" 性别对应描述和性别器官模板 """
config_sun_time: Dict[int, config_def.SunTime] = {}
""" 太阳时间配置 """
config_random_npc_sex_region: Dict[int, int] = {}
"""
生成随机npc时性别权重
性别:权重
"""
config_social_type: Dict[int, config_def.SocialType] = {}
""" 关系类型配置数据 """
config_solar_period: Dict[int, config_def.SolarPeriod] = {}
""" 节气配置数据 """
config_status: Dict[int, config_def.Status] = {}
""" 角色状态类型配置数据 """
config_talk: Dict[int, config_def.Talk] = {}
""" 口上配置 """
config_talk_data: Dict[int, Set] = {}
""" 角色行为对应口上集合 """
config_talk_premise: Dict[int, config_def.TalkPremise] = {}
""" 口上前提配置 """
config_talk_premise_data: Dict[int, Set] = {}
""" 口上前提配置数据 """
config_target: Dict[int, config_def.Target] = {}
""" 目标配置数据 """
config_target_effect: Dict[int, config_def.TargetEffect] = {}
""" 目标效果配置 """
config_target_effect_data: Dict[int, Set] = {}
""" 目标效果配置数据 """
config_effect_target_data: Dict[int, Set] = {}
""" 能达成效果的目标集合 """
config_target_premise: Dict[int, config_def.TargetPremise] = {}
""" 目标前提配置 """
config_target_premise_data: Dict[int, Set] = {}
""" 目标前提配置数据 """
config_week_day: Dict[int, config_def.WeekDay] = {}
""" 星期描述文本配置数据 """


def load_data_json():
    """载入data.json与character.json内配置数据"""
    global config_data,character_data
    config_data = json_handle.load_json(data_path)
    character_data = json_handle.load_json(character_path)


def translate_data(data: dict):
    """
    按指定字段翻译数据
    Keyword arguments:
    data -- 待翻译的字典数据
    """
    if "gettext" not in data:
        return
    for now_data in data["data"]:
        for key in now_data:
            if data["gettext"][key]:
                now_data[key] = get_text._(now_data[key])


def load_ability_type():
    """载入能力类型具体配置数据（按能力类型分类）"""
    now_data = config_data["AbilityType"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.Ability()
        now_tem.__dict__ = tem_data
        config_ability_type[now_tem.cid] = now_tem


def load_ability_type_data():
    """载入能力类型配置数据"""
    now_data = config_data["Ability"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.Ability()
        now_tem.__dict__ = tem_data
        config_ability[now_tem.cid] = now_tem
        config_ability_type_data.setdefault(now_tem.ability_type, set())
        config_ability_type_data[now_tem.ability_type].add(now_tem.cid)


def load_experience():
    """载入经验数据"""
    now_data = config_data["Experience"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.Experience()
        now_tem.__dict__ = tem_data
        config_experience[now_tem.cid] = now_tem


def load_juel():
    """载入宝珠数据"""
    now_data = config_data["Juel"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.Juel()
        now_tem.__dict__ = tem_data
        config_juel[now_tem.cid] = now_tem

def load_profession():
    """载入职业数据"""
    now_data = config_data["Profession"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.Profession()
        now_tem.__dict__ = tem_data
        config_profession[now_tem.cid] = now_tem

def load_race():
    """载入职业数据"""
    now_data = config_data["Race"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.Race()
        now_tem.__dict__ = tem_data
        config_race[now_tem.cid] = now_tem

def load_talent_type():
    """载入素质类型具体配置数据（按能力类型分类）"""
    now_data = config_data["TalentType"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.Talent()
        now_tem.__dict__ = tem_data
        config_talent_type[now_tem.cid] = now_tem


def load_talent_type_data():
    """载入素质类型配置数据"""
    now_data = config_data["Talent"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.Talent()
        now_tem.__dict__ = tem_data
        config_talent[now_tem.cid] = now_tem
        config_talent_type_data.setdefault(now_tem.Talent_type, set())
        config_talent_type_data[now_tem.Talent_type].add(now_tem.cid)


def load_bar_data():
    """载入比例条配置数据"""
    now_data = config_data["BarConfig"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_bar = config_def.BarConfig()
        # print("now_bar :",now_bar)
        # print("tem_data :",tem_data)
        now_bar.__dict__ = tem_data
        config_bar[now_bar.cid] = now_bar
        config_bar_data[now_bar.name] = now_bar.cid


def load_behavior_effect_data():
    """载入行为结算器配置"""
    now_data = config_data["BehaviorEffect"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.BehaviorEffect()
        now_tem.__dict__ = tem_data
        config_behavior_effect[now_tem.cid] = now_tem
        config_behavior_effect_data.setdefault(now_tem.behavior_id, set())
        config_behavior_effect_data[now_tem.behavior_id].add(now_tem.effect_id)


def load_book_data():
    """载入数据配置数据"""
    now_data = config_data["Book"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.Book()
        now_tem.__dict__ = tem_data
        config_book[now_tem.cid] = now_tem


def load_character_state_data():
    """载入角色状态属性配表数据"""
    now_data = config_data["CharacterState"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.CharacterState()
        now_tem.__dict__ = tem_data
        config_character_state[now_tem.cid] = now_tem
        config_character_state_type_data.setdefault(now_tem.type, set())
        config_character_state_type_data[now_tem.type].add(now_tem.cid)


def load_character_state_type_data():
    """载入角色状态类型配表数据"""
    now_data = config_data["CharacterStateType"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.CharacterStateType()
        now_tem.__dict__ = tem_data
        config_character_state_type[now_tem.cid] = now_tem


def load_clothing_evaluate():
    """载入服装评价配置数据"""
    now_data = config_data["ClothingEvaluate"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.ClothingEvaluate()
        now_tem.__dict__ = tem_data
        config_clothing_evaluate[now_tem.cid] = now_tem
        config_clothing_evaluate_list.append(now_tem.name)


def load_clothing_suit():
    """载入衣服套装配置数据"""
    now_data = config_data["ClothingSuit"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.ClothingSuit()
        now_tem.__dict__ = tem_data
        config_clothing_suit[now_tem.cid] = now_tem
        config_clothing_suit_data.setdefault(now_tem.suit_type, {})
        config_clothing_suit_data[now_tem.suit_type].setdefault(now_tem.sex, set())
        config_clothing_suit_data[now_tem.suit_type][now_tem.sex].add(now_tem.clothing_id)


def load_clothing_tem():
    """载入服装模板配置数据"""
    now_data = config_data["ClothingTem"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.ClothingTem()
        now_tem.__dict__ = tem_data
        config_clothing_tem[now_tem.cid] = now_tem


def load_clothing_type():
    """载入衣服种类配置数据"""
    now_data = config_data["ClothingType"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_type = config_def.ClothingType()
        now_type.__dict__ = tem_data
        config_clothing_type[now_type.cid] = now_type


def load_clothing_use_type():
    """载入衣服用途配置数据"""
    now_data = config_data["ClothingUseType"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_type = config_def.ClothingUseType()
        now_type.__dict__ = tem_data
        config_clothing_use_type[now_type.cid] = now_type


def load_course():
    """载入课程配置数据"""
    now_data = config_data["Course"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.Course()
        now_tem.__dict__ = tem_data
        config_course[now_tem.cid] = now_tem


def load_font_data():
    """载入字体配置数据"""
    now_data = config_data["FontConfig"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_font = config_def.FontConfig()
        now_font.__dict__ = tem_data
        config_font[now_font.cid] = now_font
        config_font_data[now_font.name] = now_font.cid


def load_food_data():
    """载入食材配置数据"""
    now_data = config_data["Food"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.Food()
        now_tem.__dict__ = tem_data
        config_food[now_tem.cid] = now_tem


def load_food_feel_data():
    """载入食材效果配置数据"""
    now_data = config_data["FoodFeel"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.FoodFeel()
        now_tem.__dict__ = tem_data
        config_food_feel[now_tem.cid] = now_tem
        config_food_feel_data.setdefault(now_tem.food_id, {})
        config_food_feel_data[now_tem.food_id][now_tem.feel_id] = now_tem.feel_value * 10


def load_food_quality_weight():
    """载入烹饪技能等级制造食物品质权重配置数据"""
    now_data = config_data["FoodQualityWeight"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.FoodQualityWeight()
        now_tem.__dict__ = tem_data
        config_food_quality_weight[now_tem.cid] = now_tem
        config_food_quality_weight_data.setdefault(now_tem.level, {})
        config_food_quality_weight_data[now_tem.level][now_tem.quality] = now_tem.weight


def load_hitpoint_tem():
    """载入hp模板对应平均值配置数据"""
    now_data = config_data["HitPointTem"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.HitPointTem()
        now_tem.__dict__ = tem_data
        config_hitpoint_tem[now_tem.cid] = now_tem


def load_instruct_type():
    """载入指令类型配置数据"""
    now_data = config_data["InstructType"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.InstructType()
        now_tem.__dict__ = tem_data
        config_instruct_type[now_tem.cid] = now_tem


def load_item():
    """载入道具配置数据"""
    now_data = config_data["Item"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.Item()
        now_tem.__dict__ = tem_data
        config_item[now_tem.cid] = now_tem
        config_item_tag_data.setdefault(now_tem.tag, set())
        config_item_tag_data[now_tem.tag].add(now_tem.cid)


def load_manapoint_tem():
    """载入mp模板对应平均值配置数据"""
    now_data = config_data["ManaPointTem"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.ManaPointTem()
        now_tem.__dict__ = tem_data
        config_manapoint_tem[now_tem.cid] = now_tem


def load_moon():
    """载入月相配置"""
    now_data = config_data["Moon"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.Moon()
        now_tem.__dict__ = tem_data
        config_moon[now_tem.cid] = now_tem
        config_moon_data.setdefault(now_tem.type, set())
        config_moon_data[now_tem.type].add(now_tem.cid)


def load_move_menu_type():
    """载入移动菜单过滤类型配置"""
    now_data = config_data["MoveMenuType"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.MoveMenuType()
        now_tem.__dict__ = tem_data
        config_move_menu_type[now_tem.cid] = now_tem


def load_nature():
    """载入性格配置数据"""
    now_data = config_data["Nature"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.Nature()
        now_tem.__dict__ = tem_data
        config_nature[now_tem.cid] = now_tem
        config_nature_tag_data.setdefault(now_tem.nature_type, set())
        config_nature_tag_data[now_tem.nature_type].add(now_tem.cid)


def load_nature_tag():
    """载入性格标签配置数据"""
    now_data = config_data["NatureTag"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.NatureTag()
        now_tem.__dict__ = tem_data
        config_nature_tag[now_tem.cid] = now_tem


def load_organ_data():
    """载入器官种类配置"""
    now_data = config_data["Organ"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.Organ()
        now_tem.__dict__ = tem_data
        config_organ[now_tem.cid] = now_tem
        config_organ_data.setdefault(now_tem.organ_type, set())
        config_organ_data[now_tem.organ_type].add(now_tem.cid)


def load_recipes():
    """载入菜谱配置数据"""
    now_data = config_data["Recipes"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.Recipes()
        now_tem.__dict__ = tem_data
        config_recipes[now_tem.cid] = now_tem


def load_recipes_formula():
    """载入菜谱配方配置"""
    now_data = config_data["RecipesFormula"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.RecipesFormula()
        now_tem.__dict__ = tem_data
        config_recipes_formula[now_tem.cid] = now_tem
        config_recipes_formula_data.setdefault(now_tem.recipe_id, {})
        config_recipes_formula_data[now_tem.recipe_id].setdefault(now_tem.formula_type, set())
        config_recipes_formula_data[now_tem.recipe_id][now_tem.formula_type].add(now_tem.food_id)


def load_recipes_formula_type():
    """载入菜谱配方材料类型配置数据"""
    now_data = config_data["RecipesFormulaType"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.RecipesFormulaType()
        now_tem.__dict__ = tem_data
        config_recipes_formula_type[now_tem.cid] = now_tem


def load_school():
    """载入学校配置数据"""
    now_data = config_data["School"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.School()
        now_tem.__dict__ = tem_data
        config_school[now_tem.cid] = now_tem


def load_school_phase_course():
    """载入各学校各年级课程科目配置数据"""
    now_data = config_data["SchoolPhaseCourse"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.SchoolPhaseCourse()
        now_tem.__dict__ = tem_data
        config_school_phase_course[now_tem.cid] = now_tem
        config_school_phase_course_data.setdefault(now_tem.school, {})
        config_school_phase_course_data[now_tem.school].setdefault(now_tem.phase, set())
        config_school_phase_course_data[now_tem.school][now_tem.phase].add(now_tem.course)


def load_school_session():
    """载入学校上课时间配置"""
    now_data = config_data["SchoolSession"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.SchoolSession()
        now_tem.__dict__ = tem_data
        config_school_session[now_tem.cid] = now_tem
        config_school_session_data.setdefault(now_tem.school_id, {})
        config_school_session_data[now_tem.school_id][now_tem.session] = now_tem.cid


def load_season():
    """载入季节配置"""
    now_data = config_data["Season"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.Season()
        now_tem.__dict__ = tem_data
        config_season[now_tem.cid] = now_tem


def load_sex_tem():
    """载入性别对应描述和性别器官模板数据"""
    now_data = config_data["SexTem"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.SexTem()
        now_tem.__dict__ = tem_data
        config_sex_tem[now_tem.cid] = now_tem
        config_random_npc_sex_region[now_tem.cid] = now_tem.region


def load_social_type():
    """载入社交关系配置数据"""
    now_data = config_data["SocialType"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.SocialType()
        now_tem.__dict__ = tem_data
        config_social_type[now_tem.cid] = now_tem


def load_solar_period():
    """载入节气配置"""
    now_data = config_data["SolarPeriod"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.SolarPeriod()
        now_tem.__dict__ = tem_data
        config_solar_period[now_tem.cid] = now_tem


def load_status():
    """载入状态类型配置数据"""
    now_data = config_data["Status"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.Status()
        now_tem.__dict__ = tem_data
        config_status[now_tem.cid] = now_tem


def load_sun_time():
    """载入太阳时间配置"""
    now_data = config_data["SunTime"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.SunTime()
        now_tem.__dict__ = tem_data
        config_sun_time[now_tem.cid] = now_tem


def load_talk():
    """载入口上配置"""
    now_data = config_data["Talk"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.Talk()
        now_tem.__dict__ = tem_data
        config_talk[now_tem.cid] = now_tem
        config_talk_data.setdefault(now_tem.behavior_id, set())
        config_talk_data[now_tem.behavior_id].add(now_tem.cid)


def load_talk_premise():
    """载入口上前提配置"""
    now_data = config_data["TalkPremise"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.TalkPremise()
        now_tem.__dict__ = tem_data
        config_talk_premise[now_tem.cid] = now_tem
        config_talk_premise_data.setdefault(now_tem.talk_id, set())
        config_talk_premise_data[now_tem.talk_id].add(now_tem.premise)


def load_target():
    """载入目标配置"""
    now_data = config_data["Target"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.Target()
        now_tem.__dict__ = tem_data
        config_target[now_tem.cid] = now_tem


def load_target_effect():
    """载入目标效果配置"""
    now_data = config_data["TargetEffect"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.TargetEffect()
        now_tem.__dict__ = tem_data
        config_target_effect[now_tem.cid] = now_tem
        config_target_effect_data.setdefault(now_tem.target_id, set())
        config_target_effect_data[now_tem.target_id].add(now_tem.effect_id)
        config_effect_target_data.setdefault(now_tem.effect_id, set())
        config_effect_target_data[now_tem.effect_id].add(now_tem.target_id)


def load_target_premise():
    """载入目标效果配置"""
    now_data = config_data["TargetPremise"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.TargetPremise()
        now_tem.__dict__ = tem_data
        config_target_premise[now_tem.cid] = now_tem
        config_target_premise_data.setdefault(now_tem.target_id, set())
        config_target_premise_data[now_tem.target_id].add(now_tem.premise_id)


def load_week_day():
    """载入星期描述文本配置数据"""
    now_data = config_data["WeekDay"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.WeekDay()
        now_tem.__dict__ = tem_data
        config_week_day[now_tem.cid] = now_tem


def init():
    """初始化游戏配置数据"""
    load_data_json()
    load_ability_type()
    load_ability_type_data()
    load_bar_data()
    load_behavior_effect_data()
    load_book_data()
    load_character_state_data()
    load_character_state_type_data()
    load_clothing_evaluate()
    load_clothing_suit()
    load_clothing_tem()
    load_clothing_type()
    load_clothing_use_type()
    load_course()
    load_experience()
    load_font_data()
    load_food_data()
    load_food_feel_data()
    load_food_quality_weight()
    load_hitpoint_tem()
    load_instruct_type()
    load_item()
    load_juel()
    load_manapoint_tem()
    load_moon()
    load_move_menu_type()
    load_nature()
    load_nature_tag()
    load_organ_data()
    load_profession()
    load_race()
    load_recipes()
    load_recipes_formula()
    load_recipes_formula_type()
    load_school()
    load_school_phase_course()
    load_school_session()
    load_season()
    load_sex_tem()
    load_social_type()
    load_solar_period()
    load_status()
    load_sun_time()
    load_talk()
    load_talk_premise()
    load_talent_type()
    load_talent_type_data()
    load_target()
    load_target_effect()
    load_target_premise()
    load_week_day()
