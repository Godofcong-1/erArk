# -*- coding: UTF-8 -*-
"""零散的锁定修复：通用占位符嵌套替换、体检 AI（跟随中不去体检、体检科满员放弃当天体检）、失去泌乳后罩杯缩回、照料婴儿的干员不算离线、三处事件数据、隐奸高潮口上的人名、脱鞋袜进大浴场衣柜的精液表、生产事件的接生人选"""
from _bootstrap import *  # noqa: F401,F403
import csv
from unittest import mock

from Script.Design import handle_talent, talk
from Script.Settle import default_cloth
from Script.StateMachine import default as state_machine_default
from Script.System.Pregnancy_System import born_event_panel

# ==== 1. 通用占位符嵌套 ====
section("通用占位符嵌套：里层排在外层前面时也全部替换")


def always_pass(premise_set, character_id, calculated_premise_dict, **kwargs) -> tuple:
    """
    让每条候选文本都通过前提，只测替换逻辑本身
    Keyword arguments:
    premise_set -- 前提集合
    character_id -- 角色id
    calculated_premise_dict -- 已算过的前提
    Return arguments:
    tuple -- (权重 1, 原样的已算前提)
    """
    return 1, calculated_premise_dict


# 构造三层嵌套：outer 插入 {mid}，mid 插入 {inner}；加载顺序取最坏的 inner → mid → outer（只替换一遍时外层插入的里层占位符会原样留下）
fake_common_data = {
    "t_outer_1": mock.Mock(context="外[{mid}]", type_id="outer"),
    "t_mid_1": mock.Mock(context="中<{inner}>", type_id="mid"),
    "t_inner_1": mock.Mock(context="内", type_id="inner"),
}
fake_common_order = {"inner": ["t_inner_1"], "mid": ["t_mid_1"], "outer": ["t_outer_1"]}
with mock.patch.object(game_config, "config_talk_common_cid_list_by_type", fake_common_order), \
        mock.patch.object(game_config, "config_talk_common_data", fake_common_data), \
        mock.patch.object(game_config, "config_talk_common_premise_data", {now_cid: set() for now_cid in fake_common_data}), \
        mock.patch.object(game_config, "config_talk_common_cid_list_by_part", {}), \
        mock.patch.object(handle_premise, "get_weight_from_premise_dict", always_pass):
    nested_result = talk.talk_common_judge("{outer}", 0)
check("三层嵌套、里层的占位符类型排在外层前面：全部替换成最终文本", nested_result == "外[中<内>]", nested_result)

# ==== 2. 体检 AI ====
section("体检 AI：跟随中的干员不去体检，体检科满员时放弃当天体检")
HEALTH_TARGET_LIST = [now_cid for now_cid in game_config.config_target_premise_data if str(now_cid) in {"default210500", "default220505", "default220510"}]
""" AI 目标：去体检科（今日体检 / 等待名单）与在体检科原地等待。目标 cid 在载入时带上所在目录名作前缀（data/target/default） """
check("fixture：三条体检相关的 AI 目标都在目标表里", len(HEALTH_TARGET_LIST) == 3, HEALTH_TARGET_LIST)
bad = [now_cid for now_cid in HEALTH_TARGET_LIST if "not_follow" not in game_config.config_target_premise_data.get(now_cid, set())]
check("去体检科与等待体检的三条 AI 目标都要求「没有在跟随」（否则智能跟随中的干员在体检科与博士之间来回走）", not bad,
      {now_cid: sorted(game_config.config_target_premise_data.get(now_cid, set())) for now_cid in bad})

EXAM_NPC_ID = 9401
""" 排了体检的干员 fixture """
exam_room_str = constant.place_data["Physical_Examination"][0]
exam_room = cache.scene_data[exam_room_str]
exam_npc = make_character(EXAM_NPC_ID, "体检测试干员")
waiting_set = cache.rhodes_island.waiting_for_exam_operator_ids
saved_exam_list = set(exam_room.character_list)
saved_waiting = set(waiting_set)
check("fixture：体检科没满", not map_handle.judge_scene_is_full(exam_room_str))
exam_npc.action_info.health_check_today = 1
exam_npc.behavior = game_type.Behavior()
exam_npc.behavior.start_time = cache.game_time
state_machine_default.character_move_to_physical_examination(EXAM_NPC_ID)
check("体检科没满：排了体检的干员照常动身去体检科，今日体检不变", exam_npc.action_info.health_check_today == 1 and exam_npc.behavior.behavior_id == constant.Behavior.MOVE,
      (exam_npc.action_info.health_check_today, exam_npc.behavior.behavior_id))
