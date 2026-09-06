# Plan 21：生殖方式开关（可分别关闭多胎胎生/带壳卵生/无壳卵生，关闭即改为单胎胎生）

- 状态：已实施（单元测试 76 项全部通过，游戏内整体测试由用户验收，2026-09-06）
- 来源：用户需求 → "增加生殖方式的选择开关，可以选择某种生殖方式关闭改为单胎生，默认全开"
- 预计改动量：7 个代码/数据文件 + 2 个文档，约 200 行（1 个 CSV + 1 个配置装载 + 1 个数据结构 + 1 个默认值 + 1 个逻辑文件 + 1 个面板文件 + 1 个存档兼容文件）
- 实际改动量：与预计一致（详见 §8 / §10.1）
- 风险等级：中低（改动集中在 `get_birth_type` 单一入口，但"立即清除存量"是破坏性操作，需二次确认与充分测试）
- 适用代码快照：`master @ 6c3718216`（2026.8.31-1）
- 已确认的口径（规划阶段与用户确认）：
  1. **粒度**：3 个开关 —— 多胎胎生(2)、带壳卵生(11)、无壳卵生(12)；单胎胎生(1) 是兜底不给开关；1% 同卵双胞胎属单胎种族的既有机制，**不受任何开关影响**
  2. **存量处理**：关闭开关时**立即清除存量**（未孵化的卵全部移除，多胎孕程重置为 1 胎）
  3. **归属栏目**：系统设置的**基础设置**
  4. **交互形态（v2 修订）**：不是三个并列的设置项，而是**基础设置里一个入口项 + 一个子面板**，在子面板里分别开关三种生殖方式（照"禁止干员"功能的形态）
- 修订记录：
  - v1 —— 基础设置直接加 3 行 `type=base` 开关项（cid 13/14/15）
  - v2 —— 按用户要求推翻 v1 的并列三项：改为基础设置 cid 13 一个入口项跳转子面板；三个开关独立为 CSV 的 `type=birth` 分类（cid 直接取生育方式编号），运行时值改存 `all_system_setting.birth_type_setting`

---

## 1. 目标

1. 系统设置 → 基础设置中新增一个`生殖方式开关`入口项，点击 `[修改生殖方式开关]` 进入子面板，可分别开关多胎胎生、带壳卵生、无壳卵生，**默认全部开启**，旧存档载入时自动补默认值。
2. 某开关关闭后，该 `birth_type` 的种族角色在**全部游戏逻辑中**（受精判定、排卵、孵化、娱乐替换、前提、口上过滤、怀孕总览面板、礼物药物可用性、NPC AI）一律按**单胎胎生**处理。
3. 关闭开关时立即清除该生殖方式的存量数据并向玩家汇报；关闭属破坏性操作，需二次确认，取消则不改动任何数据。重新开启直接生效，无需确认。
4. 开关值随存档持久化，旧存档兼容由既有的设置补全机制承担。

## 2. 现状调查

### 2.1 生育方式的唯一读取入口

| 位置 | 内容 |
| --- | --- |
| `Script/System/Pregnancy_System/egg_handle.py:27 get_birth_type` | 读 `game_config.config_race[race].birth_type`，缺列兜底 1 —— **全局唯一读取点** |
| 同文件 `is_egg_soft` / `is_egg_layer` / `is_viviparous` / `is_multiple_birth` | 全部基于 `get_birth_type` 派生 |
| `Script/System/Pregnancy_System/pregnancy_constant.py:85~93` | `BIRTH_TYPE_SINGLE=1 / BIRTH_TYPE_MULTIPLE=2 / BIRTH_TYPE_EGG=11 / BIRTH_TYPE_EGG_SOFT=12` |
| `Script/Core/save_handle.py:250 _clear_soft_egg_race_pregnancy` | **唯一绕过 `get_birth_type` 直读 `race_config.birth_type` 的地方**（旧存档迁移） |

`grep -rn "birth_type" --include=*.py Script/` 的全量结果显示：除上表最后一行与生成物 `Script/Config/config_def.py` 外，其余全部经由 `egg_handle` 的这 5 个函数。**因此开关只需挂在 `get_birth_type` 上，下游全部自动跟随**，包括：

