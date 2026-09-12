# Plan 25（方案）：生长养成系统第六轮复查

> 本 Plan 拆分为两个文件：**本文件为纯方案**（发现、现状调查、设计决策、接口设计、风险、范围外）；
> 逐文件改动步骤、构建、验证清单、回滚与实施过程记录见 `plan_25_生长养成系统第六轮复查_实施步骤与记录.md`（下文简称"实施文档"）。
>
> 本 Plan 是 Plan 22（生长养成系统，`plan/done/`）与 Plan 24（师生并入工作链，`plan/done/`）之后的又一轮全面复查。
> 实施完成后在 Plan 22 总纲追加 §11，只写一行指向本 Plan。

- 状态：**已实施**（方案定稿与实施均为 2026-09-12；全套回归 15 个文件 903 条断言通过，游戏内整体测试待用户执行；实施中的偏离已回写 §3.1、§4.2，见实施文档 §6.1）
- 来源：用户需求 → "该系统已经实现完成了，进行一次检查，检查该系统是否有哪里仍有遗漏的未实现内容、BUG、死代码、待处理项等。依然仅由主代理调查和进行，不使用子代理进行"
- 已确认的设计决策（2026-09-12 用户拍板，四项均选推荐）：
  1. **口径 62 提前退场**：实装打断，不放弃口径（§3.1）
  2. **开课后才到场的学生**：到场自动加入课堂 H，不再坐在旁边自习（§3.2）
  3. **玩家「授课」指令 2010**：全面对齐——按玩家所在教室判前提、三类教室都能用、拉人口径与教师 303 一致、只有排了课的节次才计出勤（§3.4）
  4. **学生课间迟到**：并入同一条打断规则，节次内也允许「马上开课」状态，与教师同口径（§3.1）
  5. **必修名单加入成年学生岗**（用户追加）：候选名单由「女儿 ∩ 学生岗」改为全部学生岗，实行值守卫保留（§3.7）。Plan 24 定下的「必修名单在女儿名单上再过滤学生岗」随之作废
- 预计改动量：**约 20 个文件**，净增约 350 行、删除约 60 行
  - 数据 3 个：`target.csv` 新增 1 行、`InstructConfig.csv` 改 1 行、ArkEditor `Premise.csv` 增 2 行、删 1 行、改 1 行
  - 常量 3 个：`education_constant`、`constant_promise`、`constant/StateMachine.py`
  - 逻辑约 10 个；测试 5 个；文档 3 个
- 风险等级：**中低**（打断规则作用在行为循环里，写错会让 NPC 来回抖动；其余都是局部修补。行为循环收敛由现有测试加新断言兜底）
- 适用代码快照：`master @ 6fa04f1fb`（Plan 24 提交之后）
- 前置：Plan 22 一~四期、09-12 第五轮复查、Plan 24 均已完成

---

## 1. 目标

1. 口径 61 / 62 真正生效：上一节在上课、或正在娱乐的学生，在实操课开始前能提前动身，开课时人已在教室
2. 开课之后才到的选修 / 必修生，走进教室就加入课堂 H，与开课时拉进来的人待遇相同
3. 学生在没课的节次里做娱乐，下一节有课时也能提前收手去上课（与教师「20 分钟内有下一节先去教室」同口径）
4. 被判「可用」的教师一定会来授课：`judge_teacher_available` 与教师授课行的 normal 前提完全对齐
5. 教师拉学生进课堂时，遵守与学生自己决策相同的体力闸、心情闸与口径 1（只拉学生岗）
6. 玩家「授课」指令在玩家所在的三类教室里都能用；拉人口径安全；节次外手动授课不再记出勤
7. 必修名单能点名成年学生岗
8. 清掉过期文案、双重翻译与写死的编号

**验收标准**：
- 全套回归测试通过，新增断言覆盖 §3 每一条
- 行为循环测试：实操课开始那一刻，上一节有课的选修生已经在教室；六轮都收敛
- 全仓库（`plan/` 除外）grep 不到「学生岗 ∪ 女儿」这类过期口径，也 grep 不到 `teacher_teaching_in_classroom`

## 2. 现状调查

