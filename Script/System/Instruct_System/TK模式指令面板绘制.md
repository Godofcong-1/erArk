# 指令系统TK模式面板绘制

## 概述

本文档详细说明在TK（Tkinter）绘制模式下，指令面板的绘制逻辑和实现细节。TK模式是erArk游戏的传统GUI模式，基于Python的Tkinter库实现。

---

## 1. 核心文件

```
Script/UI/Panel/
├── see_instruct_panel.py   # 指令面板绘制（核心）
├── in_scene_panel.py       # 场景主面板（调用指令面板）
└── event_option_panel.py   # 事件选项面板（角色自定义指令）

Script/UI/Moudle/
├── draw.py                 # 绘制基础类
└── panel.py                # 面板组件类
```

---

## 2. SeeInstructPanel 类

### 2.1 类定义

位于 `Script/UI/Panel/see_instruct_panel.py`：

```python
class SeeInstructPanel:
    """
    查看操作菜单面板
    
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width           # 最大绘制宽度
        self.return_list: List[str] = []  # 监听的按钮列表
```

### 2.2 初始化过程

```python
def __init__(self, width: int):
    # 初始化指令类型过滤器
    if cache.instruct_type_filter == {}:
        cache.instruct_type_filter[0] = True   # 系统
        cache.instruct_type_filter[1] = True   # 日常
        cache.instruct_type_filter[2] = True   # 娱乐
        cache.instruct_type_filter[3] = True   # 工作
        cache.instruct_type_filter[4] = True   # 技艺
    
    # 从配置加载其他类型
    for instruct_type in game_config.config_instruct_type:
        if instruct_type not in cache.instruct_type_filter:
            cache.instruct_type_filter[instruct_type] = False
    cache.instruct_type_filter[6] = True  # 性爱类默认开启

    # 初始化性爱子类型过滤器
    for instruct_type in game_config.config_instruct_sex_type:
        if instruct_type not in cache.instruct_sex_type_filter:
            if instruct_type == 0:  # 基础类默认开启
                cache.instruct_sex_type_filter[instruct_type] = True
            else:
                cache.instruct_sex_type_filter[instruct_type] = False

    # 初始化单个指令过滤器
    if cache.instruct_index_filter == {}:
        for now_type in cache.instruct_type_filter:
            for instruct in constant.instruct_type_data[now_type]:
                cache.instruct_index_filter[instruct] = True
```

---

## 3. 绘制流程

### 3.1 draw() 方法总览

```python
def draw(self):
    """绘制操作菜单面板"""
    start_instruct = time.time()  # 性能计时
    SINGLE_LINE_INSTRUCT_NUM = int(cache.all_system_setting.draw_setting[11]) + 1
    self.return_list = []
    
    # 1. 确定显示模式（H模式或普通模式）
    # 2. 绘制类型切换按钮栏
    # 3. 遍历并过滤指令
    # 4. 绘制指令按钮
    # 5. 绘制角色自定义指令
    # 6. 绘制系统指令
```

### 3.2 模式判断

```python
# 根据是否显示H指令，区分使用的配置
if handle_premise.handle_now_show_h_instruct(0):
    # H模式：使用性爱子类型配置
    instruct_type_len = len(cache.instruct_sex_type_filter) + 1
    now_instruct_type_list = cache.instruct_sex_type_filter
    now_instruct_config = game_config.config_instruct_sex_type
else:
    # 普通模式：使用主类型配置
    instruct_type_len = len(cache.instruct_type_filter) - 1
    now_instruct_type_list = cache.instruct_type_filter
    now_instruct_config = game_config.config_instruct_type
```

### 3.3 类型切换按钮绘制