- 前提：`handle_premise_other.py:1201~1332` 的 `SELF/T_BIRTH_TYPE_EGG`、`SELF/T_BIRTH_TYPE_MULTIPLE`、`SELF/T_BIRTH_TYPE_EGG_SOFT`（均 lazy import `egg_handle`）
- 主链分流：`pregnancy_handle.check_all_pregnancy`（11→排卵+破壳；12→破壳；其余→妊娠链）、`check_fertilization`、`get_multiple_birth_range`
- 卵链：`egg_handle.check_ovulation`（守卫 `get_birth_type != 11` 并消费排卵标记）、`check_egg_born`、`replace_entertainment_for_eggs`（守卫 `is_egg_layer`）
- 无壳卵链：`soft_egg_handle.have_external_ovulation_chance`（守卫 `is_egg_soft`，是 `judge_external_ovulation` 的第一道门）
- 面板：`gift_panel.py:527/548`（妊娠加速药、假孕药限胎生）

### 2.2 可复用的既有实现

| 需求 | 复用对象 |
| --- | --- |
| 新增设置分类 | `game_config.load_system_setting` 按 `type` 分派到不同字典（base/difficulty/draw），加一个 `birth` 分支即可；`attr_calculation.get_system_setting_zero` 逐分类赋 `default_value`；`save_handle.update_settings` 按 key 缺失自动补默认值并提示 |
| 入口项只画一个自定义按钮 | `system_setting.draw_option` 对绘制设置 cid 12（字体大小）/18（DPI）的写法：画自定义按钮后 `continue`，跳过通用的选项切换按钮 |
| 子面板 | `system_setting.change_ban_list`（禁止干员列表）的 `while 1:` + 逐项按钮 + `[返回]` 结构；已关闭项用 `deep_gray` 样式表现，同 `change_ban_list` 对已禁止干员的处理 |
| 二次确认 | `hypnosis_panel` 的 `[确认]/[取消]` + `flow_handle.askfor_all` 模式；警告文案用 `warning` 样式（FontConfig cid 6，红色加粗） |
| 娱乐重掷 | `handle_npc_ai.get_chara_entertainment(character_id)`，随机池已显式剔除 175 照料卵 |
| 卵数据读写 | `PLAYER_COLLECTION.held_eggs`（值为 `(角色id, 卵编号)` 索引）、`PLAYER_COLLECTION.soft_eggs`（含 `mother_id`）、`PREGNANCY.eggs` |

### 2.3 已知陷阱与硬约束

1. **`_clear_soft_egg_race_pregnancy` 每次读档都跑**（位于 `_normalize_loaded_save_paths` 的角色循环内，非一次性迁移）。若无壳卵生开关关闭、12 族角色改走胎生链正常怀孕，该函数会在**每次读档时清空她的受精/妊娠/临盆素质与胎数** —— 必须加开关守卫，否则是数据丢失级 BUG。
2. **读档顺序**：`load_save` → `_normalize_loaded_save_paths` **先于** `update_settings` 执行，且此时 `cache_control.cache` 尚未被替换。守卫必须从 `loaded_cache.all_system_setting` 读，且用 `.get(cid, 1)` 兜底（旧存档此时还没有该项，默认按"开启"处理，正是旧存档迁移应有的行为）。
3. **旧存档的设置对象没有新属性**：`update_settings` 里必须先 `hasattr` 补空字典再按 key 补默认值，直接 `len()` 会 AttributeError。
4. **CSV 分隔符**：`System_Setting.csv` 用半角逗号分列，正文里的逗号一律写全角「，」；`info` 中的换行写字面量 `\n`（两个字符），由 `option_name_info` 转成实际换行。新列不可留空（空值会被 buildconfig 删除）。
5. **照料卵娱乐残留**：清除卵后，当日 `entertainment.entertainment_type` 中值为 175 的时段若不重置，状态机 `character_tend_eggs` 的 else 分支仍会执行 60 分钟"孵化卵"空转 —— 清除时顺手重掷该角色娱乐。
6. **同卵双胞胎不归多胎管**：`pregnancy_handle` 的 1% 判定在 `elif multiple_birth_flag` 的**否定分支**里，只对单胎种族生效，清除多胎存量时不得动 `identical_twins`。
7. `pregnancy_constant.BIRTH_TYPE_EGG_SOFT` 的 docstring 仍写着"未实装"（plan_19 已实装，注释过时），本次顺带订正。

