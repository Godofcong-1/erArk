# Plan 19（实施步骤与记录）：无壳卵生种族的生育机制

> 本文件是 `plan_19_无壳卵生机制_方案.md`（下文简称"方案"）的**实施步骤清单与过程记录**。
> 需求背景、现状调查、设计决策、数据结构定义、口径确认、风险与范围外事项一律以方案文档为准；
> 本文件只写"怎么做、怎么验、怎么回滚"，实施过程与结果记入 §6。

- 状态：**实施完成（2026-08-29，单元测试 83/83 通过，plan_17/18 回归 132/132、68/68 通过，详见 §6；游戏内整体测试 §4.2 与 buildpo/buildmo 待用户执行）**
- 适用代码快照：`master @ acdbc1c08` + 工作区未提交的 plan_17/plan_18 改动
- 实施前提：先通读方案文档；实施中发现与方案冲突的事实，**先更新方案再动代码**；全程主代理自行完成，不调用子代理

## 1. 改动文件清单

| 文件 | 类型 | 改动 |
| --- | --- | --- |
| `Script/System/Pregnancy_System/soft_egg_handle.py` | 新增 | 无壳卵全部逻辑：体外排卵判定、建卵与精液转移、场景查卵、加精、0~15 级换算、1 小时受精判定、回写母亲 `eggs` |
| `Script/System/Pregnancy_System/pregnancy_constant.py` | 修改 | 分组 8 常量；阶段枚举插入 `STAGE_SOFT_EGG_WAIT` 并顺延 |
| `Script/System/Pregnancy_System/egg_handle.py` | 修改 | `get_birth_type` 去 12 归一化；`is_egg_soft/is_egg_layer`；`add_egg` 增 `soft` 键；`replace_entertainment_for_eggs` 放行 12；`check_egg_born` 对 12 批量收集 |
| `Script/System/Pregnancy_System/pregnancy_handle.py` | 修改 | `get_fertilization_rate` 三处 `now_rate = new_rate`（方案 §3.12）；`update_reproduction_period` 维护 `external_ovulation_chance` 与药效过期；`check_fertilization` 对 12 早退；`check_all_pregnancy` 分流 |
| `Script/System/Pregnancy_System/born_event_panel.py` | 修改 | `egg_id_list` 参数、批量取名、无壳文案组、`soft_egg_born` |
| `Script/System/Pregnancy_System/pregnancy_panel.py` | 修改 | 新阶段判定与信息文本 |
| `Script/Settle/orgasm_settle.py` | 修改 | 每部位分支末尾体外排卵判定 |
| `Script/Design/second_behavior.py` | 修改 | NPC 分支绝顶结算后显式结算 `lay_soft_egg` |
| `Script/Settle/Second_effect.py` / `Script/Core/constant_effect.py` | 修改 | `SecondEffect.LAY_SOFT_EGG = 621` 结算器 |
| `Script/Settle/default.py` | 修改 | 催眠立刻排卵对 12 置 `external_ovulation_chance` |
| `Script/Settle/realtime_settle.py` / `Script/Settle/sleep_settle.py` | 修改 | 体外受精判定挂钩 |
| `Script/Design/attr_calculation.py` | 修改 | 抽出 `get_semen_level_by_volume` |
| `Script/UI/Panel/ejaculation_panel.py` | 修改 | 强制手动/自慰 `self_mode`、卵按钮、`shoot_soft_egg`、`ejaculation_flow(soft_egg_id)` |
| `Script/UI/Panel/dirty_panel.py` | 修改 | 体外卵污浊行（普通/详细） |
| `Script/Core/game_type.py` / `Script/Core/save_handle.py` | 修改 | `external_ovulation_chance`、`soft_eggs/next_soft_egg_id`、回填与 12 族孕程清理 |
| `Script/Core/constant_promise.py` / `Script/Design/handle_premise/handle_premise_other.py` / `tools/ArkEditor/csv/Premise.csv` | 修改 | 4 个前提 |
| `data/csv/Behavior_Data.csv`（+ArkEditor 副本）/ `data/csv/Behavior_Effect.csv` | 修改 | 1325/1326/1327 二段行为与效果链 |
| `tools/ArkEditor/csv/Effect.csv` | 不改 | 核对后确认该文件只收录 `BehaviorEffect` 段（其 621 为 `GET_T_PAN`），`SecondEffect.LAY_SOFT_EGG=621` 不同步 |
| `data/ui_text/dirty.csv` / `data/ui_text/soft_egg_dirty_full.csv`（新） | 修改/新增 | 体外卵普通污浊 1 条 / 详细污浊 0~15 级 16 条 |
| `data/talk/system/second_pregnancy.csv` | 修改 | 508 条口上（方案 §3.13）；第 1 次修改后无壳三行为 120 条按"卵块"口径重写 + 女儿身份差分 80 条，文件共 624 条 |
| `.github/prompts/数据处理工作流/妊娠系统.md`、`射精面板系统.md`、`身体信息面板系统.md`、`plan/done/plan_12_…_方案.md` §10 | 文档 | 方案 §10 |
| `update.log` | 修改 | 新增 3 条（无壳卵生、界面、口上差分）+ 修正 1 条（受精率加成 bug） |

