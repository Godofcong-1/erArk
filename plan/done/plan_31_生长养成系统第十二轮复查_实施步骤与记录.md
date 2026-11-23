# Plan 31（实施步骤与记录）：生长养成系统第十二轮复查

> 本文件是 `plan_31_生长养成系统第十二轮复查_方案.md`（下文简称"方案"）的**实施步骤清单与过程记录**。
> 需求背景、发现、设计决策、接口定义、风险与范围外事项一律以方案为准；
> 本文件只写"怎么做、怎么验、怎么回滚"，实施过程与结果记入 §6。

- 状态：已实施（2026-09-13；用户确认 Q1~Q4 均按推荐）
- 适用代码快照：`master @ 44ed83f15`
- 实施前提：先通读方案 §2~§5；Q1~Q4 拍板后先回写方案元信息与 §3，再动代码；实施中发现与方案冲突的事实，**先更新方案再动代码**
- 实施约定：主代理先改共用文件，再用 Workflow `system-review-implement` 按下方实施单元并行实施（代理规模先报估算、按用户口径控制）；解释器一律 `./.conda/python.exe`
- 提交建议：一个提交（与 Plan 25~30 相同）

---

## 1. 改动文件清单

| 文件 | 类型 | 改动 |
| --- | --- | --- |
| `Script/Core/game_type.py` | 改 | `CHILD_GROWTH` 加 `skip_class_day`、`sex_class_count`（方案 §4.1） |
| `Script/System/Education_System/education_constant.py` | 改 | `GROWTH_VALUE_SEX_CLASS`、`ADULT_EXTRA_EVENT_UID_LIST` |
| `Script/Core/constant_promise.py` | 改 | 6 个新前提名 |
| `Script/System/Education_System/growth_handle.py` | 改 | `get_growth_value` 读 25；新增 `judge_have_course_type` |
| `Script/System/Education_System/class_ai.py` | 改 | `judge_skip_class_today`、`judge_teacher_available(…, classroom)`；`get_course_stage` / `judge_student_pullable` / `judge_student_join_class` / `get_student_leave_time` |
| `Script/Settle/default.py` | 改 | 557 放宽；549 写 `skip_class_day` |
| `Script/Design/second_behavior.py` | 改 | 623 的触发改判 `judge_skip_class_today` |
| `Script/Design/instuct_judege.py` | 改 | `calculation_instuct_judege` 加 `settle_hypnosis` |
| `Script/System/Education_System/sex_class_handle.py` | 改 | 门槛传 `settle_hypnosis=False`；`settle_attend` 按那一节判缺课、记实操课次数 |
| `Script/System/Education_System/schedule_handle.py` | 改 | `get_course_at` 收窄；`get_now_teaching` / `get_upcoming_teaching` 只认教师岗；docstring |
| `Script/System/Education_System/growth_event_handle.py` | 改 | 成年结算推通用 59 / 60；同学只取幼女 / 萝莉；注释 |
| `Script/Design/handle_premise/__init__.py` | 改 | CVP 对玩家手动授课的回落 |
| `Script/Design/handle_premise/handle_premise_work.py` | 改 | 教师能到岗的两个前提传教室 |
| `Script/Design/handle_premise/handle_premise_other.py` | 改 | 6 个新前提；同学前提 docstring |
| `Script/UI/Panel/character_info_head.py` | 改 | `<翘>` 改判 `judge_skip_class_today` |
| `Script/System/Education_System/growth_panel.py` | 改 | 翘课标记改判 `judge_skip_class_today` |
| `Script/System/Education_System/class_schedule_panel.py` | 改 | 排实操课页选修人数按门槛分行；全局课表离岗教师标注 |
| `Script/System/Education_System/course_select_panel.py` | 改 | 选课页离岗教师标注 |
| `data/official_event/萝莉.csv`、`幼女.csv`、`通用.csv`、`婴儿.csv` | 改 | 方案 §4.3 |
| `data/talk/sex/sex_class/join_sex_class.csv`、`watch_sex_class.csv`、`data/talk/work/skip_class.csv`、`data/talk/daily/check_report_card.csv`、`data/talk/work/teach.csv`、`attent_class.csv` | 改 | 方案 §4.3 |
| `data/talk/system/second_show_off_study/show_off_waist_skill.csv` | 删 | M4 |
| `tools/ArkEditor/csv/Premise.csv` | 改 | 3 行补全、6 行新前提 |
| `tools/official_event_check.py` | 改 | 期末桶禁 9 / 23、未成年与宿舍桶并入 200、成年桶只收显式推入的 uid；docstring 归位 |
| `buildata.py` | 改 | `split(" ", 1)` |
| `Script/System/Official_Event_System/official_event_handle.py` | 改 | `push_official_event` 加 `ignore_capacity`（方案 §3.2，实施时补） |
| `.github/skills/text_generation_for_instruction_code_generation/学习前提/性技科目对照表.md` | 改 | 腰技不写炫耀二段（M4，免得照表再生成一批死口上） |
| `tools/tests/education/` 10 个测试文件与 `README.md` | 改 | §2.11 |
| 说明文档、索引文档、Plan 22 总纲、`update.log` | 改 | 方案 §3.17 |

