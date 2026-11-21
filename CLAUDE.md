# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在本仓库中工作时提供指导。它只有这一个中文版本：原先的英文版与 `CLAUDE_cn.md` 已合并到这里，不要再另建其他语言的副本。

## 项目概述

erArk 是一个以明日方舟角色为题材的 R18 成人游戏，使用 Python 3.12 开发。这是一个基于文本的模拟游戏，包含角色互动、事件和各种游戏系统。

## 核心开发命令

下面命令里的 `python` 指项目用的 Python 3.12 解释器。维护者本机用的是仓库根目录的 conda 环境（`.conda\python.exe`），那台机器上裸 `python` 是 Windows 商店的空壳别名，不能用。

### 运行游戏
```bash
python game.py
```
`game.py` 启动时会导入 `auto_build_config.py`，对游戏数据进行**增量**重建（当 `data/Character_Talk.json` / `data/Talk_Common.json` 已存在时会跳过口上数据）。因此对大多数 CSV 修改，直接运行游戏即可。

### 构建游戏数据
```bash
python buildconfig.py  # 全量重建：CSV 配置 -> JSON 数据 + config_def.py + zh_CN 的 PO 文件
python init_data.py    # 预热运行时缓存（CI 在 buildconfig 之后运行）
python buildpo.py      # 从 .py 文件提取可翻译字符串，生成 zh_CN 的 erArk_py.po（依赖 GNU gettext 的 xgettext）
python buildmo.py      # 把 zh_CN 以外每种语言的全部 PO 编译成 MO（优先用 msgfmt，没有时改用 polib）
```
注意：
- `buildata.py` 虽然名字相似，但**不属于**数据构建链——它是开发者辅助工具，用于生成前提/结算的样板代码（向 `constant_promise` / `handle_premise` 中插入常量，并通过其 `mode` 变量在前提、结算定义与 CSV 之间互相转换）。
- `buildconfig.py`（以及启动时的增量构建）会整份重写 `data/po/zh_CN/LC_MESSAGES/` 下由数据生成的 PO（`erArk_csv.po`、`erArk_talk.po` 等）。提交前用 `git diff --stat` 看一眼；不打算提交翻译原文的变化时，用 `git checkout -- data/po/` 还原（先确认里面没有自己未提交的改动）。
- `buildpo.py` 一进门就删除 `erArk_py.po`，再靠 `xgettext` 重建：机器上没有 `xgettext` 时文件删掉了却建不回来，脚本报错中止，要用 `git checkout` 恢复。
- `buildmo.py` 在任何一个 PO 编译失败时以退出码 1 结束，失败的 PO 不会留下写了一半的 MO；`--out DIR` 可以把 MO 写到别处先核对。

### 安装依赖
```bash
pip install -r requirements.txt
```
关键依赖：`PySide6`（ArkEditor 图形界面）、`flask` + `flask-socketio` + `python-socketio`（Web 模式服务器）、`openai` + `google-genai`（AI 文本生成），以及 `Pillow`、`numpy`、`ephem`、`psutil`、`wcwidth`。`ruff`（静态检查）、`pyinstaller`（打包）、`polib`（编译 MO 的后备）都故意不在 `requirements.txt` 里。

### 测试
游戏使用调试模式（在 `config.ini` 中配置）进行测试。设置 `debug = 1` 启用调试功能。

无头回归测试在 `tools/tests/` 下，每个套件一个目录：
- `core/`：基础系统。配置交叉引用、前提与结算的注册表及冒烟、地图寻路与游戏时钟、医疗、资源交易、食物商店、跨日与睡眠结算、存读档与旧档兼容、Web 模式的文字输入、自动挑选行为时的处女过滤、异常状态位、地图预处理文件的语言标记、英文 / 韩文 / 中文三种语言下各跑一遍的多语言检查、翻译文件（PO 与 MO）的一致性，以及逐节锁定已修 BUG 的 `test_regression_misc.py`
- `education/`：生长养成系统

```bash
.conda\python.exe tools/tests/run_all.py                    # 全部套件
.conda\python.exe tools/tests/run_all.py core               # 只跑「套件/文件名」里含关键字的
.conda\python.exe tools/tests/run_all.py core/test_medical  # 只跑一个文件
```
每个 `test_*.py` 各起一个进程。各套件共用 `tools/tests/headless_base.py`（初始化链、UI 桩、`check / section / finish`、`make_character`）；环境变量 `ERARK_TEST_LANGUAGE`（`en_US` / `ko_KR` / `zh_CN`）让该进程的游戏在指定语言下启动。修完 BUG 的惯例是在对应套件里补一条锁定断言，并确认它在修复前的代码上会失败。写新测试见 `tools/tests/README.md` 与 skill `headless-game-test`。

