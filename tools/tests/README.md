# 无头回归测试

不启动 Tk / Web 界面、在一个 Python 进程内初始化游戏后直接调用游戏代码做断言的回归测试。CI（`.github/workflows/python-app.yml` 的 `Regression Tests` 一步）在每次推送和每个 PR 上跑全部套件。

## 怎么跑

```bash
.conda\python.exe tools/tests/run_all.py                    # 全部套件
.conda\python.exe tools/tests/run_all.py core               # 只跑「套件/文件名」里含 core 的
.conda\python.exe tools/tests/run_all.py core/test_medical  # 只跑一个文件
.conda\python.exe -u tools/tests/core/test_medical.py       # 直接单跑（进程末尾会 os._exit）
```

- **必须用 `.conda\python.exe`**，裸 `python` 是商店空壳。CI 里没有 `.conda`，`run_all.py` 会退回当前解释器。
- 每个测试文件各起一个进程：游戏的全局缓存只能初始化一次，同进程串跑会互相污染。单文件超时 240 秒。
- 日志写在 `%TEMP%/erArk_tests/<套件>/<文件名>.log`；`run_all.py` 只带出含 `[FAIL]` / `Error` / `Traceback` 的行，完整回溯看日志。CI 失败时 `Show Test Logs` 一步会把日志末尾打出来。
- 有失败时退出码为 1。汇总行里的 `PASS= / FAIL=` 来自各文件末尾 `finish()` 打印的同名行。
- 改了 CSV 后先跑 `buildconfig.py` 再跑测试（新增口上还要先删 `data/Character_Talk.json`），否则断言读到的是旧生成物；构建会清空 PO，跑完按需 `git checkout -- data/po/`（先确认 PO 里没有你自己未提交的改动）。

## 目录结构

| 路径 | 作用 |
| --- | --- |
| `run_all.py` | 自动发现套件并逐个子进程运行、汇总。套件 = 本目录下名字不以 `_` / `.` 开头、且含 `test_*.py` 的子目录，新增套件不用改 CI |
| `headless_base.py` | 各套件共用的引导：初始化链（照 `game.py` 的顺序）、两条全局前置（系统设置、设施等级与书库）、屏蔽全部绘制类并把文本收进 `drawn_text`、`askfor_all` 默认返回第一个选项、`check / known_issue / section / finish`、`make_character` 角色 fixture、`scene_str / move_to / set_time / remove_character`、玩家 fixture `pl`、可点击按钮与脚本化选择（`enable_clickable_buttons / run_panel`）、未捕获异常时立即退出 |
| `<套件>/_bootstrap.py` | 套件的引导：把本目录加进 `sys.path` 后 `from headless_base import *`，再补本套件专属的导入与工具 |
| `core/` | 基础系统套件，见下表 |
| `education/` | 生长养成系统套件，见 `education/README.md` |

## core：基础系统

| 文件 | 覆盖 |
| --- | --- |
| `test_config_integrity.py` | 静态的 id 解析检查（不执行任何前提 / 结算）：三张注册表可调用；Premise 常量都有处理函数且与编辑器前提表一一对应（标了弃用的除外）；行为 → 结算效果、二段行为 → 二段结算都已注册、CVE 格式完整；AI 目标 → 状态机、前提、目标类型都能解析；指令 → 前提（CSV 的 `premise_set` 写错会被静默丢弃）。只查运行时缺失时**静默跳过**或只打印报错的那类引用 |
| `test_premise_smoke.py` | 全部已注册前提（养成系统除外）在日常 / H 中 / 深夜睡眠三种世界、玩家与 NPC 的四种主体-对象组合、一周全时段、全部场景下都可求值且返回合法权重；注册表与 `@add_premise` 装饰器一一对应、没有重复注册；核心前提语义抽查（权重、主体、时段、地点、好感阈值、H 状态等）。fixture 全部是成年角色 |
| `test_settle_smoke.py` | 按新开局流程建的成年角色世界里，全部一段 / 二段结算器与效果串里的综合数值结算（CVE）按数据里可达的方向逐个执行不抛异常（每个用例前后快照还原、全程拦截写文件）；`handle_settle_behavior` 端到端跑常用行为；体力 / 气力 / 好感 / 信赖 / 状态通用结算的语义抽查。养成系统的结算器由 `education` 套件覆盖，不在此扫 |
| `test_map_time.py` | 地图缓存与 `data/map` 源文件一致；场景 / 地图归属、通行表双向与连通、标签索引；地图内最短路与全场景寻路表（逐步相邻、每步耗时、总耗时等于最短距离）；`character_move` 的门锁 / 私密 / 钥匙、`judge_scene_accessible`、场景移动记账与移动状态机；季月时钟推进、时停结束后的时间还原（含跨季月）、日期工具、工作日与时段判定 |
| `test_medical.py` | 医疗系统：检查目录覆盖全部并发症、菜单同一帧按钮返回文本不冲突；病人生成（并发症数量、追踪数据、不选女性限定部位）；执行检查的阳性 / 需再检 / 阴性判定与次数、记录上限；接诊策略、中止复原、结算发药与收入；诊疗面板检查菜单（#327：确诊后其后的系统不再消失）、提示高亮与灰显、已检查项；按钮驱动的完整诊疗流程（含二次确认与提前结束） |
| `test_resource_exchange.py` | 资源交易所：特产只在产地按常规价买入、异地按 1.5 倍卖出，大地图移动后异地特产可手动卖出（#326），自动交易同样受限，交易员加成抬高特产卖价；买卖的资金 / 库存不变式与各种拒绝情形 |
| `test_food_shop.py` | 食堂 / 餐馆 / 地摊的识别与购买（博士免费）；购买期间商店因跨日或补货刷新后继续购买、地摊与餐馆被买光的提示（含错字）、食堂补货不动餐馆；食物背包清理菜谱已不存在的食物；各商店的进货规则 |
| `test_day_settle.py` | 新开局基地上的新一天结算全链与每日重置、乳制品与精液的仓库上限、浮点库存的流水线与自动卖出、睡眠结算（宝珠转换、苦痛 / 反发、助理问候）与自动存档钩子、持续一天以上的长行为结算 |
| `test_save.py` | 存读档往返（存档目录重定向到临时目录，并拦截一切临时目录以外的写入）与 save_info；旧存档读档时的跨版本补全（缺字段、类型不符、新资源 / 设施 / 设置、被删的场景）；温室生产线与阿玛雅编号两处旧档修复；旧档缺国家数据；读档归一化（路径分隔符、履历平铺字段、无壳卵生孕程） |

