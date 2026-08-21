# Plan 07：助理同居时改为在博士房间完成全套洗澡行动链

- 状态：**已实施**（v3，2026-08-21，见 §10）
- 来源：新 todo → “助理洗澡可以在博士房间内洗澡”
- 补充需求：当前角色统一在大浴场洗澡；若助理开启同居服务，则不再去大浴场，改为在博士房间完成脱衣服、洗澡、换浴巾全套行动链，衣服次日起床时才穿回。
- 预计改动量：7 个文件（2 个 CSV + 5 个 Python）
- 风险等级：中低（涉及 NPC AI 目标链、移动与衣物结算）
- 适用代码快照：`master @ b88b1d3ca`（v0.66）
- 修订记录：
  - v2 —— 推翻 v1 的「给行为 805 追加效果 301」方案（详见 §9）。
  - **v3 —— 推翻 v2 的「洗完当场穿回衣服」方案**，改为与普通角色完全一致：保持浴巾到就寝、睡觉换睡衣、次日起床穿回。同时确认**不需要独立的博士房间衣柜**（详见 §11）。

---

## 1. 目标

1. 开启同居服务的当前助理，在淋浴时间不再进入大浴场洗澡链。
2. 为该助理新增一条独立洗澡行动链，所有步骤都在博士房间（`SceneTag` 含 `Dr_room` 的场景）完成：
   - 进入要脱衣服状态
   - 若不在博士房间，先去博士房间
   - 脱衣服
   - 淋浴
   - 换上浴巾/浴帽（**行动链到此自然结束**）
3. 洗完后不立刻穿回衣服，衣服留在衣柜里，**次日起床时才穿回**——处理流程与普通角色洗澡完全一致。
4. 玩家可以在博士房间用「检查衣柜」查看助理存放的衣服。
5. 普通干员洗澡流程保持不变。
6. 已开启“禁止一切洗澡”身体管理时，该助理同样不能进入此洗澡链。

## 2. 现状调查

### 2.1 现有 NPC 普通洗澡链

| cid | type | 前提 | 状态机 | 说明 |
| ---: | ---: | --- | ---: | --- |
| 51 | 11 | `normal_1267\|shower_time\|shower_flag_0\|not_ask_not_take_bath` | 71 START_SHOWER | 进入要脱衣服状态 |
| 52 | 12 | `shower_flag_1\|not_in_bathzone_locker_room` | 601 | 去大浴场更衣室 |
| 53 | 12 | `shower_flag_1\|in_bathzone_locker_room` | 72 WEAR_TO_LOCKER | 脱成全裸 |
| 54 | 12 | `shower_flag_2\|not_in_bathroom` | 515 | 去淋浴间 |
| 55 | 12 | `shower_flag_2\|in_bathroom` | 73 TAKE_SHOWER | 开始淋浴 |
| 56 | 12 | `shower_flag_3\|not_in_bathzone_locker_room` | 601 | 回更衣室 |
| 57 | 12 | `shower_flag_3\|in_bathzone_locker_room` | 74 GET_SHOWER_CLOTH_AND_CLEAN_LOCKER | 换上浴巾 |
| 58 | 0 | `normal_1267\|sleep_h_awake_1\|shower_flag_0\|not_ask_not_take_bath` | 71 | 睡奸醒来后的洗澡入口 |

洗澡状态由 `character_data.sp_flag.shower` 1~4 驱动（71→1，效果 303→2，304→3，305→4，`sleep` 的 301→0）。

### 2.2 普通角色「洗完澡→过夜→次日穿回」的完整链条（v3 要对齐的目标）

1. **围浴巾**（行为 802 `put_shower_cloth` = `305 - 633 - 647`）：`shower=4`，身上只剩 51/551/851，衣服由 647 从大浴场衣柜转进宿舍衣柜。
2. **穿着浴巾活动**到就寝时间（cid 23 `sleep_time|shower_flag_4` 才让她去睡觉）。
3. **睡觉**（行为 111 `sleep`，效果串含 `634 GET_SLEEP_CLOTH` / `301 SHOWER_FLAG_TO_0` / `648`）：脱掉浴巾换睡衣，`shower` 归零。
4. **次日起床**（cid 28 → 状态机 93 → 行为 113 `get_up`，效果含 `649 GET_CLOTH_FROM_DORMITORY_LOCKER`）→ `clothing.get_cloth_from_dormitory_locker()` 从宿舍衣柜穿回。

