# -*- coding: UTF-8 -*-
"""
静态检查系统 - 位置/场景/跟随/助理/交互对象领域检查
本模块实现 PLACE-01 ~ PLACE-31 全部不变量检查，覆盖角色位置、场景名册、门锁状态、移动路径、
收藏地点、宿舍、交互对象、助理、跟随、装袋搬运等状态的一致性约束。

约定与踩坑说明（写在此处，避免散落在各检查函数注释里重复）：
1. `["0", "0"]` 不是哨兵值，是真实场景「罗德岛出口」，也是 `Character.position` 的默认值；离线角色被置为它是合法的稳定状态。
2. 新生儿写入 `character_data` 但不进 `npc_id_got`、也不移动，所以"角色→场景名册"方向的检查必须以
   `LIVE = set(cache.npc_id_got) | {0}` 为域，不能用全体 `character_data`。
3. 当前地图更新会把已删除场景内的角色迁到区域入口或["0", "0"]；位置检查仍检查迁移后的实际状态，不预设异常成因。
4. 全部字段访问一律使用 getattr/dict.get 加默认值防御，绝不能因为老存档缺字段或类型不符而抛异常；
   若某个结构性假设本身就是不变量的一部分（例如字段类型、字段是否存在），则让比较结果记为"不变量失败"，而不是让检查器自己崩溃。
5. 依赖的 game_config 配置表在独立脚本环境下可能不可用；本模块的全部检查项均未依赖 game_config
   （PLACE-20 的服务值域上界、PLACE-11 的房间档位等均为不变量文档中给出的字面枚举值），因此无需对配置表缺失做降级处理。
"""
import collections
from typing import List

from Script.Core import cache_control
from Script.Design import map_handle
from ..check_registry import CheckFailure, register_check, make_failure

# 列表路径 -> 场景/地图键；内部用os.sep拼接，禁止自己写'/'.join
P = map_handle.get_map_system_path_str_for_list

# PLACE-20: 助理服务键 -> CSV给出的选项下标上界（据AssistantServices.csv:6-14逐项对应）
_ASSISTANT_SERVICE_MAX = {2: 1, 3: 1, 4: 3, 5: 3, 6: 3, 7: 1, 8: 1, 9: 4, 10: 1}
# PLACE-21: 期望的助理服务键全集
_ASSISTANT_SERVICE_KEYS = {2, 3, 4, 5, 6, 7, 8, 9, 10}


def _valid_scene_path(value, scene_data) -> bool:
    """
    参数:
        value: 待校验的路径字段原始值（期望是字符串列表）
        scene_data (dict): cache.scene_data
    返回值:
        bool: value是字符串列表且拼接后是scene_data合法键时为True，否则False（类型不符时直接返回False，不抛异常）
    功能:
        供多个"路径必须是现有场景"类检查复用的合法性判断，不接受空列表
    """
    return isinstance(value, list) and all(isinstance(p, str) for p in value) and P(value) in scene_data


def _valid_scene_path_or_empty(value, scene_data) -> bool:
    """
    参数:
        value: 待校验的路径字段原始值（期望是字符串列表）
        scene_data (dict): cache.scene_data
    返回值:
        bool: value是字符串列表，且为空列表或拼接后是scene_data合法键时为True
    功能:
        供移动路径类字段（允许空列表代表"当前无该状态"）复用的合法性判断
    """
    return isinstance(value, list) and all(isinstance(p, str) for p in value) and (not value or P(value) in scene_data)


def _live_ids(cache) -> set:
    """
    参数:
        cache: 全局状态缓存对象
    返回值:
        set: 在图角色id集合，等于 cache.npc_id_got 并入玩家id 0
    功能:
        计算"在图角色"域，供多条以LIVE为迭代范围的检查复用；npc_id_got缺失时按空集处理
    """
    return set(getattr(cache, "npc_id_got", set()) or set()) | {0}


def _permanent_dormitory(chara) -> str:
    """
    参数:
        chara: 角色对象
    返回值:
        str: 角色「登记宿舍」字段的当前值（临时住进客房/监牢/博士房间/舍管房/关押区休息室等特殊房间期间
        记录其原普通宿舍，住普通宿舍时恒为空）
    功能:
        读取角色的登记宿舍；兼容历史对象上可能残留的旧属性名 pre_dormitory。
        供 PLACE-28/PLACE-29 复用
    """
    return getattr(chara, "permanent_dormitory", getattr(chara, "pre_dormitory", ""))


def _offline_flags(sp_flag) -> bool:
    """
    参数:
        sp_flag: 角色的SPECIAL_FLAG对象，可能为None
    返回值:
        bool: 该角色带有被装袋/外勤中/逃跑中三个离线标记之一时为True
    功能:
        供多条检查复用的"是否带明确离线标记"判定，字段缺失时按False处理
    """
    return bool(getattr(sp_flag, "be_bagged", False) or getattr(sp_flag, "field_commission", 0) or getattr(sp_flag, "escaping", False))


@register_check("PLACE-01", "角色字典键与cid一致")
def check_character_dict_key_matches_cid() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表，character_data每个键都等于角色自身cid时返回空列表
    功能:
        校验cache.character_data的每个字典键都等于该角色对象自身的cid字段，防止场景名册、交互目标、
        助理引用等按字典键索引却指向身份不一致的对象。写入点仅character_handle.py与old_chara_to_new.py两处，
        平时零产出，是id重映射回归的探针
    """
    cache = cache_control.cache
    failures = []
    character_data = getattr(cache, "character_data", {}) or {}
    for dict_key, c in character_data.items():
        c_cid = getattr(c, "cid", None)
        if dict_key != c_cid:
            involved = [dict_key]
            if isinstance(c_cid, int) and c_cid != dict_key:
                involved.append(c_cid)
            failures.append(
                make_failure(
                    "PLACE-01",
                    "角色字典键与cid一致",
                    f"character_data字典键={dict_key}，但角色对象自身cid={c_cid}，name={getattr(c, 'name', '')}，"
                    f"adv={getattr(c, 'adv', None)}，position={getattr(c, 'position', None)}",
                    involved,
                )
            )
    return failures


@register_check("PLACE-02", "场景/地图自描述键一致")
def check_scene_and_map_self_key_consistency() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能:
        校验cache.scene_data[k].scene_path == k 且 cache.map_data[k].map_path == k。
        加载器直接以对象自身路径为键，不一致只可能来自损坏或半截迁移
    """
    cache = cache_control.cache
    failures = []
    scene_data = getattr(cache, "scene_data", {}) or {}
    for k, v in scene_data.items():
        scene_path = getattr(v, "scene_path", None)
        if k != scene_path:
            failures.append(
                make_failure(
                    "PLACE-02",
                    "场景/地图自描述键一致",
                    f"scene_data字典键={k}，但场景对象自身scene_path={scene_path}，scene_name={getattr(v, 'scene_name', '')}",
                )
            )
    map_data = getattr(cache, "map_data", {}) or {}
    for k, v in map_data.items():
        map_path = getattr(v, "map_path", None)
        if k != map_path:
            failures.append(
                make_failure(
                    "PLACE-02",
                    "场景/地图自描述键一致",
                    f"map_data字典键={k}，但地图对象自身map_path={map_path}，map_name={getattr(v, 'map_name', '')}",
                )
            )
    return failures


