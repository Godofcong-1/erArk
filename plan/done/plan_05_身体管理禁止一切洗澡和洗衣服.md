# Plan 05：身体管理新增“禁止一切洗澡”和“禁止洗衣服”

- 状态：已实施（代码已完成并通过构建与基础验证）
- 来源：`todo list.txt` → `# 待处理的小问题` → “身体管理加上禁止一切洗澡和洗衣服”
- 预计改动量：约 11 个文件（4 个 CSV 配置 + 4 个常量文件 + 3 个逻辑文件）
- 风险等级：中低（涉及数据构建与 NPC AI 行为条件）
- 适用代码快照：`master @ b17d1b1ba`（v0.66）

---

## 1. 目标

在现有“身体管理”系统中新增两项可由博士指定的长期管理：

1. **禁止一切洗澡**
   - 被管理的干员不再主动淋浴、简易洗澡、泡温泉或进入大浴场洗浴类娱乐。
   - 不限制博士主动邀请该干员“一起洗澡”。

2. **禁止洗衣服**
   - 被管理的干员洗澡时仍会清洗身体污浊，但不会清洗衣物上的污浊（`cloth_semen` 保持原样）。
   - 为未来独立的洗衣/更衣系统预留前提条件。

两项管理都应出现在体检科“身体管理”面板中，支持开启与取消，并沿用现有“明天睡醒后生效”的提示语义。

## 2. 现状调查

### 2.1 身体管理数据流

- 配置表：`data/csv/Body_Manage_Requirement.csv`
  - 字段：`cid, second_behavior_id, need_examine_id, behavior_id, need_value_1, need_value_2, need_value_3, todo`
  - 现有 cid：1~5、11~18、21~25、31~39
  - **可用空号：26、27**（本次使用）
- 运行时加载：`Script/Config/game_config.py::load_body_manage_requirement()`
- 角色数据：`game_type.Character.body_manage: Dict[int, int]`，初始化/重置见 `attr_calculation.get_body_manage_zero()`
- 面板：`Script/UI/Panel/physical_check_and_manage.py`
  - `manage_target_physical()` 列出全部管理项
  - `judge_manage_requirement()` 按 `second_behavior_id` 逐项判断开启条件
  - `settle_target_physical_manage()` 切换开启/取消

### 2.2 现有管理项是怎么工作的

以“禁止自慰”为例：

- `Body_Manage_Requirement.csv` cid 23：`23,ask_not_masturbation,0,0,50,2,100,0`
- `Behavior_Data.csv` 定义显示名：
  `1473,ask_not_masturbation,被要求禁止自慰,0,npc,二段结算|管理`
- `Behavior_Effect.csv` 给一个无实际数值效果的 `998` 结算器：
  `1473,ask_not_masturbation,998`
- `constant_promise.Premise` 定义：
  - `ASK_NOT_MASTURBATION = "ask_not_masturbation"`
  - `NOT_ASK_NOT_MASTURBATION = "not_ask_not_masturbation"`
- `handle_premise_body_manage.py` 注册 handler，直接读取 `body_manage[23]`
- NPC AI 目标表 `data/target/default/target.csv` 在自慰目标前提中追加 `not_ask_not_masturbation`，从源头阻止 NPC 执行

本次完全复用该模式。

### 2.3 当前洗澡相关行为与入口

洗澡相关行为（`Behavior_Data.csv`）：

| cid | en_name | 显示名 | 备注 |
| ---: | --- | --- | --- |
| 112 | take_shower | 淋浴 | 玩家/日常 |
| 114 | simple_shower | 简易洗澡 | NPC 快速清洁 |
| 184 | onsen_bath | 泡温泉 | 娱乐 |
| 324 | invite_to_bath | 一起洗澡 | 博士邀请目标 NPC |
| 802/808 | put_shower_cloth / wear_to_locker... | 换浴衣等 | 洗浴流程链 |

NPC 洗澡 AI 入口集中在 `data/target/default/target.csv`：

| target cid | 条件 | 动作 |
| ---: | --- | --- |
| 51 | `normal_1267\|shower_time\|shower_flag_0` | 进入要脱衣服（洗澡）状态 |
| 58 | `normal_1267\|sleep_h_awake_1\|shower_flag_0` | 睡奸醒来后进入洗澡流程 |
| 76 | `unnormal_2\|shower_time\|shower_flag_0` | 异常状态下简易洗澡 |
| 471 | `normal_all\|all_entertainment_time\|entertainment_is_bathhouse_type\|...` | 进入大浴场洗浴类娱乐 |

