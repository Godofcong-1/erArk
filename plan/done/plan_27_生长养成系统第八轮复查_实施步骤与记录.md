# Plan 27（实施步骤与记录）：生长养成系统第八轮复查

> 本文件是 `plan_27_生长养成系统第八轮复查_方案.md`（下文简称"方案"）的**实施步骤清单与过程记录**。
> 需求背景、发现、设计决策、接口定义、风险与范围外事项一律以方案为准；
> 本文件只写"怎么做、怎么验、怎么回滚"，实施过程与结果记入 §6。

- 状态：**已实施**（2026-09-13，记录见 §6）
- 适用代码快照：`master @ 90e6101e0`
- 实施前提：先通读方案 §2~§5；实施中发现与方案冲突的事实，**先更新方案再动代码**
- 实施约定：全程由主代理完成，不派子代理；解释器一律用 `.conda\python.exe`
- 提交建议：改动面小，可一个提交；若要拆，§2.1~§2.2（场所开放）、§2.3~§2.5（上课与出勤）、§2.6~§2.8（成绩单、睡觉、小修）与测试、文档随最后一个提交

---

## 1. 改动文件清单

| 文件 | 类型 | 改动 |
| --- | --- | --- |
| `Script/System/Education_System/schedule_template_handle.py` | 改 | 新增 `judge_activity_place_open`；`apply_schedule_for_child` 与 `get_child_slot_activity_text` 查场所开放 |
| `Script/System/Education_System/schedule_template_panel.py` | 改 | `_select_activity` 给未开放的活动标「未开放」 |
| `Script/Design/handle_npc_ai.py` | 改 | `get_chara_entertainment` 幼女默认池滤掉场所未开放的 |
| `Script/StateMachine/default.py` | 改 | 561 回落只挑已开放的理论教室 |
| `Script/System/Education_System/schedule_handle.py` | 改 | `get_course_at` 对已停课返回 None |
| `Script/System/Instruct_System/handle_instruct.py` | 改 | `handle_teach` 学生时长截到本节结束 |
| `Script/Settle/default.py` | 改 | 550 按待查看标记选冻结 / 现算 |
| `Script/Core/constant_effect.py`、`tools/ArkEditor/csv/Effect.csv` | 改 | 550 的说明改为「有未查看的新成绩单发那份并清 flag，否则给本学期截至目前」 |
| `Script/System/Education_System/education_constant.py` | 改 | `GROWTH_VALUE_REPORT_PENDING` |
| `Script/System/Education_System/growth_handle.py` | 改 | `get_growth_value` 支持编号 23 |
| `Script/System/Education_System/class_ai.py` | 改 | `judge_student_pullable` 睡觉双判 |
| `Script/System/Education_System/course_select_panel.py` | 改 | 周日实习课不重复提示 |
| `data/talk/daily/check_report_card.csv` | 改 | 12 条分档口上追加待查看前提 |
| `tools/tests/education/` 下 `test_schedule_template` / `test_class_ai` / `test_schedule` / `test_sex_class` / `test_settle_effects` / `test_premise_tokens` / `test_panels` / `README.md` | 改 | 见 §2.9 |
| `.github/prompts/数据处理工作流/生长养成系统.md` | 改 | 见 §2.10 |
| `plan/done/plan_22_生长养成系统_总纲.md` | 改 | 追加 §13 一行回指（实施完成后） |
| `update.log` | 改 | 用 `update-changelog` skill 登记 |

**未改动**：`sex_class_handle.py` 与 `game_type.py`（L2 按设计保留，见方案 §3.4）、存档迁移代码（本轮不加字段）、`target.csv`、`Entertainment.csv`、`Facility_open.csv`、`Behavior_Data.csv` / `Behavior_Effect.csv`、公务事件表、ArkEditor 表（CVP token 不需要注册）。

## 2. 详细改动步骤

代码与数据行的权威定义都在方案 §3~§4，这里只写落点与检查点。

