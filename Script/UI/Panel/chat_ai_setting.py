from typing import List
from types import FunctionType
from Script.Core import cache_control, game_type, get_text, flow_handle, constant
from Script.UI.Moudle import draw, panel
from Script.Config import game_config, normal_config
from Script.Design import attr_text, attr_calculation, game_time
import openai
import google.generativeai as genai
import concurrent.futures
import os
import csv
import httpx
import re

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """
line_feed = draw.NormalDraw()
""" 换行绘制对象 """
line_feed.text = "\n"
line_feed.width = 1
window_width: int = normal_config.config_normal.text_width
""" 窗体宽度 """


def judge_use_text_ai(character_id: int, behavior_id: int, original_text: str, translator: bool = False, direct_mode: bool = False) -> str:
    """
    判断是否使用文本生成AI\n
    Keyword arguments:\n
    character_id -- 角色id\n
    behavior_id -- 行为id\n
    original_text -- 原始文本\n
    translator -- 翻译模式\n
    direct_mode -- 直接对话模式\n
    Return arguments:
    fanal_text -- 最终文本
    """
    # 如果AI设置未开启，则直接返回原文本
    if 1 not in cache.ai_setting.ai_chat_setting or cache.ai_setting.ai_chat_setting[1] == 0:
        return original_text
    # 如果api密钥未设置，则直接返回原文本

    # 判断在调用哪个api
    model = cache.ai_setting.ai_chat_setting[5]
    # 如果没有输入模型名，则返回原文本
    if not model:
        return original_text
    if 'gpt' in model:
        now_key_type = 'OPENAI_API_KEY'
    elif 'gemini' in model:
        now_key_type = 'GEMINI_API_KEY'
    elif 'deepseek' in model:
        now_key_type = 'DEEPSEEK_API_KEY'
    else:
        now_key_type = 'OPENAI_API_KEY'
    if now_key_type not in cache.ai_setting.ai_chat_api_key:
        return original_text
        
    # 直接对话模式跳过安全检查
    if not direct_mode:
        # 判断是否设置了指令类型
        if cache.ai_setting.ai_chat_setting[2] == 0:
            safe_flag = False
            status_data = game_config.config_status[behavior_id]
            # 判断是否是安全标签
            for safe_tag in ["日常", "娱乐", "工作"]:
                if safe_tag in status_data.tag:
                    safe_flag = True
                    break
            if not safe_flag:
                return original_text

        # 判断是什么类型的地文
        if cache.ai_setting.ai_chat_setting[3] == 0 and not translator:
            if "地文" not in original_text:
                return original_text

    # 输出文本生成提示
    if cache.ai_setting.ai_chat_setting[8] == 0:
        model = cache.ai_setting.ai_chat_setting[5]
        info_draw = draw.NormalDraw()
        info_text = _("\n（正在调用{0}）\n").format(model)
        info_draw.text = info_text
        info_draw.width = window_width
        info_draw.draw()

    ai_result = text_ai(character_id, behavior_id, original_text, translator=translator, direct_mode=direct_mode)
    print(f"ai_result = {ai_result}")
    
    # 处理直接对话模式的返回值
    if direct_mode:
        from Script.Design.handle_instruct import chara_handle_instruct_common_settle
        tem_state_id = constant.CharacterStatus.STATUS_AI_CHAT_INSTRUCT
        ai_gererate_text = ai_result["text"]
        # 指令持续时间
        new_duration = ai_result["time"]
        # 构建该临时指令的结算
        game_config.config_behavior_effect_data[tem_state_id] = set()
        # 体力气力消耗
        game_config.config_behavior_effect_data[tem_state_id].add(10 + ai_result["tired"])
        game_config.config_behavior_effect_data[tem_state_id].add(11 + ai_result["tired"])
        # 关系变化
        if ai_result["relationship"] == 1:
            game_config.config_behavior_effect_data[tem_state_id].add(23)
        elif ai_result["relationship"] == 3:
            game_config.config_behavior_effect_data[tem_state_id].add(21)
        elif ai_result["relationship"] == 4:
            game_config.config_behavior_effect_data[tem_state_id].add(21)
            game_config.config_behavior_effect_data[tem_state_id].add(22)
        chara_handle_instruct_common_settle(tem_state_id, duration=new_duration)
    else:
        ai_gererate_text = ai_result
        
    # 检测是否显示原文本
    if cache.ai_setting.ai_chat_setting[4] == 1:
        fanal_text = ai_gererate_text
    else:
        fanal_text = "(原文本)" + original_text + "\n" + ai_gererate_text

    # 是否保存
    if cache.ai_setting.ai_chat_setting[7] == 1 and not translator:
        save_path = "data/talk/ai/ai_talk.csv"
        # 检测是否存在文件，如果不存在的话，创建文件
        # 检查文件是否存在
        if not os.path.exists(save_path):
            # 如果文件不存在，创建文件夹和文件
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write("cid,behavior_id,adv_id,premise,context\n")
                f.write("口上id,触发口上的行为id,口上限定的剧情npcid,前提id,口上内容\n")
                f.write("str,int,int,str,str\n")
                f.write("0,0,0,0,1\n")
                f.write("口上配置数据,,,,\n")

        # 读取save_path文件的最后一行，获取其cid，然后加1
        with open(save_path, "r", encoding='utf-8') as f:
            lines = f.readlines()
            last_line = lines[-1]
            last_cid = last_line.split(",")[0]
            if last_cid == "口上配置数据":
                new_cid = 0
            else:
                new_cid = int(last_cid) + 1

        # 将角色名称还原回代码
        character_data = cache.character_data[character_id]
        target_character_data = cache.character_data[character_data.target_character_id]
        Name = character_data.name
        TargetNickName = target_character_data.name
        # 查找是否存在该角色名称，如果存在的话，将其还原回代码
        if Name in ai_gererate_text:
            ai_gererate_text = ai_gererate_text.replace(Name, '{Name}')
        if character_id != 0 or character_data.target_character_id != 0:
            if TargetNickName in ai_gererate_text:
                ai_gererate_text = ai_gererate_text.replace(TargetNickName, '{TargetName}')

        # 前提文本
        premise_text = "generate_by_ai"
        # 触发者
        if character_id == 0:
            premise_text += "&sys_0"
        else:
            premise_text += "&sys_1"
        # 交互对象
        if character_data.target_character_id == 0:
            premise_text += "&sys_4"
        else:
            premise_text += "&sys_5"

        # 保存数据
        with open(save_path, "a", encoding='utf-8') as f:
            f.write(f"{new_cid},{behavior_id},0,{premise_text},{ai_gererate_text}\n")

    return fanal_text

def text_ai(character_id: int, behavior_id: int, original_text: str, translator: bool = False, direct_mode: bool = False) -> dict:
    """
    文本生成AI\n\n
    Keyword arguments:
    character_id: int 角色id\n
    behavior_id: int 行为id\n
    original_text: str 原始文本\n
    translator -- 翻译模式\n
    direct_mode -- 直接对话模式\n
    Return arguments:
    直接对话模式: dict -- {"time": int, "tired": int, "relationship": int, "text": str}
    非直接对话模式: str -- AI生成的文本\n
    """
    from Script.Design import handle_premise

    # 基础数据
    character_data = cache.character_data[character_id]
    target_character_data = cache.character_data[character_data.target_character_id]
    Name = character_data.name
    TargetNickName = target_character_data.name
    Location = character_data.position[-1]
    Season = game_time.get_month_text()
    time = game_time.get_day_and_time_text()
    talk_num = cache.ai_setting.ai_chat_setting[9] + 1
    Behavior_Name = game_config.config_status[behavior_id].name

    # 模型与密钥
    model = cache.ai_setting.ai_chat_setting[5]
    if 'gpt' in model:
        now_key_type = 'OPENAI_API_KEY'
    elif 'gemini' in model:
        now_key_type = 'GEMINI_API_KEY'
    elif 'deepseek' in model:
        now_key_type = 'DEEPSEEK_API_KEY'
    else:
        now_key_type = 'OPENAI_API_KEY'
    API_KEY = cache.ai_setting.ai_chat_api_key[now_key_type]

    # 系统提示词
    system_promote = ''
    for system_promote_cid in game_config.ui_text_data['text_ai_system_promote']:
        system_promote_text = game_config.ui_text_data['text_ai_system_promote'][system_promote_cid]
        # 对生成数量的替换处理
        if "{talk_num}" in system_promote_text:
            system_promote_text = system_promote_text.replace("{talk_num}", str(talk_num))
        system_promote += _(system_promote_text)
    # print(system_promote)
    # 生成模式
    if not translator:
        user_prompt = _('请根据以下条件，描写两个角色的互动场景：')
        # 有交互对象时
        if character_id != 0 or character_data.target_character_id != 0:
            if character_id == 0:
                pl_name = Name
                npc_name = TargetNickName
                npc_character_id = character_data.target_character_id
                npc_character_data = target_character_data
            elif character_data.target_character_id == 0:
                pl_name = TargetNickName
                npc_name = Name
                npc_character_id = character_id
                npc_character_data = character_data
            else:
                return original_text
            # 名字
            user_prompt += _("在当前的场景里，{0}是医药公司的领导人，被称为博士，{1}是一家医药公司的员工。").format(pl_name, npc_name)
            # 动作
            if not direct_mode:
                user_prompt += _("{0}正在对{1}进行的动作是{2}。你要弄清楚是谁对谁做了什么，{0}是做这个动作的人，{1}是被做了这个动作的人。").format(Name, TargetNickName, Behavior_Name)
                user_prompt += _("你需要仅描述这个动作，包括角色的肢体动作、角色的台词、角色的心理活动、角色与场景中的物体的交互等。你不要描述动作之前的剧情，或者动作之后的剧情，只描述这个动作的过程。")
            else:
                user_prompt += _("{0}正在对{1}进行互动。互动文本里的“我”都是指{0}，你都是指“{1}”。").format(Name, TargetNickName)
                user_prompt += _("互动的文本的全文是：{0}。互动文本到这里结束了。").format(original_text)
                user_prompt += _("你要将该互动的内容补充完善，并进一步续写对该互动的反应。")
                user_prompt += _("你需要尽量详细地描述，包括角色的肢体动作、角色的台词、角色的心理活动、角色与场景中的物体的交互等。你不要描述互动之前的剧情，只能描述互动本身的过程和之后的剧情，但不能出现位置或者场景的移动。")
            user_prompt += _("以下是一些额外提供的参考信息，信息里包括了两个人的详细信息，你可以这些信息中挑选一部分来丰富对本次动作的描述，你只能直接使用这些信息本身，不能从这些信息中联想或者猜测其他的信息：")
            # 地点
            user_prompt += _("场景发生的地点是{0}。").format(Location)
            # 时间
            user_prompt += _("当前的季节是{0}，当前的时间是{1}。").format(Season, time)
            # 关系
            favorability = npc_character_data.favorability[0]
            favorability_lv, tem = attr_calculation.get_favorability_level(favorability)
            trust = npc_character_data.trust
            trust_lv, tem = attr_calculation.get_trust_level(trust)
            ave_lv = int((favorability_lv + trust_lv) / 2)
            user_prompt += _("如果用数字等级来表示关系好坏，0是第一次见面的陌生人，8是托付人生的亲密伴侣，那{0}和{1}的关系大概是{2}。").format(Name, TargetNickName, ave_lv)
            # 陷落
            fall_lv = attr_calculation.get_character_fall_level(npc_character_id, minus_flag = True)
            if fall_lv > 0:
                user_prompt += _("{0}和{1}是正常的爱情关系。如果用数字等级来表示爱情的程度，1是有些懵懂的好感，4是至死不渝的爱人，那{0}和{1}的关系大概是{4}。").format(Name, TargetNickName, Name, TargetNickName, fall_lv)
            elif fall_lv < 0:
                user_prompt += _("{0}和{1}是扭曲的服从和支配的关系。如果用数字等级来表示服从的程度，1是有些讨好和有些卑微，4是无比的尊敬和彻底的服从，那{2}对{3}的服从的等级大概是{4}。").format(Name, TargetNickName, npc_name, pl_name, fall_lv)

            # 基础状态
            # 年龄素质
            age_text = attr_text.get_age_talent_text(npc_character_id)
            user_prompt += _("{0}的年龄是{1}。").format(npc_name, age_text)
            # 睡眠、疲劳、困倦
            if handle_premise.handle_action_sleep(npc_character_id) or handle_premise.handle_unconscious_flag_1(npc_character_id):
                tem,sleep_name = attr_calculation.get_sleep_level(npc_character_data.sleep_point)
                user_prompt += _("{0}正在睡觉，睡眠的深度是{1}。").format(npc_name, sleep_name)
            else:
                # 疲劳与困倦
                sleep_lv = attr_calculation.get_tired_level(npc_character_data.tired_point)
                if sleep_lv > 0:
                    sleep_text = constant.sleep_text_list[sleep_lv]
                    user_prompt += _("{0}有些困了，困的程度为{1}。").format(npc_name, sleep_text)
            # 心情
            angry_text = attr_calculation.get_angry_text(npc_character_data.angry_point)
            if angry_text != "普通":
                user_prompt += _("{0}的心情状态是{1}。").format(npc_name, angry_text)
            # 跟随
            if handle_premise.handle_is_follow_1(npc_character_id):
                user_prompt += _("{0}正在跟随{1}一起行动。").format(npc_name, pl_name)
            # 尿意
            if handle_premise.handle_urinate_ge_80(npc_character_id):
                user_prompt += _("{0}有点想上厕所尿尿。").format(npc_name)
            # 饥饿
            if handle_premise.handle_hunger_ge_80(npc_character_id):
                user_prompt += _("{0}有点饿了，想吃东西。").format(npc_name)
            # 催眠
            if handle_premise.handle_unconscious_hypnosis_flag(npc_character_id):
                user_prompt += _("{0}被{1}催眠了。").format(npc_name, pl_name)
            # 监禁
            if handle_premise.handle_imprisonment_1(npc_character_id):
                user_prompt += _("{0}被{1}监禁在监狱里了。").format(npc_name, pl_name)
            # 访客
            if npc_character_data.sp_flag.vistor == 1:
                user_prompt += _("{0}不是公司的员工，是前来拜访的访客。").format(npc_name)
            # 时停
            if handle_premise.handle_unconscious_flag_3(npc_character_id):
                user_prompt += _("{0}正处在停止的时间中，无法做出任何反应。").format(npc_name)
            # 中量数据才有的分支
            if cache.ai_setting.ai_chat_setting[6] >= 1:
                # 职业
                profession_name = game_config.config_profession[npc_character_data.profession].name
                user_prompt += _("{0}的职业是{1}。").format(npc_name, profession_name)
                # 种族
                race_name = game_config.config_race[npc_character_data.race].name
                user_prompt += _("{0}是一种虚构的奇幻种族，种族名是{1}。").format(npc_name, race_name)
                # 出身地
                birthplace_name = game_config.config_birthplace[npc_character_data.relationship.birthplace].name
                user_prompt += _("{0}的出生地是{1}。").format(npc_name, birthplace_name)
                # 势力
                nation_name = game_config.config_nation[npc_character_data.relationship.nation].name
                user_prompt += _("{0}所属的具体势力是{1}。").format(npc_name, nation_name)
                # 全素质数据
                user_prompt += _("{0}有以下素质特性：").format(npc_name)
                for talent_id in game_config.config_talent:
                    if npc_character_data.talent[talent_id]:
                        talent_name = game_config.config_talent[talent_id].name
                        user_prompt += _("{0}、").format(talent_name)
                user_prompt = user_prompt[:-1] + "。"
            # 大量数据才有的分支
            if cache.ai_setting.ai_chat_setting[6] >= 2:
                # 服装
                user_prompt += _("{0}穿着的衣服有：").format(npc_name)
                for clothing_type in game_config.config_clothing_type:
                    if len(npc_character_data.cloth.cloth_wear[clothing_type]):
                        for cloth_id in npc_character_data.cloth.cloth_wear[clothing_type]:
                            cloth_name = game_config.config_clothing_tem[cloth_id].name
                            user_prompt += _("{0}、").format(cloth_name)
                user_prompt = user_prompt[:-1] + "。"
                # 工作
                if handle_premise.handle_have_work(npc_character_id):
                    work_name = game_config.config_work_type[npc_character_data.work.work_type].name
                    user_prompt += _("{0}的工作是{1}。").format(npc_name, work_name)
                # 称呼
                if handle_premise.handle_self_have_nick_name_to_pl(npc_character_id):
                    nick_name = npc_character_data.nick_name_to_pl
                    user_prompt += _("{0}称呼{1}为{2}。").format(npc_name, pl_name, nick_name)
                if handle_premise.handle_self_have_nick_name_to_self(npc_character_id):
                    nick_name = npc_character_data.nick_name
                    user_prompt += _("{0}称呼{1}为{2}。").format(pl_name, npc_name, nick_name)

        else:
            user_prompt += _("在当前的场景里，{0}是医药公司的领导人之一，被称为博士。").format(Name)
            user_prompt += _("{0}正在进行的动作是{1}。").format(Name, Behavior_Name)
            # 地点
            user_prompt += _("场景发生的地点是{0}。").format(Location)
            # 时间
            user_prompt += _("当前的季节是{0}，当前的时间是{1}。").format(Season, time)
    # 翻译模式
    else:
        user_prompt = _('你需要将一段文本翻译为')
        user_prompt += normal_config.config_normal.language
        user_prompt += _('语言。如果文本中有有\{\}括起来的字符，请原样保留。请原样保留文本中的换行符。以下是需要翻译的文本：')
        user_prompt += original_text
    # print(f'user_prompt = {user_prompt}')

    # 直接对话模式
    if direct_mode:
        system_promote += _("你要根据以下格式返回文本，并且不需要任何其他的解释：\n")
        system_promote += _("第一行：time:int，用于表示互动行为持续的时间，单位为分钟，如 time:5 代表互动持续了5分钟\n")
        system_promote += _("第二行：tired:int，用于表示本次行为对体力的消耗程度，分为三个等级：\n")
        system_promote += _("  1 - 接近静止状态下的很少消耗，如坐着看书\n")
        system_promote += _("  2 - 正常消耗，如肢体动作、进行非体力劳动的工作\n")
        system_promote += _("  3 - 非常严重的消耗，如高强度健身、搬运重物\n")
        system_promote += _("第三行：relationship:int，用于表示本次行为对关系的影响程度，分为四个等级：\n")
        system_promote += _("  1 - 关系变差，如吵架、争执等负面行为\n")
        system_promote += _("  2 - 关系不变，如没有营养的对话、无聊的行为等\n")
        system_promote += _("  3 - 关系稍微变好，如共同工作、共同娱乐、轻度肢体交流等行为\n")
        system_promote += _("  4 - 关系快速变好，如约会、亲密行为等正面行为\n")
        system_promote += _("第四行及以后：text:str，用于返回你生成的场景描述文本，只在该行出现一次text:，后面的每一行里都不能出现text:\n")

    # 开始调用AI

    # 调用OpenAI
    if now_key_type == "OPENAI_API_KEY" or now_key_type == "DEEPSEEK_API_KEY":
        # 创建client
        client = openai.OpenAI(api_key=API_KEY)
        # deepseek则调整base_url
        if now_key_type == "DEEPSEEK_API_KEY":
            client = client.with_options(base_url="https://api.deepseek.com")
        # 自定义base_url
        if cache.ai_setting.ai_chat_setting[10] == 1:
            client = client.with_options(base_url=cache.ai_setting.now_ai_chat_base_url)
        # 自定义代理
        if cache.ai_setting.ai_chat_setting[11] == 1:
            if len(cache.ai_setting.now_ai_chat_proxy[1]) == 0:
                client = client.with_options(http_client=openai.DefaultHttpxClient(proxies=cache.ai_setting.now_ai_chat_proxy[0]))
            else:
                client = client.with_options(http_client=openai.DefaultHttpxClient(proxies=cache.ai_setting.now_ai_chat_proxy[0], transport=httpx.HTTPTransport(local_address=cache.ai_setting.now_ai_chat_proxy[1])))
        try:
            # 发送请求
            # 流式输出
            if cache.ai_setting.ai_chat_setting[14] == 1:
                completion = client.chat.completions.create(
                    model=cache.ai_setting.ai_chat_setting[5],
                    messages=[
                        {"role": "system", "content": system_promote},
                        {"role": "user", "content": user_prompt}
                    ],
                    stream=True
                )
                # 调用流式处理函数获取返回的文本
                ai_gererate_text = process_stream_response(
                    stream=completion,         # 流式返回数据的迭代器，类型为object
                    direct_mode=direct_mode,   # 是否为直接对话模式，类型为bool
                    extractor=lambda chunk: chunk.choices[0].delta.content  # 提取chunk中的文本，返回值为str
                )
           # 非流式输出
            else:
                completion = client.chat.completions.create(
                    model=cache.ai_setting.ai_chat_setting[5],
                    messages=[
                        {"role": "system", "content": system_promote},
                        {"role": "user", "content": user_prompt}
                    ]
                )
                # 获取返回的文本
                ai_gererate_text = completion.choices[0].message.content
        except Exception as e:
            # 如果发生异常，将返回的文本设为空
            ai_gererate_text = ""
    # 调用Gemini
    elif now_key_type == "GEMINI_API_KEY":
        # 创建client
        genai.configure(api_key=API_KEY)
        # gemini的传输协议改为rest
        if cache.ai_setting.ai_chat_setting[12] == 1:
            genai.configure(api_key=API_KEY, transport='rest')
        client = genai.GenerativeModel(model, system_instruction = system_promote)
        try:
            # 发送请求
            # 流式输出
            if cache.ai_setting.ai_chat_setting[14] == 1:
                completion = client.generate_content(user_prompt, stream=True)
                # 调用流式处理函数获取返回的文本
                ai_gererate_text = process_stream_response(
                    stream=completion,         # 流式返回数据的迭代器，类型为object
                    direct_mode=direct_mode,   # 是否为直接对话模式，类型为bool
                    extractor=lambda chunk: chunk.text  # 提取chunk中的文本，返回值为str
                )
            # 非流式输出
            else:
                completion = client.generate_content(user_prompt)
                # 获取返回的文本
                ai_gererate_text = completion.text
        except Exception as e:
            # 如果发生异常，将返回的文本设为空
            ai_gererate_text = ""

    # 如果没有返回文本，则返回原文本
    if ai_gererate_text == None or not len(ai_gererate_text):
        ai_gererate_text = _("(生成失败，使用原文本)") + original_text

    # 处理直接对话模式下的返回格式
    if direct_mode:
        # 解析AI返回的格式化文本
        lines = ai_gererate_text.split('\n')
        result = {
            "time": 5,  # 默认值
            "tired": 2,  # 默认值
            "relationship": 2,  # 默认值
            "text": ""  # 默认值
        }
        
        text_content = []
        for line in lines:
            if line.startswith("time:"):
                try:
                    result["time"] = int(line.replace("time:", "").strip())
                except ValueError:
                    pass
            elif line.startswith("tired:"):
                try:
                    result["tired"] = int(line.replace("tired:", "").strip())
                except ValueError:
                    pass
            elif line.startswith("relationship:"):
                try:
                    result["relationship"] = int(line.replace("relationship:", "").strip())
                except ValueError:
                    pass
            elif line.startswith("text:"):
                text_content.append(line.replace("text:", "", 1))
            else:
                text_content.append(line)
        
        # 合并所有文本内容
        result["text"] = "\n".join(text_content)
        
        # 在不影响\\n的情况下，将\n删去
        result["text"] = result["text"].replace("\n", "")
        # 删除思考过程
        if cache.ai_setting.ai_chat_setting[13] == 1:
            # 使用正则删除<think>到</think>之间的内容
            result["text"] = re.sub(r'<think>.*?</think>', '', result["text"])
        
        return result
    else:
        # 在不影响\\n的情况下，将\n删去
        ai_gererate_text = ai_gererate_text.replace("\n", "")
        # 非翻译模式下删去空格
        if not translator:
            ai_gererate_text = ai_gererate_text.replace(" ", "")
        # 删除思考过程
        if cache.ai_setting.ai_chat_setting[13] == 1:
            # 使用正则删除<think>到</think>之间的内容
            ai_gererate_text = re.sub(r'<think>.*?</think>', '', ai_gererate_text)
            
        return ai_gererate_text

def process_stream_response(stream: object, direct_mode: bool, extractor: object) -> str:
    """
    处理流式输出的返回数据，并绘制返回结果
    参数:
        stream: object - 流式返回数据的迭代器，每个元素代表部分返回内容
        direct_mode: bool - 是否为直接对话模式，直接对话模式下需要等待"text:"标记再开始输出
        extractor: function - 一个函数，输入chunk对象，返回对应的文本字符串
    返回:
        str - 拼接后的完整返回文本
    """

    ai_generate_text: str = ""
    now_draw = draw.NormalDraw()
    # 非直接对话模式时默认直接开始输出文本
    text_started: bool = not direct_mode

    for chunk in stream:
        # 提取当前chunk中的文本
        chunk_text: str = extractor(chunk)
        if not chunk_text:
            continue

        # 如果chunk仅为单独换行，则绘制换行并跳过当前循环
        if chunk_text.strip() == "\n":
            line_feed = draw.LineFeedWaitDraw()
            line_feed.text = " \n"
            line_feed.draw()
            continue

        # 在直接对话模式下，等待遇到"text:"标记后再开始绘制和存储
        if direct_mode:
            # 直接对话模式下等待遇到"text:"标记后再开始绘制和存储
            if "text:" in chunk_text and not text_started:
                text_started = True
                parts = chunk_text.split("text:", 1)
                if len(parts) > 1:
                    display_text = parts[1]
                    # 替换掉换行符
                    display_text = display_text.replace("\\n", "\n")
                    now_draw.text = display_text
                    now_draw.width = 1
                    now_draw.draw()
                    ai_generate_text += display_text
            # 如果已经开始text部分，直接显示文本
            elif text_started:
                # 替换掉换行符
                chunk_text = chunk_text.replace("\\n", "\n")
                # 替换掉text:
                now_draw.text = chunk_text.replace("text:", "")
                now_draw.width = 1
                now_draw.draw()
                ai_generate_text += chunk_text
            # 如果未开始text部分，只存储不显示
            else:
                ai_generate_text += chunk_text
        # 非直接对话模式下直接显示文本
        else:
            now_draw.text = chunk_text
            now_draw.width = 1
            now_draw.draw()
            ai_generate_text += chunk_text

    # 绘制一个空白的等待
    wait_draw = draw.LineFeedWaitDraw()
    wait_draw.text = " \n"
    wait_draw.draw()

    return ai_generate_text

def direct_chat_with_ai() -> str:
    """
    与AI进行直接对话\n
    用户输入动作文本，AI生成回复\n
    Return arguments:
    reply_text -- AI回复文本
    """
    # 提示信息
    ask_text = _("\n请描述你想要进行的动作(输入空白文本退出)：\n")

    # 获取玩家输入
    ask_panel = panel.AskForOneMessage()
    ask_panel.set(ask_text, 999)
    user_input = ask_panel.draw()
    line_feed.draw()
    
    # 如果输入为空，则退出
    if not user_input:
        return ""
        
    # 获取当前玩家角色ID和目标角色ID
    character_id = 0  # 假设0是玩家角色
    behavior_id = 0   # 默认行为ID，可以根据实际情况调整
    
    # 调用判断函数，启用直接对话模式
    reply_text = judge_use_text_ai(character_id, behavior_id, user_input, direct_mode=True)
    
    # 非流式传输下再绘制回复
    if cache.ai_setting.ai_chat_setting[14] != 1:
        reply_draw = draw.NormalDraw()
        reply_draw.text = _("\nAI回复：\n") + reply_text + _("\n")
        reply_draw.width = window_width
        reply_draw.draw()

    return reply_text

