# Plan 32（方案）：生长养成系统第十三轮复查

> 本 Plan 拆分为两个文件：**本文件为纯方案**（发现、现状调查、设计决策、接口设计、风险、范围外）；
> 逐文件改动步骤、构建、验证清单、回滚与实施过程记录见 `plan_32_生长养成系统第十三轮复查_实施步骤与记录.md`（下文简称"实施文档"）。
>
> 本 Plan 是 Plan 22（生长养成系统）、Plan 24（师生并入工作链）、Plan 25~31（第六~十二轮复查）之后的又一轮全面复查，前述各 Plan 均在 `plan/done/`。
> 实施完成后在 Plan 22 总纲追加 §18，只写一行指向本 Plan。

- 状态：未实施（方案定稿 2026-09-14）
- 来源：用户需求 → "使用skill，对 养成 系统再进行一次检查"
  - 本轮是 `system-review-round` skill 的第二次使用。用户选「约 10 个代理」：7 个核查代理（七个维度各一）+ 2 个核实代理（46 条分两批对抗式核实）+ 1 个复现代理；补漏与复查清单由主代理做
  - 每条发现都由主代理读到代码落点；H1、M2、M3、L1~L5 由主代理另写复现脚本跑出，另跑了一个长步长行为循环的探针（40 项全部正常，见 §2.3）
- 口径（待用户确认）：
  1. **课堂 H 以别的方式结束时一并下课**：玩家已不在 H 而课堂模式还开着，就按下课收尾（结束群交、体力归零、学生全部力竭、被撞见、转单人 H 后结束 H 都走这一条）；课上不再并排显示「结束群交」（§3.1）
  2. **阶段进度与「本阶段第几天」按可游玩天算**：只数季月里的天，阶段转换仍按日历天（§3.2）
     - 附问 Q1：推荐本条；备选接受现状
  3. **生日事件在生日当天直接推入**：跨天结算里对今天过生日的女儿插队首推入通用 3，正文不再写死「今天」（§3.3）
     - 附问 Q2：推荐本条；备选前提加固定高权重 / 回退 Plan 31 的生日前提
  4. **成年后改写性格倾向即重选这一对素质**：毕业典礼、成年纪念、通用 59 / 60 与成年前入队、成年后才处理的日常事件，倾向选项都落到素质上（§3.4）
     - 附问 Q3：推荐本条；备选去掉成年事件选项的倾向效果与提示
  5. **住院判定删掉**：干员从不进住院表，拿角色 id 查病人编号只会误判（§3.5）
  6. **非学生岗的萝莉只在自己的休息时间见学**（§3.6）
  7. 其余小修（§3.7~§3.15）
- 预计改动量：**约 55 个文件**，净增约 650 行（按 Q1~Q3 都选推荐估）
  - 逻辑 29 个：`sex_class_handle`、`realtime_settle`、`Settle/default.py`、`class_ai`、`handle_premise_work`、`character_behavior`、`handle_npc_ai`、`growth_handle`、`growth_event_handle`、`pregnancy_handle`、`past_day_settle`、`character_info_head`、`class_schedule_panel`、`schedule_handle`、`course_select_panel`、`growth_panel`、`schedule_template_panel`、`handle_premise/__init__`、`handle_premise_other`、`handle_premise_H`、`second_behavior`、`handle_ability`、`group_sex_panel`、`schedule_template_handle`、`game_time`、`education_constant`、`constant_promise`、`constant_effect`、`game_type`
  - 数据 11 个：`InstructConfig.csv`、`data/official_event/` 四张表、`data/talk/` 下 3 个口上文件、`target.csv`、`tools/ArkEditor/csv/Effect.csv` 与 `Premise.csv`
  - 测试约 12 个（含 README）；文档 4 个（说明文档、索引文档、Plan 22 总纲、`update.log`）
- 风险等级：**中低**。本轮的数值口径变化有三处：M1（阶段进度与抬头天数改按可游玩天，事件窗口的开放日期随之变）、M3（成年后倾向可改写素质）、H1（课堂随 H 收尾）；其余是判定收窄、去重与数据对齐
- 适用代码快照：`master @ 4275b1c98`（Plan 31 提交之后）
- 前置：Plan 22 一~四期、第五轮复查、Plan 24~31 均已完成

---

## 1. 目标

1. 课堂 H 不再留下「幽灵课堂」：H 以任何方式结束都会下课，学生不会被拉进没有博士的课堂，主修加成不再对全岛生效，也不会从此开不了课（H1）
2. 阶段进度窗口在每个出生日期上都开得出来；养成事件抬头的「本阶段第几天」不再一夜跳六十天（M1）
3. 生日事件在生日那天一定出现（M2）
4. 成年事件与成年前入队、成年后才处理的日常事件里，「倾向」选项落到性格素质上（M3）
5. 教师 / 母亲不再因为住院病人的编号与自己的角色 id 撞号而被判来不了（M4）
6. 改岗的萝莉按新岗位上班，不被日程里的「跟随母亲」顶掉（M5）
7. 截短规则与行为循环的三处接缝（L3~L5）、课堂计数与名单（L6~L12）、状态标识（L1、L13~L15）、事件队列与成长（L16、L19）、日程模板（L17、L18）、面板（L21）、数据（L22~L26）、注释 / 代码卫生 / 夹具（L27~L29）

**验收标准**：
- 全套回归测试通过，新增断言覆盖 §3 每一条
- 复现脚本（实施文档 §2.0）改前全部成立；改后问题命中全部不再成立（随口径的按拍板结果读），其余照旧
- `test_talk_data`、`tools/official_event_check.py` 通过
- 行为循环测试收敛，上午四节人均出勤 ≥ 3 节不变；长步长探针（实施文档 §2.0 的 `probe_loop.py`）照旧 40 项全部正常

## 2. 现状调查

本轮读过的范围：
- **`Education_System/` 全部 15 个模块**：七个核查代理与主代理各自逐行读过，含 Plan 31 新加的函数（`judge_skip_class_today`、`get_attend_judge_time`、`judge_schedule_teacher`、`get_course_type_by_position`、`judge_have_course_type`、`get_teacher_absent_mark`、`fit_text_width`、`get_player_manual_teach_course`、六个新前提）
- **外部挂接点**：
  - `character_behavior`：`init_character_behavior` 的玩家 / NPC 两阶段与跨天、`character_behavior` 的玩家与 NPC 分支、`judge_character_status_time_over`
  - `handle_npc_ai`：`find_character_target`（见学在工作链之前）、`judge_interrupt_character_behavior`、`judge_character_tired_sleep`、`commit_group_sex_tired_exit`、`get_chara_entertainment`；`handle_npc_ai_in_h` 的离场结束 H 与木头人锁定
  - `StateMachine/default.py`：303、304、561、713~722、见学 564 / 565；`Settle/default.py`：10010 / 10011 / 10014 / 10015、407、512、548、549、557、离线 / 上线；`Second_effect` 622 / 623；`past_day_settle`；`realtime_settle` 的实时结算与玩家实时数据
  - `handle_instruct`（授课 2010、开课 5209、下课 6021、结束群交 6008）、`group_sex_panel`（课堂模式的选人与邀请）、`sex_be_discovered_panel`、`official_event_handle` / `official_event_panel`（入队、出队、清理）、`pregnancy_handle`（婴儿→幼女、萝莉、成年）、`handle_ability`（待炫耀）、`talk`（口上加权）、医疗系统的住院表
- **数据**：`target.csv` 组 07 / 08；`InstructConfig` 的 2010 / 5209 / 6002 / 6003 / 6008 / 6021；`Behavior_Effect` 的 371~375 / 383 / 384；`data/official_event/` 五张表（前提、正文、选项的全量扫描）；教育口上 50 余个文件的前提统计；`Entertainment.csv`

基线：
- 回归 15 个文件 1438 条断言全绿（2026-09-14，Plan 31 之后）
- 死代码扫描：Education_System 442 个定义（函数 204 / 常量 187 / 方法 45 / 类 6），生产代码零引用的只有注册式的三个（说明文档 §15 第 10 条已写明）；三个面板无用的 `window_width` 属「同文件内只定义不读」，扫描按全仓名字计数查不出（见 L28）

下表的「已复现」都由 scratchpad 脚本在无头环境跑出（不入库，实施文档 §2.0 要求重建），各脚本改前全部成立：
- 主代理 `repro_c1.py`（H1）13 项：9 项问题命中，3 项前提对照，1 项数据事实
- 主代理 `repro_main.py`（M2、M3、L1、L2）22 项：8 项问题命中，9 项前提对照，5 项数据事实
- 主代理 `repro_loop.py`（L3~L5，走真实行为循环）14 项：5 项问题命中，8 项前提对照，1 项数据事实
- 复现代理 `repro_plan32.py`：（重跑后填）
- 另有长步长探针 `probe_loop.py`（40 项全部正常，§2.3）与只读模拟（M1 的 122 个出生日期枚举与蒙特卡洛，M2 的候选权重）

两个核实代理对 46 条逐条反驳：45 条成立（其中 8 条修正了机理或严重度，已按修正写进下表），1 条驳回（校验工具的「防复发缺口」：现有数据没有一处实例，属改进建议；其中唯一有实据的 Growth|3 窗口问题并入 M1）。

### 2.1 发现（高 / 中）

