# Plan 28（实施步骤与记录）：生长养成系统第九轮复查

> 本文件是 `plan_28_生长养成系统第九轮复查_方案.md`（下文简称"方案"）的**实施步骤清单与过程记录**。
> 需求背景、发现、设计决策、接口定义、风险与范围外事项一律以方案为准；
> 本文件只写"怎么做、怎么验、怎么回滚"，实施过程与结果记入 §6。

- 状态：**已实施**（2026-09-13，记录见 §6）
- 适用代码快照：`master @ ef865f8d1`
- 实施前提：先通读方案 §2~§5；实施中发现与方案冲突的事实，**先更新方案再动代码**
- 实施约定：全程由主代理完成，不派子代理；解释器一律用 `.conda\python.exe`
- 提交建议：改动面不大，可以一个提交。若要拆，分成三份：
  - §2.1 与 §2.9（婴儿事件、夹具）
  - §2.2（个人式课上不成）
  - §2.3~§2.8（照料卵与小修），测试与文档随最后一个提交

---

## 1. 改动文件清单

| 文件 | 类型 | 改动 |
| --- | --- | --- |
| `Script/System/Education_System/growth_event_handle.py` | 改 | `get_growth_event_character_list` 遍历全部角色，婴儿不要求在 `npc_id_got` |
| `Script/System/Education_System/schedule_handle.py` | 改 | 新增 `judge_personal_course_valid`；`get_course_at` 对上不成的个人式课返回 None；`get_now_course` / `get_course_at` 的 docstring |
| `Script/System/Education_System/class_ai.py` | 改 | `get_course_place_now_or_upcoming`、`get_student_leave_time` 删掉重复的 need 判定 |
| `Script/System/Education_System/course_select_panel.py` | 改 | `_get_cell_text` 写「/未开放」「/条件不符」 |
| `Script/System/Education_System/schedule_template_handle.py` | 改 | 新增 `judge_activity_schedulable`；候选、改写、日程行共用，照料卵时段不覆盖 |
| `Script/System/Education_System/sex_class_handle.py` | 改 | `get_selected_student_list` 只收学生岗 |
| `Script/System/Education_System/class_schedule_panel.py` | 改 | `_select_must_attend` 顶替标记按「确有的课」判 |
| `Script/System/Education_System/growth_panel.py` | 改 | `_draw_flag` 写学期名 |
| `Script/UI/Panel/character_info_head.py` | 改 | `get_now_class_tip` 日程自习写「自习中」 |
| `Script/System/Pregnancy_System/pregnancy_handle.py` | 改 | 写死的 152 改用常量 |
| `Script/System/Education_System/education_constant.py`、`Script/Core/constant_promise.py`、`Script/Design/handle_premise/handle_premise_work.py`、`Script/System/Education_System/growth_handle.py`、`Script/Core/game_type.py` | 改 | 只改注释（方案 §3.8） |
| `data/target/default/target.csv`、`tools/ArkEditor/csv/Premise.csv` | 改 | 只改备注 / 描述列（方案 §4.3） |
| `tools/tests/education/_bootstrap.py` | 改 | `make_character` 的婴儿不进 `npc_id_got` |
| `tools/tests/education/` 下 `test_growth_event` / `test_class_ai` / `test_schedule` / `test_settle_effects` / `test_schedule_template` / `test_sex_class` / `test_panels` / `test_premise_tokens`（及婴儿夹具波及的 `test_growth` / `test_prenatal_baby`）/ `README.md` | 改 | 见 §2.10 |
| `.github/prompts/数据处理工作流/生长养成系统.md`、`.github/prompts/数据处理工作流/妊娠系统.md` | 改 | 见 §2.11 |
| `plan/done/plan_22_生长养成系统_总纲.md` | 改 | 追加 §14 一行回指（实施完成后） |
| `update.log` | 改 | 用 `update-changelog` skill 登记 |

**未改动**：
- `character_handle.py`：婴儿照旧不进 `npc_id_got`，方案 §2.5-1
- `egg_handle.py`、`past_day_settle.py`：跨天顺序不变，方案 §3.3
- `official_event_handle.py`、公务事件表、口上 CSV
- `Entertainment.csv`（照料卵的 need 不改）、`Behavior_Data.csv` / `Behavior_Effect.csv`
- 存档迁移：不加字段

## 2. 详细改动步骤

