# Plan 13：睡觉中被吵醒的行为、反感、状态，与睡觉换衣链修复

- 状态：已完成（2026-08-25 归档，单元测试 59 项全部通过，游戏内整体测试由用户验收；见 §10）
- 来源：用户需求 → "增加一个睡觉中被吵醒的行为，增加对玩家的反感，获得一个睡觉中被吵醒的状态，并将玩家赶出去，该状态有一个小时的计时，在一小时内角色无法入睡；另外角色睡觉会刷新衣服（尤其是内裤等贴身衣物），被吵醒后再次入睡时不进行刷新"；规划过程中用户追加要求"一并处理 `Behavior_Effect.csv:20` 里 509 排在 650 之前的问题"
- 预计改动量：22 个文件，约 300~400 行（5 个 CSV + 4 个常量文件 + 7 个逻辑文件 + 1 个新口上 CSV + 3 个编辑器副本 CSV + 2 个存档/UI）
- 风险等级：中（改动了全体角色每天必跑的睡觉效果链顺序）
- 适用代码快照：`master @ 44a513de9`（v2026.8.25-1）

## 已确认的设计口径（规划阶段与用户确认）

| 问题 | 结论 |
| --- | --- |
| 怎么把玩家赶出去 | 用户指定：复用既有结算器 `TARGET_MOVE_TO_PRE_SCENE = 762` |
| 反感量级 | 用户选「中量」。⚠️ 提问时把中量标成 base=50 是错的，项目惯例中量 = base **100**（`Second_effect.py:1351`），少量 = base **5**（`default.py:3699`）。本计划按 **base=100** 实现，想更轻改这一个数即可 |
| 睡奸中被吵醒是否也走新流程 | **不走**，只对 `unconscious_h == 0` 的普通睡眠生效 |
| CD 期间 NPC 做什么 | 不新增 target，靠 AI 现有回落 |
| 509/650 顺序问题 | 在本计划内一并修复 |

---

## 1. 问题描述

本计划合并两件相关的事。

### 1.1 被吵醒之后什么都没发生

- **现状**：Plan 04 实现了「同房间内的其他睡眠角色也进行被吵醒判定」，但 `Script/Design/handle_npc_ai_in_h.py:373-380` 的普通睡眠分支只做三件事 —— 打印「{0}被{1}的动静吵醒了」、清零疲劳与熟睡值、强制结束睡眠行为。干员被博士吵醒**没有任何情绪代价**，玩家可零成本反复骚扰；醒来后又被 AI 立刻判回「要睡觉 → 睡觉」，博士还站在房间里，观感上等于没被吵醒。
- **期望**：角色执行「睡觉中被吵醒」行为 → 对玩家反感 +中量 → 获得 1 小时的「被吵醒」状态 → 玩家被推出房间、房门重新关上 → 1 小时内角色不再产生睡觉需求。
- **复现路径**：进干员宿舍，趁其浅睡（`sleep_level <= 1`）时执行任意非等待/休息/睡觉的行为。

### 1.2 睡觉会刷新贴身衣物

- **现状**：每次入睡都会 `clothing.get_sleep_cloth()` → `get_underwear(part_flag=2)` 重随机内裤；被吵醒后重睡会再刷一次，被偷走的内裤凭空复原。
- **期望**：已经穿着睡衣的角色再次入睡时不再换衣。
- **复现路径**：偷走干员内裤 → 吵醒 → 等其重睡 → 内裤回来了。

### 1.3 白天衣服在宿舍内睡觉时凭空消失

- **现状**：`data/csv/Behavior_Effect.csv:20` 的 sleep 链为 `… 457 - 509 - 606 - 648 - 650 - 634 …`。在自己宿舍睡觉时 509 先跑 `get_sleep_cloth()`，其第一步 `get_cloth_wear_zero_except_need()` 把白天衣服**直接从 `cloth_wear` 过滤掉且不写入任何衣柜**，随后换上睡衣；等 650 跑到时身上只剩睡衣，于是搬进宿舍衣柜的是睡衣；634 再跑一次 `get_sleep_cloth()` 把睡衣补穿回来（并**第二次**随机内裤）。commit `a7c0a2cb9` 新增 650 是为了修这个 BUG，但因为插在 509 之后，**只修好了「衣柜检查面板缺失该角色」，衣服照旧消失**。
- **期望**：白天衣服（连同其精液数据）完整进入宿舍衣柜，起床时由 649 穿回；一次睡觉只随机一次内裤。
- **复现路径**：干员不洗澡直接回宿舍睡觉 → 查宿舍衣柜，里面是睡衣而不是白天的制服。
- **对照**：洗澡路径（`wear_to_locker`(804) 效果 642 → 大浴场衣柜；`put_shower_cloth`(802) 效果 647 → 宿舍衣柜）在睡觉前就把白天衣服存进宿舍衣柜了，650 的「衣柜非空则 return」把它挡掉 —— **洗澡路径一直是对的，出问题的只有不洗澡直接睡这条路径**。

## 2. 现状调查

### 2.1 吵醒判定的完整调用链

```
character_behavior.character_behavior(0, ...)                Script/Design/character_behavior.py:145
└─ realtime_settle.character_aotu_change_value(0, ...)       Script/Settle/realtime_settle.py:66
     └─ (:157) not handle_time_stop_on and handle_scene_someone_sleeping
          └─ settle_sleep_h(0, true_add_time)                Script/Settle/realtime_settle.py:544
               ├─ get_sleep_disturbance_value()              Script/Settle/realtime_settle.py:517
               └─ (:604 sleep_level<=1) judge_weak_up_in_sleep_h(0, sleeper_id)
                                                             Script/Design/handle_npc_ai_in_h.py:348
                    ├─ unconscious_h==1 → recover_from_unconscious_h()   :173
                    └─ else → WaitDraw + judge_character_status_time_over(end_now=2)  :373-380
```

`settle_sleep_h()` 已有豁免（`Script/Settle/realtime_settle.py:578-583`）：玩家行为为 `WAIT/REST/SLEEP`、目标服安眠药（`h_state.body_item[9][1]==1`）、目标烂醉（`drunk_level>=3`）；时停在 :158 上游排除。这些天然把新流程一并挡住，无需重复处理。

### 2.2 参考实现：「睡奸中醒来」`sp_flag.sleep_h_awake`

| 环节 | 位置 |
| --- | --- |
| 字段 | `Script/Core/game_type.py:784`（`SPECIAL_FLAG` 内，纯 bool，无计时字段） |
| 前提常量 | `Script/Core/constant_promise.py:1646-1652` |
| 前提实现 | `Script/Design/handle_premise/handle_premise_sp_flag.py:2055-2113` |
| 编辑器登记 | `tools/ArkEditor/csv/Premise.csv:827-830`（分组「特殊flag_无意识」） |
| 置位 / 清零 | 置位 `Script/Design/handle_npc_ai_in_h.py:208-209`；清零 `Script/Settle/sleep_settle.py:97` + `Script/StateMachine/default.py:2175`（状态机 94） |
| AI 用法 | `data/target/default/target.csv` 第 12/17/54/69 行 |

### 2.3 睡觉效果链逐项拆解