所以「保持浴巾」实际只持续到就寝，睡觉会自动换睡衣。这是既有行为，助理直接复用。

### 2.3 关键发现：同居助理的宿舍地址已经是博士房间

`Script/UI/Panel/assistant_panel.py:353-361` 在开启同居服务时：

```python
if target_data.assistant_services[service_cid] == 1:
    target_data.pre_dormitory = target_data.dormitory
    target_data.dormitory = map_handle.get_map_system_path_str_for_list(["中枢", "博士房间"])
```

而 `in_dor` 前提（`handle_premise_place.py:1492-1511`）是**拿位置和 `dormitory` 字段做字符串比较**，不是查 `Dormitory` SceneTag。

于是整条就寝/起床链对她**自动成立**：cid 25「不在宿舍则回宿舍」把她送回博士房间、cid 26「在宿舍则睡觉」、cid 28「起床」照常触发。

**推论：她的「宿舍衣柜」实际上就是博士房间的衣柜，不需要新增独立数据。** 详见 §11。

### 2.4 助理同居前提

- `is_assistant`（`handle_premise_assistant.py:29`）
- `assistant_live_together_on`（`handle_premise_assistant.py:424`）
- `in_dr_room`（`handle_premise_place.py:1428`）
- `sleep_h_awake_1` / `not_ask_not_take_bath`

`data/map/中枢/博士房间/Scene.json` 的 `SceneTag` 为 `Dr_room|Toilet_Male|Bathroom`——**既没有 `Dormitory` 也没有 `Locker_Room`**，这一点对 UI 分支很关键（§3.6）。

助理进博士房间没有权限问题：`map_handle.py:645`（锁门放行）与 `map_handle.py:674`（私密放行）都对当前助理开了口子。

### 2.5 AI 检索机制（决定设计的三条硬约束）

1. **type 12（需求链）有门禁**：`handle_npc_ai.py:313` 是 `if judge == 0 and not handle_premise.handle_normal_1(character_id)`，而 `handle_normal_1` 洗澡相关只判 `handle_shower_flag_123`，**不含 shower == 4**。
   → `shower_flag_4` 时 type 12 根本不会被检索。v3 的链在 `shower_flag_3 → 围浴巾` 后结束，正好不受影响。
   （附带结论：现有 cid 59 在常规路径下不可达，属既有历史问题，本 Plan 不处理。）
2. **type 11 / 12 / 13 都用 `get_first_only=True`**（`handle_npc_ai.py:565`），取 CSV 行序里第一个前提全通过的目标；`config_target_type_index` 按 CSV 行序 append（`game_config.py:1497`）。
3. **助理会被跟随机制拖出博士房间**：`judge_same_position_npc_follow()`（`handle_npc_ai.py:722`）在 `is_follow == 1` 时直接把 NPC 拽着跟玩家走，而入口前提 `normal_1267` 明确允许 AI 跟随状态。
   → 助理专用链必须对 flag1/2/3 做**全覆盖**（在/不在博士房间都有行接管），并且普通链 52~57 必须加**显式互斥前提**。

仓库既有约定也是显式互斥而非行序：撒尿链 cid 67 给普通行加了复合前提 `not_is_assistant_and_in_dr_room`（`handle_premise/__init__.py:1560`）。

### 2.6 缺少的零件

- 没有 `not_in_dr_room` 前提。
- 没有 `not_is_assistant_live_together` 互斥前提。
- 没有“移动到博士房间”的状态机；现有 571 只去博士办公室。
- 效果 647 被 v2 加了早退守卫，v3 需要**移除**它（见 §3.5）。
- 「检查衣柜」指令的前提不含博士房间，且面板在博士房间会崩溃（见 §3.6）。

## 3. 设计决策

### 3.1 复用现有 `sp_flag.shower` 四阶段

不新增洗澡 flag，直接复用 `shower 1~4`，避免改动前提、UI 状态显示与存档。

### 3.2 行动链在「围上浴巾」结束，不设收尾行

v2 曾用 `shower_cloth`（浴巾在不在）作为终止条件、在 type 11 加一条「脱浴巾穿回衣服」的收尾行。v3 废弃该设计：

