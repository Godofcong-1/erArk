# 检查清单

每条检查是一条不变量：健康的游戏状态应当满足的命题。检查按领域分模块，编号前缀即类别。下方各表的“说明”一列取自检查函数文档字符串“功能”一节的首句，完整表述以代码为准。

| 类别 | 模块 | 数量 |
|---|---|---:|
| CORE 核心 | `check_core.py` | 2 |
| BEHAV 行为与时钟 | `check_behavior.py` | 21 |
| BODY 服装与身体 | `check_body.py` | 34 |
| EDU 养成 | `check_education.py` | 12 |
| HGROUP H 与群交 | `check_h_group.py` | 31 |
| ISLAND 罗德岛经营 | `check_island.py` | 33 |
| MIND 意识 | `check_mind.py` | 30 |
| NUM 数值范围 | `check_numeric.py` | 30 |
| OBS 可观察矛盾 | `check_observable.py` | 17 |
| OFFICIAL 公务事件 | `check_official.py` | 2 |
| PLACE 位置与场景 | `check_place.py` | 31 |
| ROSTER 名册 | `check_roster.py` | 33 |
| BIRTH / COOK 设置记忆 | `check_setting.py` | 4 |
| SUPP 补充盲点 | `check_supplement.py` | 8 |
| 合计 | | 288 |

## CORE：核心

玩家与角色索引的基本一致性，也是框架管线可用性的探针。

| 编号 | 名称 | 说明 |
|---|---|---|
| CORE-01 | 角色索引一致性 | cache.npc_id_got（已拥有的干员id集合）中的每个id都能在cache.character_data（角色对象数据缓存组）中找到对应角色对象， 避免出现"已拥有但无角色数据"的野指针式状态 |
| CORE-02 | 交互对象有效性 | cache.character_data中每个角色的target_character_id（角色当前交互对象id）指向的角色确实存在于character_data中 |

## BEHAV：行为与时钟

角色行为（Behavior）、全局时钟、结算主循环的状态标记。

| 编号 | 名称 | 说明 |
|---|---|---|
| BEHAV-01 | 角色字典键与角色自身cid一致 | cache.character_data的字典键与角色对象自身的cid一致 |
| BEHAV-02 | 全局时钟健全性 | cache.game_time/cache.pre_game_time都是已初始化的朴素datetime且只保留到分钟 |
| BEHAV-03 | 世界月份只能是四季月 | cache.game_time与cache.pre_game_time的月份都属于四季月{3,6,9,12} |
| BEHAV-04 | 上一循环时间不得晚于当前时间 | cache.pre_game_time不晚于cache.game_time |
| BEHAV-05 | 跨日刷新已经完成 | 若game_time与pre_game_time的日期不同，说明主循环的跨日刷新(比较日期并调用每日刷新，把 pre_game_time推到当前)钩子处仍未完成，今日事件记录/每日计数器等都没清 |
| BEHAV-06 | 更新流程嵌套深度必须归零 | cache.game_update_flow_running恒为0 |
| BEHAV-07 | 行为核心字段类型正确 | 每个被调度角色的behavior有字符串id、朴素datetime起时、非布尔整数分钟数 |
| BEHAV-08 | 当前行为id必须已注册 | 每个被调度角色的behavior_id都能在game_config.config_behavior(键为en_name)中查到 |
| BEHAV-09 | 运行中行为时长为非负整数 | 每个被调度角色的behavior.duration是非负整数 |
| BEHAV-10 | 活动角色的行为起时不得是哨兵 | 每个被调度角色的behavior.start_time不是哨兵0001-01-01 |
| BEHAV-11 | 行为起时不得晚于游戏时间 | 每个被调度角色的behavior.start_time不晚于cache.game_time |
| BEHAV-12 | 不得残留已过期的行为 | 非H、duration>0的被调度角色，其行为结束时间END()不早于cache.game_time |
| BEHAV-14 | 移动行为必须带着可执行的路径 | behavior_id为move的角色带着可执行的路径快照 |
| BEHAV-15 | "谁在跟我互动"的记录必须指向真实角色 | 每个角色的action_info.interacting_character_end_info[0]（结算交互行为时写进对方的"发起方id"） 要么是哨兵-1，要么指向character_data中真实存在的角色 |
| BEHAV-16 | 生效中的身体道具不得已过期 | h_state.body_item中"生效中(item[1]为真)"的道具，其结束时间item[2]要么为None要么晚于 cache.game_time |
| BEHAV-17 | 二段行为取值与待结算id合法 | second_behavior(二段行为id→0/1触发标记字典)的取值只能是0或1的int，以及 must_settle_second_behavior_id_list/must_show_second_behavior_id_list两个待处理id列表中的每个id都在 game_config.config_behavior_effect_data中——must_settle_check()与must_show_talk_check()都会无保护地 下标该配表，键错即KeyError |
| BEHAV-18 | 行为历史队列有界且条目可比 | last_behavior_id_list是长度在[1,5]的list，且每个元素要么是0要么是字符串 |
| BEHAV-19 | 时停中玩家必须处于时停无意识态 | time_stop_mode为真时，0号玩家的sp_flag.unconscious_h必须等于3(时停语义) |
| BEHAV-20 | 群交模式必须有玩家在H中 | cache.group_sex_mode为真时，0号玩家的sp_flag.is_h必须为真 |
| BEHAV-21 | 完成集合里只能是存在的角色id | cache.over_behavior_character(结算完成集合)是set，且其中每个元素都是int且指向character_data中 真实存在的角色 |
| BEHAV-22 | 行为起时落在四季月上 | 每个被调度角色(排除哨兵值)的behavior.start_time月份属于四季月{3,6,9,12} |

## BODY：服装与身体

服装四容器、污浊、妊娠、身体素质。BODY-01/10/31 是形状前置条件，形状不成立时后续检查跳过对应条目而不二次报错。

