# 角色ID系统重构文档：将cid改为基于adv

## 1. 重构概述

### 1.1 当前状态

当前游戏中角色数据 `game_type.Character()` 的核心id为 `self.cid`，是从玩家的0号id开始的顺序排列：
- 玩家：cid = 0
- NPC角色：cid = 1, 2, 3, ... （顺序递增）

角色数据 `cache.character_data` 与模板数据 `cache.npc_tem_data` 之间的对应关系为：
- **模板id = 角色id - 1**（即 `npc_tem_data[character_id - 1]`）
- `npc_tem_data` 是一个 **List** 类型，按顺序存储

### 1.2 重构目标

将角色的 `cid` 改为基于 `adv` 属性（剧情NPC校验编号），使得：
- 每个角色的 `self.cid` 等于 `self.adv`
- 查找角色数据时，`cache.character_data[character_id]` 中的 `character_id` 等于该角色的 `adv`
- 角色数据与模板数据的id相同（不再是 `-1` 的关系）
- 玩家（id=0）保持不变

### 1.3 重构原因

- 通过 `adv` 直接访问角色数据，简化代码逻辑
- 消除 `cid - 1` 的偏移计算，减少潜在的错误
- 使角色id与游戏配置中的角色编号保持一致

---

## 2. 核心数据结构分析

### 2.1 Character 类（game_type.py:1464）

```python
class Character:
    """角色数据结构体"""

    def __init__(self):
        self.cid: int = 0
        """ 角色id """
        # ...
        self.adv: int = 0
        """ 剧情npc校验 """
```

### 2.2 NpcTem 类（game_type.py:37）

```python
class NpcTem:
    """npc模板用结构体对象"""

    def __init__(self):
        self.Name: str = ""
        """ npc名字 """
        # ...
        self.AdvNpc: int = 0
        """ 剧情npc校验 """
```

### 2.3 Cache 类（game_type.py:1692）

```python
self.npc_tem_data: List[NpcTem] = []
""" npc模板数据 """
self.character_data: Dict[int, Character] = {}
""" 角色数据 """
```

**重要**：当前 `npc_tem_data` 是 **List** 类型，需要改为 **Dict** 类型（键为 `AdvNpc`）。

---

## 3. 需要修改的文件清单

### 3.1 核心模块修改

#### 3.1.1 Script/Core/game_type.py

**修改内容**：
- 将 `npc_tem_data` 从 `List[NpcTem]` 改为 `Dict[int, NpcTem]`

**修改位置**：行1692

```python
# 修改前
self.npc_tem_data: List[NpcTem] = []

# 修改后
self.npc_tem_data: Dict[int, NpcTem] = {}
```

#### 3.1.2 Script/Config/character_config.py

**修改内容**：
- 修改 `character_tem_list` 从 List 改为 Dict
- 修改 `init_character_tem_data()` 函数中的模板存储逻辑

**修改位置**：行9-12, 行82

```python
# 修改前
character_tem_list:List[game_type.NpcTem] = []
# ...
character_tem_list.append(now_tem)

# 修改后
character_tem_list: Dict[int, game_type.NpcTem] = {}
# ...
character_tem_list[now_tem.AdvNpc] = now_tem
```

#### 3.1.3 Script/Design/character_handle.py

**修改内容**：
- 修改 `init_character_list()` 函数，使用 `AdvNpc` 作为角色id
- 修改 `init_character_tem()` 函数

**修改位置**：行28-36, 行128-133, 行187-193

```python
# 修改前（行28-36）
def init_character_list():
    """
    初始生成所有npc数据
    """
    id_list = iter([i + 1 for i in range(len(cache.npc_tem_data))])
    npc_data_iter = iter(cache.npc_tem_data)
    for now_id, now_npc_data in zip(id_list, npc_data_iter):
        init_character(now_id, now_npc_data)

# 修改后
def init_character_list():
    """
    初始生成所有npc数据
    """
    for adv_id, now_npc_data in cache.npc_tem_data.items():
        init_character(adv_id, now_npc_data)

# 修改前（行128-133）
def init_character_tem():
    """
    初始化角色模板数据
    """
    cache.npc_tem_data = character_config.character_tem_list

# 修改后（无变化，但需确认character_tem_list已改为Dict）

# 修改前（行187-193）
cache.npc_tem_data.append(now_tem)
now_id = len(cache.npc_tem_data)
init_character(now_id, cache.npc_tem_data[-1])

# 修改后
now_id = now_tem.AdvNpc  # 或根据实际需求分配新的adv
cache.npc_tem_data[now_id] = now_tem
init_character(now_id, cache.npc_tem_data[now_id])
```

**修改 `born_new_character()` 函数**：

原函数无返回值，不便获取新生成角色的ID。需要修改为返回 `int` 类型的新角色ID：

```python
# 修改前
def born_new_character(mother_id, child_name):
    # ...
    # 无返回值

# 修改后
def born_new_character(mother_id, child_name) -> int:
    # ...
    return now_id  # 返回新角色的ID（等于adv）
```

---

### 3.2 存档处理模块（最关键）

#### 3.2.1 Script/Core/save_handle.py

**需要修改的内容**：

1. **修改 `input_load_save()` 函数中的模板关联逻辑**（行180）

```python
# 修改前
tem_character = loaded_dict["npc_tem_data"][new_character_data.cid - 1]

# 修改后 - 需要根据adv查找模板，使用.get()方法确保安全访问
tem_character = loaded_dict["npc_tem_data"].get(new_character_data.cid, None)
if tem_character is None:
    # 如果找不到，尝试用adv
    tem_character = loaded_dict["npc_tem_data"].get(new_character_data.adv, None)
if tem_character is None:
    # 处理找不到模板的情况（玩家跳过，NPC创建空白模板）
    if new_character_data.cid != 0:
        tem_character = character_handle.create_empty_character_tem()
        tem_character.Name = new_character_data.name
        tem_character.AdvNpc = new_character_data.adv
        loaded_dict["npc_tem_data"][new_character_data.cid] = tem_character
    else:
        continue
```

2. **添加存档迁移函数**：

将迁移逻辑拆分为多个独立函数，便于维护和复用：

- `migrate_npc_tem_data_to_dict()`: 处理 `npc_tem_data` 从List到Dict的转换
- `migrate_character_id_to_adv()`: 处理character_data的键迁移（从顺序ID到adv）
- `migrate_character_id_references()`: 处理所有角色ID引用的迁移（通用函数，见下文第5点）
- `fix_missing_character_template()`: 修复缺失角色模板的角色数据（见下文第6点）

