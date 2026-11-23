# Plan 28（方案）：生长养成系统第九轮复查

> 本 Plan 拆分为两个文件：**本文件为纯方案**（发现、现状调查、设计决策、接口设计、风险、范围外）；
> 逐文件改动步骤、构建、验证清单、回滚与实施过程记录见 `plan_28_生长养成系统第九轮复查_实施步骤与记录.md`（下文简称"实施文档"）。
>
> 本 Plan 是 Plan 22（生长养成系统）、Plan 24（师生并入工作链）、Plan 25~27（第六~八轮复查）之后的又一轮全面复查，前述各 Plan 均在 `plan/done/`。
> 实施完成后在 Plan 22 总纲追加 §14，只写一行指向本 Plan。

- 状态：**已实施**（方案定稿 2026-09-13，同日实施；实施记录见实施文档 §6）
- 来源：用户需求 → "再进行一次检查，检查该系统是否有哪里仍有遗漏的未实现内容、BUG、死代码、待处理项等。依然仅由主代理调查和进行，不使用子代理进行"
- 已确认的设计决策：用户确认按本方案处理全部问题（2026-09-13「按照该方案处理所有遇到的问题」），下列口径均按推荐实施
- 按推荐处理的口径：
  1. **婴儿期的养成事件照常派发**：每日派发名单与队列容量把婴儿算进来，频率与幼女 / 萝莉相同（§3.1）
  2. **个人式课这一节上不成视为没课**：场所未开放、或兴趣课条件不符时，按「没课」处理，沿用 Plan 27 决策 1「已停课视为没课」的口径（§3.2）
  3. **日程模板不再能选照料卵**，日程改写也不覆盖持卵者当天的照料卵时段（§3.3）
  4. 其余小修（§3.4~§3.9）
- 预计改动量：**约 32 个文件**，净增约 250 行
  - 逻辑 10 个：`growth_event_handle`、`schedule_handle`、`class_ai`、`schedule_template_handle`、`sex_class_handle`、`course_select_panel`、`class_schedule_panel`、`growth_panel`、`character_info_head`、`pregnancy_handle`
  - 注释与数据 7 处：`education_constant`、`constant_promise`、`handle_premise_work`、`growth_handle`、`game_type`、`data/target/default/target.csv`（只改备注列）、ArkEditor `Premise.csv`
  - 测试约 11 个（含 `_bootstrap.py` 与 README）；文档 4 个（说明文档、妊娠系统文档、`update.log`、Plan 22 总纲）
- 风险等级：**低**。婴儿开始收到养成事件是本轮唯一的玩法可见变化；复现脚本已在真实出生的婴儿身上逐一结算了全部 60 条可派事件的 182 个选项，0 报错。`get_course_at` 的改动与 Plan 27 同一收口方式，由测试兜底
- 适用代码快照：`master @ ef865f8d1`（Plan 27 提交之后）
- 前置：Plan 22 一~四期、第五轮复查、Plan 24~27 均已完成

---

## 1. 目标

1. 婴儿期的养成事件真的会派出来：婴儿桶 50 条，以及通用桶里婴儿能抽的那些
2. 个人式课这一节上不成（场所未开放、长大后不满足兴趣课的条件）时：不记缺课，不翘课，日程安排的自习不多记出勤，幼女照常见学；个人课表上看得出来这一格上不成
3. 日程模板不能再给孩子排「照料卵」；持卵者当天的照料卵时段不被日程改写冲掉
4. 小修：
   - 排实操课页的选修人数只数学生岗
   - 必修名单的顶替标记与实际覆盖对得上
   - 养成总览写明待查看的是哪个学期的成绩单
   - 日程安排的自习不显示成「上课中」
   - 过期注释
   - 测试夹具与真实婴儿对齐

**验收标准**：
- 全套回归测试通过，新增断言覆盖 §3 每一条
- 复现脚本（实施文档 §2.0）在改前全部成立。改后，其中 19 项问题命中不再成立；其余 13 项是前提、对照与范围外，仍成立
- `tools/official_event_check.py`、`tools/lint_target_csv.py`、口上前提校验（`test_talk_data`）通过
- 行为循环测试收敛，出勤人均 ≥ 3 节不变

## 2. 现状调查

