"""
教育养成系统常量统一定义文件

本子系统（Script/System/Education_System）内的全部模块级常量集中在此定义、记录与管理，
各模块通过 `from Script.System.Education_System import education_constant` 引用，
子系统外的代码（结算、状态机、前提、指令、角色信息头等）同样从本文件引用，
不得在各自文件内重复定义。

⚠️ 本文件里有一批常量是**从配置表现算**的（科目表、阶段名、性格倾向名），
   它们在 import 本模块时求值，因此**必须在 `game_config.init()` 之后才导入本模块**。
   实测这个前提天然成立：教育系统的每个入口（面板、结算、状态机、前提）都是在函数内
   惰性 import 的，`game.py` 的整个启动序列走完时本模块都还没有被导入。
   万一日后有人把它提前，下面的守卫会把原因打出来，而不是留下一堆空表。

⚠️ 凡是要拿去和配置/场景数据比对的字符串，一律要过 `_()`：
   `game_config` 载入时对所有 `name` 列做过翻译（`game_config.py:536`），
   场景名同样（`map_config.py:64`）。这里写死中文，在非中文语言下就永远匹配不上。

分组：
1. 成长阶段与教育区
2. 科目
3. 课型、教室与场地
4. 星期与自动排课
5. 日程模板与时段
6. 上课结算：习得与经验
7. 上课AI：缺课与翘课
8. 见学（跟随母亲）
9. 性技实操课
10. 胎教与哺乳
11. 照料值与性格倾向
12. 养成数值编号
13. 学期与成绩单
14. 养成事件
15. 面板显示与排版
"""
from types import FunctionType
from typing import List

from Script.Config import game_config
from Script.Core import get_text
from Script.System.Official_Event_System import official_event_handle

_: FunctionType = get_text._
""" 翻译api """

if not game_config.config_ability:
    print("\ndebug education_constant 在 game_config.init() 之前被导入了，从配置现算的常量会是空表\n")

# ==== 1. 成长阶段与教育区 ====
CHILD_TALENT_ID_LIST = (101, 102, 103, 104)
""" 成长链的四个年龄素质id：101婴儿 / 102幼女 / 103萝莉 / 104少女。
    ⚠️ 这四个id是成长链的**定义本身**（`pregnancy_handle` 按天数逐级换素质），配置里推不出来，
       所以写死在这里；名字则一律从 Talent.csv 现取，见下 """
STAGE_TALENT_NAME = {talent_id: game_config.config_talent[talent_id].name for talent_id in CHILD_TALENT_ID_LIST}
""" 四个阶段的显示名，从 Talent.csv 现取。
    ⚠️ 不要再包一层 `_()`：`game_config` 载入时已对所有 name 列做过翻译，再包一次反而对不上词条 """
CHILD_TALENT_SET = set(CHILD_TALENT_ID_LIST)
""" 成长链四个年龄素质的集合形式，判定「是不是孩子」用 """
STUDENT_STAGE_TALENT_SET = {102, 103, 104}
""" 可排课、可查养成总览的三个阶段：102幼女 / 103萝莉 / 104少女。
    婴儿(101)上不了课也没什么可排的，不列入 """
EDUCATION_ZONE_NAME = _("教育区")
""" 教育区在 Facility_effect.csv 中的设施名（该表按名字索引）。
    ⚠️ 必须过 `_()`：`config_facility_effect_data` 的键是 `game_config` 翻译过的 name，
       写死中文会让教育区的成长效率加成在非中文语言下整个失效 """
EDUCATION_ZONE_CID = 15
""" 教育区在 Facility.csv:22 中的设施id，用于查 Rhodes_Island.facility_level """
LEARN_STATE_ID = 9
""" 习得状态id（CharacterState.csv:15），睡眠结算时换算为习得珠(juel 9) """

# ==== 2. 科目（从 Ability.csv 的能力类型现算） ====
ABILITY_TYPE_SUBJECT = 4
""" Ability.csv 的 ability_type：技能。对应 40~49 十门通用技能 """
ABILITY_TYPE_SEX_SKILL = 5
""" Ability.csv 的 ability_type：技术。对应 70~77 八门性技 """
NOT_SUBJECT_ABILITY_SET = {90}
""" 归在上面两个类型里、但**不是课程科目**的能力。
    ⚠️ 90 隐蔽的 ability_type 也是5，可它是隐奸系统的熟练度，不是能开课教的东西。
       按类型筛科目时必须把它排掉，否则课表里会冒出一门「隐蔽课」，实操课也会把它列进主修 """
