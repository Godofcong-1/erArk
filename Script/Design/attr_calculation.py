import random
import datetime
from Script.Core import (
    cache_control,
    value_handle,
    game_type,
)
from Script.Design import game_time
from Script.Config import game_config

cache: game_type.Cache = cache_control.cache
""" 游戏内缓存数据 """


def get_age_tem_list() -> list:
    """
    获取年龄模板
    """
    return list(game_config.config_age_tem.keys())


def get_age(character_id: int) -> int:
    """
    按人物id获得对应年龄数据
    Keyword arguments:
    character_id -- 年龄模板id
    """
    print("game_config.config_age_tem :",game_config.config_age_tem)
    print("character_id :",character_id)
    print("game_config.config_age_tem[character_id] :",game_config.config_age_tem[character_id])
    tem_data = game_config.config_age_tem[character_id].Age
    return tem_data

def get_Favorability() -> dict:
    """
    直接将初始好感归为{0:0}
    """
    return {0:0}

# def get_age(tem_name: int) -> int:
#     """
#     按年龄模板id随机生成年龄数据
#     Keyword arguments:
#     tem_name -- 年龄模板id
#     """
#     tem_data = game_config.config_age_tem[tem_name]
#     max_age = tem_data.max_age
#     mini_age = tem_data.min_age
#     return random.randint(mini_age, max_age)


def get_end_age(sex: int) -> int:
    """
    按照性别模板随机生成预期寿命
    Keyword arguments:
    sex -- 性别
    """
    tem_value = game_config.config_end_age_tem_sex_data[sex]
    return value_handle.get_gauss_rand(int(tem_value * 0.5), int(tem_value * 1.5))


def get_height(tem_name: int, age: int) -> game_type.Height:
    """
    按模板和年龄计算身高
    Keyword arguments:
    tem_name -- 人物生成模板(性别id)
    age -- 人物年龄
    """
    tem_data = game_config.config_height_tem_sex_data[tem_name]
    initial_height = value_handle.get_gauss_rand(tem_data.min_value, tem_data.max_value)
    if tem_name in {0, 3}:
        expect_age = random.randint(18, 22)
        expect_height = initial_height / 0.2949
    else:
        expect_age = random.randint(13, 17)
        expect_height = initial_height / 0.3109
    development_age = random.randint(4, 6)
    growth_height_data = get_growth_height(age, expect_height, development_age, expect_age)
    growth_height = growth_height_data["GrowthHeight"]
    now_height = growth_height_data["NowHeight"]
    if now_height >= expect_height:
        now_height = expect_height
    height_data = game_type.Height()
    height_data.now_height = now_height
    height_data.growth_height = growth_height
    height_data.expect_age = expect_age
    height_data.development_age = development_age
    height_data.expect_height = expect_height
    return height_data


def get_chest(chest_tem: int, birthday: datetime.datetime) -> game_type.Chest:
    """
    按罩杯模板生成人物最终胸围差，并按人物年龄计算当前胸围差
    Keyword arguments:
    chest_tem -- 罩杯模板
    birthday -- 出生日期
    Return arguments:
    game_type.Chest -- 胸围数据
    """
    target_chest = get_rand_npc_chest(chest_tem)
    over_age = int(value_handle.get_gauss_rand(14, 18))
    over_year = birthday.year + over_age
    end_date = game_time.get_rand_day_for_year(over_year)
    now_date = cache.game_time
    end_day = game_time.count_day_for_datetime(birthday, end_date)
    now_day = game_time.count_day_for_datetime(birthday, now_date)
    sub_chest = target_chest / end_day
    now_chest = sub_chest * now_day
    if now_chest > target_chest:
        now_chest = target_chest
    chest = game_type.Chest()
    chest.now_chest = now_chest
    chest.sub_chest = sub_chest
    chest.target_chest = target_chest
    return chest


chest_tem_weight_data = {k: game_config.config_chest[k].weight for k in game_config.config_chest}


def get_rand_npc_chest_tem() -> int:
    """
    随机获取npc罩杯模板
    """
    return value_handle.get_random_for_weight(chest_tem_weight_data)


