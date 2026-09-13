# Plan 31（方案）：生长养成系统第十二轮复查

> 本 Plan 拆分为两个文件：**本文件为纯方案**（发现、现状调查、设计决策、接口设计、风险、范围外）；
> 逐文件改动步骤、构建、验证清单、回滚与实施过程记录见 `plan_31_生长养成系统第十二轮复查_实施步骤与记录.md`（下文简称"实施文档"）。
>
> 本 Plan 是 Plan 22（生长养成系统）、Plan 24（师生并入工作链）、Plan 25~30（第六~十一轮复查）之后的又一轮全面复查，前述各 Plan 均在 `plan/done/`。
> 实施完成后在 Plan 22 总纲追加 §17，只写一行指向本 Plan。

- 状态：已实施（2026-09-13；方案定稿、用户确认 Q1~Q4 均按推荐与实施同日完成，实施记录见实施文档 §6）
- 来源：用户需求 → "使用skill，对 养成 系统再进行一次检查"
  - 本轮是 `system-review-round` skill 的第一次试跑。用户要求「先只启动5个代理规模的审查」：4 个核查代理（七个维度两两合并）+ 1 个核实兼复现代理，补漏由主代理按复查清单做
  - 每条发现都由主代理读到代码落点，H / M 各条与疑点 (A) 由主代理另写复现脚本跑出
- 口径（2026-09-13 用户已确认）：
  1. **教师晚到的那一节由学生侧先结算**：学生坐下听课时，本节教师判「能到岗」就按授课的口径结算；教师到场开讲时，不再把时间线已走到后面的学生拉回来（§3.1）
     - 附问 Q1：推荐本条；备选只修「拉回来」、学生侧仍等教师到场
  2. **通用 59 / 60 在成年结算时推入**，排在毕业典礼与成年纪念之后（§3.2）
     - 附问 Q2：推荐本条；备选日常派发对成年女儿开放成年桶 / 删掉两条
  3. **实操课门槛的实行值只判不扣**：门槛判定不再扣理智、不再解除催眠，进了课堂之后每个 H 动作照常结算（§3.3）
     - 附问 Q3：推荐本条；备选门槛不认催眠补正
  4. **空气催眠 / 木头人的教师判来不了**：木头人一律来不了；空气催眠只在人已在本节教室时算能到岗（§3.4）
  5. **翘课日的两处口径对齐**：今天已翘课的学生不再被派去教室门口等开课；在娱乐里的，截到开课那一刻让她当场判翘课（§3.5）
  6. **翘课 flag 认日期**：只在挂上的那一天有效，漏清的两条路（一步跨过午夜、翘课当天离线）不再把翘课带进另一天（§3.6）
  7. **事件与口上的正文、前提对齐**（§3.14）
     - 附问 Q4：推荐前提能收窄的收窄（含新增按课型查课表的前提、生日前提、累计实操课次数），写不出前提的改正文，删掉授课 / 听课的占位行；备选只收窄现有前提 / 本轮不动数据
  8. 其余小修（§3.7~§3.13、§3.15~§3.17）
- 预计改动量：**约 45 个文件**，净增约 600 行（按 Q1~Q4 都选推荐估）
  - 逻辑 17 个：`game_type`、`education_constant`、`constant_promise`、`class_ai`、`schedule_handle`、`sex_class_handle`、`growth_handle`、`growth_event_handle`、`class_schedule_panel`、`course_select_panel`、`growth_panel`、`Settle/default.py`、`second_behavior`、`instuct_judege`、`handle_premise/__init__`、`handle_premise_work`、`handle_premise_other`、`character_info_head`
  - 数据约 12 个：`data/official_event/` 四张表、`data/talk/` 下 6 个口上文件（删 1 个）、`tools/ArkEditor/csv/Premise.csv`；工具 2 个：`tools/official_event_check.py`、`buildata.py`
  - 测试约 11 个（含 README）；文档 4 个（说明文档、索引文档、Plan 22 总纲、`update.log`）
- 风险等级：**中低**。本轮唯一明显的数值口径变化是 H1：教师晚到的那一节，学生在坐下时就拿到收益与出勤（此前要等教师到场）；其余是判定收窄、去重与数据对齐
- 适用代码快照：`master @ 44ed83f15`（Plan 30 与 skill 提交之后）
- 前置：Plan 22 一~四期、第五轮复查、Plan 24~30 均已完成

---

## 1. 目标

1. 教师换教室或因需求晚到的那一节，无论玩家一步走多长，先到的学生都不再整节白上，也不再被拉回去把下一节结算两次（H1）
2. 实操课门槛重新是纯函数：打开指令面板、判前提、看旁观名单都不再扣理智、不再解除催眠（M1）
3. 通用 59 / 60 能推出来；以后往成年桶写事件，校验工具会拦（M2、L16）
4. 被催眠后到不了教室的教师判「来不了」，她的学生降级自习、照记出勤（M3）
5. 死内容与正文、前提对不上的事件和口上清掉或对齐（M4、L10~L15）
6. 翘课一天只算一天：翘课日不白跑一趟、不整节漏记，漏清的 flag 不带进另一天（L1、L2）
7. 小修：提前开讲的实操课出勤、改岗后的残留课表与残留授课格、303 拉人的门槛、同班同学的阶段、排实操课页的人数、玩家手动授课的口上、编辑器前提表与过期注释（L3~L9、L17、L18）

**验收标准**：
- 全套回归测试通过，新增断言覆盖 §3 每一条
- 复现脚本（实施文档 §2.0）改前全部成立；改后问题命中全部不再成立，其余照旧（计数见 §2 表头与实施文档 §2.0）
- `test_talk_data`、`tools/official_event_check.py` 通过（含新增规则）
- 行为循环测试收敛，上午四节人均出勤 ≥ 3 节不变

## 2. 现状调查

本轮读过的范围：
- **`Education_System/` 全部 15 个模块**：四个核查代理与主代理各自逐行读过，含 Plan 30 新加的函数
- **外部挂接点**：
  - `character_behavior`：`init_character_behavior` 的玩家 / NPC 两阶段与跨天、`character_behavior`、`judge_character_status_time_over`
  - `handle_npc_ai`：`find_character_target`（需求链排在工作链之前）、`judge_interrupt_character_behavior`、`get_chara_entertainment`；`handle_npc_ai_in_h` 的木头人锁定
  - `StateMachine/default.py`：303、561、713~722；`Settle/default.py`：512、548、549、557、体控 / 逆推开关、离线 / 上线；`Second_effect` 623；`past_day_settle`
  - `instuct_judege.calculation_instuct_judege` 的催眠补正段；`handle_premise` 的 normal 组合、CVP Course / CourseType / Growth、H 与 other 的教育前提；`talk` 的口上加权
  - `character_info_head`、`handle_instruct`（授课、开课）、`group_sex_panel`、`official_event_handle`、`handle_ability`、`pregnancy_handle`、`sleep_panel`、`save_handle`
- **数据**：`target.csv` 组 07 / 08；`InstructConfig` 的 2010 / 5209；`data/official_event/` 五张表的全部前提与正文；教育口上（授课、听课、自习、翘课、炫耀、实操课、检查成绩单）的前提统计；`tools/ArkEditor/csv/Premise.csv`

基线：
- 回归 15 个文件 1206 条断言全绿（2026-09-13，Plan 30 之后）
- 死代码扫描：Education_System 432 个定义，生产代码零引用的只有注册式的三个函数（说明文档 §15 第 10 条已写明）

下表的「已复现」都由 scratchpad 脚本在无头环境跑出（不入库，实施文档 §2.0 要求重建），两份脚本改前全部成立：
- 主代理的 `repro_main.py`（H / M 各条与 L1~L3、L9）40 项：19 项问题命中，18 项前提对照，3 项数据事实
- 核实兼复现代理的 `repro_plan31.py`（26 组，覆盖全部发现）121 项：59 项问题命中，50 项前提对照，11 项数据事实，1 项随口径；主代理重跑一遍结果相同

核实兼复现代理对 26 条发现逐条反驳，没有一条被驳倒；另修正了两处机理：
- H1 的变体 A 在两种处理顺序下都丢一节，与 id 先后无关
- 截短规则 A 不看翘课属设计（见 §2.3）

### 2.1 发现（高 / 中）