本轮读过的范围：
- **`Education_System/` 全部 15 个模块**：逐行重读
- **外部挂接点**：
  - `handle_npc_ai`：`find_character_target` 的见学 / 工作 / 娱乐三段、`npc_auto_work_or_entertainment`、`judge_interrupt_character_behavior`、`get_chara_entertainment`
  - `StateMachine/default.py`：561 / 562 / 303 / 304 / 713~722，以及照料卵 427
  - `Settle/default.py`：512 / 548~557 / 555 / 556 / 10014 / 10015 / 上线与离线
  - 结算相关：`Second_effect` 622 / 623、`second_behavior`、`handle_ability`、`past_day_settle`、`realtime_settle`、`common_default` 的主修加成钩子、`settle_behavior`（旁观结算、CVE Growth）
  - `handle_premise`：`__init__`（CVP）与 work / H / other / place / time / entertainment 里的教育前提
  - 面板与指令：`character_info_head`、`handle_instruct` 的授课 / 开课 / 下课 / 检查成绩单、`group_sex_panel` 的邀请与旁观、`manage_basement_panel` 与 `normal_flow` 的入口
  - 妊娠系统：`pregnancy_handle` 的三次长大、`born_event_panel`、`egg_handle` 的照料卵替换
  - 角色生命周期：`character_handle` 的出生与上线、`Dormitory_System` 的新角色分宿舍
  - 存档与公务事件：`save_handle` 的回填、`official_event_handle` 的派发 / 容量 / 结算
- **数据**：`target.csv` 组 07 / 08 与 505 / 515、`Entertainment.csv`、`InstructConfig.csv` 与 `Behavior_Data.csv` / `Behavior_Effect.csv` 里的教育行，以及 `data/official_event/` 五张表

基线：
- 回归 15 个文件 1035 条断言全绿
- 死代码扫描：Education_System 375 个函数 / 方法 / 常量，全部有引用（注册式的三个函数照旧只有注册表与注释引用）
- 代码无 TODO

下表的「已复现」都由 scratchpad 脚本在无头环境跑出（不入库，实施文档 §2.0 要求重建）。改前 32 项检查全部成立：19 项是问题命中，13 项是前提、对照与范围外。

### 2.1 发现（高）

| # | 发现 | 证据 | 状态 |
| --- | --- | --- | --- |
| H1 | **婴儿期的养成事件永远派不出来**。<br>• 每日派发名单与队列容量都只遍历 `cache.npc_id_got`；婴儿出生时并不进这个集合，那一行已被注释掉，要到长成幼女、调 `get_new_character` 上线时才加入。<br>• 名单的注释与常量都写着「只看婴儿~萝莉（101~103）」，结果婴儿桶的 50 条事件（`sub_key` 101）在实际游戏里一条都没派出过；通用桶对婴儿同样派不到。<br>• Plan 26 为婴儿补的「17 条会走会说的通用事件不派给婴儿」也从未真正生效过。<br>• 八轮复查都没发现，原因是测试夹具 `make_character` 把所有非玩家角色（包括婴儿）都放进了 `npc_id_got`（见 L7） | `growth_event_handle.py:41~65`（`:57`）、`:244~253`；`character_handle.py:157~203`（`:199`）；`pregnancy_handle.py:551~565`（`:560`）；`Settle/default.py:4583~4584`；`baby_growth_handle.py:124~125`（注释已写明「婴儿不在 npc_id_got 里」）；`education_constant.py:470~474`；`data/official_event/婴儿.csv`；`_bootstrap.py:303~304` | 已复现：<br>• 走真实出生路径 `born_new_character` 造的婴儿不在 `npc_id_got`，候选事件却有；<br>• 把必派概率拉到 100% 连派 30 天，一条都派不到她；<br>• 队列容量为 0 |

### 2.2 发现（中）