@register_check("PLACE-03", "场景名册id必须存在")
def check_scene_roster_ids_exist() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能:
        校验任一Scene.character_list中的id都必须是cache.character_data的键；名册全部写入点都只写已存在角色id，
        无合法悬空来源。本条应先于PLACE-05/06报告，后两者对缺失id都做了跳过处理，不重复报
    """
    cache = cache_control.cache
    failures = []
    character_data = getattr(cache, "character_data", {}) or {}
    scene_data = getattr(cache, "scene_data", {}) or {}
    for sc in scene_data.values():
        character_list = getattr(sc, "character_list", None) or []
        missing_ids = sorted(cid for cid in character_list if cid not in character_data)
        if missing_ids:
            failures.append(
                make_failure(
                    "PLACE-03",
                    "场景名册id必须存在",
                    f"场景{getattr(sc, 'scene_path', '?')}({getattr(sc, 'scene_name', '')})的character_list="
                    f"{sorted(character_list)}中，以下id不在character_data中: {missing_ids}",
                    missing_ids,
                )
            )
    return failures


@register_check("PLACE-04", "角色位置必须是现有场景")
def check_character_position_is_existing_scene() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能:
        校验cache.character_data中每个角色（全域，不限LIVE）的position拼成的路径必须是scene_data的键。
        级别为warning：只报告角色位置未落在现有场景中的事实，不推断地图迁移原因；
        当前save_handle地图更新会迁移已删除场景内的角色。若命中角色在LIVE中，应优先处理
    """
    cache = cache_control.cache
    failures = []
    character_data = getattr(cache, "character_data", {}) or {}
    scene_data = getattr(cache, "scene_data", {}) or {}
    npc_id_got = getattr(cache, "npc_id_got", set()) or set()
    for cid, c in character_data.items():
        position = getattr(c, "position", None)
        if _valid_scene_path(position, scene_data):
            continue
        behavior = getattr(c, "behavior", None)
        sp_flag = getattr(c, "sp_flag", None)
        failures.append(
            make_failure(
                "PLACE-04",
                "角色位置必须是现有场景",
                f"[warning] 角色位置未指向现有场景；角色id={cid} name={getattr(c, 'name', '')}，"
                f"position={position}，是否在npc_id_got中={cid in npc_id_got}，behavior_id={getattr(behavior, 'behavior_id', None)}，"
                f"move_src={getattr(behavior, 'move_src', None)}，move_target={getattr(behavior, 'move_target', None)}，"
                f"move_final_target={getattr(behavior, 'move_final_target', None)}，be_bagged={getattr(sp_flag, 'be_bagged', None)}，"
                f"field_commission={getattr(sp_flag, 'field_commission', None)}，escaping={getattr(sp_flag, 'escaping', None)}",
                [cid],
            )
        )
    return failures


@register_check("PLACE-05", "角色→场景方向一致")
def check_character_to_scene_direction_consistency() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能:
        校验每个在图角色（LIVE域）必须出现在自己position所指场景的character_list里。
        先验证角色存在、position合法，避免因悬空id或非法位置键而抛异常——那两类问题分别由PLACE-03、PLACE-04定位，
        本条对它们做出的是"记为不变量失败"而非"检查异常"的守卫
    """
    cache = cache_control.cache
    failures = []
    character_data = getattr(cache, "character_data", {}) or {}
    scene_data = getattr(cache, "scene_data", {}) or {}
    npc_id_got = getattr(cache, "npc_id_got", set()) or set()
    for cid in _live_ids(cache):
        c = character_data.get(cid)
        if c is None:
            failures.append(
                make_failure(
                    "PLACE-05",
                    "角色→场景方向一致",
                    f"角色id={cid}在LIVE集合(npc_id_got∪{{0}})中，但不在character_data中（悬空id，另见PLACE-03/CORE-01）",
                    [cid],
                )
            )
            continue
        position = getattr(c, "position", None)
        if not _valid_scene_path(position, scene_data):
            failures.append(
                make_failure(
                    "PLACE-05",
                    "角色→场景方向一致",
                    f"角色id={cid} name={getattr(c, 'name', '')}的position={position}不是合法场景键（另见PLACE-04），无法核对名册方向一致性",
                    [cid],
                )
            )
            continue
        path = P(position)
        sc = scene_data.get(path)
        character_list = getattr(sc, "character_list", None) or []
        if cid not in character_list:
            behavior = getattr(c, "behavior", None)
            sp_flag = getattr(c, "sp_flag", None)
            failures.append(
                make_failure(
                    "PLACE-05",
                    "角色→场景方向一致",
                    f"角色id={cid} name={getattr(c, 'name', '')}的position={position}指向场景{path}，但该场景character_list="
                    f"{sorted(character_list)}中不含该id；behavior_id={getattr(behavior, 'behavior_id', None)}，"
                    f"move_src={getattr(behavior, 'move_src', None)}，move_target={getattr(behavior, 'move_target', None)}，"
                    f"be_bagged={getattr(sp_flag, 'be_bagged', None)}，field_commission={getattr(sp_flag, 'field_commission', None)}，"
                    f"escaping={getattr(sp_flag, 'escaping', None)}，是否在npc_id_got中={cid in npc_id_got}",
                    [cid],
                )
            )
    return failures


@register_check("PLACE-06", "场景→角色方向一致")
def check_scene_to_character_direction_consistency() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能:
        校验场景名册里的每个角色，其position必须正好指回该场景，抓"旧场景没删干净"的残影，与PLACE-05互补。
        悬空id交给PLACE-03报告，本条对其做跳过而非KeyError
    """
    cache = cache_control.cache
    failures = []
    character_data = getattr(cache, "character_data", {}) or {}
    scene_data = getattr(cache, "scene_data", {}) or {}
    pl = character_data.get(0)
    bagging_id = getattr(getattr(pl, "sp_flag", None), "bagging_chara_id", None) if pl is not None else None
    # 预先构建 cid -> 所在全部场景路径的映射，避免每条失败都重新全表扫描
    cid_to_scenes = collections.defaultdict(list)
    for path, sc in scene_data.items():
        for cid in getattr(sc, "character_list", None) or []:
            cid_to_scenes[cid].append(path)
    for path, sc in scene_data.items():
        for cid in getattr(sc, "character_list", None) or []:
            c = character_data.get(cid)
            if c is None:
                continue
            position = getattr(c, "position", None)
            if isinstance(position, list) and all(isinstance(p, str) for p in position) and P(position) == path:
                continue
            behavior = getattr(c, "behavior", None)
            failures.append(
                make_failure(
                    "PLACE-06",
                    "场景→角色方向一致",
                    f"场景{path}的character_list中含角色id={cid} name={getattr(c, 'name', '')}，但其position={position}并不指回该场景，"
                    f"实际出现在的全部场景={cid_to_scenes.get(cid, [])}；behavior_id={getattr(behavior, 'behavior_id', None)}，"
                    f"move_src={getattr(behavior, 'move_src', None)}，move_target={getattr(behavior, 'move_target', None)}，"
                    f"pl.sp_flag.bagging_chara_id={bagging_id}",
                    [cid],
                )
            )
    return failures


