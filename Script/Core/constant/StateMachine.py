class StateMachine:
    """状态机id"""

    WAIT_5_MIN = 0
    """ 原地待机5分钟 """
    WAIT_10_MIN = 1
    """ 原地待机10分钟 """
    WAIT_30_MIN = 2
    """ 原地待机30分钟，并取消跟随状态 """
    FOLLOW = 6
    """ 跟随玩家 """

    SEE_H_AND_MOVE_TO_DORMITORY = 40
    """ 目睹玩家和其他角色H """
    REST = 43
    """ 休息一会儿 """
    SLEEP = 44
    """ 睡觉 """
    SINGING = 45
    """ 唱歌 """
    PLAY_INSTRUMENT = 46
    """ 演奏乐器 """
    PEE = 50
    """ 解手 """

    START_SHOWER = 71
    """ 进入要脱衣服（洗澡）状态 """
    WEAR_TO_LOCKER = 72
    """ 当前身上衣服转移到衣柜里 """
    TAKE_SHOWER = 73
    """ 淋浴 """
    GET_SHOWER_CLOTH_AND_CLEAN_LOCKER = 74
    """ 换上浴帽和浴巾并清空衣柜 """
    START_EAT_FOOD = 75
    """ 进入要取餐状态 """
    BUY_RAND_FOOD_AT_FOODSHOP = 76
    """ 在食物商店购买随机食物 """
    EAT_BAG_RAND_FOOD = 77
    """ 食用背包内随机食物 """
    START_SLEEP = 78
    """ 进入要睡眠状态 """
    START_REST = 79
    """ 进入要休息状态 """
    START_PEE = 80
    """ 进入要撒尿状态 """
    LOCKER_TO_WEAR = 81
    """ 衣柜里的衣服穿回身上，如果有浴场flag则置0 """
    SIWM_1 = 82
    """ 进入要换泳衣状态 """
    SIWM_2 = 83
    """ 脱掉衣服并换上泳衣并进入要游泳状态 """
    START_BATHHOUSE_ENTERTAINMENT = 85
    """ 进入要去大浴场娱乐_要更衣状态 """
    FOOT_CLOTH_TO_LOCKER = 86
    """ 袜子和鞋子转移到衣柜里 """
    WEAR_TO_LOCKER_AND_GET_SHOWER_CLOTH = 87
    """ 当前身上衣服转移到衣柜里，并换上浴帽和浴巾 """
    CLEAN_WEAR_AND_LOCKER_TO_WEAR = 88
    """ 清空身上的衣服然后穿回衣柜的衣服，如果有浴场或游泳娱乐flag则置0 """
    START_MILK = 89
    """ 进入要挤奶状态 """
    MAKE_MILK = 90
    """ 挤奶 """
    START_MASTUREBATE = 91
    """ 进入要自慰状态 """
    MASTUREBATE = 92
    """ 自慰 """
    GET_CHARA_NORMAL_CLOTH_AND_DAY_EQIP = 93
    """ 起床（换上正常服装+调整管理白天道具） """
    RESET_SHOWER_STATUS_AND_GET_NORMAL_CLOTH = 94
    """ 清零洗澡状态并换上标准衣服 """
    START_MASTUREBATE_BEFORE_SLEEP = 95
    """ 进入要睡前自慰状态 """
    JOIN_GROUP_SEX = 96
    """ 加入群交 """
    STOP_JOIN_GROUP_SEX = 97
    """ 停止加入群交 """
    WAIT_FOR_HEALTH_CHECK = 98
    """ 等待体检 """

    CHAT_TO_DR = 100
    """ 和玩家聊天 """
    STROKE_TO_DR = 101
    """ 和玩家身体接触 """
    MAKE_COFFEE_TO_DR = 102
    """ 给玩家泡咖啡 """
    MAKE_COFFEE_ADD_TO_DR = 103
    """ 给玩家泡咖啡（加料） """

    CHAT_RAND_CHARACTER = 200
    """ 和场景里随机对象聊天 """
    STROKE_RAND_CHARACTER = 201
    """ 和场景里随机对象身体接触 """
    SINGING_RAND_CHARACTER = 202
    """ 唱歌给房间里随机角色听 """
    PLAY_INSTRUMENT_RAND_CHARACTER = 203
    """ 演奏乐器给房间里随机角色听 """

    WORK_CURE_PATIENT = 301
    """ 工作：诊疗病人 """
    WORK_RECRUIT = 302
    """ 工作：招募干员 """
    WORK_TEACH = 303
    """ 工作：授课 """
    WORK_ATTENT_CLASS = 304
    """ 工作：上学 """
    WORK_LIBRARY_1 = 305
    """ 工作：三成去图书馆，七成原地等待30分钟 """
    WORK_LIBRARY_2 = 306
    """ 工作：三成去图书馆办公室，七成看书 """
    WORK_MAINTENANCE_1 = 307
    """ 工作：进入要检修状态，并随机指定一个检修地点 """
    WORK_MAINTENANCE_2 = 308
    """ 工作：维护设施，并清零检修状态 """
    WORK_REPAIR_EQUIPMENT = 309
    """ 工作：修理装备 """
    WORK_COOK = 310
    """ 工作：做饭 """
    WORK_PRODUCE = 311
    """ 工作：制造产品 """
    WORK_OFFICIAL_WORK = 312
    """ 工作：处理公务 """
    WORK_MASSAGE = 313
    """ 工作：按摩（自动寻找对象） """
    WORK_INVITE_VISITOR = 314
    """ 工作：邀请访客 """
    WORK_PLANT_MANAGE_CROP = 315
    """ 工作：种植与养护作物 """
    WORK_DEAL_WITH_DIPLOMACY = 316
    """ 工作：处理外交事宜 """
    WORK_SEX_EXERCISES = 317
    """ 工作：性爱练习 """
    WORK_COMBAT_TRAINING = 318
    """ 工作：战斗训练 """
    WORK_FITNESS_TRAINING = 319
    """ 工作：健身锻炼 """
    WORK_TRAIN_PRISONER = 320
    """ 工作：对囚犯进行日常训练 """

    ENTERTAIN_READ = 401
    """ 娱乐：读书 """
    # 402空缺占位
    ENTERTAIN_SINGING = 403
    """ 娱乐：唱歌 """
    ENTERTAIN_PLAY_CLASSIC_INSTRUMENT = 404
    """ 娱乐：演奏传统乐器 """
    ENTERTAIN_PLAY_MODEN_INSTRUMENT = 405
    """ 娱乐：演奏现代乐器 """
    ENTERTAIN_WATCH_MOVIE = 406
    """ 娱乐：看电影 """
    ENTERTAIN_PHOTOGRAPHY = 407
    """ 娱乐：摄影 """
    ENTERTAIN_PLAY_WATER = 408
    """ 娱乐：玩水 """
    ENTERTAIN_PLAY_CHESS = 409
    """ 娱乐：下棋 """
    ENTERTAIN_PLAY_MAHJONG = 410
    """ 娱乐：打麻将 """
    ENTERTAIN_PLAY_CARDS = 411
    """ 娱乐：打牌 """
    ENTERTAIN_REHEARSE_DANCE = 412
    """ 娱乐：排演舞剧 """
    ENTERTAIN_PLAY_ARCADE_GAME = 413
    """ 娱乐：玩街机游戏 """
    ENTERTAIN_SWIMMING = 414
    """ 娱乐：游泳 """
    ENTERTAIN_TASTE_WINE = 415
    """ 娱乐：品酒 """
    ENTERTAIN_TASTE_TEA = 416
    """ 娱乐：品茶 """
    ENTERTAIN_TASTE_COFFEE = 417
    """ 娱乐：品咖啡 """
    ENTERTAIN_TASTE_DESSERT = 418
    """ 娱乐：品尝点心 """
    ENTERTAIN_TASTE_FOOD = 419
    """ 娱乐：品尝美食 """
    ENTERTAIN_PLAY_HOUSE = 420
    """ 娱乐：过家家 """
    ENTERTAIN_STYLE_HAIR = 421
    """ 娱乐：修整发型 """
    ENTERTAIN_FULL_BODY_STYLING = 422
    """ 娱乐：全身造型服务 """
    ENTERTAIN_SOAK_FEET = 423
    """ 娱乐：泡脚 """
    ENTERTAIN_STEAM_SAUNA = 424
    """ 娱乐：蒸桑拿 """
    ENTERTAIN_HYDROTHERAPY_TREATMENT = 425
    """ 娱乐：水疗护理 """
    ENTERTAIN_ONSEN_BATH = 426
    """ 娱乐：泡温泉 """

    MOVE_TO_RAND_SCENE = 501
    """ 移动至随机场景 """
    MOVE_TO_DORMITORY = 502
    """ 移动至所属宿舍 """
    MOVE_TO_PLAYER = 503
    """ 移动至玩家位置 """
    CONTINUE_MOVE = 504
    """ 继续移动 """
    MOVE_TO_TOILET = 511
    """ 去洗手间 """
    MOVE_TO_REST_ROOM = 512
    """ 移动至休息室 """
    MOVE_TO_TRAINING_ROOM = 514
    """ 根据职业自动移动至对应训练室 """
    MOVE_TO_BATH_ROOM = 515
    """ 移动至淋浴室 """
    MOVE_TO_RESTAURANT = 516
    """ 移动至餐馆（随机某个正餐餐馆） """
    MOVE_TO_MAINTENANCE_PLACE = 517
    """ 移动至检修地点 """
    MOVE_TO_PRODUCTION_WORKSHOP = 518
    """ 移动至生产车间 """
    MOVE_TO_KITCHEN = 521
    """ 移动至厨房 """
    MOVE_TO_FOODSHOP = 522
    """ 移动至食物商店 """
    MOVE_TO_DINING_HALL = 523
    """ 移动至食堂 """
    MOVE_TO_CLASSIC_MUSIC_ROOM = 524
    """ 移动至夕照区音乐室 """
    MOVE_TO_MODEN_MUSIC_ROOM = 525
    """ 移动至现代音乐排练室 """
    MOVE_TO_MULTIMEDIA_ROOM = 526
    """ 移动至多媒体室 """
    MOVE_TO_PHOTOGRAPHY_STUDIO = 527
    """ 移动至摄影爱好者影棚 """
    MOVE_TO_AQUAPIT_EXPERIENTORIUM = 528
    """ 移动至大水坑快活体验屋 """
    MOVE_TO_BOARD_GAMES_ROOM = 529
    """ 移动至棋牌室 """
    MOVE_TO_FAIRY_BANQUET = 530
    """ 移动至糖果仙子宴会厅 """
    MOVE_TO_BAR = 531
    """ 移动至酒吧 """
    MOVE_TO_HR_OFFICE = 541
    """ 移动到人事部办公室 """
    MOVE_TO_LIBRARY_OFFICE = 551
    """ 移动到图书馆办公室 """
    MOVE_TO_LIBRARY = 552
    """ 移动到图书馆 """
    MOVE_TO_CLASS_ROOM = 561
    """ 移动到教室 """
    MOVE_TO_TEACHER_OFFICE = 562
    """ 移动到教师办公室 """
    MOVE_TO_GOLDEN_GAME_ROOM = 563
    """ 移动到黄澄澄游戏室 """
    MOVE_TO_DR_OFFICE = 571
    """ 移动至博士办公室 """
    MOVE_TO_AVANT_GARDE_ARCADE = 584
    """ 移动至前卫街机厅 """
    MOVE_TO_WALYRIA_CAKE_SHOP = 585
    """ 移动至瓦莱丽蛋糕店 """
    MOVE_TO_STYLING_STUDIO = 586
    """ 移动至造型工作室 """
    MOVE_TO_HAIR_SALON = 587
    """ 移动至理发店 """
    MOVE_TO_TEAHOUSE = 588
    """ 移动至山城茶馆 """
    MOVE_TO_CAFÉ = 589
    """ 移动至哥伦比亚咖啡馆 """
    MOVE_TO_LIGHT_STORE = 590
    """ 移动至花草灯艺屋 """
    MOVE_TO_PIZZERIA = 591
    """ 移动至快捷连锁披萨店 """
    MOVE_TO_SEVEN_CITIES_RESTAURANT = 592
    """ 移动至七城风情餐厅 """
    MOVE_TO_BURGER = 593
    """ 移动至约翰老妈汉堡店 """
    MOVE_TO_HEALTHY_DINER = 594
    """ 移动至健康快餐店 """
    MOVE_TO_LUNGMEN_EATERY = 595
    """ 移动至龙门食坊 """
    MOVE_TO_BATHZONE_LOCKER_ROOM = 601
    """ 移动至大浴场的更衣室 """
    MOVE_TO_FOOT_BATH = 602
    """ 移动至足浴区 """
    MOVE_TO_SAUNA = 603
    """ 移动至桑拿房 """
    MOVE_TO_SPA_ROOM = 604
    """ 移动至水疗房 """
    MOVE_TO_ONSEN = 605
    """ 移动至温泉 """
    MOVE_TO_BATHZONE_REST_ROOM = 606
    """ 移动至大浴场的休息室 """
    MOVE_TO_SWIMMING_POOL = 611
    """ 移动至游泳池 """
    MOVE_TO_TRAINING_LOCKER_ROOM = 612
    """ 移动至训练场的更衣室 """
    MOVE_TO_GYM_ROOM = 613
    """ 移动至健身区 """
    MOVE_TO_MAINTENANCE_DEPARTMENT = 621
    """ 移动至运维部 """
    MOVE_TO_BLACKSMITH_SHOP = 622
    """ 移动至铁匠铺 """
    MOVE_TO_DIPLOMATIC_OFFICE = 631
    """ 移动至外交官办公室 """
    MOVE_TO_HERB_GARDEN = 641
    """ 移动至药田 """
    MOVE_TO_GREENHOUSE = 642
    """ 移动至温室 """
    MOVE_TO_HUMILIATION_ROOM = 651
    """ 移动至调教室 """
    MOVE_TO_WARDEN_OFFICE = 652
    """ 移动至监狱长办公室 """
    MOVE_TO_CLINIC = 661
    """ 随机移动到门诊室（含急诊室）（优先去当前没有人的） """
    MOVE_TO_PHYSICAL_EXAMINATION = 662
    """ 移动至体检科 """

    HELP_BUY_FOOD_1 = 701
    """ 进入要买饭状态 """
    HELP_MAKE_FOOD_1 = 702
    """ 进入要做饭状态 """
    ASSISTANT_MAKE_FOOD = 703
    """ 助理：做饭 """
    MORNING_SALUTATION_FLAG_1 = 704
    """ 进入要早安问候状态 """
    MORNING_SALUTATION_1 = 705
    """ 早安问候：叫起床 """
    MORNING_SALUTATION_2 = 706
    """ 早安问候：早安吻 """
    MORNING_SALUTATION_3 = 707
    """ 早安问候：早安咬 """
    NIGHT_SALUTATION_FLAG_1 = 708
    """ 进入要晚安问候状态 """
    NIGHT_SALUTATION_1 = 709
    """ 晚安问候：催睡觉 """
    NIGHT_SALUTATION_2 = 710
    """ 晚安问候：晚安吻 """
    NIGHT_SALUTATION_3 = 711
    """ 晚安问候：晚安咬 """
    NIGHT_SALUTATION_FLAG_2 = 712
    """ 进入已晚安问候状态 """

    SELF_NIPPLE_CLAMP_SWITCH_CHANEG = 751
    """ 切换自己是否装备道具_乳头夹 """
    SELF_CLIT_CLAMP_SWITCH_CHANEG = 752
    """ 切换自己是否装备道具_阴蒂夹 """
    SELF_V_VIBRATOR_SWITCH_CHANEG = 753
    """ 切换自己是否装备道具_V振动棒 """
    SELF_A_VIBRATOR_SWITCH_CHANEG = 754
    """ 切换自己是否装备道具_A振动棒 """

