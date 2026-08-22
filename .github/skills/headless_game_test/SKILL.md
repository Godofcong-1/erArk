---
name: headless-game-test
description: 在不启动图形界面的情况下无头运行 erArk：加载游戏配置与指定存档、复刻某条指令的执行、带护栏运行角色行为循环并逐轮内窥。用于复现与定位死循环/卡死、验证结算与AI逻辑、修复前后的回归测试。当需要"复现某存档下的BUG"、"模拟执行某指令"、"验证行为循环收敛"、"排查NPC卡死"时使用。
---

# Skill Instructions

你是 erArk 的无头测试助手。本 skill 归纳了一套经实战验证的方法：不启动 Tk/Web 界面，在一个 Python 进程内完整初始化游戏、读取存档、复刻玩家指令、带护栏地运行行为循环，并对任意函数插桩观察每一轮的中间状态。曾用该方法定位"烂醉睡眠者被吵醒后死循环"（每轮 AI 重选睡觉 ↔ 睡眠打断判定互相拉扯的活锁）。

配套模板：本目录下的 `harness_template.py`，按其中 `====` 分段标记修改后即可运行。

## 铁律（每条都是踩过的坑）

1. **必须用 `./.conda/python.exe`**，裸 `python` 是 Windows 商店空壳别名（exit 49、无任何输出）。
2. **外层必须加 `timeout N`**（bash 的 timeout 命令）。游戏导入链（Flask/SocketIO 等）会启动非守护线程，**测试跑完后进程也不会自行退出**——`EXIT=124` 且结果已全部打印 = 正常结束，不是测试失败。也可在脚本末尾 `os._exit(0)` 主动退出。
3. **加 `-u` 取消缓冲**，且脚本开头 `sys.stdout.reconfigure(encoding='utf-8', errors='replace')`（Windows 控制台是 GBK，中文会乱码/报错）。不要 `| tail` 管道观察长时间运行的进程——tail 会攒住全部输出，进程卡死时你什么都看不到。
4. **绝不调用会进入真实主循环的函数**：`handle_instruct.handle_xxx()`、`chara_handle_instruct_common_settle()`、`update.game_update_flow()` 最终都会调 `init_character_behavior()`。如果要排查的 BUG 正是死循环，harness 自己就会卡死。必须用"复刻指令赋值 + 手动推进时间 + 带护栏的自建循环"代替（见下文）。
5. **只读纪律**：读档只用 `save_handle.input_load_save(id)`（纯读入内存）；绝不调用 `establish_save()`；不 inline 调用 `init_character_behavior()`（其结尾的成就结算可能写文件）。所有修复先用 monkeypatch 在内存中模拟验证，确认收敛后再改源码。
6. 脚本用 heredoc 从仓库根目录运行（`./.conda/python.exe -u - <<'EOF'`），stdin 脚本的 sys.path[0] 为空串=当前目录，可直接 `import auto_build_config`；若写成文件放在仓库外（如 scratchpad），需先 `sys.path.insert(0, r"c:\code\erArk")`。

## 第一步：初始化链（照抄 game.py 顺序，约 3 秒）

```python
import auto_build_config                       # 增量构建数据（数据已构建时约0.4s）
from Script.Config import normal_config
from Script.Core import game_type, cache_control
cache_control.cache = game_type.Cache()        # 必须在 game_config.init() 之前
normal_config.init_normal_config()
from Script.Config import game_config, character_config
game_config.init()
character_config.init_character_tem_data()
from Script.Config import map_config
map_config.init_map_data()
from Script.Design import character_handle, game_time, character_behavior, instuct_judege, map_handle
import Script.Settle, Script.StateMachine      # 注册全部结算器与状态机，缺了会 KeyError
from Script.Core import constant, save_handle, flow_handle
from Script.UI.Moudle import draw
character_handle.init_character_tem()
game_time.init_time()
```

顺序不能乱：`cache` 先建、`normal_config` 先于 `game_config`、`Script.Settle`/`Script.StateMachine` 必须 import（装饰器注册）。Mod 系统可跳过（测试不需要）。

## 第二步：屏蔽 UI（防止任何绘制/等待阻塞）

```python
for cls_name in dir(draw):
    cls = getattr(draw, cls_name)
    if isinstance(cls, type) and hasattr(cls, 'draw'):
        try: cls.draw = lambda self, *a, **k: None
        except Exception: pass
flow_handle.askfor_all = lambda *a, **k: ""
flow_handle.askfor_wait = lambda *a, **k: None
```

需要断言"某段文本是否被绘制"（如吵醒提示）时，用记录型 stub 替换对应类：

```python
messages = []
def record_draw(self, *a, **k):
    if getattr(self, 'text', None) and '吵醒' in str(self.text):
        messages.append(str(self.text).strip())
draw.WaitDraw.draw = record_draw
```

