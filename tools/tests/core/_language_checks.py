# -*- coding: UTF-8 -*-
"""多语言回归检查的公共部分：由 test_language_*.py 在各自的语言下调用（本文件不以 test_ 开头，run_all 不会单独运行它）

游戏的翻译函数只在载入时翻译配置表的 name 列与标了 gettext 的列、角色模板的值、场景名；
行为标签、委托的类型 / 需求 / 奖励、工作的开放条件、烹饪问题的阶段、场景路径都保持中文原文。
代码里拿 `_("…")` 去比这些不翻译的值、或者拿中文原文去比已翻译的值，中文环境下恰好相等，换成英文 / 韩文就全部落空。
这里的每一节锁一处这样的修复；同一组检查在中文下也要成立，所以中文也跑一遍。
"""
import random

from _bootstrap import *  # noqa: F401,F403
from Script.Config import character_config
from Script.Core import old_chara_to_new
from Script.Design import handle_npc_ai_in_h, update
from Script.StateMachine import default as state_machine_default
from Script.System.Cooking_System import cooking
from Script.System.Dormitory_System import common as dormitory_common
from Script.System.Field_Commission_System import field_commission_function
from Script.System.Instruct_System import see_instruct_panel
from Script.System.Sex_System import group_sex_panel, hidden_sex_panel
from Script.UI.Panel import confinement_and_training, manage_basement_panel


def call(func, *args, **kwargs):
    """
    调用一个可能抛异常的函数，把异常变成返回值，好让断言给出失败原因而不是让整个测试进程崩掉
    Keyword arguments:
    func -- 要调用的函数
    args / kwargs -- 传给它的参数
    Return arguments:
    tuple -- (是否没有抛异常, 返回值或异常的 repr)
    """
    try:
        return True, func(*args, **kwargs)
    except Exception as error:  # noqa: BLE001
        return False, repr(error)[:160]


def find_behavior(need_tags: set, ban_tags: set = frozenset()) -> str:
    """
    在行为表里找一个带齐指定标签、且不带任何禁用标签的行为
    Keyword arguments:
    need_tags -- 必须都带的标签（中文原文）
    ban_tags -- 一个都不能带的标签
    Return arguments:
    str -- 行为id，找不到时为空串
    """
    for behavior_id, behavior_data in game_config.config_behavior.items():
        tag_set = set(behavior_data.tag.split("|"))
        if need_tags <= tag_set and not (ban_tags & tag_set) and behavior_id in game_config.config_behavior_effect_data:
            return behavior_id
    return ""


class Patched:
    """临时替换若干模块属性，离开 with 时还原（本文件里用来顶掉指令前提过滤、随机选择、时间推进与子面板）"""

    def __init__(self, *item_list):
        """
        Keyword arguments:
        item_list -- 若干 (对象, 属性名, 新值)
        """
        self.item_list = item_list
        self.saved_list = []

    def __enter__(self):
        for target, name, value in self.item_list:
            self.saved_list.append((target, name, getattr(target, name)))
            setattr(target, name, value)
        return self

    def __exit__(self, *_exc):
        for target, name, value in reversed(self.saved_list):
            setattr(target, name, value)
        return False


def pass_all_instruct_filter(instruct_id, now_premise_data, *_args, **_kwargs):
    """
    顶替 see_instruct_panel.judge_single_instruct_filter：所有指令都算可用
    这里要锁的是「按行为标签筛选」这一步，指令自身的前提由 test_premise_smoke 等覆盖
    Keyword arguments:
    instruct_id -- 指令id
    now_premise_data -- 已算过的前提
    Return arguments:
    tuple -- (True, 已算过的前提)
    """
    return True, now_premise_data


def check_translation(language: str) -> None:
    """
    确认本进程确实跑在指定语言下：翻译生效、哪些东西被翻译、哪些保持原文
    Keyword arguments:
    language -- 语言代码
    Return arguments:
    无
    """
    section("0. 语言环境")
    dorm_scene_name = cache.scene_data[scene_str(SCENE_DORM)].scene_name
    if language == "zh_CN":
        check("中文环境下翻译函数原样返回", _("性爱") == "性爱" and dorm_scene_name == "宿舍101房", (_("性爱"), dorm_scene_name))
    else:
        check("翻译链按指定语言载入", get_text.now_language == language and _("性爱") != "性爱", (get_text.now_language, _("性爱")))
        check("场景名随语言翻译，场景路径保持原文", dorm_scene_name != "宿舍101房" and scene_str(SCENE_DORM) in cache.scene_data, dorm_scene_name)
    tag_set = {tag for behavior_data in game_config.config_behavior.values() for tag in behavior_data.tag.split("|")}
    check("行为标签保持中文原文", {"性爱", "猥亵", "破处", "插入", "侍奉", "道具", "技艺", "工作", "娱乐"} <= tag_set)
    check("群交部位表以中文原文为键", set(game_config.config_behavior_id_list_of_group_sex_body_part) == {"插入", "侍奉", "口", "手", "肛", "道具"},
          sorted(game_config.config_behavior_id_list_of_group_sex_body_part))


