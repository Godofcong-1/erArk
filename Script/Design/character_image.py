import itertools
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
      根据角色当前状态构造所有可能差分组合，并按差分优先度依次尝试匹配完全符合的图片名，
      若无符合项则返回原始立绘。
    """
    character_data: game_type.Character = cache.character_data[character_id]
    # 底图本身是否已经是幼女立绘（女儿专用图"女儿_N"、母亲萝莉图"{母名}_小"），是则不再叠加"_小"差分，否则会拼出"女儿_1_小_全裸"这种不存在的文件名
    base_is_child_image = False
    # 判断是否为女儿（特殊角色）
    if character_data.relationship.father_id == 0:
        # 默认为使用标准图片
        character_image_name = "女儿_1"
        # 女儿专用立绘本身就是幼女画
        base_is_child_image = True
        # 母亲的名字的萝莉图片
        mother_data: game_type.Character = cache.character_data[character_data.relationship.mother_id]
        mather_image_name = mother_data.name + "_小"
        # 优先选择自己的同名图片（兼容扁平命名与半身图层命名）
        if character_data.name in era_image.image_data or f"{character_data.name}_半身" in era_image.image_data:
            character_image_name = _(character_data.name, revert_translation=True)
            # 同名立绘属于常规图组，可能自带"_小"差分，故仍按普通规则叠加
            base_is_child_image = False
        # 其次选择母亲的名字的萝莉图片（兼容扁平命名与半身图层命名）
        elif mather_image_name in era_image.image_data or f"{mather_image_name}_半身" in era_image.image_data:
            character_image_name = _(mather_image_name, revert_translation=True)
            # 母亲萝莉图的名字里已经带了"_小"
            base_is_child_image = True
    # 非女儿的正常干员角色
    else:
        character_image_name = _(character_data.name, revert_translation=True)
    base_name = character_image_name

    # 调用各差分判断，得到各差分字符串
    # 底图已是幼女画时跳过萝莉差分，避免拼出重复的"_小"
    child_diff: str = "" if base_is_child_image else child_judge(character_id)
    naked_diff: str = naked_judge(character_id)
    chest_diff: str = chest_judge(character_id)
    big_belly_diff: str = big_belly_judge(character_id)
    emotion_diff: str = emotion_judge(character_id)
    # 依照优先度顺序：萝莉 > 裸体 > 胸部 > 膨腹 > 心情
    diff_list = [child_diff, naked_diff, chest_diff, big_belly_diff, emotion_diff]

    # 图片索引以文件名首段（第一个"_"之前的部分）为键，与角色名不一定相同
    # 例如女儿的底图是"女儿_1"，索引键为"女儿"，用角色名（女儿的自定义名）去查会永远查不到，导致差分匹配被整段跳过
    base_chara_key = base_name.split("_")[0]
    # 如果底图在差分索引中存在，则尝试匹配符合的候选图片
    if base_chara_key in era_image.image_data_index_by_chara:
        # 只保留实际生效的差分，顺序仍为优先度顺序
        active_diff_list = [diff for diff in diff_list if diff != ""]
        # 构造候选组合列表：
        # 按"保留的差分个数从多到少"枚举差分子集，个数相同时优先保留高优先度的差分，最后回落到无差分的底图
        # 不能只从尾部逐级削减：高优先度差分若没有对应图片，会连带挡住所有低优先度差分
        # 例如苏苏洛有"_全裸"图但没有"_小"图，从尾部削减时"苏苏洛_全裸"永远拼不出来，只能落到无差分底图
        candidates = []
        for keep_count in range(len(active_diff_list), -1, -1):
            for index_group in itertools.combinations(range(len(active_diff_list)), keep_count):
                candidates.append(base_name + "".join(active_diff_list[i] for i in index_group))

        # 按顺序在候选列表中选择存在的第一个
        for candidate in candidates:
            # 检查候选图片是否存在（扁平命名）
            if candidate in era_image.image_data:
                return candidate
            # 检查半身图层命名（如 薇薇安娜_小_半身），兼容半身/全身双图层结构
            if f"{candidate}_半身" in era_image.image_data:
                return f"{candidate}_半身"
            # 如果候选图片不匹配且裸体差分不为空，则尝试互换全裸与半裸
            if naked_diff != "" and naked_diff in candidate:
                # 判断裸体差分类型并替换为另一种
                if naked_diff == "_全裸":
                    candidate_alt = candidate.replace("_全裸", "_半裸")  # 替换为半裸
                elif naked_diff == "_半裸":
                    candidate_alt = candidate.replace("_半裸", "_全裸")  # 替换为全裸
                # 检查替换后的候选图片是否存在
                if candidate_alt in era_image.image_data:
                    return candidate_alt
                # 同样检查替换后候选的半身图层命名
                if f"{candidate_alt}_半身" in era_image.image_data:
                    return f"{candidate_alt}_半身"

    # 若无匹配则使用原始立绘名，但需要检查半身图格式兼容
    # 这是为了兼容新的文件名格式：{角色名}_半身.png
    if base_name in era_image.image_data:
        return base_name
    # 如果原始立绘名不存在，尝试查找半身图格式
    half_body_name = f"{base_name}_半身"
    if half_body_name in era_image.image_data:
        return half_body_name
    # 都不存在则返回原始名（可能会导致图片显示失败）
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

