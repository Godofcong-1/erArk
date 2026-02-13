# 指令系统Web模式面板绘制

## 概述

本文档详细说明在Web绘制模式下，指令面板的绘制逻辑和实现细节。Web模式是erArk游戏的现代化界面模式，基于Flask+WebSocket实现前后端分离的交互架构。
**架构更新(2026-01-17)**:
- 采用单页面应用(SPA)架构,所有面板共用 `index.html`
- 主面板(IN_SCENE)的新UI通过 `new_ui_container` 元素类型在同一页面渲染
- 废弃了之前的双模板动态路由方案
- 所有面板使用统一的WebSocket事件流(`game_state_update`)
---

## 1. 核心文件结构

```
Script/Core/
├── web_server.py          # Flask服务器和SocketIO事件处理
├── io_web.py              # Web模式IO适配器
└── constant/              # 常量定义（从 Instruct_System 导入指令分类常量）

Script/System/Instruct_System/
├── instruct_category.py   # 指令分类常量
├── instruct_meta.py       # 指令元数据查询
└── handle_instruct.py     # 指令执行处理

Script/UI/
└── web_draw_adapter.py    # 绘制类Web适配器

Script/Config/
└── instruct_web_config.py # Web模式指令配置

static/                    # 前端静态资源
templates/                 # HTML模板
```

---

## 2. Web模式架构

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                        前端 (浏览器)                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  交互类型栏  │  │  角色立绘区  │  │    指令/面板区      │ │
│  │  (左侧菜单)  │  │  (可点击部位) │  │   (按钮/文本)      │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
│                          ↓ ↑                                │
│                    WebSocket通信                            │
└─────────────────────────────────────────────────────────────┘
                           ↓ ↑
┌─────────────────────────────────────────────────────────────┐
│                     后端 (Python)                            │
│  ┌─────────────────┐  ┌─────────────────────────────────┐  │
│  │  web_server.py  │  │      游戏核心逻辑               │  │
│  │  (Flask+SocketIO)│  │  (handle_instruct.py等)        │  │
│  └─────────────────┘  └─────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 通信协议

- **HTTP REST API**: 获取静态数据、图片资源等
- **WebSocket (SocketIO)**: 实时双向通信，处理指令执行、状态更新等

---

## 3. 面板选项卡系统

### 3.1 选项卡定位与布局

**位置**：画面最上方，横向占满整个屏幕宽度

**实施细节（2026-01-17 更新）**：
- 前端位置：通过 `container.insertBefore()` 将选项卡插入到 `new-ui-container` 的最前面
- CSS样式：使用 `.new-ui-panel-tabs` 类，采用网页选项卡样式（底部边框高亮）
- 响应式布局：使用 `flex-wrap: wrap` 和 `justify-content: flex-start`
- 激活状态：当前选项卡使用 `.active` 类，显示金色底部边框

### 3.2 选项卡数据源

选项卡数据由 `Script/UI/Panel/web_components/tab_menu.py` 中的 `TabMenu` 类管理。

**选项卡组成（2026-01-17 更新）**：
1. **主面板选项卡**：始终存在，默认激活，id 为 `__main_panel__`
2. **系统面板类选项卡**：动态获取所有满足前提条件的系统面板类指令

```python
def get_panel_tabs(self) -> List[dict]:
    """
    获取所有面板类选项卡
    
    选项卡来源：
    1. 主面板（始终存在，默认激活）
    2. 所有满足前提条件的系统面板类指令
    
    Returns:
    List[dict] -- 选项卡信息列表，每个元素包含：
        - id: 选项卡ID（主面板为 __main_panel__，其他为指令ID）
        - name: 选项卡显示名称
        - type: 选项卡类型（"main" 或 "panel"）
        - available: 是否可用
        - active: 是否为当前激活的选项卡
    """
    tabs = []
    
    # 1. 添加主面板选项卡（始终存在，默认激活）
    main_tab = {
        "id": MAIN_PANEL_TAB_ID,  # "__main_panel__"
        "name": MAIN_PANEL_TAB_NAME,  # "主面板"
        "type": "main",
        "available": True,
        "active": self._active_tab == MAIN_PANEL_TAB_ID,
    }
    tabs.append(main_tab)
    
    # 2. 获取所有满足条件的系统面板类指令
    panel_instructs = self._get_available_system_panel_instructs()
    
    for instruct_info in panel_instructs:
        tab = {
            "id": instruct_info["id"],
            "name": instruct_info["name"],
            "type": "panel",
            "available": instruct_info["available"],
            "active": self._active_tab == instruct_info["id"],
        }
        tabs.append(tab)
    
    return tabs
```

**系统面板类指令筛选逻辑**：
- 遍历 `constant.instruct_type_data[InstructType.SYSTEM]` 获取所有系统类型指令
- 检查 `constant.instruct_category_data[instruct_id] == InstructCategory.SYSTEM_PANEL`
- 通过 `handle_premise.handle_premise()` 判断前提条件确定可用性

### 3.3 选项卡点击处理

**前端处理** (`static/game.js`)：

```javascript
function clickPanelTab(tabId) {
    // 主面板选项卡激活时不响应点击
    // 其他选项卡使用普通的按钮点击API，tabId就是指令ID
    handleButtonClick(tabId);
}
```

选项卡点击使用与普通按钮相同的 `/api/button_click` API，而非WebSocket事件。

**后端绑定** (`Script/UI/Panel/in_scene_panel_web.py`)：

