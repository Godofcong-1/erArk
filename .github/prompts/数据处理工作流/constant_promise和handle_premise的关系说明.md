# constant_promise.py 和 handle_premise.py 的关系说明

## 概述

前提系统（Premise System）是游戏中用于判断条件是否满足的核心机制。`constant_promise.py` 定义前提常量，`handle_premise.py` 及相关文件实现具体的前提判断函数。

## 核心机制

### 1. 前提常量定义（constant_promise.py）

```python
class Premise:
    """前提id"""
    
    # 系统状态类
    DEBUG_MODE_ON = "debug_mode_on"
    """ 系统状态 现在是debug模式 """
    
    # 指令触发类
    IS_PLAYER = "sys_0"
    """ 指令_触发与交互 玩家触发的该指令 """
    
    # 地点类
    IN_PLAYER_SCENE = "place_0"
    """ 地点_角色位置 自己与玩家处于相同场景 """
```

前提按类型分类：
- **系统状态**：游戏模式、面板显示等
- **指令触发与交互**：角色类型、交互对象等
- **权重类**：`HIGH_1`~`HIGH_999` 表示不同权重值
- **最后指令类**：`LAST_CMD_` 开头，记录上次执行的指令
- **地点类**：位置、场景、设施等
- **时间类**：时段、季节、日期等
- **角色状态类**：HP、能力、特殊状态等

### 2. 前提函数实现

前提函数分布在多个文件中：
- `handle_premise.py` - 主文件，包含通用前提
- `handle_premise_place.py` - 地点相关前提
- `handle_premise_sp_flag.py` - 特殊标志相关前提

使用装饰器注册：

```python
@add_premise(constant_promise.Premise.IN_PLAYER_SCENE)
def handle_in_player_scene(character_id: int) -> int:
    """
    校验角色是否与玩家在同一场景
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重 (0=不满足, >0=满足)
    """
    # 实现逻辑
```

### 3. 命名规范

常量名到函数名的转换规则：

1. **基本转换**：UPPER_SNAKE_CASE → handle_lower_snake_case
   - `IS_PLAYER` → `handle_is_player`
   - `IN_PLAYER_SCENE` → `handle_in_player_scene`

2. **示例**：
   - `DEBUG_MODE_ON` → `handle_debug_mode_on`
   - `TARGET_IS_PLAYER` → `handle_target_is_player`
   - `LAST_CMD_MAKING_OUT` → `handle_last_cmd_making_out`

### 4. 前提ID命名规范

- 系统类：直接使用描述性名称，如 `"debug_mode_on"`
- 带分类前缀：
  - `sys_X` - 系统/指令相关
  - `sex_X` - 性别相关
  - `place_X` - 地点相关
  - `tired_X` - 疲劳相关
  - `hp_X` - 体力相关

## 前提类型

### 1. 简单布尔前提

返回 0（不满足）或 1（满足）：

```python
@add_premise(constant_promise.Premise.IS_PLAYER)
def handle_is_player(character_id: int) -> int:
    """校验是否为玩家"""
    return 1 if character_id == 0 else 0
```

### 2. 权重前提

返回不同权重值，影响AI决策：

```python
@add_premise(constant_promise.Premise.HP_1)
def handle_hp_1(character_id: int) -> int:
    """校验角色疲劳"""
    character_data = cache.character_data[character_id]
    if character_data.sp_flag.tired == 1:
        return 999  # 高权重
    else:
        return 0
```

### 3. 反向前提

使用 `not` 实现相反条件：

```python
@add_premise(constant_promise.Premise.NOT_IN_PLAYER_SCENE)
def handle_not_in_player_scene(character_id: int) -> int:
    """校验角色不在玩家场景"""
    return not handle_in_player_scene(character_id)
```

### 4. 综合值前提（CVP）

处理复杂的多值条件：

```python
# 格式：CVP_类型_值1_值2_值3
# 例如：CVP_favorability_ge_3
# 由 handle_comprehensive_value_premise() 特殊处理
```

## 添加新前提的步骤

### 1. 在 constant_promise.py 中定义常量

```python
class Premise:
    # 选择合适的分类和命名
    MY_NEW_PREMISE = "my_new_premise"
    """ 分类说明 具体描述 """
```

### 2. 在对应的 handle_premise 文件中实现函数

```python
@add_premise(constant_promise.Premise.MY_NEW_PREMISE)
def handle_my_new_premise(character_id: int) -> int:
    """
    前提描述
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    
    # 判断逻辑
    if 满足条件:
        return 1  # 或其他权重值
    return 0
```

### 3. 选择正确的文件

- 通用前提 → `handle_premise.py`
- 地点相关 → `handle_premise_place.py`
- 特殊标志相关 → `handle_premise_sp_flag.py`
- 新类别 → 创建新的 `handle_premise_xxx.py` 并在主文件中导入

## 常用模式

### 1. 通用判断函数

对于相似的判断逻辑，可以创建通用函数：

```python
def common_place_judge_by_SceneName(character_id: int, scene_name: str, judge_in_flag: bool = True) -> bool:
    """
    通用的地点判断函数
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    
    if judge_in_flag:
        return scene_name in now_scene_data.scene_name
    else:
        return scene_name not in now_scene_data.scene_name
```

### 2. 组合前提

在使用时可以组合多个前提：

```python
# 在指令或事件配置中
premise_list = [
    constant_promise.Premise.IS_PLAYER,
    constant_promise.Premise.HAVE_TARGET,
    constant_promise.Premise.IN_PLAYER_SCENE
]
```

### 3. 特殊处理

某些前提需要特殊处理，如：

```python
# 无意识模式判定
if unconscious_pass_flag == False and handle_unconscious_flag_ge_1(target_character_id):
    # 特殊处理逻辑
```

## 使用场景

前提系统用于：
1. **指令可用性判断** - 决定玩家/NPC可以执行哪些指令
2. **事件触发条件** - 判断事件是否应该触发
3. **AI决策权重** - 影响NPC的行为选择
4. **对话选择** - 决定显示哪些对话选项

## 调试提示

1. **前提不生效**：
   - 检查常量是否正确定义
   - 确认函数使用了正确的装饰器
   - 验证函数名符合命名规范

2. **权重问题**：
   - 使用 debug 模式查看前提计算结果
   - 注意权重值的选择（1, 5, 10, 50, 100, 999等）

3. **性能考虑**：
   - 频繁调用的前提应该优化性能
   - 可以缓存计算结果避免重复计算

## 注意事项

1. **返回值必须是整数**，0表示不满足，正数表示满足（同时作为权重）
2. **保持命名一致性**，便于查找和维护
3. **添加详细注释**，说明前提的判断逻辑
4. **考虑边界情况**，如角色不存在、数据未初始化等
5. **合理使用权重**，影响AI决策的平衡性

## 相关文件

- `Script/Core/constant_promise.py` - 前提常量定义
- `Script/Design/handle_premise.py` - 主前提处理文件
- `Script/Design/handle_premise_place.py` - 地点前提
- `Script/Design/handle_premise_sp_flag.py` - 特殊标志前提
- `Script/Core/constant.py` - 存储前提处理函数的字典