| # | 发现 | 证据 | 状态 |
| --- | --- | --- | --- |
| M1 | **个人式课这一节上不成时，体力闸、心情闸与出勤照样按「有课」判**。<br><br>Plan 26 §3.8 让解析不出上课地点（场所未开放）或兴趣课条件不符的课「交回既有 AI」，但只挡住了 ATTEND 的两行。`get_course_at` 对个人式课一律返回课，于是：<br>• `get_course_stage` 先过两道闸：体力低时判 ABSENT_HP，派 721 **记一节缺课**；掷中翘课时判 SKIP，派 714 **翘课**，挂上翘课 flag 与 `<翘>`，还可能被抓。220805 / 220810 两行只挂上课状态，不看地点。<br>• ATTEND 时确实交回娱乐链，但日程排了「上课（无课时自习）」的会去自习，548 以「查得到课」计出勤，**多记一节**；`<课>` 悬停写的是那节上不成的兴趣课。<br>• 幼女的这一节状态不是 NONE，**默认见学也不成立**。<br><br>现实触发路径：<br>• 过家家是唯一带 need 的兴趣课，萝莉排了它、长成少女后仍是学生岗（成年女儿照旧出成绩单）；<br>• 「复制到其他学生」不看 need；<br>• Plan 26 之前可选未开放场所的旧档 | `schedule_handle.py:421~464`；`class_ai.py:307~325`、`:656`；`target.csv:137~138`；`handle_premise_work.py:494~519`；`Settle/default.py:7674~7684`；`character_info_head.py:64~72`；`course_select_panel.py:178~195`、`:299~340`；`Entertainment.csv:29`；对照 `test_class_ai.py:931~957`（只验了 ATTEND 这一条路） | 已复现：<br>• 少女的过家家兴趣课：体力低 → 721、缺课 +1；掷中 → 714；日程自习 → 713、548 出勤 +1；`<课>` 悬停写兴趣课。<br>• 幼女的游泳池体育课在游泳池未解锁时，这一节不见学；不排这节课时照常见学 |

### 2.3 发现（低）

| # | 发现 | 证据 | 状态 |
| --- | --- | --- | --- |
| L1 | **日程模板能选「照料卵」，日程改写还会冲掉持卵者当天的照料卵时段**。<br>• 照料卵是妊娠系统给持卵者的专用娱乐：随机池专门排除它，只由每日替换钩子分配；但它的 need 是「无」。「选择活动」的候选是全部娱乐，于是它也在里面。<br>• 排给孩子后，她晚上去育儿室，状态机 427 找不到可鉴定的卵，就「孵化卵」60 分钟，效果串还给医疗经验。一期方案曾以为「照料卵需自己产过卵」，但 need 列并没有这一条。<br>• 另一面，跨天结算里照料卵替换先于日程改写，套了日程的持卵者（成年学生、少女期的女儿；批量套用名单含 104）那个时段会被改回模板的活动 | `schedule_template_handle.py:405~413`、`:352~364`；`Entertainment.csv:30`；`handle_npc_ai.py:829~831`；`StateMachine/default.py:1700~1733`；`Behavior_Effect.csv:122`；`past_day_settle.py:86~91`；`egg_handle.py:572~599`；`plan_22_生长养成系统_一期_方案.md:626` | 已复现（候选里有 152；套给幼女后晚上写成照料卵，427 派孵化卵；持卵钩子换上的时段被日程改写改回） |
| L2 | 排实操课页的「本节选修本教室的学生」不看岗位：改了岗的女儿课表里还留着这一格，会被列进「会来」（修过性技课时）或「会到场但没修过」。实际上她上课状态恒为 NONE，也进不了课堂 | `sex_class_handle.py:389~413`；`class_schedule_panel.py:468~486`；对照 `sex_class_handle.py:347~348`、`class_ai.py:295~296` | 已复现 |
| L3 | 必修名单的「*会顶替原本的课」只看教室课：<br>• 必修覆盖会顶掉她这一节的任何课，体育 / 兴趣 / 实习课也一样，按钮却不标 `*`；<br>• 反过来，教室课那一格在每周课表上空着（已停课，Plan 27 起算没课）的，照样标 `*` 并列进顶替明细 | `class_schedule_panel.py:560~573`；`schedule_handle.py:436~439` | 已复现 |
| L4 | 养成总览「待处理」写「本学期成绩单待查看」。这个 flag 在学期切换时置位，待查看的是**刚结束的那一学期**的成绩单 | `growth_panel.py:375~376`；`semester_handle.py:339~340` | 已复现 |
| L5 | 日程安排的「上课（无课时自习）」本节没排课，`<课>` 悬停却写「上课中」。第五轮起它不计出勤，本来就不算一节课 | `character_info_head.py:64~67` | 已复现 |
| L6 | 注释与文档过期：<br>• 「不在节次内且 20 分钟内那一节有课」共 6 处。Plan 25 起节次内本节没课时也看下一节，这句话已不对<br>• `temp_sex_class` 的字段注释缺第五轮加的 `reserved` / `ended`<br>• `get_student_candidate_list` 的注释还写「课表页签栏」，2026-09-09 已换成「选择学生」<br>• 婴儿长成幼女时写死 `work_type = 152`，第五轮已把 303 / `handle_teach` 的 152 改用常量，这里漏了 | 「不在节次内」：`education_constant.py:305~306`、`constant_promise.py:3745`、`handle_premise_work.py:539`、`target.csv:118`、`:142`、ArkEditor `Premise.csv:1896`；字段注释：`game_type.py:1290~1298`；「页签栏」：`growth_handle.py:74`；写死 152：`pregnancy_handle.py:565` | 读代码 |
| L7 | 测试夹具 `make_character` 把所有非玩家角色都放进 `npc_id_got`，婴儿也不例外，与真实婴儿不一致，H1 因此一直测不出来 | `_bootstrap.py:303~304`；婴儿夹具 5 处：`test_growth.py:164`、`test_prenatal_baby.py:7~8`、`test_premise_tokens.py:206`、`test_growth_event.py:13` | 读代码 |