def check_behavior_tag() -> None:
    """
    行为标签的比较：NPC 逆推的候选、无意识下技艺指令的口上放行、设施损坏检测、隐奸经验与隐蔽值
    Keyword arguments:
    无
    Return arguments:
    无
    """
    section("1. 行为标签的比较")
    npc = make_character(701, "标签对象")
    pl.target_character_id = 701
    npc.target_character_id = 0

    # 1.1 NPC 逆推：候选是「性爱类，且不是道具 / 药物 / SM / 非逆推类」的行为；对方还是处时不选破处类
    npc.h_state.npc_active_h = True
    candidate_log = []

    def record_choice(candidate_list):
        """记下候选并固定选第一个"""
        candidate_log.append(list(candidate_list))
        return candidate_list[0]

    def run_active_h(part_id: int, virgin_talent: int) -> list:
        """
        在指定部位喜好与处女素质下跑一次逆推，返回候选行为列表
        Keyword arguments:
        part_id -- 部位喜好
        virgin_talent -- 处女类素质id（-1 表示都不是处）
        Return arguments:
        list -- 候选行为id列表（一个都没有时为空）
        """
        candidate_log.clear()
        for talent_id in range(5):
            npc.talent[talent_id] = 1 if talent_id == virgin_talent else 0
        with Patched((see_instruct_panel, "judge_single_instruct_filter", pass_all_instruct_filter), (update, "game_update_flow", lambda *_a, **_k: None),
                     (handle_npc_ai_in_h, "evaluate_npc_body_part_prefs", lambda _cid: part_id), (random, "choice", record_choice)):
            handle_npc_ai_in_h.npc_active_h()
        return candidate_log[0] if candidate_log else []

    candidate_list = run_active_h(4, -1)
    tag_of = {behavior_id: set(game_config.config_behavior[behavior_id].tag.split("|")) for behavior_id in game_config.config_behavior}
    bad_list = [behavior_id for behavior_id in candidate_list if "性爱" not in tag_of[behavior_id] or tag_of[behavior_id] & {"道具", "药物", "SM", "非逆推"}]
    check("NPC 逆推能选出行为，候选都是性爱类且不含道具 / 药物 / SM / 非逆推类", len(candidate_list) > 0 and not bad_list, (len(candidate_list), bad_list[:5]))
    check("不是处时，逆推候选里有破处类行为（下一条才有意义）", any("破处" in tag_of[behavior_id] for behavior_id in candidate_list))
    virgin_candidate_list = run_active_h(4, 0)
    check("对方是处女且喜好部位为 V 时，逆推不选破处类行为", len(virgin_candidate_list) > 0 and not [b for b in virgin_candidate_list if "破处" in tag_of[b]],
          [b for b in virgin_candidate_list if "破处" in tag_of[b]][:5])
    npc.h_state.npc_active_h = False
    for talent_id in range(5):
        npc.talent[talent_id] = 0

    # 1.2 交互对象无意识时，口上要么带无意识前提、要么当前行为带「技艺」标签才放行
    arts_behavior = find_behavior({"技艺"})
    daily_behavior = find_behavior({"日常"}, {"技艺"})
    npc.sp_flag.unconscious_h = 1
    pl.behavior.behavior_id = arts_behavior
    arts_weight = handle_premise.get_weight_from_premise_dict({"high_1"}, 0, {})[0]
    pl.behavior.behavior_id = daily_behavior
    daily_weight = handle_premise.get_weight_from_premise_dict({"high_1"}, 0, {})[0]
    npc.sp_flag.unconscious_h = 0
    check("对象无意识时，技艺类行为的口上放行、普通行为的口上不放行", arts_weight > 0 and daily_weight == 0, (arts_behavior, arts_weight, daily_behavior, daily_weight))

    # 1.3 工作类、娱乐类行为结算后做一次设施损坏检测（结算 1751），其他行为不做
    damage_call = []
    behavior_by_label = (("工作", find_behavior({"工作"})), ("娱乐", find_behavior({"娱乐"})), ("其他", find_behavior({"日常"}, {"工作", "娱乐"})))
    saved_effect = constant.settle_behavior_effect_data[1751]
    constant.settle_behavior_effect_data[1751] = lambda *args: damage_call.append(args[0])
    saved_effect_data = dict(game_config.config_behavior_effect_data)
    game_config.config_behavior_effect_data.clear()  # 只看损坏检测这一步，不跑各行为自己的结算
    pl.target_character_id = 0
    result = {}
    for label, behavior_id in behavior_by_label:
        damage_call.clear()
        game_config.config_behavior_effect_data[behavior_id] = []
        pl.event.skip_instruct_talk = True  # 不结算口上
        ok, _value = call(settle_behavior.handle_instruct_data, 0, behavior_id, cache.game_time, 10, game_type.CharacterStatusChange())
        result[label] = (ok, len(damage_call))
    pl.event.skip_instruct_talk = False
    game_config.config_behavior_effect_data.clear()
    game_config.config_behavior_effect_data.update(saved_effect_data)
    constant.settle_behavior_effect_data[1751] = saved_effect
    check("工作类与娱乐类行为结算后各做一次设施损坏检测，其他行为不做", result == {"工作": (True, 1), "娱乐": (True, 1), "其他": (True, 0)}, result)

    # 1.4 隐奸中做猥亵 / 性爱类指令：隐奸经验 +1，隐蔽值上涨，带插入 / 侍奉 / 道具标签的涨得更多
    pl.target_character_id = 701
    pl.sp_flag.hidden_sex_mode = 2
    grope_behavior = find_behavior({"猥亵"}, {"道具", "插入", "侍奉"})
    insert_behavior = find_behavior({"性爱", "插入"}, {"道具"})
    pl.behavior.behavior_id = grope_behavior
    pl.behavior.duration = 10
    exp_before = pl.experience.get(35, 0)
    ok, value = call(settle_behavior.extra_exp_settle, 0, game_type.CharacterStatusChange())
    check("隐奸中做猥亵类指令，隐奸经验 +1", ok and pl.experience.get(35, 0) == exp_before + 1, (value, exp_before, pl.experience.get(35, 0)))
    pl.h_state.hidden_sex_discovery_dregree = 0
    hidden_sex_panel.settle_hidden_value_by_action(0)
    grope_add = pl.h_state.hidden_sex_discovery_dregree
    pl.h_state.hidden_sex_discovery_dregree = 0
    pl.behavior.behavior_id = insert_behavior
    hidden_sex_panel.settle_hidden_value_by_action(0)
    insert_add = pl.h_state.hidden_sex_discovery_dregree
    check("隐奸中做猥亵类指令隐蔽值上涨，插入类指令的涨幅是它的 3 倍", grope_add > 0 and insert_add == grope_add * 3, (grope_behavior, grope_add, insert_behavior, insert_add))
    pl.sp_flag.hidden_sex_mode = 0
    pl.h_state.hidden_sex_discovery_dregree = 0
    pl.behavior.behavior_id = constant.Behavior.SHARE_BLANKLY
    remove_character(701)


