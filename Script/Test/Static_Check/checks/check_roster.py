# -*- coding: UTF-8 -*-
"""
静态检查系统 - 监禁调教/访客/招募名册/外勤委托相关检查
本模块实现 ROSTER-01..ROSTER-33 全部33条不变式，覆盖在编名册、场景成员关系、监禁与逃跑、
监狱长、访客、邀请、招募、外勤委托、载具、外交官、异常位掩码、助理、装袋等子系统的状态自洽性。

设计基准: Linux(os.sep == "/")。全部涉及路径拼接的比较一律通过 os.sep.join 或场景标签集合完成，
不写死"\\"分隔符(详见各检查函数内注释)。全部离线判定一律用来源flag(field_commission/escaping/be_bagged)，
不使用 position == ["0","0"] 作为离线判据 —— 该坐标是真实场景"罗德岛出口"，在线角色途经该处合法。
全部访客排除一律写 vistor != 1，vistor == 2(前访客)是合法的招募/邀请目标，不得写成 vistor == 0。
"""
import collections
import datetime
import math
import os
from typing import Dict, List, Set

from Script.Config import game_config
from Script.Core import cache_control, game_type
from ..check_registry import CheckFailure, register_check, make_failure


# ------------------------------- 共用小工具 -------------------------------


def _spath(pos) -> str:
    """
    参数: pos -- 形如["区域","房间"]的位置列表
    返回值: str -- 用os.sep拼接得到的场景路径字符串；pos形状不合法时返回空串
    功能: 等价于map_handle.get_map_system_path_str_for_list，避免任何地方写死分隔符
    """
    if isinstance(pos, (list, tuple)) and all(isinstance(x, str) for x in pos):
        return os.sep.join(pos)
    return ""


def _prison_dorms(cache) -> Set[str]:
    """
    参数: cache -- 全局缓存
    返回值: Set[str] -- 全部带Prison标签的场景路径集合(关押/牢1..牢8)
    功能: 按场景标签动态推导合法牢房集合，避免子串匹配或写死路径
    """
    return {p for p, s in cache.scene_data.items() if "Prison" in getattr(s, "scene_tag", [])}


def _guest_rooms(cache) -> Set[str]:
    """
    参数: cache -- 全局缓存
    返回值: Set[str] -- 全部带Guest_Room标签的场景路径集合(访客/客房N)
    功能: 按场景标签动态推导合法客房集合
    """
    return {p for p, s in cache.scene_data.items() if "Guest_Room" in getattr(s, "scene_tag", [])}


def _warden_dorm() -> str:
    """
    参数: 无
    返回值: str -- 监狱长专属宿舍"关押/休息室"的场景路径
    功能: 提供监狱长宿舍常量，统一走_spath避免分隔符问题
    """
    return _spath(["关押", "休息室"])


def _scene_membership(cache) -> Dict[int, List[str]]:
    """
    参数: cache -- 全局缓存
    返回值: Dict[int, List[str]] -- 角色id到其出现的全部场景路径列表的反向索引(正常应恰好一条)
    功能: 遍历cache.scene_data建立场景成员关系反向索引，供在编/离线一致性类检查复用，避免重复遍历529个场景
    """
    membership: Dict[int, List[str]] = {}
    for path, scene in cache.scene_data.items():
        for cid in getattr(scene, "character_list", []):
            if cid != 0:
                membership.setdefault(cid, []).append(path)
    return membership


def _invite_target(ri) -> int:
    """
    参数: ri -- cache.rhodes_island
    返回值: int -- invite_visitor[0](邀请目标id)，形状不合法(旧存档/未初始化)时按0(无目标)处理
    功能: 复现ROSTER-18的形状守卫，供ROSTER-19/21/27等引用invite_visitor的检查复用，避免对不足长度的旧list直接下标
    """
    iv = ri.invite_visitor if isinstance(ri.invite_visitor, list) else []
    return iv[0] if len(iv) >= 1 and type(iv[0]) is int else 0


def _sev(cache, declared_warning: bool) -> str:
    """
    参数: cache -- 全局缓存; declared_warning -- 该检查项在不变式文档中声明的severity是否为warning
    返回值: str -- 需拼在失败信息最前面的前缀，declared_warning为True或cache.debug_mode为True时为"[warning] "，否则空串
    功能: 统一处理"[warning]"消息前缀规则，同时实现"debug模式下全部条目整体降级为提示"的全局约定，
    因为debug面板可以绕开配套流程直改facility_open/be_bagged/imprisonment等flag
    """
    return "[warning] " if declared_warning or getattr(cache, "debug_mode", False) else ""


# ------------------------------- ROSTER-01 ~ ROSTER-33 -------------------------------


@register_check("ROSTER-01", "在编名册id自洽")
def check_roster_id_self_consistency() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能: 校验cache.npc_id_got中每个id都存在角色对象，且角色自身cid与名册键一致，这是后续全部名册检查的地基
    """
    cache = cache_control.cache
    cd = cache.character_data
    warn = _sev(cache, False)
    failures: List[CheckFailure] = []
    for cid in cache.npc_id_got:
        if cid not in cd:
            failures.append(
                make_failure(
                    "ROSTER-01",
                    "在编名册id自洽",
                    f"{warn}npc_id_got中的角色id={cid}在character_data中不存在，len(npc_id_got)={len(cache.npc_id_got)}",
                    [cid],
                )
            )
            continue
        c = cd[cid]
        if c.cid != cid:
            failures.append(
                make_failure(
                    "ROSTER-01",
                    "在编名册id自洽",
                    f"{warn}character_data[{cid}].cid={c.cid}与名册键{cid}不一致，name={c.name!r}，adv={c.adv}",
                    [cid],
                )
            )
    return failures


@register_check("ROSTER-02", "玩家id不应长期留在NPC名册里")
def check_player_id_not_lingering_in_roster() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能: npc_id_got语义上是NPC集合，但init_character_position/init_character_entertainment会对玩家本体add(0)，
    discard(0)只在基建/宿舍面板(玩家触发)里执行，回合主循环从不调用。新游戏/多周目开局第一回合必然命中，
    cache没有暴露"该discard调用是否已跑过"的持久标记，这里用game_round<=1作为"很可能是开局首回合、面板尚未打开过"
    的保守豁免，避免每局开头都刷一条假警报；游戏时间推进后(game_round>1)仍命中才报出
    """
    cache = cache_control.cache
    ri = cache.rhodes_island
    warn = _sev(cache, True)
    failures: List[CheckFailure] = []
    if 0 not in cache.npc_id_got:
        return failures
    if getattr(cache, "game_round", 1) <= 1:
        return failures
    failures.append(
        make_failure(
            "ROSTER-02",
            "玩家id不应长期留在NPC名册里",
            f"{warn}玩家id=0仍留在npc_id_got中(len={len(cache.npc_id_got)})，game_time={cache.game_time}，game_round={cache.game_round}；"
            f"若非开局首回合，说明discard(0)调用点(基建/宿舍面板)未生效或该id被重新add",
            [0],
        )
    )
    return failures


