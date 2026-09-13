# Plan 29（实施步骤与记录）：生长养成系统第十轮复查

> 本文件是 `plan_29_生长养成系统第十轮复查_方案.md`（下文简称"方案"）的**实施步骤清单与过程记录**。
> 需求背景、发现、设计决策、接口定义、风险与范围外事项一律以方案为准；
> 本文件只写"怎么做、怎么验、怎么回滚"，实施过程与结果记入 §6。

- 状态：**已实施**（2026-09-13，记录见 §6；L2 按用户口径特殊处理，见方案 §8-1 与 §6.1 偏离 1）
- 适用代码快照：`master @ e2c386f96`
- 实施前提：先通读方案 §2~§5；实施中发现与方案冲突的事实，**先更新方案再动代码**
- 实施约定：全程由主代理完成，不派子代理；解释器一律用 `.conda\python.exe`
- 提交建议：改动面不大，可以一个提交。若要拆，分成三份：
  - §2.1（体育 / 兴趣课出勤）
  - §2.2（兴趣课读书）
  - §2.3~§2.6（抬头、期末事件、常量、文档），测试随各自的单元，文档随最后一个提交

---

## 1. 改动文件清单

| 文件 | 类型 | 改动 |
| --- | --- | --- |
| `Script/StateMachine/default.py` | 改 | 401 改调 `prepare_npc_read_book`；716 读书先借书，体育 / 兴趣课记出勤 |
| `Script/System/Education_System/growth_handle.py` | 改 | 新增 `settle_course_attend`、`get_stage_day`；`get_stage_progress` 改用 `get_stage_day` |
| `Script/System/Education_System/schedule_handle.py` | 改 | `judge_personal_course_valid` 对兴趣课读书再判借得到书；docstring |
| `Script/UI/Panel/borrow_book_panel.py` | 改 | 新增 `prepare_npc_read_book`、`judge_can_get_read_book` |
| `Script/System/Education_System/growth_event_handle.py` | 改 | 抬头写本阶段第几天（期末事件的推送未收窄，见 §6.1 偏离 1） |
| `Script/System/Education_System/semester_handle.py` / `growth_panel.py` | 改 | 成绩单快照加 `reason`，正文与养成总览写明改岗女儿的成绩单不全的理由（方案 §8-1） |
| `Script/System/Pregnancy_System/pregnancy_handle.py` | 改 | 写死的 151 改用常量 |
| `Script/UI/Panel/manage_basement_panel.py` | 改 | 写死的 152 改用常量 |
| `tools/tests/education/` 下 `test_class_ai` / `test_settle_effects` / `test_schedule` / `test_semester` / `test_growth` / `test_growth_event` / `README.md` | 改 | 见 §2.7 |
| `.github/prompts/数据处理工作流/生长养成系统.md` | 改 | 见 §2.6 |
| `Script/System/Education_System/生长养成系统设计文档.md` | 改 | 索引补 Plan 24~29 |
| `plan/done/plan_22_生长养成系统_总纲.md` | 改 | 追加 §15 一行回指（实施完成后） |
| `update.log` | 改 | 用 `update-changelog` skill 登记 |

**未改动**：
- CSV：`Behavior_Effect.csv`、`Entertainment.csv`、`Book.csv`、事件表、口上一律不动
- `save_handle.py`：不加字段，不需要存档迁移
- `official_event_handle.py`：期末事件的推送与队列都不动（方案 §8-1）
- 游泳换衣链（`target.csv` 310100~330105、状态机 82 / 83 / 88）：方案 §7

## 2. 详细改动步骤

代码的权威定义都在方案 §3~§4，这里只写落点与检查点。

### 2.0 改动前的基线（先做，结果记入 §6.2）

