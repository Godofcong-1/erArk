import random
from types import FunctionType
from Script.Core import (
    cache_control,
    game_type,
    get_text,
)
from Script.Config import game_config, normal_config
from Script.Design import attr_calculation, handle_premise
from Script.UI.Moudle import draw

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
window_width: int = normal_config.config_normal.text_width
""" 窗体宽度 """
_: FunctionType = get_text._
""" 翻译api """


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
        tem_character = cache.npc_tem_data[character_id - 1]

        # 如果装备严重损坏，则换为通用衣服
        if handle_premise.handle_self_equipment_damaged_ge_3(character_id):
            get_common_cloth(character_id)
        # 否则正常换衣服
        else:
            for cloth_id in tem_character.Cloth:
                type = game_config.config_clothing_tem[cloth_id].clothing_type
                # print(f"debug cloth_id = {cloth_id},name = {game_config.config_clothing_tem[cloth_id].name},type = {type}")
                character_data.cloth.cloth_wear[type].append(cloth_id)
            get_underwear(character_id)
            chara_special_wear_cloth(character_id)


def get_cloth_from_dormitory_locker(character_id: int):
    """
    清空身上的旧衣服，从宿舍的衣柜里穿上衣服、内衣内裤，并转移衣柜中的精液数据到穿着的衣服上\n
    Keyword arguments:\n
    character_id -- 角色id\n
    Return arguments:\n
    无
    """
    if character_id:
        character_data = cache.character_data[character_id]
        # 是否被监禁
        if handle_premise.handle_imprisonment_1(character_id):
            handle_prisoner_clothing(character_id)
            return
        tem_character = cache.npc_tem_data[character_id - 1]
        tem_cloth_list = tem_character.Cloth.copy()
        # 检查宿舍衣柜中是否有衣服
        wear_locker_flag = False
        for cloth_type in character_data.cloth.cloth_locker_in_dormitory:
            if len(character_data.cloth.cloth_locker_in_dormitory[cloth_type]):
                wear_locker_flag = True
                # 去掉里面不符合角色csv的衣服
                for cloth_id in character_data.cloth.cloth_locker_in_dormitory[cloth_type].copy():
                    if cloth_id not in tem_cloth_list:
                        character_data.cloth.cloth_locker_in_dormitory[cloth_type].remove(cloth_id)
                    else:
                        tem_cloth_list.remove(cloth_id)
        # 宿舍衣柜中有衣服的话，穿上衣服
        if wear_locker_flag:
            character_data.cloth.cloth_wear = attr_calculation.get_cloth_wear_zero()
            character_data.cloth.cloth_wear = character_data.cloth.cloth_locker_in_dormitory
            character_data.cloth.cloth_locker_in_dormitory = attr_calculation.get_cloth_locker_in_dormitory_zero()
            # 如果在范例里的衣服还有没穿着的，则穿上
            for cloth_id in tem_cloth_list:
                type = game_config.config_clothing_tem[cloth_id].clothing_type
                # 跳过内衣内裤
                if type in {6,9}:
                    continue
                character_data.cloth.cloth_wear[type].append(cloth_id)
            # 换内衣内裤
            get_underwear(character_id)
            # 将衣柜里的衣服精液转移到穿着的衣服上
            locker_cloth_semen_to_wear_cloth_semen(character_id)
        # 宿舍衣柜中没有衣服的话，根据csv穿衣服
        if not wear_locker_flag:
            get_npc_cloth(character_id)

        # 如果被命令了每条换新袜子
        if handle_premise.handle_ask_wear_different_socks_everyday(character_id):
            get_socks(character_id)

    # 穿特殊服装
    chara_special_wear_cloth(character_id)


