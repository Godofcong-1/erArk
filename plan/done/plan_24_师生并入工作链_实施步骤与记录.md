# Plan 24（实施步骤与记录）：教师与学生并入 NPC 工作链

> 本文件是 `plan_24_师生并入工作链_方案.md`（下文简称"方案"）的**实施步骤清单与过程记录**。
> 需求背景、现状调查、设计决策、接口与数据定义、风险与范围外事项一律以方案为准；
> 本文件只写"怎么做、怎么验、怎么回滚"，实施过程与结果记入 §6。

- 状态：**已实施**（2026-09-12；§4.1 / §4.2 全部通过，§4.3 游戏内整体测试待用户执行）
- 适用代码快照：`master @ 3574a2d5f`
- 实施前提：先通读方案 §2~§5；实施中发现与方案冲突的事实，**先更新方案再动代码**
- 实施约定：全程由主代理完成，不派子代理；解释器一律用 `.conda\python.exe`
- 提交建议：
  - §2.1~§2.5、§2.7、§2.8 是一个原子单元（AI 链主体），合成一个提交。拆开会出现「特例已删、目标行未到位」的空窗
  - §2.6 口径收窄可以单独成一个提交
  - §2.9 文档随最后一个提交

---

## 1. 改动文件清单

### 1.1 数据（3 个）

| 文件 | 类型 | 改动 |
| --- | --- | --- |
| `data/target/default/target.csv` | 改 | 新增 16 行：type 21 组 07（教师）/ 08（学生），type 22 组 07 / 08（方案 §4.5） |
| `data/csv/WorkType.csv:24~25` | 改 | 151 / 152 的 `auto_ai` 改为 0，`auto_ai_move` / `auto_ai_work` 改为「无」（方案 §4.6） |
| `tools/ArkEditor/csv/Premise.csv` | 改 | 新增 18 行前提，接在 `:1883 nursery_have_work_to_do` 之后 |

### 1.2 常量（2 个）

| 文件 | 改动 |
| --- | --- |
| `Script/Core/constant_promise.py` | 18 个前提常量，接在 `:3719 NURSERY_HAVE_WORK_TO_DO` 之后，文档串分组「工作_条件」 |
| `Script/Core/constant/StateMachine.py` | `EDUCATION_ABSENT_REST = 721`，接在 `:386` 之后 |

### 1.3 逻辑（9 个）

| 文件 | 改动 |
| --- | --- |
| `Script/System/Education_System/education_constant.py` | 第 7 组末尾加 `COURSE_STAGE_*` 与 `TEACHER_DUTY_*`（方案 §4.1） |
| `Script/System/Education_System/class_ai.py` | 新增 `get_teacher_duty` / `get_course_stage` / `get_course_place_now_or_upcoming` / `roll_skip_class`；删除 `judge_teacher_state_machine` / `judge_class_state_machine` / `judge_pre_arrive_course` / `judge_pre_arrive_sex_class`；改 `judge_teacher_available`、`judge_should_follow_mother` 与模块文档字符串 |
| `Script/Design/handle_premise/handle_premise_work.py` | 18 个前提的实现，接在 `:355 handle_nursery_have_work_to_do` 之后 |
| `Script/StateMachine/default.py` | 721 的实现，接在 `:2922 character_education_wait_next_period` 之后 |
| `Script/Design/handle_npc_ai.py` | 删 `:351~369` 三段特例与 `:377~383` 的 `student_flag`；工作链条件改为只判 `have_work`；更新注释 |
| `Script/System/Education_System/growth_handle.py:92` | `get_course_candidate_list` 只留学生岗，改文档字符串 |
| `Script/System/Education_System/class_schedule_panel.py:534~541` | 必修名单候选再过滤学生岗，改注释 |
| `Script/System/Education_System/course_select_panel.py:57~58` | 改注释：口径由「学生岗 ∪ 女儿」改为「只有学生岗」 |
| `Script/System/Education_System/schedule_template_handle.py:15~18、:318` | 改注释：上课判定已并入工作链 |

