# constant_effect.py 和 default.py 的关系说明

## 概述

`constant_effect.py` 和 `default.py` 通过装饰器模式实现了行为效果的定义与实现分离。`constant_effect.py` 定义效果常量，`default.py` 实现具体效果函数。

## 核心机制

### 1. 常量定义（constant_effect.py）

```python
class BehaviorEffect:
    """行为结算效果函数"""
    
    NOTHING = 9999
    """ 系统量_基础 什么都没有的空结算 """
    
    ADD_SMALL_HIT_POINT = 0
    """ 属性_基础 增加少量体力 """
```

常量按数值范围分类：
- **9999**: 系统效果
- **10000-10999**: 系统交互和标志位
- **0-99**: 基础属性（体力、气力、好感度等）
- **100-199**: 状态调整和技能计算
- **200-299**: 经验值
- **300-399**: 特殊标志
- **400-499**: 结构体重置
- **500-599**: 专用指令结算
- **600-699**: 服装效果
- **700-799**: 时间和地点
- **800-899**: H模式位置
- **900-999**: 道具增减
- **1000-1099**: 道具使用效果
- **1100-1199**: 初次事件
- **1200-1299**: 源石技艺
- **1400-1499**: H模式属性
- **1500-1599**: 基础属性扩展
- **1600-1699**: 体检属性
- **1700-1799**: 行动
- **1750-1799**: 设施

### 2. 函数实现（default.py）

使用装饰器注册效果函数：

```python
@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_SMALL_HIT_POINT)
def handle_add_small_hit_point(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    增加少量体力
    """
    # 实现代码
```

### 3. 命名规范

常量名到函数名的转换规则：

1. **基本转换**：UPPER_SNAKE_CASE → handle_lower_snake_case
   - `NOTHING` → `handle_nothing`
   - `ADD_SMALL_HIT_POINT` → `handle_add_small_hit_point`

2. **特殊替换**：
   - `DOWN_` → `handle_sub_` （减少）
   - `TARGET_` 通常保留在函数名中

3. **示例**：
   - `DOWN_BOTH_SMALL_HIT_POINT` → `handle_sub_both_small_hit_point`
   - `TARGET_ADD_SMALL_N_FEEL` → `handle_target_add_small_n_feel`
   - `TALK_ADD_ADJUST` → `handle_talk_add_adjust`

### 4. 函数签名

所有效果函数必须使用统一的签名：

```python
def handle_xxx(
    character_id: int,          # 角色ID
    add_time: int,             # 增加的时间
    change_data: game_type.CharacterStatusChange,  # 状态变化记录
    now_time: datetime.datetime,  # 当前时间
):
```

## 添加新效果的步骤

### 1. 在 constant_effect.py 中定义常量

```python
class BehaviorEffect:
    # 选择合适的数值范围
    MY_NEW_EFFECT = 123
    """ 分类_子类 效果描述 """
```

### 2. 在 default.py 中实现函数

```python
@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.MY_NEW_EFFECT)
def handle_my_new_effect(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    效果描述
    Keyword arguments:
    character_id -- 角色id
    add_time -- 增加时间
    change_data -- 状态变化数据
    now_time -- 结算时间
    """
    # 1. 获取角色数据
    character_data = cache.character_data[character_id]
    
    # 2. 执行效果逻辑
    # ...
    
    # 3. 记录变化（如需要）
    # change_data.xxx = value
```

## 常见效果模式

### 1. 基础属性修改

```python
@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_SMALL_HIT_POINT)
def handle_add_small_hit_point(...):
    character_data = cache.character_data[character_id]
    add_hit_point = add_time * 15
    character_data.hit_point = min(
        character_data.hit_point_max, 
        character_data.hit_point + add_hit_point
    )
```

### 2. 交互对象效果

```python
@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_SMALL_N_FEEL)
def handle_target_add_small_n_feel(...):
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    # 对 target_data 进行操作
```

### 3. 专用结算（复杂逻辑）

```python
@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TALK_ADD_ADJUST)
def handle_talk_add_adjust(...):
    # 复杂的技能计算、好感度调整等
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    
    # 技能影响计算
    adjust = attr_calculation.get_ability_adjust(character_data.ability[40])
    
    # 应用效果
    target_data.favorability[character_id] += adjust
    # ...
```

### 4. 标志位切换

```python
@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.H_FLAG_TO_1)
def handle_h_flag_to_1(...):
    character_data = cache.character_data[character_id]
    character_data.sp_flag.is_h = True
```

## 注意事项

1. **效果函数必须使用装饰器注册**，否则无法被系统调用
2. **保持命名一致性**，便于维护和查找
3. **选择正确的数值范围**，保持分类清晰
4. **记录必要的变化**到 `change_data`，用于UI显示
5. **处理边界情况**，如目标不存在、数值溢出等
6. **添加中文注释**，说明效果的具体作用

## 调试提示

如果新增的效果没有生效，检查：
1. 常量是否正确定义在 `BehaviorEffect` 类中
2. 函数是否使用了正确的装饰器
3. 装饰器参数是否正确（常量名）
4. 函数签名是否符合规范
5. 在使用效果的地方是否正确引用了常量

## 相关文件

- `Script/Core/constant_effect.py` - 效果常量定义
- `Script/Settle/default.py` - 主要效果实现
- `Script/Settle/Second_effect.py` - 二段效果实现
- `Script/Design/settle_behavior.py` - 效果注册和调用机制