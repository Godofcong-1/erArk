import datetime
import random
from typing import List
from Script.Settle import default
from Script.Config import game_config
from Script.Design import handle_state_machine, character_move, map_handle, clothing, handle_instruct, basement, handle_premise
from Script.Core import cache_control, game_type, constant
from Script.UI.Moudle import draw

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
line_feed = draw.NormalDraw()
""" 换行绘制对象 """
line_feed.text = "\n"
line_feed.width = 1


def general_movement_module(character_id: int, target_scene: list):
    """
    通用移动模块\n
    Keyword arguments:\n
    character_id -- 角色id\n
    target_scene -- 寻路目标场景(在地图系统下的绝对坐标)
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    tem_1, tem_2, move_path, move_time = character_move.character_move(character_id, target_scene)
    character_data.behavior.move_final_target = target_scene
    character_data.behavior.behavior_id = constant.Behavior.MOVE
    character_data.behavior.move_target = move_path
    character_data.behavior.duration = move_time
    character_data.state = constant.CharacterStatus.STATUS_MOVE


@handle_state_machine.add_state_machine(constant.StateMachine.WAIT_5_MIN)
def character_wait_5_min(character_id: int):
    """
    等待5分钟
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    character_data.behavior.behavior_id = constant.Behavior.WAIT
    character_data.behavior.duration = 5
    character_data.state = constant.CharacterStatus.STATUS_WAIT
    character_data.sp_flag.wait_flag = 0


@handle_state_machine.add_state_machine(constant.StateMachine.WAIT_10_MIN)
def character_wait_10_min(character_id: int):
    """
    等待10分钟
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    character_data.behavior.behavior_id = constant.Behavior.WAIT
    character_data.behavior.duration = 10
    character_data.state = constant.CharacterStatus.STATUS_WAIT


@handle_state_machine.add_state_machine(constant.StateMachine.WAIT_30_MIN)
def character_wait_30_min(character_id: int):
    """
    等待30分钟，并取消跟随状态
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    character_data.behavior.behavior_id = constant.Behavior.WAIT
    character_data.behavior.duration = 30
    character_data.state = constant.CharacterStatus.STATUS_WAIT
    character_data.sp_flag.is_follow = 0


@handle_state_machine.add_state_machine(constant.StateMachine.MOVE_TO_DORMITORY)
def character_move_to_dormitory(character_id: int):
    """
    移动至所在宿舍
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_scene = map_handle.get_map_system_path_for_str(character_data.dormitory)
    general_movement_module(character_id, target_scene)


@handle_state_machine.add_state_machine(constant.StateMachine.SLEEP)
def character_sleep(character_id: int):
    """
    睡觉
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    if handle_premise.handle_in_dormitory(character_id):
        clothing.get_sleep_cloth(character_id)
        default.handle_door_close(character_id,add_time=1,change_data=game_type.CharacterStatusChange(),now_time=cache.game_time)
    character_data.behavior.behavior_id = constant.Behavior.SLEEP
    character_data.behavior.duration = 480
    character_data.state = constant.CharacterStatus.STATUS_SLEEP
    character_data.sp_flag.tired = 0

# @handle_state_machine.add_state_machine(constant.StateMachine.FOLLOW)
# def character_follow(character_id: int):
#     """
#     跟随玩家
#     Keyword arguments:
#     character_id -- 角色id
#     """
#     character_data: game_type.Character = cache.character_data[character_id]
#     character_data.talent[400] = 1

@handle_state_machine.add_state_machine(constant.StateMachine.REST)
def character_rest(character_id: int):
    """
    休息
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    character_data.behavior.behavior_id = constant.Behavior.REST
    character_data.behavior.duration = 30
    character_data.state = constant.CharacterStatus.STATUS_REST


@handle_state_machine.add_state_machine(constant.StateMachine.MOVE_TO_RAND_SCENE)
def character_move_to_rand_scene(character_id: int):
    """
    移动至随机场景
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    scene_list = list(cache.scene_data.keys())
    now_scene_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    scene_list.remove(now_scene_str)
    target_scene = map_handle.get_map_system_path_for_str(random.choice(scene_list))
    general_movement_module(character_id, target_scene)


@handle_state_machine.add_state_machine(constant.StateMachine.MOVE_TO_DR_OFFICE)
def character_move_to_dr_office(character_id: int):
    """
    移动至博士办公室
    Keyword arguments:
    character_id -- 角色id
    """
    to_dr_office = map_handle.get_map_system_path_for_str(
        random.choice(constant.place_data["Dr_Office"])
    )
    general_movement_module(character_id, to_dr_office)


@handle_state_machine.add_state_machine(constant.StateMachine.MOVE_TO_TOILET)
def character_move_to_toilet(character_id: int):
    """
    移动至洗手间
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id

    # 检索当前角色所在的大场景里有没有厕所，没有的话再随机选择其他厕所
    now_position = character_data.position[0]
    find_flag = False
    if character_data.sex == 0:
        to_toilet = map_handle.get_map_system_path_for_str(
        random.choice(constant.place_data["Toilet_Male"])
    )
    elif character_data.sex == 1:
        for place in constant.place_data["Toilet_Female"]:
            if place.split("\\")[0] == now_position:
                to_toilet = map_handle.get_map_system_path_for_str(place)
                find_flag = True
                break
        if not find_flag:
            to_toilet = map_handle.get_map_system_path_for_str(
        random.choice(constant.place_data["Toilet_Female"])
    )
    # print(f"debug constant.place_data[\"Toilet_Female\"] = ",constant.place_data["Toilet_Female"])
    general_movement_module(character_id, to_toilet)

    # 如果和玩家位于同一地点，则输出提示信息
    if character_data.position == cache.character_data[0].position:
        now_draw = draw.NormalDraw()
        now_draw.text = f"{character_data.name}打算去洗手间\n"
        now_draw.draw()


@handle_state_machine.add_state_machine(constant.StateMachine.MOVE_TO_KITCHEN)
def character_move_to_kitchen(character_id: int):
    """
    移动至厨房
    Keyword arguments:
    character_id -- 角色id
    """
    to_kitchen = map_handle.get_map_system_path_for_str(
        random.choice(constant.place_data["Kitchen"])
    )
    general_movement_module(character_id, to_kitchen)


@handle_state_machine.add_state_machine(constant.StateMachine.MOVE_TO_FOODSHOP)
def character_move_to_foodshop(character_id: int):
    """
    移动至食物商店（取餐区）
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    to_foodshop = map_handle.get_map_system_path_for_str(
        random.choice(constant.place_data["Food_Shop"])
    )
    general_movement_module(character_id, to_foodshop)

    # 如果和玩家位于同一地点，则输出提示信息
    if character_data.position == cache.character_data[0].position:
        now_draw = draw.NormalDraw()
        now_draw.text = f"{character_data.name}打算去吃饭\n"
        now_draw.draw()


@handle_state_machine.add_state_machine(constant.StateMachine.MOVE_TO_DINING_HALL)
def character_move_to_dining_hall(character_id: int):
    """
    移动至食堂
    Keyword arguments:
    character_id -- 角色id
    """
    to_dining_hall = map_handle.get_map_system_path_for_str(
        random.choice(constant.place_data["Dining_hall"])
    )
    general_movement_module(character_id, to_dining_hall)


@handle_state_machine.add_state_machine(constant.StateMachine.MOVE_TO_CLINIC)
def character_move_to_clinic(character_id: int):
    """
    随机移动到门诊室（含急诊室）
    Keyword arguments:
    character_id -- 角色id
    """
    # 判断是否存在没有人的门诊室，存在的话优先去没有人的
    empty_flag = False
    for Clinic_place in constant.place_data["Clinic"]:
        if list(cache.scene_data[Clinic_place].character_list) == []:
            empty_flag = True
            to_clinic = map_handle.get_map_system_path_for_str(Clinic_place)
            break
    if not empty_flag:
        to_clinic = map_handle.get_map_system_path_for_str(
        random.choice(constant.place_data["Clinic"])
    )
    general_movement_module(character_id, to_clinic)


@handle_state_machine.add_state_machine(constant.StateMachine.MOVE_TO_HR_OFFICE)
def character_move_to_hr_office(character_id: int):
    """
    移动到人事部办公室
    Keyword arguments:
    character_id -- 角色id
    """
    to_hr_office = map_handle.get_map_system_path_for_str(
        random.choice(constant.place_data["HR_Office"])
    )
    general_movement_module(character_id, to_hr_office)


@handle_state_machine.add_state_machine(constant.StateMachine.MOVE_TO_LIBRARY_OFFICE)
def character_move_to_library_office(character_id: int):
    """
    移动到图书馆办公室
    Keyword arguments:
    character_id -- 角色id
    """
    to_library_office = map_handle.get_map_system_path_for_str(
        random.choice(constant.place_data["Library_Office"])
    )
    general_movement_module(character_id, to_library_office)


@handle_state_machine.add_state_machine(constant.StateMachine.MOVE_TO_LIBRARY)
def character_move_to_library(character_id: int):
    """
    移动到图书馆
    Keyword arguments:
    character_id -- 角色id
    """
    to_library = map_handle.get_map_system_path_for_str(
        random.choice(constant.place_data["Library"])
    )
    general_movement_module(character_id, to_library)


@handle_state_machine.add_state_machine(constant.StateMachine.MOVE_TO_CLASS_ROOM)
def character_move_to_class_room(character_id: int):
    """
    移动到教室
    Keyword arguments:
    character_id -- 角色id
    """
    to_class_room = map_handle.get_map_system_path_for_str(
        random.choice(constant.place_data["Class_Room"])
    )

    general_movement_module(character_id, to_class_room)


@handle_state_machine.add_state_machine(constant.StateMachine.MOVE_TO_TEACHER_OFFICE)
def character_move_to_teacher_office(character_id: int):
    """
    移动到教师办公室
    Keyword arguments:
    character_id -- 角色id
    """
    to_target = map_handle.get_map_system_path_for_str(
        random.choice(constant.place_data["Teacher_Office"])
    )
    general_movement_module(character_id, to_target)