@register_check("ROSTER-03", "在编干员与场景名册双向一致")
def check_roster_scene_bidirectional_consistency() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能: 校验在编NPC恰好出现在其position对应的那一个场景里，离线角色从所有场景消失，场景里不得有幽灵id。
    用os.sep拼路径，不加position != ["0","0"]的排除 —— 在线角色停在"罗德岛出口"(0/0)是合法状态
    """
    cache = cache_control.cache
    cd = cache.character_data
    warn = _sev(cache, False)
    failures: List[CheckFailure] = []
    membership = _scene_membership(cache)
    for path, scene in cache.scene_data.items():
        for cid in getattr(scene, "character_list", []):
            if cid == 0:
                continue
            if cid not in cd:
                failures.append(
                    make_failure(
                        "ROSTER-03",
                        "在编干员与场景名册双向一致",
                        f"{warn}场景{path}的character_list中含幽灵角色id={cid}，character_data中不存在该id",
                        [cid],
                    )
                )
    for cid, c in cd.items():
        if cid == 0:
            continue
        paths = membership.get(cid, [])
        sp = c.sp_flag
        ctx = (
            f"field_commission={sp.field_commission}, escaping={sp.escaping}, be_bagged={sp.be_bagged}, "
            f"in_diplomatic_visit={sp.in_diplomatic_visit}, vistor={sp.vistor}"
        )
        if cid in cache.npc_id_got:
            pos = getattr(c, "position", None)
            # 形状断言放宽为"非空list且元素全为str"：47%场景(248/530)是三段路径，["0","0"]是真实场景非哨兵，
            # map_handle无任何长度约束，故不再断言len==2。畸形position会被下面的路径存在性分支抓住，
            # 这里保留形状分支只为给出更精确的"形状异常"报错文案，不整段删除
            if not (isinstance(pos, list) and pos and all(isinstance(x, str) for x in pos)):
                failures.append(
                    make_failure(
                        "ROSTER-03",
                        "在编干员与场景名册双向一致",
                        f"{warn}在编角色cid={cid} name={c.name!r} position={pos!r}形状异常(应为非空且元素全为str的list)；{ctx}",
                        [cid],
                    )
                )
                continue
            expected = _spath(pos)
            if expected not in cache.scene_data:
                failures.append(
                    make_failure(
                        "ROSTER-03",
                        "在编干员与场景名册双向一致",
                        f"{warn}在编角色cid={cid} name={c.name!r} position={pos}对应路径{expected!r}不存在于scene_data中；{ctx}",
                        [cid],
                    )
                )
                continue
            if paths != [expected]:
                failures.append(
                    make_failure(
                        "ROSTER-03",
                        "在编干员与场景名册双向一致",
                        f"{warn}在编角色cid={cid} name={c.name!r} position={pos}(期望仅出现在{expected!r})，实际出现在场景{paths}中；{ctx}",
                        [cid],
                    )
                )
        else:
            if paths:
                failures.append(
                    make_failure(
                        "ROSTER-03",
                        "在编干员与场景名册双向一致",
                        f"{warn}离线角色cid={cid} name={c.name!r} 不在npc_id_got中，却残留在场景{paths}中；{ctx}",
                        [cid],
                    )
                )
    return failures


@register_check("ROSTER-04", "离线来源flag必须对应真正的离线态")
def check_offline_source_flag_matches_real_offline_state() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能: 装袋/外勤/越狱三条路径都是"置来源flag→重算异常位→handle_chara_off_line"的原子写法。
    任一来源flag为真而角色仍在编、仍在某场景、或position未归零，即为半离线的幽灵。
    不用unnormal_flag.check(7)作判据 —— 该位是懒缓存，未知位读作False，且交互对象素质会给在线角色合法置位
    """
    cache = cache_control.cache
    cd = cache.character_data
    warn = _sev(cache, False)
    failures: List[CheckFailure] = []
    membership = _scene_membership(cache)
    for cid, c in cd.items():
        if cid == 0:
            continue
        sp = c.sp_flag
        if not (sp.field_commission or sp.escaping or sp.be_bagged):
            continue
        problems = []
        if cid in cache.npc_id_got:
            problems.append("仍在npc_id_got在编名册中")
        hit = membership.get(cid, [])
        if hit:
            problems.append(f"仍残留在场景{hit}中")
        pos = getattr(c, "position", None)
        if pos != ["0", "0"]:
            problems.append(f"position={pos!r}未归零")
        if problems:
            failures.append(
                make_failure(
                    "ROSTER-04",
                    "离线来源flag必须对应真正的离线态",
                    f"{warn}角色cid={cid} name={c.name!r} 三源flag(field_commission={sp.field_commission}, escaping={sp.escaping}, "
                    f"be_bagged={sp.be_bagged})指示应离线，但{'; '.join(problems)}；state={c.state}，"
                    f"behavior.behavior_id={c.behavior.behavior_id!r}",
                    [cid],
                )
            )
    return failures


@register_check("ROSTER-05", "监禁flag的来源分区完整")
def check_imprisonment_flag_partition_completeness() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能: 带imprisonment的角色当且仅当是在册囚犯或逃跑中的前囚犯(escape_success故意保留imprisonment)；
    囚犯与逃犯两个集合互斥
    """
    cache = cache_control.cache
    cd = cache.character_data
    ri = cache.rhodes_island
    warn = _sev(cache, False)
    failures: List[CheckFailure] = []
    imp = {cid for cid, c in cd.items() if cid != 0 and c.sp_flag.imprisonment}
    esc = {cid for cid, c in cd.items() if cid != 0 and c.sp_flag.escaping}
    prisoners = set(ri.current_prisoners)
    union = prisoners | esc
    for cid in imp - union:
        c = cd[cid]
        failures.append(
            make_failure(
                "ROSTER-05",
                "监禁flag的来源分区完整",
                f"{warn}角色cid={cid} name={c.name!r} sp_flag.imprisonment为True，但既不在current_prisoners也不escaping；"
                f"position={c.position}，dormitory={c.dormitory!r}，permanent_dormitory={c.permanent_dormitory!r}",
                [cid],
            )
        )
    for cid in union - imp:
        c = cd.get(cid)
        failures.append(
            make_failure(
                "ROSTER-05",
                "监禁flag的来源分区完整",
                f"{warn}角色cid={cid} name={getattr(c, 'name', '?')!r} 在current_prisoners或escaping中，但sp_flag.imprisonment为False；"
                f"current_prisoners.get={ri.current_prisoners.get(cid)}",
                [cid],
            )
        )
    for cid in prisoners & esc:
        c = cd[cid]
        failures.append(
            make_failure(
                "ROSTER-05",
                "监禁flag的来源分区完整",
                f"{warn}角色cid={cid} name={c.name!r} 同时在current_prisoners囚犯名册与escaping逃跑者集合中(应互斥)；"
                f"position={c.position}，dormitory={c.dormitory!r}",
                [cid],
            )
        )
    return failures


@register_check("ROSTER-06", "囚犯名册条目结构合法且本人在编")
def check_prisoner_record_shape_and_roster_membership() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能: 校验current_prisoners每条记录形状为[入狱时间, 逃脱概率]，概率夹在0..100之间且非bool污染，
    本人在编且sp_flag.imprisonment为True、escaping为False
    """
    cache = cache_control.cache
    cd = cache.character_data
    ri = cache.rhodes_island
    warn = _sev(cache, False)
    failures: List[CheckFailure] = []
    for cid, rec in ri.current_prisoners.items():
        if cid == 0 or cid not in cd:
            failures.append(
                make_failure(
                    "ROSTER-06",
                    "囚犯名册条目结构合法且本人在编",
                    f"{warn}囚犯名册键cid={cid}非法(0号玩家或character_data中不存在)，record={rec!r}",
                    [cid],
                )
            )
            continue
        c = cd[cid]
        problems = []
        if cid not in cache.npc_id_got:
            problems.append("不在npc_id_got在编名册中")
        if not (isinstance(rec, list) and len(rec) == 2):
            problems.append(f"record形状异常，期望长度2的list，实得{rec!r}")
        else:
            entry_time, prob = rec[0], rec[1]
            if not (isinstance(entry_time, datetime.datetime) and entry_time <= cache.game_time):
                problems.append(f"入狱时间rec[0]={entry_time!r}不是<=game_time({cache.game_time})的datetime")
            if isinstance(prob, bool) or not isinstance(prob, (int, float)):
                problems.append(f"逃脱概率rec[1]={prob!r}类型不是int/float或被bool污染")
            elif not (math.isfinite(prob) and 0 <= prob <= 100):
                problems.append(f"逃脱概率rec[1]={prob}超出[0,100]范围或非有限数")
        if not c.sp_flag.imprisonment:
            problems.append("sp_flag.imprisonment为False")
        if c.sp_flag.escaping:
            problems.append("sp_flag.escaping为True(不应与在册囚犯并存)")
        if problems:
            failures.append(
                make_failure(
                    "ROSTER-06",
                    "囚犯名册条目结构合法且本人在编",
                    f"{warn}囚犯cid={cid} name={c.name!r} 存在问题: {'; '.join(problems)}；record={rec!r}，game_time={cache.game_time}，"
                    f"ability[42]={c.ability.get(42)}，ability[45]={c.ability.get(45)}，"
                    f"confinement_training_setting[4]={ri.confinement_training_setting.get(4)}",
                    [cid],
                )
            )
    return failures


@register_check("ROSTER-07", "囚犯宿舍是互不重复的合法牢房")
def check_prisoner_dormitory_uniqueness() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能: 每名囚犯的dormitory都必须在PRISON_DORMS(全部Prison标签场景，即牢1..牢8)集合内，且互不重复。
    唯一性是真实捕获点：指令前提SCENE_ONLY_ONE只看当前在场者，正在调教室的囚犯会让其牢房"看起来是空的"
    """
    cache = cache_control.cache
    cd = cache.character_data
    ri = cache.rhodes_island
    warn = _sev(cache, False)
    failures: List[CheckFailure] = []
    prison_dorms = _prison_dorms(cache)
    dorm_to_cids: Dict[str, List[int]] = {}
    for cid in ri.current_prisoners:
        if cid not in cd:
            continue
        d = cd[cid].dormitory
        dorm_to_cids.setdefault(d, []).append(cid)
    for d, cids in dorm_to_cids.items():
        if d not in prison_dorms:
            for cid in cids:
                c = cd[cid]
                failures.append(
                    make_failure(
                        "ROSTER-07",
                        "囚犯宿舍是互不重复的合法牢房",
                        f"{warn}囚犯cid={cid} name={c.name!r} 的宿舍dormitory={d!r}不在合法牢房集合PRISON_DORMS中；"
                        f"position={c.position}，permanent_dormitory={c.permanent_dormitory!r}，PRISON_DORMS={sorted(prison_dorms)}",
                        [cid],
                    )
                )
        if len(cids) > 1:
            names = [(cid, cd[cid].name) for cid in cids]
            failures.append(
                make_failure(
                    "ROSTER-07",
                    "囚犯宿舍是互不重复的合法牢房",
                    f"{warn}牢房{d!r}被多名囚犯共用: {names}，len(current_prisoners)={len(ri.current_prisoners)}",
                    list(cids),
                )
            )
    return failures


@register_check("ROSTER-08", "囚犯留在关押区且不得同时被装袋")
def check_prisoner_stays_in_prison_area_and_not_bagged() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能: 囚犯cant_move，NPC AI会把不在牢房的囚犯瞬移回宿舍，合法的短暂离房只有"正在H(含调教室)"；
    用position[0] == "关押"比对目录首段，不拼分隔符。囚犯与被装袋互斥 —— 装袋前提含T_IMPRISONMENT_0，
    且chara_become_prisoner首行清be_bagged
    """
    cache = cache_control.cache
    cd = cache.character_data
    ri = cache.rhodes_island
    warn = _sev(cache, False)
    failures: List[CheckFailure] = []
    player = cd.get(0)
    for cid in ri.current_prisoners:
        if cid not in cd:
            continue
        c = cd[cid]
        problems = []
        if c.sp_flag.be_bagged:
            problems.append("同时被装袋(be_bagged=True)")
        if not c.sp_flag.is_h:
            pos = getattr(c, "position", None)
            if not (isinstance(pos, list) and len(pos) >= 1 and pos[0] == "关押"):
                problems.append(f"既不在H中也不在关押区，position={pos!r}")
        if problems:
            failures.append(
                make_failure(
                    "ROSTER-08",
                    "囚犯留在关押区且不得同时被装袋",
                    f"{warn}囚犯cid={cid} name={c.name!r} {'; '.join(problems)}；position={c.position}，dormitory={c.dormitory!r}，"
                    f"is_h={c.sp_flag.is_h}，玩家position={getattr(player, 'position', None)}",
                    [cid],
                )
            )
    return failures


