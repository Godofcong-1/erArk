import random
from Script.Core import (
    cache_control,
    game_type,
)
from Script.Config import game_config
from Script.Design import handle_premise

cache: game_type.Cache = cache_control.cache
""" 游戏内缓存数据 """


def get_base_zero() -> dict:
    """
    基地情况结构体，设为空
    """

    base_data = game_type.Base_resouce()

    # 遍历全设施清单
    for all_cid in game_config.config_facility:
        # 全设施等级设为1
        base_data.facility_level[all_cid] = 1

    # 遍历全设施开放
    for all_cid in game_config.config_facility_open:
        # 全设施初始关闭
        base_data.facility_open[all_cid] = False

    # 遍历全资源清单
    for all_cid in game_config.config_resouce:
        # 全资源数量设为0
        base_data.materials_resouce[all_cid] = 0

    # 遍历全部书籍
    for book_id in game_config.config_book:
        # 全书籍设为未借出
        base_data.book_borrow_dict[book_id] = -1

    # 派对设为空
    for i in range(7):
        base_data.party_day_of_week[i] = 0

    return base_data

def get_base_updata():
    """
    遍历基地情况结构体，根据设施等级更新全部数值
    """

    cache.base_resouce.power_use = 0

    # 遍历全设施清单
    for all_cid in game_config.config_facility:
        # 全设施等级设为对应值
        level = cache.base_resouce.facility_level[all_cid]

        # 累加全设施的用电量
        facility_name = game_config.config_facility[all_cid].name
        facility_cid = game_config.config_facility_effect_data[facility_name][level]
        cache.base_resouce.power_use += game_config.config_facility_effect[facility_cid].power_use

        # 如果满足设施开放的前提条件，则开放该设施
        for open_cid in game_config.config_facility_open:
            if game_config.config_facility_open[open_cid].zone_cid == facility_cid:
                print(f"debug zone_cid = {game_config.config_facility_open[open_cid].zone_cid}")
                print(f"debug facility_cid = {facility_cid}")
                cache.base_resouce.facility_open[open_cid] = True

    # print(f"debug power_use = {base_data.power_use}")

        # 初始化供电量
        if facility_name == "动力区":
            cache.base_resouce.power_max = game_config.config_facility_effect[facility_cid].effect
        # 初始化仓库容量
        elif facility_name == "仓储区":
            cache.base_resouce.warehouse_capacity = game_config.config_facility_effect[facility_cid].effect
        # 初始化干员人数上限
        elif facility_name == "宿舍区":
            cache.base_resouce.people_max = game_config.config_facility_effect[facility_cid].effect
        # 初始化生活娱乐区设施数量上限
        elif facility_name == "生活娱乐区":
            cache.base_resouce.life_zone_max = game_config.config_facility_effect[facility_cid].effect
        # 初始化患者人数上限，并刷新当天患者人数
        elif facility_name == "医疗部":
            cache.base_resouce.patient_max = game_config.config_facility_effect[facility_cid].effect
            cache.base_resouce.patient_now = random.randint(1,cache.base_resouce.patient_max)
        # 初始化科研区设施数量上限
        elif facility_name == "科研部":
            cache.base_resouce.research_zone_max = game_config.config_facility_effect[facility_cid].effect
        # 初始化商店数量上限
        elif facility_name == "贸易区":
            cache.base_resouce.shop_max = game_config.config_facility_effect[facility_cid].effect
        # 初始化战斗时干员数量上限
        elif facility_name == "指挥室":
            cache.base_resouce.soldier_max = game_config.config_facility_effect[facility_cid].effect
        # 初始化人数上限
        elif facility_name == "文职部":
            if level >= 5 and 2 not in cache.base_resouce.recruit_now:
                cache.base_resouce.recruit_now[2] = 0
            if level >= 3 and 1 not in cache.base_resouce.recruit_now:
                cache.base_resouce.recruit_now[1] = 0
            if 0 not in cache.base_resouce.recruit_now:
                cache.base_resouce.recruit_now[0] = 0


def update_base_resouce_newday():
    """
    刷新基地资源数据\n
    Keyword arguments:
    无\n
    Return arguments:
    无
    """
    # 刷新新病人数量，已治愈病人数量和治疗收入归零
    cache.base_resouce.patient_now = random.randint(1,cache.base_resouce.patient_max)
    cache.base_resouce.patient_cured = 0
    cache.base_resouce.cure_income = 0
    cache.base_resouce.all_income = 0


