# Plan 23（方案）：公务事件系统

> 本 Plan 拆分为两个文件：**本文件为纯方案**（需求、现状调查、设计决策、数据结构、
> 风险、范围外）；具体的逐文件改动步骤、构建、验证清单、回滚与实施过程记录见
> `plan_23_公务事件系统_实施步骤与记录.md`（下文简称"实施文档"）。
>
> 本 Plan **接管** Plan 22 三期的养成事件系统：三期建成的
> `Script/System/Education_System/growth_event_*` 与 `data/growth_event/` 在本 Plan 中
> 被泛化为通用的公务事件系统，养成事件成为它的一个部门分类。
> 三期的方案与实施记录不再更新事件相关内容，只留一行指向本 Plan。

- 状态：**已实施**（v1，2026-09-07；实施中的设计修订已合并进正文，逐条差异见实施文档 §6.1）
- 来源：用户需求 → "养成事件的系统需要扩展为一个单独的系统，即公务事件系统，在处理公务的时候
  需要玩家做出判断和选择，并产生对应影响的系统。养成事件是公务事件的一个部分。公务事件还可能包括
  生产部门、医疗部门、人事部门、后勤部门、外勤部门、装备部门等各个部门单独的事件需要处理。
  所以需要将该事件系统扩展为一个兼容性较好的通用架构，并且在编辑器中单独适配该公务事件系统，
  用一个单独的页面来对公务事件进行编辑（可以参考对于外勤事件的编辑页面）。"
- 追加需求（规划阶段确认）：
  1. 同一个角色不再重复触发同一条事件（不同角色仍可各自触发同一条）
  2. 触发频率与女儿数量相关：每个女儿约一两天一条，女儿越多每天的事件越多，但仍有每日硬顶
  3. 养成事件扩容到"单女儿完整养成后，每个阶段池与通用池都还剩 ≥20%"的量
  4. 婴儿期住育儿室，幼女期起住自己的宿舍（既有文案的设定校正）
- 已确认的设计决策：
  - 新开本 Plan（不并入 plan_22 三期）
  - 本轮范围 = 通用架构 + ArkEditor 页面 + 养成事件迁移与扩容；**其余部门本轮不写内容**，只保证架构支持
  - 结算通道**两者都要**：常规数值走新增的 `CVE_RI_` 全局主体 token，复杂效果走纯数字结算 id
- 预计改动量：**约 30 个文件**（4 张事件 CSV + 编辑器 5 个文件 + 运行时 12 个文件 + 文档），
  事件条目由 18 条扩到 **250 条**
- 风险等级：**中**（既有系统迁移、存档字段改名、编辑器改造三处叠加）
- 适用代码快照：`plan22-growth-system @ a584096a5`
- 前置：Plan 22 一期~三期已完成

---

## 1. 目标

1. 把养成事件泛化为**公务事件系统**：一套数据形态、一条入队/出队/结算链路，服务全部门
2. 分类维度复用既有的**部门枚举**（`Facility.csv` 中 `type == -1` 的区块），不另造分类表
3. 事件结算除角色数值外，还能读写**罗德岛全局数值**（资源、声望、公务量、基地效率等）
4. ArkEditor 新增**独立的公务事件编辑页面**，一行一事件、四个选项块可视化编辑
5. 同一角色不重复触发同一事件；养成事件按女儿逐个入队，女儿越多每天的事件越多
6. 养成事件扩容到 250 条（婴儿 50 / 幼女 70 / 萝莉 70 / 通用 60），并保证 ≥20% 盈余
7. 架构上保证"新增一个部门只写 CSV 不改代码"（**部门事件的内容本轮不写**，留到后续）

**验收标准**：处理公务时能逐条弹出养成事件；往事件表里加一条任意部门的无主体事件即可被派发与结算（无需改代码）；
ArkEditor 能编辑并保存公务事件；单女儿养到成年不出现重复事件且四个池都有 ≥20% 盈余。

---

## 2. 现状调查

