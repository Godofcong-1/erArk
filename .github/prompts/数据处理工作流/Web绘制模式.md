# Web绘制模式详解

本文档系统梳理 erArk 在 Web 绘制模式下的端到端流程，包括后端初始化、绘制数据协议、前端渲染栈、输入回传机制及与 Tk 模式的差异，同时提供扩展建议与排错要点。

## 模式切换入口

- **配置开关**：`config.ini` 中 `[game]` 段的 `web_draw` 默认值为 `0`，设为 `1` 后启用 Web 模式。
- **初始化入口**：`game.py`
  1. 创建 `cache_control.cache = game_type.Cache()` 并调用 `normal_config.init_normal_config()`；
  2. 读取 `web_draw`，写入 `cache_control.cache.web_mode`；
  3. 若开启 Web，导入 `Script.UI.web_draw_adapter` 并执行 `apply_web_adapters()`，随后替换 `game_init.io_init = io_web`；
  4. 启动 `Script.Core.web_server.start_server()`，自动选择空闲端口并尝试打开浏览器；
  5. 进入 `game_init.run(start_flow.start_frame)`，后续流程均走 Web 适配链路。

## 后端组成

### 绘制适配链路

| 角色 | 关键文件/函数 | 说明 |
| --- | --- | --- |
| 绘制模型 | `Script/UI/Moudle/draw.py` | 定义 `NormalDraw`、`Button`、`InfoBarDraw` 等原始类。|
| 适配器 | `Script/UI/web_draw_adapter.py` | `apply_web_adapters()` 将各 `draw.*.draw()` 方法替换为 Web 版本，所有绘制在 Web 模式下都会构造字典元素并写入 `cache.current_draw_elements`。|
| IO 层 | `Script/Core/io_init.py` ↔ `Script/Core/io_web.py` | `io_init` 根据 `cache.web_mode` 自动转向 `io_web`，后者提供 `era_print`、`clear_screen`、`io_print_cmd` 等 Web 实现。|
| 流程控制 | `Script/Core/flow_handle.py` ↔ `Script/Core/flow_handle_web.py` | `flow_handle` 发现 `cache.web_mode` 后切入 `flow_handle_web`，后者负责命令绑定、按钮输出、等待与输入的轮询。|

### 绘制数据结构

- **缓存核心**：`cache.current_draw_elements`（当前帧元素）与 `cache.web_draw_history`（最多 500 行历史，`MAX_HISTORY_LENGTH` 可在 `io_web` 调整）。
- **元素格式**：字典对象，关键字段如下：
  - `type`: `text` / `button` / `line` / `title` / `image` / `center_image` / `bar` / `character` / `info_bar` / `info_character` / `image_button` / `wait` / `line_wait` 等；
  - 文本类字段：`text`、`font`、`width`、`align`、`web_type`（如地图布局 `map` / `map-padding`）；
  - 按钮类字段：`return_text`（命令值）、`style`、`align`；
  - `line_wait` 附带 `wait_id`、`await_input`，被前端 `WaitManager` 用于控制逐行等待；
  - 复合组件（`info_bar`、`info_character`）包含 `draw_list` 递归结构。
- **历史记录**：`io_web.append_current_draw_element()` 在 `record_history=True` 时同步写入历史。当 `clear_screen()` 触发时会重放历史内容，确保 Web UI 与 Tk 行为一致。
- **即时刷新**：关键节点（逐行等待、清屏等）调用 `web_server.update_game_state(cache.current_draw_elements, panel_id)`，通过 WebSocket / 轮询推送至前端。

### 流程函数要点（`flow_handle_web`）

- `askfor_all(return_list)`：调用 `update_game_state` 暴露当前按钮，之后轮询 `get_button_response()`；若命令有效则执行 `cmd_map` 中绑定的函数。
- `askfor_wait()`：轮询 `get_wait_response()`，配合 `WaitManager` 控制逐行文本停顿。
- `askfor_str` / `askfor_int`：设置 `cache.current_input_request`，通过 `update_input_request()` 通知前端弹出输入框并轮询 `get_input_response()`。
- `order_deal()`：命令输入兜底逻辑，按钮模式轮询 `get_button_response()`，控制台模式轮询文本输入；`print_order=True` 时回写到 `era_print`。
- `bind_cmd` / `print_cmd` / `cmd_clear`：维护 `constant.cmd_map`，并同步增删 `cache.current_draw_elements` 中的按钮元素。
- `set_tail_deal_cmd_func`：仍支持注册尾流程函数，`call_default_flow()` 在循环尾部调用。

### 其他后端支撑

