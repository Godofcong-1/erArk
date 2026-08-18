# Plan 03：破处记录在中断 H 时回溯到上一个有效 H 指令

- 状态：待实施
- 来源：`todo list.txt` → `# 待处理的小问题` → “如果破处的时候记录的指令为中断H指令，则往前回溯一个指令记录”
- 预计改动量：1 个文件（`Script/Settle/default.py`），约 30~50 行
- 风险等级：低
- 适用代码快照：`master @ b17d1b1ba`（v0.66）

---

## 1. 问题描述

角色第一次性交（破处）时，游戏会把“当前玩家最后一个指令的中文名”写入 `first_record.first_sex_posture` 等字段作为破处体位记录。

但破处结算可能发生在 H 因意外中断而结束时。此时 `cache.pl_pre_behavior_instruce` 的最后一条已经是中断类指令（如 `h_interrupt`、`h_hp_0`），导致破处体位被记录为“H中断”之类文本，而不是真正的插入体位。

需要：取“最近一次破处体位记录指令”时，如果最后一条是中断 H 指令，则向前回溯，找到最近一条非中断指令。

## 2. 现状调查

### 2.1 玩家最近指令记录

- 字段：`cache.pl_pre_behavior_instruce`（`game_type.Cache`）
- 写入位置：`Script/Design/character_behavior.py::character_instruct_record()` / 玩家阶段
- 当前行为循环只保留最近 10 条：
  ```python
  if len(cache.pl_pre_behavior_instruce) > 10:
      cache.pl_pre_behavior_instruce.pop(0)
  ```

### 2.2 现有破处记录代码

文件：`Script/Settle/default.py`

| 函数 | 行号（当前快照） | 当前取指令方式 |
| --- | ---: | --- |
| `handle_first_sex` | 1009；取指令约 1031 | `behavior_id = cache.pl_pre_behavior_instruce[-1]` |
| `handle_first_a_sex` | 1095；取指令约 1120 | `behavior_id = cache.pl_pre_behavior_instruce[-1]` |
| `handle_first_u_sex` | 1161；取指令约 1186 | `behavior_id = cache.pl_pre_behavior_instruce[-1]` |
| `handle_first_w_sex` | 1208；取指令约 1228 | `behavior_id = cache.pl_pre_behavior_instruce[-1]` |

四个函数随后都执行：

```python
behavior_data = game_config.config_behavior[behavior_id]
instruct_name = behavior_data.name
```

并把 `instruct_name` 写入各自的 `first_*_posture` 字段。

### 2.3 已有中断 H 指令集合

文件：`Script/Core/constant/__init__.py`

```python
special_end_H_list = [
    Behavior.H_INTERRUPT,
    Behavior.H_HP_0,
    Behavior.T_H_HP_0,
    Behavior.GROUP_SEX_PL_HP_0_END,
    Behavior.HYPNOSIS_CANCEL,
    Behavior.TIME_STOP_OFF,
]
""" 意外中断H的行为id列表 """
```

该集合已经维护好，直接复用即可，不需要新增常量。

### 2.4 为什么改动很小

- 四个函数逻辑完全相同，可提取一个共享 helper，然后各替换一行。
- 判断逻辑只是“从列表尾部向前找第一个不在 `special_end_H_list` 中的 id”。
- 不改变 CSV、存档结构、口上选择，只改变一个字符串记录的取值。

## 3. 实施方案

### 3.1 新增共享 helper 函数

放在 `Script/Settle/default.py` 顶部公共区域（例如第一个 `@settle_behavior` 函数之前），函数名为：

```python
def get_last_valid_sex_behavior_id() -> str:
    """
    获取玩家最近一条非中断H指令的behavior_id。

    输入：无
    返回：
        str -- 最近一条非中断H指令的behavior_id；
               若列表为空，返回 "share_blankly" 作为兜底。
    功能：
        从 cache.pl_pre_behavior_instruce 尾部向前遍历，
        跳过 constant.special_end_H_list 中的中断指令，
        返回第一条有效指令。
    """
```

实现伪代码：

