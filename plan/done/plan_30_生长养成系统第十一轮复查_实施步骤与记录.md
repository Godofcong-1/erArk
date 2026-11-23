# Plan 30（实施步骤与记录）：生长养成系统第十一轮复查

> 本文件是 `plan_30_生长养成系统第十一轮复查_方案.md`（下文简称"方案"）的**实施步骤清单与过程记录**。
> 需求背景、发现、设计决策、接口定义、风险与范围外事项一律以方案为准；
> 本文件只写"怎么做、怎么验、怎么回滚"，实施过程与结果记入 §6。

- 状态：**已实施**（2026-09-13；用户确认口径 1~5 按推荐，Q1 按推荐并追加「检查成绩单」的对象限制，见方案 §3.3；全套回归 15 个文件 1206 条断言全绿）
- 适用代码快照：`master @ 90716619b`
- 实施前提：先通读方案 §2~§5；实施中发现与方案冲突的事实，**先更新方案再动代码**
- 实施约定：全程由主代理完成，不派子代理；解释器一律用 `.conda\python.exe`
- 提交建议：可以一个提交。若要拆，分成三份：
  - §2.1 + §2.5（翘课记缺课、被抓后当天不再翘）
  - §2.2 + §2.3（期末事件、成绩单理由与 Q1）
  - §2.4 + §2.6 + §2.7 + §2.8（同一节只落一种记录、有课 / 同学、必修标记、文档），测试随各自的单元

---

## 1. 改动文件清单

| 文件 | 类型 | 改动 |
| --- | --- | --- |
| `Script/Core/game_type.py` | 改 | `CHILD_GROWTH` 加 `skip_count`、`skip_caught_day`、`semester_base_work_type`；`absent_count` 注释 |
| `Script/System/Education_System/education_constant.py` | 改 | 第 12 组加 `GROWTH_VALUE_SKIP = 24` |
| `Script/System/Education_System/class_ai.py` | 改 | `settle_absent(character_id, by_skip=False) -> bool`；`roll_skip_class` 看被抓当天 |
| `Script/System/Education_System/growth_handle.py` | 改 | 新增 `judge_absent_this_period`、`judge_selected_cell_real`；`settle_student_class_gain` / `settle_course_attend` 本节已缺课不计出勤；`get_growth_value` 读编号 24 |
| `Script/System/Education_System/semester_handle.py` | 改 | `reset_semester_baseline` 记岗位；`get_report_incomplete_reason` 分情形；`settle_semester_change` 的 Q1 |
| `Script/System/Education_System/schedule_handle.py` | 改 | 新增 `judge_personal_course_real`；`judge_personal_course_valid` 改用它 |
| `Script/System/Education_System/growth_event_handle.py` | 改 | `get_classmate_list` 双方同一格都是真课 |
| `Script/System/Education_System/sex_class_handle.py` | 改 | `settle_attend(student_id, now_time=None)` 本节已缺课不计 |
| `Script/System/Education_System/class_schedule_panel.py` | 改 | `_select_must_attend` 改用 `judge_personal_course_real` |
| `Script/StateMachine/default.py` | 改 | 714 派出翘课行为时记一节缺课 |
| `Script/Settle/Second_effect.py` | 改 | 623 写 `skip_caught_day` |
| `Script/Design/handle_premise/handle_premise_other.py` | 改 | `handle_self_have_any_course` 改用 `judge_selected_cell_real` |
| `data/official_event/期末.csv` | 改 | cid 9 / 10 前提去掉 `CVP_A1_Growth\|6_L_70` |
| `data/official_event/萝莉.csv` | 改 | cid 2 前提改为 `CVP_A1_Growth\|24_GE_3` |
| `tools/official_event_check.py` | 改 | 期末桶的前提禁用养成数值 4 / 5 / 6 |
| `tools/tests/education/` 下 `test_class_ai` / `test_settle_effects` / `test_semester` / `test_growth` / `test_growth_event` / `test_premise_tokens` / `test_panels` / `test_sex_class` / `test_save_compat` / `README.md` | 改 | 见 §2.9 |
| `.github/prompts/数据处理工作流/生长养成系统.md` | 改 | 见 §2.8 |
| `Script/System/Education_System/生长养成系统设计文档.md` | 改 | 索引补第十一轮 |
| `plan/done/plan_22_生长养成系统_总纲.md` | 改 | 追加 §16 一行回指（实施完成后） |
| `update.log` | 改 | 用 `update-changelog` skill 登记 |