| # | 发现 | 证据 | 状态 |
| --- | --- | --- | --- |
| H1 | **教师换教室（或因需求）晚到的那一节，玩家一步跨满一整节时，先到的学生整节白上，或被拉回去把下一节结算两次**。<br>• NPC 阶段每一遍对每个 NPC 只推进一个行为，行为在开始时结算；玩家一步越长，各 NPC 的时间线在同一遍里差得越远。<br>• 教室课的收益只有两个入口，都按「循环处理到的那一刻」判：<br>　- 学生侧 557 只在教师此刻已在同一教室、行为是授课时结算；<br>　- 教师侧 303 只拉此刻在教室里的人，并把对方的行为开始时刻改成教师的开讲时刻。<br>• 教师第 1 节在理论教室一、第 2 节在理论教室二（一键排课的常态），换教室要走两跳。学生 9:45 在教室二坐下，557 判不过（教师还在走廊）；学生这一步里已走到 10:30，教师到 9:47 才开讲：<br>　- 学生第 3 节在别处：10:30 就走了，303 拉不到她，第 2 节既无出勤也无缺课、零收益（总纲 §10.1 #2「整节白上」的反方向）；<br>　- 学生第 3 节还在教室二：她已在 10:30 结算了第 3 节，303 仍把她拉回 9:47，512 结算第 2 节后她从 10:30 重走，第 3 节再结算一次。<br>• Plan 25 §3.3 写「教师回来开讲时 303 会把在座的学生拉进来，512 负责结算」，只在玩家一步短于一节时成立；测试的步长是 40 / 45 分钟、从不跨满一整节 | `character_behavior.py:69~75`、`:165~184`、`:341~343`；`StateMachine/default.py:2706~2717`（303）；`Settle/default.py:7716`（557）；`class_ai.py:473~498`；`growth_handle.py:269~274`；`auto_schedule.py:110~129`；`test_behavior_loop.py:138` | 已复现（玩家 9:40 等 60 分钟）：<br>• 教师 9:45 动身、9:47 在教室二开讲；学生 9:45 坐下、10:31 离开，第 2 节结算 0 次；<br>• 第 3 节同教室：学生被拉回 9:47，第 3 节结算两次，两节课出勤 +3；<br>• 对照：玩家每步 10 分钟，第 2 节照常结算一次 |
| M1 | **实操课门槛的实行值计算会扣玩家理智、会解除学生的催眠**。<br>• 对非女儿的学生岗，`judge_can_join_sex_class` 最后调 `calculation_instuct_judege(0, 学生, "H模式", not_draw_flag=True)`。<br>• 这个函数的催眠补正段（目标无意识 4~7、性爱判定、实行值不足、玩家有中级催眠、目标被深层催眠）在判断 `not_draw_flag` 之前就写数据：理智够时扣玩家理智并累加今日消耗，不够时把目标的催眠清零（刷新的还是玩家当前交互对象的异常位）。<br>• 平然（4）与空气（5）先被门槛里的 normal 5 / 6 挡掉，体控（6）与心控（7）会走到这一段。<br>• 门槛挂在前提与面板上：指令 5209 的前提 `scene_have_sex_class_student`（玩家在实践教室时每刷新一次指令面板就求值）、口上前提 `self_in_sex_class`、学生自己的 `get_course_stage`（6 个学生前提各算一次）、课堂模式的邀请面板、旁观结算、必修名单面板。<br>• 违反「前提必须是纯函数」（Plan 24 §2.6-1）：理智在两次调用之间耗尽时，前一次判 JOIN、后一次判 ATTEND，入课与听课两行可能同时成立 | `sex_class_handle.py:364`；`instuct_judege.py:357~395`、`:410`；`handle_premise_H.py:2304`、`:2323`；`InstructConfig.csv:213`；`class_ai.py:367`、`:393`；`handle_premise/__init__.py:1126~1168` | 已复现：<br>• 心控中的成年学生，前提求值两次，理智 100 → 84 → 68，今日消耗 32；<br>• 理智为 0 时判一次门槛，她的心控被清零；<br>• 她自己的一次 AI 决策（派 722）里门槛算了 6 次，每次扣 16（代理实测） |
| M2 | **通用 59 / 60 永远推不出来**。<br>• 两条都在部门 15 的成年桶（sub_key 104），写的是成年后的里程碑（人事送来干员编号、第一次以干员身份报到）。<br>• 第五轮（09-12）为不让成年女儿永久占 4 条队列容量，把日常派发名单收窄到 101~103；两条是 09-07 公务事件系统扩充时加的，收窄时漏看了。<br>• 成年桶此后只有成年结算硬编码推入的通用 1 / 2 有入口：部门 15 由养成提供者独占，默认提供者跳过它；全仓库 `push_official_event` 的调用点只有 4 处。<br>• 说明文档 §8「104 只给成年事件（如通用 1 / 2）」也暗示桶里别的事件可达 | `data/official_event/通用.csv:64~65`；`growth_event_handle.py:41~73`、`:295~310`；`education_constant.py:475~480`；`official_event_handle.py:392~393`、`:446`；总纲 §10 第五轮 #12 | 已复现：<br>• 成年女儿不进日常派发名单；<br>• 每日派发 300 次（代理 800 次）从未出现 59 / 60；<br>• 成年结算只推通用 1 / 2 |
| M3 | **空气催眠（人不在教室）或木头人的教师被判能到岗，她的学生空坐整节**。<br>• Plan 25 §3.3 让无意识 5 / 6 豁免 normal 5 / 6，理由是「那两种催眠下授课行照样成立」；但授课行 220700 要人已在本节教室，去教室的移动行 210700 挂的是 `normal_all`，空气催眠下不成立。<br>• 体控（6）不在 H 的只有木头人一种（逆推一开就进 H），木头人每轮被锁成原地等待，玩家离开也不解除。<br>• 学生按「能到岗」坐下听课（304），512 不会发生，557 要求教师在场授课，出勤与缺课都不记、零收益，违反 `judge_teacher_available` 自己的约束「凡是这节确定来不了的都必须挡掉」 | `class_ai.py:81~83`、`:102~107`；`target.csv:113`、`:133`；`handle_premise/__init__.py:1151~1168`、`:1628~1644`；`handle_npc_ai_in_h.py:103~136`、`:139~163`；`Settle/default.py:1753~1757`、`:1812~1822`、`:7716` | 已复现：<br>• 空气催眠、人在教育区入口：判能到岗，`normal_all` 不成立；<br>• 木头人：判能到岗，被锁成原地等待；<br>• 学生派 304 后这一节零收益、出勤不变；<br>• 对照：空气催眠、人已在教室时判能到岗 |
| M4 | **腰技炫耀口上 52 条是死内容**。<br>• 炫耀口上要 `CourseShowOff\|76`，待炫耀只在 `gain_ability` 升级成功后写；女性遇 `sex_need == 0` 的能力直接跳过，腰技 76 是男性专属，女儿的腰技永远升不上去。<br>• 以往方案已定腰技不列进女儿可学的科目（四期 §7-21），但炫耀口上与 `test_talk_data` 的「18 门全覆盖」没跟着改 | `data/talk/system/second_show_off_study/show_off_waist_skill.csv`；`handle_ability.py:83~86`、`:120~132`；`Ability.csv` 76；`test_talk_data.py:37` | 已复现（代理）：给足珠与经验跑真实的 `gain_ability`，另 17 门都升级并记进待炫耀，76 恒为 0；52 条口上都带女儿前提与 `CourseShowOff\|76` |

### 2.2 发现（低）

