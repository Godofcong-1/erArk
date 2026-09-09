# Plan 22（四期·实施步骤与记录）：性技实操课（课堂 H 模式）+ 妊娠期胎教 + 婴儿期照料差异化

> 本文件是 `plan_22_生长养成系统_四期_方案.md`（下文简称"方案"）的**实施步骤清单与过程记录**。
> 需求背景、现状调查、设计决策、风险与范围外事项以方案与
> `plan_22_生长养成系统_总纲.md`（下文简称"总纲"）为准；
> **角色字段定义以 `plan_22_生长养成系统_一期_方案.md` §4 为准**（下文简称"一期方案"）。
> 本文件只写"怎么做、怎么验、怎么回滚"，实施过程与结果记入 §6。

- 状态：**4-A / 4-B 已实施并于 2026-09-09 完成第二轮修正（§6.9）、4-C 功能闭环已实施**（2026-09-07）。4-C 的口上已于 2026-09-09 补齐到 183 条（§6.10）、§4.1 行为级单元测试待补；
  4-A / 4-B 单元测试 101 条全绿（§6.8）；游戏内整体测试待用户执行
- 适用代码快照：`master @ 1667df589`
- **前置**：一期已实施完毕（`Script/System/Education_System/` 9 个模块 3448 行，教育区地图已改建）
- 实施前提：先通读方案 §3.28 全节与 §4.3；实施中发现与方案冲突的事实，**先更新方案再动代码**

---

## 0. 实施顺序：四期拆三块，本轮只做 4-C

⚠️ **本文件在 2026-09-07 第 4 轮设计后重写**。原 v3 的内容（把性技实操课写成"走既有 H 链的一段行为"）已全部作废。

| 块 | 内容 | 方案位置 | 依赖 | 本轮 |
| --- | --- | --- | --- | --- |
| 4-A | 妊娠期胎教 | §3.27、§4.1 | 一期 | **✅ 已实施 2026-09-07**（§6.6） |
| 4-B | 婴儿期 6 个照料行为差异化 | §3.20 | 一期 | **✅ 已实施 2026-09-07**（§6.7） |
| **4-C** | **性技实操课 / 课堂 H 模式** | **§3.28 全节、§4.3、§5** | 一期（重度） | **功能闭环已实施**（口上 49/165，§6.1~§6.5） |

三块互不依赖，可任意顺序做。4-A / 4-B 的原步骤保留在 §7 备查。

**4-C 内部的推荐实施顺序**（每步做完可独立验证，不必等下一步）：

```
① 数据层    字段 + 存档回填 + 效果 id + 前提            → 单元测试：字段回填、前提取值
② 行为层    4 个行为 + 指令 + 常量三处同步              → 游戏内：指令能出现、能开课关课
③ 结算层    模式开关、主修加成、旁观收益、出勤          → 单元测试：加成倍率、旁观 25%
④ 课表层    临时课程存取 + get_class_cell 覆盖层        → 单元测试：覆盖命中与不命中
⑤ AI 层     预到岗 + 必修豁免 + 降级旁观 + 移动查下一节 → 单元测试：三种学生的状态机分支
⑥ 提醒层    三次提醒的跨越判定 + 去重 + 跨天清理        → 单元测试：时间跳跃下不漏发不重发
⑦ 面板层    临时课程编辑面板 + 下课入口                 → 游戏内：排课、指定必修、下课
⑧ 口上      11 个文件约 165 条                          → 游戏内：各档差分能出
```

⚠️ **①~⑥ 做完游戏就能玩了**（当场开课这条链只需 ①②③⑤ 的一部分）；⑦⑧ 是让预约那条链好用。

---

## 1. 4-C 改动文件清单

> ⚠️ 全部 cid / 效果 id / 前提 cid / 指令 cid **不在此预分配**，实施时现查空闲号（方案 §7-9）。

### 1.1 数据层（3 个）

| 文件 | 类型 | 改动 |
| --- | --- | --- |
| `Script/Core/game_type.py` | 改 | `Cache` 加 `sex_class_mode`（紧挨 `:1971 group_sex_mode`）；`Rhodes_Island` 加 `temp_sex_class`（与一期的 `class_schedule` 并列）。**结构以方案 §4.3.1 / §4.3.2 的代码块为最终定义** |
| `Script/Core/save_handle.py` | 改 | 两个字段的 `hasattr` 回填：`sex_class_mode` → `False`；`temp_sex_class` → `{}`（照一期 `class_schedule` 的写法，`:551` 附近） |
| `Script/Core/constant_effect.py` | 改 | `SEX_CLASS_MODE_ON` / `SEX_CLASS_MODE_OFF` 两个效果 id（照 `:17/:19` 的 `GROUP_SEX_MODE_ON=10010` / `OFF=10011` 就近取号）；另加主修加成、旁观收益、出勤三个结算效果 id |

### 1.2 前提（2 个）

| 文件 | 类型 | 改动 |
| --- | --- | --- |
| `Script/Core/constant_promise.py` | 改 | `SEX_CLASS_MODE_ON` / `_OFF`（照 `:22/:24` 群交模式的写法）、`SCENE_HAVE_SEX_CLASS_STUDENT`（场景内有可参与的学生）、`SELF_IN_SEX_CLASS`（自己正在上实操课） |
| `Script/Design/handle_premise/handle_premise_H.py` | 改 | 上述前提的实现函数（照 `:2207 handle_self_now_go_to_join_group_sex` 的写法） |

⚠️ **地点前提零新增**：实践教室 `handle_premise_place.py:3702` 与大礼堂 `:3734` 已存在，指令前提里取或即可。
⚠️ **按科目的前提零新增**：一期已实现 `Course` 型 CVP token（`handle_premise/__init__.py:511`），
口上里直接写 `CVP_A1_Course|74_G_0`。

### 1.3 行为与指令（7 个）

| 文件 | 类型 | 改动 |
| --- | --- | --- |
| `data/csv/Behavior_Data.csv` | 改 | 3 个一段行为：`start_sex_class`(5,pl,性爱) / `end_sex_class`(5,pl,性爱) / `join_sex_class`(5,npc,性爱)。**照抄 `:170~180` 群交那一组的写法** |
| `data/csv/Behavior_Effect.csv` | 改 | 三者效果串照抄 `:370 ask_group_sex` / `:371 group_sex_end` / `:376 join_group_sex`，末尾换成新的模式开关 id（方案 §3.28.10 的表） |
| `data/csv/Behavior_Introduce.csv` | 改 | 三个行为的介绍文本 |
| `data/csv/SecondBehavior.csv` | 改 | `watch_sex_class` 旁观二段行为 |
| `Script/Core/constant/Behavior.py` / `BehaviorStr.py` / `Behavior_Int.py` | 改 | 三个一段行为的常量同步 |
| `Script/Core/constant/SecondBehavior.py` / `SecondBehavior_Int.py` | 改 | 旁观二段行为的常量同步 |
| `data/csv/InstructConfig.csv` | 改 | 「性技实操课」（开课）与「结束性技实操课」（下课）两条指令 |

