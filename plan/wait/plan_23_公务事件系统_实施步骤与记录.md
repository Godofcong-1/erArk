# Plan 23（实施步骤与记录）：公务事件系统

> 本文件是 `plan_23_公务事件系统_方案.md`（下文简称"方案"）的**实施步骤清单与过程记录**。
> 需求背景、现状调查、设计决策、数据结构定义、风险与范围外事项一律以方案文档为准；
> 本文件只写"怎么做、怎么验、怎么回滚"，实施过程与结果记入 §6。

- 状态：**已实施**（2026-09-07，与方案保持同步；游戏内验收待用户执行，见 §6.4）
- 适用代码快照：`plan22-growth-system @ a584096a5`
- 实施前提：先通读方案与 `plan_22_生长养成系统_总纲.md` §2；实施中发现与方案冲突的事实，
  **先更新方案再动代码**

---

## 1. 改动文件清单

| 文件 | 类型 | 改动 |
| --- | --- | --- |
| `data/official_event/{婴儿,幼女,萝莉,通用}.csv` | 移动+改 | 由 `data/growth_event/` 迁入，表头加 3 列，事件扩到 250 条 |
| ~~`data/official_event/{生产,医疗,人事,后勤,外勤,装备}.csv`~~ | 不做 | 部门事件的内容本轮不写，留到后续（架构已就位，加 csv 即可） |
| `buildconfig.py` | 改 | `growth_event` 编译分支改为 `official_event`，产物改 `data/Official_Event.json` |
| `auto_build_config.py` | 改 | 同上镜像一份（⚠️ 不改则跑 `game.py` 不会重建） |
| `Script/Config/config_def.py` | 生成 | 由 `buildconfig.py` 重生成，`Growth_Event` → `Official_Event` |
| `Script/Config/game_config.py` | 改 | `load_official_event()` + 三个索引，替换原 `load_growth_event()` |
| `Script/Core/game_type.py` | 改 | `Rhodes_Island.official_event_queue` / `official_event_history`（方案 §4.2） |
| `Script/Core/save_handle.py` | 改 | 旧档 `growth_event_queue` 逐项搬运并补 `department`；新字段回填 |
| `Script/System/Official_Event_System/__init__.py` | 新增 | 空包 |
| `Script/System/Official_Event_System/official_event_handle.py` | 新增 | 通用入队/节流/清理/出队/选项判定/结算/履历 + 提供者注册表 |
| `Script/System/Official_Event_System/official_event_panel.py` | 新增 | 通用弹出与决断界面（由 `growth_event_panel.py` 迁移泛化） |
| `Script/System/Official_Event_System/ri_value.py` | 新增 | 罗德岛全局数值统一读写口（方案 §4.3） |
| `Script/System/Education_System/growth_event_handle.py` | 改 | 瘦身为养成分类的候选提供者 + 事件抬头，注册到公务事件系统 |
| `Script/System/Education_System/growth_event_panel.py` | 删除 | 功能并入 `official_event_panel.py` |
| `Script/System/Education_System/growth_handle.py` | 改 | `GROWTH_VALUE_STAGE_PROGRESS = 3`（方案 §4.4） |
| `Script/System/Education_System/growth_panel.py` | 改 | 履历栏与待处理栏改读新队列/新配置 |
| `Script/Design/handle_premise/__init__.py` | 改 | CVP 主体判别加 `RI` 分支（方案 §3.6） |
| `Script/Design/handle_premise/handle_premise_other.py` | 改 | 两个新前提的实现（方案 §4.5） |
| `Script/Core/constant_promise.py` | 改 | 两个新前提常量 |
| `Script/Core/constant_effect.py` + `Script/Settle/default.py` + `data/csv/Behavior_Effect.csv` | 改 | 部门样例事件用的 2~3 个纯数字结算函数 |
| `Script/Settle/past_day_settle.py` | 改 | 每日入队入口换成 `check_new_day_official_event()` |
| `Script/System/Instruct_System/handle_instruct.py` | 改 | `handle_official_work` 改调 `official_event_panel.handle_official_event_queue` |
| `Script/System/Pregnancy_System/pregnancy_handle.py` | 改 | 毕业典礼入队改调新接口 |
| `tools/official_event_check.py` | 新增 | CSV 校验工具（方案 §6-8） |
| `tools/ArkEditor/game_type.py` | 改 | 新增 `OfficialEvent` 数据类 |
| `tools/ArkEditor/load_csv.py` | 改 | `load_official_event_dir()` / `save_official_event_csv()` |
| `tools/ArkEditor/cache_control.py` | 改 | `now_premise_target` / `now_effect_target` 间接层 |
| `tools/ArkEditor/ui/official_event_list.py` | 新增 | 左列表（按部门+文件分组） |
| `tools/ArkEditor/ui/official_event_edit.py` | 新增 | 右表单（基本字段 + 4 个选项块） |
| `tools/ArkEditor/ui/menu_bar.py` | 改 | 「公务事件」菜单块 |
| `tools/ArkEditor/main.py` | 改 | 页面装配 + 信号接线 |
| `tools/ArkEditor/ui/{premise_menu,CVP_menu,CVE_menu,effect_menu,item_premise_list,item_effect_list}.py` | 改 | 写入点改走间接层；CVP/CVE 下拉补 `Growth` 与 `RI` |
| `tools/ArkEditor/function.py` | 改 | token 反解链补 `Growth` 与 `RI` |
| `tools/ArkEditor/csv/{Premise.csv,Facility.csv}` | 改/新增 | 同步两个新前提；新增部门参照表 |
| `plan/wait/plan_22_*` 三份 | 改 | 事件相关章节改为指向本 Plan |
| `update.log` | 改 | 按 `update-changelog` 体例补条目 |

