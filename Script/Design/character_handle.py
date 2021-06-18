import random
import math
import numpy
import datetime
from Script.Core import (
    cache_control,
    value_handle,
    constant,
    game_type,
)
from Script.Design import (
    attr_calculation,
    map_handle,
    attr_text,
    character,
)
from Script.Config import game_config, normal_config, character_config


cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """


def init_character_list():
    """
    初始生成所有npc数据
    """
    init_character_tem()
    id_list = iter([i + 1 for i in range(len(cache.npc_tem_data))])
    npc_data_iter = iter(cache.npc_tem_data)
    for now_id, now_npc_data in zip(id_list, npc_data_iter):
        # print("now_id=",now_id,". now_npc_data:",now_npc_data)
        init_character(now_id, now_npc_data)
    index_character_average_value()
    calculate_the_average_value_of_each_attribute_of_each_age_group()


def calculate_the_average_value_of_each_attribute_of_each_age_group():
    """
    计算各年龄段各项属性平均值
    """
    cache.average_bodyfat_by_age = {
        sex: {
            age_tem: cache.total_bodyfat_by_age[sex][age_tem]
            / cache.total_number_of_people_of_all_ages[sex][age_tem]
            for age_tem in cache.total_bodyfat_by_age[sex]
        }
        for sex in cache.total_bodyfat_by_age
    }
    cache.average_height_by_age = {
        sex: {
            age_tem: cache.total_height_by_age[sex][age_tem]
            / cache.total_number_of_people_of_all_ages[sex][age_tem]
            for age_tem in cache.total_height_by_age[sex]
        }
        for sex in cache.total_height_by_age
    }


def index_character_average_value():
    """
    统计各年龄段所有角色各属性总值
    """
    for character_id in cache.character_data:
        character_data = cache.character_data[character_id]
        # age_tem = attr_calculation.judge_age_group(character_data.age)
        # cache.total_height_by_age.setdefault(age_tem, {})
        # cache.total_height_by_age[age_tem].setdefault(character_data.sex, 0)
        # cache.total_height_by_age[age_tem][character_data.sex] += character_data.height.now_height
        # cache.total_number_of_people_of_all_ages.setdefault(age_tem, {})
        # cache.total_number_of_people_of_all_ages[age_tem].setdefault(character_data.sex, 0)
        # cache.total_number_of_people_of_all_ages[age_tem][character_data.sex] += 1
        # cache.total_bodyfat_by_age.setdefault(age_tem, {})
        # cache.total_bodyfat_by_age[age_tem].setdefault(character_data.sex, 0)
        # cache.total_bodyfat_by_age[age_tem][character_data.sex] += character_data.bodyfat


def init_character(character_id: int, character_tem: game_type.NpcTem):
    """
    按id生成角色属性
    Keyword arguments:
    character_id -- 角色id
    character_tem -- 角色生成模板数据
    """
    # print("进入init_character")
    # print("生成阶段，character_id :",character_id)
    # print("character_id=",character_id)
    now_character = game_type.Character()
    now_character.cid = character_id
    now_character.name = character_tem.Name
    now_character.sex = character_tem.Sex
    now_character.profession= character_tem.Profession
    now_character.race= character_tem.Race
    now_character.adv = character_tem.AdvNpc
    now_character.target_character_id = character_id
    now_character.favorability = attr_calculation.get_Favorability_zero()
    now_character.trust = attr_calculation.get_Trust_zero()
    now_character.ability = character_tem.Ability
    now_character.experience = character_tem.Experience
    now_character.talent = character_tem.Talent
    now_character.hit_point_max = character_tem.Hp
    now_character.mana_point_max = character_tem.Mp
    # now_character.age = attr_calculation.get_age(character_id)
    if character_tem.MotherTongue != "":
        now_character.mother_tongue = character_tem.MotherTongue
    if character_tem.Age != "":
        # print("character_tem = ",character_tem)
        # print("character_tem.Age = ",character_tem.Age)
        now_character.age = character_tem.Age
        # now_character.age = attr_calculation.get_age(character_tem.Age)
    if character_tem.Weight != "":
        now_character.weight_tem = character_tem.Weight
    if character_tem.SexExperienceTem != "":
        if character_tem.SexExperienceTem != "Rand":
            now_character.sex_experience_tem = character_tem.SexExperienceTem
        else:
            now_character.sex_experience_tem = get_rand_npc_sex_experience_tem(
                now_character.age, now_character.sex
            )
    if character_tem.BodyFat:
        now_character.bodyfat_tem = character_tem.BodyFat
    else:
        now_character.bodyfat_tem = now_character.weight_tem
    if character_tem.Chest:
        now_character.chest_tem = character_tem.Chest
    cache.character_data[character_id] = now_character
    character.init_attr(character_id)


def init_character_tem():
    """
    初始化角色模板数据
    """
    #init_random_npc_data()
    #npc_data = cache.random_npc_list
    #numpy.random.shuffle(npc_data)
    # print("初始化角色模板数据")
    cache.npc_tem_data = character_config.character_tem_list


random_npc_max = normal_config.config_normal.random_npc_max
random_teacher_proportion = normal_config.config_normal.proportion_teacher
random_student_proportion = normal_config.config_normal.proportion_student
age_weight_data = {
    "teacher": random_teacher_proportion,
    "student": random_student_proportion,
}
age_weight_regin_data = value_handle.get_region_list(age_weight_data)
age_weight_regin_list = list(map(int, age_weight_regin_data.keys()))
age_weight_max = sum([int(age_weight_data[age_weight]) for age_weight in age_weight_data])


def init_random_npc_data() -> list:
    """
    生成所有随机npc的数据模板
    """
    cache.random_npc_list = []
    for i in range(random_npc_max):
        create_random_npc(i)


def create_random_npc(id) -> dict:
    """
    生成随机npc数据模板
    """
    now_age_weight = random.randint(-1, age_weight_max - 1)
    now_age_weight_regin = value_handle.get_next_value_for_list(now_age_weight, age_weight_regin_list)
    age_weight_tem = age_weight_regin_data[now_age_weight_regin]
    random_npc_sex = get_rand_npc_sex()
    random_npc_name = attr_text.get_random_name_for_sex(random_npc_sex)
    random_npc_age_tem = get_rand_npc_age_tem(age_weight_tem)
    fat_tem = get_rand_npc_fat_tem(age_weight_tem)
    body_fat_tem = get_rand_npc_body_fat_tem(age_weight_tem, fat_tem)
    random_npc_new_data = game_type.NpcTem()
    random_npc_new_data.Name = random_npc_name
    random_npc_new_data.Sex = random_npc_sex
    random_npc_new_data.Age = random_npc_age_tem
    random_npc_new_data.Position = ["0"]
    random_npc_new_data.AdvNpc = 0
    random_npc_new_data.Weight = fat_tem
    random_npc_new_data.BodyFat = body_fat_tem
    random_npc_new_data.SexExperienceTem = "Rand"
    if random_npc_sex in {1, 2}:
        random_npc_new_data.Chest = attr_calculation.get_rand_npc_chest_tem()
    else:
        random_npc_new_data.Chest = 0
    cache.random_npc_list.append(random_npc_new_data)


sex_weight_data = game_config.config_random_npc_sex_region
sex_weight_max = sum([sex_weight_data[weight] for weight in sex_weight_data])
sex_weight_regin_data = value_handle.get_region_list(sex_weight_data)
sex_weight_regin_list = list(map(int, sex_weight_regin_data.keys()))


def get_rand_npc_sex() -> int:
    """
    随机获取npc性别
    Return arguments:
    int -- 性别id
    """
    now_weight = random.randint(0, sex_weight_max - 1)
    weight_regin = value_handle.get_next_value_for_list(now_weight, sex_weight_regin_list)
    return sex_weight_regin_data[weight_regin]


def get_rand_npc_fat_tem(age_judge: str) -> int:
    """
    按人群年龄段体重分布比例随机生成重模板
    Keyword arguments:
    age_judge -- 职业(student:学生,teacher:老师)
    Return arguments:
    int -- 体重模板id
    """
    now_fat_weight_data = game_config.config_occupation_bmi_region_data[age_judge]
    now_fat_tem = value_handle.get_random_for_weight(now_fat_weight_data)
    return now_fat_tem


def get_rand_npc_sex_experience_tem(age: int, sex: int) -> int:
    """
    按年龄范围随机获取性经验模板
    Keyword arguments:
    age -- 年龄
    sex -- 性别
    Return arguments:
    int -- 性经验模板id
    """
    age_judge_sex_experience_tem_data = game_config.config_age_judge_sex_experience_tem_data
    if sex == 3:
        sex = 1
    if sex == 2:
        sex = 0
    now_tem_data = age_judge_sex_experience_tem_data[sex]
    age_region_list = [int(i) for i in now_tem_data.keys()]
    age_region = value_handle.get_old_value_for_list(age, age_region_list)
    age_region_data = now_tem_data[age_region]
    return value_handle.get_random_for_weight(age_region_data)


body_fat_weight_data = game_config.config_occupation_bodyfat_region_data


def get_rand_npc_body_fat_tem(age_judge: str, bmi_tem: int) -> int:
    """
    按职业和体重随机生成体脂率模板
    Keyword arguments:
    age_judge -- 职业(student:学生,teacher:老师)
    bmi_tem -- bmi模板
    """
    # now_body_fat_data = game_config.config_occupation_bodyfat_region_data[age_judge][bmi_tem]
    return bmi_tem


def get_rand_npc_age_tem(age_judge: str) -> int:
    """
    按职业断随机生成npc年龄段id
    Keyword arguments:
    age_judge -- 职业(student:学生,teacher:老师)
    Return arguments:
    int -- 年龄段id
    """
    now_age_weight_data = game_config.config_occupation_age_region_data[age_judge]
    now_age_tem = value_handle.get_random_for_weight(now_age_weight_data)
    return now_age_tem


def init_character_dormitory():
    """
    分配角色宿舍
    暂定先全部到博士房间
    """
    dormitory = {
        key: constant.place_data[key] for key in constant.place_data if "Dr_room" in key
    }
    dormitory = {
        x: 0 for j in [k[1] for k in sorted(dormitory.items(), key=lambda x: x[0])] for x in j
    }
    # print("dormitory :",dormitory)
    for character_id in cache.character_data:
        now_room = list(dormitory.keys())[0]
        cache.character_data[character_id].dormitory = now_room


# def init_character_dormitory():
#     """
#     分配角色宿舍
#     小于18岁，男生分配到男生宿舍，女生分配到女生宿舍，按宿舍楼层和角色年龄，从下往上，从小到大分配，其他性别分配到地下室，大于18岁，教师宿舍混居
#     """
#     character_sex_data = {
#         "Man": {
#             character_id: cache.character_data[character_id].age
#             for character_id in cache.character_data
#             if cache.character_data[character_id].age <= 18 and cache.character_data[character_id].sex == 0
#         },
#         "Woman": {
#             character_id: cache.character_data[character_id].age
#             for character_id in cache.character_data
#             if cache.character_data[character_id].age <= 18 and cache.character_data[character_id].sex == 1
#         },
#         "Other": {
#             character_id: cache.character_data[character_id].age
#             for character_id in cache.character_data
#             if cache.character_data[character_id].age <= 18
#             and cache.character_data[character_id].sex not in {0, 1}
#         },
#         "Teacher": {
#             character_id: cache.character_data[character_id].age
#             for character_id in cache.character_data
#             if cache.character_data[character_id].age > 18
#         },
#     }
#     man_max = len(character_sex_data["Man"])
#     woman_max = len(character_sex_data["Woman"])
#     other_max = len(character_sex_data["Other"])
#     teacher_max = len(character_sex_data["Teacher"])
#     character_sex_data["Man"] = [
#         k[0] for k in sorted(character_sex_data["Man"].items(), key=lambda x: x[1])
#     ]
#     character_sex_data["Woman"] = [
#         k[0] for k in sorted(character_sex_data["Woman"].items(), key=lambda x: x[1])
#     ]
#     character_sex_data["Other"] = [
#         k[0] for k in sorted(character_sex_data["Other"].items(), key=lambda x: x[1])
#     ]
#     character_sex_data["Teacher"] = [
#         k[0] for k in sorted(character_sex_data["Teacher"].items(), key=lambda x: x[1])
#     ]
#     teacher_dormitory = {x: 0 for x in sorted(constant.place_data["TeacherDormitory"], key=lambda x: x[0])}
#     male_dormitory = {
#         key: constant.place_data[key] for key in constant.place_data if "MaleDormitory" in key
#     }
#     female_dormitory = {
#         key: constant.place_data[key] for key in constant.place_data if "FemaleDormitory" in key
#     }
#     male_dormitory = {
#         x: 0 for j in [k[1] for k in sorted(male_dormitory.items(), key=lambda x: x[0])] for x in j
#     }
#     female_dormitory = {
#         x: 0 for j in [k[1] for k in sorted(female_dormitory.items(), key=lambda x: x[0])] for x in j
#     }
#     basement = {x: 0 for x in constant.place_data["Basement"]}
#     male_dormitoryMax = len(male_dormitory.keys())
#     female_dormitoryMax = len(female_dormitory.keys())
#     teacher_dormitoryMax = len(teacher_dormitory)
#     basement_max = len(basement)
#     single_room_man = math.ceil(man_max / male_dormitoryMax)
#     single_room_woman = math.ceil(woman_max / female_dormitoryMax)
#     single_room_basement = math.ceil(other_max / basement_max)
#     single_room_teacher = math.ceil(teacher_max / teacher_dormitoryMax)
#     for character_id in character_sex_data["Man"]:
#         now_room = list(male_dormitory.keys())[0]
#         cache.character_data[character_id].dormitory = now_room
#         male_dormitory[now_room] += 1
#         if male_dormitory[now_room] >= single_room_man:
#             del male_dormitory[now_room]
#     for character_id in character_sex_data["Woman"]:
#         now_room = list(female_dormitory.keys())[0]
#         cache.character_data[character_id].dormitory = now_room
#         female_dormitory[now_room] += 1
#         if female_dormitory[now_room] >= single_room_woman:
#             del female_dormitory[now_room]
#     for character_id in character_sex_data["Other"]:
#         now_room = list(basement.keys())[0]
#         cache.character_data[character_id].dormitory = now_room
#         basement[now_room] += 1
#         if basement[now_room] >= single_room_basement:
#             del basement[now_room]
#     for character_id in character_sex_data["Teacher"]:
#         now_room = list(teacher_dormitory.keys())[0]
#         cache.character_data[character_id].dormitory = now_room
#         teacher_dormitory[now_room] += 1
#         if teacher_dormitory[now_room] >= single_room_teacher:
#             del teacher_dormitory[now_room]


