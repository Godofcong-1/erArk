import random
from Script.Core import value_handle, cache_control, constant, game_type
from Script.Design import map_handle
from Script.Config import game_config


cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """


def init_phase_course_hour():
    """初始化各年级各科目课时"""
    for school_id in game_config.config_school:
        school_config = game_config.config_school[school_id]
        school_course_session_data = game_config.config_school_session_data[school_id]
        session_max = school_config.day * (len(school_course_session_data) - 1)
        school_course_data = game_config.config_school_phase_course_data[school_id]
        for phase in school_course_data:
            now_course_set = school_course_data[phase].copy()
            now_phase_course_data = {}
            now_session_max = session_max
            more_hour = 0
            while 1:
                if not len(now_course_set):
                    break
                now_course_id = random.choice(list(now_course_set))
                now_course_value = random.randint(1, 18)
                if now_course_value <= now_session_max:
                    now_session_max -= now_course_value
                    now_phase_course_data[now_course_id] = now_course_value
                else:
                    now_phase_course_data[now_course_id] = now_session_max
                    now_session_max = 0
                    if now_phase_course_data[now_course_id] == 0:
                        now_phase_course_data[now_course_id] = 1
                more_hour += now_phase_course_data[now_course_id]
                now_course_set.remove(now_course_id)
            while more_hour != session_max:
                for course in now_phase_course_data:
                    if more_hour == session_max:
                        break
                    elif now_phase_course_data[course] > 1 and more_hour > session_max:
                        now_phase_course_data[course] -= 1
                        more_hour -= 1
                    elif more_hour < session_max:
                        now_phase_course_data[course] += 1
                        more_hour += 1
            cache.course_data.setdefault(school_id, {})
            cache.course_data[school_id][phase] = now_phase_course_data
    # init_phase_course_hour_experience()


def init_class_time_table():
    """初始化各年级课程表"""
    class_time_table = {}
    for school_id in cache.course_data:
        school_config = game_config.config_school[school_id]
        class_time = {}
        class_time_table[school_id] = {}
        for phase in cache.course_data[school_id]:
            class_time_table[school_id][phase] = {}
            class_day = 0
            course_session = game_config.config_school_session_data[school_id]
            class_day = school_config.day
            class_hour_index = {}
            class_hour = cache.course_data[school_id][phase]
            for course in reversed(class_hour.keys()):
                class_hour_index[course] = 0
                while class_hour_index[course] < class_hour[course]:
                    for day in range(0, class_day):
                        old_day = day - 1
                        if old_day < 0:
                            old_day = class_day - 1
                        class_time_table[school_id][phase].setdefault(day, {})
                        class_time_table[school_id][phase].setdefault(old_day, {})
                        for i in range(1, len(course_session)):
                            if (
                                i not in class_time_table[school_id][phase][old_day]
                                and i not in class_time_table[school_id][phase][day]
                            ):
                                class_time_table[school_id][phase][day][i] = course
                                class_hour_index[course] += 1
                                break
                            elif i not in class_time_table[school_id][phase][day]:
                                if course != class_time_table[school_id][phase][old_day][i]:
                                    class_time_table[school_id][phase][day][i] = course
                                    class_hour_index[course] += 1
                                    break
                                elif i == len(class_time) - 1:
                                    class_time_table[school_id][phase][day][i] = course
                                    class_hour_index[course] += 1
                                    break
                                elif all(
                                    [
                                        k in class_time_table[school_id][phase][day]
                                        for k in range(i, len(course_session))
                                        if k != i
                                    ]
                                ):
                                    class_time_table[school_id][phase][day][i] = course
                                    class_hour_index[course] += 1
                                    break
                        if class_hour_index[course] >= class_hour[course]:
                            break
    cache.course_time_table_data = class_time_table


# def get_character_school_phase(character_id: int) -> (int, int):
#     """
#     获取角色所属的学校和年级
#     Keyword arguments:
#     character_id -- 角色id
#     Return arguments:
#     int -- 学校id
#     int -- 年级
#     """
#     character_data = cache.character_data[character_id]
#     for school_id in game_config.config_school:
#         school_config = game_config.config_school[school_id]
#         if character_data.age >= school_config.min_age and character_data.age <= school_config.max_age:
#             return school_id, character_data.age - school_config.min_age
#     return 0, 0


# def init_class_teacher():
#     """
#     初始化各班级任课老师
#     """
#     teacher_index = len(cache.teacher_course_experience[0].keys())
#     course_max_a = 0
#     course_max_b = 0
#     for school_id in cache.course_data:
#         for phase in cache.course_data[school_id]:
#             course_max_a += len(cache.course_data[school_id][phase].keys()) * 3
#             for course in cache.course_data[school_id][phase]:
#                 if cache.course_data[school_id][phase][course] > 7:
#                     course_max_b += 3
#                 else:
#                     course_max_b += 1.5
#     if teacher_index >= course_max_a:
#         course_distribution_a()
#     elif teacher_index >= course_max_b:
#         course_distribution_b()


