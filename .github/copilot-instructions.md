# erArk 项目 Copilot/AI Agent 开发指令

## 项目架构与核心流程
- 游戏主入口为 `game.py`，初始化配置并启动 GUI 或 Web。
- 配置与数据构建流程：
  - 运行 `python buildconfig.py` 生成 JSON 数据和 Python 配置（见 `Script/Config/config_def.py`）。
  - 运行 `python buildpo.py`、`python buildmo.py` 处理本地化。
- 主要数据存储于 `data/` 目录下（如 `csv/`、`character/`、`event/`、`talk/` 等）。
- 主要逻辑分布在 `Script/` 下，核心循环在 `Script/Design/character_behavior.py`。
- Web 模式通过 `Script/Core/web_server.py` 启动，相关适配器见 `Script/Core/io_web.py`。

## 关键开发流程
- 编辑 `data/csv/`、`data/talk/`、`data/character/` 下 CSV 后，务必重建数据。
- 测试/调试：
  - 启用 `config.ini` 的 `debug = 1` 进入调试模式。
  - 运行 `python game.py` 启动游戏。
- 依赖管理：
  - 推荐 `pip install -r requirements.txt`。

## 约定与注释规范
- 注释必须为中文。
- 每个函数需在开头注释输入/输出类型、功能说明。
- 每段代码需有中文注释解释作用。

## 目录与模块说明
- `data/`：游戏主数据，含角色、事件、对话、配置等。
- `Script/`：核心逻辑，分为 Config、Core、Design、UI 等子模块。
- `tools/`：批量数据处理、MCP/PRTS集成、辅助脚本。
- `.github/prompts/`：AI文本生成、行为前提、系统文档，详见各子目录。
- 详细系统文档见 `.github/prompts/数据处理工作流/`，涉及行为、结算、前提、事件、UI、存档等。

## MCP/PRTS 集成与 AI 工具
- MCP 服务器位于 `tools/MCP/prts_character_downloader/`，详见 `MCP_INTEGRATION_GUIDE.md`。
- VS Code 任务：
  - "启动PRTS MCP服务器" 启动服务。
  - "测试PRTS下载器" 运行功能测试。
- Copilot 可直接调用 MCP 工具（如角色立绘下载、URL搜索等）。
- 集成流程：配置 VS Code，重启后可用 Copilot Chat 直接自然语言调用。

## 重要约定与模式
- 数据驱动：大部分系统通过 CSV/JSON 配置，自动生成 Python 配置。
- 系统间高度解耦，详见 `.github/prompts/数据处理工作流/` 下各系统文档。
- 事件、对话、角色等均有独立数据与处理模块，便于扩展。

## 参考文档
- `README.md`/`README_en.md`：项目说明、依赖、配置、开发分支等。
- `CLAUDE.md`/`CLAUDE_cn.md`：架构、开发流程、主循环、数据流、系统文档导航。

---

如需扩展AI相关功能，优先查阅 `.github/prompts/` 及 `CLAUDE.md`，遵循本文件注释与开发规范。