**未改动**：
- `save_handle.py`：三个新字段靠 `CHILD_GROWTH` 属性表整体回填，不需要迁移
- `past_day_settle.py`：学期结算与期末事件的推送顺序不动（方案 §3.2）；Q1 收窄在 `settle_semester_change` 里，学期结束提示自然不再列她
- 口上 CSV、`target.csv`、地图：不动

## 2. 详细改动步骤

代码的权威定义都在方案 §3~§4，这里只写落点与检查点。

### 2.0 改动前的基线（先做，结果记入 §6.2）

1. 跑 `.conda\python.exe tools/tests/education/run_all.py`，记下各文件断言数（定案时 15 个文件、1126 条）
2. 重建复现脚本（不入库）：
   - 定案时的脚本是 scratchpad 的 `p30/repro_plan30.py` 与 `p30/repro_plan30_b.py`，会话结束即丢；丢了照下表重建
   - 以 `tools/tests/education/_bootstrap.py` 为引导：从 scratchpad 引用时，把 `tools/tests/education` 加进 `sys.path`
   - 派发工具 `prepare_ai` / `dispatch` 照抄 `test_class_ai.py:23~68`；`official_event_handle`、`realtime_settle`、`Second_effect`、`constant_effect` 要自己 import
   - 夹具的体力上限默认 100，R3 要改成真实量级（上限 2000）

   | 组 | 检查 | 改后 |
   | --- | --- | --- |
   | R1 | 成年女儿（阶段 104、岗位 21）、萝莉甲、萝莉乙：<br>0 9 月学期第一次记账，三人都立了基线<br>1 12 月切学期：成年女儿理由写「本学期改任了」<br>2 她的成绩单 0/0、无课可评<br>3 对照：萝莉乙 12 月学期上了 2 节后改岗，3 月切学期理由「本学期改任了」<br>4 萝莉乙 6 月切学期（整学期在岗位 21）仍写「本学期改任了」 | 1、4 不再成立（改为「本学期担任…，没有上课」）；0、3 照旧；2 随 Q1：按推荐她不再出成绩单（不再成立），按备选照旧 |
   | R2 | 萝莉甲周一第 1~3 节排体育课（木桩房），心情闸必中：<br>0 派 714<br>1 549 置 flag<br>2 翘一节缺课不变<br>3 第 2、3 节照翘，缺课仍不变<br>4 再上 1 节：本学期 1 / 0、出勤率 100%、良好<br>5 萝莉 2 的前提是 `Growth\|1_GE_3`<br>6 翘过 3 节的萝莉甲过不了萝莉 2<br>7 只因体力缺过 3 节的萝莉乙过得了 | 2~7 不再成立（每节缺课 +1；1 / 3、25%、待努力；前提改判翘课数；翘 3 节的过得了、只体力缺课的过不了）；0、1 照旧 |
   | R3 | 萝莉乙周一第 1 节体育课，人在木桩房，体力 560 / 2000（28%）：<br>0 派 721，缺课 +1<br>1 原地休息 30 分钟（`realtime_settle.settle_rest(202, 30)`）后 704 / 2000，回到 30% 以上<br>2 同一节 9:30 派 716，出勤 +1<br>3 这一节两边都记了 | 2、3 不再成立（716 照派、出勤不变）；0、1 照旧 |
   | R4 | 萝莉甲四项负面状态各 600（每项 2 级）：<br>0 翘课概率 25%<br>1 置 flag 后跑 623，flag 清掉<br>2 被抓后概率不降<br>3 找一天：第 1 节掷中翘课，被抓后同一天第 2~9 节里还有掷中的（定种子，几天内必能找到） | 3 不再成立（被抓当天的后续节次掷不中）；0~2 照旧 |
   | R5 | 萝莉甲、萝莉乙同一格排体育课，萝莉乙改岗 21：<br>0 课表残留<br>1 她的上课状态恒为 NONE<br>2 `self_have_any_course` 对她成立<br>3 萝莉甲的同学里有她<br>4 她自己也有同学<br>5 她的候选事件里有上课 / 同学事件（定案时 24 条）<br>6 对照：改回学生岗两者照常成立 | 2~5 不再成立；0、1、6 照旧 |
   | R6 | 读书兴趣课这一格：<br>0 书库有书时 `judge_personal_course_valid` 成立<br>1 借空后不成立 | 两项照旧（这个判定仍含借书）；必修名单的「*」改用 real 后借空照标，由 `test_panels` 断言 |
   | R7 | 萝莉甲 9 月学期 4 / 6：<br>0 本学期 4 / 6<br>1 12 月切学期：冻结的成绩单待努力、40%<br>2 推送时编号 6 读出 100<br>3 期末 9 判不过<br>4 期末 10 判不过<br>5 期末候选里没有 9 / 10（定案时为 11 / 13 / 14 / 16）<br>6 对照：只留 `7_E_2` 过得了 | 3~5 不再成立；0~2、6 照旧 |
   | R8 | 被抓前后的翘课概率：四项各 600 → 0.25 不变；各 1000 → 0.45 不变 | 照旧（数据事实） |

   改前 39 项全部成立：18 项问题命中，20 项前提 / 对照 / 数据事实，另 1 项（R1-2）随 Q1。