3. **添加旧存档迁移函数**：

需要新增一个函数来处理旧存档的数据迁移：

```python
def migrate_old_save_data(loaded_dict):
    """
    将旧版存档的角色ID从顺序排列迁移到基于adv的格式
    """
    update_count = 0
    
    # 1. 首先处理npc_tem_data：从List转换为Dict
    if isinstance(loaded_dict["npc_tem_data"], list):
        old_tem_list = loaded_dict["npc_tem_data"]
        new_tem_dict = {}
        for tem in old_tem_list:
            new_tem_dict[tem.AdvNpc] = tem
        loaded_dict["npc_tem_data"] = new_tem_dict
        update_count += len(old_tem_list)
    
    # 2. 处理character_data：重新建立以adv为键的字典
    old_character_data = loaded_dict["character_data"]
    new_character_data = {}
    
    for old_cid, character in old_character_data.items():
        if old_cid == 0:  # 玩家保持id=0
            new_character_data[0] = character
            character.cid = 0
        else:
            new_cid = character.adv
            character.cid = new_cid
            new_character_data[new_cid] = character
    
    loaded_dict["character_data"] = new_character_data
    
    # 3. 更新npc_id_got集合
    old_npc_id_got = loaded_dict.get("npc_id_got", set())
    new_npc_id_got = set()
    for old_id in old_npc_id_got:
        if old_id in old_character_data:
            new_npc_id_got.add(old_character_data[old_id].adv)
    loaded_dict["npc_id_got"] = new_npc_id_got
    
    # 4. 更新其他引用角色ID的数据结构
    # ... 需要遍历所有包含角色ID引用的数据
    
    return update_count
```

3. **修改 `update_tem_character()` 函数**（行337-430）

```python
# 修改前
for i, now_npc_tem_data in enumerate(loaded_dict["npc_tem_data"]):
    # ...
    loaded_dict["npc_tem_data"][i] = cache_dict[now_npc_tem_data.AdvNpc]

# 修改后 - npc_tem_data已经是Dict
for adv_id, now_npc_tem_data in loaded_dict["npc_tem_data"].items():
    # ...
    if adv_id in cache_dict:
        loaded_dict["npc_tem_data"][adv_id] = cache_dict[adv_id]
```

4. **修改 `fix_wrong_character()` 函数**（行435-465）

需要根据新的ID结构调整角色数据修复逻辑。其中阿玛雅修复逻辑处的模板访问 `npc_tem_data[value.cid - 1]` 需要改为使用 `.get()` 方法，先尝试 `cid` 再尝试 `adv` 作为key：

```python
# 修改前
now_tem_chara = loaded_dict["npc_tem_data"][value.cid - 1]

# 修改后
now_tem_chara = loaded_dict["npc_tem_data"].get(value.cid, None)
if now_tem_chara is None:
    now_tem_chara = loaded_dict["npc_tem_data"].get(value.adv, None)
```

5. **新增 `migrate_character_id_references()` 通用函数**

角色ID引用迁移涉及多个数据结构（收藏品、好感度、关系、场景角色列表、罗德岛设施等），需要一个通用函数统一处理：

**需求说明**：
- 输入 `old_to_new_id` 映射字典，描述旧ID到新ID的对应关系
- 输入 `character_ids_to_process` 列表，指定需要处理的角色ID
  - 如果列表为空或None，则处理所有角色的ID引用
  - 如果列表非空，则只处理列表中指定角色的ID引用
- 遍历所有包含角色ID引用的数据结构，将旧ID替换为新ID

**需要处理的数据结构**：
- `npc_id_got`、`forbidden_npc_id` 集合
- 每个角色的 `target_character_id`、`assistant_character_id`
- 每个角色的 `favorability` 好感度字典
- 每个角色的 `relationship`（父母ID、子女ID列表）
- `scene_data` 中各场景的 `character_list`
- `rhodes_island` 中的所有角色ID字段（详见附录A.2）
- 玩家收藏品（`token_list`、`first_panties`、`npc_panties`、`npc_socks`）

**使用场景**：
- 全量迁移：`migrate_character_id_to_adv()` 中调用，不传 `character_ids_to_process`
- 单角色迁移：`fix_missing_character_template()` 中ID重分配时调用，只传需要迁移的角色ID

6. **新增 `fix_missing_character_template()` 函数**

当存档中的角色数据找不到对应的角色模板时，需要进行修复处理：

**需求说明**：
- 遍历所有角色数据，检查其 `adv` 是否在 `npc_tem_data` 中有对应模板
- 如果模板缺失，根据角色姓名在现有模板中查找同名模板

**修复策略**：
| 情况 | 处理方式 |
|-----|---------|
| 无同名模板 | 根据角色数据创建空白模板（复制性别、种族、势力、出生地等信息） |
| 有同名模板，且模板adv未被占用 | 将角色的id和adv改为模板的adv值，并调用 `migrate_character_id_references()` 迁移所有ID引用 |
| 有同名模板，但模板adv已有角色数据 | 深拷贝该模板，设置新adv后添加到模板数据 |

**触发场景**：
- 角色模板被删除但存档中仍有该角色数据
- 角色模板的adv被修改导致存档中的角色找不到对应模板
- 旧版本存档中的角色在新版本中模板结构发生变化

7. **修改 `update_chara_cloth()` 函数**（行622-680）

```python
# 修改前
tem_character = tem_character  # 这行有误，实际是从参数获取

# 需要确认调用时传入正确的模板数据
```

8. **修改 `update_new_character()` 函数**（行684-710）

原逻辑使用顺序ID分配，重构后使用 `now_npc_data.AdvNpc` 作为新角色ID：

```python
# 修改前
for i, now_npc_data in enumerate(add_new_character_list):
    new_character_cid = len_old_character + i
    new_character = character_handle.init_character(new_character_cid, now_npc_data)
    loaded_dict["character_data"][new_character_cid] = new_character

# 修改后
for now_npc_data in add_new_character_list:
    new_character_cid = now_npc_data.AdvNpc  # 使用adv作为cid
    new_character = character_handle.init_character(new_character_cid, now_npc_data)
    loaded_dict["character_data"][new_character_cid] = new_character
```

