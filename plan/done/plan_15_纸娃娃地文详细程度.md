# Plan 15：纸娃娃地文的详细程度分为低/中/高三档

- 状态：**已实施（2026-08-26，单元测试 38 项全部通过，见 §10.3；游戏内整体测试与 buildpo/buildmo 本地化步骤待用户执行）**
- 来源：用户需求 → 纸娃娃地文当前把 A/B/C 三段全部绘制出来，需要在绘制设置中新增"纸娃娃地文详细程度"选项，低档随机只出一段、中档出 A 加 B/C 其一、高档三段全出，默认为中
- 预计改动量：3 个文件（1 个 CSV + 1 个配置加载 + 1 个逻辑），约 40 行
- 风险等级：低（只裁剪已有分段的拼接范围，不新增文本数据、不改存档结构、不改 UI 面板）
- 适用代码快照：`master @ 7051def26`（游戏版本 2026.8.26-1）
- 已确认的设计决策：
  1. 低档在 A/B/C 三段间**等概率随机取一段**（而非固定取 A）
  2. 中档为 A 段 + B/C 间**等概率随机**取一段
  3. 分档**只作用于动作类**（`action_part_*`），部位短词（`body_part_*`）完全不受影响

---

## 1. 目标

1. 在 `data/csv/System_Setting.csv` 的 `draw`（绘制）类中新增一项"纸娃娃地文详细程度"，选项为 `低|中|高`，默认值为"中"。
2. 低档：动作类纸娃娃地文在 A/B/C 三段中等概率随机只输出一段。
3. 中档：输出 A 段，再从 B/C 中等概率随机附加一段（即 AB 或 AC）。
4. 高档：维持现状，A/B/C 三段全部输出。
5. 部位短词占位符（如 `{breast_s}` = 形容词 + 名词）在任何档位下都保持全段拼接，不被裁剪。

## 2. 现状调查

### 2.1 关键代码落点

| 机制 | 位置 | 说明 |
| --- | --- | --- |
| 分段拼接（本次改动点） | `Script/Design/talk.py:682-720` `_part_replacer` | `for part in part_dict:` 逐段各挑一条文本拼接；动作类拼完后追加 `\n`（第 716-717 行） |
| 占位符总入口 | `Script/Design/talk.py:644-758` `talk_common_judge` | 第 671 行判断 key 是否在 `config_talk_common_cid_list_by_part` 中，是则走分段分支，否则走单条分支 |
| 唯一调用链 | `Script/Design/talk.py:780` `code_text_to_draw_text` → `Script/Design/talk.py:307` `handle_talk_draw` | `talk_common_judge` 全仓库只有这一处调用点，改动影响面收敛 |
| 分段字典构建 | `Script/Config/game_config.py:1449-1467` `load_talk_common` | `type_id` 含 `part` 时：`part_id = type_id[-1]`、`real_type_id = type_id.split("part_")[-1][:-2]` |
| 绘制设置读取 | `cache.all_system_setting.draw_setting[序号]` | 序号 = CSV 的 `cid % 100`，见 `Script/Config/game_config.py:1864-1872` |
| 默认值填充 | `Script/Design/attr_calculation.py:26-28` | 遍历 `config_draw_setting`，用 `default_value` 建空设置字典 |
| 旧存档回填 | `Script/Core/save_handle.py:660-664` | **只补缺失的 key**，已存在的 key 一律保留存档里的旧值 |
| 设置面板 | `Script/UI/Panel/system_setting.py:149-203` `draw_option` | 带 `|` 的多选项会**自动**渲染成循环切换按钮，第 218 行 `option_name_info` 自动展示 info 文本 |

### 2.2 A/B/C 三段的实际语义

文本数据分布在 `data/talk_common/` 下的 `action_A` / `action_B1` / `action_B2` / `action_C1` / `action_C2` 五个目录，但 `type_id` 末位只有 A/B/C 三种，即 B1+B2 合并进 B 段候选池、C1+C2 合并进 C 段候选池：

