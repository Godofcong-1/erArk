# Plan 30（方案）：生长养成系统第十一轮复查

> 本 Plan 拆分为两个文件：**本文件为纯方案**（发现、现状调查、设计决策、接口设计、风险、范围外）；
> 逐文件改动步骤、构建、验证清单、回滚与实施过程记录见 `plan_30_生长养成系统第十一轮复查_实施步骤与记录.md`（下文简称"实施文档"）。
>
> 本 Plan 是 Plan 22（生长养成系统）、Plan 24（师生并入工作链）、Plan 25~29（第六~十轮复查）之后的又一轮全面复查，前述各 Plan 均在 `plan/done/`。
> 实施完成后在 Plan 22 总纲追加 §16，只写一行指向本 Plan。

- 状态：**已实施**（方案定稿 2026-09-13；同日用户确认：口径 1~5 按推荐，Q1 按推荐并追加「检查成绩单」指令的对象限制，见 §3.3；实施记录与偏离见实施文档 §6）
- 来源：用户需求 → "再进行一次检查，检查该系统是否有哪里仍有遗漏的未实现内容、BUG、死代码、待处理项等。依然仅由主代理调查和进行，不使用子代理进行"
- 口径（2026-09-13 用户已确认）：
  1. **翘课记缺课**：翘掉的每一节记一节缺课，与体力缺课同一节只记一次；另记累计翘课节数，萝莉 2「翘课的事被报了上来」改按翘课数判（§3.1）
  2. **期末 9 / 10 去掉「本学期出勤率 < 70」**：待努力就是出勤率 < 70，这一项推送时永远判不过；校验工具加一条防复发的规则（§3.2）
  3. **改岗理由按学期初的岗位分情形写**：本学期改的、整学期都不在学生岗的、中途回到学生岗的各写各的（§3.3）
     - 附问 Q1：**成年且整学期都不在学生岗的女儿不再出成绩单**（推荐）；备选维持每学期一份「本学期没有排课」
  4. **同一节只落一种记录**：这一节已记了缺课，回来上课照给收益、不计出勤（§3.4）
  5. **翘课被抓后当天剩余节次不再翘**（§3.5）
  6. 其余小修（§3.6~§3.8）
- 预计改动量：**约 30 个文件**，净增约 350 行
  - 逻辑 12 个：`education_constant`、`game_type`、`class_ai`、`growth_handle`、`semester_handle`、`schedule_handle`、`growth_event_handle`、`sex_class_handle`、`class_schedule_panel`、`StateMachine/default.py`、`Settle/Second_effect.py`、`handle_premise_other`
  - 数据 2 个：`data/official_event/期末.csv`、`萝莉.csv`；工具 1 个：`tools/official_event_check.py`
  - 测试约 10 个（含 README）；文档 4 个（说明文档、索引文档、Plan 22 总纲、`update.log`）
- 风险等级：**中低**。翘课开始计缺课会拉低常翘课孩子的出勤率与档位，这是本轮唯一的数值口径变化；Q1 若按推荐，成年后不在学生岗的女儿不再出成绩单。其余是判定收窄、文本修正与去重
- 适用代码快照：`master @ 90716619b`（Plan 29 提交之后）
- 前置：Plan 22 一~四期、第五轮复查、Plan 24~29 均已完成

---

## 1. 目标

1. 翘课在成绩单上看得见：翘掉的课计缺课，频繁翘课的孩子不再评良好 / 优秀；写翘课的养成事件按翘课数触发
2. 期末 9 / 10 能推出来，以后写期末事件不会再踩「推送时本学期已重置」这个坑
3. 改了岗的女儿，成绩单上的理由与她这学期的实际岗位经历对得上
4. 同一节课只落一种记录（缺课或出勤）
5. 翘课被抓后，当天剩余的节次回去上课
6. 改了岗的萝莉不再被判「有课」「有同班同学」，不再抽到写上课与同学的养成事件
7. 小修：必修名单的顶替标记不随书库借阅状态忽隐忽现；说明文档里过期的写入点计数

**验收标准**：
- 全套回归测试通过，新增断言覆盖 §3 每一条
- 复现脚本（实施文档 §2.0）改前 39 项全部成立；改后 18 项问题命中不再成立，R1-2 随 Q1（按推荐不出成绩单即不再成立），其余 20 项（前提、对照、数据事实）照旧
- `test_talk_data`、`tools/official_event_check.py` 通过（含新增规则）
- 行为循环测试收敛，上午四节人均出勤 ≥ 3 节不变

## 2. 现状调查

