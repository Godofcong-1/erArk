# Plan 24（方案）：教师与学生并入 NPC 工作链

> 本 Plan 拆分为两个文件：**本文件为纯方案**（需求、现状调查、设计决策、接口与数据设计、行为对照、风险、范围外）；
> 具体的逐文件改动步骤、构建、验证清单、回滚与实施过程记录见
> `plan_24_师生并入工作链_实施步骤与记录.md`（下文简称"实施文档"）。
>
> 本 Plan 是 Plan 22（生长养成系统，已归档于 `plan/done/`）AI 链部分的结构性重构：课表、结算、口上、面板的玩法口径不变，
> 只把教师 / 学生的行为从 `find_character_target` 里的特例搬回通用工作链。
> Plan 22 的方案与实施记录不再更新这部分内容，只在总纲状态行留一行指向本 Plan。

- 状态：**已实施**（方案定稿与实施均为 2026-09-12；全套回归 15 个文件 843 条断言通过，游戏内整体测试待用户执行；实施中的两处设计偏离已回写 §3.9、§4.2，见实施文档 §6.1）
- 来源：用户需求 → "深入了解当前 `Script\Design\handle_npc_ai.py` 里 `find_character_target` 的工作链的相关机制，包括配套的
  `data\target\default\target.csv` 和 `data\csv\WorkType.csv`。了解完毕之后，检查生长养成系统中老师和学生的工作能否改为融入目前的工作链，
  而不是像现在一样作为单独的特例进行处理"
- 已确认的设计决策（2026-09-12 用户拍板）：
  1. **课表只对学生岗（WorkType 152）生效**。学生上课写成 `target.csv` 的 21/22 类行（带 `work_is_student`），真正并入工作链；
     选课面板与必修名单只列学生岗，被改了岗的女儿按新岗位上班、不再上课。
     弃选：「独立的数据驱动课程链（新增目标类型，对所有人检索）」「本次只并教师」
  2. **教师与其他岗位一样受 normal 前提约束**。移动行 `normal_all`、授课行 `normal_all_except_special_hypnosis`；
     助理 / 跟随 / 体检中 / 临盆 / 产后的教师不授课，`judge_teacher_available` 同步判为不可用，学生直接降级自习。
     弃选：「助理教师照常授课（`normal_124567` + `not_follow`）」
- 预计改动量：**约 23 个文件**，净增约 400 行、删除约 150 行
  - 数据 3 个：`target.csv` 新增 16 行、`WorkType.csv` 改 2 行、ArkEditor `Premise.csv` 新增 18 行
  - 常量 2 个、逻辑 9 个（前提实现约 250 行是主体；`class_ai` 删 4 个函数、增 4 个）
  - 测试 5 个、文档与日志 4 个
- 风险等级：**中**（改的是 NPC AI 主决策链的工作链外层闸，影响全体有工作的 NPC；既有目标行已逐行核对行为不变，见 §2.4）
- 适用代码快照：`master @ 3574a2d5f`
- 前置：Plan 22 一~四期与 2026-09-12 第五轮复查已完成

---

## 1. 目标

1. `find_character_target` 里不再出现养成系统的教师判定、上课判定、实操课预到岗三处特例调用，也不再有 `student_flag`；
   工作链对教师、学生与其他 `auto_ai=0` 岗位一视同仁
2. 教师与学生的全部「上班」行为由 `target.csv` 的 21/22 类行 + 前提 + 既有状态机表达；WorkType 151/152 不再挂着走不到的自动 AI 数据
3. 行为口径与现状逐条一致（§5 对照表），只有以下有意的变化：
   - 课表只对学生岗生效（口径 1）
   - 教师、学生受 normal 前提约束（口径 2；学生按同一规则）
   - 翘课每节只掷一次（§3.5）
   - 待赴实操课时人已在教室，改为原地等开课（§3.6）
   - 教室课的教室解析不出时交回既有 AI，不再在随机理论教室之间打转（§3.7）
4. 随 normal 前提生效，修掉从代码推断的两个潜在问题（§2.5）：跟随中的教师 / 学生在玩家与教室间来回走；
   临盆 / 产后的教师被反复瞬移回住院部、学生对着「可用的教师」空坐一节

**验收标准**：
- 全套回归测试通过（`test_class_ai` 按本方案改写后）
- 行为循环测试里，本节有课的教师都在课表那间教室授课，上午四节人均出勤 ≥3
- `handle_npc_ai.py` 中 grep 不到 `judge_teacher_state_machine`、`judge_class_state_machine`、`judge_pre_arrive_sex_class`、`STUDENT_WORK_TYPE`

## 2. 现状调查

### 2.1 `find_character_target` 的优先级链

`Script/Design/handle_npc_ai.py:277 find_character_target`，在 NPC 行为为「发呆」时由 `character_behavior.py:167` 调用。
各段只在前面都没派出行为（`judge == 0`）时才执行：

