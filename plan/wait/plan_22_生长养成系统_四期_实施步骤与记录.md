# Plan 22（四期·实施步骤与记录）：妊娠期胎教 + 婴儿期照料差异化 + 性技实操课

> 本文件是 `plan_22_生长养成系统_四期_方案.md`（下文简称"方案"）的**实施步骤清单与过程记录**。
> 需求背景、现状调查、设计决策、风险与范围外事项以方案与
> `plan_22_生长养成系统_总纲.md`（下文简称"总纲"）为准；
> **角色字段定义以 `plan_22_生长养成系统_一期_方案.md` §4 为准**（下文简称"一期方案"）。
> 本文件只写"怎么做、怎么验、怎么回滚"，实施过程与结果记入 §6。

- 状态：未实施（与方案、总纲保持同步）
- 适用代码快照：`master @ 6aa5090e3`
- **前置**：一期必须先完成（`prenatal_point` / `care_point` / `personality_point` 由一期建立并回填）；与二期、三期相互独立
- 实施前提：先通读总纲 §2、一期方案 §4 与本方案；实施中发现与方案冲突的事实，**先更新方案再动代码**

---

## 1. 改动文件清单

### 1.1 配置与常量（8 个）

| 文件 | 类型 | 改动 |
| --- | --- | --- |
| `data/csv/InstructConfig.csv` | 改 | 三条胎教指令 + 性技实操课指令 |
| `data/csv/Behavior_Data.csv` | 改 | `prenatal_talk` / `prenatal_music` / `prenatal_touch`（各 30 分钟）+ `practice_sex_class` |
| `data/csv/Behavior_Effect.csv` | 改 | 四个新行为的效果串；**6 个照料行为（`:109~114`）各自追加养成效果** |
| `data/csv/Behavior_Introduce.csv` | 改 | 新行为的介绍文本 |
| `Script/Core/constant/Behavior.py` | 改 | 四个新行为的 en_name 常量 |
| `Script/Core/constant/BehaviorStr.py` | 改 | 同上 |
| `Script/Core/constant/Behavior_Int.py` | 改 | 四个新行为的 cid |
| `Script/Core/constant_effect.py` | 改 | 胎教累积、照料差异化、性技实操的效果 id |

### 1.2 代码（4 个）

| 文件 | 类型 | 改动 |
| --- | --- | --- |
| `Script/Core/game_type.py` | 改 | `PREGNANCY` 加 `prenatal_point`（方案 §4.1） |
| `Script/Core/save_handle.py:331~334` | 改 | `prenatal_point` 的 `hasattr` 回填为 `0.0`，并进既有妊娠字段的回填段 |
| `Script/Settle/default.py` | 改 | 胎教累积结算；6 个照料行为的差异化结算；性技实操课结算 |
| `Script/System/Pregnancy_System/pregnancy_handle.py` | 改 | 生产结算时把母亲的 `prenatal_point` 转写到每个孩子的 `child_growth.prenatal_point`（多胎各自全额），转写后清零 |

### 1.3 口上（10 个文件，约 110 条）

| 文件 | 类型 | 条数 | 差分 |
| --- | --- | --- | --- |
| `data/talk/daily/prenatal_talk.csv` | 新增 | 10 | 妊娠期 / 临盆期 2 档 × 5 |
| `data/talk/daily/prenatal_music.csv` | 新增 | 10 | 同上 |
| `data/talk/daily/prenatal_touch.csv` | 新增 | 10 | 同上 |
| `data/talk/daily/hold_child.csv` | 改写 | 10 | 婴儿在场的一般照料 / 玩家亲自 2 档 × 5 |
| `data/talk/daily/sing_children_song.csv` | 改写 | 10 | 同上 |
| `data/talk/daily/nuirse_child.csv` | 改写 | 10 | 同上 |
| `data/talk/daily/change_diapers.csv` | 改写 | 10 | ⚠️ **已有 9 条真实文本，保留并补齐差分前提，不推翻重写** |
| `data/talk/daily/teach_talk.csv` | 改写 | 10 | 同上 |
| `data/talk/daily/give_toy.csv` | 改写 | 10 | 同上 |
| `data/talk/sex/practice_sex_class.csv` | 新增 | 约 20~40 | 沿用既有 H 口上维度 |