def handle_prisoner_clothing(character_id: int):
    """
    处理囚犯的服装\n
    参数:
        character_id -- 囚犯角色的id
    返回:
        无
    """
    if character_id:
        character_data = cache.character_data[character_id]
        cache.rhodes_island.confinement_training_setting.setdefault(2, 0)
        cache.rhodes_island.confinement_training_setting.setdefault(3, 0)
        # 全裸
        if cache.rhodes_island.confinement_training_setting[2] == 0:
            get_all_cloth_off(character_id)
        # 囚服
        elif cache.rhodes_island.confinement_training_setting[2] == 1:
            get_prison_cloth(character_id)
        # 正常衣服
        else:
            get_npc_cloth(character_id)
        # 清空内衣
        # if cache.rhodes_island.confinement_training_setting[3] == 0:
        character_data.cloth.cloth_wear[6] = []
        character_data.cloth.cloth_wear[9] = []
        # 清空袜子
        if cache.rhodes_island.confinement_training_setting[3] == 0:
            character_data.cloth.cloth_wear[10] = []
        # 提供情趣内衣与袜子
        elif cache.rhodes_island.confinement_training_setting[3] == 1:
            get_underwear(character_id, type_cid = 2)
            get_socks(character_id)
        # 提供正常内衣与袜子
        else:
            get_underwear(character_id)
            get_socks(character_id)
        chara_special_wear_cloth(character_id)


def get_random_underwear():
    """
    随机返回一件内衣和一件内裤
    Keyword arguments:
    无
    Return arguments:
    无
    """
    bra_list = []
    pan_list = []
    for cloth_id in game_config.config_clothing_tem:
        cloth = game_config.config_clothing_tem[cloth_id]
        if cloth.clothing_type == 6:
            bra_list.append(cloth_id)
        elif cloth.clothing_type == 9:
            pan_list.append(cloth_id)
    bra_id = random.choice(bra_list)
    pan_id = random.choice(pan_list)
    return bra_id, pan_id


def get_underwear(character_id: int, part_flag = 0, type_cid = 0):
    """
    随机穿内衣，包括胸罩和内裤\n
    Keyword arguments:\n
    character_id -- 角色id\n
    part_flag -- 是否只穿某个部件，0都穿，1仅胸衣，2仅内裤\n
    Return arguments:\n
    无
    """
    character_data = cache.character_data[character_id]
    # 60,幼女,61,萝莉,62,少女,63,成年,64,长生者

    # 遍历全衣服，以下分别是正常/童装/情趣的胸衣和内裤
    bra_nor_list = []
    bra_loli_list = []
    bra_H_list = []
    pan_nor_list = []
    pan_loli_list = []
    pan_H_list = []
    for cloth_id in game_config.config_clothing_tem:
        cloth = game_config.config_clothing_tem[cloth_id]
        # 跳过非自己的衣服
        if cloth.npc != 0 and cloth.npc != character_data.adv:
            continue
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
    character_fall_level = attr_calculation.get_character_fall_level(character_id)
    if character_fall_level >= 2:
        if cache.character_data[0].pl_collection.collection_bonus == {}:
            cache.character_data[0].pl_collection = attr_calculation.get_collection_zero()
        if cache.character_data[0].pl_collection.collection_bonus[102]:
            bra_nor_list += bra_H_list
            bra_loli_list += bra_H_list
            pan_nor_list += pan_H_list
            pan_loli_list += pan_H_list

    # 判断是否需要穿，包括是否已穿和part_flag限制
    if (
        not len(character_data.cloth.cloth_wear[6]) # 当前没有穿胸衣
        and part_flag != 2 # 本次穿胸衣
        and len(bra_nor_list) # 有可穿的胸衣
        and not handle_premise.handle_ask_not_wear_corset(character_id) # 没有禁止穿胸衣
        ):
        # 随机选择胸衣和内裤
        # 指定类别
        if type_cid == 2 and len(bra_H_list):
            bra_id = random.choice(bra_H_list)
            character_data.cloth.cloth_wear[6].append(bra_id)
        # 童装
        elif character_data.talent[102] or character_data.talent[103]:
            bra_id = random.choice(bra_loli_list)
            character_data.cloth.cloth_wear[6].append(bra_id)
        # 正常
        else:
            bra_id = random.choice(bra_nor_list)
            character_data.cloth.cloth_wear[6].append(bra_id)

    if (
        not len(character_data.cloth.cloth_wear[9]) # 当前没有穿内裤
        and part_flag != 1 # 本次穿内裤
        and len(pan_nor_list) # 有可穿的内裤
        ):
        if type_cid == 2 and len(pan_H_list):
            pan_id = random.choice(pan_H_list)
            character_data.cloth.cloth_wear[9].append(pan_id)
        elif character_data.talent[102] or character_data.talent[103]:
            pan_id = random.choice(pan_loli_list)
            character_data.cloth.cloth_wear[9].append(pan_id)
        else:
            pan_id = random.choice(pan_nor_list)
            character_data.cloth.cloth_wear[9].append(pan_id)