def check_group_sex() -> None:
    """
    群交模板：按行为所属部位写入模板、按部位取可用行为、「侍奉」这个部位记号在产出与各处比较之间保持一致；调教助手的可用行为
    Keyword arguments:
    无
    Return arguments:
    无
    """
    section("2. 群交模板与调教助手")
    part_table = game_config.config_behavior_id_list_of_group_sex_body_part
    first = make_character(711, "群交甲")
    second = make_character(712, "群交乙")
    for character_data in (pl, first, second):
        character_data.h_state = attr_calculation.get_h_state_reset(character_data.h_state)
    pl.target_character_id = 711
    saved_mode = cache.group_sex_mode
    cache.group_sex_mode = True
    template = pl.h_state.group_sex_body_template_dict["A"]

    # 2.1 玩家在群交模式下执行指令：按行为所属的部位写进模板
    result = {}
    for part_name, slot in (("口", "mouth"), ("手", "L_hand"), ("肛", "anal"), ("插入", "penis")):
        behavior_id = part_table[part_name][0]
        ok, value = call(group_sex_panel.group_sex_settle, 0, 711, behavior_id)
        result[part_name] = value if not ok else template[0][slot] == [711, behavior_id]
    serve_behavior = part_table["侍奉"][0]
    ok, value = call(group_sex_panel.group_sex_settle, 0, 711, serve_behavior)
    result["侍奉"] = value if not ok else (template[1] == [[711], serve_behavior] and template[0]["penis"] == [-1, -1])
    check("群交模式下执行口 / 手 / 肛 / 插入 / 侍奉类指令，各自写进模板对应的部位", all(value is True for value in result.values()), result)

    # 2.2 按部位取可用行为
    with Patched((see_instruct_panel, "judge_single_instruct_filter", pass_all_instruct_filter)):
        result = {slot: call(group_sex_panel.get_status_id_list_from_group_sex_body_part, slot) for slot in ("mouth", "L_hand", "penis", "anal")}
    expect = {"mouth": "口", "L_hand": "手", "penis": "插入", "anal": "肛"}
    bad = {slot: value for slot, (ok, value) in result.items() if not ok or not value or not set(value) <= set(part_table[expect[slot]])}
    check("按嘴 / 手 / 阴茎 / 肛门取可用行为，取到的都属于对应部位", not bad, {slot: str(value)[:80] for slot, value in bad.items()})

    # 2.3 「侍奉」记号：空缺部位列表产出的记号，交给取行为、设指令、设对象三处都要走侍奉分支
    pl.h_state = attr_calculation.get_h_state_reset(pl.h_state)
    template = pl.h_state.group_sex_body_template_dict["A"]
    empty_list, _not_empty_list = group_sex_panel.get_now_template_part_list()
    marker_list = [part for part in empty_list if part not in template[0]]
    check("模板全空时，空缺部位里有且只有一个不属于单人部位的记号（侍奉）", len(marker_list) == 1, empty_list)
    marker = marker_list[0] if marker_list else "侍奉"
    with Patched((see_instruct_panel, "judge_single_instruct_filter", pass_all_instruct_filter)):
        ok, value = call(group_sex_panel.get_status_id_list_from_group_sex_body_part, marker)
    check("用侍奉记号取可用行为，取到的是侍奉类行为", ok and len(value) > 0 and set(value) <= set(part_table["侍奉"]), str(value)[:120])
    panel = group_sex_panel.Edit_Group_Sex_Temple_Panel(120)
    ok_status, value_status = call(panel.set_status, "A", marker, serve_behavior)
    ok_target, value_target = call(panel.set_target_chara, "A", marker, 711)
    check("编辑面板用侍奉记号设指令、设对象，都写进模板的侍奉栏而不是单人部位", ok_status and ok_target and template[1] == [[711], serve_behavior] and set(template[0]) == {"mouth", "L_hand", "R_hand", "penis", "anal"},
          (value_status, value_target, template[1], sorted(template[0])))

    # 2.4 NPC 在群交里补位：抽到侍奉记号时进侍奉栏
    pl.h_state = attr_calculation.get_h_state_reset(pl.h_state)
    template = pl.h_state.group_sex_body_template_dict["A"]
    second.sp_flag.is_h = True

    def prefer_marker(candidate_list):
        """随机选择的替身：候选里有侍奉记号就选它，否则选第一个"""
        return marker if marker in candidate_list else candidate_list[0]

    with Patched((see_instruct_panel, "judge_single_instruct_filter", pass_all_instruct_filter), (random, "choice", prefer_marker)):
        ok, value = call(handle_npc_ai_in_h.npc_ai_in_group_sex, 712)
    check("NPC 补位抽到侍奉时进模板的侍奉栏，不往单人部位里多写一栏", ok and template[1][0] == [712] and template[1][1] in part_table["侍奉"] and set(template[0]) == {"mouth", "L_hand", "R_hand", "penis", "anal"},
          (value, template[1], sorted(template[0])))

    # 2.5 调教助手的可用行为：口 / 手 / 道具三类
    pl.h_state = attr_calculation.get_h_state_reset(pl.h_state)
    with Patched((see_instruct_panel, "judge_single_instruct_filter", pass_all_instruct_filter)):
        ok, value = call(confinement_and_training.get_all_can_use_behavior_id_for_sex_assistant)
    allow_set = set(part_table["口"]) | set(part_table["手"]) | set(part_table["道具"])
    check("调教助手能列出可用行为，且都属于口 / 手 / 道具三类", ok and len(value) > 0 and set(value) <= allow_set, str(value)[:120])

    cache.group_sex_mode = saved_mode
    pl.target_character_id = 0
    remove_character(711)
    remove_character(712)


