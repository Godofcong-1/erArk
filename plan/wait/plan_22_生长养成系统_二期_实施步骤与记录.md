# Plan 22（二期·实施步骤与记录）：日程模板 + 幼女跟随母亲 + 成年结算

> 本文件是 `plan_22_生长养成系统_二期_方案.md`（下文简称"方案"）的**实施步骤清单与过程记录**。
> 需求背景、现状调查、设计决策、界面设计、风险与范围外事项以方案与
> `plan_22_生长养成系统_总纲.md`（下文简称"总纲"）为准；
> **数据结构定义以 `plan_22_生长养成系统_一期_方案.md` §4 为准**（下文简称"一期方案"）。
> 本文件只写"怎么做、怎么验、怎么回滚"，实施过程与结果记入 §6。

- 状态：未实施（与方案、总纲保持同步）
- 适用代码快照：`master @ 6aa5090e3`
- **前置：一期必须先完成**——本期用到的四个字段由一期建立并做存档回填，且日程只在"没有课的时段"生效
- 实施前提：先通读总纲 §2、一期方案 §4 与本方案；实施中发现与方案冲突的事实，**先更新方案再动代码**

---

## 1. 改动文件清单

| 文件 | 类型 | 改动 |
| --- | --- | --- |
| `data/csv/Entertainment.csv` | 改 | 新增「跟随母亲」「自由玩耍」两行，`class_ok` 均配 0 |
| `data/csv/Behavior_Data.csv` | 改 | 新增 `follow_mother`（60 分钟，NPC 触发） |
| `data/csv/Behavior_Effect.csv` | 改 | `follow_mother` 的效果串（见学经验 + `care_point` + 母女好感亲密） |
| `data/csv/Behavior_Introduce.csv` | 改 | `follow_mother` 的介绍文本 |
| `Script/Core/constant/Behavior.py` | 改 | `FOLLOW_MOTHER` en_name 常量 |
| `Script/Core/constant/BehaviorStr.py` | 改 | 同上 |
| `Script/Core/constant/Behavior_Int.py` | 改 | `follow_mother` 的 cid |
| `Script/Core/constant/CharacterStatus.py` | 改 | 跟随母亲状态 cid |
| `Script/Core/constant_effect.py` | 改 | 见学结算的效果 id |
| `Script/Settle/past_day_settle.py` | 改 | 娱乐刷新**之后**改写孩子的 `entertainment_type`（⚠️ 时序，方案 §2.1） |
| `Script/Settle/default.py` | 改 | 见学结算实现（按母亲工作的 `ability_id` 加经验） |
| `Script/Design/handle_npc_ai.py` | 改 | 幼女未排课节次走跟随母亲；母亲无效时的回落链 |
| `Script/System/Pregnancy_System/pregnancy_handle.py:637` | 改 | `check_grow_to_girl` 内加性格选边与职业倾向提示；`chest_grow` / `body_part_grow` 接入 `care_point` |
| `Script/System/Education_System/schedule_template_handle.py` | 新增 | 日程模板读写、批量套用、单孩覆盖 |
| `Script/System/Education_System/schedule_template_panel.py` | 新增 | 日程模板面板（方案 §5.1） |
| `Script/System/Education_System/course_select_panel.py` | 改 | 个人课表面板加一行"日程模板：X [改]"（方案 §5.2） |
| `data/talk/daily/follow_mother.csv` | 新增 | 10 条（母亲有工作 / 无工作 2 档 × 5） |
| `tools/ArkEditor/csv/Behavior_Data.csv` | 改 | 新行为同步 |

⚠️ **不改 `game_type.py` 与 `save_handle.py`**：本期用到的四个字段已在一期建好并回填（一期方案 §4）。若实施时发现字段缺失，说明一期没按方案做全，**先补一期再继续**，不要在本期另建字段。

---

## 2. 详细改动步骤

> ⚠️ 全部 cid / 效果 id 不在此预分配，实施时现查空闲号。

