# Plan 09：进食高品质精液食物绝顶时结算饮精绝顶经验

- 状态：**已实施**（2026-08-22，单元测试全通过，游戏内测试待用户执行，见 §11）
- 来源：用户需求 → “进食高品质食物时，可能会有较高的快感结算，导致绝顶，此时如果是精液食物则加饮精绝顶经验”
- 追加需求：用户要求把 §3.5 原本备案不改的既有行为（素质 31 持有者不再累计经验 111）在本次修改中一并处理
- 预计改动量：1 个文件（`Script/Settle/default.py`，新增 3 行）
- 实际改动量：2 个文件
  - `Script/Settle/default.py` 新增 4 行（2 行注释 + 2 行代码）—— 主需求，与预计一致
  - `Script/Settle/orgasm_settle.py` 净 +5 行 —— §3.5 追加需求
- 风险等级：低（无新增数据结构/CSV/前提，无存档兼容问题）
- 适用代码快照：`master @ 5c99fa57f`（v2026.8.21-2）

---

## 1. 目标

让干员在进食**精液调味食物**（调味 11 巧妙混入 / 12 直接射上去）并因该次进食发生**部位绝顶**时，结算 **饮精绝顶经验（经验 id 111）**，从而与既有的“口内射精 → 绝顶 → 饮精绝顶经验 → 累计 50 点获得[饮精绝顶]素质”成长链打通。

附带（同一处改动的必然联动，符合素质设定）：拥有素质 **31 精爱味觉/饮精绝顶**（配表说明：“尝到精液的味道就会条件反射性地绝顶”）的干员，进食精液食物时将条件反射性地触发一次不计次绝顶。

## 2. 现状调查

### 2.1 进食结算链路

```text
指令 1010 eat（InstructConfig.csv:33）
  → handle_instruct.py:450 handle_eat()  仅打开面板
  → Cooking_System/food_bag_panel.py:448 FoodBagPanel.eat_food(uid)
       behavior.target_food = now_food
       behavior.behavior_id = constant.Behavior.EAT
  → settle_behavior.py:20 handle_settle_behavior()
       Behavior_Effect.csv:33  135,eat,516
       constant_effect.py:450  EAT_ADD_ADJUST = 516
  → Script/Settle/default.py:7639 handle_eat_add_just()      ← 唯一的进食结算点
  → settle_behavior.py:426 / :440  second_behavior.check_second_effect(...)
  → second_behavior.py:121  orgasm_settle.orgasm_judge(character_id, change_data)
```

NPC 自主进食走状态机 `StateMachine/default.py:2358 character_eat_rand_food()`，同样设 `Behavior.EAT`，最终汇入同一个 `handle_eat_add_just`。

### 2.2 高品质食物的快感结算（已存在，本 Plan 不动）

`Script/Settle/default.py:7699-7715`：

```python
# NPC吃的时候
if chara_id:
    ...
    # 高品质食物
    if food_quality >= 7:
        # 变为好心情
        handle_mood_to_good(chara_id, add_time, change_data, now_time)
        # 增加口喉快感
        base_chara_state_common_settle(chara_id, state_add * 3, 21, 0, change_data_to_target_change = change_data)
        # 增加心理快感
        base_chara_state_common_settle(chara_id, state_add * 2, 23, 0, change_data_to_target_change = change_data)
```

- `food_quality` 是**品质数值 0~8**（= 制作者料理技能 `ability[43]`，精细烹饪答题最高 +4），而非 `Food_Quality.csv` 的 5 档 cid；`>= 7` 即“美味/绝珍”档。
- `state_add` 来自 `Cooking_System/food_bag_panel.py:21 calculate_food_effects()`：
  `state_add = int(add_time * (quality/2)**2 * cook_difficulty * add_time_adjust * uniform(0.8,1.2))`，手制额外 ×1.5。品质 8 手制时 `quality_adjust` 可达 24，数值足以跨过多个快感等级。
