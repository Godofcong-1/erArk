# Plan 26（方案）：生长养成系统第七轮复查

> 本 Plan 拆分为两个文件：**本文件为纯方案**（发现、现状调查、设计决策、接口设计、风险、范围外）；
> 逐文件改动步骤、构建、验证清单、回滚与实施过程记录见 `plan_26_生长养成系统第七轮复查_实施步骤与记录.md`（下文简称"实施文档"）。
>
> 本 Plan 是 Plan 22（生长养成系统）、Plan 24（师生并入工作链）、Plan 25（第六轮复查）之后的又一轮全面复查，三者均在 `plan/done/`。
> 实施完成后在 Plan 22 总纲追加 §12，只写一行指向本 Plan。

- 状态：**已实施**（2026-09-12；方案同日定稿，同日按用户改判修订胎教折珠 §3.2、新增技巧门槛 §3.12；实施中的偏离见实施文档 §6.1，已回写 §3.5 / §3.11 / §4.2）
- 来源：用户需求 → "该系统已经实现完成了，进行一次检查，检查该系统是否有哪里仍有遗漏的未实现内容、BUG、死代码、待处理项等。依然仅由主代理调查和进行，不使用子代理进行"
- 已确认的设计决策（2026-09-12 用户拍板）：
  1. **性技科目的教室课改发理论经验**：理论 / 实践 / 公开课与自习，对性技科目发 `Experience.csv` 里类型 12 的理论经验（170~176）；没有对应理论经验的科目只给习得、不给经验（§3.1）
  2. **胎教出生转写改发习得珠、不再发任何经验**（同日改判，取代「只转 10 门技能」）：胎教值在出生时按比例折成习得珠，17 种经验一律不给；比例由方案定为每点 10 珠（§3.2）
  3. **课堂模式下的邀请按实操课门槛筛**：名单只列能参加实操课的人，到场走课堂的入课流程并记出勤（§3.3）
  4. **期末事件只给幼女 / 萝莉**：成绩单照旧（Plan 24 §3.10 定过改岗期间照出）；「无课可评」的不推带课堂情景的那条（§3.4）
- 按推荐处理、未单独询问的口径（实施前如有异议再改方案）：
  5. 同胞互动的对象只取幼女 / 萝莉；17 条不适合婴儿的通用事件补上排除婴儿的前提（§3.9）
  6. 课堂 H 只收学生岗：`judge_can_join_sex_class` 增加学生岗条件，是 Plan 24 口径 1「课表只对学生岗生效」的延伸（§3.10）
  7. 未成年且一门性技都没学会时不自动升「技巧」：否则出生时折的胎教珠在孩子第一次过夜结算时就先被技巧拿走 100 个，上学攒的珠现在也是这样（M7，§3.12）
- 预计改动量：**约 34 个文件**，净增约 480 行、删除约 100 行
  - 数据 5 个：`target.csv`（改 1 行、增 1 行）、`InstructConfig.csv`（改 1 行）、`data/official_event/通用.csv`（改 17 行）、`期末.csv`（改 1 行）、ArkEditor `Premise.csv`（增 1 行）
  - 常量 2 个：`education_constant`、`constant_promise`
  - 逻辑约 18 个；测试约 10 个；文档 2 个（说明文档、`update.log`）
- 风险等级：**中低**（核心改动是结算口径与几处判定的收紧，不新增 AI 状态；唯一碰到 AI 高优先链的是 target 505 / 515 的互斥，由 lint 与测试兜底）
- 适用代码快照：`master @ 208352d0c`（Plan 25 提交之后）
- 前置：Plan 22 一~四期、第五轮复查、Plan 24、Plan 25 均已完成

---

## 1. 目标

1. 性技科目的教室课与自习不再发真实性交经验、不再补记初体验履历；改发对应的理论经验，腰技只给习得
2. 新生儿不再带着任何经验出生：胎教改为出生时折成习得珠，给的是「学得快」而不是「已经会」；未成年女儿不再凭攒下的珠白拿「技巧」
3. 实操课进行中的「邀请」遵守实操课的参加门槛，受邀者到场后与按课表来的学生待遇相同
4. 已成年的女儿不再被推期末事件；没排课的学期不推带课堂情景的期末事件
5. 提前几分钟在预约的教室开课，开的就是预约的那节
6. 当天的临时实操课不再遮住每周课表：排课撞课判定照每周课表判，格子上看得出哪格被临时课顶替，「清空本格」清的是什么写清楚
7. 玩家在别的教室手动授课，结算、`<课>` 标识与口上都不再读到临时实操课的科目
8. 体育 / 兴趣 / 实习课的场所未开放、兴趣课的活动条件不符时，不再派人去空转，面板上也能看出来
9. 小修：同胞与婴儿事件、改岗女儿进课堂、临时课跨教室覆盖、成年后的待炫耀、婴儿检查成绩单、母亲睡觉时的见学、过期注释与死参数

**验收标准**：
- 全套回归测试通过，新增断言覆盖 §3 每一条；复现脚本（实施文档 §2.0）改前全部命中、改后全部不命中
- `lint_target_csv.py` 完整模式通过；`tools/official_event_check.py` 通过
- 行为循环测试收敛，出勤人均 ≥ 3 节不变

## 2. 现状调查

