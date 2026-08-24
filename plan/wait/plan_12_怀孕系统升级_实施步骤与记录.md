# Plan 12（实施步骤与记录）：怀孕系统升级

> 本文件是 `plan_12_怀孕系统升级_方案.md`（下文简称"方案"）的**实施步骤清单与过程记录**。
> 需求背景、现状调查、设计决策、数据结构定义、风险与范围外事项一律以方案文档为准；
> 本文件只写"怎么做、怎么验、怎么回滚"，实施过程与结果记入 §6。

- 状态：**一~六期及 v10~v14 修正实施完成（2026-08-25，单元测试 119/119 通过，详见 §6；游戏内整体测试 §4.2/§6.5 待用户执行）**
- 适用代码快照：`master @ ba388bc60`
- 实施前提：先通读方案文档；实施中发现与方案冲突的事实，**先更新方案再动代码**

## 1. 改动文件清单

| 文件 | 类型 | 改动 |
| --- | --- | --- |
| `Script/System/Pregnancy_System/__init__.py` | 新增 | 子系统包 |
| `Script/System/Pregnancy_System/pregnancy_handle.py` | 迁移 | 原 `Script/Design/pregnancy.py` 整体迁入；`check_all_pregnancy` 内加卵生分流 |
| `Script/System/Pregnancy_System/egg_handle.py` | 新增 | `get_birth_type`、排卵结算、卵增删查、鉴定结算、破壳判定、娱乐替换钩子函数 |
| `Script/System/Pregnancy_System/born_event_panel.py` | 迁移+扩展 | 原 `Script/UI/Panel/sp_event_panel.py` 迁入；`Born_Panel` 增加卵生（破壳）模式；修 :124 现存 BUG |
| `Script/System/Pregnancy_System/pregnancy_panel.py` | 新增 | 怀孕总览面板（排序/筛选 + 谱系图子页签） |
| `Script/System/Pregnancy_System/family_tree_draw.py` | 新增 | 谱系树构建（上下各 MAX_GEN 代）与纵向缩进树绘制 |
| `Script/System/Pregnancy_System/怀孕系统设计文档.md` | 新增 | 子系统设计文档（v14 起改为纯索引，实际内容并入 `.github/prompts/数据处理工作流/妊娠系统.md`） |
| `Script/Design/pregnancy.py` | 删除 | 迁移后删除（引用方全部改路径） |
| `Script/UI/Panel/sp_event_panel.py` | 删除 | 迁移后删除 |
| `Script/Settle/sleep_settle.py` | 修改 | :12 import 与 :88 调用改新路径 |
| `Script/Settle/past_day_settle.py` | 修改 | :14 import 与 :67 调用改新路径；娱乐刷新后追加孵化娱乐替换钩子 |
| `Script/UI/Panel/ejaculation_panel.py` | 修改 | :436 函数内 import 改新路径 |
| `Script/Core/game_type.py` | 修改 | `PREGNANCY` 新增 `eggs` / `next_egg_id`；`PLAYER_COLLECTION`（:878）新增 `held_eggs` / `next_held_egg_id`（定义以方案 §4 为准）；`Cache` 新增面板排序/筛选字段 |
| `Script/Core/save_handle.py` | 修改 | :259-274 段追加 `pregnancy.eggs` / `next_egg_id` 与 `pl_collection.held_eggs` / `next_held_egg_id` 回填 |
| `Script/Core/constant/__init__.py` | 修改 | 新 Panel 常量 `PREGNANCY_OVERVIEW` |
| `Script/Core/constant/Behavior.py` / `BehaviorStr.py` / `Behavior_Int.py` / `CharacterStatus.py` | 修改 | 鉴定卵行为、孵化行为常量 |
| `Script/Core/constant/StateMachine.py` | 修改 | 移动到育儿室、执行照料卵（内部按卵状态分流为鉴定/孵化行为）两个状态机常量 |
| `Script/StateMachine/default.py` | 修改 | 上述两个状态机实现 |
| `Script/Core/constant_promise.py` | 修改 | 新前提枚举（卵生种族/持未鉴定卵/持孵化中卵/娱乐是照料卵/交互对象持可拿走未鉴定卵/玩家临时持有卵非空/交互对象版若干；监禁复用现成 `T_IMPRISONMENT_1`） |
| `Script/Design/handle_premise/handle_premise_other.py`（或新建 `handle_premise_pregnancy.py`） | 修改 | 新前提判定函数（实施时定落点，若新建需在 `__init__.py` 注册） |
| `Script/Design/handle_npc_ai.py` | 修改 | `get_chara_entertainment` 随机池排除孵化娱乐 id（照 :817 品酒先例） |
| `Script/System/Instruct_System/Instruct.py` | 修改 | `PREGNANCY_OVERVIEW`、`TAKE_CHARA_EGGS`、`IDENTIFY_HELD_EGGS` 指令常量 |
| `Script/System/Instruct_System/handle_instruct.py` | 修改 | 开面板指令处理函数（`cache.now_panel_id = constant.Panel.PREGNANCY_OVERVIEW`）；拿走卵/鉴定持有卵两个指令处理函数（内联结算，调 `egg_handle`；**v12 起仅通用结算，数据结算由专用结算 546/547 完成**） |
| `Script/UI/Flow/normal_flow.py` | 修改 | 怀孕总览面板流注册 |
| `Script/UI/Panel/manage_basement_panel.py` | 修改 | `department_son_panel_button_dict` 加教育区 `[怀孕育儿系统]` 按钮 + `jump_to_son_panel` 分支（:88-102 / :807） |
| `data/csv/Race.csv` | 修改 | **已完成（2026-08-23）**：新列 `birth_type`，用户指定 8 族=11、3 族=12，其余 34 行补 1，解析校验通过（方案 §3.2） |
| `data/csv/Entertainment.csv` | 修改 | 新行"照料卵"仅 1 行（place_tag=Nursery，auto_ai=1，挂移动+执行照料卵状态机） |
| `data/csv/Behavior_Data.csv` | 修改 | 鉴定卵行为、孵化行为（NPC 娱乐行为）；拿走卵行为、玩家鉴定行为（玩家指令口上用）；二段行为 `lay_egg` / `egg_fertilized` / `egg_born`（1322+ 段现场核对） |
| `data/csv/Behavior_Effect.csv` | 修改 | 新行为挂 9999 空结算保口上（v12：拿走卵/鉴定持有卵改挂专用结算 546/547）；二段行为挂 998 Must_Show（v12：lay_egg 改 997 Must_Settle） |
| `data/csv/Behavior_Introduce.csv` | 修改 | 新行为介绍 |
| `data/csv/InstructConfig.csv` | 修改 | `pregnancy_overview`（前提 `in_nursery`）、`take_chara_eggs`（前提 `t_imprisonment_1`+卵生+持可拿走未鉴定卵）、`identify_held_eggs`（前提 持有卵非空+`in_nursery`），照 1018 行样式 |
| `data/talk/system/second_pregnancy.csv` | 修改 | `lay_egg` / `egg_fertilized` / `egg_born` 默认口上各约 5 条 |
| `data/talk/`（鉴定/孵化/拿走卵/玩家鉴定行为口上 CSV，目录实施时对齐同类） | 新增 | 每行为默认口上约 5 条 |
| `tools/ArkEditor/csv/Behavior_Data.csv` / `Premise.csv` | 修改 | 编辑器副本同步 |
| `.github/prompts/数据处理工作流/妊娠系统.md` | 修改 | 更新为新架构说明（指向子系统目录） |
| `data/data.json`、`Script/Config/config_def.py`、`data/po/` | 重建 | 由 `buildconfig.py` 生成 |

