# erArk Copilot / AI Agent 指南

聚焦让智能代理“即插即用”：如何安全修改、构建、调试、扩展。本文件是最小必读速查；深度细节见 `CLAUDE*.md` 与 `.github/prompts/数据处理工作流/`。

## 1. 总览（执行顺序视角）
0. 终端调试：使用本地 conda 环境，如 `c:/code/erArk/.conda/python.exe`。
1. 构建数据：`python buildconfig.py` （解析 `data/csv/`, 生成 `data/*.json` 与 `Script/Config/config_def.py`）
2. （若本地化改动）`python buildpo.py` → `python buildmo.py`
3. 启动游戏：`python game.py`（根据 `config.ini` 决定 GUI(Tk) 或 Web）
4. 调试：`config.ini` 里 `debug = 1`；必要时切 `web_draw = 1` 测试 Web 渲染。

## 2. 架构骨架
- 入口：`game.py`
- 主行为循环：`Script/Design/character_behavior.py`（玩家 → NPC → 时间推进）
- 初始化 & 流程：`Script/Core/game_init.py`, `Script/Design/start_flow.py`
- 数据缓存/状态：`Script/Core/cache_control.py`
- 存档：`Script/Core/save_handle.py`
- UI 抽象：`Script/UI/Moudle/draw.py`；Web 适配 `Script/UI/web_draw_adapter.py` / IO `Script/Core/io_web.py`
- 事件/口上/结算：参考 `.github/prompts/数据处理工作流/` 对应文档与 `Script/Design/` 下同名模块。

## 3. 数据 & 生成物边界
- 可编辑源：`data/csv/`, `data/character/`, `data/talk/`, `data/event/`, `config.ini`
- 生成产物：`data/*.json`, `Script/Config/config_def.py`, 以及 gettext 编译 `.mo`
- 修改 CSV/角色/口上后必须重跑 `buildconfig.py`；未重建将出现字段缺失或旧枚举。
- 不要直接手改 `config_def.py`（会被重生成覆盖）。

## 4. 渲染双模策略
- 判定：`config.ini: web_draw`（0=Tk,1=Web）
- 统一调用：所有输出经 `io_init.era_print()` 或抽象 draw 类；禁止直接写 Tk 或拼 HTML。
- Web 模式核心：元素缓冲 `cache.current_draw_elements` → 通过 `update_game_state()` 批量下发。
- 新 UI 组件：先扩展抽象/适配层，再分别适配 Tk/Web（保持同名字段）。

## 5. 行为循环要点（AI 插入扩展常用切点）
- 玩家/NPC 行为结束判定集合：`cache.over_behavior_character`
- 时间引用：`cache.game_time`；时停：`cache.time_stop_mode`
- 扩展行为/指令：新增结算逻辑 → 注册前提/事件 → 确保数值变化纳入 `settle_behavior.handle_settle_behavior()` 或对应变更结构。

## 6. 常见改动范式
| 场景 | 步骤 |
| ---- | ---- |
| 新增角色属性 | 加列至相关 CSV → run buildconfig → 在逻辑中通过生成的枚举/映射访问 |
| 新增指令/行为 | 定义前提/执行/结算 → 更新指令面板数据源 CSV → 重建 → 在行为循环中调用或自动挑选逻辑接入 |
| 新增事件/口上 | 添加 CSV/JSON → 重建 → 确认触发条件/前提脚本存在 |
| UI 面板扩展 | 新建 `Script/UI/Panel/xxx.py` → 使用抽象 draw 类 → 若需 Web 特性同步适配 |
| 本地化文本 | 更新 `data/po/<lang>/*.po` 或新增语言目录 → buildpo → buildmo |

## 7. MCP / PRTS 集成
- 目录：`tools/MCP/prts_character_downloader/`
- VS Code 任务：启动服务器（供图像/立绘下载等）与测试。
- AI 代理可自然语言触发相关下载脚本，但应避免在无新增资源需求时重复抓取。

## 8. 代码规范
- 注释/文档全部中文；函数首注释：输入类型 / 输出类型 / 功能。
- Black 行宽 200；保持生成文件不手改。
- 逻辑区块加目的说明，方便静态分析与后续代理快速定位。

## 9. 性能与风险提示
- 生成脚本 O(文件数) 读取；频繁局部小改→可临时复制小 CSV 做最小化测试。
- 大量对话/事件加载在启动期完成；避免在主循环中做磁盘 I/O。
- 未调用 buildconfig 的差异最常见：枚举缺失、KeyError、旧缓存。
- Web 模式调试注意：输出积压需定期 `clear_screen()`，否则元素数组膨胀。

## 10. 快速排错清单
- KeyError / 属性缺失：是否忘记重建？
- 本地化缺失：`.po` 未编译为 `.mo`？语言目录命名是否匹配？
- UI 不显示：是否绕过抽象层直接写入？Web 模式元素是否进入 `cache.current_draw_elements`？
- 行为不触发：前提脚本或事件条件文件是否存在 / 返回值正确？

## 11. 进一步阅读索引
- 深度行为/结算：`CLAUDE*.md` 行为循环章节
- 系统拆解：`.github/prompts/数据处理工作流/`
- 图像/资源下载：`tools/MCP/`

## 12. 给后续 AI 代理的执行建议
- 变更前先判定是否修改源数据还是运行时代码，避免对生成文件动刀。
- 对行为/事件新增：同时检视前提、结算、展示三个层面是否一致。
- 编写面板：验证双模式；若仅 Tk 生效视为不完整提交。

（本文件保持 20~50 行原则：已压缩为高信息密度速查，可按需扩展。）

---
需要新增的特定系统速记或扩展更多代码示例请反馈。 