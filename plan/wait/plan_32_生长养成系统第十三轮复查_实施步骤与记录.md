# Plan 32（实施步骤与记录）：生长养成系统第十三轮复查

> 本文件是 `plan_32_生长养成系统第十三轮复查_方案.md`（下文简称"方案"）的**实施步骤清单与过程记录**。
> 需求背景、发现、设计决策、接口定义、风险与范围外事项一律以方案为准；
> 本文件只写"怎么做、怎么验、怎么回滚"，实施过程与结果记入 §6。

- 状态：实施中（2026-09-14 用户指示「开始按方案实施」，Q1~Q3 均按推荐）
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
按 §2.2~§2.10 的步骤分组合并成 5 个单元：代理数 = 2 × 5 + 1 + 3 = 14，在本会话「单个 Workflow 15 个代理以内」的规模里（按原先 9 个单元要 22 个）。

| 单元 | 标题 | 步骤 | 文件 | 测试 |
| --- | --- | --- | --- | --- |
| 主代理先改 | 共用常量、前提、时钟与手动授课判据 | §2.1 | `education_constant.py`、`constant_promise.py`、`game_time.py`、`game_type.py`（只动说明）、`handle_premise_other.py`、`handle_premise/__init__.py`（只加 `get_listen_manual_teach_course`）、`tools/ArkEditor/csv/Premise.csv` | — |
| U1 | 课堂收尾与课堂计数 | §2.2 | `sex_class_handle.py`、`realtime_settle.py`、`Settle/default.py`、`handle_premise_H.py`、`group_sex_panel.py`、`constant_effect.py`、`InstructConfig.csv`、`tools/ArkEditor/csv/Effect.csv` | `test_sex_class.py`、`test_settle_effects.py` |
| U2 | 上课状态、见学、截短与行为循环 | §2.3、§2.4 | `class_ai.py`、`handle_premise_work.py`、`character_behavior.py`、`handle_npc_ai.py` | `test_class_ai.py`、`test_behavior_loop.py` |
| U3 | 阶段进度、性格、养成事件与跨天 | §2.5、§2.6 | `growth_handle.py`、`growth_event_handle.py`、`pregnancy_handle.py`、`past_day_settle.py` | `test_growth.py`、`test_growth_event.py`、`test_prenatal_baby.py` |
| U4 | 状态标识、面板、前提、二段与日程模板 | §2.7、§2.8、§2.9 | `character_info_head.py`、`class_schedule_panel.py`、`schedule_handle.py`、`course_select_panel.py`、`growth_panel.py`、`schedule_template_panel.py`、`handle_premise/__init__.py`（CVP 两函数）、`second_behavior.py`、`handle_ability.py`、`schedule_template_handle.py` | `test_panels.py`、`test_schedule.py`、`test_premise_tokens.py`、`test_schedule_template.py` |
| U5 | 数据与口上 | §2.10 | `data/official_event/` 4 张表、`data/talk/` 3 个文件、`target.csv` | `test_talk_data.py` |

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

   **复现代理脚本 `repro_plan32.py`**（组号是代理的编号；「对应」列是方案编号）

   运行：改前在 `p32/head`（HEAD 的干净副本；代理跑时工作区已有主代理共用文件的改动）里执行 `timeout 600 C:/code/erArk/.conda/python.exe -u ../repro_plan32.py`；改后在仓库根目录 `REPRO_PHASE=after` 跑同一份脚本。各组在同目录的 `part1.py~part8.py`，由主脚本 exec，`REPRO_PARTS=part1.py,part4.py` 可只跑其中几块。夹具另补：罗德岛派对表、监禁调教设置、岗位在岗名单的默认值；`update.game_update_flow` 换成空函数、心情翘课率设为 0（R21 另行打桩）。

   | 组 | 对应 | 问题命中（改后不再成立，除非另注） | 其余 |
   | --- | --- | --- | --- |
   | R1 | H1 | 收尾后课堂模式仍开、仍 running、5209 开不了、跨天不清；次日判 JOIN、722 拉进 H 并各 +1、同一节再 JOIN 再 +1；无关干员主修加成；带护栏循环 60 遍不收敛、一步里 722 派 30 次；R1-1 两条效果串没有 10015（**随口径**：修法不改效果串） | 模式前提、开课、体力归零走 373、效果串照常结算、END_H 倒回开始时刻、`handle_npc_ai.py:481~482` 把时长 0 改 1、10015 对照 |
   | R2 | M5 | 整链派见学、母亲睡着回落自由玩耍；R2-0 覆盖照写进槽位（**改后照旧**：日程照写，只是工作时间不见学） | 她有工作、周一 10:00、对照派工作链 |
   | R3 | M4 | 撞号的教师判来不了、学生侧降级自习、撞号的母亲判住院 | 没人住院时能到岗、病人编号的来源、真实收治路径 |
   | R4 | M1 | 83 / 122 个出生日没有婴儿中期、26 个没有萝莉 3_GE_70、117 个婴儿 4 / 50 同日；9/7 出生的例子、中期 9 条抽不到、4 / 50 都在 12/1 首次进候选 | 季月交替跳 59~63 天、9/30 的下一天是 12/1 |
   | R5 | M2 | R5-3 通用 3 占候选 1.84%（**随口径**：随机派发的份额不变，改由生日当天推入保证） | 童年只有一天生日、真实时钟下只 9/7 成立（随口径）、当天前提成立 |
   | R6 / R18 | L13 | 学生侧 CVP 读 43 / 0、听课口上候选是料理、`<课>` 写教师甲、512 发学识；节次外 CVP −1、节次内读 42 | 复刻 handle_teach、512 调 `judge_character_status`、已结算的学生 continue |
   | R7 / R20 | L6 | 512 给她出勤 +1、标记变 [d, p+1]、发第 p 节收益、再结算听课（体力 100 → 1）、开课再 +1 | 303 不倒拉、第 p+1 节普通课的对照 |
   | R8 | L16 | 长大后婴儿 5 仍在队列、抬头写幼女期、照样弹出；成年后萝莉 3 夹在通用 2 与 59 之间、抬头写少女期 | 入队、`judge_stage_pass` 为 False |
   | R9 / R15 / R19 / R28 / R43 / R44 | L27 | §13 条数、§12 的 557、§8 的 17 条；`CHILD_GROWTH` 两处说明；两处 :407 / :410 与 :3627；翘课日口径的 7 处说明；557 的 7 处说明；README 反斜杠。R15-1~3（成年学生岗记出勤 / 缺课、无胎教不创建）**改后照旧**：是说明要改的依据，行为不变 | 四个目录 522 / 529 / 468 / 405、prenatal 10 条（文档写对）、实际行号 415 / 418 / 3665、翘课日 13:45 判 NONE、557 代码不看教师位置 |
   | R10 | M1 | R10-3 117 / 122 同日进池；R10-2 婴儿 50 有效权重大于 4（**改后照旧**：权重不改） | 权重与窗口、进度 60% 两条同在 |
   | R11 | L22 | 日常候选同时有萝莉 1 / 20 / 26（改后三条挪进期末，按新 uid 核对） | 成绩单与期末事件、13 / 16 条期末写成绩单、查看后三条都不在（随口径） |
   | R12 | L23 | 萝莉候选里有通用 15；通用 27 对萝莉恒成立（随口径，按推荐不再成立） | 前提与正文、季末进度 96.6 |
   | R13 | L25 | 成年女儿的检查成绩单口上候选为空 | 1036 前提、两组口上的前提、萝莉对照 |
   | R14 | L24 | 幼女第一次到场上午 / 下午抽中 3.17%、萝莉旁观老学生行 3.1% | 权重组 {1:2, 2:7, 15:1} |
   | R16 | L4 | 一步 60 分钟累计 95 分钟 | 截到 9:25、不截短时 60 分钟 |
   | R17 | L20 | 厨师岗萝莉 show_off 含 43、见面派炫耀 | 料理升级、1003 写「老师问我」 |
   | R21 | L5 | 新一天的 flag 被清、第 4 节 SKIP → ATTEND、不再触发 623 | flag 为真的前提、跨天在 NPC 阶段之后 |
   | R22 | 方案 §7 | 母亲先离场时见学整段跳过（**改后照旧**：见学对象规则属行为循环主干，本轮不改） | 截到 9:25、母亲不动的对照 |
   | R23 | L10 | R23-3 同一节两种结果；R23-1 开课前到零收益（随口径，按推荐不再成立）；R23-2 开课后到自习记出勤（随口径，照旧） | 覆盖层教师 0 |
   | R24 | L3 | 在上课地点不截；9:00 → 11:00 出勤、缺课都不变 | 兴趣课 55、不在地点截到 9:25 |
   | R25 | L21 | 缺位标注为空、候选名单有她、一键排课给她排 45 格 | 监禁后仍在岛在岗、判来不了 |
   | R26 | L12 | 必修生落在「不能参加」行 | 面板推导不看必修（随口径）、开课时豁免 |
   | R27 / R29 / R30 | L28 | 无用 `window_width` / `normal_config` 与重复导入；`BASE[0]`、`week_day == 6`；模板键半用半不用、5 个常量不在 `education_constant` | — |
   | R31 | L17 | 离岛时套用人数 0、删除后复用 5 号她仍指着、取到新模板时段 | 注释断言（随口径） |
   | R32 | L18 | 晚上照写读书；R32-0 不在两份名单里（**改后照旧**：名单不变，只是模板不再生效） | 预设删不掉、学生岗专用时段跳过 |
   | R33 | L8 | 重开前名单不含她、10014 拉她进 H、这次不记出勤与实操课 | 第一次开课、下课后 ended |
   | R34 | L7 | 体力 20% 判 ABSENT_HP、721 再记缺课 | 开课记出勤、下课后交还课表 |
   | R35 | L9 | 理智跌破后仍在 H，却被踢出旁观与在课 | 理智够时过门槛、入课后在名单里 |
   | R36 | M2 | R36-1 三天后出队时生日前提已不成立、R36-2 选项照常结算（**随口径**：正文改为不写「今天」，出队不复核照旧） | 生日当天入队、出队链不读 add_time（随口径） |
   | R37 | L19 | R37-2 当天娱乐不在幼女默认池；R37-0 源码顺序（**改后照旧**：顺序不变，换完素质后另刷一次） | 已长成幼女、换完再刷全在默认池 |
   | R38 / R39 | L11 | 课堂模式下手交经验 1 → 2；可选名单含非学生且不置灰 | 模板动作对非 H 角色照样结算、她过不了门槛、源码只调 `judge_hp_low_only_watch`（随口径） |
   | R40 | L14 | 缺课休息时 `<课>` 显示体育课 | ABSENT_HP、721 记缺课并 REST |
   | R41 | L1 | 没课的节次、必修实操课那一节 `<翘>` 仍亮 | — |
   | R42 | L15 | 悬停写「经验减半」 | 经验比 1/3、1/5、1 |
   | R45 | L29 | `CLASS_SM_SET` 缺 722 | 220835 派 722 |

   改前 196 项全部成立：110 项问题命中，61 项前提对照，18 项数据事实，7 项随口径（主代理在 `p32/head` 上重跑结果相同）。
   - 代理登记的改后预期有十余项与本方案的修法不符，上表已按修法改注（R1-1、R2-0、R5-3、R10-2、R15-1~3、R22、R32-0、R36-1~2、R37-0），改后核对以上表为准
   - 共用文件先改之后，R15-0、R19-2、R28-1~2、R43-3 在工作区已翻为不成立（说明与常量已按方案改好），属改后预期
   - 代理脚本没有单独的组：M3（见 `repro_main.py` R1）、L2（`repro_main.py` R4）、L26（读数据核实）

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
   - 婴儿 5 入队后长成幼女：队列里不再有它；成年那一刻残留的萝莉桶与通用桶事件都被清、期末桶照留、毕业典礼照在队首
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

