# Plan 06：避孕套道具系统

- 状态：已实施（单元测试通过，游戏内整体测试待用户执行）
- 来源：用户需求 → 将避孕套从单一避孕道具完善为独立道具系统（存量记录 / 身体装饰 / 饮用 / 挤出）
- 预计改动量：约 22 个文件（新增 `Script/System/Item_System/` 道具系统目录 + 数据结构/结算/指令/前提/常量/显示/存档兼容 + 若干 CSV）
- 风险等级：中
- 适用代码快照：`master @ 680cb5f81`（v2026.8.20）

---

## 1. 目标

1. 博士**戴套射精**后，生成一条"用过的避孕套"记录（每次 +1 个，记录该次射精量 ml），存入玩家收藏品结构体中的存量池；存量池**保存到下一次 H 开始时清零**。
2. 用过的避孕套可作为**临时装饰**挂到交互对象的服装部位或头发上（显示"挂着 X 个"），可随时取回存量池。装饰在下一次 H 开始时**不清除**；但对方**换衣/洗衣时，服装部位上的装饰记录被去除**（头发上的不受影响）。
3. 新增**饮用指令**：玩家勾选存量池中若干个避孕套，要求对方喝掉其中精液；结算为少量残留口腔、绝大部分进入胃部的精液污浊，并联动饮精经验与饮精绝顶。
4. 新增**挤出指令**：玩家勾选若干个避孕套，消耗后将精液转移到对方指定的身体部位或服装部位上。
5. 饮用与挤出指令在 **H 模式与日常均可用**（日常需满足合意/态度类前提）。
6. 面板与道具专属逻辑收纳进新建的 `Script/System/Item_System/` 道具系统子目录（含自身设计文档，遵循 `Script/System/*` 各子系统惯例）。

## 2. 现状调查

### 2.1 道具与指令定义

- `data/csv/Item.csv:38` — 道具 cid **120** 避孕套（`Consumables` / `SP_use`，`h_item_id=13`）
- `data/csv/Body_Item.csv:19` — 身体道具 **13** ↔ 道具 120，`behavior_id=condom`
- `data/csv/InstructConfig.csv:336-337` — 现有指令 `6402 put_condom`（前提 `TARGET_IS_H|T_NPC_NOT_ACTIVE_H|NOW_NOT_CONDOM|HAVE_CONDOM`）、`6403 take_condom_out`
- 处理函数：`Script/System/Instruct_System/handle_instruct.py:2686-2694`（`handle_put_condom` / `handle_take_condom_out`）
- 消耗/穿戴结算：`Script/Settle/item_effect.py:927`（`handle_use_condom`，戴上时扣 `item[120]`，爱情旅馆顶级套房豁免）、`:1520` / `:1541`（穿戴标记开关）

### 2.2 现有数据结构

- `Script/Core/game_type.py:853` — `class PLAYER_COLLECTION`（玩家收集品结构体，经 `character_data[0].pl_collection` 持有，`:1622`）。内部字段多为以 NPC id 为键的字典（`npc_panties` / `npc_socks` 等），**新记录挂这里**。
- `Script/Core/game_type.py` 的 `BODY_H_STATE` 类：

| 行号 | 字段 | 说明 |
| --- | --- | --- |
| 391-399 | `body_item[13]` | 避孕套穿戴状态 `[名称, 有无bool, 结束时间]`，挂在**玩家**（角色0）身上 |
| 473-474 | `condom_count: [0, 0]` | `[0]`=本次H已用个数，`[1]`=套内总精液量ml，**仅用于展示** |

### 2.3 戴套射精分支（新系统的唯一接入点）

`Script/UI/Panel/ejaculation_panel.py:446-456`：

```python
if character_data.h_state.body_item[13][1] == False:
    # 正常路径：update_semen_dirty → calculate_semen_flow → 受孕判定
else:
    cache.shoot_position = 0
    character_data.h_state.condom_count[0] += 1
    character_data.h_state.condom_count[1] += semen_count
    character_data.h_state.body_item[13][1] = False   # 射精后自动脱落
```

戴套时**完全跳过**精液污浊写入与受孕判定，套内精液量目前只在 `dirty_panel.py:324-329` 输出一行文本，无其他消费方。

### 2.4 关键结算函数与钩子