# def init_teacher_table():
#     """初始化教师上课时间数据"""
#     teacher_table = {}
#     for school_id in cache.course_time_table_data:
#         for phase in cache.course_time_table_data[school_id]:
#             class_time_table = cache.course_time_table_data[school_id][phase]
#             phase_room_id = 0
#             if school_id == 0:
#                 phase_room_id = 1 + phase
#             elif school_id == 1:
#                 phase_room_id = 7 + phase
#             else:
#                 phase_room_id = 10 + phase
#             if f"Classroom_{phase_room_id}" not in cache.classroom_teacher_data:
#                 continue
#             classroom_list = constant.place_data[f"Classroom_{phase_room_id}"]
#             for day in class_time_table:
#                 for classroom in classroom_list:
#                     if classroom not in cache.classroom_teacher_data[f"Classroom_{phase_room_id}"]:
#                         continue
#                     for i in class_time_table[day]:
#                         now_course = class_time_table[day][i]
#                         if (
#                             now_course
#                             not in cache.classroom_teacher_data[f"Classroom_{phase_room_id}"][classroom]
#                         ):
#                             continue
#                         for now_teacher in cache.classroom_teacher_data[f"Classroom_{phase_room_id}"][
#                             classroom
#                         ][now_course]:
#                             if now_teacher not in teacher_table:
#                                 cache.character_data[now_teacher].officeroom = constant.place_data[
#                                     f"Office_{phase_room_id}"
#                                 ]
#                             teacher_table.setdefault(now_teacher, 0)
#                             if teacher_table[now_teacher] < 18:
#                                 teacher_table[now_teacher] += 1
#                                 cache.teacher_class_time_table.setdefault(day, {})
#                                 cache.teacher_class_time_table[day].setdefault(school_id, {})
#                                 cache.teacher_class_time_table[day][school_id].setdefault(phase, {})
#                                 cache.teacher_class_time_table[day][school_id][phase].setdefault(i, {})
#                                 cache.teacher_class_time_table[day][school_id][phase][i][now_teacher] = {
#                                     classroom: now_course
#                                 }
#                                 cache.class_timetable_teacher_data.setdefault(school_id, {})
#                                 cache.class_timetable_teacher_data[school_id].setdefault(phase, {})
#                                 cache.class_timetable_teacher_data[school_id][phase].setdefault(
#                                     classroom, {}
#                                 )
#                                 cache.class_timetable_teacher_data[school_id][phase][classroom].setdefault(
#                                     day, {}
#                                 )
#                                 cache.class_timetable_teacher_data[school_id][phase][classroom][day][
#                                     i
#                                 ] = now_teacher
#                                 teacher_timetable = game_type.TeacherTimeTable()
#                                 teacher_timetable.class_room = map_handle.get_map_system_path_for_str(
#                                     classroom
#                                 )
#                                 teacher_timetable.class_times = i
#                                 teacher_timetable.course = now_course
#                                 cache.teacher_class_week_day_data.setdefault(now_teacher, set())
#                                 if day not in cache.teacher_class_week_day_data[now_teacher]:
#                                     cache.teacher_class_week_day_data[now_teacher].add(day)
#                                 now_config_id = game_config.config_school_session_data[school_id][i]
#                                 now_config = game_config.config_school_session[now_config_id]
#                                 teacher_timetable.time = now_config.start_time
#                                 teacher_timetable.week_day = day
#                                 teacher_timetable.end_time = now_config.end_time
#                                 cache.teacher_school_timetable.setdefault(now_teacher, [])
#                                 cache.teacher_school_timetable[now_teacher].append(teacher_timetable)


# def course_abmain_distribution():
#     """
#     课时分配流程AB通用主课时分配流程
#     """
#     for phase in range(12, 0, -1):
#         school_id = 0
#         school_phase = 0
#         if phase > 6:
#             school_id = 1
#             school_phase = phase - 7
#         if phase > 9:
#             school_id = 2
#             school_phase = phase - 10
#         class_list = constant.place_data["Classroom_" + str(phase)]
#         cache.classroom_teacher_data["Classroom_" + str(phase)] = {}
#         for classroom in class_list:
#             cache.classroom_teacher_data["Classroom_" + str(phase)].setdefault(classroom, {})
#             for course in cache.course_data[school_id][school_phase]:
#                 now_teacher_data = value_handle.sorted_dict_for_values(
#                     cache.teacher_course_experience[course]
#                 )
#                 now_course_index = cache.course_data[school_id][school_phase][course]
#                 if cache.course_data[school_id][school_phase][course] > 9:
#                     cache.classroom_teacher_data["Classroom_" + str(phase)][classroom].setdefault(
#                         course, []
#                     )
#                     for teacher in now_teacher_data:
#                         teacher_data.setdefault(teacher, 0)
#                         teacher_course_data.setdefault(teacher, set())
#                         if teacher_data[teacher] + now_course_index > 18:
#                             continue
#                         if course in teacher_course_data[teacher]:
#                             continue
#                         cache.classroom_teacher_data["Classroom_" + str(phase)][classroom][course].append(
#                             teacher
#                         )
#                         teacher_data[teacher] += now_course_index
#                         teacher_course_data[teacher].add(course)
#                         break


