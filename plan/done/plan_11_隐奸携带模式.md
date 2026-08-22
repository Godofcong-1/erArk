# Plan 11：隐奸携带模式

- 状态：已完成（单元测试58项全部通过，游戏内整体测试由用户验收通过，2026-08-22）
- 来源：用户需求 → 隐奸中增加「携带」新模式（正面抱位抱起藏于衣下、行走中H、消耗倍增）+ 特殊指令「携带H中移动」
- 预计改动量：约 15 个文件（隐奸面板/体位面板/消耗结算/移动链路/新指令全链路 + CSV/常量/前提）
- 风险等级：中

---

## 1. 目标

1. 隐奸模式选择面板新增**模式5「携带」**：干员固定为**正面抱位（对面抱位）**被玩家抱起，藏在玩家衣服遮盖下，玩家可站立行走中进行H。
2. 进入条件与模式2-4一致：场景中只有两人，或其他人都无意识/睡眠（debug 模式不限制）。
3. **进入时先选择插入部位**：只能选择 V阴道 / A后穴 / U尿道 三者之一（各自沿用对应插入指令的前提：V需无震动棒、A需后穴无异物、U需尿道扩张5级+腰技5级+无采尿器），选定后以对面抱位直接完成插入再进入携带状态；取消选择则退回模式选择。
4. 携带模式下体位**锁定为对面抱位**（cid 9），不可切换其他体位（如后背位）；**不能拔出阴茎**，**不能更换到 V/W/A/U 以外的插入部位**——除对面抱位的 V/W/A/U 直接指令外，换体位面板类指令与所有其他部位的阴茎相关指令（口交、手交、足交、乳交、素股等）全部屏蔽；从 V 可经对面抱位子宫口姦/子宫姦指令**深入 W 子宫**。
5. 携带模式下**双方(玩家与被携带干员)的体力气力消耗均 ×3**。
6. 新增指令**「携带H中移动」**（仅携带模式下可用）：核心是**玩家处于H状态中也能移动**——普通移动 `h_mode_show_type=1`（自动携带 `NOT_H` 前提）在H中本就不可用，携带模式下玩家全程 `is_h=True`，只能经本指令移动。效果同普通移动，但体力气力消耗为**基础值 ×10**（基础值 = 自己小量体力 + 小量气力）；交互对象被一同带到目的地场景。
7. 隐蔽程度倍率 ×1（同女隐）；行走（携带移动）计入隐蔽值**增加**（行走晃动易被察觉），进入有人场景后在场人数照常放大被发现风险。

## 2. 现状调查（关键代码落点）

> 注意：隐奸面板实际路径为 `Script/System/Sex_System/hidden_sex_panel.py`（工作流文档 `隐奸系统.md` 里写的 `Script/UI/Panel/` 已过时）。