---

### 3.3 服装系统修改

#### 3.3.1 Script/Design/clothing.py

**修改位置**：行31, 行65

**模板访问安全性**：使用 `.get()` 方法和空值检查，防止模板不存在时出错：

```python
# 修改前
tem_character = cache.npc_tem_data[character_id - 1]

# 修改后 - 添加安全访问和空值检查
tem_character = cache.npc_tem_data.get(character_id, None)
if tem_character is None:
    return  # 模板不存在时安全返回
```

---

### 3.4 UI面板修改

#### 3.4.1 Script/UI/Flow/creator_character_flow.py

**修改位置**：行404, 735, 744, 755, 776, 784, 803, 824, 843

```python
# 修改前
self.id_list = [i + 1 for i in range(len(cache.npc_tem_data))]

# 修改后
self.id_list = list(cache.npc_tem_data.keys())

# 或者如果需要排序
self.id_list = sorted(cache.npc_tem_data.keys())
```

**修改位置**：行736-738

```python
# 修改前
for i in range(len(cache.npc_tem_data)):
    npc_id = i + 1
    if npc_id not in cache.npc_id_got:
        cache.npc_id_got.add(npc_id)

# 修改后
for adv_id in cache.npc_tem_data.keys():
    if adv_id not in cache.npc_id_got:
        cache.npc_id_got.add(adv_id)
```

#### 3.4.2 Script/UI/Panel/recruit_panel.py

**修改位置**：行67-76

```python
# 修改前
for i in range(len(cache.npc_tem_data)):
    chara_id = i + 1
    # ...
    if cache.npc_tem_data[i].Mother_id != 0 or cache.npc_tem_data[i].AdvNpc > 9000:

# 修改后
for adv_id, tem_data in cache.npc_tem_data.items():
    chara_id = adv_id
    # ...
    if tem_data.Mother_id != 0 or tem_data.AdvNpc > 9000:
```

#### 3.4.3 Script/UI/Panel/normal_panel.py

**修改位置**：行136-138

```python
# 修改前
for i in range(len(cache.npc_tem_data)):
    chara_id = i + 1

# 修改后
for adv_id in cache.npc_tem_data.keys():
    chara_id = adv_id
```

#### 3.4.4 Script/UI/Panel/debug_panel.py

**修改位置**：行549, 742-743

```python
# 修改前
id_list = [i + 1 for i in range(len(cache.npc_tem_data))]

# 修改后
id_list = list(cache.npc_tem_data.keys())

# 修改前
for i in range(len(cache.npc_tem_data)):
    chara_id = i + 1

# 修改后
for adv_id in cache.npc_tem_data.keys():
    chara_id = adv_id
```

#### 3.4.5 Script/UI/Panel/new_round.py

**修改位置**：行613, 712-713

```python
# 修改前（行613）
character_handle.init_character(character_id, cache.npc_tem_data[character_id])

# 修改后
character_handle.init_character(character_id, cache.npc_tem_data[character_id])
# 无需修改，只要npc_tem_data改为Dict后，用adv_id作为键即可正确访问

# 修改前（行712-713）
id_list = iter([i + 1 for i in range(len(cache.npc_tem_data))])
npc_data_iter = iter(cache.npc_tem_data)

# 修改后
for adv_id, now_npc_data in cache.npc_tem_data.items():
    # 原来的循环体逻辑
```

---

### 3.5 前提判断模块

#### 3.5.1 Script/Design/handle_premise/handle_premise_other.py

**修改位置**：行858-859

```python
# 修改前
for i in range(len(cache.npc_tem_data)):
    chara_id = i + 1

# 修改后
for adv_id in cache.npc_tem_data.keys():
    chara_id = adv_id
```

---

### 3.6 属性计算模块

#### 3.6.1 Script/Design/attr_calculation.py

**修改位置**：行32-34, 行432-433

```python
# 修改前
for i in range(len(cache.npc_tem_data)):
    chara_adv_id = cache.npc_tem_data[i].AdvNpc

# 修改后
for adv_id, tem_data in cache.npc_tem_data.items():
    chara_adv_id = tem_data.AdvNpc  # 或直接使用 adv_id
```

---

## 4. 存档兼容性处理

### 4.1 版本检测

在 `input_load_save()` 函数中添加版本检测逻辑：

```python
def input_load_save(save_id: str):
    # ...
    loaded_dict = load_save(save_id).__dict__

    # 检测是否为旧版存档（npc_tem_data是List而不是Dict）
    if isinstance(loaded_dict.get("npc_tem_data"), list):
        draw_text = _("\n检测到旧版存档，开始迁移角色ID系统...\n")
        now_draw = draw.LeftDraw()
        now_draw.text = draw_text
        now_draw.draw()
        
        migrate_count = migrate_old_save_data(loaded_dict)
        
        draw_text = _("\n角色ID迁移完成，共处理{0}条数据\n").format(migrate_count)
        now_draw = draw.LeftDraw()
        now_draw.text = draw_text
        now_draw.draw()
    # ...
```

### 4.2 迁移函数详细实现