| 编号 | 名称 | 说明 |
|---|---|---|
| BODY-01 | 服装四容器的部位键完整 | 每个角色的穿着/脱下/大浴场衣柜/宿舍衣柜四表都按全部服装类型建键且值为list； 运行期到处裸下标访问这些表，缺键即KeyError |
| BODY-02 | 服装id有效且在正确槽位 | 四容器内所有元素都是配置中存在的服装模板id（非0占位），且模板的clothing_type等于所在槽位号 |
| BODY-03 | 同一槽位内不得有重复服装id | 同一容器同一槽位的列表内无重复模板id；重复说明某条穿戴路径重复append， 会造成重复显示、重复移除、特殊装备叠加 |
| BODY-04 | 穿着与脱下不应相交 | 同一槽位的cloth_wear与cloth_off无交集 |
| BODY-06 | 角色专属服装不得出现在他人处 | 专属服装（模板npc字段非0）只出现在adv与之相符的角色身上或衣柜里 |
| BODY-07 | 内衣可见性字典形状 | cloth_see必须含6(胸衣)与9(内裤)两个被裸下标访问的键，偷袜子会合法加入10；键为int，值严格为bool |
| BODY-08 | 装备情况数值有界 | equipment_condition为有限数值且在[-4, 2]内 |
| BODY-09 | 装饰避孕套挂点合法 | condom_decoration的键为(部位类型,部位cid)二元组：类型0只允许头发(0,0)；类型1必须是合法服装部位 且该部位当前有衣服；值为非负数值列表（允许空列表） |
| BODY-10 | 精液记录表键集与条目形状 | body_semen覆盖全部身体部位、cloth_semen覆盖全部服装部位（均被裸下标访问） |
| BODY-11 | 精液量非负 | 三张污浊表的当前量[1]与累计量[3]均非负，以及累计吸收量非负 |
| BODY-12 | 累计精液量不小于当前量 | 累计量[3]恒>=当前量[1] |
| BODY-13 | 精液等级与当前量同步 | 等级[2]等于以当前量[1]重算的纯函数结果（get_semen_now_level），不一致说明某处改量未刷新等级， 会让描述文本、灌肠量、受精率算错 |
| BODY-14 | 衣柜精液与在穿精液不得共享list对象 | cloth_semen[t]与cloth_locker_semen[t]不是同一个list对象 |
| BODY-15 | 兽部有精液则须有对应兽部素质 | 尾巴12/兽角13/兽耳14的当前精液量非零时角色必须持有对应素质113/112/111 （射精入口按素质拦截，有量无素质说明数据被别的路径写脏） |
| BODY-16 | 灌肠状态与容量配对 | a_clean∈{0..4}、enema_capacity∈{0..6}（上界以代码封顶为准，注释的1~5不准确）， 且正容量只应出现在「灌肠中1/精液灌肠中3」两个进行态 |
| BODY-17 | 精液流通表结构合法 | semen_flow每项含source(type/id)与targets；源类型0身体/1服装，目标类型0/1/2（2为环境滴落，id恒0）； remaining_volume为正整数 |
| BODY-18 | 玩家不应有精液流通 | 玩家(cid 0)的semen_flow恒为空列表——流通构造与实时结算的玩家分支都不处理流通表， 玩家身上出现流通项说明写错了对象 |
| BODY-19 | 无意识精液记录列表有效且去重 | body_semen_in_unconscious/cloth_semen_in_unconscious两列表元素为合法部位号int且无重复 （写入处用not in判重，重复即状态破损） |
| BODY-20 | 阴茎污浊字典键值 | penis_dirty_dict的键仅为"semen"/"blood"，值严格为bool；默认空dict合法 |
| BODY-21 | 生理周期日为配置内合法值 | reproduction_period是int且存在于config_reproduction_period（该值被直接当配置下标，越界即KeyError） |
| BODY-22 | 受精/妊娠/临盆三阶段互斥 | 素质20受精/21妊娠/22临盆至多持有一个（单向迁移，每次先清旧再置新，同持两个即状态机破裂） |
| BODY-23 | 产后/育儿互斥且须有可追溯的孩子 | 素质23产后与24育儿互斥；两者任一成立时child_id_list须为非空list且末位id存在于character_data （推进函数无保护读取child_id_list[-1]并索引character_data，… |
| BODY-24 | 怀孕中须有有效受精时间 | 处于素质20/21/22任一阶段的角色，其fertilization_time是有效datetime（非默认值年份1）且不晚于当前游戏时间 （阶段推进全靠该时间差，默认值或未来值会让角色瞬间跳到临盆或永远卡住） |
| BODY-25 | 孕肚素质与妊娠/临盆绑定 | 素质26孕肚成立当且仅当角色处于21妊娠或22临盆（进入妊娠时授予、分娩时移除） |
| BODY-26 | 乳汁量有界且上限为正 | milk/milk_max为有限数值、milk_max>0（被当分母，<=0会ZeroDivisionError）、0<=milk<=milk_max |
| BODY-27 | 涨奶标记蕴含泌乳素质 | lactation_flag为真时素质27必为1 |
| BODY-28 | 罩杯素质有且只有一个 | 非玩家、非机械体角色的罩杯素质121~125恰好持有一个（胸部成长函数假定必有其一， 缺失会UnboundLocalError，崩溃级） |
| BODY-29 | 臀/腿/足素质各组至多一个 | 126-128(臀)、129-130(腿)、131-132(足)三组互斥档位各至多持有一个 |
| BODY-30 | 动态女儿年龄阶段素质有且只有一个 | 动态女儿（cid!=0且relationship.father_id==0，即父亲为玩家的新生角色）的年龄阶段素质101~107 恰好持有一个（108长生者可叠加体质不参与） |
| BODY-31 | 素质字典完整且取值为0/1 | talent字典覆盖config_talent全部键（全库大量裸下标访问，缺键即KeyError），键为int、值为int且取值0/1 |
| BODY-32 | 精液流通源须仍有可扣减的容器 | semen_flow中源为服装部位(类型1)的条目，其源槽位当前必须有衣服——结算先给目标加量再对源扣量， 源槽已无衣服时扣量函数提前return，导致凭空复制精液 |
| BODY-33 | 机械体妊娠须有生育模组 | 机械体(race==2)角色处于素质20/21/22/26任一阶段时必须持有素质171生育模组 （受精入口对无模组机械体显式拦截并清零受精率，无正常产生路径） |
| BODY-34 | 产后/育儿所引用的孩子须有有效出生时间 | 处于素质23/24阶段的角色，其末位孩子的born_time是有效datetime（非默认年份1）且不晚于当前游戏时间 （阶段推进直接用该时间算天数，默认值会让状态瞬间跨过阈值） |
| BODY-35 | 个人服装模板列表有效 | clothing_tem为有效服装模板id组成的list |

## EDU：养成

照料、性格倾向、胎教、出勤、学期、成绩单、课表与模板。

| 编号 | 名称 | 说明 |
|---|---|---|
| EDU-01 | 照料值 | 照料值须为有限非负数 |
| EDU-02 | 性格倾向 | 性格倾向须为dict，键为0–3，值有限，允许负值与缺键 |
| EDU-03 | 胎教值 | 检查全角色妊娠与已有养成记录的胎教值及常量上限 |
| EDU-04 | 出勤累计 | 出勤、缺课和翘课累计为非负整数，翘课不超过缺课 |
| EDU-05 | 学期基线 | 学期出勤、缺课基线须为非负整数且不超过对应累计 |
| EDU-06 | 学期号 | 学期号为空列表或[整数年,季月]，不要求等于当前学期 |
| EDU-07 | 成绩单快照 | 成绩单年份、季月、出缺勤与整数百分比，超出历史上限只警示 |
| EDU-08 | 全局课表结构 | 全局课表按星期、节次存[能力id,教师id]，教师可为-1，不要求在场或在岗 |
| EDU-09 | 个人课表结构 | 个人课表按课型检查场景名、娱乐配置id或岗位配置id |
| EDU-10 | 模板与覆盖槽 | 模板slot和角色覆盖表，空模板合法 |
| EDU-11 | 模板引用 | 角色模板引用须为0或当前模板表内的键 |
| EDU-12 | 课时去重标记 | 出缺勤去重标记须为空列表或[正整数日期序数,0–8节次] |

## HGROUP：H 与群交

H 状态、群交模式、逆推、隐奸。

