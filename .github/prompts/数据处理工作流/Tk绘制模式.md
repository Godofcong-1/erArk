# Tk 绘制体系详解

> 适用于 `web_draw = 0`（Tk 模式）时的渲染、命令与输入处理路径。本文梳理了从入口开关、底层 IO、绘制组件到上层面板的完整链路，并给出扩展与排错要点。

## 1. 模式切换与启动流程

- **配置开关**：`config.ini` 最终由 `Script.Config.normal_config` 读入，`game.py` 在启动时将 `normal_config.config_normal.web_draw` 写入 `cache_control.cache.web_mode`。
- **入口判断**：`game.py` 根据 `now_web_mode` 选择是否引入 `Script.Core.io_web` 与 `Script.UI.web_draw_adapter`。当值为 `False` 时默认走 Tk；所有 `io_*`/`flow_handle` 函数保持本地实现。
- **主流程**：`Script.Core.game_init.run()` 委托 `io_init.run(open_func)`。在 Tk 模式下该函数：
  1. 创建并启动后台线程运行具体流程（`open_func`，通常是 `Script.Design.start_flow.start_frame`）。
  2. 调用 `Script.Core.main_frame.run()` 打开 Tk 主循环。

## 2. Tk 主窗口与事件总线（`Script.Core.main_frame`）

- **窗口装配**：初始化 `Tk` 根窗口、文本输出区 `Text`、滚动条、指令输入框 `Entry`，并根据屏幕尺寸动态调整字号、窗口大小。窗口图标统一来自 `image/logo.png`。
- **字体加载**：`load_local_fonts()` 会扫描 `static/fonts` 并在 Tk 环境注册字体/别名，确保配置中的字体能被识别。
- **输出渲染**：核心逻辑在 `read_queue()`：
  - 轮询 `io_init` 推入的 JSON 消息并转化为文本插入 (`now_print`)、图片插入 (`textbox.image_create`)、命令按钮 (`io_print_cmd`) 等。
  - 支持清屏（`clear_screen`）、清命令（`io_clear_cmd`）、设背景色和动态样式注册。
- **命令标签**：按钮输出通过 Tk `Text` 的 tag 机制实现，`io_print_cmd` 为每个 cmd 生成唯一 tag，绑定 `<1>/<Enter>/<Leave>` 事件以触发回调与 hover 样式。
- **输入框行为**：`main_frame.send_input()` 从 `Entry` 读取文本，写入历史缓存 `cache.input_cache`，再触发绑定的输入处理函数。

## 3. IO 管线（`Script.Core.io_init`）

- **统一入口**：所有文本/图片/命令输出都经 `io_init.*`，它同时兼容 Web 与 Tk ——在 Tk 模式下落地到本地实现，在 Web 模式下转发给 `io_web`。
- **队列协议**：`era_print`、`image_print`、`io_print_cmd` 等函数构造 JSON 包并写入 `_send_queue`。`main_frame.read_queue()` 消费队列，实现 UI 与业务线程解耦。
- **样式初始化**：`init_style()` 遍历 `game_config.config_font`，调用 `frame_style_def()` 将样式注册为 Tk `Text` tag；同时额外生成 `bold/underline/italic` 及其与基础样式的组合标记。
- **命令输入**：`get_order()` 读取 `_order_queue` 中的指令；`put_order()` 在 Tk 模式下直接入队，被 `flow_handle.order_deal()` 消费。

## 4. 绘制组件层（`Script.UI.Moudle.draw`）

> 这里定义了所有可复用的绘制原件，面板层只负责装配。

### 4.1 文本类
- `NormalDraw`：基础文本绘制，使用 `text_handle.get_text_index` 计算宽度，按 `self.width` 自动换行。
- `FullDraw`：不处理换行，直接输出。
- `WaitDraw`：绘制完成后调用 `flow_handle.askfor_wait()`；用于需要暂停的剧情输出。
- `LineFeedWaitDraw`：以 `\n` 分段并逐行等待，底层利用 `cache.wframe_mouse` 控制跳过逻辑。
- `CenterDraw`/`RightDraw`/`LeftDraw`：对齐变种，内部调用 `text_handle.align()`。
- `CenterMergeDraw`/`LeftMergeDraw`：合并多个 `NormalDraw` 并控制整体宽度。