```python
def _bind_panel_tabs_and_get_ask_list(self) -> List[str]:
    """
    绑定面板选项卡指令并返回可选列表
    
    Returns:
    List[str] -- 可选择的指令ID列表
    """
    from Script.System.Instruct_System import handle_instruct as instruct_handler
    
    ask_list = []
    tabs = self.tab_menu.get_panel_tabs()
    
    for tab in tabs:
        if tab.get("available", True):
            instruct_id = tab["id"]
            ask_list.append(instruct_id)
            # 绑定指令处理函数到 cmd_map
            flow_handle.bind_cmd(
                instruct_id,
                instruct_handler.handle_instruct,
                (instruct_id,)
            )
    
    return ask_list
```

面板选项卡指令被绑定到 `constant.cmd_map`，通过 `flow_handle.askfor_all(ask_list)` 等待用户选择。

### 3.4 选项卡与面板切换流程

1. 用户点击选项卡按钮（如"移动"）
2. 前端发送 `/api/button_click` 请求，参数为指令ID（如 "move"）
3. 后端 `flow_handle_web.askfor_all()` 接收响应
4. 检查指令ID是否在 `cmd_map` 中且有效
5. 执行绑定的指令处理函数 `handle_instruct("move")`
6. 指令执行 `cache.now_panel_id = constant.Panel.SEE_MAP`
7. `InScenePanelWeb.draw()` 的 while 循环检测到面板ID改变，退出循环
8. 游戏流程切换到对应的面板绘制

---

## 4. 绘制元素系统

### 4.1 元素缓冲机制

位于 `Script/Core/io_web.py`：

```python
def _ensure_current_draw_list() -> None:
    """确保当前绘制元素列表存在"""
    if not hasattr(cache, "current_draw_elements"):
        cache.current_draw_elements = []

def append_current_draw_element(element: Dict[str, Any], record_history: bool = True) -> None:
    """
    添加绘制元素
    
    参数:
    element -- 绘制元素字典
    record_history -- 是否记录到历史缓存
    """
    _ensure_current_draw_list()
    cache.current_draw_elements.append(element)
    
    if record_history:
        _record_history_element(element)
```

### 3.2 元素类型

```python
HISTORY_ELEMENT_TYPES = {
    "text",           # 文本
    "line",           # 分隔线
    "title",          # 标题
    "image",          # 图片
    "center_image",   # 居中图片
    "new_ui_container", # 新UI容器(主面板专用,2026-01-17新增)
    "character",      # 角色信息
    "bar",            # 状态条
    "info_bar",       # 信息栏
    "info_character", # 角色信息栏
    "line_wait",      # 等待线
}
```

### 3.3 历史记录管理

```python
MAX_HISTORY_LENGTH = 500  # 历史记录最大行数

def _record_history_element(element: Dict[str, Any]) -> None:
    """记录历史绘制元素"""
    _ensure_history_list()
    lines = _calculate_element_lines(element)
    history_entry = {"element": copy.deepcopy(element), "line_count": lines}
    cache.web_draw_history.append(history_entry)
    cache.web_draw_history_line_total += lines
    
    # 超出限制时删除旧记录
    while cache.web_draw_history_line_total > MAX_HISTORY_LENGTH:
        removed = cache.web_draw_history.pop(0)
        cache.web_draw_history_line_total -= removed.get("line_count", 0)
```

---

## 4. 绘制适配器

### 4.1 WebDrawAdapter 类

位于 `Script/UI/web_draw_adapter.py`：

```python
class WebDrawAdapter:
    """
    Web绘制适配器基类
    用于将原有的tkinter绘制适配到Web界面
    """
```

### 4.2 文本绘制适配

```python
@staticmethod
def adapt_normal_draw(normal_draw: draw.NormalDraw):
    """
    适配普通文本绘制类
    """
    web_element = {
        "type": "text",
        "text": normal_draw.text,
        "font": normal_draw.style,
        "width": normal_draw.width,
        "web_type": getattr(normal_draw, "web_type", ""),
        "tooltip": getattr(normal_draw, "tooltip", "") or "",
    }
    append_current_draw_element(web_element, record_history=True)

@staticmethod
def adapt_center_draw(center_draw: draw.CenterDraw):
    """适配居中文本绘制类"""
    web_element = {
        "type": "text",
        "text": center_draw.text,
        "font": center_draw.style,
        "width": center_draw.width,
        "align": "center",  # 居中标记
        "web_type": getattr(center_draw, "web_type", ""),
        "tooltip": getattr(center_draw, "tooltip", "") or "",
    }
    append_current_draw_element(web_element, record_history=True)

@staticmethod
def adapt_right_draw(right_draw: draw.RightDraw):
    """适配右对齐文本绘制类"""
    web_element = {
        "type": "text",
        "text": right_draw.text,
        "font": right_draw.style,
        "width": right_draw.width,
        "align": "right",  # 右对齐标记
        "web_type": getattr(right_draw, "web_type", ""),
        "tooltip": getattr(right_draw, "tooltip", "") or "",
    }
    append_current_draw_element(web_element, record_history=True)
```

### 4.3 按钮绘制适配

```python
@staticmethod
def adapt_button(button: draw.Button):
    """
    适配按钮绘制类
    """
    # 判断对齐方式
    if isinstance(button, draw.LeftButton):
        align = 'left'
    else:
        align = 'center'
    
    tooltip_text = getattr(button, "tooltip", "") or ""
    
    web_element = {
        "type": "button",
        "text": button.text,
        "return_text": button.return_text,  # 点击返回值
        "font": button.normal_style,
        "width": button.width,
        "web_type": button.web_type,
        "align": align,
        "tooltip": tooltip_text,
    }
    
    append_current_draw_element(web_element, record_history=False)
    
    # 关键：注册按钮事件处理函数
    from Script.Core import flow_handle
    flow_handle.bind_cmd(button.return_text, button.cmd_func, button.args)
```

---

## 5. 服务器端事件处理

### 5.1 SocketIO 事件注册

位于 `Script/Core/web_server.py`：

