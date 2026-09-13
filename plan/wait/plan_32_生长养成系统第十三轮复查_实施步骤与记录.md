# Plan 32（实施步骤与记录）：生长养成系统第十三轮复查

> 本文件是 `plan_32_生长养成系统第十三轮复查_方案.md`（下文简称"方案"）的**实施步骤清单与过程记录**。
> 需求背景、发现、设计决策、接口定义、风险与范围外事项一律以方案为准；
> 本文件只写"怎么做、怎么验、怎么回滚"，实施过程与结果记入 §6。

- 状态：未实施
- 适用代码快照：`master @ 4275b1c98`
- 实施前提：先通读方案 §2~§5；Q1~Q3 拍板后先回写方案元信息与 §3，再动代码；实施中发现与方案冲突的事实，**先更新方案再动代码**
- 实施约定：主代理先改共用文件，再用 Workflow `system-review-implement` 按下方实施单元并行实施（代理规模先报估算、按用户口径控制）；解释器一律 `./.conda/python.exe`
- 提交建议：一个提交（与 Plan 25~31 相同）

---

## 1. 改动文件清单

| 文件 | 类型 | 改动 |
| --- | --- | --- |
| `Script/System/Education_System/education_constant.py` | 改 | `BIRTHDAY_EVENT_UID`；模板键 5 个常量挪入；翘课日口径与行号的 docstring |
| `Script/Core/constant_promise.py` | 改 | `SELF_HAVE_PUBLIC_COURSE`；`SELF_COURSE_UPCOMING` 说明 |
| `Script/Design/game_time.py` | 改 | `count_play_day` |
| `Script/Core/game_type.py` | 改 | `CHILD_GROWTH` 类说明与 `last_attend_period` 说明 |
| `Script/Design/handle_premise/handle_premise_other.py` | 改 | `handle_self_have_public_course` |
| `Script/Design/handle_premise/__init__.py` | 改 | `get_listen_manual_teach_course`；CVP 课型 / 科目对学生回落 |
| `tools/ArkEditor/csv/Premise.csv` | 改 | 1896 补说明；新前提一行 |
| `Script/System/Education_System/sex_class_handle.py` | 改 | `settle_orphan_class`、`get_class_member_list`；`clean_expired_temp_class`、`get_must_attend_set`、`settle_attend`、`get_watcher_list`、`end_sex_class` 说明 |
| `Script/Settle/realtime_settle.py` | 改 | `judge_pl_real_time_data` 调 `settle_orphan_class` |
| `Script/Settle/default.py` | 改 | 512 跳过节次不同的学生；557 / 10015 说明 |
| `Script/Design/handle_premise/handle_premise_H.py` | 改 | `handle_self_in_sex_class` 改用成员名单；行号引用 |
| `Script/System/Sex_System/group_sex_panel.py` | 改 | 课堂模式选人只列课堂成员 |
| `Script/Core/constant_effect.py` | 改 | 512 / 557 说明 |
| `data/csv/InstructConfig.csv` | 改 | 6008 加 `SEX_CLASS_MODE_OFF` |
| `tools/ArkEditor/csv/Effect.csv` | 改 | 557 说明 |
| `Script/System/Education_System/class_ai.py` | 改 | 删住院判定；见学入口 2；规则 B；`settle_absent`；`judge_course_teacher_available` |
| `Script/Design/handle_premise/handle_premise_work.py` | 改 | 两个教师能否到岗的前提；`self_course_upcoming` 说明 |
| `Script/Design/character_behavior.py` | 改 | NPC 分支在实时结算之前截短 |
| `Script/Design/handle_npc_ai.py` | 改 | 抽出 `judge_student_leave_truncate` |
| `Script/System/Education_System/growth_handle.py` | 改 | 阶段天数与进度按可游玩天；`settle_personality_pair`；倾向改写后重选；`BASE[0]`；557 说明 |
| `Script/System/Education_System/growth_event_handle.py` | 改 | `push_birthday_event`、`drop_stale_stage_event` |
| `Script/System/Pregnancy_System/pregnancy_handle.py` | 改 | 三处阶段转换清残留；婴儿→幼女重刷娱乐 |
| `Script/Settle/past_day_settle.py` | 改 | 翘课 flag 只清过期的；推生日事件 |
| `Script/UI/Panel/character_info_head.py` | 改 | `<翘>`、`<课>`（手动授课、缺课休息、悬停文案） |
| `Script/System/Education_System/class_schedule_panel.py` | 改 | 监禁标注；选修名单去掉必修 |
| `Script/System/Education_System/schedule_handle.py` | 改 | 教师候选排除被监禁 |
| `Script/System/Education_System/course_select_panel.py`、`growth_panel.py`、`schedule_template_panel.py` | 改 | 无用导入与重复导入；周日写死；模板键常量 |
| `Script/Design/second_behavior.py` | 改 | 623 的三种不派情形 |
| `Script/Design/handle_ability.py` | 改 | 待炫耀只记学生岗 |
| `Script/System/Education_System/schedule_template_handle.py` | 改 | 删模板遍历全部角色；非女儿离岗跳过；模板键常量 |
| `data/official_event/通用.csv`、`萝莉.csv`、`幼女.csv`、`期末.csv` | 改 | 方案 §4.3 |
| `data/talk/sex/sex_class/join_sex_class.csv`、`watch_sex_class.csv`、`data/talk/daily/check_report_card.csv` | 改 | 方案 §4.3 |
| `data/target/default/target.csv` | 改 | 210810 / 220830 说明 |
| `tools/tests/education/` 11 个测试文件与 `README.md` | 改 | §2.10 |
| 说明文档、索引文档、Plan 22 总纲、`update.log` | 改 | 方案 §3.15 |