## 第三步：读档与状态体检

```python
save_handle.input_load_save("5")     # 存档目录 save/5/，纯读入内存
cache = cache_control.cache
pl = cache.character_data[0]
```

- 按名字找角色：遍历 `cache.character_data.items()` 比对 `cd.name`。
- 体检清单（排查行为类 BUG 时先打印这些）：`behavior.behavior_id / duration / start_time`、`state`、`position`、`target_character_id`、`tired_point`、`sleep_point`、`hit_point/max`、`mana_point/max`、`hunger_point`、`sp_flag` 全量（`sleep / rest / tired / sleep_h_awake / unconscious_h / imprisonment / is_follow / is_h / hidden_sex_mode`）、醉酒等级 `drunk_sex_common.get_drunk_level(cid)`、安眠药 `h_state.body_item[9][1]`、`work.work_type`、`entertainment.entertainment_type`。
- 需要移动角色到某场景：`map_handle.character_move_scene(旧位置, 新位置, cid)`。

## 第四步：复刻指令（不进真实循环）

`chara_handle_instruct_common_settle()` 对玩家指令做的核心三件事，手动复刻：

```python
instuct_judege.init_character_behavior_start_time(0, cache.game_time)
pl.state = constant.CharacterStatus.STATUS_XXX
pl.behavior.behavior_id = constant.Behavior.XXX
dur = max(game_config.config_behavior[constant.Behavior.XXX].duration, 1)  # 查表时长
pl.behavior.duration = dur
game_time.sub_time_now(dur)          # 推进游戏时间到行动结束点（真实流程也是先推时间再跑循环）
```

指令名 → 行为常量的查找路径：`Script/System/Instruct_System/handle_instruct.py`（搜指令中文名）→ `constant.Behavior.*`；时长在 `data/csv/Behavior_Data.csv`。

## 第五步：带护栏的行为循环（核心）

复刻 `init_character_behavior()` 的主干，但每个 while 都加轮数上限，超限即判死循环并报告卡住的角色：

```python
cache.over_behavior_character = set()
g = 0
while 0 not in cache.over_behavior_character:          # 玩家阶段
    g += 1
    if g > 30: print("!! 玩家阶段卡死"); break
    pl_start = pl.behavior.start_time
    character_behavior.character_behavior(0, cache.game_time, pl_start)

id_list = cache.npc_id_got.copy(); id_list.discard(0)  # NPC 阶段
passes = 0
while len(cache.over_behavior_character) <= len(id_list):
    passes += 1
    if passes > 25:
        print("!! NPC阶段死循环, 未完成:",
              [(c, cache.character_data[c].name) for c in id_list if c not in cache.over_behavior_character][:8])
        break
    for cid in id_list:
        if cid in cache.over_behavior_character: continue
        character_behavior.character_behavior(cid, cache.game_time, pl_start)
```

判读标准：正常情况玩家阶段 1 轮、NPC 阶段个位数轮全部收敛；超过上限即为活锁，**"未完成"名单就是卡死角色清单**。注意：提前 break 时名单里也会混入还没轮到处理的正常角色，缩小范围要看逐轮内窥（下一步）。

## 第六步：逐轮内窥（定位循环形态）

对可疑角色，在每轮 `character_behavior()` 前后打印行为四元组（behavior_id / duration / start_time / state）。若"前后打印完全相同且永不完成"，说明**轮内发生了赋予→掐死的隐形循环**，需要包装中间函数看到轮内状态：

```python
orig_find = handle_npc_ai.find_character_target
def wrap_find(cid, now_time):
    orig_find(cid, now_time)
    if cid in WATCH:
        cd = cache.character_data[cid]
        print(f"    [find后] cid={cid} bhv={cd.behavior.behavior_id} dur={cd.behavior.duration} state={cd.state}")
handle_npc_ai.find_character_target = wrap_find
character_behavior.handle_npc_ai.find_character_target = wrap_find   # 双保险：两个模块引用都替换

orig_int = handle_npc_ai.judge_interrupt_character_behavior
def wrap_int(cid):
    pre = (cache.character_data[cid].behavior.behavior_id, cache.character_data[cid].behavior.duration)
    r = orig_int(cid)
    if cid in WATCH:
        cd = cache.character_data[cid]
        print(f"    [中断判定] cid={cid} 前={pre} 返回={r} 后=({cd.behavior.behavior_id},{cd.behavior.duration})")
    return r
handle_npc_ai.judge_interrupt_character_behavior = wrap_int
character_behavior.handle_npc_ai.judge_interrupt_character_behavior = wrap_int
```

