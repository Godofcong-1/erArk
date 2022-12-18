from Script.Core import constant
from Script.Design import handle_panel
from Script.UI.Panel import (
    in_scene_panel,
    assistant_panel,
    building_panel,
    collection_panel,
    dirty_panel,
    ejaculation_panel,
    find_call_panel,
    make_food_panel,
    food_bag_panel,
    food_shop_panel,
    item_shop_panel,
    see_item_info_panel,
    see_map_panel,
    undress_panel,
    department_panel,
    instruct_filter_panel,
    event_option_panel,
    check_locker_panel,
    borrow_book_panel,
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

@handle_panel.add_panel(constant.Panel.FIND_CALL)
def find_call():
    """查找与召集面板"""
    now_panel = find_call_panel.Find_call_Panel(width)
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
    """食物商店面板"""
    now_panel = make_food_panel.Make_food_Panel(width)
    now_panel.draw()

@handle_panel.add_panel(constant.Panel.ITEM_SHOP)
def item_shop_flow():
    """道具商店面板"""
    now_panel = item_shop_panel.ItemShopPanel(width)
    now_panel.draw()

@handle_panel.add_panel(constant.Panel.ITEM)
def see_item_info_flow():
    """道具栏面板"""
    now_panel = see_item_info_panel.SeeCharacterItemBagPanel(0,width)
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

@handle_panel.add_panel(constant.Panel.DEPARTMENT)
def department_flow():
    """部门运作情况面板"""
    now_panel = department_panel.Department_Panel(width)
    now_panel.draw()

@handle_panel.add_panel(constant.Panel.INSTRUCT_FILTER)
def instruct_filter_flow():
    """指令过滤面板"""
    now_panel = instruct_filter_panel.Instruct_filter_Panel(width)
    now_panel.draw()

@handle_panel.add_panel(constant.Panel.EVENT_OPTION)
def event_option_flow():
    """事件选项面板"""
    now_panel = event_option_panel.Event_option_Panel(width)
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
