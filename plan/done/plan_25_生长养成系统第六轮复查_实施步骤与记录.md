# Plan 25（实施步骤与记录）：生长养成系统第六轮复查

> 本文件是 `plan_25_生长养成系统第六轮复查_方案.md`（下文简称"方案"）的**实施步骤清单与过程记录**。
> 需求背景、发现、设计决策、接口定义、风险与范围外事项一律以方案为准；
> 本文件只写"怎么做、怎么验、怎么回滚"，实施过程与结果记入 §6。

- 状态：**已实施**（2026-09-12；§4.1 / §4.2 全部通过，§4.3 游戏内整体测试待用户执行）
- 适用代码快照：`master @ 6fa04f1fb`
- 实施前提：先通读方案 §2~§5；实施中发现与方案冲突的事实，**先更新方案再动代码**
- 实施约定：全程由主代理完成，不派子代理；解释器一律用 `.conda\python.exe`
- 提交建议：
  - §2.1~§2.3（打断 + 入课 + 教师可用性，AI 链部分）一个提交
  - §2.4~§2.6（授课指令、303、561、必修名单）一个提交
  - §2.7 清理与文档随最后一个提交

---

## 1. 改动文件清单

| 文件 | 类型 | 改动 |
| --- | --- | --- |
| `Script/System/Education_System/education_constant.py` | 改 | 第 7 组加 `UPCOMING_MINUTE`、`COURSE_STAGE_JOIN_SEX_CLASS` |
| `Script/System/Education_System/class_ai.py` | 改 | 新增 `get_student_leave_time`（实施时取代 `judge_student_should_leave_now`）/ `judge_sex_class_is_mine` / `get_attend_or_join_stage` / `judge_student_pullable` / `judge_student_join_class`；`roll_skip_class`、`judge_must_attend_sex_class` 加 `now_time`；`get_course_stage` 判 JOIN；`judge_teacher_available` 加 normal_5/6 |
| `Script/System/Education_System/schedule_handle.py` | 改 | `get_upcoming_course` 节次内也看、可指定时刻；两个 upcoming 函数默认窗口改用常量 |
| `Script/System/Education_System/sex_class_handle.py` | 改 | 新增 `pull_student_into_class` |
| `Script/System/Education_System/class_schedule_panel.py` | 改 | 必修候选改为全部学生岗（M6）；3 处双重翻译 |
| `Script/System/Education_System/course_select_panel.py` | 改 | docstring / 注释口径；2 处双重翻译 |
| `Script/System/Education_System/student_select.py` | 改 | docstring 口径 |
| `Script/System/Education_System/growth_panel.py`、`semester_handle.py` | 改 | 双重翻译 |
| `Script/System/Education_System/growth_handle.py`、`auto_schedule.py` | 改 | 写死编号换常量 |
| `Script/Design/handle_npc_ai.py` | 改 | `judge_interrupt_character_behavior` 加学生打断段 |
| `Script/StateMachine/default.py` | 改 | 新增 722；303 拉人改用 `judge_student_join_class`；561 预到岗改用 `get_pending_sex_classroom` 并改注释 |
| `Script/Settle/default.py` | 改 | 10014 循环体改调 `pull_student_into_class`；512 对玩家按课表计出勤 |
| `Script/System/Instruct_System/handle_instruct.py` | 改 | `handle_teach` 拉人口径与时刻对齐 |
| `Script/Design/handle_premise/handle_premise_work.py` | 改 | 新前提 `self_course_join_sex_class`；`work_is_teacher/student` 用常量 |
| `Script/Design/handle_premise/handle_premise_place.py` | 改 | 新前提 `in_education_classroom`；改写 `student_not_study_in_classroom`；删 `teacher_teaching_in_classroom` |
| `Script/Design/handle_premise/handle_premise_entertainment.py` | 改 | `== 151` 换常量 |
| `Script/Core/constant_promise.py` | 改 | 增 2 个、删 1 个常量 |
| `Script/Core/constant/StateMachine.py` | 改 | `EDUCATION_JOIN_SEX_CLASS = 722` |
| `data/target/default/target.csv` | 改 | 新增 220835 |
| `data/csv/InstructConfig.csv` | 改 | 2010 的前提列 |
| `tools/ArkEditor/csv/Premise.csv` | 改 | 增 2 行、删 1 行、改 1 行描述 |
| `tools/tests/education/` 下 `test_class_ai` / `test_settle_effects` / `test_premise_tokens` / `test_panels` / `test_behavior_loop` / `README.md` | 改 | 见 §2.8 |
| `.github/prompts/数据处理工作流/生长养成系统.md`、`通用NPC选择面板.md` | 改 | 见 §2.9 |
| `plan/done/plan_22_生长养成系统_总纲.md` | 改 | 追加 §11 一行回指 |
| `update.log` | 改 | 用 `update-changelog` skill 登记 |