### 4.2 图形类
- `ImageDraw`：透传图片 ID 给 `io_init.image_print`。
- `BarDraw`：根据配置 `game_config.config_bar` 拼装若干 `ImageDraw` 构成进度条。
- `CharaDraw`：同理，根据角色立绘配置生成 `ImageDraw` 序列。
- `InfoBarDraw`/`InfoCharaDraw`：在进度条/立绘前后额外挂载文本。

### 4.3 按钮类
- `Button`：核心按钮控件，内部调用 `py_cmd.pcmd()` 完成命令绑定。
- `ImageButton`、`CenterButton`、`LeftButton`：分别处理图片按钮、固定宽度按钮、左对齐按钮。
- `LineDraw`、`TitleLineDraw`、`LittleTitleLineDraw`：绘制分隔线与标题装饰。
- `ExpLevelDraw`、`StatusLevelDraw`：根据数值计算评级并输出对应样式文本。

所有 `draw` 对象的 `draw()` 最终都会调用 `io_init`，因此在 Tk 与 Web 之间保持统一接口。

## 5. 面板与流程装配层

- `Script.UI.Moudle.panel` 提供通用面板骨架，例如：
  - `SingleColumnButton`：将若干 `draw.Button` 竖向排列。
  - `OneMessageAndSingleColumnButton`：常见的“上方文本 + 下方选项”组合。
  - `CenterDrawTextListPanel`、`LeftDrawTextListPanel`：按列对齐输出列表。
  - `LeftDrawTextListWaitPanel`：绘制完成后阻塞等待输入（结合 `cache.wframe_mouse`）。
- 业务面板位于 `Script/UI/Panel/*`，多数 `draw()` 函数中：
  1. 收集数据并实例化 `draw.*` 元素。
  2. 调用 `io_init.clear_cmd()`/`io_init.clear_screen()` 等更新 UI。
  3. 使用 `flow_handle` 监听按钮结果或等待输入。
- 面板入口映射由 `Script.UI.Flow` 系列注册（例如 `normal_flow.py` 通过 `handle_panel.add_panel` 指定面板 ID → 绘制函数），供行为循环或指令调用。

## 6. 命令绑定与输入调度

- **绑定阶段**：`py_cmd.pcmd()` -> `flow_handle.print_cmd()` -> `flow_handle.bind_cmd()` 将命令编号与处理函数写入 `constant.cmd_map`。
- **渲染阶段**：`flow_handle.print_cmd()` 同时调用 `io_init.io_print_cmd()`，由 Tk 侧转为带事件的 tag。
- **输入阶段**：
  1. 玩家点击命令或直接在输入框输入数字，`main_frame.send_input()` 将文本塞入 `_order_queue`。
  2. `flow_handle.order_deal()` 监听 `_order_queue`：若命令存在于 `cmd_map` 则执行，反之触发尾处理函数或错误提示。
  3. `askfor_all`/`askfor_int` 等封装基于 `order_deal()` 循环等待合法输入。
- **默认流程**：`flow_handle.set_default_flow()` 可以注册默认逻辑（常用于绘制后的刷新）。`game_init.init()` 会在主循环中 `call_default_flow()`。

## 7. 等待控制与鼠标状态

- **状态结构体**：`cache.wframe_mouse`（定义于 `game_type.WFrameMouse`）记录逐字/逐行输出状态、鼠标点击、是否跳过等待等标志位。
- **事件绑定**：`Script.Core.key_listion_event.on_wframe_listion()` 在 Tk 根窗口上绑定鼠标与键盘事件：
  - 左键：聚焦输入框并触发 `set_wframe_up()`。
  - 右键：开启跳过模式（`w_frame_skip_wait_mouse = 1`）。
  - 上/下方向键：遍历指令历史。
  - 回车：发送输入框内容。
- **等待逻辑**：`flow_handle.askfor_wait()` 在循环中检查 `cache.wframe_mouse.w_frame_up`；部分 `draw`（例如 `LineFeedWaitDraw`）与面板会依据 `w_frame_skip_wait_mouse` 决定是否自动继续。

## 8. 样式、文本宽度与对齐

