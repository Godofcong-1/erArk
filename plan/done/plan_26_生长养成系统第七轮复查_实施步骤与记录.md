# Plan 26（实施步骤与记录）：生长养成系统第七轮复查

> 本文件是 `plan_26_生长养成系统第七轮复查_方案.md`（下文简称"方案"）的**实施步骤清单与过程记录**。
> 需求背景、发现、设计决策、接口定义、风险与范围外事项一律以方案为准；
> 本文件只写"怎么做、怎么验、怎么回滚"，实施过程与结果记入 §6。

- 状态：**已实施**（2026-09-12；方案同日定稿，同日按用户改判修订 §2.2 为胎教折珠与技巧门槛；实施记录见 §6）
- 适用代码快照：`master @ 208352d0c`
- 实施前提：先通读方案 §2~§5；实施中发现与方案冲突的事实，**先更新方案再动代码**
- 实施约定：全程由主代理完成，不派子代理；解释器一律用 `.conda\python.exe`
- 提交建议：
  - §2.1~§2.2（性技经验、胎教折珠、技巧门槛）一个提交：结算口径变化，单独可回滚
  - §2.3~§2.6（实操课：邀请、预约、学生岗、覆盖层、玩家授课）一个提交
  - §2.7~§2.9（个人式课、养成事件、小修）与测试、文档随最后一个提交

---

## 1. 改动文件清单

| 文件 | 类型 | 改动 |
| --- | --- | --- |
| `Script/System/Education_System/education_constant.py` | 改 | 加 `SEX_SKILL_THEORY_EXP_ID`、`SIBLING_PLAY_STAGE_SET`；`PRENATAL_EXP_PER_POINT` 换成 `PRENATAL_JUEL_PER_POINT`；两张科目表的注释去掉胎教用途 |
| `Script/System/Education_System/growth_handle.py` | 改 | `get_class_exp_id`；师生两侧结算改用它；两个候选名单的注释 |
| `Script/System/Education_System/baby_growth_handle.py` | 改 | 出生转写改发习得珠、不写经验；换算与读口改名，另加显示用的 `get_child_prenatal_count` / `get_learn_juel_name`；出生文本；模块注释 |
| `Script/System/Education_System/growth_panel.py` | 改 | 养成总览的胎教底子行改说习得珠 |
| `Script/UI/Panel/body_info_panel.py` | 改 | 孕期胎教行改说习得珠 |
| `Script/Design/handle_ability.py` | 改 | 技巧的额外条件：未成年且全子性技等级和为 0 不升；面板说明加一行 |
| `Script/Core/game_type.py` | 改 | `CHILD_GROWTH.prenatal_point` 注释（只改注释，不动字段） |
| `Script/System/Education_System/sex_class_handle.py` | 改 | `find_reserved_class`、`find_class_to_start`、`get_scene_name`；`get_must_attend_set(classroom)`；`start_sex_class`；`judge_can_join_sex_class` 学生岗；提醒文案 |
| `Script/System/Education_System/schedule_handle.py` | 改 | `judge_scene_open`、`judge_course_need_pass`；`get_teacher_cell(include_temp)`；`judge_teacher_conflict`；`get_now_teaching`；`get_course_place`；`get_upcoming_course` 删参数 |
| `Script/System/Education_System/class_ai.py` | 改 | SEX_PENDING → JOIN（`judge_pending_class_joinable`）；need 校验两处；新增 `judge_mother_followable`，见学决策改走它 |
| `Script/System/Education_System/growth_event_handle.py` | 改 | 同胞只取 102/103；期末事件只推 102/103 |
| `Script/System/Education_System/class_schedule_panel.py` | 改 | 覆盖格「[临]」；选科目页说明与按钮名；排实操课页的跨教室提示 |
| `Script/System/Education_System/course_select_panel.py` | 改 | 体育 / 兴趣 / 实习的「（未开放）」「（条件不符）」 |
| `Script/System/Instruct_System/handle_instruct.py` | 改 | `handle_start_sex_class` 预读主修改用 `find_class_to_start` |
| `Script/System/Sex_System/group_sex_panel.py` | 改 | 课堂模式下的邀请名单 |
| `Script/StateMachine/default.py` | 改 | 722 泛化（清前往群交标记、到场复核）；见学的移动 / 跟随两个状态机改判 `judge_mother_followable` |
| `Script/Settle/default.py` | 改 | 553 见学结算改判 `judge_mother_followable` |
| `Script/Design/second_behavior.py` | 改 | 炫耀只派 102/103 |
| `Script/System/Pregnancy_System/pregnancy_handle.py` | 改 | 成年时清 `show_off_ability` |
| `Script/Design/handle_premise/handle_premise_other.py` | 改 | 新前提 `t_baby_0` |
| `Script/Core/constant_promise.py` | 改 | `T_BABY_0` |
| `Script/Core/constant_effect.py` | 改 | 效果 555 的注释改为出生折习得珠（收尾时 grep 旧说法查到） |
| `Script/Settle/realtime_settle.py` | 改 | 提醒注释 |
| `data/target/default/target.csv` | 改 | 505 加前提；新增 515 |
| `data/csv/InstructConfig.csv` | 改 | 1036 前提 |
| `data/official_event/通用.csv` | 改 | 17 行补婴儿排除 |
| `data/official_event/期末.csv` | 改 | cid 13 前提 |
| `tools/ArkEditor/csv/Premise.csv` | 改 | 增 `t_baby_0` |
| `tools/ArkEditor/csv/Effect.csv` | 改 | 555 的描述同步为出生折习得珠 |
| `tools/tests/education/` 下 `test_growth` / `test_settle_effects` / `test_prenatal_baby` / `test_sex_class` / `test_schedule` / `test_class_ai` / `test_panels` / `test_growth_event` / `test_premise_tokens` / `README.md` | 改 | 见 §2.10 |
| `.github/prompts/数据处理工作流/生长养成系统.md` | 改 | 见 §2.11 |
| `plan/done/plan_22_生长养成系统_总纲.md` | 改 | 状态行与追加的 §12 回指本 Plan；§2.3-11 推论二加注 |
| `plan/done/plan_22_生长养成系统_一期_方案.md` | 改 | §3.1 加注：Plan 26 起课堂发理论经验 |
| `update.log` | 改 | 用 `update-changelog` skill 登记 |