## 2. 详细改动步骤

> 按阶段实施，每阶段结束跑一次语法检查与阶段断言；数据结构、字段名、数值口径以方案 §3/§4/§11 为准。

### 2.1 第一阶段：常量、数据结构、卵核心逻辑（方案 §3.1/§3.2/§3.5/§3.8/§3.9/§3.12/§4）

1. `pregnancy_constant.py` 分组 8 + 阶段枚举顺延。
2. `game_type.py` 三个字段；`save_handle.py` 回填 + 12 族孕程清理。
3. `egg_handle.py`：去归一化、两个判定函数、`add_egg(soft)`、娱乐替换放行。
4. `pregnancy_handle.py`：bug 修复、周期推进维护机会/药效、`check_fertilization` 早退、`check_all_pregnancy` 分流。
5. `attr_calculation.py`：`get_semen_level_by_volume` 抽出。
6. 新建 `soft_egg_handle.py`（除绝顶判定外的全部函数 + `judge_external_ovulation`）。
7. 前提 4 个（常量、函数、ArkEditor CSV）。

### 2.2 第二阶段：绝顶触发与结算链（方案 §3.3/§3.4）

1. `constant_effect.SecondEffect.LAY_SOFT_EGG = 621` + `Second_effect.py` 结算器。
2. `Behavior_Data.csv`（+ArkEditor）/ `Behavior_Effect.csv` 三行；`Effect.csv` 副本核对。
3. `orgasm_settle.py` 挂钩；`second_behavior.py` 显式结算；`Settle/default.py` 催眠分支。
4. `realtime_settle.judge_pl_real_time_data` / `sleep_settle` 挂钩。

### 2.3 第三阶段：射精面板与身体栏（方案 §3.6/§3.7）

1. `ejaculation_panel.py`：`draw` 分支、`draw_choose_part(self_mode)`、`shoot_soft_egg`、`ejaculation_flow(soft_egg_id)`。
2. `dirty.csv` 1 条、`soft_egg_dirty_full.csv` 16 条；`dirty_panel.py` 卵行。

### 2.4 第四阶段：破壳事件与总览面板（方案 §3.10/§3.11）

1. `egg_handle.check_egg_born` 批量；`born_event_panel.py` `egg_id_list` + 无壳文案。
2. `pregnancy_panel.py` 新阶段。

### 2.5 第五阶段：口上（方案 §3.13）

- `second_pregnancy.csv` 508 条，分行为批量写入脚本，逐组合计数校验。

### 2.6 第六阶段：构建、测试、文档、update.log

- 全量 `buildconfig.py`（先删 `data/Character_Talk.json`）；`test_plan19.py` 全部通过；重跑 `test_plan17.py`/`test_plan18.py`；文档与 update.log；方案 §12 与本文件 §6 记录。

## 3. 构建与缓存

```bash
# 本机必须用 conda 解释器（裸 python 是 Store 空壳别名）
rm -f data/Character_Talk.json
timeout 600 ./.conda/python.exe -u buildconfig.py > "<scratchpad>/build.log" 2>&1
```