- `base_chara_state_common_settle` 的第 2 参是 `add_time`、第 4 参是 `base_value`，故此处实际基数为 `state_add*3`（`common_default.py:154`）。
- **玩家（id=0）被 `if chara_id:` 整段跳过**，因此进食绝顶只发生在 NPC 身上；这与下文 2.3 的绝顶结算（玩家走射精槽、NPC 走部位快感）是自洽的。

### 2.3 绝顶判定与饮精绝顶经验的触发条件

`Script/Settle/orgasm_settle.py:37 orgasm_judge()`，NPC 分支遍历 `CharacterState.csv` 中 `type == 0` 的快感状态（0皮肤/1胸部/2阴蒂/3阴茎/4阴道/5肛肠/6尿道/7子宫/21口喉/22兽部/23心理）：

```python
now_data = attr_calculation.get_status_level(character_data.status_data[orgasm])
pre_data = character_data.h_state.orgasm_level[orgasm]
...
# 饮精绝顶                                                    ← :105-110
if orgasm == 21 and character_data.talent[31]:
    if character_data.h_state.shoot_position_body in [2, 15]:
        un_count_data += 1
        character_data.h_state.shoot_position_body = -1   # 当场重置，避免重复触发
...
normal_orgasm_dict[orgasm] = now_data - pre_data
```

以及 `orgasm_settle_in_second_behavior()` 结尾 `:308-311`：

```python
if part_count >= 1:
    # 饮精绝顶经验
    if character_data.h_state.shoot_position_body in [2, 15]:
        base_chara_experience_common_settle(character_id, 111, change_data=change_data)
```

配表佐证：

- `data/csv/Experience.csv:98` → `111,饮精绝顶经验,2`（type 2 = 绝顶经验）
- `data/csv/Talent.csv:31` → `31,0,精爱味觉,0,经常性地在绝顶的同时被口内射精而获得的素质，尝到精液的味道就会条件反射性地绝顶`
- 素质获取：`Script/Design/handle_talent.py:256 npc_gain_semen_drinking_climax_talent()`，门槛 `experience[111] >= 50`，由 `handle_talent.py:83` 调用

> **结论：只要在进食结算内把 `shoot_position_body` 置为 2 或 15，后续的二段绝顶结算会自动完成饮精绝顶与经验 111 的全部逻辑，无需改动 `orgasm_settle.py`。**

### 2.4 精液食物分支为何拿不到经验

`Script/Settle/default.py:7737-7748`：

```python
# 精液食物则将精液加到口腔污浊，并加精液经验
if food_seasoning in {11,12}:
    # 加精液经验和饮精经验
    base_chara_experience_common_settle(chara_id, 24, change_data=target_change)
    base_chara_experience_common_settle(chara_id, 25, change_data=target_change)
    # 获取精液量
    semen_ml = now_food.special_seasoning_amount if now_food is not None else 0
    # 加精液到口腔
    temp_position = cache.shoot_position
    cache.shoot_position = 2    # 口腔
    ejaculation_panel.update_semen_dirty(chara_id, 2, 0, semen_ml, update_shoot_position_flag=False)
    cache.shoot_position = temp_position
```

`update_shoot_position_flag=False` 使 `ejaculation_panel.py:264-269` 的记录段被跳过，`h_state.shoot_position_body` 保持 `-1`，因此 2.3 的两处判定恒不成立。已加的经验 24（精液经验）/ 25（饮精经验）都是 type 6，与绝顶经验 111 是两套。

### 2.5 可复用的既有做法

`Script/System/Item_System/condom_handle.py:229-261 settle_drink()`（Plan 06 产物）处理“喝下避孕套里的精液”，做法完全同构：

```python
# 记录精液射入位置为胃部，以联动饮精绝顶二段行为
target_data.h_state.shoot_position_body = 15
```

即：**直接赋值 `shoot_position_body`，而不是把 `update_shoot_position_flag` 翻成 `True`**。本 Plan 照抄这一写法。

### 2.6 `shoot_position_body` 的生命周期与副作用面

