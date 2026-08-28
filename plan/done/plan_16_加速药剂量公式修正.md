# Plan 16：妊娠/孵化加速药剂量公式修正（改为"剩余孕期的30%"）

- 状态：已实施（2026-08-28，单元测试 25/25 通过，见 §10；游戏内整体测试由用户执行）
- 来源：用户需求 → 在 plan_14（怀孕系统四种药物）验收后的追加调整：每次加速量应为"总孕期 − 已自然经过天数 − 已累计加速天数"的 30%（即真实剩余孕期的 30%），而非现行的"(270 − 已累计加速) × 30%"
- 预计改动量：2 个逻辑文件约 10 行 + 1 个工作流文档 1 行 + update.log 1 条
- 风险等级：低（单点公式改动，无 CSV/常量/存档结构变更，无需 buildconfig）
- 适用代码快照：`master @ f7e1acd8d`（2026.8.28）
- 参考文档：`plan/done/plan_14_怀孕系统四种药物.md`（§3.3 原剂量口径）、`.github/prompts/数据处理工作流/妊娠系统.md` §15.1

---

## 1. 目标

1. **妊娠加速药（道具35）**：每次使用的加速量改为 `(名义总孕期 270 − 当前有效孕期天数) × 30%`，其中有效孕期天数 = 自受精起自然经过天数 + 已累计加速天数。
   - 用户示例：总孕期 270 天、已自然经过 60 天、首次用药 → (270−60)×30% = 63 天；紧接着第二次 → (270−60−63)×30% = 44.1 天。
2. **孵化加速药（道具36）**：同口径，基数改用孵化总天数 265（见 §3.2 设计决策），加速量 = `(265 − 当前有效孵化天数) × 30%`。
3. 既有的累计上限 250 天与"临盆/破壳前一天"封顶两项夹取维持不变。

## 2. 现状调查（已完成，均为实际代码核实结果）

### 2.1 现行剂量公式（问题所在）

核心函数 `pregnancy_handle.py:54-65 get_acceleration_amount(now_acc, effective_day, day_cap)`：

```python
formula_amount = (PREGNANCY_TOTAL_DAY - now_acc) * 0.3
return min(formula_amount, ACCELERATION_MAX_DAY - now_acc, day_cap - effective_day)
```

