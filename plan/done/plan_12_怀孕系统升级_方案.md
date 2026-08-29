# Plan 12（方案）：怀孕系统升级（子系统目录整合 + 怀孕面板 + 生育谱系图 + 卵生生育方式）

> 本 Plan 拆分为两个文件：**本文件为纯方案**（需求、现状调查、设计决策、数据结构、
> 风险、范围外）；具体的逐文件改动步骤、构建、验证清单、回滚与实施过程记录见
> `plan_12_怀孕系统升级_实施步骤与记录.md`（下文简称"实施文档"）。

- 状态：**一~六期及 v10~v14 修正均已实施完成（2026-08-25，单元测试 119/119 通过，过程与结果见实施文档 §6；游戏内整体测试待用户执行）**
- 来源：用户需求 → 升级整个怀孕系统，使其更加真实和丰富
- 已确认的设计决策（2026-08-23，详见 §8）：排卵=每个排卵日必排；鉴定=**NPC 自主进行**（非玩家指令）、一次全部鉴定、无精卵静默废弃不通知玩家；孵化=自然天数推进；谱系图上下各 2 代；面板入口=育儿室内指令 + 管理罗德岛界面教育区子系统按钮
- 修订记录：
  - v1 —— 鉴定设计为玩家指令（对交互对象、在育儿室使用），面板入口设计为 DAILY 随时可开
  - v2 —— 按用户确认修订：鉴定改为 NPC 自主完成（娱乐时段替换链），无精卵静默废弃仅受精时通知玩家，一次鉴定全部；排卵改为每排卵日必排；面板入口改为育儿室指令 + 教育区子系统按钮
  - v3 —— 按用户补充修订：鉴定与孵化**不再各占一个时段**，合并为同一个特殊娱乐"照料卵"（占一个随机时段），时段内按优先级（鉴定 > 孵化）执行两种不同的行为
  - v4 —— 按用户追加需求：为解决**监禁角色**的卵无人鉴定的问题，新增两个玩家指令——"拿走产下的卵"（将被监禁者的未鉴定卵收为玩家临时持有，`PLAYER_COLLECTION` 存**索引数据**指向原角色的卵）与"鉴定持有的卵"（玩家在育儿区鉴定临时持有的卵，经索引同步回写原角色卵数据）；监禁角色无法进行孵化娱乐，其余与正常卵生一致（见 §3.10）
  - v5（二期，2026-08-23 实施）—— 按用户追加需求：①分类归位——怀孕总览/鉴定持有的卵/鉴定卵/孵化卵改**工作**类，拿走产下的卵改**猥亵**类；②新增**保育员**工作（教育区/育儿室，仅带壳卵生种族可任职，见 §3.11；**该种族限制已于 v11 取消**）；③鉴定改由保育员主导——持未鉴定卵的 NPC 到育儿室后，**在班保育员在场则等待其鉴定**，自己是保育员或无保育员在场则自己鉴定（兜底，保证卵不滞留）；保育员无卵可鉴定时等权重照料孵化中的卵/照料婴儿；母亲保留每日孵化娱乐。二期确认口径：无在职保育员→自己鉴定兜底；任职资格=仅 birth_type==11（**v11 取消**）；作息冲突（在职保育员>0 但不在场）→**在场才等待**
  - v6（三期，2026-08-23 实施）—— 按用户追加需求：新增行为与指令按所在类型段**重新编号并归位**——行为 Behavior_Data cid：鉴定卵 175→267、孵化卵 176→268、鉴定持有的卵 178→269（工作段，照顾婴儿块之后）、拿走产下的卵 177→345（猥亵段，监禁块之后）；指令 cid：怀孕总览 1036→2052、鉴定持有的卵 1038→2053（WORK 段）、拿走产下的卵 1037→5105（OBSCENITY 段）；CSV 行位同步迁移。实施中发现行为/状态**整数常量空间与 Behavior_Data cid 是两套独立编号**（如 steal_scene_all_socks Data=338/整数=345），故 take_chara_eggs 的整数常量取监禁段后的 **354**，其余三者整数与 cid 恰好可对齐（267/268/269）
  - v7（四期，2026-08-23 实施）—— 修复用户报告 BUG：**玩家在角色排卵日当天不睡觉会导致该周期的受精判定（胎生）与排卵结算（卵生）被永久错过**（两者原以"当前周期==5"为瞬时触发门且只挂在玩家睡觉结算链上，而周期在每日 0 点无条件推进）。改为**排卵日事件待办标记 `PREGNANCY.ovulation_flag` 驱动 + 0 点结算兜底**（见 §3.4 实施口径修正二）
  - v8（五期，2026-08-23 实施）—— 按用户追加需求：谱系图改为**传统家谱式五代分层布局**（每代一行、整行近似居中、夫妇以═相连、子女按另一位家长分组、代内自动换行、行尾/人名省略号语义化），并保障"一父多母、每母多子"极端场景正确显示（见 §3.8 v8 改版）。确认口径：居中分层**不画跨行连线**（遵守 §2.12 硬约束）；中心行**显示兄弟姐妹**
  - v9（六期，2026-08-24 实施）—— 按用户追加需求：谱系图改为**带完整连线的传统家谱图**——共 4 代（确认口径：上 1 代+中心+下 2 代），每代一个名字行、代间夹**排版行**画过渡连线（`┌┬┐┴┼│─` 等字形，夫妇═中点下坠→水平分叉→连到各子辈名字中点）；**父本位置逐一重复写玩家名**（游戏设定父本恒为玩家，不画长线连回单一玩家节点），NPC 名字保持唯一并正确连线（归属规则：孩子挂在更深的血缘家长节点下）；超宽处理确认口径为**以家族为单位自动分页**（一页至少一个家族、家族永不拆散，`[上一页]/[下一页]`+页码标识，单家族独占一页仍超宽时兜底右侧折叠 `…(+N人)`）。本期经用户确认**放开 §2.12 跨行列对齐约束**（仅限谱系图）：列位以 wcwidth 为单位制、整图统一前导缩进，对齐依赖等距更纱黑体 SC 度量（见 §3.8 v9 改版）。五期的代内换行续排机制随连线布局废弃
  - v10（六期修正，2026-08-25 实施）—— 按用户追加调整：夫妇连接符 `═` 改为 **`╤`**（自带向下接头）；排版行连线的**起点**从夫妇文本中点改为 `╤` 连接符所在列（无配偶/不在册时无连接符，起点退回人名中点列），连线**终点**保持在子辈名字中点不变
  - v11（二期修正，2026-08-25 实施）—— 按用户决定**取消"保育员仅带壳卵生种族可任职"的限制**：工作分配面板不再对 153 做种族过滤（用户已删除代码侧过滤段），WorkType 职业要求列为"无"，任何干员均可任保育员；其余保育员流程（鉴定/孵化/照料婴儿、在场才等待）不变
  - v12（v4 结算归位+lay_egg 结算等级，2026-08-25 实施）—— 按用户追加调整：①`拿走产下的卵`/`鉴定持有的卵`的数据结算从"指令处理函数内行为前直调 egg_handle"改为**正式注册的专用结算**（`BehaviorEffect.TAKE_CHARA_EGGS_SETTLE=546`、`IDENTIFY_HELD_EGGS_SETTLE=547`，实现于 `Script/Settle/default.py`），行为在 `Behavior_Effect.csv` 中改挂 546/547（原 9999 空结算废弃），指令处理函数仅保留通用结算——结算时点由"下指令瞬间"变为"行为结算阶段"（口上先于效果结算，前提/口上判定不受影响）；②二段行为 `lay_egg` 由 998（必须显示）改为 **997（必须计算、不必须显示）**——排卵不再强制弹出口上，由 `must_settle_check` 在下一结算阶段静默结算；③谱系图中心前缀符号由用户手动改为 `•`（原 ◆），测试与文档同步
  - v13（生育事件位置，2026-08-25 实施）—— 按用户要求核查"胎生生产与卵生破壳事件中玩家与母亲是否移动到医疗部住院区"：核实 `Born_Panel` 原本**不做任何位置移动**（胎生母亲仅靠临盆/产后 AI 守卫传送、玩家始终留在床上；卵生两人都不动），与事件文本不符。修正为事件开始时统一把母亲与玩家瞬移到住院区（母亲已在则玩家会合到其病房），确认口径：**事件结束后两人留在住院区**（见 §3.7）
  - v14（文档归位，2026-08-25 实施）—— 按用户要求：`Script/System/Pregnancy_System/怀孕系统设计文档.md` 改为**纯索引**（指向本方案、实施文档与工作流文档），不再承载实际内容；原设计文档 §1~§10 的实际内容整体并入 `.github/prompts/数据处理工作流/妊娠系统.md`（保持同号章节，原有的胎生链通用说明重编为 §11~§14，并修正其中"受精判定仅在排卵日"等陈旧表述）