`data/csv/Behavior_Effect.csv:20`（`sleep` / cid 111）：
`31 - 36 - 301 - 321 - 489 - 457 - 509 - 606 - 648 - 650 - 634 - 932 - 1504 - 1505 - 1751`

| 效果 | 实现 | 说明 |
| --- | --- | --- |
| 321 `SLEEP_FLAG_TO_0` | `Script/Settle/default.py:4735` | **睡觉开始时**就把 `sp_flag.sleep` 清成 0 |
| 509 `SLEEP_ADD_ADJUST` | `Script/Settle/default.py:9275` | 在自己宿舍 → `get_sleep_cloth()` + 50% 判定关门 |
| 606 `CLOTH_SEE_ZERO` | `Script/Settle/default_cloth.py:131` | 内衣可视清零，与顺序无关 |
| 648 `CLEAN_LOCKER_CLOTH_SEMEN` | `Script/Settle/default_cloth.py:742` | 清空 `cloth_locker_semen` |
| 650 `WEAR_TO_DORMITORY_LOCKER` | `Script/Settle/default_cloth.py:688` | 身上衣服（**含首饰**）搬进宿舍衣柜 + `cloth_locker_semen ↔ cloth_semen` 交换；玩家 / 囚犯 / **宿舍衣柜非空**时提前 return |
| 634 `GET_SLEEP_CLOTH` | `Script/Settle/default_cloth.py:476` | 管理中→全裸 / 囚犯→跳过 / 否则 `get_sleep_cloth()` |
| 932 `ADJUST_BODY_MANAGE_SLEEP_ITEM` | — | 睡觉用管理道具，与衣服无关 |

`648 → 650` 必须保持相邻且 648 在前：650 做的是 `cloth_locker_semen, cloth_semen = cloth_semen, cloth_locker_semen` 交换，需要先由 648 把旧衣柜精液清空。

**关键时序**：NPC 的行为效果链在**行为开始时**结算 —— `Script/Design/character_behavior.py:165-175` 只在 `behavior_id` 为 `SHARE_BLANKLY`（刚由 `find_character_target` 赋新行为）或 `MOVE` 时调 `judge_character_status()`。所以换睡衣发生在入睡瞬间，不是睡醒时。

### 2.4 起床回穿路径（决定 650 该不该搬首饰）

`get_up`(113) 效果链 `366 - 372 - 649 - 703 - 931`；649 → `clothing.get_cloth_from_dormitory_locker()`（`Script/Design/clothing.py:133`）。
其 :162-167 会把宿舍衣柜里**不在角色 CSV 模板 `tem_character.Cloth` 中的衣服直接删除**。
因此 650 若把首饰（`tag == 6`）搬进衣柜，非模板首饰会被 649 永久删掉。
同族的 `handle_wear_to_shower_locker`（`Script/Settle/default_cloth.py:572-575`）明确用 `tag != 6` 排除首饰，让首饰留在身上 —— 两者不一致。

### 2.5 可复用的既有实现

| 用途 | 复用对象 |
| --- | --- |
| 赶玩家出房间 | `Script/Settle/default.py:4107 handle_target_move_to_pre_scene`（effect **762**）→ `:4075 handle_move_to_pre_scene` → `:764 handle_move_to_target_scene`；依赖 `action_info.past_move_position_list`（`Script/Design/map_handle.py:118-123` 每次移动压栈，最大 10 条），并置 `sp_flag.move_stop = True` 打断玩家剩余寻路 |
| 关门 | `Script/Settle/default.py:4027 handle_door_close`（effect **752**），关的是 `character_id` 自己所在场景 |
| 加反感 | `Script/Settle/common_default.py:165 base_chara_state_common_settle(character_id, add_time, 20, base_value, ability_level=character_data.ability[18], change_data=...)`；档位参照 `Script/Settle/default.py:3699`（少量 base=5）、`Script/Settle/Second_effect.py:1351`（中量 base=100） |
| 就地插入一个行为并立刻结算 | `Script/Design/handle_npc_ai_in_h.py:337-343`（设 `behavior_id`/`state`/`duration` 后直接 `character_behavior.judge_character_status()`） |
| 新增前提 | `Script/Design/handle_premise/handle_premise_sp_flag.py` 的 `@add_premise` 模式 |
| 状态在角色信息栏的显示 | `Script/UI/Panel/character_info_head.py:110-133`（睡眠/装睡状态的输出位置） |

### 2.6 已知陷阱与硬约束

1. **`else` 分支覆盖面过宽**：`handle_unconscious_flag_ge_1`（`Script/Design/handle_premise/handle_premise_sp_flag.py:1662`）直接 `return sp_flag.unconscious_h`，是真值判定而非 `==1`。当前 `judge_weak_up_in_sleep_h` 的 `else` 会吃进 `unconscious_h ∈ {4平然,5空气,6体控,7心控}`，这些角色跑反感结算会被 `Script/Settle/common_default.py:214/217` 静默 return。**必须把 `else:` 收窄成 `elif ... == 0:`。**
2. **反感结算的顺序依赖**：`Script/Settle/common_default.py:217` 要求 `handle_normal_6` 正常。必须在 `sleep_point` 清零（`handle_npc_ai_in_h.py:365-366`）**且** `judge_character_status_time_over` 已把 `behavior_id` 从 `SLEEP` 重置**之后**再刷新异常位 5/6。现有代码 :367-368 是在结束睡眠**之前**刷的，需调序。
3. **多睡眠者会把玩家连推两格**：`Script/Settle/realtime_settle.py:569` 遍历的是 `character_list` 的拷贝，玩家被 762 移走后循环继续，第二个睡眠者会再推一次。需加守卫。
4. **762 对玩家静默**：`Script/Settle/default.py:787` 的提示条件是 `character_id > 0`，玩家（id 0）被移动**没有任何提示**，必须靠口上文案交代。
5. **762 会解锁旧场景的门**：`Script/Design/map_handle.py:106-107` 对旧场景 `close_flag = 0`。需要在 762 之后补挂 752。
6. **`sp_flag.sleep` 在入睡瞬间就是 0**（效果 321），醒来时角色不处于「要睡觉」态；CD 应挂在**产生睡觉需求**的入口（110110/110115），不是 120105。挂 120105 会让角色顶着 `sleep_flag=1` 一小时，`normal_1` 恒为 0，期间**洗澡/吃饭/聊天/工作全部做不了**。
7. **`add_time` 不会是 0**：`Script/Design/settle_behavior.py:35 add_time = int((now_time - start_time).seconds/60)`，`now_time` 是 `Script/Design/character_behavior.py:204` 的 `start_time + duration`；`duration=1` → `add_time=1`，效果链正常执行，链内顺序不影响 `add_time`。但 `.seconds` 对负 timedelta 会返回 86340 这类巨值，**`behavior.start_time` 必须被重置成当前时间**。
8. **行为 cid 必须三处都空闲**：`data/csv/Behavior_Data.csv`、`Script/Core/constant/Behavior_Int.py`、`tools/ArkEditor/csv/Behavior_Data.csv`（历史不同步）。规划时实测 **810 三处均空闲**；`Script/Core/constant/CharacterStatus.py` 现有最大 946。`Script/Core/constant_effect.py` 的 `BehaviorEffect` **按分类分号段**（属性_状态 41~88、属性_状态特殊补正 110~146、行动 1701~1724 …），新效果必须落在自己分类的号段末尾，不能一律往文件尾部追加；实测 89~109 与 1725/1726 均空闲。⚠️ 实施时必须重新核对。
9. **`Behavior_Effect.csv` 必须有对应行**，否则 `Script/Design/settle_behavior.py:404` 判定不成立，**口上根本不会触发**。
10. `data/talk/` 是 `os.walk` 递归扫描（`buildconfig.py:509-512`），新增 CSV 无需登记；但 `auto_build_config.py:57-59` 在 `data/Character_Talk.json` 存在时会跳过口上重建，**必须跑全量 `buildconfig.py`**。`Script/Config/config_def.py` 由 buildconfig 从 CSV 表头重新生成，**不可手改**。
11. 本机 Python 必须用 `.conda\python.exe`（裸 `python` 是 Store 空壳别名，exit 49 无输出）。
12. `Script/Core/save_handle.py:531 update_dict_with_default` 会递归给旧存档回填新字段默认值，但按项目惯例（skill `add-new-instruction` 第八步）仍要在 `Script/Core/save_handle.py:175` 附近的逐角色回填段补 `hasattr` 兜底。