**未改动**：
- `StateMachine/default.py`：303 的拉人循环不动，判据在 `class_ai.judge_student_join_class`；714 / 721 不动；722 经 `settle_attend`
- `past_day_settle.py`、`Second_effect.py`（623）：照旧清翘课 flag，日期由 `judge_skip_class_today` 兜住
- `auto_schedule.py`：维持只填空格（方案 §3.10）
- `talk.py`、口上加权机制：属口上系统（方案 §7）

### 实施单元

各单元的文件与测试互不相交；本表即 `system-review-implement` 的 `units`。跨单元调用的新接口（`judge_skip_class_today`、`judge_teacher_available` 的 `classroom`、`judge_have_course_type`、新常量、新前提名）一律由主代理先改好。

| 单元 | 标题 | 步骤 | 文件 | 测试 |
| --- | --- | --- | --- | --- |
| 主代理先改 | 共用字段、常量、前提名与两个判据 | §2.1 | `game_type.py`、`education_constant.py`、`constant_promise.py`、`growth_handle.py`、`class_ai.py`（只动 `judge_skip_class_today` 与 `judge_teacher_available`）、`tools/ArkEditor/csv/Premise.csv` | `test_save_compat.py`、`test_growth.py` |
| U1 | 上课状态与拉人 | §2.2 | `class_ai.py`（其余四个函数） | `test_class_ai.py` |
| U2 | 晚到结算与翘课 flag 写入 | §2.3 | `Settle/default.py`、`second_behavior.py` | `test_settle_effects.py` |
| U3 | 实操课门槛与出勤 | §2.4 | `instuct_judege.py`、`sex_class_handle.py` | `test_sex_class.py` |
| U4 | 取数口与教师反查 | §2.5 | `schedule_handle.py` | `test_schedule.py` |
| U5 | 前提与状态标识 | §2.6 | `handle_premise/__init__.py`、`handle_premise_work.py`、`handle_premise_other.py`、`character_info_head.py` | `test_premise_tokens.py` |
| U6 | 面板 | §2.7 | `class_schedule_panel.py`、`course_select_panel.py`、`growth_panel.py` | `test_panels.py` |
| U7 | 养成事件 | §2.8 | `growth_event_handle.py` | `test_growth_event.py` |
| U8 | 数据、口上与校验工具 | §2.9 | `data/official_event/` 4 张表、`data/talk/` 7 个文件、`tools/official_event_check.py`、`buildata.py` | `test_talk_data.py` |

## 2. 详细改动步骤

代码的权威定义都在方案 §3~§4，这里只写落点与检查点。

### 2.0 改动前的基线（先做，结果记入 §6.2）