**未改动**：
- `StateMachine/default.py`：303 / 304 / 713~722 不动，判据在 `class_ai`、`sex_class_handle`；716 照旧由截短后的决策派出
- `Second_effect.py`（623 结算器）：不动，派发判定在 `second_behavior`
- `official_event_handle.py` / `official_event_panel.py`：队列逻辑不动，阶段残留由养成侧在长大时清
- `handle_instruct.py`：6008 / 6021 / 授课的处理函数不动，6008 只改显示前提
- `auto_schedule.py`：候选名单由 `schedule_handle.get_teacher_candidate_list` 排除囚犯
- `talk.py`、口上加权机制：属口上系统（L24 只改数据）

### 实施单元

各单元的文件与测试互不相交；本表即 `system-review-implement` 的 `units`。跨单元调用的新接口（新常量、`count_play_day`、公开课前提、`get_listen_manual_teach_course`）一律由主代理先改好。

| 单元 | 标题 | 步骤 | 文件 | 测试 |
| --- | --- | --- | --- | --- |
| 主代理先改 | 共用常量、前提、时钟与手动授课判据 | §2.1 | `education_constant.py`、`constant_promise.py`、`game_time.py`、`game_type.py`（只动说明）、`handle_premise_other.py`、`handle_premise/__init__.py`（只加 `get_listen_manual_teach_course`）、`tools/ArkEditor/csv/Premise.csv` | — |
| U1 | 课堂收尾与课堂计数 | §2.2 | `sex_class_handle.py`、`realtime_settle.py`、`Settle/default.py`、`handle_premise_H.py`、`group_sex_panel.py`、`constant_effect.py`、`InstructConfig.csv`、`tools/ArkEditor/csv/Effect.csv` | `test_sex_class.py`、`test_settle_effects.py` |
| U2 | 上课状态、见学与截短判据 | §2.3 | `class_ai.py`、`handle_premise_work.py` | `test_class_ai.py` |
| U3 | 行为循环 | §2.4 | `character_behavior.py`、`handle_npc_ai.py` | `test_behavior_loop.py` |
| U4 | 阶段进度与性格 | §2.5 | `growth_handle.py` | `test_growth.py` |
| U5 | 养成事件、成长与跨天 | §2.6 | `growth_event_handle.py`、`pregnancy_handle.py`、`past_day_settle.py` | `test_growth_event.py`、`test_prenatal_baby.py` |
| U6 | 状态标识与面板 | §2.7 | `character_info_head.py`、`class_schedule_panel.py`、`schedule_handle.py`、`course_select_panel.py`、`growth_panel.py`、`schedule_template_panel.py` | `test_panels.py`、`test_schedule.py` |
| U7 | 前提、二段与待炫耀 | §2.8 | `handle_premise/__init__.py`（CVP 两函数）、`second_behavior.py`、`handle_ability.py` | `test_premise_tokens.py` |
| U8 | 日程模板 | §2.9 | `schedule_template_handle.py` | `test_schedule_template.py` |
| U9 | 数据与口上 | §2.10 | `data/official_event/` 4 张表、`data/talk/` 3 个文件、`target.csv` | `test_talk_data.py` |