```python
# Flask应用和SocketIO初始化
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# 游戏状态存储
game_state = {
    "current_draw_elements": [],
    "history": [],
    "waiting_input": False,
    # ...
}
```

### 5.2 交互类型选择事件

**注意**：交互类型系统已更新为大类/小类嵌套结构（2026-01-18），并于2026-01-19进行了重大重构：
- 所有大类和小类ID从数字改为小写英语字符串标识符
- 如 `0` → `"mouth"`，`10` → `"hand_touch"`
- 新增技艺类（信息素、透视、催眠、时停）
- 手类新增日常、娱乐、工作三个小类
- **2026-01-20更新**：删除了"停止交互"大类

#### 5.2.1 旧版接口（已废弃）

```python
@socketio.on('select_interaction_type')
def handle_select_interaction_type(data):
    """
    处理交互类型选择事件（Web新UI）- 已废弃，请使用 select_major_type 和 select_minor_type
    
    参数:
    data (dict): 包含 type_id 的字典
    """
    # ... 旧版逻辑
```

#### 5.2.2 新版接口：大类选择

```python
@socketio.on('select_major_type')
def handle_select_major_type(data):
    """
    选择交互大类型（Web新UI）
    
    参数:
    data (dict): 包含 major_type_id 的字典（字符串，如 'mouth', 'hand', 'sex', 'penis', 'tool', 'arts', 'other'）
    
    功能:
    1. 保存当前大类的小类选择到记忆
    2. 切换到新的大类
    3. 从记忆中恢复该大类上次选中的小类
    4. 返回该大类下的小类列表
    """
    from Script.Design import web_interaction_manager
    from Script.Core import constant
    
    major_type_id = data.get('major_type_id')  # 字符串类型
    
    # 选择大类型，返回记忆的小类型
    remembered_minor = web_interaction_manager.select_major_type(major_type_id)
    
    # 获取该大类下的小类型列表
    minor_types = web_interaction_manager.get_available_minor_types(major_type_id)
    
    socketio.emit('major_type_selected', {
        'major_type_id': major_type_id,
        'major_type_name': constant.get_major_type_name(major_type_id),
        'minor_types': minor_types,
        'remembered_minor_type': remembered_minor,
        'success': True
    })
```

#### 5.2.3 新版接口：小类选择

```python
@socketio.on('select_minor_type')
def handle_select_minor_type(data):
    """
    选择交互小类型（Web新UI）
    
    参数:
    data (dict): 包含 minor_type_id 的字典（字符串，如 'mouth_talk', 'hand_touch', 'arts_hypnosis' 等）
    
    功能:
    1. 更新当前选中的小类
    2. 更新大类记忆
    3. 获取该小类下可用的指令列表（含部位信息）
    4. 获取更新后的target_info（用于刷新右侧面板的可选部位列表）
    """
    from Script.Design import web_interaction_manager
    from Script.Core import constant
    from Script.System.Web_Draw_System.status_panel import StatusPanel
    
    minor_type_id = data.get('minor_type_id')  # 字符串类型
    
    # 选择小类型
    web_interaction_manager.select_minor_type(minor_type_id)
    
    # 获取该小类型下可用的指令列表
    instructs = web_interaction_manager.get_instructs_by_minor_type(minor_type_id)
    
    # 构建指令信息列表（包含部位信息用于前端高亮）
    instruct_list = []
    for instruct_id in instructs:
        name = constant.handle_instruct_name_data.get(instruct_id, f"指令{instruct_id}")
        body_parts = constant.instruct_body_parts_data.get(instruct_id, [])
        instruct_list.append({
            'id': instruct_id,
            'name': name,
            'body_parts': body_parts,
        })
    
    # 获取更新后的交互对象信息（包含可选部位列表）
    status_panel = StatusPanel()
    character_id = cache.character_data[0].target_character_id
    target_info = status_panel.get_target_info(character_id)
    
    socketio.emit('minor_type_selected', {
        'minor_type_id': minor_type_id,
        'minor_type_name': constant.get_minor_type_name(minor_type_id),
        'instructs': instruct_list,
        'target_info': target_info,  # 用于刷新右侧面板
        'success': True
    })
```

#### 5.2.4 前端事件监听

```javascript
// game.js 中的事件监听
socket.on('major_type_selected', (data) => {
    if (data.success) {
        // 更新交互面板的小类按钮
        updateMinorTypeButtons(data.minor_types, data.remembered_minor_type);
    }
});

socket.on('minor_type_selected', (data) => {
    if (data.success) {
        // 更新可交互的身体部位（高亮显示）
        updateAvailableBodyParts(data.instructs);
        
        // 同时更新右侧的交互对象信息面板（包含可选部位列表）
        if (data.target_info) {
            const targetInfoPanel = document.querySelector('.new-ui-target-info');
            if (targetInfoPanel && targetInfoPanel.parentNode) {
                const newTargetPanel = createTargetInfoPanel(data.target_info);
                targetInfoPanel.parentNode.replaceChild(newTargetPanel, targetInfoPanel);
            }
        }
    }
});

// 接收清空交互选择结果事件
socket.on('interaction_selection_cleared', (data) => {
    if (data.success && data.target_info) {
        // 更新右侧的交互对象信息面板（包含可选部位列表）
        const targetInfoPanel = document.querySelector('.new-ui-target-info');
        if (targetInfoPanel && targetInfoPanel.parentNode) {
            const newTargetPanel = createTargetInfoPanel(data.target_info);
            targetInfoPanel.parentNode.replaceChild(newTargetPanel, targetInfoPanel);
        }
    }
});
```

### 5.3 身体部位点击事件

