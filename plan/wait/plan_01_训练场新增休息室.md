# Plan 01：给训练场新增休息室

- 状态：待实施
- 来源：`todo list.txt` → `# 待处理的小问题` → “给训练场加休息室”
- 预计改动量：约 3 个文件（1 个新增场景 JSON + 2 个地图文件微调）
- 风险等级：低
- 适用代码快照：`master @ b17d1b1ba`（v0.66）

---

## 1. 目标

在罗德岛“训练场”地图（`data/map/训练/`）中新增一个可导航、可进入、可休息的“休息室”场景，使训练场与制造加工、中枢等其他区块一样拥有休息室。

## 2. 现状调查

### 2.1 训练场地图结构

当前 `data/map/训练/` 目录内容：

```text
data/map/训练/
├── 0/Scene.json          入口
├── 走廊/Scene.json
├── 健身区/Scene.json
├── 木桩房/Scene.json
├── 射击房/Scene.json
├── 模拟对战室/Scene.json
├── 更衣室/Scene.json
├── 淋浴/Scene.json
├── 游泳池/Scene.json
├── 男士洗手间/Scene.json
├── 女士洗手间/Scene.json
├── Map                    AA 地图文本（含各场景 <mapbutton>）
└── Map.json               地图名与 PathEdge
```

### 2.2 `Map.json` 当前邻接关系

```json
{
  "MapName": "训练场",
  "PathEdge": {
    "0": { "走廊": 1 },
    "走廊": {
      "0": 1,
      "健身区": 1,
      "木桩房": 1,
      "射击房": 1,
      "模拟对战室": 1,
      "更衣室": 1
    },
    "木桩房": { "走廊": 1 },
    "射击房": { "走廊": 1 },
    "模拟对战室": { "走廊": 1 },
    "更衣室": { "走廊": 1, "淋浴": 1 },
    "健身区": { "走廊": 1, "女士洗手间": 1, "男士洗手间": 1 },
    "淋浴": { "更衣室": 1, "游泳池": 1 },
    "游泳池": { "淋浴": 1 },
    "女士洗手间": { "健身区": 1 },
    "男士洗手间": { "健身区": 1 }
  }
}
```

结论：训练场没有“休息室”节点，也没有任何休息类场景。

### 2.3 可复用的休息室场景模板

项目内已有完全同构的休息室场景，可直接复制字段，例如：

- `data/map/制造加工/休息室/Scene.json`
- `data/map/中枢/休息室/Scene.json`

其 JSON 为：

```json
{
  "SceneName": "休息室",
  "In_Door": "1",
  "Exposed": "0",
  "Have_Furniture": "3",
  "Close_Type": "2",
  "SceneTag": "Rest_Room",
  "Room_Area": "1",
  "Scene_Img": "休息室"
}
```

`Scene_Img` 为“休息室”时，游戏已有现成休息室背景图（制造加工、中枢均在使用）。

### 2.4 地图缓存机制

- `map_config.init_map_data()` 优先读取预处理 pickle：
  - `data/SceneData`
  - `data/MapData`
  - `data/PlaceData`
  - `data/ScenePath`
- 只有当上述缓存文件不存在时，才会重新解析 `data/map/` 原始目录。
- 因此修改地图后必须删除这四个缓存文件（`ScenePath` 是 JSON，其余是 pickle），再启动游戏或运行 `init_data.py` 重建。

## 3. 实施步骤

### 3.1 新建休息室场景

新建文件：

```text
data/map/训练/休息室/Scene.json
```

内容参照制造加工休息室：

```json
{
  "SceneName": "休息室",
  "In_Door": "1",
  "Exposed": "0",
  "Have_Furniture": "3",
  "Close_Type": "2",
  "SceneTag": "Rest_Room",
  "Room_Area": "1",
  "Scene_Img": "休息室"
}
```

字段说明（与现有地图一致，不要改动字段名）：

| 字段 | 值 | 含义 |
| --- | --- | --- |
| `SceneName` | 休息室 | 场景显示名 |
| `In_Door` | 1 | 室内 |
| `Exposed` | 0 | 非露天 |
| `Have_Furniture` | 3 | 家具数量（提供桌椅/休息条件） |
| `Close_Type` | 2 | 可关门类型，与现有休息室一致 |
| `SceneTag` | Rest_Room | 休息室标签，用于前提/指令过滤 |
| `Room_Area` | 1 | 房间面积 |
| `Scene_Img` | 休息室 | 使用现成休息室背景 |

