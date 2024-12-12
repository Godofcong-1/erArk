class BehaviorEffect:
    """行为结算效果函数"""

    NOTHING = 9999
    """ 系统量_基础 什么都没有的空结算 """
    OPTION_FATER = 10001
    """ 系统量_基础 开启子选项面板 """
    OPEN_INSTRUCT_FILTER_H = 10003
    """ 系统量_基础 开启H面板过滤器（已弃用） """
    CLOSE_INSTRUCT_FILTER_H = 10004
    """ 系统量_基础 关闭H面板过滤器（已弃用） """
    ADD_THIS_EVENT_TO_TRIGGERED_RECORD = 10008
    """ 系统量_基础 将玩家当前触发的事件加入已触发记录 """
    GROUP_SEX_MODE_ON = 10010
    """ 系统量_基础 开启群交模式 """
    GROUP_SEX_MODE_OFF = 10011
    """ 系统量_基础 关闭群交模式 """

    INTERRUPT_TARGET_ACTIVITY = 10000
    """ 系统量_交互 打断交互对象活动 """
    TARGET_TO_PLAYER = 10002
    """ 系统量_交互 将交互对象设为对玩家交互 """
    PL_TARGET_TO_ME = 10005
    """ 系统量_交互 将玩家的交互对象设为自己 """
    TARGET_TO_SELF = 10006
    """ 系统量_交互 将交互对象设为对自己交互 """
    TARGET_TO_MASTUREBATE = 10007
    """ 系统量_交互 将交互对象设为对当前场景中的首位自慰角色 """

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
    DOWN_BOTH_MEDIUM_HIT_POINT = 13
    """ 属性_基础 双方减少中量体力（若没有交互对象则仅减少自己） """
    DOWN_BOTH_MEDIUM_MANA_POINT = 14
    """ 属性_基础 双方减少中量气力（若没有交互对象则仅减少自己） """
    DOWN_BOTH_LARGE_HIT_POINT = 15
    """ 属性_基础 双方减少大量体力（若没有交互对象则仅减少自己） """
    DOWN_BOTH_LARGE_MANA_POINT = 16
    """ 属性_基础 双方减少大量气力（若没有交互对象则仅减少自己） """
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
    URINATE_POINT_ZERO = 32
    """ 属性_基础 尿意值归零 """
    TARGET_URINATE_POINT_ZERO = 33
    """ 属性_基础 交互对象尿意值归零 """
    HUNGER_POINT_ZERO = 34
    """ 属性_基础 饥饿值归零 """
    TARGET_HUNGER_POINT_ZERO = 35
    """ 属性_基础 交互对象饥饿值归零 """
    SLEEP_POINT_ZERO = 36
    """ 属性_基础 熟睡值归零 """
    TARGET_SLEEP_POINT_ZERO = 37
    """ 属性_基础 交互对象熟睡值归零 """
    ADD_SMALL_URINATE_POINT = 38
    """ 属性_基础 自己增加少量尿意值 """
    TARGET_ADD_SMALL_URINATE_POINT = 39
    """ 属性_基础 交互对象增加少量尿意值 """
    TARGET_DESIRE_POINT_ZERO = 40
    """ 属性_基础 交互对象欲望值归零 """
    DESIRE_POINT_TO_79 = 1501
    """ 属性_基础 自己欲望值调为79 """
    TARGET_DESIRE_POINT_TO_79 = 1502
    """ 属性_基础 交互对象欲望值调为79 """
    DESIRE_POINT_TO_0 = 1503
    """ 属性_基础 自己欲望值归零 """
    ADD_SMALL_SANITY_POINT = 1504
    """ 属性_基础 增加少量理智值(15%/h) """
    ADD_SMALL_SEMEN_POINT = 1505
    """ 属性_基础 增加少量精液值(15%/h) """
    DOWN_SELF_SMALL_HIT_POINT = 1511
    """ 属性_基础 减少自己少量体力 """
    DOWN_SELF_SMALL_MANA_POINT = 1512
    """ 属性_基础 减少自己少量气力 """
    DOWN_SELF_MEDIUM_HIT_POINT = 1513
    """ 属性_基础 减少自己中量体力 """
    DOWN_SELF_MEDIUM_MANA_POINT = 1514
    """ 属性_基础 减少自己中量气力 """
    DOWN_SELF_LARGE_HIT_POINT = 1515
    """ 属性_基础 减少自己大量体力 """
    DOWN_SELF_LARGE_MANA_POINT = 1516
    """ 属性_基础 减少自己大量气力 """
    MOOD_TO_GOOD = 1521
    """ 属性_基础 自己心情变为好 """
    MOOD_TO_NORMAL = 1522
    """ 属性_基础 自己心情变为普通 """
    MOOD_TO_BAD = 1523
    """ 属性_基础 自己心情变为不好 """
    MOOD_TO_ANGRY = 1524
    """ 属性_基础 自己心情变为愤怒 """
    TARGET_MOOD_TO_GOOD = 1525
    """ 属性_基础 交互对象心情变为好 """
    TARGET_MOOD_TO_NORMAL = 1526
    """ 属性_基础 交互对象心情变为普通 """
    TARGET_MOOD_TO_BAD = 1527
    """ 属性_基础 交互对象心情变为不好 """
    TARGET_MOOD_TO_ANGRY = 1528
    """ 属性_基础 交互对象心情变为愤怒 """
    SCENE_ALL_CHARACTERS_DESIRE_POINT_ZERO = 1531
    """ 属性_结构体 场景内所有角色欲望值归零 """


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
    ADD_SMALL_LEARN_OLD = 72
    """ 属性_状态 （旧占位符，现用81）自己增加少量习得（技巧补正） """
    ADD_SMALL_LUBRICATION = 80
    """ 属性_状态 自己增加少量润滑（欲望补正） """
    ADD_SMALL_LEARN = 81
    """ 属性_状态 自己增加少量习得（技巧补正） """
    ADD_SMALL_RESPECT = 82
    """ 属性_状态 自己增加少量恭顺（顺从补正） """
    ADD_SMALL_FRIENDLY = 83
    """ 属性_状态 自己增加少量好意（亲密补正） """
    ADD_SMALL_DESIRE = 84
    """ 属性_状态 自己增加少量欲情（欲望补正） """
    ADD_SMALL_HAPPY = 85
    """ 属性_状态 自己增加少量快乐（快乐刻印补正） """
    ADD_SMALL_LEAD = 86
    """ 属性_状态 自己增加少量先导（施虐补正） """
    ADD_SMALL_SUBMIT = 87
    """ 属性_状态 自己增加少量屈服（屈服刻印补正） """
    ADD_SMALL_SHY = 88
    """ 属性_状态 自己增加少量羞耻（露出补正） """

    TECH_ADD_N_ADJUST = 110
    """ 属性_状态特殊补正 根据发起者的技巧技能和交互对象的感度，对交互对象进行N快、欲情调整 """
    TECH_ADD_B_ADJUST = 111
    """ 属性_状态特殊补正 根据发起者的技巧技能和交互对象的感度，对交互对象进行B快、欲情调整 """
    TECH_ADD_C_ADJUST = 112
    """ 属性_状态特殊补正 根据发起者的技巧技能和交互对象的感度，对交互对象进行C快、欲情调整 """
    TECH_ADD_P_ADJUST = 113
    """ 属性_状态特殊补正 根据发起者的技巧技能和交互对象的感度，对交互对象进行P快、欲情调整 """
    TECH_ADD_V_ADJUST = 114
    """ 属性_状态特殊补正 根据发起者的技巧技能和交互对象的感度，对交互对象进行V快、欲情调整 """
    TECH_ADD_A_ADJUST = 115
    """ 属性_状态特殊补正 根据发起者的技巧技能和交互对象的感度，对交互对象进行A快、欲情调整 """
    TECH_ADD_U_ADJUST = 116
    """ 属性_状态特殊补正 根据发起者的技巧技能和交互对象的感度，对交互对象进行U快、欲情调整 """
    TECH_ADD_W_ADJUST = 117
    """ 属性_状态特殊补正 根据发起者的技巧技能和交互对象的感度，对交互对象进行W快、欲情调整 """
    TECH_ADD_PL_P_ADJUST = 120
    """ 属性_状态特殊补正 根据交互对象的技巧技能对发起者进行P快调整 """
    TARGET_LUBRICATION_ADJUST_ADD_PAIN = 121
    """ 属性_状态特殊补正 根据交互对象的润滑情况对其进行苦痛调整 """
    TARGET_V_ADJUST_ADD_PAIN = 122
    """ 属性_状态特殊补正 根据交互对象的V属性(润滑+腰技+扩张+阴茎大小)对其进行苦痛调整 """
    TARGET_A_ADJUST_ADD_PAIN = 123
    """ 属性_状态特殊补正 根据交互对象的A属性(润滑+腰技+扩张+阴茎大小)对其进行苦痛调整 """
    TARGET_U_ADJUST_ADD_PAIN = 124
    """ 属性_状态特殊补正 根据交互对象的U属性(润滑+腰技+扩张+阴茎大小)对其进行苦痛调整 """
    TARGET_W_ADJUST_ADD_PAIN = 125
    """ 属性_状态特殊补正 根据交互对象的W属性(润滑+腰技+扩张+阴茎大小)对其进行苦痛调整 """
    TARGET_V_ADJUST_ADD_BY_SEX = 131
    """ 属性_状态特殊补正 根据发起者的技巧+腰技+阴茎大小对交互目标进行V快、欲情调整 """
    TARGET_A_ADJUST_ADD_BY_SEX = 132
    """ 属性_状态特殊补正 根据发起者的技巧+腰技+阴茎大小对交互目标进行A快、欲情调整 """
    TARGET_U_ADJUST_ADD_BY_SEX = 133
    """ 属性_状态特殊补正 根据发起者的技巧+腰技+阴茎大小对交互目标进行U快、欲情调整 """
    TARGET_W_ADJUST_ADD_BY_SEX = 134
    """ 属性_状态特殊补正 根据发起者的技巧+腰技+阴茎大小对交互目标进行W快、欲情调整 """

    FINGER_TECH_ADD_PL_P_ADJUST = 141
    """ 属性_状态特殊补正 根据交互对象的技巧+指技对发起者进行P快调整 """
    TONGUE_TECH_ADD_PL_P_ADJUST = 142
    """ 属性_状态特殊补正 根据交互对象的技巧+舌技对发起者进行P快调整 """
    FEET_TECH_ADD_PL_P_ADJUST = 143
    """ 属性_状态特殊补正 根据交互对象的技巧+足技对发起者进行P快调整 """
    BREAST_TECH_ADD_PL_P_ADJUST = 144
    """ 属性_状态特殊补正 根据交互对象的技巧+胸技对发起者进行P快调整 """
    VAGINA_TECH_ADD_PL_P_ADJUST = 145
    """ 属性_状态特殊补正 根据交互对象的技巧+膣技对发起者进行P快调整 """
    ANUS_TECH_ADD_PL_P_ADJUST = 146
    """ 属性_状态特殊补正 根据交互对象的技巧+肛技对发起者进行P快调整 """

    LOW_OBSCENITY_FAILED_ADJUST = 151
    """ 属性_失败状态 轻度性骚扰失败的加反感、加愤怒、降好感度修正 """
    HIGH_OBSCENITY_FAILED_ADJUST = 152
    """ 属性_失败状态 重度性骚扰失败的加反感、加愤怒、降好感度、降信赖修正 """
    DO_H_FAILED_ADJUST = 153
    """ 属性_失败状态 邀请H失败的加反感、加愤怒、降好感度、降信赖修正 """

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
    """ 属性_经验 交互对象增加1N绝顶经验+1绝顶经验 """
    TARGET_ADD_1_BClimax_EXPERIENCE = 211
    """ 属性_经验 交互对象增加1B绝顶经验+1绝顶经验 """
    TARGET_ADD_1_CClimax_EXPERIENCE = 212
    """ 属性_经验 交互对象增加1C绝顶经验+1绝顶经验 """
    TARGET_ADD_1_VClimax_EXPERIENCE = 214
    """ 属性_经验 交互对象增加1V绝顶经验+1绝顶经验 """
    TARGET_ADD_1_AClimax_EXPERIENCE = 215
    """ 属性_经验 交互对象增加1A绝顶经验+1绝顶经验 """
    TARGET_ADD_1_UClimax_EXPERIENCE = 216
    """ 属性_经验 交互对象增加1U绝顶经验+1绝顶经验 """
    TARGET_ADD_1_WClimax_EXPERIENCE = 217
    """ 属性_经验 交互对象增加1W绝顶经验+1绝顶经验 """
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
    TARGET_ADD_1_UnconsciouslySex_EXPERIENCE = 279
    """ 属性_经验 交互对象增加1无意识性交经验 """
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
    ADD_1_Cumming_EXPERIENCE = 331
    """ 属性_经验 增加1射精经验 """
    ADD_1_Milking_EXPERIENCE = 332
    """ 属性_经验 增加1喷乳经验 """
    ADD_1_Peeing_EXPERIENCE = 333
    """ 属性_经验 增加1放尿经验 """
    ADD_1_Cums_EXPERIENCE = 334
    """ 属性_经验 增加1精液经验 """
    ADD_1_CumsDrink_EXPERIENCE = 335
    """ 属性_经验 增加1饮精经验 """
    ADD_1_Creampie_EXPERIENCE = 336
    """ 属性_经验 增加1膣射经验 """
    ADD_1_AnalCums_EXPERIENCE = 337
    """ 属性_经验 增加1肛射经验 """
    ADD_1_Hypnosis_EXPERIENCE = 338
    """ 属性_经验 增加1催眠经验 """
    TARGET_ADD_1_BEEN_Hypnosis_EXPERIENCE = 339
    """ 属性_经验 交互对象增加1被催眠经验 """
    PLACE_ALL_CHARA_ADD_1_BEEN_Hypnosis_EXPERIENCE = 340
    """ 属性_经验 场景内所有其他角色均增加1被催眠经验 """
    ADD_1_Agriculture_EXPERIENCE = 341
    """ 属性_经验 增加1农业经验 """
    ADD_1_Create_EXPERIENCE = 342
    """ 属性_经验 增加1制造经验 """
    ADD_1_Paint_EXPERIENCE = 343
    """ 属性_经验 增加1绘画经验 """
    ADD_1_Read_EXPERIENCE = 344
    """ 属性_经验 增加1阅读经验 """
    ADD_1_Read_H_EXPERIENCE = 345
    """ 属性_经验 增加1H书阅读经验 """
    Both_ADD_1_Learn_EXPERIENCE = 350
    """ 属性_经验 双方增加1学识经验 """
    ADD_1_Masterbate_EXPERIENCE = 351
    """ 属性_经验 增加1自慰经验 """
    ADD_1_Sleep_Sex_EXPERIENCE = 352
    """ 属性_经验 增加1睡姦经验 """
    ADD_1_be_Sleep_Sex_EXPERIENCE = 353
    """ 属性_经验 增加1被睡姦经验 """
    TARGET_ADD_1_be_Sleep_Sex_EXPERIENCE = 354
    """ 属性_经验 交互对象增加1被睡姦经验 """
    ADD_1_Time_Stop_Sex_EXPERIENCE = 355
    """ 属性_经验 增加1时姦经验 """
    ADD_1_be_Time_Stop_Sex_EXPERIENCE = 356
    """ 属性_经验 增加1被时姦经验 """
    TARGET_ADD_1_be_Time_Stop_Sex_EXPERIENCE = 357
    """ 属性_经验 交互对象增加1被时姦经验 """
    ADD_1_Hypnosis_Sex_EXPERIENCE = 358
    """ 属性_经验 增加1催眠姦经验 """
    ADD_1_be_Hypnosis_Sex_EXPERIENCE = 359
    """ 属性_经验 增加1被催眠姦经验 """
    TARGET_ADD_1_be_Hypnosis_Sex_EXPERIENCE = 360
    """ 属性_经验 交互对象增加1被催眠姦经验 """
    TARGET_ADD_1_CLOTH_JOB_EXPERIENCE = 361
    """ 属性_经验 交互对象增加1服装交经验 """
    ADD_1_GROUP_SEX_EXPERIENCE = 362
    """ 属性_经验 增加1群交经验 """

    DIRTY_RESET = 401
    """ 属性_结构体 污浊结构体归零 """
    ASSISTANT_RESET = 402
    """ 属性_结构体 助理结构体归零 """
    SELF_H_STATE_RESET = 403
    """ 属性_结构体 自己H状态结构体归零，同步高潮程度记录，清零H相关二段状态 """
    BOTH_H_STATE_RESET = 404
    """ 属性_结构体 双方H状态结构体归零，同步高潮程度记录，清零H相关二段状态 """
    UPDATE_ORGASM_LEVEL = 405
    """ 属性_结构体 双方同步高潮程度记录 """
    SCENE_ALL_CHARACTERS_UPDATE_ORGASM_LEVEL = 406
    """ 属性_结构体 场景内所有角色同步高潮程度记录 """
    SCENE_ALL_CHARACTERS_H_STATE_RESET = 407
    """ 属性_结构体 场景内所有角色H状态结构体归零，同步高潮程度记录，清零H相关二段状态 """
    CHARA_OFF_LINE = 411
    """ 属性_结构体 角色离线，归零若干数据结构体，从当前干员列表中移除，离开地图 """
    CHARA_ON_LINE = 412
    """ 属性_结构体 角色上线，加入从当前干员列表，进入地图 """

    T_BE_BAGGED = 451
    """ 属性_特殊flag 交互对象变成被装袋搬走状态 """
    T_BE_IMPRISONMENT = 452
    """ 属性_特殊flag 交互对象变成被监禁状态 """
    SHOWER_FLAG_TO_1 = 453
    """ 属性_特殊flag 自身变成要脱衣服（洗澡）状态 """
    SHOWER_FLAG_TO_2 = 454
    """ 属性_特殊flag 自身变成要洗澡状态 """
    SHOWER_FLAG_TO_3 = 455
    """ 属性_特殊flag 自身变成要披浴巾状态 """
    SHOWER_FLAG_TO_4 = 456
    """ 属性_特殊flag 自身变成洗完澡状态 """
    EAT_FOOD_FLAG_TO_0 = 457
    """ 属性_特殊flag 自身清零吃饭状态 """
    EAT_FOOD_FLAG_TO_1 = 458
    """ 属性_特殊flag 自身变成要取餐状态 """
    EAT_FOOD_FLAG_TO_2 = 459
    """ 属性_特殊flag 自身变成要进食状态 """
    SLEEP_FLAG_TO_0 = 460
    """ 属性_特殊flag 自身清零要睡眠状态 """
    SLEEP_FLAG_TO_1 = 461
    """ 属性_特殊flag 自身变成要睡眠状态 """
    REST_FLAG_TO_0 = 462
    """ 属性_特殊flag 自身清零要休息状态 """
    REST_FLAG_TO_1 = 463
    """ 属性_特殊flag 自身变成要休息状态 """
    PEE_FLAG_TO_0 = 464
    """ 属性_特殊flag 自身清零要撒尿状态 """
    PEE_FLAG_TO_1 = 465
    """ 属性_特殊flag 自身变成要撒尿状态 """
    SWIM_FLAG_TO_1 = 466
    """ 属性_特殊flag 自身变成要换泳衣状态 """
    SWIM_FLAG_TO_2 = 467
    """ 属性_特殊flag 自身变成要游泳状态 """
    MAINTENANCE_FLAG_TO_0 = 468
    """ 属性_特殊flag 自身清零要检修状态 """
    CANCEL_ALL_WORK_AND_ENTERTAINMENT_FLAG = 469
    """ 属性_特殊flag 自身取消所有工作和娱乐状态 """
    H_FLAG_TO_0 = 475
    """ 属性_特殊flag 自身清零H状态 """
    H_FLAG_TO_1 = 476
    """ 属性_特殊flag 自身变成H状态 """
    T_H_FLAG_TO_0 = 477
    """ 属性_特殊flag 交互对象清零H状态 """
    T_H_FLAG_TO_1 = 478
    """ 属性_特殊flag 交互对象变成H状态 """
    SCENE_ALL_CHARACTERS_H_FLAG_TO_1 = 479
    """ 属性_特殊flag 场景内所有角色变成H状态 """
    UNCONSCIOUS_FLAG_TO_0 = 481
    """ 属性_特殊flag 自身清零无意识状态 """
    UNCONSCIOUS_FLAG_TO_1 = 482
    """ 属性_特殊flag 自身变成无意识_睡眠状态 """
    UNCONSCIOUS_FLAG_TO_2 = 483
    """ 属性_特殊flag 自身变成无意识_醉酒状态 """
    UNCONSCIOUS_FLAG_TO_3 = 484
    """ 属性_特殊flag 自身变成无意识_时停状态 """
    UNCONSCIOUS_FLAG_TO_4 = 485
    """ 属性_特殊flag 自身变成无意识_空气状态 """
    UNCONSCIOUS_FLAG_TO_5 = 486
    """ 属性_特殊flag 自身变成无意识_平然状态 """
    UNCONSCIOUS_FLAG_TO_6 = 487
    """ 属性_特殊flag 自身变成无意识_心控状态 """
    UNCONSCIOUS_FLAG_TO_7 = 488
    """ 属性_特殊flag 自身变成无意识_体控状态 """
    HELP_BUY_FOOD_FLAG_TO_0 = 489
    """ 属性_特殊flag 自身清零要帮忙买午饭状态 """
    HELP_MAKE_FOOD_FLAG_TO_0 = 490
    """ 属性_特殊flag 自身清零做午饭状态 """
    BATHHOUSE_ENTERTAINMENT_FLAG_TO_0 = 491
    """ 属性_特殊flag 自身清零大浴场娱乐状态 """
    BATHHOUSE_ENTERTAINMENT_FLAG_TO_1 = 492
    """ 属性_特殊flag 自身变成大浴场娱乐_要更衣状态 """
    BATHHOUSE_ENTERTAINMENT_FLAG_TO_2 = 493
    """ 属性_特殊flag 自身变成大浴场娱乐_要娱乐状态 """
    MILK_FLAG_TO_0 = 494
    """ 属性_特殊flag 自身清零要挤奶状态 """
    HYPNOSIS_FLAG_TO_0 = 495
    """ 属性_特殊flag 自身清零催眠系的flag状态 """
    TARGET_ANGRY_WITH_PLAYER_FLAG_TO_0 = 496
    """ 属性_特殊flag 交互对象清零对玩家的愤怒状态 """
    MASTUREBATE_FLAG_TO_0 = 497
    """ 属性_特殊flag 自身清零要自慰状态 """
    MASTUREBATE_BEFORE_SLEEP_FLAG_TO_0 = 498
    """ 属性_特殊flag 自身清零要睡前自慰状态 """
    MASTUREBATE_BEFORE_SLEEP_FLAG_TO_2 = 499
    """ 属性_特殊flag 自身变为已睡前自慰状态 """

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
    OFFICIAL_WORK_ADD_ADJUST = 506
    """ 指令_专用结算 （处理公务用）根据自己（如果有的话再加上交互对象）的学识以及办公室等级来处理当前的剩余工作量 """
    CURE_PATIENT_ADD_ADJUST = 507
    """ 指令_专用结算 （诊疗病人用）根据发起者(如果有的话再加上交互对象)的医疗技能治愈了一名病人，并获得一定的龙门币 """
    ADD_HPMP_MAX = 508
    """ 指令_专用结算 （锻炼身体用）增加体力气力上限 """
    SLEEP_ADD_ADJUST = 509
    """ 指令_专用结算 （睡觉用）如果在自己宿舍，则换睡衣并有一定几率关门 """
    RECRUIT_ADD_ADJUST = 510
    """ 指令_专用结算 （招募干员用）根据发起者(如果有的话再加上交互对象)的话术技能增加招募槽 """
    READ_ADD_ADJUST = 511
    """ 指令_专用结算 （读书用）根据书的不同对发起者(如果有的话再加上交互对象)获得对应的知识，并进行NPC的还书判定 """
    TEACH_ADD_ADJUST = 512
    """ 指令_专用结算 （教学用）自己增加习得和学识经验，所有当前场景里状态是上课的角色增加习得和学识经验，如果玩家是老师则再加好感和信赖，最后结束 """
    BAGGING_AND_MOVING_ADD_ADJUST = 513
    """ 指令_专用结算 （装袋搬走用）交互对象获得装袋搬走flag，玩家增加搬运人id，对方离线 """
    PUT_INTO_PRISON_ADD_ADJUST = 514
    """ 指令_专用结算 （投入监牢用）玩家失去搬运人id，玩家搬运的角色失去装袋搬走flag，获得监禁flag，获得屈服1，反发2和恐怖1，并从当前场景增加角色id，清零各特殊状态flag """
    SET_FREE_ADD_ADJUST = 515
    """ 指令_专用结算 （解除囚禁）交互对象失去监禁flag """
    EAT_ADD_ADJUST = 516
    """ 指令_专用结算 （进食）食物结算。会根据有无交互目标，食物的调味来自动判别食用对象和结算内容。需要搭配删除当前食物食用 """
    # REFUSE_EAT_ADD_ADJUST = 517
    # """ 指令_专用结算 （拒绝进食）吃掉该食物 """
    INVITE_VISITOR_ADD_ADJUST = 518
    """ 指令_专用结算 （邀请访客用）根据发起者(如果有的话再加上交互对象)的话术技能增加邀请槽 """
    MILK_ADD_ADJUST = 519
    """ 指令_专用结算 （挤奶用）把交互对象的乳汁转移到厨房的冰箱里 """
    #TODO 转移到随身道具上，之后到饭点了的时候再放到厨房里
    SALUTATION_3_ADD_ADJUST = 520
    """ 指令_专用结算 （早安咬与晚安咬）触发交互对象一次射精，射到发起者嘴里 """
    AROMATHERAPY_ADD_ADJUST = 521
    """ 指令_专用结算 （香薰疗愈用）对各配方结算各效果 """
    URETHRAL_SWAB_ADD_ADJUST = 522
    """ 指令_专用结算 （尿道棉棒用）根据交互对象的U属性(润滑+扩张)对其进行苦痛调整 """
    URETHRAL_FINGER_INSERTION_ADD_ADJUST = 523
    """ 指令_专用结算 （尿道指姦用）根据交互对象的U属性(润滑+扩张)对其进行苦痛调整 """
    MASTUREBATE_ADD_ADJUST = 524
    """ 指令_专用结算 （自慰用）选择自己最高感度的部位，增加该部位快感和经验 """
    DIRTY_RESET_IN_SHOWER = 525
    """ 指令_专用结算 自身部分部位污浊保留一定比例，其他污浊体归零 """
    ORGASM_EDGE_RELEASE = 526
    """ 指令_专用结算 （绝顶解放）交互对象变为寸止解放状态，将寸止计数转化为绝顶 """
    TIME_STOP_ORGASM_RELEASE = 527
    """ 指令_专用结算 （解除时停）所有角色变为时停解放状态，将时停绝顶计数转化为绝顶 """
    END_H_ADD_HPMP_MAX = 528
    """ 指令_专用结算 （结束H）自己和交互对象根据本次H中的绝顶次数增加体力气力上限，玩家根据射精次数增加精液量上限 """
    GROUP_SEX_END_H_ADD_HPMP_MAX = 529
    """ 指令_专用结算 （群交结束H）在场全部角色根据本次H中的绝顶次数增加体力气力上限，玩家根据射精次数增加精液量上限 """
    GROUP_SEX_FAIL_ADD_JUST = 530
    """ 指令_专用结算 （群交失败）在场全部角色减体力气力，拒绝者进行邀请H失败结算 """
    BOARD_GAME_WIN_ADD_ADJUST = 532
    """ 指令_专用结算 （桌游获胜用）根据游戏难度获得好感度、信赖、习得、粉红凭证 """
    BOARD_GAME_LOSE_ADD_ADJUST = 533
    """ 指令_专用结算 （桌游输了用）根据游戏难度获得好感度、习得 """

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
    SCENE_ALL_CHARACTERS_BRA_PAN_SEE = 608
    """ 属性_服装 场景内所有角色胸罩、内裤可视 """
    GET_T_PAN = 621
    """ 属性_服装 获得交互对象的内裤 """
    GET_T_SOCKS = 622
    """ 属性_服装 获得交互对象的袜子 """
    GET_SCENE_T_PAN = 623
    """ 属性_服装 获得场景内所有其他角色的内裤 """
    GET_SCENE_T_SOCKS = 624
    """ 属性_服装 获得场景内所有其他角色的袜子 """
    T_CLOTH_BACK = 631
    """ 属性_服装 交互对象穿回H时脱掉的衣服 """
    WEAR_CLOTH_OFF = 632
    """ 属性_服装 脱掉全部衣服 """
    GET_SHOWER_CLOTH = 633
    """ 属性_服装 清零其他衣服并换上浴帽和浴巾 """
    GET_SLEEP_CLOTH = 634
    """ 属性_服装 清零其他衣服并换上睡衣（管理中则全裸） """
    SELF_CLOTH_BACK = 635
    """ 属性_服装 自己穿回H时脱掉的衣服 """
    SCENE_ALL_CHARACTERS_CLOTH_BACK = 636
    """ 属性_服装 场景内所有角色穿回H时脱掉的衣服 """
    LOCKER_CLOTH_IN_SHOWER_RESET = 641
    """ 属性_服装 大浴场衣柜里的衣服清零 """
    WEAR_TO_SHOWER_LOCKER = 642
    """ 属性_服装 身上首饰以外的衣服转移到大浴场柜子里 """
    SHOWER_LOCKER_TO_WEAR = 643
    """ 属性_服装 大浴场衣柜里的衣服转移到身上 """
    GET_SWIM_CLOTH = 644
    """ 属性_服装 清零其他衣服并换上泳衣 """
    WEAR_CLOTH_OFF_MOST = 645
    """ 属性_服装 脱掉大部分衣服（保留首饰等） """
    FOOT_CLOTH_TO_SHOWER_LOCKER = 646
    """ 属性_服装 袜子和鞋子转移到大浴场衣柜里 """
    SHOWER_LOCKER_TO_DORMITORY_LOCKER = 647
    """ 属性_服装 大浴场衣柜里的衣服转移到宿舍衣柜 """
    CLEAN_LOCKER_CLOTH_SEMEN = 648
    """ 属性_服装 清理衣柜里的衣服精液 """
    GET_CLOTH_FROM_DORMITORY_LOCKER = 649
    """ 属性_服装 清空身上的旧衣服，从宿舍的衣柜里穿上衣服、内衣内裤，并转移衣柜中的精液数据到穿着的衣服上 """
    UP_AND_BRA_TO_TEM = 651
    """ 属性_服装 自己的上衣和胸罩转移到临时脱下 """
    DOWN_AND_PAN_TO_TEM = 652
    """ 属性_服装 自己的下衣和内裤转移到临时脱下 """
    TARGET_UP_AND_BRA_TO_TEM = 653
    """ 属性_服装 交互对象的上衣和胸罩转移到临时脱下 """
    TARGET_DOWN_AND_PAN_TO_TEM = 654
    """ 属性_服装 交互对象的下衣和内裤转移到临时脱下 """

    RECORD_TRAINING_TIME = 701
    """ 系统量_时间 角色记录并刷新训练时间 """
    RECORD_SHOWER_TIME = 702
    """ 系统量_时间 角色记录并刷新淋浴时间 """
    RECORD_WAKE_TIME = 703
    """ 系统量_时间 角色记录并刷新起床时间 """

    MOVE_TO_TARGET_SCENE = 751
    """ 系统量_地点 移动至目标场景 """
    DOOR_CLOSE = 752
    """ 系统量_地点 当前场景进入关门状态 """
    DOOR_CLOSE_RESET = 753
    """ 系统量_地点 当前场景取消关门状态 """
    MOVE_TO_PRE_SCENE = 761
    """ 系统量_地点 角色移动至前一场景 """

    SCENE_ALL_CHARACTERS_PENIS_IN_RESET = 800
    """ H_阴茎位置 场景内所有角色的当前阴茎位置归零 """
    PENIS_IN_T_RESET = 801
    """ H_阴茎位置 改变当前阴茎位置为交互对象_双方归零 """
    PENIS_IN_T_HAIR = 802
    """ H_阴茎位置 改变当前阴茎位置为交互对象_发交中 """
    PENIS_IN_T_FACE = 803
    """ H_阴茎位置 改变当前阴茎位置为交互对象_阴茎蹭脸中 """
    PENIS_IN_T_MOUSE = 804
    """ H_阴茎位置 改变当前阴茎位置为交互对象_口交中 """
    PENIS_IN_T_BREAST = 805
    """ H_阴茎位置 改变当前阴茎位置为交互对象_乳交中 """
    PENIS_IN_T_AXILLA = 806
    """ H_阴茎位置 改变当前阴茎位置为交互对象_腋交中 """
    PENIS_IN_T_HAND = 807
    """ H_阴茎位置 改变当前阴茎位置为交互对象_手交中 """
    PENIS_IN_T_VAGINA = 808
    """ H_阴茎位置 改变当前阴茎位置为交互对象_V插入中 """
    PENIS_IN_T_WOMB = 809
    """ H_阴茎位置 改变当前阴茎位置为交互对象_W插入中 """
    PENIS_IN_T_ANAL = 810
    """ H_阴茎位置 改变当前阴茎位置为交互对象_A插入中 """
    PENIS_IN_T_URETHRAL = 811
    """ H_阴茎位置 改变当前阴茎位置为交互对象_U插入中 """
    PENIS_IN_T_LEG = 812
    """ H_阴茎位置 改变当前阴茎位置为交互对象_腿交中 """
    PENIS_IN_T_FOOT = 813
    """ H_阴茎位置 改变当前阴茎位置为交互对象_足交中 """
    PENIS_IN_T_TAIL = 814
    """ H_阴茎位置 改变当前阴茎位置为交互对象_尾交中 """
    PENIS_IN_T_HORN = 815
    """ H_阴茎位置 改变当前阴茎位置为交互对象_阴茎蹭角中 """
    PENIS_IN_T_EARS = 816
    """ H_阴茎位置 改变当前阴茎位置为交互对象_阴茎蹭耳朵中 """
    PENIS_IN_T_HAT = 821
    """ H_阴茎位置 改变当前阴茎位置为交互对象_帽子交中 """
    PENIS_IN_T_GLASSES = 822
    """ H_阴茎位置 改变当前阴茎位置为交互对象_眼镜交中 """
    PENIS_IN_T_EAR_ORNAMENT = 823
    """ H_阴茎位置 改变当前阴茎位置为交互对象_耳饰交中 """
    PENIS_IN_T_NECK_ORNAMENT = 824
    """ H_阴茎位置 改变当前阴茎位置为交互对象_脖饰交中 """
    PENIS_IN_T_MOUTH_ORNAMENT = 825
    """ H_阴茎位置 改变当前阴茎位置为交互对象_口罩交中 """
    PENIS_IN_T_TOP = 826
    """ H_阴茎位置 改变当前阴茎位置为交互对象_上衣交中 """
    PENIS_IN_T_CORSET = 827
    """ H_阴茎位置 改变当前阴茎位置为交互对象_胸衣交中 """
    PENIS_IN_T_GLOVES = 828
    """ H_阴茎位置 改变当前阴茎位置为交互对象_手套交中 """
    PENIS_IN_T_SKIRT = 829
    """ H_阴茎位置 改变当前阴茎位置为交互对象_裙子交中 """
    PENIS_IN_T_UNDERWEAR = 830
    """ H_阴茎位置 改变当前阴茎位置为交互对象_内裤交中 """
    PENIS_IN_T_SOCKS = 831
    """ H_阴茎位置 改变当前阴茎位置为交互对象_袜子交中 """
    PENIS_IN_T_SHOES = 832
    """ H_阴茎位置 改变当前阴茎位置为交互对象_鞋子交中 """
    PENIS_IN_T_WEAPONS = 833
    """ H_阴茎位置 改变当前阴茎位置为交互对象_武器交中 """
    PENIS_IN_T_TROUSERS = 834
    """ H_阴茎位置 改变当前阴茎位置为交互对象_裤子交中 """
    CANCEL_PENIS_IN_FACE_OR_MOUSE = 840
    """ H_阴茎位置 取消为阴茎位置交互对象_阴茎蹭脸中和口交中 """

    H_IN_LOVE_HOTEL_TO_FALSE = 871
    """ H_地点 取消自己和交互对象正在爱情旅馆中H的状态 """

    ITEM_OFF = 901
    """ 道具_增减 去掉身上所有的H道具（含药品） """
    TARGET_ITEM_OFF = 902
    """ 道具_增减 交互对象去掉身上所有的道具（含药品） """
    ITEM_OFF_EXCEPT_PILL = 903
    """ 道具_增减 去掉身上所有的H道具（不含药品） """
    TARGET_ITEM_OFF_EXCEPT_PILL = 904
    """ 道具_增减 交互对象去掉身上所有的道具（不含药品） """
    TARGET_B_ITEM_OFF = 905
    """ 道具_增减 交互对象去掉B部位的道具 """
    TARGET_A_ITEM_OFF = 906
    """ 道具_增减 交互对象去掉A部位的道具 """
    TARGET_VIBRATOR_ON = 911
    """ 道具_增减 交互对象插入V震动棒 """
    TARGET_VIBRATOR_OFF = 912
    """ 道具_增减 交互对象拔出V震动棒 """
    TARGET_ANAL_VIBRATOR_ON = 913
    """ 道具_增减 交互对象插入A震动棒 """
    TARGET_ANAL_VIBRATOR_OFF = 914
    """ 道具_增减 交互对象拔出A震动棒 """
    TARGET_NIPPLE_CLAMP_ON = 915
    """ 道具_增减 交互对象戴上乳头夹 """
    TARGET_NIPPLE_CLAMP_OFF = 916
    """ 道具_增减 交互对象取下乳头夹 """
    TARGET_CLIT_CLAMP_ON = 917
    """ 道具_增减 交互对象戴上阴蒂夹 """
    TARGET_CLIT_CLAMP_OFF = 918
    """ 道具_增减 交互对象取下阴蒂夹 """
    TARGET_ANAL_BEADS_ON = 919
    """ 道具_增减 交互对象塞入肛门拉珠 """
    TARGET_ANAL_BEADS_OFF = 920
    """ 道具_增减 交互对象拔出肛门拉珠 """
    TARGET_MILKING_MACHINE_ON = 921
    """ 道具_增减 交互对象戴上搾乳机 """
    TARGET_MILKING_MACHINE_OFF = 922
    """ 道具_增减 交互对象取下搾乳机 """
    TARGET_URINE_COLLECTOR_ON = 923
    """ 道具_增减 交互对象戴上采尿器 """
    TARGET_URINE_COLLECTOR_OFF = 924
    """ 道具_增减 交互对象取下采尿器 """
    ADJUST_BODY_MANAGE_DAY_ITEM = 931
    """ 道具_增减 调整自己的身体管理_白天道具 """
    ADJUST_BODY_MANAGE_SLEEP_ITEM = 932
    """ 道具_增减 调整自己的身体管理_睡觉道具 """
    USE_BODY_LUBRICANT = 941
    """ 道具_增减 使用了一个润滑液 """
    USE_PHILTER = 942
    """ 道具_增减 使用了一个媚药 """
    USE_ENEMAS = 943
    """ 道具_增减 使用了一个灌肠液 """
    USE_DIURETICS_ONCE = 944
    """ 道具_增减 使用了一个一次性利尿剂 """
    USE_DIURETICS_PERSISTENT = 945
    """ 道具_增减 使用了一个持续性利尿剂 """
    USE_SLEEPING_PILLS = 946
    """ 道具_增减 使用了一个安眠药 """
    USE_OVULATION_PROMOTING_DRUGS = 947
    """ 道具_增减 使用了一个排卵促进药 """
    USE_CONTRACEPTIVE_BEFORE = 948
    """ 道具_增减 使用了一个事前避孕药 """
    USE_CONTRACEPTIVE_AFTER = 949
    """ 道具_增减 使用了一个事后避孕药 """
    USE_RING = 950
    """ 道具_增减 使用了一个戒指 """
    USE_COLLAR = 951
    """ 道具_增减 使用了一个项圈 """
    USE_BAG = 952
    """ 道具_增减 使用了一个干员携袋 """
    USE_CONDOM = 953
    """ 道具_增减 使用了一个避孕套 """
    USE_URETHRAL_SWAB = 954
    """ 道具_增减 使用了一个尿道棉棒 """
    DELETE_FOOD = 991
    """ 道具_增减 删除当前行动中的对象食物 """
    MAKE_FOOD = 992
    """ 道具_增减 结算因为制作食物而加好感 """
    NPC_MAKE_FOOD_TO_SHOP = 993
    """ 道具_增减 NPC随机制作一个食物，并补充到当前所在食物商店中 """
    DELETE_ALL_FOOD = 994
    """ 道具_增减 删除背包内所有食物 """
    NPC_MAKE_FOOD_TO_BAG = 995
    """ 道具_增减 NPC随机制作一个食物，并补充到自己背包中 """

    TARGET_ADD_HUGE_LUBRICATION = 1001
    """ 道具_使用效果 交互对象增加大量润滑（润滑液） """
    TARGET_ADD_HUGE_DESIRE_AND_SUBMIT = 1002
    """ 道具_使用效果 交互对象增加大量欲情和屈服和欲望值（媚药） """
    TARGET_ENEMA = 1003
    """ 道具_使用效果 交互对象A灌肠并增加中量润滑 """
    TARGET_ENEMA_END = 1004
    """ 道具_使用效果 交互对象结束A灌肠并增加中量润滑 """
    TARGET_ADD_URINATE = 1005
    """ 道具_使用效果 交互对象尿意值全满 """
    TARGET_DIURETICS_ON = 1006
    """ 道具_使用效果 交互对象获得利尿剂状态 """
    TARGET_ADD_TIRED_TO_SLEEP = 1007
    """ 道具_使用效果 交互对象疲劳值全满，进入8h的睡眠 """
    TARGET_ADD_PREGNANCY_CHANCE = 1008
    """ 道具_使用效果 交互对象获得排卵促进药状态 """
    TARGET_NO_PREGNANCY_NEXT_DAY = 1009
    """ 道具_使用效果 交互对象获得事前避孕药状态 """
    TARGET_NO_PREGNANCY_FROM_LAST_H = 1010
    """ 道具_使用效果 交互对象获得事后避孕药状态 """
    WEAR_CONDOM = 1011
    """ 道具_使用效果 自己获得戴上避孕套状态 """
    TAKE_CONDOM_OFF = 1012
    """ 道具_使用效果 自己去掉戴上避孕套状态 """

    FIRST_KISS = 1101
    """ 初次 记录初吻 """
    FIRST_HAND_IN_HAND = 1102
    """ 初次 记录初次牵手 """
    FIRST_SEX = 1103
    """ 初次 记录处女 """
    FIRST_A_SEX = 1104
    """ 初次 记录A处女 """
    DAY_FIRST_MEET_0 = 1105
    """ 初次 自己变为今天已见过面 """
    DAY_FIRST_MEET_1 = 1106
    """ 初次 自己变为今天未见过面 """
    FIRST_KISS_TO_PENIS = 1107
    """ 初次 记录阴茎初吻 """

    PENETRATING_VISION_ON = 1201
    """ 源石技艺 开启透视（含理智消耗） """
    PENETRATING_VISION_OFF = 1202
    """ 源石技艺 关闭透视 """
    HORMONE_ON = 1203
    """ 源石技艺 开启信息素 """
    HORMONE_OFF = 1204
    """ 源石技艺 关闭信息素 """
    HYPNOSIS_ONE = 1211
    """ 源石技艺 单人催眠（含理智消耗） """
    HYPNOSIS_ALL = 1212
    """ 源石技艺 集体催眠（含理智消耗） """
    HYPNOSIS_CANCEL = 1213
    """ 源石技艺 解除交互对象的催眠 """
    TARGET_HYPNOSIS_INCREASE_BODY_SENSITIVITY_ON = 1221
    """ 源石技艺 对方开启体控-敏感度提升（含理智消耗） """
    TARGET_HYPNOSIS_INCREASE_BODY_SENSITIVITY_OFF = 1222
    """ 源石技艺 对方关闭体控-敏感度提升 """
    TARGET_HYPNOSIS_FORCE_CLIMAX = 1223
    """ 源石技艺 对方体控-强制高潮（含理智消耗） """
    TARGET_HYPNOSIS_FORCE_OVULATION_ON = 1224
    """ 源石技艺 对方开启体控-强制排卵（含理智消耗） """
    TARGET_HYPNOSIS_FORCE_OVULATION_OFF = 1225
    """ 源石技艺 对方关闭体控-强制排卵 """
    TARGET_HYPNOSIS_BLOCKHEAD_SWITCH_CHANGE = 1226
    """ 源石技艺 对方切换体控-木头人开关（含理智消耗） """
    TARGET_HYPNOSIS_BLOCKHEAD_OFF = 1227
    """ 源石技艺 对方关闭体控-木头人 """
    TARGET_HYPNOSIS_ACTIVE_H_SWITCH_CHANGE = 1228
    """ 源石技艺 对方切换体控-逆推开关（含理智消耗） """
    TARGET_HYPNOSIS_ACTIVE_H_OFF = 1229
    """ 源石技艺 对方关闭体控-逆推 """
    TARGET_HYPNOSIS_PAIN_AS_PLEASURE_SWITCH_CHANGE = 1230
    """ 源石技艺 对方切换心控-苦痛快感化开关（含理智消耗） """
    TARGET_HYPNOSIS_PAIN_AS_PLEASURE_OFF = 1231
    """ 源石技艺 对方关闭心控-苦痛快感化 """
    TIME_STOP_ON = 1241
    """ 源石技艺 开启时停 """
    TIME_STOP_OFF = 1242
    """ 源石技艺 关闭时停 """
    TARGET_BE_CARRIED_IN_TIME_STOP = 1243
    """ 源石技艺 将交互对象设为当前时停搬运对象 """
    TARGET_NOT_BE_CARRIED_IN_TIME_STOP = 1244
    """ 源石技艺 清零自己的当前时停搬运对象 """
    TARGET_BE_FREE_IN_TIME_STOP = 1245
    """ 源石技艺 将交互对象设为时停中自由状态（含理智消耗） """
    TARGET_NOT_BE_FREE_IN_TIME_STOP = 1246
    """ 源石技艺 清零自己的让某人时停中自由状态 """

    NPC_ACTIVE_H_ON = 1401
    """ 属性_H 自己开启主动H """
    NPC_ACTIVE_H_OFF = 1402
    """ 属性_H 自己关闭主动H """
    TARGET_NPC_ACTIVE_H_ON = 1403
    """ 属性_H 对方开启主动H """
    TARGET_NPC_ACTIVE_H_OFF = 1404
    """ 属性_H 对方关闭主动H """
    PL_JUST_SHOOT_ON = 1405
    """ 属性_H 玩家变为前指令刚刚射精状态 """
    PL_JUST_SHOOT_OFF = 1406
    """ 属性_H 玩家清零前指令刚刚射精状态 """
    PL_CONDOM_USE_RESET = 1407
    """ 属性_H 重置玩家的避孕套使用状态 """
    SELF_CONDOM_INFO_SHOW_FLAG_ON = 1408
    """ 属性_H 自己开启避孕套信息显示 """
    TAGET_CONDOM_INFO_SHOW_FLAG_ON = 1409
    """ 属性_H 交互对象开启避孕套信息显示 """
    SCENE_ALL_CHARACTERS_CONDOM_INFO_SHOW_FLAG_ON = 1410
    """ 属性_H 场景内所有角色开启避孕套信息显示 """
    SELF_ORGASM_EDGE_ON = 1411
    """ 属性_H 自己开启绝顶寸止 """
    SELF_ORGASM_EDGE_OFF = 1412
    """ 属性_H 自己关闭绝顶寸止 """
    TARGET_ORGASM_EDGE_ON = 1413
    """ 属性_H 交互对象开启绝顶寸止 """
    TARGET_ORGASM_EDGE_OFF = 1414
    """ 属性_H 交互对象关闭绝顶寸止 """
    ALL_GROUP_SEX_TEMPLE_ON = 1415
    """ 属性_H 开启全群交模板，进行轮流群交 """
    ALL_GROUP_SEX_TEMPLE_OFF = 1416
    """ 属性_H 关闭全群交模板，进行单轮群交 """
    SELF_JOIN_GROUP_SEX_ON = 1417
    """ 属性_H 自己开始加入群交 """
    SELF_JOIN_GROUP_SEX_OFF = 1418
    """ 属性_H 自己停止加入群交 """

    # 1500+见属性_基础

    TRGET_GET_WEEKNESSS_BY_DR = 1601
    """ 属性_素质 交互对象获得[被博士持有把柄] """

    WAIT_UNITL_TRAGET_ACTION_END = 1701
    """ 行动 玩家等待至交互对象行动结束 """