def get_socks(character_id: int):
    """
    随机穿袜子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    无
    """
    character_data = cache.character_data[character_id]

    # 遍历全衣服
    socks_list = []
    for cloth_id in game_config.config_clothing_tem:
        cloth = game_config.config_clothing_tem[cloth_id]
        # 跳过非自己的衣服
        if cloth.npc != 0 and cloth.npc != character_data.adv:
            continue
        if cloth.clothing_type == 10:
            socks_list.append(cloth_id)

    # 清空旧袜子
    character_data.cloth.cloth_wear[10] = []
    # 随机穿袜子
    socks_id = random.choice(socks_list)
    character_data.cloth.cloth_wear[10].append(socks_id)


def undress_out_cloth(character_id: int):
    """
    脱掉外衣
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    无
    """
    if character_id:
        character_data = cache.character_data[character_id]
        for i in {5,8}:
            character_data.cloth.cloth_wear[i] = []
        chara_special_wear_cloth(character_id)


def strip_down_till_socks_and_gloves_left(character_id: int):
    """
    脱到只穿袜子手套等
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    无
    """
    if character_id:
        character_data = cache.character_data[character_id]
        for i in {5,6,8,9}:
            character_data.cloth.cloth_wear[i] = []
        chara_special_wear_cloth(character_id)


def pl_get_chara_pan(character_id: int):
    """
    玩家获得该角色的内裤
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    无
    """
    pl_character_data = cache.character_data[0]
    if character_id > 0:
        character_data = cache.character_data[character_id]
        # 如果角色穿了内裤
        if len(character_data.cloth.cloth_wear[9]):
            TagetPanId = character_data.cloth.cloth_wear[9][-1]
            cloth_use_type = game_config.config_clothing_tem[TagetPanId].tag
            # 加到玩家的内裤收藏里
            pl_character_data.pl_collection.npc_panties_tem.setdefault(character_id, [])
            pl_character_data.pl_collection.npc_panties_tem[character_id].append(TagetPanId)
            # 加到玩家的行动记录里
            TPanName = game_config.config_clothing_tem[TagetPanId].name
            pl_character_data.behavior.pan_name = TPanName
            # 脱掉内裤
            character_data.cloth.cloth_wear[9] = []
            character_data.cloth.cloth_see[9] = True
            # 如果该服装为泳装，则将胸衣也一起脱掉
            if cloth_use_type == 3:
                character_data.cloth.cloth_wear[6] = []
                character_data.cloth.cloth_see[6] = True
            # 如果该角色在无意识中，则标注无意识flag
            if handle_premise.handle_unconscious_flag_ge_1(character_id):
                character_data.cloth.stolen_panties_in_unconscious = True
            # 绘制信息
            now_draw = draw.WaitDraw()
            now_draw.width = window_width
            now_draw.text = _("\n获得了{0}的{1}，可在藏品馆里纳入收藏\n").format(character_data.name, TPanName)
            now_draw.draw()


def pl_get_chara_socks(character_id: int):
    """
    玩家获得该角色的袜子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    无
    """
    pl_character_data = cache.character_data[0]
    if character_id > 0:
        character_data = cache.character_data[character_id]
        # 如果角色穿了袜子
        if len(character_data.cloth.cloth_wear[10]):
            TagetSocId = character_data.cloth.cloth_wear[10][-1]
            # 加到玩家的袜子收藏里
            pl_character_data.pl_collection.npc_socks_tem.setdefault(character_id, [])
            pl_character_data.pl_collection.npc_socks_tem[character_id].append(TagetSocId)
            # 加到玩家的行动记录里
            TSocName = game_config.config_clothing_tem[TagetSocId].name
            pl_character_data.behavior.socks_name = TSocName
            # 脱掉袜子
            character_data.cloth.cloth_wear[10] = []
            character_data.cloth.cloth_see[10] = True
            # 如果该角色在无意识中，则标注无意识flag
            if handle_premise.handle_unconscious_flag_ge_1(character_id):
                character_data.cloth.stolen_socks_in_unconscious = True
            # 绘制信息
            now_draw = draw.WaitDraw()
            now_draw.width = window_width
            now_draw.text = _("\n获得了{0}的{1}，可在藏品馆里纳入收藏\n").format(character_data.name, TSocName)
            now_draw.draw()