| 机制 | 位置 | 要点 |
| --- | --- | --- |
| 模式选择面板 | `Script/System/Sex_System/hidden_sex_panel.py:339-457` `Select_Hidden_Sex_Mode_Panel` | 模式选项为硬编码 `button_text_list`（377-380）；模式2-4 的可选判定在 381-390（`handle_scene_only_two` 或 `handle_scene_all_others_unconscious_or_sleep`）；`select_this_mode`（420）做隐奸实行值判定后设双方 `sp_flag.hidden_sex_mode`，模式1/2 时玩家 `is_h = False`（440-441） |
| 隐蔽值结算 | 同文件 `settle_hidden_value_by_action`（134-200） | `mode_adjust`：模式1×2、模式4×0.5、其余默认1（162-169）；`add_flag` 按行为 tag 猥亵/性爱判定（149-158） |
| 隐奸状态面板 | 同文件 `See_Hidden_Sex_InfoPanel`（约 260-336） | 显示隐蔽程度与体位文本 |
| 隐奸模式前提 | `Script/Design/handle_premise/handle_premise_sp_flag.py:2117-2425` | `handle_hidden_sex_mode_0/1/2/3/4` 及组合、`t_` 目标版；枚举在 `Script/Core/constant_promise.py:1655-1699` |
| 体位数据 | `data/csv/Sex_Position.csv` cid 9 = 对面抱位（`face_hug_sex` 系列，type=抱位） | 玩家 `h_state.current_sex_position`（`game_type.py:449`）；体位切换/初次插入均经 `Script/System/Sex_System/sex_position_panel.py` 的 `Sex_Position_Panel`（遍历体位 62-129，`cant_flag` 灰字机制现成可扩展） |
| HP/MP 消耗唯一入口 | `Script/Settle/common_default.py:28` `base_chara_hp_mp_common_settle` | **既有倍率先例**：60-77 行群交中玩家消耗 `/3`、NPC `/2`（直接乘除 `hp_adjust`/`mp_adjust`），携带倍率插在该分支之后同样写法；`hp_adjust`/`mp_adjust` 在 :80 与 :117 生效 |
| 普通移动 | `data/csv/InstructConfig.csv:6`（cid 1，SYSTEM，panel_id=SEE_MAP）；`handle_instruct.py:463-466` 只切地图面板；实际移动 `Script/Design/character_move.py:30` `own_charcter_move`（54-60 硬编码 `behavior_id = constant.Behavior.MOVE`）；结算效果 751 `handle_move_to_target_scene`（`Script/Settle/default.py:763-801`），**当前移动无任何体力消耗** |
| 消耗效果常量 | `Script/Core/constant_effect.py:99-120` | `DOWN_SELF_SMALL_HIT_POINT`=1511、`DOWN_SELF_SMALL_MANA_POINT`=1514（即 `face_hug_sex` 行为已挂的那对，见 `Behavior_Effect.csv:271`） |
| 隐奸中指令过滤 | `handle_instruct.py:133-152`（h_mode_show_type 自动前提）、`see_instruct_panel.py:193-213`（硬过滤） | 本方案只需给 cid 1 移动加前提，不动硬过滤 |
| 隐奸模式清零点 | `hidden_sex_panel.py:234`（被发现）、`Script/Settle/default.py:4248`（H结束重置）、`:5276`（效果1213）、`handle_npc_ai_in_h.py:125` | 模式5 复用同一字段，清零链路自动覆盖，无需新增 |
| 新增指令工作流 | `.github/prompts/数据处理工作流/新增指令工作流.md` + `/add-new-instruction` skill | 选号需三处核对（InstructConfig / Behavior_Data / Behavior_Int.py 及 ArkEditor 副本） |

存档兼容：只扩展既有字段 `hidden_sex_mode` 的取值域（0-4 → 0-5），**不新增任何数据字段**，无需改 `save_handle.py`。

## 3. 实施步骤

### 3.1 模式5选项与进入流程（`hidden_sex_panel.py` `Select_Hidden_Sex_Mode_Panel`）

- `button_text_list` 追加：`[5]携带：干员以对面抱位被博士抱起，藏在博士的衣服遮盖下，可以边走边做，但博士的体力气力消耗大幅增加`
- 可选判定沿用 `i >= 1` 分支（与模式2-4完全一致）；**从被发现面板跳转时（`sex_be_discovered_flag`）模式5不可选**（此时可能已在其他部位插入，无法满足携带的插入要求）
- 面板顶部提示文本补充携带模式说明（需先选插入部位、无法拔出、体位固定、消耗倍率）
- **新增方法 `select_carry_insert_part()`**：模式5点击后先绘制插入部位选择（V阴道/A后穴/U尿道 + 返回），携带模式的两条说明文本（部位选择/无法拔出/体位固定、消耗倍率/携带移动）在此面板顶部显示（不在模式选择 `draw()` 里）；各部位可选条件与对应插入指令前提一致（V：`handle_target_not_vibrator_insertion`；A：`handle_target_a_empty`；U：`handle_target_not_urine_collector` + `handle_t_u_dilate_ge_5` + `handle_waist_technique_ge_5`），并统一判定**对面抱位的体位要求**（与 `sex_position_panel` 一致：`config_sex_position_data[9]` 的 `skill_req` 对比博士腰技 `ability[76]`；对面抱位 `furniture_req=0` 恒满足，家具判定省略），不满足时全部位灰字并显示原因文本（如"(需要博士腰技至少为5级)"）；debug 不限制；取消返回 -1 退回模式选择
- `select_this_mode`：
  - 模式5 时先调 `select_carry_insert_part()`，取消则中止
  - 模式5 时玩家 `is_h = True`（携带即H状态中的持续插入，玩家全程处于H中；`ask_hidden_sex` 行为只有效果464给交互对象置H，玩家侧需在此显式置位。注意**不同于**模式1/2的 `is_h = False`）
  - 模式5 时重置 `current_sex_position = -1`，随后结算 `ASK_HIDDEN_SEX` 后**紧接结算所选部位的对面抱位插入行为**（`config_sex_position_data[9]` 的 `vaginal/anal/urethral_sex_behavior_id`，即 `face_hug_sex`/`face_hug_anal_sex`/`face_hug_urethral_sex`，均带效果859自动把体位设为对面抱位），`force_taget_wait=True`、不再传 judge（隐奸实行值判定已在邀请时通过，避免中途失败导致进入模式但未插入）

