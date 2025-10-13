from functools import wraps
from types import FunctionType
from Script.Core import cache_control, constant, constant_promise, game_type, get_text

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """


def add_premise(premise: str) -> FunctionType:
    """
    添加前提
    Keyword arguments:
    premise -- 前提id
    Return arguments:
    FunctionType -- 前提处理函数对象
    """

    def decoraror(func):
        @wraps(func)
        def return_wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        constant.handle_premise_data[premise] = return_wrapper
        return return_wrapper

    return decoraror


@add_premise(constant_promise.Premise.HAVE_WORK)
def handle_have_work(character_id: int) -> int:
    """
    自己有工作
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type > 0


@add_premise(constant_promise.Premise.WORK_IS_POWER_OPERATOR)
def handle_work_is_power_operator(character_id: int) -> int:
    """
    自己的工作为供能调控员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 11


@add_premise(constant_promise.Premise.WORK_IS_MAINTENANCE_ENGINEER)
def handle_work_is_maintenance_engineer(character_id: int) -> int:
    """
    自己的工作为检修工程师
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 21


@add_premise(constant_promise.Premise.WORK_IS_BLACKSMITH)
def handle_work_is_blacksmith(character_id: int) -> int:
    """
    自己的工作为铁匠
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 22


@add_premise(constant_promise.Premise.WORK_IS_DOCTOR)
def handle_work_is_doctor(character_id: int) -> int:
    """
    自己的工作为医生
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 61


@add_premise(constant_promise.Premise.WORK_IS_HR)
def handle_work_is_hr(character_id: int) -> int:
    """
    自己的工作为人事
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 71


@add_premise(constant_promise.Premise.WORK_IS_LIBRARY_MANAGER)
def handle_work_is_library_manager(character_id: int) -> int:
    """
    自己的工作为图书馆管理员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 101


@add_premise(constant_promise.Premise.T_WORK_IS_LIBRARY_MANAGER)
def handle_t_work_is_library_manager(character_id: int) -> int:
    """
    交互对象的工作为图书馆管理员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return handle_work_is_library_manager(character_data.target_character_id)


@add_premise(constant_promise.Premise.WORK_IS_TEACHER)
def handle_work_is_teacher(character_id: int) -> int:
    """
    自己的工作为教师
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 151


@add_premise(constant_promise.Premise.WORK_IS_STUDENT)
def handle_work_is_student(character_id: int) -> int:
    """
    自己的工作为学生
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 152


@add_premise(constant_promise.Premise.WORK_IS_COMBAT_TRAINING)
def handle_work_is_combat_training(character_id: int) -> int:
    """
    自己的工作为战斗训练
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 91


@add_premise(constant_promise.Premise.WORK_IS_FITNESS_TRAINER)
def handle_work_is_fitness_trainer(character_id: int) -> int:
    """
    自己的工作为健身锻炼员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 92


@add_premise(constant_promise.Premise.WORK_IS_COOK)
def handle_work_is_cook(character_id: int) -> int:
    """
    自己的工作为厨师
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 51


@add_premise(constant_promise.Premise.WORK_IS_PRODUCTION_WORKER)
def handle_work_is_production_worker(character_id: int) -> int:
    """
    自己的工作为生产工人
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 121


@add_premise(constant_promise.Premise.WORK_IS_MASSAGE_THERAPIST)
def handle_work_is_massage_therapist(character_id: int) -> int:
    """
    自己的工作为按摩师
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 171


@add_premise(constant_promise.Premise.WORK_IS_DIPLOMAT)
def handle_work_is_diplomat(character_id: int) -> int:
    """
    自己的工作为外交官
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 131


@add_premise(constant_promise.Premise.WORK_IS_INVITATION_COMMISSIONER)
def handle_work_is_invitation_commissioner(character_id: int) -> int:
    """
    自己的工作为邀请专员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 132


@add_premise(constant_promise.Premise.WORK_IS_MEDICINAL_PLANTER)
def handle_work_is_medicinal_planter(character_id: int) -> int:
    """
    自己的工作为药材种植员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 161


@add_premise(constant_promise.Premise.WORK_IS_FLORAL_PLANTER)
def handle_work_is_floral_planter(character_id: int) -> int:
    """
    自己的工作为花草种植员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 162


@add_premise(constant_promise.Premise.WORK_IS_SEX_TRAINEE)
def handle_work_is_sex_trainee(character_id: int) -> int:
    """
    自己的工作为性爱练习生
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 193


@add_premise(constant_promise.Premise.WORK_IS_WARDEN)
def handle_work_is_warden(character_id: int) -> int:
    """
    自己的工作为监狱长
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.work.work_type == 191


@add_premise(constant_promise.Premise.T_WORK_IS_WARDEN)
def handle_t_work_is_warden(character_id: int) -> int:
    """
    交互对象的工作为监狱长
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return handle_work_is_warden(character_data.target_character_id)


@add_premise(constant_promise.Premise.T_WORK_IS_NOT_WARDEN)
def handle_t_work_is_not_warden(character_id: int) -> int:
    """
    交互对象的工作不是监狱长
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return not handle_work_is_warden(character_data.target_character_id)


@add_premise(constant_promise.Premise.T_WORK_IS_WARDEN_OR_T_ASSISTANT)
def handle_t_work_is_warden_or_t_assistant(character_id: int) -> int:
    """
    交互对象的工作为监狱长或交互对象是助理
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    from Script.Design.handle_premise import (
        handle_is_assistant,
    )
    character_data: game_type.Character = cache.character_data[character_id]
    if handle_work_is_warden(character_data.target_character_id):
        return 1
    if handle_is_assistant(character_data.target_character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_WARDEN)
def handle_have_warden(character_id: int) -> int:
    """
    当前有监狱长
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return cache.rhodes_island.current_warden_id


@add_premise(constant_promise.Premise.PATIENT_WAIT)
def handle_patient_wait(character_id: int) -> int:
    """
    有患者正等待就诊
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if cache.rhodes_island.patient_now > 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.NEW_NPC_WAIT)
def handle_new_npc_wait(character_id: int) -> int:
    """
    有已招募待确认的干员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if len(cache.rhodes_island.recruited_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.HAVE_OFFICE_WORK_NEED_TO_DO)
def handle_have_office_work_need_to_do(character_id: int) -> int:
    """
    有需要处理的公务
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return cache.rhodes_island.office_work > 0


@add_premise(constant_promise.Premise.NOT_HAVE_OFFICE_WORK_NEED_TO_DO)
def handle_not_have_office_work_need_to_do(character_id: int) -> int:
    """
    没有需要处理的公务
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_have_office_work_need_to_do(character_id)


@add_premise(constant_promise.Premise.PINK_CERTIFICATE_G_10)
def handle_pink_certificate_g_10(character_id: int) -> int:
    """
    拥有粉红凭证数量大于10
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if cache.rhodes_island.materials_resouce[4] > 10:
        return 1
    return 0


@add_premise(constant_promise.Premise.PRISONER_IN_CUSTODY)
def handle_prisoner_in_custody(character_id: int) -> int:
    """
    当前有关押的囚犯
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if len(cache.rhodes_island.current_prisoners):
        return 1
    return 0


@add_premise(constant_promise.Premise.PRISONER_DAILY_MANAGEMENT_SET)
def handle_prisoner_daily_management_set(character_id: int) -> int:
    """
    已设定对囚犯的日常管理
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if cache.rhodes_island.confinement_training_setting[1]:
        return 1
    return 0

