# Plan 02：快速测试口上面板支持一次测试多条口上

- 状态：基础功能已实现；本文档已同步后续两轮优化（编号与详细汇总、超过 10 条分组测试）
- 来源：`todo list.txt` → `# 待处理的小问题` → “单次测试多条口上”
- 预计改动量：1 个文件（`Script/UI/Panel/debug_panel.py`）
- 风险等级：低
- 适用代码快照：`master @ b17d1b1ba`（v0.66）

### 修订记录

| 版本 | 内容 |
| --- | --- |
| v1 | 基础方案：支持逗号分隔/区间输入，一次测试多条口上 |
| v2 | 优化一：每条测试前打印全局编号；最终汇总详细列出通过/未通过的口上 id |
| v3 | 优化二：数量大于 10 条时，每 10 条一组测试与显示，每组完成后手动选择是否继续下一轮 |

---

## 1. 目标

现有调试面板“快速测试口上”一次只能输入一个口上 id。目标是：

1. 支持一次输入多个口上 id（逗号分隔或区间）。
2. 批量输出每条口上的触发判定与文本。
3. 每条测试信息前打印全局编号，方便用户按编号追溯。
4. 最终汇总除数量统计外，换行详细列出所有通过的口上 id 和未通过的口上 id。
5. 当测试数量大于 10 条时，每 10 条一组进行测试和显示；用户确认完本轮后，手动选择继续下一轮，直到完成所有测试。

## 2. 现状调查

### 2.1 现有实现位置

- 文件：`Script/UI/Panel/debug_panel.py`
- 类：`TALK_QUICK_TEST`
- 面板入口：`normal_flow.py` 中 `constant.Panel.TALK_QUICK_TEST`
- 当前流程（`TALK_QUICK_TEST.draw()`）：
  1. 显示菜单：`[001]刷新口上文件后测试` / `[002]直接开始测试`
  2. 输入角色 `adv_id`，按 `adv` 找到运行时 `character_id`
  3. 输入单个口上 id
  4. 拼出 `full_talk_id = f"chara_{adv_id:04d}_{chara_name}{talk_id}"`
  5. 在 `game_config.config_talk` 中查找该口上
  6. 逐项检查：角色是否已获得、交互对象是否为目标、触发人/交互对象推断、口上原文本与输出文本、每个前提是否满足
  7. 汇总“测试通过/测试未通过”并绘制

### 2.2 可复用条件

- 单条测试的所有核心逻辑都集中在 `draw()` 内部，除最后 `WaitDraw` 绘制外，没有外部副作用。
- 唯一会影响游戏状态的操作是：
  ```python
  cache.character_data[start_chara_id].target_character_id = end_chara_id
  ```
  批量模式下必须先保存博士当前交互对象，测试结束后恢复。
- `game_config.config_talk` 的 key 规则已确认：`chara_0001_阿米娅0`、`chara_0001_阿米娅99` 等。
- 该面板是 debug 面板，改坏不会影响正常游戏流程。

## 3. 实施方案

### 3.1 抽出一个单条测试函数

在 `TALK_QUICK_TEST` 类中新增方法：

```python
def test_single_talk(
    self,
    target_chara_id: int,
    talk_id: int,
) -> tuple[str, bool]:
    """
    测试单条角色口上并返回文本化的测试报告。
    输入：
        target_chara_id -- 目标角色的运行时 character_id
        talk_id -- 口上数字 id
    返回：
        tuple[str, bool] -- 测试报告文本、是否通过
    """
```

该函数内容：把现有 `draw()` 中“从 `full_talk_id` 构造到最终结果拼完 `draw_text`”的整段代码搬入，并删除其中的 `draw.WaitDraw().draw()` 等绘制调用，返回 `(draw_text, pass_flag)`。

保持不变的部分：

- 角色与口上存在性判断
- `full_talk_id` 构造（改为使用 `target_character_data.adv` 与 `target_character_data.name`）
- 触发人/交互对象推断
- 前提逐项判定（`CVP_` 走 `handle_premise.handle_comprehensive_value_premise`，其他走 `constant.handle_premise_data[premise]`）
- 通过/未通过结论
- 报告头部增加“口上id”一行，便于批量模式下追溯