SUBJECT_ABILITY_LIST = [
    ability_id
    for ability_id in sorted(game_config.config_ability)
    if game_config.config_ability[ability_id].ability_type in (ABILITY_TYPE_SUBJECT, ABILITY_TYPE_SEX_SKILL)
    and ability_id not in NOT_SUBJECT_ABILITY_SET
]
""" 可排课的18门科目（一期方案 §3.4）：Ability.csv 里类型为技能(4)与技术(5)的能力。
    ⚠️ 从配置现算而不是写死 40~49 + 70~77：往后 Ability.csv 增删科目，课表、选课面板、
       成绩单、胎教转写会一起跟上，不必回头改这里 """
MALE_ONLY_SUBJECT_SET = {ability_id for ability_id in SUBJECT_ABILITY_LIST if game_config.config_ability[ability_id].sex_need == 0}
""" 男性专属的科目（Ability.csv 的 sex_need 为0），目前只有76腰技。
    女学生排了它全场吃不到加成且不会报错（四期方案 §7-21），所以下面两张给女儿用的表都排掉它 """
FEMALE_SUBJECT_LIST: List[int] = [ability_id for ability_id in SUBJECT_ABILITY_LIST if ability_id not in MALE_ONLY_SUBJECT_SET]
""" 女儿学得了的科目（17门 = 10门技能 + 7门性技）：全部科目去掉男性专属的那些。
    胎教转写与自动排课取的都是这一张——原先它叫 PRENATAL_SUBJECT_LIST，只写了胎教一个用途，
    而自动排课在自己那边又算了一遍同样的东西 """
SEX_CLASS_ABILITY_LIST = [ability_id for ability_id in FEMALE_SUBJECT_LIST if game_config.config_ability[ability_id].ability_type == ABILITY_TYPE_SEX_SKILL]
""" 实操课可选的主修性技科目：指技70/舌技71/足技72/胸技73/膣技74/肛技75/榨精77 """
PRACTICE_SUBJECT_SET = {42, 43, 46, 47, 48, 49}
""" 实践教室的动手类科目：42战斗 / 43料理 / 46医术 / 47农业 / 48制造 / 49绘画。
    ⚠️ 这一组推不出来——Ability.csv 没有「是不是动手类」这一维，只能列举。
    一期方案 §3.3 写明实践课「侧重动手类与性技理论」，但此前只是文案、代码从未落实，
    手排时实践教室照样能排话术。自动排课落实它——理论教室与大礼堂仍是全部科目 """

# ==== 3. 课型、教室与场地 ====
COURSE_TYPE_THEORY = 0
""" 课型：理论课（教室课，班级式） """
COURSE_TYPE_PRACTICE = 1
""" 课型：实践课（教室课，班级式） """
COURSE_TYPE_PUBLIC = 2
""" 课型：公开课（大礼堂，班级式） """
COURSE_TYPE_PE = 3
""" 课型：体育课（训练场各地点，个人式） """
COURSE_TYPE_INTEREST = 4
""" 课型：兴趣课（娱乐地点，个人式） """
COURSE_TYPE_INTERN = 5
""" 课型：实习课（干员在岗工作，个人式） """
CLASSROOM_COURSE_TYPE_SET = {COURSE_TYPE_THEORY, COURSE_TYPE_PRACTICE, COURSE_TYPE_PUBLIC}
""" 班级式课型（目标为教室场景名，科目与教师查全局课表） """
COURSE_TYPE_NAME = {
    COURSE_TYPE_THEORY: _("理论课"),
    COURSE_TYPE_PRACTICE: _("实践课"),
    COURSE_TYPE_PUBLIC: _("公开课"),
    COURSE_TYPE_PE: _("体育课"),
    COURSE_TYPE_INTEREST: _("兴趣课"),
    COURSE_TYPE_INTERN: _("实习课"),
}
""" 课型编号到显示名的映射，供面板与状态标识使用 """
COURSE_TYPE_SHORT = {COURSE_TYPE_PE: _("体"), COURSE_TYPE_INTEREST: _("兴"), COURSE_TYPE_INTERN: _("实")}
""" 课型在格子里的单字缩写。
    ⚠️ 只有个人式的三种课型需要它——班级式（理论/实践/公开）的格子里写的是教室名，
       「理论教室一」本身就说明了是理论课，再标一个「[理]」是重复 """
