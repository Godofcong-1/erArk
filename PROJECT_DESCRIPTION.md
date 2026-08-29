# erArk 项目完整描述（AI 工作基准文档）

> **当前 DeepSeek Harness 版本：`0.1.0-rc.7`（即 `@deepseek-ai/dsh`，以 `node_modules/@deepseek-ai/dsh` 实际安装版本为准）**

> 用途：本文档是 erArk 仓库的一份自包含、可持续维护的完整项目描述，供后续 AI/开发者快速建立上下文。
> 生成时间：2026-08-18；代码快照：`master @ b17d1b1ba`；游戏版本：`v0.66 / package.json = 2026.8.18`。
> 若代码发生大版本变更，应先更新本文档，再基于本文档工作。
> 更细的系统级文档索引见最后一节“文档导航”；仓库自带的 `CLAUDE.md` / `CLAUDE_cn.md` / `.github/copilot-instructions.md` 也需结合阅读。

---

## 1. 项目定位与状态

- **项目名**：erArk（era-明日方舟）
- **性质**：基于明日方舟角色的 R18 文字模拟游戏，纯爱向，无牛无 G（作者声明）
- **主要玩法来源**：以 eraTW 为主，缝合 AM / YM / SQC / MGT 等 era 系游戏机制
- **技术栈**：Python（3.12 目标版本）+ Tkinter（默认 GUI）+ Flask-SocketIO（Web 模式）+ PySide6（仅编辑器）+ gettext（本地化）
- **开发状态**：α 测试阶段；单人独立开发，持续更新中
- **当前版本**：v0.66（2026-08-18）
- **协议**：CC BY-NC-SA 2.0；早期部分代码来自 dieloli；禁止商业用途
- **警告**：游戏含色情、暴力内容，禁止向未成年人传播
- **玩家入口**：Release 中的 exe；官方支持系统为 Windows；Tk 模式仅 Windows，Web 模式不限设备
- **画面要求**：无显卡要求，但 AA 地图建议 1080P+；峰值内存约 1GB
- **字体**：默认依赖“等距更纱黑体 SC / Sarasa Mono SC”，可通过 `config.ini -> font` 修改

---

## 2. 仓库规模快照

| 类别 | 规模 |
| --- | --- |
| 总文件数（排除 .git/.conda/node_modules/dist/build 等生成物） | 约 6800 |
| Python 文件 | 约 294 个 |
| 核心游戏代码 `Script/` | 约 158,000 行（7 个子包） |
| 角色模板 | 359 个（`data/character/*.csv`） |
| 通用配置表 | `data/csv/` 113 张主表 + `cook_question/` 140 张题库 CSV |
| 角色口上数据 | `Character_Talk.json` 内约 91,943 条 |
| 通用口上数据 | `Talk_Common.json` 内约 215,322 条 |
| 指令 | `InstructConfig.csv` 定义 408 条，`handle_instruct.py` 注册 400 个处理函数 |
| 行为 | `Behavior_Data.csv` 定义 688 个行为 |
| 前提处理函数 | 约 1,886 个（`handle_premise` 包内统计） |
| 结算处理函数 | 一段/二段共约 638 个（`@settle_behavior` 注册，`Script/Settle`） |
| 状态机动作 | 约 175 个（`Script/StateMachine/default.py`） |
| 面板注册 | 64 个（`@handle_panel.add_panel`） |
| 地图 | 529 个 `Scene.json` + 33 个 `Map.json`，分 23 个顶层区域 |
| 图片 | `image/立绘` 1436、`image/全场景` 247、`image/场景` 66、`image/断面图` 18、`image/状态条` 12 |

### Script 子包行数

| 目录 | Python 文件数 | 代码行数 | 职责 |
| --- | ---: | ---: | --- |
| `Script/Core` | 33 | 23,276 | 引擎层：缓存、类型、存档、IO、流程、Web 服务器、Mod、常量、文本/富文本 |
| `Script/Design` | 52 | 43,327 | 主游戏逻辑：行为循环、NPC AI、地图、口上、事件、前提、结算分发、角色/时间 |
| `Script/Settle` | 10 | 18,772 | 结算实现：一段效果、二段效果、通用结算、道具、实时/过天/睡眠 |
| `Script/System` | 52 | 26,755 | 垂直子系统：烹饪、宿舍、外勤、指令、医疗、性爱、Web 绘制 |
| `Script/UI` | 67 | 38,095 | 绘制基础模块、面板、标题/创建角色/常规流程 |
| `Script/StateMachine` | 2 | 3,151 | NPC 行为原子动作（移动、等待、去某地、睡觉等） |
| `Script/Config` | 6 | 4,786 | 配置加载与自动生成的 `config_def.py` |

---

## 3. 环境、依赖与常用命令

### 3.1 依赖

`requirements.txt` 关键项：

| 依赖 | 用途 |
| --- | --- |
| `psutil`, `wcwidth`, `numpy`, `Pillow` | 运行时基础能力/排版/图像 |
| `pyephem` / `ephem`, `python-dateutil` | 天文计算（月相、太阳时段）与日期 |
| `PySide6` | ArkEditor 图形编辑器 |
| `flask`, `flask-socketio`, `python-socketio` | Web 模式服务器 |
| `openai`, `google-genai` | 游戏内 AI 文本生成（OpenAI 兼容接口与 Gemini） |

仓库自带本地 conda 环境：`.conda/python.exe`（调试时可用 `/mnt/c/code/era/erArk/.conda/python.exe` 或本地等价路径）。

### 3.2 常用命令

```bash
# 运行游戏（启动时自动执行 auto_build_config 增量构建）
python game.py

# 全量构建：data/csv、data/talk、data/event、data/character 等 -> JSON + config_def.py + PO
python buildconfig.py

# 预热运行时缓存（CI 在 buildconfig 后运行，用于打包）
python init_data.py

# 从 .py 源码提取可翻译字符串 -> data/po/zh_CN/LC_MESSAGES/erArk_py.po
python buildpo.py

# 将 en_US 的 talk/csv/py 三类 PO 编译成 MO
python buildmo.py

# 代码格式化（项目约定）
black --line-length 200 .
```

### 3.3 构建链注意事项

- **`game.py` 启动即构建**：导入 `auto_build_config.py`，对游戏配置做增量重建。
- `auto_build_config.py` 与 `buildconfig.py` 的差异：
  - `auto_build_config`：若 `data/Character_Talk.json`、`data/Talk_Common.json` 已存在，则跳过口上数据重建；不重写 `Script/Config/config_def.py`（代码中有“玩家版本不需要写入 config_def”注释）。
  - `buildconfig`：全量重建并重写 `Script/Config/config_def.py`。
- `buildata.py` **不是**数据构建脚本，而是开发者工具：生成前提/结算样板代码，并通过其 `mode` 变量在“前提/结算 Python 定义”与“CSV”之间互相转换。
- `init_data.py`：模拟游戏启动的缓存预热（Cache、normal_config、game_config、map_config），CI 打包前使用。
- 数据源修改后必须重建；未重建最常见的错误是 KeyError/属性缺失/旧枚举。

---

## 4. 顶层目录速览

| 路径 | 说明 |
| --- | --- |
| `game.py` | 唯一游戏入口（自动构建 + 初始化 + 启动 Tk/Web） |
| `config.ini` | 游戏运行配置（语言、Web/Tk、窗口、字体、日期、存档等） |
| `auto_build_config.py` | 启动时增量构建脚本 |
| `buildconfig.py` | 全量构建脚本 |
| `buildata.py` | 前提/结算样板代码开发工具 |
| `buildpo.py` / `buildmo.py` | PO 提取 / MO 编译 |
| `init_data.py` | CI 缓存预热 |
| `Script/` | 全部游戏源代码（见 §5） |
| `data/` | 数据源 + 生成 JSON + 地图 + PO（见 §6） |
| `image/` | 立绘、场景、断面图、状态条、logo、图片包版本 |
| `static/`, `templates/` | Web 模式前端（game.js / CSS / 中文字体 / index.html） |
| `tools/` | ArkEditor、AI 工具、MCP、下载/转换/维护脚本（见 §17） |
| `mod/` | Mod 系统配置与示例 Mod（见 §16） |
| `example/` | 编辑器教程/测试用例：事件、口上、外勤委托、富文本、纸娃娃文本 |
| `save/` | 存档目录（被 gitignore） |
| `.github/` | CI workflow、ISSUE 模板、agents、prompts（60+ 系统文档） |
| `old_data/`, `profiling/`, `profiling_output/` | 历史数据、性能分析与补丁、profiling 结果 |
| `dist/`, `build/` | PyInstaller 打包产物（被 gitignore） |
| `update.log` | 完整更新日志 |
| `todo list.txt` | 作者待办清单（含已规划未实装大系统） |
| `error.log` | 运行时错误记录（BUG 反馈用） |
| `package.json` | 游戏版本号（当前 `2026.8.18`） |
| `image/package.json` | 图片包版本号（当前 `2026.7.31`） |
| `CLAUDE.md` / `CLAUDE_cn.md` | 仓库 AI 指导文档（中英文） |
| `.github/copilot-instructions.md` | Copilot/AI 代理最小速查 |
| `ai_chat_api_key.csv` | AI 文本生成密钥（敏感，已 gitignore，勿提交） |