exam_room.character_list.update(range(9410, 9420))
check("fixture：体检科坐满 10 人后满员", map_handle.judge_scene_is_full(exam_room_str))
exam_npc.action_info.health_check_today = 1
waiting_set.add(EXAM_NPC_ID)
exam_npc.behavior = game_type.Behavior()
exam_npc.behavior.start_time = cache.game_time
state_machine_default.character_move_to_physical_examination(EXAM_NPC_ID)
check("体检科满员：清掉今日体检并退出等待名单，原地发呆 1 分钟后回到日常行动（不在门口反复重试）",
      exam_npc.action_info.health_check_today == 0 and EXAM_NPC_ID not in waiting_set
      and exam_npc.behavior.behavior_id == constant.Behavior.SHARE_BLANKLY and exam_npc.behavior.duration == 1,
      (exam_npc.action_info.health_check_today, EXAM_NPC_ID in waiting_set, exam_npc.behavior.behavior_id, exam_npc.behavior.duration))
exam_room.character_list.clear()
exam_room.character_list.update(saved_exam_list)
waiting_set.clear()
waiting_set.update(saved_waiting)
remove_character(EXAM_NPC_ID)

# ==== 3. 涨奶的罩杯 ====
section("失去泌乳后，涨奶时变大的罩杯缩回去")
CUP_TALENT_LIST = [121, 122, 123, 124, 125]
""" 罩杯素质：绝壁、贫乳、普乳、巨乳、爆乳 """
MILK_NPC_ID = 9402
milk_npc = make_character(MILK_NPC_ID, "涨奶测试干员")


def settle_cup() -> tuple:
    """
    跑一次涨奶罩杯结算
    Keyword arguments:
    无
    Return arguments:
    tuple -- (当前的罩杯素质id列表, 涨奶标记)
    """
    handle_talent.npc_b_talent_change_for_lactation_flag(MILK_NPC_ID)
    return [now_talent for now_talent in CUP_TALENT_LIST if milk_npc.talent[now_talent]], bool(milk_npc.pregnancy.lactation_flag)


for now_talent in CUP_TALENT_LIST:
    milk_npc.talent[now_talent] = 0
milk_npc.talent[122] = 1
milk_npc.talent[27] = 1
milk_npc.pregnancy.milk_max = 190
milk_npc.pregnancy.milk = 190
milk_npc.pregnancy.lactation_flag = False
check("泌乳中的贫乳干员涨奶：罩杯变成普乳并记下涨奶标记", settle_cup() == ([123], True))
milk_npc.talent[27] = 0
cup_after_stop = settle_cup()
check("失去泌乳素质（停乳药、育儿结束）后的下一次结算：罩杯缩回贫乳、清掉涨奶标记", cup_after_stop == ([122], False), cup_after_stop)
check("再结算一次不会继续缩", settle_cup() == ([122], False))
remove_character(MILK_NPC_ID)

# ==== 4. 离线判定 ====
section("照料婴儿的干员不算离线")
CARER_ID, BABY_ID = 9403, 9404
carer = make_character(CARER_ID, "保育测试干员")
baby = make_character(BABY_ID, "婴儿", daughter=True, stage=101, mother_id=CARER_ID)
carer.target_character_id = BABY_ID
handle_premise.refresh_unnormal_flag(CARER_ID)
check("交互对象是婴儿的干员重算异常位后仍在线（离线看的是她自己是不是婴儿，不是交互对象）", handle_premise.handle_normal_7(CARER_ID) == 1, handle_premise.handle_normal_7(CARER_ID))
handle_premise.refresh_unnormal_flag(BABY_ID)
check("婴儿自己是离线的", handle_premise.handle_normal_7(BABY_ID) == 0)
carer.target_character_id = CARER_ID
remove_character(BABY_ID)
remove_character(CARER_ID)

# ==== 5. 事件数据 ====
section("事件数据：袭击事件不解开博士锁的门、两个选项子事件能被选项面板列出")


def find_event(uid_prefix: str):
    """
    按 uid 前缀找一条事件
    Keyword arguments:
    uid_prefix -- 事件 uid 的前 8 位
    Return arguments:
    game_type.Event -- 事件对象，找不到为 None
    """
    for now_uid, now_event in game_config.config_event.items():
        if now_uid.startswith(uid_prefix):
            return now_event
    return None