- **加精液唯一正确入口**：`ejaculation_panel.update_semen_dirty(character_id, part_cid, part_type, semen_count, update_shoot_position_flag=False)`。自动处理当前量/累计量/等级重算/无意识记录/后穴精液灌肠；`part_type` 0=身体、1=穿着服装。**不要**直接改 `dirty.body_semen[x][1]`（会漏掉等级 `[2]` 和累计 `[3]`）。
- 身体部位索引（`data/csv/BodyPart.csv`）：**0 头发、2 口腔、15 胃部**；服装部位索引见 `data/csv/ClothingType.csv`（0 帽子 ~ 13 附属物）。
- "喝下去"的参考实现：`Script/Settle/default.py:7733-7744`（精液料理：加口腔污浊 + 精液经验24 + 饮精经验25）。`config_body_part_extra_flow[2]` = `B15-90`（口腔额外流通表，90% 直入胃）目前是**未接线的死配置**，本方案直接按"口腔 10% / 胃 90%"分配，不接线流通表。
- 饮精绝顶：`Script/Settle/orgasm_settle.py:105-111`（`talent[31]` 且 `h_state.shoot_position_body in [2, 15]` 时触发不计次绝顶）；经验积累 `:308-311`。
- **H 开始钩子**：`Script/Settle/default.py:5158` `handle_h_flag_to_1`，其 `if not character_data.sp_flag.is_h:` 分支（5178 行）仅在从非 H 首次进入 H 时执行——存量池清零挂这里。
- **换衣/洗衣钩子**：`Script/Settle/default_cloth.py`（约 544 / 579 / 616 / 653 / 680-695 行，穿脱与衣柜转移时的精液数据搬运）、`Script/Design/clothing.py:577-608`（衣柜精液清理/转移）、`Script/Settle/default.py` 淋浴洗衣相关结算（`handle_dirty_reset_in_shower` 一带）——服装部位装饰的去除挂这些位置。
- 旧存档兼容惯例：`Script/Core/save_handle.py:175` 附近的逐角色 `hasattr` 回填段。
- 新增指令流程参考：`Script/System/Instruct_System/指令系统整体逻辑.md` 第 9.1 节；指令内联模态面板写法参考 `handle_instruct.py:663`（`normal_panel.Close_Door_Panel(width)`，返回 `-1` 表示取消）。
- 口上 CSV 格式（`data/talk/sex/item/put_condom.csv`）：列为 `cid,behavior_id,adv_id,premise,context`，现有默认口上前提即 `high_1`。

## 3. 实施步骤

### 3.1 数据结构（`Script/Core/game_type.py`）

- **存量池**写在 `PLAYER_COLLECTION`（`:853`，经 `character_data[0].pl_collection` 访问）：

```python
self.used_condoms: List[int] = []
""" 用过的避孕套存量池，每个元素为该避孕套内的精液量(ml) """
```

- **装饰**写在**对应角色自己的 `DIRTY`**（污浊结构体）中：

```python
self.condom_decoration: Dict[tuple, List[int]] = {}
""" 挂在本角色身上作装饰的用过的避孕套
键为(部位类型, 部位cid)：部位类型 0=身体（仅头发0可用），1=服装部位
值为列表，每个元素为该避孕套内的精液量(ml) """
```

`attr_calculation.get_dirty_reset` 为原地重置已知字段，不会清掉 `condom_decoration`，装饰可在洗澡等污浊重置后存续。

- **行为目标标记**写在 `SPECIAL_FLAG`：

```python
self.condom_cloth_flag: int = 0
""" 当前避孕套装饰相关行为的目标类型，int [0身体部位（头发）,1服装部位] """
```

由挂装饰/取回装饰/挤出三个指令的处理函数在面板选择后写入玩家的 `sp_flag`，供口上前提区分（见 3.10、3.13）。

保留现有 `condom_count` 不动（H 末尾汇总展示继续使用）。

### 3.2 新增道具系统目录（`Script/System/Item_System/`）

遵循 `Script/System/*` 子系统惯例新建目录，避孕套的面板与数据操作逻辑都放在这里：

```text
Script/System/Item_System/
├── condom_handle.py      # 存量池/装饰的增删转移工具函数（供结算、换洗衣物钩子、前提调用）
├── condom_panel.py       # 避孕套选择面板（多选 + 部位选择）
└── 道具系统设计文档.md    # 子系统设计文档
```

`condom_handle.py` 至少提供：`add_used_condom(semen_count)`（射精时记录）、`clear_used_condoms()`（H 开始清零）、`move_to_decoration(...)` / `take_back_decoration(...)`（池↔装饰搬运）、`remove_cloth_decoration(character_id, part_cid=None)`（换洗衣物时去除服装部位装饰）、`get_decoration_count(character_id, part_type, part_cid)`（显示用）。

### 3.3 生成记录（`Script/UI/Panel/ejaculation_panel.py:447-456`）

在戴套分支的 `condom_count` 累加处追加调用：

```python
condom_handle.add_used_condom(semen_count)
```

### 3.4 清零钩子（`Script/Settle/default.py:5158` `handle_h_flag_to_1`）

在"首次进入H"分支（`if not character_data.sp_flag.is_h:`）内追加：进入 H 的是玩家或玩家的交互对象时，调用 `condom_handle.clear_used_condoms()`。装饰字典 `condom_decoration` **不清**。

### 3.5 换洗衣物与洗澡时去除装饰

装饰去除均为直接丢弃（不回存量池）：

- **服装部位**：在 2.4 列出的换衣/洗衣钩子处调用 `condom_handle.remove_cloth_decoration(...)`，头发上的不受影响：
  - `Script/Settle/default_cloth.py` 的穿脱/衣柜转移结算函数（约 544 / 579 / 616 / 653 / 680-695 行）：涉及的服装部位对应装饰去除
  - 洗衣结算（`Script/Design/clothing.py:577-608` 衣柜精液清理与 `Script/Settle/default.py` 淋浴洗衣一带）：全部服装部位装饰去除