### 2.4 可复用的既有实现

| 需求 | 现成实现 |
| --- | --- |
| 认女儿、认阶段 | `handle_premise.handle_self_is_player_daughter`（`father_id == 0`，婴儿出生即成立）；`growth_handle.get_character_stage` |
| 事件对婴儿的支持 | `get_candidate_event_list` 按 (0, 当前阶段) 两个桶翻；`get_sibling_child_list` 取幼女 / 萝莉的哥哥姐姐；抬头「婴儿期第 N 天」；公务事件的清理与结算只要求主体在 `character_data` 里 |
| 个人式课能否上 | `schedule_handle.get_course_place`（Plan 26 起只返回已开放的场所）+ `judge_course_need_pass` |
| 「没课」的收口方式 | Plan 27 在 `get_course_at` 里对已停课返回 None，AI、结算、`<课>`、CVP 一起跟上 |
| 照料卵常量 | `pregnancy_constant.TEND_EGGS_ENTERTAINMENT_ID`，随机池排除它用的就是它 |
| 学期名 | `semester_handle.get_semester_name` + `get_last_report_card` 的 year / month |
| 格子写法 | 教室课「教室/已停课」（`course_select_panel.py:189`）。同一写法「目标/未开放」「目标/条件不符」按显示宽度逐项算过：体育最宽 `[体]游泳池/未开放`，兴趣最宽 `[兴]演奏传统乐器/条件不符`，实习最宽 `[实]图书馆管理员/条件不符`，都 ≤ 25 列，正好等于格宽（(190−14)/7） |
| 课型·目标的文本 | `character_info_head.get_course_text` |

### 2.5 已知陷阱与硬约束

1. **婴儿不在 `npc_id_got` 是既有设计**：她不进 AI 循环、跨天刷新、宿舍分配与各类统计，到长成幼女那天才上线。不能为了派事件把婴儿加进去，只改养成事件自己的遍历来源
2. **前提必须是纯函数**（Plan 24 §2.6-1）：`get_course_at` 被前提读取，新增的判定（`get_course_place`、`judge_course_need_pass`）都只读，且后者早已在前提路径上用着（`get_course_place_now_or_upcoming`）
3. **`get_course_at` 是 AI、结算、`<课>`、CVP 的共同取数口**（Plan 27 陷阱 2 同理），调用方清单见 §3.2；测试里依赖「个人式课在未开放场所也算有课」的断言要逐条核对
4. **夹具与真实不一致**：改 `make_character` 让婴儿不进 `npc_id_got` 之后，5 处婴儿夹具的断言要逐条核对（多数不依赖这一点）
5. **旧档**：模板或单孩覆盖里已经排了照料卵的，改写时跳过，面板写明
6. **性能**：`get_course_at` 对个人式课多一次 `get_course_place`（实习课会扫岗位场景里的人）；前提在一次决策里按名缓存，个人式课的格子也不多，量级可忽略

## 3. 设计决策

### 3.1 婴儿期的养成事件照常派发（H1，推荐口径 1）

`growth_event_handle.get_growth_event_character_list` 改为遍历 `sorted(cache.character_data)`，入选条件：
- 玩家的女儿，阶段 101~103；
- 婴儿**不要求**在 `npc_id_got` 里；
- 幼女 / 萝莉仍要求在 `npc_id_got` 里（离线的不派，与现状一致）。