| 顺序 | 段 | 代码落点 | 进入条件 / 检索方式 |
| --- | --- | --- | --- |
| 0 | H 模式早退 | `:291` | H 中且不是群交自慰 → 直接结束 |
| 1 | 高优先 type 0 | `:308` | 无条件；按权重随机 |
| 2 | 需求链 12 → 13 → 11 | `:314~330` | 12 需 `not normal_1`、13 需 `unnormal_27`；`get_first_only`，行序即优先级 |
| 3 | 助理链 42 → 43 → 41 | `:332~350` | `is_assistant` |
| 4 | 实操课预到岗（**特例**） | `:353~356` | `class_ai.judge_pre_arrive_sex_class` |
| 5 | 上课判定（**特例**） | `:360~363` | `class_ai.judge_class_state_machine`，对所有人生效，不看岗位与星期 |
| 6 | 教师判定（**特例**） | `:366~369` | `class_ai.judge_teacher_state_machine` |
| 7 | 见学 | `:373~376` | `class_ai.judge_follow_mother_state_machine`（幼女 / 萝莉） |
| 8 | 工作链 | `:381~415` | `have_work` 且 `to_work_time_or_work_time` 且**不是学生岗**（`student_flag`，**特例**） |
| 9 | 娱乐链 32 → 33 → 31 | `:417~455` | `all_entertainment_time`；结构与工作链相同 |
| 10 | 全表搜索 | `:458~479` | 除已检索过的类型外的全部目标行 |
| — | 派发 | `:484~505` | 命中目标行 → 该行的 `state_machine_id`；自动 AI 或特例 → 返回值即状态机 id；时长 ≤0 补为 1 |

### 2.2 工作链的两种形态与检索语义

工作链（`:384~415`）按岗位在 `WorkType.csv` 的 `auto_ai` 列分两种形态：

| 形态 | 「进行工作」 | 「工作准备」 | 现有岗位 |
| --- | --- | --- | --- |
| `auto_ai=1` | 人在 `place`（场景名）或 `place_tag`（场景标签）→ `npc_auto_work_or_entertainment(work)`，前提 `{work_time, normal_all_except_special_hypnosis, 额外前提}`；**不在** → 检索 type 22 行 | `npc_auto_work_or_entertainment(move)`，前提 `{work_time, normal_all, 额外前提}`（`:618`） | 供能、铁匠、厨师、坐诊医生、招募、训练、健身、交易、生产、外交、邀请、保育员、种植、按摩、监狱长，以及**当前的教师 151 / 学生 152** |
| `auto_ai=0` | 检索 type 22 行 | 检索 type 21 行 | 检修工程师、宿舍管理员、住院医生、图书馆管理员、性爱练习生 |

自动 AI 的数据格式为「状态机 id|额外前提」，如保育员的 `330|nursery_have_work_to_do`。

`search_target`（`:517`）的检索语义：
- 行的前提集合来自 `game_config.config_target_premise_data`（`Script/Config/game_config.py:1516 load_target`，按 `|` 拆开存成 set）
- 逐行逐前提求值，结果按前提名缓存在 `premise_data` 里，**一次决策内所有行共享**；任一前提为 0 则该行出局
- 行权重 = 各前提返回值之和。`to_work_time` / `work_time` 返回 50（`handle_premise_time.py:347/367`），`to_work_time_or_work_time` 返回 1，多数前提返回 1
- `get_first_only` 时取第一条命中的行；否则权重 ≥100 立即返回（`:604`），其余按权重随机（`value_handle.get_rand_value_for_value_region`，权重即概率）
- 检索过的类型加入 `null_target_set`，末尾的全表搜索不再检索它们

`target.csv` 的约定（`.github/prompts/数据处理工作流/CSV数据加载机制说明.md` §3）：
- cid = type×10000 + 组号×100 + 组内序号×5，物理行序即优先级
- 构建时 cid 会加上目录名前缀（如 `default210100`）
- 文件为 CRLF，不能写 `#` 注释行
- `tools/lint_target_csv.py` 校验 8 条规则；完整模式下还检查前提与状态机是否已注册
- type 21 与 type 22 现有组号都用到 06（`target.csv:95~125`）

### 2.3 养成系统的特例与现行为（并入后的对照基准）

**教师**（`class_ai.py:118 judge_teacher_state_machine`，第五轮新增，排在工作链之前）：

| 情形 | 现行为 |
| --- | --- |
| 本节有课（任何星期） | 不在课表那间教室 → 561 移动；在 → 303 授课 |
| 本节没课、20 分钟内有下一节 | 不在那间教室 → 561；在 → 720 原地等开课 |
| 都没有、到岗或工作时间 | 不在教师办公室 → 562；在 → 720 待命（最多 30 分钟） |
| 都没有、非工作时间 | 交回链（晚上、周日没课） |
| 任何 normal 状态 | **不检查** |

**学生**（`class_ai.py:288 judge_class_state_machine` 与 `:221 judge_pre_arrive_sex_class`；对**任何有个人课表的人**生效，含改了岗的女儿）：

| 情形 | 现行为 |
| --- | --- |
| 下一节是自己的实操课、10 分钟内开始 | 不在那间教室 → 561；在 → 返回 0，继续按本节课判（§2.6-3 的缝） |
| 节次外、开课前 20 分钟内那节有课 | 不在上课地点 → 561（教室课）/ 715（个人课）；在 → 720 |
| 本节有课，体力 <30%、非必修 | 记一节缺课（`settle_absent`）+ REST 43 |
| 本节有课，非必修，今日已翘课或掷中 | 714 翘课（每次决策重掷） |
| 本节是教室课 | 不在教室 → 561；在教室且教师可用 → 304 听课；不可用 → 713 自习 |
| 本节是个人式课 | 地点解析不出 → 交回链；不在地点 → 715；在 → 716 |
| 本节没课 | 学生岗跳过工作链（`handle_npc_ai.py:383`），白天算娱乐时间（`handle_premise_time.py:408 _judge_free_daytime`）→ 见学 / 娱乐 |
| 上课接管时 | 清见学标记（`class_ai.py:303`） |
| 任何 normal 状态 | **不检查** |

**死数据**：WorkType 151（`WorkType.csv:24`，auto_ai 561/303）与 152（`:25`，561/304）的自动 AI 在工作时间内已被上面的特例全部截走，永远走不到。

### 2.4 外层闸改为只判「有工作」的影响核对

逐行核对 `target.csv` 的 type 21/22：