### 2.1 三期建成的养成事件链路（本 Plan 的改造对象）

| 环节 | 位置 |
| --- | --- |
| 数据 | `data/growth_event/{婴儿,幼女,萝莉,通用}.csv`（26 列，18 条） |
| 编译 | `buildconfig.py:473-484` 与 `auto_build_config.py:466-473`（两处镜像） |
| 运行时表 | `game_config.py:1665-1678 load_growth_event()` → `config_growth_event` / `config_growth_event_by_stage` |
| 队列 | `game_type.py:1270 Rhodes_Island.growth_event_queue`；旧档回填 `save_handle.py:560-562` |
| 入队 | `past_day_settle.py:107 check_new_day_growth_event()`（角色刷新之后） |
| 出队 | `handle_instruct.py:1849-1857 handle_official_work()`（在通用结算**之前**） |
| 逻辑 | `Script/System/Education_System/growth_event_handle.py`（530 行） |
| 界面 | `Script/System/Education_System/growth_event_panel.py`（182 行） |
| 履历 | `CHILD_GROWTH.event_history`（`game_type.py:394`），`settle_growth_event_option:529` 写入 |

### 2.2 部门枚举已经存在

`data/csv/Facility.csv` 里 `type == -1` 的区块行就是部门，`manage_basement_panel.py:186-192`
即以此枚举全部门；`WorkType.csv` 的 `department` 列与其名称严格对齐。可直接复用：

| cid | 部门 | cid | 部门 |
| --- | --- | --- | --- |
| 0 | 控制中枢 | 11 | 贸易区 |
| 1 | 动力区 | 12 | 制造加工区 |
| 2 | 工程部 | 13 | 访客区 |
| 3 | 仓储区 | 14 | 机库 |
| 4 | 宿舍区 | 15 | 教育区 |
| 5 | 生活娱乐区 | 16 | 疗养庭院 |
| 6 | 医疗部 | 17 | 大浴场 |
| 7 | 文职部 | 18 | 甲板 |
| 8 | 科研部 | 19 | 关押区 |
| 9 | 训练场 | 20 | 保卫科 |
| 10 | 图书馆 |  |  |

### 2.3 全局数值的写入通道（关键约束）

- **CVE/CVP 只有角色主体**：`settle_behavior.py:729-742` 只认 `A1/A2/A3`，属性映射
  `:754-769` 全部是 `getattr(character_data, ...)`。**无法读写 `cache.rhodes_island`**。
- **纯数字结算 id 可以写全局**：`Behavior_Effect` 的数字 id → `constant.settle_behavior_effect_data[id]`，
  函数体内可任意读写 `cache.rhodes_island`。现成例子：`Script/Settle/default.py:6119`（写 `office_work`）、
  `:6418`（写招募进度）、`:7124`（写设施损坏）、`:7085`（写 `materials_resouce`）。
- 养成事件的 `handle_effect_text:468-510` **已经**支持"CVE 串 + 纯数字 id"两分支。

### 2.4 外勤委托的编辑页面（编辑器改造的参照物）

| 环节 | 位置 |
| --- | --- |
| 菜单入口 | `tools/ArkEditor/ui/menu_bar.py:78-101` |
| 页面装配 | `tools/ArkEditor/main.py:549-592 load_commission_data()`，信号接线 `:632` |
| 左列表 | `tools/ArkEditor/ui/commission_list.py`（搜索、右键增/复制/删、拖拽排序） |
| 右表单 | `tools/ArkEditor/ui/commission_edit.py:203-251`（`QFormLayout`，12 字段） |
| 读写 | `tools/ArkEditor/load_csv.py:261 load_commission_csv` / `:292 save_commission_csv` |

该页面的**四个缺陷不能继承**：① 右键增删/拖拽不落盘；② loader 不调 `backup_file()`；
③ loader 不设 `now_edit_type_flag`，在该页按 Ctrl+S 会覆盖上一个口上/事件文件；
④ `save_commission_csv` 表头用 `f.write(text+"\n")`、数据行用 `DictWriter`（CRLF），**产出混合行尾**。