@register_check("ROSTER-09", "逃跑者处于完整离线态")
def check_escapee_full_offline_state() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能: escape_success依次置escaping→重算异常位→pop囚犯名册→handle_chara_off_line→创建追捕委托，
    并保留imprisonment。任一环缺失即为半态。position == ["0","0"]在此是离线的结果而非判据
    """
    cache = cache_control.cache
    cd = cache.character_data
    ri = cache.rhodes_island
    warn = _sev(cache, False)
    failures: List[CheckFailure] = []
    membership = _scene_membership(cache)
    for cid, c in cd.items():
        if cid == 0 or not c.sp_flag.escaping:
            continue
        problems = []
        if not c.sp_flag.imprisonment:
            problems.append("imprisonment应保留为True但为False")
        if cid in ri.current_prisoners:
            problems.append("仍残留在current_prisoners囚犯名册中")
        if cid in cache.npc_id_got:
            problems.append("仍在npc_id_got在编名册中")
        hit = membership.get(cid, [])
        if hit:
            problems.append(f"仍残留在场景{hit}中")
        if c.position != ["0", "0"]:
            problems.append(f"position={c.position!r}未归零")
        if c.sp_flag.field_commission:
            problems.append(f"field_commission={c.sp_flag.field_commission}非零(逃犯不应挂外勤)")
        if problems:
            failures.append(
                make_failure(
                    "ROSTER-09",
                    "逃跑者处于完整离线态",
                    f"{warn}逃跑者cid={cid} name={c.name!r} {'; '.join(problems)}",
                    [cid],
                )
            )
    return failures


@register_check("ROSTER-10", "逃跑者仍有一条可执行的追捕委托")
def check_escapee_has_executable_capture_commission() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能: 每个escaping角色都应存在一条reward=="追捕_{cid}_1"且未标记完成的委托配置；
    牢房全满时抓捕结算会静默跳过归案，委托却照样标完成并出表，逃犯从此永久滞留escaping。
    依赖game_config.config_commission，若该配置为空(独立环境/测试未加载配置)则无法判定，直接跳过本条
    """
    cache = cache_control.cache
    cd = cache.character_data
    ri = cache.rhodes_island
    warn = _sev(cache, True)
    failures: List[CheckFailure] = []
    if not game_config.config_commission:
        return failures
    finished = ri.finished_field_commissions_set
    for cid, c in cd.items():
        if cid == 0 or not c.sp_flag.escaping:
            continue
        target_reward = "追捕_{0}_1".format(cid)
        candidates = [
            com_id
            for com_id, com in game_config.config_commission.items()
            if getattr(com, "reward", "") == target_reward and com_id not in finished
        ]
        if not candidates:
            failures.append(
                make_failure(
                    "ROSTER-10",
                    "逃跑者仍有一条可执行的追捕委托",
                    f"{warn}逃跑者cid={cid} name={c.name!r} 没有任何未完成的追捕委托(期望reward={target_reward!r})；"
                    f"finished_field_commissions_set={ri.finished_field_commissions_set}，"
                    f"ongoing_field_commissions的id列表={list(ri.ongoing_field_commissions)}，当前囚犯数={len(ri.current_prisoners)}",
                    [cid],
                )
            )
    return failures


@register_check("ROSTER-11", "监狱长缓存唯一且指向真实岗位")
def check_warden_cache_unique_and_valid() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能: 在编干员里最多只能有一名工作类型191的监狱长，current_warden_id非零时必须指向存在的角色，
    不能与那名在编191冲突。"wid非零而没有任何在编191"是可达残留，已拆到ROSTER-12作warning，不进本条
    """
    cache = cache_control.cache
    cd = cache.character_data
    ri = cache.rhodes_island
    warn = _sev(cache, False)
    failures: List[CheckFailure] = []
    wid = ri.current_warden_id
    if type(wid) is not int:
        failures.append(
            make_failure("ROSTER-11", "监狱长缓存唯一且指向真实岗位", f"{warn}current_warden_id类型异常: {wid!r}", [])
        )
        return failures
    wardens = {cid for cid in cache.npc_id_got if cid != 0 and cid in cd and cd[cid].work.work_type == 191}
    if len(wardens) > 1:
        details = [(cid, cd[cid].name, cd[cid].dormitory) for cid in wardens]
        failures.append(
            make_failure(
                "ROSTER-11",
                "监狱长缓存唯一且指向真实岗位",
                f"{warn}存在{len(wardens)}名在编工作类型191(监狱长)的角色，超过唯一上限: {details}，current_warden_id={wid}",
                list(wardens),
            )
        )
    if wid:
        if wid not in cd:
            failures.append(
                make_failure(
                    "ROSTER-11",
                    "监狱长缓存唯一且指向真实岗位",
                    f"{warn}current_warden_id={wid}指向的角色不存在于character_data中",
                    [wid],
                )
            )
        elif wardens - {wid}:
            others = sorted(wardens - {wid})
            failures.append(
                make_failure(
                    "ROSTER-11",
                    "监狱长缓存唯一且指向真实岗位",
                    f"{warn}current_warden_id={wid}与另外在编191岗位角色冲突: {[(cid, cd[cid].name) for cid in others]}",
                    [wid] + others,
                )
            )
    return failures


@register_check("ROSTER-12", "监狱长身份软约束")
def check_warden_identity_soft_constraints() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能: 期望状态：current_warden_id非零时该人在编、宿舍是关押区休息室、不是囚犯/访客、不在外勤。
    三项都可被合法操作打破(装袋前提未排除监狱长，玩家可把监狱长本人装袋后投入监牢)，故只作提示
    """
    cache = cache_control.cache
    cd = cache.character_data
    ri = cache.rhodes_island
    warn = _sev(cache, True)
    failures: List[CheckFailure] = []
    wid = ri.current_warden_id
    if not wid or wid not in cd:
        return failures
    w = cd[wid]
    warden_dorm = _warden_dorm()
    problems = []
    if wid not in cache.npc_id_got:
        problems.append("不在npc_id_got在编名册中")
    if w.work.work_type != 191:
        problems.append(f"work.work_type={w.work.work_type}不是191")
    if w.dormitory != warden_dorm:
        problems.append(f"dormitory={w.dormitory!r}不是关押/休息室({warden_dorm!r})")
    if wid in ri.current_prisoners:
        problems.append("是当前囚犯(在current_prisoners中)")
    if w.sp_flag.vistor == 1:
        problems.append("当前是在岛访客(vistor==1)")
    if w.sp_flag.field_commission:
        problems.append(f"field_commission={w.sp_flag.field_commission}非零(在外勤中)")
    if w.sp_flag.be_bagged:
        problems.append("被装袋(be_bagged=True)")
    if problems:
        player = cd.get(0)
        failures.append(
            make_failure(
                "ROSTER-12",
                "监狱长身份软约束",
                f"{warn}监狱长wid={wid} name={w.name!r} 偏离期望状态: {'; '.join(problems)}；permanent_dormitory={w.permanent_dormitory!r}，"
                f"玩家bagging_chara_id={getattr(getattr(player, 'sp_flag', None), 'bagging_chara_id', None)}",
                [wid],
            )
        )
    return failures