- 常量（[pregnancy_handle.py:33-38](../../Script/System/Pregnancy_System/pregnancy_handle.py#L33)）：`PREGNANCY_TOTAL_DAY=270`（名义孕期，剂量基数）、`ACCELERATION_MAX_DAY=250`（累计上限）、`PARTURIENT_DAY=260`（临盆阈值）。
- **A 项（剂量公式）只基于已累计加速 `now_acc`，完全不考虑自然经过天数**：无论怀孕第 1 天还是第 200 天，首剂恒定 (270−0)×0.3=81 天，叠加序列固定 81 → 56.7 → 39.69 → …。
- C 项（`day_cap − effective_day`）是唯一引入自然天数的地方，仅起"不越过临盆/破壳前一天"的截断作用，不影响 A 项剂量。
- Item.csv 的道具描述写的是"将剩余孕期缩短30%"（[data/csv/Item.csv:26-27](../../data/csv/Item.csv#L26)），与代码实况不符——本次修正后描述才真正吻合，**CSV 无需改动**。

### 2.2 调用点全量清单（grep 穷举，改公式即全局生效，无旁路）

| 调用方 | 位置 | 传入的 effective_day / day_cap |
| --- | --- | --- |
| 妊娠 `get_pregnancy_acceleration_amount` | [pregnancy_handle.py:68-78](../../Script/System/Pregnancy_System/pregnancy_handle.py#L68) | `get_pregnancy_past_day`（自然+累计，:41-51）/ `PARTURIENT_DAY−1=259` |
| 卵 `get_egg_acceleration_amount` | [egg_handle.py:138-148](../../Script/System/Pregnancy_System/egg_handle.py#L138) | `get_hatch_day`（:126-135）/ `HATCH_TOTAL_DAY−1=264`；**公式基数现状硬编码 270 而非 HATCH_TOTAL_DAY=265**（plan_14 §11"与妊娠版完全一致"旧口径） |

消费方（全部经上述两函数，本次零改动）：`gift_panel.py:70/89`（`handle_drug_use_effect` 35/36 分支的效果结算）、`gift_panel.py:434`（`is_drug_effective` 送出前校验）、`egg_handle.py:161`（`get_accelerable_hatching_eggs` 可加速卵筛选、选卵列表数据源）。

### 2.3 需同步/无需同步的文档与数据

- [妊娠系统.md:425](../../.github/prompts/数据处理工作流/妊娠系统.md#L425)（§15.1）记有旧公式与"首次 81 天、第二次 56.7 天"示例——**需改**。
- [礼物系统.md:280](../../.github/prompts/数据处理工作流/礼物系统.md#L280) 只提"复用 get_acceleration_amount（三重夹取）"不载公式——无需改。
- `data/csv/Item.csv` 与 `tools/ArkEditor/csv/Item.csv` 的 35/36 行 info——无需改（§2.1）。

### 2.4 已知陷阱与硬约束

- 累计值以 float 存储、消费/显示时 `int()` 向下取整（`game_type.py` PREGNANCY.acceleration_days 注释约定）——新公式沿用，不改取整口径。
- `effective_day` 为 int（`timedelta.days` + `int(acc)`），公式内直接使用即可。
- 存档兼容：`acceleration_days` 字段语义不变（"已入账的额外天数"），旧存档已入账数值原样有效，**无回填/迁移需求**。
- 无 CSV/常量/翻译词条改动，**无需 buildconfig / buildpo / buildmo**。
- 新公式下 A 项理论上可为负（有效天数 > 基数），但 C 项（259/264）恒先于 A 项归零（259<270、264<265），"返回 ≤0 即不可用"的既有判定语义不变。

## 3. 设计决策

### 3.1 公式 A 项改为基于有效天数

`formula_amount = (total_day - effective_day) * 0.3`。`effective_day` 两个调用方已在传参，改动收敛在函数体一行 + docstring；每次用药后有效天数增加（且自然天数继续流逝），下一剂自动按新的剩余期计算，与用户示例口径一致。

### 3.2 基数参数化，卵改用 265

函数签名改为 `get_acceleration_amount(now_acc, effective_day, day_cap, total_day=PREGNANCY_TOTAL_DAY)`；妊娠传 270（默认值）、卵调用处显式传 `HATCH_TOTAL_DAY=265`。

- 理由：新公式语义是"剩余期的 30%"，卵的"总期"就是孵化总天数 265，沿用 270 会虚增剩余 5 天。
- 弃选：维持 270 统一基数（plan_14 §11 旧口径）——该口径是旧公式（基数只与累计加速相减）下"体验统一"的产物，新公式下语义不再成立；两者差异仅首剂 ±1.5 天，如需改回只动 egg_handle 一处传参。

### 3.3 B/C 两项夹取与下游全部维持不变

- B 项 `ACCELERATION_MAX_DAY − now_acc`（累计 250 封顶）与 C 项 `day_cap − effective_day`（临盆 259/破壳 264 封顶）不动，与新 A 项不冲突。
- `is_drug_effective`、`handle_drug_use_effect`、`get_accelerable_hatching_eggs`、选卵交互、面板显示（预计日期 = `基准时间 + timedelta(阈值 − int(累计))`）均与公式无耦合，零改动。

## 4. 详细改动步骤

### 4.1 剂量公式（Script/System/Pregnancy_System/pregnancy_handle.py:54-65）

```python
def get_acceleration_amount(now_acc: float, effective_day: int, day_cap: int, total_day: int = PREGNANCY_TOTAL_DAY) -> float:
    """
    计算加速药单次可入账的加速天数（三重夹取：剩余期30%/累计上限250/临盆(破壳)前一天）
    Keyword arguments:
    now_acc -- 当前已累计的加速天数
    effective_day -- 当前有效天数（自然天数+已累计加速）
    day_cap -- 注入后允许的有效天数上限（胎生259=临盆前一天，卵264=破壳前一天）
    total_day -- 剂量公式基数（胎生为名义孕期270，卵为孵化总天数265）
    Return arguments:
    float -- 可入账加速天数（<=0时表示已到极限无法使用）
    """
    # 剂量为剩余期（基数-当前有效天数）的30%
    formula_amount = (total_day - effective_day) * 0.3
    return min(formula_amount, ACCELERATION_MAX_DAY - now_acc, day_cap - effective_day)
```

（代码为意图示例，实施时以实际代码为准；`PREGNANCY_TOTAL_DAY` 的 docstring 同步改为"名义孕期总天数（妊娠加速药剂量公式的基数）"。）

### 4.2 卵侧传参（Script/System/Pregnancy_System/egg_handle.py:148 get_egg_acceleration_amount）

```python
    return pregnancy_handle.get_acceleration_amount(now_acc, get_hatch_day(egg_data), HATCH_TOTAL_DAY - 1, HATCH_TOTAL_DAY)
```

docstring 补一句"剂量基数为孵化总天数265"。

### 4.3 工作流文档（.github/prompts/数据处理工作流/妊娠系统.md:425）

§15.1 剂量公式行改写为：单次入账 = min((基数−当前有效天数)×0.3, 250−已累计, 上限天数−当前有效天数)，基数胎生 270 / 卵 265；示例改为"已自然经过 60 天时首剂 63 天、紧接着第二剂 44.1 天（自然 0 天首剂仍为 81 天）"。

### 4.4 更新日志（update.log）

实施完成并通过验证后，按 `update-changelog` 体例登记"调整"条目（妊娠/孵化加速药的加速量改为按剩余孕期的 30% 计算）。

## 5. 构建与缓存

无 CSV/常量/地图/翻译词条改动，**无需 buildconfig / buildpo / buildmo / 删缓存**，直接运行游戏即生效。

## 6. 验证清单

### 6.1 单元测试（实施方执行，headless-game-test 方式，scratchpad 脚本不入库）

- [x] 妊娠新公式：自然 60 天、累计 0 → 首剂 63.0；立即第二剂（累计 63、有效 123）→ 44.1（用户示例复算）。
- [x] 回归锚点：自然 0 天首剂 = 81.0（与旧公式同值）。
- [x] C 项夹取：自然 250 天 → 6.0 → 3.0 → 拒绝（有效 259 封顶，不越过临盆前一天）；卵同理 264 封顶。
- [x] B 项仍可达：自然 0 天连续用药（81 → 56.7 → …）衰减至累计 250 封顶后 `is_drug_effective` 拒绝。
- [x] 卵基数 265：排出 100 天、累计 0 → 首剂 49.5；`get_accelerable_hatching_eggs` 正确过滤已达极限的卵。
- [x] 回归：`is_drug_effective` 35/36 各拦截路径文案不变；旧存档卵缺 `acceleration_days` 键 `.get` 兜底不崩溃；送礼→结算→提示全链（含选卵）不崩溃，提示中的本次/累计/预计日期与新公式一致。

### 6.2 游戏内整体测试（由用户执行）

- [ ] 对已怀孕多日的干员使用妊娠加速药：提示的本次加速天数明显小于 81 且随孕程推进递减；总览/身体信息面板预计日期同步。
- [ ] 对孵化多日的卵使用孵化加速药：口径同上（基数 265）。
- [ ] Tk 与 Web 两种绘制模式均正常；旧存档（含已用过旧公式药的存档）载入与继续用药不报错。

## 7. 风险与回滚

| 风险 | 说明 | 对策 |
| --- | --- | --- |
| 数值体验变化 | 孕程后期用药收益大幅降低（如自然 200 天首剂仅 21 天），系有意为之 | §6.2 由用户游戏内验收 |
| 旧存档混算 | 旧公式已入账的大额加速与新公式叠加 | `acceleration_days` 语义不变（已入账天数），新公式按当前有效天数算剩余，天然兼容，无需迁移 |
| 卵基数改动争议 | 265 与 plan_14"统一 270"旧口径不同 | §3.2 已述理由；如需改回仅动 egg_handle 一处传参 |

**回滚**：还原 `get_acceleration_amount` 函数体与签名、`egg_handle.py:148` 传参、`妊娠系统.md:425` 文档行即可，无存档残留问题（已入账天数在两版公式下语义一致），无需重跑任何构建。

## 8. 改动文件清单

| 文件 | 类型 | 改动 |
| --- | --- | --- |
| `Script/System/Pregnancy_System/pregnancy_handle.py` | 修改 | `get_acceleration_amount` 加 `total_day` 参数、A 项改 `(total_day − effective_day) × 0.3`、docstring 更新 |
| `Script/System/Pregnancy_System/egg_handle.py` | 修改 | `get_egg_acceleration_amount` 传 `total_day=HATCH_TOTAL_DAY`、docstring 更新 |
| `.github/prompts/数据处理工作流/妊娠系统.md` | 修改 | §15.1 剂量公式行与示例更新 |
| `update.log` | 修改 | "调整"条目一条 |

**未改动**：`data/csv/Item.csv` 及 ArkEditor 副本（描述本就写"剩余…30%"，修正后才吻合）；`gift_panel.py` 全部分支与选卵交互；面板显示；`game_type.py`/`save_handle.py`（存档结构与回填不变）；常量三重值 270/250/260 与 265 本身不变。

## 9. 不在本 Plan 范围

- 90/260/265/270/250 各基础数值本身的调整。
- 加速药提示文案、道具价格/等级、送礼口上文本的任何变化。

## 10. 执行记录（2026-08-28）

### 10.1 实际改动

§8 清单逐文件核对，全部按计划落地，无遗漏文件、无计划外文件：

| 文件 | 实际落点 |
| --- | --- |
| `Script/System/Pregnancy_System/pregnancy_handle.py` | `get_acceleration_amount` 增加 `total_day: int = PREGNANCY_TOTAL_DAY` 参数、A 项改 `(total_day - effective_day) * 0.3`、docstring 更新；`PREGNANCY_TOTAL_DAY` docstring 改为"妊娠加速药剂量公式的基数" |
| `Script/System/Pregnancy_System/egg_handle.py` | `get_egg_acceleration_amount` 调用处第 4 参传 `HATCH_TOTAL_DAY`（=265）、docstring 更新 |
| `.github/prompts/数据处理工作流/妊娠系统.md` | §15.1 剂量公式行改为新公式（基数胎生 270 / 卵 265）与新示例 |
| `update.log` | v0.66 块"调整"段末追加一条（体例自检通过，CRLF 无破坏，diff 仅 +1 行） |

### 10.2 与计划的偏差

无。

### 10.3 测试结果

- 无头单元测试 **25 项全部通过**（模式 A 自建 fixture，脚本在会话 scratchpad 中运行后即弃，不入库），覆盖 §6.1 全部条目：用户示例复算（63.0 / 44.1）、回归锚点 81.0、C 项 259/264 封顶序列、B 项 250 封顶与封顶后 `is_drug_effective` 拦截、卵基数 265（49.5 / 64.5）、旧存档卵缺键兜底、`get_accelerable_hatching_eggs` 过滤、`handle_drug_use_effect` 35/36 全链（入账、`gift_egg_id` 消费重置、卵不存在兜底不崩溃、其余卵不受影响）。
- §6.2 游戏内整体测试由用户执行。