CLASSROOM_TAG_BY_COURSE_TYPE = {
    COURSE_TYPE_THEORY: "Class_Room",
    COURSE_TYPE_PRACTICE: "Practice_Room",
    COURSE_TYPE_PUBLIC: "Auditorium",
}
""" 班级式课型对应的场景标签，用于列出可排课的教室。
    ⚠️ 值是**场景标签**不是场景名，标签不参与翻译，绝不能包 `_()` """
PE_PLACE_DATA = {
    _("木桩房"): ("Fight_Room", "training", 205),
    _("射击房"): ("Shoot_Room", "training", 205),
    _("健身区"): ("Gym", "exercise", 206),
    _("游泳池"): ("Swimming_Pool", "swimming", 161),
}
""" 体育课的四处地点（一期方案 §3.21）：地点名 → (场景标签, 行为en_name, 状态cid)。
    ⚠️ 用固定表而不是查配置，是因为这四处各自对应不同的既有行为，没有一张现成的表能推出来。
    ⚠️ **键必须过 `_()`**：它要拿去和 `scene_data[].scene_name` 逐一比对（`schedule_handle` 里
       体育课要精确到具体那间房），而场景名在载入时过了翻译（`map_config.py:64`）。
       键同时也是存进个人课表的 target，与全局课表存教室名是同一套做法。
    ⚠️ 场景数据实际走的是 pickle 缓存（`map_config.py:22`），只有冷构建那一次才过翻译，
       所以**场景名跟的是「缓存生成时的语言」而不是当前语言**。先用中文玩过再把 config.ini
       改成英文，缓存不会重建，全岛地名都还是中文——那是整个游戏的既有问题，不是本表独有。
    ⚠️ 值里的场景标签与行为 en_name 都不翻译。
    模拟对战室不在其中：它的 SceneTag 只有 Room，全仓库没有任何行为挂在它上面 """
CLASSROOM_NUMBER_ORDER = _("一二三四五六七八九十")
""" 教室名末尾中文数字的**数值**序。默认的 sorted() 按 Unicode 码位排，
    会把「理论教室一~六」排成「一三二五六四」——码位序不是数值序。
    ⚠️ 过 `_()` 是为了让译者能给出该语言下对应的一串序号字符（如 "1234567890"），
       教室名本身是翻译过的场景名 """
TEACHER_WORK_TYPE = 151
""" 教师岗位的工作id（WorkType.csv:24），只有该岗位的干员可被排进课表 """
STUDENT_WORK_TYPE = 152
""" 学生岗位的工作id（WorkType.csv:25）。女儿长到幼女时由妊娠系统自动置为此岗位，
    成年干员也可在基建面板被分配为学生；凡此岗位的干员都可排个人课表（一期方案 §9.8.2） """
EXCLUDE_INTERN_WORK_TYPE = {TEACHER_WORK_TYPE, STUDENT_WORK_TYPE}
""" 实习课不开放的岗位：教师与学生是孩子自己在学校里的身份，作为「实习」语义重复（一期方案 §3.21）。
    ⚠️ 从上面两个常量派生而不是再写一遍 151/152，改岗位id时只动一处 """

# ==== 4. 星期与自动排课 ====
WEEK_NAME = [_("周一"), _("周二"), _("周三"), _("周四"), _("周五"), _("周六"), _("周日")]
""" 星期的显示名，下标即 datetime 的 weekday() """
WEEK_DAY_COUNT = len(WEEK_NAME)
""" 一周的天数。由 WEEK_NAME 的长度推出，两者不会各改各的 """
AUTO_SCHEDULE_WEEK_DAY_MAX = 5
""" 自动排课只铺周一~周五（week_day 0~4）。
    周末留给日程模板里的自由玩耍/跟随母亲等安排；实习课本来也因为周日全岛无人上班而排不了 """

# ==== 5. 日程模板与时段 ====
SLOT_COUNT = 3
""" 日程时段数：0上午 / 1下午 / 2晚上，与 entertainment.entertainment_type 的三个槽位一一对应 """
SLOT_NAME = {0: _("上午"), 1: _("下午"), 2: _("晚上")}
""" 时段编号到显示名 """
SLOT_PERIOD_RANGE = {
    0: (0, 4),
    1: (4, 9),
    2: (9, 9),
}
""" 每个时段覆盖的课表节次区间 [起, 止)（`game_time.CLASS_PERIOD_START`：上午4节 + 下午5节）。
    晚上是空区间——19~22 点本就不排课，所以晚上的日程永远生效 """
