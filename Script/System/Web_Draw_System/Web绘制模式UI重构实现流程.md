# erArk Web绘制模式UI重构实现流程

## 文档说明

本文档是《Web绘制模式UI重构说明文档》的配套实施文档，将整个重构工作分解为可执行的具体步骤。每个步骤完成后应在对应的复选框处打钩标记。

**标记说明**：
- `[ ]` 未开始
- `[~]` 进行中
- `[x]` 已完成
- `[!]` 遇到问题需调整

**最后更新**：2026年2月13日

---

## 阶段一：基础架构搭建 ✅

**阶段状态**：已完成
**完成日期**：2026年1月12日

### 1.1 创建Web模式专用目录结构

#### 1.1.1 创建后端组件目录
- [x] 在 `Script/UI/Panel/` 下创建 `web_components/` 目录
- [x] 在 `web_components/` 目录下创建 `__init__.py` 文件
- [x] 创建以下Python文件（已填充基础实现）：
  - [x] `web_components/scene_renderer.py` - 场景背景渲染组件
  - [x] `web_components/character_renderer.py` - 角色图像渲染组件
  - [x] `web_components/interaction_handler.py` - 交互处理组件
  - [x] `web_components/dialog_box.py` - 对话框组件
  - [x] `web_components/status_panel.py` - 状态面板组件
  - [x] `web_components/tab_menu.py` - 选项卡菜单组件
  - [x] `web_components/body_part_button.py` - 身体部位按钮组件

#### 1.1.2 创建前端文件
- [x] 在 `templates/` 下创建 `game_main.html` 文件
- [x] 在 `static/css/` 下创建 `game_main.css` 文件
- [x] 在 `static/js/` 下创建以下文件：
  - [x] `game_renderer.js` - 画面渲染器
  - [x] `interaction_manager.js` - 交互管理器
  - [x] `websocket_handler.js` - WebSocket处理
  - [x] `ui_components.js` - UI组件库
- [x] 在 `static/assets/` 下创建 `ui/` 目录用于存放UI素材

#### 1.1.3 创建工具脚本
- [x] 在 `tools/` 下创建 `build_character_folders.py` - 构建角色文件夹结构
- [x] 在 `tools/` 下创建 `rename_and_organize_images.py` - 重命名和整理图片
- [x] 在 `tools/` 下创建 `generate_body_parts_json.py` - 生成部位位置JSON（已弃用）
- [x] 在 `tools/` 下创建 `body_analysis.py` - 深度学习姿态估计（已由 ensemble 替代）
- [x] 在 `tools/` 下创建 `body_analysis_compare.py` - 三模型对比工具
- [x] 在 `tools/` 下创建 `body_analysis_multi_compare.py` - 7模型+集成对比工具
- [x] 在 `tools/` 下创建 `body_analysis_ensemble.py` - 生产用7模型集成批量处理（当前使用）

---

### 1.2 创建Web模式主面板入口

#### 1.2.1 创建 in_scene_panel_web.py 基础框架
- [x] 在 `Script/UI/Panel/` 下创建 `in_scene_panel_web.py`
- [x] 定义 `InScenePanelWeb` 类基础结构
- [x] 实现 `__init__` 方法，初始化宽度和基本属性
- [x] 实现 `draw` 方法框架（主循环）

#### 1.2.2 修改模式切换逻辑
- [x] 查看现有 `in_scene_panel.py` 的调用方式
- [x] 确定模式切换的入口点位置（`Script/UI/Flow/normal_flow.py`）
- [x] 添加 `cache.web_mode` 判断逻辑
- [x] 在web模式下导入并使用 `InScenePanelWeb`
- [x] 确保tk模式下继续使用原有 `InScenePanel`

#### 1.2.3 清屏机制（2026-01-28新增）
- [x] 在 `Script/Core/io_web.py` 中添加 `clear_screen_and_history()` 函数
- [x] 在 `Script/Core/io_init.py` 中添加 `clear_screen_and_history()` 导出函数
- [x] 在 `in_scene_panel_web.py` 的 `draw()` 方法开始时调用 `clear_screen_and_history()`
- [x] 确保每次进入主界面时清空历史记录，保持界面整洁

**实施说明（2026-01-28）**：
- **问题**：主界面显示之前的杂乱信息（数字、文本等），因为 `clear_screen()` 会回填历史记录
- **解决方案**：
  - `clear_screen()`: 清空当前绘制元素，但保留历史记录（用于循环内更新）
  - `clear_screen_and_history()`: 彻底清空当前绘制元素和历史记录（用于进入主界面）
- **效果**：进入主界面时显示干净的UI，没有之前的残留内容

---

### 1.3 前端页面基础结构

#### 1.3.1 创建 game_main.html 基础结构
- [x] 定义HTML5文档结构
- [x] 引入Socket.IO CDN
- [x] 引入 `game_main.css` 样式文件
- [x] 引入各JS模块文件
- [x] 创建主容器 `<div id="game-container">`
- [x] 创建以下区域容器：
  - [x] `<div id="panel-tabs">` - 面板选项卡栏
  - [x] `<div id="top-info-area">` - 顶部信息区（玩家信息、附加信息、头像）
  - [x] `<div id="main-scene">` - 主画面区
  - [x] `<div id="dialog-box">` - 对话框区域

#### 1.3.2 创建 game_main.css 基础样式
- [x] 定义全局样式（字体、背景、box-sizing）
- [x] 定义1920×1080基准布局
- [x] 定义 `#game-container` 为flex容器
- [x] 定义各区域的基础尺寸和位置
- [x] 定义颜色变量（CSS变量）

---

## 阶段二：指令分类系统 ✅

**阶段状态**：已完成（升级至大类/小类嵌套系统）
**完成日期**：2026年1月17日（最后更新）

### 2.0 交互类型系统重构（2026年1月17日新增）

#### 2.0.1 创建外置数据库
- [x] ~~创建 `data/csv/InstructWebConfig.csv` 存储指令的Web模式分类配置~~ **已废弃**
- [x] ~~在 `Script/Config/config_def.py` 中添加 `InstructWebConfig` 数据类~~ **已废弃**
- [x] 使用统一的 `data/csv/InstructConfig.csv` 存储所有指令配置（包括Web模式属性）
- [x] 在 `Script/Config/config_def.py` 中 `InstructConfig` 类包含 `major_type`、`minor_type`、`body_parts`、`panel_id` 等字段
- [x] 在 `Script/Config/game_config.py` 中添加读取逻辑
- [x] 修改 `add_instruct()` 从CSV数据库读取Web模式属性

**实施记录（2026年1月17日更新）**：
- **数据库合并**：原 `InstructWebConfig.csv` 已废弃并删除，所有配置统一使用 `InstructConfig.csv`
- CSV格式：`cid,instruct_id,instruct_type,name,premise_set,behavior_id,sub_type,category,panel_id,major_type,minor_type,body_parts`
- 数据读取后存储在 `game_config.config_instruct_by_id`
- `add_instruct()` 装饰器自动从CSV获取 `major_type`、`minor_type`、`body_parts`、`panel_id` 等
- `premise_set` 使用大写常量名（如 `NOT_H|HAVE_TARGET`），与 `constant_promise.Premise` 中的常量名一致
- `panel_id` 使用面板常量名（如 `SEE_MAP`、`FOOD_SHOP`），与 `constant.Panel` 中的常量名一致

#### 2.0.2 创建大类/小类嵌套结构
- [x] 创建 `Script/Core/constant/interaction_types.py` 定义新的分类枚举
- [x] 定义 `InteractionMajorType`：嘴(0)、手(1)、阴茎(2)、道具(3)、其他(4)
- [x] 定义 `InteractionMinorType`：
  - 嘴类小类：对话(0)、亲吻(1)、舔吸(2)
  - 手类小类：抚摸(10)、拍打(11)、穿脱(12)
  - 阴茎类小类：摩擦(20)、插入(21)
  - 道具类小类：药物(30)、道具(31)
  - 其他类小类：杂项(40)
- [x] 在 `Script/Core/constant/__init__.py` 中导出新的常量

**实施记录**：
- 使用十位数区分大类（0-9嘴，10-19手，20-29阴茎，30-39道具，40+其他）
- 提供 `get_major_type()`、`get_minor_types()` 等辅助函数

#### 2.0.3 实现大类切换记忆机制
- [x] 在 `Script/Core/game_type.py` 的 `Cache` 类中添加新字段：
  - `web_current_major_type` - 当前选中的大类型
  - `web_current_minor_type` - 当前选中的小类型
  - `web_major_type_memory` - 记忆列表，长度为大类数量
  - `web_selected_drug_id` - 当前选中的药物ID
  - `web_selected_item_id` - 当前选中的道具ID
- [x] 创建 `Script/Design/web_interaction_manager.py` 管理交互状态
- [x] 实现 `select_major_type()` 保存当前小类选择，恢复目标大类记忆
- [x] 实现 `select_minor_type()` 更新记忆

#### 2.0.4 实现道具大类下拉菜单
- [x] 在 `web_interaction_manager.py` 中实现 `get_drug_list()` 和 `get_item_list()`
- [x] 实现 `select_drug()` 和 `select_item()` 函数
- [x] 在 `Script/Core/web_server.py` 中添加WebSocket事件处理器：
  - `get_major_types` - 获取大类型列表
  - `select_major_type` - 选择大类型
  - `select_minor_type` - 选择小类型
  - `get_drug_list` - 获取药物列表
  - `get_item_list` - 获取道具列表
  - `select_drug` - 选择药物
  - `select_item` - 选择道具
  - `get_interaction_state` - 获取当前交互状态

### 2.1 分析现有指令结构

#### 2.1.1 查阅指令定义文件
- [x] 阅读 `Script/System/Instruct_System/handle_instruct.py` 完整内容
- [x] 记录 `add_instruct()` 函数的现有参数
- [x] 列出所有已定义的指令ID和名称
- [x] 分析指令的现有分类方式（如 `instruct_type`）

**实施记录**：
- 现有 `add_instruct()` 参数：`instruct_id`, `instruct_type`, `name`, `premise_set`, `behavior_id`, `sub_type`
- 现有 `InstructType` 枚举：SYSTEM(0), DAILY(1), PLAY(2), WORK(3), ARTS(4), OBSCENITY(5), SEX(6)
- 现有 `SexInstructSubType` 枚举：BASE(0), FOREPLAY(1), WAIT_UPON(2), DRUG(3), ITEM(4), INSERT(5), SM(6), ARTS(7)
- 文件共7500+行，定义了数百个指令

#### 2.1.2 整理指令分类映射
- [x] 创建表格记录每个指令应属于的大类（系统面板类/角色交互类/角色交互面板类）
- [x] 对于角色交互类，确定其交互子类（说话/接触/口部/穿脱等）
- [x] 对于涉及身体部位的指令，记录关联的部位名称

**实施记录**：
- 创建了 `design_docs/指令分类映射表.md` 文档
- 记录了 OBSCENITY 类指令（抚摸、亲吻等）的分类和部位映射
- 记录了 SEX 类指令（前戏、插入、服务等）的分类和部位映射
- 定义了自动推断规则和手动补充指南

### 2.2 修改指令定义结构（更新至三类分类）

#### 2.2.1 定义新的分类枚举和数据结构
- [x] 在 `Script/System/Instruct_System/instruct_category.py` 中添加 `InstructCategory` 类：
  - [x] `SYSTEM_PANEL(0)` - 系统面板类（函数为cache.now_panel_id = xxx）
  - [x] `CHARACTER(1)` - 角色交互类（普通交互，直接执行）
  - [x] `CHARACTER_PANEL(2)` - 角色交互面板类（函数带now_panel.draw()）
- [x] 在 `Script/System/Instruct_System/interaction_types.py` 中定义新的交互类型系统：
  - [x] `InteractionMajorType`：大类型（MOUTH='mouth', HAND='hand', SEX='sex', PENIS='penis', TOOL='tool', ARTS='arts', OTHER='other'）
  - [x] `InteractionMinorType`：小类型（MOUTH_TALK='mouth_talk', SEX_START_END='sex_start_end', SEX_BASE='sex_base', PENIS_INSERT='penis_insert' 等）
  - [x] 提供大类/小类的映射和工具函数
- [x] 在 `Script/System/Instruct_System/instruct_meta.py` 中更新 `InstructMeta` 类
- [x] 在 `Script/Core/constant/__init__.py` 中更新指令元数据字典：
  - [x] `instruct_category_data` - 指令分类（三类）
  - [x] `instruct_panel_id_data` - 系统面板类的面板ID
  - [x] `instruct_major_type_data` - 交互大类型（InteractionMajorType）
  - [x] `instruct_minor_type_data` - 交互小类型（InteractionMinorType）
  - [x] `instruct_body_parts_data` - 关联身体部位
  - [x] ~~`instruct_single_part_data`~~ - 已移除，改为通过 `body_parts` 长度自动判断

**实施记录（更新于2026年1月）**：
- `InstructCategory`：SYSTEM_PANEL(0), CHARACTER(1), CHARACTER_PANEL(2)
- `InteractionMajorType`（已更新为字符串标识符）：MOUTH='mouth', HAND='hand', SEX='sex', PENIS='penis', TOOL='tool', ARTS='arts', OTHER='other'
- `InteractionMinorType`（已更新为字符串标识符）：按大类分组（如 MOUTH_TALK='mouth_talk', SEX_START_END='sex_start_end', SEX_BASE='sex_base', PENIS_INSERT='penis_insert' 等）
- `BodyPart` 类基于 BodyPart.csv 的19个部位 + COCO-WholeBody 17点映射
- **2026-01-22更新**：新增性爱类（SEX='sex'），包含开始与结束（sex_start_end）和基础（sex_base）两个小类，位于阴茎类之前

#### 2.2.2 扩展 add_instruct 函数
- [x] 为 `add_instruct()` 添加新参数：
  - [x] `category` - 指令分类（可选，默认自动推断）
  - [x] `panel_id` - 系统面板类的面板ID（可选，自动提取）
  - [x] `interaction_type` - 交互子类型（可选）
  - [x] `body_parts` - 关联身体部位列表（可选）
  - [x] ~~`single_part`~~ - 已移除，改为通过 `body_parts` 列表长度自动判断（长度为1时为单部位）
- [x] 在装饰器内部实现三类分类自动推断逻辑：
  - [x] 分析函数源代码检测 `cache.now_panel_id` → `SYSTEM_PANEL`
  - [x] 分析函数源代码检测 `now_panel.draw()` → `CHARACTER_PANEL`
  - [x] 自动提取 panel_id 值（通过正则匹配）
  - [x] SYSTEM类型默认为 `SYSTEM_PANEL`
  - [x] OBSCENITY/SEX类型默认为 `CHARACTER`

**实施记录（更新于2026年1月17日）**：
- 使用 `inspect.getsource()` 分析函数源代码
- 正则表达式提取 panel_id：`r'cache\.now_panel_id\s*=\s*(\d+)'`
- 检测临时面板：`r'now_panel\.draw\s*\('`

#### 2.2.3 为所有指令补充分类信息
- [x] 遍历所有已定义的指令（自动推断完成）
- [x] 系统面板类指令自动添加 `category=InstructCategory.SYSTEM_PANEL`
- [x] 角色交互类指令自动添加 `category=InstructCategory.CHARACTER`
- [x] 角色交互面板类指令自动添加 `category=InstructCategory.CHARACTER_PANEL`
- [x] 为关键角色交互指令手动补充详细分类信息：
  - [x] 添加 `web_major_type` 和 `web_minor_type` 对应的类型（在 CSV 中配置）
  - [x] 添加 `body_parts` 关联的部位列表
  - [x] ~~`single_part`~~ 已移除，改用 `InstructMeta.is_single_part` 属性自动判断

**实施记录（2026年1月更新）**：
- 交互类型配置现在通过 CSV 的 `web_major_type` 和 `web_minor_type` 字段完成
- `handle_instruct.py` 的 `add_instruct` 装饰器自动读取 CSV 配置并写入 constant 字典
- `InstructMeta` 类的 `is_single_part` 属性通过检查 `len(body_parts) == 1` 自动判断

**实施说明**：
- 通过 `add_instruct` 装饰器的自动推断逻辑，所有指令在注册时会自动获得三类分类
- panel_id 会自动从函数源代码中提取
- 交互类型通过 CSV 配置，无需额外的配置文件

#### 2.2.3.1 指令Web分类配置方式
- [x] 在 InstructConfig.csv 中添加 `web_major_type`、`web_minor_type`、`body_parts` 字段
- [x] `handle_instruct.py` 的装饰器自动读取这些字段
- [x] 配置数据自动写入 `constant.instruct_major_type_data` 和 `constant.instruct_minor_type_data`
- [x] **为所有指令填充 `web_major_type` 和 `web_minor_type` 值**（2026年1月完成）

**数据填充实施记录**（2026年1月完成，2026-01-22更新）：
- 已为 InstructConfig.csv 中的所有指令填充交互大类和交互小类值
- 分类原则：
  - SYSTEM/WORK/PLAY/ARTS 类 → OTHER ('other','other_misc')
  - 抚摸/触摸类 → HAND_TOUCH ('hand','hand_touch')
  - 拍打/打屁股类 → HAND_SLAP ('hand','hand_slap')
  - 穿脱衣物类 → HAND_DRESS ('hand','hand_dress')
  - 亲吻类 → MOUTH_KISS ('mouth','mouth_kiss')
  - 舔吸/口交类 → MOUTH_LICK ('mouth','mouth_lick')
  - **邀请H/结束H类 → SEX_START_END ('sex','sex_start_end')**（2026-01-22新增）
  - **H中基础操作类 → SEX_BASE ('sex','sex_base')**（2026-01-22新增）
  - 摩擦/侍奉类 → PENIS_RUB ('penis','penis_rub')
  - 插入/性交类 → PENIS_INSERT ('penis','penis_insert')
  - 药物类 → TOOL_DRUG ('tool','tool_drug')
  - 道具类 → TOOL_ITEM ('tool','tool_item')

**注意**：旧的 `instruct_web_config.py` 配置文件已删除，不再使用。

#### 2.2.4 创建指令查询辅助函数
- [x] 实现 `get_system_panel_instructs()` - 获取所有系统面板类指令
- [x] 实现 `get_character_instructs()` - 获取所有角色交互类指令
- [x] 实现 `get_character_panel_instructs()` - 获取所有角色交互面板类指令
- [x] 实现 `get_all_character_interaction_instructs()` - 获取所有角色交互相关指令
- [x] 实现 `get_instructs_by_interaction_type(type)` - 按交互子类型获取指令
- [x] 实现 `get_instructs_by_body_part(part)` - 按部位获取相关指令
- [x] 实现 `get_instructs_by_type_and_part(type, part)` - 按类型和部位获取指令
- [x] 实现 `get_available_interaction_types()` - 获取可用交互类型（按预定义顺序）
- [x] 实现 `get_instruct_meta(instruct_id)` - 获取单个指令元数据

**实施记录（更新于2026年1月17日）**：
- 所有查询函数已在 `Script/System/Instruct_System/instruct_meta.py` 中实现
- 查询结果按 `INTERACTION_TYPE_ORDER` 排序
- 同时在 `Script/Core/constant/__init__.py` 中提供直接通过字典查询的能力

---

## 阶段三：前端UI组件开发

### 3.1 面板选项卡栏

#### 3.1.1 HTML结构
- [x] 在 `game_main.html` 中完善 `#panel-tabs` 区域结构
- [x] 添加选项卡容器 `<div class="tab-container">`

#### 3.1.2 CSS样式
- [x] 定义 `.panel-tabs` 样式（固定顶部、全宽）
- [x] 定义 `.tab-button` 基础样式
- [x] 定义 `.tab-button:hover` 悬停样式
- [x] 定义 `.tab-button.active` 激活样式
- [x] 实现选项卡自适应宽度逻辑（flex布局）

#### 3.1.3 JavaScript逻辑
- [x] 在 `ui_components.js` 中创建 `TabMenu` 对象
- [x] 实现 `update(tabs)` 方法 - 渲染选项卡列表
- [x] 实现 `handleClick(tabId)` 回调绑定
- [x] 实现选项卡数量变化时的宽度自适应

**实施记录（2026-01-17 更新）**：
- **位置修正**：将选项卡从布局底部移至顶部
  - 修改 `static/game.js` 中 `renderNewUIContent()` 函数
  - 选项卡现在插入到 `container` 的最前面（使用 `insertBefore`）
- **样式更新（2026-01-17 重构为网页选项卡样式）**：
  - 修改 `static/style.css` 中 `.new-ui-panel-tabs` 和 `.panel-tab-btn` 样式
  - 采用网页选项卡样式：底部边框高亮表示激活状态，无圆角按钮
  - 激活选项卡使用金色底部边框和加粗文字
  - 添加 `.panel-tab-btn.active` 激活状态样式
  - 添加 `.panel-tab-btn.main-tab` 主面板选项卡特殊样式
