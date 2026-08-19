# Plan 04：同房间内的其他睡眠中角色也进行被吵醒判定

- 状态：已实施，待游戏内验证（方案 v2，已按最新评审意见修订）
- 来源：`todo list.txt` → `# 待处理的小问题` → “同房间内的其他人也需要进行被吵醒的判定”
- 预计改动量：4 个文件，约 120~180 行
- 风险等级：中
- 适用代码快照：`master @ b17d1b1ba`（v0.66）

### 修订记录

| 版本 | 内容 |
| --- | --- |
| v1 | 初版：在 `character_behavior.py` 的 `time_judge` 位置新增场景睡眠者判定 |
| v2 | 按评审修改：结算位置回到 `settle_sleep_h()`；新增“地点_角色”前提；区分动作影响系数；非睡奸目标影响减半；仅睡眠等级 ≤1 才会吵醒 |
| v3 | 已按 v2 完成代码实施，并通过 py_compile 与核心逻辑单测 |

---

## 1. 问题描述

当前“被吵醒”只存在于玩家对无意识目标进行睡奸的结算中：

- `Script/Settle/realtime_settle.py::settle_sleep_h()`：玩家对睡奸目标动作时，按目标睡眠程度判断是否吵醒。
- `Script/Design/handle_npc_ai_in_h.py::judge_weak_up_in_sleep_h()`：睡奸中醒来结算。

但普通睡眠场景下，如果同房间内有其他角色在进行活动（例如有人进入房间、移动、工作、聊天、H 等），正在睡眠中的角色不会被吵醒。todo 要求：同房间内的其他正在睡眠中的人，也需要按睡眠深度进行被吵醒判定。

## 2. 现状调查

### 2.1 睡眠深度数据

`data/csv/Sleep_Level.csv`：

| 等级 | 名称 | sleep_point 阈值 |
| ---: | --- | ---: |
| 0 | 半梦半醒 | 30 |
| 1 | 浅睡 | 60 |
| 2 | 熟睡 | 80 |
| 3 | 完全深眠 | 100 |

取等级函数：`Script/Design/attr_calculation.py::get_sleep_level(value)`，返回 `(等级, 等级名)`。

### 2.2 现有 `settle_sleep_h()` 实现

文件：`Script/Settle/realtime_settle.py`，约第 519 行起。

当前逻辑：

```python
def settle_sleep_h(character_id: int, true_add_time: int) -> None:
    now_character_data = cache.character_data[character_id]
    target_data = cache.character_data[now_character_data.target_character_id]
    if target_data.behavior.behavior_id == constant.Behavior.SLEEP and target_data.sp_flag.unconscious_h == 1:
        # WAIT 或安眠药：sleep_level = 2 规避吵醒
        if now_character_data.behavior.behavior_id == constant.Behavior.WAIT or target_data.h_state.body_item[9][1] == 1:
            sleep_level = 2
        else:
            down_sleep = int(true_add_time * 3)
            target_data.sleep_point -= down_sleep
            sleep_level, tem = attr_calculation.get_sleep_level(target_data.sleep_point)
        if sleep_level <= 1:
            handle_npc_ai_in_h.judge_weak_up_in_sleep_h(character_id)
```

当前调用位置：`character_aotu_change_value()` 玩家分支内，约第 160 行：

```python
# 结算对无意识对象的结算
if target_data.sp_flag.unconscious_h:
    settle_sleep_h(character_id, true_add_time)
```

存在的问题：

1. 只处理“玩家当前交互对象”，不处理同房间其他睡眠 NPC。
2. 进入条件只看“交互对象是否在被睡奸”，而不是“地点是否有人睡觉”。
3. 影响量固定为 `true_add_time * 3`，没有按动作类型区分。
4. 等级 2（熟睡）也会减少睡眠程度，但不会醒；当前逻辑在等级 >1 时实际只是不调用醒来判定，符合预期，但需要在新方案中保留并明确。

### 2.3 现有睡奸吵醒逻辑

`Script/Design/handle_npc_ai_in_h.py::judge_weak_up_in_sleep_h()` 当前内部使用：

```python
target_data = cache.character_data[now_character_data.target_character_id]
```