def get_all_cloth_off(character_id: int):
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
        chara_special_wear_cloth(character_id)


def get_shower_cloth(character_id: int):
    """
    清零其他衣服并换上浴帽和浴巾
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    无
    """
    if character_id:
        character_data = cache.character_data[character_id]
        get_cloth_wear_zero_except_need(character_id)
        character_data.cloth.cloth_wear[0].append(51)
        character_data.cloth.cloth_wear[5].append(551)
        character_data.cloth.cloth_wear[8].append(851)
        chara_special_wear_cloth(character_id)


def get_sleep_cloth(character_id: int):
    """
    清零其他衣服并换上睡衣和内裤
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    无
    """
    if character_id:
        character_data = cache.character_data[character_id]
        get_cloth_wear_zero_except_need(character_id)
        choic_flag = random.randint(0,1)
        if choic_flag:
            character_data.cloth.cloth_wear[5].append(552)
            character_data.cloth.cloth_wear[8].append(852)
        else:
            character_data.cloth.cloth_wear[5].append(553)
            character_data.cloth.cloth_wear[8].append(853)
        get_underwear(character_id, part_flag = 2)
        chara_special_wear_cloth(character_id)


def get_swim_cloth(character_id: int):
    """
    清零其他衣服并换上泳衣的胸衣和内裤
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    无
    """
    if character_id:
        character_data = cache.character_data[character_id]
        get_cloth_wear_zero_except_need(character_id)
        choic_type = random.randint(1,14)
        character_data.cloth.cloth_wear[6].append(choic_type + 680)
        character_data.cloth.cloth_wear[9].append(choic_type + 980)
        chara_special_wear_cloth(character_id)


def get_prison_cloth(character_id: int):
    """
    清零其他衣服并换上囚服的上衣和下衣
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    无
    """
    if character_id:
        character_data = cache.character_data[character_id]
        get_cloth_wear_zero_except_need(character_id)
        character_data.cloth.cloth_wear[5].append(561)
        character_data.cloth.cloth_wear[8].append(861)
        chara_special_wear_cloth(character_id)


def get_common_cloth(character_id: int):
    """
    清零其他衣服并换上通用的衣服和随机内衣
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    无
    """
    if character_id:
        character_data = cache.character_data[character_id]
        get_cloth_wear_zero_except_need(character_id)
        character_data.cloth.cloth_wear[5].append(581)
        character_data.cloth.cloth_wear[5].append(582)
        down_cloth_random = random.randint(0, 1)
        character_data.cloth.cloth_wear[8].append(881 + down_cloth_random)
        shoes_random = random.randint(0, 3)
        character_data.cloth.cloth_wear[11].append(1181 + shoes_random)
        get_underwear(character_id, part_flag = 2)
        chara_special_wear_cloth(character_id)


def chara_special_wear_cloth(character_id: int):
    """
    角色穿上必须穿的衣物
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    无
    """
    if character_id:
        character_data = cache.character_data[character_id]
        # print(f"debug name = {character_data.name}")
        return_list = []

        # 阿米娅必须戴抑制戒指
        if character_data.adv == 1:
            if 701 not in character_data.cloth.cloth_wear[7]:
                character_data.cloth.cloth_wear[7].append(701)
                # print("换上戒指了")
            return_list.append(701)
        # 源石病感染者必须戴监测环
        if character_data.talent[150]:
            if 1301 not in character_data.cloth.cloth_wear[13]:
                character_data.cloth.cloth_wear[13].append(1301)
                # print("换上监测环了")
            return_list.append(1301)
        # 有戒指素质的必须戴戒指
        if character_data.talent[205]:
            if 751 not in character_data.cloth.cloth_wear[7]:
                character_data.cloth.cloth_wear[7].append(751)
                # print("换上戒指了")
            return_list.append(751)
        # 项圈同理
        elif character_data.talent[215]:
            if 352 not in character_data.cloth.cloth_wear[3]:
                character_data.cloth.cloth_wear[3].append(352)
                # print("换上项圈了")
            return_list.append(352)
    return return_list