| # | 发现 | 证据 | 状态 |
| --- | --- | --- | --- |
| H1 | **实操课除「结束性技实操课」6021 以外的收尾路径都不关课堂模式：那节课永远 running，此后学生反复被拉进没有博士的「幽灵课堂」，主修加成对全岛生效，也再开不了课**。<br>• 开课同时置 `group_sex_mode`（10010）与 `sex_class_mode`（10014）；全仓库把 `sex_class_mode` 置 False 的只有 10015，而 10015 只挂在 6021 的 384 上。<br>• 其余收尾都只关群交：6008「结束群交」（前提 `GROUP_SEX_MODE_ON\|IS_H`，课上与 6021 并排显示）、玩家体力归零（373）、学生全部力竭与群交中被撞见（直接调 `handle_group_sex_end` → 371），效果串都是 529-407-636-800-10011；只剩一人转单人 H（375 只有 10011）后用结束 H 6002 / 6003（362）收尾同样漏。407 清掉全场的 H 状态，玩家已不在 H，课堂模式却还开着。<br>• 后果：① 5209 要 `SEX_CLASS_MODE_OFF`，从此开不了课；6021 要 `IS_H`，玩家不进一场 H 看不到。② `clean_expired_temp_class` 跳过 running，跨天不清。③ `get_attend_or_join_stage` 只看课堂模式与 running：此后任何一天，课表排在那间教室、过得了门槛的学生都判 JOIN，722 把她拉进 H、`settle_attend` 记出勤与实操课次数；玩家不在场时下一步被 END_H，再重新 JOIN，每一步都 +1，她那一节的常规课整节被顶掉。④ 主修加成钩子只判课堂模式，全岛 NPC 拿那门主修对应的经验都乘加成。<br>• 四期 §5.4 写的是「玩家点了才结束，唯二的例外是体力归零兜底」，实现连这两条例外都没关课堂模式 | `Behavior_Effect.csv:181`、`:183`、`:185`、`:194`；`InstructConfig.csv:213`、`:223~224`、`:229`、`:242`；`Settle/default.py:3079`、`:3135`、`:4451~4472`；`handle_npc_ai.py:104~109`、`:145~179`；`sex_be_discovered_panel.py:293~295`；`sex_class_handle.py:256`、`:767~788`、`:885~887`；`class_ai.py:366~380`；`StateMachine/default.py:3000~3006`；`handle_npc_ai_in_h.py:103~114`；`common_default.py:962~966`；四期方案 §5.4 | 已复现（`repro_c1.py`）：<br>• 课上 6008 与 6021 的显示前提同时成立；<br>• 走 371 的真实效果链、玩家这一步走完：群交模式已关、玩家已不在 H，课堂模式仍开、那节课仍 running、5209 开不了；跨天仍在；<br>• 次日学生走进那间实践教室上常规课：判 JOIN，722 拉进 H，出勤与实操课次数各 +1；<br>• 与课无关的干员拿主修经验：基础 10 → 20 |
| M1 | **阶段进度 Growth\|3 按日历天算，季月交替那一夜进度跳约 60 个日历天：婴儿中期的 9 条事件对 68% 的出生日期一天都开不出来，萝莉 3_GE_70 的 5 条对约四分之一开不出来，Plan 31 用 50 / 60 给婴儿 4 / 50 排的先后基本不起作用**。<br>• `get_stage_progress` 经 `get_stage_day` 取 `get_child_grow_day`，即 (现在 − 出生).days；游戏时钟只有 3 / 6 / 9 / 12 四个季月，`sub_time_now` 切月时归 1 日，9/30 的下一个可游玩日是 12/1，成长天数一夜 +62。婴儿期（90 天）一夜跳约 68 个百分点，幼女 / 萝莉期（180 天）约 34 个。<br>• 孩子只在季月出生；枚举全年 122 个出生日期：婴儿期只有 28~31 个可游玩日；婴儿中期窗口 [30%, 75%) 日历宽 40.5 天，比一次跳跃窄，83 / 122（68%）的出生日期在窗口里一天都没有，105 个不超过 3 天；萝莉 3_GE_70 窗口一天都没有的 26~30 个；婴儿 4（≥50）与婴儿 50（≥60）在同一天首次成立的 117 个。<br>• 蒙特卡洛 3000 次（每晚 70% 派一条）：两条都出现时婴儿 50 先于婴儿 4 的 57.6%；出了婴儿 50 却始终没出婴儿 4 的 23.4%；见过中期 9 条之一的只有 21.3%。<br>• 养成事件抬头的「萝莉期第 N 天」同源：一夜从第 23 天跳到第 85 天。<br>• 测试夹具写 `born_time = now − 50 / 60 天`（出生在非季月），这种状态在真实时钟下不会出现，所以测不出来 | `growth_handle.py:674~712`；`pregnancy_handle.py:77~87`；`game_time.py:153~174`、`:177~214`、`:275~287`；`growth_event_handle.py:285~295`；`婴儿.csv:9`、`:22~25`、`:49~51`、`:53~55`；`萝莉.csv:57`、`:64~65`、`:70~71`；`test_growth_event.py:348` | 已复现（只读模拟 + 核实代理重算）：<br>• 9/7 出生：9/30 进度 24.4%，下一个可游玩日 12/1 已 93.3%；<br>• 122 个出生日期与 3000 次蒙特卡洛，数字见左 |
| M2 | **通用 3 生日事件改用 `self_birthday_today` 之后几乎抽不到**。<br>• 前提 `T\|101_E_0&self_birthday_today`，只派幼女 / 萝莉（出生后第 90~450 个日历天）；生日按月、日比对，童年里只有一天成立（第 365 天，萝莉期）；用过成长加速药、第 365 天前已成年的一次都没有。<br>• 那一夜先过每晚 70%，再从几十条候选里按「配置权重 × 前提条数」抽，通用 3 只占 10。<br>• Plan 31 L13 把「任意一天都能抽到」改成「只在生日那天」时没算这个频率，约 98% 的女儿永远见不到它。<br>• 另：事件只在入队那天判前提，玩家隔几天才处理公务时，正文「今天是{Name}的生日」已与日期对不上<br>（核实代理建议降为 L；主代理维持 M：这是上一轮改动造成的回归，修法要拍板） | `通用.csv:8`；`handle_premise_other.py:1340~1357`；`pregnancy_handle.py:77~87`；`growth_event_handle.py:204~259`；`education_constant.py:470`；`official_event_handle.py:367~373`、`:420~448`、`:502~514` | 已复现（`repro_main.py` R2）：<br>• 3/15 出生的孩子童年里只有第 365 天是生日；<br>• 生日当天候选 54 条，通用 3 权重 10 / 392，理论入队 1.8%；实跑 400 次抽到 11 次；<br>• 122 个出生日期模拟：当天入队概率均值 1.6%、最高 2.3% |
| M3 | **成年事件与成年前入队、成年后才处理的日常事件，「倾向」选项加的倾向值再也落不到素质上**。<br>• `check_grow_to_girl` 先调 `settle_personality_talent` 按倾向值给四对性格素质选边，再 `push_graduation_event` 推通用 1 / 2 / 59 / 60；全仓库 `settle_personality_talent` 只有定义与这一处调用，之后倾向值怎么变都不会再选边。<br>• 四条成年事件里结算倾向（养成数值 10~13）的选项 13 个，其中 8 个的提示明写「倾向：坚强」之类。<br>• 成年前入队、成年那一刻还在队列里的萝莉日常事件（队首被毕业典礼、成年纪念插队），成年后才处理，同样只加倾向值 | `pregnancy_handle.py:664~672`；`growth_handle.py:577~608`、`:795~827`；`通用.csv`（通用 1 / 2 / 59 / 60 的选项）；`official_event_handle.settle_official_event_option` | 已复现（`repro_main.py` R1）：<br>• 毕业典礼选「坐在台下，看着她自己走完全程」（提示「倾向：坚强」）：倾向值 +4，坚强素质 274 仍为 0；<br>• 萝莉 38 成年前入队、成年后选「不问，让她自己去买」（倾向：坚强）：倾向值 +3，素质仍为 0 |
| M4 | **「住院不可用」拿角色 id 查以病人编号为键的住院表：编号撞上时教师整天被判来不了、母亲被判不能跟；真正想挡的「干员住院」在这张表里根本不存在**。<br>• `medical_hospitalized` 的键是医疗系统里抽象病人的 `patient_id`（`MedicalPatient`，模块级 `count(1)` 自增，每次启动从 1 数起），不关联任何角色，全仓库没有以角色 id 往里写的地方。<br>• `judge_teacher_available` 与 `judge_mother_available` 却用 `teacher_id in …` / `mother_id in …` 判住院，而干员角色 id 就是小整数（阿米娅 1、凯尔希 3……）。<br>• 撞号的几天里：学生侧 220820 降级自习；教师自己的 303 不查这个判据照常开讲，但 548 已占去重，整节只拿自习档；`<课>` 写「本节无教师」。母亲撞号时见学整段回落育儿室，挂 `self_mother_available` 的事件也抽不到。<br>• 测试夹具按「角色 id 作键」写（`medical_hospitalized = {101: {}}`），把错位掩盖了。干员真正住进住院部的情形（临盆 / 产后被瞬移回住院部）已由 normal_2 挡住 | `class_ai.py:124`、`:677`；`game_type.py:1428`；`medical_constant.py:65`、`:202~239`；`clinic_patient_management.py:35`；`hospital_patient_management.py:61~62`；`test_class_ai.py:134` | 读代码核实（主代理与核实代理）；复现见代理脚本 |
| M5 | **改岗（非学生岗）的萝莉，日程白天时段排了「跟随母亲」时，工作时间整段去见学、不上班；母亲不可跟时还被送去育儿室自由玩耍**。<br>• 见学判定排在工作链之前（`find_character_target`），唯一的让路条件是 `get_course_stage != NONE`，而它对非学生岗恒为 NONE。<br>• `judge_should_follow_mother` 入口 2 只看当前娱乐槽位是不是「跟随母亲」，不看岗位也不看是不是她的工作时间；槽位 1 / 2 就是 9~12、14~18。<br>• `apply_schedule_for_child` 只校验 need（153 的 need 是幼女 / 萝莉），改了岗的萝莉照样每天写进槽位；批量套用的名单也不看岗位。<br>• Plan 24 §3.9 的口径「改了岗的女儿课表还在但不去上课，不该因此不见学」只考虑了残留课表，没考虑她的新岗位，与口径 1「改了岗的女儿按新岗位上班」相悖 | `handle_npc_ai.py:354~361`；`class_ai.py:317~318`、`:707~748`、`:751~775`；`game_time.py:497~516`；`schedule_template_handle.py:348~390`；`Entertainment.csv:31`；`handle_premise_time.py:408~425` | 读代码核实；复现见代理脚本 |

### 2.2 发现（低）