---

## 2. 详细改动步骤

> 数据结构、编号表、常量取值一律**以方案 §4 为准**，此处不重复定义。

### 2.1 架构迁移（先跑通空壳，再灌数据）

1. 新建 `Script/System/Official_Event_System/`，把 `growth_event_handle.py` 里**与养成无关**的部分
   （前提判定、入队/清理/出队、选项列表、effect 分发、履历写入）搬进 `official_event_handle.py`
2. `growth_event_panel.py` 整体搬成 `official_event_panel.py`，事件抬头改为**按部门取**：
   有主体角色时用提供者给的抬头函数，无主体时画「【公务事件·<部门名>】」
3. `growth_event_handle.py` 只留养成专属：女儿遍历、兄弟姐妹/同学反查、阶段桶、抬头，
   用 `@official_event_handle.register_provider(15)` 注册
4. `git mv data/growth_event data/official_event`，四个 CSV 表头加 3 列（`department`/`subject`/`sub_key`），
   `stage` 列改名 `sub_key`，已有 18 行补 `department=15`、`subject=1`
5. 两处编译分支改名 → `data/Official_Event.json`；`game_config.py` 换 loader 与三个索引
6. `game_type.py` / `save_handle.py` 的队列改名与搬运；`past_day_settle.py`、`handle_instruct.py`、
   `pregnancy_handle.py`、`growth_panel.py` 的调用点跟着换

⚠️ 这一步**不加任何新功能**，做完先跑一次构建 + 无头冒烟，确认 18 条事件仍能入队、弹出、结算。

### 2.2 全局数值通道

1. `ri_value.py` 写 `get_ri_value()` / `change_ri_value()`（编号表见方案 §4.3），只读项静默忽略
2. `official_event_handle.handle_effect_text` 加 `CVE_RI_` 分支（在 `CVE_` 判断之内、`A1/A2` 之前）
3. `handle_premise/__init__.py` 的 `handle_comprehensive_value_premise` 主体判别加 `RI` 分支
   （不解析角色，直接取值比较），⚠️ 放在 `A1/A2/A3` 判断链的最前
4. 给部门样例事件写 2~3 个纯数字结算函数（照 `default.py:6119` 的形态）

### 2.3 触发规则

