# Plan 20：做饭面板记忆上一次选择的烹饪模式与制作数量

- 状态：已实施（2026-09-06，单元测试 55/55 通过，见 §10；游戏内整体测试由用户执行）
- 来源：用户需求 → "记忆上一次做饭选择的模式"；规划阶段确认扩展为「烹饪模式 + 制作数量」，且三个入口各自独立记忆
- 预计改动量：2 个源码文件（约 45 行）+ 1 个文档 + `update.log`
- 实际改动量：2 个源码文件 44 行 + 1 个文档 3 处 + `update.log` 1 条
- 风险等级：低（纯 UI 偏好记忆，不触碰任何数值结算与行为循环）
- 适用代码快照：`master @ 6e3ef2bea`（v0.66）

---

## 1. 目标

1. 做饭面板的**烹饪模式**（标准/精细）在关闭面板后被记住，下次打开时自动沿用，而不是每次回到「标准模式」。
2. 二级确认页的**制作数量**同样被记住，下次打开时自动沿用（受当次可制作上限钳制）。
3. **普通做饭 / 泡咖啡加料 / 调酒**三个入口各自独立记忆，互不干扰。
4. 记忆值随存档持久化（读档后仍生效），旧存档载入不报错。
5. 不改变现有任何做饭数值、题库、结算逻辑；不新增面向玩家的可翻译文本。

## 2. 现状调查

### 2.1 关键代码落点

做饭主面板：`Script/System/Cooking_System/make_food_panel.py`

| 位置 | 内容 |
| --- | --- |
| `:42-55 Make_food_Panel.__init__` | `:50 self.make_food_type`（0 普通做饭 / 1 泡咖啡 / 2 调酒）、`:52 self.special_seasoning = 0`、`:54 self.cook_mode = 0` |
| `:217-255 draw()` | 绘制标准/精细按钮：选中态 `draw.CenterDraw` + `style="gold_enrod"`，未选中 `draw.CenterButton` → `cmd_func=self.change_cook_mode, args=(0,)/(1,)` |
| `:262-272 draw()` | 主面板品质预测，`cook_mode == 1` 时上限 `min(base+4, get_max_food_quality())` |
| `:288 / :297 / :338 / :345` | 把 `cook_mode` 打包进元组 `(菜谱id, 名字, special_seasoning, cook_mode)` 交给 `SeeFoodListByFoodNameDraw`（`:297/:345` 是占位空项 `"-1"`） |
| `:359-365 change_cook_mode()` | 函数体只有 `self.cook_mode = cook_mode` |
| `:645-656 SeeFoodListByFoodNameDraw.__init__` | 形参注解 `text: Tuple[str, str, int, int]`，`:655 self.cook_mode = text[3]`；`:677-683` 占位项提前 return |
| `:721-747 make_food_for_sure()` | `:742-746` 算 `max_count`（上限 10，药物调味受 `character_data.item[调味cid]` 限制），`:747 make_count = 1` |
| `:824-836` | `[-1]/[+1]/[最大]` 调整数量，`:830 [确认制作]` 分支调 `self.make_food(...)` |
| `:856-862 make_food()` | 精细模式**且** `cooking.has_cook_question_library()` 为真时才进答题流程 |

三个入口：`Script/UI/Flow/normal_flow.py:133`（做饭）、`:442`（`make_food_type=1` 泡咖啡）、`:449`（`make_food_type=2` 调酒）。**每次进入都新建面板对象**，这就是选择丢失的直接原因。

### 2.2 可复用的既有实现（同文件内先例）

同一个面板的**筛选与排序**早已实现了完全一样的记忆需求：

- 字段定义：`Script/Core/game_type.py:1295-1304`，`class Rhodes_Island` 内的 `makefood_filter_type` / `makefood_filter_difficulty` / `makefood_filter_time` / `makefood_sort_type` / `makefood_sort_order`
- 写入：`make_food_panel.py:525-550`（`toggle_filter_type` / `set_filter_*` / `clear_filter*`）、`:626-632`（`set_sort_type` / `set_sort_order`）
- 读取：`:444 / :469 / :492 / :575 / :598`（绘制选中态时**直接读 cache，不做实例镜像**）
- 业务消费：`Script/System/Cooking_System/cooking.py:425-429`