def get_rand_npc_chest(chest_tem: int) -> int:
    """
    随机获取模板对应罩杯
    Keyword arguments:
    chest_tem -- 罩杯模板
    """
    chest_scope = game_config.config_chest[chest_tem]
    return value_handle.get_gauss_rand(chest_scope.min_value, chest_scope.max_value)


def get_rand_npc_birthday(age: int):
    """
    随机生成npc生日
    Keyword arguments:
    age -- 年龄
    """
    now_year = cache.game_time.year
    now_month = cache.game_time.month
    now_day = cache.game_time.day
    birth_year = now_year - int(age)
    birthday = game_time.get_rand_day_for_year(birth_year)
    if now_month < birthday.month or (now_month == birthday.month and now_day < birthday.day):
        birthday = game_time.get_sub_date(year=-1, old_date=birthday)
    return birthday


def get_growth_height(now_age: int, expect_height: float, development_age: int, expect_age: int) -> dict:
    """
    计算每日身高增长量
    Keyword arguments:
    now_age -- 现在的年龄
    expect_height -- 预期最终身高
    development_age -- 结束发育期时的年龄
    except_age -- 结束身高增长时的年龄
    """
    if now_age > development_age:
        now_height = expect_height / 2
        judge_age = expect_age - development_age
        growth_height = now_height / (judge_age * 365)
        now_height = now_height + (now_age - development_age) * 365 * growth_height
    else:
        judge_height = expect_height / 2
        growth_height = judge_height / (now_age * 365)
        now_height = now_age * 365 * growth_height
    return {"GrowthHeight": growth_height, "NowHeight": now_height}


def get_bmi(tem_name: int) -> float:
    """
    按体重比例模板生成BMI
    Keyword arguments:
    tem_name -- 体重比例模板id
    Return arguments:
    int -- bmi值
    """
    tem_data = game_config.config_weight_tem[tem_name]
    return value_handle.get_gauss_rand(tem_data.min_value, tem_data.max_value)


def get_body_fat(sex: int, tem_name: int) -> float:
    """
    按性别和体脂率模板生成体脂率
    Keyword arguments:
    sex -- 性别
    tem_name -- 体脂率模板id
    Return arguments:
    float -- 体脂率
    """
    sex_tem = sex in (0, 3)
    tem_data_id = game_config.config_body_fat_tem_data[sex_tem][tem_name]
    tem_data = game_config.config_body_fat_tem[tem_data_id]
    return value_handle.get_gauss_rand(tem_data.min_value, tem_data.max_value)


def get_weight(bmi: float, height: float) -> float:
    """
    按bmi和身高计算体重
    Keyword arguments:
    bmi -- 身高体重比(BMI)
    height -- 身高
    """
    height = height / 100
    return bmi * height * height


def get_measurements(
    tem_name: int,
    height: float,
    weight: float,
    bodyfat: float,
    weight_tem: int,
) -> dict:
    """
    计算角色三围
    Keyword arguments:
    tem_name -- 性别模板
    height -- 身高
    weight -- 体重
    bodyfat -- 体脂率
    weight_tem -- 体重比例模板
    """
    fix = 0
    if not weight_tem:
        fix = -5
    elif weight_tem > 1:
        fix = 5 * (weight_tem - 1)
    if tem_name in {0, 3}:
        bust = value_handle.get_gauss_rand(0.4676, 0.5676) * height + fix
        waist = value_handle.get_gauss_rand(0.3779, 0.4779) * height + fix
        hip = value_handle.get_gauss_rand(0.4707, 0.5707) * height + fix
    else:
        bust = value_handle.get_gauss_rand(0.4735, 0.5735) * height + fix
        waist = value_handle.get_gauss_rand(0.3634, 0.4634) * height + fix
        hip = value_handle.get_gauss_rand(0.5278, 0.6278) * height + fix
    measurements = game_type.Measurements()
    measurements.bust = bust
    measurements.waist = waist
    measurements.hip = hip
    return measurements


def get_max_hit_point(tem_id: int) -> int:
    """
    获取最大hp值
    Keyword arguments:
    tem_id -- hp模板id
    Return arguments:
    int -- 最大hp值
    """
    tem_data = game_config.config_hitpoint_tem[tem_id]
    max_hit_point = tem_data.max_value
    add_value = value_handle.get_gauss_rand(0, 500)
    impairment = value_handle.get_gauss_rand(0, 500)
    return max_hit_point + add_value - impairment