```python
@socketio.on('click_body_part')
def handle_click_body_part(data):
    """
    处理身体部位点击事件
    
    参数:
    data (dict): 包含 part_name 的字典
    
    功能描述：接收前端的部位点击，返回该部位可执行的指令列表
              如果点击的是臀部：
              - 已选择小类时：显示该小类下所有臀部子部位的可用指令
              - 未选择小类时：展开子部位菜单
    """
    from Script.System.Instruct_System import instruct_meta
    from Script.System.Instruct_System.instruct_category import (
        BODY_PART_NAMES, 
        BodyPart, 
        HIP_SUB_PARTS
    )
    from Script.Design import web_interaction_manager
    
    part_name = data.get('part_name')
    logging.info(f"点击身体部位: {part_name}")
    
    # 获取当前选中的交互小类
    current_minor_type = web_interaction_manager.get_current_minor_type()
    
    # 检查是否是臀部点击
    if part_name == BodyPart.HIP or part_name == "臀部":
        if current_minor_type is not None:
            # 已选择小类时，收集该小类下所有臀部子部位的可用指令
            all_instructs = []
            hip_sub_parts = list(HIP_SUB_PARTS) + [BodyPart.CROTCH]  # 包含胯部
            
            for sub_part in hip_sub_parts:
                instructs = web_interaction_manager.get_instructs_by_body_part(
                    sub_part, 
                    minor_type=current_minor_type,
                    check_premise=False
                )
                for instruct_id in instructs:
                    if instruct_id not in [i['id'] for i in all_instructs]:
                        info = instruct_meta.get_web_instruct_info(instruct_id)
                        if info:
                            all_instructs.append({
                                'id': instruct_id,
                                'name': info['name'],
                            })
            
            socketio.emit('body_part_clicked', {
                'part_name': part_name,
                'part_name_cn': BODY_PART_NAMES.get(BodyPart.HIP, "臀部"),
                'available_instructs': all_instructs,
                'single_instruct': len(all_instructs) == 1,
            })
            return
        else:
            # 未选择小类时，展开子部位菜单
            sub_parts = []
            for sub_part in HIP_SUB_PARTS:
                sub_parts.append({
                    'part_id': sub_part,
                    'part_name_cn': BODY_PART_NAMES.get(sub_part, sub_part)
                })
            
            socketio.emit('hip_sub_menu', {
                'part_name': part_name,
                'part_name_cn': BODY_PART_NAMES.get(BodyPart.HIP, "臀部"),
                'sub_parts': sub_parts,
            })
            return
    
    # 其他部位处理逻辑...
```

**臀部子部位高亮映射（2026-02-07 新增）**：
- 臀部（hip）是一个特殊的可点击部位，包含子部位：小穴(vagina)、子宫(womb)、后穴(anus)、尿道(urethra)、尾巴(tail)、胯部(crotch)
- 当选择的交互小类有任何臀部子部位的指令时，臀部按钮也会高亮显示
- 后端：`interaction_handler.py` 的 `_get_available_body_parts_by_minor_type()` 自动添加 `hip` 到可用部位
- 前端：`game.js` 的 `updateAvailableBodyParts()` 检测子部位并高亮臀部
```

### 5.4 指令执行事件

```python
@socketio.on('execute_instruct')
def handle_execute_instruct(data):
    """
    处理指令执行事件
    
    参数:
    data (dict): 包含 instruct_id 的字典
    """
    from Script.Design import handle_instruct as instruct_handler
    from Script.Core import constant
    
    instruct_id = data.get('instruct_id')
    logging.info(f"执行指令: {instruct_id}")
    
    try:
        # 检查指令是否存在
        if instruct_id not in constant.handle_instruct_data:
            socketio.emit('instruct_executed', {
                'instruct_id': instruct_id,
                'success': False,
                'error': '指令不存在'
            })
            return
        
        # 执行指令
        instruct_handler.handle_instruct(instruct_id)
        
        socketio.emit('instruct_executed', {
            'instruct_id': instruct_id,
            'success': True
        })
        
    except Exception as e:
        logging.error(f"执行指令失败: {e}")
        socketio.emit('instruct_executed', {
            'instruct_id': instruct_id,
            'success': False,
            'error': str(e)
        })
```

### 5.5 切换交互对象事件

```python
@socketio.on('switch_target')
def handle_switch_target(data):
    """
    处理切换交互对象事件
    
    参数:
    data (dict): 包含 character_id 的字典
    """
    character_id = data.get('character_id')
    logging.info(f"切换交互对象: {character_id}")
    
    try:
        pl_character_data = cache.character_data[0]
        pl_character_data.target_character_id = character_id
        
        socketio.emit('target_switched', {
            'character_id': character_id,
            'success': True
        })
    except Exception as e:
        socketio.emit('target_switched', {
            'character_id': character_id,
            'success': False,
            'error': str(e)
        })
```

---

## 6. 指令元数据查询

### 6.1 get_web_instruct_info 函数

位于 `Script/System/Instruct_System/instruct_meta.py`：

```python
def get_web_instruct_info(instruct_id: int) -> Optional[Dict]:
    """
    获取单个指令的Web模式分类信息
    
    返回:
    Dict -- 包含分类信息的字典
    """
    from Script.Core import constant
    from Script.System.Instruct_System.interaction_types import get_major_type
    
    if instruct_id not in constant.instruct_category_data:
        return None
    
    minor_type = constant.instruct_minor_type_data.get(instruct_id, 40)  # 40=OTHER_MISC
    major_type = get_major_type(minor_type)
    
    return {
        "instruct_id": instruct_id,
        "name": constant.handle_instruct_name_data.get(instruct_id, ""),
        "category": constant.instruct_category_data.get(instruct_id),
        "category_name": get_instruct_category_name(...),
        "major_type": major_type,
        "major_type_name": get_major_type_name(major_type),
        "minor_type": minor_type,
        "minor_type_name": get_minor_type_name(minor_type),
        # 保留 interaction_type 作为别名
        "interaction_type": minor_type,
        "interaction_type_name": get_minor_type_name(minor_type),
        "body_parts": constant.instruct_body_parts_data.get(instruct_id, []),
        "is_single_part": len(body_parts) == 1,
    }