本计划完全照抄这一套：字段挂 `Rhodes_Island`，面板直接读写 cache。

其他同类先例（本次不采用，见 §3.1）：`Script/UI/Panel/all_npc_position_panel.py:51-53 + :198-212`（实例镜像 + 双写）、`Script/System/Pregnancy_System/pregnancy_panel.py:376-385`（直读 cache）。

### 2.3 已知陷阱与硬约束

1. **存档跨版本补齐只补顶层缺失 key，不补 dict 的子键**。`Script/Core/save_handle.py:586-620 update_dict_with_default()`：`:600-602` 补缺失 key；`:610-611` 仅当 value 有 `__dict__`（即类实例）时递归——**普通 dict 没有 `__dict__`**，会落到 `:613`，而两边类型相同（dict vs dict）时什么都不做。
   → **本计划的两个 dict 字段，读取必须一律走 `.get(键, 默认值)`，绝不可直接下标**，否则将来新增第 4 种 `make_food_type` 时老存档会 `KeyError`。
2. `:613` 的类型修复分支显式排除了 int/float，所以**脏 int 值（如 `2`、`-1`）不会被存档迁移修掉**，需要在面板侧自行钳制。
3. 旧存档缺整个字段是安全的：`input_load_save`（`save_handle.py:372-411`）先造 `new_cache.rhodes_island = basement.get_base_zero()`（`:383`，内部即 `game_type.Rhodes_Island()`），再于 `:411` 递归补默认值 → `Rhodes_Island` 的新增字段会被自动补上，**无需写迁移代码**。
4. **同名不同类**：`Script/UI/Panel/food_shop_panel.py:166` 也有一个 `SeeFoodListByFoodNameDraw`，与做饭面板里的是**两个不相干的类**。本计划只动 `make_food_panel.py` 里的那个，food_shop 的不要碰。
5. `备份/handle_instruct_20260117_152717.py:1635` 是历史备份文件，不参与运行，不改。
6. 新游戏与新周目走 `basement.get_base_zero()`（`Script/UI/Flow/creator_character_flow.py:40`、`Script/UI/Panel/new_round.py:835`）重建 `rhodes_island`，因此记忆值会随新周目一起重置——与筛选排序行为一致，属预期。
7. 模块级 `cache = cache_control.cache`（`make_food_panel.py:10`）是 import 期绑定；读档走的是 `cache.__dict__.update(...)` 原地更新，别名依然有效（`makefood_filter_*` 早已依赖这一点）。**仅无头测试需注意**：若要重绑定 `cache_control.cache`，必须在 import `make_food_panel` 之前完成。

### 2.4 引用全量清单

- `Make_food_Panel(` 实例化点：`normal_flow.py:133 / :442 / :449`（外加备份文件 1 处，不改）
- `Make_food_Panel` 内 `self.cook_mode` 读写点：`:54`（初始化）、`:223 / :240`（按钮选中态）、`:264 / :268`（品质预测）、`:288 / :297 / :338 / :345`（元组打包）、`:365`（写入）
- `SeeFoodListByFoodNameDraw` 内 `self.cook_mode`：`:655`（解包）、`:739`、`:857` —— 属另一个类，本次**不改其取值语义**
- `make_count` 出现点：`:743-747`、`:754`、`:774`、`:825 / :827 / :829`、`:831`、`:866`、`:899-903`、`:909`
- 全仓库除 `make_food_panel.py` 外无任何 `cook_mode` 引用（已 grep 确认）

## 3. 设计决策

### 3.1 烹饪模式用 `@property` 转发到 cache，不做实例镜像

- **选**：删掉 `self.cook_mode` 实例字段，改为一对 `@property` / `@setter` 读写 `cache.rhodes_island.makefood_cook_mode`。这样 `:223/:240/:264/:268/:288/:297/:338/:345/:365` 九个读写点**一行都不用改**，改动面收敛到 `__init__` 一处，也不可能出现"漏改一处读取点"。仓库已有 9 处 `@property` 先例（`game_type.py:753/757`、`Script/System/Instruct_System/instruct_meta.py:75`、`Script/System/Web_Draw_System/dialog_box.py:260+`），不是外来写法。
- **弃**：实例镜像 + 双写（`all_npc_position_panel.py` 那套）。同文件的筛选/排序全都不用镜像，引入镜像会让一个类里两套范式并存；且 `cook_mode` 要被打包进元组传给子绘制对象，一旦镜像与 cache 分叉，会出现"按钮显示标准模式、实际按精细模式做饭"这类极难定位的幽灵 BUG。
- **弃**：把九个读取点逐个替换成 `cache.rhodes_island.makefood_cook_mode.get(...)`。编辑点多 9 倍、收益为零，且 `:288/:297/:338/:345` 四行在长表达式内嵌，行宽会明显变长。