⚠️ **不往 `data/csv/InstructJudge.csv` 加行**——无实行值要求靠"指令处理函数不传 `judge` 参数"实现（方案 §3.28.2）。

### 1.4 结算（4 个）

| 文件 | 类型 | 改动 |
| --- | --- | --- |
| `Script/Settle/default.py` | 改 | 模式开关两个结算器（照抄 `:3041 handle_group_sex_mode_on` / `:3065 ..._off`）；主修科目加成；旁观收益；开课时的出勤记录 |
| `Script/Settle/realtime_settle.py` | 改 | 第 2、3 次提醒的跨越判定 |
| `Script/Settle/past_day_settle.py` | 改 | 第 1 次提醒（起床后）；跨天清理过期 `temp_sex_class`（⚠️ 跳过 `running` 的那条） |
| `Script/System/Education_System/sex_class_handle.py` | **新增** | 课堂 H 的核心逻辑：开课/下课、临时课程增删查、主修经验 id 解析、旁观名单、三次提醒的时刻计算 |

### 1.5 课表与 AI（4 个）

| 文件 | 类型 | 改动 |
| --- | --- | --- |
| `Script/System/Education_System/schedule_handle.py` | 改 | `:121 get_class_cell()` 开头插临时课程覆盖层（方案 §3.28.3） |
| `Script/System/Education_System/class_ai.py` | 改 | 新增 `judge_pre_arrive_sex_class()`；`judge_class_state_machine()` 两道闸加必修豁免与降级旁观 |
| `Script/Design/handle_npc_ai.py` | 改 | `:357` 之前插预到岗判定 |
| `Script/StateMachine/default.py` | 改 | `:434 character_move_to_class_room` 加"预到岗时查下一节次"分支 |

### 1.6 面板（2 个）

| 文件 | 类型 | 改动 |
| --- | --- | --- |
| `Script/System/Education_System/class_schedule_panel.py` | 改 | 临时课程编辑面板（方案 §5.2 的线框图） |
| `Script/System/Sex_System/group_sex_panel.py` | 改 | 课堂模式的标题差分；体力 < 30% 者标「体力不足，仅旁观」且不可选（方案 §5.3） |

### 1.7 口上（11 个文件、约 165 条）

目录 `data/talk/sex/sex_class/`，明细见方案 §3.28.10 的表。
⚠️ 表头 5 行照抄 `data/talk/sex/start_or_end/ask_grop_sex.csv`（`cid,behavior_id,adv_id,premise,context`），各文件 cid 从 1000 起。

### 1.8 ArkEditor 同步（2 个）

`tools/ArkEditor/csv/Behavior_Data.csv`、`tools/ArkEditor/csv/Effect.csv`。

---

## 2. 4-C 详细改动步骤

### 2.1 ① 数据层

1. `game_type.py` 加两个字段，**代码块直接抄方案 §4.3.1 / §4.3.2**（`notified` 是三元组、另有 `running`）
2. `save_handle.py` 两处 `hasattr` 回填
3. `constant_effect.py` 加 5 个效果 id（2 个模式开关 + 3 个结算）
4. `constant_promise.py` + `handle_premise_H.py` 加 4 条前提

⚠️ **`temp_sex_class` 的键是 `"日期序数-节次"` 字符串**（如 `"739510-3"`），日期序数取 `date.toordinal()`。
⚠️ 所有 dict 访问一律 `.get()`，旧档回填出的空 dict 每一层都可能缺键。

### 2.2 ② 行为层

1. 三个一段行为进 `Behavior_Data.csv` + `Behavior_Effect.csv` + `Behavior_Introduce.csv`，效果串照抄群交那一组
2. 常量三处同步（`Behavior.py` / `BehaviorStr.py` / `Behavior_Int.py`）
3. `watch_sex_class` 二段行为 + 两处常量
4. 两条指令进 `InstructConfig.csv`
5. 开课指令的前提：`(实践教室 或 大礼堂) 且 场景内有可参与的学生 且 不在 H 中`
6. 下课指令的前提：`sex_class_mode_on`

⚠️ **开课指令的处理函数不传 `judge` 参数**（方案 §3.28.2）——这是"无实行值要求"的全部实现。

### 2.3 ③ 结算层

1. 模式开关两个结算器照抄 `default.py:3041/:3065`；⚠️ **开课时必须同时置 `cache.group_sex_mode = True`**，
   下课时两个一起清零（方案 §7-17）
2. **主修加成**：H 结算给学生加经验时，若经验 id == `growth_handle.get_subject_exp_id(本节科目)`，
   乘 `课程加成 × 速度系数 × 教育区加成`。三个系数分别是 2.0（新常量）、
   `growth_handle.get_learn_speed()`、`growth_handle.get_education_zone_adjust()`（后两个一期已有）
3. **旁观收益**：遍历场景内的到场学生里**未占用模板部位**的那些，给主修经验 25% +
   羞耻(16) + 欲情(12)。⚠️ 三项全部 `tenths_add=False`（方案 §7-25）；
   ⚠️ **入口用 `cache.sex_class_mode` 严格圈住**，绝不能在普通群交里生效（方案 §7-24）
4. **出勤**：开课时给到场学生 `attend_class_count += 1`，只记这一次（方案 §3.28.9）
5. 旁观二段行为按 **30%** 概率赋予（口上限流），⚠️ **收益结算不限流**

### 2.4 ④ 课表层

在 `schedule_handle.get_class_cell(classroom, week_day, period)` **开头**插覆盖层：

```
今天的日期序数 + period 拼出 key
若 temp_sex_class 有这个 key 且 classroom 对得上
    → return [该临时课的 ability_id, 0]      # 教师 id 为 0 即玩家
否则走原逻辑
```

⚠️ **只有这一处改动**，下游的 `get_now_course()` / `get_now_teaching()` / `class_ai` 派课 /
`MOVE_TO_CLASS_ROOM` / 课表面板 / `<课>` 状态标识全部自动跟上（方案 §3.28.3）。

⚠️ `get_class_cell` 的 `week_day` 参数与临时课程的日期序数**不是一回事**——覆盖层要用"今天"，
不能用传进来的 `week_day`（那是周几，一周内会重复）。

### 2.5 ⑤ AI 层

1. **预到岗** `class_ai.judge_pre_arrive_sex_class(character_id)`，插在
   `handle_npc_ai.py:357` 调 `judge_class_state_machine()` **之前**。三个条件全满足才返回 `MOVE_TO_CLASS_ROOM`：
   - 下一个节次是自己要上的性技实操课（在 `temp_sex_class` 里，且自己在选修者或必修名单中）
   - 当前时刻距该节次开始 ≤ **10 分钟**
   - 人不在目标教室
2. **`MOVE_TO_CLASS_ROOM` 查下一节**：`StateMachine/default.py:434` 现在查的是 `get_now_course()`（当前节次）。
   加一个分支：预到岗时改查下一节次的教室，否则学生会走去上一节课的教室
3. **必修豁免心情闸**：`judge_class_state_machine()` 第二道闸前判一次"自己在本节的 `must_attend` 里"，是则跳过翘课判定
4. **体力闸降级旁观**：必修学生体力 < 30% 时**不返回 `REST`、不调 `settle_absent`**，照常去教室
5. **提前退场不算缺课**：预到岗分支**不调** `settle_absent`（方案 §7-23）