```

### 6.2 按交互类型查询指令

```python
def get_instructs_by_interaction_type_from_constant(interaction_type: int) -> List[int]:
    """
    根据交互小类型获取指令列表
    """
    from Script.Core import constant
    return [
        instruct_id
        for instruct_id, itype in constant.instruct_minor_type_data.items()
        if itype == interaction_type
    ]
```

### 6.3 按身体部位查询指令

```python
def get_instructs_by_body_part_from_constant(body_part: str) -> List[int]:
    """
    根据身体部位获取相关指令列表
    """
    from Script.Core import constant
    return [
        instruct_id
        for instruct_id, parts in constant.instruct_body_parts_data.items()
        if body_part in parts
    ]
```

---

## 7. 指令分类系统

### 7.1 指令大类 (InstructCategory)

```python
class InstructCategory:
    SYSTEM_PANEL = 0
    """
    系统面板类指令
    - 触发方式：点击选项卡栏的按钮
    - 效果：切换到对应的面板进行绘制
    - 示例：移动、道具、存档等
    """
    
    CHARACTER = 1
    """
    角色交互类指令
    - 触发方式：选择交互类型 → 点击身体部位
    - 效果：直接执行交互并结算
    - 示例：摸头、亲吻、性交等
    """
    
    CHARACTER_PANEL = 2
    """
    角色交互面板类指令
    - 触发方式：同角色交互类
    - 效果：打开临时面板选择后再结算
    - 示例：脱衣服、选择体位等
    """
```

### 7.2 交互类型 (InteractionMajorType / InteractionMinorType)

```python
# 大类型（按使用器官/工具分类）
class InteractionMajorType:
    MOUTH = 0    # 嘴类
    HAND = 1     # 手类
    PENIS = 2    # 阴茎类
    TOOL = 3     # 道具类
    OTHER = 4    # 其他

# 小类型（每个大类下的子分类）
class InteractionMinorType:
    # 嘴类（MOUTH=0）
    MOUTH_TALK = 0     # 对话
    MOUTH_KISS = 1     # 亲吻
    MOUTH_LICK = 2     # 舔吸
    # 手类（HAND=1）
    HAND_TOUCH = 10    # 抚摸
    HAND_SLAP = 11     # 拍打
    HAND_DRESS = 12    # 穿脱
    # 阴茎类（PENIS=2）
    PENIS_RUB = 20     # 摩擦
    PENIS_INSERT = 21  # 插入
    # 道具类（TOOL=3）
    TOOL_DRUG = 30     # 药物
    TOOL_ITEM = 31     # 道具
    # 其他类（OTHER=4）
    OTHER_MISC = 40    # 杂项
```

### 7.3 身体部位映射

```python
# COCO关键点到身体部位的映射
COCO_KEYPOINT_MAPPING = {
    0: (BodyPart.FACE, "direct"),      # 鼻子 -> 脸部
    1: (BodyPart.FACE, "direct"),      # 左眼 -> 脸部
    2: (BodyPart.FACE, "direct"),      # 右眼 -> 脸部
    3: (BodyPart.BEAST_EARS, "direct"), # 左耳 -> 兽耳
    4: (BodyPart.BEAST_EARS, "direct"), # 右耳 -> 兽耳
    5: (BodyPart.ARMPIT, "direct"),    # 左肩 -> 腋部
    6: (BodyPart.ARMPIT, "direct"),    # 右肩 -> 腋部
    9: (BodyPart.HAND, "direct"),      # 左手腕 -> 手部
    10: (BodyPart.HAND, "direct"),     # 右手腕 -> 手部
    11: (BodyPart.HIP, "direct"),      # 左胯 -> 臀部
    12: (BodyPart.HIP, "direct"),      # 右胯 -> 臀部
    13: (BodyPart.LEG, "direct"),      # 左膝 -> 腿部
    14: (BodyPart.LEG, "direct"),      # 右膝 -> 腿部
    15: (BodyPart.FOOT, "direct"),     # 左脚踝 -> 脚部
    16: (BodyPart.FOOT, "direct"),     # 右脚踝 -> 脚部
}
```

### 7.4 复合部位定义

```python
# 臀部展开的子部位
HIP_SUB_PARTS = [
    BodyPart.VAGINA,   # 小穴
    BodyPart.WOMB,     # 子宫
    BodyPart.ANUS,     # 后穴
    BodyPart.URETHRA,  # 尿道
    BodyPart.TAIL,     # 尾巴
]

# 头部展开的子部位
# 注意：兽耳已独立为单独的可点击部位（2026-02-13）
HEAD_SUB_PARTS = [
    BodyPart.HAIR,       # 头发
    BodyPart.HORN,       # 兽角（需要角色有兽角特征）
]

# 主要可点击部位列表（从上到下）
# 注意：兽耳作为条件部位，需要交互对象有兽耳（talent[111]=1）才显示
CLICKABLE_BODY_PARTS = [
    BodyPart.HEAD,        # 点击展开子部位（头发、兽角）
    BodyPart.BEAST_EARS,  # 兽耳（条件部位，分左右显示）
    BodyPart.FACE,
    BodyPart.MOUTH,
    BodyPart.CHEST,
    BodyPart.ARMPIT,
    BodyPart.HAND,
    BodyPart.BELLY,
    BodyPart.HIP,         # 点击展开子部位
    BodyPart.LEG,
    BodyPart.FOOT,
]