1. 跑 `.conda\python.exe tools/tests/education/run_all.py`，记下各文件断言数（定案时 15 个文件、1085 条）
2. 重建复现脚本（不入库）：
   - 定案时的脚本是 scratchpad 的 `repro_plan29_a/b/c.py`，会话结束即丢；丢了照下表重建
   - 以 `tools/tests/education/_bootstrap.py` 为引导：从 scratchpad 引用时，把 `tools/tests/education` 加进 `sys.path`
   - `official_event_handle` 与 `character_behavior` 不在引导的导出里，要自己 import

   | 组 | 检查 | 改后 |
   | --- | --- | --- |
   | R1 | 学生岗的萝莉女儿，人在图书馆，周一第 1 节排兴趣课读书（101）：<br>0 这一节有课<br>1 716 派 `read_book`<br>2 没借书<br>3 `book_id` 仍为 0<br>4 书名为空<br>5 511 把阅读进度记在 0 号书上<br>6 0 号书是《天灾详解》<br>7 对照：401 借到书并写入 `book_id` | 2~5 不再成立；0、1、6、7 照旧。<br>重建时先把 0 号书标成被别人借走，免得改后随机借到 0 号书、让 5 偶然成立 |
   | R2 | 养成事件抬头：<br>1 出生 300 天的萝莉「萝莉期第 300 天」<br>2 出生 100 天的幼女「幼女期第 100 天」 | 1、2 不再成立（改后为第 31 天、第 11 天） |
   | R3 | 岗位 21 的萝莉女儿，上一份成绩单是无课可评：<br>0 她不是学生岗<br>1 期末桶里 14 / 16 过得了前提<br>2 `push_semester_event_for_list` 给她推了一条<br>3 对照：学生岗的萝莉推一条 | 2 不再成立；0、1、3 照旧 |
   | R4 | 学生岗的萝莉女儿：<br>0 木桩房解析得出<br>1 本节体育课，状态 ATTEND<br>2 716 派课并结算后，出勤不变<br>3 下棋兴趣课同样不变<br>4 体力低判 ABSENT_HP<br>5 721 缺课 +1<br>6 对照：教室课降级自习出勤 +1<br>7 只上体育课、没缺过 → 成绩单无课可评<br>8 缺过一节 → 出勤率 0%、待努力 | 2、3、7、8 不再成立；0、1、4、5、6 照旧。<br>2、3 的出勤快照要取在派 716 **之前**：改后出勤在 716 里记，快照取在 716 之后会把增量漏掉 |

   改前 23 项全部成立（11 项问题命中 + 12 项前提 / 对照 / 数据事实）。
3. `git diff --stat` 记下工作区现状

### 2.1 体育课与兴趣课计出勤（方案 §3.1）

1. `growth_handle.py`：在 `settle_student_class_gain` 之后新增 `settle_course_attend(character_id)`：
   - 守卫照 `sex_class_handle.settle_attend`：只给女儿（`father_id == 0`）或学生岗记；
   - 节次取 `game_time.get_class_period`，不在节次内返回 False；
   - `[行为开始时刻的日期序数, 节次]` 与 `last_attend_period` 相同就返回 False，否则写入并 `attend_class_count += 1`，返回 True；
   - docstring 写明为什么放在 716：被复用的行为全岛共用，不能往效果串里加。
2. `StateMachine/default.py` 716 `character_education_do_course`：
   - 装好行为之后，课型为体育或兴趣时调用 `settle_course_attend`；
   - 实习课不调，552 记；
   - docstring 同步。
3. 检查点：
   - 一节体育 / 兴趣课出勤 +1；
   - 同一节再派 716 不重复；
   - 实习课仍只 +1；
   - 721 的缺课不变；
   - 只上个人式课的孩子成绩单按档评。

### 2.2 兴趣课「读书」先借书（方案 §3.2）

1. `borrow_book_panel.py`：
   - 新增 `judge_can_get_read_book(character_id)`，只读：手上有借着的书即 True；否则扫 `cache.rhodes_island.book_borrow_dict`，有一本没被借走（-1）、`can_read_book`、阅读进度 < 100 的即 True。筛选与 `check_random_borrow_book` 同口径
   - 新增 `prepare_npc_read_book(character_id)`：由 401 抽出。调 `check_random_borrow_book`，借不到返回 False；借到则取 `borrow_book_id_set` 里的书，写 `behavior.book_id / book_name`，返回 True