ambush_event_list = [find_event("3bbe039d"), find_event("5ad89e16")]
check("fixture：找到干员袭击事件的两条「逆来顺受」（移动时与等待时各一条），它们都让博士进入被逆推的 H",
      all(now_event is not None and "CSE_A2_h_by_active" in now_event.effect for now_event in ambush_event_list))
check("「逆来顺受」的结算里没有「开门」（753）：博士原来锁上的门保持锁着", all(now_event is not None and "753" not in now_event.effect for now_event in ambush_event_list),
      [sorted(now_event.effect) for now_event in ambush_event_list if now_event is not None])
move_parent, move_son = find_event("da8a5d84"), find_event("5925c54e")
check("通用移动事件的选项子事件「不进去」带着父事件的全部前提（选项面板只列出前提包含父事件前提的子事件）",
      move_parent is not None and move_son is not None and set(move_parent.premise) <= set(move_son.premise) | {"option_father"},
      sorted(set(move_parent.premise) - set(move_son.premise)) if move_parent is not None and move_son is not None else "找不到事件")
chat_parent, chat_son = find_event("110b756a"), find_event("108c4126")
check("星熊聊天的选项子事件「爱抚」与父事件属于同一行为（选项面板只在当前行为的事件里找子事件）",
      chat_parent is not None and chat_son is not None and chat_son.behavior_id == chat_parent.behavior_id,
      (chat_parent.behavior_id if chat_parent is not None else None, chat_son.behavior_id if chat_son is not None else None))

# ==== 6. 高潮口上的人名 ====
section("隐奸高潮口上：高潮的人写成 {Name}")
CLIMAX_TALK_DIR = os.path.join(ROOT, "data", "talk", "system", "second_climax")
""" 系统的绝顶口上目录：这些口上由绝顶的干员本人触发，{Name} 是她自己，{TargetName} 是她的交互对象（通常是博士） """
bad = []
for file_name in sorted(os.listdir(CLIMAX_TALK_DIR)):
    if not file_name.endswith(".csv"):
        continue
    with open(os.path.join(CLIMAX_TALK_DIR, file_name), encoding="utf-8") as talk_file:
        for row in csv.reader(talk_file):
            if len(row) >= 5 and "hidden_sex_mode" in row[3] and "{TargetName}" in row[4]:
                bad.append((file_name, row[0]))
check("隐奸中的绝顶口上不用 {TargetName} 指代绝顶的干员（否则会把博士写成绝顶的人）", not bad, (len(bad), bad[:8]))

# ==== 7. 衣柜精液表 ====
section("脱鞋袜进大浴场衣柜：衣柜精液表补齐全部服装部位，穿回时精液回到鞋上")
LOCKER_NPC_ID = 9405
locker_npc = make_character(LOCKER_NPC_ID, "泡脚测试干员")
SHOE_SEMEN = 30
""" 脱鞋前鞋上的精液量（ml） """
sock_id = next(now_cid for now_cid, now_tem in game_config.config_clothing_tem.items() if now_tem.clothing_type == 10 and now_tem.tag != 6)
shoe_id = next(now_cid for now_cid, now_tem in game_config.config_clothing_tem.items() if now_tem.clothing_type == 11 and now_tem.tag != 6)
locker_npc.cloth.cloth_wear[10] = [sock_id]
locker_npc.cloth.cloth_wear[11] = [shoe_id]
# 新开局、新招募的角色衣柜精液表是空的（game_type.DIRTY 的默认值），最小 fixture 用 get_zero_dirty 建出来的是满表，这里还原成真实角色的样子
locker_npc.dirty.cloth_locker_semen = {}
locker_npc.dirty.cloth_semen[11][1] = SHOE_SEMEN
default_cloth.handle_foot_cloth_to_shower_locker(LOCKER_NPC_ID, 5, game_type.CharacterStatusChange(), cache.game_time)
check("鞋袜进了大浴场衣柜，鞋上的精液跟着进了衣柜的表", locker_npc.cloth.cloth_locker_in_shower[10] == [sock_id] and locker_npc.cloth.cloth_locker_in_shower[11] == [shoe_id]
      and locker_npc.dirty.cloth_semen[11][1] == 0 and locker_npc.dirty.cloth_locker_semen[11][1] == SHOE_SEMEN)
