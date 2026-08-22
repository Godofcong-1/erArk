# Plan 10（方案）：性行为履历完整记录（FIRST_RECORD 重构 + 履历面板）

> 本 Plan 拆分为两个文件：**本文件为纯方案**（需求、现状调查、设计决策、数据结构、面板信息架构、风险、范围外）；具体的逐文件改动步骤、构建、验证清单、回滚与实施过程记录见 `plan_10_性行为履历完整记录_实施步骤与记录.md`（下文简称"实施文档"）。

- 状态：**已实施并归档（含第二~九轮追加调整），单元测试全绿（127/127），遗留游戏内人工验证项见实施文档 §6.4**（2026-08-22 实施；实际改动、假设复核与测试结果见实施文档 §6。第二轮（追加需求 10/11：子系统目录独立 + 体液数据迁入履历面板）设计见 §8.1/§8.2、实施记录见实施文档 §6.5；第三轮（追加需求 12：六项展示层调整）设计见 §8.3、实施记录见实施文档 §6.6；第四轮（追加需求 13：收尾四项）设计见 §8.4、实施记录见实施文档 §6.7。首轮实施与方案的 4 处实现细节级偏离与 1 项已知显示层限制记录于实施文档 §6.1）
- 来源：用户需求 → "性行为履历完整记录，包括各部位被破处时间地点、各部位第一次被射精、各部位第一次强绝顶和第一次超强绝顶、获得各级陷落素质的时间。单独创建一个面板来进行该记录，相关记录的数据放在角色的 class FIRST_RECORD"
- 追加需求（规划阶段确认）：
  1. 多周目：之前周目的记录**单独做一个数据存储**，每个周目单独计算，玩家可在面板中**同时查看**当前周目与之前周目的记录
  2. 类似口交，记录第一次深喉/足交/手交/发交等**各个部位交的第一次**；面板对不同类型的记录**分组**处理，每组可单独**展开/收起**
  3. 旧的各部位处女数据（时间/地点/姿势/道具）**合并归入 `first_part_sex_dict`**，处理好存档跨版本迁移与引用点更新；**玩家自己的童贞破处继续使用 `first_sex_*` 平铺字段不变，仅迁移 NPC 的数据**
  4. 肉体信息界面中已有的各部位初次信息显示，**统一合并到履历面板中显示**——肉体情况页不再显示初吻/破处的详情句，只保留"保有/已失去"状态
  5. 记录**每个多重绝顶等级第一次达成**时的时间、地点和参与部位（游戏有多部位同时绝顶机制）
  6. 留一个**自定义特殊履历字典**，由单独的 CSV 数据文件控制（cid + 履历名称 str + 记录的特殊数据 str），用于以后随时扩充特殊履历；每个特殊履历有单独的触发记录条件，并记录时间和地点
  7. 探索成果纳入（用户确认 A/B 级全收，§2.11）：**刻印获得履历**（7 种刻印 × 各等级，独立 dict）；以及**第一次受精、第一次分娩、第一次群交、第一次露出H、第一次隐奸H、第一次喷乳绝顶、第一次放尿绝顶、初潮、第一次装睡H**
  8. **各 H 模式的第一次触发从特殊履历拆出，独立成一个数据 dict 与一个面板分组**；其中"第一次无意识H"进一步**按全部无意识类型拆分**（睡眠/醉酒/时停/平然/空气/体控/心控各记一条）
  9. 特殊履历追加 3 条：**第一次获得精液膨腹素质、第一次饮精绝顶、获得精爱味觉素质**（配表共 8 条）
  10. （第二轮，首轮实施完成后追加）履历系统代码**集中到 `Script/System` 下的独立子系统目录**，不再零散分布（设计见 §8.1）
  11. （第二轮）肉体情况页的**体液数据一并迁移到履历面板**：喝过的精液量、各身体部位被淋/射入的累计精液量、收集的乳汁量、收集的圣水量、肠胃吸收的精液量等（设计见 §8.2）
  12. （第三轮，第二轮实施完成后追加）六项展示层调整（设计见 §8.3）：①履历分页移到肉体情况之后、角色设定之前；②未记录的履历条目直接不显示（废除"未体验/未获得"等占位行）；③「部位交/破处初体验」改名「部位初体验」并把初吻并入该组；④默认只展开「部位初体验」组；⑤喝过的精液量并入口腔行、食道直入胃量并入胃部行（代替两部位的累计被射精量显示）；⑥肠胃吸收量以逗号并入胃部行
  13. （第四轮）收尾四项（见 §8.4）：①肉体情况页状态行去掉"（详见[性行为履历]）"后缀；②履历面板组与组之间空一行；③两份 Plan 文档归档至 plan/done；④在 .github/prompts/数据处理工作流 新增《性行为履历系统》文档
  14. （第五轮）文档去重：子系统目录内的《性行为履历系统设计文档.md》与工作流文档、本 plan 文档内容重叠，降级为纯索引（只保留指向两处文档的链接）；工作流文档成为系统当前状态的唯一详细说明文档（实施记录见实施文档 §6.8）
  15. （第六轮）体液数据组的其余部位行参考口腔/胃部行改为完整文本叙述：腔内部位（小穴/子宫/后穴/尿道）用"总共被射入过Xml精液"、体表部位用"总共被淋上过Xml精液"，不再显示裸数字（实施记录见实施文档 §6.9）
  16. （第七轮）特殊履历附记数据调整：饮精绝顶（cid 7）与精爱味觉素质（cid 8）的附记改为精液来源——H 中的精液记当时的 H 模式（正常H/各特殊H/非H），精液食物记食物名称（原 cid 7 的口腔/胃部位置附记废除）；喷乳绝顶（cid 3）与放尿绝顶（cid 4）附记当时的 H 模式（本条修订 §4 配表表格中 cid 3/4/7/8 的"记录的特殊数据"列；实施记录见实施文档 §6.10）
  17. （第八轮，用户扩写后重构）H 模式文本判定函数 `get_current_h_mode_text` 由用户完善为基于前提系统的全模式判定（补充 乱伦H/爱情旅馆H/浴室H/逆推H/监禁H），并移入 `Script/System/Sex_System/h_mode_common.py` 作为通用函数；履历系统所有取 H 模式文本处改为调用该函数（实施记录见实施文档 §6.11）
  18. （第九轮）面板改为**单周目显示**：不再同屏展示所有周目（废除追加需求 2 与 §5 的同屏设计），每次只显示一个周目、默认当前周目；存在历史周目时提供周目切换按钮行；折叠默认值统一为"所查看周目的部位初体验组展开"（实施记录见实施文档 §6.12）
