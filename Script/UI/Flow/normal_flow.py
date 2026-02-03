from Script.Core import constant, cache_control, game_type
from Script.Design import handle_panel
from Script.UI.Panel import (
    all_npc_position_panel,
    aromatherapy_panel,
    nation_diplomacy_panel,
    normal_panel,
    h_item_shop_panel,
    in_scene_panel,
    in_scene_panel_web,
    assistant_panel,
    building_panel,
    collection_panel,
    ejaculation_panel,
    make_food_panel,
    food_bag_panel,
    food_shop_panel,
    manage_basement_panel,
    see_item_info_panel,
    see_map_panel,
    cloth_panel,
    instruct_filter_panel,
    event_option_panel,
    check_locker_panel,
    borrow_book_panel,
    manage_library,
    debug_panel,
    originium_arts,
    prts_panel,
    recruit_panel,
    invite_visitor_panel,
    system_setting,
    chat_ai_setting,
    physical_check_and_manage,
    see_save_info_panel,
    hypnosis_panel,
    achievement_panel,
    see_character_info_panel,
    ability_up_panel,
    gift_panel,
    manage_power_system_panel,
    equipmen_panel,
    manage_assembly_line_panel,
    agriculture_production_panel,
    manage_vehicle_panel,
    confinement_and_training,
    resource_exchange_panel,
    navigation_panel,
    read_book_panel,
)
from Script.Config import normal_config

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
width = normal_config.config_normal.text_width
""" 屏幕宽度 """


@handle_panel.add_panel(constant.Panel.IN_SCENE)
def in_scene_flow():
    """场景互动面板"""
    # Web模式下使用新的Web专用面板
    if cache.web_mode:
        now_panel = in_scene_panel_web.InScenePanelWeb(width)
    else:
        now_panel = in_scene_panel.InScenePanel(width)
    now_panel.draw()


@handle_panel.add_panel(constant.Panel.ASSISTANT)
def assistant_flow():
    """助理面板"""
    now_panel = assistant_panel.Assistant_Panel(width)
    now_panel.draw()


@handle_panel.add_panel(constant.Panel.BUILDING)
def building_flow():
    """基建面板"""
    now_panel = building_panel.Building_Panel(width)
    now_panel.draw()


@handle_panel.add_panel(constant.Panel.COLLECTION)
def collection_flow():
    """收藏品面板"""
    now_panel = collection_panel.Collection_Panel(width)
    now_panel.draw()


@handle_panel.add_panel(constant.Panel.EJACULATION)
def ejaculation_flow():
    """射精面板"""
    now_panel = ejaculation_panel.Ejaculation_Panel(width)
    now_panel.draw()


@handle_panel.add_panel(constant.Panel.ALL_NPC_POSITION)
def find_call():
    """干员位置一览面板"""
    now_panel = all_npc_position_panel.All_Npc_Position_Panel(width)
    now_panel.draw()


@handle_panel.add_panel(constant.Panel.FOOD_BAG)
def food_bag_flow():
    """食物背包面板"""
    now_panel = food_bag_panel.FoodBagPanel(width)
    now_panel.draw()


@handle_panel.add_panel(constant.Panel.FOOD_SHOP)
def food_shop_flow():
    """食物商店面板"""
    now_panel = food_shop_panel.FoodShopPanel(width)
    now_panel.draw()


@handle_panel.add_panel(constant.Panel.MAKE_FOOD)
def make_food_flow():
    """制作食物面板"""
    now_panel = make_food_panel.Make_food_Panel(width)
    now_panel.draw()


@handle_panel.add_panel(constant.Panel.H_ITEM_SHOP)
def item_h_shop_flow():
    """成人用品商店面板"""
    now_panel = h_item_shop_panel.HItemShopPanel(width)
    now_panel.draw()


@handle_panel.add_panel(constant.Panel.ITEM)
def see_item_info_flow():
    """道具栏面板"""
    now_panel = see_item_info_panel.SeeCharacterItemBagPanel(0, width)
    now_panel.draw()


@handle_panel.add_panel(constant.Panel.SEE_MAP)
def see_map_flow():
    """查看地图面板"""
    now_panel = see_map_panel.SeeMapPanel(width)
    now_panel.draw()


@handle_panel.add_panel(constant.Panel.UNDRESS)
def undress_flow():
    """脱衣服面板"""
    now_panel = cloth_panel.Undress_Panel(width)
    now_panel.draw()


@handle_panel.add_panel(constant.Panel.MANAGE_BASEMENT)
def manage_basement_flow():
    """管理罗德岛面板"""
    now_panel = manage_basement_panel.Manage_Basement_Panel(width)
    now_panel.draw()


