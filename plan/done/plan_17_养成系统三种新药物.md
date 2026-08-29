# Plan 17：养成系统三种新药物（成长加速药 / 成长停滞药 / 成长继续药）

- 状态：**已实施（2026-08-29，单元测试 68/68 通过，见 §12；第 1 次修改（时间函数复用与季月名）后回归 93/93 通过，见 §12.5；第 2 次修改（常量统一到 `pregnancy_constant.py`）后回归 93/93 通过，见 §12.6；第 3 次修改（谱系图 7 代 + 生育素质判定前提化）后回归 107/107 通过，见 §12.7；第 4 次修改（孵化加速药限定育儿室）后回归 110/110 通过，见 §12.8；第 5 次修改（成长加速药改为婴儿/幼女/萝莉三阶段通用、剂量为当前阶段剩余天数的 30%）后回归 127/127 通过，见 §12.9；第 6 次修改（35~38 号药口上补幼女/萝莉差分）后回归 132/132 通过，见 §12.10；游戏内整体测试与 buildpo/buildmo 本地化步骤待用户执行）**
- 来源：用户需求 → 在 plan_14 四种怀孕药物的基础上，新增三种通过礼物系统对 NPC 使用的养成（女儿成长）相关药物道具
- 修订记录：
  - v0 —— 骨架：章节结构 + 目标整理
  - v1 —— 现状调查（§2 全部为实际代码核实结果）+ 设计决策（§3）+ 数据结构（§4）+ 改动步骤（§5）+ 验证/风险/清单 + §11 待确认口径
  - v2 —— 口径确认轮（2026-08-28）：①加速整体提前后续阶段 ②`check_rearing_complete` 改逐婴儿结算 ③**成长停滞改为可见素质【成长停滞】（talent 28）而非 flag 字段** ④**本期实装 4 个成长停滞前提** ⑤level 3 / price 200。§3.3/§3.6/§4/§5/§7/§9/§11 已按确认结果改写
- 预计改动量：约 15 个代码/数据文件 + 4 个 ArkEditor 副本 CSV（3 张数据 CSV + 数据结构/存档回填 + 礼物面板 + 妊娠结算 3 个函数 + 前提常量/函数 + 显示面板 + 3 个口上 CSV）
- 风险等级：中低（不改 90/270/450 天基础成长数值；成长加速与 plan_14 同构做"额外天数注入"；成长停滞只是在两处成长判定前加守卫；涉及存档新字段需回填。**唯一的中等风险点是 §3.2 对 `check_rearing_complete` 的多婴儿改造**）
- 适用代码快照：`master @ 05d7d543d`
- 参考文档：`plan/done/plan_14_怀孕系统四种药物.md`（药物礼物链、加速注入、选卵交互、送礼口上的全部先例）、`plan/done/plan_12_怀孕系统升级_方案.md`、`.github/prompts/数据处理工作流/妊娠系统.md`、`.github/prompts/数据处理工作流/礼物系统.md`、`Script/System/Pregnancy_System/怀孕系统设计文档.md`

---

## 1. 目标（用户需求原文整理）

1. 新增三种养成系统相关的药物道具：**成长加速药**、**成长停滞药**、**成长继续药**，均为对 NPC 使用的药物，通过**礼物系统**以送礼方式起效（同 plan_14 四药）。
2. **成长加速药**：
   - 使用条件：玩家在**育儿室**；目标干员（母亲）至少有一个孩子正处于**婴儿期**。
   - 使用时需要**选择对哪个婴儿使用**（同 plan_14 孵化加速药的选卵交互）。
   - 效果：加速该婴儿的成长，加速到**成为幼女的前一天**；这样再睡一天，第二天自然触发"从婴儿成长到幼女"的事件。
   - 口上：参考孵化加速药——把药物递给母亲，母亲拿去给婴儿服用。
3. **成长停滞药**：
   - 使用条件：目标干员为**女儿**，且当前状态为**幼女**或**萝莉**，且**没有**已使用成长停滞药。
   - 效果：对方的成长天数依然正常计算，只是**跳过成长的事件结算**（不会成长到下一阶段）。
4. **成长继续药**：
   - 使用条件：目标干员为**女儿**，且当前状态为**幼女**或**萝莉**，且**已使用**成长停滞药。
   - 效果：解除成长停滞药效果，恢复正常的成长事件结算。

## 2. 现状调查（已完成，均为实际代码核实结果）

### 2.1 道具 CSV 与药物道具先例、空闲 id（已核实）