### 1.4 测试（5 个）

| 文件 | 改动 |
| --- | --- |
| `tools/tests/education/test_class_ai.py` | 直接调用旧函数的 7 段改为跑整条 `find_character_target`；新增状态函数、normal 门槛、外层闸、口径收窄、见学排除几段（§2.8） |
| `tools/tests/education/test_growth.py:168` | 断言反转：女儿改岗后不在个人课表名单 |
| `tools/tests/education/test_premise_tokens.py` | 新增 18 个前提的注册检查 |
| `tools/tests/education/test_talk_data.py:117~118` | ArkEditor 同步名单补 `teacher_have_class_now`、`self_course_attend` |
| `tools/tests/education/README.md` | 覆盖表与断言总数 |

### 1.5 文档与日志（4 个）

| 文件 | 改动 |
| --- | --- |
| `.github/prompts/数据处理工作流/生长养成系统.md` | `:51` 挂接表、`:112` 教师的 AI、§4 上课 AI 链（`:118~136`）、陷阱 13 / 14（`:256~257`）、测试表（`:272`） |
| `.github/prompts/数据处理工作流/角色行为系统.md` | §3.2（`:121~130`）补工作链的闸与两种形态 |
| `plan/done/plan_22_生长养成系统_总纲.md:17` | 状态行末尾加一句指向本 Plan |
| `update.log` | 用 `update-changelog` skill 登记一条「调整：（养成）……」 |

**未改动**：
- 行为、结算、口上、面板显示逻辑
- 存档结构：无新字段，不需要迁移
- `Target_Type.csv`、`effect.csv`、`Entertainment.csv`（含 155 的自动 AI）
- `buildconfig.py` / `auto_build_config.py`
- `_judge_free_daytime`（方案 §3.11）

## 2. 详细改动步骤

顺序即建议的实施顺序。代码与 CSV 行的权威定义都在方案 §4，这里只写落点与检查点。

### 2.0 改动前的基线（先做，结果记入 §6.2）

1. 跑 `.conda\python.exe tools/tests/education/run_all.py`，记下各文件的断言计数（README 记载为 15 个文件、765 条）
2. 在 scratchpad 写脚本（不入库），沿用 `test_class_ai.py` 的 fixture 与 `dispatch()` 写法，复现方案 §2.5 的两个潜在问题：
   - 跟随：教师 101 / 女儿 201 设 `is_follow = 1`、与玩家同场景、本节有课，连跑两次派发，看是否先派 561、再派 503（目标 100）
   - 临盆：教师设 `talent[22] = 1`，看 `judge_teacher_available(101)` 与学生 201 在教室里的派发（按现状预期：判为可用 → 304）
3. 记录外层闸基线：各新建一名图书馆管理员（101 岗，`auto_ai=0`）和厨师（51 岗，`auto_ai=1`）fixture，记录工作日 19:30、周日 10:00、工作日 10:00 三个时刻的派发状态机
4. `git diff --stat` 记下工作区现状。当前 `data/po/` 两个文件的改动是构建残留（约 −21 万行），收尾时一并还原

### 2.1 常量与状态函数（先写，便于先单测）

1. `education_constant.py` 第 7 组（`:271~288`）末尾加方案 §4.1 的 9 个常量
2. `class_ai.py`：
   - 在 `judge_teacher_available`（`:56`）之后加 `get_teacher_duty`
   - 在 `get_next_sex_class`（`:248`）之后加 `get_course_stage`、`get_course_place_now_or_upcoming`、`roll_skip_class`（方案 §4.2）
   - 补 `from typing import List, Tuple`
3. 检查点：此时还不接入 AI 链，旧函数仍在；先在 `test_class_ai.py` 新增「状态函数」一段（§2.8-2）并跑通

### 2.2 前提