## 2. 详细改动步骤

代码的权威定义都在方案 §3~§4，这里只写落点与检查点。

### 2.0 改动前的基线（先做，结果记入 §6.2）

1. 跑 `./.conda/python.exe tools/tests/education/run_all.py`，记下各文件断言数（定案时 15 个文件、1438 条）
2. 重建复现脚本（不入库）：
   - 定案时的脚本是 scratchpad 的 `p32/repro_c1.py`（13 项）、`p32/repro_main.py`（22 项）、`p32/repro_loop.py`（14 项）、`p32/repro_plan32.py`（复现代理，重跑后填）与探针 `p32/probe_loop.py`（40 项），会话结束即丢；丢了照下表重建
   - 骨架：`.claude/skills/system-review-round/repro_template.py`；行为循环照抄 `test_class_ai.run_loop_round`（`probe_loop.py` / `repro_loop.py` 的 `run_steps` 另装了状态机派发与实时结算的记录包装）
   - 夹具的特殊设定（Plan 31 方案 §2.5-3 与 README）：体力 / 气力设 2000；长循环里清需求后 `refresh_unnormal_flag`；真实 `update_new_day` 要把 `basement.update_base_resouce_newday` 换成空函数，还要补 `cache.rhodes_island.party_day_of_week = {0~6: 0}`（`get_chara_entertainment` 按星期取派对日，本轮复现踩到）；指令的显示前提按 `InstructConfig.csv` 原始行逐个求值

   **主代理脚本 `repro_c1.py`**（H1）

   | 组 | 检查 | 改后 |
   | --- | --- | --- |
   | C1 | 开课 → 走 371 的效果链 → 玩家这一步走完（玩家分支的行为循环）：<br>0 开课后两种模式都开、学生在 H；1 课上 6008 与 6021 的显示前提都成立；2 371 的效果链里没有 10015；3 结束群交后群交模式已关、玩家已不在 H<br>4 玩家这一步走完课堂模式仍开；5 那节课仍 running；6 5209 的 `SEX_CLASS_MODE_OFF` 不成立；7 跨天后 running 仍在<br>8 次日她这一节是实践教室一、教师甲的常规课；9 判 JOIN；10 722 拉进 H；11 出勤与实操课次数各 +1；12 与课无关的干员拿主修经验被乘倍率（10 → 20） | 1、4~7、9~12 不再成立；0、2、3、8 照旧 |

   改前 13 项全部成立：9 项问题命中，3 项前提对照，1 项数据事实。

   **主代理脚本 `repro_main.py`**（M3、M2、L1、L2）

   | 组 | 检查 | 改后 |
   | --- | --- | --- |
   | R1 | M3：<br>0 成年结算先 `settle_personality_talent`、后 `push_graduation_event`；1 全仓库 `settle_personality_talent` 只有两处；2 四条成年事件里结算倾向的选项 13 个、提示写倾向的 8 个<br>3 成年结算后队列依次是通用 1 / 2 / 59 / 60；4 毕业典礼选项 2 倾向 +4；5 提示「倾向：坚强」、素质 274 仍为 0<br>6 成年那一刻萝莉 38 还在队列里；7 成年后才处理萝莉 38，倾向 +3、素质仍为 0 | 5 不再成立；7 随 Q3（按推荐不再成立）；0、1、2、4 随 Q3（按推荐照旧）；3、6 照旧 |
   | R2 | M2：<br>0 3/15 出生的孩子童年里只有第 365 天是生日；1 当天 `self_birthday_today` 成立；2 当天候选 54 条、通用 3 权重 10 / 392<br>3 理论入队概率 1.8%；4 实跑 400 次抽中不到 10% | 3、4 随 Q2（按推荐：日常随机派发的概率不变，照旧成立；改由 `test_growth_event` 断言生日当天插队首）；0~2 照旧 |
   | R3 | L1：<br>0 第 3 节她没课；1 第 3 节没课 `<翘>` 照亮；2 对照：第 1 节有课亮「本该上」；3 必修生人在博士的实操课里；4 课堂上 `<翘>` 照亮 | 1、4 不再成立；0、2、3 照旧 |
   | R4 | L2：<br>0 课堂上与博士同场景派出 caught_skip_class；1 对照：今天翘过课的选修生开课前 5 分钟是 SEX_PENDING；2 在实操教室等开课、博士也在，同样派出；3 16 条被抓口上里 11 条写回教室 / 去上课 | 0、2 不再成立；1、3 照旧 |

   改前 22 项全部成立：8 项问题命中，9 项前提对照，5 项数据事实。

   **主代理脚本 `repro_loop.py`**（L3~L5，走真实行为循环）

   | 组 | 检查 | 改后 |
   | --- | --- | --- |
   | R5 | L3（第 1 节兴趣课「看电影」，8:30 起 120 分钟娱乐）：<br>0 看电影可排兴趣课、AI 会抽、tag 娱乐、时长 120；1 地点解析得出多媒体室；2 对照：人在育儿室截到 8:40；3 对照：120 分钟循环记一节出勤<br>4 人已在多媒体室看电影不截；5 120 分钟循环出勤、缺课都没记 | 4、5 不再成立；0~3 照旧 |
   | R6 | L4：<br>0 对照：没课、一步 60 分钟，实时结算累计 60；1 有课时自由玩耍会截到 8:40；2 一步 60 分钟累计 110 | 2 不再成立；0、1 照旧 |
   | R7 | L5：<br>0 跨天前今天已翘课（新一天的 flag）；1 `update_new_day` 在夹具里跑通；2 对照：前一天的残留 flag 照清<br>3 新一天的 flag 也被清；4 同一天第 2 节不再算今天已翘课 | 3、4 不再成立；0~2 照旧 |

   改前 14 项全部成立：5 项问题命中，8 项前提对照，1 项数据事实。

   **复现代理脚本 `repro_plan32.py`**：（主代理重跑后填表）

   **探针 `probe_loop.py`**（Plan 31 H1 的修法在长步长下是否稳健；改后照旧全部成立）

   | 组 | 情形 | 检查 |
   | --- | --- | --- |
   | S1 / S2 | 教师第 1~4 节在理论教室一 / 二轮换（每次两跳），学生跟着走班；玩家一步 180 分钟 / 120 + 60 分钟，两种处理顺序 | 各轮收敛；教师第 2~4 节都开讲；每节只结算一次；出勤 +3、缺课不变 |
   | S3 | 同上，玩家每步 10 分钟（对照） | 同上 |
   | S4 / S5 | 今天已翘课、第 2 节是空节、空节里 60 / 120 分钟娱乐，玩家一步 180 分钟 | 第 3、4 节各记缺课与翘课（+2 / +2）；空节不记；开课那一刻派 714 |

   40 项全部成立（都是「行为正常」的检查）。