本轮读过的范围：`Education_System/` 全部 16 个模块；`handle_npc_ai.find_character_target`、`judge_interrupt_character_behavior`；
Plan 24 的 18 个前提与 16 行 target；状态机 303 / 304 / 561 / 562 / 713~721；结算 512 / 548 / 549 / 550 / 552 / 553 / 554 / 557、10014 / 10015；二段 622 / 623；
`handle_ability` 的炫耀记录、`past_day_settle`、`pregnancy_handle` 的成年结算、`character_info_head`、`handle_instruct` 的授课与开课；说明文档 `生长养成系统.md`。

### 2.1 发现（中）

| # | 发现 | 证据 |
| --- | --- | --- |
| M1 | **口径 61 / 62「开课前 10 分钟到岗 / 提前退场」实际不生效** | 见 §2.3 |
| M2 | **开课后才到的学生不加入课堂**：玩家在 H 中时 `judge_teacher_available(0)` 为假，这些学生走 220820 → 713，在课堂 H 旁边自习，还按 548 记一节出勤 | `class_ai.py:86~90 judge_teacher_available`、`Settle/default.py:7684 handle_self_study_add_just` |
| M3 | **醉酒的教师被判「可用」**：教师的授课行（220700）要 `normal_all_except_special_hypnosis`，醉酒（normal_5 / normal_6）时她不会去讲课；但 `judge_teacher_available` 只同步了 normal_2 / 3 / 7 与睡着，学生会空坐一整节、零收益。与第五轮 #3 属同一类问题 | `class_ai.py:67~107`、`handle_premise/__init__.py:1126 handle_normal_5`、`:1151 handle_normal_6`、`:1628 handle_normal_all_except_special_hypnosis` |
| M4 | **玩家「授课」指令 2010 的遗留问题**（Plan 24 §7 列为范围外），见 §2.4 | `InstructConfig.csv:70`、`handle_instruct.py:549 handle_teach`、`Settle/default.py:7575 handle_teach_add_just` |
| M5 | **303 拉学生时绕过两道闸**：只看 H、睡着、翘课 flag、休息，不按 `get_course_stage` 判。开课前已在教室里等候（720）的学生，本节本该体力缺课或掷中翘课，但只要教师先被处理，就会被拉进听课，结果取决于 NPC 的处理顺序。另外会拉进课表还有残留、但已经改岗的人（违反 Plan 24 口径 1） | `StateMachine/default.py:2698~2722 character_work_teach` |

### 2.2 发现（低）

| # | 发现 | 证据 |
| --- | --- | --- |
| L1 | 学生在没课的节次做娱乐（10~120 分钟：唱歌 10、下棋 30、过家家 / 自由玩耍 60、看电影 120），下一节有课时不会提前收手，常迟到。教师有 `get_upcoming_teaching`（节次内也看下一节），学生的 `get_upcoming_course` 在节次内直接返回 None | `schedule_handle.py:392`、`Behavior_Data.csv` 的 duration 列 |
| L2 | 561 对任何人都先查 `get_next_sex_class`。被任命为教师的成年女儿（口径 39），个人课表若有残留，实操课前 10 分钟会被送去实操教室，与 210700 来回拉扯。561 的学生分支在 Plan 24 后只剩娱乐 155 的自动 AI 会走到，注释已过期 | `StateMachine/default.py:433~479 character_move_to_class_room` |
| L3 | 过期口径「学生岗 ∪ 女儿」：`course_select_panel.py:4` 与 `:108`、`student_select.py:5`、`生长养成系统.md:226`、`通用NPC选择面板.md:23`、`test_panels.py:116`（断言标签）。另外说明文档 §12 的状态机行缺 721 | — |
| L4 | 已经翻译过的常量又包了一层 `_()`，共 8 处（第五轮只修了两处）：`class_schedule_panel.py:313 / 423 / 609`、`course_select_panel.py:149 / 372`、`growth_panel.py:249`、`semester_handle.py:43 / 402` | — |
| L5 | 写死编号，违反「从常量 / 配置取」的约定：`handle_premise_entertainment.py:405`（`== 151`）、`growth_handle.py:492`（`range(40, 50)`）、`auto_schedule.py:52`（`>= 70`）、`handle_premise_work.py:287 / 313`（`== 151 / 152`）、`handle_premise_place.py:819 / 843` | — |