### 2.4 当前“洗衣服”的实现位置

当前没有独立的“洗衣服”指令/状态机。衣物清洁是淋浴结算的副作用：

- `Script/Settle/default.py::handle_dirty_reset_in_shower()`（约第 6692 行）
- 内部调用 `attr_calculation.get_dirty_reset()`：
  - 清零 `dirty.body_semen`（身体污浊）
  - 清零 `dirty.cloth_semen`（衣物污浊）
  - 清理灌肠等状态
- 因此要实现“允许洗澡但禁止洗衣服”，只需在 `handle_dirty_reset_in_shower()` 中，对该角色启用“禁止洗衣服”时保留 `cloth_semen`。

### 2.5 涉及前提系统的位置

- 前提 ID 定义：`Script/Core/constant_promise.py` 的 `Premise` 类
- 身体管理前提实现：`Script/Design/handle_premise/handle_premise_body_manage.py`
- 指令前提解析：`Script/System/Instruct_System/handle_instruct.py::add_instruct()`，从 `InstructConfig.csv` 的 `premise_set` 读取 `|` 分隔前提名，并映射到 `constant_promise.Premise`
- NPC AI 目标前提：`data/target/default/target.csv` 的 `premise_id` 列

---

## 3. 设计决策

### 3.1 使用两条独立管理项

| cid | second_behavior_id | 显示名 | 用途 |
| ---: | --- | --- | --- |
| 26 | ask_not_take_bath | 被要求禁止一切洗澡 | 阻止一切洗澡/洗浴类行为 |
| 27 | ask_not_wash_cloth | 被要求禁止洗衣服 | 洗澡时不清洗衣物污浊，并为未来洗衣系统预留前提 |

分开管理的理由：

- 两个禁令的生效点不同（一个在行为入口，一个在洗澡结算内部）。
- 与现有“禁止自慰”“禁止逆推”等单项粒度保持一致。
- 未来实装独立洗衣系统时，`ask_not_wash_cloth` 可直接复用。

### 3.2 开启条件

沿用现有身体管理通用条件结构：第一条件 + 攻略进度 + 催眠程度。

建议使用“精液经验”（`Experience.csv` 中 cid 24，运行时读取 `target_character_data.experience[24]`）作为第一条件：

| 管理项 | need_value_1 | need_value_2 | need_value_3 |
| --- | ---: | ---: | ---: |
| 禁止一切洗澡 | 200（精液经验） | 3（攻略进度） | 150（催眠程度%） |
| 禁止洗衣服 | 200（精液经验） | 3（攻略进度） | 150（催眠程度%） |

即：`精液经验大于等于 200`，或 `攻略进度达到 3`，或 `催眠程度达到 150%`，满足其一即可开启。

### 3.3 “禁止一切洗澡”的生效范围

1. **NPC 自主行为**：在 `target.csv` 的洗浴入口行（51、58、76、471）追加 `not_ask_not_take_bath`。
2. **博士邀请**：不做限制。`invite_to_bath` 不追加任何新前提，即使目标干员已开启“禁止一切洗澡”，博士仍可主动邀请其一起洗澡。
3. **玩家自己淋浴**：不受影响（身体管理只针对被管理的干员）。
4. **已在洗浴流程中开启管理**：与现有“明天睡醒后生效”一致，不强制打断当前已开始的行为链；次日 AI 将不再进入洗浴入口。

### 3.4 “禁止洗衣服”的生效范围

- 在 `handle_dirty_reset_in_shower()` 中，若角色 `body_manage[27]` 为 1：
  1. 结算前快照 `dirty.cloth_semen`（每个 value 是 list，需要复制）。
  2. 正常执行 `get_dirty_reset()`。
  3. 结算后用快照覆盖回 `dirty.cloth_semen`。
- 效果：身体洗干净了，但衣服上的精液/污浊保留。
- 不影响身体污浊、灌肠、阴茎污浊等其他清洁逻辑。
- 当前无独立洗衣入口，因此暂不改 `target.csv`；未来新增洗衣指令时，把 `not_ask_not_wash_cloth` 加入其前提即可。

---

## 4. 详细改动步骤

### 4.1 `data/csv/Body_Manage_Requirement.csv`

在 cid 25 和 cid 31 之间插入：