```python
# 绘制分隔线
line = draw.LineDraw("-.-", self.width)
line.draw()

# 遍历类型，绘制切换按钮
for now_type in now_instruct_type_list:
    # 普通模式下跳过系统类和性爱类
    if handle_premise.handle_now_show_non_h_instruct(0):
        if now_type == constant.InstructType.SYSTEM:
            continue
        if now_type == constant.InstructType.SEX:
            continue
    
    now_config = now_instruct_config[now_type]
    
    # 根据开关状态设置按钮样式
    if now_instruct_type_list[now_type]:
        # 已开启：使用对应颜色
        now_button = draw.CenterButton(
            f"[{now_config.name}]",
            now_config.name,
            int(self.width / (instruct_type_len - 1)),
            " ",
            now_instruct_config[now_type].color,  # 彩色
            "standard",
            cmd_func=self.change_filter,
            args=(now_type,),
        )
    else:
        # 已关闭：使用灰色
        now_button = draw.CenterButton(
            f"[{now_config.name}]",
            now_config.name,
            int(self.width / (instruct_type_len - 1)),
            normal_style="deep_gray",  # 灰色
            cmd_func=self.change_filter,
            args=(now_type,),
        )
    
    self.return_list.append(now_button.return_text)
    now_button.draw()
```

### 3.4 指令过滤与收集

```python
now_instruct_list = []
now_premise_data = {}  # 前提判断结果缓存

# 遍历所有开启的指令类型
for now_type in cache.instruct_type_filter:
    # 跳过未开启的类型
    if not cache.instruct_type_filter[now_type]:
        continue
    
    # 非H模式跳过性爱类
    if handle_premise.handle_now_show_non_h_instruct(0) and now_type == constant.InstructType.SEX:
        continue
    
    # 遍历该类型下的所有指令
    for instruct in constant.instruct_type_data[now_type]:
        # 调用过滤函数判断是否显示
        filter_judge, now_premise_data = judge_single_instruct_filter(
            instruct, now_premise_data, now_type
        )
        if filter_judge:
            now_instruct_list.append(instruct)

# 按数字ID排序
now_instruct_list.sort(key=lambda x: constant.instruct_id_to_cid.get(x, 999))
```

### 3.5 指令按钮绘制

```python
# 按行分组
instruct_group = value_handle.list_of_groups(now_instruct_list, SINGLE_LINE_INSTRUCT_NUM)

now_draw_list = []
system_draw_list = []

for instruct_list in instruct_group:
    for instruct_id in instruct_list:
        instruct_name = constant.handle_instruct_name_data[instruct_id]
        cid = constant.instruct_id_to_cid.get(instruct_id, 0)
        id_text = text_handle.id_index(cid)  # 格式化ID显示
        now_text = f"{id_text}{instruct_name}"
        
        # 创建按钮
        now_draw = draw.LeftButton(
            now_text,
            str(cid),
            int(self.width / SINGLE_LINE_INSTRUCT_NUM),
            cmd_func=self.handle_instruct,
            args=(instruct_id,),
        )
        
        # 根据类型设置颜色
        for instruct_type in constant.instruct_type_data:
            if instruct_id in constant.instruct_type_data[instruct_type]:
                now_draw.normal_style = game_config.config_instruct_type[instruct_type].color
                break
        
        # H模式使用子类型颜色
        if handle_premise.handle_now_show_h_instruct(0):
            now_sub_type = constant.instruct_sub_type_data[instruct_id]
            now_draw.normal_style = game_config.config_instruct_sex_type[now_sub_type].color
        
        # 系统指令单独收集
        if instruct_id in constant.instruct_type_data[constant.InstructType.SYSTEM]:
            system_draw_list.append(now_draw)
        else:
            now_draw_list.append(now_draw)
        
        self.return_list.append(now_draw.return_text)

# 使用面板组件绘制
now_draw = panel.DrawTextListPanel()
now_draw.set(now_draw_list, self.width, SINGLE_LINE_INSTRUCT_NUM)
now_draw.draw()
```

### 3.6 角色自定义指令绘制