⚠️ **第 4、5 条都是"不做某事"**，最容易在实施时漏掉——写完对着方案 §3.28.4 / §3.28.5 再核一遍。

### 2.6 ⑥ 提醒层

三次提醒共用一套跨越判定：`上次结算时间 < 提醒时刻 <= 当前时间` 则触发，
照 `game_time.py:153 sub_time_now` 的切月写法。⚠️ **不能用等于判定**——时间按行为时长跳跃（方案 §3.28.6）。

| # | 时刻 | 落点 | 去重 |
| --- | --- | --- | --- |
| 1 | 玩家起床后 | `past_day_settle.py` 或起床行为结算 | `notified[0]` |
| 2 | 节次开始前 30 分钟 | `realtime_settle.py` | `notified[1]` |
| 3 | 节次结束时刻（开始 + 45 分） | 同上，**且只在 `sex_class_mode` 进行中才发** | `notified[2]` |

⚠️ 第 3 次的措辞必须是"你可以继续，也可以随时结束这节课"，不能写成催促（方案 §7-29）。

**跨天清理**：`past_day_settle.py` 删掉日期序数 < 今天的条目，
⚠️ **但跳过 `running == True` 的那一条**——拖堂可以跨天，删了就找不到课程数据（方案 §7-27）。

### 2.7 ⑦ 面板层

1. 临时课程编辑面板：入口挂 `class_schedule_panel.py` 的教室周表格子，线框图见方案 §5.2
2. ⚠️ **"本节选修本教室的学生：N 人"是必做项**，N=0 时提示"没有学生会来，建议指定必修学生"
3. ⚠️ 必修名单每人后面标"将顶替她的第 N 节 XX 课"
4. 科目选择**只列 70~75、77 七门**，不列 76 腰技（男性专属，方案 §7-21）
5. 下课入口：`sex_class_mode_on` 时场景指令面板出现「结束性技实操课」，照抄群交的写法
6. `group_sex_panel.py` 的模板编辑面板：体力 < 30% 者标「体力不足，仅旁观」且不可选

⚠️ 只用 `Script/UI/Moudle/draw.py` 的抽象绘制类，不直接操作 Tk 或 HTML。

### 2.8 ⑧ 口上

按方案 §3.28.10 的表生成 11 个文件。三点注意：

1. 主修科目口上用 `CVP_A1_Course|<能力id>_G_0` 分流（一期已实现的 token）
2. 孩子相关口上带 `self_is_player_daughter`，命中 `talk.py:185~188` 的女儿 5 倍加权
3. 各 CSV 表头 5 行照抄 `data/talk/sex/start_or_end/ask_grop_sex.csv`，cid 从 1000 起

---

## 3. 构建与缓存

```bash
.conda\python.exe buildconfig.py   # CSV / 常量改动后
.conda\python.exe buildpo.py
.conda\python.exe buildmo.py
```

⚠️ **`buildconfig.py` 会清空 `data/po/`**（本机无 xgettext/polib），跑完必须 `git checkout -- data/po/`。
⚠️ 本期**不涉及地图改动**，不需要删场景缓存。

---

## 4. 验证清单

### 4.1 单元测试（按 `headless-game-test` 模式 A）

**数据层**

- [ ] 旧档载入：缺 `sex_class_mode` / `temp_sex_class` 时 `hasattr` 回填，不抛异常
- [ ] `temp_sex_class` 的键格式与 `.get()` 访问在空 dict 下不 KeyError

**课表层**

- [ ] `get_class_cell()` 命中临时课程时返回 `[性技科目id, 0]`
- [ ] **不命中时原样返回原课**（同一间教室、同一节次、**不同日期**必须走原逻辑——这是周循环 BUG 的回归测试）
- [ ] 临时课程顶替空格子（原本没课）时也能返回

**结算层**

- [ ] 主修加成：做命中主修经验 id 的动作，学生该经验按 `×2.0 ×速度系数 ×教育区加成` 增加
- [ ] **非主修动作照常结算但不加成**（做手部动作、主修是膣技时，手交经验按原值增加）
- [ ] 旁观收益：未占模板部位的到场学生获得主修经验的 25% + 羞耻 + 欲情
- [ ] **旁观结算不泄漏**：`sex_class_mode = False` 的普通群交中，围观干员**零收益**
- [ ] 旁观状态用 `tenths_add=False`：同一学生连续旁观 10 次，羞耻增量不呈滚雪球增长
- [ ] 出勤只记一次：一节课做 20 个动作后，学生 `attend_class_count` 只 +1

**AI 层**

- [ ] 预到岗：距实操课开始 9 分钟时，选修学生返回 `MOVE_TO_CLASS_ROOM` 且目标是**下一节**的教室
- [ ] 距开始 11 分钟时不触发预到岗
- [ ] **提前退场不算缺课**：预到岗后学生 `absent_count` 不变、`last_absent_period` 不被占用
- [ ] 必修学生心情极差（四个负面状态等级和 > 16）时**不翘课**
- [ ] 必修学生体力 < 30% 时**不返回 REST、不记缺课**，照常去教室
- [ ] 非必修学生的两道闸行为与改动前一致（回归）

**提醒层**

- [ ] 时间跳跃下不漏发：玩家 13:00 起做一个 60 分钟行为，13:30 的提醒在 14:00 结算时补发
- [ ] 三次提醒各自只发一次（连续 5 次结算只触发 1 次）
- [ ] 第 3 次提醒只在 `sex_class_mode` 为真时发
- [ ] **跨天清理跳过进行中的课**：`running=True` 的条目跨天后仍在

**模式层**

- [ ] 开课后 `sex_class_mode` 与 `group_sex_mode` **同时**为真
- [ ] 下课后两者**同时**为假
- [ ] 拖堂：H 中的学生 `find_character_target` 直接 return，不被派去上下一节课

### 4.2 游戏内整体测试（由用户执行）

- [ ] 走进实践教室，场景内有学生时能看到「性技实操课」指令；没有学生时看不到
- [ ] 在走廊等其他房间看不到该指令
- [ ] 当场开课能进入 H 模式，群交模板面板正常显示
- [ ] 对孩子无实行值要求；对成年干员仍需 S 350
- [ ] 在课表面板能排临时课程，能看到"本节有 N 名学生选修"
- [ ] 能指定必修学生，面板显示"将顶替 XXX 的第 N 节 XX 课"
- [ ] 科目列表只有 7 门，没有腰技
- [ ] 预约当天起床后收到提醒；开始前半小时收到提醒
- [ ] 学生在开始前 10 分钟往教室走
- [ ] 到点开课，选修的学生在场
- [ ] 到了预定下课时刻收到提示，但可以继续
- [ ] 「结束性技实操课」能随时点，提前和拖堂都正常
- [ ] 旁观的学生有文本反应，且不会每个动作都刷
- [ ] Web 模式（`web_draw = 1`）下表现一致
- [ ] 旧存档载入不报错，既有群交流程未被破坏

---

## 5. 回滚