def check_field_commission() -> None:
    """
    外勤委托的需求 / 奖励文本：声望、特产、好感、信赖的奖励确实发放，「招募」类需求能判断
    Keyword arguments:
    无
    Return arguments:
    无
    """
    section("3. 外勤委托的需求与奖励")
    npc = make_character(721, "委托对象")  # 委托文本里写的是干员编号，现在角色id与干员编号相同
    npc.adv = 721
    npc.favorability = {0: 100}
    npc.trust = 10

    def reward(now_text: str):
        """按「发放奖励」处理一段委托文本"""
        return call(field_commission_function.process_commission_text, now_text, True, True, [721], "", "", True)

    nation_id = sorted(game_config.config_nation)[1]
    cache.country.nation_reputation[nation_id] = 0
    ok, value = reward("声望_%d_300" % nation_id)
    check("奖励「声望」按百分之一计入该势力的声望", ok and abs(cache.country.nation_reputation[nation_id] - 3) < 1e-6, (value, cache.country.nation_reputation[nation_id]))

    specialty_nation = sorted(game_config.config_resouce_data_of_nation)[0]
    specialty_id = game_config.config_resouce_data_of_nation[specialty_nation][0]
    saved_location = list(cache.rhodes_island.current_location)
    cache.rhodes_island.current_location = [specialty_nation, 0]
    cache.rhodes_island.materials_resouce[specialty_id] = 5
    ok, value = reward("特产_0_7")
    check("奖励「特产」发放的是当前所在地的特产", ok and cache.rhodes_island.materials_resouce[specialty_id] == 12, (value, cache.rhodes_island.materials_resouce[specialty_id]))
    cache.rhodes_island.current_location = saved_location

    ok, value = reward("好感_721_50")
    check("奖励「好感」加到指定干员对博士的好感上", ok and npc.favorability[0] == 150, (value, npc.favorability[0]))
    ok, value = reward("信赖_721_5")
    check("奖励「信赖」加到指定干员的信赖上", ok and npc.trust == 15, (value, npc.trust))

    ok, value = call(field_commission_function.process_commission_text, "招募_721_1", False, False, [], "", "", True)
    check("需求「已招募某干员」能判断：该干员在编时满足", ok and value[2] is True, value)
    cache.npc_id_got.discard(721)
    ok, value = call(field_commission_function.process_commission_text, "招募_721_1", False, False, [], "", "", True)
    check("需求「已招募某干员」能判断：该干员不在编时不满足", ok and value[2] is False, value)
    remove_character(721)

    # 委托类型（type）是翻译列：面板上随语言显示，代码里按翻译后的类型名比较。
    #    这个标志一旦被改回「不翻译」，「角色类委托要先招募到该干员才列出」的筛选在「角色」有译文的语言下就会失效
    with open(os.path.join(ROOT, "data", "csv", "Commission.csv"), encoding="utf-8-sig") as csv_file:
        head_list = [csv_file.readline().rstrip("\r\n") for _index in range(5)]
    type_index = head_list[0].split(",").index("type")
    check("委托表里「委托类型」一列标了翻译", head_list[3].split(",")[type_index] == "1", head_list[3])
    with open(os.path.join(ROOT, "tools", "ArkEditor", "load_csv.py"), encoding="utf-8") as editor_file:
        editor_text = editor_file.read()
    check("编辑器保存委托表时写回的「数据类型 / 是否翻译 / 表名」三行与游戏表一致（否则用编辑器存一次委托就会把翻译标志改回去）",
          "\\n" + "\\n".join(head_list[2:5]) in editor_text, head_list[2:5])
    chara_commission_list = [data for data in game_config.config_commission.values() if "c_" in data.demand and data.type == _("角色")]
    check("载入后有类型为（翻译后的）「角色」、且要求指定干员出场的委托", len(chara_commission_list) > 0, sorted({data.type for data in game_config.config_commission.values()}))
    candidate_list = [data for data in chara_commission_list if data.country_id == -1 and data.related_id == -1 and data.level <= 2]
    if candidate_list:
        from Script.System.Field_Commission_System import field_commission_panel

        class FakeRow:
            """委托列表里一行的替身：只看哪些委托被列出来，不画具体内容"""

            def __init__(self, *_args, **_kwargs):
                self.draw_text = ""
                self.button_return = ""

            def draw(self):
                pass

        target = candidate_list[0]
        chara_adv = int(target.demand.split("_")[1])
        saved_state = (cache.now_panel_id, cache.rhodes_island.facility_level.get(14, 1), set(cache.rhodes_island.finished_field_commissions_set), set(cache.rhodes_island.shut_down_field_commissions_set))
        saved_location = list(cache.rhodes_island.current_location)
        cache.rhodes_island.current_location = [specialty_nation, 0]  # 面板要读罗德岛当前所在地；目标委托是通用委托，在哪里都能接
        cache.rhodes_island.facility_level[14] = 5
        cache.rhodes_island.finished_field_commissions_set.discard(target.cid)
        cache.rhodes_island.shut_down_field_commissions_set.discard(target.cid)
        commission_panel = field_commission_panel.Field_Commission_Panel(120)
        commission_panel.now_panel = _("特殊外勤") if target.special != 0 else _("常规外勤")

        def is_listed():
            """画一遍委托面板后立刻返回，看目标委托有没有被列出来"""
            with Patched((field_commission_panel, "CommissionDraw", FakeRow), (flow_handle, "askfor_all", lambda _return_list, *_a, **_k: _("返回"))):
                ok, value = call(commission_panel.draw)
            return ok, value, target.cid in commission_panel.handle_panel.text_list

        without_chara = is_listed()
        wanted = make_character(chara_adv, "委托要的干员")
        wanted.adv = chara_adv
        with_chara = is_listed()
        check("角色类委托：没招募到要出场的干员时不列出，招募到之后列出", without_chara == (True, None, False) and with_chara == (True, None, True), (target.cid, target.type, without_chara, with_chara))
        remove_character(chara_adv)
        cache.rhodes_island.current_location = saved_location
        cache.now_panel_id = saved_state[0]
        cache.rhodes_island.facility_level[14] = saved_state[1]
        cache.rhodes_island.finished_field_commissions_set.clear()
        cache.rhodes_island.finished_field_commissions_set.update(saved_state[2])
        cache.rhodes_island.shut_down_field_commissions_set.clear()
        cache.rhodes_island.shut_down_field_commissions_set.update(saved_state[3])
    else:
        check("有可用来检查面板筛选的通用角色类委托", False, len(chara_commission_list))


