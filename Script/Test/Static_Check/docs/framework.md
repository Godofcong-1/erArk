# 框架：结构、接口、挂钩与验收

## 包结构

```text
Script/Test/Static_Check/
  ├─ __init__.py ─────────── 唯一公开门面；就绪守卫、总兜底
  ├─ check_registry.py ───── CheckFailure、检查注册表、register_check / make_failure
  ├─ checks/__init__.py ──── 逐模块 try/except 导入 checks/check_*.py
  ├─ checks/check_*.py ───── 只读检查，按领域分模块
  ├─ check_log.py ────────── 日志轮转、检查级去重、落盘
  ├─ snapshot.py ─────────── cache → JSON 安全快照
  └─ repair.py ───────────── 修复规则与执行器
```

`checks/__init__.py` 对每个检查模块单独 `try/except` 导入：一个模块导入失败不影响其余模块注册。这些 import 写成显式的静态 import，PyInstaller 才能收集到这些模块。

分层判据是输出给谁看：面向玩家的提示由游戏侧绘制，面向开发者的日志由检查包写盘。检查包不导入游戏 UI 层，在包目录执行 `rg "Script\.UI" --glob "*.py" .` 应为零命中。

状态语义按层区分：检查层只读，同一状态可重复计算；日志层刻意保留跨回合、跨进程的去重记忆；修复层会写 cache。

取 cache 的方式按层不同：检查函数在函数体内取全局 `cache_control.cache`（见 [writing-checks.md](writing-checks.md)）；`check_log.py`、`snapshot.py`、`repair.py` 不读全局 cache，一律由调用方显式传入。全局读取只出现在门面的两个入口。

## 公开接口

```python
__all__ = ["run_turn_check", "run_load_repair", "run_all_checks", "LOG_PATH"]
```

- `run_turn_check() -> bool`：由调用方在确认开关打开后调用。cache 未就绪时返回 `False`；否则运行全部检查，并记录本版本尚未记录的失败。返回值只表示“本轮是否追加了失败记录”，不表示“是否发现失败”。
- `run_load_repair() -> List[dict]`：由调用方在确认开关打开后调用。返回全部实际修复记录；修复日志写入失败时返回空列表，已做的修改保留。游戏侧可忽略，验证脚本据此断言。
- `run_all_checks() -> List[CheckFailure]`：只运行全部检查并返回失败列表，不写日志。单条检查抛异常时转成 `CheckFailure(check_id, "检查异常(<检查名>)", traceback, [])`，其余检查继续。
- `LOG_PATH`：从 `check_log` 再导出，供游戏侧警告文案引用。

`check_log.write_error_log`、`snapshot.build_snapshot`、`repair.apply_all_repairs` 等是内部接口。玩家提示与开关判断由游戏侧完成，检查包不负责。

## 游戏挂钩与开关

总开关是系统设置“基础”类的 cid 14“是否开启游戏状态自检”，默认关闭。三处挂钩形式相同：先读开关，开关打开时才在 `if` 内部导入本包并调用接口；开关关闭时本包不会被导入。

```python
if cache.all_system_setting.base_setting.get(14, 0):
    from Script.Test import Static_Check as static_check_system
    ...
```

读开关必须用 `.get` 带默认值 0，不能用裸下标。旧存档的设置补齐只在键数量变化时逐键补，存在键数相同而键集合不同的存档，对这类存档裸下标可能抛 `KeyError`。

- Tk：`Script/UI/Panel/in_scene_panel.py` 主场景 `askfor_all(ask_list)` 之前调用 `run_turn_check()`；返回 `True` 时用 `io_init.era_print(..., "warning")` 提示玩家提交日志。
- Web：`Script/UI/Panel/in_scene_panel_web.py` 取得 `ask_list` 之后、`askfor_all` 之前，同样调用与提示。
- 读档：`Script/Core/save_handle.py` 的 `input_load_save` 末尾，存档已写入 cache 之后调用 `run_load_repair()`。

回合检查在每次主场景面板准备等待输入前执行，包括纯 UI 重绘造成的重复迭代；检查级去重保证日志和提示不随之增长。完整迁移后的 354 角色真实存档上，一次 `run_all_checks()` 约 160ms；60 角色约 20ms。若检查集增长，应把共享配置查表移到角色循环外，而不是降低挂钩频率。

检查与修复同开同关。门面在两个入口各做三道就绪守卫：cache 未初始化、角色表为空、玩家（id 0）不在角色表里，任一条成立就直接跳过。

## 异常边界

只有三层，各负责一件事：

1. `run_all_checks()` 逐检查隔离，把单条检查异常转成失败记录。
2. `run_turn_check()` 与 `run_load_repair()` 各有一个入口总兜底，覆盖就绪守卫、惰性导入和内部调用。
3. `check_log.write_self_error_log(exc)` 是日志终点，自身在任何情况下都不抛出。

修复执行器只做逐修复隔离，不重复总兜底；日志调用点不套第二层 `try/except`。游戏侧调用点不需要 `try/except`。

## 验收标准

1. 先完成 `normal_config.init_normal_config()` 与 `game_config.init()` 再导入门面，注册表为 288 条、修复表为 11 条、检查异常为 0。裸导入（跳过初始化）时部分检查模块会因配置缺失导入失败，不能用裸导入的注册数代替验收。
2. 用完整迁移的真实存档复跑，跑之前先调 `map_config.init_map_data()`，否则迁移会把所有人挪到 0/0 并产生大量误报。四项判据：既有检查的失败集合与修复数量不变；每条新出现的命中逐条对照写这份状态的代码来判定；注册了修复的检查在修复后全部通过；检查前后 cache 的 pickle 哈希一致。
3. 日志格式固定项不变：头部写实际注册数、不输出空 context 行、版本轮转、检查级去重、50MB 上限。
4. 开关关闭时，三处挂钩零调用、零写入，本包未被导入。
5. `rg "Script\.UI" --glob "*.py" .` 零命中；框架层读取 `cache_control.cache` 只出现在门面的两个入口。
