# Plan 22（一期·实施步骤与记录）：教育区改建 + 课表 + 六种课型 + 上课闭环

> 本文件是 `plan_22_生长养成系统_一期_方案.md`（下文简称"方案"）的**实施步骤清单与过程记录**。
> 需求背景、现状调查、设计决策、数据结构定义、界面设计、风险与范围外事项一律以方案与
> `plan_22_生长养成系统_总纲.md`（下文简称"总纲"）为准；本文件只写"怎么做、怎么验、怎么回滚"，
> 实施过程与结果记入 §6。

- 状态：**1a 功能闭环已完成**；§2.11 的 1b 口上已完成 **96 个文件 535 条**，17 个实习岗位的师徒两侧全部覆盖；缺失性技 8 门（见偏离 22），2026-09-06
- 适用代码快照：`master @ 6aa5090e3`
- 实施前提：先通读总纲 §2 与方案全文；实施中发现与方案冲突的事实，**先更新方案再动代码**
- ⚠️ **建议拆成两个提交推进**（总纲 §3）：
  - **1a 功能闭环**（§2.1~§2.10）—— 用既有占位文本跑通流程，完成即可进入二期
  - **1b 口上填充**（§2.11）—— 129 个文件、约 1950 条，用 AI 批量生成后穿插校对，不阻塞二期

---

## 1. 改动文件清单

### 1.1 地图（14 个文件，单独成一个提交）

| 文件 | 类型 | 改动 |
| --- | --- | --- |
| `tools/map_aa_build_education.py` | 新增 | AA 图生成脚本（⚠️ `Map` 不可手改，留白全为 U+2002） |
| `data/map/教/Map` | 改 | 由上述脚本生成；场景从 9 增至 18，全图 105U |
| `data/map/教/Map.json` | 改 | `PathEdge` 星型结构扩到 18 个节点 |
| `data/map/教/理论教室{一~六}/Scene.json` | 新增 6 | `SceneTag` 沿用 `Class_Room`（⚠️ 沿用是关键，见总纲 §2.4-A） |
| `data/map/教/实践教室{一~三}/Scene.json` | 新增 3 | `SceneTag` 新增 `Practice_Room` |
| `data/map/教/大礼堂/Scene.json` | 新增 1 | `SceneTag` 新增 `Auditorium` |
| `data/map/教/教室/Scene.json` | 删 | 被 6 间理论教室取代 |
| `data/map/教/{育儿室,办公室,活动室,游戏室,走廊}/Scene.json` | 保留 | 不动 |

### 1.2 CSV 配置（7 个）

| 文件 | 改动 |
| --- | --- |
| `data/csv/WorkType.csv:24~25` | 教师/学生行的 `place` 列「教室」→「教育区教室」（⚠️ 实测为纯显示文案，非功能依赖，见 §6.1 偏离 3） |
| `data/csv/Facility_open.csv` | 为 10 间教室各加一行，`zone_cid` 按方案 §3.11 的解锁阶梯填 |
| `data/csv/Entertainment.csv` | 加 `class_ok` 列（方案 §4.4），表头 5 行同步；16 项配 1，9 项配 0 |
| `data/csv/Behavior_Data.csv` | 新增 `self_study` / `skip_class` / `check_report_card` 三个一段行为 + `show_off_study` 一个二段行为 |
| `data/csv/Behavior_Effect.csv` | 上述四个行为的效果串；改造 213 `teach` 的效果语义 |
| `data/csv/Behavior_Introduce.csv` | 新增行为的介绍文本 |
| `data/csv/InstructConfig.csv` | 「检查成绩单」玩家指令 |

### 1.3 常量（7 个，⚠️ 编号不预分配，实施时现查空闲号）

| 文件 | 改动 |
| --- | --- |
| `Script/Core/constant/Behavior.py` | 新行为的 en_name 常量 |
| `Script/Core/constant/BehaviorStr.py` | 同上 |
| `Script/Core/constant/Behavior_Int.py` | 新行为的 cid |
| `Script/Core/constant/CharacterStatus.py` | 新状态 cid |
| `Script/Core/constant/StateMachine.py` | 新状态机 cid（自习、翘课） |
| `Script/Core/constant_promise.py` | `Course` 型 CVP token 的常量（方案 §3.17）、`Practice_Room` / `Auditorium` 场景前提 |
| `Script/Core/constant_effect.py` | 新增效果 id（自习结算、翘课结算、炫耀结算） |

### 1.4 既有代码改造（10 个）

| 文件 | 改动 |
| --- | --- |
| `Script/Core/game_type.py` | 新增 `CHILD_GROWTH` 类；`Character` 加 `child_growth`；`Rhodes_Island` 加 `class_schedule`（定义以方案 §4 为准） |
| `Script/Core/save_handle.py` | 两处 `hasattr` 回填（方案 §4.3） |
| `Script/Settle/default.py:7513 handle_teach_add_just` | 按课表格子的科目取教师对应能力、加对应经验、施加师生等级差速度曲线、区分理论/实践/礼堂基础值、乘教育区效率加成 |
| `Script/StateMachine/default.py:441` | 移动到教室：从 `random.choice(place_data["Class_Room"])` 改为按课表取指定教室，查不到则回落原逻辑 |
| `Script/StateMachine/default.py:2648 character_work_teach` | 教师授课：按课表取本节科目 |
| `Script/StateMachine/default.py:2680 character_attend_class` | 学生听课：按个人课表判断该去哪 |
| `Script/System/Instruct_System/handle_instruct.py:553~573` | ⚠️ **与上面两个状态机平行的实现，必须同步改**（方案 §2.2） |
| `Script/Design/handle_npc_ai.py` | 孩子的行为选择接入个人课表；体育/兴趣/实习课派往对应地点 |
| `Script/Design/game_time.py` | 新增节次判定函数（时间 → 节次编号 0~8） |
| `Script/UI/Panel/character_info_head.py:27` | `<课>` / `<翘>` 状态标识（方案 §3.22） |

### 1.5 前提（2 个）

| 文件 | 改动 |
| --- | --- |
| `Script/Design/handle_premise/__init__.py:302 handle_comprehensive_value_premise` | 新增 `Course` 分支，照既有 `Gift` 分支写（方案 §3.17） |
| `Script/Design/handle_premise/handle_premise_place.py` | `Practice_Room` / `Auditorium` 两个场景前提 |

### 1.6 新子系统 `Script/System/Education_System/`（8 个）

| 文件 | 内容 |
| --- | --- |
| `education_constant.py` | ⚠️ 实施时新增（§1.6 原表没有）：子系统常量统一定义文件，照 `Pregnancy_System/pregnancy_constant.py` 的成例。2026-09-08 第七轮把散在 13 个模块里的 114 个常量集中于此，见方案 §9.6 |
| `growth_handle.py` | 能力成长计算（速度曲线、教育区加成、上限判定） |
| `class_ai.py` | ⚠️ 实施时新增（§1.6 原表没有）：上课时段的行为决策——体力闸、翘课闸、按课型派状态机 |
| `auto_schedule.py` / `semester_handle.py` | ⚠️ 立项时**本期未建**：自动排课与学期切换推给二期，一期先把手动排课跑通（见偏离 21）。→ 均已于 2026-09-08 补上：`auto_schedule.py` 见第三轮与方案 §9.3，`semester_handle.py` 见第五轮与方案 §9.4 |
| `schedule_handle.py` | 课表读写、教师/学生视角反查、节次查询、冲突判定 |
| `auto_schedule.py` | 自动排课三种模式（补弱项 / 均衡 / 主修优先，口径 28） |
| `semester_handle.py` | 学期切换、成绩单生成（方案 §3.13） |
| `class_schedule_panel.py` | 全局课表面板（方案 §5.2） |
| `course_select_panel.py` | 个人课表面板（方案 §5.3） |
| `growth_panel.py` | 养成总览面板（方案 §5.4） |
| `教育与养成系统设计文档.md` | 子系统设计文档，照 `Script/System/*/` 各子系统的惯例 |

### 1.7 ArkEditor 同步（3 个）

| 文件 | 改动 |
| --- | --- |
| `tools/ArkEditor/csv/Premise.csv` | 新增前提同步（`tools/ArkEditor/load_csv.py:5` 读它，不同步则口上作者选不到） |
| `tools/ArkEditor/csv/Behavior_Data.csv` | 新增行为同步 |
| `tools/ArkEditor/csv/Effect.csv` | ⚠️ `:230` 的效果 512 描述已过时（写着"增加习得和学识经验"），改语义后同步 |

### 1.8 口上（129 个文件，约 1950 条 —— 1b 阶段）

| 目录 | 文件数 | 条数 | 说明 |
| --- | --- | --- | --- |
| `data/talk/work/teach/` | 18 | 540 | 一科一文件（方案 §3.18） |
| `data/talk/work/attent_class/` | 18 | 540 | 同上 |
| `data/talk/work/self_study/` | 18 | 180 | 同上 |
| `data/talk/system/second_show_off_study/` | 18 | 180 | 同上 |
| `data/talk/work/pe_class/` | 3 | 40 | 体育课（方案 §3.23） |
| `data/talk/play/interest_class/` | 16 | 160 | 兴趣课 |
| `data/talk/work/intern_class/` | 18 | 180 | 实习课·学生视角 |
| `data/talk/work/intern_mentor/` | 18 | 90 | 实习课·带教视角 |
| `data/talk/daily/check_report_card.csv` | 1 | 30 | 单文件 |
| `data/talk/work/skip_class.csv` | 1 | 10 | 单文件 |

⚠️ 既有的 `data/talk/work/teach.csv` 与 `attent_class.csv` 各只有 1 条占位文本，随本批覆盖（总纲 §2.1 记录的历史欠账）。

---

## 2. 详细改动步骤

> ⚠️ 全部 cid / 效果 id / 前提 id **不在此预分配**，实施时现查空闲号（方案 §7-7，plan_06 的教训）。
> 数据结构定义一律**以方案 §4 为准**，本文件不重复。

### 2.1 教育区改建（第一步，单独成一个提交）

1. 用 skill `draw-aa-map` 按方案 §3.10 的房间清单重排 `data/map/教/Map`
2. 新建 10 个房间的 `Scene.json`；⚠️ 6 间理论教室的 `SceneTag` **必须沿用 `Class_Room`**，否则 `place_data`、3 条既有前提、既有隐奸口上全部失效（总纲 §2.4-A）
3. 更新 `Map.json` 的 `PathEdge`
4. 改 `WorkType.csv:24~25` 的 `place` 列（纯显示，功能由 `place_tag` 承担）
5. 删除 `data/SceneData` / `data/MapData` / `data/PlaceData` / `data/ScenePath` 后跑 `init_data.py`
6. 跑 `tools/map_aa_check.py` 验证 AA 图对齐（⚠️ 不要靠数列数判断，字体的实际步进宽度决定版面）
7. **本步单独提交**，便于出问题时整体 revert

### 2.2 数据结构与存档

1. `game_type.py` 加 `CHILD_GROWTH` 类（方案 §4.1 的代码块即最终定义）
2. `Character.__init__` 加 `self.child_growth: CHILD_GROWTH = None`；⚠️ 只给持有素质 101~104 的角色实例化
3. `Rhodes_Island` 加 `class_schedule`（方案 §4.2）
4. `save_handle.py` 两处 `hasattr` 回填，照 `:331~334` 妊娠系列与 `:551` 的 `facility_level`

### 2.3 CSV 与常量

1. `Entertainment.csv` 加 `class_ok` 列（表头 5 行同步），按方案 §3.21 的表填值
2. `Facility_open.csv` 加 10 行教室解锁配置
3. `Behavior_Data.csv` / `Behavior_Effect.csv` / `Behavior_Introduce.csv` 加 4 个行为
4. `InstructConfig.csv` 加「检查成绩单」指令
5. 常量七处同步（§1.3）
6. 跑 `buildconfig.py` 重生成 `config_def.py`，确认 `Entertainment` 类带上 `class_ok`（总纲 §6-3）

### 2.4 节次与学期判定

1. `game_time.py` 加节次判定函数：时间 → 节次编号 0~8 或"无节次"
   - 节次表见方案 §3.2；⚠️ 边界值验证见 §4.1
2. 学期切换复用 `game_time.py:153 sub_time_now` 的切月判定，不新造时间周期（方案 §3.13）

### 2.5 新子系统骨架

按 §1.6 建 `Script/System/Education_System/` 八个文件。⚠️ **数据在 Core、逻辑在 System**，`Rhodes_Island` 不得在 Core 顶部 import System，需要时函数内延迟 import（方案 §7-10）。

先实现 `schedule_handle.py` 的读写与反查，其余模块依赖它。

### 2.6 授课结算改造

改 `Script/Settle/default.py:7513 handle_teach_add_just`：

1. 从课表取当前格子的科目能力 id，替代写死的 `ability[45]`
2. 按方案 §3.1 的速度曲线算 `speed`（`diff = 教师该科目等级 − 学生该科目等级`）
3. 按方案 §3.3 取基础值（理论 20 / 实践 35 / 礼堂 10 / 自习 10）
4. 乘教育区效率加成 `(1 + Facility_effect 的 effect / 100)`（方案 §3.12 —— 这是把已配置未实装的数值接上）
5. 能力升级时置 `show_off_ability` flag，不当场出文本（方案 §3.15 的延迟炫耀）
6. ⚠️ 保持既有干员学生链可用：`work_type == 152` 的成年干员走同一条结算

### 2.7 状态机与 AI 接课表

1. `StateMachine/default.py:441`：按课表取指定教室，查不到回落 `random.choice`
2. `:2648 character_work_teach`：按课表取本节科目
3. `:2680 character_attend_class`：按个人课表判断去向
4. `handle_instruct.py:553~573`：⚠️ **与 1~3 同步改**
5. `handle_npc_ai.py`：孩子的行为选择接入个人课表——教室课走上述链，体育/兴趣/实习课直接派往对应地点执行既有行为（方案 §3.21，零新增行为）

### 2.8 缺课与翘课

1. 上课节次开始时先判体力，低于阈值转 `rest` 并累加 `absent_count`（方案 §3.14）
2. 再判翘课：苦痛(17) + 恐怖(18) + 抑郁(19) + 反感(20) 的**等级**和，照 `Script/Design/instuct_judege.py:103~104` 的写法用 `attr_calculation.py:564 get_status_level`（方案 §3.19）
3. 达阈值按概率置 `skip_class_flag` 并走 `skip_class` 行为
4. 「翘课被抓」事件：孩子持 flag 且与玩家同场景时触发

### 2.9 新前提

1. `handle_premise/__init__.py:302` 加 `Course` 分支，照既有 `Gift` 分支（方案 §3.17）
   - ⚠️ 先确认当前课程科目放在 `behavior` 的哪个字段（总纲 §6-1，参照 `behavior.gift_id`，`game_type.py:1081`）
2. `handle_premise_place.py` 加 `Practice_Room` / `Auditorium` 两个场景前提
3. 同步 `tools/ArkEditor/csv/Premise.csv`

### 2.10 `<课>` 状态标识与面板

1. `character_info_head.py:27 get_character_status_list` 加一段，照 `:43~50` 的 `<跟>` 写法（方案 §3.22）
   - ⚠️ 一处改动同时覆盖 Tk 与 Web（`Web_Draw_System/status_panel.py:373` 复用同一函数并透传 tooltip），**不要写第二套**
2. 三个面板按方案 §5.2~§5.4 实现；只用 `Script/UI/Moudle/draw.py` 的抽象绘制类
3. 面板入口挂教育区办公室场景

### 2.11 口上填充（1b 阶段）

1. **先定稿前提写法**（§2.9 完成后）——否则 AI 生成的 premise 列不可用
2. 各 CSV 表头 5 行照抄同目录既有文件；cid 从 1000 起（`buildconfig.py:189~193` 自动加文件名前缀防跨文件冲突）
3. ⚠️ 孩子版口上**一律带 `self_is_player_daughter` 前提**——`Script/Design/talk.py:185~188 handle_special_talk_weight` 对女儿有默认 5 倍加权，这是孩子版稳定压过成人版的机制（方案 §3.23）
4. 用 skill `text-generation-for-instruction-code-generation` 按 §1.8 的目录分批生成，一次一个科目/岗位，人工校对
5. 跑 `buildpo.py` + `buildmo.py`

---

## 3. 构建与缓存

```bash
# 本机必须用 conda 解释器（裸 python 是 Store 空壳别名）
.conda\python.exe buildconfig.py   # CSV / 常量改动后全量重建

# 地图改动后：先删缓存再跑
del /S /Q data\SceneData data\MapData data\PlaceData data\ScenePath
.conda\python.exe init_data.py

.conda\python.exe buildpo.py       # 口上与 _() 文本
.conda\python.exe buildmo.py

.conda\python.exe tools\map_aa_check.py   # AA 图对齐验证，非零退出即失败
```

本期涉及 CSV、常量、地图三类改动，**三条链都必须跑**。

---

## 4. 验证清单

### 4.1 单元测试（实施方执行，按 `headless-game-test` 模式 A）