本轮读过的范围：
- **`Education_System/` 全部 15 个模块**：逐行重读，含 Plan 29 新加的函数
- **外部挂接点**：
  - `handle_npc_ai`：见学 / 工作链入口、`judge_interrupt_character_behavior`、`get_chara_entertainment`
  - `StateMachine/default.py`：401、561、303、304、713~722
  - `Settle/default.py`：511 读书、512、548~557、10014、10015；`Second_effect` 622 / 623
  - `past_day_settle`、`realtime_settle`（提醒与 `settle_rest`）、`settle_behavior`（旁观、CVE Growth）、`common_default`（主修加成）、`handle_ability`、`second_behavior`
  - `handle_premise`：work 的 19 个师生前提、`__init__` 的 CVP Course / CourseType / Growth、H 的 12 条实操课前提、other / place / time / entertainment 里的教育前提
  - `character_info_head`、`handle_instruct`（授课、开课）、`group_sex_panel`、`manage_basement_panel`、`pregnancy_handle`、`born_event_panel`、`body_info_panel`、`official_event_handle`、`save_handle`、`borrow_book_panel`
  - 其余改岗入口：`manage_dormitory_panel`、`nation_diplomacy_panel`、`physical_check_and_manage`、`basement`、`character_handle`
- **数据**：`target.csv` 组 07 / 08；`Entertainment.csv`、`Book.csv` / `BookType.csv`；`Behavior_Data` / `Behavior_Effect` 的教育行为；`InstructConfig` 的 2010 / 2039 / 1036 / 5209 / 6021；`data/official_event/` 五张表的全部前提 token；`skip_class` / `second_caught_skip_class` / `check_report_card` / 炫耀口上

基线：
- 回归 15 个文件 1126 条断言全绿（2026-09-13，Plan 29 之后）
- 死代码扫描：Education_System 384 个函数 / 方法 / 常量，按代码 token 统计引用（去掉注释与字符串），只有注册式的三个函数没有直接调用方（说明文档 §15 第 10 条已写明）

下表的「已复现」都由 scratchpad 脚本在无头环境跑出（不入库，实施文档 §2.0 要求重建）。改前 39 项检查全部成立：18 项是问题命中，20 项是前提、对照与数据事实，另 1 项（R1-2，成年女儿照出 0/0 成绩单）随 Q1。

### 2.1 发现（中）

| # | 发现 | 证据 | 状态 |
| --- | --- | --- | --- |
| M1 | **翘课不计缺课**。<br>• 全仓库给 `absent_count` 加数的只有 `class_ai.settle_absent`，调用方只有体力缺课的 721。翘课走 714 → 行为 `skip_class` → 效果 549，只置翘课 flag、回落抑郁，不记缺课。字段注释也写着「体力不足被动缺课」。<br>• 成绩单的出勤率 = 出勤 /（出勤 + 缺课），翘掉的课两边都不进：<br>　- 上 1 节、翘 2 节的孩子，出勤率 100%、评「良好」；<br>　- 一学期全翘的孩子是「本学期没有排课」。<br>• 事件与口上都把翘课当缺课写：<br>　- 萝莉 2「{Name}翘课的事被教她的干员报了上来。这已经不是第一次了」的前提是累计缺课 ≥ 3，只有体力缺课能触发，真翘课的孩子一次都触发不了；<br>　- 萝莉 15「缺课的记录又添了几笔……宁愿去训练场跑圈」、口上里按终身出勤率 < 60% 写「这一课我没去」「她知道自己缺了很多课」的差分（80 行）同样只看体力缺课。<br>• 设计文档里「孩子频繁翘课说明养育方式出了问题」（一期方案 §3.19）这条反馈，在成绩单与事件上都落不了地 | `class_ai.py:159~177`；`StateMachine/default.py:2756~2785`（714）、`:2963~2974`（721）；`Settle/default.py:7724~7746`（549）；`game_type.py:392~393`；`semester_handle.py:196~215`；`data/official_event/萝莉.csv:7`（cid 2）、cid 15；`data/talk/system/second_show_off_study/*.csv` 的 `CVP_A1_Growth\|2_L_60`；一期方案 §3.19、§3.14 | 已复现：<br>• 心情闸必中 → 派 714，连翘三节，缺课数不变；<br>• 上 1 节、翘 3 节 → 出勤率 100%、良好；<br>• 翘过 3 节的孩子过不了萝莉 2 的前提，只因体力缺过 3 节的孩子过得了 |
| M2 | **期末 9 / 10 永远推不出来**。<br>• 两条的前提是「上一份成绩单待努力」且 `CVP_A1_Growth\|6_L_70`（本学期出勤率 < 70）。<br>• 期末事件在跨天结算里、`settle_semester_change` 之后才推送；那时这孩子的学期基线已重置到当前值，本学期是 0/0，出勤率按 100 算，这一项必判不过。<br>• 16 条期末事件里这两条是死内容：待努力的萝莉候选只有期末 11 / 13 / 14 / 16。<br>• 这一项本来也多余：待努力（`get_report_grade`）就是有课且出勤率 < 70 | `data/official_event/期末.csv:14~15`（cid 9、10）；`past_day_settle.py:111~113`；`semester_handle.py:339~364`（先冻结成绩单、再重置基线）；`growth_handle.get_growth_value` 编号 6；`semester_handle.py:196~215` | 已复现：<br>• 本学期 4/6 → 冻结的成绩单待努力、40%；<br>• 推送时编号 6 读出 100，期末 9 / 10 的前提都判不过；<br>• 对照：只留 `7_E_2` 就过得了 |
| M3 | **改岗理由在之后的学期写错**（Plan 29 引入）。<br>• `get_report_incomplete_reason` 只看结算这一刻的岗位，不是学生岗就写「X本学期改任了Y，改岗后不再上课，成绩单只计改岗前上过的课」。<br>• 学期结算遍历全部幼女 / 萝莉 / 少女期的女儿（`get_student_candidate_list`），成年后在别的岗位干了多久，就每学期收到一份这样写的成绩单：<br>　- 成年女儿整学期都在岗位 21，0/0、无课可评，理由却是「本学期改任了」；<br>　- 萝莉在 12 月学期中途改岗，那一学期写得对；到了下一学期，整学期都没当学生，仍写「本学期改任了」。<br>• 学期中途从别的岗位回到学生岗的情形，成绩单只计回来之后的课，却没有理由 | `semester_handle.py:218~238`、`:319~336`；`growth_handle.py:62~89`；`past_day_settle.py:111~119` | 已复现：<br>• 成年女儿整学期在岗位 21 → 理由「本学期改任了」、0/0；<br>• 对照：学期中途改岗的那一学期写得对；<br>• 下一学期整学期不在学生岗，仍写「本学期改任了」 |