@handle_state_machine.add_state_machine(constant.StateMachine.MOVE_TO_GOLDEN_GAME_ROOM)
def character_move_to_golden_game_room(character_id: int):
    """
    移动至黄澄澄游戏室
    Keyword arguments:
    character_id -- 角色id
    """
    to_target = map_handle.get_map_system_path_for_str(
        random.choice(constant.place_data["Golden_Game_Room"])
    )
    general_movement_module(character_id, to_target)


@handle_state_machine.add_state_machine(constant.StateMachine.MOVE_TO_CLASSIC_MUSIC_ROOM)
def character_move_to_classic_music_room(character_id: int):
    """
    移动至夕照区音乐室
    Keyword arguments:
    character_id -- 角色id
    """
    to_target = map_handle.get_map_system_path_for_str(
        random.choice(constant.place_data["Classic_Musicroom"])
    )
    general_movement_module(character_id, to_target)


@handle_state_machine.add_state_machine(constant.StateMachine.MOVE_TO_MODEN_MUSIC_ROOM)
def character_move_to_moden_music_room(character_id: int):
    """
    移动至现代音乐排练室
    Keyword arguments:
    character_id -- 角色id
    """
    to_target = map_handle.get_map_system_path_for_str(
        random.choice(constant.place_data["Modern_Musicroom"])
    )
    general_movement_module(character_id, to_target)


@handle_state_machine.add_state_machine(constant.StateMachine.MOVE_TO_MULTIMEDIA_ROOM)
def character_move_to_multimedia_room(character_id: int):
    """
    移动至多媒体室
    Keyword arguments:
    character_id -- 角色id
    """
    to_target = map_handle.get_map_system_path_for_str(
        random.choice(constant.place_data["Multimedia_Room"])
    )
    general_movement_module(character_id, to_target)


@handle_state_machine.add_state_machine(constant.StateMachine.MOVE_TO_PHOTOGRAPHY_STUDIO)
def character_move_to_photography_studio(character_id: int):
    """
    移动至摄影爱好者影棚
    Keyword arguments:
    character_id -- 角色id
    """
    to_target = map_handle.get_map_system_path_for_str(
        random.choice(constant.place_data["Photography_Studio"])
    )
    general_movement_module(character_id, to_target)


@handle_state_machine.add_state_machine(constant.StateMachine.MOVE_TO_AQUAPIT_EXPERIENTORIUM)
def character_move_to_aquapit_experientorium(character_id: int):
    """
    移动至大水坑快活体验屋
    Keyword arguments:
    character_id -- 角色id
    """
    to_target = map_handle.get_map_system_path_for_str(
        random.choice(constant.place_data["Aquapit_Experientorium"])
    )
    general_movement_module(character_id, to_target)


@handle_state_machine.add_state_machine(constant.StateMachine.MOVE_TO_BOARD_GAMES_ROOM)
def character_move_to_board_games_room(character_id: int):
    """
    移动至棋牌室
    Keyword arguments:
    character_id -- 角色id
    """
    to_target = map_handle.get_map_system_path_for_str(
        random.choice(constant.place_data["Board_Games_Room"])
    )
    general_movement_module(character_id, to_target)


@handle_state_machine.add_state_machine(constant.StateMachine.MOVE_TO_FAIRY_BANQUET)
def character_move_to_fairy_banquet(character_id: int):
    """
    移动至糖果仙子宴会厅
    Keyword arguments:
    character_id -- 角色id
    """
    to_target = map_handle.get_map_system_path_for_str(
        random.choice(constant.place_data["Fairy_Banquet"])
    )
    general_movement_module(character_id, to_target)


@handle_state_machine.add_state_machine(constant.StateMachine.MOVE_TO_BAR)
def character_move_to_bar(character_id: int):
    """
    移动至酒吧
    Keyword arguments:
    character_id -- 角色id
    """
    to_target = map_handle.get_map_system_path_for_str(
        random.choice(constant.place_data["Bar"])
    )
    general_movement_module(character_id, to_target)


@handle_state_machine.add_state_machine(constant.StateMachine.MOVE_TO_AVANT_GARDE_ARCADE)
def character_move_to_avant_garde_arcade(character_id: int):
    """
    移动至前卫街机厅
    Keyword arguments:
    character_id -- 角色id
    """
    to_target = map_handle.get_map_system_path_for_str(
        random.choice(constant.place_data["Avant_Garde_Arcade"])
    )
    general_movement_module(character_id, to_target)


@handle_state_machine.add_state_machine(constant.StateMachine.MOVE_TO_WALYRIA_CAKE_SHOP)
def character_move_to_walyria_cake_shop(character_id: int):
    """
    移动至瓦莱丽蛋糕店
    Keyword arguments:
    character_id -- 角色id
    """
    to_target = map_handle.get_map_system_path_for_str(
        random.choice(constant.place_data["Walyria_Cake_Shop"])
    )
    general_movement_module(character_id, to_target)


@handle_state_machine.add_state_machine(constant.StateMachine.MOVE_TO_STYLING_STUDIO)
def character_move_to_styling_studio(character_id: int):
    """
    移动至造型工作室
    Keyword arguments:
    character_id -- 角色id
    """
    to_target = map_handle.get_map_system_path_for_str(
        random.choice(constant.place_data["Styling_Studio"])
    )
    general_movement_module(character_id, to_target)


@handle_state_machine.add_state_machine(constant.StateMachine.MOVE_TO_HAIR_SALON)
def character_move_to_hair_salon(character_id: int):
    """
    移动至理发店
    Keyword arguments:
    character_id -- 角色id
    """
    to_target = map_handle.get_map_system_path_for_str(
        random.choice(constant.place_data["Hair_Salon"])
    )
    general_movement_module(character_id, to_target)


@handle_state_machine.add_state_machine(constant.StateMachine.MOVE_TO_TEAHOUSE)
def character_move_to_teahouse(character_id: int):
    """
    移动至山城茶馆
    Keyword arguments:
    character_id -- 角色id
    """
    to_target = map_handle.get_map_system_path_for_str(
        random.choice(constant.place_data["Teahouse"])
    )
    general_movement_module(character_id, to_target)


@handle_state_machine.add_state_machine(constant.StateMachine.MOVE_TO_CAFÉ)
def character_move_to_café(character_id: int):
    """
    移动至哥伦比亚咖啡馆
    Keyword arguments:
    character_id -- 角色id
    """
    to_target = map_handle.get_map_system_path_for_str(
        random.choice(constant.place_data["Café"])
    )
    general_movement_module(character_id, to_target)


@handle_state_machine.add_state_machine(constant.StateMachine.MOVE_TO_LIGHT_STORE)
def character_move_to_light_store(character_id: int):
    """
    移动至花草灯艺屋
    Keyword arguments:
    character_id -- 角色id
    """
    to_target = map_handle.get_map_system_path_for_str(
        random.choice(constant.place_data["Light_Store"])
    )
    general_movement_module(character_id, to_target)


@handle_state_machine.add_state_machine(constant.StateMachine.MOVE_TO_PIZZERIA)
def character_move_to_pizzeria(character_id: int):
    """
    移动至快捷连锁披萨店
    Keyword arguments:
    character_id -- 角色id
    """
    to_target = map_handle.get_map_system_path_for_str(
        random.choice(constant.place_data["Pizzeria"])
    )
    general_movement_module(character_id, to_target)

@handle_state_machine.add_state_machine(constant.StateMachine.MOVE_TO_SEVEN_CITIES_RESTAURANT)
def character_move_to_seven_cities_restaurant(character_id: int):
    """
    移动至七城风情餐厅
    Keyword arguments:
    character_id -- 角色id
    """
    to_target = map_handle.get_map_system_path_for_str(
        random.choice(constant.place_data["Seven_Cities_Restaurant"])
    )
    general_movement_module(character_id, to_target)


@handle_state_machine.add_state_machine(constant.StateMachine.MOVE_TO_KFC)
def character_move_to_kfc(character_id: int):
    """
    移动至人气快餐开封菜
    Keyword arguments:
    character_id -- 角色id
    """
    to_target = map_handle.get_map_system_path_for_str(
        random.choice(constant.place_data["KFC"])
    )
    general_movement_module(character_id, to_target)


@handle_state_machine.add_state_machine(constant.StateMachine.MOVE_TO_HEALTHY_DINER)
def character_move_to_healthy_diner(character_id: int):
    """
    移动至健康快餐店
    Keyword arguments:
    character_id -- 角色id
    """
    to_target = map_handle.get_map_system_path_for_str(
        random.choice(constant.place_data["Healthy_Diner"])
    )
    general_movement_module(character_id, to_target)


@handle_state_machine.add_state_machine(constant.StateMachine.MOVE_TO_LUNGMEN_EATERY)
def character_move_to_lungmen_eatery(character_id: int):
    """
    移动至龙门食坊
    Keyword arguments:
    character_id -- 角色id
    """
    to_target = map_handle.get_map_system_path_for_str(
        random.choice(constant.place_data["Lungmen_Eatery"])
    )
    general_movement_module(character_id, to_target)


@handle_state_machine.add_state_machine(constant.StateMachine.MOVE_TO_SWIMMING_POOL)
def character_move_to_swimming_pool(character_id: int):
    """
    移动至游泳池
    Keyword arguments:
    character_id -- 角色id
    """
    to_swimming_pool = map_handle.get_map_system_path_for_str(
        random.choice(constant.place_data["Swimming_Pool"])
    )
    general_movement_module(character_id, to_swimming_pool)


@handle_state_machine.add_state_machine(constant.StateMachine.MOVE_TO_FOOT_BATH)
def character_move_to_foot_bath(character_id: int):
    """
    移动至足浴区
    Keyword arguments:
    character_id -- 角色id
    """
    to_foot_bath = map_handle.get_map_system_path_for_str(
        random.choice(constant.place_data["Foot_Bath"])
    )
    general_movement_module(character_id, to_foot_bath)