- **污浊重置时全部清空**：`attr_calculation.get_dirty_reset` 内统一执行 `condom_decoration = {}`，因此角色**洗澡**（`handle_dirty_reset_in_shower`）或污浊全归零（`handle_dirty_reset`）时，身上全部装饰（头发+服装）一并清空（洗澡时服装装饰通常已被脱衣钩子先行清除）

实施时以"该部位的衣物发生了更换或清洗 / 角色进行了洗澡"为判定标准逐个核对上述函数，避免遗漏或误删。

### 3.6 新增 8 个指令（H版 4 个 + 非H版 4 个）

同一功能按模式拆为两套指令，**共用行为、面板与结算**（先例：`clyster` / `continue_clyster` 共用行为 `CLYSTER`）：

- **H 版**：SEX 类 / ITEM 子类，cid 64xx 段空闲号，`h_mode_show_type=2`（仅H显示），前提含 `TARGET_IS_H`
- **非H版**：OBSCENITY（猥亵）类 / ITEM 子类（先例：5101-5105 遥控玩具组），cid 50xx 段空闲号，instruct_id 加 `_daily` 后缀，`h_mode_show_type=1`（仅非H显示），前提含 `NOT_H` 与合意前提 `T_NORMAL_56_OR_UNCONSCIOUS_FLAG`

| 功能 | H版 instruct_id | 非H版 instruct_id | 行为 en_name |
| --- | --- | --- | --- |
| 挂上避孕套装饰（选套+选部位） | `hang_condom_decoration` | `hang_condom_decoration_daily` | `hang_condom_decoration` |
| 取回避孕套装饰 | `take_back_condom_decoration` | `take_back_condom_decoration_daily` | `take_back_condom_decoration` |
| 饮用避孕套精液（10%口腔/90%胃） | `drink_condom_semen` | `drink_condom_semen_daily` | `drink_condom_semen` |
| 挤出避孕套精液（选套+选部位全额转移） | `squeeze_condom_semen` | `squeeze_condom_semen_daily` | `squeeze_condom_semen` |

每个指令的配套改动（照 `put_condom` 全链路样例）：

1. **CSV**：`data/csv/InstructConfig.csv`（前提集合见 3.7）、`data/csv/Behavior_Data.csv`（duration 5 分钟，trigger `pl`）、`data/csv/Behavior_Introduce.csv`、`data/csv/Behavior_Effect.csv`（effect 挂**空结算 `9999`**——数据结算已在面板内完成，但行为必须存在于该表中，否则 `settle_behavior.py:398` 的 `talk.handle_talk` 不会触发口上）
2. **常量**（照 `PUT_CONDOM` 的既有位置逐个添加）：`Script/Core/constant/Behavior.py`、`BehaviorStr.py`、`Behavior_Int.py`、`CharacterStatus.py`、`Script/System/Instruct_System/Instruct.py`、`Script/Core/constant_promise.py`（**不新增效果 id**）
3. **处理函数**：`Script/System/Instruct_System/handle_instruct.py` 中加 `@add_instruct` 函数（8 个 handler 共用一个公共流程函数 `handle_condom_instruct_common`）：
   - **实行值判定**：先调 `instuct_judege.calculation_instuct_judege(0, 目标id, _("严重骚扰"))` 进行"严重骚扰"难度的实行值判定。⚠️ 判定必须在**打开选择面板之前**——面板确认时会直接结算数据，判定失败不能给出选择机会。返回 -1 直接中止；返回 0（判定失败）则结算为严重骚扰失败行为 `constant.Behavior.HIGH_OBSCENITY_ANUS` 后中止（与 `chara_handle_instruct_common_settle` 内置 judge 失败时的替换行为一致）
   - 判定通过后弹出 `Item_System/condom_panel.py` 的选择面板；面板确认时已直接完成数据结算，取消（返回 -1）则 return，否则走 `chara_handle_instruct_common_settle`（**不再传 judge**，避免二次判定）推进时间与触发口上
4. **结算函数**：写为 `condom_handle.py` 中的面板结算函数（`settle_hang` / `settle_take_back` / `settle_drink` / `settle_squeeze`），由面板在玩家确认时直接调用，不经过行为结算器，无需 `cache` 临时变量传递选择数据：
   - 饮用 `settle_drink`：对每个选中的套 `update_semen_dirty(t_id, 2, 0, int(ml*0.1), update_shoot_position_flag=False)` + `update_semen_dirty(t_id, 15, 0, ml - int(ml*0.1), update_shoot_position_flag=False)`；加精液经验24、饮精经验25与口喉快感（`common_default` 的通用函数）；设 `target_data.h_state.shoot_position_body = 15` 以联动饮精绝顶二段行为
   - 挤出 `settle_squeeze`：`update_semen_dirty(t_id, part_cid, part_type, 总ml, update_shoot_position_flag=False)`；目标为身体部位时追加 `calculate_semen_flow` 使精液自然流动；并写入 3.13 的目标标记
   - 挂装饰 `settle_hang` / 取回 `settle_take_back`：调 `move_to_decoration` / `take_back_decoration`，并写入 3.13 的目标标记