CI 在每次推送和每个 PR 上运行这些测试，外加一项范围很窄的静态检查。本机复现静态检查：先把 CI 固定的版本（见 `.github/workflows/python-app.yml` 里的 `pip install ruff==...` 一行，目前是 0.17.5）装进项目环境，再在仓库根目录运行：
```bash
.conda\python.exe -m pip install ruff==0.17.5   # 只需一次；CI 的固定版本变了就用新版本重装
.conda\python.exe -m ruff check --config ruff.toml .
```
必须带 `--config ruff.toml`：ruff 默认按「离文件最近的配置」生效，子目录里放一份配置就会盖过根目录的规则（CI 出于同样的原因强制使用根目录这一份）。`ruff.toml` 的规则只收「几乎一定是 BUG」的几类——语法错误、未定义的名字、格式化占位符与参数对不上、字典里重复的键——不收风格类。

## 高层架构

### 核心游戏流程
1. **入口点**：`game.py` - 自动构建配置数据（`auto_build_config`），初始化缓存和配置，加载 Mod 系统（`init_mod_system()`），然后根据 `config.ini` 中的 `web_draw` 启动 Tkinter GUI（`game_init.run(start_flow.start_frame)`）或 Web 服务器
2. **游戏初始化**：`Script/Core/game_init.py` - 设置游戏环境、样式和主流程
3. **主框架循环**：`Script/Design/start_flow.py` - 包含 UI 处理和面板管理
4. **主行为循环**：`Script/Design/character_behavior.py` - 实际的游戏模拟循环

### Script 目录结构
- **`Script/Config`** - 配置加载（`game_config.py`、`map_config.py`、`character_config.py`、`normal_config.py`）以及自动生成的 `config_def.py`
- **`Script/Core`** - 引擎层：缓存（`cache_control.py`）、存档（`save_handle.py`）、Tk/Web 的 IO（`io_init.py` / `io_web.py`）、流程处理（`flow_handle.py` / `flow_handle_web.py`）、Web 服务器（`web_server.py`）、Mod 管理器（`mod_manager.py`）、游戏数据类型（`game_type.py`）、翻译入口（`get_text.py`）、常量（`constant/` 包与 `constant_promise.py` / `constant_effect.py`）、同名图片的取舍规则（`image_path_index.py`）、Tk 渲染性能埋点（`perf_hook.py`）
- **`Script/Design`** - 主要游戏逻辑：行为循环、NPC AI、地图/导航、口上、结算分发（`settle_behavior.py`）、二段行为（`second_behavior.py`）、破处类行为的处女判定（`virgin_break_gate.py`）、催眠行为模式的清理（`hypnosis_state.py`）、Web 模式交互类型管理（`web_interaction_manager.py`）等
  - **`Script/Design/handle_premise/`** - 前提（条件判定）系统是一个包，按主题拆分为约 20 个模块（`handle_premise_H.py`、`handle_premise_place.py`、`handle_premise_ability.py`、`handle_premise_talent.py` 等），主入口在 `__init__.py`
- **`Script/Settle`** - 结算模块：`default.py`、`common_default.py`（通用结算）、`Second_effect.py`（二段效果）、`default_cloth.py`、`item_effect.py`、`orgasm_settle.py`（绝顶结算）、`realtime_settle.py`、`past_day_settle.py`、`sleep_settle.py`
- **`Script/StateMachine`** - NPC 行为原子模块（`default.py`，如移动），由 `Script/Design/handle_state_machine.py` 调度执行
- **`Script/System`** - 自成一体的子系统，多数目录内附带自己的设计文档（`.md`）：`Cooking_System`（烹饪）、`Dormitory_System`（宿舍）、`Education_System`（教育与养成：课表、上课、成长）、`Field_Commission_System`（外勤委托）、`First_Record_System`（性行为履历与面板）、`Instruct_System`（指令面板与分类）、`Item_System`（道具，含避孕套）、`Medical_System`（医疗）、`Official_Event_System`（公务事件）、`Pregnancy_System`（妊娠）、`Sex_System`（H 模式相关面板与公共函数）、`Web_Draw_System`（Web 绘制）
- **`Script/UI`** - `Flow`（标题/角色创建/常规流程）、`Moudle`（绘制/面板基础模块）、`Panel`（约 60 个功能面板）

### 关键系统

#### 配置系统
- **CSV 数据**：游戏数据存储在 `data/csv/` 下的 CSV 文件中，另有 `data/talk/`、`data/talk_common/`、`data/target/`、`data/ui_text/`、`data/event/`、`data/official_event/`、`data/character/`
- **构建过程**：`buildconfig.py`（全量）/ `auto_build_config.py`（增量，游戏启动时自动运行）读取 CSV 并生成：
  - JSON 数据文件（`data/data.json`、`Character.json`、`Character_Talk.json`、`Character_Event.json`、`Official_Event.json`、`Talk_Common.json`、`ui_text.json`、`Cook_Question.json`）
  - Python 配置定义（`Script/Config/config_def.py`，入库且 CI 会与重建结果比对，不要手改）
  - 本地化 PO 文件（`data/po/zh_CN/`）