---

## 5. Script 代码架构

### 5.1 分层总览

```text
Script/
├── Config/                 # 配置加载（config_def.py 为自动生成）
│   ├── normal_config.py    # config.ini -> config_normal
│   ├── game_config.py      # data/*.json -> 运行时配置字典/对象
│   ├── character_config.py # Character.json -> NpcTem 模板
│   ├── map_config.py       # 地图 JSON -> cache.scene_data/cache.map_data
│   ├── name_config.py      # 随机姓名（当前入口被注释）
│   └── config_def.py       # 【自动生成】每张 CSV 一个带中文注释的类
├── Core/                   # 引擎层
│   ├── cache_control.py    # 全局 cache 句柄
│   ├── game_type.py        # Cache/Character/Behavior 等全部运行时数据类型
│   ├── constant/           # 常量枚举 + 注册表（详见 5.2）
│   ├── constant_effect.py  # BehaviorEffect 结算 ID 常量
│   ├── constant_promise.py # Premise 前提 ID 常量
│   ├── game_init.py        # 游戏初始化 + 主流程异常兜底
│   ├── flow_handle.py      # Tk 流程控制/命令绑定/输入
│   ├── flow_handle_web.py  # Web 流程控制/输入/面板切换
│   ├── io_init.py          # Tk IO 与绘制输出
│   ├── io_web.py           # Web 元素缓冲输出
│   ├── main_frame.py       # Tk 主窗口与事件总线
│   ├── web_server.py       # Flask-SocketIO 服务器与 API
│   ├── save_handle.py      # 存档读写与跨版本兼容
│   ├── mod_manager.py      # Mod 扫描/加载/函数替换
│   ├── get_text.py         # gettext 翻译函数 `_`
│   ├── text_handle.py      # 文本排版
│   ├── rich_text.py        # 富文本样式
│   ├── json_handle.py      # JSON 读写
│   ├── value_handle.py     # 数值处理
│   ├── era_image.py        # 图片管理
│   ├── dijkstra.py         # 寻路
│   ├── key_listion_event.py# 键盘监听
│   ├── py_cmd.py           # 命令/面板 ID 辅助
│   ├── old_chara_to_new.py # 旧角色数据迁移
│   └── perf_hook.py        # 性能埋点
├── Design/                 # 游戏设计逻辑（最大层）
│   ├── start_flow.py       # 主面板循环
│   ├── character_behavior.py # 核心行为循环
│   ├── character_handle.py / character.py / character_move.py
│   ├── handle_npc_ai.py / handle_npc_ai_in_h.py
│   ├── handle_premise/     # 前提系统（约 20 个主题模块 + __init__）
│   ├── settle_behavior.py  # 结算分发器
│   ├── second_behavior.py  # 二段行为
│   ├── talk.py             # 口上系统
│   ├── event.py            # 事件触发
│   ├── map_handle.py       # 地图/导航/场景移动
│   ├── game_time.py        # 时间、日期、月相、太阳时段
│   ├── attr_calculation.py # 属性初始化/升级计算
│   ├── handle_ability.py / handle_talent.py # 能力/素质
│   ├── pregnancy.py / clothing.py / basement.py
│   ├── handle_chat_ai.py   # AI 文本生成
│   ├── instuct_judege.py   # 指令实行值判定
│   ├── handle_state_machine.py # 状态机调度
│   ├── character_image.py / cross_section_image.py / talk_image.py # 图片决策
│   └── ...
├── Settle/                 # 结算实现
│   ├── default.py          # 376 个一段结算处理函数
│   ├── Second_effect.py    # 158 个二段结算处理函数
│   ├── common_default.py   # 通用基础结算（HP/MP/状态/好感/信赖/高潮等）
│   ├── default_cloth.py    # 服装结算
│   ├── item_effect.py      # 道具效果
│   ├── orgasm_settle.py    # 高潮结算（从二段行为中独立出）
│   ├── realtime_settle.py  # 实时数值变化/持续状态
│   ├── past_day_settle.py  # 跨天结算
│   └── sleep_settle.py     # 睡眠与自动存档
├── StateMachine/
│   └── default.py          # 175 个 NPC 原子动作（移动、等待、去某地等）
├── System/
│   ├── Cooking_System/     # 烹饪/食物
│   ├── Dormitory_System/   # 宿舍
│   ├── Field_Commission_System/ # 外勤委托
│   ├── Instruct_System/    # 指令注册、分类、显示、映射
│   ├── Medical_System/     # 医疗经营
│   ├── Sex_System/         # 群交/隐奸/露出/绳艺/醉奸等
│   └── Web_Draw_System/    # Web 渲染器与适配
└── UI/
    ├── Moudle/draw.py      # 绘制类抽象层（NormalDraw/Button/BarDraw...）
    ├── Moudle/panel.py     # 通用面板构建块
    ├── Panel/              # 64 个功能面板
    └── Flow/               # 标题 / 创建角色 / normal_flow 面板注册
```

### 5.2 注册表机制（理解扩展的关键）

`Script/Core/constant/__init__.py` 定义全局注册字典，各模块通过装饰器填充：

| 注册表 | 类型 | 注册装饰器 | 主要注册位置 |
| --- | --- | --- | --- |
| `handle_premise_data` | 前提ID -> 函数 | `@add_premise` | `Design/handle_premise/*` |
| `handle_instruct_data` | 指令ID -> 函数 | `@add_instruct` | `System/Instruct_System/handle_instruct.py` |
| `instruct_premise_data` | 指令ID -> 前提集合 | 由 `add_instruct` 写入 | 同上 |
| `settle_behavior_effect_data` | 效果ID -> 一段结算函数 | `@settle_behavior.add_settle_behavior_effect` | `Settle/default.py` 等 |
| `settle_second_behavior_effect_data` | 效果ID -> 二段结算函数 | `@settle_behavior.add_settle_second_behavior_effect` | `Settle/Second_effect.py` 等 |
| `handle_state_machine_data` | 状态机ID -> 函数 | `@handle_state_machine.add_state_machine` | `StateMachine/default.py` |
| `panel_data` | Panel ID -> 面板函数 | `@handle_panel.add_panel` | `UI/Flow/normal_flow.py` 等 |
| `cmd_map` | 命令编号 -> 命令处理 | `flow_handle.bind_cmd` | UI 各面板运行时 |

**核心流程依赖链**：CSV 配置决定“某个行为使用哪些结算效果 ID、某个指令显示需要哪些前提 ID”，代码装饰器决定“这些 ID 是否有实现”。

### 5.3 关键常量文件

- `Script/Core/constant/Behavior.py` + `Behavior_Int.py` + `BehaviorStr.py`：行为常量及其整数/字符串映射
- `Script/Core/constant/CharacterStatus.py`：角色状态属性常量
- `Script/Core/constant/SecondBehavior.py` + `SecondBehavior_Int.py`：二段行为常量
- `Script/Core/constant/StateMachine.py`：状态机动作常量
- `Script/Core/constant/__init__.py`：`Panel`、`InstructType`、`SexInstructSubType`、注册表、初始/禁止 NPC 名单、特殊结束 H 列表等
- `Script/Core/constant_promise.py`：前提 ID（`Premise` 类）
- `Script/Core/constant_effect.py`：结算 ID（`BehaviorEffect` 类）
- `Script/System/Instruct_System/Instruct.py`：指令 ID 常量

---

## 6. 数据体系

### 6.1 数据源（手改入口）

| 目录 | 内容 |
| --- | --- |
| `data/csv/` | 113 张主 CSV 配置表 + `cook_question/` 140 张烹饪题库 |
| `data/character/` | 359 个角色模板 CSV（命名 `AdvNpc_角色名.csv`） |
| `data/talk/` | 口上 CSV：`chara/`（角色专属）、`daily/sex/obscenity/play/work/system/arts/ai` 等通用场景口上 |
| `data/talk_common/` | 通用口上：`action_A`、`action_B1`、`action_B2`、`action_C1`、`action_C2`、`body`、`body_part` |
| `data/event/` | 事件 JSON：`event.json`、`hold.json`、`milk.json` + `chara/` 角色事件 |
| `data/target/default/` | NPC AI 目标定义：`target.csv`、`effect.csv` |
| `data/ui_text/` | UI 文本与 AI 系统提示词（如 `text_ai_system_promote.csv`） |
| `data/map/` | 地图定义：每张地图一对 `Map`（AA 地图文本）+ `Map.json`；每个场景一个 `Scene.json` |
| `data/po/<lang>/LC_MESSAGES/` | gettext PO/MO 文件 |