- **重置点**：`Script/Design/character_behavior.py:391 judge_before_pl_behavior()` 在玩家每次行动前把交互对象的 `shoot_position_body` / `shoot_position_cloth` 置回 `-1`；`orgasm_settle.py:110` 触发饮精绝顶后也会当场重置。故本次登记的值只在“本次进食行动的结算 + 随后的 NPC 阶段”内存活。
- **口上前提面**（已实测）：
  - `Premise.SHOOT_IN_T_MOUSE`（`handle_premise_H.py:988`，判 `== 2`）：全仓库 `data/` 下**引用数 0**。
  - 综合前提 `S_ShootPos|B2`（`handle_premise/__init__.py:363-370`）：`data/talk`、`data/talk_common`、`data/event` 下**引用数 0**。
  - 唯一大量使用射精位置的是 `data/talk/system/second_shoot/`，其 `behavior_id` 全部是 `p_orgasm_small`（玩家射精二段行为），进食不会产生该二段行为，**不会误触发**。
- **结论**：登记为 2 在口上层面无副作用。

## 3. 设计决策

### 3.1 方案：在精液食物分支登记射精位置为口腔

在 2.4 的分支末尾追加对 `shoot_position_body` 的赋值，把这条链交回给既有的二段绝顶结算器。收益：

| 效果 | 触发条件 | 由谁实现 |
| --- | --- | --- |
| 加饮精绝顶经验 111 | 本次进食产生了至少一个部位绝顶（`part_count >= 1`） | `orgasm_settle.py:308-311`，无需改动 |
| 触发不计次饮精绝顶 | 干员拥有素质 31 | `orgasm_settle.py:105-110`，无需改动 |
| 累计 50 点后获得[饮精绝顶]素质 | 经验 111 累计 | `handle_talent.py:256`，无需改动 |

### 3.2 为何取 `2`（口腔）而非 `15`（胃部）

两者都能满足 `in [2, 15]`。取 2 的理由：

1. 与同一分支已有的 `update_semen_dirty(chara_id, 2, 0, semen_ml, ...)`（精液污浊写入**口腔**）保持一致，不制造“污浊在口腔、射精位置在胃部”的错位。
2. 契合素质 31 的设定文案“**尝到**精液的味道”。
3. 口上前提引用数为 0（见 2.6），比 15 更干净——`second_shoot_stomach.csv` 有 61 条 `S_ShootPos|B15` 口上（虽然 `behavior_id` 限定为 `p_orgasm_small` 不会误触发，但取 2 可完全规避这一面）。

`condom_handle.settle_drink` 取 15 是因为那里 90% 精液确实进了胃部，与本处场景不同。

### 3.3 加保护：仅在确有精液时登记

`semen_ml` 可能为 0（老存档的食物、或 `special_seasoning_amount` 异常）。仅在 `semen_ml > 0` 时登记，避免“没有精液却算作饮精绝顶”。

### 3.4 不调整现有快感结算范围（用户已确认）

维持 `food_quality >= 7` 才加口喉/心理快感。低品质精液食物不产生快感 → 不绝顶 → 不加经验 111（但素质 31 持有者仍会条件反射绝顶，见 3.1）。

### 3.5 一并修复：素质 31 持有者不再累计经验 111

> 本节原为「已知的既有行为，本 Plan 不改」的备案项，经用户要求在本次修改中一并处理。

**问题**：素质 31 持有者触发饮精绝顶时，`orgasm_settle.py:110` 会**先**把 `shoot_position_body` 重置为 `-1`，`orgasm_judge()` 随后才调用 `orgasm_settle_in_second_behavior()`，导致其 `:310` 的经验 111 判定读到的恒为 `-1`。即：**一旦获得素质 31，经验 111 就永久停止累计**。这是口内射精路径上早已存在的行为。

**为什么值得修**：

