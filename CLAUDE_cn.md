# CLAUDE_cn.md

此文件为 Claude Code (claude.ai/code) 在处理此代码库时提供指导。

## 项目概述

erArk 是一个基于明日方舟角色的 R18 成人游戏，使用 Python 开发。这是一个基于文本的模拟游戏，包含角色互动、事件和各种游戏系统。

## 核心开发命令

### 运行游戏
```bash
python game.py
```

### 构建游戏数据
运行游戏前，需要构建配置数据：
```bash
python buildconfig.py  # 构建 CSV 配置和 JSON 数据
python buildpo.py      # 构建本地化 PO 文件
python buildmo.py      # 从 PO 文件构建 MO 文件
```

### 安装依赖
```bash
pip install -r requirements.txt
```

### 测试单个组件
游戏使用调试模式（在 config.ini 中配置）进行测试。设置 `debug = 1` 启用调试功能。

## 高层架构

### 核心游戏流程
1. **入口点**：`game.py` - 初始化游戏，加载配置，启动 GUI 或 Web 模式
2. **游戏初始化**：`Script/Core/game_init.py` - 设置游戏环境、样式和主流程
3. **主框架循环**：`Script/Design/start_flow.py` - 包含 UI 处理和面板管理
4. **主行为循环**：`Script/Design/character_behavior.py` - 实际的游戏模拟循环

### 关键系统

#### 配置系统
- **CSV 数据**：游戏数据存储在 `data/csv/` 下的 CSV 文件中
- **构建过程**：`buildconfig.py` 读取 CSV 并生成：
  - JSON 数据文件（`data/*.json`）
  - Python 配置定义（`Script/Config/config_def.py`）
  - 本地化 PO 文件（`data/po/`）

#### 角色系统
- **角色模板**：以 CSV 文件形式存储在 `data/character/`
- **角色管理**：`Script/Design/character.py` 和 `character_handle.py`
- **角色行为**：`Script/Design/character_behavior.py`
- **AI 系统**：`Script/Design/handle_npc_ai.py` 和 `handle_npc_ai_in_h.py`

#### 事件系统
- **事件数据**：`data/event/` 中的 JSON 文件
- **事件处理**：`Script/Design/event.py`
- **对话系统**：`data/talk/` 中的 CSV 文件用于角色对话

#### UI 系统
- **流程管理**：`Script/Core/flow_handle.py`（GUI）和 `flow_handle_web.py`（Web）
- **绘制系统**：`Script/UI/Moudle/draw.py`，Web 适配器在 `Script/UI/web_draw_adapter.py`
- **面板**：各种 UI 面板在 `Script/UI/Panel/`

#### 存档系统
- **存档管理**：`Script/Core/save_handle.py`
- **缓存控制**：`Script/Core/cache_control.py` 管理游戏状态

### Web 模式
游戏支持基于 Web 的界面：
- 在 `config.ini` 中设置 `web_draw = 1` 启用
- Web 服务器实现在 `Script/Core/web_server.py`
- Web IO 适配器在 `Script/Core/io_web.py`

## 代码指南

1. **注释**：所有注释应使用中文
2. **函数文档**：每个函数必须有中文注释说明：
   - 输入参数和类型
   - 返回值和类型
   - 函数功能
3. **代码段**：每一小段代码都需要有注释说明其作用
4. **代码风格**：使用 Black 格式化器，行宽 200

## 关键配置文件

- `config.ini`：主游戏配置
- `data/data.json`：从 CSV 编译的游戏数据
- `data/Character.json`：角色模板数据
- `data/Character_Talk.json`：角色对话数据
- `data/Character_Event.json`：角色事件数据

## 开发工作流

1. 编辑 `data/csv/`、`data/talk/` 或 `data/character/` 中的 CSV 文件
2. 运行 `python buildconfig.py` 重建游戏数据
3. 运行 `python game.py` 测试更改
4. 对于本地化更改，运行 `python buildpo.py` 和 `python buildmo.py`

## CI/CD 发布结构

GitHub Actions 工作流（`.github/workflows/python-app.yml`）会生成 4 个发布包：

| 包名 | 说明 | 包含内容 |
| --- | --- | ------- |
| `erArk_{版本号}.zip` | 完整游戏包 | 包含所有资源的完整游戏 |
| `erArk_Lite_{版本号}.zip` | 轻量游戏包 | 不包含立绘、场景等大图片资源的游戏 |
| `erArk_Images_{版本号}.zip` | 图片资源包 | 除 `image/状态条` 外的所有图片文件夹 |
| `erArkEditor.zip` | 口上事件编辑器 | 独立的编辑器工具 |

**图片文件夹分布：**
- **仅在图片资源包中**：`image/场景`、`image/断面图`、`image/立绘`、
- **完整版和轻量版都包含**：`image/状态条`、`image/logo.png` 及其他根目录文件

**注：** 轻量版 + 图片资源包 = 完整版

## 重要说明

- 游戏处于 alpha 测试阶段，部分功能尚未实装
- 游戏需要 Sarasa Mono SC 字体以正确显示
- 仅官方支持 Windows
- 内存需求：峰值约 1GB，确保有 2GB 空闲内存

## 主行为循环（`character_behavior.init_character_behavior()`）

这是管理角色行为和时间推进的核心游戏循环：

### 1. 玩家阶段
- 玩家通过 UI 面板选择一个行动（指令）
- 行动设置玩家角色的行为 ID、持续时间和开始时间
- 循环处理玩家行为直到完成（`0 not in cache.over_behavior_character`）
- 时停模式的特殊处理 - 玩家行动后时间会回退

