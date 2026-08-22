# Plan 10（实施步骤与记录）：性行为履历完整记录

> 本文件是 `plan_10_性行为履历完整记录_方案.md`（下文简称"方案"）的**实施步骤清单与过程记录**。需求背景、现状调查、设计决策、数据结构定义、面板信息架构、风险与范围外事项一律以方案文档为准；本文件只写"怎么做、怎么验、怎么回滚"，实施过程与结果记入 §6。

- 状态：**已实施并归档（含第二~九轮追加调整），单元测试全绿（127/127），遗留游戏内人工验证项见 §6.4**（2026-08-22 实施，过程记录见 §6；第二轮：子系统目录独立 + 体液数据迁入，见 §6.5；第三轮：六项展示层调整，见 §6.6；第四轮：收尾四项，见 §6.7；第五轮：文档去重，见 §6.8；第六轮：体液部位行完整句式，见 §6.9；第七轮：特殊履历附记H模式/食物来源，见 §6.10；第八轮：H模式判定移入Sex_System通用函数，见 §6.11；第九轮：面板单周目显示与周目切换，见 §6.12）
- 适用代码快照：`master @ 88caead6a`
- 实施前提：先通读方案文档；实施中发现与方案冲突的事实，先更新方案再动代码

---

## 1. 改动文件清单

> 注（第二轮调整，方案 §8.1）：下表中的 `Script/Design/first_record_handle.py` 与 `Script/UI/Panel/first_record_panel.py` 在第二轮已迁入 **`Script/System/First_Record_System/`**（另含新建的 `__init__.py` 与 `性行为履历系统设计文档.md`），本表保留首轮实施时的原始路径；迁移明细见 §6.5。

| 文件 | 类型 | 改动 |
| --- | --- | --- |
| `Script/Core/game_type.py` | 修改 | FIRST_RECORD 追加 9 个 dict 字段、删除 15 个平铺处女字段、`first_sex_*` docstring 收窄、新增 `has_any_record()`；Character 追加 `first_record_history` |
| `Script/Settle/default.py` | 修改 | 4 个破处 handler 的 NPC 侧写入改写进 dict（玩家侧不动）；新增 `record_first_part_sex` helper + 16 个 `PENIS_IN_T_*` handler 调用 |
| `Script/UI/Panel/ejaculation_panel.py` | 修改 | `update_semen_dirty` 记录初次被射精 |
| `Script/Design/second_behavior.py` | 修改 | `character_get_second_behavior` 统一分发：强/超强绝顶、刻印等级、受精/喷乳/放尿白名单 |
| `Script/Settle/orgasm_settle.py` | 修改 | 模块级部位反向映射常量（可顺手提升 part_dict/degree_dict）；多重绝顶生成点记录初次达成 |
| `data/csv/FirstRecordSpecial.csv` | **新建** | 特殊履历配置表（初始 8 条，§2.8(1)） |
| `Script/Config/game_config.py` | 修改 | config_first_record_special dict + load 函数 + init() 注册 |
| `Script/Design/first_record_handle.py` | **新建** | 通用写入函数、二段行为白名单映射、H 模式类中心判定、露出/隐奸模式名映射 |
| `Script/Design/settle_behavior.py` | 修改 | handle_settle_behavior 内 H 模式初体验中心挂钩（first_h_mode_dict，含无意识 7 类型拆分） |
| `Script/Design/character_handle.py` | 修改 | 生成孩子处记录第一次分娩（cid 2） |
| `Script/Design/handle_talent.py` | 修改 | 新增 `record_fall_talent_time` + :57 调用；:297 初潮（cid 5）、:244 精液膨腹（cid 6）、:264 精爱味觉（cid 8）三处专点 |
| `Script/System/Instruct_System/handle_instruct.py` | 修改 | 告白/项圈两处补记陷落时间 |
| `Script/Settle/common_default.py` | 修改 | exp42 结算补记口交初体验（E2）；exp111 结算记第一次饮精绝顶（cid 7） |
| `Script/UI/Panel/new_round.py` | 修改 | inherit_npc_data 两分支 + inherit_player_data 周目归档 |
| `Script/Design/handle_premise/handle_premise_first.py` | 修改 | 5 个 in_today 前提改读 dict（first_sex 保留玩家分支） |
| `Script/UI/Panel/body_info_panel.py` | 修改 | 移除【口】【膣】【肛】【宫】【尿】五块的初次详情句，状态行简化为"保有/已失去"，感度描述与 first_record 解耦（引用归零） |
| `Script/UI/Panel/physical_check_and_manage.py` | 修改 | 处女/A处女报告段改读 dict（补 `[3:]` 切片） |
| `Script/Core/save_handle.py` | 修改 | `_normalize_loaded_save_paths` 平铺→dict 存档迁移 + delattr 清理 |
| `Script/Core/old_chara_to_new.py` | 修改 | 三处 first_record 段追加 dict 与 first_record_history 的 id 重映射 |
| `Script/UI/Panel/first_record_panel.py` | **新建** | 履历文本组件（7 组折叠）+ 分页容器 |
| `Script/UI/Panel/see_character_info_panel.py` | 修改 | 接入第 5 分页（5 处小改） |

## 2. 详细改动步骤

### 2.1 `Script/Core/game_type.py`

**FIRST_RECORD（:505）**：
1. 删除 `first_a_sex_*`(5)、`first_u_sex_*`(5)、`first_w_sex_*`(4)、`first_m_sex_time`(1) 共 15 个字段。
2. `first_sex_*` 五个字段保留，docstring 改为「玩家童贞专用，NPC 的 V 破处记录在 first_part_sex_dict[6]」。
3. 追加 9 个 dict 字段——**字段名、键空间与值结构以方案 §4 的代码块为准**（first_part_sex_dict / first_shoot_body_dict / first_strong_orgasm_dict / first_super_orgasm_dict / first_plural_orgasm_dict / fall_talent_time_dict / first_mark_dict / first_h_mode_dict / first_special_record_dict）。
4. 增加方法 `has_any_record() -> bool`：`first_kiss_id != -1` 或 `first_sex_id != -1`（玩家童贞）或 9 个新 dict 任一非空。
5. 所有地点写入一律 `list(character_data.position)` 拷贝（引用赋值警告见 10_tem.md §6）。

**Character（约 :1624 `first_record` 附近）**：追加 `first_record_history: dict = {}`（周目数int → 该周目结束时的 FIRST_RECORD 快照）。

### 2.2 破处 handler 改写（`Script/Settle/default.py`）

玩家侧四处写入（:1038-1041/:1127-1130/:1193-1196/:1235-1238）**一字不动**。NPC 侧四处改写进 dict（无条件覆盖该键——破处是权威事件，可能早一步被同一次结算里的 E1 通用挂钩先建了简版条目）：

| handler | 原写入 | 改为 |
| --- | --- | --- |
| handle_first_sex `:1053-1056` + 道具 `:1092` | `first_sex_*` | `first_part_sex_dict[6] = {"id": character_id, "time": cache.game_time, "place": list(target_data.position), "posture": instruct_name, "item": 道具时1否则-1}` |
| handle_first_a_sex `:1142-1147` | `first_a_sex_*` | 键 8，同构 |
| handle_first_u_sex `:1199-1202` | `first_u_sex_*` | 键 9，同构（若未来接采尿器道具，item=2） |
| handle_first_w_sex `:1241-1244` | `first_w_sex_*` | 键 7，同构（无 item） |

`instruct_name` 仍来自 `get_last_valid_sex_behavior_id`（:1032，避免中断指令覆盖真实破处体位）。初吻两个 handler（:942/:1296）不动。

### 2.3 第一次被射精（`Script/UI/Panel/ejaculation_panel.py`）

`update_semen_dirty()` 的统一累加处（:253，`now_semen_data[1] += semen_count` 之前）：

```python
    # 部位历史累计精液量为0且本次有精液进入时，记录该部位的初次被射精
    if part_type == 0 and semen_count > 0 and now_semen_data[3] == 0 \
            and part_cid not in character_data.first_record.first_shoot_body_dict:
        character_data.first_record.first_shoot_body_dict[part_cid] = [cache.game_time, list(character_data.position)]
```

`semen_count > 0` 守卫必须保留——realtime_settle.py:255 会传负数扣减源部位。

### 2.4 二段行为类记录的统一分发（`Script/Design/second_behavior.py` + `Script/Settle/orgasm_settle.py`）

1. `orgasm_settle.py` 模块级（`orgasm_degree_order` 旁）新增反向映射，并可顺手把 :161-162 的局部 part_dict/degree_dict 提为模块常量消重：

```python
orgasm_part_to_state_id = {"s": 0, "b": 1, "c": 2, "p": 3, "v": 4, "a": 5, "u": 6, "w": 7, "m": 21, "f": 22, "h": 23}
""" 部位绝顶二段行为的部位字母到快感状态id的反向映射 """
```