**未改动**：胎生链数值与判定（pregnancy_handle 内原函数逻辑）、`judge_character_cant_move` 住院逻辑、`realtime_settle` 泌乳产奶、`born_new_character`、二段行为既有 1311~1321 行。

## 2. 详细改动步骤

> 建议按以下顺序实施，每步完成后可独立验证。数据结构、字段名、口径以方案 §3/§4 为准。

### 2.1 第一步：文件迁移（纯搬家，不加新功能）

1. 新建 `Script/System/Pregnancy_System/`（`__init__.py` 空包）。
2. `git mv Script/Design/pregnancy.py Script/System/Pregnancy_System/pregnancy_handle.py`；`git mv Script/UI/Panel/sp_event_panel.py Script/System/Pregnancy_System/born_event_panel.py`。
3. 改 4 处引用（方案 §2.11 清单）：`sleep_settle.py:12`、`past_day_settle.py:14`、`ejaculation_panel.py:436`、`pregnancy_handle.py:19`（原 pregnancy.py 对 sp_event_panel 的 import）。
4. 全局 grep `sp_event_panel` / `Design import pregnancy` 复核归零。
5. **此步单独可测**：启动游戏 + debug 面板走一遍胎生链（受精→生产→育儿）确认无回归。

### 2.2 第二步：数据结构与 Race 列

1. `game_type.py`：`PREGNANCY` 加 `eggs` / `next_egg_id`（代码块以方案 §4 为准）；`Cache` 加 `pregnancy_panel_sort_type` / `pregnancy_panel_filter_type`。
2. `save_handle.py:259-274` 段追加回填。
3. `Race.csv` 加 `birth_type` 列——**已提前完成**（2026-08-23，表头 4 行 + 45 数据行全部有值，无空值陷阱；分布见方案 §3.2），本步实施时仅需跳过。
4. `egg_handle.py` 建立：`get_birth_type()`（getattr 兜底、12 归一为 1）。
5. 跑 `buildconfig.py`，确认 `config_def.Race` 出现 `birth_type`。

### 2.3 第三步：排卵结算与卵数据

1. `egg_handle.py`：`check_ovulation(character_id)` —— 方案 §3.4（**每个排卵日必排**）：排卵日当天受精成功 → 受精卵并清 talent20，否则 → 无精卵；未初潮/无生育模组机械豁免；`add_egg` / `remove_egg` / `get_unidentified_eggs` / `get_hatching_eggs` 等工具函数。
2. `pregnancy_handle.check_all_pregnancy` 内分流：`get_birth_type()==11` 时跳过 `check_pregnancy/check_near_born/check_born/check_rearing`，改走 `egg_handle.check_ovulation` + `egg_handle.check_egg_born`。
3. 新二段行为 `lay_egg`（Behavior_Data 1322+ 现场核对 + Behavior_Effect 挂 998（v12 改 997）+ second_pregnancy.csv 口上）。

### 2.4 第四步："照料卵"NPC 行为链（方案 §3.5/§3.6）

1. 前提函数与常量（constant_promise + handle_premise 落点：卵生种族/持未鉴定卵/持孵化中卵/娱乐是照料卵）。
2. 状态机两件：常量 + `StateMachine/default.py` 实现——移动到 Nursery、**执行照料卵**（状态机内部按卵状态分流：有满足条件的未鉴定卵 → 设鉴定行为；否则有孵化中卵 → 设孵化行为；AI 在时段内循环取行动，鉴定完成后自然衔接孵化）。
3. 两个行为（Behavior_Data/Effect/Introduce + 常量四件套 + 默认口上 CSV）：
   - **鉴定卵行为结算（高优先级）**：一次揭示该角色全部满足条件（排出日 < 今天）的未鉴定卵——未受精 → 静默删除（无消息）；受精 → 置 identified、记 identify_time、WaitDraw 通知玩家 + 二段 `egg_fertilized`。
   - **孵化行为结算（低优先级）**：风味结算（挂 9999 保口上），不推进破壳时点。
4. `Entertainment.csv` 新行"照料卵"（仅 1 行）；`get_chara_entertainment` 随机池按 id 排除（照 :817 品酒先例）。
5. `past_day_settle.py` 娱乐刷新后调 `egg_handle.replace_entertainment_for_eggs`：有任何需要照料的卵（未鉴定 或 孵化中）→ 随机一个时段替换为照料卵；监禁等特殊状态跳过。
6. ArkEditor `Premise.csv` / `Behavior_Data.csv` 副本同步。

### 2.5 第五步：监禁角色的卵处理指令（方案 §3.10，v4）

1. 数据结构：`PLAYER_COLLECTION.held_eggs` / `next_held_egg_id`（方案 §4）；卵数据字段 `held_by_player`；`save_handle` 回填（已含在 §2.2 一并做亦可，实施时合并）。
2. `egg_handle.py` 工具函数：`take_eggs_from_chara(chara_id)`（全部未鉴定卵置 `held_by_player=True` 并写玩家索引）、`identify_held_eggs()`（逐索引回写原角色卵数据：未受精删卵+删索引；受精置 identified/identify_time/清 held 标记+删索引+通知；查无此卵静默清索引）。
3. 前提函数与常量：交互对象持可拿走的未鉴定卵、玩家临时持有卵非空（监禁复用 `T_IMPRISONMENT_1`）。
4. 指令全链（照 `take_care_baby` 先例）：`Instruct.py` 常量 ×2、`handle_instruct.py` 处理函数 ×2（内联结算；v12 改为专用结算 546/547 由行为挂接）、`InstructConfig.csv` 两行、拿走卵/玩家鉴定两个行为（Behavior_Data/Effect 9999/Introduce + 常量四件套）+ 默认口上。
5. 与 NPC 链的互斥核对：`held_by_player=True` 的卵不计入照料卵替换与 NPC 鉴定（§2.4 的 `get_unidentified_eggs` 统一加过滤参数）。
6. ArkEditor 副本同步。

### 2.6 第六步：破壳事件

1. `born_event_panel.Born_Panel` 加卵生模式（方案 §3.7：同医生/取名/`born_new_character`；结算差异——删卵、talent24=1、talent27=1、按罩杯设 milk_max、经验 86+1、unnormal_flag(2)；跳过产后与 V/W 扩张）。
2. 修复 :124 现存 BUG（`character_id` → `self.mother_character_id`，胎生路径一并受益）。
3. `egg_handle.check_egg_born`：受精后 ≥265 天触发破壳事件面板。
4. 新二段行为 `egg_born` + 口上。

### 2.7 第七步：怀孕总览面板与谱系图

1. `family_tree_draw.py`：谱系树数据构建（上溯 father/mother、下探 child_id_list、MAX_GEN 截断）+ 缩进树行生成。
2. `pregnancy_panel.py`：总览页（阶段枚举、排序、筛选、行绘制）+ 谱系图页（角色按钮点击换中心、重置回博士）。
3. 入口①：Panel 常量 + `normal_flow.py` 注册 + `pregnancy_overview` 指令全链（InstructConfig 前提挂 `in_nursery`）。
4. 入口②：`manage_basement_panel.py` 教育区子系统按钮（`department_son_panel_button_dict` + `jump_to_son_panel` 分支，照医疗经营系统先例）。
5. Tk 与 Web 双模式核验。

### 2.8 第八步：文档

1. `怀孕系统设计文档.md`（子系统内）撰写。
2. 更新 `.github/prompts/数据处理工作流/妊娠系统.md` 指向新架构。