新增 `_()` 文案与 ui_text 需用户 `buildpo` / `buildmo`。

## 4. 验证清单

### 4.1 单元测试（实施方执行，`scratchpad/test_plan19.py`，照 skill `headless-game-test`）

方案 §7.1 的 1~13 项（含 12a/12b/12c）逐条落为断言。

### 4.2 游戏内整体测试（由用户执行）

方案 §7.2。

## 5. 回滚

- 全部改动为工作区未提交状态，可 `git checkout -- <文件>` 逐文件还原、删除新增文件；存档新字段均为附加，旧版本读取新存档只是多出未用属性；12 族孕程清理不可逆（仅影响三族旧存档中正在怀孕的角色，方案 §11-6 已确认）。

## 6. 实施过程记录

### 6.1 实际改动（按 §2 阶段）

- **第一阶段**：`pregnancy_constant.py` 分组 8（12 项常量 + 3 个二段行为 id 常量）、阶段枚举插入 `STAGE_SOFT_EGG_WAIT=3` 并顺延（grep 确认代码中无硬编码阶段数字）；`game_type.py` 三字段；`save_handle.py` 回填 + 新函数 `_clear_soft_egg_race_pregnancy`（按 `config_race[race].birth_type == 12` 与 talent 20/21/22 任一判定，清 20/21/22/26/35 与 fetus_count/identical_twins/acceleration_days）；`egg_handle.py` 去归一化、`is_egg_soft/is_egg_layer`、`add_egg(soft)`、娱乐替换放行；`pregnancy_handle.py` 三处 `now_rate = new_rate`（提示文案改用改前值作起点）、周期推进维护机会与药效过期、`check_fertilization` 12 早退、`check_all_pregnancy` 分流；`attr_calculation.get_semen_level_by_volume` 抽出；新建 `soft_egg_handle.py`（13 个函数）；前提 4 个（常量/函数/ArkEditor CSV）。
- **第二阶段**：`SecondEffect.LAY_SOFT_EGG=621` + `Second_effect.handle_lay_soft_egg`；`Behavior_Data.csv`（主表 + ArkEditor 副本，副本末列为 `二段结算_生育`）/ `Behavior_Effect.csv` 三行；ArkEditor `Effect.csv` 核对后不同步（只收录 BehaviorEffect）；`orgasm_settle.py` 每部位分支记录 `max_degree` 并在 U 绝顶排尿之后调判定（`handle_self_birth_type_egg_soft` 先筛种族）；`second_behavior.check_second_effect` NPC 分支绝顶结算后显式结算 `lay_soft_egg`；`Settle/default.py` 催眠分支补置机会；`realtime_settle.judge_pl_real_time_data` 末尾与 `sleep_settle` 玩家分支各挂一次 `check_soft_eggs_fertilization`。
- **第三阶段**：`ejaculation_panel.py`：`draw` 三分支（自慰 self_mode / 群交 / 有卵强制手动）、`draw_choose_part(self_mode)`（卵按钮每 4 个换行、`[照常射出]`）、`shoot_soft_egg`、`ejaculation_flow(soft_egg_id)`；`dirty.csv` 1 条、`soft_egg_dirty_full.csv` 16 条（0 级洁净、1~10 级以子宫未孕文案为底本改写为卵膜视角、11~15 级新写）；`dirty_panel.py` 卵行。
- **第四阶段**：`egg_handle.check_egg_born` 对 12 批量收集；`Born_Panel(egg_id_list)`、`soft_egg_mode` 推断、无壳文案组（单/多）、取名循环复用 plan_18、总结行、结算删全部卵、育儿提示列全部名字；`pregnancy_panel.py` 新阶段判定与信息文本（`get_soft_egg_scene_name`/`get_soft_egg_remain_minute`）。
- **第五阶段**：口上 4 个脚本（`p19_talk_a~d.py` + 公共模块 `p19_talk_common.py`），cid 从 2001 起，逐行断言无 ASCII 逗号/无真实换行/含占位符；写入后按前提 token 逐〈行为×年龄〉计数：既有 11 个母亲视角行为七档各 5、成长类 103/104 各 5、新行为通用 5 + 七档各 5，文件 36→544 条。
- **第六阶段**：删 `Character_Talk.json` 后全量 `buildconfig.py`（EXIT=0）；文档 4 份 + update.log（新增 3 条、修正 1 条）。