- 预计改动量：约 25~30 个文件（新增 `Script/System/Pregnancy_System/` 目录 6 文件 + 迁移 2 文件改 4 处 import + 数据结构/结算/指令/前提/常量/状态机/面板/存档兼容 + 若干 CSV）
- 风险等级：中（涉及存档数据结构新增、生产事件链扩展、NPC 每日娱乐挂钩；不改动胎生既有数值逻辑）
- 适用代码快照：`master @ ba388bc60`
- 参考文档：`.github/prompts/数据处理工作流/妊娠系统.md`（该文档写成后系统有过更新，本方案 §2 调查以实际代码为准，文档仅作入口索引）

---

## 1. 目标（用户需求原文整理）

1. **子系统目录整合**：在 `Script/System/` 下创建怀孕系统单独目录（`Pregnancy_System/`），将分散在各处的怀孕系统相关文件整合进去（遵循 `Script/System/*` 子系统惯例，含自身设计文档）。
2. **怀孕总览面板**：单独面板，统计展示当前所有处于怀孕阶段的干员及其阶段，支持按怀孕阶段升/降序排序与按阶段筛选。
3. **生育谱系图子面板**：怀孕面板内的子面板，用字符绘图绘制所有生育角色的谱系关系。限定画面显示的代系数量；点击图中角色则以其为中心重绘上下 X 代；可重置回初始起点（起点为玩家）。
4. **新增生育方式**：先实装两种——鸟类/爬行类代表的**带壳卵生**、鱼类代表的**无壳卵生**。
5. **Race.csv 新增生育方式列**：`1`=单胎胎生（默认）；`11`=带壳卵生；`12`=无壳卵生（**本次不实装**，行为暂同 1）。
6. **带壳卵生 —— 排卵与鉴定**：怀孕周期中体内射精 → 排卵日当天排出无精卵或受精卵（**单独的排卵结算**）；卵在 `class PREGNANCY` 中以字典记录状态（是否已鉴定、是否受精、孵化阶段等）；次日起可拿到**育儿室**鉴定（**单独的鉴定指令**，角色持有自己未鉴定的卵且在育儿室时可用）；未受精 → 废弃删除，受精 → 打印消息、进入孵化流程。
7. **带壳卵生 —— 孵化与破壳**：受精卵一直放在育儿室孵化；母亲每天固定将一个随机娱乐时段的活动改为去育儿室**孵化**（单独的指令行为）；孵化总时长与胎生孕期一致，**无临盆阶段**；孵化完成时在**医院住院区**进行**破壳事件**（同样需要医生在场、同样取名），新生儿同样在育儿区长大结算；母亲**不进入产后**，但破壳后**进入泌乳**，之后进入与胎生完全一致的育儿链。
8. **监禁角色的卵处理指令**（v4 追加）：为解决监禁中角色的卵无人鉴定的问题，新增两个玩家指令——
   - **拿走产下的卵**：被监禁角色持有未鉴定卵时，玩家可拿走这些卵；`class PLAYER_COLLECTION` 新增"玩家临时持有的卵"字典，**仅为索引数据**（每条指向一个角色的一个卵），非详细数据。
   - **鉴定持有的卵**：玩家临时持有的卵不为空时，可在**育儿区**鉴定这些卵是否受精，根据索引**同步更新原监禁角色的卵数据**——未受精删除、已受精进入孵化状态；只是监禁角色无法进行孵化娱乐，其他都与正常卵生角色一致。

## 2. 现状调查（已完成，均为实际代码核实结果）

### 2.1 妊娠核心模块 `Script/Design/pregnancy.py`（545 行）

| 函数 | 位置 | 职责与关键规则 |
| --- | --- | --- |
| `get_fertilization_rate` | :33 | 由 V 精液量/等级（`dirty.body_semen[7]`）算基础概率；事前药 `h_state.body_item[11]`、事后药 `[12]` 清零概率；生理周期倍率 `config_reproduction_period[period].type`（0/1/2/3）；排卵促进药 `[10]`×5、催眠 `hypnosis.force_ovulation`×5、玩家浓厚精液 `talent[33]`×2；写 `pregnancy.fertilization_rate` |
| `check_fertilization` | :91 | **仅 `reproduction_period == 5`（排卵日）判定**；清空 6/7 号部位精液；已受精（talent 20/21/22 任一）跳过；未初潮 `talent[6]` 不孕；机械 `race==2` 且无生育模组 `talent[171]` 不孕；随机达成 → `talent[20]=1`、`fertilization_time=game_time`、无意识妊娠 → `talent[35]`；二段行为 `fertilization` / `fertilization_failed`；成就 706/708 |
| `check_pregnancy` | :174 | talent20 且受精 ≥90 天 → 20→0、21 妊娠=1、26 孕肚=1、**27 泌乳=1**、按罩杯素质 121~125 设 `milk_max=150+(id-121)*40`；二段 `pregnancy` |
| `check_near_born` | :211 | talent21 且 ≥260 天 → 污浊重置、22 临盆=1、`settle_chara_unnormal_flag(id,2)`；二段 `parturient` |
| `check_born` | :243 | talent22，`(天数-260)*20%` 概率 → 弹 `sp_event_panel.Born_Panel` |
| `check_rearing` | :262 | talent23 产后 且 最新孩子 `child_id_list[-1]` 的 `pregnancy.born_time` ≥2 天 → 23→0、24 育儿=1；二段 `rearing` |
| `check_rearing_complete` | :293 | talent24 且孩子出生 ≥90 天 → 24→0、**27 泌乳→0**、`character_handle.get_new_character(child)`、孩子 101 婴儿→102 幼女、`work_type=152`（教育区上课）；二段 `rearing_complete` |
| `check_grow_to_loli` | :335 | `father_id==0` 且 talent102 且出生 ≥270 天 → 102→103、`talent[6]=0`、`chest_grow`；二段 `child_to_loli` |
| `check_grow_to_girl` | :367 | talent103 且 ≥450 天 → 103→104、`talent[7]=0`、胸部+身体部位成长；二段 `loli_to_girl` |
| `check_all_pregnancy` | :401 | 依次调用上述全链 |
| `update_reproduction_period` | :418 | 周期 0..6 循环 +1 |
| `chest_grow` / `body_part_grow` | :431 / :486 | 按母亲素质遗传成长（机械母亲跳过） |

### 2.2 妊娠相关数据结构