1. `constant_promise.py:3719` 之后加 18 个常量，每个带 `""" 工作_条件 含义 """` 文档串，含义取方案 §4.3
2. `handle_premise_work.py:355` 之后加 18 个 `@add_premise` 函数。每个函数：
   - 带中文 docstring（参数、返回值、功能）
   - 在函数内延迟 import `class_ai` / `schedule_handle`，与本文件 `:932` 的写法一致
   - 先判岗位：教师前提判 151、学生前提判 152，不是本岗直接返回 0
   - 返回 0/1
3. `tools/ArkEditor/csv/Premise.csv:1883` 之后，按 `id,常量名,工作_条件,含义` 加 18 行，保持 CRLF

### 2.3 状态机 721

1. `constant/StateMachine.py:386` 之后加 `EDUCATION_ABSENT_REST = 721` 与注释「上课：体力不足缺课，记一节缺课后休息」
2. `StateMachine/default.py` 在 `character_education_wait_next_period`（`:2922`）之后实现，代码见方案 §4.4

### 2.4 AI 链主体（原子单元，必须一起落地）

1. `target.csv`：
   - type 21 的 6 行插在 `:111`（210615）之后，type 22 的 10 行插在 `:125`（220605）之后
   - 保持 CRLF；备注列只用全角逗号（`csv.DictReader` 会按半角逗号切列）
2. `WorkType.csv:24~25`：按方案 §4.6 改三列
3. `handle_npc_ai.py`：
   - 删除 `:351~369`（预到岗、上课、教师三段特例）
   - 删除 `:377~383`（学生岗注释、`education_constant` 导入、`student_flag`）
   - `:384` 的条件改为 `if judge == 0 and handle_premise.handle_have_work(character_id):`
   - 见学段（`:370~376`）保留，按方案 §4.7 更新注释；同时核对 `find_character_target` 的文档字符串
4. 检查点：
   - 跑 `.conda\python.exe tools/lint_target_csv.py`（完整模式），必须「全部规则通过」，读入行数应为 178（原 162 + 16）
   - 再跑 `test_class_ai.py` 的「没课节次的去向」一段：它原本就走整条链，应保持通过

### 2.5 教师可用性与见学排除

1. `class_ai.py:56 judge_teacher_available`：
   - 玩家分支（`:76~78`）之前的死亡、H、监禁判定不动
   - 玩家分支之后新增 `handle_premise.handle_normal_2(teacher_id)` 与 `handle_normal_3(teacher_id)`，任一不成立即不可用
   - `:85` 那一行里的跟随判定删掉（已被 normal_3 覆盖），睡着的判定保留
   - 住院、离线（`normal_7`）、换岗、不在岛上的判定保留
   - 文档字符串补一句：凡是教师目标行的 normal 前提会挡掉、且一节之内不会自行解除的状态，都要在这里同步
2. `class_ai.py:389 judge_should_follow_mother`：在阶段判定之后、节次判定之前加一条——`get_next_sex_class(character_id, now_time)[0] is not None` 时返回 False，并写注释说明原因（方案 §3.9）

### 2.6 口径收窄到学生岗（可单独成提交）

1. `growth_handle.py:92 get_course_candidate_list`：去掉 `daughter_set` 并集，只保留 `work_type == STUDENT_WORK_TYPE`；文档字符串改写为 Plan 24 口径
2. `class_schedule_panel.py:538`：循环里在 `judge_can_join_sex_class` 之前加「`work_type != STUDENT_WORK_TYPE` 则跳过」，`:534~535` 的注释同步
3. `course_select_panel.py:57~58`：注释改为「职业为学生的全部干员」。`:65` 的空表提示文案已经准确，不动

### 2.7 清理 `class_ai`