## 3. 构建与缓存

```bash
# 本机必须用 conda 解释器（裸 python 是 Store 空壳别名）
.conda\python.exe buildconfig.py   # 每次改 CSV/常量后全量重建（data.json / config_def.py / PO）
.conda\python.exe buildpo.py       # 新增可翻译词条（指令名/行为名/口上/面板文本）后
.conda\python.exe buildmo.py
```

- 本 Plan 改动 6+ 张 CSV 与多处常量，**每个实施步骤完成后都需重跑 buildconfig**。
- 不涉及地图缓存。

## 4. 验证清单

### 4.1 单元测试（实施方执行，scratchpad 脚本，无头环境照 skill `headless-game-test`）

- [x] 迁移后：`pregnancy_handle` / `born_event_panel` 可导入，全局无残留旧路径引用；胎生链函数行为与迁移前一致（H1 直调验证）
- [x] `get_birth_type`：正常 11/1、缺列 getattr 兜底 1、12 归一为 1（A 组 4 断言）
- [x] `check_ovulation`：排卵日+受精 → 受精卵入字典且 talent20 清零；排卵日+未受精 → 无精卵；非排卵日不生成；未初潮不排卵；卵编号自增不重复（B 组 6 断言；无模组机械豁免为受精链同款代码，未单测）
- [x] 鉴定结算：一次全部——未受精卵静默删除（零绘制输出）、受精卵置 identified+identify_time；当天排出的卵不参与鉴定；受精时有通知（C 组 6 断言）
- [x] 娱乐替换：持需照料卵者恰一个时段被覆盖；胎生/监禁/无卵不替换；随机池 30 轮永不出现（D 组 5 断言；时段内鉴定>孵化分流在状态机实现中，实机验证）
- [x] 监禁卵指令（v4）：拿走标记与索引、本人不再计入、玩家鉴定回写/删除/通知、失效索引静默清理、三前提实测（E 组 11 断言）
- [x] 破壳判定：≥265 天触发（真实 Born_Panel 卵生模式全流程）；卵删除、talent24/27=1、milk_max 正确、不获得 21/22/23/26、新生儿关系正确（F/G 组 10 断言）
- [x] 胎生回归：受精 90 天→妊娠链正常；卵生不进入妊娠链（H 组 4 断言）
- [x] 谱系树构建：中心/多代/MAX_GEN 截断+省略号/换中心（J 组 5 断言）
- [x] 旧存档兼容：缺四个新字段的结构体走 `_normalize_loaded_save_paths` 回填不报错（I 组 4 断言）
- [x] `buildconfig.py` 全量重建无报错，新常量/前提/行为/娱乐/Race 列在生成物中齐备（运行时读取验证）

### 4.2 游戏内整体测试（由用户执行）

- [ ] debug 模式改某干员种族为卵生（或改 Race.csv 测试行）走完整卵生链：内射→排卵日排卵→次日 NPC 在"照料卵"时段自行去育儿室鉴定（无精卵无声消失、受精卵收到通知）→每日照料卵时段孵化→破壳事件（医生+取名）→泌乳+育儿→幼女成长
- [ ] 胎生干员全链无回归；临盆住院、照顾婴儿指令正常
- [ ] 监禁卵生干员流程（v4）：监禁中排卵→"拿走产下的卵"指令在关押区对其可用→玩家到育儿室"鉴定持有的卵"→受精卵进入孵化并正常破壳（监禁角色不进行孵化娱乐）
- [ ] 怀孕总览面板两个入口均可打开：育儿室内指令（不在育儿室时不显示）、管理罗德岛界面教育区按钮
- [ ] 怀孕总览面板：排序/筛选正确；胎生与卵生阶段混排正确
- [ ] 谱系图：多代显示、点击换中心、重置回博士；行宽在窗口内不折行错位
- [ ] Tk 与 Web 两种绘制模式均正常（面板 + 破壳事件）
- [ ] 旧存档载入不报错；口上/前提过滤正常

## 5. 回滚

按可独立回滚的单元分组：

1. **文件迁移**（§2.1）：`git mv` 回原路径 + 还原 4 处 import。独立可回滚。
2. **数据结构与 Race 列**（§2.2）：还原 game_type/save_handle 改动与 Race.csv 列；存档中多余 `eggs` 字段不影响旧代码读取（pickle 忽略未知属性访问）。需重跑 buildconfig。
3. **卵生逻辑链**（§2.3~2.6，含 v4 监禁卵指令）：删除 egg_handle.py 与各 CSV 新行/常量/状态机/前提/两个玩家指令；`check_all_pregnancy` 分流还原；存档中多余 `held_eggs` 字段不影响旧代码。需重跑 buildconfig。
4. **面板**（§2.7）：删除两个面板文件 + Panel 常量 + 流注册 + 指令行 + manage_basement_panel 的教育区按钮与跳转分支。独立可回滚，需重跑 buildconfig。

## 6. 实施过程记录

### 6.1 实际改动

**第一步：文件迁移（§2.1）——已完成（2026-08-23）**

- 新建 `Script/System/Pregnancy_System/__init__.py`（空包）。
- `git mv Script/Design/pregnancy.py → Script/System/Pregnancy_System/pregnancy_handle.py`；`git mv Script/UI/Panel/sp_event_panel.py → Script/System/Pregnancy_System/born_event_panel.py`（git 已识别为 R 重命名）。
- 4 处引用全部改为新路径（与方案 §2.11 清单一致）：
  - `sleep_settle.py`：多行 import 移除 `pregnancy`，新增 `from Script.System.Pregnancy_System import pregnancy_handle`；:88 调用改 `pregnancy_handle.check_all_pregnancy`
  - `past_day_settle.py`：同上；:67 调用改 `pregnancy_handle.update_reproduction_period`
  - `ejaculation_panel.py:436`：函数内 import 改 `from Script.System.Pregnancy_System import pregnancy_handle`
  - `pregnancy_handle.py:19`：`sp_event_panel` 改 `from Script.System.Pregnancy_System import born_event_panel`，:258 调用同步改名
- 验证：全局 grep `sp_event_panel` / `Design import pregnancy` / 多行 `pregnancy,` 归零；按游戏初始化链导入 5 个受影响模块冒烟测试通过（IMPORT OK）。

**第二步：数据结构与 Race 列（§2.2）——已完成（2026-08-23）**

- `game_type.py`：`PREGNANCY` 新增 `eggs`/`next_egg_id`（定义与方案 §4 一致）；`PLAYER_COLLECTION` 新增 `held_eggs`/`next_held_egg_id`；`Cache` 新增 `pregnancy_panel_sort_type`/`pregnancy_panel_filter_type`。
- `save_handle.py` 回填段（避孕套回填之后）：`pregnancy.eggs`/`next_egg_id`、`pl_collection.held_eggs`/`next_held_egg_id` 四项 hasattr 回填。
- `Race.csv` birth_type 列为提前完成项，实施时仅复核（8 族=11、3 族=12、其余=1，45 行全有值）。
- `egg_handle.py` 建立，`get_birth_type()` 含 getattr 兜底与 12→1 归一化。
- buildconfig 全量重建通过；生成物验证：`config_def.Race.birth_type` 存在，运行时读取 11 族=[6,19,23,24,27,32,39,42]、12 族=[11,34,35]，与方案 §3.2 完全一致。

**第三~六步：卵生逻辑链（§2.3~2.6）——已完成（2026-08-23）**