### 2.2 发现（低）

| # | 发现 | 证据 | 状态 |
| --- | --- | --- | --- |
| L1 | **同一节既记缺课、又记出勤**。<br>• 体力闸在开课那一刻判：体力 < 30% → 721 记一节缺课、原地休息 30 分钟。<br>• 原地（不在休息室 / 宿舍）按 0.3 倍回复：上限 2000、28% 的孩子休完是 35%，上限 1000、20% 的是 31.7%。<br>• 休完这一节还剩 15 分钟，下一次决策过了体力闸就回去上课：716 / 557 按 `last_attend_period` 只防「出勤记两次」，不看这一节已经缺过课，于是再记一节出勤。<br>• 体力在 30% 附近来回的孩子，每遇这种节次就算一次缺课一次出勤，与成绩单「出勤 X 节 / 缺课 Y 节」的读法对不上 | `class_ai.py:159~177`；`StateMachine/default.py:166~176`（休息 30 分钟）、`:2963~2974`；`realtime_settle.py:405~433`；`growth_handle.py:229~318`、`:321~355`；`sex_class_handle.py:834~849` | 已复现（721 缺课 +1 → 原地休息 30 分钟回到 30% 以上 → 同一节 9:30 派 716 出勤 +1） |
| L2 | **翘课被抓后，当天剩余节次照样按概率掷骰**。<br>• 设计：被撞见「当场清掉，当日剩余节次回去上课」「孩子被逮住之后这一天就得回教室」（一期方案 §3.19）。<br>• 实现：623 只清 flag、加抑郁与恐怖；之后每一节 `roll_skip_class` 照常以「角色 + 日期 + 节次」掷骰，概率照旧（实测两档各加一节课的量，都没跨等级，25% / 45% 不变），同一天里还会再翘 | `Second_effect.py:3003~3022`；`class_ai.py:404~427`；一期方案 §3.19 | 已复现（被抓后 flag 清掉、概率 25% 不降；之后几天的同一情形里，后续节次都有掷中的） |
| L3 | **改了岗的萝莉仍被判「有课」「有同班同学」**。<br>• `self_have_any_course` 只看个人课表非空，`get_classmate_list` 只比对个人课表的格子，两处都不看岗位。<br>• Plan 24 定了改岗女儿的课表残留、不清理（改回学生岗即恢复），于是她：<br>　- 过得了幼女 14~26、萝莉 6~23 / 51 这批写「在上课」的事件的前提；<br>　- 仍是别的孩子的同班同学，同学事件（幼女 41~49、萝莉 4 / 24~35、通用 46~48、期末 4）会把她点成 {TargetName}。<br>• 每周课表清空后，个人课表全是「已停课」的孩子也照样判有课、有同学。<br>• 与 Plan 28 §3.4「选修人数只数学生岗」同一类遗漏 | `handle_premise_other.py:1237~1252`；`growth_event_handle.py:107~140`；Plan 24 §3.10；`data/official_event/` 各表 | 已复现（岗位 21 的萝莉：上课状态恒为 NONE，两个前提都成立；她的候选事件里有 24 条上课 / 同学事件；对照：学生岗照常成立） |
| L4 | **必修名单的「*会顶替」标记随书库此刻借没借空而变**。<br>• 指定必修学生时，个人式课这一格是不是确有的课用 `judge_personal_course_valid` 判（Plan 28 §3.5）。<br>• Plan 29 给它加了「读书课借得到书」：书库这一刻借空了，读书兴趣课那一格就不标「*」。<br>• 可顶替的是排在某一天的课，那天借不借得到书排课时不知道；Plan 29 自己也否决了在周表上标一时的借阅状态 | `class_schedule_panel.py:577`；`schedule_handle.py:646~663`；Plan 29 §3.2 | 已复现（书库有书时这一格成立；借空后同一格不成立） |
| L5 | 说明文档 §15 第 4 条写「三处写入点（学生结算 / 体力缺课 / 实操课出勤）」：Plan 29 已加了第四处（716 的体育 / 兴趣课出勤），本轮 M1 还要加翘课缺课 | `.github/prompts/数据处理工作流/生长养成系统.md` §15 | 读文档 |