@register_check("ROSTER-13", "监禁调教设置键齐全且取值在选项范围内")
def check_confinement_training_setting_keys_and_range() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能: 设置字典由配置表全量初始化为0，UI用option[cid][value]直接索引(越界IndexError)，
    结算路径对[4]/[13]直取(缺键KeyError)。type(v) is int而非isinstance，避免bool污染被当作合法整数放过。
    依赖game_config.config_confinement_training_setting，若为空(独立环境未加载配置)则循环自然不产生任何失败，等价于跳过本条
    """
    cache = cache_control.cache
    ri = cache.rhodes_island
    warn = _sev(cache, False)
    failures: List[CheckFailure] = []
    for cid in game_config.config_confinement_training_setting:
        option = game_config.config_confinement_training_setting_option.get(cid, [])
        if cid not in ri.confinement_training_setting:
            failures.append(
                make_failure(
                    "ROSTER-13",
                    "监禁调教设置键齐全且取值在选项范围内",
                    f"{warn}设置项cid={cid}缺失于ri.confinement_training_setting，option长度={len(option)}",
                    [],
                )
            )
            continue
        v = ri.confinement_training_setting[cid]
        if type(v) is not int:
            failures.append(
                make_failure(
                    "ROSTER-13",
                    "监禁调教设置键齐全且取值在选项范围内",
                    f"{warn}设置项cid={cid}取值v={v!r}类型不是int(可能被bool污染)",
                    [],
                )
            )
            continue
        if not (0 <= v < len(option)):
            failures.append(
                make_failure(
                    "ROSTER-13",
                    "监禁调教设置键齐全且取值在选项范围内",
                    f"{warn}设置项cid={cid}取值v={v}越界，option长度={len(option)}，完整设置={dict(ri.confinement_training_setting)}",
                    [],
                )
            )
    return failures


@register_check("ROSTER-14", "访客名册与访客flag完全等价")
def check_visitor_registry_and_flag_equivalence() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能: visitor_info与sp_flag.vistor == 1是同一件事的两份记录，且当前访客必然在编。
    不写成vistor != 0 —— 前访客恒为2，是合法状态，不应被本条判为不一致
    """
    cache = cache_control.cache
    cd = cache.character_data
    ri = cache.rhodes_island
    warn = _sev(cache, False)
    failures: List[CheckFailure] = []
    vis_flag = {cid for cid, c in cd.items() if cid != 0 and c.sp_flag.vistor == 1}
    vis_reg = set(ri.visitor_info)
    for cid in vis_reg - vis_flag:
        c = cd.get(cid)
        v = c.sp_flag.vistor if c is not None else None
        failures.append(
            make_failure(
                "ROSTER-14",
                "访客名册与访客flag完全等价",
                f"{warn}cid={cid}在ri.visitor_info名册中，但sp_flag.vistor={v}不为1",
                [cid],
            )
        )
    for cid in vis_flag - vis_reg:
        c = cd[cid]
        failures.append(
            make_failure(
                "ROSTER-14",
                "访客名册与访客flag完全等价",
                f"{warn}cid={cid} name={c.name!r} sp_flag.vistor==1，但不在ri.visitor_info名册中，dormitory={c.dormitory!r}",
                [cid],
            )
        )
    for cid in vis_reg - cache.npc_id_got:
        c = cd.get(cid)
        failures.append(
            make_failure(
                "ROSTER-14",
                "访客名册与访客flag完全等价",
                f"{warn}访客cid={cid} name={getattr(c, 'name', '?')!r} 不在cache.npc_id_got在编名册中",
                [cid],
            )
        )
    return failures


@register_check("ROSTER-15", "访客住在互不重复的客房")
def check_visitor_room_uniqueness() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能: 访客由分配器挑一间没有别的访客占用的客房；用场景标签集合GUEST_ROOMS判定房间合法性，
    比"客房" in d的子串判定更强。注意：Linux上分配器room_full_path.split("\\")[-1]与配置房间名比对会失配，
    dormitory可能长期停在模板初值，本条在本机命中即为跨平台缺陷的真实证据，不应回头放宽检查
    """
    cache = cache_control.cache
    cd = cache.character_data
    ri = cache.rhodes_island
    warn = _sev(cache, False)
    failures: List[CheckFailure] = []
    guest_rooms = _guest_rooms(cache)
    room_to_cids: Dict[str, List[int]] = {}
    for cid in ri.visitor_info:
        if cid not in cd:
            failures.append(
                make_failure("ROSTER-15", "访客住在互不重复的客房", f"{warn}访客cid={cid}不在character_data中", [cid])
            )
            continue
        c = cd[cid]
        d = c.dormitory
        room_to_cids.setdefault(d, []).append(cid)
        if d not in guest_rooms:
            open_2000 = {k: v for k, v in ri.facility_open.items() if 2000 < k < 2100}
            failures.append(
                make_failure(
                    "ROSTER-15",
                    "访客住在互不重复的客房",
                    f"{warn}访客cid={cid} name={c.name!r} 的dormitory={d!r}不在合法客房集合GUEST_ROOMS中；"
                    f"position={c.position}，visitor_max={ri.visitor_max}，facility_open(2000-2099)={open_2000}",
                    [cid],
                )
            )
    for d, cids in room_to_cids.items():
        if len(cids) > 1:
            names = [(cid, cd[cid].name) for cid in cids]
            failures.append(
                make_failure(
                    "ROSTER-15", "访客住在互不重复的客房", f"{warn}客房{d!r}被多名访客共用: {names}", list(cids)
                )
            )
    return failures


@register_check("ROSTER-16", "访客人数不超过客房上限")
def check_visitor_count_within_capacity() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能: visitor_max是按已开放客房数重算的接待闸门。运行期facility_open只会置True，不存在"关闭客房造成合法超员"
    的路径，但visitor_max只在基建面板刷新时重算，属派生缓存，旧存档可能带陈旧值，故定为warning
    """
    cache = cache_control.cache
    ri = cache.rhodes_island
    warn = _sev(cache, True)
    failures: List[CheckFailure] = []
    if len(ri.visitor_info) > ri.visitor_max:
        open_2000 = {k: v for k, v in ri.facility_open.items() if 2000 < k < 2100}
        failures.append(
            make_failure(
                "ROSTER-16",
                "访客人数不超过客房上限",
                f"{warn}当前访客数len(visitor_info)={len(ri.visitor_info)}超过visitor_max={ri.visitor_max}；"
                f"facility_open(2000-2099)={open_2000}，facility_level[13]={ri.facility_level.get(13)}",
                list(ri.visitor_info),
            )
        )
    return failures


@register_check("ROSTER-17", "没有严重逾期未结算的访客")
def check_no_severely_overdue_visitors() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能: 访客到期由跨日结算处理一次，"D日到期、D+1日00:00才结算"是正常窗口，阈值必须放到一整天以上，
    否则会周期性误报；类型检查不可省，脏值在减法处会抛异常而非给出判定
    """
    cache = cache_control.cache
    ri = cache.rhodes_island
    warn = _sev(cache, True)
    failures: List[CheckFailure] = []
    for cid, end in ri.visitor_info.items():
        if not isinstance(end, datetime.datetime):
            failures.append(
                make_failure(
                    "ROSTER-17", "没有严重逾期未结算的访客", f"{warn}访客cid={cid}的到期时间类型异常: {end!r}", [cid]
                )
            )
            continue
        delta = cache.game_time - end
        if delta.days >= 1:
            failures.append(
                make_failure(
                    "ROSTER-17",
                    "没有严重逾期未结算的访客",
                    f"{warn}访客cid={cid}到期时间{end}已逾期{delta}，超过一整天未结算(可能日结算漏跑或该访客被卡住)；"
                    f"game_time={cache.game_time}，last_visitor_time={ri.last_visitor_time}，"
                    f"base_move_visitor_flag={ri.base_move_visitor_flag}",
                    [cid],
                )
            )
    return failures


@register_check("ROSTER-18", "邀请栏结构完整、空目标必归零")
def check_invite_visitor_shape_integrity() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能: invite_visitor是[目标id, 进度, 效率]；目标为0时进度必须为0；进度与效率是非负有限数。
    不加进度上界 —— 客房满时settle_visitor_arrivals返回失败且不清零，进度停在>=100甚至继续增长是合法状态。
    本条形状守卫供ROSTER-19/21/27复用，本模块内各条各自独立调用_invite_target，不依赖调用顺序
    """
    cache = cache_control.cache
    cd = cache.character_data
    ri = cache.rhodes_island
    warn = _sev(cache, False)
    failures: List[CheckFailure] = []
    raw = ri.invite_visitor
    if not (isinstance(raw, list) and len(raw) == 3):
        failures.append(
            make_failure(
                "ROSTER-18",
                "邀请栏结构完整、空目标必归零",
                f"{warn}ri.invite_visitor形状异常，期望长度3的list，实得{raw!r}",
                [],
            )
        )
        return failures
    problems = []
    if type(raw[0]) is not int:
        problems.append(f"raw[0]={raw[0]!r}类型不是int")
    for i, x in enumerate(raw[1:], start=1):
        if isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) or x < 0:
            problems.append(f"raw[{i}]={x!r}不是非负有限数")
    if type(raw[0]) is int and raw[0] == 0:
        prog_ok = isinstance(raw[1], (int, float)) and not isinstance(raw[1], bool) and raw[1] == 0
        if not prog_ok:
            problems.append(f"目标raw[0]==0但进度raw[1]={raw[1]!r}未归零")
    if problems:
        target = raw[0] if type(raw[0]) is int else None
        exists = target in cd if target else None
        failures.append(
            make_failure(
                "ROSTER-18",
                "邀请栏结构完整、空目标必归零",
                f"{warn}ri.invite_visitor={raw!r}存在问题: {'; '.join(problems)}；facility_level[13]={ri.facility_level.get(13)}，"
                f"game_time={cache.game_time}，目标是否存在于character_data={exists}",
                [target] if target else [],
            )
        )
    return failures