3. `git diff --stat` 记下工作区现状

### 2.1 翘课记缺课（方案 §3.1）

1. `game_type.CHILD_GROWTH`：加 `skip_count`（方案 §4.1）；`absent_count` 注释改为含翘课
2. `class_ai.settle_absent(character_id, by_skip=False) -> bool`：
   - 去重照旧（`last_absent_period`）；
   - 记上了才 `absent_count += 1`，`by_skip` 为真时再 `skip_count += 1`；
   - 返回是否记上；docstring 写明体力缺课与翘课共用这一节的标记。
3. `StateMachine/default.py` 714 `character_education_skip_class`：
   - 在「人已不在教室」那一支、置 `SKIP_CLASS` 行为之前调 `class_ai.settle_absent(character_id, by_skip=True)`；
   - 还在教室、先离开的那一步不记；
   - docstring：记缺课放在状态机里，理由同 721（前提不能有副作用）。
4. `education_constant` 第 12 组末尾加 `GROWTH_VALUE_SKIP`；`growth_handle.get_growth_value` 读 `skip_count`（没有养成数据时走提前返回的 0）
5. `萝莉.csv` cid 2 前提改为 `CVP_A1_Growth|24_GE_3`
6. 检查点：
   - 翘一节：缺课 +1、翘课数 +1；
   - 同一节先体力缺课、再掷中翘课：只记一次，翘课数不加；
   - flag 保持的后续节次各记一节；
   - 成绩单出勤率含翘课；萝莉 2 按翘课数。

### 2.2 期末 9 / 10 与校验工具（方案 §3.2）

1. `期末.csv` cid 9 / 10：前提去掉 `&CVP_A1_Growth|6_L_70`（方案 §4.3）
2. `tools/official_event_check.py`：
   - 常量加 `SEMESTER_SUB_KEY = 200` 与 `SEMESTER_VALUE_ID = {4, 5, 6}`，各带 docstring；
   - `check_row` 里，教育区（15）且 `sub_key` 为 200 的行，主前提与四个选项前提里出现 `CVP_A[12]_Growth|4_` / `5_` / `6_` 就报错；
   - 报错文案：「期末事件在学期基线重置之后推送，养成数值 4 / 5 / 6 读的是新学期；看刚结束的学期用编号 7 / 8」。
3. 检查点：
   - 待努力的萝莉，期末候选里有 9 与 10；幼女有 9、没有 10（10 限萝莉）；
   - 工具对写回 `6_L_70` 的行报错（测试里对一行构造数据调 `check_row`，或临时目录跑 `check_dir`）。

### 2.3 成绩单理由与 Q1（方案 §3.3）

1. `game_type.CHILD_GROWTH`：加 `semester_base_work_type = -1`（方案 §4.1）
2. `semester_handle.reset_semester_baseline`：写 `character_data.work.work_type`
3. `get_report_incomplete_reason`：按方案 §3.3 的表写六种情形；学期初未知（-1）时用 `get_semester_attend` 判本学期有无出勤或缺课记录；docstring 写明只看学期初与结算时两个时刻
4. Q1（推荐口径）`settle_semester_change`，学期号变了的那一支：
   - 阶段为 104，学期初与结算时都不是学生岗 → 只 `reset_semester_baseline`，`continue`（不出成绩单、不置待查看、不进返回名单）；
   - 学期初为 -1（旧档的第一个学期）：结算时不是学生岗、且本学期 0/0，按「整学期不在学生岗」处理；
   - 备选口径：不加这一支。