def check_cook_question() -> None:
    """
    烹饪问题库的阶段名：代码里的四个阶段与特殊调味的替换阶段，都要能在问题库里查到
    Keyword arguments:
    无
    Return arguments:
    无
    """
    section("4. 烹饪问题库的阶段")
    stage_set = {stage for stage_data in game_config.config_cook_question.values() for stage in stage_data}
    check("四个烹饪阶段都能在问题库里查到", len(cooking.COOK_QUESTION_STAGES) == 4 and set(cooking.COOK_QUESTION_STAGES) <= stage_set, (cooking.COOK_QUESTION_STAGES, sorted(stage_set)))
    override_list = [cooking.get_special_seasoning_question_stage(seasoning) for seasoning in (11, 12, 101)]
    bad = [item for item in override_list if item is None or item[0] not in cooking.COOK_QUESTION_STAGES or item[1] not in stage_set]
    check("特殊调味替换的阶段与替换成的阶段都能查到", not bad, override_list)


def check_place() -> None:
    """
    地点：同居助理在中枢时去博士房间的卫生间；开放宿舍、宿舍层号、新干员 / 访客 / 模板写了宿舍的干员的宿舍分配
    Keyword arguments:
    无
    Return arguments:
    无
    """
    section("5. 地点与宿舍")
    # 5.1 同居中的助理在控制中枢想上厕所，优先去博士房间
    assistant = make_character(731, "同居助理", position=["中枢", "博士办公室"])
    assistant.assistant_services[7] = 1
    saved_assistant = pl.assistant_character_id
    pl.assistant_character_id = 731
    ok, value = call(state_machine_default.character_move_to_toilet, 731)
    dr_room_list = [map_handle.get_map_system_path_for_str(path) for path in constant.place_data["Dr_room"]]
    check("同居助理在中枢时，上厕所的目的地是博士房间", ok and assistant.behavior.move_final_target in dr_room_list, (value, assistant.behavior.move_final_target))
    pl.assistant_character_id = saved_assistant
    remove_character(731)

    # 5.2 开放宿舍：宿舍区 1 级时一层的基础房间开放；设施开放表里打开的房间也算
    saved_facility_open = dict(cache.rhodes_island.facility_open)
    cache.rhodes_island.facility_open.clear()
    ok, room_dict = call(dormitory_common.get_open_dormitory_rooms_by_layer)
    base_upper = dormitory_common._get_base_open_room_upper_no()
    base_path_list = [scene_str(["宿舍", "1区", str(room_no)]) for room_no in range(101, base_upper + 1)]
    check("宿舍区 1 级时，开放的正好是一层的基础房间，按房号排列", ok and isinstance(room_dict, dict) and [path for _name, path in room_dict.get(1, [])] == base_path_list and set(room_dict) == {1},
          str(room_dict)[:200])
    extra_cid = [cid for cid, data in game_config.config_facility_open.items() if data.name == cache.scene_data[scene_str(["宿舍", "1区", str(base_upper + 1)])].scene_name]
    check("设施开放表里有基础房间之后的那间宿舍", len(extra_cid) == 1, extra_cid)
    if extra_cid:
        cache.rhodes_island.facility_open[extra_cid[0]] = True
        ok, room_dict = call(dormitory_common.get_open_dormitory_rooms_by_layer)
        check("在设施开放表里打开一间宿舍后，它排在同层基础房间之后", ok and [path for _name, path in room_dict.get(1, [])] == base_path_list + [scene_str(["宿舍", "1区", str(base_upper + 1)])],
              str(room_dict)[:200])
    check("宿舍路径的层号取自房号的百位，非宿舍路径为 0",
          [dormitory_common.get_layer_by_dormitory_path(scene_str(path)) for path in (["宿舍", "1区", "101"], ["宿舍", "5区", "501"], ["中枢", "博士办公室"])] + [dormitory_common.get_layer_by_dormitory_path("")]
          == [1, 5, 0, 0])

    # 5.3 新干员分到开放宿舍
    newcomer = make_character(732, "新干员")
    newcomer.dormitory = "无"
    ok, value = call(dormitory_common.new_character_get_dormitory, 732)
    check("新干员被分到一间开放的宿舍", ok and newcomer.dormitory in base_path_list + [scene_str(["宿舍", "1区", str(base_upper + 1)])], (value, newcomer.dormitory))

    # 5.4 访客分到已开放的客房
    guest_path = scene_str(["访客", "客房1"])
    guest_cid = [cid for cid, data in game_config.config_facility_open.items() if data.name == cache.scene_data[guest_path].scene_name]
    visitor = make_character(733, "访客")
    visitor.dormitory = "无"
    cache.rhodes_island.visitor_info[733] = cache.game_time
    if guest_cid:
        cache.rhodes_island.facility_open[guest_cid[0]] = True
    ok, value = call(dormitory_common.new_character_get_dormitory, 733)
    check("访客被分到已开放的客房", len(guest_cid) == 1 and ok and visitor.dormitory == guest_path, (guest_cid, value, visitor.dormitory))
    del cache.rhodes_island.visitor_info[733]
    remove_character(733)
    remove_character(732)

    # 5.5 开新游戏分配宿舍：模板里写了宿舍名（中文）的干员住进对应的房间，其余两人一间
    saved_got = set(cache.npc_id_got)
    cache.npc_id_got.clear()
    special_name = "梅尔宿舍"
    special_path_list = [path for path in constant.place_data.get("Special_Dormitory", []) if cache.scene_data[path].scene_name == _(special_name)]
    owner = make_character(734, "有专属宿舍的干员")
    owner.dormitory = special_name
    normal = make_character(735, "普通干员")
    normal.dormitory = "无"
    ok, value = call(dormitory_common.init_character_dormitory)
    check("模板宿舍写着专属宿舍名的干员住进那间专属宿舍，普通干员住进普通宿舍",
          len(special_path_list) == 1 and ok and owner.dormitory == special_path_list[0] and normal.dormitory in constant.place_data["Dormitory"], (special_path_list, value, owner.dormitory, normal.dormitory))
    remove_character(734)
    remove_character(735)
    cache.npc_id_got.clear()
    cache.npc_id_got.update(saved_got)
    cache.rhodes_island.facility_open.clear()
    cache.rhodes_island.facility_open.update(saved_facility_open)