### 1.4 ArkEditor 同步（2 个）

| 文件 | 改动 |
| --- | --- |
| `tools/ArkEditor/csv/Behavior_Data.csv` | 四个新行为同步 |
| `tools/ArkEditor/csv/Effect.csv` | 新增效果 id 同步 |

---

## 2. 详细改动步骤

> ⚠️ 全部 cid / 效果 id / 指令 cid **不在此预分配**，实施时现查空闲号。
> 数据结构定义以方案 §4.1 与一期方案 §4.1 为准。

### 2.1 母亲侧的胎教字段与存档

1. `game_type.py` 的 `PREGNANCY` 加 `prenatal_point`（方案 §4.1 的代码块即最终定义）
2. `save_handle.py:331~334` 的既有妊娠字段回填段并入本条，`hasattr` 回填为 `0.0`

### 2.2 三条胎教指令

1. `InstructConfig.csv` 加三条指令；`Behavior_Data.csv` 等三表加三个行为（各 30 分钟，玩家指令触发）
2. 常量三处同步
3. 前提：对象为怀孕状态的干员（复用既有妊娠前提）
4. `Script/Settle/default.py` 加结算：母亲 `pregnancy.prenatal_point += 0.5`，另加母子好感与亲密

### 2.3 出生时转写（⚠️ 两个易错点）

改 `Script/System/Pregnancy_System/pregnancy_handle.py` 的生产结算：

1. 把母亲的 `pregnancy.prenatal_point` 写到每个新生儿的 `child_growth.prenatal_point`
2. ⚠️ **多胎各自全额，不平分**（方案 §3.27）——平分会让多胎变成惩罚
3. ⚠️ **转写后清零**（方案 §7-7）——不清零则下一胎会继承上一胎的累积
4. 转写为全科目少量初始经验，**不是单科大量**（方案 §3.27）

### 2.4 6 个照料行为差异化

改 `Behavior_Effect.csv:109~114`，**在既有的 `1513 - 1514 - 21 - 22 - 71 - 53` 之后追加**各自的养成效果（方案 §3.20 的表）：

| cid | 行为 | 追加效果 |
| --- | --- | --- |
| 261 | 抱小孩 | `care_point` +0.3；性格倾向偏坚强 +0.5 |
| 262 | 哼唱儿歌 | 音乐(44) 初始经验 +8；性格偏热情 +0.5 |
| 263 | 喂奶 | `care_point` +0.3；母子好感额外加成 |
| 264 | 换尿布 | `care_point` +0.2；性格偏羞耻 +0.5 |
| 265 | 教说话 | 话术(40) +8；学识(45) +4 |
| 266 | 给玩具 | 绘画(49) +5；制造(48) +5；性格偏勤劳 +0.3 |

⚠️ **不动既有的 6 个通用效果**（方案 §7-2）：只追加，不替换。这样保育员的自动照料与既有存档中的行为都不受影响。

⚠️ **不改保育员的等权重随机选择逻辑**（方案 §2.2）：差异化效果对 NPC 同样生效，随机选也能让孩子均衡成长。

### 2.5 性技实操课

1. `InstructConfig.csv` + `Behavior_Data.csv` 加 `practice_sex_class`，时长视体位，玩家指令触发
2. ⚠️ **前提必须包含"对象是玩家女儿"且"已选修对应性技科目"**（方案 §7-5）——避免它成为绕过既有 H 前提的旁路入口
3. 结算走既有 H 链，另加对应性技能力（70~77）的经验，速度系数走一期方案 §3.1 的曲线
4. ⚠️ 只能玩家亲自进行（口径 38），不给 NPC 开这条路

### 2.6 口上

按 §1.3 的表生成。⚠️ 三点注意：

1. `change_diapers.csv` 已有 9 条真实文本，**保留并补齐差分前提，不推翻重写**
2. 孩子相关的口上带 `self_is_player_daughter` 前提，命中 `talk.py:185~188` 的女儿 5 倍加权（一期方案 §3.23）
3. 各 CSV 表头 5 行照抄同目录既有文件；改写既有文件时保持原 cid 不变，新增行 cid 顺延

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