- 已确认的设计决策：射精口径为"任何精液进入部位都算"（含流动/食物/避孕套灌入）；面板入口为[角色属性]查看面板的第 5 个分页；补上口交初体验的写入挂钩（原 `first_m_sex_time` 无任何写入点）
- 预计改动量：21 个文件（3 新建 + 18 修改），含 1 个新增 CSV（明细见实施文档 §1；实施时修订：原"20 个文件（3 新建 + 17 修改）"为笔误，漏计 1 个修改文件）
- 风险等级：**中**（删除 15 个存档字段并做跨版本迁移；引用面已穷举，见 §2.1 与 §6）
- 适用代码快照：`master @ 88caead6a`
- 前置调研笔记：`plan/wait/10_tem.md`（存档兼容机制、绝顶/射精/破处/素质获得触发点、game_time/position 类型，本 Plan 全部复核过并在下文引用）

---

## 1. 目标

1. 在 `FIRST_RECORD`（`Script/Core/game_type.py:505`）中完整记录角色（NPC 为主）的性行为履历：
   - **部位交/破处初体验**：口交、深喉、手交、足交、发交、乳交、腋交、腿交、尾交、兽角蹭、兽耳蹭、脸交，以及 V/A/U/W 四类插入（承接原处女数据的对象/时间/地点/姿势/道具）
   - **各身体部位第一次被射精**（时间/地点）
   - **各快感部位第一次强绝顶、第一次超强绝顶**（时间/地点）
   - **各等级多重绝顶第一次达成**（时间/地点/参与部位）
   - **获得各级陷落素质的时间**（爱情系 201-204、隶属系 211-214）
   - **各刻印首次达到各等级的时间**（快乐/屈服/苦痛/时姦/恐怖/反发 1-3 级、无觉 1-6 级）
   - **各 H 模式初体验**（独立分组：无意识 H 按 7 种类型各记一条——睡眠/醉酒/时停/平然/空气/体控/心控，另有群交/露出H/隐奸H/装睡H，共 11 项）
   - **特殊履历**（CSV 驱动、可随时扩充；初始 8 条：第一次受精、第一次分娩、第一次喷乳绝顶、第一次放尿绝顶、初潮、第一次获得精液膨腹素质、第一次饮精绝顶、获得精爱味觉素质）
2. 多周目支持：换周目时把旧周目的完整记录归档进**单独的存储** `character_data.first_record_history`，面板同屏展示「当前周目块 + 各历史周目块」。
3. 新建「性行为履历」面板，作为[角色属性]查看面板（`SeeCharacterInfoPanel`）的第 5 个分页；记录按 7 组分类，每组可独立展开/收起。
4. 数据结构收敛：废弃 `first_a_sex_*`/`first_u_sex_*`/`first_w_sex_*`/`first_m_sex_time` 共 15 个平铺字段，NPC 的 V/A/U/W/M 记录统一进 `first_part_sex_dict`；做好存档跨版本迁移与全部引用点改写。
5. 展示收敛：肉体情况页中内嵌的初吻/破处详情句移除，履历面板成为初次信息的**唯一展示处**；肉体情况页只保留"保有/已失去"状态行，感度描述与 first_record 解耦。

## 2. 现状调查

### 2.1 FIRST_RECORD 现状与引用全量清单

`Script/Core/game_type.py:505-562`。现有字段：`first_meet`/`day_first_meet`（逻辑标志）、`first_hand_in_hand`（写入点整段被注释，恒 -1）、`first_kiss_id/body_part/time/place`、`first_sex_id/time/place/posture/item`、`first_a_sex_*`(5)、`first_u_sex_*`(5)、`first_w_sex_*`(4)、`first_m_sex_time`。

`first_sex_|first_a_sex_|first_u_sex_|first_w_sex_|first_m_sex_` 全库引用已穷举（grep 全 Script）：

| 类别 | 位置 |
| --- | --- |
| 写入（破处 handler） | `Script/Settle/default.py:1038-1041`（**玩家童贞**，V 破处时）、`:1053-1056`+`:1092`（NPC V+道具）、`:1127-1130`（**玩家童贞**，A 破处时）、`:1142-1147`（NPC A+道具）、`:1193-1196`（**玩家童贞**，U 破处时）、`:1199-1202`（NPC U）、`:1235-1238`（**玩家童贞**，W 破处时）、`:1241-1244`（NPC W） |
| 读取（前提） | `Script/Design/handle_premise/handle_premise_first.py:69/:98/:127/:156/:185`（五个 in_today；before_today 系列 :83/:112/:141/:170 与 target 系列 :223-363 均复用这五个函数） |
| 读取（UI） | `Script/UI/Panel/body_info_panel.py:175-185`（V）/`:204-214`（A）/`:233-243`（W）/`:289-299`（U）；`Script/UI/Panel/physical_check_and_manage.py:979-989`（处女）/`:995-1005`（A处女） |
| 间接读取（只调前提，不碰字段） | `character_info_head.py:310-325`、`dirty_panel.py:168`、`Web_Draw_System/status_panel.py:792`、`pregnancy.py:167` |
| id 迁移 | `Script/Core/old_chara_to_new.py:283-302`、`:759-769`、`:865-875`（hasattr 守卫的平铺字段重映射） |

关键既有事实：
- **玩家自己的童贞破处也复用 `first_sex_*`**——V/A/U/W 四个破处 handler 都会给玩家写 `first_sex_*`，语义是"玩家初次性交"而非某个部位。按追加需求 3 的澄清，**玩家侧保持不变**。
- `first_m_sex_time` **只有前提读取、无任何写入点**（恒为未发生）。
- `first_sex_item`/`first_a_sex_item`/`first_u_sex_item` 从未被任何 UI 展示过；`first_u_sex_item` 甚至无写入点。
- 前提 `handle_first_sex_in_today` 是两用的：玩家=今天失去童贞（character_info_head.py:312 "P破处"）、NPC=今天失去 V 处女（:315 "V破处"）。
- data/ 下的口上/事件只引用前提 id（如 `first_sex_in_today`），不直接引用字段名——前提函数改写后口上层零影响。
- **肉体情况页的初次信息显示形态**（`body_info_panel.CharacterBodyText`，按追加需求 4 将移除）：初吻/破处详情句**内嵌在各部位块中**——【口】:93-106 初吻详情（含 `first_kiss_body_part==1` 阴茎初吻）、【膣】:170-185、【肛】:199-215、【宫】:227-243、【尿】:283-299。且四个处女块的**感度描述文案与 first_record 耦合**：`保有处女 → 感度0 文案`、`elif first_x_sex_id != -1 → get_ability_lv_ui_text(真实感度)`，两者都不满足（非处模板角色无破处记录）时感度行为空串——这是移除详情句时必须一并解耦的点（也是顺手修复的既有小毛病）。
- 体检报告 `physical_check_and_manage.check_physcial_report`（:955-1005）也有一段"性爱履历"文本，属打印报告性质，**不在本次合并范围**（仅随字段迁移换数据源，实施文档 §2.10）。