**未改动**：存档结构（无新字段，不需要迁移）、口上 CSV（722 复用既有的 `join_sex_class` 二段口上）、`Behavior_Data.csv` / `Behavior_Effect.csv`、`WorkType.csv`。

## 2. 详细改动步骤

代码与 CSV 行的权威定义都在方案 §3~§4，这里只写落点与检查点。

### 2.0 改动前的基线（先做，结果记入 §6.2）

1. 跑 `.conda\python.exe tools/tests/education/run_all.py`，记下各文件断言数（README 记载为 15 个文件、843 条）
2. 在 scratchpad 写脚本（不入库），用 `test_class_ai.py` 的 fixture 复现 M1 / M2 / M3 / M5：
   - 学生 9:00 听课，9:45 有她选修的实操课：跑行为循环到 9:40，看她是否仍在听课（按现状预期：是）
   - 实操课进行中，学生走进教室：看派发（预期 713）
   - 教师 `drunk` 置为 2 级：看 `judge_teacher_available`（预期 True）
   - 体力 20% 的学生在教室等候，教师先处理：看是否被拉进听课（预期：是）
3. `git diff --stat` 记下工作区现状

### 2.1 常量与 `class_ai`

1. `education_constant.py` 第 7 组末尾加方案 §4.1 的两个常量
2. `schedule_handle.get_upcoming_course`：删掉「在节次内就返回 None」的门槛；参数改为 `minute_limit=education_constant.UPCOMING_MINUTE, now_time=None`，`now_time` 为 None 时取 `behavior.start_time`，再退回 `cache.game_time`。`get_upcoming_teaching` 的默认值改用常量
   - 检查点：`get_course_stage` 在课间给出 UPCOMING；`judge_should_follow_mother` 仍然正确让路
3. `class_ai`：
   - `roll_skip_class(character_id, now_time=None)`、`judge_must_attend_sex_class(character_id, now_time=None)`：`now_time` 缺省时的行为与现在一致；节次改由 `get_class_period_by_time(now_time)` 算
   - `judge_student_pullable`、`judge_student_join_class`：见方案 §3.4、§3.5
   - `get_course_stage`：原先返回 ATTEND 的两处（必修生、两道闸之后）统一改走一个小函数 `_attend_or_join(character_id, now_course)`，按方案 §3.2 判 JOIN
   - `judge_teacher_available`：按方案 §3.3 加一条
   - `judge_student_should_leave_now`：按方案 §3.1 的两张表实现。可打断行为的 tag 判定照 `handle_premise_other.py:3387 handle_action_work_or_entertainment` 的写法；WAIT / FOLLOW_MOTHER / FREE_PLAY 显式列入。实施时先查这三个行为在 `Behavior_Data.csv` 的 tag，已含「娱乐 / 工作」的就不必重复列
4. 检查点：先在 `test_class_ai.py` 新增「状态函数（Plan 25）」一段并跑通，再接入 AI 链

### 2.2 打断规则