@register_check("ROSTER-19", "邀请目标仍是合法的未入编候选")
def check_invite_target_still_valid_candidate() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能: 邀请目标只能来自find_recruitable_npc()。若目标在邀请期间被招募线或访客抽中，进度满100时
    会对一个已在编角色再跑一次get_new_character。用vistor != 1而非== 0 —— find_recruitable_npc只跳过vistor==1，
    前访客(vistor==2)是合法邀请目标。position == ["0","0"]在此是未入编角色的必要属性，不是离线判据
    """
    cache = cache_control.cache
    cd = cache.character_data
    ri = cache.rhodes_island
    warn = _sev(cache, False)
    failures: List[CheckFailure] = []
    t = _invite_target(ri)
    if not t:
        return failures
    if t not in cd:
        failures.append(
            make_failure(
                "ROSTER-19",
                "邀请目标仍是合法的未入编候选",
                f"{warn}邀请目标t={t}不存在于character_data中，invite_visitor={ri.invite_visitor!r}",
                [t],
            )
        )
        return failures
    c = cd[t]
    problems = []
    if t in cache.npc_id_got:
        problems.append("已在npc_id_got在编名册中")
    if t in ri.visitor_info:
        problems.append("已在ri.visitor_info访客名册中")
    if t in ri.recruited_id:
        problems.append("已在ri.recruited_id待确认招募名单中")
    if t in ri.current_prisoners:
        problems.append("已在ri.current_prisoners囚犯名册中")
    if c.sp_flag.vistor == 1:
        problems.append("当前是在岛访客(vistor==1)")
    if c.sp_flag.imprisonment:
        problems.append("sp_flag.imprisonment为True")
    if c.sp_flag.escaping:
        problems.append("sp_flag.escaping为True")
    if c.sp_flag.field_commission:
        problems.append(f"sp_flag.field_commission={c.sp_flag.field_commission}非零")
    if c.position != ["0", "0"]:
        problems.append(f"position={c.position!r}未归零(未入编角色的必要属性)")
    if problems:
        failures.append(
            make_failure(
                "ROSTER-19",
                "邀请目标仍是合法的未入编候选",
                f"{warn}邀请目标t={t} name={c.name!r} adv={c.adv} 不再是合法候选: {'; '.join(problems)}；"
                f"len(visitor_info)={len(ri.visitor_info)}，visitor_max={ri.visitor_max}",
                [t],
            )
        )
    return failures


@register_check("ROSTER-20", "待确认招募名单合法")
def check_recruited_id_pool_validity() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能: recruited_id是"已招募待玩家确认"的暂存池，里面不该有0、不存在的id，也不该有已在编或身份冲突的人。
    同样用vistor != 1(两个写入点都取自find_recruitable_npc，vistor == 2可合法入池)
    """
    cache = cache_control.cache
    cd = cache.character_data
    ri = cache.rhodes_island
    warn = _sev(cache, False)
    failures: List[CheckFailure] = []
    for cid in ri.recruited_id:
        if cid == 0 or cid not in cd:
            failures.append(
                make_failure(
                    "ROSTER-20",
                    "待确认招募名单合法",
                    f"{warn}recruited_id中的cid={cid}非法(0号玩家或不存在于character_data)，全量recruited_id={sorted(x for x in ri.recruited_id if isinstance(x, int))}",
                    [cid] if isinstance(cid, int) else [],
                )
            )
            continue
        c = cd[cid]
        problems = []
        if cid in cache.npc_id_got:
            problems.append("已在npc_id_got在编名册中")
        if cid in ri.visitor_info:
            problems.append("已在ri.visitor_info访客名册中")
        if c.sp_flag.vistor == 1:
            problems.append("当前是在岛访客(vistor==1)")
        if c.sp_flag.imprisonment:
            problems.append("sp_flag.imprisonment为True")
        if c.sp_flag.escaping:
            problems.append("sp_flag.escaping为True")
        if c.sp_flag.field_commission:
            problems.append(f"sp_flag.field_commission={c.sp_flag.field_commission}非零")
        if c.position != ["0", "0"]:
            problems.append(f"position={c.position!r}未归零")
        if problems:
            failures.append(
                make_failure(
                    "ROSTER-20",
                    "待确认招募名单合法",
                    f"{warn}待确认招募cid={cid} name={c.name!r} adv={c.adv} {'; '.join(problems)}；"
                    f"len(npc_id_got)={len(cache.npc_id_got)}，people_max={ri.people_max}",
                    [cid],
                )
            )
    return failures


@register_check("ROSTER-21", "当前访客与其它名册身份互斥")
def check_visitor_identity_mutual_exclusion() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能: 当前访客不能同时是待确认招募、邀请目标、囚犯、逃犯或外勤队员 —— 这些身份的在线规则互相冲突。
    C集合的构造自带形状守卫，不依赖ROSTER-25先跑通过
    """
    cache = cache_control.cache
    cd = cache.character_data
    ri = cache.rhodes_island
    warn = _sev(cache, False)
    failures: List[CheckFailure] = []
    V = set(ri.visitor_info)
    P = set(ri.recruited_id)
    t = _invite_target(ri)
    I = {t} if t else set()
    C: Set[int] = set()
    for r in ri.ongoing_field_commissions.values():
        if isinstance(r, list) and r and isinstance(r[0], list):
            C |= set(r[0])
    R = set(ri.current_prisoners)
    E = {cid for cid, c in cd.items() if cid != 0 and c.sp_flag.escaping}
    named = {
        "待确认招募(recruited_id)": P,
        "邀请目标(invite_visitor)": I,
        "外勤中(ongoing_field_commissions)": C,
        "囚犯(current_prisoners)": R,
        "逃跑者(escaping)": E,
    }
    for cid in V:
        c = cd.get(cid)
        hit_names = [label for label, s in named.items() if cid in s]
        if hit_names:
            failures.append(
                make_failure(
                    "ROSTER-21",
                    "当前访客与其它名册身份互斥",
                    f"{warn}访客cid={cid} name={getattr(c, 'name', '?')!r} 同时命中身份集合: {hit_names}；"
                    f"vistor={getattr(getattr(c, 'sp_flag', None), 'vistor', None)}，recruited_id={sorted(P)}，"
                    f"invite_visitor={ri.invite_visitor!r}，cid in npc_id_got={cid in cache.npc_id_got}",
                    [cid],
                )
            )
    return failures


@register_check("ROSTER-22", "招募线记录形状与进度范围")
def check_recruit_line_shape_and_progress_range() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能: 每条recruit_line是[进度, 策略id, 主专员id, 效率]；进度与效率为非负有限数，策略与主专员为整数，
    进度上界<100由增量写入与结算相邻两行保证，不存在"已加未结"窗口。
    策略id子句依赖game_config.config_recruitment_strategy，若为空(独立环境未加载配置)则降级跳过该子句
    """
    cache = cache_control.cache
    ri = cache.rhodes_island
    warn = _sev(cache, False)
    failures: List[CheckFailure] = []
    strategy_ids = set(game_config.config_recruitment_strategy)
    for lid, rec in ri.recruit_line.items():
        problems = []
        if not isinstance(lid, int):
            problems.append(f"招募线id={lid!r}不是int")
        if not (isinstance(rec, list) and len(rec) == 4):
            failures.append(
                make_failure(
                    "ROSTER-22",
                    "招募线记录形状与进度范围",
                    f"{warn}招募线lid={lid!r}记录形状异常，期望长度4的list，实得{rec!r}",
                    [],
                )
            )
            continue
        progress, strategy, main_hr, eff = rec
        if isinstance(progress, bool) or not isinstance(progress, (int, float)) or not math.isfinite(progress) or not (0 <= progress < 100):
            problems.append(f"进度rec[0]={progress!r}不在[0,100)内、非有限数或被bool污染")
        if type(strategy) is not int:
            problems.append(f"策略id rec[1]={strategy!r}类型不是int")
        elif strategy_ids and strategy not in strategy_ids:
            problems.append(f"策略id rec[1]={strategy}不在game_config.config_recruitment_strategy中")
        if type(main_hr) is not int:
            problems.append(f"主专员id rec[2]={main_hr!r}类型不是int")
        if isinstance(eff, bool) or not isinstance(eff, (int, float)) or not math.isfinite(eff) or eff < 0:
            problems.append(f"效率rec[3]={eff!r}不是非负有限数")
        if problems:
            failures.append(
                make_failure(
                    "ROSTER-22",
                    "招募线记录形状与进度范围",
                    f"{warn}招募线lid={lid} record={rec!r} {'; '.join(problems)}；facility_level[7]={ri.facility_level.get(7)}，"
                    f"game_time={cache.game_time}",
                    [],
                )
            )
    return failures