1. `judge_event_can_enqueue` 的履历守卫改为**无条件**；无主体事件查 `official_event_history`
2. 入队改为按提供者分别取候选：养成提供者按女儿逐个判定（`shuffle` + 概率 + 每孩上限），
   部门提供者汇总后按 `DEPARTMENT_EVENT_DAILY_MAX` 抽取；总量受 `OFFICIAL_EVENT_DAILY_MAX` 约束
3. `GROWTH_VALUE_STAGE_PROGRESS = 3` 与两个新前提
4. `clean_official_event_queue` 补 `partner_id` 有效性校验（无效则置 0，不丢事件）

### 2.4 编辑器

按方案 §3.7 与 §2.4 的"四个缺陷不能继承"逐条落实。顺序：
数据类 → 读写函数 → 左列表 → 右表单 → 间接层改造 → 菜单与装配 → CVP/CVE 下拉与反解链。

### 2.5 内容撰写

先写 `tools/official_event_check.py` 并对迁移后的 18 条跑通，再按
婴儿(50) → 幼女(70) → 萝莉(70) → 通用(60) → 六部门样例的顺序写，**每批约 10 条就跑一次校验**，
每个文件写完跑一次构建 + 无头冒烟再进下一个文件。内容配额与口径见方案 §5。

---

## 3. 构建与缓存

```bash
.conda\python.exe buildconfig.py   # 事件表结构与目录都变了，必跑
git checkout -- data/po/           # 本机无 xgettext/polib，buildconfig 重写的 PO 要还原
```

`buildpo.py` / `buildmo.py` **不需要跑**：event 的 PO 写出被 `BUILD_TALK` 门控，
`buildmo.py` 也不编译 `erArk_event`，中文环境直接显示 CSV 原文。
本 Plan 不涉及地图改动，不需要删场景缓存。
⚠️ `data/Official_Event.json` 是未纳入版本管理的构建产物（`.gitignore` 的 `data/*.json`）。

---

## 4. 验证清单

### 4.1 单元测试（实施方执行，按 `headless-game-test` 模式 A）

- [ ] 构建产物：条数正确，`by_department` / `by_sub_key` 分桶正确，uid 带文件名前缀
- [ ] 遍历全部事件：前提判定不抛异常；最坏情况（好感/信赖为 0）下每条至少 1 个可选选项
- [ ] 遍历全部选项：结算跑通，且结算前后 `character_data.ability` 不变（口径 33）
- [ ] 不重复触发：角色 A 处理过事件 X 后不再入队 X；角色 B 仍能入队 X
- [ ] 供需模拟：单女儿跑完 30+60+60 个可游玩日，四个养成池消耗率均 ≤80%，全程无重复 uid
- [ ] 并发入队：3 个女儿时每日入队 ≤ 全局硬顶、每个女儿每天 ≤1 条
- [ ] `RI` 通道：`CVP_RI_` 真假两侧；`CVE_RI_` 加减；资源不为负；`Work`/`Eff` 的 clamp 边界；只读项写入被忽略
- [ ] 部门事件：无主体事件（测试内注入）能入队、弹出、结算，履历写进 `official_event_history`
- [ ] 新前提与 `Growth|3` 的边界值
- [ ] 存档兼容：旧档的 `growth_event_queue` 搬进 `official_event_queue` 并补上 `department`
- [ ] 回归：plan_22 三期的 79 条断言按新口径改写后全绿
- [ ] `tools/official_event_check.py` 全绿

### 4.2 编辑器测试（实施方执行）

- [ ] 往返：读取目录 → 改一条 → 保存 → 再读取，内容一致
- [ ] 保存后的文件：5 行表头完整、UTF-8 无 BOM、全 CRLF、字段数不变
- [ ] 前提/结算选择器写进的是当前选项块，不污染口上/事件的全局数据
- [ ] 切页后旧控件不残留

### 4.3 游戏内整体测试（由用户执行）

- [ ] 处理公务时事件正常弹出、置灰选项带原因、排版可读（Tk 与 `web_draw=1` 各看一次）
- [ ] 单女儿约一两天一条；多养几个女儿后每天明显变多但不失控；同一孩子不遇到重复事件
- [ ] 往 `data/official_event/` 加一张部门 csv 后能被派发与结算（部门内容本轮未写）
- [ ] 旧存档载入不报错，养成总览与履历栏正常
- [ ] 在 ArkEditor 里新建一条公务事件，跑构建后游戏内能触发