### 2.2 精液进入部位的统一入口

`Script/UI/Panel/ejaculation_panel.py:212 update_semen_dirty(character_id, part_cid, part_type, semen_count, update_shoot_position_flag=True)`，part_type==0 为身体。统一累加逻辑在 `:253-262`。全部调用方：
- 真正射精：`ejaculation_panel.py:427`（ejaculation_flow，flag=True，唯一默认 True 的调用）
- 间接进入（全部 flag=False）：`Script/Settle/default.py:7747`（精液食物入口腔）、`Script/Settle/realtime_settle.py:247/:255`（精液流动，**:255 传负数扣减源部位**）、`Script/System/Item_System/condom_handle.py:253/:255/:285`（避孕套灌入）
- `check_locker_panel.py:509` 是衣柜衣物（part_type != 0），不涉身体。

污浊结构 `dirty.body_semen[部位id] = [部位名, 当前量, 当前等级, **累计总量**]`（game_type.py:263-266），累计总量只增不减，可作"该部位是否曾被射精"的历史判据。身体部位表 `data/csv/BodyPart.csv`：19 个部位（0头发…18背部）。

### 2.3 绝顶结算与二段行为

- 所有部位绝顶最终都调 `second_behavior.character_get_second_behavior(character_id, f"{部位}_orgasm_{程度}")`：正常结算 `Script/Settle/orgasm_settle.py:285-286`、解放超强 `:297-298`，以及寸止解放/时停解放路径、玩家射精绝顶（p_orgasm_*）。
- 解析工具已存在：`orgasm_settle.py:19 get_orgasm_part_and_degree(second_behavior_id) -> (部位str, 程度int)`，非部位绝顶 id 返回 `(None, -1)`；程度映射 `orgasm_degree_order`（:15）0小/1普/2强/3超强。
- 部位字母映射 `part_dict = {0:"s",1:"b",2:"c",3:"p",4:"v",5:"a",6:"u",7:"w",21:"m",22:"f",23:"h"}` 目前是 `orgasm_settle_in_second_behavior` 的**局部变量**（:161），无反向映射。
- `second_behavior.py:25 _get_orgasm_settle()` 已有懒加载防循环导入，`character_get_second_behavior`（:31）内可直接用。
- 强绝顶需部位敏感度≥3（:277-283），超强需≥6（:288-296），超强仅由解放分支产生。
- **多重绝顶**：`orgasm_settle.py:317-321`——`part_count >= 2` 时生成二段行为 `f"plural_orgasm_{part_count}"`，是**全库唯一生成点**（grep 确认 f-string 仅此一处；常量定义 PLURAL_ORGASM_2~11，等级上限 11）。参与部位集合 `tem_orgasm_set`（快感状态 id 的 set，与强/超强的键空间一致）就在生成点现场，随后才存入 `h_state.plural_orgasm_set`（:321，game_type.py:467），并在二段效果处理后被清空（`Second_effect.py:2378`）——因此**中心挂钩（character_get_second_behavior）拿不到本次的部位集合**（届时 plural_orgasm_set 还是旧值），必须挂生成点。

### 2.4 陷落素质赋值点

- 通用赋值点：`Script/Design/handle_talent.py:57 character_data.talent[talent_id] = 1`（gain_talent 内，唯一通用点）。
- 绕过点（grep 全 Script 确认 `talent[20x/21x] = 1` 仅此两处）：`Script/System/Instruct_System/handle_instruct.py:1112`（告白：202→0、**203=1**、205=1）、`:1144`（戴上项圈：212→0、**213=1**、215=1）。
- 陷落素质集合：`handle_talent.py:185 [201,202,203,204,211,212,213,214]`（have_fall_talent）。205 戒指/215 项圈是 type 4 信物、催眠系素质（handle_talent.py:190）均不属陷落。

### 2.5 部位交与 insert_position 体系

- `h_state.insert_position`（game_type.py:441-442）：-1 未插入，**0 开始同身体部位编号**（BodyPart.csv），20 开始同服装部位。
- 身体侧共 16 个结算效果 handler（`Script/Core/constant_effect.py:607-637`，效果 id 802-817；801 是 RESET）：802发(0)/803脸(1)/804口(2)/805乳(3)/806腋(4)/807手(5)/808V(6)/809子宫(7)/810A(8)/811U(9)/812腿(10)/813足(11)/814尾(12)/815角(13)/816耳(14)/817深喉(15胃部)。handler 实现集中在 `Script/Settle/default.py`（如 handle_penis_in_t_mouse/:9801、handle_penis_in_t_deep_throat/:10086），每个只做 `target_data.h_state.insert_position = N`。
- `data/csv/Behavior_Effect.csv` 中 420-437 各部位交指令均携带对应效果（如 421 blowjob→804、430 deep_throat→817、423 footjob→813、424 hairjob→802），**每次行为结算必经**。
- **`penis_in_body_N` 二段行为不可用作记录挂钩**：`second_behavior.py:303-305` 在插入位置刚改变的第一次结算被 `insert_position_change_save` 跳过（玩家每条指令都换部位则永不触发），且群交模式（:301）不触发。
- 不携带 802-817 效果的口交来源：早安咬/晚安咬（253/256，效果 520）、测试口腔吮吸（853）、AI 文本（handle_chat_ai.py:958），它们都会结算**口交经验（Experience.csv:44，id 42）**，统一入口 `Script/Settle/common_default.py:888 base_chara_experience_common_settle()`。

### 2.6 多周目机制

`Script/UI/Panel/new_round.py`，流程 `:612-616`：`inherit_player_data()`(:647) → `inherit_npc_data()`(:731) → `reset_game_data()`(:796)。
- `inherit_player_data`：`:658 old_pl_character_data = copy.deepcopy(...)` → `:660` 新建玩家 → 选择性继承（能力/经验/源石技艺/上限/收藏）。
- `inherit_npc_data`：`:741 old_npc_data = copy.deepcopy(cache.character_data)` → 遍历 `cache.npc_tem_data`，**所有 NPC 均被 `character_handle.init_character` 重建**（:748 未陷落分支 / :750 陷落分支），陷落者再继承好感/信任/能力/经验/催眠度。
- `reset_game_data`：`:811 new_game_round = old_cache.game_round + 1`——**周目数在最后才 +1**，inherit 阶段 `cache.game_round` 仍是旧周目数。
- 结论：角色重建 ⇒ FIRST_RECORD 每周目天然重置、处女素质恢复、陷落素质不继承；**存活的 first_record 天然就是"当前周目"的记录**，历史周目需要在 inherit 阶段显式归档。