- **地图数据**：源文件在 `data/map/`。启动时 `map_config.init_map_data()` 把它预处理成 `data/MapData`、`PlaceData`、`SceneData`、`ScenePath` 四个文件（不入库）；预处理文件里记着写出时的游戏语言，语言变了或文件不全时自动重建

#### 角色系统
- **角色模板**：以 CSV 文件形式存储在 `data/character/`
- **角色管理**：`Script/Design/character.py` 和 `character_handle.py`
- **角色行为**：`Script/Design/character_behavior.py`
- **AI 系统**：`Script/Design/handle_npc_ai.py` 和 `handle_npc_ai_in_h.py`

#### 事件与口上系统
- **事件数据**：`data/event/` 中的 JSON 文件，由 `Script/Design/event.py` 处理
- **术语**：某个角色专属的文本叫**口上**，全角色都通用的文本叫**地文**。写文档、`update.log`、提交信息和回复时按这个区分；系统名、目录名、函数名里沿用的「口上」（口上系统、`data/talk/`、`talk.py`）不改
- **文本数据**：`data/talk/` 按行为分类（`chara/` 下为各角色）存放对话 CSV，`adv_id` 不为 0 的行是该角色的口上，为 0 的行是全角色通用的地文；`data/talk_common/` 中按动作类型组织的是纸娃娃地文（`action_A`、`action_B1/B2`、`action_C1/C2`、`body`、`body_part`）
- **行为目标**：`data/target/` 存放 NPC AI 使用的目标定义，改完用 `tools/lint_target_csv.py` 校验编号
- **公务事件**：`data/official_event/*.csv`（通用、婴儿、幼女、萝莉、期末）构建成 `data/Official_Event.json`，由 `Script/System/Official_Event_System` 处理；事件表有不少静默失败的写法，每写完一批用 `tools/official_event_check.py` 校验

#### UI 系统
- **流程管理**：`Script/Core/flow_handle.py`（GUI）和 `flow_handle_web.py`（Web）
- **绘制系统**：`Script/UI/Moudle/draw.py`，Web 适配器在 `Script/System/Web_Draw_System/web_draw_adapter.py`
- **面板**：各种 UI 面板在 `Script/UI/Panel/` 以及 `Script/System/*` 各子系统内

#### 存档系统
- **存档管理**：`Script/Core/save_handle.py`
- **缓存控制**：`Script/Core/cache_control.py` 管理游戏状态
- 存档是裸 pickle，读档等于执行存档里的代码：不要加载来历不明的存档。凡是会被 pickle 进存档的字段（`game_type.py`）改动时都要考虑旧档读入后的补全，跨版本兼容见存档系统文档与 `tools/tests/core/test_save.py`

#### Mod 系统
- **管理器**：`Script/Core/mod_manager.py`（`ModInfo` / `ModManager`）；`game.py` 启动时调用 `init_mod_system()`（失败仅告警，不会中断游戏）
- **能力**：Mod 元数据（`mod_info.json`）支持依赖/不兼容声明与加载优先级；支持脚本级**函数替换**（保存原函数并注入 Mod 的新函数）以及素材覆盖（如替换某个 CSV）。Mod 脚本由管理器用 `exec` 执行，`cache`、`game_config`、`_`、`get_mod_asset` 等名字是执行前注入的
- **配置**：`mod/mod_config.json`（`enabled_mods`、`load_order`；本机生成，不入库）；示例 Mod 见 `mod/semen_boost/`；游戏内有模组面板（`Script/UI/Panel/mod_panel.py`）

#### AI 文本生成
- **核心**：`Script/Design/handle_chat_ai.py` — 支持 OpenAI 兼容接口（含 DeepSeek）和 Google Gemini；入口 `judge_use_text_ai()`，若游戏内 AI 设置未开启则原样返回文本
- **系统提示词**：`data/ui_text/text_ai_system_promote.csv`
- **API 密钥**：从仓库根目录的 `ai_chat_api_key.csv` 读取（每行一个，如 `GEMINI_API_KEY` / `DEEPSEEK_API_KEY`）——此文件属敏感内容，已被 gitignore，切勿提交真实密钥
- **工具用语料/提示词**：`tools/AI/`（本地目录，不入库）