**未改动**：存档结构（无新字段，不需要迁移）、口上 CSV、`Behavior_Data.csv` / `Behavior_Effect.csv`、`WorkType.csv`、`Entertainment.csv`、`Experience*.csv`。

## 2. 详细改动步骤

代码与数据行的权威定义都在方案 §3~§4，这里只写落点与检查点。

### 2.0 改动前的基线（先做，结果记入 §6.2）

1. 跑 `.conda\python.exe tools/tests/education/run_all.py`，记下各文件断言数（README 记载 15 个文件、903 条）
2. 在 scratchpad 重建复现脚本（不入库），以 `tools/tests/education/_bootstrap.py` 为引导；**夹具角色 id 要用有服装模板的**（如 201），否则 `get_npc_cloth` 穿不上衣服、`normal_all` 不成立，派发全部落空（本轮定案时踩过）：
   - H1：NPC 教师上舌技理论课 → 师生口交经验 > 0 且记了口交初体验；膣技自习 → 阴道性交经验增加
   - M1：9:40 在预约 9:45 的实践教室开课 → 另开第 0 节、必修生 713、10:30 下课判拖堂、预约残留
   - M3：当天有临时课 → `judge_teacher_conflict` 为空、一键排课撞课；点「清空本格」删掉每周课
   - M4：玩家在理论教室手动授课 → 学生拿到指技经验
   - M5：体育课排在未解锁的游泳池 → 从教育区入口走到训练\淋浴后每分钟 715 + 等待 1 分钟
   - M6：少女排过家家兴趣课 → 716 执行
   - L1 / L2 / L3：婴儿候选含通用 3 / 5 / 23；成年厨师女儿被推期末事件；改岗女儿进场景学生名单
   - L7：母亲睡着时幼女派见学（本轮未实跑，先复现再改）
   - H1b：满胎教（100 点）的新生儿 17 种经验各 50，其中 7 种是性交类
   - M7：萝莉手里 150 个习得珠、无任何经验 → `gain_ability` 后技巧 1 级、剩 50 珠