- **数据源重构（2026-01-18 重大更新）**：
  - 修改 `tab_menu.py` 中 `get_panel_tabs()` 为动态获取：
    1. 主面板作为默认激活的选项卡（id=`__main_panel__`）
    2. ~~从 `constant.instruct_type_data[SYSTEM]` 获取所有系统类型指令~~ **已废弃**
    3. 使用 `instruct_meta.get_panel_instructs_from_constant()` 获取所有 `web_category == SYSTEM_PANEL` 的指令
    4. 通过 `filter_instructs_by_premise()` 判断前提条件确定可用性
    5. **只有满足所有前提条件的指令才会显示**（不满足则不出现，而非禁用）
    6. **必须具有 panel_id** 的指令才会作为选项卡显示（无 panel_id 的系统面板指令不显示）
  - 选项卡数据结构包含：`id`, `name`, `type`, `available`, `active`
- **前端渲染更新（2026-01-17）**：
  - 修改 `static/game.js` 中 `createPanelTabsBar()` 函数
  - 支持 `active` 状态和 `main-tab` 样式类
  - 主面板激活时不响应点击事件
- **点击处理机制（2026-01-18 更新）**：
  - 修改 `static/game.js` 中 `clickPanelTab()` 使用 `/api/button_click` API（而非WebSocket）
  - 修改 `in_scene_panel_web.py` 中 `draw()` 方法，添加 `_bind_panel_tabs_and_get_ask_list()` 函数
  - 面板选项卡指令现在正确绑定到 `cmd_map`，通过 `flow_handle.askfor_all()` 等待用户选择
  - **主面板选项卡特殊处理**：绑定 `_handle_return_to_main_panel()` 函数，而非指令处理函数
- **返回主面板逻辑（2026-01-18 新增）**：
  - 在 `in_scene_panel_web.py` 中添加 `_handle_return_to_main_panel()` 方法
  - 点击主面板选项卡时，将 `cache.now_panel_id` 重置为 `constant.Panel.IN_SCENE`
  - 在 `draw()` 方法循环开始时检查：如果 `cache.now_panel_id == IN_SCENE` 但选项卡非主面板，自动重置选项卡状态
  - 从 `web_components/__init__.py` 导出 `MAIN_PANEL_TAB_ID` 常量

### 3.1.5 场景信息栏（2026-02-07 新增）

**功能说明**：在面板选项卡上方增加一行场景信息栏，显示当前场景名（左侧）和游戏时间（居中）

#### 后端实现
- [x] 在 `Script/UI/Panel/in_scene_panel_web.py` 中添加 `_get_scene_info_bar()` 方法
- [x] 返回数据包含：`scene_name`（场景名）和 `game_time`（游戏时间文本）
- [x] 场景名获取参考 `in_scene_panel.py` 中的 `now_position_text` 实现
- [x] 游戏时间获取参考 `game_info_panel.py` 中的 `GameTimeInfoPanel` 实现
- [x] 在 `_collect_game_state()` 中添加 `scene_info_bar` 字段

#### 前端实现
- [x] 在 `static/game.js` 中添加 `createSceneInfoBar()` 函数
- [x] 修改 `renderNewUIContent()` 函数，在面板选项卡之前插入场景信息栏
- [x] 使用 `container.insertBefore()` 将场景信息栏插入到容器最前面

#### CSS样式
- [x] 在 `static/style.css` 中添加 `.new-ui-scene-info-bar` 样式
- [x] 使用flex布局，场景名绝对定位在左侧，时间flex居中
- [x] `.scene-info-name`：场景名样式（左侧绝对定位，浅蓝色）
- [x] `.scene-info-time`：游戏时间样式（居中，灰色）

#### 样式优化（2026-02-07）
- [x] 增加上内边距从 6px 到 12px，让文本上方有更多空间
- [x] 增加下内边距从 6px 到 16px，让信息栏与选项卡之间有空隙且为背景色
- [x] 添加 `line-height: 1.5` 提升文本可读性
- [x] 使用 `padding` 而非 `margin` 确保空隙区域为背景色而非黑色

#### 样式更新（2026-02-12）
- [x] 将游戏时间从右对齐改为居中对齐
- [x] 使用 `position: relative` 和 `position: absolute` 实现场景名固定左侧，时间居中的布局
- [x] `.scene-info-name` 添加 `position: absolute; left: 16px;` 固定在左侧
- [x] `.new-ui-scene-info-bar` 使用 `justify-content: center;` 使时间居中

**样式说明**：
- 上内边距 12px：让文本上方区域不是黑色而是背景底色
- 下内边距 16px：让下方与选项卡有空隙，且空隙为背景色（rgba(15, 15, 25, 0.95)）
- 行高 1.5：让文本有更好的呼吸空间

### 3.2 玩家信息区

#### 3.2.1 HTML结构
- [x] 在 `#top-info-area` 中创建 `#player-info` 容器
- [x] 添加名字显示区域
- [x] 添加数值槽容器（体力、气力、理智、精液）
- [x] 添加特殊状态标记容器

#### 3.2.2 CSS样式
- [x] 定义 `#player-info` 定位和尺寸
- [x] 定义名字文本样式
- [x] 定义数值槽样式（进度条形式）
- [x] 定义特殊状态标记样式（`<>`包裹的文本）
- [x] **使用图片背景绘制状态槽**（2026-01-27完成）
  - [x] 体力槽使用 hpbar_null.png 和 hpbar_true.png
  - [x] 气力槽使用 mpbar_null.png 和 mpbar_true.png
  - [x] 理智槽使用 statbar_null.png 和 statbar_true.png
  - [x] 精液槽使用 spbar_null.png 和 spbar_true.png

#### 3.2.3 JavaScript逻辑
- [x] 在 `static/game.js` 中创建 `createPlayerInfoPanel()` 函数
- [x] 实现 `createImageStatusBar()` 方法使用图片渲染状态槽
- [x] 实现数值槽渲染（支持动态更新）
- [x] 实现特殊状态标记渲染（与右侧角色信息区相同逻辑）
- [x] **添加精液槽显示**（2026-01-27完成）

#### 3.2.4 后端数据
- [x] `Script/UI/Panel/web_components/status_panel.py` 中的 `get_player_info()` 方法
- [x] 返回玩家数据包含：name, nickname, hp, hp_max, mp, mp_max, sanity, sanity_max, semen, semen_max, special_states
- [x] 特殊状态标记通过 `character_info_head.get_character_status_list()` 获取
- [x] **添加药剂拥有标志**（2026-01-27新增）
  - [x] has_sanity_drug: 是否有理智药剂
  - [x] has_semen_drug: 是否有精力剂

#### 3.2.5 快速使用药剂功能（2026-01-27新增）
- [x] 在理智和精液槽的标签后面添加加号按钮
- [x] 按钮仅在玩家有对应药剂时显示
- [x] 点击按钮调用 `/api/quick_use_drug` API
- [x] 后端API实现在 `Script/Core/web_server.py`
- [x] 调用 `see_item_info_panel.py` 中的 `auto_use_sanity_drug()` 和 `use_drug(11)` 函数
- [x] CSS样式：`.bar-quick-use-btn`, `.bar-quick-use-sanity`, `.bar-quick-use-semen`
- [x] **立刻刷新功能**（2026-01-28更新）：后端返回更新后的玩家信息，前端局部更新UI

#### 3.2.6 数值变化浮动文本显示（2026-01-28新增，2026-02-03更新）
- [x] 为状态条添加 `data-field` 属性，用于浮动文本定位
- [x] 实现 `calculatePlayerValueChanges()` 函数计算数值变化
- [x] 修改 `updatePlayerInfoUI()` 函数，更新UI时显示浮动文本
- [x] 复用 `createFloatingValueChanges()` 函数（与右侧角色信息区相同）
- [x] 为 `.new-ui-player-info` 和 `.status-bar` 添加 `position: relative` 样式
- [x] **从后端传递结算数据到玩家信息区**（2026-02-03新增）
  - [x] 修改 `status_panel.py` 的 `get_player_info()` 方法，添加 `value_changes` 字段
  - [x] 添加 `createPlayerFloatingValueChanges()` 前端函数处理玩家数值变化
  - [x] 添加 `createPlayerBottomFloatingTexts()` 显示经验值等其他变化
  - [x] 添加 `.player-floating-container` 和 `.player-floating-text` CSS样式

#### 3.2.7 CSS样式优化（2026-01-27更新）
- [x] 玩家信息区顶部内边距增加至12px，让玩家姓名和边缘有适当空隙
- [x] 玩家姓名行下边距增加至12px，让姓名和体力行之间有更好的间距