并通过 `recover_from_unconscious_h(character_id, info_text)` 醒来。`recover_from_unconscious_h()` 开头有：

```python
if target_data.sp_flag.unconscious_h == 0:
    return
```

因此该函数只能处理“无意识 H / 睡奸”目标，普通睡眠角色需要单独的醒来结算分支。

### 2.4 前提注册现状

- 前提常量：`Script/Core/constant_promise.py` 的 `Premise` 类。
- 地点_角色类现有相关常量，约第 249~266 行：
  - `SCENE_SOMEONE_IS_H = "place_is_h"`
  - `SCENE_SOMEONE_UNCONSCIOUS = "place_someone_unconscious"`
  - `SCENE_ALL_UNCONSCIOUS_OR_SLEEP = "place_all_unconscious_or_sleep"`
- 地点前提实现：`Script/Design/handle_premise/handle_premise_place.py`。
  - 相似实现 `handle_scene_someone_unconscious()` 约第 407~429 行。
  - `handle_action_sleep()` 位于 `Script/Design/handle_premise/handle_premise_other.py` 约第 2682 行，可用于判断角色是否在睡眠行为中。

## 3. 实施方案

### 3.1 新增前提：该地点有人正在睡觉

#### 3.1.1 注册前提常量

文件：`Script/Core/constant_promise.py`

在 `SCENE_SOMEONE_UNCONSCIOUS` 附近新增：

```python
SCENE_SOMEONE_SLEEPING = "place_someone_sleeping"
""" 地点_角色 该地点有角色正在睡觉 """
```

命名沿用现有 `SCENE_SOMEONE_*` 系列，类型为“地点_角色”。

#### 3.1.2 实现前提函数

文件：`Script/Design/handle_premise/handle_premise_place.py`

在 `handle_scene_someone_unconscious()` 附近新增：

```python
@add_premise(constant_promise.Premise.SCENE_SOMEONE_SLEEPING)
def handle_scene_someone_sleeping(character_id: int) -> int:
    """
    校验角色所在地点是否有人正在睡觉
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    from Script.Design.handle_premise import handle_action_sleep
    character_list = map_handle.get_chara_now_scene_all_chara_id_list(character_id)
    if len(character_list) < 2:
        return 0
    for chara_id in character_list:
        # 跳过玩家，只判断NPC是否在睡觉
        if chara_id == 0:
            continue
        if handle_action_sleep(chara_id):
            return 1
    return 0
```

说明：

- `map_handle.get_chara_now_scene_all_chara_id_list(character_id)` 返回当前场景全部角色 id，包括玩家。
- `handle_action_sleep()` 判断角色当前行为是否为 `constant.Behavior.SLEEP`。
- 该前提只回答“当前地点是否有人睡觉”，不处理具体结算，保持前提函数轻量。

### 3.2 修改 `settle_sleep_h()` 进入条件

文件：`Script/Settle/realtime_settle.py`

将 `character_aotu_change_value()` 玩家分支中的：

```python
# 结算对无意识对象的结算
if target_data.sp_flag.unconscious_h:
    settle_sleep_h(character_id, true_add_time)
```

改为：

```python
# 当前地点有人睡觉时，结算玩家动作对所有睡眠NPC的影响
if handle_premise.handle_scene_someone_sleeping(character_id):
    settle_sleep_h(character_id, true_add_time)
```

不再要求“玩家交互对象正在被睡奸”；只要玩家当前场景存在任何正在睡觉的 NPC，就进入 `settle_sleep_h()`。

### 3.3 重写 `settle_sleep_h()`：遍历同场景所有睡眠 NPC

仍位于 `Script/Settle/realtime_settle.py`。

#### 3.3.1 函数流程