- 需求明确要求「和正常角色一样」，而正常角色洗完就保持浴巾到就寝；
- 收尾行本身还有隐患：它排在 type 11 里必须抢在就寝入口 cid 23 之前，位置稍有偏差就失效。

因此**删除收尾行**，`shower` 保持 4，由睡觉时的效果 301 归零。

### 3.3 新增“博士房间”移动状态机

- `StateMachine` 常量新增 `MOVE_TO_DR_ROOM = 572`（571 与 581 之间空号）。
- `Script/StateMachine/default.py` 仿照 `character_move_to_dr_office()` 新增 `character_move_to_dr_room()`，用 `general_movement_module` + `constant.place_data["Dr_room"]`。

### 3.4 新增三个前提

```python
NOT_IN_DR_ROOM = "not_in_dr_room"                                   # 地点_定位 不在博士房间
NOT_IS_ASSISTANT_LIVE_TOGETHER = "not_is_assistant_live_together"   # 属性_助理 不是同居中的助理
IN_LOCKER_ROOM_OR_DORMITORY_OR_DR_ROOM = "in_locker_room_or_dormitory_or_dr_room"  # 地点_定位 在更衣室或宿舍或博士房间
```

- `not_in_dr_room` / `in_locker_room_or_dormitory_or_dr_room` 放 `handle_premise_place.py`。
- `not_is_assistant_live_together` 放 `handle_premise_assistant.py`，写成复合判定。
  **不要用现成的 `assistant_live_together_off`**：它只看 `assistant_services[7]`，卸任助理若残留该字段会被误排除出普通洗澡链，导致该干员永远不洗澡。

### 3.5 移除 v2 加的 647 早退守卫

v2 为了让助理「当场穿回」，在 `handle_shower_locker_to_dormitory_locker`（效果 647）里加了早退：同居助理在博士房间时不把衣服转进宿舍衣柜。

v3 **删掉这个守卫**。因为她的宿舍地址就是博士房间，647 把衣服从大浴场衣柜转进宿舍衣柜，正是「衣服放进博士房间的衣柜」；次日 649 从同一个衣柜穿回。整条链与普通角色逐字一致。

### 3.6 「检查衣柜」放开到博士房间

- **指令前提**：`data/csv/InstructConfig.csv:183` 的 `5040,check_locker` 前提从 `IN_LOCKER_ROOM_OR_DORMITORY` 改为 `IN_LOCKER_ROOM_OR_DORMITORY_OR_DR_ROOM`。
- **面板地点分支**：`check_locker_panel.py` 的 `draw()` 把博士房间并入**宿舍分支**（`if "Dormitory" in scene_tag or "Dr_room" in scene_tag`）。该分支按 `character_data.dormitory == map_path_str` 过滤，而同居助理的 `dormitory` 正是博士房间，天然匹配。
- **修复既有崩溃隐患**：面板里有 6 处重复的衣柜选择 `if/elif`，其中 `FindDraw.__init__` 与 `Ejaculation_NameDraw.__init__` 两处**只有 `if/elif` 没有 `else`**，另两处用 `else` 兜底到宿舍衣柜。博士房间两个 tag 都不含，**一旦允许在博士房间开面板，前者会 AttributeError**。
  处理：在 `clothing.py` 新增衣柜路由 helper，6 处统一改用它。

### 3.7 新的助理洗澡目标链

编号占用文件末尾的 900 号段（cid 901~908）：

```csv
901,71,normal_1267|shower_time|shower_flag_0|is_assistant|assistant_live_together_on|not_ask_not_take_bath,11,淋浴时间入口
902,572,shower_flag_1|is_assistant|assistant_live_together_on|not_in_dr_room,12,不在博士房间则去博士房间
903,72,shower_flag_1|is_assistant|assistant_live_together_on|in_dr_room,12,在博士房间则脱成全裸
904,572,shower_flag_2|is_assistant|assistant_live_together_on|not_in_dr_room,12,回博士房间
905,73,shower_flag_2|is_assistant|assistant_live_together_on|in_dr_room,12,开始淋浴
906,572,shower_flag_3|is_assistant|assistant_live_together_on|not_in_dr_room,12,回博士房间
907,74,shower_flag_3|is_assistant|assistant_live_together_on|in_dr_room,12,围上浴巾
908,71,normal_1267|sleep_h_awake_1|shower_flag_0|is_assistant|assistant_live_together_on|not_ask_not_take_bath,0,睡奸醒来入口
```

