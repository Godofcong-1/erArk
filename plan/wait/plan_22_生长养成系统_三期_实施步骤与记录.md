# Plan 22（三期·实施步骤与记录）：养成事件系统

> ⚠️ **本期建成的养成事件系统已由 Plan 23「公务事件系统」接管并泛化**（`plan/wait/plan_23_公务事件系统_方案.md`）：
> 模块迁到 `Script/System/Official_Event_System/`、数据目录改为 `data/official_event/`、队列改名 `official_event_queue`，
> 养成事件成为「教育区」这一个部门分类。本文件中事件相关的落点以 Plan 23 为准，此处不再更新。

> 本文件是 `plan_22_生长养成系统_三期_方案.md`（下文简称"方案"）的**实施步骤清单与过程记录**。
> 需求背景、现状调查、设计决策、界面设计、风险与范围外事项以方案与
> `plan_22_生长养成系统_总纲.md`（下文简称"总纲"）为准；
> **角色字段定义以 `plan_22_生长养成系统_一期_方案.md` §4 为准**（下文简称"一期方案"）。
> 本文件只写"怎么做、怎么验、怎么回滚"，实施过程与结果记入 §6。

- 状态：**已实施**（2026-09-07，与方案、总纲保持同步）
- 适用代码快照：`plan22-growth-system @ 899b5b93a`
- **前置**：一期必须先完成（`event_history` / `personality_point` / `attend_class_count` 由一期建立并回填，大礼堂由一期改建）；与二期相互独立，唯一例外是毕业典礼事件依赖二期的成年结算入口
- 实施前提：先通读总纲 §2、一期方案 §4 与本方案；实施中发现与方案冲突的事实，**先更新方案再动代码**
- ⚠️ **实施前先确认**：ArkEditor 的事件数据格式能否扩展出"养成事件"分类（总纲 §6-5）。不能则退回手写 CSV，不阻塞本期。
  → 已确认**不能低成本扩展**，走退路手写 CSV，详见 §6.2 假设 5。

---

## 1. 改动文件清单

| 文件 | 类型 | 改动 |
| --- | --- | --- |
| `data/growth_event/婴儿.csv` | 新增 | 婴儿期养成事件，列结构见方案 §4.1 |
| `data/growth_event/幼女.csv` | 新增 | 幼女期养成事件 |
| `data/growth_event/萝莉.csv` | 新增 | 萝莉期养成事件 |
| `data/growth_event/通用.csv` | 新增 | 跨阶段事件（含毕业典礼、成年纪念、孩子间互动） |
| `buildconfig.py` | 改 | 新增 `data/growth_event/*.csv` → `data/Growth_Event.json` 的编译分支，照烹饪题库的合并分支写 |
| `auto_build_config.py` | 改 | ⚠️ 同样的编译分支要镜像一份，否则改完 CSV 直接跑 `game.py` 不会重建养成事件表 |
| `Script/Config/config_def.py` | 生成 | 由 `buildconfig.py` 重生成，含 `Growth_Event` 类 |
| `Script/Config/game_config.py` | 改 | 加载 `Growth_Event.json` 到运行时 config |
| `Script/Core/game_type.py` | 改 | `Rhodes_Island` 加 `growth_event_queue`（方案 §4） |
| `Script/Core/save_handle.py` | 改 | `growth_event_queue` 的 `hasattr` 回填为 `[]` |
| `Script/System/Education_System/growth_event_handle.py` | 新增 | 每日筛选与入队（含节流与幂等）、出队、选项结算 |
| `Script/System/Education_System/growth_event_panel.py` | 新增 | 事件弹出与决断界面（方案 §5.1） |
| `Script/System/Education_System/growth_panel.py` | 改 | 养成总览加"事件履历"一栏（方案 §5.2） |
| `Script/Settle/past_day_settle.py` | 改 | 每日结算时调 `growth_event_handle` 的入队 |
| `Script/System/Instruct_System/handle_instruct.py` | 改 | `handle_official_work` 里插入养成事件段（指令 2001） |
| `Script/Design/handle_premise/__init__.py` | 改 | CVP 加 `Growth` 子类型（方案 §3.7.1）；顺带修掉 G 分支的 `final_value` 覆写 BUG |
| `Script/Design/handle_premise/handle_premise_other.py` | 改 | 两个新前提 `self_have_sibling_child` / `self_have_classmate` |
| `Script/Core/constant_promise.py` | 改 | 上述两个前提的常量 |
| `Script/Design/settle_behavior.py` | 改 | CVE 加 `Growth` 子类型 |
| `Script/System/Pregnancy_System/pregnancy_handle.py` | 改 | `check_grow_to_girl` 里插毕业典礼与成年纪念 |
| `tools/ArkEditor/csv/Premise.csv` | 改 | 同步两个新前提（养成事件本体不进编辑器，见 §6.2 假设 5） |