### 6.2 实施前的假设复核

- `judge_orgasm_degree` 为概率函数（非确定映射）——测试中打桩为固定程度，配合 `ability[7]=6` 走 W 超强 100% 使集成路径确定。
- `talk.must_show_talk_check` 在玩家同场景时会立即触发口上并把二段行为归零——测试改为包装 `character_get_second_behavior` 记录赋予事件，而不是事后读 flag。
- 无头环境下 `askfor_all` 桩不会回调按钮 `cmd_func`——射精面板改为"分支进入 + 按钮布局 + 回调函数"三段分别断言。
- 体外受精桩值 100 在概率封顶 100 时会命中——失败桩改用 101。

### 6.3 单元测试结果

- `test_plan19.py` **83/83 通过**（EXIT=124 为残留线程被 timeout 回收，结果已完整打印）。覆盖：配置/常量/前提/二段行为/效果链/ui_text/口上计数；周期推进与药效过期；12 族 `check_fertilization` 早退；概率表 9 格 + 药物/催眠 ×5/封顶 + 未命中不消耗 + 不在场不触发 + 命中消耗；绝顶集成（W 超强）+ 二段链（体力/气力下降、卵 1200ml、部位各剩 20%、提示）；等级边界 13 点、受精概率公式、`get_semen_now_level` 等价；身体栏普通/详细/换交互对象；射精面板三分支、按钮布局、卵回调、避孕套；59/61 分钟判定、无限轮次数、3 枚回写与 lay_time、全失败、realtime 挂钩；孵化链四项；批量破壳 3 次取名 + 带壳单卵回归；回填、12 族孕程清理、受精率修复四项。
- 回归：`test_plan17.py` 132/132；`test_plan18.py` 68/68（"12 归一化为胎生"断言按新语义改为 False）。

### 6.5 第 1 次修改记录（2026-08-29，卵块口径 + 女儿身份差分）

- 触发：用户指出无壳卵应是"成百上千颗卵粒被凝胶包裹成的卵块"（鱼籽式），并要求补"女儿身份"的二段行为差分。
- 改动：代码文案 6 处（`soft_egg_handle` ×3、`born_event_panel` ×3、`dirty_panel`、`pregnancy_panel`、`pregnancy_constant`、`ejaculation_panel`）；`soft_egg_dirty_full.csv` 16 条重写；`second_pregnancy.csv` 无壳三行为 120 条重写 + 女儿差分 80 条（脚本 `p19b_data.py`，先删旧行再按公共模块追加，逐行校验）。
- 结构不变：`soft_eggs` 一条仍代表一团卵块；受精循环每轮成功仍是回写一枚 `eggs`（现称"一颗受精卵粒"）；孵化/破壳链与测试逻辑不受影响。
- 验证：全量重建后 `test_plan19.py`（断言改为"卵块"措辞、阶段名"卵块待受精"、女儿差分计数）83/83 通过。
- 事故与恢复：本次文档同步脚本的写函数写成 `open(p, "w").write(fn(raw))`——`open` 先于 `fn` 求值，`fn` 内断言失败时文件已被截空；先后截空了 `update.log`（git 有 HEAD，恢复后重加本会话 plan_18/plan_19 的 6 条终态条目）与方案文档（无版本控制，按 v1 原文重放 `p19_v2~v5.py` 补丁脚本、再补回拆分注释/§12/v6 记录，内容与截空前一致）。实施文档与设计文档未受影响。教训：一律先算出完整内容再打开文件写入。

### 6.4 尚未覆盖的验证（留给用户的游戏内清单）

- 方案 §7.2：安努拉干员实机流程（排卵口上 → 面板卵按钮 → 身体栏卵行 → 1 小时后受精提示 → 育儿室孵化/保育员/孵化加速药 → 批量破壳取名）；Web 模式下射精面板与身体栏的显示；`buildpo`/`buildmo` 后的翻译文件。