1. 删除 `judge_pre_arrive_course`（`:94`）、`judge_teacher_state_machine`（`:118`）、`judge_pre_arrive_sex_class`（`:221`）、`judge_class_state_machine`（`:288`）
2. `get_skip_class_rate` 的文档字符串补一句：概率由 `roll_skip_class` 每节掷一次
3. 模块文档字符串（`:1~16`）改写：由「上课时段的行为决策」改为「上课状态判定——供工作链的教师 / 学生前提读取（Plan 24）」，保留两道闸的说明
4. 全仓库 grep 方案 §2.7 的删除对象，确认引用归零（测试在 §2.8 处理）

### 2.8 测试改写

1. `test_class_ai.py` 的 `dispatch()`（`:246`）加可选参数 `now_time`：缺省仍是 `period_time(0)`；传入时 `set_time(now_time)`，不再强制拨回节次 0
2. 新增「状态函数」一段：
   - `get_teacher_duty`：本节有课 / 20 分钟内有课 / 都没有 / 非教师 / 玩家，五种情形的状态与教室
   - `get_course_stage`：六种状态各至少一例；必修实操课在体力不足、翘课 flag 挂着、掷中翘课三种情况下都是 ATTEND；非学生岗恒为 NONE
   - `roll_skip_class`：同一节连调 20 次结果一致；概率 0 恒为 False、1 恒为 True
3. 把直接调用旧函数的七段改为 `dispatch(cid, now_time)`，期望值按方案 §5 对照表（教室课的移动由 561 改为 715）：
   - 「派课：教室课」`:68~81`
   - 「两道闸」`:83~100`：翘课的桩由 `random.random` 改为 `class_ai.roll_skip_class`；体力缺课断言派 721 且 `absent_count` 加 1
   - 「必修实操课豁免」`:102~131`
   - 「派课：个人式课型」`:133~141`
   - 「教师按课表走班」`:302~343`
   - 「学生到岗时间先去第一节课」`:345~363`
   - 「预到岗」`:365~382`：新增断言，已在实操教室 → 720
4. 新增「normal 门槛」一段（改完状态位后调用 `handle_premise.refresh_unnormal_flag`）：
   - 跟随中的教师 / 学生与玩家同场景、本节有课：派发不落在 {561, 715, 303, 304, 713, 716, 714, 721} 之内
   - 临盆（`talent[22]`）、产后（`talent[23]`）、助理、体检链中的教师：`judge_teacher_available` 为 False，学生在教室派 713
5. 新增「外层闸」一段：图书馆管理员与厨师在 §2.0-3 三个时刻的派发与基线一致；周日有课的教师派 561 / 303
6. 新增「口径收窄」一段：女儿改成 21 岗后，有课表也不派任何上课行，且不在 `get_course_candidate_list` 里；改回 152 后恢复
7. 新增「见学排除」一段：幼女有待赴实操课时 `judge_should_follow_mother` 为 False，派 561
8. `test_growth.py:168`：断言改为 `201 not in get_course_candidate_list()`，说明文字改为「女儿换岗后不在个人课表名单（只认学生岗）」
9. `test_premise_tokens.py`：`:19` 的注册检查名单加入 18 个新前提；教师 / 学生前提各挑两个，断言对另一岗位返回 0
10. `test_talk_data.py:118`：ArkEditor 同步名单补 `teacher_have_class_now`、`self_course_attend`
11. `README.md`：改写 `test_class_ai.py` 一行的覆盖描述；全部跑完后更新文件数与断言总数

### 2.9 文档与日志

1. `生长养成系统.md`：
   - `:51`：挂接表的 `handle_npc_ai` 一行改为「上课 / 授课走工作链的 target 行（21/22 组 07/08），见学在工作链之前」
   - `:112`：「教师的 AI」一段改写为工作链行
   - §4 上课 AI 链：改写为「状态函数 + 16 行目标」，写明翘课每节一掷、待赴实操课原地等开课
   - 陷阱 13 / 14：给学生加新的上课行为时，加在 `target.csv` 组 08 并走 `get_course_stage`；新增会把教师带走的持久状态时，同步 `judge_teacher_available`
   - 测试表同步