3. `git diff --stat` 记下工作区现状（定案时只有 `config.ini`、`tools/ArkEditor/editor_config.ini` 两个与本轮无关的改动）

### 2.1 主代理先改：共用常量、前提、时钟与手动授课判据（方案 §4.1、§3.2、§3.9）

1. `education_constant`：`BIRTHDAY_EVENT_UID`；模板键 5 个常量（取值照搬 `schedule_template_handle` 现有定义）；`COURSE_STAGE_NONE` / `COURSE_STAGE_UPCOMING` / `UPCOMING_MINUTE` 补翘课日例外；`WATCH_STATE_BASE` 的行号引用改成函数名
2. `constant_promise`：`SELF_HAVE_PUBLIC_COURSE`；`SELF_COURSE_UPCOMING` 说明补翘课日例外
3. `handle_premise_other`：`handle_self_have_public_course`（经 `growth_handle.judge_have_course_type(character_id, COURSE_TYPE_PUBLIC)`，只读）
4. `game_time.count_play_day`：日历天数减去其间非季月的天数，按月累加
5. `handle_premise/__init__.get_listen_manual_teach_course(character_id)`：非玩家、行为是听课、与玩家同场景、玩家行为是授课且 `get_now_teaching(0)` 取不到、开始时刻与玩家对齐时，返回 `get_player_manual_teach_course(0)`；否则 None
6. `game_type.CHILD_GROWTH`：类说明与 `last_attend_period` 说明（L27）
7. `Premise.csv`：1896 补说明；新前提一行
8. 检查点：`test_premise_tokens` 能取到新前提；`count_play_day(9/7 06:00, 12/1 00:05)` 等于 9 月剩余天数加 12 月的天数（不含 10、11 月）