```python
def migrate_old_save_data(loaded_dict) -> int:
    """
    将旧版存档的角色ID从顺序排列迁移到基于adv的格式
    
    迁移内容：
    1. npc_tem_data: List -> Dict (键为AdvNpc)
    2. character_data: 键从顺序id改为adv
    3. npc_id_got: 集合中的id改为adv
    4. 所有引用character_id的数据结构
    
    Returns:
        int: 迁移的数据条目数
    """
    update_count = 0
    
    # 1. 转换npc_tem_data
    if isinstance(loaded_dict["npc_tem_data"], list):
        old_tem_list = loaded_dict["npc_tem_data"]
        new_tem_dict = {}
        for tem in old_tem_list:
            new_tem_dict[tem.AdvNpc] = tem
        loaded_dict["npc_tem_data"] = new_tem_dict
        update_count += len(old_tem_list)
    
    # 2. 建立旧id到新id的映射
    old_to_new_id = {0: 0}  # 玩家id保持为0
    old_character_data = loaded_dict["character_data"]
    
    for old_cid, character in old_character_data.items():
        if old_cid != 0:
            old_to_new_id[old_cid] = character.adv
    
    # 3. 转换character_data
    new_character_data = {}
    for old_cid, character in old_character_data.items():
        if old_cid == 0:
            new_character_data[0] = character
            character.cid = 0
        else:
            new_cid = character.adv
            character.cid = new_cid
            new_character_data[new_cid] = character
        update_count += 1
    loaded_dict["character_data"] = new_character_data
    
    # 4. 转换npc_id_got
    old_npc_id_got = loaded_dict.get("npc_id_got", set())
    new_npc_id_got = set()
    for old_id in old_npc_id_got:
        if old_id in old_to_new_id:
            new_npc_id_got.add(old_to_new_id[old_id])
    loaded_dict["npc_id_got"] = new_npc_id_got
    
    # 5. 转换其他引用角色ID的数据结构
    # 5.1 玩家收藏品
    if 0 in new_character_data:
        pl_data = new_character_data[0]
        if hasattr(pl_data, 'pl_collection'):
            # token_list
            old_token = pl_data.pl_collection.token_list.copy()
            pl_data.pl_collection.token_list = {}
            for old_id, value in old_token.items():
                new_id = old_to_new_id.get(old_id, old_id)
                pl_data.pl_collection.token_list[new_id] = value
            
            # first_panties
            old_panties = pl_data.pl_collection.first_panties.copy()
            pl_data.pl_collection.first_panties = {}
            for old_id, value in old_panties.items():
                new_id = old_to_new_id.get(old_id, old_id)
                pl_data.pl_collection.first_panties[new_id] = value
            
            # npc_panties
            old_npc_panties = pl_data.pl_collection.npc_panties.copy()
            pl_data.pl_collection.npc_panties = {}
            for old_id, value in old_npc_panties.items():
                new_id = old_to_new_id.get(old_id, old_id)
                pl_data.pl_collection.npc_panties[new_id] = value
            
            # npc_socks
            old_npc_socks = pl_data.pl_collection.npc_socks.copy()
            pl_data.pl_collection.npc_socks = {}
            for old_id, value in old_npc_socks.items():
                new_id = old_to_new_id.get(old_id, old_id)
                pl_data.pl_collection.npc_socks[new_id] = value
    
    # 5.2 每个角色的favorability字典（角色id:好感度）
    for char_id, character in new_character_data.items():
        if hasattr(character, 'favorability'):
            old_fav = character.favorability.copy()
            character.favorability = {}
            for old_id, value in old_fav.items():
                new_id = old_to_new_id.get(old_id, old_id)
                character.favorability[new_id] = value
    
    # 5.3 每个角色的target_character_id
    for char_id, character in new_character_data.items():
        if hasattr(character, 'target_character_id'):
            old_target = character.target_character_id
            character.target_character_id = old_to_new_id.get(old_target, old_target)
    
    # 5.4 每个角色的assistant_character_id
    for char_id, character in new_character_data.items():
        if hasattr(character, 'assistant_character_id'):
            old_assistant = character.assistant_character_id
            character.assistant_character_id = old_to_new_id.get(old_assistant, old_assistant)
    
    # 5.4b 每个角色的其他角色ID引用
    for char_id, character in new_character_data.items():
        # ask_group_sex_refuse_chara_id_list - 拒绝群P的角色id列表
        if hasattr(character, 'ask_group_sex_refuse_chara_id_list'):
            character.ask_group_sex_refuse_chara_id_list = [
                old_to_new_id.get(oid, oid) for oid in character.ask_group_sex_refuse_chara_id_list
            ]
        
        # state_active.bagging_chara_id - 玩家正在装袋搬走的角色id
        if hasattr(character, 'state_active') and hasattr(character.state_active, 'bagging_chara_id'):
            if character.state_active.bagging_chara_id != 0:
                character.state_active.bagging_chara_id = old_to_new_id.get(
                    character.state_active.bagging_chara_id, 
                    character.state_active.bagging_chara_id
                )
        
        # sp_flag.carry_chara_id_in_time_stop - 时停中正在搬运的角色id
        if hasattr(character, 'sp_flag') and hasattr(character.sp_flag, 'carry_chara_id_in_time_stop'):
            if character.sp_flag.carry_chara_id_in_time_stop != 0:
                character.sp_flag.carry_chara_id_in_time_stop = old_to_new_id.get(
                    character.sp_flag.carry_chara_id_in_time_stop,
                    character.sp_flag.carry_chara_id_in_time_stop
                )
        
        # sp_flag.free_in_time_stop_chara_id - 时停中允许自由活动的角色id
        if hasattr(character, 'sp_flag') and hasattr(character.sp_flag, 'free_in_time_stop_chara_id'):
            if character.sp_flag.free_in_time_stop_chara_id != 0:
                character.sp_flag.free_in_time_stop_chara_id = old_to_new_id.get(
                    character.sp_flag.free_in_time_stop_chara_id,
                    character.sp_flag.free_in_time_stop_chara_id
                )
        
        # interacting_character_end_info[0] - 正在对自己进行交互的对方角色id
        if hasattr(character, 'interacting_character_end_info'):
            if character.interacting_character_end_info[0] != -1:
                character.interacting_character_end_info[0] = old_to_new_id.get(
                    character.interacting_character_end_info[0],
                    character.interacting_character_end_info[0]
                )

    # 5.5 rhodes_island中的角色引用
    if "rhodes_island" in loaded_dict:
        ri = loaded_dict["rhodes_island"]
        
        # === 人事管理区 ===
        # hr_operator_ids_list
        if hasattr(ri, 'hr_operator_ids_list'):
            ri.hr_operator_ids_list = [old_to_new_id.get(oid, oid) for oid in ri.hr_operator_ids_list]
        
        # recruited_id
        if hasattr(ri, 'recruited_id') and ri.recruited_id:
            ri.recruited_id = old_to_new_id.get(ri.recruited_id, ri.recruited_id)
        
        # === 发电区 ===
        # power_operator_ids_list
        if hasattr(ri, 'power_operator_ids_list'):
            ri.power_operator_ids_list = [old_to_new_id.get(oid, oid) for oid in ri.power_operator_ids_list]
        
        # main_power_facility_operator_ids (Dict[int, Set])
        if hasattr(ri, 'main_power_facility_operator_ids'):
            old_power_ops = ri.main_power_facility_operator_ids.copy()
            ri.main_power_facility_operator_ids = {}
            for key, old_set in old_power_ops.items():
                ri.main_power_facility_operator_ids[key] = {old_to_new_id.get(oid, oid) for oid in old_set}
        
        # === 工程维修区 ===
        # maintenance_place (Dict[str, int])
        if hasattr(ri, 'maintenance_place'):
            old_maint = ri.maintenance_place.copy()
            ri.maintenance_place = {}
            for key, old_id in old_maint.items():
                ri.maintenance_place[key] = old_to_new_id.get(old_id, old_id)
        
        # equipment_maintain_operator_ids (Dict[str, Set])
        if hasattr(ri, 'equipment_maintain_operator_ids'):
            old_eq_ops = ri.equipment_maintain_operator_ids.copy()
            ri.equipment_maintain_operator_ids = {}
            for key, old_set in old_eq_ops.items():
                ri.equipment_maintain_operator_ids[key] = {old_to_new_id.get(oid, oid) for oid in old_set}
        
        # === 厨房区 ===
        # milk_in_fridge (Dict[int, List]) - 角色id:奶数据
        if hasattr(ri, 'milk_in_fridge'):
            old_milk = ri.milk_in_fridge.copy()
            ri.milk_in_fridge = {}
            for old_id, value in old_milk.items():
                new_id = old_to_new_id.get(old_id, old_id)
                ri.milk_in_fridge[new_id] = value
        
        # === 医疗区 ===
        # medical_clinic_doctor_ids
        if hasattr(ri, 'medical_clinic_doctor_ids'):
            ri.medical_clinic_doctor_ids = [old_to_new_id.get(oid, oid) for oid in ri.medical_clinic_doctor_ids]
        
        # medical_hospital_doctor_ids
        if hasattr(ri, 'medical_hospital_doctor_ids'):
            ri.medical_hospital_doctor_ids = [old_to_new_id.get(oid, oid) for oid in ri.medical_hospital_doctor_ids]
        
        # === 图书档案区 ===
        # book_borrow_dict (Dict[int, int]) - 书籍id:借出人id
        if hasattr(ri, 'book_borrow_dict'):
            old_borrow = ri.book_borrow_dict.copy()
            ri.book_borrow_dict = {}
            for book_id, old_id in old_borrow.items():
                if old_id != -1:  # -1表示未借出
                    ri.book_borrow_dict[book_id] = old_to_new_id.get(old_id, old_id)
                else:
                    ri.book_borrow_dict[book_id] = old_id
        
        # === 贸易区 ===
        # trade_operator_ids_list
        if hasattr(ri, 'trade_operator_ids_list'):
            ri.trade_operator_ids_list = [old_to_new_id.get(oid, oid) for oid in ri.trade_operator_ids_list]
        
        # resource_type_main_trader (Dict[str, int])
        if hasattr(ri, 'resource_type_main_trader'):
            old_traders = ri.resource_type_main_trader.copy()
            ri.resource_type_main_trader = {}
            for key, old_id in old_traders.items():
                ri.resource_type_main_trader[key] = old_to_new_id.get(old_id, old_id)
        
        # === 制造加工区 ===
        # assembly_line (Dict[int, List]) - 流水线，List[1]是主生产工人id
        if hasattr(ri, 'assembly_line'):
            for line_id, line_data in ri.assembly_line.items():
                if len(line_data) > 1 and line_data[1] != 0:
                    line_data[1] = old_to_new_id.get(line_data[1], line_data[1])
        
        # production_worker_ids
        if hasattr(ri, 'production_worker_ids'):
            ri.production_worker_ids = [old_to_new_id.get(oid, oid) for oid in ri.production_worker_ids]
        
        # === 访客区 ===
        # visitor_info (Dict[int, datetime])
        if hasattr(ri, 'visitor_info'):
            old_visitors = ri.visitor_info.copy()
            ri.visitor_info = {}
            for old_id, value in old_visitors.items():
                new_id = old_to_new_id.get(old_id, old_id)
                ri.visitor_info[new_id] = value
        
        # invite_visitor (List[目标角色id, 招募进度, 招募效率])
        if hasattr(ri, 'invite_visitor') and ri.invite_visitor:
            ri.invite_visitor[0] = old_to_new_id.get(ri.invite_visitor[0], ri.invite_visitor[0])
        
        # diplomat_of_country (Dict[int, List]) - List[0]是外交官角色id
        if hasattr(ri, 'diplomat_of_country'):
            for country_id, data in ri.diplomat_of_country.items():
                if len(data) > 0 and data[0] != 0:
                    data[0] = old_to_new_id.get(data[0], data[0])
        
        # === 机库区 ===
        # ongoing_field_commissions (Dict[int, List]) - List[0]是干员id列表
        if hasattr(ri, 'ongoing_field_commissions'):
            for commission_id, data in ri.ongoing_field_commissions.items():
                if len(data) > 0 and isinstance(data[0], list):
                    data[0] = [old_to_new_id.get(oid, oid) for oid in data[0]]
        
        # === 疗养庭院 ===
        # herb_garden_line (Dict[int, List]) - List[1]是主种植员id
        if hasattr(ri, 'herb_garden_line'):
            for line_id, line_data in ri.herb_garden_line.items():
                if len(line_data) > 1 and line_data[1] != 0:
                    line_data[1] = old_to_new_id.get(line_data[1], line_data[1])
        
        # herb_garden_operator_ids
        if hasattr(ri, 'herb_garden_operator_ids'):
            ri.herb_garden_operator_ids = [old_to_new_id.get(oid, oid) for oid in ri.herb_garden_operator_ids]
        
        # green_house_line (Dict[int, List]) - List[1]是主种植员id
        if hasattr(ri, 'green_house_line'):
            for line_id, line_data in ri.green_house_line.items():
                if len(line_data) > 1 and line_data[1] != 0:
                    line_data[1] = old_to_new_id.get(line_data[1], line_data[1])
        
        # green_house_operator_ids
        if hasattr(ri, 'green_house_operator_ids'):
            ri.green_house_operator_ids = [old_to_new_id.get(oid, oid) for oid in ri.green_house_operator_ids]
        
        # === 关押区 ===
        # current_warden_id
        if hasattr(ri, 'current_warden_id') and ri.current_warden_id != 0:
            ri.current_warden_id = old_to_new_id.get(ri.current_warden_id, ri.current_warden_id)
        
        # current_prisoners (Dict[int, List])
        if hasattr(ri, 'current_prisoners'):
            old_prisoners = ri.current_prisoners.copy()
            ri.current_prisoners = {}
            for old_id, value in old_prisoners.items():
                new_id = old_to_new_id.get(old_id, old_id)
                ri.current_prisoners[new_id] = value
        
        # === 工程维修区 ===
        # maintenance_equipment_chara_id (Dict[int, int]) - 角色id:正在维护的装备所属角色id
        if hasattr(ri, 'maintenance_equipment_chara_id'):
            old_maint_eq = ri.maintenance_equipment_chara_id.copy()
            ri.maintenance_equipment_chara_id = {}
            for old_id, old_target in old_maint_eq.items():
                new_id = old_to_new_id.get(old_id, old_id)
                new_target = old_to_new_id.get(old_target, old_target)
                ri.maintenance_equipment_chara_id[new_id] = new_target
        
        # === 医疗区 ===
        # urine_in_fridge (Dict[int, int]) - 干员id:圣水存量
        if hasattr(ri, 'urine_in_fridge'):
            old_urine = ri.urine_in_fridge.copy()
            ri.urine_in_fridge = {}
            for old_id, value in old_urine.items():
                new_id = old_to_new_id.get(old_id, old_id)
                ri.urine_in_fridge[new_id] = value
        
        # today_physical_examination_chara_id_dict (Dict[int, set]) - 干员id:体检项目集合
        if hasattr(ri, 'today_physical_examination_chara_id_dict'):
            old_exam = ri.today_physical_examination_chara_id_dict.copy()
            ri.today_physical_examination_chara_id_dict = {}
            for old_id, value in old_exam.items():
                new_id = old_to_new_id.get(old_id, old_id)
                ri.today_physical_examination_chara_id_dict[new_id] = value
        
        # examined_operator_ids (Set[int])
        if hasattr(ri, 'examined_operator_ids'):
            ri.examined_operator_ids = {old_to_new_id.get(oid, oid) for oid in ri.examined_operator_ids}
        
        # waiting_for_exam_operator_ids (Set[int])
        if hasattr(ri, 'waiting_for_exam_operator_ids'):
            ri.waiting_for_exam_operator_ids = {old_to_new_id.get(oid, oid) for oid in ri.waiting_for_exam_operator_ids}
        
        # manually_selected_exam_operator_ids (Set[int])
        if hasattr(ri, 'manually_selected_exam_operator_ids'):
            ri.manually_selected_exam_operator_ids = {old_to_new_id.get(oid, oid) for oid in ri.manually_selected_exam_operator_ids}
        
        # medical_doctor_specializations (Dict[str, Dict[str, List[int]]]) - 医生id列表
        if hasattr(ri, 'medical_doctor_specializations'):
            for pos_key, system_dict in ri.medical_doctor_specializations.items():
                for sys_key, id_list in system_dict.items():
                    system_dict[sys_key] = [old_to_new_id.get(oid, oid) for oid in id_list]
    
    # 5.6 关系数据中的角色引用
    for char_id, character in new_character_data.items():
        if hasattr(character, 'relationship'):
            rel = character.relationship
            # father_id
            if hasattr(rel, 'father_id') and rel.father_id > 0:
                rel.father_id = old_to_new_id.get(rel.father_id, rel.father_id)
            # mother_id
            if hasattr(rel, 'mother_id') and rel.mother_id > 0:
                rel.mother_id = old_to_new_id.get(rel.mother_id, rel.mother_id)
            # child_id_list
            if hasattr(rel, 'child_id_list'):
                rel.child_id_list = [old_to_new_id.get(cid, cid) for cid in rel.child_id_list]
    
    # 5.7 场景数据中的角色列表
    if "scene_data" in loaded_dict:
        for scene_name, scene in loaded_dict["scene_data"].items():
            if hasattr(scene, 'character_list'):
                old_list = scene.character_list.copy()
                scene.character_list = set()
                for old_id in old_list:
                    scene.character_list.add(old_to_new_id.get(old_id, old_id))
    
    # 5.8 cache级别的角色ID引用
    # forbidden_npc_id
    if "forbidden_npc_id" in loaded_dict:
        old_forbidden = loaded_dict["forbidden_npc_id"].copy()
        loaded_dict["forbidden_npc_id"] = {old_to_new_id.get(oid, oid) for oid in old_forbidden}
    
    # old_character_id
    if "old_character_id" in loaded_dict and loaded_dict["old_character_id"] != 0:
        loaded_dict["old_character_id"] = old_to_new_id.get(
            loaded_dict["old_character_id"], 
            loaded_dict["old_character_id"]
        )
    
    return update_count
```

