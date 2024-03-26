import os
from typing import Dict, List, Set
from Script.Config import config_def
from Script.Core import json_handle, get_text, game_type



data_path = os.path.join("data", "data.json")
""" 原始json数据文件路径 """
character_path = os.path.join("data", "Character.json")
""" 原始角色数据文件路径 """
ui_text_path = os.path.join("data", "ui_text.json")
""" 原始ui文本数据文件路径 """
config_data = {}
""" 原始json数据 """
character_data = {}
""" 原始角色数据 """
ui_text_data = {}
""" 原始ui文本数据 """
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
config_second_behavior_effect: Dict[int, config_def.SecondEffect] = {}
""" 二段行为结算器配置 """
config_second_behavior_effect_data: Dict[int, Set] = {}
""" 二段行为所包含的结算器id数据 """
config_book: Dict[int, config_def.Book] = {}
""" 书籍配表数据 """
config_book_type_data: Dict[int, Set] = {}
""" 书籍各类型下的id集合数据 类型id:书籍id集合 """
config_book_type: Dict[int, config_def.BookType] = {}
""" 书籍类型配表数据 """
config_book_type_name_data: Dict[str, Set] = {}
""" 书籍类型配表数据集合 父类型名:子类型名 """
config_character_state: Dict[int, config_def.CharacterState] = {}
""" 角色状态属性配表数据 """
config_character_state_type: Dict[int, config_def.CharacterStateType] = {}
""" 角色状态类型配表数据 """
config_character_state_type_data: Dict[int, Set] = {}
""" 角色状态类型下状态属性集合 类型id:属性集合 """
# config_clothing_suit: Dict[int, config_def.ClothingSuit] = {}
# """ 衣服套装配置列表 """
# config_clothing_suit_data: Dict[int, Dict[int, Set]] = {}
# """
# 衣服套装搭配数据
# 套装编号:性别id:服装集合
# """
config_clothing_tem: Dict[int, config_def.ClothingTem] = {}
""" 服装模板配置数据 """
config_clothing_type: Dict[int, config_def.ClothingType] = {}
""" 衣服种类配置数据 """
config_clothing_type_volume: Dict[int, list] = {}
""" 衣服种类容积配置数据 """
config_cloth_part_normal_flow: Dict[int, list] = {}
""" 衣服部位正常流通配置数据 """
config_cloth_part_full_flow: Dict[int, list] = {}
""" 衣服部位满溢流通配置数据 """
config_cloth_part_extra_flow: Dict[int, list] = {}
""" 衣服部位额外流通配置数据 """
config_clothing_use_type: Dict[int, config_def.ClothingUseType] = {}
""" 衣服用途配置数据 """
config_work_type: Dict[int, config_def.WorkType] = {}
""" 工作种类配置数据 """
config_entertainment: Dict[int, config_def.Entertainment] = {}
""" 娱乐配置数据 """
config_reproduction_period: Dict[int, config_def.Reproduction_period] = {}
""" 生理周期数据 """
config_body_part: Dict[int, config_def.BodyPart] = {}
""" 身体部位配置数据 """
config_body_part_volume: Dict[int, list] = {}
""" 身体部位容积数据 """
config_body_part_normal_flow: Dict[int, list] = {}
""" 身体部位正常流通数据 """
config_body_part_full_flow: Dict[int, list] = {}
""" 身体部位满溢流通数据 """
config_body_part_extra_flow: Dict[int, list] = {}
""" 身体部位额外流通数据 """
config_collection_bonus_data: Dict[int, config_def.Collection_bouns] = {}
""" 收藏品解锁数据 """
config_facility: Dict[int, config_def.Facility] = {}
""" 设施列表数据 """
config_facility_effect: Dict[int, config_def.Facility_effect] = {}
""" 设施效果总数据 """
config_facility_effect_data: Dict[str, Set] = {}
""" 设施效果分类数据 """
config_facility_open: Dict[int, config_def.Facility_open] = {}
""" 设施开放数据 """
config_resouce: Dict[int, config_def.Resouce] = {}
""" 资源数据 """
config_font: Dict[int, config_def.FontConfig] = {}
""" 字体配置数据 """
config_font_data: Dict[str, int] = {}
""" 字体名字对应字体id """
config_instruct_type: Dict[int, config_def.InstructType] = {}
""" 指令类型配置 """
config_item: Dict[int, config_def.Item] = {}
""" 道具配置数据 """
config_item_tag_data: Dict[str, Set] = {}
"""
道具标签配置数据
标签:道具id集合
"""
config_moon: Dict[int, config_def.Moon] = {}
""" 月相配置 """
config_moon_data: Dict[int, Set] = {}
""" 月相类型对应配置id集合 """
config_move_menu_type: Dict[int, config_def.MoveMenuType] = {}
""" 移动菜单过滤类型配置 """
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
config_birthplace: Dict[int, config_def.Birthplace] = {}
""" 出生地配置 """
config_nation: Dict[int, config_def.Nation] = {}
""" 势力配置 """
config_city: Dict[int, config_def.City] = {}
""" 城市配置 """
config_city_of_country: Dict[int, Set] = {}
""" 大地点所属的城市配置 """
config_talent_type: Dict[int, config_def.TalentType] = {}
""" 素质种类配置 """
config_talent_type_data: Dict[int, Set] = {}
"""
类型对应素质列表配置数据
类型 0:性素质,1:身体素质,2:精神素质,3:技术素质,4:其他素质
"""
config_talent: Dict[int,config_def.Talent] = {}
""" 素质类型表 """
# config_ability_up_type: Dict[int, config_def.AbilityUpType] = {}
# """ 根据能力id和等级来判断升级的前提编号 """
config_ability_up_data: Dict[int, Dict[int, config_def.AbilityUp]] = {}
"""
能力升级数据
能力id:当前等级:需求分项:需求内容
"""
config_talent_gain: Dict[int, config_def.TalentGain] = {}
"""
获得素质原数据
条目cid:条目内容
"""
config_talent_gain_data: Dict[int, config_def.TalentGain] = {}
"""
获得素质_素质排列数据
素质id:条目内容
"""
config_instruct_judge_data: Dict[int, config_def.InstructJudge] = {}
""" 每个指令的实行值判定数据 """
config_recipes: Dict[int, config_def.Recipes] = {}
""" 菜谱配置 """
config_season: Dict[int, config_def.Season] = {}
""" 季节配置数据 """
config_sex_tem: Dict[int, config_def.SexTem] = {}
""" 性别对应描述和性别器官模板 """
config_jj_tem: Dict[int, config_def.JJ] = {}
""" 阴茎对应描述 """
config_tip_tem: Dict[int, config_def.Tip] = {}
""" 提示对应描述 """
config_sun_time: Dict[int, config_def.SunTime] = {}
""" 太阳时间配置 """
config_random_npc_sex_region: Dict[int, int] = {}
"""
生成随机npc时性别权重
性别:权重
"""
config_solar_period: Dict[int, config_def.SolarPeriod] = {}
""" 节气配置数据 """
config_status: Dict[int, config_def.Status] = {}
""" 角色状态类型配置数据 """
config_talk: Dict[int, config_def.Talk] = {}
""" 口上配置 """
config_talk_data: Dict[int, Set] = {}
""" 角色行为对应口上集合 """
# config_talk_premise: Dict[int, config_def.TalkPremise] = {}
# """ 口上前提配置 """
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
config_target_premise_data: Dict[int, Set] = {}
""" 目标前提配置数据 """
config_week_day: Dict[int, config_def.WeekDay] = {}
""" 星期描述文本配置数据 """
config_event: Dict[str, game_type.Event] = {}
""" 事件配置数据 """
config_event_status_data: Dict[int, Set] = {}
"""
各个状态下事件列表
状态id:口上id集合
"""
config_event_target: Dict[int, game_type.Target] = {}
""" 目标配置数据 """
config_event_effect_target_data: Dict[int, Set] = {}
""" 能达成效果的目标集合 """
config_sleep_level: Dict[int, config_def.Sleep_Level] = {}
""" 睡眠等级数据 """
config_favorability_level: Dict[int, config_def.Favorability_Level] = {}
""" 好感度等级数据 """
config_trust_level: Dict[int, config_def.Trust_Level] = {}
""" 信赖等级数据 """
config_seasoning: Dict[int, config_def.Seasoning] = {}
""" 调味数据 """
config_prts: Dict[int, config_def.Prts] = {}
""" 教程数据 """
config_food_quality: Dict[int, config_def.Food_Quality] = {}
""" 食物质量数据 """
config_prts_data: Dict[int, Dict[int, config_def.Prts]] = {}
""" 教程数据的具体整理 父id:子id:0问1答:内容 """
config_productformula: Dict[int, config_def.ProductFormula] = {}
""" 产品配方数据 条目cid:条目内容 """
config_productformula_data: Dict[int, Dict[int, int]] = {}
""" 产品配方具体数据 条目cid:[原料id:原料数量] """
config_aromatherapy_recipes: Dict[int, config_def.Aromatherapy_Recipes] = {}
""" 香薰疗愈配方数据 """
config_aromatherapy_recipes_data: Dict[int, Dict[int, int]] = {}
""" 香薰疗愈配方具体数据 配方id:[原料id:原料数量] """
config_first_bonus: Dict[int, config_def.First_Bouns] = {}
""" 初始奖励数据 奖励id:奖励内容 """
config_chara_setting: Dict[int, config_def.CharaSetting] = {}
""" 角色设置数据 设置id:详细内容 """
config_chara_setting_option: Dict[int, Dict[int, str]] = {}
""" 角色设置数据的选项数据 设置id:选项序号:选项内容 """
config_system_setting: Dict[int, config_def.System_Setting] = {}
""" 系统设置数据 设置id:详细内容 """
config_system_setting_option: Dict[int, Dict[int, str]] = {}
""" 系统设置数据的选项数据 设置id:选项序号:选项内容 """
config_assistant_services: Dict[int, config_def.AssistantServices] = {}
""" 助理服务数据 服务id:详细内容 """
config_assistant_services_option: Dict[int, Dict[int, str]] = {}
""" 角色设置数据的选项数据 设置id:选项序号:选项内容 """
config_visitor_stay_attitude: Dict[int, config_def.Visitor_Stay_Attitude] = {}
""" 访客停留态度 """
config_recruitment_strategy: Dict[int, config_def.Recruitment_Strategy] = {}
""" 招募策略 """
config_world_setting: Dict[int, config_def.World_Setting] = {}
""" 世界设定 """
config_hypnosis_type: Dict[int, config_def.Hypnosis_Type] = {}
""" 催眠类型 """
config_hypnosis_talent_of_npc: Dict[int, config_def.Hypnosis_Talent_Of_Npc] = {}
""" 干员获得被催眠素质 """
config_hypnosis_talent_of_pl: Dict[int, config_def.Hypnosis_Talent_Of_Pl] = {}
""" 玩家获得催眠素质 """
config_talent_of_arts: Dict[int, config_def.Talent_Of_Arts] = {}
""" 源石技艺素质 """