1. **L1 `<翘>` 与 SKIP 同口径**（U4）：用 `get_course_stage == COURSE_STAGE_SKIP` 加「不在 H」判，比方案原列的三条多挡体力缺课、待赴 / 加入实操课两种情形（前者与「体力缺课」的记录不符，后者与 L2 不派被抓相反）；「翘课中（第N节）」一支删掉。方案 §3.9 已同步
2. **L12 选修都被点了名时的第一行**（U4）：去掉必修生后选修名单为空、而必修名单非空时，写「本节选修本教室的学生：0 人（点名必修的学生照常会来，见下）」，不再落到「没有学生会来」。方案 §3.8 已同步
3. **L2 不派被抓时也不转去判炫耀**（U4）：保持「今天翘过课的孩子当天不先炫耀」，待炫耀留到下次见面。方案 §3.10 已同步
4. **H1 的单元测试只结算与 H 状态相关的效果**（U1）：407 / 404 / 10011 之后调 `realtime_settle.judge_pl_real_time_data` 代表「玩家这一步走完」，并用数据断言锁定 371 / 373 / 375 / 362 各效果串的组成；整条效果链与玩家分支的覆盖由 `repro_c1.py` 与回归承担（实施代理不能跑测试，529 / 636 / 800 等在夹具里要的数据无法当场验证）
5. **`clean_expired_temp_class` 的写法**（U1）：先调 `settle_orphan_class`，再以「课堂模式是否仍开着」决定 running 条目的去留；返回值改为清理前后的条目数之差（含收尾时删掉的当场课）。与方案等价，今天日期的幽灵课堂也能收掉。方案 §4.2 已同步
6. **L22 挪进期末的三条配置权重取 2**（U5 定 4，实施复审改 2）：期末池按「配置权重 × 前提条数」抽，沿用原来的 15 / 9 / 10 会得 45 / 27 / 30 分，远超其余期末事件的 4~8 分；取 4 时一条 12 分、三条合计约占萝莉期末池一半，取 2 得 6 分，与其余期末事件同一档。方案 §3.14 已同步
7. **校验工具的萝莉条数下限 70 → 67**（主代理，U5 提出）：萝莉桶删了 3 行，`--full` 模式会报条数不足；`test_talk_data` 只跑 `--quiet`，不受影响。方案 §3.14 已同步
8. **口上改动后全量重建**（主代理，U5 提出）：回归代理只跑增量构建，`data/Character_Talk.json` 存在时不重建口上；join / watch / 检查成绩单三个口上文件改了，先删它再跑 `buildconfig.py`，随后 `git checkout -- data/po/`
9. **未改**：`save_handle._migrate_child_schedule_template` 里读模板时段仍写字面量 `"slot"`（U4 提出可选）：迁移代码读的是旧档写下的键，不随常量改名
10. **M4 母亲一侧的注释不写 normal_2**（U2）：`judge_mother_available` 本身不查 normal_2，「干员真正住院的临盆 / 产后已由 normal_2 挡住」只对教师成立；被删的住院判定从来命中不了角色，母亲临盆 / 产后时的实际行为不变。要不要给母亲补 normal_2（会连带让公务事件前提 `self_mother_available` 在产后期不成立）属设计决定，列入方案 §7
11. **行为循环测试的跨天段**（U2）：调 `update_new_day` 之前把在学女儿身上挂着的翘课 flag 统一改成前一天挂上的，断言名改为「跨天后翘课（前一天挂上的）与见学 flag 都清了」：U3 的 L5 改为跨天只清过期的 flag，存档当天真有女儿翘课时原断言会随存档而变
12. **两个辅助函数**（U3）：`growth_handle.get_grow_day_time`（阈值换算回日历时刻，阶段天数与进度共用）、`settle_adult_personality_pair`（成年女儿才重选，改写倾向的两个函数共用）。方案 §3.2、§3.4、§4.2 已同步
13. **没有可认出生日的角色**（U3）：`born_time` 还是缺省公元 1 年的，本阶段天数 0、进度 100（此前本阶段天数是两千多年的日历天，进度被夹到 100）。方案 §3.2 已同步
14. **生日事件另过阶段判定、双胞胎按 id 排队首**（U3）。方案 §3.3 已同步
15. **L16 与 M3 叠加**（U3）：成年结算先清残留的萝莉桶与通用桶事件，「成年前入队、成年后才处理」只剩旧档残留；`repro_main.py` R1-6 直接调成年结算的两个函数、不走 `check_grow_to_girl`，照旧成立。方案 §3.4 已同步，实施文档 §2.6 的检查点改为「萝莉桶与通用桶都清」
16. **`test_growth_event` 的 Plan 31 L10 段**（主代理，U5 提出）：萝莉 1 / 20 / 26 已从事件表删去，原「三条都进候选」一条改为：原 uid 已删、它们与期末 17 / 18 / 19 在各种成绩单状态下都不在日常候选里
17. **实施复审补**（U4 单元复审提出，主代理修）：
   - `test_growth.py` 的改岗段把女儿岗位改成 0 后没换回，L20（待炫耀只记学生岗）让下一段「升了级的科目记进待炫耀」必挂：换岗断言之后改回学生岗，断言名写明「学生岗的萝莉女儿」
   - L12 把必修生从三份选修名单去掉后，「此刻进不了课堂」一行也不再看她们；点名只豁免前置修习，必修生按 `judge_can_join_sex_class(cid, check_course=False)` 补列进这一行（点名之后被监禁、意识模糊或实行值跌破的）。方案 §3.8 已同步
   - L14 的个人式课分支补判 `is_h`：L1 让 `<翘>` 对在 H 里的人不亮，这里不挡，她在上课地点被带进 H 时就改亮 `<课>`。方案 §3.9 已同步
   - `character_info_head.py` 听课而此刻没课一支的注释与 `test_premise_tokens.py` 对应的断言名：L13 之后被拉来听玩家授课的走上面的新分支，这一支只剩「被拉来后玩家已换了行为」等情形
   - 补测试：`test_panels` 两条（被监禁的必修生列进「此刻进不了课堂」；在体育课地点的 H 里不亮 `<课>`）