### 2.4 存量数据的全量落点（"清除即归零"的验收判据）

| 数据 | 位置 | 归属开关 |
| --- | --- | --- |
| 角色持有的卵 | `character_data.pregnancy.eggs`（含 `soft` 字段区分带壳/无壳） | 母亲种族原始 birth_type 决定（11→带壳开关；12→无壳开关） |
| 玩家拿走的卵索引 | `cache.character_data[0].pl_collection.held_eggs` | 指向的母亲种族 |
| 体外无壳卵块 | `cache.character_data[0].pl_collection.soft_eggs`（`mother_id`） | 无壳开关 |
| 体外排卵机会 | `character_data.pregnancy.external_ovulation_chance` | 无壳开关 |
| 本次胎数 | `character_data.pregnancy.fetus_count` | 多胎开关（仅原始 birth_type==2 的角色） |
| 当日照料卵娱乐 | `character_data.entertainment.entertainment_type` 中的 175 | 两个卵生开关 |

**不清除**：已破壳/已出生的孩子与血缘关系、`talent[20]受精`（关闭卵生后该角色改走胎生链，受精自然转为正常妊娠）、`talent[23]产后 / 24育儿 / 27泌乳`、`identical_twins`、`next_egg_id` 等自增编号。

## 3. 设计决策

| 决策点 | 选择 | 弃选方案及原因 |
| --- | --- | --- |
| 开关生效位置 | 改造 `egg_handle.get_birth_type`：关闭时返回 `BIRTH_TYPE_SINGLE`；原实现拆出为 `get_race_birth_type`（读种族原始值） | 逐个改判定点：落点近 20 处、易漏且难维护 |
| 三个开关的存放 | CSV 新增 `type=birth` 分类，**cid 直接取生育方式编号 2/11/12**；运行时存 `all_system_setting.birth_type_setting`，键即生育方式 | ① 放 base 三个并列项：被用户否掉（要求一个入口）；② 写死在代码里：名称/说明/默认值脱离 CSV，翻译与维护都变差；③ 另建 cid 映射表：cid 直接取生育方式编号后完全不需要映射 |
| 入口项的形态 | 基础设置 cid 13，`option` 为单值（不可切换），`draw_option` 特判为 `[修改生殖方式开关]` 按钮 | 学禁止干员做成"否\|是"总开关：双重否定的 UX 绕，且"是"本身不改变任何行为 |
| 存量续跑 vs 清除 | **立即清除**（用户口径），因此卵链续跑的兜底代码一律不需要 | 存量续跑需在破壳判定、娱乐替换钩子、`take_chara_eggs` 指令前提等 4~5 处加"raw type"兜底 |
| 清除触发时机 | 只在**子面板里把开关从"开"切到"关"**的那一刻执行一次 | 每次 `get_birth_type` 惰性清理：函数被高频调用，副作用不可控 |
| 破坏性保护 | 关闭前二次确认（展示该项说明 + 红字警告），取消则**不改动开关值也不清数据** | 无确认：设置项是点击即切换的按钮，误触即毁存量 |
| 重新开启 | 直接生效，不确认、不恢复数据（已清除的不可逆） | 弹确认：开启是安全操作，没必要打断 |

## 4. 详细改动步骤

### 4.1 `data/csv/System_Setting.csv`

- base 段 cid 12 之后插入入口项（`option` 单值 `1`、`default_value` `0`，值本身无意义）：
  `13,base,生殖方式开关,可以分别关闭……\n点击右侧的[修改生殖方式开关]按钮进行设置，默认三种生殖方式全部开启,1,0`
- 文件末尾追加三行 `type=birth`（cid 即生育方式编号），选项统一为 `关闭，改为单胎胎生|开启`，`default_value` 全为 `1`：
  `2,birth,多胎胎生,…` / `11,birth,带壳卵生,…` / `12,birth,无壳卵生,…`
  说明文案中列出受影响的种族，并以 `※注意，关闭时会立即清除……该操作不可撤销` 收尾。