### 3.2 体位与插入部位锁定

- **体位面板**（`sex_position_panel.py:62-129`）：遍历体位时追加判定——玩家 `sp_flag.hidden_sex_mode == 5` 且 `sex_position_id != 9`（对面抱位）→ `cant_flag = True`，文案追加 `(携带中只能使用对面抱位)`
- **指令屏蔽**（`InstructConfig.csv`，共38条追加前提 `NOT_HIDDEN_SEX_MODE_5`）：
  - `6019 pull_out_penis` 拔出阴茎（携带中不能拔出）
  - `6302/6318/6332/6346/6363` 五个换体位面板指令（携带中不可换体位，面板内也无可选项，直接屏蔽入口）
  - `6601-6632` 全部32个其他部位阴茎相关指令：手交/口交/乳交/足交/发交/腋交/素股/手交口交/乳交口交/真空口交/深喉插入/清洁口交/六九式/腿交/尾交/蹭脸/蹭角/蹭耳/帽子交/眼镜交/耳饰交/脖饰交/口罩交/上衣交/胸衣交/手套交/裙子交/裤子交/内裤交/袜子交/鞋子交/武器交
- **天然屏蔽（无需改动）**：其他体位的直接插入指令（如后背位6304）前提含 `DR_POSITION_*`，体位锁定在9后不匹配；初次插入指令（6301/6345/6362）前提含 `DR_POSITION_NULL`，携带中体位恒为9也不匹配
- **保留可用**：对面抱位 V/W/A/U 直接指令（6311 对面抱位、6327 对面抱位子宫口姦、6341 对面抱位子宫姦、6355 对面抱位肛交、6372 对面抱位尿道姦）及体位无关的插入系指令（刺激G点6315、玩弄子宫口6316、玩弄s状结肠6359、隔着刺激阴道6360）——V→W 深入通过 6327/6341 实现，不依赖换体位面板

### 3.3 消耗倍率（`Script/Settle/common_default.py`，群交分支 :68-77 之后）

```python
# 隐奸携带模式中双方消耗增加
if handle_premise.handle_hidden_sex_mode_5(character_id):
    # 玩家的携带H中移动消耗×10
    if character_id == 0 and character_data.behavior.behavior_id == constant.Behavior.CARRY_MOVE:
        hp_adjust *= 10
        mp_adjust *= 10
    # 其他所有指令双方消耗均×3
    else:
        hp_adjust *= 3
        mp_adjust *= 3
```

与群交倍率同一位置、同一写法（直接乘 `hp_adjust`/`mp_adjust`），语义一致（仅作用于消耗方向）。玩家与被携带干员均生效（双方 `hidden_sex_mode` 在进入模式时都被置 5，直接按 `character_id` 自身判定即可）；×10 仅限玩家执行携带移动时。

### 3.4 新指令「携带H中移动」全链路（按 `/add-new-instruction` 工作流）

1. **选号**：InstructConfig 取 SYSTEM 段空闲 cid；行为取 `Behavior_Data.csv` / `Behavior_Int.py` / ArkEditor 副本三处均空闲的号（实施时核对）
2. **`data/csv/InstructConfig.csv`**：
   - 新行 `carry_move 携带H中移动`，type=SYSTEM，`h_mode_show_type=0`（H界面中也显示，这是本指令的核心——H中可移动），`tired_type=0`，前提 `HIDDEN_SEX_MODE_5`，behavior_id 留空，`panel_id=SEE_MAP`（与移动同款：点击后进地图面板选目的地）
   - cid 1 `move` 行**无需修改**：其 `h_mode_show_type=1` 自动携带 `NOT_H` 前提，携带模式下玩家与对象均处于H状态，普通移动天然不可用