```python
def get_last_valid_sex_behavior_id() -> str:
    from Script.Core import constant

    for behavior_id in reversed(cache.pl_pre_behavior_instruce):
        if behavior_id not in constant.special_end_H_list:
            return behavior_id

    return constant.Behavior.SHARE_BLANKLY
```

说明：

- `cache` 与 `constant` 在 `default.py` 中已经可用（当前文件已有相关 import），按文件顶部实际 import 情况放置，不要重复 import。
- 兜底 `SHARE_BLANKLY` 只是防止空列表导致 `[-1]` 崩溃；正常破处流程中列表至少有一条插入行为。
- 保留最近 10 条的限制足够：回溯目标只可能是前 1~2 条中断指令，不会超出窗口。

### 3.2 替换四个取指令位置

将四个函数中的：

```python
behavior_id = cache.pl_pre_behavior_instruce[-1]
```

统一替换为：

```python
behavior_id = get_last_valid_sex_behavior_id()
```

即改动点：

1. `handle_first_sex` 约第 1031 行
2. `handle_first_a_sex` 约第 1120 行
3. `handle_first_u_sex` 约第 1186 行
4. `handle_first_w_sex` 约第 1228 行

其他逻辑（`behavior_data` 查找、`instruct_name` 写入）保持不变。

### 3.3 兼容性说明

- `cache.pl_pre_behavior_instruce` 在新代码中保存的是字符串 behavior_id；旧存档读取时已有字符串化兼容逻辑，不会影响本函数。
- 如果某条记录不是字符串或不在 `config_behavior` 中，本 helper 不会引入新的错误：它只负责跳过 `special_end_H_list`，后续 `game_config.config_behavior[behavior_id]` 的异常表现与现状相同。
- `special_end_H_list` 中的 id 已经是 `constant.Behavior` 常量字符串，与列表元素类型一致。

## 4. 验证

### 4.1 单元级验证（推荐先做）

在游戏内调试面板或临时测试脚本中：

1. 构造 `cache.pl_pre_behavior_instruce = ["normal_sex", "h_interrupt"]`
2. 调用 `get_last_valid_sex_behavior_id()`，应返回 `"normal_sex"`
3. 构造 `["normal_sex", "h_hp_0", "h_interrupt"]`，应返回 `"normal_sex"`
4. 构造 `["normal_sex"]`，应返回 `"normal_sex"`
5. 构造 `[]`，应返回 `"share_blankly"`

### 4.2 游戏内验证

1. 选一名处女干员，进入可插入 H。
2. 在插入过程中触发中断（如 H 体力归零、打断、解除时停等）。
3. 查看角色信息/肉体信息中的“初体验姿势”或 `first_record.first_sex_posture`。
4. 确认记录的是插入体位（如“正常位”“背面座位”等），而不是“H中断”。
5. 分别验证 V/A/U/W 四种破处路径（对应四个函数）。
6. 正常无中断破处：结果与改动前完全一致。

## 5. 风险与回滚

- **风险 1：函数放置位置。** 应放在 `default.py` 模块级函数区，不要在某个注册函数内部定义，否则只对局部可见。
- **风险 2：循环变量命名。** 使用 `behavior_id` 会与外部函数中的同名变量无冲突（Python 作用域独立），但保持清晰。
- **风险 3：空列表。** 已用 `SHARE_BLANKLY` 兜底；若 `config_behavior` 中该 id 不存在会导致后续 KeyError，但该 id 是基础行为，必然存在。
- **回滚**：恢复 `Script/Settle/default.py` 即可，无数据文件改动。

## 6. 改动文件清单

| 文件 | 类型 | 改动 |
| --- | --- | --- |
| `Script/Settle/default.py` | 修改 | 新增 `get_last_valid_sex_behavior_id()`；替换 4 处 `pl_pre_behavior_instruce[-1]` |

## 7. 不在本 Plan 范围

- 不处理 `handle_first_kiss` / `handle_first_kiss_to_penis`（初吻记录不在本 todo 描述内；如后续需要，可用同一 helper 评估）。
- 不修改 `special_end_H_list` 的成员定义。
- 不修改存档字段，`first_record.first_*_posture` 仅改变写入值。