@register_check("PLACE-07", "角色不得同时出现在多个场景")
def check_character_not_in_multiple_scenes() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能:
        校验同一角色id在所有Scene.character_list中最多出现一次。单趟Counter计数，逻辑上被PLACE-06蕴含，
        保留是为了给"分身"这种状态一句直白的失败文案
    """
    cache = cache_control.cache
    failures = []
    character_data = getattr(cache, "character_data", {}) or {}
    scene_data = getattr(cache, "scene_data", {}) or {}
    counter = collections.Counter()
    cid_to_scenes = collections.defaultdict(list)
    for path, sc in scene_data.items():
        for cid in getattr(sc, "character_list", None) or []:
            counter[cid] += 1
            cid_to_scenes[cid].append(path)
    for cid, count in counter.items():
        if count > 1:
            c = character_data.get(cid)
            failures.append(
                make_failure(
                    "PLACE-07",
                    "角色不得同时出现在多个场景",
                    f"角色id={cid} name={getattr(c, 'name', '') if c else '?'}同时出现在{count}个场景的character_list中: "
                    f"{cid_to_scenes[cid]}，position={getattr(c, 'position', None) if c else None}",
                    [cid],
                )
            )
    return failures


@register_check("PLACE-08", "场景名册只容纳在册角色/离线角色必须退出名册")
def check_scene_roster_only_registered_and_offline_must_exit() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能:
        两个方向合成一条：(a) 任何场景名册成员必须是玩家或在npc_id_got中；(b) 带明确离线标记
        （被装袋/外勤中/逃跑中）的角色必须已退出npc_id_got。不检查离线角色"当前位置"对应的名册——
        离线流程先删旧名册再把position改成["0","0"]，只查0/0会漏报真残影
    """
    cache = cache_control.cache
    failures = []
    character_data = getattr(cache, "character_data", {}) or {}
    scene_data = getattr(cache, "scene_data", {}) or {}
    npc_id_got = getattr(cache, "npc_id_got", set()) or set()

    cid_to_scenes = collections.defaultdict(list)
    for path, sc in scene_data.items():
        for cid in getattr(sc, "character_list", None) or []:
            cid_to_scenes[cid].append(path)

    # (a) 名册成员必须是玩家或在npc_id_got中
    for cid, paths in cid_to_scenes.items():
        if cid != 0 and cid not in npc_id_got:
            c = character_data.get(cid)
            sp_flag = getattr(c, "sp_flag", None) if c else None
            unnormal_flag = getattr(sp_flag, "unnormal_flag", None)
            failures.append(
                make_failure(
                    "PLACE-08",
                    "场景名册只容纳在册角色/离线角色必须退出名册",
                    f"角色id={cid} name={getattr(c, 'name', '') if c else '?'}出现在场景名册{paths}中，但既非玩家也不在npc_id_got中；"
                    f"position={getattr(c, 'position', None) if c else None}，be_bagged={getattr(sp_flag, 'be_bagged', None)}，"
                    f"field_commission={getattr(sp_flag, 'field_commission', None)}，escaping={getattr(sp_flag, 'escaping', None)}，"
                    f"vistor={getattr(sp_flag, 'vistor', None)}，unnormal_flag.mask={getattr(unnormal_flag, 'mask', None)}",
                    [cid],
                )
            )

    # (b) 带明确离线标记的角色必须已退出npc_id_got
    for cid, c in character_data.items():
        sp_flag = getattr(c, "sp_flag", None)
        if _offline_flags(sp_flag) and cid in npc_id_got:
            failures.append(
                make_failure(
                    "PLACE-08",
                    "场景名册只容纳在册角色/离线角色必须退出名册",
                    f"角色id={cid} name={getattr(c, 'name', '')}带有离线标记(be_bagged={getattr(sp_flag, 'be_bagged', None)}，"
                    f"field_commission={getattr(sp_flag, 'field_commission', None)}，escaping={getattr(sp_flag, 'escaping', None)})，"
                    f"但仍在npc_id_got中；position={getattr(c, 'position', None)}，所在场景名册={cid_to_scenes.get(cid, [])}，"
                    f"vistor={getattr(sp_flag, 'vistor', None)}",
                    [cid],
                )
            )
    return failures


@register_check("PLACE-09", "空房间不该锁着门")
def check_locked_room_not_empty() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能:
        校验close_flag != 0的场景其character_list不应为空。关门只由屋内角色发起，正常离开时会解锁；
        "空着还锁"意味着有人以非移动方式离场（例如在屋内直接离线）留下的死锁
    """
    cache = cache_control.cache
    failures = []
    scene_data = getattr(cache, "scene_data", {}) or {}
    for sc in scene_data.values():
        close_flag = getattr(sc, "close_flag", 0)
        character_list = getattr(sc, "character_list", None) or []
        if close_flag != 0 and len(character_list) == 0:
            failures.append(
                make_failure(
                    "PLACE-09",
                    "空房间不该锁着门",
                    f"场景{getattr(sc, 'scene_path', '?')}({getattr(sc, 'scene_name', '')})的close_flag={close_flag}非0，"
                    f"但character_list为空；close_type={getattr(sc, 'close_type', None)}，scene_tag={getattr(sc, 'scene_tag', None)}，"
                    f"room_area={getattr(sc, 'room_area', None)}",
                )
            )
    return failures


@register_check("PLACE-10", "门类型与门状态枚举合法")
def check_door_type_and_flag_enum_valid() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能:
        校验close_type ∈ {0,1,2}（无门/普通门/隔间门），且close_flag只能是0或本场景的close_type。
        取close_flag in {0, close_type}而非close_flag<=close_type，避免放过close_type==2且close_flag==1的错位
    """
    cache = cache_control.cache
    failures = []
    scene_data = getattr(cache, "scene_data", {}) or {}
    for sc in scene_data.values():
        close_type = getattr(sc, "close_type", 0)
        close_flag = getattr(sc, "close_flag", 0)
        if close_type not in (0, 1, 2) or close_flag not in (0, close_type):
            failures.append(
                make_failure(
                    "PLACE-10",
                    "门类型与门状态枚举合法",
                    f"场景{getattr(sc, 'scene_path', '?')}({getattr(sc, 'scene_name', '')})的close_type={close_type}，"
                    f"close_flag={close_flag}不满足close_type∈{{0,1,2}}且close_flag∈{{0,close_type}}；"
                    f"room_area={getattr(sc, 'room_area', None)}，character_list={sorted(getattr(sc, 'character_list', None) or [])}",
                )
            )
    return failures