1. `handle_npc_ai.py:661 judge_interrupt_character_behavior`：在新鲜度守卫（`:674`）之后、休息分支之前插入方案 §3.1 的代码段，`class_ai` 在函数内延迟 import
2. 检查点：
   - 学生 9:35 正在听课、9:45 有她的实操课 → 被打断，派 561，到了派 720
   - 学生正在吃饭 → 不打断
   - 跟随玩家中的学生（normal_3 不成立）→ 不打断
   - 挂着翘课 flag 的学生在娱乐，下一节有课 → 不打断

### 2.3 开课后到场入课（722）

1. `sex_class_handle.pull_student_into_class`：把 `Settle/default.py:3108~3115` 的循环体搬过来（取消移动计划、`is_h`、`see_pl_h`、二段 `JOIN_SEX_CLASS`），10014 改为循环调用它
2. `constant/StateMachine.py` 加 722；`StateMachine/default.py` 在 721 之后实现：先调 `pull_student_into_class`，再调 `settle_attend`
3. `constant_promise.py` 加 `SELF_COURSE_JOIN_SEX_CLASS`；`handle_premise_work.py` 在 Plan 24 那组前提末尾加实现：`get_course_stage == COURSE_STAGE_JOIN_SEX_CLASS`
4. `target.csv`：220835 接在 220830 之后，保持 CRLF，备注列只用全角逗号
5. ArkEditor `Premise.csv` 加一行
6. 检查点：`.conda\python.exe tools/lint_target_csv.py` 完整模式全部通过，读入 179 行（178 + 1）

### 2.4 玩家「授课」指令（2010）

1. `handle_premise_place.py`：
   - 新增 `handle_in_education_classroom`：标签取自 `CLASSROOM_TAG_BY_COURSE_TYPE.values()`，函数内延迟 import
   - 改写 `handle_student_not_study_in_classroom`：只看 `character_id` 所在场景里的其他角色
   - 删掉 `handle_teacher_teaching_in_classroom`
2. `constant_promise.py`：加 `IN_EDUCATION_CLASSROOM`，删 `TEACHER_TEACHING_IN_CLASSROOM`。删之前 grep `teacher_teaching_in_classroom` 全仓库（含 `mod/`、`data/`），结果记入 §6.2
3. `InstructConfig.csv:70`：前提列按方案 §4.3 改
4. `handle_instruct.py:549 handle_teach`：拉人条件改为 `class_ai.judge_student_pullable(chara_id)` 且当前行为不是听课；被拉的人 `behavior.start_time = cache.game_time`
5. `Settle/default.py:7575 handle_teach_add_just`：玩家分支先取 `student_course`，传 `count_attend=(character_id != 0 or (student_course is not None and student_course["classroom"] == scene_data.scene_name))`
6. ArkEditor `Premise.csv`：加 `in_education_classroom`，删 `teacher_teaching_in_classroom`，改 `student_not_study_in_classroom` 的描述

### 2.5 303 与 561

1. `StateMachine/default.py:2698~2722`：拉人循环里原先的 H / 睡着 / 翘课 flag / 休息 / 课表判断，整体换成 `class_ai.judge_student_join_class(chara_id, scene_data.scene_name, character_data.behavior.start_time)`，注释同步
2. `:433 character_move_to_class_room`：预到岗改用 `class_ai.get_pending_sex_classroom`，按方案 §3.6 改写 docstring

### 2.6 必修名单加入成年学生岗（M6）

1. `class_schedule_panel.py:534~545 _select_must_attend`：候选名单改为 `growth_handle.get_course_candidate_list()`，删掉逐人的学生岗过滤，改写注释
2. 其余下游不改（方案 §3.7）

### 2.7 清理

1. 双重翻译 8 处：见方案 §3.8
2. 写死编号 6 处：见方案 §3.8
3. 过期文案：`course_select_panel.py:4 / 108`、`student_select.py:5`

### 2.8 测试