def get_cloth_wear_zero_except_need(character_id: int) -> dict:
    """
    遍历当前穿着服装类型，将首饰和必要物品以外的设为空
    """
    character_data = cache.character_data[character_id]
    # print(f"debug 脱衣服前 = {character_data.cloth.cloth_wear}")
    for clothing_type in game_config.config_clothing_type:
        if len(character_data.cloth.cloth_wear[clothing_type]):
            remove_tem_list = []
            for cloth_id in character_data.cloth.cloth_wear[clothing_type]:
                # 只要不是首饰和必须穿着的衣服，就把该服装加入删掉的list里
                if (
                    game_config.config_clothing_tem[cloth_id].tag != 6 
                    and cloth_id not in chara_special_wear_cloth(character_id)
                ):
                    remove_tem_list.append(cloth_id)
            # 获得两个list的差，并赋值给当前服装
            result = [item for item in  character_data.cloth.cloth_wear[clothing_type] if item not in remove_tem_list]
            character_data.cloth.cloth_wear[clothing_type] = result
    chara_special_wear_cloth(character_id)
    # print(f"debug 脱衣服后 = {character_data.cloth.cloth_wear}")


def clean_locker_semen(character_id: int):
    """
    清理衣柜里的衣服精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    无
    """
    character_data = cache.character_data[character_id]
    empty_dirty_data = attr_calculation.get_zero_dirty()
    character_data.dirty.cloth_locker_semen = empty_dirty_data.cloth_locker_semen


def locker_cloth_semen_to_wear_cloth_semen(character_id: int):
    """
    将衣柜里的衣服精液转移到穿着的衣服上
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    无
    """
    character_data = cache.character_data[character_id]
    semen_flag = False
    for clothing_type in game_config.config_clothing_type:
        now_add = character_data.dirty.cloth_locker_semen[clothing_type][1]
        if now_add > 0:
            character_data.dirty.cloth_semen[clothing_type][1] += now_add
            # 更新当前精液等级
            character_data.dirty.cloth_semen[clothing_type][2] = attr_calculation.get_semen_now_level(character_data.dirty.cloth_semen[clothing_type][1], clothing_type, 1)
            semen_flag = True
    if semen_flag:
        clean_locker_semen(character_id)


def get_exposed_body_parts(character_id: int, ignore_panties: bool = False):
    """
    获得角色暴露在外的身体部位
    参数:
        character_id (int): 角色id
        ignore_panties (bool): 是否忽略内裤的覆盖效果，True表示忽略内裤
    返回:
        List[int]: 可暴露的身体部位序号列表
    """
    # 初始化返回列表
    return_list = []
    # 获取角色数据
    character_data = cache.character_data[character_id]
    
    # 身体部位所对应的服装部位，-1表示无对应部位，列表表示多个对应部位
    body_cloth_list = [0, 4, 4, [5, 6], 5, 7, 9, -1, 9, 9, -1, 11, -1, -1, -1, -1, [8, 9], 8, 5]

    # 遍历所有身体部位
    for body_part_cid in game_config.config_body_part:
        # 如果角色没有该身体部位则跳过
        if body_part_cid == 12 and not character_data.talent[113]:
            continue
        elif body_part_cid == 13 and not character_data.talent[112]:
            continue
        elif body_part_cid == 14 and not character_data.talent[111]:
            continue

        now_body_cloth_cid = body_cloth_list[body_part_cid]
        # 判断对应项是否为多个服装部位
        if isinstance(now_body_cloth_cid, list):
            # 遍历所有对应的服装部位
            for cloth_type in now_body_cloth_cid:
                # 如果该服装为内裤且忽略内裤标记为True，则跳过检测这一项
                if cloth_type == 9 and ignore_panties:
                    continue
                # 如果身体部位对应的服装非空，则跳出循环
                if len(character_data.cloth.cloth_wear[cloth_type]):
                    break
            else:
                # 如果所有对应部位均无服装，则将该身体部位加入返回列表
                return_list.append(body_part_cid)
        else:
            # 如果对应部位为-1，表示无需服装，直接加入返回列表
            if now_body_cloth_cid == -1:
                return_list.append(body_part_cid)
            # 如果对应服装为内裤且忽略内裤标记为True，则视为未穿着
            elif now_body_cloth_cid == 9 and ignore_panties:
                return_list.append(body_part_cid)
            # 如果对应服装为空，则加入返回列表
            elif len(character_data.cloth.cloth_wear[now_body_cloth_cid]) == 0:
                return_list.append(body_part_cid)

    # 返回可暴露的身体部位列表
    return return_list