---

## 5. 执行步骤

### 阶段1：数据结构修改

1. 修改 `game_type.py` 中 `npc_tem_data` 的类型声明
2. 修改 `character_config.py` 中模板数据的存储方式
3. 修改 `character_handle.py` 中的初始化逻辑

### 阶段2：核心逻辑修改

1. 修改 `save_handle.py` 添加存档迁移逻辑
2. 修改 `clothing.py` 中的模板访问逻辑

### 阶段3：UI面板修改

1. 修改 `creator_character_flow.py` 中的ID列表生成
2. 修改 `recruit_panel.py` 中的遍历逻辑
3. 修改 `normal_panel.py` 中的遍历逻辑
4. 修改 `debug_panel.py` 中的遍历逻辑
5. 修改 `new_round.py` 中的多周目继承逻辑

### 阶段4：其他模块修改

1. 修改 `handle_premise_other.py` 中的前提判断
2. 修改 `attr_calculation.py` 中的属性计算

### 阶段5：测试与验证

1. 新建游戏测试
2. 旧存档读取测试
3. 角色招募测试
4. 多周目继承测试

---

## 6. 注意事项

### 6.1 玩家ID处理

- 玩家的ID始终保持为 **0**，不受此次重构影响
- 所有判断 `character_id == 0` 或 `cid == 0` 的逻辑无需修改

