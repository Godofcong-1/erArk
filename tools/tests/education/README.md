# 生长养成系统回归测试

覆盖 `Script/System/Education_System/` 及其全部外部挂接点（结算器、状态机、前提、面板、存档、口上与事件数据）的无头回归套件。系统说明见 `.github/prompts/数据处理工作流/生长养成系统.md` §16。

## 怎么跑

```bash
.conda\python.exe tools/tests/education/run_all.py            # 全部 15 个文件，约 1 分钟
.conda\python.exe tools/tests/education/run_all.py semester   # 只跑文件名含关键字的
.conda\python.exe -u tools/tests/education/test_semester.py   # 单跑一个（进程末尾会 os._exit）
```

- **必须用 `./.conda/python.exe`**，裸 `python` 是商店空壳。
- 每个文件各起一个进程：游戏的全局缓存只能初始化一次，同进程串跑会互相污染。单文件超时 240 秒。
- 日志写在 `%TEMP%/erArk_education_tests/<文件名>.log`；汇总行里的 `PASS= / FAIL=` 来自各文件末尾的同名行。
- 改了 CSV（口上 / 前提 / 效果 / 事件）后先删 `data/Character_Talk.json` 再跑一次 `buildconfig.py`，然后 `git checkout -- data/po/`（构建会清空 PO），否则断言读到的是旧生成物。

## 文件与覆盖

| 文件 | 覆盖 |
| --- | --- |
| `_bootstrap.py` | 公共引导：初始化链、屏蔽绘制并记录文本（`drawn_text`）、`askfor_all` 桩、`check / section / finish`、`make_character` fixture、`set_time / move_to / open_all_classroom / clear_schedules`；未捕获异常时 `os._exit(2)`（否则非守护线程会让崩溃的进程挂住） |
| `test_schedule.py` | 教室列表与开放、格子读写、临时课覆盖层、教师反查与冲突、个人课表、`get_now_course / get_now_teaching`、上课地点、实习导师 |
| `test_auto_schedule.py` | 一键排课的幂等 / 可复现 / 无教师冲突 / 周末不排 / 实践教室科目约束；一键选课 |
| `test_class_ai.py` | 翘课概率表、教师可用性、缺课去重、体力闸与心情闸、必修实操课豁免、六种课型派发、见学母亲有效性与回落链、萝莉按日程见学（有课优先、少女不见学）、日程优先于幼女默认见学、没课节次的去向（学生岗不走工作链、白天算娱乐时间、`find_character_target` 派发到育儿室 / 教室 / 母亲身边）、预到岗边界 |
| `test_growth.py` | 速度曲线、教育区加成、成长停滞减半、学生 / 教师 / 见学结算、成年结算、养成数值读写、两份候选名单 |
| `test_semester.py` | 学期时间、本学期出勤、四档判据、等级增量、学期切换幂等、成绩单历史上限与正文 |
| `test_schedule_template.py` | 预设模板、增删改、套用与覆盖、need 校验（幼女 / 萝莉 / 少女 / 学生岗）、`judge_require` 的 `/` 或与 `W` 岗位语法、选活动三组与「限幼女/萝莉」标注、条件不符退回自由选择、有课的时段也照写（课表在节次级别优先）、每日改写、幼女默认池（过家家 / 自由玩耍随机） |
| `test_sex_class.py` | 临时课存取与过期清理、星期→日期、谁能参加、三次提醒的跨越判定、开课 / 下课三档、主修加成、旁观名单与结算 |
| `test_prenatal_baby.py` | 胎教累积 / 转写 / 读口、效果 555、六个照料行为的效果链与 CVE 实跑、喂奶 556 |
| `test_growth_event.py` | 候选人、同胞与同学、事件桶与互动对象、每日派发、注册式容量与抬头、毕业 / 期末入队 |
| `test_settle_effects.py` | 512 / 548 / 549 / 550 / 552 / 553 / 554 / 10014 / 10015 与二段 622 / 623 |
| `test_premise_tokens.py` | 前提注册、岗位与女儿前提、CVP `Course / CourseType / CourseShowOff / Growth`、CVE Growth、实操课 12 条前提、带教前提 |
| `test_panels.py` | 页签容器、全局课表（格子编辑、临时课编辑、必修名单）、个人课表（首屏只有顶在行首的「选择学生」、走通用 NPC 选择面板的脚本化选人、选课、复制、清空）、养成总览（选人、阶段行的母亲 / 剩余天数 / 预计日期 / 成长停滞、成绩单翻页、待处理）、日程模板、`student_select` 组件、Web 适配器冒烟 |
| `test_talk_data.py` | 教育相关口上的覆盖、行为与前提 token 逐条校验、正文卫生、`tools/official_event_check.py`、配置一致性（含全部指令的 cid 落在自己类型的段内、养成相关指令编号）、ArkEditor 表同步 |
| `test_save_compat.py` | `CHILD_GROWTH` 字段级回填与成绩单迁移、教育区娱乐编号 175~178→152~155 的读档迁移（模板 / 单孩覆盖 / 娱乐槽位）、`save/` 下全部真实存档只读载入后的结构、学期结算幂等、四个面板可画 |
| `test_behavior_loop.py` | 模式 B：在女儿最多的真实存档上排课，带护栏跑六轮行为循环（收敛、女儿进教室）与一次跨天结算 |

## fixture 陷阱（本套件新增的，通用的见 `.claude/skills/headless-game-test/SKILL.md`）

- `from _bootstrap import *` 默认不导出下划线开头的名字，翻译函数 `_` 靠 `_bootstrap.__all__` 显式导出。
- `behavior.start_time` 默认是公元 1 年，`get_class_period` 读的就是它——改游戏时间一律用 `set_time()`，它会同步全部角色。
- 实行值计算会读 `assistant_services[8]`，fixture 要 `get_assistant_services_zero()`。
- `TitleLineDraw / LittleTitleLineDraw` 的文字在 `title` 属性上，不在 `text`。
- 容器 `Education_Manage_Panel.draw()` 每轮会调 `basement.get_base_updata()`，最小 fixture 要把它钉死。
- 好感链的实际数值受信物 / 难度 / 连续指令影响，断言「走了好感结算」要打桩 `common_default.base_chara_favorability_and_trust_common_settle` 记录调用。
- 真实存档里总有几个没事可做的干员在「空闲 1 分钟」里一分钟一分钟地挪，45 分钟一轮要挪 45 步，护栏上限要 ≥ 60 才不会把它误判成卡死。
- 二段效果注册表是 `constant.settle_second_behavior_effect_data[效果id](角色id, change_data)`，与一段的四参数签名不同。
- 要直接跑 `handle_npc_ai.find_character_target`（`test_class_ai.py` 的 `dispatch`）：合成角色得先把 `action_info.wake_time` 设成当天（否则被「起床」目标 205 接管）、`clothing.get_npc_cloth` 穿上衣服（全裸时 `normal_all` 不成立，工作 / 娱乐的自动 AI 根本不跑）、`handle_premise.refresh_unnormal_flag`；每次派发前清掉 `behavior.move_target / move_final_target` 并把行为置回 `SHARE_BLANKLY`，否则被「继续移动」目标接管。育儿室的场景路径是 `["教", "育儿"]`（`SCENE_NURSERY`）。