5. **口上**：见 3.10

### 3.7 新增前提（`Script/Design/handle_premise/handle_premise_H.py` + `constant_promise.py`）

| 前提 | 判定 |
| --- | --- |
| `USED_CONDOM_GE_1` | `len(cache.character_data[0].pl_collection.used_condoms) >= 1` |
| `T_CONDOM_DECORATION_GE_1` | 装饰字典中交互对象名下存在非空列表 |

指令前提组合：

- **H 版**：`HAVE_TARGET|T_NPC_NOT_ACTIVE_H|TARGET_IS_H|USED_CONDOM_GE_1`（取回装饰用 `T_CONDOM_DECORATION_GE_1` 代替 `USED_CONDOM_GE_1`）
- **非H版**：`HAVE_TARGET|NOT_H|USED_CONDOM_GE_1|T_NORMAL_56_OR_UNCONSCIOUS_FLAG`（取回装饰同上替换），合意由现有前提 `T_NORMAL_56_OR_UNCONSCIOUS_FLAG` 控制

同步 `tools/ArkEditor/csv/Premise.csv`。

### 3.8 结算效果 id

**不新增**结算效果 id：数据结算在面板确认时直接完成（见 3.6 第 4 点、3.9），`Behavior_Effect.csv` 中 4 个行为挂空结算 `9999` 仅用于保留口上触发链路。

### 3.9 选择面板（`Script/System/Item_System/condom_panel.py`）

- 内联模态样式（参考 `normal_panel.Close_Door_Panel` 返回 `-1` 取消的写法），供 4 个指令共用，按操作类型传参：
  - 第一步：列出存量池各套的编号与精液量 ml，支持多选（取回装饰时改为列出对方身上的装饰）
  - 第二步（挂装饰/挤出）：选择目标部位。挂装饰只列"头发 + 对方 `cloth.cloth_wear` 非空的服装部位"；挤出列全部身体部位 + 已穿着服装部位
  - **玩家确认后由面板直接调用 `condom_handle.settle_*` 完成数据结算**并返回 1，取消返回 `-1`
- 只用抽象绘制类（`Script/UI/Moudle/draw.py` 的 `NormalDraw` / `Button` 等），保证 Web 模式经 `web_draw_adapter` 自动兼容

### 3.10 默认口上（`data/talk/sex/item/` 下 4 个新 CSV）

按 `put_condom.csv` 的列格式（`cid,behavior_id,adv_id,premise,context`）为每个新指令各建一个 CSV。每个文件写 **5 条**口上，`adv_id=0`，cid 顺延，供随机显示。

前提分配：

- **挂装饰 / 取回装饰 / 挤出**三个文件：按每条文本描述的目标，前提用 `condom_operation_to_body`（针对头发的描述）或 `condom_operation_to_cloth`（针对衣物的描述），依赖 3.13 的行为目标标记。
- **饮用**文件：无部位区分，前提保持默认的 `high_1`。

示例（挂装饰）：

```csv
cid,behavior_id,adv_id,premise,context
0,hang_condom_decoration,0,condom_operation_to_body,{Name}把用过的避孕套系在了{TargetName}的发梢上……
3,hang_condom_decoration,0,condom_operation_to_cloth,{TargetName}红着脸站好不动，看着{Name}将装满精液的避孕套一个个挂上自己的衣角
```

### 3.13 身体/服装目标标记与前提

- `SPECIAL_FLAG.condom_cloth_flag`（见 3.1）：由 `condom_handle.settle_hang` / `settle_squeeze`（按面板选择的 `part_type`）与 `settle_take_back`（按第一个选中的装饰位置）在面板结算时写入。
- 新前提（`constant_promise.py` + `handle_premise_H.py`，同步 `tools/ArkEditor/csv/Premise.csv`）：

| 前提 | 判定 |
| --- | --- |
| `CONDOM_OPERATION_TO_BODY` | 玩家 `sp_flag.condom_cloth_flag == 0` |
| `CONDOM_OPERATION_TO_CLOTH` | 玩家 `sp_flag.condom_cloth_flag == 1` |

### 3.14 避孕套数量详细描述文本（`data/ui_text/condom_dirty.csv`）

仿照 `data/ui_text/dirty_full.csv` 的格式与文风新增，构建后经 `game_config.ui_text_data['condom_dirty']` 访问：

- 键格式：`{部位名}避孕套装饰{等级}`；部位覆盖**头发** + **全部 14 个服装部位**（帽子~附属物），共 15×5=75 条
- 等级与个数的对应（`condom_handle.get_decoration_level`）：1级=1个，2级=2个，3级=3~5个，4级=6~10个，5级=10个以上

### 3.11 界面显示