1. 经验 111 是 type 2（绝顶经验），会显示在角色信息面板的「经验」栏（`see_character_info_panel.py:843-857`，凡数值 > 0 者均列出）。持有素质后数值被永久冻结在 50 上下，与其余绝顶经验「随绝顶持续增长」的表现不一致，且这一点玩家可见。
2. 本 Plan 新建的「进食精液食物 → 部位绝顶 → 经验 111」链路，在素质 31 持有者身上会因同一原因整条落空，与 §3.1 的设计意图直接矛盾——而素质 31 持有者恰恰是最常触发该链路的人（§1 附带效果：他们进食精液食物必定条件反射绝顶）。

**修法**：不改变「重置以免重复触发」这一意图，只把重置**延后到高潮结算之后**。在 `orgasm_judge()` 的 NPC 分支引入一个局部标记 `drink_semen_orgasm_flag`，触发时只置标记，待 `orgasm_settle_in_second_behavior()` 返回后再重置射精位置。

**为什么不改 `orgasm_settle_in_second_behavior()` 的签名或在其内部重置**：该函数另有两个调用方——`default.py:6809`（时停解放）与 `orgasm_settle.py:352`（寸止解放，实施前为 `:347`）。把重置移入函数体会给这两条路径带来副作用；延后到 `orgasm_judge()` 内则完全局部，两个解放路径的行为一字未变（详见 §11.6 的回归分析）。

## 4. 详细改动步骤

共两个改动点：§4.1 为主需求，§4.2 为 §3.5 的追加需求。两者互相独立，可分别实施与回滚。

### 4.1 主改动点：`Script/Settle/default.py` 的 `handle_eat_add_just()`

精液食物分支（当前 `:7737-7748`）。在 `cache.shoot_position = temp_position` 之后追加：

```python
        # 精液食物则将精液加到口腔污浊，并加精液经验
        if food_seasoning in {11,12}:
            # 加精液经验和饮精经验
            base_chara_experience_common_settle(chara_id, 24, change_data=target_change)
            base_chara_experience_common_settle(chara_id, 25, change_data=target_change)
            # 获取精液量
            semen_ml = now_food.special_seasoning_amount if now_food is not None else 0
            # 加精液到口腔
            temp_position = cache.shoot_position
            cache.shoot_position = 2    # 口腔
            ejaculation_panel.update_semen_dirty(chara_id, 2, 0, semen_ml, update_shoot_position_flag=False)
            cache.shoot_position = temp_position
            # 登记精液进入口腔，使本次进食若因高品质快感而绝顶时，
            # 由二段绝顶结算联动饮精绝顶（素质31）与饮精绝顶经验（111）
            if semen_ml > 0:
                target_data.h_state.shoot_position_body = 2
```

要点：

1. `target_data` 已在循环头 `:7695` 定义为 `cache.character_data[chara_id]`（本轮的进食者），直接复用，**不要**误用外层的 `character_data`（那是行动发起者）。
2. 精液食物的 `eat_food_chara_id_list` 只含 `target_character_id`（`:7681-7682`），即进食者恒为 NPC，与 `orgasm_judge` 的 NPC 分支匹配。
3. 保持 `update_shoot_position_flag=False` 不变——翻成 `True` 会额外写入 `dirty.body_semen_in_unconscious` 的无意识部位记录（`ejaculation_panel.py:267-269`），超出本次需求。
4. 无需 import 新模块，无需新增常量、前提或结算效果 id。

### 4.2 追加改动点（§3.5）：`Script/Settle/orgasm_settle.py` 的 `orgasm_judge()`

三处小改，全部落在 `orgasm_judge()` 的 NPC 分支（`else:` 块）内：

**（1）在遍历快感状态的 for 循环之前声明标记**（`:83` 之后）：

```python
        normal_orgasm_dict = {}  # 高潮结算字典
        extra_orgasm_dict = {}  # 额外高潮结算字典
        un_count_orgasm_dict = {}  # 不计数高潮结算字典
        drink_semen_orgasm_flag = False  # 本次是否触发了饮精绝顶（素质31）
        for state_id in game_config.config_character_state:
```

**（2）饮精绝顶判定处改为只置标记，不再当场重置**：

