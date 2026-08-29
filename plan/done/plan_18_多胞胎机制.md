# Plan 18：胎生种族多胞胎机制（多胎胎生生育方式 2）

- 状态：**已实施（2026-08-29，无头测试 67/67 通过（九族复核后重跑仍 67/67）、plan_17 回归 132/132 通过，见 §12；游戏内整体测试与 buildpo/buildmo 本地化步骤待用户执行）**
- 来源：用户需求 → 为胎生的怀孕种族增加多胞胎机制
- 修订记录：
  - v0 —— 骨架：章节结构 + 目标整理（用户订正：多胎胎生编号为 **2** 而非 12，避开既有的 12=无壳卵生）
  - v1 —— 现状调查（§2 全部为实际代码核实结果）+ 设计决策（§3）+ 数据结构（§4）+ 改动步骤（§5）+ 构建/验证/风险/范围外/文档同步 + §11 待确认口径
  - v2 —— 口径确认轮（2026-08-29）：①**`1,卡特斯/奇美拉` 也改为多胎、范围同卡特斯 4~12**（共七族）②实装 4 个多胎前提 ③每轮概率按比例缩放 ④单胎种族 `fetus_count` 写 1、生产后清零。§1/§2.1/§3.2/§5/§7/§9/§11 已按确认结果改写
  - v3 —— 用户追加需求（2026-08-29）：**单胎胎生（1）的受精成功事件有 1% 概率生出同卵双胞胎**，之后按多胞胎流程处理（胎数 2、生产逐个取名），但提示/事件文案须与多胎胎生（2）**区分开**。新增 §3.7、`PREGNANCY.identical_twins` 字段、常量 `IDENTICAL_TWINS_RATE`、前提 `self/t_identical_twins`；§1/§4/§5/§7/§11 同步
  - v4 —— 实施完成（2026-08-29）：按 §5 全部落地；实施中用户在 `Race.csv` 追加了**阿斯兰(9)（后调整为 2~4）与阿纳缇(7) 2~6**，多胎种族实际为九族，测试/文档/update.log 已按九族记录（见 §12）
- 预计改动量：约 12 个代码/数据文件（`Race.csv` + `pregnancy_constant.py` + `egg_handle.py` + `pregnancy_handle.py` + `born_event_panel.py` + `game_type.py` + `save_handle.py` + `gift_panel.py` + `pregnancy_panel.py` + 前提常量/函数 2 文件 + ArkEditor `Premise.csv`）+ 文档 2 份 + update.log
- 风险等级：中低（不改 90/260/270 天孕程数值与单胎判定公式；多胎只在受精判定外层加"多轮循环"、在生产事件内层加"多次取名循环"；新增存档字段需回填。**中等风险点是 §3.3 多轮判定对 `check_fertilization` 的结构改造与 §3.5 生产事件的多子循环**）
- 适用代码快照：`master @ acdbc1c08`（工作区另有未提交的 plan_17 改动，本方案以工作区现状为准）
- 参考文档：`plan/done/plan_12_怀孕系统升级_方案.md`（生育方式列、卵生链、生产事件）、`plan/done/plan_14_怀孕系统四种药物.md`、`plan/done/plan_17_养成系统三种新药物.md`（逐婴儿育儿结算、常量文件、前提化、无头测试）、`.github/prompts/数据处理工作流/妊娠系统.md`
- 约束：本 Plan 的调查与实施全部由主代理自行完成，不调用子代理

---

## 1. 目标（用户需求原文整理）

1. **种族数据**：在 `Race.csv` 中将以下种族由单胎胎生 `1` 改为**多胎胎生 `2`**（用户订正，原需求写 12；12 已被"无壳卵生"占用），并**新增一列"多胞胎产胎数量"**（范围）：卡特斯 4~12、扎拉克 5~10、鲁珀 4~6、佩洛 3~6、菲林 2~5、乌萨斯 1~3。
2. **多胞胎受精判定**：受精判定时先从该种族的产胎数量范围内随机一个数 N，然后进行 N 轮判定。判定前先把当前总精液量存为临时值，每轮判定**无论成功失败**都把该临时精液量减少 30% 再进入下一轮，以此控制实际产胎数量。
3. **单轮判定逻辑**与单胎胎生的受精判定完全一致。
4. **判定结束后的提示**：与单胎一样有对应提示信息，但需适配多胎（本次受精成功的胎数）。在 `PREGNANCY` 中新增一个变量记录**本次胎生的生胎数量**。
5. **受精与妊娠阶段**与单胎胎生一致。
6. **生产事件**：事件描述需符合当前总怀孕数量；**取名需对每个孩子单独取名**。
7. **育儿阶段**与单胎胎生一致。
8. （v3 追加）**单胎胎生的同卵双胞胎**：单胎胎生（1）的受精事件中，受精成功后有 **1%** 概率为同卵双胞胎，之后也按多胞胎的胎生流程处理（胎数 2、生产时逐个取名），但其提示与事件文案需要**与多胎胎生（2）区分开**（同卵双胞胎 ≠ 多胎种族的一次多卵）。

## 2. 现状调查（已完成，均为实际代码核实结果）

### 2.1 Race.csv 与生育方式列的加载/使用链