| 文件 | 改动 |
| --- | --- |
| `Script/UI/Panel/dirty_panel.py` | 污浊栏头发部位：开启详细污浊信息（`draw_setting[10]`）时按部位避孕套数量显示 3.14 的等级描述文本，**该部位已有污浊信息时先换行再显示，否则直接显示**；未开启时显示"挂着 X 个用过的避孕套"。H 末尾汇总（324-329 行）另追加存量池明细（个数与各套 ml）与对方各部位装饰个数 |
| `Script/UI/Panel/cloth_panel.py:96-125` | 各服装部位按同样的"详细=等级文本（已有污浊先换行）/简略=个数"规则显示 |
| `Script/System/Web_Draw_System/status_panel.py` | 服装段（625-639）与身体段（721-810）按同样规则同步 |
| `Script/UI/Panel/body_info_panel.py` | 无需改动：口部累计（113-123 行）读 `body_semen[2][3]` + `[15][3]`，饮用量自动计入 |

显示处统一经 `condom_handle.get_decoration_count(...)` / `get_decoration_level(...)` 取数。

### 3.12 旧存档兼容（`Script/Core/save_handle.py:175` 附近）

旧存档中的 `pl_collection` / `dirty` 对象缺少新字段，在逐角色 `hasattr` 回填段追加：

```python
pl_collection = getattr(character, "pl_collection", None)
if pl_collection is not None and not hasattr(pl_collection, "used_condoms"):
    pl_collection.used_condoms = []
dirty_data = getattr(character, "dirty", None)
if dirty_data is not None and not hasattr(dirty_data, "condom_decoration"):
    dirty_data.condom_decoration = {}
```

## 4. 构建与缓存重建

```bash
# CSV/常量改动后全量重建（生成 data.json / config_def.py / PO）
python buildconfig.py

# 口上与新指令名称涉及翻译词条时
python buildpo.py
python buildmo.py
```

注意：本机运行须使用 `.conda\python.exe`（裸 `python` 是 Store 空壳别名）。

## 5. 验证清单

### 5.1 单元测试（实施方执行）

不启动游戏整体流程，以脚本方式初始化缓存后直接调用函数验证：

- [ ] `condom_handle` 各工具函数：`add_used_condom` 追加正确；`clear_used_condoms` 只清池不清装饰；`move_to_decoration` / `take_back_decoration` 搬运前后总数与 ml 守恒；`remove_cloth_decoration` 只删服装部位、保留头发
- [ ] 饮用结算函数：口腔(2)/胃(15)的当前量/等级/累计量按 1:9 写入；经验 24/25 增加；`shoot_position_body` 置 15
- [ ] 挤出结算函数：目标身体/服装部位污浊数值正确；勾选的套被消耗
- [ ] 新前提函数在池空/非空、有无装饰时返回正确
- [ ] 旧存档兼容：构造缺字段的 `pl_collection` 对象走载入回填不报错
- [ ] `python buildconfig.py` 全量重建无报错，新常量/前提/效果在生成物中齐备

### 5.2 游戏内整体测试（由用户执行）

- [ ] debug 模式下戴套射精：存量池 +1，记录的 ml 与射精结算文本一致；`condom_count` 汇总不受影响
- [ ] H 结束后存量池保留；再次开始新 H 时存量池清零、装饰保留
- [ ] 挂装饰：头发与已穿着服装部位可选、未穿着部位不出现；`dirty_panel` / `cloth_panel` / Web 状态栏显示"挂着 X 个"
- [ ] 对方换衣/洗衣后服装部位装饰消失、头发装饰保留
- [ ] 饮用/挤出在 H 中与日常均可触发，前提过滤正常；口上随机显示
- [ ] 有 `talent[31]` 时饮用触发饮精绝顶
- [ ] 旧存档载入不报错；Tk 与 Web 两模式均正常

## 6. 风险与回滚

- **数据挂错位置**：存量池放 `PLAYER_COLLECTION`（玩家收藏品）、装饰放各角色 `DIRTY`（原地重置不丢数据）；勿放 `BODY_H_STATE`——H 结束时 `attr_calculation.py:269` `get_h_state_reset` 会重建该结构体导致数据静默丢失。
- **换洗衣物钩子遗漏**：`default_cloth.py` 中穿脱/衣柜转移函数较多，遗漏会导致换衣后装饰残留；实施时逐个核对 2.4 所列位置。
- **漏跑 buildconfig**：新常量/前提/效果与生成物不一致会在启动时 KeyError；CSV 改动后必须重跑。
- **tuple 键**：`condom_decoration` 内层用 `(part_type, part_cid)` 作键，pickle 存档无碍；若未来做 JSON 导出需转换键格式。
- **回滚**：还原上述代码文件与 CSV 新增行，删除 `Script/System/Item_System/` 目录，重跑 `buildconfig.py` 即可；新增字段对旧逻辑无侵入，存档中多余字段不影响读取。

## 7. 改动文件清单