#### 多语言
- `config.ini` 的 `language` 决定游戏语言：`zh_CN` 是原文语言，不读 MO、直接显示原文；`en_US`、`ko_KR` 由 `Script/Core/get_text.py` 从 `data/po/<语言>/LC_MESSAGES/` 读取 MO
- zh_CN 的 PO 是翻译的原文，由构建脚本生成；其他语言的 PO 经 Crowdin（`crowdin.yml`）翻译，改了 PO 要跑 `buildmo.py` 把 MO 一并更新（`core/test_translation_files.py` 会查两者是否一致）
- 游戏只翻译配置表的 `name` 列与表头标了翻译的列、角色模板的值、场景名。行为标签、委托的需求与奖励、场景路径这些给程序认的标识始终是中文原文：代码里比较这类值时直接写原文，不要拿 `_("…")` 的结果去比。只在英文 / 韩文下才出现的问题，把检查加进 `tools/tests/core/_language_checks.py`

### Web 模式
游戏支持基于 Web 的界面：
- 在 `config.ini` 中设置 `web_draw = 1` 启用
- Web 服务器（Flask-SocketIO，默认端口 5000，被占用时自动换到空闲端口）在 `Script/Core/web_server.py`；Web IO 适配器在 `Script/Core/io_web.py`；前端页面在 `templates/index.html` 与 `static/`
- 渲染子系统在 `Script/System/Web_Draw_System/`：启动时调用 `web_draw_adapter.apply_web_adapters()` 对绘制类打补丁；专用渲染器包括 `scene_renderer.py`、`character_renderer.py`、`dialog_box.py`、`status_panel.py`、`tab_menu.py`、`interaction_handler.py`、`settlement_manager.py`、`image_processor.py`

## 代码指南

1. **注释**：所有注释应使用中文
2. **函数文档**：每个函数必须有中文注释说明：
   - 输入参数和类型
   - 返回值和类型
   - 函数功能
3. **代码段**：每一小段代码都需要有注释说明其作用
4. **代码风格**：使用 Black 格式化器，行宽 200
5. **优先复用**：尽可能复用已有的代码与变量，包括模块、前提、功能、系统等；动手前先在仓库里找有没有现成的，不另写一份作用相同的
6. **优先合并为通用实现**：如果两个系统、功能或模块可以合并成一个通用的系统、功能或模块，优先采用合并后的通用方案，而不是各自保留一套

## 关键配置文件

- `config.ini`：主游戏配置（`debug`、`web_draw`、`perf_monitor`、`language`、字体、窗口尺寸、游戏内起始日期、存档槽位等）。`perf_monitor = 1` 时（仅 Tk 模式）启用渲染性能埋点，每屏耗时写成 JSONL
- `data/data.json`：从 CSV 编译的游戏数据
- `data/Character.json`：角色模板数据
- `data/Character_Talk.json` / `data/Talk_Common.json`：`data/talk/` 的口上与地文数据 / 纸娃娃地文数据
- `data/Character_Event.json` / `data/Official_Event.json`：角色事件数据与公务事件数据
- `data/ui_text.json`：界面文本数据
- `ai_chat_api_key.csv`：AI 文本生成 API 密钥（敏感文件）
- `package.json` / `image/package.json`：CI 使用的游戏版本号和图片包版本号（把 `package.json` 改成一个还没发布过的版本号就会触发发布；只由仓库所有者修改）
- `ruff.toml`：CI 静态检查的规则集（只收几乎一定是 BUG 的规则）

`data/*.json` 都是构建生成物，不入库。

## 开发工作流

1. 编辑 `data/csv/`、`data/talk/`、`data/talk_common/`、`data/ui_text/` 或 `data/character/` 中的 CSV 文件（或使用 ArkEditor 工具）
2. 运行 `python buildconfig.py` 全量重建——或直接运行 `python game.py`，启动时会自动增量重建
3. 运行 `python game.py` 测试更改，并跑相关的回归测试
4. 对于本地化更改，运行 `python buildpo.py` 和 `python buildmo.py`
5. 面向玩家的改动登记进仓库根目录的 `update.log`，体例见 skill `update-changelog`
6. 较大的功能先写计划文档：进行中的放 `plan/wait/`，实施完成、测试通过并补齐执行记录后移入 `plan/done/` 归档，模板是 `plan/计划模板.md`

## tools 工具目录