18. **实施复审补（U5）**：
   - `test_growth_event` 的 Plan 31 L13 段拿萝莉 211 判「通用 15 进候选」，L23 之后必挂：正反两向改用幼女 212，另加萝莉判不过的断言
   - 期末 17 / 18 / 19 配置权重 4 → 2（偏离 6 随之改写）；萝莉 51 的公开课前提改为替换 `self_have_any_course`（与幼女 24 一致）。通用 5 的 `CVP_A1_T|101_E_0` 试过去掉，`test_growth_event` 的 Plan 26「17 条都带排除婴儿的前提」锁着这条约定，照留
   - 旧档履历迁移：`save_handle._OFFICIAL_EVENT_UID_MIGRATE` 与 `_migrate_official_event_history`，孩子的 `event_history` 与罗德岛的 `official_event_history`（键为「uid@角色id」）读档时把萝莉 1 / 20 / 26 改名为期末 17 / 18 / 19（旧 uid 已不在配置、新键还没有记录时才改，重复读档幂等）；`test_save_compat` 5 条
   - `test_talk_data` 期末桶条数的旧断言由 16 改为 19
19. **实施复审补（U1）**：
   - L9 的旁观名单另判状态那一层：从 `judge_can_join_sex_class` 抽出 `sex_class_handle.judge_sex_class_state_ok`（normal 2 / 5 / 6 / 7 与监禁），`get_watcher_list` 过它，成员名单照旧按身份认。时停中被冻结、醉酒、半梦半醒的学生不再拿观摩收益与旁观口上；`test_sex_class` 3 条（时停开 / 关）
   - H1 补一条走真实调用链的断言：最后一名学生力竭退出（`commit_group_sex_tired_exit` → `handle_group_sex_end`，`update.game_update_flow` 桩成玩家这一步）→ 同一步下课。NPC 阶段在第 1 层 `game_update_flow` 里，嵌套进来的是第 2 层、照常执行（第 3 层才拒绝）
   - 注释：`settle_orphan_class` 写明两类例外（意外中断 H 的二次确认只清玩家与对象；转隐奸 1 / 2 清玩家的 H），`settle_sex_class_notify` 与 `past_day_settle` 调 `clean_expired_temp_class` 处的注释随 H1 改写