**待定 Q1**：成年（少女期）后不在学生岗的女儿，每个学期照样出一份「本学期没有排课」的成绩单，学期结束提示里列出她的名字，养成总览挂「成绩单待查看」。Plan 26 §3.4 定的「已成年的女儿照旧出成绩单」那一轮讨论的是期末事件，没有讨论她已经不上学的情形。女儿一多，每季的学期结束提示会越来越长。
**回答**：成年后不在学生岗的女儿不再收到每学期的空成绩单，也不再能够对该女儿使用检查成绩单指令，但以前的成绩单照样能翻看。同时也不能对其他非女儿但依然在学生岗的角色使用检查成绩单指令。

### 2.3 排查过、没有发现问题的疑点

留给下一轮复查参考，免得重复排查：

| 疑点 | 结论 |
| --- | --- |
| 读书结算 511：难度 0 且书类型带经验的书读完时，`add_value` 没有赋值（`elif book_difficulty == 1` 写重了一支） | 现有书库只有一本难度 0 的书，类型「无」、不带经验，触发不到；属读书系统 |
| 兴趣课读完的书还拿在手上 | 读的是读完的书：没有进度，仍给习得与经验，按还书概率归还。与娱乐读书同一套既有行为 |
| 个人课表格子与 `<课>` 悬停对配置里不存在的兴趣 / 实习目标会 KeyError | 旧档娱乐改编号只动了 152~155，都不是可排兴趣课的项（`class_ok=0`）；可排兴趣课的目标从未改号，触发不到 |
| 「幼女只能当学生」只挂在基建面板，全仓库改岗入口有 8 处 | 舍管任命只从已在舍管岗的人里选；外交官候选要出身地或势力对得上外国，女儿的出身地与势力都是罗德岛（0），走不到；身体管理的练习类会把岗位改成性爱练习生，属身体管理系统，本轮未深查 |
| 实操课提前下课后，回原来那节课再记一节出勤 | 与 Plan 27 L2「同一节重开各记一次」同属实操课不做逐节去重的口径 |
| 体育 / 兴趣课在 716 派出时记出勤，迟到到场也记 | 与教室课晚到补结算（557）同口径 |
| 被抓加的抑郁与恐怖会不会把翘课率推高 | 实测四项各 600 → 抑郁与恐怖 735、各 1000 → 1175，都没跨等级，概率不变；L2 的问题在于被抓后照样掷骰 |
| 翘课行为 45 分钟、不截到节末（714），会不会跨过一整节不经过决策 | 不会。下一次决策落在下一节的同一偏移上，每节都会派发一次；逐节记缺课不会漏节 |
| 死代码 | 见基线 |

### 2.4 可复用的既有实现

| 需求 | 现成实现 |
| --- | --- |
| 同一节只记一次缺课 | `class_ai.settle_absent` 的 `last_absent_period` 去重（721 已在用） |
| 缺课记在状态机里 | 721 的写法（Plan 24：前提不能有副作用，记缺课挪进状态机） |
| 学期基线的唯一写入点 | `semester_handle.reset_semester_baseline`（第一次记账与学期切换都经过它） |
| 个人式课「这一格是不是课」 | `schedule_handle.judge_course_need_pass` + `get_course_place`（`judge_personal_course_valid` 里去掉借书那一步） |
| 教室课「每周课表这一格有没有课」 | `schedule_handle.get_class_cell(..., include_temp=False)` |
| 新字段的存档兼容 | `save_handle._normalize_loaded_save_paths` 按 `CHILD_GROWTH` 属性表整体回填，新字段不需要迁移 |
| 事件表防复发 | `tools/official_event_check.py` 的 `check_premise_text` |

### 2.5 已知陷阱与硬约束