本轮读过的范围：`Education_System/` 全部 16 个模块；外部挂接点 `handle_npc_ai`（`find_character_target`、`judge_interrupt_character_behavior`、`get_chara_entertainment`）、`StateMachine/default.py` 的 561 / 562 / 303 / 304 / 713~722、`Settle/default.py` 的 512 / 548~557 / 555 / 556 / 10014 / 10015、`Second_effect` 622 / 623、`second_behavior`、`handle_ability`、`past_day_settle`、`realtime_settle`、`common_default` 的经验写入、`settle_behavior`、`handle_premise` 的 CVP 与 H / other / work / place / time 前提、`character_info_head`、`handle_instruct` 的授课 / 开课 / 下课、`group_sex_panel`、`pregnancy_handle`、`born_event_panel`、`official_event_handle`、`save_handle`、`map_handle` / `character_move` 的通行判定；数据 `target.csv`、`WorkType.csv`、`Entertainment.csv`、`Facility_open.csv`、`Experience*.csv`、`AbilityUp.csv`、`InstructConfig.csv`、`Behavior_Data.csv` / `Behavior_Effect.csv`、`data/official_event/` 五张表。胎教改判时补读 `sleep_settle`（换珠与夜间升级）、`attr_calculation.get_juel`、`character_handle.born_new_character` / `get_new_character`、`pregnancy_handle._settle_baby_grow_up`、`body_info_panel`、`growth_panel`，数据 `Ability.csv`、`System_Setting.csv`。

基线：回归 15 个文件 903 条断言全绿；死代码扫描 Education_System 358 个函数 / 常量无零引用；代码无 TODO。
下表的「已复现」都由 scratchpad 脚本在无头环境跑出（不入库，实施文档 §2.0 要求重建），「读代码」只有代码证据。

### 2.1 发现（高）

| # | 发现 | 证据 | 状态 |
| --- | --- | --- | --- |
| H1 | **性技科目的教室课发真实性交经验**。`settle_student_class_gain` / `settle_teacher_class_gain` 按 `get_subject_exp_id` 发科目经验，而性技科目在 `AbilityUp.csv` 里解出的是真实性交经验：指技 41 手交、舌技 42 口交、足技 44 足交、胸技 43 乳交、膣技 61 阴道性交、肛技 62 肛肠性交、腰技 60 插入、榨精 24 精液。师生两侧都拿；舌技课经 `common_default` 的「补记口交初体验」钩子，给幼女记下一条地点在教室的口交履历。与一期方案 §3.1、总纲 §2.3-11 推论二「理论课只能攒珠、课堂给不了」相反，一期实施记录第 387 行「零特判落实」的结论不成立。一键排课均衡铺 17 门，实测 45 格里 15 格是性技 | `growth_handle.py:286`、`:335`；`common_default.py:973~982`；`AbilityUp.csv:242~` | 已复现（舌技课师生都被记口交初体验；膣技自习发 E61） |
| H1b | 胎教出生转写覆盖 `FEMALE_SUBJECT_LIST` 17 门（含 7 门性技），新生儿带着 17 种经验出生：对话 / 指挥 / 战斗 / 学识 / 料理 / 音乐 / 医疗 / 农业 / 制造 / 绘画，以及手交 / 口交 / 乳交 / 足交 / 阴道性交 / 肛肠性交 / 精液，满胎教各 50 点。升级比的是经验总量、不扣经验，单看经验已够到话术 1、料理 2、战斗 / 音乐 / 学识 / 医术与 7 门性技 3、指挥 / 农业 / 制造 / 绘画 5 级；常量注释「落在 2 级附近」是把各级门槛当成累加算的。四期按设计验收过，本轮用户改判：孕期的胎教不该变成任何经验 | `baby_growth_handle.py:124`；`education_constant.py:351~354`；四期实施记录 §4 第 522 行 | 已复现（满胎教新生儿 17 种经验各 50） |

### 2.2 发现（中）

