# -*- coding: UTF-8 -*-
"""schedule_template_handle：预设模板、增删改、套用与覆盖、每日改写"""
from _bootstrap import *  # noqa: F401,F403

clear_schedules()
mother = make_character(102, "母亲", 0)
child = make_character(202, "幼女", 152, daughter=True, stage=102, mother_id=102, born_days=120)
loli = make_character(201, "萝莉", 152, daughter=True, stage=103, mother_id=102, born_days=300)
T = education_constant
SELF_STUDY = T.ENTERTAINMENT_SELF_STUDY
FREE_PLAY = T.ENTERTAINMENT_FREE_PLAY
FOLLOW = T.ENTERTAINMENT_FOLLOW_MOTHER
CHESS = schedule_template_handle.get_entertainment_cid_by_name(_("下棋"))
READ = schedule_template_handle.get_entertainment_cid_by_name(_("读书"))

section("预设模板")
check("按名反查娱乐 cid", CHESS > 0 and READ > 0 and schedule_template_handle.get_entertainment_cid_by_name("不存在") == 0
      and schedule_template_handle.get_entertainment_cid_by_name("") == 0)
check("四套预设", schedule_template_handle.get_all_template_id() == [1, 2, 3, 4])
balanced = schedule_template_handle.get_template_data(T.TEMPLATE_BALANCED)
check("均衡 = 上课 / 下棋 / 自由玩耍", balanced["slot"] == {0: SELF_STUDY, 1: CHESS, 2: FREE_PLAY}, balanced)
academic = schedule_template_handle.get_template_data(T.TEMPLATE_ACADEMIC)
check("学业优先 = 上课 / 上课 / 读书", academic["slot"] == {0: SELF_STUDY, 1: SELF_STUDY, 2: READ}, academic)
check("自定义三个时段全空", schedule_template_handle.get_template_data(T.TEMPLATE_CUSTOM)["slot"] == {0: 0, 1: 0, 2: 0})
check("不存在的模板为 None", schedule_template_handle.get_template_data(99) is None)
check("预设判定", schedule_template_handle.judge_template_is_preset(1) and not schedule_template_handle.judge_template_is_preset(5))
schedule_template_handle.set_template_slot(T.TEMPLATE_CUSTOM, 1, CHESS)
check("改模板时段", schedule_template_handle.get_template_data(T.TEMPLATE_CUSTOM)["slot"][1] == CHESS)
schedule_template_handle.set_template_slot(99, 1, CHESS)
check("改不存在的模板不报错", True)
saved = {k: dict(v["slot"]) for k, v in cache.rhodes_island.child_schedule_template.items()}
schedule_template_handle.init_default_template()
check("已有模板时不再覆盖", {k: dict(v["slot"]) for k, v in cache.rhodes_island.child_schedule_template.items()} == saved)

section("新建 / 改名 / 删除")
new_id = schedule_template_handle.create_template("")
check("新建编号顺延且自动命名", new_id == 5 and schedule_template_handle.get_template_data(5)["name"] == _("模板{0}").format(5))
check("改名", schedule_template_handle.rename_template(5, "  夜猫子 ") and schedule_template_handle.get_template_data(5)["name"] == "夜猫子")
check("空名不改", not schedule_template_handle.rename_template(5, "  ") and schedule_template_handle.get_template_data(5)["name"] == "夜猫子")
check("改不存在的模板 False", not schedule_template_handle.rename_template(99, "x"))
schedule_template_handle.apply_template(201, 5)
schedule_template_handle.set_child_override(201, 2, FREE_PLAY)
check("预设不可删", not schedule_template_handle.delete_template(1) and 1 in cache.rhodes_island.child_schedule_template)
check("删自建模板", schedule_template_handle.delete_template(5) and 5 not in cache.rhodes_island.child_schedule_template)
check("删前解开引用它的孩子", loli.child_growth.schedule_template_id == 0 and loli.child_growth.schedule_override == {})
check("删不存在的 False", not schedule_template_handle.delete_template(5))
# 编号取「现存最大 + 1」：删掉的正是最大号时会被复用；靠删除时的解引用保证不串日程
reused_id = schedule_template_handle.create_template("再来一套")
check("删掉最大号后新模板复用该编号，且原先套它的孩子仍是未套用", reused_id == 5 and loli.child_growth.schedule_template_id == 0)
schedule_template_handle.apply_template(202, reused_id)
schedule_template_handle.create_template("第七套")
check("中间空缺号不被补", schedule_template_handle.delete_template(reused_id) and schedule_template_handle.create_template("再一套") == 7 and child.child_growth.schedule_template_id == 0)