---

## 2. 详细改动步骤

> ⚠️ 事件 uid 由文件名前缀自动生成（照口上 cid 的机制），不手工分配，形如 `萝莉1`、`通用1`。

### 2.1 编译链（先跑通空表）

1. 建 `data/growth_event/` 四个 CSV，只写表头 5 行与列定义（方案 §4.1），**先不写事件条目**
2. `buildconfig.py` 与 `auto_build_config.py` 各加一份编译分支，照**烹饪题库**（`data/csv/cook_question/`）的多文件合并分支写；cid 加文件名前缀照口上
3. 跑 `buildconfig.py`，确认生成 `data/Growth_Event.json` 与 `config_def.py` 的 `Growth_Event` 类
4. `game_config.py` 加载到运行时 config（存**原始 dict** 而非 config 对象，见方案 §4.1）

⚠️ **先跑通空表再写内容**：编译分支写错会让整个构建失败，而构建失败时游戏起不来、很难定位是哪一行 CSV 的问题。空表跑通后再灌数据。

### 2.2 队列与存档

1. `game_type.py` 的 `Rhodes_Island` 加 `growth_event_queue`（方案 §4 的代码块即最终定义）
2. `save_handle.py` 的罗德岛旧档兼容段（紧接 `child_schedule_template` 之后）加 `hasattr` 回填为 `[]`

### 2.3 入队逻辑（含节流与幂等）

新建 `Script/System/Education_System/growth_event_handle.py`：

1. 每日结算时遍历所有持有素质 101~104 的角色
2. 按 `stage` 与 `premise` 筛出该孩子当前可触发的事件
3. ⚠️ `once == 1` 的事件**入队前查该孩子的 `event_history`**，已触发过则跳过（方案 §7-2）
4. 把所有孩子的候选汇成一个池子，按 `weight` 加权随机取 **2** 条入队（方案 §7-1 的节流，⚠️ 这是全局上限不是每孩上限，所以要先汇总再抽）
5. 在 `Script/Settle/past_day_settle.py` 的每日结算里调用

### 2.4 出队与决断

1. 处理公务（指令 2001）流程中插入养成事件段
2. ⚠️ 弹出前校验 `chara_id in cache.character_data`，无效则静默丢弃出队（方案 §7-4）
3. 选项按 `option_N_premise` 判定：不满足则**置灰并显示原因**，不隐藏、不报错（口径 34）
4. 玩家选定后按 `option_N_effect` 结算（复用 CVE token），并写入该孩子的 `event_history`（一次性与否都写：前者靠它防重复，后者靠它给履历栏供料）
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

1. 兄弟姐妹关系直接读既有 `relationship` 的 `father_id` / `mother_id`（⚠️ 未登记时是 -1，要排除，见 §6.2 假设 6）
2. 同班同学关系由课表反查：同一格子的学生互为同学
3. 互动全部通过 `通用.csv` 的事件呈现，事件 effect 同时影响两个孩子
4. ⚠️ **不给 NPC AI 加"以另一个 NPC 为目标"的行为链**（口径 36）

### 2.7 毕业典礼（依赖二期）

在二期的 `check_grow_to_girl` 成年结算里调 `push_graduation_event()`，把 `通用1`（毕业典礼）与 `通用2`（成年纪念）插到队列最前，玩家下次处理公务时举行；舞台为一期改建出的大礼堂（`Auditorium`）。同时在成年结算的输出文本里加一行预告。

⚠️ **不在成年结算当场弹出**：那里跑在 NPC 行为循环里，当场弹多选界面会卡住循环（方案 §3.26）。