代码与数据行的权威定义都在方案 §3~§4，这里只写落点与检查点。

### 2.0 改动前的基线（先做，结果记入 §6.2）

1. 跑 `.conda\python.exe tools/tests/education/run_all.py`，记下各文件断言数（README 记载 15 个文件、1035 条）
2. 重建复现脚本（不入库）：
   - 定案时的脚本在 scratchpad 的 `repro_plan28.py`，会话结束即丢；丢了照下表重建
   - 以 `tools/tests/education/_bootstrap.py` 为引导，`dispatch()` 照 `test_class_ai.py:38~68`
   - 最小 fixture 的 `Rhodes_Island` 没有派对表，要补 `party_day_of_week = {0..6: 0}`

   | 组 | 检查 | 改后 |
   | --- | --- | --- |
   | N1 | 用 `character_handle.born_new_character(母亲, 名)` 走真实出生路径（随后补 `pregnancy.born_time`，照 `born_event_panel.py:195`）。检查：<br>1 不在 `npc_id_got`<br>2 是女儿、阶段 101<br>3 有候选事件<br>4 不在派发名单<br>5 必派概率拉满连派 30 天派不到<br>6 容量为 0<br>另有一项安全检查：婴儿桶加候选，逐条逐选项 `settle_official_event_option`，不报错 | 4~6 不再成立；1~3 与安全检查照旧 |
   | N2 | 少女（104、学生岗）排着过家家兴趣课：<br>0 地点解析不出<br>1 体力低判 ABSENT_HP<br>2 整链派 721、缺课 +1<br>3 掷中判 SKIP<br>4 整链派 714<br>5 日程排「上课（无课时自习）」、人在理论教室，派 713<br>6 548 出勤 +1<br>7 `<课>` 悬停写兴趣课<br>幼女的体育课排在未解锁的游泳池：<br>8 状态 ATTEND<br>9 不见学<br>10 对照：不排这节课时见学 | 1~4、6~9 不再成立；0、5、10 照旧 |
   | N3 | 改了岗的女儿（岗位 21、修过性技课）课表残留实践教室的一格：<br>1 在 `get_selected_student_list` 里<br>2 修过性技课<br>3 上课状态 NONE、进不了课堂 | 1 不再成立；2、3 照旧 |
   | N4 | 必修名单：<br>1 体育课不标 `*`<br>2 已停课的教室课标 `*` 并列明细<br>3 对照：必修覆盖确实顶掉体育课 | 1、2 不再成立；3 照旧 |
   | N5 | 1 候选有 152<br>2 套给幼女后晚上写成 152<br>3 她没有卵<br>4 427 派孵化卵 60 分钟<br>5 成年学生上午品酒照写（范围外）<br>6 持卵钩子换上 152（打桩 `egg_handle.is_egg_layer` / `have_need_tend_eggs`）<br>7 随后日程改写把它改回 | 1、2、7 不再成立；3~6 照旧（4 是直接调状态机，验的是机制本身；5 范围外） |
   | N6 | 养成总览 `_draw_flag` 写「本学期成绩单待查看」 | 不再成立 |
   | N7 | 本节没排课、行为是自习，`get_now_class_tip` 为「上课中」 | 不再成立 |

   改前 32 项全部成立（19 项问题命中 + 13 项前提 / 对照 / 范围外）。
3. `git diff --stat` 记下工作区现状

### 2.1 婴儿期的养成事件照常派发（方案 §3.1）

1. `growth_event_handle.get_growth_event_character_list`（`:41~65`）：
   - 遍历 `sorted(cache.character_data)`，跳过 0；
   - 入选条件：女儿、阶段在 `STAGE_ALL_CHILD`、`stage == 101 or character_id in cache.npc_id_got`；
   - docstring 写明婴儿为什么不看 `npc_id_got`（出生到长成幼女前都不上线）。
2. 检查点：
   - 婴儿（不在 `npc_id_got`）进名单与容量，必派时派得到；
   - 离线的幼女 / 萝莉仍不进；成年少女仍不进；
   - `official_event_check.py` 通过。

### 2.2 个人式课这一节上不成视为没课（方案 §3.2）

1. `schedule_handle.py`：
   - `judge_course_need_pass` 之后新增 `judge_personal_course_valid(character_id, course)`：`judge_course_need_pass(...) and bool(get_course_place(course))`；
   - `get_course_at`（`:453~464`）的班级式分支之外补 `else`：判不过就返回 None；
   - 同步 `get_now_course` / `get_course_at` 的 docstring：上不成视为没课，必修覆盖不受影响。