flag1/2/3 各配一对「不在→回博士房间」「在→执行」，做到全覆盖，助理被拖走后能自行走回来继续。

普通链 cid 51 / 52~57 / 58 全部追加 `|not_is_assistant_live_together`，做显式互斥，不依赖行序。

### 3.8 完整行动链

```
[20:00 淋浴时间] 901 → 状态机 71 → shower=1
   ├ 不在博士房间 → 902 → 572 移动
   └ 在博士房间   → 903 → 72 → 行为 804（303-642）→ shower=2，衣服进大浴场衣柜
   ├ 不在博士房间 → 904 → 572 移动
   └ 在博士房间   → 905 → 73 → 行为 112（…304…）→ shower=3，污浊清零
   ├ 不在博士房间 → 906 → 572 移动
   └ 在博士房间   → 907 → 74 → 行为 802（305-633-647）→ shower=4，围浴巾，
                                衣服由 647 转进宿舍衣柜（= 博士房间的衣柜）
[行动链结束，保持浴巾]
[就寝时间] cid 23（shower_flag_4）→ 78 → 25/26 回博士房间睡觉
           → 行为 111 的 634 换睡衣、301 让 shower=0
[次日起床] cid 28（in_dor 成立）→ 93 → 行为 113 的 649 → 从衣柜穿回原衣服
```

### 3.9 不修改大浴场娱乐链

“禁止一切洗澡”只约束洗澡链，不涉及大浴场洗浴类娱乐（桑拿、泡脚、温泉等）。本 Plan 不处理同居助理的大浴场娱乐行为。

## 4. 改动文件清单

| 文件 | 改动 |
| --- | --- |
| `data/target/default/target.csv` | 新增 901~908；51/52~57/58 追加互斥前提 |
| `data/csv/InstructConfig.csv` | `5040,check_locker` 前提放开到博士房间 |
| `Script/Core/constant/StateMachine.py` | 新增 `MOVE_TO_DR_ROOM = 572` |
| `Script/StateMachine/default.py` | 新增 `character_move_to_dr_room()` |
| `Script/Core/constant_promise.py` | 新增 3 个前提常量 |
| `Script/Design/handle_premise/handle_premise_place.py` | 新增 `handle_not_in_dr_room()`、`handle_in_locker_room_or_dormitory_or_dr_room()` |
| `Script/Design/handle_premise/handle_premise_assistant.py` | 新增 `handle_not_is_assistant_live_together()` |
| `Script/Design/clothing.py` | 新增衣柜路由 helper（供面板收敛 6 处 if/elif） |
| `Script/Settle/default_cloth.py` | 移除 v2 的 647 早退守卫，补注释说明 |
| `Script/UI/Panel/check_locker_panel.py` | 博士房间归入宿舍分支；6 处衣柜选择统一走 helper，修复 2 处崩溃隐患 |

### 4.1 不需要修改的部分

- **不新增行为、状态机、结算效果、CharacterStatus**（除移动状态机 572 外）。
- **不新增衣柜数据字段**（详见 §11）。
- **不改 `GET_SLEEP_CLOTH`**——睡觉换睡衣正是「和普通角色一样」的一环。
- 不改 `data/csv/Behavior_Data.csv` / `Behavior_Effect.csv`。
- `sp_flag.shower` 数据结构、存档字段不需要修改，**旧存档零迁移**。

## 5. 构建与验证

```bash
.conda/python.exe buildconfig.py
.conda/python.exe init_data.py
```

改了 `target.csv` 与 `InstructConfig.csv`，必须重建。

验证要点见 §10.3 的实测记录。

## 6. 风险与注意事项