| 段 | 目录 | 内容 |
| --- | --- | --- |
| A | `action_A` | 整体动作概述（一段完整地文） |
| B | `action_B1` / `action_B2` | 具体动作细节；B1 为主动方视角、B2 为承受方视角 |
| C | `action_C1` / `action_C2` | 感受描写；C1 为主动方感受、C2 为承受方感受 |

穷举 `data/talk_common/` 全部 CSV 的 `type_id`，含 `part` 的 key 共 60 个：

- **动作类 48 个**（`action_part_*`）：`eat` 1 个、`{a,b,c,h,m,s,u,v,w}_orgasm_{small,normal,strong,super}` 系列 34 个、`penis_in_body_0~11` 与 `penis_in_body_15` 共 13 个。除 `penis_in_body_7` 只有 A/B 外，其余均齐备 A/B/C。（原稿手工累加误记为 47，已按实测订正，见 §10.2 第 5 条）
- **部位短词 16 个**（`body_part_*`）：`anal_s`、`breast_s`、`vagina_s` 等，A = 形容词（"温热"）、B = 名词（"胸部"），拼成 `{breast_s}` → "温热胸部"；其中 `common_s`、`throat_s` 只有 A 段。

### 2.3 已知陷阱与硬约束

**(a) 必须排除部位短词。** 这是本计划最关键的约束：`body_part_*` 的 A/B 是"形容词 + 名词"，若一并按档位裁剪，低档下 `{breast_s}` 会只剩"温热"，全游戏所有含部位短词的地文都会出现残缺。

现有代码在 `Script/Design/talk.py:676` 用 `key.endswith("_s")` 来识别部位短词，但那处判断本身带有 `penis`/`hair` 例外，属于脆弱的字符串猜测，不宜再叠加复用。本计划改用显式白名单集合（见 §4.2）。

**(b) cid 选号不能复用 216。** CSV 现有 draw 类 cid 为 201~215、217、218、219，216 看似空号可用，但：

- `git show 02f142574 -- data/csv/System_Setting.csv` 显示 216 原为"是否显示博士的饥饿值、尿意值"，后被改号为 217，**老存档里 `draw_setting[16]` 仍残留 0/1**；
- `Script/Core/save_handle.py:660-664` 只补缺失 key、不覆盖已有 key，所以复用 216 会让老存档静默拿到错误档位。

另有先例佐证撞号的危害：`draw_setting[18]` 被 `Script/Core/web_server.py:347` 挪作"Web 全部位显示"的运行时开关，与 CSV 218（TK DPI 缩放）撞号。

⚠️ **结论：新设置用 cid 220**（对应 `draw_setting[20]`，全新号，老存档必然缺失从而被填入默认值）。实施时仍需再核对一次 CSV 里 220 未被占用。

**(c) 分段顺序不要依赖 dict 插入序。** `part_dict` 的键序来自 `Talk_Common.json` 的数据顺序，而该顺序由 `buildconfig.py:578` 的 `os.listdir(talk_common_dir)` 决定。当前恰好是 `action_A` → `action_B1` → `action_B2` → `action_C1` → `action_C2` 的字母序，A→B→C 成立，但这是巧合而非保证，实施时必须显式指定顺序。

### 2.4 引用全量清单

- `talk_common_judge`：定义于 `Script/Design/talk.py:644`，唯一调用点 `Script/Design/talk.py:780`。
- `config_talk_common_cid_list_by_part`：定义于 `Script/Config/game_config.py:300`，写入点 `Script/Config/game_config.py:1463-1465`，读取点 `Script/Design/talk.py:671`、`Script/Design/talk.py:673`、`Script/Design/talk.py:677`。
- `code_text_to_draw_text` 另有 6 处调用（事件选项、事件文本、debug 面板、指令查看面板），均走同一条 `talk_common_judge`，无需单独适配。

## 3. 设计决策