1. 跑 `./.conda/python.exe tools/tests/education/run_all.py`，记下各文件断言数（定案时 15 个文件、1206 条）
2. 重建复现脚本（不入库）：
   - 定案时的脚本是 scratchpad 的 `p31/repro_main.py`（主代理写，40 项）与 `p31/repro_plan31.py`（核实兼复现代理写、主代理重跑并改了 5 项的改后预期，121 项），会话结束即丢；丢了照下两表重建
   - 骨架：`.claude/skills/system-review-round/repro_template.py`；派发照抄 `test_class_ai.py` 的 `prepare_ai` / `dispatch`，行为循环照抄 `test_behavior_loop.run_one_round`
   - 夹具的三处特殊设定（方案 §2.5-3）：`get_npc_cloth` 穿不上时从 201 的模板借一套衣服；体力 / 气力设 2000；长循环里清需求后 `refresh_unnormal_flag`。真实 `update_new_day` 在夹具里会卡在基建日结，要用时把 `basement.update_base_resouce_newday` 临时换成空函数

   **主代理脚本 `repro_main.py`**

   | 组 | 检查 | 改后 |
   | --- | --- | --- |
   | R1 | H1（玩家 9:40 等 60 分钟；教师第 1 节理论教室一、第 2 节二）：<br>0 教师 9:47 才在教室二开讲；1 学生 9:45 先坐下（304）<br>2 变体 A：第 2 节一次都没结算；3 这一节也没记缺课<br>4 变体 B：学生被拉回 9:47；5 第 3 节记上两次；6 两节课出勤 +3<br>7 对照：每步 10 分钟时第 2 节照常结算 | 2 / 4 / 5 / 6 不再成立；0 / 1 / 3 / 7 照旧 |
   | R2 | M1（心控中的成年学生，玩家有中级催眠）：<br>0 排过性技教室课；1 没有补正时实行值不足<br>2 前提求值一次扣理智；3 再求值又扣；4 今日消耗累加；5 理智为 0 时催眠被清 | 2~5 不再成立；0 / 1 照旧 |
   | R3 | M3：<br>0 空气催眠、人不在教室判能到岗；1 `normal_all` 不成立<br>2 对照：人在教室判能到岗；3 木头人判能到岗；4 木头人被锁成等待 | 0 / 3 不再成立；1 / 2 / 4 照旧 |
   | R4 | M2：<br>0 59 / 60 在成年桶；1 日常名单不含成年女儿<br>2 每日派发 300 次没有 59 / 60；3 成年结算只推通用 1 / 2 | 2 / 3 随 Q2（按推荐不再成立）；0 / 1 照旧 |
   | R5 | L3：<br>0 9:40 开讲复用的是第 2 节的预约；1 上一节缺过课，出勤没记上；2 对照：9:46 按时开讲照记 | 1 不再成立；0 / 2 照旧 |
   | R6 | L1（空节 9:55 起看 120 分钟电影）：<br>0 看电影是娱乐类；1 对照：不挂 flag 截到 10:10；2 挂 flag 不截 | 2 不再成立；0 / 1 照旧 |
   | R7 | L1（挂 flag、14:00 有课）：<br>0 13:45 空下来是 UPCOMING；1 同一人在娱乐中 B 不截；2 14:00 判 SKIP | 0 / 1 不再成立；2 照旧 |
   | R8 | L2：<br>0 周一的 flag 没清，周二 9:00 判 SKIP；1 跨天在 NPC 阶段之后；2 跨天只清 `npc_id_got` | 0 不再成立；1 照旧；2 随口径 |
   | R9 | M3 学生侧：<br>0 学生按「能到岗」派 304；1 零收益、出勤不变 | 1 不再成立；0 随口径（改后派 713） |
   | R10 | L9 / L15：<br>0 512 按教室判课型；1 CVP 两项为 -1；2 只剩占位地文 | 1 / 2 不再成立；0 照旧 |

   改前 40 项全部成立：19 项问题命中，18 项前提对照，3 项数据事实。改后按推荐口径：18 项不再成立（问题命中 17 项 + R7-1），4 项随口径，18 项照旧。

   **代理脚本 `repro_plan31.py`**（组号是代理的编号；「对应」列是方案编号）

   | 组 | 对应 | 问题命中（改后不再成立，除非另注） | 其余 |
   | --- | --- | --- | --- |
   | R1 | H1 | 变体 A 第 2 节零结算；变体 B 出勤 +3；R1-3 学生被拉回 9:47（前提对照，改后不再成立） | 教师走两跳 9:47 开讲、学生 9:45 坐下、一步 45 分钟的对照、处理顺序反过来同样丢 |
   | R2 | M2 | 1000 次派发没有 59 / 60（随 Q2） | 成年桶的 4 条、名单只收 101~103、默认提供者跳过部门 15、成年结算只推 1 / 2、调用点 4 处 |
   | R3 | L9、L15 | 占位与正式口上同场抽；3000 次抽中 33.8%；玩家手动授课只剩占位；成年学生听课只剩占位（随 Q4） | 通用文本开关、口上前提统计 |
   | R4 | L2（换季部分见方案 §7） | flag 带进周一上午，缺课与翘课各 +3；换季首日两节记进上学期（**照旧**） | 跨天在 NPC 阶段之后、换季首日上午两节已上完 |
   | R5 | M1 | 前提两次扣两次；理智为 0 时清催眠；一次决策调门槛 6 次 | 门槛走到实行值计算 |
   | R6 | M3 | 空气催眠判能到岗；学生 304 零收益；木头人判能到岗；木头人的学生零收益 | `normal_all` 不成立、教师派不出 561 / 303、木头人被锁 |
   | R7 | M4 | 52 条腰技炫耀口上 | 另 17 门升级、腰技恒为 0、`sex_need` 与女儿性别 |
   | R8 | L10 | 萝莉 1 / 20、萝莉 26、萝莉 6 在候选里（随 Q4） | 没有成绩单、终身与本学期出勤、`level_change` 只记上涨 |
   | R9 | L11 | 只排理论课的萝莉抽到 7 / 8 / 9 / 16；只排体育课的幼女抽到幼女 1 / 22（随 Q4） | 体育课是真课 |
   | R10 | L12 | 「老学生」到场与旁观口上成立；「第一次来」读不到；1004 在翘课 5 节时成立（随 Q4） | 数据统计、累计 0 节的对照 |
   | R11 | 方案 §7 | 日程自习一条口上都没有（**照旧**） | 548 照给收益、教师缺席时有口上、口上全带 Course |
   | R12 | L16 | 期末桶读 9、读 23、改能力、写育儿室都不报错 | 原样期末 9 不报、放进萝莉桶会报、推送时 9 = 0 与 23 = 1 |
   | R13 | L13 | 出生当天就有婴儿 4 / 50；任意一天有通用 3 / 15（随 Q4） | 阶段进度 0、没有生日前提 |
   | R14 | L14 | 档位 3 只剩两条兜底口上（随 Q4） | 档位 3、理由「没有上课」 |
   | R15 | 方案 §2.3 | B 把注定翘掉的一节赶去教室（**照旧**）；A 截回实操教室（随口径，维持） | 45% 档、开课那一刻判 SKIP |
   | R16 | L3 | 14:40 提前开讲出勤 +0 | 按时 +1、标记改成本节时 +1 |
   | R17 | L4 | 改任厨师后 `<课>` 显示实习课；CVP 读成 5 | Plan 30 的真课判定已判不是 |
   | R18 | L5 | 跟随中与有吃饭需求的学生都被 303 拉走 | normal 3 / 1 不成立、她们自己决策不派 304 |
   | R19 | L1 | 挂 flag 时 UPCOMING；AI 派 715 | B 不截的对照、开课那一刻 SKIP |
   | R20 | L7 | 成年姐姐算幼女的同学；幼女 41 的对象是她 | 同胞排除 104 |
   | R21 | L6 | 一键排课不补位（**照旧**，方案 §3.10）；CVP 读成旧授课格的实践课 | 运行时已判不可用、她自己的课是理论课 |
   | R22 | L2 | 离线跨天后 flag 仍在；回岛第 1 节 SKIP；714 记翘课 | 离线后不在 `npc_id_got` |
   | R23 | L8 | 面板算她会来 | 开课名单没有她、必修判据挡掉她 |
   | R24 | L1 | 挂 flag 看完 120 分钟电影，第 3 节整节漏记 | 盖过第 3 节、不挂 flag 的对照 |
   | R25 | L17 | 3 行截断；重生成会截回另 3 行 | — |
   | R26 | L18 | 注释、§6 第 200 行、同学 docstring、`get_now_course` 说明、`TEXT_DUP_LEN` | 第 213 行是 Q1、`judge_personal_course_valid` 写了借书 |

   改前 121 项全部成立：59 项问题命中，50 项前提对照，11 项数据事实，1 项随口径。改后核对：标「照旧」的 4 项问题命中（R4-4、R11-1、R15-1、R21-1）与随 Q2 / Q4 的项按拍板结果读，其余问题命中与 R1-3 不再成立，前提对照与数据事实照旧。