⚠️ **二期未完成时本步跳过**，其余五步可正常推进（方案 §6）。

---

## 3. 构建与缓存

```bash
.conda\python.exe buildconfig.py   # ⚠️ 本期新增了 CSV → JSON 的编译分支，必跑
git checkout -- data/po/           # ⚠️ 本机没有 xgettext/polib，buildconfig 重写的 PO 要还原
.conda\python.exe buildpo.py       # 事件文本需要翻译词条（需有工具链的环境，本次未跑）
.conda\python.exe buildmo.py
```

本期**不涉及地图改动**，不需要删场景缓存。

⚠️ `data/Growth_Event.json` 与 `data/data.json` 一样是**未纳入版本管理的构建产物**，clone 后首次跑 `game.py` 会由 `auto_build_config.py` 生成。

---

## 4. 验证清单

### 4.1 单元测试（实施方执行，按 `headless-game-test` 模式 A）

全部通过，结果与断言分组见 §6.3。

- [x] 编译链：空表也能正常生成 `data/Growth_Event.json`，`buildconfig.py` 退出码为 0
- [x] **入队节流**：构造 5 个孩子、每人 10 条可触发事件，跑一次每日结算，断言队列增量 ≤ 2
- [x] **一次性事件幂等**：`once == 1` 的事件处理过一次后写入 `event_history`，再跑入队断言不再进队列
- [x] 非一次性事件可重复入队
- [x] 前提筛选：`stage` 为 102 的事件不会派给萝莉（103）
- [x] 选项前提：不满足时返回置灰标记与原因文本，而非抛异常或隐藏
- [x] 选项结算：选中后 `personality_point` 对应项按预期增减，`event_history` 写入 uid 与 choice
- [x] **无效角色出队**：队列中 `chara_id` 不在 `cache.character_data` 时静默丢弃，不抛 KeyError
- [x] 旧档载入：缺 `growth_event_queue` 时 `hasattr` 回填为 `[]`，不抛异常
- [x] （追加）`Growth` 子类型在 CVP / CVE 两侧都能读写，且没有误伤同以 G 开头的攻略程度与礼物前提
- [x] （追加）兄弟姐妹与同班同学的反查，以及 `A2` 结算落到互动对象身上
- [x] （追加）毕业典礼与成年纪念插到队首

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
| 编译链 | revert `buildconfig.py` + `auto_build_config.py` + `game_config.py` 的改动，删 `data/growth_event/` 与 `data/Growth_Event.json` | ⚠️ 要同步 revert `config_def.py`（生成物） |
| 队列与存档 | revert `game_type.py` + `save_handle.py` | 旧档因 `hasattr` 回填天然兼容 |
| 入队与出队逻辑 | 删两个新文件 + 摘掉公务入口、`past_day_settle.py` 与 `pregnancy_handle.py` 的调用 | 无外部依赖 |
| `Growth` 子类型 | revert `handle_premise/__init__.py` + `settle_behavior.py` 的 Growth 分支 | ⚠️ `handle_premise/__init__.py` 里那处 `else:` 是**既有 BUG 的修复**，不要跟着 revert（见 §6.1 偏离 10） |
| 毕业典礼 | 删 `通用.csv` 里的对应行 | 独立于其余事件 |

⚠️ 本期**没有不可回滚的部分**。「清空 CSV 数据行」这一档特别有用：系统本身出问题时可以先让它安静下来，不必回滚整套代码。

---

## 6. 实施过程记录

### 6.1 实际改动