```csv
26,ask_not_take_bath,0,0,200,3,150,0
27,ask_not_wash_cloth,0,0,200,3,150,0
```

说明：`todo=0` 表示实装并显示。

### 4.2 `data/csv/Behavior_Data.csv`

当前最大普通管理行为 cid 为 1489，本次使用 1490、1491：

```csv
1490,ask_not_take_bath,被要求禁止一切洗澡,0,npc,二段结算|管理
1491,ask_not_wash_cloth,被要求禁止洗衣服,0,npc,二段结算|管理
```

### 4.3 `data/csv/Behavior_Effect.csv`

```csv
1490,ask_not_take_bath,998
1491,ask_not_wash_cloth,998
```

`998` 与现有“禁止自慰/禁止逆推”相同，是无数值效果的管理类占位结算器。

### 4.4 行为常量

`Script/Core/constant/Behavior.py` 在 `ASK_NOT_ACTIVE_H_FOR_PLAYER` 附近新增：

```python
ASK_NOT_TAKE_BATH = "ask_not_take_bath"
""" 被要求禁止一切洗澡 """
ASK_NOT_WASH_CLOTH = "ask_not_wash_cloth"
""" 被要求禁止洗衣服 """
```

`Script/Core/constant/SecondBehavior.py` 在身体管理二段行为常量区新增相同两个字符串常量，保持现有 `ask_*` 常量完整性。

`Script/Core/constant/SecondBehavior_Int.py` 新增：

```python
ASK_NOT_TAKE_BATH = 1490
""" 被要求禁止一切洗澡 """
ASK_NOT_WASH_CLOTH = 1491
""" 被要求禁止洗衣服 """
```

### 4.5 前提常量

`Script/Core/constant_promise.py` 的 `Premise` 类，在现有身体管理前提附近新增：

```python
ASK_NOT_TAKE_BATH = "ask_not_take_bath"
""" 属性_身体管理 自己被要求禁止一切洗澡 """
NOT_ASK_NOT_TAKE_BATH = "not_ask_not_take_bath"
""" 属性_身体管理 自己没有被要求禁止一切洗澡 """
ASK_NOT_WASH_CLOTH = "ask_not_wash_cloth"
""" 属性_身体管理 自己被要求禁止洗衣服 """
NOT_ASK_NOT_WASH_CLOTH = "not_ask_not_wash_cloth"
""" 属性_身体管理 自己没有被要求禁止洗衣服 """
```

### 4.6 前提实现

`Script/Design/handle_premise/handle_premise_body_manage.py` 新增 4 个 handler：

```python
@add_premise(constant_promise.Premise.ASK_NOT_TAKE_BATH)
def handle_ask_not_take_bath(character_id: int) -> int:
    """自己被要求禁止一切洗澡"""
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.body_manage[26]


@add_premise(constant_promise.Premise.NOT_ASK_NOT_TAKE_BATH)
def handle_not_ask_not_take_bath(character_id: int) -> int:
    """自己没有被要求禁止一切洗澡"""
    return not handle_ask_not_take_bath(character_id)


@add_premise(constant_promise.Premise.ASK_NOT_WASH_CLOTH)
def handle_ask_not_wash_cloth(character_id: int) -> int:
    """自己被要求禁止洗衣服"""
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.body_manage[27]


@add_premise(constant_promise.Premise.NOT_ASK_NOT_WASH_CLOTH)
def handle_not_ask_not_wash_cloth(character_id: int) -> int:
    """自己没有被要求禁止洗衣服"""
    return not handle_ask_not_wash_cloth(character_id)
```

### 4.7 身体管理面板

`Script/UI/Panel/physical_check_and_manage.py::judge_manage_requirement()` 新增条件分支：

```python
elif body_manage_second_behavior_id in ("ask_not_take_bath", "ask_not_wash_cloth"):
    # 精液经验
    now_value_1 = target_character_data.experience[24]
    require_value_1 = body_manage_data.need_value_1
    require_text += _("精液经验{0}/{1}").format(now_value_1, require_value_1)
    if now_value_1 >= require_value_1:
        judge_result = True
```

冲突检查区域新增：

```python
# 禁止洗澡与“洗澡时不洗精液”互斥
if manage_cid == 26 and handle_premise.handle_ask_not_wash_semen(target_character_id):
    require_text += _(" 需要未选择[洗澡时不再清洗阴道内的精液]")
    judge_result = False
if manage_cid == 21 and handle_premise.handle_ask_not_take_bath(target_character_id):
    require_text += _(" 需要未选择[禁止一切洗澡]")
    judge_result = False
```