### 3.2 修改 `data/map/训练/Map.json`

在 `PathEdge` 中增加休息室节点并挂到走廊：

```json
"走廊": {
  "0": 1,
  "健身区": 1,
  "木桩房": 1,
  "射击房": 1,
  "模拟对战室": 1,
  "更衣室": 1,
  "休息室": 1
},
"休息室": { "走廊": 1 }
```

完整改动只有两处：`走廊` 对象新增一个键，根对象新增 `"休息室"` 键。

### 3.3 修改 `data/map/训练/Map`（AA 地图文本）

当前第 5 行（0-based 第 5 行，文件行号 6）是横向底边走廊行：

```text
           <mapbutton>健身区</mapbutton>                            <mapbutton>走廊</mapbutton>                          <mapbutton>0</mapbutton>
```

推荐的最小改动：在“走廊”按钮与“0”按钮之间插入休息室按钮：

```text
           <mapbutton>健身区</mapbutton>                            <mapbutton>走廊</mapbutton>          <mapbutton>休息室</mapbutton>          <mapbutton>0</mapbutton>
```

要点：

1. 只新增 `<mapbutton>休息室</mapbutton>` 标签，不改变其他按钮文字。
2. 插入后适当压缩该行原有空格，避免该行明显长于相邻行；本项目 AA 地图各行长度本身并不严格相等，允许少量差异。
3. 修改前备份原文件；修改后肉眼检查该行仍与上下框线对齐。
4. 如果后续想要更精致的布局，可在“更衣室/淋浴”右侧房间群旁扩展一个房间格，但当前 Plan 不采用该方案，以控制改动量。

## 4. 构建与缓存重建

```bash
# 1. 删除旧地图缓存（必须）
rm -f data/SceneData data/MapData data/PlaceData data/ScenePath

# 2. 任选一种方式重建：
python init_data.py        # 只重建地图缓存，快
# 或直接运行游戏：python game.py（启动时 map_config 也会重建）

# 3. 如需要同步 PO 模板（场景名“休息室”不是新词条，理论上无需，但可执行）
python buildconfig.py
```

注意：不要只删除缓存后立即读取旧存档进行验证，旧存档中的角色位置如果指向训练场其他场景仍应正常；休息室只是新场景节点，不影响存档结构。

## 5. 验证清单

- [ ] 删除缓存后启动游戏，无地图加载报错。
- [ ] 训练场大地图面板中出现“休息室”按钮。
- [ ] 点击“休息室”可进入；从休息室可返回走廊。
- [ ] 休息室场景图片正常显示“休息室”背景。
- [ ] 在休息室中可用现有休息/睡觉等指令（依赖 `Rest_Room` / 家具前提的指令显示正常）。
- [ ] NPC AI 可把休息室作为候选休息地点（场景标签 `Rest_Room` 会进入 `constant.place_data`）。
- [ ] 旧存档读取不报错，已有训练场导航路径不变。

## 6. 风险与回滚

- **主要风险**：手改 AA 地图文本导致框线错位。影响仅为视觉，不影响寻路（寻路由 `Map.json` 的 `PathEdge` 决定）。
- **缓存陷阱**：忘记删除 4 个地图缓存时，修改不会生效。
- **回滚**：删除新增的 `data/map/训练/休息室/` 目录，还原 `Map.json` 与 `Map`，再次删除地图缓存并重建即可。

## 7. 改动文件清单

| 文件 | 类型 | 改动 |
| --- | --- | --- |
| `data/map/训练/休息室/Scene.json` | 新增 | 休息室场景定义 |
| `data/map/训练/Map.json` | 修改 | PathEdge 增加休息室节点 |
| `data/map/训练/Map` | 修改 | 底边走廊行增加休息室 mapbutton |
| `data/SceneData`, `data/MapData`, `data/PlaceData`, `data/ScenePath` | 重建 | 删除后由加载逻辑重新生成 |