# 条件显示的部位列表（需满足特定条件才显示）
CONDITIONAL_BODY_PARTS = [
    BodyPart.BEAST_EARS,  # 兽耳：需要交互对象有兽耳特征 (talent[111]=1)
]
```

### 7.5 可选部位打印区的部位映射规则（2026-02-12 新增）

在交互对象信息区底部的"可选部位打印区"中，需要将指令系统的部位映射到角色立绘中实际存在的部位：

**映射规则**：
1. **头部子部位**（头发/兽角）→ 映射到"头部"
2. **兽耳**（2026-02-13更新）→ 作为独立部位显示，不再映射到头部，需要交互对象有兽耳特征才显示
3. **臀部子部位**（小穴/子宫/后穴/尿道/尾巴/胯部）→ 映射到"臀部"
4. **其他部位**：直接与角色立绘中的 `base_part` 匹配

**实现位置**：`status_panel.py` 的 `_get_available_body_parts_for_display()` 方法

**逻辑说明**：
- 选择交互小类后，获取该小类对应的指令系统部位列表
- 将部位映射为角色立绘中实际存在的部位（使用 `HEAD_SUB_PARTS` 和 `HIP_SUB_PARTS` 判断）
- 与角色立绘中的部位取交集
- 返回最终的可选部位列表（使用角色立绘的中文显示名）

---

## 8. Web指令配置

### 8.1 CSV配置字段（推荐方式）

在 `InstructConfig.csv` 中直接配置Web属性：

| 字段 | 说明 | 示例 |
|------|------|------|
| `web_category` | 指令大类 | 1 (CHARACTER) |
| `web_major_type` | 交互大类型（InteractionMajorType） | 1 (HAND) |
| `web_minor_type` | 交互小类型（InteractionMinorType） | 10 (HAND_TOUCH) |
| `body_parts` | 关联部位，`\|`分隔 | `chest\|mouth` |

配置在 `handle_instruct.py` 的 `add_instruct` 装饰器中自动读取并写入 constant 字典：
- `constant.instruct_major_type_data[instruct_id] = major_type`
- `constant.instruct_minor_type_data[instruct_id] = minor_type`
- `constant.instruct_body_parts_data[instruct_id] = body_parts`

### 8.2 交互类型配置示例

```csv
# InstructConfig.csv
cid,name,web_category,web_major_type,web_minor_type,body_parts
101,聊天,1,0,0,
102,摸头,1,1,10,head
103,摸胸,1,1,10,chest
104,亲吻,1,0,1,mouth
105,正常位,1,2,21,vagina
```

---

## 9. 状态同步机制

### 9.1 游戏状态更新

```python
def update_game_state():
    """更新游戏状态并推送到前端"""
    with state_lock:
        game_state["current_draw_elements"] = cache.current_draw_elements.copy()
        game_state["history"] = [e["element"] for e in cache.web_draw_history]
        # ... 其他状态
    
    socketio.emit('game_state_update', game_state)
```

### 9.2 前端状态同步

前端通过监听 `game_state_update` 事件获取最新状态：

```javascript
socket.on('game_state_update', function(state) {
    // 更新绘制元素
    renderDrawElements(state.current_draw_elements);
    // 更新历史记录
    updateHistory(state.history);
    // ...
});
```

---

## 10. REST API 接口

### 10.1 图片资源接口

```python
@app.route('/image/<path:filename>')
def serve_image(filename):
    """提供游戏图片文件"""
    return send_from_directory(image_dir, filename)

@app.route('/api/get_image_paths')
def get_image_paths():
    """获取所有图片路径"""
    # 返回图片列表供前端预加载
    return jsonify(image_paths)
```

### 10.2 字体配置接口

```python
@app.route('/api/get_font_config')
def get_font_config():
    """获取字体配置"""
    from Script.Config.game_config import config_font
    font_configs = [...]
    return jsonify(font_configs)
```

### 10.3 按钮点击接口

```python
@app.route('/api/button_click', methods=['POST'])
def button_click():
    """处理按钮点击"""
    data = request.json
    button_id = data.get('button_id')
    
    # 触发对应的按钮回调
    flow_handle.trigger_cmd(button_id)
    
    return jsonify({"success": True})
```

---

## 11. Web模式 vs TK模式对比

| 方面 | TK模式 | Web模式 |
|------|--------|---------|
| 绘制方式 | Tkinter直接绘制 | 生成JSON元素 → 前端渲染 |
| 按钮处理 | 回调函数直接执行 | WebSocket事件 → 回调函数 |
| 状态同步 | 内存直接访问 | WebSocket推送 |
| 指令分类 | 类型过滤器 | 交互类型+身体部位 |
| 交互方式 | 文本输入/点击按钮 | 点击立绘部位/选择类型 |

---

## 12. 前端交互流程

### 12.1 标准交互流程

```
1. 用户选择交互类型（左侧菜单）
   → 前端发送 select_interaction_type 事件
   → 后端返回可用部位和指令列表
   → 前端高亮可点击的身体部位
   → 前端渲染无部位指令的浮现按钮（2026-01-18新增）

2. 用户点击身体部位（角色立绘区）
   → 前端发送 click_body_part 事件
   → 后端返回该部位可执行的指令
   → 前端显示指令选择菜单（无论有多少个指令）
   → 用户点击菜单中的指令执行

2b. 用户点击浮现按钮（无部位指令，2026-01-18新增）
   → 前端直接发送 execute_instruct 事件
   → 后端执行指令并结算
   → 后端推送状态更新
   → 前端更新界面显示