ENTERTAINMENT_PLAY_HOUSE = 151
""" 娱乐配置「过家家」的cid（Entertainment.csv）。教育区的娱乐编号按「区块id×10+序号」排在 15x 段，
    过家家是该段的第一项，其后依次是 152 照料卵（妊娠系统，见 pregnancy_constant.TEND_EGGS_ENTERTAINMENT_ID）/
    153 跟随母亲 / 154 自由玩耍 / 155 上课（无课时自习）。幼女的每日随机娱乐固定是过家家（handle_npc_ai.get_chara_entertainment） """
ENTERTAINMENT_FOLLOW_MOTHER = 153
""" 娱乐配置「跟随母亲」的cid（Entertainment.csv）。它没有固定地点，执行走 class_ai 的见学分支；
    日程模板把某个时段排成它时，该时段也走见学分支。
    ⚠️ 2026-09-09 由 176 改为 153（原编号排在大浴场段 17x）：旧存档里的旧编号由 save_handle 读档时换算 """
ENTERTAINMENT_FREE_PLAY = 154
""" 娱乐配置「自由玩耍」的cid（原 177），地点为育儿室，也是见学的回落目标 """
ENTERTAINMENT_SELF_STUDY = 155
""" 娱乐配置「上课（无课时自习）」的cid（原 178），
    行为指向 self_study(211)：有课就去上课，没课就在理论教室自习。need 列为 W152|1，只有学生岗能排 """
SCHEDULE_ONLY_ENTERTAINMENT_SET = {ENTERTAINMENT_FOLLOW_MOTHER, ENTERTAINMENT_FREE_PLAY, ENTERTAINMENT_SELF_STUDY}
""" 只由日程模板指派、不进每日随机娱乐池的三项（handle_npc_ai.get_chara_entertainment 用它排除）。
    从上面三个常量派生，改编号时只动一处 """
SCHEDULE_FREE_CHOICE = 0
""" 日程时段的「自由选择娱乐活动」：槽位存 0，表示该时段不改写、保留当天的随机娱乐。
    ⚠️ 它不是 Entertainment.csv 里的一行，只是 0 这个哨兵值的显示名；不满足活动条件的孩子也会退回到它 """
SCHEDULE_FREE_CHOICE_NAME = _("自由选择娱乐活动")
""" 「自由选择娱乐活动」的显示名。模板表、编辑页、个人日程摘要里的 0 一律显示成它，不再显示「--」或「未设置」 """
CHILD_SCHEDULE_FIRST_ROW = [ENTERTAINMENT_SELF_STUDY, SCHEDULE_FREE_CHOICE]
""" 「选择活动」面板第一行固定的两项：上课（无课时自习）与自由选择娱乐活动。
    第二行是有年龄需求的活动（过家家 / 跟随母亲 / 自由玩耍），不写死、由 schedule_template_handle 从 need 列现算 """
TEMPLATE_ACADEMIC = 1
""" 预设模板：学业优先 """
TEMPLATE_BALANCED = 2
""" 预设模板：均衡（默认推荐） """
TEMPLATE_PLAYFUL = 3
""" 预设模板：玩乐优先 """
TEMPLATE_CUSTOM = 4
""" 预设模板：自定义（初始三个时段全空，由玩家逐时段指定） """
PRESET_TEMPLATE_NAME = {
    TEMPLATE_ACADEMIC: _("学业优先"),
    TEMPLATE_BALANCED: _("均衡"),
    TEMPLATE_PLAYFUL: _("玩乐优先"),
    TEMPLATE_CUSTOM: _("自定义"),
}
""" 四套预设模板的名字（二期方案 §3.6 的表） """
PRESET_TEMPLATE_SLOT_NAME = {
    TEMPLATE_ACADEMIC: (_("上课（无课时自习）"), _("上课（无课时自习）"), _("读书")),
    TEMPLATE_BALANCED: (_("上课（无课时自习）"), _("下棋"), _("自由玩耍")),
    TEMPLATE_PLAYFUL: (_("过家家"), _("下棋"), _("自由玩耍")),
    TEMPLATE_CUSTOM: ("", "", ""),
}
""" 预设模板各时段的娱乐**名字**（不是cid）。
    ⚠️ 写名字而不是写cid，是因为 Entertainment.csv 的编号会随内容增删漂移，
    按名字反查一次比在代码里钉死一串数字安全。查不到的名字落为0（该时段不改写）。
    ⚠️ **必须过 `_()`**：反查的对象是 `config_entertainment[].name`，那是翻译过的；
       写死中文会让四套预设模板在非中文语言下全部套用失败（三个时段都查不到、一个都不改写）。
    二期方案 §3.6 的「兴趣活动」在配置里没有同名项，取「下棋」作为代表性的兴趣类娱乐 """