编辑器**没有页面注册表也没有标签页**：所谓页面就是主窗口那一个 `QGridLayout`
加一组 `add_grid_*_layout()`，靠 `cache_control.now_edit_type_flag` 切换；
且 `main_layout` 从不 `removeWidget`，切页时旧控件会叠在同一格上。

前提/结算选择器（`premise_menu.py` / `CVP_menu.py` / `CVE_menu.py` / `effect_menu.py` /
`item_premise_list.py` / `item_effect_list.py`）都把结果**直写**进 `now_talk_data` / `now_event_data`
两个全局之一，靠 `now_edit_type_flag` 二选一；`CVE_menu.ok` 只在 flag==1 时写。

### 2.5 已知陷阱

| # | 陷阱 | 依据 |
| --- | --- | --- |
| 1 | CSV 空单元格在构建时被**删 key**，运行时必须 `.get()` | `buildconfig.py:187-189` |
| 2 | `stage`/`weight` 写成非数字 → 事件进字符串键的桶，**永不触发且不报错** | `buildconfig.py:198-199` |
| 3 | 事件正文走 `.format()`，裸 `{` `}` 直接抛异常 | `talk.py:989-1026` |
| 4 | CSV 若带 BOM，`cid` 列名变 `﻿cid`，载入配置 KeyError | `buildconfig.py:102` |
| 5 | 编译分支要在 `buildconfig.py` 与 `auto_build_config.py` **两处**同步 | 三期偏离 9 |
| 6 | 事件弹出必须排在 `chara_handle_instruct_common_settle` **之前** | 三期偏离 8 |
| 7 | 所有选项都被前提挡住时不写履历 → 无条件守卫下会反复弹出 | `growth_event_panel.py:117-124` |
| 8 | partner 靠 `in premise_text` 子串匹配挑，新前提名不能包含那两个前提名 | `growth_event_handle.py:169-172` |
| 9 | `buildconfig.py` 会重写 PO，本机无 xgettext/polib，跑完须 `git checkout -- data/po/` | 三期已知限制 1 |

---

## 3. 设计决策

### 3.1 分类维度 = 部门 id，不另造分类表

事件表加 `department` 列，取值即 §2.2 的区块 cid，养成事件填 15（教育区）。
好处：部门名、岗位、设施等级、效率加成都能直接查既有配置，面板抬头可写
「【公务事件·医疗部】」而不用维护第二套分类名。

### 3.2 候选提供者注册表：新增部门只写 CSV

```python
EVENT_PROVIDER: Dict[int, Callable] = {}
""" 部门id -> 候选提供者，返回 [(uid, 权重, 主体角色id, 互动对象id), ...] """
```

- 养成（15）注册自己的提供者（遍历女儿、挑兄弟姐妹/同学、按成长阶段分桶），实现留在
  `Education_System`，在模块导入时注册 → **公务事件系统不 import 任何部门**
- 未注册的部门走**默认提供者**：以博士（角色 0）为判定主体、按 `premise` 筛选、按 `weight` 加权
- 于是新增一个部门的事件只要写 CSV

弃选方案：在公务事件系统里写 `if department == 15: ...` 的分支表——那样每加一个部门
都要改公共模块，且公务事件系统会反向依赖全部门，循环导入风险高。

### 3.3 同一角色不重复触发同一事件

`event_history` 本就是按角色记录、且对所有事件都写入，只有入队守卫是有条件的
（`judge_event_can_enqueue:259` 仅 `once != 0` 时才查）→ 改为**无条件查询**。

- 无主体的部门事件没有角色可挂 → `Rhodes_Island` 加 `official_event_history` 作为全局履历
- `once` 列因此失去入队作用，**保留为作者标注**（标记里程碑，影响权重习惯与统计报告）
- 连带效果：所有事件都可以按"这辈子只遇到一次"来写，叙事密度反而更高