def check_identify_by_adv() -> None:
    """
    按干员编号认人：初始干员的工作安排、初始干员名单、阿玛雅的旧存档编号修正不碰同译名的别人
    Keyword arguments:
    无
    Return arguments:
    无
    """
    section("6. 按干员编号认人")
    # 6.1 开新游戏时的初始工作：可露希尔 21、凯尔希与华法琳 61、特蕾西娅 71、杜宾 91
    saved_got = set(cache.npc_id_got)
    cache.npc_id_got.clear()
    expect = {7: 21, 3: 61, 171: 61, 56: 71, 130: 91, 1: 0}
    for index, adv in enumerate(expect):
        character_data = make_character(740 + index, character_config.character_tem_list[adv].Name)
        character_data.adv = adv
    ok, value = call(character_handle.first_NPC_work)
    actual = {cache.character_data[740 + index].adv: cache.character_data[740 + index].work.work_type for index in range(len(expect))}
    check("开新游戏时五名初始干员各有初始工作，阿米娅没有", ok and actual == expect, (value, actual))
    for index in range(len(expect)):
        remove_character(740 + index)
    cache.npc_id_got.clear()
    cache.npc_id_got.update(saved_got)

    # 6.2 初始干员名单：按模板建角色时，只有六名初始干员直接入编
    saved_got = set(cache.npc_id_got)
    saved_name_data = set(cache.npc_name_data)
    cache.npc_id_got.clear()
    joined = {}
    other_adv = [adv for adv in sorted(character_config.character_tem_list) if adv not in {1, 3, 7, 56, 171, 130, 448, 450}][0]
    for adv in (1, 3, 7, 56, 171, 130, 448, 450, other_adv):
        ok, value = call(character_handle.init_character, 9000 + adv, character_config.character_tem_list[adv])
        joined[adv] = (9000 + adv) in cache.npc_id_got if ok else value
        cache.character_data.pop(9000 + adv, None)
    check("按模板建角色时，六名初始干员直接入编，阿玛雅等其他干员不入编",
          joined == {1: True, 3: True, 7: True, 56: True, 171: True, 130: True, 448: False, 450: False, other_adv: False}, joined)
    cache.npc_id_got.clear()
    cache.npc_id_got.update(saved_got)
    cache.npc_name_data.clear()
    cache.npc_name_data.update(saved_name_data)

    # 6.3 阿玛雅的编号修正（她曾与死芒同为 450 号）：只搬 450 号里名叫阿玛雅的角色，不碰编号正确的其他人
    def tem_character(cid: int, adv: int, name: str) -> game_type.Character:
        """造一个只带编号与名字的存档角色"""
        character_data = game_type.Character()
        character_data.cid = cid
        character_data.adv = adv
        character_data.name = name
        return character_data

    amiya_name = character_config.character_tem_list[1].Name
    amaiya_name = character_config.character_tem_list[448].Name
    loaded_dict = {"character_data": {0: tem_character(0, 0, "博士"), 1: tem_character(1, 1, amiya_name), 448: tem_character(448, 448, amaiya_name), 450: tem_character(450, 450, character_config.character_tem_list[450].Name)},
                   "npc_tem_data": dict(cache.npc_tem_data)}
    loaded_dict["character_data"][1].favorability = {0: 4321}
    ok, value = call(old_chara_to_new.fix_wrong_character, loaded_dict)
    data = loaded_dict["character_data"]
    check("编号都正确的存档里，阿米娅、阿玛雅、死芒都不被改动",
          ok and value == 0 and data[1].name == amiya_name and data[1].favorability == {0: 4321} and (data[448].adv, data[448].name) == (448, amaiya_name) and data[450].adv == 450,
          (value, data[1].name, data[1].favorability, data[448].adv, data[448].name))
    loaded_dict = {"character_data": {0: tem_character(0, 0, "博士"), 1: tem_character(1, 1, amiya_name), 448: tem_character(448, 448, "占位"), 450: tem_character(450, 450, amaiya_name)},
                   "npc_tem_data": dict(cache.npc_tem_data)}
    loaded_dict["character_data"][450].favorability = {0: 1234}
    with Patched((character_handle, "init_character", lambda cid, tem: tem_character(cid, tem.AdvNpc, tem.Name))):
        ok, value = call(old_chara_to_new.fix_wrong_character, loaded_dict)
    data = loaded_dict["character_data"]
    check("旧存档里 450 号的阿玛雅仍被搬到 448 号，450 号换回模板里的角色",
          ok and value >= 1 and (data[448].adv, data[448].cid, data[448].name, data[448].favorability) == (448, 448, amaiya_name, {0: 1234}) and data[450].name == character_config.character_tem_list[450].Name
          and data[1].name == amiya_name, (value, data[448].adv, data[448].cid, data[448].name, data[450].name))