2. `角色行为系统.md` §3.2：补工作链的闸（只判有工作）、两种形态、行级时间前提
3. `plan_22_生长养成系统_总纲.md:17`：状态行末尾加「（教师 / 学生的 AI 于 Plan 24 并入通用工作链，见 `plan/…/plan_24_师生并入工作链_方案.md`）」，路径按实施后所在目录写
4. `update.log`：调用 `update-changelog` skill 登记

## 3. 构建与缓存

```bash
# 本机必须用 conda 解释器（裸 python 是 Store 空壳别名）
.conda\python.exe tools/lint_target_csv.py            # 改完 target.csv 立即跑（完整模式，含前提与状态机注册检查）
.conda\python.exe tools/tests/education/run_all.py    # 测试引导会 import auto_build_config，自动从 CSV 重建 data.json
git diff --stat                                        # 收尾：检查构建残留
git checkout -- data/po/                               # 本机无 gettext，构建会把 PO 写乱，一律还原
```

- 不需要跑 `buildconfig.py` 全量重建：没有新增 CSV 列、配置类或翻译词条。`auto_build_config` 的增量构建会重建 `data.json`，`config_def.py` 不会变；若多出空行，同样还原
- 不涉及地图，不需要删场景缓存

## 4. 验证清单

### 4.1 单元测试（实施方执行，按 `headless-game-test` 模式 A）

- [x] `lint_target_csv.py` 完整模式全部规则通过，读入 178 行
- [x] 状态函数：`get_teacher_duty` 五种情形、`get_course_stage` 六种状态与必修豁免、`roll_skip_class` 同节稳定与 0/1 边界（§2.8-2）
- [x] 18 个前提已注册，对非本岗返回 0（`test_premise_tokens.py`）
- [x] 整链派发逐条符合方案 §5：教师 9 种情形、学生 16 种情形（`test_class_ai.py`）
- [x] 待赴实操课时人已在教室 → 720（新行为）
- [x] 教室课的教室解析不出 → 没有上课行命中（新行为）
- [x] 跟随中的教师 / 学生不再被派去教室；临盆、产后、助理、体检中的教师判为不可用，学生派 713（修掉方案 §2.5 的潜在问题，对照 §2.0-2 的基线）
- [x] 外层闸：图书馆管理员、厨师三个时刻的派发与基线一致；周日有课照上
- [x] 口径收窄：改岗女儿不上课、不在课表名单；改回学生岗后恢复
- [x] 见学：有待赴实操课时幼女不见学
- [x] `run_all.py` 全部文件 PASS，记录断言总数（对照 §2.0-1 的基线）

### 4.2 行为循环（实施方执行，按 `headless-game-test` 模式 B）

- [x] `test_behavior_loop.py`：收敛；学生岗女儿进教室；本节有课的教师都在课表那间教室授课；上午四节人均出勤 ≥3；跨天结算正常

### 4.3 游戏内整体测试（由用户执行）

- [ ] 工作日上午：教师按课表走班授课，没课回教师办公室；学生按课表走班，没课的节次按日程或当天随机娱乐活动
- [ ] 周日排一节课：师生照常到场
- [ ] 让一个有课的女儿智能跟随自己：不再在自己与教室之间来回
- [ ] 把一名有课的教师设为助理：她的课学生自习
- [ ] 把一个女儿改成别的岗位：选课面板不再列出她，她按新岗位上班
- [ ] 排一节带必修名单的性技实操课：必修生提前到场，已到场的原地等开课
- [ ] Tk 与 Web 两种绘制模式下，教育管理面板显示正常

## 5. 回滚

| 单元 | 内容 | 回滚方式 | 备注 |
| --- | --- | --- | --- |
| A：AI 链主体 | §2.1~§2.5、§2.7、§2.8 | 整体 `git revert` | 必须整体回滚：只恢复 `handle_npc_ai.py` 会调用已删除的 `class_ai` 函数；只恢复 CSV 则教师 / 学生回到走不到的自动 AI |
| B：口径收窄 | §2.6 | 可单独 `git revert` | A 仍生效时单独回滚 B，改岗女儿会重新出现在面板但仍不会去上课，面板与行为不一致，建议随 A 一起回滚 |
| C：文档与日志 | §2.9 | 随 A / B | — |