@handle_state_machine.add_state_machine(constant.StateMachine.MOVE_TO_SAUNA)
def character_move_to_sauna(character_id: int):
    """
    移动至桑拿房
    Keyword arguments:
    character_id -- 角色id
    """
    to_sauna = map_handle.get_map_system_path_for_str(
        random.choice(constant.place_data["Sauna"])
    )
    general_movement_module(character_id, to_sauna)


@handle_state_machine.add_state_machine(constant.StateMachine.MOVE_TO_SPA_ROOM)
def character_move_to_spa_room(character_id: int):
    """
    移动至水疗房
    Keyword arguments:
    character_id -- 角色id
    """
    to_spa_room = map_handle.get_map_system_path_for_str(
        random.choice(constant.place_data["Spa_Room"])
    )
    general_movement_module(character_id, to_spa_room)


@handle_state_machine.add_state_machine(constant.StateMachine.MOVE_TO_ONSEN)
def character_move_to_onsen(character_id: int):
    """
    移动至温泉
    Keyword arguments:
    character_id -- 角色id
    """
    to_onsen = map_handle.get_map_system_path_for_str(
        random.choice(constant.place_data["Onsen"])
    )
    general_movement_module(character_id, to_onsen)


@handle_state_machine.add_state_machine(constant.StateMachine.MOVE_TO_MAINTENANCE_DEPARTMENT)
def character_move_to_maintenance_department(character_id: int):
    """
    移动至运维部
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    to_maintenance_department = map_handle.get_map_system_path_for_str(
        random.choice(constant.place_data["Maintenance_Department"])
    )
    general_movement_module(character_id, to_maintenance_department)

    # 如果和玩家位于同一地点，则输出提示信息
    if character_data.position == cache.character_data[0].position:
        now_draw = draw.NormalDraw()
        now_draw.text = f"{character_data.name}打算去运维部\n"
        now_draw.draw()


@handle_state_machine.add_state_machine(constant.StateMachine.MOVE_TO_BLACKSMITH_SHOP)
def character_move_to_blacksmith_shop(character_id: int):
    """
    移动至铁匠铺
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    to_blacksmith_shop = map_handle.get_map_system_path_for_str(
        random.choice(constant.place_data["Blacksmith_Shop"])
    )
    general_movement_module(character_id, to_blacksmith_shop)

    # 如果和玩家位于同一地点，则输出提示信息
    if character_data.position == cache.character_data[0].position:
        now_draw = draw.NormalDraw()
        now_draw.text = f"{character_data.name}打算去铁匠铺\n"
        now_draw.draw()


@handle_state_machine.add_state_machine(constant.StateMachine.MOVE_TO_DIPLOMATIC_OFFICE)
def character_move_to_diplomatic_office(character_id: int):
    """
    移动至外交官办公室
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    to_diplomatic_office = map_handle.get_map_system_path_for_str(
        random.choice(constant.place_data["Diplomatic_Office"])
    )
    general_movement_module(character_id, to_diplomatic_office)

    # 如果和玩家位于同一地点，则输出提示信息
    if character_data.position == cache.character_data[0].position:
        now_draw = draw.NormalDraw()
        now_draw.text = f"{character_data.name}打算去外交官办公室\n"
        now_draw.draw()


@handle_state_machine.add_state_machine(constant.StateMachine.MOVE_TO_HERB_GARDEN)
def character_move_to_herb_garden(character_id: int):
    """
    移动至药田
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    to_herb_garden = map_handle.get_map_system_path_for_str(
        random.choice(constant.place_data["Herb_Garden"])
    )
    general_movement_module(character_id, to_herb_garden)

    # 如果和玩家位于同一地点，则输出提示信息
    if character_data.position == cache.character_data[0].position:
        now_draw = draw.NormalDraw()
        now_draw.text = f"{character_data.name}打算去药田\n"
        now_draw.draw()


@handle_state_machine.add_state_machine(constant.StateMachine.MOVE_TO_GREENHOUSE)
def character_move_to_greenhouse(character_id: int):
    """
    移动至温室
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    to_greenhouse = map_handle.get_map_system_path_for_str(
        random.choice(constant.place_data["Greenhouse"])
    )
    general_movement_module(character_id, to_greenhouse)

    # 如果和玩家位于同一地点，则输出提示信息
    if character_data.position == cache.character_data[0].position:
        now_draw = draw.NormalDraw()
        now_draw.text = f"{character_data.name}打算去温室\n"
        now_draw.draw()


@handle_state_machine.add_state_machine(constant.StateMachine.MOVE_TO_REST_ROOM)
def character_move_to_rest_room(character_id: int):
    """
    移动至休息室
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    # 检索当前角色所在的大场景里有没有休息室，没有的话再随机选择其他区块
    now_position = character_data.position[0]
    find_flag = False
    for place in constant.place_data["Rest_Room"]:
        if place.split("\\")[0] == now_position:
            to_rest_room = map_handle.get_map_system_path_for_str(place)
            find_flag = True
            break
    if not find_flag:
        to_rest_room = map_handle.get_map_system_path_for_str(
    random.choice(constant.place_data["Rest_Room"])
    )

    general_movement_module(character_id, to_rest_room)

    # 如果和玩家位于同一地点，则输出提示信息
    if character_data.position == cache.character_data[0].position:
        now_draw = draw.NormalDraw()
        now_draw.text = f"{character_data.name}打算去休息\n"
        now_draw.draw()


@handle_state_machine.add_state_machine(constant.StateMachine.MOVE_TO_RESTAURANT)
def character_move_to_restaurant(character_id: int):
    """
    移动至餐馆（随机某个正餐餐馆）
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]

    # 检索当前角色所在的大场景里有没有餐馆，没有的话再随机选择其他区块
    now_position = character_data.position[0]
    find_flag = False
    for place in constant.place_data["Restaurant"]:
        if place.split("\\")[0] == now_position:
            to_rest_room = map_handle.get_map_system_path_for_str(place)
            find_flag = True
            break
    if not find_flag:
        to_rest_room = map_handle.get_map_system_path_for_str(
    random.choice(constant.place_data["Restaurant"])
    )

    general_movement_module(character_id, to_rest_room)


@handle_state_machine.add_state_machine(constant.StateMachine.MOVE_TO_MAINTENANCE_PLACE)
def character_move_to_maintenance_place(character_id: int):
    """
    移动至检修地点
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    to_maintenance_place_shop = map_handle.get_map_system_path_for_str(cache.rhodes_island.maintenance_place[character_id])
    general_movement_module(character_id, to_maintenance_place_shop)

    # 如果和玩家位于同一地点，则输出提示信息
    if character_data.position == cache.character_data[0].position:
        now_draw = draw.NormalDraw()
        now_draw.text = f"{character_data.name}打算去检修地点\n"
        now_draw.draw()


@handle_state_machine.add_state_machine(constant.StateMachine.MOVE_TO_PRODUCTION_WORKSHOP)
def character_move_to_production_workshop(character_id: int):
    """
    移动至生产车间
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]

    # 如果已经属于某个车间，则直接选择该车间
    need_allocated_flag = True
    for assembly_line_id in cache.rhodes_island.assembly_line:
        if character_id in cache.rhodes_island.assembly_line[assembly_line_id][1]:
            target_scene_name = f"assembly_line_{(str(assembly_line_id))}"
            target_scene_str = random.choice(constant.place_data[target_scene_name])
            need_allocated_flag = False

    # 如果没有被分配到某个生产车间，则优先去没有人的，如果没有，则随机选择一个
    if need_allocated_flag:
        empty_flag = False
        for target_scene_str in constant.place_data["Production_Workshop"]:
            close_type = map_handle.judge_scene_accessible(target_scene_str,character_id)
            if list(cache.scene_data[target_scene_str].character_list) == [] and close_type == "open":
                empty_flag = True
                break
        if not empty_flag:
            while 1:
                target_scene_str = random.choice(constant.place_data["Production_Workshop"])
                close_type = map_handle.judge_scene_accessible(target_scene_str,character_id)
                if close_type == "open":
                    break
        assembly_line_id = int(target_scene_str[-1]) - 1
        cache.rhodes_island.assembly_line[assembly_line_id][1].add(character_id)

    to_production_workshop = map_handle.get_map_system_path_for_str(target_scene_str)
    general_movement_module(character_id, to_production_workshop)

    # 如果和玩家位于同一地点，则输出提示信息
    if character_data.position == cache.character_data[0].position:
        now_draw = draw.NormalDraw()
        now_draw.text = f"{character_data.name}打算去生产车间\n"
        now_draw.draw()


@handle_state_machine.add_state_machine(constant.StateMachine.MOVE_TO_BATHZONE_LOCKER_ROOM)
def character_move_to_bathzone_locker_room(character_id: int):
    """
    移动至大浴场的更衣室
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]

    to_locker_room = []

    # 直接检索大浴场的更衣室
    for place in constant.place_data["Locker_Room"]:
        if place.split("\\")[0] == "大浴场":
            to_locker_room = map_handle.get_map_system_path_for_str(place)
            break

    # 以防没有找到更衣室
    if to_locker_room != []:

        general_movement_module(character_id, to_locker_room)

        # 如果和玩家位于同一地点，则输出提示信息
        if character_data.position == cache.character_data[0].position:
            now_draw = draw.NormalDraw()
            now_draw.text = f"{character_data.name}打算去大浴场的更衣室\n"
            now_draw.draw()


@handle_state_machine.add_state_machine(constant.StateMachine.MOVE_TO_BATHZONE_REST_ROOM)
def character_move_to_bathzone_rest_room(character_id: int):
    """
    移动至大浴场的休息室
    Keyword arguments:
    character_id -- 角色id
    """

    to_rest_room = []

    # 直接检索大浴场的休息室
    for place in constant.place_data["Rest_Room"]:
        if place.split("\\")[0] == "大浴场":
            to_rest_room = map_handle.get_map_system_path_for_str(place)
            break

    # 以防没有找到休息室
    if to_rest_room != []:
        general_movement_module(character_id, to_rest_room)