### 3.4 触发频率随女儿数并发

| 常量 | 值 | 含义 |
| --- | --- | --- |
| `GROWTH_EVENT_DAILY_CHANCE` | 70 | 每个女儿每天入队一条的概率（平均约 1.4 天一条） |
| `GROWTH_EVENT_DAILY_MAX_PER_CHILD` | 1 | 每个女儿每天最多 1 条 |
| `DEPARTMENT_EVENT_DAILY_MAX` | 2 | 部门事件每日入队上限（全部门合计） |
| `OFFICIAL_EVENT_DAILY_MAX` | 8 | 全局每日硬顶 |
| `OFFICIAL_EVENT_QUEUE_MAX` | `max(12, 4×女儿数 + 6)` | 队列硬上限随女儿数放宽 |

遍历女儿前 `random.shuffle`，否则撞硬顶时永远是 id 小的女儿吃掉名额。
本条**推翻总纲口径 32**（"每日最多入队 1~2 条，全局上限"），须回写总纲。

### 3.5 事件条数由供需倒推（≥20% 盈余）

最坏情况（每天都触发）：婴儿期 30 可游玩日 / 幼女期 60 / 萝莉期 60（总纲 §2.3-7），共 150 次入队；
通用池权重压到阶段事件的 1/3，使其分走约 25%：

| 池 | 最坏消耗 | 目标条数 | 消耗率 | 盈余 |
| --- | --- | --- | --- | --- |
| 婴儿（sub_key 101） | ≈23 | 50 | 46% | 54% |
| 幼女（102） | 45 | 70 | 64% | 36% |
| 萝莉（103） | 45 | 70 | 64% | 36% |
| 养成通用（0） | ≈38 | 56（另 4 条 104） | 67% | 33% |

按实际 70% 触发概率，盈余为 68% / 55% / 55% / 53%。

### 3.6 全局数值通道：新增 `RI` 主体，但不动 settle_behavior

| 写法 | 作用域 | 实现 |
| --- | --- | --- |
| `CVE_A1/A2/A3\|adv_...` | 角色 | 既有 `settle_behavior.handle_comprehensive_value_effect`，**不动** |
| `CVE_RI_<类型>_<G/L/E>_<值>` | 罗德岛全局 | **新增**，由公务事件系统自己的 `handle_effect_text` 解析 |
| 纯数字 | 复杂效果 | 既有 `constant.settle_behavior_effect_data[id]` |

弃选方案：扩 `settle_behavior` 的主体判别。那里的属性映射硬绑 `Character` 对象，
加全局主体要同时改主体判别、`change_data` 记录、Web 数值收集三处，且会影响全游戏的结算路径。
公务事件的 effect 串本就由自己的 `handle_effect_text` 逐项分发，在那里认前缀即可。

前提侧 `CVP_RI_...` 则必须进 `handle_premise.handle_comprehensive_value_premise`
（前提求值统一走那里），在主体判别处加一个 `RI` 分支即可，是该函数里唯一的改动点。

### 3.7 ArkEditor：主列表 + 详情表单 + 子块弹窗

照外勤委托页的范式（§2.4），右侧 `QFormLayout` 放基本字段 + **4 个 `QGroupBox` 选项块**，
每块 5 个控件（正文、前提只读框+按钮、原因、提示、结算只读框+按钮）。
全仓没有任何 `QTableWidget`，这是这里唯一成立的范式。

- **一次读整个 `data/official_event/` 目录**，左列表按部门+文件分组，保存时只重写改过的文件
- **复用既有前提/结算选择器**，办法是在 `cache_control` 加 `now_premise_target` /
  `now_effect_target` 两个引用，把选择器的写入点改成写这个引用（§2.4 第三条）
- CVP/CVE 下拉补上三期欠的 `Growth` 与本轮的 `RI`，并补 `function.py` 的 token 反解链
- 保存**一律走 `csv.writer`** 写全部行（含 5 行表头），UTF-8 无 BOM、全 CRLF
- 读表头用**数索引跳过前 4 行**，不能照抄委托页的"找表名行"（多文件、表名各不相同）