```python
            # 饮精绝顶
            if orgasm == 21 and character_data.talent[31]:
                if character_data.h_state.shoot_position_body in [2, 15]:
                    un_count_data += 1
                    # 仅登记标记，射精位置的重置延后到高潮结算之后，
                    # 以免 orgasm_settle_in_second_behavior 内的饮精绝顶经验(111)判定读不到射精位置
                    drink_semen_orgasm_flag = True
```

**（3）高潮结算返回后再重置**：

```python
        # 高潮结算函数
        orgasm_settle_in_second_behavior(character_id, change_data, normal_orgasm_dict, extra_orgasm_dict, un_count_orgasm_dict)
        # 触发了饮精绝顶后重置射精位置，以免重复触发
        if drink_semen_orgasm_flag:
            character_data.h_state.shoot_position_body = -1
```

要点：

1. 标记必须声明在 for 循环**之外**——它在循环内（`orgasm == 21` 时）赋值，在循环结束后读取。
2. 重置块与 `orgasm_settle_in_second_behavior(...)` 同为 8 空格缩进，即在 for 循环之外、`else:` 块之内。
3. 改动前全文件仅 3 处引用 `shoot_position_body`（`:107` 判定 / `:110` 原重置 / `:310` 经验 111 判定），已逐一核对；改动后为 `:108` 判定 / `:136` 新重置 / `:315` 经验 111 判定，其中 `:315` 是唯一夹在「置标记」与「重置」之间的读取点，正是要修的目标。
4. 重复触发防护未被削弱：重置仍发生在 `orgasm_judge()` 返回之前，因此下一次 `orgasm_judge()` 调用时射精位置已是 `-1`（详见 §11.6）。

## 5. 构建与缓存

无 CSV / 常量改动，**不需要** `buildconfig.py`。

```bash
# 本机必须用 conda 解释器（裸 python 是 Store 空壳别名）
.conda\python.exe game.py
```

## 6. 验证清单

### 6.1 单元测试（脚本方式，不入库）

**全部通过**，实测结果见 §11.3。

- [x] 构造 NPC + `special_seasoning=11`、`special_seasoning_amount>0`、`quality=8` 的手制食物，调用 `handle_eat_add_just`，断言 `target_data.h_state.shoot_position_body == 2`
- [x] 同上后调用 `second_behavior.check_second_effect(npc_id, change_data)`，断言 `experience[111]` 增加、`status_data[21]` / `[23]` 有增量、产生 `m_orgasm_*` 二段行为
- [x] `semen_ml == 0` 时断言 `shoot_position_body` 仍为 `-1`
- [x] 普通调味食物（`special_seasoning=0`）断言 `shoot_position_body` 不被改动
- [x] 给 NPC 置 `talent[31]=1` 后进食**低品质**精液食物，断言产生一次不计次绝顶（`h_state.orgasm_level[21]` +1）
- [x] 经验 111 累计到 50 后调用 `handle_talent` 相关入口，断言获得 `talent[31]`

§3.5 追加需求的补充断言（同一脚本）：

- [x] 持有 `talent[31]` 的干员进食精液食物并走完二段结算后，`experience[111]` 仍能增加（修复前恒不增加）
- [x] 该次结算完成后 `shoot_position_body` 仍被重置为 `-1`（重复触发防护未被削弱）
- [x] 紧接着再走一次二段结算，`experience[111]` 不再重复增加
- [x] 回归：口内射精路径（直接置 `shoot_position_body = 2`）下，`talent[31]` 持有者同样能累计 `experience[111]`
- [x] 回归：无 `talent[31]` 时，`shoot_position_body` 不被本次改动重置（仍交由 `judge_before_pl_behavior` 处理）

### 6.2 游戏内测试（由用户执行）