def init_character_position():
    """初始化角色位置"""
    for character_id in cache.character_data:
        character_position = cache.character_data[character_id].position
        character_dormitory = cache.character_data[character_id].dormitory
        character_dormitory = map_handle.get_map_system_path_for_str(character_dormitory)
        # print("character_dormitory = ",character_dormitory)
        map_handle.character_move_scene(character_position, character_dormitory, character_id)


def add_favorability(
    character_id: int,
    target_id: int,
    now_add_favorability: int,
    target_change: game_type.TargetChange,
    now_time: datetime.datetime,
):
    """
    增加目标角色对当前角色的好感
    Keyword arguments:
    character_id -- 当前角色id
    target_id -- 目标角色id
    now_add_favorability -- 增加的好感
    target_change -- 角色状态改变对象
    now_time -- 增加好感的时间
    """
    target_data: game_type.Character = cache.character_data[target_id]
    target_data.favorability.setdefault(character_id, 0)
    if target_change is not None:
        target_change.status.setdefault(12, 0)
    old_add_favorability = now_add_favorability
    if 12 in target_data.status:
        disgust = target_data.status[12]
        if disgust:
            if now_add_favorability >= disgust:
                now_add_favorability -= disgust
                target_data.status[12] = 0
                if now_add_favorability:
                    target_data.favorability[character_id] += now_add_favorability
                    if target_change is not None:
                        target_change.favorability += now_add_favorability
                del target_data.status[12]
            else:
                target_data.status[12] -= now_add_favorability
                if target_change is not None:
                    target_change.status[12] -= now_add_favorability
        else:
            target_data.favorability[character_id] += now_add_favorability
            if target_change is not None:
                target_change.favorability += now_add_favorability
    else:
        target_data.favorability[character_id] += now_add_favorability
        if target_change is not None:
            target_change.favorability += now_add_favorability
    target_data.social_contact_last_cut_down_time[character_id] = now_time
    if target_change is not None:
        add_favorability(target_id, character_id, old_add_favorability, None, now_time)