1. `test_class_ai.py` 新增：
   - **打断**：听课中赴实操课、娱乐中赴实操课、娱乐被下一节打断、需求类不打断、跟随中不打断、翘课 flag 不打断、被打断的那节不记缺课
   - **入课**：实操课进行中走进教室 → 722，`is_h` 为真，出勤 +1；开课时已在场的人出勤只记一次；不满足实行值的成年学生 → 仍是 ATTEND
   - **教师可用性**：醉酒不可用；空气 / 体控催眠仍可用
   - **303 过闸**：体力不足、掷中翘课、改了岗的人都不拉；必修生即使体力不足也拉
   - **561**：课表有残留的教师不被带去实操教室
   - **M6**：点名必修的成年学生会预到岗、覆盖掉原本的课
2. `test_settle_effects.py`：玩家在节次外授课，给收益但出勤不变；玩家在学生课表所在的教室、本节授课，出勤 +1
3. `test_premise_tokens.py`：两个新前提已注册；`student_not_study_in_classroom` 只看所在场景；`teacher_teaching_in_classroom` 已不存在
4. `test_panels.py`：`:116` 的断言标签改为「学生岗」；必修名单里出现成年学生岗；不满足实行值的不列出
5. `test_behavior_loop.py`：在存档 11 上预约一节实操课，选修生上一节有课；断言开课时她已在教室，六轮都收敛
6. `README.md`：更新覆盖描述与断言总数

### 2.9 文档与日志

1. `生长养成系统.md`：
   - §1 挂接表：加 `judge_interrupt_character_behavior`
   - §4：预到岗改写为「打断规则 + 预到岗行」；课间 UPCOMING；JOIN 状态与 220835 行
   - §10「谁能来」：开课后到场自动加入；必修名单是全部学生岗
   - §12：状态机补 721 / 722，前提补 2 个，删 `teacher_teaching_in_classroom`
   - §15：第 5 条候选名单口径；第 14 条 `judge_teacher_available` 补 normal_5 / 6
   - §16：测试计数
2. `通用NPC选择面板.md:23`：口径改为「学生岗 / 养成中的女儿」
3. `plan_22_生长养成系统_总纲.md`：追加 §11，写一行指向本 Plan
4. `update.log`：调用 `update-changelog` skill 登记

## 3. 构建与缓存

```bash
.conda\python.exe tools/lint_target_csv.py            # 改完 target.csv 立即跑（完整模式；脚本结束后进程不会自行退出，要手动停掉）
.conda\python.exe tools/tests/education/run_all.py    # 测试引导会 import auto_build_config，自动从 CSV 重建 data.json
git diff --stat
git checkout -- data/po/                               # 本机无 gettext，构建会写乱 PO，一律还原
```

- 不需要全量 `buildconfig.py`：没有新增 CSV 列或配置类
- 不涉及地图，不删场景缓存

## 4. 验证清单

### 4.1 单元测试（实施方执行，按 `headless-game-test` 模式 A）

- [x] `lint_target_csv.py` 完整模式全部通过，读入 179 行
- [x] 截短规则：A 6 种、B 6 种情形（§2.8-1，改为截时长后按行为时间轴断言，见 §6.1 偏离 1）
- [x] 入课：722 与出勤只记一次；实行值守卫
- [x] 教师可用性：醉酒 / 催眠
- [x] 303 过闸 4 种情形 + 必修豁免
- [x] 561 只认学生岗
- [x] 授课指令：前提只看所在场景、三类教室可用、拉人口径、节次外不计出勤
- [x] M6：必修名单含成年学生岗，下游覆盖生效
- [x] 死前提已删、引用归零
- [x] `run_all.py` 全部文件 PASS，断言 843 → 903

### 4.2 行为循环（实施方执行，按 `headless-game-test` 模式 B）

- [x] `test_behavior_loop.py`：实操课开始时必修生都已离开上一节的教室、且已有人在实操教室（断言口径调整见 §6.1 偏离 5）；本节有课的教师都在课表那间教室授课；上午四节人均出勤 ≥ 3；八轮都收敛；跨天结算正常

### 4.3 游戏内整体测试（由用户执行）

