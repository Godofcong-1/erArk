# Plan 22（一期·实施步骤与记录）：教育区改建 + 课表 + 六种课型 + 上课闭环

> 本文件是 `plan_22_生长养成系统_一期_方案.md`（下文简称"方案"）的**实施步骤清单与过程记录**。
> 需求背景、现状调查、设计决策、数据结构定义、界面设计、风险与范围外事项一律以方案与
> `plan_22_生长养成系统_总纲.md`（下文简称"总纲"）为准；本文件只写"怎么做、怎么验、怎么回滚"，
> 实施过程与结果记入 §6。

- 状态：实施中（1a 功能闭环；§2.1 教育区改建已完成，2026-09-06）
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
| `growth_handle.py` | 能力成长计算（速度曲线、教育区加成、上限判定） |
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
- [ ] 学期末出成绩单 flag，用「检查成绩单」指令能查看
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

**与方案的偏离**：

1. **房间名用汉字数字（理论教室一~六），而非方案原写的阿拉伯数字（理论教室1~6）。** 原因：ASCII 数字属 ASCII 度量族（字号 20 下 14px），与框线族（13px）不通约，每间教室的按钮都会让所在行漂移 1px，6 间累计 6px，`tools/map_aa_check.py` 会判失败。汉字数字恒为 2U，零漂移。方案 §3.10 已同步更新。
2. **场景数是 18 而非方案预估的 15。** 方案的「9 增至 15」只数了功能房间，实际目录含入口 `0`、走廊与男女洗手间。不影响任何设计。
3. **`WorkType.csv` 的 `place` 列不是功能性依赖，只是显示文案。** 方案 §7-1 原写「唯一必改」，实测为「唯一需要同步的显示文案」——`handle_npc_ai.py:359` 是 `place`(按场景名) **或** `place_tag`(按标签) 的短路判断，标签命中即成立；移动到工作地点走 `auto_ai_move`(561) → `StateMachine/default.py:441` 的 `place_data["Class_Room"]`，与 `place` 无关。`place` 的实际读取点只有 `debug_panel.py:2089` 与 `manage_basement_panel.py:1230` 两处显示。方案 §7-1 与总纲 §2.4 已同步更新。
4. **大礼堂的 `Scene_Img` 取「会议室」**：`image/场景/` 下没有礼堂图，会议室是最接近的现成资源。

**已知限制**：

- ⚠️ **老存档读出来仍是旧地图**。`save_handle.py:496~516` 只在场景增删或 `scene_tag`/`scene_img`/`room_area` 变化时才刷新存档里的 `map_data`——本次确实是场景增删，理论上会刷新，但**必须用老存档实机验证**（列在 §4.2）。
- 未解锁教室的门禁（`Facility_open.csv`）尚未配置，属步骤 §2.3，本步未做——当前 10 间教室全部可进入。

### 6.2 实施前的假设复核

对总纲 §2 与方案 §2 的现状调查逐条复核：

| # | 假设 | 复核结果 |
| --- | --- | --- |
| 1 | `Class_Room` 只有 6 处引用，其中 4 处沿用标签即自动适配 | ✅ 确认。且第 5 处（`WorkType.csv` 的 `place` 列）实测也只是显示文案，见 §6.1 偏离 3 |
| 2 | `handle_instruct.py:553~573` 与 `StateMachine/default.py:2648` 是平行实现 | ✅ 确认（读码核对，改造待步骤 §2.6/§2.7） |
| 3 | `StateMachine/default.py:441` 的 `place_data` 会自动收录新教室 | ✅ 确认。重建缓存后 `place_data["Class_Room"]` 含全部 6 间理论教室，`Practice_Room` 3 间、`Auditorium` 1 间 |
| 4 | `Facility_effect.csv` 的教育区 `effect` 列在代码中从未被读取 | |
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

### 6.4 尚未覆盖的验证

（留给用户的游戏内清单）

### 6.5 第二轮追加调整实施记录

（与方案 §9.x 成对，每轮一节，附回归测试计数）