3. **`data/csv/Behavior_Data.csv` / `Behavior_Introduce.csv`**：新行为 `carry_move 携带H中移动`，duration=1（实际时长由寻路动态写入），trigger=pl
4. **`data/csv/Behavior_Effect.csv`**：`carry_move` 挂 `751 - 1511 - 1514`（场景迁移 + 自己小量体力 + 自己小量气力；经 3.3 ×10）
5. **常量五件套**：`Script/Core/constant/Behavior.py`、`BehaviorStr.py`、`Behavior_Int.py`、`CharacterStatus.py`、`Script/System/Instruct_System/Instruct.py` 各加 `CARRY_MOVE` / `携带H中移动`
6. **处理函数**（`handle_instruct.py`，仿 `handle_move` :463-466）：

   ```python
   @add_instruct(constant.Instruct.CARRY_MOVE)
   def handle_carry_move():
       cache.now_panel_id = constant.Panel.SEE_MAP
   ```

7. **行为写入**（`Script/Design/character_move.py` `own_charcter_move` :54-60）：设置 `behavior_id` 处按模式分支——玩家 `sp_flag.hidden_sex_mode == 5` 时用 `constant.Behavior.CARRY_MOVE`，否则 `MOVE`（地图面板选点是共用入口，靠此分支区分行为）
8. **携带交互对象同行**（`Script/Design/handle_npc_ai.py` `judge_same_position_npc_follow` 内）：遍历 `cache.npc_id_got`，对 `sp_flag.hidden_sex_mode == 5` 的被携带角色，经 `map_handle.character_move_scene` **直接搬运位置**到玩家本段移动的目的地（`pl.behavior.move_target`），不使用移动行为、不改变其行为数据（保持H等待锁）。配套两处：
   - `Script/Design/character_behavior.py` 玩家移动特殊结算的触发条件由 `== MOVE` 扩为 `in {MOVE, CARRY_MOVE}`（跟随结算与目击H重置对携带移动同样生效）
   - `Script/Design/handle_npc_ai_in_h.py` 场景分离重置分支对 `hidden_sex_mode == 5` 豁免（跟随结算与玩家751结算的先后可能产生同一tick内的短暂分离，不做H状态清零）
   - 时序：跟随结算与玩家751结算在玩家同一个行为pass内先后执行，NPC阶段开始前双方已同步到达，无可观察的分离状态；`Script/Settle/default.py` 的751结算保持原样不改
9. **口上**：`data/talk/` 下新增 `carry_move.csv`（标准5列表头），写 3-5 条默认口上（`premise=high_1`，如「{Name}把藏在衣服下的{TargetName}紧紧搂住，迈开脚步——每一步都让两人的结合处紧紧研磨着」）

### 3.5 新前提（`constant_promise.py` + `handle_premise_sp_flag.py`，仿既有 `handle_hidden_sex_mode_4`）

| 前提 | 判定 |
| --- | --- |
| `HIDDEN_SEX_MODE_5` | 自己 `sp_flag.hidden_sex_mode == 5` |
| `NOT_HIDDEN_SEX_MODE_5` | 自己 `sp_flag.hidden_sex_mode != 5` |
| `T_HIDDEN_SEX_MODE_5` | 交互对象 `sp_flag.hidden_sex_mode == 5`（供口上/事件用） |

同步 `tools/ArkEditor/csv/Premise.csv`。既有组合前提（`handle_hidden_sex_mode_ge_1` 等用 `> 0` / `in {...}` 判定的）逐个核对是否需把 5 纳入（如 `_2_or_4` 类按「干员是否隐藏」语义决定是否加 5）。

### 3.6 隐蔽值与状态显示（`hidden_sex_panel.py`）