2. `class_ai.py`：删掉重复的 need 判定：
   - `get_course_place_now_or_upcoming`（`:399~401`）；
   - `get_student_leave_time`（`:549~551`），保留 `if leave_time is None or not to_place` 的防御；
   - docstring 同步。
3. `course_select_panel._get_cell_text`（`:190~195`）：个人式课先按地点、后按 need 判；上不成就在「[缩写]目标」后接「/未开放」或「/条件不符」。
4. 跑一遍 `run_all.py`，逐条处理因此变化的断言：
   - 夹具依赖「上不成也算有课」的，改成新口径并注明 Plan 28；
   - 实习课无人在岗、必修覆盖相关的断言应当不变。
5. 检查点：
   - 上不成时 `get_course_stage` 为 NONE，体力低与掷中翘课都交回娱乐链、不记缺课；
   - 幼女照常见学；日程自习不计出勤；
   - 解锁或条件恢复后照常上课。

### 2.3 日程模板与照料卵（方案 §3.3）

1. `schedule_template_handle.py`：
   - 新增 `judge_activity_schedulable(entertainment_id)`，函数内 import `pregnancy_constant`；
   - `get_schedule_activity_candidate`（`:405~413`）过滤掉不可排的；
   - `apply_schedule_for_child`（`:352~364`）两处：不可排的跳过；当前槽位值是照料卵的不覆盖；
   - `get_child_slot_activity_text`：不可排的写「X（条件不符→自由选择）」，排在 need 判定之前；
   - 以上 docstring 同步。
2. 检查点：
   - 「选择活动」没有照料卵；
   - 残留的照料卵退回自由选择，日程行写明；
   - 持卵者当天的照料卵时段在改写后仍是照料卵；
   - 其余时段照常改写。

### 2.4 选修人数只数学生岗（方案 §3.4）

1. `sex_class_handle.get_selected_student_list`（`:406~413`）：加 `work_type == STUDENT_WORK_TYPE` 过滤；docstring 同步
2. 检查点：改了岗的女儿不在名单；学生岗照旧

### 2.5 必修名单的顶替标记（方案 §3.5）

1. `class_schedule_panel._select_must_attend`（`:560~573`）：
   - 教室课：每周课表那一格非空才标 `*`、列明细；
   - 个人式课：`judge_personal_course_valid` 成立才标 `*`，明细写「X→课型·目标」，复用 `character_info_head.get_course_text`，函数内 import；
   - docstring 同步。
2. 检查点：
   - 体育 / 兴趣 / 实习课标 `*`；已停课的教室课不标；
   - 按钮不超过每格 31 列。

### 2.6 养成总览的待处理（方案 §3.6）

1. `growth_panel._draw_flag`（`:375~376`）：取 `semester_handle.get_last_report_card`，写「{学期名}的成绩单待查看（用「检查成绩单」指令）」；取不到写「新的成绩单待查看……」
2. 检查点：flag 置着时写的是最新那份成绩单的学期名

### 2.7 `<课>` 悬停（方案 §3.7）

1. `character_info_head.get_now_class_tip`（`:64~67`）：`now_course is None` 时，行为是自习写「自习中（日程安排，此刻没课）」（实施时由「本节没排课」改来，见 §6.1 偏离 1），听课仍写「上课中」
2. 检查点：日程自习写「自习中」；玩家节次外手动授课拉来的学生仍写「上课中」

### 2.8 注释与文档（方案 §3.8）

1. 「不在节次内且 20 分钟内」6 处统一改写：
   - `education_constant.py:305~306`、`constant_promise.py:3745`、`handle_premise_work.py:539`；
   - `target.csv:118`、`:142`：只改 remarks 列，保持原换行符与编码；
   - ArkEditor `Premise.csv:1896`。
2. `game_type.py:1290~1298`：补 `reserved` / `ended`。
3. `growth_handle.py:74`：「课表页签栏」改为「选择学生的名单」。
4. `pregnancy_handle.py:565`：函数内 `from Script.System.Education_System import education_constant`，改用 `STUDENT_WORK_TYPE`。
5. 检查点：
   - `tools/lint_target_csv.py` 通过；
   - `test_talk_data` 的 ArkEditor 表同步断言通过。