### 2.0 改动前的基线（先做，结果记入 §6.2）

1. 跑 `.conda\python.exe tools/tests/education/run_all.py`，记下各文件断言数（README 记载 15 个文件、993 条）
2. 在 scratchpad 重建复现脚本（不入库），以 `tools/tests/education/_bootstrap.py` 为引导，夹具角色 id 取有服装模板的；最小 fixture 的 `Rhodes_Island` 没有派对表，跑 `get_chara_entertainment` 前要补 `party_day_of_week = {0..6: 0}`：
   - M1：关掉黄澄澄游戏室 → 幼女 20 次每日随机里有过家家；「玩乐优先」照写过家家；19:05 起 40 步行走模拟，末尾连续派 563、每次等待 1 分钟
   - M2：只开理论教室一，萝莉娱乐全为 155、10:00 没课，12 个种子里 561 的目标落在锁着的教室
   - M3：上一份成绩单已看过、学期中途调 550 → 正文是上学期那份（不含「尚未结束」）
   - L1：个人课表选了理论教室一、全局课表那格空着 → ATTEND、派 713、548 后出勤 +1
   - L2：必修预约 → 开课、下课、同一节再开 → 出勤 +2（按设计保留，改后仍应命中）
   - L3：学生在理论教室一自习（本节不排教师）、下一节在理论教室二有课，9:30 调 `handle_teach`（`game_update_flow` 打桩）→ 学生听到 10:15，`get_student_leave_time` 为 None
   - L4：学生行为为睡觉、`sp_flag.sleep` 为假，教师在同教室跑 303 → 学生变成听课
3. `git diff --stat` 记下工作区现状

### 2.1 日程与幼女默认娱乐查场所开放（方案 §3.1）

1. `schedule_template_handle.py`：`judge_activity_need_pass` 之后新增 `judge_activity_place_open`（模块顶部 import `schedule_handle`，确认不成环：`schedule_handle` 只在函数内 import 本模块）
2. `apply_schedule_for_child`（`:314`）：need 校验之后加场所校验，`continue`；docstring 同步
3. `get_child_slot_activity_text`（`:472`）：need 过了、场所未开放时返回「X（未开放→自由选择）」
4. `schedule_template_panel._select_activity`（`:260`）：`draw_activity` 把年龄标注与「未开放」合进同一对括号（「，」分隔），仍可选
5. `handle_npc_ai.get_chara_entertainment`（`:818~821`）：幼女默认池先按 `judge_activity_place_open` 过滤，空了用自由玩耍；函数内 import，照本文件其余教育系统 import 的写法
6. 检查点：游戏室未开放时幼女三个时段全是自由玩耍；开放后恢复二选一；「玩乐优先」上午保留随机值；个人课表日程行写「未开放→自由选择」

### 2.2 自习的去处只挑已开放的理论教室（方案 §3.2）

1. `StateMachine/default.py:471~475`：回落改为 `schedule_handle.get_classroom_list(education_constant.COURSE_TYPE_THEORY)` 里随机，空了才退回原来的全表随机；注释说明为什么
2. 检查点：只开理论教室一时，任意种子下 561 的回落目标都是理论教室一

### 2.3 已停课视为这节没课（方案 §3.3）

1. `schedule_handle.get_course_at`（`:453~458`）：班级式课取到的格子为 None 时返回 None；docstring 写明「已停课视为没课」与必修覆盖、预约不受影响的理由
2. 跑一遍 `run_all.py`，逐条处理因此变化的断言：夹具是「只排个人课表、不排全局课表」的，补排全局课表格子；确属新口径的，改断言并注明 Plan 27
3. 检查点：已停课 → `get_now_course` 为 None、`get_course_stage` 为 NONE、派发落到见学 / 娱乐；必修生被点名到一间每周课表空着的实践教室，当天照样 JOIN；预约在空教室的实操课选修生照样 SEX_PENDING

### 2.4 实操课出勤（方案 §3.4：L2 按设计保留）