- 不涉及存档字段，改动前后的存档互相兼容，回滚不需要迁移
- 回滚 CSV 后跑一次测试或启动游戏，让 `data.json` 重建；之后还原 `data/po/`

## 6. 实施过程记录

### 6.1 实际改动

实施日期 2026-09-12，全程主代理完成，AI 链主体、口径收窄与文档合为一次提交。

**数据**
- `data/target/default/target.csv`：新增 16 行，编号与方案 §4.5 一致。210700 / 210705 / 210710 / 210800 / 210805 / 210810 接在 210615 之后，220700 / 220705 / 220710 / 220800~220830 接在 220605 之后
- `data/csv/WorkType.csv`：151 / 152 的 `auto_ai` / `auto_ai_move` / `auto_ai_work` 改为 `0 / 无 / 无`
- `tools/ArkEditor/csv/Premise.csv`：18 行接在 `nursery_have_work_to_do` 之后
- 三个 CSV 都由 scratchpad 脚本按 CRLF 读写，先查新 id 不存在、锚点行唯一，再一次性写回

**常量**
- `constant_promise.py`：18 个常量接在 `NURSERY_HAVE_WORK_TO_DO` 之后
- `constant/StateMachine.py`：`EDUCATION_ABSENT_REST = 721`

**逻辑**
- `education_constant.py`：第 7 组末尾加 9 个常量
- `class_ai.py`：
  - 新增 `get_teacher_duty` / `get_pending_sex_classroom`（偏离 1）/ `get_course_stage` / `get_course_place_now_or_upcoming` / `roll_skip_class`
  - 删除 `judge_pre_arrive_course` / `judge_teacher_state_machine` / `judge_pre_arrive_sex_class` / `judge_class_state_machine`
  - `judge_teacher_available` 加 normal_2 / normal_3，去掉单独的跟随判定
  - `judge_should_follow_mother` 加让路判定（偏离 2）
  - 改写模块文档串，以及 `get_skip_class_rate`、`clear_follow_mother_flag` 的文档串
- `handle_premise_work.py`：18 个前提放在 `handle_nursery_have_work_to_do` **之前**（偏离 5），前面加一段分组注释
- `StateMachine/default.py`：721 接在 `character_education_wait_next_period` 之后
- `handle_npc_ai.py`：删掉预到岗 / 上课 / 教师三段特例与 `student_flag`，外层闸改为 `handle_have_work`，见学段的注释改写
- `growth_handle.get_course_candidate_list`、`class_schedule_panel` 必修名单、`course_select_panel` 注释、`schedule_template_handle` 两处注释：按 §2.6、§1.3 修改

**测试**
- `test_class_ai.py`：整体重写，`dispatch(cid, now_time)` 每次都把全体 NPC 的异常位刷新一遍
- `test_premise_tokens.py`：注册名单加 18 个；新增「师生工作链前提只认本岗」一段
- `test_growth.py`：两条断言改为新口径
- `test_talk_data.py`：ArkEditor 同步名单加 2 个
- `README.md`：更新计数与覆盖说明
- 另改 `test_behavior_loop.py`（偏离 3）

**文档与日志**
- `生长养成系统.md`：挂接表、状态机表、前提表、「教师的 AI」、§4 整节、见学、没课节次的去向、维护注意 5 / 13 / 14、§16
- `角色行为系统.md` §3.2：补决策优先级、工作链的两种形态
- `plan_22_生长养成系统_总纲.md` 状态行：加一句指向本 Plan
- `update.log`：v0.67 块的调整段 +3、修正段 +4（偏离 4）