- 除体检链 4 行外，全部带 `to_work_time` 或 `work_time`。体检链是 210500（`:107`）与 220500 / 220505 / 220510（`:121~123`），与岗位无关、不带时间前提
- 改动前：非工作时间工作链被跳过，体检链行在末尾的全表搜索里命中
- 改动后：`auto_ai=0` 岗位在工作链里就能检索到这 4 行；`auto_ai=1` 岗位只在不在岗位地点时检索 type 22 的 3 行。行与前提都不变，只是比娱乐链先检索。无工作的人不受影响
- 自动 AI 路径自带 `work_time`（`:637`），非工作时间两次调用都返回 0，结果不变
- 性能：有工作的 NPC 在非工作时间每次决策多检索一次 type 22（约 30 行，前提结果一次决策内缓存）；开销小于末尾本就要做的全表搜索（约 180 行）

### 2.5 特例绕开 normal 门槛带来的潜在问题（从代码推断，未实跑）

1. **智能跟随来回走**：
   - type 0 目标 100（`target.csv:6`，`is_follow_1|place_1|…`）只在「不在玩家位置」时把人拉回；人到了玩家身边，这一行就不成立
   - 接着走到教师 / 上课特例，被派去教室；到了教室又被目标 100 拉回，于是在玩家与教室之间来回
   - `judge_teacher_available` 把跟随中的教师判为不可用（学生自习），但教师 AI 自己不看跟随。学生同理
2. **临盆 / 产后教师瞬移**：
   - `judge_character_cant_move`（`handle_npc_ai.py:259~273`）每次行动前把人瞬移回住院部
   - 教师 AI 不看 normal_2，照样派她去教室
   - `judge_teacher_available` 也不挡临盆 / 产后，学生就对着「可用的教师」听课、零收益
3. **其他状态不一致**：助理、醉酒、意识模糊、全裸的教师 / 学生照样去上课，与其他岗位不一致

并入后 normal 前提自然生效，第 1、2 条随之消失。实施前先用脚本复现并记录现行为，实施后以测试断言确认（实施文档 §2.0、§4.1）。

### 2.6 已知陷阱与硬约束

1. **前提必须是纯函数**：同一个前提在一次决策里被多行读取、按名缓存。翘课掷骰若每次调用都随机，「翘课」与「照常上课」两行可能同时不成立（上课时间去闲逛）或同时成立（随机二选一）。见 §3.5
2. **行间必须互斥且覆盖完整**：漏一种组合，就会没有行命中、落到娱乐链或全表搜索；叠一种组合，就按权重随机。见 §3.3，用单一状态函数兜底
3. **现行为的一个缝**：待赴实操课时人已在实操教室，`judge_pre_arrive_sex_class` 返回 0，`judge_class_state_machine` 按本节课派 561；
   而 561（`StateMachine/default.py:433`）又按「下一节实操课」把目标定在当前教室，结果原地零距离移动、一分钟一分钟空转到开课。见 §3.6
4. **见学标记**：上课接管时要清见学标记。见学判定排在工作链之前，不成立时自己会清（`class_ai.py:442~445`）
5. **对别的角色读 normal**：`sex_class_handle.py:266 judge_can_join_sex_class` 已有对别的角色调用 `handle_normal_N` 的先例，`judge_teacher_available` 可照用；
   测试里改了状态位后要调用 `handle_premise.refresh_unnormal_flag`
6. **服装不会误伤**：泳衣占 6 胸衣 / 9 内裤，浴巾占 5 上衣 / 8 下衣（`ClothingTem.csv`），而 `handle_premise_cloth.py:587 handle_cloth_most_off` 只看 5/6/8/9，都不会触发 normal_4。
   学生白天游泳或泡澡后下一节有课，`normal_all` 仍然成立，不会因此漏课
7. **构建**：测试引导（`tools/tests/education/_bootstrap.py:81`）会 import `auto_build_config`，每次都从 CSV 重建 `data.json` 并改写 PO。
   本机没有 gettext，PO 会被写乱，收尾必须 `git checkout -- data/po/`
8. **编号**：状态机当前最大为 720（`Script/Core/constant/StateMachine.py:386`）

### 2.7 引用全量清单（改完的归零判据）

| 删改对象 | 引用处 |
| --- | --- |
| `class_ai.judge_teacher_state_machine` | `handle_npc_ai.py:369`；`test_class_ai.py:308~334` |
| `class_ai.judge_class_state_machine` | `handle_npc_ai.py:363`；`schedule_template_handle.py:318`（注释）；`test_class_ai.py:70~140、350~360` |
| `class_ai.judge_pre_arrive_course` | `class_ai.py:299`（模块内部） |
| `class_ai.judge_pre_arrive_sex_class` | `handle_npc_ai.py:356`；`test_class_ai.py:373、381` |
| `student_flag` 与 `education_constant` 导入 | `handle_npc_ai.py:381~384` |
| 课表候选的「女儿并集」 | `growth_handle.py:92~114`；`course_select_panel.py:57~59`；`test_growth.py:163~168` |
| 必修名单候选 | `class_schedule_panel.py:534~541` |
| 描述旧链的文档 | `.github/prompts/数据处理工作流/生长养成系统.md:51、:112、§4（:118~136）、:256~257、:272`；`schedule_template_handle.py:15~18`；`角色行为系统.md:121~130` |

保留不动：
- `judge_teacher_available`：只改实现
- `settle_absent`、`get_skip_class_rate`、`judge_must_attend_sex_class`、`judge_in_scene`
- `get_next_sex_class`：`StateMachine/default.py:452` 也在用
- 见学系列函数

## 3. 设计决策