- [ ] 预约一节实操课：开课前 10 分钟，上一节在上课的选修生离开教室赶来；第二次提醒的说法与实际相符
- [ ] 当场开课后，陆续走进来的学生自动加入课堂
- [ ] 让一名有课的教师喝醉：她这节的学生改为自习
- [ ] 在实践教室 / 大礼堂对学生用「授课」；在别的教室有学生、自己所在教室没有学生时，指令不可用
- [ ] 排实操课点必修时，名单里有成年学生岗
- [ ] 学生没课的节次在娱乐，下一节开课前会收手去教室
- [ ] Tk 与 Web 两种模式下教育管理面板显示正常

## 5. 回滚

| 单元 | 内容 | 回滚方式 | 备注 |
| --- | --- | --- | --- |
| A：AI 链 | §2.1~§2.3 | 整体 `git revert` | 打断规则、JOIN 状态、722、220835 互相依赖，必须一起回滚 |
| B：授课指令 / 303 / 561 / 必修名单 | §2.4~§2.6 | 可单独 `git revert` | `judge_student_pullable` / `judge_student_join_class` 放在 A 的 `class_ai` 里；只回滚 B 时它们变成未调用函数，无害 |
| C：清理与文档 | §2.7、§2.9 | 随 A / B | — |

- 不涉及存档字段，改动前后的存档互相兼容
- 回滚 CSV 后跑一次测试或启动游戏，让 `data.json` 重建；之后还原 `data/po/`

## 6. 实施过程记录

### 6.1 实际改动

实施日期 2026-09-12，全程主代理完成。

**数据**（三个 CSV 都由 scratchpad 脚本按 CRLF 读写，先断言新 id 不存在、锚点行唯一，全部算好再写回）
- `data/target/default/target.csv`：220835 接在 220830 之后
- `data/csv/InstructConfig.csv`：2010 的前提 `IN_CLASS_ROOM` → `IN_EDUCATION_CLASSROOM`
- `tools/ArkEditor/csv/Premise.csv`：删 `teacher_teaching_in_classroom`；改 `student_not_study_in_classroom` 的描述；`in_education_classroom` 接在 `not_in_auditorium` 之后，`self_course_join_sex_class` 接在 `self_course_teacher_unavailable` 之后

**常量**
- `education_constant.py`：第 7 组末尾加 `COURSE_STAGE_JOIN_SEX_CLASS = 6`、`UPCOMING_MINUTE = 20`
- `constant_promise.py`：加 `IN_EDUCATION_CLASSROOM`、`SELF_COURSE_JOIN_SEX_CLASS`，删 `TEACHER_TEACHING_IN_CLASSROOM`
- `constant/StateMachine.py`：`EDUCATION_JOIN_SEX_CLASS = 722`

**逻辑**
- `class_ai.py`：
  - 新增 `get_student_leave_time` / `judge_sex_class_is_mine` / `get_attend_or_join_stage` / `judge_student_pullable` / `judge_student_join_class`
  - `roll_skip_class` 与 `judge_must_attend_sex_class` 加可选参数 `now_time`
  - `judge_teacher_available` 加 normal_5 / 6（空气 / 体控催眠除外）
  - 补 `game_config` 顶部导入，改写模块文档串
- `schedule_handle.py`：`get_upcoming_course` 去掉「在节次内就返回 None」的门槛、加 `now_time`；两个 upcoming 函数的默认窗口改用 `UPCOMING_MINUTE`
- `sex_class_handle.py`：新增 `pull_student_into_class`
- `handle_npc_ai.py`：`judge_interrupt_character_behavior` 在新鲜度守卫之后加截短段
- `StateMachine/default.py`：
  - 新增 722
  - 303 的拉人循环改为 `judge_student_join_class`
  - 561 预到岗改用 `get_pending_sex_classroom`，并删掉不再用的 `now_time`，docstring 写明三个调用方