**与方案的偏离**
1. **`class_ai` 多了第 5 个新函数 `get_pending_sex_classroom`**。预到岗的两个前提要判断人在不在待赴那间教室，前提里不必再各写一遍取时刻的逻辑。已回写方案 §4.2
2. **见学让路的判据放宽**：由「`get_next_sex_class` 非空」改为「`get_course_stage` 不为 NONE」，同时取代原先的「节次内且本节有课」，并且只认学生岗。已回写方案 §3.9
   - 见学挪到工作链之前后，UPCOMING（到岗时间）撞上日程排了「跟随母亲」的时段，也会被见学截走
   - 改了岗的女儿课表还在，但她不会去上课，不该因此不见学
3. **`test_behavior_loop.py` 不在 §1.4 清单里，但必须改**
   - 行为循环用的存档 11 有 22 个在学女儿，其中只有 12 个是学生岗（其余：92 岗 6 人，62 / 193 / 151 / 31 岗各 1 人）
   - 口径 1 生效后，这 10 人按岗位上班。原断言按 22 人算，实测「在课 11/12/12/12 名 < 80%」「出勤 44/22 人 < 3」，必然失败
   - 改为只统计学生岗女儿；全部女儿的名单只用来避免把女儿拉去当教师
4. **update.log 按 `update-changelog` skill 的体例写**：调整 / 修正不带标签，没有用 §2.9 写的「调整：（养成）……」
5. **只是位置不同**：`handle_premise_work.py` 的 18 个前提放在 `handle_nursery_have_work_to_do` 之前，而不是之后

**已知限制**
- `judge_teacher_available` 读的是教师的异常位掩码缓存，与教师自己那几行的 `normal_all` 同源。所以两边的判定一致，但前提是状态位的改动经过游戏里的 `settle_chara_unnormal_flag` 结算点
- 无头测试直接改状态位时，要先 `refresh_unnormal_flag`（`dispatch` 已统一做）

### 6.2 实施前的假设复核

| # | 方案中的事实 | 出处 | 复核结果 |
| --- | --- | --- | --- |
| 1 | type 21/22 除体检链 4 行外，都带 `to_work_time` / `work_time` | 方案 §2.4 | **成立**：改前 30 行逐行看过，只有 210500 / 220500 / 220505 / 220510 不带 |
| 2 | WorkType 的 `auto_ai*` 字段只有 `handle_npc_ai.py` 读 | 方案 §2.2 | **成立**：`Script/` 下除 `config_def.py` 的字段声明外，只命中 `handle_npc_ai.py` |
| 3 | 715 对教室课解析到教室，节次外回退到马上那一节 | 方案 §3.8 | **成立**：`get_course_place` 对教室课返回 `get_classroom_position`；测试「715 去教室」「开课前 15 分钟 715 去第一节课的教室」通过 |
| 4 | 720 的时长截到下一节开始，且不超过 30 分钟 | `StateMachine/default.py:2922` | **成立**：测试实测 15 分钟（到岗时间）与 8 分钟（预到岗） |
| 5 | 状态机 721 空闲 | `constant/StateMachine.py:386` | **成立**：原最大 720；lint R6 通过 |
| 6 | 泳衣 / 浴巾不触发 normal_4 | 方案 §2.6-6 | **未重新复核**：沿用方案阶段的结论，本次没有改动服装与 normal_4 相关代码 |
| 7 | 18 个前提 id 无重名 | `constant_promise.py` | **成立**：CSV 脚本断言 Premise.csv 里原本没有这些 id；18 个前提都注册成功（`test_premise_tokens`） |
| 8 | `mod/` 下没有 mod 替换或调用本 Plan 要删除的 `class_ai` 函数 | `mod_manager` 的函数替换机制 | **成立**：实施时再 grep 一次，无命中 |
| 9 | 跟随来回走、临盆空坐两个潜在问题可以复现 | 方案 §2.5 | **已复现**，§2.0-2 基线：跟随的教师 / 学生先派 561、到了教室再派 503；临盆 / 产后的教师判为可用，学生派 304，教师派 303。改后：跟随派 100 / 201 → 503，不再派去教室；临盆 / 产后的教师判为不可用，学生派 713，教师不派教学行 |
| 10 | 外层闸改动前后，普通岗位的派发一致 | 方案 §2.4 | **成立**，见下文说明 |

