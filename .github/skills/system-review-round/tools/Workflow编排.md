# Workflow 编排

两个 saved workflow 放在 `.claude/workflows/`（入库），注册名取脚本里的 `meta.name`。新建或改过脚本后要 `/reload-skills` 才能按名字调；也可以一直用 `scriptPath` 调，效果相同。

## 何时用

- P0 建档完成后调 `system-review-find`（P1~P3）
- 停止点 1 用户拍板、主代理改完共用文件后调 `system-review-implement`（P5）
- 不适合：用户在本次对话里要求不用子代理（改为主代理 inline）；只有一两条已知问题要修（直接改更快）

## system-review-find

### args

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `system` | 是 | 系统名，如「生长养成系统」 |
| `round` / `plan_no` | 是 | 本轮轮次号与 Plan 编号（数字） |
| `snapshot` | 否 | `git log -1 --format=%h` |
| `modules` | 是 | 模块目录或文件（非空数组） |
| `hooks` | 否 | 外部挂接点，写到「文件 + 编号 / 函数」粒度 |
| `data` | 否 | 数据文件与目录（CSV、口上、事件） |
| `docs` | 否 | 说明文档 |
| `tests` | 否 | 回归套件目录；复现代理用它的 `_bootstrap.py`，没有就按 headless-game-test 自建 |
| `known` | 否 | `{decided, cleared, out_of_scope, uncovered}`，四个字符串数组，见 P0 |
| `dimensions` | 否 | 维度子集（`复查清单.md` 的组名），或 `{key, focus}` 自定义维度；缺省七组全开 |
| `scratch` | 是 | scratchpad 目录；复现脚本写到 `<scratch>/p<plan_no>/` |
| `maxGapAgents` | 否 | 补漏阶段最多追查几个缺口，缺省 4 |
| `followUp` / `repro` | 否 | 传 `false` 可关掉补漏追查 / 复现阶段 |
| `validateOnly` | 否 | 为真时只校验 args 就返回，0 个代理 |

### 阶段与返回

1. **Find**：每个维度一个只读核查代理（提示词里带档案、已知清单、维度要点与规则）
2. 归并（纯代码）：标题相同，或第一条证据同文件、行号相差 3 行以内的，归成一条
3. **Verify**：逐条对抗式核实，H / M 两个视角（读代码反驳、推演触发路径），L 一个视角；过半反驳就淘汰
4. **Critic**：补漏代理找没读的模块、没过的维度、没核实的说法；有缺口追加一轮定向核查与核实（只一轮，超出 `maxGapAgents` 的缺口记在 `dropped`）
5. **Repro**：一个代理把存活的发现写成复现脚本并运行

返回：`{confirmed, refuted, cleared, read_scope, gaps, dropped, repro, agent_count}`。`confirmed` 每条带 `votes`（各核实视角的理由、证据、修正后的机理、一条可断言的检查）。

代理数：维度数 + 核实（N 到 2N）+ 1 补漏 + 补漏追查（≤ 4）及其核实 + 1 复现。七组全开、一轮 10 条发现时约 25~35 个。

### 主代理怎么消费

- `confirmed`：逐条读证据位置，确认后按 P4 分级；机理以核实代理的 `corrected_mechanism` 与自己读到的为准
- `refuted`：看一眼驳倒的理由，确属误报的写进方案 §2.3 疑点表（免得下一轮再报）
- `cleared`：核实后写进 §2.3
- `read_scope`：汇成方案 §2 的「本轮读过的范围」
- `repro`：主代理自己再跑一次 `repro.script_path`，结果以自己跑的为准，写进实施文档 §2.0
- `gaps` / `dropped`：还没追查的缺口，主代理 inline 补查，或写进方案 §7

## system-review-implement

### args

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `plan` / `impl` | 是 | 方案与实施文档的路径 |
| `units` | 是 | 实施单元数组 `{id, title, sections, files, tests}`，取自实施文档的「实施单元」表；**各单元的 `files` 与 `tests` 必须互不相交**（脚本开头校验，相交直接报错返回） |
| `regress_commands` | 是 | 回归命令数组，如 `["./.conda/python.exe tools/official_event_check.py", "./.conda/python.exe tools/tests/education/run_all.py"]` |
| `scratch` | 是 | 回归日志目录 |
| `validateOnly` | 否 | 同上 |

### 阶段与返回

1. **Implement**：`pipeline(单元, 实施, 单元复审)`。实施代理只改自己名下的文件，只允许 `py_compile`，不跑测试与构建（测试引导会触发增量构建写 `data/*.json`，并行跑会互相覆盖），不做 git 写操作；与方案不符的写进 `deviations`，要改名下以外的文件写进 `needs_outside`
2. **Regress**：一个代理顺序跑 `regress_commands`，重定向到文件再读，跑完还原 `data/po/`
3. **Audit**：方案对照 / 测试覆盖 / 收尾与文档三个视角并行复审整体 diff，只报问题

返回：`{units:[{id, result, review_issues}], regress, audit, agent_count}`。代理数 = 2 × 单元数 + 1 + 3。

### 主代理怎么消费

- `deviations`：先改方案（记进实施文档 §6.1 的偏离），再决定代码怎么改
- `needs_outside`：主代理自己改
- `review_issues` / `audit`：逐条核实后修；修完主代理自己重跑 `run_all.py`
- `audit[].p6_todo`：并进 P6 的收尾清单

## 失败与续跑

- 结果为空或不对劲时，先读返回信息里 Transcript dir 下的 `journal.jsonl`（每个代理的实际返回值），不要猜
- 改了脚本或 args 想续跑：`Workflow({scriptPath, resumeFromRunId})`，没改动的前缀代理直接用缓存
- 某个代理返回 `null`（被跳过或出错）：脚本已 `.filter(Boolean)`，对应维度或单元会缺一份，看 `log` 提示后由主代理 inline 补

## 为什么核查代理不用 Explore

Explore 只读片段、不注入 CLAUDE.md，适合定位，不适合逐行审查；两个脚本都用默认的 workflow 子代理。

## 常见误用

- **把 Workflow 的发现直接抄进方案**：违反铁律 1，核实代理也会看错；主代理必须自己读证据。
- **实施单元共用文件**：`game_type.py` 字段、常量表、`constant_promise` 这类被多个单元改的文件，由主代理在调 Workflow 之前改好。
- **`known` 留空**：核查代理会把上一轮已排除、已拍板的事又报一遍，核实阶段白跑。