### 2.7 面板架构（SeeCharacterInfoPanel）

`Script/UI/Panel/see_character_info_panel.py`：
- 分页是硬编码 dict（:54-69，玩家/NPC 各 4 页），分页按钮条 `panel.CenterDrawButtonListPanel().set(..., column=4, ..., self.change_panel)`（:70-79，**:76 与 :92 两处 column=4**）。
- `draw()`（:97-110）绘制当前分页 + 按钮条；:99-102 有分页不存在时的 fallback（玩家能力/肉体情况互斥的兜底）。
- 外层事件循环 `SeeCharacterInfoHandle.draw()`（:1706-1736）：`while 1` → **每帧重建 `SeeCharacterInfoPanel`**（:1718） → `askfor_all(return_list)` → `elif yrn in draw_data` 切分页（:1735-1736）——分页按钮返回值即分页名字符串，新增分页无需改这里；未识别的返回值直接进入下一帧重绘。
- 参考容器：`See_Character_Detailed_Attributes_Panel`（:154-181，**draw() 不收集 return_list**）与 `SeeCharacterThirdPanel`（:184-215，**:211-215 会收集**）。
- first_record 的成熟显示写法可搬：`body_info_panel.CharacterBodyText`（body_info_panel.py:47-356）。
- 格式化惯例：时间 `game_time.get_date_until_day(t)[3:]`（game_time.py:67，`[3:]` 切掉"时间:"前缀是全库惯例，physical_check_and_manage.py:985/:1001 漏切属既有小毛病）；地点 `attr_text.get_scene_path_text(place)`（attr_text.py:85，**默认值 `["0"]` 会 KeyError，必须先判已发生**）；素质名 `game_config.config_talent[id].name`；部位名 `game_config.config_body_part[id].name`；快感部位名 `game_config.config_character_state[id].name`。
- ui_text CSV 无需加条目：面板文字走 gettext `_()`，中文原文即 msgid，zh_CN 直接 fallback。

### 2.8 存档兼容机制（复核 10_tem.md §1）

- 角色对象字段兼容走 `save_handle.py:301-303`：新建 `game_type.Character()` + `recursive_update()`（:469-483，遍历**旧存档**属性逐个 setattr，嵌套对象递归、**dict 整体复制不深入**）。新增字段自动获得默认值；但**旧档的孤儿属性会被原样带进新对象**。
- 显式迁移钩子：`save_handle.py:150-201 _normalize_loaded_save_paths()`（在 load_save :204-217 中、角色重建之前运行），先例为 :185-191 的避孕套 backfill。
- pickle 反序列化只还原 `__dict__` 不跑 `__init__` ⇒ 旧档 FIRST_RECORD 实例必然带平铺字段、缺新 dict，可作旧档判据。
- 存 cid 的新字段必须在 `old_chara_to_new.py` 三处 first_record 段补映射（§2.1 表）。

### 2.9 无意识H机制

- 模式标记：`sp_flag.unconscious_h: int`（game_type.py:746-747），`[0否,1睡眠,2醉酒,3时停,4平然,5空气,6体控,7心控]`。
- 赋值点 **20+ 处**（grep 确认）：default.py:5402-5558 的一组"进入各无意识模式"handler（8 个）、时停 :1921/:7562/:7600、体控 :1751/:1811、催眠面板 hypnosis_panel.py:146/:845、睡奸 handle_instruct.py:1268、NPC 睡眠 handle_npc_ai_in_h.py:258 等——**不宜逐点挂钩**。
- 模式名已有现成映射：`hypnosis_panel.unconscious_list[unconscious_h]`（settle_behavior.py:268 在结算输出中就是这么用的，settle_behavior 已 import hypnosis_panel）。
- 中心判定点：`settle_behavior.handle_settle_behavior()`（:20 入口）是玩家↔NPC 全部行为结算的必经处，其交互对象结算段能同时拿到 target_data 与 unconscious_h（:259 即读取处）。

### 2.10 新增 CSV 的接入机制（复核《CSV数据加载机制说明.md》）

- CSV 5 行头格式：字段名 / 中文说明 / 类型 / 国际化标记(0/1) / 类说明文档，第 6 行起为数据。
- `buildconfig.py` **自动**扫描 data/csv/ → data.json + config_def.py 数据类（无需手写类）。
- `Script/Config/game_config.py` 需要**手动**三步：模块级 dict（如 `config_first_record_special: Dict[int, config_def.FirstRecordSpecial] = {}`）、加载函数（照抄 :549 `load_ability_type_data` 的模式：`translate_data` + 逐行 `__dict__` 赋值入 dict）、在 `init()`（:2192-2205 的 load_* 调用链）中注册一行。
- 国际化标记为 1 的字段自动进 PO 文件（buildpo 链路）。

### 2.11 A/B 级探索候选的触发点（追加需求 7/9 的调查依据）

- **刻印**：`data/csv/Ability.csv` type 2 共 7 种——13快乐/14屈服/15苦痛/16时姦/17恐怖/18反发（各 1-3 级）、19无觉（1-6 级）。**所有升级点都伴随 `{类型}_mark_{等级}` 二段行为**：中心刻印结算 `second_behavior.py:431-582`（happy/yield/pain/unconscious/terror/hate 逐级 `character_get_second_behavior`），连监禁调教的直接赋值也规范发行为（confinement_and_training.py:209-224 的 yield/terror/hate_mark），**零旁路**。行为 id 全集见 `constant/SecondBehavior.py:56-108`（HAPPY_MARK_1 ~ UNCONSCIOUS_MARK_6）。
- **受精**：唯一写入点 `pregnancy.py:137-146`——talent[20]=1、`fertilization_time = cache.game_time`(:138)、无意识妊娠判定（talent[35]，:140-143）之后触发二段行为 `"fertilization"`(:146)——**中心挂钩可顺带解析，且届时 talent[35] 已就绪可作特殊数据**。
- **分娩**：唯一点 `character_handle.py:165-198`（生成孩子角色，:192-193 挂上母女关系），**无二段行为**，需专点挂钩；现场有孩子名（child_name）可作特殊数据。
- **群交/露出/隐奸/装睡**：标记分别为 `cache.group_sex_mode`（全局）、`sp_flag.exhibitionism_sex_mode`（game_type.py:752，1无人室内/2无人室外/3人前/4无意识人前）、`sp_flag.hidden_sex_mode`（:748，1双不隐/2女隐/3男隐/4双隐）、`h_state.pretend_sleep`（:495）。与无意识H同构，全部可挂中心结算判定（实施文档 §2.8(4)）。旁证：成就结构体（game_type.py:923-931）为群交/隐奸/露出/睡奸/醉奸各建了专门记录，游戏本身视其为重要类别。露出/隐奸**无现成的简洁模式名列表**（exhibitionism_sex_panel.py:85-88 是带说明的按钮文案），需自写 `_()` 映射。
- **喷乳/放尿绝顶**：固定二段行为 `b_orgasm_to_milk` / `u_orgasm_to_pee`（orgasm_settle.py:300-306 唯一生成点），中心挂钩匹配字符串即可。
- **初潮**：`handle_talent.py:289-302 npc_lost_no_menarche_talent`，talent[6] 置 0 的唯一点（子宫开发 ability[7]+ability[12] ≥ 4 触发）。
- **精液膨腹素质（talent 32，追加需求 9）**：唯一获得点 `handle_talent.py:243-245 npc_gain_and_lost_cumflation`——腹部精液总量（部位 6/7/8/15 当前量之和，:233-239 现场变量 `abdomen_all_semen`）≥ 6000ml 时获得；**可得可失**（:246-248 低于阈值即失去），"第一次获得"由 dict 去重天然保证。无二段行为。
- **精爱味觉素质（talent 31，追加需求 9）**：唯一获得点 `handle_talent.py:263-264 npc_gain_semen_drinking_climax_talent`（饮精绝顶经验 111 累计 ≥ 50）。无二段行为。
- **饮精绝顶事件（追加需求 9）**：每次发生的统一标志是**饮精绝顶经验（Experience.csv id 111）的结算**（orgasm_settle 高潮结算尾部，含口内射精绝顶、进食精液食物绝顶、素质 31 条件反射绝顶各路径）——与口交经验(42)同理，挂 `base_chara_experience_common_settle` 一处全覆盖；触发时 `h_state.shoot_position_body`（2口腔/15胃部）尚未重置，可作附记数据。
- C 级候选（第一次被舔 6205/6209/6210、各部位第一次普通绝顶）**经用户确认不纳入**。