- **`class PREGNANCY`**（[game_type.py:310-330](Script/Core/game_type.py#L310)，已存在，经 `character_data.pregnancy` 访问）：`fertilization_rate`、`reproduction_period`、`fertilization_time`、`born_time`、`milk`、`milk_max=200`、`unconscious_fertilization`、`lactation_flag`。**卵字典加在这里**（见 §4）。
- **`class RELATIONSHIP`**（[game_type.py:333-349](Script/Core/game_type.py#L333)）：`father_id=-1`、`mother_id=-1`、`child_id_list=[]`。谱系图数据源即这三个字段。
- 角色模板 `Mother_id`（[game_type.py:82](Script/Core/game_type.py#L82)）；`init_character` 中 `if character_tem.Mother_id:` → `father_id=0`（父亲恒为玩家）、`mother_id=Mother_id`（[character_handle.py:64-66](Script/Design/character_handle.py#L64)）。
- **当前 `data/character/` 各 CSV 均无 Mother_id 数据**——初始干员实际都没有预设父母关系（debug 面板可手改：[debug_panel.py:1824-1831](Script/UI/Panel/debug_panel.py#L1824)）；多周目迁移会保留并映射亲子关系（`old_chara_to_new.py:540-546/750-753/897-899`）。谱系图直接读 `relationship` 字段即可天然兼容"预设父母"。
- 素质编号：6 未初潮、7 未成年、20 受精、21 妊娠、22 临盆、23 产后、24 育儿、26 孕肚、27 泌乳、33 浓厚精液（玩家）、35 无意识妊娠、101 婴儿、102 幼女、103 萝莉、104 少女、121~125 罩杯、171 生育模组；**25 空闲**（Talent.csv 中 24 与 26 之间缺号）。
- `character_data.race: int`；种族配置 `game_config.config_race`（[game_config.py:194,733](Script/Config/game_config.py#L194)）。
- 泌乳产奶实时结算：[realtime_settle.py:173-178](Script/Settle/realtime_settle.py#L173)——仅 `talent[27]` 者积累乳汁。卵生母亲破壳后获得 27 即自动接入。
- **`class PLAYER_COLLECTION`**（[game_type.py:878](Script/Core/game_type.py#L878)，经 `character_data[0].pl_collection` 持有，:1651）：玩家收藏品结构体，plan_06 曾在此加 `used_condoms`——v4 的"玩家临时持有的卵"索引字典加在这里。
- 监禁相关既有设施：`sp_flag.imprisonment`（监禁 flag，[handle_npc_ai.py:252](Script/Design/handle_npc_ai.py#L252) 锁移动）；现成前提 `T_IMPRISONMENT_1`（交互对象被监禁，[constant_promise.py:1519](Script/Core/constant_promise.py#L1519)）可直接用于拿卵指令。

### 2.3 二段行为结算链

- 妊娠二段行为定义在 [Behavior_Data.csv:674-683](data/csv/Behavior_Data.csv#L674)，cid **1311~1321**（`fertilization`、`fertilization_failed`、`pregnancy`、`parturient`、`born`、`postpartum`、`rearing`、`rearing_complete`、`child_to_loli`、`loli_to_girl`），trigger 均为 `npc`；对应 [Behavior_Effect.csv:671-678](data/csv/Behavior_Effect.csv#L671) 挂效果 **998**（`SecondEffect.Must_Show`，[constant_effect.py:997](Script/Core/constant_effect.py#L997)；999 为空白结算）。**状态变化都在 pregnancy.py 内直接完成，二段行为只负责触发口上**。
- 空闲号：**1316、1322~1330**（实施时现场核对）。
- 触发 API：`second_behavior.character_get_second_behavior(character_id, "行为en_name")`。
- 口上文件：`data/talk/system/second_pregnancy.csv`（按 behavior_id 检索）。

### 2.4 每日/实时结算钩子

- **玩家睡觉结算**：[sleep_settle.py:88](Script/Settle/sleep_settle.py#L88) 逐 NPC 调 `pregnancy.check_all_pregnancy`——妊娠全链每晚推进一次。**排卵结算/孵化推进/破壳判定挂这里**（同一入口内分流）。
- **每日 0 点结算**：[past_day_settle.py:65-67](Script/Settle/past_day_settle.py#L65) 逐 NPC 先 `handle_npc_ai.get_chara_entertainment`（刷新三个娱乐时段）再 `pregnancy.update_reproduction_period`。**孵化娱乐替换挂在娱乐刷新之后**。

### 2.5 生产（分娩）事件流程

- [sp_event_panel.py](Script/UI/Panel/sp_event_panel.py) **整个文件只有 `Born_Panel`**（:31-172）。
- 医生选择（:56-73）：**并非"医生在场"前提校验**，而是文案自动选角——母亲非凯尔希且凯尔希在册则凯尔希接生，否则随机医疗干员（`profession==3`），再兜底随机任意干员。破壳事件照搬此逻辑即满足"需要医生在场"。
- 流程：二段 `born` → 取名 `character.input_name_func`（:106）→ **`character_handle.born_new_character(mother_id, name)`**（:109）→ 写 `child.pregnancy.born_time`（:111）→ 二段 `postpartum` → 产后结算（:118-137：22→0、23=1、26 孕肚→0、经验 65/68/86、V/W 扩张能力升 5）→ 生育成就。
- **现存 BUG**：[sp_event_panel.py:124](Script/UI/Panel/sp_event_panel.py#L124) `settle_chara_unnormal_flag(character_id, 2)` 用的是 :60 循环残留变量 `character_id` 而非 `self.mother_character_id`，顺手修正。
- Web 模式：`enter_managed_sub_panel_mode_by_type(BORN_EVENT_PANEL_TAB_ID)`（:160-171）包裹绘制，破壳事件复用同一包裹。
- 新生儿创建 [character_handle.py:155-201](Script/Design/character_handle.py#L155)：`Race=母亲race`、`Mother_id=母亲`、adv 9000~9999 去重、基础素质 `{0~4,6,7,101,121,126,129,131,451}` + 母亲可遗传素质、父母双方 `child_id_list` 追加、性履历特殊记录、`init_character`、婴儿异常 flag(7)。**卵生破壳直接复用此函数**。
- `sp_event_panel` 的引用方**仅** [pregnancy.py:19](Script/Design/pregnancy.py#L19) 与 :258 两处。

### 2.6 临盆住院与育儿室机制

- 临盆/产后锁定：[handle_npc_ai.py:239-274](Script/Design/handle_npc_ai.py#L239) `judge_character_cant_move`——talent22/23 者锁移动、欲望清零、不在 `Inpatient_Department` tag 场景则瞬移过去。**卵生无临盆/产后，不触碰此函数**。
- 育儿室场景 tag：`"Nursery"`；前提 `in_nursery`（[handle_premise_place.py:3418-3428](Script/Design/handle_premise/handle_premise_place.py#L3418)）、"在育儿室且有婴儿"（[handle_premise_other.py:881-894](Script/Design/handle_premise/handle_premise_other.py#L881)）。
- 玩家侧照顾婴儿指令 `TAKE_CARE_BABY`（[handle_instruct.py:1047-1050](Script/System/Instruct_System/handle_instruct.py#L1047) → `constant.Panel.TAKE_CARE_BABY=42` → [normal_flow.py:314-316](Script/UI/Flow/normal_flow.py#L314) → [normal_panel.py:105+](Script/UI/Panel/normal_panel.py#L105)）。**鉴定卵指令按此指令+面板的先例写**。

### 2.7 生理周期与排卵日

- [Reproduction_period.csv](data/csv/Reproduction_period.csv)：cid 0~6 共 7 天循环（0,1 安全日 type0 / 2,3 普通日 type1 / 4,6 危险日 type2 / **5 排卵日 type3**）；`type` 兼作受孕概率倍率。
- 排卵日判定：`pregnancy.reproduction_period == 5`（每日 0 点 +1 mod 7）。排卵结算沿用此判定。

### 2.8 Race.csv 加载链与 CSV 列新增方式

- 表头 4 行语义（[buildconfig.py:142-163](buildconfig.py#L142)）：第 2 行中文名 → docstring、第 3 行类型、第 4 行是否提取翻译（0/1）、第 5 行首格为类描述。
- **陷阱**：数据行空值字段会被整个删掉（[buildconfig.py:175-177](buildconfig.py#L175)），生成的配置对象上将**不存在**该属性 → 新列必须为全部数据行填值，代码访问统一走 `getattr(race_config, "birth_type", 1)` 兜底。
- Race.csv 现有数据行：cid 0（博士）~ 44，共 45 行。
- `config_def.py` 的 `Race` 类由 buildconfig 自动生成，新列跑一次 `buildconfig.py` 即生效。

### 2.9 NPC 娱乐时间系统

- 数据：`character_data.entertainment.entertainment_type[0..2]`（上午/下午/晚上三时段）。
- 每日刷新 [handle_npc_ai.py:773-839](Script/Design/handle_npc_ai.py#L773) `get_chara_entertainment`：派对日全覆盖；幼女固定 151 过家家；随机池 = `config_entertainment` 全部 id（除 0），逐个检查设施开放、特判（:817 品酒 62 仅晚上）、`need` 条件（`attr_calculation.judge_require`，[attr_calculation.py:925](Script/Design/attr_calculation.py#L925)，token 为 `A能力|T素质|J宝珠|E经验|F好感|X信赖|O设施|G攻略`）。**新增"孵化"娱乐必须防止进入随机池**（见 §3.6）。
- AI 消费 [handle_npc_ai.py:384-423](Script/Design/handle_npc_ai.py#L384)：娱乐时间内取当前时段娱乐配置，`auto_ai=1` 时走 `npc_auto_work_or_entertainment`，读 `auto_ai_move` / `auto_ai_entertainment` 列（**状态机 id**，:609-625）执行"移动到场所→执行娱乐行为"。
- 状态机：常量注册 `Script/Core/constant/StateMachine.py`，实现 `Script/StateMachine/default.py` `@handle_state_machine.add_state_machine`。
- [Entertainment.csv](data/csv/Entertainment.csv) 列：`cid,name,behavior_id,place,place_tag,need,tag,auto_ai,auto_ai_move,auto_ai_entertainment,describe`。
- 娱乐类前提写法先例：[handle_premise_entertainment.py:28-45](Script/Design/handle_premise/handle_premise_entertainment.py#L28)（`entertainment_is_xxx`：当前时段娱乐 == 某 id）。

### 2.10 面板先例与挂载点

- **全干员位置面板**（排序/筛选先例 + 挂载全链）：Panel 常量 `ALL_NPC_POSITION=8`（[constant/\_\_init\_\_.py:57](Script/Core/constant/__init__.py#L57)）→ 面板流注册 [normal_flow.py:99-102](Script/UI/Flow/normal_flow.py#L99) → 打开指令 [handle_instruct.py:884-887](Script/System/Instruct_System/handle_instruct.py#L884)（`cache.now_panel_id = constant.Panel.XXX`）→ [Instruct.py:81](Script/System/Instruct_System/Instruct.py#L81) + [InstructConfig.csv:42](data/csv/InstructConfig.csv#L42)（`1018,all_npc_position,干员位置一览,DAILY,...`）。筛选状态持久化在 `Cache` 字段（[game_type.py:1849-1851](Script/Core/game_type.py#L1849)）。
- **子系统面板先例**：`Script/System/First_Record_System/first_record_panel.py`（由 [see_character_info_panel.py:16,64](Script/UI/Panel/see_character_info_panel.py#L16) 集成）；子系统目录惯例参照 plan_06 的 `Item_System`。
- **管理罗德岛界面的部门子系统入口先例**：[manage_basement_panel.py:88-102](Script/UI/Panel/manage_basement_panel.py#L88) `department_son_panel_button_dict`（部门名 → 子系统按钮文本列表，**每部门最多 2 个按钮**，:227 `department_count = 2` 硬编码）+ [manage_basement_panel.py:807](Script/UI/Panel/manage_basement_panel.py#L807) `jump_to_son_panel`（按按钮文本分支、函数内 import 并实例化对应子系统面板）。**教育区目前没有子系统按钮**，可直接新增一个。
- 只用抽象绘制类（`NormalDraw` / `Button` / `CenterDraw`），Web 模式经 `web_draw_adapter` 自动兼容。

### 2.11 分散文件整合范围（引用全量清单）

`pregnancy` 模块函数的外部调用**仅 3 处**；`sp_event_panel` 的引用仅 pregnancy.py 内 2 处：

| 引用方 | 位置 | 调用 |
| --- | --- | --- |
| `Script/Settle/sleep_settle.py` | :12 import、:88 | `check_all_pregnancy` |
| `Script/Settle/past_day_settle.py` | :14 import、:67 | `update_reproduction_period` |
| `Script/UI/Panel/ejaculation_panel.py` | :436-437（函数内 import） | `get_fertilization_rate` |
| `Script/Design/pregnancy.py` | :19 import、:258 | `sp_event_panel.Born_Panel` |

→ **迁移成本低**：两文件整体迁入 `Pregnancy_System/`，共改 4 处 import，不留兼容层。
**不迁移**（属于全局分散注册体系，保持原地）：二段行为常量与 CSV、`handle_premise/*` 中的妊娠前提、`Second_effect.py`、debug/body_info/physical_check 等面板中对 `character_data.pregnancy` 字段的读写。

### 2.12 已知陷阱与硬约束

- CSV 数据行空值字段会被删除（§2.8），Race 新列全行必填。
- 旧存档回填段：[save_handle.py:259-274](Script/Core/save_handle.py#L259)（逐角色 `hasattr` 回填），PREGNANCY 新字段挂这里。
- CSV/常量改动后必须 `buildconfig.py` 全量重建；本机必须用 `.conda\python.exe`。
- 指令/行为/状态机/二段行为编号实施时必须现场核对空闲号（plan_06 §8.1 教训）。
- 谱系图的框线字符**跨行列对齐**在部分字体/字号下会错位（框线与空格宽度不可通约，见 CLAUDE.md 地图工具说明）——v8 前以无连线布局规避；**v9 起经用户确认放开该约束（仅限谱系图）**，连线对齐依赖等距更纱黑体 SC 度量（§3.8）。
- 行为若需触发口上，必须在 `Behavior_Effect.csv` 有行（可挂空结算 9999 / 二段挂 998，plan_06 §8.7 教训）。

## 3. 设计决策

### 3.1 子系统目录与迁移策略

```text
Script/System/Pregnancy_System/
├── __init__.py
├── pregnancy_handle.py      # 原 Script/Design/pregnancy.py 整体迁入（函数名不变）
├── egg_handle.py            # 新增：卵生——排卵结算、卵数据操作、鉴定、孵化推进、破壳判定、get_birth_type
├── born_event_panel.py      # 原 Script/UI/Panel/sp_event_panel.py 迁入，Born_Panel 扩展出破壳模式
├── pregnancy_panel.py       # 新增：怀孕总览面板（含谱系图子页签）
├── family_tree_draw.py      # 新增：谱系树构建与字符绘制（供 pregnancy_panel 调用）
└── 怀孕系统设计文档.md       # 仅索引（v14 起实际内容在工作流文档 妊娠系统.md）
```

- 迁移方式：直接移动 + 改 §2.11 所列 4 处 import，**不留旧路径 shim**（引用极少）。
- 弃选：保留 `Script/Design/pregnancy.py` 薄转发层——引用仅 3 处，转发层反而增加维护点。

### 3.2 生育方式配置（Race.csv 新列 `birth_type`）【CSV 已于 2026-08-23 提前完成】

- 列定义：字段名 `birth_type`、中文名 `生育方式(1单胎胎生,11带壳卵生,12无壳卵生)`、类型 `int`、翻译标记 `0`。
- **填表已完成**（用户按动物原型指定 11/12，其余由实施方补 1，已用 buildconfig 同款解析逻辑校验 45 行全通过）：
  - `11` 带壳卵生（8 族）：阿达克利斯(6)、黎博利(19)、匹特拉姆(23)、萨弗拉(24)、瓦伊凡(27)、德拉克(32)、斐迪亚(39)、羽蛇(42)
  - `12` 无壳卵生（3 族，本期按胎生处理）：安努拉(11)、阿戈尔(34)、海嗣(35)
  - 其余 34 族均为 `1` 胎生
- 统一入口 `egg_handle.get_birth_type(character_id) -> int`：`getattr(game_config.config_race[race], "birth_type", 1)`；**返回 12 时按 1 处理**（内部归一化，胎生链不感知 12 的存在），全部分支判定只认 `== 11`。
- 弃选：按种族 id 硬编码集合——违背"数据驱动"惯例，改表还要改代码。

### 3.3 卵生阶段流转总设计（与胎生链对照）

| 胎生链（不改动） | 带壳卵生链（新增） | 挂钩点 |
| --- | --- | --- |
| 受精判定（排卵日+体内射精） | **完全复用** `check_fertilization`（talent20 置位当天即被排卵结算消费） | sleep_settle 链 |
| 受精 90 天 → 妊娠 → 260 天 → 临盆（住院） | **排卵结算**：排卵日当天排出受精卵/无精卵，清 talent20，卵入 `pregnancy.eggs` | `check_all_pregnancy` 内分流 |
| — | 次日起持卵者**自行去育儿室鉴定**（"照料卵"娱乐时段内的高优先级行为）：无精 → 静默删除；受精 → 通知玩家+进入孵化 | past_day_settle 娱乐替换 |
| — | 孵化期：每天随机一个娱乐时段替换为"照料卵"娱乐（时段内无待鉴定卵时执行孵化行为） | past_day_settle 娱乐刷新后 |
| 生产事件（Born_Panel，医生+取名） | 受精后 ≥265 天 → **破壳事件**（Born_Panel 卵生模式：同医生选角、同取名、`born_new_character`） | sleep_settle 链 |
| 产后 2 天 → 育儿 | **跳过产后**：破壳当场 talent24 育儿=1、**talent27 泌乳=1**、按罩杯设 `milk_max`（补胎生在妊娠期做的事） | 破壳事件内 |
| 育儿 90 天 → 完成 → 幼女→萝莉→少女 | **完全复用**（`check_rearing_complete` 起与胎生同链） | 不改动 |

- 卵生角色**不获得** talent 21/22/23/26（妊娠/临盆/产后/孕肚），不触发 `check_pregnancy`/`check_near_born`/`check_born`；`check_rearing` 对卵生也跳过（无产后）。分流实现：`check_all_pregnancy` 中按 `get_birth_type()==11` 走 `egg_handle` 子链。
- 孵化总时长取 **265 天**（= 胎生受精→标准生产时长，"90 天在游戏内实际体验是 30 天"的换算惯例不变），基准为 `fertilization_time`。

### 3.4 排卵结算的生成口径【已确认：方案 B】

- **每个排卵日必排一枚卵**：排卵日当天（`reproduction_period == 5`）——当天受精判定成功（talent20 当天置位）→ 排出**受精卵**并清 talent20；否则（含未被内射）→ 排出**无精卵**。
- 无精卵堆积噪音由 §3.5 的 **NPC 自主鉴定 + 无精卵静默废弃**化解：玩家全程不被打扰，只在鉴定出受精卵时收到通知。
- **实施口径修正二（v7 四期，2026-08-23）**：受精判定与排卵结算的触发门由"当前周期==5"的瞬时判定改为**排卵日事件待办标记 `PREGNANCY.ovulation_flag`**——每日 0 点 `update_reproduction_period`（逐角色）推进到排卵日时置位；胎生的受精判定过门后立即消费标记（各 return 路径不残留），卵生的标记由排卵结算消费（含豁免分支）；`past_day_settle` 在周期推进前对标记仍在的角色**兜底补跑**受精判定+排卵结算（0 点结算不依赖玩家睡觉），保证事件最迟在排卵日结束的 0 点结算、永不丢失。附带行为变化：同一排卵日玩家睡多次时受精判定由"每次各判"变为"每周期仅判一次"。
- 同一角色可持有多枚卵（字典多条），未鉴定卵不自动消失。
- 特殊豁免沿用受精判定同款：未初潮（talent6）、无生育模组的机械（race==2 且无 talent171）不排卵。

### 3.5 "照料卵"娱乐与鉴定/孵化行为【已确认：NPC 自主，同一时段两级行为】

- **只新增一个娱乐**：`照料卵`（Entertainment.csv 新行，`place_tag=Nursery`、`auto_ai=1`）。持有任何"需要照料的卵"（满足条件的未鉴定卵 **或** 孵化中卵）的卵生角色，每天由替换钩子把**一个随机娱乐时段**替换为该娱乐——鉴定与孵化**共用这同一个时段**，不各占一段。
- **时段内按优先级分流为两种行为**（`auto_ai_entertainment` 挂"执行照料卵"状态机，状态机内部按卵状态分支设置行为 id）：
  1. **鉴定行为（高优先级）**：存在"排出日 < 今天"且**未被玩家拿走**（§3.10）的未鉴定卵时执行。一次行为把该角色当前全部满足条件的未鉴定卵逐枚揭示——未受精 → **静默删除**（不通知玩家、不弹消息，行为默认口上仅描写鉴定动作不区分结果）；受精 → 置 `identified=True`、记 `identify_time`、**打印消息通知玩家**（WaitDraw + 二段行为 `egg_fertilized`），进入孵化流程。
  2. **孵化行为（低优先级）**：无待鉴定卵而有孵化中卵时执行，风味结算（挂空结算 9999 保口上链路）。
  - 由于 AI 在娱乐时间内会循环取行动，鉴定完成后同一时段的后续行动自然落入孵化行为——两种行为可在同一时段先后发生。
- **v5 修订（保育员主导鉴定）**：照料卵状态机的鉴定分支细化为三支——①自己就是保育员 → 直接自己鉴定；②所在场景有**处于工作时间内的**保育员 → 改为**等待**（WAIT 10 分钟，保育员的工作状态机会以最高优先级为在场角色鉴定）；③其余情况（无在职保育员、保育员不在场或已下班）→ 自己鉴定（兜底，保证卵不会永久滞留）。孵化分支不变（母亲保留每日孵化）。"在场才等待"是为了规避作息死锁：有工作的母亲娱乐时段仅晚间 19~22 点，而保育员工作时间为工作日 9~12/14~18 点，若仅按在职人数判断等待，这类母亲的卵将永远无人鉴定。
- 行为链：`auto_ai_move` 挂"移动到育儿室"状态机；两个行为（鉴定卵/孵化）各有独立的 Behavior 常量、口上与结算，仅入口共用娱乐与分流状态机。
- 玩家不需要任何操作；`identify_egg` 玩家指令**不再新增**（v1 设计废弃）。

### 3.6 照料卵的调度与孵化进度【已确认：方案 A 自然天数推进】

- **防误随机**：`照料卵`娱乐在 `get_chara_entertainment` 随机池构建处按 id 显式排除（照 :817 品酒特判先例）。
- **每日替换钩子**（past_day_settle 娱乐刷新之后，对卵生角色）：有任何需要照料的卵（未鉴定 或 孵化中，**被玩家拿走的未鉴定卵不计入**）→ 随机一个时段替换为 `照料卵`；派对日、监禁等无法自由活动的角色跳过替换（不影响鉴定资格与破壳时点）——**监禁角色的未鉴定卵由 §3.10 的玩家指令兜底处理**。
- **进度推进：自然天数**——破壳判定只看受精时点 ≥265 天，孵化行为是每日固定的风味行为，缺勤不延迟破壳。理由：满足"孵化时长与胎生一致"；避免角色被监禁/旅行/住院等状态打断娱乐导致卵永久卡住的死锁类 BUG（参照近期两个睡眠死循环 BUG 的教训）。
  - **实施口径修正（2026-08-23）**：破壳基准实际取卵自身的 `lay_time`（排出日）而非角色的 `pregnancy.fertilization_time`——受精判定与排卵结算同发生在排卵日当天，两者同日等价；且 `fertilization_time` 会被排卵后的下一次受精覆盖，以卵内自带时间为基准才能保证多卵并存时各自计时正确。
- 卵字典保留 `hatch_stage` 展示字段（面板显示"孵化中·第 N 天"，由自然天数换算）。

### 3.7 破壳事件

- `Born_Panel` 增加卵生模式（构造参数 `egg_mode` 或子类）：复用医生选角、取名、`born_new_character`、Web 子面板包裹；差异点——文案改为破壳；跳过产后素质与 V/W 扩张结算；结算改为：删除对应卵数据、talent24 育儿=1、talent27 泌乳=1、按罩杯设 milk_max、妊娠经验 86+1、`settle_chara_unnormal_flag(id,2)`。
- 触发地点：事件文案设定在医疗部住院区进行（与胎生一致的舞台），但**不要求母亲提前住院**（无临盆），事件由睡眠结算触发时直接演出。**v13**：`Born_Panel` 开头统一调用 `move_to_inpatient_department_for_born(mother_id)`——母亲已在住院区则以其病房为目标，否则随机选一间住院区场景（与 NPC AI 同一 `constant.place_data["Inpatient_Department"]` 表）并把母亲移入，玩家不在该病房时瞬移前往（`map_handle.character_move_scene`，不走寻路/流程推进，可在睡眠结算内调用）；胎生共用同一逻辑作为 AI 尚未传送时的兜底；事件结束后两人留在住院区（用户确认口径）。
- 新增二段行为：`egg_born`（破壳对话）；排卵另增 `lay_egg`（排出卵对话）、鉴定受精 `egg_fertilized`（可并入鉴定指令口上，实施时定夺）。
- 顺手修复 §2.5 所列 :124 现存 BUG。

### 3.8 怀孕总览面板与谱系图【入口已确认】

- 挂载（两处入口，共用同一 Panel）：
  1. **育儿室内指令**：照 `ALL_NPC_POSITION` 全链——新 Panel 常量 + normal_flow 注册 + 系统指令（InstructConfig 新行，空闲 cid 现场核对），**前提挂 `in_nursery`**（玩家在育儿室时指令栏才显示）。
  2. **管理罗德岛界面教育区子系统按钮**：`department_son_panel_button_dict` 加 `_("教育区"):[_("[怀孕育儿系统]")]`（按钮文本实施时定），`jump_to_son_panel` 加对应分支（照医疗经营系统先例，§2.10）。
- **总览页**：列出所有满足"妊娠链素质 20/21/22/23/24 任一 == 1 或 `pregnancy.eggs` 非空"的干员；每行：姓名按钮（点击跳角色详情可选）、当前阶段名、阶段起始/预计事件时间（受精日+90/260/265 推算）。阶段排序键统一枚举：受精1 < 持卵待鉴定2 < 妊娠3 < 孵化中4 < 临盆5 < 产后6 < 育儿7（卵生阶段插在对应时序位置）；按钮切换升/降序；筛选按钮组按阶段过滤（全部/各阶段）。排序与筛选状态存 `Cache` 新字段（照 [game_type.py:1849-1851](Script/Core/game_type.py#L1849) 先例）。
- **谱系图页**（子页签切换；v9 六期改版为**带完整连线的传统家谱图**，v8 的五代分层无连线布局及其代内换行续排机制废弃）：
  - 数据+布局引擎：`build_family_tree_chart(center_id, max_width, page_index)`——上 1 代+中心+下 2 代**共 4 代**（确认口径），每代一个名字行、代与代之间夹一个**排版行**（纯连线行）；沿 `relationship.father_id/mother_id` 上溯、`child_id_list` 下探；空代际跳过（玩家为中心时无父母行）。
  - **完整连线**：夫妇以 `╤` 相连（v10：该符号自带向下接头，原 `═` 废弃），连线**起点**即 `╤` 所在列（无配偶/不在册时无连接符，起点退回人名中点列），向下进入排版行，排版行内以 `┌┬┐┴┼│─└┘├┤` 字形水平分叉过渡，连到该夫妇所生各子辈的名字中点（**终点**不变）。列位以 `text_handle.get_text_index`（wcwidth）为单位制自底向上测宽、自顶向下放置（夫妇文本与子块跨度互相近似居中），整图统一前导缩进保证上下列对齐。**§2.12 约束经用户确认放开（仅限谱系图）**：跨行对齐依赖游戏必需字体等距更纱黑体 SC 的度量（全角=2×半角、制表符半角）。
  - **玩家名按父本位置重复**（v9 用户指定）：游戏设定父本恒为玩家，玩家名不再唯一——每个父本位置各写一遍玩家名（中心行 `•博士╤母1　•博士╤母2`、子女行 `女儿╤•博士`），不画长线连回单一玩家节点；**NPC 名字唯一**并正确连线——归属规则：孩子的另一位家长是更深的血缘节点时，该组孩子挂在对方节点下（乱伦女儿只出现一次、其孩子从她的位置下坠），`placed_set` 先到先得兜底。
  - 同辈：中心有父母时，父母夫妇框下显示中心+**同父同母**的兄弟姐妹（连线语义要求同辈确实出自该夫妇，异母半同辈不再显示，可点击玩家名换中心查看）。
  - **家族分页**（v9 用户指定，取代折叠为主的超宽处理）：顶层家族块（玩家中心时=每个 `博士╤母i` 家族分支连同子孙子树）超宽时 `paginate_family_blocks` 从左到右贪心分页——**一页至少一个家族、家族永不拆散**（如 5 个家族第一页只装得下前 3 个+第 4 个的一半时：第一页=前 3 个，第二页=第 4、5 个）；面板绘制 `[上一页]/[下一页]`+`第X/Y页` 标识（仅多页时），页码越界钳位、换中心/重置时归零；单个家族独占一页仍超宽时兜底从右侧折叠，最深名字行末以 gold `…(+N人)` 标注（隐藏人数按"完全不再显示的角色"精确计数）。
  - 省略号语义（v9 沿用重定义）：行尾 `…(+N人)`=兜底折叠隐藏的人数；人名后 `…`=其在图外还有未显示的父母/子女（点击可探索）——不出现"静默断开"。
  - 交互：全部人物为按钮（点击 → 以其为新中心重绘），中心本人（含各重复位置）`•` 前缀高亮非按钮；`[重置回博士]`；返回按钮回总览页。初始中心 = 玩家。

### 3.9 编号新增汇总（实施时全部现场核对空闲号）

| 类别 | 项目 | 建议区段 |
| --- | --- | --- |
| 二段行为 cid | `lay_egg` / `egg_fertilized` / `egg_born` | 1322~1330 段 |
| 玩家指令 cid | `pregnancy_overview`（开面板，前提 `in_nursery`）、`take_chara_eggs`（拿走产下的卵）、`identify_held_eggs`（鉴定持有的卵） | 对应指令段空闲号 |
| 行为 cid | 鉴定卵行为、孵化行为（"照料卵"时段内分流的 NPC 行为）；拿走卵行为、玩家鉴定行为（玩家指令口上用） | Behavior_Data 空闲号 |
| 结算 id | v12：拿走卵/鉴定持有卵的专用结算 | `constant_effect` 专用指令结算段 500~599 顺延（实取 546/547），ArkEditor `Effect.csv` 同步 |
| 状态机 id | 移动到育儿室、执行照料卵（内部按卵状态分流为鉴定/孵化行为）；v5：保育员照料育儿室（实取 330） | StateMachine 空闲号 |
| 工作 cid | v5：保育员（实取 153，教育区段顺延） | WorkType.csv 空闲号 |
| Panel 常量 | `PREGNANCY_OVERVIEW` | constant.Panel 顺延 |
| 娱乐 cid | 照料卵（仅 1 个） | Entertainment.csv 顺延（175+） |
| 前提 | 卵生种族/持未鉴定卵/持孵化中卵/娱乐是照料卵/交互对象持有可拿走的未鉴定卵/玩家临时持有卵非空 等 | constant_promise 新增（`T_IMPRISONMENT_1` 等监禁前提复用现成），函数放 `handle_premise_other.py` 或新建 `handle_premise_pregnancy.py`【实施时定】 |

### 3.10 监禁角色的卵处理指令（v4）

为监禁中的卵生角色提供玩家代办的鉴定通路，两个玩家指令（照 `TAKE_CARE_BABY`/plan_06 指令全链先例；**v12 起数据结算为正式注册的专用结算 546/547**（`Script/Settle/default.py`），由行为在 `Behavior_Effect.csv` 挂接、于行为结算阶段执行，指令处理函数只做通用结算，行为不再挂 9999）：

- **拿走产下的卵 `take_chara_eggs`**：
  - 前提：`T_IMPRISONMENT_1`（交互对象被监禁，现成）+ 交互对象为卵生 + 交互对象持有**未被拿走的**未鉴定卵。
  - 效果：一次拿走交互对象当前全部未鉴定卵——每枚卵：原卵数据标记 `held_by_player=True`（详细数据**留在原角色** `pregnancy.eggs` 中不动），并向玩家 `pl_collection.held_eggs` 追加一条**索引**（指向该角色的该卵）。
  - 拿走后：该角色的照料卵替换/NPC 鉴定不再计入这些卵（§3.5/§3.6）。
- **鉴定持有的卵 `identify_held_eggs`**：
  - 前提：`held_eggs` 非空 + `in_nursery`（玩家在育儿区）。
  - 效果：一次鉴定玩家临时持有的全部卵。逐条索引找到原角色的卵数据并**同步回写**：
    - 未受精 → 删除原角色的该卵数据 + 删除索引；
    - 受精 → 原卵置 `identified=True`、记 `identify_time`、清 `held_by_player`，打印消息通知玩家（+二段 `egg_fertilized` 由原角色触发），**进入孵化状态**（卵回到育儿室孵化的常规轨道）+ 删除索引。
  - 后续：孵化按自然天数推进（§3.6），破壳事件照常触发；**监禁角色不会进行孵化娱乐**（替换钩子本就跳过监禁角色），其余与正常卵生角色完全一致。
- 索引数据结构见 §4；无"归还卵"指令（鉴定即消耗索引），若原角色在持卵期间死亡/删除，索引清理逻辑在鉴定时兜底（查无此卵则静默移除索引）。

### 3.11 保育员工作（v5 二期）

- **WorkType.csv 新行 cid 153**：`保育员`，部门教育区、地点育儿室（place_tag=Nursery）、ability_id=45（照教育区教师惯例）、`auto_ai=1`、`auto_ai_move=564`（复用移动到育儿室状态机）、`auto_ai_work=330|nursery_have_work_to_do`（带额外前提的工作状态机，照坐诊医生 `301|patient_wait` 先例）。
- **任职资格**：**无限制**（v11 按用户决定取消。原 v5 口径为仅带壳卵生种族 `get_birth_type()==11`、硬编码在工作分配面板过滤段——该过滤段已删除，WorkType 职业要求列为"无"，任何干员均可任保育员）。
- **工作状态机 `WORK_NURSERY_CARE=330`**：
  1. **优先级最高**：所在场景内（含自己）存在持可鉴定卵的角色 → 以其为交互对象执行鉴定卵行为（30 分钟），当场调 `npc_identify_eggs_settle(owner_id, identifier_id=保育员)`——他人代鉴时通知文案为"保育员X为Y鉴定…"，二段 `egg_fertilized` 仍由卵主人触发。
  2. **等权重行为池**（无卵可鉴定时 random.choice）：存在孵化中的卵（任意角色，受精卵均存放于育儿室）→ 孵化卵行为（60 分钟）；场景内有婴儿（talent101）→ 随机执行既有照料婴儿行为 261~266 之一（抱小孩/哼唱儿歌/喂奶/换尿布/教说话/给玩具，30 分钟，复用现成行为与口上，NPC 侧此前零引用）。
  3. 池空兜底：WAIT 1 分钟（前提门控下一般不触发）。
- **前提 `nursery_have_work_to_do`**：所在场景有持可鉴定卵的角色 或 存在孵化中的卵 或 场景内有婴儿——不满足时保育员自然落入通用目标（休息/闲聊等），不空转。
- 另备前提 `work_is_nursery_worker` / `t_work_is_nursery_worker`（口上与后续扩展用）。
- 育儿室不在 Facility_open.csv 中，保育员不做设施解锁门禁（与教师一致）。

## 4. 数据结构设计（权威定义）

`class PREGNANCY`（game_type.py）新增字段：

```python
self.eggs: Dict[int, Dict] = {}
""" 带壳卵生角色排出的卵，键为卵编号（自增，取 next_egg_id），值为卵数据字典：
    {
        "lay_time": datetime.datetime,      # 排出时间（排卵日当天）
        "identified": bool,                  # 是否已鉴定（未鉴定不可进入孵化）
        "fertilized": bool,                  # 是否受精（排出时即确定，鉴定只是揭示；未受精卵鉴定后即删除本条）
        "identify_time": datetime.datetime,  # 鉴定时间（受精卵进入孵化流程的起点记录）
        "father_id": int,                    # 父亲id（恒为0，预留）
        "hatch_stage": int,                  # 孵化阶段展示值（按自然天数换算，面板显示用）
        "held_by_player": bool,              # v4：该卵是否已被玩家拿走（拿走后本人的照料卵/NPC鉴定不再计入该卵）
    } """
self.next_egg_id: int = 0
""" 卵编号自增计数器 """
```

`class PLAYER_COLLECTION`（game_type.py:878）新增字段（v4）：

```python
self.held_eggs: Dict[int, tuple] = {}
""" 玩家临时持有的卵（从被监禁角色处拿走的未鉴定卵），仅为索引数据：
    键为持有编号（自增，取 next_held_egg_id），值为 (角色id, 卵编号) 元组，
    指向该角色 pregnancy.eggs 中的详细数据；鉴定后索引即消耗删除 """
self.next_held_egg_id: int = 0
""" 持有编号自增计数器 """
```

- 旧存档回填（save_handle.py:259-274 段追加）：`pregnancy` 对象缺 `eggs`/`next_egg_id`、`pl_collection` 缺 `held_eggs`/`next_held_egg_id` 时补空值。
- `Cache` 新增：`pregnancy_panel_sort_type: int`（0 降序/1 升序）、`pregnancy_panel_filter_type: int`（0 全部/按阶段枚举）——面板状态持久化。
- Race 配置对象：新属性 `birth_type: int`（config_def 自动生成，访问经 `egg_handle.get_birth_type` 兜底）。

## 5. 界面信息架构（怀孕面板）

```text
[怀孕状态总览]  （入口①玩家在育儿室时的系统指令；入口②管理罗德岛界面→教育区→[怀孕育儿系统]按钮）
┌ 页签：总览 | 生育谱系图
├ 总览页：
│   [排序：按阶段▲/▼] [筛选：全部|受精|持卵|妊娠|孵化|临盆|产后|育儿]
│   干员名   阶段        关键时间
│   XXX     妊娠        受精于X月X日 / 预计X月X日临盆
│   YYY     孵化中·N天  预计X月X日破壳
├ 谱系图页（v9 连线家谱图示意）：
│   [重置回博士]
│        •博士╤干员甲        •博士╤干员乙
│      ┌────┴────┐             │
│   女儿A╤•博士   女儿B       女儿C
│       │
│    外孙女D
│   [上一页] 第1/2页 [下一页]   （超宽时按家族分页）
└ 返回
```

## 6. 风险与注意事项

| 风险 | 说明 | 对策 |
| --- | --- | --- |
| 存档兼容 | 旧存档 `PREGNANCY` 缺新字段；旧存档中途升级时已有孕程角色不受影响（胎生链不改） | save_handle 回填 + 单元测试构造缺字段对象 |
| 文件迁移漏改 | pregnancy/sp_event_panel 迁移后 import 失效 | §2.11 引用全量清单已穷举（4 处），迁移后全局 grep 复核 |
| 生产链回归 | Born_Panel 扩展卵生模式可能破坏胎生路径 | 胎生分支代码路径不动，卵生走新分支；两条路径分别测试 |
| 娱乐替换冲突 | 照料卵娱乐与派对日覆盖、幼女固定娱乐、监禁/住院等状态冲突 | 替换钩子放在 get_chara_entertainment 之后，仅覆盖一个时段（鉴定与孵化在该时段内按优先级分流）；特殊状态角色（监禁等）跳过替换；破壳与鉴定资格不依赖行为实际执行（§3.5/§3.6） |
| 随机池污染 | 照料卵娱乐被随机分给无卵角色 | 随机池显式排除该 id + 前提双保险 |
| 未鉴定卵滞留 | NPC 长期无法娱乐（监禁等）时未鉴定卵堆积 | 卵数据不过期不丢失，角色恢复自由后次日即自动鉴定；**监禁角色可由玩家用拿走/鉴定指令代办（§3.10）**；面板中滞留卵可见 |
| 索引-数据同步 | v4 的 held_eggs 索引与原角色卵数据可能失同步（角色删除、卵被其他路径消耗） | 卵详细数据单一来源在原角色处，索引仅指针；拿走时置 `held_by_player` 防本人重复鉴定；玩家鉴定时查无此卵则静默清索引 |
| 编号冲突 | 指令/行为/状态机/二段行为编号占用 | 实施时逐表现场核对（plan_06 教训） |
| 谱系图对齐 | 框线字符跨行列对齐在部分字体/字号下错位 | v9 起为用户确认的连线布局：列位统一以 wcwidth 为单位制、整图共用前导缩进，对齐依赖游戏必需字体等距更纱黑体 SC；其他界面仍禁止跨行列对齐 |
| Web 模式 | 新面板/破壳事件的 Web 呈现 | 只用抽象绘制类；破壳复用 BORN_EVENT_PANEL_TAB_ID 包裹；Tk/Web 双模式测试 |

## 7. 不在本方案范围

- `12` 无壳卵生的差异化实现（本次归一化为胎生，仅占位枚举；安努拉/阿戈尔/海嗣三族已在表中标 12 待后续实装）。
- 卵生相关口上的大规模风味文本（每个新行为仅默认口上约 5 条）。
- 谱系图导出/图片化、跨周目谱系归档。
- 胎生链既有数值（90/260/265 天、概率公式）的任何调整。

## 8. 口径确认记录（2026-08-23，全部已确认）

| # | 问题 | 用户确认结果 | 方案落点 |
| --- | --- | --- | --- |
| 1 | 排卵生成口径 | **每个排卵日必排**；且鉴定由 **NPC 自己进行**（非玩家指令），鉴定出未受精**不通知玩家** | §3.4、§3.5（v1 的玩家鉴定指令设计废弃） |
| 2 | 孵化进度口径 | 方案 A：自然天数推进 | §3.6 |
| 3 | 谱系图默认代数 | 上下各 2 代（`MAX_GEN=2`）；**v9 改为上 1 代+中心+下 2 代共 4 代**（连线布局确认口径） | §3.8 |
| 4 | 鉴定方式 | **一次全部鉴定**（该角色全部满足条件的未鉴定卵一次行为内逐枚揭示） | §3.5 |
| 5 | 面板入口 | 单独指令、**玩家在育儿室时可用**；并在**管理罗德岛界面教育区**加子系统快捷入口（照其他地区面板先例） | §3.8、§2.10 |
| 6 | 鉴定/孵化的时段占用（追加修订） | **不各占一个时段**：合并为同一个特殊娱乐"照料卵"占一个随机时段，时段内为两个优先级不同的行为（鉴定 > 孵化） | §3.5、§3.6（v3） |
| 7 | 监禁角色的卵处理（追加需求） | 新增两个玩家指令：**拿走产下的卵**（被监禁者的未鉴定卵→玩家临时持有，`PLAYER_COLLECTION` 存索引非详细数据）、**鉴定持有的卵**（育儿区可用，经索引同步回写原角色卵数据，未受精删除/受精进孵化）；监禁角色无法孵化娱乐，其余与正常卵生一致 | §3.10、§4（v4） |

## 9. 调查与编写进度

- [x] 2.1 pregnancy.py 函数清单
- [x] 2.2 数据结构调查
- [x] 2.3 二段行为结算链
- [x] 2.4 每日/实时结算钩子
- [x] 2.5 生产事件流程
- [x] 2.6 临盆住院与育儿室
- [x] 2.7 生理周期与排卵日
- [x] 2.8 Race.csv 加载链
- [x] 2.9 NPC 娱乐时间系统
- [x] 2.10 面板先例与挂载点
- [x] 2.11 分散文件整合范围（引用全量清单）
- [x] 2.12 已知陷阱与硬约束
- [x] 设计决策成稿
- [x] 数据结构权威定义（§4）
- [x] 用户确认 §8 清单（2026-08-23）→ 方案定稿（v2）
- [x] 实施文档 `plan_12_怀孕系统升级_实施步骤与记录.md` 已按 v2 口径同步
- [x] 开始实施（2026-08-23 用户指示）
- [x] 实施完成（2026-08-23）：八步全部完成，无头单元测试 59/59 通过；唯一方案微调为破壳基准取卵 `lay_time`（§3.6 实施口径修正）；游戏内整体测试清单待用户执行（实施文档 §6.4）
- [x] 二期实施完成（2026-08-23，v5）：分类归位（工作/猥亵）、保育员工作（§3.11）、保育员主导鉴定（§3.5 v5 修订）；单元测试 76/76 通过（含一期全量回归）；实施记录见实施文档 §6.4
- [x] 三期实施完成（2026-08-23，v6）：新增行为/指令按类型段重新编号并归位（行为 267/268/269/345、指令 2052/2053/5105、整数常量 267/268/269/354）；全量回归 76/76 通过；实施记录见实施文档 §6.4 三期段
- [x] 四期实施完成（2026-08-23，v7）：修复排卵日事件被"玩家不睡觉"错过丢失的 BUG（`ovulation_flag`+0 点兜底，§3.4 实施口径修正二）；全量回归 89/89 通过；实施记录见实施文档 §6.4 四期段
- [x] 五期实施完成（2026-08-23，v8）：谱系图改传统家谱式五代分层（§3.8 v8 改版，含一父多母极端场景保障）；全量回归 100/100 通过；实施记录见实施文档 §6.4 五期段
- [x] 六期实施完成（2026-08-24，v9）：谱系图改带完整连线的传统家谱图（四代+排版行+玩家名按父本位置重复+家族分页，§3.8 v9 改版）；全量回归 108/108 通过；实施记录见实施文档 §6.4 六期段
- [x] 六期修正 v10（2026-08-25）：夫妇连接符 `═`→`╤`、连线起点改为 `╤` 所在列（终点不变）；全量回归 108/108 通过（J4b/J6c/J7 断言按新起点强化）
- [x] 二期修正 v11（2026-08-25）：取消保育员种族限制（代码侧由用户删除，文档同步）
- [x] v12（2026-08-25）：拿走卵/鉴定持有卵改为正式注册的专用结算 546/547 并由行为挂接调用；lay_egg 改 997；全量回归 111/111 通过；实施记录见实施文档 §6.4 v12 段
- [x] v13（2026-08-25）：生育/破壳事件开始时母亲与玩家统一移动到医疗部住院区（事件后留在住院区）；全量回归 119/119 通过；实施记录见实施文档 §6.4 v13 段
- [x] v14（2026-08-25）：子系统设计文档改为纯索引，实际内容并入工作流文档 `妊娠系统.md`（同号章节）；实施记录见实施文档 §6.4 v14 段

## 10. 后续修改（随 plan_17 第 3 次修改，2026-08-29）

- （随 plan_18，2026-08-29）`Race.csv` 生育方式新增 **`2` 多胎胎生**（卡特斯/奇美拉、阿纳缇、阿斯兰、菲林、卡特斯、鲁珀、佩洛、乌萨斯、札拉克九族），并新增 `multiple_birth_num` 列；本方案 §2/§4 中"胎生 == 1"的判定已改为 `egg_handle.is_viviparous()`（1 或 2），卵生分支仍只认 11。详见 `plan_18_多胞胎机制.md`。
- （随 plan_19，2026-08-29）`12` 无壳卵生实装：`get_birth_type` 不再把 12 归一化为 1；`check_egg_born` 改为对无壳卵生批量收集到期卵，`Born_Panel` 的 `egg_id` 参数改为 `egg_id_list`（带壳传单元素列表）；`check_all_pregnancy` 对 12 只跑破壳链；`replace_entertainment_for_eggs` 放行 12。详见 `plan_19_无壳卵生机制_方案.md`。

- 谱系图代数由 v9 确认口径的"上 1 代+中心+下 2 代共 4 代"改为**上 2 代+中心+下 4 代共 7 代**（`pregnancy_constant.UP_GEN=2 / DOWN_GEN=4`）；向上攀升改为按 `UP_GEN` 逐代进行，夫妇框左侧为有在册父母的血亲（母亲有父母时母亲居左、玩家名落在 ╤ 右侧），到达上限或血亲无父母时以省略号标记未显示的祖辈。本文 §3 / §8 中"4 代"的描述以此为准，原文不改写；改动明细与回归测试（107/107）见 `plan/done/plan_17_养成系统三种新药物.md` §12.7。