### 3.2 按 `make_food_type` 分入口记忆，字段用 `Dict[int, int]`

三个入口各自独立（规划阶段已确认）。用两个 `Dict[int, int]`（键 = `make_food_type`）而非六个扁平字段：字段少、语义清楚、将来加第 4 种做饭类型无需再改 `game_type.py`。代价是必须遵守 §2.3 的 `.get()` 纪律，已写进 §4 的每一处改动。

### 3.3 字段挂 `Rhodes_Island` 而非 `Cache` 根

`Cache` 根确有 UI 偏好先例（`game_type.py:1898-1905`），但选 `Rhodes_Island` 的理由更强：① 与已有的 5 个 `makefood_*` 兄弟字段聚拢，`grep makefood_` 一把捞全；② 生命周期一致——新周目时与筛选排序一起重置，不会出现"筛选清空了但烹饪模式还留着"的不一致；③ 存档迁移待遇完全相同（§2.3 第 3 条）。

### 3.4 制作数量的记忆时机与钳制

- **写回时机**：只在点击 `[确认制作]` 时写回**玩家请求的份数**（不是因材料不足而实际做出的 `real_count`）。取消不写回。
- **恢复时钳制**：`make_count = min(max(1, 记忆值), max_count)`。`max_count` 本身受药物库存限制（`:744-746`），所以"上次做 10 份、现在药只剩 2 个"会显示 2 份而非报错。
- **已知限制**（记录于此，非缺陷）：上一条钳制发生后若玩家直接确认，会把被钳低的份数写回记忆。可接受。

### 3.5 `[重置]` 按钮不重置这两项

`clear_filter_and_sort()`（`:546-550`）对应的 `[重置]` 按钮位于「○筛选：」视觉块内，语义是清筛选与排序；烹饪模式与制作数量始终以高亮按钮/明文显示，不存在"隐藏状态被遗忘"的救援需求。一并重置反而会抵消本功能。

### 3.6 子绘制对象通过元组第 5 项拿到 `make_food_type`

`make_food_for_sure()` 是 `SeeFoodListByFoodNameDraw` 的方法，该类原本不知道自己属于哪个入口。把元组从 4 元扩为 5 元 `(cid, 名字, special_seasoning, cook_mode, make_food_type)` 是最小改动（4 个打包点 + 1 个解包点），且不破坏既有的 `text[0..3]` 契约。

## 4. 详细改动步骤

### 4.1 新增缓存字段（`Script/Core/game_type.py:1304` 之后）

在 `class Rhodes_Island.__init__` 内，紧接 `makefood_sort_order` 及其 docstring（`:1303-1304`）之后、`:1306 # 医疗部` 之前插入，保持 `makefood_*` 字段连续无空行：

```python
        self.makefood_cook_mode: Dict[int, int] = {0: 0, 1: 0, 2: 0}
        """ 做饭记忆：烹饪模式（0标准模式，1精细模式），键为做饭类型（0普通做饭/1泡咖啡/2调酒） """
        self.makefood_make_count: Dict[int, int] = {0: 1, 1: 1, 2: 1}
        """ 做饭记忆：制作数量，键为做饭类型（0普通做饭/1泡咖啡/2调酒） """
```

（`Dict` 已在该文件顶部 import，无需新增 import。）

### 4.2 烹饪模式改为读写缓存（`Script/System/Cooking_System/make_food_panel.py`）

**4.2a 替换 `:54-55`**（原 `self.cook_mode = 0` 及其 docstring）为值域校验；两个新字段各做一次 `isinstance` 兜底：