- [Race.csv](data/csv/Race.csv) 现为 3 列 `cid,name,birth_type`，5 行表头（列名/中文说明/类型/翻译标记 `0,1,0`/表名），共 45 个种族（cid 0~44）。`birth_type` 说明为"生育方式(1单胎胎生,11带壳卵生,12无壳卵生)"；**2 未被使用**。
- 目标六族在 CSV 中的实际行：卡特斯(17)、**札拉克(31，用户写作"扎拉克"）**、鲁珀(20)、佩洛(22)、菲林(13)、乌萨斯(29)，当前均为 1。另有 `1,卡特斯/奇美拉,1`（拉普兰德专用混合种族）不在需求列表内，**经用户确认（v2）同样改为多胎，范围同卡特斯 4~12**，实际改动共七行。
- 加载：[game_config.load_race](Script/Config/game_config.py#L728) 把每行 `__dict__` 直接赋给 [config_def.Race](Script/Config/config_def.py#L1300)（字段 `cid/name/birth_type`）；`config_def.py` 由 `buildconfig.py` 按 CSV 表头自动生成，**新增列无需手写类定义**。第 4 行翻译标记决定该列是否提取到 PO，新列填 `0`。
- 统一入口 [egg_handle.get_birth_type](Script/System/Pregnancy_System/egg_handle.py#L27)：`getattr(race_config, "birth_type", 1)` 兜底缺列；**12 归一化为 1**；其余原样返回。
- 现有对 `birth_type` 的判定点（全部核实）：
  | 位置 | 判定 | 多胎（2）应有的行为 |
  | --- | --- | --- |
  | [pregnancy_handle.check_fertilization:259](Script/System/Pregnancy_System/pregnancy_handle.py#L259) | `!= 11` → 消费 `ovulation_flag` | 同胎生（消费） |
  | [pregnancy_handle.check_all_pregnancy:582](Script/System/Pregnancy_System/pregnancy_handle.py#L582) | `== 11` → 卵生链，否则胎生链 | 走胎生链（无需改） |
  | [egg_handle.py:251/:410](Script/System/Pregnancy_System/egg_handle.py#L251) | `!= 11` 早退 | 无需改 |
  | [gift_panel.py:527](Script/UI/Panel/gift_panel.py#L527)（妊娠加速药）/ [:548](Script/UI/Panel/gift_panel.py#L548)（假孕药） | `!= 1` → "种族不是胎生" | **须改为承认 2**（否则六族无法用 35/37 号药） |
  | [handle_premise_other.py:1201/:1214](Script/Design/handle_premise/handle_premise_other.py#L1201) `self/t_birth_type_egg` | `== 11` | 无需改 |
- `data/character/*.csv` 只存 `Race` 编号；[born_new_character:169](Script/Design/character_handle.py#L169) 让孩子**继承母亲种族**，即女儿也会是多胎种族。
- ArkEditor 副本 [tools/ArkEditor/csv/Race.csv](tools/ArkEditor/csv/Race.csv) **只有 `cid,name` 两列**（[load_csv.py:17](tools/ArkEditor/load_csv.py#L17) 仅用于种族名下拉），`birth_type` 本就未同步，新列也不需要同步。

### 2.2 受精判定 `check_fertilization` 与精液量/受精概率的关系

- **概率计算** [get_fertilization_rate:182](Script/System/Pregnancy_System/pregnancy_handle.py#L182)：读子宫精液 `dirty.body_semen[7][1]`（量 ml）与 `[7][2]`（等级），基础概率 `now_rate = (semen_count/1000)^2 * 100 + semen_level * 5`；假孕/事前药/事后药清零；再乘生理周期倍率 `config_reproduction_period[period].type`；最后 `round(…,2)` 写入 `pregnancy.fertilization_rate`。调用时机：每次体内射精（[ejaculation_panel.py:437](Script/UI/Panel/ejaculation_panel.py#L437)）、玩家睡眠结算 [check_all_pregnancy:579](Script/System/Pregnancy_System/pregnancy_handle.py#L579)、0 点兜底 [past_day_settle.py:66](Script/Settle/past_day_settle.py#L66)。
- ⚠ 顺带核实到一个**既有问题**（不在本方案范围内，仅记录）：排卵促进药 ×5、催眠强制排卵 ×5、浓厚精液 ×2 三段（:225-241）把结果写进 `pregnancy.fertilization_rate` 却**不更新局部变量 `now_rate`**，而函数末尾 `fertilization_rate = now_rate` 会把它们覆盖掉——三种加成实际无效。多胎方案的每轮概率以 `fertilization_rate` 为基准按精液比例缩放（§3.3），**不依赖也不修复**该问题（见 §9）。
- **判定** [check_fertilization:247](Script/System/Pregnancy_System/pregnancy_handle.py#L247) 的顺序：`ovulation_flag` 门 → 胎生消费标记 → **清空 6/7 号部位精液**（判定前！）→ 清强制排卵 → 已受精(20/21/22)早退 → `fertilization_rate` 非零时：未初潮 / 假孕 / 无生育模组机械 三个豁免分支带文案 → `random.randint(1,100) <= fertilization_rate` 成功：三行提示 + `talent[20]=1` + `fertilization_time` + `acceleration_days=0` + 无意识妊娠 `talent[35]` + 二段 `fertilization`；失败：提示 + 二段 `fertilization_failed` → `fertilization_rate=0` → `must_show_talk_check` + `WaitDraw` 输出 → 成就 706/708。
- 关键事实：**精液量在判定之前就被清零**，因此"总精液数量的临时值"必须在清零前读取 `body_semen[7][1]`；且 `fertilization_rate` 已把精液量折算进去，多轮判定需要按"临时精液量"重新推导每轮概率（§3.3）。

### 2.3 受精提示（二段行为口上与系统消息）

- 系统提示即 §2.2 中的 `draw_text`（"博士的精子与{0}的卵子结合，成功在子宫里着床了"/"{0}获得了[受精]"/失败文案），一次 `WaitDraw` 输出。
- 口上：二段行为 [Behavior_Data.csv:679-680](data/csv/Behavior_Data.csv#L679) `1311 fertilization` / `1312 fertilization_failed`（trigger npc，效果 998 必须显示）；系统口上 [second_pregnancy.csv](data/talk/system/second_pregnancy.csv) 按外表年龄 102~108 分支，另有 9 个角色专属口上文件含 `fertilization` 行。口上文本均为"卵子"单数叙述——多胎不新增二段行为，沿用同一口上；如需差分，可加前提（§3.4、§11）。

### 2.4 受精→妊娠→临盆→生产链的数据依赖

- [check_pregnancy:341](Script/System/Pregnancy_System/pregnancy_handle.py#L341)（≥90 天 → 21/26/27、乳汁上限）、[check_near_born:376](Script/System/Pregnancy_System/pregnancy_handle.py#L376)（≥260 天 → 22 临盆）、[check_born:406](Script/System/Pregnancy_System/pregnancy_handle.py#L406)（超期每天 +20% → `Born_Panel`）均只看 talent 与天数，**不感知胎数**，多胎可完全复用（需求 5）。
- 阶段展示 [pregnancy_panel.get_stage_info_text:60](Script/System/Pregnancy_System/pregnancy_panel.py#L60) 受精/妊娠/临盆三段文案只含日期，可追加"（N 胞胎）"。

### 2.5 生产事件 `Born_Panel`（事件描述、取名、新角色创建、亲子关系写入）

- [born_event_panel.Born_Panel._draw_born_event_content](Script/System/Pregnancy_System/born_event_panel.py#L74)：移动到住院区 → 选大夫 → 内循环 1（二段 `born` + 口上 + "目送她被推入产房" + `[焦急等待]`）→ 内循环 2：文案"{大夫}告诉你{母亲}生了**一个**可爱的女儿，母女平安"→ `character.input_name_func(" 你决定给女儿取名为——")` → `character_handle.born_new_character(mother, name)` → `child.pregnancy.born_time = game_time` → "孩子的名字叫做{0}，她是{1}的第{2}个孩子，也是{3}的第{4}个孩子" → `break` → 产后结算（二段 `postpartum`、22→23、26 清、`acceleration_days=0`、经验/能力）→ 成就 707。
- 内循环 2 本身就是 `while 1: … break` 结构，**改成按胎数循环取名只需把 `break` 换成计数**；产后结算块在循环外执行一次，天然符合"一次生产多子"。
- [born_new_character:155](Script/Design/character_handle.py#L155)：每调用一次生成一个 adv 9000~9999 的新模板、继承母亲种族与可遗传素质、把孩子 append 到玩家与母亲的 `child_id_list`、**记录"第一次分娩"特殊履历**（[first_record_handle.record_first_special_record(mother, 2, name)](Script/Design/character_handle.py#L196)，履历只记第一次，多次调用幂等）、`init_character`、婴儿 unnormal flag。**多次调用无副作用冲突**，孩子按出生顺序追加进 `child_id_list`。
- `input_name_func`（[character.py:113](Script/Design/character.py#L113)）带重名校验（"已有角色使用该姓名"），多子逐个取名不会重名。

### 2.6 育儿链对多个孩子的兼容情况

- [check_rearing:423](Script/System/Pregnancy_System/pregnancy_handle.py#L423) 取 `child_id_list[-1]`（最新一个孩子）算产后天数——多胞胎同一时刻出生，取最后一个与取任意一个等价，提示文案只点名一个孩子（可改为列出全部本胎孩子，§3.6）。
- [check_rearing_complete:494](Script/System/Pregnancy_System/pregnancy_handle.py#L494) 已在 plan_17 改为**逐婴儿**结算（`get_baby_id_list` 遍历母亲名下所有 101 婴儿），母亲名下仍有婴儿则保留 24/27；`check_grow_to_loli/girl` 以孩子为主体。**多胞胎无需改动育儿链**（需求 7）。
- 谱系图 `family_tree_draw` 以 `child_id_list` 为数据源，本就支持一母多子（plan_12 v8 已覆盖"每母多子"极端场景）。
- [debug_panel.py:1763](Script/UI/Panel/debug_panel.py#L1763) 调试项"最新孩子出生时间 -1 年"取 `child_id_list[-1]`，多胞胎下只回拨一个孩子——调试用途，不改。

### 2.7 `PREGNANCY` 结构与存档回填

- [game_type.PREGNANCY](Script/Core/game_type.py#L310)：`fertilization_rate/reproduction_period/ovulation_flag/fertilization_time/born_time/milk/milk_max/unconscious_fertilization/lactation_flag/eggs/next_egg_id/acceleration_days/growth_acceleration_days`。没有胎数字段。
- 旧存档回填先例 [save_handle.py:276-289](Script/Core/save_handle.py#L276)：`hasattr` 缺失即补默认值，新字段照加一行。

### 2.8 其他引用点

- 受精概率显示：[dirty_panel.py:290](Script/UI/Panel/dirty_panel.py#L290)、[physical_check_and_manage.py:921](Script/UI/Panel/physical_check_and_manage.py#L921)、debug 面板——只显示概率，不涉及胎数；体检报告可选追加胎数（§9 范围外）。
- 前提 CSV：[tools/ArkEditor/csv/Premise.csv:1983-1984](tools/ArkEditor/csv/Premise.csv#L1983) `self_birth_type_egg/t_birth_type_egg` 归类"生育"；[constant_promise.py:3910](Script/Core/constant_promise.py#L3910) 对应常量。新前提照此格式追加。
- 常量文件 [pregnancy_constant.py](Script/System/Pregnancy_System/pregnancy_constant.py)：分组 1~6，生育方式编号目前散落为字面量 `1/11/12`，本方案顺带收成枚举（§4）。
- 无头测试先例：plan_17 的 `scratchpad/test_plan17.py`（stub `rhodes_island`、fixture 需 talent 121 等），本方案新建 `test_plan18.py` 复用其框架。

## 3. 设计决策

### 3.1 生育方式编号 2 的加入与 `get_birth_type` 的语义

- `Race.csv` 表头说明改为"生育方式(1单胎胎生,2多胎胎生,11带壳卵生,12无壳卵生)"；六族改 2。
- `get_birth_type` 不做归一化（2 原样返回，12 仍归一化为 1）。新增判断函数 `egg_handle.is_viviparous(character_id) -> bool`（返回 `birth_type in (1, 2)`，胎生），`gift_panel` 两处 `!= 1` 改为 `not is_viviparous(...)`；`egg_handle.is_multiple_birth(character_id) -> bool`（`== 2`）供受精判定与面板使用。
- 编号收进 `pregnancy_constant`：`BIRTH_TYPE_SINGLE=1 / BIRTH_TYPE_MULTIPLE=2 / BIRTH_TYPE_EGG=11 / BIRTH_TYPE_EGG_SOFT=12`，`egg_handle/pregnancy_handle/handle_premise_other` 中的字面量替换为常量（等价替换）。

### 3.2 产胎数量列的 CSV 表达与解析

- `Race.csv` 新增第 4 列 `multiple_birth_num`（str，翻译标记 0），说明"多胞胎产胎数量范围(最小~最大，非多胎种族填1~1)"。**全部 45 行都必须有值**（buildconfig 会删除空值字段导致对象缺属性，见妊娠系统.md §2 既有备注），非多胎种族一律填 `1~1`。六族：`4~12 / 5~10 / 4~6 / 3~6 / 2~5 / 1~3`；`1,卡特斯/奇美拉` 同卡特斯 `4~12`（v2 确认）。
- 解析函数 `pregnancy_handle.get_multiple_birth_range(character_id) -> tuple[int, int]`：`getattr(race_config, "multiple_birth_num", "1~1")`，按 `~` 拆分取整、`min<=max` 且都 ≥1 否则回退 `(1, 1)`；非多胎种族直接返回 `(1, 1)`（不依赖 CSV 内容）。
- 选择 str 单列而非两列 int：符合需求"增加一列"，且与 `Commission.csv` 等既有"范围写在 str 列里"的先例一致。

### 3.3 多轮受精判定算法

把 `check_fertilization` 中"正常情况下可以受精"分支的**单次随机判定**抽成内部函数，外层按胎数循环，其余（标记消费、清精液、豁免分支、绘制、成就）保持原位：

1. 在清空 6/7 号部位精液**之前**读取 `semen_total = body_semen[7][1]`、`semen_level = body_semen[7][2]` 作为临时值（需求 2 的"总精液数量临时值"）。
2. 胎数上限 `N = random.randint(*get_multiple_birth_range(id))`；单胎种族 N=1（走完全相同的循环，行为与现状等价）。
3. 每轮概率：`rate_i = fertilization_rate * base(semen_i) / base(semen_total)`，其中 `base(x) = (x/1000)^2*100 + semen_level*5` 即 §2.2 的基础公式（抽成模块函数 `get_base_fertilization_rate(semen_count, semen_level)` 供 `get_fertilization_rate` 与本处共用）；`semen_0 = semen_total`，每轮结束后 `semen_i *= (1 - MULTIPLE_BIRTH_SEMEN_DECAY)`（衰减 30%）。`base(semen_total)==0` 时（调试直接改概率等情况）每轮用原 `fertilization_rate` 不缩放。这样第 1 轮与现状完全一致（需求 3），后续轮次概率随精液衰减自然下降，避孕/周期/假孕等修正因为已折进 `fertilization_rate` 而对每轮同样生效。
4. 每轮 `random.randint(1,100) <= rate_i` 成功则 `success += 1`；无论成败都进入下一轮，直到 N 轮结束。
5. 结果：`success >= 1` → 原成功分支的全部副作用（20、`fertilization_time`、`acceleration_days=0`、无意识妊娠、二段 `fertilization`）执行**一次**，并写 `pregnancy.fetus_count = success`；`success == 0` → 原失败分支。
6. 多胎种族追加过程提示（§3.4）；`fertilization_rate` 判定后照旧清零。

### 3.4 受精提示适配

- 单胎种族文案不变。多胎种族在"※※※"块内追加：
  - 成功：`"\n{0}的卵巢一次排出了{1}颗卵子，其中{2}颗成功受精，{0}怀上了{2}胞胎\n"`（`success==1` 时改为"其中1颗成功受精"，不写"胞胎"）；
  - 失败：`"\n{0}的卵巢一次排出了{1}颗卵子，但没有一颗成功受精\n"`。
- 妊娠/临盆提示（`check_pregnancy`/`check_near_born`）在 `fetus_count >= 2` 时把"正在孕育的新生命"句追加"（{N}胞胎）"提示一行：`"\n{0}腹中孕育着{1}个孩子\n"`。
- 口上：不新增二段行为。新增 4 个前提供口上差分（默认实装，见 §11）：`self_birth_type_multiple` / `t_birth_type_multiple`（种族是多胎胎生）、`self_multiple_fetus` / `t_multiple_fetus`（`fetus_count >= 2`，即当前怀着多胞胎）。本期**不写**差分口上文本，只提供前提。

### 3.5 生产事件的多子描述与逐个取名

- `Born_Panel` 非卵模式读取 `born_count = max(1, mom.pregnancy.fetus_count)`（旧存档/单胎为 0 或 1 → 1）。
- 内循环 2 文案按 `born_count` 分支：1 → 原文；≥2 → `"…告诉你{1}生了{2}个可爱的女儿，母女平安"` / `"{0}躺在床上，怀里抱着{1}个婴儿，对着你微微一笑，催促你逐个给孩子起名"`。
- 取名循环 `for born_index in range(born_count)`：询问文案 `" 你决定给第{0}个女儿取名为——"`（`born_count==1` 时保持原文），每个孩子调用一次 `born_new_character` + `born_time`，并各自输出"孩子的名字叫做{0}，她是{1}的第{2}个孩子…"。循环结束后再输出一次总结（≥2 时）：`"\n{0}一次生下了{1}个孩子：{2}\n"`（顿号连接的名字）。
- 产后结算块不变，末尾增加 `mom.pregnancy.fetus_count = 0`（与 `acceleration_days=0.0` 同处）。
- 卵生 `egg_mode` 分支不受影响（破壳恒为一枚卵一个孩子）。

### 3.6 产后/育儿链衔接

- `check_rearing` 保持取 `child_id_list[-1]` 算天数（同胎孩子出生时间相同）；提示"行动重心会以照顾{1}为主"改为列出**母亲名下全部婴儿**的名字（`get_baby_id_list`，顿号连接），单胎输出不变。
- `check_rearing_complete` 与后续成长链不改（§2.6）。

### 3.7 单胎胎生的同卵双胞胎（v3 追加）

- 触发点：`check_fertilization` 的 N 轮循环结束、`success >= 1` 的成功分支内，**仅当 `is_multiple_birth(id)` 为假**（单胎种族，N 恒为 1）时，额外 `random.randint(1, 100) <= IDENTICAL_TWINS_RATE`（常量 1，即 1%）→ `fetus_count = 2`、`identical_twins = True`。多胎种族不走此分支（其多胎来自多卵，不叠加同卵判定）。
- 与多胎胎生的区分完全靠 `PREGNANCY.identical_twins` 标记，而不是靠 `birth_type` 推断（女儿继承母亲种族，未来若有种族变更道具也不受影响）：
  | 环节 | 多胎胎生（2） | 同卵双胞胎（1 + 标记） |
  | --- | --- | --- |
  | 受精提示 | "卵巢一次排出了{N}颗卵子，其中{K}颗成功受精，怀上了{K}胞胎" | 原单胎成功三行文案之后追加 `"\n受精卵在着床后分裂成了两个胚胎，{0}怀上了同卵双胞胎\n"` |
  | 妊娠/临盆提示 | "腹中孕育着{N}个孩子" | `"{0}腹中孕育着一对同卵双胞胎"` |
  | 总览面板阶段文案 | "（{N}胞胎）" | "（同卵双胞胎）" |
  | 生产事件 | "生了{N}个可爱的女儿" / "怀里抱着{N}个婴儿…逐个起名" / 总结"一次生下了{N}个孩子" | `"…告诉你{1}生了一对同卵双胞胎女儿，母女平安"` / `"{0}躺在床上，怀里抱着两个一模一样的婴儿，对着你微微一笑，催促你分别给她们起名"` / 总结 `"\n{0}生下了一对同卵双胞胎：{1}与{2}\n"` |
  | 取名询问 | "你决定给第{0}个女儿取名为——" | `"你决定给双胞胎中的姐姐/妹妹取名为——"`（第 1 个为姐姐、第 2 个为妹妹） |
  | 前提 | `self/t_multiple_fetus`（`fetus_count>=2`，同卵双胞胎**也满足**） | 另加 `self/t_identical_twins`（标记为真）供口上细分 |
- 生命周期：受精成功时写入；生产结算清 `fetus_count` 时一并 `identical_twins = False`；`Born_Panel` 按 `identical_twins` 选择文案组，取名循环与多胎共用（`born_count = fetus_count = 2`）。
- 同卵双胞胎的两个孩子各自独立走 `born_new_character`（各随机 adv/职业/HP），本期不做外观/素质完全一致的处理（§9）。

## 4. 数据结构变更

| 位置 | 变更 |
| --- | --- |
| `game_type.PREGNANCY` | 新增 `fetus_count: int = 0`：本次胎生怀上的胎数（受精成功时写入；单胎种族写 1、同卵双胞胎写 2；生产结算后清零；卵生不使用）；新增 `identical_twins: bool = False`：本次为单胎种族的同卵双胞胎（受精时 1% 判定置位，生产结算后清除） |
| `save_handle.py` 回填 | `hasattr(pregnancy_data, "fetus_count")` 缺失补 0；`identical_twins` 缺失补 False |
| `pregnancy_constant.py` | 新分组 **7. 生育方式与多胎**：`BIRTH_TYPE_SINGLE=1`、`BIRTH_TYPE_MULTIPLE=2`、`BIRTH_TYPE_EGG=11`、`BIRTH_TYPE_EGG_SOFT=12`、`MULTIPLE_BIRTH_SEMEN_DECAY=0.3`（每轮临时精液量衰减比例）、`IDENTICAL_TWINS_RATE=1`（单胎种族受精成功后为同卵双胞胎的百分比概率） |
| `Race.csv` | 新列 `multiple_birth_num`（str）；六族 `birth_type` 1→2 |
| `constant_promise.Premise` | `SELF_BIRTH_TYPE_MULTIPLE="self_birth_type_multiple"`、`T_BIRTH_TYPE_MULTIPLE="t_birth_type_multiple"`、`SELF_MULTIPLE_FETUS="self_multiple_fetus"`、`T_MULTIPLE_FETUS="t_multiple_fetus"`、`SELF_IDENTICAL_TWINS="self_identical_twins"`、`T_IDENTICAL_TWINS="t_identical_twins"` |

## 5. 改动步骤（逐文件）

1. **`data/csv/Race.csv`**：表头 5 行各加一列（`multiple_birth_num` / 说明 / `str` / `0` / 空）；全部 45 行补 `1~1`；cid **1**/13/17/20/22/29/31 共七行的 `birth_type` 改 2 并填范围（1 号同 17 号填 `4~12`）。保持 CRLF、无 BOM。
2. **`pregnancy_constant.py`**：追加分组 7（§4），文件头分组说明同步。
3. **`egg_handle.py`**：`get_birth_type` docstring 更新（2 原样返回）、字面量改常量；新增 `is_viviparous`、`is_multiple_birth`。
4. **`pregnancy_handle.py`**：
   - 新增 `get_base_fertilization_rate(semen_count, semen_level)`，`get_fertilization_rate` 改为调用它（等价）；
   - 新增 `get_multiple_birth_range(character_id)`；
   - `check_fertilization` 按 §3.3 改造：清精液前记临时值；把成功/失败分支包进 N 轮循环；写 `fetus_count`；多胎提示；单胎种族成功后按 §3.7 做 1% 同卵双胞胎判定与提示；
   - `check_pregnancy` / `check_near_born` 追加多胎/同卵双胞胎提示行（按 `identical_twins` 二选一）；`check_rearing` 提示列出全部婴儿；
   - `check_all_pregnancy` 的 `== 11` 改用常量（等价）。
5. **`born_event_panel.py`**：§3.5 多子文案与取名循环，`identical_twins` 为真时换用 §3.7 的双胞胎文案组（姐姐/妹妹取名）；产后结算清 `fetus_count` 与 `identical_twins`。
6. **`game_type.py`** / **`save_handle.py`**：§4 两个字段与回填。
7. **`gift_panel.py`**：35/37 号药的胎生判定改 `egg_handle.is_viviparous`，文案不变。
8. **`pregnancy_panel.py`**：`get_stage_info_text` 受精/妊娠/临盆三段在 `fetus_count >= 2` 时追加"（{N}胞胎）"，`identical_twins` 为真时改为"（同卵双胞胎）"。
9. **前提**：`constant_promise.py` 6 个常量；`handle_premise_other.py` 6 个函数（紧随 `handle_t_birth_type_egg` 之后，同风格，`fetus_count` 经 `getattr` 兜底 0）；`tools/ArkEditor/csv/Premise.csv` 在 1984 行后追加 6 行（分类"生育"）。
10. **文档**：见 §10。
11. **update.log**：v0.66 块 `新增：` 段追加 1 条（面向玩家）：`新增：（怀孕）新增了多胎胎生的生育方式，卡特斯、卡特斯/奇美拉、札拉克、鲁珀、佩洛、菲林、乌萨斯七个种族改为多胎胎生，受精时按种族的产胎数量范围进行多轮受精判定，每轮判定后精液量衰减30%，成功受精的数量即为本次怀上的胎数，生产时会逐个为孩子取名`；再追加 1 条：`新增：（怀孕）单胎胎生的干员在受精成功时有1%的概率怀上同卵双胞胎，同样会生产两个孩子并逐个取名`。

## 6. 构建与本地化

- 改了 `Race.csv` → 需 `python buildconfig.py` 全量重建（重新生成 `config_def.Race` 与 `data.json`）；`auto_build_config` 增量也会覆盖 CSV 变化，但为保险执行全量。
- 新增/修改的 `_()` 文案需用户后续 `buildpo` / `buildmo`。
- 不改 talk CSV、不新增行为/道具。

## 7. 验证清单

### 7.1 单元/无头测试（`scratchpad/test_plan18.py`，复用 plan_17 框架）

1. 构建后 `game_config.config_race[17].birth_type == 2`、`multiple_birth_num == "4~12"`，`config_race[1]` 同；`config_race[0].multiple_birth_num == "1~1"`；全部 45 行都有该属性。
2. `get_multiple_birth_range`：卡特斯 → (4,12)；博士/黎博利 → (1,1)；伪造 `"abc"` / `"5~3"` → (1,1)。
3. `is_viviparous`：1/2 → True，11 → False，12 → True（归一化后）；`is_multiple_birth` 仅 2 为 True。
4. `get_base_fertilization_rate` 与改造前 `get_fertilization_rate` 数值逐点一致（回归）。
5. `check_fertilization` 多轮：固定 `random.seed`、把 `random.randint` 打桩为可控序列——
   - 单胎种族：行为与改前完全一致（1 轮），`fetus_count == 1`；
   - 多胎种族 N=5、序列全成功 → `fetus_count == 5`、talent20=1、只触发一次 `fertilization` 二段；
   - N=5、全失败 → talent20=0、`fetus_count == 0`、触发 `fertilization_failed`；
   - 精液衰减：断言第 i 轮传入的概率等于 `rate * base(s*0.7^(i-1)) / base(s)`；
   - 临时精液在清零前读取（判定后 `body_semen[7][1] == 0` 但循环用的是原值）。
6. 豁免分支（未初潮/假孕/机械）对多胎种族同样早退且 `fetus_count` 不变。
6a. 同卵双胞胎（v3）：单胎种族、判定成功、把 1% 判定的 `randint` 打桩为命中 → `fetus_count == 2`、`identical_twins == True`、提示含"同卵双胞胎"且不含"胞胎"以外的多胎文案；打桩为未命中 → `fetus_count == 1`、标记 False；多胎种族即使打桩命中也**不**置位标记。
7. `Born_Panel`：把 `input_name_func` 与 `flow_handle.askfor_all` 打桩，`fetus_count=3` → `born_new_character` 调用 3 次、母亲与玩家 `child_id_list` 各 +3、三个孩子 `born_time` 相同、结算后 `fetus_count == 0`、母亲 22→23；`fetus_count=0`（旧存档）→ 1 次；`fetus_count=2, identical_twins=True` → 2 次取名、询问文案含"姐姐"/"妹妹"、事件文案含"同卵双胞胎"、结算后标记清除。
8. `check_rearing` 三胞胎提示包含三个名字；`check_rearing_complete` 逐个成长（回归 plan_17 断言）。
9. `get_stage_info_text` 在 `fetus_count=3` 时含"3胞胎"，单胎不含。
10. 旧存档回填：删除属性后调用回填 → `fetus_count == 0`、`identical_twins == False`。
11. gift_panel 35/37 号药对种族 2 的目标不再报"不是胎生"。
12. 前提：6 个函数在 (种族 2, fetus 3) / (种族 1, fetus 0) / (种族 1, fetus 2, 同卵) 下返回预期真假（同卵双胞胎同时满足 `multiple_fetus` 与 `identical_twins`）。

### 7.2 游戏内测试（用户执行）

- 用 debug 面板把一名卡特斯干员受精概率设为 100、子宫精液量给足，睡觉触发排卵日 → 观察多轮提示与胎数；
- 用妊娠加速药推进到临盆 → 生产事件逐个取名、产后提示；
- 怀孕总览面板显示"（N胞胎）"；谱系图显示多子；
- 单胎种族（如萨卡兹）流程无变化；用 debug 面板反复受精可偶发验证 1% 同卵双胞胎（或临时把常量改为 100 验证文案）。

## 8. 风险与回滚

- `check_fertilization` 结构改造：以"单胎种族 N=1 时逐行等价"为回归底线（7.1-5），任何差异视为缺陷。
- `Race.csv` 新列漏填会导致 `config_race[x]` 缺属性 → `get_multiple_birth_range` 用 `getattr` 兜底，另在测试 1 中全表断言。
- 生产事件多次取名中途（web/tk 输入）异常：`Born_Panel.draw` 已有 `finally` 清理子面板；取名循环内不持有中间状态，重进事件会从头开始（与现状一致）。
- 回滚：全部改动可由 git 单次还原；存档新字段为纯附加，旧版本读取新存档只是多一个未用属性。

## 9. 范围外

- §2.2 记录的 `get_fertilization_rate` 三种加成被覆盖的既有问题（另立修正）。
- 无壳卵生 12 仍未实装。
- 体检报告/污浊面板显示胎数；多胎/同卵双胞胎专属口上文本；同卵双胞胎两个孩子的外观/素质完全一致化；多胎对孕肚外观/乳汁上限的差异；按胎数区分的生产难度或事件分支。

## 10. 文档同步

- `.github/prompts/数据处理工作流/妊娠系统.md`：§2 生育方式增加 `2` 多胎胎生的说明、六族名单、`multiple_birth_num` 列与"全行有值"要求、`is_viviparous/is_multiple_birth`；§3 对照表受精判定行注明多胎多轮；胎生链说明补 `fetus_count` 生命周期与生产事件多子取名；外部调用表补新前提。
- `plan/done/plan_12_怀孕系统升级_方案.md` §10 后续修改追加一条（生育方式编号 2 加入、`!= 1` 判定改 `is_viviparous`）。
- 本文件 §12 记录实施过程。

## 11. 待确认口径（已于 2026-08-29 通过询问工具全部确认）

| # | 问题 | 确认结果 |
| --- | --- | --- |
| 1 | `1,卡特斯/奇美拉`（拉普兰德的混合种族）是否也改为多胎胎生 | **改为多胎，范围同卡特斯 4~12** |
| 2 | 种族名"扎拉克"在 CSV 中为"札拉克"(31) | 按该行处理（默认，未提出异议） |
| 3 | 是否实装 §3.4 的 4 个多胎前提（仅前提、不写差分口上） | **实装** |
| 4 | 每轮受精概率的推导方式 | **按比例缩放**（§3.3：第 1 轮用现有 `fertilization_rate`，后续轮按基础公式对衰减后精液量的比例缩放；不采用"每轮重算 `get_fertilization_rate`"） |
| 5 | 单胎种族受精成功时的 `fetus_count` | **写 1，生产后清零** |
| 6 | （v3）同卵双胞胎的判定范围与区分方式 | 默认：仅单胎种族（1）、受精成功后 1%、以 `identical_twins` 标记区分文案；多胎种族不叠加。取名顺序默认第 1 个为姐姐 |

## 12. 实施记录（2026-08-29）

### 12.1 落地明细

| 文件 | 改动 |
| --- | --- |
| `data/csv/Race.csv` | 新增第 4 列 `multiple_birth_num`（str，翻译标记 0，全 45 行有值，非多胎 `1~1`）；`birth_type` 说明补"2多胎胎生"；cid 1/13/17/20/22/29/31 改 2 并填范围（脚本），**阿斯兰(9) `2,2~4` 与阿纳缇(7) `2,2~6` 为用户实施中追加**。文件为 LF，保持不变 |
| `pregnancy_constant.py` | 新分组 7：`BIRTH_TYPE_SINGLE/MULTIPLE/EGG/EGG_SOFT`、`MULTIPLE_BIRTH_SEMEN_DECAY=0.3`、`IDENTICAL_TWINS_RATE=1` |
| `egg_handle.py` | `get_birth_type` 字面量改常量、docstring 补 2；新增 `is_viviparous()`、`is_multiple_birth()` |
| `pregnancy_handle.py` | 新增 `get_fetus_count_draw_text()`、`get_base_fertilization_rate()`（`get_fertilization_rate` 改为调用它，等价）、`get_multiple_birth_range()`；`check_fertilization`：清精液前记临时精液量/等级、成功/失败分支外套 N 轮循环（每轮概率按比例缩放、衰减 30%）、写 `fetus_count`、多胎提示、单胎成功后 1% 同卵双胞胎；`check_pregnancy`/`check_near_born` 追加胎数提示行；`check_rearing` 提示列出名下全部婴儿；`check_all_pregnancy` 卵生分流改常量 |
| `born_event_panel.py` | 非卵模式按 `fetus_count` 取 `born_count`（≥1），同卵双胞胎/多胞胎/单胎三组文案，取名 `for` 循环（姐姐/妹妹 或 第 N 个女儿），多子总结行；产后结算清 `fetus_count`、`identical_twins` |
| `game_type.py` / `save_handle.py` | `PREGNANCY.fetus_count=0`、`identical_twins=False` + 旧存档回填 |
| `pregnancy_panel.py` | 新增 `get_fetus_count_text()`，受精/妊娠/临盆三段后缀"（N胞胎）"/"（同卵双胞胎）" |
| `gift_panel.py` | 35/37 号药的胎生判定改 `egg_handle.is_viviparous` |
| `constant_promise.py` / `handle_premise_other.py` / ArkEditor `Premise.csv` | 6 个前提：`self/t_birth_type_multiple`、`self/t_multiple_fetus`、`self/t_identical_twins`（分类"生育"，CRLF） |
| `.github/prompts/数据处理工作流/妊娠系统.md` §2 | 生育方式 2、九族名单、`multiple_birth_num` 列约束、多胎判定流程、同卵双胞胎、前提 |
| `plan/done/plan_12_怀孕系统升级_方案.md` §10 | 追加编号 2 与 `is_viviparous` 说明 |
| `update.log` | v0.66 新增段追加 2 条（多胎胎生、同卵双胞胎） |

### 12.2 验证

- `buildconfig.py` 全量重建通过，`config_def.Race` 自动生成 `multiple_birth_num: str`。
- 无头测试 `scratchpad/test_plan18.py`（`timeout 300 ./.conda/python.exe -u …`）**67/67 通过**，覆盖 §7.1 全部 12 项：配置/范围解析/非法回退、`is_viviparous`/`is_multiple_birth`、基础概率回归、单胎 1 轮等价（randint 调用序列 `[(1,1),(1,100),(1,100)]`）、同卵双胞胎命中/未命中、多胎 N=5 全成/全败/成 1、按阈值探测三轮概率 `[50.0, 31.79, 22.86]` 递减且逐轮生效、未初潮早退、妊娠/临盆提示与面板后缀、`Born_Panel` 三胞胎 3 次取名/同卵姐妹取名/旧存档 1 次、育儿提示列三名、回填、35/37 号药对多胎种族放行。
- plan_17 回归 `test_plan17.py` **132/132 通过**。
- 测试中的打桩：`achievement_panel.achievement_flow`（成就结算需完整罗德岛资源 fixture）、`character.input_name_func`、`flow_handle.askfor_all`。

### 12.3 备注

- （2026-08-29，随 plan_19）`get_birth_type` 不再把 12 归一化为 1，因此 `is_viviparous(12族)` 由 True 变为 False（无壳卵生不怀孕，妊娠加速药/假孕药对其不可用）；`test_plan18.py` 中"12 True"的断言已改为"12 False"，回归 68/68。

- 需求原文的"七族"因用户追加阿斯兰、阿纳缇实际为九族；`1,卡特斯/奇美拉` 按 §11 确认口径同卡特斯。
- 口上：未新增二段行为与差分文本，仅提供前提；新增 `_()` 文案需 `buildpo`/`buildmo`。
- §2.2 记录的 `get_fertilization_rate` 三种加成被覆盖的既有问题未处理（§9）。