| # | 发现 | 证据 | 状态 |
| --- | --- | --- | --- |
| M1 | **提前几分钟开预约的实操课，会另开一节当场课**。开课按「当前节次」找预约（`get_class_period_by_time(cache.game_time)`），而学生按设计开课前 10 分钟到场，玩家这时开课正落在上一节（或午休 / 早上的 -1）。后果：重新问主修；`get_must_attend_set` 只认当前节次，必修生被当成没修过性技课，开课时不拉、之后判不成 JOIN、在课堂 H 旁边自习；按预约时刻下课被判「拖堂」；下课后当场课被删、预约那条仍有效，覆盖层继续把那一节指向玩家 | `sex_class_handle.py:647`、`:224`；`handle_instruct.py:1660` | 已复现 |
| M2 | **课堂模式下的「邀请」绕过实行值**。邀请名单在 `sex_class_mode` 下跳过实行值、列出全岛不在场的干员；`invite_npc` 只看 normal_24567 与力竭；受邀者到场经 target 505（`group_sex_mode_on`，课堂模式同样成立）→ 状态机 96 → 行为 376（效果 462 自身进 H）。注释说「成年干员的门槛另判」，这条路没判；也不记出勤、不走实操课的到场口上 | `group_sex_panel.py:739~744`、`:822~846`；`target.csv:15` | 读代码 |
| M3 | **当天的临时实操课遮住每周课表**。①`get_teacher_cell` 对被顶掉的格子跳过（第五轮为「教师这节不用来」加的），`judge_teacher_conflict` 复用它，于是被顶掉的教师在排课面板与一键排课里判「不撞课」，一键排课实测把她在每周课表同一节排进两间教室；②格子显示的是临时课，`_edit_cell` 的「清空本格」删的是底下看不见的那节每周课 | `schedule_handle.py:208`、`:494`；`auto_schedule.py:71`；`class_schedule_panel.py:323`、`:389`、`:695` | 已复现 |
| M4 | **玩家手动授课读到临时实操课的科目**。`get_teacher_cell(0)` 只要今天该节有临时课就返回它，不看玩家在哪；512 取 `get_now_teaching(0)`，玩家在理论教室授课时，学生拿到指技的经验（按 M3 的同一覆盖层）。`<课>` 标识与 CVP `Course` / `CourseType` 同源 | `Settle/default.py:7595`、`schedule_handle.py:202` | 已复现（512 实跑） |
| M5 | **个人式课不看场所是否开放**。`get_course_place` 只查静态的 `constant.place_data`；未解锁的场所照样解析出来。体育课排在未解锁的游泳池：学生从教育区入口一路走到门口（训练\淋浴），此后每分钟派 715、寻路因 `wait_open` 失败退成等待 1 分钟，整节空转。面板上的「（未开放）」依赖同一个函数，永远不会出现。咖啡馆 / 茶馆 / 蛋糕店 / 街机厅（基建建设）、健身区、黄澄澄游戏室、温室、外交办公室同理 | `schedule_handle.py:536`；`course_select_panel.py:484`；`map_handle.py:601`；`character_move.py:118~141` | 已复现（行走模拟 12 步） |
| M6 | **兴趣课不校验活动 need**。选目标只看 `class_ok`；过家家（`T102\|1/T103\|1`）能排给少女 / 成年学生，716 照常执行 | `course_select_panel.py:503`；`StateMachine/default.py:2829` | 已复现 |
| M7 | **未成年女儿攒够 100 个习得珠当晚就升「技巧」1 级**。技巧（能力 30）0→1 级只要 `J9\|100`，额外条件「全子性技等级和 ≥ 技巧等级 × 3」在 0 级时恒成立；`gain_ability` 按 `Ability.csv` 行序遍历，技巧排在全部科目之前，珠又是通用的，所以上学 / 见学攒下的头 100 个珠总是先给了技巧。「H 结束、博士入睡时自动升级干员能力」默认开（`System_Setting.csv:7`）。H1b 改发习得珠后，胎教珠会在孩子第一次过夜结算时被同样拿走 | `AbilityUp.csv:104`；`handle_ability.py:70~105`、`:165~177` | 已复现（萝莉 150 珠、无任何经验 → 技巧 1、剩 50 珠；给到 5000 珠仍停在 1） |

### 2.3 发现（低）

| # | 发现 | 证据 | 状态 |
| --- | --- | --- | --- |
| L1 | 养成事件的同胞互动对象含婴儿（双胞胎婴儿也会互点）与少女：`get_sibling_child_list` 只看有无阶段素质。`sub_key=0` 的通用事件里有 17 条写的是会走会说的孩子，没挡婴儿（通用 3、4、5、9、23、25、29、39、42~45、49~53；其余如 11~14、20~22 等已带 `CVP_A1_T\|101_E_0`） | `growth_event_handle.py:68`；`通用.csv` | 已复现（婴儿候选含通用 3 / 5 / 23） |
| L2 | 已成年、已改岗的女儿每学期照出「无课可评」成绩单并被推期末事件；期末 13（「教室里没剩几个人…收拾东西」）没有档位前提，没排课的也会抽到 | `semester_handle.py:331`；`past_day_settle.py:111~113`；`期末.csv:18` | 已复现 |
| L3 | 改了岗的女儿人在实操教室，会被 `get_scene_student_list` 拉进课堂 H（女儿零门槛、前置修习看的是残留课表），Plan 24 口径 1 没管到这里 | `sex_class_handle.py:275`、`:299` | 已复现 |
| L4 | 临时课的键是「日期-节次」，不含教室：编辑 B 教室格子时会带出 A 教室同一节的预约并在确定时把它挪过来；在别的教室当场开课会静默覆盖那条预约 | `class_schedule_panel.py:409~413`；`sex_class_handle.py:649~659` | 读代码 |
| L5 | 成年当晚的升级留在 `show_off_ability` 里（萝莉期记的），见面时二段炫耀静默发好感（炫耀口上只写幼女 / 萝莉） | `pregnancy_handle.py:650`；`second_behavior.py:329` | 读代码 |
| L6 | 「检查成绩单」（1036）的前提只有 `TARGET_IS_PLAYER_DAUGHTER`，婴儿也能查 | `InstructConfig.csv:60` | 读代码 |
| L7 | 见学的「母亲有效」不看睡觉：母亲睡着时幼女也会去她宿舍「见学」并按岗位科目拿经验 | `class_ai.py:542` | 已复现（实施前：母亲睡着时 `judge_mother_available` 仍返回母亲） |
| L8 | 过期文字与死参数：`get_student_candidate_list` 注释仍写「指定必修学生」「面板用 [0] 回落」，`get_course_candidate_list` 同写 [0] 回落；说明文档 §15-5 同样过期；`get_upcoming_course` 的 `now_time` 参数无人传入（Plan 25 初稿 `judge_student_should_leave_now` 的遗留），注释「学生的打断规则传当前游戏时间」也过期；开课前 30 分钟的提醒写「学生们已经在往教室走了」，实际开课前 10 分钟才动身 | `growth_handle.py:62~77`、`:104`；`生长养成系统.md:272`；`schedule_handle.py:379~389`；`sex_class_handle.py:561`；`realtime_settle.py:205` | — |

### 2.4 可复用的既有实现