| # | 发现 | 证据 | 状态 |
| --- | --- | --- | --- |
| L1 | **今天已翘课的学生，两处与课表有关的判定口径相反**。<br>• 截短规则 B 特意不赶她（「免得去教室门口等一趟再掉头走」），`get_course_stage` 的 UPCOMING 却不看 flag：她只要在开课前 20 分钟内空下来，就被派去上课地点等开课，开课那一刻判 SKIP，从教室里走回去翘课。<br>• B 不截的后果：空节里抽到 120 分钟的娱乐（看电影、排演舞剧），会盖过下一节整节——那一节没有决策、没派 714、不记缺课也不记出勤。Plan 30 §2.3「逐节记缺课不漏节」只对 714 首尾相接的那条链成立 | `class_ai.py:319~324`、`:335`、`:545~546`、`:564`；`handle_npc_ai.py:682~685`；`target.csv:118`、`:142` | 已复现：<br>• 挂 flag、13:45 空下来 → UPCOMING；同一人在娱乐中 B 不截；14:00 判 SKIP；<br>• 9:55 起看 120 分钟电影：不挂 flag 截到 10:10，挂 flag 不截（盖过 10:30~11:15 那一节） |
| L2 | **翘课 flag 只靠跨天结算清除，漏清的两条路把翘课带进另一天**。<br>• flag 是布尔值，`get_course_stage` 见 flag 就判 SKIP、不看日期；清除只在跨天结算对 `npc_id_got` 与玩家做。<br>• 一步跨过午夜：跨天结算在 NPC 阶段跑完之后才调，玩家 23 点睡 10 小时以上时，NPC 已把第二天上午的课派完——昨天翘过课的女儿每一节都判翘课、记缺课与翘课数。<br>• 离线：翘课当天被派外勤（离线移出 `npc_id_got`，上线只重置 `sp_flag`），回岛那天整天判翘课，还挂着 `<翘>` | `class_ai.py:335`；`past_day_settle.py:58~76`；`character_behavior.py:78~80`；`sleep_panel.py:161`；`Settle/default.py:4527~4529`、`:4556~4584` | 已复现：<br>• 周一挂的 flag 没清时，周二 9:00 第 1 节判 SKIP（负面状态为 0）；<br>• 周日 23:00 一步走到周一 11:00，NPC 阶段里第 1~3 节各派一次 714，缺课与翘课各 +3（代理实测）；<br>• 离线期间跨天，flag 仍在，回岛第 1 节判 SKIP，714 记翘课（代理实测） |
| L3 | **提前几分钟开讲预约的实操课，出勤按开讲时刻所在的上一节判「本节已缺课」**。<br>• `find_reserved_class` 允许在开课前 30 分钟内提前开讲；`start_sex_class` 以 `cache.game_time` 记出勤，722 以学生的行为开始时刻记，都落在上一节。<br>• 上一节缺过课的学生（体力缺课、休息在这间教室），这节实操课的出勤记不上；她进了 H 不再进 AI，这一节也不会记缺课 | `sex_class_handle.py:209~216`、`:759~760`、`:851~855`；`growth_handle.py:323~`（`judge_absent_this_period`）；`StateMachine/default.py:3006`（722） | 已复现：9:40 开讲第 2 节的预约，上一节缺过课 → 出勤 +0；对照 9:46 按时开讲 → +1 |
| L4 | **取数口 `get_course_at` 不按学生岗收窄**。<br>• 课表只对学生岗生效（Plan 24 口径 1），Plan 30 修了「有课」「同学」两处消费方，另两处没修：<br>　- `<课>` 标识的个人式课分支：改任厨师的女儿在厨房上班时，每逢残留的「实习：厨师」节次都显示在上课（实习地点按「谁在岗」取，连她自己也算）；<br>　- CVP `CourseType` / `Course`：按残留课表判「在上课」 | `character_info_head.py:86~102`；`schedule_handle.py:421~470`、`:610~615`；`handle_premise/__init__.py:302~352` | 已复现（代理）：改任厨师后 `<课>` 返回「实习课·厨师」，`CourseType` 读成 5 |
| L5 | **教师 303 拉人不看 normal 门槛**。<br>• 学生自己的听课行挂 `normal_all_except_special_hypnosis`，需求链排在工作链之前；303 的 `judge_student_join_class` 只看学生岗、没睡、没翘课、没在休息与两道闸。<br>• 有需求（normal_1）、跟随或当助理（normal_3）的学生，教师先被处理就被改成听课到本节结束，与 Plan 24 口径 2 的对照表相反，结果取决于处理顺序（同 Plan 25 M5 一类） | `class_ai.py:450~498`；`target.csv:139`；`handle_npc_ai.py:314~330` | 已复现（代理）：跟随中、有吃饭需求的学生都被 303 拉成听课；她们自己决策时不命中听课行 |
| L6 | **改岗或离岛的教师还挂在全局课表上**。<br>• 运行时 `judge_teacher_available` 挡住，学生降级自习；但全局课表面板与个人课表选课页照写她的名字、没有提示，一键排课只填空格、这些格子永远是自习。<br>• `get_now_teaching` / `get_upcoming_teaching` 不看岗位：前教师改当学生后，CVP 与 561 先按「教师反查」取到她旧的授课格 | `schedule_handle.py:229~262`、`:473~504`；`class_ai.py:111`、`:134`；`handle_premise/__init__.py:313~315`、`:341~343`；`StateMachine/default.py:455~461`；`auto_schedule.py:118` | 已复现（代理）：前教师改学生岗后 CVP `CourseType` 读成旧授课格的实践课 |
| L7 | **同班同学收成年（104）的女儿**。同胞只取幼女 / 萝莉（Plan 26 口径 5：「婴儿和已成年的少女都不合适」），同学只要求有阶段素质；仍在学生岗的成年姐姐会被点成幼女 41「班上的{TargetName}」这类事件的对象 | `growth_event_handle.py:137`、`:97`；`education_constant.py:490` | 已复现（代理）：幼女 41 的互动对象是成年姐姐 |
| L8 | **排实操课页的「本节选修本教室的学生」不按实操课门槛**：H 模式实行值不足的成年学生算作会来，开课时进不了课堂；同一页的必修名单已按门槛判 | `class_schedule_panel.py:468~486`、`:560`；`sex_class_handle.py:386` | 已复现（代理） |
| L9 | **玩家手动授课只剩开发占位地文**。512 对玩家手动授课按所在教室判课型、科目回落学识，CVP `Course` / `CourseType` 没跟上（只认当天临时课的教室），522 条授课口上全判不过 | `Settle/default.py:7599~7604`；`handle_premise/__init__.py:302~352`；`schedule_handle.py:493~498` | 已复现：CVP 两项为 -1，能匹配的授课口上只剩占位行 |
| L10 | **写学期成绩的日常事件与前提对不上**。<br>• 萝莉 1「拿着这学期的成绩单……学识还算说得过去，战斗课几乎垫底」只要累计听课 ≥ 20；萝莉 20「这次的成绩单上……掉了两级」只要有课，而科目只升不降（降级只有刻印），成绩单也只记涨了的科目；萝莉 26「成绩单同一天发下来」只要有同胞。学期中途、一份成绩单都没有的萝莉照样抽到。<br>• 萝莉 6「这学期的出勤表……一节课都没落下」读的是终身出勤率 | `data/official_event/萝莉.csv:6`、`:11`、`:25`、`:31`；`semester_handle.py:168`；`growth_handle.py:726~731` | 已复现（代理）：学期第 10 天、没有成绩单的萝莉候选里有萝莉 1 / 20，加同胞有 26；终身 50/55、本学期 4 听 5 缺的候选里有萝莉 6 |
| L11 | **点名具体课型的日常事件只挂 `self_have_any_course`**：萝莉 7（体育课）、8（实习课第一次上岗，里程碑、权重 20）、9（兴趣课）、16（实践课）、幼女 22（实践课）；幼女 1「第一次坐进理论教室」读累计听课 ≥ 1（Plan 29 起体育 / 兴趣课也计出勤）。现有 token 里能判课型的只有 CVP `CourseType`，读的是此刻这一节，而日常事件在 0 点推送 | `data/official_event/萝莉.csv:12~14`、`:21`；`幼女.csv:6`、`:27`；`handle_premise_other.py:1238~` | 已复现（代理）：只排理论课的萝莉候选里有 7 / 8 / 9 / 16；只排体育课的幼女候选里有幼女 1 / 22 |
| L12 | **口上里「第一次 / 老学生」读错计数**：实操课到场 1053 / 1054、旁观 1054 / 1055「上过很多次实操课」读累计听课节数（含全部课型），到场 1055 / 1056「第一次来上这种课」要全部课型累计 ≤ 3；翘课 1004「第一次真的没去」不看累计翘课数 | `data/talk/sex/sex_class/join_sex_class.csv:59~62`；`watch_sex_class.csv:60~61`；`data/talk/work/skip_class.csv:10`；`growth_handle.py:722` | 已复现（代理） |
| L13 | **正文写具体时点、前提不限时点**：通用 3「今天是{Name}的生日」任意一天都能抽到（全仓库没有生日前提）；通用 15「季月交替的这几天」不看学期进度；婴儿 4「断奶的日子到了」出生当天就能抽到，也可能晚于婴儿 50「断奶之后……」 | `data/official_event/通用.csv:8`、`:20`；`婴儿.csv:9`、`:55`；`character.py:42` | 已复现（代理） |
| L14 | **档位 3（无课可评）的新成绩单只剩两条兜底口上**，都在讲「这学期每门课的心得」「那门课我上得最认真」。Plan 29 / 30 之后，整学期不在学生岗的萝莉每学期都会收到一份写着「没有上课」的成绩单 | `data/talk/daily/check_report_card.csv:10~11`；`semester_handle.py:208`、`:252` | 已复现（代理） |
| L15 | **授课 / 听课的占位地文不只在兜底时出现**。一期方案写「占位行只在所有具体前提都不成立时兜底（实施后确认）」；实际口上按前提条数分权重组、组间再按权重加权抽取，占位行（权重 1）与正式口上（权重 2~4）同场抽，NPC 教师开讲时约 1/3 的机会抽中「{Name}触发了授课指令的地文」 | `data/talk/work/teach.csv:6`、`attent_class.csv:6`；`talk.py:156~166`、`:241`；`value_handle.py:26`；一期方案 459 行 | 已复现（代理）：NPC 教师开讲时权重组 {1: 1 条, 2: 7 条}，3000 次抽中占位 1014 次（33.8%） |
| L16 | **公务事件校验工具的期末桶与未成年桶规则有漏洞**：期末桶只禁养成数值 4 / 5 / 6，同样在推送时恒定的 9（学期进度，恒为 0）与 23（成绩单待查看，恒为 1）不拦；`CHILD_SUB_KEY`、`DORM_SUB_KEY` 不含只推给幼女 / 萝莉的期末桶 | `tools/official_event_check.py:46`、`:52`、`:60`、`:390~403` | 已复现（代理）：构造的违规行都不报错；对照放进萝莉桶会报 |
| L17 | **ArkEditor 前提表 3 行描述截断在「（Plan」**（同胞、母亲可跟随、跟随见学），生成器按第一个空格切；重跑还会把 Plan 30 手工修好的 3 行也截回去 | `tools/ArkEditor/csv/Premise.csv:2027`、`:2029`、`:2030`；`buildata.py:147` | 已复现（代理） |
| L18 | **过期注释与文档**：<br>• `push_semester_event_for_list` 注释与说明文档 §6 第 200 行仍写「已成年的女儿照旧出成绩单」（Plan 30 Q1 已改）；<br>• `handle_self_have_classmate` 的 docstring 没跟上 Plan 30 的收窄；<br>• `get_now_course` 的返回说明漏了「兴趣课读书借不到书」；<br>• `official_event_check.py` 里 `TEXT_DUP_LEN` 的 docstring 游离在 `PLACEHOLDER_RE` 之后 | `growth_event_handle.py:352~353`；`.github/prompts/数据处理工作流/生长养成系统.md:200`；`handle_premise_other.py:1192`；`schedule_handle.py:377`；`tools/official_event_check.py:70`、`:82~84` | 已复现（代理，读文本） |