5. 检查点：
   - 五种有意义的情形各出对的理由（学期中途改出、整学期不在、中途回来、一直是学生、未知两种）；
   - 成年且整学期不在学生岗：不出成绩单、flag 不动、名单里没有她（Q1）；成年学生岗照出；
   - 萝莉整学期不在学生岗：照出，理由「本学期担任…，没有上课」。

### 2.4 同一节只落一种记录（方案 §3.4）

1. `growth_handle.judge_absent_this_period(character_id, now_time) -> bool`：
   - 读 `character_data.child_growth`，为 None 返回 False；
   - 节次按 `game_time.get_class_period_by_time(now_time)`，节次外返回 False；
   - `last_absent_period == [now_time.toordinal(), 节次]` 为 True。只读。
2. `settle_student_class_gain`：`count_attend` 为真、且本节已缺课时不加出勤；收益与 `last_attend_period` 照写
3. `settle_course_attend`：本节已缺课时返回 False，不写标记
4. `sex_class_handle.settle_attend(student_id, now_time=None)`：
   - `now_time` 为 None 取学生的行为开始时刻（722 用），`start_sex_class` 传 `cache.game_time`；
   - 本节已缺课不记。
5. 检查点：
   - 721 缺课后同一节：716、304 + 557、722 都不计出勤，收益照给；
   - 下一节照常计；
   - 没缺课的节次与改前一致。

### 2.5 翘课被抓后当天不再翘（方案 §3.5）

1. `game_type.CHILD_GROWTH`：加 `skip_caught_day = 0`（方案 §4.1）
2. `Second_effect.py` 623：清 flag 的同时写 `growth_data.skip_caught_day = cache.game_time.toordinal()`；docstring 同步
3. `class_ai.roll_skip_class`：定下 `now_time` 之后，读 `character_data.child_growth`（不惰性创建），`skip_caught_day == now_time.toordinal()` 就返回 False；docstring 同步
4. 检查点：
   - 被抓当天后续节次掷不中，`get_course_stage` 不再给 SKIP；
   - 次日照常掷；
   - `judge_student_join_class`（303 拉人）同样不再判她翘课。

### 2.6 「有课」「同班同学」只看学生岗的真课（方案 §3.6）

1. `schedule_handle.judge_personal_course_real(character_id, course) -> bool`：`judge_course_need_pass` 且上课地点解析得出；`judge_personal_course_valid` 改为 real 且（不是读书课，或借得到书）；两处 docstring
2. `growth_handle.judge_selected_cell_real(character_id, week_day, period) -> bool`：
   - 角色存在、学生岗、个人课表这一格有课；
   - 教室课：`get_class_cell(目标, 星期, 节次, include_temp=False)` 不为 None；
   - 个人式课：`judge_personal_course_real`；
   - 只读，不惰性创建。
3. `handle_self_have_any_course`：遍历个人课表，任一格 real 为 1
4. `get_classmate_list`：自己那一格 real 才进比对集合；对方同一格也 real 才算同学
5. 检查点：
   - 改岗萝莉两个前提都不成立；
   - 课表全停课的孩子不成立；
   - 学生岗照常；R5 的候选里不再有上课 / 同学事件。

### 2.7 必修名单的顶替标记（方案 §3.7）

1. `class_schedule_panel._select_must_attend`：个人式课改用 `judge_personal_course_real`；注释同步
2. 检查点：书库借空时，读书兴趣课那一格照标「*」

### 2.8 文档（方案 §3.8）

1. 说明文档 `生长养成系统.md`：按方案 §3.8 的清单逐节改；§15 第 4 条的写入点改为「学生结算 / 体育兴趣课出勤 / 实操课出勤 / 体力缺课 / 翘课缺课」，新增一条期末事件前提的维护注意
2. 索引 `生长养成系统设计文档.md`：计划表那一行改成「plan_25 ~ plan_30」，补第十一轮一句
3. Plan 22 总纲：追加 §16，一行指向本 Plan
4. `update.log`：调用 `update-changelog` skill 登记

### 2.9 测试