2. `second_behavior.py:31 character_get_second_behavior()` 的 else（置 1）分支内，作为**二段行为类记录的统一分发点**，依次处理三类：

```python
        # ——履历记录：二段行为类统一分发——
        first_record = character_data.first_record
        # (1) 部位绝顶行为则记录初次强/超强绝顶
        orgasm_settle_module = _get_orgasm_settle()
        part_str, degree = orgasm_settle_module.get_orgasm_part_and_degree(second_behavior_id)
        if part_str is not None and degree >= 2:
            state_id = orgasm_settle_module.orgasm_part_to_state_id[part_str]
            if state_id not in first_record.first_strong_orgasm_dict:
                first_record.first_strong_orgasm_dict[state_id] = [cache.game_time, list(character_data.position)]
            if degree == 3 and state_id not in first_record.first_super_orgasm_dict:
                first_record.first_super_orgasm_dict[state_id] = [cache.game_time, list(character_data.position)]
        # (2) 刻印升级行为则记录刻印首达等级（id 格式 {类型}_mark_{等级}，全集见 SecondBehavior.py:56-108）
        elif "_mark_" in second_behavior_id and second_behavior_id not in first_record.first_mark_dict:
            first_record.first_mark_dict[second_behavior_id] = [cache.game_time, list(character_data.position)]
        # (3) 固定二段行为 id -> 特殊履历的白名单映射
        elif second_behavior_id in first_record_handle.SECOND_BEHAVIOR_TO_SPECIAL_CID:
            special_cid = first_record_handle.SECOND_BEHAVIOR_TO_SPECIAL_CID[second_behavior_id]
            special_data = first_record_handle.get_special_data_for_second_behavior(character_id, second_behavior_id)
            first_record_handle.record_first_special_record(character_id, special_cid, special_data)
```

白名单（定义在 first_record_handle.py）：`{"fertilization": 1, "b_orgasm_to_milk": 3, "u_orgasm_to_pee": 4}`；`get_special_data_for_second_behavior` 对 fertilization 返回是否无意识受精（此时 pregnancy.py:140-143 的 talent[35] 判定已完成，方案 §2.11），其余返回空串。刻印判定放在部位绝顶之后用 elif 即可——`X_orgasm_Y` 与 `X_mark_N` 格式互斥。

一处覆盖全部来源（绝顶：正常结算、寸止/时停解放、玩家 p_orgasm；刻印：中心刻印结算 + 监禁调教，零旁路，方案 §2.11）；同一次结算重复置 1 由 dict 去重。

### 2.5 陷落素质时间（`Script/Design/handle_talent.py` + `handle_instruct.py`）

`handle_talent.py` 新增：

```python
def record_fall_talent_time(character_id: int, talent_id: int):
    """
    记录获得陷落素质的时间与地点\n
    Keyword arguments:
    character_id -- 角色id\n
    talent_id -- 素质id，仅陷落素质(201~204,211~214)会被记录
    """
    if talent_id not in {201, 202, 203, 204, 211, 212, 213, 214}:
        return
    character_data = cache.character_data[character_id]
    if talent_id not in character_data.first_record.fall_talent_time_dict:
        character_data.first_record.fall_talent_time_dict[talent_id] = [cache.game_time, list(character_data.position)]
```

3 个调用点：`handle_talent.py:57`（`talent[talent_id] = 1` 之后）、`handle_instruct.py:1112` 之后（记 203）、`:1144` 之后（记 213）。

### 2.6 部位交初体验（E1 主挂钩 + E2 口交补充）

**E1**：`Script/Settle/default.py` 新增公共 helper，16 个 `PENIS_IN_T_*` handler（效果 802-817）在 `target_data.h_state.insert_position = N` 后各加一行调用：

```python
def record_first_part_sex(character_id: int, target_data: game_type.Character, item: int = -1):
    """
    部位交初体验记录（键取自 insert_position，未记录才写入；破处 handler 的完整写入会覆盖本条目）\n
    Keyword arguments:
    character_id -- 行为发起者id（记为对象）\n
    target_data -- 被交部位所属角色数据\n
    item -- 道具编号，-1无/0手指/1振动棒/2采尿器
    """
    part_id = target_data.h_state.insert_position
    if part_id == -1 or part_id >= 20:
        return
    if part_id in target_data.first_record.first_part_sex_dict:
        return
    behavior_name = ""
    behavior_id = cache.character_data[character_id].behavior.behavior_id
    if behavior_id in game_config.config_behavior:
        behavior_name = game_config.config_behavior[behavior_id].name
    target_data.first_record.first_part_sex_dict[part_id] = {
        "id": character_id, "time": cache.game_time,
        "place": list(target_data.position), "posture": behavior_name, "item": item,
    }
```

（姿势取行为发起者当前行为的中文名；实施时如与 `get_last_valid_sex_behavior_id` 的惯例冲突再对齐。）

**E2**：`Script/Settle/common_default.py:888 base_chara_experience_common_settle()`，最终角色解析完成后：

```python
    # 口交经验结算时补记口交初体验（覆盖早安咬/晚安咬、测试口腔吮吸、AI文本等不经阴茎位置效果的口交来源）
    if experience_id == 42 and 2 not in character_data.first_record.first_part_sex_dict:
        character_data.first_record.first_part_sex_dict[2] = {
            "id": 0, "time": cache.game_time,
            "place": list(character_data.position), "posture": "", "item": -1,
        }
```

判定条件**只用"无键 2"**，不用 `exp42==0`（方案 §3.2）。

### 2.7 多重绝顶初次达成（`Script/Settle/orgasm_settle.py`）

挂在唯一生成点（:317-321，方案 §2.3），`character_data.h_state.plural_orgasm_set = tem_orgasm_set.copy()`（:321）旁追加：

```python
    if part_count >= 2:
        second_behavior_id = f"plural_orgasm_{part_count}"
        second_behavior.character_get_second_behavior(character_id, second_behavior_id)
        character_data.h_state.plural_orgasm_set = tem_orgasm_set.copy()
        # 记录该等级多重绝顶的初次达成（时间/地点/参与部位）
        if part_count not in character_data.first_record.first_plural_orgasm_dict:
            character_data.first_record.first_plural_orgasm_dict[part_count] = [
                cache.game_time, list(character_data.position), sorted(tem_orgasm_set)]
```

- 参与部位存排序后的**快感状态 id 列表**（与强/超强绝顶同一键空间）。
- **不做高等级回填低等级**——各等级独立达成（与 `plural_orgasm_{N}` 按实际 part_count 生成的既有逻辑一致）。

### 2.8 特殊履历（CSV 驱动，可扩充）

**(1) 新建 `data/csv/FirstRecordSpecial.csv`**（5 行头格式，方案 §2.10；name/data_info 标记国际化）：

```csv
cid,name,data_info
配表id,履历名称,记录的特殊数据说明
int,str,str
0,1,1
特殊履历配置表,,
1,第一次受精,是否为无意识受精
2,第一次分娩,孩子的名字
3,第一次喷乳绝顶,无
4,第一次放尿绝顶,无
5,初潮,无
6,第一次获得精液膨腹素质,获得时的腹部精液总量
7,第一次饮精绝顶,精液所在位置（口腔/胃部）
8,获得精爱味觉素质,无
```

以后扩充特殊履历：在此表加行（cid 递增）+ 在代码中为该 cid 编写触发记录条件（调用下述通用函数），面板显示自动跟随配表。

**(2) `Script/Config/game_config.py`** 三步接入（方案 §2.10）：模块级 `config_first_record_special: Dict[int, config_def.FirstRecordSpecial] = {}`、加载函数 `load_first_record_special()`（照抄 :549 `load_ability_type_data` 的模式）、`init()`（:2192）注册一行。`config_def.FirstRecordSpecial` 数据类由 buildconfig 自动生成。

**(3) 新建 `Script/Design/first_record_handle.py`**，特殊履历的通用写入函数（现在与以后的所有触发点统一调用）：

```python
def record_first_special_record(character_id: int, special_cid: int, special_data: str = ""):
    """
    记录特殊履历（FirstRecordSpecial.csv 配表驱动，已记录则跳过）\n
    Keyword arguments:
    character_id -- 角色id\n
    special_cid -- FirstRecordSpecial.csv 中的配表id\n
    special_data -- 该履历要附记的特殊数据文本
    """
    if special_cid not in game_config.config_first_record_special:
        return
    character_data = cache.character_data[character_id]
    if special_cid in character_data.first_record.first_special_record_dict:
        return
    character_data.first_record.first_special_record_dict[special_cid] = [
        cache.game_time, list(character_data.position), special_data]
```

**(4) H 模式初体验（独立 dict `first_h_mode_dict`，追加需求 8）的中心触发挂钩**：`Script/Design/settle_behavior.py` 的 `handle_settle_behavior()`（:20）交互对象结算段（target_data 可用处），全部条件共用一次 `handle_self_is_h` 判定，收拢为 first_record_handle 里的函数 `check_first_h_mode(target_character_id)` 供 settle_behavior 调一行：

