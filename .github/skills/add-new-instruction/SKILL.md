---
name: add-new-instruction
description: 为 erArk 新增一个玩家指令及其行为、前提、结算、口上的完整实施流程，含一段行为与二段行为的选型区分。当需要新增游戏指令、行为、二段行为、或为指令补齐前提/结算/口上时使用。
---

# Skill Instructions

你是 erArk 的指令系统实施助手。当用户要求新增一个玩家指令（或为既有指令补齐配套）时，按以下步骤依序实施。完整原理说明见仓库内文档 `.github/prompts/数据处理工作流/新增指令工作流.md`；二段行为与口上原理另见 `.github/prompts/数据处理工作流/口上系统.md`。

## 行为选型：一段行为与二段行为（动工前必须先定）

**含义区分：**
- **一段行为**：角色在时间轴上"正在做的事"，由指令触发（`handle_instruct.py` → `chara_handle_instruct_common_settle(constant.Behavior.XXX)`），`Behavior_Data.csv` 中 `duration` 为实际耗时分钟数。
- **二段行为**：不是行动，是结算阶段挂在角色身上的**反应/衍生结算标记**——`duration=0`、`trigger=npc`、`tag=二段结算`（cid 集中在 1300+ 段）。由任意结算代码调 `second_behavior.character_get_second_behavior(character_id, "en_name")` 置 1，在 `settle_behavior.handle_settle_behavior` 末尾的 `check_second_effect` 中出口上、跑效果、归零。既有例：受精 `fertilization`、刻印升级 `happy_mark_1`、初见 `first_meet`、身体道具持续效果。

**口上区别：**
- 一段行为口上：`data/talk/` 分类目录，结算时 `talk.handle_talk` **先于**数值/效果结算显示，一次行为一条；同一行为的场景差分靠前提（含参数化 CVP token，零前提代码）。
- 二段行为口上：`data/talk/system/second_*.csv`，由 `talk.handle_second_talk` 在 `check_second_effect` 中显示——晚于一段口上与主结算，且一次结算可多条并发（每个激活的二段行为各一条）。

**选型准则：**
- 效果发生在**指令行为本身的瞬间、且只由该指令触发** → 不建二段行为，口上挂一段行为 + 前提差分。礼物/药剂类一律如此：premise 写 `CVP_A1_Gift|<礼物id>_G_0`（读 `behavior.gift_id`），文件放 `data/talk/daily/gift/` 一药一文件。
- 反应**可由多种指令/多个来源在结算期触发，或触发时机与具体指令解耦**（数值阈值驱动、跨行为共用）→ 新增二段行为（实施要点见文末附录）。
- ⚠️ 反例警示：plan_14 曾把四种怀孕药物的生效口上误建为 4 个新二段行为，验收后整体返工改挂 `give_gift` 一段行为。

## 实施步骤

### 第一步：选号核对（必须最先做）

1. 指令 cid 按类型分段：系统1-99 / 日常1001 / 工作2001 / 娱乐3001 / 技艺4001 / 猥亵5001 / 性爱6001，在 `data/csv/InstructConfig.csv` 目标段落确认空闲号。
2. 行为 cid 必须在**三处**都空闲：`data/csv/Behavior_Data.csv`、`Script/Core/constant/Behavior_Int.py`、`tools/ArkEditor/csv/Behavior_Data.csv`。⚠️ 这三处存在历史不同步（同一编号含义不同），不能只看一处。
3. 若用行为结算器，效果 id 在 `Script/Core/constant_effect.py` 中确认空闲。

### 第二步：CSV 配置

1. `data/csv/InstructConfig.csv` 加行（14 列）。关键列：`h_mode_show_type`（0全显/1仅非H/2仅H）、`premise_set`（`|`分隔）、`behavior_id`（大写常量名）。
2. 同一功能需要 H 与日常都可用时：**拆两条指令共用一个行为**（H 版 SEX 类 + `TARGET_IS_H`；非H版 OBSCENITY 类 + `_daily` 后缀 + `NOT_H` + 合意前提如 `T_NORMAL_56_OR_UNCONSCIOUS_FLAG`）。先例：`clyster`/`continue_clyster`。
3. `data/csv/Behavior_Data.csv` 加行为（`duration` 分钟数；玩家专属指令 `trigger` 填 `pl`）。
4. `data/csv/Behavior_Introduce.csv` 加行为介绍。
5. `data/csv/Behavior_Effect.csv` 加行挂效果 id。⚠️ **即使结算不走行为结算器，也必须挂空结算 `9999`**——`settle_behavior.py` 只对存在于该表的行为触发口上。

### 第三步：常量（全部手工维护）

照既有条目位置逐个添加：`Script/Core/constant/Behavior.py`、`BehaviorStr.py`、`Behavior_Int.py`、`CharacterStatus.py`（`STATUS_` 前缀）、`Script/System/Instruct_System/Instruct.py`（⚠️ 本文件定义顺序决定 Web 指令显示顺序）。

### 第四步：处理函数与面板