# teacher_data = {}
# teacher_course_data = {}


# def course_distribution_a():
#     """课时分配流程A"""
#     course_abmain_distribution()
#     for phase in range(1, 13):
#         school_id = 0
#         school_phase = 0
#         if phase > 6:
#             school_id = 1
#             school_phase = phase - 7
#         if phase > 9:
#             school_id = 2
#             school_phase = phase - 10
#         classroom_list = constant.place_data["Classroom_" + str(phase)]
#         cache.classroom_teacher_data["Classroom_" + str(phase)] = {}
#         for classroom in classroom_list:
#             cache.classroom_teacher_data["Classroom_" + str(phase)].setdefault(classroom, {})
#             for course in cache.course_data[school_id][school_phase]:
#                 now_course_index = cache.course_data[school_id][school_phase][course]
#                 if cache.course_data[school_id][school_phase][course] <= 9:
#                     cache.classroom_teacher_data["Classroom_" + str(phase)][classroom].setdefault(
#                         course, []
#                     )
#                     now_teacher_data = value_handle.sorted_dict_for_values(
#                         cache.teacher_course_experience[course]
#                     )
#                     for teacher in now_teacher_data:
#                         teacher_data.setdefault(teacher, 0)
#                         teacher_course_data.setdefault(teacher, set())
#                         if teacher_data[teacher] + now_course_index > 18:
#                             continue
#                         if course in teacher_course_data[teacher]:
#                             continue
#                         cache.classroom_teacher_data["Classroom_" + str(phase)][classroom][course].append(
#                             teacher
#                         )
#                         teacher_data[teacher] += now_course_index
#                         teacher_course_data[teacher].add(course)
#                         break


# def course_distribution_b():
#     """课时分配流程B"""
#     course_abmain_distribution()
#     for phase in range(1, 13):
#         school_id = 0
#         school_phase = 0
#         if phase > 6:
#             school_id = 1
#             school_phase = phase - 7
#         if phase > 9:
#             school_id = 2
#             school_phase = phase - 10
#         classroom_list = constant.place_data["Classroom_" + str(phase)]
#         cache.classroom_teacher_data["Classroom_" + str(phase)] = {}
#         for course in cache.course_data[school_id][school_phase]:
#             now_course_index = cache.course_data[school_id][school_phase][course]
#             now_teacher_data = value_handle.sorted_dict_for_values(cache.teacher_course_experience[course])
#             for classroom in classroom_list:
#                 cache.classroom_teacher_data["Classroom_" + str(phase)].setdefault(classroom, {})
#                 if cache.course_data[school_id][school_phase][course] <= 9:
#                     cache.classroom_teacher_data["Classroom_" + str(phase)][classroom].setdefault(
#                         course, []
#                     )
#                     for teacher in now_teacher_data:
#                         teacher_data.setdefault(teacher, 0)
#                         teacher_course_data.setdefault(teacher, set())
#                         if teacher_data[teacher] + now_course_index > 18:
#                             continue
#                         if course in teacher_course_data[teacher]:
#                             continue
#                         cache.classroom_teacher_data["Classroom_" + str(phase)][classroom][course].append(
#                             teacher
#                         )
#                         teacher_data[teacher] += now_course_index
#                         teacher_course_data[teacher].add(course)
#                         break