@register_check("ROSTER-23", "招募线主专员真实可用且不重复")
def check_recruit_line_main_hr_validity_and_uniqueness() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能: 每条线第3位是主招聘专员：0(空缺)或一名工作类型71且在hr_operator_ids_list招聘专员列表内的角色；
    同一人不能同时主理两条线。不含cid in npc_id_got —— 派遣外勤不改work_type，把主专员派出去是常规操作，
    加在线子句必然长期误报
    """
    cache = cache_control.cache
    cd = cache.character_data
    ri = cache.rhodes_island
    warn = _sev(cache, False)
    failures: List[CheckFailure] = []
    mains = [
        rec[2]
        for rec in ri.recruit_line.values()
        if isinstance(rec, list) and len(rec) >= 3 and type(rec[2]) is int and rec[2] != 0
    ]
    dup = {cid for cid in mains if mains.count(cid) > 1}
    if dup:
        failures.append(
            make_failure(
                "ROSTER-23",
                "招募线主专员真实可用且不重复",
                f"{warn}以下角色同时是多条招募线的主专员(重复): {sorted(dup)}；完整recruit_line={dict(ri.recruit_line)}",
                sorted(dup),
            )
        )
    for cid in set(mains):
        problems = []
        c = cd.get(cid)
        if c is None:
            problems.append("不存在于character_data")
        else:
            if cid not in ri.hr_operator_ids_list:
                problems.append("不在ri.hr_operator_ids_list招聘专员列表中")
            if c.work.work_type != 71:
                problems.append(f"work.work_type={c.work.work_type}不是71")
        if problems:
            failures.append(
                make_failure(
                    "ROSTER-23",
                    "招募线主专员真实可用且不重复",
                    f"{warn}主专员cid={cid} name={getattr(c, 'name', '?')!r} {'; '.join(problems)}；"
                    f"field_commission={getattr(getattr(c, 'sp_flag', None), 'field_commission', None)}，"
                    f"cid in npc_id_got={cid in cache.npc_id_got}，hr_operator_ids_list={ri.hr_operator_ids_list}",
                    [cid],
                )
            )
    return failures


@register_check("ROSTER-24", "招聘专员列表无重复、成员岗位正确、在编71全部在内")
def check_hr_operator_list_integrity() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能: hr_operator_ids_list是增量维护的效率计算表。可断言的是：无重复、成员都是存在的非玩家角色且
    工作类型仍为71、所有在编的71号岗位都已收录。不做集合相等 —— 维护循环只遍历npc_id_got，结构上无法摘除
    离线成员，每次派遣必现列表残留，只保留"在编71 ⊆ 列表"这一个方向
    """
    cache = cache_control.cache
    cd = cache.character_data
    ri = cache.rhodes_island
    warn = _sev(cache, False)
    failures: List[CheckFailure] = []
    hr = ri.hr_operator_ids_list
    dup = {cid for cid in hr if hr.count(cid) > 1}
    if dup:
        failures.append(
            make_failure(
                "ROSTER-24",
                "招聘专员列表无重复、成员岗位正确、在编71全部在内",
                f"{warn}hr_operator_ids_list中存在重复id: {sorted(dup)}，完整列表={hr}",
                sorted(dup),
            )
        )
    for cid in set(hr):
        problems = []
        c = cd.get(cid)
        if cid == 0 or c is None:
            problems.append("为0号玩家或不存在于character_data")
        elif c.work.work_type != 71:
            problems.append(f"work.work_type={c.work.work_type}不是71")
        if problems:
            failures.append(
                make_failure(
                    "ROSTER-24",
                    "招聘专员列表无重复、成员岗位正确、在编71全部在内",
                    f"{warn}hr_operator_ids_list成员cid={cid} {'; '.join(problems)}；name={getattr(c, 'name', '?')!r}",
                    [cid],
                )
            )
    work71 = {cid for cid in cache.npc_id_got if cid != 0 and cid in cd and cd[cid].work.work_type == 71}
    for cid in work71 - set(hr):
        c = cd[cid]
        failures.append(
            make_failure(
                "ROSTER-24",
                "招聘专员列表无重复、成员岗位正确、在编71全部在内",
                f"{warn}在编71号岗位角色cid={cid} name={c.name!r} 未被收录进hr_operator_ids_list；"
                f"field_commission={c.sp_flag.field_commission}，in_diplomatic_visit={c.sp_flag.in_diplomatic_visit}",
                [cid],
            )
        )
    return failures


@register_check("ROSTER-25", "进行中委托记录结构合法、人员全局唯一")
def check_ongoing_commission_shape_and_member_uniqueness() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能: 每条记录是[干员id列表, 返回时间, 载具id列表]；同一人不能在单条记录里重复，也不能同时出现在两个委托里
    """
    cache = cache_control.cache
    ri = cache.rhodes_island
    warn = _sev(cache, False)
    failures: List[CheckFailure] = []
    seen: Dict[int, int] = {}
    for mid, r in ri.ongoing_field_commissions.items():
        problems = []
        if not (isinstance(mid, int) and mid != 0):
            problems.append(f"委托id={mid!r}非法(应为非零int)")
        if not (isinstance(r, list) and len(r) == 3):
            failures.append(
                make_failure(
                    "ROSTER-25",
                    "进行中委托记录结构合法、人员全局唯一",
                    f"{warn}委托mid={mid!r}记录形状异常，期望长度3的list，实得{r!r}",
                    [],
                )
            )
            continue
        members, ret_time, vehicles = r[0], r[1], r[2]
        if not isinstance(members, list):
            problems.append(f"r[0]={members!r}不是list")
        if not isinstance(ret_time, datetime.datetime):
            problems.append(f"r[1]={ret_time!r}不是datetime")
        if not isinstance(vehicles, list):
            problems.append(f"r[2]={vehicles!r}不是list")
        involved: List[int] = []
        if isinstance(members, list):
            if len(members) != len(set(members)):
                problems.append(f"r[0]内部有重复干员id: {members}")
            dup_across = set(members) & set(seen)
            if dup_across:
                problems.append(f"以下干员同时出现在别的委托中: {[(cid, seen[cid]) for cid in dup_across]}")
            for cid in members:
                seen.setdefault(cid, mid)
                involved.append(cid)
        if problems:
            failures.append(
                make_failure(
                    "ROSTER-25",
                    "进行中委托记录结构合法、人员全局唯一",
                    f"{warn}委托mid={mid} {'; '.join(problems)}；完整record={r!r}，game_time={cache.game_time}",
                    involved,
                )
            )
    return failures


@register_check("ROSTER-26", "外勤名单与角色外勤flag双向一致")
def check_field_commission_membership_flag_consistency() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能: 派遣时逐人写sp_flag.field_commission = 委托id，结算时逐人清0再上线。两侧必须互指同一委托，
    任一单向残留都要报出来。真实可达捕获点：本地外交官被派出外勤后基地返回该国时会对他调handle_chara_on_line，
    整体重建sp_flag把field_commission抹成0并塞回名册，而委托记录里还挂着他
    """
    cache = cache_control.cache
    cd = cache.character_data
    ri = cache.rhodes_island
    warn = _sev(cache, False)
    failures: List[CheckFailure] = []
    membership_scene = _scene_membership(cache)
    membership: Dict[int, int] = {}
    for mid, r in ri.ongoing_field_commissions.items():
        if not (isinstance(r, list) and r and isinstance(r[0], list)):
            continue
        for cid in r[0]:
            if cid == 0 or cid not in cd:
                failures.append(
                    make_failure(
                        "ROSTER-26",
                        "外勤名单与角色外勤flag双向一致",
                        f"{warn}委托mid={mid}人员列表含非法cid={cid}",
                        [cid] if isinstance(cid, int) else [],
                    )
                )
                continue
            c = cd[cid]
            if c.sp_flag.field_commission != mid:
                failures.append(
                    make_failure(
                        "ROSTER-26",
                        "外勤名单与角色外勤flag双向一致",
                        f"{warn}委托mid={mid}人员cid={cid} name={c.name!r} 的sp_flag.field_commission={c.sp_flag.field_commission}"
                        f"与所属委托不一致；cid in npc_id_got={cid in cache.npc_id_got}，position={c.position}，"
                        f"命中场景={membership_scene.get(cid, [])}",
                        [cid],
                    )
                )
            membership[cid] = mid
    flagged = {cid for cid, c in cd.items() if cid != 0 and c.sp_flag.field_commission}
    for cid in flagged - set(membership):
        c = cd[cid]
        failures.append(
            make_failure(
                "ROSTER-26",
                "外勤名单与角色外勤flag双向一致",
                f"{warn}角色cid={cid} name={c.name!r} sp_flag.field_commission={c.sp_flag.field_commission}非零，"
                f"但未出现在任何委托记录的人员列表中；cid in npc_id_got={cid in cache.npc_id_got}，position={c.position}，"
                f"命中场景={membership_scene.get(cid, [])}",
                [cid],
            )
        )
    return failures