```python
        # 烹饪模式与制作数量改为按做饭类型记忆在罗德岛数据里（与做饭面板的筛选/排序一致）
        # 进入面板时做一次值域校验，防止旧存档或模组写入的非法值导致两个模式按钮都不高亮
        if not isinstance(cache.rhodes_island.makefood_cook_mode, dict):
            cache.rhodes_island.makefood_cook_mode = {}
        if not isinstance(cache.rhodes_island.makefood_make_count, dict):
            cache.rhodes_island.makefood_make_count = {}
        if cache.rhodes_island.makefood_cook_mode.get(self.make_food_type, 0) not in {0, 1}:
            cache.rhodes_island.makefood_cook_mode[self.make_food_type] = 0
```

放在 `__init__` 而非 `draw()` 的理由：三个入口必经 `__init__`，一处覆盖全部；且必须在 `:50 self.make_food_type` 赋值**之后**。

**4.2b 在 `__init__` 末尾与 `def draw(self)`（现 `:57`）之间**插入 property 对：

```python
    @property
    def cook_mode(self) -> int:
        """
        当前的烹饪模式（读罗德岛缓存，按做饭类型记忆玩家上一次的选择）
        Return arguments:
        int -- 烹饪模式：0标准，1精细
        """
        return cache.rhodes_island.makefood_cook_mode.get(self.make_food_type, 0)

    @cook_mode.setter
    def cook_mode(self, cook_mode: int):
        """
        设置烹饪模式并写回罗德岛缓存，使下次打开同类型面板时沿用
        Keyword arguments:
        cook_mode -- 烹饪模式：0标准，1精细
        """
        cache.rhodes_island.makefood_cook_mode[self.make_food_type] = cook_mode
```

**4.2c 其余读写点一律不动**：`:223 / :240 / :264 / :268 / :288 / :297 / :338 / :345`、`:359-365 change_cook_mode`、`:546-550 clear_filter_and_sort` 全部保持原样。

### 4.3 元组扩为 5 元，把 `make_food_type` 传给子绘制对象

- `:288`：`food_name_list = [(x[0], x[1], self.special_seasoning, self.cook_mode, self.make_food_type) for x in food_name_list]`
- `:297`（占位空项）：`food_name_list.extend([("-1", "", self.special_seasoning, self.cook_mode, self.make_food_type)] * pad_count)`
- `:338`、`:345`：`change_panel()` 里同样的两行做同样的追加
- `:646` 形参注解改为 `text: Tuple[str, str, int, int, int]`
- `:655-656` 之后追加解包（**必须在 `:677` 占位项 `return` 之前**）：

```python
        self.make_food_type = text[4]
        """ 做饭类型：0普通做饭，1泡咖啡，2酒类 """
```

### 4.4 制作数量的恢复与写回（`make_food_for_sure()`）

**4.4a 替换 `:747`**（原 `make_count = 1`）：

```python
        # 沿用上次在同类型做饭面板中选择的制作数量，并按本次可制作上限钳制
        remember_count = cache.rhodes_island.makefood_make_count.get(self.make_food_type, 1)
        if not isinstance(remember_count, int) or remember_count < 1:
            remember_count = 1
        make_count = min(remember_count, max_count)
```

**4.4b 在 `:830` 的 `[确认制作]` 分支内、`self.make_food(...)` 之前**插入写回：

```python
            elif yrn == confirm_draw.return_text:
                # 记忆本次的制作数量，供下次打开同类型做饭面板时沿用
                cache.rhodes_island.makefood_make_count[self.make_food_type] = make_count
                self.make_food(make_food_time, make_count)
```

### 4.5 同步文档 `.github/prompts/数据处理工作流/食物系统.md`

- 缓存字段表（`:125` 的 `makefood_sort_type/order` 行之后）追加一行：
  `| makefood_cook_mode / makefood_make_count | Dict[int,int] | 做饭面板的烹饪模式与制作数量记忆，键为做饭类型（0做饭/1泡咖啡/2调酒），三入口各自独立，随新周目重置 |`
- `:135` 的流程描述补一句：该烹饪模式记忆在 `cache.rhodes_island.makefood_cook_mode`，下次打开同类型面板时沿用
- `:138` 的「批量数量」条目补一句：数量同样记忆在 `cache.rhodes_island.makefood_make_count`，恢复时按当次上限钳制

### 4.6 更新 `update.log`