3. `git diff --stat` 记下工作区现状（定案时只有 `config.ini`、`tools/ArkEditor/editor_config.ini` 两个与本轮无关的改动）

### 2.1 主代理先改：共用字段、常量、前提名与两个判据（方案 §4.1、§3.4、§3.6）

1. `game_type.CHILD_GROWTH` 加 `skip_class_day`（`skip_class_flag` 之后）、`sex_class_count`（`skip_caught_day` 之后）
2. `education_constant` 加 `GROWTH_VALUE_SEX_CLASS = 25`、`ADULT_EXTRA_EVENT_UID_LIST`
3. `constant_promise.Premise` 加 6 个前提名；`Premise.csv` 加 6 行，并补全 2027 / 2029 / 2030 三行的描述
4. `growth_handle`：`get_growth_value` 读编号 25；新增 `judge_have_course_type(character_id, course_type) -> bool`（学生岗，任一格课型相符且 `judge_selected_cell_real`；只读 `child_growth`）
5. `class_ai`：新增 `judge_skip_class_today`；`judge_teacher_available` 加 `classroom` 参数与 §3.4 的两条
6. 检查点：
   - 旧档读入后两个新字段补默认值（`test_save_compat`）
   - 编号 25 没有养成数据时为 0；`judge_have_course_type` 对改岗、已停课、课型不符都为 False（`test_growth`）

### 2.2 U1 上课状态与拉人（方案 §3.1、§3.5、§3.6、§3.9）

1. `get_course_stage`：翘课判断改走 `judge_skip_class_today`；本节没课、下一节有课但今天已翘课 → NONE
2. `judge_student_pullable`：flag 改走 `judge_skip_class_today`
3. `judge_student_join_class`：过 `normal_all_except_special_hypnosis`；学生当前行为的开始时刻晚于 `now_time` 不拉
4. `get_student_leave_time`：今天已翘课的，规则 B 截到开课那一刻（不要求上课地点）
5. 检查点：
   - 空气催眠、人不在教室 / 在教室，木头人（`judge_teacher_available`，§2.1 的改动在这里断言）
   - 挂 flag 13:45 空下来 → NONE、不派 715；在娱乐中截到 14:00；14:00 派 714 记缺课
   - 挂 flag 看 120 分钟电影 → 截到下一节开课那一刻
   - 前一天挂的 flag、离线后回岛：当天照常掷骰
   - 跟随中、有需求的学生不被 303 拉；时间线在前的学生不被拉回；与教师同时开始的照拉

### 2.3 U2 晚到结算与翘课 flag 写入（方案 §3.1、§3.6）

1. 557：本节教师 `judge_teacher_available(教师, 教室)` 成立即结算；不再要求教师在场授课
2. 549：置 flag 时写 `skip_class_day`
3. `second_behavior.judge_child_growth_second_behavior`：623 的触发改判 `judge_skip_class_today`
4. 检查点：
   - 教师还在走廊时学生开始听课 → 结算一次；教师随后开讲的 512 不再重复
   - 教师判来不了时 557 不结算
   - 前一天挂的 flag 不触发翘课被抓

### 2.4 U3 实操课门槛与出勤（方案 §3.3、§3.7、§3.14 L12）

1. `calculation_instuct_judege` 加 `settle_hypnosis=True`；为 False 时催眠补正照算、不扣理智不清催眠
2. `judge_can_join_sex_class` 传 `settle_hypnosis=False`
3. `settle_attend`：正在进行的实操课节次开始时刻晚于参照时刻时按那一节判缺课；记出勤时 `sex_class_count` +1
4. 检查点：
   - 心控中的成年学生：门槛与前提求值多次，理智与催眠都不变；理智够时门槛照样成立
   - 提前 5 分钟开讲、上一节缺过课 → 出勤 +1、实操课次数 +1；这一节本身缺过课 → 都不加

### 2.5 U4 取数口与教师反查（方案 §3.8、§3.10）

1. `get_course_at`：非学生岗返回 None
2. `get_now_teaching` / `get_upcoming_teaching`：非玩家且不在教师岗返回 None
3. `get_now_course` 的 docstring 补借不到书与非学生岗
4. 检查点：改岗后 `get_now_course` / `get_upcoming_course` 为 None，改回恢复；前教师改学生岗后教师反查为 None

### 2.6 U5 前提与状态标识（方案 §3.4、§3.6、§3.13、§3.14）