| 文件 | 类型 | 改动 |
| --- | --- | --- |
| `Script/System/Item_System/condom_handle.py` | 新增 | 存量池/装饰数据操作工具函数 + 4 个面板结算函数（`settle_*`） |
| `Script/System/Item_System/condom_panel.py` | 新增 | 避孕套选择面板（多选 + 部位选择，确认时直接结算） |
| `Script/System/Item_System/道具系统设计文档.md` | 新增 | 子系统设计文档 |
| `Script/Core/game_type.py` | 修改 | `PLAYER_COLLECTION` 新增 `used_condoms`；`DIRTY` 新增 `condom_decoration`；`SPECIAL_FLAG` 新增 `condom_cloth_flag` |
| `Script/UI/Panel/ejaculation_panel.py` | 修改 | 戴套射精分支追加存量池记录 |
| `Script/Settle/default.py` | 修改 | `handle_h_flag_to_1` 首次进 H 时清零存量池 |
| `Script/Settle/default_cloth.py` | 修改 | 穿脱/衣柜转移时去除服装部位装饰 |
| `Script/Design/clothing.py` | 修改 | 换衣/脱衣/洗衣相关处去除服装部位装饰 |
| `Script/System/Instruct_System/handle_instruct.py` | 修改 | 4 个 `@add_instruct` 处理函数（面板取消则中止，否则走通用结算推进时间/口上） |
| `Script/System/Instruct_System/Instruct.py` | 修改 | 新指令常量 |
| `Script/Core/constant/Behavior.py` / `BehaviorStr.py` / `Behavior_Int.py` / `CharacterStatus.py` | 修改 | 新行为常量 |
| `Script/Core/constant_promise.py` | 修改 | 5 个新前提枚举 |
| `Script/Design/handle_premise/handle_premise_H.py` / `handle_premise/__init__.py` | 修改 | 新前提判定函数 |
| `Script/UI/Panel/dirty_panel.py` | 修改 | 污浊栏头发部位装饰显示（详细/简略）+ H 末尾存量池明细 |
| `Script/UI/Panel/cloth_panel.py` | 修改 | 服装信息栏装饰显示（详细/简略） |
| `Script/System/Web_Draw_System/status_panel.py` | 修改 | Web 模式装饰显示（详细/简略） |
| `Script/Core/save_handle.py` | 修改 | 旧存档 `pl_collection.used_condoms` / `dirty.condom_decoration` 回填 |
| `data/csv/InstructConfig.csv` / `Behavior_Data.csv` / `Behavior_Introduce.csv` / `Behavior_Effect.csv` | 修改 | 8 个新指令（H版 6429-6432 + 非H版 5047-5050）共用 4 个新行为；`Behavior_Effect` 挂空结算 `9999` 保留口上触发 |
| `data/talk/sex/item/`（4 个新 CSV） | 新增 | 每指令 5 条默认口上（挂装饰/取回/挤出按身体/服装前提区分，饮用为 `high_1`） |
| `data/ui_text/condom_dirty.csv` | 新增 | 头发+14服装部位×5级的避孕套装饰详细描述文本 |
| `tools/ArkEditor/csv/Behavior_Data.csv` / `Premise.csv` | 修改 | 编辑器副本同步 |
| `data/data.json`、`Script/Config/config_def.py`、`data/po/` | 重建 | 由 `buildconfig.py` 生成 |

## 8. 执行记录（2026-08-21）

### 8.1 实际编号分配

实施时核对了 CSV 与常量文件，实际使用的编号如下（与计划中的建议值略有出入）：

| 项目 | 编号 | 备注 |
| --- | --- | --- |
| 指令 cid | **6429-6432** | 计划建议的 6404-6407 已被尿道棉棒等占用，6429 起为 ITEM 段空闲号 |
| 行为 cid | **475-478** | 471-474 与 481+ 已占用；`Behavior_Int.py` 与主 CSV 存在历史不同步（474 在 CSV 是电动按摩棒、在 Int 是摘套），475-478 两边均空闲 |
| 结算效果 id | **1013-1016** | 紧接现有避孕套效果 1011/1012 |
| 前提 | `USED_CONDOM_GE_1` / `T_CONDOM_DECORATION_GE_1` / `T_NORMAL_56_OR_H_OR_UNCONSCIOUS` | 第三个为新增组合前提（56正常或H中或无意识），实现放 `handle_premise/__init__.py`，复用现有 `handle_t_normal_56_or_unconscious_flag` |

### 8.2 与计划的偏差

1. **行为时长**：挂装饰/取回装饰的 duration 用了 1 分钟（对齐 `put_condom`），饮用/挤出用 5 分钟；计划原文统一写 5 分钟。
2. **数据结构细化**：`condom_decoration` 实际为 `Dict[角色id, Dict[(部位类型,部位cid), List[ml]]]`（外层按角色分键），放在 `PLAYER_COLLECTION` 中统一由玩家持有。
3. **指令双模式显示**：利用 `InstructConfig.csv` 的 `h_mode_show_type=0`（全显示）实现 H 与日常均可用，比计划中"靠前提组合"更直接；合意前提 `T_NORMAL_56_OR_H_OR_UNCONSCIOUS` 仍保留做日常过滤。
4. **饮用附加结算**：按饮下总 ml 追加了口喉快感（状态21）结算，使饮精绝顶链路（需口喉快感绝顶触发）实际可达；仅设 `shoot_position_body=15` 不足以触发。
5. **换洗衣物钩子实际落点**：`clothing.py` 的 `get_npc_cloth` / `get_cloth_from_dormitory_locker` / `get_all_cloth_off` / `get_cloth_wear_zero_except_need` 四个集中函数 + `default_cloth.py` 的 `handle_wear_to_shower_locker`（全部位）/ `handle_foot_cloth_to_shower_locker`（部位10/11）。Web 模式单件脱衣（`web_server.py`）未挂钩，列为已知边界。
6. **挤出部位过滤**：面板中排除口腔(2)/子宫(7)/胃部(15)（内腔场景由饮用指令承担），尾巴/兽角/兽耳需对方有对应素质，服装部位仅列已穿着的。