| 决策点 | 选择 | 弃选方案及原因 |
| --- | --- | --- |
| 低档取段规则 | A/B/C 中等概率随机取一段 | 弃"固定只取 A"：用户明确要求随机，且固定取 A 会让低档玩家永远看不到 B/C 段的文本资产 |
| 中档取段规则 | A + B/C 等概率随机 | 弃"优先 B、无 B 才 C"与"加权偏向 B"：用户口径为"AB 或者 AC"，等概率最贴合 |
| 动作类/部位短词的判据 | 在 `game_config` 中新建显式白名单集合 | 弃 `key.endswith("_s")`：已有 `penis`/`hair` 例外，脆弱且未来新增 key 容易误判 |
| 分段遍历顺序 | 硬编码 `("A", "B", "C")` 过滤 | 弃依赖 `part_dict` 插入序：见 §2.3(c) |
| cid 编号 | 220 | 弃 216：见 §2.3(b) |

## 4. 详细改动步骤

### 4.1 数据表（`data/csv/System_Setting.csv`）

在文件末尾 219 行之后追加一行，列序为 `cid,type,name,info,option,default_value`：

```
220,draw,纸娃娃地文详细程度,纸娃娃地文由整体动作(A)、具体动作(B)、感受描写(C)三段拼接而成。\n低：三段中随机只显示一段，文本最短。\n中：显示整体动作，再随机附加具体动作或感受描写其中一段。\n高：三段全部显示，文本最长。\n默认为中,低|中|高,1
```

`info` 列中的 `\n` 会被 `Script/UI/Panel/system_setting.py:230` 转成实际换行，与既有的 103、202、213 号设置写法一致。

### 4.2 配置加载（`Script/Config/game_config.py`）

新增一个"动作类 part 键"集合，作为区分动作类 / 部位短词的显式判据：

1. 在 `Script/Config/game_config.py:300-301` 的 `config_talk_common_cid_list_by_part` 声明之后，追加：

```python
config_talk_common_action_part_type_set: Set[str] = set()
""" 动作类分段通用口上的类型名集合（即action_part_*，用于区分部位短词body_part_*） """
```

2. 在 `Script/Config/game_config.py:1459-1465` 的 `if "part" in real_type_id:` 分支内、`part_id`/`real_type_id` 解析之后，追加：

```python
# 记录动作类分段，供纸娃娃地文详细程度分档使用（部位短词不入此集合）
if now_tem.type_id.startswith("action_"):
    config_talk_common_action_part_type_set.add(real_type_id)
```

判据口径与 `Script/Design/talk.py:702` 既有的 `'action' in type_id` 一致。该集合是运行时从 `Talk_Common.json` 解析出来的，**不需要重跑 buildconfig**。

### 4.3 拼接逻辑（`Script/Design/talk.py:682-720` `_part_replacer`）

在 `Script/Design/talk.py:692` 的 `part_str = ""` 之后、`for part in part_dict:` 之前，插入"待绘制分段列表"的计算，并把循环改为遍历该列表：

```python
# 纸娃娃地文详细程度分档：仅对动作类(action_part_*)生效，部位短词(body_part_*)必须全段拼接
# 显式指定A→B→C顺序，不依赖part_dict的插入序
draw_part_list = [p for p in ("A", "B", "C") if p in part_dict]
if key in game_config.config_talk_common_action_part_type_set:
    detail_level = cache.all_system_setting.draw_setting.get(20, 1)
    if detail_level == 0:
        # 低档：A/B/C三段中等概率随机只取一段
        draw_part_list = [random.choice(draw_part_list)] if draw_part_list else []
    elif detail_level == 1:
        # 中档：整体动作段A + B/C中等概率随机取一段
        extra_list = [p for p in draw_part_list if p in ("B", "C")]
        draw_part_list = [p for p in draw_part_list if p == "A"]
        if extra_list:
            draw_part_list.append(random.choice(extra_list))
    # 高档(detail_level == 2)不做裁剪，保持三段全出
for part in draw_part_list:
    ...  # 以下原有逻辑不变
```

实施要点：

- `key` 是 `_part_replacer` 外层闭包里的循环变量（`Script/Design/talk.py:659`），可直接读取；若担心闭包晚绑定，按第 682 行 `part_dict=part_dict` 的既有写法，把 `key` 也固化成默认参数。
- 低档直接在**实际存在**的分段里 `random.choice`，天然兼容缺段的 key；中档若某 key 缺 A 段则退化为只出 B/C 中一段，不会输出空串。
- `penis_in_body_7` 无 C 段 → 低档在 A/B 中二选一，中档 `extra_list` 只有 B 从而退回 AB，均符合预期。
- `random`、`cache`、`game_config` 均已在 `Script/Design/talk.py` 顶部导入，无需新增 import。
- 用 `.get(20, 1)` 而非 `[20]`，与 `Script/Design/talk.py:160`、`Script/Design/talk.py:222` 的既有写法保持一致，防止老存档 / 异常路径 KeyError。