### 2.9 测试夹具（方案 §3.9）

1. `_bootstrap.make_character`（`:303~304`）：`stage == 101` 时不加入 `npc_id_got`，注释写明真实婴儿到长成幼女才上线
2. 逐一核对 5 处婴儿夹具：`test_growth.py:164`、`test_prenatal_baby.py:7~8`、`test_premise_tokens.py:206`、`test_growth_event.py:13`。确属新口径的改断言并注明 Plan 28
3. README 的 fixture 陷阱补一条：「婴儿不在 `npc_id_got`，要遍历孩子时别只看它」

### 2.10 测试

| 文件 | 新增 / 改写 |
| --- | --- |
| `test_growth_event` | 婴儿（不在 `npc_id_got`）进派发名单与容量；必派时派得到婴儿；离线的幼女 / 萝莉不进；成年少女不进；抬头「婴儿期第 N 天」 |
| `test_class_ai` | 个人式课上不成（少女的过家家兴趣课、未解锁场所的体育课）：体力低 / 掷中翘课都不派 721 / 714、不记缺课，整链交回娱乐链；幼女照常见学；场所解锁 / 条件恢复后照常 715 |
| `test_schedule` | `judge_personal_course_valid`；`get_course_at` 对上不成的个人式课为 None；实习课无人在岗仍是课；必修覆盖不受影响 |
| `test_settle_effects` | 548：上不成的个人式课 + 日程自习 → 不计出勤 |
| `test_schedule_template` | 候选没有照料卵；残留的照料卵跳过、日程行写明；持卵者的照料卵时段不被覆盖（打桩 `egg_handle`） |
| `test_sex_class` | 选修名单只数学生岗 |
| `test_panels` | 个人课表格子「/条件不符」「/未开放」（不超过格宽）；必修名单的 `*` 与明细（体育课标、已停课不标）；养成总览待处理写学期名；选择活动没有照料卵 |
| `test_premise_tokens` | CVP `CourseType` 对上不成的个人式课不成立；日程自习的 `<课>` 悬停；婴儿夹具波及核对 |
| `test_growth` / `test_prenatal_baby` | 婴儿夹具波及核对（不在 `npc_id_got` 后结论不变） |
| `README.md` | 覆盖描述、断言总数、fixture 陷阱 |

### 2.11 文档与日志

1. `生长养成系统.md`：
   - §1：`growth_event_handle` 一行补「候选含不在 npc_id_got 的婴儿」；`character_info_head` 一行补日程自习的悬停
   - §3：Plan 26 那段个人式课补「这一节上不成视为没课」与格子写法
   - §4：学生表 NONE 行补「个人式课这一节上不成」；第 5 条同步；见学一段补一句
   - §5：出勤一段补「上不成的个人式课不算」
   - §7：照料卵不进候选、改写不覆盖照料卵时段
   - §8：每日派发名单含婴儿（此前一条都派不到）
   - §10：排实操课页的选修人数只数学生岗；必修名单的顶替标记
   - §11：个人课表格子的写法、必修名单、养成总览的待处理
   - §15：新增一条「遍历孩子时别只看 npc_id_got」；第 17 条补「上不成视为没课」
   - §16：测试计数
2. `妊娠系统.md`：照料卵一节补一句「日程模板不排照料卵；日程改写不覆盖当天换上的照料卵时段（Plan 28）」
3. Plan 22 总纲：追加 §14，一行指向本 Plan
4. `update.log`：调用 `update-changelog` skill 登记

## 3. 构建与缓存

```bash
.conda\python.exe tools/lint_target_csv.py             # 改了 target.csv 的备注列
.conda\python.exe tools/tests/education/run_all.py     # 测试引导会 import auto_build_config（增量重建会带上 target.csv）
.conda\python.exe tools/official_event_check.py        # 不动事件表，跑一次确认没被波及
git checkout -- data/po/                               # 本机无 gettext，构建会写乱 PO，一律还原
```

- 不改口上 CSV，不需要删 `data/Character_Talk.json`
- 不涉及地图，不删场景缓存
- 若 `buildconfig.py` 重新生成的 `config_def.py` 与仓库版本差一个空行（Plan 27 §6.1 偏离 7），`git checkout` 还原

## 4. 验证清单

### 4.1 单元测试（实施方执行，按 `headless-game-test` 模式 A）