复核 10 的做法与结论：
- 不固定 `PYTHONHASHSEED` 时，同一份代码两次跑出的序列就不同：`search_target` 用 `random.choice(list(set))`，而目标 cid 是字符串，集合的顺序随进程的哈希种子变
- 所以改为固定 `PYTHONHASHSEED=0`：旧代码在 HEAD 的临时 worktree 里跑，新代码在工作区跑
- 图书馆管理员（101 岗，auto_ai=0）与厨师（51 岗，auto_ai=1），在工作日 19:30、周日 10:00、工作日 10:00 三个时刻各跑 6 个随机种子，派发序列**全部相同**

### 6.3 单元测试结果

`run_all.py`：15 个文件全部 PASS，断言 **765 → 843**，失败 0。

| 文件 | 改前 | 改后 | 说明 |
| --- | --- | --- | --- |
| `test_class_ai` | 111 | 167 | 直接调用旧函数的七段改成整链派发；新增状态函数、定种子掷骰、normal 门槛、外层闸、口径收窄、见学让路；实施后应用户要求补了兴趣课逐项、实习课逐岗两段（+8，见下） |
| `test_premise_tokens` | 77 | 99 | 18 个前提的注册检查，外加「只认本岗」4 条 |
| `test_growth` | 62 | 62 | 两条断言改为新口径 |
| `test_behavior_loop` | 14 | 14 | 改为只统计学生岗女儿（偏离 3） |
| 其余 11 个文件 | 501 | 501 | 未改 |

`test_behavior_loop` 的实测：
- 使用存档 11，学生岗女儿 12 人
- 上午四个检查点在课的女儿分别为 11 / 12 / 12 / 12 人
- 本节有课的教师在课表那间教室授课：3 人中依次为 2 / 3 / 3 / 3（唯一的缺席是 179 夜莺第一节在女士洗手间处理需求，断言允许 1 人次）
- 六轮都收敛（NPC ≤ 45 轮）；跨天结算正常

个人式课型的补充覆盖：兴趣课与实习课原先只测到「地点解析不出交回」，实施后补了整链派发。
- **兴趣课逐项**：`Entertainment.csv` 里 `class_ok` 的全部 16 项，不在地点派 715；到场派 716，行为与状态为该娱乐的 `behavior_id`，时长 45 分钟
- **实习课逐岗**：个人课表面板可选的全部 17 个岗位，筛选口径与 `course_select_panel.py:529` 一致。无人在岗时不在地点派 715；到场派 716，执行 `intern_class`，时长 45 分钟
- **导师换房间**：取同一标签下有多间房的岗位，把导师放在非默认的那间。学徒的上课地点改指导师那间，从默认那间派 715 过去，到场派 716，`get_intern_mentor` 找得到这位导师

`lint_target_csv.py` 完整模式：读入 178 行，全部规则通过（脚本结束时进程不会自行退出，要手动停掉）。

### 6.4 尚未覆盖的验证

留给用户的游戏内整体测试，即 §4.3 的七项：
- 工作日上午的师生走班
- 周日排的课照常上
- 智能跟随的女儿不再来回走
- 当助理的教师，她的课学生改为自习
- 改岗的女儿不再出现在选课面板
- 必修生提前到场并原地等开课
- Tk / Web 两种模式下教育管理面板显示正常

另外，翘课改成每节一掷后，实际翘课率会略低于改前。本次只验证了「同一节结果稳定」和「每节概率与表值一致」，没有做长期统计。

### 6.5 追加调整实施记录

（与方案 §8 成对，每轮一节，附回归测试计数。暂无）