### 4.2 `Script/Config/game_config.py`

- 新增 `config_birth_type_setting` / `config_birth_type_setting_option` 两个字典。
- `load_system_setting()` 增加 `elif option_type == "birth":` 分支（cid **不取余**，直接用生育方式编号）。

### 4.3 `Script/Core/game_type.py` / `Script/Design/attr_calculation.py`

- `System_Setting` 新增 `birth_type_setting: Dict[int, int]`（键为生育方式编号，值 0 关 / 1 开）。
- `get_system_setting_zero()` 增加一段按 `config_birth_type_setting` 赋 `default_value` 的循环。

### 4.4 `Script/System/Pregnancy_System/pregnancy_constant.py`

- 订正 `BIRTH_TYPE_EGG_SOFT` 的过时 docstring。
- 新增 `BIRTH_TYPE_SETTING_LIST = [BIRTH_TYPE_MULTIPLE, BIRTH_TYPE_EGG, BIRTH_TYPE_EGG_SOFT]`。

### 4.5 `Script/System/Pregnancy_System/egg_handle.py`（核心）

- `get_birth_type` 的原实现改名为 `get_race_birth_type`（种族原始值，仅供存量清理与旧存档迁移）。
- 新增 `is_birth_type_enabled(birth_type)`：不在 `BIRTH_TYPE_SETTING_LIST` 中的（单胎胎生）恒 True；`all_system_setting` / `birth_type_setting` 缺失或类型不对时一律兜底 True。
- 新增开关感知的 `get_birth_type`：原始值被关闭时返回 `BIRTH_TYPE_SINGLE`。其余 4 个派生函数不动，自动跟随。
- 新增 `clear_birth_type_data(birth_type) -> str`：遍历 `cache.character_data`（用 `get_race_birth_type` 判归属，**不能用 `get_birth_type`**，此刻开关已关）→ 多胎分支重置 `fetus_count`；卵生分支清空 `pregnancy.eggs`、无壳另清 `external_ovulation_chance`、含 175 的娱乐时段重掷 → 循环外按母亲种族过滤删除 `held_eggs` 索引与 `soft_eggs` → 返回中文汇报文案，无存量时返回"没有需要清除的数据"。

### 4.6 `Script/UI/Panel/system_setting.py`

- `draw_option` 在绘制设置特判之前插入基础设置特判：cid 13 画 `[修改生殖方式开关]` 按钮并 `continue`。
- 新增 4 个方法：
  - `birth_type_setting_panel_draw()` —— 子面板主循环（标题 + 操作说明 + 逐项"名字按钮 + 状态按钮" + `[返回]`），已关闭项状态按钮用 `deep_gray`。
  - `birth_type_name_info(birth_type)` —— 显示该生殖方式的详细说明。
  - `change_birth_type_setting(birth_type)` —— 关→开直接生效；开→关先确认，确认后置 0、调 `clear_birth_type_data` 并 `WaitDraw` 汇报。
  - `confirm_close_birth_type(name, info)` —— 二次确认循环，`[确认关闭]` / `[取消]`。

### 4.7 `Script/Core/save_handle.py`（读档迁移守卫，**必做**）

- `_clear_soft_egg_race_pregnancy(character, soft_egg_enabled=True)`：新增形参，函数开头 `if not soft_egg_enabled: return`，docstring 说明原因。
- `_normalize_loaded_save_paths` 在角色循环**之外**先从 `loaded_cache.all_system_setting.birth_type_setting` 读一次开关（`.get(BIRTH_TYPE_EGG_SOFT, 1)` 兜底），传给上面的调用。
- `update_settings` 增加生殖方式设置的补全段（先 `hasattr` 补空字典，再按 key 补默认值，提示"生殖方式设置已更新"）。

### 4.8 文档与日志

