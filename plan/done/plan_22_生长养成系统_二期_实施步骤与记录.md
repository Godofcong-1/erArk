# Plan 22（二期·实施步骤与记录）：日程模板 + 幼女跟随母亲 + 成年结算

> 本文件是 `plan_22_生长养成系统_二期_方案.md`（下文简称"方案"）的**实施步骤清单与过程记录**。
> 需求背景、现状调查、设计决策、界面设计、风险与范围外事项以方案与
> `plan_22_生长养成系统_总纲.md`（下文简称"总纲"）为准；
> **数据结构定义以 `plan_22_生长养成系统_一期_方案.md` §4 为准**（下文简称"一期方案"）。
> 本文件只写"怎么做、怎么验、怎么回滚"，实施过程与结果记入 §6。

- 状态：**已实施**（日程模板 + 幼女见学 + 成年结算三块全部落地），2026-09-07
- 适用代码快照：`plan22-growth-system @ a8088d5d3`
- **前置：一期必须先完成**——本期用到的四个字段由一期建立并做存档回填，且日程只在"没有课的时段"生效
- 实施前提：先通读总纲 §2、一期方案 §4 与本方案；实施中发现与方案冲突的事实，**先更新方案再动代码**

---

## 1. 改动文件清单

| 文件 | 类型 | 改动 |
| --- | --- | --- |
| `data/csv/Entertainment.csv` | 改 | 新增「跟随母亲」「自由玩耍」两行，`class_ok` 均配 0 |
| `data/csv/Behavior_Data.csv` | 改 | 新增 `follow_mother`（60 分钟，NPC 触发） |
| `data/csv/Behavior_Effect.csv` | 改 | `follow_mother` 的效果串（见学经验 + `care_point` + 母女好感亲密） |
| `data/csv/Behavior_Introduce.csv` | 改 | `follow_mother` 的介绍文本 |
| `Script/Core/constant/Behavior.py` | 改 | `FOLLOW_MOTHER` en_name 常量 |
| `Script/Core/constant/BehaviorStr.py` | 改 | 同上 |
| `Script/Core/constant/Behavior_Int.py` | 改 | `follow_mother` 的 cid |
| `Script/Core/constant/CharacterStatus.py` | 改 | 跟随母亲状态 cid |
| `Script/Core/constant_effect.py` | 改 | 见学结算的效果 id |
| `Script/Settle/past_day_settle.py` | 改 | 娱乐刷新**之后**改写孩子的 `entertainment_type`（时序，方案 §2.1） |
| `Script/Settle/default.py` | 改 | 见学结算实现（按母亲工作的 `ability_id` 加经验） |
| `Script/Design/handle_npc_ai.py` | 改 | 幼女未排课节次走跟随母亲；母亲无效时的回落链 |
| `Script/System/Pregnancy_System/pregnancy_handle.py:637` | 改 | `check_grow_to_girl` 内加性格选边与职业倾向提示；`chest_grow` / `body_part_grow` 接入 `care_point` |
| `Script/System/Education_System/schedule_template_handle.py` | 新增 | 日程模板读写、批量套用、单孩覆盖 |
| `Script/System/Education_System/schedule_template_panel.py` | 新增 | 日程模板面板（方案 §5.1） |
| `Script/System/Education_System/course_select_panel.py` | 改 | 个人课表面板加一行"日程模板：X [改]"（方案 §5.2） |
| `data/talk/daily/follow_mother.csv` | 新增 | 10 条（母亲有工作 / 无工作 2 档 × 5） |
| `tools/ArkEditor/csv/Behavior_Data.csv` | 改 | 新行为同步 |

**不改 `game_type.py` 与 `save_handle.py`**：本期用到的四个字段已在一期建好并回填（一期方案 §4）。若实施时发现字段缺失，说明一期没按方案做全，**先补一期再继续**，不要在本期另建字段。

---

## 2. 详细改动步骤

> 全部 cid / 效果 id 不在此预分配，实施时现查空闲号。

### 2.1 CSV 与常量

1. `Entertainment.csv` 加「跟随母亲」「自由玩耍」两行；`class_ok` 配 0，它们是日程活动不是兴趣课
2. `Behavior_Data.csv` / `Behavior_Effect.csv` / `Behavior_Introduce.csv` 加 `follow_mother`
3. 常量五处同步；`tools/ArkEditor/csv/Behavior_Data.csv` 同步
4. 跑 `buildconfig.py`

### 2.2 日程模板