```python
# 获取角色自定义指令
from Script.UI.Panel import event_option_panel
len_son_event_list, son_event_list = event_option_panel.get_target_chara_diy_instruct(0)

if len_son_event_list:
    count = 0
    for event_id in son_event_list:
        count += 1
        event_data = game_config.config_event[event_id]
        pl_character_data = cache.character_data[0]
        target_character_data = cache.character_data[pl_character_data.target_character_id]
        chara_adv = target_character_data.adv
        
        # 获取选项文本
        option_text = event_data.text.split("|")[0]
        option_text = talk.code_text_to_draw_text(option_text, 0)
        now_text = f"[{chara_adv}_{count}]{option_text}"
        return_text = f"{chara_adv}_{count}"
        
        # 创建按钮
        now_draw = draw.LeftButton(
            now_text,
            return_text,
            int(self.width / SINGLE_LINE_INSTRUCT_NUM),
            cmd_func=self.handle_chara_diy_instruct,
            args=(event_id,),
        )
        
        # 使用角色颜色
        if target_character_data.text_color:
            now_draw.normal_style = target_character_data.name
        
        now_draw_list.append(now_draw)
        self.return_list.append(now_draw.return_text)
```

### 3.7 系统指令区域绘制

```python
# 分隔线
line_feed.draw()
line = draw.LineDraw("-.-", self.width)
line.draw()

# 系统指令单独绘制
system_draw = panel.DrawTextListPanel()
system_draw.set(system_draw_list, self.width, SINGLE_LINE_INSTRUCT_NUM)
system_draw.draw()
```

---

## 4. 交互处理

### 4.1 类型过滤切换

```python
def change_filter(self, now_type: int):
    """
    更改指令类型过滤状态
    
    Keyword arguments:
    now_type -- 指令类型ID
    """
    if handle_premise.handle_now_show_h_instruct(0):
        # H模式：切换性爱子类型
        if cache.instruct_sex_type_filter[now_type]:
            cache.instruct_sex_type_filter[now_type] = False
        else:
            cache.instruct_sex_type_filter[now_type] = True
        
        # 技艺类联动
        if now_type == constant.SexInstructSubType.ARTS:
            cache.instruct_type_filter[constant.InstructType.ARTS] = \
                cache.instruct_sex_type_filter[now_type]
    else:
        # 普通模式：切换主类型
        if cache.instruct_type_filter[now_type]:
            cache.instruct_type_filter[now_type] = False
        else:
            cache.instruct_type_filter[now_type] = True
        
        # 技艺类联动
        if now_type == constant.InstructType.ARTS:
            cache.instruct_sex_type_filter[constant.SexInstructSubType.ARTS] = \
                cache.instruct_type_filter[now_type]
```

### 4.2 指令执行处理

```python
def handle_instruct(self, instruct_id_or_cid):
    """
    处理玩家操作指令
    
    Keyword arguments:
    instruct_id_or_cid -- 指令字符串ID或数字cid
    """
    py_cmd.clr_cmd()  # 清除命令缓存
    
    # ID转换：数字cid → 字符串instruct_id
    if isinstance(instruct_id_or_cid, str) and instruct_id_or_cid.isdigit():
        cid = int(instruct_id_or_cid)
        instruct_id = constant.cid_to_instruct_id.get(cid)
        if instruct_id is None:
            instruct_id = instruct_id_or_cid
    else:
        instruct_id = instruct_id_or_cid
    
    # 绘制指令名称
    instruct_name = constant.handle_instruct_name_data[instruct_id]
    now_draw_1 = draw.NormalDraw()
    now_draw_1.text = f"{instruct_name}"
    
    # 检测连续指令
    if len(cache.pl_pre_behavior_instruce):
        last_behavior_id = cache.pl_pre_behavior_instruce[-1]
        if isinstance(last_behavior_id, int):
            cache.pl_pre_behavior_instruce = []
            last_behavior_id = "share_blankly"
        last_behavior_data = game_config.config_behavior[last_behavior_id]
        if instruct_name == last_behavior_data.name:
            now_draw_1.text += _("(连续)")
    
    now_draw_1.text += "\n"
    now_draw_1.draw()
    
    # 分隔线
    line = draw.LineDraw("-", self.width)
    line.draw()
    
    # 执行指令结算
    handle_instruct.handle_instruct(instruct_id)
```