- [ ] 速度系数曲线：`diff` 取 +8 / +4 / +1 / 0 / −1 / −2 / −8 七点，断言系数为 3.00 / 2.00 / 1.25 / 1.00 / 0.67 / 0.50 / 0.20
- [ ] 自习（无教师）速度系数恒为 1.0，且不参与等级差计算
- [ ] 教育区效率加成：Lv1 / Lv3 / Lv5 三点，断言最终经验为基础值的 1.0 / 1.2 / 2.0 倍
- [ ] 经验累积跨越 8 级阈值（20000）后等级不再上升（EX 封顶，`attr_calculation.py:559`）
- [ ] 节次判定边界：9:00 / 11:15 / 12:00 / 14:00 / 17:00 / 17:45 / 19:00 分别落在哪个节次或"无节次"
- [ ] 翘课阈值：四个负面状态等级和取 3 / 4 / 11 / 12 / 16 五点，断言概率档为 0% / 10% / 25% / 45% / 70%
- [ ] 体力优先于翘课：体力不足且负面状态高时，走 `rest` 而非 `skip_class`，且不置 `skip_class_flag`
- [ ] 实习课无人在岗时降级为见习：经验减半且不施加等级上限
- [ ] 周日的实习课格子在面板判定中不可选
- [ ] 兴趣课候选表只含 `class_ok == 1` 的 16 项；品酒不在其中（由既有 `T7|0` 前提排除，非新逻辑）
- [ ] 课表冲突判定：同教师同节次排两间教室、同学生同节次选两间教室，均被拒
- [ ] 旧档载入：缺 `child_growth` / `class_schedule` 时的 `hasattr` 回填不抛异常，且普通干员不被建 `child_growth`
- [ ] `<课>` 标识：学生上课中 / 教师授课中 / 自习中 / 翘课中四种输入，断言返回的文本与 tooltip

### 4.2 游戏内整体测试（由用户执行）

- [ ] 地图改建后教育区可正常通行，15 个房间都能进出，未解锁的教室给出"解锁需要将教育区升到 N 级"的提示
- [ ] 教师岗干员会按课表走班：第 1 节在 A 教室、第 2 节在 B 教室、第 3 节空闲
- [ ] 孩子按个人课表走班，未排课的节次自由行动
- [ ] 上课后能力当场增长，等级变化有提示
- [ ] 能力升级后不当场出文本；等孩子与玩家同场景时触发「炫耀」二段行为
- [ ] 把孩子排去木桩房上体育课、棋牌室上兴趣课、厨房上实习课，三者都能正常执行
- [x] 学期末出成绩单 flag，用「检查成绩单」指令能查看（2026-09-08 第五轮，方案 §9.4）
- [ ] 角色状态栏能看到 `<课>`，悬停显示当前课程；翘课时显示红色 `<翘>`
- [ ] Web 模式（`web_draw = 1`）下三个面板与 `<课>` 标识表现一致
- [ ] 旧存档载入不报错，既有的教师/学生干员行为未被破坏

---

## 5. 回滚

按可独立回滚的单元分组：

| 单元 | 回滚方式 | 备注 |
| --- | --- | --- |
| **地图改建** | revert 该单独提交 + 删场景缓存重跑 `init_data.py` | ⚠️ **唯一不可轻易回滚的部分**：存档中角色的 `position` 可能指向新房间，回滚后需把位于已删房间的角色回落到走廊。这正是要求它单独成一个提交的原因 |
| 数据结构与存档 | revert；旧档因 `hasattr` 回填天然兼容 | 新档存过 `child_growth` 后回滚，该字段会被忽略，不影响载入 |
| 授课结算改造 | revert `Settle/default.py` 的改动 | 回到写死学识的旧行为 |
| 状态机与 AI | revert；`random.choice` 回落逻辑本就保留 | 低风险 |
| 新子系统与面板 | 整个目录删除 + 摘掉入口 | 无外部依赖 |
| `<课>` 标识 | revert `character_info_head.py` 一处 | 无副作用 |
| 口上（1b） | 删除新增的 129 个文件重跑 `buildconfig.py` | 既有占位文本会重新生效 |

---

## 6. 实施过程记录

（实施时填写）

### 6.1 实际改动

#### 步骤 §2.1 教育区改建（2026-09-06）

| 文件 | 类型 | 实际改动 |
| --- | --- | --- |
| `tools/map_aa_build_education.py` | 新增 | AA 图生成脚本，照 `map_aa_build_training.py` 的 U 单位模型写；全图 105U，上排 8 格 + 走廊 + 下排 8 格，每格 12U |
| `data/map/教/Map` | 改 | 由上述脚本生成（⚠️ 留白全为 U+2002，**不可手改**） |
| `data/map/教/Map.json` | 改 | `PathEdge` 从 9 节点扩到 18 节点，星型结构，16 间房全部直通走廊 |
| `data/map/教/理论教室{一~六}/Scene.json` | 新增 6 | `SceneTag` 沿用 `Class_Room`，`Scene_Img` 沿用「教室」 |
| `data/map/教/实践教室{一~三}/Scene.json` | 新增 3 | `SceneTag` 新增 `Practice_Room` |
| `data/map/教/大礼堂/Scene.json` | 新增 1 | `SceneTag` 新增 `Auditorium`，`Room_Area` 取 2，`Scene_Img` 取「会议室」 |
| `data/map/教/教室/Scene.json` | 删除 | 被 6 间理论教室取代 |
| `data/csv/WorkType.csv:24~25` | 改 | 教师 / 学生的 `place` 列「教室」→「教育区教室」（纯显示，见偏离 3） |
| `update.log` | 改 | 登记「新增：（地图）教育区改建…」 |

#### 步骤 §2.2 数据结构与存档（2026-09-06）

| 文件 | 类型 | 实际改动 |
| --- | --- | --- |
| `Script/Core/game_type.py` | 改 | 新增 `CHILD_GROWTH` 类（13 个字段，含二/三/四期只建不写的 6 个）；`Character` 加 `child_growth`（`Optional`，默认 `None`）；`Rhodes_Island` 加 `class_schedule` 与 `child_schedule_template` |
| `Script/Core/save_handle.py` | 改 | 角色循环里补 `child_growth` 属性位；罗德岛段补两个字典的 `hasattr` 回填 |

#### 步骤 §2.4 节次与学期判定（2026-09-06）

| 文件 | 类型 | 实际改动 |
| --- | --- | --- |
| `Script/Design/game_time.py` | 改 | 新增 `CLASS_PERIOD_START` / `CLASS_PERIOD_MINUTE` 常量与 `get_class_period_by_time()` / `get_class_period()` / `get_now_semester()` 三个函数，接在 `judge_entertainment_time` 之后 |

#### 步骤 §2.5 新子系统骨架（2026-09-06）

| 文件 | 类型 | 实际改动 |
| --- | --- | --- |
| `Script/System/Education_System/__init__.py` | 新增 | 空包标记，照其余子系统的惯例 |
| `Script/System/Education_System/schedule_handle.py` | 新增 | 课表读写、教师视角反查、教室列表、冲突判定、`get_now_course()` / `get_now_teaching()` 统一入口；六种课型常量 |
| `Script/System/Education_System/growth_handle.py` | 新增 | `get_child_growth()` 惰性创建、速度曲线、教育区加成、学生/教师侧的一节课结算 |

#### 步骤 §2.6 授课结算改造（2026-09-06）

| 文件 | 类型 | 实际改动 |
| --- | --- | --- |
| `Script/Settle/default.py:7513 handle_teach_add_just` | 改 | 科目从写死的 `ability[45]` 改为教师视角查全局课表；学生侧改调 `growth_handle.settle_student_class_gain`（带师生等级差与教育区加成），教师侧改调 `settle_teacher_class_gain`（加当节所授科目而非固定学识）；查不到课表时回落学识，既有干员学生链不受影响 |

#### 步骤 §2.7 状态机接课表（2026-09-06）

| 文件 | 类型 | 实际改动 |
| --- | --- | --- |
| `Script/StateMachine/default.py:433 character_move_to_class_room` | 改 | 目标教室改为由课表决定（教师查授课表、学生查个人课表），查不到则回落既有的随机选一间理论教室 |

#### 步骤 §2.3 CSV 部分（2026-09-06，行为与常量待做）

| 文件 | 类型 | 实际改动 |
| --- | --- | --- |
| `data/csv/Facility_open.csv` | 改 | 加 7 行教室解锁：理论教室二/三→Lv2(152)、理论教室四+实践教室二→Lv3(153)、理论教室五+实践教室三→Lv4(154)、理论教室六→Lv5(155)。⚠️ 理论教室一 / 实践教室一 / 大礼堂 **不进本表**——不在表里即默认开放，正是 Lv1 就要有的三间 |
| `data/csv/Entertainment.csv` | 改 | 新增 `class_ok` 列（表头 5 行同步）。16 项配 1，9 项配 0（8 项消费服务类 + 游泳改归体育课）；品酒不需要配，既有 `T7\|0` 前提已挡住未成年 |
| `data/csv/Facility_effect.csv:97~101` | 改 | 教育区五级的 `info` 文案随改建更新（原 Lv1 写「开放基础设施:【教室】」，那间教室已不存在） |

⚠️ **编号取值说明**：`Facility_open.csv` 的 06x 本是教育区块，但 069/070 已被疗养庭院的房间占用（既有编号不一致），只剩 063~068 六个空号，第七行取同样空闲的 060。cid 只作字典键，无语义约束，但仍记在此处备查。

#### 步骤 §2.3 行为与常量（2026-09-06）

新增 3 个一段行为 + 1 个二段行为。⚠️ 编号均为实施时现查的空号，未预分配：

| cid | en_name | 名称 | 时长 | 触发 | tag | 取号理由 |
| --- | --- | --- | --- | --- | --- | --- |
| 211 | `self_study` | 自习 | 45 | npc | 工作 | 紧邻 213 `teach` / 214 `attent_class`，同属教育链 |
| 212 | `skip_class` | 翘课 | 45 | npc | 工作 | 同上 |
| 229 | `check_report_card` | 检查成绩单 | 15 | both | 日常 | 工作段末尾之后的空档 |
| 1328 | `show_off_study` | 向博士炫耀最近学到的东西 | 0 | npc | 二段结算 | 二段行为段 1327 之后的第一个空号 |

新增 4 个效果 id（548~551 为现查空号）：

| id | 常量 | 作用 |
| --- | --- | --- |
| 548 | `SELF_STUDY_ADD_ADJUST` | 按自习基础值加习得与所选科目经验，速度系数恒取 1.0 |
| 549 | `SKIP_CLASS_ADD_ADJUST` | 置翘课 flag、抑郁小幅回落，**不给任何学习收益** |
| 550 | `CHECK_REPORT_CARD_ADD_ADJUST` | 输出成绩单（各科等级 + 出勤率），按出勤率加好感与心情，清 flag |
| 551 | `SHOW_OFF_STUDY_ADD_ADJUST` | 二段结算：加好感与亲密，清空待炫耀记录 |

| 文件 | 类型 | 实际改动 |
| --- | --- | --- |
| `data/csv/Behavior_Data.csv` | 改 | 加 4 行 |
| `data/csv/Behavior_Effect.csv` | 改 | 加 4 行效果串（`self_study` 复用既有 1511/1512 扣体力气力） |
| `data/csv/Behavior_Introduce.csv` | 改 | 加 3 行介绍文本（二段行为不需要） |
| `Script/Core/constant/Behavior.py` / `BehaviorStr.py` / `Behavior_Int.py` / `CharacterStatus.py` | 改 | 常量四处同步 |
| `Script/Core/constant_effect.py` | 改 | 4 个效果 id 常量 |
| `Script/Settle/default.py` | 改 | 4 个结算函数实现，接在 `handle_teach_add_just` 之后 |
| `tools/ArkEditor/csv/Behavior_Data.csv` | 改 | 4 行同步 |

#### 步骤 §2.10 `<课>` 状态标识（2026-09-06，面板部分待做）

| 文件 | 类型 | 实际改动 |
| --- | --- | --- |
| `Script/UI/Panel/character_info_head.py` | 改 | 新增 `get_now_class_tip()` 与 `get_course_text()` 两个函数；在 `get_character_status_list()` 的 `<跟>` 之后插入 `<课>` / `<翘>` 一段 |

**与方案的偏离**：

0. ⚠️ **【重大】能力成长机制与方案 §3.1 的原假设不符，已推翻重写。** 方案原文写"上课当场调 `base_chara_experience_common_settle` 给对应能力的经验，等级由既有 `get_experience_level_weight` 自动换算"——实测发现：`Character.ability` 存的是**等级**不是经验，全项目没有能力经验字段；`get_experience_level_weight`（`attr_calculation.py:504`）**全仓库零调用方，是死代码**。真实链条是「习得状态 → 睡眠转珠 → 按 `AbilityUp.csv` 的珠+经验需求升级」。已改为完全复用该链，方案 §3.1 与 §3.9 已按实测重写，总纲 §2.3 补为第 11 条硬约束。
   - 连带影响一：**升级在当晚睡眠结算兑现，不是当场**，与已确认口径 7 的"当场换算等级"有出入（理由见方案 §3.1）。
   - 连带影响二：§3.9 的全部算例作废重算。新结论：学识 0→8 需习得珠 49,470 + 学识经验 1,145，约 659 节课，与"上课期约 720 节"的预算刚好吻合。
   - 意外收获：性技科目的升级需求本就是真实性交经验（膣技要 `E61`），课堂给不了——理论课攒珠、实操课攒经验天然成立，**零特判就落实了已确认口径 5**。
1. **房间名用汉字数字（理论教室一~六），而非方案原写的阿拉伯数字（理论教室1~6）。** 原因：ASCII 数字属 ASCII 度量族（字号 20 下 14px），与框线族（13px）不通约，每间教室的按钮都会让所在行漂移 1px，6 间累计 6px，`tools/map_aa_check.py` 会判失败。汉字数字恒为 2U，零漂移。方案 §3.10 已同步更新。
2. **场景数是 18 而非方案预估的 15。** 方案的「9 增至 15」只数了功能房间，实际目录含入口 `0`、走廊与男女洗手间。不影响任何设计。
3. **`WorkType.csv` 的 `place` 列不是功能性依赖，只是显示文案。** 方案 §7-1 原写「唯一必改」，实测为「唯一需要同步的显示文案」——`handle_npc_ai.py:359` 是 `place`(按场景名) **或** `place_tag`(按标签) 的短路判断，标签命中即成立；移动到工作地点走 `auto_ai_move`(561) → `StateMachine/default.py:441` 的 `place_data["Class_Room"]`，与 `place` 无关。`place` 的实际读取点只有 `debug_panel.py:2089` 与 `manage_basement_panel.py:1230` 两处显示。方案 §7-1 与总纲 §2.4 已同步更新。
4. **大礼堂的 `Scene_Img` 取「会议室」**：`image/场景/` 下没有礼堂图，会议室是最接近的现成资源。
5. **`<课>` 的提示文案对个人式课型单独分支**（测试驱动修出来的）：体育 / 兴趣 / 实习课本就没有指派教师（`teacher_id` 恒为 −1），初版代码把它们一律套进"本节无教师，降级自习"的文案，显示成「自习·兴趣课·下棋」。已改为只对班级式教室课判自习。
6. **`Facility_effect.csv` 的教育区文案顺带修正**：Lv1 原写「开放基础设施:【教室】」，改建后那间教室已不存在；五级文案全部按新的解锁阶梯重写。

8. **`tools/ArkEditor/csv/Behavior_Data.csv` 是落后的旧快照**：它缺主表里的 227 / 228 两行（整理宿舍意见、处理宿舍问题），锚点对不上，本次只好换用 226 作锚。这是既有的同步欠账，不影响本期，但下次谁动 ArkEditor 的 CSV 时要留意两边已经不是一份东西了。
7. **顺手修好了育儿室的文案与实现不符**（用户拍板）：`Facility_effect.csv:153` 原写教育区 Lv3「开放新设施:【育儿室】」，但 `Facility_open.csv` 里**从来没有育儿室这一行**——即育儿室实际一直是开放的。两条路：给它补一行 Lv3 门禁（会把玩家当前存档里已开放的房间重新上锁），或把文案改成"初期就开放"。按用户决定取后者：Lv1 文案列入【育儿室】，Lv3 文案不再提它。**实现不动，只改文案**，既有存档零影响。

**已知限制**：

- ⚠️ **老存档读出来仍是旧地图**。`save_handle.py:496~516` 只在场景增删或 `scene_tag`/`scene_img`/`room_area` 变化时才刷新存档里的 `map_data`——本次确实是场景增删，理论上会刷新，但**必须用老存档实机验证**（列在 §4.2）。
- 未解锁教室的门禁（`Facility_open.csv`）尚未配置，属步骤 §2.3，本步未做——当前 10 间教室全部可进入。

#### 步骤 §2.8 缺课与翘课（2026-09-06）

一节课开始时要过两道闸再决定去干什么，顺序不可调换——**体力不足是"去不了"，心情糟糕是"不想去"**，一个孩子累到爬不起来时不该再被算一次叛逆：

| 闸 | 判据 | 不过闸的结果 | 依据 |
| --- | --- | --- | --- |
| 体力 | `hit_point / hit_point_max < 0.3` | 走 `REST`(43) 状态机，累加一节缺课，**不置翘课flag** | 阈值取既有前提 `handle_premise_base_value.py:46 handle_hp_low` 的「体力低」口径，不另立一套 |
| 心情 | 苦痛17+恐怖18+抑郁19+反感20 的**等级**和 | 按阶梯概率走 `EDUCATION_SKIP_CLASS`(714) | 等级和写法照 `Script/Design/instuct_judege.py:103~104`，用 `attr_calculation.py:564 get_status_level` |

过闸后按课型派发（班级式）：不在教室 → `MOVE_TO_CLASS_ROOM`(561)；在教室且教师可用 → `WORK_ATTENT_CLASS`(304)；教师缺席 → `EDUCATION_SELF_STUDY`(713)。