@handle_state_machine.add_state_machine(constant.StateMachine.MOVE_TO_TRAINING_LOCKER_ROOM)
def character_move_to_training_locker_room(character_id: int):
    """
    移动至训练场的更衣室
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]

    to_locker_room = []

    # 直接检索训练场的更衣室
    for place in constant.place_data["Locker_Room"]:
        if place.split("\\")[0] == "训练":
            to_locker_room = map_handle.get_map_system_path_for_str(place)
            break

    # 以防没有找到更衣室
    if to_locker_room == []:

        general_movement_module(character_id, to_locker_room)

        # 如果和玩家位于同一地点，则输出提示信息
        if character_data.position == cache.character_data[0].position:
            now_draw = draw.NormalDraw()
            now_draw.text = f"{character_data.name}打算去训练场的更衣室\n"
            now_draw.draw()


@handle_state_machine.add_state_machine(constant.StateMachine.MOVE_TO_BATH_ROOM)
def character_move_to_bath_room(character_id: int):
    """
    移动至淋浴室
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]

    # 检索当前角色所在的大场景里有没有淋浴室，没有的话再随机选择其他区块
    now_position = character_data.position[0]
    find_flag = False
    for place in constant.place_data["Bathroom"]:
        if place.split("\\")[0] == now_position:
            to_bath_room = map_handle.get_map_system_path_for_str(place)
            find_flag = True
            break
    if not find_flag:
        to_bath_room = map_handle.get_map_system_path_for_str(
    random.choice(constant.place_data["Bathroom"])
    )

    general_movement_module(character_id, to_bath_room)

    # 如果和玩家位于同一地点，则输出提示信息
    if character_data.position == cache.character_data[0].position:
        now_draw = draw.NormalDraw()
        now_draw.text = f"{character_data.name}打算去淋浴\n"
        now_draw.draw()


@handle_state_machine.add_state_machine(constant.StateMachine.MOVE_TO_TRAINING_ROOM)
def character_move_to_training_room(character_id: int):
    """
    根据职业自动移动至对应训练室
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.profession in {1,5,6,8}:
        room_name = "Fight_Room"
    else:
        room_name = "Shoot_Room"

    to_training_room = map_handle.get_map_system_path_for_str(
    random.choice(constant.place_data[room_name])
    )

    general_movement_module(character_id, to_training_room)

    # 如果和玩家位于同一地点，则输出提示信息
    if character_data.position == cache.character_data[0].position:
        now_draw = draw.NormalDraw()
        now_draw.text = f"{character_data.name}打算去进行战斗训练\n"
        now_draw.draw()


@handle_state_machine.add_state_machine(constant.StateMachine.MOVE_TO_PLAYER)
def character_move_to_player(character_id: int):
    """
    移动至玩家位置
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    to_dr = cache.character_data[0].position
    move_type, tem_1, move_path, move_time = character_move.character_move(character_id, to_dr)
    move_flag = True # flase的话就是等待
    # if move_path == []:
    #     print(f"debug {character_data.name} 无法移动至玩家位置，move_type = {move_type},当前位置 = {character_data.position},move_path = {move_path}")
    # 进行私密跟随判断
    move_flag, wait_flag = character_move.judge_character_move_to_private(character_id, move_path)
    # 最后决定是移动还是继续等待
    if move_flag:
        character_data.action_info.follow_wait_time = 0
        general_movement_module(character_id, to_dr)
        # print(f"debug {character_data.name} 移动至玩家位置,move_final_target = {character_data.behavior.move_final_target}")
    else:
        character_data.state = constant.CharacterStatus.STATUS_WAIT
        character_data.behavior.behavior_id = constant.Behavior.WAIT
        character_data.behavior.duration = 5
        character_data.action_info.follow_wait_time += 5
    # if character_data.sp_flag.is_follow:
    #     print(f"debug {character_data.name}向玩家移动，当前跟随={character_data.sp_flag.is_follow}")


@handle_state_machine.add_state_machine(constant.StateMachine.CONTINUE_MOVE)
def character_continue_move(character_id: int):
    """
    继续移动
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    # print(f"\n\ndebug 判断 {character_data.name} 继续移动")
    # 仅在有最终目标的情况下进行判断
    if character_data.behavior.move_final_target != []:

        # 如果还没有抵达最终目标地点
        if character_data.position != character_data.behavior.move_final_target:
            # print(f"debug {character_data.name} 还没有抵达最终目标地点:{character_data.behavior.move_final_target}")

            # 基础数据计算
            to_dr = cache.character_data[0].position
            tem_1, tem_2, move_path, move_time = character_move.character_move(character_id, character_data.behavior.move_final_target)
            move_flag = True # true的话就是移动
            wait_flag = False # true的话就是等待

            # 如果是向玩家移动的话
            if character_data.behavior.move_final_target == to_dr:
                # 进行私密跟随判断
                move_flag, wait_flag = character_move.judge_character_move_to_private(character_id, move_path)
                # print(f"debug {character_data.name} 向玩家移动，move_flag = {move_flag}, wait_flag = {wait_flag}")

            if move_flag:
                character_data.state = constant.CharacterStatus.STATUS_MOVE
                character_data.behavior.behavior_id = constant.Behavior.MOVE
                character_data.behavior.move_target = move_path
                character_data.behavior.duration = move_time
                character_data.action_info.follow_wait_time = 0
            elif wait_flag:
                character_data.state = constant.CharacterStatus.STATUS_WAIT
                character_data.behavior.behavior_id = constant.Behavior.WAIT
                character_data.behavior.duration = 5
                character_data.action_info.follow_wait_time += 5


@handle_state_machine.add_state_machine(constant.StateMachine.CHAT_RAND_CHARACTER)
def character_chat_rand_character(character_id: int):
    """
    角色和场景内玩家以外的随机角色聊天
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    scene_data: game_type.Scene = cache.scene_data[scene_path_str]
    character_set = scene_data.character_list.copy()
    character_set.remove(character_id)
    if 0 in character_set:
        character_set.remove(0)
    character_list = list(character_set)
    if len(character_list):
        target_id = random.choice(character_list)
        if handle_premise.handle_action_not_sleep(target_id):
            character_data.behavior.behavior_id = constant.Behavior.CHAT
            character_data.behavior.duration = 10
            character_data.target_character_id = target_id
            character_data.state = constant.CharacterStatus.STATUS_CHAT


@handle_state_machine.add_state_machine(constant.StateMachine.STROKE_RAND_CHARACTER)
def character_stroke_rand_character(character_id: int):
    """
    角色和场景内随机角色身体接触
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    scene_data: game_type.Scene = cache.scene_data[scene_path_str]
    character_set = scene_data.character_list.copy()
    character_set.remove(character_id)
    if 0 in character_set:
        character_set.remove(0)
    character_list = list(character_set)
    if len(character_list):
        target_id = random.choice(character_list)
        if handle_premise.handle_action_not_sleep(target_id):
            character_data.behavior.behavior_id = constant.Behavior.STROKE
            character_data.behavior.duration = 10
            character_data.target_character_id = target_id
            character_data.state = constant.CharacterStatus.STATUS_STROKE


@handle_state_machine.add_state_machine(constant.StateMachine.CHAT_TO_DR)
def character_chat_to_dr(character_id: int):
    """
    角色和玩家聊天
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_id = 0
    character_data.behavior.behavior_id = constant.Behavior.CHAT
    character_data.behavior.duration = 5
    character_data.target_character_id = target_id
    character_data.state = constant.CharacterStatus.STATUS_CHAT


@handle_state_machine.add_state_machine(constant.StateMachine.STROKE_TO_DR)
def character_stroke_to_dr(character_id: int):
    """
    角色和玩家身体接触
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_id = 0
    character_data.behavior.behavior_id = constant.Behavior.STROKE
    character_data.behavior.duration = 10
    character_data.target_character_id = target_id
    character_data.state = constant.CharacterStatus.STATUS_STROKE


@handle_state_machine.add_state_machine(constant.StateMachine.MAKE_COFFEE_TO_DR)
def character_make_coffee_to_dr(character_id: int):
    """
    角色给玩家泡咖啡
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_id = 0
    character_data.behavior.behavior_id = constant.Behavior.MAKE_COFFEE
    character_data.behavior.duration = 15
    character_data.target_character_id = target_id
    character_data.state = constant.CharacterStatus.STATUS_MAKE_COFFEE


@handle_state_machine.add_state_machine(constant.StateMachine.MAKE_COFFEE_ADD_TO_DR)
def character_make_coffee_Add_to_dr(character_id: int):
    """
    角色给玩家泡咖啡（加料）
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_id = 0
    character_data.behavior.behavior_id = constant.Behavior.MAKE_COFFEE_ADD
    character_data.behavior.duration = 15
    character_data.target_character_id = target_id
    character_data.state = constant.CharacterStatus.STATUS_MAKE_COFFEE_ADD


@handle_state_machine.add_state_machine(constant.StateMachine.SEE_H_AND_MOVE_TO_DORMITORY)
def character_see_h_and_move_to_dormitory(character_id: int):
    """
    目睹玩家和其他角色H
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    to_target = map_handle.get_map_system_path_for_str(character_data.dormitory)
    general_movement_module(character_id, to_target)

    # 输出提示信息，并结算把柄
    now_draw = draw.NormalDraw()
    now_draw.text = f"被{character_data.name}看到了情事现场\n"
    if character_data.talent[222]:
        now_draw.text += f"{character_data.name}还不懂这是什么意义，被你随口糊弄走了"
    else:
        character_data.talent[401] = 1
        now_draw.text += f"{character_data.name}获得了[持有博士把柄]\n"
        now_draw.text += f"{character_data.name}红着脸跑走了"
    now_draw.draw()
    line_feed.draw()

    # 中断H
    pl_data: game_type.Character = cache.character_data[0]
    target_data = cache.character_data[pl_data.target_character_id]
    target_data.action_info.h_interrupt = 1
    # 原地待机10分钟
    target_data.behavior.behavior_id = constant.Behavior.WAIT
    target_data.state = constant.CharacterStatus.STATUS_WAIT
    target_data.behavior.duration = 10
    pl_data.behavior.behavior_id = constant.Behavior.H_INTERRUPT
    pl_data.state = constant.CharacterStatus.STATUS_H_INTERRUPT
    handle_instruct.handle_end_h()