同法可包装 `judge_character_status`、`realtime_settle.character_aotu_change_value` 等任意环节。

## 第七步：控制随机分支

概率判定（如吵醒 `weak_rate >= random.randint(1,100)`）会让复现不稳定。强制命中：

```python
random.seed(1)
random.randint = lambda a, b: a    # 所有 randint 返回下界 → 概率判定必中
```

注意这会影响全部随机（AI 选择、数值浮动）；只需固定可复现时用 `random.seed` 即可，需要"必中/必不中"某判定时才整体替换 `randint`。

## 第八步：内存模拟修复 → 确认收敛 → 再改源码

改源码前，先把候选修复以 monkeypatch 形式打在内存里重跑护栏循环，收敛了才动手：

```python
_orig = handle_npc_ai.judge_interrupt_character_behavior
def patched(cid):
    cd = cache.character_data[cid]
    if <候选修复条件>: return 0
    return _orig(cid)
handle_npc_ai.judge_interrupt_character_behavior = patched
character_behavior.handle_npc_ai.judge_interrupt_character_behavior = patched
# 重跑第五步，断言收敛轮数与最终状态
```

改完源码后**去掉补丁重跑同一 harness** 做最终验证，再补一组回归（如：修复烂醉豁免后，验证非烂醉浅睡者仍会被吵醒且收敛）。

## 死循环排查心法

行为循环卡死 = 某角色永远进不了 `cache.over_behavior_character`。`judge_character_status_time_over()` 只有两条 return 0 路径：

- **A 路径**（`add_time <= 0`）：行为时长为 0/负 → 重置为空闲、duration=1、start=now、返回 0；
- **B 路径**（`time_judge == 1`，结束时间早于当前时间）：重置行为、start_time=end_time、返回 0。

单次 return 0 是正常的（给 AI 一轮重选机会）；**死循环 = 每一轮重新选出的行为的"结束时间 ≤ 当前时间"且前提永不变化**。已知的三类成因：

1. **同轮掐死类**：`find_character_target` 赋予行为后，同轮的 `judge_interrupt_character_behavior`（休息/睡眠/工作淋浴三个分支）或 `settle_sleep` 自然醒用 `end_now=2` 立即终止它，而选择前提（如烂醉 `drunk_level_3`、安眠药、特殊 flag）不受终止影响 → 每轮重复。排查点：中断分支的豁免条件是否与所有可重选该行为的目标前提互斥（目标清单查 `data/target/default/target.csv`，按状态机 id 搜 `,44,` 这类）。
2. **无效时长类**：状态机算出 duration ≤ 0（如"睡到玩家醒来时间"的减法）且 `add_time=0` 的结算会跳过全部 flag 效果（`if not add_time: return` 模式），前提永不失效。
3. **start_time 回拨类**：B 路径或某处把 start_time 设回过去，且每轮被重新回拨。

对应的结构性护栏（已在代码中，排查时先确认它们还在）：`judge_interrupt_character_behavior` 开头的"本轮刚赋予的行为不打断"；`find_character_target` 状态机执行后的 duration≥1 钳制；`judge_character_status_time_over` 的 `add_time <= 0` 拦截。

## 快速查表

| 要找什么 | 位置 |
| --- | --- |
| 主循环/时间结算 | `Script/Design/character_behavior.py`（`init_character_behavior`、`judge_character_status_time_over`） |
| NPC AI 选择/打断 | `Script/Design/handle_npc_ai.py`（`find_character_target`、`judge_interrupt_character_behavior`） |
| 实时数值/睡眠/吵醒 | `Script/Settle/realtime_settle.py`（`settle_sleep`、`settle_sleep_h`） |
| AI 目标配置 | `data/target/default/target.csv`（格式：id,状态机id,前提管道,类型,注释） |
| 状态机 id ↔ 名称 | `Script/Core/constant/StateMachine.py`；实现在 `Script/StateMachine/default.py` |
| 行为时长/标签 | `data/csv/Behavior_Data.csv`；行为→结算效果 `data/csv/Behavior_Effect.csv` |
| 前提函数 | `Script/Design/handle_premise/`（按主题分模块） |
| 结算效果实现 | `Script/Settle/default.py`（`@add_settle_behavior_effect(效果id)`） |
| 读档 API | `Script/Core/save_handle.py`（`input_load_save(save_id)`） |

## 运行方式

```bash
timeout 240 ./.conda/python.exe -u - <<'EOF' 2>&1 | tail -40
# （harness 内容，见 harness_template.py）
EOF
echo "EXIT=$?"
```

短时诊断可以接 `| tail -N` 截取结果；怀疑会卡死时不要接管道，直接看实时输出。`EXIT=124` 但结果已打印完整 = 正常（残留线程被 timeout 回收）。