# ==== 6. 上课结算：习得与经验 ====
COURSE_LEARN_BASE = {
    COURSE_TYPE_THEORY: 30,  # 理论课，沿用既有授课结算的默认基础值
    COURSE_TYPE_PRACTICE: 50,  # 实践课，教室容量小、单位收益更高
    COURSE_TYPE_PUBLIC: 15,  # 大礼堂公开课，容纳全部孩子、单位收益低
    COURSE_TYPE_INTERN: 40,  # 实习课，实地跟岗，介于理论(30)与实践(50)之间
}
""" 各班级式课型的单节课习得基础值（草案，实施时以实测为准）。
    最终习得值 = (上课分钟数 + 本值) × 速度系数 × 教育区加成 × 素质修正 """
COURSE_EXP_BASE = {
    COURSE_TYPE_THEORY: 3,  # 理论课
    COURSE_TYPE_PRACTICE: 5,  # 实践课
    COURSE_TYPE_PUBLIC: 1,  # 大礼堂公开课
    COURSE_TYPE_INTERN: 4,  # 实习课
}
""" 各班级式课型的单节课科目经验基础值（草案）。科目经验是分科的，决定单科能升到多高 """
SELF_STUDY_LEARN_BASE = 15
""" 自习（本节无教师）的习得基础值；无教师则无等级差可算，速度系数恒取1.0 """
SELF_STUDY_EXP_BASE = 1
""" 自习的科目经验基础值 """
GROWTH_STOP_TALENT_ID = 28
""" 成长停滞素质的id（Talent.csv:31，由 plan_17 的成长停滞药赋予）。
    总纲口径 27：停滞期间可以继续上课，但一切学习收益减半，作为无限期养成的代价 """
GROWTH_STOP_LEARN_RATE = 0.5
""" 成长停滞期间学习收益的倍率（口径 27「经验减半」）。
    乘在学生侧的每一条收益上：教室课 / 自习 / 实习课（get_class_adjust）、见学（settle_follow_mother_gain）、
    实操课主修加成（sex_class_handle.get_subject_bonus）；教师侧的教学相长不受影响——停滞的是学生 """

# ==== 7. 上课AI：缺课与翘课 ====
ABSENT_HP_RATE = 0.3
""" 体力低于该比例则本节缺课去休息；实操课里则是必修学生降级为旁观（口径65）。
    取值与既有前提 `handle_premise_base_value.py:46 handle_hp_low` 的「体力低」口径一致，
    不另立一套阈值 """
NEGATIVE_STATE_ID_LIST = [17, 18, 19, 20]
""" 参与翘课判定的四个负面状态：苦痛17 / 恐怖18 / 抑郁19 / 反感20。
    与 `Script/Core/rich_text.py:255~258` 归为负面色的那一组一致 """
SKIP_CLASS_RATE_TABLE = [
    (4, 0.0),
    (8, 0.10),
    (12, 0.25),
    (16, 0.45),
]
""" 翘课概率阶梯（草案，实施时以实测为准）：(等级和上界, 概率)，达不到第一档则为0，
    超过最后一档取 SKIP_CLASS_RATE_MAX。四项各0~8级，理论最大和32 """
SKIP_CLASS_RATE_MAX = 0.70
""" 四项等级和达16以上（濒临崩溃）时的每节翘课概率 """

# ==== 8. 见学（跟随母亲） ====
FOLLOW_MOTHER_LEARN_BASE = 6
""" 见学的习得基础值。约为理论课(30)的两成——看着母亲干活当然比正经上课慢，
    但胜在幼女期没课的时段本来就是空的，积少成多 """
FOLLOW_MOTHER_EXP_BASE = 1
""" 见学的科目经验基础值 """
FOLLOW_MOTHER_CARE_POINT = 0.5
""" 每次见学累加的照料值。成年时参与身体发育与性格判定（一期方案 §3.8） """
FOLLOW_MOTHER_FAVORABILITY = 2
""" 每次见学母女双方各自增加的好感 """