### 6.2 生成产物（不要手改）

| 文件 | 来源 |
| --- | --- |
| `data/data.json` | `data/csv/*.csv` 汇总（每张表：`data` 列表 + `gettext` 标记） |
| `data/Character.json` | `data/character/*.csv` |
| `data/Character_Talk.json` | `data/talk/*.csv` |
| `data/Talk_Common.json` | `data/talk_common/*.csv` |
| `data/Character_Event.json` | `data/event/*.json` |
| `data/ui_text.json` | `data/ui_text/*.csv` |
| `data/Cook_Question.json` | `data/csv/cook_question/*.csv` |
| `Script/Config/config_def.py` | 每张配置 CSV 自动生成一个带字段注释的数据类 |
| `data/SceneData`, `data/MapData`, `data/PlaceData` | 地图预处理 pickle |
| `data/ScenePath` | 场景寻路路径边 JSON |
| `data/po/zh_CN/LC_MESSAGES/erArk_*.po` | 构建时同步生成的原文 PO 模板 |

### 6.3 CSV 通用格式

大多数项目 CSV 使用固定的 5 行表头结构：

1. 字段名行（如 `cid,name,type,...`）
2. 字段中文描述行
3. 字段类型行（`int` / `str` / `bool` / `float` / `list` 等）
4. 标记行（全 0 或占位）
5. 数据表名行（生成类名/JSON key 用）
6. 从下一行开始为数据

`build_csv_config()` 中会按列类型转换值、收集需要 gettext 的列，并把每个文件写进 `data.json` 对应表。**新增字段必须先加 CSV 列，再全量 buildconfig，逻辑层通过 `game_config.config_xxx` 访问。**

### 6.4 角色模板 CSV 结构

`data/character/0001_阿米娅.csv` 示例字段：

- 基础：`AdvNpc`, `Name`, `Sex`, `Profession`, `Race`, `Nation`, `Birthplace`, `Hp`, `Mp`, `Dormitory`, `Token`, `Introduce_*`, `TextColor`
- 能力：`A|能力ID -> 等级`
- 经验：`E|经验ID -> 值`
- 素质：`T|素质ID -> 1`
- 服装：`C|服装模板ID -> 服装名`（`C|5-1` 表示套装变体）
- `Mother_id`：亲子关系（随机生成角色/婴儿系统）

### 6.5 口上 CSV 结构

- 角色口上 `data/talk/chara/*.csv`：字段 `cid, behavior_id, adv_id, premise, context`（版本字段自动加）
- 通用口上 `data/talk_common/**/*.csv`：同构，type 键由“目录 + 文件名”生成，如 `action_part_eat_A`
- 口上通过前提串筛选（`&` 与关系），支持占位符如 `{Name}`、`{TargetName}`、`{FoodName}` 与富文本/换行

### 6.6 事件 JSON 结构

每个事件对象字段（示意，省略部分真实字段；示例中的 `//` 注释仅为说明，实际 JSON 不含注释）：

```json
{
  "uid": "uuid",
  "adv_id": "107",          // 限定角色（0/空为通用）
  "behavior_id": "chat",    // 触发行为
  "start": 0,               // 开始/结束条件
  "type": 1,                // 指令前/后等类型
  "text": "事件文本",
  "premise": { "CVP_A1_Flag|0_GE_0": 1 },
  "settle": {},
  "effect": { "CVE_A1_Flag|0_G_5": 1 }
}
```

效果支持三类：
- 纯数字 ID：调用 `constant.settle_behavior_effect_data[id]`
- `CVE_`：综合数值结算（Comprehensive Value Effect）
- `CSE_`：综合指令状态结算（Comprehensive State Effect）
- 前提支持 `CVP_` 综合数值前提

### 6.7 地图数据

- 层级：大地图 `Map.json`（含 `PathEdge` 相邻关系与 `Map` AA 文本）→ 场景 `Scene.json`（`SceneName`、`In_Door`、`Exposed`、`Close_Type`、`Room_Area`、`SceneTag`、`Scene_Img` 等）
- 23 个顶层区域：中枢、书、仓储、关押、制造加工、动力、医疗、卫、大浴场、宿舍（1-9 区，269 文件）、工程、教、文职、机库、泰拉、生娱、甲板、疗养庭院、科研、训练、访客、贸易等
- 场景标签 `SceneTag` 被索引进 `constant.place_data`
- 预处理后生成 pickle（`SceneData/MapData/PlaceData`）与 `ScenePath`

---

## 7. 配置系统

### 7.1 `config.ini` 关键项

| 项 | 默认 | 含义 |
| --- | --- | --- |
| `debug` | 1 | 调试模式开关 |
| `web_draw` | 0 | 0 = Tkinter，1 = Web（Flask-SocketIO，端口 5000 起自动找空端口） |
| `perf_monitor` | 0 | Tk 渲染性能埋点 |
| `language` | zh_CN | gettext 语言 |
| `window_width/height`, `textbox_*`, `text_*`, `inputbox_*`, `font_size`, `tk_dpi` | 窗口/文本/输入框尺寸 |
| `year/month/day/hour/minute` | 2019-03-01 06:00 | 新游戏起始时间 |
| `max_save`, `save_page` | 100 / 10 | 存档数量与每页条数 |
| `text_wait` | 0 | 文本等待选项 |
| `font`, `font_url` | 等距更纱黑体 SC | 字体 |
| `home_url`, `licenses_url`, `origin_author`, `origin_url` | 主页/许可/原项目信息 |

### 7.2 运行时配置加载

- `normal_config.init_normal_config()`：ConfigParser 读 `config.ini`，键值尝试 int 化后写入 `config_normal.__dict__`；再读 `package.json` 版本号
- `game_config.init()`：加载 `data/data.json`、`Character_Talk.json` 等，把每张表的 dict 转换为 `config_def` 数据类实例，并建立大量索引（行为/口上/能力升级/装备/地图等等）
- `character_config.init_character_tem_data()`：加载 `Character.json` 生成 `NpcTem`，并扫描口上/事件文件大小
- `map_config.init_map_data()`：优先读 pickle，否则递归解析地图目录
- 翻译：`get_text._` 使用 gettext 翻译链；`revert_translation=True` 可反向查中文

---

## 8. 启动流程

`game.py` 的启动顺序：

1. 导入 `auto_build_config`（自动增量构建数据）
2. `cache_control.cache = game_type.Cache()` 创建全局缓存
3. `normal_config.init_normal_config()` 读配置
4. `get_text._` 翻译函数可用
5. `game_config.init()` 加载全部游戏配置
6. `init_mod_system()` 加载 Mod（失败仅告警不中断）
7. 读取 `web_mode` 写入 `cache.web_mode`
8. `character_config.init_character_tem_data()` 加载角色模板
9. `map_config.init_map_data()` 加载地图
10. `character_handle.init_character_tem()` 实例化角色
11. `game_time.init_time()` 初始化游戏时间
12. 若 `perf_monitor=1` 且 Tk 模式：启用 `perf_hook` + `profiling.ui_perf_patch`
13. 若 Web 模式：
    - `web_draw_adapter.apply_web_adapters()` 给绘制类打补丁
    - `game_init.io_init = io_web` 切换 IO
    - `start_server()` 启动 Flask-SocketIO（5000 起自动寻空端口，支持 eventlet monkey patch）
14. `game_init.run(start_flow.start_frame)` 启动游戏
15. `start_flow.start_frame()` 进入主循环，每轮执行 `constant.panel_data[cache.now_panel_id]()`
16. 异常兜底：写入 `error.log`，自动保存 99 号档，给玩家“回到标题/退出”选项

---

## 9. 运行时核心数据结构

`Script/Core/game_type.py` 定义全部运行时对象（行数约 1942）。

### 9.1 Cache（92 个字段）

全局唯一 `cache_control.cache`，关键字段分组：