```python
def settle_sleep_h(character_id: int, true_add_time: int) -> None:
    """
    结算玩家当前场景内所有睡眠NPC的熟睡程度变化与被吵醒判定
    """
    now_character_data = cache.character_data[character_id]
    scene_path_str = map_handle.get_map_system_path_str_for_list(now_character_data.position)
    scene_data = cache.scene_data[scene_path_str]

    for sleeper_id in scene_data.character_list:
        # 只结算睡眠中的NPC，跳过玩家和非睡眠角色
        if sleeper_id == 0:
            continue
        sleeper_data = cache.character_data[sleeper_id]
        if sleeper_data.behavior.behavior_id != constant.Behavior.SLEEP:
            continue

        # 等待行为、服用安眠药的目标不受影响
        if (
            now_character_data.behavior.behavior_id == constant.Behavior.WAIT
            or sleeper_data.h_state.body_item[9][1] == 1
        ):
            continue

        # 计算本次动作对熟睡程度的影响
        down_sleep = get_sleep_disturbance_value(
            now_character_data.behavior.behavior_id, true_add_time
        )

        # 只有对玩家当前睡奸目标使用完整影响，非睡奸目标影响减半
        is_sleep_h_target = (
            sleeper_id == now_character_data.target_character_id
            and sleeper_data.sp_flag.unconscious_h == 1
        )
        if not is_sleep_h_target:
            down_sleep = max(1, down_sleep // 2)

        # 减少熟睡程度（等级>1时也只减少熟睡程度，不跳过结算）
        sleeper_data.sleep_point = max(0, sleeper_data.sleep_point - down_sleep)

        # 重新计算睡眠等级
        sleep_level, tem = attr_calculation.get_sleep_level(sleeper_data.sleep_point)

        # 只有睡眠等级<=1才会进行被吵醒判定
        if sleep_level <= 1:
            handle_npc_ai_in_h.judge_weak_up_in_sleep_h(
                character_id, sleeper_id
            )
```

要点：

- **不再只结算 `target_data`**，而是遍历 `scene_data.character_list` 中所有正在睡眠的 NPC。
- **睡眠等级 >1 不会 `continue`**：熟睡程度的减少已经在上方完成，只是不进入醒来判定。
- 等待行为或安眠药中的目标：完全不减少熟睡程度，也不进行醒来判定。
- 被吵醒判定仍放在 `settle_sleep_h()` 内，不放到 `time_judge` 位置。

### 3.4 新增动作影响分级函数

文件：`Script/Settle/realtime_settle.py`，建议放在 `settle_sleep_h()` 附近。

```python
def get_sleep_disturbance_value(behavior_id: str, true_add_time: int) -> int:
    """
    根据玩家行为类型计算对睡眠角色熟睡程度的减轻量。
    影响排序：插入 > 道具/侍奉 > 性爱 > 非性爱。
    """
    behavior_data = game_config.config_behavior.get(behavior_id)
    tags = getattr(behavior_data, "tag", "") if behavior_data else ""

    if "插入" in tags:
        factor = 3.0
    elif "道具" in tags or "侍奉" in tags:
        factor = 2.0
    elif "性爱" in tags:
        factor = 1.0
    else:
        factor = 0.5

    if true_add_time <= 0:
        return 0
    return max(1, int(true_add_time * factor))
```

说明：

- 标签数据来自 `Behavior_Data.csv` 的 `tag` 列，多个标签以 `|` 分隔。
- 标签判断顺序必须严格为“插入 → 道具/侍奉 → 性爱 → 其他”，因为插入行为通常同时带“性爱”标签。
- `WAIT` 在 `settle_sleep_h()` 中已经提前跳过，不会进入该函数。
- 完整影响与减半的规则：
  - 玩家当前睡奸目标：使用 `get_sleep_disturbance_value()` 的完整返回值。
  - 同场景其他睡眠 NPC：`down_sleep // 2`，并用 `max(1, ...)` 保证非等待动作至少产生 1 点影响。
- 该函数为纯计算函数，不访问角色状态，便于后续调试与调整数值。

### 3.5 修改 `judge_weak_up_in_sleep_h()` 支持普通睡眠者

文件：`Script/Design/handle_npc_ai_in_h.py`

当前签名：

```python
def judge_weak_up_in_sleep_h(character_id: int):
```

内部取 `target_data = cache.character_data[now_character_data.target_character_id]`，只适合睡奸目标。

修改为：

```python
def judge_weak_up_in_sleep_h(character_id: int, target_character_id: int):
```

函数内部改为使用传入的 `target_character_id`：

```python
now_character_data = cache.character_data[character_id]
target_data = cache.character_data[target_character_id]
```

吵醒概率沿用现有公式：