- **`tools/ArkEditor/`**：独立的 PySide6 图形界面编辑器，用于编辑口上/事件/角色属性/外勤委托数据（无需写代码）；从源码运行时直接读取游戏本体的配置表；CI 会将其打包为 `erArkEditor.zip`
- **`tools/tests/`**：无头回归测试，见上文「测试」
- **`tools/AI/`**：AI 文本生成用的语料和提示词文件（本地目录，不入库）
- **`tools/MCP/`**：PRTS 干员资源下载 MCP 服务（`prts_character_downloader`）
- **`tools/map_aa_check.py`**：`data/map/*/Map` 里 AA 地图的逐像素对齐校验工具。地图排版由**字体的实际字宽**决定，而不是 `wcwidth`——框线字符与 ASCII 空格分属两个互不通约的度量族，在部分字号下宽度不同（包括当前 `config.ini` 算出的字号）。绝不要靠数列数来验证 AA 地图，跑这个工具。支持 `--tol N` 与 `--list-bad`，校验不通过时以非零退出码结束
- **`tools/map_aa_build_training.py`** / **`tools/map_aa_build_education.py`**：`data/map/训练/Map` 与 `data/map/教/Map` 的生成脚本。这两张图的留白全部用 **U+2002 EN SPACE**（绝不用 ASCII 空格），这样竖墙在每个字号下都对齐；U+2002 和普通空格长得一模一样，所以必须由脚本重新生成，不能手改
- **`tools/lint_target_csv.py`**：`data/target` 的 AI 目标表编号规范校验（编号唯一、同类型内编号顺序等于物理行序、前提与状态机都能解析等），改完目标表后跑一遍
- **`tools/official_event_check.py`**：公务事件表的校验与统计，支持 `--full`、`--quiet`
- **`tools/generate_character_portrait.py`**：调用 OpenAI 图像模型为指定角色生成立绘（会联网并使用 API 密钥）
- **`profiling/`**（不在 `tools/` 下）：性能基准与 cProfile 采集脚本（`run_profile.py`）、UI 渲染基准、`perf_monitor` 用到的排版补丁；输出在 `profiling_output/`（不入库）
- **零散脚本**：PRTS 抓取（`arknights_story_downloader.py`、`download_prts_*.py`）、翻译工具（`compare_old_and_new_po.py`）、数据维护（`csv_renumber.py`、`update_behavior.py`、`body_part_editor.py`、`replace_quotes.py`、`fix_f_in_str.py` 等）

## Skill 与多代理工作流

入库的 skill 在 `.github/skills/`（`.claude/skills/` 不入库）：

| Skill | 用途 |
| --- | --- |
| `add-new-instruction` | 新增一个玩家指令及其行为、前提、结算、口上的完整流程，含一段行为与二段行为的选型 |
| `draw-aa-map` | 创建或调整 AA 地图：加房间、重排版面、修正竖墙错位 |
| `game-design-dialogue` | 以对话方式把设计点子完善成可实施的方案，并维护 `plan/wait/` 下的计划文档 |
| `handle-pr` | 处理外来 Pull Request：建档定级、按步骤读 CI、只读审查与安全审查、在隔离快照里验证、出结论报告与评论草稿 |
| `headless-game-test` | 不启动界面运行游戏：函数级单元测试、加载存档复现 BUG、带护栏跑行为循环并逐轮内窥 |
| `system-review-round` | 对某个已实现的系统做一轮全面复查：建档、多代理核查与对抗式核实、出方案、实施、回归与归档 |
| `text_generation_for_instruction_code_generation` | 按要求批量生成指令的口上文本（配合子代理 `.claude/agents/text-generation-writer.md`） |
| `update-changelog` | 按既定体例把一次改动写进 `update.log` |

- **`.claude/workflows/`**：保存好的 Workflow 脚本 `system-review-find.js` / `system-review-implement.js`，由 `system-review-round` 调起。该 skill 目录还带 `dead_code_scan.py`、`repro_template.py` 与 `wf_watch.py`——最后一个用来查看正在运行的 Workflow 里各代理是已经结束、卡住了，还是在等一条挂住的命令
- **`.github/skills/handle-pr/`**：带 `pr_triage.py`（不需要 `gh`：列出未合并的 PR、按改动路径定风险档位、逐步骤读 CI、导出 PR 头部的只读快照、记录复审轮次）与 `REVIEW.md`（在本仓库里「出问题」具体长什么样）。PR 只跑 `Check` 一个任务，而且跑的是 PR 自己那个合并提交里的工作流、测试与检查配置，所以 CI 全绿本身不算证明——要用 `pr_triage.py triage` 逐步骤读，它会标出改动了流水线 / 测试 / 检查配置的 PR，也认得 2026-11 之前的运行（那时 fork 上的运行总会在 `Create Release` 一步变红）

## CI/CD 发布结构

GitHub Actions 工作流（`.github/workflows/python-app.yml`）分三个任务：

| 任务 | 何时运行 | 做什么 |
| --- | ------- | ------ |
| `Check` | 每次推送到 master、每个 PR | 改动档案（`pr_triage.py` 的输出写进运行摘要，仅供参考）、`buildconfig.py`、生成物比对（`config_def.py` 必须与重建结果一致）、`init_data.py`、回归测试（`tools/tests/run_all.py`，全部套件）、静态检查（`ruff`，规则在 `ruff.toml`），以及对作者不是仓库所有者的 PR 检查版本号文件没有被改。使用不含 `image/` 的稀疏检出 |
| `Release Plan` | 仅 master 的推送 | 判定这次推送要不要发布 |
| `Build and Release` | 仅当 `Release Plan` 判定发布且 `Check` 通过 | PyInstaller 打包、组装发布包、创建 GitHub Release |