@handle_state_machine.add_state_machine(constant.StateMachine.SINGING)
def character_singing(character_id: int):
    """
    唱歌
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    character_data.behavior.behavior_id = constant.Behavior.SINGING
    character_data.behavior.duration = 10
    character_data.state = constant.CharacterStatus.STATUS_SINGING


@handle_state_machine.add_state_machine(constant.StateMachine.PLAY_INSTRUMENT)
def character_play_instrument(character_id: int):
    """
    角色演奏乐器
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    character_data.behavior.behavior_id = constant.Behavior.PLAY_INSTRUMENT
    character_data.behavior.duration = 30
    character_data.state = constant.CharacterStatus.STATUS_PLAY_INSTRUMENT


@handle_state_machine.add_state_machine(constant.StateMachine.ENTERTAIN_TRAINING)
def character_training(character_id: int):
    """
    角色战斗训练
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    character_data.behavior.behavior_id = constant.Behavior.TRAINING
    character_data.behavior.duration = 120
    character_data.state = constant.CharacterStatus.STATUS_TRAINING


@handle_state_machine.add_state_machine(constant.StateMachine.ENTERTAIN_SINGING)
def character_training(character_id: int):
    """
    娱乐：唱歌
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    character_data.behavior.behavior_id = constant.Behavior.SINGING
    character_data.behavior.duration = 10
    character_data.state = constant.CharacterStatus.STATUS_SINGING


@handle_state_machine.add_state_machine(constant.StateMachine.ENTERTAIN_PLAY_CLASSIC_INSTRUMENT)
def character_play_classic_instrument(character_id: int):
    """
    娱乐：演奏传统乐器
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    character_data.behavior.behavior_id = constant.Behavior.PLAY_INSTRUMENT
    character_data.behavior.duration = 10
    character_data.state = constant.CharacterStatus.STATUS_PLAY_INSTRUMENT


@handle_state_machine.add_state_machine(constant.StateMachine.ENTERTAIN_PLAY_MODEN_INSTRUMENT)
def character_play_moden_instrument(character_id: int):
    """
    娱乐：演奏现代乐器
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    character_data.behavior.behavior_id = constant.Behavior.PLAY_INSTRUMENT
    character_data.behavior.duration = 10
    character_data.state = constant.CharacterStatus.STATUS_PLAY_INSTRUMENT


@handle_state_machine.add_state_machine(constant.StateMachine.ENTERTAIN_WATCH_MOVIE)
def character_watch_movie(character_id: int):
    """
    娱乐：看电影
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    character_data.behavior.duration = 120
    character_data.behavior.behavior_id = constant.Behavior.WATCH_MOVIE
    character_data.state = constant.CharacterStatus.STATUS_WATCH_MOVIE


@handle_state_machine.add_state_machine(constant.StateMachine.ENTERTAIN_PHOTOGRAPHY)
def character_photography(character_id: int):
    """
    娱乐：摄影
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    character_data.behavior.duration = 60
    character_data.behavior.behavior_id = constant.Behavior.PHOTOGRAPHY
    character_data.state = constant.CharacterStatus.STATUS_PHOTOGRAPHY

@handle_state_machine.add_state_machine(constant.StateMachine.ENTERTAIN_PLAY_WATER)
def character_play_water(character_id: int):
    """
    娱乐：玩水
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    character_data.behavior.duration = 60
    character_data.behavior.behavior_id = constant.Behavior.PLAY_WATER
    character_data.state = constant.CharacterStatus.STATUS_PLAY_WATER

@handle_state_machine.add_state_machine(constant.StateMachine.ENTERTAIN_PLAY_CHESS)
def character_play_chess(character_id: int):
    """
    娱乐：下棋
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    character_data.behavior.duration = 30
    character_data.behavior.behavior_id = constant.Behavior.PLAY_CHESS
    character_data.state = constant.CharacterStatus.STATUS_PLAY_CHESS


@handle_state_machine.add_state_machine(constant.StateMachine.ENTERTAIN_PLAY_MAHJONG)
def character_play_mahjong(character_id: int):
    """
    娱乐：打麻将
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    character_data.behavior.duration = 60
    character_data.behavior.behavior_id = constant.Behavior.PLAY_MAHJONG
    character_data.state = constant.CharacterStatus.STATUS_PLAY_MAHJONG


@handle_state_machine.add_state_machine(constant.StateMachine.ENTERTAIN_PLAY_CARDS)
def character_play_cards(character_id: int):
    """
    娱乐：打牌
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    character_data.behavior.duration = 60
    character_data.behavior.behavior_id = constant.Behavior.PLAY_CARDS
    character_data.state = constant.CharacterStatus.STATUS_PLAY_CARDS


@handle_state_machine.add_state_machine(constant.StateMachine.ENTERTAIN_REHEARSE_DANCE)
def character_rehearse_dance(character_id: int):
    """
    娱乐：排演舞剧
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    character_data.behavior.duration = 120
    character_data.behavior.behavior_id = constant.Behavior.REHEARSE_DANCE
    character_data.state = constant.CharacterStatus.STATUS_REHEARSE_DANCE


@handle_state_machine.add_state_machine(constant.StateMachine.ENTERTAIN_PLAY_ARCADE_GAME)
def character_play_arcade_game(character_id: int):
    """
    娱乐：玩街机游戏
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    character_data.behavior.duration = 60
    character_data.behavior.behavior_id = constant.Behavior.PLAY_ARCADE_GAME
    character_data.state = constant.CharacterStatus.STATUS_PLAY_ARCADE_GAME


@handle_state_machine.add_state_machine(constant.StateMachine.ENTERTAIN_SWIMMING)
def character_swimming(character_id: int):
    """
    娱乐：游泳
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    character_data.behavior.duration = 60
    character_data.behavior.behavior_id = constant.Behavior.SWIMMING
    character_data.state = constant.CharacterStatus.STATUS_SWIMMING


@handle_state_machine.add_state_machine(constant.StateMachine.ENTERTAIN_TASTE_WINE)
def character_taste_wine(character_id: int):
    """
    娱乐：品酒
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    character_data.behavior.duration = 30
    character_data.behavior.behavior_id = constant.Behavior.TASTE_WINE
    character_data.state = constant.CharacterStatus.STATUS_TASTE_WINE


@handle_state_machine.add_state_machine(constant.StateMachine.ENTERTAIN_TASTE_TEA)
def character_taste_tea(character_id: int):
    """
    娱乐：品茶
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    character_data.behavior.duration = 30
    character_data.behavior.behavior_id = constant.Behavior.TASTE_TEA
    character_data.state = constant.CharacterStatus.STATUS_TASTE_TEA


@handle_state_machine.add_state_machine(constant.StateMachine.ENTERTAIN_TASTE_COFFEE)
def character_taste_coffee(character_id: int):
    """
    娱乐：品咖啡
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    character_data.behavior.duration = 30
    character_data.behavior.behavior_id = constant.Behavior.TASTE_COFFEE
    character_data.state = constant.CharacterStatus.STATUS_TASTE_COFFEE


@handle_state_machine.add_state_machine(constant.StateMachine.ENTERTAIN_TASTE_DESSERT)
def character_taste_dessert(character_id: int):
    """
    娱乐：品尝点心
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    character_data.behavior.duration = 30
    character_data.behavior.behavior_id = constant.Behavior.TASTE_DESSERT
    character_data.state = constant.CharacterStatus.STATUS_TASTE_DESSERT


@handle_state_machine.add_state_machine(constant.StateMachine.ENTERTAIN_TASTE_FOOD)
def character_taste_food(character_id: int):
    """
    娱乐：品尝美食
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    character_data.behavior.duration = 30
    character_data.behavior.behavior_id = constant.Behavior.TASTE_FOOD
    character_data.state = constant.CharacterStatus.STATUS_TASTE_FOOD


@handle_state_machine.add_state_machine(constant.StateMachine.ENTERTAIN_PLAY_HOUSE)
def character_play_house(character_id: int):
    """
    娱乐：过家家
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    character_data.behavior.duration = 60
    character_data.behavior.behavior_id = constant.Behavior.PLAY_HOUSE
    character_data.state = constant.CharacterStatus.STATUS_PLAY_HOUSE


@handle_state_machine.add_state_machine(constant.StateMachine.ENTERTAIN_STYLE_HAIR)
def character_style_hair(character_id: int):
    """
    娱乐：修整发型
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    character_data.behavior.duration = 60
    character_data.behavior.behavior_id = constant.Behavior.STYLE_HAIR
    character_data.state = constant.CharacterStatus.STATUS_STYLE_HAIR


@handle_state_machine.add_state_machine(constant.StateMachine.ENTERTAIN_FULL_BODY_STYLING)
def character_full_body_styling(character_id: int):
    """
    娱乐：全身造型服务
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    character_data.behavior.duration = 120
    character_data.behavior.behavior_id = constant.Behavior.FULL_BODY_STYLING
    character_data.state = constant.CharacterStatus.STATUS_FULL_BODY_STYLING


@handle_state_machine.add_state_machine(constant.StateMachine.ENTERTAIN_SOAK_FEET)
def character_soak_feet(character_id: int):
    """
    娱乐：泡脚
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    character_data.behavior.duration = 30
    character_data.behavior.behavior_id = constant.Behavior.SOAK_FEET
    character_data.state = constant.CharacterStatus.STATUS_SOAK_FEET