3. `git diff --stat` 记下工作区现状

### 2.1 性技经验改理论经验（方案 §3.1）

1. `education_constant.py` 第 6 组末尾加 `SEX_SKILL_THEORY_EXP_ID`（方案 §4.1）
2. `growth_handle.py`：新增 `get_class_exp_id`；`settle_student_class_gain`（`:286`）与 `settle_teacher_class_gain`（`:335`）的 `get_subject_exp_id` 换成它；模块头第 2 条性质改写为「性技科目的课堂只给习得与理论经验，升级要的真实经验由实操课给」
3. 检查点：舌技课后师生 42 不变、171 增加、`first_part_sex_dict` 无键 2；腰技课只有习得

### 2.2 胎教出生转写改发习得珠、技巧门槛（方案 §3.2、§3.12）

1. `education_constant.py` 第 10 组：`PRENATAL_EXP_PER_POINT`（`:351~354`）换成 `PRENATAL_JUEL_PER_POINT = 10`，注释照方案 §4.1；第 2 组 `SUBJECT_ABILITY_LIST`（`:86~88`）与 `FEMALE_SUBJECT_LIST`（`:93~95`）的注释去掉「胎教转写」
2. `baby_growth_handle.py`：
   - 模块注释第 1 条与「转写是全科目少量」一段改写为「出生时折成习得珠、不给经验」及其理由
   - `get_prenatal_exp_value`（`:92`）→ `get_prenatal_juel_value(prenatal_point) -> int`
   - `settle_prenatal_to_child`（`:103`）：删掉经验循环，改为 `child_data.juel.setdefault(LEARN_STATE_ID, 0)` 后加珠；文本「全部科目各获得了{2}点初始经验」→「获得了{2}个{3}」，`{3}` 取 `game_config.config_juel[LEARN_STATE_ID].name`；docstring 同步
   - `get_prenatal_exp_dict`（`:137`）→ `get_child_prenatal_juel(child_id) -> int`
   - 全仓库 grep 确认 `get_prenatal_exp_value`、`get_prenatal_exp_dict`、`PRENATAL_EXP_PER_POINT` 再无引用
3. `body_info_panel.py:190~195`：改调 `get_prenatal_juel_value`，文案「孩子出生时每门科目可获得{1}点初始经验」→「孩子出生时可获得{1}个{2}」
4. `growth_panel.py:156~167`：改调 `get_child_prenatal_juel`，文案「胎教底子：孕期听过{0}次胎教，出生时带来 {1} 个{2}」，次数按 `prenatal_point / PRENATAL_POINT_PER_TIME` 折；注释改写
5. `game_type.py:380`：注释改为「出生时由母亲侧转写来的胎教值；出生当时已按它折成习得珠（Plan 26）」
6. `handle_ability.extra_ability_check` 技巧的 NPC 分支（`:165~177`）：`character_data.talent[7]` 且全子性技等级和为 0 时 `judge = 0`，说明文字加一行「未成年干员至少要有一门子性技达到 1 级」；玩家分支不动
7. 检查点：
   - 满胎教新生儿的 `experience` 全为 0、`juel[9] == 1000`；双胎各 1000；生产面板文本含 200 与 1000
   - 萝莉 150 珠、无性技 → 技巧仍 0、珠仍 150；指技升到 1 级后技巧可升 1 级；成年 NPC 150 珠照旧升技巧 1 级

### 2.3 课堂模式下的邀请（方案 §3.3）