| 单元 | 回滚方式 | 备注 |
| --- | --- | --- |
| 口上 | 删 `data/talk/sex/sex_class/` 整个目录 | 独立，删了只是没文本 |
| 面板 | revert `class_schedule_panel.py` + `group_sex_panel.py` | 独立 |
| AI 层 | revert `class_ai.py` + `handle_npc_ai.py` + `StateMachine/default.py` | ⚠️ 必须三个一起 revert，否则预到岗判定调不到 |
| 课表层 | revert `schedule_handle.py` 的覆盖层 | 存档里的 `temp_sex_class` 留着不影响载入 |
| 结算层 | revert `Settle/default.py` + `realtime_settle.py` + `past_day_settle.py` | ⚠️ 若 `temp_sex_class` 已有数据，跨天清理没了会残留，但不报错 |
| 行为与指令 | revert 4 个 CSV + 5 处常量 | ⚠️ 存档里若有角色 `state` 停在新行为上，载入会 KeyError → 先在游戏里下课再回滚 |
| 数据层 | revert `game_type.py` + `save_handle.py` | 旧档因 `hasattr` 回填天然兼容 |

⚠️ **唯一需要留神的是行为 cid**：若存档中有角色的 `behavior.behavior_id` 停在新增的行为上，
删掉行为定义后载入会报错。→ **回滚前先在游戏内结束所有课堂 H 模式并存档**。

---

## 6. 实施过程记录（4-C）

- 本轮实施日期：2026-09-07
- 实施范围：**①~⑦ 全部完成，⑧ 口上完成约 30%**（49/165 条）
- 代码快照：基于 `master @ 1667df589`

### 6.1 实际改动

| 文件 | 类型 | 实际改动 |
| --- | --- | --- |
| `Script/Core/game_type.py` | 改 | `Cache.sex_class_mode`（紧邻 `group_sex_mode`）、`Rhodes_Island.temp_sex_class`（+13 行）|
| `Script/Core/save_handle.py` | 改 | `temp_sex_class` 的 `hasattr` 回填（+4 行）|
| `Script/Core/constant_effect.py` | 改 | `SEX_CLASS_MODE_ON=10014` / `_OFF=10015`；顺带把一期误插在 512~513 之间的 548~554 七个 id 挪回 547 之后的正确位置（+16 / -12 行）|
| `Script/Core/constant_promise.py` | 改 | 8 条新前提常量 + `SELF_NOT_UNDERAGE`（+18 行）|
| `Script/Design/handle_premise/handle_premise_H.py` | 改 | 7 条前提实现（模式开关 ×2、下课三档 ×3、场所、场景有学生、自己在课上）（+120 行）|
| `Script/Design/handle_premise/handle_premise_talent.py` | 改 | `SELF_NOT_UNDERAGE`（+11 行）|
| `Script/Design/settle_behavior.py` | 改 | 玩家结算末尾挂旁观收益，判 `sex_class_mode` 而非 `group_sex_mode`（+8 行）|
| `Script/Settle/default.py` | 改 | 模式开关两个结算器；开课时把在场学生全部拉进 H 并派二段行为、记出勤（+62 行）|
| `Script/Settle/common_default.py` | 改 | 经验通用结算里插主修加成（+8 行）|
| `Script/Settle/realtime_settle.py` | 改 | `settle_sex_class_notify()`，三次提醒的输出（+43 行）|
| `Script/Settle/past_day_settle.py` | 改 | 跨天清理过期临时课程（+7 行）|
| `Script/System/Education_System/sex_class_handle.py` | **新增** | 核心模块，30 个函数 + 8 个可调常量（**775 行**）|
| `Script/System/Education_System/schedule_handle.py` | 改 | `get_class_cell()` 开头的临时课程覆盖层（+11 行）|
| `Script/System/Education_System/class_ai.py` | 改 | `judge_must_attend_sex_class()` / `judge_pre_arrive_sex_class()` / `get_next_sex_class()`；两道闸的必修豁免（+111 / -7 行）|
| `Script/System/Education_System/class_schedule_panel.py` | 改 | `_edit_sex_class()` 临时课程编辑面板（+170 行）|
| `Script/Design/handle_npc_ai.py` | 改 | `:348` 上课判定之前插预到岗判定（+6 行）|
| `Script/StateMachine/default.py` | 改 | `character_move_to_class_room` 加"预到岗查下一节次"分支（+15 / -1 行）|
| `Script/System/Instruct_System/Instruct.py` | 改 | 两条指令常量（+4 行）|
| `Script/System/Instruct_System/handle_instruct.py` | 改 | `handle_start_sex_class()` / `ask_for_sex_class_ability()` / `handle_end_sex_class()`（+105 / -1 行）|
| `Script/System/Sex_System/group_sex_panel.py` | 改 | 课堂模式下不判群交实行值（+5 / -2 行）|
| `data/csv/Behavior_Data.csv` | 改 | 383 开课 / 384 下课（5 分钟, pl, 性爱）、1504 到场 / 1505 旁观（0 分钟, npc, 二段结算）|
| `data/csv/Behavior_Effect.csv` | 改 | `383 = 406-462-464-608-636-1410-10010-10014`、`384 = 529-407-636-800-10011-10015`、`1504/1505 = 998` |
| `data/csv/Behavior_Introduce.csv` | 改 | 948~951 四条介绍 |
| `data/csv/InstructConfig.csv` | 改 | 6906 性技实操课（OBSCENITY 类）、6907 结束性技实操课（SEX 类）|
| `tools/ArkEditor/csv/Behavior_Data.csv` | 改 | 四个行为同步 |
| `data/talk/sex/sex_class/` | **新增** | 11 个文件、**49 条**（开课 5 / 到场 7 / 旁观 7 / 下课 9 / 七门主修各 3）|

合计 **26 个文件、约 1560 行**（其中新增模块 775 行、口上 49 条）。

**与方案的偏离**：

1. **二段行为没走 `SecondBehavior.csv`，改用 `Behavior_Data.csv` 的「二段结算」类**（cid 1504 / 1505、时长 0、效果 `998`）。
   照抄的是 `1501~1503` 催眠素质那一组的既有写法，比方案原定的 `SecondBehavior.csv` 路线少动两个常量文件。
   于是 §1.3 里预留的 `SecondBehavior.py` / `SecondBehavior_Int.py` 两处常量同步**未发生**。
2. **前提比方案多 4 条**：方案只列了 `SEX_CLASS_MODE_ON/_OFF`、`SCENE_HAVE_SEX_CLASS_STUDENT`、`SELF_IN_SEX_CLASS`；
   实际另加了下课三档（`SEX_CLASS_END_EARLY` / `_ON_TIME` / `_LATE`，供下课口上分差分）与 `IN_SEX_CLASS_PLACE`
   （把实践教室与大礼堂两条既有地点前提并成一条，指令前提里不必写"或"）。另附带补了 `SELF_NOT_UNDERAGE`。