| 编号 | 名称 | 说明 |
|---|---|---|
| HGROUP-01 | 群交模式蕴含玩家在H | cache.group_sex_mode为真时玩家必然带is_h标记：所有真正开启群交的效果链都同时给玩家挂462； 若同时命中HGROUP-02，还存在群交模式与同场景在H的NPC人数不一致；本条不推断具体退出路径 |
| HGROUP-02 | 群交模式需满足场内在H的NPC人数 | 普通群交需同场景至少2名在H的NPC；性技实操课使用群交模式，但允许仅1名学生 |
| HGROUP-03 | 非群交时玩家群交模板必须为空 | 群交模式关闭时玩家A/B两套群交模板均已清空 |
| HGROUP-04 | 群交模板结构固定 | 玩家群交模板字典恰含A/B两键，每套为[单槽字典,侍奉项]，单槽字典恰含5个部位键、每个单槽 是长度2的列表，侍奉项是[list,state_id] |
| HGROUP-05 | 模板槽位不得半填 | 单槽[对象id,指令id]不允许只填一半，侍奉项同理(有指令⇔列表不是[-1]) |
| HGROUP-06 | 阴茎插入与侍奉互斥 | 同一模板内penis槽与侍奉槽不能同时被占用 |
| HGROUP-07 | 侍奉槽结构与去重（不含人数上限） | 侍奉项要么是占位态[[-1],-1]，要么是"≥1个互不重复、均非-1的角色id + 非-1指令id" |
| HGROUP-08 | 模板中的角色必须是已获得NPC、在H、且同场景 | A/B模板中出现的每个非-1角色id，必须是已获得的非玩家角色，且正处于H并与玩家同场景 |
| HGROUP-09 | 模板指令id必须存在且匹配所占部位 | 每个非-1的指令id必须存在于game_config.config_behavior，且属于该槽位对应的分组： mouth→口、L_hand/R_hand→手、penis→插入、anal→肛、侍奉槽→侍奉 |
| HGROUP-10 | 群交控制字段的值域与所有权 | 三个群交全局开关只从玩家身上读写：玩家npc_ai_type_in_group_sex只能是0..3，两个flag必须是 bool，NPC身上必须保持默认值 |
| HGROUP-11 | NPC自身的群交模板必须为空 | 群交模板虽挂在所有角色h_state上，但业务上只读写玩家(cid=0)的模板；NPC模板出现非空槽 即为串写或旧状态未清 |
| HGROUP-12 | 「群交自慰」标记的成立条件 | sp_flag.masturebate==3只能出现在群交开启、在H、与玩家同场景的非玩家角色身上 |
| HGROUP-13 | 玩家不得带有「前往参与群交」标记 | 玩家sp_flag.go_to_join_group_sex恒为False：该标记是给"被邀请、正从远处赶来"的NPC用的， 置位点只有群交邀请面板与SELF_JOIN_GROUP_SEX_ON，都作用在被邀请的NPC上，玩家自己永远不该带 |
| HGROUP-14 | 「前往参与群交」标记的生命周期 | [warning已知泄漏探测器] 带go_to_join_group_sex标记的NPC应处在"群交仍开着、自己尚未进入H、 尚未到达玩家场景"的途中状态 |
| HGROUP-15 | 隐奸模式必须双向一致且至多一对 | [warning已知bug探测器] 进入隐奸时玩家与对象被写入同一个hidden_sex_mode值，隐奸恒为"玩家+ 恰好一名NPC"的对称状态 |
| HGROUP-16 | 隐奸对象在H；模式1/2时玩家不在H | ask_hidden_sex带464使对象进入H；选择模式1/2(博士不隐藏)时面板会主动清掉玩家自己的H 标记 |
| HGROUP-17 | 隐奸与群交互斥（玩家侧） | 玩家不能同时处于隐奸和群交 |
| HGROUP-18 | 隐奸发现度：0..100，且只有玩家可能非0 | 隐蔽值只对角色0结算并被夹在[0,100]，NPC身上出现非0值即为错误写入 |
| HGROUP-19 | 露出模式必须双向一致且至多一对 | 选择露出模式时双方被写入同一个值，且入口效果链让双方都进入H；露出恒为"玩家+至多一名 NPC"的对称状态，与隐奸不同，露出侧"双方is_h"是真命题 |
| HGROUP-20 | 露出与群交互斥（玩家侧） | 玩家不能同时处于露出和群交 |
| HGROUP-21 | 隐奸/露出模式值域 | hidden_sex_mode与exhibitionism_sex_mode都只能是0..4 |
| HGROUP-22 | 在H的NPC必须与玩家同场景 | 本作所有H都以玩家为中心，离开玩家场景的NPC会在NPC行为循环里被强制退出H |
| HGROUP-23 | 玩家在H时场内必须有在H的NPC | 普通H(非群交、非隐奸、非时停)中玩家的H标记必然伴随至少一名同场景的在H NPC——所有给玩家 挂462的行为都同时给对象挂464 |
| HGROUP-24 | 逆推标记必须在H、同场景、且不在群交中 | h_state.npc_active_h(NPC主动逆推)是H内局部状态，只可能出现在非玩家、在H、非群交、 (非时停时)同场景的角色身上 |
| HGROUP-25 | 催眠行为模式互斥（木头人/逆推） | 每次开启某个催眠行为模式前都会先clear_hypnosis_behavior_mode复位全部模式，木头人与逆推 不可能同时为真 |
| HGROUP-26 | 无意识H档位值域 | unconscious_h取值只能是0..7([0否,1睡眠,2醉酒,3时停,4平然,5空气,6体控,7心控]) |
| HGROUP-27 | 时停开关与unconscious_h==3双向一致 | 开启时停会给ALL全员(含玩家自己)写unconscious_h=3，关闭时全员写0，除时停外没有第二处写3 |
| HGROUP-28 | 装睡必须建立在睡奸醒来状态上 | h_state.pretend_sleep=True必须同时满足sp_flag.sleep_h_awake=True、 sp_flag.unconscious_h==1、sp_flag.is_h=True |
| HGROUP-29 | 「为玩家逆推而自慰」与去洗手间/宿舍自慰互斥 | 状态机在"去找玩家逆推"和"找地方自慰"之间二选一，两者不能同时成立 |
| HGROUP-30 | 体位字段的值域与「仅博士持有」 | 玩家current_sex_position/pre_sex_position只能是-1或1..12，current_womb_sex_position只能 是0..2 |
| HGROUP-31 | 完全脱离H的角色不应残留H局部状态 | 既不在H、也不在隐奸/露出/无意识H中的角色，其插入位置、逆推标记、性爱助手、装睡、寸止、绳缚等H内局部 字段必须已归零；寸止徽章与绳缚描述会直接显示在角色标签/身体面板，绳缚残留还会持续参与每回合结算 |

## ISLAND：罗德岛经营

`cache.rhodes_island` 及其派生结构：岗位集合、设施等级与开放表、资源仓储、生产线、宿舍管理、图书、派对、动力区、外勤委托。