用 skill `update-changelog` 追加一条「调整」类条目，形如：
`调整：（做饭）做饭面板现在会记忆上一次选择的烹饪模式与制作数量，做饭/泡咖啡/调酒三个入口各自独立记忆`
具体标签与追加位置以该 skill 的体例为准。

## 5. 构建与缓存

**本次无需任何构建步骤**：没有改动 CSV / 常量 / 地图，也**没有新增任何 `_()` 可翻译文本**（新增的全部是注释与 docstring），因此不需要跑 `buildconfig.py` / `buildpo.py` / `buildmo.py`。

单元测试脚本用本机 conda 解释器执行（裸 `python` 是 Store 空壳别名）：

```bash
.conda\python.exe <scratchpad>\test_cook_mode_memory.py
```

## 6. 验证清单

### 6.1 单元测试（实施方执行）

无头脚本写在 scratchpad（不入库），fixture 参照 skill `headless-game-test` 的模式 A。本用例特有的 fixture 要点：`cache.all_system_setting = attr_calculation.get_system_setting_zero()`、`cache.rhodes_island = basement.get_base_zero()`、`cooking.init_recipes()`、玩家 `ability[43]`（料理技能）非 0、`character_data.item` 用 `attr_calculation.get_item_zero({})` 初始化（`:196` 会无条件下标药物 cid）；**`import make_food_panel` 必须发生在 `cache_control.cache` 重绑定之后**。

- [ ] `game_type.Rhodes_Island()` 与 `basement.get_base_zero()` 上两个新字段存在，默认分别为 `{0:0,1:0,2:0}` / `{0:1,1:1,2:1}`
- [ ] 置 `makefood_cook_mode[0] = 1` 后新建 `Make_food_Panel(80)`，`panel.cook_mode == 1`，且 cache 未被 `__init__` 改回 0（这是"每次回到标准模式"的正向回归断言）
- [ ] `panel.change_cook_mode(1)` → cache 为 1；再 `change_cook_mode(0)` → cache 为 0（读写双向都穿透 cache）
- [ ] `"cook_mode" not in Make_food_Panel(80).__dict__`（锁死"不存在第二份状态"这条设计约束）
- [ ] 三入口独立：`Make_food_Panel(80).change_cook_mode(1)` 后，`Make_food_Panel(80, make_food_type=1).cook_mode == 0`、`make_food_type=2` 同样为 0
- [ ] 值域校验：把 `makefood_cook_mode[0]` 依次设为 `2` / `-1` / `"1"` / `None`，每次新建面板后被钳回 `0`；设为 `0` / `1` 时不被改动
- [ ] 字段被写成非 dict（如 `0`）时新建面板不抛异常，且被重置为可用的 dict（两个字段各测一次）
- [ ] 子键缺失兼容：`makefood_cook_mode = {}`（模拟老存档 dict 缺键）时 `panel.cook_mode == 0` 不抛 `KeyError`；`makefood_make_count = {}` 同理
- [ ] 元组打包：设 mode=1 后调 `panel.change_panel(_("主食"))`，断言 `all(t[3] == 1 and t[4] == panel.make_food_type for t in panel.handle_panel.text_list)`
- [ ] 解包契约：`SeeFoodListByFoodNameDraw((cid, name, 0, 1, 2), 20, False, False, 0)` 的 `cook_mode == 1`、`make_food_type == 2`
- [ ] 数量钳制：置 `makefood_make_count[0] = 10`，构造药物调味且库存 2 的场景，断言进入二级页后 `make_count == 2`；记忆值为 `0` / `-1` / `"3"` 时回落为 1
- [ ] `clear_filter_and_sort()` 后筛选排序全部回默认，而 `makefood_cook_mode` / `makefood_make_count` **不变**
- [ ] 旧存档迁移（纯内存，不落盘）：`old = basement.get_base_zero(); del old.__dict__["makefood_cook_mode"]`，调 `save_handle.update_dict_with_default({"rhodes_island": old}, {"rhodes_island": basement.get_base_zero()})`，断言 `update_count >= 1` 且字段被补为默认 dict；已有值时不被覆盖
- [ ] 绘制冒烟：桩掉 `flow_handle.askfor_all`（第一次调用时手动触发 `change_cook_mode(1)` 并返回 `_("精细模式")`，第二次返回 `_("返回")`），跑 `panel.draw()`，断言不抛异常、桩被调用 2 次、cache 为 1、`cache.now_panel_id == constant.Panel.IN_SCENE`。若 `PageHandlePanel` 在无头下需要过多 fixture，**不要深挖**，降级为只跑上面的函数级断言，冒烟交由 6.2 手工完成