3. **结算效果只加了 2 个而非 5 个**：方案设想主修加成、旁观收益、出勤各占一个效果 id，实际这三件事都不是
   "行为效果串里的一项"——主修加成挂在 `common_default.base_chara_experience_common_settle()` 的经验通用结算里，
   旁观收益挂在 `settle_behavior.handle_settle_behavior()` 的玩家结算末尾，出勤在开课结算器里顺手记。
   所以 `constant_effect.py` 只多了 `10014` / `10015` 两个 id。
4. **顺带修了一期的一处 id 排序错误**：`constant_effect.py` 里一期新增的 548~554 被插在了 512~513 之间，
   本次挪回 547 之后。纯排版，不影响取值。
5. **`get_class_cell()` 并非全局课表的唯一读取入口**（假设 2 的复核结果，见 §6.2）——
   `get_teacher_now_class()`（`:187`）与 `get_teacher_week_schedule()`（`:203`）直接遍历 `class_schedule` 做教师反查，
   这两处**看不到临时课程**。本轮判定为可接受：临时实操课的授课者恒为玩家（教师 id 写死 0），
   而玩家不走教师反查那条 AI 链。⚠️ 若日后允许指派干员当实操课教师，这两处必须一并加覆盖层。

**已知限制**：

1. **口上只填了 49 条 / 约 165 条**（约 30%）。开课、到场、旁观、下课四类各有基础文本，
   七门主修科目各只有 3 条，年龄档（幼女 / 萝莉）与"必修 / 选修"的差分尚未铺开。缺的部分只是没文本，不影响功能。
2. **游戏内整体测试（§4.2）全部未执行**——本轮只做到静态装配级验证（§6.3），留给用户。
3. **Web 模式（`web_draw = 1`）未验证**。新面板只用了 `draw.py` 的抽象类，理论上自动适配，但未实测。
4. **PO 词条未补**：本机无 `xgettext` / `polib`，新增的界面文案与 CSV 词条要在有工具链的环境补跑
   `buildpo.py` / `buildmo.py`（与三期同样的遗留）。
5. **4-A（胎教）、4-B（照料差异化）未动**，步骤保留在 §7。

### 6.2 实施前的假设复核

| # | 假设 | 复核结果 |
| --- | --- | --- |
| 1 | 一期教育系统已实施完毕，`Education_System/` 9 个模块可用 | ✅ 成立，本轮直接复用 `growth_handle` / `schedule_handle` / `class_ai` |
| 2 | `schedule_handle.py:121 get_class_cell` 是全局课表的唯一读取入口 | ⚠️ **部分不成立**。它是唯一的"按格子查"入口，但 `get_teacher_cell()` 与 `get_teacher_week_schedule()` 直接遍历 `class_schedule` 做教师反查。第一轮判定为可接受（§6.1 偏离 5）；**2026-09-09 已补齐**：两处教师反查在查玩家（临时课的教师恒为玩家）且星期正好是今天时，也先看 `temp_sex_class`，与 `get_class_cell` 同口径——这正是 §6.5 第 2 条死文本的根因之一，见该条 |
| 3 | `handle_npc_ai.py:290~296` 让 H 中的 NPC 完全不进 AI 目标链 | ✅ 成立，但**有一个例外**：`group_sex_mode_on && masturebate_flag_3` 时会继续往下走。课堂模式会置 `group_sex_mode = True`，所以群交自慰中的学生仍会进链——与既有群交行为一致，不额外处理 |
| 4 | `growth_handle.py:98 get_subject_exp_id()` 对 7 门性技解出的经验 id 互不重叠 | ✅ 成立，实测 70→41、71→42、72→44、73→43、74→61、75→62、77→24，**七个互不相同**；76 腰技→60 亦不与之冲突（已在源头排除）|
| 5 | `handle_instruct.py:352` 只在 `judge != ""` 时才判实行值 | ✅ 成立，两条新指令的处理函数均不传 `judge`，无实行值要求由此实现 |
| 6 | `Behavior_Effect.csv:370/371/376` 的群交开关效果串可照抄 | ✅ 成立，开课串在群交基础上换掉模式开关 id 并去掉不需要的项 |
| 7 | `Course` 型 CVP token 已由一期实现且可用 | ✅ 成立，七门主修口上直接写 `CVP_A1_Course|70_G_0` 一类 |
| 8 | `handle_premise_place.py:3702/:3734` 的实践教室与大礼堂前提可用 | ✅ 成立，二者按 `scene_tag` 的 `Practice_Room` / `Auditorium` 判定，已合并进 `IN_SEX_CLASS_PLACE` |

### 6.3 单元测试结果

本轮只做了**静态装配级验证**（无头加载配置 + 注册表比对），未写 §4.1 的行为级断言。实测：

| 检查项 | 结果 |
| --- | --- |
| 9 条新前提（含 `SELF_NOT_UNDERAGE`）是否都进了 `constant.handle_premise_data` | ✅ 全部注册，未注册数 0 |
| 4 个新行为能否从 `config_behavior` 按行为名取出 | ✅ `start_sex_class`(5) / `end_sex_class`(5) / `join_sex_class`(0) / `watch_sex_class`(0) |
| 4 个行为的效果串是否都解析成已定义的效果 id | ✅ `383=[406,462,464,608,636,1410,10010,10014]`、`384=[529,407,636,800,10011,10015]`、`1504/1505=[998]`（998 = `Must_Show`）|
| 指令 6906 / 6907 的 `premise_set` 是否逐条能解到已实现的前提 | ✅ 两条指令的全部前提均可解析，问题数 0 |
| 7 门主修科目的经验 id 是否互不重叠 | ✅ 无重复（明细见 §6.2 假设 4）|
| 常量三处（`Behavior` / `BehaviorStr` / `Behavior_Int`）与 `Instruct` 是否同步 | ✅ 四个行为常量与两条指令常量均可取值 |

⚠️ §4.1 列出的行为级断言（主修加成倍率、旁观 25%、跨越判定不漏发不重发、跨天清理跳过 `running`、
预到岗 9/11 分钟边界、必修豁免两道闸）**本轮未写**，是最主要的验证缺口。

### 6.4 尚未覆盖的验证

§4.2 游戏内整体测试的 15 项**全部待执行**，其中优先级最高的五项：

1. 走进实践教室、场景内有学生时能看到「性技实操课」指令，走廊等其他房间看不到
2. 当场开课能进 H 模式，群交模板面板正常显示，对孩子无实行值要求
3. 在课表面板排一节临时实操课，能看到"本节有 N 名学生选修"，学生到点会自己走进来
4. 三次提醒各自都能收到，且时间跳跃（做长时长行为）时不漏发
5. 「结束性技实操课」随时可点，提前下课 / 按时 / 拖堂三档口上都能出

另需在有 `xgettext` / `polib` 的环境补跑 `buildpo.py` / `buildmo.py`。

### 6.5 第二轮追加调整实施记录

**2026-09-07 第二轮（随 4-A / 4-B 一并做的 4-C 收尾）**