1. **收尾行不存在**：`shower_flag_4` 时 type 12 不会被检索（`normal_1` 为真），任何想在该状态生效的行都必须放 type 11。v3 不设此类行，因而不受影响。
2. **不要给行为 805 追加效果 301**：805 被泡脚链 cid 485 引用，追加后会清零全体干员的洗澡状态，引发重复洗澡与不睡觉。
3. **不要用 805/643 脱浴巾**：643 只 append 不清空，会出现“浴巾套衣服”。
4. **不要用 `assistant_live_together_off` 做互斥**：它只看 `assistant_services[7]`，卸任助理残留该字段会被误排除。
5. **CSV 物理行序**：`config_target_type_index` 按行序 append，`get_first_only` 取第一个通过的。本 Plan 靠显式互斥前提而非行序保证正确，但新增行仍应注意位置。
6. **博士房间会被登记为损坏设施**：行为 112 带效果 1751 `FACILITY_DAMAGE_CHECK`，按角色当前场景无差别登记。按“与其他洗浴场景一致”处理，不做特殊排除。
7. **`pre_dormitory` 与监禁系统共用**（`Script/Settle/default.py:7628-7630`）：同居助理被监禁时会互相覆盖。属既有隐患，本次不修。
8. **cid 59（`sleep_h_awake_1|shower_flag_4` → 状态机 94 直接 `get_npc_cloth()`）** 没有助理排除前提，会给模板衣服并孤立衣柜内容。但受 §2.5-1 的门禁限制，该行在常规路径下不可达。本次不修，仅标注。
9. **博士房间满员**：`general_movement_module` 寻路失败只 WAIT 1 分钟后重试，低概率但无兜底。

## 7. 不在本 Plan 范围

- 不修改玩家自己的洗澡指令与地点。
- 不修改大浴场娱乐链（桑拿、温泉、足浴等）。
- 不处理同居助理在洗澡过程中被玩家互动/打断的特殊分支。
- 不修复 cid 59 在常规路径下不可达的既有问题。
- 不做「不同地点独立衣柜」的整体重构（`todo list.txt:13`）。
- 不新增口上。

## 8. 回滚

涉及的 Python 与 CSV 逐文件 `git checkout` 即可，重跑 `buildconfig.py`。因**未新增任何存档字段**，回滚不需要处理存档迁移。

## 9. v1 → v2 修订说明

v1 有 4 处会导致死循环或回归的错误：

| # | v1 的做法 | 实际后果 | v2 的做法 |
| ---: | --- | --- | --- |
| 1 | 给行为 805 追加效果 301 清零 shower | `shower_flag_0` = “今天没洗过澡”，`shower_time` 是 4 小时窗口 → 助理整晚循环洗澡；主就寝入口 cid 23 依赖 `shower_flag_4`，助理还会不睡觉 | 收尾不清零 shower |
| 2 | 认定“805 无其他 target 引用” | 泡脚链 cid 485 就用 805 | 完全不动 805 |
| 3 | 用状态机 81 / 行为 805 穿回衣服 | 643 只 append，浴巾脱不掉 → “浴巾套衣服” | 改用状态机 88 / 行为 809 |
| 4 | 收尾行放 type 12 | `shower_flag_4` 时 type 12 不被检索 → 静默失效 | 收尾行放 type 11 段首 |

另外补强：v1 只靠 CSV 行序做互斥，且 flag2/3/4 只覆盖 `in_dr_room` 一侧，助理被跟随机制拖出后会掉进大浴场链；v2 补齐了「不在→回房间」的行并加了显式互斥前提。

## 10. 实施记录

### 10.1 v3 实际改动

与 §4 清单一致，10 个文件。相较 v2 的净变化：

- **删除**了 v2 的 type 11 收尾行（原 cid 908 → 状态机 88）。
- **删除**了 v2 在 `default_cloth.py` 加的 647 早退守卫及 `handle_premise` 顶层导入。
- **新增**了「检查衣柜」的前提放开与面板改造。
- **修正**了手动重排编号时产生的重复 cid（见 §10.2）。

### 10.2 修正手动重排引入的重复 cid

助理链被手动移到文件末尾 900 号段后，**cid 902 被用了两次**：第 49 行的睡奸醒来入口（type 0）与第 190 行的「去博士房间」（type 12）。

后果比“其中一行失效”更糟：`game_config.py:1485` 让后者覆盖前者；`:1488-1495` 的 `config_target_premise_data.setdefault(cid, set())` 之后 `add`，两行前提被**并集**成含互斥项（`shower_flag_0` + `shower_flag_1`）的集合 → **两行都永远不会被选中**。