| 需求 | 现成实现 |
| --- | --- |
| 理论经验 | `Experience.csv:132~138`：170 手交 / 171 口交 / 172 足交 / 173 乳交 / 174 性交 / 175 肛交 / 176 榨精理论经验，类型 12（`Experience_Types.csv`：「针对各种性交行为和技巧的理论知识」）。**全仓库没有任何发放方，也不在任何升级需求里** |
| 场所开放判定 | `schedule_handle.judge_classroom_open`（按场景名查 `facility_open`，不在表里的恒开放）；`map_handle.judge_scene_accessible` 的 `wait_open` 分支同口径 |
| 娱乐 need 校验 | `schedule_template_handle.judge_activity_need_pass(character_id, entertainment_id)` |
| 受邀到场 → 进课堂 | `sex_class_handle.pull_student_into_class` + `settle_attend`（状态机 722，Plan 25） |
| 受邀到场 → 取消 | 状态机 97 `STOP_JOIN_GROUP_SEX`：清 `go_to_join_group_sex`、等待 1 分钟（`StateMachine/default.py:2243`） |
| 交互对象婴儿前提 | `handle_premise_other.py:3472 handle_t_baby_1`，只有 `==1` 没有 `==0` |
| CVP 运算符 | `G / L / E / GE / LE / NE` 都支持（`handle_premise/__init__.py:617~633`） |
| 习得珠 | juel 9（`education_constant.LEARN_STATE_ID`）。`sleep_settle.settle_character_juel` 把当天攒的习得状态折珠，450 以内 1:1、之后递减（`attr_calculation.get_juel`）；实测一节学识理论课（教师 3 级、学生 0 级）131 珠、一节自习 73 珠 |
| 能力升级的额外条件 | `handle_ability.extra_ability_check`：夜间自动升级与能力面板（`ability_up_panel.py:522`、`:598`）共用，面板上的说明文字也在这里拼 |

### 2.5 已知陷阱与硬约束

1. **前提必须是纯函数**（Plan 24 §2.6-1）：新判定不写数据、不惰性创建养成数据
2. **target type 0 按权重随机**，不是取第一条：505 与新行 515 必须靠前提互斥（`sex_class_mode_off / on`），不能靠行序
3. **理论经验不参与升级**：`AbilityUp.csv` 里性技的升级需求仍是真实性交经验，改后「理论课攒珠 + 理论经验、实操课给真实经验，两者都够才升级」，与口径 5 一致
4. **存档里已攒下的经验与初体验记录分不出来源**，不回溯清理（§6）
5. **测试构建会写乱 PO**：跑完 `git checkout -- data/po/`
6. **编号**：状态机不新增（722 泛化复用）；target 类型 0 组 5 已用到 510，515 空闲；前提新增 `t_baby_0`
7. **习得珠先到先得**：`gain_ability` 按 `Ability.csv` 行序遍历、珠是通用的，技巧（30）排在全部科目（40~）之前，只要珠就能升的都先被它拿走（M7）
8. **婴儿不参与每晚结算**：`born_new_character` 不把新生儿加进 `npc_id_got`（`character_handle.py:199` 那行是注释），成长为幼女时才经 `_settle_baby_grow_up` → `get_new_character` 上线（`pregnancy_handle.py:560`）；换珠与自动升级只遍历 `npc_id_got`（`sleep_settle.py:45`）。出生时发的珠整个婴儿期都不会被花掉

## 3. 设计决策

### 3.1 性技科目的教室课改发理论经验（H1，决策 1）

新增统一取数口 `growth_handle.get_class_exp_id(ability_id)`：性技科目查 `education_constant.SEX_SKILL_THEORY_EXP_ID`，其余科目照旧 `get_subject_exp_id`。
`settle_student_class_gain` 与 `settle_teacher_class_gain` 改走它；取不到（腰技）就只结算习得、不结算经验。

| 入口 | 改后 |
| --- | --- |
| 理论 / 实践 / 公开课（512、557） | 学生：习得 + 理论经验；教师：习得 + 理论经验（教学相长同一口径） |
| 自习（548） | 同上（学生侧） |
| 实习课（552）、见学（553） | 不变：科目是岗位能力，都不是性技 |
| 实操课主修加成（`get_now_bonus_exp_id`）、旁观（口径 67） | 不变：那是真实的课堂 H |

映射写成常量表而不是从配置推：

| 候选 | 弃选原因 |
| --- | --- |
| 按经验名配对（「X经验」→「X理论经验」） | 阴道性交 → 性交理论、肛肠性交 → 肛交理论、精液 → 榨精理论三对名字对不上 |
| `Ability.csv` 或 `Experience_Relations.csv` 加一列 | 为 7 个值改表结构、重生成 `config_def.py`；关系表按部位基础经验建键，放不下科目 |
| 类型 12 按 id 排序后与性技科目逐个配对 | 顺序一变就串，出错时无声无息 |

常量表由测试守住：值的经验类型必须是 12、键必须是性技科目、女学生可学的 7 门都有映射。

### 3.2 胎教出生转写改发习得珠（H1b，决策 2）

`settle_prenatal_to_child` 不再写任何经验，改为给每个新生儿的 `juel[LEARN_STATE_ID]` 加「胎教值 × `PRENATAL_JUEL_PER_POINT`」个习得珠（向下取整）。其余不变：`child_growth.prenatal_point` 照记，多胎各自全额，全部孩子创建完再清零母亲侧，孕期三条指令的当场效果（孕妇的好感、信赖、快乐，抚摸另加好意）不动。

**比例取 10**：每次胎教折 5 珠，满值 100 点折 1000 珠。