```python
weak_rate = game_config.config_sleep_level[1].sleep_point - target_data.sleep_point
if target_data.sleep_point <= game_config.config_sleep_level[0].sleep_point:
    weak_rate += game_config.config_sleep_level[0].sleep_point - target_data.sleep_point

if weak_rate >= random.randint(1, 100):
    # 醒来结算
```

醒来结算按目标类型分流：

```python
if target_data.sp_flag.unconscious_h == 1:
    # 睡奸目标：走现有 recover_from_unconscious_h 流程
    recover_from_unconscious_h(character_id, info_text)
else:
    # 普通睡眠NPC：清空疲劳和熟睡值，刷新异常位，强制结束睡眠行为
    target_data.tired_point = 0
    target_data.sleep_point = 0
    handle_premise.settle_chara_unnormal_flag(target_character_id, 5)
    handle_premise.settle_chara_unnormal_flag(target_character_id, 6)

    info_text = _("\n{0}被{1}的动静吵醒了\n").format(
        target_data.name, now_character_data.name
    )
    now_draw = draw.WaitDraw()
    now_draw.width = window_width
    now_draw.text = info_text
    now_draw.draw()

    character_behavior.judge_character_status_time_over(
        target_character_id, cache.game_time, end_now=2
    )
```

说明：

- 睡奸目标仍完全复用原 `recover_from_unconscious_h()`，不改变现有 H 醒来流程。
- 普通睡眠者醒来后行为被 `end_now=2` 强制结束，转为空闲并由 AI 重新选择行动。
- 普通睡眠者不会被错误传入 `recover_from_unconscious_h()`，避免 `unconscious_h == 0` 时直接返回导致无结算。

### 3.6 调用链总览

```text
character_aotu_change_value(0, ...)
└── if handle_premise.handle_scene_someone_sleeping(0):
        settle_sleep_h(0, true_add_time)
            ├── 遍历玩家当前场景所有 SLEEP NPC
            ├── WAIT/安眠药：跳过
            ├── get_sleep_disturbance_value() 计算动作影响
            ├── 睡奸目标：完整影响；普通睡眠NPC：影响减半
            ├── 所有非等待睡眠NPC：sleep_point -= down_sleep
            └── 仅当 sleep_level <= 1：
                    judge_weak_up_in_sleep_h(0, sleeper_id)
                        ├── unconscious_h == 1 -> 睡奸醒来流程
                        └── 普通睡眠 -> 清空睡眠值并强制结束睡眠行为
```

## 4. 关键改动点

| 文件 | 位置 | 改动 |
| --- | --- | --- |
| `Script/Core/constant_promise.py` | `SCENE_SOMEONE_UNCONSCIOUS` 附近，约第 257~266 行 | 新增 `SCENE_SOMEONE_SLEEPING = "place_someone_sleeping"` |
| `Script/Design/handle_premise/handle_premise_place.py` | `handle_scene_someone_unconscious` 附近，约第 407~429 行 | 新增 `handle_scene_someone_sleeping()` |
| `Script/Settle/realtime_settle.py` | `character_aotu_change_value()` 玩家分支，约第 160 行 | 进入条件改为新前提 |
| `Script/Settle/realtime_settle.py` | `settle_sleep_h()`，约第 519 行 | 重写为遍历场景内所有睡眠 NPC |
| `Script/Settle/realtime_settle.py` | `settle_sleep_h()` 附近 | 新增 `get_sleep_disturbance_value()` |
| `Script/Design/handle_npc_ai_in_h.py` | `judge_weak_up_in_sleep_h()`，约第 347 行 | 签名增加目标 id，支持普通睡眠者醒来 |

## 5. 验证

### 5.1 前提验证

1. 玩家单独在场景中，没有睡眠 NPC：`handle_scene_someone_sleeping(0)` 返回 0。
2. 同场景有一个 `behavior_id == SLEEP` 的 NPC：返回 1。
3. 同场景 NPC 在场景列表中但行为不是 SLEEP：返回 0。
4. 前提装饰器注册成功，`constant.handle_premise_data["place_someone_sleeping"]` 可调用。

### 5.2 影响分级验证

用 `get_sleep_disturbance_value()` 验证：