### 8.3 实施产物

- 新增 `Script/System/Item_System/`（`__init__.py`、`condom_handle.py`、`condom_panel.py`、`道具系统设计文档.md`）
- 计划第 7 章清单中的全部文件均已按计划修改；另比计划多改了 `game_type.py` 的 `Cache` 类（新增 `condom_operation_data` 临时选择数据字段）
- 口上：4 个新 CSV 各 5 条，前提均为 `high_1`，内容覆盖日常/H中、头发/衣物、主动配合/羞涩等场景
- `python buildconfig.py` 全量重建通过，`data.json` / `Character_Talk.json` 中已确认包含新指令、新前提与新口上

### 8.4 单元测试结果

测试脚本（scratchpad，不入库）以"初始化配置与缓存后直接调用函数"的方式覆盖：

- [x] `condom_handle` 全部工具函数：追加/清零（只清池不清装饰）/挂装饰/取回（ml守恒）/消耗/换洗去除（只删服装、保留头发、支持指定部位）
- [x] 前提函数：池空/非空、有无装饰、H中组合前提放行
- [x] 饮用结算：池清空、口腔:胃≈1:9 且总量守恒、等级与累计量重算、经验24/25各按套数结算、口喉快感一次、`shoot_position_body=15`、临时选择数据清空
- [x] 挤出结算：挤到身体部位数值正确且产生流动任务、挤到已穿着服装部位数值正确
- [x] 旧存档兼容：`pl_collection` 缺字段时 `check_collection_data` 与 `save_handle` 回填分支均生效
- [x] H 开始清零钩子：`handle_h_flag_to_1` 首次进 H 清池、保留装饰、`is_h` 置位
- [x] 换洗衣物钩子：`get_cloth_wear_zero_except_need` 后服装装饰清除、头发装饰保留
- [x] 注册一致性：行为常量、行为配置（duration）、指令处理函数、指令前提、前提函数注册表均包含新增项

全部断言通过（详见下方 8.5 结论）。

### 8.5 结论与遗留

- 单元测试全部通过；游戏内整体测试（Tk/Web 两模式的界面显示、口上随机、前提过滤、旧存档载入）由用户执行（见 5.2 清单）。
- 已知边界与计划一致：装饰跟随部位而非具体衣物；Web 单件脱衣不触发装饰去除；`condom_decoration` tuple 键仅适用于 pickle 存档。

### 8.6 二次修改记录（2026-08-21）

按用户要求进行了四项调整，代码与本方案文件已同步：

1. **装饰存储位置迁移**：`condom_decoration` 从玩家 `pl_collection` 移到**对应角色自己的 `dirty`**（`DIRTY` 结构体），键简化为 `(部位类型, 部位cid)`。已核实 `get_dirty_reset` 为原地重置已知字段，装饰在洗澡等污浊重置后存续；`save_handle` 回填与 `condom_handle.check_dirty_data` 兜底同步调整。
2. **新增详细描述文本**：`data/ui_text/condom_dirty.csv`，键 `{部位名}避孕套装饰{等级}`，头发+14服装部位×5级共75条，文风对齐 `dirty_full.csv`；等级换算 `get_decoration_level`（1/2/3-5/6-10/10+ → 1~5级）。
3. **污浊栏显示**：Tk（`dirty_panel` 头发部位、`cloth_panel` 各服装部位）与 Web（`status_panel`）在开启详细污浊信息时按数量等级显示上述文本，该部位已有污浊信息时先换行再显示，否则直接显示；未开启时仍显示个数。
4. **身体/服装目标标记与口上前提**：`SPECIAL_FLAG.condom_cloth_flag`（0身体/1服装）由挂装饰/挤出（按 `part_type`）与取回装饰（按第一个选中位置）的指令处理函数写入；新前提 `CONDOM_OPERATION_TO_BODY` / `CONDOM_OPERATION_TO_CLOTH` 读取该 flag；挂装饰/取回/挤出三个口上 CSV 的每条前提已按文本内容分配为对应前提（饮用保持 `high_1`）。ArkEditor `Premise.csv` 已同步。

二次修改后重跑 `buildconfig.py` 与全部单元测试（新增：装饰存储位置与 dirty 重置存续、等级换算、condom_dirty 75 条文本全覆盖校验、flag 前提判定与注册），58 项全部通过。

### 8.7 三次修改记录（2026-08-21）

按用户要求去掉了面板与结算之间的临时变量桥接，改为**面板确认时直接结算**：