- [ ] debug 模式下把料理技能 `ability[43]` 拉满，制作精液调味的绝珍级手制料理并喂给干员，结算面板出现口喉/心理快感增量与绝顶口上，数值变化中出现「饮精绝顶经验」
- [ ] 同一份低品质精液料理喂给普通干员：不绝顶、不加经验 111
- [ ] 同一份低品质精液料理喂给持有[饮精绝顶]素质的干员：条件反射绝顶，且数值变化中出现「饮精绝顶经验」（§3.5 修复点）
- [ ] （§3.5 修复点）对持有[饮精绝顶]素质的干员做一次口内射精，确认角色信息面板的「饮精绝顶经验」数值继续增长而非停在原地
- [ ] （§3.5 回归）时停解放与寸止解放各走一次含口内射精的绝顶，确认经验 111 未被重复结算
- [ ] 进食后紧接着执行其他指令，确认口上未出现“射在口中/胃部”类误匹配
- [ ] 旧存档载入正常；Tk 与 Web 两种绘制模式表现一致

## 7. 风险与注意事项

1. **变量误用**：`handle_eat_add_just` 内 `character_data`（行动者）与 `target_data`（本轮进食者）同时存在，写错会把射精位置登记到玩家身上。
2. **登记残留**：若本次进食未绝顶，`shoot_position_body = 2` 会保留到玩家下次行动前（由 `judge_before_pl_behavior` 重置）。期间若该 NPC 因其他原因绝顶，会额外获得一次经验 111。考虑到“刚吃下精液”这一语境，此行为可接受，且与 `condom_handle.settle_drink` 的既有语义一致。
3. **不要改 `update_shoot_position_flag`**：见 4.3。
4. **不影响玩家**：玩家（id=0）在 `orgasm_judge` 中走射精槽分支，本改动对其无效果。

## 8. 改动文件清单

| 文件 | 类型 | 改动 |
| --- | --- | --- |
| `Script/Settle/default.py` | 修改 | `handle_eat_add_just()` 精液食物分支追加 `shoot_position_body = 2` 登记（4 行） |
| `Script/Settle/orgasm_settle.py` | 修改 | `orgasm_judge()` 把饮精绝顶后的射精位置重置延后到高潮结算之后（§3.5，净 +5 行） |

## 9. 回滚

两处改动互相独立，可分别回滚，均无构建产物、无存档字段变更、无需数据迁移：

- `default.py`：删除新增的 4 行。
- `orgasm_settle.py`：删除 `drink_semen_orgasm_flag` 的声明与结算后的重置块，把重置写回 `un_count_data += 1` 之后即可。

## 10. 不在本 Plan 范围

- 不调整 `food_quality >= 7` 的快感触发门槛，也不为精液食物追加无视品质的口喉快感
- 不让玩家（id=0）自身进食获得快感/心情反馈（`default.py:7700` 的 `if chara_id:` 保持原样）
- 不结算 `Food.milk_ml` / `Food.urine_ml`（当前为已定义未使用字段）
- 不改动时停解放（`default.py:6809`）与寸止解放（`orgasm_settle.py:352`）两条路径的经验 111 结算行为（这两条路径下射精位置本就已是 `-1`，§3.5 的修复对其无影响，见 §11.6）
- 不新增进食绝顶专属口上（沿用现有部位绝顶口上）

---

## 11. 实施记录（2026-08-22）

### 11.1 实际改动

按 §4 原样落地，**无任何设计偏离**。唯一改动点为 `Script/Settle/default.py` 的 `handle_eat_add_just()` 精液食物分支，实施后位于 `:7749-7752`：

```python
        # 精液食物则将精液加到口腔污浊，并加精液经验
        if food_seasoning in {11,12}:
            ...
            ejaculation_panel.update_semen_dirty(chara_id, 2, 0, semen_ml, update_shoot_position_flag=False)
            cache.shoot_position = temp_position
            # 登记精液进入口腔，使本次进食若因高品质快感而绝顶时，
            # 由二段绝顶结算联动饮精绝顶（素质31）与饮精绝顶经验（111）
            if semen_ml > 0:
                target_data.h_state.shoot_position_body = 2
```