说明：`body_manage[26]` / `body_manage[27]` 由 `manage_target_physical()` 的字典补全逻辑自动创建，不需要额外初始化代码。

### 4.8 禁止 NPC 自主洗澡

`data/target/default/target.csv` 修改以下行（在 `premise_id` 末尾追加 `|not_ask_not_take_bath`）：

| cid | 原前提 | 新前提 |
| ---: | --- | --- |
| 51 | `normal_1267\|shower_time\|shower_flag_0` | `normal_1267\|shower_time\|shower_flag_0\|not_ask_not_take_bath` |
| 58 | `normal_1267\|sleep_h_awake_1\|shower_flag_0` | `normal_1267\|sleep_h_awake_1\|shower_flag_0\|not_ask_not_take_bath` |
| 76 | `unnormal_2\|shower_time\|shower_flag_0` | `unnormal_2\|shower_time\|shower_flag_0\|not_ask_not_take_bath` |
| 471 | `normal_all\|all_entertainment_time\|entertainment_is_bathhouse_type\|bathhouse_entertainment_flag_0` | 末尾追加 `\|not_ask_not_take_bath` |

只拦截入口行。已进入洗浴流程的后续状态行（52~57、472~486 等）保持不动，避免管理开启时角色卡在中间状态。

### 4.9 不限制博士邀请“一起洗澡”

按需求，`data/csv/InstructConfig.csv` 中 `invite_to_bath`（当前 cid 5019）不做任何修改。

即使目标干员已开启“禁止一切洗澡”，博士仍可主动邀请其一起洗澡；该禁令只约束干员的自主洗浴行为。

### 4.10 禁止洗衣服的洗澡结算

`Script/Settle/default.py::handle_dirty_reset_in_shower()`：

在调用 `attr_calculation.get_dirty_reset()` 前保存衣物污浊，并在结算后恢复：

```python
# 被要求禁止洗衣服时，保留衣物污浊
keep_cloth_semen = {}
if handle_premise.handle_ask_not_wash_cloth(character_id):
    keep_cloth_semen = {
        clothing_type: semen_data.copy()
        for clothing_type, semen_data in character_data.dirty.cloth_semen.items()
    }

character_data.dirty = attr_calculation.get_dirty_reset(character_data.dirty)

# 恢复被禁止清洗的衣物污浊
for clothing_type, semen_data in keep_cloth_semen.items():
    character_data.dirty.cloth_semen[clothing_type] = semen_data
```

注意：

- 这里复制的是 list，不能用 `dict(character_data.dirty.cloth_semen)` 浅拷贝。
- `handle_target_dirty_reset_in_shower()` 内部调用同一函数，因此目标角色洗澡时同样生效，无需重复修改。
- 可选的体验增强：在保留衣物污浊时输出一行提示，如“因为被要求禁止洗衣服，{Name}没有清洗自己的衣服”。本 Plan 建议加上，但非必须。

---

## 5. 构建与缓存

```bash
# 1. 全量构建（本次改了 4 张 CSV，必须全量 buildconfig）
python buildconfig.py

# 2. 启动游戏自动增量构建也可以，但建议全量确保 config_def.py 更新
python game.py
```

修改 `target.csv` 后，`buildconfig.py` 会把新前提写入 `data/data.json`；运行游戏时 `auto_build_config` 也会重建 target 数据。

不需要删除地图缓存，本次不涉及地图。

---

## 6. 验证清单

### 6.1 数据构建

- [ ] `buildconfig.py` 执行成功。
- [ ] `data/data.json` 中 `Body_Manage_Requirement` 出现 cid 26、27。
- [ ] `Behavior_Data` 出现 1490、1491。
- [ ] `Behavior_Effect` 出现 1490/1491 且 effect_id 为 998。
- [ ] `data.json` 中 `Target` 表第 51/58/76/471 条前提包含 `not_ask_not_take_bath`。

### 6.2 面板验证

1. 体检科选择目标干员 → 身体管理。
2. 面板显示 `[26]：禁止一切洗澡` 与 `[27]：禁止洗衣服`。
3. 满足条件时可点击开启，再点一次可取消。
4. 开启后显示“(进行中)”。
5. 已选择“洗澡时不再清洗阴道内的精液”时，`禁止一切洗澡` 显示冲突原因且不可开启。
6. 已选择“禁止一切洗澡”时，`洗澡时不再清洗阴道内的精液` 同样冲突。

