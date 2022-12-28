import random
from Script.Core import (
    cache_control,
    game_type,
)
from Script.Config import game_config
from Script.Design import handle_premise

cache: game_type.Cache = cache_control.cache
""" 游戏内缓存数据 """


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