**待定 Q1**：见 §3.1。H1 的两个变体一起修（推荐），还是只修「拉回去重复结算」、先到的学生仍等教师到场才结算？
**回答**：学生坐下时就结算（推荐）

**待定 Q2**：见 §3.2。通用 59 / 60 怎么推？
**回答**：成年结算时推入（推荐）

**待定 Q3**：见 §3.3。实操课门槛遇到催眠补正时，只判不扣（推荐），还是门槛不认催眠补正？
**回答**：只判不扣（推荐）

**待定 Q4**：见 §3.14。事件与口上的正文、前提对齐到什么程度？
**回答**：全部对齐（推荐）

### 2.3 排查过、没有发现问题的疑点

留给下一轮复查参考，免得重复排查：

| 疑点 | 结论 |
| --- | --- |
| Plan 30 新代码的死代码、未用 import、TODO、对已翻译常量再包 `_()` | 没有：新增函数都有生产调用方，新文案的 `_()` 只包模板串，Education_System 里没有 TODO / FIXME |
| `judge_adult_out_of_school` 写死阶段素质 104、714 的 45 分钟、623 的状态 18 / 19 | 阶段 id 就是成长链的定义本身（`education_constant.py:50~53`），45 与状态号是 Plan 22 留下的，不在岗位 / 行为 / 状态机 / 娱乐 cid 之列 |
| 校验工具把 200、{4,5,6}、15 从 `education_constant` 另抄一份 | 按设计：工具不启动游戏、不 import 游戏模块，docstring 注明了与常量一致 |
| 夹具与真实创建路径的差异（素质 6、`child_id_list`、惰性 `child_growth`、体力 100、改岗不调 `update_work_people`） | 都碰不到 Plan 30 的路径；另见 §2.5-3 本轮复现踩到的两处夹具陷阱 |
| `set_time` 把全部角色的开始时刻同步成 `cache.game_time`，测试分不出开课时刻与学生行为开始时刻 | 真实循环里 NPC 的开始时刻不晚于 `cache.game_time`；`settle_absent` 与三个出勤写入点都用 `get_class_period`，节次口径一致（提前开讲的例外见 L3） |
| Plan 30 新增的断言有没有走到它声称覆盖的路径 | 都走真实路径（`dispatch` 整条 AI 链、真实效果器、真实事件表） |
| 改岗理由的推断「本学期有出勤 / 缺课记录就说明在学生岗待过」会不会被非学生岗的记录污染 | 不会：缺课与出勤的写入点都要先过学生岗 |
| 被抓后正在进行的翘课行为（tag 为工作）会不会被截短规则 B 截掉 | 常见情形不截（离开时刻落在本节、本节有课即置 None）；跨进空节时截到下一节开课前 20 分钟，属合理的提前动身 |
| `settle_course_attend` 本节已缺课时直接返回、不写 `last_attend_period` | 不会重复记：同一节再派 716 仍先判已缺课 |
| 萝莉 15 等按累计缺课写的事件，在翘课计缺课之后口径对不对 | 对得上：萝莉 15 读累计缺课（含翘课），萝莉 2 已改读编号 24 |
| 总纲 §16、索引、说明文档 §16 与 README 的计数 | 都跟上了 Plan 30 |
| 节次外当场开实操课、课表不在这间教室的学生被拉入课堂也记出勤 | 与 Plan 27 决策 3 同一口径 |
| 教室满员挡人 | 触发不到：理论 / 实践教室上限 50 人，大礼堂 100 人 |
| 见学的幼女追母亲时母亲在锁门的房间里 | 没发现系统性触发，属地图系统既有行为 |
| 623 用 `cache.game_time` 记被抓日期，跨午夜的一步里会记成次日 | 只让次日整天不再翘，与「夜间撞见翘课也触发」（总纲 §10.2）同类，不单独报 |
| 白天小睡时婴儿长成幼女，当天上的课先于第一次学期基线 | 按设计：从第一次被学期结算看到的那天起算 |
| 同一节先记出勤、后记缺课的倒序双记录 | 正常流程触发不到（听课、自习、716 都截到节末）；唯一的路径是 H1 的倒拉重走 |
| 557 结算时教师还在同一间教室讲上一节 | 不会多记：557 先结算下一节，之后 303 拉她时 512 去重返回 |
| 计数与标记还有别的写入点（调试面板、读档迁移） | 没有：`attend_class_count` 3 处、`absent_count` / `skip_count` / `last_absent_period` 各 1 处、`last_attend_period` 2 处、`skip_caught_day` 1 处、`skip_class_flag` 3 处、`report_card_flag` 2 处、学期基线 1 处 |
| 临时实操课的覆盖层泄漏进每周数据 | 没有：写每周数据与判真课的地方都传 `include_temp=False` |
| 716 复用娱乐行为时漏了原状态机的前置步骤 | 可排兴趣课的 `ENTERTAIN_*` 只写对象、行为、时长与状态；读书的借书已抽成 `prepare_npc_read_book` |
| 派活地点未开放导致 `wait_open` 空转（561、715、自习回落） | 没发现新情形 |
| 截短规则会不会反复截同一个行为、不收敛 | 不会：截出的结束时刻让下一轮检查命中 break |
| 722 / 10014 直接写 `is_h`，没走群交的 376 效果串 | `is_h` 不参与 normal 1~7，异常位掩码不会过期 |
| `calculation_instuct_judege` 是否含随机数 | 没有，同样输入同样结果；它的问题是写数据（M1） |
| 平然（4）、空气（5）催眠下的成年学生走门槛会不会扣理智 | 不会：normal 5 / 6 在调用实行值之前就挡掉 |
| 外勤 / 外交跨过学期切换的女儿，成绩单漏出或错标 | 回岛后第一次跨天补出离开时那个学期的一份，内容正确，只是晚出 |
| 装袋、临盆、产后的学生被 303 拉进听课 | 不会：装袋离开地图，临盆 / 产后每次行动前被瞬移回住院部 |
| 养成事件派发名单与队列容量对婴儿、离线孩子、非女儿的过滤 | 与 Plan 28 口径一致 |
| 心控（7）的教师 | 同口径：无意识 7 不在 normal 5 / 6 里，照常走班授课 |
| `get_scene_student_list` 把婴儿或非学生岗拉进课堂 | 不会：门槛第一步判学生岗 |
| 「有课」前提与同学名单的取数口是否纯函数 | 是：直接读 `child_growth`，`judge_selected_cell_real` 只读 |
| 开课、10014、722 三处是否重复记出勤 | 不重复：只在开课与 722 记，10014 不记 |
| 外勤委托的人员筛选没有排除幼女、萝莉 | 属外勤系统；养成侧的后果见 L2 |
| 检查成绩单分档口上带 `Growth\|23_E_1`，550 会清 flag | 不是死内容：先出口上再跑效果 |
| 炫耀口上 `CourseShowOff` 是否因 622 先清空待炫耀而判不过 | 不会：先出二段口上再跑效果（腰技另见 M4） |
| 节次外当场开课时开课口上的 `Course\|7x`、预约 / 当场前提取不到 | 取得到：开课先置 running 再结算行为 |
| 下课口上的提前 / 按时 / 拖堂在 10015 之后才判 | 不是：口上先于 10015 |
| 实操课开课 / 下课口上挂了只对孩子成立的 A1 前提 | 没有 |
| 兴趣课 16 项的幼女口上因娱乐 need 不符而死 | 不死：只有过家家带 need，且限幼女 / 萝莉 |
| 实习课口上的 17 个场景前提与可实习岗位 | 一一对应 |
| 检修工程师带教口上 3 条触发不到 | 一期 §9.1 已记为「暂不触发」 |
| 期末 9 / 10、萝莉 2 是否已按 Plan 30 改 | 已改 |
| 授课指令 2010 的前提与拉人口径 | 一致：都用 `judge_student_pullable` 且排除已在听课的 |
| target 505 / 515 与组 07 / 08 的行数、互斥 | 与说明文档 §4 一致 |
| 期末 11「没有一栏特别难看」与待努力相悖 | 「栏」可理解为各科水平，不报 |
| 成年后不在学生岗、有待查看成绩单的女儿，养成总览提示「用检查成绩单指令」 | 指令对她可用，看完才不可用，与提示一致 |
| 时停中玩家授课，拉人不看 normal（时停下全体 NPC 都是异常 6） | 时停本就放行大多数指令（`InstructConfig` 只有 10 条挂 `TIME_STOP_OFF`）；学生每节只结算一次，刷不了收益 |
| 截短规则 A 与 SEX_PENDING 不看翘课：挂 flag 的选修生被截回实操教室，开课那一刻再走 | 按设计：预到岗排在两道闸之前，玩家按时开讲时她人在场就被拉进课堂（Plan 25 决策 1、Plan 26 §3.5）；只有玩家不开讲她才掉头 |
| 截短规则 B 不预掷下一节的翘课骰子：注定翘掉的那一节照样被赶去教室 | 不改：翘课是开课那一刻才决定的事，提前掷会把「临时起意」变成「早有预谋」；今天已翘课的另见 L1 |
| 死代码 | 见基线 |

### 2.4 可复用的既有实现