1. 不改 `sex_class_handle` / `game_type` / 722
2. `test_sex_class` 加一条锁定断言：同一节开课 → 下课 → 再开，到场学生出勤 +2
3. 说明文档 §10 写明「每次开课单独记一次出勤，按设计」

### 2.5 玩家授课的学生截到本节下课（方案 §3.5）

1. `handle_instruct.handle_teach`（`:574~577`）：先对齐 `start_time`，再 `duration = schedule_handle.get_period_left_minute(chara_id)`；函数内 import `schedule_handle`
2. 检查点：9:30 授课 → 学生时长 15；午休 12:30 授课 → 学生 45；玩家自己的时长仍是 45

### 2.6 检查成绩单（方案 §3.6）

1. `education_constant.py` 第 12 组末尾加 `GROWTH_VALUE_REPORT_PENDING = 23`
2. `growth_handle.get_growth_value`：有养成数据时编号 23 返回 `1.0 if report_card_flag else 0.0`（没有养成数据时走既有的 0.0）
3. `Settle/default.py:7873~7876`：`finished = growth_data.report_card_flag and bool(report_data)`，不成立就 `build_report_card`；注释改写（原注释「学期已经结束就发冻结的那一份」的判据不对）
4. `check_report_card.csv`：12 条分档口上追加 `&CVP_A2_Growth|23_E_1`（方案 §4.3）。脚本按 UTF-8 读写、保持原换行符、只改前提列并断言每条都只改一次
5. 删 `data/Character_Talk.json`，跑 `.conda\python.exe buildconfig.py`，`git checkout -- data/po/`
6. 检查点：有新成绩单 → 正文是冻结的那份、分档口上成立、标记清掉；再查 → 正文含「尚未结束」、分档口上都不成立、通用口上成立、标记不动；第一份成绩单出来之前与现状相同

### 2.7 学生睡着的判定同时看行为（方案 §3.7）

1. `class_ai.judge_student_pullable`（`:448`）：`or character_data.behavior.behavior_id == constant.Behavior.SLEEP`；docstring 补一句来源（状态机 44 不置标记）
2. 检查点：爆睡的学生不被 303 拉、不被 `handle_teach` 拉、授课指令的前提不因她成立；醒着的照旧被拉

### 2.8 小修（方案 §3.8）

1. L5：`course_select_panel._select_target`（`:534~539`）周日分支画完提示后置 `empty_flag = False`
2. L6：说明文档 §1 挂接表「18 个师生前提」改为 19 个

### 2.9 测试

| 文件 | 新增 / 改写 |
| --- | --- |
| `test_schedule_template` | `judge_activity_place_open`；`apply_schedule_for_child` 跳过未开放场所；日程文本「未开放→自由选择」；幼女默认池（补派对表夹具）只剩自由玩耍、开放后二选一 |
| `test_class_ai` | 561 回落只挑已开放的理论教室（定种子）；已停课 → NONE 且派发不落 713；必修覆盖到空格子的实践教室仍 JOIN；爆睡学生不被 303 拉；因 §2.3 变化的夹具补排格子 |
| `test_schedule` | `get_course_at` 对已停课为 None、对当天有临时课覆盖的空格子非 None |
| `test_sex_class` | 同一节下课后重开：到场学生再记一节（L2 按设计保留，锁定断言） |
| `test_settle_effects` | 550 三种情形（新成绩单 / 看过之后 / 从未有过）的正文与标记；`handle_teach` 学生时长（节次内 / 节次外）与爆睡学生不被拉；因 §2.3 变化的夹具补排格子 |
| `test_premise_tokens` | CVP `Growth\|23` 读数；因 §2.3 变化的 `CourseType` / `Course` 夹具补排格子 |
| `test_panels` | 选择活动面板的「未开放」标注；周日实习课只画一句提示 |
| `README.md` | 覆盖描述与断言总数 |

### 2.10 文档与日志