- **渲染/输入**：`web_mode`, `current_draw_elements`, `web_*` 系列（交互状态/文本回溯/子面板/数值变化等）, `input_cache`, `cmd_data`, `now_panel_id`, `font_size`
- **角色世界**：`character_data`（角色ID -> Character）, `npc_tem_data`, `npc_id_got`, `forbidden_npc_id`, `npc_name_data`, `random_npc_list`
- **时间**：`game_time`, `pre_game_time`, `sun_phase`, `moon_phase`
- **地图**：`map_data`, `scene_data`, `now_init_map_id`, `collect_position_list`
- **行为循环**：`over_behavior_character`, `pl_sleep_save_flag`, `time_stop_mode`, `group_sex_mode`
- **基地/世界**：`rhodes_island`, `country`, `all_system_setting`, `world_setting`, `ai_setting`
- **玩家**：`achievement`, `first_bonus`, `daily_intsruce`, `pl_pre_behavior_instruce`
- **记录**：`taiggered_event_record`, `today_taiggered_event_record`
- **指令过滤/样式**：`instruct_type_filter`, `show_non_h_in_hidden_sex`, `output_text_style` 等

### 9.2 Character（74 个字段）

关键字段：

- 基本：`cid`, `name`, `nick_name*`, `sex`, `adv`, `dead`
- 数值：`hit_point*`, `mana_point*`, `sanity_point*`, `eja_point*`, `semen_point*`, `angry_point`, `tired_point`, `urinate_point`, `hunger_point`, `sleep_point`, `desire_point`, `drunk_point`
- 成长/社交：`ability`, `experience`, `juel`, `talent`, `favorability`, `trust`, `status_data`
- 行为：`behavior`（Behavior 对象）, `second_behavior`, `must_settle/must_show_second_behavior_id_list`, `last_behavior_id_list`
- 位置/住宿：`position`, `officeroom`, `dormitory`, `pre_dormitory`
- 子对象：`event`, `cloth`, `item`, `food_bag`, `target_character_id`, `body_manage`, `first_record`, `dirty`, `h_state`, `sp_flag`, `action_info`, `work`, `entertainment`, `pregnancy`, `relationship`, `hypnosis`, `author_flag`
- 玩家特有：`pl_ability`, `pl_collection`, `collection_character`
- 其他：`birthday`, `text_color`, `talk_size`, `token_text`, `assistant_character_id`, `assistant_services`, `chara_setting`

### 9.3 Behavior / 其他重要类

- `Behavior`：`start_time`, `duration`, `behavior_id`, 移动目标 `move_target/move_src/move_final_target`, 食物 `target_food`, 书、奶量、尿量、礼物等 19 个字段
- `NpcTem`：角色模板（能力/经验/素质/服装/基础属性）
- `Map` / `MapDraw` / `MapDrawLine` / `MapDrawText`：AA 地图与绘制
- `Scene`：场景路径、名字、室内外、家具、门、面积、标签、角色列表、图片
- `Rhodes_Island`：基地设施等级、电力、宿舍、食堂、医疗、仓库、外交、囚犯、收入等
- `Country`：势力外交数据
- `CharacterStatusChange` / `TargetChange`：结算数值变更累积器
- `DIRTY`, `PREGNANCY`, `RELATIONSHIP`, `HYPNOSIS`, `CLOTH`, `BODY_H_STATE`, `FIRST_RECORD`, `ACTION_INFO`, `AUTHOR_FLAG` 等：角色各领域状态容器

---

## 10. 主行为循环（核心机制）

入口 `Script/Design/character_behavior.py`：

```text
init_character_behavior()
├── 清空 cache.over_behavior_character
├── 玩家阶段：while 0 not in over_behavior_character
│       pl_start_time/pl_duration 记录 -> character_behavior(0, game_time, pl_start_time)
├── 时停模式：回退时间，直接结束
├── field_commission_function.update_field_commission()
├── NPC 阶段：id_list = npc_id_got - {0}
│       while len(over_behavior_character) <= len(id_list)
│           for 每个未完成 NPC: character_behavior(id, game_time, pl_start_time)
├── 跨天：game_time.day != pre_game_time.day -> past_day_settle.update_new_day()
├── 睡觉存档：pl_sleep_save_flag -> sleep_settle.update_save()
└── 结束时成就结算（时停/群交）
```

`character_behavior(character_id, now_time, pl_start_time)` 对每个角色：

1. 死亡角色直接返回；`start_time` 为空时初始化
2. NPC：`run_npc_pre_behavior_checks()`（疲劳/睡眠/移动限制/助理/跟随/H 等）
3. 玩家：
   - 记录指令历史 `daily_intsruce`、`pl_pre_behavior_instruce`
   - 空闲 `SHARE_BLANKLY`：直接标记完成
   - 移动：结算同场景跟随 + 重置目击玩家 H
   - 非空闲：`judge_before_pl_behavior()` -> `judge_character_status()`（事件 + 结算）-> `realtime_settle.character_aotu_change_value()` -> 睡眠结算 -> `change_character_persistent_state()` -> `judge_character_status_time_over()`
   - 随后结算疲劳、H/猥亵/无意识、玩家实时数据
4. NPC：
   - 空闲：`handle_npc_ai.find_character_target()` 寻找目标
   - 移动或空闲时执行 `judge_character_status()`
   - 实时数值/持续状态更新
   - `judge_interrupt_character_behavior()` 打断判定
   - 时间到则加入完成集合
5. 末尾 `handle_talent.gain_talent()` 自动获得素质

`judge_character_status()` 内部：
- 取场景、行为起止时间
- 触发指令前置事件 `event.handle_event(..., event_before_instrust_flag=True)`
- 调用 `settle_behavior.handle_settle_behavior(character_id, end_time, event_type_now)`
- 触发指令后事件
- 绘制事件/结算面板

时间推进与完成判定：
- `cache.game_time` 是当前游戏时间；行为有 `start_time + duration`
- `judge_character_status_time_over()` 比较时间并处理跨天
- 新一天 `past_day_settle.update_new_day()`

---

## 11. 前提系统（条件判定）

### 11.1 组成

- **ID 常量**：`Script/Core/constant_promise.py` 的 `Premise` 类
- **核心管理**：`Script/Design/handle_premise/__init__.py`
  - `@add_premise(premise)` 注册
  - `handle_premise(premise, character_id)` 分发执行
  - `get_weight_from_premise_dict()` 批量计算权重（含缓存、目标角色处理、无意识跳过）
  - `handle_comprehensive_value_premise()` 处理 `CVP_` 综合前提
- **主题模块**：`handle_premise_H.py`（H 相关，4084 行）、`handle_premise_other.py`、`handle_premise_place.py`、`handle_premise_ability.py`、`handle_premise_arts.py`、`handle_premise_assistant.py`、`handle_premise_base_value.py`、`handle_premise_body_manage.py`、`handle_premise_cloth.py`、`handle_premise_dirty.py`、`handle_premise_entertainment.py`、`handle_premise_fall.py`、`handle_premise_first.py`、`handle_premise_food.py`、`handle_premise_last_cmd.py`、`handle_premise_sp_flag.py`、`handle_premise_talent.py`、`handle_premise_time.py`、`handle_premise_work.py`
- **特殊优化**：`UnnormalFlagMask` 位掩码缓存（`_ensure_unnormal_flag_storage`、`_calculate_unnormal_flag_mask`）减少异常状态前提重复计算；`premise_profiler_patch.py` 性能分析补丁

### 11.2 命名约定

- `T_` 前缀：交互对象（target）版本前提
- `t_` 前缀：否/反向版本
- 组合前提如 `NORMAL_1_2_4`、`T_NORMAL_267` 等

### 11.3 调用场景

- 指令面板：判断指令是否显示、是否可执行
- 口上选择：判断口上适用
- NPC AI：判断目标/行动可用性
- 事件：判断事件触发

---

## 12. 结算系统

### 12.1 一段结算

- 分发器：`Script/Design/settle_behavior.py::handle_settle_behavior()`
- 数据流：`Behavior_Effect.csv` 定义“行为ID -> 效果ID 列表”，`game_config.config_behavior_effect_data` 加载索引
- 效果 ID 可以是：
  - int：直接调用 `constant.settle_behavior_effect_data[effect_id]`
  - `CVE_*`：综合数值结算
  - 事件中的 `CSE_*`：综合指令状态结算
- 实现：`Script/Settle/default.py`（376 个处理函数）、`common_default.py`（通用 HP/MP/状态/快感/好感/信赖/高潮/经验计算）、`default_cloth.py`、`item_effect.py`、`orgasm_settle.py`
- 所有变化累积在 `CharacterStatusChange` / `TargetChange`，玩家行动后格式化显示；Web 模式还有 `collect_web_value_changes()`
- 群交、性爱助手等特殊结算分支在 `handle_settle_behavior()` 中处理

### 12.2 二段结算

- `Script/Design/second_behavior.py::check_second_effect()`
- `Script/Settle/Second_effect.py` 定义 158 个二段处理函数
- 用于事后连锁：刻印获得、初吻/初夜、高潮经验、多周目素质、特殊状态转变等
- 玩家对 NPC 行动后额外对目标做二段结算；解除时停时对全部 NPC 做二段结算