### 2.2 U1：课堂收尾与课堂计数（方案 §3.1、§3.8 L6~L9、L11）

1. `sex_class_handle`：
   - `settle_orphan_class`：课堂模式开着且玩家不在 H → 关课堂模式、`end_sex_class()`，返回 True
   - `clean_expired_temp_class`：running 的那条只在课堂模式开着且玩家在 H 时跳过；否则按过期处理并关课堂模式
   - `get_class_member_list`：与玩家同场景、`is_h`、学生岗或女儿；`get_watcher_list` 改用它
   - `get_must_attend_set(classroom)`：没有 running 时走 `find_class_to_start`
   - `settle_attend`：记出勤时写 `last_attend_period`（节次外不写）
   - `end_sex_class` docstring 改写（方案 §3.1）
2. `realtime_settle.judge_pl_real_time_data` 末尾调 `settle_orphan_class`（函数内延迟导入）
3. `Settle/default.py`：512 对 NPC 教师跳过节次不同的学生；557 与 10015 的 docstring（L27）
4. `handle_premise_H.handle_self_in_sex_class` 改用成员名单；`handle_sex_class_end_early` 的行号引用改成函数名
5. `group_sex_panel.show_target_chara_list`：课堂模式只列 `get_class_member_list()`
6. `InstructConfig.csv` 6008 加 `SEX_CLASS_MODE_OFF`；`constant_effect` 512 / 557 说明；`Effect.csv` 557 说明
7. 检查点：
   - 走 371 / 373 的效果链后玩家这一步走完：课堂模式关、running 清、5209 可用；转单人 H（375）后仍在课、结束 H 后下课；旧档幽灵课（模式开、玩家不在 H）玩家下一步或跨天清掉
   - 课上 6008 不显示、6021 显示
   - 下一节是玩家实操课、上一节教师晚到开讲：学生出勤不变（L6）
   - 实操课之后本节内体力 20%：不再记缺课（与 U2 的 `settle_absent` 合看，U1 只断言 `settle_attend` 写了标记）
   - 下课后同一节重开：没修过理论的必修生开课前就在名单里、记出勤（L8）
   - 课中实行值跌破门槛的成年学生仍在旁观名单与在课前提里（L9）
   - 课堂模式的模板选人不含非学生（L11）