### 6.2 游戏内整体测试（由用户执行）

- [ ] 做饭面板选「精细模式」→ 返回 → 再开做饭面板，仍是精细模式
- [ ] 此时打开「泡咖啡加料」与「调酒」面板，仍是标准模式（三入口独立）；在调酒里选精细后回做饭面板，做饭仍是精细
- [ ] 做 3 份某道菜 → 再次进入同一道菜的确认页，默认份数为 3；换一道菜也是 3
- [ ] 选药物调味且库存少于记忆份数时，份数自动降到库存数且不报错
- [ ] 存档 → 退出游戏 → 重进读档，模式与份数仍被记住
- [ ] **改动前的旧存档**读档无报错，模式为标准、份数为 1
- [ ] Tk 与 Web 两种绘制模式均正常

## 7. 风险与回滚

| 风险 | 说明 | 对策 |
| --- | --- | --- |
| 漏改元组打包点导致 `IndexError` | `:288/:297/:338/:345` 四处必须同步扩为 5 元 | §6.1 的元组打包断言 + 绘制冒烟必然暴露；四处已在 §4.3 逐一列出 |
| dict 子键缺失 `KeyError` | 将来新增第 4 种 `make_food_type` 时老存档字典缺键 | 全部读取走 `.get(键, 默认)`，已写进 §4.2b / §4.4a |
| 脏 int 值（`2`/`-1`）不被存档迁移修掉 | `save_handle.py:613` 显式排除 int | `__init__` 值域钳制 + §6.1 断言 |
| 精细模式变粘导致玩家"意外进入答题" | 这正是需求本身；模式在面板上始终高亮可见 | 不加额外提示文本（会引入新 msgid 与翻译轮次） |
| 记忆份数被钳低后写回 | 见 §3.4 已知限制 | 可接受，不处理 |
| 旧存档缺字段崩溃 | 无此风险 | §2.3 第 3 条已逐行确认迁移路径覆盖 `Rhodes_Island` 新增字段 |

**回滚**：改动是纯追加式的两文件小改，`git revert` 该提交即可。回滚后**已写过新字段的存档不会出问题**——`update_dict_with_default` 只补缺失 key、从不删多余 key，残留字段成为无人读取的孤儿属性，pickle 正常存取。无需数据清理脚本，无需重跑 `buildconfig`。

## 8. 改动文件清单

| 文件 | 类型 | 改动 |
| --- | --- | --- |
| `Script/Core/game_type.py` | 修改 | `Rhodes_Island` 新增 `makefood_cook_mode` / `makefood_make_count` 两个 `Dict[int,int]` 字段 |
| `Script/System/Cooking_System/make_food_panel.py` | 修改 | `Make_food_Panel`：删实例字段 `cook_mode`、加值域校验与 property；元组扩 5 元；`make_food_for_sure` 恢复与写回制作数量 |
| `.github/prompts/数据处理工作流/食物系统.md` | 修改 | 缓存字段表加一行 + 流程描述补两句 |
| `update.log` | 修改 | 追加一条「调整」类条目 |

**未改动**：`Script/Core/save_handle.py`（仅需确认兼容性）、`Script/System/Cooking_System/cooking.py`、`cook_question_panel.py`、`Script/UI/Flow/normal_flow.py`、`Script/UI/Panel/food_shop_panel.py`（同名不同类）、任何 CSV / PO / 常量文件。

## 9. 不在本 Plan 范围

- **不记忆调味选择**（精液/药物）：规划阶段已确认排除。若日后要做，需额外处理"读档后药物库存为 0 / 不再拥有该道具"时回落到「正常」的有效性校验（`make_food_panel.py:195-197` 会直接不绘制该按钮）。
- **不记忆食物大类页签**（主食/零食/饮品/酒类）：规划阶段已确认排除。
- **不修主面板品质预测偏乐观的既有问题**：`:264-272` 的主面板预测没有 `cooking.has_cook_question_library()` 门槛，而 `:739-740` 与 `:856-859` 有；对无题库菜谱（如菜谱 999 加料咖啡）会显示一个兑现不了的 `~绝珍` 区间。这是改动前就存在的不一致，只是模式变粘后更易被撞见（主面板选菜谱前拿不到 `food_cid`，无法就地收紧）。建议另开议题。
- **不改 `[重置]` 按钮的语义与文案**（见 §3.5）。