| 文件 | 类型 | 实际改动 |
| --- | --- | --- |
| `Script/System/Education_System/class_ai.py` | 新增 | 两道闸 + 派课的决策总入口 `judge_class_state_machine()`，返回状态机id，0 表示不接管 |
| `Script/Core/constant/StateMachine.py` | 改 | `EDUCATION_SELF_STUDY = 713` / `EDUCATION_SKIP_CLASS = 714`（现查空号，701~712 已占、751 起是道具开关段） |
| `Script/StateMachine/default.py` | 改 | 两个状态机实现，接在既有上学状态机之后。⚠️ 翘课是**两步**：人还在教室就先溜回宿舍，离开教室之后才开始摸鱼——"该在教室的人不在教室"正是翘课的可见表现 |
| `Script/Design/handle_npc_ai.py:351` | 改 | 课表决策接在**工作分支之前**。排在工作前是必须的：孩子的"工作"就是上学，落到工作链只会随机挑一间教室（`StateMachine/default.py:460` 的 `random.choice`），课表就白排了 |
| `Script/Core/game_type.py` | 改 | `CHILD_GROWTH` 加 `last_absent_period`（方案 §4.1 已同步） |
| `Script/Settle/past_day_settle.py:62` | 改 | 次日零点无条件清翘课flag，紧邻既有的香薰flag清零 |
| `Script/Design/handle_ability.py:119` | 改 | 孩子能力升级时记一笔待炫耀——升级发生在玩家睡觉的睡眠结算里，当场没有观众，攒着等下次见面（方案 §3.15） |
| `Script/Design/second_behavior.py` | 改 | 新增 `judge_child_growth_second_behavior()`，接在 `judge_character_first_meet()` 之后；同场景时触发炫耀或翘课被抓，**翘课被抓优先**（正翘着课的孩子不会先炫耀成绩） |
| `Script/Settle/Second_effect.py` | 改 | 两个二段结算：`handle_show_off_study`（622）、`handle_caught_skip_class`（623） |
| `Script/Core/constant_effect.py` | 改 | `SecondEffect` 加 622/623；`BehaviorEffect` **删掉** 551（见偏离 9） |
| `Script/Core/constant/SecondBehavior.py` / `SecondBehavior_Int.py` | 改 | 两个二段行为常量 |
| `data/csv/Behavior_Data.csv` / `Behavior_Effect.csv` | 改 | 新增 `1329,caught_skip_class`；`1328` 的效果由 551 改为 622 |
| `tools/ArkEditor/csv/Behavior_Data.csv` | 改 | 1329 同步 |
| `Script/UI/Panel/character_info_head.py` | 改 | `<课>` 把 `self_study` 行为一并纳入（此前只认 `teach` / `attent_class`，自习时标识会消失） |

**「翘课被抓」的实际后果**：不只出一段文本——`caught_skip_class` 的结算会**当场清掉 flag**，当日剩余节次得回教室，另加抑郁与恐怖（数值取一节课量级，与翘课本身给的抑郁回落大致相抵）。

#### 实施中发现的偏离（§2.8）

9. **⚠️ 上一步埋的 BUG：`show_off_study` 的结算注册错了命名空间。** 二段行为的效果走 `constant.settle_second_behavior_effect_data`（`settle_behavior.py:504 add_settle_second_behavior_effect`），用的是 `constant_effect.SecondEffect` 这套**独立的编号空间**，函数签名也只有 `(character_id, change_data)` 两个参数。而 §2.3 里我把 `handle_show_off_study_add_just` 写成了一段行为的样子：`add_settle_behavior_effect` + `BehaviorEffect.SHOW_OFF_STUDY_ADD_ADJUST = 551` + 四参数签名，放在 `Script/Settle/default.py` 里。这样注册出来的函数**永远不会被二段结算找到**，运行时会打印"没有找到对应的结算效果"然后跳过。本步已改正：函数移到 `Script/Settle/Second_effect.py`、改用 `add_settle_second_behavior_effect`、编号改为 `SecondEffect.SHOW_OFF_STUDY = 622`（接在既有最大号 621 之后），`Behavior_Effect.csv` 的 1328 行同步改指 622。
   §2.3 的验证之所以没抓到，是因为当时只断言了"效果串是 `[551]`"，没有断言"551 在哪个注册表里"。本步的测试补上了这一条。