- 编号现场核对结果（与方案 §3.9 建议一致）：
  - 二段行为：`lay_egg=1322`、`egg_fertilized=1323`、`egg_born=1324`（1316 保留空置）
  - 行为：`identify_eggs=175`、`hatch_eggs=176`（npc 娱乐）、`take_chara_eggs=177`、`identify_held_eggs=178`（pl 日常）
  - 状态机：`MOVE_TO_NURSERY=564`（教育区段顺延）、`ENTERTAIN_TEND_EGGS=427`（娱乐段顺延）
  - Panel：`PREGNANCY_OVERVIEW=67`；指令：`1036 pregnancy_overview`、`1037 take_chara_eggs`、`1038 identify_held_eggs`；娱乐：`175 照料卵`
- 常量七件套：`Behavior.py`/`BehaviorStr.py`/`Behavior_Int.py`/`CharacterStatus.py`（4 行为）+ `SecondBehavior.py`/`SecondBehavior_Int.py`/`Behavior.py`（3 二段）+ `StateMachine.py`（2 状态机）+ `constant/__init__.py`（Panel）+ `Instruct.py`（3 指令）+ `constant_promise.py`（7 前提：SELF_BIRTH_TYPE_EGG/T_BIRTH_TYPE_EGG/HAVE_UNIDENTIFIED_EGGS/HAVE_HATCHING_EGGS/ENTERTAINMENT_IS_TEND_EGGS/T_HAVE_TAKEABLE_EGGS/PLAYER_HELD_EGGS_NOT_EMPTY）。
- `egg_handle.py` 全量实现：`get_birth_type`/`add_egg`/`get_unidentified_eggs`/`get_identifiable_eggs`/`get_hatching_eggs`/`get_hatch_day`/`have_need_tend_eggs`/`check_ovulation`/`npc_identify_eggs_settle`/`check_egg_born`/`take_eggs_from_chara`/`identify_held_eggs_settle`/`replace_entertainment_for_eggs`。要点：
  - 破壳基准取卵的 `lay_time`（受精卵的排出日=受精日，两者同日，见方案 §3.3/§3.6；比取 `pregnancy.fertilization_time` 更稳——后者会被后续新受精覆盖）。
  - `check_ovulation` 排出受精卵时同步清 talent20 与 talent35（无意识妊娠随卵流程走，防止与无受精状态矛盾）；talent21/22 在身者跳过（防 debug 改种族的中间态）。
  - `identify_held_eggs_settle` 逐索引消耗，查无角色/卵时静默清索引；同一角色多枚受精卵合并为一次通知。
- `pregnancy_handle.check_all_pregnancy` 分流：birth_type==11 → `check_ovulation`+`check_egg_born`，跳过 `check_pregnancy/check_near_born/check_born/check_rearing`；`check_rearing_complete` 起共用。
- `born_event_panel.Born_Panel` 增加 `egg_mode`/`egg_id` 参数：卵生分支为破壳文案、二段 `egg_born`、结算=删卵+talent24/27=1+按罩杯 milk_max+经验86+1+unnormal_flag(2)，不触碰 21/22/23/26 与 V/W 扩张；同时修复 :124 现存 BUG（`character_id`→`self.mother_character_id`，胎生路径受益）。
- 状态机实现 ×2（`StateMachine/default.py`）：移动到育儿室（照黄澄澄游戏室先例）；照料卵分流（有可鉴定卵→鉴定行为并当场调 `npc_identify_eggs_settle`，否则→孵化行为）。
- `handle_npc_ai.get_chara_entertainment`：随机池构建处显式剔除娱乐 id 175。
- `past_day_settle.py`：娱乐刷新后调 `egg_handle.replace_entertainment_for_eggs`（监禁/派对日/幼女跳过）。
- `handle_instruct.py`：三个指令处理函数（开面板 / 拿卵+口上行为 / 鉴定持有卵+口上行为，数据结算在处理函数内完成）。
- 前提函数 7 个落位 `handle_premise_other.py`（生育前提区段，函数内 lazy import egg_handle 规避 handle_premise↔egg_handle 循环导入）。
- CSV：`Behavior_Data.csv`（4 行为+3 二段）、`Behavior_Effect.csv`（4×9999、3×998）、`Behavior_Introduce.csv`（4 行）、`Entertainment.csv`（175 照料卵，auto_ai_move=564，auto_ai_entertainment=427）、`InstructConfig.csv`（1036~1038 三行）。
- 口上：`second_pregnancy.csv` 追加 lay_egg/egg_fertilized/egg_born 各 5 条+3 条地文占位；新建 `talk/play/identify_eggs.csv`、`talk/play/hatch_eggs.csv`（sys_1）、`talk/daily/take_chara_eggs.csv`、`talk/daily/identify_held_eggs.csv`（sys_0）各 5 条。
- 用字说明：实施中文件保存时"産"被规范化为"产"（IDE/钩子行为），已全线统一为"产"（指令名、口上、注释）。
- buildconfig 全量重建通过；运行时验证：行为 175~178、娱乐 175（564/427）、二段 1322~1324 均在生成物中，且三个二段行为进入 must_show 列表。

**第七步：怀孕总览面板与谱系图（§2.7）——已完成（2026-08-23）**

- `family_tree_draw.py`：`build_family_tree_lines(center_id, max_gen=2)`——长辈递归上溯（逐代全角空格缩进+◇，倒序使远代在上）、中心行•高亮、后代 tree 风格（`├─`/`└─`/`│　` 行前缀）下探；超限行尾 `…`；行内并列注明另一位家长；框线字符仅作行前缀不做跨行列对齐（规避 §2.12 陷阱）。
- `pregnancy_panel.py`：阶段枚举 1~7（受精<持卵待鉴定<妊娠<孵化中<临盆<产后<育儿，多态取时序最靠后者）；总览页排序（降/升序切换按钮）+筛选（全部+7 阶段按钮组，状态持久化 `Cache` 两字段）+每行姓名按钮（点击→以其为中心打开谱系图页）；谱系图页角色按钮点击换中心、`[重置回博士]`、中心角色被删除时兜底回玩家；只用抽象绘制类。
- 入口①：`normal_flow.py` 注册 `PREGNANCY_OVERVIEW`（函数内 import）；指令 1036（前提 `IN_NURSERY`，web_category 2 开面板）。
- 入口②：`manage_basement_panel.py` `department_son_panel_button_dict` 加 `教育区:[怀孕育儿系统]`（教育区原无子系统按钮，未触及每部门 2 按钮上限）+ `jump_to_son_panel` 分支（函数内 import 实例化）。
- ArkEditor 副本同步：`Premise.csv` 生育区段 +7 行、`Behavior_Data.csv` +4 行为 +3 二段（脚本化插入并断言锚点，去重校验）。

**第八步：文档（§2.8）——已完成（2026-08-23）**

- 新增 `Script/System/Pregnancy_System/怀孕系统设计文档.md`（目录构成/引用清单/生育方式/双链对照/卵数据结构/照料卵行为链/监禁卵指令/面板/编号一览/口上/维护注意事项）。
- 更新 `.github/prompts/数据处理工作流/妊娠系统.md`：概述后加架构更新导语（指向子系统目录与设计文档），两处旧路径（`Script/Design/pregnancy.py`、`sp_event_panel.py`）改标新路径，补怀孕总览面板条目。

**构建与本地化**