- `settle_hidden_value_by_action`：模式5 的 `mode_adjust` 保持默认 1（同女隐，不用改倍率代码）；在 `add_flag` 判定处对 `CARRY_MOVE` 特判 `add_flag = True`（行走计入隐蔽值增加，强度按默认 1）
- `See_Hidden_Sex_InfoPanel`：模式5 时追加一行携带状态文本（如「正把{干员名}藏在衣服下抱着行动」）
- `game_type.py:765-766` `hidden_sex_mode` 的 docstring 取值域更新为 `[0否,1双不隐,2女隐,3男隐,4双隐,5携带]`

### 3.7 边界核对（实施时逐项确认）

- 被发现结算 `settle_discovered`（:223）与三处模式清零点对模式5的兼容（字段复用，预期零改动，跑通即可）
- `cache.achievement.hidden_sex_record`（:438）写入 mode_id=5 后成就统计代码不因未知模式报错
- 携带移动进入有人场景后 `handle_hidden_sex_flow` 的发现判定正常触发（这正是玩法预期风险）
- NPC AI 不会让被携带干员自行行动/离开（与模式2-4同款 `settle_chara_unnormal_flag(target, 3)`，预期零改动）
- 结束隐奸（6006 `hidden_sex_end`）在携带模式下可用，结束后体位与消耗倍率恢复正常

## 4. 构建与缓存重建

```bash
python buildconfig.py   # CSV/常量改动后必跑
python buildpo.py       # 新指令名/口上词条
python buildmo.py
```

本机运行须用 `.conda\python.exe`（裸 `python` 是 Store 空壳别名）。

## 5. 验证清单

### 5.1 单元测试（实施方执行）

- [x] 前提函数：`hidden_sex_mode` 为 0/4/5 时三个新前提返回正确
- [x] 消耗倍率：构造双方 mode=5，调 `base_chara_hp_mp_common_settle`，玩家与干员普通行为消耗均为基准×3、玩家 `CARRY_MOVE` 为基准×10（干员不套用×10）；mode=0 不受影响
- [x] `own_charcter_move` 在 mode=5 时写入 `CARRY_MOVE`、否则 `MOVE`
- [x] `judge_same_position_npc_follow`：mode=5 时被携带NPC被直接搬运到玩家本段移动目的地、行为保持等待、场景 `character_list` 同步、重复调用无副作用；非携带非跟随NPC不受影响；751结算已无携带搬运代码
- [x] `handle_npc_ai_in_h`：场景分离重置分支对 mode=5 豁免
- [x] `select_carry_insert_part`：含携带说明文本与对面抱位体位要求判定；模式选择 `draw()` 已不含携带说明文本
- [x] 被发现面板：接收 `from_hidden_sex_flag` 参数，转隐奸选项与顶部描述按隐奸上下文判定；`settle_discovered` 在统计发现者后清零双方隐奸标记并传递上下文（功能测试：双方 mode=5 被发现后标记均清零）
- [x] `settle_hidden_value_by_action`：`CARRY_MOVE` 走增加分支，等待走减少分支
- [x] 指令屏蔽：38条被屏蔽指令的前提集合均含 `not_hidden_sex_mode_5`；对面抱位 V/W/A/U 直接指令与体位无关插入指令不含该前提；`move` 不含该前提（靠 `NOT_H` 天然屏蔽）
- [x] 模式5入口给玩家置 `is_h = True`
- [x] 隐奸模式选择面板存在 `select_carry_insert_part` 方法且模式5入口先走部位选择、结算插入行为
- [x] `python buildconfig.py` 全量重建无报错，新常量/前提/行为/效果/口上在生成物中齐备（`config_behavior` / `config_instruct_by_id` / `config_behavior_effect_data` / `config_talk_data` 均含 `carry_move`）

（以上共43项断言，含三次调整的 is_h/前提检查，2026-08-22 全部通过）

### 5.2 游戏内整体测试（由用户执行）

