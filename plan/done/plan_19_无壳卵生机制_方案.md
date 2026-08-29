# Plan 19（方案）：无壳卵生种族的生育机制（体外排卵 → 体外受精 → 孵化 → 生产）

> 本 Plan 拆分为两个文件：**本文件为纯方案**（需求、现状调查、设计决策、数据结构、风险、范围外、口径确认）；具体的逐文件改动步骤、构建、验证清单、回滚与实施过程记录见 `plan_19_无壳卵生机制_实施步骤与记录.md`（下文简称"实施文档"）。

- 状态：**已实施（2026-08-29，无头测试 83/83 通过，plan_17 回归 132/132、plan_18 回归 68/68 通过，见 §12 与实施文档 §6；第 1 次修改（卵块口径 + 女儿身份差分）后回归 83/83，见 §12.1；游戏内整体测试与 buildpo/buildmo 本地化步骤待用户执行）**
- 来源：用户需求 → 实装 `Race.csv` 中占位已久的无壳卵生（`birth_type=12`）生育方式
- 修订记录：
  - v0 —— 骨架：章节结构 + 目标整理（12 条需求原文）
  - v1 —— 现状调查（§2 全部为实际代码核实结果）+ 设计决策（§3）+ 数据结构（§4）+ 改动步骤（§5）+ 构建/验证/风险/范围外/文档同步 + §11 待确认口径
  - v2 —— 口径确认轮（2026-08-29）：①排卵概率表改为**普通 5 / 强 10 / 超强 15**（其他部位；阴道 ×2、子宫 ×4、子宫超强 100%）②体外受精不乘生理周期倍率 ③体外受精基础概率**含精液等级项**（level 取卵的 0~15 级污浊等级）④排卵日睡觉不清体内精液 ⑤身体栏保持“有交互对象才绘制”门限 ⑥三族旧存档中已在孕程的角色**读档时直接清除孕程素质** ⑦未受精卵判定后立即废弃。§3.3/§3.8/§4/§5/§7/§8/§11 已按确认结果改写
  - v3 —— 第二轮口径确认（2026-08-29）：⑧受精卵数量**不设上限**，但体外受精的精液等级项由每级 +5 改为**每级 +3** ⑨自慰（交互对象为自己）且场景有卵时**弹窗只列卵按钮 + “照常射出”按钮** ⑩排卵促进药/催眠强制排卵的 ×5 效果**保留到当日排卵机会结束**（命中排卵或离开排卵日时清除，判定本身不消耗）⑪怀孕总览面板**新增“体外卵待受精”阶段**。§3.3/§3.6/§3.8/§3.11(新)/§4/§5/§7/§11 同步
  - v4 —— 范围外逐项确认（2026-08-29）：⑫三个新二段行为的系统口上**按 102~108 全套外表年龄差分**编写（纳入本期）⑬体外卵不做图片/纸娃娃地文（确认不做）⑭体外卵不受其他 NPC 干扰（确认不做）⑮不提供收走体外卵的指令（确认不做）⑯**顺带修复 `get_fertilization_rate` 三种加成被覆盖的既有 bug**（纳入本期）。§3.4/§3.12(新)/§4/§5/§7/§9/§11 同步
  - v6 —— 第 1 次修改（2026-08-29）：①**无壳卵的形态口径改为"卵块"**——不是一枚卵，而是成百上千颗细小卵粒被大量黏稠凝胶包裹成的一大团/一大串（鱼籽式），受精即精液穿过凝胶层与卵粒结合；详细污浊 16 级文本、三个无壳二段行为的 120 条口上、游戏内提示/事件/面板/按钮文案全部按此改写（数据结构不变：一团卵块=`soft_eggs` 的一条，每轮成功=一颗受精卵粒回写 `eggs`） ②**全部 16 个妊娠类二段行为补"女儿身份"差分**（前提 `high_1&self_is_player_daughter`，各 5 条，共 80 条）。§3.4/§3.7/§3.10/§3.13 与 §12.1 同步
  - v5 —— 用户追加需求（2026-08-29）：口上年龄差分不限于无壳卵生——`second_pregnancy.csv` 中**全部妊娠类二段行为**（胎生 10 个 + 带壳卵生 3 个 + 本期新增 3 个）都补齐 102~108 七档外表年龄差分，**每个〈行为×年龄〉前提组合 5 条**；新增 §3.13 与口上规模表，§3.4/§4/§5/§7/§11 同步
- 预计改动量：约 20 个代码/数据文件（新增 `soft_egg_handle.py` + 2 个 ui_text CSV；改 `pregnancy_constant/egg_handle/pregnancy_handle/born_event_panel/pregnancy_panel`、`orgasm_settle/second_behavior/Second_effect/realtime_settle`、`ejaculation_panel/dirty_panel`、`game_type/save_handle/constant_effect/constant_promise/handle_premise_other`、`Behavior_Data/Behavior_Effect/dirty.csv/second_pregnancy.csv` + ArkEditor 副本）+ 文档 3 份 + update.log；口上 508 条为本期最大的文本工作量
- 风险等级：**中**（触及三条热路径：绝顶结算 `orgasm_settle_in_second_behavior`、射精面板 `Ejaculation_Panel`/`ejaculation_flow`、身体栏 `SeeCharacterBodyPanel`；新增玩家侧存档字典与卵字典新键；`get_birth_type` 取消 12→1 归一化会改变三族的既有行为——它们此前一直按单胎胎生在跑）
- 适用代码快照：`master @ acdbc1c08` + 工作区未提交的 plan_17/plan_18 改动（本方案以工作区现状为准）
- 参考文档：`plan/done/plan_12_怀孕系统升级_方案.md`（带壳卵生链、`eggs` 结构、鉴定/孵化/破壳、保育员、玩家持卵索引）、`plan/wait/plan_18_多胞胎机制.md`（多轮受精循环、精液衰减、多子生产事件）、`plan/done/plan_14_怀孕系统四种药物.md`（孵化加速药）、`.github/prompts/数据处理工作流/妊娠系统.md`、`射精面板系统.md`、`身体信息面板系统.md`
- 约束：本 Plan 的调查与实施全部由主代理自行完成，不调用子代理

---

## 1. 目标（用户需求原文整理）

1. **体外排卵机会**：无壳卵生干员在每个排卵日当天有一次体外排卵机会，`PREGNANCY` 中用一个 flag 记录该机会是否已使用。
2. **触发时机**：排卵日当天、机会未用、且与玩家同一位置时，该干员在**性绝顶**时有概率伴随一次**体外排卵二段行为**；执行后消耗机会（flag 置 False），直到下次进入排卵日再重置。
3. **触发概率**：任意部位的性绝顶都可触发，但绝顶程度须 ≥ 普通绝顶；阴道绝顶概率为其他部位的 2 倍、子宫绝顶为 4 倍；子宫超强绝顶时 100%。排卵促进药 / 立刻排卵（催眠）等原本作用于受精概率的效果，对无壳卵生改为提升排卵概率。
4. **排卵结算**：触发体外排卵时三个结算——大量体力消耗、大量气力消耗、**新结算：生成一枚该角色排出的体外无壳卵**。
5. **玩家侧数据**：`PLAYER_COLLECTION` 新增字典记录当前所有角色排出的体外无壳卵：排卵时间、排卵地点、卵上精液量。
6. **精液转移**：生成体外无壳卵时自动把该角色子宫与阴道部位 80% 的精液量转移到卵上，并打印提示：共转移了多少 ml，提示玩家在 **1 小时内**尽量多地射在该卵上以提高受精概率与受精卵数量。
7. **射精位置选择**：玩家字典非空且当前地点至少有一枚体外无壳卵时——即使玩家开了"自动选择射精位置"，也**强制手动选择**；射精位置面板在原有部位之外**追加当前地点的所有体外无壳卵**作为可选对象；选中卵时把精液加到该卵的精液量上。
8. **污浊显示**：同样条件下，无论交互对象是谁，身体栏对每枚卵各增加一行污浊信息，分普通/详细两档：普通只写精液量；详细参考 `data/ui_text/dirty_full_diff.csv` 子宫污浊描述，但改为 **0~15 级**。普通污浊文本加在 `data/ui_text/dirty.csv`，详细污浊单独建一个 `data/ui_text/` 下的新文件。0 级=无精液；1~10 级与部位精液等级判定一致（按最大 5000ml 比例）；超过 5000ml 后每 1000ml 加一级，15 级=10000ml 封顶，需在原 1~10 级描述基础上再补 5 级文本。
9. **体外受精判定**：每枚卵自排出起 ≥1 小时后开始受精计算，参考多胞胎的循环计算：按轮次计算、每轮精液量减 30%，但轮次**无限**，直到剩余精液量 <5ml 为止。体外受精难度更高：不受排卵药等效果影响；基础概率公式的除数由 1000 改为 **1500**。
10. **受精卵回写**：判定完成后，类似带壳卵生，把每枚已受精卵的数据转移到母亲 `PREGNANCY` 中（结构类似现有 `eggs`）。
11. **孵化与生产**：无壳卵生干员走与带壳卵生相同的孵化流程；类比破壳事件与多胞胎生产事件做无壳卵生的生产事件，为每个女儿起名；后续养育流程一致。
12. **药物与保育员**：孵化流程同样受孵化加速药影响；保育员同样照顾无壳卵生的卵。