- 未新增 import、常量、前提、结算效果 id；未改动 CSV。
- 按 §4.3 保持 `update_shoot_position_flag=False` 不变。
- 按 §4.1 使用 `target_data`（本轮进食者）而非 `character_data`（行动发起者）。
- 未按 §5 执行 `buildconfig.py`（确认无 CSV / 常量改动，不需要）。

### 11.2 实施前的假设复核

落地前逐条实测复核了 §2 的调查结论，全部成立：

| 假设 | 复核结果 |
| --- | --- |
| `orgasm_settle.py:105-110` 素质 31 饮精绝顶判定 `shoot_position_body in [2, 15]` | 成立，位置未变 |
| `orgasm_settle.py:308-311` `part_count >= 1` 时结算经验 111 | 成立，位置未变 |
| `condom_handle.settle_drink()` 直接赋值 `shoot_position_body` 的同构写法 | 成立（`:260-261`，取 15） |
| 精液食物分支现状与 §2.4 一致 | 成立 |

### 11.3 单元测试结果

测试脚本按约定不入库（写在 scratchpad 目录）。脚本以 `game_config.init()` + `character_config` + `map_config` + `attr_calculation.get_system_setting_zero()` + `basement.get_base_zero()` 构建无头运行环境，手工创建玩家（id=0，`data/Character.json` 中无 id 0 模板）与全部 NPC，并屏蔽 `draw.*.draw()` 以免阻塞等待玩家输入。

**11 项断言全部通过（PASS 11 / FAIL 0）**：

| # | 用例 | 断言 | 实测值 |
| --- | --- | --- | --- |
| 1 | 精液食物(11)、`amount=50`、`quality=8` | `shoot_position_body == 2` | `2` |
| 1 | 同上 | `status_data[21]`（口喉）> 0 | `348` |
| 1 | 同上 | `status_data[23]`（心理）> 0 | `232` |
| 2 | 接着走 `check_second_effect` | `experience[111]` 增加 | `0 -> 1` |
| 2 | 同上 | 产生 `m_orgasm_*` 二段行为 | `m_orgasm_small` / `h_orgasm_small` / `plural_orgasm_2` |
| 3 | `semen_ml == 0` | `shoot_position_body` 保持 `-1` | `-1` |
| 4 | 普通调味食物(0) | `shoot_position_body` 未被改动 | `-1` |
| 5 | `talent[31]=1` + 低品质精液食物 | 低品质下 `status_data[21]` 未增加 | `0` |
| 5 | 同上 | `shoot_position_body == 2` | `2` |
| 5 | 同上，走二段结算 | 触发不计次绝顶（射精位置被当场重置） | `-1` |
| 6 | `experience[111] = 50` | `npc_gain_semen_drinking_climax_talent` 后获得 `talent[31]` | `1` |

用例 2 实测产生了 `plural_orgasm_2`（口喉 + 心理双部位绝顶），说明高品质精液食物一次进食即可跨过两个部位的绝顶阈值，§3.1 预期的完整链路（进食 → 部位绝顶 → 经验 111）已贯通。

用例 5 验证了 §3.1 的附带效果：素质 31 持有者进食**低品质**精液食物（无任何快感增量）时，仍由 `orgasm_settle.py:105-110` 条件反射性地触发一次不计次绝顶，与素质配表文案「尝到精液的味道就会条件反射性地绝顶」一致。

### 11.4 尚未覆盖的验证

§6.2 的游戏内测试（含 Tk / Web 两种绘制模式表现、旧存档载入、口上无误匹配）需在真实游戏进程中由用户人工执行，本次未覆盖。

### 11.5 §3.5 追加需求的实施（2026-08-22，同日追加）

按 §4.2 落地，改动位于 `Script/Settle/orgasm_settle.py` 的 `orgasm_judge()`，实施后：

- `:84` 新增 `drink_semen_orgasm_flag = False` 声明
- `:106-112` 饮精绝顶判定改为只置标记
- `:134-136` 高潮结算（`:133`）返回后再重置射精位置

净增 5 行（1 行声明 + 2 行重置块 + 2 行注释净增）。未改动函数签名，未新增 import / 常量 / CSV，因此同样**不需要** `buildconfig.py`。