class SecondEffect:
    """二段结算效果函数"""

    Nothing = 999
    """ 空白结算 """
    Must_Show = 998
    """ 必须显示的空白结算 """
    Must_Settle = 997
    """ 必须计算但不必须显示的空白结算 """

    ADD_1_NClimax_EXPERIENCE = 210
    """ 增加1N绝顶经验 """
    ADD_1_BClimax_EXPERIENCE = 211
    """ 增加1B绝顶经验 """
    ADD_1_CClimax_EXPERIENCE = 212
    """ 增加1C绝顶经验 """
    # ADD_1_PClimax_EXPERIENCE = 213
    # """ 增加1P绝顶经验 """
    ADD_1_VClimax_EXPERIENCE = 214
    """ 增加1V绝顶经验 """
    ADD_1_AClimax_EXPERIENCE = 215
    """ 增加1A绝顶经验 """
    ADD_1_UClimax_EXPERIENCE = 216
    """ 增加1U绝顶经验 """
    ADD_1_WClimax_EXPERIENCE = 217
    """ 增加1W绝顶经验 """
    # ADD_1_Climax_EXPERIENCE = 220
    # """ 增加1绝顶经验 """
    ADD_1_Cumming_EXPERIENCE = 221
    """ 增加1射精经验 """
    ADD_1_Milking_EXPERIENCE = 222
    """ 增加1喷乳经验 """
    ADD_1_Peeing_EXPERIENCE = 223
    """ 增加1放尿经验 """
    TARGET_ADD_1_Cums_EXPERIENCE = 224
    """ 交互对象增加1精液经验 """
    TARGET_ADD_SMALL_LUBRICATION = 225
    """ 交互对象增加少量润滑 """
    TARGET_ADD_MIDDLE_LUBRICATION = 226
    """ 交互对象增加中量润滑 """
    TARGET_ADD_LARGE_LUBRICATION = 227
    """ 交互对象增加大量润滑 """
    ADD_SMALL_LUBRICATION = 228
    """ 增加少量润滑 """
    ADD_MIDDLE_LUBRICATION = 229
    """ 增加中量润滑 """
    ADD_LARGE_LUBRICATION = 230
    """ 增加大量润滑 """
    DOWN_SMALL_HIT_POINT = 231
    """ 减少少量体力 """
    DOWN_SMALL_MANA_POINT = 232
    """ 减少少量气力 """
    DOWN_MIDDLE_HIT_POINT = 233
    """ 减少中量体力 """
    DOWN_MIDDLE_MANA_POINT = 234
    """ 减少中量气力 """
    DOWN_LARGE_HIT_POINT = 235
    """ 减少大量体力 """
    DOWN_LARGE_MANA_POINT = 236
    """ 减少大量气力 """
    ADD_SMALL_N_FEEL = 237
    """ 增加少量Ｎ快（N感补正） """
    ADD_SMALL_B_FEEL = 238
    """ 增加少量Ｂ快（B感补正） """
    ADD_SMALL_C_FEEL = 239
    """ 增加少量Ｃ快（C感补正） """
    ADD_SMALL_P_FEEL = 240
    """ 增加少量玩家射精值（P感补正） """
    ADD_SMALL_V_FEEL = 241
    """ 增加少量Ｖ快（V感补正） """
    ADD_SMALL_A_FEEL = 242
    """ 增加少量Ａ快（A感补正） """
    ADD_SMALL_U_FEEL = 243
    """ 增加少量Ｕ快（U感补正） """
    ADD_SMALL_W_FEEL = 244
    """ 增加少量Ｗ快（W感补正） """
    ADD_MIDDLE_N_FEEL = 245
    """ 增加中量Ｎ快（N感补正） """
    ADD_MIDDLE_B_FEEL = 246
    """ 增加中量Ｂ快（B感补正） """
    ADD_MIDDLE_C_FEEL = 247
    """ 增加中量Ｃ快（C感补正） """
    ADD_MIDDLE_P_FEEL = 248
    """ 增加中量Ｐ快（P感补正） """
    ADD_MIDDLE_V_FEEL = 249
    """ 增加中量Ｖ快（V感补正） """
    ADD_MIDDLE_A_FEEL = 250
    """ 增加中量Ａ快（A感补正） """
    ADD_MIDDLE_U_FEEL = 251
    """ 增加中量Ｕ快（U感补正） """
    ADD_MIDDLE_W_FEEL = 252
    """ 增加中量Ｗ快（W感补正） """
    ADD_LARGE_N_FEEL = 253
    """ 增加大量Ｎ快（N感补正） """
    ADD_LARGE_B_FEEL = 254
    """ 增加大量Ｂ快（B感补正） """
    ADD_LARGE_C_FEEL = 255
    """ 增加大量Ｃ快（C感补正） """
    ADD_LARGE_P_FEEL = 256
    """ 增加大量Ｐ快（P感补正） """
    ADD_LARGE_V_FEEL = 257
    """ 增加大量Ｖ快（V感补正） """
    ADD_LARGE_A_FEEL = 258
    """ 增加大量Ａ快（A感补正） """
    ADD_LARGE_U_FEEL = 259
    """ 增加大量Ｕ快（U感补正） """
    ADD_LARGE_W_FEEL = 260
    """ 增加大量Ｗ快（W感补正） """
    ADD_SMALL_LUBRICATION_PLUS = 261
    """ 增加少量润滑（欲望补正） """
    ADD_SMALL_LEARN = 262
    """ 增加少量习得（技巧补正） """
    ADD_SMALL_RESPECT = 263
    """ 增加少量恭顺（顺从补正） """
    ADD_SMALL_FRIENDLY = 264
    """ 增加少量好意（亲密补正） """
    ADD_SMALL_DESIRE = 265
    """ 增加少量欲情（欲望补正） """
    ADD_SMALL_HAPPY = 266
    """ 增加少量快乐（快乐刻印补正） """
    ADD_SMALL_LEAD = 267
    """ 增加少量先导（施虐补正） """
    ADD_SMALL_SUBMIT = 268
    """ 增加少量屈服（屈服刻印补正） """
    ADD_SMALL_SHY = 269
    """ 增加少量羞耻（露出补正） """
    ADD_SMALL_PAIN = 270
    """ 增加少量苦痛（苦痛刻印补正） """
    ADD_SMALL_TERROR = 271
    """ 增加少量恐怖（恐怖刻印补正） """
    ADD_SMALL_DEPRESSION = 272
    """ 增加少量抑郁 """
    ADD_SMALL_DISGUST = 273
    """ 增加少量反感（反发刻印补正） """
    ADD_MIDDLE_LUBRICATION_PLUS = 274
    """ 增加中量润滑（欲望补正） """
    ADD_MIDDLE_LEARN = 275
    """ 增加中量习得（技巧补正） """
    ADD_MIDDLE_RESPECT = 276
    """ 增加中量恭顺（顺从补正） """
    ADD_MIDDLE_FRIENDLY = 277
    """ 增加中量好意（亲密补正） """
    ADD_MIDDLE_DESIRE = 278
    """ 增加中量欲情（欲望补正） """
    ADD_MIDDLE_HAPPY = 279
    """ 增加中量快乐（快乐刻印补正） """
    ADD_MIDDLE_LEAD = 280
    """ 增加中量先导（施虐补正） """
    ADD_MIDDLE_SUBMIT = 281
    """ 增加中量屈服（屈服刻印补正） """
    ADD_MIDDLE_SHY = 282
    """ 增加中量羞耻（露出补正） """
    ADD_MIDDLE_PAIN = 283
    """ 增加中量苦痛（苦痛刻印补正） """
    ADD_MIDDLE_TERROR = 284
    """ 增加中量恐怖（恐怖刻印补正） """
    ADD_MIDDLE_DEPRESSION = 285
    """ 增加中量抑郁 """
    ADD_MIDDLE_DISGUST = 286
    """ 增加中量反感（反发刻印补正） """
    ADD_LARGE_LUBRICATION_PLUS = 287
    """ 增加大量润滑（欲望补正） """
    ADD_LARGE_LEARN = 288
    """ 增加大量习得（技巧补正） """
    ADD_LARGE_RESPECT = 289
    """ 增加大量恭顺（顺从补正） """
    ADD_LARGE_FRIENDLY = 290
    """ 增加大量好意（亲密补正） """
    ADD_LARGE_DESIRE = 291
    """ 增加大量欲情（欲望补正） """
    ADD_LARGE_HAPPY = 292
    """ 增加大量快乐（快乐刻印补正） """
    ADD_LARGE_LEAD = 293
    """ 增加大量先导（施虐补正） """
    ADD_LARGE_SUBMIT = 294
    """ 增加大量屈服（屈服刻印补正） """
    ADD_LARGE_SHY = 295
    """ 增加大量羞耻（露出补正） """
    ADD_LARGE_PAIN = 296
    """ 增加大量苦痛（苦痛刻印补正） """
    ADD_LARGE_TERROR = 297
    """ 增加大量恐怖（恐怖刻印补正） """
    ADD_LARGE_DEPRESSION = 298
    """ 增加大量抑郁 """
    ADD_LARGE_DISGUST = 299
    """ 增加大量反感（反发刻印补正） """
    DOWN_SMALL_PAIN = 301
    """ 减少少量苦痛（苦痛刻印补正） """
    DOWN_SMALL_DISGUST = 302
    """ 减少少量反感（反发刻印补正） """
    DOWN_MIDDLE_PAIN = 303
    """ 减少中量苦痛（苦痛刻印补正） """
    DOWN_MIDDLE_DISGUST = 304
    """ 减少中量反感（反发刻印补正） """
    DOWN_LARGE_PAIN = 305
    """ 减少大量苦痛（苦痛刻印补正） """
    DOWN_LARGE_DISGUST = 306
    """ 减少大量反感（反发刻印补正） """
    ADD_LARGE_PAIN_FIRST_SEX = 400
    """ 增加巨量苦痛（破处修正） """
    ADD_LARGE_PAIN_FIRST_A_SEX = 401
    """ 增加巨量苦痛（A破处修正） """
    ADD_URINATE = 402
    """ 增加尿意（持续性利尿剂） """
    ADD_SLEEP_POINT = 403
    """ 维持熟睡值（安眠药） """
    MILKING_MACHINE = 404
    """ 角色的奶量转化为乳汁（搾乳机） """
    URINE_COLLECTOR = 405
    """ 角色的尿液转化为圣水（采尿器） """
    B_ORGASM_TO_MILK = 406
    """ 结算因B绝顶而被迫喷乳 """
    U_ORGASM_TO_PEE = 407
    """ 结算因U绝顶而被迫漏尿 """
    EXTRA_ORGASM = 408
    """ 结算额外绝顶(痛苦+恐怖) """
    PLURAL_ORGASM = 409
    """ 结算多重绝顶(快乐+屈服) """

    PENIS_IN_T_RESET = 501
    """ 改变当前阴茎位置为交互对象_双方归零 """

    GIVE_PAN_IN_DAY_FIRST_MEET = 511
    """ 在每日招呼时上交今天的内裤 """
    GIVE_SOCKS_IN_DAY_FIRST_MEET = 512
    """ 在每日招呼时上交今天的袜子 """

    ADD_1_SEX_V_EXPERIENCE = 601
    """ 属性_经验 增加1V性交经验 """
    ADD_1_SEX_A_EXPERIENCE = 602
    """ 属性_经验 增加1A性交经验 """
    ADD_1_SEX_U_EXPERIENCE = 603
    """ 属性_经验 增加1U性交经验 """
    ADD_1_SEX_W_EXPERIENCE = 604
    """ 属性_经验 增加1W性交经验 """
    ADD_1_EXPAND_V_EXPERIENCE = 605
    """ 属性_经验 增加1V扩张经验 """
    ADD_1_EXPAND_A_EXPERIENCE = 606
    """ 属性_经验 增加1A扩张经验 """
    ADD_1_EXPAND_U_EXPERIENCE = 607
    """ 属性_经验 增加1U扩张经验 """
    ADD_1_EXPAND_W_EXPERIENCE = 608
    """ 属性_经验 增加1W扩张经验 """
    ADD_1_N_EXPERIENCE = 610
    """ 属性_经验 自己增加1N经验 """
    ADD_1_B_EXPERIENCE = 611
    """ 属性_经验 自己增加1B经验 """
    ADD_1_C_EXPERIENCE = 612
    """ 属性_经验 自己增加1C经验 """
    ADD_1_P_EXPERIENCE = 613
    """ 属性_经验 自己增加1P经验 """
    ADD_1_V_EXPERIENCE = 614
    """ 属性_经验 自己增加1V经验 """
    ADD_1_A_EXPERIENCE = 615
    """ 属性_经验 自己增加1A经验 """
    ADD_1_U_EXPERIENCE = 616
    """ 属性_经验 自己增加1U经验 """
    ADD_1_W_EXPERIENCE = 617
    """ 属性_经验 自己增加1W经验 """