### 3.1 工作链外层闸只判「有工作」，时间窗交给各目标行

改为 `if judge == 0 and handle_premise.handle_have_work(character_id):`。时间窗由各行自己的时间前提决定：既有行本来就每行都带，
教师 / 学生的课表行则不看星期。影响核对见 §2.4。

| 候选 | 弃选原因 |
| --- | --- |
| 保留外层闸，周日课表对 AI 不生效（排课面板周日置灰） | 丢掉现有玩法：周日排课、周日的临时实操课 |
| WorkType 新增「工作时间前提」列，按岗位换闸 | 多一列配置只为两个岗位服务；而且行上本来就有时间前提，重复表达 |
| 在工作链前单开 51/52「课程链」 | 用户已弃选（口径 1） |

### 3.2 151 / 152 改 `auto_ai=0`，`student_flag` 自然消失

两个岗位改走「检索 21/22 行」的形态。学生没课时没有任何行命中，工作链返回 0，照旧落到见学 / 娱乐链；不再需要在工作链条件上排除学生岗。

### 3.3 一个状态函数 + 薄前提包装，保证行间互斥

- `class_ai.get_course_stage` 把现有的闸门顺序（预到岗 → 到岗时间 → 体力闸 → 心情闸 → 派课）直译为 6 个互斥状态；`get_teacher_duty` 给出教师的 3 个状态
- 前提只做「状态 == X」与地点、课型、教师可用性这类原子判定
- 学生的「照常上课」「翘课」「体力缺课」出自同一个函数的不同分支，不可能同时成立或同时落空

| 候选 | 弃选原因 |
| --- | --- |
| 全部拆成原子前提，在 CSV 里组合 | 预到岗 > 体力闸 > 心情闸的先后要靠每行叠 4~5 个否定前提来表达，组合爆炸且极易漏 |
| 自动 AI 挂一个「分派状态机」 | 逻辑藏进状态机，`target.csv` 里看不见，等于换个地方的特例 |

### 3.4 normal 门槛（口径 2）

- 教师与学生相同：移动 / 等待 / 翘课 / 缺课行用 `normal_all`，授课 / 听课 / 自习 / 个人课行用 `normal_all_except_special_hypnosis`，与既有岗位的 21/22 行完全同款
- `judge_teacher_available` 在现有判定上加 `handle_normal_2`（临盆、产后、监禁）与 `handle_normal_3`（助理、跟随、体检）；原先单独写的监禁、跟随两条被它们覆盖
- 只挂「这一节确定来不了」的持久状态。不挂 1（需求）、4（服装）：教师上个厕所、吃个饭回来照样开讲，学生不该因此整节自习
- 学生侧不需要对应的判定：学生不来，教师照讲

### 3.5 翘课每节只掷一次（定种子）

`roll_skip_class` 用 `random.Random(f"{角色id}|{日期序数}|{节次}")` 定种子，再与 `get_skip_class_rate`（按当下负面状态的等级和查表）比较。

- 前提成为纯函数，同一次决策里各行读到同一个结果
- 每节的翘课概率严格等于表值。原来一节里每做一次决策都重掷一次（移动一次、到场一次），实际概率偏高，与说明文档「每节翘课概率」的口径不符
- `test_behavior_loop.py:85` 给 `get_skip_class_rate` 打的桩照样有效

弃选「在前提里缓存本次决策的掷骰」：前提拿不到本次决策的上下文，只能把结果挂在角色身上，得新增存档字段。

### 3.6 待赴实操课：人已在教室就原地等开课

新增行 220800 → 720，补上 §2.6-3 的缝；时长由 720 截到下一节开始（≤10 分钟）。

### 3.7 上课地点能否解析，决定是否有行命中

`self_in_course_place` 与 `self_not_in_course_place` 都要求地点可解析；解析不出时两个都不成立，没有行命中，交回既有 AI。

- 个人式课：与原口径一致
- 教室课：原先会被 561 的随机回落带去任一理论教室，到了又判不在，来回打转

### 3.8 学生课的移动统一用 715，561 只留给待赴实操课

- `EDUCATION_MOVE_TO_COURSE_PLACE`（`StateMachine/default.py:2787`）经 `schedule_handle.get_course_place` 取目的地：对教室课返回教室（`schedule_handle.py:545`），节次外回退到马上那一节，目的地与原 561 相同
- 561 保留给待赴实操课，因为只有它会先查「下一节」

### 3.9 见学留在工作链之前，只加一条排除

见学是孩子的日程行为，不是工作，位置不动。

- `judge_should_follow_mother` 加一条：学生此刻与课表有关（`get_course_stage` 不为 NONE：本节有课、马上开课、待赴实操课）时不见学，保住原来「预到岗 / 上课判定排在见学之前」的优先级
  - 实施时由「只看 `get_next_sex_class`」放宽为看状态（实施文档 §6.1 偏离 2）：它一并取代了原先「节次内且本节有课」那条判定，
    也盖住了 UPCOMING——见学挪到工作链之前后，到岗时间若撞上日程排了「跟随母亲」的时段，不让路就会被见学截走
  - 只认学生岗：改了岗的女儿课表还在，但她不会去上课（口径 1），不该因此不见学
- 见学判定在工作链之前执行，不成立时会自己清标记，所以上课接管时的清标记（原 `class_ai.py:303`）不再需要

### 3.10 课表只对学生岗（口径 1）

- `get_course_candidate_list` 去掉女儿并集，只留学生岗
- 必修名单候选在女儿名单上再过滤学生岗
- 存档里改岗女儿残留的个人课表不迁移、不清理：没有行会命中，不会生效；她改回学生岗后课表恢复生效
- 学期结算与成绩单不受影响：改岗期间既不记出勤也不记缺课