# ==== 9. 性技实操课 ====
PRE_ARRIVE_MINUTE = 10
""" 选修学生提前到岗的分钟数（四期方案 §3.28.5）。
    ⚠️ 既有节次表首尾相接、没有课间（game_time.py:519），9个节次里有7个的「提前10分钟」
       落在上一节课的最后10分钟内，届时学生会中止当前节次的课转为移动（口径62 提前退场） """
NOTIFY_BEFORE_MINUTE = 30
""" 第二次提醒的提前量（分钟） """
SUBJECT_BONUS = 2.0
""" 主修科目的经验加成倍率（草案）。对照一期的课型经验值（理论3/实践5/公开1/自习1），
    与「实践课比理论课高」是同一量级 """
WATCH_EXP_RATE = 0.25
""" 旁观学生获得的主修科目经验比例。观摩不如亲身，1/4 让「多排学生」有意义又不喧宾夺主 """
WATCH_STATE_BASE = 15
""" 旁观学生的状态结算基础值。既有露出补正对被操作者本人用默认的30
    （Script/Settle/default.py:3627 handle_target_add_small_shy），旁观是二手刺激，取一半 """
WATCH_TALK_RATE = 0.30
""" 旁观口上的触发概率。⚠️ 只限流口上，收益结算每个动作都给——
    玩家一节课可能做20个动作，每次都描写一遍旁观者会刷满屏幕 """

# ==== 10. 胎教与哺乳 ====
PRENATAL_POINT_PER_TIME = 0.5
""" 每次胎教给母亲累积的胎教值（一期方案 §3.9 的数值表） """
PRENATAL_POINT_MAX = 100.0
""" 胎教值上限。妊娠期约 60 个可游玩日，每天两三次也到不了顶，上限只是防止极端刷值 """
PRENATAL_EXP_PER_POINT = 0.5
""" 每 1 点胎教值转写为每门科目多少初始经验。
    满值 100 点 → 每科 50 经验，对照 AbilityUp.csv 的累计需求（10/35/75/145...）落在 2 级附近，
    是「这孩子底子好」的量级，不喧宾夺主 """
NUIRSE_CHILD_HP_MAX_ADD = 2
""" 喂奶一次给婴儿增加的体力上限（体质相关初始值） """
NUIRSE_CHILD_MP_MAX_ADD = 2
""" 喂奶一次给婴儿增加的气力上限 """
NUIRSE_CHILD_FAVOR_BASE = 10
""" 玩家亲自喂奶时额外的好感固定值（照料行为通用的 21 号效果之外再加这一份） """
NUIRSE_CHILD_FRIENDLY_BASE = 10
""" 玩家亲自喂奶时额外的好意（亲密）结算基础值 """

# ==== 11. 照料值与性格倾向 ====
PERSONALITY_PAIR_TALENT = {
    0: (271, 272),
    1: (274, 273),
    2: (275, 276),
    3: (278, 277),
}
""" 四对性格倾向 → (正数侧素质id, 负数侧素质id)：
    勤劳/懒散、坚强/脆弱、热情/孤僻、开放/羞耻（game_type.CHILD_GROWTH.personality_point 为正偏前者）。
    ⚠️ 三期的养成事件是它的主要写入方，四对全为0时面板显示「尚未形成」 """
PERSONALITY_PAIR_NAME = {
    pair_id: (game_config.config_talent[positive_id].name, game_config.config_talent[negative_id].name)
    for pair_id, (positive_id, negative_id) in PERSONALITY_PAIR_TALENT.items()
}
""" 四对性格倾向的显示名，从上面那张素质id表现取 Talent.csv 的名字。
    ⚠️ 这样两张表**不可能对不上**——它们原先分居 growth_panel 与 growth_handle 两个文件，
       注释里互相叮嘱「正负顺序必须一致」，一旦有人只改一处，面板会显示「偏坚强」而结算写的是脆弱 """
CARE_POINT_CHEST_MAX_BONUS = 20
""" 照料值对胸部发育概率表的最大偏移（百分点）。
    偏移的是 `chest_grow` 里「不长」那一档的宽度：照料得越多，落进「不长」的窗口越窄 """
CARE_POINT_PER_CHEST_BONUS = 5.0
""" 每多少点照料值换 1 个百分点的发育偏移 """