### 4.3 角色自定义指令处理

```python
def handle_chara_diy_instruct(self, event_id: str):
    """
    处理角色自定义指令
    
    Keyword arguments:
    event_id -- 事件ID
    """
    event_data = game_config.config_event[event_id]
    py_cmd.clr_cmd()
    
    # 绘制指令名称
    option_text = event_data.text.split("|")[0]
    option_text = talk.code_text_to_draw_text(option_text, 0)
    instruct_name = option_text
    now_draw_1 = draw.NormalDraw()
    now_draw_1.text = f"{instruct_name}\n"
    now_draw_1.draw()
    
    line = draw.LineDraw("-", self.width)
    line.draw()
    
    # 设置事件标记并执行
    pl_character_data = cache.character_data[0]
    pl_character_data.event.event_id = event_id
    pl_character_data.event.chara_diy_event_flag = True
    handle_instruct.handle_instruct(constant.Instruct.CHARA_DIY_INSTRUCT)
```

---

## 5. 单个指令过滤逻辑

### 5.1 judge_single_instruct_filter 函数

```python
def judge_single_instruct_filter(
    instruct_id: int, 
    now_premise_data: dict, 
    now_type: int, 
    use_type_filter_flag: bool = True, 
    skip_h_judge: bool = False, 
    skip_not_h_judge: bool = False
) -> tuple:
    """
    判断单个指令是否通过过滤
    
    参数:
    instruct_id -- 指令字符串ID
    now_premise_data -- 当前记录的前提数据缓存
    now_type -- 当前指令类型
    use_type_filter_flag -- 是否使用类型过滤
    skip_h_judge -- 是否跳过is_h前提判断
    skip_not_h_judge -- 是否跳过not_h前提判断
    
    返回:
    (是否通过过滤, 更新后的前提数据缓存)
    """
```

### 5.2 过滤逻辑步骤

```python
filter_judge = True

# 步骤1：检查指令过滤器
if instruct_id not in cache.instruct_index_filter:
    cache.instruct_index_filter[instruct_id] = True
if not cache.instruct_index_filter[instruct_id]:
    filter_judge = False

# 步骤2：H子类指令过滤
if (use_type_filter_flag and 
    handle_premise.handle_now_show_h_instruct(0) and 
    now_type == constant.InstructType.SEX):
    now_sub_type = constant.instruct_sub_type_data[instruct_id]
    if cache.instruct_sex_type_filter[now_sub_type] == 0:
        filter_judge = False

# 步骤3：前提条件判断
if filter_judge:
    premise_judge = True
    if instruct_id in constant.instruct_premise_data:
        for premise in constant.instruct_premise_data[instruct_id]:
            # 特殊跳过逻辑
            if use_type_filter_flag == False and \
               handle_premise.handle_t_npc_active_h(0) and \
               premise == 't_npc_not_active_h':
                continue
            
            # 使用缓存结果
            if premise in now_premise_data:
                if now_premise_data[premise]:
                    continue
                premise_judge = False
                break
            
            # 跳过H/非H判断
            elif skip_h_judge and premise == 'is_h':
                now_premise_data[premise] = 1
            elif skip_not_h_judge and premise == 'not_h':
                now_premise_data[premise] = 1
            else:
                # 实际判断前提
                now_premise_value = handle_premise.handle_premise(premise, 0)
                now_premise_data[premise] = now_premise_value
                if not now_premise_value:
                    premise_judge = False
                    break
    
    if not premise_judge:
        filter_judge = False

# 步骤4：Debug模式强制通过
if cache.debug_mode:
    filter_judge = True

return filter_judge, now_premise_data
```

---

## 6. 在场景主面板中的调用

### 6.1 InScenePanel 中的使用

位于 `Script/UI/Panel/in_scene_panel.py`：

```python
class InScenePanel:
    def draw(self):
        # ... 绘制场景信息 ...
        
        # 指令面板
        instruct_panel = see_instruct_panel.SeeInstructPanel(self.width)
        instruct_panel.draw()
        ask_list.extend(instruct_panel.return_list)
        
        # 等待用户输入
        yrn = flow_handle.askfor_all(ask_list)
        py_cmd.clr_cmd()
```