### 3.11 `_judge_free_daytime` 的学生岗条款保留

它定义的是「学生岗的白天算娱乐时间」，是前提层对岗位的描述，不是 AI 链特例；学生没课时工作链没有行命中，要靠它走到娱乐链。
改成 WorkType 新列只为一个岗位服务，不值得（§7）。

## 4. 接口与数据设计（实施的权威定义）

### 4.1 常量（`education_constant.py` 第 7 组「上课AI：缺课与翘课」末尾）

```python
COURSE_STAGE_NONE = 0
""" 学生此刻与课表无关：本节没课、20 分钟内也没有，或不是学生岗 """
COURSE_STAGE_SEX_PENDING = 1
""" 下一节是自己要上的性技实操课（必修或选修）且 PRE_ARRIVE_MINUTE 分钟内开始，优先于本节的一切 """
COURSE_STAGE_ABSENT_HP = 2
""" 本节有课、体力低于 ABSENT_HP_RATE、不是必修实操课：本节缺课去休息 """
COURSE_STAGE_SKIP = 3
""" 本节有课、不是必修实操课，今日已翘课或本节掷中翘课 """
COURSE_STAGE_ATTEND = 4
""" 本节有课且照常上课（必修实操课在体力不足、心情糟糕时也归入这里） """
COURSE_STAGE_UPCOMING = 5
""" 不在节次内，20 分钟内（schedule_handle.get_upcoming_course 的默认 minute_limit）开始的那一节排了课 """
TEACHER_DUTY_NONE = 0
""" 教师本节与 20 分钟内都没课，或不是教师岗 """
TEACHER_DUTY_NOW = 1
""" 教师本节有课要教 """
TEACHER_DUTY_UPCOMING = 2
""" 教师本节没课，但 20 分钟内（get_upcoming_teaching 的默认 minute_limit）开始的下一节有课 """
```

### 4.2 `class_ai` 新函数（意图示例，实施时以实际代码为准）

```python
def get_teacher_duty(character_id: int) -> Tuple[int, str]:
    """
    教师此刻的课表职责（Plan 24，供工作链的教师前提读取）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    Tuple[int, str] -- (TEACHER_DUTY_* 状态, 该职责对应的教室场景名；无职责时为空字符串)
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == 0 or character_data.work.work_type != education_constant.TEACHER_WORK_TYPE:
        return education_constant.TEACHER_DUTY_NONE, ""
    teaching = schedule_handle.get_now_teaching(character_id)
    if teaching is not None:
        return education_constant.TEACHER_DUTY_NOW, teaching["classroom"]
    upcoming = schedule_handle.get_upcoming_teaching(character_id)
    if upcoming is not None:
        return education_constant.TEACHER_DUTY_UPCOMING, upcoming["classroom"]
    return education_constant.TEACHER_DUTY_NONE, ""


def get_course_stage(character_id: int) -> int:
    """
    学生此刻的上课状态（Plan 24）：把原 judge_pre_arrive_sex_class → judge_class_state_machine 的闸门顺序直译为互斥状态，
    工作链的学生前提都从这里取值，保证 target.csv 的学生行两两互斥
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- COURSE_STAGE_* 之一
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.work.work_type != education_constant.STUDENT_WORK_TYPE:
        return education_constant.COURSE_STAGE_NONE
    now_time = character_data.behavior.start_time
    if now_time is None:
        now_time = cache.game_time
    # 预到岗优先于本节的一切（原 find_character_target 里排在上课判定之前）
    if get_next_sex_class(character_id, now_time)[0] is not None:
        return education_constant.COURSE_STAGE_SEX_PENDING
    now_course = schedule_handle.get_now_course(character_id)
    if now_course is None:
        if schedule_handle.get_upcoming_course(character_id) is not None:
            return education_constant.COURSE_STAGE_UPCOMING
        return education_constant.COURSE_STAGE_NONE
    # 必修实操课两道闸都跳过（口径 60 / 65）
    if judge_must_attend_sex_class(character_id):
        return education_constant.COURSE_STAGE_ATTEND
    # 第一道闸：体力
    if character_data.hit_point_max and character_data.hit_point / character_data.hit_point_max < education_constant.ABSENT_HP_RATE:
        return education_constant.COURSE_STAGE_ABSENT_HP
    # 第二道闸：心情。前提求值不能写数据，所以直接读 child_growth 而不走会惰性创建的 get_child_growth
    growth_data = character_data.child_growth
    if (growth_data is not None and growth_data.skip_class_flag) or roll_skip_class(character_id):
        return education_constant.COURSE_STAGE_SKIP
    return education_constant.COURSE_STAGE_ATTEND


def get_course_place_now_or_upcoming(character_id: int) -> List[str]:
    """
    取本节课（不在节次内时为马上开始的那一节）的上课地点，与 715 移动状态机的取法一致
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    List[str] -- 场景路径，没课或解析不出为空列表
    """
    course = schedule_handle.get_now_course(character_id)
    if course is None:
        course = schedule_handle.get_upcoming_course(character_id)
    if course is None:
        return []
    return schedule_handle.get_course_place(course)


def roll_skip_class(character_id: int) -> bool:
    """
    本节是否掷中翘课：以「角色 + 日期 + 节次」定种子，同一节无论判定多少次结果都相同（Plan 24 §3.5）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    bool -- 是否掷中
    """
    rate = get_skip_class_rate(character_id)
    if rate <= 0:
        return False
    character_data: game_type.Character = cache.character_data[character_id]
    now_time = character_data.behavior.start_time
    if now_time is None:
        now_time = cache.game_time
    period = game_time.get_class_period_by_time(now_time)
    return random.Random(f"{character_id}|{now_time.toordinal()}|{period}").random() < rate
```