| # | 发现 | 证据 | 状态 |
| --- | --- | --- | --- |
| L1 | **`<翘>` 当天整天都亮**：只看在节次内、今天挂着翘课 flag，不看这一节有没有课、是不是正在上点名必修的实操课。没课的节次写「翘课中（第 N 节）」，在课堂 H 里写「翘课中：本该上 实操课」，与 `get_course_stage` 的 SKIP 口径不一致 | `character_info_head.py:43~51`；`class_ai.py:329~339` | 已复现（R3）：第 3 节没课照亮；课堂上照亮；对照第 1 节有课亮「本该上」 |
| L2 | **今天翘过课的学生在博士的实操课上、或在实操教室等开课时被判「翘课被抓」**：623 只看 `judge_skip_class_today` 与同场景；她此刻正按设计去上 / 在上实操课（SEX_PENDING / JOIN / 课堂 H），16 条被抓口上里 11 条写「回教室 / 去上课」 | `second_behavior.py:325~331`；`class_ai.py:323~328`；`data/talk/system/second_caught_skip_class.csv` | 已复现（R4）：课堂上、等开课时都派出 caught_skip_class；对照开课前 5 分钟是 SEX_PENDING |
| L3 | **截短规则 B 对「人已在上课地点」一律不截**：个人式课（体育 / 兴趣 / 实习）没有拉人的一方，716 只能由她自己发呆时派出；她在上课地点做 120 分钟的同类娱乐（兴趣课「看电影」「排演舞剧」）时整节没有决策，出勤、缺课都不记，整节悄悄丢了。教室课有教师 303 拉人，不受影响。Plan 31 L1 只补了翘课日 | `class_ai.py:633~636`；`handle_npc_ai.py:682~685`；`StateMachine/default.py:2860~2864`；`target.csv:141`；`Entertainment.csv:12`、`:18` | 已复现（`repro_loop.py` R5，真实循环）：人在多媒体室看电影不截，120 分钟循环里出勤 +0、缺课 +0；对照人在育儿室截到 8:40、出勤 +1 |
| L4 | **截短规则在实时结算之后才截，截掉的那一段实时数值算两遍**：NPC 分支先按 [开始, min(原结束, 这一步结束)] 结算饥饿、尿意、疲劳、醉酒回落，之后才把行为截到离开时刻；下一个行为又从离开时刻结算一遍。淋浴 / 休息 / 睡醒的打断跳到 `cache.game_time`，不会重叠；学生截短是唯一会把时间线落回这一步之内的打断 | `character_behavior.py:176~184`、`:341~343`；`realtime_settle.py:106~148`、`:236~258`；`handle_npc_ai.py:674~685` | 已复现（R6，真实循环）：玩家一步 60 分钟，她的实时结算累计 110 分钟；对照没课 60 |
| L5 | **跨天结算无条件清翘课 flag**：一步跨过午夜走到次日上课时间时，NPC 阶段先跑完新一天的早上、549 挂上新一天的 flag，随后 `update_new_day` 把它清掉；当天剩余节次重新掷翘课，`<翘>`、被抓、截短的翘课日分支都失效。Plan 31 只兜住了反方向（旧 flag 带进新一天） | `past_day_settle.py:71~72`；`character_behavior.py:69~80`；`Settle/default.py:7751~7758`；`class_ai.py:472~478` | 已复现（R7）：新一天的 flag 被清、同一天第 2 节不再算今天已翘课；对照前一天的残留照清 |
| L6 | **512 广播按在座学生「自己的」时间线判排课与去重**：她下一节是玩家预约的临时实操课（格子教师为 0，557 直接返回、不写标记）而坐在这间教室等时，上一节的 NPC 教师换教室晚到开讲，512 按她下一节的节次记出勤 +1、发上一节的科目收益，并把她下一节的听课行为再结算一遍；玩家开课时 `settle_attend` 再 +1。触发组合窄（核实代理把 M 改为 L；教师走两跳即可，不需要处理顺序） | `Settle/default.py:7620~7649`、`:7716~7718`；`growth_handle.py:267~274`；`class_ai.py:97~101`、`:532~533`；`sex_class_handle.py:883~887` | 读代码核实；复现见代理脚本 |
| L7 | **同一节先记出勤、后记缺课在正常流程里触发得到**（Plan 31 §2.3 的「触发不到」不再成立）：实操课的 `settle_attend` 不写 `last_attend_period`，`settle_absent` 又不看这一节有没有出勤。实操课本节内提前下课、或玩家课中与学生做 H 后放回，体力落在 1~30% 的学生在本节内再派 721，记一节缺课 | `sex_class_handle.py:860~887`；`class_ai.py:169~197`、`:341~342`；`handle_instruct.py:1731~1740`；`Settle/default.py:4371` | 读代码核实；复现见代理脚本 |
| L8 | **同一节下课后重开预约的课，开课前后的必修名单不一致**：开课前名单与开课前提走 `find_reserved_class`（跳过 ended），必修名单是空集，没修过性技理论的必修生被排除；开课后 10014 按 running 那一条的必修名单把她拉进 H，这次既不记出勤也不加实操课次数 | `sex_class_handle.py:204~205`、`:231~238`、`:311~316`、`:762~763`；`Settle/default.py:3108~3110` | 读代码核实 |
| L9 | **旁观收益与「在上实操课」前提每次都重算入课门槛**：成年学生的实行值随苦痛、露出、玩家理智在课中变化，一跌破门槛，她仍在课堂 H 里，却拿不到旁观收益、在课前提判不过 | `sex_class_handle.py:895~923`、`:322~367`；`handle_premise_H.py:2308~2323`；`instuct_judege.py:101~107`、`:249~263`、`:390` | 读代码核实 |
| L10 | **不够格参加实操课的选修生，按到场时玩家开没开课得到两种结果**：开课前到的判「教师（玩家）能到岗」坐下听课，557 对教师 0 直接返回，整节零收益、不计出勤；开课后到的（玩家已在 H）判教师来不了，713 自习，548 计出勤并发这门性技的理论经验 | `class_ai.py:97~101`、`:366~379`；`Settle/default.py:7672~7682`、`:7716~7718`；`target.csv:139~140` | 读代码核实 |
| L11 | **课堂模式的群交模板选人不过入课门槛**：模板部位的选人列表是场景全员去掉玩家，课堂模式下只把体力不足的学生置灰；模板动作逐个目标结算、不查 is_h 与门槛，非学生（跟随进教室的干员、没过门槛的学生）被选进模板就会被操作并吃主修加成，绕过「课堂 H 只收学生岗」 | `group_sex_panel.py:596~645`、`:767~771`；`settle_behavior.py:54~74`、`:394~428`；`common_default.py:962~966` | 读代码核实（核实代理补核了模板动作的结算路径） |
| L12 | **排实操课页把已点名的必修生列进「不能参加（点名必修可豁免）」**：三份选修名单只按前置修习与门槛分，不对照同一页的必修名单 | `class_schedule_panel.py:528~559` | 读代码核实 |
| L13 | **玩家手动授课时，被拉来的学生的口上前提与 `<课>` 仍按她自己的课表取**：Plan 31 §3.13 只给玩家一侧加了回落。节次外授课时学生 CVP 为 −1，529 条听课口上一句不出；节次内本节尚未结算的学生，口上写她课表上的科目，实际发的是学识；`<课>` 写课表上的 NPC 教师（核实代理修正：原教师来不了、学生已自习时 548 已占去重，512 不出口上，只剩悬停写错） | `handle_premise/__init__.py:316~317`、`:343~346`、`:376~384`；`Settle/default.py:7593~7649`；`character_info_head.py:65~82`；`handle_instruct.py:549~581` | 读代码核实 |
| L14 | **学生在个人式课的上课地点体力缺课休息时，`<课>` 仍亮**：个人式课分支只看「本节有这门课、人在地点」，不看行为，与函数 docstring「体力不足去休息时不该显示」相反 | `character_info_head.py:27~35`、`:87~103`；`StateMachine/default.py:2966~2977` | 读代码核实 |
| L15 | **`<课>` 悬停「本节无教师，经验减半」与实际不符**：自习的科目经验是理论课的 1/3、实践课的 1/5、公开课不变；习得同级教师时约为 0.8 / 0.63 / 1 | `character_info_head.py:80`；`education_constant.py:247~265`；`growth_handle.py:276~313` | 读代码核实 |
| L16 | **公务队列出队不重判阶段**：孩子长大（婴儿→幼女、幼女→萝莉、萝莉→少女）前入队的上一阶段事件留在队列里，长大后顶着新阶段的抬头弹出；成年那一刻残留的萝莉期事件夹在毕业典礼、成年纪念与通用 59 / 60 之间（核实代理改为 L） | `official_event_panel.py:173~186`；`official_event_handle.py:451~514`；`growth_event_handle.py:285~295`、`:313~323`；`pregnancy_handle.py:551~607`、`:640~672` | 读代码核实 |
| L17 | **删除自建日程模板只解开在岛上的人**：外勤 / 外交 / 离线中的女儿仍指着旧编号，新模板复用这个编号时她回岛后静默套上新模板；「套用中 N 人」也漏数离线者 | `schedule_template_handle.py:140~160`、`:182~209`、`:413~428`；`Settle/default.py:4528~4529` | 读代码核实 |
| L18 | **成年非女儿干员离开学生岗后，当学生时套的日程模板永久生效**：每日改写不看岗位与身份，她不在个人课表名单、也不在批量套用名单，要解除只能先改回学生岗 | `schedule_template_handle.py:348~390`；`past_day_settle.py:58~91`；`growth_handle.py:62~111` | 读代码核实 |
| L19 | **婴儿长成幼女时先刷当天娱乐、后换素质**：`_settle_baby_grow_up` 先 `get_new_character`（刷娱乐），再把素质 101 换成 102，刷新时她还算婴儿，走成年通用池；玩家午夜之后入睡时这份娱乐用一整天（节次内没课默认见学不读槽位，主要影响节次外时段） | `pregnancy_handle.py:562~564`；`character_handle.py:345`；`handle_npc_ai.py:818~826` | 读代码核实 |
| L20 | **待炫耀只看女儿与阶段、不看岗位**：改岗萝莉靠工作练升的科目也记待炫耀，萝莉炫耀口上约一半写老师与课堂 | `handle_ability.py:120~132`；`second_behavior.py:333~334`；`show_off_cooking.csv:9` | 读代码核实 |
| L21 | **全局课表的缺位标注只认离岗 / 离岛**：被监禁（仍在岛、仍挂教师岗）的教师每节都降级自习，格子却不灰不标；一键排课的候选名单也不排除她 | `class_schedule_panel.py:46~66`；`schedule_handle.py:558~571`；`auto_schedule.py:96`、`:124`；`confinement_and_training.py:181~195` | 读代码核实 |
| L22 | **萝莉 1 / 20 / 26 与同一夜推入的期末事件讲的是同一份成绩单**：学期切换那一夜先置成绩单 flag、推期末事件，接着日常派发就可能再抽中这三条，两三条「交成绩单」叠在一起 | `萝莉.csv:6`、`:25`、`:31`；`期末.csv:6~14`；`past_day_settle.py:111~113`、`:131` | 读代码核实 |
| L23 | **通用 15 / 6 / 27 的正文是婴儿向（被人抱着、被抱去、抱着她站在舷梯口），却放在对幼女 / 萝莉都开放的通用桶里**。Plan 26 只处理了「不适合婴儿」这一侧 | `通用.csv:11`、`:20`、`:32`；`growth_event_handle.py:199~200` | 读代码核实 |
| L24 | **实操课「第一次来 / 老学生」口上被带女儿前提的行压住**：女儿行乘女儿倍率（设置 215，默认 5），1053~1056 只有 2；幼女第一次到场抽中「第一次来」的概率约 2.5~3.2%，旁观的老学生行约 8% | `join_sex_class.csv:37~40`、`:59~62`；`watch_sex_class.csv:56~61`；`talk.py:156~224` | 读数据与加权核实（核实代理手算） |
| L25 | **成年女儿拿到档位 3 的新成绩单时检查成绩单一条口上都没有**：1004 / 1005 带 `7_NE_3`，档位 3 的 1014~1017 只写幼女 / 萝莉 | `check_report_card.csv:10~11`、`:20~23`；`semester_handle.py:207~208`、`:421~428` | 读数据核实 |
| L26 | **点名课型的日常事件仍有漏网**：通用 5「实践课上……分到了同一组」只挂同胞；萝莉 57「训练场的记录……教官说」只挂阶段进度；萝莉 51 / 幼女 24「大礼堂的公开课」挂任意课（没有公开课前提） | `通用.csv:10`；`萝莉.csv:56`、`:62`；`幼女.csv:29` | 读数据核实 |
| L27 | **过期注释与文档**：<br>• 557 的说明 7 处仍写「学生晚于教师到场、教师正在同一教室授课」（Plan 31 §3.1 已改）；512 常量说明仍写「学识经验」；<br>• 翘课日「本节没课、下一节马上开课 → NONE」只写进了 `get_course_stage`，阶段常量、前提说明、target 行说明、编辑器前提表 7 处还是旧口径；<br>• `CHILD_GROWTH` 与说明文档 §2 写「出生时创建」「成年学生只用到 selected_course」；<br>• 三处行号引用过期（`settle_behavior.py:407 / :410` 实为 415 / 418，`default.py:3627` 实为 3665）；<br>• 说明文档 §13 口上条数（实为 522 / 529 / 468 / 405）、§8「17 条带 `T\|101_E_0`」（实为 40 条）、§12 的 557；<br>• 测试 README 的反斜杠陷阱示例自己被写坏 | `Effect.csv:232`、`:274`；`constant_effect.py:448~449`、`:535~536`；`game_type.py:364~372`、`:398~400`；`growth_handle.py:255~257`；`test_settle_effects.py:2`；`education_constant.py:299`、`:309`、`:320`、`:348`；`handle_premise_work.py:539`；`constant_promise.py:3745`；`target.csv:118`、`:142`；`Premise.csv:1896`；`Settle/default.py:3125`；`handle_premise_H.py:2235`；说明文档 `:77`、`:87`、`:234`、`:278`、`:294`；`README.md:50~51` | 读文本核实 |
| L28 | **代码卫生**：三个面板定义了不用的 `window_width`（`normal_config` 只为它导入），两处函数内重复导入；`schedule_template_handle` 定义了模板键常量却一半地方写字面量，5 个模块级常量违反「集中在 `education_constant`」的约定；`COURSE_LEARN_BASE[0]` / `COURSE_EXP_BASE[0]` 与 `week_day == 6` 写死编号 | `course_select_panel.py:14`、`:27`、`:519`、`:549`；`growth_panel.py:17`、`:29`、`:336`；`schedule_template_panel.py:18`、`:30`；`schedule_template_handle.py:40~51`、`:86`、`:126`、`:282`、`:408`；`growth_handle.py:277~278` | 读代码核实 |
| L29 | **测试夹具与真实数据不齐**：`CLASS_SM_SET` 自称「组 07 / 08 会派发的全部状态机」却缺 722，9 处「没有上课行命中」的断言防不住它；住院夹具按角色 id 建键（M4） | `test_class_ai.py:16~18`、`:134`；`target.csv:143` | 读代码核实 |