# ==== 12. 养成数值编号（事件表与口上前提的 CVP/CVE_A?_Growth 取数编号） ====
GROWTH_VALUE_ATTEND = 0
""" 养成数值编号：累计听课节数 """
GROWTH_VALUE_ABSENT = 1
""" 养成数值编号：累计缺课节数 """
GROWTH_VALUE_ATTEND_RATE = 2
""" 养成数值编号：出勤率百分比（0~100），一节课都没上过时算作100 """
GROWTH_VALUE_STAGE_PROGRESS = 3
""" 养成数值编号：本成长阶段已过的进度百分比（0~100，只读）。
    ⚠️ 事件表靠它把同一阶段的几十条事件分出早/中/后期——
       婴儿期的「第一次睁眼」和「扶着床沿站起来」不该同时在池子里 """
GROWTH_VALUE_SEMESTER_ATTEND = 4
""" 养成数值编号：本学期听课节数（累计减学期基线，一期方案 §3.13） """
GROWTH_VALUE_SEMESTER_ABSENT = 5
""" 养成数值编号：本学期缺课节数 """
GROWTH_VALUE_SEMESTER_ATTEND_RATE = 6
""" 养成数值编号：本学期出勤率百分比（0~100），本学期一节课都没轮到过时算作100 """
GROWTH_VALUE_REPORT_GRADE = 7
""" 养成数值编号：上一份成绩单的档位 0优秀/1良好/2待努力/3无课可评；
    还没有过成绩单时为 -1。⚠️ 成绩单口上与期末事件的差分全靠它，取值口径见本文件第13组 """
GROWTH_VALUE_REPORT_LEVEL_UP = 8
""" 养成数值编号：上一份成绩单里升了级的科目数 """
GROWTH_VALUE_SEMESTER_PROGRESS = 9
""" 养成数值编号：本学期已过的进度百分比（0~100，只读）。
    ⚠️ 与角色无关（学期是全岛共用的），但仍走同一个读口，免得事件表要记两套取数方式 """
GROWTH_VALUE_PERSONALITY_BASE = 10
""" 养成数值编号：四对性格倾向占用 10~13（10+性格对编号），正数偏前者、负数偏后者 """
GROWTH_VALUE_CARE = 20
""" 养成数值编号：照料累积 """
GROWTH_VALUE_PRENATAL = 21
""" 养成数值编号：胎教累积 """
GROWTH_VALUE_EVENT_COUNT = 22
""" 养成数值编号：已触发的养成事件条数 """

# ==== 13. 学期与成绩单 ====
SEMESTER_NAME = {3: _("春季学期"), 6: _("夏季学期"), 9: _("秋季学期"), 12: _("冬季学期")}
""" 四个季月各自对应的学期显示名，键即 game_time.get_season_month() 的返回值 """
REPORT_GRADE_EXCELLENT = 0
""" 成绩档位：优秀 """
REPORT_GRADE_GOOD = 1
""" 成绩档位：良好 """
REPORT_GRADE_POOR = 2
""" 成绩档位：待努力 """
REPORT_GRADE_NO_CLASS = 3
""" 成绩档位：无课可评。本学期一节课都没排，不该被评成「待努力」——那是玩家没排课，不是孩子的问题 """
REPORT_GRADE_NONE = -1
""" 档位读口的空值：这孩子还没有过成绩单。
    ⚠️ 绝不能用0兜底——0是「优秀」，会让全岛没上过学的人都通过优秀档的口上前提 """
REPORT_GRADE_NAME = {
    REPORT_GRADE_EXCELLENT: _("优秀"),
    REPORT_GRADE_GOOD: _("良好"),
    REPORT_GRADE_POOR: _("待努力"),
    REPORT_GRADE_NO_CLASS: _("本学期没有排课"),
}
""" 各档位的显示名 """
EXCELLENT_RATE = 90
""" 评为优秀所需的出勤率下限（百分比） """
EXCELLENT_LEVEL_UP = 2
""" 评为优秀所需的本学期升级科目数下限。⚠️ 光靠不缺课评不上优秀，还得真学出东西来 """
GOOD_RATE = 70
""" 评为良好所需的出勤率下限（百分比），低于此为待努力 """
REPORT_CARD_HISTORY_MAX = 8
""" 每个孩子保留的历年成绩单份数上限，超出时丢掉最旧的那份。
    8 份约两年（一年四个学期），够玩家回看整段成长；
    ⚠️ 必须有上限——一个孩子养到成年约十几个学期，多孩存档不设上限会让存档持续变大 """

# ==== 14. 养成事件 ====
GROWTH_EVENT_DEPARTMENT = 15
""" 养成事件所属的部门id：教育区（Facility.csv 中 type 为 -1 的区块cid） """
GROWTH_EVENT_DAILY_CHANCE = 70
""" 每个女儿每天入队一条养成事件的概率（百分比）。约1.4天一条，
    ⚠️ 不设成100：天天都有事要定夺会让养成变成日常打卡，留出空白日子反而更像在过日子 """