1. `group_sex_panel.py:739~744`：`sex_class_mode` 下改判 `judge_can_join_sex_class(chara_id, check_course=chara_id not in sex_class_handle.get_must_attend_set())`，函数内延迟 import；注释改写
2. `target.csv`：505 前提追加 `sex_class_mode_off`；515 接在 510 之后，保持 CRLF，备注列只用全角逗号
3. `StateMachine/default.py:2958` 722：先清 `go_to_join_group_sex`；`cache.sex_class_mode` 为假或 `judge_can_join_sex_class(character_id, check_course=not 必修)` 不成立时，按 97 的写法等待 1 分钟后返回；否则照旧 `pull_student_into_class` + `settle_attend`；docstring 写明两个调用方（220835、515）
4. 检查点：`.conda\python.exe tools/lint_target_csv.py` 完整模式全部通过（读入行数 +1）

### 2.4 提前开预约课（方案 §3.5）

1. `sex_class_handle.py`：新增 `find_reserved_class`；`get_must_attend_set(classroom="")`；`get_scene_student_list` 传玩家所在教室名；`start_sex_class`（`:629`）按方案表改写
2. `handle_instruct.py:1659~1666`：预读主修改用 `find_reserved_class`
3. `class_ai.get_course_stage`（`:301`）：SEX_PENDING 分支内，待赴的那节已 `running`、人在那间教室、不在 H、能参加 → 返回 JOIN
4. 检查点：9:40 开课复用预约键、不问主修、必修生开课即被拉入、10:30 下课判「按时」、下课后预约 `ended`

### 2.5 覆盖层与玩家授课（方案 §3.6、§3.7）

1. `schedule_handle.get_teacher_cell` 加 `include_temp`，`judge_teacher_conflict` 传 False
2. `schedule_handle.get_now_teaching`：`character_id == 0` 且查到的教室不是玩家所在教室时返回 None（`class_ai.judge_in_scene` 在函数内延迟 import，注意循环导入）
3. `class_schedule_panel.py`：`_draw_week_table` 覆盖格加「[临]」；`_select_subject` 加说明行、改清空按钮名（返回值哨兵不变）；`_edit_sex_class` 的跨教室提示
4. 检查点：当天有临时课时被顶掉的教师判撞课；一键排课不再撞；玩家在理论教室手动授课学生拿学识；在预约的实践教室手动授课拿理论经验

### 2.6 课堂 H 只收学生岗（方案 §3.10）

1. `sex_class_handle.judge_can_join_sex_class`：在 `dead` 判定后加学生岗条件，注释写明口径来源
2. 检查点：改岗女儿不进场景学生名单；必修名单面板不变；成年学生仍走实行值

### 2.7 个人式课的场所开放与 need（方案 §3.8）

1. `schedule_handle.py`：新增 `judge_scene_open`（`judge_classroom_open` 改为调用它）、`judge_course_need_pass`；`get_course_place`（`:536`）三种课型过滤未开放场所
2. `class_ai.get_course_place_now_or_upcoming`（`:356`）与 `get_student_leave_time` 的 B 分支过 `judge_course_need_pass`
3. `course_select_panel._select_target`（`:463`）：兴趣课、实习课的未开放与条件不符置灰（照体育课现有的灰字写法）
4. 检查点：未解锁的游泳池 → 在 / 不在上课地点两个前提同为 0、落到娱乐链；解锁后恢复；少女的过家家兴趣课不派 716

### 2.8 养成事件与学期（方案 §3.4、§3.9）

1. `education_constant.py` 第 14 组加 `SIBLING_PLAY_STAGE_SET`；`growth_event_handle.get_sibling_child_list` 过滤阶段
2. `growth_event_handle.push_semester_event_for_list`：跳过阶段不在 102 / 103 的
3. `data/official_event/通用.csv`：17 行按方案 §3.9 补前提；`期末.csv` cid 13 前提填 `CVP_A1_Growth|7_NE_3`。脚本按 UTF-8 读写并断言行数不变、只改前提列
4. 检查点：`.conda\python.exe tools/official_event_check.py` 通过；婴儿候选不再含那 17 条；成年女儿学期切换不入队期末事件

### 2.9 小修（方案 §3.11）