1. 新建 `Script/System/Education_System/schedule_template_handle.py`：模板增删改查、批量套用、单孩覆盖的合并读取（`schedule_override` 优先于模板）
2. 初始化四套预设模板（方案 §3.6 的表），在新周目或首次进入面板时写入 `Rhodes_Island.child_schedule_template`
3. 新建 `schedule_template_panel.py`（方案 §5.1）；「批量套用」走既有的通用 NPC 选择面板
4. `course_select_panel.py` 加"日程模板：X [改]"一行（方案 §5.2）

### 2.3 日程执行链（时序硬约束）

改 `Script/Settle/past_day_settle.py`：

1. 找到既有的娱乐刷新调用点（`handle_npc_ai.py:788~841` 的刷新在此之后被消费）
2. **在刷新之后**插入孩子的 `entertainment_type` 改写，照 `egg_handle.replace_entertainment_for_eggs` 的挂点（方案 §2.2）
3. 改写规则：只覆盖该时段内**完全没有课**的情况；有课的时段跳过（方案 §3.6）。**（2026-09-10 已改：不再避让有课的时段，课表在节次级别优先，方案 §9.2.9）**

顺序颠倒是本期最容易犯的错，且症状是"日程时灵时不灵"，很难查。实施后用 §4.1 的第一条断言直接验。

### 2.4 幼女跟随母亲

1. `handle_npc_ai.py`：幼女（素质 102）+ 当前节次未排课 → 置 `follow_mother_flag`，走 `follow_mother` 行为
2. **回落链**：按方案 §3.24 的表逐条实现五种母亲无效情形
   - 母亲在 H / 监禁 / 无意识时**必须**回落育儿室，既有跟随链不判这个
3. `Script/Settle/default.py` 加见学结算：读母亲 `work.work_type` → `WorkType.csv` 的 `ability_id` → 基础值 6 × 速度系数（母亲该能力等级，走一期方案 §3.1 的曲线）
4. 母亲 `work_type == 0` 时不加见学经验，只加 `care_point` 与好感

### 2.5 成年结算

改 `Script/System/Pregnancy_System/pregnancy_handle.py:637 check_grow_to_girl`，在既有的 `chest_grow` / `body_part_grow` 调用附近插入：

1. 四对性格素质按 `personality_point` 符号选边写 `talent[271~278]`
2. `personality_point` 全为 0 时输出"性格尚未定型"，**不随机选边**
3. `chest_grow` / `body_part_grow` 接入 `care_point` 作为第二输入
4. 按能力最高的科目反查 `WorkType.csv` 的 `ability_id` 输出职业倾向提示（只提示，不自动任命）
5. 文本输出照既有 `check_grow_to_girl` 的 `WaitDraw` 模式

### 2.6 口上

`data/talk/daily/follow_mother.csv`，10 条（母亲有工作 / 无工作 2 档 × 5）。带 `self_is_player_daughter` 前提以命中 `talk.py:185~188` 的女儿 5 倍加权（一期方案 §3.23）。

---

## 3. 构建与缓存

```bash
.conda\python.exe buildconfig.py   # CSV / 常量改动后
.conda\python.exe buildpo.py
.conda\python.exe buildmo.py
```

本期**不涉及地图改动**，不需要删场景缓存。

---

## 4. 验证清单

### 4.1 单元测试（实施方执行，按 `headless-game-test` 模式 A）

- [ ] **日程改写时序**：构造一个孩子跑完一次跨天结算，断言 `entertainment_type` 是模板值而非随机值（这条直接验 §2.3 的时序）
- [ ] 有课的时段日程不生效：某时段排满课时，`entertainment_type` 该位保持不变
- [ ] `schedule_override` 优先于模板：同一时段模板与覆盖不同时，取覆盖值
- [ ] 批量套用：对 3 个孩子套用同一模板后，三者的 `schedule_template_id` 一致
- [ ] 见学经验：母亲为厨师（`ability_id` 43）时，幼女跟随后 43 号能力经验增加，增量 = 6 × 速度系数
- [ ] 母亲 `work_type == 0` 时不加见学经验，但 `care_point` 增加
- [ ] **回落链五条全覆盖**：`mother_id == -1` / 母亲 `dead` / 母亲在 H / 母亲在监禁 / 母亲在外勤，五种输入均回落育儿室且不抛异常
- [ ] 成年结算：`personality_point` 各项为正 / 为负 / 为 0 三种输入，断言写入的 `talent[271~278]` 组合与"性格尚未定型"分支
- [ ] 成年结算幂等：连续调用两次 `check_grow_to_girl`，第二次因 `talent[103] == 0` 不再执行

### 4.2 游戏内整体测试（由用户执行）