2. `StateMachine/default.py` 401 `character_entertain_read`：
   - 改调 `prepare_npc_read_book`；
   - 借不到仍等 1 分钟；
   - 其余不变（行为 `READ_BOOK`、时长 30）。
3. `schedule_handle.judge_personal_course_valid`：
   - 兴趣课的行为是读书时，再要求 `judge_can_get_read_book`。判法：`get_behavior_name_by_cid(config_entertainment[target].behavior_id) == Behavior.READ_BOOK`，不写死 101；
   - 函数内 import `borrow_book_panel`（UI 层模块，顶层 import 可能循环，照现有写法延迟）；
   - docstring 同步。
4. 716 兴趣课分支：
   - 行为是读书时先 `prepare_npc_read_book`；
   - 失败就置等待 1 分钟并返回，不记出勤；
   - 成功才装行为与记出勤（接 §2.1）。
5. 检查点：
   - 读书兴趣课借到书，`book_id` 与书名是借到的那本；
   - 手上已有书的不再借；
   - 借不到时 `get_course_at` 为 None，交回娱乐链；
   - 401 的行为与改前一致。

### 2.3 养成事件抬头（方案 §3.3）

1. `growth_handle.get_stage_day(character_id)`：
   - 按阶段取起点：101→0、102→`REARING_COMPLETE_DAY`、103→`GROW_TO_LOLI_DAY`、104→`GROW_TO_GIRL_DAY`；
   - 返回 `max(0, get_child_grow_day − 起点)`，不是孩子返回 0。
2. `get_stage_progress` 改用 `get_stage_day`，数值不变（本阶段天数仍用阈值差）。
3. `growth_event_handle.get_growth_event_title`：写 `get_stage_day + 1`；docstring 与模块头的示例「萝莉期第 38 天」保留。
4. 检查点：
   - 婴儿出生当天为第 1 天；
   - 出生 100 天的幼女为第 11 天；
   - 出生 300 天的萝莉为第 31 天；
   - 少女（毕业典礼）从 450 天起算；
   - 养成数值 3（阶段进度）与改前一致。

### 2.4 期末事件只推学生岗（方案 §3.4）

> 未按此实施：用户拍板改为方案 §8-1 的特殊处理，落点见 §6.1。

1. `push_semester_event_for_list`：阶段为 102 / 103，且 `work.work_type == education_constant.STUDENT_WORK_TYPE`，才推；docstring 同步
2. 检查点：改岗萝莉不推，学生岗照推；`settle_semester_change` 的成绩单不受影响

### 2.5 写死的岗位编号（方案 §3.5）

1. `pregnancy_handle.py:583`：改为 `all_work_npc_set[education_constant.TEACHER_WORK_TYPE]`，同函数已延迟 import `education_constant`
2. `manage_basement_panel.py:1267`：函数内 `from Script.System.Education_System import education_constant`，改用 `STUDENT_WORK_TYPE`
3. 检查点：`test_growth`（长成幼女）、`test_panels` 照过

### 2.6 文档（方案 §3.6）

1. 索引 `生长养成系统设计文档.md`：
   - 表里补 Plan 24~29 一行：师生并入工作链；第六~十轮复查；
   - 首段「plan_22 / plan_23」改成包含后续各轮复查。
2. 说明文档 `生长养成系统.md`：
   - §1：`growth_event_handle` 一行补「抬头写本阶段第几天」
   - §3：兴趣课读书先借书；个人式课上不成的情形补「借不到书」
   - §4：第 5 条同步「借不到书」
   - §5：出勤一段补「体育 / 兴趣课在 716 派出时记一节，同一节只记一次（Plan 29）」
   - §8：抬头写本阶段第几天；期末事件只推学生岗
   - §15：新增一条「复用既有行为的课型要补齐那个行为原本的前置步骤：读书借书已补；游泳换衣未做，见 Plan 29 §7」
   - §16：测试计数
3. Plan 22 总纲：追加 §15，一行指向本 Plan
4. `update.log`：调用 `update-changelog` skill 登记

### 2.7 测试