```python
def record_first_h_mode(character_id: int, mode_key: str, extra_data: str = ""):
    """H模式初体验通用写入（未记录才写）"""
    character_data = cache.character_data[character_id]
    if mode_key not in character_data.first_record.first_h_mode_dict:
        character_data.first_record.first_h_mode_dict[mode_key] = [cache.game_time, list(character_data.position), extra_data]

def check_first_h_mode(character_id: int):
    """H模式初体验的中心判定（由行为结算必经处调用）"""
    character_data = cache.character_data[character_id]
    if not handle_premise.handle_self_is_h(character_id):
        return
    # 无意识H按类型拆分为独立键（1睡眠~7心控），一名角色可积累至多7条
    if character_data.sp_flag.unconscious_h:
        record_first_h_mode(character_id, f"unconscious_{character_data.sp_flag.unconscious_h}")
    # 群交（附加数据：当时场景内角色数）
    if cache.group_sex_mode:
        record_first_h_mode(character_id, "group_sex", str(场景内角色数))
    # 露出H（附加数据：模式名，自写 _() 映射——方案 §2.11：无现成简洁列表）
    if character_data.sp_flag.exhibitionism_sex_mode:
        record_first_h_mode(character_id, "exhibitionism", 露出模式名[character_data.sp_flag.exhibitionism_sex_mode])
    # 隐奸H（附加数据：模式名）
    if character_data.sp_flag.hidden_sex_mode:
        record_first_h_mode(character_id, "hidden_sex", 隐奸模式名[character_data.sp_flag.hidden_sex_mode])
    # 装睡H
    if character_data.h_state.pretend_sleep:
        record_first_h_mode(character_id, "pretend_sleep")
```

- 露出/隐奸模式名映射（各 4 项，`_()` 包裹）与群交人数取值（`cache.scene_data[场景路径].character_list` 长度）都放 first_record_handle.py；无意识类型的显示名复用 `hypnosis_panel.unconscious_list`（面板侧拼「第一次{类型名}H」）。
- 选中心判定而非分散赋值点逐点挂（无意识 20+ 处，方案 §2.9）；dict 去重使每次结算的重复判定零成本。
- **注意**：要挂在 target 结算的必经逻辑段，**不要**挂 :259 的输出显示段（该段仅在有可显示变化时执行，可能漏记）；实施时以"每次玩家↔NPC 行为结算都会执行"为准定位。

**(5) 特殊履历的专点挂钩（cid 2/5/6/8，无二段行为可解析）**：
- **cid 2 第一次分娩**：`Script/Design/character_handle.py:165-198` 生成孩子处（:193 母亲关系挂上后），`record_first_special_record(mother_id, 2, child_name)`——地点即母亲分娩时所在位置。
- **cid 5 初潮**：`Script/Design/handle_talent.py:297`（`talent[6] = 0` 之后），`record_first_special_record(character_id, 5, "")`。
- **cid 6 第一次获得精液膨腹素质**：`Script/Design/handle_talent.py:244`（`npc_gain_and_lost_cumflation` 的 `talent[32] = 1` 之后），`record_first_special_record(character_id, 6, f"{abdomen_all_semen}ml")`——素质可得可失（:246-248），首次记录由 dict 去重保证，失去/再获得不再写。
- **cid 8 获得精爱味觉素质**：`Script/Design/handle_talent.py:264`（`npc_gain_semen_drinking_climax_talent` 的 `talent[31] = 1` 之后），`record_first_special_record(character_id, 8, "")`。
- （cid 1/3/4 受精/喷乳/放尿走统一分发点的白名单映射，见 §2.4(3)。）

**(6) cid 7 第一次饮精绝顶——经验类挂钩**：`Script/Settle/common_default.py:888 base_chara_experience_common_settle()`，与口交初体验（E2，exp 42）同函数并列一个分支：`experience_id == 111` 时 `record_first_special_record(final_character_id, 7, 位置名)`，位置名按 `h_state.shoot_position_body` 映射（2→口腔、15→胃部，其他值留空）——此时该字段尚未被重置（方案 §2.11）。一处覆盖全部饮精绝顶路径：口内射精绝顶、进食精液食物绝顶（plan_09 链路）、素质 31 条件反射绝顶。dict 去重使重复零成本。

### 2.9 周目归档（`Script/UI/Panel/new_round.py`）

- `inherit_npc_data()`：**两个分支**（:748 未陷落、:750 陷落）的 `init_character` 之后统一追加：

```python
            # 归档旧周目的性行为履历（old_npc_data 已整体 deepcopy，快照直接引用即可）
            new_data = cache.character_data[now_id]
            old_data = old_npc_data[now_id]
            new_data.first_record_history = getattr(old_data, "first_record_history", {})
            if old_data.first_record.has_any_record():
                new_data.first_record_history[cache.game_round] = old_data.first_record
```

- `inherit_player_data()`：`:663 new_pl_character_data.name = ...` 之后追加同样的归档（old_pl_character_data 亦已 deepcopy，:658）。
- 归档键 `cache.game_round` 此时仍是旧周目数（reset_game_data 最后才 +1，方案 §2.6）。

### 2.10 引用点改写（前提/面板/报告）

建议先做小工具（放 FIRST_RECORD 方法或新面板模块）：`get_part_sex_record(first_record, part_id) -> dict | None`，统一 `getattr(fr, "first_part_sex_dict", {})` 防御与取值。

| 位置 | 改法 |
| --- | --- |
| `handle_premise_first.py:69` handle_first_sex_in_today | `character_id == 0` 仍读 `first_sex_time`；否则读 dict 键 6 的 `"time"`（无键视为未发生） |
| `:98/:127/:156/:185`（a/u/w/m 四个 in_today） | 分别读 dict 键 8/9/7/2 的 `"time"`；before_today 与 target 系列复用这五个函数，无需另改 |
| `body_info_panel.py`（5 块，见下方详表） | **移除初次详情句 + 感度解耦**（追加需求 4，不是换数据源）；改完后 body_info_panel 对 first_record 的引用归零 |
| `physical_check_and_manage.py:979-989/:995-1005` | 处女/A处女段改读 dict 键 6/8；顺手补上 `get_date_until_day(t)[3:]` 切片（该处原本漏切）。体检报告性质不同，不并入履历面板 |

**body_info_panel.CharacterBodyText 的移除与解耦详表**（追加需求 4）：

| 块 | 现状 | 改为 |
| --- | --- | --- |
| 【口】:93-106 | 初吻情况：保有初吻 / 于{时}在{地}向{人}(的阴茎)献上了初吻 | 初吻情况：`talent[4]` → "保有初吻"，否则 → "已失去初吻（详见[性行为履历]）"；删除详情句与 first_kiss_* 读取 |
| 【膣】:170-188 | 处女情况详情句 + 感度文案耦合（保有→感度0 / elif first_sex_id != -1→真实感度 / 否则空串） | 处女情况：`talent[0]` → "保有处女"，否则 → "已失去处女（详见[性行为履历]）"；感度行解耦为 `talent[0] ? 感度0文案 : get_ability_lv_ui_text(4)` |
| 【肛】:199-216 | 同上（talent[1] / first_a_sex_*） | 同构：状态行 + `talent[1] ? 感度0 : get_ability_lv_ui_text(5)` |
| 【宫】:227-246 | 同上（talent[3] / first_w_sex_*，无记录时不显示状态行） | 同构：状态行（`talent[3]` → 保有 / 否则 → 已失去）+ `talent[3] ? 感度0 : get_ability_lv_ui_text(7)` |
| 【尿】:283-302 | 同上（talent[2] / first_u_sex_*） | 同构：状态行 + `talent[2] ? 感度0 : get_ability_lv_ui_text(6)` |

各块的精液量/技巧/怀孕等其余内容一概不动。解耦后"非处模板角色感度行为空串"的既有小毛病自然修复（感度只看素质，不再依赖破处记录存在与否）。

### 2.11 存档跨版本迁移（`Script/Core/save_handle.py`）

挂在 `_normalize_loaded_save_paths()`（:150-201，先例 :185-191；此函数在角色重建/recursive_update **之前**运行）。对每个角色的 `first_record`：

1. 旧档判据：无 `first_part_sex_dict` 属性（pickle 只还原 `__dict__`，旧档实例必带平铺字段、缺新 dict）→ 先补 `first_part_sex_dict = {}` 等 9 个 dict 默认值。
2. 转换（存在且已发生才转）：
   - **仅 NPC（cid != 0）**：`first_sex_id != -1` → 键 6 `{"id","time","place","posture","item"}`；随后把 NPC 的 `first_sex_*` 五个字段重置回默认值（字段保留给玩家用，**不 delattr**）。
   - 所有角色：`first_a_sex_id != -1` → 键 8；`first_u_sex_id != -1` → 键 9（**item 1采尿器 → 2**）；`first_w_sex_id != -1` → 键 7；`first_m_sex_time` 非 `datetime(1,1,1)` → 键 2（id=-1、posture=""、item=-1）。