- `Script/Core/game_type.Cache`：新增 `web_mode`、`current_draw_elements`、`web_draw_history` 等字段，供适配器与服务器共享。
- `Script/Core/era_image.py` + `web_server.get_image_paths`：Web 端通过 `/api/get_image_paths` 解析图片路径，避免硬编码文件系统差异。
- `Script/Core/main_frame.py`：保留 Tk 逻辑，Web 模式下不会执行。
- `Script/UI/Panel` 中的个别面板对 `cache.web_mode` 做了分支，例如 `in_scene_panel` 每轮重置屏幕，`see_map_panel` 为地图元素打上 `web_type` 标签供前端布局。

## 输入与命令交互

后端 API 定义于 `Script/Core/web_server.py`：

| Endpoint | 方法 | payload | 用途 | 对应后端读取 |
| --- | --- | --- | --- | --- |
| `/api/button_click` | POST | `{button_id}` | 普通命令按钮 | `flow_handle_web.askfor_all` / `order_deal` 轮询 `get_button_response()` |
| `/api/wait_response` | POST | - | 文本等待确认 | `flow_handle_web.askfor_wait` 轮询 `get_wait_response()` |
| `/api/skip_wait` | POST | - | 启动跳过等待模式，设置 `cache.wframe_mouse.w_frame_skip_wait_mouse` | `WaitManager.requestSkipUntilMain()` 与后端 skip 标志互锁 |
| `/api/string_input` | POST | `{value}` | 字符串输入 | `flow_handle_web.askfor_str` |
| `/api/integer_input` | POST | `{value}` | 数值输入 | `flow_handle_web.askfor_int` |
| `/api/get_state` | GET | - | 轮询模式获取最新 `game_state` | 前端回退使用 |
| `/api/get_image_paths` | GET | - | 拉取图片路径映射 | `static/game.js` 初始化图片缓存 |
| `/api/get_font_config` | GET | - | 同步字体/颜色配置 | `static/game.js` 的 `applyFontStyle` |

`game_state` 结构（由 `update_game_state` 构造）：

```text
{
  text_content: List[元素字典],
  buttons: List[{id,text,style}],
  panel_id: 当前面板 ID 或 None,
  skip_wait: bool,
  input_request: Optional[{type("string"/"integer"/"command"), message, default}]
}
```

## Web 服务器与传输

- **框架**：`Flask + Flask-SocketIO`（线程模式）。模板目录和静态目录在 PyInstaller 场景下会改指向 exe 同级。
- **端口管理**：`start_server()` 自动检测占用（`psutil.net_connections()`），必要时向上递增端口。成功后打印本地与局域网地址并尝试 `webbrowser.open(...)`。
- **WebSocket**：名称空间默认，事件 `game_state_update` 由 `_emit_game_state_update()` 广播。连接失败时前端退化到轮询。
- **线程安全**：`state_lock` 保护 `game_state` 与各类响应缓存（`button_click_response`、`wait_response_triggered`、`input_response`）。
- **退出清理**：`atexit.register(cleanup)` 调用 `stop_server()`，阻止孤立线程。

## 前端渲染框架（`static/`）

### 静态资源

- `templates/index.html`：容器结构、Socket.IO CDN、输入框与缩放控制。
- `static/style.css`：全面定义排版、主题、地图行布局、等待态样式、缩放动画、字体引入。
- `static/game.js`：核心逻辑（≈2.3k 行），模块化对象式实现。

### 核心模块概览

| 模块 | 功能 |
| --- | --- |
| `DeviceDetector` | 设备特征探测，决定自动缩放与横屏提示策略。|
| `AutoScaleManager` | 通过调整 `document.documentElement` 字体大小实现界面缩放，支持手动/自动模式。|
| `LandscapeManager` | 移动端竖屏提示覆盖层控制。|
| `ScrollManager` | 智能滚动与“有新内容”指示器管理。|
| `WaitManager` | 侦测 `line_wait`/`wait` 元素并绑定点击、键盘、右键跳过，调用 `/api/wait_response` 或 `/api/skip_wait`。|
| `renderGameState(state)` | 按顺序渲染 `state.text_content`，根据 `type` 生成 DOM；对地图元素应用 `map-line`、`map-button` 布局；同步按钮 dataset 与字体样式。|
| `initWebSocket()` | 创建 Socket.IO 连接，接收 `game_state_update` 实时刷新；失败时触发 `fallbackToPolling()`。|
| `handleButtonClick` / `sendInputToServer` | 将命令或输入 POST 回后端。|
| `initialize()` | DOMContentLoaded 时入口：依次初始化图片/字体缓存、缩放、滚动、等待监听、WebSocket，并在失败时回退轮询。

### 运行时交互细节