| 文件 | 新增 / 改写 |
| --- | --- |
| `test_class_ai` | 714 记缺课与翘课数、同一节体力缺课后再翘只记一次、flag 保持的后续节次各记一节、在教室里先离开的那一步不记；被抓当天 `get_course_stage` 不再给 SKIP、次日照常；721 后同一节 716 不计出勤 |
| `test_settle_effects` | 623 写 `skip_caught_day`；本节已缺课时 512 / 557 照给收益、不计出勤 |
| `test_sex_class` | 本节已缺课时 `settle_attend` 不记（开课与 722 两条路） |
| `test_semester` | 学期基线记岗位；改岗理由的六种情形；Q1：成年且整学期不在学生岗不出成绩单、成年学生岗照出、萝莉整学期不在学生岗照出；成绩单出勤率含翘课 |
| `test_growth` | 养成数值 24；`judge_absent_this_period`；`judge_selected_cell_real`（学生岗、停课、未开放、条件不符、改岗） |
| `test_growth_event` | 同学只算学生岗的真课（**夹具要改**：`test_growth_event.py:26~30` 的两格要在全局课表上排 `set_class_cell`，否则按「已停课」不再算同学）；改岗萝莉没有同学、不抽上课 / 同学事件；期末 9 / 10 进得了待努力萝莉的候选；萝莉 2 前提 |
| `test_premise_tokens` | `self_have_any_course` 只看学生岗的真课；`CVP_A1_Growth\|24` |
| `test_panels` | 书库借空时必修名单照标「*」 |
| `test_save_compat` | 三个新字段回填 |
| `test_talk_data` | `official_event_check.py` 通过（含新规则）；新规则对构造的违规行报错 |
| `README.md` | 覆盖描述、断言总数 |

## 3. 构建与缓存

```bash
.conda\python.exe tools/official_event_check.py        # 改完两张事件表跑（含新规则）
.conda\python.exe tools/tests/education/run_all.py     # 测试引导 import auto_build_config（BUILD_OFFICIAL_EVENT=True），自动从 CSV 重建 Official_Event.json 与 data.json
git diff --stat
git checkout -- data/po/                               # 本机无 gettext，构建会写乱 PO，一律还原
```

- 不改口上、`target.csv`、地图：不需要 `buildconfig.py`，不删 `data/Character_Talk.json` 与场景缓存
- 若增量构建重新生成的 `config_def.py` 与仓库版本差一个空行（Plan 27 §6.1 偏离 7），`git checkout` 还原
- 往文件里写含反斜杠转义的字符串时别走 Bash heredoc（Plan 29 踩过），用 Write / Edit 或 `chr(92)`；写完先 `py_compile`

## 4. 验证清单

### 4.1 单元测试（实施方执行，按 `headless-game-test` 模式 A）

- [x] §2.0 复现：改前 39 项全部成立；改后 18 项问题命中不再成立，R1-2 随 Q1，其余 20 项照旧
- [x] `test_talk_data`、`tools/official_event_check.py` 通过（含新规则）
- [x] §2.9 各文件新增断言通过
- [x] `run_all.py` 全部文件 PASS，断言数记入 §6.3

### 4.2 行为循环（实施方执行，按 `headless-game-test` 模式 B）

- [x] `test_behavior_loop.py` 收敛；上午四节人均出勤 ≥ 3（本轮只有「已缺课的节次不计出勤」可能让出勤略少，存档里体力充足的学生不受影响）；教师在对的教室授课；实操课到场断言不变

### 4.3 游戏内整体测试（由用户执行）

- [ ] 让女儿翘一次课：养成总览本学期缺课 +1，成绩单的出勤率跟着降
- [ ] 翘课被撞见后，当天后面的课都回去上了
- [ ] 把一个萝莉改岗：处理公务时不再出现写「在上课」「同班同学」的事件；下一学期成绩单的理由写「本学期担任…，没有上课」
- [ ] 成年后换了岗位的女儿，学期结束不再出成绩单（Q1 按推荐时）
- [ ] 期末：待努力的孩子有机会遇到期末 9 / 10
- [ ] Tk 与 Web 两种模式下无报错

## 5. 回滚

| 单元 | 内容 | 回滚方式 | 备注 |
| --- | --- | --- | --- |
| A：翘课 | §2.1、§2.5 | `git revert` | 已记的缺课与翘课数不回收；萝莉 2 的前提随之回滚 |
| B：期末事件与工具 | §2.2 | `git revert` | 回滚后跑一次 `official_event_check.py` |
| C：成绩单理由与 Q1 | §2.3 | `git revert` | `semester_base_work_type` 留在存档里无害 |
| D：同一节只落一种记录 | §2.4 | `git revert` | 不影响存档 |
| E：有课 / 同学 / 必修标记 | §2.6、§2.7 | `git revert` | 不影响存档 |

