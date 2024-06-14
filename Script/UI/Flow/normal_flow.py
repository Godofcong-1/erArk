from Script.Core import constant
from Script.Design import handle_panel
from Script.UI.Panel import (
    all_npc_position_panel,
    normal_panel,
    h_item_shop_panel,
    in_scene_panel,
    assistant_panel,
    building_panel,
    collection_panel,
    dirty_panel,
    ejaculation_panel,
    make_food_panel,
    food_bag_panel,
    food_shop_panel,
    manage_basement_panel,
    see_item_info_panel,
    see_map_panel,
    undress_panel,
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
    aromatherapy,
)
from Script.Config import normal_config

width = normal_config.config_normal.text_width
""" 屏幕宽度 """


@handle_panel.add_panel(constant.Panel.IN_SCENE)
def in_scene_flow():
    """场景互动面板"""
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


@handle_panel.add_panel(constant.Panel.DIRTY)
def dirty_flow():
    """污浊面板"""
    now_panel = dirty_panel.Dirty_Panel(width)
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
    now_panel = undress_panel.Undress_Panel(width)
    now_panel.draw()


@handle_panel.add_panel(constant.Panel.MANAGE_BASEMENT)
def manage_basement_flow():
    """管理罗德岛面板"""
    now_panel = manage_basement_panel.Manage_Basement_Panel(width)
    now_panel.draw()


@handle_panel.add_panel(constant.Panel.INSTRUCT_FILTER)
def instruct_filter_flow():
    """指令过滤面板"""
    now_panel = instruct_filter_panel.Instruct_filter_Panel(width)
    now_panel.draw()


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
    now_panel = aromatherapy.Aromatherapy_Panel(width)
    now_panel.draw()