def load_data_json():
    """载入data.json、character.json与ui_text.json内配置数据"""
    global config_data,character_data,ui_text_data
    config_data = json_handle.load_json(data_path)
    character_data = json_handle.load_json(character_path)
    ui_text_data = json_handle.load_json(ui_text_path)


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
                # print("now_data :",now_data)
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


# def load_ability_up_type():
#     """根据能力id和等级来判断升级的前提编号"""
#     now_data = config_data["AbilityUpType"]
#     translate_data(now_data)
#     for tem_data in now_data["data"]:
#         now_tem = config_def.AbilityUpType()
#         now_tem.__dict__ = tem_data
#         config_ability_up_type[now_tem.cid] = now_tem


def load_ability_up_data():
    """载入根据编号来判断具体的能力升级的具体数据"""
    now_data = config_data["AbilityUp"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.AbilityUp()
        now_tem.__dict__ = tem_data
        config_ability_up_data.setdefault(now_tem.ability_id, {})
        config_ability_up_data[now_tem.ability_id].setdefault(now_tem.now_level, set())

        # 以&为分割判定是否有多个需求
        if "&" not in now_tem.up_need:
            config_ability_up_data[now_tem.ability_id][now_tem.now_level].add(now_tem.up_need)
        else:
            up_need_list = now_tem.up_need.split('&')
            for up_need in up_need_list:
                config_ability_up_data[now_tem.ability_id][now_tem.now_level].add(up_need)

        # print("tem_data :",tem_data)
        # print("now_tem.cid :",now_tem.cid)
        # print("now_tem.ability_id :",now_tem.ability_id)
        # print("config_ability_up_data[now_tem.ability_id] :",config_ability_up_data[now_tem.ability_id])
        # print("config_ability_up_data[now_tem.ability_id][now_tem.now_level] :",config_ability_up_data[now_tem.ability_id][now_tem.now_level])
        # print()

def load_talent_gain_data():
    """载入获得素质数据"""
    now_data = config_data["TalentGain"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.TalentGain()
        now_tem.__dict__ = tem_data
        config_talent_gain[now_tem.cid] = now_tem
        config_talent_gain_data.setdefault(now_tem.talent_id, {})
        config_talent_gain_data[now_tem.talent_id] = now_tem


def load_instruct_judge_data():
    """每个指令的实行值判定数据"""
    now_data = config_data["InstructJudge"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.InstructJudge()
        now_tem.__dict__ = tem_data
        config_instruct_judge_data[now_tem.cid] = now_tem


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


def load_birthplace():
    """载入出生地数据"""
    now_data = config_data["Birthplace"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.Birthplace()
        now_tem.__dict__ = tem_data
        config_birthplace[now_tem.cid] = now_tem


def load_nation():
    """载入势力数据"""
    now_data = config_data["Nation"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.Nation()
        now_tem.__dict__ = tem_data
        config_nation[now_tem.cid] = now_tem


def load_city():
    """载入城市数据"""
    now_data = config_data["City"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.City()
        now_tem.__dict__ = tem_data
        config_city[now_tem.cid] = now_tem
        config_city_of_country.setdefault(now_tem.country_id, set())
        config_city_of_country[now_tem.country_id].add(now_tem.cid)


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
        # config_behavior_effect_data[now_tem.behavior_id].add(now_tem.effect_id)

        if "|" not in now_tem.effect_id:
            config_behavior_effect_data[now_tem.behavior_id].add(int(now_tem.effect_id))
        else:
            effect_list = now_tem.effect_id.split('|')
            for effect in effect_list:
                config_behavior_effect_data[now_tem.behavior_id].add(int(effect))


def load_second_behavior_effect_data():
    """载入二段行为结算器配置"""
    now_data = config_data["SecondEffect"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.SecondEffect()
        now_tem.__dict__ = tem_data
        config_second_behavior_effect[now_tem.cid] = now_tem
        config_second_behavior_effect_data.setdefault(now_tem.behavior_id, set())
        # config_second_behavior_effect_data[now_tem.behavior_id].add(now_tem.effect_id)

        if "|" not in now_tem.effect_id:
            config_second_behavior_effect_data[now_tem.behavior_id].add(int(now_tem.effect_id))
        else:
            effect_list = now_tem.effect_id.split('|')
            for effect in effect_list:
                config_second_behavior_effect_data[now_tem.behavior_id].add(int(effect))


def load_book_data():
    """载入书籍配置数据"""
    now_data = config_data["Book"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.Book()
        now_tem.__dict__ = tem_data
        config_book[now_tem.cid] = now_tem
        config_book_type_data.setdefault(now_tem.type, set())
        config_book_type_data[now_tem.type].add(now_tem.cid)


def load_book_type():
    """载入书籍种类配置数据"""
    now_data = config_data["BookType"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_type = config_def.BookType()
        now_type.__dict__ = tem_data
        config_book_type[now_type.cid] = now_type
        config_book_type_name_data.setdefault(now_type.father_type_name, set())
        config_book_type_name_data[now_type.father_type_name].add(now_type.son_type_name)


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


# def load_clothing_suit():
#     """载入衣服套装配置数据"""
#     now_data = config_data["ClothingSuit"]
#     translate_data(now_data)
#     for tem_data in now_data["data"]:
#         now_tem = config_def.ClothingSuit()
#         now_tem.__dict__ = tem_data
#         config_clothing_suit[now_tem.cid] = now_tem
#         config_clothing_suit_data.setdefault(now_tem.suit_type, {})
#         config_clothing_suit_data[now_tem.suit_type].setdefault(now_tem.sex, set())
#         config_clothing_suit_data[now_tem.suit_type][now_tem.sex].add(now_tem.clothing_id)


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
        # 容积表
        volume_list = now_type.volume_table.split("-")
        volume_list = [int(volume) for volume in volume_list]
        config_clothing_type_volume[now_type.cid] = volume_list
        # 流通表
        def update_config_flow(flow_str, config_dict, cid):
            if flow_str == "无":
                config_dict[cid] = []
            elif "+" in flow_str:
                flow_list = flow_str.split("+")
                config_dict[cid] = flow_list
            else:
                config_dict[cid] = [flow_str]
        update_config_flow(now_type.normal_flow_table, config_cloth_part_normal_flow, now_type.cid)
        update_config_flow(now_type.full_flow_table, config_cloth_part_full_flow, now_type.cid)
        update_config_flow(now_type.extra_flow_table, config_cloth_part_extra_flow, now_type.cid)
    # print(f"debug config_clothing_type_volume = {config_clothing_type_volume}\n config_cloth_part_normal_flow = {config_cloth_part_normal_flow}\n config_cloth_part_full_flow = {config_cloth_part_full_flow}\n config_cloth_part_extra_flow = {config_cloth_part_extra_flow}")


def load_clothing_use_type():
    """载入衣服用途配置数据"""
    now_data = config_data["ClothingUseType"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_type = config_def.ClothingUseType()
        now_type.__dict__ = tem_data
        config_clothing_use_type[now_type.cid] = now_type


def load_work_type():
    """载入工作种类配置数据"""
    now_data = config_data["WorkType"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_type = config_def.WorkType()
        now_type.__dict__ = tem_data
        config_work_type[now_type.cid] = now_type


def load_entertainment():
    """载入娱乐配置数据"""
    now_data = config_data["Entertainment"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_type = config_def.Entertainment()
        now_type.__dict__ = tem_data
        config_entertainment[now_type.cid] = now_type


def load_reproduction_period():
    """载入生理周期数据"""
    now_data = config_data["Reproduction_period"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_type = config_def.Reproduction_period()
        now_type.__dict__ = tem_data
        config_reproduction_period[now_type.cid] = now_type


def load_body_part():
    """载入身体部位配置数据"""
    now_data = config_data["BodyPart"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_type = config_def.BodyPart()
        now_type.__dict__ = tem_data
        config_body_part[now_type.cid] = now_type
        # 容积表
        volume_list = now_type.volume_table.split("-")
        volume_list = [int(volume) for volume in volume_list]
        config_body_part_volume[now_type.cid] = volume_list
        # 流通表
        def update_config_flow(flow_str, config_dict, cid):
            if flow_str == "无":
                config_dict[cid] = []
            elif "+" in flow_str:
                flow_list = flow_str.split("+")
                config_dict[cid] = flow_list
            else:
                config_dict[cid] = [flow_str]
        update_config_flow(now_type.normal_flow_table, config_body_part_normal_flow, now_type.cid)
        update_config_flow(now_type.full_flow_table, config_body_part_full_flow, now_type.cid)
        update_config_flow(now_type.extra_flow_table, config_body_part_extra_flow, now_type.cid)


def load_collection_bonus_data():
    """载入收藏品奖励数据"""
    now_data = config_data["Collection_bouns"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_type = config_def.Collection_bouns()
        now_type.__dict__ = tem_data
        config_collection_bonus_data[now_type.cid] = now_type


def load_facility():
    """载入设施列表数据"""
    now_data = config_data["Facility"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.Facility()
        now_tem.__dict__ = tem_data
        config_facility[now_tem.cid] = now_tem


def load_facility_effect():
    """载入设施效果数据"""
    now_data = config_data["Facility_effect"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.Facility_effect()
        now_tem.__dict__ = tem_data
        config_facility_effect[now_tem.cid] = now_tem
        config_facility_effect_data.setdefault(now_tem.name, list())
        # 补个0，让序号=等级
        if config_facility_effect_data[now_tem.name] == []:
            config_facility_effect_data[now_tem.name].append(0)

        config_facility_effect_data[now_tem.name].append(now_tem.cid)
    # print(f"debug config_facility_effect_data = {config_facility_effect_data}")


def load_facility_open():
    """载入设施开放数据"""
    now_data = config_data["Facility_open"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.Facility_open()
        now_tem.__dict__ = tem_data
        config_facility_open[now_tem.cid] = now_tem


def load_resouce():
    """载入资源数据"""
    now_data = config_data["Resouce"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.Resouce()
        now_tem.__dict__ = tem_data
        config_resouce[now_tem.cid] = now_tem


def load_font_data():
    """载入字体配置数据"""
    now_data = config_data["FontConfig"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_font = config_def.FontConfig()
        now_font.__dict__ = tem_data
        config_font[now_font.cid] = now_font
        config_font_data[now_font.name] = now_font.cid


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


def load_jj_tem():
    """载入阴茎模板数据"""
    now_data = config_data["JJ"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.JJ()
        now_tem.__dict__ = tem_data
        config_jj_tem[now_tem.cid] = now_tem


def load_tip_tem():
    """载入提示数据"""
    now_data = config_data["Tip"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.Tip()
        now_tem.__dict__ = tem_data
        config_tip_tem[now_tem.cid] = now_tem


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
        # print(f"debug now_tem.context = {now_tem.context}")
        config_talk_data.setdefault(now_tem.behavior_id, set())
        config_talk_data[now_tem.behavior_id].add(now_tem.cid)

        config_talk_premise_data.setdefault(now_tem.cid, set())
        # print(f"debug now_tem.context = {now_tem.context}")
        if "&" not in now_tem.premise:
            config_talk_premise_data[now_tem.cid].add(now_tem.premise)
        else:
            premise_list = now_tem.premise.split('&')
            for premise in premise_list:
                config_talk_premise_data[now_tem.cid].add(premise)


# def load_talk_premise():
#     """载入口上前提配置"""
#     now_data = config_data["TalkPremise"]
#     translate_data(now_data)
#     for tem_data in now_data["data"]:
#         now_tem = config_def.TalkPremise()
#         now_tem.__dict__ = tem_data
#         config_talk_premise[now_tem.cid] = now_tem
#         config_talk_premise_data.setdefault(now_tem.talk_id, set())
#         config_talk_premise_data[now_tem.talk_id].add(now_tem.premise)


def load_target():
    """载入目标配置"""
    now_data = config_data["Target"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.Target()
        now_tem.__dict__ = tem_data
        config_target[now_tem.cid] = now_tem

        config_target_premise_data.setdefault(now_tem.cid, set())
        if len(now_tem.premise_id):
            if "|" not in now_tem.premise_id:
                config_target_premise_data[now_tem.cid].add(now_tem.premise_id)
            else:
                premise_list = now_tem.premise_id.split('|')
                for premise_id in premise_list:
                    config_target_premise_data[now_tem.cid].add(premise_id)


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


def load_week_day():
    """载入星期描述文本配置数据"""
    now_data = config_data["WeekDay"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.WeekDay()
        now_tem.__dict__ = tem_data
        config_week_day[now_tem.cid] = now_tem


def load_event():
    """载入事件配置"""
    now_data = config_data["Event"]
    # translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = game_type.Event()
        now_tem.__dict__ = tem_data
        config_event[now_tem.uid] = now_tem
        config_event_status_data.setdefault(int(now_tem.status_id), set())
        config_event_status_data[int(now_tem.status_id)].add(now_tem.uid)


def load_event_target():
    """载入事件目标配置"""
    now_data = config_data["Event_Target"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = game_type.Target()
        now_tem.__dict__ = tem_data
        config_event_target[now_tem.uid] = now_tem
        for effect in now_tem.effect:
            config_event_effect_target_data.setdefault(effect, set())
            config_event_effect_target_data[effect].add(now_tem.uid)


def load_sleep_level():
    """载入睡眠等级数据"""
    now_data = config_data["Sleep_Level"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.Sleep_Level()
        now_tem.__dict__ = tem_data
        config_sleep_level[now_tem.cid] = now_tem


def load_food_quality():
    """载入食物质量数据"""
    now_data = config_data["Food_Quality"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.Food_Quality()
        now_tem.__dict__ = tem_data
        config_food_quality[now_tem.cid] = now_tem


def load_favorability_level():
    """载入好感度等级数据"""
    now_data = config_data["Favorability_Level"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.Favorability_Level()
        now_tem.__dict__ = tem_data
        config_favorability_level[now_tem.cid] = now_tem


def load_trust_level():
    """载入信赖等级数据"""
    now_data = config_data["Trust_Level"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.Trust_Level()
        now_tem.__dict__ = tem_data
        config_trust_level[now_tem.cid] = now_tem


def load_seasoning():
    """载入调味数据"""
    now_data = config_data["Seasoning"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.Seasoning()
        now_tem.__dict__ = tem_data
        config_seasoning[now_tem.cid] = now_tem


def load_first_bonus():
    """载入初始奖励数据"""
    now_data = config_data["First_Bouns"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.First_Bouns()
        now_tem.__dict__ = tem_data
        config_first_bonus[now_tem.cid] = now_tem


def load_visitor_stay_attitude():
    """载入访客停留态度数据"""
    now_data = config_data["Visitor_Stay_Attitude"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.Visitor_Stay_Attitude()
        now_tem.__dict__ = tem_data
        config_visitor_stay_attitude[now_tem.cid] = now_tem


def load_recruitment_strategy():
    """载入招募策略数据"""
    now_data = config_data["Recruitment_Strategy"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.Recruitment_Strategy()
        now_tem.__dict__ = tem_data
        config_recruitment_strategy[now_tem.cid] = now_tem


def load_world_setting():
    """载入世界设定数据"""
    now_data = config_data["World_Setting"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.World_Setting()
        now_tem.__dict__ = tem_data
        config_world_setting[now_tem.cid] = now_tem


def load_hypnosis_type():
    """载入催眠类型"""
    now_data = config_data["Hypnosis_Type"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.Hypnosis_Type()
        now_tem.__dict__ = tem_data
        config_hypnosis_type[now_tem.cid] = now_tem


def load_hypnosis_talent_of_npc():
    """载入催眠npc素质"""
    now_data = config_data["Hypnosis_Talent_Of_Npc"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.Hypnosis_Talent_Of_Npc()
        now_tem.__dict__ = tem_data
        config_hypnosis_talent_of_npc[now_tem.cid] = now_tem


def load_hypnosis_talent_of_player():
    """载入催眠玩家素质"""
    now_data = config_data["Hypnosis_Talent_Of_Pl"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.Hypnosis_Talent_Of_Pl()
        now_tem.__dict__ = tem_data
        config_hypnosis_talent_of_pl[now_tem.cid] = now_tem


def load_talent_of_arts():
    """载入源石技艺素质"""
    now_data = config_data["Talent_Of_Arts"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.Talent_Of_Arts()
        now_tem.__dict__ = tem_data
        config_talent_of_arts[now_tem.cid] = now_tem


def load_product_formula():
    """载入产品配方"""
    now_data = config_data["ProductFormula"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.ProductFormula()
        now_tem.__dict__ = tem_data
        config_productformula[now_tem.cid] = now_tem

        formula_text = now_tem.formula
        # 以&为分割判定是否有多个需求
        if "&" not in formula_text:
            need_list = []
            need_list.append(formula_text)
        else:
            need_list = formula_text.split('&')
        for need_text in need_list:
            need_type = int(need_text.split('|')[0])
            need_value = int(need_text.split('|')[1])
            config_productformula_data.setdefault(now_tem.cid, {})
            config_productformula_data[now_tem.cid][need_type] = need_value


def load_aromatherapy_recipes():
    """载入香薰疗愈"""
    now_data = config_data["Aromatherapy_Recipes"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.Aromatherapy_Recipes()
        now_tem.__dict__ = tem_data
        config_aromatherapy_recipes[now_tem.cid] = now_tem

        formula_text = now_tem.formula
        # 以&为分割判定是否有多个需求
        if "&" not in formula_text:
            need_list = []
            need_list.append(formula_text)
        else:
            need_list = formula_text.split('&')
        for need_text in need_list:
            need_type = int(need_text.split('|')[0])
            need_value = int(need_text.split('|')[1])
            config_aromatherapy_recipes_data.setdefault(now_tem.cid, {})
            config_aromatherapy_recipes_data[now_tem.cid][need_type] = need_value


def load_chara_setting():
    """载入角色设置"""
    now_data = config_data["CharaSetting"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.CharaSetting()
        now_tem.__dict__ = tem_data
        config_chara_setting[now_tem.cid] = now_tem

        option_text = now_tem.option
        # 以|为分割判定是否有多个选项
        if "|" not in option_text:
            config_chara_setting_option[now_tem.cid] = []
            config_chara_setting_option[now_tem.cid].append(option_text)
        else:
            config_chara_setting_option[now_tem.cid] = option_text.split('|')


def load_system_setting():
    """载入系统设置"""
    now_data = config_data["System_Setting"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.System_Setting()
        now_tem.__dict__ = tem_data
        config_system_setting[now_tem.cid] = now_tem

        option_text = now_tem.option
        # 以|为分割判定是否有多个选项
        if "|" not in option_text:
            config_system_setting_option[now_tem.cid] = []
            config_system_setting_option[now_tem.cid].append(option_text)
        else:
            config_system_setting_option[now_tem.cid] = option_text.split('|')


def load_assistant_services():
    """载入助理服务"""
    now_data = config_data["AssistantServices"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.AssistantServices()
        now_tem.__dict__ = tem_data
        config_assistant_services[now_tem.cid] = now_tem

        option_text = now_tem.option
        require_text = now_tem.require
        config_assistant_services_option[now_tem.cid] = {}
        # 以|为分割判定是否有多个选项
        if "|" not in option_text:
            config_assistant_services_option[now_tem.cid][0] = [option_text]
        else:
            config_assistant_services_option[now_tem.cid][0] = option_text.split('|')
        # 以#为分割判定是否有多个需求
        if "#" not in require_text:
            config_assistant_services_option[now_tem.cid][1] = [require_text]
        else:
            config_assistant_services_option[now_tem.cid][1] = require_text.split('#')


def load_prts():
    """载入教程数据"""
    now_data = config_data["Prts"]
    translate_data(now_data)
    for tem_data in now_data["data"]:
        now_tem = config_def.Prts()
        now_tem.__dict__ = tem_data
        config_prts[now_tem.cid] = now_tem

        config_prts_data.setdefault(now_tem.fater_type, {})
        config_prts_data[now_tem.fater_type].setdefault(now_tem.son_type, {})
        if now_tem.qa == "q":
            config_prts_data[now_tem.fater_type][now_tem.son_type][0] = now_tem
        else:
            config_prts_data[now_tem.fater_type][now_tem.son_type][1] = now_tem

    """
    draw_text_list = []
    for son_type in config_prts_data[0]:
        Q_data = config_prts_data[0][son_type][0]
        draw_text_list.append(Q_data.text)
    for son_type in config_prts_data[0]:
        A_data = config_prts_data[0][son_type][1]
        draw_text_list.append(A_data.text)
    print(draw_text_list)
    """


def init():
    """初始化游戏配置数据"""
    load_data_json()
    load_ability_type()
    load_ability_type_data()
    # load_ability_up_type()
    load_ability_up_data()
    load_bar_data()
    load_behavior_effect_data()
    load_second_behavior_effect_data()
    load_book_data()
    load_book_type()
    load_character_state_data()
    load_character_state_type_data()
    # load_clothing_suit()
    load_clothing_tem()
    load_clothing_type()
    load_clothing_use_type()
    load_work_type()
    load_entertainment()
    load_reproduction_period()
    load_body_part()
    load_collection_bonus_data()
    load_facility()
    load_facility_effect()
    load_facility_open()
    load_resouce()
    load_experience()
    load_font_data()
    load_instruct_type()
    load_instruct_judge_data()
    load_item()
    load_juel()
    load_moon()
    load_move_menu_type()
    load_organ_data()
    load_profession()
    load_race()
    load_birthplace()
    load_nation()
    load_city()
    load_recipes()
    load_season()
    load_sex_tem()
    load_jj_tem()
    load_tip_tem()
    load_solar_period()
    load_status()
    load_sun_time()
    load_talk()
    load_talent_type()
    load_talent_type_data()
    load_talent_gain_data()
    load_target()
    load_target_effect()
    load_week_day()
    load_event()
    # load_event_target()
    load_sleep_level()
    load_food_quality()
    load_favorability_level()
    load_trust_level()
    load_seasoning()
    load_product_formula()
    load_aromatherapy_recipes()
    load_prts()
    load_first_bonus()
    load_chara_setting()
    load_system_setting()
    load_assistant_services()
    load_visitor_stay_attitude()
    load_recruitment_strategy()
    load_world_setting()
    load_hypnosis_type()
    load_hypnosis_talent_of_npc()
    load_hypnosis_talent_of_player()
    load_talent_of_arts()