## 3. 设计决策

### 3.1 状态只用一个自过期的 datetime，不再加 bool

`action_info.sleep_disturbed_end_time: datetime` 一个字段即状态本体：`cache.game_time < end_time` 即「处于被吵醒状态」。

弃选「bool + datetime 两个字段」（照抄 `sleep_h_awake` 的形态）：bool 需要清零挂点，而可用的两个挂点都不可靠 —— 状态机 94 的唯一入口 `data/target/default/target.csv:69` 硬要求 `sleep_h_awake_1`，被吵醒的角色永远进不去（**死代码**）；状态机 93 的入口 `target.csv:9` 要求 `in_dor`，角色若不在宿舍就不跑，flag 会永久残留、导致该角色此后再也不换睡衣。datetime 自过期，读档也不会有脏状态，前提与编辑器同步量减半。

### 3.2 衣服问题分两层解决

**第一层（治本）：把效果链顺序改对。** `648 - 650` 整体前移到 `509` 之前：

```
旧：31 - 36 - 301 - 321 - 489 - 457 - 509 - 606 - 648 - 650 - 634 - 932 - 1504 - 1505 - 1751
新：31 - 36 - 301 - 321 - 489 - 457 - 648 - 650 - 509 - 606 - 634 - 932 - 1504 - 1505 - 1751
```

新顺序语义：清理衣柜精液 → 白天衣服（连同精液数据）入宿舍衣柜 → 在宿舍则换睡衣＋判定关门 → 内衣可视清零 → 634 兜底换睡衣（只在不在宿舍睡时真正生效）→ 管理道具调整。洗澡路径不受影响（宿舍衣柜非空，650 照旧 early-return）。

**第二层（治标，也是用户要的「被吵醒后重睡不换衣」）：`get_sleep_cloth()` 开头加无状态早退** —— 已经穿着睡衣（`cloth_wear[5]` 含 552/553 且 `cloth_wear[8]` 含 852/853）就直接返回。

弃选「在 509/634 外面套 `if not 被吵醒`」：那需要一个额外的 bool 状态字段和清零挂点（§3.1 的同样问题），且只覆盖被吵醒一条路径。无状态判断的好处：

- 509 / 634 / 650 三个结算器都不用为此改一行；
- 自动覆盖**所有**重睡路径（爆睡 200 / 安眠药 210 / 烂醉 215 / 监禁 130105·130110 / 自然醒后重睡）；
- 与第一层协同：顺序改对后，在宿舍睡觉时 509 已换好睡衣，634 命中早退，**顺带消除「一次睡觉随机两次内裤」的浪费**；不在宿舍睡时 509 跳过，634 正常换睡衣；
- 万一 650 因某种原因把睡衣搬进了衣柜，634 会发现「没穿睡衣」从而补穿，不会裸睡。

已知副作用：跳过 `get_sleep_cloth` 等于连开头的 `get_cloth_wear_zero_except_need()` 一起跳过，角色身上若有玩家给穿的道具或污浊衣物会带着睡；异常位 4（服装异常）也不会刷新 —— 早退前补一次 `settle_chara_unnormal_flag(character_id, 4)` 即可。属可接受的行为差异，记录于此，非缺陷。

### 3.3 650 对齐 642，排除首饰

顺序修复后 650 首次真正作用于白天装束，而它会把首饰（`tag == 6`）一并搬进宿舍衣柜，起床时被 649 的模板过滤（`Script/Design/clothing.py:162-167`）永久删除。给 650 的循环加上和 `handle_wear_to_shower_locker`（`Script/Settle/default_cloth.py:572-575`）一致的 `game_config.config_clothing_tem[cloth_id].tag != 6` 条件，让首饰留在身上，两条路径行为统一。

### 3.4 CD 挂在「产生睡觉需求」而不是「执行睡觉」

`sleep_disturbed_0` 挂到 `data/target/default/target.csv` 的 `110110` / `110115`（→ 状态机 78 进入要睡觉状态）与 `130110`（`unnormal_2|sleep_time` → 状态机 44，监禁/临盆角色的睡觉分支）。

- CD 期间角色**行为完全正常**（能洗澡、吃饭、聊天、工作），只是不会重新产生睡觉需求，比顶着 `sleep_flag=1` 在宿舍呆站一小时自然得多；
- 语义也更准：「被吵醒后一小时内不想睡」优于「想睡但睡不着」。

不挡生理性强制睡眠：`200`（`tired_100` 爆睡）、`210`（安眠药）、`215`（烂醉）、`110100`（HP=1）、`130105`（`unnormal_2|self_tired`）一律不加限制；且 `judge_weak_up_in_sleep_h` 本来就把 `tired_point` 清零，`tired_ge_85` 类目标短期内不会触发。

### 3.5 做成 Behavior 而不是直接写 Python

用户要求的是「增加一个睡觉中被吵醒的**行为**」。收益：口上走 `talk.handle_talk()` 可配、效果链在 CSV 里可用 ArkEditor 编辑、结算面板复用现有绘制。先例是 `NO_CONSCIOUS_H_END` 在 `Script/Design/handle_npc_ai_in_h.py:337-343` 的就地插入写法。

## 4. 详细改动步骤

> 下列 cid / effect id 均为**建议值**（规划时实测过一次），实施时必须重新核对空闲号。
> 建议实施顺序：先做 A 组（换衣链修复，独立可验证），再做 B 组（被吵醒行为）。

---

### A 组：睡觉换衣链修复

#### 4.1 重排 sleep 效果链（`data/csv/Behavior_Effect.csv:20`）

按 §3.2 的新链改写该行。⚠️ 只调整顺序，不增删任何 effect id。

#### 4.2 650 排除首饰（`Script/Settle/default_cloth.py:725-733`）

循环内除 `if cloth_id in special_cloth_list: continue` 之外，再加 `game_config.config_clothing_tem[cloth_id].tag == 6` 的跳过（与 :572-575 写法一致）。同步修正函数 docstring（:696 的「含首饰」需要改）。

#### 4.3 已穿睡衣则不换衣（`Script/Design/clothing.py:509 get_sleep_cloth`）

