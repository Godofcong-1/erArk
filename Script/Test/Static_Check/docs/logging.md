# 日志与快照

## 文件

三个文件都相对于游戏进程工作目录，与 `error.log` 的约定一致：

- `static_check_error.log`：失败与修复记录。
- `static_check_error.log.old`：最近一次轮转前的日志。
- `static_check_seen.json`：已详写过的检查编号集合（跨进程去重用）。

失败与修复记录写入前，日志首行的版本头必须等于当前游戏版本。版本变化或首行损坏时，当前日志改名为 `.old`，再新建日志并写入当前版本头；改名失败时直接覆盖原文件。检查器自身异常的记录不做版本检查，直接追加。任何异常不向游戏传播。

失败与修复记录写入前检查日志体积，达到 50MB 时本进程只写一次说明行，之后跳过这两类写入；自身异常记录不受此限。

## 条目格式

失败和修复条目共用头部：

```text
================================================================================
[静态检查] 现实时间: <ISO> | 游戏时间: <game_time> | 周目: <game_round> | 已注册检查项: <实际数量>
最近输入(input_cache 末尾10条): ...
最近行为指令(pl_pre_behavior_instruce, id+名称): ...
```

头部写的是实际注册数量，注册表残缺时从这一行就能看出来。只有调用方显式传入非空 `context` 时才追加“上下文包”一行；门面（`__init__.py`）不传 `context`，因此日志里不会出现这一行。

## 检查级去重

同一 `check_id` 每个游戏版本只详写首个失败实例，已详写的编号集合存在 `static_check_seen.json` 里。因此 `run_turn_check()` 返回 `True` 至多每版本每检查一次，重复失败既不写日志也不重复提示玩家。`static_check_seen.json` 写入失败或丢失时，下一个进程会重新详写。去重只看 `check_id`，不看失败消息，因为消息里的数值随游玩变化，拿它去重会让去重失效。修复记录不参与去重，每次实际修复都留痕。

`check_log` 有三项相互关联的进程运行态：`_seen_check_ids`、`_log_cap_notice_written`，以及 `LOG_PATH`/`OLD_LOG_PATH`/`SEEN_STATE_PATH` 三个路径常量。在同一进程内多次验证日志行为时，必须重置前两个变量，并成组改向三个路径；只改其中一个路径，验证会被旧状态污染。门面的 `LOG_PATH` 是按值再导出的独立名字，改向 `check_log.LOG_PATH` 后门面的值不会跟着变。

## 状态快照

`snapshot.build_snapshot(cache, ids)` 使用调用方传入的 cache。传入涉事角色 id 时，`character_data` 只转储涉事角色与玩家，最多 30 人，其余涉事角色只记 id；`scene_data` 只保留有角色的场景。

排除静态配置与渲染缓存字段：`map_data`、`npc_tem_data`、`random_npc_list`、`recipe_data`、天文表、`wframe_mouse`、`cmd_data`、流水字段（每日指令文本、已触发事件 id），以及 `web_`、`current_`、`text_` 前缀字段。`rhodes_island.medical_patients_today` 用占位文本替代。

转换遇到循环引用时写占位文本，达到 15 层或对象不可序列化时用 `repr` 兜底。