| 对照 | 习得珠 |
| --- | --- |
| 一节学识理论课（实测，教师 3 级、学生 0 级） | 131 |
| 一天 6 节同样的课（按实测单节折算） | 约 707 |
| 10 门技能各从 0 升 1 级要花的珠（9 × 70 + 话术 100） | 730 |
| 满胎教（做满 200 次，共 100 小时） | 1000 |

珠是通用的学习资源，经验是分科的知识：满胎教的孩子「学得快」，但每门课仍要自己攒经验才升得上去，与「孕期谈不上学会什么」一致。

| 候选 | 弃选原因 |
| --- | --- |
| 比例 5（满值 500 珠） | 200 次、100 小时的胎教还抵不上 4 节课 |
| 比例 20 以上（满值 2000 珠起） | 够好几门从 1 升到 2 级（每门 400 珠），开学头几天的进度由胎教主导 |
| 折成习得状态值，等当晚睡眠结算再换珠 | 满值落进递减段，折出来不足 1000；何况婴儿根本不进睡眠结算 |

- 直接写 `juel`：出生时没有行为，不记变更记录（沿用旧转写直接写 `experience` 的理由）
- 花珠的时机：婴儿不参与每晚结算（§2.5 第 8 条），这些珠整个婴儿期不动；成长为幼女上线后的第一晚才开始花，届时婴儿期被照料攒下的技能经验（唱儿歌、教说话、给玩具）会先兑现成 1 级。技巧不再抢珠见 §3.12
- 显示：生产面板「…底子比别的孩子好一些：获得了 N 个习得珠」；母亲身体信息面板「已做过 N 次胎教，孩子出生时可获得 M 个习得珠」；养成总览的胎教底子行「孕期听过 N 次胎教，出生时带来 M 个习得珠」。珠名取 `game_config.config_juel[LEARN_STATE_ID].name`，不写死
- 折出 0 珠的那句文本（「还不足以留下什么」）保留：按现行比例 0.5 点也有 5 珠，只有调低比例才会走到
- 顺带：`SUBJECT_ABILITY_LIST`、`FEMALE_SUBJECT_LIST` 的注释去掉「胎教转写」这一用途；`CHILD_GROWTH.prenatal_point` 的注释删掉从未实现的「参与初始资质计算」；同日版本计划新增的 `SKILL_SUBJECT_LIST` 不再需要，`get_career_suggestion_text` 不动

### 3.3 课堂模式下的邀请（M2，决策 3）

- **名单**：`show_invite_npc_panel` 在 `sex_class_mode` 下改判 `sex_class_handle.judge_can_join_sex_class(chara_id, check_course=chara_id not in 必修名单)`，其余情形照旧判「群交」实行值
- **到场**：
  - target 505 的前提加 `sex_class_mode_off`
  - 新增 `515,722,self_now_go_to_join_group_sex|place_0|sex_class_mode_on,0,…`
  - 状态机 722 泛化：先清 `go_to_join_group_sex`；到场那一刻不再满足 `judge_can_join_sex_class` 就按 97 的写法等待 1 分钟收场，满足才 `pull_student_into_class` + `settle_attend`
- 结合 §3.10，邀请名单实际只剩「没到场的学生岗」，与课堂的语义一致

| 候选 | 弃选原因 |
| --- | --- |
| 课堂模式隐藏邀请按钮 | 用户选了按门槛筛 |
| 新开状态机 723 | 与 722 的动作完全相同，只多一个清标记 |

### 3.4 期末事件只给幼女 / 萝莉（L2，决策 4）

- `push_semester_event_for_list` 跳过阶段不在 102 / 103 的孩子；成绩单与 `report_card_flag` 照旧
- 期末 13 的前提填 `CVP_A1_Growth|7_NE_3`（上一份成绩单不是「无课可评」）；期末 14「下学期的课表要重排了」、15、16 对没排课的孩子也说得通，不动

### 3.5 提前开预约的实操课（M1）

新增 `sex_class_handle.find_reserved_class(classroom, now_time) -> (键, 课程)`：在今天的临时课里找**这间教室**、未开始、未下课、且「就是当前节次」或「开始时刻在 `NOTIFY_BEFORE_MINUTE`（30 分钟）之内」的那条，当前节次优先。

| 调用方 | 改为 |
| --- | --- |
| `start_sex_class` | 经 `find_class_to_start` 找：先是它找到的预约，其次本节同一间教室已下课的那条（下课后再开，复用而不另建）；找到就复用（`running`、`reserved`、清 `ended`）。找不到时，若当前节次的键被**别的教室**未开始的预约占着，把那条挪到这间教室（L4，决定在这里上）；都没有才新建当场课 |
| `handle_start_sex_class` 预读主修 | 同一个查找（`find_class_to_start`），预约过的就不再问 |
| `get_must_attend_set(classroom="")` | 有进行中的课取它；否则取这间教室 `find_reserved_class` 找到的那条；`get_scene_student_list` 传入玩家所在教室 |
| `judge_end_type` | 不改：键的节次就是预约的节次，自然按预约时刻判档 |

配套：学生处于 SEX_PENDING 且那节课已提前开讲、人已在那间教室、能参加时，`get_course_stage` 直接给 JOIN，不再原地等到开课那一刻才入课（判定抽成 `class_ai.judge_pending_class_joinable`）。开课与预读主修取「玩家所在教室名」共用 `sex_class_handle.get_scene_name`。

### 3.6 每周课表与当天临时课的覆盖层（M3、L4）