### 2.3 M1 的机理

1. NPC 只在行为为「发呆」时做决策（`character_behavior.py:165~167`）；行为进行中的唯一插手点是 `handle_npc_ai.py:661 judge_interrupt_character_behavior`，而它只处理三种情形：休息中体力回满、睡觉中自然醒、工作 / 娱乐中到了淋浴时间
2. 听课、自习、个人式课的时长都截到本节结束（`schedule_handle.py:335 get_period_left_minute`，第五轮），所以上一节有课的学生，恰好在实操课开始那一刻才空闲
3. `class_ai.py:195 get_next_sex_class` 只看「还没开始」的节次（`start_time <= now_time` 跳过），开课那一刻她已经不是 SEX_PENDING，只能按本节的课走 ATTEND → 715，开课之后才动身
4. 在做娱乐的学生同理：娱乐不会被打断
5. 于是第二次提醒写的「选修的学生们已经在往教室走了」（`sex_class_handle.py:561`）与说明文档 §4-1 的「中止当前节次去教室」都与实际不符
6. 测试 `test_class_ai.py:612` 派发的是一个已经空闲的学生，所以没测出来

### 2.4 M4 的三个问题

1. **前提**：`handle_premise_place.py:831 handle_student_not_study_in_classroom` 遍历全岛，只要任何一间理论教室里有一个没在听课的 152，就返回 1，并不看玩家自己所在的教室。
   `in_class_room`（`:3658`）只认 `Class_Room`，所以玩家只能在理论教室授课。`handle_teach_add_just` 的「按所在教室的场景标签判课型」分支（`Settle/default.py:7604~7609`）因此对玩家永远只会得到理论课
2. **拉人**：`handle_instruct.py:565~575` 把场景里所有学生岗改成听课，不看 H、睡着、翘课、休息，也不对齐开始时刻；303 则会把 `start_time` 对齐到教师
3. **计出勤**：512 对玩家也按 `settle_student_class_gain` 的默认 `count_attend=True` 结算，节次外手动授课照样给学生记一节出勤，与第五轮「只有课表排了课的节次计出勤」冲突
4. 附带：`teacher_teaching_in_classroom`（`:806`）已注册，但所有 CSV 都不引用，而且写死了 151 与 `Class_Room`，属于死前提

### 2.5 可复用的既有实现

| 需求 | 现成实现 |
| --- | --- |
| 强制结束当前行为 | `character_behavior.judge_character_status_time_over(character_id, now_time, end_now=2)`（`:272`），淋浴打断即是先例（`handle_npc_ai.py:727~737`） |
| 防循环不收敛 | `judge_interrupt_character_behavior` 开头的「本轮刚赋予的行为不打断」守卫（`:672~675`） |
| 把学生拉进课堂 H | `Settle/default.py:3108~3115 handle_sex_class_mode_on` 的循环体：取消移动计划、`is_h`、`see_pl_h`、到场二段 `JOIN_SEX_CLASS`；出勤走 `sex_class_handle.settle_attend` |
| 实操课是否可参加 | `sex_class_handle.judge_can_join_sex_class(character_id, check_course)`，必修生豁免前置修习 |
| 正在进行的实操课 | `sex_class_handle.get_running_class()`，教室名在 `["classroom"]` |
| 三类教室的场景标签 | `education_constant.CLASSROOM_TAG_BY_COURSE_TYPE`（Class_Room / Practice_Room / Auditorium） |
| 状态函数 + 薄前提的范式 | Plan 24：`class_ai.get_course_stage` + `handle_premise_work.py:356~662` |

### 2.6 已知陷阱与硬约束

