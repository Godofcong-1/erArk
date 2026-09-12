# 生长养成系统回归测试

覆盖 `Script/System/Education_System/` 及其全部外部挂接点（结算器、状态机、前提、面板、存档、口上与事件数据）的无头回归套件。系统说明见 `.github/prompts/数据处理工作流/生长养成系统.md` §16。

## 怎么跑

```bash
.conda\python.exe tools/tests/education/run_all.py            # 全部 15 个文件、1035 条断言，约 1 分钟
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
| `test_schedule.py` | 教室列表与开放、格子读写、临时课覆盖层（含 `include_temp=False`、一键选课不选临时课）、教师反查与冲突、个人课表、`get_now_course / get_now_teaching`、上课地点、实习导师；Plan 26：撞课判定照每周课表（被临时课顶掉的教师照样判撞课）、`get_now_teaching(0)` 只在玩家就在那间教室时返回临时课、上课地点过滤未开放的场所（`judge_scene_open`）、`judge_course_need_pass`、`get_upcoming_course` 不再收 `now_time`；Plan 27：全局课表那一格清空即视为没课（`get_course_at` 为 None），格子在、教师为 -1 仍是一节课，临时课覆盖层给出的格子（预约 / 必修）照算 |
| `test_auto_schedule.py` | 一键排课的幂等 / 可复现 / 无教师冲突 / 周末不排 / 实践教室科目约束；一键选课 |
| `test_class_ai.py` | Plan 24 起师生走工作链，派发一律跑整条 `find_character_target`（`dispatch(cid, now_time)`）：翘课概率表与定种子掷骰（同节稳定、0/1 边界、每节一掷）、教师可用性（含换岗 / 跟随 / 睡着 / 住院 / 不在岛上 / 临盆 / 产后 / 助理 / 体检中）、缺课去重、状态函数 `get_teacher_duty` / `get_course_stage`（六种状态、必修豁免、非本岗恒为 NONE、前提只读不惰性创建养成数据）、教室课与个人式课的整链派发（715 移动、304 / 713 / 716、教室或地点解析不出交回娱乐链）、兴趣课逐项（`class_ok` 的全部 16 项：715 → 716 执行该娱乐的行为、截到本节结束）、实习课逐岗（面板可选的全部岗位：715 → 716 `intern_class`；多房间岗位的导师在哪间学徒就去哪间）、两道闸（721 记缺课、714 翘课）、必修实操课豁免与必修生覆盖、教师按课表走班（实践教室、被临时课顶掉、办公室待命、午休、到岗时间、周日有课照上）、学生到岗时间先去第一节课、预到岗（已在实操教室原地等开课）、normal 门槛（跟随不再来回走，临盆 / 产后 / 助理 / 体检中的教师不授课、学生自习）、外层闸（图书馆管理员与厨师的派发不变）、口径收窄（改岗女儿不上课、改回恢复）、见学让路与回落链、萝莉按日程见学、没课节次的去向；Plan 25：学生截短规则（A 待赴实操课 / B 马上开课；`begin()` 造「行为已进行一段、玩家这一步已跨过开课」的情形，断言的是截出来的时长）、开课后到场加入课堂（722）、醉酒教师不可用、303 拉人过闸（`teach_pull()`）、561 只认学生岗、成年必修生；Plan 26：未解锁场所与兴趣课条件不符都交回娱乐链、待赴的实操课被玩家提前开讲且人已在教室 → 722、课堂模式下受邀到场走 515 → 722（非学生干员到场即收场、不进 H）而普通群交走 505 → 96、母亲睡着时见学回落自由玩耍（公务事件的 `self_mother_available` 不受影响）；Plan 27：已停课 → NONE、交回娱乐链且不记出勤、不为它提前动身，必修覆盖到空格子与预约在空格子上的实操课照旧，561 的回落只挑已开放的理论教室（定种子），爆睡（行为是睡觉、没挂标记）的学生不被 303 拉 |
| `test_growth.py` | 速度曲线、教育区加成、成长停滞减半、学生 / 教师 / 见学结算、同一节去重与 `count_attend`、成年结算、养成数值读写、两份候选名单、待炫耀只记科目与幼女 / 萝莉期的女儿（跑真实的 `gain_ability`）；Plan 26：性技科目的课堂只发理论经验（`get_class_exp_id` 与映射表的类型 / 覆盖面守卫、腰技只给习得、师生两侧）、未成年一门性技都没学会时不凭珠升技巧（面板说明、学会一门后可升、成年不受影响） |
| `test_semester.py` | 学期时间、本学期出勤、四档判据、等级增量、学期切换幂等、成绩单历史上限与正文 |
| `test_schedule_template.py` | 预设模板、增删改、套用与覆盖、need 校验（幼女 / 萝莉 / 少女 / 学生岗）、`judge_require` 的 `/` 或与 `W` 岗位语法、选活动三组与「限幼女/萝莉」标注、条件不符退回自由选择、有课的时段也照写（课表在节次级别优先）、每日改写、幼女默认池（过家家 / 自由玩耍随机）；Plan 27：`judge_activity_place_open`、地点未开放的时段退回自由选择与「未开放→自由选择」标注、幼女默认池滤掉未开放的（游戏室没解锁只剩自由玩耍，解锁后恢复） |
| `test_sex_class.py` | 临时课存取与过期清理、星期→日期（含季月月底按游戏时钟跳到下个季月）、谁能参加（前置修习与必修豁免）、三次提醒的跨越判定、开课 / 下课三档、下课后 ended 与当场开的课即删、主修加成、旁观名单与结算、出勤只给女儿与学生岗；Plan 26：提前开预约课（复用预约不另开、`find_reserved_class` / `find_class_to_start`、按教室取必修名单、按预约时刻判档、下课后 ended 与同节重开）、在别的教室开课挪用预约、只收学生岗、提醒文案；Plan 27：同一节下课后重开，到场学生再记一节（L2 按设计保留，锁定断言） |
| `test_prenatal_baby.py` | 胎教累积 / 出生折习得珠（Plan 26：不写任何经验、双胎各自全额、按比例折算、折出 0 珠时的文本）/ 读口、效果 555、六个照料行为的效果链与 CVE 实跑、喂奶 556 |
| `test_growth_event.py` | 候选人（成年少女不进名单与容量）、同胞与同学、事件桶与互动对象、每日派发、注册式容量与抬头、毕业 / 期末入队（毕业典礼不受队列上限）；Plan 26：同胞只取幼女 / 萝莉、17 条通用事件对婴儿不成立、成年女儿不推期末事件、期末 13 的档位前提 |
| `test_settle_effects.py` | 512（只发自己的学生、同一节不重复、玩家手动授课只在课表排在这间教室时计出勤）/ 557 晚到补结算 / 548（日程自习不计出勤）/ 549 / 550 / 552 / 553 / 554 / 10014（开课整条链路只记一节出勤）/ 10015 与二段 622 / 623；Plan 26：性技科目的 512 / 548 只发理论经验、不补记初体验，玩家手动授课只在那节临时课的教室里才按性技讲；同一节里连验多种结算时用 `reset_mark()` 清去重标记；Plan 27：550 有待查看才发冻结那份并清 flag、看过之后给截至目前，养成数值 23，玩家手动授课拉来的学生截到本节下课（节次外 45 分钟）、爆睡的学生不拉（`handle_teach` 打桩 `game_update_flow`） |
| `test_premise_tokens.py` | 前提注册（含 Plan 24 的 18 个师生前提、Plan 25 的 2 个新前提，死前提已删）、师生前提只认本岗、岗位与女儿前提、CVP `Course / CourseType / CourseShowOff / Growth`、CVE Growth、实操课 12 条前提、带教前提、授课指令的前提只看所在场景且三类教室都算、`t_baby_0`（Plan 26：1036 对婴儿不成立）；Plan 27：`Growth|23` 成绩单待查看、授课指令的前提对爆睡的学生不成立 |
| `test_panels.py` | 页签容器、全局课表（格子编辑、临时课编辑、必修名单含成年学生岗）、个人课表（首屏只有顶在行首的「选择学生」、走通用 NPC 选择面板的脚本化选人、选课、复制、清空）、养成总览（选人、阶段行的母亲 / 剩余天数 / 预计日期 / 成长停滞、成绩单翻页、待处理）、日程模板、`student_select` 组件；Plan 26：覆盖格「[临]」与选科目页的说明和清空按钮、排实操课页的跨教室提示、个人课表的「（未开放）」「（条件不符）」、课堂模式的邀请名单（打桩通用 NPC 选择面板取名单）；Plan 27：选择活动的「未开放」标注（按钮不超过每格 31 列）、周日实习课只画一句提示；Web 适配器冒烟 |
| `test_talk_data.py` | 教育相关口上的覆盖、行为与前提 token 逐条校验、正文卫生、`tools/official_event_check.py`、配置一致性（含全部指令的 cid 落在自己类型的段内、养成相关指令编号）、ArkEditor 表同步 |
| `test_save_compat.py` | `CHILD_GROWTH` 字段级回填与成绩单迁移、教育区娱乐编号 175~178→152~155 的读档迁移（模板 / 单孩覆盖 / 娱乐槽位）、`save/` 下全部真实存档只读载入后的结构、学期结算幂等、四个面板可画 |
| `test_behavior_loop.py` | 模式 B：在女儿最多的真实存档上排课，从 08:40（到岗时间）起带护栏跑六轮行为循环，检查点落在每节课中段（节次交界处人人都在换教室）：收敛、学生岗的女儿进教室（课表只对学生岗生效，存档里改了岗的女儿不计入）、本节有课的教师在课表上那间教室授课、上午四节每人平均 ≥ 3 节出勤；再预约一节下午的实操课，断言开课时必修生都已离开上一节的教室、且已有人在实操教室等（路上撞上需求会晚到，所以不要求全员到场）；再跑一次跨天结算 |

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
- 循环变量别用 `_`：它是 `_bootstrap` 导出的翻译函数，`for _ in range(...)` 之后同一文件里再调 `_()` 会报 `'int' object is not callable`（Plan 27 踩过）。
- 个人课表指向的教室课要在全局课表上排格子（`set_class_cell`）：空格子按「已停课」算没课，只排个人课表的夹具测不到上课（Plan 27）。
- 按 cid 查 `game_config.config_target` / `config_target_premise_data` 时，键是「所在文件夹名 + cid」：`data/target/default/target.csv` 的 505 是 `"default505"`（`buildconfig.py` 的 `path_list[-2] + row[k]`），直接用 `"505"` 查会静默落空；列举一组行用 `config_target_type_index`。