### 4.4 无需改动的配套项（已逐项核对）

| 项 | 结论 |
| --- | --- |
| `Script/Config/config_def.py` | `System_Setting` 未增列，`buildconfig` 生成结果不变 |
| `Script/UI/Panel/system_setting.py` | 带 `|` 的多选项自动渲染为循环切换按钮，无需写面板代码 |
| `Script/Core/game_type.py` | `draw_setting` 已是 `Dict[int, int]`，无需加字段 |
| `Script/Core/save_handle.py` | 第 660-664 行的回填逻辑已覆盖新 key |
| ArkEditor | 全仓库仅 `data/csv/System_Setting.csv` 一份，无编辑器副本需同步 |
| Web 绘制模式 | 设置面板走同一套 `draw` 抽象，无需单独适配 |

## 5. 构建与缓存

```bash
# 本机必须用 conda 解释器（裸 python 是 Store 空壳别名，会 exit 49 且无输出）
.conda\python.exe buildconfig.py   # 改了 System_Setting.csv，必须全量重建 data.json 与 PO
.conda\python.exe buildpo.py       # 新增了 name / info / option 三处待翻译词条
.conda\python.exe buildmo.py
```

§4.2 的 `game_config` 改动是运行时解析 `Talk_Common.json`，不需要重建口上数据；§4.3 是纯逻辑改动，无需任何重建。

## 6. 验证清单

### 6.1 单元测试（实施方执行）

不启动图形界面，以 scratchpad 脚本（不入库）初始化配置与缓存后直接调用函数验证；无头环境搭法参照 skill `headless-game-test`。

- [x] `game_config.config_draw_setting[20]` 存在，`config_draw_setting_option[20] == ["低", "中", "高"]`，`default_value == 1`
- [x] `attr_calculation` 生成的空设置里 `draw_setting[20] == 1`
- [x] `config_talk_common_action_part_type_set` 含 48 个动作类 key，且不含任何 `*_s` 部位短词
- [x] 对 `{penis_in_body_6}` 分别在档位 0 / 1 / 2 下调用 `talk.talk_common_judge`，断言输出的动作段条数为 1 / 2 / 3（按 `\n` 计数）
- [x] 低档重复调用 N 次，A/B/C 三段都出现过（验证是三选一随机而非固定 A）
- [x] 中档重复调用 N 次，B 段与 C 段都出现过（验证随机而非固定），且每次都含 A 段
- [x] `{penis_in_body_7}`（无 C 段）在低档下只出 A 或 B、在中档下稳定输出 A+B，均不报错
- [x] 三档位下 `{breast_s}` 均输出"形容词 + 名词"两段，不受档位影响（**核心回归项**）
- [x] 构造缺 `draw_setting[20]` 的旧存档 dict 走 `save_handle` 回填后取到默认值 1
- [x] `.conda\python.exe buildconfig.py` 全量重建无报错，新设置在 `data/data.json` 中齐备

### 6.2 游戏内整体测试（由用户执行）

- [ ] 系统设置 → 绘制设置中出现"纸娃娃地文详细程度"，可在 低/中/高 间循环切换，点选项名能看到介绍文本
- [ ] 三档位下分别触发一次进食、一次高潮、一次插入类 H 指令，地文长度呈现明显的短 / 中 / 长差异
- [ ] 低档下多触发几次，能看到不同段落（有时只有整体动作、有时只有感受描写）
- [ ] 各档位下 `{breast_s}` 之类的部位描述均正常（如"温热的胸部"而非"温热的"）
- [ ] Tk 与 Web 两种绘制模式均正常
- [ ] 载入旧存档不报错，且档位为默认的"中"

## 7. 风险与回滚