### 2. NPC 阶段
- 玩家行动完成后，处理 `cache.npc_id_got` 中的所有 NPC
- 每个 NPC 的行为基于以下内容计算：
  - 当前状态（疲劳、跟随、H 模式、无意识等）
  - AI 决策（`handle_npc_ai.find_character_target()`）
  - 所在位置的可用行动和目标
- NPC 继续他们的行为直到全部完成

### 3. 时间管理
- 时间基于行为持续时间推进
- 每个角色都有 `behavior.start_time` 和 `behavior.duration`
- 行为完成时，角色进入空闲状态（`SHARE_BLANKLY`）
- 午夜时触发新一天，执行 `past_day_settle.update_new_day()`
- 玩家睡眠触发自动存档，通过 `sleep_settle.update_save()`

### 4. 行为处理（`character_behavior()`）
对每个角色：
- **行为前检查**：疲劳/睡眠、移动限制、助理模式、跟随模式、H 状态
- **状态结算**：`judge_character_status()` 处理事件和数值变化
- **实时更新**：`realtime_settle.character_aotu_change_value()` 应用基于时间的变化
- **状态持续**：更新持续中的状态和条件
- **完成检查**：`judge_character_status_time_over()` 判断行为是否完成
- **素质获得**：基于行动自动获得素质

### 5. 结算系统
- **行为效果**：`settle_behavior.handle_settle_behavior()` 计算数值变化
- **事件系统**：事件可以在指令前或指令后触发
- **变化累积**：所有变化都在 `CharacterStatusChange` 对象中追踪
- **向玩家显示**：玩家行动后，变化会被格式化并显示
- **特殊处理**：群体活动、隐藏行动和复杂交互

### 6. 关键变量
- `cache.over_behavior_character`：完成当前行为的角色集合
- `cache.game_time`：当前游戏时间
- `pl_start_time`：玩家行为开始时间（NPC 计时的参考）
- `cache.time_stop_mode`：时间不推进的特殊模式

### 7. 循环退出条件
- 所有角色（玩家 + NPC）都完成了他们的行为
- 时停模式激活（只有玩家行动，然后循环中断）
- 中断正常流程的特殊事件或状态变化

## 绘制系统 - 两种渲染模式

游戏支持两种渲染模式：普通模式（Tkinter）和 Web 模式。模式由 `config.ini` 中的 `web_draw` 决定。

### 普通绘制模式（Tkinter）

当 `web_draw = 0` 时，游戏使用 Tkinter 进行 GUI 渲染：

1. **绘制类**（`Script/UI/Moudle/draw.py`）：
   - `NormalDraw`：带宽度限制的基础文本绘制
   - `CenterDraw`：居中对齐文本
   - `RightDraw`：右对齐文本
   - `Button`：交互式按钮元素
   - `FullDraw`：不截断地绘制文本
   - `WaitDraw`：绘制文本并等待玩家输入
   - `LineFeedWaitDraw`：在每个换行处等待

2. **IO 操作**（`Script/Core/io_init.py`）：
   - 使用 Tkinter 的 `main_frame` 进行显示
   - 通过事件队列处理命令
   - 直接渲染到 Tkinter 文本小部件

3. **流程控制**（`Script/Core/flow_handle.py`）：
   - `askfor_all()`：等待玩家从选项中选择
   - `askfor_wait()`：简单等待玩家输入
   - 通过 Tkinter 绑定直接处理事件

### Web 绘制模式

当 `web_draw = 1` 时，游戏作为 web 服务器运行：

1. **Web 绘制类**（`Script/UI/web_draw.py`）：
   - `WebDrawBase`：web 元素的基类
   - `WebNormalDraw`：文本元素转为 HTML
   - `WebButton`：交互式按钮转为 HTML
   - 所有绘制对象生成 HTML 元素字典

2. **绘制适配**（`Script/UI/web_draw_adapter.py`）：
   - `WebDrawAdapter`：将 Tkinter 绘制对象转换为 web 元素
   - 适配所有绘制类型（普通、居中、右对齐、按钮等）
   - 元素存储在 `cache.current_draw_elements`

3. **Web IO 操作**（`Script/Core/io_web.py`）：
   - `era_print()`：将文本转换为 HTML 元素
   - `clear_screen()`：清空元素缓存并更新 web 状态
   - 通过 web API 请求处理命令
   - 无直接渲染，所有输出作为 HTML 元素缓冲

4. **Web 流程控制**（`Script/Core/flow_handle_web.py`）：
   - `askfor_all()`：轮询 web API 响应
   - 通过 `update_game_state()` 更新游戏状态
   - 通过 HTTP 请求进行异步命令处理

### 主要差异

1. **输出处理**：
   - 普通模式：直接写入 Tkinter 小部件
   - Web 模式：在 `cache.current_draw_elements` 中缓冲 HTML 元素

2. **输入处理**：
   - 普通模式：Tkinter 事件绑定和队列
   - Web 模式：HTTP API 轮询和响应处理

3. **状态管理**：
   - 普通模式：即时 UI 更新
   - Web 模式：通过 `update_game_state()` 批量更新发送给客户端

4. **命令处理**：
   - 普通模式：同步事件处理
   - Web 模式：异步请求/响应循环

### 开发注意事项

- 所有 UI 组件都应使用抽象绘制类
- 避免直接操作 Tkinter 或 HTML
- 使用 `io_init.era_print()` 进行所有文本输出
- 在进行 UI 更改时测试两种模式
- Web 模式需要 web 服务器在端口 5000 上运行