- [Item.csv](data/csv/Item.csv) 列结构与翻译标记同 plan_14 §2.1（`cid,name,type,tag,level,price,effect,h_item_id,info`，name/info 两列提取翻译）。
- 对 NPC 使用的药物先例：21~28（level 2）、31~38（level 3），price 均 200、effect 0、h_item_id −1；plan_14 新增的 35~38 已落地（[Item.csv:26-29](data/csv/Item.csv#L26)）。
- **id 空闲段核实**（awk 穷举全部 cid）：38 之后下一个已用 id 为 50（相机）——**39~49 空闲**，新药取 **39 / 40 / 41**。
- [Gift_Items.csv](data/csv/Gift_Items.csv)：药物行 cid==item_id、type=11，最后一行药物为 38（[:26](data/csv/Gift_Items.csv#L26)），其后是 51（阴茎倒模 type 13）——39~41 落在 38 与 51 之间，自动归入面板的药物折叠组。

### 2.2 礼物系统全链与药物生效机制（plan_14 落地后的现状，已核实）

| 环节 | 位置 | 说明 |
| --- | --- | --- |
| 指令 | [InstructConfig.csv:49](data/csv/InstructConfig.csv#L49) `1025 give_gift` | 前提 `HAVE_TARGET|NO_TARGET_OR_TARGET_CAN_COOPERATE_OR_IMPRISONMENT_1`，**对幼女/萝莉女儿可用**（无年龄排除） |
| 送出确认 | [gift_panel.py:221](Script/UI/Panel/gift_panel.py#L221) `select_gift` | `check_gift_available` → **gift_id==36 时先 `select_target_egg`**（:232-234）→ `behavior.gift_id = gift_id` → type 11 走 `judge=_("初级骚扰")` 的 `chara_handle_instruct_common_settle(GIVE_GIFT, force_taget_wait=True)` |
| 选卵交互 | [gift_panel.py:247-301](Script/UI/Panel/gift_panel.py#L247) `select_target_egg` / `select_egg_id` | 读 `egg_handle.get_accelerable_hatching_eggs`；仅一枚时直接写 `behavior.gift_egg_id` 跳过选择；多枚时 `TitleLineDraw` + 每枚 `LeftButton` + `[返回]`（返回 False 取消送礼），`flow_handle.askfor_all` 通道 Tk/Web 通用。**成长加速药的选婴儿交互可整段照抄** |
| 使用条件校验 | [gift_panel.py:355](Script/UI/Panel/gift_panel.py#L355) `is_drug_effective` | 每药一个 elif；不满足 → WaitDraw 提示 + return False（不送出、不消耗）。35~38 分支（:441-478）为函数内 import 妊娠模块的先例 |
| 效果结算 | [default.py:7290](Script/Settle/default.py#L7290) `handle_give_gift_add_adjust` | 道具 −1 后 type 11 调 `gift_panel.handle_drug_use_effect(target_id, gift_id)`（:7360） |
| 效果实现 | [gift_panel.py:29](Script/UI/Panel/gift_panel.py#L29) `handle_drug_use_effect` | 每药一个 elif + gold_enrod WaitDraw；36 分支（:79-98）为"读 `behavior.gift_egg_id` → 重置 −1 → 兜底校验目标仍存在 → 注入加速 → 提示新预计日期"的完整先例 |
| 行为字段 | [game_type.py:1064](Script/Core/game_type.py#L1064) `gift_egg_id` | `CharacterBehavior` 上的礼物附加选择字段先例，`getattr(...,-1)` 兜底读取 |
| 购买 | h_item_shop_panel | 自动列出全部 `type=="Drug"`，新药无需改动 |

→ 结论同 plan_14：新增一种药物的礼物链本体 = Item.csv 行 + Gift_Items.csv 行 + `is_drug_effective` 分支 + `handle_drug_use_effect` 分支（+ ArkEditor 副本同步）；成长加速药另加一个"选婴儿"步骤，照 36 号药的选卵结构。

### 2.3 孩子成长机制：婴儿→幼女→萝莉→少女的计时与事件触发点（已核实）

**阶段素质**（[Talent.csv](data/csv/Talent.csv)，Talent_type 1 身体素质）：101 婴儿 / 102 幼女 / 103 萝莉 / 104 少女；母亲侧 23 产后 / 24 育儿 / 27 泌乳。新生儿模板素质固定含 `101:1, 6:1(未初潮), 7:1(未成年)`（[character_handle.py:178](Script/Design/character_handle.py#L178) `born_new_character`）。

**计时基准**：孩子自身的 `pregnancy.born_time`（[game_type.py:323](Script/Core/game_type.py#L323)），写入点唯一——生产/破壳事件 [born_event_panel.py:149](Script/System/Pregnancy_System/born_event_panel.py#L149)（`= cache.game_time`）；debug 面板 [:1765-1766](Script/UI/Panel/debug_panel.py#L1765) / [:1795-1799](Script/UI/Panel/debug_panel.py#L1795) 手改（先例：把 born_time 倒退一年来一键触发育儿完成）。

**`born_time` 的全部天数换算消费点**（grep 穷举 `born_time`，仅 3 个文件）：

| 位置 | 计算 | 阈值/用途 | 驱动方 |
| --- | --- | --- | --- |
| [pregnancy_handle.py:324-350](Script/System/Pregnancy_System/pregnancy_handle.py#L324) `check_rearing` | `(game_time − child.born_time).days`，child = **母亲 `child_id_list[-1]`** | `>= 2` 母亲 23→24（产后→育儿） | 母亲 talent23 |
| [pregnancy_handle.py:355-394](Script/System/Pregnancy_System/pregnancy_handle.py#L355) `check_rearing_complete` | 同上，child = **母亲 `child_id_list[-1]`** | `>= 90`：母亲 24→0、27→0；**孩子 `get_new_character`（上线入 npc_id_got）、101→102、unnormal_flag 7 重算、work_type=152 学生**；二段行为 `rearing_complete`；文案"从[婴儿]成长为了[幼女]" | **母亲 talent24** |
| [pregnancy_handle.py:397-426](Script/System/Pregnancy_System/pregnancy_handle.py#L397) `check_grow_to_loli` | `(game_time − self.born_time).days` | `father_id==0 and talent[102]` 且 `>= 270`：102→103、6→0、`chest_grow`；二段行为 `child_to_loli` | **孩子自身** |
| [pregnancy_handle.py:429-460](Script/System/Pregnancy_System/pregnancy_handle.py#L429) `check_grow_to_girl` | 同上 | `father_id==0 and talent[103]` 且 `>= 450`：103→104、7→0、`chest_grow`+`body_part_grow`；二段行为 `loli_to_girl` | 孩子自身 |
| [pregnancy_panel.py:115-122](Script/System/Pregnancy_System/pregnancy_panel.py#L115) | `child.born_time + 90 天` | 育儿阶段显示"预计 X 完成育儿"（同样只看 `child_id_list[-1]`） | 显示 |
| [debug_panel.py:1723](Script/UI/Panel/debug_panel.py#L1723) | 原值显示 | `[004]:出生的时间` | 显示 |

**推进时机**：以上全部经 [check_all_pregnancy:463-484](Script/System/Pregnancy_System/pregnancy_handle.py#L463) 调用；`check_all_pregnancy` **唯一调用点是玩家睡觉结算** [sleep_settle.py:88](Script/Settle/sleep_settle.py#L88)，遍历 `cache.npc_id_got ∪ {0}`（[:46-47](Script/Settle/sleep_settle.py#L46)）。0 点结算 [past_day_settle.py:66-74](Script/Settle/past_day_settle.py#L66) 只跑受精率/受精/排卵/生理周期，**不跑成长判定**。→ 用药当晚睡觉即结算一次成长判定；"加速到幼女前一天 → 睡一天 → 第二天自然触发"的口径要求：**用药当晚睡觉时有效天数 = 89（不触发），次日睡觉时 = 90（触发）**。

### 2.4 婴儿的存在形态：离线、不在场景、不在 npc_id_got（已核实，直接决定 §3.2/§3.4）

- `born_new_character`（[character_handle.py:155-201](Script/Design/character_handle.py#L155)）创建婴儿后 `init_character` 只对初始干员名集合加 `npc_id_got`（[:55-56](Script/Design/character_handle.py#L55)），`born_new_character` 内的 `npc_id_got.add` 被注释掉（[:197](Script/Design/character_handle.py#L197)）；随后 `settle_chara_unnormal_flag(now_id, 7)`（[:200](Script/Design/character_handle.py#L200)）。
- unnormal flag 7 = 角色离线，判定 [handle_normal_7:1061-1084](Script/Design/handle_premise/__init__.py#L1061) 含 `handle_t_baby_1`（talent101）——**婴儿是离线角色**；position 保持 `Character` 默认 `["0","0"]`（[game_type.py:1607](Script/Core/game_type.py#L1607)），不在任何场景的 `character_list` 中。
- 婴儿在 `check_rearing_complete` 时才经 `get_new_character`（[character_handle.py:301](Script/Design/character_handle.py#L301) → `default.handle_chara_on_line` [:4480](Script/Settle/default.py#L4480)，`npc_id_got.add` [:4524](Script/Settle/default.py#L4524)）上线。
- **推论 1**：婴儿不在 `npc_id_got` → 睡觉结算不会对婴儿本人调用 `check_all_pregnancy`，婴儿→幼女的成长**只能由母亲驱动**（现状即如此）；幼女/萝莉已上线，`check_grow_to_loli/girl` 由本人驱动。
- **推论 2**：婴儿不在场景 `character_list` → "在育儿室"条件只能判**玩家自身位置**（`handle_in_nursery(0)`，[handle_premise_place.py:3416](Script/Design/handle_premise/handle_premise_place.py#L3416)，scene_tag 含 `Nursery`），不能用"场景内有婴儿"的前提（[POSITION_IN_IN_NURSERY_AND_FLAG_BABY_EXIST:939](Script/Design/handle_premise/handle_premise_other.py#L939) 靠 scene character_list，对离线婴儿恒为 0）。育儿室内婴儿清单的既有做法是遍历 `cache.npc_tem_data` 取 talent101（[normal_panel.py:136-140](Script/UI/Panel/normal_panel.py#L136)、[FLAG_BABY_EXIST:921](Script/Design/handle_premise/handle_premise_other.py#L921)）。

### 2.5 多婴儿的既有限制（已核实，本 Plan 的关键设计输入）

- `check_rearing_complete` 与 `check_rearing` 都只看 **`child_id_list[-1]`**（[:332](Script/System/Pregnancy_System/pregnancy_handle.py#L332)、[:363](Script/System/Pregnancy_System/pregnancy_handle.py#L363)），且入口是母亲 talent24。
- 母亲同时有 ≥2 个婴儿是可能的：卵生角色多枚卵各自破壳（[check_egg_born:316-330](Script/System/Pregnancy_System/egg_handle.py#L316) 每晚一枚），破壳结算直接 `talent[24]=1`（[born_event_panel.py:164](Script/System/Pregnancy_System/born_event_panel.py#L164)），育儿期间再破壳一枚即成"双婴"；胎生则要在 90 天育儿期内再次受精+生产（妊娠加速药已让这成为可能）。
- 现状下第二个婴儿出生会把 `child_id_list[-1]` 换成新婴儿，育儿 90 天重新以新婴儿计；**旧婴儿永远不会被 `check_rearing_complete` 处理**（101 永驻、离线永驻），直到再无新婴儿也不会——这是既有 BUG 级限制，与用户"选择对哪个婴儿使用"的需求正面冲突：若不改造，对非最后一个婴儿用药无任何效果。→ §3.2 必须处理。

### 2.6 "女儿"与幼女/萝莉的判定先例（已核实）

- 女儿 = `relationship.father_id == 0`：[handle_self_is_player_daughter:1150-1159](Script/Design/handle_premise/handle_premise_other.py#L1150)（常量 `SELF_IS_PLAYER_DAUGHTER` [constant_promise.py:3890](Script/Core/constant_promise.py#L3890)、`TARGET_IS_PLAYER_DAUGHTER` [:3894](Script/Core/constant_promise.py#L3894) 转发 target）；`init_character` 对带 `Mother_id` 的模板固定 `father_id=0`（[character_handle.py:63-66](Script/Design/character_handle.py#L63)）。成长判定本身也用 `father_id == 0`（§2.3）。
- 幼女或萝莉：现成前提 `SELF_CHILD_OR_LOLI_1` / `T_CHILD_OR_LOLI_1`（[constant_promise.py:2472-2474](Script/Core/constant_promise.py#L2472)，实现 [handle_premise_talent.py:205-228](Script/Design/handle_premise/handle_premise_talent.py#L205)）= `talent[102] or talent[103]`；口上侧可直接用参数化 token `CVP_A2_T|102_E_1` / `CVP_A2_T|103_E_1` 区分。
- 药物条件在 `is_drug_effective` 内直接判 `relationship.father_id == 0` 与 `talent[102]/[103]` 数组即可，不依赖前提系统。

### 2.7 可复用的加速注入与剂量先例（plan_14 已落地，已核实）

- 胎生：`PREGNANCY.acceleration_days`（[game_type.py:344-347](Script/Core/game_type.py#L344)）+ [get_pregnancy_past_day:41](Script/System/Pregnancy_System/pregnancy_handle.py#L41)（`(now − fertilization_time).days + int(acc)`）+ [get_acceleration_amount:54](Script/System/Pregnancy_System/pregnancy_handle.py#L54)（三重夹取剂量）+ [get_pregnancy_acceleration_amount:70](Script/System/Pregnancy_System/pregnancy_handle.py#L70)。
- 卵：[get_hatch_day:126](Script/System/Pregnancy_System/egg_handle.py#L126) / [get_egg_acceleration_amount:138](Script/System/Pregnancy_System/egg_handle.py#L138) / [get_accelerable_hatching_eggs:151](Script/System/Pregnancy_System/egg_handle.py#L151)（供 is_drug_effective 与选卵列表共用的"可加速目标筛选"函数）。
- ⚠️ 注意 `PREGNANCY.acceleration_days` 语义是"**本人怀孕**的加速"，并在本人受精时清零（plan_14 §3.3）——女儿长到少女后可以自己怀孕，因此**不能把成长加速复用到这个字段**，需要独立字段（§3.1）。
- 成长加速与孕期加速的差别：孕期加速是"剩余 30% 的可叠加剂量"，而本需求是"**一次到位加速到幼女前一天**"（剂量 = 89 − 当前有效天数，非公式量），因此不复用 `get_acceleration_amount`。

### 2.8 礼物口上机制与先例文件（已核实）

- 机制同 plan_14 §2.10：口上挂 `give_gift` 一段行为，文件放 [data/talk/daily/gift/](data/talk/daily/gift/)，参数化前提 `CVP_A1_Gift|<礼物id>_G_0`（[handle_premise/__init__.py:392-398](Script/Design/handle_premise/__init__.py#L392) 读 `behavior.gift_id`），cid 从 1000 起（buildconfig 加文件名前缀不冲突），口上显示先于效果结算。
- 先例前提组合（实际文件统计）：`give_gift_hatch_accelerate.csv`（36）与 `give_gift_fake_pregnancy.csv`（37）均为 **6 组 × 5 条 = 30 条**：`基础` / `&CVP_A2_T|104_E_1`（少女）/ `|105`（御姐）/ `|106`（熟女）/ `|107`（人妻）/ `&target_is_player_daughter`；`give_gift_pregnancy_accelerate.csv`（35）为受精/妊娠 × 上述 6 组 = 60 条。单条约 1730~1780 字节（≈ 800 中文字）。
- 文本生成要求文件：[扩充赠礼的代码文本.prompt.md](.github/prompts/复数文本技能生成提示词/V0的无子代理版本/特定指令/扩充赠礼的代码文本.prompt.md)（每前提组合 5 行、约 800 字不少于 650、句号后 `\n`、无对话/地点、占位符 {TargetUpClothName}/{TargetDownClothName}/{breast_s}/{legs_s}）。
- 成长阶段的既有二段行为：`1319 rearing_complete` / `1320 child_to_loli` / `1321 loli_to_girl`（[Behavior_Data.csv:686-688](data/csv/Behavior_Data.csv#L686)）——本 Plan 不新增二段行为（plan_14 v4 口径），成长事件本身的口上沿用既有。

### 2.9 已知陷阱与硬约束（已核实）

- ArkEditor 副本同步：`tools/ArkEditor/csv/Item.csv`、`Gift_Items.csv`（末行格式 `38,38,11,0,假孕终止药`）、`Talent.csv`（info 为短版，先例 [:28](tools/ArkEditor/csv/Talent.csv#L28) `25,0,假孕孕肚,0,因药物而产生的假性孕肚，…`）、`Premise.csv`（素质类前提分组"素质_妊娠"，先例 [:1166-1169](tools/ArkEditor/csv/Premise.csv#L1166) fake_inflation 四行）。
- **素质 id 空闲核实**：Talent.csv 中 27 泌乳之后下一个已用 id 为 31（精爱味觉）——**28~30 空闲**，成长停滞素质取 **28**（Talent_type 0，与 20~27 生育组同组、不可遗传）。素质类前提的完整先例：常量 [constant_promise.py:2312-2318](Script/Core/constant_promise.py#L2312) `FAKE_INFLATION_0/1`、`T_FAKE_INFLATION_0/1` + 函数 [handle_premise_other.py:2763-2775](Script/Design/handle_premise/handle_premise_other.py#L2763)（`talent[25]==1` 返回 1）+ ArkEditor Premise.csv 四行。
- CSV 行所有列必填；CSV/常量改动后必须 `.conda\python.exe buildconfig.py` 全量重建（talk 数据增量构建会跳过）；新增可翻译文本需 buildpo/buildmo。
- 编号（道具 39~41）实施时再次现场核对空闲（plan_06 §8.1 教训）。
- 旧存档兼容：`PREGNANCY` 新字段走 [save_handle.py:276-287](Script/Core/save_handle.py#L276) 逐角色 hasattr 回填段（`acceleration_days` 先例 [:285-287](Script/Core/save_handle.py#L285)）；behavior 新字段 `getattr` 兜底。多周目：[old_chara_to_new.py:740](Script/Core/old_chara_to_new.py#L740) `pregnancy` 结构体整体沿用，新字段自动迁移。
- `handle_drug_use_effect` 在结算阶段执行、道具已扣——全部使用条件必须在 `is_drug_effective` 拦截，结算内只做兜底（选中的婴儿已不是婴儿则提示不生效）。
- Tk/Web 双模式：只用抽象绘制类，选婴儿交互复用面板 `askfor_all`。
- **婴儿是离线角色且不在 npc_id_got**（§2.4）：选婴儿列表必须从母亲 `child_id_list` 过滤 talent101（而非场景或 npc_id_got）；婴儿数据在 `cache.character_data` 中可直接读写。

### 2.10 引用全量清单（成长天数换算点，作为"改完归零"验收判据）

`born_time` 的天数换算裸计算共 **4 处结算 + 1 处显示**（§2.3 表前 5 行），实施后 grep `born_time).days` 应无残留，全部改走 §3.1 的 helper；debug 面板原值显示不改。`talent[101]` 的读取点（[handle_premise_other.py:932/954/3204](Script/Design/handle_premise/handle_premise_other.py#L932)、[handle_premise_work.py:347](Script/Design/handle_premise/handle_premise_work.py#L347)、[StateMachine/default.py:1718](Script/StateMachine/default.py#L1718)、[normal_panel.py:140](Script/UI/Panel/normal_panel.py#L140)）均为只读判定，不受本 Plan 影响。

## 3. 设计决策

### 3.1 成长加速的注入方式与剂量口径

| 方案 | 说明 | 取舍 |
| --- | --- | --- |
| **A（推荐）：孩子 `PREGNANCY` 新增 `growth_acceleration_days: int`，新增 helper `get_child_grow_day(child_id)` = `(game_time − born_time).days + growth_acceleration_days`，§2.3 表中 5 处换算全部改走 helper** | 与 plan_14 的 `acceleration_days + get_pregnancy_past_day` 完全同构；`born_time` 保持真实出生日；debug/面板可显示"已加速 X 天" | 采用 |
| B：直接把 `born_time` 向前拨（`born_time −= timedelta(days=N)`） | 零新字段、所有消费点自动一致（debug 面板一键触发就是这么做的 :1765） | 弃选：出生日失真（后续任何"生日/年龄"类功能都会错），且无法显示加速量 |

- **剂量**：~~一次到位，`add_day = 89 − get_child_grow_day(child_id)`（幼女阈值 90 的前一天）；`add_day <= 0`（已到 89 天及以上）则判定无效、不消耗道具。不叠加、不用 30% 公式。~~ 【第 5 次修改已推翻，见 §12.9：改为与妊娠/孵化加速药同构的 **当前阶段剩余天数 × 30%**（剩余 = 阶段阈值 − 自然天数 − 已累计加速），可叠加，夹取到进入下一阶段的前一天，不足 1 天视为极限；且对婴儿/幼女/萝莉三个阶段通用】
- **加速同时影响后续阶段**：`growth_acceleration_days` 参与 `check_grow_to_loli`（270）与 `check_grow_to_girl`（450）的换算——即"成长被整体提前 N 天"，与 born_time 拨前的语义一致，也与用户"加速婴儿的成长"一致；不做"只提前婴儿期"的特殊处理（否则幼女期反而被拉长）。【已确认 §11-1（2026-08-28）】
- **生效时机**：用药当晚睡觉结算时有效天数 = 89 不触发；次日睡觉 = 90 触发育儿完成事件（§2.3 推进时机）。用药时 WaitDraw 提示："本次加速 X 天，{婴儿名}预计将在 {季月名D日} 成长为幼女"（预计日 = `game_time.get_sub_date(day=90 − growth_acceleration_days, old_date=born_time)`，自动归并到四季月，月份用 `game_time.get_month_text` 的春夏秋冬月名；与 pregnancy_panel 的"预计完成育儿"口径同步修改。【第 1 次修改：原写法 `born_time + timedelta(...)` 已废除，见 §12.5】）。

### 3.2 多婴儿改造：`check_rearing_complete` 改为逐婴儿驱动【关键决策，已确认方案 A（§11-2，2026-08-28）】

现状只处理 `child_id_list[-1]`（§2.5），与"选择对哪个婴儿使用"冲突。两个方案：

| 方案 | 内容 | 取舍 |
| --- | --- | --- |
| **A（推荐）：逐婴儿结算** | `check_rearing_complete(mother_id)` 在母亲 talent24 时，遍历母亲 `child_id_list` 中 `talent[101]==1 and mother_id==母亲` 的全部婴儿，对 `get_child_grow_day >= 90` 的**每一个**执行既有的成长块（get_new_character / 101→102 / flag 7 / work_type 152 / 二段行为 / 文案）；处理完后**若母亲名下再无婴儿**才清 24/27 并打印育儿完成文案，否则只打印孩子成长文案并保留育儿状态。`check_rearing` 保持看最新婴儿（产后→育儿只与最近一次生产有关）。 | 采用：顺带修复 §2.5 的既有限制，任何婴儿都能被加速并如期成长 |
| B：维持只看最后一个婴儿 | 成长加速药限定只能对 `child_id_list[-1]` 且它是婴儿时使用，选婴儿步骤退化为提示 | 弃选：需求明确要"选择对哪个婴儿"；且旧婴儿永远长不大的限制仍在 |

- 同步修改 `pregnancy_panel.py:115-122` 育儿阶段文案：改为列出全部婴儿及各自预计完成日（或取最早一个），不再只看 `[-1]`。
- 风险：成长块内的 `second_behavior.character_get_second_behavior(mother, "rearing_complete")` 与 `talk.must_show_talk_check` 每个婴儿各触发一次（同晚多婴儿同时到期的极端情况），可接受；单元测试覆盖"双婴儿其中一个到期"。

### 3.3 成长停滞/继续的状态存储与挂钩位置

- **状态存储【已确认：可见素质（§11-3，2026-08-28）】**：新增素质 **id 28【成长停滞】**（Talent.csv `28,0,成长停滞,0,<描述>`，Talent_type 0、不可遗传，与 25 假孕孕肚同组；ArkEditor 副本 info 短版）。成长停滞药 `talent[28]=1`、成长继续药 `talent[28]=0`，赋予/移除提示照泌乳药先例（"{0}获得了【成长停滞】"/"{0}失去了【成长停滞】"）。弃选 v1 的 `growth_stop_flag` 字段方案（用户希望在素质列表可见）。
- **挂钩位置**：`check_grow_to_loli` 与 `check_grow_to_girl` 的 if 条件追加 `and not character_data.talent[28]`（§2.3 表第 3/4 行）。天数照常累计（born_time/加速字段不动），解除后下一次睡觉结算若已过阈值立即成长——完全符合"成长天数依然在正常计算，只是跳过成长的事件结算"。
- 不挂到 `check_rearing_complete`：停滞药条件限定幼女/萝莉，婴儿不可能持有 talent28。
- **显示**：素质列表自动显示【成长停滞】；body_info_panel 在 talent25 假孕行（[:186-187](Script/UI/Panel/body_info_panel.py#L186)）附近加一行"  正处于[成长停滞]状态，不会成长到下一阶段"（可选，实施时定）。
- 成长为少女（104）后素质已无意义；成长继续药只在幼女/萝莉阶段可用；在 `check_grow_to_girl` 成长块内顺手 `talent[28]=0`（并打印"失去了[成长停滞]"）保持素质列表干净。
- 旧存档/多周目：新素质 id 由既有素质补齐机制自动处理（[old_chara_to_new.py:1368-1371](Script/Core/old_chara_to_new.py#L1368) 对配置表新增素质补 0，plan_14 §2.9 已核实），无需回填代码。

### 3.4 三种药物的道具注册与使用条件

**CSV 新行**（level 3 / price 200 照 31~38 先例；描述为草案，实施时定稿）：

`data/csv/Item.csv`（插在 38 假孕终止药行后）：

```csv
39,成长加速药,Drug,npc_use,3,200,0,-1,在育儿室使用，让对方正在照顾的一名婴儿大幅加快成长，直接成长到即将成为幼女的前一天，需要指定作用的婴儿
40,成长停滞药,Drug,npc_use,3,200,0,-1,使用后让处于幼女或萝莉阶段的女儿停止成长，身体会一直保持在当前阶段，直到使用成长继续药为止
41,成长继续药,Drug,npc_use,3,200,0,-1,使用后解除女儿身上成长停滞药的效果，让她重新开始正常成长
```

`data/csv/Gift_Items.csv`（插在 38 行后）：

```csv
39,39,11,0,成长加速药
40,40,11,0,成长停滞药
41,41,11,0,成长继续药
```

**使用条件（`is_drug_effective` 新增 3 个 elif，全部送出前拦截、不消耗道具）**：

| 药物 | 有效条件（按序判定） | 无效提示（草案） |
| --- | --- | --- |
| 39 成长加速药 | 【第 5 次修改后】目标是幼女/萝莉阶段的女儿（`is_growth_drug_self_target`）→ 对本人生效，只需 `get_child_growth_acceleration_amount > 0`（不要求育儿室）；否则视为母亲：① `handle_in_nursery(0)`；② `get_accelerable_babies(t_id)` 非空（婴儿且剂量 > 0）。原口径：~~① 玩家在育儿室；② 母亲名下有 `grow_day < 89` 的婴儿~~ | "{0}已经快要成长到下一阶段了，无法使用成长加速药" / "只能在育儿室对母亲使用成长加速药" / "{0}没有正在婴儿期的孩子，无法使用成长加速药" / "{0}的孩子都已经快要长成幼女了，无法使用成长加速药" |
| 40 成长停滞药 | ① `relationship.father_id == 0`；② `talent[102] or talent[103]`；③ `talent[28] == 0` | "{0}不是博士的女儿，无法使用成长停滞药" / "{0}不处于幼女或萝莉阶段，无法使用成长停滞药" / "{0}已经处于【成长停滞】状态了，无法重复使用成长停滞药" |
| 41 成长继续药 | ① 同上；② 同上；③ `talent[28] == 1` | 前两条同上 / "{0}没有处于【成长停滞】状态，不需要使用成长继续药" |

**效果实现（`handle_drug_use_effect` 新增 3 个 elif）**：

- 39：读玩家 `behavior.gift_child_id`（§3.5）并重置 −1；兜底校验该 id 在目标 `child_id_list` 中且 `talent[101]==1`（否则打印"选中的婴儿已经不在婴儿期，药物没有产生效果"）；`add_day = 89 − get_child_grow_day(child_id)`，`>0` 时 `child.pregnancy.growth_acceleration_days += add_day`，打印"本次加速{X}天，{婴儿名}预计将在{M月D日}成长为幼女"。
- 40：`character_data.talent[28] = 1`，打印"{0}获得了【成长停滞】，在使用成长继续药之前她会一直保持在[幼女/萝莉]阶段"（照泌乳药 :61-63 先例）。
- 41：`character_data.talent[28] = 0`，打印"{0}失去了【成长停滞】，她会继续正常成长"。
- 三个分支只做数据结算与系统提示，不触发二段行为；口上由 give_gift 常规链路按 `CVP_A1_Gift|39/40/41` 前提自动选取（§3.6）。

### 3.5 成长加速药的选婴儿交互（照 §2.2 选卵先例）

- 选点：`select_gift` 内、`check_gift_available` 通过后、行为触发前，`gift_id == 39` 时调用新方法 `select_target_baby()`（结构照抄 `select_target_egg` :247-292）：
  1. 列表来源 `get_accelerable_babies(target_id)`（§5.3）；
  2. 仅一名可加速婴儿时直接写 `behavior.gift_child_id` 跳过选择；
  3. 多名时 `TitleLineDraw(_("选择要加速成长的婴儿"))` + 每名一行 `LeftButton`：`[{名字}] 出生第{X}天（已加速{Y}天，预计{M月D日}成长为幼女）` + `[返回]`（取消送礼）。
- `CharacterBehavior` 新增 `gift_child_id: int = -1`（挂 [game_type.py:1064](Script/Core/game_type.py#L1064) `gift_egg_id` 旁），结算 `getattr(..., "gift_child_id", -1)` 兜底。

### 3.6 三种药物的专用送礼口上（照 plan_14 v4 口径）

新建 3 个口上文件于 `data/talk/daily/gift/`，cid 从 1000 起、adv_id=0、behavior_id=`give_gift`，每前提组合 5 条，按 §2.8 的 prompt 格式撰写：

| 文件 | 药物 | 前提组合 | 条数 | 文案题材 |
| --- | --- | --- | --- | --- |
| `give_gift_growth_accelerate.csv` | 39 | 照 36 号先例 6 组：`CVP_A1_Gift|39_G_0` 基础 / `&CVP_A2_T|104_E_1` / `|105` / `|106` / `|107` / `&target_is_player_daughter`【第 5 次修改：6 组均追加 `&t_rearing_1`；另加女儿本人服用分支 `&CVP_A2_T|102_E_1` / `|103_E_1` 各 5 条，合计 40 条，见 §12.9】 | 6×5=30（+10） | 在育儿室递药给母亲 → 母亲接过，抱起摇篮里的婴儿、把药液一点点喂进婴儿口中（用户口径：**药递给母亲、母亲给婴儿服用**）→ 母亲看着婴儿身体微微发热、小手小脚躁动的悸动与复杂心绪（期待/不舍/隐秘的兴奋） |
| `give_gift_growth_stop.csv` | 40 | 目标是幼女/萝莉女儿，2 组：`CVP_A1_Gift|40_G_0&CVP_A2_T|102_E_1` / `&CVP_A2_T|103_E_1` | 2×5=10 | 女儿从父亲手中接过药、乖乖喝下 → 身体里那股向上生长的暖流缓缓停住、被定格在当前娇小身躯里的奇妙感受（幼女写懵懂，萝莉写朦胧的自觉与羞怯） |
| `give_gift_growth_resume.csv` | 41 | 同上 2 组（`|41_G_0`） | 2×5=10 | 女儿喝下药后，停滞的成长重新苏醒、身体深处微微发热的鼓动与对"继续长大"的期待/不安 |

- 39 号的口上目标是母亲，外表年龄分支沿用先例；40/41 的目标必然是女儿且为幼女/萝莉，故不做外表年龄分支、不加 `target_is_player_daughter`（条件已蕴含）。
- **成长停滞前提组【已确认：本期实装（§11-4，2026-08-28）】**：供口上/事件作者区分停滞状态，全部照 FAKE_INFLATION 先例（§2.9），函数放在 [handle_premise_other.py:2763](Script/Design/handle_premise/handle_premise_other.py#L2763) 假孕组旁：

| 前提 cid | 常量名 | 判定 | ArkEditor 行（分组"素质_妊娠"，插在 [:1169](tools/ArkEditor/csv/Premise.csv#L1169) 后） |
| --- | --- | --- | --- |
| `growth_stop_0` | `GROWTH_STOP_0` | 自己 `talent[28]==0` | `growth_stop_0,GROWTH_STOP_0,素质_妊娠,自己成长停滞==0` |
| `growth_stop_1` | `GROWTH_STOP_1` | 自己 `talent[28]==1` | `growth_stop_1,GROWTH_STOP_1,素质_妊娠,自己成长停滞==1` |
| `t_growth_stop_0` | `T_GROWTH_STOP_0` | 交互对象 `talent[28]==0` | `t_growth_stop_0,T_GROWTH_STOP_0,素质_妊娠,交互对象成长停滞==0` |
| `t_growth_stop_1` | `T_GROWTH_STOP_1` | 交互对象 `talent[28]==1` | `t_growth_stop_1,T_GROWTH_STOP_1,素质_妊娠,交互对象成长停滞==1` |

  常量放 [constant_promise.py:2318](Script/Core/constant_promise.py#L2318) `T_FAKE_INFLATION_1` 之后。口上侧亦可直接用参数化 token `CVP_A2_T|28_E_1`，本前提组是给 ArkEditor 作者的可读别名。

## 4. 数据结构设计（权威定义）

`class PREGNANCY`（[game_type.py:310](Script/Core/game_type.py#L310)，在 `acceleration_days` 之后）新增：

```python
self.growth_acceleration_days: float = 0.0   # 第 5 次修改：由 int 改为 float 累计（每次为剩余天数的 30%），天数换算时向下取整
""" 成长加速药对本角色（作为孩子）累计的额外成长天数：
    参与婴儿→幼女(90)/幼女→萝莉(270)/萝莉→少女(450)的天数换算与面板预计日期；
    由 get_child_grow_day 统一读取；出生时为0，不清零（成长为少女后不再消费） """
```

成长停滞状态不新增字段，由素质 **talent[28]【成长停滞】** 承载（§3.3）：Talent.csv 新行 `28,0,成长停滞,0,因药物而停止了身体的成长，会一直保持在当前的幼女或萝莉阶段，直到使用成长继续药为止`（描述草案）。

`class CharacterBehavior`（[game_type.py:1064](Script/Core/game_type.py#L1064) 旁）新增：

```python
self.gift_child_id: int = -1
""" 前提结算用:成长加速药选中的目标婴儿角色id（-1为未选择，结算消费后重置） """
```

- 旧存档回填（[save_handle.py:285-287](Script/Core/save_handle.py#L285) 段后追加）：`pregnancy` 缺 `growth_acceleration_days` 补 0。behavior 字段 `getattr` 兜底不回填；素质 28 由既有素质补齐机制处理（§3.3）。

## 5. 详细改动步骤

> ⚠️ 道具编号 39~41 实施时现场再核对一次空闲。

### 5.1 CSV 数据（data/csv/Item.csv、Gift_Items.csv、Talent.csv）

- Item.csv 在 38 行后插入 §3.4 的 3 行；Gift_Items.csv 在 38 行后插入 3 行；Talent.csv 在 27 泌乳行后插入 `28,0,成长停滞,0,<§4 描述草案>`。
- 同步 ArkEditor 副本 `tools/ArkEditor/csv/Item.csv`、`Gift_Items.csv`、`Talent.csv`（info 短版）。

### 5.2 数据结构与存档（Script/Core/game_type.py、save_handle.py）

- 按 §4 新增 2 处字段 docstring（`growth_acceleration_days`、`gift_child_id`）；save_handle 回填段追加 `growth_acceleration_days`。

### 5.3 妊娠结算（Script/System/Pregnancy_System/pregnancy_handle.py）

- 新增 `get_child_grow_day(child_id) -> int`（born_time 天数 + `getattr(pregnancy, "growth_acceleration_days", 0)`）与 `get_child_growth_acceleration_amount(child_id) -> int`（= `max(0, 89 − grow_day)`）、`get_accelerable_babies(mother_id) -> list[int]`（母亲 `child_id_list` 中 `talent[101]==1 and mother_id==母亲 and amount>0`，供 is_drug_effective 与选婴儿列表共用）。
- `check_rearing`（:335-336）：裸计算改 helper（保持看最新婴儿）。
- `check_rearing_complete`（:355-394）：按 §3.2 方案 A 重写为逐婴儿循环；成长块提取为内部函数 `_settle_baby_grow_up(mother_id, child_id)`；母亲名下无婴儿时才清 24/27。
- `check_grow_to_loli`（:397-426）/ `check_grow_to_girl`（:429-460）：裸计算改 helper；if 条件追加 `and not character_data.talent[28]`；`check_grow_to_girl` 成长块内 `talent[28] = 0`（如原为 1 则附打印"失去了[成长停滞]"）。

### 5.4 礼物面板（Script/UI/Panel/gift_panel.py）

- `is_drug_effective`：新增 39/40/41 分支（§3.4；`handle_premise` 已在模块顶部导入，`handle_in_nursery(0)` 直接可用；妊娠模块函数内 import 照 35~38 先例）。
- `select_gift`：`gift_id == 39` 时插入 `select_target_baby()`（§3.5）；新增 `select_target_baby` / `select_child_id` 两个方法（照 :247-301）。
- `handle_drug_use_effect`：新增 3 个效果分支（§3.4）。

### 5.5 显示面板（pregnancy_panel.py、body_info_panel.py、debug_panel.py）

- pregnancy_panel `get_stage_info_text` 育儿阶段（:115-122）：改为遍历母亲全部婴儿，预计日 = `game_time.get_sub_date(day=90 − growth_acceleration_days, old_date=born_time)`（多婴儿列出最早的一个或逐个列出，实施时定）。【第 1 次修改：原 `timedelta` 写法已废除，见 §12.5】
- body_info_panel：talent28 角色加一行状态描述（§3.3，可选）。
- 可选：debug 面板 `[004]` 行旁显示 `growth_acceleration_days`（非必需，实施时定）。

### 5.6 专用送礼口上（data/talk/daily/gift/ 新增 3 文件）

- 按 §3.6 表新建 3 个文件（表头 5 行照既有礼物口上文件；无 BOM、CRLF；文本内不得出现 ASCII 逗号），文本按 §2.8 prompt 要求撰写。

### 5.7 成长停滞前提组（Script/Core/constant_promise.py、handle_premise_other.py、ArkEditor Premise.csv）

- `constant_promise.Premise` 在 [:2318](Script/Core/constant_promise.py#L2318) `T_FAKE_INFLATION_1` 后新增 §3.6 表的 4 个常量（带中文 docstring）。
- `handle_premise_other.py` 在假孕前提组（[:2763](Script/Design/handle_premise/handle_premise_other.py#L2763) 段）后新增 4 个函数，判 `talent[28]`。
- `tools/ArkEditor/csv/Premise.csv` 在 [:1169](tools/ArkEditor/csv/Premise.csv#L1169) 后插入 4 行（分组"素质_妊娠"）。

## 6. 构建与缓存

```bash
# 本机必须用 conda 解释器（裸 python 是 Store 空壳别名）
.conda\python.exe buildconfig.py   # 改了 Item/Gift_Items 两张 CSV + 3 个口上 CSV，必须全量重建（talk 数据在增量构建下会被跳过）
.conda\python.exe buildpo.py       # 新增道具名/描述/提示文案词条
.conda\python.exe buildmo.py
```

实施完成并通过验证后，按 `update-changelog` 体例把三种药物登记进 update.log（新增类条目；§3.2 的多婴儿修复另记一条修正类）。

## 7. 验证清单

### 7.1 单元测试（实施方执行，headless-game-test 方式）

- [ ] `get_child_grow_day`：无加速 = 自然天数；加速 N 后 = 自然 + N。
- [ ] 加速剂量：出生第 10 天的婴儿 `amount == 79`；第 89 天及以后 `amount == 0` 且 `is_drug_effective(39)` 返回 False（道具不消耗）。
- [ ] 生效时序：用药后当晚 `check_rearing_complete` 不触发（有效 89），把 game_time +1 天后触发：孩子 101→102、work_type 152、进入 npc_id_got；母亲 24→0、27→0。
- [ ] 多婴儿：母亲两名婴儿只对**非最后一个**用药 → 到期时它成长、另一名仍为婴儿、母亲保留 24/27；第二名到期后母亲才清 24/27。
- [ ] 加速影响后续阶段：加速 79 天的孩子在自然 191 天（有效 270）时 `check_grow_to_loli` 触发。
- [ ] 使用条件矩阵：39 玩家不在育儿室 / 目标无婴儿 → 拦截；40 对非女儿 / 少女 / 已停滞 → 拦截；41 对未停滞 → 拦截；正常路径三药均通过。
- [ ] 停滞：`talent[28]=1` 的幼女在有效 300 天时 `check_grow_to_loli` 不触发、天数照常；继续药（28→0）后下一次判定立即成长；萝莉→少女同理，成长为少女后 talent28 被清 0。
- [ ] 前提组：talent28==1 的角色 `GROWTH_STOP_1`/`T_GROWTH_STOP_1` 返回 1、`_0` 返回 0；==0 时反之；4 个前提均注册进 config 且 ArkEditor Premise.csv 行齐备。
- [ ] 选婴儿字段：`gift_child_id` 写入 → 结算消费 → 重置 −1；选中的孩子结算前已非婴儿时兜底提示不崩溃。
- [ ] 旧存档兼容：缺 `growth_acceleration_days` 的 PREGNANCY 对象经 save_handle 回填后字段就位；缺 `gift_child_id` 的 behavior `getattr` 兜底；旧存档角色素质表缺 28 时经素质补齐机制补 0。
- [ ] 送礼口上：3 个口上文件编译进 config_talk 且条数正确（30/10/10）；`CVP_A1_Gift|39_G_0` 在 `behavior.gift_id==39` 时返回 1。
- [ ] grep `born_time).days` 无裸计算残留（§2.10）。
- [ ] `buildconfig.py` 全量重建无报错。

### 7.2 游戏内整体测试（由用户执行）

- [ ] 商店可购买 3 种新药；礼物面板药物折叠组内正常显示/灰显。
- [ ] 在育儿室对有婴儿的母亲送成长加速药：多婴儿时选婴儿列表正确、单婴儿跳过；先弹送礼口上再显示系统提示；睡两晚后触发"从[婴儿]成长为了[幼女]"事件；总览面板预计日期同步。
- [ ] 在非育儿室送成长加速药被拦截且不消耗道具。
- [ ] 对幼女/萝莉女儿送成长停滞药后，跨过 270/450 天不成长；送成长继续药后下一晚成长；身体信息面板状态行正确。
- [ ] Tk 与 Web 两种绘制模式均正常；旧存档载入不报错。

## 8. 风险与回滚

| 风险 | 说明 | 对策 |
| --- | --- | --- |
| 多婴儿改造回归 | `check_rearing_complete` 重写影响所有正常育儿流程 | 成长块逻辑原样提取不改内容；单测覆盖单婴儿（现状路径）与双婴儿；§7.2 用户验收 |
| 天数注入漏点 | 加速只改部分换算点导致结算与显示不一致 | §2.10 清单穷举 5 处，统一 helper，实施后 grep 复核 |
| 一剂药直接越过阈值 | 加速量算错导致当晚就成长 | 剂量固定 `89 − grow_day`，单测断言当晚不触发/次日触发 |
| 停滞素质残留 | 少女阶段仍带【成长停滞】 | 成长为少女时清 0；少女阶段无消费方，残留亦无副作用 |
| 素质编号冲突 | 28 被并行开发占用 | 实施时现场核对（与道具 39~41 同） |
| 结算期目标婴儿失效 | 选婴儿后、结算前婴儿状态改变（同回合不可能，仅理论） | 结算内兜底校验 |
| 存档兼容 | 旧存档缺新字段 | save_handle 回填 + getattr 兜底 + 单测构造缺字段对象 |
| 编号冲突 | 39~41 被并行开发占用 | 实施时现场核对 |

**回滚**：CSV 行删除 + gift_panel 分支/方法删除 + pregnancy_handle 三函数恢复（`check_rearing_complete` 建议以 git 恢复整函数）+ 口上文件删除；`PREGNANCY` 新字段与回填代码可保留（存档中为普通数值，无害）；回滚后重跑 buildconfig。

## 9. 改动文件清单

| 文件 | 类型 | 改动 |
| --- | --- | --- |
| `data/csv/Item.csv` | 修改 | 新增道具 39~41 三行 |
| `data/csv/Gift_Items.csv` | 修改 | 新增礼物 39~41 三行（type 11） |
| `data/csv/Talent.csv` | 修改 | 新增素质 28【成长停滞】 |
| `Script/Core/game_type.py` | 修改 | PREGNANCY.growth_acceleration_days、behavior.gift_child_id |
| `Script/Core/save_handle.py` | 修改 | 回填 growth_acceleration_days |
| `Script/Core/constant_promise.py` | 修改 | 新增 GROWTH_STOP_0/1、T_GROWTH_STOP_0/1 四个前提常量 |
| `Script/Design/handle_premise/handle_premise_other.py` | 修改 | 新增 4 个成长停滞前提函数 |
| `Script/System/Pregnancy_System/pregnancy_handle.py` | 修改 | 成长天数 helper、剂量/可加速婴儿筛选函数、check_rearing 走 helper、check_rearing_complete 逐婴儿重写、loli/girl 停滞守卫 |
| `Script/UI/Panel/gift_panel.py` | 修改 | is_drug_effective / select_gift 选婴儿 / handle_drug_use_effect 各 3 分支 + 2 个新方法 |
| `Script/System/Pregnancy_System/pregnancy_panel.py` | 修改 | 育儿阶段预计日期扣减加速、多婴儿展示 |
| `Script/UI/Panel/body_info_panel.py` | 可选修改 | 成长停滞状态行 |
| `Script/UI/Panel/debug_panel.py` | 可选修改 | 显示成长加速/停滞值 |
| `data/talk/daily/gift/give_gift_growth_accelerate.csv` | 新增 | 成长加速药送礼口上（6 组 × 5） |
| `data/talk/daily/gift/give_gift_growth_stop.csv` | 新增 | 成长停滞药送礼口上（幼女/萝莉 × 5） |
| `data/talk/daily/gift/give_gift_growth_resume.csv` | 新增 | 成长继续药送礼口上（幼女/萝莉 × 5） |
| `tools/ArkEditor/csv/Item.csv` / `Gift_Items.csv` / `Talent.csv` / `Premise.csv` | 修改 | 副本同步（Premise 含 4 新行） |

**未改动**：Behavior_Data / Behavior_Effect / 二段行为常量（复用 give_gift 口上链路，成长事件沿用 1319~1321）；InstructConfig（送礼指令全链复用）；`handle_give_gift_add_adjust` 结算（新药沿用挂接）；h_item_shop_panel（自动收录）；`born_new_character` / `born_event_panel`（出生流程不变）；`check_grow_to_*` 的 270/450 阈值与 `chest_grow`/`body_part_grow`；old_chara_to_new（pregnancy 整体迁移自动兼容）。

## 10. 不在本 Plan 范围

- 90/270/450 天基础成长数值的调整；成长加速药的可叠加/百分比剂量（本需求为一次到位）。
- 让婴儿上线/进入场景（§2.4 现状维持，"在育儿室"只判玩家位置）。
- 成长停滞状态的日常风味口上/事件；§3.6 可选前提组只在用户要求时加。
- 少女之后的"外表年龄"变化（那是 31/32 号药的领域）。
- 成长事件（rearing_complete / child_to_loli / loli_to_girl）本身的口上扩充。

## 11. 口径确认记录（2026-08-28，全部已确认）

| # | 问题 | 用户确认结果 | 方案落点 |
| --- | --- | --- | --- |
| 1 | 成长加速是否同时提前后续的幼女→萝莉（270）/萝莉→少女（450）阶段？ | **是，整体提前 N 天**（`growth_acceleration_days` 参与三个阶段的换算） | §3.1、§5.3 |
| 2 | 是否把 `check_rearing_complete` 改为逐婴儿结算（顺带修复"非最后一个婴儿永远长不大"）？ | **是（方案 A）** | §3.2、§5.3 |
| 3 | 成长停滞状态用字段还是可见素质？ | **新增可见素质【成长停滞】（talent 28）**，v1 的 `growth_stop_flag` 字段方案作废 | §3.3、§4、§5.1 |
| 4 | 是否本期就加 `growth_stop_0/1`、`t_growth_stop_0/1` 前提组？ | **加**（4 个前提 + ArkEditor Premise.csv 同步） | §3.6、§5.7 |
| 5 | 三种新药 level/price 照 31~38 先例？ | **是，level 3 / price 200** | §3.4 |

以下小项采用推荐默认（实施时可微调，无需再确认）：目标仅一名可加速婴儿时跳过选择；口上分支组合照 §3.6 表；成长为少女时清 talent28；body_info/debug 面板的附加显示为可选项。

## 12. 执行记录（2026-08-29）

### 12.1 实际改动

§9 清单逐文件核对，全部按计划落地，无遗漏文件、无计划外文件。编号类实际分配值与建议值全部一致（实施时已现场核对空闲：Item/Gift_Items 38→50 之间、Talent 27→31 之间）：

| 编号类 | 实际分配 |
| --- | --- |
| 道具/礼物 cid | 39 成长加速药 / 40 成长停滞药 / 41 成长继续药（Item.csv 与 Gift_Items.csv 同号，type=11，level 3 / price 200） |
| 素质 cid | 28 成长停滞（type 0，不可遗传） |
| 前提 | `growth_stop_0/1`、`t_growth_stop_0/1`（常量紧接 `T_FAKE_INFLATION_1`；函数紧接 `handle_t_fake_inflation_1`；ArkEditor Premise.csv 分组"素质_妊娠"，插在 `t_fake_inflation_1` 后） |

逐文件落点：

| 文件 | 实际改动 |
| --- | --- |
| `data/csv/Item.csv` / `Gift_Items.csv` / `Talent.csv` + ArkEditor 三副本 | 各插入 3/3/1 行（CRLF、无 BOM，按行前缀脚本插入） |
| `tools/ArkEditor/csv/Premise.csv` | 4 行成长停滞前提 |
| `Script/Core/game_type.py` | `PREGNANCY.growth_acceleration_days: int = 0`（紧接 `acceleration_days`）；`CharacterBehavior.gift_child_id: int = -1`（紧接 `gift_egg_id`） |
| `Script/Core/save_handle.py` | `_normalize_loaded_save_paths` 回填段追加 `growth_acceleration_days` |
| `Script/Core/constant_promise.py` / `handle_premise_other.py` | 4 常量 + 4 前提函数 |
| `pregnancy_handle.py` | 新增常量 `REARING_COMPLETE_DAY=90 / GROW_TO_LOLI_DAY=270 / GROW_TO_GIRL_DAY=450` 与 helper `get_child_grow_day` / `get_child_growth_acceleration_amount` / `get_baby_id_list` / `get_accelerable_babies`（放在 `get_pregnancy_acceleration_amount` 之后）；`check_rearing` 改走 helper；`check_rearing_complete` 重写为逐婴儿循环，成长块提取为 `_settle_baby_grow_up(mother_id, child_id)`；`check_grow_to_loli/girl` 加 `not talent[28]` 守卫并改走 helper，成长为少女时清 talent28 |
| `gift_panel.py` | `handle_drug_use_effect` 39/40/41 三分支；`select_gift` 的 39 选婴儿钩子；新增 `select_target_baby` / `select_child_id`；`is_drug_effective` 39/40/41 三分支 |
| `pregnancy_panel.py` | 育儿阶段文案改为遍历 `get_baby_id_list` 逐个列出"名字（预计 X 长大）"，扣减加速天数（函数内 import pregnancy_handle 防循环导入） |
| `data/talk/daily/gift/give_gift_growth_accelerate.csv` / `_stop.csv` / `_resume.csv` | 30 / 10 / 10 条，前提组合与 §3.6 表完全一致 |
| `update.log` | 新增 3 条（怀孕×2、口上×1）+ 修正 1 条（多婴儿成长） |

### 12.2 与计划的偏差

1. **`get_baby_id_list` 额外要求 `child.relationship.mother_id == 母亲`**：防止 `child_id_list` 中混入非本人所生的孩子（博士的 `child_id_list` 汇总全部孩子）——计划 §3.2 已写明此条件，此处只是记录实际落点。
2. **口上字数**：单条 505~609 个汉字，低于 prompt 的 650 下限，但**高于** plan_14 落地的三个先例文件（424~529 / 438~710 / 287~648，平均 447~501），与仓库现有水平一致，按 plan_14 v4 "接近即可"口径放宽。
3. **body_info_panel 成长停滞状态行、debug 面板显示**：计划标为可选，本次未实装（素质列表已能看到【成长停滞】）。
4. **buildpo / buildmo** 未执行（po 文件当前工作区已有大量未提交改动，照 plan_14 先例留给用户统一处理）。
5. 已知限制（记录于此，非缺陷）：成长加速药"在育儿室"只判玩家位置（婴儿是离线角色，不在任何场景，§2.4）。

### 12.3 测试结果（headless 模式 A，`scratchpad/test_plan17.py`，68 项全部通过）

对照 §7.1 逐项：

- [x] 注册：道具 39~41、礼物 39~41（type 11）、素质 28、4 个前提均进入 config/运行时；口上 30/10/10 条；`CVP_A1_Gift|39_G_0` 在 gift_id==39 时返回 1、否则 0。
- [x] `get_child_grow_day`：无加速=自然天数；加速 N 后=自然+N。
- [x] 剂量：出生第 10 天 `amount==79`；第 89 天 `amount==0` 且 `is_drug_effective(39)` 拦截。
- [x] 生效时序：有效 89 天当晚 `check_rearing_complete` 不触发；+1 天后触发（101→102、work_type 152、进入 npc_id_got）。
- [x] 多婴儿：三名婴儿中两名到期各自成长、第三名仍为婴儿、母亲保留 24/27 并提示"还有其他婴儿"；最后一名成长后母亲清 24/27 并提示"完成了育儿行动"。
- [x] 加速影响后续阶段：加速 79 天的幼女在自然 191 天成长为萝莉。
- [x] 使用条件矩阵：39 不在育儿室/无婴儿/全部到 89 天 → 拦截；40 非女儿/少女/已停滞 → 拦截；41 未停滞 → 拦截；正常路径三药均通过。
- [x] 停滞：talent28=1 的幼女 300 天不成长、天数照常累计；清 0 后立即成长；萝莉→少女同理，成长后 talent28 被清 0。
- [x] 前提组：`growth_stop_0/1`、`t_growth_stop_0/1` 与参数化 `CVP_A2_T|28_E_1` 判定正确。
- [x] 选婴儿：单一可加速婴儿跳过选择直接写入；多婴儿进入选择流程，`select_child_id` 写入 → 结算消费 → 重置 −1；选中的孩子非婴儿时兜底提示不崩溃。
- [x] 旧存档：缺 `growth_acceleration_days` 经 `_normalize_loaded_save_paths` 回填为 0；behavior 缺 `gift_child_id` 时 getattr 兜底。
- [x] 面板：育儿阶段文案含婴儿名与预计日。
- [x] grep `born_time).days` 仅剩 helper 内 1 处；`buildconfig.py` 全量重建无报错。

测试 fixture 备注：`get_new_character` 的上线链需要完整的 `rhodes_island`（娱乐安排等），测试中以"仅登记 npc_id_got"的 stub 替代；`chest_grow` 需要孩子持有胸部素质（121~125）、成长文案需要 `rhodes_island.all_work_npc_set[151]`——均为既有代码的 fixture 要求，非本次改动引入。

### 12.4 尚未覆盖的验证（留给用户，§7.2）

- [ ] 商店购买与礼物面板显示；Tk/Web 两种模式下的选婴儿列表交互。
- [ ] 游戏内完整流程：育儿室送成长加速药 → 口上 → 提示 → 睡两晚触发成长事件；总览面板预计日。
- [ ] 成长停滞/继续药的游戏内流程与素质列表显示。
- [ ] 旧存档载入；`buildpo` / `buildmo` 后的翻译词条。

### 12.5 第 1 次修改记录（2026-08-29）：时间计算复用 `game_time` 既有函数 + 季月名显示

用户验收要求：生育系统里临时写的时间算式改为复用 [game_time.py](Script/Design/game_time.py) 的既有函数——日期加减一律 `get_sub_date(day=N, old_date=X)`（自动归并到游戏的 3/6/9/12 四季月，避免 `timedelta` 直接相加得到 4 月、5 月等游戏中不存在的月份），天数统计一律 `count_day_for_datetime(start, end)`；所有显示"X 月"的地方改用春夏秋冬月名；`get_month_text` 对非四季月增加兜底（5 月按夏显示）。

| 文件 | 改动 |
| --- | --- |
| `Script/Design/game_time.py` | 新增 `get_season_month(month)`（1,2→3 / 4,5→6 / 7,8→9 / 10,11→12，规则与 `get_sub_date` 一致）；`get_month_text` 经其兜底后取"春/夏/秋/冬"；`get_date_text` / `get_date_until_day` 删除各自复制的 if 链改为调用 `get_month_text`；**`get_sub_date` 归并月份时把日期夹取到目标季月的最后一天**（原代码 5/31、7/31、8/31 归并到 30 天的 6/9 月会 `ValueError`，属既有 BUG，本次回归测试暴露后一并修复，`import calendar`） |
| `pregnancy_handle.py` | `get_pregnancy_past_day` / `get_child_grow_day` 改用 `count_day_for_datetime` |
| `egg_handle.py` | `get_hatch_day` 改用 `count_day_for_datetime`；`get_identifiable_eggs` 改用 `count_day_for_datetime(lay_time 截到0点, game_time 截到0点)`（用 `replace(hour=0, minute=0, …)` 而非 `.date()`，既保留按日历日语义又满足函数的 `datetime` 类型标注）；补 `game_time` 导入 |
| `pregnancy_panel.py` | `get_date_text` 改为 `game_time.get_month_text(t) + 月 + 日`（"春月5日"）；预计妊娠/临盆/破壳/长大四处改 `get_sub_date`；补 `game_time` 导入 |
| `gift_panel.py` | 妊娠/孵化/成长加速药三处提示与选卵/选婴儿两处列表文案改 `get_sub_date` + `pregnancy_panel.get_date_text`（占位符由 `{X}月{Y}日` 收为单个 `{X}`，翻译词条随之变化）；删除不再使用的 `import datetime` |
| `physical_check_and_manage.py` | 体检报告初吻时间的数字月改为 `game_time.get_month_text` |
| `update.log` | 修正段追加 1 条（预计日期显示不存在的月份） |
| `plan_14` §12.5 | 追加后续修改说明（其 §3.3/§5.7 所述 `timedelta` 写法已废除） |

- 连带修改了 plan_14 落地的 6 处日期计算（妊娠/孵化预计日 ×2 面板 + 提示 ×2 + 选卵列表 + `get_hatch_day`）。
- 回归测试：`scratchpad/test_plan17.py` 原 68 项 + 新增 25 项 = **93/93 全部通过**。新增覆盖：`get_month_text` 兜底（1/5/11 月→春/夏/冬，四季月不变）、`get_season_month` 全 12 月、`get_date_text`/`get_date_until_day` 输出与 5 月不报错、`pregnancy_panel.get_date_text`=="春月5日"、总览面板/三种加速药提示/选卵/选婴儿列表文案全部为季月名且无数字月、`get_sub_date` 5/31→6/30、7/31→9/30 与既有 5/30→6/30 一致、天数统计与改前一致、卵排出当天不可鉴定次日可鉴定。
- 实施后 grep：`Script/System/Pregnancy_System/`、`gift_panel.py` 中 `timedelta(` 与 `).days` 零残留。
- 遗留：提示文案词条变化需 `buildpo` / `buildmo`（与 §12.2-4 同）。

### 12.6 第 2 次修改记录（2026-08-29）：怀孕系统常量统一到 `pregnancy_constant.py`

用户验收要求：`Script/System/Pregnancy_System` 下各文件开头各自定义的模块级常量，改为由一个单独的常量文件统一定义、记录与管理，其他文件从该文件引用。

- 新建 [pregnancy_constant.py](Script/System/Pregnancy_System/pregnancy_constant.py)（只依赖 `get_text`，任何模块可在顶部直接导入，无循环导入风险），按 6 组收纳全部常量并带中文 docstring：
  1. 胎生孕程：`PREGNANCY_DAY=90`（新命名，原 `check_pregnancy` 字面量）、`PARTURIENT_DAY=260`、`PREGNANCY_TOTAL_DAY=270`、`POSTPARTUM_REST_DAY=2`（新命名，原 `check_rearing` 字面量）
  2. 加速药：`ACCELERATION_MAX_DAY=250`、`ACCELERATION_RATE=0.3`（新命名，原 `get_acceleration_amount` 字面量）
  3. 孩子成长：`REARING_COMPLETE_DAY=90`、`GROW_TO_LOLI_DAY=270`、`GROW_TO_GIRL_DAY=450`
  4. 卵生：`HATCH_TOTAL_DAY=265`、`TEND_EGGS_ENTERTAINMENT_ID=175`、`NURSERY_WORKER_WORK_ID=153`
  5. 总览面板阶段枚举 `STAGE_NONE~STAGE_REARING` 与 `STAGE_NAME_LIST`
  6. 谱系图排版 `UP_GEN=1`、`DOWN_GEN=2`、`GAP=2`
- 原定义处全部删除：`pregnancy_handle.py`（6 个）、`egg_handle.py`（3 个）、`pregnancy_panel.py`（9 个）、`family_tree_draw.py`（3 个）；四文件内的裸引用与跨文件引用（`egg_handle.HATCH_TOTAL_DAY`、`pregnancy_handle.REARING_COMPLETE_DAY`、`family_tree_draw.UP_GEN` 等）全部改为 `pregnancy_constant.X`；`check_pregnancy`/`check_near_born`/`check_born`/`check_rearing` 与 `pregnancy_panel` 预计妊娠/临盆日中的字面量 90/260/2 改为常量。
- 子系统外引用同步：`gift_panel.py`（5 处）、`handle_premise_other.py`（`TEND_EGGS_ENTERTAINMENT_ID`）、`StateMachine/default.py`（`NURSERY_WORKER_WORK_ID`）改为 `pregnancy_constant.X`，各自在模块顶部新增导入。
- 保留在原处：`family_tree_draw._LINK_CHAR_MAP`（私有的连线字形查表，属渲染实现细节而非可调常量）。
- 文档：`.github/prompts/数据处理工作流/妊娠系统.md` §1 目录树与外部调用点表已加入 `pregnancy_constant.py`。update.log 不登记（纯内部重构，玩家不可见）。
- 回归：`scratchpad/test_plan17.py`（引用改为 `pregnancy_constant.STAGE_*`）**93/93 通过**；grep 复核子系统内除 `_LINK_CHAR_MAP` 外无模块级常量定义残留、无裸常量引用残留。

### 12.7 第 3 次修改记录（2026-08-29）：谱系图改为上 2 代+下 4 代共 7 代；生育素质判定改走前提系统

**A. 谱系图代数**（用户要求：向上 2 代、向下 4 代，共 7 代）

- `pregnancy_constant.UP_GEN=2`、`DOWN_GEN=4`（原 1/2）。向下展开（`_build_blood_depth` / `_expand_person`）本就按 `DOWN_GEN` 参数化，改常量即生效。
- 向上攀升原先硬编码只取中心的父母一层（`_build_family_blocks` 只建一个父母夫妇框并对祖辈打省略号），改为**按 `UP_GEN` 逐代攀升**：每一代建一个夫妇框，子辈=当前血亲节点+其同辈（同辈不向下展开），再把该框包进左侧血亲的人物节点作为上一代夫妇框的子辈；到达 `UP_GEN` 或左侧血亲无在册父母时停止，并以 `left_more` 省略号标记未显示的祖辈。
- 新增 `_choose_couple_order(father_id, mother_id)`：左侧为向上继续攀升的血亲（有在册父母者优先，均有/均无时父在左）。因父本恒为玩家且玩家无父母，**母亲有父母时母亲居左、玩家名落在 ╤ 右侧**（原先父恒居左）——这是唯一的显示差异，plan_12 §3 "玩家名按父本位置重复"的口径仍成立，只是父本位置可在 ╤ 左或右。
- 中心无父母（如以玩家为中心）的分支不变。

**B. 生育素质判定前提化**（用户要求：`get_chara_pregnancy_stage()` 等处不再直接写素质编号，改调前提函数）

- 新增 2 个自身前提补齐缺口：`SELF_IS_BABY="baby_1"`（talent101）、`SELF_IS_LOLI="loli_1"`（talent103），实现放在 [handle_premise_talent.py](Script/Design/handle_premise/handle_premise_talent.py) `SELF_IS_CHILD` 旁；ArkEditor `Premise.csv` 在 `child_1` 后插两行（分组"属性_素质"）。
- 替换清单（只改读判定，`talent[x] = 1/0` 的写入不动）：

| 文件 | 原判定 → 前提函数 |
| --- | --- |
| `pregnancy_panel.get_chara_pregnancy_stage` | talent 20/21/22/23/24 → `handle_fertilization_1` / `handle_pregnancy_1` / `handle_parturient_1` / `handle_postpartum_1` / `handle_rearing_1`（模块顶部新增 `from Script.Design import handle_premise`） |
| `pregnancy_handle` | `get_baby_id_list` talent101 → `handle_self_is_baby`；`get_fertilization_rate` / `check_fertilization` talent25 → `handle_fake_inflation_1`、talent6 → `handle_menarche_1`；`check_fertilization` / `check_pregnancy` talent20 → `handle_fertilization_1`；`check_near_born` 21 → `handle_pregnancy_1`；`check_born` 22 → `handle_parturient_1`；`check_rearing` 23 → `handle_postpartum_1`；`check_rearing_complete` 与受精豁免中的 24 → `handle_rearing_1`；`check_grow_to_loli/girl` 的 `father_id==0` / 102 / 103 / 28 → `handle_self_is_player_daughter` / `handle_self_is_child` / `handle_self_is_loli` / `handle_growth_stop_1` |
| `egg_handle` | `check_ovulation` talent6 → `handle_menarche_1`、21/22 → `handle_pregnancy_1`/`handle_parturient_1`、20 → `handle_fertilization_1`；`replace_entertainment_for_eggs` 102 → `handle_self_is_child`（模块顶部新增 `handle_premise` 导入；`handle_premise` 包顶层不导入本子系统模块，无循环导入） |
| `gift_panel.is_drug_effective` 33~41 号药 | 27 → `handle_lactation_1`；35 的 20/21；37 的 20~26 循环 → 7 个前提函数列表；38 的 25 → `handle_fake_inflation_1`；40/41 的 `father_id!=0` / 102 or 103 / 28 → `handle_self_is_player_daughter` / `handle_self_child_or_loli_1` / `handle_growth_stop_1` |

- 未改：21~32 号药（胸/臀/腿/足/外表年龄）的身体素质判定——不属于生育相关素质；`get_baby_id_list` 中 `mother_id == 母亲` 的关系判定保留（无对应前提）。

**验证**：语法检查通过；grep 复核 `Script/System/Pregnancy_System/` 内不再有 `talent[20~28/101~104/6/7]` 读判定；`scratchpad/test_plan17.py` 新增 14 项（7 代直系链的行数/首末行/截断/省略号/玩家名重复、以玩家为中心可构建、阶段枚举走前提、新前提注册与判定）→ **107/107 通过**。

**文档**：`妊娠系统.md` §1 目录与 §7 谱系图段改为 7 代并说明左侧血亲攀升规则；update.log 调整段登记谱系图代数变化（前提化为内部重构不登记）；plan_12 方案末尾追加后续修改说明。

### 12.8 第 4 次修改记录（2026-08-29）：孵化加速药也限定在育儿室使用

用户要求：孵化加速药（36）与成长加速药（39）一样，只能在育儿室中使用。

| 文件 | 改动 |
| --- | --- |
| `Script/UI/Panel/gift_panel.py` | `is_drug_effective` 的 36 分支首条判定改为 `not handle_premise.handle_in_nursery(0)` → 拦截并提示"只能在育儿室使用孵化加速药"（送出前拦截、不消耗道具，与 39 分支同构）；原"无孵化中卵 / 卵已到加速极限"两条判定顺延 |
| `data/csv/Item.csv` / `tools/ArkEditor/csv/Item.csv` | 36 号描述加注"需要在育儿室中使用" |
| `update.log` | 孵化加速药为本版本新增，育儿室限制直接并入其"新增"条目（第 6 次修改时整理，原先追加的"调整"条目已删除） |
| `plan_14` §12.5 | 追加后续修改说明（其 §3.4 使用条件表的 36 号条件以此为准） |

- 判定依据同 §2.4 推论 2：受精卵均存放于育儿室孵化，"在育儿室"只判玩家自身位置（`handle_in_nursery(0)`）。
- 验证：`buildconfig.py` 全量重建无报错（道具描述已进 config）；`scratchpad/test_plan17.py` 新增 3 项（不在育儿室拦截并提示、在育儿室通过、道具描述含"育儿室"）→ **110/110 通过**。
- 遗留：道具描述与提示文案词条变化需 `buildpo` / `buildmo`。

### 12.9 第 5 次修改记录（2026-08-29）：成长加速药改为婴儿/幼女/萝莉通用，剂量改为当前阶段剩余天数的 30%

用户要求：成长加速药同时对婴儿、幼女、萝莉生效；剂量参照妊娠/孵化加速药，为"当前阶段到下一阶段的总剩余天数 × 30%"（剩余 = 阶段总天数 − 已自然经过天数 − 已生效药剂的加速天数）。对婴儿仍为"送给母亲后选择婴儿"；对女儿干员直接送给女儿本人。

**设计口径**

- 阶段阈值：婴儿→幼女 `REARING_COMPLETE_DAY=90`、幼女→萝莉 `GROW_TO_LOLI_DAY=270`、萝莉→少女 `GROW_TO_GIRL_DAY=450`（均以出生时间为基准的有效成长天数，`get_child_grow_day` = 自然天数 + 累计加速）。
- 剂量 `amount = min((阈值 − grow_day) × ACCELERATION_RATE(0.3), 阈值 − 1 − grow_day)`，float 累计、可叠加、永不越过下一阶段（最多到前一天）；`amount < 1` 视为已到极限（不消耗道具）。与妊娠/孵化加速药的差别：不设 250 天累计上限（成长加速跨三个阶段累计，上限无意义）。
- 目标判定 `is_growth_drug_self_target(cid)` = 玩家女儿 ∧（幼女 ∨ 萝莉）→ 对本人生效，**不要求在育儿室**（假设：女儿本人不在育儿室生活）；否则走母亲路径（育儿室 + 选婴儿），与第 4 次修改前逻辑一致。
- 提示文案改为通用："本次加速 X 天，累计加速 Y 天，{名}预计将在{季月日}成长为{幼女/萝莉/少女}"。

| 文件 | 改动 |
| --- | --- |
| `pregnancy_handle.py` | `get_child_growth_acceleration_amount` 改为 30% 剂量公式（返回 float）；新增 `get_child_growth_stage_total_day`、`get_child_next_stage_name`、`is_growth_drug_self_target` |
| `gift_panel.py` | `is_drug_effective` 39 分支：先判本人生效路径，再判母亲路径（育儿室提示改为"只能在育儿室对母亲使用成长加速药"）；`select_gift`：本人生效时跳过选婴儿；`handle_drug_use_effect` 39 分支：按路径确定 `child_id`，用阶段阈值算预计日与下一阶段名 |
| `game_type.py` / `save_handle.py` | `growth_acceleration_days` 改为 float（回填 0.0） |
| `data/csv/Item.csv` / ArkEditor 副本 | 39 号描述改为两种用法 + 30% 口径 |
| `data/talk/daily/gift/give_gift_growth_accelerate.csv` | 原 30 条母亲喂婴儿分支前提全部追加 `&t_rearing_1`（有婴儿的母亲必带育儿素质，避免与女儿分支互相命中）；新增女儿本人服用分支 `CVP_A1_Gift|39_G_0&CVP_A2_T|102_E_1` / `|103_E_1` 各 5 条（cid 1030~1039，幼女写懵懂雀跃、萝莉写羞怯的悸动），共 40 条 |
| `update.log` | 成长加速药为本版本新增，三阶段与 30% 剂量直接改写其"新增"条目（第 6 次修改时整理，原先追加的"调整"条目已删除） |

- §3.1 剂量口径、§3.4 使用条件表、§4 字段类型已加注记（原文划线保留）。
- 验证：`buildconfig.py` 全量重建无报错；`scratchpad/test_plan17.py` 原断言按新剂量改写（10 天婴儿 24.0、30 天婴儿 18.0 且叠加后 30.6、当日出生 27.0→预计夏月 3 日）并新增 16 项（幼女 51.0 / 萝莉 45.0 对本人生效且不要求育儿室、剩余 1/3 天判极限、剩余 4 天 1.2、少女女儿与不在育儿室的母亲拦截、口上分支计数 30/5/5）→ **127/127 通过**。
- 遗留：道具描述、提示文案与新增口上词条需 `buildpo` / `buildmo`。

### 12.10 第 6 次修改记录（2026-08-29）：妊娠加速药 / 孵化加速药 / 假孕药 / 假孕终止药的口上补充幼女、萝莉外表年龄差分

用户要求：plan_14 的四种药物口上也要有对幼女（talent102）与萝莉（talent103）年龄阶段的差分。这两档是既有 104~107 外表年龄分支缺失的两级（同一外表年龄轴，可由外表年龄减少药到达，也可能是女儿），文案按"外表稚嫩的干员"而非"女儿"来写（不预设父女关系），幼女写懵懂天真、萝莉写羞怯矜持。

| 文件 | 新增前提组合 | 条数 | cid |
| --- | --- | --- | --- |
| `give_gift_pregnancy_accelerate.csv` | `CVP_A1_Gift|35_G_0&CVP_A2_T|20_E_1&CVP_A2_T|102_E_1` / `|103` 与 `…|21_E_1&…|102` / `|103`（受精/妊娠 × 幼女/萝莉） | 4×5=20（共 80） | 1060~1079 |
| `give_gift_hatch_accelerate.csv` | `CVP_A1_Gift|36_G_0&CVP_A2_T|102_E_1` / `|103`（药液淋在卵壳上） | 2×5=10（共 40） | 1030~1039 |
| `give_gift_fake_pregnancy.csv` | `CVP_A1_Gift|37_G_0&CVP_A2_T|102_E_1` / `|103`（肚子骤然隆起） | 2×5=10（共 40） | 1030~1039 |
| `give_gift_fake_pregnancy_end.csv` | `CVP_A1_Gift|38_G_0&CVP_A2_T|102_E_1` / `|103`（孕肚消退） | 2×5=10（共 40） | 1030~1039 |

- 前提数与既有 104~107 分支相同（35 为 3 个、其余 2 个），与 `target_is_player_daughter` 分支平级，选取规则不变。
- 验证：`buildconfig.py` 全量重建无报错；`scratchpad/test_plan17.py` 新增 5 项（各组合计数与四文件总条数 80/40/40/40）→ **132/132 通过**。
- 遗留：新增口上词条需 `buildpo` / `buildmo`；update.log 新增段登记 1 条。