| 编号 | 名称 | 说明 |
|---|---|---|
| ISLAND-01 | 干员名单引用完整性 | cache.npc_id_got中的每个id都存在于cache.character_data，且0号玩家角色存在 |
| ISLAND-02 | 设施等级键完整且落在配置区间 | 当前配置的每个设施都在facility_level中有等级记录，且等级是int、落在该设施效果表的合法下标区间 |
| ISLAND-03 | 非控制中枢设施等级不超过中枢等级+1 | 除控制中枢(cid 0)自身外，任一设施等级不得高于控制中枢等级+1 |
| ISLAND-04 | 设施开放表键完整、值为0/1语义 | 当前配置的每个可开放设施都在facility_open中有开放记录，值必须是True/False或语义等价的1/0 |
| ISLAND-05 | 资源表键完整且库存为非负整数 | 当前Resource.csv的每种资源都在materials_resouce中有库存记录，值必须是非负int |
| ISLAND-06 | 仓库容量与干员上限是设施等级的派生值 | warehouse_capacity == 仓储区(cid 3)当前等级效果 + 已用仓储扩展模块数*200， people_max == 宿舍区(cid 4)当前等级效果 |
| ISLAND-07 | 已招募干员的岗位id必须合法 | 每个在编非玩家干员的work.work_type存在于WorkType.csv |
| ISLAND-08 | 岗位集合键完整、成员合法且与自身键自洽 | all_work_npc_set的键必须等于岗位配置全集；集合里的每个id必须是存在的角色，且其work.work_type 必须等于所在集合的键 |
| ISLAND-09 | 岗位集合与在编名单的逐人重算一致 | 按当前在编名单逐人重算的岗位集合应与缓存一致 |
| ISLAND-10 | 在岗人数计数可由岗位集合重算 | work_people_now必须等于所有非0岗位集合的规模之和 |
| ISLAND-11 | 岗位人员列表引用合法、无重复、不漏在岗者 | 六个岗位派生列表的成员必须是存在的角色且岗位匹配、列表内不得重复；每个列表必须包含对应岗位集合 的全部成员（漏人=真bug） |
| ISLAND-12 | 岗位人员列表的离线残留漂移 | 五个增量维护的岗位列表应与对应岗位集合严格相等；出现多余成员说明列表在两次刷新之间 滞后于成员实际状态 |
| ISLAND-13 | 流水线结构、数量与配方id合法 | 制造加工区(cid 12)等级N恰好开放0..N-1号流水线；每条记录是长度5的list，当前配方与待切换配方都是 合法配方id，结算小时在0..23 |
| ISLAND-14 | 农业线与招募线结构、种植类型合法 | 药田线与温室线每条是长度5的list，种植类型只能是0(停种)或该线唯一允许的资源——药田11、温室16； 招募线每条至少4项 |
| ISLAND-15 | 各生产/招募/交易线主负责人有效、岗位匹配、同类不重复 | 流水线(岗位121)、药田(161)、温室(162)、招募线(71)的主负责人槽位与各资源类型主交易员(111)必须是 0或一名存在的角色，岗位须与该线要求一致，且必须在对应岗位人员列表中；同类线内一人不得同时主理两条 |
| ISLAND-16 | 宿舍管理员表结构与引用合法 | dormitory_managers的键只能是1..9层；值是0(未任命)或一名存在的角色；同一人不得同时管理两层 |
| ISLAND-17 | 宿舍管理员岗位联动与层键覆盖 | 每个被任命的管理员的work.work_type应为31，且1..9层键应齐全 |
| ISLAND-18 | 已关闭楼层不得保留管理员 | 层号高于当前宿舍区等级理论开放上限的层，其管理员必须为0 |
| ISLAND-19 | 已招募干员的宿舍路径必须是合法场景 | 每个在编非玩家干员的dormitory必须非空且是cache.scene_data的合法键，不得残留""或模板值"无" |
| ISLAND-20 | 普通宿舍房间不超过2人 | 普通宿舍房设计容量2人；超员说明分配逻辑或特殊搬迁把人塞进了满房 |
| ISLAND-21 | 借书记录双向一致且不超借阅上限 | book_borrow_dict[book]=借阅者id(-1未借出，0为玩家)与角色的entertainment.borrow_book_id_set必须 互为反向索引；书籍id必须合法；单人持书不超过3本 |
| ISLAND-22 | 一周派对排期键值合法且同一娱乐不占两天 | party_day_of_week必须是dict、键恰为0..6，值为合法娱乐id(0表示无活动)，且同一非零娱乐id不得同时 占据两天 |
| ISLAND-23 | 干员娱乐安排固定三项且id合法 | 每个角色的entertainment.entertainment_type必须是长度恰为3的list，每项都是Entertainment.csv中的 合法cid(0=无) |
| ISLAND-24 | 自动交易设置键与阈值合法 | 每个自动交易资源id必须存在于资源配置；设置字典必须含六个标准键；库存阈值在0..仓库容量，价格 百分比在0..300，开关是0/1或True/False |
| ISLAND-25 | 载具在外数量与进行中委托占用一致 | 每种载具记录形如[总数,外勤中数量]，满足0<=外勤中<=总数，且"外勤中"精确等于所有进行中委托占用 该型载具的台数之和；委托引用的载具型号必须同时存在于配置与载具表 |
| ISLAND-26 | 外勤派遣名单与干员外勤标记一致 | 每个进行中委托的id必须合法；成员必须是存在的角色、不被两个委托同时派遣、其sp_flag.field_commission 等于该委托id；反过来，任何field_commission!=0的角色都必须恰好出现在对应委… |
| ISLAND-27 | 储能与供能设施结构、绝对范围合法 | 当前储能落在[0, power_storage_max]；三个供能列表结构固定(副反应炉2项、其他清洁能源3项、蓄电池 3项)；所有数量与已用扩展位计数非负 |
| ISLAND-28 | 主供能调控员槽位有效且不重复 | main_power_facility_operator_ids是固定4槽(火/水/风/光)，每个非0值必须是存在的角色且 work.work_type==11，四槽互不重复 |
| ISLAND-29 | 监狱长引用与囚犯数据自洽 | current_warden_id为0或指向一名存在的、work.work_type==191的角色；每个囚犯id必须存在，逃脱概率 落在0..100 |
| ISLAND-30 | 设施损坏数据与检修分派自洽 | facility_damage_data的键必须是合法场景路径、值为正整数(<=0时代码会pop)；maintenance_place的键 必须是存在的、work.work_type==21的角色，值必须是合法场景路径 |
| ISLAND-31 | 访客集合与待确认招募集合合法 | visitor_info是dict，键均为存在的角色，访客数不超过visitor_max；recruited_id是集合、不含0、 成员均存在，且与已招募名单不相交 |
| ISLAND-32 | 贸易子设施列表与开放表一致、不超上限、无重复 | shop_open_list无重名、长度不超过贸易区(cid 11)当前等级效果值，且其中每个名称都对应一个贸易区 可建设施且该设施已开放 |
| ISLAND-33 | 外交官映射、岗位与外派标记三方一致 | diplomat_of_country[国家][0]的非零角色必须存在、sp_flag.in_diplomatic_visit等于该国家、 work.work_type==131，且一人不得同时负责两国 |

## MIND：意识

时间停止、催眠深度与类型、角色扮演、异常位掩码 5/6、睡眠与装睡、熟睡值。