@register_check("ROSTER-27", "外勤人员不得兼任访客/囚犯/助理/监狱长/招募目标")
def check_field_commission_member_identity_exclusion() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能: 派遣候选表显式排除访客、助理、监狱长以及2类(临盆/产后/监禁)、7类(离线)异常；待确认招募与
    邀请目标本就不在在编名册内。这些身份同时成立意味着有别的流程绕过了派遣面板
    """
    cache = cache_control.cache
    cd = cache.character_data
    ri = cache.rhodes_island
    warn = _sev(cache, False)
    failures: List[CheckFailure] = []
    C: Set[int] = set()
    commission_of: Dict[int, int] = {}
    for mid, r in ri.ongoing_field_commissions.items():
        if isinstance(r, list) and r and isinstance(r[0], list):
            for cid in r[0]:
                C.add(cid)
                commission_of.setdefault(cid, mid)
    t = _invite_target(ri)
    player = cd.get(0)
    assistant = getattr(player, "assistant_character_id", 0) if player is not None else 0
    forbidden = {
        "访客(visitor_info)": set(ri.visitor_info),
        "待确认招募(recruited_id)": set(ri.recruited_id),
        "囚犯(current_prisoners)": set(ri.current_prisoners),
        "邀请目标(invite_visitor)": {t} if t else set(),
        "监狱长(current_warden_id)": {ri.current_warden_id} if ri.current_warden_id else set(),
        "逃跑者(escaping)": {cid for cid, c in cd.items() if cid != 0 and c.sp_flag.escaping},
        "助理(assistant_character_id)": {assistant} if assistant else set(),
    }
    for cid in C:
        c = cd.get(cid)
        hit = [label for label, s in forbidden.items() if cid in s]
        if hit:
            failures.append(
                make_failure(
                    "ROSTER-27",
                    "外勤人员不得兼任访客/囚犯/助理/监狱长/招募目标",
                    f"{warn}外勤中cid={cid} name={getattr(c, 'name', '?')!r}(委托mid={commission_of.get(cid)}) 同时命中身份集合: {hit}；"
                    f"work.work_type={getattr(getattr(c, 'work', None), 'work_type', None)}，current_warden_id={ri.current_warden_id}，"
                    f"assistant_character_id={assistant}，dormitory={getattr(c, 'dormitory', None)}",
                    [cid],
                )
            )
        if c is not None:
            if c.sp_flag.vistor == 1:
                failures.append(
                    make_failure(
                        "ROSTER-27",
                        "外勤人员不得兼任访客/囚犯/助理/监狱长/招募目标",
                        f"{warn}外勤中cid={cid} name={c.name!r}(委托mid={commission_of.get(cid)}) sp_flag.vistor==1(当前在岛访客)",
                        [cid],
                    )
                )
            if c.sp_flag.imprisonment:
                failures.append(
                    make_failure(
                        "ROSTER-27",
                        "外勤人员不得兼任访客/囚犯/助理/监狱长/招募目标",
                        f"{warn}外勤中cid={cid} name={c.name!r}(委托mid={commission_of.get(cid)}) sp_flag.imprisonment为True",
                        [cid],
                    )
                )
    return failures


@register_check("ROSTER-28", "载具外勤中数与委托明细守恒")
def check_vehicle_busy_count_conservation() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能: vehicles[vid] = [拥有数, 外勤中数]；外勤中数必须等于所有进行中委托里该型号载具的出现次数，
    且不超过拥有数。调用顺序安全(先settle_vehicle再pop委托)，计数错误会直接表现为"有车却派不出去"或负库存
    """
    cache = cache_control.cache
    ri = cache.rhodes_island
    warn = _sev(cache, False)
    failures: List[CheckFailure] = []
    used = collections.Counter()
    for r in ri.ongoing_field_commissions.values():
        if isinstance(r, list) and len(r) == 3 and isinstance(r[2], list):
            used.update(r[2])
    for vid in set(used) - set(ri.vehicles):
        failures.append(
            make_failure(
                "ROSTER-28",
                "载具外勤中数与委托明细守恒",
                f"{warn}委托明细中出现的载具vid={vid}未在ri.vehicles中登记，使用次数={used[vid]}",
                [],
            )
        )
    for vid, v in ri.vehicles.items():
        if not (isinstance(v, list) and len(v) == 2 and all(type(x) is int for x in v)):
            failures.append(
                make_failure(
                    "ROSTER-28",
                    "载具外勤中数与委托明细守恒",
                    f"{warn}ri.vehicles[{vid}]形状异常，期望[拥有数,外勤中数]两个int，实得{v!r}",
                    [],
                )
            )
            continue
        own, busy = v[0], v[1]
        u = used.get(vid, 0)
        if not (0 <= busy <= own):
            failures.append(
                make_failure(
                    "ROSTER-28",
                    "载具外勤中数与委托明细守恒",
                    f"{warn}载具vid={vid} 外勤中数busy={busy}不在[0,拥有数own={own}]范围内",
                    [],
                )
            )
        if busy != u:
            detail = {mid: r[2] for mid, r in ri.ongoing_field_commissions.items() if isinstance(r, list) and len(r) == 3}
            failures.append(
                make_failure(
                    "ROSTER-28",
                    "载具外勤中数与委托明细守恒",
                    f"{warn}载具vid={vid} 缓存外勤中数busy={busy}与委托明细实际出现次数{u}不一致，vehicles[{vid}]={v}，"
                    f"委托载具明细={detail}",
                    [],
                )
            )
    return failures


@register_check("ROSTER-29", "进行中委托id有效且未逾期")
def check_ongoing_commission_id_valid_and_not_overdue() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能: 委托完成判定在每个非时停玩家回合的行为树里先于NPC结算跑一次，回合结束时留下的委托必须严格
    满足end_time > game_time(> 而非 >=，恰好到点的委托按完成条件本应已结算)；逾期判定排除debug_mode与time_stop_mode。
    id有效性依赖game_config.config_commission，若为空(独立环境未加载配置)则降级跳过该子句，仅保留结构与逾期判定
    """
    cache = cache_control.cache
    ri = cache.rhodes_island
    warn = _sev(cache, False)
    failures: List[CheckFailure] = []
    config_loaded = bool(game_config.config_commission)
    for mid, r in ri.ongoing_field_commissions.items():
        if config_loaded and mid not in game_config.config_commission:
            failures.append(
                make_failure(
                    "ROSTER-29",
                    "进行中委托id有效且未逾期",
                    f"{warn}进行中委托mid={mid}在game_config.config_commission中查不到配置",
                    [],
                )
            )
        if not (isinstance(r, list) and len(r) == 3):
            failures.append(
                make_failure(
                    "ROSTER-29",
                    "进行中委托id有效且未逾期",
                    f"{warn}委托mid={mid}记录形状异常，期望长度3的list，实得{r!r}",
                    [],
                )
            )
            continue
        end_time = r[1]
        if not isinstance(end_time, datetime.datetime):
            failures.append(
                make_failure(
                    "ROSTER-29", "进行中委托id有效且未逾期", f"{warn}委托mid={mid}的结束时间r[1]={end_time!r}不是datetime", []
                )
            )
            continue
        if not cache.debug_mode and not cache.time_stop_mode:
            if not (end_time > cache.game_time):
                overdue = cache.game_time - end_time
                members = r[0] if isinstance(r[0], list) else []
                failures.append(
                    make_failure(
                        "ROSTER-29",
                        "进行中委托id有效且未逾期",
                        f"{warn}委托mid={mid}已到期或逾期，end_time={end_time}，game_time={cache.game_time}，逾期时长={overdue}；"
                        f"人员={members}，finished_field_commissions_set={ri.finished_field_commissions_set}",
                        members,
                    )
                )
    return failures


@register_check("ROSTER-30", "外交官表与角色外派flag双向一致")
def check_diplomat_registry_and_flag_consistency() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能: 任命写diplomat_of_country[国家][0] = id与sp_flag.in_diplomatic_visit = 国家，解任同时清两者。
    外派到非当前所在国的外交官处于离线态，罗德岛抵达该国时会让他上线。本条大概率会报出真实缺陷：
    handle_chara_on_line整体重建sp_flag会把in_diplomatic_visit抹成0
    """
    cache = cache_control.cache
    cd = cache.character_data
    ri = cache.rhodes_island
    warn = _sev(cache, False)
    failures: List[CheckFailure] = []
    current_country = ri.current_location[0] if isinstance(ri.current_location, list) and ri.current_location else None
    for country, info in ri.diplomat_of_country.items():
        if not (isinstance(info, list) and len(info) >= 1):
            failures.append(
                make_failure(
                    "ROSTER-30",
                    "外交官表与角色外派flag双向一致",
                    f"{warn}diplomat_of_country[{country}]形状异常，期望非空list，实得{info!r}",
                    [],
                )
            )
            continue
        did = info[0]
        if type(did) is not int:
            failures.append(
                make_failure(
                    "ROSTER-30",
                    "外交官表与角色外派flag双向一致",
                    f"{warn}diplomat_of_country[{country}][0]={did!r}类型不是int",
                    [],
                )
            )
            continue
        if not did:
            continue
        if did not in cd:
            failures.append(
                make_failure(
                    "ROSTER-30",
                    "外交官表与角色外派flag双向一致",
                    f"{warn}国家{country}的外交官did={did}不存在于character_data中",
                    [did],
                )
            )
            continue
        c = cd[did]
        problems = []
        if c.sp_flag.in_diplomatic_visit != country:
            problems.append(f"sp_flag.in_diplomatic_visit={c.sp_flag.in_diplomatic_visit}与所属国家{country}不一致")
        if current_country is not None:
            if country != current_country:
                if did in cache.npc_id_got:
                    problems.append(f"外派到非当前所在国({country}!={current_country})但仍在npc_id_got在编名册中")
            else:
                if did not in cache.npc_id_got:
                    problems.append(f"外派国家与当前所在国一致({country})但不在npc_id_got在编名册中")
        if problems:
            failures.append(
                make_failure(
                    "ROSTER-30",
                    "外交官表与角色外派flag双向一致",
                    f"{warn}国家{country}外交官did={did} name={c.name!r} {'; '.join(problems)}；"
                    f"work.work_type={c.work.work_type}，current_location={ri.current_location}，position={c.position}",
                    [did],
                )
            )
    for cid, c in cd.items():
        if cid == 0 or not c.sp_flag.in_diplomatic_visit:
            continue
        slot = ri.diplomat_of_country.get(c.sp_flag.in_diplomatic_visit, [0])
        if not (isinstance(slot, list) and slot and slot[0] == cid):
            failures.append(
                make_failure(
                    "ROSTER-30",
                    "外交官表与角色外派flag双向一致",
                    f"{warn}角色cid={cid} name={c.name!r} sp_flag.in_diplomatic_visit={c.sp_flag.in_diplomatic_visit}，"
                    f"但diplomat_of_country[{c.sp_flag.in_diplomatic_visit}]={slot!r}的槽位[0]不指回该角色",
                    [cid],
                )
            )
    return failures