1. **修正一个会让游戏起不来的 BUG**：`join_sex_class.csv:1006`、`watch_sex_class.csv:1005/1006` 三条口上的前提列为空，
   `game_config.load_talk()` 读到没有 `premise` 属性的对象直接 AttributeError。第一轮只跑了增量构建、
   `Character_Talk.json` 还是旧的，所以整个 `sex_class/` 目录当时**根本没被编译过**，静态验证也就没暴露。
   本轮全量重建后才炸出来，已把三条补上 `self_not_underage`（它们本就是成年干员那一档的文案）。
   ⚠️ 教训：**新增口上目录后必须删 `Character_Talk.json` 再验**，增量构建会静默跳过。
2. **7 个 `sex_class_main_*.csv` 曾是死文本（2026-09-09 已修，另揪出并修掉了同类的 14 条，见本条末尾）。** 它们挂在 `start_sex_class`（玩家行为）上、
   前提写的是 `CVP_A1_Course|7X_G_0`，而 `handle_premise.get_now_course_ability(0)` 对玩家走的是
   `get_now_teaching()` → `get_teacher_now_class()`，那条教师反查**不经过临时课程覆盖层**（§6.2 假设 2 的后果），
   `get_now_course(0)` 又查不到玩家的个人课表，所以这 7 个文件的前提对玩家**永远不成立**；当场开课在节次外时
   学生侧同样取不到科目。要修得让 `get_now_course_ability()` 在 `sex_class_handle.get_running_class()` 非空时
   直接返回本节主修科目。
   **修法（2026-09-09）**：`sex_class_handle` 新增 `judge_in_running_class(character_id)`——有课在进行时，
   玩家恒算在课中（授课者恒为玩家，口径 38），学生则看人在不在本节课的那间教室（复用
   `class_ai.judge_in_scene`，不能只看"有课在进行"，否则同一时刻在别的教室上普通课的孩子也会被算进来）；
   `handle_premise.get_now_course_ability()` 开头先问它，成立就直接返回 `get_now_class_ability()`，
   再往下才走原来的课表两条链。教师反查 `get_teacher_cell()` / `get_teacher_week_schedule()` 绕过覆盖层的问题
   随后也补上了（§6.2 假设 2）：查玩家且星期是今天时先看 `temp_sex_class`。于是 `get_now_teaching(0)` /
   `get_now_course_type(0)` 在预约了实操课的那一节也取得到，玩家在该节手动授课时的授课状态与教学相长
   按该节主修科目结算，与学生侧早已经过覆盖层的 `get_now_course()` 对齐；NPC 教师与其他星期不受影响。
   **端到端验证时又揪出第二处死文本**：`start_sex_class.csv` 的 5 条与 `end_sex_class.csv` 的 9 条，前提列写的是
   常量名（`SCENE_OVER_TWO` / `SCENE_ONLY_TWO` / `SEX_CLASS_END_EARLY|ON_TIME|LATE`）而不是注册值
   （`place_11` / `place_10` / `sex_class_end_early|on_time|late`），运行时报「前提不存在」、一条都进不了候选池——
   也就是说开课与下课的口上从实施起就没出现过。已按注册值改正；其余 9 个文件经静态核对无此问题。
   ⚠️ 改口上 CSV 后必须删 `data/Character_Talk.json` 再构建，增量构建会静默跳过口上（同 §6.5 第 1 条的教训）。
   **验证**（headless）：开课前 `get_now_course_ability(0)` 为 -1、七条 `CVP_A1_Course|7X_G_0` 全为 0；
   当场开课（节次外）后玩家与在场学生取到 74、场外的孩子仍为 -1，七条前提恰好只有 74 那条为 1；
   `talk.handle_talk_sub(0, start_sex_class)` 的候选池未开课时含 3 条开课口上（三人在场，`place_11`）、
   开课后恰好多出 main_74 的 3 条、其余六门一条不混入，2000 次抽取里主修与开课口上都会被抽中；
   换主修为 70 后池子随之切换；课中 `end_sex_class` 的候选池恰好是一档 3 条；下课后主修三条退出池子。
3. ~~4-C 的口上仍是 49/165，本轮未补。~~ → 2026-09-09 已补齐到 183 条，见 §6.10。

### 6.6 4-A 妊娠期胎教实施记录（2026-09-07）

**实际改动**（新增 1 模块、改 11 处、口上 3 文件 30 条）：

| 文件 | 类型 | 实际改动 |
| --- | --- | --- |
| `Script/System/Education_System/baby_growth_handle.py` | **新增** | 胎教累积 / 封顶 / 清零、出生转写 `settle_prenatal_to_child()`、换算常量；顺带承载 4-B 喂奶的常量（约 170 行）|
| `Script/Core/game_type.py` | 改 | `PREGNANCY.prenatal_point: float = 0.0` |
| `Script/Core/save_handle.py` | 改 | 逐角色循环里并入 `hasattr` 回填（紧接 `external_ovulation_chance`）|
| `Script/Core/constant_effect.py` | 改 | `PRENATAL_ADD_ADJUST = 555` |
| `Script/Core/constant/Behavior.py` / `BehaviorStr.py` / `Behavior_Int.py` | 改 | `PRENATAL_TALK` / `_MUSIC` / `_TOUCH`（Int 取 952~954，即 Introduce 的 cid）|
| `Script/System/Instruct_System/Instruct.py` / `handle_instruct.py` | 改 | 三条指令常量与处理函数（照 `listen_inflation` 的写法，一行 `chara_handle_instruct_common_settle`）|
| `Script/Settle/default.py` | 改 | `handle_prenatal_add_adjust()`：交互对象 `pregnancy.prenatal_point += 0.5`，无交互对象不结算 |
| `Script/System/Pregnancy_System/born_event_panel.py` | 改 | 每个新生儿创建后立即 `settle_prenatal_to_child()` 并显示说明；全部起完名后 `clear_prenatal_point()` |
| `data/csv/Behavior_Data.csv`（+ ArkEditor 同步） | 改 | 270 `prenatal_talk` / 271 `prenatal_music` / 272 `prenatal_touch`，各 30 分钟、pl、娱乐 |
| `data/csv/Behavior_Effect.csv` | 改 | `1511 - 1512 - 21 - 22 - 55 - 555`（抚摸另带 53 亲密），照抄 `listen_inflation` 再接 555 |
| `data/csv/Behavior_Introduce.csv` | 改 | 952~954 |
| `data/csv/InstructConfig.csv` | 改 | 3031~3033，PLAY 组，前提 `HAVE_TARGET|NOT_IN_TOILET|T_INFLATION_1|T_FAKE_INFLATION_0`，部位 belly |
| `data/talk/daily/prenatal_talk.csv` / `prenatal_music.csv` / `prenatal_touch.csv` | **新增** | 各 10 条：妊娠（`t_pregnancy_1`）5 + 临盆（`t_parturient_1`）5 |

**与方案的偏离**：