section("套用与覆盖")
schedule_template_handle.apply_template(201, T.TEMPLATE_BALANCED)
check("套用写入编号", loli.child_growth.schedule_template_id == T.TEMPLATE_BALANCED)
schedule_template_handle.set_child_override(201, 1, READ)
check("覆盖优先于模板", schedule_template_handle.get_child_slot_activity(201, 1) == READ and schedule_template_handle.get_child_slot_activity(201, 0) == SELF_STUDY)
schedule_template_handle.set_child_override(201, 1, 0)
check("取消覆盖回到模板值", schedule_template_handle.get_child_slot_activity(201, 1) == CHESS)
schedule_template_handle.set_child_override(201, 2, READ)
schedule_template_handle.apply_template(201, T.TEMPLATE_ACADEMIC)
check("换模板清空覆盖", loli.child_growth.schedule_override == {})
schedule_template_handle.apply_template(201, T.TEMPLATE_ACADEMIC)
check("重复套用同一模板不动覆盖", True)
check("没养成数据的角色时段为 0", schedule_template_handle.get_child_slot_activity(102, 0) == 0)
check("批量套用跳过不存在的角色", schedule_template_handle.batch_apply_template([201, 202, 999], T.TEMPLATE_BALANCED) == 2)
check("套用人数统计", schedule_template_handle.get_template_use_count(T.TEMPLATE_BALANCED) == 2 and schedule_template_handle.get_template_use_count(T.TEMPLATE_PLAYFUL) == 0)
text = schedule_template_handle.get_child_schedule_text(201)
check("日程摘要含模板名与三个时段", text.startswith(_("均衡")) and text.count("/") == 2, text)
schedule_template_handle.apply_template(201, 0)
check("取消套用后为「未设置」", schedule_template_handle.get_child_schedule_text(201) == _("未设置"))

section("need 校验与课表优先")
check("跟随母亲：幼女可、萝莉不可", schedule_template_handle.judge_activity_need_pass(202, FOLLOW) and not schedule_template_handle.judge_activity_need_pass(201, FOLLOW))
check("无 need 条件一律可", schedule_template_handle.judge_activity_need_pass(201, FREE_PLAY))
check("不存在的娱乐不可", not schedule_template_handle.judge_activity_need_pass(201, 99999))
open_all_classroom()
schedule_handle.set_selected_course(201, cache.game_time.weekday(), 0, T.COURSE_TYPE_THEORY, _("理论教室一"))
check("上午有课 → 时段 0 不空", not schedule_template_handle.judge_slot_free_of_class(201, 0, cache.game_time.weekday()))
check("下午没课 → 时段 1 空", schedule_template_handle.judge_slot_free_of_class(201, 1, cache.game_time.weekday()))
check("晚上永远空", schedule_template_handle.judge_slot_free_of_class(201, 2, cache.game_time.weekday()))

section("每日改写")
loli.entertainment.entertainment_type = [11, 12, 13]
schedule_template_handle.apply_schedule_for_child(201)
check("没套模板不改写", loli.entertainment.entertainment_type == [11, 12, 13])
schedule_template_handle.apply_template(201, T.TEMPLATE_BALANCED)
schedule_template_handle.apply_schedule_for_child(201)
check("有课的时段保留随机值、没课的按模板改写", loli.entertainment.entertainment_type == [11, CHESS, FREE_PLAY], loli.entertainment.entertainment_type)
custom = schedule_template_handle.create_template("跟妈")
schedule_template_handle.set_template_slot(custom, 2, FOLLOW)
schedule_template_handle.batch_apply_template([201, 202], custom)
loli.entertainment.entertainment_type = [11, 12, 13]
child.entertainment.entertainment_type = [11, 12, 13]
schedule_template_handle.apply_schedule_for_child(201)
schedule_template_handle.apply_schedule_for_child(202)
check("萝莉不满足 need 的时段跳过、幼女写入", loli.entertainment.entertainment_type[2] == 13 and child.entertainment.entertainment_type[2] == FOLLOW)
check("候选活动表不含 0 号", 0 not in schedule_template_handle.get_schedule_activity_candidate() and FOLLOW in schedule_template_handle.get_schedule_activity_candidate())
schedule_template_handle.apply_schedule_for_child(102)
check("没有养成数据的干员不报错", True)

finish()