@register_check("ROSTER-31", "异常位掩码与其来源状态一致(第2、7位)")
def check_unnormal_flag_mask_consistency() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能: sp_flag.unnormal_flag是带"已知/未知"两层的位掩码缓存，第2位=AI停止(临盆/产后/监禁)，
    第7位=离线(装袋/外勤/婴儿/异国外派/逃跑)。定为warning是因为这是懒缓存：check()不看known位，未知即读作False，
    且只覆盖在线角色的每日重算；只做单向蕴含(有离线来源⟹该位为真)，并跳过临盆/产后(talent[22]/[23]，属素质域)
    """
    cache = cache_control.cache
    cd = cache.character_data
    warn = _sev(cache, True)
    failures: List[CheckFailure] = []
    for cid, c in cd.items():
        if cid == 0:
            continue
        m = c.sp_flag.unnormal_flag
        if not isinstance(m, game_type.UnnormalFlagMask):
            continue
        if m.is_known(2) and not (c.talent.get(22) or c.talent.get(23)):
            if m.check(2) != bool(c.sp_flag.imprisonment):
                failures.append(
                    make_failure(
                        "ROSTER-31",
                        "异常位掩码与其来源状态一致(第2、7位)",
                        f"{warn}角色cid={cid} name={c.name!r} 异常位2(AI停止)缓存check(2)={m.check(2)}与来源imprisonment={c.sp_flag.imprisonment}不符；"
                        f"talent[22]={c.talent.get(22)}，talent[23]={c.talent.get(23)}，cid in npc_id_got={cid in cache.npc_id_got}",
                        [cid],
                    )
                )
        if m.is_known(7) and (c.sp_flag.be_bagged or c.sp_flag.field_commission or c.sp_flag.escaping):
            if not m.check(7):
                failures.append(
                    make_failure(
                        "ROSTER-31",
                        "异常位掩码与其来源状态一致(第2、7位)",
                        f"{warn}角色cid={cid} name={c.name!r} 有离线来源(be_bagged={c.sp_flag.be_bagged}, "
                        f"field_commission={c.sp_flag.field_commission}, escaping={c.sp_flag.escaping})，但异常位7(离线)缓存"
                        f"check(7)={m.check(7)}为False；in_diplomatic_visit={c.sp_flag.in_diplomatic_visit}，"
                        f"cid in npc_id_got={cid in cache.npc_id_got}",
                        [cid],
                    )
                )
    return failures


@register_check("ROSTER-32", "助理身份互斥")
def check_assistant_identity_exclusion() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能: 助理候选排除访客、监狱长以及2/7类异常。各写入点都做了过滤，且统一离线流程会调
    handle_assistant_reset把离线角色从助理位清掉 —— 命中即为某个任命流程漏清身份的真实问题
    """
    cache = cache_control.cache
    cd = cache.character_data
    ri = cache.rhodes_island
    warn = _sev(cache, False)
    failures: List[CheckFailure] = []
    player = cd.get(0)
    if player is None:
        return failures
    a = getattr(player, "assistant_character_id", 0)
    if type(a) is not int:
        failures.append(make_failure("ROSTER-32", "助理身份互斥", f"{warn}cd[0].assistant_character_id类型异常: {a!r}", []))
        return failures
    if not a:
        return failures
    if a not in cd:
        failures.append(make_failure("ROSTER-32", "助理身份互斥", f"{warn}助理a={a}不存在于character_data中", [a]))
        return failures
    ca = cd[a]
    problems = []
    if a not in cache.npc_id_got:
        problems.append("不在npc_id_got在编名册中")
    if a in ri.visitor_info or ca.sp_flag.vistor == 1:
        problems.append(f"当前是访客(a in visitor_info={a in ri.visitor_info}, vistor={ca.sp_flag.vistor})")
    if a == ri.current_warden_id:
        problems.append("同时是current_warden_id监狱长")
    if a in ri.current_prisoners or ca.sp_flag.imprisonment:
        problems.append("同时是囚犯(在current_prisoners中或imprisonment为True)")
    if ca.sp_flag.field_commission:
        problems.append(f"field_commission={ca.sp_flag.field_commission}非零(外勤中)")
    if ca.sp_flag.escaping:
        problems.append("sp_flag.escaping为True")
    if ca.sp_flag.be_bagged:
        problems.append("sp_flag.be_bagged为True")
    if problems:
        failures.append(
            make_failure(
                "ROSTER-32",
                "助理身份互斥",
                f"{warn}助理a={a} name={ca.name!r} {'; '.join(problems)}",
                [a],
            )
        )
    return failures


@register_check("ROSTER-33", "装袋双方记录双向一致")
def check_bagging_pair_consistency() -> List[CheckFailure]:
    """
    参数: 无
    返回值: List[CheckFailure]: 失败记录列表
    功能: 玩家的sp_flag.bagging_chara_id与被搬运者的sp_flag.be_bagged必须互指；被装袋者必须离线，
    且不能同时是囚犯、访客、外勤或逃跑者。这对flag分居玩家与目标两个对象，是本域内最容易单边脱钩的一对
    """
    cache = cache_control.cache
    cd = cache.character_data
    ri = cache.rhodes_island
    warn = _sev(cache, False)
    failures: List[CheckFailure] = []
    player = cd.get(0)
    if player is None:
        return failures
    b = getattr(player.sp_flag, "bagging_chara_id", 0)
    if type(b) is not int:
        failures.append(make_failure("ROSTER-33", "装袋双方记录双向一致", f"{warn}cd[0].sp_flag.bagging_chara_id类型异常: {b!r}", []))
        return failures
    bagged = {cid for cid, c in cd.items() if cid != 0 and c.sp_flag.be_bagged}
    expected = {b} if b else set()
    for cid in bagged - expected:
        c = cd[cid]
        failures.append(
            make_failure(
                "ROSTER-33",
                "装袋双方记录双向一致",
                f"{warn}角色cid={cid} name={c.name!r} sp_flag.be_bagged=True，但玩家bagging_chara_id={b}未指向它",
                [cid],
            )
        )
    for cid in expected - bagged:
        c = cd.get(cid)
        failures.append(
            make_failure(
                "ROSTER-33",
                "装袋双方记录双向一致",
                f"{warn}玩家bagging_chara_id={b}指向cid={cid}，但该角色sp_flag.be_bagged不为True；name={getattr(c, 'name', '?')!r}",
                [cid],
            )
        )
    if b and b in cd:
        membership = _scene_membership(cache)
        c = cd[b]
        problems = []
        if b in cache.npc_id_got:
            problems.append("仍在npc_id_got在编名册中")
        hit = membership.get(b, [])
        if hit:
            problems.append(f"仍残留在场景{hit}中")
        if c.position != ["0", "0"]:
            problems.append(f"position={c.position!r}未归零")
        if b in ri.current_prisoners or c.sp_flag.imprisonment:
            problems.append("同时是囚犯(current_prisoners或imprisonment)")
        if b in ri.visitor_info or c.sp_flag.vistor == 1:
            problems.append("同时是访客(visitor_info或vistor==1)")
        if c.sp_flag.field_commission:
            problems.append(f"field_commission={c.sp_flag.field_commission}非零")
        if c.sp_flag.escaping:
            problems.append("sp_flag.escaping为True")
        if problems:
            failures.append(
                make_failure(
                    "ROSTER-33",
                    "装袋双方记录双向一致",
                    f"{warn}被装袋者b={b} name={c.name!r} {'; '.join(problems)}；玩家position={player.position}",
                    [b],
                )
            )
    return failures