@register_check("PLACE-11", "房间容量档位枚举合法")
def check_room_area_enum_valid() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能:
        校验room_area只能是0/1/2/3（对应满员判定的10/50/100/9999四档）。不检查"人数<=容量"——
        容量只是常规寻路准入策略，玩家豁免、character_move_scene与handle_chara_on_line均不查容量，合法越界可达
    """
    cache = cache_control.cache
    failures = []
    scene_data = getattr(cache, "scene_data", {}) or {}
    for sc in scene_data.values():
        room_area = getattr(sc, "room_area", 0)
        if room_area not in (0, 1, 2, 3):
            failures.append(
                make_failure(
                    "PLACE-11",
                    "房间容量档位枚举合法",
                    f"场景{getattr(sc, 'scene_path', '?')}({getattr(sc, 'scene_name', '')})的room_area={room_area}不在合法枚举{{0,1,2,3}}中；"
                    f"当前人数={len(getattr(sc, 'character_list', None) or [])}",
                )
            )
    return failures


@register_check("PLACE-12", "移动路径字段必须是现有场景")
def check_move_path_fields_are_existing_scenes() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能:
        校验behavior.move_src/move_target/move_final_target只要非空，就必须拼成cache.scene_data的合法键；
        空列表合法（寻路失败时会先写behavior_id=move再写空move_target）。级别为warning：
        唯一已知命中源与PLACE-04同因（老存档地图更新后场景键被删却未迁移角色）
    """
    cache = cache_control.cache
    failures = []
    character_data = getattr(cache, "character_data", {}) or {}
    scene_data = getattr(cache, "scene_data", {}) or {}
    for cid, c in character_data.items():
        behavior = getattr(c, "behavior", None)
        if behavior is None:
            continue
        for field_name in ("move_src", "move_target", "move_final_target"):
            value = getattr(behavior, field_name, [])
            if _valid_scene_path_or_empty(value, scene_data):
                continue
            failures.append(
                make_failure(
                    "PLACE-12",
                    "移动路径字段必须是现有场景",
                    f"[warning] 角色id={cid} name={getattr(c, 'name', '')}的behavior.{field_name}={value}既非空列表也不是合法场景路径；"
                    f"position={getattr(c, 'position', None)}，behavior_id={getattr(behavior, 'behavior_id', None)}，"
                    f"move_src={getattr(behavior, 'move_src', None)}，move_target={getattr(behavior, 'move_target', None)}，"
                    f"move_final_target={getattr(behavior, 'move_final_target', None)}，start_time={getattr(behavior, 'start_time', None)}，"
                    f"duration={getattr(behavior, 'duration', None)}",
                    [cid],
                )
            )
    return failures


@register_check("PLACE-13", "移动历史长度与内容合法")
def check_past_move_position_list_valid() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能:
        校验action_info.past_move_position_list最多10条，每条都必须是合法场景路径。该字段只在标准移动入口
        追加、超10立即pop(0)，长度超限一定是绕过character_move_scene的写入
    """
    cache = cache_control.cache
    failures = []
    character_data = getattr(cache, "character_data", {}) or {}
    scene_data = getattr(cache, "scene_data", {}) or {}
    for cid, c in character_data.items():
        action_info = getattr(c, "action_info", None)
        past_list = getattr(action_info, "past_move_position_list", None)
        if not isinstance(past_list, list):
            continue
        bad_items = [p for p in past_list if not _valid_scene_path(p, scene_data)]
        if len(past_list) > 10 or bad_items:
            failures.append(
                make_failure(
                    "PLACE-13",
                    "移动历史长度与内容合法",
                    f"角色id={cid} name={getattr(c, 'name', '')}的action_info.past_move_position_list长度={len(past_list)}"
                    f"（应≤10），其中非法项={bad_items}；position={getattr(c, 'position', None)}",
                    [cid],
                )
            )
    return failures


@register_check("PLACE-14", "收藏地点必须是合法场景")
def check_collect_position_list_valid() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能:
        校验cache.collect_position_list每一项都是场景路径列表，必须存在于cache.scene_data；
        否则地图收藏面板点一下就会跳进不存在的场景
    """
    cache = cache_control.cache
    failures = []
    scene_data = getattr(cache, "scene_data", {}) or {}
    collect_list = getattr(cache, "collect_position_list", None)
    if not isinstance(collect_list, list):
        return failures
    pl = (getattr(cache, "character_data", {}) or {}).get(0)
    bad_items = [pos for pos in collect_list if not _valid_scene_path(pos, scene_data)]
    if bad_items:
        failures.append(
            make_failure(
                "PLACE-14",
                "收藏地点必须是合法场景",
                f"cache.collect_position_list中存在非法场景路径: {bad_items}；完整列表长度={len(collect_list)}，"
                f"玩家当前position={getattr(pl, 'position', None)}",
            )
        )
    return failures


@register_check("PLACE-15", "宿舍字段必须是合法场景或哨兵值")
def check_dormitory_field_valid_or_sentinel() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能:
        校验LIVE域内角色的dormitory（场景路径字符串）只允许是cache.scene_data的键，或未分配哨兵""/"无"。
        两个哨兵都必须放行：宿舍管理允许在线角色暂时落在""空白位，初始化与访客分房合法使用"无"
    """
    cache = cache_control.cache
    failures = []
    character_data = getattr(cache, "character_data", {}) or {}
    scene_data = getattr(cache, "scene_data", {}) or {}
    rhodes_island = getattr(cache, "rhodes_island", None)
    visitor_info = getattr(rhodes_island, "visitor_info", {}) or {}
    for cid in _live_ids(cache):
        c = character_data.get(cid)
        if c is None:
            continue
        dormitory = getattr(c, "dormitory", "")
        if dormitory in ("", "无") or dormitory in scene_data:
            continue
        work = getattr(c, "work", None)
        failures.append(
            make_failure(
                "PLACE-15",
                "宿舍字段必须是合法场景或哨兵值",
                f"角色id={cid} name={getattr(c, 'name', '')}的dormitory={dormitory!r}既不是合法场景键也不是哨兵值('' / '无')；"
                f"permanent_dormitory={getattr(c, 'permanent_dormitory', None)!r}，position={getattr(c, 'position', None)}，"
                f"work_type={getattr(work, 'work_type', None)}，是否为访客={cid in visitor_info}",
                [cid],
            )
        )
    return failures


@register_check("PLACE-16", "交互对象id必须存在")
def check_target_character_id_exists() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能:
        校验每个角色的target_character_id必须是cache.character_data的键。自指（==cid）是"无交互对象"的
        默认值，合法；对NPC而言==0表示"目标是玩家"，同样合法（settle_behavior.py据此互换双方结算数据）
    """
    cache = cache_control.cache
    failures = []
    character_data = getattr(cache, "character_data", {}) or {}
    for cid, c in character_data.items():
        target_id = getattr(c, "target_character_id", cid)
        if target_id not in character_data:
            behavior = getattr(c, "behavior", None)
            sp_flag = getattr(c, "sp_flag", None)
            failures.append(
                make_failure(
                    "PLACE-16",
                    "交互对象id必须存在",
                    f"角色id={cid} name={getattr(c, 'name', '')}的target_character_id={target_id}在character_data中不存在"
                    f"（自指=无交互对象、0=以玩家为交互对象均合法，此处既非自指也非现存id）；"
                    f"behavior_id={getattr(behavior, 'behavior_id', None)}，is_h={getattr(sp_flag, 'is_h', None)}，"
                    f"position={getattr(c, 'position', None)}",
                    [cid],
                )
            )
    return failures