def get_max_mana_point(tem_id: int) -> int:
    """
    获取最大mp值
    Keyword arguments:
    tem_id -- mp模板
    Return arguments:
    int -- 最大mp值
    """
    tem_data = game_config.config_manapoint_tem[tem_id]
    max_mana_point = tem_data.max_value
    add_value = value_handle.get_gauss_rand(0, 500)
    impairment = value_handle.get_gauss_rand(0, 500)
    return max_mana_point + add_value - impairment


def get_init_learn_abllity(age: int, end_age: int):
    """
    按年龄和生成学习能力
    Keyword arguments:
    age -- 年龄
    end_age -- 预期寿命
    """
    stop_age = int(end_age / 2)
    forget_age = int(end_age * 0.9)
    if age <= stop_age:
        return age / stop_age
    elif age > stop_age and age < end_age:
        return 1 - 1 / (forget_age - stop_age) * (forget_age - age)
    else:
        return 0 - (age - forget_age) / (end_age - forget_age)


def get_sex_experience(tem_name: int, sex: int) -> dict:
    """
    按模板生成角色初始性经验
    Keyword arguments:
    tem_name -- 性经验丰富程度模板
    sex -- 性别id
    Return arguments:
    dict -- 性经验数据
    """
    sex_tem = sex in {0, 3}
    sex_experience_data = {}
    for organ in game_config.config_organ_data[sex_tem] | game_config.config_organ_data[2]:
        sex_experience_tem_id = game_config.config_sex_experience_data[tem_name][organ]
        organ_sex_experience_tem_id = game_config.config_sex_experience_tem_data[organ][
            sex_experience_tem_id
        ]
        organ_sex_experience_tem = game_config.config_sex_experience_tem[organ_sex_experience_tem_id]
        sex_experience_data[organ] = random.uniform(
            organ_sex_experience_tem.min_exp, organ_sex_experience_tem.max_exp
        )
    return sex_experience_data


def get_experience_level_weight(experience: int) -> int:
    """
    按经验计算技能等级权重
    Keyword arguments:
    experience -- 经验数值
    Return arguments:
    int -- 权重
    """
    grade = 0
    if experience < 100:
        grade = 0
    elif experience < 500:
        grade = 1
    elif experience < 1000:
        grade = 2
    elif experience < 2000:
        grade = 3
    elif experience < 3000:
        grade = 4
    elif experience < 5000:
        grade = 5
    elif experience < 10000:
        grade = 6
    elif experience < 20000:
        grade = 7
    elif experience >= 20000:
        grade = 8
    return grade


def judge_grade(experience: int) -> str:
    """
    按经验数值评定等级
    Keyword arguments:
    experience -- 经验数值
    Return arguments:
    str -- 评级
    """
    grade = ""
    if experience < 100:
        grade = "G"
    elif experience < 500:
        grade = "F"
    elif experience < 1000:
        grade = "E"
    elif experience < 2000:
        grade = "D"
    elif experience < 3000:
        grade = "C"
    elif experience < 5000:
        grade = "B"
    elif experience < 10000:
        grade = "A"
    elif experience < 20000:
        grade = "S"
    elif experience >= 20000:
        grade = "EX"
    return grade


def judge_age_group(age: int) -> int:
    """
    判断所属年龄段
    Keyword arguments:
    age -- 年龄
    Return arguments:
    int -- 年龄段
    """
    for age_tem_id in game_config.config_age_tem:
        age_tem = game_config.config_age_tem[age_tem_id]
        if age >= age_tem.min_age and age < age_tem.max_age:
            return age_tem_id
    return 0


def judge_chest_group(chest: float) -> int:
    """
    判断胸围差所属罩杯
    Keyword arguments:
    chest -- 胸围差
    Return arguments:
    int -- 罩杯id
    """
    for chest_tem_id in game_config.config_chest:
        chest_tem = game_config.config_chest[chest_tem_id]
        if chest >= chest_tem.min_value and chest < chest_tem.max_value:
            return chest_tem_id
    return 0