| 文件 | 新增 / 改写 |
| --- | --- |
| `test_class_ai` | 体育 / 兴趣课派 716 时记一节出勤，同一节再派不重复，实习课不重复记；读书兴趣课借书并写入 `book_id` 与书名；借不到书 → NONE、交回娱乐链；401 的行为对照 |
| `test_settle_effects` | 552 实习课出勤仍只 +1（716 不另记） |
| `test_schedule` | `judge_personal_course_valid`：读书兴趣课借得到 / 借不到 / 手上已有书 |
| `test_semester` | 只排个人式课的孩子按档评，不再是无课可评 |
| `test_growth` | `get_stage_day` 各阶段起点与下限；阶段进度与改前一致 |
| `test_growth_event` | 抬头写本阶段第几天（婴儿 / 幼女 / 萝莉）；改岗萝莉不推期末事件，学生岗照推 |
| `README.md` | 覆盖描述、断言总数 |

## 3. 构建与缓存

```bash
.conda\python.exe tools/tests/education/run_all.py     # 测试引导会 import auto_build_config（增量构建）
.conda\python.exe tools/official_event_check.py        # 不动事件表，跑一次确认没被波及
git checkout -- data/po/                               # 本机无 gettext，构建会写乱 PO，一律还原
```

- 不改 CSV、口上、地图：不需要 `buildconfig.py`，不删 `data/Character_Talk.json` 与场景缓存
- 若增量构建重新生成的 `config_def.py` 与仓库版本差一个空行（Plan 27 §6.1 偏离 7），`git checkout` 还原

## 4. 验证清单

### 4.1 单元测试（实施方执行，按 `headless-game-test` 模式 A）

- [ ] §2.0 复现脚本：改前 23 项全部成立；改后 11 项问题命中不再成立，其余 12 项照旧
- [ ] `test_talk_data`、`tools/official_event_check.py` 通过
- [ ] §2.7 各文件新增断言通过
- [ ] `run_all.py` 全部文件 PASS，断言数记入 §6.3

### 4.2 行为循环（实施方执行，按 `headless-game-test` 模式 B）

- [ ] `test_behavior_loop.py` 收敛；上午四节人均出勤 ≥ 3（该测试以教室课为主，本轮只会更多）；教师在对的教室授课；实操课到场断言不变

### 4.3 游戏内整体测试（由用户执行）

- [ ] 萝莉排一节木桩房体育课，上完后养成总览的本学期出勤 +1
- [ ] 排兴趣课读书：到图书馆后借了一本书（借阅面板可见），读的就是那本
- [ ] 处理公务时，养成事件的抬头写本阶段第几天
- [ ] 把一个萝莉女儿改岗，学期结束时不再收到期末事件，成绩单照出
- [ ] Tk 与 Web 两种模式下无报错

## 5. 回滚

| 单元 | 内容 | 回滚方式 | 备注 |
| --- | --- | --- | --- |
| A：出勤 | §2.1 | `git revert` | 回滚后体育 / 兴趣课又不计出勤；已记的出勤不回收 |
| B：读书 | §2.2 | `git revert` | 已借的书留在孩子手上，照娱乐读书的还书概率归还 |
| C：小修 | §2.3~§2.6 | 可分别 `git revert` | 不影响存档 |

- 不涉及存档迁移，改动前后的存档互相兼容

## 6. 实施过程记录

### 6.1 实际改动

实施日期 2026-09-13，全程由主代理完成：