@register_check("PLACE-17", "H状态角色的交互对象必须同场")
def check_h_state_target_same_scene() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能:
        校验LIVE域内处于sp_flag.is_h的角色，其交互对象必须存在且与自己position相同。不放宽到
        "所有角色的持久目标都必须同场"——引擎明确容忍普通目标离场，从不重置target_character_id。
        级别为warning：H结束到NPC AI清理is_h之间存在一拍误报窗口
    """
    cache = cache_control.cache
    failures = []
    character_data = getattr(cache, "character_data", {}) or {}
    pl = character_data.get(0)
    bagging_id = getattr(getattr(pl, "sp_flag", None), "bagging_chara_id", None) if pl is not None else None
    for cid in _live_ids(cache):
        c = character_data.get(cid)
        if c is None:
            continue
        sp_flag = getattr(c, "sp_flag", None)
        if not getattr(sp_flag, "is_h", False):
            continue
        target_id = getattr(c, "target_character_id", cid)
        target = character_data.get(target_id)
        if target is not None and getattr(target, "position", None) == getattr(c, "position", None):
            continue
        behavior = getattr(c, "behavior", None)
        target_desc = f"（目标name={getattr(target, 'name', '')}，target.position={getattr(target, 'position', None)}）" if target is not None else "，目标在character_data中不存在"
        failures.append(
            make_failure(
                "PLACE-17",
                "H状态角色的交互对象必须同场",
                f"[warning] 角色id={cid} name={getattr(c, 'name', '')}处于sp_flag.is_h=True，其target_character_id={target_id}"
                f"{target_desc}，自身position={getattr(c, 'position', None)}；behavior_id={getattr(behavior, 'behavior_id', None)}，"
                f"unconscious_h={getattr(sp_flag, 'unconscious_h', None)}，pl.sp_flag.bagging_chara_id={bagging_id}",
                [cid] + ([target_id] if target is not None else []),
            )
        )
    return failures


@register_check("PLACE-18", "助理字段只属于玩家")
def check_assistant_field_only_for_player() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能:
        校验只有id 0可以有非零assistant_character_id；NPC上非零都是脏数据（面板与前提只读玩家那一份，
        NPC上的值永远失效却会随存档迁移传播）
    """
    cache = cache_control.cache
    failures = []
    character_data = getattr(cache, "character_data", {}) or {}
    pl = character_data.get(0)
    pl_aid = getattr(pl, "assistant_character_id", None) if pl is not None else None
    for cid, c in character_data.items():
        if cid == 0:
            continue
        aid = getattr(c, "assistant_character_id", 0)
        if aid != 0:
            failures.append(
                make_failure(
                    "PLACE-18",
                    "助理字段只属于玩家",
                    f"非玩家角色id={cid} name={getattr(c, 'name', '')}的assistant_character_id={aid}非0（该字段仅玩家使用）；"
                    f"玩家自身assistant_character_id={pl_aid}",
                    [cid],
                )
            )
    return failures


@register_check("PLACE-19", "当前助理必须有效且在线")
def check_current_assistant_valid_and_online() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能:
        校验pl.assistant_character_id非0时，该id必须存在于character_data、在npc_id_got中、未死亡、
        且不带任何离线标记。短路顺序：先查存在再解引用，避免持有id损坏时抛KeyError
    """
    cache = cache_control.cache
    failures = []
    character_data = getattr(cache, "character_data", {}) or {}
    npc_id_got = getattr(cache, "npc_id_got", set()) or set()
    pl = character_data.get(0)
    if pl is None:
        return failures
    aid = getattr(pl, "assistant_character_id", 0)
    if aid == 0:
        return failures
    assistant = character_data.get(aid)
    if assistant is None:
        failures.append(
            make_failure(
                "PLACE-19",
                "当前助理必须有效且在线",
                f"玩家assistant_character_id={aid}指向的角色不在character_data中；玩家position={getattr(pl, 'position', None)}",
                [aid],
            )
        )
        return failures
    in_got = aid in npc_id_got
    dead = getattr(assistant, "dead", False)
    sp_flag = getattr(assistant, "sp_flag", None)
    offline = _offline_flags(sp_flag)
    if not (in_got and not dead and not offline):
        failures.append(
            make_failure(
                "PLACE-19",
                "当前助理必须有效且在线",
                f"玩家当前助理id={aid} name={getattr(assistant, 'name', '')} position={getattr(assistant, 'position', None)}，"
                f"是否在npc_id_got中={in_got}，dead={dead}，be_bagged={getattr(sp_flag, 'be_bagged', None)}，"
                f"field_commission={getattr(sp_flag, 'field_commission', None)}，escaping={getattr(sp_flag, 'escaping', None)}，"
                f"玩家position={getattr(pl, 'position', None)}",
                [aid],
            )
        )
    return failures


@register_check("PLACE-20", "助理服务值域合法")
def check_assistant_services_value_range() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能:
        校验assistant_services中每个已知服务键的值不得超过CSV给出的选项下标上界，且不得为负。
        不排除bool值——服务2的写入点本身就是Python bool，True==1语义有效，消费端做的都是真值判断
    """
    cache = cache_control.cache
    failures = []
    character_data = getattr(cache, "character_data", {}) or {}
    pl = character_data.get(0)
    pl_aid = getattr(pl, "assistant_character_id", None) if pl is not None else None
    for cid, c in character_data.items():
        services = getattr(c, "assistant_services", None)
        if not isinstance(services, dict):
            continue
        out_of_range = {k: v for k, v in services.items() if k in _ASSISTANT_SERVICE_MAX and not (0 <= v <= _ASSISTANT_SERVICE_MAX[k])}
        if out_of_range:
            failures.append(
                make_failure(
                    "PLACE-20",
                    "助理服务值域合法",
                    f"角色id={cid} name={getattr(c, 'name', '')}的assistant_services中以下键值超出合法范围: {out_of_range}"
                    f"（上界表{_ASSISTANT_SERVICE_MAX}），完整assistant_services={services}，是否为当前助理={cid == pl_aid}",
                    [cid],
                )
            )
    return failures