| 编号 | 名称 | 说明 |
|---|---|---|
| MIND-01 | 时停开启时玩家处于时停无意识 | TIME_STOP_ON把npc_id_got\|{0}全部置为3之后，玩家侧没有任何"上线重置"之类的合法例外路径； 时停开着而玩家unconscious_h不是3，意味着有非指令路径改写了玩家意识状态 |
| MIND-02 | 时停开启时已登场干员处于时停无意识 | 时停开启时全体已登场干员的unconscious_h均为3；漏掉的干员会被AI与指令前提当作可正常交互对象 |
| MIND-03 | 时停关闭后不得残留时停无意识 | TIME_STOP_OFF在同一次结算里先关time_stop_mode再清零npc_id_got\|{0}的unconscious_h |
| MIND-04 | 时停开启需要玩家持有窄域时停素质 | 时停开启时玩家持有素质316(唯一正常入口PRIMARY_TIME_STOP读素质316)； 时停开着而玩家没有316，说明状态来自读档迁移/mod/debug |
| MIND-05 | 时停搬运/自由活动字段在正常游戏中恒为零 | pl_ability.carry_chara_id_in_time_stop与pl_ability.free_in_time_stop_chara_id恒为0 |
| MIND-06 | 时停开启时不应残留时停解放标记 | time_stop_mode开启时，全体存活的已登场干员h_state.time_stop_release均为False |
| MIND-07 | 被搬运的干员必须存在且与玩家同地点 | pl.action_info.carry_chara_id指向的角色存在、未死亡且与玩家同地点 |
| MIND-08 | 催眠深度值域 | hypnosis.hypnosis_degree为非bool数值且落在[0, 200]内 |
| MIND-09 | 催眠类无意识状态需要对应的催眠深度 | unconscious_h∈{4,5,6,7}(平然/空气/体控/心控)时催眠深度达到对应门槛(50/100/200/200， Hypnosis_Type.csv) |
| MIND-10 | 被催眠素质不早于深度阈值 | 干员的被催眠素质71/72/73分别在深度达到50/100/200时才可能持有(Hypnosis_Talent_Of_Npc.csv) |
| MIND-11 | 被催眠素质需要玩家持有对应前置素质 | npc_gain_hypnosis_talent授予71/72/73前分别校验玩家的331/332/334(handle_talent.py) |
| MIND-12 | 玩家催眠/时停素质链自洽 | 玩家素质链332←331、333←332、334←333(Hypnosis_Talent_Of_Pl.csv)、317←316、318←317 (Talent_Of_Arts.csv)不存在跳级持有 |
| MIND-13 | 三种催眠行为模式互斥 | 木头人blockhead/逆推active_h/角色扮演roleplay三个"行为主模式"至多一个生效 |
| MIND-14 | 体控无意识必须由木头人或逆推支撑 | unconscious_h==6(体控)时hypnosis.blockhead或hypnosis.active_h至少一个为真 |
| MIND-15 | 心控无意识必须有角色扮演项 | unconscious_h==7(心控)时hypnosis.roleplay非空 |
| MIND-16 | 角色扮演列表的形状与内容合法 | hypnosis.roleplay是list，元素为正整数且均属于game_config.config_roleplay，且无重复 |
| MIND-17 | 体控/心控子项需要「被完全催眠」素质 | 六个体控/心控子项(增加敏感度/强制排卵/木头人/逆推/角色扮演/苦痛快感化)任一为真时角色必须 持有素质73(被完全催眠) |
| MIND-18 | 空气催眠者必须与玩家同处已记录的催眠地点 | 全体unconscious_h==5(空气催眠)的角色的position都等于共享锚点pl_ability.air_hypnosis_position 且等于玩家当前position |
| MIND-19 | 空气催眠地点必须处于锁门状态 | unconscious_h==5的角色所在场景close_type==1(可锁门)且close_flag!=0(已锁门) |
| MIND-20 | 空气催眠地点记录的形状可解析 | pl_ability.air_hypnosis_position为""，或为可解析成合法场景的字符串list |
| MIND-21 | 玩家当前催眠类型合法且已解锁 | pl_ability.hypnosis_type∈{0,1,2,3,4}，且1需素质331、2需333、3/4需334(Hypnosis_Type.csv的 talent_id列) |
| MIND-22 | 无意识状态取值域 | sp_flag.unconscious_h∈[0,7] |
| MIND-23 | 睡眠行为与角色状态ID对齐 | behavior.behavior_id=="sleep"时state==111 |
| MIND-24 | 熟睡值值域 | sleep_point为非bool数值且落在[0,100]内(Sleep_Level.csv最高档上限100) |
| MIND-25 | 睡眠无意识必须依附睡眠行为或装睡 | unconscious_h==1(睡眠)时behavior_id=="sleep"或h_state.pretend_sleep为真 |
| MIND-26 | 异常位掩码5/6不得与意识状态相矛盾 | 时停模式/unconscious_h==3/5时若已知第6位则必须为异常，unconscious_h==4时若已知第5位则 必须为异常 |
| MIND-27 | 睡眠异常位与可推导的睡眠等级一致 | 正在睡眠(behavior_id=="sleep")或处于睡眠无意识(unconscious_h==1)的角色，已知的异常位5/6 与熟睡等级一致：sleep_point<=30(等级0，半梦半醒)时第5位应为异常，>30(等级>=1)时第6位应为异常 (handle_premise/__init__.py，0档上限30来自Sleep_Level.csv) |
| MIND-28 | 时停高潮计数结构合法 | h_state.time_stop_orgasm_count是dict，键为int、值为非负整数 |
| MIND-29 | 睡眠计划时分字段合法 | action_info.plan_to_sleep_time与plan_to_wake_time均为[时,分]形状的二元int列表， 小时0-23、分钟0-59 |
| MIND-30 | 装睡标记在当前版本不应出现 | h_state.pretend_sleep恒为False |

## NUM：数值范围

角色六大数值字典（ability/experience/juel/status_data/talent/favorability）的键集与取值范围，以及基地资源等全局数值。

| 编号 | 名称 | 说明 |
|---|---|---|
| NUM-01 | 数值容器字段存在且为dict | 六个数值字典字段(ability/experience/juel/status_data/talent/favorability)在每个角色对象上都存在且 类型为dict |
| NUM-02 | 能力字典键集覆盖配表且键为纯int | config_ability的每个id都在chara.ability中存在（配表⊆角色，方向不可颠倒——补零与迁移只补不删， 角色⊆配表或键集相等的方向会在每份升级存档上每回合误报），且chara.ability的键类型均为精确int （避免Python集合里True==1、1.0==1造成的伪装键） |
| NUM-03 | 能力值必须是Ability_Lv_Adjust的合法键 | chara.ability的每个值都是config_ability_lv_adjust中的合法键（配表键仅0-10） |
| NUM-04 | 能力等级不超过8（事件白名单除外） | chara.ability的值不超过8（自动升级循环硬停在8） |
| NUM-05 | 感度/扩张类能力与角色性别一致 | sex_need标注为0(男)/1(女)的能力，对性别不符的角色应恒为0（自动升级明确跳过不符项） |
| NUM-06 | 角色性别取值域 | chara.sex只能是0或1 |
| NUM-07 | 经验字典键集覆盖配表且键为纯int | config_experience的每个id都在chara.experience中存在（配表⊆角色），键类型均为精确int |
| NUM-08 | 经验为非负整数 | chara.experience的每个值都是非负整数 |
| NUM-09 | 宝珠字典键集覆盖配表且键为纯int | config_juel的每个id都在chara.juel中存在（配表⊆角色），键类型均为精确int |
| NUM-10 | 宝珠为非负整数 | chara.juel的每个值都是非负整数 |
| NUM-11 | 素质字典键集覆盖配表且值为int | config_talent的每个id都在chara.talent中存在（配表⊆角色），键与值类型均为精确int（排除bool） |
| NUM-12 | 状态值字典键集覆盖配表且键为纯int | config_character_state的每个id都在chara.status_data中存在（配表⊆角色），键类型均为精确int |
| NUM-13 | 状态值为非负整数 | chara.status_data的每个值都是非负整数 |
| NUM-14 | 状态值不超过99999 | chara.status_data的每个值不超过99999 |
| NUM-15 | 好感键有效且必含玩家 | 本域唯一方向为"角色⊆全局"的键集检查：校验chara.favorability的每个目标id都必须是cache.character_data 中现存角色，且必须含键0（玩家）——能力升级需求F<n>与事件通道均裸取/裸写favorability[0] |
| NUM-16 | 好感值为整数 | 只检查chara.favorability值的类型为int，不设上下界 |
| NUM-17 | 信赖与催眠程度为有限实数 | chara.trust与chara.hypnosis.hypnosis_degree都是类型合法(int/float)且有限(非NaN/inf)的实数 |
| NUM-18 | 体力/气力上限为正整数 | hit_point_max/mana_point_max均为正整数 |
| NUM-19 | 玩家专属槽位上限为正整数 | 仅校验cid 0（玩家）的sanity_point_max/eja_point_max/semen_point_max均为正整数，且sanity_point_max<=9999 |
| NUM-20 | 当前体力在[1,上限] | chara.hit_point在[1, hit_point_max]范围内（力竭底线为1而非0） |
| NUM-21 | 当前气力在[0,上限] | chara.mana_point在[0, mana_point_max]范围内 |
| NUM-22 | 当前理智在[0,上限] | chara.sanity_point在[0, sanity_point_max]范围内 |
| NUM-23 | 射精槽非负且不设上限 | chara.eja_point非负，不检查<=eja_point_max——槽满时"忍住射精"会直接return，合法保留 eja_point>=eja_point_max |
| NUM-24 | 精液槽与临时精液槽范围 | chara.semen_point在[0, semen_point_max]，chara.tem_extra_semen_point在[0, semen_point_max*4] |
| NUM-25 | 基地资源键集覆盖配表且为非负整数 | config_resouce的每个id都在cache.rhodes_island.materials_resouce中存在（配表⊆资源，方向同NUM-02—— 存档迁移只补不删已下线的资源id，多余键合法），且键为精确int、值为非负整数（各面板按固定id裸下标， 没有任何统一的max(0,...)兜底，负资源意味着某条支付路径漏判） |
| NUM-26 | 仓库容量为非负整数 | cache.rhodes_island.warehouse_capacity为非负整数 |
| NUM-27 | 疲劳/饥饿/熟睡/醉酒在各自量程内 | tired_point∈[0,160]、hunger_point∈[0,240]、sleep_point∈[0,100]、drunk_point∈[0,100] |
| NUM-28 | 尿意值非负且为整数 | chara.urinate_point为非负整数 |
| NUM-29 | 角色尿意值不超过300 | 所有角色（含玩家cid=0）的urinate_point不超过300（设计上界，realtime_settle与 drunk_sex_common两处min(300,...)体现 |
| NUM-30 | 欲望值为非负整数且不设上限 | chara.desire_point为非负整数，不强制<=100——尽管字段注释称100为最大，逐日结算逐日累加且无任何 钳制，前提函数在>=100时权重仍随数值单调增长，说明设计上预期会超过100 |