- `.github/prompts/数据处理工作流/妊娠系统.md` §2：新增"生殖方式开关"条目（数据、入口、生效点唯一、关闭即清除存量、读档守卫）。
- `.github/prompts/数据处理工作流/系统设置系统.md`：`type` 增加 `birth`、两处字典/字段清单、核心方法清单、"特殊设置处理"第 4 条、"设置类型详解"新增 birth 小节。
- 仓库根 `update.log` 当前版本块的新增段追加一条（体例见 skill `update-changelog`）。

## 5. 构建与缓存

```bash
# 本机必须用 conda 解释器（裸 python 是 Store 空壳别名，exit 49 无输出）
.conda\python.exe buildconfig.py   # 改了 System_Setting.csv，必须全量重建（data.json / config_def.py / PO）
```

不涉及地图/角色模板，无需删 `data/SceneData` 等缓存。`tools/ArkEditor/csv/` 下没有 `System_Setting.csv`，无需同步副本。
`buildpo.py` / `buildmo.py` 在本机跑不了（前者依赖 xgettext 产出的 `erArk.pot`，后者依赖未安装的 `polib`），且 **`buildpo.py` 中途失败会删掉 `data/po/zh_CN/LC_MESSAGES/erArk_py.po`，必须 `git checkout` 还原**。新增的 `.py` 界面文案没有 PO 条目时 gettext 回落到中文原串，显示正常。

## 6. 验证清单

### 6.1 单元测试（实施方执行，scratchpad 脚本不入库，环境搭法参照 skill `headless-game-test`）

- [x] 默认值与配置：新游戏三个开关齐备且全为开启；base 入口项 13 与 birth 三项均已装载
- [x] `is_birth_type_enabled`：三个开关各自开/关正确；单胎胎生恒 True；字典为空 / 属性缺失时兜底 True
- [x] `get_birth_type`：三族在对应开关关闭后返回 1，互不干扰；`get_race_birth_type` 始终返回原始值
- [x] 派生函数联动：`is_egg_layer / is_egg_soft / is_multiple_birth` 归零、`is_viviparous` 转真
- [x] 前提联动：`self/t_birth_type_egg`、`_multiple`、`_egg_soft` 六个前提随开关归零
- [x] `check_ovulation`：关带壳后不产新卵且排卵标记被消费
- [x] `get_multiple_birth_range`：关多胎后回退 `(1,1)`，开启时为种族值 `(4,12)`
- [x] `have_external_ovulation_chance`：关无壳后恒 False
- [x] `clear_birth_type_data(11)` 与 `(12)` 互不越界：各自只清自己那一族的卵/索引/卵块，无壳另清体外排卵机会
- [x] `clear_birth_type_data(2)`：`fetus_count>1` 归 1；单胎族的同卵双胞胎不被改动
- [x] 清除幂等：连续调用第二次返回"没有需要清除的数据"
- [x] 清除后 `entertainment_type` 中不再残留 175
- [x] `check_all_pregnancy` 分流：关带壳走胎生链不产卵，开启照常排卵
- [x] `_clear_soft_egg_race_pregnancy`：开关关闭时整体跳过（孕程保留），开启时照常清除，非无壳族不受影响
- [x] `update_settings`：旧存档（设置对象缺属性）补全为三项全开；已有的开关值不被覆盖
- [x] 面板层：基础设置栏绘制不报错；说明绘制不报错；关闭→开关置 0 + 存量清除 + `get_birth_type` 归一；再次点击恢复开启；取消确认时开关与存量均不变
- [x] `buildconfig.py` 全量重建无报错，新分类在生成物中齐备

### 6.2 游戏内整体测试（由用户执行）