### 3.2 新增批量 id 解析函数

```python
def parse_talk_id_list(self, input_text: str) -> List[int]:
    """
    将玩家输入解析为口上 id 列表。
    支持格式：
        "12"           -> [12]
        "12,15,18"     -> [12, 15, 18]
        "12-15"        -> [12, 13, 14, 15]
        "12-15,20"     -> [12, 13, 14, 15, 20]
    输入：
        input_text -- 面板输入的字符串
    返回：
        List[int] -- 去重后的口上 id 列表
    """
```

解析规则：

1. 先按 `,` 或中文逗号 `，` 切分。
2. 每段若含 `-` 且左右都是数字，则展开为闭区间；左右数字反序时自动交换。
3. 对列表去重并保持输入顺序。
4. 空段、非数字段直接跳过；全部非法时返回空列表。

该函数只做字符串解析，不访问游戏状态。

### 3.3 修改菜单：增加“批量测试”按钮

在现有两个按钮后新增：

```python
button_text = _("[003]批量测试多条口上")
button3_draw = draw.LeftButton(
    button_text,
    button_text,
    len(button_text) * 2,
    cmd_func=self.nothing,
)
button3_draw.draw()
return_list.append(button3_draw.return_text)
```

同时在面板说明文本中补充：

```text
批量测试时，口上id支持逗号分隔（如1,3,5）和区间（如95-98）
```

在 `draw()` 的菜单分支判断中：

- `[001]` / `[002]`：设置 `batch_mode = False` 后进入测试。
- `[003]`：设置 `batch_mode = True` 后进入测试。

### 3.4 批量测试执行总控（draw 分支）

在第二阶段的“输入口上 id”处，根据 `batch_mode` 显示不同提示：

- 单条模式：`请输入口上id`
- 批量模式：`请输入口上id（支持1,3,5或95-98）`

解析输入后：

```python
talk_id_list = self.parse_talk_id_list(talk_id_text)

if not talk_id_list:
    # 提示“未输入有效的口上id”，绘制返回按钮
    ...
elif len(talk_id_list) > 10:
    # 数量超过10条：走分组测试流程
    self.run_batch_talk_test_in_groups(target_chara_id, talk_id_list)
else:
    # 10条及以下：一次性测试并显示，逻辑见 3.5
    ...
```

### 3.5 优化一：每条编号打印与详细汇总

#### 3.5.1 每条编号

一次性路径（10 条及以下）与分组路径都使用全局编号：

```python
for talk_index, talk_id in enumerate(talk_id_list, 1):
    report_text, pass_flag = self.test_single_talk(target_chara_id, talk_id)

    report_lines.append(
        _("\n===== 第 {0} 条 / 共 {1} 条（口上id：{2}） =====").format(
            talk_index, len(talk_id_list), talk_id
        )
    )
    report_lines.append(report_text)
```

分组路径中，`talk_index` 使用全局起始序号，例如第二组第 1 条显示“第 11 条 / 共 25 条”。

#### 3.5.2 收集通过/未通过 id

除 `pass_count` / `fail_count` 外，额外维护：

```python
pass_id_list = []
fail_id_list = []
```

每条测试结束后按 `pass_flag` 分别追加 `talk_id`。

#### 3.5.3 最终汇总格式

```text
汇总：共测试 X 条，通过 Y 条，未通过 Z 条

通过的口上id：1、3、5
未通过的口上id：2、4
```

对应实现：

```python
report_lines.append(
    _("\n汇总：共测试 {0} 条，通过 {1} 条，未通过 {2} 条").format(
        total_count, pass_count, fail_count
    )
)

if pass_id_list:
    report_lines.append(
        _("\n通过的口上id：{0}").format(
            "、".join(str(talk_id) for talk_id in pass_id_list)
        )
    )
else:
    report_lines.append(_("\n通过的口上id：无"))

if fail_id_list:
    report_lines.append(
        _("未通过的口上id：{0}\n").format(
            "、".join(str(talk_id) for talk_id in fail_id_list)
        )
    )
else:
    report_lines.append(_("未通过的口上id：无\n"))
```