- `get_teacher_cell(teacher_id, week_day, period, include_temp=True)`：`judge_teacher_conflict` 传 `include_temp=False`，撞课一律照每周课表判；工作链、`get_now_teaching` 仍用默认值（被顶掉的教师当天照样不用来）
- 全局课表格子：被临时课覆盖的格子在文字前加「[临]」
- 选科目页：覆盖格多一行说明「今天这一节由临时实操课（主修 X）顶替；每周课表这一格：Y/Z」，「清空本格」改名「清空每周课表这一格」；临时课仍从「排一节性技实操课」进去改或删
- 排实操课页：该日该节已在别的教室排了实操课时，多一行「该节已在 A 排了实操课，确定后改到本教室」

### 3.7 玩家手动授课（M4）

`get_now_teaching(0)` 只在玩家就在那节临时课的教室里时返回它，否则 None：512 回落「学识 + 按所在教室判课型」（说明文档 §3 的原口径）；`<课>` 标识与 CVP `Course` / `CourseType` 同源跟上。玩家在预约的教室里手动授课，照旧按那门性技讲，经 §3.1 只发理论经验。

### 3.8 个人式课的场所开放与 need（M5、M6）

- `schedule_handle.judge_scene_open(scene_name)`：`judge_classroom_open` 的通用版（场景名在 `Facility_open` 表里就查 `facility_open`，不在表里恒开放），`judge_classroom_open` 保留为它的别名
- `get_course_place`：体育课精确那间房未开放 → []；兴趣课取第一间**开放**的；实习课在岗者所在房间优先（天然开放），其次同名、再其次第一间开放的；都没有 → []。解析不出即「没有行命中，交回既有 AI」（Plan 24 §3.7），不再空转
- `schedule_handle.judge_course_need_pass(character_id, course)`：兴趣课走 `judge_activity_need_pass`，其余恒真。`class_ai.get_course_place_now_or_upcoming` 与截短规则 B 过它，不满足按解析不出处理
- 个人课表面板：体育课的「（未开放）」恢复生效；兴趣课未开放的标「（未开放）」、这名学生条件不符的标「（条件不符）」，均不可选；实习课整组房间都未开放的岗位标「（未开放）」

### 3.9 同胞与婴儿事件（L1，推荐口径 5）

- `get_sibling_child_list` 只收阶段 102 / 103（`education_constant.SIBLING_PLAY_STAGE_SET`）：互动事件写的都是能一起玩的孩子；婴儿期的两条同胞事件（婴儿 37 / 38）主体是婴儿、对手是哥哥姐姐，照样成立
- 17 条通用事件的前提补 `CVP_A1_T|101_E_0`（空前提直接填；已有前提的用 `&` 追加）：3、4、5、9、23、25、29、39、42、43、44、45、49、50、51、52、53

### 3.10 课堂 H 只收学生岗（L3，推荐口径 6）

`judge_can_join_sex_class` 开头加学生岗条件。影响面：开课前提与拉人（`get_scene_student_list`）、旁观名单、`self_in_sex_class`、JOIN 判定、§3.3 的邀请名单；必修名单本来就只列学生岗，不变。

### 3.11 小修（L5~L8）

| # | 改为 |
| --- | --- |
| L5 | `check_grow_to_girl` 成年时清空 `show_off_ability`；`judge_child_growth_second_behavior` 只对 102 / 103 派炫耀 |
| L6 | 新前提 `t_baby_0`（交互对象不是婴儿），1036 前提改为 `TARGET_IS_PLAYER_DAUGHTER\|T_BABY_0` |
| L7 | 新增 `class_ai.judge_mother_followable` = `judge_mother_available` + 母亲不在睡觉（`sp_flag.sleep` 或行为是睡觉）；见学的决策（`judge_follow_mother_state_machine`）、移动 / 跟随两个状态机与 553 见学结算改走它，母亲在睡觉时回落育儿室自由玩耍。`judge_mother_available` 本身不动：它也是公务事件前提 `self_mother_available` 的判据，而养成事件在跨天结算时派发，那时母亲多半睡着（实施中改定，原写法是直接改 `judge_mother_available`，见实施文档 §6.1 偏离 1） |
| L8 | 两个候选名单的注释与说明文档 §15-5 改为现行口径；删 `get_upcoming_course` 的 `now_time` 参数并改注释；提醒文案改为「选修与点名必修的学生会在开课前 10 分钟动身赶来」，`realtime_settle` 注释同步 |

### 3.12 未成年不凭珠白拿技巧（M7，推荐口径 7）

`handle_ability.extra_ability_check` 技巧的 NPC 分支：未成年（素质 7）且全子性技等级和为 0 时判不满足，能力面板的说明多一行「未成年干员至少要有一门子性技达到 1 级」。

- 女儿在实操课里真学会了一门性技，技巧照常按「子性技等级和 ≥ 技巧等级 × 3」升，实操课这条路不受影响
- 成年干员与玩家不变；成年时素质 7 被清（`pregnancy_handle.py:652`），此后回到原规则
- 被挡下的珠留在手里，按行序往后轮到科目时照常花
- 旧档里已经升了的技巧不回退

| 候选 | 弃选原因 |
| --- | --- |
| 所有 NPC 的技巧 0→1 级都要求至少一门性技 | 改动全体干员的成长节奏，超出养成系统 |
| 未成年一律不升技巧 | 在实操课学会了性技却升不了技巧，与实操课的设计相悖 |
| 胎教珠推迟到上学时再发 | 用户定的是出生时转写；也挡不住上学攒的珠被技巧拿走 |

## 4. 接口设计（实施的权威定义）

### 4.1 常量

`education_constant.py`：