@register_check("PLACE-21", "助理服务键集完整")
def check_assistant_services_key_set_complete() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能:
        校验每个角色的assistant_services应恰好包含服务键2..10。级别为warning：assistant_panel.py与
        handle_premise_assistant.py均用setdefault兜底缺键，老存档迁移可能暂时缺键
    """
    cache = cache_control.cache
    failures = []
    character_data = getattr(cache, "character_data", {}) or {}
    for cid, c in character_data.items():
        services = getattr(c, "assistant_services", None)
        if not isinstance(services, dict):
            continue
        keys = set(services.keys())
        if keys != _ASSISTANT_SERVICE_KEYS:
            failures.append(
                make_failure(
                    "PLACE-21",
                    "助理服务键集完整",
                    f"[warning] 角色id={cid} name={getattr(c, 'name', '')}的assistant_services键集合与期望不符："
                    f"缺失键={sorted(_ASSISTANT_SERVICE_KEYS - keys)}，多余键={sorted(keys - _ASSISTANT_SERVICE_KEYS)}，"
                    f"完整assistant_services={services}",
                    [cid],
                )
            )
    return failures


@register_check("PLACE-22", "同居服务与宿舍一致")
def check_cohabitation_service_matches_dormitory() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能:
        校验当前助理开启服务7（同居）时，其宿舍应为"中枢/博士房间"。级别为warning。判定范围有两处限制：
        当前助理同时任命为监狱长(work_type==191)是合法状态，予以豁免；不要求permanent_dormitory非空
        （Character.dormitory初值即""，该子句守不住任何真实约束）
    """
    cache = cache_control.cache
    failures = []
    character_data = getattr(cache, "character_data", {}) or {}
    pl = character_data.get(0)
    if pl is None:
        return failures
    aid = getattr(pl, "assistant_character_id", 0)
    if aid == 0:
        return failures
    assistant = character_data.get(aid)
    if assistant is None:
        return failures  # 助理id本身无效由PLACE-19负责报告，本条不重复报
    services = getattr(assistant, "assistant_services", None) or {}
    if services.get(7, 0) != 1:
        return failures
    work = getattr(assistant, "work", None)
    if getattr(work, "work_type", None) == 191:
        return failures  # 豁免监狱长：任命为监狱长会改宿舍但不清同居服务位，是合法且持久的状态
    expected_dormitory = P(["中枢", "博士房间"])
    dormitory = getattr(assistant, "dormitory", None)
    if dormitory != expected_dormitory:
        rhodes_island = getattr(cache, "rhodes_island", None)
        failures.append(
            make_failure(
                "PLACE-22",
                "同居服务与宿舍一致",
                f"[warning] 当前助理id={aid} name={getattr(assistant, 'name', '')}已开启同居服务(assistant_services[7]=1)，"
                f"但dormitory={dormitory}（期望{expected_dormitory}），permanent_dormitory={getattr(assistant, 'permanent_dormitory', None)}，"
                f"work_type={getattr(work, 'work_type', None)}，current_warden_id={getattr(rhodes_island, 'current_warden_id', None)}",
                [aid],
            )
        )
    return failures


@register_check("PLACE-23", "跟随模式取值合法")
def check_follow_mode_value_valid() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能:
        校验sp_flag.is_follow只能取0-4。debug_panel.py可写任意值，调试会话下本条必噪，故cache.debug_mode
        为True时直接跳过整条检查
    """
    cache = cache_control.cache
    if bool(getattr(cache, "debug_mode", False)):
        return []
    failures = []
    character_data = getattr(cache, "character_data", {}) or {}
    pl = character_data.get(0)
    pl_aid = getattr(pl, "assistant_character_id", 0) if pl is not None else 0
    for cid, c in character_data.items():
        sp_flag = getattr(c, "sp_flag", None)
        is_follow = getattr(sp_flag, "is_follow", 0)
        if is_follow not in (0, 1, 2, 3, 4):
            behavior = getattr(c, "behavior", None)
            services = getattr(c, "assistant_services", None) or {}
            failures.append(
                make_failure(
                    "PLACE-23",
                    "跟随模式取值合法",
                    f"角色id={cid} name={getattr(c, 'name', '')}的sp_flag.is_follow={is_follow}超出合法范围[0,4]；"
                    f"是否为当前助理={cid == pl_aid}，assistant_services[2]={services.get(2)}，behavior_id={getattr(behavior, 'behavior_id', None)}",
                    [cid],
                )
            )
    return failures


@register_check("PLACE-24", "玩家不跟随自己")
def check_player_not_following_self() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能:
        校验id 0的sp_flag.is_follow必须为0。跟随语义是NPC跟随玩家，玩家带上跟随位没有任何合法产生路径
        （唯一能写坏的是debug面板，这正是本条想抓的对象），cache.debug_mode为True时将消息降级为warning
    """
    cache = cache_control.cache
    failures = []
    character_data = getattr(cache, "character_data", {}) or {}
    pl = character_data.get(0)
    if pl is None:
        return failures
    sp_flag = getattr(pl, "sp_flag", None)
    is_follow = getattr(sp_flag, "is_follow", 0)
    if is_follow != 0:
        debug_mode = bool(getattr(cache, "debug_mode", False))
        prefix = "[warning] （调试模式下降级，疑似debug面板写入）" if debug_mode else ""
        behavior = getattr(pl, "behavior", None)
        failures.append(
            make_failure(
                "PLACE-24",
                "玩家不跟随自己",
                f"{prefix}玩家(id 0)的sp_flag.is_follow={is_follow}，应恒为0；position={getattr(pl, 'position', None)}，"
                f"behavior_id={getattr(behavior, 'behavior_id', None)}，move_target={getattr(behavior, 'move_target', None)}，"
                f"debug_mode={debug_mode}",
                [0],
            )
        )
    return failures


@register_check("PLACE-25", "跟随者必须在册、活着、在线")
def check_follower_must_be_registered_alive_online() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能:
        校验sp_flag.is_follow != 0的角色必须是非玩家、在npc_id_got中、未死亡、且不带离线标记。级别为warning：
        访客到期离开的手写下线流程不清is_follow，"一键全跟随"又不过滤访客，可组合出持久的遗留状态，
        属遗留垃圾而非崩溃源（角色若回归，handle_chara_on_line会整体重建sp_flag）
    """
    cache = cache_control.cache
    failures = []
    character_data = getattr(cache, "character_data", {}) or {}
    npc_id_got = getattr(cache, "npc_id_got", set()) or set()
    rhodes_island = getattr(cache, "rhodes_island", None)
    visitor_info = getattr(rhodes_island, "visitor_info", {}) or {}
    for cid, c in character_data.items():
        sp_flag = getattr(c, "sp_flag", None)
        is_follow = getattr(sp_flag, "is_follow", 0)
        if is_follow == 0:
            continue
        dead = getattr(c, "dead", False)
        offline = _offline_flags(sp_flag)
        in_got = cid in npc_id_got
        if cid != 0 and in_got and not dead and not offline:
            continue
        vistor = getattr(sp_flag, "vistor", None)
        known_bug_note = "；已知缺陷：访客到期离开(invite_visitor_panel.visitor_leave)未清is_follow，若vistor==2大概率是该已知路径" if vistor == 2 else ""
        failures.append(
            make_failure(
                "PLACE-25",
                "跟随者必须在册、活着、在线",
                f"[warning] 角色id={cid} name={getattr(c, 'name', '')}的sp_flag.is_follow={is_follow}非0，但是否为玩家自身={cid == 0}，"
                f"是否在npc_id_got中={in_got}，dead={dead}，position={getattr(c, 'position', None)}，"
                f"be_bagged={getattr(sp_flag, 'be_bagged', None)}，field_commission={getattr(sp_flag, 'field_commission', None)}，"
                f"escaping={getattr(sp_flag, 'escaping', None)}，vistor={vistor}，是否在rhodes_island.visitor_info中={cid in visitor_info}"
                f"{known_bug_note}",
                [cid],
            )
        )
    return failures


@register_check("PLACE-26", "跟随/助理身份必须反映在异常位缓存中")
def check_follow_assistant_reflected_in_unnormal_flag() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能:
        校验sp_flag.unnormal_flag第3位（高优先级AI：助理、跟随、体检）缓存：若角色正在跟随或就是助理，
        而该位已被标记为"已知"却是"正常"，说明缓存过期。单向检查，只查"该异常却标了正常"，
        不加反向断言（体检也会置位，属额外置位原因，不构成反向误报）
    """
    cache = cache_control.cache
    failures = []
    character_data = getattr(cache, "character_data", {}) or {}
    pl = character_data.get(0)
    pl_aid = getattr(pl, "assistant_character_id", 0) if pl is not None else 0
    for cid in _live_ids(cache):
        c = character_data.get(cid)
        if c is None:
            continue
        sp_flag = getattr(c, "sp_flag", None)
        is_follow = getattr(sp_flag, "is_follow", 0)
        if not (bool(is_follow) or cid == pl_aid):
            continue
        unnormal_flag = getattr(sp_flag, "unnormal_flag", None)
        if unnormal_flag is None:
            continue
        is_known = unnormal_flag.is_known(3)
        checked = unnormal_flag.check(3)
        if is_known and not checked:
            failures.append(
                make_failure(
                    "PLACE-26",
                    "跟随/助理身份必须反映在异常位缓存中",
                    f"角色id={cid} name={getattr(c, 'name', '')}正在跟随(is_follow={is_follow})或是当前助理({cid == pl_aid})，"
                    f"但sp_flag.unnormal_flag第3位已知却标记为正常(mask={getattr(unnormal_flag, 'mask', None)}，"
                    f"known_bits={getattr(unnormal_flag, 'known_bits', None)})，AI可能用旧结论调度该角色",
                    [cid],
                )
            )
    return failures