**只有以下条件同时成立才会打包发布**，普通推送不打包也不发布：
1. `package.json` 里的版本号在 GitHub Releases 中还不存在（所以发版的方法是改 `package.json` 的版本号）
2. `Check` 通过
3. 推送者是仓库所有者，且最后一次修改 `package.json` 的提交不是从别人的 PR 合入的

发布页正文末尾会列出自上一个版本标签以来的提交标题，按提交先后排列；超过 10 条时只露出前 10 条，全部条目收在展开栏里。

改动它时要知道的事：
- 生成物在任何系统上都能复现：`buildconfig.py` 与 `auto_build_config.py` 都通过 `sorted_listdir` / `sorted_walk` 遍历目录（按名字不区分大小写排序，与 NTFS 给出的顺序一致）。在这两个脚本里新增目录遍历时必须用它们，否则 Linux/macOS 上的构建结果又会与 Windows 不同（2026-11 之前就是这样：`config_def.py` 类顺序不同，还引出了 #316）。
- `tools/tests/run_all.py` 自动发现套件（`tools/tests/` 下名字不以 `_` 或 `.` 开头、且含 `test_*.py` 的目录），新增套件不用改工作流。日志写在 `%TEMP%/erArk_tests/<套件>/`，失败时 `Show Test Logs` 一步会把它打印出来。
- 游戏运行时需要的新顶层目录要加进 `Copy Game Files` 一步；打包不再随每次推送执行，这里写错要到下次发版才暴露。

一次发布包含 4 个包：

| 包名 | 说明 | 包含内容 |
| --- | --- | ------- |
| `erArk_{版本号}.zip` | 完整游戏包 | 包含所有资源的完整游戏 |
| `erArk_Lite_{版本号}.zip` | 轻量游戏包 | 不包含立绘、场景等大图片资源的游戏 |
| `erArk_Images_{图片版本号}.zip` | 图片资源包 | 除 `image/状态条` 外的所有图片文件夹 |
| `erArkEditor.zip` | 口上事件编辑器 | 独立的编辑器工具（`tools/ArkEditor/main.py`） |

游戏版本号取自 `package.json`，图片版本号取自 `image/package.json`（图片包的文件名用的是图片版本号，图片没更新时文件名不变）。另有第二个工作流（`sync-wiki.yml`）用于同步 wiki。

**图片文件夹分布：**
- **仅在图片资源包中**：`image/场景`、`image/断面图`、`image/立绘`
- **完整版和轻量版都包含**：`image/状态条`、`image/logo.png` 及其他根目录文件

**注：** 轻量版 + 图片资源包 = 完整版

## 重要说明

- 游戏处于 alpha 测试阶段，部分功能尚未实装
- 游戏需要 Sarasa Mono SC 字体（等距更纱黑体 SC）以正确显示
- 官方只支持 Windows（README：Tk 绘制模式仅限 Windows，Web 绘制模式不限设备）
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
- 午夜时触发新一天，执行 `past_day_settle.update_new_day()`（位于 `Script/Settle/`）
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
- **行为效果**：`settle_behavior.handle_settle_behavior()` 计算数值变化；具体效果实现位于 `Script/Settle/`
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
   - 同一文件里还有按钮变体 `CenterButton` / `LeftButton` / `ImageButton`，线条 `LineDraw` / `TitleLineDraw` / `LittleTitleLineDraw`，以及 `LeftDraw`、`ImageDraw`、`BarDraw`、`CharaDraw`、`InfoBarDraw`、`CenterMergeDraw`、`LeftMergeDraw`、`ExpLevelDraw`、`StatusLevelDraw` 等，写新面板先在这里找现成的

2. **IO 操作**（`Script/Core/io_init.py`）：
   - 使用 Tkinter 的 `main_frame` 进行显示
   - 通过事件队列处理命令
   - 直接渲染到 Tkinter 文本小部件

3. **流程控制**（`Script/Core/flow_handle.py`）：
   - `askfor_all()`：等待玩家从选项中选择
   - `askfor_wait()`：简单等待玩家输入
   - 通过 Tkinter 绑定直接处理事件

### Web 绘制模式

当 `web_draw = 1` 时，游戏作为 Flask-SocketIO Web 服务器运行（默认端口 5000）：

1. **渲染子系统**（`Script/System/Web_Draw_System/`）：
   - `web_draw_adapter.py`：启动时调用 `apply_web_adapters()` 将 Tkinter 绘制类转换/打补丁为 Web 元素生成器；元素存储在 `cache.current_draw_elements`
   - 专用渲染器：`scene_renderer.py`、`character_renderer.py`、`dialog_box.py`、`status_panel.py`、`tab_menu.py`、`interaction_handler.py`、`settlement_manager.py`、`image_processor.py`、`body_part_button.py`
   - 设计文档就在同目录下（`Web绘制模式UI重构说明文档.md`）