1. **前提必须是纯函数**（Plan 24 §2.6-1）：新状态、新前提都不能写数据，也不能惰性创建养成数据
2. **打断会不会抖动**：打断之后，AI 必须真的派出上课行，否则会回头选同一个娱乐，下一轮再被打断。所以打断条件要包含「上课行的 normal 门槛成立」和「上课地点能解析」，而且「本轮刚赋予的行为不打断」
3. **NPC 的结算发生在行为开始时**：被打断的那一节课，收益已经按整节结算过了，打断不会回退收益，也不会少记出勤；提前退场不记缺课（口径 66），所以打断路径上绝不能调 `settle_absent`
4. **时刻取值**：打断判定发生在行为进行中，此时 `behavior.start_time` 是这个行为的开始时刻，不是「现在」。`get_next_sex_class` 已经接受显式的 `now_time`；`get_upcoming_course` / `roll_skip_class` / `judge_must_attend_sex_class` 目前只读 `behavior.start_time`，要加一个可选的 `now_time` 参数
5. **测试构建会写乱 PO**：测试引导会跑 `auto_build_config`，本机没有 gettext，收尾必须 `git checkout -- data/po/`
6. **编号**：状态机最大为 721，下一个已占用的是 751，722 空闲；target 组 08 已用到 220830，220835 空闲

## 3. 设计决策

### 3.1 一条打断规则（M1 + L1）

在 `judge_interrupt_character_behavior` 的新鲜度守卫之后、休息 / 睡觉 / 工作娱乐三段之前，加一段——**把当前行为截到应离开的时刻**，而不是「现在就结束」：

```python
    leave_time = class_ai.get_student_leave_time(character_id)
    if leave_time is not None:
        character_data.behavior.duration = max(1, int((leave_time - character_data.behavior.start_time).total_seconds() // 60))
        return 1
```

> **实施时的改写**（实施文档 §6.1 偏离 1）：初稿是「以 `cache.game_time` 为现在，成立就 `end_now=2` 立即结束」。
> 行为循环测试里 4 名必修生一个都没提前到——行为循环中 `cache.game_time` 是玩家这一步的**结束时刻**，NPC 按各自的行为时刻追赶；
> 玩家一步走 45 分钟时，「现在」早已越过开课时刻，`get_next_sex_class` 只看还没开始的节次，判据整个落空（既有的淋浴打断有同样的盲区）。
> 改为按 NPC 自己的行为时间轴算出「应离开的时刻」并截短时长：循环推进到那一刻行为自然结束，NPC 在那一刻重新决策。
> 截出来的结束时刻严格晚于开始，新行为开始于离开时刻，不会被再截，循环必然收敛。

`class_ai.get_student_leave_time` 的判据（按行为自己的时间轴，不看「现在」）：

| 前置条件（全部满足才继续） | 理由 |
| --- | --- |
| 学生岗；不在 H、不在睡觉；当前行为不是 MOVE / 发呆 | 只管学生；H 与睡觉各有自己的链 |
| `handle_normal_all` 成立 | 这是上课行的门槛：不成立时打断了 AI 也不会派上课行，会抖动 |
| 当前行为可截：行为 tag 含「工作」或「娱乐」（见学、自由玩耍的 tag 都是「娱乐」）。等待（WAIT，tag「日常」）不截——它用处很杂，而学生等开课时本就已在教室（实施文档 §6.1 偏离 2） | 需求类（吃饭、如厕、休息、淋浴）不截，否则人会饿着去上课 |

对行为开始之后、结束之前开始的每一节，按先后找第一个落在行为之内的离开时刻：

| 触发 A：待赴实操课 | 触发 B：马上开课 |
| --- | --- |
| 这一节是自己要上的实操课（必修或选修，`judge_sex_class_is_mine`），人不在那间教室 → 离开时刻 = 开课前 `PRE_ARRIVE_MINUTE` | 这一节排了课、今天没挂翘课 flag，开课前 `UPCOMING_MINUTE`（20 分钟）那一刻本节没课，上课地点能解析且人不在那里 → 离开时刻 = 开课前 20 分钟 |
| 上课中、娱乐中、见学中都截（提前退场） | 离开的那一刻本节还有课的不截：那节课由截到节末的时长自然结束 |

行为开始时已经进了窗口（比如当时 AI 因为需求没派上课行）的，离开时刻取开课那一刻，至少别拖过开课。