- [ ] 场景仅两人时模式5可选，有清醒第三人时灰字；debug 模式不限制；从被发现面板跳转时模式5灰字
- [ ] 选择模式5后先出现 V/A/U 部位选择（不满足前提的部位灰字，如后穴有异物时A不可选），取消可退回；确认后直接完成对面抱位插入并进入携带
- [ ] 携带中：拔出阴茎、换体位类指令、口交/手交/足交等其他部位阴茎指令全部不显示；对面抱位子宫口姦/子宫姦可深入W
- [ ] 进入携带模式后：玩家处于H状态（H界面），体位面板只能选对面抱位；普通移动指令不可见（H中天然屏蔽），「携带H中移动」在H界面中可见可用
- [ ] 携带移动：目的地正常到达、干员跟随、行动结算显示体力气力大量消耗（×10）
- [ ] 携带中其他指令（猥亵/性爱等）双方消耗均为平时×3
- [ ] 走进有人场景后隐蔽值上升、可被发现，被发现后打断/转群交流程正常
- [ ] 隐奸（含携带）被发现进入被发现面板时：顶部描述为"你和XX的隐奸"，且**没有**"[2]迅速地隐藏起来，转为隐奸"选项；普通H被发现时 [2] 正常显示
- [ ] 结束隐奸后消耗恢复、体位可自由切换；Tk 与 Web 两模式均正常；旧存档载入正常

## 6. 风险与回滚

- **消耗倍率误伤恢复类结算**：倍率写在群交倍率同一位置，沿用其只影响消耗方向的语义；实施时确认 `hp_adjust`/`mp_adjust` 不参与恢复（UP）路径
- **组合前提遗漏**：`handle_hidden_sex_mode_ge_1` 等用范围判定的前提会自动含 5，但 `_1_or_2` 之类显式枚举的不含；按语义逐个核对（3.5）
- **移动共用入口**：地图面板与 751 结算被普通移动/NPC移动共用，分支必须严格限定 `character_id == 0` 且 mode==5，避免影响 NPC 寻路
- **漏跑 buildconfig**：启动 KeyError；CSV/常量改动后必跑
- **回滚**：还原代码与 CSV 新增行、重跑 `buildconfig.py` 即可；无新增存档字段，存档天然兼容

## 7. 改动文件清单

| 文件 | 类型 | 改动 |
| --- | --- | --- |
| `Script/System/Sex_System/hidden_sex_panel.py` | 修改 | 模式5选项/说明文本、`select_this_mode`（is_h、体位重置）、`select_carry_insert_part`、隐蔽值 `CARRY_MOVE` 特判、状态面板携带文本、`settle_discovered` 清零双方标记并传递隐奸上下文 |
| `Script/System/Sex_System/sex_be_discovered_panel.py` | 修改 | 新增 `from_hidden_sex_flag` 参数，转隐奸选项与顶部描述按隐奸上下文判定 |
| `Script/System/Sex_System/sex_position_panel.py` | 修改 | 携带模式下仅对面抱位可选 |
| `Script/Settle/common_default.py` | 修改 | 携带模式双方消耗 ×3 / 玩家携带移动 ×10 |
| `Script/Design/character_move.py` | 修改 | `own_charcter_move` 按模式写入 `CARRY_MOVE` |
| `Script/Design/handle_npc_ai.py` | 修改 | `judge_same_position_npc_follow` 直接搬运被携带角色到玩家本段移动目的地 |
| `Script/Design/handle_npc_ai_in_h.py` | 修改 | 场景分离重置分支对携带模式豁免 |
| `Script/Design/character_behavior.py` | 修改 | 玩家移动特殊结算条件扩为 `{MOVE, CARRY_MOVE}` |
| `Script/System/Instruct_System/handle_instruct.py` | 修改 | `handle_carry_move` |
| `Script/System/Instruct_System/Instruct.py`、`Script/Core/constant/Behavior.py` / `BehaviorStr.py` / `Behavior_Int.py` / `CharacterStatus.py` | 修改 | `CARRY_MOVE` 常量 |
| `Script/Core/constant_promise.py`、`Script/Design/handle_premise/handle_premise_sp_flag.py` | 修改 | 3 个新前提 |
| `Script/Core/game_type.py` | 修改 | `hidden_sex_mode` docstring 取值域 |
| `data/csv/InstructConfig.csv` / `Behavior_Data.csv` / `Behavior_Introduce.csv` / `Behavior_Effect.csv` | 修改 | `carry_move` 指令/行为/效果；38条指令（拔出阴茎+5换体位+32其他部位阴茎指令）追加 `NOT_HIDDEN_SEX_MODE_5`；`move` 行不改（H中靠 `NOT_H` 天然屏蔽） |
| `data/talk/carry_move.csv` | 新增 | 携带移动默认口上 |
| `tools/ArkEditor/csv/Behavior_Data.csv` / `Premise.csv` | 修改 | 编辑器副本同步 |
| `data/data.json`、`Script/Config/config_def.py`、`data/po/` | 重建 | 由 `buildconfig.py` 生成 |