- [ ] 日程模板面板能新建、编辑、批量套用到多个孩子
- [ ] 单孩微调只影响该孩子，不影响模板与其他孩子
- [ ] 幼女在没课的时段会跟着母亲去她的工作岗位，并获得对应科目的经验
- [ ] 母亲在 H / 被监禁 / 外勤时，幼女不会跟过去，而是在育儿室玩耍
- [ ] 萝莉成年时出性格选边与职业倾向提示文本
- [ ] Web 模式（`web_draw = 1`）下日程模板面板表现一致
- [ ] 旧存档载入不报错

---

## 5. 回滚

| 单元 | 回滚方式 | 备注 |
| --- | --- | --- |
| 日程模板（面板 + handle） | 删除两个新文件 + 摘掉入口 | 字段留在存档里不影响载入 |
| 日程执行链 | revert `past_day_settle.py` 的改动 | 回到既有随机娱乐 |
| 幼女跟随母亲 | revert `handle_npc_ai.py` 与结算；删 `follow_mother` 行为 | 幼女回落为与萝莉同样的自由行动（即一期的状态） |
| 成年结算 | revert `pregnancy_handle.py` 的改动 | 回到只做发育判定 |
| 口上 | 删 `follow_mother.csv` 重跑 `buildconfig.py` | |

本期**没有不可回滚的部分**——所有改动都可独立 revert，且不涉及地图与存档结构。

---

## 6. 实施过程记录

### 6.1 实际改动

| 文件 | 类型 | 实际改动 |
| --- | --- | --- |
| `data/csv/Behavior_Data.csv` | 改 | 新增 231 `follow_mother`（60分钟/npc/娱乐）、232 `free_play`（60分钟/npc/娱乐） |
| `data/csv/Behavior_Effect.csv` | 改 | `follow_mother` → `1511 - 1512 - 553`；`free_play` → `1511 - 1512 - 554` |
| `data/csv/Behavior_Introduce.csv` | 改 | 两个新行为的介绍文本 |
| `data/csv/Entertainment.csv` | 改 | 新增 176 跟随母亲、177 自由玩耍、**178 自习**（见偏离 1）；`class_ok` 均为 0 |
| `tools/ArkEditor/csv/Behavior_Data.csv` | 改 | 两个新行为同步 |
| `Script/Core/constant/Behavior.py` / `BehaviorStr.py` / `Behavior_Int.py` | 改 | `FOLLOW_MOTHER` / `FREE_PLAY`（cid 231 / 232） |
| `Script/Core/constant/CharacterStatus.py` | 改 | `STATUS_FOLLOW_MOTHER = 231`、`STATUS_FREE_PLAY = 232` |
| `Script/Core/constant/StateMachine.py` | 改 | `EDUCATION_MOVE_TO_MOTHER = 717`、`EDUCATION_FOLLOW_MOTHER = 718`、`ENTERTAIN_FREE_PLAY = 719` |
| `Script/Core/constant_effect.py` | 改 | `FOLLOW_MOTHER_ADD_ADJUST = 553`、`FREE_PLAY_ADD_ADJUST = 554` |
| `Script/System/Education_System/schedule_template_handle.py` | **新增** | 模板增删改查、四套预设、批量套用、单孩覆盖合并读取、每日改写、面板辅助查询（约 330 行） |
| `Script/System/Education_System/schedule_template_panel.py` | **新增** | 日程模板面板：模板表、编辑模板、多选批量套用（约 280 行） |
| `Script/System/Education_System/class_ai.py` | 改 | 追加见学分支：`judge_mother_available` / `judge_should_follow_mother` / `judge_follow_mother_state_machine` |
| `Script/System/Education_System/growth_handle.py` | 改 | 追加见学结算 `settle_follow_mother_gain`、成年结算 `settle_personality_talent` / `get_career_suggestion_text` / `get_care_point_grow_bonus` |
| `Script/System/Education_System/course_select_panel.py` | 改 | 加「日程：X [改]」一行与 `_edit_schedule` 单孩微调子面板 |
| `Script/System/Education_System/class_schedule_panel.py` | 改 | 教育管理主面板加第四个页签「日程模板」 |
| `Script/Settle/past_day_settle.py` | 改 | 娱乐刷新 → 卵替换 → **孩子日程改写**（时序硬约束，见 §6.3 的断言） |
| `Script/Settle/default.py` | 改 | 新增 553 见学结算、554 自由玩耍结算 |
| `Script/StateMachine/default.py` | 改 | 新增三个状态机 717 / 718 / 719 |
| `Script/Design/handle_npc_ai.py` | 改 | ① 上课判定之后插入见学分支；② 176/177/178 排除出每日随机娱乐池 |
| `Script/System/Pregnancy_System/pregnancy_handle.py` | 改 | `check_grow_to_girl` 插入性格选边与职业倾向；`chest_grow` 接入 `care_point` |
| `data/talk/daily/follow_mother.csv` | **新增** | 10 条（母亲有工作 6 / 无工作 4），全部带 `self_is_player_daughter` |