## OBS：可观察矛盾

玩家能从指令面板、角色标签、身体面板直接看到的矛盾。

| 编号 | 名称 | 说明 |
|---|---|---|
| OBS-01 | 玩家不在H时同场不得有在H的NPC | 玩家完全退出普通H且不在隐奸/群交/时停时，同场 NPC 的 is_h 应已由结束链清零；健康存档的结束链对象一致，因此恒不命中 |
| OBS-02 | 玩家有性交体位时场内必须真有人被对应插入 | 玩家独占体位字段与场内 NPC 插入位置相互支撑；健康存档的体位切换与拔出链同步维护两侧字段，因此恒不命中 |
| OBS-03 | 完全脱离H的角色不得残留口球 | 检查完全脱离 H 的角色 body_item[14] 未仍处于装备状态；健康存档应在 H 重置时移除 H 装备，所以恒不命中 |
| OBS-04 | 透视或信息素开关开启时玩家必须持有对应素质 | 透视/信息素开关与其关闭指令所需基础素质一致；健康存档只能经持有素质的开启指令置位，所以恒不命中 |
| OBS-05 | 玩家的交互对象必须在当前场景名册里 | 指令面板轴心 target 与场景名册一致；健康存档中 Tk 会归一化目标，Web 也应只保留在场目标，装袋搬运是唯一明确例外 |
| OBS-06 | 同一角色不得同时处于隐奸模式与露出模式 | 检查同一角色的两种 H 分流模式不会同时大于零；健康存档的入口与结束链应保持模式互斥，因此恒不命中 |
| OBS-07 | 性爱助手结算必须满足监狱长约束 | 群交调教现场有非零监狱长，且 sex_assist 只落在该监狱长身上；健康存档的助手结算应只写当前监狱长，因此恒不命中 |
| OBS-08 | 醉酒型无意识H不得在醉酒值耗尽后残留 | 检查醉酒型无意识 H 不会在 drunk_point<=0 后继续残留；健康存档若来源消失就应同步退出该模式，因此恒不命中 |
| OBS-09 | 非群交下至多一名NPC处于阴茎插入中 | 玩家单一阴茎不会在普通 H 中同时记录插入多名 NPC；健康存档换位与拔出链会清旧对象，所以恒不命中 |
| OBS-10 | 异常位掩码第5和第6位的反向一致性 | 保守反向复算第5/6位来源，对照 handle_normal_5/6（Script/Design/handle_premise/__init__.py:1010-1058）： 睡眠项复用 MIND-27 已有的睡眠等级安全推导（attr_calculation.get_sleep_level，纯读）配合行为/unconscious_h==1 直读 |
| OBS-12 | 助理跟随服务开启时恢复正常的空闲助理必须在跟随 | 检查服务2开启后，非疲劳、非困倦、无生理意图、非H的空闲在线助理不会丢失跟随；健康存档的服务承诺应维持 is_follow=1，因此恒不命中 |
| OBS-13 | 非当前助理的角色助理服务位必须全为0 | 全量检查非玩家、非当前助理角色的已实装服务位均归零；健康存档在替换或取消助理时会清旧服务，因此恒不命中 |
| OBS-14 | 异常位掩码第4位必须与当前穿着重算一致 | 直读 cloth_wear 复算全裸或大致全裸，不调用会写掩码的 handle_normal_4；健康存档的换衣路径会同步刷新第4位，因此恒不命中 |
| OBS-15 | 异常位掩码第1位必须与基础生理来源重算一致 | 直读来源 flag 复算基础生理异常，不调用会写掩码的 handle_normal_1；健康存档在来源变化时同步更新缓存，因此恒不命中 |
| OBS-16 | 洗浴和游泳类行为必须发生在对应设施 |  NPC 当前洗浴/游泳行为与场景标签匹配；健康存档只会在带目标设施前提的状态机中启动行为，移动又会替换行为，因此恒不命中 |
| OBS-17 | 移动行为中的NPC必须带非空最终目的地 | 检查位置面板可见的移动行为拥有最终目的地；健康存档的寻路提交会同步填写该字段，抵达或取消时会退出移动行为，因此恒不命中 |
| OBS-18 | 绳缚值必须是合法配置键 | 防止 realtime_settle 以非法绳缚键直接索引 config_bondage 崩溃；健康存档只由绳缚面板写配置表中的合法键，因此恒不命中 |

## OFFICIAL：公务事件

公务事件队列与事件履历。

| 编号 | 名称 | 说明 |
|---|---|---|
| OFFICIAL-01 | 队列条目 | 检查队列及字段类型；角色引用失效单独警示 |
| OFFICIAL-02 | 事件履历 | 全局与角色履历条目须为dict，time为datetime，choice为非负整数 |

## PLACE：位置与场景

角色位置、场景名册、门锁、移动路径、收藏地点、宿舍、交互对象、助理、跟随、装袋搬运、教室。