## 8. 执行记录（2026-08-22）

### 8.1 编号分配

| 项目 | 编号 |
| --- | --- |
| 指令 cid | **19**（SYSTEM 段，1-18 已占用） |
| 行为 cid | **7**（`Behavior_Data.csv` / `Behavior_Int.py` / ArkEditor 副本三处均空闲） |
| 前提 | `hidden_sex_mode_5` / `not_hidden_sex_mode_5` / `t_hidden_sex_mode_5`（无新增效果 id，复用 751/1511/1514） |

### 8.2 与计划的偏差

1. **携带对象同行的实现**：计划原文用 `get_hidden_sex_targets(0)` 获取对象，但该函数只扫描玩家**当前**场景——玩家先行迁移后对象还留在旧场景，会找不到。实际改为遍历 `cache.npc_id_got` 中 `sp_flag.hidden_sex_mode == 5` 的角色（携带对唯一，语义等价且不受场景时序影响）。
2. **组合前提并入**：`hidden_sex_mode_2_or_4` / `t_hidden_sex_mode_2_or_4`（口上中语义为"干员处于隐藏状态"）已并入模式5，携带模式可复用现有口上；`_1_or_3`（干员不隐藏）与 `_3_or_4`（博士隐藏，用于指令硬过滤和初见招呼跳过）语义不符，未并入。docstring 与 ArkEditor `Premise.csv` 描述同步更新。
3. **本地化构建**：本机缺 `xgettext`（gettext 工具链）与 `polib` 包，`buildpo.py` / `buildmo.py` 无法运行；CSV 侧 PO 已由 `buildconfig.py` 生成，代码内新增 `_()` 文本均为中文原文，zh_CN 下功能不受影响。
4. **`carry_move` 行为 tag 用「日常」**（非「性爱」），隐蔽值增加通过 `settle_hidden_value_by_action` 中对 `CARRY_MOVE` 的特判实现，避免「性爱」tag 触发其他 H 逻辑。

### 8.3 二次调整（同日，用户需求）

1. **进入即插入**：模式5点击后先经 `select_carry_insert_part()` 选择插入部位（仅 V阴道/A后穴/U尿道，各自沿用对应插入指令的前提做可选判定，debug 不限制；取消退回），确认并通过隐奸实行值判定后，在 `ASK_HIDDEN_SEX` 结算后紧接结算对面抱位对应部位的插入行为（不再传 judge，避免中途失败导致进入模式但未插入）。从被发现面板跳转时模式5不可选。
2. **禁止拔出与更换部位**：38条指令追加 `NOT_HIDDEN_SEX_MODE_5` 前提（`6019 拔出阴茎`、`6302/6318/6332/6346/6363` 换体位、`6601-6632` 其他部位阴茎指令）；W 子宫深入经对面抱位直接指令（6327/6341）保留可用；其他体位直接指令与 `DR_POSITION_NULL` 初插指令靠体位锁定天然屏蔽。
3. 修改由脚本批量完成并保持 CSV 原编码（UTF-8 无 BOM）与换行不变。

### 8.3.1 三次调整（同日，用户需求）

「携带H中移动」的重点是**玩家已处于H状态中也能移动**（普通移动 `h_mode_show_type=1`、自动携带 `NOT_H`，H中本就不可用）。据此修正：

1. 模式5入口改为给玩家显式置 `is_h = True`（此前误照抄模式2的 `is_h = False`；`ask_hidden_sex` 行为只有效果464给交互对象置H，玩家侧不会被自动置位），携带全程为H状态、H界面。
2. 撤销 `move` 行（cid 1）追加的 `NOT_HIDDEN_SEX_MODE_5` 前提——携带中双方均为H状态，`NOT_H` 已天然屏蔽普通移动，该前提冗余。`NOT_HIDDEN_SEX_MODE_5` 前提本身保留注册（38条屏蔽指令仍在使用）。