注意点：
- 两个状态函数对非本岗一开头就返回 NONE：外层闸放宽后，所有有工作的 NPC 都会检索 21/22 行，前提里的状态函数必须对它们几乎零开销
- 不调用 `growth_handle.get_child_growth`（它会惰性创建养成数据），直接读 `character_data.child_growth` 并判 None——前提求值不能写任何数据
- 时刻取 `behavior.start_time`，为 None 时退回 `cache.game_time`，与 `class_ai` 现有写法一致
- 实施时另加第 5 个函数 `get_pending_sex_classroom(character_id) -> str`：学生岗且有待赴实操课时返回那间教室，否则为空字符串，
  供 `self_in_pending_sex_class_room` / `self_not_in_pending_sex_class_room` 判断人在不在那间教室，前提里就不必再各写一遍取时刻的逻辑（实施文档 §6.1 偏离 1）

### 4.3 新增前提（18 个，放 `handle_premise_work.py`，分组「工作_条件」）

| 前提 id | 常量名 | 含义与实现要点 |
| --- | --- | --- |
| `teacher_have_class_now` | `TEACHER_HAVE_CLASS_NOW` | 自己是教师且本节有课要教（全局课表反查，含当天临时课覆盖层，不看星期）：`get_teacher_duty` 为 NOW |
| `teacher_have_upcoming_class` | `TEACHER_HAVE_UPCOMING_CLASS` | 自己是教师，本节没课但 20 分钟内开始的下一节有课：状态为 UPCOMING |
| `teacher_no_class_duty` | `TEACHER_NO_CLASS_DUTY` | 自己是教师，本节与 20 分钟内都没课：**先判岗位**再判状态为 NONE（非教师返回 0） |
| `teacher_in_duty_classroom` | `TEACHER_IN_DUTY_CLASSROOM` | 状态非 NONE 且人在该职责的教室（`judge_in_scene`） |
| `teacher_not_in_duty_classroom` | `TEACHER_NOT_IN_DUTY_CLASSROOM` | 状态非 NONE 且人不在该职责的教室 |
| `self_sex_class_pending` | `SELF_SEX_CLASS_PENDING` | 自己是学生，下一节是自己要上的性技实操课（必修或选修）且 10 分钟内开始：状态为 SEX_PENDING |
| `self_in_pending_sex_class_room` | `SELF_IN_PENDING_SEX_CLASS_ROOM` | 同上且人已在那间教室（`get_next_sex_class` 的教室 + `judge_in_scene`） |
| `self_not_in_pending_sex_class_room` | `SELF_NOT_IN_PENDING_SEX_CLASS_ROOM` | 同上但人不在那间教室 |
| `self_course_absent_by_hp` | `SELF_COURSE_ABSENT_BY_HP` | 状态为 ABSENT_HP（本节有课、体力 <30%、不是必修实操课） |
| `self_course_skip` | `SELF_COURSE_SKIP` | 状态为 SKIP（本节有课、不是必修实操课，今日已翘课或本节掷中） |
| `self_course_attend` | `SELF_COURSE_ATTEND` | 状态为 ATTEND（本节有课且照常上课） |
| `self_course_upcoming` | `SELF_COURSE_UPCOMING` | 状态为 UPCOMING（节次外，20 分钟内那一节有课） |
| `self_course_is_classroom` | `SELF_COURSE_IS_CLASSROOM` | 自己是学生，本节的课是班级式教室课（理论 / 实践 / 公开） |
| `self_course_is_personal` | `SELF_COURSE_IS_PERSONAL` | 自己是学生，本节的课是个人式课（体育 / 兴趣 / 实习） |
| `self_in_course_place` | `SELF_IN_COURSE_PLACE` | 自己是学生，`get_course_place_now_or_upcoming` 非空且人就在那里 |
| `self_not_in_course_place` | `SELF_NOT_IN_COURSE_PLACE` | 自己是学生，上课地点非空但人不在那里（地点解析不出时与上一条同为 0） |
| `self_course_teacher_available` | `SELF_COURSE_TEACHER_AVAILABLE` | 自己是学生，本节是教室课且 `judge_teacher_available(本节教师)` 成立 |
| `self_course_teacher_unavailable` | `SELF_COURSE_TEACHER_UNAVAILABLE` | 自己是学生，本节是教室课但授课教师这节来不了（或课表没排教师） |

- 所有学生前提对非学生岗返回 0，所有教师前提对非教师岗返回 0
- 返回值一律 0/1，不参与权重调度
- `class_ai` 与 `schedule_handle` 在函数内延迟 import，与 `handle_premise_work.py:932` 等处的既有写法一致
- ArkEditor 的 `Premise.csv` 按 `id,常量名,工作_条件,含义` 同步 18 行

### 4.4 新增状态机 721 `EDUCATION_ABSENT_REST`

```python
@handle_state_machine.add_state_machine(constant.StateMachine.EDUCATION_ABSENT_REST)
def character_education_absent_rest(character_id: int):
    """
    上课：体力不足缺这一节课，记一节缺课后原地休息（Plan 24）
    记缺课原先写在 AI 判定里，前提不能有副作用，所以挪进状态机；settle_absent 自带同一节只记一次的去重
    Keyword arguments:
    character_id -- 角色id
    """
    from Script.System.Education_System import class_ai

    class_ai.settle_absent(character_id)
    character_rest(character_id)
```

`character_rest` 即 REST 43（`StateMachine/default.py:165`，30 分钟休息）。常量加在 `constant/StateMachine.py:386` 之后：`EDUCATION_ABSENT_REST = 721`，注释「上课：体力不足缺课，记一节缺课后休息」。