派发、容量、抬头都经这一个名单，改一处即全部跟上：
- 每人每天 70% 派一条，每人 4 条队列容量，全局硬顶 8 条，都不变；
- 候选、互动对象、抬头都已支持婴儿（§2.4）；
- 结算安全：复现脚本在真实出生的婴儿身上把 60 条可派事件的 182 个选项逐一结算，0 报错。

| 候选 | 弃选原因 |
| --- | --- |
| 出生时把婴儿加进 `npc_id_got` | 那是「在岛上活动的干员」集合，进去就进 AI 循环、跨天刷新、宿舍分配与各类统计，婴儿全都用不上，影响面远超养成事件 |
| 遍历玩家的 `child_id_list` | 与全系统「按 `father_id` 认女儿」的口径不一致；测试夹具也不维护这个名单 |

### 3.2 个人式课这一节上不成视为没课（M1，推荐口径 2）

新增 `schedule_handle.judge_personal_course_valid(character_id, course) -> bool`：兴趣课的 need 相符（`judge_course_need_pass`），且上课地点解析得出（`get_course_place` 非空，含场所已开放）。`get_course_at` 对个人式课（体育 / 兴趣 / 实习）判不过就返回 None，与 Plan 27 对已停课的处理同一个位置、同一种语义。

| 下游 | 改后 |
| --- | --- |
| `get_course_stage` / `get_upcoming_course` | NONE：不判体力闸与心情闸，不为它提前动身，交回见学 / 娱乐链 |
| 见学 | 幼女这一节照常默认见学 |
| 548 自习结算 | 「上课（无课时自习）」只给收益、不计出勤 |
| `<课>` 悬停、CVP `Course` / `CourseType` | 按没课处理 |
| `get_course_place_now_or_upcoming`（`class_ai.py:399~401`）、截短规则 B（`class_ai.py:549~551`） | 这两处原来各自再判一次 need，现在取数口已经挡住，删掉重复判定；截短规则保留「地点为空不截」的防御 |
| 必修覆盖 | 不受影响：覆盖后是教室课 |
| 实习课无人在岗 | 不受影响：地点解析得出，照旧降级见习 |
| 个人课表面板格子 | 写「[兴]过家家/条件不符」「[体]游泳池/未开放」，与教室课「/已停课」同一写法；地点先判、need 后判，与选课页 `_select_target` 的顺序一致 |
| 同班同学 | 不受影响：直接读个人课表（范围外，见 §7） |

| 候选 | 弃选原因 |
| --- | --- |
| 只在 `get_course_stage` 里挡 | 548、`<课>`、见学、CVP 要各补一遍；Plan 27 已在同一取数口收口「已停课」 |
| 萝莉长成少女时清掉条件不符的兴趣课 | 只能覆盖「长大」这一条路，复制课表与旧档照样会残留；课表是玩家的设置，自动删改会让人困惑 |
| 照旧记缺课 | 这节课上不成不是孩子的问题，与 Plan 27 决策 1「已停课不记出勤也不记缺课」同理 |

### 3.3 日程模板与照料卵（L1，推荐口径 3）

新增 `schedule_template_handle.judge_activity_schedulable(entertainment_id) -> bool`：照料卵为 False，其余为 True。候选表、改写、日程行共用它：
- **候选**：`get_schedule_activity_candidate` 去掉不可排的，「选择活动」面板里不再出现照料卵
- **改写**（`apply_schedule_for_child`）：
  1. 模板 / 覆盖里残留的照料卵（旧档里已排上的）跳过，退回自由选择
  2. 当天槽位已被持卵钩子换成照料卵的不覆盖：持卵者那个时段要去照料卵
- **日程行**（`get_child_slot_activity_text`）：残留的照料卵写「照料卵（条件不符→自由选择）」

| 候选 | 弃选原因 |
| --- | --- |
| 在 427 状态机里对没有卵的人改派别的 | 那是妊娠系统的状态机，保育员与持卵者共用；问题出在日程这条写入路径 |
| 把照料卵的 need 改成「有需要照料的卵」 | need 语法没有这类判定，要为一项娱乐扩通用语法 |
| 改跨天结算的顺序（日程改写先于照料卵替换） | 钩子是「随机挑一个时段」，挪到后面照样可能落在日程排好的时段上，而且会改动妊娠系统的既有顺序；在改写这边不碰照料卵更直接 |