1. **转写换算率方案没定，本轮取 0.5 经验/点、胎教值封顶 100**：满值 → 每科 50 经验，对照 `AbilityUp.csv` 累计需求（10/35/75/145）落在 2 级附近，是"底子好"而非"先修"的量级。
2. **转写覆盖 17 门而非 18 门**：不含 76 腰技（男性专属，女儿学不了），与 4-C 排课面板不列腰技同一口径。
3. **指令前提用 `T_INFLATION_1|T_FAKE_INFLATION_0`（真孕肚）而不是 `T_PREGNANCY_1`**：后者只覆盖妊娠（素质 21），会把临盆期（22）排除在外；孕肚素质 26 从妊娠一直挂到生产，且假孕（25）要单独排掉。
4. **转写时经验直接写 `experience` 字典**，不走 `base_chara_experience_common_settle()`——出生时没有行为，走通用函数会刷一屏升级提示，且会撞上 4-C 挂在那里的主修加成钩子。
5. **卵生分娩同样走转写**：胎教指令要求真孕肚，卵生母亲攒不到值，转写拿到 0 静默跳过，不必在面板里分支。
6. 方案 §3.27 说"母子好感与亲密"另加，实际由效果串里既有的 21/53 承担，未另建效果。

### 6.7 4-B 婴儿期照料差异化实施记录（2026-09-07）

**实际改动**（改 3 处、口上 6 文件 55 条）：

| 文件 | 类型 | 实际改动 |
| --- | --- | --- |
| `data/csv/Behavior_Effect.csv:261~266` | 改 | 在既有 `1513 - 1514 - 21 - 22 - 71 - 53` **之后追加**，既有 6 项一字未动：抱小孩 `CVE_A2_Growth|20_G_0.3 - CVE_A2_Growth|11_L_0.5`；哼唱儿歌 `CVE_A2_E|85_G_8 - CVE_A2_Growth|12_G_0.5`；喂奶 `CVE_A2_Growth|20_G_0.3 - 556`；换尿布 `CVE_A2_Growth|20_G_0.2 - CVE_A2_Growth|13_G_0.5`；教说话 `CVE_A2_E|80_G_8 - CVE_A2_E|82_G_4`；给玩具 `CVE_A2_E|91_G_5 - CVE_A2_E|90_G_5 - CVE_A2_Growth|10_G_0.3` |
| `Script/Core/constant_effect.py` | 改 | `NUIRSE_CHILD_ADD_ADJUST = 556` |
| `Script/Settle/default.py` | 改 | `handle_nuirse_child_add_adjust()`：婴儿体力/气力上限各 +2；发起者是玩家时另加好感（固定 10）与好意（基础 10）；非婴儿目标不生效 |
| `data/talk/daily/hold_child.csv` 等 5 个 | 改 | 占位文本换成 玩家（`sys_0`）5 + 保育员（`sys_1`）5 |
| `data/talk/daily/change_diapers.csv` | 改 | 原 9 条（`high_1`）原样保留，追加 5 条 `sys_0` |
| `tools/ArkEditor/csv/Effect.csv` | 改 | 顺带补登记一期～四期一直缺的 548~556 与 10014/10015 |

**与方案的偏离**：

1. **除喂奶外全部用 CVE token 写在效果串里，零新效果 id**：三期已经把养成数值接进了 `CVE_A2_Growth|N`（性格倾向 10~13、照料值 20，支持浮点），技能经验走既有 `CVE_A2_E|N`。经验 id 由 `AbilityUp.csv` 解出：话术 40→80、音乐 44→85、学识 45→82、制造 48→90、绘画 49→91。
2. **"体质相关初始值"落为体力/气力上限各 +2 / 次**；"母子好感额外加成"落为**玩家亲自喂奶**才有的好感 +10 与好意，保育员喂奶只长体质——方案 §2.2 说的"差异化对保育员同样生效、玩家亲自才额外加好感"就是这个分法。
3. ⚠️ **性格倾向的符号第一轮写反了两条，已于 2026-09-09 订正（§6.9）**。正确口径以 `education_constant.PERSONALITY_PAIR_TALENT` 为准：四对都是**正数偏前者**，10=(勤劳/懒散)、11=(坚强/脆弱)、12=(热情/孤僻)、13=(开放/羞耻)。所以偏坚强是 `11_G`、偏羞耻是 `13_L`、偏热情是 `12_G`、偏勤劳是 `10_G`。
4. 保育员的等权重随机选择逻辑（`StateMachine/default.py:1765`）**未动**。

### 6.8 4-A / 4-B 单元测试结果

脚本 `test_plan22_4ab.py`（headless-game-test 模式 A），**101 条断言全绿**，分组：

| 组 | 断言数 | 关键实测值 |
| --- | --- | --- |
| 注册与生成物 | 39 | 555/556 已注册；3 个行为与 3 条指令（含前提逐条可解）；胎教口上每档 5 条；5 个照料文件玩家档/NPC 档各 5 条且占位文本已清；换尿布 9 + 5 |
| 数据层 | 3 | `PREGNANCY()` 默认 0.0；回填代码在位；旧档缺字段时读口兜底为 0 |
| 胎教累积（555） | 5 | 一次 +0.5、两次 1.0、`add_time=0` 不累积、99.8 → 封顶 100.0、无交互对象不累积 |
| 出生转写 | 11 | 双胎各自 20 点；学识/指技各 10 经验、腰技 0；17 门全部命中；转写不清零、`clear` 后为 0；1 点时经验 0 但仍记录；无胎教不出文本 |
| 照料效果链 | 20 | 六个行为前 6 项与改动前逐项相同、追加项逐项相同、六条链互不相同；CVE 实跑：倾向 -0.5/+0.5、照料 +0.3、音乐 +8、话术 +8/学识 +4；保育员发起同样生效 |
| 喂奶（556） | 9 | 玩家：体力/气力上限 +2、好感与好意增加；保育员：体质 +2 但好感/好意不变；非婴儿不生效；`add_time=0` 不生效 |
| 口上前提 | 9 | `sys_0`/`sys_1` 对玩家与 NPC 取值正确；妊娠/临盆两档互斥；假孕时 `t_fake_inflation_0` 为假 |
| 生产面板集成 | 4 | `Born_Panel._draw_born_event_content()` 生双胎：两名新生儿各 30 点、每科 15 经验；母亲侧清零；面板输出胎教说明 |

⚠️ 断言"通用口上每档 5 条"要**过滤 `adv_id != 0`**：`data/talk/chara/0377_澄闪.csv` 里也有这几个行为的 `sys_0` 行。

**尚未覆盖**：游戏内实际点三条胎教指令看指令出现条件与文本；保育员随机照料后在养成总览看倾向值变化；Web 模式；PO 词条（同前）。

---

### 6.9 4-A / 4-B 第二轮修正（2026-09-09）

复查 4-A / 4-B 时发现三处未兑现，本轮全部处理（4-C 的口上缺口与 PO 词条按用户要求不动）。