- 新字段靠回填，改动前后的存档互相兼容

## 6. 实施过程记录

### 6.1 实际改动

| 文件 | 改动 |
| --- | --- |
| `Script/Core/game_type.py` | `CHILD_GROWTH` 加 `skip_count` / `skip_caught_day`（`last_attend_period` 之后）、`semester_base_work_type`（`semester_base_ability` 之后）；`absent_count` / `last_absent_period` 注释 |
| `Script/Core/constant_promise.py` | 加 `TARGET_REPORT_CARD_CHECKABLE`；`SELF_HAVE_ANY_COURSE` / `SELF_HAVE_CLASSMATE` 注释改为新口径 |
| `education_constant.py` | 第 12 组末尾加 `GROWTH_VALUE_SKIP = 24` |
| `class_ai.py` | `settle_absent(character_id, by_skip=False) -> bool`（记上才加、`by_skip` 另加翘课数、节次外返回 False）；`roll_skip_class` 被抓当天返回 False；模块头注释 |
| `growth_handle.py` | 新增 `judge_absent_this_period`、`judge_selected_cell_real`；`settle_student_class_gain` / `settle_course_attend` 本节已缺课不计出勤；`get_growth_value` 读编号 24 |
| `semester_handle.py` | `reset_semester_baseline` 记岗位；`get_report_incomplete_reason` 按学期初岗位分情形；新增 `judge_adult_out_of_school`、`judge_report_card_checkable`；`settle_semester_change` 的 Q1 |
| `schedule_handle.py` | 新增 `judge_personal_course_real`，`judge_personal_course_valid` 改用它 |
| `growth_event_handle.py` | `get_classmate_list` 双方同一格都是真课 |
| `sex_class_handle.py` | `settle_attend(student_id, now_time=None)` 本节已缺课不记；`start_sex_class` 传 `cache.game_time` |
| `class_schedule_panel.py` | `_select_must_attend` 的个人式课改用 `judge_personal_course_real` |
| `Script/StateMachine/default.py` | 714 在人已不在教室那一支记一节缺课（`by_skip=True`） |
| `Script/Settle/Second_effect.py` | 623 写 `skip_caught_day` |
| `handle_premise_other.py` | `handle_self_have_any_course` 改用 `judge_selected_cell_real`；新增前提 `handle_target_report_card_checkable` |
| `data/official_event/期末.csv` / `萝莉.csv` | 期末 9 / 10 去掉 `&CVP_A1_Growth\|6_L_70`；萝莉 2 改为 `CVP_A1_Growth\|24_GE_3` |
| `data/csv/InstructConfig.csv` | 1036 前提串末尾加 `TARGET_REPORT_CARD_CHECKABLE` |
| `tools/ArkEditor/csv/Premise.csv` | 加 `target_report_card_checkable` 一行；`self_have_classmate` / `self_have_any_course` 的描述改为新口径 |
| `tools/official_event_check.py` | `SEMESTER_SUB_KEY` / `SEMESTER_VALUE_ID` / `GROWTH_VALUE_RE` 与 `check_semester_premise`：期末桶的主前提与选项前提读养成数值 4 / 5 / 6 报错 |
| 测试 10 个 + README | 见 §6.3 |
| 文档 | 说明文档 §1 / §2 / §4 / §5 / §6 / §8 / §10 / §12 / §14 / §15（第 2、4 条改写，新增第 22 条）/ §16；索引文档；Plan 22 总纲 §16；`update.log`（调整 1 条、修正 8 条） |

与方案的偏离：