- [x] §2.0 复现脚本：改前 32 项全部成立；改后 19 项问题命中不再成立，其余 13 项照旧
- [x] `test_talk_data` 通过；`official_event_check.py`、`lint_target_csv.py --fast` 通过（完整模式本机跑了 300 秒没有退出，已中止，见 §6.3）
- [x] §2.10 各文件新增断言通过
- [x] `run_all.py` 全部文件 PASS，断言数记入 §6.3

### 4.2 行为循环（实施方执行，按 `headless-game-test` 模式 B）

- [x] `test_behavior_loop.py` 收敛；上午四节人均出勤 ≥ 3；教师在对的教室授课；实操课到场断言不变

### 4.3 游戏内整体测试（由用户执行）

- [ ] 有婴儿的女儿时，处理公务里会出现婴儿期的养成事件，抬头写「婴儿期第 N 天」
- [ ] 萝莉排了过家家兴趣课、长成少女之后：那一节不再记缺课或翘课，个人课表格子写「/条件不符」
- [ ] 日程模板的「选择活动」里没有照料卵
- [ ] 必修名单里排了体育课的学生名字后有 `*`，下方明细写「→体育课·…」
- [ ] 学期切换后，养成总览的待处理写明是哪个学期的成绩单
- [ ] Tk 与 Web 两种模式下个人课表格子显示正常

## 5. 回滚

| 单元 | 内容 | 回滚方式 | 备注 |
| --- | --- | --- | --- |
| A：婴儿事件 | §2.1、§2.9 | 整体 `git revert` | 回滚后婴儿又派不到事件；已派进队列的婴儿事件照常处理，不受影响 |
| B：个人式课上不成 | §2.2 | `git revert` | 与其他单元无依赖 |
| C：照料卵与小修 | §2.3~§2.8 | 可分别 `git revert` | 注释与数据备注的改动不影响运行 |

- 不涉及存档迁移，改动前后的存档互相兼容
- 回滚 `target.csv` 后跑一次测试（增量构建会带上）；之后还原 `data/po/`

## 6. 实施过程记录

### 6.1 实际改动

实施日期 2026-09-13，全程由主代理完成，改动落点与 §1 清单一致：

| 文件 | 改动 |
| --- | --- |
| `growth_event_handle.py` | `get_growth_event_character_list` 改为遍历 `sorted(cache.character_data)`、跳过 0；入选：阶段在 `STAGE_ALL_CHILD`、`stage == 101 or 在 npc_id_got`、是女儿；docstring 写明婴儿为什么不看 `npc_id_got` |
| `schedule_handle.py` | 新增 `judge_personal_course_valid`（`judge_course_need_pass` 且 `get_course_place` 非空）；`get_course_at` 在班级式分支之后补 `elif not judge_personal_course_valid(...): return None`；`get_now_course` / `get_course_at` 的 docstring |
| `class_ai.py` | `get_course_place_now_or_upcoming` 删掉重复的 need 判定；`get_student_leave_time` 规则 B 删掉重复的 need 判定（保留 `if leave_time is None or not to_place` 的防御）；两处 docstring |
| `course_select_panel.py` | `_get_cell_text`：个人式课先判地点（「/未开放」）、后判 need（「/条件不符」）；docstring |
| `schedule_template_handle.py` | 新增 `judge_activity_schedulable`（函数内 import `pregnancy_constant`）；`get_schedule_activity_candidate` 过滤；`apply_schedule_for_child` 当前槽位是照料卵的不覆盖、不可排的跳过；`get_child_slot_activity_text` 不可排的写「条件不符→自由选择」（排在 need 判定之前）；docstring |
| `sex_class_handle.py` | `get_selected_student_list` 只收学生岗；docstring |
| `class_schedule_panel.py` | `_select_must_attend`：教室课看每周课表那一格非空，个人式课看 `judge_personal_course_valid`，明细「X→课型·目标」复用 `character_info_head.get_course_text`（函数内 import）；docstring |
| `growth_panel.py` | `_draw_flag` 写「{学期名}的成绩单待查看」，取不到最新一份时写「新的成绩单待查看」 |
| `character_info_head.py` | `get_now_class_tip`：此刻没课、行为是自习时写「自习中（日程安排，此刻没课）」 |
| `pregnancy_handle.py` | `_settle_baby_grow_up` 改用 `education_constant.STUDENT_WORK_TYPE`（函数内 import） |
| 注释 | `education_constant` / `constant_promise` / `handle_premise_work` 与 `target.csv` 210810、220830 的备注列、ArkEditor `Premise.csv` 统一为「本节没课（含不在节次内）且20分钟内开始的那一节有课」；`game_type` 的 `temp_sex_class` 补 `reserved` / `ended`；`growth_handle` 的「课表页签栏」改为「选择学生的名单」 |
| `_bootstrap.py` | `make_character` 造的婴儿（`stage=101`）不进 `npc_id_got`；docstring |
| 测试 | 见 §6.3；两条断言按新口径改写：`test_growth.py:166`（旧夹具让婴儿进了 `npc_id_got` 才成立，改为婴儿不在其中、学生岗也不进个人课表名单）、`test_schedule.py:114~115`（非法目标的兴趣课现在视为没课，`get_now_course` 为 None，改为直接构造课程 dict 验解析为空，并补「这一节视为没课」） |
| 文档 | 说明文档 §1 / §3 / §4 / §5 / §7 / §8 / §10 / §11 / §15（第 5、17 条补充，新增第 20 条）/ §16；妊娠系统文档 §5.1 / §8；测试 README（覆盖、计数、fixture 陷阱）；Plan 22 总纲 §14；`update.log` 8 条修正 |