2. **Web IO 操作**（`Script/Core/io_web.py`）：
   - `era_print()`：将文本转换为 HTML 元素
   - `clear_screen()`：清空元素缓存并更新 Web 状态
   - 通过 Web API 请求处理命令
   - 无直接渲染，所有输出作为 HTML 元素缓冲

3. **Web 流程控制**（`Script/Core/flow_handle_web.py`）：
   - `askfor_all()`：轮询 Web API 响应
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
- Web 模式需要 Web 服务器在运行（默认端口 5000）

## 数据处理工作流文档

`.github/prompts/数据处理工作流` 目录包含 64 个详细文档（63 个系统/工作流文档加一个 README）。这些文档解释了不同系统与代码组件之间的关系。在处理相关功能时，请参考这些文档以理解系统之间的关联、依赖和数据流。此外，`Script/System/*` 的多数子系统目录内也附带自己的设计文档。

### 🏗️ 核心系统架构文档
- **[角色行为系统](.github/prompts/数据处理工作流/角色行为系统.md)** - 核心行为循环、时间管理、状态变化
- **[结算系统](.github/prompts/数据处理工作流/结算系统.md)** - 行为结算、数值计算、状态更新
- **[前提系统](.github/prompts/数据处理工作流/前提系统.md)** - 行为和事件的条件验证
- **[口上系统](.github/prompts/数据处理工作流/口上系统.md)** - 文本和对话系统
- **[事件系统](.github/prompts/数据处理工作流/事件系统.md)** - 剧情事件和特殊触发机制

### 🔧 技术与工具系统
- **[CSV数据加载机制说明](.github/prompts/数据处理工作流/CSV数据加载机制说明.md)** - CSV 数据加载和处理
- **[AI文本生成系统](.github/prompts/数据处理工作流/AI文本生成系统.md)** - AI 文本生成功能
- **[存档系统](.github/prompts/数据处理工作流/存档系统.md)** - 存档系统和跨版本兼容性
- **[通用结算函数函数](.github/prompts/数据处理工作流/通用结算函数函数.md)** - 通用计算函数
- **[多周目结算与继承系统](.github/prompts/数据处理工作流/多周目结算与继承系统.md)** - 多周目数据继承
- **[ArkEditor编辑器系统说明](.github/prompts/数据处理工作流/ArkEditor编辑器系统说明.md)** - 内置编辑器系统
- **[新增指令工作流](.github/prompts/数据处理工作流/新增指令工作流.md)** - 新增一个玩家指令的完整流程（配置、行为、前提、结算、口上）
- **[系统复查工作流](.github/prompts/数据处理工作流/系统复查工作流.md)** - 对已实现系统反复做全面复查：系统档案、Workflow 多代理的核查/核实与实施/复审、方案双文件、收尾（skill `system-review-round`）
- **[剧情总结工作流](.github/prompts/数据处理工作流/剧情总结工作流.md)** - 剧情总结工作流
- **[剧情转外勤委托工作流](.github/prompts/数据处理工作流/剧情转外勤委托工作流.md)** - 剧情转外勤委托的转换工作流

### 🎮 用户界面系统
- **[主场景互动界面](.github/prompts/数据处理工作流/主场景互动界面.md)** - 主场景交互界面
- **[指令面板系统](.github/prompts/数据处理工作流/指令面板系统.md)** - 玩家指令面板
- **[通用NPC选择面板](.github/prompts/数据处理工作流/通用NPC选择面板.md)** - 通用 NPC 选择面板
- **[系统设置系统](.github/prompts/数据处理工作流/系统设置系统.md)** - 系统配置界面
- **[全干员位置面板](.github/prompts/数据处理工作流/全干员位置面板.md)** - 全干员位置面板
- **[PRTS系统](.github/prompts/数据处理工作流/PRTS系统.md)** - PRTS 通讯系统
- **[Tk绘制模式](.github/prompts/数据处理工作流/Tk绘制模式.md)** - Tkinter 渲染模式
- **[Web绘制模式](.github/prompts/数据处理工作流/Web绘制模式.md)** - Web 渲染模式

### 🗺️ 场景与地图系统
- **[地图系统](.github/prompts/数据处理工作流/地图系统.md)** - 地图数据结构和管理
- **[导航系统](.github/prompts/数据处理工作流/导航系统.md)** - 导航和场景切换

### 👥 角色创建与成长
- **[角色创建流程](.github/prompts/数据处理工作流/角色创建流程.md)** - 角色创建工作流
- **[能力升级面板](.github/prompts/数据处理工作流/能力升级面板.md)** - 能力升级界面
- **[生长养成系统](.github/prompts/数据处理工作流/生长养成系统.md)** - 养成全链路：胎教、婴儿照料、课表与六类课程、学期与成绩单、每日日程、成长事件、性技实操课（`Script/System/Education_System`）
- **[成就系统](.github/prompts/数据处理工作流/成就系统.md)** - 成就系统