函数开头加早退：若 `cloth_wear[5]` 已含 552 或 553、且 `cloth_wear[8]` 已含 852 或 853，则先 `handle_premise.settle_chara_unnormal_flag(character_id, 4)` 再 `return`。睡衣编号以 :521-526 的实际取值为准。

---

### B 组：睡觉中被吵醒

#### 4.4 数据结构（`Script/Core/game_type.py:595 ACTION_INFO`）

紧邻 :615 `sleep_time` 新增：

```python
self.sleep_disturbed_end_time: datetime.datetime = datetime.datetime(1, 1, 1)
""" 睡觉中被吵醒状态的结束时间，在此之前角色不会产生睡觉需求 """
```

并在 `Script/Core/save_handle.py:175` 附近的逐角色回填段补 `hasattr` 兜底。

#### 4.5 前提（3 个文件）

- `Script/Core/constant_promise.py`：在**时间_角色**段末尾（`TARGET_NOT_HAVE_CONSCIOUS_OR_UNCONSCIOUS_H_TODAY` 之后）新增
  `SLEEP_DISTURBED_0 = "sleep_disturbed_0"` / `SLEEP_DISTURBED_1 = "sleep_disturbed_1"`，
  以及交互对象版 `t_sleep_disturbed_0/1`（供口上使用）。
- `Script/Design/handle_premise/handle_premise_other.py`：时间_角色 类的前提实现都集中在该文件（不是 `handle_premise_time.py`，后者放的是「时间_当前」），接在 `handle_target_not_have_conscious_or_unconscious_h_today()` 之后实现 4 个函数。
  `sleep_disturbed_1` 判定：
  `game_time.judge_date_big_or_small(character_data.action_info.sleep_disturbed_end_time, cache.game_time) == 1`
  （`Script/Design/game_time.py:268`，返回 1 表示前者大于后者；相等返回 2，此处按「已到期」处理）。`handle_premise_other.py` 顶部已 import `game_time`，无需局部导入。
- `tools/ArkEditor/csv/Premise.csv`：接在 `t_not_have_conscious_or_unconscious_h_today` 之后补 4 行，分组填「**时间_角色**」。

#### 4.6 新结算器（`Script/Core/constant_effect.py` + `Script/Settle/default.py` + `tools/ArkEditor/csv/Effect.csv`）

`BehaviorEffect` 新增两个，**分属两个不同的分类，编号必须落在各自分类的号段里**：

| 常量 | 编号 | 分类 | 位置 | 实现 |
| --- | --- | --- | --- | --- |
| `SELF_ADD_MIDDLE_DISGUST` | **89** | 属性_状态 | 紧接 `ADD_SMALL_SHY = 88`（属性_状态段 41~88 的末尾）；函数体也放在 `Script/Settle/default.py` 的 `handle_add_small_shy()` 之后，与同类的 `ADD_SMALL_*` 自身系列并排 | 仿 `Script/Settle/default.py:3678 handle_target_add_small_disgust`，改为对自己：`base_chara_state_common_settle(character_id, add_time, 20, 100, ability_level=character_data.ability[18], change_data=change_data)` |
| `GET_SLEEP_DISTURBED_STATE` | **1726** | 行动 | 留在行动段（1701~1724）之后 | `character_data.action_info.sleep_disturbed_end_time = game_time.get_sub_date(minute=60, old_date=cache.game_time)` |

两者都要在 `tools/ArkEditor/csv/Effect.csv` 按各自分类补行：89 插在 `88,ADD_SMALL_SHY` 之后、`effect_type` 填「属性_状态」；1726 的 `effect_type` 填「行动」。

#### 4.7 新行为（8 个文件）

- `data/csv/Behavior_Data.csv`：`810,wake_up_by_noise,睡觉中被吵醒,1,npc,日常|AI行动`（与 801-809 同段）
- `data/csv/Behavior_Introduce.csv`：补行为介绍
- `data/csv/Behavior_Effect.csv`：`810,wake_up_by_noise,89 - 1726 - 321 - 762 - 752`
  —— 89 加中量反感；1726 赋予被吵醒状态；321 兜底清「要睡觉」；762 把交互对象（＝玩家）推回前一场景；752 重新关上房门（修 §2.6-5）
- `Script/Core/constant/Behavior.py`：`WAKE_UP_BY_NOISE = "wake_up_by_noise"`
- `Script/Core/constant/BehaviorStr.py`：同名条目
- `Script/Core/constant/Behavior_Int.py`：`WAKE_UP_BY_NOISE = 810`
- `Script/Core/constant/CharacterStatus.py`：`STATUS_WAKE_UP_BY_NOISE = 947`
- `tools/ArkEditor/csv/Behavior_Data.csv`：同步一行

#### 4.8 口上（`data/talk/daily/wake_up_by_noise.csv`）

五列 `cid,behavior_id,adv_id,premise,context`，表头 5 行照抄 `data/talk/daily/sleep.csv`。
⚠️ 由于 762 对玩家**没有任何移动提示**（§2.6-4），文案必须显式交代「被推出房间」，例如
`{Name}猛地睁开眼睛，看清是{PlayerName}后，皱着眉一言不发地把{PlayerName}推出了房间，关上了门。`
至少给 `high_1` 兜底几条；可另按好感度 / 反发刻印 / `sleep_time` 分档写差异化文本。

#### 4.9 触发点改造（`Script/Design/handle_npc_ai_in_h.py:369-380`）

1. `else:` **收窄为** `elif target_data.sp_flag.unconscious_h == 0:`，其余 `unconscious_h`（2醉酒/3时停/4平然/5空气/6体控/7心控）保留原来的 `WaitDraw` + `judge_character_status_time_over(end_now=2)`（修 §2.6-1）。
2. 新分支内的顺序（**顺序即正确性**）：
   1. `character_behavior.judge_character_status_time_over(target_character_id, cache.game_time, end_now=2)`
      结束睡眠 —— `Script/Design/character_behavior.py:331` 会 `character_data.behavior = game_type.Behavior()` 整体重置，**必须在它之后**再赋新行为；
   2. `handle_premise.settle_chara_unnormal_flag(target_character_id, 5)` 与 `(…, 6)`
      —— 把现有 :367-368 的这两行**移到这里**（修 §2.6-2）；
   3. `instuct_judege.init_character_behavior_start_time(target_character_id, cache.game_time)`
      —— `judge_character_status_time_over` 在 `time_judge==2` 时（`Script/Design/character_behavior.py:349`）已调过一次，这里显式再调是**冗余但便宜**的保险，防 §2.6-7 的 `.seconds` 巨值；
   4. `duration = 1`；`behavior_id = constant.Behavior.WAKE_UP_BY_NOISE`；
      `state = constant.CharacterStatus.STATUS_WAKE_UP_BY_NOISE`；
      `target_character_id = character_id`（＝玩家 0，供 762 使用）；
   5. `character_behavior.judge_character_status(target_character_id)` 当场结算（口上 + 效果链）。
3. 原来的 `WaitDraw`「{0}被{1}的动静吵醒了」由口上取代（实施时二选一，不要两段都出）。
4. **加一行注释**说明 §7 表中的 `bagging_chara_id` 哨兵依赖，避免以后被误改。

`instuct_judege` 与 `character_behavior` 已分别在该文件 :12 / :15 顶部导入，无循环导入问题。