| 文件 | 改动 |
| --- | --- |
| `growth_handle.py` | 新增 `settle_course_attend`（守卫同 `settle_attend`：女儿或学生岗；节次内按 `last_attend_period` 去重）、`get_stage_start_day`、`get_stage_day`；`get_stage_progress` 改用它们，数值不变 |
| `StateMachine/default.py` | 401 改调 `prepare_npc_read_book`（借不到仍等 1 分钟，行为 / 状态 / 时长 30 不变）；716 兴趣课读书先 `prepare_npc_read_book`（失败置等待 1 分钟并返回、不记出勤），体育 / 兴趣课装好行为后 `settle_course_attend`，实习课不调；docstring |
| `borrow_book_panel.py` | 新增 `judge_can_get_read_book`（只读，筛选与 `check_random_borrow_book` 同口径）、`prepare_npc_read_book`（由 401 抽出） |
| `schedule_handle.py` | `judge_personal_course_valid` 对读书兴趣课再判 `judge_can_get_read_book`（函数内 import UI 层模块）；新增 `judge_interest_course_is_read_book`（按行为名判，不写死 101）；docstring |
| `growth_event_handle.py` | 抬头写 `get_stage_day + 1`；`push_semester_event_for_list` **未改** |
| `semester_handle.py` | 新增 `get_report_incomplete_reason`；`build_report_card` 快照加 `reason` 键；`get_report_card_text` 有理由时在出勤行之后多一行「※ …」 |
| `growth_panel.py` | 历年成绩单有 `reason` 时多画一行（deep_gray） |
| `pregnancy_handle.py` / `manage_basement_panel.py` | 151 / 152 改用 `TEACHER_WORK_TYPE` / `STUDENT_WORK_TYPE`（后者函数内 import） |
| `_bootstrap.py` | 书库全部在架（与 `basement` 初始化一致） |
| 测试 | 见 §6.3 |
| 文档 | 说明文档 §1 / §3 / §4 / §5 / §6 / §8 / §15（新增第 21 条）/ §16；索引文档首段与表（补 Plan 24 与 Plan 25~29 两行）；测试 README；Plan 22 总纲 §15；`update.log` 3 条修正 + 2 条调整 |

与方案的偏离：
1. **L2 按用户指示特殊处理**（方案 §8-1）：不收窄期末事件的推送（§2.4 未实施），改为改岗的女儿照出成绩单、只计改岗前的课，并在成绩单正文与养成总览写明不全的理由。方案 §3.4 / §4.2 / §5 已同步
2. 方案 §4.2 之外多了两个小函数：`get_stage_start_day`（抬头与阶段进度共用起点）、`judge_interest_course_is_read_book`（716 / 判定 / 测试共用）
3. 测试引导把书库置为全部在架：夹具的 `book_borrow_dict` 原为空，改后读书兴趣课会被视为没课，逐项断言过不了；真实游戏 `basement` 初始化就是全部在架
4. 复现脚本（§2.0）未重建：改前 23 项的结论沿用定案时的记录；改后各项由 §6.3 的新断言覆盖（R1 → `test_class_ai` Plan 29 分节与 `test_schedule`；R2 → `test_growth_event`；R3 → `test_growth_event`（按新口径：照推）与 `test_semester`（成绩单带理由）；R4 → `test_class_ai` 个人式课分节与 `test_semester`）
5. 实施工具的陷阱：Bash 工具的 heredoc 会把 `
` 折成真换行，`semester_handle` / `growth_panel` 两处字符串一度被写坏、全套测试在导入期报语法错误并挂到超时；已改用不含反斜杠的写法修复，写进测试 README 的陷阱表

### 6.2 实施前的假设复核

以下是定案时（2026-09-13，`master @ e2c386f96`）已经复核过的事实，实施前只需抽查：