**与方案的偏离**：

1. **多加了一行娱乐「自习」（178）。** 方案 §3.6 的「学业优先」模板上午/下午都是自习，但 `Entertainment.csv` 里
   根本没有「自习」这一项——自习一直只是个行为（`self_study` 211），没有对应的娱乐配置，日程模板排不上去。
   于是补了 178 自习：地点 `Class_Room`、移动状态机复用 561 `MOVE_TO_CLASS_ROOM`、娱乐状态机复用一期的
   713 `EDUCATION_SELF_STUDY`。**零新代码**：561 在查不到课表时本就回落"随机去一间理论教室"，
   713 本就只是"赋予 self_study 行为"，548 结算查不到课表时回落学识——三段现成的回落链正好拼成"课外自习"。
2. **方案表里的「兴趣活动」落为「下棋」（58）。** `Entertainment.csv` 里没有名为"兴趣活动"的项，它是个类别不是具体活动。
   预设模板按名字反查 cid（`PRESET_TEMPLATE_SLOT_NAME`），取「下棋」作为兴趣类的代表。预设表写的是**名字不是cid**，
   因为娱乐编号会随内容增删漂移，按名字反查一次比在代码里钉死一串数字安全。
3. **多加了一个行为 `free_play`（232）而不是只加娱乐行。** 方案 §1 只列了 `follow_mother` 一个新行为，
   但「自由玩耍」作为娱乐必须有 `behavior_id`，且它同时是见学回落链的**唯一出口**——
   回落时若返回 0 交回既有 AI 链，等于让幼女在没课的时段随机游荡，方案 §3.24 要的是确定的去处（育儿室）。
4. **回落链实到 6 条而不是方案 §3.24 的 5 条。** 方案漏了"母亲住院"：`rhodes_island.medical_hospitalized`
   是独立于 `sp_flag` 的一张表，住院的母亲既不算外勤也不算外交访问。另外把"母亲所在场景不在 `scene_data` 里"
   也补成一条（未解锁/已拆除的场景），否则移动状态机会拿到一个走不到的目标。
5. **`body_part_grow` 没有接入 `care_point`。** 方案 §3.8 要求 `chest_grow` **与** `body_part_grow` 都接。
   实际读代码发现 `body_part_grow`（`pregnancy_handle.py:776`）**根本没有概率判定**——它是"直接继承母亲的臀/腿/足素质，
   母亲为0时母女一起随机取一个"，没有任何可以被照料值推动的量。硬塞一个偏移进去等于改写它的语义。
   于是只在 `chest_grow` 接：把照料值折算为"不长"那一档窗口的收窄量（每 5 点换 1 个百分点，上限 20）。
6. **`personality_point` 的正负两侧以一期 `growth_panel.PERSONALITY_PAIR_NAME` 为准，不是方案 §3.8 的文字顺序。**
   方案写"273 脆弱 / 274 坚强"、"277 羞耻 / 278 开放"，而一期面板已经把 pair1 显示为（坚强, 脆弱）、
   pair3 显示为（开放, 羞耻）。**面板是既成事实**，若按方案文字写，会出现"面板显示偏坚强、结算却写了脆弱"。
   已在 `growth_handle.PERSONALITY_PAIR_TALENT` 的注释里钉住这一点。
7. **见学的母女好感直接调 `character_handle.add_favorability`，不走 `common_default` 的好感链。**
   那条链的信物加成、连续指令减值、系统难度修正全部是围绕**玩家**设计的，套在一对母女身上只会得到看不懂的数字。
8. **`follow_mother` 的触发多了一个入口。** 方案 §3.24 只写"节次内且本节没课"，实际还需要第二个入口：
   日程模板把某个**娱乐时段**排成了「跟随母亲」（176）时也要走见学——否则新加的 176 那一行娱乐没有任何执行路径。
9. **`get_chara_entertainment` 里 176/177/178 被排除出随机池。** 照 175 照料卵的既有做法。
   不排除的话，成年干员会被随机分配到"跟随母亲""自由玩耍""自习"，语义上讲不通。

**已知限制**：

- **PO / MO 未重建**：本机没有 `xgettext`，`.conda` 里也没有 `polib`，`buildpo.py` / `buildmo.py` 均无法运行。
  更要紧的是 **`buildconfig.py` 会因此把 `data/po/**/*.po` 写空**（实测 `erArk_py.po` 掉 13627 行、
  `erArk_csv.po` 掉 22 万行），且不报错。本轮已 `git checkout -- data/po/` 还原，
  **后续每次跑完 `buildconfig.py` 都要检查 `git diff --stat` 里有没有 `data/po/`**。本地化产物留给 CI。