- [ ] 系统设置 → 基础设置能看到`生殖方式开关`一行与 `[修改生殖方式开关]` 按钮；点名字能看到介绍（含换行）
- [ ] 进入子面板能看到三种生殖方式，默认均为「开启」；点名字看说明，点状态切换
- [ ] 关闭任一项弹出二次确认；选「取消」状态不变、存量不变；选「确认关闭」显示清除汇报且状态变灰
- [ ] 关闭带壳卵生后：卵生干员不再产卵，走正常受精→妊娠→生产；育儿室不再出现照料卵/保育员鉴定；怀孕总览面板不再有卵相关阶段
- [ ] 关闭无壳卵生后：无壳卵生干员绝顶时不再体外排卵，体内射精可正常受孕
- [ ] 关闭多胎胎生后：多胎种族受精只怀 1 胎，生产事件只取 1 次名
- [ ] 重新开启后行为恢复（新的排卵日起重新产卵/多胎判定）
- [ ] **重点**：关闭无壳卵生 → 让 12 族干员正常怀孕 → 存档 → 读档，孕程仍在（验证 §2.3-1 的 BUG 已堵）
- [ ] 旧存档载入提示"生殖方式设置已更新"，三项为开启，原有卵与多胎孕程不受影响
- [ ] Tk 与 Web 两种绘制模式下设置面板、子面板与确认框均正常

## 7. 风险与回滚

| 风险 | 说明 | 对策 |
| --- | --- | --- |
| 误触关闭导致存量被毁 | 子面板中状态按钮点击即切换 | 二次确认 + 红字"不可撤销"警告 + 说明文案明写；取消时不动任何数据 |
| 读档反复清孕程 | §2.3-1，最严重 | §4.7 守卫 + 单元测试与游戏内测试各一条专项 |
| 清除时漏掉某处存量 | 卵数据分散在角色与玩家收藏品两处 | 按 §2.4 全量清单逐项实现与断言 |
| `save_handle` 导入 `pregnancy_constant` 引入循环 | Core → System 方向 | `pregnancy_constant` 只依赖 `get_text`；单元测试已完整走过 `save_handle` 的导入链 |
| 关闭卵生后角色残留 `talent[20]受精` | 按设计保留并转为正常妊娠 | 记录于文档，非缺陷 |

**回滚**（三组可独立回滚）：
1. 开关本体：删 CSV 的 4 行 + 还原 `egg_handle` 的 `get_birth_type` + 删 `BIRTH_TYPE_SETTING_LIST` + 还原 `game_config` / `game_type` / `attr_calculation` 三处，重跑 `buildconfig.py`；
2. 面板入口与清除：删 `draw_option` 的 cid 13 特判与 4 个新方法、删 `clear_birth_type_data`（不影响开关本体）；
3. `save_handle` 守卫与设置补全：还原函数签名与调用（**必须与第 1 组一起回滚**，否则单独保留守卫会使旧存档迁移失效）。

存量清除**不可回滚**（数据已删），只能由玩家读旧档。

## 8. 改动文件清单

| 文件 | 类型 | 改动 |
| --- | --- | --- |
| `data/csv/System_Setting.csv` | 修改 | base 新增入口项 cid 13；文件末尾新增 `type=birth` 三行（cid 2/11/12，默认值 1） |
| `Script/Config/game_config.py` | 修改 | 新增 `config_birth_type_setting(_option)` 两个字典与 `load_system_setting` 的 `birth` 分支 |
| `Script/Core/game_type.py` | 修改 | `System_Setting` 新增 `birth_type_setting` 字段 |
| `Script/Design/attr_calculation.py` | 修改 | `get_system_setting_zero` 增加生殖方式设置的默认值循环 |
| `Script/System/Pregnancy_System/pregnancy_constant.py` | 修改 | 新增 `BIRTH_TYPE_SETTING_LIST`；订正 `BIRTH_TYPE_EGG_SOFT` 过时注释 |
| `Script/System/Pregnancy_System/egg_handle.py` | 修改 | 拆出 `get_race_birth_type`、新增 `is_birth_type_enabled`、`get_birth_type` 改为开关感知、新增 `clear_birth_type_data` |
| `Script/UI/Panel/system_setting.py` | 修改 | `draw_option` 的 cid 13 入口按钮 + 子面板/说明/切换/二次确认 4 个方法 |
| `Script/Core/save_handle.py` | 修改 | `_clear_soft_egg_race_pregnancy` 开关守卫、`_normalize_loaded_save_paths` 读开关、`update_settings` 补全生殖方式设置 |
| `.github/prompts/数据处理工作流/妊娠系统.md` | 修改 | §2 新增"生殖方式开关"条目 |
| `.github/prompts/数据处理工作流/系统设置系统.md` | 修改 | 新分类、字典/字段清单、核心方法、特殊设置处理第 4 条、设置类型详解 |
| `update.log` | 修改 | v0.67 新增段追加一条 |

