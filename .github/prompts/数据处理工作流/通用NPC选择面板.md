# 通用NPC选择面板说明

## 概述
通用NPC选择面板（common_select_NPC）是erArk游戏中用于角色选择和筛选的核心UI组件。该系统提供了统一的接口，支持多种筛选条件，被游戏中多个功能模块广泛使用。

## 系统架构

### 核心文件
- **主要实现**: `Script/UI/Panel/common_select_NPC.py`
- **依赖组件**: 
  - `Script/UI/Moudle/draw.py` - 绘制系统
  - `Script/UI/Moudle/panel.py` - 面板系统
  - `Script/Design/handle_premise.py` - 前提条件处理
  - `Script/Core/cache_control.py` - 缓存控制
  - `Script/Config/game_config.py` - 游戏配置

### 使用该系统的模块
1. **助理面板** (`assistant_panel.py`) - 选择助理角色
2. **外勤委托面板** (`field_commission_panel.py`) - 分配外勤任务
3. **群交面板** (`group_sex_panel.py`) - 群交场景
4. **图书馆管理** (`manage_library.py`) - 图书馆操作
5. **体检管理面板** (`physical_check_and_manage.py`) - 体检和管理功能

## 核心功能

### 1. 主要函数

#### `common_select_npc_button_list_func()`
通用NPC选择按钮列表函数，是整个系统的核心入口点。

**参数说明:**
- `now_draw_panel`: 当前绘制面板对象
- `title_text`: 面板标题文本
- `info_text`: 信息提示文本
- `select_state`: 筛选状态字典

**返回值:**
- `return_list`: 主要按钮列表（包含返回按钮）
- `other_return_list`: 其他功能按钮列表（翻页、筛选等）
- `select_state`: 更新后的筛选状态

#### `select_type_change()`
处理筛选类型切换的函数，负责用户交互和参数收集。

#### `CommonSelectNPCButtonList`
角色按钮的UI组件类，负责单个角色的显示和交互。

### 2. 筛选功能

系统提供9种筛选方式：

| 筛选类型 | 名称 | 功能描述 | 实现方式 |
|---------|------|----------|----------|
| 0 | 不筛选 | 显示所有角色 | 直接显示原始列表 |
| 1 | 筛选收藏干员 | 显示被收藏的角色 | 检查`character_data.chara_setting[2] == 1` |
| 2 | 筛选访客干员 | 显示访客角色 | 检查`npc_id in cache.rhodes_island.visitor_info` |
| 3 | 筛选未陷落干员 | 显示未陷落的角色 | 使用`handle_premise.handle_self_not_fall()` |
| 4 | 筛选已陷落干员 | 显示已陷落的角色 | 使用`handle_premise.handle_self_fall()` |
| 5 | 按名称筛选 | 根据名称关键词筛选 | 字符串包含匹配 |
| 6 | 筛选同区块干员 | 显示同区域的角色 | 使用`handle_premise.handle_in_player_zone()` |
| 7 | 筛选无意识干员 | 显示意识清醒的角色 | 使用`handle_premise.handle_unconscious_flag_0()` |
| 8 | 按能力等级筛选 | 根据能力等级筛选 | 检查`character_data.ability[cid] >= threshold` |

### 3. 筛选状态管理

筛选状态通过字典管理：
```python
select_state = {
    "type": 0,        # 筛选类型（0-8）
    "name": "",       # 名称筛选关键词
    "obj_cid": 0,     # 能力ID（用于能力筛选）
    "obj_value": 0    # 能力阈值（用于能力筛选）
}
```

## 数据结构关系

### 1. 角色数据结构

#### 基础信息（来源：`data/character/*.csv`）
- **AdvNpc**: 干员编号
- **Name**: 角色姓名
- **Sex**: 性别（0=男，1=女）
- **Profession**: 职业ID
- **Race**: 种族ID  
- **Nation**: 国家/势力ID
- **TextColor**: 角色专属颜色

#### 角色设置（来源：`data/csv/CharaSetting.csv`）
- **设置ID 2**: 收藏状态（0=否，1=是）
- 用于收藏筛选功能

#### 能力系统（来源：`data/csv/Ability.csv`）
能力分为6大类：
- **类型0**: 感度（皮肤感度、胸部感度等）
- **类型1**: 扩张（阴道扩张、肛肠扩张等）
- **类型2**: 刻印（快乐刻印、屈服刻印等）
- **类型3**: 基础（技巧、顺从、亲密等）
- **类型4**: 技能（话术、指挥、战斗等技能）
- **类型5**: 性技（指技、舌技、足技等）

#### 天赋系统（来源：`data/csv/Talent.csv`）
特殊的陷落状态天赋：
- **201-204**: 情感依赖（思慕、恋慕、恋人、爱侣）
- **211-214**: 支配关系（屈从、驯服、宠物、奴隶）

### 2. 前提条件系统

#### 陷落状态检测
```python
# 检测已陷落：拥有任意情感依赖或支配关系天赋
def handle_self_fall(character_id: int) -> int:
    for talent_id in {201, 202, 203, 204, 211, 212, 213, 214}:
        if character_data.talent[talent_id]:
            return 1
    return 0
```

