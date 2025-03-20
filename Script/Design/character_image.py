from types import FunctionType
from Script.Core import (
    cache_control,
    game_type,
    get_text,
    era_image
)
from Script.Design import handle_premise

cache: game_type.Cache = cache_control.cache  # 游戏缓存数据
_: FunctionType = get_text._  # 翻译api

def find_character_image_name(character_id: int) -> str:
    """
    查找角色图片名称。
    参数:
      character_id (int): 角色id。
    返回:
      str: 最终选中的角色图片名称。
    功能描述:
      根据角色当前状态构造所有可能差分组合，并按差分优先度（萝莉>裸体>胸部>膨腹>心情）依次尝试匹配完全符合的图片名，
      若无符合项则返回原始立绘。
    """
    character_data: game_type.Character = cache.character_data[character_id]
    # 判断是否为女儿（特殊角色）
    if character_data.relationship.father_id == 0:
        # 默认为使用标准图片
        character_image_name = "女儿_1"
        # 母亲的名字的萝莉图片
        mother_data: game_type.Character = cache.character_data[character_data.relationship.mother_id]
        mather_image_name = mother_data.name + "_小"
        # 优先选择自己的同名图片
        if character_data.name in era_image.image_data:
            character_image_name = _(character_data.name, revert_translation=True)
        # 其次选择母亲的名字的萝莉图片
        elif mather_image_name in era_image.image_data:
            character_image_name = _(mather_image_name, revert_translation=True)
    # 非女儿的正常干员角色
    else:
        character_image_name = _(character_data.name, revert_translation=True)
    base_name = character_image_name

    # 调用各差分判断，得到各差分字符串
    child_diff: str = child_judge(character_id)
    naked_diff: str = naked_judge(character_id)
    chest_diff: str = chest_judge(character_id)
    big_belly_diff: str = big_belly_judge(character_id)
    emotion_diff: str = emotion_judge(character_id)
    # 依照优先度顺序：萝莉 > 裸体 > 胸部 > 膨腹 > 心情
    diff_list = [child_diff, naked_diff, chest_diff, big_belly_diff, emotion_diff]

    # 如果角色在差分索引中存在，则尝试匹配符合的候选图片
    if character_data.name in era_image.image_data_index_by_chara:
        all_image_names = era_image.image_data_index_by_chara[character_data.name]
        # 构造候选组合列表：
        # 先尝试全组合，再依次去掉低优先级的差分（即从后向前移除非空项）
        candidates = []
        # 全组合
        full_candidate = base_name + "".join(diff_list)
        candidates.append(full_candidate)
        # 逐级去掉低优先级差分
        for i in range(1, len(diff_list)+1):
            # 去掉最后 i 个差分（若为空则保留，但此步骤对比无影响）
            candidate = base_name + "".join(diff_list[:-i])
            candidates.append(candidate)
        # 去掉所有差分（即仅选原始候选）也作为候选
        candidates.append(base_name)

        # 按顺序在候选列表中选择存在的第一个
        for candidate in candidates:
            if candidate in era_image.image_data:
                return candidate

    # 若无匹配则使用原始立绘名
    return base_name

def child_judge(character_id: int) -> str:
    """
    判断角色萝莉状态。
    参数:
      character_id (int): 角色id。
    返回:
      str: 若符合萝莉状态返回差分后缀，否则返回空字符串。
    """
    image_name = ""
    if handle_premise.handle_self_child_or_loli_1(character_id):
        image_name += "_小"
    return image_name

def emotion_judge(character_id: int) -> str:
    """
    判断角色心情状态。
    参数:
      character_id (int): 角色id。
    返回:
      str: 根据角色心情返回对应的差分后缀，否则返回空字符串。
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
    判断角色裸体状态。
    参数:
      character_id (int): 角色id。
    返回:
      str: 若符合裸体状态返回差分后缀（全裸或半裸），否则返回空字符串。
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
    判断角色胸部状态。
    参数:
      character_id (int): 角色id。
    返回:
      str: 返回对应的胸部差分后缀（绝壁、贫乳、普乳、巨乳或爆乳），否则返回空字符串。
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

def big_belly_judge(character_id: int) -> str:
    """
    判断角色膨腹状态。
    参数:
      character_id (int): 角色id。
    返回:
      str: 若符合膨腹状态返回对应的差分后缀，否则返回空字符串。
    """
    image_name = ""
    if handle_premise.handle_parturient_1(character_id):
        image_name += "_大膨腹"
    elif handle_premise.handle_inflation_1(character_id):
        image_name += "_膨腹"
    elif handle_premise.handle_cumflation_1(character_id):
        image_name += "_膨腹"
    return image_name