@handle_state_machine.add_state_machine(constant.StateMachine.ENTERTAIN_STEAM_SAUNA)
def character_steam_sauna(character_id: int):
    """
    娱乐：蒸桑拿
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    character_data.behavior.duration = 30
    character_data.behavior.behavior_id = constant.Behavior.STEAM_SAUNA
    character_data.state = constant.CharacterStatus.STATUS_STEAM_SAUNA


@handle_state_machine.add_state_machine(constant.StateMachine.ENTERTAIN_HYDROTHERAPY_TREATMENT)
def character_hydrotherapy_treatment(character_id: int):
    """
    娱乐：水疗护理
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    character_data.behavior.duration = 60
    character_data.behavior.behavior_id = constant.Behavior.HYDROTHERAPY_TREATMENT
    character_data.state = constant.CharacterStatus.STATUS_HYDROTHERAPY_TREATMENT


@handle_state_machine.add_state_machine(constant.StateMachine.ENTERTAIN_ONSEN_BATH)
def character_onsen_bath(character_id: int):
    """
    娱乐：泡温泉
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    character_data.behavior.duration = 60
    character_data.behavior.behavior_id = constant.Behavior.ONSEN_BATH
    character_data.state = constant.CharacterStatus.STATUS_ONSEN_BATH


@handle_state_machine.add_state_machine(constant.StateMachine.SINGING_RAND_CHARACTER)
def character_singing_to_rand_character(character_id: int):
    """
    唱歌给房间里随机角色听
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_list = list(
        cache.scene_data[
            map_handle.get_map_system_path_str_for_list(character_data.position)
        ].character_list
    )
    character_list.remove(character_id)
    if 0 in character_list:
        character_list.remove(0)
    if len(character_list):
        target_id = random.choice(character_list)
        character_data.behavior.behavior_id = constant.Behavior.SINGING
        character_data.behavior.duration = 10
        character_data.target_character_id = target_id
        character_data.state = constant.CharacterStatus.STATUS_SINGING


@handle_state_machine.add_state_machine(constant.StateMachine.PLAY_INSTRUMENT_RAND_CHARACTER)
def character_play_instrument_to_rand_character(character_id: int):
    """
    演奏乐器给房间里随机角色听
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_list = list(
        cache.scene_data[
            map_handle.get_map_system_path_str_for_list(character_data.position)
        ].character_list
    )
    character_list.remove(character_id)
    if 0 in character_list:
        character_list.remove(0)
    if len(character_list):
        target_id = random.choice(character_list)
        character_data.behavior.behavior_id = constant.Behavior.PLAY_INSTRUMENT
        character_data.behavior.duration = 30
        character_data.target_character_id = target_id
        character_data.state = constant.CharacterStatus.STATUS_PLAY_INSTRUMENT


@handle_state_machine.add_state_machine(constant.StateMachine.PEE)
def character_pee(character_id: int):
    """
    角色解手
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    character_data.behavior.behavior_id = constant.Behavior.PEE
    character_data.state = constant.CharacterStatus.STATUS_PEE
    character_data.behavior.duration = 5


@handle_state_machine.add_state_machine(constant.StateMachine.START_SHOWER)
def character_start_shower(character_id: int):
    """
    进入要脱衣服（洗澡）状态
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.shower = 1
    character_data.target_character_id = character_id
    character_data.behavior.behavior_id = constant.Behavior.SHARE_BLANKLY
    character_data.behavior.duration = 1
    character_data.state = constant.CharacterStatus.STATUS_ARDER


@handle_state_machine.add_state_machine(constant.StateMachine.SIWM_1)
def character_swim_1(character_id: int):
    """
    进入要换泳衣状态
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.swim = 1
    character_data.target_character_id = character_id
    character_data.behavior.behavior_id = constant.Behavior.SHARE_BLANKLY
    character_data.behavior.duration = 1
    character_data.state = constant.CharacterStatus.STATUS_ARDER


@handle_state_machine.add_state_machine(constant.StateMachine.SIWM_2)
def character_swim_2(character_id: int):
    """
    脱掉衣服并换上泳衣并进入要游泳状态
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    character_data.behavior.behavior_id = constant.Behavior.READY_TO_SWIM
    character_data.state = constant.CharacterStatus.STATUS_READY_TO_SWIM
    character_data.behavior.duration = 10


@handle_state_machine.add_state_machine(constant.StateMachine.START_BATHHOUSE_ENTERTAINMENT)
def character_start_bathhouse_entertainment(character_id: int):
    """
    进入要去大浴场娱乐_要更衣状态
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.bathhouse_entertainment = 1
    character_data.target_character_id = character_id
    character_data.behavior.behavior_id = constant.Behavior.SHARE_BLANKLY
    character_data.behavior.duration = 1
    character_data.state = constant.CharacterStatus.STATUS_ARDER


@handle_state_machine.add_state_machine(constant.StateMachine.FOOT_CLOTH_TO_LOCKER)
def character_foot_cloth_to_locker(character_id: int):
    """
    袜子和鞋子转移到衣柜里
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    character_data.behavior.behavior_id = constant.Behavior.FOOT_CLOTH_TO_LOCKER
    character_data.state = constant.CharacterStatus.STATUS_FOOT_CLOTH_TO_LOCKER
    character_data.behavior.duration = 5


@handle_state_machine.add_state_machine(constant.StateMachine.WEAR_TO_LOCKER_AND_GET_SHOWER_CLOTH)
def character_wear_to_locker_and_get_shower_cloth(character_id: int):
    """
    当前身上衣服转移到衣柜里，并换上浴帽和浴巾
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    character_data.behavior.behavior_id = constant.Behavior.WEAR_TO_LOCKER_AND_GET_SHOWER_CLOTH
    character_data.state = constant.CharacterStatus.STATUS_WEAR_TO_LOCKER_AND_GET_SHOWER_CLOTH
    character_data.behavior.duration = 10


@handle_state_machine.add_state_machine(constant.StateMachine.CLEAN_WEAR_AND_LOCKER_TO_WEAR)
def character_clean_wear_and_locker_to_wear(character_id: int):
    """
    清空身上的衣服然后穿回衣柜的衣服，如果有浴场或游泳娱乐flag则置0
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    character_data.behavior.behavior_id = constant.Behavior.CLEAN_WEAR_AND_LOCKER_TO_WEAR
    character_data.state = constant.CharacterStatus.STATUS_CLEAN_WEAR_AND_LOCKER_TO_WEAR
    character_data.behavior.duration = 10

    # 如果有浴场或游泳娱乐flag则置0
    if character_data.sp_flag.bathhouse_entertainment:
        character_data.sp_flag.bathhouse_entertainment = 0
    if character_data.sp_flag.swim:
        character_data.sp_flag.swim = 0


@handle_state_machine.add_state_machine(constant.StateMachine.HELP_BUY_FOOD_1)
def character_help_buy_food(character_id: int):
    """
    进入要买饭状态
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.help_buy_food = 1
    character_data.target_character_id = character_id
    character_data.behavior.behavior_id = constant.Behavior.SHARE_BLANKLY
    character_data.behavior.duration = 1
    character_data.state = constant.CharacterStatus.STATUS_ARDER

    # 如果和玩家位于同一地点，则输出提示信息
    if character_data.position == cache.character_data[0].position:
        now_draw = draw.NormalDraw()
        now_draw.text = f"{character_data.name}打算去买饭\n"
        now_draw.draw()


@handle_state_machine.add_state_machine(constant.StateMachine.HELP_MAKE_FOOD_1)
def character_help_make_food(character_id: int):
    """
    进入要做饭状态
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.help_make_food = 1
    character_data.target_character_id = character_id
    character_data.behavior.behavior_id = constant.Behavior.SHARE_BLANKLY
    character_data.behavior.duration = 1
    character_data.state = constant.CharacterStatus.STATUS_ARDER

    # 如果和玩家位于同一地点，则输出提示信息
    if character_data.position == cache.character_data[0].position:
        now_draw = draw.NormalDraw()
        now_draw.text = f"{character_data.name}打算去做饭\n"
        now_draw.draw()


@handle_state_machine.add_state_machine(constant.StateMachine.MORNING_SALUTATION_FLAG_1)
def character_morning_salutation_flag_1(character_id: int):
    """
    进入要早安问候状态
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.morning_salutation = 1
    character_data.target_character_id = character_id
    character_data.behavior.behavior_id = constant.Behavior.SHARE_BLANKLY
    character_data.behavior.duration = 1
    character_data.state = constant.CharacterStatus.STATUS_ARDER
    # print(f"{character_data.name}进入要早安问候状态")


@handle_state_machine.add_state_machine(constant.StateMachine.NIGHT_SALUTATION_FLAG_1)
def character_night_salutation_flag_1(character_id: int):
    """
    进入要晚安问候状态
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.night_salutation = 1
    character_data.target_character_id = character_id
    character_data.behavior.behavior_id = constant.Behavior.SHARE_BLANKLY
    character_data.behavior.duration = 1
    character_data.state = constant.CharacterStatus.STATUS_ARDER
    # print(f"debug {character_data.name} 进入要晚安问候状态，time = {cache.game_time}")


@handle_state_machine.add_state_machine(constant.StateMachine.START_MILK)
def character_start_milk(character_id: int):
    """
    进入要挤奶状态
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.milk = 1
    character_data.target_character_id = character_id
    character_data.behavior.behavior_id = constant.Behavior.SHARE_BLANKLY
    character_data.behavior.duration = 1
    character_data.state = constant.CharacterStatus.STATUS_ARDER


