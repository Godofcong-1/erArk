# Plan 22（三期·实施步骤与记录）：养成事件系统

> 本文件是 `plan_22_生长养成系统_三期_方案.md`（下文简称"方案"）的**实施步骤清单与过程记录**。
> 需求背景、现状调查、设计决策、界面设计、风险与范围外事项以方案与
> `plan_22_生长养成系统_总纲.md`（下文简称"总纲"）为准；
> **角色字段定义以 `plan_22_生长养成系统_一期_方案.md` §4 为准**（下文简称"一期方案"）。
> 本文件只写"怎么做、怎么验、怎么回滚"，实施过程与结果记入 §6。

- 状态：未实施（与方案、总纲保持同步）
- 适用代码快照：`master @ 6aa5090e3`
- **前置**：一期必须先完成（`event_history` / `personality_point` / `attend_class_count` 由一期建立并回填，大礼堂由一期改建）；与二期相互独立，唯一例外是毕业典礼事件依赖二期的成年结算入口
- 实施前提：先通读总纲 §2、一期方案 §4 与本方案；实施中发现与方案冲突的事实，**先更新方案再动代码**
- ⚠️ **实施前先确认**：ArkEditor 的事件数据格式能否扩展出"养成事件"分类（总纲 §6-5）。不能则退回手写 CSV，不阻塞本期。

---

## 1. 改动文件清单

| 文件 | 类型 | 改动 |
| --- | --- | --- |
| `data/growth_event/婴儿.csv` | 新增 | 婴儿期养成事件，列结构见方案 §4.1 |
| `data/growth_event/幼女.csv` | 新增 | 幼女期养成事件 |
| `data/growth_event/萝莉.csv` | 新增 | 萝莉期养成事件 |
| `data/growth_event/通用.csv` | 新增 | 跨阶段事件（含毕业典礼、成年纪念、孩子间互动） |
| `buildconfig.py` | 改 | 新增 `data/growth_event/*.csv` → `data/Growth_Event.json` 的编译分支，照既有事件与口上的处理写 |
| `Script/Config/config_def.py` | 生成 | 由 `buildconfig.py` 重生成，含 `GrowthEvent` 类 |
| `Script/Config/game_config.py` | 改 | 加载 `Growth_Event.json` 到运行时 config |
| `Script/Core/game_type.py` | 改 | `Rhodes_Island` 加 `growth_event_queue`（方案 §4） |
| `Script/Core/save_handle.py` | 改 | `growth_event_queue` 的 `hasattr` 回填为 `[]` |
| `Script/System/Education_System/growth_event_handle.py` | 新增 | 每日筛选与入队（含节流与幂等）、出队、选项结算 |
| `Script/System/Education_System/growth_event_panel.py` | 新增 | 事件弹出与决断界面（方案 §5.1） |
| `Script/System/Education_System/growth_panel.py` | 改 | 养成总览加"事件履历"一栏（方案 §5.2） |
| `Script/Settle/past_day_settle.py` | 改 | 每日结算时调 `growth_event_handle` 的入队 |
| 处理公务入口 | 改 | 指令 2001 的流程中插入养成事件段（`Script/System/Instruct_System/` 或对应面板） |
| `tools/ArkEditor/` | 改（可选） | 养成事件的编辑支持 |

---

## 2. 详细改动步骤

> ⚠️ 事件 uid 由文件名前缀自动生成（照 `buildconfig.py:189~193` 的口上 cid 机制），不手工分配。

### 2.1 编译链（先跑通空表）

1. 建 `data/growth_event/` 四个 CSV，只写表头 5 行与列定义（方案 §4.1），**先不写事件条目**
2. `buildconfig.py` 加编译分支，照既有事件与口上的处理写
3. 跑 `buildconfig.py`，确认生成 `data/Growth_Event.json` 与 `config_def.py` 的 `GrowthEvent` 类
4. `game_config.py` 加载到运行时 config

⚠️ **先跑通空表再写内容**：编译分支写错会让整个构建失败，而构建失败时游戏起不来、很难定位是哪一行 CSV 的问题。空表跑通后再灌数据。

### 2.2 队列与存档

1. `game_type.py` 的 `Rhodes_Island` 加 `growth_event_queue`（方案 §4 的代码块即最终定义）
2. `save_handle.py:551` 附近加 `hasattr` 回填为 `[]`

### 2.3 入队逻辑（含节流与幂等）

新建 `Script/System/Education_System/growth_event_handle.py`：

1. 每日结算时遍历所有持有素质 101~104 的角色
2. 按 `stage` 与 `premise` 筛出该孩子当前可触发的事件
3. ⚠️ `once == 1` 的事件**入队前查该孩子的 `event_history`**，已触发过则跳过（方案 §7-2）
4. 按 `weight` 加权随机取 1~2 条入队（方案 §7-1 的节流，⚠️ 这是全局上限不是每孩上限）
5. 在 `Script/Settle/past_day_settle.py` 的每日结算里调用

### 2.4 出队与决断

1. 处理公务（指令 2001）流程中插入养成事件段
2. ⚠️ 弹出前校验 `chara_id in cache.character_data`，无效则静默丢弃出队（方案 §7-4）
3. 选项按 `option_N_premise` 判定：不满足则**置灰并显示原因**，不隐藏、不报错（口径 34）
4. 玩家选定后按 `option_N_effect` 结算（复用 CVE token），并写入该孩子的 `event_history`
5. 界面按方案 §5.1；⚠️ 只用 `Script/UI/Moudle/draw.py` 的抽象绘制类

### 2.5 事件内容编写