check("衣柜精液表覆盖全部服装部位（穿回时按全部部位读这张表）", sorted(locker_npc.dirty.cloth_locker_semen) == sorted(game_config.config_clothing_type),
      sorted(locker_npc.dirty.cloth_locker_semen))
check("衣柜表与穿着表的各部位不共用同一个列表", all(locker_npc.dirty.cloth_locker_semen[now_type] is not locker_npc.dirty.cloth_semen[now_type]
      for now_type in locker_npc.dirty.cloth_locker_semen if now_type in locker_npc.dirty.cloth_semen))
wear_back_error = ""
try:
    default_cloth.handle_shower_locker_to_wear(LOCKER_NPC_ID, 5, game_type.CharacterStatusChange(), cache.game_time)
except Exception as error:  # noqa: BLE001  要把异常类型写进断言的附带信息
    wear_back_error = repr(error)
check("泡完脚穿回鞋袜不报错，鞋袜回到身上、精液回到鞋上", wear_back_error == "" and locker_npc.cloth.cloth_wear[10] == [sock_id] and locker_npc.cloth.cloth_wear[11] == [shoe_id]
      and locker_npc.dirty.cloth_semen[11][1] == SHOE_SEMEN, (wear_back_error, locker_npc.cloth.cloth_wear[10], locker_npc.cloth.cloth_wear[11], locker_npc.dirty.cloth_semen[11][1]))
remove_character(LOCKER_NPC_ID)

section("穿着与衣柜两张服装精液表互不共用：往穿着的衣服上射精不会同时改衣柜的表")
from Script.Core import old_chara_to_new  # noqa: E402


def shared_part_list(dirty_data: game_type.DIRTY) -> list:
    """
    找出穿着表与衣柜表共用同一个列表对象的服装部位
    Keyword arguments:
    dirty_data -- 污浊数据
    Return arguments:
    list -- 共用列表的服装部位id
    """
    return [now_type for now_type in dirty_data.cloth_semen
            if now_type in dirty_data.cloth_locker_semen and dirty_data.cloth_semen[now_type] is dirty_data.cloth_locker_semen[now_type]]


zero_dirty = attr_calculation.get_zero_dirty()
check("新建的空污浊数据：两张表各部位各有各的列表", zero_dirty.cloth_semen is not zero_dirty.cloth_locker_semen and shared_part_list(zero_dirty) == [], shared_part_list(zero_dirty))
SHARE_NPC_ID = 9409
share_npc = make_character(SHARE_NPC_ID, "精液表测试干员")
upper_id = next(now_cid for now_cid, now_tem in game_config.config_clothing_tem.items() if now_tem.clothing_type == 5 and now_tem.tag != 6)
# 两张表都缺某个部位时（旧存档、表被清空过的角色），转移衣服的结算会给两边各补一项
for move_effect in (default_cloth.handle_wear_to_shower_locker, default_cloth.handle_wear_to_dormitory_locker):
    share_npc.cloth = attr_calculation.get_cloth_zero()
    share_npc.cloth.cloth_locker_in_dormitory = attr_calculation.get_cloth_locker_in_dormitory_zero()
    share_npc.cloth.cloth_locker_in_shower = attr_calculation.get_shower_cloth_locker_zero()
    share_npc.cloth.cloth_wear[5] = [upper_id]
    share_npc.dirty.cloth_semen = {}
    share_npc.dirty.cloth_locker_semen = {}
    move_effect(SHARE_NPC_ID, 5, game_type.CharacterStatusChange(), cache.game_time)
    check("两张表都缺部位时把衣服转移到衣柜（%s）：补出来的两边不共用列表" % move_effect.__name__,
          sorted(share_npc.dirty.cloth_semen) == sorted(game_config.config_clothing_type) and shared_part_list(share_npc.dirty) == [], shared_part_list(share_npc.dirty))
# 读档：存档里两张表可能已经是同一个 dict（旧版本「检查衣柜」造成），或各部位共用列表
saved_pl_dirty = pl.dirty
pl.dirty = attr_calculation.get_zero_dirty()
pl.dirty.cloth_locker_semen = pl.dirty.cloth_semen
old_chara_to_new.update_chara_cloth(pl, None)
pl.dirty.cloth_semen[5][1] = 25
check("读档后：原本是同一个 dict 的两张表被拆开，往穿着的上衣上射精不改衣柜的表",
      pl.dirty.cloth_semen is not pl.dirty.cloth_locker_semen and shared_part_list(pl.dirty) == [] and pl.dirty.cloth_locker_semen[5][1] == 0,
      (pl.dirty.cloth_semen is pl.dirty.cloth_locker_semen, shared_part_list(pl.dirty)))