### 12.3 实时/跨天/睡眠结算

- `realtime_settle.character_aotu_change_value()`：按时间流逝自动变化数值
- `realtime_settle.change_character_persistent_state()`：持续状态
- `past_day_settle.update_new_day()`：跨天刷新（污浊、高潮计数等）
- `sleep_settle.update_sleep()` / `update_save()`：睡觉结算与自动存档

---

## 13. 口上系统

- 入口：`Script/Design/talk.py::handle_talk()`
- 数据：`Character_Talk.json`（角色口上）+ `Talk_Common.json`（通用口上）
- 选择流程：按行为 ID 取候选 -> 计算每条前提权重 -> 按权重随机选择 -> 渲染文本
- 支持：连锁口上（`handle_second_talk`）、必须显示/必须结算口上、特殊口上权重、口上跳绘判定、富文本代码转绘制文本
- 口上按角色 `adv_id` 索引：`game_config.config_talk_data_by_chara_adv`
- 通用口上类型由目录生成，如 `action_part_eat_A`
- 编辑器可直接编辑口上 CSV；快速测试口上面板 `debug_panel.TALK_QUICK_TEST`

---

## 14. 事件系统

- 入口：`Script/Design/event.py::handle_event(character_id, event_before_instrust_flag)`（文件小，逻辑核心）
- 数据：`data/event/*.json` -> 构建为 `Character_Event.json`
- 触发时按角色 `adv_id`、行为 `behavior_id`、`start/type`、`premise` 筛选
- 事件类型：指令前置、指令后置、子事件（`son_event_id`）、多层嵌套事件
- 事件文本通过 `DrawEventTextPanel` 绘制；选项通过 `Event_option_Panel`
- 效果结算走与行为相同的 `CVE/CSE/int` 体系
- 记录触发次数：`cache.taiggered_event_record` / `today_taiggered_event_record`

---

## 15. 指令系统

- 注册：`Script/System/Instruct_System/handle_instruct.py`
  - 400 个 `@add_instruct` 装饰器
  - `add_instruct` 支持从 `InstructConfig.csv` 读参数（类型/名称/前提集/行为ID/Web分类等），装饰器参数优先
- ID 常量：`Script/System/Instruct_System/Instruct.py`
- 配置：`data/csv/InstructConfig.csv`（408 条）
- 分类：`InstructCategory`（系统面板/角色交互/角色交互面板）、`InteractionMajorType` / `InteractionMinorType`（Web 新模式身体部位分类）
- 显示与过滤：`Script/UI/Panel/instruct_filter_panel.py`、`Script/System/Instruct_System/see_instruct_panel.py`
- 实行判定：`Script/Design/instuct_judege.py`；`InstructJudge.csv` 定义实行值判定
- 调度：`handle_instruct()` 将指令放入 `instruct_queue`，若存在 `constant.instruct_premise_data` 映射则调用对应 `constant.handle_instruct_data` 函数
- 执行后行为写入 `character_data.behavior.behavior_id`，由主行为循环结算

---

## 16. NPC AI 与状态机

### 16.1 NPC AI

`Script/Design/handle_npc_ai.py` 关键函数：

- `run_npc_pre_behavior_checks()`：行动前检查序列
- `find_character_target()`：空闲 NPC 根据状态/地点/可用行动/目标表寻找行动
- `search_target()`：按目标定义搜索
- `npc_auto_work_or_entertainment()`：自动工作/娱乐
- `judge_interrupt_character_behavior()`：中断判定
- `judge_character_tired_sleep()`：疲劳睡眠
- `judge_assistant_character()` / `judge_character_follow()` / `judge_character_cant_move()`：助理、跟随、移动限制
- `judge_same_position_npc_follow()`：玩家移动时同场景跟随
- `select_random_free_character()`：随机空闲角色

目标数据：`data/target/default/target.csv` + `effect.csv`（构建为 `data.json` 中 `Target`/`TargetEffect` 表）。

### 16.2 H 相关 NPC AI

`Script/Design/handle_npc_ai_in_h.py`：
- 无意识/睡奸/醉奸/猥亵状态处理
- `handle_unconscious_h_response()`：无意识H被打断后按目标本人裁决响应并完成对应收尾
- `npc_active_h()` / `npc_ai_in_group_sex()`：NPC 主动 H 与群交 AI
- 醒来/恢复意识结算、精液与服装结算、身体部位偏好

### 16.3 状态机

- 调度：`Script/Design/handle_state_machine.py`
- 原子动作：`Script/StateMachine/default.py` 注册 175 个函数
- 内容以 `general_movement_module()` 和各具体移动/等待动作（等待 5/10/30 分钟、回宿舍、去博士办公室、去厕所、去厨房、去食堂、去图书馆、去酒吧等）为主

---

## 17. 时间、地图与导航

### 17.1 时间

`Script/Design/game_time.py`：
- `init_time()` 从 config.ini 起始日期创建 `cache.game_time`
- 加减时间、日期差、星期、月份文本
- 天文计算：太阳时段/节气（`get_solar_period`, `get_sun_phase_for_sun_az`, 依赖 pyephem），月相（`get_moon_phase`），供游戏内时间系统使用
- 工作/娱乐时间判断

### 17.2 地图与导航

`Script/Design/map_handle.py`：
- 路径转换（系统路径 `["中枢","博士办公室"]` 与字符串）
- 同图/跨图移动（`identical_map_move` / `difference_map_move`）
- 寻路：`map_config` 在加载地图时用 `Script/Core/dijkstra.py` 预计算各节点最短路存入 `Map.sorted_path`；运行时由 `map_handle.get_path_finding()` 直接查询
- 场景可达性、门/锁判定、场景内角色列表、场景满员
- 导航面板：`Script/UI/Panel/navigation_panel.py`、`see_map_panel.py`

---

## 18. 子系统清单

> 每个系统均有对应文档；代码文件为该系统主要实现，可能与其他面板/结算模块交叉。

### 18.1 罗德岛经营

| 系统 | 核心文件 | 主要数据 |
| --- | --- | --- |
| 基地/基建管理 | `Design/basement.py`, `UI/Panel/building_panel.py`, `manage_basement_panel.py` | `Facility*.csv` |
| 动力/能源 | `UI/Panel/manage_power_system_panel.py` | `Power_Generation.csv`, `Power_Storage.csv` |
| 农业生产 | `UI/Panel/agriculture_production_panel.py`, `Design/basement.py` | 农场设施 |
| 工业生产/流水线 | `UI/Panel/manage_assembly_line_panel.py` | `ProductFormula.csv` |
| 资源交易 | `UI/Panel/resource_exchange_panel.py` | `Resource.csv`, `Restaurant.csv` |
| 装备维护 | `UI/Panel/equipmen_panel.py` | `Equipment_*` 系列 |
| 载具管理 | `UI/Panel/manage_vehicle_panel.py` | `Vehicle.csv` |
| 宿舍管理 | `System/Dormitory_System/*` | 宿舍场景地图 |
| 医疗经营 | `System/Medical_System/*` | `Medical_*` 系列 |
| 外勤委托 | `System/Field_Commission_System/*` | `Commission.csv` |
| 招募 | `UI/Panel/recruit_panel.py` | `Recruitment_Strategy.csv` |
| 邀请访客 | `UI/Panel/invite_visitor_panel.py` | 访客设施 |
| 势力外交 | `UI/Panel/nation_diplomacy_panel.py` | `Nation.csv`, `Diplomatic_Policy.csv` |
| 助理 | `UI/Panel/assistant_panel.py` | `AssistantServices.csv` |
| 全干员位置/召集 | `UI/Panel/all_npc_position_panel.py` | 角色位置 |

### 18.2 角色养成与状态

| 系统 | 核心文件 | 说明 |
| --- | --- | --- |
| 能力升级 | `UI/Panel/ability_up_panel.py` | `AbilityUp.csv` |
| 素质/天赋 | `Design/handle_talent.py`, `UI/Panel/talent_up_panel.py` | `Talent*.csv` |
| 属性查看 | `UI/Panel/see_character_info_panel.py` | 多页角色面板 |
| 服装/脱衣/换装 | `Design/clothing.py`, `UI/Panel/cloth_panel.py` | `Clothing*.csv` |
| 衣柜检查 | `UI/Panel/check_locker_panel.py` | 衣柜偷取等 |
| 收藏品 | `UI/Panel/collection_panel.py` | `Collection_bouns.csv` |
| 成就/蚀刻章 | `UI/Panel/achievement_panel.py` | `Achievement.csv` |
| 身体信息 | `UI/Panel/body_info_panel.py`, `dirty_panel.py` | `BodyPart.csv` |
| 射精面板 | `UI/Panel/ejaculation_panel.py` | `Semen_Shoot_Amount.csv` |
| 妊娠/婴儿 | `Design/pregnancy.py`, `UI/Panel/sp_event_panel.py`, `get_up_panel.py` | 怀孕状态、孩子出生 |
| 身体检查与管理 | `UI/Panel/physical_check_and_manage.py` | `Physical_Exam_Setting.csv` |
| 读书/图书馆 | `UI/Panel/borrow_book_panel.py`, `read_book_panel.py`, `manage_library.py` | `Book*.csv` |
| 五子棋 | `UI/Panel/play_gomoku_panel.py` | 娱乐小游戏 |