# @handle_panel.add_panel(constant.Panel.INSTRUCT_FILTER)
# def instruct_filter_flow():
#     """指令过滤面板"""
#     now_panel = instruct_filter_panel.Instruct_filter_Panel(width)
#     now_panel.draw()


@handle_panel.add_panel(constant.Panel.EVENT_OPTION)
def event_option_flow():
    """事件选项面板"""
    now_panel = event_option_panel.Event_option_Panel(0, width)
    now_panel.draw()


@handle_panel.add_panel(constant.Panel.CHECK_LOCKER)
def check_locker_flow():
    """检查衣柜面板"""
    now_panel = check_locker_panel.Check_locker_Panel(width)
    now_panel.draw()


@handle_panel.add_panel(constant.Panel.BORROW_BOOK)
def borrow_book_flow():
    """借阅书籍面板"""
    now_panel = borrow_book_panel.Borrow_Book_Panel(width)
    now_panel.draw()


@handle_panel.add_panel(constant.Panel.MANAGE_LIBRARY)
def manage_library_flow():
    """图书馆管理面板"""
    now_panel = manage_library.Manage_Library_Panel(width)
    now_panel.draw()

@handle_panel.add_panel(constant.Panel.DEBUG_ADJUST)
def debug_flow():
    """debug数值调整面板"""
    now_panel = debug_panel.Debug_Panel(width)
    now_panel.draw()

@handle_panel.add_panel(constant.Panel.ORIGINIUM_ARTS)
def originium_arts_flow():
    """源石技艺面板"""
    now_panel = originium_arts.Originium_Arts_Panel(width)
    now_panel.draw()

@handle_panel.add_panel(constant.Panel.PRTS)
def prts_flow():
    """普瑞赛斯面板"""
    now_panel = prts_panel.Prts_Panel(width)
    now_panel.draw()

@handle_panel.add_panel(constant.Panel.RECRUITMENT)
def recruit_flow():
    """公开招募面板"""
    now_panel = recruit_panel.Recruit_Panel(width)
    now_panel.draw()

@handle_panel.add_panel(constant.Panel.VISITOR)
def visitor_flow():
    """访客面板"""
    now_panel = invite_visitor_panel.Invite_Visitor_Panel(width)
    now_panel.draw()

@handle_panel.add_panel(constant.Panel.FRIDGE)
def fridge_flow():
    """冰箱面板"""
    now_panel = normal_panel.Fridge_Panel(width)
    now_panel.draw()

@handle_panel.add_panel(constant.Panel.SYSTEM_SETTING)
def system_setting_flow():
    """系统设置面板"""
    now_panel = system_setting.System_Setting_Panel(width)
    now_panel.draw()

@handle_panel.add_panel(constant.Panel.AROMATHERAPY)
def aromatherapy_flow():
    """芳香疗法面板"""
    now_panel = aromatherapy_panel.Aromatherapy_Panel(width)
    now_panel.draw()

@handle_panel.add_panel(constant.Panel.NATION_DIPLOMACY)
def nation_diplomacy_flow():
    """势力外交面板"""
    now_panel = nation_diplomacy_panel.Nation_Diplomacy_Panel(width)
    now_panel.draw()

# @handle_panel.add_panel(constant.Panel.CHAT_AI_SETTING)
# def chat_ai_setting_flow():
#     """文本生成AI设置面板"""
#     now_panel = chat_ai_setting.Chat_Ai_Setting_Panel(width)
#     now_panel.draw()

@handle_panel.add_panel(constant.Panel.PHYSICAL_CHECK_AND_MANAGE)
def physical_check_and_manage_flow():
    """身体检查与管理面板"""
    now_panel = physical_check_and_manage.Physical_Check_And_Manage_Panel(width)
    now_panel.draw()

@handle_panel.add_panel(constant.Panel.SAVE)
def save_flow():
    """读写存档面板"""
    now_panel = see_save_info_panel.SeeSaveListPanel(width, True)
    now_panel.draw()

@handle_panel.add_panel(constant.Panel.CHANGE_HYPNOSIS_MODE)
def change_hypnosis_mode_flow():
    """切换催眠模式面板"""
    now_panel = hypnosis_panel.Chose_Hypnosis_Type_Panel(width, instruct_flag=True)
    now_panel.draw()

@handle_panel.add_panel(constant.Panel.SEE_ACHIEVEMENT)
def see_achievement_flow():
    """查看蚀刻章面板"""
    now_panel = achievement_panel.Achievement_Panel(width)
    now_panel.draw()

@handle_panel.add_panel(constant.Panel.SEE_ATTR)
def see_attr_flow():
    """查看属性面板"""
    now_panel = see_character_info_panel.SeeCharacterInfoInScenePanel(
        cache.character_data[0].target_character_id, width
    )
    now_panel.draw()