- `buildconfig.py` 全量重建 ×3 均通过（数据结构步、CSV 步、口上步各一次）。
- `buildpo.py` / `buildmo.py` **本机无法执行**（环境缺失，非本次改动引入）：buildpo 依赖的 `xgettext` 命令行工具未安装（`os.system` 静默失败导致 erArk.pot 未生成）、buildmo 依赖的 `polib` 包未装入 .conda 环境。中文为源语言不影响 zh_CN 运行；其他语言词条待环境补齐后由用户执行。
- 注意：buildpo 脚本会先删除 `data/po/zh_CN/LC_MESSAGES/erArk_py.po` 再重建，本次因 xgettext 缺失导致该文件被误删未重建，已用 `git checkout --` 恢复原文件。

### 6.2 实施前的假设复核

| 方案假设 | 复核结果 |
| --- | --- |
| §2.11 引用全量清单仅 4 处 | ✅ 全局 grep 证实（sleep_settle:12/88、past_day_settle:14/67、ejaculation_panel:436、pregnancy.py:19/258），迁移后归零 |
| §2.3 二段行为空闲号 1316、1322~1330 | ✅ 现场核对 Behavior_Data.csv 证实；取用 1322~1324 |
| 行为 cid 175~180 空闲 | ✅ 174 与 181 之间空置；常量四件套同段无占用 |
| 状态机 427（娱乐段）、564（教育区移动段）空闲 | ✅ 现场核对 StateMachine.py 证实 |
| Panel 常量顺延 67 空闲 | ✅ 66 MIXOLOGY 为当前最大 |
| 指令 cid 1036~1038 空闲 | ✅ DAILY 段现最大 1035 |
| §2.8 Race.csv birth_type 已提前完成 | ✅ 表头 4 行+45 数据行全有值；buildconfig 后 config_def.Race 出现 birth_type |
| §2.9 随机池特判先例（:817 品酒） | ✅ 位置无偏移，剔除逻辑落位其上方（remove(0) 之后） |
| §2.10 教育区无子系统按钮 | ✅ department_son_panel_button_dict 无教育区键，新增不触 2 按钮上限 |
| §2.5 sp_event_panel:124 现存 BUG（循环残留变量） | ✅ 属实，已随卵生模式扩展一并修复 |
| §2.4 两处结算钩子位置 | ✅ 无偏移；娱乐替换钩子插在 get_chara_entertainment 与 update_reproduction_period 之间 |
| 前提落点（handle_premise_other.py vs 新建） | 选择 handle_premise_other.py 生育前提区段（毗邻既有生育前提，免去 __init__ 注册）；因 egg_handle→second_behavior→handle_premise 的导入链，前提函数内对 egg_handle 用 lazy import |
| 方案 §3.6 破壳基准 fertilization_time | ✗ 微调：改取卵自身 lay_time（同日等价且不被下次受精覆盖），已回写方案 §3.6 实施口径修正 |
| 存档回填段 :259-274 | ✅ 实际为 `_normalize_loaded_save_paths` 内避孕套回填段，紧随其后追加 |

### 6.3 单元测试结果

无头测试环境（照 skill `headless-game-test`：完整初始化链+UI 屏蔽+WaitDraw 记录 stub+askfor stub+取名 stub），脚本位于会话 scratchpad `test_plan12_egg.py`。**59 断言全部通过（PASS 59 / FAIL 0）**：

- A 生育方式（4）：卵生 11 / 胎生 1 / 12 归一为 1 / 玩家 1（测试角色：九 race39 斐迪亚、阿米娅）
- B 排卵结算（6）：非排卵日不排；受精→受精卵+talent20/35 清零；再排→无精卵+编号自增；未初潮豁免
- C 鉴定（6）：当天卵不可鉴定；次日可鉴定；一次全部揭示（无精静默删、受精置 identified+通知）；纯无精卵时零绘制输出
- D 娱乐替换与随机池（5）：持卵者恰一个时段被替换；监禁跳过；胎生不替换；30 轮随机刷新中 175 永不出现
- E 监禁卵指令（11）：拿走后本人不可鉴定+索引正确+held 标记；三前提实测（t_have_takeable_eggs/player_held_eggs_not_empty/t_birth_type_egg）；失效索引静默清理；受精卵回写进入孵化+通知
- F/G 破壳（10）：未满 265 天不触发+hatch_stage 刷新；满期走真实 Born_Panel 卵生模式全流程——卵删除、talent24/27=1、不获得 21/22/23/26、新角色诞生且母女关系正确、milk_max 按罩杯、妊娠经验+1
- H 分流回归（4）：胎生受精 90 天→妊娠(21/26/27) 正常；卵生跳过妊娠链、非排卵日保留 talent20、排卵日消费为受精卵
- I 存档回填（4）：缺 eggs/next_egg_id/held_eggs/next_held_egg_id 的旧结构体经 `_normalize_loaded_save_paths` 回填为空值
- J 谱系树（5）：中心行、女儿入树、换中心含父母行、MAX_GEN=2 截断不含曾孙、超限行省略号
- K 阶段枚举（4）：育儿/妊娠/孵化阶段判定与妊娠时间文本

另有全链导入冒烟：三个指令与 Panel 67 均注册成功（constant.handle_instruct_data / panel_data 实测）。

测试环境适配备注（非生产代码问题）：无头环境需自建玩家结构体（id 0 由创建流程生成）、`get_system_setting_zero()`、`basement.get_base_zero()`；`egg_handle.replace_entertainment_for_eggs` 对 `party_day_of_week` 的读取顺手改为 `.get(week_day, 0)` 增强健壮性。

### 6.4 二期实施记录（2026-08-23，方案 v5：分类调整 + 保育员 + 鉴定流程改造）

**确认口径**（AskUserQuestion）：无在职保育员→自己鉴定兜底；任职资格=仅带壳卵生种族(11)（**后于 v11 取消**，见 §6.4 末尾 v11 段）；母亲保留每日孵化娱乐；作息冲突→**在场才等待**（在班保育员在场才等待，否则自己鉴定——规避"有工作的母亲娱乐仅晚间 19~22 而保育员 9~18 上班"导致的永久滞留死锁）。

**A. 分类调整**

- `InstructConfig.csv`（cid 不变，避免连锁风险）：1036 怀孕总览 DAILY→WORK；1037 拿走产下的卵 DAILY→OBSCENITY；1038 鉴定持有的卵 DAILY→WORK 且 web_minor `hand_scene`→`hand_work`。
- `Behavior_Data.csv` tag：175/176 娱乐→工作、177 日常→猥亵、178 日常→工作（设施损坏检测 1751 对 178 新生效，无害；177 进入猥亵判定链，监禁场景无实际影响）。
- `Behavior_Introduce.csv` 175/176 介绍改写（提及保育员）。
- 口上文件移动（未入库文件用 mv）：`play/identify_eggs.csv`、`play/hatch_eggs.csv`、`daily/identify_held_eggs.csv`→`data/talk/work/`；`daily/take_chara_eggs.csv`→`data/talk/obscenity/`（目录仅影响生成 cid 前缀，重跑 buildconfig 即可）。
- `Instruct.py` 三常量移至 #工作#/#猥亵# 分区；ArkEditor `Behavior_Data.csv` 副本 `type` 列同步 4 行。
- 说明：拿走产下的卵改猥亵类后**默认不显示**（猥亵分栏默认关闭、交互对象为临盆/产后/婴儿时强制关闭），需玩家开启猥亵分栏——属猥亵类既有惯例。

**B. 保育员工作**

