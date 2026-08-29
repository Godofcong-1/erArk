# Plan 14：怀孕系统四种药物（妊娠加速药 / 孵化加速药 / 假孕药 / 假孕终止药）

- 状态：**已实施（2026-08-26，v4 修正轮回归测试 62/62 通过，见 §12.4；游戏内整体测试与 buildpo/buildmo 本地化步骤待用户执行）**
- 来源：用户需求 → 在 plan_12 怀孕系统升级的基础上，新增四种通过礼物系统对 NPC 使用的怀孕相关药物道具
- 修订记录：
  - v1 —— 初稿：现状调查 + 设计决策 + §11 待确认口径清单
  - v2 —— 复查轮（2026-08-25）：经用户确认全部口径——**假孕采用方案 B（仅赋素质 25，INFLATION 前提改并联判定）**、妊娠加速药限定胎生、临盆/破壳前一天硬夹取实装、新增假孕前提组（§3.6）；补齐遗漏关联项：多周目继承核实（§2.9）、好感/信赖妊娠加成说明（§2.4）、update.log 登记（§6）、debug 面板可选项（§5.7）、AI 纸娃娃地文说明（§10）
  - v3 —— 范围扩充（2026-08-25，用户指示）：**四种药物的专用二段行为与专用口上从范围外移入本 Plan**（§2.10 调查、§3.7 设计、§5.9 步骤）——每种药物生效时由目标干员触发专属二段行为并显示专用口上，不再只有系统文本提示
  - v4 —— 用户验收修正（2026-08-26）：**药物口上不新造二段行为，改挂"赠送礼物"（give_gift）一段行为本身**（照泌乳药等既有药剂先例，口上文件放 `data/talk/daily/gift/`，以参数化前提 `CVP_A1_Gift|<礼物id>_G_0` 区分药物）——v3 的二段行为方案（行为 1325~1328、三处常量、Behavior_Effect 挂接、second_pregnancy 口上与地文占位）**全部回退删除**；文本按 `.github/prompts/复数文本技能生成提示词/V0的无子代理版本/特定指令/扩充赠礼的代码文本.prompt.md` 的格式与要求撰写；另按用户口径修正：**孵化加速药的药液由干员倒在卵壳表面、由卵吸收**（非干员自饮）。§2.10/§3.7/§5.9 已按 v4 重写，实施记录见 §12.4
- 预计改动量：约 19 个代码/数据文件 + 5 个 ArkEditor 副本 CSV（4 张数据 CSV + 1 张素质 CSV + 1 张口上 CSV + 前提/二段行为常量与函数 + 数据结构/存档回填 + 礼物面板 + 妊娠/卵结算 + 2 个显示面板）
- 风险等级：中低（不改动 90/260/265 天基础数值与既有孕程逻辑，只做"额外天数注入"与新素质；涉及存档新字段，需回填）
- 适用代码快照：`master @ 25183beb2`
- 参考文档：`plan/done/plan_12_怀孕系统升级_方案.md`、`.github/prompts/数据处理工作流/妊娠系统.md`、`.github/prompts/数据处理工作流/礼物系统.md`、`.github/prompts/数据处理工作流/道具背包系统.md`

---

## 1. 目标（用户需求原文整理）

1. 新增四种怀孕系统相关的药物道具：**妊娠加速药**、**孵化加速药**、**假孕药**、**假孕终止药**。
2. 四种药物的道具 id 从 **35** 开始，都为对 NPC 使用的药物，都通过**礼物系统**以送礼的方式在 NPC 身上起效。
3. **妊娠加速药**：
   - 只能对【受精】（talent20）或【妊娠】（talent21）状态下的干员使用。
   - 效果：每使用一次，获得一个**额外的已加速时间**；统计怀孕相关事件时会算上这个额外时间。
   - 每次加速量为剩余基准孕期的 30%：第一次加速获得 270×0.3=81 天；第二次再获得 (270−81)×30%=56.7 天，累计 137.7 天；以此类推可叠加使用，最多能加速到临盆前一天。
   - 额外加速时间上限为 **250 天**（即临盆期前 10 天）；超过该时间就无法使用。
   - 每次使用时提示玩家：当前累计加速了多少天、新的预期产期是哪一天。
4. **孵化加速药**：
   - 类似妊娠加速药，只能对**已有孵化中的卵**的干员使用。
   - 因为一个角色可能有多个受精卵，使用成功时需要**选择目标卵**是哪一个。
   - 同样每个卵最多加速到 250 天；使用时同样对玩家进行提示（当前加速天数、新的预计破壳日）。
5. **假孕药**：
   - 只能对**胎生**生育类型种族的干员使用，且该干员不得处于任意怀孕阶段素质内。
   - 效果：赋予新素质（id **25**）【假孕孕肚】——肚子隆起，拥有与真怀孕孕肚一样的身体特征，但并没有真的怀孕。
   - 拥有【假孕孕肚】素质的角色无法受精怀孕，跳过受精怀孕结算。
6. **假孕终止药**：用于消除干员的【假孕孕肚】素质。

## 2. 现状调查（已完成，均为实际代码核实结果）

### 2.1 道具 CSV 与药物道具先例（已核实）

- **[Item.csv](data/csv/Item.csv) 列结构**：`cid,name,type,tag,level,price,effect,h_item_id,info`（表头 4 行 + 第 5 行类描述；第 4 行翻译标记 `0,1,0,0,0,0,0,0,1`——**name 与 info 两列提取翻译**，新增行需跑 buildpo/buildmo）。
- **对 NPC 使用的药物先例**（type=`Drug`、tag=`npc_use`）：id 21~28（丰胸/缩胸/丰臀/缩臀/丰腿/瘦腿/丰足/瘦足，level 2）、id 31~34（外表年龄增长/减少药 level 3、**泌乳药/停乳药** level 3），price 均 200、effect 0、h_item_id −1。
- **id 空闲段核实**：34 之后下一个已用 id 为 50（相机）——**35~49 空闲**，新药取 35/36/37/38。
- H 药品（100~108，type=`H_Drug`）走 `h_item_id → h_state.body_item` 的体内延时生效机制，与本次无关；新药照 21~34 先例即时生效，`h_item_id=-1`。

### 2.2 礼物系统全链与药物生效机制（已核实）