## 3. 设计决策

### 3.1 数据结构：稀疏 dict + 玩家童贞平铺保留

`first_part_sex_dict` 的键直接采用 `insert_position` 的身体部位编号（§2.5），一套编号同时覆盖"部位交初体验"与"NPC 破处数据"两个语义——V/A/U/W 破处本质就是对应部位的初次插入。含 6-9 插入类还有一个独立收益：**处女素质模板为 0 的非处干员没有破处记录，此 dict 是她们初次插入的唯一记录**。

值采用带键名的 dict（而非位置列表），因为要兼容承接原处女数据的全部字段（id/time/place/posture/item），且各部位可选字段不同；其余新 dict 语义单一，沿用 `[时间, 地点]`（或加附加数据位）的定长列表即可。

玩家童贞保留 `first_sex_*` 平铺（用户澄清）：玩家的"初次性交"不属于任何自身部位，硬塞进 dict 需要特殊键，得不偿失；保留后前提 `handle_first_sex_in_today` 只需加玩家分支。

### 3.2 挂钩选点（每组的"为什么选这里"）

| 记录 | 挂钩点 | 弃选方案及原因 |
| --- | --- | --- |
| 部位交初体验 | 16 个 `PENIS_IN_T_*` 结算效果 handler（每次部位交结算必经）+ 口交经验补充挂钩 | `penis_in_body_N` 二段行为：首次结算被跳过、群交不触发（§2.5）；逐经验挂钩：腿/尾/角/耳等无专属经验 id |
| 口交补充 | `base_chara_experience_common_settle` 的 exp 42 分支 | 判定条件**只用"dict 无键 2"，不用 `exp42==0`**——多周目下经验按比例继承（new_round.py:775-776），exp42 非 0 不代表本周目发生过口交 |
| 第一次被射精 | `update_semen_dirty` 统一累加处 | 挂 ejaculation_flow 会漏精液流动/食物/避孕套（已确认口径：任何精液进入都算）；判据 `累计总量==0` 保证旧档已被射过的部位不误记 |
| 强/超强绝顶 | `character_get_second_behavior` 置 1 分支集中解析 | 挂 orgasm_settle.py:285/:297 两处会漏寸止解放/时停解放/玩家射精绝顶等其它产生 `X_orgasm_strong` 的路径 |
| 陷落素质时间 | `handle_talent.py:57` + 告白/项圈两处直接赋值点 | 已 grep 确认赋值点仅此 3 处 |
| 多重绝顶 | `orgasm_settle.py:317-321` 唯一生成点 | 中心挂钩（character_get_second_behavior）拿不到本次部位集合——`plural_orgasm_set` 在调用**之后**才更新（§2.3） |
| 刻印等级 | 中心挂钩顺带解析 `{类型}_mark_{等级}` 二段行为 | 全部升级点（含监禁调教）都发该行为，零旁路（§2.11）；逐点挂 second_behavior.py:431-582 + 监禁调教是重复劳动 |
| 受精/喷乳/放尿绝顶 | 中心挂钩的"二段行为 id → 特殊履历"白名单映射 | 三者各有唯一的固定二段行为 id（fertilization/b_orgasm_to_milk/u_orgasm_to_pee），无需新挂点 |
| 分娩/初潮 | 各自唯一触发点专点挂钩（character_handle.py:165-198 / handle_talent.py:297） | 无二段行为可解析（§2.11） |
| 膨腹/精爱味觉素质 | 素质获得唯一点专点挂钩（handle_talent.py:244 / :264） | 两者是"特殊素质获得"，不经过 gain_talent 通用赋值点，也无二段行为（§2.11） |
| 饮精绝顶 | `base_chara_experience_common_settle` 的经验 111 分支（与 exp42 同函数） | 经验 111 结算是全部饮精绝顶路径（口内射精/精液食物/条件反射）的统一标志（§2.11） |
| H 模式初体验（独立 dict：无意识×7 类型/群交/露出H/隐奸H/装睡H） | `settle_behavior.handle_settle_behavior()` 中心判定（H 状态 + 对应 flag） | 赋值点分散（无意识 20+ 处，§2.9）逐点挂必漏；前提函数是只读高频调用，不能带副作用。不放特殊履历配表：固定结构化条目（尤其无意识按类型 7 条）用代码键更干净，配表留给真正的临时扩充 |
| 周目归档 | `inherit_player_data`/`inherit_npc_data`（old 数据已 deepcopy、周目数未 +1） | 挂 reset_game_data 时角色已被重建，旧记录只剩 old_cache 深拷贝，取用绕远 |

超强绝顶同时回填空缺的强绝顶记录（超强必然 ≥ 强）。

### 3.3 周目归档：Character 层 `first_record_history`

历史放 Character 层而非 FIRST_RECORD 内部——避免"快照里再嵌历史"的递归嵌套。归档时以 `has_any_record()` 过滤全空记录，避免几百名 NPC × 周目数的空对象膨胀存档。存档为 pickle 对象序列化，dict 内嵌 FIRST_RECORD 实例可直接保存。