| 文件 | 类型 | 实际改动 |
| --- | --- | --- |
| `data/growth_event/{婴儿,幼女,萝莉,通用}.csv` | 新增 | 26 列的事件表，共 18 条事件（4/4/5/5） |
| `buildconfig.py` | 改 | `growth_event` 编译分支：合并四个 CSV 为 `Growth_Event` 表、cid 加文件名前缀、文本进 event 的 PO、空表也写出 JSON |
| `auto_build_config.py` | 改 | 同上镜像一份 |
| `Script/Config/config_def.py` | 生成 | 新增 `Growth_Event` 类（26 个字段） |
| `Script/Config/game_config.py` | 改 | `growth_event_path` / `growth_event_data` / `config_growth_event` / `config_growth_event_by_stage` + `load_growth_event()`，挂进 `init()` |
| `Script/Core/game_type.py` | 改 | `Rhodes_Island.growth_event_queue`（方案 §4） |
| `Script/Core/save_handle.py` | 改 | `growth_event_queue` 的 `hasattr` 回填为 `[]` |
| `Script/Core/constant_promise.py` | 改 | `SELF_HAVE_SIBLING_CHILD` / `SELF_HAVE_CLASSMATE` |
| `Script/Design/handle_premise/__init__.py` | 改 | CVP 的 `Growth` 子类型；G 分支的 `final_value` 覆写修复（见偏离 10） |
| `Script/Design/handle_premise/handle_premise_other.py` | 改 | 两个新前提的实现 |
| `Script/Design/settle_behavior.py` | 改 | CVE 的 `Growth` 子类型（浮点值，只写性格倾向与照料值） |
| `Script/System/Education_System/growth_handle.py` | 改 | 追加养成数值的统一读写口：`GROWTH_VALUE_*` / `get_growth_value` / `change_growth_value` / `set_growth_value` |
| `Script/System/Education_System/growth_event_handle.py` | 新增 | 入队（节流+幂等）、出队、清理无效项、选项判定与结算、兄弟姐妹与同学反查、毕业典礼入队 |
| `Script/System/Education_System/growth_event_panel.py` | 新增 | 事件弹出与决断界面（方案 §5.1） |
| `Script/System/Education_System/growth_panel.py` | 改 | 「养成履历」栏 + 「待处理」栏的待决断条数提示（方案 §5.2） |
| `Script/Settle/past_day_settle.py` | 改 | 每日结算末尾调 `check_new_day_growth_event()`（排在角色刷新之后） |
| `Script/System/Instruct_System/handle_instruct.py` | 改 | `handle_official_work` 在通用结算**之前**调 `handle_growth_event_queue(width)` |
| `Script/System/Pregnancy_System/pregnancy_handle.py` | 改 | `check_grow_to_girl` 里 `push_graduation_event()` + 一行提示文本 |
| `tools/ArkEditor/csv/Premise.csv` | 改 | 同步两个新前提 |

**与方案的偏离**（均已回写进方案正文）：

1. **`stage = 0` 的语义收窄**为"全部未成年阶段（101~103）"，并新增 `stage = 104` 供毕业典礼用。方案原文只写"0 通用"，照那样实现的话女儿成年后会一直被派"生日""换季"这类给孩子写的日常事件。
2. **列结构从 9 类扩到 11 类**：加了 `option_N_reason`（置灰原因）与 `option_N_tip`（后果提示）。口径 34 要求"标明原因"，但前提系统里没有任何"前提 → 人话"的说明表，只能作者手写；§5.1 的"倾向：坚强"提示同理，且要能独立翻译。
3. **性格倾向的写入不另造 token**，而是给 CVP/CVE 各加一个 `Growth` 子类型（方案 §3.7.1）。这样前提与结算共用既有分发链，作者也不用记第二套语法。
4. **队列元素加 `partner_id`**，判前提与跑结算时临时把孩子的 `target_character_id` 指向它，使 `A2` 指向本次事件的互动对象（方案 §3.25）。方案 §4 的队列结构里原本没有这一项，孩子间互动事件"effect 同时影响两个孩子"就落不了地。
5. **毕业典礼不在成年结算当场弹出**，改为插到队列最前 + 在成年结算文本里加一行预告。`check_grow_to_girl` 跑在 NPC 行为循环里，当场弹多选界面会把循环卡在中间。
6. **新增队列硬上限 12 条**（`GROWTH_EVENT_QUEUE_MAX`），方案只写了每日入队上限。玩家长期不处理公务时队列会无限堆积。
7. **每日入队上限定为 2 条**（方案写的是"1~2 条"），且明确是**全局**上限：先汇总所有孩子的候选再加权抽 2 条，而不是每个孩子各抽一条。
8. **事件段插在 `chara_handle_instruct_common_settle` 之前**。它的末尾会 `update.game_update_flow()` 推进行为循环并重绘主面板，放在其后弹出的事件会被盖掉。
9. **`auto_build_config.py` 也要改**，方案的文件清单只列了 `buildconfig.py`。不改的话改完 CSV 直接跑 `game.py` 不会重建养成事件表，而这正是方案 §1 目标 2「往 CSV 追加一行就能加事件」的日常工作流。
10. **顺手修了一个既有 BUG**：`handle_comprehensive_value_premise` 的 `G` 分支里，`Gift` 之后的 `final_value = get_character_fall_level(...)` 是无条件执行的（`Gift` 靠 return 提前退出才没暴露）。加 `Growth` 分支时若不把它改成 `else`，任何 `Growth` 前提读出的值都会被攻略程度覆盖掉——首轮单元测试里正是这 5 条断言先红的。
11. **ArkEditor 不扩展**（方案列为可选项），见 §6.2 假设 5。