- `WorkType.csv` 新行 **153**：`保育员,教育区,育儿室,Nursery,0,45,无,1,564,330|nursery_have_work_to_do`（auto_ai_move 复用一期的 MOVE_TO_NURSERY=564；带额外前提照坐诊医生先例）。
- 任职种族限制：`manage_basement_panel.py` `button_0` 过滤段硬编码（work_cid==153 且 `get_birth_type()!=11` → 不显示，照幼女只能当学生先例；`need` 列 token 体系不支持种族）。**（v11 已取消：该过滤段已删除，见 §6.4 末尾 v11 段）**
- 状态机 `WORK_NURSERY_CARE=330`（工作段 301~329 连续占满后顺延）：优先级1=为在场角色（含自己）鉴定卵（30min+当场结算，identifier 通知文案）；否则等权重池 random.choice——存在孵化中卵→孵化卵(60min)、场景有婴儿→随机复用既有照料婴儿行为 261~266（trigger=both、tag=工作、效果口上齐备、NPC 侧此前零引用，无需新建行为）；池空兜底 WAIT 1min。
- 新前提 ×3（constant_promise + `handle_premise_work.py` 照教师先例 + ArkEditor Premise.csv）：`WORK_IS_NURSERY_WORKER`/`TARGET_WORK_IS_NURSERY_WORKER`（work_type==153）、`NURSERY_HAVE_WORK_TO_DO`（场景有持可鉴定卵者 或 存在孵化中卵 或 场景有婴儿；不满足时保育员自然落入通用目标不空转）。
- `egg_handle.py` 新增：`NURSERY_WORKER_WORK_ID=153` 常量、`any_hatching_eggs_exist()`（遍历 npc_id_got）、`find_identifiable_egg_owner_in_scene()`（含自己，-1 为无）、`nursery_worker_on_duty_in_scene()`（要求该保育员 `work_time` 前提成立，排除下班滞留者防白等）；`npc_identify_eggs_settle` 加参 `identifier_id`——他人代鉴时通知文案"保育员X在育儿室为Y鉴定…"，二段 `egg_fertilized` 仍由卵主人触发。

**C. 母亲流程改造**

- `character_tend_eggs`(SM 427) 鉴定分支改三支：①自己是保育员→自己鉴定；②在班保育员在场→WAIT 10min+STATUS_WAIT（保育员工作状态机以最高优先级鉴定在场角色）；③否则自己鉴定（兜底）。孵化分支不变。收敛性：等待为有限时长且仅在娱乐时段内重评，WAIT 另有引擎级零时长豁免，无死循环路径。

**验证**

- buildconfig 全量重建通过；全链冒烟：WorkType 153 载入正确（564/330|nursery_have_work_to_do）、SM330 已注册、`instruct_type_data` 中 WORK 含两指令/OBSCENITY 含拿卵/DAILY 已移除三者且非空（规避 see_instruct_panel 的 KeyError 坑）、四行为 tag 实测 工作/工作/猥亵/工作。
- 无头单元测试 **76/76 通过**（一期 59 全量回归 + 二期 W 组 17）：W1/W2 在班保育员在场判定（含下班排除）；W3/W6d/W6e 前提三分支与全空=0；W4 保育员优先鉴定在场角色（行为/目标/卵结算/保育员文案四断言）；W5 无卵可鉴定→孵化；W6 仅婴儿→照料婴儿行为之一且目标为婴儿、SM 兜底 WAIT；W7 母亲三分支（在场→等待且卵未动、离场→自己鉴定兜底、自己是保育员→直接鉴定）。
- ArkEditor 副本（Behavior_Data type 列 4 行、Premise 3 行）已同步。

**三期：编号按类型段归位（2026-08-23，方案 v6）**

- 行为 Behavior_Data cid 迁移（行位同步移动）：鉴定卵 175→**267**、孵化卵 176→**268**、鉴定持有的卵 178→**269**（工作段，266 give_toy 之后，育儿室主题连续）；拿走产下的卵 177→**345**（猥亵段，344 release_from_bag 监禁块之后）。`Behavior_Effect.csv`/`Behavior_Introduce.csv` 同步迁移（Introduce 编号跟随整数空间，见下）。
- 指令 InstructConfig cid 迁移（行位同步移动）：怀孕总览 1036→**2052**、鉴定持有的卵 1038→**2053**（2051 manage_basement 之后）；拿走产下的卵 1037→**5105**（5104 ask_copy_key 之后）。指令 cid 仅用于面板排序（`instruct_id_to_cid`），处理函数按 instruct_id 字符串注册，无连锁。
- **关键发现（修正了本次计划的一个假设）**：`Behavior_Int`/`CharacterStatus` 的整数常量空间与 Behavior_Data cid 是**两套独立编号**（早段恰好对齐属巧合；如 steal_scene_all_socks Data=338/整数=345、hold_child Data=261/整数=801）。345 在整数空间已被占用，故 `TAKE_CHARA_EGGS`/`STATUS_TAKE_CHARA_EGGS` 整数取监禁段（351~353）后的 **354**；其余三者整数空间 262~269 空闲，与 cid 对齐取 267/268/269。`Behavior_Introduce.csv` 编号跟随整数空间（先例：give_toy 介绍行 cid=806），四行落位 267/268/269/354。
- `Entertainment.csv` 175 照料卵的 behavior_id 列 176→268。`Behavior.py`/`BehaviorStr.py` 字符串常量（值不变）移至 GIVE_TOY 之后与 SET_FREE 之后的对应分区。ArkEditor Behavior_Data 副本同步迁移。
- 代码零改动（所有引用均经 en_name 字符串与符号常量；`handle_npc_ai`/`egg_handle` 中的 175 为娱乐 cid，不涉及）。
- 验证：buildconfig 重建通过；冒烟实测 behavior cid=267/268/269/345、instruct cid=2052/2053/5105、Entertainment behavior_id=268、整数常量=267/268/269/354；全量回归 **76/76 通过**；grep 复核 CSV/代码无旧编号残留。

**四期：修复排卵日事件被"玩家不睡觉"错过丢失的 BUG（2026-08-23，方案 v7）**

- **成因**：受精判定与排卵结算均以"当前周期==5"为瞬时触发门且只挂在玩家睡觉结算链（sleep_settle→check_all_pregnancy）；而周期在每日 0 点由 `update_reproduction_period` 无条件推进（0 点结算按日期变化触发、不依赖睡觉——已核实 character_behavior.py 的 update_new_day 调用）。玩家在角色排卵日当天不睡 → 次日 0 点周期推进过 5 → 胎生当日体内射精的受精判定、卵生该周期的排卵结算被永久跳过。
- **修复**（用户确认胎生受精一并处理）：
  - `PREGNANCY.ovulation_flag: bool` 新字段（save_handle 回填 False）；
  - `update_reproduction_period` 推进到排卵日时逐角色置位（不限种族）；
  - `check_fertilization` 触发门改 flag；过门后非卵生立即消费标记（后续任何 return 路径不残留），卵生留给排卵结算；
  - `check_ovulation` 触发门改 flag；加非卵生守卫（0 点兜底对全角色调用）；豁免分支与正常路径均消费标记；
  - `past_day_settle` 在周期推进前对标记仍在者兜底补跑 `get_fertilization_rate`+`check_fertilization`+`check_ovulation`（体内残留精液仍参与判定；补排卵 lay_time 为次日 0 点，可鉴定时点晚一天，已接受）。
- 附带行为变化（记录）：同一排卵日玩家睡多次时，受精判定由"每次各判一次"变为"每周期仅判一次"（标记一次性消费的自然结果）。
- 测试：B 组改 flag 语义（周期推进置位/无标记不排/消费与豁免消费）、C/E/H 组准备步骤改置标记、I 组加回填断言、新增 M 组 9 断言（胎生兜底补判受精/rate=0 消费/无标记不判、卵生补排无精卵与受精卵/不双排、胎生守卫）——**89/89 通过**。测试环境适配：桩玩家补 talent 默认值。