### 2.1 CSV 与常量

1. `Entertainment.csv` 加「跟随母亲」「自由玩耍」两行；⚠️ `class_ok` 配 0，它们是日程活动不是兴趣课
2. `Behavior_Data.csv` / `Behavior_Effect.csv` / `Behavior_Introduce.csv` 加 `follow_mother`
3. 常量五处同步；`tools/ArkEditor/csv/Behavior_Data.csv` 同步
4. 跑 `buildconfig.py`

### 2.2 日程模板

1. 新建 `Script/System/Education_System/schedule_template_handle.py`：模板增删改查、批量套用、单孩覆盖的合并读取（`schedule_override` 优先于模板）
2. 初始化四套预设模板（方案 §3.6 的表），在新周目或首次进入面板时写入 `Rhodes_Island.child_schedule_template`
3. 新建 `schedule_template_panel.py`（方案 §5.1）；「批量套用」走既有的通用 NPC 选择面板
4. `course_select_panel.py` 加"日程模板：X [改]"一行（方案 §5.2）

### 2.3 日程执行链（⚠️ 时序硬约束）

改 `Script/Settle/past_day_settle.py`：

1. 找到既有的娱乐刷新调用点（`handle_npc_ai.py:788~841` 的刷新在此之后被消费）
2. **在刷新之后**插入孩子的 `entertainment_type` 改写，照 `egg_handle.replace_entertainment_for_eggs` 的挂点（方案 §2.2）
3. 改写规则：只覆盖该时段内**完全没有课**的情况；有课的时段跳过（方案 §3.6）

⚠️ 顺序颠倒是本期最容易犯的错，且症状是"日程时灵时不灵"，很难查。实施后用 §4.1 的第一条断言直接验。

### 2.4 幼女跟随母亲

1. `handle_npc_ai.py`：幼女（素质 102）+ 当前节次未排课 → 置 `follow_mother_flag`，走 `follow_mother` 行为
2. **回落链**：按方案 §3.24 的表逐条实现五种母亲无效情形
   - ⚠️ 母亲在 H / 监禁 / 无意识时**必须**回落育儿室，既有跟随链不判这个
3. `Script/Settle/default.py` 加见学结算：读母亲 `work.work_type` → `WorkType.csv` 的 `ability_id` → 基础值 6 × 速度系数（母亲该能力等级，走一期方案 §3.1 的曲线）
4. 母亲 `work_type == 0` 时不加见学经验，只加 `care_point` 与好感

### 2.5 成年结算

改 `Script/System/Pregnancy_System/pregnancy_handle.py:637 check_grow_to_girl`，在既有的 `chest_grow` / `body_part_grow` 调用附近插入：

1. 四对性格素质按 `personality_point` 符号选边写 `talent[271~278]`
2. ⚠️ `personality_point` 全为 0 时输出"性格尚未定型"，**不随机选边**
3. `chest_grow` / `body_part_grow` 接入 `care_point` 作为第二输入
4. 按能力最高的科目反查 `WorkType.csv` 的 `ability_id` 输出职业倾向提示（只提示，不自动任命）
5. 文本输出照既有 `check_grow_to_girl` 的 `WaitDraw` 模式

### 2.6 口上

`data/talk/daily/follow_mother.csv`，10 条（母亲有工作 / 无工作 2 档 × 5）。⚠️ 带 `self_is_player_daughter` 前提以命中 `talk.py:185~188` 的女儿 5 倍加权（一期方案 §3.23）。

---

## 3. 构建与缓存

```bash
.conda\python.exe buildconfig.py   # CSV / 常量改动后
.conda\python.exe buildpo.py
.conda\python.exe buildmo.py
```

本期**不涉及地图改动**，不需要删场景缓存。

---

## 4. 验证清单

### 4.1 单元测试（实施方执行，按 `headless-game-test` 模式 A）