3. 清理：对 `first_a_sex_*`/`first_u_sex_*`/`first_w_sex_*`/`first_m_sex_time` 逐个 `delattr`（hasattr 守卫）——这些字段已从类中删除，不清掉会被 recursive_update 当孤儿属性带进新对象并永久跟随存档。
4. 幂等：整段以"无 `first_part_sex_dict` 属性"为门槛，二次载入不重复转换。

### 2.12 角色 id 迁移（`Script/Core/old_chara_to_new.py`）

三处 first_record 段（:283-302、:759-769、:865-875）：
1. **保留**现有平铺字段的 hasattr 守卫重映射（服务尚未走本文件 §2.11 迁移的更老路径）。
2. 每处追加：遍历 `getattr(fr, 'first_part_sex_dict', {})`，值中 `rec.get("id", -1) > 0` 的按 old_to_new_id 重映射。
3. 每处追加：遍历 `getattr(character, 'first_record_history', {})` 的每个历史快照，做同样的 dict 重映射与平铺字段重映射（历史快照里同样存着角色 id）。

### 2.13 履历面板（新建 `Script/UI/Panel/first_record_panel.py` + 接入）

分组内容、条目文案与显示规则以**方案 §5（面板信息架构）**为准；本节只列实现要点：

**新模块**：
- 模块级折叠状态 `_fold_state: dict = {}`（键 `f"{周目}_{组序号}"` → bool；仅会话内有效，不进存档）。默认：当前周目 7 组全部展开，历史周目块所有组默认收起。
- `FirstRecordText(character_id, width, column, center_status)` 文本组件，写法照抄 `body_info_panel.CharacterBodyText`（:47-356）；渲染逻辑抽公共函数 `build_group_text(first_record, group_key)` 供当前/历史周目复用；读取历史快照字段一律 `getattr(record, "first_part_sex_dict", {})` 防御（老版本归档的快照可能缺新字段——recursive_update 不深入 dict 值回填）。
- 每组组头一个 `draw.Button`（`[▼组名]`/`[▶组名]`，`cmd_func` 翻转 `_fold_state`，return_text 加入 return_list；外层循环对未识别返回值直接下一帧重绘，无需改外层）。
- `See_Character_First_Record_Panel` 容器类，骨架照抄 `See_Character_Detailed_Attributes_Panel`（:154-181），但 **draw() 必须按 `SeeCharacterThirdPanel`（:211-215）的写法收集 return_list**，且在 draw() 开头 `self.return_list = []` 清空（现有代码未清空，靠每帧重建掩盖，本面板有按钮不能省）。

**接入 `see_character_info_panel.py`（5 处小改）**：
1. `:15` import 新模块（如遇循环导入，参照 :229 函数内 import 规避）
2. `:50-53` 实例化
3. `:62-68` 仅 NPC 的 `draw_data` 加 `_("性行为履历")` 分页（玩家不加）
4. `:76` 与 `:92` 两处 `column=4` → `5`（否则 5 个分页按钮排成 4+1 两行）
5. `:99-102` 补 fallback：查看玩家时若 `now_panel` 为「性行为履历」则退回「基础属性」

不需要改 constant.Panel / normal_flow.py / InstructConfig.csv / ui_text CSV。

## 3. 构建与缓存

新增了 `data/csv/FirstRecordSpecial.csv`（§2.8），**需要跑一次 `buildconfig.py`**（生成 data.json 条目与 config_def.FirstRecordSpecial 数据类；日常测试也可直接跑 game.py 走 auto_build_config 增量构建）。无其他 CSV/常量改动。配表的 name/data_info 已标记国际化，外语翻译需要时再跑 `buildpo.py`/`buildmo.py`。

```bash
# 本机必须用 conda 解释器（裸 python 是 Store 空壳别名）
.conda\python.exe buildconfig.py
.conda\python.exe game.py
```

## 4. 验证清单

### 4.1 单元测试（scratchpad 脚本，不入库；无头环境搭法参照 plan_09 §11.3）

- [x] 射精记录：`update_semen_dirty` 首次进入即记录；累计总量非 0 不记；负数（流出）不记；part_type != 0 不记
- [x] 强/超强绝顶：`X_orgasm_strong` 入 strong dict；`X_orgasm_super` 同时回填空缺的 strong；重复绝顶不覆盖首记
- [x] 多重绝顶：构造 2/3 部位同时跨阈值的快感状态走 `orgasm_settle_in_second_behavior`，断言 `first_plural_orgasm_dict` 以 part_count 为键入库、部位列表与 tem_orgasm_set 一致、重复达成不覆盖、4 重不回填 2/3 重
- [x] 特殊履历通用函数：`record_first_special_record` 对无效 cid 不写、重复不写
- [x] H 模式初体验：分别置 `unconscious_h=1..7`、`cache.group_sex_mode`、`exhibitionism_sex_mode=3`、`hidden_sex_mode=2`、`pretend_sleep=True` 走行为结算，断言 `first_h_mode_dict` 以对应键入库（无意识按类型独立成键，同一角色可积累多条）且附加数据正确（人数/模式名）；非 H 状态一概不记；重复触发不覆盖首记
- [x] 刻印：触发 `happy_mark_1`/`unconscious_mark_6` 等二段行为后 `first_mark_dict` 以行为 id 为键入库、重复升级不覆盖；监禁调教路径（yield/terror/hate_mark）同样入库
- [x] 统一分发白名单：触发 `fertilization`（含 talent[35] 置位路径断言特殊数据为无意识受精）、`b_orgasm_to_milk`、`u_orgasm_to_pee`，断言 cid 1/3/4 入库
- [x] 专点：调用生成孩子流程断言母亲 cid 2 入库且特殊数据为孩子名；`npc_lost_no_menarche_talent` 满足条件后 cid 5 入库；腹部精液 ≥6000ml 走 `npc_gain_and_lost_cumflation` 后 cid 6 入库且特殊数据带 ml 数（失去再获得不重写）；exp[111] 置 50 走 `npc_gain_semen_drinking_climax_talent` 后 cid 8 入库
- [x] 饮精绝顶：置 `shoot_position_body=2` 结算一次经验 111，断言 cid 7 入库且特殊数据为"口腔"；重复结算不覆盖
- [x] CSV 构建：跑 buildconfig 后 `game_config.config_first_record_special` 共 8 条、`[1].name == "第一次受精"`，config_def.FirstRecordSpecial 类存在
- [x] 陷落时间：gain_talent、告白（203）、项圈（213）三条路径均入 dict；非陷落素质不记（告白/项圈以 `record_fall_talent_time` 直调覆盖，UI 全流程见 §6.4）
- [x] 部位交：各 `PENIS_IN_T_*` handler 触发后对应键入 dict（以 `record_first_part_sex` 直调覆盖，16 个 handler 均为同一行调用）；重复不覆盖；破处 handler 覆盖 E1 简版条目并带姿势/道具；玩家童贞仍写 `first_sex_*` 平铺；E2 在 exp42 继承非 0 时仍能补记键 2
- [x] 存档迁移：构造带旧平铺字段的 FIRST_RECORD 过 `_normalize_loaded_save_paths`——NPC 的 V/A/U/W/M 数据转入键 6/8/9/7/2；U 道具 1→2；NPC 的 `first_sex_*` 被重置、玩家的原样保留；a/u/w/m 平铺属性被 delattr；二次载入幂等
- [x] 前提回归：5 个 in_today 前提在迁移后数据上的判定与迁移前一致（含玩家/NPC 两个分支）
- [x] 旧存档 recursive_update 后 9 个新 dict 与 `first_record_history` 为默认空
- [x] 周目归档：模拟 inherit 流程后历史快照入库、键为旧周目数、全空记录不归档、新周目存活记录为全新默认值、二周目再破处正常写入 dict

全部 16 项已由单元测试覆盖（92 断言全 PASS，明细见 §6.3）。

### 4.2 游戏内测试（由用户执行）

- [ ] 新分页「性行为履历」显示正常，含多周目分块；7 组展开/收起按钮点击生效且状态跨帧保持
- [ ] 肉体情况页各部位块只剩"保有/已失去"状态行，初吻/破处详情句只出现在履历页；非处模板角色的感度行不再为空（解耦生效）
- [ ] H 中触发一次多部位同时绝顶后，绝顶组出现「N重绝顶」条目（时间/地点/参与部位）；对时停中的干员做一次 H 后，H 模式组出现「第一次时停H」条目（再对催眠体控中的干员做一次，另出现「第一次体控H」——按类型独立）
- [ ] 干员首次获得快乐刻印后，陷落与刻印组出现该刻印等级条目；受精/分娩后特殊履历组出现对应条目（分娩附记孩子名）；群交/露出/隐奸各走一次 H 确认 H 模式组对应条目出现且附加数据正确
- [ ] 分页按钮条 column=5 排版正常；查看玩家自己不崩（fallback 生效）
- [ ] Tk 与 Web 两种绘制模式表现一致（含折叠按钮）
- [ ] 旧存档载入正常：肉体情况页、体检报告的处女信息照旧显示（数据源已换 dict）；口上无异常
- [ ] 走一次 Re:败者食尘，新周目中历史周目块可见、当前周目记录从零开始