### 18.3 烹饪与物品

| 系统 | 核心文件 | 说明 |
| --- | --- | --- |
| 烹饪/食谱 | `System/Cooking_System/cooking.py` | `Recipes.csv`, `Seasoning.csv` |
| 制作食物 | `System/Cooking_System/make_food_panel.py` | 批量制作 |
| 食物商店 | `UI/Panel/food_shop_panel.py` | `Restaurant.csv` |
| 食物背包/进食 | `System/Cooking_System/food_bag_panel.py` | 饮用类独立、尿意结算 |
| 烹饪题库 | `data/csv/cook_question/*.csv` | 140 张题目表 -> `Cook_Question.json` |
| 道具背包 | `UI/Panel/see_item_info_panel.py` | `Item.csv` |
| 成人用品商店 | `UI/Panel/h_item_shop_panel.py` | H 道具 |
| 礼物 | `UI/Panel/gift_panel.py` | `Gift_Items.csv` |
| 香薰疗愈 | `UI/Panel/aromatherapy_panel.py` | `Aromatherapy_Recipes.csv` |
| 泡咖啡（加料） | 面板 ID `MAKE_COFFEE_ADD=60` | 咖啡与特殊调料 |
| 调酒 | 面板 ID `MIXOLOGY=66` | 酒类系统 |

### 18.4 源石技艺 / 特殊能力

| 系统 | 核心文件 | 说明 |
| --- | --- | --- |
| 源石技艺 | `UI/Panel/originium_arts.py` | 催眠/透视/激素/时停等技艺 |
| 催眠 | `UI/Panel/hypnosis_panel.py`, `Design/hypnosis_state.py` | `Hypnosis_*` 系列 |
| 时间停止 | `Design/…` + 主循环特殊处理 | `cache.time_stop_mode` |
| 醉酒/醉奸 | `Sex_System/drunk_sex_common.py` | `Alcohol_Level.csv`, `Drunk_Level.csv` |

### 18.5 特殊 H 系统

| 系统 | 核心文件 | 说明 |
| --- | --- | --- |
| 群交 | `System/Sex_System/group_sex_panel.py` | 模板编辑、群体结算 |
| 隐奸 | `System/Sex_System/hidden_sex_panel.py` | 隐蔽值/发现度 |
| 露出 | `System/Sex_System/exhibitionism_sex_panel.py` | 露出 H |
| 绳艺 | `System/Sex_System/bondage_panel.py` | `Bondage.csv` |
| 监禁调教 | `UI/Panel/confinement_and_training.py` | 关押区、监狱长 |
| 睡眠/无意识 | `UI/Panel/sleep_panel.py`, `handle_npc_ai_in_h.py` | 睡奸/无意识 H |
| 性爱姿势 | `System/Sex_System/sex_position_panel.py` | `Sex_Position.csv` |
| H 被发现 | `System/Sex_System/sex_be_discovered_panel.py` | 目击/逃走 |

### 18.6 系统/UI 功能

| 系统 | 核心文件 | 说明 |
| --- | --- | --- |
| PRTS 教程 | `UI/Panel/prts_panel.py` | `Prts.csv`, `Tip*.csv` |
| 系统设置 | `UI/Panel/system_setting.py` | `System_Setting.csv` |
| AI 设置 | `UI/Panel/chat_ai_setting.py` | `Ai_Chat_Setting.csv` |
| 存档面板 | `UI/Panel/see_save_info_panel.py` | 存档选择/信息 |
| 日记 | `UI/Panel/diary_panel.py` | 游戏记录 |
| Mod 面板 | `UI/Panel/mod_panel.py` | Mod 管理 |
| 角色图片列表 | `UI/Panel/chara_image_list_panel.py` | 图片查看 |
| 通用 NPC 选择 | `UI/Panel/common_select_NPC.py` | 跨面板复用 |

---

## 19. UI 体系与双渲染模式

### 19.1 抽象绘制层

`Script/UI/Moudle/draw.py` 提供所有 UI 组件基类：

- 文本：`NormalDraw`, `FullDraw`, `WaitDraw`, `LineFeedWaitDraw`, `CenterDraw`, `RightDraw`, `LeftDraw`, `CenterMergeDraw`, `LeftMergeDraw`, `ExpLevelDraw`, `StatusLevelDraw`
- 图形：`ImageDraw`, `BarDraw`, `CharaDraw`, `InfoBarDraw`, `InfoCharaDraw`
- 按钮：`Button`, `ImageButton`, `CenterButton`, `LeftButton`
- 分隔线/标题：`LineDraw`, `TitleLineDraw`, `LittleTitleLineDraw`

`Script/UI/Moudle/panel.py` 提供通用面板构建块（单选列表、消息+按钮、分页面板等）。

### 19.2 Tk 模式（`web_draw=0`）

- `Script/Core/io_init.py`：`era_print()`, `clear_screen()`, 命令绑定/输入事件，所有输出直接写入 Tk 文本组件
- `Script/Core/flow_handle.py`：`askfor_all/askfor_str/askfor_int/askfor_wait`、命令处理
- `Script/Core/main_frame.py`：主窗口与事件总线
- 启动时有文本度量预热（`warm_up_text_metrics`）；`perf_monitor=1` 时启用性能埋点

### 19.3 Web 模式（`web_draw=1`）

- 服务器：`Script/Core/web_server.py`（Flask-SocketIO）
- IO 适配：`Script/Core/io_web.py` 把输出转成元素字典追加到 `cache.current_draw_elements`，并通过 `update_game_state()` 批量下发
- 流程：`Script/Core/flow_handle_web.py`（轮询 API 响应、`PanelChangeException` 面板切换）
- 绘制适配：`Script/System/Web_Draw_System/web_draw_adapter.py::apply_web_adapters()` 给绘制类打补丁
- 专用渲染器：`scene_renderer.py`, `character_renderer.py`, `dialog_box.py`, `status_panel.py`, `tab_menu.py`, `interaction_handler.py`, `settlement_manager.py`, `image_processor.py`, `body_part_button.py`, `body_analysis_ensemble.py`
- 前端：`templates/index.html`, `static/game.js`, `static/js/*`, `static/css/style.css`, 字体
- 端口：5000 起自动寻找空端口（最多尝试 50 次）
- API：REST `/api/*` + SocketIO 事件（见 §20）

### 19.4 Web 服务器 API 摘要

REST：
- `GET /` 首页
- `GET /api/get_state` 游戏状态
- `POST /api/button_click`, `/api/wait_response`, `/api/skip_wait`, `/api/string_input`, `/api/integer_input`
- 切换开关：`toggle_extra_info_section`, `toggle_detailed_dirty`, `toggle_all_body_parts`, `quick_use_drug`, `toggle_cloth`
- 图片：`/api/get_image_paths`, `/image/<path>`, `/api/cropped_image/<path>`, `/api/avatar_image/<name>`
- 字体：`/api/get_font_config`

SocketIO 事件（后端处理函数）：
- 连接/状态：`connect`, `disconnect`, `refresh_state`, `request_game_state`
- 交互选择：`select_interaction_type`, `click_body_part`, `select_major_type`, `select_minor_type`, `clear_interaction_selection`
- 指令/目标：`execute_instruct`, `switch_target`, `get_panel_instructs`, `get_interaction_types`, `get_major_types`
- 药物/道具：`get_drug_list`, `get_item_list`, `select_drug`, `select_item`
- 场景/对话：`get_all_scene_characters`, `get_interaction_state`, `advance_dialog`, `skip_all_dialogs`, `get_character_dialog`
- 事件/结算：`event_option_selected`, `settlement_button_selected`, `get_settlement_state`

### 19.5 面板注册与切换

- `constant.Panel` 定义面板 ID（TITLE=0 … MIXOLOGY=66）
- `UI/Flow/normal_flow.py` 用 `@handle_panel.add_panel(constant.Panel.X)` 注册面板函数
- `start_flow.start_frame()` 主循环执行 `constant.panel_data[cache.now_panel_id]()`
- 面板通过设置 `cache.now_panel_id` 切换；Web 模式抛出 `PanelChangeException` 实现子面板/主面板切换