#### 4.10 多睡眠者守卫（`Script/Settle/realtime_settle.py:569` 循环内）

循环体开头加：玩家当前 `position` 已不等于本场景（说明已被上一个睡眠者赶出去）就 `break`（修 §2.6-3）。

#### 4.11 禁止入睡（`data/target/default/target.csv`）

在下列三行的前提串里加 `sleep_disturbed_0`，并同步更新备注列：

| 行 | target | 现有前提 |
| --- | --- | --- |
| 43 | `110110` | `normal_1267\|sleep_time\|shower_flag_4\|assistant_salutation_of_ai_disable` |
| 44 | `110115` | `normal_1267\|sleep_time\|not_shower_time\|assistant_salutation_of_ai_disable\|tired_ge_10` |
| 92 | `130110` | `unnormal_2\|sleep_time` |

**不动** `120105`（见 §3.4），也不新增 target 行。

#### 4.12 状态显示（`Script/UI/Panel/character_info_head.py:110-133`）

在装睡判定（:128）附近增加 `<被吵醒>` 输出，tooltip 说明「刚被吵醒，短时间内不会想睡」，可附剩余分钟数。Web 模式共用同一份 draw 对象，无需单独适配。

## 5. 构建与缓存

```bash
# 本机必须用 conda 解释器（裸 python 是 Store 空壳别名）
.conda\python.exe tools\lint_target_csv.py   # 先校验 target.csv 里新前提名拼写
.conda\python.exe buildconfig.py             # 必跑全量：改了 5 张 CSV + 新增口上文件
.conda\python.exe init_data.py               # 预热运行时缓存
.conda\python.exe buildpo.py                 # 新增 _() 中文提示时
.conda\python.exe buildmo.py
```

必须**全量** `buildconfig.py`：`auto_build_config.py` 在 `data/Character_Talk.json` 存在时会跳过口上重建，新口上文件不会生效。无地图改动，不需要删 `data/SceneData` / `data/MapData` / `data/PlaceData` / `data/ScenePath` 缓存。

## 6. 验证清单

### 6.1 单元测试（实施方执行）

不启动图形界面，以 scratchpad 脚本（不入库）初始化配置与缓存后直接调用函数验证；无头环境搭法参照 skill `headless-game-test`。

**A 组：换衣链**

- [ ] `get_sleep_cloth`：已穿睡衣 → `cloth_wear` 不变且异常位 4 已刷新；未穿睡衣 → 正常换睡衣
- [ ] 不洗澡直接在自己宿舍睡：跑完整条新 sleep 链后，**宿舍衣柜里是白天衣服**（不是睡衣），身上是睡衣，首饰仍在身上，`cloth_semen` / `cloth_locker_semen` 已正确交换
- [ ] 洗澡后再睡：宿舍衣柜内容不被睡衣覆盖（650 仍 early-return）
- [ ] 不在自己宿舍睡（如休息室）：白天衣服进宿舍衣柜，身上由 634 换成睡衣
- [ ] 一次睡觉只调用一次 `get_underwear`（可用 monkeypatch 计数）
- [ ] 囚犯 / 被要求裸睡 / 玩家（id 0）三条早退分支行为不变
- [ ] 起床跑 649 后能穿回宿舍衣柜里的白天衣服

**B 组：被吵醒**

- [ ] 注册断言：`constant.handle_premise_data` 含 4 个新前提；`constant.settle_behavior_effect_data` 含 2 个新效果；`game_config.config_behavior["wake_up_by_noise"]` 与 `game_config.config_behavior_effect_data["wake_up_by_noise"]` 均存在
- [ ] `sleep_disturbed_1`：`end_time` 在未来 → 1；已过 / 等于当前 / 为 `datetime(1,1,1)` → 0
- [ ] 状态结算器执行后 `sleep_disturbed_end_time == cache.game_time + 60min`
- [ ] 反感结算器在 `unconscious_h == 0` 且异常位 5/6 正常时确实增加 `status_data[20]`；置成意识模糊后按既有规则被跳过
- [ ] `judge_weak_up_in_sleep_h(0, npc)`：`unconscious_h == 0` 走新行为；`== 1` 仍走 `recover_from_unconscious_h`；`∈ {4,5,6,7}` 走旧 WaitDraw 分支不报错
- [ ] 走完新行为后：NPC `status_data[20]` 增加、`sleep_disturbed_end_time` 已设、玩家 `position` 变为 `past_move_position_list` 栈顶、NPC 所在场景 `close_flag` 已恢复
- [ ] `past_move_position_list` 为空时 762 静默不动作，不抛异常
- [ ] `bagging_chara_id != 0` 时新行为的实际表现（记录结果，见 §7）
- [ ] `settle_sleep_h`：同场景两个浅睡 NPC 都被判醒时，玩家只被推一格
- [ ] 旧存档兼容：构造缺 `sleep_disturbed_end_time` 的 `ACTION_INFO` 走载入回填不报错
- [ ] `.conda\python.exe buildconfig.py` 全量重建无报错，新行为/效果/口上在 `data/data.json`、`data/Character_Talk.json` 中齐备

### 6.2 游戏内整体测试（由用户执行）

- [ ] 干员不洗澡直接回宿舍睡 → 查宿舍衣柜，里面是**白天的制服**；次日起床穿回；首饰整晚都在身上
- [ ] 干员洗完澡再睡 → 衣柜内容与修改前一致
- [ ] 偷内裤 → 吵醒 → 重睡，确认内裤**没有**复原；睡衣也不变
- [ ] 进干员宿舍趁其浅睡时做动作 → 触发被吵醒行为：看到口上、反感变化面板，博士被弹回上一个场景，宿舍门重新关上
- [ ] 被吵醒的干员 1 小时内不会重新去睡；CD 期间**照常**洗澡/吃饭/工作/聊天；1 小时后正常入睡
- [ ] 睡奸中被吵醒仍走原有无意识 H 恢复流程，没有重复提示、玩家没被误赶出去
- [ ] 时停中、目标服安眠药、目标烂醉、玩家行为为等待/休息/睡觉时都不触发
- [ ] 一屋多人睡觉时玩家只被推出一次
- [ ] Tk 与 Web 两种绘制模式下口上、结算面板、`<被吵醒>` 状态显示都正常
- [ ] 旧存档载入不报错，且载入后的第一晚睡觉衣柜数据正常

## 7. 风险与回滚