10. **`CHILD_GROWTH` 加了一个方案里没有的字段 `last_absent_period`。** 起因是缺课计数不幂等：休息行为 30 分钟、一节课 45 分钟，同一节课里 AI 会两次走到缺课分支，`absent_count` 会多加一次，成绩单的出勤率直接失真。用 `[日期序数, 节次]` 做去重标记最省事，也天然可存档（都是 int）。**已先改方案 §4.1 再改代码**，符合本文件开头的实施前提。
11. **`§2.7-5 个人课型（体育/兴趣/实习）的派发暂未接线**，`class_ai.judge_class_state_machine()` 对这三种课型返回 0 交回既有 AI。原因是它们的落地方式还有一处需要定夺：体育课复用 `training` / `exercise` / `swimming` 三个既有行为、效果照走既有 `Behavior_Effect` 配置（方案 §3.21 的"零新增结算公式"成立）；但**实习课不成立**——导师是"该岗位当时的在岗干员"，他执行的是自己的工作行为，身上没有任何把经验给学徒的效果，学徒侧必须另有一次结算才能拿到方案 §3.21 承诺的"按师徒等级差学该岗位 `ability_id`"。这与"零新增结算"直接冲突，需要单独处理，不适合顺手带过。
12. **`Script.Settle` 一旦被 import，进程就不会自己退出。** 它会起一个非守护线程 `init_instruct_handle_thread`，无头测试末尾必须用 `os._exit()`（且先 `sys.stdout.flush()`，`os._exit` 不刷缓冲）。这与总纲记过的"配置初始化前 import 会挂住"是同一个线程，但表现不同：配置就绪后 import 不再报错，只是不肯退出。

#### 步骤 §2.7-5 个人式课型（体育 / 兴趣 / 实习）（2026-09-06）

三种课型统一是"人到地点，执行该地点既有的行为"。地点解析收敛到一个入口 `schedule_handle.get_course_place()`，
六种课型（含班级式）共用它，AI、状态机与 `<课>` 提示三处都不再各自算一遍：

| 课型 | 目标存的是什么 | 地点怎么解析 | 执行什么行为 |
| --- | --- | --- | --- |
| 3 体育课 | 训练场的场景名 str | `PE_PLACE_DATA` 固定表（4 处）取标签，再在同标签的房间里**精确匹配场景名** | `training` / `exercise` / `swimming` |
| 4 兴趣课 | `Entertainment.csv` 的 cid int | 直接读该行的 `place_tag` | 直接读该行的 `behavior_id`（存的是 cid，需反查 en_name） |
| 5 实习课 | `WorkType.csv` 的 cid int | 直接读该岗位的 `place_tag` | 新增的 `intern_class` |

体育课必须精确匹配场景名，因为木桩房与射击房同挂 `Training_Room`，只按标签取会随机去错地方；
兴趣课与实习课同标签的房间彼此等价（厨房只有一间），取第一间即可。

| 文件 | 类型 | 实际改动 |
| --- | --- | --- |
| `data/csv/Behavior_Data.csv` | 改 | 新增 `230,intern_class,实习,45,npc,工作`（230 紧接 229，仍在工作段） |
| `data/csv/Behavior_Effect.csv` | 改 | `230,intern_class,1511 - 1512 - 552`，前两个是与听课同档的体力气力消耗 |
| `data/csv/Behavior_Introduce.csv` | 改 | 1 行介绍 |
| `Script/Core/constant/{Behavior,BehaviorStr,Behavior_Int,CharacterStatus}.py` | 改 | `INTERN_CLASS` 四处同步 |
| `Script/Core/constant_effect.py` | 改 | `INTERN_CLASS_ADD_ADJUST = 552`。⚠️ **551 空着不复用**——它刚随 `show_off_study` 迁到 `SecondEffect` 命名空间，留空以免与历史记录混淆 |
| `Script/Core/constant/StateMachine.py` | 改 | `EDUCATION_MOVE_TO_COURSE_PLACE = 715` / `EDUCATION_DO_COURSE = 716` |
| `Script/StateMachine/default.py` | 改 | 两个状态机。⚠️ **时长一律截到 45 分钟**：战斗训练本是 120 分钟、锻炼与游泳 60 分钟，照原时长一节体育课会吃掉整个上午；既有结算按 `add_time` 线性计算，截断天然成立 |
| `Script/System/Education_System/schedule_handle.py` | 改 | 加 `PE_PLACE_DATA`、`get_course_place()`、`get_intern_mentor()`、`get_behavior_name_by_cid()` |
| `Script/System/Education_System/growth_handle.py` | 改 | 基础值表加课型 5（习得 40 / 经验 4，介于理论 30 与实践 50 之间）；无教师降级改为**分课型**：教室课掉到自习档，实习课只把本岗位基础值减半 |
| `Script/System/Education_System/class_ai.py` | 改 | 个人式课型的派发（此前返回 0 的死分支） |
| `Script/Settle/default.py` | 改 | `handle_intern_class_add_just`（552） |
| `Script/UI/Panel/character_info_head.py` | 改 | `<课>` 覆盖个人式课型；实习课的提示补一句带教是谁 |
| `tools/ArkEditor/csv/Behavior_Data.csv` | 改 | 230 同步 |

**为什么 `<课>` 对个人式课型只能靠"地点 + 课表"判定**：这三种课执行的是既有行为（打木桩、下棋、跟岗），
没有一个专属的"上课中"行为可认。所以判据改成"本节排了这门课 **且** 人确实在那个地点"——
孩子被叫走跟随、或自己跑去别处玩时，标识会自动消失，与 §3.22 的"描述此刻的状态"口径一致。

#### 实施中发现的偏离（§2.7-5）

13. **方案 §3.21 的"后三种课型零新增行为、零新增结算公式"对实习课不成立，已先改方案再动代码。** 体育课与兴趣课成立——孩子执行的是 `training` / `swimming` / 各娱乐行为，这些行为**自带**效果串，到点就结算，学生侧什么都不用加。实习课不成立：导师是"该岗位当时的在岗干员"，**他执行的是自己的工作行为**，那串效果是给他自己发工作产出的，里面没有任何"把经验分给身边学徒"的部分——对比理论课，教师的 `teach` 行为里有 512 效果专门结算全场学生。学徒站在厨房里什么也不会发生。于是新增 1 个行为 `intern_class` + 1 个结算 552。不复用 `attent_class` 是因为状态栏要显示「实习」而不是「上学」，口上也要按 `behavior_id` 分流。
14. **虚惊一场：`data/talk/` 的目录名不构成对行为的约束。** §1.8 里列了 `pe_class/` / `interest_class/` / `intern_class/` 三个口上目录，看上去像是要求三个同名行为。实测 `buildconfig.py:509~520` 对 `data/talk/` 是**递归遍历**，每行口上的归属由 CSV 里的 `behavior_id` **列**决定，目录与文件名纯粹是组织手段（`data/talk/work/teach.csv` 里每行也都写着 `behavior_id`）。所以前两个目录装的是 `training` / 各娱乐行为的口上，靠 §3.17 的 `Course` 前提区分"这是在上课"还是"自己在玩"，只有 `intern_class/` 恰好与新行为同名。方案 §3.21 已补记这一条。
15. **`Entertainment.csv` 的 `behavior_id` 列此前从未被代码读取过。** 全仓库 grep 只有 `.name` / `.place_tag` / `.auto_ai_*` 被用到——娱乐行为一直是靠 `auto_ai_entertainment` 状态机或目标搜索驱动的。本次是第一次读它，读出来是**行为 cid**，而角色身上的 `behavior.behavior_id` 存的是 **en_name 字符串**，两者之间需要一层反查（`config_behavior` 只有 en_name → 数据的正向索引）。加了 `get_behavior_name_by_cid()` 带惰性缓存。
16. **`growth_handle` 里另写了一份 `CLASSROOM_COURSE_TYPE_SET`。** `schedule_handle` 已经在函数内反向 import 了 `growth_handle`，模块级互相 import 会成环，所以这三个数字在两处各写一份并互相注明。

#### 步骤 §2.9 新前提（2026-09-06）

| 文件 | 类型 | 实际改动 |
| --- | --- | --- |
| `Script/Design/handle_premise/__init__.py` | 改 | CVP token 的值类型加 `C` 开头的分支，覆盖 `Course` 与 `CourseType` 两个 token；另加 `get_now_course_ability()` / `get_now_course_type()` 两个取值函数 |
| `Script/Core/constant_promise.py` | 改 | `IN_PRACTICE_ROOM` / `NOT_IN_PRACTICE_ROOM` / `IN_AUDITORIUM` / `NOT_IN_AUDITORIUM` |
| `Script/Design/handle_premise/handle_premise_place.py` | 改 | 上述四条的实现，照同文件 `:3657 handle_in_class_room` 的写法 |
| `tools/ArkEditor/csv/Premise.csv` | 改 | 4 行同步（`tools/ArkEditor/load_csv.py:5` 读它，不同步则口上作者在编辑器里选不到） |

**两个 token 都不新增字段。** 方案原先设想"把当前科目写进 `behavior` 的某个字段，参照 `behavior.gift_id`"，
实施时弃选：课表本身就是唯一真相源，现算即可；多存一份反而要在开课、换课、教师缺席、翘课几处同步维护，
早晚会与课表打架。取值函数读的是 `schedule_handle` 的同一个入口，与 `<课>` 标识、上课结算三处共用。

**两个 token 对教师侧与学生侧通用**：先查 `get_now_teaching()`（教师视角反查全局课表），查不到再查
`get_now_course()`（学生视角）。同一个人不可能既在授课又在听课，不会歧义——所以
`data/talk/work/teach/` 与 `attent_class/` 两批口上可以用完全相同的 premise 写法，1b 阶段的生成模板少一套。

#### 实施中发现的偏离（§2.9）

17. **`CourseType` 必须先于 `Course` 判断。** `"CourseType" in premise_all_value_list[1]` 与 `"Course" in ...` 是子串判断，前者的字符串里含有后者——判序写反的话 `CVP_A1_CourseType|5_G_0` 会被 `Course` 分支吃掉，然后拿"当前科目 == 5"去比，永远不成立且不报错。代码里已加注释，测试里也专门留了一项断言钉住这个顺序。
18. **方案 §3.17 只写了 `Course` 一个 token，实施时加成了两个。** 起因是 §3.21 说体育课与兴趣课的口上"靠 `Course` 前提区分这是在上课还是自己在玩"——但这两种课**没有科目**（学的是该活动自带的东西），`Course|<能力id>` 对它们无从取值。补 `CourseType|<0~5>` 才能表达"这一节是体育课"。方案 §3.17 已同步定稿。

#### 步骤 §2.10 三个面板与入口（2026-09-06）

| 文件 | 类型 | 实际改动 |
| --- | --- | --- |
| `Script/System/Education_System/class_schedule_panel.py` | 新增 | 页签容器 `Education_Manage_Panel` + 全局课表面板；另含两个被另两个面板共用的常量与函数（`WEEK_NAME`、`SUBJECT_ABILITY_LIST`、`get_period_time_text()`） |
| `Script/System/Education_System/course_select_panel.py` | 新增 | 个人课表面板，含「复制到其他孩子」 |
| `Script/System/Education_System/growth_panel.py` | 新增 | 养成总览面板 |
| `Script/Core/constant/__init__.py` | 改 | `Panel.EDUCATION_MANAGE = 68`（67 妊娠总览是当前最大） |
| `Script/UI/Flow/normal_flow.py` | 改 | 注册面板 68，照 `MANAGE_DORMITORY` 的写法用函数内延迟 import |
| `Script/System/Instruct_System/Instruct.py` | 改 | `EDUCATION_MANAGE` / `CHECK_REPORT_CARD` 两个指令常量 |
| `Script/System/Instruct_System/handle_instruct.py` | 改 | 两个指令的处理函数 |
| `data/csv/InstructConfig.csv` | 改 | `2039,education_manage`（前提 `IN_TEACHER_OFFICE`，开面板 68）、`2040,check_report_card`（前提 `TARGET_IS_PLAYER_DAUGHTER`，走 §2.3 建的行为 229） |

**三个面板都靠"降一个维度"来适配终端宽度**：全局课表是「10 教室 × 7 天 × 9 节」的三维数据，
一次全画必然溢出，所以**一次只画一间教室的周表**，教室走上方横向页签；个人课表同理，一次一个孩子。

**排课冲突在面板上直接阻止，不留到运行时兜错**（方案 §3.14）：选教师时撞课的干员**不做成按钮**，
直接灰显并标出"第 N 节已在 X 教室"——玩家看得见原因，比事后弹一句报错好懂。同理，
个人课表选教室课时只列**该节次已经排了课**的教室，格子上直接把"科目/教师"写出来，看得见再选；
周日的实习课整列不可选，标明"全岛无人上班，找不到带教干员"。

**入口挂在教师办公室**（`data/map/教/办公室/Scene.json` 的 `SceneTag` 是 `Teacher_Office`，
既有前提 `IN_TEACHER_OFFICE` 直接可用，无需新增前提）。

#### 实施中发现的偏离（§2.10）

19. **`game_config.config_instruct` 按 **cid** 索引，按 `instruct_id` 字符串查要走 `config_instruct_by_id`。** 与 §2.3 记过的 `config_behavior`（按 en_name 字符串索引）**正好相反**——两张表的索引口径不一致，验证时按错的那个查会拿到 `KeyError`，看上去像配置没生效。
20. **页签容器放在了 `class_schedule_panel.py` 里，而不是另起一个文件。** §1.6 只规划了三个面板文件，没有容器文件；全局课表是三个页签里的主页面，容器跟它放一起最省一次跳转。三个面板共用的 `WEEK_NAME` / `SUBJECT_ABILITY_LIST` / `get_period_time_text()` 也定义在这里，另两个面板 import 它。
21. **`auto_schedule.py`（自动排课）与 `semester_handle.py`（学期切换 / 成绩单生成）本期未建。** §1.6 把它们列进了一期的文件清单，但自动排课的三种模式（补弱项 / 均衡 / 主修优先）依赖二期的日程模板，学期切换要接的成绩单也要等口上到位才有内容可出。一期先把**手动排课**跑通即可验收——全局课表能排、个人课表能选、孩子能按表上课，这条链已经闭环。方案 §5.2 的面板草图里画了一个「自动排课」按钮，本轮**没有画上去**——功能不在本期，画个点不动的按钮不如不画。

#### 步骤 §2.11 口上填充：格式定稿与试点（2026-09-06）

先做 2 个试点文件把格式钉死，再按科目铺开：

| 文件 | 条数 | 前提写法 |
| --- | --- | --- |
| `data/talk/work/teach/teach_knowledge.csv` | 16 | `CVP_A1_Course\|45_G_0&CVP_A1_CourseType\|<0/1/2>_G_0` |
| `data/talk/work/attent_class/attent_class_knowledge.csv` | 14 | 上述两条 + `self_is_player_daughter` + `CVP_A1_T\|<102/103>_E_1` |

**定稿的四条格式约定：**

1. **表头 5 行照抄同目录既有文件**，`cid,behavior_id,adv_id,premise,context`，第 4 行的 `0,0,0,0,1`
   指明只有 `context` 列参与翻译。
2. **cid 从 1000 起**，构建时会自动加 `<父目录名>_<文件名>` 前缀防跨文件冲突
   （`buildconfig.py:190`）——实测 `data/talk/work/teach/teach_knowledge.csv` 的 1000 变成了
   `teach_teach_knowledge1000`。⚠️ 前缀是**父目录+文件名**，所以 §3.18 的命名会出现
   `teach_teach_` 这样的重复；`data/talk/daily/gift/` 早就是这样了，本期沿用不另立规矩。
3. **教师侧不带年龄前提**：方案 §3.18 原写"30 条 = 3 课型 × 2 年龄 × 5"，但 `teach` 的
   `character_id` 是教师，他身上没有学生的年龄可判。改为 3 课型 × N 条，年龄差分只做在
   学生侧的 `attent_class` 上。
4. **既有的占位口上保留不删**：`data/talk/work/teach.csv` 与 `attent_class.csv` 各一条
   `high_1` 的空前提行，正好充当所有具体前提都不成立时的兜底，删掉反而会出现"没有任何口上"的空窗。

#### 步骤 §2.11 第二批：10 门文化课的授课与听课（2026-09-06）

| 目录 | 文件数 | 条数 |
| --- | --- | --- |
| `data/talk/work/teach/` | 10 | 115 |
| `data/talk/work/attent_class/` | 10 | 113 |

10 门文化课：话术 40 / 指挥 41 / 战斗 42 / 料理 43 / 音乐 44 / 学识 45 / 医术 46 / 农业 47 / 制造 48 / 绘画 49。
每门都按 3 种课型分了差分，学生侧再叠幼女 / 萝莉两档年龄。

**写作口径**（供后续批次照办）：

- **教师侧写课，学生侧写人**。`teach` 的视角是"这堂课是怎么上的"——板书、示范、提问、点评；
  `attent_class` 的视角是"这孩子在课上经历了什么"——听懂了没有、走神了没有、想起了什么。
  两边写同一节课，但不重复叙述同一件事。
- **课型差分要写出物理差别**，不是换个形容词：理论课在讲台与黑板前，实践课围着工作台、会出事故、
  老师会走下来；公开课在大礼堂，人多、坐得远、听众里混着干员。
- **年龄差分写能力而不是心智贴标签**：幼女够不着桌子、认不全字、坐不住；萝莉能预习、会复盘、
  开始意识到自己的局限。避免把幼女写成只会犯傻。
- **不写具体角色名**，一律用 `{Name}`，老师一侧也只称"老师"——因为教师是课表指派的，谁都可能。

#### 步骤 §2.11 第三批：自习与炫耀（2026-09-06）

| 目录 | 文件数 | 条数 | 行为 |
| --- | --- | --- | --- |
| `data/talk/work/self_study/` | 10 | 52 | `self_study` |
| `data/talk/system/second_show_off_study/` | 10 | 41 | `show_off_study`（二段） |

四个按科目分文件的目录到此齐了：**40 个文件、321 条**。

**为炫耀口上新增了第三个 CVP token `CourseShowOff`**（`Script/Design/handle_premise/__init__.py` 的 `C` 分支，
6 行代码）：炫耀发生在**见到玩家时**，那时通常不在任何节次内，`Course` 取不到值，
所以另开一个 token 读 `child_growth.show_off_ability`。方案 §3.17 已同步。

**自习口上不带课型差分**：自习是"本节没有可用教师"的降级，理论课与实践课的自习其实没什么
体感区别（都是一个人对着书或工具），再分三档只会写出三份雷同的文本。只按科目 × 年龄分。

**炫耀口上的写法**：幼女举着东西冲过来、萝莉装作路过——同一件事的两种表达方式差别很大，
所以这个目录的年龄差分比别处更值得写。

#### 步骤 §2.11 第四批：体育 / 兴趣 / 实习 / 成绩单 / 翘课（2026-09-06）

| 目录 / 文件 | 文件数 | 条数 | 分文件的依据 |
| --- | --- | --- | --- |
| `data/talk/work/pe_class/` | 4 | 20 | 按地点（木桩房 / 射击房 / 健身区 / 游泳池），行为分别是 `training` / `training` / `exercise` / `swimming` |
| `data/talk/play/interest_class/` | 16 | 64 | 按娱乐行为；演奏传统 / 现代乐器共用 `play_instrument`，靠场景前提分开 |
| `data/talk/work/intern_class/` | 16 | 64 | 按**岗位所在场景**，全部复用既有的 `in_<场景>` 前提 |
| `data/talk/daily/check_report_card.csv` | 1 | 6 | 单文件，用 `CVP_A2_T\|<102/103>_E_1` 分年龄 |
| `data/talk/work/skip_class.csv` | 1 | 5 | 单文件 |

**至此 §2.11 累计 78 个文件、480 条**（7 个目录 + 2 个单文件）。

**实习课按"场景"而不是按"岗位"分文件**：17 个可实习岗位只涉及 7 种能力，按能力分会把
厨房、图书馆、育儿室这些完全不同的场面糅成一份文本；而按场景分，16 处地点**全部有现成的
`in_<场景>` 前提**（`in_kitchen` / `in_clinic` / `in_library` / `in_blacksmith_shop` …），
一个新前提都不用加。坐诊医生与住院医生同在 `Clinic`，合用一份——这两个岗位的实习体验本就一样。

#### 步骤 §2.11 第五批：带教侧（2026-09-06）

带教侧口上此前卡在一个缺口上：干员执行的是**他自己的工作行为**（厨师在 `npc_work_cook`、
医生在 `cure_patient`），要让这些行为出"身边有实习生"的口上，得先有一条能表达这件事的前提。
本批把它补上了：

| 文件 | 类型 | 改动 |
| --- | --- | --- |
| `Script/Core/constant_promise.py` | 改 | `HAVE_INTERN_STUDENT` / `NOT_HAVE_INTERN_STUDENT` |
| `Script/Design/handle_premise/handle_premise_work.py` | 改 | 两条实现；⚠️ 它是 `schedule_handle.get_intern_mentor()` 的**反向查询**，两边读同一份判据（同场景 + 对方行为是 `intern_class` + 对方本节的实习目标正好是我的岗位），不会出现"学徒找得到导师、导师却不知道有学徒"的单向成立 |
| `tools/ArkEditor/csv/Premise.csv` | 改 | 2 行同步 |
| `data/talk/work/intern_mentor/` | 新增 14 | 42 条，覆盖 12 个能查到工作行为的岗位 |

**只做了 12 个岗位**：`WorkType.csv` 里宿舍管理员、住院医生、图书馆管理员、检修工程师四个岗位的
`auto_ai_work` 是「无」——他们不走状态机而是走目标搜索，当班时的行为不固定，没有稳定的
`behavior_id` 可以挂口上。这四个岗位的**学徒侧**口上照常有（`intern_class` 是学徒自己的行为），
只是带教侧不出文本。

⚠️ 铁匠与检修工程师同用 `repair_equipment` 行为、药材与花草种植员同用 `plant_manage_crop`，
所以这两对各拆成两个文件，靠场景前提分开——与实习课学徒侧按场景分文件的做法一致。

#### 步骤 §2.11 收尾：补齐第五批遗留的四个实习岗位（2026-09-06）

第五批把宿舍管理员、住院医生、图书馆管理员、检修工程师四个岗位判为"没有稳定的 `behavior_id`
可挂口上"（当时的偏离 25）。**这个结论是错的**，回头核了一遍才发现：这四个岗位不是没有工作行为，
只是不走 `WorkType.csv` 的 `auto_ai_work` 字段，而是走 `data/target/default/target.csv` 的目标链
（220100 / 220105 / 220200 / 220205 / 220305 / 220400 / 220405 七条）。顺着目标链查到状态机，
再从状态机读出它赋予的行为，四个岗位的行为都是固定的。查证过程中还带出了三个实打实的缺陷：

| 文件 | 类型 | 改动 |
| --- | --- | --- |
| `data/csv/WorkType.csv` | 改 2 行 | 031 宿舍管理员 `place_tag` `Dormitory_Manager` → `Dormitory_Manager_Room`；062 住院医生 `place_tag` `Clinic` → `Inpatient_Department` |
| `Script/System/Education_System/schedule_handle.py` | 改 | `get_course_place()` 的实习课分支：同标签多间房时不再一律取第一间 |
| `data/talk/work/intern_mentor/mentor_dormitory.csv` | 新增 | 3 条，`organize_dormitory_opinion` |
| `data/talk/work/intern_mentor/mentor_library.csv` | 新增 | 3 条，`read_book` + `in_library` |
| `data/talk/work/intern_mentor/mentor_ward.csv` | 新增 | 3 条，`ward_round` |
| `data/talk/work/intern_mentor/mentor_maintenance.csv` | 改 | 行为由 `repair_equipment` 改为 `maintenance_facilities`，3 条重写 |
| `data/talk/work/intern_class/intern_ward.csv` | 新增 | 4 条，前提用 `in_inpatient_department` |

**四个岗位的行为落点**（每一条都在测试里用状态机实调钉住，不是照着注释抄的）：

| 岗位 | 目标链 | 状态机 | 行为 | 与学徒同场景？ |
| --- | --- | --- | --- | --- |
| 宿舍管理员 031 | 220400 | 327 `dormitory_admin_organize` | `organize_dormitory_opinion` | ✅ 在舍管房 |
| 图书馆管理员 101 | 220105 | 306 `character_work_library_2` | `read_book` | ✅ 在图书馆 |
| 住院医生 062 | 220305 | 323 `character_work_ward_round` | `ward_round` | ✅ 在住院部（修正 `place_tag` 之后） |
| 检修工程师 021 | 220205 | 308 `character_work_maintenance_2` | `maintenance_facilities` | ⚠️ 否，见偏离 29 |

至此 17 个可选实习岗位中，**16 个师徒两侧都有口上**，检修工程师只有学徒侧。

#### 实施中发现的偏离（§2.11）

22. **缺失 8 门性技科目（70~77 指技/舌技/足技/胸技/膣技/肛技/腰技/榨精）的课堂口上（包括上课、自习、教学、炫耀）。** 受影响的是 `teach/` `attent_class/` `self_study/` `second_show_off_study/` 四个目录里对应这 8 门科目的 **32 个文件、约 530 条**。
   ⚠️ **机制上不受影响**：性技能力的升级需求本就是真实性交经验（方案 §3.1 的发现），课堂理论只能攒珠不能升级；
   没有专属口上时会回落到 `teach.csv` / `attent_class.csv` 里那条 `high_1` 占位地文，功能链不断。
23. **`chara_4091_U-Official` 已经有 3 条 `attent_class` 的专属口上**，前提是 `CVP_A3|4091_A|45_LE_3` 一类的学识分档。本期新增的通用口上与它并存、互不覆盖——查总条数时要记得这几条也在里面（试点验证时按总数断言就翻了车，改成按 cid 前缀筛才对）。
24. **实习课的口上按场景分而不是按岗位分**（见上），所以是 16 个文件而不是 §1.8 写的 18 个。
25. **~~缺的四个岗位没有稳定的 `behavior_id`~~ —— 这个结论是错的，收尾批次已推翻并补齐。** 第五批看到宿舍管理员、住院医生、图书馆管理员、检修工程师的 `auto_ai_work` 是「无」，就断定它们当班行为不固定。实际上 `auto_ai_work` 只是工作 AI 的**其中一条**入口（`handle_npc_ai.py:366`，且要 `auto_ai` 为真才走），这四个岗位走的是另一条：`data/target/default/target.csv` 的目标链 → 状态机 → 固定行为。
    **教训**：判断"某个岗位当班时干什么"，不能只看 `WorkType.csv` 一张表就下结论——`auto_ai_work` 为「无」恰恰说明它走的是目标链，应当接着去 `target.csv` 里按 `work_is_xxx` 前提搜一遍。当时少搜了这一步，就把"我没找到"写成了"不存在"。
26. **为带教侧新增了一条前提 `have_intern_student`。** 这是本期第二次为口上加前提（第一次是 §2.9 的三个 `Course*` token）。判据必须与学徒侧的 `get_intern_mentor()` 完全对称，否则会出现"学徒拿到了导师加成、导师却不知道有学徒"这种半边成立的状态——测试里专门用"改换实习岗位"的用例钉住了这一点。
27. **`WorkType.csv` 里两个岗位的 `place_tag` 是错的，实习课踩到了。** 031 宿舍管理员写的是 `Dormitory_Manager`，而真正的场景标签是 `Dormitory_Manager_Room`（`handle_premise_place.py:1591`）——`constant.place_data` 里根本没有前者这个键，于是 `get_course_place()` 对这个岗位**返回空列表**，学徒压根走不到岗位上去，这门实习课等于是废的。062 住院医生写的是 `Clinic`，但 `Clinic` 标签下是急诊室与门诊室，住院医生实际在住院部（`Inpatient_Department`）查房，学徒被送去了一个没有导师的房间。两条都改了。
    ⚠️ **改这两个字段是安全的**：`work_type.place_tag` 全仓只有 `handle_npc_ai.py:366` 一处读，且被 `work_type_data.auto_ai and ...` 短路保护，而这两个岗位的 `auto_ai` 都是 0，所以基础游戏的行为一点没动，受影响的只有本期新写的 `get_course_place()`。
28. **`get_course_place()` 原先"同标签的房间等价，取第一间"的假设不成立。** 实测：`Clinic` 含急诊室与门诊室但坐诊医生只在门诊室；`Dormitory_Manager_Room` 有 9 间、各区管理员只守自己那间；`Training_Room` 含射击房与木桩房；`Production_Workshop` 含生产车间 1~5。取第一间的话，学徒有很大概率站在一间没有导师的房里，然后 `get_intern_mentor()` 返回 -1、降级成见习——而且**不会报任何错**，只会表现为"实习课好像总是没人带"。
    改成三级取房：①**该标签下哪间房此刻有这个岗位的在岗干员就去哪间**（口径 53：实习就是跟着此刻在做这份工作的人）→ ②取与岗位 `place` 同名的那间（坐诊医生 → 门诊室）→ ③退回第一间。三级都是纯读取，无副作用，导师换房时学徒下一节次自然跟过去。
29. **检修工程师仍然只有学徒侧口上，但原因换了。** 不是"没有稳定行为"（那是错的），而是**师徒必然不同场景**：目标链 220200 让他在运维部进入"要检修"状态（行为是 `SHARE_BLANKLY`，1 分钟），随即 517 移动到损坏设施处，220205 才在**那里**执行 `maintenance_facilities`；而学徒是待在岗位地点（运维部）不动的。`mentor_maintenance.csv` 已经从错挂的 `repair_equipment`（那是铁匠的行为，害得它一直在铁匠铺里跟 `mentor_blacksmith.csv` 抢词条）改回正确的 `maintenance_facilities`，条文也重写了；在一期"学徒待在岗位地点"的模型下它基本不会触发，等哪一期做了"学徒跟着导师走"再自然生效。
30. **住院医生的学徒侧要单独一份 `intern_ward.csv`。** `place_tag` 从 `Clinic` 改到 `Inpatient_Department` 之后，这个岗位的学徒不再站在门诊室里，原先靠 `in_clinic` 前提的 `intern_clinic.csv` 就盖不住他了。新写 4 条、前提改用 `in_inpatient_department`，与门诊那份按场景互斥，不会互相串台。

### 6.2 实施前的假设复核

对总纲 §2 与方案 §2 的现状调查逐条复核：

| # | 假设 | 复核结果 |
| --- | --- | --- |
| 1 | `Class_Room` 只有 6 处引用，其中 4 处沿用标签即自动适配 | ✅ 确认。且第 5 处（`WorkType.csv` 的 `place` 列）实测也只是显示文案，见 §6.1 偏离 3 |
| 2 | `handle_instruct.py:553~573` 与 `StateMachine/default.py:2648` 是平行实现 | ✅ 确认（读码核对，改造待步骤 §2.6/§2.7） |
| 3 | `StateMachine/default.py:441` 的 `place_data` 会自动收录新教室 | ✅ 确认。重建缓存后 `place_data["Class_Room"]` 含全部 6 间理论教室，`Practice_Room` 3 间、`Auditorium` 1 间 |
| 4 | `Facility_effect.csv` 的教育区 `effect` 列在代码中从未被读取 | ✅ 确认，本期已接上（`growth_handle.get_education_zone_adjust()`，Lv1~Lv5 实测倍率 1.0/1.05/1.2/1.5/2.0） |
| 7 | ✗ **方案 §3.1 原假设「等级由 `get_experience_level_weight` 自动换算」** | ✗ **不成立**：该函数零调用方，是死代码；真实链条见总纲 §2.3-11。方案已重写 |
| 8 | 科目→经验id 可从 `AbilityUp.csv` 解出，无需硬编码 | ✅ 确认（学识→82、战斗→81、话术→80、料理→83、膣技→61） |
| 5 | `talk.py:185~188` 对女儿有 5 倍加权 | |
| 6 | `Entertainment.csv:62` 品酒的 `T7|0` 前提能挡住未成年 | |

### 6.3 单元测试结果

#### 步骤 §2.1 教育区改建

| 验证项 | 结果 |
| --- | --- |
| `tools/map_aa_check.py 教` | ✅ **0px 错位**，10 个字号（12/14/16/18/20/22/24/26/30/40）全部通过。⚠️ 这是目前仓库里唯一在 0 容差下通过的地图（`训练` 需 `--tol 2`，其余地图均 FAIL） |
| 生成期自检 | ✅ 15 行每行 105U；全图无 ASCII 空格；无裸尖括号 |
| 按钮名 ↔ 目录名 | ✅ 双向零差集（避免 `map_handle.py:363` 的 `RecursionError`） |
| `Map.json` PathEdge ↔ 目录 | ✅ 双向零差集，18 节点全部双向边 |
| `buildconfig.py` | ✅ 退出码 0 |
| `init_data.py`（删缓存后重建） | ✅ 退出码 0，产出 `ScenePath` 22.1 MB |
| 场景标签收录 | ✅ `Class_Room` 6 间、`Practice_Room` 3 间、`Auditorium` 1 间 |
| 教育区内部寻路 | ✅ 走廊 → 全部 17 个节点均可达 |
| 旧「教室」场景 | ✅ 已从 `scene_data` 中消失（残留的「关押\调教室」是无关场景） |

#### 步骤 §2.4 节次判定（13 项断言全部通过）

09:00→0、09:44→0、09:45→1、11:15→3、11:59→3、12:00→−1、13:59→−1、14:00→4、17:00→8、17:44→8、17:45→−1、19:00→−1、08:59→−1

#### 步骤 §2.5/§2.6 成长与课表（31 项断言全部通过）

| 组 | 断言 | 结果 |
| --- | --- | --- |
| 速度系数曲线 | diff = +8/+4/+1/0/−1/−2/−8 → 3.00/2.00/1.25/1.00/0.67/0.50/0.20 | ✅ 7/7 |
| 科目经验id（从 `AbilityUp.csv` 解出） | 学识45→82、战斗42→81、话术40→80、料理43→83、膣技74→61 | ✅ 5/5 |
| 教育区效率加成 | Lv1~Lv5 → 1.0/1.05/1.2/1.5/2.0 | ✅ 5/5 |
| 课表读写与教师反查 | 存取、未排返回None、教师整周反查、撞课判定、清空 | ✅ 8/8 |
| 可排课教室列表（源自场景标签） | 理论 6 / 实践 3 / 大礼堂 1，按教室反查课型 | ✅ 6/6 |

**关键实测值**：学识 0→8 累计需习得珠 49,470、学识经验 1,145；一节理论课（速度 1.0）习得值 75、经验 3；珠约束 659 节、经验约束 381 节 —— **珠是瓶颈**。

#### 步骤 §2.3/§2.10 配置与状态标识（24 项断言全部通过）

| 组 | 断言 | 结果 |
| --- | --- | --- |
| `class_ok` 列进入运行时 | 下棋=1、泡温泉=0、游泳=0、品酒=0，可排兴趣课共 **16 项** | ✅ 5/5 |
| 教室解锁配置 | 理论教室二→152、理论教室六→155；理论教室一与大礼堂不在解锁表（Lv1 即开） | ✅ 4/4 |
| `<课>` 提示文案 | 学生听课 / 教师授课 / 无教师自习 / 翘课 / 休息中不显示 / 无课表信息 / 兴趣课 / 实习课 / 体育课 | ✅ 11/11 |
| 状态列表结构 | draw 对象数与文本数一致；`<课>` 样式为 `light_steel_blue`；带 tooltip | ✅ 4/4 |

#### 步骤 §2.3 行为与效果进入运行时（8 项断言全部通过）

| 断言 | 结果 |
| --- | --- |
| `config_behavior` 含 self_study/skip_class/check_report_card/show_off_study，cid 与时长正确 | ✅ 4/4 |
| `config_behavior_effect_data` 的效果串：`[1511,1512,548]` / `[549]` / `[550]` / `[551]` | ✅ 4/4 |

⚠️ **本表最后一项后来被推翻**：`show_off_study` 的 `[551]` 是错的 —— 551 注册在**一段**结算表里，二段行为永远取不到它。§2.8 已改为 `[622]`（`SecondEffect` 命名空间），详见 §2.8 的偏离 9。这份断言当时只查了效果串的**值**、没查它注册在**哪张表**，所以放过了这个 BUG。
| 全部改动文件通过 `py_compile` | ✅ |
| 两套既有测试（31 项 + 24 项）全部回归通过 | ✅ |

⚠️ 排查记录：`game_config.config_behavior` 是**按 `en_name` 字符串索引**的，不是按 cid。首次验证时按 cid 取而报 `KeyError: 211`，虚惊一场。

**实际文案样例**：
- 学生：`理论课·学识技能｜理论教室一｜授课：凯尔希｜第1节`
- 教师：`授课中：理论课·学识技能｜理论教室一｜第1节`
- 无教师：`自习·理论课·学识技能｜理论教室一｜本节无教师，经验减半｜第1节`
- 翘课：`翘课中：本该上 理论课·学识技能｜理论教室一（第1节）`（红色 `<翘>`）
- 个人式课：`兴趣课·下棋｜第1节`、`实习课·厨师｜第1节`、`体育课·木桩房｜第1节`

#### 步骤 §2.8 验证（42 项断言全部通过）

| 断言组 | 项数 | 结果 |
| --- | --- | --- |
| 四个负面状态的等级和：全0 / 四项各600（各2级）→ 0 / 8 | 2 | ✅ |
| 翘课概率阶梯：等级和 0/3/4/7/8/11/12/15/16/20 → 0/0/.1/.1/.25/.25/.45/.45/.7/.7 | 10 | ✅ |
| 体力闸：体力20%时走 `REST`、累加一节缺课、不置翘课flag | 3 | ✅ |
| 体力闸优先于心情闸：等级和打桩为 32（最坏）时仍走 `REST` | （含上） | ✅ |
| 缺课去重：同一节课判定三次只记一次；换一节课才再记一次 | 2 | ✅ |
| 翘课掷骰：等级和32时 400 次里 276 次翘课（期望区间 240~320）；等级和0时 200 次一次不翘 | 2 | ✅ |
| 翘课不计入 `absent_count`（它只统计被动缺课） | 1 | ✅ |
| 已置 flag 则当日不再掷骰，直接翘 | 1 | ✅ |
| 派课：不在教室→561、在教室有老师→304、老师在H中/外勤中/课表没排老师→713 | 5 | ✅ |
| 不接管：不在节次内返回0；没有个人课表的角色返回0，**且不会被凭空建出养成数据** | 3 | ✅ |
| 二段行为 1328/1329 的 cid 与效果串 `[622]` / `[623]`，且 622/623 在**二段**注册表里 | 6 | ✅ |
| 551 已不在一段注册表；548/549/550 仍在 | 4 | ✅ |
| 状态机 713/714 已注册 | 2 | ✅ |
| 既有两套测试（31 项 + 24 项）全部回归通过 | —— | ✅ |
| 全部改动文件 `py_compile`；`buildconfig.py` 退出码 0 | —— | ✅ |

#### 步骤 §2.7-5 个人式课型（45 项断言全部通过）

| 断言组 | 项数 | 结果 |
| --- | --- | --- |
| 实习岗位的能力与地点直接读 `WorkType.csv`（厨师 → 能力43料理、地点 `Kitchen`） | 3 | ✅ |
| `get_course_place()` 六种课型全部解析出地点；体育课精确到木桩房而非同标签的射击房；不存在的地点返回空 | 8 | ✅ |
| 行为 cid → en_name 反查：161→swimming、205→training、230→intern_class、不存在的返回空串 | 4 | ✅ |
| AI 派发：不在地点→715、到了→716；体育课执行 `training`、兴趣课执行 `play_chess`、实习课执行 `intern_class` | 8 | ✅ |
| 时长一律截到 45 分钟（战斗训练原 120 分钟） | 2 | ✅ |
| 导师到点现找：现场没厨师→-1，有厨师→他就是导师 | 2 | ✅ |
| 见习降级：有导师习得 191、无导师 65，且 65 仍高于自习档的 45+15 —— 是减半而不是掉档 | 5 | ✅ |
| `<课>` 覆盖个人式课型：实习中带导师名、无人在岗显示"降为见习"、体育课显示"体育课"、人不在地点则不显示 | 5 | ✅ |
| 新行为 230 的 cid / 时长 / 效果串 `[1511,1512,552]`；效果 552 与状态机 715/716 已注册 | 8 | ✅ |
| 既有三套测试（31 + 24 + 42 项）全部回归通过 | —— | ✅ |
| 全部改动文件 `py_compile`；`buildconfig.py` 退出码 0 | —— | ✅ |

**关键实测值**：厨师岗（能力 43 料理）实习一节 45 分钟，导师 5 级 / 学徒 0 级时习得 191、无导师见习时 65。

#### 步骤 §2.9 新前提（33 项断言全部通过）

| 断言组 | 项数 | 结果 |
| --- | --- | --- |
| `Course`：教室课的科目查全局课表；学生与教师同一 token 都成立；无关角色不成立 | 4 | ✅ |
| `CourseType`：理论 0 / 实践 1 / 体育 3 / 兴趣 4 / 实习 5 各自成立且互不串台 | 8 | ✅ |
| 实习课的科目取岗位 `ability_id`（厨师 → 料理 43） | 1 | ✅ |
| 体育课没有科目，`Course` 恒不成立 | 1 | ✅ |
| 判序：`CourseType\|5` 不会被 `Course` 分支吃掉，且 `Course\|5` 本身不成立 | 2 | ✅ |
| 不在节次内 / 清掉个人课表后一律不成立 | 3 | ✅ |
| 既有 CVP 类型（`A` 能力、`T` 素质）未被新分支影响 | 2 | ✅ |
| 场景前提：实践教室与大礼堂各自成立、互不成立；理论教室的 `in_class_room` 仍成立 | 7 | ✅ |
| ArkEditor 的 `Premise.csv` 已同步 4 行 | 4 | ✅ |
| 既有四套测试（31 + 24 + 42 + 45 项）全部回归通过 | —— | ✅ |
| 全部改动文件 `py_compile`；`buildconfig.py` 退出码 0 | —— | ✅ |

#### 步骤 §2.10 三个面板（30 项断言全部通过）

| 断言组 | 项数 | 结果 |
| --- | --- | --- |
| 入口三处齐全：面板id 68、flow 已注册、两条指令进配置且各有处理函数 | 8 | ✅ |
| `education_manage` 的前提是 `IN_TEACHER_OFFICE` 且绑定面板 68 | （含上） | ✅ |
| 节次时间文本：第1/4/5/9节 → 09:00~09:45 / 11:15~12:00 / 14:00~14:45 / 17:00~17:45 | 4 | ✅ |
| 18 门科目表齐全且全在能力表里 | 2 | ✅ |
| 可排课学生列表：孩子在前；选了课的成年干员也进；没选课的教师不进 | 3 | ✅ |
| 个人课表格子文本：教室课/体育/兴趣（显示娱乐名）/实习（显示岗位名）/未排课 | 5 | ✅ |
| 复制到其他孩子后格子与源一致；清空后全为 `--` | 2 | ✅ |
| 实习可选岗位 17 个，教师/学生/监狱长均被排除 | 4 | ✅ |
| 养成总览的阶段素质集合与 `growth_handle.CHILD_TALENT_SET` 一致；四对性格倾向 | 3 | ✅ |
| 既有五套测试（31 + 24 + 42 + 45 + 33 项）全部回归通过 | —— | ✅ |
| 全部改动文件 `py_compile`；`buildconfig.py` 退出码 0 | —— | ✅ |

⚠️ 排查记录：`game_config.config_instruct` 按 **cid** 索引，按 `instruct_id` 字符串查要走
`config_instruct_by_id`；这与 `config_behavior`（按 en_name 字符串索引）**正好相反**。
两张表的索引口径不一致，查错会拿到 `KeyError`，看上去像配置没生效。

⚠️ 面板的**绘制循环**（`flow_handle.askfor_all` 要等玩家输入）无法在无头环境里跑，
上述断言覆盖的是**数据层与注册层**：候选表、格子文本、复制与清空、入口挂载。
按钮的实际点击流程留给 §6.4 的游戏内清单。

#### 构建链：PO / MO 两步在本机跑不了（环境缺件，非代码问题）

`§3 构建与缓存` 要求 CSV / 常量改动后跑四条链，本轮的实际结果：

| 命令 | 结果 |
| --- | --- |
| `buildconfig.py` | ✅ 退出码 0，CSV 与 `config_def.py` 已重建 |
| `init_data.py`（地图缓存） | ✅ 在 §2.1 已跑过 |
| `tools/map_aa_check.py` | ✅ 「教」0px |
| `buildpo.py` | ❌ 本机没有 GNU gettext 的 `xgettext`，脚本在 `:29` 因找不到 `erArk.pot` 中止 |
| `buildmo.py` | ❌ 本机 conda 环境没装 `polib` |

⚠️ **`buildpo.py` 在没有 `xgettext` 的机器上会删掉文件**：它 `:10~11` 一进门就无条件
`os.remove(data/po/zh_CN/LC_MESSAGES/erArk_py.po)`，再靠 `xgettext` 重建（`:24`）。
`xgettext` 不存在时重建那步静默失败，脚本在 `:29` 复制 `erArk.pot` 时才报 `FileNotFoundError` 中止——
此时 `erArk_py.po` 已经没了。本轮就踩了这一下，已 `git checkout` 恢复。
**这是仓库既有的隐患，不是本计划引入的**：任何没装 GNU gettext 的人照 CLAUDE.md 的构建说明跑一次
`buildpo.py` 都会丢这个文件。建议把 `:10~11` 的删除挪到 `xgettext` 成功之后，或先判断
`shutil.which("xgettext")` 再动手。（本计划范围外，只记录不改。）

⚠️ 影响面：`buildconfig.py` 已经把**CSV 来源**的文本刷进了 `data/po/`（git 里那几个 po 的改动就是它生成的），
缺的只是从 `.py` 源码里抽 `_()` 字符串这一步——也就是本期三个面板与状态标识里新写的界面文案。
游戏默认语言是 zh_CN 而这些原文本身就是中文，**不影响显示**，只影响将来做其他语种翻译时的词条完整性。
需要在装有 `xgettext` 与 `polib` 的环境上补跑这两步。

#### 步骤 §2.11 口上试点（13 项断言全部通过）

| 断言组 | 项数 | 结果 |
| --- | --- | --- |
| 两个新文件进运行时配置：teach 16 条、attent_class 14 条，cid 已带前缀 | 3 | ✅ |
| 教师与学生身上「科目+课型」同一串前提都成立（两侧通用，口上模板可共用） | 2 | ✅ |
| 换成实践课型则不成立（课型差分真的生效） | 1 | ✅ |
| 学生侧四段串：萝莉女儿全成立；改成幼女后萝莉那条落空、幼女那条成立 | 3 | ✅ |
| 非女儿的成年学生拿不到孩子版口上，但仍拿得到「科目+课型」那两条 | 2 | ✅ |
| `buildconfig.py` 退出码 0，两文件被递归遍历收进 `config_talk` | 2 | ✅ |

#### 步骤 §2.11 第二批（8 项断言全部通过，覆盖 90 次前提判定）

| 断言组 | 结果 |
| --- | --- |
| 20 个文件全部进运行时：teach 115 条、attent_class 113 条带课程前提 | ✅ |
| 30 个「科目 × 课型」组合两侧都有口上，无遗漏 | ✅ |
| 在真实课表下逐组判前提：教师侧 / 学生侧 / 萝莉女儿侧共 **90 次全部成立** | ✅ |
| 串台检查：排学识课时，其余 9 门科目的口上**全部落空** | ✅ |
| 文本卫生：228 条全部含 `{Name}` 且为多行 | ✅ |
| 八套测试（31 + 24 + 42 + 45 + 33 + 30 + 13 + 8）全部回归通过 | ✅ |
| `buildconfig.py` 退出码 0 | ✅ |

⚠️ 两个验证脚本自身的坑，记下来免得后面重踩：

1. **`self_is_player_daughter` 判的是 `relationship.father_id == 0`**（`handle_premise_other.py:1159`），
   **不是**素质 101~104。`RELATIONSHIP.father_id` 的默认值是 **-1**，fixture 里不显式置 0，
   所有孩子版口上都会静默落空。
2. **口上里的换行是字面的两个字符「反斜杠 + n」**，不是真换行符。用 `"
" in text` 去查会
   因为转义层数不同而查错，稳妥写法是 `chr(92) + "n"`。