1. `生长养成系统.md`：
   - §1：挂接表 18 → 19；`handle_npc_ai` 一行补幼女默认池查场所
   - §2：`report_card_flag` 一行补养成数值 23 的读口
   - §3：个人课表指向已停课的格子视为没课；玩家授课拉来的学生截到本节下课
   - §4：第 5 条补「全局课表那格空着即没课」；拉人口径补睡觉双判；561 回落只挑已开放的理论教室
   - §5：出勤一段补「已停课不算」
   - §6：检查成绩单的取法（待查看 → 冻结，否则截至目前）与分档口上的新前提
   - §7：日程改写与幼女默认池查场所开放，面板标注
   - §10：每次开课单独记一次出勤（按设计，L2）
   - §12：养成数值编号补 23
   - §13：检查成绩单的 12 条分档口上带待查看前提
   - §15：新增一条「给孩子派活动的地方都要查场所开放」；第 2 条补「格子空着即停课」
   - §16：测试计数
2. Plan 22 总纲：追加 §13，一行指向本 Plan
3. `update.log`：调用 `update-changelog` skill 登记

## 3. 构建与缓存

```bash
del data\Character_Talk.json                           # 口上改了，增量构建会跳过口上
.conda\python.exe buildconfig.py                       # 全量重建
git checkout -- data/po/                               # 本机无 gettext，构建会写乱 PO，一律还原
.conda\python.exe tools/tests/education/run_all.py     # 测试引导会 import auto_build_config
.conda\python.exe tools/official_event_check.py        # 不动事件表，跑一次确认没被波及
git checkout -- data/po/
```

- 不动 `target.csv`，不需要跑 `lint_target_csv.py`
- 不涉及地图，不删场景缓存

## 4. 验证清单

### 4.1 单元测试（实施方执行，按 `headless-game-test` 模式 A）

- [x] §2.0 复现脚本：改前 9 项全部命中、改后除 L2（按设计保留）外全部不命中（N1 第三项是空转机制本身，改后仍命中属预期，见 §6.1 偏离 4）
- [x] `test_talk_data` 通过（口上前提逐条校验）；`official_event_check.py` 通过
- [x] §2.9 各文件新增断言通过
- [x] `run_all.py` 全部文件 PASS，断言数记入 §6.3

### 4.2 行为循环（实施方执行，按 `headless-game-test` 模式 B）

- [x] `test_behavior_loop.py` 收敛；上午四节人均出勤 ≥ 3；教师在对的教室授课；实操课到场断言不变

### 4.3 游戏内整体测试（由用户执行）

- [ ] 教育区 1 级时，幼女晚上不会再站在黄澄澄游戏室门口；教育区升到 2 级后会去玩过家家
- [ ] 日程模板选活动时，没解锁的场所的活动带「未开放」；孩子的日程行写「未开放→自由选择」
- [ ] 只开了理论教室一时，排了「上课（无课时自习）」的学生都去理论教室一
- [ ] 把全局课表某格清空后，个人课表显示「已停课」的学生那一节自由活动，成绩单不多一节出勤
- [ ] 9 点半在理论教室手动授课，学生 9 点 45 分走去下一节
- [ ] 刚出成绩单时检查：给新成绩单、口上按档位；再查一次：写着「本学期尚未结束」、口上是通用的
- [ ] Tk 与 Web 两种模式下日程面板显示正常

## 5. 回滚

| 单元 | 内容 | 回滚方式 | 备注 |
| --- | --- | --- | --- |
| A：场所开放 | §2.1、§2.2 | 整体 `git revert` | 与其他单元无依赖 |
| B：上课与出勤 | §2.3、§2.5 | 可分别 `git revert` | §2.4 未改代码（L2 按设计保留），只有测试与文档 |
| C：成绩单、睡觉、小修 | §2.6~§2.8 | 可分别 `git revert` | §2.6 回滚时口上 CSV 与代码一起回，并删 `Character_Talk.json` 重建 |