### 3.8 跨阶段事件怎么排除掉婴儿

`sub_key = 0` 的事件会派给婴儿、幼女、萝莉三个阶段，可"她做了个东西送给你""她学你说话"这类
显然不适合婴儿。不为此新增前提，直接用既有的素质判定：**`CVP_A1_T|101_E_0`**（不持有婴儿素质）。

同理，跨阶段事件的正文**不能绑死住处**（婴儿住育儿室、幼女起住宿舍），
写"她住的地方"或干脆把场景放在食堂、走廊、甲板这些公共区域。

### 3.9 复杂效果用到的两个结算函数

| 结算id | 常量 | 作用 |
| --- | --- | --- |
| 3002 | `OFFICIAL_EVENT_ACCEPT_RECRUIT` | 接收一名待确认的招募干员（复用 `recruit_panel.recruit_new_chara`） |
| 3003 | `OFFICIAL_EVENT_TEMP_COMMISSION` | 生成一条突发的临时外勤委托（复用 `create_temp_commission`） |

**`create_temp_commission` 会把新委托追加写进 `data/csv/Commission.csv`**（不是只改内存），
所以它的描述里换行必须写成两个字符的 `
` 转义、且不能出现英文逗号，否则写出去的那一行会把 CSV 撑断，
下次构建直接报错。无头测试里也要把这个函数换成桩，不然跑一次测试就往仓库数据文件里塞一条脏数据。

---

## 4. 数据结构设计

### 4.1 事件表列结构（28 列）

`data/official_event/*.csv`，在三期 26 列基础上**净增 2 列**（`stage` 改名为 `sub_key` 不算新增）：

| 列 | 类型 | 说明 |
| --- | --- | --- |
| `cid` | str | 事件 uid，构建时自动加文件名前缀（如 `萝莉1`） |
| `department` | int | 部门 id（§2.2）。养成事件填 15 |
| `subject` | int | 事件主体：0 无主体（部门事务）/ 1 角色 |
| `sub_key` | int | 分类内子桶键。养成填成长阶段素质 id（0 全未成年 / 101 / 102 / 103 / 104） |
| `once` | int | **仅作者标注**（里程碑），不再影响入队（§3.3） |
| `weight` | int | 入队权重，与前提算出的权重相乘 |
| `premise` | str | 触发前提，`&` 连接 |
| `text` | str | 事件正文 |
| `option_1~4` | str | 选项文本，空则该选项不存在 |
| `option_1~4_premise` | str | 选项前提，不满足则置灰 |
| `option_1~4_reason` | str | 置灰原因（作者手写） |
| `option_1~4_tip` | str | 后果提示（只写方向不写数值） |
| `option_1~4_effect` | str | 选项结算，`&` 连接 |

三期的 `stage` 列**改名为 `sub_key`**（语义泛化），取值不变，所以总列数是 28 而不是 29。
四个养成 CSV 的**文件名保持不变**（`婴儿/幼女/萝莉/通用.csv`）——cid 前缀由文件名生成，
改名会让全部 uid 变化，而旧存档的 `event_history` 里存的是旧 uid。

运行时索引（`game_config.py`）：

```python
config_official_event: Dict[str, dict] = {}
""" 公务事件表 键str:事件uid 值dict:事件原始dict
    存原始dict而非config对象：CSV里空着的选项列在构建时已被删掉，必须用 .get() 取 """
config_official_event_by_department: Dict[int, list] = {}
""" 部门id -> 事件uid列表 """
config_official_event_by_sub_key: Dict[tuple, list] = {}
""" (部门id, sub_key) -> 事件uid列表 """
```

### 4.2 队列与全局履历（`Rhodes_Island`）