GROWTH_EVENT_DAILY_MAX_PER_CHILD = 1
""" 每个女儿每天最多入队的条数。⚠️ 这是**每孩**上限，全局上限在公务事件系统那边 """
GROWTH_EVENT_QUEUE_PER_CHILD = 4
""" 每个女儿为队列贡献的容量。女儿多的时候待办清单本来就该更长，否则后面的事件会被直接丢掉 """
STAGE_ANY = official_event_handle.SUB_KEY_ANY
""" 事件的 sub_key 取0时表示适用于全部成长阶段（101婴儿~103萝莉），⚠️ 不含已成年的104。
    取公务事件系统的同名常量，只留一个真相来源 """
STAGE_ALL_CHILD = (101, 102, 103)
""" sub_key 为 0 的事件实际覆盖的阶段。成年（104）只接 sub_key 明确写 104 的事件（如毕业典礼） """
GRADUATION_EVENT_UID = "通用1"
""" 毕业典礼的事件uid。uid由「文件名+cid」拼成，对应 data/official_event/通用.csv 的 cid=1。
    ⚠️ 这是**数据键**不是显示文本，绝不能包 `_()`——包了就再也对不上事件表 """
ADULT_MEMORIAL_EVENT_UID = "通用2"
""" 成年纪念的事件uid，紧跟在毕业典礼之后 """
SEMESTER_EVENT_SUB_KEY = 200
""" 期末事件的**保留**子桶键（对应 data/official_event/期末.csv 的 sub_key 列）。

    ⚠️ 绝不能用 0 或 101~104：get_candidate_event_list() 每天翻的正是
       (15, 0) 与 (15, 当前阶段) 这两个桶，期末事件写进去会天天被抽到。
       用一个日常池永远不会翻的键，期末事件就只能由学期结算显式推入。
    ⚠️ 于是期末事件的**阶段区分只能写进 premise**（CVP_A1_T|102_E_1 等），
       不能像日常养成事件那样靠 sub_key 分桶 """

# ==== 15. 面板显示与排版 ====
HISTORY_SHOW_MAX = 8
""" 养成履历最多列出的条数。养到成年会攒下几十条，全列出来会把总览面板顶爆 """
HISTORY_TEXT_MAX = 24
""" 履历里事件正文的截断长度，只留能认出是哪件事的开头 """
REPORT_CARD_PREV = "GROWTH_REPORT_PREV"
""" 成绩单往前翻一页的返回值。⚠️ 不能用中文按钮名做返回值——
    容器里同屏还有孩子页签，撞名会让点了张三跳到李四 """
REPORT_CARD_NEXT = "GROWTH_REPORT_NEXT"
""" 成绩单往后翻一页的返回值。⚠️ 同上，是内部哨兵值，不参与翻译 """
SELECT_STUDENT_RETURN = "EDU_SELECT_STUDENT"
""" 个人课表与养成总览里「选择学生」按钮的返回值（2026-09-09 取代了原来每页 8 人的人名页签栏，见二期方案 §9.2.5）。
    ⚠️ 与 REPORT_CARD_PREV 同一做法：内部哨兵、不翻译，同屏还有容器页签与成绩单翻页，
       用中文按钮名做返回值留有撞名的余地 """
COLUMN_INDENT = "  "
""" 模板表每行的前导缩进，表头与数据行必须用同一个。⚠️ 是排版用的空白，不参与翻译 """
COLUMN_WIDTH_ID = 4
""" 模板表「编号」列的显示列宽 """
COLUMN_WIDTH_NAME = 10
""" 模板表「模板名」列的显示列宽。最长的预设模板名「学业优先」「玩乐优先」占8列 """
TEMPLATE_NAME_MAX = 10
""" 新建/重命名模板时允许输入的最大长度。
    ⚠️ 与 COLUMN_WIDTH_NAME 对齐：模板表的名字列宽是10显示列，
       输入更长的名字会把后面三个时段列整体挤右，一行对不齐 """
COLUMN_WIDTH_SLOT = 20
""" 模板表三个时段列各自的显示列宽。
    ⚠️ pad_display_width 不截断，列宽必须≥该列最长内容：
       娱乐名最长的是「上课（无课时自习）」，占18显示列（len() 只有9） """
