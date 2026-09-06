# E1 BUG 与漏洞检查

## 何时用

- 方案的挂钩点、数据结构、数值都已基本定下，用户开始问"还有什么漏的 / 会不会有 BUG"。
- 方案新增了存档字段、新行为/前提/效果、或改动了全体角色每天必跑的链（睡觉、跨天、实时结算）。
- 方案触及任何一种特殊状态（时停、催眠、无意识、睡眠、群交、隐奸、监禁、跟随、助理）。
- **不适合**：方向未定、还在比较候选方案时（先用 B1/B4）；纯文案/口上改动且不新增前提时（用 D5 即可）。

## 怎么做

1. 先读计划 §3/§4 已定的挂钩点与新字段，列出"本方案会写到的数据 + 会被调用的时机"。
2. 对照下方固定清单**逐项过一遍**，每项只有三种结论：不涉及 / 涉及且已有对策 / 涉及且待处理。
3. 每条"涉及"的结论都必须 grep 或读代码拿到依据位置；拿不到依据的写"疑似，待实施时核实"，不写成事实。
4. 把"涉及且待处理"的项按严重度排序，最严重的 1~2 条作为本轮提问抛给用户（附推荐对策）。
5. 写进 §2.3（机制层陷阱）与 §7（风险 | 说明 | 对策）；不要在两处重复写同一句，§2.3 写"为什么会出问题"，§7 写"怎么防"。

固定清单（每条附已核实的落点）：