| 风险 | 说明 | 对策 |
| --- | --- | --- |
| **改动 sleep 效果链是全局性的** | 全体角色每天必跑，衣柜/精液数据/关门判定都在这条链上 | A 组单独先做、先验证；单元测试覆盖「不洗澡直接睡 / 洗澡后睡 / 不在宿舍睡 / 囚犯 / 裸睡管理」五条分支 |
| 650 排除首饰改变既有表现 | 非模板首饰不再进衣柜、不再被 649 删除 | 这是与 642 对齐的修正；若发现有依赖旧行为的地方，单独撤销这一处即可 |
| 762 静默失效 | 玩家若无移动记录（`past_move_position_list` 为空）则不会被移动 | 按用户选定的 762 实现；若实测常见路径下会空栈，再补回落：`map_handle.get_map_for_path(position) + ["0"]` 即本区入口（实测除顶层 `泰拉` 外所有地图都有 `0` 场景） |
| 新行为被瞬间抹掉 | `Script/Design/character_behavior.py:290-296`：玩家被 762 移出场景后本该触发 `end_time = now_time` → `add_time=0` → 新行为被 `game_type.Behavior()` 抹掉。只因 `sp_flag.bagging_chara_id` 默认值恰好是 0、与 `target_character_id=0` 相等才跳过这道覆盖 | **巧合成立**：若该 NPC 正在搬运别人（`bagging_chara_id != 0`）新行为会被抹掉。§4.9-4 要求加注释固化该依赖；§6.1 补一条用例记录实际表现 |
| 反感被静默吞掉 | `Script/Settle/common_default.py:214/217` 对意识模糊/非 normal_6 直接 return | §4.9 的收窄 + 调序就是为此；单元测试专项验证 |
| 跳过换衣带来的行为差异 | 已穿睡衣时不再 `get_cloth_wear_zero_except_need()`，道具/污浊衣物会带着睡 | 记录为已知限制（§3.2），非缺陷 |
| 编号撞号 | 建议的 cid / effect id 可能已被占用 | 实施前用脚本重新扫描 `Behavior_Data.csv` × `Behavior_Int.py` × `tools/ArkEditor/csv/Behavior_Data.csv` 三处交集 |
| 漏跑 buildconfig | 口上不触发、启动 KeyError | §5 列为必跑步骤 |

**回滚**：四组可独立回滚 ——

1. 效果链顺序：把 `data/csv/Behavior_Effect.csv:20` 改回旧顺序；
2. 650 排除首饰：撤销 `Script/Settle/default_cloth.py` 里那一个条件；
3. 换衣早退：撤销 `Script/Design/clothing.py:509` 处的 `if`；
4. 被吵醒全套（整体回滚）：常量 + 结算器 + 3 张 CSV + 口上 + 触发点改造 + `settle_sleep_h` 守卫 + `ACTION_INFO` 字段 + 前提 + UI 显示。

撤销任何 CSV 改动后都要重跑 `.conda\python.exe buildconfig.py`。

## 8. 改动文件清单

| 文件 | 类型 | 改动 | 组 |
| --- | --- | --- | --- |
| `data/csv/Behavior_Effect.csv` | 修改 | :20 sleep 链重排为 `… 457 - 648 - 650 - 509 - 606 - 634 …`；新增 `wake_up_by_noise` 行 | A+B |
| `Script/Settle/default_cloth.py` | 修改 | 650 `handle_wear_to_dormitory_locker` 排除首饰（`tag != 6`），同步 docstring | A |
| `Script/Design/clothing.py` | 修改 | `get_sleep_cloth` 开头加「已穿睡衣则早退」 | A |
| `Script/Core/game_type.py` | 修改 | `ACTION_INFO` 加 `sleep_disturbed_end_time` | B |
| `Script/Core/save_handle.py` | 修改 | :175 附近加 `hasattr` 兜底回填 | B |
| `Script/Core/constant_promise.py` | 修改 | 新增 4 个前提常量 | B |
| `Script/Design/handle_premise/handle_premise_other.py` | 修改 | 实现 4 个「时间_角色」前提函数 | B |
| `Script/Core/constant_effect.py` | 修改 | 新增 2 个 `BehaviorEffect` 常量 | B |
| `Script/Settle/default.py` | 修改 | 新增「自身增加中量反感」「获得被吵醒状态」两个结算器 | B |
| `Script/Settle/realtime_settle.py` | 修改 | `settle_sleep_h` 循环加「玩家已被赶走则 break」守卫 | B |
| `Script/Design/handle_npc_ai_in_h.py` | 修改 | `judge_weak_up_in_sleep_h`：`else` 收窄、调整异常位刷新顺序、改为执行新行为 | B |
| `Script/Core/constant/Behavior.py` | 修改 | `WAKE_UP_BY_NOISE` | B |
| `Script/Core/constant/BehaviorStr.py` | 修改 | `WAKE_UP_BY_NOISE` | B |
| `Script/Core/constant/Behavior_Int.py` | 修改 | `WAKE_UP_BY_NOISE = 810` | B |
| `Script/Core/constant/CharacterStatus.py` | 修改 | `STATUS_WAKE_UP_BY_NOISE = 947` | B |
| `Script/UI/Panel/character_info_head.py` | 修改 | 显示 `<被吵醒>` | B |
| `data/csv/Behavior_Data.csv` | 修改 | 新增 `wake_up_by_noise` | B |
| `data/csv/Behavior_Introduce.csv` | 修改 | 新增行为介绍 | B |
| `data/target/default/target.csv` | 修改 | 110110 / 110115 / 130110 加 `sleep_disturbed_0` | B |
| `data/talk/daily/wake_up_by_noise.csv` | 新增 | 被吵醒口上 | B |
| `tools/ArkEditor/csv/Premise.csv` | 修改 | 同步 4 个前提 | B |
| `tools/ArkEditor/csv/Effect.csv` | 修改 | 同步 2 个结算器 | B |
| `tools/ArkEditor/csv/Behavior_Data.csv` | 修改 | 同步新行为 | B |

**未改动**：`Script/Settle/sleep_settle.py`（自过期状态不需要日更新清理）、`Script/StateMachine/default.py`（不需要清零挂点）、`Script/Design/handle_npc_ai_in_h.py` 的 `recover_from_unconscious_h()`（睡奸分支不变）、`data/csv/Sleep_Level.csv`（阈值不变）、`Script/Settle/default_cloth.py` 的 634 与 `Script/Settle/default.py` 的 509（因 §3.2 的无状态方案而无需改）。

## 9. 不在本 Plan 范围

- 不改睡奸中醒来（`sleep_h_awake`）的既有流程与洗澡闭环。
- 不处理 NPC 之间互相吵醒；仍以「玩家动作吵醒同房间 NPC」为范围（与 Plan 04 一致）。
- 不新增 CD 期间的专属 AI 行为（用户已确认靠现有回落）。
- 不调整 `get_sleep_disturbance_value()` 的动作影响系数与 `data/csv/Sleep_Level.csv` 阈值。
- **不修** `Script/Design/clothing.py:162-167` 中 649 对「不在角色 CSV 模板里的衣服」的过滤删除 —— 玩家给角色换的非模板服装在起床时仍会丢失。这是洗澡路径与睡觉路径共用的既有设计，两条路径表现一致，需另开计划讨论。
- **不修** `data/target/default/target.csv:69` 的 `120330,94,sleep_h_awake_1|shower_flag_4` 导致状态机 94 里的清零逻辑对非睡奸路径不可达的问题。

## 10. 执行记录

### 10.1 实际改动

实施日期 2026-08-25，实际改动 **22 个文件**（与 §8 清单一致，无增减）。按组核对：

**A 组：睡觉换衣链修复**

| 文件 | 实际落点 | 说明 |
| --- | --- | --- |
| `data/csv/Behavior_Effect.csv` | 第 20 行 | sleep 链改为 `31 - 36 - 301 - 321 - 489 - 457 - 648 - 650 - 509 - 606 - 634 - 932 - 1504 - 1505 - 1751`，只调顺序未增删 |
| `Script/Settle/default_cloth.py` | `handle_wear_to_dormitory_locker()` 循环内 | 新增 `tag == 6` 跳过；docstring 由「含首饰」改为「除首饰与必穿项外」 |
| `Script/Design/clothing.py` | `get_sleep_cloth()` 开头 | 新增「已穿睡衣则刷新异常位4后早退」 |