**五期：谱系图改传统家谱式五代分层（2026-08-23，方案 v8）**

- 确认口径（AskUserQuestion）：居中分层**不画跨行连线**（遵守 §2.12 框线字符跨行列对齐硬约束；近似居中不需要列级精度）；中心行**显示兄弟姐妹**；用户特别要求保障"玩家为父、多位母亲、每母若干后代"的极端场景正确显示。
- `family_tree_draw.py` 数据层重写（旧 `build_family_tree_lines`/缩进树函数删除）：`build_family_tree_generations(center_id)` 输出祖辈/父母/中心/子女/孙辈五个代际行（空代际跳过）——祖辈=父方/母方双亲夫妇单元（有更深先代者名后标"…"）、父母=父═母、中心=•中心═配偶链+〔同辈〕兄弟姐妹、子女按另一位家长分组〔母:某某〕、孙辈按〔子女═其配偶〕分组（有更深后代者名后标"…"）；`layout_units_to_lines(units, max_width, max_lines=4)` 纯函数按 `text_handle.get_text_index` 宽度贪心装填多条物理行（不可拆分块边界换行、组标签与首成员同块不悬挂），超行数上限折叠并返回隐藏人数。
- `pregnancy_panel.draw_family_tree_page` 重绘：代际标签仅首行、整行近似居中（前导半角空格）、人物为按钮（return_text 带实例序号防重复）、中心高亮非按钮、行尾 `…(+N人)` gold 显示、代际间空行；顶部说明更新。
- 语义发现（记入设计文档）：新生儿父亲恒为玩家 → 孙辈同时是玩家子女，同一人依不同亲缘路径可合法出现在多个代际行（测试中原"曾孙不显示"断言因此改为用"纯第四代"角色验证截断）。
- 测试：J 组重写 15 断言（五代结构/配偶链/兄弟姐妹/换中心父母成对/孙辈与更深标记/纯四代截断/一父多母 3 母×2 子分组数与成员/装填三态：宽裕零隐藏、窄宽换行不丢人、行数上限折叠计数准确/组标签不悬挂/面板冒烟）——**100/100 通过**。

**六期：谱系图改带完整连线的传统家谱图（2026-08-24，方案 v9）**

- 确认口径（AskUserQuestion+计划补充）：四代分配=**上 1 代+中心+下 2 代**（空代际跳过）；超宽处理=**以家族为单位自动分页**（一页至少一个家族、家族永不拆散，`[上一页]/[下一页]`+`第X/Y页` 标识；用户以"5 个家族、第一页只装得下前 3 个+第 4 个的一半→前 3 个一页、第 4/5 个下一页"为例指定）。用户明确要求完整连线，**§2.12 跨行列对齐约束在谱系图范围内放开**（对齐依赖等距更纱黑体 SC 度量，已记入方案与设计文档的风险/维护条目）。五期的代内换行续排机制随连线布局废弃（连线下同代必须单行）。
- `family_tree_draw.py` 布局引擎重写（五期 `build_family_tree_generations`/`layout_units_to_lines` 删除）：
  - `build_family_tree_chart(center_id, max_width, page_index)`：名字行/排版行交替输出（`rows` 内 cell 携带列位），列位以 `text_handle.get_text_index`（wcwidth）为单位制自底向上测宽、自顶向下放置（夫妇文本与子块跨度互相近似居中）；排版行字形由(上接/下接/向左/向右)真值表映射 `┌┬┐┴┼│─└┘├┤`，下坠点=夫妇文本中点、上接点=子辈名字中点，连续字符合并为单 cell。
  - **玩家名按父本位置重复**：每个夫妇框独立写左右两人名（父本恒为玩家的游戏设定下即玩家名逐位置重复），不画长线连回单一节点；**NPC 唯一**由归属规则保证——孩子的另一位家长是更深的血缘节点时该组挂到对方节点下（乱伦女儿只出现一次、其孩子从她的位置下坠），`placed_set` 先到先得兜底。
  - 同辈口径微调（连线语义所需）：父母夫妇框下仅显示**同父同母**（或同单亲）的兄弟姐妹，异母半同辈不再入图（可点玩家名换中心查看）。
  - `paginate_family_blocks` 家族分页（左→右贪心装填）；单家族独占一页仍超宽时 `_fit_family_block` 从右侧逐叶折叠（每框至少保留 1 个孩子），隐藏人数按"折叠前后 id 集合差"精确计数、以 gold `…(+N人)` 标注在最深名字行末。
- `pregnancy_panel.py`：`draw_family_tree_page` 改统一前导缩进+逐 cell 补空格渲染（全部行同一缩进保证列对齐，取消五期的每行代际标签与逐行独立居中）；新增 `tree_page` 状态与 `change_tree_page(±1)`（下限钳位，上限由 chart 按总页数钳位回写），换中心/跳转/重置时页码归零；多页时绘制分页控制行。
- 测试：J 组重写 23 断言（行序名/线交替、玩家名重复 5 次均高亮、NPC 母亲唯一、女儿唯一且与重复玩家名╤相连、孙辈"…"、四代截断、**连线列位数学校验**（下接字形列=子辈名字中点列集、上接字形列=夫妇连接符╤所在列集、上接点数=有子夫妇框数）、NPC 中心四代齐全（父母/中心+同辈/子女/孙辈）、家族分页（4 顶层块、窄宽多页、各页宽度合规、并集无遗漏、家族不拆散、页码越界钳位、宽裕单页）、单家族兜底折叠计数、面板冒烟+分页按钮+翻页/换中心页码重置）——**108/108 通过**。另以可视化脚本目检：三家族连线图、窄宽两页分页、NPC 中心含父母行/同辈/孙辈图形均正确。

**六期修正 v10：夫妇连接符与连线起点（2026-08-25）**

- 按用户追加调整：夫妇连接符 `═` 改为 **`╤`**（自带向下接头）；排版行连线**起点**从夫妇文本中点改为 `╤` 所在列（`_place_box` 中 `drop_col = couple_col + 左侧人物宽`；无配偶/不在册时无连接符，起点退回人名中点列），**终点**保持子辈名字中点不变。面板说明文字同步。
- 测试：J4b 连接符断言改 `╤`；J6c 由"上接列落在夫妇文本范围内"强化为"上接字形列集==╤所在列集"；J7 增加"第二排版行上接列==子女夫妇 ╤ 列"——**108/108 通过**。可视化目检：`╤` 正下方为 `┴`/`│`，单子偏移时正确出 `┌┘` 折线。

**二期修正 v11：取消保育员种族限制（2026-08-25）**

- 用户决定删除"保育员必须是带壳卵生种族"的需求：代码侧由用户自行删除 `manage_basement_panel.button_0` 中对 153 的 `get_birth_type()!=11` 过滤段（复核：该文件已无 153/birth_type 引用），WorkType 153 行职业要求列为"无"。任何干员均可任命为保育员；鉴定/孵化/照料婴儿与"在场才等待"流程不变。
- 测试：W 组无任职资格断言，无需改动（其选用卵生干员当保育员仅为构造方便，仍有效）；方案 §3.11、设计文档 §5、工作流文档已同步。

**v12：监禁卵指令结算归位与 lay_egg 结算等级（2026-08-25）**