#### 步骤 §2.11 第三批（10 项断言，覆盖 100 次交叉判定）

| 断言组 | 结果 |
| --- | --- |
| `CourseShowOff`：无养成数据 / 有数据但表空 / 进表 / 未进表 / 同时两门 / 清空后，六种情形全对 | ✅ |
| 三个 `Course*` token 互不抢食：上着学识课且待炫耀是战斗时，五条判定各归各位 | ✅ |
| 四个目录各 10 个文件，合计 321 条 | ✅ |
| 40 个「目录 × 科目」组合全部有口上，无遗漏 | ✅ |
| 10 门科目的自习前提在真实课表下全部成立 | ✅ |
| 炫耀交叉判定 **10 × 10 = 100 次**：表里有哪门就只有哪门成立 | ✅ |
| 文本卫生：321 条全部含 `{Name}`、多行；三个孩子版目录全部带 `self_is_player_daughter` | ✅ |
| 十套测试全部回归通过 | ✅ |

⚠️ 又一次被自己的旧断言绊到：`test_showoff.py` 里写死了"self_study 7 条 / show_off 5 条"，
那是只有 1 个试点文件时的数字，目录铺开后必然失败。**同一个数字不要在两个脚本里各断言一次**——
总数交给覆盖面最广的那个脚本（`test_talk40.py`），其余只断言非空。