---

## 20. 存档系统

- 核心：`Script/Core/save_handle.py`
- 存储：`save/{save_id}/0`（头部信息，pickle）+ `save/{save_id}/1`（完整游戏数据，pickle）
- 头部信息含 `game_verson`；读取时执行大量跨版本兼容更新（`input_load_save`, `update_dict_with_default`, `recursive_update`, `update_map`, `update_settings` 等）
- 自动存档：玩家睡觉结算完毕后 `sleep_settle.update_save()` 写入 `auto` 档；输入 `999` 退出游戏时也会保存 `auto` 档；运行出错时自动保存 99 号档
- 存档配置：`max_save=100`, `save_page=10`
- 存档面板：`UI/Panel/see_save_info_panel.py`
- 跨版本兼容关键点：旧整数行为 ID -> 字符串常量、新增角色补全、口上版本、角色收藏品扩展、设施/资源检测

多周目：
- `New_Round_Inherit.csv` 定义继承项；`UI/Flow/creator_character_flow.py` 处理角色创建与多周目开局
- 继承内容包括点数花费、好感信赖、催眠进度等（详见工作流文档）

---

## 21. Mod 系统

- 核心：`Script/Core/mod_manager.py`（`ModInfo` / `ModManager`）
- 启动：`game.py` 调用 `init_mod_system()`；失败仅告警
- 配置：`mod/mod_config.json`（`enabled_mods`, `load_order`）
- `mod_info.json` 能力：
  - `dependencies`, `incompatible`, `load_priority`
  - `scripts[].functions[]`：`type=replace` 函数替换（保留原函数 `call_original`）或 `type=new` 注册新函数
  - `assets.data[]`：CSV 覆盖（`type=csv`）；`assets.image[]`：图片覆盖
- 脚本环境自动注入：`cache`, `game_config`, `game_type`, `_`, `get_mod_asset`, `call_original`
- 示例 Mod：`mod/semen_boost/`（替换 `ejaculation_panel.common_ejaculation` + 覆盖 `Semen_Shoot_Amount.csv`）
- 游戏内面板：`UI/Panel/mod_panel.py`

---

## 22. AI 文本生成

- 核心：`Script/Design/handle_chat_ai.py`（966 行）
- 入口：`judge_use_text_ai(character_id, behavior_id, original_text, translator, direct_mode)`；未开启或条件不满足时原样返回
- 支持 OpenAI 兼容接口（含 DeepSeek）与 Google Gemini
- 系统提示词：`data/ui_text/text_ai_system_promote.csv`
- 发送数据配置：`data/csv/Ai_Chat_Send_Data.csv`（25 条）；AI 设置：`data/csv/Ai_Chat_Setting.csv`
- API 密钥：根目录 `ai_chat_api_key.csv`（`GEMINI_API_KEY` / `DEEPSEEK_API_KEY`），敏感文件，勿提交
- 功能：口上/地文生成、翻译模式、直接聊天、流式响应处理；生成记录可保存（`data/talk/ai/`）
- 工具与提示词：`tools/AI/`（生成要求、模板、AI 工作流 agent 文件）

---

## 23. ArkEditor 与工具

### 23.1 ArkEditor（`tools/ArkEditor/`）

- 独立 PySide6 图形编辑器，打包为 `erArkEditor.zip`；入口 `main.py`
- 编辑对象：角色属性 CSV、口上 CSV、事件 JSON、外勤委托 CSV
- 核心 UI：`ui/data_list.py`, `ui/item_text_edit.py`, `ui/premise_menu.py`, `ui/effect_menu.py`, `ui/CVP_menu.py`, `ui/CVE_menu.py`, `ui/CSE_menu.py`, `ui/commission_edit.py`
- 自带 CSV 参考表：`csv/Premise.csv`（前提）、`csv/Effect.csv`（结算）、`csv/Behavior_Data.csv`（行为）等
- 教程/模板在 `example/` 目录

### 23.2 其他工具（`tools/`）

- `ai_text_all_to_one.py`：AI 文本合并
- `arknights_story_downloader.py`、`download_prts_*.py`：PRTS 剧情/背景/角色图抓取
- `compare_old_and_new_po.py`：PO 对比
- `csv_renumber.py`、`update_behavior.py`、`body_part_editor.py`：CSV 数据维护
- `MCP/`：PRTS 干员资源下载 MCP 服务
- `backup/`：历史一次性处理脚本
- `profiling/`：循环统计、渲染基准、UI 性能补丁

---

## 24. 本地化

- 机制：Python gettext；翻译函数 `get_text._`
- 语言目录：`data/po/<lang>/LC_MESSAGES/`
- 现有语言：`zh_CN`（源语言 PO 模板）、`en_US`（talk/csv/py 三域 + MO）、`ko_KR`（三域 + MO）
- 切换：`config.ini -> language`
- 构建：
  1. `buildconfig.py` 同步生成 zh_CN 源 PO
  2. `buildpo.py` 从 `.py` 提取生成 `erArk_py.po`
  3. `buildmo.py` 将 en_US 的 `erArk_talk/csv/py` 编译为 MO
- CSV 中第 4 行 `get_text` 列标记哪些列需要翻译；JSON 的 `gettext` 字典保存标记

---

## 25. CI/CD 发布结构

GitHub Actions `.github/workflows/python-app.yml`（push/PR 到 master，windows-latest）：

1. Python 3.12 + 依赖 + PyInstaller 打包 `game.py`（`-F`，隐藏导入 `engineio.async_drivers.threading`）
2. `buildconfig.py` 构建数据
3. `init_data.py` 预热缓存
4. 复制游戏文件（data/config/image/update.log/example/static/templates/mod 等）
5. 打包四个产物：
   - `erArk_{版本}.zip`：完整游戏包
   - `erArk_Lite_{版本}.zip`：轻量版（移除 `image/场景`、`image/断面图`、`image/立绘`，仅保留基础场景）
   - `erArk_Images_{图片版本}.zip`：图片资源包
   - `erArkEditor.zip`：口上/事件编辑器（附教程、模板和参考 CSV）
6. 版本号：游戏 `package.json`，图片 `image/package.json`
7. 另有 `sync-wiki.yml` 同步 wiki

轻量版 + 图片资源包 = 完整版。

---

## 26. 开发规范与约定

- 注释和文档使用中文
- 每个函数必须有中文文档字符串：输入参数与类型、返回值与类型、功能说明
- 每小段代码需有注释说明作用
- 格式化：Black，行宽 200
- 不得手改生成文件：`data/*.json`、`Script/Config/config_def.py`、`.mo`、地图 pickle
- 修改 CSV/口上/事件/角色后必须运行构建（或直接运行 `game.py` 触发增量构建）
- UI 输出统一走抽象 draw 类或 `era_print`，不要直接操作 Tk/HTML；新 UI 需双模式验证
- 新增指令/行为/事件时，同时检查前提、结算、显示三层面
- 主循环中避免磁盘 IO；注意输出积压与渲染性能
- `ai_chat_api_key.csv` 敏感，不要提交真实密钥
- 提交 PR 到 `master` 分支

---

## 27. 常见任务工作流

### 27.1 新增/修改一张配置表

1. 编辑 `data/csv/xxx.csv`（注意 5 行表头与类型行）
2. `python buildconfig.py` 全量重建（或 `python game.py` 增量）
3. 在逻辑中通过 `game_config.config_xxx` 使用
4. 若新增表：确认 `config_def.py` 生成类并在 `game_config.init()` 加载/索引（复杂表需加加载代码）

### 27.2 新增一个指令

1. 在 `InstructConfig.csv` 增加行（行为 ID、前提集、Web 分类、身体部位等）
2. 在 `Script/System/Instruct_System/handle_instruct.py` 用 `@add_instruct` 写处理函数
3. 确保关联 `behavior_id` 在 `Behavior_Data.csv` / `Behavior_Effect.csv` 有结算配置
4. 重跑构建，双模式验证显示与执行

### 27.3 新增一个结算效果

1. 在 `constant_effect.py` 加效果 ID 常量（命名按现有分类）
2. 在 `Settle/default.py`（一段，`@settle_behavior.add_settle_behavior_effect`）或 `Second_effect.py`（二段，`@settle_behavior.add_settle_second_behavior_effect`）注册实现函数
3. 在 `Behavior_Effect.csv` 给行为绑定效果 ID
4. 重跑构建并验证

### 27.4 新增一个前提