### 8.3.2 四次调整（同日，用户需求）

1. **携带同行结算迁移**：被携带角色的移动结算从 `Script/Settle/default.py` 的 `handle_move_to_target_scene`（751）移到 `Script/Design/handle_npc_ai.py` 的 `judge_same_position_npc_follow()`。按用户澄清，**沿用原本"直接搬运位置"的方式**（`map_handle.character_move_scene` 仅移动位置），不改用移动行为结算；搬运目标为玩家本段移动的目的地 `pl.behavior.move_target`。配套：`character_behavior.py` 玩家移动特殊结算条件扩为 `{MOVE, CARRY_MOVE}`；`handle_npc_ai_in_h.py` 场景分离重置分支对模式5豁免（跟随结算与751结算的先后在极端时序下可能产生同tick内短暂分离）。751结算恢复原样。
2. **说明文本迁移**：模式选择面板 `draw()` 中针对携带模式的两条 `info_text` 移到 `select_carry_insert_part()` 顶部显示。
3. **部位选择时的体位要求判定**：`select_carry_insert_part()` 中统一判定对面抱位的体位要求（与 `sex_position_panel` 一致：家具需求对比场景家具等级、`skill_req=5` 对比博士腰技 `ability[76]`），不满足时全部位灰字并显示原因文本。

### 8.3.3 五次调整（同日，用户实测反馈）

**问题**：携带隐奸被发现进入 `Sex_Be_Discovered_Panel` 时，依旧可以选择"[2]迅速地隐藏起来，转为隐奸"。

**原因**：`settle_discovered` 在打开被发现面板**之前**就把玩家的 `hidden_sex_mode` 清零（`hidden_sex_panel.py`），而面板中 [2] 选项的判定 `not handle_hidden_sex_mode_ge_1(0)` 查的正是玩家标记——此时恒为0，判定形同虚设（模式1-4同样受影响，顶部"你和XX的隐奸"描述也因此失效，显示为"单独H"）。

**修正**：
1. `Sex_Be_Discovered_Panel.__init__` 新增 `from_hidden_sex_flag: bool = False` 参数显式传递隐奸上下文；[2] 选项判定追加 `not self.from_hidden_sex_flag`，顶部描述判定追加 `or self.from_hidden_sex_flag`。普通H被发现的调用方（`StateMachine/default.py`）走默认 `False`，不受影响。
2. `settle_discovered` 在清零标记前记录 `from_hidden_sex_flag` 并传给面板；同时改为**双方**（玩家+隐奸对象）标记一并清零——原先只清玩家侧，对方标记残留会使携带模式的消耗×3、场景分离豁免等效果异常延续（效果472/473只挂在转群交/转露出行为上，[1]支开/[5]结束路径不清对方标记）。
3. 时序注意：可打断者列表必须在清零对方标记**之前**统计（`get_nearby_conscious_unfallen_characters` 以"不在隐奸中"过滤，若先清零会把隐奸对象自己计入发现者）。

### 8.4 单元测试结果

测试脚本（scratchpad，不入库）以"初始化配置与缓存后直接调用函数"的方式覆盖 5.1 全部条目，含二至五次调整的指令屏蔽/进入流程/is_h/携带搬运迁移/体位要求判定/被发现面板修正检查，共 **58 项断言全部通过**（2026-08-22）。注意事项：项目导入链（web 相关模块）会启动非守护线程，测试脚本需用 `os._exit` 退出，否则进程结束后悬挂。

### 8.5 已知边界

- 射精面板中的射精位置选择不受携带限制约束（与"无法拔出"的指令级约束互不干扰），如需一并限制另行处理。
- Web 模式下部位选择子面板复用抽象绘制类，经 `web_draw_adapter` 自动兼容，未做专门渲染器。
- 携带移动时若目标场景路径含多段，每段的玩家行为pass内都会先经跟随结算把对象搬运到本段目的地、再由玩家751结算到达，NPC阶段开始前双方已同步；极端时序下的短暂分离由 `handle_npc_ai_in_h.py` 场景分离重置分支的模式5豁免兜底，不会清零H状态。