| 风险 | 说明 | 对策 |
| --- | --- | --- |
| 误伤部位短词 | 若判据写错，`{breast_s}` 会退化成"温热"，影响全游戏地文 | 用 `config_talk_common_action_part_type_set` 显式白名单；§6.1 已把该项列为必测回归 |
| cid 撞号 | 复用 216 会让老存档静默继承已废弃设置的旧值 | 用 220；实施时再核对一次 CSV 未占用 |
| 分段顺序依赖 | 依赖 dict 插入序会在换 OS / 换构建顺序后错乱 | 显式按 `("A", "B", "C")` 过滤排序 |
| 低档文本观感 | 低档随机只出一段，可能出现"只有感受没有动作"的突兀文本 | 属设计取舍（用户已确认），若验收不满意可改为 A 段加权 |

回滚：三处改动彼此独立，可分别回滚。

1. 删除 `data/csv/System_Setting.csv` 的 220 行 → **必须重跑 `buildconfig.py`**
2. 还原 `Script/Design/talk.py` 的 `_part_replacer`（恢复 `for part in part_dict:`）→ 无需重建
3. 删除 `Script/Config/game_config.py` 的新集合及其写入 → 无需重建

若只回滚 1 而保留 2、3，`.get(20, 1)` 会退到默认的中档，游戏仍可运行但玩家无法调节，属可接受的中间态。

## 8. 改动文件清单

| 文件 | 类型 | 改动 |
| --- | --- | --- |
| `data/csv/System_Setting.csv` | 修改 | 新增 cid 220 的绘制设置一行 |
| `Script/Config/game_config.py` | 修改 | 新增 `config_talk_common_action_part_type_set` 声明与写入 |
| `Script/Design/talk.py` | 修改 | `_part_replacer` 按档位裁剪待绘制分段列表 |

**未改动**：`Script/Config/config_def.py`、`Script/UI/Panel/system_setting.py`、`Script/Core/game_type.py`、`Script/Core/save_handle.py`、`Script/Core/web_server.py`、`data/talk_common/` 下任何文本 CSV、ArkEditor。

## 9. 不在本 Plan 范围

- 不新增 / 补写任何 A/B/C 段文本（`todo list.txt:41` 的"补上阴道、后穴、阴蒂、乳房的时停解放纸娃娃地文"是另一件事）
- 不处理 `draw_setting[18]` 与 Web 全部位显示的既有撞号问题（仅在 §2.3 记录，留待单独修复）
- 不做角色级（`chara_setting`）的独立档位，只做全局绘制设置
- 不改 `data/csv/System_Setting.csv` 中其他任何设置项的 cid 或默认值
- 不调整 B1/B2、C1/C2 之间的权重关系（仍由既有的前提权重机制决定）

## 10. 执行记录

### 10.1 实际改动（2026-08-26）

| 文件 | 实际落点 | 改动 |
| --- | --- | --- |
| `data/csv/System_Setting.csv` | 第 39 行（末尾） | 新增 `220,draw,纸娃娃地文详细程度,...,低\|中\|高,1`；CRLF 行尾与全文一致 |
| `Script/Config/game_config.py` | 第 302-303 行声明、第 1468-1470 行写入 | 新增 `config_talk_common_action_part_type_set` 与 `load_talk_common` 中的写入 |
| `Script/Design/talk.py` | 第 682-710 行 `_part_replacer` | 签名加 `key=key` 默认参数；新增 `draw_part_list` 分档裁剪；循环改为 `for part in draw_part_list` |
| `update.log` | v0.66 块新增段末尾 | 登记一条「新增：（纸娃娃地文）……」 |

cid 实际按计划取 **220**，核对时确认 CSV 中未被占用。

### 10.2 与计划的偏差