## 5. 回滚

- 挂钩类改动（§2.2-2.9）各自独立，可分别删除；dict 中已写入的记录留在存档中无副作用（无读取方即无效数据）。特殊履历（§2.8）回滚时一并删除 CSV、game_config 加载与 first_record_handle.py，并重跑 buildconfig。
- 字段合并（§2.1 删字段 + §2.10/2.11/2.12 迁移与引用改写）是一个整体，需一起回滚：恢复 15 个平铺字段与原读写代码、删除迁移段。**注意**：已被 §2.11 迁移过并保存的新存档，回滚后平铺字段是默认值（数据在 dict 里）——因此字段合并部分建议在充分测试后再合入。body_info_panel 的详情句移除与感度解耦（§2.10 详表）也绑定在这个单元里——原详情句读取的正是被删字段，回滚字段合并时一并恢复原句。
- 面板（§2.13）独立，删除新文件与 see_character_info_panel.py 的 5 处小改即可。
- 除特殊履历的 CSV 外无构建产物变更。

## 6. 实施过程记录

> 实施时按 `plan/done/plan_09_进食绝顶与饮精绝顶经验.md` §11 的风格填写本节；每完成一个改动单元即更新，与方案发生偏离时先在方案文档修订、再在此注明。

### 6.1 实际改动

实施日期：2026-08-22。改动与 §1 清单完全一致，共 21 个文件（3 新建 + 18 修改；方案头部原写"20 个文件（3 新建 + 17 修改）"系笔误漏计 1 个修改文件，已随实施修订），逐文件记录如下（default.py 拆为两行对应两个步骤）：

| 文件 | 对应步骤 | 实际改动 |
| --- | --- | --- |
| `Script/Core/game_type.py` | §2.1 | FIRST_RECORD（:505）删除 15 个平铺字段；`first_sex_*` 五字段保留并在 docstring 标注「玩家童贞专用」；追加 9 个 dict 字段与 `has_any_record()` 方法；Character 在 `first_record` 之后（原 :1624）追加 `first_record_history` |
| `Script/Settle/default.py` | §2.2 | 4 个破处 handler 的 NPC 侧写入改为 dict：V→键6（含 `item_flag`，该 flag 在 V handler 中恒为 False 属既有事实）、A→键8（振动棒道具保留）、U→键9、W→键7；玩家侧四处一字未动；顺带删除 A handler 中引用已删字段的整段注释代码（原 :1151-1158） |
| `Script/Settle/default.py` | §2.6 E1 | 新增 `record_first_part_sex()` helper（含玩家 target 防御：`not target_data.cid` 直接返回）；16 个 `PENIS_IN_T_*` handler（原 :9757-10105）在 `insert_position = N` 后各加一行调用 |
| `Script/UI/Panel/ejaculation_panel.py` | §2.3 | `update_semen_dirty` 统一结算处（原 :253）插入初次被射精记录，四重守卫（part_type==0 / semen_count>0 / 累计总量==0 / dict 无键） |
| `Script/Design/second_behavior.py` | §2.4 | `character_get_second_behavior` 置 1 分支尾部追加三类统一分发（强/超强绝顶→刻印→白名单，elif 互斥）；顶部 import 增加 `first_record_handle` |
| `Script/Settle/orgasm_settle.py` | §2.4/§2.7 | 模块级新增 `orgasm_part_to_state_id` 反向映射（:161 局部 part_dict/degree_dict 未提升——属方案中的「可顺手」项，为最小化改动面未做）；多重绝顶生成点（原 :318-321）追加初次达成记录 |
| `data/csv/FirstRecordSpecial.csv` | §2.8(1) | 新建，8 条初始数据，与实施文档模板逐字一致（LF 行尾、UTF-8 无 BOM，与库内其他 CSV 一致） |
| `Script/Config/game_config.py` | §2.8(2) | `config_first_record_special` 模块级 dict（:127 前）、`load_first_record_special()`（load_font_data 前）、`init()` 注册（load_experience_types 之后） |
| `Script/Design/first_record_handle.py` | §2.8(3)(4) | 新建：`SECOND_BEHAVIOR_TO_SPECIAL_CID` 白名单、`get_special_data_for_second_behavior`、`record_first_special_record`、`record_first_h_mode`、`check_first_h_mode`、露出/隐奸模式名映射、`get_part_sex_record` 防御读取工具。顶层只导入 Core + map_handle + game_config；H 判定直读 `sp_flag.is_h`（不经 handle_premise，消除循环导入风险，语义与 `handle_self_is_h` 等价） |
| `Script/Design/settle_behavior.py` | §2.8(4) | `handle_settle_behavior` 在 add_time 计算后（进入任何分支前的必经处）对自己与交互对象各调一次 `check_first_h_mode`；import 行增加 first_record_handle |
| `Script/Design/character_handle.py` | §2.8(5) | `born_new_character` 母女关系挂上后（原 :193）记录 cid 2，函数内延迟 import 规避循环 |
| `Script/Design/handle_talent.py` | §2.5/§2.8(5) | 新增 `record_fall_talent_time()`；`gain_talent` 的 `talent[talent_id] = 1`（原 :57）后调用；膨腹（原 :244 后，附记 `{abdomen_all_semen}ml`）、精爱味觉（原 :264 后）、初潮（原 :297 后）三处专点；import 行增加 first_record_handle |
| `Script/System/Instruct_System/handle_instruct.py` | §2.5 | 告白（原 :1112）/项圈（原 :1144）两处直接赋值后补记 203/213；函数内延迟 import handle_talent（该文件原本未导入 handle_talent，顶层导入有循环风险） |
| `Script/Settle/common_default.py` | §2.6 E2/§2.8(6) | `base_chara_experience_common_settle` 结算最终值后追加：exp42 补记口交初体验（键 2，**加了 `final_character_id != 0` 玩家排除守卫**，方案代码块未写但与「玩家不做部位交记录」的口径一致）；exp111 记录 cid 7（口腔/胃部按 shoot_position_body 映射）；import 增加 first_record_handle |
| `Script/UI/Panel/new_round.py` | §2.9 | `inherit_player_data`（name 赋值后）与 `inherit_npc_data`（两分支 if/else 之后的循环体尾部，等效于「两分支之后统一追加」）各加归档段；NPC 侧用 `old_npc_data.get(now_id)` 防御旧数据缺角色 |
| `Script/Design/handle_premise/handle_premise_first.py` | §2.10 | 5 个 in_today 前提改读 dict（V 保留玩家平铺分支）；before_today 与 target 系列复用未改 |
| `Script/UI/Panel/body_info_panel.py` | §2.10 | 五块详情句移除+感度解耦，全部按详表执行；【宫】【尿】原「无记录时不显示状态行」改为恒显状态行；文件对 first_record 的引用归零（grep 确认），顺带移除已无用的 `attr_text`/`game_time` 导入 |
| `Script/UI/Panel/physical_check_and_manage.py` | §2.10 | 处女/A处女报告段改读 dict 键 6/8，补上 `[3:]` 切片；初吻段未动（字段未迁移） |
| `Script/Core/save_handle.py` | §2.11 | 新增 `_migrate_first_record_flat_fields()`（旧档判据/转换/delattr 清理/幂等，全按 §2.11 四步）；在 `_normalize_loaded_save_paths` 角色循环内避孕套 backfill 之后逐角色调用 |
| `Script/Core/old_chara_to_new.py` | §2.12 | 新增公共 helper `_remap_first_record_ids()`（平铺字段 hasattr 守卫保留 + first_part_sex_dict 值 id 重映射）；三处 first_record 段（原 :282-302/:755-769/:861-875）改为调用 helper 并追加 `first_record_history` 各快照的同样处理 |
| `Script/UI/Panel/first_record_panel.py` | §2.13 | 新建：模块级 `_fold_state`、7 个分组构建函数 + `build_group_text` 公共入口（历史快照读取全部 `getattr` 防御）、`FirstRecordText` 组件、`See_Character_First_Record_Panel` 容器（draw() 先清空再收集 return_list）；折叠按钮用 `draw.LeftButton`（▼/▶ 前缀，库内惯例），return_text 用内部 id `first_record_fold_{周目}_{组}` 保证多周目块间唯一；`_format_place` 对旧数据默认地点 `["0"]` 做 try/except 防御（返回「未知地点」，覆盖迁移产生的 M 记录与旧快照）；`_format_time` 同样做了 try/except 防御（返回「未知时间」——游戏历法只使用 3/6/9/12 月，`get_date_until_day` 对其他月份会抛 UnboundLocalError，防御异常时间数据） |
| `Script/UI/Panel/see_character_info_panel.py` | §2.13 | 5 处小改全部执行：import、NPC 分支实例化+分页注册、两处 column 4→5、draw() 补「性行为履历→基础属性」fallback |