- [ ] **日程改写时序**：构造一个孩子跑完一次跨天结算，断言 `entertainment_type` 是模板值而非随机值（这条直接验 §2.3 的时序）
- [ ] 有课的时段日程不生效：某时段排满课时，`entertainment_type` 该位保持不变
- [ ] `schedule_override` 优先于模板：同一时段模板与覆盖不同时，取覆盖值
- [ ] 批量套用：对 3 个孩子套用同一模板后，三者的 `schedule_template_id` 一致
- [ ] 见学经验：母亲为厨师（`ability_id` 43）时，幼女跟随后 43 号能力经验增加，增量 = 6 × 速度系数
- [ ] 母亲 `work_type == 0` 时不加见学经验，但 `care_point` 增加
- [ ] **回落链五条全覆盖**：`mother_id == -1` / 母亲 `dead` / 母亲在 H / 母亲在监禁 / 母亲在外勤，五种输入均回落育儿室且不抛异常
- [ ] 成年结算：`personality_point` 各项为正 / 为负 / 为 0 三种输入，断言写入的 `talent[271~278]` 组合与"性格尚未定型"分支
- [ ] 成年结算幂等：连续调用两次 `check_grow_to_girl`，第二次因 `talent[103] == 0` 不再执行

### 4.2 游戏内整体测试（由用户执行）

- [ ] 日程模板面板能新建、编辑、批量套用到多个孩子
- [ ] 单孩微调只影响该孩子，不影响模板与其他孩子
- [ ] 幼女在没课的时段会跟着母亲去她的工作岗位，并获得对应科目的经验
- [ ] 母亲在 H / 被监禁 / 外勤时，幼女不会跟过去，而是在育儿室玩耍
- [ ] 萝莉成年时出性格选边与职业倾向提示文本
- [ ] Web 模式（`web_draw = 1`）下日程模板面板表现一致
- [ ] 旧存档载入不报错

---

## 5. 回滚

| 单元 | 回滚方式 | 备注 |
| --- | --- | --- |
| 日程模板（面板 + handle） | 删除两个新文件 + 摘掉入口 | 字段留在存档里不影响载入 |
| 日程执行链 | revert `past_day_settle.py` 的改动 | 回到既有随机娱乐 |
| 幼女跟随母亲 | revert `handle_npc_ai.py` 与结算；删 `follow_mother` 行为 | 幼女回落为与萝莉同样的自由行动（即一期的状态） |
| 成年结算 | revert `pregnancy_handle.py` 的改动 | 回到只做发育判定 |
| 口上 | 删 `follow_mother.csv` 重跑 `buildconfig.py` | |

⚠️ 本期**没有不可回滚的部分**——所有改动都可独立 revert，且不涉及地图与存档结构。

---

## 6. 实施过程记录

（实施时填写）

### 6.1 实际改动

| 文件 | 类型 | 实际改动 |
| --- | --- | --- |
| | | |

**与方案的偏离**：

1. （逐条编号）

**已知限制**：

### 6.2 实施前的假设复核

| # | 假设 | 复核结果 |
| --- | --- | --- |
| 1 | 一期已建好 `schedule_template_id` / `schedule_override` / `follow_mother_flag` / `child_schedule_template` 四个字段并做了存档回填 | |
| 2 | `handle_npc_ai.py:788~841` 每日随机刷新 `entertainment_type` | |
| 3 | `egg_handle.replace_entertainment_for_eggs` 的挂点在娱乐刷新之后 | |
| 4 | `character_move.py:172~173` 会清 `sp_flag.is_follow` | |
| 5 | `check_grow_to_girl` 的守卫是 `handle_self_is_loli`，天然幂等 | |
| 6 | `WorkType.csv` 的 `ability_id` 列可直接作为见学科目 | |

### 6.3 单元测试结果

（断言计数与关键实测值）

### 6.4 尚未覆盖的验证

（留给用户的游戏内清单）

### 6.5 第二轮追加调整实施记录

（与方案 §9.x 成对，每轮一节，附回归测试计数）