@handle_panel.add_panel(constant.Panel.ABL_UP)
def ability_up_flow():
    """能力提升面板"""
    now_panel = ability_up_panel.Character_abi_up_main_Handle(
        cache.character_data[0].target_character_id, width
    )
    now_panel.draw()

@handle_panel.add_panel(constant.Panel.OWNER_ABL_UP)
def owner_ability_up_flow():
    """干员能力提升面板"""
    now_panel = ability_up_panel.Character_abi_up_main_Handle(
        0, width
    )
    now_panel.draw()

@handle_panel.add_panel(constant.Panel.TAKE_CARE_BABY)
def take_care_baby_flow():
    """照顾婴儿面板"""
    now_panel = normal_panel.Take_Care_Baby_Panel(width)
    now_panel.draw()

@handle_panel.add_panel(constant.Panel.ORDER_HOTEL_ROOM)
def order_hotel_room_flow():
    """预订酒店房间面板"""
    now_panel = normal_panel.Order_Hotel_Room_Panel(width)
    now_panel.draw()

@handle_panel.add_panel(constant.Panel.GIVE_GIFT)
def give_gift_flow():
    """赠送礼物面板"""
    now_panel = gift_panel.Gift_Panel(width)
    now_panel.draw()

@handle_panel.add_panel(constant.Panel.FIELD_COMMISSION)
def field_commission_flow():
    """外勤委托面板"""
    from Script.System.Field_Commission_System import field_commission_panel
    now_panel = field_commission_panel.Field_Commission_Panel(width)
    now_panel.draw()

@handle_panel.add_panel(constant.Panel.CURE_PATIENT)
def cure_patient_flow():
    """治疗病人面板"""
    from Script.System.Medical_System import medical_player_diagnose_panel
    medical_player_diagnose_panel.start_player_diagnose_flow()

@handle_panel.add_panel(constant.Panel.MANAGE_DEDICAL_DEPARTMENT)
def manage_medical_department_flow():
    """管理医疗系统面板面板"""
    from Script.System.Medical_System import medical_department_panel
    now_panel = medical_department_panel.Medical_Department_Panel(width)
    now_panel.draw()

@handle_panel.add_panel(constant.Panel.MANAGE_POWER_SYSTEM)
def manage_power_system_flow():
    """管理动力系统面板"""
    now_panel = manage_power_system_panel.Manage_Power_System_Panel(width)
    now_panel.draw()

@handle_panel.add_panel(constant.Panel.EQUIPMENT_MAINTAIN)
def equipment_maintain_flow():
    """设备维护面板"""
    now_panel = equipmen_panel.Equipment_Maintain_Panel(width)
    now_panel.draw()

@handle_panel.add_panel(constant.Panel.TALK_QUICK_TEST)
def talk_quick_test_flow():
    """快速测试口上面板"""
    now_panel = debug_panel.TALK_QUICK_TEST(width)
    now_panel.draw()

@handle_panel.add_panel(constant.Panel.MANAGE_ASSEMBLY_LINE)
def manage_assembly_line_flow():
    """管理流水线面板"""
    now_panel = manage_assembly_line_panel.Manage_Assembly_Line_Panel(width)
    now_panel.draw()

@handle_panel.add_panel(constant.Panel.MANAGE_AGRICULTURE)
def manage_agriculture_flow():
    """管理农业生产面板"""
    now_panel = agriculture_production_panel.Agriculture_Production_Panel(width)
    now_panel.draw()

@handle_panel.add_panel(constant.Panel.MANAGE_VEHICLE)
def manage_vehicle_flow():
    """管理载具面板"""
    now_panel = manage_vehicle_panel.Manage_Vehicle_Panel(width)
    now_panel.draw()

@handle_panel.add_panel(constant.Panel.MANAGE_CONFINEMENT_AND_TRAINING)
def manage_confinement_and_training_flow():
    """管理监禁调教面板"""
    now_panel = confinement_and_training.Confinement_And_Training_Manage_Panel(width)
    now_panel.draw()

@handle_panel.add_panel(constant.Panel.MANAGE_RESOURCE_EXCHANGE)
def manage_resource_exchange_flow():
    """管理资源交易面板"""
    now_panel = resource_exchange_panel.Resource_Exchange_Line_Panel(width)
    now_panel.draw()

@handle_panel.add_panel(constant.Panel.NAVIGATION)
def navigation_flow():
    """导航面板"""
    now_panel = navigation_panel.Navigation_Panel(width)
    now_panel.draw()

@handle_panel.add_panel(constant.Panel.READ_BOOK)
def read_book_flow():
    """阅读书籍面板"""
    now_panel = read_book_panel.Read_Book_Panel(width)
    now_panel.draw()