- **幼女的 `entertainment_type` 仍被 `get_chara_entertainment` 强制刷成 151 过家家**（`handle_npc_ai.py:797~801`
  的既有分支，早于本期存在）。日程改写发生在它之后，所以套了模板的幼女会被正确覆盖；
  **没套模板的幼女维持一期行为不变**。这是刻意保留的，不属于本期范围。
- **日程只覆盖"该时段完全没有课"的槽位**，粒度是时段不是节次：上午 9~12 只要有任意一节排了课，整个上午的日程就不生效。**（2026-09-10 已改：这正是方案 §9.2.9 修掉的问题，现在有课的节次上课、没课的节次做日程活动）**
  这是方案 §3.6 定的口径，不是实现妥协。

### 6.2 实施前的假设复核

| # | 假设 | 复核结果 |
| --- | --- | --- |
| 1 | 一期已建好 `schedule_template_id` / `schedule_override` / `follow_mother_flag` / `child_schedule_template` 四个字段并做了存档回填 | ✅ 前三个在 `game_type.py:403/405/407`，第四个在 `:1267`；回填在 `save_handle.py:344~346`（`child_growth` 惰性创建）与 `:556~557`（`child_schedule_template`）。本期确实一个字段都没新建 |
| 2 | `handle_npc_ai.py:788~841` 每日随机刷新 `entertainment_type` | ✅ `get_chara_entertainment` 在 `:781`，随机赋值在 `:848`。顺带发现 `:797~801` 有一条**幼女强制 151 过家家并 return** 的既有分支，见"已知限制" |
| 3 | `egg_handle.replace_entertainment_for_eggs` 的挂点在娱乐刷新之后 | ✅ `past_day_settle.py:73` 刷新、`:75` 卵替换，本期的日程改写接在 `:76`。已用断言钉住（§6.3） |
| 4 | `character_move.py:172~173` 会清 `sp_flag.is_follow` | ✅ 确认；本期用 `follow_mother_flag`，测试里断言了 `sp_flag.is_follow` 始终为 0 |
| 5 | `check_grow_to_girl` 的守卫是 `handle_self_is_loli`，天然幂等 | ✅ `pregnancy_handle.py:643`；结算后 `talent[103] = 0`。已用"连调两次只输出一次"的断言验证 |
| 6 | `WorkType.csv` 的 `ability_id` 列可直接作为见学科目 | ✅ 第 7 列；料理岗位 → 能力 43 → 经验 83，链路通 |

### 6.3 单元测试结果

两个脚本，**114 条断言全部通过**（模式 A，自建 fixture）。

**新功能测试（85 条）**

| 组 | 断言要点 | 结果 |
| --- | --- | --- |
| 注册 | 两个行为 / 两个效果链 / 两个结算器 / 三个状态机 / 三行娱乐 / 10 条口上 | ✅ 13/13 |
| 日程模板 | 四套预设初始化、模板名与三格取值、套用写入、override 优先于模板、取消 override 回落、批量套用 3 人一致、套用中人数统计 | ✅ 13/13 |
| **改写时序** | 随机值被模板值覆盖；**上午排课后该格保持随机值、同日晚上仍生效**；未套模板的孩子不被改写；`past_day_settle.py` 里改写挂点的字符偏移 > 娱乐刷新挂点 | ✅ 6/6 |
| 见学结算 | 母亲工作科目反查、习得与经验增加、`care_point` +0.5、母女好感增加、速度曲线三点、**母亲无工作时只加 care 与好感**、`add_time=0` 不结算 | ✅ 14/14 |
| **回落链** | 无母亲 / 母亲死亡 / **母亲在H** / **母亲无意识H** / 母亲被监禁 / 母亲外勤 / 母亲住院 —— 七种输入全部回落 `ENTERTAIN_FREE_PLAY`；不同场景先移动；有课时不接管；**萝莉不走见学**；晚上日程排跟随母亲则走见学、排自由玩耍则不接管 | ✅ 13/13 |
| 结算器直调 | 553 生效、母亲无效时 553 不结算；554 抑郁与反感各回落 60、清见学flag、**不置翘课flag** | ✅ 6/6 |
| 成年结算 | 四对性格按符号选边（正→勤劳/热情，负→脆弱/羞耻）且对侧被清零；**全0时不写任何素质并出"性格尚未定型"**；职业倾向含最高科目名且不自动任命；无科目时提示为空；`care_point` 偏移 0/10/20 三点；**同随机值下无照料不长、高照料长一档**；成年跑通且**连调两次只输出一次** | ✅ 20/20 |
| 随机池 | 176/177/178 已排除 | ✅ 1/1 |