### 2.3 U2：上课状态、见学与截短判据（方案 §3.5、§3.6、§3.7 L3、§3.8 L7 / L10）

1. `class_ai`：
   - `judge_teacher_available` / `judge_mother_available` 删住院判定
   - `judge_should_follow_mother` 入口 2 另要 `handle_premise.handle_all_entertainment_time`
   - `get_student_leave_time` 规则 B：人已在上课地点时截到开课那一刻（离开那一刻本节还有课的仍不截）
   - `settle_absent`：本节已记出勤不记
   - `judge_course_teacher_available(student_id, course)`
2. `handle_premise_work`：两个教师能否到岗的前提改用 `judge_course_teacher_available`；`handle_self_course_upcoming` docstring 补翘课日例外
3. `test_class_ai`：住院夹具改写（M4）；`CLASS_SM_SET` 补 722 并断言与 target 组 07 / 08 一致（L29）
4. 检查点：
   - 病人编号等于教师 / 母亲的角色 id 时照常可用
   - 改任厨师的萝莉日程上午是跟随母亲：工作日上午不见学、晚上照旧；学生岗照旧
   - 人已在多媒体室看电影：截到开课那一刻；对照人在别处截到开课前 20 分钟
   - 同一节已记出勤：721 不再记缺课
   - 不够格的选修生：玩家开课前后都判教师来不了

### 2.4 U3：行为循环（方案 §3.7 L4）

1. `handle_npc_ai.judge_student_leave_truncate`：从 `judge_interrupt_character_behavior` 抽出（守卫：行为开始时刻早于 `cache.game_time`）；原处删掉
2. `character_behavior` 的 NPC 分支：`character_aotu_change_value` 之前调它
3. 检查点：一步 60 分钟、截到 8:40 的学生实时结算累计 60 分钟（此前 110）；`test_behavior_loop` 各轮收敛、上午人均出勤不变

### 2.5 U4：阶段进度与性格（方案 §3.2、§3.4、L28 的 `BASE[0]`）

1. `get_stage_day` / `get_stage_progress` 按可游玩天（`game_time.count_play_day`；阶段起止按有效成长天数换算回日历时刻，早于出生的按出生算）
2. `settle_personality_pair`；`settle_personality_talent` 改为逐对调它
3. `change_growth_value` / `set_growth_value`：已成年（阶段 104）的女儿改写倾向后重选这一对
4. `COURSE_LEARN_BASE[0]` / `COURSE_EXP_BASE[0]` → `[COURSE_TYPE_THEORY]`；`settle_student_class_gain` 的 557 说明
5. 检查点：
   - 122 个季月出生日期逐日推进（用真实的季月跳跃），婴儿中期 [30, 75) 都至少有 12 个可游玩日；9/7 出生的婴儿从 9/30 到 12/1 的进度只走一天
   - 夹具出生日落在季月（旧断言里 `born_time = now − N 天` 的改写）
   - 成年女儿毕业典礼选「倾向：坚强」：坚强素质落上；倾向归零时两侧不动；未成年女儿改倾向不选边

### 2.6 U5：养成事件、成长与跨天（方案 §3.3、§3.7 L5、§3.11）

1. `growth_event_handle.push_birthday_event`、`drop_stale_stage_event`
2. `past_day_settle.update_new_day`：翘课 flag 只清过期的；`check_new_day_official_event` 之前调 `push_birthday_event`
3. `pregnancy_handle`：三处阶段转换换完素质后调 `drop_stale_stage_event`（成年结算在推毕业典礼之前）；`_settle_baby_grow_up` 换完素质后重刷当天娱乐
4. 检查点：
   - 生日当天跨天：通用 3 在她的队首；已在队列里的不重复；非生日不推
   - 新一天的翘课 flag 跨天后仍在；前一天的照清
   - 婴儿 5 入队后长成幼女：队列里不再有它；成年那一刻残留的萝莉事件被清、毕业典礼照在队首
   - 婴儿长成幼女：当天娱乐在幼女默认池里