**与方案的偏离（共 4 处，均为实现细节级）**：
1. `check_first_h_mode` 不调用 `handle_premise.handle_self_is_h` 而直读 `sp_flag.is_h`（等价语义），并加了「玩家不记录」守卫——玩家不进履历面板，群交等全局 flag 会在玩家对象上产生无意义记录。
2. E2（exp42）补记加了 `final_character_id != 0` 守卫，理由同上。
3. `record_first_part_sex` 加了 `not target_data.cid` 防御（正常流程 target 恒为 NPC——NPC 逆推也是把行为赋给玩家执行，`handle_npc_ai_in_h.py:580` 已确认；守卫仅防御未来的异常调用路径）。
4. orgasm_settle 的局部 part_dict/degree_dict 未提升为模块常量（方案标注「可顺手」，为控制改动面未做）。

**已知显示层限制（记录于此，非缺陷）**：处女素质模板为 0 的非处干员，其键 6/8/9/7 条目来自 E1 通用挂钩（初次插入而非破处），面板仍会沿用「夺走了处女」句式——写入侧无法区分两种来源（dict 值结构以方案 §4 为准，未扩充标记位）。

### 6.2 实施前的假设复核

复核时间：2026-08-22，代码快照 `master @ 88caead6a`（与方案标注一致，工作区 Script/ 无未提交改动）。方案 §2 现状调查逐条复核结果：

| 复核项 | 结果 |
| --- | --- |
| FIRST_RECORD 位置与 15 个平铺字段（game_type.py:505-562） | ✅ 一致 |
| Character.first_record 位置（game_type.py:1624） | ✅ 一致 |
| 破处 handler 四处玩家/NPC 写入（default.py:1036-1247） | ✅ 一致。附带发现：`handle_first_sex` 的 `item_flag` 在 :1029 恒为 False 且无再赋值，:1090-1092 的道具分支实际不可达（V 道具破处从未被记录过），改写后行为等价保留 |
| update_semen_dirty 统一累加处（ejaculation_panel.py:253-262），`semen_count>0` 守卫必要性 | ✅ 一致 |
| character_get_second_behavior 置 1 分支（second_behavior.py:31-59）、`_get_orgasm_settle` 懒加载（:14-29） | ✅ 一致 |
| orgasm_settle：part_dict 局部变量（:161）、强/超强敏感度门槛（:277-298）、喷乳/放尿生成点（:300-306）、多重绝顶唯一生成点（:318-321）、饮精绝顶经验结算（:313-316） | ✅ 一致 |
| gain_talent 通用赋值点（handle_talent.py:57）、告白/项圈绕过点（handle_instruct.py:1112/:1144） | ✅ 一致 |
| 膨腹（handle_talent.py:243-244，现场变量 abdomen_all_semen）、精爱味觉（:263-264）、初潮（:294-297） | ✅ 一致 |
| 分娩唯一点（character_handle.py `born_new_character`，函数起始行实为 :155，母女关系挂上为 :192-193） | ✅ 与方案 :165-198 的段落吻合（起始行号略有出入，不影响挂钩点） |
| 受精唯一点（Script/Design/pregnancy.py:137-146，talent[35] 判定在 fertilization 二段行为之前） | ✅ 一致 |
| base_chara_experience_common_settle（common_default.py:888，最终角色解析 :906-914，结算最终值 :949-952） | ✅ 一致 |
| 多周目流程（new_round.py:612-616，deepcopy :658/:741，两分支 :748/:750，game_round+1 :811） | ✅ 一致 |
| 5 个 in_today 前提（handle_premise_first.py:59-187） | ✅ 一致 |
| body_info_panel 五块初次详情句与感度耦合（【口】:92-106、【膣】:169-196、【肛】:198-225、【宫】:227-246、【尿】:283-302） | ✅ 一致，感度耦合形态与方案 §2.1 描述完全相符 |
| physical_check_and_manage 报告段（:955-1005，处女/A处女段漏切 `[3:]`） | ✅ 一致 |
| save_handle._normalize_loaded_save_paths（:150-201，角色循环 :172-191，避孕套 backfill 先例 :185-191） | ✅ 一致 |
| old_chara_to_new 三处 first_record 段（:282-302、:755-769、:861-875） | ✅ 一致 |
| see_character_info_panel（分页 dict :54-69、两处 column=4 :76/:92、fallback :99-102、外层每帧重建 :1716-1736） | ✅ 一致 |
| game_config 加载模式（load_ability_type_data :549-558）与 init() 注册链（:2192 起） | ✅ 一致 |
| hypnosis_panel.unconscious_list（:20，8 项含"无"） | ✅ 一致 |
| sp_flag 字段（is_h :744、unconscious_h :746、hidden_sex_mode :748、exhibitionism_sex_mode :752）、h_state.pretend_sleep（:495） | ✅ 一致 |
| 16 个 PENIS_IN_T 身体侧 handler（default.py:9757-10105，每个只做 insert_position=N） | ✅ 一致 |
| 循环导入排查：handle_premise 包不反向导入 second_behavior / handle_talent / settle_behavior；map_handle 为低层模块 | ✅ 新模块 first_record_handle 顶层只导入 Core 层 + map_handle + game_config，handle_self_is_h 改为直读 `sp_flag.is_h`，无循环风险 |

### 6.3 单元测试结果

测试脚本按约定不入库（scratchpad `test_plan10_first_record.py`），无头环境搭法沿用 plan_09 §11.3（`game_config.init()` + `map_config` + `attr_calculation.get_system_setting_zero()` + `basement.get_base_zero()` + 手工创建玩家 + `init_character_list()` 创建全部 NPC + 屏蔽 `draw.*.draw()`）。构建链验证：`buildconfig.py` 全量重建成功，`config_def.FirstRecordSpecial` 数据类生成，PO 文件含 12 处新配表文本；全部 21 个改动文件 `py_compile` 通过；`start_flow`/`character_behavior` 等全游戏导入链冒烟通过。

**92 项断言全部通过（PASS 92 / FAIL 0）**，按 §4.1 清单逐项对应：

| §4.1 项 | 断言数 | 结果 | 关键实测值 |
| --- | --- | --- | --- |
| 射精记录 | 5 | 全 PASS | 首次进入即记录；重复/累计总量非0/负数流出/服装部位均不记 |
| 强/超强绝顶 | 6 | 全 PASS | `v_orgasm_strong`→键4；`b_orgasm_super` 同时回填强 dict；重复不覆盖；small/normal 不记录 |
| 多重绝顶 | 5 | 全 PASS | 2部位（V+B）→键2 参与部位 `[1, 4]`；3重独立入库不覆盖2重；不回填4重 |
| 特殊履历通用函数 | 3 | 全 PASS | cid 999 不写；重复调用保留首记（含特殊数据） |
| H 模式初体验 | 10 | 全 PASS | 非H不记；unconscious_3 与 unconscious_6 独立成键；群交/露出（附"人前露出"）/隐奸（附"仅女方隐蔽"）/装睡入库；重复不覆盖；玩家不记录；经 `handle_settle_behavior` 真实行为结算路径联通（unconscious_1 入库） |
| 刻印 | 4 | 全 PASS | happy_mark_1 / unconscious_mark_6 / yield_mark_2 / terror_mark_1 / hate_mark_3 入库；重复升级不覆盖 |
| 统一分发白名单 | 4 | 全 PASS | fertilization→cid1（talent[35] 置位时特殊数据="无意识受精"）；b_orgasm_to_milk→cid3；u_orgasm_to_pee→cid4 |
| 专点挂钩 | 7 | 全 PASS | 初潮 cid5（talent[6] 同步归零）；膨腹 cid6 特殊数据 "8000ml"，失去→再获得不重写；精爱味觉 cid8；`born_new_character` 全流程后母亲 cid2 特殊数据="测试之子"且孩子角色生成 |
| 饮精绝顶 | 2 | 全 PASS | shoot_position_body=2 时 cid7 特殊数据="口腔"；重复结算不覆盖 |
| CSV 构建 | 3 | 全 PASS | `config_first_record_special` 共 8 条，`[1].name == "第一次受精"`，config_def 类存在 |
| 陷落时间 | 4 | 全 PASS | gain_talent 手动路径（201）、203/213 补记函数入库；非陷落素质 205 不记 |
| 部位交 | 9 | 全 PASS | E1 口交入库（id=0、姿势非空）；重复不覆盖；未插入/服装部位不记；玩家 target 不记；E2 在 exp42 继承非 0（=10）时仍补记键 2；真实 `handle_first_sex` 调用后 NPC 键 6 覆盖预置简版条目、处女素质清零、玩家童贞仍写平铺字段 |
| 存档迁移 | 11 | 全 PASS | NPC 的 V/A/U/W/M → 键 6/8/9/7/2；U 道具 1→2；NPC first_sex_* 重置、玩家原样保留；a/u/w/m 平铺属性 delattr；二次调用幂等 |
| 前提回归 | 4 | 全 PASS | 迁移后数据上 A/M 的 in_today 判定当天=1 非当天=0；玩家童贞分支当天=1 |
| recursive_update 兼容 | 2 | 全 PASS | 旧档缺新 dict/缺 first_record_history 经 recursive_update 后均为默认空 |
| 周目归档 | 6 | 全 PASS | 快照入库键=旧周目数、内容保留（对象引用一致）；新周目记录全新；全空记录 has_any_record=False；新周目再记录与历史互不影响 |
| 面板（补充冒烟，§4.1 未列） | 7 | 全 PASS | 含 1 历史周目块时构建+绘制无异常；折叠按钮 14 个（当前 7 + 历史 7）；折叠状态跨帧保持；7 组文本当前/历史双模式构建；旧快照缺字段防御（裸对象不炸）；SeeCharacterInfoPanel 的 NPC draw_data 含"性行为履历"；玩家查看时 fallback 回"基础属性" |