1. **改岗理由的规则推广**（方案 §3.3 已同步）：「学期初非学生岗 → 结算时非学生岗」而本学期有出勤 / 缺课记录（中途进过学生岗又出去）时按「改任了」写，不写「没有上课」，免得理由与正文的出勤数矛盾。结算时不在学生岗的三行合成一条规则：学期初是学生岗、或本学期有记录 →「改任了」，否则 →「担任…，没有上课」。
2. **Q1 收窄多一个条件「本学期 0/0」**（方案 §3.3 已同步）：学期初已知为非学生岗、但本学期有记录的成年女儿照出成绩单，与学期初未知时的推断口径一致。
3. **用户追加口径：「检查成绩单」的对象限制**（方案 §3.3 / §4.2 / §4.3 已同步）：新增前提 `target_report_card_checkable` 挂在 1036 前提串末尾，判据 `semester_handle.judge_report_card_checkable`，与学期结算共用 `judge_adult_out_of_school`。有待查看成绩单时例外（学期中途才离开学生岗那一学期照出，养成总览提示「用「检查成绩单」指令」，挡掉的话 flag 永远清不掉）。「不能对非女儿的学生岗使用」由既有的 `TARGET_IS_PLAYER_DAUGHTER` 保证，只补断言。
4. `settle_absent` 加了节次外守卫（返回 False），方案没写：两个调用方都只在节次内派发，兜一道防止节次外的标记占掉当天真正的缺课。
5. `Premise.csv` 里 `self_have_classmate` / `self_have_any_course` 两行的描述原本在空格处被截成「（Plan」，顺带改成新口径的完整描述（不含空格）。
6. 测试夹具三处随口径改：`test_class_ai` 两道闸那一段之后清 `last_absent_period`（同一天第 1 节后面的段落还要验出勤，否则按「本节已缺课」不计，5 条断言挂掉）；`test_premise_tokens` 与 `test_growth_event` 的同学用例补 `set_class_cell`（按「已停课」不再算同学，实施文档 §2.9 已预见后者）；`test_semester` 原「学生岗理由为空」断言之前多一条「中途回到学生岗」并重置基线。
7. 复现 R7-5 定案时写的候选为 11 / 13 / 14 / 16，实测改前为 11 / 13 / 14 / 15 / 16（期末 15 也在），不影响结论；改后多了 9 / 10。

### 6.2 实施前的假设复核

以下是定案时（2026-09-13，`master @ 90716619b`）已经复核过的事实，实施前只需抽查：

| # | 方案中的事实 | 出处 | 复核结果 |
| --- | --- | --- | --- |
| 1 | `absent_count` 只有 `class_ai.settle_absent` 写，调用方只有 721 | grep `absent_count +=`、`settle_absent(` | **成立** |
| 2 | 549 只置翘课 flag、回落抑郁，不记缺课 | `Settle/default.py:7724~7746` | **成立**（读代码 + 复现 R2） |
| 3 | 714 还在教室时先离开，不在教室才置翘课行为 | `StateMachine/default.py:2756~2785` | **成立**（读代码） |
| 4 | 萝莉 2 的前提是累计缺课 ≥ 3，正文写翘课 | `萝莉.csv` cid 2 | **成立**（复现 R2-5） |
| 5 | 期末事件在 `settle_semester_change` 之后推送，那时学期基线已重置 | `past_day_settle.py:111~113`；`semester_handle.py:339~364` | **成立**（复现 R7） |
| 6 | 待努力就是有课且出勤率 < 70 | `semester_handle.get_report_grade` | **成立**（读代码） |
| 7 | `get_report_incomplete_reason` 只看结算时的岗位 | `semester_handle.py:218~238` | **成立**（复现 R1） |
| 8 | 学期结算遍历含成年女儿 | `growth_handle.get_student_candidate_list` | **成立**（复现 R1-0） |
| 9 | 721 原地休息 30 分钟，不在休息室 / 宿舍按 0.3 倍回复 | `StateMachine/default.py:166~176`；`realtime_settle.py:405~433` | **成立**（复现 R3-1：560 → 704 / 2000） |
| 10 | 716 / 557 的出勤只按 `last_attend_period` 去重，不看本节缺课 | `growth_handle.py:229~355` | **成立**（复现 R3） |
| 11 | 623 只清 flag、加抑郁与恐怖；`roll_skip_class` 不看被抓 | `Second_effect.py:3003~3022`；`class_ai.py:404~427` | **成立**（复现 R4） |
| 12 | 被抓加的量在两档都不跨等级 | 复现 R8 | **成立** |
| 13 | `self_have_any_course` 只看课表非空；`get_classmate_list` 不看岗位 | `handle_premise_other.py:1237~1252`；`growth_event_handle.py:107~140` | **成立**（复现 R5） |
| 14 | 必修名单的「*」用 `judge_personal_course_valid` 判，含借书 | `class_schedule_panel.py:577`；`schedule_handle.py:646~663` | **成立**（读代码 + 复现 R6） |
| 15 | 改岗入口 8 处，幼女限制只在基建面板 | grep `work.work_type =` | **成立**（读代码，方案 §2.3） |
| 16 | 女儿的出身地与势力默认罗德岛（0） | `character_handle.create_empty_character_tem` | **成立**（读代码，方案 §2.3） |
| 17 | 增量构建会重建公务事件表 | `auto_build_config.py:53`、`:467` | **成立**（读代码） |
| 18 | 新字段靠属性表回填 | `save_handle.py:389~400` | **成立**（读代码） |
| 19 | 测试夹具的同学用例依赖「个人课表同一格」而全局课表空着 | `test_growth_event.py:26~30` | **成立**（读代码；§2.6 实施后要补 `set_class_cell`） |