1. **前提必须是纯函数**（Plan 24 §2.6-1）：`roll_skip_class`、新增的「这一格是不是真课」判定都在前提路径上，只读 `character_data.child_growth`，不走会惰性创建的 `get_child_growth`
2. **期末事件在学期基线重置之后推送**：推送那一刻，养成数值 4 / 5 / 6（本学期出勤、缺课、出勤率）读的是新学期（0/0，出勤率按 100）；刚结束的学期只能从成绩单读（编号 7 档位、8 升级门数）
3. **`last_absent_period` 被体力缺课与翘课共用**：同一节先判体力闸、再判心情闸，一节只会落进其中一种；翘课记缺课复用它，天然不会重复
4. **公务事件表是编译产物**：改 `data/official_event/*.csv` 后要重建 `data/Official_Event.json`；测试引导 import 的增量构建会重建（`auto_build_config.py:467`）
5. **学期结算只遍历 `npc_id_got` 里的女儿，含成年的**（`get_student_candidate_list`）；Q1 的收窄只能加在结算里，不能改这份名单（养成总览、日程批量套用也用它）

## 3. 设计决策

### 3.1 翘课记缺课（M1，推荐口径 1）

- 714 派出翘课行为（人已不在教室的那一支）时调 `class_ai.settle_absent(character_id, by_skip=True)`：
  - 与体力缺课共用 `last_absent_period`，同一节只记一次；
  - 这次确实记上了，再给新字段 `skip_count` +1。
- 新增养成数值 24 `GROWTH_VALUE_SKIP`（累计翘课节数），`get_growth_value` 读它。
- 萝莉 2 的前提改为 `CVP_A1_Growth|24_GE_3`（累计翘过 3 节）。
- 成绩单的「缺课」从此含翘课；正文不另列翘课节数。

| 候选 | 弃选原因 |
| --- | --- |
| 维持翘课不计缺课，改写萝莉 2 / 15 与 80 行「缺课」差分口上 | 翘课是「该在的课没去」；出勤率不算它，常翘课的孩子照评良好，「频繁翘课说明养育方式出了问题」这条反馈就断了 |
| 在效果 549 里记 | 缺课原本就挪进了状态机（721，Plan 24）；两边对称，效果串只管收益与心情 |
| 成绩单另列「其中翘课 N 节」 | 要多一个学期基线字段；缺课数已含翘课，萝莉 2 读累计翘课数就够 |

### 3.2 期末 9 / 10 的前提（M2，推荐口径 2）

- 两条事件的前提去掉 `&CVP_A1_Growth|6_L_70`：待努力（`7_E_2`）就是有课且出勤率 < 70，语义不变。
- `tools/official_event_check.py` 加一条：期末桶（`sub_key` 200）的前提不许用养成数值 4 / 5 / 6，报错写明「期末事件在学期基线重置之后推送，这几项读的是新学期；看刚结束的学期用编号 7 / 8」。
- 说明文档 §15 记一条同样的维护注意。

| 候选 | 弃选原因 |
| --- | --- |
| 把期末事件的推送挪到重置基线之前 | 要把学期结算拆成「出成绩单」与「重置基线」两步，逐孩比对学期号的幂等要重新论证；期末事件要看刚结束的学期，读成绩单就够 |
| 新增养成数值「上一份成绩单的出勤率」 | 同上；档位已经表达了出勤率 < 70 |

### 3.3 改岗理由按学期初的岗位分情形写（M3，推荐口径 3；附 Q1）

新增字段 `semester_base_work_type`（学期开始时的岗位，-1 为未知），`reset_semester_baseline` 写入。`get_report_incomplete_reason` 按「学期初 / 结算时」写：

| 学期初 | 结算时 | 理由 |
| --- | --- | --- |
| 学生岗 | 非学生岗 | 「X本学期改任了Y，改岗后不再上课，成绩单只计改岗前上过的课」；岗位为无时「X本学期不再担任学生，之后没有再上课，成绩单只计那之前上过的课」（同 Plan 29） |
| 非学生岗 | 非学生岗 | 本学期没有出勤与缺课记录：「X本学期担任Y，没有上课」；岗位为无时「X本学期不是学生，没有上课」。有记录（学期中途进过学生岗又改出去）按第一行写 |
| 非学生岗 | 学生岗 | 「X本学期中途回到了学生岗，成绩单只计回来之后上过的课」 |
| 学生岗 | 学生岗 | 无 |
| 未知（旧档的第一个学期） | 非学生岗 | 本学期有出勤或缺课记录的按第一行写，没有的按第二行写 |
| 未知 | 学生岗 | 无 |

只看这两个时刻：学期中途改出去又改回来，看不出来，不写理由。结算时不在学生岗的三行合起来就是一条规则：学期初是学生岗、或本学期有出勤 / 缺课记录，写第一行；否则写第二行（实施时由「未知」一行的推断法推广而来，免得「中途进过又出去」写成「没有上课」而正文却有出勤）。