| # | 问题 | 处理 |
| --- | --- | --- |
| 1 | **抱小孩与换尿布的性格倾向落在设计的反面**：`11_L_0.5` 实际让孩子偏脆弱、`13_G_0.5` 实际偏开放，而方案 §3.20 与 `update.log` v0.67 写的是偏坚强、偏羞耻 | `Behavior_Effect.csv:115` 改 `11_G_0.5`、`:118` 改 `13_L_0.5` |
| 2 | **换尿布的口上没做成 2 档**：其余 5 个文件都是 `sys_0` 5 条 + `sys_1` 5 条，它是 9 条 `high_1` + 5 条 `sys_0`，`high_1` 是恒真空白前提（权重 1），既让保育员抽不到专属文案，也把新写的玩家档稀释进 14 条平摊 | 旧 9 条**原文一字未动**，前提由 `high_1` 改为 `sys_1`——它们写的都是「娴熟」「一气呵成」，本就贴保育员；结果为玩家 5 条 + 保育员 9 条 |
| 3 | **孕期胎教全程无反馈**：母亲侧 `pregnancy.prenatal_point` 没有任何面板显示，`handle_prenatal_add_adjust` 也不往 `change_data` 记账，玩家要等生产那一刻才第一次知道攒了多少 | `body_info_panel.py` 的【宫】区在妊娠状态行之后加一行；`baby_growth_handle` 新增 `get_prenatal_count()` 作唯一算口，生产面板的次数也改走它 |

**为什么第 1 条不在 `update.log` 里开「修正」条目**：v0.67 是未发布块，其第 53 行原本就写的是
「抱小孩让孩子偏坚强……换尿布偏羞耻」，错的行为从未到过玩家手里，改对之后代码与该条目一致。
本轮只补了两条玩家可见的新条目（照料口上分档、身体信息面板的孕期胎教行）。

**验证**（`.conda/python.exe`，headless-game-test 模式 A）：

| 项 | 实测 |
| --- | --- |
| 倾向落点（照 `growth_panel` 的显示口径渲染） | 抱小孩→偏坚强(+0.5)、换尿布→偏羞耻(-0.5)、哼唱儿歌→偏热情(+0.5)、给玩具→偏勤劳(+0.3)；`care_point` 0.3+0.2=0.5 |
| 六个照料口上的档位分布 | 五个文件 5/5，换尿布 `sys_0` 5 + `sys_1` 9，`high_1` 已清零 |
| 孕期胎教显示三分支 | 1 次→「累积还太少」；10 次→每科 2 点；刷满 200 次→每科 50 点并标「（已达上限）」 |

⚠️ **必须重跑数据构建才看得到效果**：`game_config` 读的是 `data/data.json`，只改 CSV 不重建时运行时拿到的仍是旧效果串
（本轮第一次跑验证就被这个骗过）。⚠️ 本机跑 `auto_build_config.py` 会把 `data/po/zh_CN` 的
`erArk_csv.po`（8.4MB→2.2MB）与 `erArk_cook_question.po` 改坏，跑完必须 `git checkout -- data/po/`。

### 6.10 4-C 口上补全（2026-09-09）

按方案 §3.28.10 的差分表把 11 个文件从 49 条补到 **183 条**（+134，设计值 165），全部为主代理手写、未走 AI 批量生成。

| 文件 | 差分维度 | 补前 | 补后 | 说明 |
| --- | --- | --- | --- | --- |
| `start_sex_class.csv` | 预约 / 当场 × 多人 / 1 人 | 5 | 25 | 4 档 × 5；原 5 条按人数分的通用文本保留 |
| `end_sex_class.csv` | 提前 / 按时 / 拖堂 | 9 | 15 | 各档 +2 |
| `join_sex_class.csv` | 必修 / 选修 × 萝莉 / 幼女 / 成年 | 7 | 35 | 6 档 × 4，另加 4 条带 `self_is_player_daughter` 的女儿专属（吃 `talk.py` 的女儿 5 倍加权） |
| `watch_sex_class.csv` | 羞耻 低 / 中 / 高 × 萝莉 / 幼女 | 7 | 31 | 6 档 × 4；原 2 条成年通用文本保留 |
| `sex_class_main_*.csv`（7 个） | 交互对象 幼女 / 萝莉 | 3 × 7 | 11 × 7 | 每文件 2 档 × 4，用 `CVP_A2_T|102/103_E_1` 判开课时的第一名学生 |

**为此补的 4 个前提**（方案的"关键前提写法"表漏列了这两个维度，`constant_promise.py` / `handle_premise_H.py`，并首次把 4-C 全部 12 个前提登记进 `tools/ArkEditor/csv/Premise.csv`）：

| 前提 | 含义 | 取数 |
| --- | --- | --- |
| `sex_class_reserved` / `sex_class_impromptu` | 进行中的实操课是预约的 / 当场开的 | `start_sex_class()` 复用了已有条目即 `reserved=True`，新建即 `False`；`set_temp_class()` 的数据里加了这个键（旧档缺键按当场处理） |
| `self_sex_class_must_attend` / `self_sex_class_elective` | 自己在 / 不在本节的必修名单 | 到场与旁观都是课 `running` 之后派发的二段行为，直接读 `get_running_class()["must_attend"]` |

**羞耻等级的阈值**：走既有 `CVP_A1_S|16_…` 状态数值 token，按 `Character_State_Level.csv` 的刻度取 低 `<1000`（≤2 级）/ 中 `1000~12000`（3~5 级）/ 高 `>12000`（6 级+），与既有口上惯用的 1000 / 12000 阈值一致。

⚠️ 权重：`handle_talk_sub` 里每条前提计 1 权重，所以带 2~3 个前提的分档文本在命中时会压过只带 1 个前提的通用文本，通用文本仍会以较低概率出现——这是既有口上系统的通行做法，没有另做处理。

## 7. 4-A / 4-B 的原步骤（已于 2026-09-07 实施，备查）

⚠️ 以下是 v3 时期拟的步骤，实际改动与偏离见 §6.6 / §6.7，以那两节为准。

### 7.1 4-A 妊娠期胎教

1. `game_type.py` 的 `PREGNANCY` 加 `prenatal_point`（方案 §4.1 的代码块即最终定义）
2. `save_handle.py:331~334` 的既有妊娠字段回填段并入本条，`hasattr` 回填为 `0.0`
3. `InstructConfig.csv` 加三条指令；`Behavior_Data.csv` 等三表加三个行为（各 30 分钟，玩家指令触发）
4. 常量三处同步；前提复用既有妊娠前提
5. `Script/Settle/default.py` 加结算：母亲 `pregnancy.prenatal_point += 0.5`，另加母子好感与亲密
6. 改 `pregnancy_handle.py` 的生产结算：转写到每个新生儿，⚠️ **多胎各自全额不平分**，⚠️ **转写后清零**，
   ⚠️ 转写为**全科目少量**初始经验而非单科大量（方案 §3.27）
7. 口上：`data/talk/daily/prenatal_talk.csv` / `_music` / `_touch` 各 10 条

### 7.2 4-B 婴儿期照料差异化

改 `Behavior_Effect.csv:109~114`，**在既有的 `1513 - 1514 - 21 - 22 - 71 - 53` 之后追加**各自的养成效果
（方案 §3.20 的表：抱小孩→坚强、哼唱儿歌→音乐、喂奶→亲密、换尿布→羞耻、教说话→语言、给玩具→创造）。

⚠️ **不动既有的 6 个通用效果**，只追加不替换（方案 §7-2）
⚠️ **不改保育员的等权重随机选择逻辑**（方案 §2.2）
⚠️ 口上 6 个文件各 10 条；`change_diapers.csv` **已有 9 条真实文本，保留并补齐差分前提，不推翻重写**（方案 §7-3），
改写前先备份该文件