#### 步骤 §2.11 第四批与总校验（10 项断言全部通过）

| 断言组 | 结果 |
| --- | --- |
| 7 个目录 + 2 个单文件，合计 **78 个文件 480 条** | ✅ |
| 480 条的 `behavior_id` 全部存在于 `config_behavior` | ✅ |
| 480 条用到的普通前提名全部存在于 `constant_promise` | ✅ |
| 480 条全部含 `{Name}` 或 `{TargetName}`，且全部是多行 | ✅ |
| 十一套测试全部回归通过 | ✅ |
| `buildconfig.py` 退出码 0 | ✅ |

⚠️ 校验脚本自己踩的两个坑：

1. **扫描范围写成了 `os.path.dirname(单文件)`**，结果把整个 `data/talk/work/` 与 `daily/`
   的既有口上全扫了进来，报出一堆"不合规"——那些是别人的文件，格式本来就不同。
   校验新增内容时，扫描范围必须**显式列出自己的文件**。
2. **提取前提名的正则写成了 `[a-z0-9_]+`**，把 `in_café` 判成了未定义前提。
   仓库里确实存在带非 ASCII 字符的前提名（`constant_promise.py:622 IN_CAFÉ`），正则不能只认 ASCII。

#### 步骤 §2.11 第五批：带教侧（17 项断言全部通过）

| 断言组 | 结果 |
| --- | --- |
| `have_intern_student`：学徒未开始 / 在实习 / 不在场 / 回来 / 午休不在节次内，五种情形全对 | ✅ |
| 同场景的**别的岗位**干员不成立；反向前提 `not_have_intern_student` 对称 | ✅ |
| 与 `get_intern_mentor()` 互为反向：改换实习岗位后，两侧同时切换，无单向成立 | ✅ |
| 带教口上 14 文件 42 条（收尾批次后为 17 文件 51 条），行为id全部有效且全部带 `have_intern_student` | ✅ |
| ArkEditor 的 `Premise.csv` 已同步 2 行 | ✅ |
| 口上总校验：**92 个文件 522 条**（收尾批次后为 96 文件 535 条），行为id / 前提名 / 文本卫生全部合规 | ✅ |
| 十二套测试全部回归通过 | ✅ |

⚠️ 又一次踩到快照过期：总校验脚本用的是导出到文件的前提名清单，新增前提之后忘了重新导出，
于是把刚加的 `have_intern_student` 判成了未定义。**从外部文件读的校验基准，每次改动源头都要重导。**

#### 步骤 §2.11 收尾：实习课选房与四个补写岗位（20 项断言全部通过）

| 断言组 | 项数 | 结果 |
| --- | --- | --- |
| 17 个可选实习岗位**全部**能解析出地点（宿舍管理员原先返回空列表） | 2 | ✅ |
| 同标签多间房按岗位 `place` 精确取：坐诊医生 → 门诊室（而非 `Clinic` 的第一间急诊室）；住院医生 → 住院部 | 2 | ✅ |
| 在岗导师优先：3 区管理员在岗 → 解析到 3 区；他一走 → 退回第一间；训练学员在木桩房 → 解析到木桩房 | 4 | ✅ |
| 无人在岗时不报错、稳定退回第一间 | 1 | ✅ |
| 体育课仍按场景名精确取、理论课仍走教室名（新分支没有波及其他课型） | 2 | ✅ |
| **四个补写岗位的口上行为 == 状态机实调后真正赋予的行为**（`dormitory_admin_organize` / `character_work_maintenance_2` / `character_work_ward_round` / `character_work_library_2` 逐个真跑一遍再比对） | 4 | ✅ |
| 学徒侧 `intern_ward.csv` 4 条，全带 `in_inpatient_department` 与 `self_is_player_daughter`；与门诊那份按场景互斥 | 4 | ✅ |
| 口上总校验：**96 个文件 535 条**，行为id / 前提名 / 文本卫生全部合规 | 1 | ✅ |
| 十三套测试全部回归通过（growth / premise / mentor / talk / talk10 / talk40 / showoff / talkall / personal / classmark / classai / panel / place） | —— | ✅ |
| `buildconfig.py` 退出码 0 | —— | ✅ |

⚠️ 这批里最值钱的一项是**用状态机实调去校验口上的行为id**。第五批把 `mentor_maintenance.csv`
挂在了 `repair_equipment` 上（那是铁匠的行为），当时的测试只查"这个行为id在 `config_behavior` 里存在"，
所以一路绿灯——存在不等于**是这个岗位的**。改成"把状态机真跑一遍，看它给角色赋了哪个行为，
再跟口上文件里写的比"之后，这个错当场就露出来了。
**校验一个 id 时，要校验的是它指向对不对，而不是它存不存在。**

⚠️ 顺带记一条环境坑：`character_work_ward_round` / `character_work_maintenance_2` 会调
`basement.calc_facility_efficiency()` 折算时长，无头环境下 `cache.rhodes_island.facility_level` 是空的，
补零也不行（`config_facility_effect_data[name][0]` 取不到）。本测只关心它赋了哪个行为，
所以直接把 `calc_facility_efficiency` 钉成 `lambda: 1.0` —— 无头测试里，**与被测目标无关的基建依赖直接钉死比喂 fixture 划算**。

### 6.4 尚未覆盖的验证

（留给用户的游戏内清单）

### 6.5 追加调整实施记录

**2026-09-08 第二轮（与方案 §9.2 成对）：面板架构重构 + 九项界面调整**

分两批做：先修玩家反馈的三个面板 BUG（§9.2.1），再做九项界面调整（§9.2.2~9.2.5）。

#### 实际改动

| 文件 | 类型 | 实际改动 |
| --- | --- | --- |
| `Script/System/Education_System/class_schedule_panel.py` | 改 | 容器 `Education_Manage_Panel` 改为持有四个子面板实例并统一 `askfor_all`，页签按钮去掉 `cmd_func` 改显式派发，while 顶部加 `basement.get_base_updata()`；`Class_Schedule_Panel.draw()` 拆为 `draw_page/handle_yrn`、删「返回上级」、教室 return_text 加 `ROOM_` 前缀；`_select_teacher` 加 `ability_id` 参数、包 `while 1`、每行6人、显示科目等级、可切排序；`_select_must_attend` 换人口来源并改每行6个；`_edit_sex_class` 主修科目加 `gold_enrod` |
| `Script/System/Education_System/course_select_panel.py` | 改 | `draw()` 拆为 `draw_page/handle_yrn`、删「返回上级」；`get_student_candidate_list()` 改为委托数据层；`_select_course_type` 删除，新增 `_select_course`（班级式课直接列本节各教室的课）；`_select_target` 只留三个个人式分支，三类都改每行6个 |
| `Script/System/Education_System/schedule_template_panel.py` | 改 | `draw()` 拆为 `draw_page/handle_yrn`、删与容器撞名的 `[返回]`；`_select_activity` 改每行6个并固定第一行三项；`_batch_apply` / `_select_template` 补换行 |
| `Script/System/Education_System/growth_panel.py` | 改 | `draw()` 拆为 `draw_page/handle_yrn`、删「返回上级」 |
| `Script/System/Education_System/growth_handle.py` | 改 | 新增 `STUDENT_STAGE_TALENT_SET`、`get_character_stage()`、`get_student_candidate_list()`（口径的唯一出处） |
| `Script/System/Education_System/schedule_handle.py` | 改 | 新增 `CLASSROOM_NUMBER_ORDER`、`judge_classroom_open()`、`get_classroom_sort_key()`；`get_classroom_list()` 重写为「按课型分组 + 开放过滤 + 组内数值序」 |
| `Script/System/Education_System/schedule_template_handle.py` | 改 | `ENTERTAINMENT_SELF_STUDY` 由错值 154 改为 178；新增 `CHILD_SCHEDULE_FIRST_ROW`；`PRESET_TEMPLATE_SLOT_NAME` 同步改名 |
| `data/csv/Entertainment.csv` | 改 | cid 178 娱乐名 `自习` → `上课（无课时自习）` |
| `update.log` | 改 | v0.67 段追加 调整 7 条、修正 3 条 |

#### 实施中发现的偏离（§9.2）

31. **「返回上级」的语义直到重构时才被识别清楚。** 它不是一个功能按钮，而是「退出子面板的 while、
    让容器重新接管输入」——也就是「解锁上面那排页签」。方案 §5.2/§5.3/二期 §5.1 的线框图里画的
    `[返回]` 被实现成了这个东西，容器自己的 `[返回]` 反而要等它之后才画得出来。本轮把三个
    「返回上级」整个删除，线框图同步改为标注「由页签容器统一提供」。
    ⚠️ 这**打破了宿舍面板确立的既有范式**（`Dormitory_System/宿舍管理系统设计文档.md` 写着
    「每页均提供返回上级按钮，保持与现有基建面板一致」）。教育面板不再有它，是因为宿舍面板的
    子页面本就不持有自己的循环，那里的「返回上级」是真的进出子流程；教育面板的则是循环嵌套的副产物。

32. **方案 §5.2 线框图那句"只列已解锁的（§3.11）"，一期实现时并未真正成立。**
    代码里写着「未解锁的教室不会出现在 place_data 里」，但 `place_data` 是配置载入期由
    `data/map/` 目录树静态构建的，与存档无关——十间教室从一开始就全在里面。
    本轮才真正接上 `facility_open`（§9.2.3）。

33. **口径 24 被推翻。** 「成年干员自选了课时也要能改」的分支随学生口径收紧一并取消，
    详见 §9.2.2。方案 §5.3 与本文件未再出现该口径的描述。

34. **`_select_teacher` 的签名变更是被迫的。** 要在教师名后显示「该科目」的等级，就必须知道是哪一科，
    而原签名里没有 `ability_id`——它在调用方 `_edit_cell` 的局部变量里。加参数是最小改动。

35. **发现一个与本期无关的既有缺陷，未处理**：`Script/Design/basement.py:211-214`，
    `green_house_line` 尚无 0 号线时，那段会用到尚未赋值的 `produce_effect` 而抛 `UnboundLocalError`
    （追溯到 2025-12-01 的 `eb4730bc5`）。异常抛出前 0 号线已被种下，所以第二次调用起就正常，
    真实存档不受影响；但**首次 `get_base_updata()` 会炸**。本轮给教育面板加了这个调用，
    风险与宿舍/基建面板完全同级，故未改动 `basement.py`——它不属于本期范围。

#### 单元测试结果

三套无头测试，共 **67 条断言全绿**（`headless-game-test` 模式 A，捕获面板每一屏的 `return_list`）：

| 测试 | 条数 | 覆盖 |
| --- | --- | --- |
| 面板架构回归 | 27 | 四个页签在每一屏都可点、同屏 return_text 无撞名、切教室后页签仍在、选中态跨页签保持、首屏即有 `[返回]`、「返回上级」零残留 |
| 数据层 | 16 | 教育区 Lv1~Lv5 各自的教室名单与顺序精确匹配 `Facility_open.csv`；默认页签落在理论教室一；候选人只剩三阶段的女儿，**且开启萝莉化世界设定后结果不变** |
| 九项界面 | 24 | 改名与预设模板一致性；教师排序升降序、8人分栏；必修学生只列女儿；选课首屏含已排课教室、班级式类型按钮消失；六处屏幕的最宽一行均 ≤ 190 列 |

排版断言的做法：替换全部绘制类的 `draw`，按 `line_feed` 切行、用 `text_handle.get_text_index`
实算每个元素的显示列宽（**不能用 `len()`**，中文只算 1 会漏掉一半宽度），断言每行 ≤ `text_width`。
这条断言在改前会对「选择活动」报出 1102 列。

反向验证：把四个面板文件 `git checkout` 回改前版本再跑同一套测试，第一屏捕获到 74 项、
其中**零个面板页签、也没有 `[返回]`**，三个症状同时复现——证明测试确实能抓到原 BUG。

#### 尚未覆盖的验证

- 排版观感与 Web 绘制模式仍需人工各跑一遍。无头测试验的是 `return_list` 判定链路与列宽算术，
  不是最终观感。Tk 模式全程不清屏、内容向下追加，验收时看最底下那一屏。
- 存量存档里若已把课排在了「当前等级尚未开放」的教室上，那些排课数据仍在，只是不再显示。
  未做迁移——教室只会随等级增加而开放，不会反向关闭。

**2026-09-08 第三轮（与方案 §9.3 成对）：一键自动排课 + 基建面板入口 + 日程模板排版**

#### 实际改动

| 文件 | 类型 | 实际改动 |
| --- | --- | --- |
| `Script/System/Education_System/auto_schedule.py` | **新增** | 纯函数层：`auto_fill_class_schedule()`（全局课表，均衡铺满周一~周五）、`auto_fill_selected_course()`（个人课表，有课就上）、`pick_best_teacher()`、`judge_subject_fit_classroom()`、`get_auto_subject_list()` |
| `Script/System/Education_System/class_schedule_panel.py` | 改 | 加 `[一键排满全部教室]` 按钮与 `_auto_fill_schedule()`，结果用 `NormalDraw` + `gold_enrod` |
| `Script/System/Education_System/course_select_panel.py` | 改 | 加 `[一键选课]` 按钮与 `_auto_fill_course()` |
| `Script/System/Education_System/schedule_template_panel.py` | 改 | 新增 `COLUMN_INDENT` / `COLUMN_WIDTH_ID` / `COLUMN_WIDTH_NAME` / `COLUMN_WIDTH_SLOT` 四个常量；`_draw_head` 与 `_draw_template_table` 改为共用这组常量并走 `pad_display_width`；三个孤立按钮的宽度由 `width/2` 改为满宽 |
| `Script/UI/Panel/manage_basement_panel.py` | 改 | 教育区的子系统按钮加 `[教育管理系统]`；`jump_to_son_panel` 加对应分支（函数内 import） |
| `update.log` | 改 | v0.67 段追加 新增 3 条、修正 2 条 |
| `plan_22_生长养成系统_一期_方案.md` | 改 | §5.2/§5.3 线框图加回一键按钮；新增 §9.3 |
| `plan_22_生长养成系统_总纲.md` | 改 | 口径 23/28 标注实装状态与差距 |

#### 实施中发现的偏离（§9.3）

36. **偏离 21 本轮兑现。** 一期把 `auto_schedule.py` 推给二期，理由是「三种模式依赖二期的日程模板」——
    该依赖在二期实施（2026-09-07）时就已解除，但二/三/四期文档里 `自动排课` 零命中，
    这条一直没人认领，直到本轮才补上。**教训：跨期推迟的欠账要在目标期的方案里落一条，否则会永久悬空。**
    （`semester_handle.py`（学期切换 / 成绩单）仍未建，继续挂账。**该挂账已于同日第五轮结清**。）

37. **口径 28 只落实三分之一。** 只做「均衡」。另两种的硬障碍写在方案 §9.3.2：
    补弱项会被**升不了级的性技科目**刷屏（性技升级要真实性交经验，理论课只攒通用珠）；
    主修优先缺 `CHILD_GROWTH` 的主修/副修字段。两者都不是「顺手加个分支」能解决的。

38. **方案 §3.3 的「实践课侧重动手类」此前从未落实过。** 那一条一直只是方案里的文字，
    代码对 18 门科目一视同仁，手排时实践教室照样能排话术。本轮的自动排课**第一次把它变成代码**
    （`PRACTICE_SUBJECT_SET`）。⚠️ 但**手排仍不受限**——`_select_subject` 没改，
    这是有意的：自动排课给的是合理默认值，不该反过来限制玩家手排。

39. **教育管理系统新增第二个入口，且不需要任何新机制。** 管理罗德岛跳子系统走的是嵌套函数调用
    而非 `now_panel_id` 切换，所以 `[返回]` 里那句 `now_panel_id = IN_SCENE` 在这条路径上
    是无害空操作。全仓库没有「记住来源面板」机制，也不需要。详见方案 §9.3.4。

40. **日程模板的列错位是 `{:<10}` 对中文失效。** `str.__format__` 按 `len()` 补齐、终端按显示列排版。
    四行的字符数**全都是 57**，显示列宽却是 82/75/71/61。⚠️ 这类错位**用 `len()` 是测不出来的**，
    回归断言必须用 `text_handle.get_text_index()` 实算显示宽。

#### 单元测试结果

新增 `test_auto_schedule`（21 条），连同既有三套共 **88 条断言全绿**：