1. 在 `constant_promise.py` 的 `Premise` 类加前提 ID
2. 在 `Design/handle_premise/` 对应主题模块用 `@add_premise` 实现（或使用 `buildata.py` 生成样板）
3. 在口上/事件/指令 CSV 的前提串中引用
4. 重跑构建

### 27.5 新增角色

1. 添加 `data/character/{AdvNpc}_{名字}.csv`（复制模板改字段）
2. 可选：添加 `data/talk/chara/` 口上、`data/event/chara/` 事件、`image/立绘/` 图片
3. 重跑 `buildconfig.py`
4. 确认 `constant.first_NPC_name_set` / `ban_NPC_name_set` 是否符合预期

### 27.6 新增 UI 面板

1. 在 `constant/__init__.py` 的 `Panel` 类加面板 ID
2. 在 `Script/UI/Panel/` 新建面板，使用抽象 draw 类
3. 在 `UI/Flow/normal_flow.py` 用 `@handle_panel.add_panel` 注册
4. Tk + Web 双模式验证（Web 特殊交互可能需要扩展 `Web_Draw_System` 与 `static/game.js`）

### 27.7 本地化

1. 修改源文本或翻译 PO
2. `python buildpo.py`（若源码文本变化）
3. `python buildmo.py`
4. 检查 `config.ini -> language`

### 27.8 性能排查

- Tk 卡顿：`config.ini -> perf_monitor=1`，查看 `profiling` 补丁与输出
- Web 输出积压：确认 `clear_screen()` 时机、元素历史长度
- 数据异常：确认是否漏跑构建

---

## 28. 重要陷阱与注意事项

1. **增量构建陷阱**：`game.py` 自动构建会跳过已有口上 JSON；口上 CSV 改动后若发现不生效，请跑 `python buildconfig.py` 全量重建。
2. **config_def.py 边界**：`auto_build_config` 不重写它；新 CSV 列必须全量构建才会出现在 Python 类中。
3. **生成 JSON 被 gitignore**：`data/*.json` 不入库；clone 后首次运行构建。
4. **地图预处理**：`data/MapData/SceneData/PlaceData/ScenePath` 是生成 pickle/JSON；地图改了需要删除或重建这些缓存（`map_config` 仅在文件不存在时解析原始地图目录）。
5. **口上/事件前提串**：ID 必须与 `constant_promise.Premise` 一致，否则会被静默忽略或报错。
6. **行为 ID 字符串化**：旧代码/旧存档用整数，新代码用字符串；跨版本兼容逻辑在存档读取中处理。
7. **Web 模式线程模型**：指令执行与 SocketIO 处理有专门的线程/执行中标志（`web_instruct_executing*`），避免在任意线程直接调用游戏循环。
8. **端口**：Web 默认 5000，自动找空端口，不要硬编码。
9. **Tk 仅在 Windows 官方支持**；Web 模式用于跨设备。
10. **敏感数据**：`ai_chat_api_key.csv` 不可提交。
11. **R18 内容**：所有涉及敏感内容的文本仍需保留在数据和口上系统中，代码审查/生成内容时注意合规。

---

## 29. 关键文件索引（查找问题时的优先级）

| 问题类型 | 先看 |
| --- | --- |
| 游戏启动失败/初始化 | `game.py`, `Script/Core/game_init.py`, `Script/Config/*` |
| 配置字段/枚举缺失 | `Script/Config/config_def.py`, `data/data.json`, `buildconfig.py` |
| 指令不显示/不能点 | `Script/System/Instruct_System/handle_instruct.py`, `instruct_filter_panel.py`, `handle_premise` |
| 行为不结算/数值错误 | `Script/Design/settle_behavior.py`, `Script/Settle/default.py`, `Second_effect.py`, `Behavior_Effect.csv` |
| NPC 行为异常 | `Script/Design/handle_npc_ai.py`, `StateMachine/default.py`, `data/target/default` |
| 口上不触发/选错 | `Script/Design/talk.py`, `Character_Talk.json`, `Talk_Common.json` |
| 事件不触发 | `Script/Design/event.py`, `data/event` |
| 地图/寻路错误 | `Script/Design/map_handle.py`, `map_config.py`, `data/map` |
| 时间/月相/节气 | `Script/Design/game_time.py` |
| 存档兼容/损坏 | `Script/Core/save_handle.py` |
| Mod 不生效 | `Script/Core/mod_manager.py`, `mod/*` |
| AI 文本不生成 | `Script/Design/handle_chat_ai.py`, `ai_chat_api_key.csv`, `Ai_Chat_Setting.csv` |
| Tk 渲染/输入 | `Script/Core/io_init.py`, `flow_handle.py`, `main_frame.py`, `UI/Moudle/draw.py` |
| Web 模式不显示/交互异常 | `Script/Core/web_server.py`, `io_web.py`, `flow_handle_web.py`, `System/Web_Draw_System/*` |
| 编辑器问题 | `tools/ArkEditor/main.py`, `load_csv.py`, `ui/*` |

---

## 30. 文档导航

### 30.1 仓库根文档

- `CLAUDE_cn.md`：中文 AI 指导（最详细的一页式架构说明）
- `CLAUDE.md`：英文 AI 指导
- `.github/copilot-instructions.md`：AI 代理最小必读速查
- `README.md` / `README_en.md`：玩家向 README
- `update.log`：版本更新日志
- `todo list.txt`：作者待办与未实装系统规划

### 30.2 `.github/prompts/数据处理工作流/`（60 个文档）

核心架构：
`角色行为系统`, `前提系统`, `结算系统`, `口上系统`, `事件系统`, `通用结算函数函数`, `CSV数据加载机制说明`, `多周目结算与继承系统`

绘制/UI：
`Tk绘制模式`, `Web绘制模式`, `主场景互动界面`, `指令面板系统`, `通用NPC选择面板`, `系统设置系统`, `全干员位置面板`, `PRTS系统`

地图：
`地图系统`, `导航系统`

角色/外观/身体：
`角色创建流程`, `能力升级面板`, `成就系统`, `服装系统说明`, `衣柜检查功能`, `收藏品系统`, `角色图片系统`, `身体信息面板系统`, `射精面板系统`, `妊娠系统`

罗德岛部门/经营：
`管理罗德岛系统`, `助理系统`, `基建系统`, `动力系统`, `农业生产系统`, `工业生产系统`, `装备维护系统`, `医疗经营系统`, `资源交易系统`, `招募系统`, `外勤委托系统`, `邀请访客系统`, `势力外交系统`, `载具管理系统`, `读书系统`, `身体检查与管理系统`

物品：
`道具背包系统`, `礼物系统`, `食物系统`

特殊能力/H：
`源石技艺系统`, `时间停止系统`, `催眠系统`, `群交系统`, `监禁调教系统`, `睡眠系统`, `隐奸系统`

工作流：
`AI文本生成系统`, `ArkEditor编辑器系统说明`, `存档系统`, `剧情总结工作流`, `剧情转外勤委托工作流`

### 30.3 `Script/System/*` 内设计文档

- `Cooking_System/烹饪系统说明文档.md`
- `Dormitory_System/宿舍管理系统设计文档.md`, `实现步骤.md`
- `Field_Commission_System/外勤委托系统.md`, `剧情总结工作流.md`, `剧情转外勤委托工作流.md`
- `Instruct_System/指令系统整体逻辑.md`, `TK模式指令面板绘制.md`, `Web模式指令面板绘制.md`, `指令分类映射表.md`
- `Medical_System/医疗经营系统.md`, `医疗经营系统实现流程.md`
- `Sex_System/drunk_sex_plan.md`
- `Web_Draw_System/Web绘制模式UI重构说明文档.md`, `Web绘制模式UI重构实现流程.md`

### 30.4 其他 `.github/prompts/` 内容资产

- `基础/`：常用地点、种族等指令前提分支提示词
- `H方式/`：按 H 方式（群交、隐奸、露出、催眠、监禁、时停、角色扮演等）拆分的前提分支提示词
- `其他差分/`：礼物、药剂、食物加料、香薰疗愈等前提分支提示词
- `AI文本生成工作流/`：AI 批量生成口上/地文的工作流与目标文件
- `复数文本技能生成提示词/`：复数文本技能生成模板

---

## 31. 文档维护说明

- 本文件定位：仓库级“完整描述”，不是生成文件，可随代码更新持续修订。
- 更新建议：每次大版本（如 0.66 -> 0.67）同步更新“当前版本/规模快照/新增子系统/关键文件索引”。
- 数字统计口径：Python 代码行为含空行与注释；口上条数来自构建 JSON；如精确数字对任务重要，以实际文件为准。
- 与 `CLAUDE_cn.md` 冲突时：优先相信代码与最近更新的本文档；本文档生成时间晚于 CLAUDE 文件时以本文档为准。