与方案的偏离：
1. `<课>` 悬停的措辞：方案写「自习中（日程安排，本节没排课）」，实施为「自习中（日程安排，此刻没课）」。日程的「上课（无课时自习）」在节次外也会自习 45 分钟（`StateMachine/default.py:2757`），已停课与上不成的个人式课也是「排了但没课」，「本节没排课」对这几种都不准。方案 §3.7 / §5 已同步。
2. 妊娠系统文档照料卵一节顺手订正了旧编号 175（2026-09-09 已改为 152，§5.1 三处与 §8 编号表），方案只要求补一句
3. 其余与方案一致；`character_handle.py`、`egg_handle.py`、`past_day_settle.py`、公务事件表、口上 CSV、`Entertainment.csv` 均未改动，不涉及存档迁移

### 6.2 实施前的假设复核

以下是定案时（2026-09-13，`master @ ef865f8d1`）已经复核过的事实，实施前只需抽查：

| # | 方案中的事实 | 出处 | 复核结果 |
| --- | --- | --- | --- |
| 1 | 婴儿出生不进 `npc_id_got`，长成幼女调 `get_new_character` 上线时才加入 | `character_handle.py:199`；`pregnancy_handle.py:560`；`Settle/default.py:4583~4584` | **成立**（复现：真实出生路径） |
| 2 | 养成事件的派发名单与容量只遍历 `npc_id_got` | `growth_event_handle.py:57`、`:253` | **成立**（复现：必派 30 天一条都派不到婴儿，容量 0） |
| 3 | 婴儿桶 50 条（`sub_key` 101）；通用桶 57 条 `sub_key` 0（其中 17 条带排除婴儿的前提）、4 条 104 | `data/official_event/婴儿.csv`、`通用.csv` | **成立**（读数据） |
| 4 | 真实婴儿身上结算全部可派事件不报错 | 复现脚本的安全检查 | **成立**（60 条、182 个选项、0 报错） |
| 5 | 公务事件的清理、结算只要求主体在 `character_data` 里，不看 `npc_id_got` | `official_event_handle.py:449~486`、`:584~653`；全目录 grep `npc_id_got` 只命中 `ri_value` | **成立**（读代码） |
| 6 | 个人式课上不成时 `get_course_at` 仍返回课，两道闸先于地点判 | `schedule_handle.py:442~464`；`class_ai.py:307~325` | **成立**（复现） |
| 7 | 220805 / 220810 只挂上课状态，不看地点 | `target.csv:137~138` | **成立** |
| 8 | 548 以「查得到课」计出勤 | `Settle/default.py:7681~7684` | **成立**（复现） |
| 9 | 过家家是唯一带 need 的兴趣课 | `Entertainment.csv` 的 `class_ok` 列 | **成立**（读数据） |
| 10 | 照料卵 need「无」、随机池排除、427 无可鉴定卵即孵化 60 分钟、孵化给医疗经验 | `Entertainment.csv:30`；`handle_npc_ai.py:829~831`；`StateMachine/default.py:1730~1733`；`Behavior_Effect.csv:122`；`Experience.csv:90` | **成立**（复现） |
| 11 | 跨天结算里照料卵替换先于日程改写 | `past_day_settle.py:86~91` | **成立**（复现 N5-7） |
| 12 | 选修名单不看岗位；它只有排实操课页一个调用方 | `sex_class_handle.py:406~413`；`class_schedule_panel.py:468` | **成立**（复现 + grep） |
| 13 | 必修覆盖顶掉任何课型 | `schedule_handle.py:436~439` | **成立**（复现 N4-3） |
| 14 | 格子「目标/未开放」「目标/条件不符」最宽 25 列 | 按东亚宽度逐项算过（体育 / 16 项兴趣课 / 全部可实习岗位） | **成立** |
| 15 | `make_character` 让全部非玩家角色进 `npc_id_got` | `_bootstrap.py:303~304` | **成立** |
| 16 | 孩子长成幼女时分到宿舍（714 翘课回宿舍的去处有效） | `character_handle.py:337`；`Dormitory_System/common.py:421~476` | **成立**（读代码，本轮不改） |