首轮测试唯一失败项为面板冒烟中的测试数据错误（历史快照造了 5 月日期，而游戏历法仅使用 3/6/9/12 月，`get_date_until_day` 对其他月份抛 UnboundLocalError）——顺势给面板 `_format_time` 加了防御（§6.1），修正测试日期后复跑全绿。

### 6.4 尚未覆盖的验证

§4.2 的游戏内测试需在真实游戏进程中由用户人工执行，本次全部未覆盖，遗留清单：

1. 新分页「性行为履历」的实际观感：单周目显示与周目切换按钮（第九轮后：默认当前周目，多周目时顶部切换行；当前周目 7 组/历史周目 6 组，默认只展开部位初体验组）、折叠按钮点击、分页按钮条 column=5 排版与新分页顺序
2. 肉体情况页改动后的观感（状态行 + 感度解耦后非处模板角色感度行不再为空）
3. H 中实际触发多部位绝顶 / 时停H / 体控H / 刻印 / 受精 / 分娩 / 群交 / 露出 / 隐奸后各组条目出现
4. Tk 与 Web 两种绘制模式的一致性（折叠按钮在 Web 模式的表现）
5. 旧存档载入（真实旧档过 `_normalize_loaded_save_paths` 迁移；单元测试只构造了模拟对象）
6. 走一次 Re:败者食尘（真实 inherit 流程；单元测试只复刻了归档代码段的逻辑）
7. 口上层回归（前提改读 dict 后，破处当日类口上的实际触发；单元测试只验证了前提函数本身）
8. （第二轮）体液数据组在游戏内的观感：各部位累计小节的长度、与肉体情况页（体液句移除后）的分工是否清晰
9. （第三轮）六项展示调整的游戏内确认：分页顺序（肉体情况→性行为履历→角色设定）、默认只展开部位初体验组、未记录条目不再出现占位行（记录较少的角色面板应显著变短）、初吻条目在部位初体验组首行、口腔/胃部行的喝精与"直入胃，肠胃吸收"合并显示

另注：§4.1 中「E2 在 exp42 继承非 0 时仍能补记键 2」「破处 handler 覆盖 E1 简版条目并带姿势/道具」等项已由单元测试覆盖；告白/项圈两处的补记走的是与单元测试相同的 `record_fall_talent_time`，但 `handle_confession`/`handle_give_necklace` 的 UI 全流程未在无头环境执行，游戏内做一次告白可顺带确认。

### 6.5 第二轮追加调整实施记录（方案 §8，2026-08-22 同日）

**(1) 履历系统独立子系统目录（方案 §8.1）**：

| 改动 | 明细 |
| --- | --- |
| 新建 `Script/System/First_Record_System/` | 含空 `__init__.py`（同其他子系统惯例）、`性行为履历系统设计文档.md`（系统概览/数据结构/挂钩分布/面板架构/扩充指引） |
| 迁入 `first_record_handle.py` | 自 `Script/Design/` 平移，内容零改动 |
| 迁入 `first_record_panel.py` | 自 `Script/UI/Panel/` 平移，随后叠加第二轮 (2) 的体液组改动 |
| import 路径更新（6 文件） | `second_behavior.py`、`settle_behavior.py`、`handle_talent.py`（顶层 Design 导入行拆出，改 `from Script.System.First_Record_System import first_record_handle`）；`common_default.py`（Design 导入块后独立一行）；`character_handle.py`（born_new_character 内延迟导入改路径）；`see_character_info_panel.py`（改 `from Script.System.First_Record_System import first_record_panel`） |

grep 复核：全库对 `Script.Design.first_record_handle` / `Script.UI.Panel...first_record_panel` 旧路径的引用归零；循环导入面未变（新包 `__init__.py` 为空，导入图只换路径不加边）。

**(2) 体液数据迁入履历面板（方案 §8.2）**：

| 文件 | 改动 |
| --- | --- |
| `Script/System/First_Record_System/first_record_panel.py` | 新增 `_FLUID_GROUP_NAME` 与 `_build_fluid_text(character_id)`（沿用肉体页原句式：全身累计→喝过的精液（含胃部拆分）→肠胃吸收→各部位累计小节（遍历 BodyPart.csv 只列非零）→乳汁→圣水，乳汁/圣水改用 `.get(character_id, 0)` 等价读取）；周目块分组循环改为组装 `group_entry_list`（7 履历组 + 当前周目在槽位 3 插入体液组，体液组以序号 -1 标识、调用 `_build_fluid_text` 而非 `build_group_text`）；折叠键语义改为「折叠槽位序号」（当前 8 槽/历史 7 槽，docstring 已更新） |
| `Script/UI/Panel/body_info_panel.py` | 移除十处体液内容：【总】整块（该块只含体液句）、【口】喝过精液句组、【胸】被淋精液+收集乳汁、【指】【足】被淋精液、【膣】【肛】【宫】【尿】被射入精液、【尿】收集圣水、【其他】肠胃吸收；顺带移除已无引用的 `pl_character_data` 赋值。移除后本文件对 `dirty`/`pl_collection` 引用归零（grep 确认），其余内容（感度/技巧/怀孕/孩子/母亲/姿势）未动 |

**(3) 第二轮单元测试**：原 92 项全部保持 PASS（含更新断言：面板折叠按钮 14→15，当前 8 组+历史 7 组），新增「体液数据组」10 项断言——全身总量 800ml、喝过 300ml（含 100ml 直入胃）、肠胃吸收 77ml、各部位累计只列非零、乳汁 120ml、圣水 45ml、全零占位文案、体液组仅当前周目块出现（历史块无该组按钮）、肉体情况页构建冒烟、肉体情况页十处体液句式全部不再出现。**合计 PASS 102 / FAIL 0**。

**(4) 回滚补充**：目录迁移可通过反向移动两文件 + 还原 6 处 import 撤销；体液组迁移的回滚 = 删除 `_build_fluid_text` 与 group_entry_list 插槽 + 还原 body_info_panel 十处句子（无数据层改动，无存档影响）。

### 6.6 第三轮展示层调整实施记录（方案 §8.3，2026-08-22 同日）

只改 2 个文件，数据结构与挂钩零变化：

| 文件 | 改动 |
| --- | --- |
| `Script/System/First_Record_System/first_record_panel.py` | ①`_GROUP_NAME_LIST` 减为 6 组、首组更名「部位初体验」；②`_build_first_kiss_text` 删除，初吻条目并入 `_build_part_sex_text` 首行（句式不变、加"初吻："前缀）；③6 个履历组构建函数与 `build_group_text` 移除 `is_current` 参数并删除全部占位分支，小节头改为对应 dict 非空才输出；④体液组重构：删除独立的喝精/肠胃吸收行与"未接触过/未品尝过"占位，口腔行显示"总共喝过Xml精液"、胃部行显示"有Yml精液在食道直接射进了胃里，肠胃一共吸收了Zml精液"（逗号并列，仅吸收无直入时单独显示吸收段），全零时组文本为空（面板兜底「无记录」）；⑤体液组插槽 3→2；⑥默认折叠改为 `default_expand = is_current and group_index == 0`（只展开当前周目的部位初体验组）；⑦`_fold_state` docstring 更新（当前 7 槽/历史 6 槽） |
| `Script/UI/Panel/see_character_info_panel.py` | NPC 分页 dict 重排：性行为履历移到肉体情况之后、角色设定之前 |

同步更新：子系统设计文档（分组列表/入口位置/折叠默认/显示规则/体液行合并）、方案文档（追加需求 12、§5 修订注记、§8.3）。

**第三轮单元测试**：原有断言按新行为更新（折叠按钮 15→13：当前 7+历史 6；`build_group_text` 双参数化；体液断言改为并入行格式），新增/替换断言 8 项——默认仅部位初体验组展开（▼恰好 1 个且为该组）、空记录 6 组文本全空、有记录组无任何占位文案、初吻并入部位初体验组、分页顺序（肉体情况→性行为履历→角色设定）、口腔行喝精格式、胃部行"直入胃，吸收"逗号并列格式、仅吸收无直入时胃部行保留、全零时体液文本为空。**合计 PASS 110 / FAIL 0**。