```python
PRENATAL_JUEL_PER_POINT = 10
""" 每 1 点胎教值在出生时折成多少习得珠（Plan 26 §3.2，取代按科目发经验的 PRENATAL_EXP_PER_POINT）。
    每次胎教 0.5 点 → 5 珠，满值 100 点 → 1000 珠：比一天 6 节课（按实测单节折算约 707 珠）多一些，
    够 10 门技能各从 0 升 1 级的珠（730），但每门仍要自己攒经验——胎教给的是学得快，不是已经会 """

SEX_SKILL_THEORY_EXP_ID = {70: 170, 71: 171, 72: 172, 73: 173, 74: 174, 75: 175, 77: 176}
""" 性技科目 → 理论经验id（Experience.csv 类型 12）。教室课与自习对性技科目发这里的理论经验，
    不发 AbilityUp 里的真实性交经验（Plan 26 §3.1，用户拍板）；76 腰技没有对应的理论经验，只给习得。
    推不出来：阴道性交 → 性交理论等三对名字对不上，只能列举，由测试守住类型与覆盖面 """

SIBLING_PLAY_STAGE_SET = {102, 103}
""" 同胞互动的对象只取这两个阶段：互动事件写的都是能一起玩的孩子（Plan 26 §3.9） """
```

`constant_promise.py`：`T_BABY_0 = "t_baby_0"`，注释「素质_妊娠 交互对象婴儿==0」，紧跟 `T_BABY_1`。

### 4.2 函数签名

| 模块 | 函数 | 变化 |
| --- | --- | --- |
| `growth_handle` | `get_class_exp_id(ability_id) -> int` | 新增（§3.1） |
| `growth_handle` | `settle_student_class_gain` / `settle_teacher_class_gain` | 科目经验改取 `get_class_exp_id` |
| `baby_growth_handle` | `settle_prenatal_to_child` | 不写经验，改给 `juel[LEARN_STATE_ID]` 加珠（§3.2） |
| `baby_growth_handle` | `get_prenatal_juel_value(prenatal_point) -> int` | 取代 `get_prenatal_exp_value` |
| `baby_growth_handle` | `get_child_prenatal_juel(child_id) -> int` | 取代 `get_prenatal_exp_dict`，养成总览用 |
| `baby_growth_handle` | `get_child_prenatal_count(child_id) -> int`、`get_learn_juel_name() -> str` | 新增：显示胎教次数与珠名（珠名从配置取） |
| `sex_class_handle` | `find_reserved_class(classroom, now_time) -> Tuple[str, Optional[dict]]` | 新增（§3.5） |
| `sex_class_handle` | `find_class_to_start(classroom, now_time) -> Tuple[str, Optional[dict]]` | 新增：预约优先，其次本节同教室已下课的那条（§3.5） |
| `sex_class_handle` | `get_scene_name(scene_path) -> str` | 新增：开课与预读主修取所在教室名 |
| `sex_class_handle` | `get_must_attend_set(classroom="")` | 加参数 |
| `sex_class_handle` | `start_sex_class` | 预约查找与跨教室挪用 |
| `sex_class_handle` | `judge_can_join_sex_class` | 加学生岗条件 |
| `schedule_handle` | `judge_scene_open(scene_name) -> bool` | 新增；`judge_classroom_open` 保留为别名 |
| `schedule_handle` | `judge_course_need_pass(character_id, course) -> bool` | 新增 |
| `schedule_handle` | `get_teacher_cell(..., include_temp=True)` | 加参数；`judge_teacher_conflict` 传 False |
| `schedule_handle` | `get_now_teaching` | 玩家只在那间教室里时返回临时课 |
| `schedule_handle` | `get_course_place` | 过滤未开放场所 |
| `schedule_handle` | `get_upcoming_course(character_id, minute_limit=UPCOMING_MINUTE)` | 删 `now_time` |
| `class_ai` | `get_course_stage` | SEX_PENDING 且已提前开讲、人在教室 → JOIN |
| `class_ai` | `judge_pending_class_joinable(character_id, pending_class, pending_classroom) -> bool` | 新增：上一行的 JOIN 判定 |
| `class_ai` | `get_course_place_now_or_upcoming` / `get_student_leave_time` | 过 need 校验 |
| `class_ai` | `judge_mother_followable(character_id) -> int` | 新增：`judge_mother_available` + 母亲不在睡觉，见学四处改走它；`judge_mother_available` 不变（§3.11） |
| `growth_event_handle` | `get_sibling_child_list` / `push_semester_event_for_list` | 阶段过滤 |
| `handle_premise_other` | `handle_t_baby_0` | 新增 |
| `handle_ability` | `extra_ability_check` | 技巧：未成年且全子性技等级和为 0 时不满足（§3.12） |

### 4.3 数据行

```csv
505,96,self_now_go_to_join_group_sex|place_0|group_sex_mode_on|sex_class_mode_off,0,自己正在前往加入群交，自己在玩家位置，群交模式开启中且不是性技实操课，则加入群交
515,722,self_now_go_to_join_group_sex|place_0|sex_class_mode_on,0,自己正在前往加入群交，自己在玩家位置，性技实操课进行中，则加入课堂
```

`InstructConfig.csv` 1036 的前提列：`TARGET_IS_PLAYER_DAUGHTER|T_BABY_0`。
ArkEditor `Premise.csv`：`t_baby_0,T_BABY_0,素质_妊娠,交互对象婴儿==0`，接在 `t_baby_1` 之后。

## 5. 行为对照