| 需求 | 现成实现 |
| --- | --- |
| 同一节只结算一次 | `growth_handle.settle_student_class_gain` 的 `last_attend_period` 去重（H1 放宽 557 后，512 靠它不重复发） |
| 教师「这节能不能到岗」 | `class_ai.judge_teacher_available`（H1 的学生侧结算、M3 的收紧都在它上面） |
| 听课行的门槛 | `handle_premise.handle_normal_all_except_special_hypnosis`（L5 照抄） |
| 「这一格是不是真课」 | `growth_handle.judge_selected_cell_real`（L11 的按课型查课表在它上面加课型判断） |
| 某天某节的开始时刻 | `sex_class_handle.get_period_start_time`（L3） |
| 翘课 flag 的日期 | `skip_caught_day` 的写法（Plan 30：存日期序数、次日自然失效） |
| 新字段的存档兼容 | `save_handle._normalize_loaded_save_paths` 按 `CHILD_GROWTH` 属性表整体回填 |
| 事件表防复发 | `tools/official_event_check.py` 的 `check_semester_premise` / `check_row` |
| 成年结算推事件 | `growth_event_handle.push_graduation_event` |

### 2.5 已知陷阱与硬约束

1. **前提必须是纯函数**（Plan 24 §2.6-1）：M1 修的正是这一条；新增的课型前提、生日前提只读 `child_growth`，不走会惰性创建的 `get_child_growth`
2. **NPC 按各自的时间线推进，玩家一步可以跨过整节**：判定一律用行为开始时刻；303 改别人的开始时刻时要防时间线倒退（H1）
3. **两处夹具陷阱**（本轮复现踩到，收尾时写进测试 README）：
   - `clothing.get_npc_cloth` 对部分 cid 一件都穿不上，`normal_4` 不成立，工作链与娱乐链的目标行全不跑，NPC 只会原地待机（代理脚本的 R1 等组因此没跑出来）
   - 夹具体力上限 100，一节课就耗到 1，下一节去睡觉；跑行为循环的复现要把体力 / 气力设成真实量级
4. **跨天结算在 NPC 阶段之后**（`character_behavior.py:78~80`）：凡是靠跨天清的标记，一步跨过午夜时 NPC 已按旧值跑完新一天的早上（L2 用日期兜住翘课 flag）
5. **口上按权重组抽**：前提条数就是权重，`high_1` 占位行权重为 1，组间按 `random.choices(权重, weights=权重)` 抽（L15）
6. **公务事件表是编译产物**：改 `data/official_event/*.csv` 后要重建 `data/Official_Event.json`；测试引导 import 的增量构建会重建

## 3. 设计决策

### 3.1 教师晚到的那一节由学生侧先结算（H1，推荐口径 1；Q1）

- **557 放宽**：学生开始听课时，本节授课教师 `judge_teacher_available` 成立，就按与 512 相同的口径结算（科目、课型取课表，速度系数按师生等级差），不再要求教师此刻已在同一教室、正在授课。教师「能到岗」本就是学生坐下来等她的判据；判过了，这一节就算上了。
- **303 不倒拉**：`judge_student_join_class` 增加一条：学生当前行为的开始时刻晚于教师的开讲时刻（她的时间线已走到后面）就不拉。开课前在教室里等候的、与教师同时或更早开始当前行为的学生照拉，时刻照对齐。
- 512 仍在教师开讲时给在座的学生发；已由 557 结算过的，靠 `last_attend_period` 去重。
- 557 另有两道防护（实施时补）：学生须在本节的教室里（被玩家拉到别处听课的由玩家的广播结算）；课表没排教师（-1，自习）与授课者为玩家（0，临时实操课是课堂 H）的不走 557。

| 候选 | 弃选原因 |
| --- | --- |
| 只修倒拉（303 不拉时间线在前的学生），557 不放宽 | 重复结算没了，但教师晚到、玩家一步跨满一整节时，先到的学生仍整节白上 |
| 303 取消拉人、全交给 557 | Plan 25 §3.5 已弃选：拉人会对齐时刻、压掉每个学生各自一条听课口上 |
| 303 开讲时给「课表排在这间教室、此刻不在教室」的学生补结算 | 学生可能已在别处上下一节，隔空结算与出勤去重交错，比放宽 557 复杂 |
| 教师晚到就让学生降级自习 | 教师来不来要到场才知道；「能到岗」的判据就是为了让学生等她 |

代价：教师若在这一节里被临时叫走（例如被玩家拉进 H），学生照样拿到这节课。与「能到岗」判据的既有含义一致（Plan 24 §3.4 不同步需求与服装，也是按「一节之内会回来」处理）。

### 3.2 通用 59 / 60 在成年结算时推入（M2，推荐口径 2；Q2）

- `push_graduation_event` 在推入毕业典礼与成年纪念（队首）之后，把通用 59 / 60 按普通顺序推到队尾：成年当天先看到毕业典礼，之后处理公务时再遇到这两条。
- 两条的 uid 进 `education_constant` 的新常量 `ADULT_EXTRA_EVENT_UID_LIST`，推入时仍过 `judge_event_can_enqueue`（一次性、已触发的不再推）。
- 两条不受队列容量上限约束：`push_official_event` 加关键字参数 `ignore_capacity`（缺省 False）。与毕业典礼、成年纪念一样一辈子只有这一次入口，成年那一刻队列若已满，按普通入队就永远丢了（实施时补，2026-09-13）
- 校验工具加一条：部门 15、sub_key 104 的行，uid 必须是成年结算显式推入的（通用 1 / 2 与这张表），否则报「成年桶只有成年结算显式推入的事件会出现」。

| 候选 | 弃选原因 |
| --- | --- |
| 日常派发对成年女儿开放成年桶，只抽没出过的一次性事件（除通用 1 / 2） | 要改名单过滤与容量；第五轮收窄名单就是为了不让成年女儿占容量，放回去要另立规则 |
| 删掉两条 | 内容本身写的就是成年后的里程碑，只是缺入口 |

### 3.3 实操课门槛的实行值只判不扣（M1，推荐口径 3；Q3）

- `calculation_instuct_judege` 加关键字参数 `settle_hypnosis: bool = True`：为 False 时，催眠补正照算（玩家理智够就加补正），但不扣理智、不累加今日消耗、理智不够时不清催眠。缺省为 True，其它系统的调用不变。
- `judge_can_join_sex_class` 传 `settle_hypnosis=False`。进了课堂之后每个 H 动作照常各自结算实行值与理智。
- 门槛从此是纯函数：面板刷新、前提求值、旁观名单、学生自己的决策都不再改数据；入课与听课两行不再可能同时成立。

| 候选 | 弃选原因 |
| --- | --- |
| 门槛不认催眠补正（实行值不足就进不了课堂） | 催眠中的成年学生从此进不了课堂，玩家既有的催眠玩法被挡 |
| 只在真正拉进课堂时（开课、722、邀请）扣一次，其余路径只判 | 同一个人面板上判能来、开课时却可能因理智不够被拒；拉人有三个入口，各扣一次的口径还要另定 |
| 调用前后存下再还原理智与催眠 | 还要还原玩家交互对象的异常位，治标不治本 |

### 3.4 空气催眠 / 木头人的教师判来不了（M3，推荐口径 4）

- `judge_teacher_available(teacher_id, classroom="")`：
  - 木头人（`hypnosis.blockhead`）一律判来不了：行动每轮被锁成原地等待。无意识 6（体控）本就不在 normal 5 / 6 里，原先对它的豁免不起作用，删掉豁免挡不住木头人，要显式判（实施前复核发现，2026-09-13）；逆推一开就进 H，本来就被 `is_h` 挡掉
  - 空气催眠（无意识 5，属 normal 6）只在她已身处 `classroom`（本节授课的教室）时豁免——那时授课行 220700 照样成立；`classroom` 为空时按不豁免判
- 两个学生前提 `self_course_teacher_available` / `unavailable` 传 `now_course["classroom"]`。

| 候选 | 弃选原因 |
| --- | --- |
| 空气催眠一律判来不了 | 人已在教室时 220700 能讲，判来不了会让学生白白自习 |
| 只挡木头人，空气催眠不管 | 在办公室被空气催眠的教师同样走不到教室 |

### 3.5 翘课日的两处口径对齐（L1，推荐口径 5）

- `get_course_stage`：本节没课、下一节 20 分钟内开课，但今天已翘课（§3.6 的 `judge_skip_class_today`）→ NONE，不去门口等。
- `get_student_leave_time` 的规则 B：今天已翘课的，不再整段豁免，而是把工作 / 娱乐行为截到**开课那一刻**（不是开课前 20 分钟，也不要求上课地点解析得出）。她在开课那一刻重新决策，判 SKIP → 714，记一节缺课。
- 截短规则 A（待赴实操课）维持不看翘课（§2.3）。

| 候选 | 弃选原因 |
| --- | --- |
| 只改 UPCOMING，B 维持豁免 | 空节里的长娱乐仍会盖过整节，「翘掉的每一节记一节缺课」（Plan 30 口径 1）漏节 |
| 让翘课行为自己延长到下一节 | 714 的 45 分钟是既有设计（Plan 30 §2.3），延长会让被抓、下课等时机都变 |
| 翘课日照常赶去门口 | 与规则 B 的注释相反，白跑一趟再掉头 |

### 3.6 翘课 flag 认日期（L2，推荐口径 6）

