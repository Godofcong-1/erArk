from types import FunctionType
from Script.Core import (
    cache_control,
    game_type,
    get_text,
    era_image
)
from Script.Design import handle_premise

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """

def find_character_image_name(character_id: int) -> str:
    """
    查找角色图片名称
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    str -- 角色图片名称
    """
    character_data: game_type.Character = cache.character_data[character_id]
    image_name = ""

    # 如果是女儿的话
    if character_data.relationship.father_id == 0:
        character_image_name = "女儿_1"
        image_name = character_image_name
    # 非女儿的正常干员角色
    else:
        character_image_name = _(character_data.name, revert_translation=True)
        image_name = character_image_name
        # 查询角色差分图片是否存在
        if character_data.name in era_image.image_data_index_by_chara:
            all_image_name_for_character = era_image.image_data_index_by_chara[character_data.name]
            # print(all_image_name_for_character)
            # 心情差分
            emotion_flag = False
            emotion_text = emotion_judge(character_id)
            # 裸体差分
            naked_flag = False
            naked_text = naked_judge(character_id)
            # 胸部差分
            chest_flag = False
            chest_text = chest_judge(character_id)
            # 遍历差分，确认各差分是否存在
            for image_name_for_character in all_image_name_for_character:
                if emotion_text in image_name_for_character:
                    emotion_flag = True
                # 裸体则宽容处理
                if naked_text != "":
                    if "_全裸" in image_name_for_character:
                        naked_flag = 1
                    elif "_半裸" in image_name_for_character:
                        naked_flag = 2
                if chest_text in image_name_for_character:
                    chest_flag = True
            # 根据flag来确定最终图片名称
            if emotion_flag:
                image_name += emotion_text
            if naked_flag == 1:
                image_name += "_全裸"
            elif naked_flag == 2:
                image_name += "_半裸"
            if chest_flag:
                image_name += chest_text

    # 如果目标图片不存在，则使用角色原始图片
    if image_name not in era_image.image_data:
        image_name = character_image_name
    return image_name


def emotion_judge(character_id: int) -> str:
    """
    角色心情判断
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    str -- 角色图片名称
    """
    image_name = ""
    if handle_premise.handle_good_mood(character_id):
        image_name += "_愉快"
    elif handle_premise.handle_bad_mood(character_id):
        image_name += "_不爽"
    elif handle_premise.handle_angry_mood(character_id):
        image_name += "_愤怒"
    return image_name


def naked_judge(character_id: int) -> str:
    """
    角色裸体判断
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    str -- 角色图片名称
    """
    image_name = ""
    if handle_premise.handle_cloth_off(character_id):
        image_name += "_全裸"
    elif handle_premise.handle_cloth_most_off(character_id):
        image_name += "_半裸"
    elif handle_premise.handle_not_wear_in_up(character_id) and handle_premise.handle_not_wear_bra(character_id):
        image_name += "_半裸"
    return image_name


def chest_judge(character_id: int) -> str:
    """
    角色胸部判断
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    str -- 角色图片名称
    """
    image_name = ""
    if handle_premise.handle_self_chest_is_cliff(character_id):
        image_name += "_绝壁"
    elif handle_premise.handle_self_chest_is_small(character_id):
        image_name += "_贫乳"
    elif handle_premise.handle_self_chest_is_normal(character_id):
        image_name += "_普乳"
    elif handle_premise.handle_self_chest_is_big(character_id):
        image_name += "_巨乳"
    elif handle_premise.handle_self_chest_is_super(character_id):
        image_name += "_爆乳"
    return image_name