### 6.2 特殊角色处理

- 女儿等动态生成的角色（`Mother_id != 0` 或 `AdvNpc > 9000`）需要特殊处理
- 这些角色的adv通常是动态分配的，需要确保分配逻辑正确

### 6.3 ID遍历模式变更

**重要**：所有使用以下模式的代码都需要修改：

```python
# 旧模式（需要修改）
for i in range(len(cache.npc_tem_data)):
    chara_id = i + 1
    # ...

# 新模式
for adv_id in cache.npc_tem_data.keys():
    chara_id = adv_id
    # 或
for adv_id, tem_data in cache.npc_tem_data.items():
    # ...
```

### 6.4 直接使用cache.character_data的代码

大多数直接使用 `cache.character_data[character_id]` 的代码无需修改，只要传入的 `character_id` 已经是 `adv` 值即可。

---

## 7. 风险评估

### 7.1 高风险点

1. **存档迁移**：旧存档的数据结构复杂，需要全面处理所有引用角色ID的字段
2. **ID引用遗漏**：可能存在未被识别的ID引用位置

### 7.2 中风险点

1. **动态角色**：女儿等动态生成角色的ID分配逻辑
2. **第三方mod**：如果有mod使用了旧的ID访问方式

### 7.3 低风险点

1. **UI显示**：遍历方式的改变可能影响显示顺序