---

## 5. 回滚

| 单元 | 回滚方式 |
| --- | --- |
| 编辑器改造 | 删除两个新 ui 文件、还原 6 个选择器文件与 `main.py`/`menu_bar.py`（与运行时无关，可独立回滚） |
| 内容扩容 | `git checkout -- data/official_event/`，重跑 `buildconfig.py` |
| 全局数值通道 | 删 `ri_value.py`、还原 `handle_effect_text` 与 `handle_premise/__init__.py` 的两处分支 |
| 架构迁移 | **整体回滚**（模块、数据目录、队列字段、调用点是一个整体），`git revert` 该提交后重跑 `buildconfig.py` |

---

## 6. 实施过程记录

### 6.1 实际改动

| 文件 | 类型 | 实际改动 |
| --- | --- | --- |
| `data/official_event/{婴儿,幼女,萝莉,通用}.csv` | 移动+改 | 由 `data/growth_event/` 迁入并改为 28 列，事件 18 → **250 条**（50/70/70/60） |
| `buildconfig.py` / `auto_build_config.py` | 改 | `growth_event` → `official_event` 全量改名，产物 `data/Official_Event.json` |
| `Script/Config/config_def.py` | 生成 | `Growth_Event` → `Official_Event`（28 字段） |
| `Script/Config/game_config.py` | 改 | `load_official_event()` + `config_official_event` / `_by_department` / `_by_sub_key` 三个索引 |
| `Script/Core/game_type.py` | 改 | `official_event_queue`（元素加 `department`）与 `official_event_history` |
| `Script/Core/save_handle.py` | 改 | 旧档 `growth_event_queue` 逐项搬运并按 uid 补 `department`，查不到配置的直接丢弃 |
| `Script/System/Official_Event_System/` | 新增 | `official_event_handle.py`（约 540 行）、`official_event_panel.py`（约 180 行）、`ri_value.py`（约 190 行） |
| `Script/System/Education_System/growth_event_handle.py` | 改 | 瘦身为教育区的候选提供者（含 capacity 与抬头两个注册） |
| `Script/System/Education_System/growth_event_panel.py` | 删除 | 并入 `official_event_panel.py` |
| `Script/System/Education_System/growth_handle.py` | 改 | `GROWTH_VALUE_STAGE_PROGRESS = 3` + `get_stage_progress()` |
| `Script/System/Education_System/growth_panel.py` | 改 | 履历栏读新配置、待处理栏改调 `get_official_event_queue_count()` |
| `Script/Design/handle_premise/__init__.py` | 改 | CVP 加 `RI` 主体分支 + 新增可复用的 `judge_value_by_operator()` |
| `Script/Design/handle_premise/handle_premise_other.py` | 改 | `self_mother_available` / `self_have_any_course` |
| `Script/Core/constant_promise.py` | 改 | 上述两个前提常量 |
| `Script/Core/constant_effect.py` / `Script/Settle/default.py` | 改 | 新增结算 id **3002**（接收招募干员）与 **3003**（生成临时外勤委托） |
| `Script/Settle/past_day_settle.py` | 改 | 每日入队改调 `check_new_day_official_event()` |
| `Script/System/Instruct_System/handle_instruct.py` | 改 | 处理公务改调 `official_event_panel.handle_official_event_queue()`（仍在通用结算之前） |
| `tools/official_event_check.py` | 新增 | 校验工具（约 470 行），含 12 项硬校验与统计报告 |
| `tools/ArkEditor/game_type.py` | 改 | `OfficialEvent` 数据类（含 `to_row()`） |
| `tools/ArkEditor/load_csv.py` | 改 | `load_official_event_dir()` / `save_official_event_csv()` |
| `tools/ArkEditor/ui/official_event_list.py` | 新增 | 左列表：文件筛选、关键字搜索、右键增删复制、cid 自动分配 |
| `tools/ArkEditor/ui/official_event_edit.py` | 新增 | 右表单：基本字段 + 4 个选项块 + 前提/结算选择器接入 |
| `tools/ArkEditor/ui/menu_bar.py` / `main.py` | 改 | 「公务事件」菜单块与页面装配、信号接线 |
| `tools/ArkEditor/csv/Premise.csv` | 改 | 同步两个新前提 |
| `plan/wait/plan_22_*` 三份 | 改 | 三期两份加指向本 Plan 的说明；总纲的口径 16、32 标注为已被本 Plan 推翻/改写 |