**已知限制**：

1. **PO 词条未生成**：本机没有 `xgettext` / `polib`，`buildpo.py` / `buildmo.py` 跑不了，`buildconfig.py` 重写的 PO 已按惯例 `git checkout -- data/po/` 还原。18 条事件的中文原文在中文环境下直接显示无碍，但**其他语言的翻译词条需要用户在有工具链的环境里补跑一次**。
2. **CVP/CVE 菜单未加 `Growth` 选项**：ArkEditor 的 `ui/CVP_menu.py` / `ui/CVE_menu.py` 是硬编码的下拉列表，一期加的 `Course` / `CourseType` / `CourseShowOff` 也同样没进去，本期沿用这个现状。手写 token 仍然有效。
3. **旧存档里已成年的女儿会被补派毕业典礼**：她们的 `event_history` 是空的，日常入队路径会把 `通用1` / `通用2` 派给她们。这是有意保留的（追认一次典礼），不是 BUG。
4. **「萝莉化」世界设定下的同学判定**：该设定会给一大批干员挂上萝莉素质，若这些干员又选了课（口径 24 允许），就可能被当成孩子的"同学"。兄弟姐妹判定已按有效双亲 id 排除了这种情况，同学判定则是按课表算的、本身就说得通，故未排除。

### 6.2 实施前的假设复核

| # | 假设 | 复核结果 |
| --- | --- | --- |
| 1 | 一期已建好 `event_history` / `personality_point` / `attend_class_count` / `absent_count` 并做了存档回填 | ✅ 成立，`game_type.py:361` 的 `CHILD_GROWTH` 四个字段齐备，本期直接写入 |
| 2 | 一期已改建出大礼堂（`Auditorium` 场景标签） | ✅ 成立，`data/map/教/大礼堂/Scene.json` 的 `SceneTag` 为 `Auditorium` |
| 3 | `buildconfig.py` 的既有事件与口上编译分支可作为新分支的范式 | ⚠️ 部分成立。既有事件是 **JSON** 不是 CSV，不能照抄；真正的范式是**烹饪题库**（`data/csv/cook_question/` 多个 CSV 合并为一张 `Cook_Question` 表 + 独立 JSON），cid 加文件名前缀则照口上 |
| 4 | 指令 2001 `official_work` 的流程中有可插入的位置 | ✅ 成立。`handle_official_work` 只有一行通用结算，在其**之前**插入即可；已确认插入的代码不会干扰 `add_instruct` 对指令大类的源码推断（那段只认 `cache.now_panel_id` 与 `now_panel.draw()`） |
| 5 | ArkEditor 的事件格式能扩展出"养成事件"分类 | ❌ **不成立**。编辑器的数据模型硬绑 `behavior_id` + `adv_id` + 单条 premise/effect/text（`ui/data_list.py`），而养成事件一行带四个各自独立的选项块，要另起一整套 grid 布局与序列化。按方案的退路走手写 CSV，只同步了两个新前提到 `csv/Premise.csv` |
| 6 | 既有 `relationship.child_id_list` 可直接用于兄弟姐妹判定 | ⚠️ 改用 `father_id` / `mother_id` 比对。`child_id_list` 挂在父母身上、要先找到父母再回查，而按双亲 id 比对一步到位。⚠️ 双亲未登记时是 **-1** 不是 0，不排除掉的话两个都没登记的角色会互相认成兄弟姐妹 |