- 新字段 `skip_class_day`（挂上 flag 那天的日期序数，0 为没有）；549 置 flag 时一并写入。
- 新增只读判据 `class_ai.judge_skip_class_today(character_id, now_time=None) -> bool`：flag 为真且 `skip_class_day` 等于参照时刻（缺省取行为开始时刻）的日期。只读 `child_growth`。
- 全部读取点改走它：`get_course_stage`、`judge_student_pullable`、`get_student_leave_time`、`character_info_head` 的 `<翘>`、`growth_panel` 的标记、`second_behavior` 的 623 触发判定。623 与跨天结算照旧清 flag。
- 旧档里挂着的 flag 回填 `skip_class_day = 0`，读作「不是今天」，等于已清。

| 候选 | 弃选原因 |
| --- | --- |
| 跨天结算改为遍历全部角色清 flag | 只修离线那条；一步跨过午夜的那条仍在 |
| 把跨天结算挪到 NPC 阶段之前 | 行为循环主干，影响全部系统 |
| 把 flag 改成日期序数、去掉布尔 | 旧档是布尔值，读的地方也多；并存一个日期字段最省 |

### 3.7 提前开讲的实操课按那一节判缺课（L3）

`settle_attend`：有正在进行的实操课、且它的节次开始时刻晚于参照时刻（提前开讲），就按那一节的开始时刻判「本节已缺课」。开课（`start_sex_class`）与 722 两个调用点都经过它；节次外的当场课（节次 -1）照旧按参照时刻。

### 3.8 取数口按学生岗收窄（L4）

`get_course_at`：角色不在学生岗时返回 None。取数口统一收窄，下游全部跟上：`<课>` 的个人式课分支、CVP `Course` / `CourseType`、561 的学生分支、548 的计出勤、552 的实习课、实习导师前提认学徒。`get_course_stage`、`judge_selected_cell_real` 等已有的岗位判断保留（冗余无害）。

### 3.9 303 拉人过 normal 门槛（L5）

`judge_student_join_class` 在 `judge_student_pullable` 之后加 `handle_premise.handle_normal_all_except_special_hypnosis(student_id)`，与学生自己的听课行 220815 同口径。玩家「授课」指令（只用 `judge_student_pullable`）不变（Plan 25 §3.4：手动授课本来就是「对在场孩子」）。

### 3.10 残留授课格（L6）

- `get_now_teaching` / `get_upcoming_teaching`：非玩家且不在教师岗时返回 None（与 `get_teacher_duty` 同口径）。
- 全局课表面板与个人课表选课页：格子上的教师已不在教师岗时名字后加「（已离岗）」，不在岛上（不在 `npc_id_got`）时加「（不在岛上）」，灰字。
  - 全局周表一格只有 25 列，「学识技能/三字名（不在岛上）」放不下：格子里写短标注「（离岗）」「（离岛）」，悬停提示写全称与后果；两种都成立时标「已离岗」（改了岗的人回岛也不会再授课，一定要换人）；选科目页被临时课顶替时那行「每周课表这一格」同样标注（实施时定，2026-09-13）
- 一键排课维持只填空格（一期定下的「保护手排内容、幂等」），玩家看到提示后手动改。

### 3.11 同班同学只取幼女 / 萝莉（L7）

`get_classmate_list`：对方阶段须在 `SIBLING_PLAY_STAGE_SET`，与同胞同口径（Plan 26 口径 5 的理由：互动事件写的都是能一起玩的孩子）。

### 3.12 排实操课页的人数按门槛分开（L8）

选修名单再按 `judge_can_join_sex_class`（§3.3 之后是纯函数）分出一行：「另有 N 人会到场，但此刻进不了课堂（实行值不足或状态异常）：……」。「本节选修本教室的学生：N 人」只数能参加的。

### 3.13 玩家手动授课的 CVP 回落（L9）

`get_now_course_type` / `get_now_course_ability`：角色是玩家、行为是授课、`get_now_teaching` 取不到时，课型按所在教室（`get_course_type_by_classroom`）、科目取学识 45，与 512 同口径。两处共用 `schedule_handle.get_course_type_by_position` 与 `education_constant.FALLBACK_SUBJECT_ABILITY`（548 自习的回落也用它），不再各写一份（实施复审补）。

### 3.14 事件与口上对齐（M4、L10~L15，Q4 推荐）

| # | 做法 |
| --- | --- |
| M4 | 删 `show_off_waist_skill.csv`；`test_talk_data` 的炫耀覆盖改按女儿可学的 17 门（去掉 `MALE_ONLY_SUBJECT_SET`），并断言男性专属科目没有带女儿前提的炫耀口上 |
| L10 | 萝莉 1 / 20 / 26 加 `CVP_A1_Growth\|23_E_1&CVP_A1_Growth\|7_NE_3`（有待查看的新成绩单，且不是无课可评的档位 3；后一半为实施复审补）；萝莉 1 的正文与选项 2 去掉点名的「学识」「战斗」；萝莉 20「掉了两级」改为「一级都没涨」；萝莉 6 改读本学期：`CVP_A1_Growth\|4_GE_20&CVP_A1_Growth\|5_E_0&self_have_any_course` |
| L11 | 新增 5 个前提 `self_have_theory_course` / `self_have_practice_course` / `self_have_pe_course` / `self_have_interest_course` / `self_have_intern_course`（任一格是该课型的真课，走 `judge_selected_cell_real`）；萝莉 7 → 体育、8 → 实习、9 → 兴趣、16 → 实践；幼女 22 → 实践；幼女 1 → 理论（保留 `Growth\|0_GE_1`） |
| L12 | 新增累计实操课次数 `sex_class_count` 与养成数值 25（`settle_attend` 记出勤时 +1）；到场 1053 / 1054、旁观 1054 / 1055 改读 `Growth\|25_GE_5`，到场 1055 / 1056 改读 `Growth\|25_LE_1`；翘课 1004 加 `CVP_A1_Growth\|24_LE_1` |
| L13 | 新增前提 `self_birthday_today`（出生日的月、日与今天相同，读 `pregnancy.born_time`），通用 3 改用它（保留 `T\|101_E_0`）；通用 15 加 `CVP_A1_Growth\|9_GE_90`（季月最后几天）；婴儿 4 加 `CVP_A1_Growth\|3_GE_50`、婴儿 50 加 `CVP_A1_Growth\|3_GE_60` |
| L14 | `check_report_card.csv` 新增 4 条档位 3 口上（幼女 / 萝莉各 2，前提带 `Growth\|7_E_3&Growth\|23_E_1`）；1004 / 1005 加 `CVP_A2_Growth\|7_NE_3` |
| L15 | 删掉 `teach.csv` / `attent_class.csv` 的占位行：NPC 教师不再抽到开发占位；玩家手动授课由 §3.13 取到学识口上；成年学生听课没有口上时不出文本 |

| 候选 | 弃选原因 |
| --- | --- |
| 只收窄现有前提，不新增前提与计数、不改正文；写不出前提的留到下一轮 | L11~L13 的多数条目没有现成 token，留着就是继续抽错 |
| 本轮不动数据，只修代码 | 数据类问题正是本轮 M / L 的一半 |
| 占位行保留 | 与一期方案「只在兜底时出现」的承诺不符；全项目别处的占位行不动（§7） |

### 3.15 校验工具（L16）

- `SEMESTER_VALUE_ID` 扩为 {4, 5, 6, 9, 23}，报错文案补「9 推送当天恒为 0、23 推送时恒为 1」。
- `CHILD_SUB_KEY`、`DORM_SUB_KEY` 并入 200（期末桶只推给幼女 / 萝莉）。
- 成年桶规则见 §3.2。
- 各规则在 `test_talk_data` 里对构造的违规行断言报错、对照行不报。

### 3.16 编辑器前提表（L17）

- `Premise.csv` 3 行补全描述（去掉出处括注，写法同 Plan 30 手工修的 3 行）；本轮新增的 6 个前提同步加行。
- `buildata.constand_promise_2_csv` 按第一个空格切一刀（`split(" ", 1)`），描述里的空格不再截断。

### 3.17 注释与文档（L18 与各项说明）

- 代码：`growth_event_handle.py:352~353` 注释改写成 Q1 口径；`handle_self_have_classmate` 的 docstring 补「双方都在学生岗、同一格确有的课、只取幼女 / 萝莉」；`get_now_course` 的返回说明补借不到书、非学生岗；`TEXT_DUP_LEN` 的 docstring 归位
- 说明文档：
  - §1：`class_ai` 一行补「教师来不了的催眠状态、翘课日的两处口径、翘课 flag 认日期」；`sex_class_handle` 补「门槛只判不扣」
  - §2：字段表补 `skip_class_day`、`sex_class_count`
  - §3：`get_course_at` 对非学生岗返回 None；教师反查只认教师岗
  - §4：H1 的结算口径（557 放宽、303 不倒拉）；303 拉人过 normal；L1 的两处口径
  - §5：实操课出勤按那一节判缺课；累计实操课次数
  - §6：第 200 行的过期括注删掉
  - §8：成年结算推通用 59 / 60；同学只取幼女 / 萝莉；课型前提与生日前提
  - §12：养成数值 25
  - §13：授课 / 听课不再有占位行
  - §14：两个新字段靠属性表回填
  - §15：新增三条：「303 改别人的开始时刻要防时间线倒退」「凡是靠跨天清的标记，一步跨过午夜时会被带进新一天的早上」「门槛与前提里调实行值计算要传 `settle_hypnosis=False`」
  - §16：测试计数