pl.dirty = saved_pl_dirty
remove_character(SHARE_NPC_ID)

# ==== 8. 生产事件的接生人选 ====
section("生产事件：没有凯尔希也没有医疗干员时照常选出接生的人，且不会选到产妇本人")
MOTHER_ID, HELPER_ID, MEDIC_ID = 9406, 9407, 9408
saved_npc_id_got = set(cache.npc_id_got)
cache.npc_id_got.clear()
mother = make_character(MOTHER_ID, "产妇测试干员")
check("岛上只有产妇一名干员时不报错、也不让她给自己接生（返回 0，事件文本里写成医疗部的产科干员）", born_event_panel.get_born_doctor_id(MOTHER_ID) == 0,
      born_event_panel.get_born_doctor_id(MOTHER_ID))
helper = make_character(HELPER_ID, "普通测试干员")
random.seed(20261118)
doctor_pick_list = {born_event_panel.get_born_doctor_id(MOTHER_ID) for _sample in range(40)}
check("没有凯尔希也没有医疗干员、但有别的干员时：由别的干员接生", doctor_pick_list == {HELPER_ID}, doctor_pick_list)
medic = make_character(MEDIC_ID, "医疗测试干员")
medic.profession = 3
mother.profession = 3
mother.name = _("凯尔希")
doctor_pick_list = {born_event_panel.get_born_doctor_id(MOTHER_ID) for _sample in range(40)}
check("产妇是凯尔希时由别的医疗干员接生（她自己虽是医疗干员也不会被选中）", doctor_pick_list == {MEDIC_ID}, doctor_pick_list)
mother.name = "产妇测试干员"
mother.profession = 0
helper.name = _("凯尔希")
check("凯尔希在岛上且不是产妇时由凯尔希接生", born_event_panel.get_born_doctor_id(MOTHER_ID) == HELPER_ID)
for now_cid in (MOTHER_ID, HELPER_ID, MEDIC_ID):
    remove_character(now_cid)
cache.npc_id_got.clear()
cache.npc_id_got.update(saved_npc_id_got)

# ==== 9. 同名图片的取舍 ====
section("同名图片：按固定规则取一个文件，并列出重名")
import tempfile  # noqa: E402

from Script.Core import image_path_index  # noqa: E402


def touch_image(root: str, *part_list) -> str:
    """
    在临时目录里建一个空文件（取舍只看路径，不读内容）
    Keyword arguments:
    root -- 临时的图片根目录
    part_list -- 相对路径的各段
    Return arguments:
    str -- 建好的文件路径
    """
    file_path = os.path.join(root, *part_list)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    open(file_path, "wb").close()
    return file_path


with tempfile.TemporaryDirectory() as temp_dir:
    image_root = os.path.join(temp_dir, "image")
    # 两个分类文件夹下同层级的重名：干员在特殊NPC之前（主支 image/ 里现有的 10 组重名都是这种）
    operator_half = touch_image(image_root, "立绘", "干员", "电弧", "电弧_半身.png")
    npc_half = touch_image(image_root, "立绘", "特殊NPC", "电弧", "电弧_半身.png")
    # 角色主文件夹与更深一层的子文件夹重名：主文件夹里的优先
    main_full = touch_image(image_root, "立绘", "干员", "莱伊", "莱伊_全身.png")
    draft_full = touch_image(image_root, "立绘", "干员", "莱伊", "构思", "莱伊_全身.png")
    # 不重名的图片与非图片文件
    single_half = touch_image(image_root, "立绘", "干员", "莱伊", "莱伊_半身.png")
    touch_image(image_root, "立绘", "干员", "莱伊", "莱伊_body.json")
    image_index, image_duplicates = image_path_index.build_image_path_index(image_root)
check("每个图片名只取一个文件：同层级重名取干员文件夹的，主文件夹与子文件夹重名取主文件夹的",
      image_index == {"电弧_半身": operator_half, "莱伊_全身": main_full, "莱伊_半身": single_half}, image_index)
check("重名的图片被列出来，第一个是取中的文件", image_duplicates == {"电弧_半身": [operator_half, npc_half], "莱伊_全身": [main_full, draft_full]}, image_duplicates)

finish()