1. CVP `CourseType` / `Course`：玩家手动授课的回落
2. `handle_self_course_teacher_available` / `unavailable` 传 `now_course["classroom"]`
3. `handle_premise_other`：6 个新前提（走 `judge_have_course_type` 与 `pregnancy.born_time`）；同学前提 docstring
4. `character_info_head.get_now_class_tip`：`<翘>` 改判 `judge_skip_class_today`
5. 检查点：
   - 玩家在理论教室手动授课 → CVP 为理论课 / 学识
   - 6 个新前提注册；课型前提对改岗、已停课为 0；生日前提在生日当天为 1、第二天为 0（2 月 29 日出生的在平年 2 月 28 日为 1）
   - 改任厨师的女儿在厨房不亮 `<课>`；前一天的 flag 不亮 `<翘>`

### 2.7 U6 面板（方案 §3.10、§3.12、§3.6）

1. `class_schedule_panel._edit_sex_class`：选修名单按 `judge_can_join_sex_class` 分出「此刻进不了课堂」一行
2. 全局课表与个人课表选课页：离岗 / 不在岛上的教师名字后加标注（灰字）
3. `growth_panel`：翘课标记改判 `judge_skip_class_today`
4. 检查点：面板文本（`drawn_text`）含对应行；Web 适配器冒烟

### 2.8 U7 养成事件（方案 §3.2、§3.11）

1. `push_graduation_event`：通用 1 / 2 之后把 `ADULT_EXTRA_EVENT_UID_LIST` 推到队尾（过 `judge_event_can_enqueue`）
2. `get_classmate_list`：对方阶段须在 `SIBLING_PLAY_STAGE_SET`
3. `push_semester_event_for_list` 的注释改写
4. 检查点：成年结算后队列里依次有通用 1 / 2 / 59 / 60；成年姐姐不算同学

### 2.9 U8 数据、口上与校验工具（方案 §3.14~§3.16、§4.3）

1. 按方案 §4.3 改事件表与口上；删腰技炫耀口上与两条占位行；新增 4 条档位 3 口上
2. `official_event_check.py`：`SEMESTER_VALUE_ID` 扩为 {4, 5, 6, 9, 23}；`CHILD_SUB_KEY` / `DORM_SUB_KEY` 并入 200；成年桶只收 `GRADUATION_EVENT_UID` / `ADULT_MEMORIAL_EVENT_UID` / `ADULT_EXTRA_EVENT_UID_LIST`（工具不 import 游戏模块，照旧另抄一份并注明）；`TEXT_DUP_LEN` 的 docstring 归位
3. `buildata.constand_promise_2_csv`：`split(" ", 1)`
4. 检查点：
   - 真实事件表整张通过；构造的违规行各报一条、对照行不报
   - 炫耀口上覆盖按女儿可学的 17 门；男性专属科目没有带女儿前提的炫耀口上
   - 口上前提 token 逐条校验通过（新前提名已注册）

### 2.10 文档（方案 §3.17）

1. 说明文档：按方案的清单逐节改；维护注意事项新增三条
2. 测试 README：覆盖描述、断言总数、fixture 陷阱补两条
3. 索引文档；Plan 22 总纲追加 §17 回指
4. `update.log`：调用 `update-changelog` skill

### 2.11 测试

| 文件 | 新增 / 改写 |
| --- | --- |
| `test_save_compat.py` | 两个新字段回填 |
| `test_growth.py` | 编号 25；`judge_have_course_type` |
| `test_class_ai.py` | §2.2 检查点；M3 的教师可用性 |
| `test_settle_effects.py` | §2.3 检查点 |
| `test_sex_class.py` | §2.4 检查点 |
| `test_schedule.py` | §2.5 检查点 |
| `test_premise_tokens.py` | §2.6 检查点 |
| `test_panels.py` | §2.7 检查点 |
| `test_growth_event.py` | §2.8 检查点；Q4 各事件的新前提逐条（候选里有 / 没有） |
| `test_talk_data.py` | §2.9 检查点 |
| `README.md` | 覆盖描述、断言总数、fixture 陷阱 |

## 3. 构建与缓存

```bash
./.conda/python.exe tools/official_event_check.py            # 改了事件表
rm data/Character_Talk.json && ./.conda/python.exe buildconfig.py   # 改了口上（README：否则断言读到旧生成物）
./.conda/python.exe tools/tests/education/run_all.py         # 测试引导的增量构建会重建事件表
git diff --stat
git checkout -- data/po/                                     # 本机无 gettext，构建会写乱 PO
```

- 改了口上与前提名，需要一次全量 `buildconfig.py`；事件表由测试引导的增量构建重建

## 4. 验证清单

### 4.1 单元测试（实施方执行，按 `headless-game-test` 模式 A）

- [x] §2.0 两份复现：改前全部成立；改后按 §2.0 的「改后」列核对
- [x] `tools/official_event_check.py` 通过
- [x] §2.11 各文件新增断言通过
- [x] `run_all.py` 全部文件 PASS，断言数记入 §6.3

### 4.2 行为循环（实施方执行，按 `headless-game-test` 模式 B）

- [x] `test_behavior_loop` 收敛；上午四节人均出勤 ≥ 3 节不变
- [x] 另跑一次玩家一步 60 分钟、教师换教室的课表（照 §2.0 R1），第 2 节结算一次、第 3 节不重复（`test_class_ai` 的 H1 行为循环，两种处理顺序都跑）

### 4.3 游戏内整体测试（由用户执行）

