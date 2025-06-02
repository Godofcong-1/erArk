# CSV数据加载机制说明

本文档详细说明了erArk项目中CSV文件如何被定义、处理并加载到缓存数据库中的完整流程。

## 概述

游戏使用CSV文件作为基础配置数据源，通过构建脚本转换为JSON文件和Python配置类，最终在游戏运行时加载到内存中。

## 数据流程

```
CSV文件 → buildconfig.py → JSON文件 + config_def.py → game_config.py → 内存缓存
```

## CSV文件格式

每个CSV文件都遵循固定的格式：

```csv
第1行: 字段名（英文标识符）
第2行: 字段说明（中文描述）  
第3行: 字段类型（int/str/bool/float）
第4行: 是否需要国际化（0/1）
第5行: 类的说明文档
第6行开始: 实际数据
```

示例（Ability.csv）：
```csv
cid,ability_type,name
能力id,"类型(0:感度,1:扩张,2:刻印,3:基础,4:技能,5:性技)",名字
int,int,str
0,0,1
能力对应类型和文字描述,,
0,0,皮肤感度
1,0,胸部感度
```

## 构建过程（buildconfig.py）

### 1. 读取CSV文件

`build_csv_config()` 函数处理CSV文件：

- 读取前5行作为元数据
- 第1行：字段名，作为字典的键
- 第2行：字段说明，用于生成Python类的文档字符串
- 第3行：字段类型，用于数据类型转换
- 第4行：国际化标记，决定是否提取到PO文件
- 第5行：类说明，作为Python类的文档字符串

### 2. 数据类型转换

根据第3行定义的类型进行转换：
- `int`: 转换为整数
- `str`: 转换为字符串（转义引号）
- `bool`: 转换为整数（0/1）
- `float`: 转换为浮点数

### 3. 生成JSON文件

处理后的数据存储到不同的JSON文件中：

- **data.json**: 通用配置数据（来自data/csv/）
- **Character.json**: 角色数据（来自data/character/）
- **Character_Talk.json**: 角色对话数据（来自data/talk/）
- **Character_Event.json**: 角色事件数据（来自data/event/）
- **Talk_Common.json**: 通用对话组件（来自data/talk_common/）
- **ui_text.json**: UI文本数据（来自data/ui_text/）

JSON结构示例：
```json
{
    "Ability": {
        "data": [
            {"cid": 0, "ability_type": 0, "name": "皮肤感度"},
            {"cid": 1, "ability_type": 0, "name": "胸部感度"}
        ],
        "gettext": {"cid": 0, "ability_type": 0, "name": 1}
    }
}
```

### 4. 生成Python配置类（config_def.py）

`build_config_def()` 函数自动生成Python数据类：

```python
class Ability:
    """ 能力对应类型和文字描述 """
    
    cid: int
    """ 能力id """
    ability_type: int
    """ 类型(0:感度,1:扩张,2:刻印,3:基础,4:技能,5:性技) """
    name: str
    """ 名字 """
```

## 加载过程（game_config.py）

### 1. 定义全局变量

为每种配置定义对应的字典变量：

```python
config_ability: Dict[int, config_def.Ability] = {}
""" 能力类型表 """

config_ability_type_data: Dict[int, Set] = {}
"""
类型对应能力列表配置数据
类型 0:感觉,1:扩张,2:刻印,3:基础
"""
```

### 2. 加载JSON数据

`load_data_json()` 函数加载所有JSON文件：

```python
config_data = json_handle.load_json(data_path)
character_data = json_handle.load_json(character_path)
ui_text_data = json_handle.load_json(ui_text_path)
```

### 3. 解析并存储数据

每种配置都有对应的加载函数，例如 `load_ability_type_data()`：

```python
def load_ability_type_data():
    """载入能力类型配置数据"""
    now_data = config_data["Ability"]
    translate_data(now_data)  # 处理国际化
    for tem_data in now_data["data"]:
        now_tem = config_def.Ability()
        now_tem.__dict__ = tem_data
        config_ability[now_tem.cid] = now_tem
        # 构建类型索引
        config_ability_type_data.setdefault(now_tem.ability_type, set())
        config_ability_type_data[now_tem.ability_type].add(now_tem.cid)
```

### 4. 数据处理特点

- **主键索引**: 大多数配置以`cid`作为主键存储
- **类型分组**: 许多配置会额外构建类型分组索引
- **关系映射**: 处理配置间的关联关系
- **特殊解析**: 某些字段需要特殊解析（如用分隔符的多值字段）

## 特殊处理

### 1. 口上系统（Talk）

- 文件名前缀作为ID的一部分，避免冲突
- 支持角色特定的口上（adv_id）
- 前提条件支持多条件（用&分隔）

### 2. 事件系统（Event）

- 从JSON文件直接加载，不经过CSV
- 支持行为ID和角色ID的双重索引

### 3. 目标系统（Target）

- 使用目录名作为ID前缀
- 支持前提条件和效果的关联

### 4. 国际化支持

- 第4行标记为1的字段会提取到PO文件
- 支持gettext机制进行翻译

## 数据访问

游戏运行时通过game_config模块访问配置：

```python
from Script.Config import game_config

# 获取能力配置
ability = game_config.config_ability[0]
print(ability.name)  # "皮肤感度"

# 获取某类型的所有能力
sensitivity_abilities = game_config.config_ability_type_data[0]
```

## 构建标志

buildconfig.py中的标志控制构建行为：

- `BUILD_CONFIG`: 是否构建基础配置
- `BUILD_EVENT`: 是否构建事件数据
- `BUILD_TALK`: 是否构建口上数据
- `BUILD_CHARACTER`: 是否构建角色数据
- `BUILD_CHARA_ID`: 指定只构建某个角色的数据（0表示全部）

## 总结

这个系统通过CSV提供了灵活的配置方式，自动生成类型安全的Python代码，并在运行时高效地加载和索引数据。整个流程确保了数据的一致性和类型安全，同时支持国际化和复杂的数据关系。