### 3.6 优化二：超过 10 条按每 10 条一组测试与显示

新增方法：

```python
def run_batch_talk_test_in_groups(
    self,
    target_chara_id: int,
    talk_id_list: List[int],
):
    """
    按每10条一组分批测试口上，每组显示后等待用户手动选择是否继续。
    输入：
        target_chara_id -- 目标角色的运行时 character_id
        talk_id_list -- 待测试的口上 id 列表
    返回：
        无
    """
```

#### 3.6.1 分组规则

```python
total_count = len(talk_id_list)
group_size = 10
group_count = (total_count + group_size - 1) // group_size
```

- 第一组：第 1~10 条。
- 第二组：第 11~20 条。
- 依此类推，最后一组不足 10 条时按实际剩余条数显示。

#### 3.6.2 组内测试与显示

- 组内每条仍调用 `test_single_talk()`。
- 每条报告前打印全局编号：
  ```text
  ===== 第 11 条 / 共 25 条（口上id：42） =====
  ```
- 组的累计通过/未通过 id 写入 `all_pass_id_list` / `all_fail_id_list`。

#### 3.6.3 非最后一组结束后的手动确认

本组报告末尾追加：

```text
本轮已测试第 1-10 条，请确认后选择是否继续下一轮
```

先绘制 `WaitDraw` 等待用户确认本组内容，再绘制两个按钮：

- `[继续下一轮测试]`
- `[停止测试并查看汇总]`

```python
yrn = flow_handle.askfor_all([
    continue_draw.return_text,
    stop_draw.return_text,
])

if yrn == stop_draw.return_text:
    test_stopped = True
    break
```

选择“继续下一轮测试”时，进入下一组测试和显示；选择“停止测试并查看汇总”时，结束循环并显示当前累计汇总。

#### 3.6.4 最后一组

最后一组测试后直接显示该组报告，然后统一显示最终汇总，不需要再次手动确认继续。

#### 3.6.5 最终汇总

- 所有组测试完成后，汇总统计已测试的全部条目。
- 若用户中途停止，汇总前先提示：
  ```text
  测试已停止，以下是已测试部分的汇总
  ```
- 汇总格式与 3.5.3 相同：
  ```text
  汇总：共测试 X 条，通过 Y 条，未通过 Z 条

  通过的口上id：...
  未通过的口上id：...
  ```

#### 3.6.6 状态保护

- 进入分组测试前保存博士当前交互对象：
  ```python
  old_target_character_id = pl_character_data.target_character_id
  ```
- 无论测试完成还是中途停止，都在 `finally` 中恢复：
  ```python
  pl_character_data.target_character_id = old_target_character_id
  ```

### 3.7 保持单条模式与错误处理

- 原有 `[002]直接开始测试` 的单条流程保留，复用同一个 `test_single_talk`。
- 单条模式下输入无法转换为非负整数时，提示“口上id输入错误，请重新进入面板输入”，不再因 `int()` 失败抛出异常。
- 批量模式下解析结果为空时，提示“未输入有效的口上id，请重新进入面板输入”。

## 4. 当前实现的关键改动点

以下行号为当前工作区实际实现位置：

| 位置 | 内容 |
| ---: | --- |
| `TALK_QUICK_TEST.draw()`，约第 163 行起 | 主面板流程：菜单、单条/批量分支 |
| 约第 196~200 行 | `[003]批量测试多条口上` 按钮 |
| 约第 244~248 行 | 根据 `batch_mode` 显示不同的口上 id 输入提示 |
| 约第 256~301 行 | 批量解析、`>10` 分组分流、`<=10` 一次性输出 |
| 约第 275~298 行 | 一次性路径的编号打印、通过/未通过 id 收集、详细汇总 |
| 约第 329~436 行 | `test_single_talk()`：单条测试报告生成，返回 `(report, passed)` |
| 约第 439~512 行 | `run_batch_talk_test_in_groups()`：每 10 条分组、组间手动续跑、最终汇总 |
| 约第 515 行起 | `parse_talk_id_list()`：逗号/区间解析与去重 |
| 约第 548 行起 | `refresh_talk_file()`：保持原有刷新功能 |