#### 区域检测
```python
# 检测同区域：主要位置坐标相同
def handle_in_player_zone(character_id: int) -> int:
    return character_data.position[0] == player_position[0]
```

#### 意识状态检测
```python
# 检测意识状态：无意识状态标志
def handle_unconscious_flag_0(character_id: int) -> int:
    return character_data.sp_flag.unconscious_h == 0
```

意识状态类型：
- **0**: 正常意识（清醒）
- **1**: 睡眠状态
- **2**: 醉酒状态
- **3**: 时停状态
- **4**: 平然状态
- **5**: 空气状态
- **6**: 身体控制
- **7**: 心理控制

## 使用流程

### 1. 典型调用流程
```python
# 1. 创建面板数据
panel_data = [
    [character_id, callback_func, selected_list],  # 角色信息
    # ... 更多角色
]

# 2. 创建面板对象
select_panel = SomeSelectPanel(panel_data)

# 3. 调用通用选择函数
return_list, other_list, state = common_select_npc_button_list_func(
    select_panel, 
    title="选择角色", 
    info="请选择要操作的角色",
    select_state={}
)

# 4. 处理用户选择
user_choice = flow_handle.askfor_all(return_list)
```

### 2. 筛选交互流程
1. **显示筛选选项**: 9种筛选方式的按钮列表
2. **用户选择筛选类型**: 点击对应筛选按钮
3. **收集筛选参数**: 
   - 名称筛选：弹出输入框收集关键词
   - 能力筛选：显示能力列表→收集能力ID→输入等级阈值
4. **应用筛选条件**: 遍历角色列表，应用筛选逻辑
5. **更新显示**: 重新绘制过滤后的角色列表

### 3. 状态持久化
- 筛选状态在会话期间保持
- 支持筛选条件的动态切换
- 分页浏览时保持筛选状态

## 技术实现细节

### 1. 绘制系统集成
- 使用`draw.LeftButton`创建角色按钮
- 支持角色专属颜色显示
- 已选择角色使用金色高亮样式
- 分页显示支持大量角色

### 2. 回调函数机制
```python
# 角色按钮创建
name_draw = draw.LeftButton(
    button_text, 
    character_data.name, 
    width,
    normal_style=draw_style,
    cmd_func=callback_function,  # 点击回调
    args=(character_id,)         # 回调参数
)
```

### 3. 状态管理
- 局部状态字典避免全局变量污染
- 内部回调函数更新状态
- 状态通过返回值传递给调用方

### 4. 性能优化
- 筛选条件预检查，减少不必要计算
- 分页显示，避免一次性渲染过多元素
- 缓存角色数据，避免重复查询

## 扩展性设计

### 1. 新增筛选类型
在`common_select_npc_button_list_func()`中添加新的筛选逻辑：
```python
elif select_state["type"] == 9:  # 新筛选类型
    if not custom_filter_condition(npc_id):
        continue
```

### 2. 自定义前提条件
在`handle_premise.py`中实现新的前提条件函数，并在筛选逻辑中调用。

### 3. 复合筛选支持
当前为单一筛选条件，可扩展为多条件组合筛选。

## 注意事项

### 1. 性能考虑
- 大量角色时筛选可能较慢
- 复杂前提条件检查会影响响应速度
- 建议在必要时添加筛选结果缓存

### 2. 用户体验
- 筛选结果为空时需要友好提示
- 筛选条件重置机制
- 筛选历史记录功能

### 3. 数据一致性
- 角色数据变化时需要刷新筛选结果
- 前提条件的实时性保证
- 筛选状态与游戏状态同步

## 相关配置文件

### CSV数据文件
- `data/character/*.csv` - 角色基础数据
- `data/csv/Ability.csv` - 能力定义
- `data/csv/Talent.csv` - 天赋定义
- `data/csv/CharaSetting.csv` - 角色设置
- `data/csv/Race.csv` - 种族定义
- `data/csv/Profession.csv` - 职业定义
- `data/csv/Nation.csv` - 国家/势力定义

### 编译后数据
- `data/Character.json` - 编译后的角色数据
- `data/data.json` - 游戏主配置数据

### 构建流程
1. `python buildconfig.py` - 编译CSV到JSON
2. 游戏启动时加载JSON数据到内存缓存
3. UI系统从缓存读取数据进行显示和筛选

## 总结

通用NPC选择系统是erArk游戏中一个设计精良的可复用组件，它：

1. **统一接口**: 为多个功能模块提供一致的角色选择体验
2. **丰富筛选**: 支持9种不同的筛选方式，满足各种使用场景
3. **灵活扩展**: 良好的架构设计支持功能扩展和定制
4. **性能优化**: 合理的数据结构和算法确保流畅的用户体验
5. **数据驱动**: 基于CSV配置的数据驱动设计，便于维护和修改

该系统体现了游戏开发中组件化、模块化设计的优秀实践，为复杂的角色管理功能提供了坚实的技术基础。