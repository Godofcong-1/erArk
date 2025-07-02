# PRTS系统

## 系统概述

PRTS系统是erArk游戏中的一个帮助与教程系统，模拟明日方舟世界中的"普瑞赛斯"，为玩家提供游戏机制说明、攻略指导和角色口上信息查询功能。

## 核心组件

### 1. 面板类

**主要类：** `Prts_Panel` (`Script/UI/Panel/prts_panel.py`)

**功能：**
- 显示普瑞赛斯终端主界面
- 提供分类教程问题选择
- 管理问答交互流程
- 处理角色口上信息查询

**关键属性：**
- `width`: 绘制宽度
- `draw_list`: 绘制文本列表
- `fater_type`: 当前选择的父分类

### 2. 角色信息显示类

**主要类：** `ShowCharaNameDraw` (`Script/UI/Panel/prts_panel.py`)

**功能：**
- 显示角色名称和作者信息
- 管理角色文本版本切换
- 处理角色口上信息展示
- 支持多版本文本选择

## 数据结构

### 1. PRTS教程数据

**配置文件：** `data/csv/Prts.csv`
**数据结构：**
```python
class Prts:
    cid: int          # 编号id
    fater_type: int   # 父类id(0系统，1日常，2攻略，3H，4经营)
    son_type: int     # 子类id
    qa: str           # 问题还是回答 ("q"/"a")
    text: str         # 内容
```

**存储方式：**
- `config_prts_data[父类id][子类id][0]` - 问题
- `config_prts_data[父类id][子类id][1]` - 答案

### 2. 角色文本说明数据

**配置文件：** `data/csv/Tip_Chara.csv`
**数据结构：**
```python
class Tip_Chara:
    cid: int               # 提示id
    chara_adv_id: int      # 角色adv_id
    version_id: int        # 版本id
    writer_name: str       # 作者名
    talk_file_path: str    # 口上文件路径
    event_file_path: str   # 事件文件路径
    text: str              # 文本内容
```

**存储方式：**
- `config_tip_chara_data[cid]` - 角色提示数据
- `config_tip_chara_data_by_adv[adv_id]` - 按角色分组的提示列表

## 主要功能模块

### 1. 问答系统

**入口函数：** `Prts_Panel.draw()`

**流程：**
1. 显示普瑞赛斯欢迎界面
2. 展示主要分类选项（系统、日常、攻略、H、经营等）
3. 进入子分类选择 (`select_question`)
4. 显示具体问答内容 (`show_answer`)

**分类说明：**
- 0: 系统相关（UI问题、刻印、催眠等）
- 1: 日常生活（干员行动、体力提升等）
- 2: 攻略指导（关系处理、路线说明等）
- 3: H相关（H指令、怀孕系统等）
- 4: 经营管理（基建、招募、资源等）

### 2. 角色口上信息系统

**入口函数：** `chara_talk_info()`

**流程：**
1. 获取所有有口上信息的角色列表
2. 使用 `ShowCharaNameDraw` 显示角色信息
3. 支持版本切换功能
4. 显示作者信息和文本内容

**关键功能：**
- 角色文本版本管理
- 多作者支持
- 动态版本切换
- 口上文件大小显示

### 3. 版本管理系统

**功能：** 管理同一角色的多个文本版本

**存储位置：** `cache.all_system_setting.character_text_version[adv_id]`

**切换机制：**
1. 显示角色所有可用版本
2. 显示当前选择版本
3. 允许切换到其他版本或不使用版本
4. 实时更新显示状态

## 数据流程

### 1. 数据加载流程

```
CSV文件 → buildconfig.py → JSON数据 → config_def类 → game_config配置
```

**详细步骤：**
1. `Prts.csv` 被 `buildconfig.py` 读取
2. 转换为JSON格式存储在 `data/data.json`
3. 游戏启动时通过 `load_prts()` 加载
4. 构建层次化数据结构 `config_prts_data`

### 2. 角色信息加载流程

```
Tip_Chara.csv → character文本信息 → 按adv_id分组 → 版本管理
```

**详细步骤：**
1. `Tip_Chara.csv` 记录角色文本版本信息
2. 按 `chara_adv_id` 分组存储
3. 支持多版本文本管理
4. 与角色数据关联显示

### 3. ID转换机制

**函数：** `character.get_character_id_from_adv(adv_id)`

**作用：** 将剧情ID转换为游戏内角色ID

**实现：** 遍历 `cache.character_data` 匹配 `adv` 字段

## 用户交互流程

### 1. 主界面交互

```
主界面 → 选择分类 → 选择具体问题 → 查看答案 → 返回
```

### 2. 角色信息交互

```
角色列表 → 选择角色 → 版本信息 → 版本切换 → 确认选择
```

### 3. 导航结构

- **Panel.PRTS (24)** - 普瑞赛斯面板常量
- **normal_flow.py** - 面板流程管理
- **constant.Panel** - 面板ID定义

## 技术特点

### 1. 模块化设计
- 独立的面板类设计
- 数据与UI分离
- 可扩展的分类系统

### 2. 多版本支持
- 同一角色多个文本版本
- 动态版本切换
- 作者信息管理

### 3. 层次化数据
- 父类-子类分类结构
- 问答对应机制
- 灵活的扩展性

### 4. 国际化支持
- 使用翻译API (`get_text._`)
- 支持多语言文本
- 文本动态加载

## 配置文件关系

```
Prts.csv ────────┐
                 ├──→ buildconfig.py ──→ data.json ──→ game_config.py
Tip_Chara.csv ───┘

Character.csv ──→ 角色基础数据 ──→ character.py ──→ ID转换
```

## 代码依赖关系

```
prts_panel.py
├── game_config (数据配置)
├── character (角色处理)
├── draw (UI绘制)
├── panel (面板基类)
├── flow_handle (流程控制)
└── constant (常量定义)
```

## 扩展点

### 1. 新增问答分类
- 在Prts.csv中添加新的 `fater_type`
- 在主界面添加对应选项
- 实现对应的处理逻辑

### 2. 角色文本版本管理
- 支持版本比较功能
- 添加版本更新通知
- 实现版本回退机制

### 3. 搜索功能
- 问答内容全文搜索
- 角色快速查找
- 标签分类系统

该系统为游戏提供了完整的帮助和教程功能，通过结构化的数据管理和用户友好的界面设计，帮助玩家理解游戏机制和角色信息。