```

**更新说明（2026-02-12）**：
- 原来当只有一个可执行指令时会自动执行，现已改为始终显示指令选择菜单
- 这样可以避免误操作，让用户有更好的控制感

### 12.2 无部位指令浮现按钮机制（2026-01-18新增，2026-01-20更新）

**概述**：对于不涉及任何身体部位（body_parts为空数组）的指令，不在角色立绘上显示按钮，而是在主场景区域右侧（交互面板外部）显示浮现按钮。

**实现位置**：
- 前端：`static/game.js` 中的 `renderNewUIContent()` 函数创建容器，`updateAvailableBodyParts()` 和 `renderFloatingInstructButtons()` 函数渲染按钮
- 样式：`static/style.css` 中的 `.interaction-floating-buttons` 和 `.floating-instruct-btn` 类

**数据流程**：
1. 用户选择小类型后，后端返回该小类下所有指令的列表
2. 每个指令包含 `body_parts` 数组
3. 前端区分有部位和无部位的指令：
   - 有部位指令 → 高亮对应的身体部位按钮
   - 无部位指令 → 在浮现按钮容器中渲染

**前端代码逻辑**：
```javascript
function updateAvailableBodyParts(instructs) {
    const availableParts = new Set();
    const noBodyPartInstructs = [];
    
    instructs.forEach(instruct => {
        if (instruct.body_parts && instruct.body_parts.length > 0) {
            // 有部位的指令
            instruct.body_parts.forEach(part => availableParts.add(part));
        } else {
            // 无部位的指令，添加到浮现按钮列表
            noBodyPartInstructs.push(instruct);
        }
    });
    
    // 高亮身体部位
    // ...
    
    // 渲染浮现按钮
    renderFloatingInstructButtons(noBodyPartInstructs);
}

function renderFloatingInstructButtons(instructs) {
    const container = document.getElementById('floating-instruct-buttons');
    if (!container) return;
    
    container.innerHTML = '';
    if (!instructs || instructs.length === 0) {
        container.style.display = 'none';
        return;
    }
    
    container.style.display = 'flex';
    instructs.forEach(instruct => {
        const btn = document.createElement('button');
        btn.className = 'floating-instruct-btn';
        btn.textContent = instruct.name;
        btn.onclick = () => executeInstruct(instruct.id);
        container.appendChild(btn);
    });
}
```

**布局说明（2026-01-18更新）**：
- 浮现按钮容器位于主场景区域（`mainScene`）的右侧，交互面板（`.new-ui-interaction-panel`）外部
- 容器使用 `flex-direction: column` 和 `flex-wrap: wrap` 实现自动换列
- 按钮从上到下依次排列，容器高度受限于视口高度
- 超过可显示高度时自动换到新列（从左到右增长）
- 容器样式：`max-height: min(calc(100vh - 200px), 700px)`，基于视口高度限制，确保在不同屏幕高度下正确换列
- 容器使用绝对定位（`position: absolute`），不影响角色立绘大小

**身体部位按钮匹配机制（2026-01-18更新）**：
- 身体部位按钮使用 `data-part-name`（中文显示名）和 `data-base-part`（英文部位名）两个属性
- 指令配置中的 `body_parts` 使用英文部位名（如 "head", "chest"）
- 前端在匹配时使用 `data-base-part` 与指令的 `body_parts` 进行比较
- 对于左右对称部位（如 "hand_left"），会自动匹配基础部位名（如 "hand"）

**身体部位点击处理机制（2026-01-18更新）**：

1. **前端点击触发**：
   - 用户点击部位按钮触发 `handleBodyPartClick(partName)`
   - 先关闭已有的指令菜单（避免多个菜单同时存在）
   - 发送 `click_body_part` 事件到后端，携带部位名称

2. **后端指令过滤**：
   - 接收中文部位名（如"头部""左手部"）
   - 转换为英文部位名（如"head""hand"）用于匹配指令数据
   - 支持左右方向前缀处理（如"左手部"→"手部"→"hand"）
   - 获取当前选择的交互小类 `web_interaction_manager.get_current_minor_type()`
   - 如果选择了小类，调用 `web_interaction_manager.get_instructs_by_body_part()` 过滤该部位在该小类下的指令
   - 如果未选择小类，返回该部位在所有交互类型下的指令
   - 返回 `body_part_clicked` 事件，包含可用指令列表和是否单一指令标志

3. **前端处理结果**：
   - `handleBodyPartClickResult(data)` 接收后端返回的数据
   - 更新部位tooltip显示：单指令时显示指令名，多指令时显示部位名
   - 单指令时：直接发送 `execute_instruct` 事件执行指令
   - 多指令时：调用 `showInstructMenu()` 在部位位置显示选择菜单

4. **菜单显示**：
   - 使用 `window.lastClickedBodyPartButton` 获取点击的按钮位置
   - 菜单默认显示在按钮右侧，超出边界时自动调整
   - 点击菜单外任意位置关闭菜单
   - 点击其他部位按钮会先关闭当前菜单再处理新部位
   - **滚动条支持（2026-02-07新增）**：
     - 指令按钮放入独立的滚动容器（`.instruct-menu-container`）
     - 滚动容器最大高度：400px（约8个指令按钮）
     - 指令数量 > 8个时自动显示滚动条
     - 滚动条样式：8px宽，金色半透明滑块
     - 支持鼠标滚轮和拖动滑块两种滚动方式
     - 菜单高度根据指令数量动态计算，避免超出屏幕边界

5. **重叠检测与调整**：
   - `checkAndAdjustCharacterImage()` 检测浮现指令列与角色显示区是否重叠
   - **优先右移策略**：先尝试仅右移，如果会与右侧状态栏冲突才缩小
   - 对整个 `character-container`（包含图片和部位按钮层）应用变换
   - 确保角色图片和部位按钮同步变换，位置保持一致
   - 无重叠时恢复角色容器原始状态

6. **部位按钮形状优化**：
   - 使用 `aspect-ratio: 1/1` 确保在任何屏幕比例下按钮都是正圆
   - 使用百分比定位和 `transform: translate(-50%, -50%)` 确保位置准确

7. **空白区域点击**：
   - 点击主场景空白区域触发 `handleMainSceneClick()`
   - 调用 `clearInteractionSelection()` 清空交互选择
   - 清空大类/小类高亮、隐藏浮现按钮、恢复角色容器变换
   - 发送 `clear_interaction_selection` 事件通知后端

3. 用户选择指令
   → 前端发送 execute_instruct 事件
   → 后端执行指令并结算
   → 后端推送状态更新
   → 前端更新界面显示
```

