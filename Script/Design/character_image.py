from types import FunctionType
from Script.Core import (
    cache_control,
    game_type,
    get_text,
)
from Script.Design import (
    handle_premise
)


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
        image_name = "女儿_1"
    # 非女儿的正常干员角色
    else:
        character_image_name = _(character_data.name, revert_translation=True)
        image_name = character_image_name
        # 白金差分
        if character_data.adv == 204:
            # 没有穿上衣+胸衣
            if handle_premise.handle_not_wear_in_up(character_id) and handle_premise.handle_not_wear_bra(character_id):
                image_name += "_半裸"
                # 胸部大小差分
                if character_data.talent[122]:
                    image_name += "_贫乳"
                elif character_data.talent[123]:
                    image_name += "_普乳"
                elif character_data.talent[124]:
                    image_name += "_巨乳"
                elif character_data.talent[125]:
                    image_name += "_爆乳"
                else:
                    image_name = character_image_name
    return image_name