- `Script.Core.text_handle`：
  - `get_text_index()` 使用 `wcwidth` 计算字符显示宽度，并去除类似 `<style>` 的样式标签。
  - `align()` 根据列数和宽度生成左右/居中对齐文本，广泛用于 `CenterDraw`/`LeftButton` 等。
- 样式数据来源于 `game_config.config_font` & `config_font_data`，`io_init.init_style()` 会注册所有组合样式（含 bold/underline/italic 修饰符）。
- `normal_config.config_normal.text_width` 决定单行宽度，是大多数 `draw` 对象的默认 `width`。

## 9. 图片与资源处理

- **图片加载**：`Script.Core.era_image` 在启动时扫描 `image/` 目录，将 `.png` 缩放后缓存为 `PhotoImage`。缩放比例与当前字体宽度相关 (`main_frame.normal_font.measure("A")`) ，保证图像与文本排版一致。
- **图片绘制**：
  - `draw.ImageDraw.draw()` 调用 `io_init.image_print()`。
  - `main_frame.read_queue()` 在 `textbox` 中 `image_create`。
  - 图片按钮 (`ImageButton`) 则通过 `io_print_image_cmd()` 绑定点击事件。

## 10. Tk 与 Web 的差异点

| 环节 | Tk 模式 | Web 模式 |
| --- | --- | --- |
| IO 入口 | `io_init` 本地实现 | `io_init` 代理到 `io_web` |
| 绘制类 | `draw.*` 直接调用 `io_init` | 启动时 `web_draw_adapter.apply_web_adapters()` monkey patch `draw.*`，把 `draw()` 输出记录到 `cache.current_draw_elements`|
| 命令绑定 | Tk tag 事件 + `_order_queue` | HTTP/WebSocket 事件，经 `web_server.update_game_state()` 分发 |
| 等待控制 | 使用 `cache.wframe_mouse` + Tk 事件 | 适配器在等待元素里追加 `await_input` 标记，前端负责触发 `flow_handle_web` |

了解差异有助于编写代码时避免写死 Tk 逻辑（如直接操作 Tk 控件）。

## 11. 扩展指引

1. **新增文本/组件**：
   - 优先复用 `draw.py` 中的基础类；若需自定义，保持 `draw()` 中只调用 `io_init`/`py_cmd` 等抽象层，避免直接引用 Tk API。
   - 若组件需要 Web 同步，确保在 `draw.py` 中新增的类同样能被 `web_draw_adapter` 适配（可仿照已有 `adapt_*`）。
2. **新增面板**：
   - 在 `Script/UI/Panel` 下建模块，组合 `draw.*` 与 `panel.*` 组件。
   - 通过 `handle_panel.add_panel` 注册到对应 Flow，或在行为循环中直接调用。
3. **新增样式**：更新 `data/csv` → `buildconfig.py` 生成配置，再调用 `io_init.init_style()` 时自动注册。
4. **新增图片**：放入 `image/`，注意命名与配置。需要差分立绘时使用 `角色名_xxx.png`，`era_image` 会自动建立索引。

## 12. 调试与排错建议

- **输出异常/乱码**：检查 `io_init.init_style()` 是否执行；确认字体文件是否被 `load_local_fonts()` 正常加载（查看控制台日志）。
- **命令点击无反应**：确认 `py_cmd.pcmd()` 绑定的 `cmd_id` 是否唯一，`flow_handle.cmd_map` 有对应条目；`io_init.clear_cmd()` 是否被提前清空。
- **等待卡死**：定位 `cache.wframe_mouse` 状态，确保在鼠标事件中正确设置 `w_frame_up`；必要时排查是否存在持续的 `askfor_wait()`。
- **图片不显示**：确认 `image/*.png` 名称与 `game_config.config_image` 中一致，`era_image.load_images_from_directory()` 控制台是否输出异常。
- **与 Web 共存**：扩展 Tk 专用逻辑前，先判断 `cache.web_mode`，必要时提供双实现或保持抽象层调用。

---

通过上述链路可以快速定位 Tk 渲染的各个环节：配置 → IO → 绘制组件 → 面板 → 行为循环。在开发新 UI 或排查显示问题时，优先确认是否遵循了这些抽象层，借助 `cache` 与 `flow_handle` 维护的状态避免直接操作底层 Tk 控件，从而兼容 Web 绘制并简化维护。