@handle_state_machine.add_state_machine(constant.StateMachine.MAKE_MILK)
def character_make_milk(character_id: int):
    """
    角色挤奶
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    character_data.behavior.behavior_id = constant.Behavior.MILK
    character_data.state = constant.CharacterStatus.STATUS_MILK
    character_data.behavior.duration = 30


@handle_state_machine.add_state_machine(constant.StateMachine.WEAR_TO_LOCKER)
def character_wear_to_locker(character_id: int):
    """
    当前身上衣服转移到衣柜里
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    character_data.behavior.behavior_id = constant.Behavior.WEAR_TO_LOCKER
    character_data.state = constant.CharacterStatus.STATUS_WEAR_TO_LOCKER
    character_data.behavior.duration = 10
    if character_data.position == cache.character_data[0].position:
        now_draw = draw.NormalDraw()
        now_draw.text = f"{character_data.name}脱成全裸了\n"
        now_draw.draw()


@handle_state_machine.add_state_machine(constant.StateMachine.LOCKER_TO_WEAR)
def character_locker_to_wear(character_id: int):
    """
    当前衣柜里衣服转移到身上，如果有浴场flag则置0
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    character_data.behavior.behavior_id = constant.Behavior.LOCKER_TO_WEAR
    character_data.state = constant.CharacterStatus.STATUS_LOCKER_TO_WEAR
    character_data.behavior.duration = 10
    if character_data.position == cache.character_data[0].position:
        now_draw = draw.NormalDraw()
        now_draw.text = f"{character_data.name}穿上了衣服\n"
        now_draw.draw()
    # 如果有浴场或游泳娱乐flag则置0
    if character_data.sp_flag.bathhouse_entertainment:
        character_data.sp_flag.bathhouse_entertainment = 0


@handle_state_machine.add_state_machine(constant.StateMachine.TAKE_SHOWER)
def character_take_shower(character_id: int):
    """
    角色淋浴
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    character_data.behavior.behavior_id = constant.Behavior.TAKE_SHOWER
    character_data.state = constant.CharacterStatus.STATUS_TAKE_SHOWER
    character_data.behavior.duration = 30


@handle_state_machine.add_state_machine(constant.StateMachine.GET_SHOWER_CLOTH_AND_CLEAN_LOCKER)
def character_get_shower_cloth_and_clean_locker(character_id: int):
    """
    角色换上浴帽和浴巾并清空衣柜
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    character_data.behavior.behavior_id = constant.Behavior.PUT_SHOWER_CLOTH
    character_data.state = constant.CharacterStatus.STATUS_PUT_SHOWER_CLOTH
    character_data.behavior.duration = 10
    if character_data.position == cache.character_data[0].position:
        now_draw = draw.NormalDraw()
        now_draw.text = f"{character_data.name}换上了浴帽和浴巾\n"
        now_draw.draw()


@handle_state_machine.add_state_machine(constant.StateMachine.START_EAT_FOOD)
def character_start_eat_food(character_id: int):
    """
    进入要取餐状态
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.eat_food = 1
    character_data.target_character_id = character_id
    character_data.behavior.behavior_id = constant.Behavior.SHARE_BLANKLY
    character_data.behavior.duration = 1
    character_data.state = constant.CharacterStatus.STATUS_ARDER


@handle_state_machine.add_state_machine(constant.StateMachine.BUY_RAND_FOOD_AT_FOODSHOP)
def character_buy_rand_food_at_foodshop(character_id: int):
    """
    在取餐区购买随机食物
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    new_food_list = []
    for food_id in cache.restaurant_data:
        if not len(cache.restaurant_data[food_id]):
            continue
        for food_uid in cache.restaurant_data[food_id]:
            now_food: game_type.Food = cache.restaurant_data[food_id][food_uid]
            # if now_food.eat:
            new_food_list.append(food_id)
            break
    if not len(new_food_list):
        return
    now_food_id = random.choice(new_food_list)
    now_food = cache.restaurant_data[now_food_id][
        random.choice(list(cache.restaurant_data[now_food_id].keys()))
    ]
    character_data.food_bag[now_food.uid] = now_food
    del cache.restaurant_data[now_food_id][now_food.uid]

    # 记录食物名字
    food_recipe: game_type.Recipes = cache.recipe_data[now_food.recipe]
    food_name = food_recipe.name
    character_data.behavior.behavior_id = constant.Behavior.BUY_FOOD
    character_data.state = constant.CharacterStatus.STATUS_BUY_FOOD
    character_data.behavior.duration = 5
    character_data.behavior.food_name = food_name

    # 特殊flag进行对应更改
    # 帮忙买饭
    if character_data.sp_flag.help_buy_food == 1:
        character_data.sp_flag.help_buy_food = 2
    # 帮忙买第二次饭
    elif character_data.sp_flag.help_buy_food == 2:
        character_data.sp_flag.help_buy_food = 3
    # AI正常吃饭
    elif character_data.sp_flag.eat_food == 1:
        character_data.sp_flag.eat_food = 2


@handle_state_machine.add_state_machine(constant.StateMachine.EAT_BAG_RAND_FOOD)
def character_eat_rand_food(character_id: int):
    """
    角色随机食用背包中的食物
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    character_data.behavior.behavior_id = constant.Behavior.EAT
    now_food_list = []
    for food_id in character_data.food_bag:
        # now_food: game_type.Food = character_data.food_bag[food_id]
        # if 27 in now_food.feel and now_food.eat:
        now_food_list.append(food_id)
    choice_food_id = random.choice(now_food_list)
    character_data.behavior.target_food = character_data.food_bag[choice_food_id]
    character_data.state = constant.CharacterStatus.STATUS_EAT

    # 记录食物名字
    food_data: game_type.Food = character_data.food_bag[choice_food_id]
    food_recipe: game_type.Recipes = cache.recipe_data[food_data.recipe]
    food_name = food_recipe.name
    character_data.behavior.food_name = food_name
    character_data.behavior.duration = 30


@handle_state_machine.add_state_machine(constant.StateMachine.START_SLEEP)
def character_start_sleep(character_id: int):
    """
    进入要睡眠状态
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.sleep = 1
    character_data.target_character_id = character_id
    character_data.behavior.behavior_id = constant.Behavior.SHARE_BLANKLY
    character_data.behavior.duration = 1
    character_data.state = constant.CharacterStatus.STATUS_ARDER


@handle_state_machine.add_state_machine(constant.StateMachine.START_REST)
def character_start_rest(character_id: int):
    """
    进入要休息状态
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.rest = 1
    character_data.target_character_id = character_id
    character_data.behavior.behavior_id = constant.Behavior.SHARE_BLANKLY
    character_data.behavior.duration = 1
    character_data.state = constant.CharacterStatus.STATUS_ARDER


@handle_state_machine.add_state_machine(constant.StateMachine.START_PEE)
def character_start_pee(character_id: int):
    """
    进入要撒尿状态
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.pee = 1
    character_data.target_character_id = character_id
    character_data.behavior.behavior_id = constant.Behavior.SHARE_BLANKLY
    character_data.behavior.duration = 1
    character_data.state = constant.CharacterStatus.STATUS_ARDER


@handle_state_machine.add_state_machine(constant.StateMachine.WORK_CURE_PATIENT)
def character_work_cure_patient(character_id: int):
    """
    角色工作：治疗病人
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    character_data.behavior.behavior_id = constant.Behavior.CURE_PATIENT
    character_data.behavior.duration = 30
    character_data.state = constant.CharacterStatus.STATUS_CURE_PATIENT


@handle_state_machine.add_state_machine(constant.StateMachine.WORK_RECRUIT)
def character_work_recruit(character_id: int):
    """
    角色工作：招募干员
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    character_data.behavior.behavior_id = constant.Behavior.RECRUIT
    character_data.behavior.duration = 60
    character_data.state = constant.CharacterStatus.STATUS_RECRUIT


@handle_state_machine.add_state_machine(constant.StateMachine.WORK_TEACH)
def character_work_teach(character_id: int):
    """
    角色工作：授课
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    character_data.behavior.behavior_id = constant.Behavior.TEACH
    character_data.behavior.duration = 45
    character_data.state = constant.CharacterStatus.STATUS_TEACH
    # 将当前场景里所有工作是上学的角色变为学习状态
    # 遍历当前场景的其他角色
    scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    scene_data: game_type.Scene = cache.scene_data[scene_path_str]
    # 场景角色数大于等于2时进行检测
    if len(scene_data.character_list) >= 2:
        # 遍历当前角色列表
        for chara_id in scene_data.character_list:
            # 跳过自己
            if chara_id == character_id:
                continue
            else:
                other_character_data: game_type.Character = cache.character_data[chara_id]
                # 让对方变成听课状态
                if other_character_data.work.work_type == 152:
                    other_character_data.behavior.behavior_id = constant.Behavior.ATTENT_CLASS
                    other_character_data.behavior.duration = 45
                    other_character_data.state = constant.CharacterStatus.STATUS_ATTENT_CLASS


@handle_state_machine.add_state_machine(constant.StateMachine.WORK_ATTENT_CLASS)
def character_work_teach(character_id: int):
    """
    角色工作：上学
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    character_data.behavior.behavior_id = constant.Behavior.ATTENT_CLASS
    character_data.behavior.duration = 45
    character_data.state = constant.CharacterStatus.STATUS_ATTENT_CLASS


@handle_state_machine.add_state_machine(constant.StateMachine.WORK_LIBRARY_1)
def character_work_library_1(character_id: int):
    """
    工作：三成去图书馆，七成原地等待30分钟
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    rand_num = random.randint(0, 99)
    if rand_num < 30:
        to_library = map_handle.get_map_system_path_for_str(
            random.choice(constant.place_data["Library"])
        )
        general_movement_module(character_id, to_library)
    else:
        character_data.behavior.behavior_id = constant.Behavior.WAIT
        character_data.behavior.duration = 30
        character_data.state = constant.CharacterStatus.STATUS_WAIT


