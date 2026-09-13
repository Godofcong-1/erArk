---
name: system-review-round
description: 对 erArk 某个已实现的系统做一轮全面复查：主代理建系统档案，用 Workflow 多代理并行核查、对抗式核实、复现，产出 plan/wait 下的方案与实施步骤双文件；用户拍板后用 Workflow 并行实施各单元、回归与复审，再收尾归档。当用户说"再进行一次检查 / 复查某系统"、"检查该系统是否仍有遗漏的未实现内容、BUG、死代码、待处理项"、"第 N 轮复查"时使用。
---

# Skill Instructions

你是 erArk 的系统复查负责人。一轮复查从「找问题」走到「修完归档」，中间有两个必须停下来等用户的点。本 skill 从生长养成系统第五~十一轮复查（Plan 22 总纲 §10、Plan 25~30）归纳而来，对任意系统通用；叙述版与复查史见 `.github/prompts/数据处理工作流/系统复查工作流.md`。

必读的仓库资料：
- 计划文档格式：`plan/计划模板.md`（双文件附录）；本轮用的骨架在本目录 `templates/`
- 蓝本：`plan/done/plan_30_生长养成系统第十一轮复查_方案.md` 与 `_实施步骤与记录.md`
- 无头测试：`.claude/skills/headless-game-test/SKILL.md`；日志：`update-changelog` skill
- 各阶段详解：本目录 `tools/`（进入某阶段前先读对应文件）

## 铁律

1. **扇出的活走 Workflow，结论由主代理把关**：P1~P3 调 `system-review-find`，P5 调 `system-review-implement`（用户 2026-09-13 明确要求用 Workflow 做多代理编排）。Workflow 返回的发现只是线索，主代理亲自读到 `file:line` 或看过复现输出才写进方案；写双文件、向用户提问、记录拍板、提交只由主代理做。用户在本次对话里写了「不使用子代理」时，以用户为准，改成主代理 inline 照同样的阶段做。
2. **结论要有落点**：每条发现写 `file.py:行号 函数名` 与依据（读代码或复现）；拿不到依据的写「疑似」，不写成事实。
3. **改前全部成立才立项**：复现脚本的每一项在改前都要成立，按「问题命中 / 前提对照 / 数据事实 / 随口径」四类分开计数（Plan 30 §2：39 = 18 + 20 + 1）。
4. **不翻旧账**：用户已拍板的口径、既往轮次 §2.3「排查过、没有发现问题的疑点」、§7「不在本方案范围」，不重复排查、不重复提问；它们放进 Workflow 的 `known`（先例：Plan 27 L2 用户拍板按设计保留，此后各轮不再报）。
5. **停止点 1 之前不改源码**；实施中发现与方案冲突的事实，先改方案再改代码（`plan/计划模板.md`）。
6. **环境**：解释器一律 `./.conda/python.exe`；构建或跑测试之后 `git checkout -- data/po/`；含反斜杠或中文的脚本用 Write 写成文件再跑；PowerShell 提交信息先写文件再 `git commit -F`。

## 阶段总览

| 阶段 | 执行者 | 做什么 | 产出 | 详解 |
| --- | --- | --- | --- | --- |
| P0 建档与基线 | 主代理 | 编号、轮次、快照；系统档案；已知清单；回归基线；死代码扫描 | Workflow 的 args、方案元信息头 | `tools/P0_建档与基线.md` |
| P1~P3 通读、核查、复现 | Workflow `system-review-find` | 按维度并行核查 → 归并 → 对抗式核实 → 补漏 → 复现脚本 | 存活发现、疑点表、R 组表 | `tools/Workflow编排.md` |
| 核实 | 主代理 | 逐条读证据、自己再跑一次复现脚本 | 方案 §2 | `tools/P1_通读与挂接点.md`、`tools/P2_逐项核查.md`、`tools/P3_复现脚本.md` |
| P4 分级、口径、双文件 | 主代理 | H / M / L；推荐口径与弃选方案；`plan/wait` 双文件；中文提问 | 双文件（状态「未实施」） | `tools/P4_分级口径与双文件.md` |
| **停止点 1** | 用户 | 拍板口径；主代理回写方案元信息、§3、§8 | — | — |
| P5 实施 | 主代理 → Workflow `system-review-implement` | 主代理先改共用文件；各单元并行实施与复审；全套回归；三视角复审；主代理修问题 | 代码与测试全绿 | `tools/P5_实施.md` |
| P6 收尾 | 主代理 | 实施记录 §6；说明文档 / 索引 / 总纲回指 / 测试 README；`update-changelog`；`git mv` 到 `plan/done/` | 可提交的工作区 | `tools/P6_收尾与下一轮.md` |
| **停止点 2** | 用户 | 看 `git diff --stat` 与拟用提交信息，确认后提交 | 提交 | 同上 |

检查维度的清单：`tools/复查清单.md`（Workflow 的七个核查维度与它一一对应）。

## 两个 Workflow

| Workflow | 文件 | 调用 |
| --- | --- | --- |
| `system-review-find` | `.claude/workflows/system-review-find.js` | `Workflow({name: "system-review-find", args: {...}})`；本会话里刚改过脚本、或名字没注册上时用 `{scriptPath: ".claude/workflows/system-review-find.js"}` |
| `system-review-implement` | `.claude/workflows/system-review-implement.js` | 同上 |

- args 的字段、返回结构、代理数估算、续跑方式见 `tools/Workflow编排.md`；正式跑之前先用 `validateOnly: true` 检查 args（0 个代理）。
- 用户调起本 skill，就等于同意本 skill 里写明要跑的这两个 Workflow；规模明显超出常规（例如一轮 30 个代理以上）时先告诉用户估算再跑。
- 跑起来之后马上挂 Monitor 盯着（本目录 `wf_watch.py --watch`），用户在对话里看得到每个代理交卷；停没停住的判法与处理见 `tools/Workflow编排.md`「运行中：怎么判断停没停住」。

## 在 plan mode 下被调起时

Workflow 不能在 plan mode 里跑。只做 P0，把档案与已知清单写进会话计划文件；ExitPlanMode 时写明「退出后先跑 `system-review-find`、落 `plan/wait` 双文件，**不实施**」。用户的计划文档生命周期是 `plan/wait` → 拍板 → 实施 → `plan/done`，会话里的临时计划文件不留档。

## 每轮产出物清单

| 产出 | 位置 | 阶段 |
| --- | --- | --- |
| 方案 / 实施步骤与记录 | `plan/wait/plan_NN_<系统>第N轮复查_*.md` → 收尾时 `git mv` 到 `plan/done/` | P4 / P6 |
| 复现脚本与日志 | scratchpad `pNN/`（不入库，表写进实施文档 §2.0） | P3 |
| 代码、数据、测试 | 按实施文档 §1 | P5 |
| 系统说明文档 | 维护注意事项新增条目、测试章节计数 | P6 |
| 主 Plan / 总纲 | 追加一节，只写一行回指本轮 | P6 |
| `update.log` | `update-changelog` skill | P6 |
| 提交 | 用户确认后 | 停止点 2 |

## 回复前自检

- 写进方案的每条发现，我是否亲自读过它的证据位置？
- 复现脚本改前是否全部成立？四类计数写了吗？
- 有没有把已拍板的口径又拿出来问？
- 停止点 1 之前有没有动过源码？停止点 2 之前有没有提交？
- 跑过构建或测试之后，`data/po/` 还原了吗？