| 编号 | 名称 | 说明 |
|---|---|---|
| PLACE-01 | 角色字典键与cid一致 | cache.character_data的每个字典键都等于该角色对象自身的cid字段，防止场景名册、交互目标、 助理引用等按字典键索引却指向身份不一致的对象 |
| PLACE-02 | 场景/地图自描述键一致 | cache.scene_data[k].scene_path == k 且 cache.map_data[k].map_path == k |
| PLACE-03 | 场景名册id必须存在 | 任一Scene.character_list中的id都必须是cache.character_data的键；名册全部写入点都只写已存在角色id， 无合法悬空来源 |
| PLACE-04 | 角色位置必须是现有场景 | cache.character_data中每个角色（全域，不限LIVE）的position拼成的路径必须是scene_data的键 |
| PLACE-05 | 角色→场景方向一致 | 每个在图角色（LIVE域）必须出现在自己position所指场景的character_list里 |
| PLACE-06 | 场景→角色方向一致 | 场景名册里的每个角色，其position必须正好指回该场景，抓"旧场景没删干净"的残影，与PLACE-05互补 |
| PLACE-07 | 角色不得同时出现在多个场景 | 同一角色id在所有Scene.character_list中最多出现一次 |
| PLACE-08 | 场景名册只容纳在册角色/离线角色必须退出名册 | 两个方向合成一条：(a) 任何场景名册成员必须是玩家或在npc_id_got中；(b) 带明确离线标记 （被装袋/外勤中/逃跑中）的角色必须已退出npc_id_got |
| PLACE-09 | 空房间不该锁着门 | close_flag != 0的场景其character_list不应为空 |
| PLACE-10 | 门类型与门状态枚举合法 | close_type ∈ {0,1,2}（无门/普通门/隔间门），且close_flag只能是0或本场景的close_type |
| PLACE-11 | 房间容量档位枚举合法 | room_area只能是0/1/2/3（对应满员判定的10/50/100/9999四档） |
| PLACE-12 | 移动路径字段必须是现有场景 | behavior.move_src/move_target/move_final_target只要非空，就必须拼成cache.scene_data的合法键 |
| PLACE-13 | 移动历史长度与内容合法 | action_info.past_move_position_list最多10条，每条都必须是合法场景路径 |
| PLACE-14 | 收藏地点必须是合法场景 | cache.collect_position_list每一项都是场景路径列表，必须存在于cache.scene_data； 否则地图收藏面板点一下就会跳进不存在的场景 |
| PLACE-15 | 宿舍字段必须是合法场景或哨兵值 | LIVE域内角色的dormitory（场景路径字符串）只允许是cache.scene_data的键，或未分配哨兵""/"无" |
| PLACE-16 | 交互对象id必须存在 | 每个角色的target_character_id必须是cache.character_data的键 |
| PLACE-17 | H状态角色的交互对象必须同场 | LIVE域内处于sp_flag.is_h的角色，其交互对象必须存在且与自己position相同 |
| PLACE-18 | 助理字段只属于玩家 | 只有id 0可以有非零assistant_character_id；NPC上非零都是脏数据（面板与前提只读玩家那一份， NPC上的值永远失效却会随存档迁移传播） |
| PLACE-19 | 当前助理必须有效且在线 | pl.assistant_character_id非0时，该id必须存在于character_data、在npc_id_got中、未死亡、 且不带任何离线标记 |
| PLACE-20 | 助理服务值域合法 | assistant_services中每个已知服务键的值不得超过CSV给出的选项下标上界，且不得为负 |
| PLACE-21 | 助理服务键集完整 | 每个角色的assistant_services应恰好包含服务键2..10 |
| PLACE-22 | 同居服务与宿舍一致 | 当前助理开启服务7（同居）时，其宿舍应为"中枢/博士房间" |
| PLACE-23 | 跟随模式取值合法 | sp_flag.is_follow只能取0-4 |
| PLACE-24 | 玩家不跟随自己 | id 0的sp_flag.is_follow必须为0 |
| PLACE-25 | 跟随者必须在册、活着、在线 | sp_flag.is_follow != 0的角色必须是非玩家、在npc_id_got中、未死亡、且不带离线标记 |
| PLACE-26 | 跟随/助理身份必须反映在异常位缓存中 | sp_flag.unnormal_flag第3位（高优先级AI：助理、跟随、体检）缓存：若角色正在跟随或就是助理， 而该位已被标记为"已知"却是"正常"，说明缓存过期 |
| PLACE-27 | 装袋搬运双向一致 | "装袋搬走"状态的双向一致性：(1) 只有玩家(id 0)可以持有非零bagging_chara_id |
| PLACE-28 | 登记宿舍不得停留在与当前宿舍相同的值 | LIVE域内角色的「登记宿舍」（双名兼容：permanent_dormitory/pre_dormitory）非空时不得等于 当前dormitory |
| PLACE-29 | 登记宿舍非空时必须是合法的普通宿舍房间 | LIVE域内角色的「登记宿舍」（双名兼容）非空且不等于当前dormitory时（与PLACE-28互斥的另一种 失败模式），其值必须是一间真实的、当前开放的普通宿舍房间——用 Script/System/Dormitory_System/common.py的get_open_dormitory_room_occupancy()（函数级导入，避免 加载顺序问题）取得的开放宿舍占用表判定，不接受特殊房间（客房/监牢/博士房间/舍管房/关押区休息室） |
| PLACE-30 | 教室标签索引 | 教育标签索引内路径须存在且带该标签，场景带标签时也须出现在索引中 |
| PLACE-31 | 教室名称无歧义 | 全局课表与个人0–3课型的场景名须唯一对应匹配教育标签的场景，未开放或关闭不报错 |

## ROSTER：名册

在编名册、监禁与逃跑、监狱长、访客、邀请、招募、外勤委托、载具、外交官、装袋。