**待定 Q1**：见 §3.2。阶段进度与「本阶段第几天」按可游玩天算（推荐），还是接受现状？
**回答**：按可游玩天算

**待定 Q2**：见 §3.3。生日事件怎么保证出现？生日当天直接推入（推荐）、前提加固定高权重、还是回退 Plan 31 的生日前提？
**回答**：生日当天直接推入

**待定 Q3**：见 §3.4。成年后改写倾向即重选素质（推荐），还是去掉成年事件选项的倾向效果与提示？
**回答**：成年后改写倾向即重选素质

### 2.3 排查过、没有发现问题的疑点

留给下一轮复查参考，免得重复排查：

| 疑点 | 结论 |
| --- | --- |
| 玩家一步 120 / 180 分钟、教师每节换教室（两跳晚到）时，Plan 31 H1 的修法是否稳健 | 稳健：探针 S1 / S2（两种处理顺序）每节只结算一次、出勤 +3、缺课不变；S3 每步 10 分钟对照一致 |
| 翘课日长步长下的缺课逐节记、空节不记（含空节里 60 / 120 分钟娱乐） | 成立：探针 S4 / S5 缺课与翘课各 +2、最后一次缺课记在第 4 节、开课那一刻派 714 |
| Plan 31 新增 / 改签名的判据有没有漏改的调用点 | 没有：`judge_teacher_available(classroom)` 三处都传教室，`judge_skip_class_today` 是翘课 flag 的唯一读口（623 自读原始 flag，但只经它派发） |
| Plan 31 新代码的死代码、未用 import、TODO、对已翻译常量再包 `_()` | 没有（老代码的 `window_width` 另见 L28） |
| `judge_teacher_available` 与教师目标行 normal 前提对体控 / 心控是否同口径 | 同口径：体控 6、心控 7 不在 normal 1~7 任何一位；空气催眠只在人已在教室时豁免 |
| 空气催眠豁免与醉酒等其它 normal_5 原因叠加 | 不分叉：离开施术位置又不在玩家场景时空气催眠被解除，豁免只在那间教室里生效 |
| 全局课表「离岛」标注漏外勤 / 外交外派 | 不漏：两者都经 `handle_chara_off_line` 离开 `npc_id_got`，外派外交官还改了岗 |
| 教室课不查教室开放，开放后又关闭 | 触发不到：除初始化与调试面板外没有代码把已开放的场所关回去 |
| 0 点派发的事件读到前一天（生日、学期进度） | 不会：跨天结算在两阶段之后，`cache.game_time` 已是新的一天；学期结算排在事件派发之前 |
| 口上计数前提的取值时机（翘课 1004 读 24、实操课 1053~1056 读 25） | 对：714 先 `settle_absent` 再派行为，开课与 722 先 `settle_attend` 再派二段，口上都在计数之后判 |
| 检查成绩单分档口上带 `Growth\|23_E_1`，550 会清 flag | 不是死内容：玩家指令先出口上再跑效果 |
| 事件履历按「有没有养成数据」分存两处，婴儿先记全局、后建数据查不到 | 触发不到：婴儿能抽到的事件每个选项都带 `CVE_A1_Growth`，结算先于记履历就建出了养成数据 |
| 预设干员带 `Mother_id` 被当成玩家女儿 | 不存在：`Mother_id` 只由 `born_new_character` 写入，招募面板排除 |
| 世界设定「萝莉化」给全岛挂 103，只按阶段筛的地方卷进非女儿 | 没有问题：同胞、见学、成绩单、养成事件、待炫耀、成年结算都另判女儿；同学名单收萝莉化的成年学生，题材一致 |
| 玩家本人（id 0）混进学生 / 教师 / 事件名单 | 没有 |
| Plan 31 六个新前提漏身份过滤；课型前提在跨天推送时随时刻漂移 | 都没有：课型前提读每周课表与场所解锁状态，不看时刻 |
| 成年结算推通用 59 / 60 推给离线或非女儿；`ignore_capacity` 入队重复 | 都不会：先判女儿、只在睡眠结算遍历在岛的人；入队前仍过 `judge_event_can_enqueue` |
| 判母亲有效时没查母亲在不在 `npc_id_got` | 没有问题：离线的三条路都把位置改成 ["0","0"]，场景存在性检查判无效 |
| 检查成绩单对挂着素质 104 的预设干员可用 | 不会：指令前提先要是玩家的女儿 |
| `settle_attend` / `settle_course_attend` 的守卫放行改岗女儿 | 触发不到：调用方都先经只收学生岗的门槛或取数口 |
| 必修名单 / 选修人数 / 教师候选遍历 `npc_id_got` 漏离线者 | 按设计：只列此刻在岛的人 |
| Plan 31 M3 的「木头人」断言有没有走到 blockhead 分支 | 走到了：normal_5 / 6 都不含无意识 6 |
| Plan 31 其余新断言是否走真实路径；夹具女儿没有素质 451 | 都走真实路径；451 只在实行值计算里读，女儿在调用之前就返回 |
| 校验工具与 `education_constant` 的成年桶 / 期末桶常量是否一致 | 一致，`test_talk_data` 另有断言 |
| `calculation_instuct_judege` 传 `settle_hypnosis=False` 后还有没有别的写数据 | 没有：唯一的写入在催眠补正段，已按参数挡住 |
| 557 放宽后，512 给时间线在前、没被 303 拉回的学生重复记 | 常规情形不会（`last_attend_period` 去重）；下一节是玩家临时实操课的例外见 L6 |
| 翘课日的幼女在见学 / 自由玩耍中，截短规则 B 截不到 | 截得到：`follow_mother` / `free_play` 的 tag 都是娱乐 |
| 生日前提的出生日来源与 2 月 29 日分支 | 出生日只在出生面板写入；游戏时钟没有 2 月，2/29 分支走不到 |
| 课上重复开课、开课名单与 10014 拉人名单不一致 | 不会：5209 要 `SEX_CLASS_MODE_OFF`；两份名单同源（同一节下课后重开的例外见 L8） |
| 毕业典礼 / 成年纪念重复推 | 不会：只在 103→104 时推，萝莉化只在建角时调一次 |
| 同一教师在同一节被排进两间教室，两边学生都按能到岗结算 | 排不出来：一键排课与手排都过 `judge_teacher_conflict` |
| 课堂 H 里力竭退出的学生回到 AI 后被 721 记缺课 | 体力 ≤1 时置疲劳、需求链先接管，不会；体力 1~30% 的另见 L7 |
| 548 日程自习在没课的节次写 `last_attend_period`，挡掉后来的真课 | 不会：派到日程自习说明那一节没课 |
| 714 在教室里要先回宿舍，孩子没宿舍时空转 | 不会：新角色一定分得到宿舍 |
| 体力低的学生被需求链的休息截走、721 记不上 | 不会：需求链只在气力为 0 时才要休息 |
| 婴儿长成幼女上线时，NPC 阶段把婴儿期整段重演 | 不会：上线时开始时刻设为 `cache.game_time` |
| 303 按场景名单拉人，把刚开始走出教室的学生拉回来 | 不会：移动在行为开始时就换场景 |
| 教师晚到、先被处理时把还没决策的学生拉成听课，时长只剩余下分钟 | 属实但幅度小，属「303 保留拉人、照对齐」的既定口径（Plan 25 §3.5） |
| 教师在一节里被叫走、回来重开授课，教师侧收益重复 | 只在教师侧，属「行为开始时结算、不回退」的通用写法；学生侧去重 |
| 休息打断 / 睡醒打断跳到 `cache.game_time` 漏掉之后的节次 | 几乎触发不到 / 不会（睡醒按原结束时刻接着走） |
| `get_today_temp_class` 按 `cache.game_time` 判「今天」，一步跨过午夜 | 要连续 7 小时以上从上课时间走过午夜才碰到，覆盖层失效后 NPC 教师照常授课，可以接受 |
| 截短条件在后一步才成立，截出的离开时刻早于本步开始 | 回退几分钟重走，实时结算按 `pl_start_time` 封顶，不重复；循环照样收敛 |
| 303 拉人、玩家授课拉人也造成实时结算重复 | 不会：重复只出在打断截短这一条上（L4） |
| 本轮养成口上与事件表的前提 token 有没有拼错、未注册、引用不存在的编号 | 没有：全量扫描 50 余个口上文件与 5 张事件表 |
| 校验防复发缺口（CVP 运算符拼错、养成数值编号越界、部门 15 的 sub_key 越界、日常事件读此刻课型） | 核实代理驳回：现有数据没有一处实例，属改进建议；有实据的 Growth\|3 窗口问题并入 M1 |
| 胎教三个行为、照料行为的口上条数 | 说明文档写得对（各 10 条、10~14 条） |
| 萝莉 8「实习课第一次上岗」、幼女 1「第一次坐进理论教室」不保证真是第一次 | 接受：现有 token 表达不了「第一节某课型」，两条都是每人一次、权重高 |
| 萝莉 6 改读本学期出勤后会不会恒不成立 | 不会：只有学期切换那一夜本学期出勤为 0 |
| 死代码 | 见基线 |