```python
        self.official_event_queue: list = []
        """ 待玩家在处理公务中决断的公务事件队列（Plan 23）
            元素dict:{"uid": 事件uid str, "department": 部门id int,
                      "chara_id": 主体角色id int（无主体为0）,
                      "partner_id": 互动对象角色id int（无则0）, "add_time": datetime}
            由 plan22 三期的 growth_event_queue 改名而来，旧档在 save_handle 里逐项搬运 """

        self.official_event_history: dict = {}
        """ 无主体（部门）公务事件的全局履历 键str:事件uid 值dict:{"time": datetime, "choice": int}
            有主体的事件记在角色自己的 CHILD_GROWTH.event_history 里，两者语义一致 """
```

### 4.3 `RI` 全局数值编号表（`ri_value.py`）

| 类型 | 含义 | 读 | 写 | 落点 |
| --- | --- | --- | --- | --- |
| `R\|<资源id>` | 素材资源（`Resource.csv`） | ✅ | ✅ | `rhodes_island.materials_resouce` |
| `Rep\|<势力id>` | 势力声望 | ✅ | ✅ | `cache.country.nation_reputation` |
| `Fac\|<设施cid>` | 设施等级 | ✅ | ❌ | `rhodes_island.facility_level` |
| `Work` | 待处理公务量 | ✅ | ✅ | `rhodes_island.office_work`（clamp 到 `[0, all_work]`） |
| `Eff` | 基地效率 | ✅ | ✅ | `rhodes_island.effectiveness`（clamp 50~200） |
| `Power` | 电力储量 | ✅ | ✅ | `rhodes_island.power_storage` |
| `People` | 当前干员数 | ✅ | ❌ | `len(cache.npc_id_got)` |

写入一律走 `change_ri_value()`：它负责 clamp、`setdefault` 与只读项的静默忽略，
避免各处直接改 dict 导致资源为负或效率越界。

### 4.4 新增的养成数值 `Growth|3`

`growth_handle.GROWTH_VALUE_STAGE_PROGRESS = 3`：本阶段进度百分比（0~100，只读）。
复用 `pregnancy_handle.get_child_grow_day()` 与 `get_child_growth_stage_total_day()`；
阶段阈值是累计值（婴儿 0~90 / 幼女 90~270 / 萝莉 270~450），
进度 = `(当前天 - 本阶段起点) / (阈值 - 起点) × 100`。
该分支要放在 `growth_data is None` 的提前返回**之前**（进度不依赖养成数据）。

### 4.5 两个新前提

| 常量 | 值 | 判据 | 复用 |
| --- | --- | --- | --- |
| `SELF_MOTHER_AVAILABLE` | `self_mother_available` | 母亲仍在队中且可跟随 | `class_ai.judge_mother_available()` |
| `SELF_HAVE_ANY_COURSE` | `self_have_any_course` | 个人课表非空 | `child_growth.selected_course` |

新前提名不能包含 `self_have_classmate` / `self_have_sibling_child`（§2.5-8 的子串匹配）。

---

## 5. 内容规划

### 5.1 养成事件（部门 15，扩到 250 条）

| 文件 | 现状 → 目标 | 分组配额 |
| --- | --- | --- |
| `婴儿.csv`（sub_key 101） | 4 → 50 | 早期 12（`Growth\|3_L_35`）/ 中期 12 / 后期 12（`Growth\|3_GE_50`）/ 带前提 10 |
| `幼女.csv`（102） | 4 → 70 | 搬进自己的房间 8 / 学业 14 / 生活 14 / 同伴 10 / 与你的关系 10 / 罗德岛与季节 10 |
| `萝莉.csv`（103） | 5 → 70 | 学业 18 / 同伴 12 / 与你的关系 13 / 身心成长 12 / 罗德岛设定向 10 |
| `通用.csv`（0 与 104） | 5 → 60 | 季节 10 / 日常 14 / 与你的关系 12 / 兄弟姐妹与同学 10 / 母亲相关 8 / 成年后 4 |