### 6.3 单元测试结果

`headless-game-test` 模式 A，**79 条断言全部通过**（首轮 73 通过 / 5 失败，全部指向偏离 10 的那个既有 BUG，修复后转绿）。基线回归：skill 自带的 `unit_test_template.py` 8 条断言仍全绿。

断言分组（scratchpad 会随会话丢失，这里留清单供下轮复现）：

| 组 | 条数 | 覆盖 |
| --- | --- | --- |
| A 编译链与配置 | 9 | `Growth_Event.json` 生成、运行时表非空、阶段分桶含 {0,101,102,103,104}、uid 带文件名前缀、毕业典礼与成年纪念 uid 存在、空选项列不残留空串、两个新前提已注册 |
| B `Growth` 前提与结算 token | 14 | `Growth\|0/1/2` 读出勤三值、无养成数据时出勤率按满勤、`Growth\|11` 正负值都能判、攻略程度前提未被误伤、CVE 写性格倾向正负与照料值、CVE 不允许改写出勤数 |
| C 入队节流 | 3 | 5 个孩子各 10 条候选，单日增量 ≤ 2 且 > 0；连跑 10 天后队列长度 ≤ 硬上限 |
| D 一次性幂等 | 7 | 处理前可入队、已在队列不重复、结算写 `event_history` 与 choice、处理后不再入队、非一次性事件仍可再入队 |
| E 阶段筛选 | 6 | 102 与 101 的事件不派给萝莉、101 的派给婴儿、通用事件派给萝莉但不派给少女、104 的只派给少女 |
| F 选项前提置灰 | 8 | 4 个选项全出、无前提的可选、好感/信赖不足的置灰、置灰项带原因且未被隐藏、满足后转为可选、每个选项都有后果提示 |
| G 选项结算的实际数值 | 5 | 选项1 好感升+倾向偏脆弱、选项2 好感小降+倾向偏坚强、**选错不掉能力**（口径 33） |
| H 兄弟姐妹与同学 | 11 | 反查命中/非同父同母不算/双亲未登记不互认/两个前提的真假/同格子互为同学/不同教室不算/事件挑出互动对象/`A2` 结算落在对方身上/结算后交互对象已还原 |
| I 无效队列项与旧档 | 4 | 角色不存在与事件已删两类无效项静默丢弃且不抛 KeyError、清理后只剩有效项、空队列返回 None、旧档回填为 `[]` |
| J 毕业典礼入队 | 3 | 毕业典礼在队首、成年纪念紧随、已有日常事件时仍插队首 |
| K 面板与履历 | 6 | 公务里的弹出流程可跑通、队列清空、写入履历、交互对象已还原、履历栏可绘制、缺 `time` 的旧记录不炸排序 |
| L 每日结算钩子 | 3 | 每日结算挂了入队、处理公务挂了弹出、且弹出排在通用结算之前 |

关键实测值：18 条事件（婴儿 4 / 幼女 4 / 萝莉 5 / 通用 5）；5 孩 × 10 候选的单日入队增量为 2；连跑 10 天后队列停在 12 条硬上限。

### 6.4 尚未覆盖的验证

以下要在真实游戏里跑（对应 §4.2）：

- [ ] Tk 模式下事件弹出的排版是否好读（正文换行、置灰项与按钮的对比）
- [ ] Web 模式（`web_draw = 1`）下的多选项交互
- [ ] 真实存档载入不报错，且旧档的养成总览能正常打开
- [ ] 养几个孩子连玩数天，确认一次公务不会涌出十几条
- [ ] 萝莉成年时的毕业典礼从预告到举行的完整观感
- [ ] 往 `data/growth_event/萝莉.csv` 追加一行后跑 `buildconfig.py`，游戏内能触发
- [ ] 18 条事件的文案本身是否合口味（数值尺度已按口径 33 压在"好感小幅升降 + 倾向"上）
- [ ] PO 词条在有 `xgettext`/`polib` 的环境里补跑 `buildpo.py` + `buildmo.py`

### 6.5 第二轮追加调整实施记录

（与方案 §9.x 成对，每轮一节，附回归测试计数）