**与方案的偏离**：

1. **列数是 28 不是 29**：`stage` 改名 `sub_key` 是重命名而非新增，净增只有 `department` 与 `subject` 两列。方案 §4.1 已改。
2. **编辑器不改那 6 个选择器文件**：方案原打算在 `cache_control` 加 `now_premise_target` / `now_effect_target`
   间接层并改 15 处写入点。实际改用**临时载体**（`official_event_edit.SelectorShim`）：
   打开弹窗前把 `now_event_data` / `now_select_id` / `now_edit_type_flag` 与两个列表面板换成载体，
   关闭后还原并把结果写回输入框。既有文件**一行未改**，风险与改动量都小得多。
3. **`tools/ArkEditor/csv/Facility.csv` 没有新增**：部门名直接从所选目录的同级 `../csv/Facility.csv` 读，
   与游戏本体永远同步，省掉一份会过期的快照。
4. **CVP/CVE 下拉与 `function.py` 反解链未补 `Growth` / `RI`**：新页面的前提与结算是可直接手写的输入框，
   两个构造器仍可用（写出来的 token 一样有效），补下拉属于锦上添花，留待后续。
5. **新增 `judge_value_by_operator()`**：`RI` 前提不走角色主体那条链，需要一个独立的比较函数；
   顺手把它写成可复用的公共函数，而不是在 RI 分支里再抄一遍六个运算符。
6. **跨阶段事件用 `CVP_A1_T|101_E_0` 排除婴儿**（方案 §3.8 已补写）：不新增前提，直接用素质判定。
7. **通用池权重压到 3~5**：方案只写了口径，实测统计报告显示迁移进来的 3 条旧事件还是 6~10，已统一压到 ≤5。
8. **补了一轮倾向配平**：统计报告显示羞耻/孤僻/懒散侧的选项太少（婴儿池一度是开放 +22 / 羞耻 −1），
   给 36 处「退让、回避、代劳」类选项补上了负向倾向与对应提示。

9. **部门事件的内容本轮一条不写**（用户在收尾时确认）：六个部门的样例 csv 已删除，只保留架构、默认提供者与两个结算函数（3002/3003）。
   无头测试改为**运行时注入**一条制造加工区的无主体事件来验证这条路径——等价于往目录里丢一张 csv，反而更直接地证明了「新增部门不用改代码」。

**已知限制**：

1. **`create_temp_commission` 会写盘**：结算 id 3003 复用的这个函数会把新委托**追加进 `data/csv/Commission.csv`**，
   所以它的描述里换行必须写成 `\n` 转义、且不能有英文逗号（实施中曾因真换行把该 CSV 撑断，已修）。
   无头测试里必须把它换成桩。
2. **PO 词条未生成**：本机没有 `xgettext` / `polib`，`buildconfig.py` 重写的 PO 已按惯例 `git checkout -- data/po/` 还原。
   中文环境直接显示 CSV 原文，其他语言的词条要在有工具链的环境里补跑。
3. **编辑器页面未在真实 GUI 里点过**：控件构造、填表、筛选、载体机制与读写往返都有无头测试覆盖，
   但"打开程序点一遍"要留给用户（§6.4）。

### 6.2 实施前的假设复核