20. **实施复审补（U2）**：
   - L7 跨单元整链：开课记出勤（按 `get_attend_judge_time` 那一节写标记）→ 本节内下课 → `settle_absent`（721 调它）按她所在的节次读；按时开讲、提前 5 分钟开讲各一条，外加下一节照记缺课的对照；`test_sex_class` 3 条
   - `judge_interrupt_character_behavior` / `judge_student_leave_truncate` 的 docstring、`system-review-find.js` 与复查清单补上「工作 / 娱乐中到了淋浴时间」这一打断分支；`E1_BUG与漏洞检查.md` 的过期行号改为引用函数名，`P0_建档与基线.md` 的挂接点补 `judge_student_leave_truncate`
   - L10 扩了语义的两条前提（`self_course_teacher_available` / `unavailable`）在 `constant_promise` 与 `Premise.csv` 的说明补上临时实操课的情形
21. **实施复审补（U3）**：`settle_personality_pair` 的 docstring 里「方案 §3.8」改为「Plan 22 二期 §3.8」

**中期提交（2026-09-14，用户要求先暂停）时尚未处理的事项，下次从这里接着做**（提交时 `run_all.py` 15 个文件、断言 1693 条全部通过，改前基线 1438；`official_event_check.py` 通过；`update.log` 已追加本轮已实施的条目）：