**Q1（用户拍板，2026-09-13，按推荐并追加指令限制）**：
- 成年（少女期）、结算时不在学生岗、学期初也不在学生岗（或未知）、且本学期没有出勤与缺课记录的女儿，学期切换时只重置基线，不出成绩单、不置待查看、不进学期结束提示；她以前的成绩单照旧可在养成总览里翻。本学期有记录的（学期中途才离开学生岗）照出最后一份。幼女 / 萝莉整学期不在学生岗的，照 Plan 29 用户口径照出成绩单（写第二行的理由）。
- 「检查成绩单」（指令 1036）对成年后不在学生岗的女儿不成立。例外：她有一份还没看过的成绩单（学期中途才离开学生岗，那一学期照出）时仍成立，看完即不成立——否则养成总览的「成绩单待查看（用「检查成绩单」指令）」永远消不掉。
- 「检查成绩单」对不是女儿的学生岗角色不成立：1036 本就挂着 `TARGET_IS_PLAYER_DAUGHTER`，维持并补断言。
- 实现：新增前提 `target_report_card_checkable`（`semester_handle.judge_report_card_checkable`），挂在 1036 前提串末尾；学期结算与前提共用 `semester_handle.judge_adult_out_of_school`（成年且不在学生岗）。

| 候选 | 弃选原因 |
| --- | --- |
| 在改岗处记下改岗的日期 | 改岗入口有 8 处（基建面板、宿舍、外交、身体管理、调试……），逐处挂钩容易漏；学期初的岗位一处就能记 |
| 只按本学期有没有出勤记录推断 | 学期中途回到学生岗的情形推断不出来 |

### 3.4 同一节只落一种记录（L1，推荐口径 4）

- 这一节已记了缺课（体力或翘课），回来上课照给收益，不计出勤。
- 三个出勤写入点都先问一次：
  - `growth_handle.settle_student_class_gain`（`count_attend` 为真时）；
  - `growth_handle.settle_course_attend`（716 的体育 / 兴趣课）；
  - `sex_class_handle.settle_attend`（实操课开课与 722）。
- 判据抽成 `growth_handle.judge_absent_this_period(character_id, now_time)`：`last_absent_period == [日期序数, 节次]`。

| 候选 | 弃选原因 |
| --- | --- |
| 迟到算出勤，撤回这一节的缺课 | 要倒扣累计数，学期基线可能被扣穿；翘课的那一节也会被一起撤回 |
| 维持两边都记 | 一节算一次缺课一次出勤，出勤率被拉成对半 |

### 3.5 翘课被抓后当天不再翘（L2，推荐口径 5）

- 新增字段 `skip_caught_day`（被撞见那天的日期序数，0 为没有），623 写入。
- `roll_skip_class`：参照时刻的日期等于它就返回 False。只读 `child_growth`，不惰性创建。
- 当天剩余节次照常过体力闸；被抓那一刻正在进行的翘课行为照旧走完（设计写的是「当日剩余节次」）。次日自然失效，不需要跨天清零。

| 候选 | 弃选原因 |
| --- | --- |
| 被抓时立刻结束当前翘课行为、回去上课 | 设计只要求剩余节次；当场打断要处理移动与这一节的出勤，改动面大 |
| 把 `skip_class_flag` 改成三态 | 旧档里是布尔值，改整型要迁移，读的地方也多 |

### 3.6 「有课」「同班同学」只看学生岗的真课（L3）

- `schedule_handle` 新增 `judge_personal_course_real(character_id, course)`：活动条件相符且上课地点解析得出，不看此刻借不借得到书。`judge_personal_course_valid` 改为 real 加读书课借书。
- `growth_handle` 新增 `judge_selected_cell_real(character_id, week_day, period)`：学生岗，且个人课表这一格是每周课表上确有的课（教室课看每周课表那一格不空；个人式课看 `judge_personal_course_real`）。
- `handle_self_have_any_course`：有任一格 real 才成立。
- `get_classmate_list`：自己与对方都在同一格 real 才算同学。

| 候选 | 弃选原因 |
| --- | --- |
| 只加学生岗判断 | 每周课表清空后，个人课表全是「已停课」的孩子仍被判有课、有同学 |
| 改岗时清空个人课表 | Plan 24 §3.10 定了课表残留、不清理，改回学生岗后恢复 |

### 3.7 必修名单的顶替标记（L4）

`class_schedule_panel._select_must_attend` 的个人式课改用 `judge_personal_course_real`。

### 3.8 文档（L5 与各项说明）

- 说明文档：
  - §1：`class_ai` 一行补「翘课记缺课、被抓后当天不再翘」；`semester_handle` 一行补「成绩单不全的理由按学期初岗位写」
  - §2：字段表补 `skip_count`、`skip_caught_day`、`semester_base_work_type`；`absent_count` 改为「体力缺课与翘课」
  - §4：第 3 条补「同一节已缺课的回来上课不计出勤」；第 4 条补「翘掉的每一节记一节缺课、被抓后当天剩余节次不再翘」
  - §5：出勤一段补「同一节只落一种记录」
  - §6：改岗理由的表、Q1 的口径、期末事件的推送时机
  - §8：「有课」「同班同学」只看学生岗的真课
  - §12：养成数值 24
  - §14：三个新字段靠属性表回填
  - §15：第 4 条改写写入点；新增一条「期末事件的前提别用本学期数值（4 / 5 / 6）」
  - §16：测试计数