def check_manage_basement_panel() -> None:
    """
    管理罗德岛面板：点每个子系统按钮都进入对应的面板（或给出提示），不报错
    Keyword arguments:
    无
    Return arguments:
    无
    """
    section("7. 管理罗德岛面板的子系统按钮")
    from Script.System.Dormitory_System import manage_dormitory_panel
    from Script.System.Education_System import class_schedule_panel
    from Script.System.Field_Commission_System import field_commission_panel
    from Script.System.Medical_System import medical_department_panel
    from Script.System.Pregnancy_System import pregnancy_panel
    from Script.UI.Panel import (agriculture_production_panel, building_panel, equipmen_panel, invite_visitor_panel, manage_assembly_line_panel, manage_library, manage_power_system_panel,
                                 manage_vehicle_panel, nation_diplomacy_panel, recruit_panel, resource_exchange_panel)

    opened = []

    def fake_panel(label: str):
        """造一个只记录「被打开」的面板替身"""

        class FakePanel:
            def __init__(self, *_args, **_kwargs):
                pass

            def draw(self):
                opened.append(label)

        return FakePanel

    # 按钮文字（与面板里 department_son_panel_button_dict 的写法一致）→ 应进入的面板所在的 (模块, 类名)；None 表示只给一句提示
    button_target = {
        "[能源系统]": (manage_power_system_panel, "Manage_Power_System_Panel"), "[基建系统]": (building_panel, "Building_Panel"), "[装备维护系统]": (equipmen_panel, "Equipment_Maintain_Panel"),
        "[宿舍管理系统]": (manage_dormitory_panel, "Manage_Dormitory_Panel"), "[烹饪系统]": None, "[生产系统]": (manage_assembly_line_panel, "Manage_Assembly_Line_Panel"),
        "[图书馆管理系统]": (manage_library, "Manage_Library_Panel"), "[资源交易系统]": (resource_exchange_panel, "Resource_Exchange_Line_Panel"), "[招募系统]": (recruit_panel, "Recruit_Panel"),
        "[妊娠总览系统]": (pregnancy_panel, "Pregnancy_Overview_Panel"), "[教育管理系统]": (class_schedule_panel, "Education_Manage_Panel"), "[医疗经营系统]": (medical_department_panel, "Medical_Department_Panel"),
        "[诊疗病人系统]": None, "[势力外交系统]": (nation_diplomacy_panel, "Nation_Diplomacy_Panel"), "[邀请访客系统]": (invite_visitor_panel, "Invite_Visitor_Panel"),
        "[外勤委托系统]": (field_commission_panel, "Field_Commission_Panel"), "[载具管理系统]": (manage_vehicle_panel, "Manage_Vehicle_Panel"), "[农业系统]": (agriculture_production_panel, "Agriculture_Production_Panel"),
        "[监禁调教系统]": (confinement_and_training, "Confinement_And_Training_Manage_Panel"),
    }
    patch_list = [(target[0], target[1], fake_panel(text)) for text, target in button_target.items() if target is not None]
    # 铁匠铺开放、已任命监狱长：让装备维护与监禁调教两个按钮走到「进入面板」的分支
    patch_list += [(handle_premise, "handle_blacksmith_shop_open", lambda _cid: 1), (handle_premise, "handle_have_warden", lambda _cid: 1)]
    panel = manage_basement_panel.Manage_Basement_Panel(120)
    wrong = {}
    with Patched(*patch_list):
        for text, target in button_target.items():
            opened.clear()
            drawn_text.clear()
            ok, value = call(panel.jump_to_son_panel, _(text))
            expect = [text] if target is not None else []
            if not ok or opened != expect or (target is None and not drawn_text):
                wrong[text] = (value, list(opened))
    check("十九个子系统按钮各自进入对应的面板（烹饪、诊疗病人两项只给提示），都不报错", not wrong, wrong)