1. L5：`pregnancy_handle.check_grow_to_girl`（`:650` 起）清空 `show_off_ability`；`second_behavior.judge_child_growth_second_behavior`（`:329`）加阶段判定
2. L6：`constant_promise.py` 加 `T_BABY_0`；`handle_premise_other.py` 在 `handle_t_baby_1` 后加 `handle_t_baby_0`；`InstructConfig.csv:60` 前提列；ArkEditor `Premise.csv` 加行
3. L7：先用 §2.0 的脚本复现，成立再改 `class_ai.judge_mother_available`（实施时改为新增 `judge_mother_followable`，见 §6.1 偏离 1）
4. L8：`growth_handle.py:62~77`、`:104` 注释；`schedule_handle.get_upcoming_course` 删 `now_time` 并改注释（全仓库 grep 确认无人传该参数）；`sex_class_handle.py:561` 文案；`realtime_settle.py:205` 注释

### 2.10 测试

| 文件 | 新增 / 改写 |
| --- | --- |
| `test_growth` | `get_class_exp_id`：7 门性技映射到类型 12、腰技为 0、技能科目不变；常量表守卫（值类型 12、键 ⊆ 性技、女学生可学的 7 门全覆盖）；师生两侧结算不再产生 41~44 / 60~62 / 24；技巧门槛：未成年有珠无性技不升且珠留着、学会一门性技后可升、成年 NPC 不受影响 |
| `test_settle_effects` | 512 舌技课：理论经验增加、无口交初体验；548 膣技自习：性交理论经验增加；512 玩家在别处授课回落学识 |
| `test_prenatal_baby` | 换算改为 100 点 → 1000 珠；双胎 40 点各 400 珠、17 种经验全为 0；1 点 → 10 珠且有文本；`get_child_prenatal_juel` 读口；改写「17 门各得 20 经验」「底子读口」等旧断言 |
| `test_sex_class` | 提前开课复用预约、必修豁免、判档；跨教室挪用；学生岗条件；提醒文案 |
| `test_schedule` | `judge_teacher_conflict` 忽略覆盖层；`get_now_teaching(0)` 只在那间教室；`get_course_place` 过滤未开放；`judge_course_need_pass` |
| `test_class_ai` | 未解锁场所与条件不符交回娱乐链（跑整条 `find_character_target`）；SEX_PENDING 已开讲 → 722；母亲睡觉回落自由玩耍；505 / 515 各自只在对应模式下命中 |
| `test_panels` | 覆盖格「[临]」与清空按钮语义；兴趣 / 实习的「（未开放）」「（条件不符）」；课堂模式邀请名单 |
| `test_growth_event` | 同胞只取 102/103；婴儿候选不含那 17 条；成年女儿不入队期末事件；期末 13 的档位前提 |
| `test_premise_tokens` | `t_baby_0` 已注册、ArkEditor 同步；1036 对婴儿不成立 |
| `README.md` | 覆盖描述与断言总数 |

### 2.11 文档与日志

1. `生长养成系统.md`：
   - §1 挂接表：`group_sex_panel` 的邀请、target 515、`handle_ability` 的技巧门槛
   - §2：阶段表「妊娠期」一行与字段表 `prenatal_point` 的说明改为出生时折珠
   - §3：覆盖格「[临]」、撞课照每周课表判、玩家授课只在临时课教室里才读临时课
   - §4：SEX_PENDING 已开讲 → JOIN；未开放 / 条件不符交回
   - §5：性技科目的课堂收益 = 习得 + 理论经验，升级要的真实经验由实操课给；未成年且无性技不自动升技巧（M7）；旧档不回溯
   - §8：同胞只取 102/103、期末事件只推 102/103、期末 13 前提
   - §9：胎教出生时折成习得珠（每点 10 珠、满值 1000），不再给经验；婴儿不进每晚结算，珠在成长为幼女上线后才开始花
   - §10：提前开课、邀请、学生岗
   - §11：面板的三处提示
   - §12：`t_baby_0`、target 515、722 泛化、两个新常量；`PRENATAL_JUEL_PER_POINT` 取代 `PRENATAL_EXP_PER_POINT`
   - §15：第 5 条候选名单口径；新增「理论经验映射由常量表 + 测试守住」「写每周循环的撞课判定用 `include_temp=False`」
   - §16：测试计数