### 2.7 U6：状态标识与面板（方案 §3.9、§3.13、L28 面板部分）

1. `character_info_head.get_now_class_tip`：L1 / L13 / L14 / L15
2. `class_schedule_panel`：`get_teacher_absent_mark` 加监禁；`_edit_sex_class` 选修名单去掉必修
3. `schedule_handle.get_teacher_candidate_list` 排除被监禁
4. 三个面板删无用导入；`course_select_panel` 周日按 `WEEK_DAY_COUNT`；`schedule_template_panel` 改用模板键常量
5. 检查点：没课的节次与必修实操课上 `<翘>` 不亮；手动授课的学生悬停写博士；缺课休息 `<课>` 不亮；自习悬停不再写减半；囚犯教师标注、一键排课不排；点名必修的选修生只在必修行

### 2.8 U7：前提、二段与待炫耀（方案 §3.10）

1. `handle_premise/__init__`：`get_now_course_type` / `get_now_course_ability` 对学生先问 `get_listen_manual_teach_course`
2. `second_behavior.judge_child_growth_second_behavior`：623 的三种不派情形
3. `handle_ability`：待炫耀只记学生岗
4. 检查点：节次外手动授课，学生 CVP 课型按教室、科目 45；课堂上 / 等开课时不派被抓，翘课在外撞见照派；改任厨师的萝莉升级料理不记待炫耀

### 2.9 U8：日程模板（方案 §3.12）

1. `delete_template` / `get_template_use_count` 遍历 `cache.character_data`
2. `apply_schedule_for_child`：非女儿且不在学生岗的跳过
3. 模块内的模板键与 need 分隔符改用 `education_constant` 的常量（删掉模块级定义）
4. 检查点：离线女儿指着被删的最大号模板，新建同号模板后她的 `schedule_template_id` 已是 0；成年干员改岗后日程不再改写

### 2.10 U9：数据与口上（方案 §3.14、§4.3）

1. `通用.csv` 3 / 5 / 6 / 15 / 27；`萝莉.csv` 删 1 / 20 / 26、改 51 / 57；`幼女.csv` 24；`期末.csv` 新增 3 行
2. `join_sex_class.csv` 1053~1056、`watch_sex_class.csv` 1054 / 1055 加女儿前提；`check_report_card.csv` 新增 2 行
3. `target.csv` 210810 / 220830 的说明
4. 检查点：`tools/official_event_check.py` 通过（期末桶新 3 行不读 23）；`test_talk_data` 断言各行前提；幼女第一次到场「第一次来」的抽中概率与女儿行同量级

### 2.11 文档（方案 §3.15）

1. 说明文档：按方案的清单逐节改；维护注意事项新增三条
2. 索引文档；Plan 22 总纲追加 §18
3. 测试 README：夹具出生日落在季月；`update_new_day` 夹具补派对日表；反斜杠示例改写
4. `update.log`：调用 `update-changelog` skill

### 2.12 测试