- 测试 README：fixture 陷阱补 §2.5-3 的两条
- 索引文档：计划表那一行改成「plan_25 ~ plan_31」，补第十二轮一句
- Plan 22 总纲：追加 §17，一行指向本 Plan

## 4. 接口设计（实施的权威定义）

### 4.1 常量与字段

`education_constant.py`（养成数值一组末尾）：

```python
GROWTH_VALUE_SEX_CLASS = 25
""" 养成数值编号：累计实操课次数（Plan 31）。开课与开课后到场各记一次，与出勤同一处写入；口上里「第一次来 / 老学生」读它 """
```

`education_constant.py`（成年事件常量旁）：

```python
ADULT_EXTRA_EVENT_UID_LIST = ("通用59", "通用60")
""" 成年结算时在毕业典礼、成年纪念之后推入队尾的成年事件（Plan 31）。成年桶（sub_key 104）只有显式推入的事件会出现，校验工具据此拦截别的 uid """
```

`education_constant.py`（科目表之后，实施复审补）：

```python
FALLBACK_SUBJECT_ABILITY = 45
""" 取不到科目时回落的科目：学识。玩家手动授课（512）、日程自习（548）与 CVP 对玩家手动授课的回落共用 """
```

`game_type.CHILD_GROWTH`（放在 `skip_class_flag` 之后）：

```python
self.skip_class_day: int = 0
""" 翘课 flag 挂上那天的日期序数（date.toordinal()），0 为没有（Plan 31）。flag 只在这一天有效：
    跨天结算在 NPC 阶段之后才清 flag、离线的人跨天不清，靠它不把翘课带进另一天 """
```

`game_type.CHILD_GROWTH`（放在 `skip_caught_day` 之后）：

```python
self.sex_class_count: int = 0
""" 累计上过的实操课次数（终身累计，Plan 31）。与 attend_class_count 在同一处 +1（sex_class_handle.settle_attend），这一节已缺课的也不记 """
```

`constant_promise.Premise`（`TARGET_REPORT_CARD_CHECKABLE` 之后）：

```python
SELF_HAVE_THEORY_COURSE = "self_have_theory_course"
""" 自己有理论课：学生岗且个人课表上至少有一格是每周确有的理论课 """
SELF_HAVE_PRACTICE_COURSE = "self_have_practice_course"
""" 自己有实践课：学生岗且个人课表上至少有一格是每周确有的实践课 """
SELF_HAVE_PE_COURSE = "self_have_pe_course"
""" 自己有体育课：学生岗且个人课表上至少有一格是确有的体育课 """
SELF_HAVE_INTEREST_COURSE = "self_have_interest_course"
""" 自己有兴趣课：学生岗且个人课表上至少有一格是确有的兴趣课 """
SELF_HAVE_INTERN_COURSE = "self_have_intern_course"
""" 自己有实习课：学生岗且个人课表上至少有一格是确有的实习课 """
SELF_BIRTHDAY_TODAY = "self_birthday_today"
""" 今天是自己的生日：出生日的月、日与今天相同（2 月 29 日出生的按 2 月 28 日过） """
```

### 4.2 函数签名

| 模块 | 函数 | 变化 |
| --- | --- | --- |
| `class_ai` | `judge_teacher_available(teacher_id, classroom="") -> bool` | 体控不豁免；空气催眠只在人在 `classroom` 时豁免（§3.4） |
| `class_ai` | `judge_skip_class_today(character_id, now_time=None) -> bool` | 新增，只读（§3.6） |
| `class_ai` | `get_course_stage` | 翘课日的 UPCOMING → NONE；flag 改走 `judge_skip_class_today`（§3.5、§3.6） |
| `class_ai` | `judge_student_pullable` | flag 改走 `judge_skip_class_today`（§3.6） |
| `class_ai` | `judge_student_join_class` | 过 `normal_all_except_special_hypnosis`；学生行为开始时刻晚于 `now_time` 不拉（§3.1、§3.9） |
| `class_ai` | `get_student_leave_time` | 翘课日的规则 B 截到开课那一刻（§3.5） |
| `Settle/default` | 557 `handle_attent_class_add_just` | 教师 `judge_teacher_available(教师, 教室)` 即结算（§3.1） |
| `Settle/default` | 549 `handle_skip_class_add_just` | 置 flag 时写 `skip_class_day`（§3.6） |
| `second_behavior` | `judge_child_growth_second_behavior` | 623 的触发改判 `judge_skip_class_today`（§3.6） |
| `instuct_judege` | `calculation_instuct_judege(..., not_draw_flag=False, settle_hypnosis=True)` | 新增关键字参数（§3.3） |
| `sex_class_handle` | `judge_can_join_sex_class` | 传 `settle_hypnosis=False`（§3.3） |
| `sex_class_handle` | `settle_attend` | 提前开讲按那一节判缺课；记出勤时 `sex_class_count` +1（§3.7、§3.14 L12） |
| `schedule_handle` | `get_course_at` | 非学生岗返回 None（§3.8） |
| `schedule_handle` | `get_now_teaching` / `get_upcoming_teaching` | 非玩家且不在教师岗返回 None（§3.10） |
| `growth_handle` | `get_growth_value` | 读编号 25 |
| `growth_handle` | `judge_have_course_type(character_id, course_type) -> bool` | 新增，只读：任一格是该课型的真课（§3.14 L11） |
| `growth_event_handle` | `push_graduation_event` | 追加推入 `ADULT_EXTRA_EVENT_UID_LIST`（§3.2） |
| `growth_event_handle` | `get_classmate_list` | 对方阶段须在 `SIBLING_PLAY_STAGE_SET`（§3.11） |
| `handle_premise/__init__` | `get_now_course_type` / `get_now_course_ability` | 玩家手动授课的回落（§3.13） |
| `handle_premise_work` | `handle_self_course_teacher_available` / `unavailable` | 传 `now_course["classroom"]`（§3.4） |
| `handle_premise_other` | 6 个新前提 | §4.1 |
| `character_info_head` | `get_now_class_tip` | `<翘>` 改判 `judge_skip_class_today`（§3.6） |
| `growth_panel` | 待处理 / 标记栏 | 翘课标记改判 `judge_skip_class_today`（§3.6） |
| `class_schedule_panel` | `_edit_sex_class`、`_draw_week_table` | 选修人数按门槛分行（§3.12）；离岗教师标注（§3.10） |
| `course_select_panel` | `_select_course` | 离岗教师标注（§3.10） |
| `tools/official_event_check` | 常量与 `check_row` | §3.15、§3.2 |
| `buildata` | `constand_promise_2_csv` | `split(" ", 1)`（§3.16） |
| `official_event_handle` | `push_official_event(..., to_front=False, ignore_capacity=False)` | 新增关键字参数：追加到队尾时不受队列容量上限约束（§3.2，实施时补） |
| `schedule_handle` | `judge_schedule_teacher(character_id) -> bool` | 新增：玩家恒为真、NPC 要在教师岗；两个教师反查函数开头调它（§3.10） |
| `sex_class_handle` | `get_attend_judge_time(now_time) -> datetime` | 新增：正在进行的实操课是提前开讲的，取那一节的开始时刻（§3.7） |
| `handle_premise/__init__` | `get_player_manual_teach_course(character_id) -> Optional[tuple]` | 新增：玩家手动授课的（课型, 45）（§3.13） |
| `class_schedule_panel` | `get_teacher_absent_mark(teacher_id, short=False) -> str` | 新增：离岗 / 离岛标注，周表格子用短写（§3.10） |
| `buildata` | `build_promise_csv_text(line_list) -> str` | 新增：前提表的生成抽成纯函数，测试用 ast 取出执行（§3.16） |
| `schedule_handle` | `get_course_type_by_position(position) -> int` | 新增：按所在位置判课型，不在三类教室按理论课；512 与 CVP 的回落共用（§3.13，实施复审补） |
| `class_schedule_panel` | `fit_text_width(text, width) -> str` | 新增：按显示宽度截文本，周表格子先截教师名再拼标注（§3.10，实施复审补） |

### 4.3 数据行