---

## 8. 回滚方案

如果重构出现严重问题：

1. 保留旧版代码分支
2. 存档迁移函数设计为可逆的
3. 添加存档版本标记，支持版本识别

---

## 9. 完整修改文件清单

| 文件路径 | 需修改行数(约) | 优先级 |
|---------|--------------|--------|
| Script/Core/game_type.py | 1 | P0 |
| Script/Config/character_config.py | 3 | P0 |
| Script/Design/character_handle.py | 15 | P0 |
| Script/Core/save_handle.py | 100+ | P0 |
| Script/Design/character.py | 10 | P0 |
| Script/Design/clothing.py | 4 | P1 |
| Script/UI/Flow/creator_character_flow.py | 20 | P1 |
| Script/UI/Panel/recruit_panel.py | 8 | P1 |
| Script/UI/Panel/normal_panel.py | 4 | P1 |
| Script/UI/Panel/debug_panel.py | 10 | P2 |
| Script/UI/Panel/new_round.py | 15 | P1 |
| Script/UI/Panel/sp_event_panel.py | 2 | P1 |
| Script/Design/handle_premise/handle_premise_other.py | 4 | P2 |
| Script/Design/attr_calculation.py | 10 | P2 |

### 9.1 额外需要修改的文件

#### Script/Design/character.py

**修改位置**：行224-237

`get_character_id_from_adv()` 函数可以大幅简化：

```python
# 修改前
def get_character_id_from_adv(adv_id: int) -> int:
    """
    通过剧情id获取角色id
    """
    for character_id in cache.character_data:
        if cache.character_data[character_id].adv == adv_id:
            return character_id
    return 0

# 修改后
def get_character_id_from_adv(adv_id: int) -> int:
    """
    通过剧情id获取角色id
    重构后character_id等于adv_id，直接判断是否存在即可
    """
    if adv_id in cache.character_data:
        return adv_id
    return 0
```

#### Script/UI/Panel/sp_event_panel.py

**修改位置**：行110

```python
# 修改前
child_character_data: game_type.Character = cache.character_data[len(cache.npc_tem_data)]

# 修改后
# 在born_new_character修改后，需要获取新角色的adv作为id
# 方案1：born_new_character返回新角色的id
new_child_id = character_handle.born_new_character(self.mother_character_id, new_name)
child_character_data: game_type.Character = cache.character_data[new_child_id]

# 方案2：或者通过模板数据获取（不推荐）
```

#### Script/Design/character_handle.py（born_new_character函数）

**修改位置**：行155-193

```python
# 修改前
def born_new_character(mother_id, child_name):
    """生成新的小孩模板数据"""
    # ...
    cache.npc_tem_data.append(now_tem)
    now_id = len(cache.npc_tem_data)
    cache.character_data[0].relationship.child_id_list.append(now_id)
    mom_character_data.relationship.child_id_list.append(now_id)
    init_character(now_id, cache.npc_tem_data[-1])
    # ...

# 修改后
def born_new_character(mother_id, child_name) -> int:
    """
    生成新的小孩模板数据
    Returns:
        int: 新角色的id（等于adv）
    """
    # ...
    now_id = now_tem.AdvNpc  # 使用adv作为id
    cache.npc_tem_data[now_id] = now_tem
    cache.character_data[0].relationship.child_id_list.append(now_id)
    mom_character_data.relationship.child_id_list.append(now_id)
    init_character(now_id, cache.npc_tem_data[now_id])
    # ...
    return now_id  # 返回新角色id
```

#### Script/Design/attr_calculation.py

**修改位置**：行32-34, 行202, 行432-433

```python
# 修改前（行202）
for i in range(len(cache.npc_tem_data) + 1):
    # ...

# 修改后
for adv_id in [0] + list(cache.npc_tem_data.keys()):  # 0是玩家，然后是所有NPC
    # ...
```

---

## 10. 附录：搜索关键词

以下正则表达式可用于搜索需要修改的代码位置：

```regex
# 顺序ID生成模式
range\(len\(cache\.(character_data|npc_tem_data)\)\)
\[i \+ 1 for i in range\(len\(cache\.npc_tem_data\)\)\]
chara_id = i \+ 1
character_id = i \+ 1

# cid - 1 模式
\.cid - 1
character_id - 1
npc_tem_data\[.*- 1\]

# 直接用数字索引访问npc_tem_data
npc_tem_data\[\d+\]
npc_tem_data\[i\]
```

---

*文档版本: 1.3*
*创建日期: 2026-02-27*
*最后更新: 2026-02-27*
*适用于: erArk 角色ID系统重构*

---

## 11. 重构执行进度

### 11.1 完成状态表