**B 组：睡觉中被吵醒**

| 文件 | 实际落点 | 说明 |
| --- | --- | --- |
| `Script/Core/game_type.py` | `ACTION_INFO`，紧邻 `sleep_time` | 新增 `sleep_disturbed_end_time` |
| `Script/Core/save_handle.py` | `_normalize_loaded_save_paths()` 逐角色回填段 | 新增 `hasattr` 兜底 |
| `Script/Core/constant_promise.py` | 时间_角色段末尾（`TARGET_NOT_HAVE_CONSCIOUS_OR_UNCONSCIOUS_H_TODAY` 之后） | 新增 4 个前提常量 |
| `Script/Design/handle_premise/handle_premise_other.py` | `handle_target_not_have_conscious_or_unconscious_h_today()` 之后 | 新增 4 个前提函数；`handle_sleep_disturbed_1()` 用 `getattr` 对缺字段的旧存档兜底 |
| `Script/Core/constant_effect.py` | `ADD_SMALL_SHY = 88` 之后 / `TARGET_NOT_BE_CARRIED = 1724` 之后 | `SELF_ADD_MIDDLE_DISGUST = 89`（属性_状态）、`GET_SLEEP_DISTURBED_STATE = 1726`（行动） |
| `Script/Settle/default.py` | `handle_add_small_shy()` 之后 / `handle_target_not_be_carried()` 之后 | 分别新增 `handle_self_add_middle_disgust()`（89）与 `handle_get_sleep_disturbed_state()`（1726） |
| `Script/Settle/realtime_settle.py` | `settle_sleep_h()` 循环首行 | 玩家已离开本场景则 `break` |
| `Script/Design/handle_npc_ai_in_h.py` | `judge_weak_up_in_sleep_h()` | `else` 收窄为 `elif unconscious_h == 0`，新增其他无意识的 `else` 分支；异常位刷新移到结束睡眠之后 |
| `Script/Core/constant/Behavior.py` / `BehaviorStr.py` | `PUT_SLEEP_CLOTH` 之后 | `WAKE_UP_BY_NOISE = "wake_up_by_noise"` |
| `Script/Core/constant/Behavior_Int.py` / `CharacterStatus.py` | 同上位置 | `947` |
| `Script/UI/Panel/character_info_head.py` | 装睡判定之后 | `<被吵醒>` + 剩余分钟数 tooltip，样式 `warning` |
| `data/csv/Behavior_Data.csv` | 809 之后 | `810,wake_up_by_noise,睡觉中被吵醒,1,npc,日常\|AI行动` |
| `data/csv/Behavior_Introduce.csv` | 946 之后 | `947,wake_up_by_noise,...` |
| `data/csv/Behavior_Effect.csv` | 809 之后 | `810,wake_up_by_noise,89 - 1726 - 321 - 762 - 752` |
| `data/target/default/target.csv` | 第 43/44/91 行 | 110110 / 110115 / 130110 各加 `sleep_disturbed_0` 与备注 |
| `data/talk/daily/wake_up_by_noise.csv` | 新增 | 7 条口上（5 条 `high_1` + 1 条 `sleep_time` + 1 条 `favorability_ge_3`） |
| `tools/ArkEditor/csv/Premise.csv` | 时间_角色段末尾（430 行之后） | 同步 4 个前提，分组填「时间_角色」 |
| `tools/ArkEditor/csv/Effect.csv` | `88,ADD_SMALL_SHY` 之后 / 1724 之后 | 同步 `89,...,属性_状态` 与 `1726,...,行动` |
| `tools/ArkEditor/csv/Behavior_Data.csv` | 文件末尾 | 同步 `810,wake_up_by_noise,...` |

实施前重新扫描确认：行为 cid **810** 在 `Behavior_Data.csv` / `Behavior_Int.py` / `tools/ArkEditor/csv/Behavior_Data.csv` 三处均空闲；`CharacterStatus` 最大 946、**947** 空闲；`BehaviorEffect` 的属性_状态段最大 88、**89~109** 空闲，行动段最大 1724、**1725/1726** 空闲；`tools/ArkEditor/csv/Effect.csv` 同上。

### 10.2 与计划的偏差

1. **`Behavior_Int` 与 `Behavior_Introduce` 用的不是 `Behavior_Data` 的 cid 空间。** §4.7 写的是 `Behavior_Int.WAKE_UP_BY_NOISE = 810`，实际发现 `Behavior_Introduce.csv` 的 cid 与 `Behavior_Int` / `CharacterStatus` 一一对应（如 `143,put_sleep_cloth` 对应 `Behavior_Int.PUT_SLEEP_CLOTH = 143`，而它在 `Behavior_Data.csv` 里是 803）。因此三者统一取 **947**，只有 `data/csv/Behavior_Data.csv` 与 `tools/ArkEditor/csv/Behavior_Data.csv` 用 810。ArkEditor 副本按近期条目（1501~1503 与 `data/csv` 一致）的做法沿用 810。
2. **异常位 5/6 的刷新对三条分支做了拆分。** §4.9 只说「移到结束睡眠之后」，实际因为 `else` 分支被拆成三条（睡奸 / 普通睡眠 / 其他无意识），三条各自保留了自己的刷新调用：睡奸分支维持原来的「先刷新再走 `recover_from_unconscious_h`」，另两条改为「先结束睡眠再刷新」。这样对睡奸路径零行为变更。
3. **`settle_sleep_h` 守卫用字符串比较而非列表比较。** `Scene.scene_path` 是 `str`、`Character.position` 是 `list`，直接比较恒不相等。实际写成 `map_handle.get_map_system_path_str_for_list(now_character_data.position) != scene_path_str`。
4. **`tools/lint_target_csv.py` 的 `EXIT` 不可信。** 首次带 `| tail` 运行时输出被管道攒住、看起来像卡死；去掉管道后确认它**已输出「全部规则通过」**（R5 前提名解析、R6 状态机、R7 effect 引用全部通过），只是游戏导入链拉起了 Flask 非守护线程导致进程不自行退出。这与 skill `headless-game-test` 铁律第 2 条描述一致。
5. **§7 的 `bagging_chara_id` 风险实测不成立。** 单元测试构造 `bagging_chara_id = 999` 的场景后，新行为仍正常完成（`behavior='wake_up_by_noise'`、反感 +101、玩家被推回前一场景）。原因是 `judge_character_status()` 在 `judge_character_status_time_over()` 之前就把整条效果链跑完了，那条「交互对象不在场景内则立刻结束行动」的例外分支影响的是**下一轮**的行为收尾，不会回滚已结算的效果。代码里的注释保留，作为对该依赖的说明。

**已知限制（记录于此，非缺陷）**：

- 跳过 `get_sleep_cloth()` 时连开头的 `get_cloth_wear_zero_except_need()` 一起跳过，角色身上若有玩家给穿的道具或污浊衣物会带着睡（§3.2 已述）。
- 玩家被 762 移动时没有任何系统提示（§2.6-4），完全依赖口上文案交代，因此 7 条口上全部显式写了「推出房间 / 关上门」。