### 6.7 第四轮收尾实施记录（方案 §8.4，2026-08-22 同日）

| 项 | 改动 |
| --- | --- |
| ① 肉体页状态行简化 | `body_info_panel.py` 五处"已失去X（详见[性行为履历]）"→"已失去X"（初吻/处女/后庭处女/子宫处女/尿道处女） |
| ② 组间空行 | `first_record_panel.py` 的分组循环末尾追加一个 `line_feed`，每组（按钮+内容）后空一行 |
| ③ 文档归档 | 本方案与实施文档自 `plan/wait/` 移至 `plan/done/`；子系统设计文档中的 plan 路径引用同步改为 `plan/done/` |
| ④ 工作流文档 | 新建 `.github/prompts/数据处理工作流/性行为履历系统.md`（概述/核心组件/数据结构/挂钩分布表/面板架构/与其他系统的关系/扩展指南/注意事项）；登记进目录 README（🧼 污浊系统分类）并更新其页脚计数（61 个系统文档）与 CLAUDE.md 的文档列表及计数（62 文件=61 文档+README，原计数本就滞后一并修正）；顺带修订 `身体信息面板系统.md` 中因初次记录/体液内容迁出而陈旧的段落（概述、FIRST_RECORD 节、显示内容详解、收集系统接口、注意事项） |

第四轮回归测试：①②为纯文案/排版改动，原断言不受影响（"详见"未被任何断言引用；组间 line_feed 不计入按钮数），全量复跑 **PASS 110 / FAIL 0**。

### 6.8 文档去重（2026-08-22 同日）

`Script/System/First_Record_System/性行为履历系统设计文档.md` 与工作流文档、plan 归档文档内容重叠，已**降级为纯索引**（只保留指向 `.github/prompts/数据处理工作流/性行为履历系统.md` 与 plan/done 两份文档的链接，不再有具体内容）；工作流文档相应标注为该系统当前状态的唯一详细说明文档。本节及 §6.5(1) 中对该设计文档原有内容结构的描述均为历史记录。

### 6.9 体液部位行完整句式（追加需求 15，2026-08-22 同日）

`first_record_panel._build_fluid_text()` 中除口腔/胃部外的部位行由裸数字（"部位：Xml"）改为完整句式，沿用肉体情况页原措辞：腔内部位（6小穴/7子宫/8后穴/9尿道）用"总共被射入过Xml精液"、其余体表部位用"总共被淋上过Xml精液"。回归测试更新体液断言（腔内/体表句式各一例、"无裸数字行"检查，净增 3 项），全量复跑 **PASS 113 / FAIL 0**。

另：本次编辑时发现该文件被 IDE 自动补全误插入了一行 `from torch import int16`（全文件未使用，torch 不在 requirements.txt 中，保留会使无 torch 环境启动游戏时 ImportError），已一并移除。

### 6.10 特殊履历附记改为H模式/食物来源（追加需求 16，2026-08-22 同日）

| 文件 | 改动 |
| --- | --- |
| `Script/System/First_Record_System/first_record_handle.py` | 新增 `get_current_h_mode_text(character_id)`——非H→"非H"；H中无特殊模式→"正常H"；特殊模式按 无意识7类型（"{类型名}H"，延迟导入 hypnosis_panel 规避 hypnosis_panel→handle_talent→本模块 的循环导入）/群交/露出H/隐奸H/装睡H 收集、多模式顿号连接。新增 `get_semen_source_text(character_id)`——H中→H模式文本；非H→从进食上下文取精液食物名（依次查本人与玩家的 `behavior.target_food`，限 `special_seasoning in (11,12)`，优先 `Food.name`、缺省回退菜谱名；二段结算与进食结算同帧且 `handle_delete_food` 只删背包不清 target_food，上下文可靠——本轮实测复核）；两者皆无→"非H"。`get_special_data_for_second_behavior` 增加 b_orgasm_to_milk/u_orgasm_to_pee 分支返回当时 H 模式 |
| `Script/Settle/common_default.py` | exp111 分支的附记由 shoot_position_body 口腔/胃部映射改为 `get_semen_source_text(final_character_id)`，并增加"cid 7 未记录才计算"的前置守卫 |
| `Script/Design/handle_talent.py` | cid 8（精爱味觉）附记由空串改为 `get_semen_source_text(character_id)` |
| `data/csv/FirstRecordSpecial.csv` | cid 3/4 的 data_info→"当时的H模式"；cid 7/8→"H中的精液记当时的H模式，精液食物记食物名称"（全角逗号，不影响 CSV 解析）；已重跑 buildconfig |

设计取舍：喂食发生在 H 中时按"H中的精液"记 H 模式（此时"当时是H中"为真）；条件反射绝顶、避孕套饮精等非H非食物来源统一记"非H"。回归测试更新白名单/饮精/精爱味觉断言并新增 正常H/时停H/隐奸H/食物名 四类附记用例（净增 2 项），全量复跑 **PASS 115 / FAIL 0**。方案 §4 配表表格与本文件 §2.8 中 cid 3/4/7/8 的附记描述为首轮历史记录，现状以配表与工作流文档为准。

### 6.11 H模式判定移入Sex_System通用函数（追加需求 17，2026-08-22 同日）

用户先在 `first_record_handle.get_current_h_mode_text` 中把 H 模式判定改为**基于前提系统**（handle_premise 各前提函数）并补全模式覆盖（新增 乱伦H/爱情旅馆H/浴室H/逆推H/监禁H，合计：无意识 7 类型、群交、露出H、隐奸H、装睡H、乱伦H、爱情旅馆H、浴室H、逆推H、监禁H），随后由本轮完成迁移：

| 改动 | 明细 |
| --- | --- |
| 新建 `Script/System/Sex_System/h_mode_common.py` | H 模式判定通用函数文件，承载 `get_current_h_mode_text()`（用户的前提版实现原样迁入；hypnosis_panel 保持函数内延迟导入） |
| `Script/System/First_Record_System/first_record_handle.py` | 移除本地 `get_current_h_mode_text` 与顶层 `handle_premise` 导入；`get_semen_source_text()` 与 `get_special_data_for_second_behavior()`（cid 3/4 分支）改为**函数内延迟导入** `h_mode_common` 调用 |
| 循环导入治理 | 复核确认 `handle_premise/__init__ → instuct_judege → handle_talent → first_record_handle` 链真实存在——用户原先在 first_record_handle 顶层导入 handle_premise 会构成启动期导入环（靠导入顺序侥幸可运行）；迁移后 handle_premise 依赖收敛到 h_mode_common，且履历侧对 h_mode_common 采用函数内延迟导入（附记时机才触发），导入环彻底断开 |

回归测试：既有 H 模式附记断言（非H/正常H/时停H/隐奸H）在前提版判定下语义不变全数保持；新增通用函数专项用例 7 项——非H、正常H、浴室H、多模式顿号连接（"时停H、群交"）、监禁H、逆推H、履历模块不再自带实现。全量复跑 **PASS 122 / FAIL 0**。

### 6.12 面板单周目显示与周目切换（追加需求 18，2026-08-22 同日）

`first_record_panel.py` 的 `FirstRecordText` 由"当前+全部历史周目同屏"改为**单周目显示**：

- 模块级新增 `_selected_round`（-1 为跟随当前周目）与切换函数 `_select_round()`；无效选择（如换角色后该周目不存在）回退为当前周目；仅会话内有效
- 可查看周目列表 = 各历史周目升序 + 当前周目；**存在历史周目时**面板顶部渲染「周目切换」按钮行（每周目一个 `LeftButton`，当前周目标注"(当前)"，▶ 前缀标记正在查看项，return_text 为 `first_record_round_{周目}`）；无历史周目时不显示切换行
- 只渲染所选周目的一个内容块；体液数据组仅在查看当前周目时插入（历史周目无实时体液数据）
- 折叠默认值由"仅当前周目的部位初体验组展开"改为"**所查看周目**的部位初体验组展开、其余收起"（`default_expand = group_index == 0`）；折叠状态键 `{周目数}_{槽位}` 不变，各周目折叠状态互相独立
- 顺带清理：切换按钮宽度用 `int()` 收敛类型（与折叠按钮一致）

另：本轮前用户将配表 cid 7/8 的 data_info 精简为"H模式或精液食物的名称"，已随本轮重跑 buildconfig 使 data.json/config 同步。

回归测试：面板断言按新结构更新（按钮数 13→9：2 切换+7 折叠；新增 单周目显示、切换到历史周目、历史周目无体液组、历史周目按钮数 8、无历史时不显示切换行 共 5 项），全量复跑 **PASS 127 / FAIL 0**。方案追加需求 2 与 §5 的"同屏展示"设计自本轮起废除，现状以工作流文档为准。