### 👗 外观与装饰系统
- **[服装系统说明](.github/prompts/数据处理工作流/服装系统说明.md)** - 服装系统详情
- **[衣柜检查功能](.github/prompts/数据处理工作流/衣柜检查功能.md)** - 衣柜检查功能
- **[收藏品系统](.github/prompts/数据处理工作流/收藏品系统.md)** - 收藏品管理
- **[角色图片系统](.github/prompts/数据处理工作流/角色图片系统.md)** - 角色图片资源

### 👨‍⚕️ 身体状态系统
- **[身体信息面板系统](.github/prompts/数据处理工作流/身体信息面板系统.md)** - 身体信息显示
- **[性行为履历系统](.github/prompts/数据处理工作流/性行为履历系统.md)** - 性行为初次记录、多周目存档与履历面板
- **[射精面板系统](.github/prompts/数据处理工作流/射精面板系统.md)** - 射精状态面板
- **[妊娠系统](.github/prompts/数据处理工作流/妊娠系统.md)** - 妊娠状态管理

### 🎯 罗德岛部门系统
- **[管理罗德岛系统](.github/prompts/数据处理工作流/管理罗德岛系统.md)** - 罗德岛基地管理
- **[助理系统](.github/prompts/数据处理工作流/助理系统.md)** - 助理角色功能
- **[基建系统](.github/prompts/数据处理工作流/基建系统.md)** - 建设和建筑管理
- **[动力系统](.github/prompts/数据处理工作流/动力系统.md)** - 动力系统
- **[农业生产系统](.github/prompts/数据处理工作流/农业生产系统.md)** - 农业生产
- **[工业生产系统](.github/prompts/数据处理工作流/工业生产系统.md)** - 工业生产
- **[装备维护系统](.github/prompts/数据处理工作流/装备维护系统.md)** - 装备维护
- **[医疗经营系统](.github/prompts/数据处理工作流/医疗经营系统.md)** - 医疗经营系统
- **[资源交易系统](.github/prompts/数据处理工作流/资源交易系统.md)** - 资源交易和市场
- **[招募系统](.github/prompts/数据处理工作流/招募系统.md)** - 角色招募机制
- **[外勤委托系统](.github/prompts/数据处理工作流/外勤委托系统.md)** - 外勤任务委托
- **[邀请访客系统](.github/prompts/数据处理工作流/邀请访客系统.md)** - 访客邀请系统
- **[势力外交系统](.github/prompts/数据处理工作流/势力外交系统.md)** - 势力外交
- **[载具管理系统](.github/prompts/数据处理工作流/载具管理系统.md)** - 载具管理
- **[读书系统](.github/prompts/数据处理工作流/读书系统.md)** - 阅读和学习功能
- **[身体检查与管理系统](.github/prompts/数据处理工作流/身体检查与管理系统.md)** - 身体检查和健康管理
- **[宿舍管理系统](Script/System/Dormitory_System/宿舍管理系统设计文档.md)** - 宿舍管理（文档位于子系统目录内）

### 🛍️ 物品与装备系统
- **[道具背包系统](.github/prompts/数据处理工作流/道具背包系统.md)** - 道具背包管理
- **[礼物系统](.github/prompts/数据处理工作流/礼物系统.md)** - 礼物赠送和接收
- **[食物系统](.github/prompts/数据处理工作流/食物系统.md)** - 食物制作和消耗

### 🌟 源石技艺系统
- **[源石技艺系统](.github/prompts/数据处理工作流/源石技艺系统.md)** - 源石技艺学习和管理
- **[时间停止系统](.github/prompts/数据处理工作流/时间停止系统.md)** - 时间停止特殊功能
- **[催眠系统](.github/prompts/数据处理工作流/催眠系统.md)** - 催眠功能和机制

### 🎭 特殊 H 模式系统
- **[群交系统](.github/prompts/数据处理工作流/群交系统.md)** - 群体交互功能
- **[监禁调教系统](.github/prompts/数据处理工作流/监禁调教系统.md)** - 监禁和调教
- **[睡眠系统](.github/prompts/数据处理工作流/睡眠系统.md)** - 睡眠状态管理
- **[隐奸系统](.github/prompts/数据处理工作流/隐奸系统.md)** - 隐藏行为系统

### 使用指南
1. **按类别浏览**：根据你正在处理的系统类型选择相应的类别
2. **系统依赖**：许多系统相互关联 - 请参考相关系统文档
3. **文档结构**：每个文档通常包含系统概述、核心组件、数据结构、工作流说明、配置详情、技术实现和扩展指南