def update_work_people():
    """
    刷新各干员的职位和当前正在工作的干员
    """

    cache.base_resouce.doctor_now = 0
    cache.base_resouce.doctor_id_set = set()
    cache.base_resouce.HR_now = 0
    cache.base_resouce.HR_id_set = set()
    cache.base_resouce.library_manager_now = 0
    cache.base_resouce.library_manager_set = set()
    cache.base_resouce.teacher_set = set()
    cache.base_resouce.student_set = set()
    cache.base_resouce.work_people_now = 0

    cache.npc_id_got.discard(0)
    for id in cache.npc_id_got:
        character_data = cache.character_data[id]

        # 医生统计
        if character_data.work.work_type == 61:
            cache.base_resouce.doctor_id_set.add(id)
            if handle_premise.handle_in_clinic(id):
                cache.base_resouce.doctor_now += 1
                cache.base_resouce.work_people_now += 1
        # HR统计
        elif character_data.work.work_type == 71:
            cache.base_resouce.HR_id_set.add(id)
            if handle_premise.handle_in_hr_office(id):
                cache.base_resouce.HR_now += 1
                cache.base_resouce.work_people_now += 1
        # 图书馆管理员统计
        elif character_data.work.work_type == 101:
            cache.base_resouce.library_manager_set.add(id)
            if handle_premise.handle_in_library_office(id) or handle_premise.handle_in_library(id):
                cache.base_resouce.library_manager_now += 1
                cache.base_resouce.work_people_now += 1
        # 老师统计
        elif character_data.work.work_type == 151:
            cache.base_resouce.teacher_set.add(id)
            if handle_premise.handle_in_class_room(id):
                cache.base_resouce.work_people_now += 1
        # 学生统计
        elif character_data.work.work_type == 152:
            cache.base_resouce.student_set.add(id)
            if handle_premise.handle_in_class_room(id):
                cache.base_resouce.work_people_now += 1


def update_facility_people():
    """
    更新当前基地各设施使用人数
    """

    cache.base_resouce.reader_now = 0

    cache.npc_id_got.discard(0)
    for id in cache.npc_id_got:
        # 图书馆读者统计
        if handle_premise.handle_in_library(id):
            cache.base_resouce.reader_now += 1

def check_random_borrow_book(character_id):
    """
    检查角色是否有借书，有的话跳过，没有的话随机借一本书
    """
    character_data: game_type.Character = cache.character_data[character_id]

    # 已借书则跳过
    if len(character_data.entertainment.borrow_book_id_set):
        return 1
    # 未借书则随机借书
    else:
        # 遍历获得所有没借的书id
        recommend_book_id_set,book_id_set = [],[]
        for book_id in cache.base_resouce.book_borrow_dict:
            # 未被借出则加入book_id_set
            if cache.base_resouce.book_borrow_dict[book_id] == -1:
                book_id_set.append(book_id)
                # 如果类型在推荐列表里，则加入recommend_book_id_set
                if game_config.config_book[book_id].type in cache.base_resouce.recommend_book_type_set:
                    recommend_book_id_set.append(book_id)
        # 如果推荐列表有书，则有一半的概率在推荐列表里借书，否则在全列表里借书
        if len(recommend_book_id_set) and random.randint(0,1) == 1:
            borrow_book_id = random.choice(recommend_book_id_set)
        else:
            borrow_book_id = random.choice(book_id_set)
        cache.base_resouce.book_borrow_dict[borrow_book_id] = character_id
        character_data.entertainment.borrow_book_id_set.add(borrow_book_id)
        # print(f"debug {character_data.name}借了书{borrow_book_id}")
        return 0

def check_return_book(character_id):
    """
    检查并决定是否归还当前书籍
    """
    character_data: game_type.Character = cache.character_data[character_id]

    # 未借书则跳过
    if len(character_data.entertainment.borrow_book_id_set) == 0:
        return 0
    # 已借书则d100和还书概率比大小
    else:
        return_d100 = random.randint(1,100)
        # 小于还书概率则还书
        # print(f"debug return_d100 = {return_d100},book_return_possibility = {character_data.entertainment.book_return_possibility}")
        if return_d100 < character_data.entertainment.book_return_possibility:
            for book_id in character_data.entertainment.borrow_book_id_set:
                cache.base_resouce.book_borrow_dict[book_id] = -1
                character_data.entertainment.borrow_book_id_set.discard(book_id)
                # print(f"debug {character_data.name}还了书{book_id}")
                return 1