| # | 检查项 | 落点 | 典型漏洞 |
| --- | --- | --- | --- |
| 1 | 存档兼容 | `Script/Core/save_handle.py:266 _normalize_loaded_save_paths` 内逐角色 `hasattr` 回填段（:299~358），设置类走 `:704 update_settings`；`:601 update_dict_with_default` 只能补顶层默认值 | 新字段挂在旧对象上，旧档载入后 `AttributeError`；dict 型字段补空 dict 后 `[key]` 仍 KeyError |
| 2 | Tk/Web 双模式 | `Script/System/Web_Draw_System/web_draw_adapter.py:605 apply_web_adapters` 只包装 `Script/UI/Moudle/draw.py` 的抽象绘制类 | 面板直接拼 Tk 控件或 HTML，另一模式下不显示 |
| 3 | NPC AI 目标链 | `Script/Design/handle_npc_ai.py:277 find_character_target`；前置检查 `:182 judge_assistant_character` / `:205 judge_character_follow` / `:239 judge_character_cant_move` / `:652 judge_interrupt_character_behavior` | 新前提让某状态下 NPC 没有任何可选 target → 卡在 SHARE_BLANKLY |
| 4 | 行为循环收敛 | `Script/Design/character_behavior.py:38 init_character_behavior`，`:50/:69` 用 `cache.over_behavior_character` 计数收敛，`:272 judge_character_status_time_over` 决定何时加入 | 行为 `duration` 永远不结束或 `start_time` 被重置成过去 → 死循环（plan_13 §2.6-7：`.seconds` 对负 timedelta 返回 86340） |
| 5 | 时停 | `character_behavior.py:59 if cache.time_stop_mode`（玩家行动后时间回滚，NPC 不行动）；前提 `constant_promise.py:2633 PRIMARY_TIME_STOP` | 时停中触发的实时结算/二段行为被回滚吞掉，或反而重复累加 |
| 6 | 催眠 / 无意识 | `game_type.py:793 sp_flag.unconscious_h`（1 睡眠…7 心控）；前提 `constant_promise.py:1610 UNCONSCIOUS_FLAG_1`、`:1608 UNCONSCIOUS_HYPNOSIS_FLAG` | ⚠️ plan_13 §2.6-1：`unconscious_flag_ge_1` 是真值判定，`else` 分支会吃进催眠态；反感结算对意识模糊者静默 return（`common_default.py:214/217`） |
| 7 | 睡眠 | `game_type.py:821 sp_flag.sleep`；前提 `:259 SCENE_SOMEONE_SLEEPING`、`:860 SLEEP_DISTURBED_0`；实时结算 `realtime_settle.py:548 settle_sleep_h` | 入睡瞬间 `sp_flag.sleep` 已是 0（效果 321），CD 挂错入口会让角色一小时什么都做不了（plan_13 §2.6-6） |
| 8 | 群交 / 隐奸 / 监禁 | `game_type.py:1900 cache.group_sex_mode`、`:795 sp_flag.hidden_sex_mode`、`:817 sp_flag.imprisonment`；前提 `:22 GROUP_SEX_MODE_ON`、`:1667 PLAYER_IN_HIDDEN_SEX_MODE`、`:1523 IMPRISONMENT_1` | 新指令没加 `NOT_H`/隐奸排除，在群交或隐奸中弹出普通面板 |
| 9 | 跟随 / 助理 | `game_type.py:805 sp_flag.is_follow`；前提 `:1470 IS_FOLLOW`、`:1216 IS_ASSISTANT` | 跟随者被强制移动后没同步（`handle_npc_ai.py:733 judge_same_position_npc_follow`） |
| 10 | 编号占用 | 行为 cid 三处：`data/csv/Behavior_Data.csv`、`Script/Core/constant/Behavior_Int.py`、`tools/ArkEditor/csv/Behavior_Data.csv`（历史不同步）；效果 id `Script/Core/constant_effect.py` 按分类分号段；前提 cid `Script/Core/constant_promise.py` | ⚠️ plan_06 §8.1：计划里的建议号实施时已被占用；效果 id 追加到文件末尾会落错分类 |
| 11 | 边界值 | 空集合 / 0 / 负数 / 上限；罩杯素质 121~125 一个都没有时 `UnboundLocalError`（`headless-game-test` fixture 表） | 好感字典没有 `[0]`、`favorability[0]` 直接下标 |
| 12 | 重复触发与幂等 | 同一行为在 `character_behavior.py:145` 与 `:177` 两处都会走实时结算；二段行为在 `second_behavior.py:81 check_second_effect` 末尾归零 | 每次结算都累加的"一次性"奖励；清除函数第二次调用再报一次（plan_21 §6.1 有"清除幂等"专项） |
| 13 | 跨天与多周目 | `Script/Settle/past_day_settle.py:31 update_new_day`（:49 遍历 `cache.npc_id_got`）；多周目 `Script/UI/Panel/new_round.py`（继承项 :37~49），`game_type.py:1698 first_record_history` / `:1902 game_round` | 跨天字段没清 → 第二天仍算"今天已做"；新周目 `Cache()` 重建后新字段丢失但继承逻辑没带上 |
| 14 | `BODY_H_STATE` 重建 | `Script/Settle/default.py:4260 handle_self_h_state_reset`（效果 403）在 :4279 调 `attr_calculation.py:273 get_h_state_reset` **整个换新对象**；`default.py:4441 handle_chara_off_line` :4462、`sleep_settle.py:98` 同样 | 挂在 `h_state` 上的新字段 H 一结束就被重建丢掉；要持久的数据不能放这里 |
| 15 | 二段行为跨场景 | `second_behavior.py:180`：NPC 与玩家不同场景时只处理 must_show / must_settle，其余**直接丢弃**；`constant_effect.py:1011 Nothing=999` / `:1013 Must_Show=998` / `:1015 Must_Settle=997` | 远程触发的二段行为（如受精）挂了 999 → 不结算不显示 |
| 16 | 循环导入 | Core → System 方向最危险（plan_21 §7 `save_handle` 导入 `pregnancy_constant`）；惯例是函数内延迟 import（`.github/prompts/数据处理工作流/主场景互动界面.md:123`） | 顶部 import 子系统模块导致游戏启动即报错 |

## 输出格式