| 文件 | 行 | 改为 |
| --- | --- | --- |
| `data/official_event/萝莉.csv` | cid 1 | 前提 `CVP_A1_Growth\|0_GE_20&CVP_A1_Growth\|23_E_1&CVP_A1_Growth\|7_NE_3`；正文「学识那一栏还算说得过去，但战斗课的成绩几乎垫底」→「有一门还算说得过去，另一门几乎垫底」；选项 2「指出她战斗课确实没认真上」→「指出她那门课确实没认真上」 |
| 同上 | cid 6 | 前提 `CVP_A1_Growth\|4_GE_20&CVP_A1_Growth\|5_E_0&self_have_any_course` |
| 同上 | cid 7 / 8 / 9 / 16 | 前提 `self_have_pe_course` / `self_have_intern_course` / `self_have_interest_course` / `self_have_practice_course` |
| 同上 | cid 20 | 前提 `self_have_any_course&CVP_A1_Growth\|23_E_1&CVP_A1_Growth\|7_NE_3`；「掉了两级」→「一级都没涨」 |
| 同上 | cid 26 | 前提 `self_have_sibling_child&CVP_A1_Growth\|23_E_1&CVP_A1_Growth\|7_NE_3` |
| `data/official_event/幼女.csv` | cid 1 / 22 | 前提 `CVP_A1_Growth\|0_GE_1&self_have_theory_course` / `self_have_practice_course` |
| `data/official_event/通用.csv` | cid 3 / 15 | 前提 `CVP_A1_T\|101_E_0&self_birthday_today` / `CVP_A1_Growth\|9_GE_90` |
| `data/official_event/婴儿.csv` | cid 4 / 50 | 前提 `CVP_A1_Growth\|3_GE_50` / `self_mother_available&CVP_A1_Growth\|3_GE_60` |
| `data/talk/sex/sex_class/join_sex_class.csv` | 1053~1056 | `Growth\|0_G_10` → `Growth\|25_GE_5`；`Growth\|0_LE_3` → `Growth\|25_LE_1` |
| `data/talk/sex/sex_class/watch_sex_class.csv` | 1054 / 1055 | `Growth\|0_G_10` → `Growth\|25_GE_5` |
| `data/talk/work/skip_class.csv` | 1004 | 前提加 `&CVP_A1_Growth\|24_LE_1` |
| `data/talk/daily/check_report_card.csv` | 1004 / 1005；新增 1014~1017 | 加 `&CVP_A2_Growth\|7_NE_3`；新增 4 条档位 3 口上 |
| `data/talk/work/teach.csv`、`attent_class.csv` | 占位行 | 删除 |
| `data/talk/system/second_show_off_study/show_off_waist_skill.csv` | 整个文件 | 删除 |
| `tools/ArkEditor/csv/Premise.csv` | 2027 / 2029 / 2030；新增 6 行 | 补全描述；新前提 |

## 5. 行为对照

| 情形 | 现行为 | 改后 |
| --- | --- | --- |
| 教师换教室晚到，玩家一步跨满一整节，学生下一节在别处 | 这一节零收益、出勤缺课都不记 | 学生坐下时就结算，出勤 +1 |
| 同上，学生下一节还在这间教室 | 被拉回教师开讲时刻，下一节结算两次 | 不拉回，两节各一次 |
| 玩家一步短于一节（常见情形） | 303 拉人、512 结算 | 学生坐下时 557 先结算，303 照拉、512 去重；出勤与收益不变 |
| 心控中的成年学生，玩家在实践教室刷新指令面板 | 每刷新一次扣理智；理智耗尽时静默解除催眠 | 不扣、不解除；门槛结果照旧（理智够就能进） |
| 女儿成年 | 只推毕业典礼、成年纪念 | 另推通用 59 / 60 到队尾 |
| 教师在办公室被空气催眠 / 被木头人 | 学生坐下听课、零收益 | 学生降级自习、计出勤 |
| 空气催眠、人已在教室的教师 | 能开讲 | 不变 |
| 今天已翘课、开课前 20 分钟内空下来 | 走到教室门口等，开课再掉头 | 不去；开课那一刻判翘课 |
| 今天已翘课、空节里看 120 分钟电影 | 盖过下一节，整节不记缺课 | 截到开课那一刻，判翘课、记缺课 |
| 23 点睡到次日 10 点，昨天翘过课 | 次日上午每节都判翘课 | 按当天重新掷 |
| 翘课当天去外勤、几天后回岛 | 回岛那天整天判翘课 | 按当天重新掷 |
| 提前 5 分钟开讲预约的实操课，学生上一节缺过课 | 出勤记不上 | 照记 |
| 改任厨师的女儿在厨房上班 | 残留的实习节次显示 `<课>`，CVP 读成实习课 | 不显示、读 -1 |
| 303 开讲时教室里有跟随中 / 有需求的学生 | 拉成听课 | 不拉，她自己决策 |
| 前教师改当学生 | CVP 与 561 按旧授课格取课 | 按自己的课表 |
| 课表上挂着已离岗的教师 | 面板照写名字 | 名字后标「（已离岗）」（周表格子写短标注「（离岗）」，悬停看全称） |
| 成年姐姐与幼女妹妹同班 | 姐姐被点成「班上的孩子」 | 不算同学 |
| 实行值不足的成年学生选修了实践教室 | 排课页算作会来 | 单列「此刻进不了课堂」 |
| 玩家在理论教室手动授课 | 只有「博士触发了授课指令的地文」 | 学识授课口上 |
| NPC 教师开讲（玩家在场） | 约 1/3 是占位地文 | 只有正式口上 |
| 学期中途、没有成绩单的萝莉 | 抽得到「拿着这学期的成绩单」「掉了两级」 | 有待查看的新成绩单、且不是档位 3（这学期没有上课）时才抽到 |
| 只排理论课的萝莉 | 抽得到体育 / 实习 / 兴趣 / 实践课的事件 | 只抽得到自己有的课型 |
| 上过 20 节普通课、第一次上实操课 | 口上写「老学生」「不是第一次上实操课」 | 写「第一次来」 |
| 任意一天 | 可能抽到「今天是{Name}的生日」 | 只在生日那天 |
| 萝莉整学期担任厨师，检查成绩单 | 口上讲「这学期每门课的心得」 | 档位 3 专属口上 |
| 腰技炫耀 | 52 条口上永远不出 | 删掉 |

## 6. 风险与注意事项

| 风险 | 说明 | 对策 |
| --- | --- | --- |
| H1 让学生在教师到场前就拿到收益 | 教师判能到岗、这一节却被临时叫走时，学生照拿这节课 | 与「能到岗」判据的既有含义一致；说明文档 §4、§15 写明 |
| H1 的 303 不倒拉 | 时间线在前的学生不再被教师对齐时刻，可能多出一条她自己的听课口上 | 只在玩家一步跨满一整节时出现；Plan 25 §3.5 的顾虑（同屏刷出一串口上）只在这种少见情形里出现 |
| M1 改了其它系统的共用函数 | `calculation_instuct_judege` 被全仓库调用 | 新参数缺省为 True，其它调用不变；只有养成门槛传 False |
| `get_course_at` 收窄 | 下游 7 处都跟着变 | 逐处列在 §3.8；`test_schedule` / `test_class_ai` / `test_premise_tokens` 断言 |
| 两个新字段 | 存档结构变化 | 属性表整体回填；`test_save_compat` 断言 |
| 事件池与口上池变化 | 萝莉 1 / 6 / 7~9 / 16 / 20 / 26、幼女 1 / 22、通用 3 / 15、婴儿 4 / 50 的触发条件收窄 | 这是 Q4 的本意；`test_growth_event` 逐条断言 |
| 删掉占位行 | 成年学生听课、玩家在没有学识口上的教室授课时不出文本 | 与「没有写就不出」的口上惯例一致；其它系统的占位行不动 |
| 档位 3 的成绩单看过之后再检查 | 1004 / 1005 已排除档位 3，四条新口上只配新成绩单（养成数值 23 为 1），这时不出口上 | 同上；此前出的是讲「每门课的心得」的错文本（实施时确认） |
| 事件表是编译产物 | 改 CSV 后要重建 | 测试引导的增量构建会重建；口上改动后先删 `data/Character_Talk.json` 再 `buildconfig.py`（README） |
| 构建会写乱 PO | 本机无 gettext | 收尾 `git checkout -- data/po/` |

## 7. 不在本方案范围

- **口上占位行的权重组机制**：全项目 33 个口上文件都有「{Name}触发了X指令的地文」这种 `high_1` 占位行，按权重组参与抽取，属口上系统；本轮只删养成的授课 / 听课两条（L15）
- **成年（非女儿）学生的听课、翘课口上**：总纲 §5「成年后的其余专属内容」、§10.2「成年学生静默翘课」
- **日程自习（此刻没课）没有专属口上**：现有 468 条自习口上写的是「老师没来」，要另写一套，属内容扩充
- **换季首日一步睡过上课时间，那几节记进上学期成绩单**：跨天结算在 NPC 阶段之后是行为循环主干，改动面超出养成系统；L2 只兜住翘课 flag。已复现（代理）：9/30 23:00 一步走到 12/1 11:00，12/1 上午两节体育课记进秋季成绩单，新学期记成 0/0
- **一键排课替换已离岗的教师**：一期定下只填空格；L6 只加提示
- **别的前提与名单调实行值计算同样会扣理智、解除催眠**：`handle_premise/__init__.py:782~938` 的初级 / 严重骚扰、H 模式、群交 7 个前提，`drunk_sex_common.py:165`，普通群交的邀请名单（`group_sex_panel.py:748`、`handle_instruct.py:1466`）都以 `not_draw_flag=True` 调用。属前提系统 / 性爱系统；本轮新增的 `settle_hypnosis=False` 可以直接给它们用（实施代理报告、主代理核实）
- **`calculation_instuct_judege` 解除催眠时刷新的是玩家当前交互对象的异常位**：属催眠系统；养成门槛改走 `settle_hypnosis=False` 后不再触发
- 既往各轮 §7 的范围外事项（游泳不换泳衣、读书系统、身体管理的练习类、成长停滞后一次长大、保育员前提写死 153、总纲 §10.2 五条备忘、成绩单另列翘课节数等）
- Plan 24~30 留给用户的游戏内测试项

## 8. 追加调整

（实施后每轮追加一节，只写设计；实施记录见实施文档 §6.5。暂无）