修复前后对照：

| 场景 | 修复前 | 修复后 |
| --- | --- | --- |
| 无素质 31，口内射精后绝顶 | 加经验 111 | 加经验 111（不变） |
| **持有素质 31，口内射精后绝顶** | **不加经验 111** | **加经验 111** |
| **持有素质 31，进食精液食物后绝顶** | **不加经验 111** | **加经验 111** |
| 同一次射精被连续结算两次 | 不重复加 | 不重复加（不变） |
| 时停解放 / 寸止解放路径 | 不加经验 111 | 不加经验 111（不变，见 §11.6） |

### 11.6 §3.5 的回归分析

**（1）重复触发防护未被削弱。** 重置仍在 `orgasm_judge()` 返回之前执行，而 `:108` 的判定发生在下一次 `orgasm_judge()` 调用中，届时读到的已是 `-1`。单元测试用例 7 的第三条断言实测确认：紧接着再走一次 `check_second_effect`，经验 111 不再增加。

**（2）另外两个调用方未受影响。** `orgasm_settle_in_second_behavior()` 共 3 个调用方：

| 调用方 | 场景 | 是否受影响 |
| --- | --- | --- |
| `orgasm_settle.py:133` | `orgasm_judge()` 正常绝顶结算 | 是——本次修复的目标 |
| `default.py:6809` | 时停解放 | 否 |
| `orgasm_settle.py:352` | 寸止解放 | 否 |

后两条路径不经过 `orgasm_judge()` 的 NPC 分支，`drink_semen_orgasm_flag` 对其不可见。且这两条路径下射精位置在绝顶被“存入”时（时停 `continue` 进 `time_stop_orgasm_count` / 寸止 `continue` 进 `orgasm_edge_count`）就已被本次修复的重置块置为 `-1`，解放时读到的仍是 `-1`，与修复前完全一致——即不会因解放而把同一次口内射精重复结算成第二份经验 111。

**（3）字段读取面已穷举。** `orgasm_settle.py` 全文件仅 3 处引用 `shoot_position_body`：`:108`（饮精绝顶判定）、`:136`（新的重置点）、`:315`（经验 111 判定）。逐一核对后，`:315` 是唯一夹在“置标记”与“重置”之间的读取点，正是本次要修的目标，无其他代码落在这个窗口内。

**（4）存档兼容。** 未新增/变更任何持久化字段，`drink_semen_orgasm_flag` 是纯局部变量。旧存档载入后行为直接切换到修复后的表现，无需迁移。

### 11.7 §3.5 的单元测试结果

在 §11.3 的同一脚本中追加 3 个用例、6 条断言，连同原有断言**共 17 项全部通过（PASS 17 / FAIL 0）**：

| # | 用例 | 断言 | 实测值 |
| --- | --- | --- | --- |
| 7 | `talent[31]` + 精液食物 + 走二段结算 | `experience[111]` 增加 | `0 -> 1` |
| 7 | 同上 | 结算后 `shoot_position_body` 仍重置为 `-1` | `-1` |
| 7 | 紧接着再走一次二段结算 | 不重复加经验 111 | `1 -> 1` |
| 8 | 回归：口内射精路径（直接置 `shoot_position_body = 2`）+ `talent[31]` | `experience[111]` 增加 | `1` |
| 8 | 同上 | 结算后重置为 `-1` | `-1` |
| 9 | 回归：无 `talent[31]`，`shoot_position_body = 2` | 射精位置未被本改动重置，仍为 `2` | `2` |

用例 9 确认修复没有把重置行为扩散到无素质 31 的角色身上——他们的射精位置仍由 `judge_before_pl_behavior()` 在玩家下次行动前统一重置，与 §2.6 描述的生命周期一致。

### 11.8 §3.5 尚未覆盖的验证

§6.2 中新增的 3 条游戏内测试（素质持有者的经验增长可见性、时停解放与寸止解放的无重复结算）需由用户在真实游戏进程中人工执行，本次未覆盖。