2. Plan 22 总纲：追加 §12，一行指向本 Plan；总纲 §2.3-11 推论二与一期方案 §3.1 加注「Plan 26 起课堂发理论经验」
3. `update.log`：调用 `update-changelog` skill 登记

## 3. 构建与缓存

```bash
.conda\python.exe tools/lint_target_csv.py            # 改完 target.csv 立即跑（完整模式；脚本结束后进程不会自行退出，要手动停掉）
.conda\python.exe tools/official_event_check.py       # 改完两张事件表跑
.conda\python.exe tools/tests/education/run_all.py    # 测试引导会 import auto_build_config，自动从 CSV 重建 data.json
git diff --stat
git checkout -- data/po/                               # 本机无 gettext，构建会写乱 PO，一律还原
```

- 不需要全量 `buildconfig.py`：没有新增 CSV 列或配置类，也不动口上
- 不涉及地图，不删场景缓存

## 4. 验证清单

### 4.1 单元测试（实施方执行，按 `headless-game-test` 模式 A）

- [x] §2.0 复现脚本：改前全部命中、改后全部不命中（27 / 27，§6.3）
- [x] `lint_target_csv.py` 完整模式通过；`official_event_check.py` 通过
- [x] §2.10 各文件新增断言通过
- [x] `run_all.py` 全部文件 PASS，断言数记入 §6.3

### 4.2 行为循环（实施方执行，按 `headless-game-test` 模式 B）

- [x] `test_behavior_loop.py` 收敛；上午四节人均出勤 ≥ 3；教师在对的教室授课；实操课到场断言不变（18 条，与改前相同）

### 4.3 游戏内整体测试（由用户执行）

- [ ] 上完一节舌技理论课，女儿的经验里是口交理论经验、没有口交经验与口交初体验履历
- [ ] 满胎教的孩子出生：生产面板说获得了 1000 个习得珠，孩子的经验里一项都没有；她成长为幼女后的第一晚，技巧不升
- [ ] 开课前 5 分钟在预约的实践教室开课：不再问主修，必修生一起被拉进来，按时下课口上是「按时」
- [ ] 实操课中点「邀请」：名单只有没到场的学生岗，受邀者到场后加入课堂
- [ ] 当天有临时课的格子显示「[临]」；给被顶掉的教师排同一节别的教室时置灰
- [ ] 体育课排在未解锁的游泳池：面板标「（未开放）」；已排的学生不再去门口空转
- [ ] Tk 与 Web 两种模式下教育管理面板显示正常

## 5. 回滚

| 单元 | 内容 | 回滚方式 | 备注 |
| --- | --- | --- | --- |
| A：结算口径 | §2.1、§2.2 | 整体 `git revert` | 已经发下去的理论经验留在存档里，无害（不参与升级）；已折给新生儿的习得珠是普通的珠，留着无害 |
| B：实操课 | §2.3~§2.6 | 整体 `git revert` | 505 / 515 与 722 泛化互相依赖，必须一起回滚 |
| C：个人式课、事件、小修 | §2.7~§2.9 | 可单独 `git revert` | 事件表回滚后跑一次 `official_event_check.py` |

- 不涉及存档字段，改动前后的存档互相兼容
- 回滚 CSV 后跑一次测试或启动游戏，让 `data.json` 重建；之后还原 `data/po/`

## 6. 实施过程记录

### 6.1 实际改动

按方案 §3~§4 落地：代码 23 个、数据 6 个（含 ArkEditor 两张表）、测试 9 个（`git diff --shortstat` 这 38 个文件 +950 / −171 行），另有测试 README、说明文档、`update.log`、Plan 22 总纲与一期方案；逐文件改动见 §1（已按实际更新）。存档结构不变。

与方案的偏离：