```markdown
| 检查项 | 是否涉及 | 依据位置 | 风险与对策 |
| --- | --- | --- | --- |
| 存档兼容 | 涉及 | `file.py:行号 函数名` | <一句风险> → <一句对策，写进 §7> |
| Tk/Web 双模式 | 不涉及 | — | — |
```

只列"涉及"与"疑似"的行进 §2.3；"不涉及"的行可以在对话里一句带过，不进文档。

## 写进计划的哪一节

§2.3（已知陷阱与硬约束：写触发机理与代码落点）+ §7（风险 | 说明 | 对策）。理由：§2.3 是给实施者读的"为什么"，§7 是验收时逐条打勾的"怎么防"，模板要求两者都不可省。

## 例子

取材 `plan/done/plan_04_同房间睡眠者被吵醒判定.md`（v1→v2 修订）与 `plan/done/plan_13_睡觉中被吵醒.md`。

**用户原话**："同房间内的其他人也需要进行被吵醒的判定，方案我觉得差不多了，帮我看看有没有坑。"

**助手调研**：
- 读 `Script/Settle/realtime_settle.py:548 settle_sleep_h` 与 `:521 get_sleep_disturbance_value`，确认吵醒结算在玩家实时结算里跑，遍历的是同场景角色列表拷贝。
- grep `recover_from_unconscious_h` → `Script/Design/handle_npc_ai_in_h.py`，开头 `if target_data.sp_flag.unconscious_h == 0: return`，说明它只能处理睡奸目标（plan_04 §2.3）。
- grep `unconscious_flag_ge_1` → `handle_premise_sp_flag.py:1662`，返回值是 `sp_flag.unconscious_h` 真值，不是 `==1`。
- 读 `character_behavior.py:59` 时停分支，确认时停中不会走 NPC 实时结算。

**产出**：

| 检查项 | 是否涉及 | 依据位置 | 风险与对策 |
| --- | --- | --- | --- |
| 催眠/无意识 | 涉及 | `handle_premise_sp_flag.py:1662` | `else` 会吃进催眠态 4~7，反感结算在 `common_default.py:214/217` 静默 return → `else` 收窄为 `elif unconscious_h == 0` |
| 重复触发 | 涉及 | `realtime_settle.py:569` 遍历拷贝列表 | 两个睡眠者会把玩家连推两格（plan_13 §2.6-3）→ 推出一次后 break |
| 行为循环收敛 | 涉及 | `settle_behavior.py:35 add_time` | 被吵醒后 `behavior.start_time` 若不重置，`.seconds` 对负差返回巨值 → 必须重置为当前时间 |
| 时停 | 不涉及 | `character_behavior.py:59` | 时停中不跑 NPC 实时结算 |
| 存档兼容 | 涉及 | `save_handle.py:356` | 新增 `sleep_disturbed_end_time` 需 hasattr 回填（plan_13 实际落点） |

**抛给用户的问题**：
1. 睡奸目标与普通睡眠者要不要走两条醒来路径？推荐：是，按 `unconscious_h` 分流，睡奸目标沿用 `recover_from_unconscious_h`，避免重复提示（plan_04 §6 风险 1 的结论）。
2. 多个睡眠者同时醒来时是逐条 `WaitDraw` 还是合并成一条？推荐：逐条，与既有醒来说明一致，但 Web 模式要专项验证（plan_04 §5.4-5）。

## 常见误用

- **把清单当问卷全文抄进计划**："存档兼容：无 / 双模式：无 / …" 十六行"无"没有信息量；只写涉及项，并给出依据行号。
- **没查代码就写"可能有并发问题"**：本游戏是单线程回合制，"并发"几乎不成立；每条风险都要能指出"在哪一行、什么输入触发"。
- **只报不解**：列了风险却没有对策与验证方式，用户无法拍板；每行都要带"→ 对策"，并在 §6.1 补一条对应断言。