**一期回归 + 收敛测试（28 条）**

| 组 | 断言要点 | 结果 |
| --- | --- | --- |
| 一期未被破坏 | 兴趣课候选仍为 16 项且不含新增三项、品酒仍被排除；理论 6 / 实践 3 / 大礼堂 1；速度曲线七点未变；学识45→82、料理43→83；一期五个行为仍注册 | ✅ 14/14 |
| 娱乐随机刷新 | 成年干员仍能刷出多样娱乐；随机池不含 176/177/178，也不含 175 照料卵 | ✅ 3/3 |
| 行为循环收敛 | 见学状态机赋予 `follow_mother` 且 **duration = 60（正整数，不会死循环）**；置了 `follow_mother_flag` 而 `sp_flag.is_follow` 保持 0；母亲进H后改走自由玩耍状态机且不赋予见学行为；人在育儿室时赋予 `free_play`；不同场景时决策为移动且移动后 duration ≥ 1 | ✅ 11/11 |

**关键实测值**：母亲料理 4 级、孩子 0 级 → 速度系数 2.00；一次 60 分钟见学 `care_point` +0.5；
`care_point` 100 → 胸部发育概率表"不长"档从 60 收窄到 40（同一随机值 55 下，无照料不长、高照料长一档）。

**踩到的两个坑**（记下来给后续几期）：

1. **`constant.state_machine_data` 不存在，真名是 `constant.handle_state_machine_data`。** 断言状态机是否注册时会撞上。
2. **`find_character_target` 在单元测试里跑不动**：它会走完整条目标链，途中 `handle_assistant_live_together_on`
   取 `assistant_services[7]` 直接 KeyError。本期只关心自己那一段决策，所以改为**直调
   `class_ai.judge_follow_mother_state_machine` + `constant.handle_state_machine_data[id](cid)`**——
   与被测目标无关的 fixture 不值得喂全（与一期 §6.3 记的"无关基建依赖直接钉死"是同一条经验）。

### 6.4 尚未覆盖的验证

（留给用户的游戏内清单，对应 §4.2）

- [ ] 日程模板面板能新建、编辑、批量套用到多个孩子（Tk 与 Web 两种模式）
- [ ] 个人课表面板的「日程：X [改]」一行显示正确，单孩微调只影响该孩子
- [ ] 幼女在没课的时段真的会跟着母亲走到她的工作岗位，并拿到对应科目的经验
- [ ] 母亲在 H / 被监禁 / 外勤 / 住院时，幼女出现在育儿室而不是跟过去
- [ ] 萝莉成年时能看到性格定型与职业倾向两段文本
- [ ] 套了「学业优先」的孩子晚上真的会去图书馆读书、白天没课时去理论教室自习
- [ ] 旧存档载入不报错，一期的课表与上课链未被破坏
- [ ] **PO / MO 重建**（本机无 gettext，须在装了 gettext 的机器或 CI 上做）

### 6.5 第二轮追加调整实施记录

（与方案 §9.x 成对，每轮一节，附回归测试计数）

**2026-09-08 第一轮（与方案 §9.1 成对）：见学与日程的缺口修补**

一期第六轮盘完之后回头盘二期。这轮**换了三个扫描方向**——字段查**读取**点
（上一轮查的是写入点）、行为查**口上覆盖率**、口上前提查**判定对象**——
扫出的七项全是上一轮那套方法结构上看不见的。

#### 实际改动