- `Settle/default.py`：10014 改调 `pull_student_into_class`；512 按 `scheduled_here` 传 `count_attend`
- `handle_instruct.py`：`handle_teach` 改用 `judge_student_pullable`，对齐开始时刻
- `handle_premise_work.py`：新前提 `self_course_join_sex_class`；`work_is_teacher/student` 改用常量
- `handle_premise_place.py`：新前提 `in_education_classroom`；改写 `student_not_study_in_classroom`；删 `teacher_teaching_in_classroom`
- `handle_premise_entertainment.py`：`== 151` → `ENTERTAINMENT_PLAY_HOUSE`
- `class_schedule_panel.py`：必修名单改用 `get_course_candidate_list`（M6）；3 处双重翻译
- `course_select_panel.py`（2 处双重翻译、docstring 与注释口径）、`student_select.py`（docstring）、`growth_panel.py`、`semester_handle.py`（各双重翻译）
- `growth_handle.py`：`range(40, 50)` → 科目表按类型筛
- `auto_schedule.py`：`>= 70` → `SEX_SKILL_SUBJECT_SET`

**测试**：`test_class_ai`（+38）、`test_settle_effects`（+3）、`test_premise_tokens`（+12）、`test_panels`（+3，另改一条断言标签）、`test_behavior_loop`（+4）、README

**文档与日志**
- `生长养成系统.md`：§1 挂接表、§3 教师段、§4（行数、状态、学生表、第 1 / 2 / 5 条，新增第 8 / 9 条）、§10「谁能来」、§11 个人课表、§12 状态机与前提、§15 第 5 / 13 / 14 条，新增第 16 条、§16
- `通用NPC选择面板.md`：第 23 行口径
- Plan 22 总纲：状态行、§7 表、§11
- `update.log`：v0.67 块的调整段 +4、修正段 +7

**与方案的偏离**
1. **打断改为截短时长**（方案 §3.1 已回写）
   - 初稿「以 `cache.game_time` 为现在、成立就 `end_now=2` 立即结束」在行为循环测试里 0/4 提前到场
   - 原因：行为循环中 `cache.game_time` 是玩家这一步的结束时刻，NPC 按各自的行为时刻追赶；玩家一步走 45 分钟时，「现在」已越过开课，`get_next_sex_class` 只看未开始的节次，判据落空
   - 改为 `get_student_leave_time`：按 NPC 自己的行为时间轴算出应离开的时刻，把 `duration` 截到那一刻
   - 单元测试相应改为断言截出来的时长，并专门造了「玩家这一步已跨过开课」的情形
2. **等待（WAIT）不截**：方案曾把 WAIT 列为可截。它的 tag 是「日常」、用处很杂（被玩家叫住等待等），而学生等开课时本就在教室，截它只有风险没有收益
3. **多抽了两个函数**：`judge_sex_class_is_mine`（`get_next_sex_class` 与截短规则共用）、`get_attend_or_join_stage`（方案写的是私有的 `_attend_or_join`）
4. **update.log 按 `update-changelog` skill 的体例写**：调整 / 修正不带标签
5. **行为循环的到场断言改口径**
   - 方案写的是「至少一半必修生开课时已在实操教室」
   - 两次实跑分别 1/4、2/4：没到的人都已离开上一节的教室，是在路上撞上需求（累了去休息）。需求优先、不截是设计本意，到场人数因此随机
   - 改为两条确定的断言：没人还坐在上一节的教室里（改前 4/4 都在）；已有人在实操教室
6. **测试夹具**：醉酒教师那一段派发时她被派去睡觉，后面的「恢复后可用」要先把她叫醒；断言附带了诊断输出

**已知限制**
- 截短不回退收益：被截短的那节课，收益与出勤在行为开始时已按整节结算过。符合口径 66「提前退场不记缺课」
- 学生在课间最多提前 20 分钟收手去教室，没课节次里的娱乐时间相应变短，与教师同口径
- 路上撞上需求的学生会晚到

### 6.2 实施前的假设复核