- [ ] 一键排课后让博士「处理公务」60 分钟：换教室的教师晚到的那一节，学生照记出勤
- [ ] 对成年学生施加心控后站在实践教室反复打开指令面板：理智不再下降
- [ ] 对教师施加木头人：她的学生这一节去自习
- [ ] 女儿成年：公务队列里依次出现毕业典礼、成年纪念、通用 59 / 60
- [ ] 女儿翘课的当天：她不再走到教室门口再掉头；睡过午夜到 10 点后，她次日照常上课
- [ ] 提前几分钟开讲预约的实操课：上一节缺过课的学生照记出勤
- [ ] Tk 与 Web 两种模式下面板无报错

## 5. 回滚

| 单元 | 内容 | 回滚方式 | 备注 |
| --- | --- | --- | --- |
| 主代理先改 | §2.1 | `git revert` | 两个新字段留在旧档里无害 |
| U1~U7 | §2.2~§2.8 | `git revert` | 无存档影响 |
| U8 | §2.9 | `git revert` 后重建事件表与口上 | 删掉的口上文件随 revert 恢复 |

## 6. 实施过程记录

### 6.1 实际改动

| 文件 | 改动 |
| --- | --- |
| `Script/Core/game_type.py` | `CHILD_GROWTH` 加 `skip_class_day`、`sex_class_count` |
| `Script/Core/constant_promise.py` | 6 个新前提名；同学前提 docstring |
| `Script/System/Education_System/education_constant.py` | `GROWTH_VALUE_SEX_CLASS`、`ADULT_EXTRA_EVENT_UID_LIST`、`FALLBACK_SUBJECT_ABILITY`（偏离 12） |
| `Script/System/Education_System/growth_handle.py` | `get_growth_value` 读 25；`judge_have_course_type` |
| `Script/System/Education_System/class_ai.py` | `judge_skip_class_today`、`judge_teacher_available(…, classroom)`（木头人显式判，偏离 1）；`get_course_stage` / `judge_student_pullable` / `judge_student_join_class` / `get_student_leave_time`（偏离 3） |
| `Script/Settle/default.py` | 557 按教师能到岗结算（另两道防护，偏离 2）；549 写 `skip_class_day`；512 / 548 的回落改用共用定义（偏离 12） |
| `Script/Design/second_behavior.py` | 623 的触发改判 `judge_skip_class_today` |
| `Script/Design/instuct_judege.py` | `calculation_instuct_judege` 加 `settle_hypnosis` |
| `Script/System/Education_System/sex_class_handle.py` | 门槛传 `settle_hypnosis=False`；`get_attend_judge_time`；`settle_attend` 按那一节判缺课、记 `sex_class_count` |
| `Script/System/Education_System/schedule_handle.py` | `get_course_at` 收窄；`judge_schedule_teacher` 与两个教师反查；`get_course_type_by_position`（偏离 12）；docstring |
| `Script/System/Education_System/growth_event_handle.py` | 成年结算推通用 59 / 60（不受容量约束，偏离 9）；同学只取幼女 / 萝莉；期末推送注释 |
| `Script/System/Official_Event_System/official_event_handle.py` | `push_official_event` 加 `ignore_capacity`（偏离 9） |
| `Script/Design/handle_premise/__init__.py` | `get_player_manual_teach_course`；CVP `CourseType` / `Course` 对玩家手动授课的回落 |
| `Script/Design/handle_premise/handle_premise_work.py` | 教师能到岗的两个前提传本节教室 |
| `Script/Design/handle_premise/handle_premise_other.py` | 6 个新前提（生日前提挡缺省出生日，偏离 7）；同学前提 docstring |
| `Script/UI/Panel/character_info_head.py` | `<翘>` 改判 `judge_skip_class_today` |
| `Script/System/Education_System/growth_panel.py` | 翘课标记改判 `judge_skip_class_today`（按游戏时间，偏离 6） |
| `Script/System/Education_System/class_schedule_panel.py` | `get_teacher_absent_mark`、`fit_text_width`；周表离岗 / 离岛标注（偏离 4、13）；排实操课页按门槛分行（偏离 5）；选科目页标注 |
| `Script/System/Education_System/course_select_panel.py` | 选课页离岗 / 离岛标注 |
| `data/official_event/` 萝莉 / 幼女 / 通用 / 婴儿 | 方案 §4.3 的 14 条事件（萝莉 1 / 20 / 26 另加 `CVP_A1_Growth\|7_NE_3`，偏离 11） |
| `data/talk/` 6 个口上文件 | 实操课到场 / 旁观读 `Growth\|25`、翘课 1004、检查成绩单 1004 / 1005 与新增 1014~1017、授课 / 听课删占位行 |
| `data/talk/system/second_show_off_study/show_off_waist_skill.csv` | 删除（52 条死口上） |
| `tools/ArkEditor/csv/Premise.csv` | 3 行补全、6 行新前提 |
| `tools/official_event_check.py` | 期末桶禁 9 / 23、未成年与宿舍规则并入 200、成年桶只收显式推入的 uid、docstring 归位 |
| `buildata.py` | `build_promise_csv_text`（偏离 8）、按第一个空格切一刀 |
| `tools/tests/education/` 10 个测试文件与 `README.md` | 见 §6.3；README 覆盖描述、断言总数、夹具陷阱 4 条 |
| `.github/skills/text_generation_for_instruction_code_generation/学习前提/性技科目对照表.md` | 腰技不写炫耀二段 |
| 说明文档、设计文档索引、Plan 22 总纲 §17、`update.log` | 方案 §3.17 |