### 2.4 可复用的既有实现

| 需求 | 现成实现 |
| --- | --- |
| 下课收尾 | `sex_class_handle.end_sex_class`（没有 running 时直接返回，天然幂等，H1 与 10015 可以各调一次） |
| 「今天过生日」 | `handle_premise_other.handle_self_birthday_today` |
| 插队首、不受容量约束的推入 | `official_event_handle.push_official_event(…, to_front=True)`（毕业典礼的写法） |
| 性格选边 | `growth_handle.settle_personality_talent` 的逐对规则（M3 抽成按对的函数共用） |
| 「此刻算不算她的休息时间」 | `handle_premise.handle_all_entertainment_time`（学生岗 / 没有工作 / 休息日白天也算，其余工作日只有晚上） |
| 季月归并 | `game_time.get_season_month` |
| 按课型查课表 | `growth_handle.judge_have_course_type`（L26 的公开课前提在它上面加一个课型） |
| 本节已缺课 | `growth_handle.judge_absent_this_period` |
| 某节是否已结算 | `CHILD_GROWTH.last_attend_period`（L7 让 `settle_attend` 也写它） |
| 玩家手动授课的课型 / 科目 | `handle_premise.get_player_manual_teach_course`（L13 学生侧复用） |
| 开课沿用的临时课条目 | `sex_class_handle.find_class_to_start`（L8 的必修名单与它同源） |
| 教师缺位标注 | `class_schedule_panel.get_teacher_absent_mark`（L21 加监禁） |

### 2.5 已知陷阱与硬约束

1. **前提必须是纯函数**（Plan 24 §2.6-1）：L9、L10、L13 新的判据只读数据；公开课前提只读 `child_growth`
2. **NPC 按各自的时间线推进，玩家一步可以跨过整节**：判定一律用行为开始时刻；L4 调整的是同一步里实时结算与截短的先后，不改截短的判据
3. **跨天结算在 NPC 阶段之后**（`character_behavior.py:78~80`）：凡是跨天清的标记，一步跨过午夜时既可能把旧值带进新一天（Plan 31 L2），也可能清掉新一天刚写的值（L5）；认日期的标记只清过期的
4. **游戏时钟只有季月**：成长天数按日历天，一夜可以跳 60 天；凡是按日历宽度设计的窗口都要按可游玩天复核（M1）。测试夹具的出生日要落在季月，`born_time = now − N 天` 这种写法在真实时钟下不会出现
5. **课堂模式同时置群交模式**：凡是只关群交的收尾路径都会留下课堂模式；H1 之后以「玩家不在 H」作为课堂的收尾判据，不再逐条补效果串
6. **口上按权重组抽**：前提条数就是权重，女儿前提再乘设置 215（默认 5），同一行为内女儿行与非女儿行混放时非女儿行几乎抽不到（L24）
7. **公务事件表是编译产物**：改 `data/official_event/*.csv` 后要重建 `data/Official_Event.json`；测试引导 import 的增量构建会重建

## 3. 设计决策

### 3.1 课堂 H 随 H 收尾（H1，推荐口径 1）

- 新增 `sex_class_handle.settle_orphan_class() -> bool`：课堂模式开着、而玩家已不在 H 时，按下课处理——`cache.sex_class_mode = False`、`end_sex_class()`（预约的打 ended、当场开的删除）；返回是否收了尾。
- 挂点：
  - 玩家每一步都跑的 `realtime_settle.judge_pl_real_time_data()` 末尾调它：6008、体力归零、全员力竭、被撞见、转单人 H 后结束 H 等路径都以 407 / 404 清掉玩家的 H 状态告终，玩家这一步的收尾检查里就下课；
  - `clean_expired_temp_class`（跨天结算已调用）里，running 的那条只在课堂模式开着且玩家在 H 时跳过；否则按过期清掉，并把课堂模式一并关掉——兜住旧档里已经留下的幽灵课堂。
- 6008「结束群交」的前提加 `SEX_CLASS_MODE_OFF`：课上只剩 6021，下课口上（提前 / 按时 / 拖堂）照常出。
- `end_sex_class` 与 10015 的 docstring 改写：「只由玩家手动触发，唯二的例外是体力归零兜底」→「玩家点下课，或课堂 H 以别的方式结束（玩家已不在 H）时一并下课」。
- 转单人 H（375）时玩家仍在 H，课照上（最后那名学生的单人 H 仍是课、主修加成照算），直到这场 H 结束。

| 候选 | 弃选原因 |
| --- | --- |
| 只在 371 / 373 的效果串里补 10015 | 漏掉转单人 H 后结束 H、单人 H 里体力归零、被撞见等路径，旧档里的幽灵课堂也清不掉 |
| 10011 关群交时一并下课 | 只剩一人转单人 H（375 也跑 10011）时课就下了；转单人 H 后结束 H 那条仍漏 |
| 保留课堂模式、让 6021 在玩家不在 H 时也能点 | 学生照样被 722 拉进没有博士的课堂，主修加成照样对全岛生效 |

代价：6008 在课上隐藏后，玩家要结束课堂只能用 6021；这本来就是课堂的正门，四期 §5.4 写的也是「出现结束性技实操课」。

### 3.2 阶段进度按可游玩天（M1，推荐口径 2；Q1）

- 新增 `game_time.count_play_day(start_date, end_date) -> int`：两个时刻之间经过的可游玩天数——日历天数减去其间被时钟跳过的非季月天数（按月累加，不逐日遍历）。
- `growth_handle.get_stage_day`：本阶段已过的**可游玩天**数；`get_stage_progress`：本阶段已过可游玩天 ÷ 本阶段总可游玩天。阶段的起点、终点仍按有效成长天数（90 / 270 / 450，含成长加速药）换算回日历时刻：出生时刻 + (阈值 − 加速药天数) 天，早于出生的按出生算；再用 `count_play_day` 数这一段里的可游玩天。
- 阶段转换（长大）照旧按有效成长天数，不变。
- 养成事件抬头「萝莉期第 N 天」随之按可游玩天（婴儿期约 30 天、幼女 / 萝莉期约 60 天）；养成总览的阶段进度同源。
- 改后：婴儿期 28~31 个可游玩日，每个出生日期的婴儿中期窗口 [30%, 75%) 都有 12~14 个可游玩日；婴儿 4（≥50）与婴儿 50（≥60）首次成立相隔约 3 个可游玩日。校验工具不另加「窗口日历宽度」规则。