1. **`draw_part_list` 的默认值改为 `list(part_dict)` 而非 `[p for p in ("A","B","C") if p in part_dict]`。** 计划里对所有 part 型占位符统一按 ABC 过滤排序，实施时改为：只有命中动作类白名单时才做 ABC 过滤，部位短词分支保持 `list(part_dict)` 原插入序。原因是若将来出现 A/B/C 之外的分段 id，统一过滤会把它**静默丢弃**；现在部位短词路径与改动前逐字节等价，风险面进一步收窄。
2. **`_part_replacer` 额外把 `key` 固化为默认参数。** 计划正文提到"若担心闭包晚绑定可固化"，实施时直接做了，与既有的 `part_dict=part_dict` 写法一致。
3. **§2.3(b) 的 216 号风险实测复核。** 编写单元测试时发现 `save_handle.update_settings`（`Script/Core/save_handle.py:659`）用的是 `len(存档) != len(默认)` 作为回填触发条件，而非逐 key 比对。真实的老存档（缺 217~220、残留 16）长度必然不等，回填正常触发，已断言通过；但如果某个存档恰好"少一个 key、多一个废弃 key"导致长度相等，回填会被整体跳过。这是 `update_settings` 的既有性质，非本次引入，本 Plan 不修改；`talk.py` 侧的 `.get(20, 1)` 已能兜底退化为中档，也已单独断言。
4. **`buildpo.py` / `buildmo.py` 未能在本机执行。** 前者依赖 GNU gettext 的 `xgettext`（本机未安装，脚本在生成 `erArk.pot` 前失败），后者依赖未安装的 `polib`。二者只处理 `.py` 源码中的 `_()` 词条，本次未新增任何此类词条；CSV 的翻译词条由 `buildconfig.py` 内部的 `build_config_po` 直接写入 `data/po/zh_CN/LC_MESSAGES/erArk_csv.po`，已确认新设置的三处文案（name / info / option）均已写入。**留给用户在有完整本地化工具链的环境中补跑这两步。**（注：`buildpo.py` 失败时会先删除 `erArk_py.po` 再复制，已 `git checkout` 还原。）
5. **动作类 key 的实际数量是 48 而非计划 §2.2 写的 47**（计划撰写时手工累加漏了一个）。构成为：`eat` 1 个 + orgasm 系列 34 个 + `penis_in_body_*` 13 个 = 48。§2.2 的其余结论（哪些缺段、部位短词 16 个）均经实测复核无误。

### 10.3 测试结果

单元测试脚本（scratchpad，未入库）覆盖 §6.1 全部条目，**38 项断言全部通过**（`EXIT=0`）：

| 分组 | 项数 | 关键实测值 |
| --- | --- | --- |
| 5.1 CSV 新设置项 | 6 | `config_draw_setting_option[20] == ["低","中","高"]`、`default_value == 1`、16 号确认未占用 |
| 5.2 动作类白名单 | 6 | 动作类 48 个 / 部位短词 16 个，集合内无任何 `*_s`，全部 type_id 确为 `action_` 开头 |
| 5.3 分档裁剪 | 7 | 高档恒为 `[A,B,C]`；中档恒 2 段且首段恒为 A，60 次采样中 B/C 均出现；低档恒 1 段，60 次采样中 A/B/C 均出现 |
| 5.4 缺 C 段的 `penis_in_body_7` | 5 | 低档在 A/B 间二选一（40 次采样两者均出现），中/高档稳定 `[A,B]` |
| 5.5 部位短词回归 | 6 | 三档位下 `{breast_s}` 均输出 A+B 两段，且不产生任何动作段 |
| 5.6 真实前提端到端 | 5 | 以 `a_orgasm_normal` 实测：高档 3 段 / 中档 2 段 / 低档 1 段，低档文本非空 |
| 5.7 旧存档兼容 | 4 | 缺 key 回填为 1；残留 `draw_setting[16]` 不被误读；`draw_setting[20]` 缺失时退化为中档不报错 |

测试方法说明：5.3~5.5 用 monkeypatch 把 `get_weight_from_premise_dict` 固定返回权重 1，以隔离前提系统、单独验证分段挑选逻辑；同时包装 `talk.random.choice` 反查每次被选中文本的 `type_id` 末位，从而精确断言"实际绘制了哪几段"而非只数行数。5.6 则关闭全部 monkeypatch，在真实前提下端到端复核。

`.conda\python.exe buildconfig.py` 全量重建无报错。

### 10.4 尚未覆盖的验证（留给用户）

- §6.2 的全部游戏内整体测试项
- `buildpo.py` / `buildmo.py` 的本地化重建（见 §10.2 第 4 条）