与方案的偏离：

1. **M3 的木头人要显式判**（方案 §3.4 已同步）：主代理先改 `judge_teacher_available` 时复核发现，无意识 6（体控）本就不在 normal 5 / 6 里，Plan 25 对它的豁免从未起作用；照方案初稿「取消体控豁免」挡不住木头人，改为显式判 `hypnosis.blockhead`。空气催眠一条照方案
2. **557 多两道防护**（U2）：学生须在本节的教室里（被玩家拉到别处听课的由玩家的广播结算）；课表教师为 -1（自习）或 0（玩家的临时实操课）不走 557。前者补回原条件「教师在同一教室」里隐含的约束，后者保留原注释「临时实操课是课堂 H，不是授课」的口径
3. **翘课日的规则 B 不看地点**（U1）：人已在上课地点、离开那一刻本节还有课，也照样截到开课那一刻，她要在那一刻当场判翘课；上一节也翘着时重新判出的仍是翘课，结果与不截一致
4. **周表格子用短标注**（U6，方案 §3.10 已同步）：一格 25 列放不下全称，写「（离岗）」「（离岛）」、悬停提示写全称；两种都成立时标「已离岗」；选科目页的「每周课表这一格」同样标注
5. **排实操课页一个都进不了课堂时改写第一行**（U6）：「本节选修本教室的学生：0 人 —— 选修的人都进不了课堂（见下）」，免得与下一行「另有 N 人会到场」矛盾
6. **养成总览的翘课标记按游戏时间判日期**（U6）：面板上的「今天」是玩家看面板的这一天，不取学生行为的开始时刻
7. **生日前提挡缺省出生日**（U5）：`born_time` 还是公元 1 年的（不是在岛上出生的）判不成立，否则这类角色每年 1 月 1 日都算过生日
8. **`buildata` 的前提表生成抽成纯函数**（U8）：`build_promise_csv_text`，测试用 ast 取出执行、不写 `Premise.csv`；docstring 没有空格时描述写空串、不再抛异常。mode 2 的行为不变
9. **通用 59 / 60 不受队列容量约束**（主代理，方案 §3.2 已同步）：U7 照方案走普通入队，并报告队列满时两条会永远丢掉；`push_official_event` 加 `ignore_capacity`，与毕业典礼、成年纪念同理
10. **H1 的行为循环测试只让师生两人参加**（U1）：按给定顺序处理教师 101、学生 201，两种顺序都跑；夹具里别的角色与本题无关，按集合顺序也定不下处理顺序
11. **萝莉 1 / 20 / 26 再排除档位 3**（整体复审第 2 条，方案 §3.14 / §4.3 已同步）：只加「有待查看的新成绩单」时，整学期没有上课的萝莉拿到档位 3 的成绩单，也抽得到这三条写各科成绩的事件；三条都加 `CVP_A1_Growth\|7_NE_3`
12. **玩家手动授课的回落收拢成共用定义**（整体复审第 3 条，方案 §3.13 / §4 已同步）：`education_constant.FALLBACK_SUBJECT_ABILITY`（学识）与 `schedule_handle.get_course_type_by_position`，512、548 与 CVP 的回落共用；此前 45 与按教室判课型的几行各写一份，改一处就会分叉
13. **周表格子先截名字、再拼标注**（整体复审第 4 条，方案 §3.10 / §4.2 已同步）：`class_schedule_panel.fit_text_width`；异格干员这类五六个字的名字不再把「（离岗）」「（离岛）」挤掉

整体复审报了 4 条（M 1 条、L 3 条），全部采纳：第 1 条（通用 59 / 60 在队列满时丢失）主代理在复审交卷前已改，即偏离 9；其余三条为偏离 11~13。

### 6.2 实施前的假设复核

| # | 方案中的事实 | 出处 | 复核结果 |
| --- | --- | --- | --- |
| 1 | 定案到实施之间代码没动过 | `git log -1` = `44ed83f15` | 成立 |
| 2 | `CHILD_GROWTH` 的新字段靠属性表整体回填，不需要迁移 | `save_handle.py:396~401` | 成立（`test_save_compat` 断言两个新字段补默认值） |
| 3 | 取消无意识 5 / 6 的豁免就能挡住木头人 | `handle_premise/__init__.py:1126~1168`；`class_ai.py:102~107` | 不成立：无意识 6 / 7 都不在 normal 5 / 6 里，木头人照样过这道判断；改为显式判 `hypnosis.blockhead`（偏离 1） |
| 4 | `start_sex_class` 先置 running 再记出勤，`settle_attend` 里取得到正在进行的那节课 | `sex_class_handle.py:746~760` | 成立 |
| 5 | 两个教师可用性前提拿得到本节的教室名 | `handle_premise_work.py:643~646`、`:663~666` | 成立（`now_course["classroom"]`） |
| 6 | 通用 59 / 60 推到队尾就能出现 | `official_event_handle.py:348~376` | 不完全成立：队列已满时普通入队被挡，成年桶又没有别的入口，会永远丢掉；改为不受容量约束（偏离 9） |

### 6.3 单元测试结果