已把睡奸醒来入口改为 **cid 908**，链保持 901~907 连续。

### 10.3 验证结果

**静态断言（25 项全部通过）**

- `target.csv` 无重复 cid（162 行，删除收尾行后）；不存在指向状态机 88 的助理行。
- 901~908 全部载入，状态机分别为 71/572/72/572/73/572/74/71。
- 新前提 `in_locker_room_or_dormitory_or_dr_room` 已注册；`5040,check_locker` 前提已放开。
- 全表无未注册前提。

**目标链选取模拟（用受控前提驱动真实 `handle_npc_ai.search_target()`）**

| 场景 | 命中 |
| --- | --- |
| 助理·淋浴时间入口 | 901 |
| 助理·flag1 不在/在博士房间 | 902 / 903 |
| 助理·flag2 不在/在博士房间 | 904 / 905 |
| 助理·flag3 不在/在博士房间 | 906 / 907 |
| 助理·flag4 围浴巾 | **无命中**（链已结束） |
| 助理·flag4 围浴巾 + 就寝时间 | 23（去睡觉） |
| 助理·flag4 仍在淋浴时间 | **无命中**（不重复洗澡） |
| 助理·禁止一切洗澡 | **无命中** |
| 普通干员 flag0/1/2/3 | 51 / 52 / 54 / 57（原样） |

睡奸醒来入口互斥也已验证：同居助理只满足 908，普通干员只满足 58。

**衣物结算模拟（走完整夜，9 项全部通过）**

| 检查项 | 结果 |
| --- | --- |
| ① 脱衣后身上清空、衣服进大浴场衣柜（中转） | 通过 |
| ② 围浴巾后身上只剩 51/551/851，647 把衣服转进她的衣柜 | 通过 |
| ③ 睡觉换睡衣、浴巾已脱，衣服仍在衣柜 | 通过 |
| ④ 次日在博士房间起床，从衣柜穿回原衣服并清空衣柜 | 通过 |
| ⑤⑥ 普通干员大浴场链与次日穿回 | 通过 |
| ⑦⑧⑨ 衣柜路由 helper：更衣室→2、宿舍→3、博士房间→3（不再崩溃） | 通过 |

### 10.4 尚未覆盖的验证

需要在真实游戏进程中人工确认：

1. 572 的实际寻路表现（跨大场景移动耗时、博士房间满员时的等待）。
2. 助理在博士房间洗澡时，玩家在场看到的提示文本与断面图表现。
3. 在博士房间实际打开「检查衣柜」，以及在更衣室/宿舍各开一次确认无回归。
4. 行为 112 的效果 1751 是否真的把博士房间登记进 `facility_damage_data`（§6.6 已标注为已知副作用）。

## 11. v2 → v3 修订说明：为什么不需要独立的博士房间衣柜

v3 最初的设计是新增一个 `cloth_locker_in_dr_room` 字段，作为独立的「博士房间衣柜」。实测后放弃，改为**直接复用宿舍衣柜**。

**理由**：开启同居服务时 `dormitory` 字段已被改写为博士房间（§2.3），所以：

- 647 把衣服从大浴场衣柜转进「宿舍衣柜」，对她而言就是转进了博士房间的衣柜；
- 次日 649 从「宿舍衣柜」穿回，而她正是在博士房间起床。

实测（强制路由退回宿舍衣柜、并让 647 守卫失效）确认整条链贯通，原衣服完整穿回。

**独立字段反而引入新问题**：

| | 复用宿舍衣柜 | 独立字段 |
| --- | --- | --- |
| 新增数据/存档迁移 | 无 | 需要新字段 + `old_chara_to_new` 回填 |
| 关闭同居时 | 衣服自动跟她回自己宿舍 | 衣服被永久遗留在博士房间，需专门写转移代码 |
| 别的角色在博士房间脱衣 | 进他们自己的宿舍衣柜，次日照常穿回 | **变成孤儿衣服** |
| UI `part_type` | 沿用 3 | 需扩展出 4 |

唯一的代价是不再有「博士房间衣柜」这个独立概念，但由于博士房间本来就是她的宿舍，语义并不矛盾。若将来要做 `todo list.txt:13` 的「不同地点独立衣柜」整体重构，届时再统一处理。