1. `Script/System/Instruct_System/handle_instruct.py` 加 `@add_instruct(constant.Instruct.XXX)` 函数，内部调 `chara_handle_instruct_common_settle(constant.Behavior.XXX)`。
2. 需要玩家二次选择时用**内联模态面板**：面板 `.draw()` 返回 -1 表示取消，处理函数据此直接 return（不结算不耗时）。参考 `Script/System/Item_System/condom_panel.py`；面板只用 `Script/UI/Moudle/draw.py` 的抽象绘制类以兼容 Web 模式。
3. 需要对方"接受"的指令加**实行值判定**：`chara_handle_instruct_common_settle(..., judge = _("严重骚扰"))`（难度档位见 `data/csv/InstructJudge.csv`，失败自动替换为失败行为）。⚠️ 若面板确认时会直接结算数据，judge 必须**前置到打开面板之前**手动调 `instuct_judege.calculation_instuct_judege(0, 目标id, _("严重骚扰"))`：-1 → return；0 → 结算失败行为 `constant.Behavior.HIGH_OBSCENITY_ANUS` 后 return；通过 → 开面板，最终通用结算不再传 judge（避免二次判定）。参考 `handle_condom_instruct_common`。

### 第五步：结算

二选一：
- **行为结算器**：`constant_effect.py` 加常量 → `Script/Settle/` 对应文件加 `@settle_behavior.add_settle_behavior_effect` 函数（首行 `if not add_time: return`）→ `Behavior_Effect.csv` 挂接 → 同步 `tools/ArkEditor/csv/Effect.csv`（四列 `cid,effect_name,effect_type,effect`，`effect_type` 填与常量 docstring 首词一致的分类词）。
- **面板直接结算**：结算函数写在子系统 handle 模块中（如 `condom_handle.settle_*`），面板确认时直接调用；`Behavior_Effect.csv` 挂 `9999`。副作用：数值变化不进入行动结算展示。

**效果 id 选号与分类**（`BehaviorEffect` 按数字分段，docstring 格式 `""" 分类 说明 """`，新 id 必须插进对应分类段内相邻位置，勿追加到文件末尾）：
1. 通用数值优先不新增 id：能用既有效果 id、CVE 综合数值结算 token（`Behavior_Effect.csv` 里直接写 `CVE_A1_E|80_G_1` 形式字符串，零代码）或 `common_default.py` 通用函数解决的，不加新常量。
2. 新指令的专属结算逻辑 → **501~547 指令_专用结算** 段选空闲号，函数写在 `Script/Settle/default.py`。
3. 其他常用段速查：0~40 与 1501~1531 属性_基础 / 41~89 属性_状态 / 110~146 属性_状态特殊补正 / 301~374 特殊flag_基础 / 451~489 特殊flag_H / 601~654 属性_服装（函数在 `default_cloth.py`）/ 800~868 H_阴茎位置与体位 / 901~1063 道具（函数在 `item_effect.py`）/ 1201~1246 源石技艺 / 1401~1419 属性_H / 1701~1726 行动 / 9999 空结算。
4. ⚠️ 二段行为效果是 `SecondEffect` 独立编号空间（函数在 `Second_effect.py`，装饰器 `add_settle_second_behavior_effect`），与 `BehaviorEffect` 编号互不相干，勿混用（空结算 999 vs 9999 即一例）。

数值增减优先走 `Script/Settle/common_default.py` 通用函数；精液污浊唯一入口 `ejaculation_panel.update_semen_dirty(..., update_shoot_position_flag=False)`。

### 第六步：前提

1. **先查重**：优先用现成前提或参数化 CVP token（解析在 `handle_premise/__init__.py`，支持 A能力/T素质/E经验/S状态/F好感/X信赖/G攻略度/Gift礼物id 等；如 `CVP_A2_T|20_E_1` 交互对象素质20==1、`CVP_A1_F_GE_2000` 好感≥2000、`CVP_A1_Gift|35_G_0` 当前礼物id==35），能覆盖就不新增前提。
2. `Script/Core/constant_promise.py` 加枚举：值为小写字符串 cid，docstring 格式 `""" 分类 说明 """`——首词分类决定归属段（约 70 类，如 系统状态/地点_定位/属性_能力/素质_妊娠/特殊flag_无意识/H_绝顶/初次_素质/道具_使用），新前提插到同分类相邻条目旁，勿追加到文件末尾。
3. `Script/Design/handle_premise/` 按主题选模块加 `@add_premise` 函数（返回 1/0）：19 个主题文件 `handle_premise_<主题>.py`（H / ability / arts / assistant / base_value / body_manage / cloth / dirty / entertainment / fall / first / food / last_cmd / other / place / sp_flag / talent / time / work），选与分类词对应者。
4. 同步 `tools/ArkEditor/csv/Premise.csv`（四列 `cid,premise_name,premise_type,premise`，`premise_type` 填与 docstring 相同的分类词）。

### 第七步：口上