### 4.5 `target.csv` 新增 16 行

type 21 的两组插在 `210615`（`:111`）之后，type 22 的两组插在 `220605`（`:125`）之后。保持 CRLF，备注列只用全角逗号：

```csv
210700,561,normal_all|work_is_teacher|teacher_have_class_now|teacher_not_in_duty_classroom,21,正常状态下，工作为教师，本节有课，当前不在本节授课的教室，则去该教室
210705,561,normal_all|work_is_teacher|teacher_have_upcoming_class|teacher_not_in_duty_classroom,21,正常状态下，工作为教师，本节没课但20分钟内有下一节，当前不在下一节授课的教室，则提前去该教室
210710,562,normal_all|work_is_teacher|to_work_time_or_work_time|teacher_no_class_duty|not_in_teacher_office,21,正常状态下，工作为教师，在到岗或工作时间，本节与20分钟内都没课，当前不在教师办公室，则回教师办公室
210800,561,normal_all|work_is_student|self_sex_class_pending|self_not_in_pending_sex_class_room,21,正常状态下，工作为学生，下一节是自己要上的性技实操课且10分钟内开始，当前不在那间教室，则提前去该教室
210805,715,normal_all|work_is_student|self_course_attend|self_not_in_course_place,21,正常状态下，工作为学生，本节有课且照常上课，当前不在上课地点，则去上课地点
210810,715,normal_all|work_is_student|self_course_upcoming|self_not_in_course_place,21,正常状态下，工作为学生，不在节次内且20分钟内那一节有课，当前不在上课地点，则提前去上课地点
```

```csv
220700,303,normal_all_except_special_hypnosis|work_is_teacher|teacher_have_class_now|teacher_in_duty_classroom,22,正常状态下或被空气或体控催眠中，工作为教师，本节有课，当前在本节授课的教室，则授课
220705,720,normal_all|work_is_teacher|teacher_have_upcoming_class|teacher_in_duty_classroom,22,正常状态下，工作为教师，本节没课但20分钟内有下一节，当前已在下一节授课的教室，则原地等开课
220710,720,normal_all|work_is_teacher|to_work_time_or_work_time|teacher_no_class_duty|in_teacher_office,22,正常状态下，工作为教师，在到岗或工作时间，本节与20分钟内都没课，当前在教师办公室，则待命到下一节开始
220800,720,normal_all|work_is_student|self_sex_class_pending|self_in_pending_sex_class_room,22,正常状态下，工作为学生，下一节是自己要上的性技实操课且10分钟内开始，当前已在那间教室，则原地等开课
220805,721,normal_all|work_is_student|self_course_absent_by_hp,22,正常状态下，工作为学生，本节有课但体力低于30%且不是必修实操课，则记一节缺课并休息
220810,714,normal_all|work_is_student|self_course_skip,22,正常状态下，工作为学生，本节有课且不是必修实操课，今日已翘课或本节掷中翘课，则翘课
220815,304,normal_all_except_special_hypnosis|work_is_student|self_course_attend|self_course_is_classroom|self_in_course_place|self_course_teacher_available,22,正常状态下或被空气或体控催眠中，工作为学生，本节照常上教室课，当前在该教室，本节教师能到岗，则听课
220820,713,normal_all_except_special_hypnosis|work_is_student|self_course_attend|self_course_is_classroom|self_in_course_place|self_course_teacher_unavailable,22,正常状态下或被空气或体控催眠中，工作为学生，本节照常上教室课，当前在该教室，本节教师来不了，则自习
220825,716,normal_all_except_special_hypnosis|work_is_student|self_course_attend|self_course_is_personal|self_in_course_place,22,正常状态下或被空气或体控催眠中，工作为学生，本节照常上个人式课，当前在上课地点，则执行该课对应的行为
220830,720,normal_all|work_is_student|self_course_upcoming|self_in_course_place,22,正常状态下，工作为学生，不在节次内且20分钟内那一节有课，当前已在上课地点，则原地等开课
```

**互斥与完整性**：
- 教师：`get_teacher_duty` 的三个状态互斥，在 / 不在教室互斥。无职责且不在到岗 / 工作时间时没有行命中，交回链（晚上、周日没课），与现状一致
- 学生：`get_course_stage` 的六个状态互斥。
  - SEX_PENDING 按在 / 不在那间教室二分
  - ATTEND 的教室课按在 / 不在二分，在教室时再按教师可用与否二分；个人课按在 / 不在二分
  - UPCOMING 按在 / 不在二分
  - 地点解析不出时没有行命中，交回链
  - NONE 没有行命中，交回链
- 权重：新行的前提全部返回 1，最大和为 6，碰不到 ≥100 立即返回；同一时刻至多一行命中，权重随机不起作用

### 4.6 `WorkType.csv:24~25`

```csv
151,教师,教育区,教育区教室,Class_Room,0,45,无,0,无,无,给学生上课,无
152,学生,教育区,教育区教室,Class_Room,0,45,无,0,无,无,听老师讲课,无
```

只改 `auto_ai` / `auto_ai_move` / `auto_ai_work` 三列，`place` / `place_tag` 保留（面板显示与岗位描述在用）。

### 4.7 `find_character_target` 改后的相关片段（意图示例）

```python
    # 然后判断见学：孩子的日程行为，不是工作，排在工作链之前（Plan 22 二期 §3.24）
    #    有待赴的实操课时见学判定不成立，工作链里的预到岗行才能接手（Plan 24 §3.9）
    if judge == 0:
        from Script.System.Education_System import class_ai

        judge = class_ai.judge_follow_mother_state_machine(character_id)
    # 然后判断工作：只要有工作就进工作链，时间窗由各目标行自己的时间前提决定
    #    既有 21/22 行都带 to_work_time / work_time，自动 AI 路径自带 work_time；
    #    教师 / 学生的课表行不看星期，周日排的课照常上（Plan 24 §3.1）
    if judge == 0 and handle_premise.handle_have_work(character_id):
        # （内部两种形态不变）
```