弃选方案：

| 候选 | 弃选原因 |
| --- | --- |
| 在「现在」立即结束当前行为（本方案初稿） | 行为循环里「现在」是玩家这一步的结束时刻，一步跨过开课时刻就整个错过，实测 0/4 提前到场 |
| 在各个上课状态机里预先把时长截到下一节实操课前 | 只管上课中的学生，娱乐中的照样迟到；而且每个上课状态机都要去查下一节，逻辑分散 |
| 放弃口径 62，改文案 | 用户已选实装打断 |
| 触发 B 也用 10 分钟窗口 | 教师用 20 分钟，同一套课表两套窗口会让「谁先到教室」不可预期；统一成 `UPCOMING_MINUTE` |

配套：`schedule_handle.get_upcoming_course` 放开到节次内（去掉 `get_class_period != -1 → None` 的门槛），窗口改用常量。
这样 `get_course_stage` 在课间也会给出 UPCOMING，工作链的 210810 / 220830 就会接手，见学判定也会让路（Plan 24 §3.9）。

### 3.2 开课后到场的自动入课（M2）

在 `get_course_stage` 里加一个状态 `COURSE_STAGE_JOIN_SEX_CLASS`，而不是另写一个独立前提：
新增的行必须与 220815 / 220820（听课 / 自习）互斥，否则会按权重随机二选一。沿用 Plan 24 §3.3「一个状态函数 + 薄前提」的范式，互斥由状态函数保证。

- **判定位置**：`get_course_stage` 本来要返回 ATTEND 的地方（两道闸之后；必修生不过闸），再判一次：
  `sex_class_mode` 为真，正在进行的实操课就在她这节课的教室里，人已在该教室，不在 H，且 `judge_can_join_sex_class` 成立（必修生豁免前置修习）→ 返回 JOIN_SEX_CLASS
- **不在教室时仍是 ATTEND**：走 715 过去，到了再判一次就成了 JOIN
- **新行** `220835,722,normal_all_except_special_hypnosis|work_is_student|self_course_join_sex_class,22,…`
- **新状态机 722** `EDUCATION_JOIN_SEX_CLASS`：调用 `sex_class_handle.pull_student_into_class(student_id)`（从 10014 的循环体抽出来，两处共用：取消移动计划、`is_h`、`see_pl_h`、到场二段口上），然后 `settle_attend`
  - 开课时拉进来的人，出勤已由 `start_sex_class` 记过，所以 10014 那一侧**不**调 `settle_attend`
  - `pull_student_into_class` 本身不记出勤，由调用方决定
- 体力不足的必修生照样加入，进了模板面板只能旁观（口径 65，`group_sex_panel.py:630` 已处理）

### 3.3 教师可用性对齐授课行（M3）

`judge_teacher_available` 在 normal_2 / normal_3 那条之后加一条：

```python
    # 授课行挂的是 normal_all_except_special_hypnosis：意识模糊 / 不清（醉酒、半梦半醒、深睡等）时她不会来讲课，
    #    空气 / 体控催眠除外（Plan 25 §3.3）
    if (not handle_premise.handle_normal_5(teacher_id) or not handle_premise.handle_normal_6(teacher_id)) and not (
        handle_premise.handle_unconscious_flag_5(teacher_id) or handle_premise.handle_unconscious_flag_6(teacher_id)
    ):
        return False
```

仍不同步 normal_1（需求）与 normal_4（服装）：理由同 Plan 24 §3.4，这两种状态一节之内会自行解除；教师回来开讲时，303 会把在座的学生拉进来，512 负责结算。

### 3.4 玩家「授课」指令全面对齐（M4）