@handle_state_machine.add_state_machine(constant.StateMachine.WORK_LIBRARY_2)
def character_work_library_2(character_id: int):
    """
    工作：三成去图书馆办公室，七成看书
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    rand_num = random.randint(0, 99)
    if rand_num < 30:
        to_library = map_handle.get_map_system_path_for_str(
            random.choice(constant.place_data["Library_Office"])
        )
        general_movement_module(character_id, to_library)
    else:
        basement.check_random_borrow_book(character_id)# 检查是否要借书
        for book_id_all in character_data.entertainment.borrow_book_id_set:
            book_id = book_id_all
        book_data = game_config.config_book[book_id]
        character_data.behavior.behavior_id = constant.Behavior.READ_BOOK
        character_data.state = constant.CharacterStatus.STATUS_READ_BOOK
        character_data.behavior.book_id = book_id
        character_data.behavior.book_name = book_data.name
        character_data.behavior.duration = 30


@handle_state_machine.add_state_machine(constant.StateMachine.WORK_MAINTENANCE_1)
def character_work_maintenance_1(character_id: int):
    """
    工作：进入要检修状态，并随机指定一个检修地点
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.work_maintenance = 1
    character_data.target_character_id = character_id
    character_data.behavior.behavior_id = constant.Behavior.SHARE_BLANKLY
    character_data.behavior.duration = 1
    character_data.state = constant.CharacterStatus.STATUS_ARDER

    # 指定的地点需要是可进入的
    while 1:
        target_scene_str = random.choice(constant.place_data["Room"])
        close_type = map_handle.judge_scene_accessible(target_scene_str,character_id)
        if close_type == "open":
            break
    cache.rhodes_island.maintenance_place[character_id] = target_scene_str


@handle_state_machine.add_state_machine(constant.StateMachine.WORK_MAINTENANCE_2)
def character_work_maintenance_2(character_id: int):
    """
    角色工作：维护设施，并清零检修状态
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    character_data.behavior.behavior_id = constant.Behavior.MAINTENANCE_FACILITIES
    character_data.behavior.duration = 60
    character_data.state = constant.CharacterStatus.STATUS_MAINTENANCE_FACILITIES


@handle_state_machine.add_state_machine(constant.StateMachine.WORK_REPAIR_EQUIPMENT)
def character_work_repair_equipment(character_id: int):
    """
    角色工作：修理装备
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    
    character_data.target_character_id = character_id
    character_data.behavior.behavior_id = constant.Behavior.REPAIR_EQUIPMENT
    character_data.behavior.duration = 60
    character_data.state = constant.CharacterStatus.STATUS_REPAIR_EQUIPMENT


@handle_state_machine.add_state_machine(constant.StateMachine.WORK_COOK)
def character_work_cook(character_id: int):
    """
    角色工作：做饭
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    
    character_data.target_character_id = character_id
    character_data.behavior.behavior_id = constant.Behavior.NPC_WORK_COOK
    character_data.behavior.duration = 30
    character_data.state = constant.CharacterStatus.STATUS_NPC_WORK_COOK


@handle_state_machine.add_state_machine(constant.StateMachine.ASSISTANT_MAKE_FOOD)
def character_work_cook(character_id: int):
    """
    角色助理：做饭
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    
    character_data.target_character_id = character_id
    character_data.behavior.behavior_id = constant.Behavior.NPC_ASSISTANT_COOK
    character_data.behavior.duration = 30
    character_data.behavior.make_food_time = character_data.behavior.duration
    character_data.state = constant.CharacterStatus.STATUS_NPC_ASSISTANT_COOK
    # 特殊flag进行对应更改
    if character_data.sp_flag.help_make_food == 1:
        character_data.sp_flag.help_make_food = 2


@handle_state_machine.add_state_machine(constant.StateMachine.MORNING_SALUTATION_1)
def character_morning_salutation_1(character_id: int):
    """
    早安问候：叫起床
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    
    character_data.target_character_id = 0
    character_data.behavior.behavior_id = constant.Behavior.MORNING_SALUTATION_1
    character_data.behavior.duration = 5
    character_data.state = constant.CharacterStatus.STATUS_MORNING_SALUTATION_1
    # 特殊flag进行对应更改
    if character_data.sp_flag.morning_salutation == 1:
        character_data.sp_flag.morning_salutation = 2


@handle_state_machine.add_state_machine(constant.StateMachine.MORNING_SALUTATION_2)
def character_morning_salutation_2(character_id: int):
    """
    早安问候：早安吻
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    
    character_data.target_character_id = 0
    character_data.behavior.behavior_id = constant.Behavior.MORNING_SALUTATION_2
    character_data.behavior.duration = 5
    character_data.state = constant.CharacterStatus.STATUS_MORNING_SALUTATION_2
    # 特殊flag进行对应更改
    if character_data.sp_flag.morning_salutation == 1:
        character_data.sp_flag.morning_salutation = 2


@handle_state_machine.add_state_machine(constant.StateMachine.MORNING_SALUTATION_3)
def character_morning_salutation_2(character_id: int):
    """
    早安问候：早安咬
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    
    character_data.target_character_id = 0
    character_data.behavior.behavior_id = constant.Behavior.MORNING_SALUTATION_3
    character_data.behavior.duration = 10
    character_data.state = constant.CharacterStatus.STATUS_MORNING_SALUTATION_3
    # 特殊flag进行对应更改
    if character_data.sp_flag.morning_salutation == 1:
        character_data.sp_flag.morning_salutation = 2


@handle_state_machine.add_state_machine(constant.StateMachine.NIGHT_SALUTATION_1)
def character_night_salutation_1(character_id: int):
    """
    晚安问候：催睡觉
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    
    character_data.target_character_id = 0
    character_data.behavior.behavior_id = constant.Behavior.NIGHT_SALUTATION_1
    character_data.behavior.duration = 30
    character_data.state = constant.CharacterStatus.STATUS_NIGHT_SALUTATION_1


@handle_state_machine.add_state_machine(constant.StateMachine.NIGHT_SALUTATION_2)
def character_night_salutation_2(character_id: int):
    """
    晚安问候：晚安吻
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    
    character_data.target_character_id = 0
    character_data.behavior.behavior_id = constant.Behavior.NIGHT_SALUTATION_2
    character_data.behavior.duration = 5
    character_data.state = constant.CharacterStatus.STATUS_NIGHT_SALUTATION_2
    # 特殊flag进行对应更改
    if character_data.sp_flag.night_salutation == 1:
        character_data.sp_flag.night_salutation = 2


@handle_state_machine.add_state_machine(constant.StateMachine.NIGHT_SALUTATION_3)
def character_night_salutation_3(character_id: int):
    """
    晚安问候：晚安咬
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    
    character_data.target_character_id = 0
    character_data.behavior.behavior_id = constant.Behavior.NIGHT_SALUTATION_3
    character_data.behavior.duration = 10
    character_data.state = constant.CharacterStatus.STATUS_NIGHT_SALUTATION_3
    # 特殊flag进行对应更改
    if character_data.sp_flag.night_salutation == 1:
        character_data.sp_flag.night_salutation = 2


@handle_state_machine.add_state_machine(constant.StateMachine.WORK_PRODUCE)
def character_work_produce(character_id: int):
    """
    角色工作：制造产品
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    character_data.behavior.behavior_id = constant.Behavior.PRODUCE
    character_data.state = constant.CharacterStatus.STATUS_PRODUCE
    character_data.behavior.duration = 30


@handle_state_machine.add_state_machine(constant.StateMachine.WORK_OFFICIAL_WORK)
def character_work_official_work(character_id: int):
    """
    工作：处理公务
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    character_data.behavior.duration = 60
    character_data.behavior.behavior_id = constant.Behavior.OFFICIAL_WORK
    character_data.state = constant.CharacterStatus.STATUS_OFFICIAL_WORK


@handle_state_machine.add_state_machine(constant.StateMachine.WORK_MASSAGE)
def character_work_massage(character_id: int):
    """
    工作：按摩（自动寻找对象）
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.behavior.duration = 30
    character_data.behavior.behavior_id = constant.Behavior.OFFICIAL_WORK
    character_data.state = constant.CharacterStatus.STATUS_OFFICIAL_WORK

    scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    scene_data: game_type.Scene = cache.scene_data[scene_path_str]
    # 场景角色数大于等于2时进行检测
    if len(scene_data.character_list) >= 2:
        # 遍历当前角色列表
        for chara_id in scene_data.character_list:
            # 遍历非玩家的角色
            if chara_id != character_id:
                other_character_data: game_type.Character = cache.character_data[chara_id]
                if other_character_data.work.work_type != 171:
                    character_data.target_character_id = chara_id
                    break


@handle_state_machine.add_state_machine(constant.StateMachine.WORK_INVITE_VISITOR)
def character_work_invite_visitor(character_id: int):
    """
    工作：邀请访客
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    character_data.behavior.duration = 60
    character_data.behavior.behavior_id = constant.Behavior.INVITE_VISITOR
    character_data.state = constant.CharacterStatus.STATUS_INVITE_VISITOR


@handle_state_machine.add_state_machine(constant.StateMachine.WORK_PLANT_MANAGE_CROP)
def character_work_plant_manage_crop(character_id: int):
    """
    工作：种植与养护作物
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id
    character_data.behavior.duration = 60
    character_data.behavior.behavior_id = constant.Behavior.PLANT_MANAGE_CROP
    character_data.state = constant.CharacterStatus.STATUS_PLANT_MANAGE_CROP


@handle_state_machine.add_state_machine(constant.StateMachine.ENTERTAIN_READ)
def character_entertain_read(character_id: int):
    """
    角色娱乐：读书
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    # 检查是否要借书
    basement.check_random_borrow_book(character_id)

    for book_id_all in character_data.entertainment.borrow_book_id_set:
        book_id = book_id_all
    book_data = game_config.config_book[book_id]
    character_data.behavior.behavior_id = constant.Behavior.READ_BOOK
    character_data.state = constant.CharacterStatus.STATUS_READ_BOOK
    character_data.behavior.book_id = book_id
    character_data.behavior.book_name = book_data.name
    character_data.behavior.duration = 30