1. U3 复审（M）：`drop_stale_stage_event` 只按 sub_key 桶判阶段，前提里的阶段素质记号（`CVP_A1_T|101~104_E_0/1`）长大时不重判——L23 之后幼女期入队的通用 6 / 15 / 27 长成萝莉照弹，期末 2 / 6 / 12（幼女）、3 / 7 / 10 / 17 / 18 / 19（萝莉）长大后照弹。拟按复审建议改：新增常量 `education_constant.STAGE_TALENT_PREMISE_SET`，`growth_event_handle.judge_stage_marker_pass(uid, character_id)` 用 `official_event_handle.judge_premise_pass` 只判这些记号；`drop_stale_stage_event` 对 sub_key 0 / 101~103 再加判记号，对期末桶（200）只判记号（`judge_stage_pass` 对 200 恒不成立，不能套用），成年桶（104）不动。同步 docstring、方案 §3.11、说明文档 §8，以及 `test_growth_event` 的 L16 两段：期末事件改用前提不写阶段的一条（期末 1），幼女→萝莉时通用 27 应被清掉、改用通用 16（前提为空）验「通用桶照留」；每孩队列容量 4，推毕业典礼要 `ignore_capacity=True` 或少推一条
2. 方案文字：§3.2 与 §6 风险表写「养成总览的阶段进度同源」，与实际不符（`growth_panel._draw_stage` 写的是「距成长为X还有 N 天（日历天）」与预计日期，按有效成长天数），实施文档 §4.3 游戏内测试第 3 条随之改写；§3.3 补「生日当天离岛（外勤、外交）的幼女 / 萝莉不推，一生仅此一次，属已知取舍」；§3.5 的理由只对教师成立（`judge_teacher_available` 查 normal_2，`judge_mother_available` / `judge_mother_followable` 都不查），§7「见学的母亲临盆 / 产后」补复审提的窄做法（只在 followable 里加 normal_2，不动公务事件前提 `self_mother_available`）；§4.3 萝莉 51 一行改为替换；§6 风险表 H1 一行补两类例外、L22 一行补履历迁移
3. §7 新增三条：意外中断 H（`constant.special_end_H_list` 里的 HYPNOSIS_CANCEL、TIME_STOP_OFF 等）的二次确认只清玩家与对象，群交模式与其余学生的 H 残留（普通群交同样存在，属群交系统）；通用 5「分到了同一组」而互动对象不要求同一格实践课（现有前提表达不了）；`test_behavior_loop` 的 `run_one_round` 读档后仍用夹具 `pl`（旧问题，列入下一轮的已知清单）
4. 三视角复审（收尾与文档、方案对照、测试覆盖）中期提交时仍在跑，结果在本会话（b579dc5f）的 Workflow 运行目录 `~/.claude/projects/C--code-erArk/b579dc5f-ec77-4275-8734-78e9419994f1/subagents/workflows/wf_b0533574-437`，用 `wf_watch.py <运行目录> --dump <文件>` 导出后逐条核实
5. 改后复现：`repro_c1` / `repro_main` / `repro_loop` / `repro_plan32`（`REPRO_PHASE=after`）与探针 `probe_loop`（应仍 40 / 40），脚本在 `%TEMP%/claude/C--code-erArk/b579dc5f-ec77-4275-8734-78e9419994f1/scratchpad/p32/`（不入库；找不到时按 §2.0 的表重建）
6. P6 收尾：测试 README 的覆盖描述、断言总数与夹具陷阱（`open_all_classroom`、`all_work_npc_set.setdefault(151, set())`、`talk.must_show_talk_check` 打桩、截短断言调 `judge_student_leave_truncate`、自建循环要把 `target_character_id` 设回自己、读档后 `pl` 已不是 `cache.character_data[0]`）；说明文档 §1 补新函数、§8、§16 计数；实施文档 §6.1 文件表、§6.3、§6.4；`update.log` 补本轮余下的条目；两个方案文档 `git mv` 到 `plan/done/`；停止点 2