**7a 一段行为口上**：`data/talk/` 按分类目录建 CSV（五列 `cid,behavior_id,adv_id,premise,context`，表头 5 行照抄同目录文件）。`behavior_id` 填行为小写 en_name（共用行为的指令自动共用口上）；`premise` 填前提小写 cid（默认 `high_1`）；文本用 `{Name}`/`{TargetName}` 占位符。显示时机：`talk.handle_talk` 在结算数值前触发，一次行为一条。cid 无跨文件冲突问题（buildconfig 自动加文件名前缀），各文件从 1000 起编号即可。需要按场景区分文案时优先用现成参数化 CVP token（如 `CVP_A1_Gift|35_G_0` 礼物id、`CVP_A2_T|20_E_1` 交互对象素质）；无现成 token 再走：结算里往 `SPECIAL_FLAG` 写标记 → 为标记做一对前提 → 口上各行分配对应前提。

**7b 二段行为口上**（仅当选型为二段行为时）：`data/talk/system/second_*.csv` 建条目（同五列格式），`behavior_id` 填二段行为小写 en_name；由 `talk.handle_second_talk` 显示，晚于一段口上与主结算。⚠️ NPC 不与玩家同场景时二段行为默认被丢弃（不显示不结算）；需跨场景生效的，在 `Behavior_Effect.csv` 挂 `998`（必须显示）或 `997`（必须计算但不显示）代替普通空结算 `999`（三者都是 `constant_effect.SecondEffect` 的空白结算，先例：`fertilization` 挂 998、`first_meet` 挂 999）。

### 第八步：数据结构与存档兼容（如有新数据）

挂载位置按生命周期选择：
- ⚠️ **勿放 `BODY_H_STATE`**（H 结束时 `get_h_state_reset` 整体重建，数据会丢）
- 角色身上的可见状态 → `DIRTY`（`get_dirty_reset` 原地重置，重置范围逐字段显式列出：新字段需随洗澡等污浊重置清空的，要在该函数中显式加入；否则可存续）
- 玩家持久收集 → `PLAYER_COLLECTION`；瞬时标记 → `SPECIAL_FLAG`

新增字段必须在 `Script/Core/save_handle.py:175` 附近的逐角色回填段加 `hasattr` 兜底，数据访问函数内也做兜底回填。

清零/去除时机常用挂点："下次H开始" → `default.py` 的 `handle_h_flag_to_1` 首次进H分支；"换衣/脱衣" → `clothing.py` 四个换装函数 + `default_cloth.py` 两个入柜结算；"洗澡/污浊重置" → 在 `attr_calculation.get_dirty_reset` 中显式清空。

### 第九步：构建与验证

1. `python buildconfig.py` **必跑**（漏跑启动 KeyError）；新翻译词条再跑 `buildpo.py` + `buildmo.py`。
2. 单元测试脚本要点：**先** `cache_control.cache = game_type.Cache()` **再** import 其他模块；`normal_config.init_normal_config()` + `game_config.init()`；角色 fixture 用 `attr_calculation.get_dirty_reset` / `get_cloth_wear_zero` / `get_talent_zero` 初始化。
3. 注册断言：`constant.handle_instruct_data` / `instruct_premise_data` / `handle_premise_data` / `game_config.config_behavior` / `config_behavior_effect_data` 包含新增项。
4. 游戏内测试可开 debug 模式（config.ini `debug=1`，跳过全部前提）。

## 附录：新增二段行为的实施要点

选型确定为二段行为时，按此清单实施（替代上面第二~七步中的一段行为路线）：

1. `data/csv/Behavior_Data.csv` 加行：cid 在 1300+ 段选空闲号，`duration=0`、`trigger=npc`、`tag=二段结算`。
2. 常量三处照既有条目位置添加：`Script/Core/constant/SecondBehavior.py`、`SecondBehavior_Int.py`、`Behavior.py`。
3. 在结算代码的触发点调 `second_behavior.character_get_second_behavior(character_id, "en_name")`（可在 `Script/Settle/`、`second_behavior.py`、各子系统 handle 中，视反应来源而定）。
4. `data/csv/Behavior_Effect.csv` 必须加行：有数值效果挂对应效果 id（`Script/Settle/Second_effect.py` 中 `@add_settle_second_behavior_effect` 注册）；无数值效果挂空结算 `999`（⚠️ 二段行为的空结算是 999，不是一段行为的 9999）；需跨场景生效改挂 `998`/`997`（见 7b）。
5. 口上按第七步 7b 建 `data/talk/system/second_*.csv` 条目。
6. 同步 `tools/ArkEditor/csv/Behavior_Data.csv`。
7. `python buildconfig.py` 后验证：`game_config.config_behavior` 含新 cid、`config_behavior_effect_data` 含新 en_name、（如挂了 997/998）`config_behavior_must_settle_cid_list`/`config_behavior_must_show_cid_list` 含新 en_name。

## 完整案例

避孕套道具系统：`plan/wait/plan_06_避孕套道具系统.md`（8 轮执行记录）与 `Script/System/Item_System/道具系统设计文档.md`。
一段/二段行为选型与礼物药剂口上：`plan/done/plan_14_怀孕系统四种药物.md`（含二段行为方案返工为一段口上方案的完整记录）。