@register_check("PLACE-27", "装袋搬运双向一致")
def check_bagging_consistency() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能:
        校验"装袋搬走"状态的双向一致性：(1) 只有玩家(id 0)可以持有非零bagging_chara_id；
        (2) 全体be_bagged=True的角色集合必须恰好等于{玩家当前装袋的角色id}（未装袋时为空集）；
        (3) 被装袋角色必须已完成离线三件套：退出npc_id_got、position归为["0","0"]、不在任何场景名册中。
        "position==['0','0']"单独不具区分力（那是真实场景"罗德岛出口"），与"不在任何场景名册"合取后才有效
    """
    cache = cache_control.cache
    failures = []
    character_data = getattr(cache, "character_data", {}) or {}
    scene_data = getattr(cache, "scene_data", {}) or {}
    npc_id_got = getattr(cache, "npc_id_got", set()) or set()
    pl = character_data.get(0)
    if pl is None:
        return failures

    # (1) 非玩家角色不得持有bagging_chara_id
    for cid, c in character_data.items():
        if cid == 0:
            continue
        sp_flag = getattr(c, "sp_flag", None)
        bagging_id = getattr(sp_flag, "bagging_chara_id", 0)
        if bagging_id != 0:
            failures.append(
                make_failure(
                    "PLACE-27",
                    "装袋搬运双向一致",
                    f"非玩家角色id={cid} name={getattr(c, 'name', '')}的sp_flag.bagging_chara_id={bagging_id}非0，只有玩家可持有该字段",
                    [cid],
                )
            )

    pl_sp_flag = getattr(pl, "sp_flag", None)
    pl_bagging_id = getattr(pl_sp_flag, "bagging_chara_id", 0) or 0

    # (2) be_bagged集合必须恰好等于{玩家当前装袋对象}
    be_bagged_ids = {cid for cid, c in character_data.items() if getattr(getattr(c, "sp_flag", None), "be_bagged", False)}
    expected_ids = {pl_bagging_id} if pl_bagging_id else set()
    if be_bagged_ids != expected_ids:
        failures.append(
            make_failure(
                "PLACE-27",
                "装袋搬运双向一致",
                f"玩家sp_flag.bagging_chara_id={pl_bagging_id}，理论被搬者集合应为{sorted(expected_ids)}，但实际be_bagged=True的角色"
                f"集合为{sorted(be_bagged_ids)}（name: {[(cid, getattr(character_data.get(cid), 'name', '?')) for cid in sorted(be_bagged_ids)]}）",
                sorted(be_bagged_ids | expected_ids),
            )
        )

    # (3) 被装袋角色必须已完成离线三件套
    if pl_bagging_id:
        bid = pl_bagging_id
        target = character_data.get(bid)
        if target is None:
            failures.append(
                make_failure(
                    "PLACE-27",
                    "装袋搬运双向一致",
                    f"玩家sp_flag.bagging_chara_id={bid}指向的角色不在character_data中，pl.position={getattr(pl, 'position', None)}",
                    [bid],
                )
            )
        else:
            target_sp_flag = getattr(target, "sp_flag", None)
            be_bagged = getattr(target_sp_flag, "be_bagged", False)
            in_got = bid in npc_id_got
            position = getattr(target, "position", None)
            scenes_with_bid = [p for p, s in scene_data.items() if bid in (getattr(s, "character_list", None) or [])]
            if not (be_bagged and not in_got and position == ["0", "0"] and not scenes_with_bid):
                failures.append(
                    make_failure(
                        "PLACE-27",
                        "装袋搬运双向一致",
                        f"被装袋角色id={bid} name={getattr(target, 'name', '')}未完成离线三件套：be_bagged={be_bagged}，"
                        f"是否仍在npc_id_got中={in_got}，position={position}，仍出现在场景名册={scenes_with_bid}"
                        f"（已知隐患：Script/Settle/default.py的handle_t_be_bagged效果id 451在Behavior_Effect.csv中无引用，是死代码）",
                        [bid],
                    )
                )
    return failures


@register_check("PLACE-28", "登记宿舍不得停留在与当前宿舍相同的值")
def check_permanent_dormitory_not_equal_to_dormitory() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能:
        校验LIVE域内角色的「登记宿舍」（双名兼容：permanent_dormitory/pre_dormitory）非空时不得等于
        当前dormitory。该字段语义是"临时住进客房/监牢/博士房间/舍管房/关押区休息室期间记录其原普通宿舍"，
        住普通宿舍时恒为空；健康存档里该字段只在"正住在特殊房间"这一瞬间与dormitory不同，一旦离开特殊房间
        就应被game既有的四处恢复点写回dormitory并清空自身，因此健康存档里它不会停留在与dormitory相同的值。
        级别为warning：触发源仅为历史旧档残留值
    """
    cache = cache_control.cache
    failures = []
    character_data = getattr(cache, "character_data", {}) or {}
    for cid in _live_ids(cache):
        c = character_data.get(cid)
        if c is None:
            continue
        permanent = _permanent_dormitory(c)
        dormitory = getattr(c, "dormitory", "")
        if permanent != "" and permanent == dormitory:
            failures.append(
                make_failure(
                    "PLACE-28",
                    "登记宿舍不得停留在与当前宿舍相同的值",
                    f"[warning] 角色id={cid} name={getattr(c, 'name', '')}的登记宿舍(permanent_dormitory/pre_dormitory)"
                    f"={permanent!r}与当前dormitory相同，说明离开特殊房间时的恢复点未清空该字段；"
                    f"position={getattr(c, 'position', None)}",
                    [cid],
                )
            )
    return failures