1. 插入标签（如 `正常位`，tag 含 `插入`）影响最大。
2. 道具/侍奉标签（如 `手交`，tag 含 `侍奉`；`捆绑`，tag 含 `道具`）次之。
3. 仅含 `性爱` 标签的行为再次之。
4. 日常/工作等非性爱标签影响最小。
5. `true_add_time <= 0` 返回 0。

### 5.3 `settle_sleep_h()` 验证

1. 玩家场景内有：
   - NPC A：`SLEEP`，`sleep_point = 20`（半梦半醒）。
   - NPC B：`SLEEP`，`sleep_point = 50`（浅睡）。
   - NPC C：`SLEEP`，`sleep_point = 75`（熟睡）。
   - NPC D：`SLEEP`，`sleep_point = 100`（完全深眠）。
2. 玩家执行非等待、非性爱动作后：
   - A/B/C/D 的 `sleep_point` 都会减少。
   - A/B 会按概率被吵醒；C/D 只减少熟睡程度，绝不会被吵醒。
   - C/D 虽然等级 >1，但结算未跳过，`sleep_point` 已下降。
3. 玩家执行 `WAIT`：所有睡眠 NPC 的 `sleep_point` 都不变，也没有醒来判定。
4. 玩家当前睡奸目标：受到完整影响。
5. 同场景其他普通睡眠 NPC：影响约为完整值的一半，且至少为 1。
6. 服用安眠药的睡眠者：`sleep_point` 不变，不醒来。

### 5.4 游戏内验证

1. 安排多个干员同房间睡觉，博士执行工作/聊天等行为。
2. 半梦半醒和浅睡者可能被吵醒，熟睡和完全深眠者只减少熟睡程度。
3. 睡奸目标醒来仍走原有无意识 H 恢复流程，不出现重复提示。
4. 普通睡眠者被吵醒后显示“{A}被{B}的动静吵醒了”，并结束睡眠行为，由 AI 选择新行动。
5. Web 模式下提示与等待行为正常。

## 6. 风险与回滚

- **风险 1：与睡奸系统重复判定。** 通过 `unconscious_h` 分流解决：睡奸目标走 `recover_from_unconscious_h()`，普通睡眠者走强制结束睡眠流程。
- **风险 2：熟睡角色被过快扣到浅睡。** 这是需求允许的结果；影响系数若不平衡，后续只调整 `get_sleep_disturbance_value()` 中的 factor。
- **风险 3：玩家场景内多个睡眠者时输出多条提示。** 使用 `WaitDraw` 逐条绘制，和现有醒来说明一致；Web 模式需重点验证。
- **风险 4：前提热路径开销。** 新前提每次玩家实时结算只遍历当前场景角色，且只做行为 ID 判断，开销很小。
- **风险 5：`judge_weak_up_in_sleep_h` 签名变更。** 当前只有 `settle_sleep_h()` 一个调用点，同步修改即可；如后续其他模块调用，搜索更新。
- **回滚**：恢复 `realtime_settle.py`、`handle_npc_ai_in_h.py` 的旧版本，并删除新前提常量与函数即可，无数据文件改动。

## 7. 改动文件清单

| 文件 | 类型 | 改动 |
| --- | --- | --- |
| `Script/Core/constant_promise.py` | 修改 | 注册 `SCENE_SOMEONE_SLEEPING` 前提常量 |
| `Script/Design/handle_premise/handle_premise_place.py` | 修改 | 实现 `handle_scene_someone_sleeping()` |
| `Script/Settle/realtime_settle.py` | 修改 | 修改进入条件；重写 `settle_sleep_h()`；新增影响分级函数 |
| `Script/Design/handle_npc_ai_in_h.py` | 修改 | `judge_weak_up_in_sleep_h()` 支持传入目标 id 与普通睡眠者醒来 |

## 8. 不在本 Plan 范围

- 不修改 `Sleep_Level.csv` 阈值与睡眠恢复公式。
- 不新增 CSV 配置项；动作影响系数先写在 `get_sleep_disturbance_value()` 中。
- 不修改 NPC 之间的睡眠吵醒关系；本 Plan 仍以“玩家动作影响同房间睡眠 NPC”为范围。
- 不处理关门房间隔音、不同动作发出声音差异等更细的规则。