### 3.4 面板：第 5 分页 + 7 组折叠

- 入口做成 `SeeCharacterInfoPanel` 第 5 分页（已确认）：复用现成的按角色查看/切人框架，不需要动 constant.Panel、normal_flow、InstructConfig.csv。
- 折叠按钮用 `draw.Button` + `cmd_func`（同 :70-79 分页按钮条的模式）；**折叠状态必须存面板实例之外**——外层循环每帧重建面板（§2.7），采用新模块的模块级 dict（仅会话内有效，不进存档）。
- 只给 NPC 加分页（肉体情况页同为 NPC 专属）；查看玩家时按 :99-102 的既有模式 fallback 回「基础属性」。
- **初次信息展示唯一化**（追加需求 4）：初吻/破处的详情句（对象/时间/地点/姿势）从肉体情况页移除，履历面板成为唯一展示处；肉体情况页各部位块只保留"保有初吻/处女"或"已失去（详见[性行为履历]）"的**状态行**，感度描述与 first_record **解耦**（改为只看处女素质：有素质→感度0文案，无素质→真实感度等级）——顺带修复"非处模板角色感度行为空"的既有小毛病（§2.1）。两页职责划清：肉体情况页=当前状态与数值，履历面板=事件履历。

## 4. 数据结构设计

**FIRST_RECORD（game_type.py:505）**：删除 `first_a_sex_*`(5)、`first_u_sex_*`(5)、`first_w_sex_*`(4)、`first_m_sex_time`(1) 共 15 个字段；`first_sex_*` 五个字段保留，docstring 改为「玩家童贞专用，NPC 的 V 破处记录在 first_part_sex_dict[6]」；追加 9 个 dict：

```python
        self.first_part_sex_dict: dict = {}
        """ 部位交/破处初体验记录（每周目一份）
        键int：同 h_state.insert_position 的身体部位编号，0发交/1脸交/2口交/3乳交/4腋交/5手交/6V性交/7子宫性交/8A性交/9U性交/10腿交/11足交/12尾交/13兽角蹭/14兽耳蹭/15深喉
        值dict：{"id": 对象角色id int(-1无), "time": datetime, "place": List[str], "posture": str(行为中文名,空串无), "item": int(-1无/0手指/1振动棒/2采尿器)} """
        self.first_shoot_body_dict: dict = {}
        """ 各身体部位第一次被射精记录 部位id(同BodyPart.csv 0-18):[时间datetime, 地点List[str]] """
        self.first_strong_orgasm_dict: dict = {}
        """ 各部位第一次强绝顶记录 快感状态id(0皮1胸2阴蒂3阴茎4V5A6U7W21口喉22兽部23心理):[时间, 地点] """
        self.first_super_orgasm_dict: dict = {}
        """ 各部位第一次超强绝顶记录 结构同上 """
        self.first_plural_orgasm_dict: dict = {}
        """ 各等级多重绝顶初次达成记录 同时绝顶部位数int(2~11):[时间, 地点, 参与部位id列表List[int](快感状态id)] """
        self.fall_talent_time_dict: dict = {}
        """ 各级陷落素质获得记录 素质id(201-204/211-214):[时间, 地点] """
        self.first_mark_dict: dict = {}
        """ 各刻印首次达到各等级记录 刻印二段行为id str(如happy_mark_2，见constant/SecondBehavior.py:56-108):[时间, 地点] """
        self.first_h_mode_dict: dict = {}
        """ 各H模式初体验记录 模式键str:[时间, 地点, 附加数据str]
        模式键：unconscious_1~unconscious_7(按sp_flag.unconscious_h类型,1睡眠2醉酒3时停4平然5空气6体控7心控)、
        group_sex(附加数据:当时场景内人数)、exhibitionism(附加数据:露出模式名)、hidden_sex(附加数据:隐奸模式名)、pretend_sleep """
        self.first_special_record_dict: dict = {}
        """ 特殊履历记录 配表cid(FirstRecordSpecial.csv):[时间, 地点, 特殊数据str] """
```

- `first_mark_dict` 的键直接用刻印二段行为 id 字符串（happy/yield/pain/time/terror/hate_mark_1~3、unconscious_mark_1~6）——挂钩处零转换，显示时拆出类型与等级（刻印名用 `game_config.config_ability[13~19].name`）。
- `first_h_mode_dict` 的无意识条目按类型独立成键（追加需求 8）——同一角色可先后积累"第一次睡眠H""第一次时停H"等至多 7 条；露出/隐奸不再拆模式，首次发生时把模式名记进附加数据。
- 增加方法 `has_any_record() -> bool`：`first_kiss_id != -1` 或 `first_sex_id != -1`（玩家童贞）或 9 个新 dict 任一非空。
- 所有地点写入一律 `list(character_data.position)` 拷贝（引用赋值警告见 10_tem.md §6）。

**Character（约 :1624 `first_record` 附近）**：

```python
        self.first_record_history: dict = {}
        """ 之前各周目性行为履历的单独存储 周目数int:该周目结束时的FIRST_RECORD快照 """
```

**特殊履历配表 `data/csv/FirstRecordSpecial.csv`**（初始 8 条，完整表内容与接入步骤见实施文档 §2.8）：

| cid | 履历名称 | 记录的特殊数据 |
| --- | --- | --- |
| 1 | 第一次受精 | 是否为无意识受精 |
| 2 | 第一次分娩 | 孩子的名字 |
| 3 | 第一次喷乳绝顶 | 无 |
| 4 | 第一次放尿绝顶 | 无 |
| 5 | 初潮 | 无 |
| 6 | 第一次获得精液膨腹素质 | 获得时的腹部精液总量 |
| 7 | 第一次饮精绝顶 | 精液所在位置（口腔/胃部） |
| 8 | 获得精爱味觉素质 | 无 |

## 5. 面板信息架构

**显示结构**：先渲染「第 `cache.game_round` 周目（当前）」= 存活 `first_record`，再按周目数升序渲染 `first_record_history` 各快照。每个周目块内 7 组，每组组头一个折叠按钮（当前周目默认全部展开，历史周目块默认全部收起）：