| 候选 | 弃选原因 |
| --- | --- |
| 接受现状 | 68% 的出生日期见不到婴儿中期 9 条，约四分之一见不到萝莉 3_GE_70 的 5 条；抬头天数一夜跳六十天 |
| 按日历天，把窄窗口放宽到 ≥62 天 | 婴儿期一共 90 天放不下；换季仍让进度一夜跳 68 个百分点 |
| 游戏时钟不跳月 | 季月制是全局设计，影响全部系统 |

### 3.3 生日事件在生日当天直接推入（M2，推荐口径 3；Q2）

- 新常量 `education_constant.BIRTHDAY_EVENT_UID = "通用3"`。
- 新增 `growth_event_handle.push_birthday_event() -> List[int]`：跨天结算里，对日常派发名单（`get_growth_event_character_list`）中今天过生日（`handle_self_birthday_today`）、`judge_event_can_enqueue` 通过、事件前提成立的女儿，插队首推入（不受容量约束）；返回推入的角色 id。
- `update_new_day` 在 `check_new_day_official_event` 之前调它：日常随机派发因「已在队列里」不会再抽到它。
- 正文不再写死「今天」：「今天是{Name}的生日。」→「{Name}的生日到了。」（插了队首，玩家多半当天就看到；隔几天才处理时也不矛盾）。

| 候选 | 弃选原因 |
| --- | --- |
| 前提里加固定高权重（`CVP_A1_Weight`） | 仍要过每晚 70% 与每孩 4 条容量，抽中率约六成，生日照样可能错过 |
| 回退 Plan 31（任意一天可抽） | 正文「今天是生日」与日期对不上正是 Plan 31 L13 要修的 |

### 3.4 成年后改写倾向即重选这一对素质（M3，推荐口径 4；Q3）

- 从 `settle_personality_talent` 抽出按对的 `settle_personality_pair(character_id, pair_id) -> int`：正值取正向素质、负值取负向并清掉另一侧；为 0 时两侧都不动（与成年结算同一规则）；返回写上的素质 id（没写为 0）。`settle_personality_talent` 改为逐对调它，行为不变。
- `change_growth_value` / `set_growth_value` 改写性格倾向（10~13）之后：角色是已成年（阶段 104）的女儿，就对这一对调 `settle_personality_pair`。成年结算之后的一切倾向改写（毕业典礼、成年纪念、通用 59 / 60、成年前入队成年后才处理的日常事件）都因此落到素质上。
- 静默改写，不另出文本：事件选项的提示已写明倾向。

| 候选 | 弃选原因 |
| --- | --- |
| 把成年选边挪到毕业典礼、成年纪念、59 / 60 都处理完以后 | 四条事件的处理时机由玩家决定，拖多久都有可能；成年前入队、成年后才处理的日常事件照样落空 |
| 去掉成年事件选项的倾向效果与提示 | 13 个选项里 8 个明写倾向，是成年事件的主要内容；成年前入队的日常事件仍落空 |

### 3.5 住院判定删掉（M4，推荐口径 5）

- `judge_teacher_available`、`judge_mother_available` 删掉 `medical_hospitalized` 两行；注释写明理由（那张表的键是抽象病人编号，干员从不进表；干员真正「住院」的临盆 / 产后已由 normal_2 挡住）。
- `test_class_ai` 的住院夹具改为：住院表里有编号等于教师角色 id 的病人时，教师照常可用。

| 候选 | 弃选原因 |
| --- | --- |
| 按病人结构反查角色 | `MedicalPatient` 不关联任何角色，查不出来 |

### 3.6 非学生岗的萝莉只在自己的休息时间见学（M5，推荐口径 6）

- `judge_should_follow_mother` 入口 2：槽位是「跟随母亲」时，另要 `handle_premise.handle_all_entertainment_time(character_id)` 成立——学生岗、没有工作、休息日的白天也算她的休息时间，其余岗位工作日只有晚上。
- 入口 1（幼女默认见学）不变：幼女恒在学生岗。
- 日程模板照写不动；她改回学生岗、或到了晚上，「跟随母亲」照旧生效。

### 3.7 截短规则与行为循环（L3、L4、L5）

- **L3**：`get_student_leave_time` 的规则 B，人已在上课地点时不再跳过，截到**开课那一刻**（与翘课日分支同一写法）：她在开课那一刻重新决策，个人式课派 716，教室课照常听课 / 被 303 拉；离开那一刻本节还有课的仍不截。
- **L4**：从 `judge_interrupt_character_behavior` 抽出学生截短为 `handle_npc_ai.judge_student_leave_truncate(character_id) -> bool`（守卫照旧：行为开始时刻早于 `cache.game_time` 才判），`character_behavior` 的 NPC 分支在 `realtime_settle.character_aotu_change_value` 之前调它；`judge_interrupt_character_behavior` 里原来那段删掉。实时结算于是按截短后的结束时刻封顶。
- **L5**：`update_new_day` 只在 `skip_class_day` 早于今天时清翘课 flag；见学 flag 照旧无条件清。

### 3.8 课堂计数与名单（L6~L12）

- **L6**：512 对 NPC 教师：学生当前行为的节次（按她的开始时刻）与教师开讲的节次不同，就跳过她（她已在上别的节次）。玩家手动授课不变。
- **L7**：`settle_absent` 在本节已记出勤（`last_attend_period` 等于本节）时不记；`settle_attend` 记出勤时一并写 `last_attend_period`（按 `get_attend_judge_time` 那一节，节次外不写）。同一节只落一种记录的两个方向都齐了。
- **L8**：`get_must_attend_set(classroom)` 在没有 running 时改走 `find_class_to_start`（含本节已下课的那条），与 `start_sex_class` 取条目同源。
- **L9**：新增 `sex_class_handle.get_class_member_list() -> List[int]`：课堂模式下与玩家同场景、`is_h`、是学生岗或女儿的角色——「已被拉进这节课」按身份认，不再重算入课门槛（门槛只在入课那一刻判）。`get_watcher_list` 与 `handle_self_in_sex_class` 改用它。
- **L10**：新增 `class_ai.judge_course_teacher_available(student_id, course) -> bool`：课表格子的教师是玩家（0，临时实操课）时，另要她能进课堂（`judge_can_join_sex_class`，必修生豁免前置修习）；否则同 `judge_teacher_available(教师, 教室)`。`self_course_teacher_available` / `unavailable` 改用它：不够格的选修生无论开课前后都判「教师来不了」，降级自习、计出勤，与开课后到场的现行为一致。
- **L11**：群交模板选人：课堂模式下名单只收 `get_class_member_list()`（已在课堂 H 里的学生）；普通群交不变。
- **L12**：排实操课页：三份选修名单先去掉本页必修名单里的人（必修行单列）。

### 3.9 状态标识（L1、L13 的 `<课>`、L14、L15）

- **L1**：`<翘>` 只在本节有课、不是点名必修、人不在 H 时亮（与 SKIP 同口径）；其余节次落到下面的 `<课>` 判定。
- **L13**：听玩家手动授课的学生（行为是听课、与玩家同场景、玩家正在授课且 `get_now_teaching(0)` 取不到、开始时刻与玩家对齐），悬停写「授课：{玩家}」与玩家的课型、学识。判据抽成 `handle_premise.get_listen_manual_teach_course(character_id) -> Optional[tuple]`（§3.10 的 CVP 共用）。
- **L14**：个人式课分支：本节已记缺课或行为是休息时不亮。
- **L15**：悬停改为「本节无教师，按自习收益」。

### 3.10 前提与二段行为（L2、L13 的 CVP、L20）

- **L2**：623 翘课被抓：她在 H 中、在正在进行的实操课里、或此刻 `get_course_stage` 为 SEX_PENDING / JOIN（去上、正要上实操课）时不派。
- **L13**：`get_now_course_type` / `get_now_course_ability` 对学生：`get_listen_manual_teach_course` 取得到时按它回落（课型按教室、科目学识），与 512 同口径。
- **L20**：待炫耀只记学生岗。

### 3.11 事件队列与成长（L16、L19）

- **L16**：新增 `growth_event_handle.drop_stale_stage_event(character_id) -> int`：把队列里这个孩子的部门 15 阶段桶事件（sub_key 0 / 101~103）中 `judge_stage_pass` 已不成立的删掉；成年桶（104）与期末桶（200）不动。婴儿→幼女、幼女→萝莉、萝莉→少女三处阶段转换在换完素质后调它；成年结算在推毕业典礼之前调。
- **L19**：`_settle_baby_grow_up` 换完素质、置学生岗之后重刷当天娱乐（`get_chara_entertainment` + `apply_schedule_for_child`）。

### 3.12 日程模板（L17、L18、L28 的模板键）

- **L17**：`delete_template` 与 `get_template_use_count` 遍历全部角色（`cache.character_data`），不只在岛的。
- **L18**：`apply_schedule_for_child`：非女儿且不在学生岗的跳过（模板保留，改回学生岗照旧生效）。
- **L28**：模板键与 need 分隔符 5 个常量挪进 `education_constant`（`TEMPLATE_KEY_NAME` / `TEMPLATE_KEY_SLOT` / `TEMPLATE_NEED_NONE` / `TEMPLATE_NEED_SPLIT` / `TEMPLATE_NEED_OR_SPLIT`），模块与面板里的字面量一律改用常量。

### 3.13 面板（L21、L28 的面板部分）

- **L21**：`get_teacher_absent_mark` 加「（被监禁）」（短写「（监禁）」），优先级排在「已离岗」之后、「不在岛上」之前；`get_teacher_candidate_list` 排除被监禁的教师。
- **L28**：删三个面板不用的 `window_width` 与只为它服务的 `normal_config` 导入、两处函数内的重复导入；`week_day == 6` 改为按 `WEEK_DAY_COUNT` 推。