1. **L7 改为新增 `judge_mother_followable`，不动 `judge_mother_available`**。方案写的是给 `judge_mother_available` 加睡觉判定；实施时发现它同时是公务事件前提 `self_mother_available` 的判据，而养成事件在跨天结算（`past_day_settle.check_new_day_official_event`）时派发，那时母亲多半在睡，加进去会让带母亲的事件几乎都抽不到。改为新增 `class_ai.judge_mother_followable` = `judge_mother_available` + 母亲不在睡觉（`sp_flag.sleep` 或行为是睡觉），见学的决策（`judge_follow_mother_state_machine`）、`EDUCATION_MOVE_TO_MOTHER` / `EDUCATION_FOLLOW_MOTHER` 两个状态机与 553 见学结算改走它。方案 §3.11 / §4.2 已回写
2. **开课的查找多一个 `find_class_to_start`**。`find_reserved_class` 只找未开讲、未下课的预约，预约课下课后在同一间教室同一节再开时找不到那条，会另建当场课覆盖同一个键；`find_class_to_start` 先找预约、再找本节同教室的那条，`start_sex_class` 与 `handle_start_sex_class` 都走它（`test_sex_class` 的「下课后同节重开」覆盖）
3. **抽出几个小函数**：`sex_class_handle.get_scene_name`（开课与预读主修都要玩家所在的教室名）；`class_ai.judge_pending_class_joinable`（§3.5 配套的 JOIN 判定：实操课模式、那节已开讲、自己不在 H、人在那间教室、`judge_can_join_sex_class` 成立，必修的豁免前置修习）；`baby_growth_handle.get_child_prenatal_count` 与 `get_learn_juel_name`（养成总览显示胎教次数；珠名从配置取，取不到返回空串）
4. **实习课的「（未开放）」也覆盖岗位场所一间都没有的情形**：面板按 `get_course_place` 解析不出置灰，场所标签在地图上没有房间的岗位同样灰掉（此前可选，选了也上不成）
5. **复现脚本的 L7 检查**改为看 `judge_follow_mother_state_machine` 的派发结果（因偏离 1，`judge_mother_available` 本身不再变化）；改前那次运行用的是原检查（母亲睡着时 `judge_mother_available` 仍返回母亲），已命中

已知限制：

- 旧档不回溯：孩子已攒下的性交经验与口交初体验、按旧规则出生时拿到的 17 种胎教经验、已经升了的技巧都保留；养成总览的胎教底子行按现行比例显示珠数，与旧档孩子当年实际拿到的不符（方案 §6）
- 学生都已按课表到场时，课堂模式的邀请名单为空（符合语义）
- 养成系统的代码词条仍未提取进 PO（方案 §7）

### 6.2 实施前的假设复核

以下是定案时（2026-09-12，`master @ 208352d0c`）已经复核过的事实，实施前只需抽查；未复核的标「待查」：