| # | 方案中的事实 | 出处 | 复核结果 |
| --- | --- | --- | --- |
| 1 | 状态机 722 空闲 | `constant/StateMachine.py:388` 为 721，下一个已占用的是 751 | **成立** |
| 2 | target 组 08 已用到 220830，220835 空闲 | `target.csv:141` | **成立**；lint 读入 179 行、全部规则通过 |
| 3 | `judge_character_status_time_over(end_now=2)` 会立即结束当前行为 | `character_behavior.py:272`，`end_now` 直接覆盖 `time_judge`，结束后 `start_time` 置为 `now_time` | **成立**，但用不上：见偏离 1，最终做法是截短时长、由循环自然结束 |
| 4 | NPC 的行为结算发生在行为开始时，截短不回退收益 | Plan 22 第五轮 §10 #2 的结论 | **沿用**：本轮没有改动结算时机，没有另写测试 |
| 5 | `teacher_teaching_in_classroom` 没有任何引用 | 删前全仓库 grep（含 `mod/`、`data/`，排除 `plan/`、`data/po/`、pyc） | **成立**：只命中 `constant_promise.py`、`handle_premise_place.py`、ArkEditor `Premise.csv` 三处定义 |
| 6 | 基线行为：M1 听课中不走、M2 自习、M3 醉酒判可用、M5 被拉 | 方案 §2 | **已复现**（scratchpad 脚本）：M1 打断返回 0、仍在听课；M2 晚到派 713；M3 醉酒等级 3、normal_6 为 0、`judge_teacher_available` 为 True；M5 体力 10% 的学生被拉进听课 |
| 7 | 三个行为的 tag | `Behavior_Data.csv` | wait 为「日常」，follow_mother / free_play 为「娱乐」，attent_class / self_study / intern_class / teach 为「工作」 |

### 6.3 单元测试结果

`run_all.py`：15 个文件全部 PASS，断言 **843 → 903**，失败 0。

| 文件 | 改前 | 改后 | 说明 |
| --- | --- | --- | --- |
| `test_class_ai` | 167 | 205 | 醉酒 / 催眠；截短规则 A 与 B 各 6 种情形；开课后到场入课；303 过闸；561 只认学生岗；成年必修生 |
| `test_premise_tokens` | 99 | 111 | 新前提注册、死前提已删、`in_education_classroom` 三类教室、`student_not_study_in_classroom` 只看所在场景 |
| `test_settle_effects` | 62 | 65 | 玩家手动授课：午休不计出勤、课表排在这间教室才计、排在别处不计 |
| `test_panels` | 59 | 62 | 必修名单：成年学生不满足实行值不列、满足则列、教师不列 |
| `test_behavior_loop` | 14 | 18 | 下午预约一节实操课的到场检查（两条）+ 两轮收敛 + 选人 |
| 其余 10 个文件 | 442 | 442 | 未改 |

`test_behavior_loop` 的实测（存档 11，学生岗女儿 12 人，14:45 开课的实践教室一，4 名必修生）：
- 14:45 时 4 人都已离开上一节的教室；2 人已在实践教室等开课（另一次实跑为 1 人），另 2 人 14:38 在活动室休息——她们提前退场后路上累了，需求优先
- 前六轮与后两轮都收敛（NPC ≤ 45 轮）；上午四节在课 11 / 12 / 12 / 12；教师在对的教室授课 2/3、3/3、3/3、3/3（与改前一致）

`lint_target_csv.py` 完整模式：读入 179 行，全部规则通过。

### 6.4 尚未覆盖的验证

留给用户的游戏内整体测试，即 §4.3 的七项。另外：
- 截短规则只在无头行为循环里跑过一个下午，没有做长期统计（课间收手让没课节次的娱乐时间变短多少、翘课与需求交织时的表现）
- PO / MO 词条待在有 xgettext / polib 的环境补跑（本机没有，`data/po/` 已还原）

### 6.5 追加调整实施记录

（与方案 §8 成对，每轮一节，附回归测试计数。暂无）
