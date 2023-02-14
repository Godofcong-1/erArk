class BehaviorEffect:
    """行为结算效果函数"""

    NOTHING = 9999
    """ 系统状态 什么都没有的空结算 """
    INTERRUPT_TARGET_ACTIVITY = 10000
    """ 系统状态 打断交互对象活动 """
    OPTION_FATER = 10001
    """ 系统状态 开启子选项面板 """

    ADD_SMALL_HIT_POINT = 0
    """ 属性_基础 增加少量体力 """
    ADD_SMALL_MANA_POINT = 1
    """ 属性_基础 增加少量气力 """
    ADD_BOTH_SMALL_HIT_POINT = 2
    """ 属性_基础 增加双方少量体力 """
    ADD_BOTH_SMALL_MANA_POINT = 3
    """ 属性_基础 增加双方少量气力 """
    ADD_MEDIUM_HIT_POINT = 5
    """ 属性_基础 增加中量体力 """
    ADD_MEDIUM_MANA_POINT = 6
    """ 属性_基础 增加中量气力 """
    DOWN_BOTH_SMALL_HIT_POINT = 11
    """ 属性_基础 双方减少少量体力（若没有交互对象则仅减少自己） """
    DOWN_BOTH_SMALL_MANA_POINT = 12
    """ 属性_基础 双方减少少量气力（若没有交互对象则仅减少自己） """
    DOWN_SELF_SMALL_HIT_POINT = 13
    """ 属性_基础 减少自己少量体力 """
    DOWN_SELF_SMALL_MANA_POINT = 14
    """ 属性_基础 减少自己少量气力 """
    ADD_INTERACTION_FAVORABILITY = 21
    """ 属性_基础 增加基础互动好感 """
    ADD_SMALL_TRUST = 22
    """ 属性_基础 增加基础互动信赖 """
    DOWN_INTERACTION_FAVORABILITY = 23
    """ 属性_基础 降低基础互动好感 """
    DOWN_SMALL_TRUST = 24
    """ 属性_基础 降低基础互动信赖 """
    NOT_TIRED = 31
    """ 属性_基础 从疲劳中恢复 """
    URINATE_POINT_DOWN = 32
    """ 属性_基础 尿意值归零 """
    TARGET_URINATE_POINT_DOWN = 33
    """ 属性_基础 交互对象尿意值归零 """
    HUNGER_POINT_DOWN = 34
    """ 属性_基础 饥饿值归零 """
    TARGET_HUNGER_POINT_DOWN = 35
    """ 属性_基础 交互对象饥饿值归零 """

    TARGET_ADD_SMALL_N_FEEL = 41
    """ 属性_状态 交互对象增加少量Ｎ快（N感补正） """
    TARGET_ADD_SMALL_B_FEEL = 42
    """ 属性_状态 交互对象增加少量Ｂ快（B感补正） """
    TARGET_ADD_SMALL_C_FEEL = 43
    """ 属性_状态 交互对象增加少量Ｃ快（C感补正） """
    TARGET_ADD_SMALL_P_FEEL = 44
    """ 属性_状态 交互对象增加少量Ｐ快（P感补正） """
    TARGET_ADD_SMALL_V_FEEL = 45
    """ 属性_状态 交互对象增加少量Ｖ快（V感补正） """
    TARGET_ADD_SMALL_A_FEEL = 46
    """ 属性_状态 交互对象增加少量Ａ快（A感补正） """
    TARGET_ADD_SMALL_U_FEEL = 47
    """ 属性_状态 交互对象增加少量Ｕ快（U感补正） """
    TARGET_ADD_SMALL_W_FEEL = 48
    """ 属性_状态 交互对象增加少量Ｗ快（W感补正） """
    TARGET_ADD_SMALL_LUBRICATION = 49
    """ 属性_状态 交互对象增加少量润滑（欲望补正） """
    TARGET_ADD_SMALL_LEARN = 51
    """ 属性_状态 交互对象增加少量习得（技巧补正） """
    TARGET_ADD_SMALL_RESPECT = 52
    """ 属性_状态 交互对象增加少量恭顺（顺从补正） """
    TARGET_ADD_SMALL_FRIENDLY = 53
    """ 属性_状态 交互对象增加少量好意（亲密补正） """
    TARGET_ADD_SMALL_DESIRE = 54
    """ 属性_状态 交互对象增加少量欲情（欲望补正） """
    TARGET_ADD_SMALL_HAPPY = 55
    """ 属性_状态 交互对象增加少量快乐（快乐刻印补正） """
    TARGET_ADD_SMALL_LEAD = 56
    """ 属性_状态 交互对象增加少量先导（施虐补正） """
    TARGET_ADD_SMALL_SUBMIT = 57
    """ 属性_状态 交互对象增加少量屈服（屈服刻印补正） """
    TARGET_ADD_SMALL_SHY = 58
    """ 属性_状态 交互对象增加少量羞耻（露出补正） """
    TARGET_ADD_SMALL_PAIN = 59
    """ 属性_状态 交互对象增加少量苦痛（苦痛刻印补正） """
    TARGET_ADD_SMALL_TERROR = 60
    """ 属性_状态 交互对象增加少量恐怖（恐怖刻印补正） """
    TARGET_ADD_SMALL_DEPRESSION = 61
    """ 属性_状态 交互对象增加少量抑郁 """
    TARGET_ADD_SMALL_DISGUST = 62
    """ 属性_状态 交互对象增加少量反感（反发刻印补正） """
    ADD_SMALL_P_FEEL = 70
    """ 属性_状态 自身增加少量Ｐ快 """
    BOTH_ADD_SMALL_LEARN = 71
    """ 属性_状态 双方增加少量习得（若没有交互对象则仅增加自己） """
    ADD_SMALL_LEARN = 72
    """ 属性_状态 自己增加少量习得 """

    TECH_ADD_N_ADJUST = 110
    """ 属性_状态特殊补正 根据发起者的技巧技能对交互对象进行N快、欲情调整 """
    TECH_ADD_B_ADJUST = 111
    """ 属性_状态特殊补正 根据发起者的技巧技能对交互对象进行B快、欲情调整 """
    TECH_ADD_C_ADJUST = 112
    """ 属性_状态特殊补正 根据发起者的技巧技能对交互对象进行C快、欲情调整 """
    TECH_ADD_P_ADJUST = 113
    """ 属性_状态特殊补正 根据发起者的技巧技能对交互对象进行P快、欲情调整 """
    TECH_ADD_V_ADJUST = 114
    """ 属性_状态特殊补正 根据发起者的技巧技能对交互对象进行V快、欲情调整 """
    TECH_ADD_A_ADJUST = 115
    """ 属性_状态特殊补正 根据发起者的技巧技能对交互对象进行A快、欲情调整 """
    TECH_ADD_U_ADJUST = 116
    """ 属性_状态特殊补正 根据发起者的技巧技能对交互对象进行U快、欲情调整 """
    TECH_ADD_W_ADJUST = 117
    """ 属性_状态特殊补正 根据发起者的技巧技能对交互对象进行W快、欲情调整 """
    TECH_ADD_PL_P_ADJUST = 120
    """ 属性_状态特殊补正 根据交互对象的技巧技能对发起者进行P快调整 """
    TARGET_LUBRICATION_ADJUST_ADD_PAIN = 121
    """ 属性_状态特殊补正 根据交互对象的润滑情况对其进行苦痛调整 """

    LOW_OBSCENITY_FAILED_ADJUST = 151
    """ 属性_失败状态 轻度性骚扰失败的加反感、加愤怒、降好感度修正 """
    HIGH_OBSCENITY_FAILED_ADJUST = 152
    """ 属性_失败状态 重度性骚扰失败的加反感、加愤怒、降好感度、降信赖修正 """

    TARGET_ADD_1_N_EXPERIENCE = 200
    """ 属性_经验 交互对象增加1N经验 """
    TARGET_ADD_1_B_EXPERIENCE = 201
    """ 属性_经验 交互对象增加1B经验 """
    TARGET_ADD_1_C_EXPERIENCE = 202
    """ 属性_经验 交互对象增加1C经验 """
    TARGET_ADD_1_P_EXPERIENCE = 203
    """ 属性_经验 交互对象增加1P经验 """
    TARGET_ADD_1_V_EXPERIENCE = 204
    """ 属性_经验 交互对象增加1V经验 """
    TARGET_ADD_1_A_EXPERIENCE = 205
    """ 属性_经验 交互对象增加1A经验 """
    TARGET_ADD_1_U_EXPERIENCE = 206
    """ 属性_经验 交互对象增加1U经验 """
    TARGET_ADD_1_W_EXPERIENCE = 207
    """ 属性_经验 交互对象增加1W经验 """
    TARGET_ADD_1_NClimax_EXPERIENCE = 210
    """ 属性_经验 交互对象增加1N绝顶经验 """
    TARGET_ADD_1_BClimax_EXPERIENCE = 211
    """ 属性_经验 交互对象增加1B绝顶经验 """
    TARGET_ADD_1_CClimax_EXPERIENCE = 212
    """ 属性_经验 交互对象增加1C绝顶经验 """
    TARGET_ADD_1_VClimax_EXPERIENCE = 214
    """ 属性_经验 交互对象增加1V绝顶经验 """
    TARGET_ADD_1_AClimax_EXPERIENCE = 215
    """ 属性_经验 交互对象增加1A绝顶经验 """
    TARGET_ADD_1_UClimax_EXPERIENCE = 216
    """ 属性_经验 交互对象增加1U绝顶经验 """
    TARGET_ADD_1_WClimax_EXPERIENCE = 217
    """ 属性_经验 交互对象增加1W绝顶经验 """
    TARGET_ADD_1_Cumming_EXPERIENCE = 221
    """ 属性_经验 交互对象增加1射精经验 """
    TARGET_ADD_1_Milking_EXPERIENCE = 222
    """ 属性_经验 交互对象增加1喷乳经验 """
    TARGET_ADD_1_Peeing_EXPERIENCE = 223
    """ 属性_经验 交互对象增加1放尿经验 """
    TARGET_ADD_1_Cums_EXPERIENCE = 224
    """ 属性_经验 交互对象增加1精液经验 """
    TARGET_ADD_1_CumsDrink_EXPERIENCE = 225
    """ 属性_经验 交互对象增加1饮精经验 """
    TARGET_ADD_1_Creampie_EXPERIENCE = 226
    """ 属性_经验 交互对象增加1膣射经验 """
    TARGET_ADD_1_AnalCums_EXPERIENCE = 227
    """ 属性_经验 交互对象增加1肛射经验 """
    TARGET_ADD_1_plServe_EXPERIENCE = 230
    """ 属性_经验 交互对象增加1奉仕快乐经验 """
    TARGET_ADD_1_Love_EXPERIENCE = 231
    """ 属性_经验 交互对象增加1爱情经验 """
    TARGET_ADD_1_plPain_EXPERIENCE = 232
    """ 属性_经验 交互对象增加1苦痛快乐经验 """
    TARGET_ADD_1_plSadism_EXPERIENCE = 233
    """ 属性_经验 交互对象增加1嗜虐快乐经验 """
    TARGET_ADD_1_plExhibit_EXPERIENCE = 234
    """ 属性_经验 交互对象增加1露出快乐经验 """
    TARGET_ADD_1_Kiss_EXPERIENCE = 240
    """ 属性_经验 交互对象增加1接吻经验 """
    TARGET_ADD_1_Handjob_EXPERIENCE = 241
    """ 属性_经验 交互对象增加1手淫经验 """
    TARGET_ADD_1_Blowjob_EXPERIENCE = 242
    """ 属性_经验 交互对象增加1口淫经验 """
    TARGET_ADD_1_Paizuri_EXPERIENCE = 243
    """ 属性_经验 交互对象增加1乳交经验 """
    TARGET_ADD_1_Footjob_EXPERIENCE = 244
    """ 属性_经验 交互对象增加1足交经验 """
    TARGET_ADD_1_Hairjob_EXPERIENCE = 245
    """ 属性_经验 交互对象增加1发交经验 """
    TARGET_ADD_1_Masterbate_EXPERIENCE = 246
    """ 属性_经验 交互对象增加1自慰经验 """
    TARGET_ADD_1_bdsmMasterbate_EXPERIENCE = 247
    """ 属性_经验 交互对象增加1调教自慰经验 """
    TARGET_ADD_1_Toys_EXPERIENCE = 248
    """ 属性_经验 交互对象增加1道具使用经验 """
    TARGET_ADD_1_Tiedup_EXPERIENCE = 249
    """ 属性_经验 交互对象增加1紧缚经验 """
    TARGET_ADD_1_Insert_EXPERIENCE = 250
    """ 属性_经验 交互对象增加1插入经验 """
    TARGET_ADD_1_sexV_EXPERIENCE = 251
    """ 属性_经验 交互对象增加1V性交经验 """
    TARGET_ADD_1_sexA_EXPERIENCE = 252
    """ 属性_经验 交互对象增加1A性交经验 """
    TARGET_ADD_1_sexU_EXPERIENCE = 253
    """ 属性_经验 交互对象增加1U性交经验 """
    TARGET_ADD_1_sexW_EXPERIENCE = 254
    """ 属性_经验 交互对象增加1W性交经验 """
    TARGET_ADD_1_expandV_EXPERIENCE = 255
    """ 属性_经验 交互对象增加1V扩张经验 """
    TARGET_ADD_1_expandA_EXPERIENCE = 256
    """ 属性_经验 交互对象增加1A扩张经验 """
    TARGET_ADD_1_expandU_EXPERIENCE = 257
    """ 属性_经验 交互对象增加1U扩张经验 """
    TARGET_ADD_1_expandW_EXPERIENCE = 258
    """ 属性_经验 交互对象增加1W扩张经验 """
    TARGET_ADD_1_TWRape_EXPERIENCE = 259
    """ 属性_经验 交互对象增加1时奸经验 """
    TARGET_ADD_1_SlumberRape_EXPERIENCE = 260
    """ 属性_经验 交互对象增加1睡奸经验 """
    TARGET_ADD_1_Abnormal_EXPERIENCE = 261
    """ 属性_经验 交互对象增加1异常经验 """
    TARGET_ADD_1_Axillajob_EXPERIENCE = 262
    """ 属性_经验 交互对象增加1腋交经验 """
    TARGET_ADD_1_Enema_EXPERIENCE = 263
    """ 属性_经验 交互对象增加1灌肠经验 """
    TARGET_ADD_1_UnconsciouslyN_EXPERIENCE = 270
    """ 属性_经验 交互对象增加1无意识N经验 """
    TARGET_ADD_1_UnconsciouslyB_EXPERIENCE = 271
    """ 属性_经验 交互对象增加1无意识B经验 """
    TARGET_ADD_1_UnconsciouslyC_EXPERIENCE = 272
    """ 属性_经验 交互对象增加1无意识C经验 """
    TARGET_ADD_1_UnconsciouslyP_EXPERIENCE = 273
    """ 属性_经验 交互对象增加1无意识P经验 """
    TARGET_ADD_1_UnconsciouslyV_EXPERIENCE = 274
    """ 属性_经验 交互对象增加1无意识V经验 """
    TARGET_ADD_1_UnconsciouslyA_EXPERIENCE = 275
    """ 属性_经验 交互对象增加1无意识A经验 """
    TARGET_ADD_1_UnconsciouslyU_EXPERIENCE = 276
    """ 属性_经验 交互对象增加1无意识U经验 """
    TARGET_ADD_1_UnconsciouslyW_EXPERIENCE = 277
    """ 属性_经验 交互对象增加1无意识W经验 """
    TARGET_ADD_1_UnconsciouslyClimax_EXPERIENCE = 278
    """ 属性_经验 交互对象增加1无意识绝顶经验 """
    TARGET_ADD_1_Chat_EXPERIENCE = 280
    """ 属性_经验 交互对象增加1对话经验 """
    TARGET_ADD_1_Combat_EXPERIENCE = 281
    """ 属性_经验 交互对象增加1战斗经验 """
    TARGET_ADD_1_Learn_EXPERIENCE = 282
    """ 属性_经验 交互对象增加1学识经验 """
    TARGET_ADD_1_Cooking_EXPERIENCE = 283
    """ 属性_经验 交互对象增加1料理经验 """
    TARGET_ADD_1_Date_EXPERIENCE = 284
    """ 属性_经验 交互对象增加1约会经验 """
    TARGET_ADD_1_Music_EXPERIENCE = 285
    """ 属性_经验 交互对象增加1音乐经验 """
    TARGET_ADD_1_GiveBirth_EXPERIENCE = 286
    """ 属性_经验 交互对象增加1妊娠经验 """
    TARGET_ADD_1_Command_EXPERIENCE = 288
    """ 属性_经验 交互对象增加1指挥经验 """
    TARGET_ADD_1_Cure_EXPERIENCE = 289
    """ 属性_经验 交互对象增加1医疗经验 """
    TARGET_ADD_1_ForwardClimax_EXPERIENCE = 300
    """ 属性_经验 交互对象增加1正面位绝顶经验 """
    TARGET_ADD_1_BackClimax_EXPERIENCE = 301
    """ 属性_经验 交互对象增加1后入位绝顶经验 """
    TARGET_ADD_1_RideClimax_EXPERIENCE = 302
    """ 属性_经验 交互对象增加1骑乘位绝顶经验 """
    TARGET_ADD_1_FSeatClimax_EXPERIENCE = 303
    """ 属性_经验 交互对象增加1对面座位绝顶经验 """
    TARGET_ADD_1_BSeatClimax_EXPERIENCE = 304
    """ 属性_经验 交互对象增加1背面座位绝顶经验 """
    TARGET_ADD_1_FStandClimax_EXPERIENCE = 305
    """ 属性_经验 交互对象增加1对面立位绝顶经验 """
    TARGET_ADD_1_BStandClimax_EXPERIENCE = 306
    """ 属性_经验 交互对象增加1背面立位绝顶经验 """
    ADD_1_Kiss_EXPERIENCE = 307
    """ 属性_经验 增加1接吻经验 """
    ADD_1_Handjob_EXPERIENCE = 308
    """ 属性_经验 增加1手淫经验 """
    ADD_1_Blowjob_EXPERIENCE = 309
    """ 属性_经验 增加1口淫经验 """
    ADD_1_Paizuri_EXPERIENCE = 310
    """ 属性_经验 增加1乳交经验 """
    ADD_1_Footjob_EXPERIENCE = 311
    """ 属性_经验 增加1足交经验 """
    ADD_1_Hairjob_EXPERIENCE = 312
    """ 属性_经验 增加1发交经验 """
    ADD_1_Chat_EXPERIENCE = 313
    """ 属性_经验 增加1对话经验 """
    ADD_1_Combat_EXPERIENCE = 314
    """ 属性_经验 增加1战斗经验 """
    ADD_1_Learn_EXPERIENCE = 315
    """ 属性_经验 增加1学识经验 """
    ADD_1_Cooking_EXPERIENCE = 316
    """ 属性_经验 增加1料理经验 """
    ADD_1_Date_EXPERIENCE = 317
    """ 属性_经验 增加1约会经验 """
    ADD_1_Music_EXPERIENCE = 318
    """ 属性_经验 增加1音乐经验 """
    ADD_1_GiveBirth_EXPERIENCE = 319
    """ 属性_经验 增加1妊娠经验 """
    ADD_1_Insert_EXPERIENCE = 320
    """ 属性_经验 增加1插入经验 """
    ADD_1_Command_EXPERIENCE = 321
    """ 属性_经验 增加1指挥经验 """
    ADD_1_Cure_EXPERIENCE = 322
    """ 属性_经验 增加1医疗经验 """
    Both_ADD_1_Learn_EXPERIENCE = 350
    """ 属性_经验 双方增加1学识经验 """

    DIRTY_RESET = 401
    """ 属性_结构体 污浊结构体归零 """
    BOTH_H_STATE_RESET = 404
    """ 属性_结构体 双方H状态结构体归零 """

    TALK_ADD_ADJUST = 501
    """ 指令_专用结算 （聊天用）根据发起者的话术技能进行双方的好感度、好意、快乐调整，并记录当前谈话时间 """
    COFFEE_ADD_ADJUST = 502
    """ 指令_专用结算 （泡咖啡用）根据发起者的料理技能进行好感度、信赖、好意调整 """
    TARGET_COFFEE_ADD_ADJUST = 503
    """ 指令_专用结算 （泡咖啡用）根据交互对象的料理技能进行好感度、信赖、好意调整 """
    SING_ADD_ADJUST = 504
    """ 指令_专用结算 （唱歌用）根据自己的音乐技能进行好感度、信赖、好意调整 """
    PLAY_INSTRUMENT_ADD_ADJUST = 505
    """ 指令_专用结算 （演奏乐器用）根据发起者的音乐技能进行好感度、信赖、好意调整 """
    KONWLEDGE_ADD_PINK_MONEY = 506
    """ 指令_专用结算 （处理公务用）根据自己（如果有的话再加上交互对象）的学识获得少量粉色凭证 """
    CURE_PATIENT_ADD_ADJUST = 507
    """ 指令_专用结算 （诊疗病人用）根据发起者(如果有的话再加上交互对象)的医疗技能治愈了一名病人，并获得一定的龙门币 """
    ADD_HPMP_MAX = 508
    """ 指令_专用结算 （锻炼身体用）增加体力气力上限 """
    SLEEP_POINT_DOWN = 509
    """ 指令_专用结算 （睡觉用）降低困倦值 """
    RECRUIT_ADD_ADJUST = 510
    """ 指令_专用结算 （招募干员用）根据发起者(如果有的话再加上交互对象)的话术技能增加招募槽 """
    READ_ADD_ADJUST = 511
    """ 指令_专用结算 （读书用）根据书的不同对发起者(如果有的话再加上交互对象)获得对应的知识，并进行NPC的还书判定 """
    TEACH_ADD_ADJUST = 512
    """ 指令_专用结算 （教学用）自己增加习得和学识经验，所有当前场景里状态是上课的角色增加习得和学识经验，如果玩家是老师则再加好感和信赖，最后结束 """

    CHANGE_UNDERWERA = 601
    """ 属性_服装 换新的内衣（胸衣+内裤） """
    BRA_SEE = 602
    """ 属性_服装 胸罩可视 """
    TARGET_BRA_SEE = 603
    """ 属性_服装 交互对象胸罩可视 """
    PAN_SEE = 604
    """ 属性_服装 内裤可视 """
    TARGET_PAN_SEE = 605
    """ 属性_服装 交互对象内裤可视 """
    CLOTH_SEE_ZERO = 606
    """ 属性_服装 内衣可视清零 """
    RESTE_CLOTH = 607
    """ 属性_服装 衣服重置为初始状态 """
    ASK_FOR_PAN = 621
    """ 属性_服装 获得交互对象的内裤 """
    ASK_FOR_SOCKS = 622
    """ 属性_服装 获得交互对象的袜子 """
    T_CLOTH_BACK = 631
    """ 属性_服装 交互对象穿回H时脱掉的衣服 """
    WEAR_CLOTH_OFF = 632
    """ 属性_服装 脱掉全部衣服 """
    GET_SHOWER_CLOTH = 633
    """ 属性_服装 换上浴帽和浴巾 """
    LOCKER_CLOTH_RESET = 641
    """ 属性_服装 衣柜里的衣服清零 """
    WEAR_TO_LOCKER = 642
    """ 属性_服装 身上首饰以外的衣服转移到柜子里 """
    LOCKER_TO_WEAR = 643
    """ 属性_服装 衣柜里的衣服转移到身上 """

    RECORD_TRAINING_TIME = 701
    """ 系统量_时间 角色记录并刷新训练时间 """
    RECORD_SHOWER_TIME = 702
    """ 系统量_时间 角色记录并刷新淋浴时间 """

    MOVE_TO_TARGET_SCENE = 751
    """ 系统量_地点 移动至目标场景 """
    DOOR_CLOSE = 752
    """ 系统量_地点 当前场景进入关门状态 """
    DOOR_CLOSE_RESET = 753
    """ 系统量_地点 当前场景取消关门状态 """
    MOVE_TO_PRE_SCENE = 761
    """ 系统量_地点 角色移动至前一场景 """

    PENIS_IN_T_RESET = 801
    """ H_阴茎位置 当前阴茎位置为交互对象_归零 """
    PENIS_IN_T_HAIR = 802
    """ H_阴茎位置 当前阴茎位置为交互对象_发交中 """
    PENIS_IN_T_FACE = 803
    """ H_阴茎位置 当前阴茎位置为交互对象_阴茎蹭脸中 """
    PENIS_IN_T_MOUSE = 804
    """ H_阴茎位置 当前阴茎位置为交互对象_口交中 """
    PENIS_IN_T_BREAST = 805
    """ H_阴茎位置 当前阴茎位置为交互对象_乳交中 """
    PENIS_IN_T_AXILLA = 806
    """ H_阴茎位置 当前阴茎位置为交互对象_腋交中 """
    PENIS_IN_T_HAND = 807
    """ H_阴茎位置 当前阴茎位置为交互对象_手交中 """
    PENIS_IN_T_VAGINA = 808
    """ H_阴茎位置 当前阴茎位置为交互对象_V插入中 """
    PENIS_IN_T_WOMB = 809
    """ H_阴茎位置 当前阴茎位置为交互对象_W插入中 """
    PENIS_IN_T_ANAL = 810
    """ H_阴茎位置 当前阴茎位置为交互对象_A插入中 """
    PENIS_IN_T_URETHRAL = 811
    """ H_阴茎位置 当前阴茎位置为交互对象_U插入中 """
    PENIS_IN_T_LEG = 812
    """ H_阴茎位置 当前阴茎位置为交互对象_腿交中 """
    PENIS_IN_T_FOOT = 813
    """ H_阴茎位置 当前阴茎位置为交互对象_足交中 """
    PENIS_IN_T_TAIL = 814
    """ H_阴茎位置 当前阴茎位置为交互对象_尾交中 """
    PENIS_IN_T_HORN = 815
    """ H_阴茎位置 当前阴茎位置为交互对象_阴茎蹭角中 """
    PENIS_IN_T_EARS = 816
    """ H_阴茎位置 当前阴茎位置为交互对象_阴茎蹭耳朵中 """

    ITEM_OFF = 901
    """ 道具_使用 去掉身上所有的道具 """
    TARGET_ITEM_OFF = 902
    """ 道具_使用 交互对象去掉身上所有的道具 """
    TARGET_VIBRATOR_ON = 911
    """ 道具_使用 交互对象插入V震动棒 """
    TARGET_VIBRATOR_OFF = 912
    """ 道具_使用 交互对象拔出V震动棒 """
    TARGET_ANAL_VIBRATOR_ON = 913
    """ 道具_使用 交互对象插入A震动棒 """
    TARGET_ANAL_VIBRATOR_OFF = 914
    """ 道具_使用 交互对象拔出A震动棒 """
    TARGET_NIPPLE_CLAMP_ON = 915
    """ 道具_使用 交互对象戴上乳头夹 """
    TARGET_NIPPLE_CLAMP_OFF = 916
    """ 道具_使用 交互对象取下乳头夹 """
    TARGET_CLIT_CLAMP_ON = 917
    """ 道具_使用 交互对象戴上阴蒂夹 """
    TARGET_CLIT_CLAMP_OFF = 918
    """ 道具_使用 交互对象取下阴蒂夹 """
    TARGET_ANAL_BEADS_ON = 919
    """ 道具_使用 交互对象塞入肛门拉珠 """
    TARGET_ANAL_BEADS_OFF = 920
    """ 道具_使用 交互对象拔出肛门拉珠 """
    USE_BODY_LUBRICANT = 941
    """ 道具_使用 使用了一个润滑液 """
    USE_PHILTER = 942
    """ 道具_使用 使用了一个媚药 """
    USE_ENEMAS = 943
    """ 道具_使用 使用了一个灌肠液 """
    USE_DIURETICS_ONCE = 944
    """ 道具_使用 使用了一个一次性利尿剂 """
    USE_DIURETICS_PERSISTENT = 945
    """ 道具_使用 使用了一个持续性利尿剂 """
    EAT_FOOD = 991
    """ 道具_使用 进食指定食物 """
    MAKE_FOOD = 992
    """ 道具_使用 制作指定食物 """

    TARGET_ADD_HUGE_LUBRICATION = 1001
    """ 道具_使用效果 交互对象增加大量润滑（润滑液） """
    TARGET_ADD_HUGE_DESIRE_AND_SUBMIT = 1002
    """ 道具_使用效果 交互对象增加大量欲情和屈服（媚药） """
    TARGET_ENEMA = 1003
    """ 道具_使用效果 交互对象A灌肠并增加中量润滑 """
    TARGET_ENEMA_END = 1004
    """ 道具_使用效果 交互对象结束A灌肠并增加中量润滑 """
    TARGET_ADD_URINATE = 1005
    """ 道具_使用效果 交互对象尿意值全满 """
    TARGET_DIURETICS_ON = 1006
    """ 道具_使用效果 交互对象获得利尿剂状态 """

    FIRST_KISS = 1101
    """ 初次 记录初吻 """
    FIRST_HAND_IN_HAND = 1102
    """ 初次 记录初次牵手 """
    FIRST_SEX = 1103
    """ 初次 记录处女 """
    FIRST_A_SEX = 1104
    """ 初次 记录A处女 """