## 5. 测试与验证

### 5.1 构建

- 此改动为纯 Python UI 逻辑，不涉及 CSV/JSON 构建。
- 直接运行 `python game.py` 即可生效（`config.ini -> debug = 1` 时可见调试面板）。

### 5.2 解析用例

| 输入 | 期望结果 |
| --- | --- |
| `12` | `[12]` |
| `12,15,18` | `[12, 15, 18]` |
| `12-15` | `[12, 13, 14, 15]` |
| `12-15,20` | `[12, 13, 14, 15, 20]` |
| `1，3,5` | `[1, 3, 5]` |
| `3-1` | `[1, 2, 3]` |
| `1,1,2-3` | `[1, 2, 3]` |
| `abc,5` | `[5]` |
| 空输入 | `[]` |

### 5.3 面板验证用例

1. **单条兼容**：输入 `42`，结果与改动前一致。
2. **多条编号**：输入 `10,11,12`，每条报告前显示“第 1/2/3 条 / 共 3 条（口上id：...）”。
3. **区间**：输入 `95-98`，输出 95、96、97、98 共 4 条报告。
4. **混合**：输入 `1,3-5,9`，输出 1、3、4、5、9 共 5 条报告。
5. **不存在 id**：某条在 `config_talk` 中不存在时，显示“未找到该口上（id=...）”，计入失败但不中断后续条目。
6. **详细汇总**：测试结束后汇总同时显示数量统计、所有通过 id、所有未通过 id；“无”的情况正确显示。
7. **状态恢复**：批量测试结束后，博士交互对象恢复到进入面板前的值。
8. **11 条分组**：输入 `1-11`，第一组显示第 1~10 条，末尾出现“本轮已测试第 1-10 条”，并提供“继续下一轮测试/停止测试并查看汇总”。
9. **继续下一轮**：选择继续后，显示第 11 条（编号“第 11 条 / 共 11 条”），随后显示最终汇总。
10. **中途停止**：输入 `1-25`，第一组后选择“停止测试并查看汇总”，输出“测试已停止，以下是已测试部分的汇总”，统计仅包含已测试的 10 条。
11. **长报告**：分组后每轮 `WaitDraw` 文本长度可控，不出现错位或崩溃。

## 6. 风险与回滚

- **游戏状态污染**：唯一写入是 `target_character_id`，单条路径沿用原行为；批量路径已通过保存/恢复机制控制博士交互对象。
- **代码重复**：抽函数时不要把绘制调用带进去；重构后单条、`<=10` 批量、分组批量三者共用 `test_single_talk()`。
- **长文本**：`>10` 条时已分组为每轮最多 10 条，避免一次性生成过长文本。
- **分组输出累积**：每组新报告会追加在上一组报告之后；当前面板未强制清屏，若后续需要可再增加分组间清屏逻辑。
- **回滚**：恢复 `debug_panel.py` 旧版本即可，无其他关联文件。

## 7. 改动文件清单

| 文件 | 类型 | 改动 |
| --- | --- | --- |
| `Script/UI/Panel/debug_panel.py` | 修改 | 新增 `test_single_talk()`、`parse_talk_id_list()`、`run_batch_talk_test_in_groups()`；新增 `[003]` 批量入口；实现编号打印、详细汇总与 `>10` 条分组显示 |

## 8. 不在本 Plan 范围

- 不修改口上选择核心逻辑（`Script/Design/talk.py`）。
- 不做真实口上抽取/模拟结算，只沿用现有“静态判定”测试方式。
- 不做 UI 批量导出报告到文件；后续如需要可在 `test_single_talk` 返回文本基础上追加。
- 不做组间自动清屏；如后续体验需要，再评估是否在每组测试前清屏。