- **字体同步**：启动时调用 `/api/get_font_config` 构建 `fontConfigDict`，`applyFontStyle()` 根据后端配置还原 Tk 风格。
- **图片加载**：`initImagePathDict()` 拉取图片路径，渲染时通过 `getImagePath()` 映射，MutationObserver 监听图片加载完成后再次滚动。
- **等待机制**：`WaitManager.start()` 根据 `await_input` 决定是否自动触发；右键或长按 `game-container` 调用 `requestSkipUntilMain()`。
- **持久输入框**：底部输入框 `persistent-input` 优先匹配按钮 ID，再回退到当前 `input_request`。
- **地图渲染**：利用 `web_type` 区分文字行、补位空格、按钮；`normalizeMapBlocks()` 将地图行宽统一居中。

## 与 Tk 模式的差异

| 项目 | Tk 模式 | Web 模式 |
| --- | --- | --- |
| 渲染目标 | `tkinter.Text` 队列 | WebSocket 推送 JSON，由浏览器渲染 |
| 事件源 | `main_frame.bind_return`、本地键鼠事件 | HTTP API + WebSocket，由前端 JS 采集 |
| 样式定义 | `io_init.frame_style_def` + Tk 字体 | CSS + 动态字体同步，`frame_style_def` 在 Web 模式中被忽略 |
| 等待机制 | Tk 事件阻塞 | `WaitManager` + `wait_response` API |
| 清屏策略 | `Text` 控件清空 | `clear_screen()` 清 `current_draw_elements` 并回放历史 |
| 进程退出 | Tk 主循环 | `start_server()` 的守护线程，`cleanup()` 负责关闭 SocketIO |

## 扩展与开发建议

1. **新增绘制组件**
   - 在 `draw.py` 中实现逻辑后，需要在 `WebDrawAdapter` 中提供 `adapt_xxx_draw`，并在 `apply_web_adapters()` 中注册；
   - 前端 `renderGameState` 必须识别新的 `type`，否则需要添加 DOM 构建逻辑和样式；
   - 如需持久化到历史，调用 `append_current_draw_element(..., record_history=True)`。

2. **新增输入或交互**
   - 后端：在 `web_server.py` 添加 API 并在 `flow_handle_web` 中封装轮询函数；
   - 前端：在 `game.js` 中添加对应的提交函数/按钮绑定，并在 `initialize()` 中注册事件。

3. **面板适配**
   - 复杂面板（如地图、场景）应为 Web 模式提供 `web_type`、宽度、对齐字段，前端通过 CSS 定制布局；
   - 高频刷新面板建议显式调用 `io_init.clear_screen()` + `io_init.clear_order()`，避免历史堆积。

4. **性能建议**
   - 控制 `update_game_state` 频率，批量添加元素后统一推送；
   - 合理设置 `cache.wframe_mouse.w_frame_skip_wait_mouse`，避免 `line_wait` 产生大量同步阻塞；
   - 如需扩展历史上限，可调整 `MAX_HISTORY_LENGTH`，但注意前端渲染负载。

## 故障排查

| 症状 | 排查要点 |
| --- | --- |
| 前端空白或 404 | 检查 `templates/index.html`、`static/` 是否存在；确认 `start_server()` 是否报错。|
| 按钮点击无响应 | 观察后端日志是否命中 `/api/button_click`；确认 `cmd_map` 中存在绑定；检查 `renderGameState` 是否正确渲染 `button`。|
| 文本不换行或地图错位 | 确认 `draw` 对象是否设置 `width`、`web_type`；前端 `normalizeMapBlocks` 仅对 `map-line` 生效。|
| 等待无法跳过 | 检查 `WaitManager` 是否收到 `line_wait` 元素的 `await_input=false`，或后端 `skip_wait` API 是否成功设置 `cache.wframe_mouse.w_frame_skip_wait_mouse`。|
| 打包版本静态资源丢失 | 需保证 `templates/`、`static/` 与 exe 同级；`web_server` 会根据 `sys._MEIPASS` 切换路径。|
| 高 CPU 占用 | `flow_handle_web` 使用 `time.sleep(0.1)` 轮询，可根据需要优化为事件通知；确保没有频繁空转的面板刷新。|

## 参考文件索引

- `config.ini`
- `game.py`
- `Script/Core/io_init.py`, `Script/Core/io_web.py`
- `Script/Core/flow_handle.py`, `Script/Core/flow_handle_web.py`
- `Script/UI/web_draw_adapter.py`, `Script/UI/Moudle/draw.py`
- 重要面板：`Script/UI/Panel/in_scene_panel.py`, `Script/UI/Panel/see_map_panel.py`
- `Script/Core/web_server.py`
- 前端：`templates/index.html`, `static/game.js`, `static/style.css`

> **提示**：修改 CSV / 数据后仍需执行传统的 `buildconfig.py` 等生成脚本；Web 模式仅替换显示与输入通道，不改变数据构建流程。