### 12.2 常见问题：浮现按钮显示位置

**更新（2026-02-11）**：
- 浮现按钮（无部位指令）不再显示在屏幕右侧的独立容器中。
- 现在它们以**交互卡片**的形式，直接显示在左侧交互面板中，位于当前选中的小类卡片下方。
- 当选择小类进入聚焦模式后，无关的大类会被隐藏，浮现指令作为扩展操作直接列出，视觉上更加统一。

**前端实现变更**：
- `renderFloatingInstructButtons` 函数不再向 `#floating-instruct-buttons` 插入内容。
- 而是查找 `.interaction-minor-list` 并将指令生成为 `.interaction-card.minor-card.floating-instruct` 元素插入。
- 同时触发大类隐藏逻辑（Focus Mode）。

### 12.3 面板类指令流程

```
1. 用户点击系统面板按钮
   → 前端发送 execute_instruct 事件
   → 后端设置 cache.now_panel_id
   → 后端推送新面板绘制元素
   → 前端渲染新面板

2. 用户在面板中操作
   → 前端发送按钮点击事件
   → 后端处理并更新状态

3. 用户退出面板
   → 返回主交互界面
```

### 12.4 交互大类图标系统（2026-02-13新增）

**概述**：交互大类按钮现在支持显示图片图标，图标位于按钮文本左侧，提供更直观的视觉标识。

**图标文件位置**：`static/assets/ui/`

**图标映射关系**：
| 交互大类ID | 中文名称 | 图标文件 |
|------------|----------|----------|
| `mouth` | 嘴部 | 嘴部.png |
| `hand` | 手部 | 手部.png |
| `sex` | 性爱 | 性爱.png |
| `penis` | 阴茎 | 阴茎.png |
| `tool` | 道具 | 道具.png |
| `arts` | 源石技艺 | 源石技艺.png |
| `other` | 设置 | 设置.png |

**前端实现**（`static/game.js`）：
```javascript
// createInteractionTypePanel() 中的图标生成函数
const getIconHtml = (typeId) => {
    const iconFiles = {
        'mouth': '嘴部.png',
        'hand': '手部.png',
        'sex': '性爱.png',
        'penis': '阴茎.png',
        'tool': '道具.png',
        'arts': '源石技艺.png',
        'other': '设置.png'
    };
    
    const iconFile = iconFiles[String(typeId)];
    if (iconFile) {
        return `<img src="/static/assets/ui/${encodeURIComponent(iconFile)}" alt="${typeId}" class="interaction-icon-img">`;
    }
    return '<span class="interaction-icon-default">●</span>';
};
```

**CSS样式**（`static/css/game_main.css`）：
```css
/* 图片图标样式 */
.interaction-card .icon .interaction-icon-img {
    width: 32px;
    height: 32px;
    object-fit: contain;
    filter: drop-shadow(0 2px 4px rgba(0,0,0,0.5));
}

/* 默认图标样式（无图片时的圆点） */
.interaction-card .icon .interaction-icon-default {
    font-size: 32px;
}
```

**扩展说明**：
- 添加新的交互大类时，需要在 `static/assets/ui/` 目录添加对应的 PNG 图标
- 图标文件名使用中文名称，在代码中通过 `encodeURIComponent()` 处理 URL 编码
- 图标尺寸建议为正方形，实际显示时会缩放至 32x32 像素

---

## 13. 扩展指南

### 13.1 添加新的交互类型

1. 在 `interaction_types.py` 添加小类型常量：
```python
class InteractionMinorType:
    # 在对应大类的编号段内添加
    NEW_MINOR_TYPE = 42  # 新小类型（OTHER类下）
```

2. 添加小类型名称映射：
```python
MINOR_TYPE_NAMES = {
    InteractionMinorType.NEW_MINOR_TYPE: "新类型名",
    # ...
}
```

3. 在 `MAJOR_TO_MINOR_TYPES` 中添加映射关系

4. 在CSV中配置指令的 `web_major_type` 和 `web_minor_type`

### 13.2 添加新的身体部位

1. 在 `instruct_category.py` 添加部位常量：
```python
class BodyPart:
    NEW_PART = "new_part"
```

2. 添加部位名称映射：
```python
BODY_PART_NAMES = {
    BodyPart.NEW_PART: "新部位",
    # ...
}
```

3. 在 `CLICKABLE_BODY_PARTS` 中添加（如需显示为按钮）

4. 配置COCO关键点映射（如需姿态检测）

### 13.3 自定义绘制元素

1. 在 `web_draw_adapter.py` 添加适配方法：
```python
@staticmethod
def adapt_custom_element(element):
    web_element = {
        "type": "custom_type",
        # ... 自定义字段
    }
    append_current_draw_element(web_element)
```

2. 在前端添加对应的渲染逻辑

---

## 14. 调试与日志

### 14.1 服务器日志

```python
import logging

logging.info(f"选择交互类型: {type_id}")
logging.info(f"点击身体部位: {part_name}")
logging.info(f"执行指令: {instruct_id}")
logging.error(f"执行指令失败: {e}")
```

### 14.2 前端调试

```javascript
socket.on('game_state_update', function(state) {
    console.log('Game state updated:', state);
});

socket.on('instruct_executed', function(result) {
    console.log('Instruct executed:', result);
});
```

### 14.3 元素输出调试

```python
# 在 io_web.py 中
# print(f"[io_web] appended element type={elem_type} ...")
```