- 按用户追加调整：①`take_eggs_from_chara`/`identify_held_eggs_settle` 从指令处理函数内"行为前直调"改为**正式注册的专用结算**——`constant_effect.BehaviorEffect.TAKE_CHARA_EGGS_SETTLE=546`、`IDENTIFY_HELD_EGGS_SETTLE=547`（专用指令结算段 500~599 顺延，现场核对 545 后空闲），实现于 `Script/Settle/default.py` 末尾（`@settle_behavior.add_settle_behavior_effect` 注册；照 ASK_COPY_KEY 先例 `add_time=0` 守卫；拿走卵取 `target_character_id`、无有效目标不结算；鉴定仅 `character_id==0` 生效），`Behavior_Effect.csv` 中 345/269 由 9999 改挂 546/547，`handle_instruct.py` 两处理函数仅保留 `chara_handle_instruct_common_settle`；`tools/ArkEditor/csv/Effect.csv` 同步两行。行为语义变化：数据结算由下指令瞬间改为行为结算阶段（`handle_instruct_data` 先口上后效果，两指令的前提/口上判定在结算前仍成立）。②`lay_egg` 由 998 改 **997**（`SecondEffect.Must_Settle`：`game_config` 载入时进入 `config_behavior_must_settle_cid_list`，触发时进 `must_settle_second_behavior_id_list`，由 `second_behavior.must_settle_check` 在下一结算阶段静默结算，不再强制弹出口上；`egg_fertilized`/`egg_born` 仍 998）。③谱系图中心前缀由用户手改为 `•`（原 ◆），源码文档字符串/测试/文档同步。
- 构建：`buildconfig.py` 全量重建（effect 挂接与 must_settle 列表生效）。
- 测试：E 组改用注册结算调用（`constant.settle_behavior_effect_data[546/547]`），新增 E0a（结算已注册且行为已挂接）、E0b（lay_egg=997 且在必须计算列表、不在必须显示列表）、E0c（add_time=0 守卫不生效）——**111/111 通过**。

**v13：生育/破壳事件中玩家与母亲移动到医疗部住院区（2026-08-25）**

- 用户要求核查两条链的位置处理。核实结果：`Born_Panel`（胎生/卵生共用）**不做任何位置移动**，迁移前的旧 `pregnancy.py` 亦然——胎生母亲只靠 `handle_npc_ai` 的临盆/产后守卫（`talent[22]/[23]`，随机 `constant.place_data["Inpatient_Department"]`）在她自己的 AI 轮次被传送，事件本身不保证；玩家始终留在床上；卵生母亲无临盆状态，破壳时两人都不动。与"你第一时间赶到住院区"文本不符。
- 修正（`born_event_panel.py`）：新增模块级 `move_to_inpatient_department_for_born(mother_id) -> 目标路径`——母亲已在住院区则以其病房为目标（玩家会合），否则随机选一间住院区场景并 `map_handle.character_move_scene` 移入母亲；玩家不在该病房时同样瞬移；幂等。在 `_draw_born_event_content` 开头（选医生前）调用，两种模式共用；胎生场景下兼作 AI 尚未传送时的兜底。**不用** `character_move.own_charcter_move`（寻路+流程推进，不能在睡眠结算内调用）。确认口径：事件结束后两人留在住院区，不做回传（入睡前房门锁因离场解锁属正常）。
- 测试：G 组破壳前把母亲/玩家放到宿舍/育儿室，新增 G9~G11（母亲到住院区、玩家同病房且登记场景角色表、两人从旧场景移除）；新增 N 组（胎生生产：临盆+受精 266 天→`check_born` 必触发真实 `Born_Panel`）N1~N3（同上位置断言+临盆→产后+新角色）、N4（母亲已在住院区则玩家会合到同一病房不换房）、N5（母亲不在则两人同去同一间）——**119/119 通过**。

**v14：子系统设计文档改为纯索引（2026-08-25）**

- 按用户要求：`Script/System/Pregnancy_System/怀孕系统设计文档.md` 只保留索引表（指向方案、实施文档、工作流文档 `妊娠系统.md`），不承载实际内容。原设计文档 §1~§10（目录构成与外部调用点、生育方式、胎生/卵生链对照、卵数据结构、照料卵与保育员、监禁卵指令、面板与谱系图、编号一览、口上文件、维护注意）整体并入 `.github/prompts/数据处理工作流/妊娠系统.md` 并保持同号章节（历史记录中的"设计文档 §N"引用仍可按号对应）；工作流文档原有的胎生链通用说明重编为 §11~§14，顺手修正"受精判定仅在排卵日"（改为 `ovulation_flag` 驱动+0 点兜底）、`handle_premise.py`（已为包）、谱系图"纵向缩进树"等陈旧表述；工作流文档头部改为指向计划文档而非设计文档。
- 代码无改动；测试不变（119/119）。

### 6.5 尚未覆盖的验证（留给用户的游戏内清单）

一期重点：

- [ ] 完整卵生链实机体验：内射→排卵日排卵→次日 NPC 自行去育儿室鉴定（无精卵无声消失、受精卵通知）→每日照料卵时段→破壳事件（医生+取名）→泌乳+育儿→幼女成长（单元测试已逐环节直调验证，实机主要看 AI 行为循环中"照料卵"状态机的移动/执行衔接与口上显示）
- [ ] 胎生干员全链无回归（临盆住院、照顾婴儿指令）
- [ ] 监禁卵生干员流程：关押区"拿走产下的卵"→育儿室"鉴定持有的卵"→孵化破壳
- [ ] 面板两个入口、排序/筛选、谱系图行宽在窗口内不折行错位
- [ ] Tk 与 Web 双绘制模式（面板+破壳事件）
- [ ] 旧存档载入
- [ ] buildpo/buildmo：本机缺 xgettext 与 polib，需环境补齐后执行（见 §6.1 构建与本地化）

即 §4.2 全部条目，另加二期项：

- [ ] 管理罗德岛→干员工作安排：保育员(153)对全部干员可见可任命（v11 已取消种族限制）；任命后工作时间自动前往育儿室
- [ ] 保育员实机流转：优先鉴定在场干员的卵（含保育员文案通知）→无卵可鉴定时孵化/照料婴儿；持卵母亲在保育员在场时等待、不在场时自己鉴定
- [ ] 指令分栏：怀孕总览/鉴定持有的卵出现在工作分栏；拿走产下的卵需开启猥亵分栏后可见
- [ ] 四期：角色排卵日当天玩家整日不睡（跨过 0 点），次日检查该角色——卵生应已在 0 点补排一枚卵（面板可见）、胎生若当日曾内射应已完成受精判定
- [ ] 六期：谱系图连线家谱图显示（上1代+中心+下2代共4代、夫妇以╤相连且连线自╤列下坠到子女名字中点、玩家名按父本位置重复且各处高亮）；**在等距更纱黑体 SC 下目测连线与名字上下对齐无错位**；多位母亲时家族自动分页（[上一页]/[下一页]/页码、家族不拆散、换中心后回第1页）；单家族过宽时行尾"…(+N人)"；点击人名换中心、名后"…"提示图外还有父母/子女
- [ ] v12：关押区"拿走产下的卵"——行为结束后卵才被拿走（口上先于结算显示）；育儿室"鉴定持有的卵"——行为结束后出受精通知；排卵日 lay_egg 口上不再强制弹出但卵数据照常产生
- [ ] v13：胎生生产/卵生破壳当晚事件结束后，博士醒来时身处医疗部住院区且母亲在同一病房（胎生母亲随后按产后守卫留院、卵生母亲次日自行离开）