| # | 方案中的事实 | 出处 | 复核结果 |
| --- | --- | --- | --- |
| 1 | 性技科目解出的经验：70→41、71→42、72→44、73→43、74→61、75→62、76→60、77→24 | `AbilityUp.csv:242~` | **成立** |
| 2 | 类型 12 理论经验 170~176，全仓库无发放方、不在升级需求里 | `Experience.csv:132~138`；全仓库 grep | **成立** |
| 3 | `common_default` 对经验 42 有「补记口交初体验」钩子，不看来源 | `common_default.py:973~982` | **成立**（复现：舌技课师生都被记） |
| 4 | 开课按「当前节次」找预约，节次首尾相接，开课前 5 分钟落在上一节 | `sex_class_handle.py:647`；`game_time.py:519` | **成立**（复现） |
| 5 | 邀请名单在课堂模式下跳过实行值；受邀到场经 505 → 96 → 376（效果 462 自身进 H） | `group_sex_panel.py:742`；`target.csv:15`；`Behavior_Effect.csv:186` | **成立**（读代码） |
| 6 | 被顶掉的教师在撞课判定里查不到 | `schedule_handle.py:208` | **成立**（复现：一键排课撞课） |
| 7 | 未解锁场所的寻路在门口返回 `wait_open`、移动时长 0 | `character_move.py:118~141` | **成立**（行走模拟） |
| 8 | CVP 支持 `NE`；target 类型 0 组 5 的 515 空闲；状态机无需新号 | `handle_premise/__init__.py:633`；`target.csv:14~17` | **成立** |
| 9 | 母亲睡着时幼女仍会见学 | `class_ai.py:542` | **成立**（§2.0 脚本复现：母亲 `sp_flag.sleep` 时 `judge_mother_available` 仍返回母亲；另查到它也是公务事件前提的判据，见 §6.1 偏离 1） |
| 10 | 满胎教新生儿 17 种经验各 50，其中 7 种是性交类 | `baby_growth_handle.py:124` | **成立**（实测） |
| 11 | 习得状态 450 以内 1:1 折珠；学识理论课一节 131 珠、自习 73 珠 | `attr_calculation.py:575`；512 / 548 实跑 | **成立**（实测） |
| 12 | 技巧 0→1 级只要 `J9\|100`，额外条件在 0 级恒成立，按行序排在科目之前 | `AbilityUp.csv:104`；`handle_ability.py:165~177` | **成立**（实测：萝莉 150 珠 → 技巧 1） |
| 13 | 新生儿不在 `npc_id_got`，成长为幼女时经 `get_new_character` 上线；睡眠结算只遍历 `npc_id_got` | `character_handle.py:199`；`pregnancy_handle.py:560`；`sleep_settle.py:45` | **成立**（读代码） |

### 6.3 单元测试结果

- 改前基线：15 个文件、903 条断言全绿
- 改后：15 个文件、**993 条**断言全绿（+90）

| 文件 | 改前 | 改后 |
| --- | --- | --- |
| `test_class_ai` | 205 | 224 |
| `test_sex_class` | 70 | 87 |
| `test_schedule` | 46 | 60 |
| `test_growth` | 62 | 74 |
| `test_panels` | 62 | 74 |
| `test_growth_event` | 36 | 41 |
| `test_settle_effects` | 65 | 70 |
| `test_premise_tokens` | 111 | 115 |
| `test_prenatal_baby` | 34 | 36 |
| 其余 6 个（`auto_schedule` 25、`behavior_loop` 18、`save_compat` 12、`schedule_template` 57、`semester` 43、`talk_data` 57） | 212 | 212 |

- 复现脚本（scratchpad，不入库）：改前 27 项全部命中（PASS=27），改后全部不命中（PASS=0 FAIL=27，脚本以「缺陷仍在」为 PASS）
- `lint_target_csv.py` 完整模式：读入 180 行、全部规则通过（数据行比改前多 1 行，即 515；脚本跑完不自行退出，用 240 秒超时停掉）；`official_event_check.py` 通过（`test_talk_data` 里也跑一遍）
- 关键实测值：
  - 满胎教新生儿 `juel[9] == 1000`、经验全为 0；双胎各 40 点 → 各 400 珠，生产文本含「80 次」与珠数；1 点 → 10 珠
  - 舌技理论课：师生口交经验（42）不变、口交理论经验（171）增加、无口交初体验；膣技自习 → 性交理论经验（174）；腰技只有习得
  - 萝莉 150 珠、无任何性技 → 技巧仍 0、珠仍 150；指技 1 级后技巧升 1、剩 50 珠；成年 NPC 150 珠照旧升技巧 1
  - 9:40 在预约 9:45 的实践教室开课：复用预约键、必修生被拉入、按预约时刻下课判「按时」、下课后预约 `ended`
  - 玩家在理论教室手动授课 → 学生拿学识；在预约的实践教室手动授课 → 手交理论经验（170）

### 6.4 尚未覆盖的验证

- §4.3 的七项游戏内检查留给用户
- Web 模式只跑了适配器冒烟，教育管理面板的新提示（「[临]」、「（未开放）」「（条件不符）」、跨教室提示）未在浏览器里看过
- PO / MO 未更新（方案 §7）

### 6.5 追加调整实施记录

（与方案 §8 成对，每轮一节，附回归测试计数。暂无）