### 6.3 单元测试结果

| 文件 | 改前（Plan 27） | 改后 | 变化 |
| --- | --- | --- | --- |
| `test_class_ai` | 236 | 246 | +10：Plan 28 §3.2 一节（两道闸、不提前动身、条件恢复、截短规则 B 与对照、幼女见学与解锁对照） |
| `test_growth` | 74 | 74 | 改写 1 条（婴儿夹具） |
| `test_growth_event` | 41 | 50 | +9：婴儿进名单与容量、必派、离线幼女、婴儿期抬头、真实出生的婴儿逐条结算 |
| `test_panels` | 80 | 91 | +11：格子标注与全部宽度、必修名单四种情形、待处理学期名与兜底、选择活动没有照料卵 |
| `test_premise_tokens` | 118 | 123 | +5：CVP 与学生前提、`<课>` 悬停三种 |
| `test_schedule` | 64 | 71 | +7，改写 1 条（非法目标） |
| `test_schedule_template` | 63 | 68 | +5 |
| `test_settle_effects` | 80 | 82 | +2：548 不计出勤与对照 |
| `test_sex_class` | 88 | 89 | +1 |
| 其余 6 个 | 191 | 191 | 不变 |
| **合计** | **1035** | **1085** | 15 个文件全部通过 |

关键实测：
- 复现脚本（scratchpad `repro_plan28.py`，不入库）：改前 32 项全部成立；改后 PASS=13 / FAIL=19，19 项问题命中全部不再成立（N1-4~6、N2-1~4、N2-6~9、N3-1、N4-1、N4-2、N5-1、N5-2、N5-7、N6-1、N7-1），其余 13 项（前提、对照、N5-4 的状态机机制、N5-5 范围外）照旧成立
- 安全检查：真实出生的婴儿身上 60 条可派事件、182 个选项逐一结算，0 报错（改后复跑同样 0 报错，并已固化进 `test_growth_event`）
- `test_behavior_loop` 18 条通过：收敛、上午四节人均出勤 ≥ 3、教师在对的教室授课、实操课到场断言不变
- `tools/official_event_check.py` 通过（5 个文件、266 条事件）；`tools/lint_target_csv.py --fast` 全部规则通过（180 行，R1~R4、R7、R8）。不带 `--fast` 的完整模式（R5 / R6 要载入游戏配置）本机跑了 300 秒没有退出，已中止；本轮只改了 210810、220830 两行的备注列，前提名与状态机 id 没动，这两行的整链派发也在 `test_class_ai` 里实跑过
- `test_talk_data` 的 ArkEditor 表同步断言通过；构建后一律 `git checkout -- data/po/`

### 6.4 尚未覆盖的验证

- §4.3 游戏内整体测试由用户执行（婴儿期事件在处理公务里出现、少女残留的过家家不再记缺课、选择活动没有照料卵、必修名单的「*」、学期名、Tk / Web 两种模式下的个人课表格子）
- `lint_target_csv.py` 的完整模式（R5 / R6）没有跑完，原因见 §6.3
- Web 模式下个人课表格子的新标注只经适配器冒烟，没有看过真实画面
- 婴儿期事件在真实存档里的派发频率（每人每天 70%、每人 4 条容量、全局硬顶 8 条）没有经过长时间游戏观察

### 6.5 追加调整实施记录

（与方案 §8 成对，每轮一节，附回归测试计数。暂无）