### 6.2 实施前的假设复核

定案快照 `4275b1c98` 到实施时的 HEAD `c870b587f` 只多了两个方案文档（用户提交），源码未动；下表挑与代码结构有关的几条重读确认。

| # | 方案中的事实 | 出处 | 复核结果 |
| --- | --- | --- | --- |
| 1 | 10015 只挂在 384；371 / 373 / 375 只有 10011 | `Behavior_Effect.csv:181`、`:183`、`:185`、`:194` | 成立（`repro_c1` C1-2） |
| 2 | 407 清掉全场（含玩家）的 H 状态 | `Settle/default.py:4451~4472` | 成立（`repro_c1` C1-3） |
| 3 | `end_sex_class` 没有 running 时直接返回，可以重复调 | `sex_class_handle.py:778~780` | 成立（读代码） |
| 4 | 阶段进度取日历天、时钟跳过非季月 | `growth_handle.py:674~712`；`game_time.py:153~214` | 成立（读代码；`count_play_day` 已按此实现） |
| 5 | 性格倾向只在 `change_growth_value` / `set_growth_value` 写；选边只在成年结算 | `growth_handle.py:795~827`；`pregnancy_handle.py:667` | 成立（`repro_main` R1-1） |
| 6 | 住院判定拿角色 id 查病人表 | `class_ai.py:124`、`:677` | 成立（读代码） |
| 7 | 见学入口 2 只看槽位；`handle_all_entertainment_time` 对非学生岗工作日只算晚上 | `class_ai.py:739~740`；`handle_premise_time.py:408~441` | 成立（读代码） |
| 8 | NPC 分支先实时结算、后截短 | `character_behavior.py:177`、`:181` | 成立（`repro_loop` R6） |
| 9 | 跨天无条件清翘课 flag，且在 NPC 阶段之后 | `past_day_settle.py:71~72`；`character_behavior.py:78~80` | 成立（`repro_loop` R7） |
| 10 | 学生被玩家「授课」拉来时开始时刻对齐到玩家 | `handle_instruct.py:573~580` | 成立（读代码；`get_listen_manual_teach_course` 按此判） |

### 6.3 单元测试结果

| 文件 | 改前 | 改后 | 新增覆盖 |
| --- | --- | --- | --- |
| **合计** | **1438** | | |

### 6.4 尚未覆盖的验证

- 实施文档 §4.3 的游戏内整体测试留给用户
- PO / MO 重建（本机无 gettext）

### 6.5 追加调整实施记录

（与方案 §8 成对，每轮一节，附回归测试计数。暂无）