### 6.2 特殊状态处理

```python
# 临盆、产后、婴儿状态下隐藏特定类型
if (handle_premise.handle_t_parturient_1(0) or 
    handle_premise.handle_t_postpartum_1(0) or 
    handle_premise.handle_t_baby_1(0)):
    cache.instruct_type_filter[4] = False  # 技艺
    cache.instruct_type_filter[5] = False  # 猥亵
    cache.instruct_type_filter[6] = False  # 性爱
```

---

## 7. 绘制基础组件

### 7.1 draw.LeftButton

```python
class LeftButton:
    """
    左对齐按钮
    
    属性:
    text -- 按钮显示文本
    return_text -- 返回值（用于输入匹配）
    width -- 按钮宽度
    normal_style -- 正常状态样式/颜色
    cmd_func -- 点击回调函数
    args -- 回调函数参数
    """
```

### 7.2 draw.CenterButton

```python
class CenterButton:
    """
    居中按钮
    
    用于类型切换按钮等需要居中显示的场景
    """
```

### 7.3 panel.DrawTextListPanel

```python
class DrawTextListPanel:
    """
    文本列表面板
    
    用于将多个绘制元素按行排列显示
    
    方法:
    set(draw_list, width, column_num) -- 设置绘制内容
    draw() -- 执行绘制
    """
```

### 7.4 draw.LineDraw

```python
class LineDraw:
    """
    分隔线绘制
    
    用于绘制各种样式的分隔线
    例如: "-.-", "~..", "-"
    """
```

---

## 8. 颜色系统

### 8.1 指令类型颜色

| 类型 | 颜色名 | 说明 |
|------|--------|------|
| 系统 | standard | 标准色 |
| 日常 | shadow_green | 阴影绿 |
| 娱乐 | light_french_beige | 浅法式米色 |
| 工作 | grullo | 灰褐色 |
| 技艺 | light_steel_blue | 浅钢蓝 |
| 猥亵 | pale_chestnut | 浅栗色 |
| 性爱 | amarath_pink | 苋菜粉 |

### 8.2 H子类型颜色

| 子类型 | 颜色名 |
|--------|--------|
| 基础 | standard |
| 前戏 | light_pink |
| 侍奉 | pastel_magenta |
| 药物 | princess_perfume |
| 道具 | rose_pink |
| 插入 | deep_pink |
| SM | crimson |
| 技艺 | light_steel_blue |

---

## 9. 布局配置

### 9.1 单行指令数量

```python
# 从系统设置读取，默认值+1
SINGLE_LINE_INSTRUCT_NUM = int(cache.all_system_setting.draw_setting[11]) + 1
```

### 9.2 按钮宽度计算

```python
# 类型切换按钮宽度
button_width = int(self.width / (instruct_type_len - 1))

# 指令按钮宽度
instruct_button_width = int(self.width / SINGLE_LINE_INSTRUCT_NUM)
```

---

## 10. 性能优化

### 10.1 前提缓存

```python
# 在遍历指令时复用前提判断结果
now_premise_data = {}
for instruct in all_instructs:
    filter_judge, now_premise_data = judge_single_instruct_filter(
        instruct, now_premise_data, now_type
    )
```

### 10.2 绘制时间记录

```python
start_instruct = time.time()
# ... 绘制逻辑 ...
# 可用于性能分析
```

---

## 11. 扩展说明

### 11.1 添加新类型

1. 在 `InstructType.csv` 添加新类型定义
2. 运行 `buildconfig.py`
3. 过滤器会自动包含新类型

### 11.2 自定义颜色

1. 在 `FontConfig.csv` 中定义新颜色
2. 在类型配置中引用颜色名

### 11.3 修改布局

1. 通过系统设置调整 `draw_setting[11]` 改变单行数量
2. 直接修改 `SINGLE_LINE_INSTRUCT_NUM` 计算逻辑