| 环节 | 位置 | 说明 |
| --- | --- | --- |
| 指令入口 | [Instruct.py:95](Script/System/Instruct_System/Instruct.py#L95)、[handle_instruct.py:974-977](Script/System/Instruct_System/handle_instruct.py#L974) | `GIVE_GIFT` 指令 → `cache.now_panel_id = constant.Panel.GIVE_GIFT` 打开礼物面板 |
| 礼物表 | [data/csv/Gift_Items.csv](data/csv/Gift_Items.csv) | 列 `cid,item_id,type,todo,info`；**type=11 为药物类**（2 道歉/3 好感/13 阴茎倒模）；药物行 cid==item_id（21~34），**35~38 空闲** |
| 面板绘制 | [gift_panel.py:103-183](Script/UI/Panel/gift_panel.py#L103) `Gift_Panel.draw` | 按 cid 序遍历 `config_gift_items`；药物组折叠按钮硬编码在 gift_id==21 处（:121），**type==11 未展开时统一跳过（:139）——新药落在 34 与 51 之间自动归入折叠组，无需改折叠逻辑**；未拥有/未实装灰字不可点（:145-160） |
| 送出确认 | [gift_panel.py:185-204](Script/UI/Panel/gift_panel.py#L185) `select_gift` | `check_gift_available` 校验 → `behavior.gift_id = gift_id`（字段定义 [game_type.py:1057](Script/Core/game_type.py#L1057)）→ `chara_handle_instruct_common_settle(constant.Behavior.GIVE_GIFT, judge=_("初级骚扰"), force_taget_wait=True)`（药物类统一初级骚扰门槛，:198-199，新药自动沿用） |
| **使用条件校验** | [gift_panel.py:258-335](Script/UI/Panel/gift_panel.py#L258) `is_drug_effective` | 每种药一个 elif 分支：条件不满足 → WaitDraw 提示 + return False（**送礼不会发出、道具不消耗**）。泌乳药 :319-322（已有 27 则无效）/ 停乳药 :324-327（没有 27 则无效）即"素质类药物"的成对先例。**四种新药的使用前提全部写在这里** |
| **效果结算** | [Settle/default.py:7283-7364](Script/Settle/default.py#L7283) `handle_give_gift_add_adjust`（效果 `GIVE_GIFT_ADD_ADJUST`，挂在送礼行为上） | 读 `behavior.gift_id`（:7300）→ 道具持有数 −1（:7308）→ type==11 时调 `gift_panel.handle_drug_use_effect(target_id, gift_id)`（:7351-7354） |
| **效果实现** | [gift_panel.py:28-70](Script/UI/Panel/gift_panel.py#L28) `handle_drug_use_effect` | 每种药一个 elif 分支 + gold_enrod WaitDraw 结果提示。泌乳药/停乳药先例（:61-66）：直接 `talent[27] = 1/0` 并打印"获得了/失去了【泌乳】"。**四种新药的效果全部写在这里** |
| 购买 | [h_item_shop_panel.py:79-80](Script/UI/Panel/h_item_shop_panel.py#L79) | 商店自动列出全部 `type=="Drug"` 道具（价格读 price 列，粉红凭证支付 :295-300）——**新药无需任何购买侧改动** |

→ **结论**：新增一种药物的礼物链本体只需 4 处：Item.csv 行 + Gift_Items.csv 行 + `is_drug_effective` 分支 + `handle_drug_use_effect` 分支（外加 ArkEditor 副本同步）；送礼指令/行为/GIVE_GIFT 结算全链复用，无新指令与结算效果。（v3 起另配专属二段行为与口上，注册链见 §2.10。）

### 2.3 妊娠计时机制与天数计算点全量清单（已核实）

**胎生链——`fertilization_time` 的全部天数换算消费点（加速注入点，穷举）**：

| 位置 | 计算 | 阈值/用途 |
| --- | --- | --- |
| [pregnancy_handle.py:186-191](Script/System/Pregnancy_System/pregnancy_handle.py#L186) `check_pregnancy` | `(cache.game_time - fertilization_time).days` | `>= 90` 受精→妊娠 |
| [pregnancy_handle.py:223-228](Script/System/Pregnancy_System/pregnancy_handle.py#L223) `check_near_born` | 同上 | `>= 260` 妊娠→临盆（注释：标准妊娠 265 天） |
| [pregnancy_handle.py:255-262](Script/System/Pregnancy_System/pregnancy_handle.py#L255) `check_born` | `.days - 260` | 临盆后每日 `+20%` 概率触发生产事件 |
| [body_info_panel.py:164-176](Script/UI/Panel/body_info_panel.py#L164) | `.days` | 显示"已受精 X 天 / 距离临盆预计还有 261−X 天" |
| [pregnancy_panel.py:88-96](Script/System/Pregnancy_System/pregnancy_panel.py#L88) `get_stage_info_text` | `fertilization_time + timedelta(days=90/260)` | 总览面板"预计 X 月 X 日妊娠/临盆" |

`fertilization_time` 写入点：受精时 [pregnancy_handle.py:143](Script/System/Pregnancy_System/pregnancy_handle.py#L143)（=**妊娠加速清零点①**）、debug 面板手改（debug_panel.py:1758-1788）。产后转换（22→0、23=1、26→0）在 [born_event_panel.py:180-184](Script/System/Pregnancy_System/born_event_panel.py#L180)（=**清零点②**）。`check_rearing`/`check_rearing_complete` 基于孩子的 `born_time`，产后链**不受加速影响**。

**卵生链——卵 `lay_time` 的天数换算点**：

- [egg_handle.py:125-133](Script/System/Pregnancy_System/egg_handle.py#L125) `get_hatch_day(egg_data)`：`(cache.game_time - lay_time).days`——**唯一孵化天数换算函数**，消费方为破壳判定 [check_egg_born:292-300](Script/System/Pregnancy_System/egg_handle.py#L292)（`>= HATCH_TOTAL_DAY`，常量 265 在 [:22](Script/System/Pregnancy_System/egg_handle.py#L22)；同函数刷新 `hatch_stage` 展示值）与总览面板 [pregnancy_panel.py:97-102](Script/System/Pregnancy_System/pregnancy_panel.py#L97)（"孵化第 X 天"）。**在此函数内注入加速即全局生效**。
- 面板预计破壳日 [pregnancy_panel.py:101](Script/System/Pregnancy_System/pregnancy_panel.py#L101)：`lay_time + timedelta(days=265)`——需要单独扣减加速天数。
- ⚠️ [get_identifiable_eggs:104](Script/System/Pregnancy_System/egg_handle.py#L104) 也用 `lay_time` 判"排出日早于今天"（鉴定资格）——**与孵化进度无关，加速不得影响此处**（孵化加速药只对"已鉴定+受精"的孵化中卵可用，天然无交集，但实施时不要顺手改到）。

**推进时机**：`check_all_pregnancy` 全链挂玩家睡觉结算 + 每日 0 点兜底（plan_12 §2.4/§3.4）——加速后的阶段转换在**当晚睡觉或次日 0 点**生效，使用药物时不立即转换阶段。

**数字口径核实**：代码中 260=临盆阈值、265=名义标准孕期/孵化总天数、90=受精→妊娠。用户公式的 **270 为剂量公式基数**（名义孕期），**250 上限 = 临盆 260 前 10 天**，两者不冲突（见 §3.3）。

**数据结构与存档**：`class PREGNANCY` 现有字段见 [game_type.py:310-343](Script/Core/game_type.py#L310)（含 eggs/next_egg_id/ovulation_flag）；旧存档回填段在 [save_handle.py:276-287](Script/Core/save_handle.py#L276)（逐角色 hasattr 补空值，新字段照抄）。卵字典键缺失的兼容先例：`egg_data.get("held_by_player", False)`（[egg_handle.py:88](Script/System/Pregnancy_System/egg_handle.py#L88)）。日期工具：跨天数 `game_time.count_day_for_datetime`（gift_panel.py:224 在用）、日期文本 `pregnancy_panel.get_date_text`（[:67-75](Script/System/Pregnancy_System/pregnancy_panel.py#L67)）。

### 2.4 素质系统与孕肚素质引用点（已核实）

- **Talent.csv 结构**：列为 `cid,Talent_type,name,heredity,info`（表头 4 行 + 第 5 行类描述，与其他 CSV 同制）。`Talent_type`：0 性素质 / 1 身体素质 / 2 精神素质 / 3 技术素质 / 4 其他素质。
- **id 25 确认空闲**：[Talent.csv:27-28](data/csv/Talent.csv#L27) 中 24（育儿）与 26（孕肚）之间缺号，与 plan_12 §2.2 记载一致。新增行建议：`25,0,假孕孕肚,0,<描述>`（type=0 性素质、不可遗传，与 26 孕肚同组）。
- **id 26【孕肚】行**：`26,0,孕肚,0,处于怀孕中后期，腹部明显隆起，行动不便但仍可进行部分活动，外观会有显著变化`。
- **talent[26] 全部代码引用点**（grep 穷举，仅 3 文件）：
  | 类别 | 位置 | 内容 |
  | --- | --- | --- |
  | 写入（真孕获得） | [pregnancy_handle.py:194](Script/System/Pregnancy_System/pregnancy_handle.py#L194) `check_pregnancy` | 受精满 90 天转妊娠时 `talent[26]=1`（:207 打印"获得了[孕肚]"） |
  | 写入（生产清除） | [born_event_panel.py:184-185](Script/System/Pregnancy_System/born_event_panel.py#L184) | 生产结算 `talent[26]=0`（打印"失去了[孕肚]"） |
  | 读取（外观前提，唯一读取点） | [handle_premise_other.py:2659-2718](Script/Design/handle_premise/handle_premise_other.py#L2659) | 4 个前提 `INFLATION_0/1`、`T_INFLATION_0/1`（常量 [constant_promise.py:2300-2307](Script/Core/constant_promise.py#L2300)；ArkEditor 副本 [tools/ArkEditor/csv/Premise.csv:1162-1165](tools/ArkEditor/csv/Premise.csv#L1162)） |
- **孕肚前提的消费方**：口上/事件 CSV 经前提 cid `inflation_1` 等过滤（含 AI 纸娃娃地文的前提组合）；指令 [InstructConfig.csv:101](data/csv/InstructConfig.csv#L101) `3003 听肚子里的动静` 前提含 `T_INFLATION_1`。**即：文本/指令层的"孕肚外观"完全由 talent26 驱动**。
- **断面图**（H 中的身体截面）：[cross_section_image.py:38-44](Script/Design/cross_section_image.py#L38) 按前提 `t_fertilization_1`（20）→"受精"、`t_pregnancy_1`（21）→"妊娠"、`t_parturient_1`（22）→"临盆"选图，**不读 26**。
- **身体信息面板**：[body_info_panel.py:164-176](Script/UI/Panel/body_info_panel.py#L164) 按 talent20/21 显示怀孕天数，不读 26。
- **素质赋予/移除惯用写法**：直接 `character_data.talent[x] = 1/0`，配合手工拼接 `draw_text += _("\n{0}获得了[XX]\n")` 的 WaitDraw 提示（先例 [pregnancy_handle.py:203-209](Script/System/Pregnancy_System/pregnancy_handle.py#L203)；药物侧先例即泌乳药 [gift_panel.py:61-66](Script/UI/Panel/gift_panel.py#L61)），无统一 helper。
- **好感/信赖结算的妊娠加成**（复查轮补充）：[common_default.py:743](Script/Settle/common_default.py#L743) 与 [:806](Script/Settle/common_default.py#L806) 对 talent 20/21/22 各给 +0.5 倍好感/信赖增益——只认真孕素质。**假孕（25）不享受该加成**，方案 B 下天然不含假孕，维持现状不改动。

### 2.5 受精怀孕结算的豁免点（已核实）

- **`get_fertilization_rate`**（[pregnancy_handle.py:34-89](Script/System/Pregnancy_System/pregnancy_handle.py#L34)）：事前避孕药 `h_state.body_item[11]` / 事后避孕药 `[12]` 将概率清 0 并打印"在避孕药的影响下…无法受精"（:52-64）——**假孕素质清零受精率照此先例**。
- **`check_fertilization`**（[pregnancy_handle.py:92-176](Script/System/Pregnancy_System/pregnancy_handle.py#L92)）：
  - 触发门：`pregnancy.ovulation_flag`（:101）；胎生在 :104-105 消费标记。
  - 现有豁免链：已受精（talent20/21/22 任一，:116-119，静默清概率）→ 未初潮 talent6（:125-126，带文案）→ 机械 race2 无 talent171（:129-131，带文案）。
  - **假孕跳过选点**：在未初潮豁免（:125）同层加 talent25 带文案分支（清概率），配合 `get_fertilization_rate` 清零双保险。
- **卵生排卵结算**（[egg_handle.py:208-244](Script/System/Pregnancy_System/egg_handle.py#L208) `check_ovulation`）无需加豁免：假孕药前提已限定胎生（birth_type==1），卵生角色（==11）不可能持有 talent25。

### 2.6 生育类型判定与怀孕阶段判定先例（已核实）

- **`egg_handle.get_birth_type`**（[egg_handle.py:30-47](Script/System/Pregnancy_System/egg_handle.py#L30)）：读 `Race.csv` 的 `birth_type` 列，缺列兜底 1；**12（无壳卵生）归一化返回 1**——即假孕药"只能对胎生使用"的判定写 `get_birth_type(id) == 1` 即可，安努拉/阿戈尔/海嗣三族自动按胎生放行（与 plan_12 "胎生链不感知 12"口径一致）。
- **现成的怀孕阶段组合前提**：[handle_premise_other.py:1120-1134](Script/Design/handle_premise/handle_premise_other.py#L1120) `T_FERTILIZATION_OR_PREGNANCY`（交互对象 talent 20/21/22/23 任一）及其否定 `T_NOT_FERTILIZATION_OR_PREGNANCY`（:1137）——注意**不含 24 育儿**；本次药物条件在 `is_drug_effective` 内直接判素质数组，不依赖前提系统。
- 怀孕阶段素质全集参考：[debug_panel.py:1722](Script/UI/Panel/debug_panel.py#L1722) 列举 20 受精/21 妊娠/22 临盆/23 产后/24 育儿；卵生阶段判定用 `egg_handle.get_unidentified_eggs / get_hatching_eggs`（[pregnancy_panel.py:40-64](Script/System/Pregnancy_System/pregnancy_panel.py#L40) 阶段枚举先例）。

### 2.7 孵化加速药的选卵交互先例（已核实）

- **没有"送礼后二次选择"的现成先例**，但礼物面板本身就是"面板循环内 `flow_handle.askfor_all` 选择 → 写 `behavior` 字段 → 触发行为"的结构（[gift_panel.py:185-204](Script/UI/Panel/gift_panel.py#L185)），在 `select_gift` 内追加第二步"选卵列表"完全同构，Tk/Web 双模式均走同一 askfor_all 通道，无需特殊适配。
- 结算侧读取 behavior 字段的先例：`handle_give_gift_add_adjust` 读 `behavior.gift_id`（[default.py:7300](Script/Settle/default.py#L7300)）。
- 弃选方案：在结算函数 `handle_drug_use_effect` 内弹选择（Born_Panel 在睡眠结算内弹面板有先例）——但 Web 模式需子面板包裹（BORN_EVENT_PANEL_TAB_ID 先例），复杂度高且结算内交互违背"选择在指令期、效果在结算期"的既有分工。

### 2.8 已知陷阱与硬约束（已核实）

- **ArkEditor 副本 CSV 同步**：`tools/ArkEditor/csv/` 下需同步 `Item.csv`、`Gift_Items.csv`、`Talent.csv`（Talent 副本的 info 列为缩写版描述，照现有行风格写短版）。本次不新增前提/效果/行为，`Premise.csv`/`Effect.csv`/`Behavior_Data.csv` 副本无需动。
- CSV 数据行空值字段会被删除（plan_12 §2.8 陷阱）：新增 CSV 行所有列必填。
- CSV/常量改动后必须 `.conda\python.exe buildconfig.py` 全量重建；新增可翻译文本需 buildpo/buildmo。
- 编号（道具 id 35~38、素质 id 25）实施时必须再次现场核对空闲（plan_06 §8.1 教训）。
- 旧存档兼容：`PREGNANCY.acceleration_days` 走 save_handle 回填；卵字典新键走 `.get` 兜底（held_by_player 先例）。
- Tk 与 Web 双绘制模式：新增提示只用抽象绘制类（WaitDraw/NormalDraw），选卵交互复用面板 askfor_all。
- `handle_drug_use_effect` 在**结算阶段**执行，此时道具已扣（default.py:7308 先扣 1 再生效）——新药的全部使用条件必须在 `is_drug_effective`（送出前）拦截，结算内只做兜底校验（如选中的卵已不存在则提示并不生效，道具照常消耗与否见 §3.5）。

### 2.9 多周目继承兼容（复查轮补充，已核实无需改动）

- 素质迁移：[old_chara_to_new.py:687](Script/Core/old_chara_to_new.py#L687) 新周目角色素质整表 `.copy()`；[:1368-1371](Script/Core/old_chara_to_new.py#L1368) 对配置表新增而旧存档缺号的素质统一补 0——**新素质 25 对旧周目角色自动兼容**。
- 妊娠数据迁移：[:740](Script/Core/old_chara_to_new.py#L740) `pregnancy` 结构体整体沿用（缺失时才新建）——`acceleration_days` 与卵字典新键随对象整体迁移，无需额外处理。

### 2.10 礼物口上机制（v4 重写，已核实；v3 的二段行为注册链方案已废除并回退）

药物送礼口上挂在 **`give_gift` 一段行为**本身上，机制与泌乳药等既有药剂完全一致：

| 环节 | 位置 | 说明 |
| --- | --- | --- |
| 口上文件组织 | `data/talk/daily/gift/`（先例 [give_gift_lactation_medicine.csv](data/talk/daily/gift/give_gift_lactation_medicine.csv) 泌乳药 151 条） | 一药一文件；列 `cid,behavior_id,adv_id,premise,context`，behavior_id 恒为 `give_gift`，{Name}=博士、{TargetName}=收礼干员 |
| 礼物判定前提 | [handle_premise/__init__.py:392-398](Script/Design/handle_premise/__init__.py#L392) | **参数化 token** `CVP_A1_Gift|<礼物id>_G_0`（读 `behavior.gift_id`），**零前提代码**；可叠加 `CVP_A2_T|<素质id>_E_1` 等 token 做状态差分 |
| cid 冲突规则 | [buildconfig.py:189-193](buildconfig.py#L189) | talk 类 CSV 的 cid 会被加**文件名前缀**（`file_id + cid`），各礼物文件全部从 1000 起互相重叠也不冲突——新文件同样从 1000 起 |
| 显示时机 | v12 口径 | give_gift 行为口上在行为结算阶段**先于效果结算**显示，premise 求值时 `behavior.gift_id` 仍在——与 33/34 号药完全一致，无需时序处理 |
| 文本生成要求 | `.github/prompts/复数文本技能生成提示词/V0的无子代理版本/特定指令/扩充赠礼的代码文本.prompt.md` | 每种前提组合各写 5 行；单条约 800 中文字（不少于 650，v4 实施按"接近即可"口径放宽）；句号非结尾时后接 `\n`；无具体对话/地点/家具；可用占位符 {TargetUpClothName}/{TargetDownClothName}/{breast_s}/{legs_s} |

## 3. 设计决策

### 3.1 假孕孕肚（素质25）与孕肚（素质26）的外观联动【已确认：方案 B（2026-08-25）】

- **方案 B（用户确认采用）：假孕药只置 `talent[25]=1`，假孕终止药只置 `talent[25]=0`，不触碰 talent26**。
  - talent26 保持"真孕专属"语义（仅由 `check_pregnancy` 赋予、生产结算清除），无需任何守卫逻辑。
  - **孕肚外观的统一入口改造**：把 4 个既有 INFLATION 前提（[handle_premise_other.py:2659-2718](Script/Design/handle_premise/handle_premise_other.py#L2659)）改为并联判定——`INFLATION_1`/`T_INFLATION_1` = `talent[26]==1 or talent[25]==1`；`INFLATION_0`/`T_INFLATION_0` = 两者均为 0。由 §2.4 核实，talent26 的唯一读取点就是这 4 个前提，改造后口上/事件/指令（如 3003 听肚子里的动静）对假孕角色自动生效。
  - ArkEditor [Premise.csv:1162-1165](tools/ArkEditor/csv/Premise.csv#L1162) 副本的 info 文案同步为"孕肚外观"语义（如"自己有孕肚外观(含假孕)"），提醒口上作者该前提不区分真假孕；需要区分时使用 §3.6 的假孕前提组。
- 弃选方案 A（同时赋予/移除 25+26）：外观钩子零改动，但素质列表会同时显示两条素质、26 的"怀孕中后期"描述对假孕角色失真，且真假孕语义混在同一素质上——用户选择保持 26 语义纯净。
- 注意：断面图（读 21/22）与妊娠的工作暂停（读 21）**不会**因假孕触发——假孕只有外观孕肚，无行为限制，符合"并没有真的怀孕"；好感/信赖的妊娠加成（§2.4）同样不含假孕，维持现状。

### 3.2 假孕的受精怀孕结算跳过

- `get_fertilization_rate`（[pregnancy_handle.py:34](Script/System/Pregnancy_System/pregnancy_handle.py#L34)）：照避孕药先例（:52-64），talent25==1 时概率清 0，文案格式照抄（如"在假孕状态下，{0}的身体不会真正受精"）。
- `check_fertilization`（[pregnancy_handle.py:92](Script/System/Pregnancy_System/pregnancy_handle.py#L92)）：在未初潮豁免（:125）同层加 talent25 带文案分支——双保险，防止绕过 rate 计算的路径漏判。
- 卵生排卵结算不加豁免（§2.5）。

### 3.3 加速时间的数值口径与计时注入

**剂量公式（妊娠/孵化通用）**：

- 每次使用加速量 = `(270 − 该目标已累计加速天数) × 0.3`，以 **float 累计**（81 → 137.7 → 177.39 → …），在天数换算与显示时**向下取整**（与用户示例"累计 137 天"口径一致）。
- **三重上限【已确认：硬夹取实装（2026-08-25）】**，实际入账量取三者夹取后的最小值，可入账量 ≤ 0 时药物判定为无效（`is_drug_effective` 拦截，不消耗道具）：
  1. 累计加速 ≤ **250 天**（"超过该时间就无法使用"）；
  2. 胎生：注入后的有效孕期天数 ≤ **259 天**（临盆 260 前一天，"最多能加速到临盆前一天"——药物永远不会把孕程直接推入/越过临盆，自然孕程较长的角色用药后最快下个自然日进入临盆）；
  3. 卵：注入后的有效孵化天数 ≤ **264 天**（破壳 265 前一天，同理类推）。
- 孵化加速药的剂量公式与妊娠版**完全一致**（270 基数、30%、250 上限，已确认采用默认口径），玩家体验统一。

**注入方式（引用清单见 §2.3，全部经统一 helper，防漏改）**：

- 胎生：`PREGNANCY` 新增 `acceleration_days: float`；在 pregnancy_handle 新增 `get_pregnancy_past_day(character_id) -> int` = `(cache.game_time − fertilization_time).days + int(acceleration_days)`，替换 §2.3 表中 5 处消费点的裸计算（3 处结算 + body_info_panel + pregnancy_panel 的预计日期改为 `fertilization_time + timedelta(days=90/260 − int(acceleration_days))`）。
- 卵：卵字典新增键 `acceleration_days: float`（`add_egg` 初始化 0.0，旧卵 `.get` 兜底）；`get_hatch_day` 返回值加 `int(egg_data.get("acceleration_days", 0))`——破壳判定与"孵化第 X 天"显示自动生效；pregnancy_panel:101 预计破壳日改为 `lay_time + timedelta(days=265 − int(acc))`。
- **清零点**：胎生加速在受精写入 `fertilization_time` 时（[pregnancy_handle.py:143](Script/System/Pregnancy_System/pregnancy_handle.py#L143)）与生产结算（[born_event_panel.py:180 段](Script/System/Pregnancy_System/born_event_panel.py#L180)）清零；卵加速随卵数据删除（鉴定废弃/破壳）自清，无需处理。
- **生效时机**：使用后不立即转换阶段，阶段转换在当晚睡觉结算或次日 0 点兜底时按新有效天数触发（§2.3 推进时机）；使用时的提示文本即时给出新预计日期。

**使用时的提示文本**（handle_drug_use_effect 内，gold_enrod WaitDraw，照药物结果提示先例）：

- 妊娠加速药：`本次加速 X 天，累计加速 Y 天；{名字}的预计临盆日期提前到了 {M月D日}`（预计临盆日 = `fertilization_time + timedelta(days=260 − int(acc))`，日期格式化复用 `pregnancy_panel.get_date_text`）。
- 孵化加速药：`本次加速 X 天，累计加速 Y 天；这枚卵的预计破壳日期提前到了 {M月D日}`。

### 3.4 四种药物的道具注册与使用条件

**CSV 新行**（等级/价格照 31~34 先例 level 3 / price 200，实施时可按用户意见调整）：

`data/csv/Item.csv`（描述为草案，实施时定稿）：

```csv
35,妊娠加速药,Drug,npc_use,3,200,0,-1,使用后大幅加快对方腹中胎儿的发育速度，将剩余孕期缩短30%，可叠加使用，最多能加速到临盆前一天
36,孵化加速药,Drug,npc_use,3,200,0,-1,使用后大幅加快正在孵化的卵的发育速度，将剩余孵化时间缩短30%，可叠加使用，需要指定作用的卵
37,假孕药,Drug,npc_use,3,200,0,-1,使用后会让对方的身体进入假性怀孕状态，肚子会像真正的孕妇一样隆起，但并没有真的怀孕，在此期间也无法受精怀孕
38,假孕终止药,Drug,npc_use,3,200,0,-1,使用后解除对方的假性怀孕状态，隆起的肚子会恢复原状
```

`data/csv/Gift_Items.csv`：

```csv
35,35,11,0,妊娠加速药
36,36,11,0,孵化加速药
37,37,11,0,假孕药
38,38,11,0,假孕终止药
```

**使用条件（`is_drug_effective` 新增 4 个 elif 分支，全部在送出前拦截、不消耗道具）**：

| 药物 | 有效条件 | 无效提示（草案） |
| --- | --- | --- |
| 35 妊娠加速药 | `talent[20] or talent[21]`；且 `get_birth_type(t_id)==1`【已确认：限定胎生（2026-08-25）】；且按 §3.3 计算的可入账加速量 > 0 | "{0}没有处于受精或妊娠状态，无法使用妊娠加速药" / "{0}的种族不是胎生，无法使用妊娠加速药" / "{0}的孕期已经加速到极限了，无法继续使用妊娠加速药" |
| 36 孵化加速药 | `len(egg_handle.get_hatching_eggs(t_id)) > 0`；且至少一枚卵可入账加速量 > 0 | "{0}没有正在孵化中的卵，无法使用孵化加速药" / "{0}的卵都已经加速到极限了，无法继续使用孵化加速药" |
| 37 假孕药 | `get_birth_type(t_id)==1` 且 talent 20/21/22/23/24/25/26 全为 0 | "{0}的种族不是胎生，无法使用假孕药" / "{0}正处于怀孕相关状态中，无法使用假孕药" |
| 38 假孕终止药 | `talent[25]==1` | "{0}没有处于假孕状态，不需要使用假孕终止药" |

**效果实现（`handle_drug_use_effect` 新增 4 个 elif 分支）**：

- 35：按 §3.3 计算入账量，`pregnancy.acceleration_days += 入账量`，打印提示。
- 36：读玩家 `behavior.gift_egg_id`（§3.5），兜底校验该卵仍存在且为孵化中（否则打印"卵已不存在"并直接返回），`egg_data["acceleration_days"] = egg_data.get("acceleration_days", 0) + 入账量`，打印提示，用后将字段重置为 −1。
- 37：`talent[25]=1`（方案 B，不触碰 26），打印"{0}获得了【假孕孕肚】，肚子像真正的孕妇一样隆起来了"。
- 38：`talent[25]=0`（方案 B，不触碰 26），打印"{0}失去了【假孕孕肚】，隆起的肚子恢复了原状"。
- **v4**：以上 4 个分支只做数据结算与系统提示，**不触发任何二段行为**；药物的专用口上由送礼行为（give_gift）的常规口上链路按 `CVP_A1_Gift|3X` 前提自动选取，先于效果提示显示（§3.7）。

### 3.5 孵化加速药的选卵交互【已确认（含"单卵跳过选择"默认口径）】

- **选点：`select_gift` 内、行为触发前**（照 gift_id 先例，弃选"结算内弹面板"，理由见 §2.7）：
  1. gift_id==36 且 `check_gift_available` 通过后，绘制目标当前全部**可加速**的孵化中卵列表，每行按钮：`[卵编号] 孵化第 X 天（已加速 Y 天，预计 M月D日 破壳）`，外加 `[返回]`（取消本次送礼，不触发行为）。
  2. 玩家点选后：`behavior.gift_egg_id = 选中卵编号`，随后照常 `chara_handle_instruct_common_settle(GIVE_GIFT, ...)`。
  3. 目标只有一枚可加速的孵化中卵时**跳过选择直接选中**（体验优化）。
- `CharacterBehavior` 新增字段 `gift_egg_id: int = -1`（挂在 [game_type.py:1057](Script/Core/game_type.py#L1057) `gift_id` 旁）；结算读取用 `getattr(..., "gift_egg_id", -1)` 兜底旧存档（该字段先写后读，回填非必需，兜底读取即可）。

### 3.6 假孕前提组【已确认：新增（2026-08-25）】

供口上/事件作者区分真孕肚与假孕孕肚。全部照 INFLATION 前提先例（[constant_promise.py:2300-2307](Script/Core/constant_promise.py#L2300) + [handle_premise_other.py:2659-2718](Script/Design/handle_premise/handle_premise_other.py#L2659) + ArkEditor [Premise.csv:1162-1165](tools/ArkEditor/csv/Premise.csv#L1162)），函数放在 INFLATION 组旁：

| 前提 cid | 常量名 | 判定 | ArkEditor 行（分组"素质_妊娠"） |
| --- | --- | --- | --- |
| `fake_inflation_0` | `FAKE_INFLATION_0` | 自己 `talent[25]==0` | `fake_inflation_0,FAKE_INFLATION_0,素质_妊娠,自己假孕孕肚==0` |
| `fake_inflation_1` | `FAKE_INFLATION_1` | 自己 `talent[25]==1` | `fake_inflation_1,FAKE_INFLATION_1,素质_妊娠,自己假孕孕肚==1` |
| `t_fake_inflation_0` | `T_FAKE_INFLATION_0` | 交互对象 `talent[25]==0` | `t_fake_inflation_0,T_FAKE_INFLATION_0,素质_妊娠,交互对象假孕孕肚==0` |
| `t_fake_inflation_1` | `T_FAKE_INFLATION_1` | 交互对象 `talent[25]==1` | `t_fake_inflation_1,T_FAKE_INFLATION_1,素质_妊娠,交互对象假孕孕肚==1` |

同时改造 4 个既有 INFLATION 前提为并联判定（§3.1 方案 B）：`_1` = `talent[26] or talent[25]`、`_0` = 两者均 0，ArkEditor 副本 info 同步为"孕肚外观(含假孕)"语义。

### 3.7 四种药物的专用送礼口上【v4 定稿（2026-08-26，用户验收修正）；v3 二段行为方案已废除回退】

药物口上挂 **`give_gift` 一段行为**（机制见 §2.10），新建 4 个口上文件于 `data/talk/daily/gift/`，cid 均从 1000 起、adv_id=0、每前提组合 5 条：

| 文件 | 药物 | 前提组合 | 条数 | 文案题材 |
| --- | --- | --- | --- | --- |
| `give_gift_pregnancy_accelerate.csv` | 35 妊娠加速药 | ① 受精期 `CVP_A1_Gift|35_G_0&CVP_A2_T|20_E_1`；② 妊娠期 `CVP_A1_Gift|35_G_0&CVP_A2_T|21_E_1` | 2×5=10 | 递药→服下→腹中胎儿被骤然加速发育的胀热悸动与心绪（受精期写平坦小腹内的暗涌，妊娠期写孕肚变沉与胎动加剧） |
| `give_gift_hatch_accelerate.csv` | 36 孵化加速药 | `CVP_A1_Gift|36_G_0` | 5 | 递药→干员**将药液倒在卵壳表面、由卵吸收**（用户口径，非干员自饮）→卵壳发热泛光、壳内生命躁动 |
| `give_gift_fake_pregnancy.csv` | 37 假孕药 | `CVP_A1_Gift|37_G_0` | 5 | 递药→服下→肚子迅速隆起成孕妇模样的惊异/羞耻/隐秘悸动 |
| `give_gift_fake_pregnancy_end.csv` | 38 假孕终止药 | `CVP_A1_Gift|38_G_0` | 5 | 递药→服下→孕肚消退复原的轻盈、松弛与一丝怅然 |

- 文本格式与写法遵循 §2.10 所引的"扩充赠礼的代码文本"prompt（字数、`\n` 规则、无对话/地点、占位符）。
- `handle_drug_use_effect` 各分支**只做数据结算与系统提示 WaitDraw**，不再触发任何二段行为；口上由送礼行为的常规口上链路自动选取显示（先于效果提示）。
- 编辑器作者如需为特定角色写专属版本，直接在角色口上中对 `give_gift` 行为叠加 `CVP_A1_Gift|3X_G_0` 前提即可，无需任何代码或表改动。

## 4. 数据结构设计（权威定义）

`class PREGNANCY`（[game_type.py:310](Script/Core/game_type.py#L310)）新增字段：

```python
self.acceleration_days: float = 0.0
""" 妊娠加速药累计的额外已加速时间（天）：float累计、参与天数换算时向下取整；
    统计怀孕相关事件（受精转妊娠/临盆/生产概率/面板显示）时计入；
    受精时与生产结算时清零；累计上限250天 """
```

卵数据字典（`PREGNANCY.eggs` 的值，[game_type.py:333-341](Script/Core/game_type.py#L333) docstring 同步更新）新增键：

```python
"acceleration_days": float,  # 孵化加速药对该卵累计的额外已加速时间（天），add_egg时初始化0.0，
                             # 旧存档卵缺键时一律 .get("acceleration_days", 0) 兜底；随卵删除自清；上限250
```

`class CharacterBehavior`（[game_type.py:1057](Script/Core/game_type.py#L1057) 旁）新增字段：

```python
self.gift_egg_id: int = -1
""" 前提结算用:孵化加速药选中的目标卵编号（-1为未选择，结算消费后重置） """
```

- 旧存档回填（[save_handle.py:276-287](Script/Core/save_handle.py#L276) 段追加）：`pregnancy` 缺 `acceleration_days` 补 0.0。卵字典键与 behavior 字段走 `.get`/`getattr` 兜底，不回填。

## 5. 详细改动步骤

> ⚠️ 所有编号（道具 35~38、素质 25）实施时现场再核对一次空闲。

### 5.1 CSV 数据（data/csv/Item.csv、Gift_Items.csv、Talent.csv）

- Item.csv 在 34 停乳药行后插入 §3.4 的 4 行；Gift_Items.csv 在 34 行后插入 4 行；Talent.csv 在 24 与 26 之间插入 `25,0,假孕孕肚,0,<描述草案见§2.4>`。
- 同步 ArkEditor 副本：`tools/ArkEditor/csv/Item.csv`、`Gift_Items.csv`、`Talent.csv`（info 用短版）。

### 5.2 数据结构与存档（Script/Core/game_type.py、save_handle.py）

- 按 §4 权威定义新增 3 处字段/键 docstring；save_handle 回填段追加 `acceleration_days`。

### 5.3 礼物面板（Script/UI/Panel/gift_panel.py）

- `is_drug_effective`：新增 35/36/37/38 分支（§3.4 条件与提示；35/36 的"可入账量>0"判定调用 §5.4 的公用计算函数）。
- `select_gift`：gift_id==36 时插入选卵步骤（§3.5）。
- `handle_drug_use_effect`：新增 4 个效果分支（§3.4，v4 起不触发二段行为，仅数据结算+系统提示）；函数内 import `egg_handle`/`pregnancy_handle`（照 :35 函数内 import 先例，避免循环导入）。

### 5.4 妊娠结算（Script/System/Pregnancy_System/pregnancy_handle.py）

- 新增 `get_pregnancy_past_day(character_id) -> int` 与剂量计算函数 `get_acceleration_amount(now_acc: float, effective_day: int, day_cap: int) -> float`（三重夹取，§3.3；供 gift_panel 的 35/36 分支与 is_drug_effective 复用）。
- `check_pregnancy`/`check_near_born`/`check_born` 三处裸天数计算替换为 helper（:186-191、:223-228、:255-262）。
- `get_fertilization_rate` 与 `check_fertilization` 加假孕豁免（§3.2）。
- 受精写入 `fertilization_time`（:143）处清零 `acceleration_days`。

### 5.5 卵结算（Script/System/Pregnancy_System/egg_handle.py）

- `add_egg` 卵字典补 `"acceleration_days": 0.0`。
- `get_hatch_day` 返回值加 `int(egg_data.get("acceleration_days", 0))`。
- 新增 `get_accelerable_hatching_eggs(character_id) -> dict`（孵化中且可入账量>0 的卵，供选卵列表与 is_drug_effective 用）。

### 5.6 生产事件（Script/System/Pregnancy_System/born_event_panel.py）

- 胎生产后结算段（:180-192）清零母亲 `pregnancy.acceleration_days`。

### 5.7 显示面板（pregnancy_panel.py、body_info_panel.py）

- pregnancy_panel `get_stage_info_text`：受精/妊娠阶段预计日期改为扣减加速（:88-96）；孵化阶段的"孵化第 X 天"经 get_hatch_day 自动生效，预计破壳日（:101）改为扣减加速。
- body_info_panel（:164-176）：`past_day` 改用 helper，"261 − past_day" 剩余天数随之自动修正；可顺带为 talent25 角色加一行假孕状态描述（实施时定）。
- 可选：debug 面板妊娠调试段（[debug_panel.py:1721-1788](Script/UI/Panel/debug_panel.py#L1721)）顺手显示 `acceleration_days`，便于调试（非必需，实施时定）。

### 5.8 假孕前提组（Script/Core/constant_promise.py、handle_premise_other.py、ArkEditor Premise.csv）

- `constant_promise.Premise` 在 INFLATION 组（:2300-2307）旁新增 4 个常量（§3.6 表）。
- `handle_premise_other.py` 新增 4 个前提函数（照 :2659-2718 先例），并把既有 4 个 INFLATION 函数改为并联判定（§3.1 方案 B）。
- `tools/ArkEditor/csv/Premise.csv` 在 :1162-1165 后插入 4 行新前提、同步修改 4 行既有 INFLATION 的 info 文案。

### 5.9 专用送礼口上（v4 重写；data/talk/daily/gift/ 新增 4 文件）

- 新建 §3.7 表所列 4 个口上文件（表头 5 行照既有礼物口上文件；无 BOM、CRLF；文本内不得出现 ASCII 逗号）。
- 文本按 §2.10 所引 prompt 的格式与要求撰写；妊娠加速药按受精/妊娠两分支各 5 条，其余各 5 条。
- **v3 方案回退**（v4 时执行）：删除 Behavior_Data.csv / Behavior_Effect.csv / ArkEditor Behavior_Data.csv 的 1325~1328 各 4 行；删除三个常量文件中的 4 个常量；删除 second_pregnancy.csv 的 61~95 段 20 条口上与 1325~1328 地文占位 4 行；`handle_drug_use_effect` 移除二段行为触发调用——以上文件相对 v3 前状态零残留。

## 6. 构建与缓存

```bash
# 本机必须用 conda 解释器（裸 python 是 Store 空壳别名）
.conda\python.exe buildconfig.py   # 改了 Item/Gift_Items/Talent/Behavior_Data/Behavior_Effect 五张CSV + 口上CSV，必须全量重建（talk 数据在增量构建下会被跳过，务必全量）
.conda\python.exe buildpo.py       # 新增道具名/描述/素质名/提示文案词条
.conda\python.exe buildmo.py
```

实施完成并通过验证后，按 `update-changelog` 体例把四种药物登记进 update.log（新增类条目）。

## 7. 验证清单

### 7.1 单元测试（实施方执行，headless-game-test 方式；已全部通过，详见 §12.3）

- [x] 剂量公式：初始 81；第二次 137.7；连续使用逼近并封顶于 250；封顶后 `is_drug_effective` 返回 False。
- [x] 临盆前一天夹取：自然孕期 200 天的角色使用后有效天数被夹到 ≤259，不会当场越过临盆；卵同理 ≤264。
- [x] 注入生效：受精角色加速 81 天后跑 `check_pregnancy` 于（自然 9 天 + 81）≥90 时转妊娠；`check_near_born`/`check_born` 同口径；`get_hatch_day` 对含加速卵返回自然+加速。
- [x] 多卵独立：两枚卵各自加速互不影响；选卵字段 `gift_egg_id` 写入→结算消费→重置 −1；卵中途被删除时结算兜底不崩溃。
- [x] 假孕：药后 talent25==1 且 **talent26 保持 0**（方案 B）；`get_fertilization_rate` 返回 0；`check_fertilization` 不受精不置 talent20；终止药后 25==0。
- [x] 前提组：假孕角色（25==1、26==0）`INFLATION_1`/`T_INFLATION_1` 返回 1、`INFLATION_0`/`T_INFLATION_0` 返回 0、`FAKE_INFLATION_1` 返回 1；真孕角色（26==1、25==0）两组前提均正确（`INFLATION_1`==1、`FAKE_INFLATION_1`==0）；终止药后全部复原。
- [x] 使用条件矩阵：四种药对 不满足条件的目标 全部被 `is_drug_effective` 拦截（拦截即不进入送礼行为，道具不消耗）。
- [x] 送礼口上（v4）：4 个口上文件编译进 config_talk 且条数正确（35 为受精/妊娠各 5 条）；`CVP_A1_Gift|35_G_0` 前提在 `behavior.gift_id==35` 时返回 1、否则 0；四药效果分支不再触发任何二段行为；二段行为 1325~1328 已从 config 消失。
- [x] 旧存档兼容：缺 `acceleration_days` 键的旧卵字典 `.get` 兜底按 0 加速；旧行为对象缺 `gift_egg_id` 字段 `getattr` 兜底不崩溃；save_handle 回填代码就位（源码断言）。
- [x] `buildconfig.py` 全量重建无报错，config 中新道具/素质/礼物/二段行为/前提/口上全部齐备。

### 7.2 游戏内整体测试（由用户执行）

- [ ] 商店可购买 4 种新药；礼物面板药物折叠组内正常显示/灰显。
- [ ] 对受精与妊娠干员送妊娠加速药：先弹目标的专属二段口上、再显示系统提示（本次/累计/新预计临盆日）；总览面板与身体信息面板日期同步变化；当晚睡觉后阶段按新天数推进。
- [ ] 四种药生效时的专属二段口上均正常弹出（ArkEditor 为角色写的专属口上可覆盖默认口上）。
- [ ] 对多卵干员送孵化加速药：选卵列表正确、单卵时跳过选择；提示与总览面板破壳日一致。
- [ ] 假孕药：孕肚口上/纸娃娃地文/听肚子指令对假孕角色生效；H 内射不受精；终止药恢复。
- [ ] Tk 与 Web 两种绘制模式均正常；旧存档载入不报错。

## 8. 风险与回滚

| 风险 | 说明 | 对策 |
| --- | --- | --- |
| 天数注入漏点 | 加速只改了部分计算点导致结算与显示不一致 | §2.3 引用清单已穷举（fertilization_time 消费 5 处、lay_time 经 get_hatch_day 单点）；统一走 helper，实施后 grep 复核无裸 `.days` 残留 |
| 加速越界 | 一剂药把孕程直接推入临盆/破壳 | 三重夹取（§3.3），单元测试覆盖边界 |
| 假孕素质误清真孕孕肚 | debug 手改等异常状态 | 终止药清 26 前判 `talent[21]==0`；假孕药条件要求 26==0 |
| 存档兼容 | 旧存档缺新字段/卵缺新键 | save_handle 回填 + `.get` 兜底 + 单测构造缺字段对象 |
| 结算期目标卵失效 | 选卵后、结算前卵被其他路径消耗 | 结算内兜底校验，查无此卵则提示并跳过效果 |
| 编号冲突 | 道具/素质编号被并行开发占用 | 实施时现场核对（§5 前置检查） |

**回滚**：本计划各改动单元相互独立可整体回退——CSV 行删除 + 代码分支删除 + 字段保留（存档中已写入的 `acceleration_days`/卵键为普通数值，留存无害）；回滚后需重跑 buildconfig。

## 9. 改动文件清单

| 文件 | 类型 | 改动 |
| --- | --- | --- |
| `data/csv/Item.csv` | 修改 | 新增道具 35~38 四行 |
| `data/csv/Gift_Items.csv` | 修改 | 新增礼物 35~38 四行（type 11） |
| `data/csv/Talent.csv` | 修改 | 新增素质 25【假孕孕肚】 |
| `Script/Core/game_type.py` | 修改 | PREGNANCY.acceleration_days、卵字典 docstring、behavior.gift_egg_id |
| `Script/Core/save_handle.py` | 修改 | 回填 acceleration_days |
| `Script/UI/Panel/gift_panel.py` | 修改 | is_drug_effective / select_gift 选卵 / handle_drug_use_effect 各 4 分支 |
| `Script/System/Pregnancy_System/pregnancy_handle.py` | 修改 | 天数 helper、剂量函数、3 处计时替换、假孕豁免、受精清零 |
| `Script/System/Pregnancy_System/egg_handle.py` | 修改 | add_egg 新键、get_hatch_day 注入、可加速卵筛选函数 |
| `Script/System/Pregnancy_System/born_event_panel.py` | 修改 | 产后清零加速 |
| `Script/System/Pregnancy_System/pregnancy_panel.py` | 修改 | 预计日期扣减加速 |
| `Script/UI/Panel/body_info_panel.py` | 修改 | 天数显示走 helper（+可选假孕描述行） |
| `Script/Core/constant_promise.py` | 修改 | 新增 FAKE_INFLATION_* 4 个前提常量 |
| `Script/Design/handle_premise/handle_premise_other.py` | 修改 | 新增 4 个假孕前提函数；4 个既有 INFLATION 前提改并联判定 |
| `data/talk/daily/gift/give_gift_pregnancy_accelerate.csv` | 新增 | v4：妊娠加速药送礼口上（受精/妊娠两分支各 5 条） |
| `data/talk/daily/gift/give_gift_hatch_accelerate.csv` | 新增 | v4：孵化加速药送礼口上（药液倒在卵壳上吸收，5 条） |
| `data/talk/daily/gift/give_gift_fake_pregnancy.csv` | 新增 | v4：假孕药送礼口上（5 条） |
| `data/talk/daily/gift/give_gift_fake_pregnancy_end.csv` | 新增 | v4：假孕终止药送礼口上（5 条） |
| `tools/ArkEditor/csv/Item.csv` / `Gift_Items.csv` / `Talent.csv` / `Premise.csv` | 修改 | 副本同步（Premise 含 4 新行 + 4 行 info 改文案） |

**未改动**（v4 起）：Behavior_Data / Behavior_Effect / constant 三常量文件 / second_pregnancy.csv / ArkEditor Behavior_Data.csv——v3 曾改动、v4 已全部回退至 plan_14 实施前状态；InstructConfig（复用送礼指令全链，无新指令）；送礼行为本体与 GIVE_GIFT_ADD_ADJUST 结算（新药沿用既有挂接）；h_item_shop_panel（商店自动收录）；egg_handle 的鉴定资格判定（§2.3 ⚠️）；common_default 的妊娠好感加成（§2.4，假孕不享受）；old_chara_to_new 多周目迁移（§2.9，自动兼容）。

## 10. 不在本 Plan 范围

- 90/260/265 天基础孕程数值与既有概率公式的任何调整。
- ~~四种药物的专用二段行为与专用口上~~——**v3 已移入范围**（§2.10 调查、§3.7 设计、§5.9 步骤，每行为默认口上约 5 条）。
- 假孕状态的日常风味口上/事件的**大规模**文本仍不在范围——§3.6 前提组与 §3.7 二段行为已备好，口上作者后续可随时按 `fake_inflation_*` 前提补写。
- 假孕角色的断面图差分（断面图由 talent21/22 驱动，假孕不显示妊娠断面，维持现状）。
- AI 纸娃娃地文无需新增生成要求文档：孕肚地文经 INFLATION 前提消费，方案 B 的并联判定使假孕角色自动复用既有孕肚地文；四个新二段行为仅加地文占位行（§3.7），其地文生成要求文档不在本期。
- 假孕角色不享受妊娠期好感/信赖加成（§2.4，维持现状，不改 common_default）。
- 无壳卵生（12）的差异化实现。

## 11. 口径确认记录（2026-08-25，全部已确认）

| # | 问题 | 用户确认结果 | 方案落点 |
| --- | --- | --- | --- |
| 1 | 假孕素质联动 | **方案 B：仅赋予/移除素质 25**，4 个 INFLATION 前提改为 `26 or 25` 并联判定，talent26 保持真孕专属 | §3.1、§3.6、§5.8 |
| 2 | 妊娠加速药适用种族 | **限定胎生**（`get_birth_type==1`；卵生干员使用孵化加速药） | §3.4 |
| 3 | "最多加速到临盆/破壳前一天" | **硬夹取实装**：入账量三重取小（公式量 / 250−已累计 / 259−有效孕期天数，卵为 264−有效孵化天数） | §3.3 |
| 4 | 假孕配套口上前提 | **新增 4 个**（`fake_inflation_0/1`、`t_fake_inflation_0/1`，含 ArkEditor 同步） | §3.6、§5.8 |

以下小项采用推荐默认（实施时可微调，无需再确认）：

| 项 | 采用口径 |
| --- | --- |
| 孵化加速药剂量公式 | 与妊娠加速药完全一致（270 基数、30%、250 上限） |
| 目标仅一枚可加速卵时 | 跳过选卵直接选中 |
| 新药等级/价格 | 照 31~34 先例：level 3、price 200 |
| 假孕与好感/信赖妊娠加成 | 不享受（维持 common_default 现状） |
| debug 面板显示加速值 | 可选项，实施时定 |

## 12. 执行记录（2026-08-26）

### 12.1 实际改动

§9 清单逐文件核对，全部按计划落地，无遗漏文件、无计划外文件。编号类实际分配值与建议值全部一致（实施时已现场核对空闲）：

| 编号类 | 实际分配 |
| --- | --- |
| 道具/礼物 cid | 35 妊娠加速药 / 36 孵化加速药 / 37 假孕药 / 38 假孕终止药（Item.csv 与 Gift_Items.csv 同号，type=11） |
| 素质 cid | 25 假孕孕肚（type 0，不可遗传） |
| 二段行为 cid | 1325 pregnancy_accelerate / 1326 hatch_accelerate / 1327 fake_pregnancy / 1328 fake_pregnancy_end（均挂 998） |
| 口上 cid | second_pregnancy.csv 61~65 / 71~75 / 81~85 / 91~95（每行为 5 条）+ 地文占位 1325~1328 |
| 前提 cid | fake_inflation_0/1、t_fake_inflation_0/1；另改造既有 inflation_0/1、t_inflation_0/1 为并联判定 |
| 新增函数 | pregnancy_handle：`get_pregnancy_past_day` / `get_acceleration_amount` / `get_pregnancy_acceleration_amount` 及常量 `PREGNANCY_TOTAL_DAY=270`、`ACCELERATION_MAX_DAY=250`、`PARTURIENT_DAY=260`；egg_handle：`get_egg_acceleration_amount` / `get_accelerable_hatching_eggs`；gift_panel：`Gift_Panel.select_target_egg` / `select_egg_id` |
| 数据结构 | `PREGNANCY.acceleration_days: float`、卵字典键 `acceleration_days`、`CharacterBehavior.gift_egg_id: int`（save_handle 回填 acceleration_days，其余 `.get`/`getattr` 兜底） |

### 12.2 与计划的偏差

1. **buildpo/buildmo 未执行**：本机无 xgettext（GNU gettext 未安装）且 `.conda` 环境无 polib 模块，翻译词条提取与 MO 编译无法在本环境运行，留待用户的常规本地化流程执行。不影响游戏内中文原文显示。
2. **地文占位块现状与文档记载不符**（记录于此，非缺陷）：`second_pregnancy.csv` 既有地文占位实际只覆盖 1313~1321（工作流文档《妊娠系统.md》记载 1322~1324 也有占位，实际没有）。本次按计划为新增 4 个行为补齐了 1325~1328 的占位行，1322~1324 的缺口未顺手补（不在本 Plan 范围）。
3. debug 面板显示 acceleration_days 的可选项未做（§11 小项表标注"可选"，从简）。
4. 其余与计划无偏差。

### 12.3 测试结果

- **无头单元测试 107 项全部通过**（模式 A 自建 fixture，测试脚本在会话 scratchpad 中运行后即弃，不入库），分组覆盖：
  - A 注册断言（道具/礼物/素质/二段行为/前提/口上/998 效果器/save_handle 回填源码/born_event_panel 清零源码，共 33 项）
  - B 剂量公式与三重上限（81 → 56.7 → 封顶 250 → 封顶后拒绝；自然 200 天夹取 59；有效 259 拒绝，共 7 项）
  - C 胎生计时注入（9+81 转妊娠；89/90 天回归；180+80 临盆；200+65 生产事件必中触发；新受精清零加速，共 8 项）
  - D 卵计时注入（含加速孵化天数；旧卵缺键兜底；夹取 64；可加速筛选；卵 250 封顶；200+65 破壳触发；add_egg 新键，共 7 项）
  - E 假孕结算跳过与前提组（受精率清零及文案；必中概率下仍不受精；标记消费；INFLATION 并联/FAKE_INFLATION 交叉验证，共 15 项）
  - F 药物使用条件矩阵（四药 × 有效/无效路径，含卵生种族/上限/已假孕等 13 项）
  - G 药物效果与二段行为（加速入账与叠加、选中卵独立、gift_egg_id 消费重置、卵失效兜底、旧行为对象缺字段兜底、25/26 素质变化、四个二段行为经 must_show 链路触发并归零、系统提示文本，共 18 项）
  - H 选卵交互（单卵跳过、多卵取消、无卵拒绝，共 3 项）
  - （其余为各分组内的细分断言）
- `buildconfig.py` 全量重建无报错（含 572 个口上文件与 210 个纸娃娃地文文件的重新处理）。
- §7.2 游戏内整体测试由用户执行，遗留清单见 §7.2。

### 12.4 v4 修改记录（2026-08-26，用户验收修正：口上改挂送礼一段行为）

用户验收指出：药物生效的口上不应新造二段行为，应像其他药剂一样挂在 `give_gift` 一段行为上（口上文件放 `data/talk/daily/gift/`）；并补充口径：孵化加速药的药液由干员**倒在卵壳表面、由卵吸收**。改动明细：

| 改动 | 内容 |
| --- | --- |
| 回退 v3 二段行为方案 | Behavior_Data / Behavior_Effect / ArkEditor Behavior_Data 各删 1325~1328 四行；SecondBehavior / SecondBehavior_Int / Behavior 三常量文件各删 4 常量；second_pregnancy.csv 删 61~95 段 20 条口上与 1325~1328 地文占位；`handle_drug_use_effect` 移除全部二段行为触发调用——相关文件相对 v3 前零残留（git diff 复核） |
| 新增送礼口上 | 4 个新文件共 25 条（35 药按受精/妊娠两分支各 5 条），premise 用参数化 token `CVP_A1_Gift|3X_G_0`（+`CVP_A2_T|20/21_E_1` 差分），零前提代码；文本按"扩充赠礼的代码文本"prompt 撰写（无 BOM、CRLF、无 ASCII 逗号、句号后 `\n` 校验通过） |
| 文档与日志同步 | 本文件 §2.10/§3.7/§5.9/§7.1/§9 按 v4 重写；`礼物系统.md` 增补药物清单 35~38、§3.3 药物礼物对话、效果流程图、特殊限制与数据结构；`妊娠系统.md` 新增 §15 怀孕相关药物（含 §12 药物对话与 §13 流程/时间节点的关联修订）；update.log 第 4 条改为送礼口上表述 |

- 与计划的偏差：①单条文本字数未全部达到 prompt 的 650 字下限（实测 25 条中约半数在 500~649 区间，其余达标），经用户确认"只差一点问题不大"后收尾；②文本由实施方直接撰写，未调用 text-generation 子代理。
- 回归测试：**62/62 全部通过**（注册与回退断言 30 项、CVP 礼物前提求值 3 项、剂量/计时回归 8 项、假孕回归 3 项、药物效果无二段行为 11 项、条件与选卵抽查 7 项）；`buildconfig.py` 全量重建无报错（口上文件 572→576）。
- 遗留：§7.2 游戏内整体测试（新增验证点：送四种药时弹出对应送礼口上且先于效果提示；泌乳药等旧药口上不受影响）；buildpo/buildmo 本地化步骤仍待用户环境执行（§12.2-1）。

### 12.5 后续修改（随 plan_17 第 1 次修改，2026-08-29）

本 Plan §3.3 / §5.7 所述的预计日期写法 `fertilization_time + timedelta(days=260 − acc)`、`lay_time + timedelta(days=265 − acc)` 与 `get_pregnancy_past_day` / `get_hatch_day` 的裸 `(now − t).days` 计算，已统一改为复用 `game_time.get_sub_date(day=…, old_date=…)`（自动归并到 3/6/9/12 四季月）与 `game_time.count_day_for_datetime(start, end)`；妊娠加速药/孵化加速药提示、选卵列表与怀孕总览面板的日期显示改用春夏秋冬月名（`pregnancy_panel.get_date_text` → "夏月30日"）。原因、改动明细与回归测试（93/93）见 `plan/done/plan_17_养成系统三种新药物.md` §12.5；本文原文不改写。

随 plan_17 第 2 次修改（同日），本文 §5.4 所述定义在 `pregnancy_handle.py` 顶部的 `PREGNANCY_TOTAL_DAY / ACCELERATION_MAX_DAY / PARTURIENT_DAY` 与 `egg_handle.py` 的 `HATCH_TOTAL_DAY` 已迁移到子系统统一常量文件 `Script/System/Pregnancy_System/pregnancy_constant.py`（另新增 `ACCELERATION_RATE=0.3` 命名原剂量公式中的字面量），所有引用改为 `pregnancy_constant.X`，见 plan_17 §12.6。

随 plan_17 第 4 次修改（同日），**孵化加速药（36）改为只能在育儿室中使用**（与成长加速药一致）：`is_drug_effective` 的 36 分支首条判定改为 `handle_premise.handle_in_nursery(0)`，不满足时提示"只能在育儿室使用孵化加速药"且不消耗道具；Item.csv 与 ArkEditor 副本的道具描述加注"需要在育儿室中使用"。本文 §3.4 使用条件表中 36 号的条件以此为准，见 plan_17 §12.8。

随 plan_17 第 6 次修改（同日），本文 §3.7 的四个口上文件各补充了**幼女（102）/ 萝莉（103）外表年龄差分**（35 号为受精/妊娠 × 两档共 20 条，36/37/38 号各 10 条，总条数 80/40/40/40），前提写法与既有 104~107 分支同构，见 plan_17 §12.10。