| # | 方案中的事实 | 出处 | 复核结果 |
| --- | --- | --- | --- |
| 1 | 全仓库给 `attend_class_count` 加数的只有 `settle_student_class_gain` 与 `settle_attend` 两处 | grep `attend_class_count +=` | **成立** |
| 2 | 716 对体育 / 兴趣课派的是被复用的行为，其效果串里没有上课结算 | `StateMachine/default.py:2810~2850`；`Behavior_Effect.csv:50`、`:79~80` | **成立**（复现 R4-2、R4-3） |
| 3 | 体力闸不分课型，721 对体育课照记缺课 | `class_ai.py:318~319`；`StateMachine/default.py:2952~2963` | **成立**（复现 R4-4、R4-5） |
| 4 | 实习课由 552 记出勤 | `Settle/default.py:7750~7786` | **成立**（读代码） |
| 5 | `behavior.book_id` 默认 0，`Book.csv` 的 0 号是《天灾详解》 | `game_type.py:1140`；`Book.csv` | **成立**（复现 R1） |
| 6 | 401 先借书再写 `book_id` / 书名，716 两步都没有 | `StateMachine/default.py:1423~1447`、`:2836~2840` | **成立**（复现 R1） |
| 7 | 读书结算按 `behavior.book_id` 取书 | `Settle/default.py:7482~7483` | **成立**（复现 R1-5） |
| 8 | `can_read_book` 只读 | `borrow_book_panel.py:128~` | **成立**（读代码） |
| 9 | 书库 366 本，难度 1 / 2 / 3 各 140 / 97 / 92 本 | `Book.csv` | **成立**（读数据） |
| 10 | 抬头的天数取 `get_child_grow_day`，即出生以来 | `growth_event_handle.py:283` | **成立**（复现 R2） |
| 11 | 期末事件 14 / 16 不看档位，15 只看同胞 | `期末.csv` | **成立**（读数据 + 复现 R3） |
| 12 | 幼女不能改岗，萝莉可以 | `manage_basement_panel.py:1266~1269` | **成立**（读代码） |
| 13 | 可派给婴儿的 68 条事件，每个选项都带 `CVE_A1_Growth`；没有全部选项都带前提的事件 | `婴儿.csv`、`通用.csv` | **成立**（脚本扫描，方案 §2.3） |
| 14 | 教师爆睡时 normal_5 / 6 判不过 | `handle_premise/__init__.py:1126~1173` | **成立**（读代码，方案 §2.3） |
| 15 | 通用指令结算把行为 id 写进 `state` | `handle_instruct.py:372` | **成立**（读代码，方案 §2.3） |

### 6.3 单元测试结果

`run_all.py` 15 个文件全部 PASS，断言 1085 → **1126**（+41），`tools/official_event_check.py` 通过，`data/po/` 已还原：

| 文件 | 改前 | 改后 | 新增断言 |
| --- | --- | --- | --- |
| `test_class_ai` | 246 | 257 | 体育课派 716 即记出勤、同一节不重复；兴趣课逐项 16 种都记出勤且读书写入借到的书；实习课 716 不记；读书先借书 / 手上有书不另借 / 借不到 → NONE 交回娱乐链且不记出勤 / 判定与执行之间被借走则等 1 分钟；401 借书与借不到对照 |
| `test_schedule` | 71 | 81 | `judge_interest_course_is_read_book`；读书课：书库有书 / 全被借走 / 手上有书 / 只剩读完的 / 没读完 / 只剩读不了的 / 能力够了；判定不写数据 |
| `test_semester` | 43 | 53 | `settle_course_attend` 守卫、去重、节次外不记；只排个人式课按档评（良好）、缺一节按实际算（50%）；改岗萝莉成绩单带理由（岗位名 / 岗位为无）、正文有那一行、学期切换冻结、学生岗为空、旧快照无键 |
| `test_growth` | 74 | 80 | 各阶段起点；`get_stage_day` 萝莉 / 幼女 / 婴儿 / 少女 / 成年；低于起点夹 0；阶段进度不变 |
| `test_growth_event` | 50 | 53 | 抬头萝莉 300 天 → 第 31 天、幼女 → 第 31 天、婴儿 5 天 → 第 6 天；改岗萝莉照推期末事件 |
| `test_settle_effects` | 82 | 83 | 552 记的实习课出勤，同一节 `settle_course_attend` 不重复 |
| 其余 9 个文件 | 519 | 519 | 无改动，全部照过（含 `test_behavior_loop` 的收敛与上午出勤 ≥ 3 节、`test_talk_data`、`test_save_compat`） |

### 6.4 尚未覆盖的验证

- §4.3 游戏内整体测试（Tk 与 Web 两种模式）由用户执行
- 改岗萝莉在游戏内的完整链路（基建面板改岗 → 跨天学期结算 → 处理公务看到期末事件 → 检查成绩单看到「※」那一行）只在无头环境验过各段，没有串起来跑
- 兴趣课读书借了书之后的还书（按还书概率）走的是读书系统既有逻辑，本轮没有加断言
- 体育课游泳不换泳衣（方案 §7）未做

### 6.5 追加调整实施记录

（与方案 §8 成对，每轮一节，附回归测试计数。暂无）