| 文件 | 状态 | 完成日期 | 备注 |
|-----|------|---------|-----|
| Script/Core/game_type.py | ✅ 已完成 | 2026-02-27 | `npc_tem_data` 类型改为 `Dict[int, NpcTem]` |
| Script/Config/character_config.py | ✅ 已完成 | 2026-02-27 | `character_tem_list` 改为 `character_tem_dict`，存储方式改为Dict |
| Script/Design/character_handle.py | ✅ 已完成 | 2026-02-27 | `init_character_list()`, `init_character_tem()`, `born_new_character()` 已修改，`born_new_character()` 现在返回新角色ID |
| Script/Core/save_handle.py | ✅ 已完成 | 2026-02-27 | 添加 `migrate_npc_tem_data_to_dict()`, `migrate_character_id_to_adv()`, `fix_missing_character_template()` 迁移/修复函数，修改 `update_tem_character()` 和 `update_new_character()` |
| Script/Design/clothing.py | ✅ 已完成 | 2026-02-27 | 模板访问改为 `.get()` 方式，添加空值检查 |
| Script/Design/character.py | ✅ 已完成 | 2026-02-27 | `get_character_id_from_adv()` 简化为直接判断 |
| Script/UI/Flow/creator_character_flow.py | ✅ 已完成 | 2026-02-27 | ID列表改为 `list(cache.npc_tem_data.keys())` |
| Script/UI/Panel/recruit_panel.py | ✅ 已完成 | 2026-02-27 | 遍历改为 `.items()` 方式 |
| Script/UI/Panel/normal_panel.py | ✅ 已完成 | 2026-02-27 | 遍历改为 `.keys()` 方式 |
| Script/UI/Panel/debug_panel.py | ✅ 已完成 | 2026-02-27 | ID列表和遍历改为Dict方式 |
| Script/UI/Panel/new_round.py | ✅ 已完成 | 2026-02-27 | 多周目继承逻辑修改为Dict方式 |
| Script/UI/Panel/sp_event_panel.py | ✅ 已完成 | 2026-02-27 | 使用 `born_new_character()` 返回值获取新角色ID |
| Script/Design/handle_premise/handle_premise_other.py | ✅ 已完成 | 2026-02-27 | 婴儿存在检查改为 `.keys()` 遍历 |
| Script/Design/attr_calculation.py | ✅ 已完成 | 2026-02-27 | 所有遍历改为Dict方式 |

### 11.2 待测试项

- [ ] 新建游戏功能
- [ ] 旧存档读取与迁移
- [ ] 角色招募功能
- [ ] 女儿出生功能
- [ ] 多周目继承功能
- [ ] 缺失模板角色修复（模拟角色模板被删除或adv变更的场景）

## 附录A：完整需要迁移的角色ID字段清单

### A.1 Character 类字段
| 字段路径 | 类型 | 说明 |
|---------|------|------|
| `cid` | int | 主ID，需要改为等于adv |
| `target_character_id` | int | 目标角色ID |
| `assistant_character_id` | int | 助理角色ID |
| `ask_group_sex_refuse_chara_id_list` | List[int] | 拒绝群P的角色ID列表 |
| `state_active.bagging_chara_id` | int | 正在装袋的角色ID |
| `sp_flag.carry_chara_id_in_time_stop` | int | 时停搬运角色ID |
| `sp_flag.free_in_time_stop_chara_id` | int | 时停自由活动角色ID |
| `interacting_character_end_info[0]` | int | 交互对方角色ID |
| `favorability` | Dict[int, int] | 好感度字典 |
| `relationship.father_id` | int | 父亲ID |
| `relationship.mother_id` | int | 母亲ID |
| `relationship.child_id_list` | List[int] | 子女ID列表 |

### A.2 Rhodes_Island 类字段
| 字段路径 | 类型 | 说明 |
|---------|------|------|
| `hr_operator_ids_list` | List[int] | 人事干员ID列表 |
| `recruited_id` | int | 已招募ID |
| `power_operator_ids_list` | List[int] | 发电干员ID列表 |
| `main_power_facility_operator_ids` | Dict[int, Set[int]] | 发电设施干员ID |
| `maintenance_place` | Dict[str, int] | 维修位置干员ID |
| `equipment_maintain_operator_ids` | Dict[str, Set[int]] | 装备维护干员ID |
| `maintenance_equipment_chara_id` | Dict[int, int] | 维护装备角色ID映射 |
| `milk_in_fridge` | Dict[int, int] | 冰箱母乳-干员ID |
| `medical_clinic_doctor_ids` | List[int] | 诊所医生ID列表 |
| `medical_hospital_doctor_ids` | List[int] | 医院医生ID列表 |
| `book_borrow_dict` | Dict[int, int] | 书籍借出人ID |
| `trade_operator_ids_list` | List[int] | 贸易干员ID列表 |
| `resource_type_main_trader` | Dict[str, int] | 资源主交易员ID |
| `assembly_line[x][1]` | int | 流水线主工人ID |
| `production_worker_ids` | List[int] | 生产工人ID列表 |
| `visitor_info` | Dict[int, datetime] | 访客ID信息 |
| `invite_visitor[0]` | int | 邀请目标ID |
| `diplomat_of_country[x][0]` | int | 外交官ID |
| `ongoing_field_commissions[x][0]` | List[int] | 外勤干员ID列表 |
| `herb_garden_line[x][1]` | int | 药田种植员ID |
| `herb_garden_operator_ids` | List[int] | 药田干员ID列表 |
| `green_house_line[x][1]` | int | 温室种植员ID |
| `green_house_operator_ids` | List[int] | 温室干员ID列表 |
| `current_warden_id` | int | 监狱长ID |
| `current_prisoners` | Dict[int, List] | 囚犯ID字典 |
| `urine_in_fridge` | Dict[int, int] | 圣水-干员ID |
| `today_physical_examination_chara_id_dict` | Dict[int, set] | 今日体检干员ID |
| `examined_operator_ids` | Set[int] | 已体检干员ID集合 |
| `waiting_for_exam_operator_ids` | Set[int] | 等待体检干员ID集合 |
| `manually_selected_exam_operator_ids` | Set[int] | 手动选择体检干员ID |
| `medical_doctor_specializations` | Dict | 医生分科ID列表 |

### A.3 Cache 类字段
| 字段路径 | 类型 | 说明 |
|---------|------|------|
| `character_data` | Dict[int, Character] | 角色数据字典（键需要改为adv） |
| `npc_tem_data` | List → Dict | 模板数据（需要改为Dict[int, NpcTem]） |
| `npc_id_got` | Set[int] | 已获得NPC ID集合 |
| `forbidden_npc_id` | Set[int] | 禁止NPC ID集合 |
| `old_character_id` | int | 场景查看角色ID |

### A.4 其他数据
| 数据位置 | 类型 | 说明 |
|---------|------|------|
| `scene_data[x].character_list` | Set[int] | 场景角色列表 |
| `pl_collection.token_list` | Dict[int, ...] | 信物-角色ID |
| `pl_collection.first_panties` | Dict[int, ...] | 初次内裤-角色ID |
| `pl_collection.npc_panties` | Dict[int, ...] | NPC内裤-角色ID |
| `pl_collection.npc_socks` | Dict[int, ...] | NPC袜子-角色ID |
