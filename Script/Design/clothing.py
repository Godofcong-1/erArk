import random
import math
import uuid
from typing import Dict
from Script.Core import game_type,cache_control
from Script.Config import game_config
from Script.Design import attr_calculation

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """


def get_npc_cloth(character_id: int):
    """
    根据csv换一身同样的衣服，然后随机内衣
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    无
    """
    if character_id:
        character_data = cache.character_data[character_id]
        character_data.cloth.cloth_wear = attr_calculation.get_cloth_wear_zero()
        tem_character = cache.npc_tem_data[character_id]

        for cloth_id in tem_character.Cloth:
            type = game_config.config_clothing_tem[cloth_id].clothing_type
            # print(f"debug cloth_id = {cloth_id},name = {game_config.config_clothing_tem[cloth_id].name},type = {type}")
            character_data.cloth.cloth_wear[type].append(cloth_id)
        get_underwear(character_id)

def get_underwear(character_id: int):
    """
    随机穿内衣，包括胸罩和内裤
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    无
    """
    character_data = cache.character_data[character_id]
    # 60,幼女,61,萝莉,62,少女,63,成年,64,长生者

    # 遍历全衣服，以下分别是正常/童装/情趣的胸罩和内裤
    bra_nor_list = []
    bra_loli_list = []
    bra_H_list = []
    pan_nor_list = []
    pan_loli_list = []
    pan_H_list = []
    for cloth_id in game_config.config_clothing_tem:
        cloth = game_config.config_clothing_tem[cloth_id]
        if cloth.clothing_type == 6:
            if cloth.tag == 0:
                bra_nor_list.append(cloth_id)
            elif cloth.tag == 1:
                bra_loli_list.append(cloth_id)
            elif cloth.tag == 2:
                bra_H_list.append(cloth_id)
        elif cloth.clothing_type == 9:
            if cloth.tag == 0:
                pan_nor_list.append(cloth_id)
            elif cloth.tag == 1:
                pan_loli_list.append(cloth_id)
            elif cloth.tag == 2:
                pan_H_list.append(cloth_id)

    # 解锁了情趣内衣的情况下，对2级攻略以上的角色增加情趣内衣
        for i in {11,12,13,16,17,18}:
            if character_data.talent[i]:
                if cache.character_data[0].pl_collection.collection_bonus[102]:
                    bra_nor_list += bra_H_list
                    bra_loli_list += bra_H_list
                    pan_nor_list += pan_H_list
                    pan_loli_list += pan_H_list
                    break

    # 判断是否当前已经穿了胸衣和内裤
    if not len(character_data.cloth.cloth_wear[6]):
        # 随机选择胸衣和内裤，有儿童和普通人两个分支
        if character_data.talent[60] or character_data.talent[61]:
            bra_id = random.choice(bra_loli_list)
            character_data.cloth.cloth_wear[6].append(bra_id)
        else:
            bra_id = random.choice(bra_nor_list)
            character_data.cloth.cloth_wear[6].append(bra_id)

    if not len(character_data.cloth.cloth_wear[9]):
        if character_data.talent[60] or character_data.talent[61]:
            pan_id = random.choice(pan_loli_list)
            character_data.cloth.cloth_wear[9].append(pan_id)
        else:
            pan_id = random.choice(pan_nor_list)
            character_data.cloth.cloth_wear[9].append(pan_id)


def get_cloth_off(character_id: int):
    """
    脱成全裸
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    无
    """
    if character_id:
        character_data = cache.character_data[character_id]
        character_data.cloth.cloth_wear = attr_calculation.get_cloth_wear_zero()


def get_shower_cloth(character_id: int):
    """
    换上浴帽和浴巾
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    无
    """
    if character_id:
        character_data = cache.character_data[character_id]
        character_data.cloth.cloth_wear = attr_calculation.get_cloth_wear_zero()
        character_data.cloth.cloth_wear[0].append(51)
        character_data.cloth.cloth_wear[5].append(551)
        character_data.cloth.cloth_wear[8].append(851)


def get_sleep_cloth(character_id: int):
    """
    换上睡衣和内衣
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    无
    """
    if character_id:
        character_data = cache.character_data[character_id]
        character_data.cloth.cloth_wear = attr_calculation.get_cloth_wear_zero()
        choic_flag = random.randint(0,1)
        if choic_flag:
            character_data.cloth.cloth_wear[5].append(552)
            character_data.cloth.cloth_wear[8].append(852)
        else:
            character_data.cloth.cloth_wear[5].append(553)
            character_data.cloth.cloth_wear[8].append(853)
        get_underwear(character_id)


'''
不用的旧函数

def creator_suit(suit_id: int, sex: int) -> Dict[int, game_type.Clothing]:
    """
    创建套装
    Keyword arguments:
    suit_name -- 套装模板
    sex -- 性别模板
    Return arguments:
    Dict[int,game_type.Clothing] -- 套装数据 服装穿戴位置:服装数据
    """
    suit_data = game_config.config_clothing_suit_data[suit_id][sex]
    clothing_data = {}
    for clothing_id in suit_data:
        clothing = creator_clothing(clothing_id)
        clothing_data[clothing.wear] = clothing
    return clothing_data


def creator_clothing(clothing_tem_id: int) -> game_type.Clothing:
    """
    创建服装的基础函数
    Keyword arguments:
    clothing_tem_id -- 服装id
    Return arguments:
    game_type.Clothing -- 生成的服装数据
    """
    clothing_data = game_type.Clothing()
    clothing_data.uid = uuid.uuid4()
    clothing_data.sexy = random.randint(1, 1000)
    clothing_data.handsome = random.randint(1, 1000)
    clothing_data.elegant = random.randint(1, 1000)
    clothing_data.fresh = random.randint(1, 1000)
    clothing_data.sweet = random.randint(1, 1000)
    clothing_data.warm = random.randint(0, 30)
    clothing_data.price = sum(
        [
            clothing_data.__dict__[x]
            for x in clothing_data.__dict__
            if isinstance(clothing_data.__dict__[x], int)
        ]
    )
    clothing_data.cleanliness = 100
    clothing_data.evaluation = game_config.config_clothing_evaluate_list[
        math.floor(clothing_data.price / 480) - 1
    ]
    clothing_data.tem_id = clothing_tem_id
    clothing_data.wear = game_config.config_clothing_tem[clothing_tem_id].clothing_type
    return clothing_data

'''