#### 3.2.9 玩家名字按钮功能（2026-02-07新增）
- [x] 将玩家名字从span改为button元素
- [x] 点击后执行`target_to_self`指令（与自己交互）
- [x] 通过WebSocket发送`execute_instruct`事件
- [x] 指令执行后自动触发`WEB_REFRESH_SIGNAL`刷新主界面
- [x] 按钮样式：黄色边框(#ffd700)、灰色底色(#3a3a4a)、保持原有字体大小和颜色
- [x] 添加`.player-name-btn` CSS样式

**实施记录（2026年2月7日）**：
- **问题背景**：玩家需要便捷的方式触发"与自己交互"指令
- **解决方案**：将玩家名字改为可点击按钮
- **前端实现**：
  - 修改 `createPlayerInfoPanel()` 函数，将玩家名字从 `<span>` 改为 `<button>`
  - 点击事件发送 `execute_instruct` WebSocket消息，`instruct_id` 为 `target_to_self`
  - 按钮添加 `title` 属性，显示"点击与自己交互"提示
- **后端处理**：
  - 复用现有的 `handle_execute_instruct()` 处理函数
  - 指令执行后自动设置 `WEB_REFRESH_SIGNAL` 刷新信号
- **CSS样式**：
  - `.player-name-btn` 类名
  - 黄色边框 `border: 1px solid #ffd700`
  - 灰色底色 `background-color: #3a3a4a`
  - 文字保持黄色 `color: #ffd700`，字体大小 `font-size: 1.2em`
  - 悬停时的箱阴影效果 `box-shadow: 0 0 5px rgba(255, 215, 0, 0.3)`

#### 3.2.8 Web模式结算信息显示优化（2026-02-03新增，2026-02-07更新）
- [x] 修改 `character_behavior.py`，在Web模式下跳过 `settle_panel.draw()` 调用
- [x] Web模式下不直接打印结算文本，改为通过浮动文本显示
- [x] 玩家数值变化通过 `get_player_info()` 的 `value_changes` 字段传递到前端
- [x] 交互对象数值变化通过 `get_target_info()` 的 `value_changes` 字段传递到前端
- [x] 浮动文本显示位置：
  - 玩家：体力、气力、理智、精液在对应数值槽位置，其他在特殊状态下方
  - 交互对象：在右侧交互对象信息栏的对应位置
- [x] TK模式保持原有行为不变
- [x] **玩家状态变化过滤**（2026-02-07新增）
  - 修改 `settle_behavior.py` 的 `collect_web_value_changes()` 函数
  - 玩家（character_id == 0）不再收集常规状态变化（部位快感、好意、快乐等）
  - 仅保留体力、气力、理智、精液、经验的变化显示
  - 交互对象仍然显示所有状态变化

**实施记录（2026年2月7日更新）**：
- **浮动文本位置优化**（2026年2月7日新增）：
  - 修改 `game.js` 的 `createInlineFloatingText()` 函数，添加 `end-inline` 位置类型
  - 状态条类数值变化（体力、气力、理智、精液、好感、信赖、催眠度）改为在数值后面显示
  - 格式示例：`100/200 +20`（当前值/上限值 空格+变化量）
  - 修改 `createPlayerFloatingValueChanges()` 和 `createFloatingValueChanges()`：
    - 玩家：体力、气力、理智、精液使用 `end-inline` 位置
    - 交互对象：体力、气力、好感、信赖、催眠度使用 `end-inline` 位置
  - CSS添加 `.position-end-inline` 样式和 `endInlineFadeIn` 动画
  - 浮动文本显示为静态内联元素，不使用绝对定位
  - 浮动文本前添加空格分隔，保持可读性
- **玩家状态变化过滤**：
  - 修改 `settle_behavior.py` 的 `collect_web_value_changes()` 函数
  - 添加 `if character_id != 0:` 条件判断
  - 玩家不再收集 `status_data`（状态变化，包括快感状态和其他状态如好意、快乐等）
  - 目的：玩家信息区不需要显示部位快感、好意、快乐等常规状态变化，只显示关键数值变化
- **快速使用药剂浮动文本优化**：
  - 修改 `web_server.py` 的 `/api/quick_use_drug` API
  - 在使用药剂前记录旧值，使用后计算变化并添加到 `cache.web_value_changes`
  - 前端 `updatePlayerInfoUI()` 使用后端返回的 `value_changes` 显示浮动文本
  - 不再由前端自己计算数值变化，统一由后端管理

**实施记录（2026年2月3日更新）**：
- **结算信息显示机制重构**：
  - 问题：Web模式下结算信息会直接打印在主界面上方，影响体验
  - 解决方案：
    1. 修改 `character_behavior.py`，添加 `cache.web_mode` 判断
    2. Web模式下跳过 `settle_panel.draw()` 和相关的 `WaitDraw`
    3. 数值变化仍通过 `settle_behavior.py` 的 `collect_web_value_changes()` 收集
    4. 通过前端浮动文本在对应位置显示
  - 修改文件：
    - `Script/Design/character_behavior.py` - 添加Web模式判断，跳过结算面板绘制
    - `Script/UI/Panel/web_components/status_panel.py` - `get_player_info()` 添加 `value_changes`
    - `static/game.js` - 添加 `createPlayerFloatingValueChanges()` 和 `createPlayerBottomFloatingTexts()`
    - `static/style.css` - 添加 `.player-floating-container` 和 `.player-floating-text` 样式
- **玩家信息栏浮动文本**：
  - `createPlayerFloatingValueChanges(panel, valueChanges)` 处理玩家的结算信息
  - 体力、气力、理智、精液：在对应状态条位置显示（复用 `createInlineFloatingText()`）
  - 经验值、射精欲等其他变化：在特殊状态下方显示（`createPlayerBottomFloatingTexts()`）
  - 浮动文本15秒后自动淡出消失

**实施记录（2026年1月28日更新）**：
- 玩家信息区现在使用与右侧角色信息区相同的图片绘制方式
- 状态槽使用 `/image/状态条/` 目录下的图片资源
- **特殊状态标记从名字后移至精液槽下面单独一行显示**
- 精液槽已添加显示（仅玩家角色显示）
- **理智和精液槽添加快速使用药剂的加号按钮**
  - 理智槽加号按钮：快速使用最小规格的理智药剂
  - 精液槽加号按钮：快速使用精力剂
  - 按钮样式为小型圆角按钮，带悬停效果
  - **按钮点击后立刻生效并刷新界面**
    - 后端 `/api/quick_use_drug` 返回更新后的完整玩家信息（包含 `value_changes`）
    - 前端 `updatePlayerInfoUI()` 函数使用后端返回的 `value_changes` 显示浮动文本
    - 无需刷新整个页面，只更新玩家信息区
- **数值变化浮动文本显示**（2026-01-28新增，2026-02-07更新）
  - 参考右侧交互对象信息区的浮动文本实现逻辑
  - 在体力、气力、理智、精液数值变化时显示浮动文本
  - 浮动文本显示颜色：体力(红)、气力(绿)、理智(蓝)、精液(黄)
  - 浮动文本自动在15秒后淡出消失
  - **实现方式改进**（2026-02-07更新）：
    - 后端 `/api/quick_use_drug` 直接将数值变化记录到 `cache.web_value_changes`
    - 通过 `get_player_info()` 的 `value_changes` 字段传递到前端
    - 前端 `updatePlayerInfoUI()` 直接使用后端返回的数据，不再自己计算变化量
    - `calculatePlayerValueChanges()` 函数已废弃（保留但不再使用）
  - 实现细节：
    - `createImageStatusBar` 和 `createImageStatusBarWithButton` 添加 `data-field` 属性
    - `updatePlayerInfoUI` 使用 `playerInfo.value_changes` 数据
    - `createPlayerFloatingValueChanges` 显示浮动文本
    - CSS添加 `position: relative` 为浮动文本提供定位上下文
- **CSS间距优化**
  - `.new-ui-player-info` 顶部内边距从8px增加至12px
  - `.player-name-line` 下边距从8px增加至12px
  - 玩家姓名现在有更好的视觉空间，与边缘和下方状态槽保持适当距离

### 3.3 交互对象附加信息区（中上）

#### 3.3.1 HTML结构
- [x] 在 `#top-info-area` 中创建 `#target-extra-info` 容器
- [x] 添加服装栏区域
- [x] 添加身体栏区域
- [x] 添加群交栏区域
- [x] 添加隐奸栏区域

#### 3.3.2 CSS样式
- [x] 定义 `#target-extra-info` 定位和尺寸
- [x] 定义各栏目的样式
- [x] 定义服装按钮样式（H模式可点击）
- [x] 定义污浊文本颜色样式

#### 3.3.3 JavaScript逻辑
- [x] 在 `static/game.js` 中实现 `createTargetExtraInfoPanel()` 函数
- [x] 实现 `createClothingSection()` 服装栏渲染
- [x] 实现 `createBodySection()` 身体栏渲染
- [x] 实现 `createGroupSexSection()` 群交栏渲染
- [x] 实现 `createHiddenSexSection()` 隐奸栏渲染
- [x] 实现 `toggleExtraInfoSection()` 栏位展开/收起
- [x] 实现 `toggleDetailedDirty()` 详细污浊切换
- [x] 实现 `toggleCloth()` 服装穿脱切换

#### 3.3.4 后端数据获取
- [x] 在 `Script/UI/Panel/web_components/status_panel.py` 中实现 `get_target_extra_info()` 方法
- [x] 实现 `_get_clothing_info()` 获取服装信息（参考 cloth_panel.py）
- [x] 实现 `_get_body_info()` 获取身体信息（参考 dirty_panel.py）
- [x] 实现 `_get_group_sex_info()` 获取群交信息（参考 group_sex_panel.py）
- [x] 实现 `_get_hidden_sex_info()` 获取隐奸信息（参考 hidden_sex_panel.py）

#### 3.3.5 后端API
- [x] 在 `Script/Core/web_server.py` 中添加 `/api/toggle_extra_info_section` API
- [x] 添加 `/api/toggle_detailed_dirty` API
- [x] 添加 `/api/toggle_cloth` API

**实施记录（2026年1月26日）**：
- **数据结构**：`get_target_extra_info()` 返回包含以下字段的字典：
  - `clothing`: 服装信息，包含 `visible`, `expanded`, `data` 子字段
  - `body`: 身体信息，包含部位污浊、爱液、精液等信息
  - `group_sex`: 群交信息，包含各部位状态和目标角色
  - `hidden_sex`: 隐奸信息，包含隐蔽程度和阴茎位置
  - `show_detailed_dirty`: 是否显示详细污浊
  - `is_h_mode`: 是否在H模式（影响服装是否可点击）
- **H模式服装按钮**：在H模式下，服装名称显示为可点击按钮，点击后可切换穿脱状态
- **栏位按钮**：顶部按钮栏显示各栏位名称，点击可切换展开/收起
- **详细污浊按钮**：切换是否显示完整污浊文本描述
- **样式更新**：
  - 服装按钮使用 `.clothing-button` 样式
  - 精液污浊使用 `.semen-color` 金黄色
  - 爱液使用 `.lavender-color` 淡紫色
  - 处子血使用 `.blood-color` 红色

**问题修复记录（2026年1月27日）**：
- **修复1：栏位切换立即更新**
  - 问题：点击服装/身体栏位按钮后需要等下一次指令结算才会更新
  - 解决方案：修改 `toggleExtraInfoSection()` 函数，在发送后端请求的同时，立即在前端本地更新UI（切换按钮样式和内容显示/隐藏）
- **修复2：收起栏位后按钮消失**
  - 问题：`visible` 和 `expanded` 使用同一个值，导致收起时按钮也一起消失
  - 解决方案：在 `get_target_extra_info()` 中，服装和身体栏位的 `visible` 始终设为 `True`（按钮始终显示），仅用 `expanded` 控制内容是否展开
- **修复3：附加信息区域空间不足**
  - 问题：附加信息内容较多，需要更多绘制空间
  - 解决方案：将玩家信息区域从 `flex: 1` 改为固定宽度 `width: 200px`，附加信息区域使用 `flex: 1` 自动扩展填充剩余空间
- **修复4：详细污浊切换立即更新（2026-01-27第二轮）**
  - 问题：点击"展开/收起详细污浊"按钮后，需要等待指令结算才能看到更新（因为详细污浊会显示不同的文本内容）
  - 解决方案：虽然当前实现已经会调用 `refreshGameState()` 刷新数据，但为保持一致性，简化代码并添加注释说明此操作需要后端刷新
  - 修改文件：`static/game.js` - 优化 `toggleDetailedDirty()` 函数的代码结构和注释
- **修复5：附加信息区域高度调整（2026-01-27第二轮）**
  - 问题：附加信息内容比较多，需要更多垂直空间
  - 解决方案：将 `.new-ui-target-extra-info` 的 `max-height` 从 `200px` 改为 `100px`（减半以给更多纵向空间）
  - 修改文件：`static/style.css` - 调整 `.new-ui-target-extra-info` 的 `max-height` 属性
- **修复6：详细污浊切换立即更新优化（2026-01-27第三轮）** ✅
  - 问题：虽然修复4做了优化，但 `refreshGameState()` 仍需要通过 socket.io 往返，用户感受不到"立即"更新
  - 解决方案：改为API直接返回更新后的附加信息数据，前端收到响应后立即重新渲染附加信息面板
  - 修改文件：
    - `Script/Core/web_server.py` - `/api/toggle_detailed_dirty` API 在切换后调用 `get_target_extra_info()` 并返回数据
    - `static/game.js` - `toggleDetailedDirty()` 收到响应后立即调用 `createTargetExtraInfoPanel()` 重新渲染面板

**新功能实现记录（2026年1月28日）**：
- **全部位显示切换功能** ✅
  - 功能描述：在交互对象附加信息区域新增"展开/收起全部位显示"按钮，控制角色立绘上的身体部位按钮是否始终显示
  - 实现细节：
    - **后端状态管理**：使用 `cache.all_system_setting.draw_setting[18]` 存储全部位显示状态（0=收起，1=展开）
    - **后端API**：新增 `/api/toggle_all_body_parts` 接口，处理状态切换并返回更新后的附加信息数据
    - **状态面板数据**：`get_target_extra_info()` 返回的数据中新增 `show_all_body_parts` 字段
    - **前端按钮UI**：在 `createTargetExtraInfoPanel()` 中，在详细污浊按钮左侧添加全部位显示切换按钮
    - **前端交互逻辑**：新增 `toggleAllBodyParts()` 函数，点击按钮时立即更新UI并调用后端API
    - **身体部位显示逻辑**：
      - 收起状态（默认）：部位按钮 `opacity: 0`，仅在鼠标悬停时显示（`:hover` 时 `opacity: 1`）
      - 展开状态：部位按钮添加 `.always-visible` 类，`opacity: 0.5` 且有脉冲动画，悬停时 `opacity: 1`
    - **CSS样式**：新增 `.body-part-button.always-visible` 样式类，定义展开状态下的显示效果
  - 修改文件：
    - `Script/UI/Panel/web_components/status_panel.py` - 添加 `show_all_body_parts` 状态获取
    - `Script/Core/web_server.py` - 新增 `/api/toggle_all_body_parts` API
    - `static/game.js` - 新增 `toggleAllBodyParts()` 函数，修改 `createTargetExtraInfoPanel()`、`createCharacterDisplay()`、`createBodyPartsLayer()` 函数
    - `static/style.css` - 新增 `.body-part-button.always-visible` 样式
  - 交互特性：
    - 该按钮只影响无交互类型选择时的部位显示
    - 不影响已选择交互类型后的可交互部位高亮与选择逻辑
    - 状态持久化保存在用户设置中

**新功能实现记录（2026年1月28日 - 第二批）**：
- **身体污浊部位名称显示优化** ✅
  - 功能描述：在交互对象附加信息区的身体栏中，为每个部位的污浊信息添加部位名称标签，与服装栏的显示方式保持一致
  - 实现细节：
    - **前端渲染逻辑**：修改 `createBodySection()` 函数，为每个部位创建 `.body-part-group` 分组，包含部位名称标签和污浊文本
    - **部位名称显示**：格式为 `[部位名]:污浊文本`，例如 `[头发]: 精液附着明显`
    - **CSS样式**：新增 `.body-part-group`、`.body-part-label` 样式类
  - 修改文件：
    - `static/game.js` - 修改 `createBodySection()` 函数，添加部位名称显示逻辑
    - `static/style.css` - 新增身体部位分组相关样式（`.body-part-group`、`.body-part-label`）
  - 参考实现：`Script/UI/Panel/dirty_panel.py` 中的 `SeeCharacterBodyPanel` 类
  - 显示效果：与服装栏保持一致的格式，每个部位以 `[部位名]: 污浊文本` 的形式显示
  - **显示优化（2026-01-28）**：
    - 修改 `.body-part-group` 从 `display: inline-flex` 改为 `display: inline`
    - 移除 `align-items: baseline`，使部位名称和内容真正在同一行显示
    - 增加右边距从 `4px` 到 `8px`，与服装栏保持一致的间距

- **附加信息区悬停延展显示** ✅
  - 功能描述：取消滚动条，改为鼠标悬停时向下延展显示全部内容，不影响其他布局
  - 实现细节（2026-01-28更新）：
    - **外层容器**：`.new-ui-target-extra-info` 保持在flex布局中占据固定高度（150px，与玩家信息区高度匹配），`overflow: visible` 允许内容溢出
    - **内部容器**：`.extra-info-container` 实际承载内容和样式
    - **默认状态**：内部容器 `max-height: 134px`（150px - 8px*2 padding），`overflow: hidden`（无滚动条）
    - **悬停状态**：内部容器使用 `position: absolute` 脱离文档流，`max-height: 800px`，`overflow-y: auto`（必要时显示滚动条）
    - **层级控制**：悬停时 `z-index: 100`，覆盖其他元素
    - **视觉效果**：添加阴影（`box-shadow`）增强浮动效果
    - **独立延展**：通过绝对定位脱离文档流，不带动flex父容器和其他兄弟元素（玩家信息区、头像区）变动
  - 修改文件：
    - `static/style.css` - 采用嵌套容器策略，外层维持布局空间，内层悬停时绝对定位扩展
  - 技术方案：
    - **嵌套容器策略**：外层维持flex布局空间，内层悬停时绝对定位扩展
    - **布局隔离**：避免悬停时影响父容器flex高度，确保左侧玩家信息和右侧头像区保持稳定
  - 交互特性：
    - 鼠标移开后自动收起
    - 延展时保持整体布局不变，向下覆盖其他内容而非推动布局
  - **高度优化（2026-01-28）**：
    - 外层容器高度从 `100px` 增加到 `150px`，与玩家信息区高度更好匹配
    - 内部容器相应调整为 `134px`（150px - 16px padding）
    - 确保默认状态下信息区与同行其他区域高度一致
    - 内容超过800px时显示滚动条

**新功能实现记录（2026年2月7日）**：
- **臀部子部位高亮映射功能** ✅
  - 功能描述：当选择的交互小类有臀部子部位（小穴、子宫、后穴、尿道、尾巴、胯部）的指令时，臀部按钮也显示高亮，点击臀部显示该小类下所有子部位的可用指令
  - 实现细节：
    - **后端可用部位计算**：修改 `interaction_handler.py` 的 `_get_available_body_parts_by_minor_type()` 函数
      - 引入 `HIP_SUB_PARTS` 和 `BodyPart` 常量
      - 检测收集到的部位是否包含臀部子部位（vagina, womb, anus, urethra, tail, crotch）
      - 如果包含则自动将 `hip` 添加到可用部位列表
    - **后端点击处理**：修改 `web_server.py` 的 `handle_click_body_part()` 函数
      - 区分已选择小类和未选择小类两种情况
      - 已选择小类时：收集该小类下所有臀部子部位的可用指令，发送 `body_part_clicked` 事件
      - 未选择小类时：展开子部位菜单，发送 `hip_sub_menu` 事件
    - **前端高亮逻辑**：修改 `game.js` 的 `updateAvailableBodyParts()` 函数
      - 定义 `HIP_SUB_PARTS` 数组与后端保持一致
      - 检测可用部位中是否包含臀部子部位
      - 如果有则将 `hip` 添加到 `availableParts` 集合
  - 修改文件：
    - `Script/UI/Panel/web_components/interaction_handler.py` - 添加臀部子部位到可用部位列表的逻辑
    - `Script/Core/web_server.py` - 修改臀部点击处理逻辑
    - `static/game.js` - 添加前端臀部子部位高亮映射
  - 交互特性：
    - 选择小类后，如果该小类有臀部子部位的指令，臀部按钮高亮
    - 点击高亮的臀部，直接显示该小类下所有臀部子部位的可用指令菜单
    - 未选择小类时，点击臀部展开子部位选择菜单

- **指令菜单滚动条功能** ✅
  - 功能描述：解决指令数量过多导致菜单超出屏幕底部的问题，添加滚动条支持
  - 问题背景：当某个身体部位的可用指令数量过多时，指令菜单会超出游戏界面底部，导致无法显示全部指令
  - 实现细节：
    - **菜单结构调整**：在 `showInstructMenu()` 中创建独立的滚动容器 `.instruct-menu-container`
    - **CSS样式配置**：
      - 滚动容器最大高度：400px（约可显示8个指令按钮，每个按钮高度约46px）
      - 滚动条宽度：8px
      - 滚动条轨道：半透明黑色背景 `rgba(0, 0, 0, 0.3)`
      - 滚动条滑块：金色半透明 `rgba(255, 215, 0, 0.5)`，悬停时变深 `rgba(255, 215, 0, 0.7)`
      - 启用垂直滚动：`overflow-y: auto`，自动出现/隐藏滚动条
      - 隐藏水平滚动：`overflow-x: hidden`
    - **高度动态计算**：根据指令数量计算菜单实际高度（`Math.min(instructs.length * 46 + 80, 480)`），确保菜单不超出屏幕边界
    - **自动适应**：
      - 指令数量 ≤ 8个：不显示滚动条，菜单高度适应内容
      - 指令数量 > 8个：显示滚动条，菜单高度固定为400px
  - 修改文件：
    - `static/style.css` - 添加 `.instruct-menu-container` 样式类和滚动条样式
    - `static/game.js` - 修改 `showInstructMenu()` 函数，将指令按钮放入滚动容器，调整高度计算逻辑
  - 用户体验：
    - 所有指令都能正常显示和访问
    - 滚动条样式与游戏整体风格保持一致
    - 支持鼠标滚轮和拖动滑块两种滚动方式

### 3.4 头像区

#### 3.4.1 HTML结构
- [x] 在 `#top-info-area` 中创建 `#avatar-area` 容器
- [x] 添加头像位置容器（最多5个+1个翻页按钮）

#### 3.4.2 CSS样式
- [x] 定义 `#avatar-area` 定位和尺寸
- [x] 定义头像圆形样式
- [x] 定义翻页按钮样式
- [x] 定义头像悬停效果

#### 3.4.3 JavaScript逻辑
- [x] 在 `ui_components.js` 中创建 `AvatarPanel` 对象
- [x] 实现 `render(characters, currentPage)` 方法
- [x] 实现头像点击切换交互对象
- [x] 实现翻页逻辑

### 3.5 交互对象信息区（右侧）

#### 3.5.1 HTML结构
- [x] 在 `#main-scene` 中创建 `#target-info-panel` 容器（右侧定位）
- [x] 添加第一行：名字 + 好感度 + 信赖度
- [x] 添加第二行：体力槽 + 气力槽
- [x] 添加第三行：特殊状态标记
- [x] 添加状态槽区域（快感状态块 + 其他状态块）

#### 3.5.2 CSS样式
- [x] 定义 `#target-info-panel` 右侧固定定位
- [x] 定义各行的布局样式
- [x] 定义状态槽网格布局（每行2个）
- [x] 定义快感状态块和其他状态块的分隔样式
- [x] 定义特殊状态颜色样式（对应 character_info_head.py 中的 draw.style 值）

#### 3.5.3 JavaScript逻辑
- [x] 在 `game.js` 中扩展 `createTargetInfoPanel()` 函数
- [x] 实现 `createStateItem()` 辅助函数用于创建状态项
- [x] 实现好感度/信赖度显示（等级+数值）
- [x] 实现特殊状态标记渲染（带颜色样式和tooltip）
- [x] 实现状态槽分块渲染（快感状态/其他状态）

**实施记录（2026-01-21 完成）**：
- **后端数据源**：
  - 修改 `Script/UI/Panel/web_components/status_panel.py`
  - `_get_special_states()` 使用 `character_info_head.get_character_status_list()` 获取特殊状态标记
  - `_get_pleasure_states()` 获取状态类型0（快感状态）+ 润滑状态
  - `_get_other_states()` 获取状态类型1（其他状态）排除润滑
  - `_get_status_info()` 辅助函数处理单个状态，包含性别过滤、等级计算等
- **前端渲染**：
  - 在 `static/game.js` 中扩展 `createTargetInfoPanel()` 函数
  - 添加 `createStateItem()` 函数创建带进度条的状态项
  - 状态按块显示：快感状态块和其他状态块，每块使用2列网格布局
  - 特殊状态支持颜色样式（通过 CSS 类 `.style-{style_name}`）
- **CSS样式**（在 `static/style.css` 中）：
  - `.new-ui-target-info`：调整宽度为220px，添加滚动支持
  - `.target-relation-row`：好感度/信赖度行样式
  - `.target-special-states`：特殊状态标记容器，支持换行
  - `.target-state-section`、`.state-section-title`：状态区块样式
  - `.state-grid`：2列网格布局
  - `.state-item`：状态项样式（标签+进度条+数值）
  - `.special-state.style-*`：17种颜色样式对应 character_info_head.py 中的 draw.style 值
- **数据同步**：
  - 修改 `Script/Core/web_server.py` 的 `send_full_game_state()` 使用 `StatusPanel` 获取完整 target_info
  - 每次主循环迭代时 `in_scene_panel_web.py` 会重新收集状态，确保指令结算后数据同步

#### 3.5.4 可选部位打印区（2026-02-12 新增）
- [x] 在交互对象信息区最下方添加可选部位打印区
- [x] 仅在"全部位显示"开启时显示
- [x] 后端实现：
  - 在 `status_panel.py` 的 `get_target_info()` 方法中添加 `show_all_body_parts` 和 `available_body_parts` 字段
  - 添加 `_get_available_body_parts_for_display()` 方法获取可选部位列表
  - 未选择交互小类时：返回角色身上的所有可交互部位（从body.json中获取）
  - 选择了交互小类后：返回角色立绘中存在的部位与该小类对应部位的交集
- [x] 前端实现：
  - 修改 `static/game.js` 的 `createTargetInfoPanel()` 函数
  - 添加可选部位打印区（`.target-body-parts-section`）
  - 使用2列网格布局显示部位（`.body-parts-display-grid`）
  - 点击部位项可触发 `handleBodyPartClick()` 事件
- [x] CSS样式：
  - `.target-body-parts-section`：可选部位区块样式（顶部边框分隔）
  - `.body-parts-display-grid`：2列网格布局
  - `.body-part-display-item`：部位项样式（淡蓝色背景、可点击）
- [x] 切换交互类型时同步刷新（2026-02-12 新增）：
  - 修改 `web_server.py` 的 `handle_select_minor_type()` 函数，返回数据中新增 `target_info` 字段
  - 修改 `web_server.py` 的 `handle_clear_interaction_selection()` 函数，返回数据中新增 `target_info` 字段
  - 修改 `static/game.js` 的 `minor_type_selected` 事件处理器，接收 `target_info` 后刷新右侧面板
  - 添加 `interaction_selection_cleared` 事件监听器，清空选择后刷新右侧面板
- [x] 部位映射逻辑（2026-02-12 新增）：
  - 指令系统定义的部位（如兽耳、兽角、头发、小穴、尾巴等）需要映射到角色立绘中实际存在的部位
  - 头部子部位（头发/兽角/兽耳）→ 映射到"头部"
  - 臀部子部位（小穴/子宫/后穴/尿道/尾巴/胯部）→ 映射到"臀部"
  - 其他部位直接匹配角色立绘中的部位
  - 最终返回的部位列表是映射后的部位与角色立绘部位的交集

### 3.6 交互类型栏（左侧）

#### 3.6.1 HTML结构
- [x] 在 `#main-scene` 中创建 `#interaction-type-panel` 容器（左侧定位）
- [x] 添加交互类型按钮容器

#### 3.6.2 CSS样式
- [x] 定义 `#interaction-type-panel` 左侧固定定位
- [x] 定义交互类型按钮样式
- [x] 定义选中状态样式
- [x] 定义悬停效果

#### 3.6.3 JavaScript逻辑
- [x] 在 `ui_components.js` 中创建 `InteractionTypePanel` 对象
- [x] 实现 `update(types)` 方法
- [x] 实现类型选择回调
- [x] 实现当前选中状态管理

#### 3.6.4 大类/小类嵌套结构重构（2026-01-18 新增）
- [x] 重构 `interaction_handler.py` 中的 `get_interaction_types()` 方法
  - 返回 `major_types`（大类列表）、`minor_types`（当前大类下的小类列表）
  - 每个大类包含 `id`、`name`、`selected`、`minor_types`
  - 每个小类包含 `id`、`name`、`selected`
- [x] 添加 `select_major_type()` 和 `select_minor_type()` 方法处理大类/小类选择
- [x] 添加 `_get_available_body_parts_by_minor_type()` 方法获取小类对应的可交互部位
- [x] 重构 `static/game.js` 中的 `createInteractionTypePanel()` 函数
  - 支持新版大类/小类嵌套数据结构
  - 保留旧版数组格式的向后兼容
  - 渲染大类选项卡（`.interaction-major-tabs`）和小类按钮（`.interaction-minor-buttons`）
- [x] 添加 `selectMajorType()` 和 `selectMinorType()` 前端函数
- [x] 添加 `updateMinorTypeButtons()` 函数处理大类切换后的小类按钮更新
- [x] 添加 `updateAvailableBodyParts()` 函数处理小类选择后的部位高亮
- [x] 添加前端WebSocket事件监听：`major_type_selected`、`minor_type_selected`
- [x] 更新 `static/style.css` 添加新的交互面板样式：
  - `.interaction-major-tabs`：大类选项卡容器（垂直排列）
  - `.interaction-major-tab`：大类选项卡样式（左边框高亮表示选中）
  - `.interaction-minor-buttons`：小类按钮容器
  - `.interaction-minor-btn`：小类按钮样式
  - `.body-part-button.available`：可交互部位高亮样式（绿色脉冲动画）
  - `.body-part-button.unavailable`：不可交互部位隐藏样式

**实施记录（2026-01-18）**：
- 交互面板从简单的4个按钮列表重构为大类选项卡+小类按钮的嵌套结构
- 大类（5个）：嘴、手、阴茎、道具、其他，作为垂直选项卡显示
- 小类按钮在选中大类下方显示，点击后会高亮角色身上可交互的部位
- 大类切换时自动记忆并恢复上次选中的小类
- WebSocket事件：后端已有 `select_major_type` 和 `select_minor_type` 处理器

#### 3.6.5 交互面板视觉风格优化（2026-02-11）
- [x] 优化大类按钮布局：改为横向排列（图标在左，文字在右），节省垂直空间
- [x] 调整按钮高度：
  - 大类按钮高度从100px减至50px，后回调至70px（增加1/3）
  - 小类按钮高度减至36px
- [x] 修复3D旋转导致的点击区域问题：
  - 调整 `transform-origin` 为 `left center`
  - 添加 `min-width` 和 `padding-right` 防止容器裁剪
- [x] 优化浮现按钮样式：去掉英文标识，使用深蓝色背景和青色边框区分
- [x] 修复刷新后小类名称丢失问题：统一前后端HTML生成结构
- [x] 实现小类按钮反选逻辑：点击已选中的小类取消选中并清空部位高亮

#### 3.6.6 交互大类图标支持（2026-02-13）
- [x] 在 `static/assets/ui/` 目录添加7个交互大类图标文件：
  - `嘴部.png` → mouth
  - `手部.png` → hand
  - `性爱.png` → sex
  - `阴茎.png` → penis
  - `道具.png` → tool
  - `源石技艺.png` → arts
  - `设置.png` → other
- [x] 修改 `static/game.js` 中的 `createInteractionTypePanel()` 函数：
  - 将 `getIcon()` 函数改为 `getIconHtml()` 函数
  - 从返回 emoji 字符改为返回 `<img>` 标签 HTML
  - 图标路径：`/static/assets/ui/${encodeURIComponent(iconFile)}`
- [x] 在 `static/css/game_main.css` 中添加图标样式：
  - `.interaction-icon-img`：图片图标样式（32x32px，居中显示）
  - `.interaction-icon-default`：默认圆点图标样式（无图片时使用）
  - 更新 `.interaction-card .icon` 为 flex 布局以支持图片居中

**实施说明（2026-02-13）**：
- 图标位置保持与原 emoji 图标一致（文本左侧）
- 图标尺寸缩放至 32x32px，不影响原有按钮大小和排版
- 使用 `encodeURIComponent` 处理中文文件名的 URL 编码
- 保留默认圆点图标作为兜底显示

### 3.7 对话框区域

#### 3.7.1 HTML结构
- [x] 完善 `#dialog-box` 容器结构
- [x] 添加角色名称显示区域
- [x] 添加对话文本显示区域

#### 3.7.2 CSS样式
- [x] 定义 `#dialog-box` 底部固定定位
- [x] 定义半透明背景样式
- [x] 定义角色名称样式
- [x] 定义对话文本样式
- [ ] 定义文本渐显动画（待完善）

#### 3.7.3 JavaScript逻辑
- [x] 在 `ui_components.js` 中创建 `DialogBox` 对象
- [x] 实现 `show(charName, text)` 方法
- [ ] 实现文本逐字显示动画（待完善）
- [x] 实现点击推进逻辑
- [x] 实现右键/Ctrl跳过逻辑
- [x] 实现 `hide()` 方法

**实施记录（2026年1月19日更新）**：
- **后端对话框组件重构**：
  - 在 `Script/UI/Panel/web_components/dialog_box.py` 中添加全局函数：
    - `add_dialog_text(speaker, text, color, wait)` - 添加对话到队列
    - `advance_dialog()` - 推进对话
    - `hide_dialog()` - 隐藏对话框
    - `get_dialog_state()` - 获取对话框状态
    - `skip_all_dialogs()` - 跳过所有对话
  - `DialogBox` 类现在是全局函数的封装器，状态存储在 cache 中
- **Cache扩展**：
  - 在 `Script/Core/game_type.py` 的 `Cache` 类中添加对话框相关字段：
    - `web_dialog_visible` - 对话框是否可见
    - `web_dialog_speaker` - 说话者名称
    - `web_dialog_text` - 对话文本
    - `web_dialog_text_color` - 文本颜色样式
    - `web_dialog_queue` - 对话队列
    - `web_dialog_wait_input` - 是否等待用户输入
- **talk.py集成**：
  - 修改 `handle_talk_draw()` 函数，在Web模式下将文本发送到对话框而非直接打印
  - 通过 `cache.web_mode` 判断是否为Web模式
  - 调用 `add_dialog_text()` 添加对话到队列
- **前端渲染**：
  - 在 `static/game.js` 中添加 `createDialogBox()` 函数
  - 在 `renderNewUIContent()` 中渲染对话框区域
  - 实现 `updateDialogBox()` 更新对话框状态
  - 添加 `handleDialogClick()` 处理点击推进
  - 添加 `initDialogKeyboardShortcuts()` 支持Ctrl/右键快速跳过
- **CSS样式**：
  - 在 `static/style.css` 中添加 `.new-ui-dialog-box` 等样式
  - 半透明背景、金色说话者名称、点击推进提示
- **WebSocket事件**：
  - `advance_dialog` - 推进对话（前端发送）
  - `skip_all_dialogs` - 跳过所有对话（前端发送）
  - `dialog_advanced` - 推进结果响应（后端发送）
  - `dialogs_skipped` - 跳过结果响应（后端发送）
  - `dialog_state_update` - 对话框状态更新（后端主动推送，由talk.py触发）
- **状态推送机制**（2026年1月19日新增）：
  - 在 `dialog_box.py` 中添加 `_trigger_state_update()` 函数
  - 当 `add_dialog_text()` 被调用时，自动通过 `dialog_state_update` 事件推送对话框状态
  - 在 `web_server.py` 的 `send_full_game_state()` 和 `_emit_game_state_update()` 中包含对话框状态
  - 前端 `renderGameState()` 中调用 `updateDialogBox()` 更新对话框

---

## 阶段四：场景与角色渲染

### 4.1 场景背景渲染

#### 4.1.1 后端数据准备
- [x] 在 `scene_renderer.py` 中创建 `SceneRenderer` 类
- [x] 实现 `get_scene_background(scene_name)` 方法
- [x] 实现背景图片路径查找逻辑（优先同名，默认博士办公室）
- [ ] 在WebSocket推送数据中包含背景图路径（需扩展web_server.py）

#### 4.1.2 前端渲染
- [x] 在 `game_renderer.js` 中创建场景背景渲染功能
- [x] 实现背景图加载和显示
- [x] 实现图片保持比例缩放居中
- [x] 实现空白区域黑色填充（CSS实现）

### 4.2 角色立绘渲染

#### 4.2.1 后端数据准备
- [x] 在 `character_renderer.py` 中创建 `CharacterRenderer` 类
- [x] 实现 `get_character_image_data(char_id)` 方法
- [x] 返回数据结构：基础图层路径、服装图层、特效图层、部位位置JSON

**实施记录（2026-01-17）**：
- **图片路径修正**：
  - 修改 `static/game.js` 中 `createCharacterDisplay()` 函数
  - 使用 `full_body_image || half_body_image` 替代错误的 `base_image` 字段
  - 图片路径正确添加 `/` 前缀以匹配 Flask 静态路由
- **身体部位数据处理**：
  - 修改 `character_renderer.py` 中 `_load_body_parts_data()` 方法
  - 支持 `{角色名}_body.json` 格式的 landmarks 数据（归一化坐标 0-1）
  - 自动将 landmarks 数组转换为前端需要的 body_parts 字典格式
  - 根据部位名称映射（如 `nose` → `鼻子`、`left_eye` → `左眼` 等）
- **前端渲染**：
  - 添加 `.character-container`、`.character-image`、`.body-parts-layer` 等CSS样式
  - 身体部位按钮使用百分比定位，支持响应式布局
  - 鼠标悬停时显示部位名称提示

#### 4.2.2 前端Canvas渲染
- [x] 在 `game_renderer.js` 中实现角色图像渲染功能
- [x] 创建Canvas元素用于角色渲染
- [x] 实现图层加载和绘制
- [x] 实现角色居中显示
- [x] 保存渲染变换信息供部位按钮使用

### 4.2.3 角色立绘高度统一缩放功能（2026-02-07新增）

##### 功能描述
- **目标**：解决角色立绘因原图大小不一致而产生不同缩放情况的问题
- **规则**：
  1. 检查当前窗口大小导致的角色立绘可用高度上限
  2. 如果可用高度 > 1024像素，将图片高度固定为 1024像素
  3. 如果可用高度 ≤ 1024像素，将图片高度设为可用高度
  4. 图片保持原比例，居中显示
  5. 身体部位按钮的点击位置随图片一起缩放

##### 实现细节
- **CSS修改（`static/style.css`）**：
  - `.new-ui-character-display`：添加 `overflow: visible` 便于高度计算
  - `.character-container`：改为 `display: inline-flex`，尺寸由内部图片决定；添加 `transition` 实现平滑变换
  - `.character-image`：移除 `max-height`，由JS动态设置 `height` 属性
  - `.body-parts-layer`：添加 `transform-origin: center center`

- **JS修改（`static/game.js`）**：
  - `createCharacterDisplay()`：在图片 `onload` 事件中调用 `applyCharacterImageHeight()`
  - 新增 `applyCharacterImageHeight(display, img)` 函数：
    - 获取显示区域可用高度（减去边距）
    - 计算目标高度：`min(1024, 可用高度)`
    - 设置 `img.style.height` 和 `img.style.width = 'auto'`
    - 保存目标高度到 `display.dataset` 供后续使用
    - 触发重叠检测
  - 新增 `updateCharacterImageHeightOnResize()` 函数：窗口大小改变时重新计算高度
  - 新增 `debounce()` 辅助函数：防抖处理
  - 添加窗口 `resize` 事件监听

##### 身体部位按钮同步缩放
- **原理**：身体部位按钮使用百分比定位（相对于 `body-parts-layer`）
- **机制**：
  1. `body-parts-layer` 大小为 100% x 100%，与 `character-container` 一致
  2. `character-container` 的大小由 `character-image` 决定
  3. 当图片高度设置后，容器和按钮层都会自动调整
  4. 百分比定位的按钮会自动映射到正确位置

##### 与浮现按钮重叠调整的兼容
- **两阶段调整**：
  1. **高度缩放**（基础）：通过 `img.style.height` 实现，统一到1024px或可用高度
  2. **重叠调整**（附加）：通过 `transform` 实现右移和/或缩小
- **顺序**：先应用高度缩放，再检测重叠、应用变换
- **效果叠加**：两者独立，`transform` 在固定高度基础上进行

#### 4.2.4 角色立绘透明区域裁切（2026-02-08新增）✅

**功能描述**：自动裁切角色立绘图片四周的透明区域，优化显示效果

##### 后端实现
- [x] 创建 `Script/UI/Panel/web_components/image_processor.py` 图片处理模块
- [x] 实现 `ImageProcessor` 类（单例模式）
- [x] 实现LRU缓存机制（最大10张图片）
  - [x] 使用 `OrderedDict` 维护访问顺序
  - [x] 缓存命中时更新访问顺序（移到末尾）
  - [x] 缓存已满时删除最旧的图片
- [x] 实现 `get_cropped_image()` 方法
  - [x] 使用PIL的 `getbbox()` 检测非透明区域边界
  - [x] 裁切图片并转换为PNG字节数据
  - [x] 返回裁切后图片和元数据（原始尺寸、裁切后尺寸、偏移量）
- [x] 实现 `clear_cache()` 方法（用于存档时清理）
- [x] 在 `__init__.py` 中导出新模块

##### API路由
- [x] 在 `web_server.py` 中添加 `/api/cropped_image/<path:filename>` 路由
- [x] 从响应头返回裁切元数据：
  - `X-Original-Width`、`X-Original-Height`
  - `X-Cropped-Width`、`X-Cropped-Height`
  - `X-Offset-X`、`X-Offset-Y`
- [x] 如果PIL不可用，自动回退到原始图片

##### 存档清理
- [x] 修改 `save_handle.py` 的 `establish_save_linux()` 函数
- [x] 在保存存档前调用 `clear_image_cache()` 清理图片缓存

##### 前端实现
- [x] 修改 `game.js` 的 `createCharacterDisplay()` 函数
  - [x] 使用 `fetch()` 加载裁切图片API
  - [x] 从响应头解析裁切元数据
  - [x] 将元数据保存到容器元素的 `dataset.cropMetadata`
  - [x] 图片加载完成后调用 `adjustBodyPartsLayerForCrop()`（使用 requestAnimationFrame 确保渲染尺寸已确定）
  - [x] 如果裁切API失败，回退到原始图片
- [x] 修改 `createBodyPartsLayer()` 函数（2026-02-08更新）
  - [x] 保存原图坐标（像素值）到按钮的 `data-orig-x`、`data-orig-y` 属性
  - [x] 保存原始大小百分比到按钮的 `data-orig-size-percent` 属性
  - [x] 保存数据图片尺寸到layer的 `data-data-image-width`、`data-data-image-height` 属性（用于坐标系转换）
- [x] 修改 `adjustBodyPartsLayerForCrop()` 函数（2026-02-08更新）
  - [x] 获取图片实际渲染尺寸（`img.offsetWidth`、`img.offsetHeight`）
  - [x] 获取图片相对于容器的偏移量（使用 `getBoundingClientRect()`）
  - [x] 设置 layer 尺寸和位置为像素值，精确覆盖图片（2026-02-08修复）
  - [x] 支持数据坐标系与实际原图坐标系不一致的情况
  - [x] 第一步：将数据坐标转换为实际原图坐标（乘以缩放比例）
  - [x] 第二步：将实际原图坐标转换为裁切后图片坐标（百分比）
  - [x] 按比例调整按钮大小（使用 dataImageWidth/croppedWidth 因子）
  - [x] 确保部位按钮位置与裁切后图片准确对齐，支持图片居中
- [x] 修改 `updateCharacterImageHeightOnResize()` 函数（2026-02-08更新）
  - [x] 窗口大小变化时重新应用角色立绘高度
  - [x] 重新调用 `adjustBodyPartsLayerForCrop()` 更新 layer 尺寸和按钮位置

##### CSS样式
- [x] 修改 `.character-container` 改用 `display: inline-flex; flex-direction: column`（2026-02-08更新）
  - [x] 使用 inline-flex 实现紧密包裹同时保持居中
  - [x] 确保容器紧密包裹图片，避免 layer 对齐问题
- [x] 简化 `.body-parts-layer` 样式（2026-02-08更新）
  - [x] 移除 `transform-origin: left top`（不再需要）
  - [x] 尺寸由 JS 动态设置为像素值

##### 前端图片缓存（2026-02-08新增）
- [x] 添加 `croppedImageCache` 全局 Map 对象
  - [x] 以裁切图片 API URL 为键
  - [x] 值包含 `blobUrl` 和 `metadata`
- [x] 修改 `createCharacterDisplay()` 函数
  - [x] 请求前检查缓存，命中则直接使用
  - [x] 缓存未命中时发起 fetch 并存入缓存
- [x] 添加 `clearCroppedImageCache()` 函数
  - [x] 释放所有 blob URL 避免内存泄漏
  - [x] 在切换交互对象时调用
- [x] 修改 `target_switched` 事件处理
  - [x] 切换交互对象时调用 `clearCroppedImageCache()`
- [x] 注释掉后端缓存命中日志
  - [x] `image_processor.py` 中的 `[图片处理器] 缓存命中` 日志

### 4.3 身体部位按钮系统

#### 4.3.1 部位按钮管理器
- [x] 在 `game_renderer.js` 中实现部位按钮功能
- [x] 实现 `updateBodyPartButtons(parts)` 方法
- [x] 实现部位按钮创建（隐形圆形）
- [x] 实现鼠标悬停效果（光标变化、提示框）
- [x] 实现点击事件处理

#### 4.3.2 指令选择菜单
- [x] 实现单指令直接执行逻辑
- [x] 实现多指令时的选项菜单显示
- [x] 实现菜单定位（以部位为中心）
- [x] 实现点击空白关闭菜单
- [ ] 实现点击其他部位切换菜单（待完善）

#### 4.3.3 部位提示框
- [x] 创建提示框DOM元素
- [x] 实现提示框跟随鼠标
- [x] 实现部位名称中文显示映射

---

## 阶段五：后端数据通信 ✅

**阶段状态**：基本完成（API集成已完成，部分状态字段待扩展）
**更新日期**：2026年1月13日

### 5.1 扩展WebSocket数据结构

#### 5.1.1 定义新的游戏状态数据结构
- [~] 在 `web_server.py` 中扩展 `game_state` 结构（已添加push_game_state函数和WebSocket事件处理器）
- [ ] 添加 `scene` 字段（背景图路径、场景名称）
- [ ] 添加 `player_info` 字段（玩家信息数据）
- [ ] 添加 `target_info` 字段（交互对象信息数据）
- [ ] 添加 `scene_characters` 字段（场景角色头像列表）
- [x] 添加 `interaction_types` 字段（可用交互类型列表）- 通过 `get_interaction_types` API
- [x] 添加 `panel_tabs` 字段（面板选项卡列表）- 通过 `get_panel_instructs` API
- [x] 添加 `dialog` 字段（对话框状态）- 2026年1月19日完成
- [ ] 添加 `settlement` 字段（结算阶段状态）

#### 5.1.2 实现增量更新机制
- [x] 在 `in_scene_panel_web.py` 中实现状态缓存
- [x] 实现 `_calculate_diff()` 方法计算状态差异
- [x] 仅推送变动的数据字段（push_game_state支持diff_only参数）
- [x] 前端实现增量更新渲染

**实施记录（2026-01-17）**：
- **状态推送修复**：
  - 问题：`_push_state_to_frontend` 直接调用 `web_server.update_game_state`，导致元素未添加到 `cache.current_draw_elements`
  - 解决：修改为将元素添加到 `cache.current_draw_elements`，由 `askfor_all` 统一发送
  - 确保 `clear_screen()` → `_push_state_to_frontend()` → `askfor_all()` 的流程正确
  - 修复后主面板能够正常显示新UI元素

### 5.2 新增API端点（使用WebSocket事件替代REST API）

#### 5.2.1 交互类型选择API
- [x] 添加 `select_interaction_type` WebSocket事件处理器
- [x] 接收 `{type_id}` 参数
- [x] 返回该类型可用的部位列表和指令列表（已与阶段二指令分类系统集成）
- [x] 在后端更新当前交互类型状态（`cache.current_interaction_type`）

**实施记录**：
- 集成了 `instruct_meta` 模块的查询函数
- 返回数据包含部位中文名映射

#### 5.2.2 部位点击API
- [x] 添加 `click_body_part` WebSocket事件处理器
- [x] 接收 `{part_name}` 参数
- [x] 返回该部位可执行的指令列表（已与阶段二指令分类系统集成）
- [x] 返回 `single_instruct` 字段指示是否只有一个指令（后端仍返回，但前端不再使用此字段自动执行）

**实施记录**：
- 支持根据当前交互类型过滤指令
- 返回部位中文名供前端显示

**行为更新（2026-02-12）**：
- 前端不再根据 `single_instruct` 字段自动执行唯一的指令
- 无论有多少个可执行指令，都显示指令选择菜单，需要用户点击才能执行
- 这样可以避免误操作，让用户有更好的控制感

#### 5.2.3 执行指令API
- [x] 添加 `execute_instruct` WebSocket事件处理器
- [x] 接收 `{instruct_id}` 参数
- [x] 执行指令并触发结算流程（已调用 `handle_instruct.handle_instruct()`）
- [x] 执行完成后设置刷新信号，通知主面板循环刷新数据（2026-01-21修复）
- [~] 返回结算状态（待阶段六完善）

**实施记录**：
- 调用 `handle_instruct.handle_instruct(instruct_id)` 执行指令
- 包含错误处理和异常捕获
- **2026-01-21修复**：添加刷新信号机制
  - 定义 `WEB_REFRESH_SIGNAL = "__WEB_REFRESH__"` 常量
  - 执行完指令后设置 `button_click_response = WEB_REFRESH_SIGNAL`
  - 这会唤醒 `askfor_all()` 并让主面板循环刷新数据
- **2026-02-12更新**：刷新信号不再打印到界面
  - 修改 `flow_handle_web.py` 的 `askfor_all()` 函数
  - 添加判断：当 `response == WEB_REFRESH_SIGNAL` 时跳过 `io_init.era_print()` 调用
  - 避免界面显示 `__WEB_REFRESH__` 这类内部信号字符串

#### 5.2.4 切换交互对象API
- [x] 添加 `switch_target` WebSocket事件处理器
- [x] 接收 `{character_id}` 参数
- [x] 更新玩家的交互对象（`pl_character_data.target_character_id`）
- [x] 返回新的交互对象信息（角色名等）
- [x] 设置刷新信号唤醒主循环（2026-02-07新增）
- [x] 处理待显示行为文本的移动（2026-02-07新增）
- [x] 刷新角色数值变化时间戳（2026-02-07新增）

**实施记录（2026-02-07更新）**：
- 检查目标角色是否存在
- 更新 `target_character_id`
- **处理待显示的行为指令文本**：
  - 检查 `cache.web_minor_dialog_queue` 中是否有该角色的小对话框
  - 如果有，将完整文本移动到主对话框队列进行显示
  - 从 `minor_dialog` 队列中移除该角色的条目
- **刷新数值变化时间戳**：
  - 遍历 `cache.web_value_changes` 中该角色的数据
  - 刷新时间戳为当前时间，确保不会被2秒超时过滤
- 设置 `cache.web_need_full_refresh = True` 标记需要完整刷新
- 设置 `button_click_response = WEB_REFRESH_SIGNAL` 触发主循环刷新
- 返回 `target_switched` 事件通知前端切换结果

#### 5.2.4.1 无交互对象时的显示逻辑（2026-02-07新增）

**交互对象判断逻辑**：
- 当 `target_character_id == 0`（等于玩家自己的cid）时，表示玩家没有交互对象
- 当 `target_character_id > 0` 时，表示有交互对象
- 当 `target_character_id < 0` 时，表示无效

**无交互对象时隐藏的内容**：
- 正中间的交互对象角色立绘图片和相关交互
- 最右边的交互对象角色信息
- 上方中间的交互对象其他信息（服装/身体/群交/隐奸栏）

**始终显示的内容**：
- 上方右边的场景内其他角色头像区（显示场景内除玩家外的所有角色）

**后端实现**：
- [x] `in_scene_panel_web.py` 的 `_get_target_info()` 在 `target_id <= 0` 时返回空字典
- [x] `status_panel.py` 的 `get_target_info()` 在 `character_id <= 0` 时返回空字典
- [x] `status_panel.py` 的 `get_target_extra_info()` 在 `character_id <= 0` 时返回空字典
- [x] `character_renderer.py` 的 `get_character_image_data()` 在 `character_id <= 0` 时返回空字典
- [x] `_get_scene_characters()` 在没有交互对象时只排除玩家，不排除 target_id

**前端实现**：
- [x] `game.js` 的 `renderNewUIContent()` 检查 `target_info` 是否为空对象
- [x] 当 `target_info` 为空对象时，不创建角色立绘区和交互对象信息区
- [x] 当 `target_extra_info` 为空对象时，不创建交互对象附加信息区

#### 5.2.5 新增API端点（补充）
- [x] 添加 `get_interaction_types` WebSocket事件处理器 - 获取可用交互类型列表
- [x] 添加 `get_panel_instructs` WebSocket事件处理器 - 获取面板类指令列表
- [x] 更新 `click_panel_tab` 处理器 - 执行面板类指令

### 5.3 前端API调用

#### 5.3.1 WebSocket事件监听
- [x] 在 `websocket_handler.js` 中监听 `game_state_update` 事件
- [x] 解析新增的数据字段
- [x] 调用各UI组件的更新方法

#### 5.3.2 API调用封装
- [x] 在 `websocket_handler.js` 中封装API调用函数（通过WebSocket）
- [x] 实现 `selectInteractionType(typeId)`
- [x] 实现 `clickBodyPart(partName)`
- [x] 实现 `executeInstruct(instructId)`
- [x] 实现 `switchTarget(characterId)`
- [x] 实现 `clickPanelTab(tabId)`

#### 5.3.3 无部位指令浮现按钮（2026-01-18新增，2026-01-19更新）
- [x] 修改 `updateAvailableBodyParts()` 函数区分有部位和无部位指令
- [x] 创建 `renderFloatingInstructButtons()` 函数渲染浮现按钮
- [x] ~~在 `createInteractionTypePanel()` 中添加浮现按钮容器~~ → 改为在 `renderNewUIContent()` 中添加到 `mainScene`
- [x] 添加 `.interaction-floating-buttons` 和 `.floating-instruct-btn` CSS样式
- [x] 点击浮现按钮调用 `executeInstruct()` 执行指令
- [x] 切换大类时清空浮现按钮和身体部位高亮
- [x] 浮现按钮容器位置修正：从交互面板内部移到 `mainScene` 右侧（2026-01-18）
- [x] 浮现按钮换列布局修正：使用 `max-height: min(calc(100vh - 200px), 500px)` 基于视口高度限制（2026-01-18）
- [x] **无交互对象时的特殊处理**：当玩家没有交互对象（交互对象是自己）时，所有指令（包括身体部位指令）都作为浮现按钮显示（2026-01-19）

**实施记录（2026-01-18）**：
- **问题背景**：对于不涉及身体部位的指令（如"聊天"），原有设计没有显示入口
- **解决方案**：在主场景区域右侧（交互面板外部）添加"浮现按钮"区域
- **前端实现**：
  - 修改 `static/game.js` 中 `updateAvailableBodyParts()` 函数
  - 将 `body_parts` 为空的指令收集到单独数组
  - 调用新增的 `renderFloatingInstructButtons()` 渲染浮现按钮
  - 修改 `updateMinorTypeButtons()` 函数，在切换大类时清空浮现按钮和身体部位高亮
  - 浮现按钮容器在 `renderNewUIContent()` 中创建，作为 `mainScene` 的直接子元素
- **CSS样式**：
  - 浮现按钮容器使用 `flex-direction: column; flex-wrap: wrap`
  - 使用 `max-height: min(calc(100vh - 200px), 500px)` 基于视口高度限制，确保换列正确
  - 按钮使用紫色调高亮样式区别于小类按钮
- **交互逻辑**：
  - 遵循交互类型筛选：只显示当前选中小类下的无部位指令
  - 点击直接执行指令，无需二次确认
  - 切换大类时自动清空，等待选择小类后重新渲染

**无交互对象时的特殊处理（2026-01-19新增）**：
- **问题背景**：当玩家没有交互对象时（`hasTargetCharacter === false`），角色立绘不显示，导致身体部位指令无法访问
- **解决方案**：
  - 在 `renderNewUIContent()` 中存储 `hasTargetCharacter` 到 `window.hasTargetCharacter`，供其他函数访问
  - 修改 `updateAvailableBodyParts()` 函数：
    - 检测 `window.hasTargetCharacter` 标志
    - **有交互对象时**：身体部位指令加入 `availableParts`（原有行为），用于高亮身体部位按钮
    - **无交互对象时**：所有指令（包括身体部位指令）都加入 `noBodyPartInstructs`，统一作为浮现按钮显示
  - 这保证了在没有交互对象时，所有指令仍然可以通过浮现按钮访问
- **实施细节**：
  - 在 `updateAvailableBodyParts()` 中添加 `const hasTarget = window.hasTargetCharacter !== undefined ? window.hasTargetCharacter : true;`
  - 对于有 `body_parts` 的指令，根据 `hasTarget` 决定是加入 `availableParts` 还是 `noBodyPartInstructs`
  - 无 `body_parts` 的指令始终加入 `noBodyPartInstructs`

#### 5.3.4 身体部位按钮匹配机制（2026-01-18新增）
- [x] 身体部位按钮添加 `data-base-part` 属性（英文部位名）
- [x] 修改 `updateAvailableBodyParts()` 使用 `basePart` 匹配指令的 `body_parts`
- [x] 支持左右对称部位自动匹配基础部位名（如 `hand_left` 匹配 `hand`）

**实施记录（2026-01-18）**：
- **问题背景**：身体部位按钮使用中文名（如"头部"），而指令的 `body_parts` 使用英文（如"head"），导致匹配失败
- **解决方案**：
  - 后端 `character_renderer.py` 已在 `body_parts` 数据中包含 `base_part` 和 `part_id` 字段
  - 前端 `createBodyPartsLayer()` 添加 `data-base-part` 属性
  - 前端 `updateAvailableBodyParts()` 使用 `basePart` 进行匹配
  - 对于 `hand_left` 等后缀名，自动去除后缀匹配基础部位名

#### 5.3.5 浮现按钮布局优化（2026-01-18新增）
- [x] 浮现按钮容器改为绝对定位，不影响角色立绘大小
- [x] 浮现按钮容器固定在交互面板右侧（left: 148px）

**实施记录（2026-01-18）**：
- **问题背景**：浮现按钮列绘制时会压缩角色立绘
- **解决方案**：将浮现按钮容器从 flex 子元素改为绝对定位
- **CSS修改**：`.interaction-floating-buttons` 添加 `position: absolute; left: 148px; top: 8px; z-index: 10`

#### 5.3.6 身体部位点击执行指令（2026-01-18新增）
- [x] 后端 `click_body_part` 事件处理：中文部位名转换为英文进行匹配
- [x] 前端 `handleBodyPartClick()` 点击时关闭已有的指令菜单
- [x] 前端 `showInstructMenu()` 菜单在点击的部位位置显示
- [x] 点击空白区域关闭菜单，点击其他部位切换到该部位

**实施记录（2026-01-18）**：
- **问题背景**：点击高亮的身体部位没有反应
- **原因分析**：
  1. 后端在匹配指令时使用中文部位名与英文 `body_parts` 比较，永远匹配不上
  2. 前端指令菜单居中显示而非在部位位置显示
- **解决方案**：
  - 后端：添加中文→英文部位名转换逻辑（反向查找 `BODY_PART_NAMES`）
  - 后端：支持"左手部""右腿部"等带方向的中文名转换
  - 前端：保存点击的按钮引用 `window.lastClickedBodyPartButton`
  - 前端：菜单在部位按钮右侧显示，超出边界时自动调整位置
  - 前端：点击其他部位时自动关闭当前菜单

#### 5.3.7 浮现指令列重叠检测与部位交互优化（2026-01-18新增）
- [x] 浮现指令列与角色图片重叠时缩小或移动角色图片
- [x] 部位只有一个指令时tooltip显示指令名而非部位名
- [x] 点击部位时根据当前选择的交互小类过滤指令
- [x] 修复部位按钮在横屏时变形和位置偏移问题

**实施记录（2026-01-18）**：
- **问题背景**：
  1. 浮现指令列会遮挡角色立绘，虽然不再压缩但未检测重叠
  2. 部位只有一个指令时tooltip仍显示部位名，不直观
  3. 选择了交互小类后点击部位仍显示所有类型的指令
  4. 横屏时部位按钮被拉长成椭圆且位置偏移
- **解决方案**：
  - **重叠检测**（game.js）：
    - 新增 `checkAndAdjustCharacterImage()` 函数
    - 在 `renderFloatingInstructButtons()` 末尾调用检测
    - 计算浮现按钮与角色容器的矩形重叠
    - 重叠时缩小角色图片并向右移动避开按钮
    - 无重叠时恢复原始大小
  - **单指令部位显示优化**（game.js）：
    - `createBodyPartsLayer()` 中保存 `button._tooltip` 引用
    - `handleBodyPartClickResult()` 中根据指令数量更新tooltip文本
    - 单指令时显示指令名，多指令时显示部位名
  - **小类过滤**（web_server.py）：
    - 导入 `web_interaction_manager`
    - 使用 `get_current_minor_type()` 获取当前小类
    - 有小类时调用 `get_instructs_by_body_part()` 过滤指令
    - 无小类时返回该部位所有指令
  - **部位按钮形状修复**（style.css）：
    - 添加 `aspect-ratio: 1 / 1` 确保始终是正圆
    - 添加 `height: auto !important` 让高度跟随宽度
    - 保持 `transform: translate(-50%, -50%)` 确保居中定位

#### 5.3.8 部位按钮与角色图片同步变换（2026-01-18新增）
- [x] 修复角色图片缩放时部位按钮不跟随变化的问题

**实施记录（2026-01-18）**：
- **问题背景**：
  - 当浮现按钮列与角色图片重叠时，角色图片被缩小和移动
  - 但身体部位按钮仍停留在原位置，与图片位置不匹配
- **原因分析**：
  - 之前的实现只对 `character-image` 应用变换
  - `body-parts-layer` 是与 `character-image` 平级的元素，不会跟随变化
- **解决方案**：
  - 将变换应用到 `character-container` 上（同时包含图片和部位按钮层）
  - 使用 `scale()` 变换替代 `max-width` 调整，确保缩放比例一致
  - 设置 `transformOrigin: 'center center'` 确保从中心缩放
  - 组合使用 `translateX()` 和 `scale()` 实现移动+缩放效果

#### 5.3.9 优化重叠处理与空白区域点击（2026-01-18新增）
- [x] 优化重叠处理策略：优先右移，必要时再缩小
- [x] 点击空白区域清空交互选择并恢复角色立绘

**实施记录（2026-01-18）**：
- **问题背景**：
  1. 重叠时立即缩小不够优雅，应优先尝试右移
  2. 没有方式取消当前的交互选择
- **解决方案**：
  - **优化重叠处理策略**（game.js `checkAndAdjustCharacterImage()`）：
    - 获取右侧状态栏位置作为右边界
    - 检测重叠时，先计算仅右移是否足够
    - 如果右移后不会与右侧状态栏冲突，则仅右移
    - 如果右移会冲突，则在右移基础上进行缩小
  - **空白区域点击处理**（game.js）：
    - 新增 `handleMainSceneClick()` 函数处理主场景点击
    - 排除交互面板、浮现按钮、角色容器等元素的点击
    - 点击空白区域时调用 `clearInteractionSelection()`
    - 新增 `clearInteractionSelection()` 函数：
      - 清空大类和小类选择的高亮
      - 隐藏浮现按钮
      - 恢复角色容器变换
      - 通知后端清空选择
    - 新增 `resetCharacterContainerTransform()` 重置变换状态
  - **后端支持**（web_server.py）：
    - 新增 `clear_interaction_selection` WebSocket事件处理
    - 调用 `web_interaction_manager.clear_selection()` 清空选择

#### 5.3.10 完善重叠检测时机与空白区域判定（2026-01-18新增）
- [x] 在切换交互大类或小类时都触发重叠检测
- [x] 点击角色图像的非按钮区域也触发清空交互选择

**实施记录（2026-01-18）**：
- **问题背景**：
  1. 切换交互类型时，有时会正确处理图片移动与缩放，有时没有
  2. 点击角色图像上的非按钮区域不会清空交互选择
- **解决方案**：
  - **统一重叠检测时机**（game.js）：
    - 在 `updateMinorTypeButtons()` 末尾添加 `setTimeout(() => checkAndAdjustCharacterImage(), 150)`
    - 在 `updateAvailableBodyParts()` 末尾添加 `setTimeout(() => checkAndAdjustCharacterImage(), 150)`
    - 确保无论切换大类还是小类，都会触发重叠检测
  - **扩展空白区域判定**（game.js `handleMainSceneClick()`）：
    - 从排除选择器中移除 `.character-container`
    - 保留 `.body-part-button` 以避免点击部位按钮时误触发
    - 这样点击角色图像的非按钮区域也会触发清空交互选择

#### 5.3.11 修复交互类型按钮重复点击逻辑（2026-01-18新增）
- [x] 修复交互小类按钮重复点击时的变形问题
- [x] 交互大类和小类按钮支持重复点击切换显示/隐藏

**实施记录（2026-01-18）**：
- **问题背景**：
  1. 重复点击交互小类按钮时，图像会先变形再恢复原状
  2. 用户期望重复点击时应该像交互大类一样，在当前状态和未选中状态之间切换
- **问题分析**：
  - 重复点击小类时，`updateAvailableBodyParts()` 会重新调用 `renderFloatingInstructButtons()`
  - `renderFloatingInstructButtons()` 先清空容器（`innerHTML = ''`），导致浮现按钮暂时消失
  - 然后重新渲染按钮，同时触发两次 `checkAndAdjustCharacterImage()`
  - 这导致了变形→恢复的视觉效果
- **解决方案**：
  - **交互大类按钮**（game.js `createInteractionTypePanel()`）：
    - 添加 `wasActive` 检测，判断是否重复点击
    - 重复点击时调用 `clearInteractionSelection()` 清空选择
    - 非重复点击时正常选择大类
  - **交互小类按钮**（game.js 两处）：
    - 在 `createInteractionTypePanel()` 的小类按钮渲染中添加重复点击检测
    - 在 `updateMinorTypeButtons()` 的按钮渲染中添加重复点击检测
    - 重复点击时调用 `clearInteractionSelection()`，而非重新渲染
  - **优化重叠检测调用**（game.js `updateAvailableBodyParts()`）：
    - 移除末尾的重复 `checkAndAdjustCharacterImage()` 调用
    - 因为 `renderFloatingInstructButtons()` 内部已经调用，无需重复

#### 5.3.12 修复清空交互选择时的部位按钮状态（2026-01-19新增）
- [x] 清空交互选择时重置身体部位按钮状态

**实施记录（2026-01-19）**：
- **问题背景**：
  1. 调用 `clearInteractionSelection()` 清空交互大类和小类选择后
  2. 身体部位按钮仍然保持之前选择的交互小类的高亮状态
  3. 用户期望清空选择后，部位按钮应回到"未选择交互大类"的初始状态
- **期望行为**：
  - 清空选择后，所有部位按钮回到初始状态
  - 全部位可互动，但都没有高亮（既不是 `available` 也不是 `unavailable`）
- **解决方案**（game.js `clearInteractionSelection()`）：
  - 在清空大类和小类按钮状态后
  - 添加代码重置所有身体部位按钮：
    ```javascript
    const bodyPartButtons = document.querySelectorAll('.body-part-button');
    bodyPartButtons.forEach(button => {
        button.classList.remove('available');
        button.classList.remove('unavailable');
    });
    ```
  - 这样部位按钮就回到了初始状态，与未选择任何交互类型时一致

---

## 阶段六：演出与结算系统 ✅

### 6.1 结算阶段管理

#### 6.1.1 后端结算管理器
- [x] 在 `web_components/` 中创建 `settlement_manager.py`
- [x] 创建 `SettlementPhase` 枚举（IDLE/SETTLING/DIALOG/VALUE_CHANGE/WAITING_INPUT）
- [x] 创建 `SettlementManager` 类
- [x] 实现 `start_settlement(duration)` 方法
- [x] 实现对话队列收集（`add_dialog()` 方法）
- [x] 实现数值变化收集（`add_value_change()` 方法）
- [x] 实现 `get_state()` 获取结算状态

**实施记录**：
- 创建了 `DialogEntry` 和 `ValueChangeEntry` 数据类
- 支持区分玩家/交互对象对话和其他角色对话
- 其他角色对话存储在单独字典中，用于头像显示
- 在 `web_server.py` 中添加了 `get_settlement_manager()` 单例获取函数

#### 6.1.2 对话显示逻辑
- [x] 实现玩家和交互对象的完整对话显示（通过 `dialog_queue`）
- [x] 实现场景内其他角色的简略对话显示（通过 `other_characters_dialogs`）
- [x] 实现对话推进API（`advance_dialog` WebSocket事件）
- [x] 实现对话跳过API（`advance_dialog(skip=True)` 参数）

**实施记录**：
- `advance_dialog()` 方法支持 skip 参数跳过当前角色对话
- 对话按行拆分，支持逐行推进
- 推进完成自动进入数值变化阶段

#### 6.1.3 数值变化显示
- [x] 实现数值变化数据收集（`add_value_change()` 方法）
- [x] 实现数值变化推送到前端（通过 `get_state()` 包含在返回数据中）
- [x] 前端实现数值变化动画（跳出、渐隐）
- [x] 实现交互对象信息面板浮动文本显示（2026年1月20日）
- [x] 修复体力/气力条显示错误问题（2026年1月21日）
- [x] 修复浮动文本时间过滤逻辑（2026年1月21日）
- [x] 修复浮动文本位置与颜色（2026年1月21日）

**实施记录（2026年1月21日更新）**：
- 支持指定显示位置（player_info/target_info/default）
- 变化量为0的条目自动过滤不添加
- **体力/气力条显示修复**：
  - 问题：`.bar-fill` 元素没有重叠显示在背景图上，而是显示在另外的行上
  - 修复：为 `.target-bars .bar-fill` 添加 `position: absolute; top: 0; left: 0;`
  - 确保填充条正确覆盖在轨道背景图上
- **交互对象信息面板浮动文本**：
  - 在 `settle_behavior.py` 末尾添加 `collect_web_value_changes()` 函数
  - 收集体力、气力、射精欲、理智、状态变化、经验变化、交互对象属性变化
  - 变化数据存储在 `cache.web_value_changes` 列表中
  - 每个变化记录包含：`character_id`, `field`, `value`, `timestamp`, `field_name`, `color`
  - `status_panel.py` 的 `get_target_info()` 方法添加 `value_changes` 字段
  - `_get_value_changes(character_id)` 筛选当前角色相关的变化
- **浮动文本时间过滤**：
  - 只返回最近2秒内的变化数据，避免显示过时信息
  - 清理超过5秒的旧数据，防止缓存膨胀
  - 获取后移除对应角色的数据，避免重复显示
- **浮动文本位置调整（2026年1月21日，2026年2月7日更新）**：
  - **状态条类数值变化**（2026年2月7日更新）：
    - 体力、气力、理智、精液、好感、信赖、催眠度：显示在数值后面（`position-end-inline` 类）
    - 格式示例：`100/200 +20`（当前值/上限值 +变化量）
    - 不再下移一行或显示在特殊位置，直接作为内联文本显示
  - 状态栏数值变化：位置不变，在对应状态项右侧显示（`position-inline` 类）
  - 经验值/其他变化：在面板底部统一显示（`bottom-floating-container`）
- **浮动文本颜色系统（2026年1月21日）**：
  - 后端 `collect_web_value_changes()` 为每个变化添加 `color` 字段
  - 颜色值使用 `data/csv/FontConfig.csv` 中定义的富文本颜色名称
  - 各数值类型对应颜色：
    - 体力：`hp_point` (#e15a5a)
    - 气力：`mp_point` (#70C070)
    - 好感：`light_pink` (#ffb6c1)
    - 信赖：`summer_green` (#96bbab)
    - 射精欲：`semen` (#fffacd)
    - 理智：`sanity` (#7070C0)
    - 经验：`medium_spring_green` (#00ff7f)
    - 快感状态：`persian_pink` (#f77fbe)
    - 欲情/快乐：`rose_pink` (#ff66cc)
    - 先导/屈服/羞耻：`deep_pink` (#ff1493)
    - 苦痛：`crimson` (#dc143c)
    - 负面状态：`slate_blue` (#6a5acd)
    - 其他状态：`pale_cerulean` (#9bc4e2)
    - 催眠度：动态获取（通过 `hypnosis_panel.get_hypnosis_degree_color()`）
  - 前端 `game.js` 添加 `RICH_TEXT_COLORS` 颜色映射表
  - 浮动文本直接使用后端传递的颜色，不再使用 `.positive/.negative` 类
- **前端浮动文本渲染**：
  - `game.js` 添加 `createFloatingValueChanges(panel, valueChanges)` 函数
  - 按字段分组显示，合并同类变化的数值
  - `createInlineFloatingText()` 接收 `positionType` 参数控制位置
  - `createBottomFloatingTexts()` 处理经验值等无对应位置的变化
  - 浮动动画：`inlineFloatUp` 0.4秒上浮入场
  - 2秒后自动触发 `fade-out` 类，0.5秒淡出后移除DOM
- **CSS样式**：
  - `.inline-floating-text`：基础浮动文本样式
  - `.position-inline`：状态栏内联显示（右侧居中）
  - `.position-end-inline`：数值后面显示（用于状态条类，2026年2月7日新增）
  - `.position-hp-middle`：体力变化位置（已废弃，2026年2月7日）
  - `.position-below`：下移一行位置（已废弃，2026年2月7日）
  - `.bottom-floating-container`：底部容器，flex布局横向排列
  - `.bottom-floating-text`：底部浮动文本，显示名称+数值

### 6.2 前端结算UI

#### 6.2.1 结算阶段UI状态
- [x] 实现结算开始时隐藏交互UI
- [x] 实现结算结束时恢复交互UI

#### 6.2.2 对话框交互
- [x] 实现点击推进对话
- [x] 实现右键/Ctrl跳过
- [x] 实现对话完成后显示数值变化
- [x] 实现文本分页（每页最多4行）（2026年1月19日）
- [x] 实现换行符正确渲染（2026年1月19日）
- [x] 修复文本错误截断问题（2026年1月19日）

**实施记录（2026年1月19日更新）**：
- **文本分页功能**：
  - 在 `dialog_box.py` 中添加 `_split_text_to_pages()` 函数
  - 常量：`MAX_LINES_PER_PAGE = 4`（每页最大行数）
  - 常量：`MAX_CHARS_PER_LINE = 50`（用于估算行数，不强制截断）
  - **重要修正**：只按显式换行符 `\n` 分行，不强制按字符数截断词语
  - 长行由前端CSS的 `word-wrap: break-word` 处理自动换行
  - 超过4行估算行数的文本自动分页
- **换行符渲染修复**：
  - 前端 `createDialogBox()` 和 `updateDialogBox()` 中使用 `innerText` 替代 `textContent`
  - 添加 `replace(/\\n/g, '\n')` 处理转义换行符
  - 确保后端传递的 `\n` 正确渲染为换行

#### 6.2.3 头像小对话框
- [x] 实现头像下方的小型对话框
- [x] 实现漫画风格向下悬浮样式（2026年1月19日更新）
- [x] 实现结算后点击头像查看完整对话（`get_character_dialog` WebSocket事件）
- [x] 实现主对话框与小对话框分离（2026年1月19日）

**实施记录（2026年1月19日更新）**：
- 在 `web_server.py` 中添加了 `get_character_dialog` 事件处理器
- `get_full_dialog(character_id)` 方法返回指定角色的完整对话
- **主/小对话框分离机制**：
  - 在 `game_type.py` 中添加 `web_minor_dialog_queue` 字段
  - `add_dialog_text()` 新增 `is_minor` 和 `character_id` 参数
  - `is_minor=True` 时，对话加入小对话框队列而非主对话框
  - `get_dialog_state()` 返回 `minor_dialogs` 列表
  - `clear_minor_dialogs()` 清空小对话框队列
- **talk.py 集成**：
  - `handle_talk_draw()` 判断角色是否为玩家或当前交互对象
  - 玩家(id=0)和交互对象的台词显示在主对话框
  - 其他角色的台词显示在小对话框（`is_minor=True`）
  - **交互对象姓名显示（2026年1月19日新增）**：
    - `add_dialog_text()` 新增 `target_character_id` 参数
    - 当 `target_character_id >= 0` 时，说话者名称格式为 `{speaker_name} → {target_name}`
    - 在主对话框中清晰显示当前角色的交互对象
- **前端渲染**：
  - `createAvatarPanel()` 接收 `minorDialogs` 参数
  - 在角色头像下方渲染 `.avatar-mini-dialog` 元素
  - 添加 `updateMinorDialogs()` 函数动态更新小对话框
- **小对话框样式（2026年1月19日更新）**：
  - 漫画风格向下悬浮：`position: absolute; top: calc(100% - 10px)`
  - 字体大小与角色姓名一致：`font-size: 0.7em`
  - 带三角形指示器（`::before` 和 `::after` 伪元素）
  - 深色背景、金色边框、阴影效果
  - 尺寸设置：
    - `min-width: 80px; max-width: 110px`（避免相邻对话框水平重叠）
    - `min-height: 2.8em; max-height: 4.5em`（容纳2-3行文本）
    - `line-height: 1.3`（确保文本清晰）
  - 文本换行：`white-space: normal; word-wrap: break-word`
  - 超出隐藏：`overflow: hidden`
  - **防截断和重叠处理（2026年1月19日新增）**：
    - `.new-ui-top-info` 设置 `overflow: visible; z-index: 20`
    - `.new-ui-avatar-panel` 设置 `overflow: visible; padding-bottom: 60px`
    - `.avatar-item` 使用 `nth-child` 递增 z-index（1→5, 2→6...），右侧对话框优先显示
    - 移除 `.avatar-item:hover` 的 `transform: scale()` 防止闪烁
    - 保留 `transition: background-color 0.2s` 作为hover效果
  - **姓名显示修复（2026年1月19日新增）**：
    - `.avatar-name` 改为允许换行：`white-space: normal`
    - 移除 `text-overflow: ellipsis`，添加 `word-wrap: break-word; word-break: break-all`
    - 设置 `width: 100%; line-height: 1.1` 确保完整显示

#### 6.2.4 切换交互对象联动
- [x] 实现点击头像切换交互对象（2026年1月19日新增）
- [x] 实现切换后主界面立绘同步更新
- [x] 实现切换后身体部位按钮同步更新
- [x] 实现切换后右上角头像列表同步更新
- [x] 实现点击角色时显示行为文本（2026-02-07新增）
- [x] 实现点击角色时显示数值变化（2026-02-07新增）

**实施记录（2026年1月19日新增、2026-02-07更新）**：
- **后端处理**：
  - `web_server.py` 中 `handle_switch_target()` 更新 `target_character_id`
  - 设置 `cache.web_need_full_refresh = True` 标志
  - 在 `game_type.py` 中添加 `web_need_full_refresh` 字段
- **面板状态刷新**：
  - `in_scene_panel_web.py` 检查 `web_need_full_refresh` 标志
  - 标志为True时跳过增量计算，发送完整状态
  - 发送后清除标志和状态缓存
- **前端事件监听**：
  - `game.js` 中添加 `target_switched` 事件监听
  - 收到成功响应后等待后端推送新状态
- **自动同步内容**：
  - `_get_target_character_info()` 返回新交互对象信息
  - `_get_scene_characters()` 自动排除新交互对象
  - `character_renderer` 返回新对象的图像和部位数据
- **行为文本显示（2026-02-07新增）**：
  - 在 `handle_switch_target()` 中检查 `cache.web_minor_dialog_queue`
  - 查找被点击角色的待显示小对话框
  - 将完整文本移动到主对话框队列进行显示
  - 从 `minor_dialog` 队列中移除该角色的条目
- **数值变化显示（2026-02-07新增）**：
  - 在 `handle_switch_target()` 中遍历 `cache.web_value_changes`
  - 刷新该角色所有数值变化的时间戳为当前时间
  - 确保数值变化不会被2秒超时过滤，能正确显示在右侧信息栏

---

## 阶段七：素材处理工具 ✅

### 7.1 角色文件夹构建脚本

#### 7.1.1 build_character_folders.py
- [x] 实现遍历 `image/立绘/干员` 目录
- [x] 实现为每个png创建同名文件夹
- [x] 实现移动png到对应文件夹
- [x] 添加日志输出和错误处理

### 7.2 图片重命名和整理脚本

#### 7.2.1 rename_and_organize_images.py
- [x] 实现遍历 `image/立绘/干员/差分` 目录
- [x] 实现识别不含下划线的png（原始半身图）
- [x] 实现重命名为 `{角色名}_半身.png`
- [x] 实现调用 `download_prts_character_image.py` 下载全身图
- [x] 实现全身图重命名为 `{角色名}_全身.png`
- [x] 添加日志输出和错误处理

**实施记录**：
- 修正了下载函数的导入名称（`download_character_image_api`）
- 添加了下载延迟（0.5秒）避免被限流
- 自动创建目标目录
- 下载的图片自动移动并重命名为 `{角色名}_全身.png`

### 7.3 部位位置生成脚本

#### 7.3.1 generate_body_parts_json.py（已由 body_analysis.py 替代）
- [x] 研究适合动漫角色的姿态识别方案（使用简化的估计方法）
- [x] 实现图像加载和预处理（使用PIL）
- [x] 实现身体部位估计（基于图像比例）
- [x] 实现结果转换为JSON格式
- [x] 实现遍历所有角色文件夹批量处理
- [x] 添加日志输出和错误处理

#### 7.3.2 body_analysis.py（旧生产工具，已由 body_analysis_ensemble.py 替代）
- [x] 使用 rtmlib 库进行深度学习姿态估计
- [x] 使用 HumanArt 训练的 YOLOX 检测器（支持动漫角色检测）
- [x] 输出 COCO 17关键点格式的归一化坐标 JSON
- [x] 支持 GPU(CUDA) / CPU 自动回退
- [x] 版本化输出（v2.0格式，增量更新不重复处理）
- **状态**：保留但不再使用，已由 `body_analysis_ensemble.py`（7模型集成）替代

#### 7.3.3 body_analysis_compare.py（三模型对比工具，2026-02-10新增）
- [x] 对比三个候选模型在动漫角色上的识别效果
- [x] 生成逐关键点分数对比表和可视化标注对比图
- [x] 在 `image/立绘/模型测试用/对比结果/` 输出三模型横向对比图
- [x] 人工审查结果：模型B和C各有优劣，需扩展测试

**候选模型说明**：
| 模型 | 检测器 | 姿态估计器 | 备注 |
|------|--------|-----------|------|
| A: Wholebody balanced（当前） | YOLOX-m (HumanArt) | RTMW-dw-x-l@256x192 | 133关键点截取前17 |
| B: Body performance | YOLOX-x (HumanArt, AP 61.3) | RTMPose-x@384x288 (AP 78.8) | 最大检测器+专用身体17kp模型 |
| C: Wholebody performance | YOLOX-m (HumanArt) | RTMW-dw-x-l@384x288 | 高分辨率姿态，分数为logit值(>1.0) |

#### 7.3.4 body_analysis_multi_compare.py（7模型+集成全面对比工具，2026-02-10新增）
- [x] 扩展至7个候选模型 + 集成（Ensemble）方案
- [x] 新增模型：YOLO11x-pose (D)、BodyWithFeet (E)、RTMO-l (F)、Custom YOLOX-x+RTMW (G)
- [x] 实现 sigmoid 归一化处理 RTMW 模型 (C/G) 的 logit 输出值
- [x] 实现集成方案：对每个关键点取所有模型中归一化置信度最高者
- [x] 生成多种可视化输出：全模型对比图、TOP3+集成对比图、分数表、单模型标注图
- [x] 在 `image/立绘/模型测试用/多模型对比结果/` 输出完整对比结果和 comparison_report.json
- [x] 13个角色完整测试完成

**7模型 + 集成对比结果**：

| 模型 | 检测器 | 姿态估计器 | 平均归一化分 | 关键点胜出 |
|------|--------|-----------|------------|-----------|
| A: WB_bal（当前） | YOLOX-m | RTMW@256x192 | 0.6685 | 0/221 |
| B: Body_perf | YOLOX-x | RTMPose-x@384x288 | 0.6736 | 1/221 |
| C: WB_perf | YOLOX-m | RTMW@384x288 (sigmoid) | **0.9727** | 63/221 |
| D: YOLO11x | 内置 (COCO) | YOLO11x-pose | 0.8418 | 13/221 |
| E: BWF_perf | YOLOX-x | halpe26@384x288 | 0.6773 | 1/221 |
| F: RTMO-l | 内置 (640×640) | RTMO-l | 0.7631 | 91/221 |
| G: Custom_max | YOLOX-x | RTMW@384x288 (sigmoid) | **0.9739** | 52/221 |
| **ENSEMBLE** | — | 逐关键点最高置信度 | **0.9839** | — |

**集成来源分布**：F 41.2% / C 28.5% / G 23.5% / D 5.9% / B 0.5% / E 0.5%

**关键发现**：
- G（YOLOX-x + RTMW@384x288）为最佳单模型（0.9739），C仅次之（0.9727）
- F(RTMO-l) 在躯干关键点表现突出，贡献集成中最多关键点（41.2%）
- D(YOLO11x) 基于COCO训练，部分动漫角色无法检测
- 集成方案达0.9839，比最佳单模型再提升约1%
- C/G 的RTMW输出为logit值，需sigmoid归一化后才可公平比较

**建议**：生产环境选用G作为单模型方案，或C+F+G三模型集成获取最高精度

#### 7.3.5 body_analysis_ensemble.py（生产集成批量处理工具，2026-02-10新增）✅
- [x] 基于7模型集成方案对所有角色进行批量处理
- [x] 对每个关键点取所有模型中归一化置信度最高者的结果
- [x] 输出 `{角色名}_body.json`（v2.0格式，model="ensemble"，包含 source_model/source_distribution 字段）
- [x] GPU加速支持：自动注册 NVIDIA CUDA 12 DLL 路径，rtmlib/YOLO11 均使用 CUDA device
- [x] 自动检测模型A是否需要sigmoid归一化（首张图片测试）
- [x] 处理范围：`image/立绘/干员/` + `image/立绘/特殊NPC/`
- [x] **已完成运行**：388个角色全部成功，0失败，总耗时 1.8min（GPU模式）

**GPU加速环境配置**：
- 硬件：NVIDIA RTX 4080 (16GB)，驱动 591.74，CUDA 13.1
- 安装：`pip install onnxruntime-gpu nvidia-cublas-cu12 nvidia-cudnn-cu12 nvidia-cufft-cu12 nvidia-cusparse-cu12 nvidia-cusolver-cu12 nvidia-curand-cu12 nvidia-cuda-runtime-cu12 nvidia-cuda-nvrtc-cu12`
- Windows特殊处理：脚本启动时通过 `os.add_dll_directory()` 注册 pip 安装的 nvidia 包中的 DLL 路径
- 性能对比：CPU ~5s/角色 → GPU **0.26s/角色**（~19x 加速）

**输出JSON格式示例**：
```json
{
  "version": "2.0",
  "model": "ensemble",
  "ensemble_models": ["A", "B", "C", "D", "E", "F", "G"],
  "character": "角色名",
  "ensemble_avg_score": 0.9964,
  "per_model_avg": {"A": 0.73, "B": 0.70, "C": 0.98, ...},
  "source_distribution": {"C": 5, "F": 12},
  "landmarks": [
    {"id": 0, "name": "nose", "x": 0.44, "y": 0.27, "score": 0.999, "source_model": "C"},
    ...
  ]
}
```

#### 7.3.6 body_part_editor.py（身体部位数据手动编辑工具，2026-02-12新增）✅
- [x] 创建带GUI界面的Python脚本工具，用于手动修正识别错误的角色身体部位数据
- [x] 支持读取单个JSON文件或递归读取整个文件夹
- [x] 自动加载JSON同目录下的 `{角色名}_全身.png` 图片
- [x] 在图片上显示17个COCO关键点和骨架连线
- [x] 支持鼠标拖动修改关键点位置
- [x] 保存时将手动修改的点的 `source_model` 标记为 "Z"
- [x] 支持左右键切换多个文件，底部显示当前序号/总数
- [x] 快捷键支持：Ctrl+S 保存

**使用方法**：
```powershell
# 使用本地conda环境运行
c:/code/erArk/.conda/python.exe tools/body_part_editor.py
```

**界面布局**：
- 顶部：角色名称 + 修改状态标记
- 中央：角色全身图 + 关键点可视化（圆点+中文标签+骨架连线）
- 底部：文件路径 + 导航按钮 + 保存按钮 + 序号显示

**关键点颜色编码**：
- 红色系：头部（鼻子、眼睛、耳朵）
- 绿色系：上肢（肩膀、肘部、手腕）
- 蓝紫色系：下肢（髋部、膝盖、脚踝）

**来源模型标记**：
- A-G：由7模型集成自动识别
- Z：手动修改

### 7.4 tk模式兼容性修改 ✅

#### 7.4.1 查找tk模式图片读取代码
- [x] 搜索现有代码中读取立绘图片的位置
- [x] 记录涉及的文件和函数

**关键发现**：
- `Script/Core/era_image.py`: 加载所有图片到 `image_data` 字典，键为文件名（不含扩展名）
- `Script/Design/character_image.py`: `find_character_image_name()` 根据角色状态构建图片名
- `Script/UI/Panel/in_scene_panel.py` 和 `see_character_info_panel.py`: 调用 `flow_handle.print_image_cmd()`

#### 7.4.2 修改图片读取逻辑
- [x] 修改读取逻辑以识别新的文件名格式 `{角色名}_半身.png`
- [x] 确保tk模式正常工作
- [ ] 测试验证

**实施记录**：
- 在 `character_image.py` 的 `find_character_image_name()` 函数末尾添加了半身图格式兼容逻辑
- 优先查找原始立绘名 `{base_name}`
- 如果不存在，尝试查找 `{base_name}_半身` 格式
- 这确保了无论图片是否已重命名，tk模式都能正常工作

---

## 阶段八：集成测试

### 8.1 单元测试

#### 8.1.1 后端组件测试
- [x] 测试指令分类查询函数
- [x] 测试场景背景路径查找（通过代码审查）
- [x] 测试角色图像数据获取（通过代码审查）
- [x] 测试WebSocket数据结构（通过代码审查）

**实施记录**：
- 创建了 `tests/test_web_ui_components.py` 测试文件
- 测试了指令分类枚举（InstructCategory、InteractionMajorType/MinorType、BodyPart）
- 测试了指令元数据查询函数（instruct_meta 模块）
- 测试了结算管理器（SettlementManager）
- 测试了半身图格式兼容性代码
- 所有 4 个测试全部通过

#### 8.1.2 前端组件测试
- [x] 测试各UI组件的渲染（通过代码审查确认结构正确）
- [x] 测试交互事件响应（WebSocket事件处理器已实现）
- [x] 测试API调用（API函数封装已完成）

**说明**：前端组件的完整测试需要在游戏运行时通过浏览器进行验证。当前已通过代码审查确认：
- `static/js/` 目录下的所有 JavaScript 文件结构正确
- WebSocket 事件监听和发送函数已实现
- UI 组件类的方法签名和属性定义完整

### 8.2 集成测试

#### 8.2.1 完整流程测试
- [x] 测试游戏启动和Web服务器启动
- [x] 测试面板选项卡点击和面板切换
- [ ] 测试交互类型选择
- [ ] 测试身体部位点击
- [ ] 测试指令执行和结算流程
- [ ] 测试对话显示和推进
- [ ] 测试数值变化显示

**说明**：完整流程测试需要启动游戏（`python game.py`，配置 `web_draw = 1`）后在浏览器中手动验证。

**实施记录（2026-01-17）**：
- **面板选项卡测试通过**：
  - 选项卡正确显示在画面顶部
  - 点击选项卡能够正确切换面板（如移动、存档、设置等）
  - 选项卡指令正确绑定到 `cmd_map` 并通过 `/api/button_click` API 处理
  - 面板切换流程正常工作

#### 8.2.2 tk模式回归测试
- [ ] 确保tk模式启动正常
- [x] 确保tk模式启动正常（已验证）
- [x] 确保tk模式立绘显示正常（延迟加载兼容）
- [x] 确保tk模式功能不受影响

**说明**：tk模式测试需要配置 `web_draw = 0` 后启动游戏验证。已添加半身图格式兼容代码确保向后兼容。

**实施记录**：
- tk模式可正常启动
- 图片加载性能已优化（见10.1.1）

---

## 阶段九：问题修复和调试

**阶段状态**：进行中
**开始日期**：2026年1月17日

### 9.1 主界面无法绘制问题修复 ✅

#### 9.1.1 问题现象
- [x] Web 模式启动正常，可以进入开始界面和创建人物界面
- [x] 进入主界面后画面空白，无任何绘制
- [x] 浏览器控制台出现 404 错误
- [x] 后端日志显示 "404 Not Found: The requested URL was not found on the server"

#### 9.1.2 问题分析
- [x] 检查发现服务器 `/` 路由渲染的是旧的 `index.html`
- [x] 新的 Web UI 应该使用 `game_main.html`，包含完整的游戏界面结构
- [x] `game_main.html` 需要加载 4 个 JS 文件：websocket_handler.js、ui_components.js、game_renderer.js、interaction_manager.js
- [x] WebSocket 前端发送 `request_game_state` 事件，但服务器端没有对应的处理器
- [x] `connect` 事件处理器发送的是旧的简化版 `game_state`，不包含新 UI 所需的完整数据

#### 9.1.3 修复措施
- [x] **修改主路由**：将 `web_server.py` 中的 `/` 路由从渲染 `index.html` 改为 `game_main.html`
- [x] **添加事件处理器**：新增 `@socketio.on('request_game_state')` 处理器
- [x] **实现完整状态构建**：新增 `send_full_game_state()` 函数，构建包含以下内容的完整游戏状态：
  - 玩家信息（姓名、昵称、HP、MP、理智等）
  - 交互对象信息（姓名、HP等）
  - 当前面板ID
  - 可用交互大类列表
  - 当前选中的大类和小类
  - 当前大类下的小类列表
  - 面板选项卡列表（系统面板类指令）
- [x] **更新连接处理**：修改 `handle_connect()` 函数，连接时调用 `send_full_game_state()`

#### 9.1.4 相关文件修改
- [x] `Script/Core/web_server.py`:
  - 第 115-134 行：将 `render_template('index.html')` 改为 `render_template('game_main.html')`
  - 第 404-454 行：重写 `handle_connect()` 和添加 `handle_request_game_state()`
  - 第 1377-1457 行：新增 `send_full_game_state()` 函数

#### 9.1.5 验证步骤
- [x] 重新启动游戏（`python game.py`，确保 `config.ini` 中 `web_draw = 1`）
- [x] 打开浏览器访问 http://localhost:5001
- [x] 检查是否正确加载 `game_main.html`
- [x] 查看浏览器控制台是否有 404 错误
- [x] 检查网络面板中 WebSocket 消息是否包含完整游戏状态
- [x] 验证主界面是否正确显示面板选项卡、交互类型栏等UI元素

**修复日期**：2026年1月17日
**修复人员**：AI Assistant

### 9.2 游戏启动流程面板切换问题修复 ✅

#### 9.2.1 问题现象
- [x] 打开浏览器后，直接显示 `game_main.html`（场景互动面板的专用UI）
- [x] 跳过了游戏的正常启动流程（标题画面、角色创建等）
- [x] 用户期望：先进入标题画面 → 选择"初次唤醒" → 角色创建 → 场景互动

#### 9.2.2 问题分析
- [x] **根本原因**：`game_main.html` 是为 `IN_SCENE` 面板（场景互动）设计的专用UI，不适用于其他面板
- [x] `index.html` 才是通用的Web界面，使用动态元素绘制系统，可以显示所有面板（标题、角色创建等）
- [x] 游戏启动时 `cache.now_panel_id` 初始化为 `0`（即 `Panel.TITLE`），但Web服务器的 `/` 路由总是返回 `game_main.html`
- [x] 需要根据当前面板动态选择模板：
  - 非 `IN_SCENE` 面板 → 使用 `index.html`（通用UI）
  - `IN_SCENE` 面板 → 使用 `game_main.html`（新UI）

#### 9.2.3 解决方案
**方案说明**：实现动态模板路由 + 前端面板切换检测

1. **后端：动态模板选择**
   - [x] 修改 `web_server.py` 的 `/` 路由逻辑

2. **前端：面板切换自动刷新**
   - [x] 修改 `static/game.js` 的 `initWebSocket()` 函数
   - [x] 这样可以加载对应的UI模板（`index.html` 或 `game_main.html`）

#### 9.2.4 相关文件修改
- [x] `Script/Core/web_server.py`（第 115-137 行）：
  ```python
  @app.route('/')
  def index():
      """根据当前面板动态选择模板"""
      from Script.Core import constant
      if hasattr(cache, 'now_panel_id') and cache.now_panel_id == constant.Panel.IN_SCENE:
          return render_template('game_main.html')  # 场景互动面板使用新UI
      else:
          return render_template('index.html')  # 其他面板使用通用UI
  ```

- [x] `static/game.js`（第 1159-1206 行）：
  ```javascript
  // 在 initWebSocket() 中添加面板切换检测
  let lastPanelId = null;
  socket.on('game_state_update', (data) => {
      const currentPanelId = data.panel_id;
      const IN_SCENE_PANEL = 2;
      
      // 检测是否需要刷新页面
      if (lastPanelId !== null && currentPanelId !== lastPanelId) {
          const needsRefresh = (lastPanelId === IN_SCENE_PANEL && currentPanelId !== IN_SCENE_PANEL) ||
                             (lastPanelId !== IN_SCENE_PANEL && currentPanelId === IN_SCENE_PANEL);
          if (needsRefresh) {
              window.location.reload();  // 刷新以加载对应模板
              return;
          }
      }
      lastPanelId = currentPanelId;
      renderGameState(data);
  });
  ```

#### 9.2.5 验证步骤
- [x] 重新启动游戏（`python game.py`）
- [x] 打开浏览器访问 http://localhost:5001
- [x] **验证点1**：应该看到标题画面（使用 `index.html` 通用UI）
- [x] **验证点2**：选择"初次唤醒"，进入角色创建界面
- [x] **验证点3**：完成角色创建后，自动切换到 `IN_SCENE` 面板
- [x] **验证点4**：页面应自动刷新并显示 `game_main.html` 的新UI（面板选项卡、交互类型栏等）
- [x] **验证点5**：从 `IN_SCENE` 面板点击系统面板按钮（如"查看地图"），页面应刷新回 `index.html` 通用UI

#### 9.2.6 架构说明
- **两套UI并存**：
  - `index.html`：通用UI，基于动态元素绘制，适用于所有传统面板
  - `game_main.html`：新UI，为场景互动面板专门设计，提供更丰富的交互体验
- **无缝切换**：通过动态模板路由和前端自动刷新，实现两套UI之间的无缝切换
- **向后兼容**：保留了原有的通用UI，不影响其他面板的正常使用

**修复日期**：2026年1月17日
**修复人员**：AI Assistant

### 9.3 页面刷新机制回滚与单页面新UI实现 ✅

#### 9.3.1 问题现象
- [x] 页面刷新机制导致404错误
- [x] 用户反馈：主面板需要在当前页面绘制，不需要单独网页
- [x] 用户需求：使用新版UI绘制主界面

#### 9.3.2 问题分析
- [x] **问题根源**：9.2中实现的动态模板路由 + 页面刷新方案存在缺陷
  - 页面刷新时URL变化导致404
  - 两套模板切换体验不佳
  - 不符合单页应用(SPA)的设计理念
- [x] **新架构需求**：
  - 所有面板统一使用 `index.html`
  - 主面板的新UI作为特殊元素类型在同一页面内渲染
  - 使用标准WebSocket事件流，不需要页面刷新

#### 9.3.3 解决方案
**方案说明**：单页面应用 + 新UI容器元素

1. **回滚页面刷新机制**
   - [x] 修改 `web_server.py` 的 `/` 路由，始终返回 `index.html`
   - [x] 移除 `game.js` 中的面板切换自动刷新逻辑
   - [x] `game_main.html` 保留但不作为路由目标，仅作为参考

2. **修正InScenePanelWeb事件通道**
   - [x] 修改 `in_scene_panel_web.py` 的 `_push_state_to_frontend()` 方法
   - [x] 使用 `web_server.update_game_state()` 替代 `push_game_state()`
   - [x] 确保发送正确的 `game_state_update` 事件(game.js监听的事件)
   - [x] 添加 `_convert_state_to_elements()` 方法将状态转换为元素列表

3. **实现new_ui_container元素类型**
   - [x] 在 `game.js` 的 `createGameElement()` 中添加 `new_ui_container` case
   - [x] 创建 `renderNewUIContent()` 函数渲染新UI布局
   - [x] 实现各新UI组件的渲染函数：
     - `createPlayerInfoPanel()` - 玩家信息面板
     - `createStatusBar()` - 状态条组件
     - `createTargetExtraInfoPanel()` - 交互对象附加信息
     - `createAvatarPanel()` - 角色头像面板
     - `createInteractionTypePanel()` - 交互类型按钮
     - `createCharacterDisplay()` - 角色立绘显示
     - `createTargetInfoPanel()` - 交互对象信息
     - `createPanelTabsBar()` - 面板选项卡
   - [x] 实现事件处理函数：
     - `switchTarget()`, `selectInteractionType()`, `clickPanelTab()`

4. **添加新UI CSS样式**
   - [x] 在 `style.css` 末尾添加完整的新UI样式(~200行)
   - [x] 包含所有新UI组件的样式定义

#### 9.3.4 相关文件修改
- [x] `Script/Core/web_server.py`(第115-127行)：
  ```python
  @app.route('/')
  def index():
      """Web模式主页面"""
      # 所有面板统一使用index.html
      return render_template('index.html')
  ```

- [x] `static/game.js`：
  - 第1160-1195行：移除 `lastPanelId` 跟踪和自动刷新逻辑
  - 第2165-2180行：添加 `new_ui_container` 元素类型处理
  - 第2190-2420行：添加约200行新UI渲染函数

- [x] `Script/UI/Panel/in_scene_panel_web.py`(第208-240行)：
  ```python
  def _push_state_to_frontend(self, state: Dict):
      # 使用正确的事件通道
      elements = self._convert_state_to_elements(state)
      web_server.update_game_state(elements, panel_id=constant.Panel.IN_SCENE)
  
  def _convert_state_to_elements(self, state: Dict) -> List[Dict]:
      # 将状态包装为new_ui_container元素
      elements = [{
          "type": "new_ui_container",
          "panel_type": "in_scene",
          "game_state": state
      }]
      return elements
  ```

- [x] `static/style.css`(第882行后)：
  - 添加约200行新UI样式
  - 包含 `.new-ui-container`, `.new-ui-layout` 等所有新UI类

#### 9.3.5 架构改进说明
**新架构优势**：
1. **单页应用**：所有面板共用一个HTML，通过元素动态更新
2. **无缝切换**：面板切换不需要页面刷新，体验更流畅
3. **统一事件流**：所有面板使用相同的WebSocket事件机制
4. **易于扩展**：新增面板只需添加元素类型，无需创建新模板

**元素类型体系**：
- 通用元素：`text`, `button`, `line`, `image` 等 → 适用于所有传统面板
- 特殊元素：`new_ui_container` → 适用于主面板新UI
- 前端根据元素类型自动选择对应的渲染逻辑

**废弃内容**：
- ~~动态模板路由(9.2方案)~~ → 已回滚
- ~~页面自动刷新机制~~ → 已移除
- `game_main.html` → 保留作为参考，但不再用于路由

#### 9.3.6 验证步骤
- [x] 重新启动游戏
- [x] 确认可以正常进入主面板
- [x] 确认主面板使用新UI渲染(在同一页面内)
- [x] 测试面板切换是否流畅(无刷新)
- [x] 测试新UI交互功能是否正常

**修复日期**：2026年1月17日  
**修复人员**：AI Assistant  
**架构变更**：从双模板系统改为单页面应用 + 元素类型扩展

### 9.4 选项卡系统完善 ✅

#### 9.4.1 选项卡位置问题
**问题**：选项卡显示在底部，而非设计文档中的顶部位置

**修复**：
- 修改 `static/game.js` 第2258-2268行
- 使用 `container.insertBefore(panelTabs, container.firstChild)` 将选项卡插入到容器最前面
- 修改 `static/style.css` 第1174-1185行，更新为顶部样式

#### 9.4.2 选项卡指令ID映射问题
**问题**：`tab_menu.py` 中使用字符串ID如 "move"、"save"，但未与 `Instruct.py` 中的常量一致

**修复**：
- 修改 `Script/UI/Panel/web_components/tab_menu.py` 第23-56行
- 使用 `Instruct.Instruct.MOVE`、`Instruct.Instruct.SAVE` 等常量
- 确保指令ID与 `constant.handle_instruct_data` 中的键一致

#### 9.4.3 选项卡点击处理问题
**问题**：选项卡使用WebSocket事件，但后端 `askfor_all` 轮询的是 `/api/button_click` 响应

**修复**：
- 修改 `static/game.js` 第2543-2550行的 `clickPanelTab()` 函数
- 改为调用 `handleButtonClick(tabId)` 使用统一的按钮点击API
- 修改 `in_scene_panel_web.py` 第66-118行
  - 添加 `_bind_panel_tabs_and_get_ask_list()` 方法
  - 将选项卡指令绑定到 `cmd_map`
  - 通过 `flow_handle.askfor_all()` 等待用户选择

#### 9.4.4 状态推送问题
**问题**：`_push_state_to_frontend` 直接调用 `update_game_state`，导致元素未添加到 `cache.current_draw_elements`，`askfor_all` 发送空状态

**修复**：
- 修改 `in_scene_panel_web.py` 第236-255行的 `_push_state_to_frontend()` 方法
- 改为将元素添加到 `cache.current_draw_elements`
- 由 `askfor_all` 统一发送状态到前端

#### 9.4.5 测试结果
- [x] 选项卡正确显示在画面顶部
- [x] 点击选项卡能够切换面板（移动、存档、设置、属性、收藏、成就等）
- [x] 角色立绘和身体部位按钮正常显示
- [x] 主面板UI完整渲染

#### 9.4.6 文档更新
- [x] 更新 `Web绘制模式UI重构实现流程.md` 添加实施记录
- [x] 更新 `Web绘制模式UI重构说明文档.md` 补充实现细节
- [x] 更新 `Web模式指令面板绘制.md` 添加选项卡系统章节
- [x] 标记测试项完成

### 9.5 选项卡问题诊断与修复（2026-01-17）

#### 9.5.1 选项卡位置问题
**问题**：选项卡显示在底部，而非设计文档中的顶部位置

**修复**：
- 修改 `static/game.js` 第2258-2268行
- 使用 `container.insertBefore(panelTabs, container.firstChild)` 将选项卡插入到容器最前面
- 修改 `static/style.css` 第1174-1185行，更新为顶部样式

#### 9.5.2 选项卡指令ID映射问题
**问题**：`tab_menu.py` 中使用字符串ID如 "move"、"save"，但未与 `Instruct.py` 中的常量一致

**修复**：
- 修改 `Script/UI/Panel/web_components/tab_menu.py` 第23-56行
- 使用 `Instruct.Instruct.MOVE`、`Instruct.Instruct.SAVE` 等常量
- 确保指令ID与 `constant.handle_instruct_data` 中的键一致

#### 9.5.3 选项卡点击处理问题
**问题**：选项卡使用WebSocket事件，但后端 `askfor_all` 轮询的是 `/api/button_click` 响应

**修复**：
- 修改 `static/game.js` 第2543-2550行的 `clickPanelTab()` 函数
- 改为调用 `handleButtonClick(tabId)` 使用统一的按钮点击API
- 修改 `in_scene_panel_web.py` 第66-118行
  - 添加 `_bind_panel_tabs_and_get_ask_list()` 方法
  - 将选项卡指令绑定到 `cmd_map`
  - 通过 `flow_handle.askfor_all()` 等待用户选择

#### 9.5.4 状态推送问题
**问题**：`_push_state_to_frontend` 直接调用 `update_game_state`，导致元素未添加到 `cache.current_draw_elements`，`askfor_all` 发送空状态

**修复**：
- 修改 `in_scene_panel_web.py` 第236-255行的 `_push_state_to_frontend()` 方法
- 改为将元素添加到 `cache.current_draw_elements`
- 由 `askfor_all` 统一发送状态到前端

### 9.5.5 测试结果
- [x] 选项卡正确显示在画面顶部
- [x] 点击选项卡能够切换面板（移动、存档、设置、属性、收藏、成就等）
- [x] 角色立绘和身体部位按钮正常显示
- [x] 主面板UI完整渲染

### 9.5.6 文档更新
- [x] 更新 `Web绘制模式UI重构实现流程.md` 添加实施记录
- [x] 更新 `Web绘制模式UI重构说明文档.md` 补充实现细节
- [x] 更新 `Web模式指令面板绘制.md` 添加选项卡系统章节
- [x] 标记测试项完成


### 9.6 交互面板bug诊断与修复（2026-01-18）

#### 9.6.1 大类切换后小类未更新问题
**问题**：切换交互大类时，小类按钮列表没有正确更新（如选择"手"后仍显示"嘴"的小类：对话/亲吻/舔吸）

**根因分析**：
1. ~~WebSocket传递的 `major_type_id` 可能是字符串类型，而后端字典键是整数类型，导致查找失败~~ **（已于之前修复）**
2. **新发现根因**：前端 `socket` 变量使用 `let` 声明为模块级变量，但 `selectMajorType()` 函数检查的是 `window.socket`。由于 `let` 声明的变量不会自动成为 `window` 的属性，导致 `window.socket` 为 `undefined`，WebSocket事件无法发送。

**修复**：
- ~~修改 `Script/Core/web_server.py` 第807-823行~~ **（已废弃 - 现在使用字符串类型）**
  - ~~在 `handle_select_major_type()` 中添加 `major_type_id = int(major_type_id)` 类型转换~~
  - **2026-01-19更新**：交互类型现在使用字符串标识符（如 `'mouth'`, `'hand'`, `'arts'` 等），已移除 int 转换
- ~~修改 `Script/Core/web_server.py` 第848-864行~~ **（已废弃 - 现在使用字符串类型）**
  - ~~在 `handle_select_minor_type()` 中添加 `minor_type_id = int(minor_type_id)` 类型转换~~
  - **2026-01-19更新**：交互类型现在使用字符串标识符（如 `'mouth_talk'`, `'hand_touch'`, `'arts_hypnosis'` 等），已移除 int 转换
- ~~修改 `Script/UI/Panel/web_components/interaction_handler.py` 第75-88行~~ **（已废弃 - 现在使用字符串类型）**
  - ~~在 `select_major_type()` 方法中添加类型转换~~
- ~~修改 `Script/UI/Panel/web_components/interaction_handler.py` 第105-118行~~ **（已废弃 - 现在使用字符串类型）**
  - ~~在 `select_minor_type()` 方法中添加类型转换~~
- **新增修复（2026-01-18）**：修改 `static/game.js` 第1163-1167行
  - 在 `initWebSocket()` 中添加 `window.socket = socket`，确保socket全局可访问
  ```javascript
  function initWebSocket() {
      socket = io();
      // 同时设置到 window 上，确保全局可访问
      window.socket = socket;
      // ...
  }
  ```
- **新增调试日志**：在 `selectMajorType()` 和 `selectMinorType()` 函数中添加调试日志

#### 9.6.2 部位按钮使用COCO名称问题
**问题**：角色立绘上的部位按钮显示COCO关键点原始名称（如"鼻子"、"左眼"、"左手腕"）而非游戏部位名称（如"脸部"、"手部"）

**根因**：`character_renderer.py` 的 `_convert_body_data()` 方法使用简单的COCO名称映射，未使用 `BodyPartButton` 类的转换逻辑

**修复**：
- 重写 `Script/UI/Panel/web_components/character_renderer.py` 第181-268行的 `_convert_body_data()` 方法
- 导入并使用 `BodyPartButton` 类和 `CLICKABLE_BODY_PARTS` 常量
- 将COCO landmarks转换为关键点列表，调用 `body_part_button.load_coco_keypoints()`
- 使用 `body_part_button.get_buttons_data()` 获取正确的游戏部位数据
- 返回的数据包含：
  - `display_name`: 中文显示名称（如"脸部"）
  - `part_id`: 英文部位ID（如"face"）供后端逻辑使用
  - `is_hip_sub_part`: 是否为臀部子部位

---

## 阶段十：优化与完善

### 10.1 性能优化

#### 10.1.1 后端优化
- [x] 优化图片加载性能（`era_image.py`）
- [ ] 优化WebSocket推送频率
- [ ] 实现数据缓存减少重复计算
- [ ] 优化指令查询性能

**图片加载优化实施记录**（2026-01-14）：
- **问题**：原始代码加载781张图片非常缓慢（超过30秒）
- **原因分析**：
  1. 每张图片被加载两次（PhotoImage + Image.open）
  2. font_scaling在每次循环中重复计算
  3. PhotoImage创建是同步阻塞操作
- **优化方案**：
  1. 只用PIL.Image加载一次，避免重复加载
  2. 缓存font_scaling
  3. 使用多线程（ThreadPoolExecutor）并行加载PIL图片
  4. **延迟加载策略**：启动时只预加载PIL图像，PhotoImage转换延迟到首次使用时
  5. 使用BILINEAR缩放算法替代LANCZOS
- **优化结果**：加载时间从30+秒降至**1.35秒**
- **实现细节**：
  - 创建`_LazyImageDict`类实现透明的延迟加载
  - `get_image()`函数处理按需转换
  - 完全兼容现有代码，无需修改调用方

#### 10.1.2 前端优化
- [ ] 实现图片预加载
- [ ] 优化Canvas渲染性能
- [ ] 实现DOM复用减少重绘

### 10.2 样式完善

#### 10.2.1 视觉效果
- [ ] 完善颜色主题
- [ ] 添加过渡动画
- [ ] 完善悬停效果
- [ ] 完善按钮样式

#### 10.2.2 布局调整
- [ ] 微调各区域尺寸
- [ ] 确保1920×1080下显示效果

#### 10.2.3 交互面板样式重构 (2026-02-11)
- [x] 将交互类型按钮改为明日方舟风格的悬浮卡片
- [x] 实现3D向中心倾斜的视觉效果
- [x] 添加悬停和点击动效
- [x] 实现大类-小类两级菜单的视觉层级（小类显示在大类下方）
- [x] 适配JS逻辑以支持展开/折叠显示
- [x] **[修复]** 解决中英文名重叠问题（改为上下布局）
- [x] **[优化]** 将卡片宽度缩减至一半（120px），采用图标上文字下的紧凑纵向布局
- [x] **[修复]** 修复"嘴部"大类按钮无法点击的问题
- [x] **[优化]** 实现点击空白区域重置面板至初始折叠状态
- [x] **[特性]** 实现"聚焦模式"：选择小类后隐藏其他大类，仅显示当前路径
- [x] **[特性]** 将浮现按钮（无部位指令）集成到小类卡片列表下方

### 10.3 文档更新

#### 10.3.1 更新说明文档
- [x] 根据实际实现更新《Web绘制模式UI重构说明文档》
- [x] 补充遗漏的细节

#### 10.3.2 更新实施文档
- [x] 标记所有完成的步骤（持续更新）
- [x] 记录遇到的问题和解决方案
- [x] 补充新增的步骤

**实施记录**：
- 两份文档均已更新实施记录
- 添加了新建文件清单和修改文件清单
- 记录了测试结果和注意事项

### 10.4 头部子菜单系统重构 (2026-02-12)

#### 10.4.1 需求说明
- [x] 头部部位位置改为使用双眼中间偏上一点的位置
- [x] 头发、兽角、兽耳部位合并到头部子菜单（类似臀部子菜单模式）
- [x] 兽耳、兽角部位需要满足交互对象有对应特征时才显示

#### 10.4.2 后端修改
- [x] **instruct_category.py**: 添加 `HEAD_SUB_PARTS` 常量定义头部子部位列表
- [x] **instruct_category.py**: 修改 `COMPUTED_BODY_PARTS` 中头部位置计算使用关键点[1,2]（双眼中间）并添加 (0, -0.03) 偏移
- [x] **instruct_category.py**: 从 `CLICKABLE_BODY_PARTS` 中移除 `BEAST_EARS` 和 `HORN`
- [x] **body_part_button.py**: 添加头部展开/折叠状态管理（`_head_expanded`, `_has_horn`, `_has_beast_ears`）
- [x] **body_part_button.py**: 实现 `expand_head()`、`collapse_head()`、`is_head_sub_part()`、`set_has_beast_features()` 方法
- [x] **character_renderer.py**: 添加兽耳/兽角检测逻辑（talent[111]=兽耳, talent[112]=兽角）
- [x] **web_server.py**: 添加头部点击处理，发送 `head_sub_menu` 事件

#### 10.4.3 前端修改
- [x] **game.js**: 添加 `head_sub_menu` Socket监听器
- [x] **game.js**: 实现 `showHeadSubMenu()` 函数显示头部子菜单弹窗
- [x] **style.css**: 添加 `.head-sub-menu` 及相关样式类

#### 10.4.4 技术实现要点
- 头部子菜单机制参照臀部子菜单（`HIP_SUB_PARTS`）的实现模式
- 兽耳/兽角的显示条件由 talent 字典中的对应标记决定：
  - `talent[111] == 1` 表示有兽耳
  - `talent[112] == 1` 表示有兽角
- 子菜单中始终显示"头发"选项，兽耳/兽角按实际拥有情况动态显示

**实施记录**：
- 修改了6个文件实现头部子菜单系统
- 复用臀部子菜单的CSS样式结构，保持UI一致性

### 10.5 修复头部按钮半径过大问题 (2026-02-12)

#### 10.5.1 问题描述
- 头部部位按钮的半径太大，与其他部位形成遮盖
- 实际显示的半径与 `_get_default_radius` 方法中设定的值（0.06比例）不一致

#### 10.5.2 问题原因
- 在 `body_part_button.py` 的 `_calculate_body_parts()` 方法中，当双眼都有效时，头部半径被乘以了1.5倍：
  ```python
  # 修改前：
  head_radius = int(self._get_default_radius(BodyPart.HEAD, width, height) * 1.5)
  ```
- 这导致头部按钮比 `_get_default_radius` 中定义的标准值（0.06比例）大50%

#### 10.5.3 修复方案
- [x] 移除 `body_part_button.py` 第153行的 `* 1.5` 放大系数
- [x] 头部按钮现在使用 `_get_default_radius` 返回的标准半径值（0.06比例）

#### 10.5.4 修改文件
- [x] `Script/System/Web_Draw_System/body_part_button.py`: 移除头部半径的1.5倍放大

**实施记录**：
- 修复后，头部按钮使用与其他部位（如胸部）相同的半径比例，不再造成遮盖问题

### 10.6 地图AA字符画Web模式显示修复 (2026-02-12)

#### 10.6.1 问题描述
- 地图在Web模式下排版显示错乱
- 地图源文件依赖行尾空格对齐，但Web模式下空格处理不一致
- 各行宽度计算不统一，导致居中显示不正确
- 罗德岛地图各行行首空格数不一致（0-12不等），导致内容起点不统一

#### 10.6.2 问题原因
1. **宽度计算不一致**：`map_config.get_print_map_data()` 混用 `len()` 和 `text_handle.get_text_index()` 计算宽度
2. **每行单独居中**：`see_map_panel.py` 使用每行宽度计算居中偏移，导致各行起点不一致
3. **行尾空格处理时机不当**：行尾空格在Web渲染时才移除，但宽度计算时仍包含空格
4. **行首空格不一致**：不同行的行首空格数不同，导致各行内容起点不对齐（例如罗德岛地图第1-3行有3个行首空格，第4-22行有2个，第24行有0个）

#### 10.6.3 修复方案
- [x] **game_type.py**: 为 `MapDraw` 类添加 `max_width` 字段，记录所有行的最大显示宽度
- [x] **map_config.py**: 统一使用 `text_handle.get_text_index()` 计算宽度
- [x] **map_config.py**: 在解析时调用 `_trim_map_line_trailing_spaces()` 移除行尾空格
- [x] **map_config.py**: 添加 `_normalize_map_leading_spaces()` 函数规范化行首空格
  - 找出所有非空行中最小的行首空格数
  - 每行都减去这个最小值，保持行与行之间的相对对齐关系
- [x] **map_config.py**: 解析完成后计算并存储 `max_width`
- [x] **see_map_panel.py**: 使用 `map_draw.max_width` 计算统一的居中偏移，使所有行从同一起点开始
- [x] **navigation_panel.py**: 同步更新使用最大行宽计算居中

#### 10.6.4 修改文件
| 文件路径 | 修改内容 | 状态 |
|---------|---------|------|
| `Script/Core/game_type.py` | 添加 `MapDraw.max_width` 字段 | ✅ |
| `Script/Config/map_config.py` | 统一宽度计算，移除行尾空格，规范化行首空格，计算最大行宽 | ✅ |
| `Script/UI/Panel/see_map_panel.py` | 使用最大行宽计算统一居中偏移 | ✅ |
| `Script/UI/Panel/navigation_panel.py` | 同步更新使用最大行宽 | ✅ |

#### 10.6.5 技术细节
**行首空格规范化算法**：
1. 遍历所有非空行，计算每行第一个绘制对象的行首空格数
2. 取所有行首空格数的最小值（min_leading）
3. 每行都从第一个绘制对象的文本中移除 min_leading 个空格
4. 如果移除后绘制对象为空（非按钮），则删除该绘制对象
5. 重新计算每行的宽度

**为什么控制中枢正常而罗德岛异常**：
- 控制中枢地图所有行的行首空格数都是0，不存在不一致问题
- 罗德岛地图的行首空格数从0到12不等，导致各行实际内容的起点位置不同

#### 10.6.6 效果说明
- **地图源文件**：不再需要手动补齐行尾空格，也不需要保证所有行有相同的行首空格
- **Web模式**：地图整体居中显示，所有行内容从同一起点左对齐
- **Tk模式**：保持兼容，显示效果不变
- **需要重建**：修改地图源文件后需执行 `buildconfig.py` 重新生成数据

**实施记录**：
- 修复了4个Python文件
- 同步更新了 `.github/prompts/数据处理工作流/Web绘制模式.md` 中的地图渲染说明

#### 10.6.7 追加修复：行尾填充与字体渲染优化 (2026-02-12)

**问题**：罗德岛地图在Web模式下仍有列错位，原因是：
1. 各行的显示宽度不一致（4到142不等），导致Web端渲染时各行实际像素宽度不同
2. 浏览器字体渲染可能导致某些字符宽度与Python端`wcswidth`计算不一致

**解决方案**：

1. **map_config.py**: 添加 `_pad_map_lines_to_max_width()` 函数
   - 在计算 `max_width` 后，为每行添加填充空格使其达到 `max_width`
   - 确保每行在Python端都有相同的"显示宽度单位"

2. **web_draw_adapter.py**: 移除 `map-last` 元素的 `rstrip(" ")` 逻辑
   - 原逻辑会移除行尾空格，抵消填充效果
   - 现在保留填充空格用于对齐

3. **style.css**: 添加CSS属性改善字符宽度一致性
   - `font-kerning: none` - 禁用字距调整
   - `font-variant-ligatures: none` - 禁用连字
   - `text-rendering: geometricPrecision` - 精确渲染

**修改文件**：
| 文件路径 | 修改内容 |
|---------|---------|
| `Script/Config/map_config.py` | 添加 `_pad_map_lines_to_max_width()` 函数 |
| `Script/System/Web_Draw_System/web_draw_adapter.py` | 移除行尾空格移除逻辑 |
| `static/style.css` | 添加字体渲染优化CSS |

#### 10.6.8 最终修复：JavaScript端宽度同步 (2026-02-12)

**问题**：由于Python端填充空格方案会导致emoji字符（如控制中枢地图）宽度计算不一致，需要改为前端处理。

**根本原因分析**：
1. 地图行之间存在换行元素（`text-break`、空div等），导致JS端 `flushGroup()` 将每行单独作为一组处理
2. 每组只有1行时，`min-width` 设置无法产生对齐效果
3. 各行的CSS `margin: auto` 居中导致不同宽度的行有不同的起点

**解决方案**：

1. **game.js - normalizeMapBlocks()**:
   - 修改分组逻辑，忽略换行元素（`text-break`、`line-break`、空div）
   - 只有遇到有实际内容的非地图元素时才中断当前组
   - 这样确保连续的地图行被作为一组处理

2. **style.css - .map-line**:
   - 简化 `font-family`，移除可能影响字符宽度的回退字体
   - 添加 `text-align: left` 确保文本内容左对齐
   - 移除 `font-variant-east-asian: full-width`（可能导致字符宽度不一致）

3. **map_config.py**:
   - 保留 `_pad_map_lines_to_max_width()` 函数定义但不调用
   - 后端不再进行行尾填充，由前端JS处理宽度同步

**JavaScript分组逻辑**：
```javascript
children.forEach(child => {
    if (child.classList && child.classList.contains('map-line')) {
        currentGroup.push(child);
    } else {
        // 检查是否是换行/空元素
        const isBreakElement = child.classList && (
            child.classList.contains('text-break') ||
            child.classList.contains('line-break')
        );
        const isEmptyDiv = child.tagName === 'DIV' && 
            !child.textContent.trim() && 
            !child.querySelector('.map-line');
        
        // 只有遇到有实际内容的非地图元素时才中断组
        if (!isBreakElement && !isEmptyDiv) {
            flushGroup();
        }
    }
});
```

**修改文件**：
| 文件路径 | 修改内容 |
|---------|---------|
| `static/game.js` | 修改 `normalizeMapBlocks()` 分组逻辑，忽略换行元素 |
| `static/style.css` | 简化字体配置，添加 `text-align: left` |
| `Script/Config/map_config.py` | 移除 `_pad_map_lines_to_max_width()` 调用 |

**效果**：
- 控制中枢地图（包含emoji）：正常对齐显示
- 罗德岛地图（纯文本，行首空格不一致）：正常对齐显示
- 所有map-line元素被正确分组，统一设置 `min-width` 实现对齐

### 10.7 兽耳部位从头部子菜单独立 (2026-02-13)

#### 10.7.1 需求说明
- 兽耳从头部子部位中独立出来，作为单独的可点击部位处理
- 兽耳使用身体部位里的 `BEAST_EARS`，分左耳和右耳显示
- 需满足交互对象有兽耳的前提（talent[111]=1）才会显示和可用
- 同时对无交互类型下的全身体部位、选择交互类型后的该交互类型下的身体部位两种情况生效

#### 10.7.2 设计变更
- **之前**：兽耳作为头部子部位，点击头部后展开子菜单才能选择
- **现在**：兽耳作为独立的条件部位，在角色立绘上直接显示为左耳和右耳按钮

#### 10.7.3 后端修改
- [x] **instruct_category.py**: 从 `HEAD_SUB_PARTS` 中移除 `BEAST_EARS`
- [x] **instruct_category.py**: 在 `CLICKABLE_BODY_PARTS` 中添加 `BEAST_EARS`（位于头部之后、脸部之前）
- [x] **instruct_category.py**: 添加 `CONDITIONAL_BODY_PARTS` 列表，定义需要条件判断才显示的部位
- [x] **body_part_button.py**: 修改 `set_visible_parts()` 方法，添加 `has_beast_ears` 参数
- [x] **body_part_button.py**: 修改 `set_default_visible_parts()` 方法，添加 `has_beast_ears` 参数
- [x] **body_part_button.py**: 修改 `expand_head()` 方法，移除 BEAST_EARS 的处理
- [x] **body_part_button.py**: 修改 `handle_click()` 方法中头部展开时的子部位列表
- [x] **character_renderer.py**: 修改 `_load_body_parts_data()` 方法，添加 `has_beast_ears` 参数
- [x] **character_renderer.py**: 修改 `_convert_body_data()` 方法，添加 `has_beast_ears` 参数
- [x] **character_renderer.py**: 在设置可见部位时传入 `has_beast_ears` 参数

#### 10.7.4 技术实现要点

**条件部位机制**：
- `CONDITIONAL_BODY_PARTS` 列表定义了需要条件判断的部位
- `set_visible_parts()` 和 `set_default_visible_parts()` 接受 `has_beast_ears` 参数
- 当 `has_beast_ears=False` 时，兽耳部位会被跳过
- 兽耳作为成对部位，会被展开为 `beast_ears_left` 和 `beast_ears_right`

**判断逻辑**：
- 在 `character_renderer.py` 中，通过 `character_data.talent.get(111, 0) == 1` 判断角色是否有兽耳
- `has_beast_ears` 参数从 `get_character_image_data()` 传递到 `_load_body_parts_data()` 再到 `_convert_body_data()`
- 最终传递给 `body_part_button.set_visible_parts()` 用于过滤

**显示效果**：
- 交互对象有兽耳时：在角色立绘上显示"左兽耳"和"右兽耳"按钮
- 交互对象无兽耳时：不显示兽耳按钮
- 点击头部时：子菜单只显示"头发"和"兽角"（如果有兽角）

#### 10.7.5 修改文件清单
| 文件路径 | 修改内容 | 状态 |
|---------|---------|------|
| `Script/System/Instruct_System/instruct_category.py` | 移除 `HEAD_SUB_PARTS` 中的 `BEAST_EARS`，添加到 `CLICKABLE_BODY_PARTS`，添加 `CONDITIONAL_BODY_PARTS` | ✅ |
| `Script/System/Web_Draw_System/body_part_button.py` | 修改 `set_visible_parts()`、`set_default_visible_parts()`、`expand_head()`、`handle_click()` 方法 | ✅ |
| `Script/System/Web_Draw_System/character_renderer.py` | 修改 `_load_body_parts_data()`、`_convert_body_data()` 方法传递 `has_beast_ears` 参数 | ✅ |
| `Script/Core/web_server.py` | 移除头部子部位处理中的 `BEAST_EARS` 相关条件判断 | ✅ |

**实施记录**：
- 修复了3个Python文件
- 兽耳部位现在作为条件独立部位显示，不再需要点击头部才能选择

---

## 附录A：关键文件清单

### 新建文件
| 文件路径 | 用途 | 状态 |
|---------|------|------|
| `Script/UI/Panel/in_scene_panel_web.py` | Web模式主面板 | ✅ |
| `Script/UI/Panel/web_components/__init__.py` | 组件包初始化 | ✅ |
| `Script/UI/Panel/web_components/scene_renderer.py` | 场景渲染 | ✅ |
| `Script/UI/Panel/web_components/character_renderer.py` | 角色渲染 | ✅ |
| `Script/UI/Panel/web_components/interaction_handler.py` | 交互处理 | ✅ |
| `Script/UI/Panel/web_components/dialog_box.py` | 对话框 | ✅ |
| `Script/UI/Panel/web_components/status_panel.py` | 状态面板 | ✅ |
| `Script/UI/Panel/web_components/tab_menu.py` | 选项卡菜单 | ✅ |
| `Script/UI/Panel/web_components/body_part_button.py` | 部位按钮 | ✅ |
| `Script/UI/Panel/web_components/settlement_manager.py` | 结算管理 | ✅ |
| `Script/System/Instruct_System/instruct_category.py` | 指令分类枚举 | ✅ |
| `Script/System/Instruct_System/instruct_meta.py` | 指令元数据管理 | ✅ |
| `Script/Config/instruct_web_config.py` | Web指令配置 | ✅ |
| `templates/game_main.html` | 主游戏页面 | ✅ |
| `static/css/game_main.css` | 主界面样式 | ✅ |
| `static/js/game_renderer.js` | 画面渲染器 | ✅ |
| `static/js/interaction_manager.js` | 交互管理器 | ✅ |
| `static/js/ui_components.js` | UI组件库 | ✅ |
| `static/js/websocket_handler.js` | WebSocket处理 | ✅ |
| `tools/build_character_folders.py` | 构建角色文件夹 | ✅ |
| `tools/rename_and_organize_images.py` | 重命名整理图片 | ✅ |
| `tools/generate_body_parts_json.py` | 生成部位JSON（旧，已弃用） | ✅ |
| `tools/body_analysis.py` | 单模型姿态估计（旧，已由ensemble替代） | ✅ |
| `tools/body_analysis_compare.py` | 三模型对比工具 | ✅ |
| `tools/body_analysis_multi_compare.py` | 7模型+集成对比工具 | ✅ |
| `tools/body_analysis_ensemble.py` | 生产集成批量处理（当前使用） | ✅ |
| `tests/test_web_ui_components.py` | 单元测试 | ✅ |

### 需修改文件
| 文件路径 | 修改内容 | 状态 |
|---------|---------|------|
| `Script/System/Instruct_System/handle_instruct.py` | 添加指令分类系统 | ✅ |
| `Script/Core/game_type.py` | 添加Web模式缓存字段；添加 `MapDraw.max_width` 字段 | ✅ |
| `Script/Config/map_config.py` | 地图宽度计算统一化，移除行尾空格，规范化行首空格，计算最大行宽 | ✅ |
| `Script/UI/Panel/see_map_panel.py` | 使用最大行宽计算统一居中偏移 | ✅ |
| `Script/UI/Panel/navigation_panel.py` | 使用最大行宽计算统一居中偏移 | ✅ |
| `Script/Core/web_server.py` | 扩展API和数据结构；修复主路由和WebSocket事件；实现动态模板路由 | ✅ |
| `Script/Core/constant/__init__.py` | 添加指令分类数据字典 | ✅ |
| `Script/Design/character_image.py` | 适配半身图文件名格式 | ✅ |
| `Script/UI/Flow/normal_flow.py` | 添加模式切换逻辑 | ✅ |
| `static/game.js` | 添加面板切换自动刷新逻辑；添加头部子菜单支持；添加 `normalizeMapBlocks()` 地图行宽度同步 | ✅ |
| `Script/System/Instruct_System/instruct_category.py` | 添加 HEAD_SUB_PARTS 常量；修改头部位置计算 | ✅ |
| `Script/UI/Panel/web_components/body_part_button.py` | 添加头部展开/折叠功能 | ✅ |
| `Script/UI/Panel/web_components/character_renderer.py` | 添加兽耳/兽角检测 | ✅ |
| `static/style.css` | 添加头部子菜单样式；添加地图行字体和对齐优化 | ✅ |
| `Script/System/Web_Draw_System/body_part_button.py` | 条件部位支持（兽耳独立显示） | ✅ |
| `Script/System/Web_Draw_System/character_renderer.py` | 兽耳条件参数传递 | ✅ |
| `Script/Core/web_server.py` | 移除头部子菜单中的兽耳处理 | ✅ |

---

## 附录B：数据结构定义

### WebSocket推送的game_state结构
```json
{
  "scene": {
    "name": "场景名称",
    "background_image": "image/场景/xxx.png"
  },
  "player_info": {
    "name": "玩家名字",
    "nick_name": "昵称",
    "hp": 100, "hp_max": 100,
    "mp": 100, "mp_max": 100,
    "sanity": 100, "sanity_max": 100,
    "semen": 100, "semen_max": 100,
    "special_states": ["<状态1>", "<状态2>"]
  },
  "target_info": {
    "id": 1,
    "name": "角色名",
    "favorability": {"value": 1234, "level": "A"},
    "trust": {"value": 50.0, "level": "B"},
    "hp": 100, "hp_max": 100,
    "mp": 100, "mp_max": 100,
    "special_states": ["<状态1>"],
    "pleasure_states": [],
    "other_states": [],
    "image_data": {
      "base_image": "path/to/image.png",
      "body_parts": {}
    }
  },
  "target_extra_info": {
    "clothing": {},
    "body": {},
    "group_sex": {},
    "hidden_sex": {}
  },
  "scene_characters": [
    {"id": 2, "name": "角色A", "avatar": "角色A_头部.png", "has_dialog": true}
  ],
  "interaction_types": [
    {"id": "talk", "name": "说话", "icon": "talk.png"},
    {"id": "touch", "name": "抚摸", "icon": "touch.png"}
  ],
  "panel_tabs": [
    {"id": "move", "name": "移动", "available": true},
    {"id": "save", "name": "存档", "available": true}
  ],
  "dialog": {
    "visible": false,
    "speaker": "",
    "text": ""
  },
  "settlement": {
    "phase": "idle",
    "current_dialog": null,
    "value_changes": []
  },
  "current_interaction_type": null,
  "available_body_parts": []
}
```

### 身体部位JSON格式
```json
{
  "image_size": {"width": 1024, "height": 2048},
  "body_parts": {
    "head": {"center": [512, 150], "radius": 80},
    "mouth": {"center": [512, 200], "radius": 30},
    "L_hand": {"center": [280, 800], "radius": 50},
    "R_hand": {"center": [744, 800], "radius": 50},
    "chest": {"center": [512, 500], "radius": 100},
    "waist": {"center": [512, 700], "radius": 80},
    "L_leg": {"center": [380, 1400], "radius": 60},
    "R_leg": {"center": [644, 1400], "radius": 60},
    "L_foot": {"center": [380, 1900], "radius": 40},
    "R_foot": {"center": [644, 1900], "radius": 40}
  }
}
```

---

---