| 测试 | 条数 | 覆盖 |
| --- | --- | --- |
| 面板架构回归 | 27 | 页签、撞名、选中态、首屏 `[返回]` |
| 数据层 | 16 | 教室开放与排序、学生候选人口径 |
| 九项界面 | 24 | 改名一致性、教师排序、选课链路、六处屏幕列宽 |
| **自动排课等三项** | **21** | 周末不排、无教师撞课、76腰技零命中、实践教室科目约束、每格教师是最优、学科均衡极差、只填空格、**幂等**、**可复现**、个人选课取等级最低、基建入口、**日程模板表头与四行列起点完全一致** |

8 名教师铺满 10 间教室的周一~周五：排上 360 节、留空 90 节
（教师同时只能在一处，10 间教室同一节次最多同时开 8 节课，符合预期）。

关键断言的写法：
- **无教师撞课**用「遍历全表自查」而不是信任 `judge_teacher_conflict`——后者正是被测对象。
- **可复现**：清空后重排两次，断言两次的 `class_schedule` 完全相等（验 `sorted()` 是否到位）。
- **幂等**：连点两次，断言第二次 `filled_count == 0` 且课表快照不变。
- **列对齐**：按显示宽度切出每列起点，断言表头与四行的起点列表完全相同。改前会得到 82/75/71/61 四个值。

#### 尚未覆盖的验证

- Tk 与 Web 两种模式的实际观感仍需人工各跑一遍。
- 自动排课在**教师数远大于教室数**时的分布未测（本轮 fixture 是 8 教师 / 10 教室，
  教师是瓶颈；反过来教师富余时「均衡」的极差表现如何没验）。
- `semester_handle.py`（学期切换与成绩单）仍未建，学期之间的整体重排（方案 §3.13）无从谈起　→ **已于 2026-09-08 第五轮结清，见本文件末尾与方案 §9.4**。

**2026-09-08 第四轮（与方案 §9.3.6 成对）：个人课表格子同时写科目名与教室名**

| 文件 | 类型 | 实际改动 |
| --- | --- | --- |
| `Script/System/Education_System/course_select_panel.py` | 改 | `_get_cell_text()` 对班级式课回查 `get_class_cell()` 取科目名，成「学识技能/理论教室一」（不带课型缩写，教室名已说明课型）；那节课被清空时显示「/已停课」。`COURSE_TYPE_SHORT` 收窄到只剩个人式三种课型 |
| `update.log` | 改 | v0.67 段追加 调整 1 条 |
| `plan_22_生长养成系统_一期_方案.md` | 改 | §5.3 线框图更新；新增 §9.3.6 |

#### 实施中发现的偏离（§9.3.6）

41. **课型缩写被去掉了，因为教室名已经说明了课型。** 「理论教室一」必然是理论课，
    再标一个「[理]」是重复；`COURSE_TYPE_SHORT` 随之收窄到只剩个人式的三种课型。
    副产物是宽度余量从 2 列涨到 6 列——最坏组合由 23 列降到 19 列，格子宽 25 列。
    ⚠️ `CenterButton` 超宽时走的截断分支（`draw.py`）**砍 2 个字符补 `~` 且完全不补齐宽度**，
    一旦触发，整行网格会左移错位而不是简单地截断。所以回归里穷举了
    **全部 18 科目 × 10 教室 = 180 种组合**逐一算显示宽，而不是只测几个样本。
    今后若新增更长的科目名或教室名，这一格会先坏——测试会先报出来。

#### 单元测试结果

新增 `test_cell_text`（12 条），连同既有四套共 **100 条断言全绿**：
班级式课两者都有、非班级式三种课型显示逻辑不变、未选课仍为 `--`、
课被清空时标「已停课」、**180 种组合穷举无一超宽**。

**2026-09-08 第五轮（与方案 §9.4 成对）：学期切换与成绩单**

一期最后一笔挂账结清。`semester_handle.py` 自 §1.6 立项起被记了三次
（偏离 21 推给二期 → 二/三/四期无人认领 → 第三轮偏离 36 再记一次挂账），本轮兑现。

#### 实际改动

| 文件 | 类型 | 实际改动 |
| --- | --- | --- |
| `Script/System/Education_System/semester_handle.py` | **新增** | 纯函数层：`settle_semester_change()`（总入口）、`build_report_card()`、`get_report_grade()`、`get_semester_attend()`、`reset_semester_baseline()`、学期进度与抬头文本、成绩单正文拼装 |
| `Script/Core/game_type.py` | 改 | `CHILD_GROWTH` 加 `semester_id` / `semester_base_attend` / `semester_base_absent` / `semester_base_ability` / `last_report_card` 五个字段 |
| `Script/Core/save_handle.py` | 改 | `CHILD_GROWTH` 的**字段级**旧档回填（按属性表整体补，不逐字段 `hasattr`） |
| `Script/Settle/past_day_settle.py` | 改 | `update_new_day()` 的非角色部分开头调学期切换，出了成绩单则推期末事件并给一条 `gold_enrod` 提示 |
| `Script/Settle/default.py` | 改 | 「检查成绩单」结算改走 `semester_handle`：有冻结快照发那份并清 flag，没有则现算「截至目前」且不动 flag；加状态 13 的判据由出勤率阈值改为读成绩档位 |
| `Script/System/Education_System/growth_handle.py` | 改 | 新增养成数值编号 4~9（本学期听课/缺课/出勤率、成绩档位、升级科目数、学期进度）并接进 `get_growth_value()` 的读口 |
| `Script/System/Education_System/growth_event_handle.py` | 改 | 加 `SEMESTER_EVENT_SUB_KEY = 200`、`push_semester_event()`、`push_semester_event_for_list()` |
| `Script/System/Education_System/class_schedule_panel.py` | 改 | 容器加 `_draw_semester_head()`，四个页签共用的学期抬头与过半提示 |
| `Script/System/Education_System/growth_panel.py` | 改 | 出勤栏拆为「累计 / 本学期」两行；新增 `_draw_report_card()` |
| `data/official_event/期末.csv` | **新增** | 16 条期末事件（优秀 4 / 良好 4 / 待努力 4 / 中性 4） |
| `data/talk/daily/check_report_card.csv` | 改 | 现有 6 条按语气挂上档位前提（正文未改），补写 8 条，凑齐 3 档 × 2 年龄 × 2 条 + 2 条兜底 |
| `update.log` | 改 | v0.67 段追加 新增 4 条、调整 2 条、修正 2 条 |
| `plan_22_生长养成系统_一期_方案.md` | 改 | §3.13 就地更正学期长度口径；新增 §9.4（含 9.4.1~9.4.8） |
| `plan_22_生长养成系统_总纲.md` | 改 | 口径 35 / 43 标注实装状态与实际口径 |

#### 实施中发现的偏离（§9.4）

42. **偏离 21 与 36 本轮全部结清，一期不再有挂账。** 这条欠账跨了四期没人认领，
    印证了第三轮偏离 36 的教训——**跨期推迟的欠账要在目标期的方案里落一条**。
    本轮之所以能找回来，靠的是回头对着总纲的口径表逐条盘实装状态，不是靠代码里有任何报错。

43. **`report_card_flag` 此前从无写入方，是一个「先有字段、后无写入」的半截功能。**
    字段在一期就写进了 `CHILD_GROWTH`，「检查成绩单」指令、行为、结算、口上也都齐了，
    唯独没有任何一处把它置 True，养成总览的「本学期成绩单待查看」永远不出现。
    ⚠️ **这种半截状态不会报任何错**——面板照画、指令照能用，只是内容是错的
    （给的是终身累计而不是本学期）。**教训：字段与它的写入方要在同一轮里落地**，
    否则只能靠人工盘口径才发现。

44. **`sub_key` 必须用保留桶键 200，这是期末事件唯一的硬约束。**
    `get_candidate_event_list()` 每天翻 `(15, 0)` 与 `(15, 当前阶段)`，
    期末事件用 0 或 101~104 会**天天被日常池抽到**。回归里为此写了双向断言：
    正向断言期末桶里 16 条一条都不在日常桶里，反向断言日常候选列表里不含任何期末事件。

45. **`CHILD_GROWTH` 的字段级旧档兼容此前整体缺失。**
    `save_handle` 只保证 `child_growth` 这个**挂载位**存在，没有任何字段级补全——
    二期加的 `schedule_template_id` / `schedule_override` / `follow_mother_flag`、
    四期加的字段，在更早的存档里其实都是缺的，只是还没人撞上 `AttributeError`。
    本轮改成**按新结构体的属性表整体回填**，一次补齐历史欠账。
    ⚠️ 每个角色各 `new` 一个默认体，否则 dict/list 这类可变默认值会被多个角色共享。

46. **成绩档位的空值必须是 −1 而不是 0。** 0 是「优秀」档，
    没有养成数据的角色若回落成 0，全岛没上过学的人都会通过优秀档的口上前提。
    `get_growth_value()` 里为此专门写了一条分支，而不是沿用「没数据一律返回 0」的通例。

47. **口上的档位差分是加权随机，不是「最具体的独占」。**
    `weight_all_to_1_flag=True` 让权重等于满足的前提条数，档位条权重 3、兜底条权重 1，
    **兜底条仍有约四分之一的概率出场**。所以那 2 条兜底的正文必须保持档位中立——
    一开始按「加了档位前提，兜底就轮不到了」设计的话，成绩很差时也会读到一条中性偏正面的文本。

48. **学期长度是季月的日历天数（28~31），方案原文的「约 30 天」是错的。**
    非季月被时钟整段跳过，季月本身的每一天都是可游玩日，两者重合，
    所以直接 `calendar.monthrange` 即可。⚠️ 写死 30 会在 2 月与大月上各错一两天，
    进度条与「还剩几天」都会偏。已先改方案 §3.13 再改代码。

#### 单元测试结果

新增 `test_semester`（90 条），连同既有五套共 **190 条断言全绿**：

| 测试 | 条数 | 覆盖 |
| --- | --- | --- |
| 面板架构回归 | 27 | 页签、撞名、选中态、首屏 `[返回]` |
| 数据层 | 16 | 教室开放与排序、学生候选人口径 |
| 九项界面 | 24 | 改名一致性、教师排序、选课链路、六处屏幕列宽 |
| 自动排课等三项 | 21 | 周末不排、无教师撞课、实践教室科目约束、幂等、可复现、日程模板列对齐 |
| **学期切换与成绩单** | **90** | 见下 |

关键断言的写法：
- **幂等与自愈**：同一学期连调两次不出第二份成绩单；学期中途新出现的孩子第一次只立基线，
  下一个学期的成绩单**只算她入学后的那一段**（断言 `attend == 4` 而不是终身的那个数）。
- **终身累计不被污染**：切学期后再上 3 节，断言本学期为 3 而 `attend_class_count` 仍是 13。
- **档位边界逐个打**：出勤率 89 差一点不算优秀、满勤但只升 1 门不算优秀、
  出勤率 70 整算良好、`0/0` 是「无课可评」而**不是**待努力。
- **桶隔离双向验**：正向查期末桶与日常桶无交集，反向查日常候选列表不含期末事件。
- **池子抽干**：把 16 条全写进 `event_history`，断言 `push_semester_event()` 返回 `False`
  且不往队列里塞东西。
- **档位覆盖**：优秀 / 良好 / 待努力三档各自都要抽得到至少 3 条（实测 5 / 5 / 4），
  否则某个档位的孩子期末永远没事件；并静态校验 16 条里全部 `CVE_` / `CVP_` token 的形状，
  写错的 token 不会在加载时报错，要等玩家做决断时才炸。
- **旧档回填**：`delattr` 掉 5 个字段再跑 `_normalize_loaded_save_paths()`，
  断言属性集合与新结构体一致，且**两个角色的 dict/list 不是同一个对象**。
- **结算两条路径**：把 `base_chara_*_common_settle` 换成空操作以隔离被测分支，
  抓 `NormalDraw.draw` 的文本，断言有快照时发冻结那份并清 flag、无快照时发「截至目前」且 flag 不动。

⚠️ 三个 fixture 陷阱（今后写养成相关的无头测试都会撞上）：
1. 前提系统的通用闸门会读 `h_state.body_item[14]`，最小角色 fixture 必须
   先 `attr_calculation.get_h_state_reset()`，否则 `KeyError: 14`；
2. 同一个闸门还会顺带判**交互对象**（默认是玩家 0）的同一个字段，所以玩家也要初始化；
3. `favorability` 是 `{0: 0}` 起步的（`character_handle.py:70`），空 dict 会让
   `CVP_*_F_*` 前提在 `favorability[0]` 上 `KeyError`。

⚠️ 还有一个测试脚本本身的坑：`os._exit()` **不会 flush 缓冲区**，
输出重定向到文件时会把全部 PASS 行丢光、只留下一个 `EXIT=0`。
要么在 `os._exit` 前 `sys.stdout.flush()`，要么用 `python -u`。

#### 尚未覆盖的验证

- Tk 与 Web 两种模式的实际观感仍需人工各跑一遍：学期抬头与过半提示、成绩单正文的排版、
  期末事件在处理公务界面里的显示。
- 16 条期末事件的**抽取分布**未测：一个孩子养到成年约十几个学期，
  档位若长期固定（例如一直优秀），只能从那一档的 4 条 + 中性 4 条里抽，
  实际会不会在成年前抽干、抽干后连着几个学期没有期末事件，需要长盘验证。
- 成绩档位的阈值（90/2 门、70）是拍的，没有按实际课表密度校准过。

**2026-09-08 第六轮（与方案 §9.5 成对）：成绩单历史页 / 本学期增量 / 死代码清理**

第五轮上线学期制之后，回头对着一期方案**逐条盘实装状态**扫出来的活。
盘查方式不是读文档凭印象，而是四轮机扫：`CHILD_GROWTH` 逐字段查写入点、
教育子系统全部非私有函数查调用点、模块级常量查读取点、
`Behavior_Effect.csv` 的效果号对 Settle 的注册表。

#### 实际改动

| 文件 | 类型 | 实际改动 |
| --- | --- | --- |
| `Script/Core/game_type.py` | 改 | `last_report_card`（单份）→ `report_card_history`（列表，最新在末尾） |
| `Script/Core/save_handle.py` | 改 | 存档迁移：把已有的单份并进列表头再删掉旧属性 |
| `Script/System/Education_System/semester_handle.py` | 改 | 新增 `REPORT_CARD_HISTORY_MAX = 8`、`get_report_card_history()`、`get_last_report_card()`、`push_report_card()`；`settle_semester_change` 改走 push |
| `Script/System/Education_System/growth_handle.py` | 改 | 成绩档位与升级科目数改读历史末尾那份；两处 `-1.0` 字面量改用 `REPORT_GRADE_NONE` |
| `Script/System/Education_System/growth_panel.py` | 改 | `_draw_report_card` 改为带前后翻页的历史页；`_draw_subject` 加本学期增量并高亮；`_draw_stage` 加胎教底子行；`_draw_flag` 改走 `growth_event_handle` 的读口；新增 `report_card_index` 状态与两个翻页返回值常量 |
| `Script/System/Education_System/class_schedule_panel.py` | 改 | 选教师时名字后加「本周已排 N 节」（接上 `get_teacher_week_schedule`） |
| `Script/System/Education_System/schedule_handle.py` | 改 | 删 `judge_student_conflict` 与 `STUDENT_WORK_TYPE`；`set_selected_course` 的docstring就地说明学生撞课为何不可能 |
| `Script/System/Sex_System/group_sex_panel.py` | 改 | 模板编辑面板里，课堂模式下体力 < 30% 的学生改为灰显「体力不足，只能旁观」且不可选 |
| `Script/Settle/default.py` | 改 | 「检查成绩单」改走 `get_last_report_card`，并在末尾提示更早的学期去哪翻 |
| `update.log` | 改 | v0.67 段追加 新增 2 条、调整 3 条、修正 1 条 |
| `plan_22_生长养成系统_一期_方案.md` | 改 | §3.13 / §3.14 / §5.4 就地更正；新增 §9.5 |
| `plan_22_生长养成系统_四期_方案.md` | 改 | §682 与 §757-26 标注实装时间 |

#### 实施中发现的偏离（§9.5）

49. **成绩单只存一份是第五轮自己埋的坑。** 「冻结快照」这个决定是对的（避免查看时现算），
    但存成**单份**就把历史一并弄丢了——学期成绩本来就该能纵向比，
    玩家看不出「上学期是不是比这学期好」。改成带上限的列表，并给第五轮那几天的存档做迁移。
    ⚠️ **必须有上限**：一个孩子养到成年约十几个学期，多孩存档不设上限会让存档持续变大。

50. **翻页下标必须是面板的属性，不能是局部变量。** 容器 `Education_Manage_Panel` 每轮 `while`
    都会重画子页，局部变量每轮都被重置，玩家点一次「上一学期」马上又跳回最新那份。
    这与 §9.2 里「子面板实例只创建一次」是同一个坑的两种表现——**凡是跨轮要保留的选中态，
    都得挂在面板实例上**。

51. **§5.4 的「本学期增量」写了五轮才落实。** 不是遗漏，是**依赖没到位**：
    「本学期」这个概念要等第五轮的学期制上线才存在。⚠️ 这类「方案写了但当期做不了」的条目，
    应当在方案里当场标出依赖与预计落地期，否则就会像 `semester_handle` 那样悬空好几期。

52. **四期口径 65 此前只落实了一半。** 「体力不足的必修学生到场、不计缺课」那半在
    `class_ai.py:249` 实装了；但四期方案 §682 与 §757-26 明写的另一半——
    「模板编辑面板实时判体力，不可选中并标『体力不足，仅旁观』」——**从未实装**，
    `judge_hp_low_only_watch` 写好了却没有任何调用者，玩家仍能把体力低的学生拖进群交模板。
    本轮接上。⚠️ **只在 `cache.sex_class_mode` 下生效**：`show_target_chara_list` 是
    普通群交共用的面板，不加这道闸会改掉既有玩法。