| 文件 | 类型 | 实际改动 |
| --- | --- | --- |
| `data/talk/daily/free_play.csv` | **新增** | 12 条（幼女4 / 萝莉4 / 少女2 / 中立兜底2）。此前 `free_play` 是全游戏 40 个娱乐类行为里唯一零口上的 |
| `data/talk/daily/chat/chat_follow_mother.csv` | **新增** | 8 条：见学中的女儿主动找博士说话的专属地文，给 `self_follow_mother` 前提一个真实使用者 |
| `data/talk/daily/follow_mother.csv` | 改 | 6 条 `have_work` → `t_have_work`；4 条补上 `t_not_have_work` 做排他 |
| `Script/Core/constant_promise.py` | 改 | 新增 `TARGET_HAVE_WORK` / `TARGET_NOT_HAVE_WORK` / `SELF_FOLLOW_MOTHER` |
| `Script/Design/handle_premise/handle_premise_work.py` | 改 | 实现 `t_have_work` / `t_not_have_work` |
| `Script/Design/handle_premise/handle_premise_other.py` | 改 | 实现 `self_follow_mother` |
| `Script/Design/attr_calculation.py` | 改 | `judge_require` 的素质分支改为读竖线**前面**的素质id（见偏离 14） |
| `Script/System/Education_System/class_ai.py` | 改 | 新增 `judge_in_follow_mother()` 读口与 `clear_follow_mother_flag()` 清位；上课接管与见学判定不成立两处接上清位 |
| `Script/UI/Panel/character_info_head.py` | 改 | 角色状态栏新增 `<学>` 标识 |
| `Script/Settle/past_day_settle.py` | 改 | 见学标记每日兜底清零，与既有的翘课标记并排 |
| `Script/System/Education_System/schedule_template_handle.py` | 改 | 新增 `judge_activity_need_pass` / `judge_template_is_preset` / `create_template` / `rename_template` / `delete_template`；删 `get_child_candidate_list`；每日改写接上 need 校验 |
| `Script/System/Education_System/schedule_template_panel.py` | 改 | 主页加「新建模板」；编辑页加「重命名」「删除本模板」；选模板页加「不套用日程（恢复随机）」；批量套用名单改走一期的 `get_student_candidate_list` |
| `update.log` | 改 | v0.67 段追加 新增 3 条、调整 1 条、修正 4 条 |
| `plan_22_生长养成系统_二期_方案.md` | 改 | 口径行摘掉误认领的 25 与 32；新增 §9.1 |
| `plan_22_生长养成系统_总纲.md` | 改 | 口径 25 / 32 / 52 就地标注 |

#### 与方案的偏离（接 §6.1 的 1~9 往下排）

10. **`free_play` 零口上是二期自己埋的坑。** 方案 §2.6 只安排了 `follow_mother.csv` 的
    10 条，而 `free_play` 是实施时才加的行为（偏离 3），加完没有回头补口上。
    **零口上的行为是彻底静默的**：`choice_talk_from_talk_data` 只有当行为在
    通用地文表里时才有回落，否则一个字都不打印。而它偏偏是**回落链的唯一出口**
    加**两套预设模板的晚上时段**，是二期最常被执行的行为之一。
    **往后新增行为，「注册了」与「有内容」要分开验**——一期第六轮那套符号级机扫
    只查代码引用，查不出口上是不是空的。

11. **口上的前提列绝不能留空。** 写中立兜底那两条时把 `premise` 留空了，
    `buildconfig` 不报错，但 `game_config.load_talk` 读 `now_tem.premise` 直接
    `AttributeError`，**完整重建后游戏起不来**。v0.67 已经因为同一件事栽过一次
    （性技实操课的三条到场/旁观口上），本轮又栽了一次。
    中立兜底改用 `sys_1`（NPC 触发该指令）：`free_play` 恒由 NPC 触发，永真且语义正确。
    顺手对 `data/talk` 全量扫了一遍空前提，现在是 0。

12. **`have_work` 判的是行为发起者，不是母亲。** 见学口上的「妈妈在干活 / 妈妈今天没工作」
    两档从上线起就没分开过：孩子一长成幼女就被赋予 152 学生岗，`have_work` 于是恒为真。
    实测两种母亲下候选池完全相同、都是 10 条。结算侧（`settle_follow_mother_gain`）分得很对，
    只有口上这一层判错了对象。补 `t_have_work` / `t_not_have_work` 两个目标侧前提。
    **反向前提必须成对补**：口上选取是加权随机不是最具体独占，
    只给「有工作」那 6 条加前提、「没工作」那 4 条不加，后者会在两种情形下都出场。

13. **`follow_mother_flag` 是 `CHILD_GROWTH` 19 个字段里唯一只写不读的。**
    状态机里的注释自己写着「供口上前提与面板判定使用」，两个消费者一个都没建。
    与一期 `report_card_flag` 是同一类半截链的**镜像**（那个有读无写）。
    **置位一处、清位四处**：自由玩耍状态机、见学结算、上课接管、见学判定不成立，
    外加每日结算兜底。其中**上课接管**那处最容易漏——`judge_class_state_machine`
    排在见学判定**之前**，幼女从见学转去上课时根本走不到 `judge_follow_mother_state_machine`。
    一开始连目标侧的 `t_follow_mother` 一起写了，但没有任何口上会用它——
    那正是本轮在清理的同一类债，于是删掉。