1. **初吻履历**：对象/时间/地点/部位（`first_kiss_*` 平铺字段，`first_kiss_body_part==1` 为阴茎初吻）
2. **部位交/破处初体验**：遍历 dict 键 0-15，交型名用自写映射（0发交/1脸交/2口交/3乳交/4腋交/5手交/6V性交/7子宫性交/8A性交/9U性交/10腿交/11足交/12尾交/13兽角蹭/14兽耳蹭/15深喉，`_()` 包裹）；每条显示对象/时间/地点，`posture` 非空补显姿势、`item != -1` 补显道具（-1无/0手指/1振动棒/2采尿器，此信息现有 UI 从未展示过）；未记录显示「未体验」。本面板是初次信息的**唯一展示处**（追加需求 4）：初吻与 V/A/U/W 破处条目的文案**沿用 body_info_panel 原句式**（"于{时}在{地}，向{人}博士(的阴茎)献上了初吻"、"于{时}在{地}，被{人}博士以{姿势}夺走了(后庭/子宫/尿道)处女"），保证信息与玩家熟悉度不降级；其余部位交条目用统一的简句式
3. **初次被射精**：遍历 `game_config.config_body_part`（19 部位），未记录显示「未记录」；历史周目块只列已记录项，避免刷屏
4. **初次绝顶履历**（强/超强/多重）：强与超强按快感部位列表遍历（NPC 排除 3 阴茎），部位名 `config_character_state[id].name`；**多重绝顶小节**遍历 `first_plural_orgasm_dict` 按等级升序，每条显示「N重绝顶：时间/地点/参与部位（部位名顿号连接）」，未达成的等级不列出；历史周目块同样只列已记录项
5. **陷落与刻印履历**：陷落小节——爱情系 201-204、隶属系 211-214 各 4 行，素质名 + 时间，未获得显示「未获得」；**刻印小节**——遍历 `first_mark_dict` 按刻印类型分行（刻印名 `game_config.config_ability[13~19].name`），每行列出已达成等级及其时间/地点，全未达成的刻印不列出
6. **H 模式初体验**（追加需求 8 独立分组）：固定 11 项——无意识 7 类型（条目名拼「第一次{`hypnosis_panel.unconscious_list[n]`}H」）+ 群交/露出H/隐奸H/装睡H（条目名自写 `_()` 文案）；已记录的显示 时间/地点/附加数据（群交人数、露出/隐奸模式名），未记录显示「未体验」；历史周目块只列已记录项
7. **特殊履历**：遍历 `game_config.config_first_record_special`（按 cid 升序，初始 8 条），履历名取配表 `name`；已记录的显示 时间/地点/特殊数据（特殊数据非空才显示，含义见配表 `data_info`），未记录显示「未达成」——配表加行后面板自动跟随，无需改面板代码

模块结构、折叠状态实现、接入 see_character_info_panel 的 5 处小改见实施文档 §2.13。

**第二轮追加（追加需求 11）**：当前周目块在「初次被射精」之后插入「**体液数据**」组，内容自肉体情况页迁移：全身累计被射精液量、喝过的精液量（口腔+胃部）、肠胃吸收的精液量、各身体部位累计被射精液量（只列非零部位）、收集的乳汁量与圣水量。该组读取的是**实时数据**（`dirty.body_semen`/`dirty.absorbed_total_semen`/玩家 `pl_collection.milk_total/urine_total`）而非 FIRST_RECORD，因此不随周目归档、仅当前周目块显示（见 §8.2）。

**第三轮追加（追加需求 12）对本节的修订**：本节开头的"7 组"分组表已被 §8.3 修订为 **6 个履历组**（初吻履历组撤销、条目并入更名后的「部位初体验」组首行；当前周目块加体液组共 7 组）；各组中"未体验/未获得/未记录/未达成"的占位显示规则全部废除（未记录条目直接不显示，整组无记录时展开显示「无记录」）；折叠默认值改为只展开当前周目的「部位初体验」组；体液组的喝精/直入胃/肠胃吸收三行并入口腔与胃部行。分组明细以 §8.3 与子系统设计文档为准。

## 6. 风险与注意事项

1. **删字段 + 迁移是本 Plan 最大风险面**。引用已按 §2.1 穷举，实施完成的判据：全库 grep `first_a_sex_|first_u_sex_|first_w_sex_|first_m_sex_` **归零**（`first_sex_` 允许保留：玩家童贞与迁移代码）；`body_info_panel.py` 中 `first_record` 引用（含 `first_kiss_*`）**归零**（追加需求 4）；data/ 下口上/事件只引用前提 id，前提函数改写后口上层零影响。
2. 旧存档历史事件无法回溯：部位交初体验、强/超强绝顶"自更新起算"，已有经历者更新后的第一次会被记为初体验；已处于 N>1 周目的旧档没有之前周目的归档，历史块为空。均为已知限制。
3. `update_semen_dirty` 的 `semen_count > 0` 守卫必须保留（realtime_settle.py:255 传负数）。
4. 归档快照是对象引用进 history dict（来自已 deepcopy 的 old 数据），实施后不得再有代码改写历史快照；`has_any_record()` 过滤防存档膨胀。
5. 面板每帧重建（`SeeCharacterInfoHandle` while 1），文本拼装放 `__init__` 符合现有约定，但别做重计算；折叠状态必须放模块级。
6. `attr_text.get_scene_path_text` 对未发生记录的默认地点会 KeyError，显示前必须先判已发生。
7. debug 面板若有直接翻素质 dict 的作弊入口会绕过陷落时间记录（属调试工具，可接受）。
8. `first_sex_*` 保留后是"玩家专用字段存在于所有角色对象"的历史包袱，NPC 侧恒为默认值——docstring 注明即可，不做进一步拆分。

## 7. 不在本方案范围

- 不迁移/不启用 `first_hand_in_hand`（初次牵手，写入点整段被注释，恒 -1）
- 不把体检报告（physical_check_and_manage 的"性爱履历"段）并入履历面板——打印报告性质不同，保留原样、仅随字段迁移换数据源
- 不动 character_info_head.py 的当日破处状态标签（"<V破处>"等，走前提判定，与详情句展示无关）
- 不给玩家展示履历分页（玩家童贞数据保留但不进新面板；后续如需可加）
- 不记录服装部位交（insert_position ≥ 20 的 `PENIS_IN_T_HAT` 等 821-834 效果）
- 不为陷落/部位交等新记录新增前提、口上或成就
- 不把折叠状态持久化进存档
- 不处理"旧存档已发生事件的回溯补记"（无历史数据可依据，见 §6 第 2 条）
- 特殊履历配表初始 8 条，不再预置其他条目；后续每加一条只需配表加行 + 编写该条的触发挂钩。H 模式初体验不走配表（追加需求 8，固定结构化条目用代码键，见 §3.2 决策表）
- 精液膨腹只记"第一次获得"，不记失去与再获得（素质随腹中精液量波动，由 dict 去重只保首次）
- 露出/隐奸不按模式拆分独立键（用户只要求无意识按类型拆分）——首次发生时的模式名记在附加数据里
- C 级探索候选**不纳入**（用户确认，§2.11）：第一次被舔（舔吸乳头/舔阴/舔肛，需 3 个专点挂钩）、各部位第一次普通绝顶（纪念价值低）
- 多重绝顶不做高等级回填低等级，也不记录"历史最高多重等级"之类的衍生统计
- 刻印记录不含刻印**消退/清零**（如 default.py:7283 反发清零）——只记首次达到，不追踪后续变化

