# A4 NPC 视角推演

## 何时用

- 需求里出现"干员会自己去 / 自动 / 主动"——这意味着要走 AI 目标链，而不是玩家指令。
- A3 推演表的"NPC 当场反应"一列出现两处以上"无"，需要决定 NPC 侧到底要不要参与。
- 功能涉及 NPC 的位置、时段、需求标记（`sp_flag.shower / sleep / pee` 等），可能与既有目标链抢优先级。
- 用户说"跟随 / 助理 / 睡觉时也要这样"，但没说各状态下有何不同。
- **不适合**：纯玩家侧 UI 功能（plan_20 做饭面板记忆）；系统设置类开关（plan_21）——NPC 侧只是"读同一入口"，没有独立行为可推。

## 怎么做

1. 先定性：本功能 NPC 是**主动触发者**（要写 `data/target/default/target.csv` 新行）、**被动参与者**（只在玩家指令结算里被改数值）、还是**不参与**。三者改动量差一个数量级，先问用户。
2. 主动触发时读 `Script/Design/handle_npc_ai.py:277 find_character_target`，按它的检索顺序推演：type 0 高优先 → type 12 需求执行（门禁 `handle_premise/__init__.py:907 handle_normal_1`）→ type 13 非链需求 → type 11 进入需求链 → 工作/娱乐（`:586 npc_auto_work_or_entertainment`）。type 11/12/13 都是 `get_first_only=True`（`:316/:322/:328`），**CSV 行序即优先级**。类型含义查 `data/csv/Target_Type.csv`。
3. grep 与本功能同一需求标记的既有行（如 `grep -n "shower_flag_1|" data/target/default/target.csv`），逐行判断新行放前还是放后、需不需要显式互斥前提。plan_07 §2.5：靠行序做互斥不可靠，仓库约定是显式互斥前提（先例 `handle_premise/__init__.py:1561 handle_not_is_assistant_and_in_dr_room`）。
4. 按状态逐格填表：跟随（`:733 judge_same_position_npc_follow` 会把 `is_follow==1` 的 NPC 直接拽走）、助理（`:182 judge_assistant_character`）、睡眠 / 疲劳（`:41 judge_character_tired_sleep`）、无意识（`sp_flag.unconscious_h`）、监禁（`handle_premise_sp_flag.py:1050 handle_imprisonment_1`，监禁角色走 type 13 的 `unnormal_2` 分支，见 `target.csv:91` cid 130110）、H 中（`find_character_target` 开头：`is_h` 且非群交自慰时直接结束）。
5. 每格写"表现 + 依据"；写不出依据的格子标 并列为问题。
6. 把"NPC 定性"写进 §1，目标链行与互斥前提写进 §3。

## 输出格式

```markdown
### NPC 视角

定性：<主动触发 / 被动参与 / 不参与>（理由）

目标链落点：type <n>，插在 cid <x> 之<前/后>；互斥前提：<名>

| NPC 状态 | 表现 | 依据 |
| --- | --- | --- |
| 跟随中 | | `handle_npc_ai.py:行号` |
| 助理 | | |
| 睡眠 / 疲劳 | | |
| 无意识 H | | |
| 监禁 | | |
| 玩家正在与其 H | | |
```

## 写进计划的哪一节

定性与状态表进 §1（它决定验收范围）；目标链行、优先级与互斥前提进 §3（它是取舍，要写弃选方案）。

## 例子

**用户原话**："助理和博士同居时，洗澡直接在博士房间洗，不用跑大浴场。"

**助手调研**：`grep -n "shower_flag_1|" data/target/default/target.csv` → `:63` cid 120300 普通链"去大浴室更衣室"、`:82` cid 120800 助理链"不在博士房间则去博士房间"、`:83` cid 120805"在博士房间则脱成全裸"（plan_07 实施后的现状；plan_08 已把 cid 重编为 `type×10000+组×100+序号`）；`sed -n 277,330p Script/Design/handle_npc_ai.py` 确认 type 12 门禁与 `get_first_only`；`grep -n "def judge_same_position_npc_follow" Script/Design/handle_npc_ai.py` → `:733`。

**产出**：定性 = 主动触发（洗澡本来就是 NPC 自主需求链，玩家不下指令）。目标链落点 type 12，每个 `shower_flag` 阶段配一对"不在→回博士房间 / 在→执行"；普通链每行追加 `not_is_assistant_live_together` 显式互斥。

| NPC 状态 | 表现 | 依据 |
| --- | --- | --- |
| 跟随中 | 会被拽出博士房间，下一轮经"不在→回博士房间"行自行走回 | `handle_npc_ai.py:733`；plan_07 §2.5 第 3 条 |
| 助理（非同居） | 走普通大浴场链 | 入口前提含 `assistant_live_together_on`（`target.csv:51` cid 110800） |
| 睡眠 / 疲劳 | 不进链；睡奸醒来有单独 type 0 入口 | `target.csv:17` cid 600 用 `sleep_h_awake_1` |
| 无意识 H | `find_character_target` 开头 `is_h` 直接结束，不检索 | `handle_npc_ai.py:277` 起 |
| 监禁 | 走 `unnormal_2` 组自己的洗澡行（状态机 70 原地淋浴，不进助理链） | `target.csv:93` cid 130120 |
| shower_flag_4（围浴巾后） | type 12 门禁 `handle_normal_1` 不含 flag 4，链必须在围浴巾结束 | `handle_premise/__init__.py:907`；plan_07 §2.5 第 1 条 |

**抛给用户的问题**：
1. 助理被跟随拽走时，是"走回博士房间继续洗"还是"本次洗澡作废"？（推荐：走回，靠 flag1/2/3 各配一对行全覆盖；作废需要额外清 flag 的效果。）
2. 洗完后穿回衣服要不要在博士房间也能"检查衣柜"？（推荐：要，否则玩家看到助理裸着走出去；plan_07 §3.6 最终放开。）

## 常见误用

- **只推玩家侧的"NPC 反应"**：写了"好感 +5"就当 NPC 视角推完了。真正的 NPC 视角是它会不会**自己**触发、在哪一步被别的目标抢走。
- **状态表全填"正常"**：六种状态每格都写"照常生效"而无行号。跟随与 H 中几乎从不"照常"。
- **靠行序做互斥**：把新行放在普通行之前就认为搞定。plan_07 v1 只靠行序互斥，助理被跟随拖走后掉进大浴场链，v2 才补显式互斥前提（plan_07 §9）；plan_08 重编号后行序更不可作为约束。