- [ ] 胎教累积：连续做 10 次胎教，断言母亲 `pregnancy.prenatal_point == 5.0`
- [ ] **多胎各自全额**：母亲累积 5.0 且怀 3 胎，生产后断言三个孩子的 `prenatal_point` 各为 5.0（不是 1.67）
- [ ] **转写后清零**：生产后断言母亲的 `pregnancy.prenatal_point == 0.0`
- [ ] 转写为全科目少量：断言 18 门科目的经验都有微量增加，且无单科突出
- [ ] **6 个照料行为效果各不相同**：逐个执行后断言 `care_point` / 各科经验 / `personality_point` 的变化组合互不相同
- [ ] 既有通用效果未被破坏：执行任一照料行为后，体力气力与好感的变化与改动前一致
- [ ] 保育员随机照料：NPC 执行照料行为时差异化效果同样生效
- [ ] 性技实操课前提：对象不是玩家女儿、或未选修对应性技科目时，指令不可用
- [ ] 旧档载入：缺 `PREGNANCY.prenatal_point` 时 `hasattr` 回填为 `0.0`，不抛异常

### 4.2 游戏内整体测试（由用户执行）

- [ ] 对怀孕的干员可以做三种胎教，各有不同的文本
- [ ] 孩子出生后，养成总览的"初始资质"一栏能看到胎教带来的非零值
- [ ] 6 个照料婴儿行为的文本各不相同，且能看出各自的养成方向
- [ ] 换尿布的既有文本没有丢失
- [ ] 性技实操课可对已选修性技科目的女儿发起，走既有 H 流程
- [ ] Web 模式（`web_draw = 1`）下新指令表现一致
- [ ] 旧存档载入不报错，既有的照料婴儿流程未被破坏

---

## 5. 回滚

| 单元 | 回滚方式 | 备注 |
| --- | --- | --- |
| 胎教（指令 + 结算 + 转写） | revert `InstructConfig.csv` / 三个行为 / `pregnancy_handle.py` 的改动 | 已存档的 `prenatal_point` 留着不影响载入 |
| 存档字段 | revert `game_type.py` + `save_handle.py` | 旧档因 `hasattr` 回填天然兼容 |
| **照料行为差异化** | revert `Behavior_Effect.csv:109~114` 的追加部分 | ⚠️ 只 revert 追加的效果，**保留既有的 6 个通用效果**——它们本来就在那里 |
| 照料行为口上 | 恢复 6 个文件；⚠️ `change_diapers.csv` 的 9 条既有文本必须保住 | 建议改写前先备份该文件 |
| 性技实操课 | 删行为与指令 | 独立于其余改动 |

⚠️ 本期**没有不可回滚的部分**。唯一需要留神的是 `change_diapers.csv`——它是 6 个照料口上里**唯一有真实内容的**，改写前先备份。

---

## 6. 实施过程记录

（实施时填写）

### 6.1 实际改动

| 文件 | 类型 | 实际改动 |
| --- | --- | --- |
| | | |

**与方案的偏离**：

1. （逐条编号）

**已知限制**：

### 6.2 实施前的假设复核

| # | 假设 | 复核结果 |
| --- | --- | --- |
| 1 | 一期已建好 `CHILD_GROWTH.prenatal_point` / `care_point` / `personality_point` 并做了存档回填 | |
| 2 | `Behavior_Effect.csv:109~114` 六行的效果串完全相同（`1513 - 1514 - 21 - 22 - 71 - 53`） | |
| 3 | 6 个照料口上里只有 `change_diapers.csv` 有真实文本（9 条），其余 5 个是占位 | |
| 4 | 保育员的自动照料是在 6 个行为里等权重随机选 | |
| 5 | `save_handle.py:331~334` 已有一批 `pregnancy` 字段的回填可并入 | |
| 6 | 生产结算里有可插入胎教转写的位置 | |

### 6.3 单元测试结果

（断言计数与关键实测值）

### 6.4 尚未覆盖的验证

（留给用户的游戏内清单）

### 6.5 第二轮追加调整实施记录

（与方案 §9.x 成对，每轮一节，附回归测试计数）