### 10.2.1 第二轮调整（2026-08-25，用户验收后的分类修正）

用户指出两处归类不当，已同步修正代码与本文档正文（§2.6-8 / §4.5 / §4.6 / §4.7 / §8 / §10.1）：

| # | 调整 | 改动 |
| --- | --- | --- |
| 1 | 「自身增加中量反感」原本按「新效果一律追加到文件尾部」的做法取了 1725、分类填「状态」，与它实际所属的**属性_状态**类不符 | 编号 **1725 → 89**，紧接同类段末尾的 `ADD_SMALL_SHY = 88`；`constant_effect.py` 的常量与 docstring、`tools/ArkEditor/csv/Effect.csv` 的行位置与 `effect_type` 均改为「属性_状态」；`Script/Settle/default.py` 里的函数体也从 `handle_target_not_be_carried()` 之后移到 `handle_add_small_shy()` 之后，与同类的 `ADD_SMALL_*` 自身系列并排；`data/csv/Behavior_Effect.csv` 的 `wake_up_by_noise` 效果链随之改为 `89 - 1726 - 321 - 762 - 752` |
| 2 | 「自身获得睡觉中被吵醒状态」分类填的是「状态」，但它做的是给角色打一个行动性质的计时标记 | 编号保持 **1726** 不变，`constant_effect.py` docstring 与 `tools/ArkEditor/csv/Effect.csv` 的 `effect_type` 均改为「**行动**」，位置留在行动段（1701~1724）之后 |
| 3 | 4 个新前提原本归在「特殊flag_无意识」，但它们判定的是「被吵醒后的一小时是否已过」，本质是时间类 | 分类改为「**时间_角色**」：`constant_promise.py` 中 4 个常量从特殊flag_无意识段移到时间_角色段末尾（`TARGET_NOT_HAVE_CONSCIOUS_OR_UNCONSCIOUS_H_TODAY` 之后）并改写 docstring 前缀；`tools/ArkEditor/csv/Premise.csv` 的 4 行同样移位并把分组列改为「时间_角色」；**实现函数从 `handle_premise_sp_flag.py` 整体迁到 `handle_premise_other.py`**（时间_角色 类的前提实现都在该文件，而不是 `handle_premise_time.py` —— 后者放的是「时间_当前」），迁移时去掉了块内的局部 `from Script.Design import game_time`，改用该文件顶部已有的模块级导入 |

**由此得到的一条通用教训（已写入 §2.6-8）**：`constant_effect.py` 的 `BehaviorEffect` 是**按分类分号段**的（属性_状态 41~88、属性_状态特殊补正 110~146、行动 1701~1724 …），新增效果必须落在自己分类的号段末尾，不能一律往文件尾部追加。前提常量与 `Premise.csv` 同理，分组列决定它在 ArkEditor 里出现在哪个下拉分组下。

**回归验证**：改完后重新跑 `buildconfig.py` 全量重建（EXIT=0）、`init_data.py`（EXIT=0），并把单元测试中引用 1725 的两处断言改为 89 后重跑 —— **59 项断言依然全部通过**，其中直接覆盖本轮改动的有「结算器 89（自身增加中量反感）已注册」「反感结算器在正常状态下确实增加 `status_data[20]`」「4 个前提均已注册」「`data/data.json` 中 `wake_up_by_noise` 效果链为 `89 - 1726 - 321 - 762 - 752`」。

### 10.3 测试结果

**§6.1 单元测试：59 项断言全部通过**（脚本在 scratchpad，不入库）。

A 组 17 项：

- [x] `get_sleep_cloth` 首次换睡衣 + 穿内裤；已穿睡衣时早退，内裤不复原、睡衣不变；未穿睡衣时正常换（5 项）
- [x] sleep 效果链顺序 648 < 650 < 509 < 634，且仍为 15 项未增删（2 项）
- [x] 650 把普通衣服搬进宿舍衣柜、把首饰留在身上（2 项）
- [x] 650 的两条早退分支（宿舍衣柜非空 / 玩家 id=0）（2 项）
- [x] 在宿舍睡觉时 509 调用一次 `get_underwear`、634 因已穿睡衣不再调用，结束后角色确实穿着睡衣不裸睡（3 项）
- [x] 跑完整条新 sleep 链后：白天衣服进宿舍衣柜（不是睡衣）、身上穿睡衣、首饰整晚留在身上（3 项）

B 组 42 项：

- [x] 4 个前提、2 个结算器、行为配置、行为效果链、口上编译进 `Character_Talk.json` 的注册断言（9 项）
- [x] `sleep_disturbed_1/0` 的未来 / 已过 / 相等 / 默认值 / 交互对象版 / 缺字段旧存档共 8 项
- [x] 状态结算器：`end_time == 当前 + 60min`、设置后立刻处于该状态、`add_time=0` 不生效（3 项）
- [x] 反感结算器：正常状态下 `status_data[20]` 增加、意识模糊时被跳过（2 项）
- [x] `judge_weak_up_in_sleep_h` 三条分支分流：`unconscious_h == 0` 走新行为（反感增加、获得状态、玩家被推回前一场景、疲劳与熟睡值清零）；`== 1` 仍走 `recover_from_unconscious_h` 且不赋状态、不赶玩家；`== 6`（体控）走旧分支不赋新行为、不赋状态、不赶玩家（10 项）
- [x] `past_move_position_list` 为空时不抛异常、玩家原地不动、但反感与状态仍然生效（3 项）
- [x] `settle_sleep_h` 多睡眠者：玩家只被推一格，只有一个睡眠者完成被吵醒结算（2 项）
- [x] `target.csv` 三行含 `sleep_disturbed_0` 且 120105 未被改动（4 项）
- [x] 旧存档缺 `sleep_disturbed_end_time` 时载入回填不报错（1 项）
- 另记录一条观察项（非断言）：`bagging_chara_id != 0` 时新行为仍正常完成，见 §10.2-5

**构建验证**：

- [x] `.conda\python.exe buildconfig.py` 全量重建（先删 `data/Character_Talk.json` 强制重建口上）无报错
- [x] `data/data.json` 中 sleep 效果链已是新顺序、含 `wake_up_by_noise` 行为与其效果链 `1725 - 1726 - 321 - 762 - 752`
- [x] `data/Character_Talk.json` 中 `wake_up_by_noise` 口上 7 条齐备
- [x] `.conda\python.exe tools\lint_target_csv.py` 输出「全部规则通过」

### 10.4 尚未覆盖的验证（留给用户的游戏内清单）

§6.2 的 10 项游戏内整体测试全部留待用户执行，其中最需要重点确认的三条：

1. 干员不洗澡直接回宿舍睡 → 查宿舍衣柜里是**白天的制服**、次日起床能穿回、首饰整晚在身上（这是本次风险最高的全局性改动）。
2. 干员洗完澡再睡 → 衣柜内容与修改前一致（验证 650 的 early-return 未被顺序调整破坏）。
3. 被吵醒的干员 CD 期间**照常**洗澡/吃饭/工作/聊天，只是不去睡觉（验证 §3.4 的挂点选择确实避开了 `sleep_flag=1` 卡死一小时的副作用）。

另需在 Web 绘制模式下确认口上、结算面板与 `<被吵醒>` 状态显示正常。