### 3.4 选修人数只数学生岗（L2）

`sex_class_handle.get_selected_student_list` 加学生岗过滤，与 `judge_can_join_sex_class`、「课表只对学生岗生效」（Plan 24 口径 1）同口径。它只有排实操课页一个调用方。

### 3.5 必修名单的顶替标记（L3）

只有「会顶掉这一节确有的课」才标 `*`：
- **教室课**：每周课表那一格非空才算（`get_class_cell(..., include_temp=False)`）；空着即已停课，不标
- **个人式课**（体育 / 兴趣 / 实习）：用 §3.2 的 `judge_personal_course_valid` 判，明细写「X→体育课·木桩房」，课型·目标的写法照 `character_info_head.get_course_text`

按钮宽度不变，只多一个 `*`。

### 3.6 养成总览的待处理（L4）

改为「{学期名}的成绩单待查看（用「检查成绩单」指令）」，学期名取最新一份成绩单的 year / month（`get_semester_name`）；万一取不到，写「新的成绩单待查看」。

### 3.7 `<课>` 悬停（L5）

行为是自习、此刻又没课时，写「自习中（日程安排，此刻没课）」。听课而此刻没课（玩家在节次外手动授课）仍写「上课中」。

措辞在实施时由「本节没排课」改为「此刻没课」（实施文档 §6.1 偏离 1）：日程的「上课（无课时自习）」在节次外也会自习 45 分钟，已停课与上不成的个人式课也是「排了但没课」，「本节没排课」对这几种都不准。

### 3.8 注释与文档（L6）

| 位置 | 改为 |
| --- | --- |
| 「不在节次内且 20 分钟内那一节有课」6 处 | 「本节没课（含不在节次内）且 20 分钟内开始的那一节有课」。`target.csv` 只改 remarks 列，改完跑 `tools/lint_target_csv.py`；ArkEditor `Premise.csv` 同步 |
| `game_type.py:1290~1298` | 字段注释补 `reserved`（开课时是否复用了预约条目，开课口上分档用）与 `ended`（预约的课下课后打的标记，覆盖层与必修判定不再认它） |
| `growth_handle.py:74` | 「课表页签栏」改为「选择学生的名单」 |
| `pregnancy_handle.py:565` | 改用 `education_constant.STUDENT_WORK_TYPE`，函数内延迟 import，照 `handle_npc_ai` 的写法 |

### 3.9 测试夹具（L7）

`make_character` 造的婴儿（`stage=101`）不进 `npc_id_got`，与真实婴儿一致；README 的 fixture 陷阱补一条。波及的 5 处婴儿夹具逐条核对，确属新口径的改断言并注明 Plan 28。

## 4. 接口设计（实施的权威定义）

### 4.1 常量与字段

无新增常量与字段。照料卵的编号复用 `pregnancy_constant.TEND_EGGS_ENTERTAINMENT_ID`（`schedule_template_handle` 函数内 import）。

### 4.2 函数签名

| 模块 | 函数 | 变化 |
| --- | --- | --- |
| `growth_event_handle` | `get_growth_event_character_list` | 遍历全部角色，婴儿不要求在 `npc_id_got`（§3.1） |
| `schedule_handle` | `judge_personal_course_valid(character_id, course) -> bool` | 新增（§3.2） |
| `schedule_handle` | `get_course_at` | 个人式课判不过时返回 None（§3.2） |
| `class_ai` | `get_course_place_now_or_upcoming` / `get_student_leave_time` | 删掉重复的 need 判定（§3.2） |
| `course_select_panel` | `_get_cell_text` | 个人式课上不成时写「/未开放」「/条件不符」 |
| `schedule_template_handle` | `judge_activity_schedulable(entertainment_id) -> bool` | 新增（§3.3） |
| `schedule_template_handle` | `get_schedule_activity_candidate` / `apply_schedule_for_child` / `get_child_slot_activity_text` | 不可排的不列、不写，照料卵时段不覆盖（§3.3） |
| `sex_class_handle` | `get_selected_student_list` | 只收学生岗（§3.4） |
| `class_schedule_panel` | `_select_must_attend` | 顶替标记按「确有的课」判（§3.5） |
| `growth_panel` | `_draw_flag` | 写学期名（§3.6） |
| `character_info_head` | `get_now_class_tip` | 日程自习写「自习中」（§3.7） |
| `tools/tests/education/_bootstrap.py` | `make_character` | 婴儿不进 `npc_id_got`（§3.9） |