按阶段分文件批量写入。⚠️ 结果尺度遵循口径 33：**选错会导致性格偏向不如预期、好感小幅下降，但不掉能力、不造成不可逆损失**。

四个文件的内容分工：

| 文件 | 覆盖 |
| --- | --- |
| `婴儿.csv` | 夜哭、第一次翻身、认人、断奶 |
| `幼女.csv` | 第一次上课、跟着母亲闹脾气、和其他孩子抢玩具、怕生 |
| `萝莉.csv` | 成绩单、翘课被抓的后续、想学某科目、同学矛盾、青春期困惑 |
| `通用.csv` | 生日、季节事件、兄弟姐妹互动（方案 §3.25）、**毕业典礼与成年纪念**（方案 §3.26） |

### 2.6 孩子之间的互动（方案 §3.25）

1. 兄弟姐妹关系直接读既有 `relationship`（`game_type.py:366~370` 的 `child_id_list`）
2. 同班同学关系由课表反查：同一格子的学生互为同学
3. 互动全部通过 `通用.csv` 的事件呈现，事件 effect 同时影响两个孩子
4. ⚠️ **不给 NPC AI 加"以另一个 NPC 为目标"的行为链**（口径 36）

### 2.7 毕业典礼（依赖二期）

在二期的 `check_grow_to_girl` 成年结算之后触发 `通用.csv` 里的毕业典礼事件，舞台为一期改建出的大礼堂（`Auditorium`）。

⚠️ **二期未完成时本步跳过**，其余五步可正常推进（方案 §6）。

---

## 3. 构建与缓存

```bash
.conda\python.exe buildconfig.py   # ⚠️ 本期新增了 CSV → JSON 的编译分支，必跑
.conda\python.exe buildpo.py       # 事件文本需要翻译词条
.conda\python.exe buildmo.py
```

本期**不涉及地图改动**，不需要删场景缓存。

---

## 4. 验证清单

### 4.1 单元测试（实施方执行，按 `headless-game-test` 模式 A）

- [ ] 编译链：空表也能正常生成 `data/Growth_Event.json`，`buildconfig.py` 退出码为 0
- [ ] **入队节流**：构造 5 个孩子、每人 10 条可触发事件，跑一次每日结算，断言队列增量 ≤ 2
- [ ] **一次性事件幂等**：`once == 1` 的事件处理过一次后写入 `event_history`，再跑入队断言不再进队列
- [ ] 非一次性事件可重复入队
- [ ] 前提筛选：`stage` 为 102 的事件不会派给萝莉（103）
- [ ] 选项前提：不满足时返回置灰标记与原因文本，而非抛异常或隐藏
- [ ] 选项结算：选中后 `personality_point` 对应项按预期增减，`event_history` 写入 uid 与 choice
- [ ] **无效角色出队**：队列中 `chara_id` 不在 `cache.character_data` 时静默丢弃，不抛 KeyError
- [ ] 旧档载入：缺 `growth_event_queue` 时 `hasattr` 回填为 `[]`，不抛异常

### 4.2 游戏内整体测试（由用户执行）

- [ ] 在博士办公室处理公务时，养成事件会逐条弹出
- [ ] 事件选项的后果提示可读（写方向不写数值），不满足前提的选项置灰并显示原因
- [ ] 选完后性格倾向确实变化，可在养成总览的事件履历里看到本次选择
- [ ] 一次公务不会涌出十几条事件（多养几个孩子验证节流）
- [ ] 往 `data/growth_event/萝莉.csv` 追加一行新事件，跑 `buildconfig.py` 后游戏内能触发（验证"批量增删改查"）
- [ ] 萝莉成年时在大礼堂触发毕业典礼（需二期已完成）
- [ ] Web 模式（`web_draw = 1`）下事件弹出与选项交互表现一致
- [ ] 旧存档载入不报错

---

## 5. 回滚

| 单元 | 回滚方式 | 备注 |
| --- | --- | --- |
| 事件内容 | 清空四个 CSV 的数据行（保留表头）重跑 `buildconfig.py` | 系统还在但不再触发任何事件，可作为出问题时的紧急降级 |
| 编译链 | revert `buildconfig.py` + `game_config.py` 的改动，删 `data/growth_event/` | ⚠️ 要同步 revert `config_def.py`（生成物） |
| 队列与存档 | revert `game_type.py` + `save_handle.py` | 旧档因 `hasattr` 回填天然兼容 |
| 入队与出队逻辑 | 删两个新文件 + 摘掉公务入口与 `past_day_settle.py` 的调用 | 无外部依赖 |
| 毕业典礼 | 删 `通用.csv` 里的对应行 | 独立于其余事件 |

⚠️ 本期**没有不可回滚的部分**。「清空 CSV 数据行」这一档特别有用：系统本身出问题时可以先让它安静下来，不必回滚整套代码。

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
| 1 | 一期已建好 `event_history` / `personality_point` / `attend_class_count` / `absent_count` 并做了存档回填 | |
| 2 | 一期已改建出大礼堂（`Auditorium` 场景标签） | |
| 3 | `buildconfig.py` 的既有事件与口上编译分支可作为新分支的范式 | |
| 4 | 指令 2001 `official_work` 的流程中有可插入的位置 | |
| 5 | ArkEditor 的事件格式能扩展出"养成事件"分类 | |
| 6 | 既有 `relationship.child_id_list` 可直接用于兄弟姐妹判定 | |

### 6.3 单元测试结果

（断言计数与关键实测值）

### 6.4 尚未覆盖的验证

（留给用户的游戏内清单）

### 6.5 第二轮追加调整实施记录

（与方案 §9.x 成对，每轮一节，附回归测试计数）