实施前抽查：#1、#2、#3、#10、#11、#13、#14 读代码复核成立；其余由复现脚本改前 39 项全部成立佐证。

### 6.3 单元测试结果

复现脚本（scratchpad `p30/repro_plan30.py`，不入库）：改前 39 项全部成立；改后成立 20、不成立 19——18 项问题命中（R1-1、R1-4、R2-2~7、R3-2、R3-3、R4-3、R5-2~5、R7-3~5）加 R1-2（Q1：成年女儿不再有成绩单），其余 20 项照旧。关键实测：R2 上 1 节翘 3 节 → 本学期 (1, 3)、25%、待努力；R3 休完同一节 716 照派、出勤 +0；R5 改岗萝莉候选里的上课 / 同学事件 24 → 0；R1-4 改为「萝莉丁本学期担任检修工程师，没有上课」。

| 文件 | 改前 | 改后 | 新增覆盖 |
| --- | --- | --- | --- |
| `test_class_ai` | 257 | 269 | 714 记缺课与翘课数（在教室先离开不记、同节不重复、flag 后续各记、体力缺课后再翘只记一次），721 后同节 716 不计出勤，被抓当天不再 SKIP / 303 不判翘课 / 次日照常 |
| `test_growth` | 80 | 94 | 养成数值 24、`judge_absent_this_period`、`judge_selected_cell_real` |
| `test_growth_event` | 53 | 63 | 同学 / 有课只算学生岗的真课、改岗萝莉无上课与同学事件、期末 9 / 10 候选、萝莉 2 按翘课数 |
| `test_panels` | 91 | 92 | 书库借空时必修名单照标「*」 |
| `test_premise_tokens` | 123 | 133 | `self_have_any_course`、`Growth\|24`、1036 的对象（成年离岗 / 有待查看 / 成年学生岗 / 改岗萝莉 / 非女儿学生岗） |
| `test_save_compat` | 12 | 13 | 三个新字段回填 |
| `test_semester` | 53 | 75 | 缺课含翘课、学期基线记岗位、改岗理由九种组合、Q1 各情形、`judge_adult_out_of_school` / `judge_report_card_checkable` |
| `test_settle_effects` | 83 | 87 | 本节已缺课 512 / 557 不计出勤、623 记被抓日期 |
| `test_sex_class` | 89 | 92 | 本节已缺课时开课与 722 不记出勤 |
| `test_talk_data` | 57 | 60 | 期末 9 / 10 前提、校验工具新规则对违规行报错 |
| 其余 5 个 | 228 | 228 | —（`test_behavior_loop` 18 条：六轮收敛、上午四节人均出勤 ≥ 3、教师在对的教室授课） |
| **合计** | **1126** | **1206** | |

`tools/official_event_check.py`：校验通过，5 个文件共 266 条事件。构建写乱的 `data/po/` 已 `git checkout` 还原；`config_def.py` 与其它生成物不在 git 追踪的改动里。

### 6.4 尚未覆盖的验证

- 实施文档 §4.3 的游戏内整体测试（翘课计缺课与成绩单、被撞见后当天回去上课、改岗萝莉的事件与成绩单理由、成年离岗女儿不出成绩单且检查成绩单不可用、期末 9 / 10、Tk 与 Web 两种模式）留给用户
- 新增的五句成绩单理由 / 注释文案走 `_()`：本机无 gettext，没跑 `buildpo.py` / `buildmo.py`，要在装有 gettext 的机器上补（说明文档 §15 第 9 条）
- 真实存档读档后的旧档第一个学期（`semester_base_work_type` = -1）只由单元测试覆盖，没有在真实存档上跑一次学期切换

### 6.5 追加调整实施记录

（与方案 §8 成对，每轮一节，附回归测试计数。暂无）