## 10. 执行记录

### 10.1 实际改动（2026-09-06）

| 文件 | 落点 | 内容 |
| --- | --- | --- |
| `Script/Core/game_type.py` | `:1305-1308` | `Rhodes_Island` 新增 `makefood_cook_mode` / `makefood_make_count` 两个 `Dict[int, int]`，紧接 `makefood_sort_order` |
| `Script/System/Cooking_System/make_food_panel.py` | `:54-61` | `__init__` 里删掉 `self.cook_mode = 0`，改为两个字段的 `isinstance` 兜底 + 烹饪模式值域钳制 |
| 同上 | `:63-79` | 新增 `cook_mode` 的 `@property` / `@setter`，读写 `cache.rhodes_island.makefood_cook_mode[make_food_type]` |
| 同上 | `:312 / :321 / :362 / :369` | 四处元组打包扩为 5 元，追加 `self.make_food_type` |
| 同上 | `:670 / :681-682` | `SeeFoodListByFoodNameDraw` 形参注解改 5 元；新增 `self.make_food_type = text[4]`（位于占位项 return 之前） |
| 同上 | `:773-777` | `make_food_for_sure()` 用记忆值替代 `make_count = 1`，含非 int / 小于 1 的回落与 `max_count` 钳制 |
| 同上 | `:861-862` | `[确认制作]` 分支写回 `makefood_make_count[make_food_type]` |
| `.github/prompts/数据处理工作流/食物系统.md` | `:126 / :136 / :139` | 缓存字段表加一行；制作流程第 1 条与「批量数量」条各补一句 |
| `update.log` | `:108` | 「调整」段末尾追加一条 |

### 10.2 与计划的偏差

1. §4.2a 中 `makefood_make_count` 的 `isinstance` 兜底原写在括号补充里（"实施时按此办"），实际已随校验块一并落地，两个字段各两行。
2. 计划未提的顺带改动：`:311 / :361` 两处注释由「将调味、烹饪模式增加进去」改为「将调味、烹饪模式、做饭类型增加进去」，以与新的 5 元元组一致。
3. 其余各步与计划一致；`buildconfig` / `buildpo` / `buildmo` 按 §5 判断确认无需执行（无 CSV、无新增 `_()` 文本）。

### 10.3 测试结果

`§6.1` 全部落地为无头脚本（scratchpad，不入库），**55 项断言全部通过，0 失败**：

| 分组 | 项数 | 覆盖 |
| --- | --- | --- |
| A 字段与默认值 | 5 | `Rhodes_Island()` 与 `get_base_zero()` 的默认 dict |
| B 记忆生效 | 5 | 跨面板实例沿用、读写双向穿透、无实例镜像 |
| C 三入口独立 | 4 | 做饭 / 泡咖啡 / 调酒互不干扰 |
| D 值域校验 | 11 | `2 / -1 / "1" / None / 99` 钳回 0；合法值不动；非 dict 重建；子键缺失回落 |
| E 下游传递 | 7 | 四处元组打包的第 4/5 项、子对象解包（含占位空项） |
| F 制作数量 | 12 | 沿用、写回、药物库存钳制、非法值回落、子键缺失、入口独立 |
| G `[重置]` 行为 | 3 | 清筛选排序但不动两项记忆 |
| H 旧存档迁移 | 4 | 删字段后 `update_dict_with_default` 补回默认；已有值不被覆盖 |
| I 主面板绘制冒烟 | 4 | 桩输入跑通 `draw()` 两轮重绘、模式落库、退出回场景 |

I 组冒烟**未降级**，完整跑通了 `draw()` 的全部八个 `cook_mode` 读取点。

### 10.4 尚未覆盖的验证

`§6.2` 的游戏内清单留给用户执行，重点：真实读档后的记忆保持、改动前的旧存档载入、Tk 与 Web 双绘制模式。验收通过后本计划可移入 `plan/done/`。