**数值口径**：未成年阶段好感 +5~+30 / −5~−20、信赖 +2~+6、性格倾向 ±1~±4、照料 +1~+5；
成年阶段（104）好感 +80~+200、信赖 +10~+20。
**权重**：阶段日常 9~12、里程碑 15~25、跨阶段通用 3~5（压低是 §3.5 的 25% 前提）。
口径 33 不变：选错只让性格偏得不如预期、好感小幅下降，不掉能力、不造成不可逆损失。

**设定校正**：婴儿期（101）住育儿室；幼女期起（102/103/104）住自己的宿舍
（`Script/System/Dormitory_System/common.py:409` 分配）。因此不写"想搬出育儿室自己住"，
"从育儿室搬进自己的房间"反而是很好的幼女期开篇里程碑；跨阶段的 `通用.csv` 措辞不能绑死住处。

### 5.2 部门事件的决策点备忘（内容留到后续，本轮不写）

下表是后续写部门事件时的落点清单，架构与结算通道都已就位：

| 部门 | 文件 | 决策点 | 落点字段 |
| --- | --- | --- | --- |
| 12 制造加工区 | `生产.csv` | 原料告罄，切配方还是停线 | `assembly_line[line][3]` |
| 6 医疗部 | `医疗.csv` | 重症潮，涨价保药品 vs 保声望 | `new_medical_price_ratio` / 声望 |
| 7 文职部 | `人事.csv` | 已招募干员的接收/婉拒 | `recruited_id` |
| 3 仓储区 | `后勤.csv` | 仓储告急，抛售 vs 扩容 | `materials_resouce` |
| 14 机库 | `外勤.csv` | 突发委托的接/拒 | `create_temp_commission` |
| 2 工程部 | `装备.csv` | 批量损坏，先修高损坏 vs 先保养全体 | `equipment_maintain_setting` |

---

## 6. 风险与注意事项

| # | 风险 | 对策 |
| --- | --- | --- |
| 1 | 迁移面大（模块、数据目录、队列字段同时改名） | 一次改完一起验；旧档队列逐项搬运并按 uid 补 `department`，补不到则丢弃 |
| 2 | 事件表两处编译分支不同步 | `buildconfig.py` 与 `auto_build_config.py` 必须同改（三期教训） |
| 3 | 无条件履历守卫 + 全选项置灰 = 反复弹出 | 校验工具强制"每条至少一个无前提选项" |
| 4 | 部门事件没有主体角色，却写了 `CVE_A1` | 校验工具禁止 `subject=0` 的事件出现 `CVE_A1/A2` |
| 5 | 全局数值被写成负数/越界 | 一律走 `change_ri_value()` 的 clamp |
| 6 | 编辑器保存破坏表头或行尾 | 全部走 `csv.writer`；往返测试（读→改→存→再读）纳入验证 |
| 7 | 编辑器切页控件叠加 | 装配前先 `window.completed_layout()` 重建 centralWidget |
| 8 | 268 条手写数据的静默错误 | `tools/official_event_check.py` 每批必跑 |
| 9 | 多周目 | 队列与全局履历随 `Rhodes_Island` 重置（`new_round.py:37-49`） |
| 10 | 循环导入 | 数据在 Core、逻辑在 System，部门提供者靠注册表反向注册，函数内延迟 import |

---

## 7. 不在本方案范围

- 六个部门事件的**全部内容**（含样例，本轮一条不写；架构、默认提供者与 `RI` 结算通道都已就位，后续只需往 `data/official_event/` 加 csv）
- 动力区、贸易区、访客区等其余部门的事件表
- 把外勤委托的 `demand`/`reward` 前缀语法统一到 CVP/CVE（两套语法暂时并存）
- ArkEditor 的口上/事件页面重构（只新增公务事件页，不动既有页）
- NPC 之间的自主互动行为链（plan_22 口径 36 明确不做）

## 8. 第二轮追加调整

（实施完成后按 §8.1 / §8.2 顺延追加，只写设计；对应的实施记录写在实施文档 §6.5）