| 点 | 改为 |
| --- | --- |
| 可用地点 | 新前提 `in_education_classroom`：所在场景带三类教室标签之一（从 `CLASSROOM_TAG_BY_COURSE_TYPE` 取）。2010 的 `IN_CLASS_ROOM` 换成它 |
| 有没有可教的学生 | `student_not_study_in_classroom` 改写为按玩家**所在场景**判：场景里至少有一人满足 `class_ai.judge_student_pullable`，且没在听课（已在听别的教师的课的人不抢）。id 不变，ArkEditor 描述同步改 |
| 拉谁 | `handle_teach` 只拉满足 `judge_student_pullable` 且没在听课的人；开始时刻对齐到玩家（`start_time = cache.game_time`），时长 45 |
| 计出勤 | 512 对玩家：只有该生本节课表排的就是这间教室（`get_now_course` 的 classroom 等于所在场景名）才 `count_attend=True`，其余只给收益不计出勤 |
| 死前提 | 删 `teacher_teaching_in_classroom`（常量、实现、ArkEditor 行）。删前全仓库 grep 一遍确认没有引用 |

`judge_student_pullable(student_id)` 是 M4 与 M5 共用的底层判据：学生岗、不在 H、不在睡觉、没挂今日翘课 flag、当前行为不是休息。
玩家授课**不**套课表与两道闸：口径 37 的手动授课本来就是「对在场孩子」，不看她这节排了什么；体力不足的人正在休息，已经被「休息」这一条挡住。

### 3.5 303 拉人过闸（M5）

新增 `class_ai.judge_student_join_class(student_id, classroom, now_time) -> bool`：

1. 满足 `judge_student_pullable`
2. 在 `now_time` 这一节的课表指向 `classroom`（`schedule_handle.get_course_at(student_id, now_time, period)`；已含必修覆盖）
3. 必修生（`judge_must_attend_sex_class(student_id, now_time)`）直接成立；否则过体力闸（`hit_point / hit_point_max >= ABSENT_HP_RATE`），再过心情闸（`roll_skip_class(student_id, now_time)` 为假）

为此：`roll_skip_class`、`judge_must_attend_sex_class` 各加可选参数 `now_time=None`，缺省时仍取 `behavior.start_time`。
掷骰种子不变（角色 + 日期 + 节次），所以 303 替学生判的结果，与学生自己决策时的结果一定相同。
303 的拉人循环改为调用它（教室取 `scene_data.scene_name`，时刻取教师的 `behavior.start_time`）。

弃选「303 不再拉人，全靠 557 晚到补结算」：功能上 557 已经能保证收益，但拉人会顺带对齐时刻、压掉每个学生各自一条听课口上。去掉拉人会让同屏刷出一串听课口上，是玩家可见的体验变化，不在本轮做。

### 3.6 561 预到岗只认学生岗（L2）

`character_move_to_class_room` 的第一段改用 `class_ai.get_pending_sex_classroom(character_id)`（Plan 24 新增，只认学生岗）。注释改为说明当前三个调用方：教师 210700 / 210705、学生 210800、娱乐 155 的自动 AI。

### 3.7 必修名单加入成年学生岗（M6，用户追加）

| 点 | 改为 |
| --- | --- |
| 候选名单 | `class_schedule_panel._select_must_attend` 由 `growth_handle.get_student_candidate_list()` + 学生岗过滤，改为 `growth_handle.get_course_candidate_list()`，即全部学生岗，与个人课表同口径 |
| 状态守卫 | 保留 `judge_can_join_sex_class(check_course=False)`：成年学生仍须满足 H 模式实行值（口径 63 第二层），否则必修名单就成了绕开全部 H 前提的旁路。面板显示时判一次，开课时 `get_scene_student_list` 与 §3.2 的 JOIN 判定各再判一次 |
| 下游 | 必修覆盖（`get_course_at`）、豁免心情闸（`judge_must_attend_sex_class`）、出勤（`settle_attend` 已认学生岗）都不看是不是女儿，无需改动 |
| 已知表现 | 成年学生面板上列出时满足实行值，到开课那一刻不再满足（好感下降等）的，会到场但进不了课堂，在 §3.2 的判定下落回 ATTEND → 自习。这是实行值守卫的本意，写进说明文档 |

### 3.8 清理（L3~L5）