14. **`judge_require` 的素质分支一直判错素质，这是缺口 4 的真正根因。**
    给日程改写接上 `need` 校验后，测试立刻报「连幼女都过不了 `T102|1`」。
    读代码发现该分支取的是 `talent[judge_value]`，把竖线**后面**的「要求值」当成了素质 id，
    而 `A` / `J` / `E` / `O` 四个分支取的都是竖线**前面**的 id：

    | 配置 | 本意 | 实际判成 |
    | --- | --- | --- |
    | `T7\|0`（品酒） | 非未成年 | 素质 0 阴道处女 |
    | `T103\|1`（过家家） | 是萝莉 | 素质 1 肛门处女 |
    | `T102\|1`（跟随母亲） | 是幼女 | 素质 1 肛门处女 |

    **总纲口径 52 写的「既有配置已经把品酒挡在孩子之外」实际上是反的**：
    未成年角色只要还是处女就能品酒，成年角色反倒被挡住。
    **敢改这个共享函数，是因为先量过影响面**：全仓库 CSV 里 `T<id>|<值>`
    只出现三次，全在 `Entertainment.csv`。这是一处行为回正，不是全局语义变更。

15. **批量套用的名单会列出全岛干员。** `get_child_candidate_list` 用的是只看素质的
    `judge_is_child`，而世界设定「萝莉化」会把全岛干员的年龄素质改写为萝莉 103。
    一期 `get_student_candidate_list` 的注释里**逐字写过这个陷阱**，二期这个函数还是掉了进去。
    处理方式是**删掉重复实现**而不是给它补条件——同一个语义只留一个口子，
    下次再改血缘或阶段口径时才不会漏改一处。顺带把婴儿也挡掉了。

16. **模板此前不能新建。** §1 写的是「可定义**若干套**」、§4.2 的验证清单写的是「能**新建**」，
    而实装是固定 4 套。补上新建 / 重命名 / 删除。
    **新编号从既有最大编号往后顺延，不补空缺号**：孩子身上存的是模板编号，
    删掉 5 号后把新模板也叫 5 号，原来套 5 号的孩子会凭空换一套日程。
    **删除前必须解开引用它的孩子**；四套预设不可删（`init_default_template`
    只在整张表为空时才补），但可改名、可改内容。
    另外补上「不套用日程（恢复随机）」的出口——`apply_template(id, 0)` 数据层一直支持，
    只是面板没给按钮，少了它孩子一旦套上日程就再也回不去。

17. **口径 25 / 32 是二期误认领。** 二期的三个目标里没有任何对应内容，
    §8 的范围外还明写「养成事件系统 → 三期」。这两条实际由三期兑现
    （`get_sibling_child_list` / `get_classmate_list` + 38 条用了兄弟姐妹/同学前提的公务事件）。
    从二期的认领清单里摘掉，总纲里就地标注实装位置。

#### 单元测试结果

新建 `test_phase2_fix.py`，**65 条断言全部通过**；连同一期的 `test_semester`（120 条）
一起跑，**185 条全绿**。

断言的重点：

- **口上池的实际构成**：母亲有工作时池里**只有**「在干活」那 6 条、无工作时**只有**
  「没工作」那 4 条，两个池不再相同——修前两个池是同一批 10 条。
- **状态标识的两个方向**：置位后 `<学>` 出现、清位后消失；没有 `child_growth`
  的角色（全岛绝大多数干员）读口与前提都安全返回而不是 `AttributeError`。
- **need 校验的两侧**：幼女那一格照常写成 176、萝莉那一格不再被写——
  只断言「萝莉不写」是不够的，把 `judge_require` 判错素质这个更深的问题正是
  「幼女应当写得进去」这条反向断言逼出来的。
- **删除模板的连带效应**：引用它的孩子被解开、删过的编号不被复用、预设删不掉。

本轮测试脚本自身踩的两个坑：

1. **`behavior.start_time` 不能设成 `None`**——`get_class_period` 读它时 `None` 会回落
   `cache.game_time` 没问题，但 `get_character_status_list:211` 直接取 `.hour`，`None` 会崩。
2. **脚本末尾必须 `os._exit()`**——导入链会起 Web 服务的非守护线程，
   断言跑完、`print` 也打完了，进程却不会自己结束。串跑两个脚本时表现为第二个「一直没输出」，很容易误判成第二个脚本卡死。

#### 尚未覆盖的验证

- Tk 与 Web 两种模式的人工验收：`<学>` 标识的位置与悬停提示、
  模板面板新增的三个按钮（新建 / 重命名 / 删除）的排版、「不套用日程」的出口。
- **文本输入在 Web 模式下的表现**：新建与重命名走的是 `panel.AskForOneMessage`，
  它在 Web 侧会弹一个固定文案「请输入文本：」的输入框，与 Tk 下的提示语不一致，未实测。
- `judge_require` 素质分支回正后，品酒与过家家进入随机娱乐池的实际频率未观察——
  这两项此前谁都抽不到（品酒只对阴道处女开放、过家家只对肛门处女开放）。
- `free_play` 的 12 条与见学聊天的 8 条在实际游戏里的出现频率与重复感未验。