def check_cloth_tag() -> None:
    """
    角色专属服装的分类：按模板里服装名的中文原文判断「必带」与下衣的裤 / 裙，不受服装名译文影响
    Keyword arguments:
    无
    Return arguments:
    无
    """
    section("8. 角色专属服装的分类")
    wrong = []
    count = {0: 0, 4: 0, 5: 0, 6: 0}
    for tem_data in character_config.character_config_data.values():
        cloth_count = 0
        for key, raw_name in tem_data.items():
            if not key.startswith("C|"):
                continue
            cloth_type = int(key[2:].split("-")[0])
            if cloth_type in (5999, 8999):
                continue
            now_cid = 10000 + tem_data["AdvNpc"] * 50 + cloth_count
            cloth_count += 1
            # 设计：名字带「必带」的是必带服装（6）；下衣（类型 8）里名字带「裤」的是裤子（4）、其余是裙子（5）；别的都是 0
            expect_tag = 6 if "必带" in raw_name else 0
            if cloth_type == 8:
                expect_tag = 4 if "裤" in raw_name else 5
            count[expect_tag] += 1
            actual = game_config.config_clothing_tem[now_cid]
            if actual.tag != expect_tag or "必带" in actual.name:
                wrong.append((now_cid, raw_name, expect_tag, actual.tag, actual.name))
    check("模板里有裤子、裙子与必带服装（下一条才有意义）", count[4] > 0 and count[5] > 0 and count[6] > 0, count)
    check("每件角色专属服装的分类都与它的中文名相符，「必带」二字不留在显示名里", not wrong, (len(wrong), wrong[:4]))


def run_language_checks(language: str) -> None:
    """
    在当前进程的语言下跑完全部检查
    Keyword arguments:
    language -- 本进程启动时指定的语言代码
    Return arguments:
    无
    """
    cache.debug_mode = False  # 维护者本地的 config.ini 可能开着 debug，会改变若干面板与前提的走向
    check_translation(language)
    check_behavior_tag()
    check_group_sex()
    check_field_commission()
    check_cook_question()
    check_place()
    check_identify_by_adv()
    check_manage_basement_panel()
    check_cloth_tag()