### 4.3 数据行

- `data/target/default/target.csv`：210810、220830 两行只改 `remarks` 列（§3.8）
- `tools/ArkEditor/csv/Premise.csv`：`self_course_upcoming` 一行的描述列（§3.8）

## 5. 行为对照

| 情形 | 现行为 | 改后 |
| --- | --- | --- |
| 有婴儿的女儿、跨天派养成事件 | 婴儿一条事件都派不到，婴儿桶的 50 条从未出现 | 婴儿与幼女 / 萝莉一样每天 70% 一条，每人占 4 条队列容量 |
| 少女还排着萝莉时选的过家家兴趣课，这一节体力不足 | 记一节缺课去休息 | 这节没课，按日程或随机娱乐自由行动，不记缺课 |
| 同上，心情糟糕 | 翘课，挂 `<翘>`，可能被抓 | 不翘课 |
| 同上，日程排了「上课（无课时自习）」 | 去自习，多记一节出勤；`<课>` 悬停写兴趣课 | 去自习，只给收益；悬停写「自习中（日程安排，此刻没课）」 |
| 幼女的体育课排在还没解锁的游泳池 | 这一节不见学 | 照常默认见学 |
| 个人课表上的这种格子 | 照常写「[兴]过家家」 | 写「[兴]过家家/条件不符」「[体]游泳池/未开放」 |
| 日程模板给孩子排照料卵 | 每晚去育儿室「孵化卵」一小时，拿医疗经验 | 选择活动里没有这一项；旧档里排了的退回自由选择，日程行写明 |
| 少女期的女儿持卵、又套了日程 | 当天换上的照料卵时段被日程改回 | 照料卵时段保留 |
| 排实操课页、改了岗的女儿课表里残留这一格 | 被算进「会来」 | 不算 |
| 必修名单、学生这一节排了体育课 | 不标 `*` | 标 `*`，明细「X→体育课·木桩房」 |
| 必修名单、学生这一节的教室课已停课 | 标 `*` 并列进明细 | 不标 |
| 学期切换后查看养成总览 | 「本学期成绩单待查看」 | 「2026年 夏季学期的成绩单待查看」 |

## 6. 风险与注意事项

| 风险 | 说明 | 对策 |
| --- | --- | --- |
| 婴儿开始收到养成事件 | 此前婴儿期一条事件都没出过，修好后公务队列会多出婴儿的事 | 这是设计本意（口径 12「覆盖婴儿到少女全阶段」）；全局硬顶 8 条与队列上限兜底；全部选项已在真实婴儿身上结算过 |
| `get_course_at` 对个人式课多判两样 | AI、结算、`<课>`、CVP 一起变 | §3.2 逐项核对；依赖「上不成也算有课」的测试断言逐条核对；新增「上不成视为没课」与「解锁 / 条件恢复后照常」的断言 |
| 旧档模板里的照料卵 | 改写跳过 | 日程行写「条件不符→自由选择」 |
| 夹具改动波及既有测试 | 5 处婴儿夹具 | 逐条核对，确属新口径的改断言 |
| 构建会写乱 PO | 同前几轮 | 收尾 `git checkout -- data/po/` |

## 7. 不在本方案范围

- **日程模板白天排品酒**：成年学生经日程微调才排得上，是玩家明确的安排；随机池「品酒只在晚上」是给 NPC 自主抽娱乐定的规则（复现脚本 N5-5 改后仍成立）
- **同班同学名单**按个人课表格子重合算，含已停课与上不成的格子（与 Plan 27 §7「同班同学含成年学生岗」同理，事件文本说得通）
- **检查成绩单的兜底口上 1005**「成绩单上有一门格外突出」：学期中途没有升级科目时略显突兀，属文本层面，不改
- **婴儿不进养成总览**（`STUDENT_STAGE_TALENT_SET` 不含 101，按设计）：婴儿期事件留下的养成履历，要到她长成幼女、进了名单才看得到
- Plan 22 总纲 §10.2 的五条备忘；Plan 26 §7、Plan 27 §7 的其余范围外事项
- Plan 24~27 留给用户的游戏内测试项

## 8. 追加调整

（实施后每轮追加一节，只写设计；实施记录见实施文档 §6.5。暂无）