53. **`judge_student_conflict` 是设计冗余，不是漏接。** §3.14 列了三类冲突，
    但「学生撞课」在个人课表的结构下**不可能发生**——一个 (星期, 节次) 只存一门课，
    `set_selected_course` 直接覆盖。删掉并在 §3.14 与函数注释里就地说明，
    免得下一轮盘查的人又把它当成漏接的功能补一遍。

54. **6 个「未注册效果号」是扫描脚本的假阳性，本项经用户判断不做改动。**
    271 / 410 / 420 / 421 / 998 / 999 全在 `SecondEffect` 里且都注册了。
    扫错的两个原因值得记住：**效果号有两套号段重叠的独立注册表**
    （`BehaviorEffect` 496 个 / `SecondEffect` 158 个），只搜一套必然把另一套全报成缺失；
    **行为的 `tag` 是「二段结算|H装备」这种带子标签的形式**，用 `== "二段结算"` 精确匹配会漏判。
    按一段/二段拆开重扫后两侧都是零缺口。

#### 单元测试结果

`test_semester` 由 90 条扩到 **120 条**，连同既有五套共 **220 条断言全绿**。

新增断言的重点：
- **历史上限与顺序**：连过 11 个学期，断言被裁到 8 份、最新在末尾、列表按时间正序、
  最旧那几份确实被丢掉、`get_last_report_card()` 取的就是末尾那个对象。
- **翻页边界**：首次进入回落到最新那份；最新那份只画一个按钮、中间页两个都在；
  连点 20 次「上一页」被夹回有效区间；换孩子清掉下标；只有一份时一个按钮都不画。
- **死代码接线**：六个符号逐个断言——两个已从模块上消失（`hasattr` 为假），
  四个能在对应函数的源码里搜到调用。
- **宽度**：教师按钮加了「/N节」之后穷举最坏组合，断言不超过 31 列的格位
  （超了会触发 `LeftButton` 的截断分支，整行网格左移）。

⚠️ 本轮的测试脚本自身踩了两个坑，记下来：
`Growth_Panel.student_list` 平时由 `draw_page` 每轮重算，直接调 `handle_yrn` 要先手动喂一份，
否则它在换孩子之前就 `return` 了；群交模板面板的类名是 `Edit_Group_Sex_Temple_Panel`
而不是想当然的 `Group_Sex_Panel`。

#### 尚未覆盖的验证

- Tk 与 Web 两种模式的人工验收：成绩单翻页区的排版、科目栏加了「（本学期+N）」之后的对齐、
  选教师那一屏加了「/N节」之后的网格。
- 群交模板面板的改动**只在课堂模式下生效**，普通群交的表现未回归——需要人工开一次普通群交确认没变。
- 成绩单上限 8 份是拍的，没有按实际养成周期（幼女到少女约十几个学期）校准过。

**2026-09-08 第七轮（与方案 §9.6 成对）：教育系统常量集中到 `education_constant.py`**

照怀孕系统 `pregnancy_constant.py` 的成例做的一次纯搬家。盘查方式是 AST 逐文件取模块级
`ALL_CAPS` 赋值，再对全仓库反查引用点（裸引用 / `<模块>.常量` 两种写法都扫）。

#### 实际改动

| 文件 | 类型 | 实际改动 |
| --- | --- | --- |
| `Script/System/Education_System/education_constant.py` | **新建** | 402 行，113 个常量分 15 组；原 114 个去重合并掉 1 个 |
| `Script/System/Education_System/` 其余 13 个模块 | 改 | 删掉全部 116 处模块级常量定义，补 `education_constant` 的 import，209 处引用改写 |
| `Script/Settle/default.py` | 改 | 11 处引用改写；`handle_nuirse_child_add_adjust` 的 `baby_growth_handle` 导入随之作废 |
| `Script/StateMachine/default.py` | 改 | 6 处；`character_education_skip_class` 的 `schedule_handle` 导入随之作废 |
| `Script/UI/Panel/character_info_head.py` | 改 | 8 处；`get_course_text` 的 `schedule_handle` 导入随之作废 |
| `Script/Design/handle_premise/__init__.py` | 改 | 2 处引用 + 1 处注释里的编号出处 |
| `Script/Design/handle_premise/handle_premise_work.py` | 改 | 1 处 |
| `Script/System/Instruct_System/handle_instruct.py` | 改 | 2 处；`ask_for_sex_class_ability` 的 `sex_class_handle` 导入随之作废 |
| `Script/Design/settle_behavior.py` | 改 | 注释里的养成数值编号出处 |
| `Script/Core/game_type.py` | 改 | `prenatal_point` 字段注释里的上限出处 |
| `update.log` | 改 | v0.67 段追加 调整 1 条 |
| `plan_22_生长养成系统_一期_方案.md` | 改 | 新增 §9.6 |
| `plan_22_生长养成系统_一期_实施步骤与记录.md` | 改 | §1.6 文件清单补一行；新增本节 |

#### 实施中发现的偏离（§9.6，编号接 54 往下）

55. **散落不是「不整齐」，是让作者只能重复写。** 扫出 2 个同名常量各写两份
    （`ABSENT_HP_RATE`、`CLASSROOM_COURSE_TYPE_SET`）、1 个同物两名
    （`FOLLOW_MOTHER_ENTERTAINMENT_ID` 与 `ENTERTAINMENT_FOLLOW_MOTHER` 都是娱乐 176）。
    ⚠️ **三份重复里有两份的注释明写了「此处另写一份是为了避免循环导入」**——
    问题当时就被记下来了，只是**没有解法**：两个模块都要用同一个数，互相 import 会成环。
    常量单独成文件正是那个解法。这类「注释里写着已知缺陷」的地方，
    往后盘查时应当当成待办来读，而不是当成说明。

56. **6 处函数内 import 只为取一个常量。** `semester_handle` 有 4 处、
    `auto_schedule` 与 `growth_panel` 各 1 处，都是 `from ... class_schedule_panel import SUBJECT_ABILITY_LIST`，
    理由是「面板模块提到文件顶层会循环导入」。⚠️ 这些 import 在函数体里，
    **每次调用都要走一次导入机制**，而 `get_semester_level_change` 是成绩单结算的热路径。
    搬家后 6 处全删，改成模块顶层一次性 import 常量文件。

57. **`class_schedule_panel` 的循环导入注释本身也过期了。** 原文写「这三个模块在自己的模块顶层
    反向 import 本模块（取 `WEEK_NAME` 等共用常量）」。搬家后 `growth_panel` 与
    `schedule_template_panel` 已不再 import 它，只剩 `course_select_panel` 为取
    `get_period_time_text()` 这个**函数**而 import。环还在，但理由变了，注释照实改写。

58. **分组按「谁在用」而不是「原来在哪个文件」。** 譬如 `MALE_ONLY_ABILITY_ID`、
    `SEX_CLASS_ABILITY_LIST`、`PRENATAL_SUBJECT_LIST` 原本分居三个文件，
    注释各自解释了同一件事——为什么不含 76 腰技。归到「科目」一组后，
    第一条写清楚、后两条引用它，重复的解释才消得掉。

59. **三对该相等的常量改为派生，从结构上杜绝漂移。**
    `WEEK_DAY_COUNT = len(WEEK_NAME)`、`CHILD_TALENT_SET = set(STAGE_TALENT_NAME)`、
    `CLASSROOM_COURSE_TYPE_SET` 由三个 `COURSE_TYPE_*` 推出。
    ⚠️ 派生要节制：只对**注释里已经写明「两者必须一致」**的那几对做，
    别把普通常量也算成表达式——常量文件的第一价值是「一眼能看见这个数是多少」。

60. **搬家不许顺手改语义。** 两条自设红线：
    ⚠️ **不给字符串加 `_()`**——`SLOT_NAME`、`COURSE_TYPE_NAME` 等原本没有翻译标记，
    加上去会改变 PO 词条集合，那是另一件事；
    ⚠️ **不搬函数内的局部常量表**——它们只服务一处，搬出去反而要跳文件读。

61. **改写必须按 token 走，不能按文本替换。** 用 `tokenize` 逐 NAME 令牌改，
    天然不碰字符串与注释。⚠️ 唯一踩到的坑是**括号式 from-import**：
    `from ... import (\n    WEEK_NAME, get_period_time_text)` 里的 `WEEK_NAME`
    前一个令牌是 `(` 而不是 `import`，被当成裸引用改成了
    `education_constant.WEEK_NAME`，写出一行语法错误。单行的
    `from ... import SUBJECT_ABILITY_LIST` 反而没事（前一个令牌正是 `import`）。
    往后做同类改写，**from-import 一律先单独处理掉，再跑令牌改写**。

62. **删定义会顺手吃掉 black 要求的两行空行。** 常量块与其后的 `def` 之间原本是两行空行，
    连块带空行一起删之后只剩一行。本机没装 black，改用「与 HEAD 版逐个 `def` 比对空行数、
    只补回变少的那些」的办法修，15 处。⚠️ 判据要排除**装饰器**（`@register_provider`
    下面的 `def` 本来就是 0 行空行）与**区块横幅**（`# ---` 三行注释块的中间两行同理），
    否则会误报一大片。

#### 单元测试结果

新增 `test_const_move.py` **28 条**，连同既有三套共 **257 条全绿**
（本轮 28 + 一期 120 + 二期 65 + 三期 44）。

本轮断言的核心只有一条，其余都围着它转：

- **114 个常量的取值搬家前后完全一致**——逐个 `git show HEAD:<文件>` 取出原定义的表达式源码，
  在受限命名空间里求值，与新文件的运行时值逐个比对。⚠️ 这是纯搬家唯一真正要证明的事，
  「能 import」「能跑」都证明不了某个数字有没有被抄错。
- **HEAD 版本确实有 114 个不同名常量、且跨文件同名重复正好是那 2 个**——
  反向锁住基线，免得日后有人加了常量却不更新这条断言还以为它在保护自己。
- **13 个模块里一个模块级常量都不剩**、**全仓库没有裸引用与 `<模块>.常量` 的旧写法**、
  **没有因搬家而变成死引用的 import**（放过带 `noqa: F401` 的副作用导入）。
- 派生关系四条各断言一次；性格倾向的正负顺序两表一致；腰技 76 不在任何女儿可选的科目表里。

#### 尚未覆盖的验证

- 游戏内没有跑过：本轮不改任何行为，风险集中在 import 期，
  而 13 个教育模块 + 子系统外 5 个引用方的导入都已在无头环境里实跑过。
- `education_constant` 依赖 `official_event_handle`，若日后公务事件系统在**模块顶层**
  反向 import 教育系统，这个环会立刻炸在 import 期。⚠️ 目前它只在函数内 import
  （`official_event_handle.py:128`，带 `noqa: F401` 的注册用副作用导入），
  那条注释里也写明了理由。
- 本机没有 black，新文件与改动文件的格式只按「与 HEAD 比对空行数」这一条修过，
  未跑过完整的 `black --line-length 200`。

**2026-09-08 第八轮（与方案 §9.7 成对）：常量改为从配置现算，字符串接入翻译api**

紧接第七轮。集中之后再做两件事：能从配置推出来的不写死，要给玩家看的一律过翻译。

#### 实际改动

| 文件 | 类型 | 实际改动 |
| --- | --- | --- |
| `Script/System/Education_System/education_constant.py` | 改 | 三张科目表改为按 `ability_type` 现算；阶段名与性格倾向名改读 Talent.csv；46 处显示字符串接入 `_()`；新增「未初始化就导入」的守卫 |
| `Script/System/Education_System/auto_schedule.py` | 改 | `get_auto_subject_list()` 不再自己算一遍，直接取 `FEMALE_SUBJECT_LIST` 的副本 |
| `Script/System/Education_System/baby_growth_handle.py` | 改 | 两处跟着 `PRENATAL_SUBJECT_LIST` → `FEMALE_SUBJECT_LIST` 改名 |
| `update.log` | 改 | v0.67 段追加 调整 1 条、修正 1 条 |
| `plan_22_生长养成系统_一期_方案.md` | 改 | 新增 §9.7 |
| `plan_22_生长养成系统_一期_实施步骤与记录.md` | 改 | 新增本节 |

#### 实施中发现的偏离（§9.7，编号接 62 往下）

63. **按 `ability_type` 筛科目会多筛出一个 90 隐蔽。** 类型5（技术）里除了 70~77 八门性技，
    还有一个隐蔽——它是隐奸系统的熟练度，不是能开课教的科目。
    ⚠️ 只按类型筛会让课表里冒出一门「隐蔽课」，实操课也会把它列进主修。
    立 `NOT_SUBJECT_ABILITY_SET = {90}` 显式排除并写明理由，**不用 `cid < 90` 这类边界条件**——
    那种写法挡不住下一次往类型5里加非科目的能力。
    ⚠️ 这条也说明「改为从配置现算」不是无脑替换：**先要确认那一维在配置里真的存在**。

64. **`PRACTICE_SUBJECT_SET` 推不出来，只能继续列举。** Ability.csv 没有「是不是动手类」这一维。
    注释里写明它是例外，免得下一个人以为漏改了。同理 `CHILD_TALENT_ID_LIST` 的四个id 也写死：
    Talent.csv 里 101~104 的类型都是「身体素质」，与其他几十个身体素质并无区别，按类型筛不出来。

65. **三张科目表其实是一条链，此前各算各的。** 理成
    `SUBJECT_ABILITY_LIST` → `MALE_ONLY_SUBJECT_SET` → `FEMALE_SUBJECT_LIST` → `SEX_CLASS_ABILITY_LIST`。
    ⚠️ 顺带发现 `auto_schedule.get_auto_subject_list()` 与 `PRENATAL_SUBJECT_LIST`
    **算的是同一个东西**（全部科目去掉腰技），只是一个叫「自动排课能排的」、一个叫「胎教覆盖的」。
    改名为 `FEMALE_SUBJECT_LIST`（女儿学得了的科目）后两处共用一张。

66. **`MALE_ONLY_ABILITY_ID = 76` 改成集合。** 从 `sex_need == 0` 现算出来的本来就是一个集合，
    写成单个 id 等于假定「男性专属科目永远只有一门」。

67. **给硬编码中文包 `_()`，不如直接读配置。** 素质名走 `config_talent[id].name` 时**自带翻译**——
    `game_config` 载入时对所有 `name` 列跑过 `get_text._()`（`game_config.py:536`），
    PO 里早有 `婴儿 → Baby`。⚠️ 因此这类现取的名字**绝不能再包一层 `_()`**，包了反而对不上词条。
    这条得写进注释，否则下一个人按「字符串就包 `_()`」的规律一扫就会包上去。

68. **有三处 `_()` 不是体例问题，是活BUG。** `EDUCATION_ZONE_NAME`、`PRESET_TEMPLATE_SLOT_NAME`、
    `PE_PLACE_DATA` 的键都不是拿来显示的，是拿去和**翻译过的**配置/场景数据比对的。
    写死中文在非中文语言下分别导致：教育区成长加成整个失效、四套预设日程模板全部套用失败、
    体育课永远找不到上课地点。⚠️ **判断一个字符串该不该翻译，看的不是它长什么样，
    而是它要和谁比对**——同一个文件里 `Class_Room`（场景标签）、`通用1`（事件uid）、
    `GROWTH_REPORT_PREV`（面板哨兵）就一个都不能包。

69. **场景名走的是 pickle 缓存，翻译只在冷构建那一次生效。** `map_config.init_map_data()`
    有缓存就直接 `pickle.load`，只有冷构建才走 `get_text._(SceneName)`。
    ⚠️ 于是**场景名跟的是「缓存生成时的语言」而不是当前语言**——我第一次验证时正是撞在
    「缓存中文、会话英文」这个状态里，一度以为自己把体育课改坏了。
    改用「照 `map_config.py:64` 那行的写法直接对 Scene.json 求值」验证，
    冷构建下 `scene_name` 就是 `'Stake Room'`，与 `_("木桩房")` 一致。
    ⚠️ **验证一个「载入期做的转换」，不能只看缓存里的成品**。
    这是整个游戏的既有问题（改语言不重建缓存则全岛地名不变），不是本表独有，记在这里备查。

#### 单元测试结果

`test_const_move` 由 28 条扩到 **56 条**，连同既有三套共 **285 条全绿**。

新增断言的重点：

- **现算的结果与改造前写死的值逐个相等**：科目18门、女儿可学17门、实操课7门、
  阶段名四个、性格倾向名四对，全部与硬编码版本比对通过。
- **90 隐蔽确实是类型5、且确实被排除**——正反两面都断言，免得哪天有人把排除表删了还以为没事。
- **`_()` 的正反覆盖**：用 AST 走每个常量的取值表达式，分出「裸字符串」与「`_()` 包着的字符串」，
  11 个必须全包、6 个必须一个都不包（场景标签、事件uid、面板哨兵、排版空白）。
  ⚠️ 反向那半更要紧：正向漏了只是不翻译，反向误包会直接写坏数据键。
- **现取的名字没有被再包一层 `_()`**。

#### 尚未覆盖的验证

- 新加的 46 处 `_()` 需要跑一次 `buildpo.py`（扫全仓库 `.py` 交给 `xgettext`）才会进 PO，
  本机没有 `xgettext`，未跑。在跑通之前，这批词条在英文模式下仍显示中文——
  与改造前一模一样，不构成回退。
- 英文模式的实机验收：本轮只在无头环境里比对了键能否对上，没有真开一局英文游戏。
- `NOT_SUBJECT_ABILITY_SET` 目前只有 90 一项，是照当前 Ability.csv 盘出来的；
  日后往类型4/5 里加非科目的能力时必须同步。