原 `:351~369` 的三段特例与 `:377~384` 的 `student_flag` 整段删除。

## 5. 并入后的行为对照

**教师**：

| 情形 | 现行为 | 并入后 | 命中的行 |
| --- | --- | --- | --- |
| 本节有课、不在该教室 | 561 | 561 | 210700 |
| 本节有课、在该教室 | 303 | 303 | 220700 |
| 20 分钟内有下一节、不在那间 | 561 | 561 | 210705 |
| 同上、已在那间 | 720 | 720 | 220705 |
| 都没有、到岗或工作时间、不在办公室 | 562 | 562 | 210710 |
| 同上、在办公室 | 720 | 720 | 220710 |
| 都没有、非工作时间 | 交回链 | 交回链（没有行命中） | — |
| 周日有课 | 照上 | 照上（行不看星期，外层闸只判有工作） | 210700 / 220700 |
| 跟随 / 助理 / 体检中 / 临盆 / 产后 | 照样去上课（来回走、被瞬移） | 不去；学生判教师不可用 → 自习 | — |

**学生**（只对学生岗）：

| 情形 | 现行为 | 并入后 | 命中的行 |
| --- | --- | --- | --- |
| 待赴实操课、不在那间教室 | 561 | 561 | 210800 |
| 待赴实操课、已在那间教室 | 按本节课派 561 → 原地空转 | 720 原地等开课 | 220800 |
| 节次外、20 分钟内有课、不在地点 | 561（教室课）/ 715（个人课） | 715（目的地相同） | 210810 |
| 同上、已在地点 | 720 | 720 | 220830 |
| 本节有课、体力 <30%、非必修 | 记缺课 + REST | 同（由 721 完成） | 220805 |
| 本节有课、非必修、翘课 flag 或掷中 | 714（每次决策重掷） | 714（每节一掷） | 220810 |
| 教室课、不在教室 | 561 | 715（目的地相同） | 210805 |
| 教室课、在教室、教师可用 | 304 | 304 | 220815 |
| 教室课、在教室、教师不可用 | 713 | 713 | 220820 |
| 个人课、不在地点 | 715 | 715 | 210805 |
| 个人课、在地点 | 716 | 716 | 220825 |
| 上课地点解析不出 | 个人课交回链；教室课在随机理论教室间打转 | 都交回链 | — |
| 必修实操课 + 体力不足或心情糟糕 | 照常到场、不记缺课、不翘课 | 同（状态为 ATTEND） | 同上各行 |
| 本节没课 | 跳过工作链 → 见学 / 娱乐 | 没有行命中 → 见学 / 娱乐 | — |
| 改了岗的女儿有课表 | 照样上课 | 不上课，按新岗位工作（口径 1） | — |
| 跟随等 normal 异常 | 照样去上课（来回走） | 不去 | — |

## 6. 风险与注意事项

| 风险 | 说明 | 对策 |
| --- | --- | --- |
| 外层闸影响全体有工作的 NPC | 主决策链改动 | §2.4 逐行核对；实施文档 §2.0 记录改动前的派发基线，改动后对比；跑行为循环测试 |
| 行间漏组合 / 叠组合 | 漏了上课时间去闲逛，叠了随机二选一 | 单一状态函数（§3.3）；测试按 §5 逐行断言派发结果 |
| 前提不纯 | 缓存与多行读取不一致 | 状态函数不写数据、不惰性创建养成数据，掷骰定种子 |
| 助理教师不再授课（口径 2） | 玩家可见的玩法变化 | 说明文档写明；学生侧同步判不可用，直接自习，不会空坐 |
| 改岗女儿不再上课（口径 1） | 玩家可见的玩法变化 | 面板不再列出她；存档里的课表残留无害，改回学生岗即恢复 |
| 翘课概率变化 | 从每次决策一掷改为每节一掷，实际翘课率略降 | 回到说明文档写的「每节概率」口径；数值表不动 |
| 性能 | 非工作时间多检索一次 type 22 | 状态函数对非本岗直接返回；量级见 §2.4 |
| mod 函数替换 | 若有 mod 替换了本 Plan 要删除的 `class_ai` 函数，会失效 | 实施文档 §6.2-8 复核 `mod/` |
| 文档漂移 | 说明文档第四、五轮写着「学生 / 教师不走工作链」 | 实施文档 §2.9 同步改写 |

## 7. 不在本方案范围

- 见学改写为目标行：它是孩子的日程行为，不是工作；本 Plan 只加一条待赴实操课排除
- 娱乐 155「上课（无课时自习）」的自动 AI（`561|713`）：娱乐链本就是数据驱动，不动
- `_judge_free_daytime` 泛化为 WorkType 列（§3.11）
- 玩家「授课」指令 `handle_instruct.py:548 handle_teach` 按 `work_type == 152` 拉人的平行实现
- 旧前提 `teacher_teaching_in_classroom` / `student_not_study_in_classroom`（`handle_premise_place.py:806/831`）只认 `Class_Room` 且写死 151/152
- 自动 AI 岗位（`auto_ai=1`）不检索 type 21 行、在岗时不检索 type 22 行的既有结构
- Plan 22 总纲 §10.2 的五条备忘

## 8. 追加调整

（实施后每轮追加一节，只写设计；实施记录见实施文档 §6.5。暂无）