- 索引文档：计划表那一行改成「plan_25 ~ plan_30」，补第十一轮一句
- Plan 22 总纲：追加 §16，一行指向本 Plan

## 4. 接口设计（实施的权威定义）

### 4.1 常量与字段

`education_constant.py` 第 12 组末尾：

```python
GROWTH_VALUE_SKIP = 24
""" 养成数值编号：累计翘课节数（Plan 30）。翘掉的课同时记进累计缺课（编号 1）；要单看翘课的事件（如萝莉 2）读它 """
```

`game_type.CHILD_GROWTH`（放在 `last_attend_period` 之后）：

```python
self.skip_count: int = 0
""" 累计翘课节数（终身累计，只增不减，Plan 30）。翘掉的那一节同时记一节缺课（absent_count），同一节只记一次，与体力缺课共用 last_absent_period """
self.skip_caught_day: int = 0
""" 最近一次翘课被博士撞见那天的日期序数（date.toordinal()），0 为没有（Plan 30）。当天剩余节次不再掷翘课，次日自然失效 """
```

`game_type.CHILD_GROWTH`（放在 `semester_base_ability` 之后）：

```python
self.semester_base_work_type: int = -1
""" 本学期开始时的岗位（WorkType cid），-1 为未知：旧档、或还没在新学期立过基线（Plan 30）。成绩单按它与结算时的岗位写不全的理由 """
```

`absent_count` 的注释改为「累计缺课节数（体力不足的被动缺课与翘课，Plan 30 起翘课也记），计入学期成绩单」。

### 4.2 函数签名

| 模块 | 函数 | 变化 |
| --- | --- | --- |
| `class_ai` | `settle_absent(character_id, by_skip=False) -> bool` | 返回是否记上；`by_skip` 且记上时 `skip_count` +1（§3.1） |
| `class_ai` | `roll_skip_class` | 被抓当天返回 False（§3.5） |
| `StateMachine/default` | 714 `character_education_skip_class` | 派出翘课行为时调 `settle_absent(..., by_skip=True)`（§3.1） |
| `Second_effect` | 623 `handle_caught_skip_class` | 写 `skip_caught_day`（§3.5） |
| `growth_handle` | `judge_absent_this_period(character_id, now_time) -> bool` | 新增，只读（§3.4） |
| `growth_handle` | `settle_student_class_gain` / `settle_course_attend` | 本节已缺课不计出勤（§3.4） |
| `growth_handle` | `judge_selected_cell_real(character_id, week_day, period) -> bool` | 新增，只读（§3.6） |
| `growth_handle` | `get_growth_value` | 读编号 24（§3.1） |
| `sex_class_handle` | `settle_attend` | 本节已缺课不计出勤（§3.4） |
| `semester_handle` | `reset_semester_baseline` | 记 `semester_base_work_type`（§3.3） |
| `semester_handle` | `get_report_incomplete_reason` | 按学期初岗位分情形（§3.3） |
| `semester_handle` | `settle_semester_change` | Q1：成年且整学期不在学生岗的只重置基线（§3.3） |
| `semester_handle` | `judge_adult_out_of_school(character_id) -> bool` | 新增：成年且此刻不在学生岗（Q1 的学期结算与指令前提共用） |
| `semester_handle` | `judge_report_card_checkable(character_id) -> bool` | 新增：「检查成绩单」的对象判据，成年后不在学生岗且没有待查看成绩单的为 False（§3.3 Q1） |
| `handle_premise_other` | `handle_target_report_card_checkable` | 新增前提 `target_report_card_checkable`（§3.3 Q1） |
| `schedule_handle` | `judge_personal_course_real(character_id, course) -> bool` | 新增；`judge_personal_course_valid` 改用它（§3.6） |
| `growth_event_handle` | `get_classmate_list` | 双方都在同一格 real（§3.6） |
| `handle_premise_other` | `handle_self_have_any_course` | 改用 `judge_selected_cell_real`（§3.6） |
| `class_schedule_panel` | `_select_must_attend` | 改用 `judge_personal_course_real`（§3.7） |
| `tools/official_event_check` | `check_premise_text` 或 `check_row` | 期末桶禁用养成数值 4 / 5 / 6（§3.2） |

### 4.3 数据行

| 文件 | 行 | 改为 |
| --- | --- | --- |
| `data/official_event/期末.csv` | cid 9 | 前提 `CVP_A1_Growth\|7_E_2` |
| `data/official_event/期末.csv` | cid 10 | 前提 `CVP_A1_Growth\|7_E_2&CVP_A1_T\|103_E_1` |
| `data/official_event/萝莉.csv` | cid 2 | 前提 `CVP_A1_Growth\|24_GE_3` |
| `data/csv/InstructConfig.csv` | 1036 检查成绩单 | 前提 `TARGET_IS_PLAYER_DAUGHTER\|T_BABY_0\|TARGET_REPORT_CARD_CHECKABLE`（§3.3 Q1） |
| `tools/ArkEditor/csv/Premise.csv` | 新行 | `target_report_card_checkable,TARGET_REPORT_CARD_CHECKABLE,生育,交互对象可以检查成绩单（成年后不在学生岗的女儿不行，有待查看的成绩单除外）` |