| # | 假设 | 复核结果 |
| --- | --- | --- |
| 1 | 部门可直接复用 `Facility.csv` 中 `type == -1` 的区块 | ✅ 成立，21 个部门，`manage_basement_panel.py:186-192` 就是这么枚举的 |
| 2 | CVE/CVP 只有角色主体，够不着罗德岛全局数值 | ✅ 成立，因此另开 `RI` 主体并只在公务事件自己的分发里解析 |
| 3 | 纯数字结算 id 能写全局 | ✅ 成立，`default.py:6119` 等多处先例 |
| 4 | 外勤委托编辑页可作为新页面的范式 | ✅ 成立，但它的四个缺陷（不落盘 / 不备份 / 不设 flag / 混合行尾）都没有继承 |
| 5 | 前提/结算选择器要靠改 6 个文件才能复用 | ❌ 不成立，用临时载体顶替全局即可，既有文件一行未改（偏离 2） |
| 6 | 迁移后旧 uid 不变，旧档履历仍然有效 | ✅ 成立，四个养成 CSV 文件名保持原样，uid 仍是 `婴儿1`…`通用5` |

### 6.3 单元测试结果

`headless-game-test` 模式 A，三组脚本合计 **102 条断言全部通过**：

| 脚本 | 断言 | 覆盖 |
| --- | --- | --- |
| 主测试 | 79 | 配置与分桶 8｜`RI` 通道 14｜阶段进度 6｜新前提 3｜不重复触发 7｜入队节流 8｜出队与结算 10｜队列清理与旧档 3｜毕业典礼与面板 7｜部门事件 13（**运行时注入**一条无主体事件，等价于往目录里丢一张 csv） |
| 供需模拟 | 5 | 单女儿跑完 30+60+60 个可游玩日：无重复 uid，四池消耗率 50.0% / 52.9% / 48.6% / 76.8% |
| 编辑器读写 | 18 | 读目录 / 表头 / 选项块解析｜原样保存与原文件**逐字节一致**｜改一条往返｜新增事件｜无BOM+全CRLF+表头5行｜校验工具对编辑器产出的结果仍全绿 |

另：`tools/official_event_check.py --full` 对 250 条事件全绿（含条数下限与查重）。

关键实测值：事件总数 **250**（全部为教育区的养成事件，部门内容留到后续）；分桶 `{15: 250}`，
养成子桶 `{101: 50, 102: 70, 103: 70, 0: 56, 104: 4}`；最坏情况下养成通用池消耗 76.8%（盈余 23.2%），
是四个池里最紧的一个，与方案 §3.5 的推导一致。

### 6.4 尚未覆盖的验证

以下要在真实游戏与编辑器里跑（对应 §4.3 与 §4.2 的最后一项）：

- [ ] Tk 模式与 `web_draw = 1` 下的事件弹出排版
- [ ] 真实存档载入不报错，且旧档的待处理队列能搬过来
- [ ] 养几个女儿连玩数日，确认频率手感（单女儿约一两天一条、多女儿明显变多）
- [ ] 部门样例事件触发后，对应部门的数值确实变了（资源、效率、声望）
- [ ] 打开 ArkEditor 走一遍：读目录 → 改一条 → 选前提 → 保存 → 跑构建 → 游戏内触发
- [ ] 250 条养成事件的文案本身是否合口味
- [ ] PO 词条在有 `xgettext`/`polib` 的环境里补跑

### 6.5 第二轮追加调整实施记录

#### 第 1 次（2026-09-07）：后果提示统一用「好感」

用户看事件表时发现提示里的「亲密」含义不清。查证：307 个写「亲密」的选项，结算全是
`CVE_A1_F_G_N`（好感度），其中 51 个另加信赖；**没有一个**动过能力表里那个真正的「亲密」
（`Ability.csv` 的能力 32，前提系统里有 `交互对象亲密>=3` 之类的判定）。

也就是说同一个好感度，涨的时候叫「亲密」、跌的时候叫「好感」，而且「亲密」还与一项真实能力重名。
→ 把 `option_N_tip` 里的 307 处「亲密」全部改为「好感」（正文与选项文本里的叙述用词不动，实测也没有）。

改后提示词分布：好感＋ 334｜好感＋＋ 138｜好感小降 97｜好感下降 54｜对方好感 44｜信赖 140｜照料 144｜倾向 680。
回归：校验工具 250 条全绿，三套无头测试 79 / 5 / 18 仍全绿。
`update.log` 与三期方案里那两处「亲密＋」的举例也一并跟着改了。

