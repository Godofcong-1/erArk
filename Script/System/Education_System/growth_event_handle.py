"""养成事件：公务事件系统里「教育区」这个部门的候选提供者（Plan 23 方案 §3.2）

通用的入队/出队/结算/履历都在 `Script/System/Official_Event_System/official_event_handle.py`，
这里只留养成专属的三件事：

    1. 候选从**玩家的女儿**里找，按成长阶段分桶（本阶段桶 + 跨阶段的通用桶）
    2. 互动对象从兄弟姐妹或同班同学里挑（事件里的 A2 于是指向本次事件的对手）
    3. 事件抬头写成「薇薇安 · 萝莉期第 38 天」

触发频率（方案 §3.4）：**按女儿逐个判定**，每个女儿每天最多 1 条、有 70% 的概率派到，
于是单个女儿约一两天一条，女儿越多每天的事件越多，但总量仍受公务事件系统的全局硬顶约束。
"""
import random
from types import FunctionType
from typing import List

from Script.Core import cache_control, game_type, get_text
from Script.Config import game_config
from Script.System.Education_System import education_constant
from Script.System.Official_Event_System import official_event_handle

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """


def get_character_stage(character_id: int) -> int:
    """
    取角色当前的成长阶段素质id（统一走 growth_handle 的实现，按素质id升序取，萝莉化设定下结果也确定）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 101婴儿/102幼女/103萝莉/104少女，都不是则0
    """
    from Script.System.Education_System import growth_handle

    return growth_handle.get_character_stage(character_id)


def get_growth_event_character_list() -> List[int]:
    """
    取本次入队要遍历的角色列表

    只看玩家的女儿：普通干员也可能因为选课被建出 child_growth（口径24），
       但养成事件是给孩子的，给成年干员派「第一次上课」只会显得莫名其妙
    只看婴儿~萝莉（101~103）：已成年的少女没有日常养成事件可派，毕业典礼与成年纪念由成年结算显式推入；
       算进来会让每个成年女儿永久多占 4 条队列容量，旧档里早就成年的女儿还会被每日派发随机抽中毕业典礼（2026-09-12 第五轮）
    遍历全部角色，婴儿不看 npc_id_got（Plan 28 §3.1）：婴儿从出生到长成幼女都不上线——
       character_handle.born_new_character 不把她加进 npc_id_got，长成幼女时 get_new_character 才加。
       此前只遍历 npc_id_got，婴儿桶的事件一条都派不出来，队列容量里也没有婴儿的份。
       幼女 / 萝莉仍要求在 npc_id_got 里：离线的不派
    Keyword arguments:
    无
    Return arguments:
    List[int] -- 角色id列表，按id升序
    """
    from Script.Design import handle_premise

    result = []
    for character_id in sorted(cache.character_data):
        # 玩家自己不参与
        if character_id == 0:
            continue
        stage = get_character_stage(character_id)
        if stage not in education_constant.STAGE_ALL_CHILD:
            continue
        if stage != 101 and character_id not in cache.npc_id_got:
            continue
        if not handle_premise.handle_self_is_player_daughter(character_id):
            continue
        result.append(character_id)
    return result


def get_sibling_child_list(character_id: int) -> List[int]:
    """
    取能一起玩的兄弟姐妹列表（只取幼女 / 萝莉，Plan 26 §3.9）

    直接读既有的 relationship，不新建亲缘结构：同父同母、同父异母都算兄弟姐妹，
       判据是「父亲相同或母亲相同」
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    List[int] -- 兄弟姐妹的角色id列表
    """
    character_data: game_type.Character = cache.character_data[character_id]
    father_id = character_data.relationship.father_id
    mother_id = character_data.relationship.mother_id
    # 双亲未登记时是 -1，两个都没登记的角色会互相认成兄弟姐妹（世界设定的萝莉化会给一大批
    #    干员挂上萝莉素质，正好撞进这个洞），所以只认有效的双亲id
    result = []
    for other_id in cache.npc_id_got:
        if other_id == character_id:
            continue
        # 互动事件写的都是能一起玩、一起闯祸的孩子，婴儿和已成年的少女都不合适
        if get_character_stage(other_id) not in education_constant.SIBLING_PLAY_STAGE_SET:
            continue
        other_data: game_type.Character = cache.character_data[other_id]
        if father_id >= 0 and other_data.relationship.father_id == father_id:
            result.append(other_id)
        elif mother_id >= 0 and other_data.relationship.mother_id == mother_id:
            result.append(other_id)
    return result


def get_classmate_list(character_id: int) -> List[int]:
    """
    取同班同学列表：个人课表上有重合节次的其他孩子

    同学关系由课表反查，不落成字段——课表一改，同学关系就跟着变，
       存成字段反而要多一处同步点
    只认双方都在学生岗、且那一格是每周确有的课（Plan 30 §3.6，growth_handle.judge_selected_cell_real）：
       改了岗的女儿课表残留、已停课的格子、上不成的个人式课都还躺在课表上，那都不是在一起上课
    对方只取幼女 / 萝莉（Plan 31 §3.11，与同胞同口径）：同学事件写的都是能一起玩的孩子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    List[int] -- 同学的角色id列表
    """
    from Script.System.Education_System import growth_handle

    growth_data = cache.character_data[character_id].child_growth
    if growth_data is None or not growth_data.selected_course:
        return []
    # 把自己确有的课压成 (星期, 节次, 课型, 目标) 的集合，再看别人有没有在同一个格子上确有这节课
    self_slot = set()
    for week_day, day_data in growth_data.selected_course.items():
        for period, course in day_data.items():
            if growth_handle.judge_selected_cell_real(character_id, week_day, period):
                self_slot.add((week_day, period, course[0], str(course[1])))
    if not self_slot:
        return []
    result = []
    for other_id in cache.npc_id_got:
        if other_id == character_id:
            continue
        # 只取幼女 / 萝莉（Plan 31 §3.11，与同胞同口径，Plan 26 口径 5）：仍在学生岗的成年姐姐与妹妹同班时，
        #    会被点成幼女 41「班上的{TargetName}」这类事件的对象；婴儿不上学，本就没有课表
        if get_character_stage(other_id) not in education_constant.SIBLING_PLAY_STAGE_SET:
            continue
        other_growth = cache.character_data[other_id].child_growth
        if other_growth is None or not other_growth.selected_course:
            continue
        for week_day, day_data in other_growth.selected_course.items():
            hit = False
            for period, course in day_data.items():
                if (week_day, period, course[0], str(course[1])) in self_slot and growth_handle.judge_selected_cell_real(other_id, week_day, period):
                    result.append(other_id)
                    hit = True
                    break
            if hit:
                break
    return result


def get_event_partner(uid: str, character_id: int) -> int:
    """
    按事件前提挑一个互动对象

    没有互动对象需求时返回0（玩家）——事件里的 A2 于是指向博士，这是绝大多数事件的情形。
    Keyword arguments:
    uid -- 事件uid
    character_id -- 孩子角色id
    Return arguments:
    int -- 互动对象角色id，无则0
    """
    from Script.Core import constant_promise

    event_data = official_event_handle.get_event_data(uid)
    if event_data is None:
        return 0
    premise_text = event_data.get("premise", "")
    candidate = []
    if constant_promise.Premise.SELF_HAVE_SIBLING_CHILD in premise_text:
        candidate = get_sibling_child_list(character_id)
    elif constant_promise.Premise.SELF_HAVE_CLASSMATE in premise_text:
        candidate = get_classmate_list(character_id)
    if not candidate:
        return 0
    return random.choice(candidate)


def judge_stage_pass(uid: str, character_id: int) -> bool:
    """
    判定一条养成事件的适用阶段与孩子当前的成长阶段是否对得上
    Keyword arguments:
    uid -- 事件uid
    character_id -- 孩子角色id
    Return arguments:
    bool -- 阶段是否匹配
    """
    event_data = official_event_handle.get_event_data(uid)
    if event_data is None:
        return False
    sub_key = event_data.get("sub_key", education_constant.STAGE_ANY)
    now_stage = get_character_stage(character_id)
    # sub_key 为 0 时覆盖全部未成年阶段，写了具体阶段就只派给该阶段
    if sub_key == education_constant.STAGE_ANY:
        return now_stage in education_constant.STAGE_ALL_CHILD
    return sub_key == now_stage


def get_candidate_event_list(character_id: int) -> List[list]:
    """
    列出这个孩子当前可触发的全部事件
    Keyword arguments:
    character_id -- 孩子角色id
    Return arguments:
    List[list] -- [事件uid str, 权重 int, 互动对象id int] 的列表
    """
    result = []
    now_stage = get_character_stage(character_id)
    # 只翻本阶段桶与通用桶，不遍历全表
    for sub_key in (education_constant.STAGE_ANY, now_stage):
        for uid in game_config.config_official_event_by_sub_key.get((education_constant.GROWTH_EVENT_DEPARTMENT, sub_key), ()):
            if not official_event_handle.judge_event_can_enqueue(uid, character_id):
                continue
            if not judge_stage_pass(uid, character_id):
                continue
            event_data = game_config.config_official_event[uid]
            partner_id = get_event_partner(uid, character_id)
            now_weight = official_event_handle.judge_premise_pass(event_data.get("premise", ""), character_id, partner_id)
            if not now_weight:
                continue
            # 配置权重与前提权重相乘：前提里的 high_ 系列照样能拉高稀有事件的出场率
            result.append([uid, official_event_handle.get_event_weight(uid) * now_weight, partner_id])
    return result


@official_event_handle.register_provider(education_constant.GROWTH_EVENT_DEPARTMENT)
def get_today_growth_event_pick_list() -> List[dict]:
    """
    每日结算时给出今日的养成事件候选（已按女儿逐个节流）

    遍历前先 shuffle：撞上公务事件系统的全局硬顶时，不打散的话永远是 id 小的那几个女儿吃满名额
    Keyword arguments:
    无
    Return arguments:
    List[dict] -- [{"uid": str, "chara_id": int, "partner_id": int}, ...]
    """
    character_list = get_growth_event_character_list()
    random.shuffle(character_list)
    result = []
    for character_id in character_list:
        # 每个女儿每天只有一定概率派到事件，于是单个女儿约一两天一条
        if random.randint(1, 100) > education_constant.GROWTH_EVENT_DAILY_CHANCE:
            continue
        candidate = get_candidate_event_list(character_id)
        if not candidate:
            continue
        for _index in range(education_constant.GROWTH_EVENT_DAILY_MAX_PER_CHILD):
            if not candidate:
                break
            weight_list = [one[1] for one in candidate]
            chosen = random.choices(candidate, weights=weight_list, k=1)[0]
            candidate.remove(chosen)
            result.append({"uid": chosen[0], "chara_id": character_id, "partner_id": chosen[2]})
    return result


@official_event_handle.register_capacity(education_constant.GROWTH_EVENT_DEPARTMENT)
def get_growth_event_queue_capacity() -> int:
    """
    养成事件为公务队列贡献的容量：每个女儿 4 条
    Keyword arguments:
    无
    Return arguments:
    int -- 容量
    """
    return education_constant.GROWTH_EVENT_QUEUE_PER_CHILD * len(get_growth_event_character_list())


@official_event_handle.register_title(education_constant.GROWTH_EVENT_DEPARTMENT)
def get_growth_event_title(queue_data: dict) -> str:
    """
    取养成事件的抬头："薇薇安 · 萝莉期第 38 天"
    Keyword arguments:
    queue_data -- 队列元素dict
    Return arguments:
    str -- 抬头文本
    """
    from Script.System.Education_System import growth_handle

    character_id = queue_data.get("chara_id", 0)
    if character_id not in cache.character_data:
        return official_event_handle.get_department_name(education_constant.GROWTH_EVENT_DEPARTMENT)
    character_data: game_type.Character = cache.character_data[character_id]
    stage = get_character_stage(character_id)
    # STAGE_TALENT_NAME 取自 Talent.csv，载入时已翻译过，不再包 _()
    stage_name = education_constant.STAGE_TALENT_NAME.get(stage, education_constant.STAGE_TALENT_NAME[104])
    # 写的是**本阶段**的第几天，进入该阶段当天为第 1 天（Plan 29 §3.3）：
    #    此前取出生以来的总天数，出生 300 天的萝莉会写成「萝莉期第 300 天」，而萝莉期一共才 180 天。
    #    数的是可游玩天（Plan 32 §3.2）：婴儿期约 30 天、幼女 / 萝莉期约 60 天，季月交替那一夜只走一天，不再一夜跳六十天
    stage_day = growth_handle.get_stage_day(character_id) + 1
    return _("{0} · {1}期第 {2} 天").format(character_data.name, stage_name, stage_day)


def push_graduation_event(character_id: int):
    """
    成年结算时把毕业典礼与成年纪念插到队首，再把成年后的里程碑事件（通用 59 / 60）推到队尾

    **不做成玩家指令**（口径44）：一辈子只触发一次的叙事节点，
       做成指令要配行为、时长、口上、前提一整套，事件系统的一次性叙事正是为此而生
    插队首而不是追加：成年是叙事上的大节点，让它排在一堆日常事件后面会很怪
    幂等由成年结算本身的守卫保证（素质 103→104，一个孩子只会经过一次）
    成年桶（sub_key 104）只有这里显式推入的事件会出现（Plan 31 §3.2）：日常派发名单只收 101~103（第五轮），
       默认提供者又跳过部门 15。通用 59 / 60 此前没有入口，永远推不出来
    Keyword arguments:
    character_id -- 刚成年的孩子角色id
    Return arguments:
    无
    """
    # 倒序插入，使毕业典礼最终排在成年纪念之前
    official_event_handle.push_official_event(education_constant.ADULT_MEMORIAL_EVENT_UID, character_id, to_front=True)
    official_event_handle.push_official_event(education_constant.GRADUATION_EVENT_UID, character_id, to_front=True)
    # 通用 59 / 60（人事送来干员编号、第一次以干员身份报到）按普通顺序推到队尾（Plan 31 §3.2）：
    #    成年当天先看到毕业典礼与成年纪念，之后处理公务时再遇到这两条。
    #    仍过 judge_event_can_enqueue：已触发过、已在队列里的不重复推。
    #    不受队列容量上限约束：与毕业典礼、成年纪念一样一辈子只有这一次入口，成年那一刻队列若已满，按普通入队就永远丢了
    for uid in education_constant.ADULT_EXTRA_EVENT_UID_LIST:
        if not official_event_handle.judge_event_can_enqueue(uid, character_id):
            continue
        official_event_handle.push_official_event(uid, character_id, ignore_capacity=True)


def push_birthday_event() -> List[int]:
    """
    跨天结算时给今天过生日的女儿把生日事件插到队首（Plan 32 §3.3）
    Keyword arguments:
    无
    Return arguments:
    List[int] -- 推入了生日事件的角色id列表，按id升序
    功能: 生日按月、日比对，童年里只有第 365 天那一次（萝莉期）；只靠每日随机派发的话，当天先要过每晚 70% 的概率、
             再从几十条候选里按权重抽中，绝大多数女儿一辈子都见不到它。
          名单与日常派发相同（get_growth_event_character_list）；今天过生日（handle_self_birthday_today）、
             能入队（没经历过、不在队列里）、阶段与事件前提都成立的才推，与 get_candidate_event_list 同一套判定；
             只是事件前提逐条判、不带口上的口球判定（judge_premise_all_pass，实施复审补）：跨天那一刻她或博士被塞着口球，也不该错过一辈子仅此一次的生日。
          插队首、不受队列容量约束，与毕业典礼同一写法（push_graduation_event）：一辈子只有这一次，队列满了也不能丢。
          必须排在日常派发（official_event_handle.check_new_day_official_event）之前：推入之后它已在队列里，日常派发不会再抽到它
    """
    from Script.Design import handle_premise

    uid = education_constant.BIRTHDAY_EVENT_UID
    event_data = official_event_handle.get_event_data(uid)
    if event_data is None:
        return []
    result = []
    # 倒序插到队首：同一天过生日的几个女儿（双胞胎）最终按 id 升序排在队首
    for character_id in reversed(get_growth_event_character_list()):
        if not handle_premise.handle_self_birthday_today(character_id):
            continue
        if not official_event_handle.judge_event_can_enqueue(uid, character_id):
            continue
        if not judge_stage_pass(uid, character_id):
            continue
        partner_id = get_event_partner(uid, character_id)
        # 逐条判前提、不带口上的口球判定（judge_premise_all_pass）：跨天那一刻她或博士被塞着口球时，按口上的判法整组判 0，这一次就永远错过了
        if not judge_premise_all_pass(event_data.get("premise", ""), character_id, partner_id):
            continue
        if official_event_handle.push_official_event(uid, character_id, partner_id, to_front=True):
            result.append(character_id)
    return sorted(result)


def judge_premise_all_pass(premise_text: str, character_id: int, partner_id: int = 0) -> bool:
    """
    逐条判定一组事件前提是否全部成立，不带口上的口球判定（Plan 32 §3.3 / §3.11）
    Keyword arguments:
    premise_text -- & 连接的前提串
    character_id -- 主体角色id
    partner_id -- 互动对象角色id，默认0为玩家
    Return arguments:
    bool -- 全部成立（或前提为空）为 True；主体不存在为 False
    功能: official_event_handle.judge_premise_pass 走口上的权重计算（handle_premise.get_weight_from_premise_dict），
             主体或交互对象被塞着口球、前提里又没写口球时整组判 0。每日派发里这只是那天少派一条，
             一辈子只推一次的生日事件、孩子长大时重判阶段记号却会因此错过或误清。
          这里逐条调前提处理函数（handle_premise.handle_premise，CVP 走 handle_comprehensive_value_premise）；
             权重类前提（high_ 开头的与 CVP 的 Weight|0）只管权重、不算条件，跳过。
          判定期间照 judge_premise_pass 的写法把交互对象临时指向 partner_id（前提里的 A2 与 target_* 于是指向互动对象），判完立刻还原
    """
    from Script.Design import handle_premise

    premise_set = official_event_handle.get_premise_set(premise_text)
    if not premise_set:
        return True
    if character_id not in cache.character_data:
        return False
    character_data: game_type.Character = cache.character_data[character_id]
    old_target_id = character_data.target_character_id
    character_data.target_character_id = partner_id
    try:
        for premise in sorted(premise_set):
            if premise.startswith("high_") or "Weight|0" in premise:
                continue
            if not handle_premise.handle_premise(premise, character_id):
                return False
    finally:
        character_data.target_character_id = old_target_id
    return True


def judge_stage_marker_pass(uid: str, character_id: int) -> bool:
    """
    判定一条事件前提里的阶段素质记号对孩子当前的阶段是否仍成立（Plan 32 §3.11）
    Keyword arguments:
    uid -- 事件uid
    character_id -- 孩子角色id
    Return arguments:
    bool -- 前提里没有阶段素质记号、或记号全部成立时为 True；事件不存在时为 False
    功能: 期末桶的阶段区分与通用桶的「不派婴儿 / 不派萝莉」写在前提里（education_constant.STAGE_TALENT_PREMISE_SET），
             sub_key 上看不出来，judge_stage_pass 管不到；这里只取这些记号去判，别的前提一概不看。
          记号经 judge_premise_all_pass 逐条求值，不走 official_event_handle.judge_premise_pass：
             那条路带着口上的口球判定，长大那一刻她正被塞着口球时，会把成立的记号误判为不成立
    """
    event_data = official_event_handle.get_event_data(uid)
    if event_data is None:
        return False
    marker_set = official_event_handle.get_premise_set(event_data.get("premise", "")) & education_constant.STAGE_TALENT_PREMISE_SET
    return judge_premise_all_pass("&".join(sorted(marker_set)), character_id)


def drop_stale_stage_event(character_id: int) -> int:
    """
    孩子长大时把队列里已经对不上新阶段的养成事件清掉（Plan 32 §3.11）
    Keyword arguments:
    character_id -- 刚长大的孩子角色id（素质已换成新阶段）
    Return arguments:
    int -- 清掉的条数
    功能: 公务队列出队时不重判阶段，长大前入队、还没处理的上一阶段事件会顶着新阶段的抬头弹出
             （婴儿期入队的「忽然睁开了眼睛」写成「幼女期第 3 天」）。
          阶段桶（sub_key 0 与 101~103）：judge_stage_pass 已不成立的清掉——婴儿→幼女、幼女→萝莉清掉上一阶段桶的事件，
             成年时通用桶与萝莉桶一并清掉；前提里的阶段素质记号（judge_stage_marker_pass）已不成立的也清掉——
             幼女期入队、写婴儿的通用 6 / 15 / 27（前提写着不派萝莉）长成萝莉时清掉。
          期末桶（200）：sub_key 不分阶段，judge_stage_pass 对它恒不成立，只按阶段素质记号判——
             幼女期的期末 2 / 6 / 12 长成萝莉时、萝莉期的期末 3 / 7 / 10 / 17 / 18 / 19 成年时清掉，前提不写阶段的照留。
          成年桶（104：毕业典礼、成年纪念、通用 59 / 60）不动：只由成年结算显式推入。
          只重判阶段，别的前提（课型、好感、养成数值等）出队时照旧不复核。
          事件配置已删掉的队列项留给 official_event_handle.clean_official_event_queue 处理。
          由妊娠系统的三处阶段转换在换完素质后调用；成年结算要排在推毕业典礼之前
    """
    stage_bucket_set = {education_constant.STAGE_ANY, *education_constant.STAGE_ALL_CHILD}
    queue = official_event_handle.get_queue()
    keep_list = []
    drop_count = 0
    for one in queue:
        if isinstance(one, dict) and one.get("chara_id") == character_id:
            uid = one.get("uid")
            event_data = official_event_handle.get_event_data(uid)
            if event_data is not None and official_event_handle.get_event_department(uid) == education_constant.GROWTH_EVENT_DEPARTMENT:
                sub_key = event_data.get("sub_key", education_constant.STAGE_ANY)
                # 阶段桶：sub_key 与前提里的阶段素质记号都要对得上新阶段
                if sub_key in stage_bucket_set:
                    stale = not judge_stage_pass(uid, character_id) or not judge_stage_marker_pass(uid, character_id)
                # 期末桶：阶段只写在前提里，只按记号判
                elif sub_key == education_constant.SEMESTER_EVENT_SUB_KEY:
                    stale = not judge_stage_marker_pass(uid, character_id)
                # 成年桶：只由成年结算显式推入，不动
                else:
                    stale = False
                if stale:
                    drop_count += 1
                    continue
        keep_list.append(one)
    # 原地改写，队列本体的引用不变
    if drop_count:
        queue[:] = keep_list
    return drop_count


def push_semester_event(character_id: int) -> bool:
    """
    学期结算时给某个孩子推一条期末事件（Plan 22 一期 §3.13 第2条）

    事件是**按角色去重**的（official_event_handle.judge_event_done），
       同一个孩子不会重复遇到同一条期末事件。幼女到少女约十几个学期，
       所以池子迟早会被抽干——抽干时本函数只是返回 False，不报错也不重复派发
    Keyword arguments:
    character_id -- 孩子的角色id
    Return arguments:
    bool -- 是否成功入队
    """
    candidate = []
    for uid in game_config.config_official_event_by_sub_key.get(
            (education_constant.GROWTH_EVENT_DEPARTMENT, education_constant.SEMESTER_EVENT_SUB_KEY), ()):
        if not official_event_handle.judge_event_can_enqueue(uid, character_id):
            continue
        partner_id = get_event_partner(uid, character_id)
        now_weight = official_event_handle.judge_premise_pass(
            game_config.config_official_event[uid].get("premise", ""), character_id, partner_id)
        if not now_weight:
            continue
        candidate.append([uid, official_event_handle.get_event_weight(uid) * now_weight, partner_id])
    if not candidate:
        return False
    chosen = random.choices(candidate, weights=[one[1] for one in candidate], k=1)[0]
    return official_event_handle.push_official_event(chosen[0], character_id, chosen[2])


def push_semester_event_for_list(character_list: List[int]) -> int:
    """
    给一批刚出了成绩单的孩子各推一条期末事件（只推幼女 / 萝莉）
    Keyword arguments:
    character_list -- 孩子角色id列表
    Return arguments:
    int -- 实际入队的条数
    """
    push_count = 0
    for character_id in character_list:
        # 期末事件写的都是在上学的孩子（成绩单、教室、课表），只推给幼女 / 萝莉（Plan 26 §3.4）。
        #    成年女儿在学生岗时照出成绩单、整学期不在学生岗的不出（Plan 30 Q1），两种都不推事件
        if get_character_stage(character_id) not in (102, 103):
            continue
        if push_semester_event(character_id):
            push_count += 1
    return push_count


def get_growth_event_queue_count(character_id: int) -> int:
    """
    取某个孩子待处理的养成事件条数（养成总览的「待处理」栏用）
    Keyword arguments:
    character_id -- 孩子角色id
    Return arguments:
    int -- 待处理条数
    """
    return official_event_handle.get_official_event_queue_count(character_id)