## 8. 第二轮追加调整（追加需求 10/11，2026-08-22 首轮实施完成后）

### 8.1 履历系统独立子系统目录（追加需求 10）

按 `Script/System` 的既有惯例（每个子系统一个目录 + 空 `__init__.py` + 自带设计文档），新建 **`Script/System/First_Record_System/`**：

| 文件 | 来源 |
| --- | --- |
| `first_record_handle.py` | 自 `Script/Design/` 迁入（通用写入函数、白名单映射、H 模式中心判定、模式名映射） |
| `first_record_panel.py` | 自 `Script/UI/Panel/` 迁入（履历分页组件与容器、折叠状态、分组文本构建） |
| `__init__.py` | 新建（空文件，同其他子系统） |
| `性行为履历系统设计文档.md` | 新建（系统概览、数据结构、挂钩分布、面板架构、扩充指引） |

迁移原则：**只动模块路径，不动函数签名与逻辑**。数据结构（FIRST_RECORD/first_record_history）仍留在 `game_type.py`（全库数据结构统一定义处，不属于子系统目录的职责）；各挂钩点（default.py/second_behavior.py/settle_behavior.py 等）留在原自然模块，只更新 import 路径——挂钩必须长在触发事件的结算代码处，无法也不应集中。引用方共 6 个文件改 import：second_behavior、settle_behavior、handle_talent、common_default（顶层）、character_handle（函数内延迟导入）、see_character_info_panel。

### 8.2 体液数据迁入履历面板（追加需求 11）

**迁移口径：纯展示层迁移，不改数据存储。** 体液数据本就存于 `dirty.body_semen[部位][3]`（累计量）、`dirty.absorbed_total_semen`、玩家 `pl_collection.milk_total/urine_total`，与 FIRST_RECORD 无关；本轮只是把肉体情况页中分散在【总】【口】【胸】【指】【足】【膣】【肛】【宫】【尿】【其他】十处的体液句子收拢为履历面板的一个「体液数据」分组。

- **面板侧**：当前周目块在「初次被射精」组之后插入「体液数据」组（组头折叠按钮同其他组）。内容沿用肉体页原句式：全身累计、喝过的精液（含食道直入胃的拆分句）、肠胃吸收，另有「各部位累计被射精液量」小节（遍历 BodyPart.csv，只列非零部位——肉体页原本只展示 8 个固定部位，迁移后覆盖全部 19 部位是顺带的增强）、收集乳汁/圣水。
- **仅当前周目块显示**：该组读实时数据，历史周目的体液数据没有归档存储（角色重建时 dirty 天然重置），历史块不出现此组。不为体液做周目归档——那是数据结构扩张，不在本需求范围。
- **肉体情况页**：十处体液句子全部移除（【总】块因只含体液句而整块移除），其余内容（感度/技巧描述、怀孕情况、分娩孩子列表、母亲/喜欢的姿势等）不动。移除后肉体页对 `dirty`/`pl_collection` 的引用归零。
- **折叠状态键**：由「组序号」改为「折叠槽位序号」（当前周目块 8 槽、历史块 7 槽——第三轮后为 7/6 槽，见 §8.3），键仍为 `{周目数}_{槽位}`、仅会话内有效。

### 8.3 第三轮展示层调整（追加需求 12）

六项全部为**纯展示层**改动，只动 `first_record_panel.py` 与 `see_character_info_panel.py` 两个文件，数据结构与挂钩零变化：

1. **分页位置**：`SeeCharacterInfoPanel` 的 NPC 分页 dict 重排为 基础属性 → 能力经验宝珠 → 肉体情况 → **性行为履历** → 角色设定（dict 插入序即按钮序）。
2. **未记录不显示**：7 个（并组后 6 个）履历组构建函数中全部 `is_current` 占位分支（"未体验/未获得/未记录/未达成/尚无记录"）删除，当前周目块与历史块统一为"只列已记录项"；`is_current` 参数从各构建函数与 `build_group_text` 签名中移除。整组无记录时沿用既有兜底（展开显示「无记录」一行）。小节头（强/超强/多重绝顶、陷落素质、刻印）只在对应 dict 非空时输出。体液组的"未接触过/未品尝过精液"占位同步删除（全零时组文本为空 → 兜底「无记录」）。
3. **并组改名**：「初吻履历」组撤销，「部位交/破处初体验」改名「**部位初体验**」，初吻作为该组首个条目（"初吻：于{时}在{地}，向{人}博士(的阴茎)献上了初吻"，句式不变）。履历组从 7 个减为 6 个；体液组插槽相应由 3 前移到 2（仍在「初次被射精」之后）。
4. **默认折叠**：默认只展开**当前周目的「部位初体验」组**（`default_expand = is_current and group_index == 0`），其余组（含体液组与历史块全部组）默认收起。
5. **喝精并入口腔行**：体液组撤销独立的"总共喝过Xml精液（有Yml…）"行；各部位累计小节中口腔行改显示 `口腔：总共喝过{body_semen[2][3]}ml精液`、胃部行改显示 `有{body_semen[15][3]}ml精液在食道直接射进了胃里`——两部位的原始"累计被射精量"数值不变，只换了更贴切的表述（旧合并行的"总喝过量=口+胃"拆回各部位自身数值）。
6. **肠胃吸收并入胃部行**：撤销独立的"肠胃一共吸收了Xml精液"行，以逗号接在胃部行的直入胃量之后（`胃部：有Yml精液在食道直接射进了胃里，肠胃一共吸收了Zml精液`）；只有吸收量无直入量时胃部行单独显示吸收段。

### 8.4 第四轮收尾（追加需求 13）

1. **肉体情况页状态行简化**：五处"已失去X（详见[性行为履历]）"去掉括注后缀，只留"已失去X"——履历分页已紧邻肉体情况页，指引冗余。
2. **组间空行**：履历面板每个分组（按钮+内容）之后追加一个换行，组与组之间以一个空行分隔，提升可读性。
3. **文档归档**：本方案与实施文档自 `plan/wait/` 移至 `plan/done/`（实施与单元测试均已完成，遗留的游戏内人工验证项见实施文档 §6.4）。
4. **工作流文档**：新增 `.github/prompts/数据处理工作流/性行为履历系统.md`（系统概述/数据结构/挂钩分布/面板架构/与其他系统的关系/扩展指南），并登记进该目录 README 与 CLAUDE.md 的文档索引（👨‍⚕️ 身体状态系统分类，文档计数 60→61）；同时修订 `身体信息面板系统.md` 中因体液/初次记录迁出而陈旧的段落。