### 3.14 数据（M2 正文、L22~L26）

| # | 做法 |
| --- | --- |
| M2 | 通用 3 正文开头「今天是{Name}的生日。」→「{Name}的生日到了。」，其余不动 |
| L22 | 萝莉 1 / 20 / 26 挪进 `期末.csv`（sub_key 200）：前提去掉 `23_E_1`（推送时恒为 1，校验工具也禁它），加 `CVP_A1_T\|103_E_1`，保留 `7_NE_3` 与原有其余条件；日常派发不再抽到，学期切换时与其它期末事件同池抽一条 |
| L23 | 通用 6 / 15 / 27 加 `CVP_A1_T\|103_E_0`（婴儿、幼女仍可抽到） |
| L24 | 实操课到场 1053~1056、旁观 1054 / 1055 加 `self_is_player_daughter`：这几行都限幼女 / 萝莉，与女儿行同享女儿倍率 |
| L25 | `check_report_card.csv` 新增 2 条成年女儿的档位 3 口上：前提照 1014~1017 的写法（档位 3、新成绩单待查看、交互对象是女儿），阶段换成 `CVP_A2_T\|104_E_1` |
| L26 | 通用 5 加 `self_have_practice_course`；萝莉 57 加 `self_have_pe_course`；萝莉 51、幼女 24 加新前提 `self_have_public_course` |

| 候选 | 弃选原因 |
| --- | --- |
| L22 只在三条上加「今天不是学期切换当天」之类的前提 | 学期切换后几天里 flag 仍在，玩家不查成绩单时照样与期末事件叙述同一份成绩单 |
| L24 把女儿行拆到与首次 / 老学生不同时成立的情形 | 要改 8 行前提的语义，加一个女儿前提最省 |

### 3.15 注释、文档与夹具（L27~L29 与各项说明）

- **L27**：
  - 557 的说明（`Effect.csv:274`、`constant_effect.py:536`、`game_type.py:398~400`、`growth_handle.py:255~257`、说明文档 `:87` / `:278`、`test_settle_effects.py:2`）改为「学生坐下听课时，本节教师判能到岗即结算」；512 常量说明补「按课表科目、NPC 教师只发给自己的学生」
  - 翘课日口径补进 `COURSE_STAGE_NONE` / `COURSE_STAGE_UPCOMING` / `UPCOMING_MINUTE`、`handle_self_course_upcoming`、`constant_promise`、target 210810 / 220830 的说明、`Premise.csv:1896`
  - `CHILD_GROWTH` 类说明与说明文档 §2：出生时不一定创建（胎教值 > 0 才建，否则首次写入时惰性建）；成年学生岗也会记出勤、缺课、翘课、实操课次数
  - 三处行号改成引用函数名（`settle_behavior.handle_instruct_data` 里口上先于效果；`handle_target_add_small_shy`），不再写行号
  - 测试 README 的反斜杠示例改用文字描述
- **L28**：见 §3.12、§3.13；`COURSE_LEARN_BASE[0]` / `COURSE_EXP_BASE[0]` 改为 `[COURSE_TYPE_THEORY]`
- **L29**：`CLASS_SM_SET` 改从 target 组 07 / 08 的实际状态机取（或补 722，并断言与 target 一致）；住院夹具见 §3.5
- 说明文档：
  - §1：`sex_class_handle` 一行补「课堂随 H 收尾、课堂成员按身份认」；`growth_handle` 补「阶段进度按可游玩天」
  - §2：`CHILD_GROWTH` 生命周期（L27）；`last_attend_period` 的写入点加上 `settle_attend`
  - §4：截短规则 B 人已在地点时截到开课那一刻；截短在实时结算之前；512 跳过节次不同的学生；教师为玩家时够不够格的判据
  - §5：课堂收尾；必修名单与开课条目同源；旁观按成员名单
  - §6：翘课 flag 跨天只清过期的
  - §8：生日事件推入；阶段桶事件在长大时清掉；阶段进度按可游玩天；萝莉 1 / 20 / 26 挪进期末；公开课前提
  - §12、§13：557 描述、口上条数、通用桶 40 条
  - §15：新增三条：「课堂模式以玩家在 H 为前提，任何只关群交的收尾都由 `settle_orphan_class` 兜住」「按日历天设计的窗口一律按可游玩天复核」「同一步里改行为时长的打断要排在实时结算之前」
  - §16：测试计数
- 测试 README：夹具出生日要落在季月（§2.5-4）
- 索引文档：计划表那一行改成「plan_25 ~ plan_32」，补第十三轮一句
- Plan 22 总纲：追加 §18，一行指向本 Plan

## 4. 接口设计（实施的权威定义）

### 4.1 常量与字段

`education_constant.py`（成年事件常量旁）：

```python
BIRTHDAY_EVENT_UID = "通用3"
""" 生日事件（Plan 32）：跨天结算时对今天过生日的女儿直接插队首推入，不走每日随机派发（一生只有一次生日落在童年里） """
```

`education_constant.py`（日程模板一组，自 `schedule_template_handle` 挪入）：

```python
TEMPLATE_KEY_NAME = "name"
""" 日程模板数据的键：模板名 """
TEMPLATE_KEY_SLOT = "slot"
""" 日程模板数据的键：各时段的活动 """
TEMPLATE_NEED_NONE = …
TEMPLATE_NEED_SPLIT = …
TEMPLATE_NEED_OR_SPLIT = …
""" need 解析用的三个分隔符 / 占位值，取值照搬 schedule_template_handle 现有定义 """
```

`constant_promise.Premise`（`SELF_HAVE_INTERN_COURSE` 之后）：

```python
SELF_HAVE_PUBLIC_COURSE = "self_have_public_course"
""" 自己有公开课：学生岗且个人课表上至少有一格是每周确有的公开课（大礼堂） """
```

不新增存档字段。

### 4.2 函数签名

| 模块 | 函数 | 变化 |
| --- | --- | --- |
| `game_time` | `count_play_day(start_date, end_date) -> int` | 新增：两个时刻之间的可游玩天数（§3.2） |
| `growth_handle` | `get_stage_day` / `get_stage_progress` | 按可游玩天（§3.2） |
| `growth_handle` | `settle_personality_pair(character_id, pair_id) -> int` | 新增；`settle_personality_talent` 改为逐对调它（§3.4） |
| `growth_handle` | `change_growth_value` / `set_growth_value` | 已成年女儿改写倾向后重选这一对（§3.4） |
| `growth_event_handle` | `push_birthday_event() -> List[int]` | 新增（§3.3） |
| `growth_event_handle` | `drop_stale_stage_event(character_id) -> int` | 新增（§3.11） |
| `past_day_settle` | `update_new_day` | 翘课 flag 只清过期的；派发前推生日事件（§3.7、§3.3） |
| `pregnancy_handle` | `_settle_baby_grow_up` / `check_grow_to_loli` / `check_grow_to_girl` | 换完素质后清阶段桶残留；婴儿→幼女重刷娱乐（§3.11） |
| `sex_class_handle` | `settle_orphan_class() -> bool` | 新增（§3.1） |
| `sex_class_handle` | `clean_expired_temp_class` | running 的只在课堂模式开着且玩家在 H 时跳过（§3.1） |
| `sex_class_handle` | `get_class_member_list() -> List[int]` | 新增；`get_watcher_list` 改用它（§3.8 L9） |
| `sex_class_handle` | `get_must_attend_set(classroom)` | 没有 running 时走 `find_class_to_start`（§3.8 L8） |
| `sex_class_handle` | `settle_attend` | 记出勤时写 `last_attend_period`（§3.8 L7） |
| `realtime_settle` | `judge_pl_real_time_data` | 末尾调 `settle_orphan_class`（§3.1） |
| `Settle/default` | 512 `handle_teach_add_just` | NPC 教师跳过节次不同的学生（§3.8 L6） |
| `class_ai` | `judge_teacher_available` / `judge_mother_available` | 删住院判定（§3.5） |
| `class_ai` | `judge_should_follow_mother` | 入口 2 另要休息时间（§3.6） |
| `class_ai` | `get_student_leave_time` | 规则 B 人已在地点截到开课那一刻（§3.7 L3） |
| `class_ai` | `settle_absent` | 本节已记出勤不记缺课（§3.8 L7） |
| `class_ai` | `judge_course_teacher_available(student_id, course) -> bool` | 新增（§3.8 L10） |
| `handle_premise_work` | `handle_self_course_teacher_available` / `unavailable` | 改用 `judge_course_teacher_available`（§3.8 L10） |
| `handle_npc_ai` | `judge_student_leave_truncate(character_id) -> bool` | 新增，自 `judge_interrupt_character_behavior` 抽出（§3.7 L4） |
| `character_behavior` | `character_behavior` | NPC 分支在实时结算之前截短（§3.7 L4） |
| `handle_premise/__init__` | `get_listen_manual_teach_course(character_id) -> Optional[tuple]` | 新增；CVP 课型 / 科目对学生回落（§3.9、§3.10 L13） |
| `handle_premise_H` | `handle_self_in_sex_class` | 改用 `get_class_member_list`（§3.8 L9） |
| `handle_premise_other` | `handle_self_have_public_course` | 新增前提（§3.14 L26） |
| `second_behavior` | `judge_child_growth_second_behavior` | 623 的三种不派情形（§3.10 L2） |
| `handle_ability` | `gain_ability` 的待炫耀 | 只记学生岗（§3.10 L20） |
| `group_sex_panel` | `show_target_chara_list` | 课堂模式只列课堂成员（§3.8 L11） |
| `character_info_head` | `get_now_class_tip` | L1、L13、L14、L15 |
| `class_schedule_panel` | `get_teacher_absent_mark`、`_edit_sex_class` | 监禁标注（L21）；选修名单去掉必修（L12） |
| `schedule_handle` | `get_teacher_candidate_list` | 排除被监禁的教师（L21） |
| `schedule_template_handle` | `delete_template` / `get_template_use_count` / `apply_schedule_for_child` | 遍历全部角色（L17）；非女儿离岗跳过（L18）；模板键常量（L28） |

### 4.3 数据行