**未改动**：`data/csv/Race.csv`（种族原始生育方式不动）、全部前提函数与 `constant_promise`、`Behavior_*.csv`、任何口上 CSV、`Script/Config/config_def.py`（`System_Setting` 列结构未变）、`tools/ArkEditor/`。

## 9. 不在本 Plan 范围

- 不给单胎胎生(1) 与 1% 同卵双胞胎加开关（用户已确认）。
- 不做逐种族/逐角色的生殖方式覆写，不在角色创建或多周目继承时提供选择。
- 不新增"当前生殖方式"的信息展示（身体信息面板、干员图鉴等）；如需要另开 plan。
- 不改 `take_chara_eggs`(5105) / `identify_held_eggs`(2053) 的指令前提 —— 采用"立即清除"口径后不存在孤儿卵，无需放宽。
- 不为存量卵提供"续跑到孵化完毕"的兼容模式（评估过，用户选择立即清除）。

## 10. 执行记录

### 10.1 实际改动

按 §8 清单逐文件落地，无遗漏。关键落点：

| 落点 | 实际 |
| --- | --- |
| CSV | base 入口项 cid 13（`option` 单值 `1`、默认 0）；末尾 `2/11/12,birth,...`，选项 `关闭，改为单胎胎生\|开启`，默认 1 |
| 装载 | `game_config.load_system_setting` 的 `birth` 分支不取余，`config_birth_type_setting` 键即 2/11/12 |
| 生效点 | `egg_handle.get_birth_type`（唯一），`get_race_birth_type` 供清理与迁移 |
| 清除 | `egg_handle.clear_birth_type_data`，返回中文汇报文案（如"已清除1名干员持有的2枚卵（其中博士持有1枚）"） |
| 面板 | `system_setting.draw_option` cid 13 特判 + `birth_type_setting_panel_draw` / `birth_type_name_info` / `change_birth_type_setting` / `confirm_close_birth_type` |
| 守卫 | `save_handle._clear_soft_egg_race_pregnancy(character, soft_egg_enabled)`，开关在角色循环外读一次 |

### 10.2 与计划的偏差

1. **交互形态在规划后被推翻一次**：v1 的"基础设置三个并列开关项"按用户要求改为 v2 的"一个入口 + 子面板"，连带把开关存储从 `base_setting` 迁到独立的 `birth_type_setting`，改动文件从 5 个增加到 7 个（多出 `game_config.py`、`game_type.py`、`attr_calculation.py`，少了原计划中的 `BIRTH_TYPE_SETTING_CID` 映射常量——cid 直接取生育方式编号后不再需要）。
2. **`update_settings` 需要额外的 `hasattr` 补空字典**：v1 计划里开关值寄生在既有的 `base_setting` 上，无此问题；独立字段后旧存档的设置对象根本没有该属性，直接 `len()` 会 AttributeError（§2.3-3）。
3. **本地化未能构建**：`buildpo.py` 依赖 xgettext 产出的 `erArk.pot`、`buildmo.py` 依赖未安装的 `polib`，两者在本机均无法执行；且 `buildpo.py` 中途失败会删除 `erArk_py.po`，已 `git checkout` 还原。新增的 `.py` 文案在缺 PO 条目时由 gettext 回落到中文原串，显示正常。CSV 侧文案已由 `buildconfig.py` 写入 `erArk_csv.po`。
4. **已知限制（记录于此，非缺陷）**：关闭卵生开关时保留角色的 `talent[20]受精`，该角色改走胎生链后会转为一次正常妊娠。

### 10.3 测试结果

§6.1 全部 16 组断言通过，**共 76 项，失败 0 项**（无头单元测试，脚本置于 scratchpad 未入库）。测试过程中补齐的 fixture 前置：`cache.rhodes_island.party_day_of_week` 与 `facility_open` 需预填（娱乐重掷会读），`update_settings` 需要 `character_data` / `ai_setting` / `rhodes_island` 三个键。

§6.2 游戏内整体测试留给用户执行，清单见上。