复现脚本（scratchpad `p31/`，不入库）：改前 40 + 121 项全部成立；改后（`REPRO_PHASE=after`）两份都「改后全部符合预期」：
- `repro_main.py` 40 项：成立 20、不成立 20。问题命中 19 项只剩随口径的 R4-2 成立（方案选了成年结算推入，日常派发照旧没有 59 / 60，R4-3 翻转）；前提对照 18 项成立 16（R7-1 描述的是改前的截短规则 B、R9-0 改后派 713，都按预期不再成立）；数据事实 3 项照旧
- `repro_plan31.py` 121 项：成立 58、不成立 63。问题命中 59 项成立 6：标「照旧」的 R4-4、R11-1、R15-1、R21-1（方案 §7 / §2.3 / §3.10 不改），与随口径的 R2-3（日常派发照旧没有 59 / 60，改由成年结算推入，R2-4 翻转）、R22-1（离线时 flag 照旧没被清，但认了日期、读作不是今天）；前提对照 50 项成立 44、数据事实 11 项成立 7，不成立的都是描述改前机理或标随口径的项
- 第一次改后核对有 3 + 17 项与预期不符，逐项看过都是脚本的问题，修了脚本再跑（改前的结论不受影响）：
  - 夹具只挂翘课 flag、没写 `skip_class_day`（main R6~R8，代理 R4 / R15 / R19 / R22 / R24）：549 现在同时写日期，只挂 flag 在新口径下读作前一天的残留，翘课日的新路径一条都没走到；补写日期后按新路径核对
  - 检查的写法：main R3 判能到岗补传本节教室；R3-5 / R10 在占位行与旧前提改掉后按前提串找口上，取到空列表、空集恒真，改按口上 cid 取；R23 改画真实的排实操课页（原为复刻改前面板的筛法）；R25 改跑 buildata 里真实的生成函数（原为复刻改前的切法）；R26 按内容而不是行号读文档；R22-3 改经 AI 派发（原为直接调 714，714 本身恒记翘课）
  - 5 项改后预期标错：R2-3、R22-1 改为随口径（理由见上）；R19-2、R24-0、R24-1 描述的正是改前的截短规则 B，改为不再成立（同 main R7-1）

| 文件 | 改前 | 改后 | 新增覆盖 |
| --- | --- | --- | --- |
| `test_class_ai` | 269 | 315 | M3 教师可用性、`judge_skip_class_today`、翘课日的 UPCOMING 与截短规则 B、303 不倒拉与 normal 门槛、H1 行为循环（两种处理顺序与每步 10 分钟对照） |
| `test_growth` | 94 | 100 | 养成数值 25、`judge_have_course_type` |
| `test_growth_event` | 63 | 97 | 同学只取幼女 / 萝莉、成年结算推 59 / 60（含队列已满）、Q4 各事件的候选（课型、成绩单与档位 3、本学期出勤、生日、季月交替、断奶） |
| `test_panels` | 92 | 107 | 翘课标记认日期、排实操课页按门槛分行、离岗 / 离岛标注（短写、宽度、长名字、选课页） |
| `test_premise_tokens` | 133 | 169 | 六个新前提、教师能到岗前提传教室、`<课>` / `<翘>`、前教师改当学生的 CVP、玩家手动授课的 CVP 回落 |
| `test_save_compat` | 13 | 14 | 两个新字段回填 |
| `test_schedule` | 81 | 96 | `get_course_at` 只对学生岗、教师反查只认教师岗、`get_now_course` 的说明 |
| `test_settle_effects` | 87 | 96 | 557 按教师能到岗结算与各排除情形、549 记日期、前一天的 flag 不触发 623 |
| `test_sex_class` | 92 | 108 | M1 门槛只判不扣、L3 提前开讲按那一节判缺课、L12 实操课次数 |
| `test_talk_data` | 60 | 114 | 炫耀 17 门与男性专属科目、事件前提逐条与 token、校验工具新规则、实操课 / 翘课 / 检查成绩单口上、占位行删除、`Premise.csv` 与 buildata 生成器 |
| 其余 5 个 | 222 | 222 | —（`test_behavior_loop` 18 条：六轮收敛、上午四节人均出勤 ≥ 3、教师在对的教室授课） |
| **合计** | **1206** | **1438** | |

`tools/official_event_check.py`：校验通过，5 个文件共 266 条事件。构建写乱的 `data/po/` 已 `git checkout` 还原；`config_def.py` 与其它生成物不在 git 追踪的改动里。

### 6.4 尚未覆盖的验证

- 实施文档 §4.3 的游戏内整体测试（换教室晚到的一节、心控学生与指令面板、木头人教师、成年后的公务队列、翘课日、提前开讲的实操课、Tk 与 Web 两种模式）留给用户
- PO / MO 未重建（本机无 gettext）：本轮新增的 `_()` 文案——实行值计算的「+催眠(+{0},需{1}理智)」「+催眠(+0,理智不足)」，课表面板的「（已离岗）」「（不在岛上）」「（离岗）」「（离岛）」、悬停提示「{0}{1}：她来不了……」，排实操课页的「另有 {0} 人会到场……」「本节选修本教室的学生：0 人 —— 选修的人都进不了课堂……」——要在装有 gettext 的机器上跑 `buildpo.py` / `buildmo.py`
- 档位 3 的成绩单看过之后再检查不出口上（方案 §6），没有另写专属口上

### 6.5 追加调整实施记录

（与方案 §8 成对，每轮一节，附回归测试计数。暂无）