| 编号 | 名称 | 说明 |
|---|---|---|
| ROSTER-01 | 在编名册id自洽 | cache.npc_id_got中每个id都存在角色对象，且角色自身cid与名册键一致，这是后续全部名册检查的地基 |
| ROSTER-02 | 玩家id不应长期留在NPC名册里 | npc_id_got语义上是NPC集合，但init_character_position/init_character_entertainment会对玩家本体add(0)， discard(0)只在基建/宿舍面板(玩家触发)里执行，回合主循环从不调用 |
| ROSTER-03 | 在编干员与场景名册双向一致 | 在编NPC恰好出现在其position对应的那一个场景里，离线角色从所有场景消失，场景里不得有幽灵id |
| ROSTER-04 | 离线来源flag必须对应真正的离线态 | 装袋/外勤/越狱三条路径都是"置来源flag→重算异常位→handle_chara_off_line"的原子写法 |
| ROSTER-05 | 监禁flag的来源分区完整 | 带imprisonment的角色当且仅当是在册囚犯或逃跑中的前囚犯(escape_success故意保留imprisonment)； 囚犯与逃犯两个集合互斥 |
| ROSTER-06 | 囚犯名册条目结构合法且本人在编 | current_prisoners每条记录形状为[入狱时间, 逃脱概率]，概率夹在0..100之间且非bool污染， 本人在编且sp_flag.imprisonment为True、escaping为False |
| ROSTER-07 | 囚犯宿舍是互不重复的合法牢房 | 每名囚犯的dormitory都必须在PRISON_DORMS(全部Prison标签场景，即牢1..牢8)集合内，且互不重复 |
| ROSTER-08 | 囚犯留在关押区且不得同时被装袋 | 囚犯cant_move，NPC AI会把不在牢房的囚犯瞬移回宿舍，合法的短暂离房只有"正在H(含调教室)"； 用position[0] == "关押"比对目录首段，不拼分隔符 |
| ROSTER-09 | 逃跑者处于完整离线态 | escape_success依次置escaping→重算异常位→pop囚犯名册→handle_chara_off_line→创建追捕委托， 并保留imprisonment |
| ROSTER-10 | 逃跑者仍有一条可执行的追捕委托 | 每个escaping角色都应存在一条reward=="追捕_{cid}_1"且未标记完成的委托配置； 牢房全满时抓捕结算会静默跳过归案，委托却照样标完成并出表，逃犯从此永久滞留escaping |
| ROSTER-11 | 监狱长缓存唯一且指向真实岗位 | 在编干员里最多只能有一名工作类型191的监狱长，current_warden_id非零时必须指向存在的角色， 不能与那名在编191冲突 |
| ROSTER-12 | 监狱长身份软约束 | 期望状态：current_warden_id非零时该人在编、宿舍是关押区休息室、不是囚犯/访客、不在外勤 |
| ROSTER-13 | 监禁调教设置键齐全且取值在选项范围内 | 设置字典由配置表全量初始化为0，UI用option[cid][value]直接索引(越界IndexError)， 结算路径对[4]/[13]直取(缺键KeyError) |
| ROSTER-14 | 访客名册与访客flag完全等价 | visitor_info与sp_flag.vistor == 1是同一件事的两份记录，且当前访客必然在编 |
| ROSTER-15 | 访客住在互不重复的客房 | 访客由分配器挑一间没有别的访客占用的客房；用场景标签集合GUEST_ROOMS判定房间合法性， 比"客房" in d的子串判定更强 |
| ROSTER-16 | 访客人数不超过客房上限 | visitor_max是按已开放客房数重算的接待闸门 |
| ROSTER-17 | 没有严重逾期未结算的访客 | 访客到期由跨日结算处理一次，"D日到期、D+1日00:00才结算"是正常窗口，阈值必须放到一整天以上， 否则会周期性误报；类型检查不可省，脏值在减法处会抛异常而非给出判定 |
| ROSTER-18 | 邀请栏结构完整、空目标必归零 | invite_visitor是[目标id, 进度, 效率]；目标为0时进度必须为0；进度与效率是非负有限数 |
| ROSTER-19 | 邀请目标仍是合法的未入编候选 | 邀请目标只能来自find_recruitable_npc() |
| ROSTER-20 | 待确认招募名单合法 | recruited_id是"已招募待玩家确认"的暂存池，里面不该有0、不存在的id，也不该有已在编或身份冲突的人 |
| ROSTER-21 | 当前访客与其它名册身份互斥 | 当前访客不能同时是待确认招募、邀请目标、囚犯、逃犯或外勤队员 —— 这些身份的在线规则互相冲突 |
| ROSTER-22 | 招募线记录形状与进度范围 | 每条recruit_line是[进度, 策略id, 主专员id, 效率]；进度与效率为非负有限数，策略与主专员为整数， 进度上界<100由增量写入与结算相邻两行保证，不存在"已加未结"窗口 |
| ROSTER-23 | 招募线主专员真实可用且不重复 | 每条线第3位是主招聘专员：0(空缺)或一名工作类型71且在hr_operator_ids_list招聘专员列表内的角色； 同一人不能同时主理两条线 |
| ROSTER-24 | 招聘专员列表无重复、成员岗位正确、在编71全部在内 | hr_operator_ids_list是增量维护的效率计算表 |
| ROSTER-25 | 进行中委托记录结构合法、人员全局唯一 | 每条记录是[干员id列表, 返回时间, 载具id列表]；同一人不能在单条记录里重复，也不能同时出现在两个委托里 |
| ROSTER-26 | 外勤名单与角色外勤flag双向一致 | 派遣时逐人写sp_flag.field_commission = 委托id，结算时逐人清0再上线 |
| ROSTER-27 | 外勤人员不得兼任访客/囚犯/助理/监狱长/招募目标 | 派遣候选表显式排除访客、助理、监狱长以及2类(临盆/产后/监禁)、7类(离线)异常；待确认招募与 邀请目标本就不在在编名册内 |
| ROSTER-28 | 载具外勤中数与委托明细守恒 | vehicles[vid] = [拥有数, 外勤中数]；外勤中数必须等于所有进行中委托里该型号载具的出现次数， 且不超过拥有数 |
| ROSTER-29 | 进行中委托id有效且未逾期 | 委托完成判定在每个非时停玩家回合的行为树里先于NPC结算跑一次，回合结束时留下的委托必须严格 满足end_time > game_time(> 而非 >=，恰好到点的委托按完成条件本应已结算) |
| ROSTER-30 | 外交官表与角色外派flag双向一致 | 任命写diplomat_of_country[国家][0] = id与sp_flag.in_diplomatic_visit = 国家，解任同时清两者 |
| ROSTER-31 | 异常位掩码与其来源状态一致(第2、7位) | sp_flag.unnormal_flag是带"已知/未知"两层的位掩码缓存，第2位=AI停止(临盆/产后/监禁)， 第7位=离线(装袋/外勤/婴儿/异国外派/逃跑) |
| ROSTER-32 | 助理身份互斥 | 助理候选排除访客、监狱长以及2/7类异常 |
| ROSTER-33 | 装袋双方记录双向一致 | 玩家的sp_flag.bagging_chara_id与被搬运者的sp_flag.be_bagged必须互指；被装袋者必须离线， 且不能同时是囚犯、访客、外勤或逃跑者 |

## BIRTH / COOK：设置记忆

生育开关与烹饪记忆。

| 编号 | 名称 | 说明 |
|---|---|---|
| BIRTH-01 | 生育开关 | 生育开关覆盖配置键，值为0/1，多余键仅警示 |
| BIRTH-02 | 已关闭卵生存量 | 按原始种族生育方式检查关闭后的卵、无壳排卵机会与博士持卵索引，不检查胎数 |
| COOK-01 | 烹饪模式记忆 | 烹饪模式字典只允许0–2页签，模式为0或1，允许缺键 |
| COOK-02 | 制作份数记忆 | 制作份数字典只允许0–2页签，份数为1–10整数 |

## SUPP：补充盲点

不属于任何单一领域的条目。

| 编号 | 名称 | 说明 |
|---|---|---|
| SUPP-01 | 供电策略合法性 | cache.rhodes_island.power_supply_strategy的键值域：键必须是当前配置中 type==-1的大区块设施cid，值必须是game_config.config_supply_strategy的合法键 |
| SUPP-02 | 生活娱乐/科研/士兵/访客上限派生一致 | life_zone_max/research_zone_max/soldier_max分别与设施cid 5/8/21 当前等级效果一致，visitor_max与当前config_facility_open中名称含"客房"且facility_open为真的数量一致 |
| SUPP-03 | 设施开放派生单调覆盖 | 对当前config_facility_open中每个待开放项，只要其zone_cid已被全设施 当前等级效果cid覆盖（相等，或同十位且个位数达标），对应facility_open[open_cid]就应为真 |
| SUPP-04 | 时停无意识值跨名单残留 | 非时停时，character_data中任何角色都不应残留专属时停无意识值 unconscious_h==3 |
| SUPP-05 | 愤怒值下界 | 每个角色的angry_point类型为int且不小于0 |
| SUPP-06 | 模板对象别名 | 任一角色实例的ability/experience/talent字典都不得与任一NPC模板 对应字典是同一个对象（用id()判等，不比较值） |
| SUPP-07 | 仓储扩展模块使用数非负 | （只取独立于NUM-26的后半式） |
| SUPP-08 | 办公室场景引用合法 | character_data中每个角色的officeroom（列表字段）只允许是空列表或 cache.scene_data的合法键 |