| 文件 | 新增 / 改写 |
| --- | --- |
| `test_sex_class.py` | H1 各收尾路径与旧档幽灵课；6008 显示前提；L8 重开；L9 成员名单；L11 模板选人 |
| `test_settle_effects.py` | L6 的 512 跳过；557 说明（模块 docstring） |
| `test_class_ai.py` | M4 撞号；M5 改岗萝莉；L3 规则 B；L7 `settle_absent`；L10 教师为玩家；`CLASS_SM_SET` 与 target 一致 |
| `test_behavior_loop.py` | L4 实时结算只算一遍（真实循环） |
| `test_growth.py` | M1 可游玩天（122 个出生日期）；M3 成年后重选；`count_play_day` |
| `test_growth_event.py` | M2 生日推入；L16 长大清残留；L13 婴儿 4 / 50 断言按季月出生日重写 |
| `test_prenatal_baby.py` | L19 婴儿→幼女的当天娱乐；L5 跨天只清过期 flag（与 `update_new_day` 同段） |
| `test_panels.py` | L1、L12、L13 悬停、L14、L15、L21 |
| `test_schedule.py` | L21 教师候选 |
| `test_premise_tokens.py` | 公开课前提；L13 CVP；L2 被抓；L20 待炫耀 |
| `test_schedule_template.py` | L17、L18；模板键常量 |
| `test_talk_data.py` | 方案 §4.3 的各数据行；期末桶新 3 行过校验 |
| `README.md` | 覆盖描述、断言总数、夹具陷阱 |

## 3. 构建与缓存

```bash
./.conda/python.exe tools/official_event_check.py                    # 改了公务事件表
./.conda/python.exe tools/tests/education/run_all.py                 # 测试引导的增量构建会重建生成物
git diff --stat
git checkout -- data/po/                                             # 本机无 gettext，构建会写乱 PO
```

- 口上改动后先删 `data/Character_Talk.json` 再 `./.conda/python.exe buildconfig.py`（README），否则增量构建跳过口上
- 不新增存档字段，不需要存档迁移

## 4. 验证清单

### 4.1 单元测试（实施方执行，按 `headless-game-test` 模式 A）

- [ ] §2.0 复现：各脚本改前全部成立；改后问题命中不再成立（随口径的按拍板结果读），其余照旧
- [ ] `tools/official_event_check.py` 通过
- [ ] §2.12 各文件新增断言通过
- [ ] `run_all.py` 全部文件 PASS，断言数记入 §6.3

### 4.2 行为循环（实施方执行，按 `headless-game-test` 模式 B）

- [ ] `test_behavior_loop` 各轮收敛；上午四节人均出勤 ≥ 3 节
- [ ] 探针 `probe_loop.py` 照旧 40 项全部成立

### 4.3 游戏内整体测试（由用户执行）

- [ ] 上一节实操课，中途点「结束性技实操课」以外的方式收尾（体力耗尽、学生全部力竭）：下一步课堂模式已关，可以再开课；次日学生照常上那间教室的常规课
- [ ] 课上指令面板只有「结束性技实操课」，没有「结束群交」
- [ ] 新生的婴儿跨过一次季月交替：养成事件抬头与养成总览的进度连续、不跳；婴儿期能遇到「第一次自己坐稳了」等中期事件
- [ ] 女儿第一次生日那天处理公务：队首是生日事件
- [ ] 女儿成年后处理毕业典礼、选带「倾向」的选项：性格素质随之变化
- [ ] 改任厨师的萝莉日程上午排着跟随母亲：工作日上午在厨房
- [ ] Tk 与 Web 两种模式下无报错

## 5. 回滚

| 单元 | 内容 | 回滚方式 | 备注 |
| --- | --- | --- | --- |
| 全部 | 本 Plan | `git revert` 该提交 | 不改存档结构；M3 已重选的素质、L22 清掉的旧 uid 不会自动恢复 |

## 6. 实施过程记录

### 6.1 实际改动

| 文件 | 改动 |
| --- | --- |

与方案的偏离：

（暂无）

### 6.2 实施前的假设复核

| # | 方案中的事实 | 出处 | 复核结果 |
| --- | --- | --- | --- |

### 6.3 单元测试结果

| 文件 | 改前 | 改后 | 新增覆盖 |
| --- | --- | --- | --- |
| **合计** | **1438** | | |

### 6.4 尚未覆盖的验证

- 实施文档 §4.3 的游戏内整体测试留给用户
- PO / MO 重建（本机无 gettext）

### 6.5 追加调整实施记录

（与方案 §8 成对，每轮一节，附回归测试计数。暂无）