1. **删除 `cache.condom_operation_data`**（`game_type.py` 的 `Cache` 类字段移除）。
2. **结算迁移**：`item_effect.py` 中 4 个行为结算函数与 `constant_effect.py` 的效果 id 1013-1016 全部删除；结算逻辑改写为 `condom_handle.py` 的 `settle_hang` / `settle_take_back` / `settle_drink` / `settle_squeeze`，由 `condom_panel.Condom_Select_Panel.draw()` 在玩家确认选择后直接调用；`condom_cloth_flag` 的写入也随之移入结算函数。
3. **指令处理函数简化**：只负责"开面板 → 取消则中止 → 走 `chara_handle_instruct_common_settle` 推进时间并触发口上"。
4. **关键约束**：`settle_behavior.py:398` 只对存在于 `Behavior_Effect.csv` 的行为触发口上（`talk.handle_talk`），因此 4 个行为在该表中的行**不能删除**，改挂空结算 `9999`；ArkEditor `Effect.csv` 中的 1013-1016 行已删除。
5. 副作用说明：结算不再经过行为结算器，饮用的经验/口喉快感变化不会出现在行动结算的数值变化展示中（数据本身正常结算）。

三次修改后重跑 `buildconfig.py` 与全部单元测试（结算测试改为直接调用 `condom_handle.settle_*`，新增各结算函数与 flag 联动、口上触发链路存在性校验），64 项全部通过。

### 8.8 四次修改记录（2026-08-21）

按用户要求补充：**挂在头发上的装饰避孕套会在对方洗澡时被去除**。

- `condom_handle.py` 新增 `remove_body_decoration(character_id)`：去除身体部位（头发）上的装饰记录（丢弃，不回池），服装部位不受影响。
- 钩子：`Script/Settle/default.py` 的 `handle_dirty_reset_in_shower`（洗澡按比例清洗结算，交互对象版本 `handle_target_dirty_reset_in_shower` 委托到它，一处覆盖两处）与 `handle_dirty_reset`（污浊全归零）末尾各追加调用。
- 方案文件 3.5 节、设计文档生命周期一节与 `tem.md` 公告已同步；单元测试新增洗澡去除头发装饰（保留服装装饰不受影响验证）用例，68 项全部通过。

### 8.9 五次修改记录（2026-08-21）

按用户要求将指令拆分为 H / 非H 两套：

- **原 4 个指令（6429-6432）改为 H 专用**：`h_mode_show_type` 0→2，前提改为 `HAVE_TARGET|T_NPC_NOT_ACTIVE_H|TARGET_IS_H|USED_CONDOM_GE_1`（取回装饰相应替换），去掉组合前提 `T_NORMAL_56_OR_H_OR_UNCONSCIOUS`。
- **新增 4 个猥亵-道具类指令（5047-5050，`*_daily`）**：`OBSCENITY`/`ITEM`，`h_mode_show_type=1`（仅非H），`tired_type=1`，前提 `HAVE_TARGET|NOT_H|USED_CONDOM_GE_1（或 T_CONDOM_DECORATION_GE_1）|T_NORMAL_56_OR_UNCONSCIOUS_FLAG`。
- **共用行为**：daily 版复用原行为 cid 475-478（先例：`clyster`/`continue_clyster` 共用行为），因此行为/口上/结算/常量均无需新增，仅加了 `Instruct.py` 4 个指令常量与 `handle_instruct.py` 4 个处理函数。
- 组合前提 `T_NORMAL_56_OR_H_OR_UNCONSCIOUS` 保留注册（口上/事件仍可使用），仅不再被指令引用。
- 6429 行的 `body_parts` 保持为空（用户手动调整），5047 同样置空。

### 8.10 六次修改记录（2026-08-21）

按用户要求为全部 8 个避孕套指令加上**"严重骚扰"难度的实行值判定**：

- 8 个 handler 重构为共用公共流程函数 `handle_condom_instruct_common(mode, behavior_id)`。
- 判定**前置到打开选择面板之前**（面板确认时直接结算数据，失败不能给出选择机会），因此不使用 `chara_handle_instruct_common_settle` 的 `judge` 参数（那会在结算阶段才判定），而是 handler 内直接调 `instuct_judege.calculation_instuct_judege(0, 目标id, _("严重骚扰"))`：
  - 返回 -1 → 静默中止；
  - 返回 0（失败）→ 结算为严重骚扰失败行为 `HIGH_OBSCENITY_ANUS`（与通用结算内置的 judge 失败替换表一致）；
  - 通过 → 打开面板，确认后走通用结算（不再传 judge，避免二次判定与二次绘制）。
- 实行值细节：判定含好感/信赖/状态/刻印/陷落/催眠/监禁/睡眠等修正，debug 模式 +99999 自动通过；玩家为目标时必过。
- 同步更新：流程文档《新增指令工作流》第 4 章新增实行值判定小节，skill（两份）第四步补充 judge 说明；单元测试以替换桩方式覆盖公共流程函数的三个分支。
- **洗澡装饰清理实现收敛**（用户优化）：8.8 的 `remove_body_decoration` 钩子方案被更彻底的实现取代——`attr_calculation.get_dirty_reset` 内统一 `condom_decoration = {}`（用户直接修改），污浊重置（洗澡/归零）时清空该角色全部装饰。`condom_handle.remove_body_decoration` 函数与 `default.py` 两处钩子调用已删除，测试断言按新语义反转（重置后装饰清空而非存续）。