`constant_promise.Premise` 在 `SELF_HAVE_ANY_COURSE` 之后加 `TARGET_REPORT_CARD_CHECKABLE = "target_report_card_checkable"`。不改口上与其它 CSV。

## 5. 行为对照

| 情形 | 现行为 | 改后 |
| --- | --- | --- |
| 心情闸掷中、翘了一节 | 缺课不变 | 缺课 +1、累计翘课 +1 |
| 同一天翘了之后的每一节（flag 保持） | 缺课不变 | 每节缺课 +1 |
| 同一节先体力缺课、休完又掷中翘课 | — | 只记一次缺课，翘课数不加 |
| 上 1 节、翘 2 节 | 出勤率 100%、良好 | 1/3、33%、待努力 |
| 萝莉 2「翘课的事被报了上来」 | 体力缺够 3 节就触发，翘课从不触发 | 翘够 3 节触发 |
| 期末：待努力的萝莉 | 候选 11 / 13 / 14 / 16 | 候选另有 9 / 10 |
| 成年女儿整学期在别的岗位 | 成绩单 0/0，理由「本学期改任了」 | 不出成绩单；「检查成绩单」对她不再可用（有待查看的那一份除外，看完即不可用） |
| 对不是女儿的学生岗角色用「检查成绩单」 | 不可用 | 不变（补断言） |
| 萝莉学期中途改岗 | 理由「本学期改任了Y」 | 不变 |
| 萝莉改岗后的下一学期 | 理由仍是「本学期改任了Y」 | 「本学期担任Y，没有上课」 |
| 学期中途回到学生岗 | 没有理由 | 「本学期中途回到了学生岗，成绩单只计回来之后上过的课」 |
| 开课时体力不足缺课，休完回来上课 | 缺课 +1、出勤 +1 | 缺课 +1，出勤不变，照给收益 |
| 翘课被抓 | flag 清掉，之后每节照常掷骰 | 当天剩余节次不再翘 |
| 改了岗的萝莉 | 判「有课」「有同学」，抽得到上课 / 同学事件 | 两者都不成立 |
| 每周课表清空后，个人课表全是已停课的孩子 | 判「有课」「有同学」 | 两者都不成立 |
| 书库此刻借空，指定必修学生 | 读书兴趣课那一格不标「*」 | 照标 |

## 6. 风险与注意事项

| 风险 | 说明 | 对策 |
| --- | --- | --- |
| 成绩单档位下移 | 常翘课的孩子出勤率与档位下降；「缺课太多」炫耀差分、萝莉 15、期末 10 等更容易触发 | 这是口径 1 的本意；说明文档 §4 / §6 与 `update.log` 写明 |
| 萝莉 2 触发条件变化 | 从「缺 3 节」变为「翘 3 节」，只因体力缺课的孩子不再抽到它 | 事件正文写的就是翘课 |
| 三个新字段 | 存档结构变化 | 属性表整体回填，旧档读入即补默认值；`test_save_compat` 断言 |
| 旧档第一个学期的改岗理由 | `semester_base_work_type` 为 -1 | 按有无出勤记录推断，见 §3.3 表 |
| Q1 让成年女儿不再出成绩单 | 学期结束提示与「成绩单待查看」随之消失 | 以前的成绩单保留；备选口径可维持 |
| 事件池变小 | 改岗萝莉与课表全停课的孩子不再抽到上课 / 同学事件 | 口径 1（Plan 24）的延伸 |
| 事件表是编译产物 | 改 CSV 后要重建 `Official_Event.json` | 测试引导的增量构建会重建；`official_event_check.py` 通过 |
| 构建会写乱 PO | 同前几轮 | 收尾 `git checkout -- data/po/` |

## 7. 不在本方案范围

- **成绩单另列翘课节数**：§3.1 弃选；要做时加 `semester_base_skip` 与快照键
- **体育课游泳不换泳衣**：Plan 29 §7
- **读书系统**：511 里难度 0 的书读完时 `add_value` 未赋值、读完的书留在手上、娱乐读书借不到书每分钟重试
- **身体管理的练习类把岗位改成性爱练习生，没有看年龄**：属身体管理系统，本轮未深查
- **成长停滞解除后一次长大，「本阶段第几天」偏大**：Plan 29 §2.5-5
- `handle_premise_work.py:343` 保育员前提写死的 153：属妊娠系统
- Plan 22 总纲 §10.2 的五条备忘（含实习导师只按岗位认人）；Plan 26~29 §7 的其余范围外事项
- Plan 24~29 留给用户的游戏内测试项

## 8. 追加调整

（实施后每轮追加一节，只写设计；实施记录见实施文档 §6.5。暂无）