- **过期文案**：改 6 处「学生岗 ∪ 女儿」；说明文档 §12 的状态机行补 721 / 722，§4-1 改写提前退场的实现方式，§10「谁能来」与 §15-5 改为必修名单是全部学生岗
- **双重翻译**：8 处去掉外层的 `_()`。`SEMESTER_NAME.get(month, "学期")` 的兜底值改为 `_("学期")`；`REPORT_GRADE_NAME.get(…, "无课可评")` 的兜底改为 `_("无课可评")`
- **写死编号**：
  - `== 151`（过家家）→ `education_constant.ENTERTAINMENT_PLAY_HOUSE`
  - `range(40, 50)` → 从 `SUBJECT_ABILITY_LIST` 里筛 `ability_type == ABILITY_TYPE_SUBJECT`
  - `>= 70` → `in SEX_SKILL_SUBJECT_SET`
  - 前提里的 `== 151 / 152` → `TEACHER_WORK_TYPE` / `STUDENT_WORK_TYPE`，在函数内延迟 import（与 `handle_premise_time.py:423` 同款）

## 4. 接口设计（实施的权威定义）

### 4.1 常量

`education_constant.py`：

```python
UPCOMING_MINUTE = 20
""" 「马上开课」的提前量（分钟）：教师与学生都在下一节开始前这么多分钟内先去上课地点。
    get_upcoming_teaching / get_upcoming_course 的默认窗口与学生打断规则共用它（Plan 25 §3.1） """
COURSE_STAGE_JOIN_SEX_CLASS = 6
""" 本节的课所在教室正在上性技实操课、人已在教室、可以参加但还没进 H：走进来就加入课堂（Plan 25 §3.2） """
```

`constant/StateMachine.py`：`EDUCATION_JOIN_SEX_CLASS = 722`，注释「上课：走进正在上性技实操课的教室，加入课堂 H 并记出勤」。

`constant_promise.py`：
- 新增 `SELF_COURSE_JOIN_SEX_CLASS = "self_course_join_sex_class"`（工作_条件）与 `IN_EDUCATION_CLASSROOM = "in_education_classroom"`（地点_工作）
- 删除 `TEACHER_TEACHING_IN_CLASSROOM`

### 4.2 函数签名

| 模块 | 函数 | 变化 |
| --- | --- | --- |
| `class_ai` | `get_student_leave_time(character_id) -> Optional[datetime]` | 新增（§3.1；实施时取代了初稿的 `judge_student_should_leave_now`） |
| `class_ai` | `judge_sex_class_is_mine(character_id, temp_class, week_day, period) -> bool` | 新增，从 `get_next_sex_class` 抽出，截短规则共用 |
| `class_ai` | `get_attend_or_join_stage(character_id, now_course) -> int` | 新增，`get_course_stage` 本该返回 ATTEND 的两处改走它（§3.2） |
| `class_ai` | `judge_student_pullable(student_id) -> bool` | 新增（§3.4） |
| `class_ai` | `judge_student_join_class(student_id, classroom, now_time) -> bool` | 新增（§3.5） |
| `class_ai` | `roll_skip_class(character_id, now_time=None)` | 加可选参数 |
| `class_ai` | `judge_must_attend_sex_class(character_id, now_time=None)` | 加可选参数 |
| `class_ai` | `get_course_stage` | 在返回 ATTEND 之前判 JOIN_SEX_CLASS |
| `class_ai` | `judge_teacher_available` | 加 normal_5 / 6 一条 |
| `schedule_handle` | `get_upcoming_course(character_id, minute_limit=UPCOMING_MINUTE, now_time=None)` | 节次内也看下一节；可指定时刻 |
| `schedule_handle` | `get_upcoming_teaching(character_id, minute_limit=UPCOMING_MINUTE)` | 默认值改用常量 |
| `sex_class_handle` | `pull_student_into_class(student_id) -> None` | 新增，从 10014 抽出 |

### 4.3 数据行

```csv
220835,722,normal_all_except_special_hypnosis|work_is_student|self_course_join_sex_class,22,正常状态下或被空气或体控催眠中，工作为学生，本节的课所在教室正在上性技实操课且自己可以参加，则加入课堂
```

`InstructConfig.csv:70`（2010）的前提列：`STUDENT_NOT_STUDY_IN_CLASSROOM|IN_EDUCATION_CLASSROOM|TARGET_HP_NE_1|NO_TARGET_OR_TARGET_CAN_COOPERATE`。