- 不涉及存档迁移，改动前后的存档互相兼容
- 回滚 CSV 后删 `Character_Talk.json` 跑一次 `buildconfig.py`；之后还原 `data/po/`

## 6. 实施过程记录

### 6.1 实际改动

| 文件 | 改动 |
| --- | --- |
| `schedule_template_handle.py` | 新增 `judge_activity_place_open`（模块顶部 import `schedule_handle`，不成环）；`apply_schedule_for_child` 在 need 之后查地点，未开放的时段跳过；`get_child_slot_activity_text` 写「未开放→自由选择」（need 不符优先） |
| `schedule_template_panel.py` | `_select_activity` 给地点未开放的活动标「未开放」，与年龄标注同一对括号，仍可选 |
| `handle_npc_ai.py` | `get_chara_entertainment` 幼女默认池按 `judge_activity_place_open` 过滤，滤空退回自由玩耍 |
| `StateMachine/default.py` | 561 回落先在 `get_classroom_list(理论)` 里随机，空了才退回全表 |
| `schedule_handle.py` | `get_course_at` 对班级式课的空格子返回 None；`get_now_course` / `get_course_at` 的 docstring |
| `handle_instruct.py` | `handle_teach` 学生时长 = `get_period_left_minute`（对齐开始时刻之后取） |
| `Settle/default.py` | 550：`finished = report_card_flag and 有成绩单`；「更早的 N 个学期」按发的是哪份算（偏离 3） |
| `education_constant.py` / `growth_handle.py` | `GROWTH_VALUE_REPORT_PENDING = 23` 与读口 |
| `class_ai.py` | `judge_student_pullable` 睡觉双判 |
| `course_select_panel.py` | 周日实习课画完提示置 `empty_flag = False` |
| `constant_effect.py`、ArkEditor `Effect.csv` | 550 的说明（偏离 2） |
| `data/talk/daily/check_report_card.csv` | 12 条分档口上追加 `&CVP_A2_Growth|23_E_1`（脚本改：逐条断言只改一次、CRLF 不变；重建后 `Character_Talk.json` 里正好 12 处） |
| 测试 7 个 + README | 见 §6.3 |
| 文档 | 说明文档 §1~§7、§10、§12、§13、§15（新增第 19 条）、§16；Plan 22 总纲 §13；`update.log` 修正 7 条（skill 自检通过） |

与方案的偏离：

1. **L2 按设计保留**（实施前用户拍板）：不改 `sex_class_handle` / `game_type` / 722，方案 §3.4、§4 已同步改写；`test_sex_class` 加一条锁定断言，说明文档 §10 写明
2. **550 的效果说明**同步改了 `constant_effect.py` 与 ArkEditor `Effect.csv`（方案初稿的文件表没列）
3. **检查成绩单的「更早的 N 个学期」提示**：学期中途也给截至目前之后，历史里的每一份都比本学期早，原来的「历史数 − 1」只在发冻结那一份时对（只有一份历史时提示整个不出）；改为发冻结那份时「历史数 − 1」、给截至目前时「历史数」，方案 §3.6 已补一句
4. **复现脚本 N1 第三项改后仍命中**：它把过家家直接写进槽位去跑行走模拟，验证的是寻路在门口 wait_open 的空转机制本身；方案 §3.1 修在派活动的两处源头、明确不在 563 里挡，这一项命中属预期。其余 BUG 项（N1 前两项、N2、N3、N5、N6、N7）改后都不再命中，N4（L2）按设计仍命中
5. **测试夹具波及**（§2.3 预期内）：`test_class_ai` 两条见学用例、`test_schedule`「教室课地点」、`test_settle_effects`「玩家手动授课计出勤」只排了个人课表，补排全局课表格子；`test_schedule` 原「教室课被清掉后科目 / 教师为 -1」按新口径拆成两条（格子在、教师 -1 仍是课；清掉即 None）
6. **`test_schedule_template` 的循环变量**：原有的 `for _ in range(100)` 把翻译函数 `_` 覆盖成了 int，之前后面没再调 `_()` 所以没暴露；新分节一调就崩，改名 `_i`，README 的 fixture 陷阱补了一条
7. **构建副作用**：`buildconfig.py` 重新生成的 `config_def.py` 比仓库里的少一个空行（生成器与仓库版本历来不一致，与本轮无关），已 `git checkout` 还原；PO 照例还原