| 情形 | 现行为 | 改后 |
| --- | --- | --- |
| 幼女上一节舌技理论课 | 口交经验 +3×倍率，补记口交初体验（地点教室），教师同样 | 口交理论经验 +3×倍率，不记初体验 |
| 膣技自习 | 阴道性交经验 +1 | 性交理论经验 +1 |
| 腰技课 | 插入经验 | 只给习得 |
| 满胎教的新生儿 | 17 种经验各 50，含手交 / 阴道性交 / 精液 | 不带任何经验；习得珠 +1000（每次胎教折 5 珠），婴儿期不花 |
| 萝莉攒够 100 个习得珠、没学过性技 | 当晚升技巧 1 级 | 不升，珠留给科目 |
| 实操课中邀请 | 全岛任何人不判实行值，到场直接进 H、不记出勤 | 只列能参加的学生岗，到场走入课流程、记出勤；到场时不再满足则收场 |
| 成年女儿的学期切换 | 出成绩单并推期末事件 | 只出成绩单 |
| 没排课的萝莉期末 | 可能抽到「教室里没剩几个人」 | 不会 |
| 9:40 在预约 9:45 的教室开课 | 另开当场课，重问主修，必修生自习，按时下课判拖堂，预约残留 | 就是预约那节 |
| 当天有临时课时给被顶掉的教师排别的教室 | 判不撞课，可排进去 | 判撞课、置灰 |
| 点被临时课盖住的格子「清空本格」 | 静默删掉底下的每周课 | 格子带「[临]」，按钮写明清的是每周课表那格 |
| 玩家在理论教室手动授课、当天别处有临时课 | 按那门性技结算 | 回落学识 |
| 体育课排在未解锁的游泳池 | 走到门口每分钟空转一次 | 解析不出，交回既有 AI；面板标「（未开放）」 |
| 少女排过家家兴趣课 | 照常执行 | 面板不可选；残留的交回既有 AI |
| 萝莉的同胞事件对手 | 可能是婴儿或少女 | 只会是幼女 / 萝莉 |
| 婴儿抽到「探头探脑问你有没有空」 | 会 | 不会 |
| 改岗女儿在实操教室 | 被拉进课堂 H | 不拉 |
| 成年当晚升了级 | 见面静默加好感 | 成年时清掉，不派 |
| 对婴儿用「检查成绩单」 | 可用 | 不可用 |
| 母亲在睡觉时的幼女见学 | 去母亲宿舍见学、拿岗位经验 | 回落育儿室自由玩耍 |

## 6. 风险与注意事项

| 风险 | 说明 | 对策 |
| --- | --- | --- |
| 旧档里孩子已攒下的性交经验与初体验记录 | 分不出是上课来的还是真做过 | 不回溯；说明文档与 `update.log` 写明 |
| 505 / 515 同时成立 | type 0 按权重随机 | 505 加 `sex_class_mode_off`；测试断言课堂 / 普通群交各只命中一条 |
| 课堂邀请名单变空 | 学生多半已按课表到场 | 符合语义；面板照常显示「当前可邀请的干员有：」 |
| 覆盖格的显示变化 | 玩家习惯看到「指技/博士」 | 只加「[临]」前缀，内容不变 |
| 场所过滤影响 `<课>` 标识与截短规则 | 两者都读 `get_course_place` | 同一口径，未开放就既不显示在上课、也不截 |
| `judge_can_join_sex_class` 收紧 | 此前凭实行值到场的非学生成年干员不再能进课堂 | 口径 6 的本意；必修名单本来就只列学生岗 |
| 测试里按旧口径写的断言 | `test_prenatal_baby`「17 门各得 20 经验」「换算：100 点 → 每科 50 经验」等 | 实施文档 §2.10 逐条改写 |
| 旧档里按旧规则出生的孩子 | 已拿到的 17 种胎教经验不回收；养成总览的胎教底子行按现行比例显示珠数，与她当年实际拿到的不符 | 不回溯；说明文档与 `update.log` 写明 |
| 技巧门槛只对未成年收紧 | 已经升了技巧的女儿不回退；成年后回到原规则 | M7 的本意；能力面板写明原因 |
| 构建会写乱 PO | 同前几轮 | 收尾 `git checkout -- data/po/` |

## 7. 不在本方案范围

- Plan 22 总纲 §10.2 的五条备忘：日程改完次日才生效、未来日期的临时课在格子上看不见、成年学生静默翘课、夜间撞见翘课也触发、实习导师不判当班
- 旁观学生按被操作者 25% 领真实性交经验（口径 67，本轮未改）
- 婴儿期照料直接给技能经验（唱儿歌音乐 +8、教说话对话 +8 / 学识 +4、给玩具绘画 / 制造各 +5，`Behavior_Effect.csv:116~120`）：用户这次只改判胎教，照料不动
- 临时课的键改为含教室（存档结构变化；L4 以挪用 + 提示处理）
- 通用事件里口径模糊的几条（如 8、19、35），本轮只改明确不适合婴儿的 17 条
- PO / MO：养成系统的代码词条从未提取进 `erArk_py.po`；CI 只跑 `buildconfig` / `init_data`，不跑 `buildpo` / `buildmo`，前几轮「留给 CI」的说法不成立。需要在装有 gettext 的机器手动跑 `buildpo.py`、`buildmo.py`，否则 en_US / ko_KR 下这些界面显示中文
- Plan 23（公务事件系统）状态已是「已实施」，文档仍在 `plan/wait/`；是否归档、以及说明文档里指向它的路径，由用户决定
- Plan 24 / 25 留给用户的游戏内测试项

## 8. 追加调整

（实施后每轮追加一节，只写设计；实施记录见实施文档 §6.5。暂无）