# def init_phase_course_hour_experience():
#     """按年级计算各科目课时经验标准量"""
#     phase_knownledge_experience = {}
#     phase_language_experience = {}
#     for school_id in cache.course_data:
#         phase_knownledge_experience[school_id] = {}
#         phase_language_experience[school_id] = {}
#         for phase in cache.course_data[school_id]:
#             phase_knownledge_experience[school_id][phase] = {}
#             phase_language_experience[school_id][phase] = {}
#             course_data = cache.course_data[school_id][phase]
#             for course in course_data:
#                 course_hour = course_data[course]
#                 if course in game_config.config_course_knowledge_experience_data:
#                     knowledge_experience_data = game_config.config_course_knowledge_experience_data[course]
#                     for knowledge in knowledge_experience_data:
#                         experience = knowledge_experience_data[knowledge] * course_hour * 38
#                         phase_knownledge_experience[school_id][phase].setdefault(course, {})
#                         phase_knownledge_experience[school_id][phase][course].setdefault(knowledge, 0)
#                         phase_knownledge_experience[school_id][phase][course][knowledge] += experience
#                 if course in game_config.config_course_language_experience_data:
#                     language_experience_data = game_config.config_course_language_experience_data[course]
#                     for language in language_experience_data:
#                         experience = language_experience_data[language] * course_hour * 38
#                         phase_language_experience[school_id][phase].setdefault(course, {})
#                         phase_language_experience[school_id][phase][course].setdefault(language, 0)
#                         phase_language_experience[school_id][phase][course][language] += experience
#     cache.course_school_phase_knowledge_experience = phase_knownledge_experience
#     cache.course_school_phase_language_experience = phase_language_experience


# def init_character_knowledge():
#     """
#     初始化所有角色知识等级
#     """
#     for i in cache.character_data:
#         init_experience_for_grade(i)
#         if cache.character_data[i].age > 18:
#             character_data = cache.character_data[i]
#             init_teacher_knowledge(i)
#             for course in game_config.config_course_knowledge_experience_data:
#                 if course not in cache.teacher_course_experience:
#                     cache.teacher_course_experience.setdefault(course, {})
#                 cache.teacher_course_experience[course].setdefault(i, 0)
#                 for knowledge in game_config.config_course_knowledge_experience_data[course]:
#                     if knowledge in character_data.knowledge:
#                         cache.teacher_course_experience[course][i] += character_data.knowledge[knowledge]
#             for course in game_config.config_course_language_experience_data:
#                 if course not in cache.teacher_course_experience:
#                     cache.teacher_course_experience.setdefault(course, {})
#                 cache.teacher_course_experience[course].setdefault(i, 0)
#                 for language in game_config.config_course_language_experience_data[course]:
#                     if language in character_data.language:
#                         cache.teacher_course_experience[course][i] += character_data.language[language]


# def init_teacher_knowledge(character_id: int):
#     """
#     按年龄修正教师知识等级
#     Keyword arguments:
#     character_id -- 角色id
#     """
#     character_data = cache.character_data[character_id]
#     study_year = character_data.age - 18
#     for knowledge in character_data.knowledge:
#         character_data.knowledge[knowledge] += (
#             character_data.knowledge[knowledge] / 12 * study_year * random.uniform(0.25, 0.75)
#         )
#     for language in character_data.language:
#         character_data.language[language] += (
#             character_data.language[language] / 12 * study_year * random.uniform(0.25, 0.75)
#         )


# def init_experience_for_grade(character_id: int):
#     """
#     按年级生成角色初始经验数据
#     Keyword arguments:
#     character_id -- 角色id
#     """
#     character_data = cache.character_data[character_id]
#     character_school_id, character_phase = get_character_school_phase(character_id)
#     knowledge_experience_data = cache.course_school_phase_knowledge_experience
#     language_experience_data = cache.course_school_phase_language_experience
#     if character_data.age > 18:
#         character_school_id = 2
#         character_phase = 2
#     for school_id in range(0, character_school_id):
#         if school_id in knowledge_experience_data:
#             school_knowledge_experience_data = knowledge_experience_data[school_id]
#             for phase in range(0, character_phase):
#                 if phase not in school_knowledge_experience_data:
#                     continue
#                 phase_knownledge_experience_data = school_knowledge_experience_data[phase]
#                 for course in phase_knownledge_experience_data:
#                     course_knowledge_experience_data = phase_knownledge_experience_data[course]
#                     for knowledge in course_knowledge_experience_data:
#                         knowledge_experience = course_knowledge_experience_data[knowledge]
#                         knowledge_interest = character_data.knowledge_interest[knowledge]
#                         knowledge_experience *= knowledge_interest
#                         character_data.knowledge.setdefault(knowledge, 0)
#                         character_data.knowledge[knowledge] += knowledge_experience
#         if school_id in language_experience_data:
#             school_language_experience_data = language_experience_data[school_id]
#             for phase in range(0, character_phase):
#                 if phase not in school_language_experience_data:
#                     continue
#                 phase_language_experience_data = school_language_experience_data[phase]
#                 for course in phase_language_experience_data:
#                     course_language_experience_data = phase_language_experience_data[course]
#                     for language in course_language_experience_data:
#                         language_experience = course_language_experience_data[language]
#                         language_interest = character_data.language_interest[language]
#                         language_experience *= language_interest
#                         character_data.language.setdefault(language, 0)
#                         character_data.language[language] += language_experience