已知限制：

- 读档当天已经写进槽位的过家家（更新前的存档）要到次日娱乐刷新才换掉；设施只会解锁不会关闭，之后不会再出现
- 成年干员的随机娱乐仍用它自己那段场所判定（方案 §7）

### 6.2 实施前的假设复核

以下是定案时（2026-09-13，`master @ 90e6101e0`）已经复核过的事实，实施前只需抽查：

| # | 方案中的事实 | 出处 | 复核结果 |
| --- | --- | --- | --- |
| 1 | 开局全部设施 1 级、`facility_open` 全关，按区块等级逐个开放；黄澄澄游戏室要教育区 2 级（`zone_cid` 152），理论教室二~六要 2~5 级 | `basement.py:33~40`、`:136~146`；`Facility_open.csv:22`、`:24~30` | **成立**（读代码） |
| 2 | 幼女的每日随机娱乐不查场所开放，成年分支查 | `handle_npc_ai.py:818~821`、`:842~848` | **成立**（复现：20 个种子里抽到过家家） |
| 3 | 日程改写只校验 need，不看场所 | `schedule_template_handle.py:334~343` | **成立**（复现：「玩乐优先」照写过家家） |
| 4 | 走到锁着的场所门口，寻路返回 `wait_open`、移动时长 0，通用移动模块等待 1 分钟 | `character_move.py:118~141`；`StateMachine/default.py:59~64` | **成立**（复现：行走模拟末尾连续派 563、每次等待 1 分钟） |
| 5 | 娱乐 155 的自动移动是 561，561 回落在全部 6 间理论教室里随机 | `Entertainment.csv:33`；`StateMachine/default.py:471~475` | **成立**（复现） |
| 6 | `get_course_at` 对全局课表空格子仍返回一条课，548 按它记出勤 | `schedule_handle.py:442~459`；`Settle/default.py:7681~7684` | **成立**（复现） |
| 7 | `settle_attend` 不去重；重开时预约条目被复用、当场课被新建 | `sex_class_handle.py:220~239`、`:760~781`、`:830~845` | **成立**（复现：出勤 +2）；用户拍板按设计保留，不改 |
| 8 | 玩家授课给学生写死 45 分钟；截短规则 B 在离开时刻本节有课时不截 | `handle_instruct.py:576`；`class_ai.py:546~556` | **成立**（复现） |
| 9 | 550 以「有历史」判冻结；口上先于效果输出 | `Settle/default.py:7873~7876`；`settle_behavior.py:414~428` | **成立**（复现 + 读代码） |
| 10 | 分档口上 12 条读 `CVP_A2_Growth\|7`，1004 / 1005 只有女儿前提 | `check_report_card.csv` cid 1000~1013 | **成立**（读数据） |
| 11 | 养成数值编号 0~22 已用，23 空闲 | `education_constant.py:391~423` | **成立** |
| 12 | 状态机 44 不置 `sp_flag.sleep`，只有 78 与睡觉效果置 | `StateMachine/default.py:2538`；`Settle/default.py:4883`；全仓库 grep | **成立**（复现：303 拉起爆睡的学生） |
| 13 | 教师侧已被 normal_5 / 6 挡住：行为是睡觉时这两个前提不成立 | `handle_premise/__init__.py:1126~1167`；`class_ai.py:102~105` | **成立**（读代码，本轮不改） |
| 14 | `CHILD_GROWTH` 新字段读档时按属性表回填 | `save_handle.py:396~401` | **成立**（读代码） |
| 15 | `Character_Talk.json` 等生成物不入库，增量构建见它存在就跳过口上 | `git ls-files`；`auto_build_config.py:24` | **成立** |