### 6.3 禁止洗澡验证

1. 给目标干员开启“禁止一切洗澡”。
2. 等到 `shower_time` 或使用 debug 面板推进时间，确认 NPC 不会进入“要脱衣服（洗澡）”状态。
3. 玩家主场景中，“一起洗澡”指令仍可正常选择与执行，不受目标干员已开启“禁止一切洗澡”的影响。
4. 目标干员不会进入大浴场洗浴类娱乐。
5. 取消管理后，目标干员恢复洗澡行为。

### 6.4 禁止洗衣服验证

1. 使目标干员衣物带有污浊（例如射在衣服上）。
2. 开启“禁止洗衣服”并让其淋浴。
3. 淋浴后检查身体污浊已清零，但 `dirty.cloth_semen` 中对应衣物污浊保持不变。
4. 取消“禁止洗衣服”后再次淋浴，衣物污浊被正常清零。

### 6.5 存档兼容

- [ ] 旧存档读取时 `body_manage` 字典自动补齐 26、27 两项（已有补全逻辑）。
- [ ] 开启新管理项后保存/读取存档，状态保持为 1。
- [ ] 关闭后保存/读取，状态为 0。

---

## 7. 风险与注意事项

1. **前提名必须完全一致**：`target.csv` 中写入的字符串必须与 `constant_promise.Premise` 中定义完全一致，否则运行时会打印“前提不存在”。
2. **只拦截 AI 入口行**：不要给洗浴流程中间状态行追加前提，否则目标角色可能卡在脱衣/围浴巾状态。
3. **衣物污浊必须深复制**：`cloth_semen` 的 value 是 list，浅拷贝会导致恢复失效。
4. **行为 cid 不要冲突**：新增行为使用 1490/1491，实施前需再次确认 `Behavior_Data.csv` 中这两个 cid 未被占用。
5. **当前没有独立洗衣行为**：“禁止洗衣服”当前只影响淋浴中的衣物清洁；未来若新增洗衣指令/状态机，需把 `not_ask_not_wash_cloth` 加入其入口前提。
6. **文本语义**：面板提示沿用“将在明天睡醒后生效”，但底层与其他管理项一样是即时写值；不做额外延迟机制。

## 8. 改动文件清单

| 文件 | 类型 | 改动 |
| --- | --- | --- |
| `data/csv/Body_Manage_Requirement.csv` | 修改 | 新增 cid 26、27 |
| `data/csv/Behavior_Data.csv` | 修改 | 新增 1490、1491 行为 |
| `data/csv/Behavior_Effect.csv` | 修改 | 新增 1490、1491 效果行 |
| `data/target/default/target.csv` | 修改 | 4 条洗浴入口追加 `not_ask_not_take_bath` |
| `Script/Core/constant/Behavior.py` | 修改 | 新增 2 个行为常量 |
| `Script/Core/constant/SecondBehavior.py` | 修改 | 新增 2 个二段行为字符串常量 |
| `Script/Core/constant/SecondBehavior_Int.py` | 修改 | 新增 2 个二段行为数字常量 |
| `Script/Core/constant_promise.py` | 修改 | 新增 4 个前提常量 |
| `Script/Design/handle_premise/handle_premise_body_manage.py` | 修改 | 新增 4 个前提 handler |
| `Script/UI/Panel/physical_check_and_manage.py` | 修改 | 新增条件判定与冲突检查 |
| `Script/Settle/default.py` | 修改 | 淋浴结算保留衣物污浊 |

## 9. 回滚

- 还原所有 CSV 与 `.py` 文件。
- 重新执行 `python buildconfig.py`。
- 旧存档中 `body_manage` 多出的 26/27 键可保留为 0，不影响游戏；如要彻底清除，可重新进行“取消全部身体管理”或读档兼容逻辑会保持为 0。

## 10. 不在本 Plan 范围

- 不新增独立“洗衣服”指令/状态机。
- 不处理“禁止洗澡”对当前已开始洗浴流程的即时打断。
- 不修改玩家自己淋浴/泡温泉的可用性。
- 不限制博士主动邀请干员“一起洗澡”。
- 不新增洗澡/洗衣相关的口上与事件；如后续需要，可在 `data/talk/system/second.csv` 按现有 `ask_not_*` 二段行为格式追加文本。