## 写新测试

1. 放进合适的套件目录（没有合适的就新建一个目录，带一个照 `core/_bootstrap.py` 写的 `_bootstrap.py`），文件名 `test_<主题>.py`。
2. 第 2 行是一行模块说明，概括覆盖范围；开头 `from _bootstrap import *`，结尾 `finish()`。
3. 用 `section()` 分节、`check(名称, 条件, 失败时附带的实际值)` 断言，名称写中文。对「注册表里每一项都……」这类扫一遍的检查，合成一条断言、把不合格的项放进第三个参数，不要每项一条。
4. 断言写**设计意图**（设计文档、`update.log`、修复提交、代码注释），不写「现在代码返回什么」。锁定某个 BUG 修复时，确认这条断言在修复前的代码上会失败。
5. 遵守 `.github/skills/headless-game-test/SKILL.md` 的铁律：不调 `save_handle.establish_save()`、不进真实主循环（`init_character_behavior`、`handle_instruct.*`、`chara_handle_instruct_common_settle`、`update.game_update_flow`）——代码会走到它们时在调用方模块上打桩；fixture 字段与置零函数照抄该 skill 的对照表。例外只有两处：`core/test_save.py` 的存读档往返（存档目录与 save_info 都重定向到临时目录，并拦截临时目录以外的一切写入，要测存档就照它的做法）；`core/test_map_time.py` 的 `run_time_stop_flow`（让真实的 `update.game_update_flow` 只跑时停分支：逐角色结算换成带调用上限的桩，成就结算与输入框聚焦换成空函数，时停分支在玩家阶段后即退出）。
6. 必须能在 CI 上跑：Windows、没有 `save/` 与 `image/` 目录、数据刚由 `buildconfig.py` 构建。依赖真实存档的段落要在没有存档时跳过（写法见 `education/test_behavior_loop.py` 开头）。
7. 驱动面板：默认的 `askfor_all` 桩只返回第一个选项、**不执行按钮回调**，靠按钮回调改状态或退出循环的面板会死循环。先调 `enable_clickable_buttons()`（按钮绘制桩登记 `返回值 → (回调, 参数)`，脚本化的 `askfor_all` 选中后像真实的 `_cmd_deal` 一样执行回调），再用 `run_panel(入口函数, [返回值或谓词, ...])` 跑，之后看 `ask_log`（每次询问的选项与选中项）、`missed`（没找到的选择）与 `drawn_text`；用法见 `core/test_food_shop.py`、`core/test_resource_exchange.py`。还要断言按钮样式等更多信息时，自己记录按钮（见 `core/test_medical.py` 的 `ScriptedChoice`）。
8. 确认是 BUG、但修法要维护者拍板时，用 `known_issue(名称, 修好后应成立的条件, 说明)` 代替 `check`：问题仍在时记为 `[KNOWN]`、不算失败，`run_all.py` 汇总里会列出；问题消失后它按通过计并提示改回 `check`。
9. 注释、函数说明一律中文，函数写明参数与返回值（格式照 `headless_base.py`），行宽 200。