### 6.3 单元测试结果

- 基线（改前，`master @ 90e6101e0`）：15 个文件、993 条断言全绿；复现脚本 9 项全部命中（PASS=9）
- 改后：15 个文件、**1035 条断言全绿**（+42）。改完第一遍跑出 3 个文件 4 处失败，都是测试侧的问题（§6.1 偏离 5、6），修完复跑全绿；550 的翻看提示（偏离 3）补上后又全量复跑一遍

| 文件 | 改前 | 改后 | 新增 / 改写 |
| --- | --- | --- | --- |
| `test_class_ai` | 224 | 236 | 已停课视为没课 7 条（NONE、交回娱乐链不记出勤、不为它提前动身、格子在教师 -1 仍 ATTEND、必修覆盖到空格子、预约在空格子上 SEX_PENDING 与开课时 ATTEND）、561 回落 2 条、爆睡不被 303 拉 3 条；两条见学用例补排全局课表格子 |
| `test_schedule` | 60 | 64 | 「教室课被清掉后科目 / 教师为 -1」拆成「格子在、教师 -1 仍是课」与「清掉即 None」；已停课与覆盖层 3 条；「教室课地点」补排格子 |
| `test_schedule_template` | 57 | 63 | 地点开放判定、日程改写退回、「未开放→自由选择」文本（need 不符优先）、默认池没解锁 / 解锁后各一条、解锁后照写；循环变量 `_` 改名 `_i` |
| `test_settle_effects` | 70 | 80 | 550 七条（看过之后给截至目前、两种情形的翻看提示、养成数值 23 的 0 / 1 / 无养成数据、发冻结那份清待查看）、`handle_teach` 三条（9:30 学生 15 分钟且玩家 45、爆睡不拉、12:30 学生 45）；「玩家手动授课计出勤」补排格子 |
| `test_premise_tokens` | 115 | 118 | `Growth|23` 两条、授课指令的前提对爆睡的学生不成立 |
| `test_panels` | 74 | 80 | 选择活动的「未开放」标注（取消、带标注仍是按钮、不超过 31 列、开放的不带、解锁后不标）、周日实习课只画一句提示 |
| `test_sex_class` | 87 | 88 | 同一节下课后重开再记一节（L2 按设计保留，锁定断言） |
| 其余 8 个 | 306 | 306 | 未改（`test_auto_schedule` 25、`test_behavior_loop` 18、`test_growth` 74、`test_growth_event` 41、`test_prenatal_baby` 36、`test_save_compat` 12、`test_semester` 43、`test_talk_data` 57） |

关键实测值：

- 复现脚本改后 PASS=2 FAIL=7：仍命中的是 N1 第三项（空转机制本身，偏离 4）与 N4（L2 按设计保留）；N3 改后为「上课状态 NONE、派发落到娱乐链、出勤不变」，N5 改后学生听到 9:45
- 9:30 玩家授课：学生时长 15、玩家 45；12:30 授课：学生 45
- 只开理论教室一时，12 个种子下 561 的回落全是理论教室一；全开时落在多间已开放的理论教室
- 重建后 `Character_Talk.json` 里 `Growth|23_E_1` 正好 12 处；`test_talk_data` 的前提 token 逐条校验与 `official_event_check` 通过
- `test_behavior_loop` 收敛（18 条），上午四节人均出勤 ≥ 3、教师在课表上那间教室授课、实操课到场断言照过

### 6.4 尚未覆盖的验证

- §4.3 的 7 条游戏内检查由用户执行，本轮都没在游戏里跑过
- 无头环境看不到 Tk / Web 下选择活动面板的实际排版：「[过家家（限幼女/萝莉，未开放）]」按 `text_handle.get_text_index` 核算正好 31 列、测试断言了不超过每格宽度，真机上的对齐仍要看一眼

### 6.5 追加调整实施记录

（与方案 §8 成对，每轮一节，附回归测试计数。暂无）