| 文件 | 行 | 改为 |
| --- | --- | --- |
| `data/csv/InstructConfig.csv` | 6008 | 前提加 `SEX_CLASS_MODE_OFF` |
| `data/official_event/通用.csv` | cid 3 | 正文开头「{Name}的生日到了。」 |
| 同上 | cid 5 | 前提加 `&self_have_practice_course` |
| 同上 | cid 6 / 15 / 27 | 前提加 `CVP_A1_T\|103_E_0` |
| `data/official_event/萝莉.csv` | cid 1 / 20 / 26 | 删去（挪进期末） |
| 同上 | cid 51 / 57 | 前提加 `self_have_public_course` / `self_have_pe_course` |
| `data/official_event/幼女.csv` | cid 24 | 前提改 `self_have_public_course`（替换 `self_have_any_course`） |
| `data/official_event/期末.csv` | 新增 3 行 | 原萝莉 1 / 20 / 26 的正文与选项；前提见 §3.14 L22 |
| `data/talk/sex/sex_class/join_sex_class.csv` | 1053~1056 | 前提加 `&self_is_player_daughter` |
| `data/talk/sex/sex_class/watch_sex_class.csv` | 1054 / 1055 | 同上 |
| `data/talk/daily/check_report_card.csv` | 新增 2 行 | 成年女儿档位 3（§3.14 L25） |
| `data/target/default/target.csv` | 210810 / 220830 | 说明补翘课日例外（L27） |
| `tools/ArkEditor/csv/Effect.csv` | 557 | 说明改写（L27） |
| `tools/ArkEditor/csv/Premise.csv` | 1896；新增 1 行 | 补翘课日例外；`self_have_public_course` |

## 5. 行为对照

| 情形 | 现行为 | 改后 |
| --- | --- | --- |
| 课上玩家点「结束群交」 | 课堂模式留着，次日学生被拉进没有博士的课堂 | 课上不再显示「结束群交」，只有「结束性技实操课」 |
| 课上玩家体力归零 / 学生全部力竭 / 群交中被撞见 | 课堂模式留着 | 这一步收尾时下课 |
| 只剩一名学生、转为单人 H | 课照上 | 课照上；这场 H 结束时下课 |
| 旧档里已经留下的幽灵课堂 | 永远 running | 玩家下一步（或跨天）收尾 |
| 9/7 出生的婴儿 | 婴儿中期 9 条一条都开不出来，12/1 婴儿 4 / 50 同时进池子 | 每个出生日期都有 12~14 天的中期窗口；4 比 50 早约 3 天开放 |
| 养成事件抬头 | 「萝莉期第 23 天」一夜变「第 85 天」 | 按可游玩天，萝莉期共约 60 天 |
| 女儿第一次生日 | 约 1.6% 的机会见到生日事件 | 当天插队首推入 |
| 毕业典礼选「倾向：坚强」的选项 | 只加倾向值，素质不变 | 按新倾向值重选这一对素质 |
| 病人编号撞上教师 / 母亲的角色 id | 教师整天来不了、母亲不能跟 | 不受影响 |
| 改任厨师的萝莉，日程上午是跟随母亲 | 工作日上午去见学 | 上午上班，晚上的「跟随母亲」照旧 |
| 人已在多媒体室看电影、下一节兴趣课就是看电影 | 整节出勤缺课都不记 | 开课那一刻重新决策，派 716 记出勤 |
| 截短落在玩家这一步里 | 被截掉的那段饥饿、尿意算两遍 | 只算一遍 |
| 23 点睡到次日 10 点，9 点掷中翘课 | 醒来前 flag 被清，余下节次重新掷 | 当天翘到底 |
| 下一节是玩家实操课的学生，上一节的教师晚到开讲 | 下一节多记一节出勤 | 不再记 |
| 实操课提前下课、体力 20% 的学生本节内回到 AI | 同一节出勤又缺课 | 只有出勤 |
| 下课后同一节重开预约课 | 没修过理论的必修生被拉进课、不记出勤 | 开课前就算必修，照记出勤 |
| 课中实行值跌破门槛的成年学生 | 拿不到旁观收益 | 仍按课堂成员照拿 |
| 不够格的选修生到场 | 开课前到零收益，开课后到自习计出勤 | 都自习、计出勤 |
| 课堂模式下的群交模板选人 | 场上任何人都能选 | 只列课堂成员 |
| 排实操课页点名一名没修过理论的选修生 | 同时列在必修与「不能参加」 | 只在必修行 |
| 玩家在节次外手动授课 | 学生听课口上一句不出，`<课>` 写课表 | 按学识口上，`<课>` 写博士 |
| 翘课后的空节 / 必修实操课上 | `<翘>` 亮 | 不亮 |
| 翘课的学生在实操课上撞见博士 | 被判翘课被抓 | 不判 |
| 体育课地点缺课休息 | `<课>` 亮 | 不亮 |
| 自习的 `<课>` 悬停 | 「经验减半」 | 「按自习收益」 |
| 婴儿期入队、长成幼女后才处理的事件 | 以「幼女期」抬头弹出 | 长大时清掉 |
| 外勤中的女儿套着被删的模板 | 回岛后套上新模板 | 删模板时一并解开 |
| 成年干员当过学生、改岗后 | 每晚照模板读书 | 按随机娱乐 |
| 婴儿午夜后入睡长成幼女 | 当天娱乐是成年池 | 幼女默认池 |
| 改岗萝莉靠工作升级料理 | 下次见面炫耀课堂 | 不记待炫耀 |
| 被监禁的教师 | 格子照常、一键排课会排她 | 标「（被监禁）」、不排 |
| 学期切换那一夜的萝莉 | 期末事件与萝莉 1 / 20 / 26 同时入队 | 只有期末事件（三条并入期末池） |
| 萝莉抽到通用 15 | 「被人抱着从一个部门送到另一个部门」 | 只派婴儿 / 幼女 |
| 幼女第一次上实操课 | 「第一次来」约 3% | 与女儿行同权重 |
| 成年女儿整学期没排课，检查成绩单 | 没有口上 | 档位 3 专属口上 |
| 只排理论课的萝莉 | 抽得到实践课 / 训练场 / 公开课事件 | 只抽得到自己有的课型 |

## 6. 风险与注意事项

| 风险 | 说明 | 对策 |
| --- | --- | --- |
| M1 改了阶段进度的单位 | 全部 Growth\|3 窗口的开放日期都变；抬头天数变小；养成总览同源 | 窗口百分比不动；`test_growth` / `test_growth_event` 按季月出生日重写夹具（§2.5-4），断言 122 个出生日期都开得出婴儿中期 |
| M3 让成年后的倾向改写素质 | 成年后事件选项可能把已定型的素质翻到另一侧 | 这正是选项提示的本意；倾向为 0 时两侧都不动；只对已成年的女儿生效 |
| H1 以「玩家不在 H」判下课 | 若有别的系统在课中临时清掉玩家的 H 标记，课会被收掉 | 全仓库清玩家 `is_h` 的都是结束 H 的效果；`test_sex_class` 覆盖 6008 隐藏、体力归零、全员力竭、转单人 H 后结束 H、旧档幽灵课 |
| L4 改了行为循环主干的顺序 | NPC 分支里截短挪到实时结算之前 | 只挪学生截短一段，守卫与判据不变；`test_behavior_loop` 与探针的收敛、出勤不变 |
| L7 让 `settle_attend` 写 `last_attend_period` | 同一节实操课之后，557 / 512 不再给她结算这一节的常规课 | 同一节只落一种记录（Plan 30 口径）；实操课本身已记出勤 |
| L10 改变了开课前到场的不够格选修生 | 从零收益改为自习、计出勤 | 与开课后到场的现行为一致；成绩单出勤率略升 |
| L22 删掉三条萝莉事件的 uid | 旧档队列里的萝莉 1 / 20 / 26 会被清理掉，履历照留 | `clean_official_event_queue` 静默清掉失效 uid；新 uid 在期末池 |
| L24 给 6 行口上加女儿前提 | 萝莉化世界里的非女儿萝莉学生不再有这 6 行 | 萝莉化是建角时的一次性设定，学生口上仍有其余通用行 |
| 事件表与口上是编译产物 | 改 CSV 后要重建 | 测试引导的增量构建会重建；口上改动后先删 `data/Character_Talk.json` 再 `buildconfig.py`（README） |
| 构建会写乱 PO | 本机无 gettext | 收尾 `git checkout -- data/po/` |

## 7. 不在本方案范围

- **行为循环「交互对象不在场即把结束时刻改写为这一步的结束」**：见学的对象是母亲，见学跨过玩家一步的边界、下一步里母亲先决策离开时，孩子的时间线跳到这一步的末尾，中间的节次不计出勤也不记缺课（核实代理确认成立，触发要求较窄）。这条规则作用于全部带对象的行为（聊天、H 等），改成「取原结束与这一步结束的较早者」属行为循环主干
- **一步跨过两个午夜只跑一次跨天结算**（`new_day_flag`）：属行为循环主干，与 Plan 31 §7「换季首日」同类
- **婴儿 4 与婴儿 50 的严格先后**：M1 之后两条相隔约 3 个可游玩日开放，仍可能先后颠倒；严格先后要「某事件已触发」的前提，本轮不做
- **公务事件出队复核事件前提**：M2 只处理生日正文；季末入队、新学期才处理的通用 15 等同类时效问题属公务事件系统
- **口上 / 事件校验的防复发规则**（运算符白名单、编号白名单、sub_key 值域）：现有数据没有实例，留作工具改进
- **成年（非女儿）学生的听课、翘课口上**：总纲 §5、§10.2
- 既往各轮 §7 的范围外事项（口上占位行机制、日程自习没有专属口上、换季首日一步睡过上课时间、一键排课替换离岗教师、别的前提调实行值计算会扣理智、游泳不换泳衣、读书系统、身体管理的练习类、成长停滞后一次长大、保育员前提写死 153、总纲 §10.2 五条备忘、成绩单另列翘课节数等）
- Plan 24~31 留给用户的游戏内测试项

## 8. 追加调整

（实施后每轮追加一节，只写设计；实施记录见实施文档 §6.5。暂无）