## 5. 行为对照

| 情形 | 现行为 | 改后 |
| --- | --- | --- |
| 上一节在听课，下一节是自己的实操课 | 开课那一刻才动身 | 开课前 10 分钟被打断，去实操教室，到了原地等（220800） |
| 在娱乐中，10 分钟后有自己的实操课 | 娱乐做完才走，常晚到 | 同上 |
| 没课的节次在娱乐，下一节 20 分钟内有课 | 娱乐做完才走 | 被打断 → UPCOMING → 715 过去 → 720 原地等 |
| 同上，但今天已翘课 | — | 不打断 |
| 开课后才走进实操教室的选修 / 必修生 | 713 自习，记一节出勤 | 722 加入课堂 H，记一节出勤 |
| 教师醉酒，本节有课 | 学生 304 空坐整节 | 学生 713 自习 |
| 在教室里等候、本节该体力缺课的学生，教师先开讲 | 被拉进听课 | 不拉，她自己决策时走 721 |
| 课表有残留、已改岗的人恰在教室 | 被拉进听课 | 不拉 |
| 玩家在实践教室 / 大礼堂用「授课」 | 指令不可用 | 可用，课型按教室判定 |
| 玩家所在教室没有学生，别的理论教室里有 | 指令可用（空讲） | 不可用 |
| 玩家午休时对学生手动授课 | 给收益并记出勤 | 只给收益，不记出勤 |
| 玩家授课时场景里有学生正在睡觉 / 在 H 中 | 被改成听课 | 不拉 |
| 被任命为教师、课表有残留的成年女儿，实操课前 10 分钟 | 被 561 送去实操教室 | 照常去自己授课的教室 |
| 排实操课点必修 | 只列女儿（学生岗） | 列全部学生岗，含成年；成年学生须满足实行值 |

## 6. 风险与注意事项

| 风险 | 说明 | 对策 |
| --- | --- | --- |
| 打断规则让 NPC 来回抖动 | 打断后 AI 若派不出上课行，会回头选同一个娱乐，下一轮再被打断 | 前置条件带上 `normal_all`、地点可解析、没挂翘课 flag；「本轮刚赋予的行为不打断」；行为循环测试断言收敛，另写一例「跟随中的学生不被打断」 |
| 打断需求类行为 | 人饿着、憋着去上课 | 只打断 tag 含工作 / 娱乐的行为与 WAIT / 见学 / 自由玩耍 |
| 课间多等 20 分钟 | 学生在没课的节次，最后 20 分钟改去教室等 | 与教师同口径，是有意的取舍；说明文档写明 |
| 打断不回退收益 | 被打断的那节课，收益与出勤在开始时已按整节结算 | 符合口径 66「提前退场的那一节不算缺课」；写进说明文档 |
| 在前提里调用 `judge_can_join_sex_class` | 它对成年学生会调 `calculation_instuct_judege(not_draw_flag=True)`，开销较大 | 只在 `sex_class_mode` 为真、且人已在那间教室时才判，平时直接短路 |
| 2010 前提语义变化 | ArkEditor 里 `student_not_study_in_classroom` 的描述要同步 | 一并改 |
| 删除 `teacher_teaching_in_classroom` | mod 或口上可能引用 | 删前 grep 全仓库，含 `mod/`、`data/`；实施记录登记结果 |
| 成年学生点名必修后到场却进不了课堂 | 实行值是动态的 | 口径 63 的本意；面板与说明文档写明 |

## 7. 不在本方案范围

- Plan 22 总纲 §10.2 的五条备忘：日程改完次日才生效、未来日期的临时课在格子上看不见、成年学生静默翘课、夜间撞见翘课也触发、实习导师不判当班
- 303 取消拉人、完全交给 557（§3.5 的弃选方案）
- 玩家授课套课表与两道闸（§3.4：手动授课本来就是「对在场孩子」）
- Plan 24 §4.3 的七项游戏内测试；PO / MO 重建（本机无 gettext）

## 8. 追加调整

（实施后每轮追加一节，只写设计；实施记录见实施文档 §6.5。暂无）