@register_check("PLACE-29", "登记宿舍非空时必须是合法的普通宿舍房间")
def check_permanent_dormitory_is_valid_normal_room() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能:
        校验LIVE域内角色的「登记宿舍」（双名兼容）非空且不等于当前dormitory时（与PLACE-28互斥的另一种
        失败模式），其值必须是一间真实的、当前开放的普通宿舍房间——用
        Script/System/Dormitory_System/common.py的get_open_dormitory_room_occupancy()（函数级导入，避免
        加载顺序问题）取得的开放宿舍占用表判定，不接受特殊房间（客房/监牢/博士房间/舍管房/关押区休息室）。
        健康存档里该字段只在角色临时住进特殊房间前，由register_permanent_dormitory()从其原本的普通宿舍写入，
        因此恒落在开放宿舍池内；级别为warning：触发源仅为历史旧档残留值。若某普通宿舍房间在写入之后被玩家
        降级宿舍区等级而关闭，也会落入本条（占用表只统计当前开放房间），这是可接受的边缘噪声，不构成放宽检查的理由
    """
    cache = cache_control.cache
    failures = []
    character_data = getattr(cache, "character_data", {}) or {}
    from Script.System.Dormitory_System import common as dormitory_common

    normal_rooms = set(dormitory_common.get_open_dormitory_room_occupancy())
    for cid in _live_ids(cache):
        c = character_data.get(cid)
        if c is None:
            continue
        permanent = _permanent_dormitory(c)
        dormitory = getattr(c, "dormitory", "")
        if permanent == "" or permanent == dormitory:
            continue
        if permanent not in normal_rooms:
            failures.append(
                make_failure(
                    "PLACE-29",
                    "登记宿舍非空时必须是合法的普通宿舍房间",
                    f"[warning] 角色id={cid} name={getattr(c, 'name', '')}的登记宿舍(permanent_dormitory/pre_dormitory)"
                    f"={permanent!r}不在开放普通宿舍房间池中(len={len(normal_rooms)})，当前dormitory={dormitory!r}，"
                    f"position={getattr(c, 'position', None)}",
                    [cid],
                )
            )
    return failures


# 教育场景只校验静态标签和名称，不以设施开放状态筛选。
def _education_tags():
    """参数: 无；返回值: set[str]；功能: 从教育常量取班级教室与体育场地标签，不硬编码房间数量。"""
    from Script.System.Education_System import education_constant

    return set(education_constant.CLASSROOM_TAG_BY_COURSE_TYPE.values()) | {data[0] for data in education_constant.PE_PLACE_DATA.values()}


def _has_scene_tag(scene, tag):
    """参数: scene(场景对象)、tag(str)；返回值: bool；功能: 防御式读取场景标签列表。"""
    tags = getattr(scene, "scene_tag", None)
    return isinstance(tags, (list, tuple, set)) and tag in tags


@register_check("PLACE-30", "教室标签索引")
def check_place_30() -> List[CheckFailure]:
    """参数: 无；返回值: List[CheckFailure]；功能: 教育标签索引内路径须存在且带该标签，场景带标签时也须出现在索引中。"""
    cache = cache_control.cache
    from Script.Core import constant

    scenes = getattr(cache, "scene_data", None)
    places = getattr(constant, "place_data", None)
    if not isinstance(scenes, dict) or not isinstance(places, dict):
        return []
    failures = []
    for tag in sorted(_education_tags()):
        paths = places.get(tag, [])
        if not isinstance(paths, (list, tuple, set)):
            continue
        for index, path in enumerate(paths):
            if not isinstance(path, str) or path not in scenes or not _has_scene_tag(scenes[path], tag):
                failures.append(make_failure("PLACE-30", "教室标签索引", f"cid=None key=place_data[{tag!r}][{index}] value={path!r}；路径不存在或场景未带{tag!r}标签", []))
        for path, scene in scenes.items():
            if _has_scene_tag(scene, tag) and path not in paths:
                failures.append(make_failure("PLACE-30", "教室标签索引", f"cid=None key=scene_data[{path!r}].scene_tag value={getattr(scene, 'scene_tag', None)!r}；place_data[{tag!r}]漏列此路径", []))
    return failures


def _check_room_name(scenes, tags, name, cid, key, failures):
    """参数: scenes(dict)、tags(标签集合)、name(场景名)、cid(角色id或None)、key(str)、failures(list)；返回值: None；功能: 检查一次名称引用是否唯一解析。"""
    paths = [path for path, scene in scenes.items() if isinstance(name, str) and getattr(scene, "scene_name", None) == name and any(_has_scene_tag(scene, tag) for tag in tags)]
    if len(paths) != 1:
        failures.append(
            make_failure("PLACE-31", "教室名称无歧义", f"cid={cid!r} key={key} value={name!r}；匹配场景数={len(paths)}，路径={paths!r}，标签={sorted(tags)!r}", [cid] if type(cid) is int else [])
        )


@register_check("PLACE-31", "教室名称无歧义")
def check_place_31() -> List[CheckFailure]:
    """参数: 无；返回值: List[CheckFailure]；功能: 全局课表与个人0–3课型的场景名须唯一对应匹配教育标签的场景，未开放或关闭不报错。"""
    cache = cache_control.cache
    from Script.System.Education_System import education_constant

    scenes = getattr(cache, "scene_data", None)
    if not isinstance(scenes, dict):
        return []
    failures = []
    classroom_tags = set(education_constant.CLASSROOM_TAG_BY_COURSE_TYPE.values())
    schedule = getattr(getattr(cache, "rhodes_island", None), "class_schedule", None)
    if isinstance(schedule, dict):
        for name in schedule:
            _check_room_name(scenes, classroom_tags, name, None, f"class_schedule[{name!r}]", failures)
    characters = getattr(cache, "character_data", None)
    if not isinstance(characters, dict):
        return failures
    for cid, character in characters.items():
        selected = getattr(getattr(character, "child_growth", None), "selected_course", None)
        if not isinstance(selected, dict):
            continue
        for day, periods in selected.items():
            if not isinstance(periods, dict):
                continue
            for period, cell in periods.items():
                if not isinstance(cell, list) or len(cell) != 2:
                    continue
                course_type, target = cell
                if type(course_type) is not int or course_type not in (0, 1, 2, 3) or not isinstance(target, str):
                    continue
                if course_type == education_constant.COURSE_TYPE_PE:
                    data = education_constant.PE_PLACE_DATA.get(target)
                    tags = {data[0]} if data is not None else set()
                else:
                    tags = {education_constant.CLASSROOM_TAG_BY_COURSE_TYPE[course_type]}
                _check_room_name(scenes, tags, target, cid, f"selected_course[{day!r}][{period!r}]", failures)
    return failures