## 2. 现状调查（已完成，均为实际代码核实结果）

### 2.1 生育方式 12 的现有处理与无壳卵生种族

- `Race.csv` 中 12 已填于 **安努拉(11)、阿戈尔(34)、海嗣(35)** 三行（`multiple_birth_num` 均为 `1~1`）。
- [egg_handle.get_birth_type](Script/System/Pregnancy_System/egg_handle.py#L27) 把 12 **归一化为 1**——三族目前实际按**单胎胎生**运行（会受精/妊娠/临盆/生产）。取消归一化后，所有 `get_birth_type` 调用点的行为都要重新核对（见 §3.1 表）。`pregnancy_constant.BIRTH_TYPE_EGG_SOFT = 12` 已在 plan_18 定义。
- 对生育方式的判定点（plan_18 后的现状）：`check_fertilization:259`（`!= EGG` 消费 `ovulation_flag`）、`check_all_pregnancy:582`（`== EGG` 卵生链否则胎生链）、`egg_handle.check_ovulation/replace_entertainment_for_eggs`（`!= 11` 早退）、`gift_panel` 35/37（`is_viviparous`，1 或 2）、前提 `self/t_birth_type_egg`（`== 11`）。

### 2.2 生理周期与排卵日：`reproduction_period` / `ovulation_flag`

- [pregnancy_handle.update_reproduction_period:692](Script/System/Pregnancy_System/pregnancy_handle.py#L692)：每日 0 点周期 0..6 循环 +1，推进到 **5（排卵日）** 时 `ovulation_flag = True`。
- 消费：胎生由 `check_fertilization` 消费（睡觉结算 `check_all_pregnancy` + 0 点兜底 [past_day_settle.py:66](Script/Settle/past_day_settle.py#L66)）；带壳卵生由 `check_ovulation` 消费。12 归一化为 1 后目前走胎生消费。
- 催眠"立刻排卵" [Settle/default.py:1696](Script/Settle/default.py#L1696)：`hypnosis.force_ovulation = True` 并**直接把 `reproduction_period` 设为 5**（不置 `ovulation_flag`）；排卵促进药 [item_effect.py:1496](Script/Settle/item_effect.py#L1496)：`h_state.body_item[10][1] = True`。

### 2.3 性绝顶的判定链

- 绝顶次数→二段行为在 [orgasm_settle.orgasm_settle_in_second_behavior:141](Script/Settle/orgasm_settle.py#L141)：按部位 `part_dict = {0:s,1:b,2:c,4:v,5:a,6:u,7:w,21:m,22:f,23:h}` 遍历，`judge_orgasm_degree(累计次数)` 得程度 0 小/1 普通/2 强/3 超强（强需敏感度 ≥3、超强需 ≥6 否则降级），触发 `{部位}_orgasm_{程度}` 二段行为；同一部位后面紧跟 **B 绝顶喷乳 / U 绝顶排尿** 的附加二段行为（`b_orgasm_to_milk` / `u_orgasm_to_pee`，[:302-309](Script/Settle/orgasm_settle.py#L302)）——**体外排卵的挂钩点就在这一段**（每部位一次、已知本部位本次的最高程度）。
- 该函数由 [second_behavior.check_second_effect](Script/Design/second_behavior.py#L108) 的 NPC 分支调用：顺序为 `second_behavior_effect(全部)` → `orgasm_judge` → `second_behavior_effect(orgasm_list, orgasm_settle_flag=True)`，其中 `orgasm_list` 是**进入函数时**已存在于 `second_behavior` 字典且 id 含 `orgasm` 的键。绝顶结算中新赋予的、id 不含 `orgasm` 的二段行为（如新增的 `lay_soft_egg`）不会在本轮被结算，需在该处**补一行显式结算**（§3.4）。
- 二段行为效果链走 `constant.settle_second_behavior_effect_data`（[second_behavior_effect:214-226](Script/Design/second_behavior.py#L214)），注册装饰器 `settle_behavior.add_settle_second_behavior_effect`，实现于 [Script/Settle/Second_effect.py](Script/Settle/Second_effect.py)，编号空间为 [constant_effect.SecondEffect](Script/Core/constant_effect.py#L1008)（210~620 已用，997/998/999 保留）。**已有** `DOWN_LARGE_HIT_POINT = 235` / `DOWN_LARGE_MANA_POINT = 236`（减少大量体力/气力）可直接复用为需求 4 的前两个结算。
- 二段行为定义 [Behavior_Data.csv](data/csv/Behavior_Data.csv)（`cid,行为id,说明,0,npc,二段结算`），效果链 [Behavior_Effect.csv](data/csv/Behavior_Effect.csv)（多个效果以 ` - ` 连接，如 `1511 - 1512 - 62`）。妊娠段 1311~1324 已用，**1316、1325~1330 空闲**。

### 2.4 排卵促进药 / 催眠立刻排卵 / 浓厚精液在受精概率中的现有作用

- [get_fertilization_rate:225-241](Script/System/Pregnancy_System/pregnancy_handle.py#L225)：排卵促进药 `body_item[10]` ×5（用后清）、催眠 `force_ovulation` ×5（用后清）、玩家浓厚精液 `talent[33]` ×2（不清）——均只对 `fertilization_rate` 生效（且如 plan_18 §2.2 所记，实际被末尾覆盖）。`check_fertilization` 开头也会清 `force_ovulation`。对 12 而言这两处都不再经过，可把这两个 flag 改为在体外排卵判定时消费（§3.3）。

### 2.5 射精面板

- 入口 [Ejaculation_Panel.draw:501](Script/UI/Panel/ejaculation_panel.py#L501)：目标为玩家自己 → 直接射；群交 → 选对象+选部位；**`base_setting[3]` 为 0（自动）** 且有插入位置 → 直接 `shoot_here(插入位置)`；否则 `draw_choose_part`。设置项 [System_Setting.csv:8](data/csv/System_Setting.csv#L8)（`3,base,每次射精时手动选择射在哪里`）。
- [draw_choose_part:592](Script/UI/Panel/ejaculation_panel.py#L592)：身体部位按钮（`part_can_choose` 过滤）+ 服装部位按钮，每 8 个换行，点击 → `shoot_here(part_cid, part_type)` → [ejaculation_flow:385](Script/UI/Panel/ejaculation_panel.py#L385)。
- `ejaculation_flow`：`common_ejaculation()` 出量 → 非避孕套时 `update_semen_dirty` + `calculate_semen_flow` + `get_fertilization_rate` + 文案；避孕套时精液进套；最后画文本 + 成就。射精量与 `cache.shoot_position` / `h_state.shoot_position_body` 的消费方：饮精经验（`in [2,15]`）、部位射精前提、`character_behavior:403` 每次行动后重置——**射在卵上时不设置这些字段即可**（保持 -1）。
- 其他调用方：`common_default.py:893`、`orgasm_settle.py:78`（玩家绝顶射精）、`normal_flow.py:95`、`check_locker_panel.py:510`、`Settle/default.py:6610`（口内 `ejaculation_flow(2,0,cid)`）。

### 2.6 身体栏污浊显示

- [dirty_panel.SeeCharacterBodyPanel](Script/UI/Panel/dirty_panel.py#L67) 由 [in_scene_panel.py:310](Script/UI/Panel/in_scene_panel.py#L310) 在 `cache.scene_panel_show[2] and pl.target_character_id` 时绘制（**没有交互对象时整个身体栏不画**）。
- 部位循环 [:124-233](Script/UI/Panel/dirty_panel.py#L124)：每部位 `body_semen[i][2]`（等级）非零 → 普通文本 `ui_text_data['dirty'][f"{部位}精液污浊{等级}"]`（一行 ` 部位文本`），详细（`draw_setting[10]`）→ 优先 `dirty_full_diff` 差分（[get_dirty_diff_text_cid:377](Script/UI/Panel/dirty_panel.py#L377)，子宫按 妊娠/受精/未初潮/未孕 分支）否则 `dirty_full`，格式 `  [部位]:<semen>文本</semen>\n`。循环后是腹部整体、灌肠等追加行——**卵的污浊行插在部位循环之后、腹部整体之前**即可。
- 等级换算 [attr_calculation.get_semen_now_level:717](Script/Design/attr_calculation.py#L717)：按部位 `max_volume`（[BodyPart.csv](data/csv/BodyPart.csv)：小穴 2000、子宫 **4000**）的 1%/5%/10%/20% 得 1~4 级，之后每 15% +1 级，≥max 为 10 级，上下限 1~10。卵的 0~15 级需要一个**以 5000 为基数**的独立换算（§3.7）。
- ui_text 文件由 [buildconfig.build_ui_text:358](buildconfig.py#L358) 按 `data/ui_text/*.csv` **自动全部加载**，键为文件名（`ui_text_data['dirty_full_diff']`），新文件无需注册；`context` 列全部提取到 PO。现有文件：`ability/condom_dirty/dirty/dirty_full/dirty_full_diff/h_state/text_ai_system_promote`。
- `dirty_full_diff.csv` 子宫描述现有 11 级（`子宫未孕精液污浊1~11`、`子宫未初潮精液污浊1~11`），可作为卵 1~10 级文案的改写底本，11~15 级需新写。

### 2.7 `PLAYER_COLLECTION` 与 `PREGNANCY.eggs`

- [PLAYER_COLLECTION](Script/Core/game_type.py#L906)：`held_eggs: Dict[int, tuple]`（索引）+ `next_held_egg_id`；回填于 [save_handle.py:295-298](Script/Core/save_handle.py#L295)。新字典照此加。
- [add_egg:69](Script/System/Pregnancy_System/egg_handle.py#L69) 卵字典键：`lay_time/identified/fertilized/identify_time/father_id/hatch_stage/held_by_player/acceleration_days`；`get_hatching_eggs` 取 `identified and fertilized and not held`；`get_hatch_day` 以 `lay_time` 为基准 + `acceleration_days`；孵化加速药 36 只看 `get_accelerable_hatching_eggs`，**不判种族**。

### 2.8 带壳卵生链对 11 的硬判定点

- `check_ovulation`（`!= 11` 消费标记后早退）、`replace_entertainment_for_eggs`（`!= 11` 早退）、`check_all_pregnancy`（`== 11` 走 `check_ovulation + check_egg_born`）。
- 状态机 [ENTERTAIN_TEND_EGGS:1659](Script/StateMachine/default.py#L1659) 与保育员 [WORK_NURSERY_CARE:1697](Script/StateMachine/default.py#L1697) 只查 `get_identifiable_eggs / get_hatching_eggs / any_hatching_eggs_exist`，**不判种族**；`have_need_tend_eggs` 同。→ 无壳卵只要进入 `pregnancy.eggs` 且 `identified=True`，照料/保育员/孵化药全部自动接入（需求 12）。
- [check_egg_born:338](Script/System/Pregnancy_System/egg_handle.py#L338)：每晚只处理**一枚**到期卵 → `Born_Panel(egg_mode=True, egg_id)`；`Born_Panel` 卵模式：删该卵、24 育儿=1、27 泌乳=1、经验 +1。无壳卵同一批次多枚受精卵同日到期，需要**批量破壳 + 逐个取名**（§3.10）。

### 2.9 多胞胎受精循环与可复用函数（plan_18）

- `get_base_fertilization_rate(semen_count, semen_level) = (count/1000)^2*100 + level*5`；`check_fertilization` 多轮：`rate_i = rate * base(s_i)/base(s_0)`，`s_{i+1} = s_i * 0.7`（`MULTIPLE_BIRTH_SEMEN_DECAY`）。体外受精按需求 9 改为"无限轮、<5ml 停、除数 1500、无药物/周期修正"，可写成独立函数，不复用 `fertilization_rate`。

### 2.10 体力/气力消耗结算先例

- 二段结算 `SecondEffect.DOWN_LARGE_HIT_POINT=235 / DOWN_LARGE_MANA_POINT=236`（[Second_effect.py:486-515](Script/Settle/Second_effect.py#L486)），直接挂在新二段行为效果链上即满足需求 4 前两项。

### 2.11 实时结算挂钩点（体外受精的 1 小时判定）

- 玩家阶段每轮结算末尾调用 [realtime_settle.judge_pl_real_time_data()](Script/Settle/realtime_settle.py#L59)（[character_behavior.py:157](Script/Design/character_behavior.py#L157)），现只做酒店退房——是"每次玩家行动后检查一遍全部体外卵是否满 1 小时"的天然位置。时间差用 `cache.game_time - lay_time`（`game_time.py` 只有按天的 `count_day_for_datetime`，小时级直接用 `timedelta.total_seconds()/3600`）。

### 2.12 口上与前提先例

- 系统口上 [second_pregnancy.csv](data/talk/system/second_pregnancy.csv)：`lay_egg`(31~35)、`egg_fertilized`(41~45)、`egg_born`(51~55) 各 5 条，前提 `high_1`。
- 前提 CSV 分类"生育"段 [Premise.csv:1983-1996](tools/ArkEditor/csv/Premise.csv#L1983)；实现在 `handle_premise_other.py:1201~1380`。
- 存档回填先例见 §2.7；卵字典新键用 `.get(键, 默认)` 兜底（`acceleration_days` 先例）。

## 3. 设计决策

### 3.1 生育方式 12 的语义变更

- `get_birth_type` **取消 12→1 归一化**，原样返回 12；`is_viviparous` 保持 `(1, 2)`（三族不再能用妊娠加速药/假孕药，因为它们不再怀孕）；新增 `is_egg_soft(cid)`（`== 12`）、`is_egg_layer(cid)`（`in (11, 12)`，需要照料卵/孵化的两类）。
- 调用点逐一处理：
  | 位置 | 改法 |
  | --- | --- |
  | `check_fertilization` | 开头新增：`is_egg_soft` → 消费 `ovulation_flag` 后 **return**（无壳卵生没有体内受精；体内精液**不清零**，任其自然吸收，v2 确认） |
  | `check_all_pregnancy` | `== EGG` → `is_egg_layer`：11 走 `check_ovulation + check_egg_born`，12 只走 `check_egg_born`（排卵在绝顶时发生） |
  | `check_ovulation` | 不改（仍只认 11） |
  | `replace_entertainment_for_eggs` | `!= 11` → `not is_egg_layer` |
  | 0 点兜底 `past_day_settle:66` | 不改（`check_fertilization` 对 12 会消费标记，`check_ovulation` 早退） |
  | 前提 `self/t_birth_type_egg` | 不改（带壳专用），新增 `self/t_birth_type_egg_soft` |

### 3.2 体外排卵机会 flag 的生命周期

- `PREGNANCY.external_ovulation_chance: bool`：`update_reproduction_period` 推进到 5 时置 True（与 `ovulation_flag` 同处），推进到其他值时置 False（机会过期）；体外排卵触发时置 False。
- 催眠"立刻排卵"把周期直接设为 5 但不经过 `update_reproduction_period` → 在 [Settle/default.py:1696](Script/Settle/default.py#L1696) 处对无壳卵生**同时置 `external_ovulation_chance = True`**（否则催眠对该种族无意义）。
- 触发条件（全部满足）：NPC（`character_id != 0`）、`is_egg_soft`、`reproduction_period == 5`、`external_ovulation_chance`、`handle_in_player_scene`、未初潮豁免（`handle_menarche_1` 为假）、机械无生育模组豁免。

### 3.3 绝顶触发体外排卵的概率模型

- 挂钩：`orgasm_settle_in_second_behavior` 每部位分支内、B 喷乳/U 排尿之后（此时本部位本次最高程度 `now_degree` 已定；释放态多次掷骰取最高）。新增 `soft_egg_handle.judge_external_ovulation(cid, orgasm_part, degree) -> bool`。
- 概率表（常量，v2 已确认）：
  | 程度 \ 部位 | 其他部位 | 阴道 V(4) ×2 | 子宫 W(7) ×4 |
  | --- | --- | --- | --- |
  | 小绝顶(0) | 0 | 0 | 0 |
  | 普通(1) | 5% | 10% | 20% |
  | 强(2) | 10% | 20% | 40% |
  | 超强(3) | 15% | 30% | **100%**（固定） |
- 药物/催眠改向：判定时 `body_item[10][1]`（排卵促进药）→ 概率 ×5；`hypnosis.force_ovulation` → ×5（两者对无壳卵生不再进入受精概率）；上限 100%。**判定本身不消耗药效**（v3 确认）：两个 flag 在体外排卵**命中**时随 `external_ovulation_chance` 一起清除，或在 `update_reproduction_period` 离开排卵日（机会过期）时清除；`check_fertilization` 开头对 `force_ovulation` 的清除对 12 族跳过（12 在更早处已早退，见 §3.1）。玩家浓厚精液 ×2 **不**移植（它是精液属性，与排卵无关）。
- 同一次绝顶结算内多个部位都可能命中：`external_ovulation_chance` 在首次命中时立即置 False，后续部位自然不再触发，保证每排卵日至多一枚。
- 命中 → `character_get_second_behavior(cid, "lay_soft_egg")`；在 `check_second_effect` NPC 分支的绝顶结算之后补一行 `second_behavior_effect(cid, change_data, ["lay_soft_egg"])`，让三项结算与口上在**本轮**完成（§2.3 所述的列表时序问题）。

### 3.4 体外排卵二段行为与三项结算

- `Behavior_Data.csv` 新增 `1325,lay_soft_egg,结算体外排出无壳卵,0,npc,二段结算`；`Behavior_Effect.csv`：`1325,lay_soft_egg,235 - 236 - 621 - 998`（大量体力、大量气力、生成体外无壳卵、必须显示）。
- 新二段结算 `SecondEffect.LAY_SOFT_EGG = 621`（紧接 620），实现于 `Second_effect.py`，逻辑委托 `soft_egg_handle.lay_soft_egg(cid)`：
  1. 在 `pl_collection.soft_eggs` 新建卵：`{"mother_id", "lay_time": game_time, "position": list(母亲位置), "semen_count": 0.0}`，编号取 `next_soft_egg_id`；
  2. 精液转移：`transfer = (body_semen[6][1] + body_semen[7][1]) * SOFT_EGG_SEMEN_TRANSFER_RATE(0.8)`，两部位各扣 80%（`[1]` 减量、`[2]` 用 `get_semen_now_level` 重算，不动累计 `[3]`），卵 `semen_count += transfer`；
  3. `WaitDraw` 提示：`"\n{母亲}的体内排出了一枚无壳的卵，子宫与小穴中的{X}ml精液随之附着在了卵上\n请在1小时内尽量多地把精液射在这枚卵上，精液越多，卵受精的概率与受精卵的数量就越高\n"`（X=0 时改为"卵上还没有任何精液"）。
- 口上（v5 口径）：`second_pregnancy.csv` 为 `lay_soft_egg` / `soft_egg_fertilized` / `soft_egg_born` 各写 **通用 `high_1` 5 条 + 102~108 七档外表年龄各 5 条** = 40 条，三个行为共 120 条（前提 `high_1&CVP_A1_T|10X_G_0`，与既有 `fertilization` 2~8 行同构）；文案视角：102/103 稚嫩懵懂、104 少女、105 适龄、106 成熟、107 熟妇、108 长生者，无壳卵的质感（半透明卵膜、凝胶状）贯穿各档。既有妊娠类二段行为的补齐见 §3.13。

### 3.5 体外无壳卵的数据结构与工具函数（新模块 `soft_egg_handle.py`）

- `PLAYER_COLLECTION.soft_eggs: Dict[int, dict]` + `next_soft_egg_id: int`（§4）。
- 工具：`get_soft_eggs_in_scene(position) -> dict`（按 `position` 列表相等筛选）、`get_soft_egg_semen_level(count) -> int`（0~15，§3.7）、`add_semen_to_soft_egg(egg_id, count)`、`get_soft_egg_name(egg_id) -> "{母亲}排出的卵"`。

### 3.6 射精面板改造

- `Ejaculation_Panel.draw`：在“自动射精”分支之前插入 `if len(get_soft_eggs_in_scene(pl.position)): self.draw_choose_part()`（群交分支保持先选对象再选部位，卵按钮同样出现在部位面板中）。**交互对象为自己（自慰）** 且场景有卵时（v3 确认）：进入 `draw_choose_part(self_mode=True)`——不列身体/服装部位，只列卵按钮 + 一个 `[照常射出]` 按钮（点击走原来的 `shoot_here(6, 0)` 路径，行为与现状完全一致）。
- `draw_choose_part(self_mode: bool = False)`：服装按钮之后新增第三行“体外卵”按钮：`[卵{编号}]{母亲}排出的卵（{X}ml）` → `self.shoot_soft_egg(egg_id)`；`self_mode` 为真时跳过身体/服装两行，只画卵按钮与 `[照常射出]`。
- `shoot_soft_egg(egg_id)` → `ejaculation_flow(-1, 0, soft_egg_id=egg_id)`：`ejaculation_flow` 新增关键字参数 `soft_egg_id: int = -1`，非避孕套且 `soft_egg_id >= 0` 时**不走** `update_semen_dirty/calculate_semen_flow/get_fertilization_rate`，改为 `add_semen_to_soft_egg`，文案 `"在{母亲}排出的卵上{semen_text}"`；`cache.shoot_position`、`shoot_position_body` 保持不变（-1），避孕套分支照旧（精液进套）；成就照旧。
- 面板退出条件不变（选中即射、`now_panel_id` 回场景）。

### 3.7 身体栏污浊行

> v6 口径：显示名为"{母亲}排出的卵块"，详细行前缀 `[卵块]`，16 级文本以"凝胶包裹的成百上千颗卵粒"为形态基调（0 级洁净的胶质与卵粒 → 精液渗入凝胶、卵粒被浓白吞没 → 白浊堆山、卵粒在其中闪光）。

- 插入位置：部位循环结束后、腹部整体判定前；条件 `len(get_soft_eggs_in_scene(pl.position))`，对每枚卵各一行，与交互对象无关（身体栏本身仍受"有交互对象才绘制"的既有门限，§11-5）。
- 等级 `get_soft_egg_semen_level(count)`：`count <= 0 → 0`；`count < 5000 → 1~10`（复用 `get_semen_now_level` 的比例阶梯，基数 `SOFT_EGG_SEMEN_LEVEL_MAX_VOLUME = 5000`——把该函数的阶梯段抽成 `get_semen_level_by_volume(value, max_volume)` 供两处共用，等价重构）；`count >= 5000 → 10 + int((count-5000)/1000)`，上限 15。
- 普通污浊（`draw_setting[10]` 关）：`dirty.csv` 新增 `体外卵精液污浊,上面附着着{0}ml精液`，输出 ` {母亲}排出的卵上面附着着{X}ml精液`。
- 详细污浊：新文件 `data/ui_text/soft_egg_dirty_full.csv`（`cid,context` 五行表头同 `dirty.csv`），cid `体外卵精液污浊0` ~ `体外卵精液污浊15` 共 16 条：0 级"洁净无物"，1~10 级以 `子宫未孕精液污浊1~10` 为底本改写为"半透明的无壳卵浸在精液中"的视角，11~15 级新写（卵完全没入精液、精液堆成小丘……），输出 `  [体外卵]:<semen>{母亲}排出的卵：文本</semen>\n`。

### 3.8 体外受精判定

- 挂钩：`realtime_settle.judge_pl_real_time_data()` 末尾调用 `soft_egg_handle.check_soft_eggs_fertilization()`（每次玩家行动后）；`sleep_settle` 的 `check_all_pregnancy` 之前也调一次（长睡眠兜底）。
- 对每枚 `game_time - lay_time >= 1h` 的卵：
  ```
  semen = egg["semen_count"]; success = 0
  while semen >= SOFT_EGG_MIN_SEMEN(5):
      level = get_soft_egg_semen_level(semen)            # 卵的 0~15 级污浊等级（按当轮剩余精液量重算）
      rate = min(100, (semen / SOFT_EGG_RATE_DIVISOR(1500)) ** 2 * 100 + level * SOFT_EGG_LEVEL_RATE(3))
      if randint(1,100) <= rate: success += 1
      semen *= 1 - MULTIPLE_BIRTH_SEMEN_DECAY(0.3)
  ```
  不乘生理周期倍率、不看药物/催眠/浓厚精液（v2 确认）；等级项参照部位公式但改为 **`+level*3`**（v3 确认，不设受精卵数量上限、靠更低的等级加成收敛），level 用卵自身的 0~15 级换算（每轮按剩余精液量重算，衰减后等级随之下降）。
- 结果：`success` 枚 → 对母亲各调 `egg_handle.add_egg(mother, fertilized=True)` 并把该卵置 `identified=True, identify_time=now, lay_time=体外卵的 lay_time, soft=True`（孵化计时从体外排出起算，与带壳一致）；`success == 0` → 卵废弃。两种情况都从 `soft_eggs` 删除该卵，并 `WaitDraw`：`"{母亲}排出的卵在{X}ml精液的包裹下完成了受精，共有{N}枚卵受精，已送往育儿室孵化"` / `"…但没有一枚受精，卵失去了活性"`；受精时母亲二段 `soft_egg_fertilized`（1326，998）。
- 母亲不在场/被监禁均不影响（卵在玩家字典里，判定与母亲位置无关）。

### 3.9 接入孵化链、保育员、孵化加速药

- 受精卵已 `identified=True` → `get_hatching_eggs`/`have_need_tend_eggs`/`any_hatching_eggs_exist`/`get_accelerable_hatching_eggs` 全部直接生效；`replace_entertainment_for_eggs` 放行 12 后母亲每日照料卵（只会落入孵化分支，因为无未鉴定卵）；保育员无需改；孵化加速药 36 无需改；总览面板 `STAGE_HATCHING` 无需改。
- 卵字典新键 `soft: bool`（`.get("soft", False)` 兜底），供破壳事件选择文案与批量模式。

### 3.10 无壳卵生的生产事件

- `check_egg_born` 对 12：收集**全部**到期的孵化中卵（同批次受精卵 `lay_time` 相同必然同日到期）→ `Born_Panel(character_id, egg_mode=True, egg_id_list=[...])`；`egg_id` 参数改为 `egg_id_list`（带壳传单元素列表，兼容）。
- `Born_Panel` 卵模式：`born_count = len(egg_id_list)`，取名循环复用 plan_18 的 `for born_index in range(born_count)`；`soft` 卵换用无壳文案组（"半透明的卵膜破开"/"{N}个小小的身影相继从卵膜中挣脱出来"，询问"你决定给第{N}个女儿取名为——"），二段行为 `soft_egg_born`（1327，998）替代 `egg_born`；结算删除列表中全部卵、24/27/经验 +1（一次），总结行 `"{母亲}的{N}枚卵一同孵化了：{名字…}"`。

### 3.11 怀孕总览面板新增“体外卵待受精”阶段（v3 确认）

- `pregnancy_constant` 阶段枚举在 `STAGE_EGG_WAIT` 之后插入 `STAGE_SOFT_EGG_WAIT`，其后枚举顺延 +1（`STAGE_PREGNANCY=4 … STAGE_REARING=8`），`STAGE_NAME_LIST` 同位插入 `_("体外卵待受精")`。枚举值只在运行时用于排序/筛选，不进存档，顺延无兼容问题（实施时 grep 确认无硬编码数字）。
- 阶段判定 `get_chara_pregnancy_stage`：母亲在 `pl_collection.soft_eggs` 中有卵（`mother_id == cid`）→ 该阶段（优先级放在“持卵待鉴定”之后、“妊娠”之前，与枚举顺序一致）。
- `get_stage_info_text`：列出每枚卵 `"{地点}的卵（{X}ml，{N}分钟后判定）"`，多枚以顿号连接；已到判定时间但尚未结算的显示“即将判定”。地点文本用 `map_handle` 现有的场景名获取函数（实施时核对 `get_map_system_path_str_for_list` + `cache.scene_data[...].scene_name`）。

### 3.12 顺带修复 `get_fertilization_rate` 的加成覆盖 bug（v4 确认）

- 现状：[get_fertilization_rate:225-241](Script/System/Pregnancy_System/pregnancy_handle.py#L225) 三段加成各自算出 `new_rate` 写进 `pregnancy.fertilization_rate`，但**不更新局部 `now_rate`**，函数末尾 `fertilization_rate = round(now_rate, 2)` 把它们全部覆盖——排卵促进药 ×5、催眠强制排卵 ×5、浓厚精液 ×2 对胎生/带壳卵生一直无效。
- 修法：三处改为 `now_rate = new_rate`（提示文案里的"由{0}上升到{1}%"改用改前的 `now_rate` 作起点，避免显示旧值），其余逻辑不动；三种加成按现有顺序**连乘**（每步 `min(100, …)`）。plan_18 的多轮判定以 `fertilization_rate` 为基准按比例缩放，修复后自动继承加成。
- 影响：胎生/带壳卵生的受精概率在用药/催眠/浓厚精液时真正提高（行为变化，update.log 记"修正"）；无壳卵生不经过该函数（§3.1），不受影响。

### 3.13 妊娠类二段行为口上补齐 102~108 年龄差分（v5 追加）

> v6 追加：每个行为再补一组**女儿身份**差分（前提 `high_1&self_is_player_daughter`，5 条；口吻为女儿对父亲，与年龄差分并列、不叠加年龄前提），16 个行为共 80 条；三个无壳行为的口上按"卵块/卵粒/凝胶"口径全部重写。

- 现状（按前提 token 统计 [second_pregnancy.csv](data/talk/system/second_pregnancy.csv)，共 36 条）：`fertilization` 102~108 各 1 条、无通用；`fertilization_failed/parturient/born/postpartum/rearing/rearing_complete/child_to_loli/loli_to_girl` 各只有 1 条通用；`pregnancy` 6 条通用；`lay_egg/egg_fertilized/egg_born` 各 5 条通用；**没有任何行为具备完整的七档差分**。
- 口径：每个〈行为 × 年龄档〉前提组合补到 **5 条**（已有的计入，如 `fertilization` 各档补 4 条）；通用分支不在本次范围（`pregnancy` 6 条、卵生三者 5 条、其余 1 条维持现状）。
- 成长类两个行为的可达性：`child_to_loli` 触发时孩子已是 103 萝莉、`loli_to_girl` 触发时已是 104 少女（二段行为在素质变更后结算，口上前提读的是变更后的外表年龄），其余年龄档永不可达——只补**可达的一档各 5 条**（实施时若用户要求补全七档也可，但会是死文本）。
- 规模表：

| 行为 | 触发者视角 | 需补条数 |
| --- | --- | --- |
| fertilization | 母亲 | 7 档 × 4 = 28 |
| fertilization_failed | 母亲 | 7 × 5 = 35 |
| pregnancy | 母亲 | 35 |
| parturient | 母亲 | 35 |
| born | 母亲（产前） | 35 |
| postpartum | 母亲 | 35 |
| rearing | 母亲 | 35 |
| rearing_complete | 母亲 | 35 |
| child_to_loli | 孩子（已是 103） | 5 |
| loli_to_girl | 孩子（已是 104） | 5 |
| lay_egg / egg_fertilized / egg_born | 母亲 | 3 × 35 = 105 |
| lay_soft_egg / soft_egg_fertilized / soft_egg_born（新） | 母亲 | 3 × 40 = 120 |
| **合计** | | **508 条**（既有行为 388 + 新行为 120） |

- 写法：cid 从 2001 起连续编号（该文件 cid 只需文件内唯一），`adv_id=0`，前提 `high_1&CVP_A1_T|10X_G_0`，五列、`\n` 字面量、无 ASCII 逗号；同一组合的 5 条在情绪/动作/侧重上互不重复；各年龄档文案基调沿用既有 `fertilization` 2~8 行（102 稚嫩、103 娇小、104 健康少女、105 适龄、106 成熟、107 熟妇、108 长生者）。
- 文本生成方式：由主代理直接撰写（本 Plan 约束不用子代理），分行为批量写入脚本，写完后用前提 token 计数断言逐组合 = 5。

## 4. 数据结构变更

| 位置 | 变更 |
| --- | --- |
| `game_type.PREGNANCY` | `external_ovulation_chance: bool = False`（本排卵日的体外排卵机会） |
| `game_type.PREGNANCY.eggs[*]` | 新键 `soft: bool`（无壳卵，`.get` 兜底 False） |
| `game_type.PLAYER_COLLECTION` | `soft_eggs: Dict[int, dict] = {}`（键自增；值 `mother_id/lay_time/position/semen_count`）、`next_soft_egg_id: int = 0` |
| `save_handle.py` 回填 | 上述三个属性；**并对生育方式为 12 的角色做一次性孕程清理**（v2 确认：持有 talent 20/21/22 任一者清 20/21/22/26/35，`fetus_count=0`、`identical_twins=False`、`acceleration_days=0`，并 `settle_chara_unnormal_flag(cid, 2)` 刷新异常位；23 产后/24 育儿/27 泌乳保留，已出生的孩子不受影响） |
| `pregnancy_constant.py` 新分组 8 | `EXTERNAL_OVULATION_RATE = {1: 5, 2: 10, 3: 15}`、`EXTERNAL_OVULATION_V_MULT = 2`、`EXTERNAL_OVULATION_W_MULT = 4`、`EXTERNAL_OVULATION_DRUG_MULT = 5`、`SOFT_EGG_SEMEN_TRANSFER_RATE = 0.8`、`SOFT_EGG_FERTILIZATION_DELAY_HOUR = 1`、`SOFT_EGG_MIN_SEMEN = 5`、`SOFT_EGG_RATE_DIVISOR = 1500`、`SOFT_EGG_LEVEL_RATE = 3`、`STAGE_SOFT_EGG_WAIT`（阶段枚举插入，其后顺延）、`SOFT_EGG_SEMEN_LEVEL_MAX_VOLUME = 5000`、`SOFT_EGG_SEMEN_LEVEL_EXTRA_STEP = 1000`、`SOFT_EGG_SEMEN_LEVEL_MAX = 15`、`LAY_SOFT_EGG_SECOND_BEHAVIOR = "lay_soft_egg"` |
| `constant_effect.SecondEffect` | `LAY_SOFT_EGG = 621` |
| `constant_promise.Premise` | `SELF_BIRTH_TYPE_EGG_SOFT`、`T_BIRTH_TYPE_EGG_SOFT`、`SELF_EXTERNAL_OVULATION_CHANCE`（机会可用）、`PLAYER_SOFT_EGGS_IN_SCENE`（当前地点有体外卵） |
| `Behavior_Data.csv` / `Behavior_Effect.csv` | 1325 `lay_soft_egg`（`235 - 236 - 621 - 998`）、1326 `soft_egg_fertilized`（998）、1327 `soft_egg_born`（998） |
| `data/ui_text/dirty.csv` | `体外卵精液污浊` 1 条 |
| `data/ui_text/soft_egg_dirty_full.csv`（新） | `体外卵精液污浊0~15` 16 条 |
| `data/talk/system/second_pregnancy.csv` | 新行为 `lay_soft_egg` / `soft_egg_fertilized` / `soft_egg_born` 各 40 条（通用 5 + 102~108 各 5）+ 既有 13 个妊娠类二段行为补齐年龄差分 388 条，共 **508 条**（§3.13） |

## 5. 改动步骤（逐文件）

1. **`pregnancy_constant.py`**：分组 8 常量（§4）。
2. **`egg_handle.py`**：`get_birth_type` 去归一化；新增 `is_egg_soft`、`is_egg_layer`；`replace_entertainment_for_eggs` 守卫改 `is_egg_layer`；`check_egg_born` 对 12 改批量收集并传 `egg_id_list`；`add_egg` 增加 `soft` 键（默认 False）。
3. **新建 `Script/System/Pregnancy_System/soft_egg_handle.py`**：`judge_external_ovulation`、`lay_soft_egg`（建卵+转移精液+提示）、`get_soft_eggs_in_scene`、`add_semen_to_soft_egg`、`get_soft_egg_semen_level`、`get_soft_egg_name`、`check_soft_eggs_fertilization`（§3.8）。全部函数中文 docstring。
4. **`pregnancy_handle.py`**：`get_fertilization_rate` 三处 `now_rate = new_rate`（§3.12）；`update_reproduction_period` 维护 `external_ovulation_chance`（离开排卵日时同时清 `body_item[10]` 与 `force_ovulation`，§3.3）；`check_fertilization` 开头 12 早退；`check_all_pregnancy` 分流改 `is_egg_layer` + 12 只跑 `check_egg_born`。
5. **`attr_calculation.py`**：抽出 `get_semen_level_by_volume(value, max_volume)`，`get_semen_now_level` 改为调用（等价）。
6. **`orgasm_settle.py`**：每部位分支在 U 绝顶排尿之后加体外排卵判定（记录本部位本次最高程度；命中则赋予二段行为）。
7. **`second_behavior.py`**：`check_second_effect` NPC 分支绝顶结算后补 `second_behavior_effect(cid, change_data, [LAY_SOFT_EGG_SECOND_BEHAVIOR])`。
8. **`Second_effect.py`** / **`constant_effect.py`**：`LAY_SOFT_EGG = 621` 结算器 → `soft_egg_handle.lay_soft_egg`。
9. **`Settle/default.py:1696`**（催眠立刻排卵）：无壳卵生同时置 `external_ovulation_chance = True`。
10. **`realtime_settle.py`**：`judge_pl_real_time_data` 末尾调 `check_soft_eggs_fertilization`；**`sleep_settle.py`**：`check_all_pregnancy` 前调一次。
11. **`ejaculation_panel.py`**：`draw` 强制手动分支（含自慰 `self_mode`）；`draw_choose_part(self_mode)` 卵按钮与 `[照常射出]`；`shoot_soft_egg`；`ejaculation_flow(..., soft_egg_id=-1)` 卵分支。
12. **`dirty_panel.py`**：卵污浊行（普通/详细）。
13. **`born_event_panel.py`**：`egg_id_list` 参数、批量取名、无壳文案组、`soft_egg_born`。
13a. **`pregnancy_panel.py`** / **`pregnancy_constant.py`**：§3.11 新阶段枚举、阶段判定与信息文本。
14. **`game_type.py`** / **`save_handle.py`**：§4 字段与回填；`save_handle` 读档归一化处追加 12 族孕程清理（需在 `game_config` 已加载后按 `config_race[race].birth_type == 12` 判断）。
15. **前提**：`constant_promise.py` 4 个常量、`handle_premise_other.py` 4 个函数、ArkEditor `Premise.csv` 4 行（分类"生育"，CRLF）。
16. **CSV**：`Behavior_Data.csv` / `Behavior_Effect.csv` 3 行（同步 ArkEditor 副本，若存在同名文件）；`dirty.csv` 1 行；新建 `soft_egg_dirty_full.csv` 16 行；`second_pregnancy.csv` 508 行（§3.13；`\n` 字面量、无 ASCII 逗号；年龄差分前提 `high_1&CVP_A1_T|10X_G_0`），实施时单独成一步、分行为批量写入并逐组合计数校验。
17. **文档**：§10。
18. **update.log**：v0.66 修正段追加：`修正：修正了排卵促进药、催眠强制排卵与浓厚精液对受精概率的加成实际不生效的BUG`；新增段追加：`新增：（怀孕）实装了无壳卵生的生育方式，安努拉、阿戈尔、海嗣三个种族改为无壳卵生：排卵日当天与博士同处一地时，干员在普通以上程度的性绝顶中有概率体外排出一枚无壳卵（阴道绝顶概率翻倍、子宫绝顶四倍、子宫超强绝顶必定排卵，排卵促进药与催眠强制排卵改为提升排卵概率），排出时子宫与小穴中八成的精液会附着到卵上，之后一小时内博士可以在射精时选择射在卵上，卵上的精液越多受精概率与受精卵数量越高，一小时后进行受精判定，受精卵送往育儿室孵化，孵化与保育员、孵化加速药的机制与带壳卵生一致，同批受精卵会一同孵化并逐个取名` 与 `新增：（界面）当前地点有体外无壳卵时，射精时必定手动选择射精位置且可以选择射在卵上，身体栏会显示每枚卵上的精液量（详细污浊分0~15级）`。

## 6. 构建与本地化

- 改了 `Behavior_Data/Behavior_Effect/dirty.csv/ui_text 新文件/system 口上` → `python buildconfig.py` 全量重建。`data/talk/system/` 是 `talk_dir = data/talk` 的子目录（[buildconfig.py:10](buildconfig.py#L10)），随全部口上一起编译进 `Character_Talk.json`；只改既有文件的行时全量重建即可，若新建口上文件则按 skill 铁律先删 `data/Character_Talk.json` 再重建。
- ArkEditor 副本同步：`tools/ArkEditor/csv/` 有 `Behavior_Data.csv`、`Effect.csv`、`Premise.csv`（无 `Behavior_Effect.csv`）——二段行为 3 行同步进 `Behavior_Data.csv`，新二段结算 621 按 `Effect.csv` 现有的二段结算行格式追加（实施时核对该文件是否收录 `SecondEffect` 段）。
- 新增/修改的 `_()` 文案需用户后续 `buildpo` / `buildmo`。

## 7. 验证清单

### 7.1 单元/无头测试（`scratchpad/test_plan19.py`，复用 plan_18 框架 + skill 面板级打桩）

1. `get_birth_type(安努拉) == 12`；`is_egg_soft/is_egg_layer/is_viviparous` 真值表（1/2/11/12）。
2. `update_reproduction_period`：4→5 置 `external_ovulation_chance=True` 与 `ovulation_flag=True`；5→6 置 False。
3. `check_fertilization` 对 12：消费 `ovulation_flag`、不改 talent20、不清精液、无提示。
4. `judge_external_ovulation` 概率表（5/10/15 · 10/20/30 · 20/40/100）：打桩 randint 阈值探测 9 个格子（3 程度 × 其他/V/W），小绝顶恒假，W 超强恒真，药物 ×5 / 催眠 ×5 且**判定未命中时不清除**、命中时随机会一起清除、`update_reproduction_period` 5→6 时清除；不在玩家场景/非排卵日/机会已用 → 恒假。
5. 绝顶集成：给无壳卵生 NPC 造 W 部位 normal 绝顶（`normal_orgasm_dict={7:1}`）→ `orgasm_settle_in_second_behavior` 后 `second_behavior["lay_soft_egg"]==1`、机会置 False；再次绝顶不再触发。
6. `lay_soft_egg` 结算：子宫 1000ml/小穴 500ml → 卵 `semen_count == 1200`、两部位各剩 20%、等级重算、`WaitDraw` 含"1200ml"与"1小时"；`soft_eggs` 键自增。
7. `check_second_effect` NPC 分支一轮内完成 235/236/621 结算（体力气力下降、卵生成）。
8. 射精面板：场景有卵 + `base_setting[3]=0` + 有插入位置 → 进入 `draw_choose_part`（打桩 `askfor_all` 返回卵按钮）；交互对象为自己 + 场景有卵 → 面板只含卵按钮与 `[照常射出]`，选后者行为与原 `shoot_here(6,0)` 一致；`ejaculation_flow(soft_egg_id=k)` 后卵精液增加、目标部位精液不变、`shoot_position_body` 仍为 -1；避孕套时进套不进卵。
9. 污浊行：`get_soft_egg_semen_level` 0/1/…/10/11/15 边界（0、1、50、250、500、1000、4999、5000、5999、6000、9999、10000、12000）；身体栏文本在普通/详细两档各含预期串；卵不在当前地点则不显示。
10. 体外受精：`lay_time` 59 分钟前不判定；61 分钟后判定；打桩 randint 序列验证轮数 = 精液从 X 衰减到 <5 的次数、每轮阈值 `=(s/1500)^2*100 + level(s)*3`（level 随剩余量重算）、不乘周期倍率；10000ml 起判时统计受精卵数落在合理区间且无上限截断；`success=3` → 母亲 `eggs` 增 3 枚（`identified/fertilized/soft` 为真，`lay_time` 等于体外卵的）、`soft_eggs` 删除、母亲二段 `soft_egg_fertilized`；`success=0` → 只删卵。
11. 孵化接入：`get_hatching_eggs` 含新卵；`replace_entertainment_for_eggs` 对 12 生效；`get_accelerable_hatching_eggs` 含新卵；`any_hatching_eggs_exist` 为真。
12. 破壳：3 枚同批到期 → `Born_Panel(egg_id_list=3)` 取名 3 次、`born_new_character` 3 次、3 枚卵删除、24/27 置位、二段 `soft_egg_born`；带壳单卵路径回归（plan_12 行为不变）。
12a. 总览面板：母亲有体外卵 → 阶段为“体外卵待受精”，信息文本含地点/精液量/剩余分钟；枚举顺延后原有阶段的排序与筛选回归（plan_12 测试断言）。
12b. `get_fertilization_rate` 修复回归：子宫 500ml/等级 2、排卵日 → 基准 105%→100 封顶不适合观察，改用 100ml/等级 0（基准 1%×周期倍率）：仅排卵促进药 → ×5；仅催眠 → ×5；仅浓厚精液 → ×2；三者同时 → 连乘封顶 100；无加成时数值与改前逐位一致；用后 `body_item[10]`/`force_ovulation` 被清（既有行为）。
12c. 口上计数：`second_pregnancy.csv` 三个新二段行为各 40 条（通用 5 + 七档各 5）；既有 11 个母亲视角行为 102~108 每档各 ≥5 条、`child_to_loli` 103 档 5 条、`loli_to_girl` 104 档 5 条；文件总条数 = 36 + 508 = 544（按前提 token 计数）。
13. 前提 4 个真值；旧存档回填 3 项；12 族旧存档孕程清理：造一名 race=11（安努拉）且 talent21/26=1、fetus_count=2 的角色 → 回填后 20/21/22/26/35 全 0、fetus_count=0，talent23/24/27 与 `child_id_list` 不变；plan_17/18 回归测试重跑。

### 7.2 游戏内测试（用户执行）

- 安努拉干员排卵日：与其 H 至 V/W 绝顶 → 观察体外排卵口上与提示；射精面板出现卵按钮、身体栏卵行；等 1 小时后受精提示；育儿室孵化、保育员照料、孵化加速药可用；到期批量破壳逐个取名。
- 带壳卵生（黎博利）与胎生流程无变化。

## 8. 风险与回滚

- `get_birth_type` 去归一化会让三族现有存档中**已在胎生链里的角色**（受精/妊娠/临盆）失去后续结算：v2 确认口径为**读档时直接清除孕程素质**（§4 `save_handle` 行），不在分流里保留胎生链；清理只针对 20/21/22 三个孕程素质及其伴生状态，产后/育儿/泌乳与已出生的孩子保留。
- 绝顶结算热路径：新增判定只在 `is_egg_soft` 为真时展开，其余角色一次种族查表即返回。
- 射精面板：卵分支不设置射精部位字段，下游"射精部位"前提天然为假；口上不会误触发部位射精文案。
- 回滚：git 单次还原；存档新字段均为附加。

## 9. 范围外（v4 已逐项经用户确认）

- 体外卵的图片/纸娃娃地文（确认不做）。
- 体外卵被其他 NPC 干扰（路过/在场的干员不会捣毁、拿走或搬运卵；母亲离场也不带走卵）（确认不做）。
- 在 1 小时判定前收走/丢弃体外卵的指令（两轮均确认不做）。
- （原列入范围外、v4 改为纳入本期）三个新二段行为的口上全套年龄差分 → §3.4；`get_fertilization_rate` 加成覆盖 bug → §3.12。

## 10. 文档同步

- `妊娠系统.md`：§2 生育方式补 12 的实装说明与三族；§3 对照表加"无壳卵生链"一列；§4 卵字典新键 `soft`、`PLAYER_COLLECTION.soft_eggs`；§1 目录树加 `soft_egg_handle.py`；外部调用表加 `orgasm_settle/second_behavior/realtime_settle/ejaculation_panel/dirty_panel`。
- `射精面板系统.md`：`Ejaculation_Panel.draw` 强制手动分支、卵按钮、`ejaculation_flow(soft_egg_id)`。
- `身体信息面板系统.md`：体外卵污浊行与 0~15 级换算、新 ui_text 文件。
- `plan_12` §10 追加一条（12 实装、`check_egg_born` 批量化）。

## 11. 待确认口径（已于 2026-08-29 通过询问工具分三轮全部确认，共 16 项；第 17 项为用户直接追加的需求）

| # | 问题 | 确认结果 |
| --- | --- | --- |
| 1 | 体外排卵概率表 | **普通 5 / 强 10 / 超强 15**（其他部位）；阴道 ×2 → 10/20/30；子宫 ×4 → 20/40/**100**；排卵促进药与催眠各 ×5 |
| 2 | 体外受精是否乘生理周期倍率 | **不乘** |
| 3 | 体外受精基础概率是否含精液等级项 | **含**：`+level*5`，level 为卵的 0~15 级污浊等级（按当轮剩余精液量重算） |
| 4 | 排卵日睡觉结算时 12 族体内精液是否清零 | **不清零** |
| 5 | 身体栏"有交互对象才绘制"门限 | **保持**，卵行只在身体栏可见时出现 |
| 6 | 三族旧存档中已处于受精/妊娠/临盆的角色 | **读档时直接清除孕程素质**（20/21/22/26/35 及 fetus_count/identical_twins/acceleration_days），产后/育儿/泌乳与已出生孩子保留 |
| 7 | 未受精的体外卵 | **判定后立即废弃并提示**，不新增丢弃指令 |
| 8 | 单枚体外卵的受精卵数量是否设上限 | **不设上限**，改为把精液等级项由每级 +5 降为**每级 +3** 以收敛 |
| 9 | 自慰（交互对象为自己）且场景有卵时的射精面板 | **弹窗只列卵按钮 + “照常射出”按钮** |
| 10 | 排卵促进药/催眠 ×5 的消耗时机 | **保留到当日排卵机会结束**（命中或离开排卵日时清除，判定不消耗） |
| 11 | 怀孕总览面板是否新增“体外卵待受精”阶段 | **新增**（§3.11） |
| 12 | 新二段行为口上是否做外表年龄差分 | **按 102~108 全套差分**（每个行为 通用 5 + 七档各 2 = 19 条） |
| 13 | 体外卵的图片/纸娃娃地文 | 确认不做 |
| 14 | 体外卵被其他 NPC 干扰 | 确认不做 |
| 15 | 收走体外卵随身携带的指令 | 确认不做 |
| 16 | `get_fertilization_rate` 三种加成被覆盖的既有 bug | **本期顺带修复**（§3.12） |
| 17 | （v5 用户追加）妊娠类全部二段行为的年龄差分 | 全部 16 个行为补齐 102~108，每个〈行为×年龄〉组合 5 条；成长类两个行为只补可达档（103/104）；通用分支维持现状（§3.13） |

## 12. 实施记录（2026-08-29）

- 全部按 §5 落地，逐文件明细、阶段顺序、测试结果与实施中的口径微调见实施文档 `plan_19_无壳卵生机制_实施步骤与记录.md` §6。
- 实施中与方案的差异（均已在实施文档记录）：
  1. ArkEditor `Effect.csv` 只收录 `BehaviorEffect` 段（其 621 是 `GET_T_PAN`），`SecondEffect.LAY_SOFT_EGG=621` 不同步进去（§5 第 16 步"若收录则同步"的核对结果）。
  2. `check_egg_born` 对带壳卵生保持"每晚一枚"，只有无壳卵生走批量；`Born_Panel` 的 `egg_id` 参数改名为 `egg_id_list`，`soft_egg_mode` 由卵字典的 `soft` 键推断。
  3. 无壳卵生 3 族受精率修复（§3.12）落地后，plan_18 测试中"12 归一化为胎生"的断言按新语义改为 False。
- 口上：`second_pregnancy.csv` 由 36 条增至 544 条（+508），逐〈行为×年龄〉计数校验通过。
- 无头测试 `scratchpad/test_plan19.py` 83/83：覆盖 §7.1 全部 13 项（含 12a/12b/12c）。

### 12.1 第 1 次修改（2026-08-29，卵块口径 + 女儿身份差分）

- 代码文案：`soft_egg_handle.lay_soft_egg` 提示（"一大团裹在黏稠凝胶里的无壳卵块…精液需要穿过凝胶层才能与卵粒结合"）、`get_soft_egg_name` → "{母亲}排出的卵块"、受精提示（"Xml精液渗过了…的凝胶层…共有N颗卵粒受精" / "没能穿透凝胶层…整团卵块失去了活性"）；`born_event_panel` 无壳文案组改为"凝胶里的卵粒胀大、胶质化开"、总结行"N颗受精卵粒一同孵化了"；`dirty_panel` 详细行前缀 `[卵块]`；`pregnancy_panel` 信息文本"…的卵块（…）"、阶段名 `STAGE_NAME_LIST[3]` → "卵块待受精"；射精按钮 `[卵块N]`。
- 数据：`soft_egg_dirty_full.csv` 16 条全部重写；`second_pregnancy.csv` 删除原 120 条无壳口上后按新口径重写 120 条，再为 16 个行为各追加 5 条女儿身份差分（80 条），文件 544 → 624 条。
- 文档：本文件 v6、§3.7/§3.13 口径注；实施文档 §6.5；`妊娠系统.md` §2 措辞；update.log 两条新增的措辞改为"卵块"、口上条目补"女儿身份的差分"。
- 验证：删 `Character_Talk.json` 全量重建；`test_plan19.py` 断言改为新措辞后 **83/83 通过**（含女儿差分计数）。
- 用户手动微调（2026-08-30）：`EXTERNAL_OVULATION_DRUG_MULT` 由 5 改为 **2**（排卵促进药/催眠各 ×2，两者同时 ×4）；总览面板信息文本改为"待受精卵块：…"；update.log 中无壳卵生的单行条目拆为 4 行。测试断言改为引用常量。
- 事故记录：本次文档同步脚本因"先 `open(w)` 再求值内容"的写法，在断言失败时截空了 `update.log` 与本方案文件；`update.log` 由 git HEAD 恢复并重加本会话条目，本方案由 v1 原文重放 v2~v5 补丁脚本后补回 §12 与 v6 记录（内容与截空前一致）。
