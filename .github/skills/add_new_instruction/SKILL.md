---
name: add-new-instruction
description: 为 erArk 新增一个玩家指令及其行为、前提、结算、口上的完整实施流程。当需要新增游戏指令、行为、或为指令补齐前提/结算/口上时使用。
---

# Skill Instructions

你是 erArk 的指令系统实施助手。当用户要求新增一个玩家指令（或为既有指令补齐配套）时，按以下步骤依序实施。完整原理说明见 [新增指令工作流](../../prompts/数据处理工作流/新增指令工作流.md)。

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
- **行为结算器**：`constant_effect.py` 加常量 → `Script/Settle/` 对应文件加 `@settle_behavior.add_settle_behavior_effect` 函数（首行 `if not add_time: return`）→ `Behavior_Effect.csv` 挂接 → 同步 `tools/ArkEditor/csv/Effect.csv`。
- **面板直接结算**：结算函数写在子系统 handle 模块中（如 `condom_handle.settle_*`），面板确认时直接调用；`Behavior_Effect.csv` 挂 `9999`。副作用：数值变化不进入行动结算展示。

数值增减优先走 `Script/Settle/common_default.py` 通用函数；精液污浊唯一入口 `ejaculation_panel.update_semen_dirty(..., update_shoot_position_flag=False)`。

### 第六步：前提

1. `Script/Core/constant_promise.py` 按分类段加枚举（值为小写字符串）。
2. `Script/Design/handle_premise/` 按主题选文件加 `@add_premise` 函数（返回 1/0）。
3. 同步 `tools/ArkEditor/csv/Premise.csv`。

### 第七步：口上

`data/talk/` 按分类目录建 CSV（五列 `cid,behavior_id,adv_id,premise,context`，表头 5 行照抄同目录文件）。`behavior_id` 填行为小写 en_name（共用行为的指令自动共用口上）；`premise` 填前提小写 cid（默认 `high_1`）；文本用 `{Name}`/`{TargetName}` 占位符。需要按场景区分文案时：结算里往 `SPECIAL_FLAG` 写标记 → 为标记做一对前提 → 口上各行分配对应前提。

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

## 完整案例

避孕套道具系统：`plan/wait/plan_06_避孕套道具系统.md`（8 轮执行记录）与 `Script/System/Item_System/道具系统设计文档.md`。
